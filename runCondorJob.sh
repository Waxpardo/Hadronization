#!/bin/bash
set -euo pipefail

# Canonical campaign mode:
#   runCondorJob.sh --campaign CAMPAIGN CAMPAIGN_ORDINAL TUNE LOGICAL_ID \
#       ROLE ATTEMPT SEED NEVT PTHAT_OVERRIDE MULTIPLICITY_AUDIT_EVENTS \
#       REPOSITORY_COMMIT EFFECTIVE_CARD_SHA256 PRODUCER_EXECUTABLE_SHA256 \
#       [CLUSTER_ID] [PROCESS_ID]
#
# All older argument forms are delegated to the explicitly labelled legacy
# wrapper so completed productions remain reproducible.

if [[ "${1:-}" != "--campaign" ]]; then
  script_dir="$(cd "$(dirname "$0")" && pwd)"
  exec "${script_dir}/runCondorJob_legacy.sh" "$@"
fi
shift

if [[ "$#" -ne 15 ]]; then
  echo "Usage: $0 --campaign CAMPAIGN CAMPAIGN_ORDINAL TUNE LOGICAL_ID ROLE ATTEMPT SEED NEVT PTHAT_OVERRIDE MULTIPLICITY_AUDIT_EVENTS REPOSITORY_COMMIT EFFECTIVE_CARD_SHA256 PRODUCER_EXECUTABLE_SHA256 [CLUSTER_ID] [PROCESS_ID]" >&2
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
pthat_min_override="$9"
multiplicity_audit_events="${10}"
repository_commit="${11}"
effective_card_sha256="${12}"
producer_executable_sha256="${13}"
cluster_id="${14}"
process_id="${15}"

is_uint() {
  [[ "${1:-}" =~ ^[0-9]+$ ]]
}

if [[ ! "${campaign}" =~ ^[A-Za-z0-9._-]+$ ]]; then
  echo "ERROR: campaign may contain only letters, digits, dot, underscore, and hyphen" >&2
  exit 2
fi
for scheduler_value in cluster_id process_id; do
  value="${!scheduler_value}"
  if [[ ! "${value}" =~ ^[A-Za-z0-9._-]+$ ]]; then
    echo "ERROR: ${scheduler_value} contains unsafe characters" >&2
    exit 2
  fi
done

for value_name in campaign_ordinal logical_id attempt seed requested_successes multiplicity_audit_events; do
  value="${!value_name}"
  if ! is_uint "${value}"; then
    echo "ERROR: ${value_name} must be a non-negative integer, got '${value}'" >&2
    exit 2
  fi
done
if (( campaign_ordinal < 1 || campaign_ordinal > 65535 )); then
  echo "ERROR: campaign_ordinal must be in [1,65535]" >&2
  exit 2
fi
if (( attempt > 4095 )); then
  echo "ERROR: attempt must be in [0,4095] for the 12-bit event-ID field" >&2
  exit 2
fi
if (( seed < 1 || seed > 900000000 )); then
  echo "ERROR: seed outside verified PYTHIA domain [1,900000000]" >&2
  exit 2
fi
if (( requested_successes < 1 )); then
  echo "ERROR: requested_successes must be positive" >&2
  exit 2
fi
if (( multiplicity_audit_events > requested_successes )); then
  echo "ERROR: multiplicity_audit_events exceeds requested_successes" >&2
  exit 2
fi
case "${pthat_min_override}" in
  NONE|0.5|1.0|2.0) ;;
  *)
    echo "ERROR: pTHat override must be NONE, 0.5, 1.0, or 2.0" >&2
    exit 2
    ;;
esac
if [[ ! "${repository_commit}" =~ ^[0-9a-f]{40}$ ]]; then
  echo "ERROR: repository_commit must be a lowercase 40-hex SHA" >&2
  exit 2
fi
for hash_name in effective_card_sha256 producer_executable_sha256; do
  value="${!hash_name}"
  if [[ ! "${value}" =~ ^[0-9a-f]{64}$ ]]; then
    echo "ERROR: ${hash_name} must be a lowercase SHA-256" >&2
    exit 2
  fi
