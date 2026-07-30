#!/usr/bin/env python3
"""Synthetic and operational audits for publication Gate C.

The functions in this module deliberately operate on manifests and technical
metadata only.  Canonical selection never receives a physics observable.  The
workflow audit proves exact membership and SHA-256 continuity from the frozen
raw manifest through status submission, central/block merge inputs, and the
plot-selection contract.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import statistics
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Sequence


TUNES = ("MONASH", "JUNCTIONS", "CLOSEPACKING")
TUNE_ORDINAL = {tune: index for index, tune in enumerate(TUNES)}
EXPECTED_CANDIDATES = {
    "MONASH": 100,
    "JUNCTIONS": 200,
    "CLOSEPACKING": 200,
}
CANONICAL_PER_TUNE = 100
BLOCK_COUNT = 10
SELECTION_STATUS_SCHEMA = "hf_candidate_technical_status_v1"
SELECTION_REPORT_SCHEMA = "hf_canonical_selection_audit_v1"
EVENT_ROW_SCHEMA = "hf_event_id_audit_row_v1"
EVENT_REPORT_SCHEMA = "hf_global_event_id_audit_v1"
DIAGNOSTIC_ROW_SCHEMA = "hf_gate_c_job_diagnostic_v1"
DIAGNOSTIC_REPORT_SCHEMA = "hf_primary_reserve_failure_bias_audit_v1"
WORKFLOW_SPEC_SCHEMA = "hf_gate_c_manifest_workflow_spec_v1"
WORKFLOW_REPORT_SCHEMA = "hf_gate_c_manifest_workflow_audit_v1"
HEX64 = set("0123456789abcdef")


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def digest_rows(rows: Sequence[dict[str, Any]]) -> str:
    text = "".join(
        json.dumps(row, sort_keys=True) + "\n"
        for row in rows
    )
    return hashlib.sha256(text.encode()).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"expected object at {path}:{number}")
        rows.append(value)
    return rows


def exclusive_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(
        path,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL,
        0o444,
    )
    try:
        with os.fdopen(descriptor, "w") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        # Retain a partial file as a fail-closed marker.
        raise


def require_int(
    value: object,
    label: str,
    minimum: int = 0,
    maximum: int | None = None,
) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value < minimum
        or (maximum is not None and value > maximum)
    ):
        raise ValueError(f"invalid {label}: {value!r}")
    return value


def require_hex64(value: object, label: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in HEX64 for character in value)
    ):
        raise ValueError(f"invalid {label}: {value!r}")
    return value


def require_tune(value: object, label: str = "tune") -> str:
    if value not in TUNES:
        raise ValueError(f"invalid {label}: {value!r}")
    return str(value)


def candidate_contract(
    candidates: Sequence[dict[str, Any]],
) -> tuple[str, dict[tuple[str, int], dict[str, Any]]]:
    if not candidates:
        raise ValueError("candidate manifest is empty")
    campaign_values = {row.get("campaign") for row in candidates}
    if len(campaign_values) != 1:
        raise ValueError("candidate manifest mixes campaigns")
    campaign = next(iter(campaign_values))
    if not isinstance(campaign, str) or not campaign:
        raise ValueError("candidate campaign is absent")
    lookup: dict[tuple[str, int], dict[str, Any]] = {}
    counts = Counter()
    for row in candidates:
        tune = require_tune(row.get("tune"))
        logical_id = require_int(
            row.get("logical_id"),
            "candidate logical ID",
        )
        expected_count = EXPECTED_CANDIDATES[tune]
        if logical_id >= expected_count:
            raise ValueError(
                f"candidate logical ID outside {tune} range: {logical_id}"
            )
        role = row.get("role")
        expected_role = (
            "primary"
            if logical_id < CANONICAL_PER_TUNE
            else "reserve"
        )
        if role != expected_role:
            raise ValueError(
                f"candidate role differs for {tune}/{logical_id}: {role!r}"
            )
        key = (tune, logical_id)
        if key in lookup:
            raise ValueError(f"duplicate candidate: {tune}/{logical_id}")
        lookup[key] = row
        counts[tune] += 1
    for tune, expected in EXPECTED_CANDIDATES.items():
        if counts[tune] != expected:
            raise ValueError(
                f"candidate count differs for {tune}: "
                f"{counts[tune]} != {expected}"
            )
        expected_ids = set(range(expected))
        actual_ids = {
            logical_id
            for row_tune, logical_id in lookup
            if row_tune == tune
        }
        if actual_ids != expected_ids:
            raise ValueError(f"candidate logical-ID coverage differs for {tune}")
    return campaign, lookup


def deterministic_canonical_selection(
    candidates: Sequence[dict[str, Any]],
    technical_status: Sequence[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Choose valid primaries, then the lowest valid reserves.

    ``technical_status`` has an exact field set so a yield, process fraction,
    multiplicity, or any other physics-sensitive quantity cannot influence
    selection.
    """

    campaign, candidate_lookup = candidate_contract(candidates)
    status_keys = {
        "schema",
        "campaign",
        "tune",
        "logical_id",
        "attempt",
        "valid",
        "terminal_state",
        "raw_path",
        "raw_sha256",
        "validation_receipt_sha256",
    }
    status_lookup: dict[tuple[str, int], dict[str, Any]] = {}
    for row in technical_status:
        if set(row) != status_keys:
            raise ValueError(
                "technical status field set differs; physics-sensitive "
                "selection inputs are forbidden"
            )
        if row["schema"] != SELECTION_STATUS_SCHEMA:
            raise ValueError("technical status schema differs")
        if row["campaign"] != campaign:
            raise ValueError("technical status campaign differs")
        tune = require_tune(row["tune"])
        logical_id = require_int(row["logical_id"], "status logical ID")
        key = (tune, logical_id)
        if key not in candidate_lookup:
            raise ValueError(f"status row is not a candidate: {key}")
        if key in status_lookup:
            raise ValueError(f"duplicate technical status: {key}")
        require_int(row["attempt"], "status attempt")
        if not isinstance(row["valid"], bool):
            raise ValueError("technical validity must be boolean")
        terminal = row["terminal_state"]
        allowed_terminal = {
            "VALIDATED",
            "PRODUCER_FAILURE",
            "VALIDATOR_FAILURE",
            "EVICTED_OR_LOST",
            "NOT_RUN",
        }
        if terminal not in allowed_terminal:
            raise ValueError(f"unsupported terminal state: {terminal!r}")
        if row["valid"] != (terminal == "VALIDATED"):
            raise ValueError("validity contradicts terminal state")
        if row["valid"]:
            if (
                not isinstance(row["raw_path"], str)
                or not row["raw_path"]
            ):
                raise ValueError("valid status lacks a raw path")
            require_hex64(row["raw_sha256"], "valid raw SHA-256")
            require_hex64(
                row["validation_receipt_sha256"],
                "valid validation-receipt SHA-256",
            )
        elif any(
            row[key] is not None
            for key in (
                "raw_path",
                "raw_sha256",
                "validation_receipt_sha256",
            )
        ):
            raise ValueError("invalid status claims validated raw provenance")
        status_lookup[key] = row
    if set(status_lookup) != set(candidate_lookup):
        missing = sorted(set(candidate_lookup) - set(status_lookup))
        extra = sorted(set(status_lookup) - set(candidate_lookup))
        raise ValueError(
            f"technical status coverage differs: missing={missing} extra={extra}"
        )

    status_sha = digest_rows(
        sorted(
            technical_status,
            key=lambda row: (
                TUNE_ORDINAL[row["tune"]],
                int(row["logical_id"]),
            ),
        )
    )
    approval = f"technical_status_sha256:{status_sha}"
    choices: list[dict[str, Any]] = []
    substitutions: list[dict[str, Any]] = []
    for tune in TUNES:
        valid_reserves = [
            logical_id
            for logical_id in range(
                CANONICAL_PER_TUNE,
                EXPECTED_CANDIDATES[tune],
            )
            if status_lookup[(tune, logical_id)]["valid"]
        ]
        reserve_cursor = 0
        for slot in range(CANONICAL_PER_TUNE):
            primary_status = status_lookup[(tune, slot)]
            if primary_status["valid"]:
                logical_id = slot
                reason = "valid_primary_initial_allocation"
            else:
                if reserve_cursor >= len(valid_reserves):
                    raise ValueError(
                        f"insufficient valid reserves for {tune} slot {slot}"
                    )
                logical_id = valid_reserves[reserve_cursor]
                reserve_cursor += 1
                reason = (
                    "lowest_valid_reserve_replaces_"
                    f"missing_primary_{slot:03d}"
                )
                substitutions.append(
                    {
                        "tune": tune,
                        "canonical_slot": slot,
                        "missing_primary_logical_id": slot,
                        "replacement_logical_id": logical_id,
                        "primary_terminal_state":
                            primary_status["terminal_state"],
                    }
                )
            selected_status = status_lookup[(tune, logical_id)]
            choices.append(
                {
                    "tune": tune,
                    "canonical_slot": slot,
                    "logical_id": logical_id,
                    "attempt": selected_status["attempt"],
                    "reason": reason,
                    "approval": approval,
                }
            )
    if len(choices) != len(TUNES) * CANONICAL_PER_TUNE:
        raise AssertionError("canonical choice count invariant failed")
    selected_keys = {
        (row["tune"], row["logical_id"])
        for row in choices
    }
    if len(selected_keys) != len(choices):
        raise AssertionError("canonical selection reused a logical output")
    report = {
        "schema": SELECTION_REPORT_SCHEMA,
        "state": "PASS",
        "campaign": campaign,
        "candidate_manifest_sha256": digest_rows(list(candidates)),
        "technical_status_sha256": status_sha,
        "selection_sha256": digest_rows(choices),
        "selected_rows": len(choices),
        "selected_per_tune": {
            tune: sum(row["tune"] == tune for row in choices)
            for tune in TUNES
        },
        "substitution_count": len(substitutions),
        "substitutions": substitutions,
        "selection_inputs":
            "technical validity only; physics observables forbidden",
    }
    return choices, report


