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

WHERE AN INPUT COMES FROM. Results are commit-scoped, and an accepted result
is immutable under the commit root that produced it. This tool therefore
resolves every measurement input in one order: the current commit root first,
then the digest pin in `config/accepted_measurements_v1.json`, then a refusal
that names the campaign and that file. A pinned receipt is hashed BEFORE its
directory is read, because the directory beside a wrong receipt holds wrong
render logs too. Nothing here writes: a request that would place its own
output under an accepted root refuses instead.
"""

from __future__ import annotations

import argparse
import hashlib
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
ACCEPTED_CONTRACT = ROOT / "config" / "accepted_measurements_v1.json"
ACCEPTED_SCHEMA = "hadronization_accepted_measurements_v1"
NOMINAL_STATUSES = ("canonical", "canonical_candidate")
RECEIPT_NAME = "measurement_receipt.json"
BOUNDARY_RECEIPT_NAME = "multiplicity_boundary_receipt_v2.json"
CURRENT_ROOT = "current_commit_root"
ACCEPTED_PIN = "accepted_pin"


class RequestRefused(Exception):
    """A request that cannot be satisfied. Named before any work starts."""


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def accepted_pins() -> dict:
    """The accepted measurement roots, or a refusal that names the file."""
    if not ACCEPTED_CONTRACT.is_file():
        raise RequestRefused(
            f"the accepted-measurement pin file is absent: {ACCEPTED_CONTRACT}")
    payload = json.loads(ACCEPTED_CONTRACT.read_text())
    if payload.get("schema") != ACCEPTED_SCHEMA:
        raise RequestRefused(
            f"{ACCEPTED_CONTRACT} declares schema "
            f"{payload.get('schema')!r}, expected {ACCEPTED_SCHEMA!r}")
    return payload


def refuse_an_accepted_destination(commit: str, pins: dict) -> None:
    """An accepted root is read, never written. Ruling R7's fail-closed frame.

    The destination is built from the CURRENT commit, so this can only fire
    when a checkout sits on a commit that already owns accepted results. That
    is exactly the case where a run would overwrite them.
    """
    roots = {row.get("accepted_root")
             for row in pins.get("campaigns", {}).values()}
    roots.add(pins.get("nominal", {}).get("accepted_root"))
    roots.discard(None)
    if commit in roots:
        raise RequestRefused(
            f"the current commit root is {commit}, which {ACCEPTED_CONTRACT} "
            "names as an accepted root; an accepted result is never "
            "regenerated and never written into")


def resolve_receipt(results_root: Path, campaign: str, dataset: str,
                    commit: str, pins: dict) -> dict:
    """Where this campaign's measurement receipt comes from.

    The current commit root wins when it holds the receipt. Otherwise the pin
    answers, and its sha256 is checked here, before any caller opens the
    directory the receipt names. A campaign the pin does not declare refuses.
    """
    current = (results_root / campaign / commit / "measurements" / dataset
               / RECEIPT_NAME)
    if current.is_file():
        return {"path": str(current), "root": commit, "source": CURRENT_ROOT,
                "receipt_sha256": sha256(current), "verified": True}

    pin = pins.get("campaigns", {}).get(campaign)
    if pin is None:
        raise RequestRefused(
            f"{campaign}: the current commit root {commit} holds no "
            f"{RECEIPT_NAME} and {ACCEPTED_CONTRACT} pins no accepted root "
            "for this campaign")

    pinned = results_root / pin["receipt_path"]
    entry = {"path": str(pinned), "root": pin["accepted_root"],
             "source": ACCEPTED_PIN,
             "receipt_sha256": pin["receipt_sha256"], "verified": False}
    if not pinned.is_file():
        # The pin is declared and this host does not hold the artifact. The
        # extraction chain refuses by path; a preflight on a laptop that holds
        # no campaign data must still answer the contract question.
        return entry
    measured = sha256(pinned)
    if measured != pin["receipt_sha256"]:
        raise RequestRefused(
            f"{campaign}: the pinned receipt {pinned} hashes to {measured}; "
            f"{ACCEPTED_CONTRACT} pins {pin['receipt_sha256']}")
    entry["verified"] = True
    return entry


def resolve_nominal_boundary(results_root: Path, campaign: str, dataset: str,
                             commit: str, pins: dict) -> dict:
    """The boundary receipt of the render this envelope will be bound to.

    The receipt is located, never guessed: exactly one file of that name may
    stand under a plotting plane, which is the plotter's own invariant. Two
    receipts are a refusal and never a reason to fall through to the pin.
    """
    measurement = (
        results_root / campaign / commit / "measurements" / dataset
    )
    measurement_found = (
        sorted(measurement.rglob(BOUNDARY_RECEIPT_NAME))
        if measurement.is_dir() else []
    )
    if len(measurement_found) > 1:
        raise RequestRefused(
            f"{campaign}: {len(measurement_found)} "
            f"{BOUNDARY_RECEIPT_NAME} files under {measurement}; exactly one "
            "is required"
        )
    if len(measurement_found) == 1:
        return {
            "path": str(measurement_found[0]),
            "root": commit,
            "source": CURRENT_ROOT,
            "boundary_receipt_sha256": sha256(measurement_found[0]),
            "verified": True,
        }

    plane = results_root / campaign / commit / "plotting"
    found = (
        sorted(plane.rglob(BOUNDARY_RECEIPT_NAME))
        if plane.is_dir() else []
    )
    if len(found) > 1:
        raise RequestRefused(
            f"{campaign}: {len(found)} {BOUNDARY_RECEIPT_NAME} files under "
            f"{plane}; exactly one is required and the plotter writes one")
    if len(found) == 1:
        return {"path": str(found[0]), "root": commit, "source": CURRENT_ROOT,
                "boundary_receipt_sha256": sha256(found[0]), "verified": True}

    pin = pins.get("nominal", {})
    if pin.get("campaign") != campaign:
        raise RequestRefused(
            f"{campaign}: the current commit root {commit} holds no "
            f"{BOUNDARY_RECEIPT_NAME} and {ACCEPTED_CONTRACT} pins no "
            "accepted plotting root for this campaign")

    pinned = results_root / pin["boundary_receipt_path"]
    entry = {"path": str(pinned), "root": pin["accepted_root"],
             "source": ACCEPTED_PIN,
             "boundary_receipt_sha256": pin["boundary_receipt_sha256"],
             "verified": False}
    if not pinned.is_file():
        return entry
    measured = sha256(pinned)
    if measured != pin["boundary_receipt_sha256"]:
        raise RequestRefused(
            f"{campaign}: the pinned boundary receipt {pinned} hashes to "
            f"{measured}; {ACCEPTED_CONTRACT} pins "
            f"{pin['boundary_receipt_sha256']}")
    entry["verified"] = True
    return entry


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

    pins = accepted_pins()
    refuse_an_accepted_destination(commit, pins)

    resolver_tags: dict[str, str] = {}
    receipts: dict[str, str] = {}
    accepted_roots: dict[str, dict] = {}
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
        try:
            resolved = resolve_receipt(
                results_root, variation, key, commit, pins)
        except RequestRefused as error:
            unresolved.append(f"{error}")
            continue
        accepted_roots[variation] = resolved
        receipts[variation] = resolved["path"]
    if unresolved:
        raise RequestRefused(
            "cannot resolve every declared source: " + "; ".join(unresolved))

    boundary = resolve_nominal_boundary(
        results_root, campaign, nominal_key, commit, pins
    )

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
        "nominal_measurement_root": str(
            results_root / campaign / commit / "measurements" / nominal_key
        ),
        "commit": commit,
        "resolver_tags": resolver_tags,
        "receipts": receipts,
        "accepted_roots": accepted_roots,
        "nominal_boundary": boundary,
        "out_dir": str(out_dir),
        "envelope": str(out_dir / "systematics_envelope.json"),
        "sources_contract": str(SOURCES_CONTRACT),
        "accepted_measurements_contract": str(ACCEPTED_CONTRACT),
        "accepted_measurements_sha256": sha256(ACCEPTED_CONTRACT),
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

    pinned = sorted(c for c, row in resolved["accepted_roots"].items()
                    if row["source"] == ACCEPTED_PIN)
    print(
        f"SYSTEMATICS_REQUEST dataset={resolved['nominal_dataset']} "
        f"campaign={resolved['nominal_campaign']} "
        f"sources={len(resolved['resolver_tags'])} "
        f"out={resolved['out_dir']}")
    for campaign in pinned:
        row = resolved["accepted_roots"][campaign]
        print(f"SYSTEMATICS_ACCEPTED_ROOT {campaign} root={row['root']} "
              f"sha256={row['receipt_sha256']} verified={row['verified']}")
    boundary = resolved["nominal_boundary"]
    print(f"SYSTEMATICS_NOMINAL_BOUNDARY root={boundary['root']} "
          f"source={boundary['source']} "
          f"sha256={boundary['boundary_receipt_sha256']} "
          f"verified={boundary['verified']}")
    if args.preflight_only:
        print(
            "SYSTEMATICS_PREFLIGHT_ONLY status=PASS extraction=false "
            "outputs_written=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