done
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
for forbidden_name in \
  HADRONIZATION_BASE \
  HADRONIZATION_CAMPAIGN_DIR \
  HADRONIZATION_PRODUCTION_ROOT \
  HADRONIZATION_PTHAT_MIN_OVERRIDE \
  HADRONIZATION_STORE_MULTIPLICITY_AUDIT_EVENTS \
  HADRONIZATION_FORCE_FAILURES \
  HADRONIZATION_ABORT_AFTER_ATTEMPTS \
  HADRONIZATION_ATTEMPT_CEILING_FACTOR \
  HADRONIZATION_DEBUG_LOCAL_EVENT \
  HADRONIZATION_CONFIG_SHA256 \
  HADRONIZATION_EXECUTABLE_SHA256 \
  HADRONIZATION_REPOSITORY_COMMIT \
  HADRONIZATION_REPOSITORY_DIRTY
do
  if declare -p "${forbidden_name}" >/dev/null 2>&1; then
    echo "ERROR: forbidden inherited campaign control: ${forbidden_name}" >&2
    exit 3
  fi
done
project_base="${script_dir%/}"
export HADRONIZATION_BASE="${project_base}"
campaign_manifest_dir="${project_base}/campaigns/${campaign}"
if [[ ! -d "${campaign_manifest_dir}" ]]; then
  echo "ERROR: campaign production requires its canonical manifest: ${campaign_manifest_dir}" >&2
  exit 3
fi
authorization_args=(
  "${campaign_manifest_dir}" "${campaign}" "${tune}" "${logical_id}"
  "${role}" "${attempt}" "${seed}" "${requested_successes}"
  --campaign-ordinal "${campaign_ordinal}"
  --pthat-min-override "${pthat_min_override}"
  --multiplicity-audit-events "${multiplicity_audit_events}"
  --repository-commit "${repository_commit}"
  --effective-card-sha256 "${effective_card_sha256}"
  --producer-executable-sha256 "${producer_executable_sha256}"
  --checkout-root "${project_base}"
  --cluster-id "${cluster_id}"
  --process-id "${process_id}"
)
authorization_args+=(--require-submission-claim)
python3 "${project_base}/tools/campaign_manifest.py" authorize \
  "${authorization_args[@]}"
if [[ ! -f "${project_base}/setupEnv.sh" ]]; then
  echo "ERROR: setupEnv.sh not found under ${project_base}" >&2
  exit 3
fi

producer_source="${project_base}/SimulationScripts/heavyflavourcorrelations_status"
card="${project_base}/SimulationScripts/${card_name}"
validator_source="${project_base}/Validation/validate_raw_output.sh"
validator_macro_source="${project_base}/Validation/ValidateRawOutput.C"
validator_dependency_sources=(
  "${project_base}/setupEnv.sh"
  "${project_base}/SimulationScripts/HeavyFlavourUtils.h"
  "${project_base}/SimulationScripts/GeneratedHeavyFlavourRegistry.h"
  "${project_base}/SimulationScripts/GeneratedTuneSettingRegistry.h"
  "${project_base}/SimulationScripts/Sha256.h"
  "${project_base}/AnalysisScripts/GeneratedPairRegistry.h"
)
validator_dependency_sources_args=()
for dependency_path in "${validator_dependency_sources[@]}"; do
  validator_dependency_sources_args+=(--dependency "${dependency_path}")
done
for required in \
  "${producer_source}" \
  "${card}" \
  "${validator_source}" \
  "${validator_macro_source}" \
  "${validator_dependency_sources[@]}"
do
  if [[ ! -e "${required}" ]]; then
    echo "ERROR: required campaign component missing: ${required}" >&2
    exit 3
  fi
done
actual_commit="$(git -C "${project_base}" rev-parse HEAD)"
if [[ "${actual_commit}" != "${repository_commit}" ]]; then
  echo "ERROR: checkout commit changed after campaign authorization" >&2
  exit 3
fi
tracked_changes="$(
  git -C "${project_base}" diff --name-only HEAD --
)"
if [[ "${role}" == "pilot" ]]; then
  if [[ -n "${tracked_changes}" ]]; then
    echo "ERROR: checkout became tracked-dirty after campaign authorization" >&2
    exit 3
  fi
