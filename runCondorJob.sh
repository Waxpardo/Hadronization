#!/bin/bash
set -euo pipefail

# Usage:
#   runCondorJob.sh JOBID TUNE NEVT_PER_JOB
#   runCondorJob.sh JOBID CHANNEL TUNE NEVT_PER_JOB
#
#   JOBID        : integer
#   CHANNEL      : bbbar | ccbar
#   TUNE         : MONASH | JUNCTIONS
#   NEVT_PER_JOB : integer

usage() {
  echo "Usage:"
  echo "  $0 JOBID TUNE NEVT_PER_JOB"
  echo "    Unified heavy-flavour workflow"
  echo "    TUNE = MONASH | JUNCTIONS"
  echo
  echo "  $0 JOBID CHANNEL TUNE NEVT_PER_JOB"
  echo "    Split independent workflow"
  echo "    CHANNEL = bbbar | ccbar"
  echo "    TUNE    = MONASH | JUNCTIONS"
}

if [ "$#" -eq 3 ]; then
  WORKFLOW="hf"
  JOBID="$1"
  TUNE="$2"
  NEVT_PER_JOB="$3"
elif [ "$#" -eq 4 ]; then
  WORKFLOW="split"
  JOBID="$1"
  CHANNEL="$2"
  TUNE="$3"
  NEVT_PER_JOB="$4"
else
  usage
  exit 1
fi

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

# --------------------------------------------------
# Checks
# --------------------------------------------------
if [ ! -d "${CODEDIR}" ]; then
  echo "ERROR: SimulationScripts directory not found at ${CODEDIR}"
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
# Workflow-dependent config
# --------------------------------------------------
case "${WORKFLOW}" in
  hf)
    EXE="${CODEDIR}/heavyflavourcorrelations_status"
    OUTDIR="${BASEDIR}/RootFiles/HF/${TUNE}"
    WORKDIR_BASE="${BASEDIR}/Jobs/HF/${TUNE}"
    WORKDIR="${WORKDIR_BASE}/job_${JOBID}"

    case "${TUNE}" in
      MONASH)
        CFG_TEMPLATE="${CODEDIR}/pythiasettings_Hard_Low_ccbb_MONASH.cmnd"
        CFG_BASENAME="pythiasettings_Hard_Low_ccbb_MONASH.cmnd"
        MODE="monash"
        OUTBASENAME="hf_${TUNE}_job${JOBID}.root"
        ;;
      JUNCTIONS)
        CFG_TEMPLATE="${CODEDIR}/pythiasettings_Hard_Low_ccbb_JUNCTIONS.cmnd"
        CFG_BASENAME="pythiasettings_Hard_Low_ccbb_JUNCTIONS.cmnd"
        MODE="junctions"
        OUTBASENAME="hf_${TUNE}_job${JOBID}.root"
        ;;
      *)
        echo "ERROR: Unsupported TUNE='${TUNE}'. Use MONASH or JUNCTIONS."
        exit 1
        ;;
    esac
    ;;
  split)
    OUTDIR="${BASEDIR}/RootFiles/${CHANNEL}/${TUNE}"
    WORKDIR_BASE="${BASEDIR}/Jobs/${CHANNEL}/${TUNE}"
    WORKDIR="${WORKDIR_BASE}/job_${JOBID}"

    case "${CHANNEL}:${TUNE}" in
      bbbar:MONASH)
        EXE="${CODEDIR}/bbbarcorrelations_status"
        CFG_TEMPLATE="${CODEDIR}/pythiasettings_Hard_Low_bb.cmnd"
        CFG_BASENAME="pythiasettings_Hard_Low_bb.cmnd"
        OUTBASENAME="bbbar_${TUNE}_job${JOBID}.root"
        ;;
      bbbar:JUNCTIONS)
        EXE="${CODEDIR}/bbbarcorrelations_status_JUNCTIONS"
        CFG_TEMPLATE="${CODEDIR}/pythiasettings_Hard_Low_bb_JUNCTIONS.cmnd"
        CFG_BASENAME="pythiasettings_Hard_Low_bb_JUNCTIONS.cmnd"
        OUTBASENAME="bbbar_${TUNE}_job${JOBID}.root"
        ;;
      ccbar:MONASH)
        EXE="${CODEDIR}/ccbarcorrelations_status"
        CFG_TEMPLATE="${CODEDIR}/pythiasettings_Hard_Low_cc.cmnd"
        CFG_BASENAME="pythiasettings_Hard_Low_cc.cmnd"
        OUTBASENAME="ccbar_${TUNE}_job${JOBID}.root"
        ;;
      ccbar:JUNCTIONS)
        EXE="${CODEDIR}/ccbarcorrelations_status_JUNCTIONS"
        CFG_TEMPLATE="${CODEDIR}/pythiasettings_Hard_Low_cc_JUNCTIONS.cmnd"
        CFG_BASENAME="pythiasettings_Hard_Low_cc_JUNCTIONS.cmnd"
        OUTBASENAME="ccbar_${TUNE}_job${JOBID}.root"
        ;;
      *)
        echo "ERROR: Unsupported CHANNEL/TUNE combination '${CHANNEL}/${TUNE}'."
        echo "       CHANNEL = bbbar | ccbar"
        echo "       TUNE    = MONASH | JUNCTIONS"
        exit 1
        ;;
    esac
    ;;
  *)
    echo "ERROR: Unsupported workflow '${WORKFLOW}'."
    exit 1
    ;;
esac

if [ ! -f "${CFG_TEMPLATE}" ]; then
  echo "ERROR: Config template not found: ${CFG_TEMPLATE}"
  exit 1
fi

if [ ! -x "${EXE}" ]; then
  echo "ERROR: Executable not found or not executable: ${EXE}"
  exit 1
fi

mkdir -p "${OUTDIR}" "${WORKDIR_BASE}" "${WORKDIR}" "${BASEDIR}/logs"

echo ">>> WORKFLOW     = ${WORKFLOW}"
echo ">>> JOBID        = ${JOBID}"
if [ "${WORKFLOW}" = "split" ]; then
  echo ">>> CHANNEL      = ${CHANNEL}"
fi
echo ">>> TUNE         = ${TUNE}"
echo ">>> NEVT_PER_JOB = ${NEVT_PER_JOB}"
echo ">>> BASEDIR      = ${BASEDIR}"
echo ">>> WORKDIR      = ${WORKDIR}"
echo ">>> OUTDIR       = ${OUTDIR}"

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

if [ "${WORKFLOW}" = "hf" ]; then
  echo "Running: ${EXE} ${MODE} ${OUTBASENAME} ${SEED1} ${SEED2}"
  "${EXE}" "${MODE}" "${OUTBASENAME}" "${SEED1}" "${SEED2}"
else
  echo "Running: ${EXE} ${OUTBASENAME} ${SEED1} ${SEED2}"
  "${EXE}" "${OUTBASENAME}" "${SEED1}" "${SEED2}"
fi

if [ ! -f "${WORKDIR}/${OUTBASENAME}" ]; then
  echo "ERROR: Expected output file not found: ${WORKDIR}/${OUTBASENAME}"
  ls -l "${WORKDIR}"
  exit 1
fi

mv "${WORKDIR}/${OUTBASENAME}" "${OUTDIR}/${OUTBASENAME}"
echo "Moved: ${OUTDIR}/${OUTBASENAME}"
echo "Done."
