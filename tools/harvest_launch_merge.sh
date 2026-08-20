#!/bin/bash
# Launch one systematics-variation merge with a full E8-compliant identity
# record, behind six refusals and a pipeline lock.
#
# Usage:
#   HADRONIZATION_EXPECTED_PAIR_SCHEMA=v3 tools/harvest_launch_merge.sh CAMPAIGN
#
# WHY THIS FILE IS IN THE REPOSITORY. It lived only in the Nikhef workspace
# until 2026-08-18. On that day a second executor overwrote it, dropped two
# guards and added the schema default the owner had forbidden, and nothing
# recorded the change. A launcher that is not versioned cannot be reviewed and
# cannot be restored. It is here now, and the deployed copy is a copy.
#
# Paths are overridable so the suite can exercise every refusal in a sandbox.
set -euo pipefail

C="${1:?campaign required}"
H="${HADRONIZATION_BASE:-/data/alice/ipardoza/Hadronization}"
W="${HARVEST_WORKSPACE:-/data/alice/ipardoza/systematics_harvest}"
PROD_ROOT="${HARVEST_PRODUCTION_ROOT:-/data/alice/ipardoza/hadronization_production}"
ANA_ROOT="${HARVEST_ANALYSIS_ROOT:-/data/alice/ipardoza/hadronization_analysis}"
MERGED="${HARVEST_MERGED_ROOT:-/data/alice/ipardoza/hadronization_merged}"
DISK_PATH="${HARVEST_DISK_PATH:-/data/alice}"
DISK_FLOOR_GB="${HARVEST_DISK_FLOOR_GB:-150}"
LOCK="$W/pipeline.lock"
LOG="$W/merge_runs/merge_${C}.log"
ID="$W/merge_runs/identity_${C}.txt"

# Resolve the host ONCE. The lock writes this value and the lock check compares
# against it, so they agree by construction rather than by two calls agreeing.
#
# The fallback chain exists because `hostname -f` needs name resolution, and a
# host without it answers on stderr instead of stdout. That made the lock refuse
# a lock it had taken itself, and it made the launcher test depend on DNS.
# THE BOUND, STATED: every branch after the host comparison ends in `exit 3`, so
# a resolution failure could only ever cause a FALSE REFUSAL. It could not let
# two executors share the lock. This removes a false refusal, not a race.
#
# `uname -n` comes BEFORE `hostname -s` because it is the project's own spelling
# of "this host": tests/test_harvest_launcher.py writes its lock fixtures with
# os.uname().nodename. On a host where the two differ -- macOS gives
# Inakis-MacBook-Air.local against Inakis-MacBook-Air -- a short-name fallback
# reintroduces the same false refusal from the other direction.
HOSTNAME_FQDN="$(hostname -f 2>/dev/null || uname -n 2>/dev/null \
                 || hostname -s 2>/dev/null || echo unknown-host)"

# ---------------------------------------------------------------------------
# REFUSAL 1. The schema is required and has NO default.
# A `:-v3` default passes a v2 campaign silently on the day one exists. That is
# the A4 defect relocated from the wrapper to its caller, not removed.
# ---------------------------------------------------------------------------
if [ -z "${HADRONIZATION_EXPECTED_PAIR_SCHEMA:-}" ]; then
  echo "REFUSING: HADRONIZATION_EXPECTED_PAIR_SCHEMA is required and has no default." >&2
  echo "          Set it explicitly: v3 for Run-3 production and the variations." >&2
  exit 2
fi
SCHEMA="$HADRONIZATION_EXPECTED_PAIR_SCHEMA"

mkdir -p "$W/merge_runs"

# ---------------------------------------------------------------------------
# REFUSAL 2. THE PIPELINE LOCK. One executor at a time.
# Two executors ran this pipeline on 2026-08-18. Both were correct in
# isolation; together they duplicated a five-hour closure and raced on this
# file. The lock is created atomically, so the loser of a race refuses rather
# than sharing.
# ---------------------------------------------------------------------------
lock_report() {
  echo "          lock contents:" >&2
  sed 's/^/            /' "$LOCK" >&2 2>/dev/null || echo "            (empty)" >&2
}
if ! ( set -o noclobber
       printf 'pid=%s\npgid=%s\nhost=%s\nstarted_utc=%s\ncampaign=%s\n' \
         "$$" "$(ps -o pgid= -p $$ | tr -d ' ')" "$HOSTNAME_FQDN" \
         "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$C" > "$LOCK" ) 2>/dev/null; then
  lock_host="$(sed -n 's/^host=//p' "$LOCK" 2>/dev/null)"
  lock_pid="$(sed -n 's/^pid=//p' "$LOCK" 2>/dev/null)"
  if [ "$lock_host" != "$HOSTNAME_FQDN" ]; then
    # E8: a PID checked on the wrong host is indistinguishable from one that
    # exited. We cannot ask, so we refuse.
    echo "REFUSING: a pipeline lock exists and was taken on ${lock_host:-an unknown host}." >&2
    echo "          This host cannot ask whether PID ${lock_pid:-?} is alive there." >&2
    lock_report; exit 3
  fi
  # `kill -0` rather than /proc: /proc is Linux-only, and this script is also
  # exercised by the suite on developer machines. Everything here runs as one
  # user, so a success means alive and not merely "exists but is not ours".
  if [ -n "$lock_pid" ] && kill -0 "$lock_pid" 2>/dev/null; then
    echo "REFUSING: a live pipeline lock is held by PID $lock_pid on this host." >&2
    lock_report; exit 3
  fi
  echo "REFUSING: a STALE pipeline lock is present; PID ${lock_pid:-?} is dead." >&2
  echo "          Confirm no merge is running, then remove it: rm $LOCK" >&2
  lock_report; exit 3
