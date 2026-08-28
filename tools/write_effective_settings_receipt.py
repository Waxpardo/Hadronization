#!/usr/bin/env python3
"""Audit three exhaustive post-init PYTHIA settings snapshots.

The ROOT loader is deliberately separate from ``compare_effective_settings``.
Tests exercise the complete comparison contract with synthetic source records;
campaign use loads the producer's ``effective_settings`` tree and immutable
``job_metadata`` directly from one raw file per published tune.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any

RECEIPT_SCHEMA = "hadronization_effective_tune_settings_receipt_v1"
RAW_SCHEMA = "hf_primary_ground_raw_v7"
EFFECTIVE_SETTINGS_SCHEMA = "effective_pythia_settings_exhaustive_v2"
ALLOWLIST_SCHEMA = "pythia_tune_difference_allowlist_v2"
TUNES = ("MONASH", "JUNCTIONS", "CLOSEPACKING")
HEX40 = re.compile(r"[0-9a-f]{40}")
HEX64 = re.compile(r"[0-9a-f]{64}")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(16 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _cpp_quoted(value: str) -> str:
    """C++ ``std::quoted(value)`` with its default delimiter and escape."""
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def serialize_effective_settings(rows: list[tuple[str, str]],
                                 schema: str = EFFECTIVE_SETTINGS_SCHEMA
                                 ) -> bytes:
    """The producer's committed ``SerializeEffectiveSettings`` byte rule."""
    text = f"schema={schema}\n"
    text += "".join(
        f"{_cpp_quoted(name)}\t{_cpp_quoted(value)}\n"
        for name, value in rows)
    return text.encode("utf-8")


def effective_settings_digest(rows: list[tuple[str, str]],
                              schema: str = EFFECTIVE_SETTINGS_SCHEMA) -> str:
    return hashlib.sha256(serialize_effective_settings(rows, schema)).hexdigest()


def _root_string_object(root_file: Any, name: str) -> str:
    obj = root_file.Get(name)
    if not obj or not hasattr(obj, "GetString"):
        raise ValueError(f"missing TObjString {name}")
    return str(obj.GetString())


def load_root_source(path: Path, expected_tune: str) -> dict[str, Any]:
    """Load one raw ROOT file into comparison facts, without interpreting cards."""
    basename = path.name
    if not path.is_file():
        raise ValueError(f"{basename}: input is not a regular file")
    file_sha = sha256_file(path)
    try:
        import ROOT  # type: ignore
    except ImportError as error:
        raise RuntimeError("PyROOT is unavailable") from error

    ROOT.gROOT.SetBatch(True)
    root_file = ROOT.TFile.Open(str(path), "READ")
    if not root_file or root_file.IsZombie():
        raise ValueError(f"{basename}: ROOT could not open the input")
    try:
        metadata = root_file.Get("job_metadata")
        if not metadata or metadata.GetEntries() != 1:
            raise ValueError(f"{basename}: job_metadata must contain exactly one row")
        metadata.GetEntry(0)

        def field(name: str) -> Any:
            if not metadata.GetBranch(name):
                raise ValueError(f"{basename}: job_metadata lacks {name}")
            return getattr(metadata, name)

        settings_tree = root_file.Get("effective_settings")
        if not settings_tree or settings_tree.GetEntries() <= 0:
            raise ValueError(f"{basename}: effective_settings tree is absent or empty")
        if not settings_tree.GetBranch("name") or not settings_tree.GetBranch("value"):
            raise ValueError(f"{basename}: effective_settings lacks name/value branches")
        settings: list[tuple[str, str]] = []
        for index in range(int(settings_tree.GetEntries())):
            settings_tree.GetEntry(index)
            settings.append((str(settings_tree.name), str(settings_tree.value)))

        return {
            "expected_tune": expected_tune,
            "basename": basename,
            "sha256": file_sha,
            "observed_tune": str(field("tune")),
            "raw_schema": str(field("raw_schema")),
            "tune_difference_allowlist_schema": str(
                field("tune_difference_allowlist_schema")),
            "tune_difference_allowlist_sha256": str(
                field("tune_difference_allowlist_sha256")),
            "effective_settings_schema": str(field("effective_settings_schema")),
            "effective_settings_sha256": str(field("effective_settings_sha256")),
            "effective_settings_entries": int(field("effective_settings_entries")),
            "repository_commit": str(field("repository_commit")),
            "repository_dirty": str(field("repository_dirty")),
            "complete": int(field("complete")),
            "settings": settings,
            "effective_settings_canonical_object": _root_string_object(
                root_file, "effective_settings_canonical"),
            "effective_settings_sha256_object": _root_string_object(
                root_file, "effective_settings_sha256"),
        }
    finally:
        root_file.Close()