def event_id(
    campaign_ordinal: int,
    tune_ordinal: int,
    logical_id: int,
    attempt: int,
    local_success: int,
) -> int:
    """Mirror HeavyFlavourUtils.h's collision-free 64-bit layout."""

    campaign_ordinal = require_int(
        campaign_ordinal, "campaign ordinal", 0, 0xFFFF
    )
    tune_ordinal = require_int(tune_ordinal, "tune ordinal", 0, 3)
    logical_id = require_int(logical_id, "logical ID", 0, 0x3FFF)
    attempt = require_int(attempt, "attempt", 0, 0xFFF)
    local_success = require_int(
        local_success,
        "local success",
        0,
        (1 << 20) - 1,
    )
    return (
        (campaign_ordinal << 48)
        | (tune_ordinal << 46)
        | (logical_id << 32)
        | (attempt << 20)
        | local_success
    )


def audit_event_rows(
    rows: Sequence[dict[str, Any]],
) -> dict[str, Any]:
    expected_keys = {
        "schema",
        "campaign_ordinal",
        "tune",
        "logical_id",
        "attempt",
        "local_success",
        "event_id",
    }
    seen: dict[int, int] = {}
    normalized = []
    for index, row in enumerate(rows):
        if set(row) != expected_keys:
            raise ValueError(f"event-ID row {index} field set differs")
        if row["schema"] != EVENT_ROW_SCHEMA:
            raise ValueError(f"event-ID row {index} schema differs")
        tune = require_tune(row["tune"])
        observed = require_int(
            row["event_id"],
            f"event-ID row {index} observed ID",
        )
        if observed in seen:
            raise ValueError(
                "duplicate global event ID "
                f"{observed} at rows {seen[observed]} and {index}"
            )
        seen[observed] = index
        expected = event_id(
            require_int(row["campaign_ordinal"], "campaign ordinal"),
            TUNE_ORDINAL[tune],
            require_int(row["logical_id"], "logical ID"),
            require_int(row["attempt"], "attempt"),
            require_int(row["local_success"], "local success"),
        )
        if observed != expected:
            raise ValueError(
                f"event-ID row {index} does not match declared provenance"
            )
        normalized.append(row)
    return {
        "schema": EVENT_REPORT_SCHEMA,
        "state": "PASS",
        "rows": len(rows),
        "unique_event_ids": len(seen),
        "event_rows_sha256": digest_rows(normalized),
        "layout":
            "[campaign:16][tune:2][logical:14][attempt:12][local:20]",
    }


