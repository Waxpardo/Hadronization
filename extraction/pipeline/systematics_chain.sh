#!/bin/bash
# Build one systematics envelope from a resolved request plan.
#
# THE ORDER IS THE CONTRACT. Receipts are asserted BEFORE the extraction chain
# runs, because an extraction that consumes a FAILED variation produces numbers
# that look exactly like good ones. Every step stops the chain: a stage that
# records a mismatch and returns success is the specific defect that made the
# receipt rule (PRACTICE 3.5).
#
# EVERY REFUSAL EXITS NONZERO, AND SAYS SO EXPLICITLY. The envelope probe of
# 2026-08-25 reported a refusal that reached its caller as status 0. A refusal
# a caller cannot tell from success is not a refusal. So no step here relies on
# `set -e` to carry a status outward: each one captures the status it cares
# about and exits with it, and `refuse` is the only way out of a failed gate.
#
# INPUTS this script does not create. The measurement render logs and the
# measurement receipts come from `./hadronization plot <variation>
# measure-balancing`, run once per variation campaign. This script refuses
# when any of them is absent; it never renders them itself, because a
# systematic that silently re-rendered its own inputs could hide a change in
# the instrument between the nominal and the variation.
#
# WHICH ROOT SUPPLIED EACH INPUT. An accepted result is immutable under its own
# commit root, so tools/systematics_request.py resolves each input through the
# digest pin in config/accepted_measurements_v1.json when the current commit
# root lacks it. This script re-hashes every receipt against that resolution
# BEFORE it reads the render log beside it: the directory next to a wrong
# receipt holds wrong logs too.
set -euo pipefail

PLAN="${1:?request plan required}"
OUT_DIR="${2:?systematics output directory required}"

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHECKOUT="${HADRONIZATION_BASE:-$(cd "${script_dir}/../.." && pwd)}"

refuse() {
  local status="$1"; shift
  echo "SYSTEMATICS_CHAIN_REFUSED $*" >&2
  exit "${status}"
}

case "${OUT_DIR}" in
  */plotting/*|*/plotting|*/plotting-syst/*|*/plotting-syst)
    refuse 2 "an envelope may not be written under a plotting output plane: ${OUT_DIR}"
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
  refuse 3 "at least one declared measurement receipt is absent"
fi

# ---- 2. every receipt must hash to the digest the request tool resolved ----
digest_status=0
python3 - "${PLAN}" <<'PY' || digest_status=$?
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
if [[ "${digest_status}" -ne 0 ]]; then
  refuse "${digest_status}" "at least one measurement receipt does not hash to the digest the request resolved"
fi

# ---- 3. the extraction chain ----------------------------------------------
REPORT="${OUT_DIR}/per_class_deltas.json"
NOMINAL_LOG="${HADRONIZATION_SYSTEMATICS_NOMINAL_LOG:?set HADRONIZATION_SYSTEMATICS_NOMINAL_LOG to the new nominal v2 measurement render log}"
CONTROL_LOG="${HADRONIZATION_SYSTEMATICS_CONTROL_LOG:?set HADRONIZATION_SYSTEMATICS_CONTROL_LOG to the accepted historical shared-field control log}"

variation_args=()
while IFS='=' read -r campaign path; do
  [[ -n "${campaign}" ]] || continue
  log="$(dirname "${path}")/render.log"
  if [[ ! -f "${log}" ]]; then
    echo "SYSTEMATICS_CHAIN_MISSING_LOG ${campaign} ${log}" >&2
    refuse 3 "at least one variation render log is absent"
  fi
  variation_args+=(--variation "${campaign}=${log}")
done < <(python3 -c 'import json,sys
plan=json.load(open(sys.argv[1]))
for campaign, path in sorted(plan["receipts"].items()):
    print(f"{campaign}={path}")' "${PLAN}")

HARVEST_RC=0
python3 "${CHECKOUT}/extraction/harvest_class_report.py" \
  --nominal "${NOMINAL_LOG}" --control "${CONTROL_LOG}" \
  "${variation_args[@]}" --out "${REPORT}" || HARVEST_RC=$?
if [[ "${HARVEST_RC}" -ne 0 ]]; then
  refuse "${HARVEST_RC}" "harvest_class_report.py exited ${HARVEST_RC}"
fi

# ---- 4. the envelope -------------------------------------------------------
# The nominal boundary receipt comes from the request plan, which resolved it
# against the current commit root first and the accepted pin second. An
# exported value may agree with that answer; it may not replace it.
BOUNDARY_SHA="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["nominal_boundary"]["boundary_receipt_sha256"])' "${PLAN}")"
BOUNDARY_ROOT="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["nominal_boundary"]["root"])' "${PLAN}")"
BOUNDARY_PATH="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["nominal_boundary"]["path"])' "${PLAN}")"
if [[ -z "${BOUNDARY_SHA}" ]]; then
  refuse 3 "the request plan resolved no nominal boundary receipt; the envelope cannot be bound to the render it applies to"
fi
EXPORTED_SHA="${HADRONIZATION_NOMINAL_BOUNDARY_RECEIPT_SHA256:-}"
if [[ -n "${EXPORTED_SHA}" && "${EXPORTED_SHA}" != "${BOUNDARY_SHA}" ]]; then
  refuse 3 "HADRONIZATION_NOMINAL_BOUNDARY_RECEIPT_SHA256=${EXPORTED_SHA} disagrees with the plan's ${BOUNDARY_SHA}"
fi
echo "SYSTEMATICS_CHAIN_NOMINAL_BOUNDARY root=${BOUNDARY_ROOT} sha256=${BOUNDARY_SHA}"

ENVELOPE_RC=0
python3 "${CHECKOUT}/tools/systematics_envelope.py" \
  --report "${REPORT}" \
  "${receipt_args[@]}" \
  --campaign "${CAMPAIGN}" \
  --nominal-dataset "${DATASET}" \
  --resolver-tags "${TAGS}" \
  --accepted-roots "${ROOTS}" \
  --boundary-receipt-sha "${BOUNDARY_SHA}" \
  --boundary-receipt "${BOUNDARY_PATH}" \
  --out "${ENVELOPE}" || ENVELOPE_RC=$?
echo "SYSTEMATICS_CHAIN campaign=${CAMPAIGN} envelope=${ENVELOPE} rc=${ENVELOPE_RC}"
if [[ "${ENVELOPE_RC}" -ne 0 ]]; then
  refuse "${ENVELOPE_RC}" "systematics_envelope.py exited ${ENVELOPE_RC}"
fi
exit 0
