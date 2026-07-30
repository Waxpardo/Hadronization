#!/bin/bash
set -euo pipefail

# Legacy dispatcher target. New publication production must use
# runCondorJob.sh --campaign and an immutable campaign manifest.

# Usage:
#   runCondorJob.sh JOBID TUNE NEVT_PER_JOB
#   runCondorJob.sh CLUSTERID JOBID TUNE NEVT_PER_JOB
#   runCondorJob.sh CLUSTERID JOBID TUNE NEVT_PER_JOB ATTEMPT
#   runCondorJob.sh JOBID CHANNEL TUNE NEVT_PER_JOB
#   runCondorJob.sh CLUSTERID JOBID CHANNEL TUNE NEVT_PER_JOB
#   runCondorJob.sh CLUSTERID JOBID CHANNEL TUNE NEVT_PER_JOB ATTEMPT
#
#   CLUSTERID    : Condor cluster id (optional for manual runs)
#   JOBID        : integer
#   CHANNEL      : bbbar | ccbar
#   TUNE         : MONASH | JUNCTIONS | CLOSEPACKING (HF only)
#   NEVT_PER_JOB : integer
#   ATTEMPT      : retry/start counter, optional

usage() {
  echo "Usage:"
  echo "  $0 JOBID TUNE NEVT_PER_JOB"
  echo "  $0 CLUSTERID JOBID TUNE NEVT_PER_JOB"
  echo "  $0 CLUSTERID JOBID TUNE NEVT_PER_JOB ATTEMPT"
  echo "    Unified heavy-flavour workflow"
  echo "    TUNE = MONASH | JUNCTIONS | CLOSEPACKING"
  echo
  echo "  $0 JOBID CHANNEL TUNE NEVT_PER_JOB"
  echo "  $0 CLUSTERID JOBID CHANNEL TUNE NEVT_PER_JOB"
  echo "  $0 CLUSTERID JOBID CHANNEL TUNE NEVT_PER_JOB ATTEMPT"
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

CLUSTERID=""
ATTEMPT="0"

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
  CLUSTERID="$1"
  JOBID="$2"
  if [ "$3" = "bbbar" ] || [ "$3" = "ccbar" ]; then
    WORKFLOW="split"
    CHANNEL="$3"
    TUNE="$4"
    NEVT_PER_JOB="$5"
  else
    WORKFLOW="hf"
    TUNE="$3"
    NEVT_PER_JOB="$4"
    ATTEMPT="$5"
  fi
elif [ "$#" -eq 6 ]; then
  WORKFLOW="split"
  CLUSTERID="$1"
  JOBID="$2"
  CHANNEL="$3"
  TUNE="$4"
  NEVT_PER_JOB="$5"
  ATTEMPT="$6"
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

if ! is_nonnegative_integer "${ATTEMPT}"; then
  echo "ERROR: ATTEMPT must be a non-negative integer."
  exit 1
fi

# HTCondor exposes the live job ClassAd inside the job sandbox. When jobs are
# retried by max_retries, NumJobStarts increments even though the command-line
# arguments stay unchanged. Folding it into the seed modifiers makes retry
# attempts statistically independent.
if [ -n "${_CONDOR_JOB_AD:-}" ] && [ -r "${_CONDOR_JOB_AD}" ]; then
  JOB_AD_ATTEMPT="$(awk -F'= ' '/^NumJobStarts = / {gsub(/"/, "", $2); print $2; exit}' "${_CONDOR_JOB_AD}" 2>/dev/null || true)"
  if is_nonnegative_integer "${JOB_AD_ATTEMPT:-}" && [ "${JOB_AD_ATTEMPT}" -gt "${ATTEMPT}" ]; then
    ATTEMPT="${JOB_AD_ATTEMPT}"
  fi
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
    HF_OUTPUT_ROOT="${HADRONIZATION_HF_OUTPUT_ROOT:-${BASEDIR}/RootFiles/HF}"
    HF_WORK_ROOT="${HADRONIZATION_HF_WORK_ROOT:-${BASEDIR}/Jobs/HF}"
    HF_LOG_ROOT="${HADRONIZATION_HF_LOG_ROOT:-${BASEDIR}/logs/HF}"
    OUTDIR="${HF_OUTPUT_ROOT%/}/${TUNE}"
    WORKDIR_BASE="${HF_WORK_ROOT%/}/${TUNE}"
    LOGDIR="${HF_LOG_ROOT%/}/${TUNE}"

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
      CLOSEPACKING)
        CFG_TEMPLATE="${CODEDIR}/pythiasettings_Hard_Low_ccbb_CLOSEPACKING.cmnd"
        CFG_BASENAME="pythiasettings_Hard_Low_ccbb_CLOSEPACKING.cmnd"
        MODE="closepacking"
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
        ;;
      bbbar:JUNCTIONS)
        EXE="${CODEDIR}/bbbarcorrelations_status_JUNCTIONS"
        CFG_TEMPLATE="${CODEDIR}/pythiasettings_Hard_Low_bb_JUNCTIONS.cmnd"
        CFG_BASENAME="pythiasettings_Hard_Low_bb_JUNCTIONS.cmnd"
        ;;
      ccbar:MONASH)
        EXE="${CODEDIR}/ccbarcorrelations_status"
        CFG_TEMPLATE="${CODEDIR}/pythiasettings_Hard_Low_cc.cmnd"
        CFG_BASENAME="pythiasettings_Hard_Low_cc.cmnd"
        ;;
      ccbar:JUNCTIONS)
        EXE="${CODEDIR}/ccbarcorrelations_status_JUNCTIONS"
        CFG_TEMPLATE="${CODEDIR}/pythiasettings_Hard_Low_cc_JUNCTIONS.cmnd"
        CFG_BASENAME="pythiasettings_Hard_Low_cc_JUNCTIONS.cmnd"
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

