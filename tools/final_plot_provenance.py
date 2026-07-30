#!/usr/bin/env python3
"""Create and verify fail-closed provenance for generated publication plots.

The runner takes a snapshot immediately before a plotting stage.  After ROOT
returns successfully, ``record`` identifies every generated/overwritten PDF,
PNG, and ROOT macro, validates that each canvas has all three representations,
freezes the exact input inventory, writes one immutable run receipt, and puts
an adjacent ``.provenance.json`` sidecar next to every output.

Canonical pair mode requires the sealed canonical manifest, all ten block
manifests, and the v2 merge provenance/checksum inventory in every central and
block directory.  Legacy mode deliberately records the absence of those
manifests and can never be publication eligible.

Canonical-validation modes consume the same sealed inputs for an explicitly
ineligible candidate review stage.  They prevent a circular dependency
between final evidence, human authorization, and plotting; candidate outputs
must be regenerated in eligible canonical mode after authorization.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path
from typing import Any, Iterable

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
import dataset_selector as dataset_contract  # noqa: E402


SCHEMA = "hf_final_plot_provenance_v1"
RUN_SCHEMA = "hf_final_plot_run_provenance_v1"
SNAPSHOT_SCHEMA = "hf_plot_output_snapshot_v1"
TUNES = ("MONASH", "JUNCTIONS", "CLOSEPACKING")
OUTPUT_SUFFIXES = (".pdf", ".png", ".C")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


class ProvenanceFailure(ValueError):
    """A publication plot cannot be provenance-certified."""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(16 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_digest(rows: Any) -> str:
    payload = json.dumps(
        rows, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()
    return hashlib.sha256(payload).hexdigest()


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def require_regular(path: Path, label: str, *, nonempty: bool = True) -> Path:
    if path.is_symlink() or not path.is_file():
        raise ProvenanceFailure(f"{label} is absent/not regular: {path}")
    if nonempty and path.stat().st_size <= 0:
        raise ProvenanceFailure(f"{label} is empty: {path}")
    return path


def load_json(path: Path, label: str) -> dict[str, Any]:
    require_regular(path, label)
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise ProvenanceFailure(f"{label} is invalid JSON: {path}") from error
    if not isinstance(value, dict):
        raise ProvenanceFailure(f"{label} must contain one JSON object")
    return value


def load_jsonl(path: Path, label: str) -> list[dict[str, Any]]:
    require_regular(path, label)
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as error:
            raise ProvenanceFailure(
                f"{label} row {number} is invalid JSON: {path}"
            ) from error
        if not isinstance(row, dict):
            raise ProvenanceFailure(f"{label} row {number} is not an object")
        rows.append(row)
    if not rows:
        raise ProvenanceFailure(f"{label} has no rows: {path}")
    return rows


def atomic_json(path: Path, value: dict[str, Any], *, exclusive: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if exclusive and path.exists():
        raise ProvenanceFailure(f"refusing to overwrite provenance: {path}")
    descriptor, temporary_text = tempfile.mkstemp(
        prefix=f".{path.name}.", dir=path.parent
    )
    temporary = Path(temporary_text)
    try:
        with os.fdopen(descriptor, "w") as stream:
            json.dump(value, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        if exclusive:
            try:
                os.link(temporary, path)
            except FileExistsError as error:
                raise ProvenanceFailure(
                    f"refusing to overwrite provenance: {path}"
                ) from error
            temporary.unlink()
        else:
            os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def exclusive_copy(source: Path, destination: Path) -> None:
    require_regular(source, "configuration to archive")
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(
        destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o444
    )
    try:
        with os.fdopen(descriptor, "wb") as output:
            with source.open("rb") as input_stream:
                for chunk in iter(
                    lambda: input_stream.read(16 * 1024 * 1024), b""
                ):
                    output.write(chunk)
            output.flush()
            os.fsync(output.fileno())
    except BaseException:
        destination.unlink(missing_ok=True)
        raise


def resolve(path: str | Path, checkout: Path) -> Path:
    candidate = Path(path).expanduser()
    if not candidate.is_absolute():
        candidate = checkout / candidate
    return candidate.resolve()


def display_path(path: Path, checkout: Path) -> str:
    try:
        return path.resolve().relative_to(checkout.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def git(checkout: Path, *arguments: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(checkout), *arguments], text=True
    ).strip()


def checkout_binding(checkout: Path, publication_eligible: bool,
                     development: bool) -> dict[str, Any]:
    commit = git(checkout, "rev-parse", "HEAD")
    if not HEX40.fullmatch(commit):
        raise ProvenanceFailure("plotting checkout has no full Git commit")
    tracked_status = git(
        checkout, "status", "--porcelain=v1", "--untracked-files=no"
    )
    if publication_eligible and tracked_status and not development:
        raise ProvenanceFailure(
            "publication plot provenance requires a tracked-clean checkout"
        )
    return {
        "plotting_commit": commit,
        "plotting_tree": git(checkout, "rev-parse", "HEAD^{tree}"),
        "tracked_worktree_status": tracked_status,
        "development_override": development,
    }


def file_record(path: Path, checkout: Path) -> dict[str, Any]:
    require_regular(path, "input/output artifact")
    return {
        "path": display_path(path, checkout),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def output_roots(
    checkout: Path,
    explicit: Iterable[str],
    config_path: Path | None,
) -> list[Path]:
    roots = {resolve(item, checkout) for item in explicit}
    if config_path is not None:
        config = load_json(config_path, "plot configuration")
        for key in ("canvases_to_be_drawn", "global_canvases_to_be_drawn"):
            for row in config.get(key, []):
                if (
                    isinstance(row, dict)
                    and row.get("write") is True
                    and isinstance(row.get("write_path"), str)
                    and row["write_path"] not in ("", "NONE")
                ):
                    roots.add(resolve(row["write_path"], checkout))
        if config.get("draw_correlation_plots") is True:
            roots.add(
                checkout
                / "PlottingScripts"
                / "Plots"
                / "THnSparse"
                / "Correlations"
            )
    if not roots:
        raise ProvenanceFailure("no plot output root was declared")
    for root in roots:
        if root == checkout or root == checkout.parent or root == Path("/"):
            raise ProvenanceFailure(f"unsafe broad plot output root: {root}")
    return sorted(roots)


def discover_outputs(roots: Iterable[Path]) -> dict[str, dict[str, Any]]:
    outputs: dict[str, dict[str, Any]] = {}
    for root in roots:
        if root.is_symlink():
            raise ProvenanceFailure(f"plot output root is a symlink: {root}")
        if not root.exists():
            continue
        if not root.is_dir():
            raise ProvenanceFailure(f"plot output root is not a directory: {root}")
        for path in sorted(root.rglob("*")):
            if path.is_symlink():
                raise ProvenanceFailure(f"plot output contains a symlink: {path}")
            if path.is_file() and path.suffix in OUTPUT_SUFFIXES:
                stat_value = path.stat()
                outputs[str(path.resolve())] = {
                    "bytes": stat_value.st_size,
                    "mtime_ns": stat_value.st_mtime_ns,
                    "sha256": sha256(path),
                }
    return outputs


def command_snapshot(args: argparse.Namespace) -> int:
    checkout = args.checkout.resolve()
    config = args.config.resolve() if args.config else None
    roots = output_roots(checkout, args.output_root, config)
    payload = {
        "schema": SNAPSHOT_SCHEMA,
        "checkout": str(checkout),
        "roots": [str(path) for path in roots],
        "outputs": discover_outputs(roots),
        "created_utc": utc_now(),
    }
    atomic_json(args.state.resolve(), payload, exclusive=True)
    print(
        "PLOT_PROVENANCE_SNAPSHOT "
        f"roots={len(roots)} outputs={len(payload['outputs'])}"
    )
    return 0


def changed_outputs(
    snapshot: dict[str, Any], roots: list[Path]
) -> list[Path]:
    previous = snapshot.get("outputs")
    if snapshot.get("schema") != SNAPSHOT_SCHEMA or not isinstance(
        previous, dict
    ):
        raise ProvenanceFailure("invalid plot-output snapshot")
    current = discover_outputs(roots)
    changed = [
        Path(name)
        for name, binding in current.items()
        if previous.get(name) != binding
    ]
    if not changed:
        raise ProvenanceFailure(
            "plot stage produced or overwrote no PDF/PNG/ROOT macro"
        )
    return sorted(changed)


def logical_canvas(path: Path) -> tuple[str, str]:
    name = path.name
    if name.endswith("_PDF.pdf"):
        return name[:-8], ".pdf"
    if name.endswith("_PNG.png"):
        return name[:-8], ".png"
    if name.endswith("_MACRO.C"):
        return name[:-8], ".C"
    return path.stem, path.suffix


def require_triplets(outputs: list[Path]) -> None:
    groups: dict[tuple[Path, str], set[str]] = {}
    for path in outputs:
        stem, suffix = logical_canvas(path)
        groups.setdefault((path.parent, stem), set()).add(suffix)
    required = set(OUTPUT_SUFFIXES)
    failures = {
        f"{directory}/{stem}": sorted(required - suffixes)
        for (directory, stem), suffixes in groups.items()
        if suffixes != required
    }
    if failures:
        raise ProvenanceFailure(
            "generated canvas representations are incomplete: "
            + json.dumps(failures, sort_keys=True)
        )


def manifest_binding(path: Path, checkout: Path, role: str) -> dict[str, Any]:
    rows = load_jsonl(path, role)
    return {
        "role": role,
        **file_record(path, checkout),
        "rows": len(rows),
    }


def canonical_freeze_binding(
    canonical_manifest: Path, checkout: Path
) -> dict[str, Any]:
    directory = canonical_manifest.parent
    summary_path = directory / "freeze_summary.json"
    seal_path = directory / "freeze_seal.json"
    receipt_path = directory / "canonical_raw_validation_receipt.json"
    log_path = directory / "canonical_raw_validation.log"
    summary = load_json(summary_path, "canonical freeze summary")
    seal = load_json(seal_path, "canonical freeze seal")
    receipt = load_json(receipt_path, "canonical validation receipt")
    require_regular(log_path, "canonical validation log")
    manifest_sha = sha256(canonical_manifest)
    if (
        summary.get("schema")
        not in {
            "hf_canonical_freeze_summary_v3",
            "hf_superseding_canonical_freeze_summary_v4",
        }
        or summary.get("canonical_manifest_sha256") != manifest_sha
        or seal.get("schema")
        not in {
            "hf_canonical_freeze_seal_v2",
            "hf_superseding_canonical_freeze_seal_v3",
        }
        or seal.get("state") != "SEALED"
        or seal.get("canonical_manifest_sha256") != manifest_sha
        or seal.get("validation_receipt_path")
        != "canonical_raw_validation_receipt.json"
        or seal.get("validation_receipt_sha256") != sha256(receipt_path)
        or seal.get("validation_log_path") != "canonical_raw_validation.log"
        or seal.get("validation_log_sha256") != sha256(log_path)
        or receipt.get("state") != "PASS"
        or receipt.get("canonical_manifest_sha256") != manifest_sha
        or receipt.get("validation_log_sha256") != sha256(log_path)
    ):
        raise ProvenanceFailure(
            "canonical plot input is not bound to an exact sealed PASS freeze"
        )
    return {
        "summary": file_record(summary_path, checkout),
        "seal": file_record(seal_path, checkout),
        "validation_receipt": file_record(receipt_path, checkout),
        "validation_log": file_record(log_path, checkout),
        "summary_schema": summary["schema"],
        "seal_schema": seal["schema"],
        "campaign": summary.get("campaign"),
        "campaign_ordinal": summary.get("campaign_ordinal"),
        "jobs_per_tune": summary.get("jobs_per_tune"),
        "canonical_manifest_sha256": manifest_sha,
    }


def validate_canonical_block_partition(
    canonical_path: Path, block_paths: list[Path]
) -> tuple[int, dict[str, int]]:
    canonical_rows = load_jsonl(canonical_path, "canonical manifest")
    identities = []
    per_tune = {tune: 0 for tune in TUNES}
    for row in canonical_rows:
        tune = row.get("tune")
        slot = row.get("canonical_slot")
        block = row.get("block")
        if (
            tune not in TUNES
            or isinstance(slot, bool)
            or not isinstance(slot, int)
            or slot < 0
            or isinstance(block, bool)
            or not isinstance(block, int)
            or block != slot % 10
        ):
            raise ProvenanceFailure("canonical manifest block identity is invalid")
        identities.append((tune, slot))
        per_tune[tune] += 1
    if len(set(identities)) != len(identities):
        raise ProvenanceFailure("canonical manifest identities are duplicated")
    counts = set(per_tune.values())
    if (
        len(counts) != 1
        or next(iter(counts)) < 100
        or next(iter(counts)) % 10 != 0
    ):
        raise ProvenanceFailure(
            "canonical manifest needs equal N>=100 per tune divisible by ten"
        )
    observed: set[tuple[str, int]] = set()
    expected_per_block = len(canonical_rows) // 10
    for expected_block, path in enumerate(block_paths):
        rows = load_jsonl(path, f"canonical block {expected_block + 1}")
        if len(rows) != expected_per_block:
            raise ProvenanceFailure(
                f"canonical block {expected_block + 1} has wrong row count"
            )
        for row in rows:
            identity = (row.get("tune"), row.get("canonical_slot"))
            if (
                row.get("block") != expected_block
                or identity not in set(identities)
                or identity in observed
            ):
                raise ProvenanceFailure(
                    "canonical block manifests are not exact/disjoint"
                )
            observed.add(identity)
    if observed != set(identities):
        raise ProvenanceFailure(
            "ten canonical block manifests do not cover the central union"
        )
    return next(iter(counts)), per_tune


def selector_binding(
    selector_path: Path | None, checkout: Path
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    if selector_path is None:
        return {
            "selector_document": None,
            "active_dataset": None,
            "status": "gate_d_pilot",
            "publication_eligible": False,
            "manifest_status": "PILOT_NOT_FINAL_CANONICAL_DATASET",
        }, None
    try:
        active, row = dataset_contract.load(selector_path, checkout)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        raise ProvenanceFailure(
            f"dataset selector is not publication-authorized: {error}"
        ) from error
    publication_eligible = row["publication_eligible"]
    return {
        "selector_document": file_record(selector_path, checkout),
        "active_dataset": active,
        "status": row.get("status"),
        "publication_eligible": publication_eligible,
        "raw_schema": row.get("raw_schema"),
        "selector": row.get("selector"),
        "campaign": row.get("campaign"),
        "interpretation": row.get("interpretation"),
        "publication_eligibility_evidence":
            row.get("publication_eligibility_evidence"),
    }, row


def configured_pair_files(config: dict[str, Any]) -> list[str]:
    names: set[str] = set()
    for key in (
        "beauty_correlations_to_analyse",
        "charm_correlations_to_analyse",
    ):
        groups = config.get(key)
        if not isinstance(groups, list) or not groups:
            raise ProvenanceFailure(f"plot configuration lacks {key}")
        for group in groups:
            if not isinstance(group, dict) or not isinstance(
                group.get("configs"), list
            ):
                raise ProvenanceFailure(f"malformed configured pair group: {key}")
            for pair in group["configs"]:
                if not isinstance(pair, dict):
                    raise ProvenanceFailure("malformed configured OS/SS pair")
                for field in ("OS", "SS"):
                    name = pair.get(field)
                    if (
                        not isinstance(name, str)
                        or not name.endswith(".root")
                        or Path(name).name != name
                    ):
                        raise ProvenanceFailure(
                            f"invalid configured pair filename: {name!r}"
                        )
                    names.add(name)
    return sorted(names)


def resolve_central(
    base: Path, tune: str, tag: str, filename: str
) -> Path:
    candidates = (
        base / tune / f"{tag}_{tune}" / filename,
        base / tune / tag / filename,
        base / f"{tag}_{tune}" / filename,
        base / tag / filename,
    )
    for candidate in candidates:
        if candidate.is_file() and not candidate.is_symlink():
            return candidate.resolve()
    raise ProvenanceFailure(
        f"configured central pair input is absent: {tune}/{filename}"
    )


def resolve_block(
    base: Path, tune: str, block: int, filename: str
) -> Path:
    subdir = f"combined_root_{block}"
    candidates = (
        Path(f"{base}_{tune}") / subdir / filename,
        base / tune / subdir / filename,
    )
    for candidate in candidates:
        if candidate.is_file() and not candidate.is_symlink():
            return candidate.resolve()
    raise ProvenanceFailure(
        f"configured block pair input is absent: "
        f"{tune}/block_{block:02d}/{filename}"
    )


def validate_merge_directory(
    directory: Path,
    configured_paths: list[Path],
    expected_source_manifest_sha: str,
    expected_input_count: int,
    checkout: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    provenance_path = directory / "merge_provenance.json"
    inventory_path = directory / "merged_pair_checksums.json"
    source_path = directory / "source_manifest.jsonl"
    provenance = load_json(provenance_path, "merged-pair provenance")
    inventory = load_json(inventory_path, "merged-pair checksum inventory")
    require_regular(source_path, "copied source manifest")
    if (
        provenance.get("schema")
        != "hf_merged_pair_directory_provenance_v2"
        or provenance.get("status") != "PASS"
        or provenance.get("source_manifest_sha256")
        != expected_source_manifest_sha
        or provenance.get("merge_input_file_count") != expected_input_count
        or sha256(source_path) != expected_source_manifest_sha
    ):
        raise ProvenanceFailure(
            f"merged-pair provenance/source manifest differs: {directory}"
        )
    rows = inventory.get("files")
    if (
        inventory.get("schema") != "hf_merged_pair_checksum_inventory_v1"
        or not isinstance(rows, list)
    ):
        raise ProvenanceFailure(
            f"merged-pair checksum inventory is invalid: {directory}"
        )
    indexed = {
        row.get("path"): row
        for row in rows
        if isinstance(row, dict) and isinstance(row.get("path"), str)
    }
    exact = []
    for path in sorted(configured_paths):
        row = indexed.get(path.name)
        if (
            row is None
            or row.get("bytes") != path.stat().st_size
            or row.get("sha256") != sha256(path)
        ):
            raise ProvenanceFailure(
                f"configured ROOT input differs from merged inventory: {path}"
            )
        exact.append(file_record(path, checkout))
    binding = {
        "directory": display_path(directory, checkout),
        "tune": provenance.get("tune"),
        "analysis_commit": provenance.get("analysis_commit"),
        "merge_commit": provenance.get("repository_commit"),
        "merge_provenance": file_record(provenance_path, checkout),
        "root_checksum_inventory": file_record(inventory_path, checkout),
        "source_manifest": file_record(source_path, checkout),
        "configured_root_inputs": len(exact),
    }
    return binding, exact


def canonical_pair_inputs(
    *,
    checkout: Path,
    config_path: Path,
    config: dict[str, Any],
    row: dict[str, Any],
    analyzed_data_base: str | None,
    complete_root_tag: str | None,
    subsample_base: str | None,
) -> dict[str, Any]:
    manifest_value = row.get("canonical_manifest")
    if not isinstance(manifest_value, str) or not manifest_value:
        raise ProvenanceFailure("canonical selector has no canonical manifest")
    canonical_manifest = resolve(manifest_value, checkout)
    canonical = manifest_binding(
        canonical_manifest, checkout, "canonical_manifest"
    )
    freeze = canonical_freeze_binding(canonical_manifest, checkout)
    block_bindings = []
    block_paths = []
    for block in range(1, 11):
        path = canonical_manifest.parent / f"block_{block:02d}.jsonl"
        block_paths.append(path)
        block_bindings.append(
            manifest_binding(path, checkout, f"block_{block:02d}")
        )
    jobs_per_tune, manifest_tune_counts = validate_canonical_block_partition(
        canonical_manifest, block_paths
    )

    base = resolve(
        analyzed_data_base or str(config.get("base_dir", "")), checkout
    )
    tag = complete_root_tag or str(
        config.get("bb_bar_complete_root_dir", "")
    )
    charm_tag = complete_root_tag or str(
        config.get("cc_bar_complete_root_dir", "")
    )
    if not tag or not charm_tag:
        raise ProvenanceFailure("complete-root tag is absent")
    block_base = resolve(
        subsample_base
        or str(config.get("bb_bar_complete_root_dir_sub_samples", "")),
        checkout,
    )
    charm_block_base = resolve(
        subsample_base
        or str(config.get("cc_bar_complete_root_dir_sub_samples", "")),
        checkout,
    )
    names_by_flavour = {}
    for flavour, key in (
        ("beauty", "beauty_correlations_to_analyse"),
        ("charm", "charm_correlations_to_analyse"),
    ):
        reduced = dict(config)
        other = (
            "charm_correlations_to_analyse"
            if flavour == "beauty"
            else "beauty_correlations_to_analyse"
        )
        reduced[other] = [{"configs": []}]
        names: set[str] = set()
        for group in config.get(key, []):
            for pair in group.get("configs", []):
                names.update((pair.get("OS"), pair.get("SS")))
        if not names or any(not isinstance(name, str) for name in names):
            raise ProvenanceFailure(f"no valid {flavour} pair inputs")
        names_by_flavour[flavour] = sorted(names)

    directories: dict[Path, dict[str, Any]] = {}
    for tune in config.get("PYTHIA_TUNES", []):
        if tune not in TUNES:
            raise ProvenanceFailure(f"unsupported tune in plot config: {tune}")
        for flavour, names in names_by_flavour.items():
            central_tag = tag if flavour == "beauty" else charm_tag
            central_paths = [
                resolve_central(base, tune, central_tag, name) for name in names
            ]
            directory = central_paths[0].parent
            if any(path.parent != directory for path in central_paths):
                raise ProvenanceFailure(
                    f"{flavour}/{tune} central inputs span directories"
                )
            directories.setdefault(
                directory,
                {
                    "paths": set(),
                    "source_sha": canonical["sha256"],
                    "kind": "central",
                    "block": None,
                },
            )["paths"].update(central_paths)
            selected_block_base = (
                block_base if flavour == "beauty" else charm_block_base
            )
            for block, block_binding in enumerate(block_bindings, start=1):
                paths = [
                    resolve_block(selected_block_base, tune, block, name)
                    for name in names
                ]
                directory = paths[0].parent
                if any(path.parent != directory for path in paths):
                    raise ProvenanceFailure(
                        f"{flavour}/{tune}/block {block} inputs span directories"
                    )
                entry = directories.setdefault(
                    directory,
                    {
                        "paths": set(),
                        "source_sha": block_binding["sha256"],
                        "kind": "block",
                        "block": block,
                    },
                )
                if entry["source_sha"] != block_binding["sha256"]:
                    raise ProvenanceFailure("block directory source ambiguity")
                entry["paths"].update(paths)

    merged = []
    exact = []
    for directory, values in sorted(
        directories.items(), key=lambda item: str(item[0])
    ):
        binding, root_inputs = validate_merge_directory(
            directory,
            sorted(values["paths"]),
            values["source_sha"],
            (
                jobs_per_tune
                if values["kind"] == "central"
                else jobs_per_tune // 10
            ),
            checkout,
        )
        binding["kind"] = values["kind"]
        binding["block"] = values["block"]
        merged.append(binding)
        exact.extend(root_inputs)
    deduplicated = {row["path"]: row for row in exact}
    analysis_commits = {
        row.get("analysis_commit") for row in merged
    }
    if (
        len(analysis_commits) != 1
        or not HEX40.fullmatch(str(next(iter(analysis_commits), "")))
    ):
        raise ProvenanceFailure(
            "merged directories do not bind one valid analysis commit"
        )
    for tune in config.get("PYTHIA_TUNES", []):
        tune_rows = [row for row in merged if row.get("tune") == tune]
        if (
            not any(row.get("kind") == "central" for row in tune_rows)
            or {
                row.get("block")
                for row in tune_rows
                if row.get("kind") == "block"
            }
            != set(range(1, 11))
        ):
            raise ProvenanceFailure(
                f"merged input provenance lacks central/ten blocks for {tune}"
            )
    return {
        "input_mode": "canonical_merged_pairs_v2",
        "canonical_manifest": canonical,
        "canonical_freeze": freeze,
        "block_manifests": block_bindings,
        "analysis_commit": next(iter(analysis_commits)),
        "jobs_per_tune": jobs_per_tune,
        "manifest_tune_counts": manifest_tune_counts,
        "merged_directories": merged,
        "exact_inputs": sorted(
            deduplicated.values(), key=lambda value: value["path"]
        ),
        "exact_input_count": len(deduplicated),
        "exact_input_inventory_sha256": canonical_digest(
            sorted(deduplicated.values(), key=lambda value: value["path"])
        ),
    }


def canonical_raw_inputs(
    checkout: Path,
    row: dict[str, Any],
    production_root_override: str | None,
) -> dict[str, Any]:
    manifest_value = row.get("canonical_manifest")
    production_value = production_root_override or row.get("production_root")
    if (
        not isinstance(manifest_value, str)
        or not manifest_value
        or not isinstance(production_value, str)
        or not production_value
    ):
        raise ProvenanceFailure(
            "canonical raw plot requires manifest and production root"
        )
    manifest = resolve(manifest_value, checkout)
    freeze = canonical_freeze_binding(manifest, checkout)
    production = resolve(production_value, checkout)
    rows = load_jsonl(manifest, "canonical raw manifest")
    exact = []
    commits = set()
    per_tune = {tune: 0 for tune in TUNES}
    for row_value in rows:
        tune = row_value.get("tune")
        relative = row_value.get("raw_path")
        claimed = row_value.get("raw_sha256")
        claimed_bytes = row_value.get("raw_bytes")
        if (
            tune not in TUNES
            or not isinstance(relative, str)
            or Path(relative).is_absolute()
            or ".." in Path(relative).parts
            or not HEX64.fullmatch(str(claimed))
            or isinstance(claimed_bytes, bool)
            or not isinstance(claimed_bytes, int)
        ):
            raise ProvenanceFailure("canonical raw manifest row is invalid")
        path = production / relative
        require_regular(path, "canonical raw plot input")
        if path.stat().st_size != claimed_bytes or sha256(path) != claimed:
            raise ProvenanceFailure(f"canonical raw input changed: {path}")
        exact.append(
            {
                "path": display_path(path, checkout),
                "bytes": claimed_bytes,
                "sha256": claimed,
            }
        )
        commits.add(row_value.get("repository_commit"))
        per_tune[tune] += 1
    counts = set(per_tune.values())
    if (
        len(counts) != 1
        or next(iter(counts)) < 100
        or next(iter(counts)) % 10 != 0
        or len(commits) != 1
        or not HEX40.fullmatch(str(next(iter(commits), "")))
    ):
        raise ProvenanceFailure(
            "canonical raw plot manifest has unequal/invalid tune scope"
        )
    blocks = []
    block_paths = []
    for block in range(1, 11):
        block_path = manifest.parent / f"block_{block:02d}.jsonl"
        block_paths.append(block_path)
        blocks.append(
            manifest_binding(block_path, checkout, f"block_{block:02d}")
        )
    jobs_per_tune, _ = validate_canonical_block_partition(
        manifest, block_paths
    )
    exact.sort(key=lambda value: value["path"])
    return {
        "input_mode": "sealed_canonical_raw_manifest_v2",
        "canonical_manifest": manifest_binding(
            manifest, checkout, "canonical_manifest"
        ),
        "canonical_freeze": freeze,
        "block_manifests": blocks,
        "analysis_commit": None,
        "production_commit": next(iter(commits)),
        "jobs_per_tune": jobs_per_tune,
        "per_tune_input_count": per_tune,
        "exact_inputs": exact,
        "exact_input_count": len(exact),
        "exact_input_inventory_sha256": canonical_digest(exact),
    }


def legacy_pair_inputs(
    *,
    checkout: Path,
    config: dict[str, Any],
    analyzed_data_base: str | None,
    complete_root_tag: str | None,
    subsample_base: str | None,
) -> dict[str, Any]:
    base = resolve(
        analyzed_data_base or str(config.get("base_dir", "")), checkout
    )
    exact: dict[str, dict[str, Any]] = {}
    for key, tag_field, block_field in (
        (
            "beauty_correlations_to_analyse",
            "bb_bar_complete_root_dir",
            "bb_bar_complete_root_dir_sub_samples",
        ),
        (
            "charm_correlations_to_analyse",
            "cc_bar_complete_root_dir",
            "cc_bar_complete_root_dir_sub_samples",
        ),
    ):
        tag = complete_root_tag or str(config.get(tag_field, ""))
        block_base = resolve(
            subsample_base or str(config.get(block_field, "")), checkout
        )
        names = {
            pair[field]
            for group in config.get(key, [])
            for pair in group.get("configs", [])
            for field in ("OS", "SS")
            if isinstance(pair.get(field), str)
        }
        if not names:
            raise ProvenanceFailure(f"legacy plot configuration lacks {key}")
        for tune in config.get("PYTHIA_TUNES", []):
            for name in sorted(names):
                path = resolve_central(base, tune, tag, name)
                exact[str(path)] = file_record(path, checkout)
                for block in range(1, 11):
                    path = resolve_block(block_base, tune, block, name)
                    exact[str(path)] = file_record(path, checkout)
    values = sorted(exact.values(), key=lambda value: value["path"])
    return {
        "input_mode": "legacy_pair_regression",
        "canonical_manifest": {
            "status": "NOT_AVAILABLE_FOR_LEGACY_INPUT"
        },
        "block_manifests": [
            {
                "block": block,
                "status": "NOT_AVAILABLE_FOR_LEGACY_INPUT",
            }
            for block in range(1, 11)
        ],
        "analysis_commit": None,
        "manifest_limitation": (
            "The dated metadata-free input predates sealed canonical and "
            "block manifests; hashes below identify files but do not "
            "establish publication provenance."
        ),
        "exact_inputs": values,
        "exact_input_count": len(values),
        "exact_input_inventory_sha256": canonical_digest(values),
    }


def gate_d_inputs(
    checkout: Path,
    pair_inventory_path: Path,
    pilot_manifest_path: Path | None,
) -> dict[str, Any]:
    rows = load_jsonl(pair_inventory_path, "Gate-D pair inventory")
    analysis = pair_inventory_path.parent
    exact = []
    block_groups: dict[int | None, list[dict[str, Any]]] = {
        None: [],
        **{block: [] for block in range(1, 11)},
    }
    for row in rows:
        relative = row.get("path")
        if (
            not isinstance(relative, str)
            or Path(relative).is_absolute()
            or ".." in Path(relative).parts
            or not HEX64.fullmatch(str(row.get("sha256")))
            or isinstance(row.get("bytes"), bool)
            or not isinstance(row.get("bytes"), int)
        ):
            raise ProvenanceFailure("Gate-D pair inventory row is invalid")
        path = analysis / relative
        require_regular(path, "Gate-D pair input")
        if (
            path.stat().st_size != row["bytes"]
            or sha256(path) != row["sha256"]
        ):
            raise ProvenanceFailure(f"Gate-D pair input changed: {path}")
        binding = {
            "path": display_path(path, checkout),
            "bytes": row["bytes"],
            "sha256": row["sha256"],
        }
        exact.append(binding)
        match = re.search(r"/combined_root_([1-9]|10)/", f"/{relative}/")
        block_groups[int(match.group(1)) if match else None].append(binding)
    if len(block_groups[None]) != 900 or any(
        len(block_groups[block]) != 900 for block in range(1, 11)
    ):
        raise ProvenanceFailure(
            "Gate-D pair inventory is not 900 central plus 900 per block"
        )
    exact.sort(key=lambda value: value["path"])
    pilot = (
        manifest_binding(pilot_manifest_path, checkout, "gate_b_pilot_manifest")
        if pilot_manifest_path is not None
        else {"status": "NOT_PROVIDED"}
    )
    return {
        "input_mode": "gate_d_one_million_pilot_pairs",
        "canonical_manifest": {
            "status": "PILOT_NOT_FINAL_CANONICAL_MANIFEST",
            "pilot_manifest": pilot,
        },
        "block_manifests": [
            {
                "block": block,
                "status": "PILOT_PAIR_INVENTORY_DIGEST_NOT_MANIFEST",
                "input_count": len(block_groups[block]),
                "sha256": canonical_digest(
                    sorted(
                        block_groups[block], key=lambda value: value["path"]
                    )
                ),
            }
            for block in range(1, 11)
        ],
        "analysis_commit": git(checkout, "rev-parse", "HEAD"),
        "pair_inventory": file_record(pair_inventory_path, checkout),
        "exact_inputs": exact,
        "exact_input_count": len(exact),
        "exact_input_inventory_sha256": canonical_digest(exact),
        "publication_limitation": (
            "Gate-D plots are one-million-event pilot validation artifacts, "
            "not final canonical paper plots."
        ),
    }


def boundary_receipt_binding(
    path: Path, config_path: Path, checkout: Path
) -> dict[str, Any]:
    receipt = load_json(path, "multiplicity-boundary receipt")
    claimed_payload_sha256 = receipt.get("payload_sha256")
    payload = dict(receipt)
    payload.pop("payload_sha256", None)
    if (
        receipt.get("schema")
        != "hadronization_multiplicity_boundary_receipt_v1"
        or receipt.get("schema_version") != 1
        or receipt.get("algorithm")
        != "ascending_discrete_weighted_quantile_v1"
        or receipt.get("completion_status") != "PASS"
        or receipt.get("configuration_path")
        != display_path(config_path, checkout)
        or receipt.get("configuration_sha256") != sha256(config_path)
        or receipt.get("plotter_source_sha256")
        != sha256(checkout / "PlottingScripts/improvedPlotting_THnSparse.C")
        or receipt.get("boundary_utility_sha256")
        != sha256(checkout / "PlottingScripts/MultiplicityBoundaryUtils.h")
        or not HEX64.fullmatch(str(claimed_payload_sha256 or ""))
        or claimed_payload_sha256 != canonical_digest(payload)
        or not isinstance(receipt.get("tunes"), dict)
        or set(receipt["tunes"]) != set(TUNES)
    ):
        raise ProvenanceFailure(
            "multiplicity-boundary receipt is incomplete/stale"
        )
    for tune, value in receipt["tunes"].items():
        if not isinstance(value, dict):
            raise ProvenanceFailure(
                f"multiplicity-boundary tune receipt is invalid: {tune}"
            )
        source = Path(str(value.get("central_reference_path", "")))
        if (
            not source.is_absolute()
            or not source.is_file()
            or source.is_symlink()
            or sha256(source)
            != value.get("central_source_file_sha256")
        ):
            raise ProvenanceFailure(
                f"multiplicity-boundary source changed: {tune}"
            )
    return {
        **file_record(path, checkout),
        "payload_sha256": receipt["payload_sha256"],
        "algorithm": receipt.get("algorithm"),
        "configuration_sha256": receipt["configuration_sha256"],
    }


def auto_boundary_path(config: dict[str, Any], checkout: Path) -> Path:
    directories = {
        resolve(row["write_path"], checkout)
        for row in config.get("global_canvases_to_be_drawn", [])
        if isinstance(row, dict)
        and row.get("write") is True
        and isinstance(row.get("write_path"), str)
        and row["write_path"] not in ("", "NONE")
    }
    if len(directories) != 1:
        raise ProvenanceFailure(
            "cannot uniquely resolve multiplicity-boundary receipt"
        )
    return next(iter(directories)) / "multiplicity_boundary_receipt_v1.json"


def generator_bindings(
    checkout: Path, target: str, config_path: Path | None
) -> list[dict[str, Any]]:
    relative_paths = ["PlottingScripts/TunePlotStyle.h"]
    if (
        target.startswith("thnsparse")
        or target.startswith("gate-d")
        or target == "legacy-regression"
    ):
        relative_paths.extend(
            [
                "PlottingScripts/improvedPlotting_THnSparse.C",
                "PlottingScripts/MultiplicityBoundaryUtils.h",
                "PlottingScripts/PairInputSelectionUtils.h",
            ]
        )
    elif target.startswith("multiplicity-boundaries"):
        relative_paths.extend(
            [
                "PlottingScripts/Plot_MultiplicityDistribution_PercentileBoundaries.C",
                "PlottingScripts/MultiplicityBoundaryUtils.h",
            ]
        )
    elif target in ("kinematic-spectra", "multiplicity-spectrum"):
        relative_paths.append(
            "PlottingScripts/Plot_InclusiveKinematicSpectra_Raw.C"
        )
    bindings = [
        file_record(checkout / relative, checkout) for relative in relative_paths
    ]
    if config_path is not None:
        bindings.append(file_record(config_path, checkout))
    return bindings


def contract_binding(
    mode: str,
    dataset: dict[str, Any],
    config: dict[str, Any] | None,
) -> dict[str, Any]:
    def multiplicity_value(
        row: dict[str, Any],
        canonical_key: str,
        compatibility_key: str,
    ) -> int | float:
        has_canonical = canonical_key in row
        has_compatibility = compatibility_key in row
        if not has_canonical and not has_compatibility:
            raise ProvenanceFailure(
                "plot histogram definition lacks multiplicity range key "
                f"{canonical_key!r}"
            )
        if (
            has_canonical
            and has_compatibility
            and row[canonical_key] != row[compatibility_key]
        ):
            raise ProvenanceFailure(
                "plot histogram definition has conflicting multiplicity "
                f"range values for {canonical_key!r} and "
                f"{compatibility_key!r}"
            )
        value = (
            row[canonical_key]
            if has_canonical
            else row[compatibility_key]
        )
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or (isinstance(value, float) and not math.isfinite(value))
        ):
            raise ProvenanceFailure(
                "plot histogram definition has a non-finite/non-numeric "
                f"{canonical_key!r}"
            )
        return value

    if config is not None:
        return {
            "raw_schema": dataset.get("raw_schema"),
            "dataset_selector": dataset.get("selector"),
            "pair_input_selection_contract":
                config.get("pair_input_selection_contract"),
            "pair_combinatorics_mode":
                config.get("pair_combinatorics_mode"),
            "same_sign_pair_factor": config.get("same_sign_pair_factor"),
            "n_subsamples": config.get("nSubSamples"),
            "calculate_errors": config.get("calculate_errors"),
            "multiplicity_classes": [
                {
                    "name": row.get("hDPhi"),
                    "minimum": multiplicity_value(
                        row, "multiplicityMin", "multiplicity_min"
                    ),
                    "maximum": multiplicity_value(
                        row, "multiplicityMax", "multiplicity_max"
                    ),
                }
                for row in config.get("histograms_to_analyse", [])
                if isinstance(row, dict)
            ],
        }
    if mode in ("canonical-raw", "canonical-validation-raw"):
        return {
            "raw_schema": dataset.get("raw_schema"),
            "dataset_selector": dataset.get("selector"),
            "plot_selection_contract":
                "inclusive_direct_primary_ground_raw_v5_v1",
            "particle_pt_min_exclusive_gev": 0.15,
            "particle_eta_abs_max_inclusive": 4.0,
            "origin_policy": "inclusive_all_origins",
            "pair_conditioning": "none",
        }
    return {
        "plot_selection_contract": "legacy_unsealed_diagnostic",
    }


def provenance_location(path: Path, checkout: Path) -> str:
    return display_path(path, checkout)


def command_record(args: argparse.Namespace) -> int:
    checkout = args.checkout.resolve()
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", args.target):
        raise ProvenanceFailure(f"unsafe plot target name: {args.target!r}")
    snapshot = load_json(args.state.resolve(), "plot-output snapshot")
    roots = [Path(value).resolve() for value in snapshot.get("roots", [])]
    if not roots or str(checkout) != snapshot.get("checkout"):
        raise ProvenanceFailure("snapshot checkout/root binding differs")
    changed = changed_outputs(snapshot, roots)
    require_triplets(changed)

    config_path = args.config.resolve() if args.config else None
    config = (
        load_json(config_path, "executed plot configuration")
        if config_path is not None
        else None
    )
    dataset, selector_row = selector_binding(args.selector, checkout)
    publication_eligible = dataset["publication_eligible"]
    if args.mode in (
        "canonical-validation-pair",
        "canonical-validation-raw",
        "legacy-pair",
        "legacy-unsealed",
        "gate-d",
    ):
        publication_eligible = False
    checkout_info = checkout_binding(
        checkout, publication_eligible, args.development
    )

    if args.mode == "canonical-pair":
        if (
            selector_row is None
            or dataset.get("status") != "canonical"
            or dataset.get("publication_eligible") is not True
            or config is None
        ):
            raise ProvenanceFailure(
                "canonical pair provenance requires an eligible selector/config"
            )
        inputs = canonical_pair_inputs(
            checkout=checkout,
            config_path=config_path,
            config=config,
            row=selector_row,
            analyzed_data_base=args.analyzed_data_base,
            complete_root_tag=args.complete_root_tag,
            subsample_base=args.subsample_base,
        )
    elif args.mode == "canonical-validation-pair":
        if (
            selector_row is None
            or dataset.get("status")
            not in {"canonical_candidate", "canonical"}
            or dataset.get("publication_eligible") not in {False, True}
            or config is None
        ):
            raise ProvenanceFailure(
                "canonical validation pair provenance requires a canonical "
                "candidate/eligible selector and config"
            )
        inputs = canonical_pair_inputs(
            checkout=checkout,
            config_path=config_path,
            config=config,
            row=selector_row,
            analyzed_data_base=args.analyzed_data_base,
            complete_root_tag=args.complete_root_tag,
            subsample_base=args.subsample_base,
        )
    elif args.mode == "canonical-raw":
        if (
            selector_row is None
            or dataset.get("status") != "canonical"
            or dataset.get("publication_eligible") is not True
        ):
            raise ProvenanceFailure(
                "canonical raw provenance requires an eligible selector"
            )
        inputs = canonical_raw_inputs(
            checkout, selector_row, args.production_root
        )
    elif args.mode == "canonical-validation-raw":
        if (
            selector_row is None
            or dataset.get("status")
            not in {"canonical_candidate", "canonical"}
        ):
            raise ProvenanceFailure(
                "canonical validation raw provenance requires a canonical "
                "candidate/eligible selector"
            )
        inputs = canonical_raw_inputs(
            checkout, selector_row, args.production_root
        )
    elif args.mode == "legacy-pair":
        if config is None:
            raise ProvenanceFailure("legacy pair provenance requires config")
        if dataset.get("publication_eligible") is not False:
            raise ProvenanceFailure("legacy products cannot be eligible")
        inputs = legacy_pair_inputs(
            checkout=checkout,
            config=config,
            analyzed_data_base=args.analyzed_data_base,
            complete_root_tag=args.complete_root_tag,
            subsample_base=args.subsample_base,
        )
    elif args.mode == "gate-d":
        if args.pair_inventory is None:
            raise ProvenanceFailure("Gate-D provenance requires pair inventory")
        inputs = gate_d_inputs(
            checkout,
            args.pair_inventory.resolve(),
            args.pilot_manifest.resolve() if args.pilot_manifest else None,
        )
    else:
        inputs = {
            "input_mode": "legacy_unsealed_diagnostic",
            "canonical_manifest": {"status": "NOT_AVAILABLE"},
            "block_manifests": [
                {"block": value, "status": "NOT_AVAILABLE"}
                for value in range(1, 11)
            ],
            "analysis_commit": None,
            "exact_inputs": [],
            "exact_input_count": 0,
            "exact_input_inventory_sha256": canonical_digest([]),
            "publication_limitation":
                "This target is not a current publication pipeline.",
        }

    if args.mode in (
        "canonical-validation-pair",
        "canonical-validation-raw",
    ):
        inputs["publication_limitation"] = (
            "Prepublication canonical validation artifact. It is deliberately "
            "ineligible and must be regenerated after exact scientific-review "
            "and project-owner dataset authorization."
        )

    if args.mode in ("canonical-pair", "canonical-raw"):
        eligibility = dataset.get("publication_eligibility_evidence")
        canonical_manifest = inputs.get("canonical_manifest")
        canonical_freeze = inputs.get("canonical_freeze")
        if (
            not isinstance(eligibility, dict)
            or not isinstance(canonical_manifest, dict)
            or eligibility.get("canonical_manifest_sha256")
            != canonical_manifest.get("sha256")
            or not isinstance(canonical_freeze, dict)
            or eligibility.get("freeze_seal_sha256")
            != canonical_freeze.get("seal", {}).get("sha256")
        ):
            raise ProvenanceFailure(
                "publication authorization does not bind the exact plotted "
                "canonical freeze"
            )

    boundary = None
    if args.require_boundary_receipt:
        if config is None or config_path is None:
            raise ProvenanceFailure(
                "boundary receipt requires an exact plot configuration"
            )
        boundary_path = (
            auto_boundary_path(config, checkout)
            if args.require_boundary_receipt == "auto"
            else resolve(args.require_boundary_receipt, checkout)
        )
        boundary = boundary_receipt_binding(
            boundary_path, config_path, checkout
        )

    output_rows = [file_record(path, checkout) for path in changed]
    for output in output_rows:
        output_path = resolve(output["path"], checkout)
        sidecar = Path(f"{output_path}.provenance.json")
        if sidecar.exists() and (
            sidecar.is_symlink() or not sidecar.is_file()
        ):
            raise ProvenanceFailure(
                f"refusing to replace unsafe output sidecar: {sidecar}"
            )
    primary_root = next(
        root for root in roots if any(root in path.parents for path in changed)
    )
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_identity = f"{stamp}_{args.target}_{uuid.uuid4().hex[:12]}"
    provenance_directory = primary_root / "provenance"
    receipt_path = provenance_directory / f"{run_identity}.json"
    configuration_record = None
    configuration_generator = None
    if config_path is not None and config is not None:
        archived_config = (
            provenance_directory
            / f"{run_identity}.configuration.snapshot"
        )
        exclusive_copy(config_path, archived_config)
        archived_binding = file_record(archived_config, checkout)
        configuration_record = {
            "source_path_at_execution": display_path(config_path, checkout),
            "archived_binding": archived_binding,
            "payload": config,
        }
        configuration_generator = archived_binding
    generators = generator_bindings(checkout, args.target, None)
    if configuration_generator is not None:
        generators.append(configuration_generator)
    run = {
        "schema": RUN_SCHEMA,
        "state": "PASS",
        "publication_eligible": publication_eligible,
        "target": args.target,
        "command": args.command,
        "created_utc": utc_now(),
        "checkout": checkout_info,
        "dataset": dataset,
        "configuration": configuration_record,
        "contracts": contract_binding(args.mode, dataset, config),
        "generators": generators,
        "inputs": inputs,
        "multiplicity_boundary_receipt": boundary,
        "outputs": output_rows,
    }
    atomic_json(receipt_path, run, exclusive=True)
    receipt_binding = file_record(receipt_path, checkout)

    for output in output_rows:
        output_path = resolve(output["path"], checkout)
        sidecar = Path(f"{output_path}.provenance.json")
        value = {
            "schema": SCHEMA,
            "state": "PASS",
            "publication_eligible": publication_eligible,
            "output": output,
            "target": args.target,
            "command": args.command,
            "created_utc": run["created_utc"],
            "plotting_commit": checkout_info["plotting_commit"],
            "analysis_commit": inputs.get("analysis_commit"),
            "production_commit": inputs.get("production_commit"),
            "selection_cut_schema_versions": run["contracts"],
            "configuration": run["configuration"],
            "publication_eligibility":
                dataset.get("publication_eligibility_evidence"),
            "canonical_manifest": inputs.get("canonical_manifest"),
            "canonical_freeze": inputs.get("canonical_freeze"),
            "block_manifests": inputs.get("block_manifests"),
            "exact_input_count": inputs.get("exact_input_count"),
            "exact_input_inventory_sha256":
                inputs.get("exact_input_inventory_sha256"),
            "multiplicity_boundary_receipt": boundary,
            "run_receipt": receipt_binding,
        }
        atomic_json(sidecar, value, exclusive=False)

    print(
        "FINAL_PLOT_PROVENANCE_PASS "
        f"target={args.target} outputs={len(output_rows)} "
        f"inputs={inputs.get('exact_input_count')} "
        f"publication_eligible={str(publication_eligible).lower()} "
        f"receipt={receipt_path}"
    )
    return 0


def verify_file_record(
    record: dict[str, Any], checkout: Path, label: str
) -> Path:
    path_value = record.get("path")
    if not isinstance(path_value, str):
        raise ProvenanceFailure(f"{label} has no path")
    path = resolve(path_value, checkout)
    require_regular(path, label)
    if (
        path.stat().st_size != record.get("bytes")
        or sha256(path) != record.get("sha256")
    ):
        raise ProvenanceFailure(f"{label} checksum/size differs: {path}")
    return path


def command_verify(args: argparse.Namespace) -> int:
    checkout = args.checkout.resolve()
    sidecar = load_json(args.sidecar.resolve(), "plot provenance sidecar")
    if sidecar.get("schema") != SCHEMA or sidecar.get("state") != "PASS":
        raise ProvenanceFailure("unsupported/failed plot sidecar")
    output_path = verify_file_record(sidecar["output"], checkout, "plot output")
    receipt_path = verify_file_record(
        sidecar["run_receipt"], checkout, "plot run receipt"
    )
    run = load_json(receipt_path, "plot run receipt")
    if (
        run.get("schema") != RUN_SCHEMA
        or run.get("state") != "PASS"
        or run.get("target") != sidecar.get("target")
        or run.get("command") != sidecar.get("command")
        or run.get("publication_eligible")
        != sidecar.get("publication_eligible")
    ):
        raise ProvenanceFailure("sidecar/run receipt binding differs")
    matching = [
        row
        for row in run.get("outputs", [])
        if isinstance(row, dict)
        and resolve(str(row.get("path", "")), checkout) == output_path
    ]
    if len(matching) != 1 or matching[0] != sidecar["output"]:
        raise ProvenanceFailure("run receipt does not uniquely bind output")
    inputs = run.get("inputs")
    if not isinstance(inputs, dict):
        raise ProvenanceFailure("run receipt has no input inventory")
    exact = inputs.get("exact_inputs")
    if not isinstance(exact, list) or canonical_digest(exact) != inputs.get(
        "exact_input_inventory_sha256"
    ):
        raise ProvenanceFailure("exact input inventory digest differs")
    for record in exact:
        if not isinstance(record, dict):
            raise ProvenanceFailure("exact input inventory row is invalid")
        verify_file_record(record, checkout, "plot input")
    if sidecar.get("exact_input_inventory_sha256") != inputs.get(
        "exact_input_inventory_sha256"
    ):
        raise ProvenanceFailure("sidecar exact-input digest differs")
    for record in run.get("generators", []):
        if not isinstance(record, dict):
            raise ProvenanceFailure("generator inventory row is invalid")
        verify_file_record(record, checkout, "plot generator")
    configuration = run.get("configuration")
    if configuration is not None:
        if not isinstance(configuration, dict) or not isinstance(
            configuration.get("archived_binding"), dict
        ):
            raise ProvenanceFailure("archived configuration binding is invalid")
        archived = verify_file_record(
            configuration["archived_binding"],
            checkout,
            "archived plot configuration",
        )
        if load_json(archived, "archived plot configuration") != (
            configuration.get("payload")
        ):
            raise ProvenanceFailure(
                "archived configuration payload differs from run receipt"
            )
    dataset_document = run.get("dataset", {}).get("selector_document")
    if isinstance(dataset_document, dict):
        selector_path = verify_file_record(
            dataset_document, checkout, "dataset selector"
        )
        try:
            _, verified_dataset = dataset_contract.load(
                selector_path, checkout
            )
        except (OSError, ValueError) as error:
            raise ProvenanceFailure(
                f"dataset publication authorization no longer validates: "
                f"{error}"
            ) from error
        if (
            verified_dataset.get("publication_eligibility_evidence")
            != run.get("dataset", {}).get(
                "publication_eligibility_evidence"
            )
        ):
            raise ProvenanceFailure(
                "dataset publication-eligibility evidence differs"
            )
    for record in (
        [inputs.get("canonical_manifest")]
        + list(inputs.get("block_manifests", []))
    ):
        if isinstance(record, dict) and isinstance(record.get("path"), str):
            verify_file_record(record, checkout, "central/block manifest")
    freeze = inputs.get("canonical_freeze")
    if isinstance(freeze, dict):
        for key in (
            "summary",
            "seal",
            "validation_receipt",
            "validation_log",
        ):
            verify_file_record(
                freeze.get(key, {}), checkout, f"canonical freeze {key}"
            )
    for directory in inputs.get("merged_directories", []):
        if not isinstance(directory, dict):
            raise ProvenanceFailure("merged-directory binding is invalid")
        for key in (
            "merge_provenance",
            "root_checksum_inventory",
            "source_manifest",
        ):
            verify_file_record(
                directory.get(key, {}),
                checkout,
                f"merged-directory {key}",
            )
    pair_inventory = inputs.get("pair_inventory")
    if isinstance(pair_inventory, dict):
        verify_file_record(pair_inventory, checkout, "pair input inventory")
    boundary = run.get("multiplicity_boundary_receipt")
    if boundary is not None:
        verify_file_record(boundary, checkout, "multiplicity receipt")
    if (
        sidecar.get("canonical_manifest")
        != inputs.get("canonical_manifest")
        or sidecar.get("canonical_freeze")
        != inputs.get("canonical_freeze")
        or sidecar.get("block_manifests")
        != inputs.get("block_manifests")
        or sidecar.get("publication_eligibility")
        != run.get("dataset", {}).get(
            "publication_eligibility_evidence"
        )
        or sidecar.get("configuration") != configuration
        or sidecar.get("multiplicity_boundary_receipt") != boundary
    ):
        raise ProvenanceFailure("sidecar/run scientific bindings differ")
    print(
        "FINAL_PLOT_PROVENANCE_VALID "
        f"output={output_path} inputs={len(exact)}"
    )
    return 0


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    commands = value.add_subparsers(required=True)

    snapshot = commands.add_parser("snapshot")
    snapshot.add_argument("--checkout", type=Path, required=True)
    snapshot.add_argument("--state", type=Path, required=True)
    snapshot.add_argument("--config", type=Path)
    snapshot.add_argument("--output-root", action="append", default=[])
    snapshot.set_defaults(function=command_snapshot)

    record = commands.add_parser("record")
    record.add_argument("--checkout", type=Path, required=True)
    record.add_argument("--state", type=Path, required=True)
    record.add_argument("--target", required=True)
    record.add_argument("--command", required=True)
    record.add_argument(
        "--mode",
        required=True,
        choices=(
            "canonical-pair",
            "canonical-validation-pair",
            "canonical-raw",
            "canonical-validation-raw",
            "legacy-pair",
            "legacy-unsealed",
            "gate-d",
        ),
    )
    record.add_argument("--selector", type=Path)
    record.add_argument("--config", type=Path)
    record.add_argument("--analyzed-data-base")
    record.add_argument("--complete-root-tag")
    record.add_argument("--subsample-base")
    record.add_argument("--production-root")
    record.add_argument("--pair-inventory", type=Path)
    record.add_argument("--pilot-manifest", type=Path)
    record.add_argument(
        "--require-boundary-receipt",
        nargs="?",
        const="auto",
    )
    record.add_argument("--development", action="store_true")
    record.set_defaults(function=command_record)

    verify = commands.add_parser("verify")
    verify.add_argument("--checkout", type=Path, required=True)
    verify.add_argument("--sidecar", type=Path, required=True)
    verify.set_defaults(function=command_verify)
    return value


def main() -> int:
    args = parser().parse_args()
    try:
        return args.function(args)
    except (OSError, subprocess.CalledProcessError, ProvenanceFailure) as error:
        print(f"FINAL_PLOT_PROVENANCE_ERROR: {error}", file=os.sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
