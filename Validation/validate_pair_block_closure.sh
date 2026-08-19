#!/bin/bash
set -euo pipefail

if [[ "$#" -lt 3 || "$#" -gt 4 ]]; then
  cat >&2 <<'USAGE'
Usage:
  validate_pair_block_closure.sh CENTRAL_DIRECTORY BLOCK_BASE_DIRECTORY \
                                 EXPECTED_SCHEMA [EXPECTED_CENTRAL_EVENTS]

EXPECTED_SCHEMA is REQUIRED and is the schema the CAMPAIGN demands -- `v2` or
`v3`, or the full tag. It is deliberately NOT derived from the data.

WHY IT IS REQUIRED (review finding A4). This gate used to read the schema out of
the input and then derive its expected counts FOR THAT SCHEMA. A complete,
internally consistent v2 dataset therefore passed at 1800/600 -- the exact state
README says must be treated as failure -- because nothing compared the schema
found against the schema wanted. A gate whose expectations are supplied by the
thing under test cannot fail it. The caller now states what the campaign
requires, and a v2 directory under a v3 expectation is a hard error.

BLOCK_BASE_DIRECTORY must contain combined_root_1 through combined_root_10.
The command checks all 300 generated pair-registry files and fails unless
the central content and stored Sumw2 of summed MULTIPLICITY, hTrKinematics,
hAsKinematics, hCorrelations, and hCorrelationsByOrigin equal the ten-block
sum within the fixed ROOT merge tolerance. Additive event/count/weight
metadata and the all-event or event-ID-modulo block contract are also checked.
The associate-origin category schema and exact category-label map must be
identical in the central file and every block.
USAGE
  exit 2
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_base="$(cd "${script_dir}/.." && pwd)"
export HADRONIZATION_BASE="${HADRONIZATION_BASE:-${project_base}}"
source "${project_base}/setupEnv.sh"

central_directory="$1"
block_base_directory="$2"
requested_schema="$3"
expected_central_events="${4:--1}"
if [[ ! "${expected_central_events}" =~ ^-?[0-9]+$ ]] ||
   (( expected_central_events == 0 || expected_central_events < -1 )); then
  echo "ERROR: EXPECTED_CENTRAL_EVENTS must be -1 or a positive integer" >&2
  exit 2
fi

# Resolve the requested schema to its full tag from the contract, so that both
# `v3` and the full tag are accepted and anything else is rejected HERE --
# before ROOT is started and before any count is derived. A numeric third
# argument almost certainly means a caller written against the old three-
# argument signature, so it gets a specific message rather than "unknown".
if [[ "${requested_schema}" =~ ^-?[0-9]+$ ]]; then
  echo "ERROR: EXPECTED_SCHEMA is now the third argument and must be a schema" >&2
  echo "       (v2, v3, or a full tag); got the number '${requested_schema}'." >&2
  echo "       EXPECTED_CENTRAL_EVENTS moved to the fourth position." >&2
  exit 2
fi
expected_schema="$(python3 -c '
import json, pathlib, sys
payload = json.loads(pathlib.Path(sys.argv[1]).read_text())
tags = payload["schema_version_tags"]
requested = sys.argv[2]
if requested in tags:
    print(tags[requested])
elif requested in tags.values():
    print(requested)
else:
    raise SystemExit(
        f"unknown EXPECTED_SCHEMA {requested!r}; known: "
        + ", ".join(f"{k} ({v})" for k, v in tags.items()))
' "${project_base}/config/pair_file_object_contract_v1.json" "${requested_schema}")" || {
  echo "ERROR: EXPECTED_SCHEMA '${requested_schema}' is not a known schema" >&2
  exit 2
}

log_file="$(mktemp "/tmp/validate_pair_block_closure_XXXXXX.log")"
status=0
root -l -b -q \
  "${script_dir}/ValidatePairBlockClosure.C(\"${central_directory}\",\"${block_base_directory}\",${expected_central_events},\"${expected_schema}\")" \
  >"${log_file}" 2>&1 || status=$?
cat "${log_file}"
# The sumw2 check count is a function of the generated contract, not a
# constant, and pinning it as a literal is what made this gate reject a
# correct result. b01536b added hFlavourClosure to the closure's object list
# -- fixing a real gap, since it had been silently unchecked since the tool
# was written -- taking the count from 5 x 300 to 6 x 300, while this string
# still demanded the pre-fix 1500. Deriving keeps the wrapper and the macro
# reading one source of truth.
#
# Deriving does NOT discard the anti-regression property the literal gave.
# That now lives in tests/test_pair_object_contract.py, whose
# test_closure_content_object_count pins the six object names in a list
# deliberately NOT derived from the contract, so a contract that dropped an
# object fails there under `make check`. What this gate can actually see --
# the macro diverging from the contract it reads -- is still caught here.
#
# The count is also a function of the SCHEMA the data declares, not of the
# contract alone. An object added to v3 is absent from a correct v2 directory,
# so deriving over every contract row would demand seven checks from a
# directory that rightly carries six -- the same class of error as the pinned
# 1500, one version later. The macro reports the schema it adopted; the count
# is derived for that schema.
declared_schema="$(sed -n 's/.*PAIR_BLOCK_CLOSURE errors=[0-9]* analysis_schema=\([^ ]*\).*/\1/p' "${log_file}" | head -1)"
if [[ -z "${declared_schema}" || "${declared_schema}" == "NONE" ]]; then
  echo "ERROR: the closure did not report an analysis_schema, so the expected" >&2
  echo "       object count cannot be derived. Retained log: ${log_file}" >&2
  exit 2