else
  allowed_ledger="campaigns/${campaign}/seed_ledger.jsonl"
  while IFS= read -r changed_path; do
    if [[ -n "${changed_path}" && "${changed_path}" != "${allowed_ledger}" ]]; then
      echo "ERROR: unauthorized tracked change after campaign authorization: ${changed_path}" >&2
      exit 3
    fi
  done <<< "${tracked_changes}"
fi
actual_producer_sha256="$(sha256sum "${producer_source}" | awk '{print $1}')"
if [[ "${actual_producer_sha256}" != "${producer_executable_sha256}" ]]; then
  echo "ERROR: producer executable changed after campaign authorization" >&2
  exit 3
fi
expected_phase_space_pthat_min="$(
  python3 "${project_base}/tools/campaign_manifest.py" effective-pthat-min \
    "${card}" "${pthat_min_override}"
)"

validate_raw_output() {
  local validator_wrapper="$1"
  local output="$2"
  "${validator_wrapper}" "${output}" "${campaign}" "${tune}" "${logical_id}" \
    "${requested_successes}" "${attempt}" "${seed}" "${role}" \
    "${campaign_ordinal}" "${expected_phase_space_pthat_min}" \
    "${multiplicity_audit_events}" "${effective_card_sha256}" \
    "${producer_executable_sha256}" "${repository_commit}"
}

campaign_root="${project_base}/Production/${campaign}"
raw_dir="${campaign_root}/raw/${tune}"
partial_dir="${campaign_root}/partial/${tune}"
work_dir="${campaign_root}/work/${tune}/job_$(printf '%03d' "${logical_id}")/attempt_$(printf '%03d' "${attempt}")/${cluster_id}_${process_id}"
quarantine_dir="${campaign_root}/quarantine/${tune}"
metadata_dir="${campaign_root}/attempt_metadata/${tune}"
validation_dir="${campaign_root}/raw_validation/${tune}/job_$(printf '%03d' "${logical_id}")/attempt_$(printf '%03d' "${attempt}")"
attempt_start_dir="${campaign_root}/attempt_starts/${tune}/job_$(printf '%03d' "${logical_id}")"
python3 "${project_base}/tools/campaign_manifest.py" \
  verify-production-directories "${project_base}" "${campaign}" \
  --directory "${raw_dir}" \
  --directory "${partial_dir}" \
  --directory "${work_dir}" \
  --directory "${quarantine_dir}" \
  --directory "${metadata_dir}" \
  --directory "${validation_dir}" \
  --directory "${attempt_start_dir}" \
  --private-directory "${work_dir}"

stable_output="${raw_dir}/hf_${tune}_job$(printf '%03d' "${logical_id}").root"
attempt_stem="hf_${tune}_job$(printf '%03d' "${logical_id}")_attempt$(printf '%03d' "${attempt}")_${cluster_id}_${process_id}"
partial_output="${partial_dir}/${attempt_stem}.partial.root"
sidecar="${metadata_dir}/${attempt_stem}.json"
sidecar_partial="${sidecar}.partial"
validation_log="${validation_dir}/validate_raw_output.log"
validation_receipt="${validation_dir}/receipt.json"
validation_log_partial="${validation_dir}/.validate_raw_output.log.partial.${cluster_id}_${process_id}"
attempt_start_receipt="${attempt_start_dir}/attempt_$(printf '%03d' "${attempt}").json"
raw_validation_provenance_args=(
  --campaign "${campaign}"
  --campaign-ordinal "${campaign_ordinal}"
  --tune "${tune}"
  --logical-id "${logical_id}"
  --role "${role}"
  --attempt "${attempt}"
  --seed "${seed}"
  --requested-successes "${requested_successes}"
  --phase-space-pthat-min "${expected_phase_space_pthat_min}"
  --multiplicity-audit-events "${multiplicity_audit_events}"
  --repository-commit "${repository_commit}"
  --effective-card-sha256 "${effective_card_sha256}"
  --producer-executable-sha256 "${producer_executable_sha256}"
)

