#!/usr/bin/env python3
"""Resolve one systematics request, or refuse before anything runs.

WHAT A REQUEST NEEDS BEFORE IT MAY RUN. An envelope is built from several
campaigns at once, so the request layer has more to check than a single-
dataset render: every included arm of every included source must name a
campaign, every such campaign must have a selector row that declares its
complete-root tag, and the destination must be a systematics plane and not a
plotting one.

Checking those AFTER a multi-hour extraction chain would be checking them too
late, so this tool answers first and the orchestrator runs second. With
HADRONIZATION_REQUEST_PREFLIGHT_ONLY the answer is the whole result, which is
what makes the refusal testable on a laptop that holds no campaign data.

THE NOMINAL MUST BE A NOMINAL. A systematic variation is an input to an
uncertainty, never the thing an uncertainty is attached to, so a request that
names a variation as its nominal is refused here rather than producing an
envelope that describes nothing.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))
if str(ROOT / "extraction") not in sys.path:
    sys.path.insert(0, str(ROOT / "extraction"))

import dataset_selector  # noqa: E402

SOURCES_CONTRACT = ROOT / "config" / "systematics_sources_v1.json"
SOURCES_SCHEMA = "hadronization_systematics_sources_v1"
NOMINAL_STATUSES = ("canonical", "canonical_candidate")
RECEIPT_NAME = "measurement_receipt.json"


class RequestRefused(Exception):
    """A request that cannot be satisfied. Named before any work starts."""


def included_campaigns(sources: dict) -> dict[str, str]:
    """campaign -> source name, for every INCLUDED ARM of an included source.

    Inclusion is per arm. Ruling R9 excludes the HF_SYS_PTHAT_1 arm of S3 and
    keeps HF_SYS_PTHAT_4, so a request must not demand a selector row or a
    receipt for the excluded arm. Ruling R11 excludes S5_class_migration
    whole; it declares no campaign either way.
    """
    out: dict[str, str] = {}
    for row in sources["sources"]:
        if not row.get("included", False):
            continue
        for arm in row.get("campaigns", []):
            if not arm.get("included", False):
                continue
            out[arm["campaign"]] = row["source"]
    return out


def rows_by_campaign(selector: Path, checkout: Path) -> dict[str, tuple[str, dict]]:
    payload = json.loads(selector.read_text())
    out: dict[str, tuple[str, dict]] = {}
    for key in payload.get("datasets", {}):
        try:
            _, row = dataset_selector.load(selector, checkout, key)
        except ValueError:
            continue
        campaign = row.get("campaign")
        if campaign:
            out[campaign] = (key, row)
    return out


def plan(selector: Path, checkout: Path, dataset: str, results_root: Path,
         commit: str) -> dict:
    sources = json.loads(SOURCES_CONTRACT.read_text())
    if sources.get("schema") != SOURCES_SCHEMA:
        raise RequestRefused(
            f"source contract declares {sources.get('schema')!r}, "
            f"expected {SOURCES_SCHEMA!r}")

    try:
        nominal_key, nominal = dataset_selector.load(
            selector, checkout, dataset)
    except ValueError as error:
        raise RequestRefused(f"nominal dataset: {error}") from error
    if nominal["status"] not in NOMINAL_STATUSES:
        raise RequestRefused(
            f"an envelope attaches to a nominal render; dataset {nominal_key} "
            f"has status {nominal['status']!r} and this command accepts "
            + ", ".join(NOMINAL_STATUSES))

    campaign = nominal["campaign"]
    available = rows_by_campaign(selector, checkout)
    wanted = included_campaigns(sources)

    resolver_tags: dict[str, str] = {}
    receipts: dict[str, str] = {}
    unresolved: list[str] = []
    for variation, source in sorted(wanted.items()):
        if variation not in available:
            unresolved.append(
                f"{variation} ({source}): the dataset selector has no row for "
                "this campaign")
            continue
        key, row = available[variation]
        if row["status"] != "systematic_variation":
            unresolved.append(
                f"{variation} ({source}): selector row {key} has status "
                f"{row['status']!r}, expected 'systematic_variation'")
            continue
        resolver_tags[variation] = row["complete_root_tag"]
        receipts[variation] = str(
            results_root / variation / commit / "measurements" / key
            / RECEIPT_NAME)
    if unresolved:
        raise RequestRefused(
            "cannot resolve every declared source: " + "; ".join(unresolved))

    out_dir = results_root / campaign / commit / "systematics"
    if "plotting" in out_dir.parts:
        raise RequestRefused(
            f"an envelope may not be written under a plotting output plane: "
            f"{out_dir}")

    return {
        "nominal_dataset": nominal_key,
        "nominal_campaign": campaign,
        "nominal_status": nominal["status"],
        "nominal_complete_root_tag": nominal["complete_root_tag"],
        "nominal_plot_plane": str(results_root / campaign / commit / "plotting"),
        "commit": commit,
        "resolver_tags": resolver_tags,
        "receipts": receipts,
        "out_dir": str(out_dir),
        "envelope": str(out_dir / "systematics_envelope.json"),
        "sources_contract": str(SOURCES_CONTRACT),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--selector", type=Path, required=True)
    ap.add_argument("--checkout", type=Path, default=ROOT)
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--results-root", type=Path, required=True)
    ap.add_argument("--commit", required=True)
    ap.add_argument("--preflight-only", action="store_true")
    ap.add_argument("--out", type=Path,
                    help="write the resolved plan as JSON")
    args = ap.parse_args()

    try:
        resolved = plan(args.selector.resolve(), args.checkout.resolve(),
                        args.dataset, args.results_root, args.commit)
    except RequestRefused as error:
        print(f"SYSTEMATICS_REQUEST_REFUSED {error}", file=sys.stderr)
        return 2

    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(resolved, indent=1, sort_keys=True) + "\n")

    print(
        f"SYSTEMATICS_REQUEST dataset={resolved['nominal_dataset']} "
        f"campaign={resolved['nominal_campaign']} "
        f"sources={len(resolved['resolver_tags'])} "
        f"out={resolved['out_dir']}")
    if args.preflight_only:
        print(
            "SYSTEMATICS_PREFLIGHT_ONLY status=PASS extraction=false "
            "outputs_written=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
