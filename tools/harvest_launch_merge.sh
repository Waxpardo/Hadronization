#!/bin/bash
# Launch one systematic-variation merge with a recorded identity and six refusal checks.
#
# Usage:
#   HADRONIZATION_EXPECTED_PAIR_SCHEMA=v3 tools/harvest_launch_merge.sh CAMPAIGN
#
# Overridable paths let the tests exercise every refusal without site storage.
set -euo pipefail

C="${1:?campaign required}"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
H="${HADRONIZATION_BASE:-$(cd "${script_dir}/.." && pwd)}"
W="${HARVEST_WORKSPACE:?set HARVEST_WORKSPACE}"
PROD_ROOT="${HARVEST_PRODUCTION_ROOT:?set HARVEST_PRODUCTION_ROOT}"
ANA_ROOT="${HARVEST_ANALYSIS_ROOT:?set HARVEST_ANALYSIS_ROOT}"
MERGED="${HARVEST_MERGED_ROOT:?set HARVEST_MERGED_ROOT}"
DISK_PATH="${HARVEST_DISK_PATH:-${PROD_ROOT}}"
DISK_FLOOR_GB="${HARVEST_DISK_FLOOR_GB:-150}"
LOCK="$W/pipeline.lock"
LOG="$W/merge_runs/merge_${C}.log"
ID="$W/merge_runs/identity_${C}.txt"

# Resolve the host once so the lock writer and checker use one value.
# The fallback avoids a DNS dependency and matches the test fixture's uname spelling.
HOSTNAME_FQDN="$(hostname -f 2>/dev/null || uname -n 2>/dev/null \
                 || hostname -s 2>/dev/null || echo unknown-host)"

# ---------------------------------------------------------------------------
# REFUSAL 1. Require a schema so another campaign cannot inherit v3 silently.
# ---------------------------------------------------------------------------
if [ -z "${HADRONIZATION_EXPECTED_PAIR_SCHEMA:-}" ]; then
  echo "REFUSING: HADRONIZATION_EXPECTED_PAIR_SCHEMA is required and has no default." >&2
  echo "          Set it explicitly: v3 for Run-3 production and the variations." >&2
  exit 2
fi
SCHEMA="$HADRONIZATION_EXPECTED_PAIR_SCHEMA"

mkdir -p "$W/merge_runs"

# ---------------------------------------------------------------------------
# REFUSAL 2. Create the pipeline lock atomically so only one executor proceeds.
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
    # Refuse a remote lock because this host cannot test that process.
    echo "REFUSING: a pipeline lock exists and was taken on ${lock_host:-an unknown host}." >&2
    echo "          This host cannot ask whether PID ${lock_pid:-?} is alive there." >&2
    lock_report; exit 3
  fi
  # `kill -0` keeps the process check portable beyond Linux.
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
# REFUSAL 3. Refuse an existing log before consuming the campaign attempt.
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
# REFUSAL 5. Require the closure schema gate before starting the long merge.
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
