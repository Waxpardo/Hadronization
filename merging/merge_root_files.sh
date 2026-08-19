#!/bin/bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  ./merging/merge_root_files.sh FREEZE_DIR PRODUCTION_ROOT ANALYSIS_ROOT ANALYZED_DATA_BASE [OUTPUT_TAG]

Consumes only the sealed canonical manifest and its ten exact deterministic
blocks. It creates Paul-compatible pair-object directories:
  complete_root_OUTPUT_TAG_{MONASH,JUNCTIONS,CLOSEPACKING}
  SUBSAMPLES_OUTPUT_TAG/combined_root_subSamples_TUNE/combined_root_{1..10}

Each directory contains the full generated pair registry (including all legacy
56 names used by Paul's configurations), is checksum-inventoried, and is
promoted only after exact object/provenance validation. Existing output is
validated but never overwritten.
USAGE
}

if [[ "$#" -lt 4 || "$#" -gt 5 || "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 2
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_base="${HADRONIZATION_BASE:-${script_dir}}"
project_base="${project_base%/}"
export HADRONIZATION_BASE="${project_base}"
source "${project_base}/setupEnv.sh"

freeze_dir="$(cd "$1" && pwd)"
production_root="$(cd "$2" && pwd)"
analysis_root="$(cd "$3" && pwd)"
analyzed_data_base="$4"
output_tag="${5:-$(basename "$(dirname "${freeze_dir}")")}"
if [[ ! "${output_tag}" =~ ^[A-Za-z0-9._-]+$ ]]; then
  echo "ERROR: unsafe output tag: ${output_tag}" >&2
  exit 2
fi
if [[ -n "$(git -C "${project_base}" status --porcelain --untracked-files=no)" ]]; then
  echo "ERROR: canonical merge requires a tracked-clean checkout" >&2
  exit 3
fi

mkdir -p "${analysis_root}/validation"
# Merge shape, derived from the manifest rather than from a sealed contract
# report. The only properties the merge actually requires are that every tune
# contributed the same number of per-job analysis outputs and that the count
# divides into the ten blocks the ratios are formed in.
read -r canonical_inputs_per_tune canonical_inputs_per_block canonical_events_per_tune < <(
python3 -c '
import collections, json, pathlib, sys
rows = [
    json.loads(line)
    for line in pathlib.Path(sys.argv[1]).read_text().splitlines()
    if line.strip()
]
if not rows:
    raise SystemExit("canonical manifest is empty")
per_tune = collections.Counter(row["tune"] for row in rows)
counts = set(per_tune.values())
if len(counts) != 1:
    raise SystemExit("tunes have unequal exposure: %s" % dict(per_tune))
inputs = counts.pop()
if inputs % 10:
    raise SystemExit("jobs per tune (%d) must divide into ten blocks" % inputs)
events = collections.Counter()
for row in rows:
    events[row["tune"]] += int(row["requested_successes"])
if len(set(events.values())) != 1:
    raise SystemExit("tunes have unequal event exposure: %s" % dict(events))
print(inputs, inputs // 10, events.popitem()[1])
' "${freeze_dir}/canonical_manifest.jsonl"
)
echo "CANONICAL_MERGE_SHAPE inputs_per_tune=${canonical_inputs_per_tune}" \
     "inputs_per_block=${canonical_inputs_per_block}" \
     "events_per_tune=${canonical_events_per_tune}"

analysis_report="${analysis_root}/validation/analysis_output_manifest_validation.json"
canonical_manifest_sha="$(sha256sum "${freeze_dir}/canonical_manifest.jsonl" \
  | awk '{print $1}')"

# ---------------------------------------------------------------------------
# CONSULT THE EXISTING REPORT BEFORE REPEATING IT.
#
# validate_analysis_outputs.py sha256s all 3000 raw inputs and then spawns a
# ROOT ValidatePairDirectory pass per per-job directory. Measured cost: 12 h
# 42 m. It ran unconditionally on every start, so each transient death -- a
# reboot, a momentarily-absent CVMFS interpreter -- cost that much again before
# the merge could resume, and it dominated the recovery rather than the work.
#
# WHY SKIPPING IS CONTENT-NEUTRAL. This is a PRECONDITION CHECK, not a
# transformation. It reads inputs and writes one report; no merged byte depends
# on whether it ran. What the merge consumes is the manifest and the per-job
# directories, and the merge validates every directory it promotes on its own
# (validate_pair_directory.sh + merged_pair_provenance.py, twice, before the
# mv). Skipping a repeated precondition check does not change a single output;
# it only changes whether we re-establish something already established and
# recorded.
#
# WHAT MAKES REUSE SAFE. The report names the exact manifest it validated, by
# sha. If the manifest changed, the sha changes and the report is not reused.
# Everything else is required to be an unambiguous PASS over the full expected
# row count. FAIL CLOSED: any missing key, any type surprise, any count that
# is not exactly right, any unreadable file -> run the validator.
# ---------------------------------------------------------------------------
expected_rows=$(( canonical_inputs_per_tune * 3 ))
if [[ -f "${analysis_report}" ]] && python3 - \
     "${analysis_report}" "${canonical_manifest_sha}" "${expected_rows}" <<'PY'
import json
import sys

report_path, manifest_sha, expected_text = sys.argv[1:]
expected = int(expected_text)
try:
    with open(report_path) as stream:
        report = json.load(stream)
except (OSError, ValueError):
    raise SystemExit(1)
if not isinstance(report, dict):
    raise SystemExit(1)
if report.get("schema") != "hf_analysis_output_validation_v3":
    raise SystemExit(1)
if report.get("status") != "PASS":
    raise SystemExit(1)
# The report must be ABOUT the manifest this merge is running on.
if report.get("canonical_manifest_sha256") != manifest_sha:
    raise SystemExit(1)
for key, want in (("validated_output_count", expected),
                  ("canonical_manifest_rows", expected),
                  ("missing_output_count", 0)):
    value = report.get(key)
    if not isinstance(value, int) or isinstance(value, bool) or value != want:
        raise SystemExit(1)
# The per-output list must actually carry the outputs it claims to.
outputs = report.get("validated_outputs")
if not isinstance(outputs, list) or len(outputs) != expected:
    raise SystemExit(1)
raise SystemExit(0)
PY
then
  report_sha="$(sha256sum "${analysis_report}" | awk '{print $1}')"
  report_time="$(date -r "${analysis_report}" '+%Y-%m-%dT%H:%M:%S%z')"
  echo "ANALYSIS_OUTPUT_MANIFEST_SKIPPED status=PASS" \
       "reason=existing_report_matches_manifest" \
       "report=${analysis_report}" \
       "report_sha256=${report_sha}" \
       "report_recorded=${report_time}" \
       "manifest_sha256=${canonical_manifest_sha}" \
       "rows=${expected_rows}"
else
  python3 "${project_base}/tools/validate_analysis_outputs.py" \
    "${freeze_dir}/canonical_manifest.jsonl" "${analysis_root}" \
    --production-root "${production_root}" --checkout "${project_base}" \
    --report "${analysis_report}"
fi
mkdir -p "${analyzed_data_base}"

merge_one() {
  local tune="$1"
  local manifest="$2"
  local expected_inputs="$3"
  local final_directory="$4"
  local manifest_sha
  manifest_sha="$(sha256sum "${manifest}" | awk '{print $1}')"

  if [[ -e "${final_directory}" ]]; then
    # A DATA verdict and an ENVIRONMENT failure are different diagnoses and
    # must not share a message. On 2026-08-13 the CVMFS python3 vanished for a
    # moment, the provenance validator exited 127 (command not found), and this
    # branch reported "existing merge directory is stale/invalid" -- accusing a
    # directory that ValidatePairDirectory had just PASSED with errors=0, and
    # pointing the next diagnostician at the data instead of the interpreter.
    # Exit 126/127 means the check never ran, and "we could not look" is never
    # evidence of "we looked and it was bad".
    local dir_status=0 prov_status=0
    "${project_base}/Validation/validate_pair_directory.sh" \
      "${final_directory}" "${expected_inputs}" "${manifest_sha}" || dir_status=$?
    if (( dir_status == 126 || dir_status == 127 )); then
      echo "ERROR: ENVIRONMENT -- validate_pair_directory.sh could not EXECUTE (exit ${dir_status}) for ${final_directory}." >&2
      echo "       This is NOT a verdict on the data. Nothing was validated and nothing is known to be wrong with the directory." >&2
      echo "       Check the interpreter/ROOT availability (CVMFS mounts drop transiently) and re-run; the merge resumes per directory." >&2
      return 8
    fi
    if (( dir_status == 0 )); then
      python3 "${project_base}/tools/merged_pair_provenance.py" validate \
        "${final_directory}" "${manifest}" "${tune}" "${expected_inputs}" \
        "${project_base}" "${analysis_report}" "${freeze_dir}" || prov_status=$?
      if (( prov_status == 126 || prov_status == 127 )); then
        echo "ERROR: ENVIRONMENT -- merged_pair_provenance.py could not EXECUTE (exit ${prov_status}) for ${final_directory}." >&2
        echo "       This is NOT a verdict on the data. ValidatePairDirectory PASSED this directory immediately above; only the provenance check failed to run." >&2
        echo "       Most likely the CVMFS python3 is momentarily absent. Re-run; the merge resumes per directory." >&2
        return 8
      fi
      if (( prov_status == 0 )); then
        echo "VALIDATED_EXISTING_MERGE ${final_directory}"
        return 0
      fi
    fi
    echo "ERROR: DATA -- existing merge directory is stale/invalid; refusing overwrite: ${final_directory}" >&2
    echo "       validate_pair_directory exit=${dir_status} merged_pair_provenance exit=${prov_status}" >&2
    echo "       Both checks RAN. This is a verdict on the directory's contents or provenance, not an environment problem." >&2
    return 4
  fi

  mkdir -p "$(dirname "${final_directory}")"
  local stage
  stage="$(mktemp -d "${final_directory}.partial.XXXXXX")"
  local slot_temp_dir slot_list
  slot_temp_dir="$(mktemp -d "/tmp/hadronization_${tune}_slots_XXXXXX")"
  slot_list="${slot_temp_dir}/slots.txt"
  if ! python3 - "${tune}" "${manifest}" "${expected_inputs}" >"${slot_list}" <<'PY'
import json
import sys
from pathlib import Path

tune, manifest, expected_text = sys.argv[1:]
expected = int(expected_text)
rows = [
    json.loads(line)
    for line in Path(manifest).read_text().splitlines()
    if line.strip()
]
tune_rows = [row for row in rows if row.get("tune") == tune]
slots = [row.get("canonical_slot") for row in tune_rows]
if len(tune_rows) != expected or len(set(slots)) != expected:
    raise SystemExit(
        f"manifest subset for {tune} is not {expected} unique slots"
    )
if any(
    not isinstance(row.get("schema"), str)
    or not row.get("schema")
    or not isinstance(slot, int)
    or isinstance(slot, bool)
    or slot < 0
    for row, slot in zip(tune_rows, slots)
):
    raise SystemExit(f"invalid canonical manifest row for {tune}")
if slots != sorted(slots):
    raise SystemExit(f"canonical slots are not ordered for {tune}")
print(*slots, sep="\n")
PY
  then
    rm -f "${slot_list}"
    rmdir "${slot_temp_dir}"
    echo "ERROR: invalid merge manifest; retained stage ${stage}" >&2
    return 4
  fi

  local merge_log="${stage}/merge.log"
  local status=0
  root -l -b -q \
    "${project_base}/merging/MergeCanonicalAnalysis.C(\"${slot_list}\",\"${analysis_root}/per_job\",\"${tune}\",\"${stage}\",\"${manifest_sha}\",${expected_inputs})" \
    >"${merge_log}" 2>&1 || status=$?
  rm -f "${slot_list}"
  rmdir "${slot_temp_dir}"
  cat "${merge_log}"
  if (( status != 0 )) ||
     [[ "$(grep -c '^CANONICAL_MERGE_SUMMARY ' "${merge_log}")" -ne 1 ]] ||
     grep -qE 'CANONICAL_MERGE_ERROR|segmentation violation|Break +segmentation|cling JIT session error' \
       "${merge_log}"; then
    echo "ERROR: merge failed; retained stage ${stage}" >&2
    return 5
  fi
  "${project_base}/Validation/validate_pair_directory.sh" \
    "${stage}" "${expected_inputs}" "${manifest_sha}"
  python3 "${project_base}/tools/merged_pair_provenance.py" write \
    "${stage}" "${manifest}" "${tune}" "${expected_inputs}" \
    "${project_base}" "${analysis_report}" "${freeze_dir}"
  "${project_base}/Validation/validate_pair_directory.sh" \
    "${stage}" "${expected_inputs}" "${manifest_sha}"
  python3 "${project_base}/tools/merged_pair_provenance.py" validate \
    "${stage}" "${manifest}" "${tune}" "${expected_inputs}" \
    "${project_base}" "${analysis_report}" "${freeze_dir}"

  if [[ -e "${final_directory}" ]]; then
    echo "ERROR: final merge directory appeared before promotion: ${final_directory}" >&2
    return 6
  fi
  mv "${stage}" "${final_directory}"
  echo "PROMOTED_MERGE ${final_directory}"
}

for tune in MONASH JUNCTIONS CLOSEPACKING; do
  merge_one "${tune}" "${freeze_dir}/canonical_manifest.jsonl" \
    "${canonical_inputs_per_tune}" \
    "${analyzed_data_base}/complete_root_${output_tag}_${tune}"
  for block in $(seq 1 10); do
    block_name="$(printf 'block_%02d.jsonl' "${block}")"
    merge_one "${tune}" "${freeze_dir}/${block_name}" \
      "${canonical_inputs_per_block}" \
      "${analyzed_data_base}/SUBSAMPLES_${output_tag}/combined_root_subSamples_${tune}/combined_root_${block}"
  done
done

# Promotion is not complete until every numeric object in every canonical
# pair file is shown to be the union of the same ten deterministic blocks.
# Keep the successful, deterministic validator transcript with the other
# post-production evidence and never silently replace a differing report.
for tune in MONASH JUNCTIONS CLOSEPACKING; do
  closure_report="${analysis_root}/validation/pair_block_closure_${output_tag}_${tune}.log"
  closure_stage="$(mktemp "${analysis_root}/validation/.pair_block_closure_${output_tag}_${tune}.XXXXXX")"
  if ! "${project_base}/Validation/validate_pair_block_closure.sh" \
       "${analyzed_data_base}/complete_root_${output_tag}_${tune}" \
       "${analyzed_data_base}/SUBSAMPLES_${output_tag}/combined_root_subSamples_${tune}" \
       "${canonical_events_per_tune}" >"${closure_stage}" 2>&1; then
    cat "${closure_stage}"
    echo "ERROR: canonical central/ten-block closure failed; retained report ${closure_stage}" >&2
    exit 7
  fi
  cat "${closure_stage}"
  if [[ -e "${closure_report}" ]]; then
    if ! cmp -s "${closure_stage}" "${closure_report}"; then
      echo "ERROR: existing closure report differs; retained candidate ${closure_stage}" >&2
      exit 8
    fi
    rm -f "${closure_stage}"
  else
    mv "${closure_stage}" "${closure_report}"
  fi
  echo "CANONICAL_PAIR_BLOCK_CLOSURE_PASS tune=${tune} report=${closure_report}"
done
