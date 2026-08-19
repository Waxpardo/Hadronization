#!/bin/bash
# run_cc_analysis.sh
#
# Simple wrapper for the ccbar multi-file + subsampling analysis.

set -euo pipefail

if [ "$#" -lt 1 ] || [ "$#" -gt 3 ]; then
  echo "Usage: $0 OUTPUT_TAG [NSUB] [CHARGE_MODE]"
  echo "   or: $0 OUTPUT_TAG [CHARGE_MODE] [NSUB]"
  echo "  OUTPUT_TAG = output folder name inside AnalyzedData (example: 12-01-2026)"
  echo "  NSUB       = number of subsamples (optional, default 10)"
  echo "  CHARGE_MODE = combined or separate (optional, default combined)"
  exit 1
fi

OUTPUT_TAG="$1"
NSUB="10"
CHARGE_MODE="combined"

if [ "$#" -ge 2 ]; then
  if [[ "$2" =~ ^[0-9]+$ ]]; then
    NSUB="$2"
    CHARGE_MODE="${3:-combined}"
  else
    CHARGE_MODE="$2"
    if [ "$#" -ge 3 ]; then
      NSUB="$3"
    fi
  fi
fi

case "${CHARGE_MODE}" in
  combined|separate) ;;
  *)
    echo "ERROR: CHARGE_MODE must be 'combined' or 'separate' (got '${CHARGE_MODE}')"
    exit 1
    ;;
esac

if ! [[ "${NSUB}" =~ ^[0-9]+$ ]]; then
  echo "ERROR: NSUB must be an integer (got '${NSUB}')"
  exit 1
fi

# Resolve Hadronization base from base_path.txt
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -f "${SCRIPT_DIR}/../base_path.txt" ]; then
  PROJECT_BASE="$(cat "${SCRIPT_DIR}/../base_path.txt")"
else
  PROJECT_BASE="$(cd "${SCRIPT_DIR}/.." && pwd)"
fi
PROJECT_BASE="${PROJECT_BASE%/}"
export HADRONIZATION_BASE="${PROJECT_BASE}"

cd "${PROJECT_BASE}" || exit 1

if [ ! -f "${PROJECT_BASE}/setupEnv.sh" ]; then
  echo "ERROR: setupEnv.sh not found at ${PROJECT_BASE}/setupEnv.sh"
  exit 1
fi

export SETUPENV_QUIET=1
source "${PROJECT_BASE}/setupEnv.sh"

MONASH_DIR="${PROJECT_BASE}/RootFiles/ccbar/MONASH"
JUNCTIONS_DIR="${PROJECT_BASE}/RootFiles/ccbar/JUNCTIONS"

if [ ! -d "${MONASH_DIR}" ]; then
  echo "ERROR: Expected split charm input directory not found: ${MONASH_DIR}"
  exit 1
fi

if [ ! -d "${JUNCTIONS_DIR}" ]; then
  echo "ERROR: Expected split charm input directory not found: ${JUNCTIONS_DIR}"
  exit 1
fi

echo "Running split charm analysis from:"
echo "  ${MONASH_DIR}"
echo "  ${JUNCTIONS_DIR}"

# Run the ccbar multi-file analysis macro with NSUB subsamples
root -l -b -q "AnalysisScripts/cc_mult_pt_analysis_multi.C+(${NSUB}, \"${OUTPUT_TAG}\", \"${CHARGE_MODE}\")"
