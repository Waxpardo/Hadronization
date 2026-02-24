#!/bin/bash
# runCondorJob.sh
#
# Usage:
#   runCondorJob.sh JOBID CHANNEL TUNE
#
#   JOBID   : integer (for book-keeping / output naming)
#   CHANNEL : ccbar | bbbar
#   TUNE    : MONASH | JUNCTIONS
#
# For ccbar/bbbar:
#   - runs {cc,bb}barcorrelations_status[_JUNCTIONS] OUTNAME SEED1 SEED2
#   - uses a per-job copy of the appropriate pythiasettings_*.cmnd in WORKDIR
#   - enforces Main:numberOfEvents = NEVT_PER_JOB in that copy

set -euo pipefail

# Now allow optional 4th argument: NEVT_PER_JOB
if [ "$#" -lt 3 ] || [ "$#" -gt 4 ]; then
  echo "Usage: $0 JOBID CHANNEL TUNE [NEVT_PER_JOB]"
  echo "  CHANNEL = ccbar | bbbar"
  echo "  TUNE    = MONASH | JUNCTIONS"
  echo "  NEVT_PER_JOB (optional, default 100)"
  exit 1
fi

JOBID="$1"
CHANNEL="$2"
TUNE="$3"
NEVT_PER_JOB="${4:-100}"   # default to 100 if not given

# ----- Base directories -----
#
# Priority:
# 1) HADRONIZATION_BASE (environment)
# 2) base_path.txt next to this script
# 3) script directory
# 4) fallback fixed path
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

# Heavy-quark code (same tree as this script)
HEAVY_CODEDIR="${BASEDIR}/SimulationScripts"

# Where to store output
OUTDIR="${BASEDIR}/RootFiles/${CHANNEL}/${TUNE}"
mkdir -p "${OUTDIR}"

# Worker-local scratch inside the Hadronization tree
WORKDIR_BASE="${BASEDIR}/Jobs/${CHANNEL}/${TUNE}"
mkdir -p "${WORKDIR_BASE}"
WORKDIR="${WORKDIR_BASE}/job_${JOBID}"

mkdir -p "${WORKDIR}"

echo ">>> JOBID   = ${JOBID}"
echo ">>> CHANNEL = ${CHANNEL}"
echo ">>> TUNE    = ${TUNE}"
echo ">>> WORKDIR = ${WORKDIR}"
echo ">>> OUTDIR  = ${OUTDIR}"
echo ">>> NEVT_PER_JOB = ${NEVT_PER_JOB}"

# ----- Environment -----

if [ ! -d "${HEAVY_CODEDIR}" ]; then
  echo "ERROR: SimulationScripts directory not found at ${HEAVY_CODEDIR}"
  exit 1
fi

if [ ! -f "${BASEDIR}/setupEnv.sh" ]; then
  echo "ERROR: setupEnv.sh not found at ${BASEDIR}/setupEnv.sh"
  exit 1
fi

cd "${BASEDIR}"
export SETUPENV_QUIET=1
source "${BASEDIR}/setupEnv.sh"

# ----- Seeds for cc/bb -----

SEED1=$((10000 + JOBID))
SEED2=$((20000 + JOBID))
OUTBASENAME="${CHANNEL}_${TUNE}_job${JOBID}"

EXE=""
CFG_TEMPLATE=""

case "${CHANNEL}" in
  ccbar)
    case "${TUNE}" in
      MONASH)
        EXE="${HEAVY_CODEDIR}/ccbarcorrelations_status"
        CFG_TEMPLATE="${HEAVY_CODEDIR}/pythiasettings_Hard_Low_cc.cmnd"
        ;;
      JUNCTIONS)
        EXE="${HEAVY_CODEDIR}/ccbarcorrelations_status_JUNCTIONS"
        CFG_TEMPLATE="${HEAVY_CODEDIR}/pythiasettings_Hard_Low_cc_JUNCTIONS.cmnd"
        ;;
      *)
        echo "ERROR: Unsupported TUNE='${TUNE}' for ccbar."
        exit 1
        ;;
    esac
    ;;

  bbbar)
    case "${TUNE}" in
      MONASH)
        EXE="${HEAVY_CODEDIR}/bbbarcorrelations_status"
        CFG_TEMPLATE="${HEAVY_CODEDIR}/pythiasettings_Hard_Low_bb.cmnd"
        ;;
      JUNCTIONS)
        EXE="${HEAVY_CODEDIR}/bbbarcorrelations_status_JUNCTIONS"
        CFG_TEMPLATE="${HEAVY_CODEDIR}/pythiasettings_Hard_Low_bb_JUNCTIONS.cmnd"
        ;;
      *)
        echo "ERROR: Unsupported TUNE='${TUNE}' for bbbar."
        exit 1
        ;;
    esac
    ;;

  *)
    echo "ERROR: Unsupported CHANNEL='${CHANNEL}'. Use ccbar | bbbar."
    exit 1
    ;;
esac

if [ ! -x "${EXE}" ]; then
  echo "ERROR: Executable not found or not executable: ${EXE}"
  exit 1
fi

if [ ! -f "${CFG_TEMPLATE}" ]; then
  echo "ERROR: Config template not found: ${CFG_TEMPLATE}"
  exit 1
fi

CFG_BASENAME="$(basename "${CFG_TEMPLATE}")"

# ----- Create per-job .cmnd with NEVT_PER_JOB *inside WORKDIR* -----

cd "${WORKDIR}"

JOB_CMND="${WORKDIR}/${CFG_BASENAME}"

if grep -q "^Main:numberOfEvents" "${CFG_TEMPLATE}"; then
  sed "s/^Main:numberOfEvents.*/Main:numberOfEvents = ${NEVT_PER_JOB}/" \
    "${CFG_TEMPLATE}" > "${JOB_CMND}"
else
  cat "${CFG_TEMPLATE}" > "${JOB_CMND}"
  echo "Main:numberOfEvents = ${NEVT_PER_JOB}" >> "${JOB_CMND}"
fi


echo "Using .cmnd file (first few lines):"
head -n 10 "${JOB_CMND}" || true

# ----- Run ccbar / bbbar -----
# Executable expects: EXE output_name random_number1 random_number2
# and reads pythiasettings_*.cmnd in CWD.
#
# Program writes a ROOT file with the exact output_name (sometimes without .root).

echo "Running (${CHANNEL}): ${EXE} ${OUTBASENAME} ${SEED1} ${SEED2}"
"${EXE}" "${OUTBASENAME}" "${SEED1}" "${SEED2}"

RAWFILE=""

if [ -f "${WORKDIR}/${OUTBASENAME}" ]; then
  RAWFILE="${WORKDIR}/${OUTBASENAME}"
elif [ -f "${WORKDIR}/${OUTBASENAME}.root" ]; then
  RAWFILE="${WORKDIR}/${OUTBASENAME}.root"
fi

if [ -z "${RAWFILE}" ]; then
  echo "ERROR: Expected output file '${OUTBASENAME}' (or with .root) not found in ${WORKDIR}"
  ls -l "${WORKDIR}"
  exit 1
fi

NEWNAME="${CHANNEL}_${TUNE}_job${JOBID}.root"
mv "${RAWFILE}" "${OUTDIR}/${NEWNAME}"
echo "Moved: $(basename "${RAWFILE}") -> ${OUTDIR}/${NEWNAME}"

echo "Done."
