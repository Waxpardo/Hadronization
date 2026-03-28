#!/bin/bash
set -euo pipefail

# Usage:
#   runCondorJob.sh JOBID TUNE NEVT_PER_JOB
#
#   JOBID        : integer
#   TUNE         : MONASH | JUNCTIONS
#   NEVT_PER_JOB : integer

if [ "$#" -ne 3 ]; then
  echo "Usage: $0 JOBID TUNE NEVT_PER_JOB"
  echo "  TUNE = MONASH | JUNCTIONS"
  exit 1
fi

JOBID="$1"
TUNE="$2"
NEVT_PER_JOB="$3"

# --------------------------------------------------
# Base directory resolution
# Priority:
# 1) HADRONIZATION_BASE
# 2) base_path.txt next to this script
# 3) script directory
# 4) fallback fixed path
# --------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FALLBACK_BASEDIR="/data/alice/ipardoza/Hadronization"

if [ -n "${HADRONIZATION_BASE:-}" ]; then
  BASEDIR="${HADRONIZATION_BASE}"
elif [ -f "${SCRIPT_DIR}/base_path.txt" ]; then
  BASEDIR="$(cat "${SCRIPT_DIR}/base_path.txt")"
else
  BASEDIR="${SCRIPT_DIR}"
fi

BASEDIR="${BASEDIR%/}"
if [ -z "${BASEDIR}" ]; then
  BASEDIR="${FALLBACK_BASEDIR}"
fi

CODEDIR="${BASEDIR}/SimulationScripts"
EXE="${CODEDIR}/heavyflavourcorrelations_status"

OUTDIR="${BASEDIR}/RootFiles/HF/${TUNE}"
WORKDIR_BASE="${BASEDIR}/Jobs/HF/${TUNE}"
WORKDIR="${WORKDIR_BASE}/job_${JOBID}"

mkdir -p "${OUTDIR}" "${WORKDIR_BASE}" "${WORKDIR}" "${BASEDIR}/logs"

echo ">>> JOBID        = ${JOBID}"
echo ">>> TUNE         = ${TUNE}"
echo ">>> NEVT_PER_JOB = ${NEVT_PER_JOB}"
echo ">>> BASEDIR      = ${BASEDIR}"
echo ">>> WORKDIR      = ${WORKDIR}"
echo ">>> OUTDIR       = ${OUTDIR}"

# --------------------------------------------------
# Checks
# --------------------------------------------------
if [ ! -d "${CODEDIR}" ]; then
  echo "ERROR: SimulationScripts directory not found at ${CODEDIR}"
  exit 1
fi

if [ ! -x "${EXE}" ]; then
  echo "ERROR: Executable not found or not executable: ${EXE}"
  exit 1
fi

if [ ! -f "${BASEDIR}/setupEnv.sh" ]; then
  echo "ERROR: setupEnv.sh not found at ${BASEDIR}/setupEnv.sh"
  exit 1
fi

# --------------------------------------------------
# Environment
# --------------------------------------------------
cd "${BASEDIR}"
export SETUPENV_QUIET=1
source "${BASEDIR}/setupEnv.sh"

# --------------------------------------------------
# Tune-dependent config
# --------------------------------------------------
case "${TUNE}" in
  MONASH)
    CFG_TEMPLATE="${CODEDIR}/pythiasettings_Hard_Low_ccbb_MONASH.cmnd"
    CFG_BASENAME="pythiasettings_Hard_Low_ccbb_MONASH.cmnd"
    MODE="monash"
    ;;
  JUNCTIONS)
    CFG_TEMPLATE="${CODEDIR}/pythiasettings_Hard_Low_ccbb_JUNCTIONS.cmnd"
    CFG_BASENAME="pythiasettings_Hard_Low_ccbb_JUNCTIONS.cmnd"
    MODE="junctions"
    ;;
  *)
    echo "ERROR: Unsupported TUNE='${TUNE}'. Use MONASH or JUNCTIONS."
    exit 1
    ;;
esac

if [ ! -f "${CFG_TEMPLATE}" ]; then
  echo "ERROR: Config template not found: ${CFG_TEMPLATE}"
  exit 1
fi

# --------------------------------------------------
# Per-job working directory and per-job .cmnd file
# The executable reads the .cmnd by bare filename, so we run in WORKDIR.
# --------------------------------------------------
cd "${WORKDIR}"

JOB_CMND="${WORKDIR}/${CFG_BASENAME}"

if grep -q "^Main:numberOfEvents" "${CFG_TEMPLATE}"; then
  sed "s/^Main:numberOfEvents.*/Main:numberOfEvents = ${NEVT_PER_JOB}/" \
    "${CFG_TEMPLATE}" > "${JOB_CMND}"
else
  cp "${CFG_TEMPLATE}" "${JOB_CMND}"
  echo "Main:numberOfEvents = ${NEVT_PER_JOB}" >> "${JOB_CMND}"
fi

echo "Using .cmnd file:"
head -n 12 "${JOB_CMND}" || true

# --------------------------------------------------
# Deterministic seeds from JOBID
# --------------------------------------------------
SEED1=$((10000 + JOBID))
SEED2=$((20000 + JOBID))

OUTBASENAME="hf_${TUNE}_job${JOBID}.root"

echo "Running: ${EXE} ${MODE} ${OUTBASENAME} ${SEED1} ${SEED2}"
"${EXE}" "${MODE}" "${OUTBASENAME}" "${SEED1}" "${SEED2}"

if [ ! -f "${WORKDIR}/${OUTBASENAME}" ]; then
  echo "ERROR: Expected output file not found: ${WORKDIR}/${OUTBASENAME}"
  ls -l "${WORKDIR}"
  exit 1
fi

mv "${WORKDIR}/${OUTBASENAME}" "${OUTDIR}/${OUTBASENAME}"
echo "Moved: ${OUTDIR}/${OUTBASENAME}"
echo "Done."