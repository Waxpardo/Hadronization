#!/bin/bash
set -euo pipefail

# Generate, validate, and promote one campaign raw file.
#
#   runCondorJob.sh --campaign CAMPAIGN CAMPAIGN_ORDINAL TUNE LOGICAL_ID \
#       ROLE ATTEMPT SEED NEVT PTHAT_OVERRIDE MULTIPLICITY_AUDIT_EVENTS \
#       REPOSITORY_COMMIT EFFECTIVE_CARD_SHA256 PRODUCER_EXECUTABLE_SHA256 \
#       CARD_VARIANT CLUSTER_ID PROCESS_ID
#
# CARD_VARIANT selects a generated single-setting variation card.
# NONE selects the nominal tune card.
# EFFECTIVE_CARD_SHA256 still pins the selected card.
#
# The worker enforces four boundaries:
#
#   * The checkout matches the recorded commit and has no tracked changes.
#   * The producer digest matches the rendered job row.
#   * The effective-card digest matches the rendered job row.
#   * Raw validation passes before promotion, and promotion never overwrites.
#
# HF_PRODUCTION_ROOT selects external storage; otherwise the worker uses Production/.

if [[ "${1:-}" != "--campaign" ]]; then
  echo "ERROR: only --campaign invocation is supported" >&2
  echo "       older forms: check out the commit that produced that run" >&2
  exit 2
fi
shift

if [[ "$#" -ne 16 ]]; then
  echo "Usage: $0 --campaign CAMPAIGN CAMPAIGN_ORDINAL TUNE LOGICAL_ID ROLE ATTEMPT SEED NEVT PTHAT_OVERRIDE MULTIPLICITY_AUDIT_EVENTS REPOSITORY_COMMIT EFFECTIVE_CARD_SHA256 PRODUCER_EXECUTABLE_SHA256 CARD_VARIANT CLUSTER_ID PROCESS_ID" >&2
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
card_variant="${14}"
cluster_id="${15}"
process_id="${16}"

is_uint() { [[ "$1" =~ ^[0-9]+$ ]]; }
for name in campaign_ordinal logical_id attempt seed requested_successes \
            multiplicity_audit_events; do
  if ! is_uint "${!name}"; then
    echo "ERROR: ${name} must be a non-negative integer, got '${!name}'" >&2
    exit 2
  fi
done
if [[ ! "${campaign}" =~ ^[A-Za-z0-9._-]+$ ]]; then
  echo "ERROR: unsafe campaign name '${campaign}'" >&2
  exit 2
fi
if [[ "${role}" != "primary" && "${role}" != "reserve" && "${role}" != "pilot" ]]; then
  echo "ERROR: role must be primary, reserve, or pilot" >&2
  exit 2
fi
# Lowercase token or the literal NONE. Validated here as well as in
# campaign.py because this value becomes part of a path.
if [[ ! "${card_variant}" =~ ^(NONE|[a-z0-9_]+)$ ]]; then
  echo "ERROR: card_variant must be NONE or a lowercase [a-z0-9_] token, got '${card_variant}'" >&2
  exit 2
fi
for name in repository_commit; do
  if [[ ! "${!name}" =~ ^[0-9a-f]{40}$ ]]; then
    echo "ERROR: ${name} must be a 40-hex commit" >&2
    exit 2
  fi
done
for name in effective_card_sha256 producer_executable_sha256; do
  if [[ ! "${!name}" =~ ^[0-9a-f]{64}$ ]]; then
    echo "ERROR: ${name} must be a 64-hex sha256" >&2
    exit 2
  fi
done

# Published tunes plus JUNCTIONS_MATCHED. The producer derives its mode and its
# card name from the tune, so a new configuration needs one entry here and one
# card file.
#
# card_name is the name the PRODUCER opens, and it is deliberately NOT
# variant-dependent: the producer derives its settings filename from the tune
# alone (heavyflavourcorrelations_status.cpp:144) and reads it relative to the
# working directory. So a variation is materialised into work_dir under the
# nominal filename, with variant CONTENT. The producer needs no change, and
# what the job ran is identified by effective_card_sha256, not by a filename.
case "${tune}" in
  MONASH|JUNCTIONS|CLOSEPACKING|JUNCTIONS_MATCHED)
    mode="$(printf '%s' "${tune}" | tr '[:upper:]' '[:lower:]')"
    card_name="pythiasettings_Hard_Low_ccbb_${tune}.cmnd"
    ;;
  *)
    echo "ERROR: unsupported tune '${tune}'" >&2
    exit 2
    ;;
