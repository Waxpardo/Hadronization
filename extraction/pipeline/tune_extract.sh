#!/bin/bash
# Run species decomposition for one tune's central product and ten blocks.
# The script records the deployed reader digest and reads the frozen checkout.
# Each block runs in an independent ROOT process.
set -euo pipefail
TUNE="${1:?tune required}"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHECKOUT="${HADRONIZATION_BASE:-$(cd "${script_dir}/../.." && pwd)}"
MERGED="${HADRONIZATION_MERGED_ROOT:?set HADRONIZATION_MERGED_ROOT}"
RUN_ROOT="${HADRONIZATION_EXTRACTION_RUN_ROOT:?set HADRONIZATION_EXTRACTION_RUN_ROOT}"
READER="${HADRONIZATION_EXTRACTION_READER:-${CHECKOUT}/extraction/extract_species_decomposition.py}"
ARTIFACT="${HADRONIZATION_SPECIES_ARTIFACT:-${CHECKOUT}/contracts/species_ordinals_v2.json}"
DECAY_MAP="${HADRONIZATION_DECAY_MAP:-${CHECKOUT}/contracts/decay_parent_map_v2.json}"
PAIR_REGISTRY="${HADRONIZATION_PAIR_REGISTRY:-${CHECKOUT}/config/heavy_flavour_pair_registry_v1.json}"
R=$RUN_ROOT/$TUNE
CENTRAL=$MERGED/complete_root_HF_RUN3_V1_${TUNE}
BLOCKS=$MERGED/SUBSAMPLES_HF_RUN3_V1/combined_root_subSamples_${TUNE}
mkdir -p "$R" || exit 9

cd "$CHECKOUT" || exit 9
export HADRONIZATION_BASE="$CHECKOUT"
source ./setupEnv.sh >/dev/null 2>&1

MAN=$R/manifest.txt
{
  echo "# host=$(hostname)"
  echo "# started=$(date -Is)"
  echo "# tune=$TUNE"
  echo "# checkout=$(git rev-parse HEAD)"
  echo "# reader_sha=$(shasum -a 256 "$READER" | awk '{print $1}')"
  echo "# artifact_sha=$(shasum -a 256 "$ARTIFACT" | awk '{print $1}')"
  echo "# map_v2_sha=$(shasum -a 256 "$DECAY_MAP" | awk '{print $1}')"
  echo "# registry_sha=$(shasum -a 256 "$PAIR_REGISTRY" | awk '{print $1}')"
  echo "# central=$CENTRAL"
  echo "# blocks_base=$BLOCKS"
} > "$MAN"

# PREFLIGHT -- all eleven directories must exist with 300 root files each.
missing=0
for d in "$CENTRAL" $BLOCKS/combined_root_{1,2,3,4,5,6,7,8,9,10}; do
  n=$(ls "$d"/*.root 2>/dev/null | wc -l)
  echo "# input $(basename $d) root_files=$n" >> "$MAN"
  [[ "$n" -eq 300 ]] || missing=$((missing+1))
done
if [[ $missing -gt 0 ]]; then
  echo "PREFLIGHT_FAIL $missing of 11 inputs missing or not 300 files" | tee -a "$MAN"
  exit 3
fi
echo "# preflight=OK all 11 inputs present with 300 root files" >> "$MAN"

run_one() {
  local dir="$1" tag="$2"
  # The registry deduplicates trigger-owned histograms across pair files.
  # The v2 decay map supplies the current species-level parent splits.
  # The manifest records the deployed reader digest.
  python3 "$READER" "$dir" \
    --out "$R/$tag" \
    --artifact "$ARTIFACT" \
    --registry "$PAIR_REGISTRY" \
    --decay-map "$DECAY_MAP" \
    > "$R/${tag}.log" 2>&1
  echo "rc=$? $tag" >> "$R/DONE_LIST"
}

: > "$R/DONE_LIST"
run_one "$CENTRAL" central &
for i in 1 2 3 4 5; do run_one "$BLOCKS/combined_root_$i" "block_$i" & done
wait
for i in 6 7 8 9 10; do run_one "$BLOCKS/combined_root_$i" "block_$i" & done
wait

echo "# finished=$(date -Is)" >> "$MAN"
echo "# outputs=$(ls -d $R/central $R/block_* 2>/dev/null | wc -l)" >> "$MAN"
grep -c "^rc=0" "$R/DONE_LIST" | xargs -I{} echo "# rc0_count={} (expect 11)" >> "$MAN"
echo "TUNE_EXTRACT_DONE $TUNE"
