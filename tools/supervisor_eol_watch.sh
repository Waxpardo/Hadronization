#!/bin/bash
# Stop the merge supervisor WHEN, AND ONLY WHEN, the merge completes cleanly.
#
# WHY. tools/merge_supervisor.sh detects the merge by presence of a process
# (merge_pid()) and cannot distinguish "finished all work and exited 0" from
# "died". On a clean exit every pre-check still passes -- checkout clean, HEAD
# pinned, reflog unmoved, manifest sha, CVMFS python3 executes -- so it would
# restart a COMPLETED merge into another 12 h 42 m preamble, up to
# MAX_RESTARTS=6. Its fail-closed design is right for deaths and wrong for
# completion, and completion is not a case it can see.
#
# THE TRIGGER IS RACE-FREE, not a poll that has to beat the supervisor.
# merge_root_files.sh ends with a `for tune in MONASH JUNCTIONS CLOSEPACKING`
# closure loop; the CLOSEPACKING pass line is the last statement in the file.
# Once it is printed the merge has done all its work, so stopping the
# supervisor is correct whether the merge then exits 0 or is killed.
#
# WHAT IT MAY TOUCH: one TERM to one recorded PID whose /proc/cmdline is
# re-checked first (PID reuse). Nothing else. It never touches the merge, the
# checkout, a partial, or a merged directory. If the merge disappears WITHOUT
# the completion marker it does nothing at all and exits, leaving the
# supervisor to guard exactly the case it was built for.
set -uo pipefail

BASE="${HADRONIZATION_SITE_ROOT:?set HADRONIZATION_SITE_ROOT}"
RUNDIR="${HADRONIZATION_MERGE_RUN_ROOT:-${BASE}/merge_runs/HF_RUN3_V1_merge}"
LOG="${RUNDIR}/supervisor_eol_watch.log"
MERGE_PID="${MERGE_PID:?set MERGE_PID}"
SUP_PID="${SUPERVISOR_PID:?set SUPERVISOR_PID}"
MARKER="CANONICAL_PAIR_BLOCK_CLOSURE_PASS tune=CLOSEPACKING"
POLL=5
DEADLINE=$(( $(date +%s) + 96*3600 ))

say() { echo "$(date "+%Y-%m-%d %H:%M:%S") $*" >> "${LOG}"; }

# Newest merge log only: an older run must never supply the marker.
newest_log() { ls -t "${RUNDIR}"/merge_v*.log "${RUNDIR}"/merge_sup_*.log 2>/dev/null | head -1; }
alive()      { [[ -d "/proc/$1" ]]; }
is_sup()     { tr "\0" " " < "/proc/$1/cmdline" 2>/dev/null | grep -q "merge_supervisor.sh"; }

stop_supervisor() {
  if ! alive "${SUP_PID}"; then say "SUPERVISOR ALREADY GONE pid=${SUP_PID}; nothing to stop"; return 0; fi
  if ! is_sup "${SUP_PID}"; then say "REFUSE  pid=${SUP_PID} is not merge_supervisor.sh (PID reuse); not signalling"; return 1; fi
  say "STOPPING SUPERVISOR pid=${SUP_PID} (merge work complete)"
  kill "${SUP_PID}"
  sleep 3
  if alive "${SUP_PID}"; then say "WARN    supervisor pid=${SUP_PID} still alive 3s after TERM"; else say "STOPPED supervisor pid=${SUP_PID}"; fi
}

say "EOL-WATCH START pid=$$ merge=${MERGE_PID} supervisor=${SUP_PID} poll=${POLL}s"
while true; do
  if (( $(date +%s) > DEADLINE )); then say "EXIT    96 h deadline reached with no completion marker; supervisor left running"; exit 0; fi

  log="$(newest_log)"
  if [[ -n "${log}" ]] && grep -qF "${MARKER}" "${log}" 2>/dev/null; then
    say "MARKER SEEN in ${log}: ${MARKER}"
    stop_supervisor
    say "EOL-WATCH EXIT"
    exit 0
  fi

  if ! alive "${MERGE_PID}"; then
    say "MERGE ABSENT pid=${MERGE_PID} with NO completion marker in ${log:-<no log>}"
    say "NO ACTION    this is the death case the supervisor exists for; leaving it running. Human required."
    say "EOL-WATCH EXIT"
    exit 0
  fi

  sleep "${POLL}"
done
