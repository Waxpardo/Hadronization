#!/bin/bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  ./submit_status_analysis.sh [NUMBER_OF_SUBJOBS] [TUNE|all] [OUTPUT_BASE]

Defaults:
  NUMBER_OF_SUBJOBS = 1
  TUNE              = all
  OUTPUT_BASE       = <repo>/AnalyzedData/status_analysis/HF

Examples:
  ./submit_status_analysis.sh 10 all
  ./submit_status_analysis.sh 100 CLOSEPACKING
  ./submit_status_analysis.sh 100 MONASH /data/alice/ipardoza/StatusAnalysis/HF
USAGE
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

NUMBER_OF_SUBJOBS="${1:-1}"
TUNE_SELECTION="${2:-all}"

if ! [[ "${NUMBER_OF_SUBJOBS}" =~ ^[0-9]+$ ]] || [[ "${NUMBER_OF_SUBJOBS}" -lt 1 ]]; then
  echo "ERROR: NUMBER_OF_SUBJOBS must be a positive integer (got '${NUMBER_OF_SUBJOBS}')" >&2
  usage >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_BASE="${HADRONIZATION_BASE:-}"
if [[ -z "${PROJECT_BASE}" ]]; then
  if [[ -f "${SCRIPT_DIR}/base_path.txt" ]]; then
    PROJECT_BASE="$(cat "${SCRIPT_DIR}/base_path.txt")"
  else
    PROJECT_BASE="${SCRIPT_DIR}"
  fi
fi
PROJECT_BASE="${PROJECT_BASE%/}"

INPUT_BASE="${PROJECT_BASE}/RootFiles/HF"
ANALYSIS_SCRIPTS_DIR="${PROJECT_BASE}/AnalysisScripts"
OUTPUT_BASE="${3:-${PROJECT_BASE}/AnalyzedData/status_analysis/HF}"
SUBFILE="${PROJECT_BASE}/submit_status_analysis.sub"

normalize_tune() {
  case "${1^^}" in
    ALL) echo "all" ;;
    MONASH) echo "MONASH" ;;
    JUNCTIONS) echo "JUNCTIONS" ;;
    CLOSEPACKING|CLOSE_PACKING|CLOSE-PACKING) echo "CLOSEPACKING" ;;
    *)
      echo "ERROR: unknown tune '${1}'. Use all, MONASH, JUNCTIONS, or CLOSEPACKING." >&2
      exit 1
      ;;
  esac
}

normalized_selection="$(normalize_tune "${TUNE_SELECTION}")"
if [[ "${normalized_selection}" == "all" ]]; then
  TUNES=("MONASH" "JUNCTIONS" "CLOSEPACKING")
else
  TUNES=("${normalized_selection}")
fi

for required in "${PROJECT_BASE}/run_status_analysis.sh" "${ANALYSIS_SCRIPTS_DIR}/status_analysis_qq.C"; do
  if [[ ! -f "${required}" ]]; then
    echo "ERROR: required file not found: ${required}" >&2
    exit 1
  fi
done

cat > "${SUBFILE}" <<EOF
universe = vanilla
executable = ${PROJECT_BASE}/run_status_analysis.sh
initialdir = ${PROJECT_BASE}

request_cpus = 1
request_memory = 2GB
request_disk = 2GB

+UseOS = "el9"
+JobCategory = "short"

should_transfer_files = NO

EOF

queued_jobs=0

for tune in "${TUNES[@]}"; do
  input_directory="${INPUT_BASE}/${tune}"
  output_directory="${OUTPUT_BASE}/${tune}"
  output_logs_directory="${output_directory}/Logs"

  if [[ ! -d "${input_directory}" ]]; then
    echo "ERROR: expected input directory not found for ${tune}: ${input_directory}" >&2
    exit 1
  fi

  mkdir -p "${output_directory}" "${output_logs_directory}"

  for ((job_id = 0; job_id < NUMBER_OF_SUBJOBS; job_id++)); do
    input_file="$(find "${input_directory}" -maxdepth 1 -type f -name "*job${job_id}.root" | sort | head -n 1)"

    if [[ -z "${input_file}" ]]; then
      echo "WARNING: missing ${tune} input file for job ${job_id}" >&2
      continue
    fi

    cat >> "${SUBFILE}" <<EOF

arguments = ${job_id} ${input_file} ${output_directory} ${ANALYSIS_SCRIPTS_DIR}

output = ${output_logs_directory}/job_${job_id}.out
error  = ${output_logs_directory}/job_${job_id}.err
log    = ${output_logs_directory}/job_${job_id}.log

queue 1
EOF

    queued_jobs=$((queued_jobs + 1))
  done
done

if [[ "${queued_jobs}" -eq 0 ]]; then
  echo "ERROR: no status-analysis jobs were queued." >&2
  exit 1
fi

echo "Wrote ${SUBFILE}"
echo "Queued ${queued_jobs} status-analysis jobs for tune selection '${TUNE_SELECTION}'."
condor_submit "${SUBFILE}"
