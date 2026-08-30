#!/bin/bash
# Wait for one tune's 10 promoted blocks, then run closure and extraction.
# Long-running execution may be detached according to the local site's policy.
set -euo pipefail

TUNE="${1:?tune required}"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHECKOUT="${HADRONIZATION_BASE:-$(cd "${script_dir}/../.." && pwd)}"
MERGED="${HADRONIZATION_MERGED_ROOT:?set HADRONIZATION_MERGED_ROOT}"
RUN_ROOT="${HADRONIZATION_EXTRACTION_RUN_ROOT:?set HADRONIZATION_EXTRACTION_RUN_ROOT}"
TUNE_EXTRACT="${HADRONIZATION_TUNE_EXTRACT:-${CHECKOUT}/extraction/pipeline/tune_extract.sh}"
if [[ ! -f "${TUNE_EXTRACT}" ]]; then
  echo "TUNE_CHAIN_MISSING_CALLEE ${TUNE_EXTRACT}" >&2
  echo "TUNE_CHAIN_REFUSED extraction entrypoint does not exist" >&2
  exit 3
fi
CENTRAL=$MERGED/complete_root_HF_RUN3_V1_${TUNE}
BLOCKS=$MERGED/SUBSAMPLES_HF_RUN3_V1/combined_root_subSamples_${TUNE}
R=$RUN_ROOT/$TUNE
mkdir -p "$R"
LOG=$R/chain.log
: > "$LOG"
echo "# chain started=$(date -Is) tune=$TUNE" >> "$LOG"

# ---- 1. wait for all ten blocks + central (up to 30 h) ----------------------
# The 30-hour ceiling allows for a delayed final merge.
ok=0
for i in $(seq 1 3600); do
  ok=1
  [[ -d "$CENTRAL" ]] || ok=0
  for b in 1 2 3 4 5 6 7 8 9 10; do
    [[ -d "$BLOCKS/combined_root_$b" ]] || ok=0
  done
  [[ $ok -eq 1 ]] && break
  sleep 30
done
# Stop after a timeout so closure cannot inspect incomplete input.
if [[ $ok -ne 1 ]]; then
  echo "# CHAIN_ABORT inputs never completed within the wait ceiling" >> "$LOG"
  echo "TUNE_CHAIN_ABORTED $TUNE" >> "$LOG"
  exit 4
fi
echo "# all_inputs_present=$(date -Is)" >> "$LOG"

# ---- 2. CLOSURE ------------------------------------------------------------
cd "$CHECKOUT" || exit 9
export HADRONIZATION_BASE="$CHECKOUT"
# The caller must state the expected pair schema.
SCHEMA="${HADRONIZATION_EXPECTED_PAIR_SCHEMA:-}"
if [[ -z "$SCHEMA" ]]; then
  echo "# CHAIN_ABORT HADRONIZATION_EXPECTED_PAIR_SCHEMA is required and has no default" >> "$LOG"
  echo "TUNE_CHAIN_ABORTED $TUNE" >> "$LOG"
  exit 2
fi
echo "=== CLOSURE $TUNE ===" >> "$LOG"
echo "# closure_expected_schema=$SCHEMA" >> "$LOG"
echo "# closure_script_sha=$(shasum -a 256 Validation/validate_pair_block_closure.sh | awk '{print $1}')" >> "$LOG"
echo "# closure_macro_sha=$(shasum -a 256 Validation/ValidatePairBlockClosure.C | awk '{print $1}')" >> "$LOG"
set +e
bash Validation/validate_pair_block_closure.sh "$CENTRAL" "$BLOCKS" "$SCHEMA" >> "$LOG" 2>&1
rc=$?
set -e
if [[ $rc -eq 0 ]]; then
  echo "# CLOSURE_RC=0" >> "$LOG"
else
  echo "# CLOSURE_RC=$rc" >> "$LOG"
  echo "TUNE_CHAIN_ABORTED $TUNE" >> "$LOG"
  exit "$rc"
fi

# ---- 3. EXTRACTION (central + 10 blocks) -----------------------------------
echo "=== EXTRACTION $TUNE ===" >> "$LOG"
if bash "$TUNE_EXTRACT" "$TUNE" >> "$LOG" 2>&1; then
  echo "# EXTRACT_RC=0" >> "$LOG"
else
  rc=$?
  echo "# EXTRACT_RC=$rc" >> "$LOG"
  echo "TUNE_CHAIN_ABORTED $TUNE" >> "$LOG"
  exit "$rc"
fi
echo "# chain finished=$(date -Is)" >> "$LOG"
echo "TUNE_CHAIN_DONE $TUNE" >> "$LOG"
