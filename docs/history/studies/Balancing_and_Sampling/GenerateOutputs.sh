#!/bin/bash

set -euo pipefail

# Generates output root files using the B_Balancing_MakeOutputYields macro.
# This can be used for sampling of the batches, so that errors can be estimated.

# Path 214 is used because production 215 did not have prompt/non-prompt simulations for charm

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_BASE="$(cd "${SCRIPT_DIR}/.." && pwd)"
export HADRONIZATION_BASE="${HADRONIZATION_BASE:-${REPO_BASE}}"

if [ -f "${HADRONIZATION_BASE}/setupEnv.sh" ]; then
    export SETUPENV_QUIET=1
    # shellcheck disable=SC1090
    source "${HADRONIZATION_BASE}/setupEnv.sh"
fi

cd "${SCRIPT_DIR}"

BB_MONASH_BASE="${BB_MONASH_BASE:-/data/alice/pveen/ProductionsPythia/BatchedOutput_bb_215/SAMPLING_MONASH_bb_215}"
BB_JUNCTIONS_BASE="${BB_JUNCTIONS_BASE:-/data/alice/pveen/ProductionsPythia/BatchedOutput_bb_JUNCTIONS_215/SAMPLING_MONASH_bb_JUNCTIONS_215}"
CC_MONASH_BASE="${CC_MONASH_BASE:-/data/alice/pveen/ProductionsPythia/BatchedOutput_cc_215/SAMPLING_MONASH_cc_215}"
CC_JUNCTIONS_BASE="${CC_JUNCTIONS_BASE:-/data/alice/pveen/ProductionsPythia/BatchedOutput_cc_JUNCTIONS_215/SAMPLING_MONASH_cc_JUNCTIONS_215}"
CC_PROMPT_MONASH_BASE="${CC_PROMPT_MONASH_BASE:-/data/alice/pveen/ProductionsPythia/BatchedOutput_cc_prompt_214/SAMPLING_MONASH_cc_prompt_214}"
CC_PROMPT_JUNCTIONS_BASE="${CC_PROMPT_JUNCTIONS_BASE:-/data/alice/pveen/ProductionsPythia/BatchedOutput_cc_prompt_JUNCTIONS_214/SAMPLING_MONASH_cc_prompt_JUNCTIONS_214}"
CC_NONPROMPT_MONASH_BASE="${CC_NONPROMPT_MONASH_BASE:-/data/alice/pveen/ProductionsPythia/BatchedOutput_cc_214/SAMPLING_MONASH_cc_non_prompt_214}"
CC_NONPROMPT_JUNCTIONS_BASE="${CC_NONPROMPT_JUNCTIONS_BASE:-/data/alice/pveen/ProductionsPythia/BatchedOutput_cc_JUNCTIONS_214/SAMPLING_MONASH_cc_non_prompt_JUNCTIONS_214}"

# Loop through i from 1 to 20
for ((i = 1; i <= 20; i++)); do
    root -l -b -q "B_Balancing_MakeOutputYields.C($i, \"${BB_MONASH_BASE}/SAMPLING_MONASH$i/\", \"${BB_JUNCTIONS_BASE}/SAMPLING_MONASH$i/\", \"${CC_MONASH_BASE}/SAMPLING_MONASH$i/\", \"${CC_JUNCTIONS_BASE}/SAMPLING_MONASH$i/\", \"${CC_PROMPT_MONASH_BASE}/SAMPLING_MONASH$i/\", \"${CC_PROMPT_JUNCTIONS_BASE}/SAMPLING_MONASH$i/\", \"${CC_NONPROMPT_MONASH_BASE}/SAMPLING_MONASH$i/\", \"${CC_NONPROMPT_JUNCTIONS_BASE}/SAMPLING_MONASH$i/\")"
done
