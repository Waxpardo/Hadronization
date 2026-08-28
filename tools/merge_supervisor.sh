#!/bin/bash
# Blocking supervisor for one fully resolved canonical merge invocation.
set -uo pipefail

usage() {
  cat <<'USAGE' >&2
Usage: merge_supervisor.sh FREEZE_DIR PRODUCTION_ROOT ANALYSIS_ROOT MERGED_BASE CAMPAIGN PAIR_SCHEMA EXPECTED_HEAD EXPECTED_MANIFEST_SHA256
USAGE
}

if [[ "$#" -ne 8 ]]; then
  usage
  exit 2
fi

FREEZE="$1"
PRODUCTION_ROOT="$2"
ANALYSIS_ROOT="$3"
MERGED_BASE="$4"
CAMPAIGN="$5"
PAIR_SCHEMA="$6"
EXPECTED_HEAD="$7"
EXPECTED_MANIFEST_SHA="$8"
CHECKOUT="${HADRONIZATION_BASE:?set HADRONIZATION_BASE}"
MANIFEST="${FREEZE%/}/canonical_manifest.jsonl"
RUN_ROOT="${HADRONIZATION_MERGE_RUN_ROOT:-${MERGED_BASE%/}/merge_runs/${CAMPAIGN}}"
MERGE_COMMAND="${HADRONIZATION_SUPERVISOR_MERGE_CMD:-${CHECKOUT}/merging/merge_root_files.sh}"
WATCH_COMMAND="${HADRONIZATION_SUPERVISOR_WATCH_CMD:-${CHECKOUT}/tools/supervisor_eol_watch.sh}"
PRECHECK_COMMAND="${HADRONIZATION_SUPERVISOR_PRECHECK_CMD:-}"
PYTHON_COMMAND="${HADRONIZATION_SUPERVISOR_PYTHON:-python3}"
GIT_COMMAND="${HADRONIZATION_SUPERVISOR_GIT:-git}"
SESSION_LAUNCHER="${HADRONIZATION_SUPERVISOR_SESSION_LAUNCHER:-${CHECKOUT}/tools/launch_in_new_session.py}"
POLL_SECONDS="${HADRONIZATION_SUPERVISOR_POLL_SECONDS:-5}"
WATCH_MAX_POLLS="${HADRONIZATION_SUPERVISOR_WATCH_MAX_POLLS:-69120}"
MAX_RESTARTS="${HADRONIZATION_MERGE_MAX_RESTARTS:-2}"
SESSION_READY_POLL_SECONDS="${HADRONIZATION_SESSION_READY_POLL_SECONDS:-0.01}"
SESSION_READY_MAX_POLLS="${HADRONIZATION_SESSION_READY_MAX_POLLS:-3000}"
TERM_GRACE_POLL_SECONDS="${HADRONIZATION_MERGE_TERM_GRACE_POLL_SECONDS:-0.1}"
TERM_GRACE_MAX_POLLS="${HADRONIZATION_MERGE_TERM_GRACE_MAX_POLLS:-100}"
FINAL_MARKER="CANONICAL_SUPERVISED_MERGE_COMPLETE output_tag=${CAMPAIGN}"

if [[ ! "${EXPECTED_HEAD}" =~ ^[0-9a-f]{40}$ ]] ||
   [[ ! "${EXPECTED_MANIFEST_SHA}" =~ ^[0-9a-f]{64}$ ]] ||
   [[ ! "${MAX_RESTARTS}" =~ ^[0-9]+$ ]] ||
   [[ ! "${POLL_SECONDS}" =~ ^[0-9]+([.][0-9]+)?$ ]] ||
   [[ ! "${WATCH_MAX_POLLS}" =~ ^[0-9]+$ ]] ||
   [[ ! "${SESSION_READY_POLL_SECONDS}" =~ ^[0-9]+([.][0-9]+)?$ ]] ||
   [[ ! "${SESSION_READY_MAX_POLLS}" =~ ^[0-9]+$ ]] ||
   [[ ! "${TERM_GRACE_POLL_SECONDS}" =~ ^[0-9]+([.][0-9]+)?$ ]] ||
   [[ ! "${TERM_GRACE_MAX_POLLS}" =~ ^[0-9]+$ ]]; then
  echo "SUPERVISOR_REFUSAL invalid launch pin or polling/restart input" >&2
  exit 2
fi

mkdir -p "${RUN_ROOT}"
SUPERVISOR_LOG="${RUN_ROOT}/supervisor_$$.log"
child_pid=""
attempt_pgid=""
watcher_pid=""

say() {
  local line="SUPERVISOR $*"
  echo "${line}" | tee -a "${SUPERVISOR_LOG}"
}

