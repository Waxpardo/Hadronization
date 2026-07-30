#!/bin/bash
set -euo pipefail

# Canonical campaign mode:
#   runCondorJob.sh --campaign CAMPAIGN CAMPAIGN_ORDINAL TUNE LOGICAL_ID \
#       ROLE ATTEMPT SEED NEVT [CLUSTER_ID] [PROCESS_ID]
#
# All older argument forms are delegated to the explicitly labelled legacy
# wrapper so completed productions remain reproducible.

if [[ "${1:-}" != "--campaign" ]]; then
  script_dir="$(cd "$(dirname "$0")" && pwd)"
  exec "${script_dir}/runCondorJob_legacy.sh" "$@"
fi
shift

if [[ "$#" -lt 8 || "$#" -gt 10 ]]; then
  echo "Usage: $0 --campaign CAMPAIGN CAMPAIGN_ORDINAL TUNE LOGICAL_ID ROLE ATTEMPT SEED NEVT [CLUSTER_ID] [PROCESS_ID]" >&2
  exit 2
fi

campaign="$1"
campaign_ordinal="$2"
tune="$3"
logical_id="$4"
role="$5"
attempt="$6"
seed="$7"
requested_successes="$8"
cluster_id="${9:-${CLUSTERID:-manual}}"
process_id="${10:-${PROCESSID:-manual}}"

is_uint() {
  [[ "${1:-}" =~ ^[0-9]+$ ]]
}

for value_name in campaign_ordinal logical_id attempt seed requested_successes; do
  value="${!value_name}"
  if ! is_uint "${value}"; then
    echo "ERROR: ${value_name} must be a non-negative integer, got '${value}'" >&2
    exit 2
  fi
done
if (( seed < 1 || seed > 900000000 )); then
  echo "ERROR: seed outside verified PYTHIA domain [1,900000000]" >&2
  exit 2
fi
if [[ "${role}" != "primary" && "${role}" != "reserve" && "${role}" != "pilot" ]]; then
  echo "ERROR: role must be primary, reserve, or pilot" >&2
  exit 2
fi
case "${tune}" in
  MONASH)
    mode="monash"
    card_name="pythiasettings_Hard_Low_ccbb_MONASH.cmnd"
    ;;
  JUNCTIONS)
    mode="junctions"
    card_name="pythiasettings_Hard_Low_ccbb_JUNCTIONS.cmnd"
    ;;
  CLOSEPACKING)
    mode="closepacking"
    card_name="pythiasettings_Hard_Low_ccbb_CLOSEPACKING.cmnd"
    ;;
  *)
    echo "ERROR: unsupported tune '${tune}'" >&2
    exit 2
    ;;
esac

script_dir="$(cd "$(dirname "$0")" && pwd)"
project_base="${HADRONIZATION_BASE:-${script_dir}}"
project_base="${project_base%/}"
export HADRONIZATION_BASE="${project_base}"
campaign_manifest_dir="${HADRONIZATION_CAMPAIGN_DIR:-${project_base}/campaigns/${campaign}}"
if [[ -d "${campaign_manifest_dir}" ]]; then
  python3 "${project_base}/tools/campaign_manifest.py" authorize \
    "${campaign_manifest_dir}" "${campaign}" "${tune}" "${logical_id}" \
    "${role}" "${attempt}" "${seed}" "${requested_successes}"
elif [[ "${role}" != "pilot" ]]; then
  echo "ERROR: canonical/reserve production requires a campaign manifest: ${campaign_manifest_dir}" >&2
  exit 3
else
  echo "WARNING: unmanifested development pilot ${campaign}" >&2
fi
if [[ ! -f "${project_base}/setupEnv.sh" ]]; then
  echo "ERROR: setupEnv.sh not found under ${project_base}" >&2
  exit 3
fi
source "${project_base}/setupEnv.sh"

producer="${project_base}/SimulationScripts/heavyflavourcorrelations_status"
card="${project_base}/SimulationScripts/${card_name}"
validator="${project_base}/Validation/validate_raw_output.sh"
for required in "${producer}" "${card}" "${validator}"; do
  if [[ ! -e "${required}" ]]; then
    echo "ERROR: required campaign component missing: ${required}" >&2
    exit 3
  fi
done

campaign_root="${HADRONIZATION_PRODUCTION_ROOT:-${project_base}/Production}/${campaign}"
raw_dir="${campaign_root}/raw/${tune}"
partial_dir="${campaign_root}/partial/${tune}"
work_dir="${campaign_root}/work/${tune}/job_$(printf '%03d' "${logical_id}")/attempt_$(printf '%03d' "${attempt}")"
quarantine_dir="${campaign_root}/quarantine/${tune}"
metadata_dir="${campaign_root}/attempt_metadata/${tune}"
mkdir -p "${raw_dir}" "${partial_dir}" "${work_dir}" "${quarantine_dir}" "${metadata_dir}"

stable_output="${raw_dir}/hf_${tune}_job$(printf '%03d' "${logical_id}").root"
attempt_stem="hf_${tune}_job$(printf '%03d' "${logical_id}")_attempt$(printf '%03d' "${attempt}")_${cluster_id}_${process_id}"
partial_output="${partial_dir}/${attempt_stem}.partial.root"
sidecar="${metadata_dir}/${attempt_stem}.json"

