#!/bin/bash
# Build one systematics envelope from a resolved request plan.
#
# THE ORDER IS THE CONTRACT. Receipts are asserted BEFORE the extraction chain
# runs, because an extraction that consumes a FAILED variation produces numbers
# that look exactly like good ones. Every step stops the chain: a stage that
# records a mismatch and returns success is the specific defect that made the
# receipt rule (PRACTICE 3.5).
#
# INPUTS this script does not create. The measurement render logs and the
# measurement receipts come from `./hadronization plot <variation>
# measure-balancing`, run once per variation campaign. This script refuses
# when any of them is absent; it never renders them itself, because a
# systematic that silently re-rendered its own inputs could hide a change in
# the instrument between the nominal and the variation.
set -euo pipefail

PLAN="${1:?request plan required}"
OUT_DIR="${2:?systematics output directory required}"

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHECKOUT="${HADRONIZATION_BASE:-$(cd "${script_dir}/../.." && pwd)}"

case "${OUT_DIR}" in
  */plotting/*|*/plotting|*/plotting-syst/*|*/plotting-syst)
    echo "SYSTEMATICS_CHAIN_REFUSED an envelope may not be written under a plotting output plane: ${OUT_DIR}" >&2
    exit 2
    ;;
esac

read_plan() {
  python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))[sys.argv[2]])' \
    "${PLAN}" "$1"
}

CAMPAIGN="$(read_plan nominal_campaign)"
DATASET="$(read_plan nominal_dataset)"
ENVELOPE="$(read_plan envelope)"

TAGS="${OUT_DIR}/resolver_tags.json"
python3 -c 'import json,sys;json.dump(json.load(open(sys.argv[1]))["resolver_tags"],open(sys.argv[2],"w"),indent=1,sort_keys=True)' \
  "${PLAN}" "${TAGS}"

# ---- 1. every declared receipt must exist before anything else runs --------
missing=0
receipt_args=()
while IFS='=' read -r campaign path; do
  [[ -n "${campaign}" ]] || continue
  if [[ ! -f "${path}" ]]; then
    echo "SYSTEMATICS_CHAIN_MISSING_RECEIPT ${campaign} ${path}" >&2
    missing=1
    continue
  fi
  receipt_args+=(--receipt "${campaign}=${path}")
done < <(python3 -c 'import json,sys
plan=json.load(open(sys.argv[1]))
for campaign, path in sorted(plan["receipts"].items()):
    print(f"{campaign}={path}")' "${PLAN}")
if [[ "${missing}" -ne 0 ]]; then
  echo "SYSTEMATICS_CHAIN_REFUSED at least one declared measurement receipt is absent" >&2
  exit 3
fi

# ---- 2. the extraction chain ----------------------------------------------
REPORT="${OUT_DIR}/per_class_deltas.json"
NOMINAL_LOG="${HADRONIZATION_SYSTEMATICS_NOMINAL_LOG:?set HADRONIZATION_SYSTEMATICS_NOMINAL_LOG to the sealed nominal render log}"
CONTROL_LOG="${HADRONIZATION_SYSTEMATICS_CONTROL_LOG:?set HADRONIZATION_SYSTEMATICS_CONTROL_LOG to the control render log}"

variation_args=()
while IFS='=' read -r campaign path; do
  [[ -n "${campaign}" ]] || continue
  log="$(dirname "${path}")/render.log"
  if [[ ! -f "${log}" ]]; then
    echo "SYSTEMATICS_CHAIN_MISSING_LOG ${campaign} ${log}" >&2
    exit 3
  fi
  variation_args+=(--variation "${campaign}=${log}")
done < <(python3 -c 'import json,sys
plan=json.load(open(sys.argv[1]))
for campaign, path in sorted(plan["receipts"].items()):
    print(f"{campaign}={path}")' "${PLAN}")

python3 "${CHECKOUT}/extraction/harvest_class_report.py" \
  --nominal "${NOMINAL_LOG}" --control "${CONTROL_LOG}" \
  "${variation_args[@]}" --out "${REPORT}"

# ---- 3. the envelope -------------------------------------------------------
BOUNDARY_SHA="${HADRONIZATION_NOMINAL_BOUNDARY_RECEIPT_SHA256:-}"
python3 "${CHECKOUT}/tools/systematics_envelope.py" \
  --report "${REPORT}" \
  "${receipt_args[@]}" \
  --campaign "${CAMPAIGN}" \
  --nominal-dataset "${DATASET}" \
  --resolver-tags "${TAGS}" \
  --boundary-receipt-sha "${BOUNDARY_SHA}" \
  --out "${ENVELOPE}"
ENVELOPE_RC=$?
echo "SYSTEMATICS_CHAIN campaign=${CAMPAIGN} envelope=${ENVELOPE} rc=${ENVELOPE_RC}"
exit "${ENVELOPE_RC}"
