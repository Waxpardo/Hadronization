#!/bin/bash
set -euo pipefail

# Canonical one-pass per-logical-file analysis wrapper. It writes 300 signed
# pair files to a unique staging directory, validates the complete directory,
# and promotes it atomically only after all checks pass.

if [[ "$#" -ne 2 ]]; then
  echo "Usage: $0 RAW_ROOT_FILE FINAL_PAIR_DIRECTORY" >&2
  exit 2
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_base="${HADRONIZATION_BASE:-${script_dir}}"
project_base="${project_base%/}"
export HADRONIZATION_BASE="${project_base}"
source "${project_base}/setupEnv.sh"

input_file="$1"
final_directory="$2"
validator="${project_base}/Validation/validate_pair_directory.sh"
macro="${project_base}/AnalysisScripts/status_analysis_THnSparse_qq.C"

for required in "${input_file}" "${validator}" "${macro}"; do
  if [[ ! -e "${required}" ]]; then
    echo "ERROR: required analysis component missing: ${required}" >&2
    exit 3
  fi
done

if [[ -d "${final_directory}" ]]; then
  if "${validator}" "${final_directory}"; then
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
  "${macro}(\"${input_file}\",\"${stage_directory}\",\"central_primary_ground_v1\")" \
  >"${analysis_log}" 2>&1 || status=$?
cat "${analysis_log}"
if (( status != 0 )) ||
   ! grep -q 'ONE_PASS_ANALYSIS_SUMMARY' "${analysis_log}" ||
   grep -q 'ONE_PASS_ANALYSIS_ERROR' "${analysis_log}" ||
   grep -qE 'segmentation violation|Break +segmentation|cling JIT session error' \
     "${analysis_log}"; then
  echo "ERROR: one-pass analysis failed; retained stage: ${stage_directory}" >&2
  exit 5
fi

if ! "${validator}" "${stage_directory}"; then
  echo "ERROR: pair-directory validation failed; retained stage: ${stage_directory}" >&2
  exit 6
fi

input_sha256="$(sha256sum "${input_file}" | awk '{print $1}')"
repository_commit="$(git -C "${project_base}" rev-parse HEAD)"
repository_dirty=false
if [[ -n "$(git -C "${project_base}" status --porcelain --untracked-files=no)" ]]; then
  repository_dirty=true
fi
printf '{\n  "raw_input": "%s",\n  "raw_sha256": "%s",\n  "repository_commit": "%s",\n  "repository_dirty": %s,\n  "selector": "%s"\n}\n' \
  "${input_file}" "${input_sha256}" "${repository_commit}" \
  "${repository_dirty}" \
  "hard_trigger_primary_ground__primary_ground_associate_v1" \
  >"${stage_directory}/analysis_job_metadata.json"

if [[ -e "${final_directory}" ]]; then
  echo "ERROR: final analysis directory appeared before promotion" >&2
  exit 7
fi
mv "${stage_directory}" "${final_directory}"
echo "PROMOTED_ANALYSIS ${final_directory}"