if [ ! -f "${CFG_TEMPLATE}" ]; then
  echo "ERROR: Config template not found: ${CFG_TEMPLATE}"
  exit 1
fi

if [ ! -x "${EXE}" ]; then
  echo "ERROR: Executable not found or not executable: ${EXE}"
  exit 1
fi

mkdir -p "${OUTDIR}" "${WORKDIR_BASE}" "${WORKDIR}" "${LOGDIR}"

echo ">>> WORKFLOW     = ${WORKFLOW}"
if [ -n "${CLUSTERID}" ]; then
  echo ">>> CLUSTERID    = ${CLUSTERID}"
fi
echo ">>> JOBID        = ${JOBID}"
echo ">>> ATTEMPT      = ${ATTEMPT}"
if [ "${WORKFLOW}" = "split" ]; then
  echo ">>> CHANNEL      = ${CHANNEL}"
fi
echo ">>> TUNE         = ${TUNE}"
echo ">>> NEVT_PER_JOB = ${NEVT_PER_JOB}"
echo ">>> BASEDIR      = ${BASEDIR}"
echo ">>> WORKDIR      = ${WORKDIR}"
echo ">>> OUTDIR       = ${OUTDIR}"
echo ">>> LOGDIR       = ${LOGDIR}"

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

if [ -s "${OUTDIR}/${OUTBASENAME}" ]; then
  echo "Final output already exists, leaving it untouched: ${OUTDIR}/${OUTBASENAME}"
  exit 0
fi

if [ -e "${WORKDIR}/${OUTBASENAME}" ]; then
  echo "WARNING: Removing stale workdir output from a previous failed/evicted attempt:"
  echo "         ${WORKDIR}/${OUTBASENAME}"
  rm -f "${WORKDIR}/${OUTBASENAME}"
fi

echo "Using .cmnd file:"
head -n 12 "${JOB_CMND}" || true

# --------------------------------------------------
# Seed modifiers from cluster, job id, tune, and retry attempt.
# The C++ producer also folds in time and process id; these modifiers make the
# Condor identity and retry count explicit, so reruns do not reuse old seeds.
# --------------------------------------------------
CLUSTER_FOR_SEED="${CLUSTERID:-0}"
TUNE_COMPONENT=0
case "${TUNE}" in
  MONASH)       TUNE_COMPONENT=101 ;;
  JUNCTIONS)   TUNE_COMPONENT=202 ;;
  CLOSEPACKING) TUNE_COMPONENT=303 ;;
esac

SEED1=$((10000 + (CLUSTER_FOR_SEED % 100000) * 1000 + JOBID * 10 + ATTEMPT))
SEED2=$((20000 + TUNE_COMPONENT * 100000 + (CLUSTER_FOR_SEED % 1000) * 10 + ATTEMPT))
echo ">>> SEED_MOD_1   = ${SEED1}"
echo ">>> SEED_MOD_2   = ${SEED2}"

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
