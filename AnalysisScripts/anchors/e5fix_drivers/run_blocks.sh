#!/bin/bash
# Re-extract MONASH's ten canonical blocks with the E5-fixed extractor.
set -uo pipefail
B=/data/alice/ipardoza/extractor_e5fix
S=/data/alice/ipardoza/hadronization_merged/SUBSAMPLES_HF_RUN3_V1/combined_root_subSamples_MONASH
O=/data/alice/ipardoza/tune_runs_e5fix/MONASH
echo "# blocks started=$(date -Is)"
for i in $(seq 1 10); do
  echo "=== BLOCK $i $(date -Is) ==="
  if ! "$B/run_extract.sh" "$S/combined_root_$i" "$O/block_$i" > "$O/block_$i.log" 2>&1; then
    echo "BLOCK_${i}_FAILED rc=$?"
    tail -5 "$O/block_$i.log"
  else
    grep -E "^EXTRACTION|^DEDUPLICATION|^SELF_CHECK" "$O/block_$i.log"
  fi
done
echo "# blocks finished=$(date -Is)"
echo BLOCKS_DONE
