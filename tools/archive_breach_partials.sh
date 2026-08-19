#!/usr/bin/env bash
# Move provably-superseded .partial. staging directories out of the gate's scan
# root, and emit a manifest of exactly what moved.
#
# WHY THIS EXISTS. The v3 analysis campaign's checkout-freeze breach left 34
# staging directories in MONASH slots 298-331. A job writes
# `slot_NNN.partial.XXXXXX`, validates it, and promotes it by atomic rename; the
# breach made promotion fail after the work had succeeded, so the staging
# directory survived and the slot was later re-run successfully.
#
# `tools/validate_analysis_outputs.py:365` sweeps ANY directory containing
# `.partial.` into `staging`, and `:373` raises unconditionally. There is no
# flag to tolerate it, and THAT IS CORRECT -- stale material in the scan root is
# exactly what a gate should refuse. This script does not weaken the gate; it
# removes the material the gate is right to object to.
#
# NOTHING IS DELETED. Every directory is MOVED, and the manifest records where
# from and where to, so the move is reversible by reading it.
#
# THE REDUNDANCY CHECK IS THE POINT, and it fails closed. A partial may only be
# moved if its promoted slot:
#   - exists,
#   - holds exactly 302 entries (300 pair files + metadata + log),
#   - carries analysis_job_metadata.json (whose ABSENCE in the partial is what
#     identifies the partial as a failed promotion rather than a failed run),
#   - has a log certifying exactly one ONE_PASS_ANALYSIS_SUMMARY and no
#     ONE_PASS_ANALYSIS_ERROR,
#   - and passed ValidatePairDirectory with errors=0, evidenced by a results
#     file passed in with --evidence.
# Any partial failing any check is LEFT IN PLACE and reported. One failure does
# not block the others, but it does block the gate, which is the intended
# pressure.
#
# Dry run is the default. --apply moves.
#
# Usage:
#   tools/archive_breach_partials.sh --root <per_job/TUNE> --archive <dir> \
#       --evidence <validate log> [--apply]

set -euo pipefail

ROOT=""; ARCHIVE=""; EVIDENCE=""; APPLY=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --root) ROOT="${2:-}"; shift 2 ;;
    --archive) ARCHIVE="${2:-}"; shift 2 ;;
    --evidence) EVIDENCE="${2:-}"; shift 2 ;;
    --apply) APPLY=1; shift ;;
    -h|--help) sed -n '2,40p' "$0"; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done
[[ -n "$ROOT" && -n "$ARCHIVE" && -n "$EVIDENCE" ]] || {
  echo "ERROR: --root, --archive and --evidence are all required" >&2; exit 2; }
[[ -d "$ROOT" ]] || { echo "ERROR: no such root: $ROOT" >&2; exit 2; }
[[ -f "$EVIDENCE" ]] || { echo "ERROR: no such evidence file: $EVIDENCE" >&2; exit 2; }

echo "# archive_breach_partials $( [[ $APPLY -eq 1 ]] && echo APPLY || echo DRY-RUN )"
echo "# root=$ROOT"
echo "# archive=$ARCHIVE"
echo "# evidence=$EVIDENCE"
echo "# generated=$(date -Is)"
echo "#"

moved=0; held=0; total=0
for p in $(ls "$ROOT" | grep "\.partial\." | sort); do
  total=$((total+1))
  n="${p%%.partial.*}"
  d="$ROOT/$n"
  reason=""

  [[ -d "$d" ]] || reason="promoted-slot-absent"
  if [[ -z "$reason" ]]; then
    sf=$(ls "$d" | wc -l | tr -d ' ')
    [[ "$sf" == "302" ]] || reason="promoted-slot-has-$sf-entries-not-302"
  fi
  if [[ -z "$reason" ]]; then
    [[ -f "$d/analysis_job_metadata.json" ]] || reason="promoted-slot-missing-metadata"
  fi
  if [[ -z "$reason" ]]; then
    su=$(grep -c ONE_PASS_ANALYSIS_SUMMARY "$d/analysis.log" 2>/dev/null || :)
    er=$(grep -c ONE_PASS_ANALYSIS_ERROR "$d/analysis.log" 2>/dev/null || :)
    [[ "$su" == "1" ]] || reason="promoted-slot-summary-count-$su"
    [[ -z "$reason" && "$er" == "0" ]] || { [[ -n "$reason" ]] || reason="promoted-slot-has-$er-errors"; }
  fi
  if [[ -z "$reason" ]]; then
    # ValidatePairDirectory evidence: the slot must appear with rc=0 errors=0.
    grep -q "slot=${n#slot_} rc=0 errors=0" "$EVIDENCE" || reason="no-validation-evidence"
  fi
  # A partial that already carries metadata was NOT a failed promotion and is
  # not covered by this ruling.
  if [[ -z "$reason" && -f "$ROOT/$p/analysis_job_metadata.json" ]]; then
    reason="partial-has-metadata-not-a-failed-promotion"
  fi

  pf=$(ls "$ROOT/$p" | wc -l | tr -d ' ')
  bytes=$(du -sb "$ROOT/$p" 2>/dev/null | cut -f1)

  if [[ -n "$reason" ]]; then
    held=$((held+1))
    printf 'HELD    %-32s slot=%-9s files=%-5s bytes=%-12s reason=%s\n' "$p" "$n" "$pf" "${bytes:-?}" "$reason"
    continue
  fi

  printf 'MOVE    %-32s slot=%-9s files=%-5s bytes=%-12s from=%s to=%s\n' \
    "$p" "$n" "$pf" "${bytes:-?}" "$ROOT/$p" "$ARCHIVE/$p"
  if [[ $APPLY -eq 1 ]]; then
    mkdir -p "$ARCHIVE"
    [[ -e "$ARCHIVE/$p" ]] && { echo "ERROR: destination exists: $ARCHIVE/$p" >&2; exit 3; }
    mv "$ROOT/$p" "$ARCHIVE/$p"
  fi
  moved=$((moved+1))
done

echo "#"
printf '# TOTAL=%s MOVED=%s HELD=%s mode=%s\n' "$total" "$moved" "$held" \
  "$( [[ $APPLY -eq 1 ]] && echo APPLY || echo DRY-RUN )"
[[ $held -eq 0 ]] || echo "# NOTE: held partials remain in the scan root and the gate will still refuse."
