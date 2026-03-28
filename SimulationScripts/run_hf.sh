#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 {monash|junctions}"
  exit 1
fi

MODE="$1"

if [ "$MODE" != "monash" ] && [ "$MODE" != "junctions" ]; then
  echo "Error: mode must be either 'monash' or 'junctions'"
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