fi
trap 'rm -f "$LOCK"' EXIT

# ---------------------------------------------------------------------------
# REFUSAL 3. One-shot log guard. Every refusal happens before the log exists,
# so a refused launch never consumes the campaign's single attempt.
# ---------------------------------------------------------------------------
if [ -e "$LOG" ]; then
  echo "REFUSING: $LOG exists; a merge for $C was already started" >&2; exit 3
fi

# REFUSAL 4. Tracked-clean checkout.
if [ -n "$(git -C "$H" status --porcelain --untracked-files=no)" ]; then
  echo "REFUSING: checkout not tracked-clean" >&2
  git -C "$H" status --porcelain --untracked-files=no | head -3 >&2; exit 3
fi

# ---------------------------------------------------------------------------
# REFUSAL 5. The checkout must carry the closure-gate fix. Without it a merge
# runs for hours and dies at exit 7 with none of its work recorded, which is
# what happened to HF_SYS_MUR_UP on 2026-08-18.
# ---------------------------------------------------------------------------
if ! grep -q "HADRONIZATION_EXPECTED_PAIR_SCHEMA" "$H/merging/merge_root_files.sh"; then
  echo "REFUSING: the checkout's merge driver predates the closure-gate fix;" >&2
  echo "          it would merge for hours and then die at exit 7. Sync first." >&2
  exit 3
fi

# REFUSAL 6. Free disk floor. `df -Pk` is POSIX: one line per filesystem, no
# wrapping, and the same columns on every platform the suite runs on.
FREE_GB=$(df -Pk "$DISK_PATH" 2>/dev/null | awk 'NR==2 {printf "%d", $4/1048576}')
if [ "${FREE_GB:-0}" -lt "$DISK_FLOOR_GB" ]; then
  echo "REFUSING: free disk ${FREE_GB}G is below the ${DISK_FLOOR_GB}G floor" >&2; exit 3
fi

setsid nohup env HADRONIZATION_BASE="$H" HADRONIZATION_EXPECTED_PAIR_SCHEMA="$SCHEMA" \
  bash "$H/merging/merge_root_files.sh" \
    "$W/manifests/$C" "$PROD_ROOT/$C" "$ANA_ROOT/$C" "$MERGED" "$C" \
    > "$LOG" 2>&1 < /dev/null &
PID=$!
sleep "${HARVEST_SETTLE_SECONDS:-12}"
PGID=$(ps -o pgid= -p "$PID" 2>/dev/null | tr -d ' ' || echo GONE)
{
  echo "campaign          = $C"
  echo "pid               = $PID"
  echo "pgid              = $PGID"
  echo "host              = $HOSTNAME_FQDN"
  echo "log               = $LOG"
  echo "checkout_commit   = $(git -C "$H" rev-parse HEAD)"
  echo "expected_schema   = $SCHEMA"
  echo "disk_free_gb      = $FREE_GB"
  echo "loadavg           = $(cut -d' ' -f1-3 /proc/loadavg 2>/dev/null || echo n/a)"
  echo "launched_utc      = $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "completion_marker = 3 x CANONICAL_PAIR_BLOCK_CLOSURE_PASS (one per tune), after 33 PROMOTED_MERGE"
  echo "death_rule        = PID absent WITHOUT all three markers is a DEATH, not a completion (E8)"
  echo "kill_rule         = kill by PGID $PGID on this host only; never pkill -f"
} > "$ID"
cat "$ID"
echo "alive_after_settle = $(ps -o etime= -p "$PID" 2>/dev/null | tr -d ' ' || echo NO)"
grep -m1 "CLOSURE_EXPECTED_SCHEMA\|ERROR" "$LOG" || echo "(schema line not yet printed)"