esac

# A campaign job must be driven by its arguments, never by the submitting
# shell's environment. Inheriting any of these would let a resubmission run
# under settings that no submit file recorded.
for forbidden_name in \
  HADRONIZATION_BASE \
  HADRONIZATION_CAMPAIGN_DIR \
  HADRONIZATION_PTHAT_MIN_OVERRIDE \
  HADRONIZATION_STORE_MULTIPLICITY_AUDIT_EVENTS \
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

script_dir="$(cd "$(dirname "$0")" && pwd)"
# Require this worker's known location before deriving the checkout root.
# External HADRONIZATION_BASE values cannot replace this layout contract.
if [[ "${script_dir}" != */generation/submit ]]; then
  echo "ERROR: worker expects to live at <checkout>/generation/submit, not ${script_dir}" >&2
  echo "       update this derivation deliberately if the layout changed" >&2
  exit 2
fi
project_base="$(cd "${script_dir}/../.." && pwd)"
export HADRONIZATION_BASE="${project_base}"

if [[ "${pthat_min_override}" != "NONE" && "${role}" != "pilot" ]]; then
  echo "ERROR: pTHat override is restricted to declared pilot jobs" >&2
  exit 3
fi
if (( multiplicity_audit_events > 0 )) && [[ "${role}" != "pilot" ]]; then
  echo "ERROR: multiplicity audit storage is restricted to declared pilots" >&2
  exit 3
fi

producer="${project_base}/generation/producer/heavyflavourcorrelations_status"
# The SOURCE card. Resolved by campaign.py rather than assembled here, so the
# renderer (which hashed this file to produce effective_card_sha256) and this
# worker cannot disagree about which file the sha belongs to.
card="$(python3 "${project_base}/tools/campaign.py" card-path \
  "${project_base}" "${tune}" --card-variant "${card_variant}")"
validator="${project_base}/Validation/validate_raw_output.sh"
for required in "${producer}" "${card}" "${validator}" \
                "${project_base}/setupEnv.sh"; do
  if [[ ! -e "${required}" ]]; then
    echo "ERROR: required component missing: ${required}" >&2
    exit 3
  fi
done

# The submit file recorded a commit; if the shared checkout has moved or been
# edited since, this job is not the job that was queued.
actual_commit="$(git -C "${project_base}" rev-parse HEAD)"
if [[ "${actual_commit}" != "${repository_commit}" ]]; then
  echo "ERROR: checkout is at ${actual_commit}, submit recorded ${repository_commit}" >&2
  exit 3
fi
if [[ -n "$(git -C "${project_base}" diff --name-only HEAD --)" ]]; then
  echo "ERROR: checkout has tracked modifications; refusing to produce" >&2
  exit 3
fi
actual_producer_sha256="$(sha256sum "${producer}" | awk '{print $1}')"
if [[ "${actual_producer_sha256}" != "${producer_executable_sha256}" ]]; then
  echo "ERROR: producer binary is ${actual_producer_sha256}, submit recorded ${producer_executable_sha256}" >&2
  echo "       rebuild happened after submission; resubmit rather than continue" >&2
  exit 3
fi

# Resolve the environment BEFORE deciding where output goes.
#
# The submit file sets `getenv = False`, so a Condor job starts with none of
# the submitter's environment: HF_PRODUCTION_ROOT arrives only from
# config/dependencies.local.conf via setupEnv.sh. Computing the data root
# before this point silently fell back to <checkout>/Production and wrote
# hundreds of gigabytes into the git working tree -- the exact thing the
# separate data root exists to prevent. It failed silently because the
# fallback is a valid path.
# shellcheck source=/dev/null
source "${project_base}/setupEnv.sh"

# Data root is deliberately separate from the code checkout.
production_root="${HF_PRODUCTION_ROOT:-${project_base}/Production}"
if [[ "${production_root%/}" == "${project_base%/}"* ]]; then
  echo "WARNING: production root is inside the checkout: ${production_root}" >&2
  echo "         set HF_PRODUCTION_ROOT in config/dependencies.local.conf" >&2