def _equivalent_required_value(observed: str, required: str) -> bool:
    """Compare PYTHIA output spelling with a required card-value spelling."""
    if observed == required:
        return True
    if observed.lower() in {"on", "off"} or required.lower() in {"on", "off"}:
        return observed.lower() == required.lower()
    observed_parts = observed.split(",")
    required_parts = required.split(",")
    if len(observed_parts) != len(required_parts):
        return False
    try:
        return all(
            math.isfinite(float(left)) and math.isfinite(float(right))
            and float(left) == float(right)
            for left, right in zip(observed_parts, required_parts))
    except ValueError:
        return False


def _validate_allowlist(allowlist: dict[str, Any], errors: list[str]
                        ) -> tuple[set[str], set[str], dict[str, str]]:
    if allowlist.get("schema") != ALLOWLIST_SCHEMA:
        errors.append(
            f"allowlist schema is {allowlist.get('schema')!r}, expected "
            f"{ALLOWLIST_SCHEMA!r}")

    def names(field: str) -> set[str]:
        values = allowlist.get(field)
        if not isinstance(values, list) or any(
                not isinstance(value, str) or not value for value in values):
            errors.append(f"allowlist {field} must be a list of nonempty strings")
            return set()
        if len(values) != len(set(values)):
            errors.append(f"allowlist {field} contains duplicate names")
        return set(values)

    tune_allowed = names("allowed_tune_differences")
    per_job = names("allowed_per_job_differences")
    overlap = sorted(tune_allowed & per_job)
    if overlap:
        errors.append("allowlist tune/per-job classes overlap: " + ", ".join(overlap))
    required = allowlist.get("common_required_card_values")
    if not isinstance(required, dict) or any(
            not isinstance(key, str) or not key or not isinstance(value, str)
            for key, value in (required.items() if isinstance(required, dict) else [])):
        errors.append("allowlist common_required_card_values must be a string map")
        required = {}
    return tune_allowed, per_job, dict(required)


