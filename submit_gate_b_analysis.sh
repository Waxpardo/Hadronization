#!/bin/bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  ./submit_gate_b_analysis.sh CAMPAIGN_DIR PRODUCTION_ROOT ANALYSIS_ROOT --dry-run
  ./submit_gate_b_analysis.sh CAMPAIGN_DIR PRODUCTION_ROOT ANALYSIS_ROOT --submit

Validate and queue exactly the nine raw files declared by a Gate-B pilot
manifest. Append --scope=central or --scope=sensitivity to validate and queue
only that declared subset while the other jobs are still running. Directory
discovery and retry are forbidden.
USAGE
}

if [[ ("$#" -ne 4 && "$#" -ne 5) ||
      "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 2
fi
campaign_dir="$(cd "$1" && pwd)"
production_root="$(cd "$2" && pwd)"
analysis_root="$3"
mode="$4"
scope="all"
case "${5:-}" in
  "") ;;
  --scope=central) scope="central" ;;
  --scope=sensitivity) scope="sensitivity" ;;
  *) usage; exit 2 ;;
esac
case "${mode}" in
  --dry-run|--submit) ;;
  *) usage; exit 2 ;;
esac

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_base="${HADRONIZATION_BASE:-${script_dir}}"
project_base="${project_base%/}"
export HADRONIZATION_BASE="${project_base}"
if [[ -n "$(git -C "${project_base}" status --porcelain --untracked-files=no)" ]]; then
  echo "ERROR: Gate-B analysis requires no tracked worktree changes" >&2
  exit 3
fi
python3 "${project_base}/tools/campaign_manifest.py" validate \
  "${campaign_dir}" --implementation-policy ancestor \
  --checkout-root "${project_base}"
source "${project_base}/setupEnv.sh"

mkdir -p "${analysis_root}/validation/raw" \
  "${analysis_root}/condor_logs"/{MONASH,JUNCTIONS,CLOSEPACKING}
analysis_root="$(cd "${analysis_root}" && pwd)"
while IFS=$'\t' read -r tune logical_id successes attempt seed stable_name; do
  raw="${production_root}/raw/${tune}/${stable_name}"
  log="${analysis_root}/validation/raw/${tune}_job$(printf '%03d' "${logical_id}").log"
  if [[ ! -f "${raw}" ]]; then
    echo "ERROR: missing manifest-declared Gate-B raw file: ${raw}" >&2
    exit 4
  fi
  if [[ ! -f "${raw}.sha256" ]] ||
     ! (cd "$(dirname "${raw}")" && sha256sum -c "$(basename "${raw}.sha256")") \
       >>"${log}" 2>&1; then
    echo "ERROR: Gate-B raw checksum verification failed: ${raw}" >&2
    exit 4
  fi
  "${project_base}/Validation/validate_raw_output.sh" \
    "${raw}" \
    "$(basename "${campaign_dir}")" \
    "${tune}" "${logical_id}" "${successes}" "${attempt}" "${seed}" \
    >"${log}" 2>&1
  if ! grep -q 'RAW_VALIDATION_SUMMARY errors=0' "${log}"; then
    echo "ERROR: Gate-B raw validation did not pass: ${log}" >&2
    exit 5
  fi
done < <(
  python3 - "${campaign_dir}/candidate_manifest.jsonl" "${scope}" <<'PY'
import json
import sys
for line in open(sys.argv[1]):
    row = json.loads(line)
    if sys.argv[2] == "central" and row["purpose"] != "one_million_central":
        continue
    if sys.argv[2] == "sensitivity" and row["purpose"] == "one_million_central":
        continue
    print(
        row["tune"],
        row["logical_id"],
        row["requested_successes"],
        row["attempt"],
        row["seed"],
        row["stable_name"],
        sep="\t",
    )
PY
)

submit_file="${analysis_root}/submit_gate_b_analysis_${scope}.sub"
python3 "${project_base}/tools/render_gate_b_analysis_submit.py" \
  "${campaign_dir}" "${project_base}" "${production_root}" \
  "${analysis_root}" "${submit_file}" --scope "${scope}"
if [[ "${mode}" == "--dry-run" ]]; then
  echo "GATE_B_ANALYSIS_DRY_RUN_OK scope=${scope} submit_file=${submit_file}"
  exit 0
fi
condor_submit "${submit_file}"
