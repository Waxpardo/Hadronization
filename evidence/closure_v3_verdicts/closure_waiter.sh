#!/bin/bash
# Record the moment each closure ends, and whether its log carries a summary
# line at all. It does NOT rule on the verdict: that is the harvest driver
# (extraction/pipeline/harvest_tune.py --stage closure), which checks the
# emitted counts against the closure v3 preregistration. The fuller dated
# record is preserved in the internal archive. This exists so a
# closure that finishes -- or dies -- after the session ends leaves a dated,
# unambiguous record instead of a log whose last line is silence.
#
# WHY THE MARKER MATTERS. The launches were detached, so no shell holds their
# exit status. Absence of the summary line plus a recorded exit time is how a
# killed closure is told apart from one still running.
set -uo pipefail
D=/data/alice/ipardoza/closure_runs
W="${D}/closure_waiter.log"
say() { echo "$(date "+%Y-%m-%d %H:%M:%S") $*" >> "${W}"; }

watch_one() {
  local tune="$1" pid="$2" log="$3"
  while [[ -d "/proc/${pid}" ]]; do sleep 30; done
  say "CLOSURE PROCESS EXITED tune=${tune} pid=${pid}"
  local summary
  summary="$(grep -m1 "^PAIR_BLOCK_CLOSURE " "${log}" 2>/dev/null)"
  if [[ -n "${summary}" ]]; then
    say "  SUMMARY tune=${tune} ${summary}"
    echo "${summary}" > "${D}/verdict_line_${tune}.txt"
  else
    say "  NO SUMMARY LINE tune=${tune} -- the closure did not reach its verdict (killed, or crashed). Log: ${log}"
  fi
  if grep -qE "PAIR_BLOCK_CLOSURE_ERROR|RETAINED closure log|segmentation violation" "${log}" 2>/dev/null; then
    say "  ERROR MARKERS PRESENT tune=${tune} -- read the log before believing anything"
  fi
  say "  DONE tune=${tune}"
}

say "WAITER START pid=$$"
watch_one JUNCTIONS    2563461 "${D}/closure_HF_RUN3_V1_JUNCTIONS_20260815_220840.log" &
watch_one CLOSEPACKING 2563536 "${D}/closure_HF_RUN3_V1_CLOSEPACKING_20260815_220842.log" &
wait
say "WAITER EXIT"