def audit_manifest_event_ranges(
    canonical_rows: Sequence[dict[str, Any]],
) -> dict[str, Any]:
    ranges: list[tuple[int, int, tuple[int, int, int, int]]] = []
    seen_prefixes: set[tuple[int, int, int, int]] = set()
    seeds: set[int] = set()
    total_events = 0
    for index, row in enumerate(canonical_rows):
        tune = require_tune(row.get("tune"))
        campaign_ordinal = require_int(
            row.get("campaign_ordinal"),
            f"manifest row {index} campaign ordinal",
            0,
            0xFFFF,
        )
        logical_id = require_int(
            row.get("logical_id"),
            f"manifest row {index} logical ID",
            0,
            0x3FFF,
        )
        attempt = require_int(
            row.get("attempt"),
            f"manifest row {index} attempt",
            0,
            0xFFF,
        )
        successes = require_int(
            row.get("requested_successes"),
            f"manifest row {index} requested successes",
            1,
            1 << 20,
        )
        seed = require_int(
            row.get("seed"),
            f"manifest row {index} seed",
            1,
        )
        if seed in seeds:
            raise ValueError(f"duplicate global seed in manifest: {seed}")
        seeds.add(seed)
        prefix = (
            campaign_ordinal,
            TUNE_ORDINAL[tune],
            logical_id,
            attempt,
        )
        if prefix in seen_prefixes:
            raise ValueError(
                "duplicate global event-ID prefix in canonical manifest: "
                f"{prefix}"
            )
        seen_prefixes.add(prefix)
        first = event_id(*prefix, 0)
        last = event_id(*prefix, successes - 1)
        ranges.append((first, last, prefix))
        total_events += successes
    ranges.sort()
    for previous, current in zip(ranges, ranges[1:]):
        if current[0] <= previous[1]:
            raise ValueError(
                "overlapping global event-ID ranges: "
                f"{previous[2]} and {current[2]}"
            )
    return {
        "schema": EVENT_REPORT_SCHEMA,
        "state": "PASS",
        "manifest_rows": len(canonical_rows),
        "unique_prefixes": len(seen_prefixes),
        "unique_seeds": len(seeds),
        "total_event_ids_proved": total_events,
        "canonical_manifest_sha256": digest_rows(list(canonical_rows)),
        "method": "disjoint_provenance_prefix_ranges",
        "layout":
            "[campaign:16][tune:2][logical:14][attempt:12][local:20]",
    }


