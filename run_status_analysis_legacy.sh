#!/bin/bash
# LEGACY per-file analysis wrapper. Not valid for canonical publication use.
set -euo pipefail

# =========================================================
# ARGUMENTS
# =========================================================

JOBID="$1"
INPUTFILE="$2"
OUTPUTDIR="$3"
SCRIPTSDIR="$4"
HADRONIZATION_BASE="${HADRONIZATION_BASE:-/user/pveen/Hadronization}"

# =========================================================
# ENVIRONMENT SETUP
# =========================================================

if [[ -f "${HADRONIZATION_BASE}/setupEnv.sh" ]]; then
  source "${HADRONIZATION_BASE}/setupEnv.sh"
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

root -l -b -q "${SCRIPTSDIR}/status_analysis_THnSparse_qq.C(\"${INPUTFILE}\",\"${JOB_OUTPUT_DIR}\")"

# =========================================================
# OPTIONAL COPY SAFETY (if macro writes elsewhere)
# =========================================================

find . -maxdepth 1 \
    \( -name "*.root" -o -name "*.pdf" -o -name "*.png" \) \
    -exec cp {} "${JOB_OUTPUT_DIR}/" \;

echo "Job ${JOBID} finished successfully"
