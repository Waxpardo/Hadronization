#!/usr/bin/env python3
"""Exhaustively validate manifest-bound Gate-B analysis outputs."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path


TUNES = ("MONASH", "JUNCTIONS", "CLOSEPACKING")
SELECTOR = "hard_trigger_primary_ground__primary_ground_associate_v1"
RAW_SCHEMA = "hf_primary_ground_raw_v7"
ORIGIN_ALGORITHM = "signed_heavy_constituent_complete_mothers_unique_v4"
ANALYSIS_JOB_SCHEMA = "hf_analysis_job_metadata_v3"
ANALYSIS_SCHEMA = "paul_pair_objects_primary_ground_v2"
ANALYSIS_IMPLEMENTATION = "one_pass_primary_ground_pair_analysis_v2"
ANALYSIS_VERSION = "status_analysis_THnSparse_qq_v2"
ANALYSIS_PROFILE = "central_primary_ground_v1"
PAIR_COMBINATORICS_MODE = "ordered_conditional_v1"
GATE_B_PROFILES = {
    0: ("one_million_central", "hf_{tune}_job000.root"),
    1: ("pthat_sensitivity_low", "hf_{tune}_job001.root"),
    2: ("pthat_sensitivity_high", "hf_{tune}_job002.root"),
}
HEX40 = re.compile(r"[0-9a-f]{40}")
HEX64 = re.compile(r"[0-9a-f]{64}")
SAFE_TOKEN = re.compile(r"[A-Za-z0-9._-]+")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text().splitlines()
        if line.strip()
    ]


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def require_commit(checkout: Path, commit: str, label: str) -> None:
    if not HEX40.fullmatch(commit):
        raise ValueError(f"invalid {label} commit: {commit!r}")
    result = subprocess.run(
        ["git", "-C", str(checkout), "cat-file", "-e", f"{commit}^{{commit}}"],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if result.returncode != 0:
        raise ValueError(f"{label} commit is absent from checkout: {commit}")


def require_ancestor(checkout: Path, ancestor: str, descendant: str) -> None:
    result = subprocess.run(
        [
            "git",
            "-C",
            str(checkout),
            "merge-base",
            "--is-ancestor",
            ancestor,
            descendant,
        ],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if result.returncode != 0:
        raise ValueError(
            f"production commit {ancestor} is not an ancestor of "
            f"analysis commit {descendant}"
        )


def validate_production_receipt(
    campaign_dir: Path, production: Path, config: dict, rows: list[dict]
) -> str:
    claim_path = (
        production
        / "submission_receipts"
        / "gate_b_attempt0_submission_claim.json"
    )
    record_path = (
        production
        / "submission_receipts"
        / "gate_b_attempt0_submitted.json"
    )
    if not claim_path.is_file() or not record_path.is_file():
        raise FileNotFoundError("Gate-B production submission receipt is absent")
    claim = json.loads(claim_path.read_text())
    record = json.loads(record_path.read_text())
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
    for key, expected_value in expected_claim.items():
        if claim.get(key) != expected_value:
            raise ValueError(f"Gate-B production claim {key} differs")
    submit_file = production / "submit_gate_b.sub"
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
    allocation_key = lambda row: (
        row["tune"],
        int(row["logical_id"]),
        int(row["attempt"]),
        int(row["seed"]),
    )
    if sorted(claim.get("allocations", []), key=allocation_key) != sorted(
        expected_allocations, key=allocation_key
    ):
        raise ValueError("Gate-B production claim allocations differ")
    expected_record = {
        "schema": "hf_gate_b_submission_record_v1",
        "state": "condor_submit_succeeded",
        "claim_sha256": sha256(claim_path),
        "campaign": config["campaign"],
        "campaign_ordinal": config["campaign_ordinal"],
    }
    for key, expected_value in expected_record.items():
        if record.get(key) != expected_value:
            raise ValueError(f"Gate-B production record {key} differs")
    producer_sha = claim.get("producer_executable_sha256")
    if not isinstance(producer_sha, str) or not HEX64.fullmatch(producer_sha):
        raise ValueError("Gate-B production claim producer checksum is invalid")
    return producer_sha


def parse_pair_summary(output: str, directory: Path) -> dict[str, str]:
    lines = [
        line
        for line in output.splitlines()
        if line.startswith("PAIR_DIRECTORY_VALIDATION ")
    ]
    if len(lines) != 1 or "errors=0" not in lines[0]:
        raise ValueError(f"pair validator did not certify {directory}")
    fields = {}
    for token in lines[0].split()[1:]:
        if "=" in token:
            key, value = token.split("=", 1)
            fields[key] = value
    return fields


def validate_raw_file(
    checkout: Path,
    raw: Path,
    row: dict,
    config: dict,
    producer_sha256: str,
) -> None:
    environment = os.environ.copy()
    environment["HADRONIZATION_BASE"] = str(checkout)
    result = subprocess.run(
        [
            str(checkout / "Validation/validate_raw_output.sh"),
            str(raw),
            config["campaign"],
            row["tune"],
            str(int(row["logical_id"])),
            str(int(row["requested_successes"])),
            str(int(row["attempt"])),
            str(int(row["seed"])),
            row["role"],
            str(int(row["campaign_ordinal"])),
            str(row["pthat_min_override"]),
            str(int(row["multiplicity_audit_events"])),
            row["effective_card_sha256"],
            producer_sha256,
            row["repository_commit"],
        ],
        check=False,
        text=True,
        capture_output=True,
        env=environment,
    )
    combined = result.stdout + result.stderr
    if result.returncode != 0 or "RAW_VALIDATION_SUMMARY errors=0 " not in combined:
        diagnostic = "\n".join(combined.splitlines()[-30:])
        raise ValueError(
            f"raw validation failed for {raw}:\n{diagnostic}"
        )


def validate_pair_directory(
    checkout: Path,
    directory: Path,
    metadata: dict,
    production_commit: str,
    producer_sha256: str,
    tune_allowlist_sha256: str,
) -> dict[str, str]:
    environment = os.environ.copy()
    environment["HADRONIZATION_BASE"] = str(checkout)
    environment["HADRONIZATION_ANALYSIS_COMMIT"] = metadata["repository_commit"]
    environment["HADRONIZATION_ANALYSIS_MACRO_SHA256"] = metadata[
        "analysis_macro_sha256"
    ]
    environment["HADRONIZATION_EXPECTED_RAW_SHA256"] = metadata["raw_sha256"]
    environment["HADRONIZATION_EXPECTED_CAMPAIGN"] = metadata["campaign"]
    environment["HADRONIZATION_EXPECTED_TUNE"] = metadata["tune"]
    result = subprocess.run(
        [str(checkout / "Validation/validate_pair_directory.sh"), str(directory)],
        check=False,
        text=True,
        capture_output=True,
        env=environment,
    )
    if result.returncode != 0:
        diagnostic = "\n".join((result.stdout + result.stderr).splitlines()[-30:])
        raise ValueError(
            f"pair-directory validation failed for {directory}:\n{diagnostic}"
        )
    fields = parse_pair_summary(result.stdout + result.stderr, directory)
    expected = {
        "expected_files": "300",
        "found_root_files": "300",
        "analysis_commit": metadata["repository_commit"],
        "analysis_macro_sha256": metadata["analysis_macro_sha256"],
        "raw_campaign": metadata["campaign"],
        "raw_tune": metadata["tune"],
        "upstream_raw_sha256": metadata["raw_sha256"],
        "upstream_commit": production_commit,
        "upstream_executable_sha256": producer_sha256,
        "upstream_tune_allowlist_sha256": tune_allowlist_sha256,
        "pair_combinatorics_mode": PAIR_COMBINATORICS_MODE,
        "same_sign_pair_factor": "1",
    }
    for key, value in expected.items():
        if fields.get(key) != value:
            raise ValueError(
                f"pair provenance mismatch for {directory}: "
                f"{key}={fields.get(key)!r}, expected {value!r}"
            )
    return fields


def selected_rows(rows: list[dict], scope: str) -> list[dict]:
    if scope == "central":
        return [row for row in rows if row["purpose"] == "one_million_central"]
    if scope == "sensitivity":
        return [row for row in rows if row["purpose"] != "one_million_central"]
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("campaign_dir", type=Path)
    parser.add_argument("production_root", type=Path)
    parser.add_argument("analysis_root", type=Path)
    parser.add_argument(
        "--scope",
        choices=("all", "central", "sensitivity"),
        default="all",
        help=(
            "validate all nine jobs for final PASS, or a declared subset for "
            "INTERIM_PASS"
        ),
    )
    parser.add_argument(
        "--checkout-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="write the atomic JSON validation report, including pair checksums",
    )
    parser.add_argument(
        "--checksum-inventory",
        type=Path,
        help="also write the pair-file SHA-256 inventory as JSON Lines",
    )
    args = parser.parse_args()
    campaign_dir = args.campaign_dir.resolve()
    production = args.production_root.resolve()
    analysis = args.analysis_root.resolve()
    checkout = args.checkout_root.resolve()
    config = json.loads((campaign_dir / "campaign.json").read_text())
    rows = load_jsonl(campaign_dir / "candidate_manifest.jsonl")
    if (
        config.get("schema") != "hf_gate_b_pilot_campaign_v1"
        or config.get("raw_schema") != RAW_SCHEMA
        or config.get("origin_algorithm") != ORIGIN_ALGORITHM
        or config.get("selector") != SELECTOR
        or len(rows) != 9
    ):
        raise ValueError("expected an exact nine-row Gate-B v4 campaign")
    if (
        not isinstance(config.get("campaign"), str)
        or not SAFE_TOKEN.fullmatch(config["campaign"])
        or campaign_dir.name != config["campaign"]
    ):
        raise ValueError("campaign name and campaign-directory basename differ")
    identities = {
        (row.get("tune"), int(row.get("logical_id", -1))) for row in rows
    }
    expected_identities = {
        (tune, logical_id)
        for tune in TUNES
        for logical_id in (0, 1, 2)
    }
    if identities != expected_identities:
        raise ValueError("Gate-B candidate identities are incomplete or duplicated")
    for row in rows:
        logical_id = int(row["logical_id"])
        expected_purpose, stable_template = GATE_B_PROFILES[logical_id]
        expected_fields = {
            "campaign": config["campaign"],
            "purpose": expected_purpose,
            "stable_name": stable_template.format(tune=row["tune"]),
        }
        for key, expected_value in expected_fields.items():
            if row.get(key) != expected_value:
                raise ValueError(
                    f"Gate-B manifest identity mismatch "
                    f"{row['tune']}/{logical_id}: {key}"
                )
    if sha256(checkout / "config/heavy_flavour_pair_registry_v1.json") != config.get(
        "pair_registry_sha256"
    ):
        raise ValueError("campaign pair registry differs from validation checkout")
    pair_registry = json.loads(
        (checkout / "config/heavy_flavour_pair_registry_v1.json").read_text()
    )
    expected_filenames = {row["filename"] for row in pair_registry["pairs"]}
    if pair_registry.get("pair_count") != 300 or len(expected_filenames) != 300:
        raise ValueError("pair registry does not define 300 unique outputs")
    producer_sha256 = validate_production_receipt(
        campaign_dir, production, config, rows
    )

    selected = selected_rows(rows, args.scope)
    expected_selected = {"all": 9, "central": 3, "sensitivity": 6}[args.scope]
    if len(selected) != expected_selected:
        raise ValueError(
            f"Gate-B {args.scope} scope has {len(selected)} rows, "
            f"expected {expected_selected}"
        )
    all_directories = {
        (
            analysis
            / "per_pthat"
            / row["tune"]
            / f"job_{int(row['logical_id']):03d}"
        ).resolve()
        for row in rows
    }
    selected_directories = {
        (
            analysis
            / "per_pthat"
            / row["tune"]
            / f"job_{int(row['logical_id']):03d}"
        ).resolve()
        for row in selected
    }
    discovered_entries = {
        path.resolve()
        for tune in TUNES
        for path in (analysis / "per_pthat" / tune).glob("job_*")
        if path.is_dir()
    }
    discovered = {
        path
        for path in discovered_entries
        if re.fullmatch(r"job_[0-9]{3}", path.name)
    }
    staging = {
        path
        for path in discovered_entries
        if re.fullmatch(r"job_[0-9]{3}\.partial\.[A-Za-z0-9]+", path.name)
    }
    unknown = sorted(
        str(path) for path in discovered_entries - discovered - staging
    )
    unknown.extend(
        sorted(str(path) for path in discovered - all_directories)
    )
    selected_staging = {
        path
        for path in staging
        if path.with_name(path.name.split(".partial.", 1)[0])
        in selected_directories
    }
    if args.scope == "all":
        selected_staging = staging
    out_of_scope_staging = (
        staging - selected_staging if args.scope != "all" else set()
    )
    unknown.extend(sorted(str(path) for path in selected_staging))
    missing = sorted(str(path) for path in selected_directories - discovered)
    if unknown or missing:
        raise ValueError(
            f"Gate-B analysis coverage mismatch unknown={unknown} missing={missing}"
        )

    production_commit = config.get("repository_implementation_commit")
    if not isinstance(production_commit, str):
        raise ValueError("campaign lacks production implementation commit")
    require_commit(checkout, production_commit, "production")
    validated = []
    checksums = []
    analysis_commits: set[str] = set()
    macro_hashes: set[str] = set()
    stability_hashes: set[str] = set()
    for row in selected:
        tune = row["tune"]
        logical_id = int(row["logical_id"])
        raw = production / "raw" / tune / row["stable_name"]
        directory = analysis / "per_pthat" / tune / f"job_{logical_id:03d}"
        metadata_path = directory / "analysis_job_metadata.json"
        if not raw.is_file() or not metadata_path.is_file():
            raise FileNotFoundError(f"missing raw or analysis metadata for {directory}")
        raw_sha256 = sha256(raw)
        sidecar = Path(f"{raw}.sha256")
        sidecar_fields = sidecar.read_text().split() if sidecar.is_file() else []
        if (
            len(sidecar_fields) != 2
            or sidecar_fields[0] != raw_sha256
            or Path(sidecar_fields[1]).name != raw.name
        ):
            raise ValueError(f"raw checksum sidecar mismatch for {raw}")
        validate_raw_file(
            checkout, raw, row, config, producer_sha256
        )
        metadata = json.loads(metadata_path.read_text())
        exact_metadata = {
            "schema": ANALYSIS_JOB_SCHEMA,
            "analysis_schema": ANALYSIS_SCHEMA,
            "analysis_implementation": ANALYSIS_IMPLEMENTATION,
            "analysis_version": ANALYSIS_VERSION,
            "analysis_profile": ANALYSIS_PROFILE,
            "pair_combinatorics_mode": PAIR_COMBINATORICS_MODE,
            "event_filter_schema": "all_events_v1",
            "event_filter_modulo": 0,
            "event_filter_remainder": -1,
            "same_sign_pair_factor": 1.0,
            "raw_sha256": raw_sha256,
            "raw_schema": RAW_SCHEMA,
            "raw_input_validation_contract":
                "analysis_raw_input_fail_closed_v1",
            "raw_validation_evidence_mode":
                "direct_preflight_only_v1",
            "raw_validation_receipt": None,
            "raw_validation_receipt_schema": None,
            "raw_validation_receipt_sha256": None,
            "origin_algorithm": ORIGIN_ALGORITHM,
            "selector": SELECTOR,
            "repository_dirty": False,
            "campaign": config["campaign"],
            "tune": tune,
            "logical_id": logical_id,
            "purpose": row["purpose"],
        }
        for key, expected_value in exact_metadata.items():
            if metadata.get(key) != expected_value:
                raise ValueError(
                    f"analysis metadata mismatch for {directory}: "
                    f"{key}={metadata.get(key)!r}, expected {expected_value!r}"
                )
        if Path(metadata.get("raw_input", "")).name != row["stable_name"]:
            raise ValueError(f"raw stable-name mismatch for {directory}")
        commit = metadata.get("repository_commit")
        macro_hash = metadata.get("analysis_macro_sha256")
        if not isinstance(commit, str) or not HEX40.fullmatch(commit):
            raise ValueError(f"invalid analysis commit for {directory}")
        if not isinstance(macro_hash, str) or not HEX64.fullmatch(macro_hash):
            raise ValueError(f"invalid analysis macro checksum for {directory}")
        require_commit(checkout, commit, "analysis")
        require_ancestor(checkout, production_commit, commit)
        committed_macro = subprocess.check_output(
            [
                "git",
                "-C",
                str(checkout),
                "show",
                f"{commit}:AnalysisScripts/status_analysis_THnSparse_qq.C",
            ]
        )
        if hashlib.sha256(committed_macro).hexdigest() != macro_hash:
            raise ValueError(
                f"analysis macro is not the version committed at {commit}"
            )
        analysis_commits.add(commit)
        macro_hashes.add(macro_hash)

        root_files = {
            path.name: path for path in directory.glob("*.root") if path.is_file()
        }
        if set(root_files) != expected_filenames:
            raise ValueError(
                f"pair-file set mismatch for {directory}: "
                f"missing={sorted(expected_filenames - set(root_files))} "
                f"extra={sorted(set(root_files) - expected_filenames)}"
            )
        pair_provenance = validate_pair_directory(
            checkout,
            directory,
            metadata,
            production_commit,
            producer_sha256,
            config["tune_allowlist_sha256"],
        )
        stability_hashes.add(pair_provenance["upstream_stability_sha256"])
        for filename in sorted(expected_filenames):
            path = root_files[filename]
            checksums.append(
                {
                    "tune": tune,
                    "logical_id": logical_id,
                    "purpose": row["purpose"],
                    "path": str(path.relative_to(analysis)),
                    "bytes": path.stat().st_size,
                    "sha256": sha256(path),
                }
            )
        validated.append(
            {
                "tune": tune,
                "logical_id": logical_id,
                "purpose": row["purpose"],
                "raw_path": str(raw),
                "raw_sha256": raw_sha256,
                "analysis_commit": commit,
                "analysis_macro_sha256": macro_hash,
                "upstream_heavy_stability_audit_sha256":
                    pair_provenance["upstream_stability_sha256"],
                "upstream_effective_settings_sha256":
                    pair_provenance["upstream_settings_sha256"],
                "pair_files": len(root_files),
            }
        )

    if (
        len(analysis_commits) != 1
        or len(macro_hashes) != 1
        or len(stability_hashes) != 1
    ):
        raise ValueError(
            f"mixed analysis implementation commits={sorted(analysis_commits)} "
            f"macro_hashes={sorted(macro_hashes)} "
            f"stability_hashes={sorted(stability_hashes)}"
        )
    expected_checksums = expected_selected * 300
    if len(checksums) != expected_checksums:
        raise AssertionError(
            f"checksum inventory has {len(checksums)} rows, "
            f"expected {expected_checksums}"
        )
    status = "PASS" if args.scope == "all" else "INTERIM_PASS"
    report = {
        "schema": "hf_gate_b_analysis_validation_v2",
        "campaign": config["campaign"],
        "scope": args.scope,
        "status": status,
        "production_implementation_commit": production_commit,
        "production_executable_sha256": producer_sha256,
        "analysis_commit": next(iter(analysis_commits)),
        "analysis_macro_sha256": next(iter(macro_hashes)),
        "heavy_stability_audit_sha256": next(iter(stability_hashes)),
        "pair_combinatorics_mode": PAIR_COMBINATORICS_MODE,
        "same_sign_pair_factor": 1.0,
        "validated_directory_count": len(validated),
        "expected_final_directory_count": 9,
        "pair_checksum_count": len(checksums),
        "expected_final_pair_checksum_count": 2700,
        "out_of_scope_staging_directories": (
            sorted(
                str(path.relative_to(analysis))
                for path in out_of_scope_staging
            )
        ),
        "validated_outputs": validated,
        "pair_file_checksums": checksums,
    }
    if args.report:
        atomic_write(
            args.report.resolve(),
            json.dumps(report, indent=2, sort_keys=True) + "\n",
        )
    if args.checksum_inventory:
        atomic_write(
            args.checksum_inventory.resolve(),
            "".join(json.dumps(row, sort_keys=True) + "\n" for row in checksums),
        )
    label = (
        "GATE_B_ANALYSIS_OUTPUTS_VALID"
        if status == "PASS"
        else "GATE_B_ANALYSIS_OUTPUTS_INTERIM_VALID"
    )
    print(
        f"{label} scope={args.scope} directories={len(validated)} "
        f"pair_checksums={len(checksums)} "
        f"commit={next(iter(analysis_commits))}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
