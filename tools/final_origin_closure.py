#!/usr/bin/env python3
"""Audit and aggregate origin resolution over an exact sealed final manifest.

This is a post-production publication gate, not a pilot extrapolation.  Every
canonical raw file is audited with Validation/AuditOriginResolution.C and the
per-job ROOT outputs are retained.  The aggregate report is bound to the
sealed canonical manifest and fails publication readiness when a trigger
candidate has unresolved hard-process ancestry.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import math
import os
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
import statistical_robustness as robustness  # noqa: E402


REPORT_SCHEMA = "hf_final_origin_closure_report_v1"
EXPECTED_AUDIT_SCHEMA = "origin_resolution_audit_v3"
EXPECTED_CLOSURE_SCHEMA = "primary_all_heavy_closure_v1"
ORIGIN_NAMES = {
    0: "unresolved",
    1: "selected_hard",
    2: "shower",
    3: "MPI",
    4: "other_resolved",
}
ROLE_NAMES = {0: "associate", 1: "trigger_candidate"}
CLOSURE_CATEGORIES = {
    0: "central_ground_associate",
    1: "central_ground_outside_associate_acceptance",
    2: "excluded_vector",
    3: "excluded_excited",
    4: "hidden_heavy",
    5: "multiply_heavy",
    6: "other_noncentral",
    7: "unresolved_companion",
}


def require_regular(path: Path, label: str) -> None:
    if path.is_symlink() or not path.is_file() or path.stat().st_size <= 0:
        raise ValueError(f"{label} is absent, empty, or a symlink: {path}")


def resolve_evidence_path(root: Path, relative: Any, label: str) -> Path:
    if not isinstance(relative, str) or not relative:
        raise ValueError(f"{label} path is absent")
    value = Path(relative)
    if value.is_absolute() or ".." in value.parts:
        raise ValueError(f"{label} path is not production-root-relative")
    resolved_root = root.resolve()
    resolved = (resolved_root / value).resolve()
    if resolved != resolved_root and resolved_root not in resolved.parents:
        raise ValueError(f"{label} escapes the production root")
    require_regular(resolved, label)
    return resolved


def cpp_string(value: str) -> str:
    return json.dumps(value)


def run_one_audit(
    checkout: Path,
    production_root: Path,
    staging: Path,
    row: dict[str, Any],
) -> dict[str, Any]:
    tune = str(row["tune"])
    slot = int(row["canonical_slot"])
    raw = resolve_evidence_path(
        production_root, row.get("raw_path"), f"{tune}/slot_{slot:03d} raw"
    )
    receipt = resolve_evidence_path(
        production_root,
        row.get("raw_validation_receipt_path"),
        f"{tune}/slot_{slot:03d} raw-validation receipt",
    )
    if (
        robustness.sha256(raw) != row.get("raw_sha256")
        or robustness.sha256(receipt)
        != row.get("raw_validation_receipt_sha256")
    ):
        raise ValueError(
            f"{tune}/slot_{slot:03d}: canonical raw/receipt checksum changed"
        )

    job_directory = staging / "per_job" / tune / f"slot_{slot:03d}"
    job_directory.mkdir(parents=True, exist_ok=False)
    audit = job_directory / "origin_resolution.root"
    log = job_directory / "origin_resolution.log"
    macro = checkout / "Validation/AuditOriginResolution.C"
    script = "\n".join(
        (
            f"gROOT->ProcessLine({cpp_string(f'.L {macro}')});",
            "int final_origin_status = AuditOriginResolution("
            f"{cpp_string(str(raw))},{cpp_string(str(audit))},"
            f"{cpp_string(str(receipt))});",
            "gSystem->Exit(final_origin_status);",
            "",
        )
    )
    with log.open("w") as stream:
        completed = subprocess.run(
            ["root", "-l", "-b"],
            input=script,
            text=True,
            stdout=stream,
            stderr=subprocess.STDOUT,
            check=False,
        )
        stream.flush()
        os.fsync(stream.fileno())
    if completed.returncode != 0:
        raise RuntimeError(
            f"{tune}/slot_{slot:03d}: origin audit failed; see {log}"
        )
    require_regular(audit, f"{tune}/slot_{slot:03d} origin audit")
    text = log.read_text(errors="replace")
    if (
        "ORIGIN_RESOLUTION_AUDIT" not in text
        or f"tune={tune}" not in text
        or "error:" in text.lower()
    ):
        raise RuntimeError(
            f"{tune}/slot_{slot:03d}: origin audit log is incomplete"
        )
    return {
        "tune": tune,
        "canonical_slot": slot,
        "raw_path": raw.as_posix(),
        "raw_sha256": row["raw_sha256"],
        "raw_validation_receipt_path": receipt.as_posix(),
        "raw_validation_receipt_sha256":
            row["raw_validation_receipt_sha256"],
        "audit_path": audit.as_posix(),
        "audit_sha256": robustness.sha256(audit),
        "audit_log_path": log.as_posix(),
        "audit_log_sha256": robustness.sha256(log),
    }


def _tree_string(entry: Any, name: str) -> str:
    return str(getattr(entry, name))


def read_audit_root(record: dict[str, Any]) -> dict[str, Any]:
    try:
        import ROOT  # type: ignore
    except ImportError as error:
        raise RuntimeError("PyROOT is required to aggregate origin audits") from error
    path = Path(record["audit_path"])
    root_file = ROOT.TFile.Open(str(path), "READ")
    if not root_file or root_file.IsZombie():
        raise ValueError(f"cannot open origin-audit ROOT file: {path}")
    try:
        metadata_tree = root_file.Get("audit_metadata")
        summary_tree = root_file.Get("origin_summary")
        closure_tree = root_file.Get("primary_all_heavy_closure")
        if (
            not metadata_tree
            or metadata_tree.ClassName() != "TTree"
            or metadata_tree.GetEntries() != 1
            or not summary_tree
            or summary_tree.ClassName() != "TTree"
            or not closure_tree
            or closure_tree.ClassName() != "TTree"
        ):
            raise ValueError(f"{path}: required audit trees differ")
        metadata_tree.GetEntry(0)
        metadata = {
            name: _tree_string(metadata_tree, name)
            for name in (
                "audit_schema",
                "raw_schema",
                "selector",
                "origin_algorithm",
                "species_registry_schema",
                "species_registry_sha256",
                "tune",
                "primary_all_heavy_match_schema",
                "primary_all_heavy_closure_schema",
                "raw_input_sha256",
                "raw_validation_receipt_sha256",
                "role_definition",
                "weight_definition",
                "axis_policy",
            )
        }
        if (
            metadata["audit_schema"] != EXPECTED_AUDIT_SCHEMA
            or metadata["primary_all_heavy_closure_schema"]
            != EXPECTED_CLOSURE_SCHEMA
            or metadata["tune"] != record["tune"]
            or metadata["raw_input_sha256"] != record["raw_sha256"]
            or metadata["raw_validation_receipt_sha256"]
            != record["raw_validation_receipt_sha256"]
        ):
            raise ValueError(f"{path}: audit metadata does not bind its input")

        origin_rows: list[dict[str, Any]] = []
        for entry in summary_tree:
            row = {
                "tune": _tree_string(entry, "tune"),
                "sector": _tree_string(entry, "sector"),
                "species": _tree_string(entry, "species"),
                "role_name": _tree_string(entry, "role_name"),
                "origin_name": _tree_string(entry, "origin_name"),
                "resolution_name": _tree_string(entry, "resolution_name"),
                "role": int(entry.role),
                "hard_channel": int(entry.hard_channel),
                "pdg": int(entry.pdg),
                "origin": int(entry.origin),
                "resolution": int(entry.resolution),
                "candidates": int(entry.candidates),
                "sum_weights": float(entry.sum_weights),
                "sum_weights2": float(entry.sum_weights2),
            }
            if (
                row["tune"] != record["tune"]
                or row["role_name"] != ROLE_NAMES.get(row["role"])
                or row["origin_name"] != ORIGIN_NAMES.get(row["origin"])
                or row["candidates"] < 0
                or not math.isfinite(row["sum_weights"])
                or not math.isfinite(row["sum_weights2"])
                or row["sum_weights2"] < 0.0
            ):
                raise ValueError(f"{path}: invalid origin-summary row")
            origin_rows.append(row)

        closure_rows: list[dict[str, Any]] = []
        job_bases: dict[tuple[Any, ...], dict[str, Any]] = {}
        for entry in closure_tree:
            row = {
                "closure_schema": _tree_string(entry, "closure_schema"),
                "tune": _tree_string(entry, "tune"),
                "sector": _tree_string(entry, "sector"),
                "trigger_species": _tree_string(entry, "trigger_species"),
                "category_name": _tree_string(entry, "category_name"),
                "hard_channel": int(entry.hard_channel),
                "multiplicity_nch": int(entry.multiplicity_nch),
                "trigger_pdg": int(entry.trigger_pdg),
                "category": int(entry.category),
                "count": int(entry.count),
                "denominator_count": int(entry.denominator_count),
                "sum_weights": float(entry.sum_weights),
                "denominator_sum_weights":
                    float(entry.denominator_sum_weights),
            }
            if (
                row["closure_schema"] != EXPECTED_CLOSURE_SCHEMA
                or row["tune"] != record["tune"]
                or row["category_name"]
                != CLOSURE_CATEGORIES.get(row["category"])
                or row["multiplicity_nch"] < 0
                or row["multiplicity_nch"] > 4095
                or row["count"] < 0
                or row["denominator_count"] <= 0
                or not math.isfinite(row["sum_weights"])
                or not math.isfinite(row["denominator_sum_weights"])
            ):
                raise ValueError(f"{path}: invalid closure row")
            base = (
                row["tune"],
                row["sector"],
                row["trigger_species"],
                row["hard_channel"],
                row["multiplicity_nch"],
                row["trigger_pdg"],
            )
            base_state = job_bases.setdefault(
                base,
                {
                    "categories": set(),
                    "count": 0,
                    "weight": 0.0,
                    "denominator_count": row["denominator_count"],
                    "denominator_weight": row["denominator_sum_weights"],
                },
            )
            if (
                row["category"] in base_state["categories"]
                or base_state["denominator_count"] != row["denominator_count"]
                or not robustness.nearly_equal(
                    base_state["denominator_weight"],
                    row["denominator_sum_weights"],
                )
            ):
                raise ValueError(f"{path}: inconsistent closure denominator")
            base_state["categories"].add(row["category"])
            base_state["count"] += row["count"]
            base_state["weight"] += row["sum_weights"]
            closure_rows.append(row)
        for base, state in job_bases.items():
            if (
                state["categories"] != set(CLOSURE_CATEGORIES)
                or state["count"] != state["denominator_count"]
                or not robustness.nearly_equal(
                    state["weight"], state["denominator_weight"]
                )
            ):
                raise ValueError(f"{path}: closure does not close for {base}")
        return {
            "input": record,
            "metadata": metadata,
            "origin_rows": origin_rows,
            "closure_rows": closure_rows,
        }
    finally:
        root_file.Close()


def bind_promoted_audit_paths(
    payloads: Iterable[dict[str, Any]],
    staging: Path,
    output_directory: Path,
) -> list[dict[str, Any]]:
    """Replace staging-only audit names with their final absolute names.

    ROOT aggregation must read the files while they still live in ``staging``.
    The report is written before the atomic directory promotion, so its input
    inventory must name the paths that the promotion will create.
    """
    staging_root = staging.resolve()
    final_root = output_directory.resolve()
    rebound: list[dict[str, Any]] = []
    for payload in payloads:
        copied = dict(payload)
        record = dict(payload["input"])
        for key in ("audit_path", "audit_log_path"):
            staged_path = Path(str(record[key])).resolve()
            try:
                relative = staged_path.relative_to(staging_root)
            except ValueError as error:
                raise ValueError(
                    f"{key} is outside the final-origin staging directory: "
                    f"{staged_path}"
                ) from error
            record[key] = (final_root / relative).as_posix()
        copied["input"] = record
        rebound.append(copied)
    return rebound


def aggregate_payloads(
    payloads: Iterable[dict[str, Any]],
    freeze_provenance: dict[str, Any],
    audit_macro_sha256: str,
    checkout_commit: str,
    provenance_binding: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if provenance_binding is None:
        provenance_binding = {
            "provenance_mode": robustness.CURRENT_GRAPH_ANCESTRY,
            "accepted_historical_provenance_registry_sha256": None,
        }
    ordered = sorted(
        payloads,
        key=lambda payload: (
            robustness.EXPECTED_TUNES.index(payload["input"]["tune"]),
            payload["input"]["canonical_slot"],
        ),
    )
    jobs_per_tune = int(freeze_provenance["jobs_per_tune"])
    expected = [
        (tune, slot)
        for tune in robustness.EXPECTED_TUNES
        for slot in range(jobs_per_tune)
    ]
    observed = [
        (payload["input"]["tune"], payload["input"]["canonical_slot"])
        for payload in ordered
    ]
    if observed != expected:
        raise ValueError("origin audits do not cover every canonical tune/slot")

    common_metadata: dict[str, str] | None = None
    origin: dict[tuple[Any, ...], dict[str, Any]] = {}
    closure: dict[tuple[Any, ...], dict[str, Any]] = {}
    for payload in ordered:
        comparable_metadata = {
            key: value
            for key, value in payload["metadata"].items()
            if key not in {
                "tune",
                "raw_input_sha256",
                "raw_validation_receipt_sha256",
            }
        }
        if common_metadata is None:
            common_metadata = comparable_metadata
        elif comparable_metadata != common_metadata:
            raise ValueError("origin audits mix incompatible metadata contracts")
        for row in payload["origin_rows"]:
            key = (
                row["tune"],
                row["sector"],
                row["species"],
                row["role_name"],
                row["origin_name"],
                row["resolution_name"],
                row["role"],
                row["hard_channel"],
                row["pdg"],
                row["origin"],
                row["resolution"],
            )
            aggregate = origin.setdefault(
                key,
                {
                    **{
                        name: row[name]
                        for name in (
                            "tune",
                            "sector",
                            "species",
                            "role_name",
                            "origin_name",
                            "resolution_name",
                            "role",
                            "hard_channel",
                            "pdg",
                            "origin",
                            "resolution",
                        )
                    },
                    "candidates": 0,
                    "sum_weights": 0.0,
                    "sum_weights2": 0.0,
                },
            )
            aggregate["candidates"] += row["candidates"]
            aggregate["sum_weights"] += row["sum_weights"]
            aggregate["sum_weights2"] += row["sum_weights2"]

        for row in payload["closure_rows"]:
            key = (
                row["tune"],
                row["sector"],
                row["trigger_species"],
                row["hard_channel"],
                row["multiplicity_nch"],
                row["trigger_pdg"],
                row["category"],
                row["category_name"],
            )
            aggregate = closure.setdefault(
                key,
                {
                    **{
                        name: row[name]
                        for name in (
                            "closure_schema",
                            "tune",
                            "sector",
                            "trigger_species",
                            "hard_channel",
                            "multiplicity_nch",
                            "trigger_pdg",
                            "category",
                            "category_name",
                        )
                    },
                    "count": 0,
                    "denominator_count": 0,
                    "sum_weights": 0.0,
                    "denominator_sum_weights": 0.0,
                },
            )
            aggregate["count"] += row["count"]
            aggregate["denominator_count"] += row["denominator_count"]
            aggregate["sum_weights"] += row["sum_weights"]
            aggregate["denominator_sum_weights"] += (
                row["denominator_sum_weights"]
            )

    origin_rows = list(origin.values())
    for row in origin_rows:
        row["effective_entries"] = (
            row["sum_weights"] ** 2 / row["sum_weights2"]
            if row["sum_weights2"] > 0.0
            else None
        )
    closure_rows = list(closure.values())
    aggregate_bases: dict[tuple[Any, ...], dict[str, Any]] = {}
    for row in closure_rows:
        row["fraction"] = row["count"] / row["denominator_count"]
        row["weighted_fraction"] = (
            row["sum_weights"] / row["denominator_sum_weights"]
            if row["denominator_sum_weights"] != 0.0
            else None
        )
        base = (
            row["tune"],
            row["sector"],
            row["trigger_species"],
            row["hard_channel"],
            row["multiplicity_nch"],
            row["trigger_pdg"],
        )
        state = aggregate_bases.setdefault(
            base,
            {
                "categories": set(),
                "count": 0,
                "weight": 0.0,
                "denominator_count": row["denominator_count"],
                "denominator_weight": row["denominator_sum_weights"],
            },
        )
        if (
            row["category"] in state["categories"]
            or state["denominator_count"] != row["denominator_count"]
            or not robustness.nearly_equal(
                state["denominator_weight"],
                row["denominator_sum_weights"],
            )
        ):
            raise ValueError("aggregated closure denominator is inconsistent")
        state["categories"].add(row["category"])
        state["count"] += row["count"]
        state["weight"] += row["sum_weights"]
    for base, state in aggregate_bases.items():
        if (
            state["categories"] != set(CLOSURE_CATEGORIES)
            or state["count"] != state["denominator_count"]
            or not robustness.nearly_equal(
                state["weight"], state["denominator_weight"]
            )
        ):
            raise ValueError(f"aggregated closure does not close for {base}")

    unresolved_trigger_count = sum(
        row["candidates"]
        for row in origin_rows
        if row["role"] == 1 and row["origin"] == 0
    )
    unresolved_associate_count = sum(
        row["candidates"]
        for row in origin_rows
        if row["role"] == 0 and row["origin"] == 0
    )
    completion = (
        "PASS"
        if unresolved_trigger_count == 0
        else "NEEDS_FINAL_PHYSICS_REVIEW"
    )
    readiness = "READY" if unresolved_trigger_count == 0 else "BLOCKED"
    input_rows = [payload["input"] for payload in ordered]
    report = {
        "schema": REPORT_SCHEMA,
        "completion_state": completion,
        "publication_readiness": readiness,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "canonical_manifest_sha256":
            freeze_provenance["canonical_manifest_sha256"],
        "freeze_seal_sha256": freeze_provenance["freeze_seal_sha256"],
        "raw_production_commit": freeze_provenance["repository_commit"],
        "provenance_mode": provenance_binding["provenance_mode"],
        "accepted_historical_provenance_registry_sha256":
            provenance_binding[
                "accepted_historical_provenance_registry_sha256"
            ],
        "jobs_per_tune": jobs_per_tune,
        "audited_job_count": len(ordered),
        "audit_macro_sha256": audit_macro_sha256,
        "audit_checkout_commit": checkout_commit,
        "audit_contract": common_metadata,
        "input_audit_inventory_sha256": robustness.json_sha256(input_rows),
        "input_audits": input_rows,
        "unresolved_trigger_candidate_count": unresolved_trigger_count,
        "unresolved_associate_candidate_count": unresolved_associate_count,
        "origin_summary": sorted(
            origin_rows,
            key=lambda row: (
                robustness.EXPECTED_TUNES.index(row["tune"]),
                row["role"],
                row["sector"],
                row["pdg"],
                row["hard_channel"],
                row["origin"],
                row["resolution"],
            ),
        ),
        "primary_all_heavy_closure": sorted(
            closure_rows,
            key=lambda row: (
                robustness.EXPECTED_TUNES.index(row["tune"]),
                row["sector"],
                row["trigger_pdg"],
                row["hard_channel"],
                row["multiplicity_nch"],
                row["category"],
            ),
        ),
        "closure_base_count": len(aggregate_bases),
        "policy": (
            "Every sealed-canonical raw file must be audited. Nonzero "
            "unresolved trigger candidates require explicit final-sample "
            "physics review and block publication readiness. Unresolved "
            "associates are reported here and tested by exclusion in the "
            "statistical robustness report."
        ),
    }
    payload = dict(report)
    report["payload_sha256"] = robustness.json_sha256(payload)
    return report


def write_report_outputs(report: dict[str, Any], directory: Path) -> None:
    report_path = directory / "final_origin_closure_report_v1.json"
    robustness.atomic_write(
        report_path,
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n",
    )
    origin_stream = io.StringIO()
    origin_fields = [
        "tune",
        "sector",
        "species",
        "role_name",
        "origin_name",
        "resolution_name",
        "role",
        "hard_channel",
        "pdg",
        "origin",
        "resolution",
        "candidates",
        "sum_weights",
        "sum_weights2",
        "effective_entries",
    ]
    writer = csv.DictWriter(origin_stream, fieldnames=origin_fields)
    writer.writeheader()
    writer.writerows(report["origin_summary"])
    robustness.atomic_write(
        directory / "final_origin_summary_v1.csv", origin_stream.getvalue()
    )

    closure_stream = io.StringIO()
    closure_fields = [
        "closure_schema",
        "tune",
        "sector",
        "trigger_species",
        "hard_channel",
        "multiplicity_nch",
        "trigger_pdg",
        "category",
        "category_name",
        "count",
        "denominator_count",
        "sum_weights",
        "denominator_sum_weights",
        "fraction",
        "weighted_fraction",
    ]
    writer = csv.DictWriter(closure_stream, fieldnames=closure_fields)
    writer.writeheader()
    writer.writerows(report["primary_all_heavy_closure"])
    robustness.atomic_write(
        directory / "final_primary_all_heavy_closure_v1.csv",
        closure_stream.getvalue(),
    )


def run(
    canonical_freeze: Path,
    production_root: Path,
    output_directory: Path,
    checkout: Path,
    config_path: Path,
    workers: int,
) -> dict[str, Any]:
    if workers < 1 or workers > 32:
        raise ValueError("--workers must be in [1,32]")
    if output_directory.exists():
        raise ValueError(
            "output directory already exists; refusing to overwrite final "
            f"origin evidence: {output_directory}"
        )
    spec = robustness.load_json(config_path)
    robustness.validate_spec(spec, checkout)
    rows, freeze_provenance = robustness.validate_canonical_freeze(
        canonical_freeze, spec
    )
    macro = checkout / "Validation/AuditOriginResolution.C"
    require_regular(macro, "origin audit macro")
    checkout_commit = subprocess.check_output(
        ["git", "-C", str(checkout), "rev-parse", "HEAD"], text=True
    ).strip()
    tracked_status = subprocess.check_output(
        [
            "git",
            "-C",
            str(checkout),
            "status",
            "--porcelain",
            "--untracked-files=no",
        ],
        text=True,
    ).strip()
    if tracked_status:
        raise ValueError("origin audit checkout has tracked modifications")
    provenance_binding = robustness.validate_raw_checkout_lineage(
        checkout, rows, freeze_provenance, "origin-audit"
    )
    if provenance_binding["checkout_commit"] != checkout_commit:
        raise ValueError("origin-audit checkout changed during preflight")

    output_directory.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(
        tempfile.mkdtemp(
            prefix=f".{output_directory.name}.staging.",
            dir=output_directory.parent,
        )
    )
    print(
        "FINAL_ORIGIN_AUDIT_START "
        f"jobs={len(rows)} workers={workers} staging={staging}",
        flush=True,
    )
    records: list[dict[str, Any]] = []
    try:
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(
                    run_one_audit,
                    checkout,
                    production_root,
                    staging,
                    row,
                ): (row["tune"], row["canonical_slot"])
                for row in rows
            }
            for completed, future in enumerate(as_completed(futures), start=1):
                tune, slot = futures[future]
                records.append(future.result())
                print(
                    "FINAL_ORIGIN_AUDIT_PROGRESS "
                    f"completed={completed}/{len(rows)} tune={tune} "
                    f"slot={int(slot):03d}",
                    flush=True,
                )
        # Keep staging paths until every ROOT file has been read. Only the
        # serialized inventory is rebound to the directory that os.replace()
        # promotes below.
        payloads = [read_audit_root(record) for record in records]
        payloads = bind_promoted_audit_paths(
            payloads, staging, output_directory
        )
        report = aggregate_payloads(
            payloads,
            freeze_provenance,
            robustness.sha256(macro),
            checkout_commit,
            provenance_binding,
        )
        write_report_outputs(report, staging)
        os.replace(staging, output_directory)
    except Exception:
        print(
            "FINAL_ORIGIN_AUDIT_STAGING_RETAINED "
            f"path={staging}",
            flush=True,
        )
        raise
    print(
        "FINAL_ORIGIN_AUDIT_COMPLETE "
        f"state={report['completion_state']} "
        f"publication_readiness={report['publication_readiness']} "
        f"jobs={report['audited_job_count']} "
        "unresolved_trigger_candidates="
        f"{report['unresolved_trigger_candidate_count']} "
        f"report={output_directory / 'final_origin_closure_report_v1.json'}",
        flush=True,
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--canonical-freeze", type=Path, required=True)
    parser.add_argument("--production-root", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument(
        "--checkout",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(__file__).resolve().parents[1]
        / "config/statistical_robustness_v1.json",
    )
    parser.add_argument("--workers", type=int, default=4)
    arguments = parser.parse_args()
    try:
        report = run(
            arguments.canonical_freeze.resolve(),
            arguments.production_root.resolve(),
            arguments.output_directory.resolve(),
            arguments.checkout.resolve(),
            arguments.config.resolve(),
            arguments.workers,
        )
    except (
        OSError,
        KeyError,
        TypeError,
        ValueError,
        RuntimeError,
        subprocess.SubprocessError,
    ) as error:
        print(f"FINAL_ORIGIN_AUDIT_ERROR {error}")
        return 2
    return 0 if report["publication_readiness"] == "READY" else 3


if __name__ == "__main__":
    raise SystemExit(main())
