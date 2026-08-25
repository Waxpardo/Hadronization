#!/bin/bash
# Build one systematics envelope from a resolved request plan.
#
# THE ORDER IS THE CONTRACT. Receipts are asserted BEFORE the extraction chain
# runs, because an extraction that consumes a FAILED variation produces numbers
# that look exactly like good ones. Every step stops the chain: a stage that
# records a mismatch and returns success is the specific defect that made the
# receipt rule (PRACTICE 3.5).
#
# WHICH ROOT SUPPLIED EACH INPUT. An accepted result is immutable under its own
# commit root, so tools/systematics_request.py resolves each input through the
# digest pin in config/accepted_measurements_v1.json when the current commit
# root lacks it. This script re-hashes every receipt against that resolution
# BEFORE it reads the render log beside it: the directory next to a wrong
# receipt holds wrong logs too.
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

# Which commit root supplied each campaign, and the digest the request tool
# resolved for it. The envelope re-checks both; this file is how they travel.
ROOTS="${OUT_DIR}/accepted_roots.json"
python3 -c 'import json,sys;json.dump(json.load(open(sys.argv[1]))["accepted_roots"],open(sys.argv[2],"w"),indent=1,sort_keys=True)' \
  "${PLAN}" "${ROOTS}"

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

# ---- 2. every receipt must hash to the digest the request tool resolved ----
python3 - "${PLAN}" <<'PY'
import hashlib, json, sys
plan = json.load(open(sys.argv[1]))
roots = plan["accepted_roots"]
bad = 0
for campaign, path in sorted(plan["receipts"].items()):
    row = roots.get(campaign)
    if row is None:
        print(f"SYSTEMATICS_CHAIN_UNRESOLVED_ROOT {campaign} {path}",
              file=sys.stderr)
        bad = 1
        continue
    measured = hashlib.sha256(open(path, "rb").read()).hexdigest()
    if measured != row["receipt_sha256"]:
        print(f"SYSTEMATICS_CHAIN_RECEIPT_DIGEST {campaign} root={row['root']} "
              f"measured={measured} resolved={row['receipt_sha256']}",
              file=sys.stderr)
        bad = 1
        continue
    print(f"SYSTEMATICS_CHAIN_INPUT {campaign} root={row['root']} "
          f"source={row['source']} sha256={measured}")
sys.exit(4 if bad else 0)
PY

# ---- 3. the extraction chain ----------------------------------------------
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

# ---- 4. the envelope -------------------------------------------------------
# The nominal boundary receipt comes from the request plan, which resolved it
# against the current commit root first and the accepted pin second. An
# exported value may agree with that answer; it may not replace it.
BOUNDARY_SHA="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["nominal_boundary"]["boundary_receipt_sha256"])' "${PLAN}")"
BOUNDARY_ROOT="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["nominal_boundary"]["root"])' "${PLAN}")"
if [[ -z "${BOUNDARY_SHA}" ]]; then
  echo "SYSTEMATICS_CHAIN_REFUSED the request plan resolved no nominal boundary receipt" >&2
  exit 3
fi
EXPORTED_SHA="${HADRONIZATION_NOMINAL_BOUNDARY_RECEIPT_SHA256:-}"
if [[ -n "${EXPORTED_SHA}" && "${EXPORTED_SHA}" != "${BOUNDARY_SHA}" ]]; then
  echo "SYSTEMATICS_CHAIN_REFUSED HADRONIZATION_NOMINAL_BOUNDARY_RECEIPT_SHA256=${EXPORTED_SHA} disagrees with the plan's ${BOUNDARY_SHA}" >&2
  exit 3
fi
echo "SYSTEMATICS_CHAIN_NOMINAL_BOUNDARY root=${BOUNDARY_ROOT} sha256=${BOUNDARY_SHA}"

python3 "${CHECKOUT}/tools/systematics_envelope.py" \
  --report "${REPORT}" \
  "${receipt_args[@]}" \
  --campaign "${CAMPAIGN}" \
  --nominal-dataset "${DATASET}" \
  --resolver-tags "${TAGS}" \
  --accepted-roots "${ROOTS}" \
  --boundary-receipt-sha "${BOUNDARY_SHA}" \
  --out "${ENVELOPE}"
ENVELOPE_RC=$?
echo "SYSTEMATICS_CHAIN campaign=${CAMPAIGN} envelope=${ENVELOPE} rc=${ENVELOPE_RC}"
exit "${ENVELOPE_RC}"
