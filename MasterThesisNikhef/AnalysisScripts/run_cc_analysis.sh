#!/bin/bash
# run_cc_analysis.sh
#
# Simple wrapper for the ccbar multi-file + subsampling analysis.
# Edit NSUB below to change the number of subsamples.

NSUB=10   # <<< EDIT THIS NUMBER OF SUBSAMPLES

# Go to the main HRP_clean directory
cd /data/alice/ipardoza/HRP_clean || exit 1

# Run the ccbar multi-file analysis macro with NSUB subsamples
root -l -b -q 'MasterThesisNikhef/AnalysisScripts/cc_mult_pt_analysis_multi.C+('"$NSUB"')'