if [[ -s "${stable_output}" ]]; then
  if [[ -L "${attempt_start_receipt}" || ! -f "${attempt_start_receipt}" ]]; then
    echo "ERROR: stable output has no regular attempt-start claim: ${attempt_start_receipt}" >&2
    exit 4
  fi
  attempt_start_claim_sha256="$(
    sha256sum "${attempt_start_receipt}" | awk '{print $1}'
  )"
  producing_cluster_id="$(
    python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["cluster_id"])' \
      "${attempt_start_receipt}"
  )"
  producing_process_id="$(
    python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["process_id"])' \
      "${attempt_start_receipt}"
  )"
  raw_validation_provenance_args+=(
    --attempt-start-claim-sha256 "${attempt_start_claim_sha256}"
    --cluster-id "${producing_cluster_id}"
    --process-id "${producing_process_id}"
  )
  if python3 "${project_base}/tools/campaign_manifest.py" verify-raw-validation \
    "${validation_receipt}" \
    "${stable_output}" \
    "${validation_log}" \
    "${validator_source}" \
    "${validator_macro_source}" \
    "${validator_dependency_sources_args[@]}" \
    "${raw_validation_provenance_args[@]}"
  then
    python3 "${project_base}/tools/campaign_manifest.py" \
      write-checksum-sidecar "${stable_output}"
    echo "VERIFIED_EXISTING_VALIDATED_OUTPUT ${stable_output}"
    exit 0
  fi
  quarantine_target="${quarantine_dir}/$(basename "${stable_output}").invalid.$(date -u +%Y%m%dT%H%M%SZ)"
  echo "ERROR: nonempty stable output lacks a matching immutable PASS receipt; refusing to overwrite." >&2
  echo "       Move it to quarantine after review: ${quarantine_target}" >&2
  exit 4
fi
if [[ -e "${partial_output}" ]]; then
  echo "ERROR: unique partial path already exists: ${partial_output}" >&2
  exit 4
fi
if [[ -e "${sidecar}" || -e "${sidecar_partial}" ]]; then
  echo "ERROR: immutable attempt sidecar or partial already exists: ${sidecar}" >&2
  exit 4
fi
if [[ -e "${validation_log}" || -e "${validation_receipt}" ]]; then
  echo "ERROR: immutable raw-validation evidence already exists for this attempt." >&2
  echo "       validation_log=${validation_log}" >&2
  echo "       validation_receipt=${validation_receipt}" >&2
  echo "       Use a new declared attempt after reviewing the existing receipt." >&2
  exit 4
fi
if [[ -e "${validation_log_partial}" ]]; then
  echo "ERROR: unique validation-log partial already exists: ${validation_log_partial}" >&2
  exit 4
fi

if [[ "${pthat_min_override}" != "NONE" && "${role}" != "pilot" ]]; then
  echo "ERROR: pTHat override is restricted to declared pilot jobs" >&2
  exit 3
fi
if (( multiplicity_audit_events > 0 )) && [[ "${role}" != "pilot" ]]; then
  echo "ERROR: multiplicity audit storage is restricted to declared pilots" >&2
  exit 3
fi

job_card="${work_dir}/${card_name}"
python3 "${project_base}/tools/campaign_manifest.py" materialize-effective-card \
  "${card}" "${job_card}" "${requested_successes}" \
  "${pthat_min_override}" "${effective_card_sha256}"
producer="${work_dir}/heavyflavourcorrelations_status"
python3 "${project_base}/tools/campaign_manifest.py" snapshot-executable \
  "${producer_source}" "${producer}" "${producer_executable_sha256}"

validator_root="${work_dir}/sealed_validator"
validator="${validator_root}/Validation/validate_raw_output.sh"
validator_macro="${validator_root}/Validation/ValidateRawOutput.C"
validator_dependencies=(
  "${validator_root}/setupEnv.sh"
  "${validator_root}/SimulationScripts/HeavyFlavourUtils.h"
  "${validator_root}/SimulationScripts/GeneratedHeavyFlavourRegistry.h"
  "${validator_root}/SimulationScripts/GeneratedTuneSettingRegistry.h"
  "${validator_root}/SimulationScripts/Sha256.h"
  "${validator_root}/AnalysisScripts/GeneratedPairRegistry.h"
)
validator_dependencies_args=()
for dependency_path in "${validator_dependencies[@]}"; do
  validator_dependencies_args+=(--dependency "${dependency_path}")
