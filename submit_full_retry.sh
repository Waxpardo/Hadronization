#!/bin/bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  ./submit_full_retry.sh CAMPAIGN_DIR TUNE LOGICAL_ID ATTEMPT --dry-run
  ./submit_full_retry.sh CAMPAIGN_DIR TUNE LOGICAL_ID ATTEMPT --submit

ATTEMPT must already have been allocated append-only with:
  tools/campaign_manifest.py allocate-retry CAMPAIGN_DIR TUNE LOGICAL_ID \
    --reason 'reviewed technical failure' [--scheduler-loss-approval FILE]

This command never allocates a seed and never overwrites a prior retry submit,
claim, or submission record.
USAGE
}

if [[ "$#" -ne 5 || "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 2
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_base="${HADRONIZATION_BASE:-${script_dir}}"
project_base="$(cd "${project_base%/}" && pwd)"
campaign_dir="$(cd "$1" && pwd)"
tune="$2"
logical_id="$3"
attempt="$4"
mode="$5"
case "${tune}" in
  MONASH|JUNCTIONS|CLOSEPACKING) ;;
  *) echo "ERROR: unsupported tune ${tune}" >&2; exit 2 ;;
esac
if [[ ! "${logical_id}" =~ ^[0-9]+$ ]] ||
   [[ ! "${attempt}" =~ ^[1-9][0-9]*$ ]]; then
  echo "ERROR: logical ID must be nonnegative and retry attempt positive" >&2
  exit 2
fi
case "${mode}" in
  --dry-run|--submit) ;;
  *) usage; exit 2 ;;
esac

python3 "${project_base}/tools/campaign_manifest.py" validate \
  "${campaign_dir}" --checkout-root "${project_base}"
campaign_name="$(
  python3 -c \
    'import json,sys; print(json.load(open(sys.argv[1]))["campaign"])' \
    "${campaign_dir}/campaign.json"
)"
campaign_commit="$(
  python3 -c \
    'import json,sys; print(json.load(open(sys.argv[1]))["repository_commit"])' \
    "${campaign_dir}/campaign.json"
)"
if [[ "${campaign_dir}" != "${project_base}/campaigns/${campaign_name}" ]]; then
  echo "ERROR: retry campaign is outside the canonical checkout path" >&2
  exit 3
fi
if [[ "$(git -C "${project_base}" rev-parse HEAD)" != "${campaign_commit}" ]]; then
  echo "ERROR: retry checkout commit differs from campaign" >&2
  exit 3
fi
allowed_ledger="campaigns/${campaign_name}/seed_ledger.jsonl"
while IFS= read -r changed_path; do
  if [[ -n "${changed_path}" && "${changed_path}" != "${allowed_ledger}" ]]; then
    echo "ERROR: unauthorized tracked change during retry: ${changed_path}" >&2
    exit 3
  fi
done < <(git -C "${project_base}" diff --name-only HEAD --)

seed="$(
  python3 -c '
import json,sys
path,tune,logical_id,attempt=sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4])
rows=[
    json.loads(line) for line in open(path)
    if line.strip()
]
matches=[
    row for row in rows
    if row.get("tune")==tune
    and int(row.get("logical_id",-1))==logical_id
    and int(row.get("attempt",-1))==attempt
    and row.get("allocation")=="retry"
]
if len(matches)!=1:
    raise SystemExit("retry allocation is absent or duplicated")
print(int(matches[0]["seed"]))
' "${campaign_dir}/seed_ledger.jsonl" "${tune}" "${logical_id}" "${attempt}"
)"

producer="${project_base}/SimulationScripts/heavyflavourcorrelations_status"
if [[ -L "${producer}" || ! -x "${producer}" ]]; then
  echo "ERROR: canonical producer is absent, nonregular, or nonexecutable" >&2
  exit 3
fi
producer_executable_sha256="$(sha256sum "${producer}" | awk '{print $1}')"
retry_stem="${tune}_job$(printf '%03d' "${logical_id}")_attempt$(printf '%03d' "${attempt}")"
mkdir -p \
  "${project_base}/Production/${campaign_name}/condor_logs/${tune}" \
  "${project_base}/Production/${campaign_name}/retry_submissions"
submit_file="${project_base}/Production/${campaign_name}/retry_submissions/submit_${retry_stem}.sub"
python3 "${project_base}/tools/render_production_submit.py" \
  "${campaign_dir}" "${project_base}" "${submit_file}" \
  --producer-executable-sha256 "${producer_executable_sha256}" \
  --retry-tune "${tune}" \
  --retry-logical-id "${logical_id}" \
  --retry-attempt "${attempt}"

if [[ "${mode}" == "--dry-run" ]]; then
  echo "FULL_RETRY_DRY_RUN_OK submit_file=${submit_file} seed=${seed}"
  exit 0
fi

claim_path="$(
  python3 "${project_base}/tools/campaign_manifest.py" \
    claim-retry-submission "${campaign_dir}" \
    --checkout-root "${project_base}" \
    --production-root "${project_base}/Production" \
    --submit-file "${submit_file}" \
    --producer "${producer}" \
    --producer-executable-sha256 "${producer_executable_sha256}" \
    --tune "${tune}" \
    --logical-id "${logical_id}" \
    --attempt "${attempt}" \
    --seed "${seed}"
)"
echo "FULL_RETRY_SUBMISSION_CLAIMED receipt=${claim_path}"
if ! condor_result="$(
  condor_submit -terse -append "hold = True" "${submit_file}"
)"; then
  echo "ERROR: condor_submit failed; immutable retry claim remains at ${claim_path}" >&2
  exit 5
fi
submitted_record="$(
  python3 "${project_base}/tools/campaign_manifest.py" \
    record-retry-submission "${claim_path}" "${condor_result}" \
    --checkout-root "${project_base}"
)"
submitted_cluster="$(
  python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["condor_cluster_id"])' \
    "${submitted_record}"
)"
if ! condor_release "${submitted_cluster}"; then
  echo "ERROR: immutable retry record exists, but release failed; cluster ${submitted_cluster} remains held" >&2
  exit 6
fi
echo "FULL_RETRY_SUBMITTED result=${condor_result} record=${submitted_record} released_cluster=${submitted_cluster}"
