#!/bin/bash
set -euo pipefail

if [[ "$#" -ne 2 ]]; then
  echo "Usage: $0 CAMPAIGN_DIR --dry-run|--submit" >&2
  exit 2
fi
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_base="${HADRONIZATION_BASE:-${script_dir}}"
project_base="${project_base%/}"
campaign_dir="$(cd "$1" && pwd)"
mode="$2"
case "${mode}" in --dry-run|--submit) ;; *) exit 2 ;; esac
if [[ -n "$(git -C "${project_base}" status --porcelain --untracked-files=no)" ]]; then
  echo "ERROR: Gate-B pilots require no tracked worktree changes" >&2
  exit 3
fi
python3 "${project_base}/tools/campaign_manifest.py" validate "${campaign_dir}"
manifest_commit="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["repository_implementation_commit"])' "${campaign_dir}/campaign.json")"
current_commit="$(git -C "${project_base}" rev-parse HEAD)"
if [[ "${manifest_commit}" != "${current_commit}" ]]; then
  echo "ERROR: Gate-B manifest commit ${manifest_commit} differs from checkout ${current_commit}" >&2
  exit 4
fi
"${project_base}/tools/build_producer.sh" "${project_base}"
campaign_name="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["campaign"])' "${campaign_dir}/campaign.json")"
mkdir -p "${project_base}/Production/${campaign_name}/condor_logs"/{MONASH,JUNCTIONS,CLOSEPACKING}
submit_file="${project_base}/Production/${campaign_name}/submit_gate_b.sub"
python3 "${project_base}/tools/render_production_submit.py" \
  "${campaign_dir}" "${project_base}" "${submit_file}" --roles pilot
if [[ "${mode}" == "--dry-run" ]]; then
  echo "GATE_B_DRY_RUN_OK submit_file=${submit_file}"
  exit 0
fi
condor_submit "${submit_file}"