def _validate_source(tune: str, source: dict[str, Any], errors: list[str]
                     ) -> tuple[dict[str, Any], dict[str, str]]:
    prefix = f"{tune}"
    record = {
        "expected_tune": tune,
        "observed_tune": source.get("observed_tune"),
        "basename": source.get("basename"),
        "sha256": source.get("sha256"),
        "raw_schema": source.get("raw_schema"),
        "tune_difference_allowlist_schema": source.get(
            "tune_difference_allowlist_schema"),
        "tune_difference_allowlist_sha256": source.get(
            "tune_difference_allowlist_sha256"),
        "effective_settings_schema": source.get("effective_settings_schema"),
        "effective_settings_sha256": source.get("effective_settings_sha256"),
        "reconstructed_effective_settings_sha256": None,
        "effective_settings_entries": source.get("effective_settings_entries"),
        "complete": source.get("complete"),
        "repository_commit": source.get("repository_commit"),
        "repository_dirty": source.get("repository_dirty"),
    }
    if source.get("load_error"):
        errors.append(f"{prefix}: {source['load_error']}")
        return record, {}
    if source.get("observed_tune") != tune:
        errors.append(
            f"{prefix}: tune identity is {source.get('observed_tune')!r}, expected {tune!r}")
    basename = source.get("basename")
    if not isinstance(basename, str) or not basename or Path(basename).name != basename:
        errors.append(f"{prefix}: basename is absent or host-specific")
    if not isinstance(source.get("sha256"), str) or not HEX64.fullmatch(
            source.get("sha256", "")):
        errors.append(f"{prefix}: input SHA-256 is malformed")
    if source.get("raw_schema") != RAW_SCHEMA:
        errors.append(
            f"{prefix}: raw schema is {source.get('raw_schema')!r}, expected {RAW_SCHEMA!r}")
    embedded_allowlist_schema = source.get("tune_difference_allowlist_schema")
    if embedded_allowlist_schema is None:
        errors.append(f"{prefix}: embedded allowlist pin schema is absent")
    elif embedded_allowlist_schema != ALLOWLIST_SCHEMA:
        errors.append(
            f"{prefix}: embedded allowlist pin schema is "
            f"{embedded_allowlist_schema!r}, expected {ALLOWLIST_SCHEMA!r}")
    embedded_allowlist_sha = source.get("tune_difference_allowlist_sha256")
    if embedded_allowlist_sha is None:
        errors.append(f"{prefix}: embedded allowlist pin SHA-256 is absent")
    elif not isinstance(embedded_allowlist_sha, str) or not HEX64.fullmatch(
            embedded_allowlist_sha):
        errors.append(
            f"{prefix}: embedded allowlist pin SHA-256 is malformed: "
            f"{embedded_allowlist_sha!r}")
    schema = source.get("effective_settings_schema")
    if schema != EFFECTIVE_SETTINGS_SCHEMA:
        errors.append(
            f"{prefix}: effective-settings schema is {schema!r}, expected "
            f"{EFFECTIVE_SETTINGS_SCHEMA!r}")
    if source.get("complete") != 1:
        errors.append(f"{prefix}: job metadata complete is not 1")
    if source.get("repository_dirty") != "false":
        errors.append(f"{prefix}: repository_dirty is not false")
    if not isinstance(source.get("repository_commit"), str) or not HEX40.fullmatch(
            source.get("repository_commit", "")):
        errors.append(f"{prefix}: repository_commit is malformed")

    raw_rows = source.get("settings")
    if not isinstance(raw_rows, list) or not raw_rows:
        errors.append(f"{prefix}: effective_settings catalogue is absent or empty")
        return record, {}
    rows: list[tuple[str, str]] = []
    names: list[str] = []
    for index, row in enumerate(raw_rows):
        if (not isinstance(row, (list, tuple)) or len(row) != 2
                or not isinstance(row[0], str) or not row[0]
                or not isinstance(row[1], str)):
            errors.append(f"{prefix}: malformed effective_settings entry {index}")
            continue
        name, value = row
        rows.append((name, value))
        names.append(name)
    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        errors.append(
            f"{prefix}: duplicate effective_settings name(s): " + ", ".join(duplicates))
    if names != sorted(names):
        errors.append(f"{prefix}: effective_settings catalogue is not name-sorted")
    declared_count = source.get("effective_settings_entries")
    if not isinstance(declared_count, int) or declared_count != len(rows):
        errors.append(
            f"{prefix}: effective_settings_entries={declared_count!r}, tree has {len(rows)}")

    canonical = serialize_effective_settings(rows, EFFECTIVE_SETTINGS_SCHEMA)
    reconstructed = hashlib.sha256(canonical).hexdigest()
    record["reconstructed_effective_settings_sha256"] = reconstructed
    metadata_digest = source.get("effective_settings_sha256")
    if not isinstance(metadata_digest, str) or not HEX64.fullmatch(metadata_digest):
        errors.append(f"{prefix}: effective_settings_sha256 is malformed")
    elif metadata_digest != reconstructed:
        errors.append(
            f"{prefix}: effective_settings_sha256 does not match reconstructed digest")
    if source.get("effective_settings_sha256_object") != reconstructed:
        errors.append(f"{prefix}: effective_settings_sha256 object disagrees")
    canonical_object = source.get("effective_settings_canonical_object")
    if canonical_object != canonical.decode("utf-8"):
        errors.append(f"{prefix}: effective_settings_canonical object disagrees")
    return record, dict(rows)