cleanup_watcher() {
  if [[ -n "${watcher_pid}" ]]; then
    if kill -0 "${watcher_pid}" 2>/dev/null; then
      kill "${watcher_pid}" 2>/dev/null || true
    fi
    wait "${watcher_pid}" 2>/dev/null || true
  fi
  watcher_pid=""
}

attempt_group_alive() {
  [[ -n "${attempt_pgid}" ]] &&
    kill -0 -- "-${attempt_pgid}" 2>/dev/null
}

terminate_attempt_group() {
  local poll
  if attempt_group_alive; then
    kill -TERM -- "-${attempt_pgid}" 2>/dev/null || true
  elif [[ -n "${child_pid}" ]] && kill -0 "${child_pid}" 2>/dev/null; then
    # Before the launcher handshake there is no merge descendant. Terminating
    # the exact child is therefore sufficient and cannot reach the caller.
    kill -TERM "${child_pid}" 2>/dev/null || true
  fi
  for ((poll = 0; poll < TERM_GRACE_MAX_POLLS; ++poll)); do
    attempt_group_alive || break
    sleep "${TERM_GRACE_POLL_SECONDS}"
  done
  if attempt_group_alive; then
    kill -KILL -- "-${attempt_pgid}" 2>/dev/null || true
  fi
  if [[ -n "${child_pid}" ]]; then
    wait "${child_pid}" 2>/dev/null || true
  fi
  child_pid=""
  attempt_pgid=""
}

on_signal() {
  trap - HUP INT TERM
  cleanup_watcher
  terminate_attempt_group
  exit 130
}

trap cleanup_watcher EXIT
trap on_signal HUP INT TERM

pre_checks() {
  local actual_head actual_manifest checkout_status
  if ! command -v "${PYTHON_COMMAND}" >/dev/null 2>&1 ||
     ! "${PYTHON_COMMAND}" -c 'import hashlib,json,sys' >/dev/null 2>&1; then
    say "REFUSAL_INTERPRETER_UNAVAILABLE interpreter=${PYTHON_COMMAND}"
    return 1
  fi
  if [[ ! -x "${MERGE_COMMAND}" ]]; then
    say "REFUSAL_MERGE_DRIVER_UNAVAILABLE path=${MERGE_COMMAND}"
    return 1
  fi
  if [[ ! -x "${WATCH_COMMAND}" ]]; then
    say "REFUSAL_WATCHER_UNAVAILABLE path=${WATCH_COMMAND}"
    return 1
  fi
  if [[ ! -r "${SESSION_LAUNCHER}" ]]; then
    say "REFUSAL_SESSION_LAUNCHER_UNAVAILABLE path=${SESSION_LAUNCHER}"
    return 1
  fi
  if ! checkout_status="$("${GIT_COMMAND}" -C "${CHECKOUT}" status \
      --porcelain --untracked-files=no 2>&1)"; then
    say "REFUSAL_CHECKOUT_STATUS_FAILED checkout=${CHECKOUT}"
    return 1
  fi
  if [[ -n "${checkout_status}" ]]; then
    say "REFUSAL_CHECKOUT_DIRTY checkout=${CHECKOUT}"
    return 1
  fi
  actual_head="$("${GIT_COMMAND}" -C "${CHECKOUT}" rev-parse HEAD 2>/dev/null || true)"
  if [[ "${actual_head}" != "${EXPECTED_HEAD}" ]]; then
    say "REFUSAL_HEAD_CHANGED expected=${EXPECTED_HEAD} actual=${actual_head:-unreadable}"
    return 1
  fi
  if [[ ! -f "${MANIFEST}" ]]; then
    say "REFUSAL_MANIFEST_UNAVAILABLE basename=$(basename "${MANIFEST}")"
    return 1
  fi
  actual_manifest="$("${PYTHON_COMMAND}" - "${MANIFEST}" <<'PY'
import hashlib, pathlib, sys
digest = hashlib.sha256()
with pathlib.Path(sys.argv[1]).open("rb") as stream:
    for chunk in iter(lambda: stream.read(16 * 1024 * 1024), b""):
        digest.update(chunk)
print(digest.hexdigest())
PY
)" || actual_manifest=""
  if [[ "${actual_manifest}" != "${EXPECTED_MANIFEST_SHA}" ]]; then
    say "REFUSAL_MANIFEST_CHANGED expected=${EXPECTED_MANIFEST_SHA} actual=${actual_manifest:-unreadable}"
    return 1
  fi
  if [[ -n "${PRECHECK_COMMAND}" ]]; then
    if [[ ! -x "${PRECHECK_COMMAND}" ]]; then
      say "REFUSAL_TEST_PRECHECK_UNAVAILABLE path=${PRECHECK_COMMAND}"
      return 1
    fi
    if ! "${PRECHECK_COMMAND}" \
        "${FREEZE}" "${PRODUCTION_ROOT}" "${ANALYSIS_ROOT}" \
        "${MERGED_BASE}" "${CAMPAIGN}" "${PAIR_SCHEMA}" \
        "${EXPECTED_HEAD}" "${EXPECTED_MANIFEST_SHA}"; then
      say "REFUSAL_PRECHECK_COMMAND_FAILED path=${PRECHECK_COMMAND}"
      return 1
    fi
  fi
  say "PRECHECK_PASS head=${actual_head} manifest_sha256=${actual_manifest}"
  return 0
}

