#!/bin/bash
set -euo pipefail

if [[ "$#" -lt 5 || "$#" -gt 7 ]]; then
  echo "Usage: $0 FILE CAMPAIGN TUNE LOGICAL_ID EXPECTED_SUCCESSES [ATTEMPT] [SEED]" >&2
  exit 2
fi
file="$1"
campaign="$2"
tune="$3"
logical_id="$4"
successes="$5"
attempt="${6:--1}"
seed="${7:--1}"
script_dir="$(cd "$(dirname "$0")" && pwd)"
project_base="$(cd "${script_dir}/.." && pwd)"
export HADRONIZATION_BASE="${HADRONIZATION_BASE:-${project_base}}"
source "${project_base}/setupEnv.sh"

validation_log="$(mktemp /tmp/hadronization_raw_validation_XXXXXX.log)"
trap 'rm -f "${validation_log}"' EXIT
set +e
root -l -b >"${validation_log}" 2>&1 <<ROOT_COMMANDS
.L ${script_dir}/ValidateRawOutput.C
int validation_status = ValidateRawOutput("${file}", "${campaign}", "${tune}", ${logical_id}, ${successes}, ${attempt}, ${seed}, true);
gSystem->Exit(validation_status);
ROOT_COMMANDS
root_status=$?
set -e
cat "${validation_log}"
if (( root_status != 0 )); then
  echo "ERROR: ROOT validator exited ${root_status}" >&2
  exit "${root_status}"
fi
if grep -q "segmentation violation" "${validation_log}" ||
   ! grep -q '^RAW_VALIDATION_SUMMARY errors=0 ' "${validation_log}"; then
  echo "ERROR: validator success marker missing or ROOT crash detected" >&2
  exit 90
fi
