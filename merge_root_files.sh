#!/bin/bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  ./merge_root_files.sh FREEZE_DIR ANALYSIS_ROOT ANALYZED_DATA_BASE [OUTPUT_TAG]

Merges only manifest-enumerated canonical slots. It creates:
  complete_root_OUTPUT_TAG_{MONASH,JUNCTIONS,CLOSEPACKING}
  SUBSAMPLES_OUTPUT_TAG/combined_root_subSamples_TUNE/combined_root_{1..10}

Each final directory is promoted only after all 300 pair files validate.
Existing final directories are never overwritten.
USAGE
}

if [[ "$#" -lt 3 || "$#" -gt 4 || "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 2
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_base="${HADRONIZATION_BASE:-${script_dir}}"
project_base="${project_base%/}"
export HADRONIZATION_BASE="${project_base}"
source "${project_base}/setupEnv.sh"

freeze_dir="$(cd "$1" && pwd)"
analysis_root="$(cd "$2" && pwd)"
analyzed_data_base="$3"
output_tag="${4:-$(basename "$(dirname "${freeze_dir}")")}"
python3 "${project_base}/tools/canonical_manifest.py" validate "${freeze_dir}"
mkdir -p "${analyzed_data_base}"

merge_one() {
  local tune="$1"
  local manifest="$2"
  local final_directory="$3"
  if [[ -e "${final_directory}" ]]; then
    echo "ERROR: final merge directory exists; refusing overwrite: ${final_directory}" >&2
    return 4
  fi
  local stage
  stage="$(mktemp -d "${final_directory}.partial.XXXXXX")"
  local slot_list="${stage}/canonical_slots.txt"
  python3 -c '
import json,sys
tune=sys.argv[1]
for line in open(sys.argv[2]):
    row=json.loads(line)
    if row["tune"] == tune:
        print(row["canonical_slot"])
' "${tune}" "${manifest}" >"${slot_list}"
  local manifest_sha
  manifest_sha="$(sha256sum "${manifest}" | awk '{print $1}')"
  local merge_log="${stage}/merge.log"
  status=0
  root -l -b -q \
    "${project_base}/AnalysisScripts/MergeCanonicalAnalysis.C(\"${slot_list}\",\"${analysis_root}/per_job\",\"${tune}\",\"${stage}\",\"${manifest_sha}\")" \
    >"${merge_log}" 2>&1 || status=$?
  cat "${merge_log}"
  if (( status != 0 )) ||
     ! grep -q 'CANONICAL_MERGE_SUMMARY' "${merge_log}" ||
     grep -q 'CANONICAL_MERGE_ERROR' "${merge_log}"; then
    echo "ERROR: merge failed; retained stage ${stage}" >&2
    return 5
  fi
  "${project_base}/Validation/validate_pair_directory.sh" "${stage}"
  mv "${stage}" "${final_directory}"
  echo "PROMOTED_MERGE ${final_directory}"
}

for tune in MONASH JUNCTIONS CLOSEPACKING; do
  merge_one "${tune}" "${freeze_dir}/canonical_manifest.jsonl" \
    "${analyzed_data_base}/complete_root_${output_tag}_${tune}"
  for block in $(seq 1 10); do
    block_name="$(printf 'block_%02d.jsonl' "${block}")"
    merge_one "${tune}" "${freeze_dir}/${block_name}" \
      "${analyzed_data_base}/SUBSAMPLES_${output_tag}/combined_root_subSamples_${tune}/combined_root_${block}"
  done
done