fi
campaign_root="${production_root%/}/${campaign}"
job_tag="job$(printf '%03d' "${logical_id}")"
attempt_tag="attempt$(printf '%03d' "${attempt}")"
raw_dir="${campaign_root}/raw/${tune}"
partial_dir="${campaign_root}/partial/${tune}"
work_dir="${campaign_root}/work/${tune}/${job_tag}/${attempt_tag}/${cluster_id}_${process_id}"
metadata_dir="${campaign_root}/attempt_metadata/${tune}"
validation_dir="${campaign_root}/raw_validation/${tune}/${job_tag}/${attempt_tag}"
mkdir -p "${raw_dir}" "${partial_dir}" "${metadata_dir}" "${validation_dir}"
mkdir -p -m 0700 "${work_dir}"

attempt_stem="hf_${tune}_${job_tag}_${attempt_tag}_${cluster_id}_${process_id}"
stable_output="${raw_dir}/hf_${tune}_${job_tag}.root"
partial_output="${partial_dir}/${attempt_stem}.partial.root"
sidecar="${metadata_dir}/${attempt_stem}.json"
validation_log="${validation_dir}/validate_raw_output.log"
validation_receipt="${validation_dir}/receipt.json"

if [[ -e "${stable_output}" ]]; then
  echo "ERROR: stable output already exists, refusing to overwrite: ${stable_output}" >&2
  exit 7
fi
for unique in "${partial_output}" "${sidecar}" "${validation_log}"; do
  if [[ -e "${unique}" ]]; then
    echo "ERROR: unique per-attempt path already exists: ${unique}" >&2
    exit 4
  fi
done

# Materialise the card the producer will actually read. The producer resolves
# its settings file relative to the working directory, which is why this lands
# in work_dir and the producer is run from there. --expect-sha256 fails closed
# if the result differs from what the submit file committed to.
job_card="${work_dir}/${card_name}"
python3 "${project_base}/tools/campaign.py" materialize-card \
  "${card}" "${job_card}" \
  --events "${requested_successes}" \
  --pthat-min "${pthat_min_override}" \
  --expect-sha256 "${effective_card_sha256}" >/dev/null

expected_phase_space_pthat_min="$(
  python3 "${project_base}/tools/campaign.py" effective-pthat-min \
    "${card}" --pthat-min "${pthat_min_override}"
)"

# setupEnv.sh was already sourced above, before the data root was resolved.

if (( multiplicity_audit_events > 0 )); then
  export HADRONIZATION_STORE_MULTIPLICITY_AUDIT_EVENTS="${multiplicity_audit_events}"
fi
export HADRONIZATION_CONFIG_SHA256="${effective_card_sha256}"
export HADRONIZATION_EXECUTABLE_SHA256="${producer_executable_sha256}"
export HADRONIZATION_REPOSITORY_COMMIT="${repository_commit}"
export HADRONIZATION_REPOSITORY_DIRTY=false
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
  partial_bytes="$(wc -c < "${partial_output}" | tr -d '[:space:]')"
fi

python3 - "${sidecar}" >/dev/null <<PY
import json, sys
json.dump({
    "schema": "hf_attempt_metadata_v2",
    "campaign": "${campaign}", "campaign_ordinal": ${campaign_ordinal},
    "tune": "${tune}", "logical_id": ${logical_id}, "role": "${role}",
    "attempt": ${attempt}, "seed": ${seed},
    "requested_successes": ${requested_successes},
    "card_variant": "${card_variant}",
    "pthat_min_override": "${pthat_min_override}",
    "multiplicity_audit_events": ${multiplicity_audit_events},
    "repository_commit": "${repository_commit}",
    "effective_card_sha256": "${effective_card_sha256}",
    "producer_executable_sha256": "${producer_executable_sha256}",
    "cluster_id": "${cluster_id}", "process_id": "${process_id}",
    "start_utc": "${start_utc}", "end_utc": "${end_utc}",
    "elapsed_seconds": $((end_epoch - start_epoch)),
    "producer_exit": ${status},
    "partial_path": "${partial_output}",
    "partial_bytes": ${partial_bytes},
    "partial_sha256": "${partial_sha}",
}, open(sys.argv[1], "w"), indent=2, sort_keys=True)
PY
chmod 0444 "${sidecar}"

if (( status != 0 )); then
  echo "ERROR: producer exited ${status}; partial is not promoted: ${partial_output}" >&2
  exit "${status}"
