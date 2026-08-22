#!/usr/bin/env bash
# Install the checkout-freeze guard as a git hook on a clone that runs jobs.
#
# WHY THIS EXISTS, and why a hook rather than the Makefile target.
#
# `make can-advance` (tools/checkout_advance_guard.py) enforces the invariant
#
#     jobs in flight that pin a commit  =>  the checkout does not move
#
# but only for the person who remembers to run it. Raw `git checkout`,
# `git reset --hard`, `git merge` and `git pull` bypass it completely. That is
# the gap named earlier as "the obvious next hardening".
#
# THERE IS A SHARPER REASON, discovered on 2026-08-09 and not known earlier.
# The Nikhef checkout is DETACHED at 61fe978f, the
# commit its 3000 in-flight analysis jobs pin. The guard was committed later, at
# 7e1f7e7. So on Nikhef, right now:
#
#     $ make can-advance
#     make: *** No rule to make target 'can-advance'.  Stop.
#
# Restoring the pin -- the correct remedy for the freeze breach -- ALSO
# uninstalled the mechanism built to prevent it. The freeze is once again
# enforced by memory alone, on the one machine where breaking it costs a
# campaign.
#
# A git hook is immune to that failure, for two reasons:
#
#   1. `.git/hooks/` is NOT part of the working tree, so moving the checkout
#      between commits does not add, remove, or alter the hook.
#   2. This hook is SELF-CONTAINED. It re-implements the probe rather than
#      importing tools/queue_probe.py, because the checked-out tree cannot be
#      assumed to contain it -- which is exactly the situation on Nikhef today.
#
# WHY `reference-transaction` AND NOT THE OBVIOUS HOOKS.
#
#   post-checkout      runs AFTER the checkout has already moved. It can warn.
#                      It cannot refuse. Useless for an invariant.
#   pre-merge-commit   only fires for merges that CREATE a commit. A
#                      fast-forward merge -- precisely how a pin gets advanced
#                      onto a branch -- does not trigger it at all.
#   pre-rebase         rebase only.
#   pre-push           the wrong direction entirely.
#
# `reference-transaction` fires on every ref update, in a "prepared" phase where
# a non-zero exit ABORTS the transaction. It therefore covers `git checkout`,
# `git reset`, `git merge` (fast-forward included), `git pull`, and `git commit`
# alike. It is the only hook that can actually hold the invariant.
#
# It fires for OTHER ref updates too -- `git fetch` writing refs/remotes/* is
# the common one -- so the hook narrows to updates that genuinely move the
# checkout: HEAD itself, or the branch HEAD currently points at. Fetching stays
# unblocked.
#
# FAIL-CLOSED, on the same principle as tools/queue_probe.py: an unanswered
# question is not an empty queue. Note the consequence on Nikhef's LOGIN node,
# where `condor_q` is not installed: the probe cannot ask, so the answer is
# UNKNOWN, so the move is refused. That is correct rather than unfortunate --
# a host that cannot check whether jobs are in flight is not a host that should
# be moving a pinned checkout. Do it on `stbc`, where the question can be
# answered.
#
# THE OVERRIDE has the same shape as the Makefile guard's: it exists for
# RESTORING a pin, not for ignoring the check, and it requires a reason, which
# is echoed and appended to .git/checkout_guard.log.
#
#     HADRONIZATION_CHECKOUT_OVERRIDE_REASON="restoring the pin ..." git checkout 61fe978
#
# Usage:
#   tools/install_checkout_guard_hook.sh --repo /path/to/clone            # install
#   tools/install_checkout_guard_hook.sh --repo /path/to/clone --print    # dry run
#   tools/install_checkout_guard_hook.sh --repo /path/to/clone --uninstall

set -euo pipefail

REPO=""
MODE="install"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo) REPO="${2:-}"; shift 2 ;;
    --print) MODE="print"; shift ;;
    --uninstall) MODE="uninstall"; shift ;;
    -h|--help) sed -n '2,74p' "$0"; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

if [[ -z "$REPO" ]]; then
  echo "ERROR: --repo is required (the clone whose checkout must not move)" >&2
  exit 2
fi

read -r -d '' HOOK_BODY <<'HOOK_EOF' || true
#!/usr/bin/env bash
# INSTALLED BY tools/install_checkout_guard_hook.sh -- DO NOT EDIT IN PLACE.
#
# Refuses to move this checkout while jobs that pin its commit are in flight.
#
#     jobs in flight that pin a commit  =>  the checkout does not move
#
# Production jobs verify their pinned commit at STARTUP, analysis jobs at
# PROMOTION. Either way, moving the checkout under them invalidates work that
# has already been done.
#
# Self-contained on purpose: the checked-out tree may predate the guard tooling
# (it does on Nikhef, pinned at 61fe978f), so nothing here imports from it.

