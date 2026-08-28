#!/bin/bash
# Observe one exact child PID and one exact log; signal no process.
set -uo pipefail

if [[ "$#" -ne 5 ]]; then
  echo "Usage: supervisor_eol_watch.sh CHILD_PID RUN_LOG FINAL_MARKER POLL_SECONDS MAX_POLLS" >&2
  exit 2
fi

CHILD_PID="$1"
RUN_LOG="$2"
FINAL_MARKER="$3"
POLL_SECONDS="$4"
MAX_POLLS="$5"
if [[ ! "${CHILD_PID}" =~ ^[1-9][0-9]*$ ]] ||
   [[ ! "${POLL_SECONDS}" =~ ^[0-9]+([.][0-9]+)?$ ]] ||
   [[ ! "${MAX_POLLS}" =~ ^[0-9]+$ ]]; then
  echo "EOL_WATCH_REFUSAL invalid PID or polling input" >&2
  exit 2
fi

polls=0
while kill -0 "${CHILD_PID}" 2>/dev/null; do
  if (( polls >= MAX_POLLS )); then
    echo "EOL_WATCH_TIMEOUT pid=${CHILD_PID} log=${RUN_LOG}" >&2
    exit 2
  fi
  polls=$((polls + 1))
  sleep "${POLL_SECONDS}"
done

if grep -qF "${FINAL_MARKER}" "${RUN_LOG}" 2>/dev/null; then
  echo "EOL_WATCH_PASS pid=${CHILD_PID} log=${RUN_LOG}"
  exit 0
fi
echo "EOL_WATCH_FAIL pid=${CHILD_PID} missing_final_marker log=${RUN_LOG}" >&2
exit 1
