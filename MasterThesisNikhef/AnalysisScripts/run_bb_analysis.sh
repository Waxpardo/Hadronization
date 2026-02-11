#!/bin/bash
# run_bb_mult_pt_analysis_multi.sh

NSUB=10   # number of subsamples

cd /data/alice/ipardoza/HRP_clean || exit 1

root -l -b -q 'MasterThesisNikhef/AnalysisScripts/bb_mult_pt_analysis_multi.C+('"$NSUB"')'