set -u

# reference-transaction runs three times per transaction. Only "prepared" can
# refuse; the others are notifications.
[[ "${1:-}" == "prepared" ]] || exit 0

GIT_DIR_PATH="$(git rev-parse --git-dir 2>/dev/null)" || exit 0
LOG="${GIT_DIR_PATH}/checkout_guard.log"

# Which refs moving means "the checkout moved"? HEAD itself, and -- when HEAD is
# attached -- the branch it points at. Everything else (refs/remotes/* from a
# fetch, tags, notes) leaves the working tree where it is and is not our
# business.
CURRENT_BRANCH="$(git symbolic-ref -q HEAD 2>/dev/null || true)"

MOVED=0
MOVED_REF=""
MOVED_OLD=""
MOVED_NEW=""
while read -r OLD NEW REF; do
  [[ -n "${REF:-}" ]] || continue
  [[ "$OLD" == "$NEW" ]] && continue
  if [[ "$REF" == "HEAD" ]] || [[ -n "$CURRENT_BRANCH" && "$REF" == "$CURRENT_BRANCH" ]]; then
    MOVED=1
    MOVED_REF="$REF"
    MOVED_OLD="$OLD"
    MOVED_NEW="$NEW"
  fi
done

[[ "$MOVED" -eq 1 ]] || exit 0

stamp() { date -Is 2>/dev/null || date; }

# --- DETACHED-RUN PIN, checked BEFORE the queue probe -----------------------
# THE QUEUE PROBE CANNOT SEE A DETACHED PROCESS. A long merge runs as a nohup
# process, not a Condor job, so "the schedd holds nothing" is NOT evidence that
# nothing pins this checkout. That gap once left both this hook and
# `make can-advance` reporting ALLOWED while a 65 h merge was reading the tree.
#
# EXISTENCE-BASED AND FAIL-CLOSED, and it does NOT probe liveness. A liveness
# check is the wrong instrument: the hook can run on a different node or as a
# different user than the pinning process, and PIDs get reused -- every one of
# those degrades to "looks dead" => ALLOWED, which is the failure being closed.
#
# There is deliberately NO env-var override. The control is the file: removing
# it is a deliberate act that leaves a trace, which an env var does not.
PINFILE="${GIT_DIR_PATH}/checkout_pin"
if [[ -e "$PINFILE" ]]; then
  printf 'CHECKOUT_ADVANCE_REFUSED %s ref=%s %s -> %s state=PINFILE (%s)\n' \
    "$(stamp)" "$MOVED_REF" "${MOVED_OLD:0:8}" "${MOVED_NEW:0:8}" "$PINFILE" \
    >> "$LOG" 2>/dev/null || true
  {
    echo ""
    echo "CHECKOUT_ADVANCE_REFUSED  --  PINFILE: a detached run pins this checkout"
    echo ""
    echo "  A long-running process outside the batch system is reading this"
    echo "  checkout. The Condor queue cannot see it, so the queue probe would"
    echo "  have said ALLOWED. It is wrong."
    echo ""
    echo "    ref:  ${MOVED_REF}"
    echo "    from: ${MOVED_OLD}"
    echo "    to:   ${MOVED_NEW}"
    echo ""
    echo "  The pin says:"
    echo ""
    sed 's/^/    /' "$PINFILE" 2>/dev/null || echo "    (pinfile unreadable)"
    echo ""
    echo "  Do NOT delete the pinfile to get past this message. Verify the run"
    echo "  it names has actually finished, then remove it:"
    echo ""
    echo "    rm ${PINFILE}"
    echo ""
  } >&2
  exit 1
fi

