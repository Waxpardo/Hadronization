#!/bin/bash
# count_events.sh
# Run the ROOT macro that counts events in all combined-HF and split bbbar/ccbar files.

# Resolve Hadronization base from base_path.txt
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -f "${SCRIPT_DIR}/../../base_path.txt" ]; then
  BASEDIR="$(cat "${SCRIPT_DIR}/../../base_path.txt")"
else
  BASEDIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
fi
BASEDIR="${BASEDIR%/}"
export HADRONIZATION_BASE="${BASEDIR}"

cd "${BASEDIR}" || exit 1

# Load your environment (same as for other analysis if needed)
if [ -f "${BASEDIR}/setupEnv.sh" ]; then
  export SETUPENV_QUIET=1
  source "${BASEDIR}/setupEnv.sh"
fi

# Run the ROOT macro (with ACLiC compilation)
root -l -b -q 'AnalysisScripts/CountEvents/count_events_bb_cc.C++'
ROOT_STATUS=$?

# Clean up ACLiC-generated files
rm -f \
  "${SCRIPT_DIR}/count_events_bb_cc_C_ACLiC_dict_rdict.pcm" \
  "${SCRIPT_DIR}/count_events_bb_cc_C.d" \
  "${SCRIPT_DIR}/count_events_bb_cc_C.so"

# Propagate ROOT exit status
exit $ROOT_STATUS
