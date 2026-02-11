#!/bin/bash
# count_events.sh
# Run the ROOT macro that counts events in all bbbar/ccbar files.

BASEDIR="/data/alice/ipardoza/HRP_clean"

cd "${BASEDIR}" || exit 1

# Load your environment (same as for other analysis if needed)
if [ -f "${BASEDIR}/setupEnv.sh" ]; then
  export SETUPENV_QUIET=1
  source "${BASEDIR}/setupEnv.sh"
fi

# Run the ROOT macro (with ACLiC compilation)
root -l -b -q 'count_events_bb_cc.C++'
ROOT_STATUS=$?

# Clean up ACLiC-generated files
rm -f \
  count_events_bb_cc_C_ACLiC_dict_rdict.pcm \
  count_events_bb_cc_C.d \
  count_events_bb_cc_C.so

# Propagate ROOT exit status
exit $ROOT_STATUS

