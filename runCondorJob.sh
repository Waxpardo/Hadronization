#!/bin/bash
set -euo pipefail

# Usage:
#   runCondorJob.sh JOBID TUNE NEVT_PER_JOB
#   runCondorJob.sh CLUSTERID JOBID TUNE NEVT_PER_JOB
#   runCondorJob.sh JOBID CHANNEL TUNE NEVT_PER_JOB
#   runCondorJob.sh CLUSTERID JOBID CHANNEL TUNE NEVT_PER_JOB
#
#   CLUSTERID    : Condor cluster id (optional for manual runs)
#   JOBID        : integer
#   CHANNEL      : bbbar | ccbar
#   TUNE         : MONASH | JUNCTIONS | CLOSEPACKING (HF only)
#   NEVT_PER_JOB : integer

usage() {
  echo "Usage:"
  echo "  $0 JOBID TUNE NEVT_PER_JOB"
  echo "  $0 CLUSTERID JOBID TUNE NEVT_PER_JOB"
  echo "    Unified heavy-flavour workflow"
  echo "    TUNE = MONASH | JUNCTIONS | CLOSEPACKING"
  echo
  echo "  $0 JOBID CHANNEL TUNE NEVT_PER_JOB"
  echo "  $0 CLUSTERID JOBID CHANNEL TUNE NEVT_PER_JOB"
  echo "    Split independent workflow"
  echo "    CHANNEL = bbbar | ccbar"
  echo "    TUNE    = MONASH | JUNCTIONS"
}

is_nonnegative_integer() {
  case "${1:-}" in
    ''|*[!0-9]*)
      return 1
      ;;
    *)
      return 0
      ;;
  esac
}

read_condor_job_starts() {
  local job_ad="${_CONDOR_JOB_AD:-}"
  local starts=""

  if [ -n "${job_ad}" ] && [ -f "${job_ad}" ]; then
    starts="$(awk -F '=' '
      $1 ~ /^[[:space:]]*NumJobStarts[[:space:]]*$/ {
        gsub(/[[:space:]]/, "", $2);
        print $2;
        exit;
      }
    ' "${job_ad}")"
  fi

  if is_nonnegative_integer "${starts}"; then
    echo "${starts}"
  else
    echo "0"
  fi
}

CLUSTERID=""

if [ "$#" -eq 3 ]; then
  WORKFLOW="hf"
  JOBID="$1"
  TUNE="$2"
  NEVT_PER_JOB="$3"
elif [ "$#" -eq 4 ]; then
  if [ "$2" = "bbbar" ] || [ "$2" = "ccbar" ]; then
    WORKFLOW="split"
    JOBID="$1"
    CHANNEL="$2"
    TUNE="$3"
    NEVT_PER_JOB="$4"
  else
    WORKFLOW="hf"
    CLUSTERID="$1"
    JOBID="$2"
    TUNE="$3"
    NEVT_PER_JOB="$4"
  fi
elif [ "$#" -eq 5 ]; then
  WORKFLOW="split"
  CLUSTERID="$1"
  JOBID="$2"
  CHANNEL="$3"
  TUNE="$4"
  NEVT_PER_JOB="$5"
else
  usage
  exit 1
fi

if [ -n "${CLUSTERID}" ] && ! is_nonnegative_integer "${CLUSTERID}"; then
  echo "ERROR: CLUSTERID must be a non-negative integer."
  exit 1
fi

if ! is_nonnegative_integer "${JOBID}"; then
  echo "ERROR: JOBID must be a non-negative integer."
  exit 1
fi

# --------------------------------------------------
# Base directory resolution
# Priority:
# 1) script directory (most reliable for Condor jobs)
# 2) base_path.txt next to this script
# 3) HADRONIZATION_BASE from the environment
# 4) fallback fixed path
# --------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FALLBACK_BASEDIR="/data/alice/ipardoza/Hadronization"
BASE_FILE="${SCRIPT_DIR}/base_path.txt"

is_valid_hadronization_base() {
  local candidate="${1:-}"
  [ -n "${candidate}" ] || return 1
  candidate="${candidate%/}"
  [ -d "${candidate}/SimulationScripts" ] || return 1
  [ -f "${candidate}/setupEnv.sh" ] || return 1
  return 0
}

if is_valid_hadronization_base "${SCRIPT_DIR}"; then
  RESOLVED_BASEDIR="${SCRIPT_DIR}"
