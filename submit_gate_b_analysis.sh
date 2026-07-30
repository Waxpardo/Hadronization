#!/bin/bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  ./submit_gate_b_analysis.sh CAMPAIGN_DIR PRODUCTION_ROOT ANALYSIS_ROOT --dry-run
  ./submit_gate_b_analysis.sh CAMPAIGN_DIR PRODUCTION_ROOT ANALYSIS_ROOT --submit

Validate and queue exactly the nine raw files declared by a Gate-B pilot
manifest. Append --scope=central or --scope=sensitivity to validate and queue
only that declared subset while the other jobs are still running. Directory
discovery and retry are forbidden. Every job is pinned to the tracked-clean
analysis commit, analysis-macro SHA-256, and manifest raw-file SHA-256; the
Condor jobs do not inherit the submitter's environment.
USAGE
}

if [[ ("$#" -ne 4 && "$#" -ne 5) ||
      "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 2
fi
campaign_dir="$(cd "$1" && pwd)"
production_root="$(cd "$2" && pwd)"
analysis_root="$3"
mode="$4"
scope="all"
case "${5:-}" in
  "") ;;
  --scope=central) scope="central" ;;
  --scope=sensitivity) scope="sensitivity" ;;
  *) usage; exit 2 ;;
esac
case "${mode}" in
  --dry-run|--submit) ;;
  *) usage; exit 2 ;;
esac

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_base="${HADRONIZATION_BASE:-${script_dir}}"
project_base="${project_base%/}"
export HADRONIZATION_BASE="${project_base}"
if [[ -n "$(git -C "${project_base}" status --porcelain --untracked-files=no)" ]]; then
  echo "ERROR: Gate-B analysis requires no tracked worktree changes" >&2
  exit 3
fi
python3 "${project_base}/tools/campaign_manifest.py" validate \
  "${campaign_dir}" --implementation-policy ancestor \
  --checkout-root "${project_base}"
submission_claim="${production_root}/submission_receipts/gate_b_attempt0_submission_claim.json"
submission_record="${production_root}/submission_receipts/gate_b_attempt0_submitted.json"
producer_executable_sha256="$(
  python3 - "${campaign_dir}" "${submission_claim}" "${submission_record}" <<'PY'
import hashlib
import json
import re
import sys
from pathlib import Path

campaign_dir, claim_path, record_path = map(Path, sys.argv[1:])
config = json.loads((campaign_dir / "campaign.json").read_text())
rows = [
    json.loads(line)
    for line in (campaign_dir / "candidate_manifest.jsonl").read_text().splitlines()
    if line.strip()
]
if not claim_path.is_file() or not record_path.is_file():
    raise ValueError("Gate-B production submission claim/record is absent")
claim = json.loads(claim_path.read_text())
record = json.loads(record_path.read_text())
sha256 = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
expected_claim = {
    "schema": "hf_gate_b_submission_claim_v1",
    "state": "claimed_before_condor_submit",
    "campaign": config["campaign"],
    "campaign_ordinal": config["campaign_ordinal"],
    "repository_commit": config["repository_implementation_commit"],
    "campaign_json_sha256": sha256(campaign_dir / "campaign.json"),
    "candidate_manifest_sha256": sha256(
        campaign_dir / "candidate_manifest.jsonl"
    ),
    "seed_ledger_sha256": sha256(campaign_dir / "seed_ledger.jsonl"),
}
for key, expected in expected_claim.items():
    if claim.get(key) != expected:
        raise ValueError(f"Gate-B production claim {key} differs")
production_root = claim_path.parents[1]
submit_file = production_root / "submit_gate_b.sub"
if (
    not submit_file.is_file()
    or claim.get("submit_file_sha256") != sha256(submit_file)
):
    raise ValueError("Gate-B production claim submit-file checksum differs")
