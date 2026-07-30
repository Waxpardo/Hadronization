#!/usr/bin/env python3
"""Validate the immutable raw PASS evidence consumed by an analysis job."""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import re
from pathlib import Path


HEX64 = re.compile(r"[0-9a-f]{64}")


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(16 * 1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def validate_analysis_raw_receipt(
    receipt: Path,
    raw: Path,
    expected_raw_sha256: str,
    expected_receipt_sha256: str,
    campaign: str,
    tune: str,
    logical_id: int,
    *,
    expected_log: Path | None = None,
    expected_log_sha256: str | None = None,
) -> dict:
    receipt_source = receipt
    raw_source = raw
    for label, path in (
        ("receipt", receipt_source),
        ("raw input", raw_source),
    ):
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"analysis raw {label} is absent or non-regular")
    receipt = receipt_source.resolve()
    raw = raw_source.resolve()
    for label, value in (
        ("raw checksum", expected_raw_sha256),
        ("receipt checksum", expected_receipt_sha256),
    ):
        if not isinstance(value, str) or not HEX64.fullmatch(value):
            raise ValueError(f"analysis raw {label} is invalid")
    if sha256(raw) != expected_raw_sha256:
        raise ValueError("analysis raw input checksum differs")
    if sha256(receipt) != expected_receipt_sha256:
        raise ValueError("analysis raw-validation receipt checksum differs")

    payload = json.loads(receipt.read_text())
    validated_utc = payload.get("validated_utc")
    try:
        parsed = datetime.datetime.fromisoformat(validated_utc)
    except (TypeError, ValueError) as error:
        raise ValueError(
            "analysis raw-validation timestamp is invalid"
        ) from error
    if (
        parsed.tzinfo is None
        or parsed.utcoffset() != datetime.timedelta(0)
    ):
        raise ValueError(
            "analysis raw-validation timestamp is not UTC"
        )
    exact = {
        "schema": "hf_raw_validation_receipt_v1",
        "result": "PASS",
        "validator_exit_status": 0,
        "output_sha256": expected_raw_sha256,
        "output_bytes": raw.stat().st_size,
    }
    for key, value in exact.items():
        if payload.get(key) != value:
            raise ValueError(
                f"analysis raw-validation receipt {key} differs"
            )
    provenance = payload.get("expected_provenance")
    identity = {
        "campaign": campaign,
        "tune": tune,
        "logical_id": logical_id,
    }
    if not isinstance(provenance, dict) or any(
        provenance.get(key) != value for key, value in identity.items()
    ):
        raise ValueError(
            "analysis raw-validation receipt identity differs"
        )

    log_name = payload.get("validation_log_name")
    log_sha = payload.get("validation_log_sha256")
    if (
        not isinstance(log_name, str)
        or Path(log_name).name != log_name
        or not isinstance(log_sha, str)
        or not HEX64.fullmatch(log_sha)
    ):
        raise ValueError(
            "analysis raw-validation log binding is invalid"
        )
    log = receipt.parent / log_name
    if log.is_symlink() or not log.is_file() or sha256(log) != log_sha:
        raise ValueError(
            "analysis raw-validation log is absent or stale"
        )
    if expected_log is not None and log.resolve() != expected_log.resolve():
        raise ValueError(
            "analysis raw-validation log path differs from manifest"
        )
    if (
        expected_log_sha256 is not None
        and log_sha != expected_log_sha256
    ):
        raise ValueError(
            "analysis raw-validation log checksum differs from manifest"
        )
    log_text = log.read_text(errors="replace")
    if (
        len(
            re.findall(
                r"^RAW_VALIDATION_SUMMARY errors=0(?:\s|$)",
                log_text,
                flags=re.MULTILINE,
            )
        )
        != 1
        or "RAW_VALIDATION_ERROR" in log_text
        or re.search(
            r"segmentation violation|segmentation fault|"
            r"cling JIT session error",
            log_text,
            flags=re.IGNORECASE,
        )
    ):
        raise ValueError(
            "analysis raw-validation log does not certify one PASS"
        )
    for key in ("validator_wrapper_sha256", "validator_macro_sha256"):
        if not HEX64.fullmatch(str(payload.get(key, ""))):
            raise ValueError(
                f"analysis raw-validation receipt {key} is invalid"
            )
    dependencies = payload.get("validator_dependency_sha256")
    if (
        not isinstance(dependencies, dict)
        or not dependencies
        or any(
            not isinstance(name, str)
            or not name
            or not HEX64.fullmatch(str(value))
            for name, value in dependencies.items()
        )
    ):
        raise ValueError(
            "analysis raw-validation dependency binding is invalid"
        )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("receipt", type=Path)
    parser.add_argument("raw", type=Path)
    parser.add_argument("raw_sha256")
    parser.add_argument("receipt_sha256")
    parser.add_argument("campaign")
    parser.add_argument("tune")
    parser.add_argument("logical_id", type=int)
    args = parser.parse_args()
    validate_analysis_raw_receipt(
        args.receipt,
        args.raw,
        args.raw_sha256,
        args.receipt_sha256,
        args.campaign,
        args.tune,
        args.logical_id,
    )
    print(
        "ANALYSIS_RAW_VALIDATION_RECEIPT_OK "
        f"receipt={args.receipt.resolve()} "
        f"raw_sha256={args.raw_sha256}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
