#!/usr/bin/env python3
"""Generate machine-derived evidence for an equal-tune expansion decision.

This command does not authorize an expansion.  It deterministically evaluates
a frozen coverage/precision specification against a complete matrix, and it
projects storage from the byte inventories of the sealed parent production.
The project owner may bind the resulting read-only artifacts in a separate
authorization only when the coverage report requires expansion and the fresh
storage projection passes.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
import stat
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import canonical_manifest as canonical_contract
except ModuleNotFoundError:
    _canonical_spec = importlib.util.spec_from_file_location(
        "canonical_manifest",
        Path(__file__).resolve().with_name("canonical_manifest.py"),
    )
    if _canonical_spec is None or _canonical_spec.loader is None:
        raise RuntimeError("cannot load canonical_manifest.py")
    canonical_contract = importlib.util.module_from_spec(_canonical_spec)
    _canonical_spec.loader.exec_module(canonical_contract)


TUNES = ("MONASH", "JUNCTIONS", "CLOSEPACKING")
COVERAGE_SPEC_SCHEMA = "hf_expansion_coverage_precision_spec_v1"
COVERAGE_MATRIX_SCHEMA = "hf_final_coverage_precision_matrix_v1"
COVERAGE_REPORT_SCHEMA = "hf_final_coverage_precision_report_v1"
STORAGE_REPORT_SCHEMA = "hf_equal_tune_expansion_storage_projection_v1"
EXPANSION_KIND = "equal_tune_canonical_expansion_v1"
SELECTION_RULE = "predeclared_coverage_and_precision_only_v1"
CAPACITY_POLICY = (
    "live_statvfs_available_after_full_projection_ge_5_percent_capacity_v1"
)


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(16 * 1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def read_json(path: Path, label: str) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"{label} is absent or a symbolic link: {path}")
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read {label} {path}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"{label} is not a JSON object: {path}")
    return value


def checked_file(path: Path, label: str) -> Path:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"{label} is absent or a symbolic link: {path}")
    resolved = path.resolve()
    if not resolved.is_file():
        raise ValueError(f"{label} does not resolve to a regular file: {path}")
    return resolved


def checked_directory(path: Path, label: str) -> Path:
    if path.is_symlink() or not path.is_dir():
        raise ValueError(f"{label} is absent or a symbolic link: {path}")
    resolved = path.resolve()
    if not resolved.is_dir():
        raise ValueError(f"{label} does not resolve to a directory: {path}")
    return resolved


def write_once(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o444)
    try:
        with os.fdopen(descriptor, "w") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        path.unlink(missing_ok=True)
        raise


def require_int(value: Any, label: str, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{label} is not an integer >= {minimum}: {value!r}")
    return value


def require_number(value: Any, label: str, minimum: float = 0.0) -> float:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(float(value))
        or float(value) < minimum
    ):
        raise ValueError(f"{label} is not finite and >= {minimum}: {value!r}")
    return float(value)


def sealed_parent(parent_freeze: Path) -> tuple[dict[str, Any], str]:
    parent_freeze = checked_directory(parent_freeze, "sealed parent freeze")
    canonical_contract.validate_directory(parent_freeze, require_seal=True)
    summary = read_json(
        parent_freeze / "freeze_summary.json", "parent freeze summary"
    )
    manifest = parent_freeze / "canonical_manifest.jsonl"
    manifest_sha = sha256(manifest)
    if summary.get("canonical_manifest_sha256") != manifest_sha:
        raise ValueError("sealed parent manifest checksum differs")
    return summary, manifest_sha


def generate_coverage(
    parent_freeze: Path,
    specification_path: Path,
    matrix_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    summary, manifest_sha = sealed_parent(parent_freeze)
    specification_path = checked_file(
        specification_path, "coverage/precision specification"
    )
    matrix_path = checked_file(matrix_path, "coverage/precision matrix")
    specification = read_json(
        specification_path, "coverage/precision specification"
    )
    matrix = read_json(matrix_path, "coverage/precision matrix")
    if (
        specification.get("schema") != COVERAGE_SPEC_SCHEMA
        or specification.get("frozen") is not True
        or specification.get("selection_rule") != SELECTION_RULE
    ):
        raise ValueError("coverage/precision specification contract differs")
    if (
        matrix.get("schema") != COVERAGE_MATRIX_SCHEMA
        or matrix.get("state") != "COMPLETE"
        or matrix.get("canonical_manifest_sha256") != manifest_sha
        or matrix.get("jobs_per_tune") != summary["jobs_per_tune"]
    ):
        raise ValueError("coverage/precision matrix is not parent-bound")

    criteria = specification.get("observables")
    observations = matrix.get("observations")
    if (
        not isinstance(criteria, list)
        or not criteria
        or not isinstance(observations, list)
        or not observations
    ):
        raise ValueError("coverage specification/matrix is empty")
    criteria_by_name: dict[str, dict[str, Any]] = {}
    for criterion in criteria:
        if not isinstance(criterion, dict):
            raise ValueError("coverage criterion is not an object")
        name = criterion.get("name")
        if not isinstance(name, str) or not name or name in criteria_by_name:
            raise ValueError("coverage criterion name is absent or duplicated")
        if set(criterion) != {
            "name",
            "minimum_finite_subsamples",
            "minimum_effective_entries",
            "maximum_relative_sem",
        }:
            raise ValueError(f"coverage criterion fields differ for {name}")
        require_int(
            criterion["minimum_finite_subsamples"],
            f"{name} minimum finite subsamples",
            2,
        )
        require_int(
            criterion["minimum_effective_entries"],
            f"{name} minimum effective entries",
            1,
        )
        require_number(
            criterion["maximum_relative_sem"],
            f"{name} maximum relative SEM",
            0.0,
        )
        criteria_by_name[name] = criterion

    observations_by_name: dict[str, dict[str, Any]] = {}
    for observation in observations:
        if not isinstance(observation, dict):
            raise ValueError("coverage observation is not an object")
        name = observation.get("name")
        if (
            not isinstance(name, str)
            or not name
            or name in observations_by_name
            or set(observation) != {
                "name",
                "central_value",
                "std_error",
                "finite_subsamples",
                "effective_entries",
            }
        ):
            raise ValueError("coverage observation fields/name differ")
        observations_by_name[name] = observation
    if set(criteria_by_name) != set(observations_by_name):
        raise ValueError(
            "coverage matrix does not exactly cover predeclared observables"
        )

    evaluations: list[dict[str, Any]] = []
    failing: list[str] = []
    for name in sorted(criteria_by_name):
        criterion = criteria_by_name[name]
        observation = observations_by_name[name]
        central = require_number(
            observation["central_value"], f"{name} absolute central value"
        )
        error = require_number(
            observation["std_error"], f"{name} standard error"
        )
        finite_subsamples = require_int(
            observation["finite_subsamples"],
            f"{name} finite subsamples",
        )
        effective_entries = require_int(
            observation["effective_entries"],
            f"{name} effective entries",
        )
        # A signed observable may have a negative central value.  The matrix
        # stores its magnitude specifically so the relative precision rule is
        # unambiguous and cannot flip with the observed physics sign.
        relative_sem = error / central if central > 0.0 else math.inf
        reasons: list[str] = []
        if finite_subsamples < criterion["minimum_finite_subsamples"]:
            reasons.append("insufficient_finite_subsamples")
        if effective_entries < criterion["minimum_effective_entries"]:
            reasons.append("insufficient_effective_entries")
        if not math.isfinite(relative_sem):
            reasons.append("zero_central_magnitude")
        elif relative_sem > criterion["maximum_relative_sem"]:
            reasons.append("relative_sem_above_predeclared_limit")
        passed = not reasons
        if not passed:
            failing.append(name)
        evaluations.append(
            {
                "name": name,
                "central_magnitude": central,
                "std_error": error,
                "finite_subsamples": finite_subsamples,
                "effective_entries": effective_entries,
                "relative_sem": (
                    relative_sem if math.isfinite(relative_sem) else None
                ),
                "criterion": criterion,
                "state": "PASS" if passed else "FAIL",
                "failure_reasons": reasons,
            }
        )

    report = {
        "schema": COVERAGE_REPORT_SCHEMA,
        "state": "EXPANSION_REQUIRED" if failing else "SUFFICIENT",
        "publication_promotion_allowed": not failing,
        "selection_rule": SELECTION_RULE,
        "canonical_manifest_sha256": manifest_sha,
        "parent_campaign": summary["campaign"],
        "parent_campaign_ordinal": summary["campaign_ordinal"],
        "jobs_per_tune": summary["jobs_per_tune"],
        "specification_path": str(specification_path),
        "specification_sha256": sha256(specification_path),
        "matrix_path": str(matrix_path),
        "matrix_sha256": sha256(matrix_path),
        "generator_sha256": sha256(Path(__file__).resolve()),
        "evaluations": evaluations,
        "failing_predeclared_observables": failing,
    }
    write_once(output_path.resolve(), report)
    return report


def directory_inventory(path: Path, label: str) -> dict[str, Any]:
    path = checked_directory(path, label)
    files = 0
    total_bytes = 0
    digest = hashlib.sha256()
    for candidate in sorted(path.rglob("*")):
        relative = candidate.relative_to(path).as_posix()
        metadata = candidate.lstat()
        if stat.S_ISLNK(metadata.st_mode):
            raise ValueError(f"{label} contains a symbolic link: {candidate}")
        if candidate.is_dir():
            continue
        if not candidate.is_file():
            raise ValueError(f"{label} contains a non-regular file: {candidate}")
        files += 1
        total_bytes += metadata.st_size
        digest.update(relative.encode())
        digest.update(b"\0")
        digest.update(str(metadata.st_size).encode())
        digest.update(b"\0")
        digest.update(sha256(candidate).encode())
        digest.update(b"\n")
    if files < 1 or total_bytes < 1:
        raise ValueError(f"{label} inventory is empty")
    return {
        "path": str(path),
        "file_count": files,
        "bytes": total_bytes,
        "inventory_sha256": digest.hexdigest(),
    }


def ceil_ratio(value: int, numerator: int, denominator: int) -> int:
    return (value * numerator + denominator - 1) // denominator


def generate_storage(
    campaign_json_path: Path,
    parent_freeze: Path,
    production_collection_root: Path,
    parent_analysis_root: Path,
    parent_analyzed_data_root: Path,
    capacity_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    summary, manifest_sha = sealed_parent(parent_freeze)
    campaign_json_path = checked_file(
        campaign_json_path, "expansion campaign"
    )
    campaign = read_json(campaign_json_path, "expansion campaign")
    additional = require_int(
        campaign.get("planned_additional_jobs_per_tune"),
        "additional jobs per tune",
        10,
    )
    parent_jobs = require_int(
        summary.get("jobs_per_tune"), "parent jobs per tune", 100
    )
    final_jobs = parent_jobs + additional
    candidate_slots = {
        "MONASH": additional,
        "JUNCTIONS": 2 * additional,
        "CLOSEPACKING": 2 * additional,
    }
    parent_binding = campaign.get("supersedes")
    if (
        campaign.get("campaign_kind") != EXPANSION_KIND
        or additional > 100
        or additional % 10
        or campaign.get("planned_final_jobs_per_tune") != final_jobs
        or campaign.get("candidate_slots") != candidate_slots
        or not isinstance(parent_binding, dict)
        or parent_binding.get("campaign") != summary["campaign"]
        or parent_binding.get("campaign_ordinal") !=
            summary["campaign_ordinal"]
        or parent_binding.get("jobs_per_tune") != parent_jobs
        or parent_binding.get("canonical_manifest_sha256") != manifest_sha
        or parent_binding.get("freeze_summary_sha256") !=
            sha256(parent_freeze.resolve() / "freeze_summary.json")
        or parent_binding.get("freeze_seal_sha256") !=
            sha256(parent_freeze.resolve() / canonical_contract.SEAL_NAME)
    ):
        raise ValueError("expansion campaign does not match its sealed parent")

    collection = checked_directory(
        production_collection_root, "production collection root"
    )
    rows = canonical_contract.read_jsonl(
        parent_freeze.resolve() / "canonical_manifest.jsonl"
    )
    maximum_raw_bytes = {tune: 0 for tune in TUNES}
    raw_inventory = hashlib.sha256()
    for row in rows:
        tune = row.get("tune")
        if tune not in maximum_raw_bytes:
            raise ValueError("parent manifest contains an unknown tune")
        relative = canonical_contract.relative_path(
            row.get("raw_path"), "parent raw path"
        )
        source = (
            collection / relative
            if summary["schema"]
            == canonical_contract.SUPERSEDING_SUMMARY_SCHEMA
            else collection / summary["campaign"] / relative
        )
        if (
            source.is_symlink()
            or not source.is_file()
            or source.stat().st_size != row.get("raw_bytes")
            or sha256(source) != row.get("raw_sha256")
        ):
            raise ValueError(f"parent raw inventory differs: {source}")
        maximum_raw_bytes[tune] = max(
            maximum_raw_bytes[tune], source.stat().st_size
        )
        raw_inventory.update(relative.as_posix().encode())
        raw_inventory.update(b"\0")
        raw_inventory.update(str(source.stat().st_size).encode())
        raw_inventory.update(b"\0")
        raw_inventory.update(row["raw_sha256"].encode())
        raw_inventory.update(b"\n")
    if any(value <= 0 for value in maximum_raw_bytes.values()):
        raise ValueError("parent raw inventory has no positive per-tune maximum")

    analysis_inventory = directory_inventory(
        parent_analysis_root, "parent analysis output"
    )
    analyzed_inventory = directory_inventory(
        parent_analyzed_data_root, "parent analyzed-data output"
    )
    projected_raw = sum(
        candidate_slots[tune] * maximum_raw_bytes[tune] for tune in TUNES
    )
    projected_analysis = ceil_ratio(
        analysis_inventory["bytes"], additional, parent_jobs
    )
    # The superseding pair-object tree is regenerated for all N accepted jobs;
    # it is a new output namespace and coexists with the sealed parent's tree.
    projected_final_analyzed = ceil_ratio(
        analyzed_inventory["bytes"], final_jobs, parent_jobs
    )
    retry_partial_contingency = projected_raw
    merge_staging_contingency = projected_final_analyzed
    subtotal = (
        projected_raw
        + projected_analysis
        + projected_final_analyzed
        + retry_partial_contingency
        + merge_staging_contingency
    )
    filesystem_overhead = ceil_ratio(subtotal, 1, 10)
    required = subtotal + filesystem_overhead

    if capacity_path.is_symlink() or not capacity_path.exists():
        raise ValueError("capacity target is absent or a symbolic link")
    capacity_target = capacity_path.resolve()
    filesystem = os.statvfs(capacity_target)
    capacity_bytes = filesystem.f_blocks * filesystem.f_frsize
    available_bytes = filesystem.f_bavail * filesystem.f_frsize
    reserve_bytes = ceil_ratio(capacity_bytes, 5, 100)
    projected_available = available_bytes - required
    passed = projected_available >= reserve_bytes
    checked_utc = datetime.now(timezone.utc).isoformat()
    capacity_check = {
        "state": "PASS" if passed else "FAIL",
        "checked_utc": checked_utc,
        "path": str(capacity_target),
        "device": capacity_target.stat().st_dev,
        "capacity_bytes": capacity_bytes,
        "available_bytes": available_bytes,
        "required_additional_bytes": required,
        "reserve_fraction": 0.05,
        "reserve_bytes": reserve_bytes,
        "projected_available_bytes": projected_available,
        "capacity_policy": CAPACITY_POLICY,
    }
    report = {
        "schema": STORAGE_REPORT_SCHEMA,
        "state": "PASS" if passed else "FAIL",
        "gate_e_storage_authorized": passed,
        "campaign": campaign["campaign"],
        "campaign_ordinal": campaign["campaign_ordinal"],
        "campaign_json_sha256": sha256(campaign_json_path),
        "parent_campaign": summary["campaign"],
        "parent_canonical_manifest_sha256": manifest_sha,
        "parent_jobs_per_tune": parent_jobs,
        "additional_jobs_per_tune": additional,
        "final_jobs_per_tune": final_jobs,
        "candidate_slots": candidate_slots,
        "parent_raw_inventory_sha256": raw_inventory.hexdigest(),
        "maximum_parent_raw_bytes_by_tune": maximum_raw_bytes,
        "parent_analysis_inventory": analysis_inventory,
        "parent_analyzed_data_inventory": analyzed_inventory,
        "projection_components": {
            "all_candidate_raw_outputs_bytes": projected_raw,
            "additional_per_job_analysis_outputs_bytes": projected_analysis,
            "new_full_superseding_analyzed_outputs_bytes":
                projected_final_analyzed,
            "one_full_candidate_batch_retry_partial_contingency_bytes":
                retry_partial_contingency,
            "one_full_derived_output_staging_contingency_bytes":
                merge_staging_contingency,
            "ten_percent_filesystem_overhead_bytes": filesystem_overhead,
        },
        "projected_required_additional_bytes": required,
        "capacity_policy": CAPACITY_POLICY,
        "final_capacity_recheck": capacity_check,
        "generator_sha256": sha256(Path(__file__).resolve()),
    }
    write_once(output_path.resolve(), report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    coverage = commands.add_parser("coverage")
    coverage.add_argument("parent_freeze", type=Path)
    coverage.add_argument("specification", type=Path)
    coverage.add_argument("matrix", type=Path)
    coverage.add_argument("output", type=Path)
    coverage.set_defaults(
        function=lambda arguments: generate_coverage(
            arguments.parent_freeze,
            arguments.specification,
            arguments.matrix,
            arguments.output,
        )
    )

    storage = commands.add_parser("storage")
    storage.add_argument("campaign_json", type=Path)
    storage.add_argument("parent_freeze", type=Path)
    storage.add_argument("production_collection_root", type=Path)
    storage.add_argument("parent_analysis_root", type=Path)
    storage.add_argument("parent_analyzed_data_root", type=Path)
    storage.add_argument("capacity_path", type=Path)
    storage.add_argument("output", type=Path)
    storage.set_defaults(
        function=lambda arguments: generate_storage(
            arguments.campaign_json,
            arguments.parent_freeze,
            arguments.production_collection_root,
            arguments.parent_analysis_root,
            arguments.parent_analyzed_data_root,
            arguments.capacity_path,
            arguments.output,
        )
    )
    arguments = parser.parse_args()
    result = arguments.function(arguments)
    print(
        f"EXPANSION_EVIDENCE_{arguments.command.upper()} "
        f"state={result['state']} output={arguments.output.resolve()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