elif [ -f "${BASE_FILE}" ]; then
  BASEDIR_FROM_FILE="$(cat "${BASE_FILE}")"
  if is_valid_hadronization_base "${BASEDIR_FROM_FILE}"; then
    RESOLVED_BASEDIR="${BASEDIR_FROM_FILE}"
  elif is_valid_hadronization_base "${HADRONIZATION_BASE:-}"; then
    RESOLVED_BASEDIR="${HADRONIZATION_BASE}"
  else
    RESOLVED_BASEDIR="${FALLBACK_BASEDIR}"
  fi
elif is_valid_hadronization_base "${HADRONIZATION_BASE:-}"; then
  RESOLVED_BASEDIR="${HADRONIZATION_BASE}"
else
  RESOLVED_BASEDIR="${FALLBACK_BASEDIR}"
fi

RESOLVED_BASEDIR="${RESOLVED_BASEDIR%/}"
if [ -z "${RESOLVED_BASEDIR}" ]; then
  RESOLVED_BASEDIR="${FALLBACK_BASEDIR}"
fi

export HADRONIZATION_BASE="${RESOLVED_BASEDIR}"
BASEDIR="${HADRONIZATION_BASE}"
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

# External environment scripts may reuse generic variable names such as
# BASEDIR, so re-anchor all project paths from HADRONIZATION_BASE after setup.
BASEDIR="${HADRONIZATION_BASE%/}"
CODEDIR="${BASEDIR}/SimulationScripts"

# --------------------------------------------------
# Workflow-dependent config
# --------------------------------------------------
case "${WORKFLOW}" in
  hf)
    EXE="${CODEDIR}/heavyflavourcorrelations_status"
    OUTDIR="${BASEDIR}/RootFiles/HF/${TUNE}"
    WORKDIR_BASE="${BASEDIR}/Jobs/HF/${TUNE}"
    LOGDIR="${BASEDIR}/logs/HF/${TUNE}"

    case "${TUNE}" in
      MONASH)
        CFG_TEMPLATE="${CODEDIR}/pythiasettings_Hard_Low_ccbb_MONASH.cmnd"
        CFG_BASENAME="pythiasettings_Hard_Low_ccbb_MONASH.cmnd"
        MODE="monash"
        WORKFLOW_SEED_OFFSET=101
        ;;
      JUNCTIONS)
        CFG_TEMPLATE="${CODEDIR}/pythiasettings_Hard_Low_ccbb_JUNCTIONS.cmnd"
        CFG_BASENAME="pythiasettings_Hard_Low_ccbb_JUNCTIONS.cmnd"
        MODE="junctions"
        WORKFLOW_SEED_OFFSET=202
        ;;
      CLOSEPACKING)
        CFG_TEMPLATE="${CODEDIR}/pythiasettings_Hard_Low_ccbb_CLOSEPACKING.cmnd"
        CFG_BASENAME="pythiasettings_Hard_Low_ccbb_CLOSEPACKING.cmnd"
        MODE="closepacking"
        WORKFLOW_SEED_OFFSET=303
        ;;
      *)
        echo "ERROR: Unsupported TUNE='${TUNE}'. Use MONASH, JUNCTIONS, or CLOSEPACKING."
        exit 1
        ;;
    esac
    ;;
  split)
    OUTDIR="${BASEDIR}/RootFiles/${CHANNEL}/${TUNE}"
    WORKDIR_BASE="${BASEDIR}/Jobs/${CHANNEL}/${TUNE}"
    LOGDIR="${BASEDIR}/logs/${CHANNEL}/${TUNE}"

    case "${CHANNEL}:${TUNE}" in
      bbbar:MONASH)
        EXE="${CODEDIR}/bbbarcorrelations_status"
        CFG_TEMPLATE="${CODEDIR}/pythiasettings_Hard_Low_bb.cmnd"
        CFG_BASENAME="pythiasettings_Hard_Low_bb.cmnd"
        WORKFLOW_SEED_OFFSET=1101
        ;;
      bbbar:JUNCTIONS)
        EXE="${CODEDIR}/bbbarcorrelations_status_JUNCTIONS"
        CFG_TEMPLATE="${CODEDIR}/pythiasettings_Hard_Low_bb_JUNCTIONS.cmnd"
        CFG_BASENAME="pythiasettings_Hard_Low_bb_JUNCTIONS.cmnd"
        WORKFLOW_SEED_OFFSET=1201
        ;;
      ccbar:MONASH)
        EXE="${CODEDIR}/ccbarcorrelations_status"
        CFG_TEMPLATE="${CODEDIR}/pythiasettings_Hard_Low_cc.cmnd"
        CFG_BASENAME="pythiasettings_Hard_Low_cc.cmnd"
        WORKFLOW_SEED_OFFSET=2101
        ;;
      ccbar:JUNCTIONS)
        EXE="${CODEDIR}/ccbarcorrelations_status_JUNCTIONS"
        CFG_TEMPLATE="${CODEDIR}/pythiasettings_Hard_Low_cc_JUNCTIONS.cmnd"
        CFG_BASENAME="pythiasettings_Hard_Low_cc_JUNCTIONS.cmnd"
        WORKFLOW_SEED_OFFSET=2201
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

