#!/bin/bash
# run_hf_analysis.sh
#
# Usage:
#   ./AnalysisScripts/run_hf_analysis.sh OUTPUT_TAG [NSUB] [CHARGE_MODE]
#   ./AnalysisScripts/run_hf_analysis.sh OUTPUT_TAG [CHARGE_MODE] [NSUB]
#
# Example:
#   ./AnalysisScripts/run_hf_analysis.sh 27-03-2026
#   ./AnalysisScripts/run_hf_analysis.sh 27-03-2026 20
#   ./AnalysisScripts/run_hf_analysis.sh 27-03-2026 20 separate

set -euo pipefail

if [ "$#" -lt 1 ] || [ "$#" -gt 3 ]; then
  echo "Usage: $0 OUTPUT_TAG [NSUB] [CHARGE_MODE]"
  echo "   or: $0 OUTPUT_TAG [CHARGE_MODE] [NSUB]"
  echo "  OUTPUT_TAG = output folder name inside AnalyzedData (example: 27-03-2026)"
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

HF_TUNES=("MONASH" "JUNCTIONS" "CLOSEPACKING")

for tune in "${HF_TUNES[@]}"; do
  tune_dir="${PROJECT_BASE}/RootFiles/HF/${tune}"
  if [ ! -d "${tune_dir}" ]; then
    echo "ERROR: Expected combined HF input directory not found: ${tune_dir}"
    exit 1
  fi
done

echo "Running combined HF analysis from:"
for tune in "${HF_TUNES[@]}"; do
  echo "  ${PROJECT_BASE}/RootFiles/HF/${tune}"
done

root -l -b -q "AnalysisScripts/hf_mult_pt_analysis_multi.C+(${NSUB}, \"${OUTPUT_TAG}\", \"${CHARGE_MODE}\")"
