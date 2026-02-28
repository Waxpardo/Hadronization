#!/bin/bash
# run_bb_mult_pt_analysis_multi.sh

if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
  echo "Usage: $0 OUTPUT_TAG [NSUB]"
  echo "  OUTPUT_TAG = output folder name inside AnalyzedData (example: 12-01-2026)"
  echo "  NSUB       = number of subsamples (optional, default 10)"
  exit 1
fi

OUTPUT_TAG="$1"
NSUB="${2:-10}"

# Resolve Hadronization base from base_path.txt
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -f "${SCRIPT_DIR}/../base_path.txt" ]; then
  BASEDIR="$(cat "${SCRIPT_DIR}/../base_path.txt")"
else
  BASEDIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
fi
BASEDIR="${BASEDIR%/}"
export HADRONIZATION_BASE="${BASEDIR}"

cd "${BASEDIR}" || exit 1

root -l -b -q "AnalysisScripts/bb_mult_pt_analysis_multi.C+(${NSUB}, \"${OUTPUT_TAG}\")"