expected_allocations = [
    {
        "tune": row["tune"],
        "logical_id": int(row["logical_id"]),
        "attempt": int(row["attempt"]),
        "seed": int(row["seed"]),
        "campaign_ordinal": int(row["campaign_ordinal"]),
        "pthat_min_override": str(row["pthat_min_override"]),
        "multiplicity_audit_events": int(row["multiplicity_audit_events"]),
        "repository_commit": row["repository_commit"],
        "effective_card_sha256": row["effective_card_sha256"],
    }
    for row in rows
]
key = lambda row: (row["tune"], row["logical_id"], row["attempt"], row["seed"])
if sorted(claim.get("allocations", []), key=key) != sorted(
    expected_allocations, key=key
):
    raise ValueError("Gate-B production claim allocations differ from manifest")
expected_record = {
    "schema": "hf_gate_b_submission_record_v1",
    "state": "condor_submit_succeeded",
    "claim_sha256": sha256(claim_path),
    "campaign": config["campaign"],
    "campaign_ordinal": config["campaign_ordinal"],
}
for key_name, expected in expected_record.items():
    if record.get(key_name) != expected:
        raise ValueError(f"Gate-B production record {key_name} differs")
producer_sha = claim.get("producer_executable_sha256")
if not isinstance(producer_sha, str) or not re.fullmatch(
    r"[0-9a-f]{64}", producer_sha
):
    raise ValueError("Gate-B production claim has invalid producer checksum")
print(producer_sha)
PY
)"
source "${project_base}/setupEnv.sh"

mkdir -p "${analysis_root}/validation/raw" \
  "${analysis_root}/condor_logs"/{MONASH,JUNCTIONS,CLOSEPACKING}
analysis_root="$(cd "${analysis_root}" && pwd)"
while IFS=$'\t' read -r tune logical_id successes attempt seed stable_name \
  role campaign_ordinal pthat_min audit_events effective_card_sha256 \
  repository_commit; do
  raw="${production_root}/raw/${tune}/${stable_name}"
  log="${analysis_root}/validation/raw/${tune}_job$(printf '%03d' "${logical_id}").log"
  if [[ ! -f "${raw}" ]]; then
    echo "ERROR: missing manifest-declared Gate-B raw file: ${raw}" >&2
    exit 4
  fi
  if [[ ! -f "${raw}.sha256" ]] ||
     ! (cd "$(dirname "${raw}")" && sha256sum -c "$(basename "${raw}.sha256")") \
       >>"${log}" 2>&1; then
    echo "ERROR: Gate-B raw checksum verification failed: ${raw}" >&2
    exit 4
  fi
  "${project_base}/Validation/validate_raw_output.sh" \
    "${raw}" \
    "$(basename "${campaign_dir}")" \
    "${tune}" "${logical_id}" "${successes}" "${attempt}" "${seed}" \
    "${role}" "${campaign_ordinal}" "${pthat_min}" "${audit_events}" \
    "${effective_card_sha256}" "${producer_executable_sha256}" \
    "${repository_commit}" \
    >"${log}" 2>&1
  if ! grep -q 'RAW_VALIDATION_SUMMARY errors=0' "${log}"; then
    echo "ERROR: Gate-B raw validation did not pass: ${log}" >&2
    exit 5
  fi
done < <(
  python3 - "${campaign_dir}/candidate_manifest.jsonl" "${scope}" <<'PY'
import json
import sys
for line in open(sys.argv[1]):
    row = json.loads(line)
    if sys.argv[2] == "central" and row["purpose"] != "one_million_central":
        continue
    if sys.argv[2] == "sensitivity" and row["purpose"] == "one_million_central":
        continue
    print(
        row["tune"],
        row["logical_id"],
        row["requested_successes"],
        row["attempt"],
        row["seed"],
        row["stable_name"],
        row["role"],
        row["campaign_ordinal"],
        row["pthat_min_override"],
        row["multiplicity_audit_events"],
        row["effective_card_sha256"],
        row["repository_commit"],
        sep="\t",
    )
PY
)

submit_file="${analysis_root}/submit_gate_b_analysis_${scope}.sub"
python3 "${project_base}/tools/render_gate_b_analysis_submit.py" \
  "${campaign_dir}" "${project_base}" "${production_root}" \
  "${analysis_root}" "${submit_file}" --scope "${scope}"
if [[ "${mode}" == "--dry-run" ]]; then
  echo "GATE_B_ANALYSIS_DRY_RUN_OK scope=${scope} submit_file=${submit_file}"
  exit 0
fi
condor_submit "${submit_file}"