if [ -n "${CLUSTERID}" ]; then
  WORKDIR="${WORKDIR_BASE}/cluster_${CLUSTERID}/job_${JOBID}"
  case "${WORKFLOW}" in
    hf)
      OUTBASENAME="hf_${TUNE}_cluster${CLUSTERID}_job${JOBID}.root"
      ;;
    split)
      OUTBASENAME="${CHANNEL}_${TUNE}_cluster${CLUSTERID}_job${JOBID}.root"
      ;;
  esac
else
  WORKDIR="${WORKDIR_BASE}/job_${JOBID}"
  case "${WORKFLOW}" in
    hf)
      OUTBASENAME="hf_${TUNE}_job${JOBID}.root"
      ;;
    split)
      OUTBASENAME="${CHANNEL}_${TUNE}_job${JOBID}.root"
      ;;
  esac
fi

FINAL_OUTPUT="${OUTDIR}/${OUTBASENAME}"
WORK_OUTPUT="${WORKDIR}/${OUTBASENAME}"
CONDOR_JOB_STARTS="$(read_condor_job_starts)"
SEED_INPUT1="${CLUSTERID:-0}"
SEED_INPUT2=$((JOBID * 1000000 + WORKFLOW_SEED_OFFSET * 1000 + CONDOR_JOB_STARTS))

if [ ! -f "${CFG_TEMPLATE}" ]; then
  echo "ERROR: Config template not found: ${CFG_TEMPLATE}"
  exit 1
fi

if [ ! -x "${EXE}" ]; then
  echo "ERROR: Executable not found or not executable: ${EXE}"
  exit 1
fi

mkdir -p "${OUTDIR}" "${WORKDIR_BASE}" "${WORKDIR}" "${LOGDIR}"

if [ -f "${FINAL_OUTPUT}" ]; then
  echo "Final output already exists, treating job as complete: ${FINAL_OUTPUT}"
  exit 0
fi

if [ -f "${WORK_OUTPUT}" ]; then
  echo "Removing stale partial workdir output before retry: ${WORK_OUTPUT}"
  rm -f "${WORK_OUTPUT}"
fi

echo ">>> WORKFLOW     = ${WORKFLOW}"
if [ -n "${CLUSTERID}" ]; then
  echo ">>> CLUSTERID    = ${CLUSTERID}"
fi
echo ">>> JOBID        = ${JOBID}"
if [ "${WORKFLOW}" = "split" ]; then
  echo ">>> CHANNEL      = ${CHANNEL}"
fi
echo ">>> TUNE         = ${TUNE}"
echo ">>> NEVT_PER_JOB = ${NEVT_PER_JOB}"
echo ">>> BASEDIR      = ${BASEDIR}"
echo ">>> WORKDIR      = ${WORKDIR}"
echo ">>> OUTDIR       = ${OUTDIR}"
echo ">>> LOGDIR       = ${LOGDIR}"
echo ">>> CONDOR_STARTS = ${CONDOR_JOB_STARTS}"
echo ">>> SEED_INPUT1  = ${SEED_INPUT1}"
echo ">>> SEED_INPUT2  = ${SEED_INPUT2}"

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
# Deterministic seed inputs from cluster/job/workflow/attempt
# --------------------------------------------------
if [ "${WORKFLOW}" = "hf" ]; then
  echo "Running: ${EXE} ${MODE} ${OUTBASENAME} ${SEED_INPUT1} ${SEED_INPUT2}"
  "${EXE}" "${MODE}" "${OUTBASENAME}" "${SEED_INPUT1}" "${SEED_INPUT2}"
else
  echo "Running: ${EXE} ${OUTBASENAME} ${SEED_INPUT1} ${SEED_INPUT2}"
  "${EXE}" "${OUTBASENAME}" "${SEED_INPUT1}" "${SEED_INPUT2}"
fi

if [ ! -f "${WORKDIR}/${OUTBASENAME}" ]; then
  echo "ERROR: Expected output file not found: ${WORKDIR}/${OUTBASENAME}"
  ls -l "${WORKDIR}"
  exit 1
fi

mv "${WORK_OUTPUT}" "${FINAL_OUTPUT}"
echo "Moved: ${FINAL_OUTPUT}"
echo "Done."
