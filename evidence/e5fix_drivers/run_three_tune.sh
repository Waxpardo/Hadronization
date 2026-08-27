#!/bin/bash
# Extract central + ten blocks for JUNCTIONS and CLOSEPACKING with the same
# E5-fixed, trigger-deduplicating extractor that produced the MONASH table of
# record (sha 4cd8b6fa...). Fresh run root: the 2026-08-13 outputs under
# tune_runs_e5fix/ are left untouched so JUNCTIONS central can be cross-checked
# against its independent earlier extraction.
set -uo pipefail
B=/data/alice/ipardoza/extractor_e5fix
S=/data/alice/ipardoza/hadronization_merged/SUBSAMPLES_HF_RUN3_V1
C=/data/alice/ipardoza/hadronization_merged
R=/data/alice/ipardoza/tune_runs_three

echo "# three-tune extraction started=$(date -Is)"
for T in JUNCTIONS CLOSEPACKING; do
  O="$R/$T"; mkdir -p "$O"
  echo "=== $T central $(date -Is) ==="
  if ! "$B/run_extract.sh" "$C/complete_root_HF_RUN3_V1_$T" "$O/central" > "$O/central.log" 2>&1; then
    echo "${T}_CENTRAL_FAILED"; tail -5 "$O/central.log"
  else
    grep -E "^EXTRACTION|^DEDUPLICATION|^SELF_CHECK|^REGROUP" "$O/central.log"
  fi
  for i in $(seq 1 10); do
    echo "=== $T block $i $(date -Is) ==="
    if ! "$B/run_extract.sh" "$S/combined_root_subSamples_$T/combined_root_$i" "$O/block_$i" > "$O/block_$i.log" 2>&1; then
      echo "${T}_BLOCK_${i}_FAILED"; tail -5 "$O/block_$i.log"
    else
      grep -E "^EXTRACTION|^DEDUPLICATION|^SELF_CHECK|^REGROUP" "$O/block_$i.log"
    fi
  done
done
echo "# three-tune extraction finished=$(date -Is)"
echo THREE_TUNE_EXTRACTION_DONE
