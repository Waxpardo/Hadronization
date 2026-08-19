#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 {monash|junctions|closepacking}"
  exit 1
fi

MODE="$1"

if [ "$MODE" != "monash" ] && [ "$MODE" != "junctions" ] && [ "$MODE" != "closepacking" ]; then
  echo "Error: mode must be one of 'monash', 'junctions', or 'closepacking'"
  exit 1
fi

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
OUTFILE="hf_${MODE}_${TIMESTAMP}.root"

SEED1=$RANDOM
SEED2=$RANDOM

echo "Running mode       : $MODE"
echo "Output file        : $OUTFILE"
echo "Seed modifiers     : $SEED1 $SEED2"

./heavyflavourcorrelations_status "$MODE" "$OUTFILE" "$SEED1" "$SEED2"