fi
# THE GATE THE COUNTS CANNOT PROVIDE (A4). Everything below derives its
# expectations from `declared_schema`, i.e. from the data. That is correct for
# checking internal consistency and useless for enforcing a campaign
# requirement: a complete v2 directory is internally consistent at 1800/600.
# The macro is also given the expected schema and fails on its own, so this is a
# second line rather than the only one -- but it is the line that survives
# someone running the macro through a different driver.
if [[ "${declared_schema}" != "${expected_schema}" ]]; then
  echo "ERROR: schema mismatch. The campaign requires ${expected_schema}" >&2
  echo "       but the data declares ${declared_schema}." >&2
  echo "       This is the 1800/600 failure mode: a complete, internally" >&2
  echo "       consistent dataset of the WRONG schema. Retained log: ${log_file}" >&2
  exit 1
fi
#
# invariant_metadata_checks is derived for the same reason, and it is the
# literal that would have broken next: it was pinned at 600, i.e. the two
# hand-listed origin-category objects x 300. v3 adds three species-axis
# legibility objects, taking it to 1500. Both counts now come from the
# contract's own identity_checked axis, so neither the macro nor this wrapper
# owns a number the other can drift from.
read -r closure_content_objects identity_objects <<<"$(python3 -c '
import json, pathlib, sys
payload = json.loads(pathlib.Path(sys.argv[1]).read_text())
declared = sys.argv[2]
versions = payload["schema_versions"]
tags = payload["schema_version_tags"]
# Fail closed on an unknown tag, exactly as ParsePairSchemaVersion does.
matches = [name for name, tag in tags.items() if tag == declared]
if len(matches) != 1:
    raise SystemExit(f"unknown analysis_schema {declared!r}")
index = versions.index(matches[0])


def in_schema(row):
    return versions.index(row.get("since_schema", versions[0])) <= index


content = sum(1 for row in payload["objects"]
              if row["closure"] == "checked"
              and row["merge_semantics"] == "additive_content"
              and in_schema(row))
identity = sum(1 for row in payload["objects"]
               if row.get("identity_checked") and in_schema(row))
print(content, identity)
' "${project_base}/config/pair_file_object_contract_v1.json" "${declared_schema}")"
if [[ ! "${closure_content_objects}" =~ ^[0-9]+$ ]] ||
   (( closure_content_objects == 0 )) ||
   [[ ! "${identity_objects}" =~ ^[0-9]+$ ]] ||
   (( identity_objects == 0 )); then
  echo "ERROR: could not derive the closure object counts from the contract" >&2
  echo "       for schema ${declared_schema}. Retained log: ${log_file}" >&2
  exit 2
fi
#
# WHY additive_metadata_closure_checks IS 3600 AND NOT 3000, i.e. 12 per pair
# file against only 10 additive_scalar objects in the contract. Carried as an
# unexplained number through three handoffs; derived here so it stops being one.
#
#   10  contract-derived. ValidatePairBlockClosure.C:392-407 iterates
#       ClosureCheckedScalars("TParameter<Long64_t>") and
#       ClosureCheckedScalars("TParameter<double>"), which together are exactly
#       the contract's 10 closure-checked additive_scalar objects.
#    2  hand-written, at :522 and :530 -- input_file_count and
#       source_input_events.
#   --
#   12  per pair file, x 300 files = 3600.
#
# THOSE TWO ARE CORRECTLY HAND-WRITTEN, not an oversight. Both are declared
# `invariant`/`exempt` in the contract, so neither is an additive closure at
# all; what the closure checks for them is a MODE-DEPENDENT block-structure
# relation -- under all-event blocks the block sum must equal the central
# value, under modulo blocks it must equal kBlockCount x the central value. No
# contract axis expresses "equals the sum here, equals N times it there", so
# they cannot be derived from the existing axes.
#
# FOLLOW-UP, deliberately not taken here: contract-deriving these two would
# need a new axis for that conditional relation. That is a larger change than
# the derivations already landed and is not the same trivial shape, so it is
# recorded rather than done. The literal 3600 is safe meanwhile: it is 12 x 300
# and neither term is version-sensitive -- v3 adds no additive_scalar object.
expected_summary="PAIR_BLOCK_CLOSURE errors=0 analysis_schema=${declared_schema} central_pair_files=300 block_pair_files=3000 object_content_sumw2_closure_checks=$(( closure_content_objects * 300 )) additive_metadata_closure_checks=3600 invariant_metadata_checks=$(( identity_objects * 300 )) source_filter_contract_checks=300 expected_central_events=${expected_central_events} relative_tolerance=2e-10"
if (( status != 0 )) ||
   [[ "$(grep -Fxc "${expected_summary}" "${log_file}")" -ne 1 ]] ||
   grep -qE 'PAIR_BLOCK_CLOSURE_ERROR|segmentation violation|Break +segmentation|cling JIT session error' \
     "${log_file}"; then
  # B13: the failure path RETAINS the log. It used to delete it here, so a
  # genuine closure failure produced exit 1 and nothing to read -- which is
  # exactly how B12 presented as an opaque exit code, at a cost of one session
  # to reconstruct. A validator keeps its evidence precisely when it fails.
  # The success path below is unchanged and still cleans up.
  echo "RETAINED closure log for diagnosis: ${log_file}" >&2
  exit 1
fi
rm -f "${log_file}"
