#!/bin/bash
# Extract the A2 per-slot pair yields for one tune and one arm into one CSV.
#
# analysis/a2_pair_yield.C handles ONE slot and appends. This drives it over the
# slot range and nothing else -- the observable, the multiplicity classes and
# the OS/SS join all live where the pre-registration put them, and none of them
# is re-decided here.
#
# The CSV is removed first: appending to a stale file would silently mix two
# extractions, and the row count check at the end would not notice because it
# would only be too LARGE, which is the direction nobody looks at.
#
# Usage:
#   tools/a2_extract_yields.sh SLOT_ROOT OUT_CSV [N_SLOTS]
# where SLOT_ROOT holds slot_000 .. slot_(N-1).
set -euo pipefail

slot_root="${1:?SLOT_ROOT required}"
out_csv="${2:?OUT_CSV required}"
n_slots="${3:-100}"

project_base="${HADRONIZATION_BASE:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
macro="${project_base}/analysis/a2_pair_yield.C"
if [[ ! -f "${macro}" ]]; then
  echo "ERROR: missing ${macro}" >&2
  exit 2
fi

rm -f "${out_csv}"
missing_slots=0
wrote_header=false
for ((slot = 0; slot < n_slots; ++slot)); do
  dir="$(printf '%s/slot_%03d' "${slot_root}" "${slot}")"
  if [[ ! -d "${dir}" ]]; then
    echo "MISSING_SLOT ${dir}" >&2
    missing_slots=$((missing_slots + 1))
    continue
  fi
  # a2_pair_yield.C's `append` argument DEFAULTS TO FALSE, which truncates and
  # rewrites the header. Driving it without this flag leaves a CSV holding only
  # the LAST slot -- a silently wrong extraction that still looks well-formed.
  append="true"
  if [[ "${wrote_header}" == "false" ]]; then append="false"; fi
  root -l -b -q "${macro}(\"${dir}\",${slot},\"${out_csv}\",${append})" 2>&1 \
    | grep -E 'A2_YIELD_DONE|A2_YIELD_ERROR|Error|error:' || true
  wrote_header=true
done

if [[ "${missing_slots}" -ne 0 ]]; then
  echo "ERROR: ${missing_slots} of ${n_slots} slot directories were absent." >&2
  echo "       A partial arm must not be compared against a complete one." >&2
  exit 3
fi

# Assert what the truncate bug would have destroyed: one header, and one
# distinct slot value per requested slot.
headers="$(grep -c '^slot,pair_file,mclass,yield$' "${out_csv}")"
distinct_slots="$(tail -n +2 "${out_csv}" | cut -d, -f1 | sort -u | wc -l)"
rows="$(wc -l < "${out_csv}")"
if [[ "${headers}" -ne 1 || "${distinct_slots}" -ne "${n_slots}" ]]; then
  echo "ERROR: ${out_csv} carries ${headers} header lines and ${distinct_slots}" >&2
  echo "       distinct slots; expected 1 and ${n_slots}." >&2
  exit 4
fi
echo "A2_EXTRACT_DONE root=${slot_root} csv=${out_csv} slots=${distinct_slots} rows=${rows}"
