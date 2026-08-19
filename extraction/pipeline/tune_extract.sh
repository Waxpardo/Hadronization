#!/bin/bash
# Per-tune extraction: run the species-decomposition reader on the central and
# all ten blocks of ONE tune, writing per_species.csv for each.
#
# The reader postdates the frozen checkout, so it runs from scratch-deploy with
# its sha recorded -- the M7b pattern. The frozen checkout is READ for setupEnv
# only and never written.
#
# Blocks run in parallel batches; each is an independent ROOT process over its
# own 300-file directory.
set -u
TUNE="$1"
CHECKOUT=/data/alice/ipardoza/Hadronization
R=/data/alice/ipardoza/tune_runs/$TUNE
T=/data/alice/ipardoza/sigmab_runs/task22          # holds the deployed reader
MERGED=/data/alice/ipardoza/hadronization_merged
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
  echo "# reader_sha=$(sha256sum $T/extract_species_decomposition.py | awk '{print $1}')"
  echo "# artifact_sha=$(sha256sum $T/species_ordinals_v2.json | awk '{print $1}')"
  echo "# map_v2_sha=$(sha256sum $T/decay_parent_map_v2.json | awk '{print $1}')"
  echo "# registry_sha=$(sha256sum $T/../config/heavy_flavour_pair_registry_v1.json | awk '{print $1}')"
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
  # E5 FIX, 2026-08-13. The Nikhef copy of this script was corrected in place
  # earlier today; THIS repo copy was not, so the tracked version would have
  # reintroduced the defect for anyone deploying from the repo. Three things are
  # load-bearing:
  #   --registry  : REQUIRED for trigger-level deduplication. The closure
  #                 histograms are TRIGGER-owned and were written into every
  #                 pair file sharing that trigger, so summing files counted
  #                 each charm trigger 24x and each beauty trigger 26x. Only the
  #                 signed registry says which trigger a file belongs to.
  #   --decay-map : v1_1 -> v2. v1_1 is the retired conjugation fix; v2 is
  #                 current and carries the two species-level splits.
  #   the reader at $T must be the DEDUPLICATING one (sha 4cd8b6fa...). The
  #                 replicating one (b67f9008...) is archived on Nikhef under
  #                 attic_e5_replicating_extractor_20260813/.
  python3 "$T/extract_species_decomposition.py" "$dir" \
    --out "$R/$tag" \
    --artifact "$T/species_ordinals_v2.json" \
    --registry "$T/../config/heavy_flavour_pair_registry_v1.json" \
    --decay-map "$T/decay_parent_map_v2.json" \
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
