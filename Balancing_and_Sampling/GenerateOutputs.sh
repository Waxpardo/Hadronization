#!/bin/bash

# Generates output root files using the B_Balancing_MakeOutputYields macro.
# This can be used for sampling of the batches, so that errors can be estimated.

# Path 214 is used because production 215 did not have prompt/non-prompt simulations for charm

# Loop through i from 1 to 20
for ((i = 1; i <= 20; i++)); do
    root -l -b -q "B_Balancing_MakeOutputYields.C($i, \"/data/alice/pveen/ProductionsPythia/BatchedOutput_bb_215/SAMPLING_MONASH_bb_215/SAMPLING_MONASH$i/\", \"/data/alice/pveen/ProductionsPythia/BatchedOutput_bb_JUNCTIONS_215/SAMPLING_MONASH_bb_JUNCTIONS_215/SAMPLING_MONASH$i/\", \"/data/alice/pveen/ProductionsPythia/BatchedOutput_cc_215/SAMPLING_MONASH_cc_215/SAMPLING_MONASH$i/\", \"/data/alice/pveen/ProductionsPythia/BatchedOutput_cc_JUNCTIONS_215/SAMPLING_MONASH_cc_JUNCTIONS_215/SAMPLING_MONASH$i/\", \"/data/alice/pveen\
/ProductionsPythia/BatchedOutput_cc_prompt_214/SAMPLING_MONASH_cc_prompt_214/SAMPLING_MONASH$i/\", \"/data/alice/pveen\
/ProductionsPythia/BatchedOutput_cc_prompt_JUNCTIONS_214/SAMPLING_MONASH_cc_prompt_JUNCTIONS_214/SAMPLING_MONASH$i/\", \"/data/alice/pveen/ProductionsPythia/BatchedOutput_cc_214/SAMPLING_MONASH_cc_non_prompt_214/SAMPLING_MONASH$i/\", \"/data/alice/pveen/ProductionsPythia/BatchedOutput_cc_JUNCTIONS_214/SAMPLING_MONASH_cc_non_prompt_JUNCTIONS_214/SAMPLING_MONASH$i/\")"
done
