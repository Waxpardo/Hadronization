#!/bin/bash
set -euo pipefail

if [[ "$#" -ne 1 && "$#" -ne 3 ]]; then
  echo "Usage: $0 PAIR_OUTPUT_DIRECTORY [EXPECTED_MERGE_INPUT_FILES SOURCE_MANIFEST_SHA256]" >&2
  exit 2
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_base="$(cd "${script_dir}/.." && pwd)"
export HADRONIZATION_BASE="${HADRONIZATION_BASE:-${project_base}}"
source "${project_base}/setupEnv.sh"

directory="$1"
expected_merge_inputs="${2:--1}"
expected_manifest_sha256="${3:-}"
if [[ ! "${expected_merge_inputs}" =~ ^-?[0-9]+$ ]] ||
   (( expected_merge_inputs == 0 || expected_merge_inputs < -1 )); then
  echo "ERROR: expected merge input count must be -1 or a positive integer" >&2
  exit 2
fi
if [[ "${expected_merge_inputs}" != "-1" &&
      ! "${expected_manifest_sha256}" =~ ^[0-9a-f]{64}$ ]]; then
  echo "ERROR: invalid source-manifest SHA-256" >&2
  exit 2
fi
log_file="$(mktemp "/tmp/validate_pair_directory_XXXXXX.log")"
status=0
root -l -b -q \
  "${script_dir}/ValidatePairDirectory.C(\"${directory}\",true,${expected_merge_inputs},\"${expected_manifest_sha256}\")" \
  >"${log_file}" 2>&1 || status=$?
cat "${log_file}"
if (( status != 0 )) ||
   ! grep -q 'PAIR_DIRECTORY_VALIDATION errors=0' "${log_file}" ||
   ! grep -q 'trigger_histogram_digest_groups=12 trigger_histogram_identity_comparisons=288' \
     "${log_file}" ||
   ! grep -q 'multiplicity_histogram_digest_groups=1 multiplicity_histogram_identity_comparisons=299' \
     "${log_file}" ||
   grep -qE 'segmentation violation|Break +segmentation|cling JIT session error' \
     "${log_file}"; then
  rm -f "${log_file}"
  exit 1
fi
rm -f "${log_file}"