DIAGNOSTIC_METRICS = (
    "elapsed_seconds",
    "completed_attempts",
    "event_rate_hz",
    "output_bytes",
    "process_charm_fraction",
    "process_beauty_fraction",
    "mean_nch_hadronisation",
)


def numeric_or_none(value: object, label: str) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be numeric or null")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{label} is non-finite")
    return result


def summarize_metric(values: Iterable[float | None]) -> dict[str, Any]:
    finite = [float(value) for value in values if value is not None]
    if not finite:
        return {"n": 0, "mean": None, "sample_sd": None}
    return {
        "n": len(finite),
        "mean": statistics.fmean(finite),
        "sample_sd": (
            statistics.stdev(finite) if len(finite) >= 2 else None
        ),
    }


def compare_metric(
    first: Sequence[float | None],
    second: Sequence[float | None],
) -> dict[str, Any]:
    left = [float(value) for value in first if value is not None]
    right = [float(value) for value in second if value is not None]
    if not left or not right:
        return {
            "n_first": len(left),
            "n_second": len(right),
            "mean_difference": None,
            "standardized_difference": None,
            "status": "INSUFFICIENT",
        }
    difference = statistics.fmean(left) - statistics.fmean(right)
    if len(left) < 2 or len(right) < 2:
        standardized = None
    else:
        pooled_variance = (
            statistics.variance(left) + statistics.variance(right)
        ) / 2.0
        standardized = (
            difference / math.sqrt(pooled_variance)
            if pooled_variance > 0
            else (0.0 if difference == 0 else None)
        )
    return {
        "n_first": len(left),
        "n_second": len(right),
        "mean_difference": difference,
        "standardized_difference": standardized,
        "status": "COMPLETE",
    }


