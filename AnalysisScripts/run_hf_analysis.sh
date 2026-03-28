#!/bin/bash
# run_hf_analysis.sh
#
# Usage:
#   ./AnalysisScripts/run_hf_analysis.sh OUTPUT_TAG [NSUB]
#
# Example:
#   ./AnalysisScripts/run_hf_analysis.sh 27-03-2026
#   ./AnalysisScripts/run_hf_analysis.sh 27-03-2026 20

if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
  echo "Usage: $0 OUTPUT_TAG [NSUB]"
  echo "  OUTPUT_TAG = output folder name inside AnalyzedData (example: 27-03-2026)"
  echo "  NSUB       = number of subsamples (optional, default 10)"
  exit 1
fi

OUTPUT_TAG="$1"
NSUB="${2:-10}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -f "${SCRIPT_DIR}/../base_path.txt" ]; then
  BASEDIR="$(cat "${SCRIPT_DIR}/../base_path.txt")"
else
  BASEDIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
fi
BASEDIR="${BASEDIR%/}"
export HADRONIZATION_BASE="${BASEDIR}"

cd "${BASEDIR}" || exit 1

MONASH_DIR="${BASEDIR}/RootFiles/HF/MONASH"
JUNCTIONS_DIR="${BASEDIR}/RootFiles/HF/JUNCTIONS"

if [ ! -d "${MONASH_DIR}" ]; then
  echo "ERROR: Expected combined HF input directory not found: ${MONASH_DIR}"
  exit 1
fi

if [ ! -d "${JUNCTIONS_DIR}" ]; then
  echo "ERROR: Expected combined HF input directory not found: ${JUNCTIONS_DIR}"
  exit 1
fi

echo "Running combined HF analysis from:"
echo "  ${MONASH_DIR}"
echo "  ${JUNCTIONS_DIR}"

root -l -b -q "AnalysisScripts/hf_mult_pt_analysis_multi.C+(${NSUB}, \"${OUTPUT_TAG}\")"
