#!/bin/bash
# Re-extract a merged directory with the E5-fixed, trigger-deduplicating
# extractor. Deployed OUTSIDE the frozen checkout on purpose: the merge reads
# that checkout live and it must not move until the 33rd promotion.
set -euo pipefail
BASE=/data/alice/ipardoza/extractor_e5fix
source /data/alice/ipardoza/Hadronization/setupEnv.sh >/dev/null 2>&1
merged="$1"; out="$2"
mkdir -p "$out"
cd "$BASE"
exec ./extraction/extract_species_decomposition.py "$merged" \
  --out "$out" \
  --artifact "$BASE/AnalysisScripts/species_ordinals_v2.json" \
  --registry "$BASE/config/heavy_flavour_pair_registry_v1.json" \
  --decay-map "$BASE/AnalysisScripts/decay_parent_map_v2.json" \
  --root-bin "$(command -v root)"
