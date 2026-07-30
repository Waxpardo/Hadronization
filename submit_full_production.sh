#!/bin/bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  ./submit_full_production.sh CAMPAIGN_DIR --dry-run
  ./submit_full_production.sh CAMPAIGN_DIR --submit

The submission path is fail-closed. --submit requires:
  * a clean committed checkout matching campaign.json;
  * a validated 100/200/200 candidate and seed manifest;
  * PHYSICS_ORIGIN_SIGNOFF.json in CAMPAIGN_DIR, explicitly approving the
    documented nonzero ambiguous-trigger treatment.

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
project_base="${project_base%/}"
campaign_dir="$(cd "$1" && pwd)"
mode="$2"
case "${mode}" in
  --dry-run|--submit) ;;
  *) usage; exit 2 ;;
esac

python3 "${project_base}/tools/campaign_manifest.py" validate "${campaign_dir}"
campaign_name="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["campaign"])' "${campaign_dir}/campaign.json")"
campaign_commit="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["repository_commit"])' "${campaign_dir}/campaign.json")"
current_commit="$(git -C "${project_base}" rev-parse HEAD)"
if ! git -C "${project_base}" merge-base --is-ancestor \
    "${campaign_commit}" "${current_commit}"; then
  echo "ERROR: campaign implementation commit ${campaign_commit} is not an ancestor of checkout ${current_commit}" >&2
  exit 3
fi
if [[ -n "$(git -C "${project_base}" status --porcelain --untracked-files=no)" ]]; then
  echo "ERROR: canonical production requires no tracked worktree changes" >&2
  exit 3
fi

mkdir -p "${project_base}/Production/${campaign_name}/condor_logs"/{MONASH,JUNCTIONS,CLOSEPACKING}
submit_file="${project_base}/Production/${campaign_name}/submit_primary.sub"
python3 "${project_base}/tools/render_production_submit.py" \
  "${campaign_dir}" "${project_base}" "${submit_file}" --roles primary

if [[ "${mode}" == "--dry-run" ]]; then
  echo "PRODUCTION_DRY_RUN_OK submit_file=${submit_file}"
  exit 0
fi

signoff="${campaign_dir}/PHYSICS_ORIGIN_SIGNOFF.json"
if [[ ! -f "${signoff}" ]]; then
  echo "ERROR: required physics sign-off is absent: ${signoff}" >&2
  exit 4
fi
python3 -c '
import json,sys
row=json.load(open(sys.argv[1]))
required=("approved","reviewer","date","finding","allowed_unresolved_treatment")
missing=[key for key in required if key not in row]
if missing or row.get("approved") is not True:
    raise SystemExit("invalid physics sign-off; missing=%s approved=%r" % (missing,row.get("approved")))
' "${signoff}"

condor_submit "${submit_file}"
