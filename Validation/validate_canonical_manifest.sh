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

python3 "${project_base}/tools/canonical_manifest.py" validate "${freeze_dir}"
python3 -c '
import hashlib,json,pathlib,sys
manifest=pathlib.Path(sys.argv[1])
production=pathlib.Path(sys.argv[2])
for line in manifest.read_text().splitlines():
    if not line.strip():
        continue
    row=json.loads(line)
    path=production / row["raw_path"]
    value=hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(16*1024*1024), b""):
            value.update(chunk)
    if value.hexdigest() != row["raw_sha256"]:
        raise SystemExit("checksum mismatch: %s" % path)
print("CANONICAL_SHA256_VALID files=300")
' "${freeze_dir}/canonical_manifest.jsonl" "${production_root}"

mkdir -p "$(dirname "${log_path}")"
status=0
root -l -b -q \
  "${script_dir}/ValidateCanonicalRawManifest.C(\"${freeze_dir}/canonical_manifest.jsonl\",\"${production_root}\")" \
  >"${log_path}" 2>&1 || status=$?
cat "${log_path}"
if (( status != 0 )) ||
   ! grep -q 'CANONICAL_RAW_VALIDATION errors=0 files=300' "${log_path}"; then
  exit 1
fi