restarts=0
attempt=0
say "START campaign=${CAMPAIGN} pair_schema=${PAIR_SCHEMA} max_restarts=${MAX_RESTARTS}"
while true; do
  if ! pre_checks; then
    say "FAIL precheck attempt=${attempt}"
    exit 64
  fi

  run_log="$(mktemp "${RUN_ROOT}/merge_attempt_${attempt}_XXXXXX.log")"
  session_ready="${run_log}.session_ready"
  session_go="${run_log}.session_go"
  say "LAUNCH attempt=${attempt} run_log=${run_log}"
  HADRONIZATION_EXPECTED_PAIR_SCHEMA="${PAIR_SCHEMA}" \
    "${PYTHON_COMMAND}" "${SESSION_LAUNCHER}" \
    "${session_ready}" "${session_go}" "$$" "${MERGE_COMMAND}" \
    "${FREEZE}" "${PRODUCTION_ROOT}" "${ANALYSIS_ROOT}" \
    "${MERGED_BASE}" "${CAMPAIGN}" >"${run_log}" 2>&1 &
  child_pid=$!
  # The launcher cannot exec the merge command until this supervisor validates
  # that it is the leader of the new session and process group.
  attempt_pgid="${child_pid}"
  ready_polls=0
  while [[ ! -s "${session_ready}" ]] &&
        kill -0 "${child_pid}" 2>/dev/null &&
        (( ready_polls < SESSION_READY_MAX_POLLS )); do
    ready_polls=$((ready_polls + 1))
    sleep "${SESSION_READY_POLL_SECONDS}"
  done
  ready_pid=""
  ready_pgid=""
  ready_sid=""
  if [[ -s "${session_ready}" ]]; then
    read -r ready_pid ready_pgid ready_sid < "${session_ready}" || true
  fi
  if [[ "${ready_pid}" != "${child_pid}" ]] ||
     [[ "${ready_pgid}" != "${child_pid}" ]] ||
     [[ "${ready_sid}" != "${child_pid}" ]]; then
    say "FAIL session_isolation_handshake pid=${child_pid} "
    terminate_attempt_group
    exit 69
  fi
  : > "${session_go}"
  "${WATCH_COMMAND}" "${child_pid}" "${run_log}" "${FINAL_MARKER}" \
    "${POLL_SECONDS}" "${WATCH_MAX_POLLS}" >>"${SUPERVISOR_LOG}" 2>&1 &
  watcher_pid=$!
  say "CHILD_START pid=${child_pid} pgid=${attempt_pgid} watcher_pid=${watcher_pid}"

  child_status=0
  wait "${child_pid}" || child_status=$?
  child_pid=""
  watcher_status=0
  wait "${watcher_pid}" || watcher_status=$?
  watcher_pid=""
  if attempt_group_alive; then
    say "FAIL lingering_attempt_process_group pgid=${attempt_pgid}"
    terminate_attempt_group
    exit 70
  fi
  attempt_pgid=""
  cat "${run_log}"
  say "CHILD_END attempt=${attempt} exit=${child_status} watcher=${watcher_status}"

  if (( child_status == 0 )); then
    if (( watcher_status == 0 )); then
      say "PASS clean_exit_and_final_marker run_log=${run_log}"
      exit 0
    fi
    say "FAIL missing_final_marker run_log=${run_log}"
    exit 66
  fi

  # Bash reports a child terminated by signal N as 128+N. Only that class is
  # restartable. Ordinary nonzero exits are deterministic refusals/failures.
  if (( child_status < 129 || child_status > 192 )); then
    say "FAIL deterministic_child_exit=${child_status} no_restart"
    exit "${child_status}"
  fi
  if (( restarts >= MAX_RESTARTS )); then
    say "FAIL restart_budget_exhausted budget=${MAX_RESTARTS} last_exit=${child_status}"
    exit 75
  fi
  restarts=$((restarts + 1))
  attempt=$((attempt + 1))
  say "RESTART_ALLOWED restart=${restarts} previous_signal_exit=${child_status}"
done
