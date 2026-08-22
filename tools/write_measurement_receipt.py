#!/usr/bin/env python3
"""Write and enforce the output receipt for one systematic measurement.

The renderer's exit code only says that ROOT finished.  A usable measurement
also has to emit every configured uncertainty identity, resolve the dataset's
exact complete-root tag, keep every row at PASS, and satisfy the independent
output-plane assertion.  This tool records those facts even on failure and
returns nonzero unless all of them hold.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fields(line: str) -> dict[str, str]:
    return dict(token.split("=", 1) for token in line.split() if "=" in token)


def identity(row: dict[str, str]) -> str:
    return "|".join(
        row.get(key, "")
        for key in ("flavour", "trigger", "tune", "associate", "bin")
    )


def build_receipt(args: argparse.Namespace) -> tuple[dict, list[str]]:
    text = args.log.read_text(errors="replace")
    facts = json.loads(args.facts.read_text())
    assertion = (
        json.loads(args.assertion.read_text()) if args.assertion.exists() else None
    )

    resolved = sorted(
        {
            line.split("tag=", 1)[1].strip()
            for line in text.splitlines()
            if "central resolver" in line and "tag=" in line
        }
    )
    rows = [
        fields(line)
        for line in text.splitlines()
        if line.startswith("UNCERTAINTY_MATRIX")
    ]
    actual = [identity(row) for row in rows]
    expected = facts["expected_uncertainty_identities"]
    actual_set, expected_set = set(actual), set(expected)
    missing = sorted(expected_set - actual_set)
    unexpected = sorted(actual_set - expected_set)
    duplicate_count = len(actual) - len(actual_set)
    failing_rows = sorted(
        identity(row) for row in rows if row.get("status") != "PASS"
    )

    failures: list[str] = []
    if args.render_status != 0:
        failures.append(f"render_exit_status={args.render_status}")
    if args.assertion_status != 0:
        failures.append(f"output_assertion_exit_status={args.assertion_status}")
    if resolved != [args.expected_tag]:
        failures.append(
            f"resolved_complete_root_tags={resolved!r}, expected={[args.expected_tag]!r}"
        )
    if len(actual) != len(expected):
        failures.append(
            f"uncertainty_matrix_rows={len(actual)}, expected={len(expected)}"
        )
    if missing:
        failures.append(f"missing_uncertainty_identities={len(missing)}")
    if unexpected:
        failures.append(f"unexpected_uncertainty_identities={len(unexpected)}")
    if duplicate_count:
        failures.append(f"duplicate_uncertainty_identities={duplicate_count}")
    if failing_rows:
        failures.append(f"non_pass_uncertainty_rows={len(failing_rows)}")

    receipt = {
        "schema": "hadronization_measurement_receipt_v3",
        "completion_status": "FAIL" if failures else "PASS",
        "failure_reasons": failures,
        "purpose": "measurement",
        "publication_eligible": False,
        "campaign": args.campaign,
        "render_exit_status": args.render_status,
        "output_assertion_exit_status": args.assertion_status,
        "output_assertion": assertion,
        "render_window": [args.window_start, args.window_end],
        "uncertainty_matrix_rows": len(actual),
        "expected_uncertainty_matrix_rows": len(expected),
        "missing_uncertainty_identities": missing,
        "unexpected_uncertainty_identities": unexpected,
        "duplicate_uncertainty_identities": duplicate_count,
        "non_pass_uncertainty_rows": failing_rows,
        "staged_configuration_facts": facts,
        "expected_complete_root_tag": args.expected_tag,
        "resolved_complete_root_tags": resolved,
        "staged_configuration_sha256": sha256(args.staged),
        "log_sha256": sha256(args.log),
        "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    return receipt, failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--campaign", required=True)
    parser.add_argument("--render-status", type=int, required=True)
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--staged", type=Path, required=True)
    parser.add_argument("--assertion-status", type=int, required=True)
    parser.add_argument("--facts", type=Path, required=True)
    parser.add_argument("--assertion", type=Path, required=True)
    parser.add_argument("--window-start", type=int, required=True)
    parser.add_argument("--window-end", type=int, required=True)
    parser.add_argument("--expected-tag", required=True)
    args = parser.parse_args()

    receipt, failures = build_receipt(args)
    args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(
        "receipt "
        f"status={receipt['completion_status']} purpose=measurement "
        f"rc={args.render_status} output_assertion_rc={args.assertion_status} "
        f"rows={receipt['uncertainty_matrix_rows']}/"
        f"{receipt['expected_uncertainty_matrix_rows']} "
        f"resolved={receipt['resolved_complete_root_tags']}"
    )
    for failure in failures:
        print(f"MEASUREMENT_RECEIPT_FAIL {failure}")
    return 4 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
