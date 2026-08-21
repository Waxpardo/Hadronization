#!/bin/bash
set -euo pipefail

# Canonical one-pass per-logical-file analysis wrapper. It writes 300 signed
# pair files to a unique staging directory, validates the complete directory,
# and promotes it atomically only after all checks pass.

if [[ "$#" -ne 2 && "$#" -ne 9 && "$#" -ne 12 ]]; then
  echo "Usage: $0 RAW_ROOT_FILE FINAL_PAIR_DIRECTORY [CAMPAIGN TUNE LOGICAL_ID RAW_SHA256 ANALYSIS_COMMIT MACRO_SHA256 PURPOSE [CANONICAL_MANIFEST_SHA256 RAW_VALIDATION_RECEIPT RAW_VALIDATION_RECEIPT_SHA256]]" >&2
  exit 2
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_base="${HADRONIZATION_BASE:-${script_dir}}"
project_base="${project_base%/}"
export HADRONIZATION_BASE="${project_base}"

input_file="$1"
final_directory="$2"
validator="${project_base}/Validation/validate_pair_directory.sh"
macro="${project_base}/analysis/status_analysis_THnSparse_qq.C"
# The analysis raw-receipt validator was part of the gate layer.
raw_receipt_validator=""
expected_campaign=""
expected_tune=""
expected_logical_id=""
expected_raw_sha256=""
expected_analysis_commit=""
expected_macro_sha256=""
analysis_purpose="manual"
canonical_manifest_sha256=""
raw_validation_receipt=""
expected_raw_validation_receipt_sha256=""
raw_validation_evidence_mode="direct_preflight_only_v1"
event_filter_modulo="${HADRONIZATION_EVENT_FILTER_MODULO:-0}"
event_filter_remainder="${HADRONIZATION_EVENT_FILTER_REMAINDER:--1}"
if [[ "$#" -ge 9 ]]; then
  expected_campaign="$3"
  expected_tune="$4"
  expected_logical_id="$5"
  expected_raw_sha256="$6"
  expected_analysis_commit="$7"
  expected_macro_sha256="$8"
  analysis_purpose="$9"
fi
if [[ "$#" -eq 12 ]]; then
  canonical_manifest_sha256="${10}"
  raw_validation_receipt="${11}"
  expected_raw_validation_receipt_sha256="${12}"
  raw_validation_evidence_mode="immutable_receipt_plus_direct_preflight_v1"
fi

for required in "${input_file}" "${validator}" "${macro}"; do
  if [[ ! -e "${required}" ]]; then
    echo "ERROR: required analysis component missing: ${required}" >&2
    exit 3
  fi
done

# Where the analysis commit comes from. Deploying from a tracked commit is the
# standing rule; its corollary is that a tree deployed with `git archive` has NO
# .git to interrogate, so the sha must be INJECTED rather than discovered. The
# archive was made from a tracked commit, which is the same guarantee the
# tracked-clean check below provides for a real checkout.
#
# Discovery stays the default. A tree that is neither a checkout nor carries an
# injected sha is a hard error: an unknown provenance is never guessed.
analysis_macro_sha256="$(sha256sum "${macro}" | awk '{print $1}')"
analysis_schema="$(python3 - "${macro}" \
  "${project_base}/config/pair_file_object_contract_v1.json" <<'PY'
import json
import re
import sys
from pathlib import Path

macro, contract_path = map(Path, sys.argv[1:])
matches = re.findall(
    r'constexpr\s+const\s+char\s*\*\s*kAnalysisSchema\s*=\s*"([^"]+)"',
    macro.read_text(),
)
if len(matches) != 1:
    raise SystemExit(
        f"expected exactly one kAnalysisSchema declaration in {macro}, "
        f"found {len(matches)}"
    )
known = set(
    json.loads(contract_path.read_text())["schema_version_tags"].values()
)
if matches[0] not in known:
    raise SystemExit(
        f"producer analysis schema {matches[0]!r} is absent from "
        f"{contract_path}"
    )