done
validator_source_sha256="$(
  python3 "${project_base}/tools/campaign_manifest.py" tracked-file-sha256 \
    "${project_base}" "${repository_commit}" \
    "Validation/validate_raw_output.sh"
)"
python3 "${project_base}/tools/campaign_manifest.py" snapshot-executable \
  "${validator_source}" "${validator}" "${validator_source_sha256}"
validator_macro_source_sha256="$(
  python3 "${project_base}/tools/campaign_manifest.py" tracked-file-sha256 \
    "${project_base}" "${repository_commit}" \
    "Validation/ValidateRawOutput.C"
)"
python3 "${project_base}/tools/campaign_manifest.py" snapshot-file \
  "${validator_macro_source}" "${validator_macro}" \
  "${validator_macro_source_sha256}"
for dependency_index in "${!validator_dependency_sources[@]}"; do
  dependency_source="${validator_dependency_sources[${dependency_index}]}"
  dependency_destination="${validator_dependencies[${dependency_index}]}"
  dependency_relative="${dependency_source#${project_base}/}"
  dependency_sha256="$(
    python3 "${project_base}/tools/campaign_manifest.py" tracked-file-sha256 \
      "${project_base}" "${repository_commit}" "${dependency_relative}"
  )"
  python3 "${project_base}/tools/campaign_manifest.py" snapshot-file \
    "${dependency_source}" "${dependency_destination}" "${dependency_sha256}"
done
source "${validator_dependencies[0]}"

if (( multiplicity_audit_events > 0 )); then
  export HADRONIZATION_STORE_MULTIPLICITY_AUDIT_EVENTS="${multiplicity_audit_events}"
fi

export HADRONIZATION_CONFIG_SHA256
HADRONIZATION_CONFIG_SHA256="${effective_card_sha256}"
export HADRONIZATION_EXECUTABLE_SHA256
HADRONIZATION_EXECUTABLE_SHA256="${producer_executable_sha256}"
export HADRONIZATION_REPOSITORY_COMMIT
HADRONIZATION_REPOSITORY_COMMIT="${repository_commit}"
export HADRONIZATION_REPOSITORY_DIRTY
HADRONIZATION_REPOSITORY_DIRTY=false
export CLUSTERID="${cluster_id}"
export PROCESSID="${process_id}"

claimed_attempt_start_receipt="$(
  python3 "${project_base}/tools/campaign_manifest.py" claim-attempt-start \
    "${campaign_manifest_dir}" \
    --checkout-root "${project_base}" \
    --campaign "${campaign}" \
    --campaign-ordinal "${campaign_ordinal}" \
    --tune "${tune}" \
    --logical-id "${logical_id}" \
    --role "${role}" \
    --attempt "${attempt}" \
    --seed "${seed}" \
    --requested-successes "${requested_successes}" \
    --repository-commit "${repository_commit}" \
    --effective-card-sha256 "${effective_card_sha256}" \
    --producer-executable-sha256 "${producer_executable_sha256}" \
    --cluster-id "${cluster_id}" \
    --process-id "${process_id}" \
    --private-card "${job_card}" \
    --private-producer "${producer}"
)"
if [[ ! "${claimed_attempt_start_receipt}" -ef "${attempt_start_receipt}" ]]; then
  echo "ERROR: attempt-start helper returned a noncanonical path" >&2
  exit 5
fi
echo "ATTEMPT_START_CLAIMED receipt=${attempt_start_receipt}"
attempt_start_claim_sha256="$(
  sha256sum "${attempt_start_receipt}" | awk '{print $1}'
)"
raw_validation_provenance_args+=(
  --attempt-start-claim-sha256 "${attempt_start_claim_sha256}"
  --cluster-id "${cluster_id}"
  --process-id "${process_id}"
)

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
  partial_bytes="$(wc -c < "${partial_output}" | tr -d '[:space:]')"
