#!/bin/bash
set -euo pipefail

if [[ "$#" -ne 1 ]]; then
  echo "Usage: $0 PAIR_OUTPUT_DIRECTORY" >&2
  exit 2
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_base="$(cd "${script_dir}/.." && pwd)"
export HADRONIZATION_BASE="${HADRONIZATION_BASE:-${project_base}}"
source "${project_base}/setupEnv.sh"

directory="$1"
log_file="$(mktemp "/tmp/validate_pair_directory_XXXXXX.log")"
status=0
root -l -b -q \
  "${script_dir}/ValidatePairDirectory.C(\"${directory}\",true)" \
  >"${log_file}" 2>&1 || status=$?
cat "${log_file}"
if (( status != 0 )) ||
   ! grep -q 'PAIR_DIRECTORY_VALIDATION errors=0' "${log_file}" ||
   grep -qE 'segmentation violation|Break +segmentation|cling JIT session error' \
     "${log_file}"; then
  rm -f "${log_file}"
  exit 1
fi
rm -f "${log_file}"
