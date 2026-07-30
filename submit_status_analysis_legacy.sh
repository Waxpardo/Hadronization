#!/bin/bash
# LEGACY filename-discovery submitter. Not valid for the canonical campaign.
set -euo pipefail

# Submit Paul's THnSparse status analysis for one HF tune or for all paper tunes.
#
# Usage:
#   ./submit_status_analysis.sh TUNE [NUMBER_OF_FILES] [JOB_TAG]
#   ./submit_status_analysis.sh ALL 100 Job700
#
# TUNE can be MONASH, JUNCTIONS, CLOSEPACKING, or ALL.
# NUMBER_OF_FILES is the number of available raw ROOT files to process per tune.
#
# Environment overrides:
#   RAW_INPUT_BASE      default: /data/alice/ipardoza/Hadronization/RootFiles/HF
#   ANALYSIS_OUTPUT_BASE default: /data/alice/pveen_new/PanosPaper/RootFiles/AnalysisResults/HF
#   HADRONIZATION_BASE  default: directory containing this script
#   STATUS_ANALYSIS_REQUEST_MEMORY default: 8GB
#   DRY_RUN             set to 1/true to write the submit file without condor_submit

usage() {
    cat <<'USAGE'
Usage:
  ./submit_status_analysis.sh TUNE [NUMBER_OF_FILES] [JOB_TAG]
  ./submit_status_analysis.sh ALL 100 Job700

TUNE:
  MONASH
  JUNCTIONS
  CLOSEPACKING
  ALL

Defaults:
  NUMBER_OF_FILES = 1
  JOB_TAG         = Job700

NUMBER_OF_FILES selects the first N available raw ROOT files for each tune,
sorted by the numeric job id in the filename. This means validation runs can
use, for example, 50 completed files per tune even if some low job ids are
still running.

Environment overrides:
  RAW_INPUT_BASE       Raw HF ROOT input base directory.
  ANALYSIS_OUTPUT_BASE Per-job THnSparse analysis output base directory.
  HADRONIZATION_BASE   Hadronization checkout containing AnalysisScripts.
  STATUS_ANALYSIS_REQUEST_MEMORY
                       Condor memory request for each status-analysis job.
  DRY_RUN              Set to 1/true to write the submit file without condor_submit.
USAGE
}

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_base="${HADRONIZATION_BASE:-${script_dir}}"
project_base="${project_base%/}"
export HADRONIZATION_BASE="${project_base}"

raw_input_base="${RAW_INPUT_BASE:-/data/alice/ipardoza/Hadronization/RootFiles/HF}"
analysis_output_base="${ANALYSIS_OUTPUT_BASE:-/data/alice/pveen_new/PanosPaper/RootFiles/AnalysisResults/HF}"
analysis_scripts_dir="${project_base}/AnalysisScripts"
dry_run="${DRY_RUN:-0}"
request_memory="${STATUS_ANALYSIS_REQUEST_MEMORY:-8GB}"

requested_tune="${1:-}"
number_of_files="${2:-1}"
job_tag="${3:-Job700}"

if [[ -z "${requested_tune}" || "${requested_tune}" == "-h" || "${requested_tune}" == "--help" ]]; then
    usage
    exit 0
fi

requested_tune="$(printf '%s' "${requested_tune}" | tr '[:lower:]' '[:upper:]')"

if ! [[ "${number_of_files}" =~ ^[0-9]+$ ]]; then
    echo "ERROR: NUMBER_OF_FILES must be an integer, got '${number_of_files}'" >&2
    exit 1
fi

if [[ ! -d "${analysis_scripts_dir}" ]]; then
    echo "ERROR: AnalysisScripts directory not found: ${analysis_scripts_dir}" >&2
    exit 1
fi

resolve_tunes() {
    case "$1" in
        MONASH|JUNCTIONS|CLOSEPACKING)
            printf '%s\n' "$1"
            ;;
        ALL)
            printf '%s\n' MONASH JUNCTIONS CLOSEPACKING
            ;;
        *)
            echo "ERROR: unknown tune '$1'. Expected MONASH, JUNCTIONS, CLOSEPACKING, or ALL." >&2
            exit 1
            ;;
    esac
}

tunes=($(resolve_tunes "${requested_tune}"))

subfile="submit_status_analysis_${requested_tune}_${job_tag}.sub"

cat > "${subfile}" <<EOF
universe = vanilla
executable = ${project_base}/run_status_analysis.sh

request_cpus = 1
request_memory = ${request_memory}
request_disk = 2GB

+UseOS = "el9"
+JobCategory = "short"

environment = "HADRONIZATION_BASE=${project_base}"

should_transfer_files = NO

EOF

queued_jobs=0

for tune in "${tunes[@]}"; do
    input_directory="${raw_input_base}/${tune}"
    output_directory="${analysis_output_base}/${tune}/${job_tag}"
    output_logs_directory="${output_directory}/Logs"

    mkdir -p "${output_directory}"
    mkdir -p "${output_logs_directory}"

    if [[ ! -d "${input_directory}" ]]; then
        echo "WARNING: input directory not found for ${tune}: ${input_directory}" >&2
        continue
    fi

    queued_for_tune=0

    while IFS=$'\t' read -r job_id file; do
        if [[ -z "${job_id}" || -z "${file}" ]]; then
            continue
        fi

        cat >> "${subfile}" <<EOF

arguments = ${job_id} ${file} ${output_directory} ${analysis_scripts_dir}

output = ${output_logs_directory}/job_${job_id}.out
error  = ${output_logs_directory}/job_${job_id}.err
log    = ${output_logs_directory}/job_${job_id}.log

queue 1
EOF

        queued_jobs=$((queued_jobs + 1))
        queued_for_tune=$((queued_for_tune + 1))
    done < <(
        find "${input_directory}" -maxdepth 1 -type f -name "*.root" -print |
        while IFS= read -r candidate; do
            job_id=$(printf '%s\n' "${candidate}" | sed -n 's/.*job\([0-9][0-9]*\)\.root$/\1/p')
            if [[ -n "${job_id}" ]]; then
                printf '%s\t%s\n' "${job_id}" "${candidate}"
            fi
        done |
        sort -n -k1,1 |
        head -n "${number_of_files}"
    )

    if [[ "${queued_for_tune}" -lt "${number_of_files}" ]]; then
        echo "WARNING: requested ${number_of_files} files for ${tune}, but only queued ${queued_for_tune}" >&2
    fi
done

if [[ "${queued_jobs}" -eq 0 ]]; then
    echo "ERROR: no status-analysis jobs were queued. Check input directories and job count." >&2
    exit 1
fi

echo "Prepared ${queued_jobs} status-analysis jobs in ${subfile}"
echo "Tunes: ${tunes[*]}"
echo "Raw input base: ${raw_input_base}"
echo "Analysis output base: ${analysis_output_base}"

case "${dry_run}" in
    1|true|TRUE|yes|YES)
        echo "DRY_RUN=${dry_run}; not submitting to Condor."
        exit 0
        ;;
esac

condor_submit "${subfile}"
