#!/bin/bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  ./submit_status_analysis.sh FREEZE_DIR PRODUCTION_ROOT ANALYSIS_ROOT --dry-run
  ./submit_status_analysis.sh FREEZE_DIR PRODUCTION_ROOT ANALYSIS_ROOT --submit

Only paths enumerated in FREEZE_DIR/canonical_manifest.jsonl are queued.
Directory discovery, "first N files", and reserve over-inclusion are forbidden.
USAGE
}

if [[ "$#" -ne 4 || "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 2
fi
freeze_dir="$(cd "$1" && pwd)"
production_root="$(cd "$2" && pwd)"
analysis_root="$3"
mode="$4"
case "${mode}" in
  --dry-run|--submit) ;;
  *) usage; exit 2 ;;
esac

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_base="${HADRONIZATION_BASE:-${script_dir}}"
project_base="${project_base%/}"
python3 "${project_base}/tools/canonical_manifest.py" validate "${freeze_dir}"
mkdir -p "${analysis_root}"/condor_logs/{MONASH,JUNCTIONS,CLOSEPACKING}
submit_file="${analysis_root}/submit_canonical_analysis.sub"
python3 "${project_base}/tools/render_analysis_submit.py" \
  "${freeze_dir}/canonical_manifest.jsonl" "${project_base}" \
  "${production_root}" "${analysis_root}" "${submit_file}"
if [[ "${mode}" == "--dry-run" ]]; then
  echo "ANALYSIS_DRY_RUN_OK submit_file=${submit_file}"
  exit 0
fi
condor_submit "${submit_file}"
