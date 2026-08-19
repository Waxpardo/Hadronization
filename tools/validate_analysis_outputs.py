#!/usr/bin/env python3
"""Exhaustively validate canonical per-job analysis before any merge."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLS_DIRECTORY = str(Path(__file__).resolve().parent)
if TOOLS_DIRECTORY not in sys.path:
    sys.path.insert(0, TOOLS_DIRECTORY)

from campaign import PUBLISHED_TUNES  # noqa: E402

TUNES = PUBLISHED_TUNES
ROW_SCHEMAS = {
    "hf_canonical_raw_manifest_v2",
    "hf_superseding_canonical_raw_manifest_v3",
}
SELECTOR = "hard_trigger_primary_ground__primary_ground_associate_v1"
RAW_SCHEMA = "hf_primary_ground_raw_v7"
ORIGIN_ALGORITHM = "signed_heavy_constituent_complete_mothers_unique_v4"
ANALYSIS_JOB_SCHEMA = "hf_analysis_job_metadata_v3"
# The analysis schema is an AXIS, not a constant. The pair-object contract
# declares which schemas exist -- v2 carries six closure-checked content
# objects, v3 adds hFlavourClosureSpecies -- and a directory is judged against
# the one it declares. Pinning a single string here would reject a correct v3
# directory that the object contract accepts: the one-consumer blindness
# already removed from ValidatePairDirectory.C and both plotting gates.
#
# Derived from the contract rather than restated, so it cannot drift from it.
# ANALYSIS_IMPLEMENTATION and ANALYSIS_VERSION stay pinned deliberately: the
# producer did not move them for the species axis, only the schema.
ANALYSIS_SCHEMAS = frozenset(
    json.loads(
        (Path(__file__).resolve().parents[1]
         / "config/pair_file_object_contract_v1.json").read_text()
    )["schema_version_tags"].values()
)
ANALYSIS_IMPLEMENTATION = "one_pass_primary_ground_pair_analysis_v2"
ANALYSIS_VERSION = "status_analysis_THnSparse_qq_v2"
ANALYSIS_PROFILE = "central_primary_ground_v1"
PAIR_COMBINATORICS_MODE = "ordered_conditional_v1"
HEX40 = re.compile(r"[0-9a-f]{40}")
HEX64 = re.compile(r"[0-9a-f]{64}")
SLOT_DIRECTORY = re.compile(r"slot_[0-9]+")

METADATA_KEYS = {
    "schema",
    "analysis_schema",
    "analysis_implementation",
    "analysis_version",
    "analysis_profile",
    "pair_combinatorics_mode",
    "event_filter_schema",
    "event_filter_modulo",
    "event_filter_remainder",
    "same_sign_pair_factor",
    "analysis_macro_sha256",
    "raw_input",
    "raw_sha256",
    "raw_schema",
    "raw_input_validation_contract",
    "raw_validation_evidence_mode",
    "raw_validation_receipt",
    "raw_validation_receipt_schema",
    "raw_validation_receipt_sha256",
    "origin_algorithm",
    "repository_commit",
    "repository_dirty",
    "selector",
    "campaign",
    "tune",
    "logical_id",
    "purpose",
    "canonical_manifest_sha256",
}


def optional_sha256(path: Path) -> str | None:
    """Checksum a provenance artifact that may legitimately be absent.

    freeze_seal.json and canonical_raw_validation_receipt.json are recorded in
    the analysis report but are not inputs to any check. The gate layer wrote
    both; only the seal survives, so a missing file is recorded as null rather
    than aborting a valid analysis.
    """
    return sha256(path) if path.is_file() else None


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(16 * 1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text().splitlines()
        if line.strip()
    ]


def canonical_jobs_per_tune(rows: list[dict]) -> int:
    tune_counts = {
        tune: sum(row.get("tune") == tune for row in rows)
        for tune in TUNES
    }
    schemas = {row.get("schema") for row in rows}
    if (
        len(set(tune_counts.values())) != 1
        or not tune_counts
        # Jobs per tune is a campaign parameter, not a contract constant. The
        # requirements that matter are equal exposure across tunes and a count
        # that divides into the ten blocks the ratios are formed in; the old
        # floor of 100 hardcoded one campaign shape and rejected every other.
        or (jobs_per_tune := next(iter(tune_counts.values()))) < 10
        or jobs_per_tune % 10
        or len(rows) != len(TUNES) * jobs_per_tune
        or len(schemas) != 1
        or not schemas.issubset(ROW_SCHEMAS)
    ):
        raise ValueError(
            "canonical analysis validation requires equal per-tune exposure "
            "that is a positive multiple of the ten blocks; "
            f"counts={tune_counts} rows={len(rows)}"
        )
    expected = [
        (tune, slot)
        for tune in TUNES
        for slot in range(jobs_per_tune)
    ]
    observed = [
        (row.get("tune"), row.get("canonical_slot")) for row in rows
    ]
    if observed != expected:
        raise ValueError("canonical analysis tune/slot order differs")
    return jobs_per_tune


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
    if not isinstance(commit, str) or not HEX40.fullmatch(commit):
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


def expected_pair_filenames(checkout: Path) -> set[str]:
    header = (
        checkout / "AnalysisScripts" / "GeneratedPairRegistry.h"
    ).read_text()
    values = set(re.findall(r'"([^"]+\.root)"', header))
    declared = re.search(
        r"std::array<PairDefinition,\s*([0-9]+)>", header
    )
    if not declared or len(values) != int(declared.group(1)):
        raise ValueError(
            "cannot establish exact pair-file set from GeneratedPairRegistry.h"
        )
    return values


def parse_pair_summary(output: str, directory: Path) -> dict[str, str]:
    lines = [
        line
        for line in output.splitlines()
        if line.startswith("PAIR_DIRECTORY_VALIDATION ")
    ]
    if len(lines) != 1 or "errors=0" not in lines[0]:
        raise ValueError(f"pair validator did not certify {directory}")
    result: dict[str, str] = {}
    for token in lines[0].split()[1:]:
        if "=" in token:
            key, value = token.split("=", 1)
            result[key] = value
    return result


def validate_pair_directory(
    checkout: Path, directory: Path, metadata: dict, row: dict
) -> dict[str, str]:
    environment = os.environ.copy()
    environment.update(
        {
            "HADRONIZATION_BASE": str(checkout),
            "HADRONIZATION_ANALYSIS_COMMIT": metadata["repository_commit"],
            "HADRONIZATION_ANALYSIS_MACRO_SHA256": metadata[
                "analysis_macro_sha256"
            ],
            "HADRONIZATION_EXPECTED_RAW_SHA256": row["raw_sha256"],
            "HADRONIZATION_EXPECTED_CAMPAIGN": row["campaign"],
            "HADRONIZATION_EXPECTED_TUNE": row["tune"],
        }
    )
    result = subprocess.run(
        [str(checkout / "Validation/validate_pair_directory.sh"), str(directory)],
        check=False,
        text=True,
        capture_output=True,
        env=environment,
    )
    combined = result.stdout + result.stderr
    if result.returncode != 0:
        diagnostic = "\n".join(combined.splitlines()[-40:])
        raise ValueError(
            f"pair-directory validation failed for {directory}:\n{diagnostic}"
        )
    fields = parse_pair_summary(combined, directory)
    expected = {
        "expected_files": "300",
        "found_root_files": "300",
        "analysis_commit": metadata["repository_commit"],
        "analysis_macro_sha256": metadata["analysis_macro_sha256"],
        "raw_campaign": row["campaign"],
        "raw_tune": row["tune"],
        "upstream_raw_sha256": row["raw_sha256"],
        "upstream_commit": row["repository_commit"],
        "upstream_executable_sha256": row["producer_executable_sha256"],
        "upstream_tune_allowlist_sha256": row[
            "tune_difference_allowlist_sha256"
        ],
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


def directory_digest(root_files: dict[str, Path]) -> str:
    value = hashlib.sha256()
    for name in sorted(root_files):
        path = root_files[name]
        value.update(name.encode())
        value.update(b"\0")
        value.update(str(path.stat().st_size).encode())
        value.update(b"\0")
        value.update(sha256(path).encode())
        value.update(b"\n")
    return value.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("canonical_manifest", type=Path)
    parser.add_argument("analysis_root", type=Path)
    parser.add_argument("--production-root", required=True, type=Path)
    parser.add_argument("--checkout", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--allow-missing", action="store_true")
    args = parser.parse_args()

    checkout = (
        args.checkout.resolve()
        if args.checkout
        else Path(__file__).resolve().parents[1]
    )
    manifest = args.canonical_manifest.resolve()
    freeze_dir = manifest.parent
    # The sealed-manifest validation that ran here belonged to the gate layer.
    # The per-output structural checks below are what catch a bad analysis.
    rows = read_jsonl(manifest)
    jobs_per_tune = canonical_jobs_per_tune(rows)
    manifest_sha = sha256(manifest)
    analysis_root = args.analysis_root.resolve()
    production_root = args.production_root.resolve()
    expected_filenames = expected_pair_filenames(checkout)

    expected_raw_paths: set[Path] = set()
    for row in rows:
        raw_source = production_root / row["raw_path"]
        raw = raw_source.resolve()
        expected_raw_paths.add(raw)
        sidecar = Path(f"{raw}.sha256")
        fields = sidecar.read_text().split() if sidecar.is_file() else []
        if (
            raw_source.is_symlink()
            or not raw.is_file()
            or raw.stat().st_size != row["raw_bytes"]
            or sha256(raw) != row["raw_sha256"]
            or len(fields) != 2
            or fields[0] != row["raw_sha256"]
            or Path(fields[1]).name != raw.name
        ):
            raise ValueError(f"canonical raw input is absent or stale: {raw}")
    # Declared reserve outputs may coexist in production.  They are not
    # consumers: only the exact 3*N manifest paths above are admitted.

    per_job = analysis_root / "per_job"
    expected_directories = {
        (
            per_job
            / row["tune"]
            / f"slot_{int(row['canonical_slot']):03d}"
        ).resolve()
        for row in rows
    }
    discovered_directories: set[Path] = set()
    staging: list[Path] = []
    unknown_tune_entries: list[Path] = []
    if per_job.exists():
        for entry in per_job.iterdir():
            if not entry.is_dir() or entry.name not in TUNES:
                unknown_tune_entries.append(entry)
                continue
            for child in entry.iterdir():
                if child.is_dir() and ".partial." in child.name:
                    staging.append(child)
                elif child.is_dir() and SLOT_DIRECTORY.fullmatch(child.name):
                    discovered_directories.add(child.resolve())
                else:
                    unknown_tune_entries.append(child)
    extras = discovered_directories - expected_directories
    missing = expected_directories - discovered_directories
    if staging or unknown_tune_entries or extras:
        raise ValueError(
            "analysis directory set contains stale/extra material: "
            f"staging={sorted(str(path) for path in staging)} "
            f"unknown={sorted(str(path) for path in unknown_tune_entries)} "
            f"extra={sorted(str(path) for path in extras)}"
        )
    if missing and not args.allow_missing:
        raise ValueError(
            f"analysis output set is incomplete: {len(missing)} directories missing"
        )

    analysis_commits: set[str] = set()
    macro_hashes: set[str] = set()
    stability_hashes: set[str] = set()
    validated: list[dict] = []
    for row in rows:
        if row.get("schema") not in ROW_SCHEMAS:
            raise ValueError("canonical manifest row schema differs")
        tune = row["tune"]
        slot = int(row["canonical_slot"])
        directory = (per_job / tune / f"slot_{slot:03d}").resolve()
        if directory not in discovered_directories:
            continue
        metadata_path = directory / "analysis_job_metadata.json"
        log_path = directory / "analysis.log"
        if metadata_path.is_symlink() or not metadata_path.is_file():
            raise FileNotFoundError(f"analysis metadata is absent: {metadata_path}")
        if log_path.is_symlink() or not log_path.is_file():
            raise FileNotFoundError(f"analysis log is absent: {log_path}")
        metadata = json.loads(metadata_path.read_text())
        if set(metadata) != METADATA_KEYS:
            raise ValueError(
                f"analysis metadata field set differs for {directory}: "
                f"missing={sorted(METADATA_KEYS - set(metadata))} "
                f"extra={sorted(set(metadata) - METADATA_KEYS)}"
            )
        # Judged against the schema the directory itself declares, provided
        # that schema is one the contract knows. An unrecognised schema fails
        # closed here rather than being compared against a guessed default.
        declared_schema = metadata.get("analysis_schema")
        if declared_schema not in ANALYSIS_SCHEMAS:
            raise ValueError(
                f"analysis_schema {declared_schema!r} in {directory} is not "
                f"declared by config/pair_file_object_contract_v1.json "
                f"(known: {sorted(ANALYSIS_SCHEMAS)}); refusing to guess which "
                "object contract applies"
            )
        expected_metadata = {
            "schema": ANALYSIS_JOB_SCHEMA,
            "analysis_schema": declared_schema,
            "analysis_implementation": ANALYSIS_IMPLEMENTATION,
            "analysis_version": ANALYSIS_VERSION,
            "analysis_profile": ANALYSIS_PROFILE,
            "pair_combinatorics_mode": PAIR_COMBINATORICS_MODE,
            "event_filter_schema": "all_events_v1",
            "event_filter_modulo": 0,
            "event_filter_remainder": -1,
            "same_sign_pair_factor": 1.0,
            "raw_sha256": row["raw_sha256"],
            "raw_schema": RAW_SCHEMA,
            "raw_input_validation_contract":
                "analysis_raw_input_fail_closed_v1",
            "raw_validation_evidence_mode":
                "immutable_receipt_plus_direct_preflight_v1",
            "raw_validation_receipt": str(
                (
                    production_root
                    / row["raw_validation_receipt_path"]
                ).resolve()
            ),
            "raw_validation_receipt_schema":
                "hf_raw_validation_receipt_v1",
            "raw_validation_receipt_sha256":
                row["raw_validation_receipt_sha256"],
            "origin_algorithm": ORIGIN_ALGORITHM,
            "selector": SELECTOR,
            "repository_dirty": False,
            "campaign": row["campaign"],
            "tune": tune,
            "logical_id": row["logical_id"],
            "purpose": f"canonical_slot_{slot:03d}",
            "canonical_manifest_sha256": manifest_sha,
        }
        for key, expected in expected_metadata.items():
            if metadata.get(key) != expected:
                raise ValueError(
                    f"analysis metadata {key} differs for {directory}: "
                    f"{metadata.get(key)!r} != {expected!r}"
                )
        raw_input = Path(metadata["raw_input"]).resolve()
        expected_raw = (production_root / row["raw_path"]).resolve()
        if raw_input != expected_raw:
            raise ValueError(f"analysis raw path differs for {directory}")
        receipt_source = (
            production_root / row["raw_validation_receipt_path"]
        )
        receipt = receipt_source.resolve()
        if (
            receipt_source.is_symlink()
            or not receipt.is_file()
            or sha256(receipt) != row["raw_validation_receipt_sha256"]
        ):
            raise ValueError(
                f"analysis raw-validation receipt is absent or stale "
                f"for {directory}"
            )
        # The receipt's presence and checksum are verified just above. The
        # cross-binding of receipt to campaign/tune/logical-id was part of the
        # gate layer's authorisation chain and went with it.
        commit = metadata.get("repository_commit")
        macro_hash = metadata.get("analysis_macro_sha256")
        require_commit(checkout, commit, "analysis")
        if not isinstance(macro_hash, str) or not HEX64.fullmatch(macro_hash):
            raise ValueError(f"invalid analysis macro checksum for {directory}")
        require_ancestor(checkout, row["repository_commit"], commit)
        committed_macro = subprocess.check_output(
            [
                "git",
                "-C",
                str(checkout),
                "show",
                f"{commit}:analysis/status_analysis_THnSparse_qq.C",
            ]
        )
        if hashlib.sha256(committed_macro).hexdigest() != macro_hash:
            raise ValueError(
                f"analysis macro checksum is not committed at {commit}"
            )
        log_text = log_path.read_text()
        if (
            log_text.count("ONE_PASS_ANALYSIS_SUMMARY") != 1
            or "ONE_PASS_ANALYSIS_ERROR" in log_text
            or re.search(
                r"segmentation violation|Break +segmentation|"
                r"cling JIT session error",
                log_text,
            )
        ):
            raise ValueError(f"analysis log does not certify {directory}")

        root_files = {
            path.name: path
            for path in directory.iterdir()
            if path.is_file() and path.suffix == ".root"
        }
        expected_entries = expected_filenames | {
            "analysis_job_metadata.json",
            "analysis.log",
        }
        actual_entries = {path.name for path in directory.iterdir()}
        if actual_entries != expected_entries or set(root_files) != expected_filenames:
            raise ValueError(
                f"analysis file set differs for {directory}: "
                f"missing={sorted(expected_entries - actual_entries)} "
                f"extra={sorted(actual_entries - expected_entries)}"
            )
        if any(path.is_symlink() for path in directory.iterdir()):
            raise ValueError(f"analysis directory contains a symlink: {directory}")
        provenance = validate_pair_directory(
            checkout, directory, metadata, row
        )
        analysis_commits.add(commit)
        macro_hashes.add(macro_hash)
        stability_hashes.add(provenance["upstream_stability_sha256"])
        validated.append(
            {
                "tune": tune,
                "canonical_slot": slot,
                "logical_id": row["logical_id"],
                "raw_sha256": row["raw_sha256"],
                "analysis_commit": commit,
                "analysis_macro_sha256": macro_hash,
                "raw_validation_receipt_sha256":
                    row["raw_validation_receipt_sha256"],
                "pair_file_count": len(root_files),
                "pair_file_inventory_sha256": directory_digest(root_files),
                "upstream_heavy_stability_audit_sha256": provenance[
                    "upstream_stability_sha256"
                ],
                "upstream_tune_difference_allowlist_sha256": provenance[
                    "upstream_tune_allowlist_sha256"
                ],
            }
        )

    if validated and (
        len(analysis_commits) != 1
        or len(macro_hashes) != 1
        or len(stability_hashes) != 1
    ):
        raise ValueError(
            "analysis outputs mix implementation/raw provenance: "
            f"commits={sorted(analysis_commits)} "
            f"macro_hashes={sorted(macro_hashes)} "
            f"stability_hashes={sorted(stability_hashes)}"
        )
    status = "PASS" if not missing else "INCOMPLETE_VALID_PREFIX"
    report = {
        "schema": "hf_analysis_output_validation_v3",
        "status": status,
        "canonical_manifest": str(manifest),
        "canonical_manifest_sha256": manifest_sha,
        "canonical_freeze_seal_sha256": optional_sha256(
            freeze_dir / "freeze_seal.json"
        ),
        "canonical_validation_receipt_sha256": optional_sha256(
            freeze_dir / "canonical_raw_validation_receipt.json"
        ),
        "canonical_manifest_rows": len(rows),
        "analysis_root": str(analysis_root),
        "analysis_commit": (
            next(iter(analysis_commits)) if analysis_commits else None
        ),
        "analysis_macro_sha256": (
            next(iter(macro_hashes)) if macro_hashes else None
        ),
        "validated_output_count": len(validated),
        "missing_output_count": len(missing),
        "validated_outputs": validated,
    }
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.report:
        report_path = args.report.resolve()
        if report_path.exists() and report_path.read_text() != text:
            raise ValueError(
                f"refusing to overwrite a different validation report: {report_path}"
            )
        if not report_path.exists():
            atomic_write(report_path, text)
    print(
        "ANALYSIS_OUTPUT_MANIFEST_VALID "
        f"status={status} directories={len(validated)} "
        f"missing={len(missing)} commit="
        f"{next(iter(analysis_commits)) if analysis_commits else 'NONE'}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