fi
if [[ ! -f "${partial_output}" ]]; then
  echo "ERROR: producer exited 0 but wrote no output: ${partial_output}" >&2
  exit 5
fi
chmod 0444 "${partial_output}"

validator_status=0
set +e
"${validator}" "${partial_output}" "${campaign}" "${tune}" "${logical_id}" \
  "${requested_successes}" "${attempt}" "${seed}" "${role}" \
  "${campaign_ordinal}" "${expected_phase_space_pthat_min}" \
  "${multiplicity_audit_events}" "${effective_card_sha256}" \
  "${producer_executable_sha256}" "${repository_commit}" \
  >"${validation_log}" 2>&1
validator_status=$?
set -e
chmod 0444 "${validation_log}"
cat "${validation_log}"

python3 - "${validation_receipt}" >/dev/null <<PY
import hashlib, json, sys
def digest(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()
json.dump({
    "schema": "hf_raw_validation_receipt_v3",
    "campaign": "${campaign}", "tune": "${tune}",
    "logical_id": ${logical_id}, "attempt": ${attempt},
    "validator_status": ${validator_status},
    "state": "PASS" if ${validator_status} == 0 else "FAIL",
    "output_sha256": "${partial_sha}",
    "output_bytes": ${partial_bytes},
    "validation_log_sha256": digest("${validation_log}"),
    "validator_sha256": digest("${validator}"),
    "validator_macro_sha256": digest(
        "${project_base}/Validation/ValidateRawOutput.C"),
    # Name -> SHA-256 of everything that decided this verdict. The flat
    # validator_*_sha256 keys above are kept because tools/evaluate_pthat_
    # sensitivity.py reads them; this map is what the ROOT-side audits
    # (AuditOriginResolution.C, ListUnresolvedOrigins.C) require, and they
    # only assert it is a non-empty object of name -> digest.
    "validator_dependency_sha256": {
        "Validation/validate_raw_output.sh": digest("${validator}"),
        "Validation/ValidateRawOutput.C": digest(
            "${project_base}/Validation/ValidateRawOutput.C"),
    },
    # The full campaign parameter set this attempt was queued under, so an
    # audit can bind a promoted raw file back to its exact submission without
    # trusting the filename. Types must match the Contract struct in
    # Validation/AuditOriginResolution.C:38-59 exactly -- it compares by JSON
    # equality, so cluster_id/process_id are STRINGS and
    # phase_space_pthat_min is a float.
    #
    # attempt_start_claim_sha256 is deliberately absent. It hashed a
    # submission claim, and claims were removed with the gate layer, so no
    # current receipt can carry one and none can be reconstructed.
    "expected_provenance": {
        "campaign": "${campaign}",
        "campaign_ordinal": ${campaign_ordinal},
        "tune": "${tune}",
        "logical_id": ${logical_id},
        "role": "${role}",
        "attempt": ${attempt},
        "seed": ${seed},
        "requested_successes": ${requested_successes},
        "phase_space_pthat_min": float("${expected_phase_space_pthat_min}"),
        "multiplicity_audit_events": ${multiplicity_audit_events},
        "repository_commit": "${repository_commit}",
        "effective_card_sha256": "${effective_card_sha256}",
        "producer_executable_sha256": "${producer_executable_sha256}",
        "cluster_id": "${cluster_id}",
        "process_id": "${process_id}",
    },
    "repository_commit": "${repository_commit}",
}, open(sys.argv[1], "w"), indent=2, sort_keys=True)
PY
chmod 0444 "${validation_receipt}"

if (( validator_status != 0 )); then
  echo "ERROR: validation exited ${validator_status}; partial is not promoted" >&2
  echo "       FAIL receipt: ${validation_receipt}" >&2
  exit 6
fi

if [[ -e "${stable_output}" ]]; then
  echo "ERROR: stable output appeared during validation; refusing to overwrite" >&2
  exit 7
fi
mv -n "${partial_output}" "${stable_output}"
promoted_sha="$(sha256sum "${stable_output}" | awk '{print $1}')"
if [[ "${promoted_sha}" != "${partial_sha}" ]]; then
  echo "ERROR: promoted output changed during promotion" >&2
  exit 7
fi
printf '%s  %s\n' "${promoted_sha}" "$(basename "${stable_output}")" \
  > "${stable_output}.sha256"
chmod 0444 "${stable_output}.sha256"
rm -rf "${work_dir}"
echo "PROMOTED ${stable_output}"