def failure_bias_diagnostic(
    candidates: Sequence[dict[str, Any]],
    metadata_rows: Sequence[dict[str, Any]],
    *,
    input_kind: str,
) -> dict[str, Any]:
    """Describe role/outcome associations without declaring them ignorable."""

    campaign, candidate_lookup = candidate_contract(candidates)
    if input_kind not in {"synthetic", "pilot"}:
        raise ValueError("input_kind must be synthetic or pilot")
    exact_keys = {
        "schema",
        "source",
        "campaign",
        "tune",
        "logical_id",
        "role",
        "attempt",
        "outcome",
        *DIAGNOSTIC_METRICS,
    }
    normalized: list[dict[str, Any]] = []
    identities: set[tuple[str, int, int]] = set()
    for index, row in enumerate(metadata_rows):
        if set(row) != exact_keys:
            raise ValueError(f"diagnostic row {index} field set differs")
        if row["schema"] != DIAGNOSTIC_ROW_SCHEMA:
            raise ValueError(f"diagnostic row {index} schema differs")
        if row["source"] != input_kind:
            raise ValueError(f"diagnostic row {index} source differs")
        if row["campaign"] != campaign:
            raise ValueError(f"diagnostic row {index} campaign differs")
        tune = require_tune(row["tune"])
        logical_id = require_int(
            row["logical_id"], f"diagnostic row {index} logical ID"
        )
        candidate = candidate_lookup.get((tune, logical_id))
        if candidate is None:
            raise ValueError(f"diagnostic row {index} is not a candidate")
        if row["role"] != candidate["role"]:
            raise ValueError(f"diagnostic row {index} role differs")
        attempt = require_int(
            row["attempt"], f"diagnostic row {index} attempt"
        )
        identity = (tune, logical_id, attempt)
        if identity in identities:
            raise ValueError(f"duplicate diagnostic identity: {identity}")
        identities.add(identity)
        outcome = row["outcome"]
        if outcome not in {
            "VALID",
            "PRODUCER_FAILURE",
            "VALIDATOR_FAILURE",
            "EVICTED",
            "NOT_RUN",
        }:
            raise ValueError(f"diagnostic row {index} outcome differs")
        clean = dict(row)
        for metric in DIAGNOSTIC_METRICS:
            clean[metric] = numeric_or_none(
                row[metric], f"diagnostic row {index} {metric}"
            )
        normalized.append(clean)
    if not normalized:
        raise ValueError("failure-bias diagnostic has no metadata")

    cohort_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in normalized:
        cohort_rows[f"{row['tune']}:{row['role']}"].append(row)
        cohort_rows[
            f"{row['tune']}:{'valid' if row['outcome'] == 'VALID' else 'failed'}"
        ].append(row)
    cohorts = {}
    for name, rows in sorted(cohort_rows.items()):
        cohorts[name] = {
            "n": len(rows),
            "outcomes": dict(sorted(Counter(
                row["outcome"] for row in rows
            ).items())),
            "metrics": {
                metric: summarize_metric(row[metric] for row in rows)
                for metric in DIAGNOSTIC_METRICS
            },
        }

    comparisons = []
    for tune in ("JUNCTIONS", "CLOSEPACKING"):
        primary = [
            row
            for row in normalized
            if row["tune"] == tune
            and row["role"] == "primary"
            and row["outcome"] == "VALID"
        ]
        reserve = [
            row
            for row in normalized
            if row["tune"] == tune
            and row["role"] == "reserve"
            and row["outcome"] == "VALID"
        ]
        comparisons.append(
            {
                "comparison": f"{tune}:valid_primary_vs_valid_reserve",
                "first_cohort": "valid_primary",
                "second_cohort": "valid_reserve",
                "metrics": {
                    metric: compare_metric(
                        [row[metric] for row in primary],
                        [row[metric] for row in reserve],
                    )
                    for metric in DIAGNOSTIC_METRICS
                },
            }
        )
    for tune in TUNES:
        valid = [
            row for row in normalized
            if row["tune"] == tune and row["outcome"] == "VALID"
        ]
        failed = [
            row for row in normalized
            if row["tune"] == tune and row["outcome"] != "VALID"
        ]
        comparisons.append(
            {
                "comparison": f"{tune}:valid_vs_failed",
                "first_cohort": "valid",
                "second_cohort": "failed",
                "metrics": {
                    metric: compare_metric(
                        [row[metric] for row in valid],
                        [row[metric] for row in failed],
                    )
                    for metric in DIAGNOSTIC_METRICS
                },
            }
        )
    complete_comparisons = sum(
        metric["status"] == "COMPLETE"
        for comparison in comparisons
        for metric in comparison["metrics"].values()
    )
    return {
        "schema": DIAGNOSTIC_REPORT_SCHEMA,
        "state": "DIAGNOSTIC_COMPLETE",
        "campaign": campaign,
        "input_kind": input_kind,
        "candidate_manifest_sha256": digest_rows(list(candidates)),
        "metadata_sha256": digest_rows(
            sorted(
                normalized,
                key=lambda row: (
                    TUNE_ORDINAL[row["tune"]],
                    row["logical_id"],
                    row["attempt"],
                ),
            )
        ),
        "rows": len(normalized),
        "cohorts": cohorts,
        "comparisons": comparisons,
        "complete_metric_comparisons": complete_comparisons,
        "requires_human_review": True,
        "interpretation":
            "Descriptive technical/failure-bias evidence only. This report "
            "does not authorize missingness as ignorable and never selects "
            "canonical jobs.",
    }