fi
printf '{\n  "campaign": "%s",\n  "campaign_ordinal": %s,\n  "tune": "%s",\n  "logical_id": %s,\n  "role": "%s",\n  "attempt": %s,\n  "seed": %s,\n  "requested_successes": %s,\n  "pthat_min_override": "%s",\n  "multiplicity_audit_events": %s,\n  "repository_commit": "%s",\n  "effective_card_sha256": "%s",\n  "producer_executable_sha256": "%s",\n  "attempt_start_claim_path": "%s",\n  "attempt_start_claim_sha256": "%s",\n  "cluster_id": "%s",\n  "process_id": "%s",\n  "start_utc": "%s",\n  "end_utc": "%s",\n  "elapsed_seconds": %s,\n  "producer_exit": %s,\n  "partial_path": "%s",\n  "partial_bytes": %s,\n  "partial_sha256": "%s"\n}\n' \
  "${campaign}" "${campaign_ordinal}" "${tune}" "${logical_id}" "${role}" \
  "${attempt}" "${seed}" "${requested_successes}" "${pthat_min_override}" \
  "${multiplicity_audit_events}" "${repository_commit}" \
  "${effective_card_sha256}" "${producer_executable_sha256}" \
  "${attempt_start_receipt#${project_base}/}" \
  "${attempt_start_claim_sha256}" "${cluster_id}" "${process_id}" \
  "${start_utc}" "${end_utc}" \
  "$((end_epoch - start_epoch))" "${status}" "${partial_output}" \
  "${partial_bytes}" "${partial_sha}" > "${sidecar_partial}"
chmod 0444 "${sidecar_partial}"
python3 "${project_base}/tools/campaign_manifest.py" promote-output \
  "${sidecar_partial}" "${sidecar}"
chmod 0444 "${sidecar}"

if (( status != 0 )); then
  echo "ERROR: producer exited ${status}; partial is not promoted: ${partial_output}" >&2
  exit "${status}"
fi
if [[ -f "${partial_output}" ]]; then
  chmod 0444 "${partial_output}"
fi

validator_status=0
set +e
validate_raw_output "${validator}" "${partial_output}" \
  >"${validation_log_partial}" 2>&1
validator_status=$?
set -e
chmod 0444 "${validation_log_partial}"
validation_log_sha256="$(
  sha256sum "${validation_log_partial}" | awk '{print $1}'
)"
python3 "${project_base}/tools/campaign_manifest.py" promote-output \
  "${validation_log_partial}" "${validation_log}" \
  --expected-sha256 "${validation_log_sha256}"
python3 "${project_base}/tools/campaign_manifest.py" record-raw-validation \
  "${validation_receipt}" \
  "${partial_output}" \
  "${validation_log}" \
  "${validator}" \
  "${validator_macro}" \
  "${validator_dependencies_args[@]}" \
  "${raw_validation_provenance_args[@]}" \
  --validator-status "${validator_status}"
cat "${validation_log}"
if (( validator_status != 0 )); then
  echo "ERROR: validation exited ${validator_status}; partial is not promoted: ${partial_output}" >&2
  echo "       Immutable FAIL receipt: ${validation_receipt}" >&2
  exit 6
fi
if ! python3 "${project_base}/tools/campaign_manifest.py" verify-raw-validation \
  "${validation_receipt}" \
  "${partial_output}" \
  "${validation_log}" \
  "${validator}" \
  "${validator_macro}" \
  "${validator_dependencies_args[@]}" \
  "${raw_validation_provenance_args[@]}"
then
  echo "ERROR: validator output did not produce a matching immutable PASS receipt." >&2
  echo "       Partial is not promoted: ${partial_output}" >&2
  exit 6
fi
if [[ -e "${stable_output}" ]]; then
  echo "ERROR: stable output appeared during validation; refusing to overwrite" >&2
  exit 7
fi
python3 "${project_base}/tools/campaign_manifest.py" promote-output \
  "${partial_output}" "${stable_output}" \
  --expected-sha256 "${partial_sha}"
python3 "${project_base}/tools/campaign_manifest.py" verify-raw-validation \
  "${validation_receipt}" \
  "${stable_output}" \
  "${validation_log}" \
  "${validator}" \
  "${validator_macro}" \
  "${validator_dependencies_args[@]}" \
  "${raw_validation_provenance_args[@]}"
python3 "${project_base}/tools/campaign_manifest.py" \
  write-checksum-sidecar "${stable_output}"
echo "PROMOTED ${stable_output}"
