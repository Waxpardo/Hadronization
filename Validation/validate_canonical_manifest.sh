#!/bin/bash
set -euo pipefail

if [[ "$#" -ne 3 ]]; then
  echo "Usage: $0 FREEZE_DIR PRODUCTION_ROOT LOG_PATH" >&2
  exit 2
fi
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_base="$(cd "${script_dir}/.." && pwd)"
freeze_dir="$(cd "$1" && pwd)"
production_root="$(cd "$2" && pwd)"
log_path="$3"
export HADRONIZATION_BASE="${HADRONIZATION_BASE:-${project_base}}"
source "${project_base}/setupEnv.sh"

# Validate every raw path and digest, count events, and require unique seeds.
shape="$(
python3 -c '
import hashlib,json,pathlib,sys
manifest=pathlib.Path(sys.argv[1])
production=pathlib.Path(sys.argv[2])
rows=[]
for line in manifest.read_text().splitlines():
    if not line.strip():
        continue
    row=json.loads(line)
    rows.append(row)
    path=production / row["raw_path"]
    value=hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(16*1024*1024), b""):
            value.update(chunk)
    if value.hexdigest() != row["raw_sha256"]:
        raise SystemExit("checksum mismatch: %s" % path)
if not rows:
    raise SystemExit("canonical manifest is empty")
events=sum(int(row["requested_successes"]) for row in rows)
seeds=len({int(row["seed"]) for row in rows})
print("%d %d %d" % (len(rows), seeds, events))
' "${freeze_dir}/canonical_manifest.jsonl" "${production_root}"
)"
read -r expected_rows expected_seeds expected_events <<<"${shape}"
if [[ ! "${expected_rows}" =~ ^[0-9]+$ ]] ||
   [[ ! "${expected_seeds}" =~ ^[0-9]+$ ]] ||
   [[ ! "${expected_events}" =~ ^[0-9]+$ ]]; then
  echo "ERROR: invalid canonical manifest shape: ${shape}" >&2
  exit 1
fi
echo "CANONICAL_SHA256_VALID files=${expected_rows} unique_seeds=${expected_seeds} total_events=${expected_events}"

mkdir -p "$(dirname "${log_path}")"
validation_log="$(mktemp "${log_path}.partial.XXXXXX")"
status=0
root -l -b -q \
  "${script_dir}/ValidateCanonicalRawManifest.C(\"${freeze_dir}/canonical_manifest.jsonl\",\"${production_root}\")" \
  >"${validation_log}" 2>&1 || status=$?
cat "${validation_log}"
if (( status != 0 )) ||
   [[ "$(grep -c "^CANONICAL_RAW_VALIDATION errors=0 files=${expected_rows} unique_seeds=${expected_seeds} total_events=${expected_events}$" \
       "${validation_log}")" -ne 1 ]] ||
   grep -qE 'CANONICAL_RAW_ERROR|RAW_VALIDATION_ERROR|segmentation violation|Break +segmentation|cling JIT session error' \
     "${validation_log}"; then
  echo "ERROR: canonical raw validation failed; retained log ${validation_log}" >&2
  exit 1
fi

if [[ -e "${log_path}" ]]; then
  if ! cmp -s "${validation_log}" "${log_path}"; then
    echo "ERROR: refusing to overwrite different validation log ${log_path}; retained ${validation_log}" >&2
    exit 1
  fi
  rm -f "${validation_log}"
else
  mv "${validation_log}" "${log_path}"
fi
echo "CANONICAL_MANIFEST_VALIDATED freeze=${freeze_dir} log=${log_path}"