def row_identity(row: dict[str, Any]) -> tuple[str, int, int, str, str]:
    return (
        require_tune(row.get("tune")),
        require_int(row.get("canonical_slot"), "canonical slot"),
        require_int(row.get("logical_id"), "logical ID"),
        str(row.get("raw_path")),
        require_hex64(row.get("raw_sha256"), "raw SHA-256"),
    )


def exact_membership(
    expected: Sequence[dict[str, Any]],
    observed: Sequence[dict[str, Any]],
    label: str,
) -> None:
    expected_identities = [row_identity(row) for row in expected]
    observed_identities = [row_identity(row) for row in observed]
    if len(set(observed_identities)) != len(observed_identities):
        raise ValueError(f"{label} contains duplicate canonical inputs")
    if observed_identities != expected_identities:
        missing = sorted(set(expected_identities) - set(observed_identities))
        extra = sorted(set(observed_identities) - set(expected_identities))
        raise ValueError(
            f"{label} differs from canonical manifest: "
            f"missing={missing[:3]} extra={extra[:3]}"
        )


def validate_manifest_workflow(
    specification: dict[str, Any],
    *,
    base: Path,
) -> dict[str, Any]:
    """Validate one-manifest membership through every downstream stage."""

    exact_keys = {
        "schema",
        "canonical_manifest",
        "candidate_manifest",
        "block_manifests",
        "status_submission_manifest",
        "complete_root_merge_manifests",
        "subsample_merge_manifests",
        "plot_selection_contract",
    }
    if set(specification) != exact_keys:
        raise ValueError("manifest-workflow specification field set differs")
    if specification["schema"] != WORKFLOW_SPEC_SCHEMA:
        raise ValueError("manifest-workflow specification schema differs")

    def resolve(relative: object, label: str) -> Path:
        if not isinstance(relative, str) or not relative:
            raise ValueError(f"{label} path is absent")
        path = Path(relative)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError(f"{label} path escapes workflow base")
        full = base / path
        if full.is_symlink() or not full.is_file():
            raise FileNotFoundError(f"{label} is absent: {full}")
        return full

    canonical_path = resolve(
        specification["canonical_manifest"],
        "canonical manifest",
    )
    candidate_path = resolve(
        specification["candidate_manifest"],
        "candidate manifest",
    )
    canonical_rows = read_jsonl(canonical_path)
    candidate_rows = read_jsonl(candidate_path)
    candidate_contract(candidate_rows)
    if len(canonical_rows) != len(TUNES) * CANONICAL_PER_TUNE:
        raise ValueError("canonical manifest is not exactly 300 rows")
    expected_order = [
        (tune, slot)
        for tune in TUNES
        for slot in range(CANONICAL_PER_TUNE)
    ]
    actual_order = [
        (
            require_tune(row.get("tune")),
            require_int(row.get("canonical_slot"), "canonical slot"),
        )
        for row in canonical_rows
    ]
    if actual_order != expected_order:
        raise ValueError("canonical manifest tune/slot ordering differs")
    canonical_candidate_keys = {
        (row["tune"], int(row["logical_id"]))
        for row in canonical_rows
    }
    candidate_keys = {
        (row["tune"], int(row["logical_id"]))
        for row in candidate_rows
    }
    if not canonical_candidate_keys.issubset(candidate_keys):
        raise ValueError("canonical manifest includes undeclared candidate")
    manifest_sha = sha256(canonical_path)

    status_rows = read_jsonl(resolve(
        specification["status_submission_manifest"],
        "status submission manifest",
    ))
    exact_membership(
        canonical_rows,
        status_rows,
        "status submission manifest",
    )

    central_paths = specification["complete_root_merge_manifests"]
    if not isinstance(central_paths, dict) or set(central_paths) != set(TUNES):
        raise ValueError("complete-root merge manifest map differs")
    central_hashes = {}
    for tune in TUNES:
        rows = read_jsonl(resolve(
            central_paths[tune],
            f"{tune} complete-root merge manifest",
        ))
        expected = [
            row for row in canonical_rows if row["tune"] == tune
        ]
        exact_membership(
            expected,
            rows,
            f"{tune} complete-root merge manifest",
        )
        central_hashes[tune] = digest_rows(rows)

    block_paths = specification["block_manifests"]
    block_merge_paths = specification["subsample_merge_manifests"]
    expected_block_names = {
        f"block_{block:02d}"
        for block in range(1, BLOCK_COUNT + 1)
    }
    if (
        not isinstance(block_paths, dict)
        or set(block_paths) != expected_block_names
        or not isinstance(block_merge_paths, dict)
        or set(block_merge_paths) != expected_block_names
    ):
        raise ValueError("ten-block manifest maps differ")
    block_union: list[tuple[str, int, int, str, str]] = []
    block_hashes: dict[str, str] = {}
    block_tune_hashes: dict[str, dict[str, str]] = {}
    for block_index in range(1, BLOCK_COUNT + 1):
        name = f"block_{block_index:02d}"
        rows = read_jsonl(resolve(
            block_paths[name],
            f"{name} canonical block manifest",
        ))
        if len(rows) != 30:
            raise ValueError(f"{name} does not contain 30 rows")
        expected = [
            row
            for row in canonical_rows
            if int(row.get("block", -1)) == block_index - 1
        ]
        exact_membership(expected, rows, f"{name} canonical block manifest")
        merged_rows = read_jsonl(resolve(
            block_merge_paths[name],
            f"{name} subsample merge manifest",
        ))
        exact_membership(
            rows,
            merged_rows,
            f"{name} subsample merge manifest",
        )
        block_union.extend(row_identity(row) for row in rows)
        block_hashes[name] = digest_rows(rows)
        block_tune_hashes[name] = {
            tune: digest_rows([
                row for row in rows if row["tune"] == tune
            ])
            for tune in TUNES
        }
    canonical_identities = [row_identity(row) for row in canonical_rows]
    if (
        len(block_union) != len(canonical_identities)
        or len(set(block_union)) != len(block_union)
        or set(block_union) != set(canonical_identities)
    ):
        raise ValueError("ten-block union is not exactly canonical")

    plot_path = resolve(
        specification["plot_selection_contract"],
        "plot selection contract",
    )
    plot = read_json(plot_path)
    plot_exact = {
        "schema",
        "canonical_manifest_sha256",
        "canonical_rows",
        "complete_root_input_sha256",
        "subsample_input_sha256",
        "block_count",
    }
    if set(plot) != plot_exact:
        raise ValueError("plot selection contract field set differs")
    if plot["schema"] != "hf_plot_selection_contract_v1":
        raise ValueError("plot selection contract schema differs")
    if (
        plot["canonical_manifest_sha256"] != manifest_sha
        or plot["canonical_rows"] != len(canonical_rows)
        or plot["block_count"] != BLOCK_COUNT
        or plot["complete_root_input_sha256"] != central_hashes
        or plot["subsample_input_sha256"] != block_tune_hashes
    ):
        raise ValueError(
            "plot selection contract does not bind the canonical "
            "central/block inputs"
        )

    selected_keys = set(canonical_candidate_keys)
    extra_reserves = sorted(
        (row["tune"], int(row["logical_id"]))
        for row in candidate_rows
        if row["role"] == "reserve"
        and (row["tune"], int(row["logical_id"])) not in selected_keys
    )
    downstream_keys = {
        (row["tune"], int(row["logical_id"]))
        for row in status_rows
    }
    if downstream_keys & set(extra_reserves):
        raise ValueError("status submission admitted an unselected reserve")
    return {
        "schema": WORKFLOW_REPORT_SCHEMA,
        "state": "PASS",
        "canonical_manifest_sha256": manifest_sha,
        "canonical_rows": len(canonical_rows),
        "status_rows": len(status_rows),
        "complete_root_rows": len(canonical_rows),
        "subsample_rows": len(block_union),
        "block_count": BLOCK_COUNT,
        "unselected_reserve_count": len(extra_reserves),
        "unselected_reserves_rejected": True,
        "plot_selection_contract_sha256": sha256(plot_path),
    }


