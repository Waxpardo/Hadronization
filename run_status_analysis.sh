#!/bin/bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  ./run_status_analysis.sh JOBID INPUTFILE OUTPUTDIR SCRIPTSDIR
USAGE
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ "$#" -ne 4 ]]; then
  usage >&2
  exit 1
fi

JOBID="$1"
INPUTFILE="$2"
OUTPUTDIR="$3"
SCRIPTSDIR="$4"

# =========================================================
# ENVIRONMENT SETUP
# =========================================================

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
export HADRONIZATION_BASE="${PROJECT_BASE}"

if [[ ! -f "${PROJECT_BASE}/setupEnv.sh" ]]; then
  echo "ERROR: setupEnv.sh not found at ${PROJECT_BASE}/setupEnv.sh" >&2
  exit 1
fi

source "${PROJECT_BASE}/setupEnv.sh"

if [[ ! -f "${INPUTFILE}" ]]; then
  echo "ERROR: input file not found: ${INPUTFILE}" >&2
  exit 1
fi

if [[ ! -f "${SCRIPTSDIR}/status_analysis_qq.C" ]]; then
  echo "ERROR: status_analysis_qq.C not found in ${SCRIPTSDIR}" >&2
  exit 1
fi

# =========================================================
# BUILD OUTPUT STRUCTURE
# =========================================================

BASENAME=$(basename "${INPUTFILE}" .root)

JOB_OUTPUT_DIR="${OUTPUTDIR}/${BASENAME}"
mkdir -p "${JOB_OUTPUT_DIR}"

echo "========================================"
echo "Job ID     : ${JOBID}"
echo "Input file : ${INPUTFILE}"
echo "Output dir : ${JOB_OUTPUT_DIR}"
echo "========================================"

# =========================================================
# RUN ROOT MACRO
# =========================================================

root -l -b -q "${SCRIPTSDIR}/status_analysis_qq.C(\"${INPUTFILE}\",\"${JOB_OUTPUT_DIR}\")"

# =========================================================
# OPTIONAL COPY SAFETY (if macro writes elsewhere)
# =========================================================

find . -maxdepth 1 \
    \( -name "*.root" -o -name "*.pdf" -o -name "*.png" \) \
    -exec cp {} "${JOB_OUTPUT_DIR}/" \;

echo "Job ${JOBID} finished successfully"