# --- the probe, fail-closed -------------------------------------------------
# Emptiness needs TWO conditions, never one: the listing must exit zero AND a
# separate -totals probe must name the schedd. A command that exits zero while
# printing nothing because it could not reach the schedd satisfies the first
# and fails the second -- the exact case that once produced a false
# QUEUE_EMPTY.
probe() {
  command -v condor_q >/dev/null 2>&1 || { echo "UNKNOWN condor_q not installed on $(hostname -s)"; return; }
  local totals listing count
  totals="$(condor_q -totals 2>/dev/null)" || { echo "UNKNOWN condor_q -totals failed"; return; }
  [[ "$totals" == *"Schedd:"* ]] || { echo "UNKNOWN condor_q -totals did not name a schedd"; return; }
  listing="$(condor_q -af ClusterId 2>/dev/null)" || { echo "UNKNOWN condor_q listing failed"; return; }
  count="$(printf '%s\n' "$listing" | grep -c '[0-9]' || true)"
  if [[ "$count" -gt 0 ]]; then
    echo "NONEMPTY ${count} job(s) in flight"
  else
    echo "EMPTY schedd answered and holds nothing"
  fi
}

VERDICT="$(probe)"
STATE="${VERDICT%% *}"
DETAIL="${VERDICT#* }"

if [[ "$STATE" == "EMPTY" ]]; then
  printf 'CHECKOUT_ADVANCE_ALLOWED %s ref=%s %s -> %s (%s)\n' \
    "$(stamp)" "$MOVED_REF" "${MOVED_OLD:0:8}" "${MOVED_NEW:0:8}" "$DETAIL" >> "$LOG" 2>/dev/null || true
  exit 0
fi

REASON="${HADRONIZATION_CHECKOUT_OVERRIDE_REASON:-}"
if [[ -n "$REASON" ]]; then
  printf 'CHECKOUT_ADVANCE_OVERRIDE %s ref=%s %s -> %s state=%s (%s) reason=%s\n' \
    "$(stamp)" "$MOVED_REF" "${MOVED_OLD:0:8}" "${MOVED_NEW:0:8}" "$STATE" "$DETAIL" "$REASON" >> "$LOG" 2>/dev/null || true
  echo "CHECKOUT_ADVANCE_OVERRIDE state=${STATE} (${DETAIL})" >&2
  echo "  reason recorded: ${REASON}" >&2
  echo "  logged to: ${LOG}" >&2
  exit 0
fi

printf 'CHECKOUT_ADVANCE_REFUSED %s ref=%s %s -> %s state=%s (%s)\n' \
  "$(stamp)" "$MOVED_REF" "${MOVED_OLD:0:8}" "${MOVED_NEW:0:8}" "$STATE" "$DETAIL" >> "$LOG" 2>/dev/null || true

{
  echo ""
  echo "CHECKOUT_ADVANCE_REFUSED  --  ${STATE}: ${DETAIL}"
  echo ""
  echo "  This checkout is pinned by jobs that verify its commit."
  echo "  Moving it invalidates work that has already been done."
  echo ""
  echo "    ref:  ${MOVED_REF}"
  echo "    from: ${MOVED_OLD}"
  echo "    to:   ${MOVED_NEW}"
  echo ""
  if [[ "$STATE" == "UNKNOWN" ]]; then
    echo "  The queue could not be QUERIED, which is not the same as the queue"
    echo "  being empty, so the move is refused. If condor_q is missing here,"
    echo "  run this on the submit node (stbc) where the question can be asked."
  else
    echo "  Wait for the campaign to converge, then retry."
  fi
  echo ""
  echo "  If you are RESTORING a pin rather than breaking one, say so:"
  echo ""
  echo "    HADRONIZATION_CHECKOUT_OVERRIDE_REASON=\"restoring the pin to <sha>\" \\"
  echo "      git <your command>"
  echo ""
} >&2

exit 1
HOOK_EOF

GIT_DIR="$(git -C "$REPO" rev-parse --git-dir 2>/dev/null)" || {
  echo "ERROR: not a git repository: $REPO" >&2; exit 2; }
case "$GIT_DIR" in /*) ;; *) GIT_DIR="$REPO/$GIT_DIR" ;; esac
HOOK_PATH="$GIT_DIR/hooks/reference-transaction"

case "$MODE" in
  print)
    echo "would install: $HOOK_PATH"
    echo "--- hook body ---"
    printf '%s\n' "$HOOK_BODY"
    ;;
  uninstall)
    if [[ -e "$HOOK_PATH" ]]; then
      rm -f "$HOOK_PATH"
      echo "removed: $HOOK_PATH"
    else
      echo "nothing to remove at: $HOOK_PATH"
    fi
    ;;
  install)
    mkdir -p "$GIT_DIR/hooks"
    printf '%s\n' "$HOOK_BODY" > "$HOOK_PATH"
    chmod +x "$HOOK_PATH"
    echo "installed: $HOOK_PATH"
    echo "log:       $GIT_DIR/checkout_guard.log"
    ;;
esac
