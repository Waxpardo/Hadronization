#!/bin/bash
set -euo pipefail

if [[ "$#" -ne 2 ]]; then
  echo "Usage: $0 CAMPAIGN_DIR --dry-run|--submit" >&2
  exit 2
fi
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_base="${HADRONIZATION_BASE:-${script_dir}}"
project_base="$(cd "${project_base%/}" && pwd)"
campaign_dir="$(cd "$1" && pwd)"
mode="$2"
case "${mode}" in --dry-run|--submit) ;; *) exit 2 ;; esac
if [[ "${mode}" == "--submit" ]]; then
  if [[ -z "${HADRONIZATION_SUBMISSION_REGISTRY_ROOT:-}" ]] ||
     [[ "${HADRONIZATION_SUBMISSION_REGISTRY_ROOT}" != /* ]]; then
    echo "ERROR: --submit requires an absolute shared HADRONIZATION_SUBMISSION_REGISTRY_ROOT" >&2
    exit 3
  fi
fi
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
campaign_name="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["campaign"])' "${campaign_dir}/campaign.json")"
expected_campaign_dir="${project_base}/campaigns/${campaign_name}"
if [[ "${campaign_dir}" != "${expected_campaign_dir}" ]]; then
  echo "ERROR: Gate-B campaign must be under this checkout: ${expected_campaign_dir}" >&2
  exit 4
fi
"${project_base}/tools/build_producer.sh" "${project_base}"
if [[ -n "$(git -C "${project_base}" status --porcelain --untracked-files=no)" ]] ||
   [[ "$(git -C "${project_base}" rev-parse HEAD)" != "${manifest_commit}" ]]; then
  echo "ERROR: checkout changed while preparing Gate-B submission" >&2
  exit 4
fi
producer="${project_base}/SimulationScripts/heavyflavourcorrelations_status"
producer_executable_sha256="$(sha256sum "${producer}" | awk '{print $1}')"
mkdir -p "${project_base}/Production/${campaign_name}/condor_logs"/{MONASH,JUNCTIONS,CLOSEPACKING}
submit_file="${project_base}/Production/${campaign_name}/submit_gate_b.sub"
python3 "${project_base}/tools/render_production_submit.py" \
  "${campaign_dir}" "${project_base}" "${submit_file}" --roles pilot \
  --producer-executable-sha256 "${producer_executable_sha256}"
if [[ "${mode}" == "--dry-run" ]]; then
  echo "GATE_B_DRY_RUN_OK submit_file=${submit_file} producer_executable_sha256=${producer_executable_sha256}"
  exit 0
fi
claim_path="$(
  python3 "${project_base}/tools/campaign_manifest.py" claim-submission \
    "${campaign_dir}" \
    --checkout-root "${project_base}" \
    --production-root "${project_base}/Production" \
    --submit-file "${submit_file}" \
    --producer "${producer}" \
    --producer-executable-sha256 "${producer_executable_sha256}" \
    --submission-kind gate_b
)"
echo "GATE_B_SUBMISSION_CLAIMED receipt=${claim_path}"
if ! condor_result="$(
  condor_submit -terse -append "hold = True" "${submit_file}"
)"; then
  echo "ERROR: condor_submit failed; immutable claim remains at ${claim_path}" >&2
  exit 5
fi
submitted_record="$(
  python3 "${project_base}/tools/campaign_manifest.py" record-submission \
    "${claim_path}" "${condor_result}" --checkout-root "${project_base}"
)"
submitted_cluster="$(
  python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["condor_cluster_id"])' \
    "${submitted_record}"
)"
if ! condor_release "${submitted_cluster}"; then
  echo "ERROR: immutable Gate-B record exists, but release failed; cluster ${submitted_cluster} remains held" >&2
  exit 6
fi
echo "GATE_B_SUBMITTED result=${condor_result} record=${submitted_record} released_cluster=${submitted_cluster}"