def compare_effective_settings(
    sources: dict[str, dict[str, Any]],
    allowlist: dict[str, Any],
    allowlist_sha256: str,
    initial_errors: list[str] | None = None,
) -> dict[str, Any]:
    """Validate structure and compare resolved settings across all three tunes."""
    errors = list(initial_errors or [])
    extra = sorted(set(sources) - set(TUNES))
    missing = sorted(set(TUNES) - set(sources))
    if extra:
        errors.append("unexpected source tune(s): " + ", ".join(extra))
    if missing:
        errors.append("missing source tune(s): " + ", ".join(missing))
    if not HEX64.fullmatch(allowlist_sha256):
        errors.append("allowlist SHA-256 is malformed")
    tune_allowed, per_job, required = _validate_allowlist(allowlist, errors)

    inputs: dict[str, dict[str, Any]] = {}
    catalogues: dict[str, dict[str, str]] = {}
    for tune in TUNES:
        record, settings = _validate_source(tune, sources.get(tune, {}), errors)
        inputs[tune] = record
        catalogues[tune] = settings

    embedded_schemas = {
        tune: inputs[tune]["tune_difference_allowlist_schema"] for tune in TUNES
    }
    if len({(type(value).__name__, repr(value))
            for value in embedded_schemas.values()}) != 1:
        errors.append(
            "raw embedded allowlist pin schemas disagree across tunes: "
            + ", ".join(
                f"{tune}={embedded_schemas[tune]!r}" for tune in TUNES))
    embedded_digests = {
        tune: inputs[tune]["tune_difference_allowlist_sha256"] for tune in TUNES
    }
    if len({(type(value).__name__, repr(value))
            for value in embedded_digests.values()}) != 1:
        errors.append(
            "raw embedded allowlist pin SHA-256 values disagree across tunes: "
            + ", ".join(
                f"{tune}={embedded_digests[tune]!r}" for tune in TUNES))
    for tune in TUNES:
        embedded_digest = embedded_digests[tune]
        if (isinstance(embedded_digest, str)
                and HEX64.fullmatch(embedded_digest)
                and embedded_digest != allowlist_sha256):
            errors.append(
                f"{tune}: embedded allowlist pin SHA-256 does not match "
                "the supplied allowlist file")

    name_sets = {tune: set(catalogues[tune]) for tune in TUNES}
    if len({frozenset(names) for names in name_sets.values()}) != 1:
        union = set().union(*name_sets.values())
        for tune in TUNES:
            absent = sorted(union - name_sets[tune])
            if absent:
                errors.append(
                    f"{tune}: catalogue missing {len(absent)} setting(s): "
                    + ", ".join(absent[:8]))
    counts = {len(name_sets[tune]) for tune in TUNES}
    authoritative_count = next(iter(counts)) if len(counts) == 1 and counts != {0} else None

    differences = []
    for name in sorted(set().union(*name_sets.values())):
        values = {tune: catalogues[tune].get(name) for tune in TUNES}
        if len(set(values.values())) == 1:
            continue
        if any(value is None for value in values.values()):
            classification = "catalogue_mismatch"
        elif name in per_job:
            classification = "excluded_per_job_difference"
        elif name in tune_allowed:
            classification = "allowed_tune_difference"
        else:
            classification = "forbidden_difference"
            errors.append(f"forbidden resolved setting difference: {name}")
        differences.append({
            "name": name,
            "values": values,
            "classification": classification,
        })

    required_checks = []
    for name, expected in sorted(required.items()):
        values = {tune: catalogues[tune].get(name) for tune in TUNES}
        passed = all(
            value is not None and _equivalent_required_value(value, expected)
            for value in values.values())
        if not passed:
            errors.append(f"required common setting check failed: {name}")
        required_checks.append({
            "name": name,
            "required_value": expected,
            "resolved_values": values,
            "status": "PASS" if passed else "FAIL",
        })

    return {
        "schema": RECEIPT_SCHEMA,
        "status": "PASS" if not errors else "FAIL",
        "effective_setting_count": authoritative_count,
        "allowlist": {
            "schema": allowlist.get("schema"),
            "sha256": allowlist_sha256,
        },
        "inputs": inputs,
        "effective_settings_sha256": {
            tune: inputs[tune]["effective_settings_sha256"] for tune in TUNES
        },
        "differences": differences,
        "resolved_tune_difference_count": sum(
            row["classification"] == "allowed_tune_difference"
            for row in differences),
        "excluded_per_job_difference_count": sum(
            row["classification"] == "excluded_per_job_difference"
            for row in differences),
        "required_common_value_checks": required_checks,
        "serialization_rule": {
            "schema_prefix": f"schema={EFFECTIVE_SETTINGS_SCHEMA}\\n",
            "row": "std::quoted(name) + tab + std::quoted(value) + newline",
            "ordering": "setting name ascending",
            "digest": "sha256 of UTF-8 serialized bytes",
        },
        "errors_refusals": errors,
    }


def _write_receipt(path: Path, receipt: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--monash", type=Path, required=True)
    parser.add_argument("--junctions", type=Path, required=True)
    parser.add_argument("--closepacking", type=Path, required=True)
    parser.add_argument("--allowlist", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    errors: list[str] = []
    try:
        allowlist_bytes = args.allowlist.read_bytes()
        allowlist = json.loads(allowlist_bytes)
        allowlist_sha = hashlib.sha256(allowlist_bytes).hexdigest()
    except Exception as error:  # a failure receipt is required for bad input
        allowlist = {}
        allowlist_sha = ""
        message = str(error).replace(str(args.allowlist), args.allowlist.name)
        errors.append(f"allowlist {args.allowlist.name}: {message}")

    paths = {
        "MONASH": args.monash,
        "JUNCTIONS": args.junctions,
        "CLOSEPACKING": args.closepacking,
    }
    sources: dict[str, dict[str, Any]] = {}
    for tune, path in paths.items():
        try:
            sources[tune] = load_root_source(path, tune)
        except Exception as error:  # preserve the failure as deterministic JSON
            message = str(error).replace(str(path), path.name)
            sources[tune] = {
                "expected_tune": tune,
                "basename": path.name,
                "sha256": sha256_file(path) if path.is_file() else None,
                "load_error": message,
            }

    receipt = compare_effective_settings(
        sources, allowlist, allowlist_sha, initial_errors=errors)
    _write_receipt(args.output, receipt)
    print(
        f"EFFECTIVE_SETTINGS_RECEIPT status={receipt['status']} "
        f"count={receipt['effective_setting_count']} "
        f"differences={len(receipt['differences'])}")
    return 0 if receipt["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