print(matches[0])
PY
)"
if [[ -n "${HADRONIZATION_DEPLOYED_ANALYSIS_COMMIT:-}" ]]; then
  analysis_commit="${HADRONIZATION_DEPLOYED_ANALYSIS_COMMIT}"
  analysis_commit_source="injected_deploy_commit_v1"
  if [[ ! "${analysis_commit}" =~ ^[0-9a-f]{40}$ ]]; then
    echo "ERROR: HADRONIZATION_DEPLOYED_ANALYSIS_COMMIT is not a 40-character lowercase sha" >&2
    exit 3
  fi
elif git -C "${project_base}" rev-parse --git-dir >/dev/null 2>&1; then
  analysis_commit="$(git -C "${project_base}" rev-parse HEAD)"
  analysis_commit_source="git_checkout_v1"
  if [[ -n "$(git -C "${project_base}" status --porcelain --untracked-files=no)" ]]; then
    echo "ERROR: analysis worker requires a tracked-clean checkout" >&2
    exit 3
  fi
else
  echo "ERROR: analysis worker tree is not a git checkout and no deploy commit was injected." >&2
  echo "       Set HADRONIZATION_DEPLOYED_ANALYSIS_COMMIT to the tracked commit the tree was archived from." >&2
  exit 3
fi
echo "A2_PROVENANCE_SOURCE source=${analysis_commit_source} commit=${analysis_commit}"
if [[ -n "${expected_analysis_commit}" &&
      "${analysis_commit}" != "${expected_analysis_commit}" ]]; then
  echo "ERROR: analysis checkout commit differs from submitted commit" >&2
  exit 3
fi
if [[ -n "${expected_macro_sha256}" &&
      "${analysis_macro_sha256}" != "${expected_macro_sha256}" ]]; then
  echo "ERROR: analysis macro checksum differs from submitted checksum" >&2
  exit 3
fi
if [[ -n "${expected_raw_sha256}" ]]; then
  input_sha256="$(sha256sum "${input_file}" | awk '{print $1}')"
  if [[ "${input_sha256}" != "${expected_raw_sha256}" ]]; then
    echo "ERROR: raw input checksum differs from submitted checksum" >&2
    exit 3
  fi
else
  input_sha256="$(sha256sum "${input_file}" | awk '{print $1}')"
fi
if [[ -n "${expected_logical_id}" &&
      ! "${expected_logical_id}" =~ ^[0-9]+$ ]]; then
  echo "ERROR: invalid submitted logical ID" >&2
  exit 3
fi
if [[ -n "${canonical_manifest_sha256}" &&
      ! "${canonical_manifest_sha256}" =~ ^[0-9a-f]{64}$ ]]; then
  echo "ERROR: invalid canonical-manifest checksum" >&2
  exit 3
fi
if [[ -n "${raw_validation_receipt}" ]]; then
  if [[ -L "${raw_validation_receipt}" ||
        ! -f "${raw_validation_receipt}" ]]; then
    echo "ERROR: raw-validation receipt is absent, symlinked, or not regular" >&2
    exit 3
  fi
  if [[ ! "${expected_raw_validation_receipt_sha256}" =~ ^[0-9a-f]{64}$ ]]; then
    echo "ERROR: invalid raw-validation receipt checksum" >&2
    exit 3
  fi
  actual_raw_validation_receipt_sha256="$(
    sha256sum "${raw_validation_receipt}" | awk '{print $1}'
  )"
  if [[ "${actual_raw_validation_receipt_sha256}" != "${expected_raw_validation_receipt_sha256}" ]]; then
    echo "ERROR: raw-validation receipt checksum differs from submission" >&2
    exit 3
  fi
  # The receipt exists and its checksum matches what the submission recorded,
  # which is checked above. The deeper receipt-to-campaign cross-binding was
  # part of the gate layer's authorisation chain.
