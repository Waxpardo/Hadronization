#!/bin/bash
# run_cc_analysis.sh
#
# Simple wrapper for the ccbar multi-file + subsampling analysis.
# Edit NSUB below to change the number of subsamples.

NSUB=10   # <<< EDIT THIS NUMBER OF SUBSAMPLES

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

# Run the ccbar multi-file analysis macro with NSUB subsamples
root -l -b -q 'AnalysisScripts/cc_mult_pt_analysis_multi.C+('"$NSUB"')'
