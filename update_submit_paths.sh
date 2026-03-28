#!/bin/bash
# update_submit_paths.sh
# Update executable/initialdir in Condor submit files to match base_path.txt.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE_FILE="${SCRIPT_DIR}/base_path.txt"

if [ ! -f "${BASE_FILE}" ]; then
  echo "ERROR: base_path.txt not found at ${BASE_FILE}"
  exit 1
fi

BASE="$(cat "${BASE_FILE}")"
BASE="${BASE%/}"

if [ -z "${BASE}" ]; then
  echo "ERROR: base_path.txt is empty"
  exit 1
fi

update_file() {
  local file="$1"
  [ -f "${file}" ] || return 0

  perl -0pi -e "s|^executable\\s*=\\s*.*$|executable = ${BASE}/runCondorJob.sh|m; s|^initialdir\\s*=\\s*.*$|initialdir = ${BASE}|m" "${file}"
  echo "Updated: ${file}"
}

update_file "${SCRIPT_DIR}/submitCondor_10M.sub"
update_file "${SCRIPT_DIR}/submitCondor_hf_10M.sub"

mkdir -p \
  "${BASE}/RootFiles/HF/MONASH" \
  "${BASE}/RootFiles/HF/JUNCTIONS" \
  "${BASE}/RootFiles/bbbar/MONASH" \
  "${BASE}/RootFiles/bbbar/JUNCTIONS" \
  "${BASE}/RootFiles/ccbar/MONASH" \
  "${BASE}/RootFiles/ccbar/JUNCTIONS" \
  "${BASE}/Jobs/HF/MONASH" \
  "${BASE}/Jobs/HF/JUNCTIONS" \
  "${BASE}/Jobs/bbbar/MONASH" \
  "${BASE}/Jobs/bbbar/JUNCTIONS" \
  "${BASE}/Jobs/ccbar/MONASH" \
  "${BASE}/Jobs/ccbar/JUNCTIONS" \
  "${BASE}/logs/HF/MONASH" \
  "${BASE}/logs/HF/JUNCTIONS" \
  "${BASE}/logs/bbbar/MONASH" \
  "${BASE}/logs/bbbar/JUNCTIONS" \
  "${BASE}/logs/ccbar/MONASH" \
  "${BASE}/logs/ccbar/JUNCTIONS"

echo "Ensured output/work/log directory structure under: ${BASE}"