elif [[ -n "${canonical_manifest_sha256}" ]]; then
  echo "ERROR: canonical analysis requires its immutable raw-validation receipt" >&2
  exit 3
fi
if [[ ! "${event_filter_modulo}" =~ ^[0-9]+$ ]] ||
   [[ ! "${event_filter_remainder}" =~ ^-?[0-9]+$ ]]; then
  echo "ERROR: event-filter modulo/remainder must be integers" >&2
  exit 3
fi
if (( event_filter_modulo == 0 )); then
  if (( event_filter_remainder != -1 )); then
    echo "ERROR: the all-event filter requires remainder -1" >&2
    exit 3
  fi
elif (( event_filter_modulo < 2 ||
        event_filter_remainder < 0 ||
        event_filter_remainder >= event_filter_modulo )); then
  echo "ERROR: invalid event-ID modulo filter" >&2
  exit 3
fi

export HADRONIZATION_ANALYSIS_COMMIT="${analysis_commit}"
export HADRONIZATION_ANALYSIS_MACRO_SHA256="${analysis_macro_sha256}"
export HADRONIZATION_ANALYSIS_PROFILE="central_primary_ground_v1"
export HADRONIZATION_RAW_INPUT_SHA256="${input_sha256}"
export HADRONIZATION_EXPECTED_RAW_SHA256="${input_sha256}"
export HADRONIZATION_EXPECTED_CAMPAIGN="${expected_campaign}"
export HADRONIZATION_EXPECTED_TUNE="${expected_tune}"
export HADRONIZATION_EXPECTED_LOGICAL_ID="${expected_logical_id}"
export HADRONIZATION_RAW_VALIDATION_EVIDENCE_MODE="${raw_validation_evidence_mode}"
export HADRONIZATION_RAW_VALIDATION_RECEIPT_SHA256="${expected_raw_validation_receipt_sha256}"
source "${project_base}/setupEnv.sh"

verify_analysis_checkout() {
  local current_commit current_macro_sha256
  current_macro_sha256="$(sha256sum "${macro}" | awk '{print $1}')"
  if [[ "${current_macro_sha256}" != "${analysis_macro_sha256}" ]]; then
    echo "ERROR: analysis macro changed after worker provenance was pinned" >&2
    return 1
  fi
  # An archived tree has no git to re-interrogate. The macro checksum above is
  # what remains checkable there, and it is the thing that could actually
  # change under the running job.
  if [[ "${analysis_commit_source}" != "git_checkout_v1" ]]; then
    return 0
  fi
  current_commit="$(git -C "${project_base}" rev-parse HEAD)"
  if [[ "${current_commit}" != "${analysis_commit}" ]] ||
     [[ -n "$(git -C "${project_base}" status --porcelain --untracked-files=no)" ]]; then
    echo "ERROR: analysis checkout changed after worker provenance was pinned" >&2
    return 1
  fi
}

