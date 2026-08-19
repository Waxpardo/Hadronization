#!/bin/bash
# Supervise the canonical merge: detect death, re-run the pre-checks, restart.
#
# WHY THIS EXISTS. The merge driver is resumable by construction but not
# self-restarting, and it dies from causes that have nothing to do with the
# data: a scheduled reboot killed v3, and a momentarily-absent CVMFS python3
# killed v4 at 22:27 on 2026-08-13. That second death went unnoticed for
# 10.6 hours. The cost of a death is not the death, it is the time between the
# death and someone noticing.
#
# WHAT IT IS ALLOWED TO TOUCH: process lifecycle, and nothing else. It never
# deletes a partial, never writes in the checkout, never touches the seed
# ledger, never removes a merged directory. Its only mutation is starting a
# process that the operator would otherwise start by hand, with the identical
# command.
#
# FAIL CLOSED. Every pre-check the operator ran by hand on 2026-08-14 is run
# here, and ANY failure means log-and-stop, never restart. A supervisor that
# restarts blindly is worse than no supervisor: it would have cheerfully
# relaunched into a missing interpreter every 60 seconds all night, and buried
# the real cause under thousands of identical failures.
set -uo pipefail

BASE=/data/alice/ipardoza
CHECKOUT="${BASE}/Hadronization"
RUNDIR="${BASE}/merge_runs/HF_RUN3_V1_merge"
LOG="${RUNDIR}/supervisor.log"
FREEZE="${CHECKOUT}/campaigns/HF_RUN3_V1/freeze"

# Pinned expectations. These are the values verified by hand on 2026-08-14.
EXPECTED_HEAD="43e35be876dd5d881a931cb845ab490ab9b97509"
EXPECTED_MANIFEST_SHA="fcd96eaebd4dc11f071a2c8db8849f6a4cc19b764622a796664e524b27d0fc80"
CVMFS_PYTHON="/cvmfs/alice.cern.ch/el9-x86_64/Packages/Python/v3.9.16-15/bin/python3"

POLL_SECONDS="${POLL_SECONDS:-120}"
MAX_RESTARTS="${MAX_RESTARTS:-6}"

say() { echo "$(date '+%Y-%m-%d %H:%M:%S') $*" >> "${LOG}"; }

merge_pid() {
  pgrep -u "$(id -u)" -f "merge_root_files.sh ${FREEZE}" | head -1
}

# Returns 0 only if EVERY pre-check passes. Logs each one either way.
pre_checks() {
  local ok=0

  if [[ -n "$(git -C "${CHECKOUT}" status --porcelain --untracked-files=no 2>&1)" ]]; then
    say "PRECHECK FAIL  checkout is not tracked-clean"
    ok=1
  else
    say "PRECHECK ok    checkout tracked-clean"
  fi

  local head
  head="$(git -C "${CHECKOUT}" rev-parse HEAD 2>&1)"
  if [[ "${head}" != "${EXPECTED_HEAD}" ]]; then
    say "PRECHECK FAIL  HEAD is ${head}, expected ${EXPECTED_HEAD}"
    ok=1
  else
    say "PRECHECK ok    HEAD ${head}"
  fi

  # The reflog is the check that HEAD has not been moved and moved back.
  local moved
  moved="$(git -C "${CHECKOUT}" reflog --since='2026-08-10' 2>/dev/null | wc -l)"
  if [[ "${moved}" -ne 0 ]]; then
    say "PRECHECK FAIL  reflog shows ${moved} HEAD movement(s) since 2026-08-10"
    ok=1
  else
    say "PRECHECK ok    reflog unmoved since 2026-08-10"
  fi

  local msha
  msha="$(sha256sum "${FREEZE}/canonical_manifest.jsonl" 2>/dev/null | awk '{print $1}')"
  if [[ "${msha}" != "${EXPECTED_MANIFEST_SHA}" ]]; then
    say "PRECHECK FAIL  canonical manifest sha ${msha:-<unreadable>}"
    ok=1
  else
    say "PRECHECK ok    canonical manifest sha matches"
  fi

  # The cause of the v4 death. Checked by EXECUTING it, not by stat: the
  # symlink survived the outage; what vanished was the resolved target.
  if ! "${CVMFS_PYTHON}" -c 'import hashlib,json,sys' >/dev/null 2>&1; then
    say "PRECHECK FAIL  CVMFS python3 does not execute (${CVMFS_PYTHON})"
    ok=1
  else
    say "PRECHECK ok    CVMFS python3 executes"
  fi

  return "${ok}"
}

restarts=0
say "SUPERVISOR START pid=$$ poll=${POLL_SECONDS}s max_restarts=${MAX_RESTARTS}"
pid="$(merge_pid)"
say "SUPERVISOR observed merge pid=${pid:-none} at start"

while true; do
  pid="$(merge_pid)"
  if [[ -n "${pid}" ]]; then
    sleep "${POLL_SECONDS}"
    continue
  fi

  say "MERGE ABSENT   no merge_root_files.sh process found"

  if (( restarts >= MAX_RESTARTS )); then
    say "STOP           restart budget ${MAX_RESTARTS} exhausted; not restarting"
    say "SUPERVISOR EXIT"
    exit 0
  fi

  say "PRECHECKS      running"
  if ! pre_checks; then
    say "STOP           a pre-check FAILED; refusing to restart. Human required."
    say "SUPERVISOR EXIT"
    exit 1
  fi
  say "PRECHECKS      all passed"

  restarts=$((restarts + 1))
  stamp="$(date +%Y%m%d_%H%M%S)"
  newlog="${RUNDIR}/merge_sup_${stamp}.log"
  say "RESTART        #${restarts} -> ${newlog}"
  (
    cd "${CHECKOUT}" || exit 1
    setsid nohup ./merge_root_files.sh \
      "${FREEZE}" \
      "${BASE}/hadronization_production/HF_RUN3_V1" \
      "${BASE}/hadronization_analysis/HF_RUN3_V1" \
      "${BASE}/hadronization_merged" \
      HF_RUN3_V1 > "${newlog}" 2>&1 < /dev/null &
  )
  sleep 20
  pid="$(merge_pid)"
  if [[ -n "${pid}" ]]; then
    say "RESTART ok     merge pid=${pid}"
  else
    say "RESTART FAILED no merge process 20s after launch; see ${newlog}"
    say "SUPERVISOR EXIT"
    exit 1
  fi
done