if [[ -e "${partial_output}" ]]; then
  echo "ERROR: unique partial path already exists: ${partial_output}" >&2
  exit 4
fi

if [[ -s "${stable_output}" ]]; then
  if "${validator}" "${stable_output}" "${campaign}" "${tune}" "${logical_id}" "${requested_successes}"; then
    echo "VALIDATED_EXISTING_OUTPUT ${stable_output}"
    exit 0
  fi
  quarantine_target="${quarantine_dir}/$(basename "${stable_output}").invalid.$(date -u +%Y%m%dT%H%M%SZ)"
  echo "ERROR: nonempty stable output failed validation; refusing to overwrite." >&2
  echo "       Move it to quarantine after review: ${quarantine_target}" >&2
  exit 4
fi

job_card="${work_dir}/${card_name}"
cp "${card}" "${job_card}"
if grep -q '^Main:numberOfEvents' "${job_card}"; then
  sed -i "s/^Main:numberOfEvents.*/Main:numberOfEvents = ${requested_successes}/" "${job_card}"
else
  printf '\nMain:numberOfEvents = %s\n' "${requested_successes}" >> "${job_card}"
fi

if [[ -n "${HADRONIZATION_PTHAT_MIN_OVERRIDE:-}" ]]; then
  if [[ "${role}" != "pilot" ]]; then
    echo "ERROR: pTHat override is restricted to declared pilot jobs" >&2
    exit 3
  fi
  case "${HADRONIZATION_PTHAT_MIN_OVERRIDE}" in
    0.5|1.0|2.0) ;;
    *)
      echo "ERROR: pilot pTHat override must be 0.5, 1.0, or 2.0" >&2
      exit 3
      ;;
  esac
  sed -i \
    "s/^PhaseSpace:pTHatMin.*/PhaseSpace:pTHatMin = ${HADRONIZATION_PTHAT_MIN_OVERRIDE}/" \
    "${job_card}"
fi

export HADRONIZATION_CONFIG_SHA256
HADRONIZATION_CONFIG_SHA256="$(sha256sum "${job_card}" | awk '{print $1}')"
export HADRONIZATION_EXECUTABLE_SHA256
HADRONIZATION_EXECUTABLE_SHA256="$(sha256sum "${producer}" | awk '{print $1}')"
export HADRONIZATION_REPOSITORY_COMMIT
HADRONIZATION_REPOSITORY_COMMIT="$(git -C "${project_base}" rev-parse HEAD 2>/dev/null || printf UNRECORDED)"
export HADRONIZATION_REPOSITORY_DIRTY
if [[ -n "$(git -C "${project_base}" status --porcelain --untracked-files=no 2>/dev/null)" ]]; then
  HADRONIZATION_REPOSITORY_DIRTY=true
else
  HADRONIZATION_REPOSITORY_DIRTY=false
fi
export CLUSTERID="${cluster_id}"
export PROCESSID="${process_id}"

start_utc="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
start_epoch="$(date +%s)"
status=0
(
  cd "${work_dir}"
  "${producer}" "${mode}" "${partial_output}" "${seed}" "${campaign}" \
    "${campaign_ordinal}" "${logical_id}" "${role}" "${attempt}"
) || status=$?
end_epoch="$(date +%s)"
end_utc="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

partial_sha=""
partial_bytes=0
if [[ -f "${partial_output}" ]]; then
  partial_sha="$(sha256sum "${partial_output}" | awk '{print $1}')"
  partial_bytes="$(stat -c %s "${partial_output}")"
fi
printf '{\n  "campaign": "%s",\n  "tune": "%s",\n  "logical_id": %s,\n  "role": "%s",\n  "attempt": %s,\n  "seed": %s,\n  "requested_successes": %s,\n  "cluster_id": "%s",\n  "process_id": "%s",\n  "start_utc": "%s",\n  "end_utc": "%s",\n  "elapsed_seconds": %s,\n  "producer_exit": %s,\n  "partial_path": "%s",\n  "partial_bytes": %s,\n  "partial_sha256": "%s"\n}\n' \
  "${campaign}" "${tune}" "${logical_id}" "${role}" "${attempt}" "${seed}" \
  "${requested_successes}" "${cluster_id}" "${process_id}" "${start_utc}" \
  "${end_utc}" "$((end_epoch - start_epoch))" "${status}" "${partial_output}" \
  "${partial_bytes}" "${partial_sha}" > "${sidecar}"

if (( status != 0 )); then
  echo "ERROR: producer exited ${status}; partial is not promoted: ${partial_output}" >&2
  exit "${status}"
fi
if ! "${validator}" "${partial_output}" "${campaign}" "${tune}" "${logical_id}" "${requested_successes}" "${attempt}" "${seed}"; then
  echo "ERROR: validation failed; partial is not promoted: ${partial_output}" >&2
  exit 6
fi
if [[ -e "${stable_output}" ]]; then
  echo "ERROR: stable output appeared during validation; refusing to overwrite" >&2
  exit 7
fi
mv "${partial_output}" "${stable_output}"
sha256sum "${stable_output}" > "${stable_output}.sha256"
echo "PROMOTED ${stable_output}"
