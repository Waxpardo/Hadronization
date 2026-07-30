#!/bin/bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  ./submit_full_production.sh CAMPAIGN_DIR --dry-run
  ./submit_full_production.sh CAMPAIGN_DIR --submit

The submission path is fail-closed. --submit requires:
  * a clean committed checkout matching campaign.json;
  * a validated first-stage 100/200/200 candidate manifest, or a
    parent-bound equal-tune expansion manifest with A/2A/2A candidates;
  * a sealed PHYSICS_ORIGIN_SIGNOFF.json in CAMPAIGN_DIR, binding the exact
    Gate-B report and its nine-sample unresolved-origin evidence;
  * FULL_PRODUCTION_GATE_AUTHORIZATION.json, binding passing Gates A-D and
    the pTHat decision to an explicit project-owner launch authorization.
  * for an expansion, EQUAL_TUNE_EXPANSION_AUTHORIZATION.json binding the
    sealed parent, failed predeclared coverage/precision report, exact A and
    final N, fresh storage PASS, campaign bytes, and reserved seed interval.

Automatic Condor retries are disabled. Allocate every retry through
tools/campaign_manifest.py allocate-retry and render an explicit retry submit.
USAGE
}

if [[ "$#" -ne 2 || "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 2
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_base="${HADRONIZATION_BASE:-${script_dir}}"
project_base="$(cd "${project_base%/}" && pwd)"
campaign_dir="$(cd "$1" && pwd)"
mode="$2"
case "${mode}" in
  --dry-run|--submit) ;;
  *) usage; exit 2 ;;
esac
if [[ "${mode}" == "--submit" ]]; then
  if [[ -z "${HADRONIZATION_SUBMISSION_REGISTRY_ROOT:-}" ]] ||
     [[ "${HADRONIZATION_SUBMISSION_REGISTRY_ROOT}" != /* ]]; then
    echo "ERROR: --submit requires an absolute shared HADRONIZATION_SUBMISSION_REGISTRY_ROOT" >&2
    exit 3
  fi
fi

python3 "${project_base}/tools/campaign_manifest.py" validate "${campaign_dir}"
campaign_name="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["campaign"])' "${campaign_dir}/campaign.json")"
campaign_commit="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["repository_commit"])' "${campaign_dir}/campaign.json")"
current_commit="$(git -C "${project_base}" rev-parse HEAD)"
if [[ "${campaign_commit}" != "${current_commit}" ]]; then
  echo "ERROR: full campaign commit ${campaign_commit} differs from checkout ${current_commit}" >&2
  exit 3
fi
expected_campaign_dir="${project_base}/campaigns/${campaign_name}"
if [[ "${campaign_dir}" != "${expected_campaign_dir}" ]]; then
  echo "ERROR: full campaign must be under this checkout: ${expected_campaign_dir}" >&2
  exit 3
fi
if [[ -n "$(git -C "${project_base}" status --porcelain --untracked-files=no)" ]]; then
  echo "ERROR: canonical production requires no tracked worktree changes" >&2
  exit 3
fi
"${project_base}/tools/build_producer.sh" "${project_base}"
if [[ -n "$(git -C "${project_base}" status --porcelain --untracked-files=no)" ]] ||
   [[ "$(git -C "${project_base}" rev-parse HEAD)" != "${campaign_commit}" ]]; then
  echo "ERROR: checkout changed while preparing full submission" >&2
  exit 3
fi
producer="${project_base}/SimulationScripts/heavyflavourcorrelations_status"
producer_executable_sha256="$(sha256sum "${producer}" | awk '{print $1}')"

mkdir -p "${project_base}/Production/${campaign_name}/condor_logs"/{MONASH,JUNCTIONS,CLOSEPACKING}
submit_file="${project_base}/Production/${campaign_name}/submit_candidates.sub"
python3 "${project_base}/tools/render_production_submit.py" \
  "${campaign_dir}" "${project_base}" "${submit_file}" --roles all \
  --producer-executable-sha256 "${producer_executable_sha256}"

if [[ "${mode}" == "--dry-run" ]]; then
  echo "PRODUCTION_DRY_RUN_OK submit_file=${submit_file} producer_executable_sha256=${producer_executable_sha256}"
  exit 0
fi

signoff="${campaign_dir}/PHYSICS_ORIGIN_SIGNOFF.json"
if [[ ! -f "${signoff}" ]]; then
  echo "ERROR: required physics sign-off is absent: ${signoff}" >&2
  exit 4
fi
gate_authorization="${campaign_dir}/FULL_PRODUCTION_GATE_AUTHORIZATION.json"
if [[ ! -f "${gate_authorization}" || -L "${gate_authorization}" ]]; then
  echo "ERROR: required immutable Gates A-D owner authorization is absent: ${gate_authorization}" >&2
  exit 4
fi
campaign_kind="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("campaign_kind","first_stage"))' "${campaign_dir}/campaign.json")"
expansion_authorization_args=()
if [[ "${campaign_kind}" == "equal_tune_canonical_expansion_v1" ]]; then
  expansion_authorization="${campaign_dir}/EQUAL_TUNE_EXPANSION_AUTHORIZATION.json"
  if [[ ! -f "${expansion_authorization}" || -L "${expansion_authorization}" ]]; then
    echo "ERROR: required immutable equal-tune expansion authorization is absent: ${expansion_authorization}" >&2
    exit 4
  fi
  expansion_authorization_args=(
    --expansion-authorization-file "${expansion_authorization}"
  )
fi
python3 -c '
import json,sys
row=json.load(open(sys.argv[1]))
required=(
    "schema","decision","approved","reviewer","reviewer_role","decision_utc",
    "finding","allowed_unresolved_treatment","gate_b_report_path",
    "gate_b_report_sha256","gate_b_campaign","gate_b_campaign_ordinal",
    "reviewed_unresolved_trigger_candidates",
    "reviewed_unresolved_trigger_candidates_total",
)
missing=[key for key in required if key not in row]
campaign=json.load(open(sys.argv[2]))
expected={
    "schema": "hf_full_production_origin_signoff_v1",
    "decision": "APPROVE_FULL_PRODUCTION",
    "approved": True,
    "reviewer_role": "project_owner",
    "campaign": campaign["campaign"],
    "campaign_ordinal": campaign["campaign_ordinal"],
    "repository_commit": campaign["repository_commit"],
}
wrong=[key for key,value in expected.items() if row.get(key) != value]
if missing or wrong:
    raise SystemExit(
        "invalid physics sign-off; missing=%s wrong=%s"
        % (missing, wrong)
    )
' "${signoff}" "${campaign_dir}/campaign.json"

claim_path="$(
  python3 "${project_base}/tools/campaign_manifest.py" claim-submission \
    "${campaign_dir}" \
    --checkout-root "${project_base}" \
    --production-root "${project_base}/Production" \
    --submit-file "${submit_file}" \
    --producer "${producer}" \
    --producer-executable-sha256 "${producer_executable_sha256}" \
    --submission-kind full \
    --approval-file "${signoff}" \
    --gate-authorization-file "${gate_authorization}" \
    "${expansion_authorization_args[@]}"
)"
echo "FULL_SUBMISSION_CLAIMED receipt=${claim_path}"
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
  echo "ERROR: immutable submission record exists, but release failed; cluster ${submitted_cluster} remains held" >&2
  exit 6
fi
echo "FULL_PRODUCTION_SUBMITTED result=${condor_result} record=${submitted_record} released_cluster=${submitted_cluster}"