validate_existing_job_metadata() {
  local metadata_path="${final_directory}/analysis_job_metadata.json"
  local existing_log="${final_directory}/analysis.log"
  if [[ -L "${metadata_path}" || ! -f "${metadata_path}" ]]; then
    echo "ERROR: existing analysis metadata is absent or non-regular" >&2
    return 1
  fi
  if [[ -L "${existing_log}" || ! -f "${existing_log}" ]] ||
     [[ "$(grep -c '^ONE_PASS_ANALYSIS_SUMMARY ' "${existing_log}")" -ne 1 ]] ||
     grep -qE 'ONE_PASS_ANALYSIS_ERROR|segmentation violation|Break +segmentation|cling JIT session error' \
       "${existing_log}"; then
    echo "ERROR: existing analysis log does not certify one clean run" >&2
    return 1
  fi
  python3 - "${metadata_path}" "${input_file}" "${input_sha256}" \
    "${analysis_commit}" "${analysis_macro_sha256}" \
    "${expected_campaign}" "${expected_tune}" "${expected_logical_id}" \
    "${analysis_purpose}" "${canonical_manifest_sha256}" \
    "${event_filter_modulo}" "${event_filter_remainder}" \
    "${raw_validation_evidence_mode}" "${raw_validation_receipt}" \
    "${expected_raw_validation_receipt_sha256}" \
    "${analysis_schema}" <<'PY'
import json
import sys
from pathlib import Path

(
    metadata_path,
    raw_input,
    raw_sha256,
    repository_commit,
    macro_sha256,
    campaign,
    tune,
    logical_id,
    purpose,
    manifest_sha256,
    event_filter_modulo,
    event_filter_remainder,
    evidence_mode,
    receipt,
    receipt_sha256,
    analysis_schema,
) = sys.argv[1:]
payload = json.loads(Path(metadata_path).read_text())
expected = {
    "schema": "hf_analysis_job_metadata_v3",
    "analysis_schema": analysis_schema,
    "analysis_implementation": "one_pass_primary_ground_pair_analysis_v2",
    "analysis_version": "status_analysis_THnSparse_qq_v2",
    "analysis_profile": "central_primary_ground_v1",
    "pair_combinatorics_mode": "ordered_conditional_v1",
    "event_filter_schema": (
        "all_events_v1"
        if int(event_filter_modulo) == 0
        else "unsigned_event_id_modulo_v1"
    ),
    "event_filter_modulo": int(event_filter_modulo),
    "event_filter_remainder": int(event_filter_remainder),
    "same_sign_pair_factor": 1.0,
    "analysis_macro_sha256": macro_sha256,
    "raw_sha256": raw_sha256,
    "raw_schema": "hf_primary_ground_raw_v7",
    "raw_input_validation_contract": "analysis_raw_input_fail_closed_v1",
    "raw_validation_evidence_mode": evidence_mode,
    "raw_validation_receipt": receipt or None,
    "raw_validation_receipt_schema": (
        "hf_raw_validation_receipt_v1" if receipt else None
    ),
    "raw_validation_receipt_sha256": receipt_sha256 or None,
    "origin_algorithm":
        "signed_heavy_constituent_complete_mothers_unique_v4",
    "repository_commit": repository_commit,
    "repository_dirty": False,
    "selector":
        "hard_trigger_primary_ground__primary_ground_associate_v1",
    "campaign": campaign or None,
    "tune": tune or None,
    "logical_id": int(logical_id) if logical_id else None,
    "purpose": purpose,
    "canonical_manifest_sha256": manifest_sha256 or None,
}
for key, value in expected.items():
    if payload.get(key) != value:
        raise ValueError(
            f"existing analysis metadata {key} differs: "
            f"{payload.get(key)!r} != {value!r}"
        )
if Path(payload.get("raw_input", "")).resolve() != Path(raw_input).resolve():
    raise ValueError("existing analysis raw path differs")
PY
}

if [[ -d "${final_directory}" ]]; then
  if "${validator}" "${final_directory}" &&
     validate_existing_job_metadata &&
     verify_analysis_checkout; then
    echo "VALIDATED_EXISTING_ANALYSIS ${final_directory}"
    exit 0
  fi
  echo "ERROR: existing analysis directory is invalid; refusing overwrite: ${final_directory}" >&2
  exit 4
fi

parent_directory="$(dirname "${final_directory}")"
mkdir -p "${parent_directory}"
stage_directory="$(mktemp -d "${final_directory}.partial.XXXXXX")"
analysis_log="${stage_directory}/analysis.log"

status=0
root -l -b -q \
  "${macro}(\"${input_file}\",\"${stage_directory}\",\"central_primary_ground_v1\",${event_filter_modulo},${event_filter_remainder})" \
  >"${analysis_log}" 2>&1 || status=$?
cat "${analysis_log}"
if (( status != 0 )) ||
   [[ "$(grep -c '^ONE_PASS_ANALYSIS_SUMMARY ' "${analysis_log}")" -ne 1 ]] ||
   grep -q 'ONE_PASS_ANALYSIS_ERROR' "${analysis_log}" ||
   grep -qE 'segmentation violation|Break +segmentation|cling JIT session error' \
     "${analysis_log}"; then
  echo "ERROR: one-pass analysis failed; retained stage: ${stage_directory}" >&2
  exit 5