def write_json_output(path: Path, value: object) -> None:
    exclusive_text(
        path,
        json.dumps(value, indent=2, sort_keys=True) + "\n",
    )


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    selection = subparsers.add_parser("select")
    selection.add_argument("candidate_manifest", type=Path)
    selection.add_argument("technical_status", type=Path)
    selection.add_argument("selection_output", type=Path)
    selection.add_argument("report_output", type=Path)

    event_rows = subparsers.add_parser("event-rows")
    event_rows.add_argument("event_rows", type=Path)
    event_rows.add_argument("report_output", type=Path)

    event_manifest = subparsers.add_parser("event-manifest")
    event_manifest.add_argument("canonical_manifest", type=Path)
    event_manifest.add_argument("report_output", type=Path)

    diagnostic = subparsers.add_parser("failure-bias")
    diagnostic.add_argument("candidate_manifest", type=Path)
    diagnostic.add_argument("metadata", type=Path)
    diagnostic.add_argument("report_output", type=Path)
    diagnostic.add_argument(
        "--input-kind",
        required=True,
        choices=("synthetic", "pilot"),
    )

    workflow = subparsers.add_parser("workflow")
    workflow.add_argument("specification", type=Path)
    workflow.add_argument("report_output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_arguments()
    if args.command == "select":
        choices, report = deterministic_canonical_selection(
            read_jsonl(args.candidate_manifest),
            read_jsonl(args.technical_status),
        )
        write_json_output(args.selection_output, choices)
        write_json_output(args.report_output, report)
        print(
            "GATE_C_CANONICAL_SELECTION_PASS "
            f"rows={len(choices)} substitutions={len(report['substitutions'])}"
        )
    elif args.command == "event-rows":
        report = audit_event_rows(read_jsonl(args.event_rows))
        write_json_output(args.report_output, report)
        print(
            "GATE_C_EVENT_ID_ROWS_PASS "
            f"unique={report['unique_event_ids']}"
        )
    elif args.command == "event-manifest":
        report = audit_manifest_event_ranges(
            read_jsonl(args.canonical_manifest)
        )
        write_json_output(args.report_output, report)
        print(
            "GATE_C_EVENT_ID_MANIFEST_PASS "
            f"events={report['total_event_ids_proved']}"
        )
    elif args.command == "failure-bias":
        report = failure_bias_diagnostic(
            read_jsonl(args.candidate_manifest),
            read_jsonl(args.metadata),
            input_kind=args.input_kind,
        )
        write_json_output(args.report_output, report)
        print(
            "GATE_C_FAILURE_BIAS_DIAGNOSTIC_COMPLETE "
            f"rows={report['rows']} "
            f"comparisons={report['complete_metric_comparisons']}"
        )
    else:
        specification = read_json(args.specification)
        report = validate_manifest_workflow(
            specification,
            base=args.specification.resolve().parent,
        )
        write_json_output(args.report_output, report)
        print(
            "GATE_C_MANIFEST_WORKFLOW_PASS "
            f"rows={report['canonical_rows']} blocks={report['block_count']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
