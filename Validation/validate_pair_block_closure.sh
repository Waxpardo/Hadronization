#!/bin/bash
set -euo pipefail

if [[ "$#" -lt 2 || "$#" -gt 3 ]]; then
  cat >&2 <<'USAGE'
Usage:
  validate_pair_block_closure.sh CENTRAL_DIRECTORY BLOCK_BASE_DIRECTORY [EXPECTED_CENTRAL_EVENTS]

BLOCK_BASE_DIRECTORY must contain combined_root_1 through combined_root_10.
The command checks all 300 generated pair-registry files and fails unless
the central content and stored Sumw2 of summed MULTIPLICITY, hTrKinematics,
hAsKinematics, hCorrelations, and hCorrelationsByOrigin equal the ten-block
sum within the fixed ROOT merge tolerance. Additive event/count/weight
metadata and the all-event or event-ID-modulo block contract are also checked.
The associate-origin category schema and exact category-label map must be
identical in the central file and every block.
USAGE
  exit 2
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_base="$(cd "${script_dir}/.." && pwd)"
export HADRONIZATION_BASE="${HADRONIZATION_BASE:-${project_base}}"
source "${project_base}/setupEnv.sh"

central_directory="$1"
block_base_directory="$2"
expected_central_events="${3:--1}"
if [[ ! "${expected_central_events}" =~ ^-?[0-9]+$ ]] ||
   (( expected_central_events == 0 || expected_central_events < -1 )); then
  echo "ERROR: EXPECTED_CENTRAL_EVENTS must be -1 or a positive integer" >&2
  exit 2
fi

log_file="$(mktemp "/tmp/validate_pair_block_closure_XXXXXX.log")"
status=0
root -l -b -q \
  "${script_dir}/ValidatePairBlockClosure.C(\"${central_directory}\",\"${block_base_directory}\",${expected_central_events})" \
  >"${log_file}" 2>&1 || status=$?
cat "${log_file}"
expected_summary="PAIR_BLOCK_CLOSURE errors=0 central_pair_files=300 block_pair_files=3000 object_content_sumw2_closure_checks=1500 additive_metadata_closure_checks=3600 invariant_metadata_checks=600 source_filter_contract_checks=300 expected_central_events=${expected_central_events} relative_tolerance=2e-10"
if (( status != 0 )) ||
   [[ "$(grep -Fxc "${expected_summary}" "${log_file}")" -ne 1 ]] ||
   grep -qE 'PAIR_BLOCK_CLOSURE_ERROR|segmentation violation|Break +segmentation|cling JIT session error' \
     "${log_file}"; then
  rm -f "${log_file}"
  exit 1
fi
rm -f "${log_file}"
