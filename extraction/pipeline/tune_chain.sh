#!/bin/bash
# Wait for a tune's 10 blocks to be promoted, then run closure, then extraction.
# Chained server-side so the waiting costs the session nothing.
set -u

# Every absolute script this chain invokes must exist before the chain starts.
# The 2026-08-17 consolidation moved tune_extract.sh and updated the translation
# table without updating this caller, so the chain named a path that was not
# there. A missing callee is a silent no-op inside a `>> "$LOG" 2>&1` redirect:
# the step "runs", writes an error nobody reads, and the chain reports done.
assert_invoked_paths_exist() {
  local self="${BASH_SOURCE[0]}" missing=0 path
  while read -r path; do
    [ -f "$path" ] || { echo "TUNE_CHAIN_MISSING_CALLEE $path" >&2; missing=1; }
  done < <(grep -oE '^[[:space:]]*bash[[:space:]]+/[^"[:space:]]+' "$self" \
             | awk '{print $2}')
  [ "$missing" -eq 0 ] || {
    echo "TUNE_CHAIN_REFUSED one or more invoked scripts do not exist" >&2
    exit 3
  }
}
assert_invoked_paths_exist

TUNE="$1"
CHECKOUT=/data/alice/ipardoza/Hadronization
MERGED=/data/alice/ipardoza/hadronization_merged
CENTRAL=$MERGED/complete_root_HF_RUN3_V1_${TUNE}
BLOCKS=$MERGED/SUBSAMPLES_HF_RUN3_V1/combined_root_subSamples_${TUNE}
R=/data/alice/ipardoza/tune_runs/$TUNE
mkdir -p "$R"
LOG=$R/chain.log
: > "$LOG"
echo "# chain started=$(date -Is) tune=$TUNE" >> "$LOG"

# ---- 1. wait for all ten blocks + central (up to 30 h) ----------------------
# CLOSEPACKING is last in the merge order and can be a day out, so the ceiling
# is generous. It is a ceiling, not a schedule.
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
# FAIL CLOSED. A wait that times out must NOT fall through to closure on
# incomplete input -- that would produce a failing closure log that looks like
# a physics result rather than a missing-input error.
if [[ $ok -ne 1 ]]; then
  echo "# CHAIN_ABORT inputs never completed within the wait ceiling" >> "$LOG"
  echo "TUNE_CHAIN_ABORTED $TUNE" >> "$LOG"
  exit 4
fi
echo "# all_inputs_present=$(date -Is)" >> "$LOG"

# ---- 2. CLOSURE ------------------------------------------------------------
cd "$CHECKOUT" || exit 9
export HADRONIZATION_BASE="$CHECKOUT"
# EXPECTED_SCHEMA is stated by the caller and has no default (review finding
# A4). This call used to pass two arguments and could therefore only ever exit
# 2 on the wrapper's own usage check -- and the chain went on to extraction
# anyway, because CLOSURE_RC below is recorded and not acted on. The arity is
# fixed here; the fall-through is recorded as a finding and is not this
# session's to restructure.
SCHEMA="${HADRONIZATION_EXPECTED_PAIR_SCHEMA:-}"
if [[ -z "$SCHEMA" ]]; then
  echo "# CHAIN_ABORT HADRONIZATION_EXPECTED_PAIR_SCHEMA is required and has no default" >> "$LOG"
  echo "TUNE_CHAIN_ABORTED $TUNE" >> "$LOG"
  exit 2
fi
echo "=== CLOSURE $TUNE ===" >> "$LOG"
echo "# closure_expected_schema=$SCHEMA" >> "$LOG"
echo "# closure_script_sha=$(sha256sum Validation/validate_pair_block_closure.sh | awk '{print $1}')" >> "$LOG"
echo "# closure_macro_sha=$(sha256sum Validation/ValidatePairBlockClosure.C | awk '{print $1}')" >> "$LOG"
bash Validation/validate_pair_block_closure.sh "$CENTRAL" "$BLOCKS" "$SCHEMA" >> "$LOG" 2>&1
echo "# CLOSURE_RC=$?" >> "$LOG"

# ---- 3. EXTRACTION (central + 10 blocks) -----------------------------------
echo "=== EXTRACTION $TUNE ===" >> "$LOG"
bash /data/alice/ipardoza/hadronization/scratch/deploys/tune_extract.sh "$TUNE" >> "$LOG" 2>&1
echo "# EXTRACT_RC=$?" >> "$LOG"
echo "# chain finished=$(date -Is)" >> "$LOG"
echo "TUNE_CHAIN_DONE $TUNE" >> "$LOG"