fi
if ! verify_analysis_checkout; then
  echo "ERROR: retained stage after checkout-provenance failure: ${stage_directory}" >&2
  exit 5
fi

if ! "${validator}" "${stage_directory}"; then
  echo "ERROR: pair-directory validation failed; retained stage: ${stage_directory}" >&2
  exit 6
fi
if ! verify_analysis_checkout; then
  echo "ERROR: retained stage after checkout-provenance failure: ${stage_directory}" >&2
  exit 6
fi

python3 - "${stage_directory}/analysis_job_metadata.json" \
  "${input_file}" "${input_sha256}" "${analysis_commit}" \
  "${analysis_macro_sha256}" "${expected_campaign}" "${expected_tune}" \
  "${expected_logical_id}" "${analysis_purpose}" \
  "${canonical_manifest_sha256}" "${event_filter_modulo}" \
  "${event_filter_remainder}" "${raw_validation_evidence_mode}" \
  "${raw_validation_receipt}" \
  "${expected_raw_validation_receipt_sha256}" \
  "${analysis_schema}" <<'PY'
import json
import sys
from pathlib import Path

(
    output,
    raw_input,
    raw_sha256,
    repository_commit,
    macro_sha256,
    campaign,
    tune,
    logical_id,
    purpose,
    canonical_manifest_sha256,
    event_filter_modulo,
    event_filter_remainder,
    raw_validation_evidence_mode,
    raw_validation_receipt,
    raw_validation_receipt_sha256,
    analysis_schema,
) = sys.argv[1:]
event_filter_modulo = int(event_filter_modulo)
event_filter_remainder = int(event_filter_remainder)
metadata = {
    "schema": "hf_analysis_job_metadata_v3",
    "analysis_schema": analysis_schema,
    "analysis_implementation": "one_pass_primary_ground_pair_analysis_v2",
    "analysis_version": "status_analysis_THnSparse_qq_v2",
    "analysis_profile": "central_primary_ground_v1",
    "pair_combinatorics_mode": "ordered_conditional_v1",
    "same_sign_pair_factor": 1.0,
    "analysis_macro_sha256": macro_sha256,
    "raw_input": raw_input,
    "raw_sha256": raw_sha256,
    "raw_schema": "hf_primary_ground_raw_v7",
    "raw_input_validation_contract": "analysis_raw_input_fail_closed_v1",
    "raw_validation_evidence_mode": raw_validation_evidence_mode,
    "raw_validation_receipt": raw_validation_receipt or None,
    "raw_validation_receipt_schema": (
        "hf_raw_validation_receipt_v1"
        if raw_validation_receipt
        else None
    ),
    "raw_validation_receipt_sha256":
        raw_validation_receipt_sha256 or None,
    "origin_algorithm":
        "signed_heavy_constituent_complete_mothers_unique_v4",
    "repository_commit": repository_commit,
    "repository_dirty": False,
    "selector": "hard_trigger_primary_ground__primary_ground_associate_v1",
    "campaign": campaign or None,
    "tune": tune or None,
    "logical_id": int(logical_id) if logical_id else None,
    "purpose": purpose,
    "canonical_manifest_sha256": canonical_manifest_sha256 or None,
    "event_filter_schema": (
        "all_events_v1"
        if event_filter_modulo == 0
        else "unsigned_event_id_modulo_v1"
    ),
    "event_filter_modulo": event_filter_modulo,
    "event_filter_remainder": event_filter_remainder,
}
Path(output).write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
PY

if [[ -e "${final_directory}" ]]; then
  echo "ERROR: final analysis directory appeared before promotion" >&2
  exit 7
fi
mv "${stage_directory}" "${final_directory}"
echo "PROMOTED_ANALYSIS ${final_directory}"
