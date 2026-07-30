#!/bin/bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  ./merge_root_files.sh FREEZE_DIR PRODUCTION_ROOT ANALYSIS_ROOT ANALYZED_DATA_BASE [OUTPUT_TAG]

Consumes only the sealed canonical manifest and its ten exact deterministic
blocks. It creates Paul-compatible pair-object directories:
  complete_root_OUTPUT_TAG_{MONASH,JUNCTIONS,CLOSEPACKING}
  SUBSAMPLES_OUTPUT_TAG/combined_root_subSamples_TUNE/combined_root_{1..10}

Each directory contains the full generated pair registry (including all legacy
56 names used by Paul's configurations), is checksum-inventoried, and is
promoted only after exact object/provenance validation. Existing output is
validated but never overwritten.
USAGE
}

if [[ "$#" -lt 4 || "$#" -gt 5 || "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 2
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_base="${HADRONIZATION_BASE:-${script_dir}}"
project_base="${project_base%/}"
export HADRONIZATION_BASE="${project_base}"
source "${project_base}/setupEnv.sh"

freeze_dir="$(cd "$1" && pwd)"
production_root="$(cd "$2" && pwd)"
analysis_root="$(cd "$3" && pwd)"
analyzed_data_base="$4"
output_tag="${5:-$(basename "$(dirname "${freeze_dir}")")}"
if [[ ! "${output_tag}" =~ ^[A-Za-z0-9._-]+$ ]]; then
  echo "ERROR: unsafe output tag: ${output_tag}" >&2
  exit 2
fi
if [[ -n "$(git -C "${project_base}" status --porcelain --untracked-files=no)" ]]; then
  echo "ERROR: canonical merge requires a tracked-clean checkout" >&2
  exit 3
fi

python3 "${project_base}/tools/canonical_manifest.py" validate "${freeze_dir}"
mkdir -p "${analysis_root}/validation"
merge_contract_report="${analysis_root}/validation/canonical_merge_contract.json"
merge_contract_stage="$(mktemp "${analysis_root}/validation/.canonical_merge_contract.XXXXXX")"
python3 "${project_base}/tools/canonical_merge_contract.py" \
  "${freeze_dir}" >"${merge_contract_stage}"
if [[ -e "${merge_contract_report}" ]]; then
  if ! cmp -s "${merge_contract_stage}" "${merge_contract_report}"; then
    echo "ERROR: existing canonical merge contract differs; retained candidate ${merge_contract_stage}" >&2
    exit 3
  fi
  rm -f "${merge_contract_stage}"
else
  mv "${merge_contract_stage}" "${merge_contract_report}"
fi
read -r canonical_inputs_per_tune canonical_inputs_per_block canonical_events_per_tune < <(
  python3 "${project_base}/tools/canonical_merge_contract.py" \
    "${freeze_dir}" --shell-values
)
analysis_report="${analysis_root}/validation/analysis_output_manifest_validation.json"
python3 "${project_base}/tools/validate_analysis_outputs.py" \
  "${freeze_dir}/canonical_manifest.jsonl" "${analysis_root}" \
  --production-root "${production_root}" --checkout "${project_base}" \
  --report "${analysis_report}"
mkdir -p "${analyzed_data_base}"

merge_one() {
  local tune="$1"
  local manifest="$2"
  local expected_inputs="$3"
  local final_directory="$4"
  local manifest_sha
  manifest_sha="$(sha256sum "${manifest}" | awk '{print $1}')"

  if [[ -e "${final_directory}" ]]; then
    if "${project_base}/Validation/validate_pair_directory.sh" \
         "${final_directory}" "${expected_inputs}" "${manifest_sha}" &&
       python3 "${project_base}/tools/merged_pair_provenance.py" validate \
         "${final_directory}" "${manifest}" "${tune}" "${expected_inputs}" \
         "${project_base}" "${analysis_report}" "${freeze_dir}"; then
      echo "VALIDATED_EXISTING_MERGE ${final_directory}"
      return 0
    fi
    echo "ERROR: existing merge directory is stale/invalid; refusing overwrite: ${final_directory}" >&2
    return 4
  fi

  mkdir -p "$(dirname "${final_directory}")"
  local stage
  stage="$(mktemp -d "${final_directory}.partial.XXXXXX")"
  local slot_temp_dir slot_list
  slot_temp_dir="$(mktemp -d "/tmp/hadronization_${tune}_slots_XXXXXX")"
  slot_list="${slot_temp_dir}/slots.txt"
  if ! python3 - "${tune}" "${manifest}" "${expected_inputs}" >"${slot_list}" <<'PY'
import json
import sys
from pathlib import Path

tune, manifest, expected_text = sys.argv[1:]
expected = int(expected_text)
rows = [
    json.loads(line)
    for line in Path(manifest).read_text().splitlines()
    if line.strip()
]
tune_rows = [row for row in rows if row.get("tune") == tune]
slots = [row.get("canonical_slot") for row in tune_rows]
if len(tune_rows) != expected or len(set(slots)) != expected:
    raise SystemExit(
        f"manifest subset for {tune} is not {expected} unique slots"
    )
if any(
    not isinstance(row.get("schema"), str)
    or not row.get("schema")
    or not isinstance(slot, int)
    or isinstance(slot, bool)
    or slot < 0
    for row, slot in zip(tune_rows, slots)
):
    raise SystemExit(f"invalid canonical manifest row for {tune}")
if slots != sorted(slots):
    raise SystemExit(f"canonical slots are not ordered for {tune}")
print(*slots, sep="\n")
PY
  then
    rm -f "${slot_list}"
    rmdir "${slot_temp_dir}"
    echo "ERROR: invalid merge manifest; retained stage ${stage}" >&2
    return 4
  fi

  local merge_log="${stage}/merge.log"
  local status=0
  root -l -b -q \
    "${project_base}/AnalysisScripts/MergeCanonicalAnalysis.C(\"${slot_list}\",\"${analysis_root}/per_job\",\"${tune}\",\"${stage}\",\"${manifest_sha}\",${expected_inputs})" \
    >"${merge_log}" 2>&1 || status=$?
  rm -f "${slot_list}"
  rmdir "${slot_temp_dir}"
  cat "${merge_log}"
  if (( status != 0 )) ||
     [[ "$(grep -c '^CANONICAL_MERGE_SUMMARY ' "${merge_log}")" -ne 1 ]] ||
     grep -qE 'CANONICAL_MERGE_ERROR|segmentation violation|Break +segmentation|cling JIT session error' \
       "${merge_log}"; then
    echo "ERROR: merge failed; retained stage ${stage}" >&2
    return 5
  fi
  "${project_base}/Validation/validate_pair_directory.sh" \
    "${stage}" "${expected_inputs}" "${manifest_sha}"
  python3 "${project_base}/tools/merged_pair_provenance.py" write \
    "${stage}" "${manifest}" "${tune}" "${expected_inputs}" \
    "${project_base}" "${analysis_report}" "${freeze_dir}"
  "${project_base}/Validation/validate_pair_directory.sh" \
    "${stage}" "${expected_inputs}" "${manifest_sha}"
  python3 "${project_base}/tools/merged_pair_provenance.py" validate \
    "${stage}" "${manifest}" "${tune}" "${expected_inputs}" \
    "${project_base}" "${analysis_report}" "${freeze_dir}"

  if [[ -e "${final_directory}" ]]; then
    echo "ERROR: final merge directory appeared before promotion: ${final_directory}" >&2
    return 6
  fi
  mv "${stage}" "${final_directory}"
  echo "PROMOTED_MERGE ${final_directory}"
}

for tune in MONASH JUNCTIONS CLOSEPACKING; do
  merge_one "${tune}" "${freeze_dir}/canonical_manifest.jsonl" \
    "${canonical_inputs_per_tune}" \
    "${analyzed_data_base}/complete_root_${output_tag}_${tune}"
  for block in $(seq 1 10); do
    block_name="$(printf 'block_%02d.jsonl' "${block}")"
    merge_one "${tune}" "${freeze_dir}/${block_name}" \
      "${canonical_inputs_per_block}" \
      "${analyzed_data_base}/SUBSAMPLES_${output_tag}/combined_root_subSamples_${tune}/combined_root_${block}"
  done
done

# Promotion is not complete until every numeric object in every canonical
# pair file is shown to be the union of the same ten deterministic blocks.
# Keep the successful, deterministic validator transcript with the other
# post-production evidence and never silently replace a differing report.
for tune in MONASH JUNCTIONS CLOSEPACKING; do
  closure_report="${analysis_root}/validation/pair_block_closure_${output_tag}_${tune}.log"
  closure_stage="$(mktemp "${analysis_root}/validation/.pair_block_closure_${output_tag}_${tune}.XXXXXX")"
  if ! "${project_base}/Validation/validate_pair_block_closure.sh" \
       "${analyzed_data_base}/complete_root_${output_tag}_${tune}" \
       "${analyzed_data_base}/SUBSAMPLES_${output_tag}/combined_root_subSamples_${tune}" \
       "${canonical_events_per_tune}" >"${closure_stage}" 2>&1; then
    cat "${closure_stage}"
    echo "ERROR: canonical central/ten-block closure failed; retained report ${closure_stage}" >&2
    exit 7
  fi
  cat "${closure_stage}"
  if [[ -e "${closure_report}" ]]; then
    if ! cmp -s "${closure_stage}" "${closure_report}"; then
      echo "ERROR: existing closure report differs; retained candidate ${closure_stage}" >&2
      exit 8
    fi
    rm -f "${closure_stage}"
  else
    mv "${closure_stage}" "${closure_report}"
  fi
  echo "CANONICAL_PAIR_BLOCK_CLOSURE_PASS tune=${tune} report=${closure_report}"
done
