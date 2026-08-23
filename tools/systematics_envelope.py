#!/usr/bin/env python3
"""Build the per-class systematic envelope, or refuse and say why.

WHAT THIS IS. One tracked artifact that carries every per-class systematic
term, its combination, and the provenance that ties it to the exact nominal
render it applies to. Ruling R7 makes it the ONLY route by which a systematic
reaches a figure, and `./hadronization plot --systematics PATH` the only
consumer.

WHAT IT REFUSES, AND WHY REFUSING IS THE POINT. A systematic that is quietly
short one source understates, and an understated systematic is worse than an
absent one -- that is the pre-registration's own closing rule for section 9.
So every refusal below writes its reason into the envelope's `missing` list,
returns nonzero, and stamps the envelope INCOMPLETE or FAIL:

  missing receipt     an included source has no measurement receipt
  FAIL receipt        a receipt exists and reports completion_status FAIL
  tag disagreement    a receipt resolved a complete-root tag the selector
                      does not declare for that campaign
  partition mismatch  an input row carries a class the v2 percentile contract
                      does not define, or the report does not cover the
                      contract's classes
  unreasoned exclusion
                      a source or an arm is excluded and records no
                      exclusion_reason

WHAT AN EXCLUSION IS, AND WHY IT IS NOT A DELETION. Rulings R9 and R11 of
2026-08-23 exclude the HF_SYS_PTHAT_1 arm of S3 and the whole of
S5_class_migration. Both stay declared in `config/systematics_sources_v1.json`
with their reasons, and both are copied into the envelope's `exclusions` block.
A source deleted from the contract would leave a smaller envelope that looks
complete; an excluded source with a recorded reason says what is not in the
band and who decided that.

STAGE, THEN PROMOTE. The envelope is written to a temporary file beside its
destination and renamed only after the status is decided, so no reader can
ever observe a half-filled COMPLETE envelope. A refusal still writes the
envelope: a refusal with no artifact is a refusal nobody can audit.

THE ARITHMETIC IS NOT HERE. Every number comes from `extraction/
systematics_delta.py` and `extraction/combine_per_class.py`, which already
carry amendments A1 and A2 as required policy flags that refuse to default.
This module supplies validation, provenance, and shape. Re-deriving the
combination here would mean two implementations of one ruling.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _extra in (ROOT / "extraction", ROOT / "tools"):
    if str(_extra) not in sys.path:
        sys.path.insert(0, str(_extra))

from combine_per_class import (CAMPAIGNLESS_TERMS, SOURCES,  # noqa: E402
                               SourcesIncomplete, combine_cell,
                               source_arms, source_exclusions)
from harvest_class_axis import (INTEGRATED, class_names,  # noqa: E402
                                class_order)

ENVELOPE_SCHEMA = "hadronization_systematics_envelope_v1"
SOURCES_SCHEMA = "hadronization_systematics_sources_v1"
DELTA_REPORT_SCHEMA = "hadronization_per_class_delta_v1"
RECEIPT_SCHEMA = "hadronization_measurement_receipt_v3"
CLASS_CONTRACT = ROOT / "config" / "multiplicity_percentile_classes_v2.json"
ENVELOPE_CONTRACT = ROOT / "config" / "systematics_envelope_v1.json"
SOURCES_CONTRACT = ROOT / "config" / "systematics_sources_v1.json"

METHOD_TAGS = {
    "d2_quadrature": "SEM(Delta) = sqrt(SEM_var^2 + SEM_nominal^2)",
    "a1_max_rule": "max(|Delta|, SEM(Delta)) per class, applied continuously",
    "a2_s6_excluded": "S6 stays on the M1..M5 partition and out of this sum",
}
OBSERVABLE = "balancing_yield"


class EnvelopeRefused(Exception):
    """A declared input is absent or contradicts itself. Never a warning."""

    def __init__(self, status: str, reasons: list[str]):
        super().__init__("; ".join(reasons))
        self.status = status
        self.reasons = reasons


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path, schema: str | None = None) -> dict:
    if not path.is_file():
        raise EnvelopeRefused("INCOMPLETE", [f"input is absent: {path}"])
    payload = json.loads(path.read_text())
    if schema is not None and payload.get("schema") != schema:
        raise EnvelopeRefused(
            "FAIL",
            [f"{path.name} declares schema {payload.get('schema')!r}, "
             f"expected {schema!r}"])
    return payload


# --------------------------------------------------------------------------
# The declared sources
# --------------------------------------------------------------------------

def arms(row: dict) -> list[dict]:
    """The campaign entries of one source, as objects.

    Every entry is `{campaign, included, reason}`, and an excluded entry adds
    `exclusion_reason`. The per-arm shape exists because ruling R9 excludes ONE
    arm of a two-sided source: a single flag on the source could only have
    dropped S3 entirely or kept an arm the owner ruled out.
    """
    return source_arms(row)


def included_campaigns(sources: dict) -> tuple[list[str], dict[str, str]]:
    """(campaigns needing a receipt, campaign -> source name).

    An excluded source needs no receipt for any arm, and an excluded arm of an
    included source needs none either. A source that declares no campaign needs
    none by construction.
    """
    campaigns: list[str] = []
    owner: dict[str, str] = {}
    for row in sources["sources"]:
        if not row.get("included", False):
            continue
        for arm in arms(row):
            if not arm.get("included", False):
                continue
            campaigns.append(arm["campaign"])
            owner[arm["campaign"]] = row["source"]
    return campaigns, owner


def exclusions(sources: dict) -> tuple[list[dict], list[str]]:
    """(the recorded exclusions, the entries that record no reason).

    The implementation is `combine_per_class.source_exclusions`. Ruling R16
    puts the derived route on the same reader, and two copies of the shape
    would be free to drift.
    """
    return source_exclusions(sources)


def agrees_with_combination_map(sources: dict) -> list[str]:
    """The declared map must equal the map the arithmetic actually applies.

    Two files naming the same thing is a drift risk, so a disagreement is a
    refusal rather than a comment. The comparison runs per arm, so excluding one
    arm in the contract and not in the arithmetic is caught here instead of
    surfacing later as a silently two-sided term.
    """
    declared: dict[str, tuple[str, ...]] = {}
    campaignless: set[str] = set()
    problems: list[str] = []
    for row in sources["sources"]:
        if not row.get("included", False):
            continue
        kept = tuple(a["campaign"] for a in arms(row) if a.get("included"))
        if not kept:
            if arms(row):
                problems.append(
                    f"source {row['source']} is included and every one of its "
                    "arms is excluded; a source with no measured arm cannot "
                    "contribute a term")
            campaignless.add(row["source"])
            continue
        declared[row["source"]] = kept

    for source, campaigns in sorted(SOURCES.items()):
        if source not in declared:
            problems.append(
                f"combine_per_class requires source {source} and "
                "config/systematics_sources_v1.json does not include it")
        elif declared[source] != campaigns:
            problems.append(
                f"source {source} maps to {declared[source]} in the contract "
                f"and to {campaigns} in combine_per_class")
    for source in sorted(set(declared) - set(SOURCES)):
        problems.append(
            f"source {source} is included in the contract and unknown to "
            "combine_per_class")
    if campaignless != set(CAMPAIGNLESS_TERMS):
        problems.append(
            "the contract includes campaignless sources "
            f"{sorted(campaignless)} and combine_per_class adds "
            f"{sorted(CAMPAIGNLESS_TERMS)}")
    return problems


# --------------------------------------------------------------------------
# Receipts and resolver tags
# --------------------------------------------------------------------------

def assert_receipts(campaigns: list[str], receipt_paths: dict[str, Path],
                    resolver_tags: dict[str, str]) -> tuple[dict, list[str]]:
    """One receipt per campaign, PASS, and agreeing with its resolver tag.

    The caller names every receipt path explicitly, exactly as
    `harvest_class_report.py` names every variation log. A receipt directory
    whose shape this tool guessed would resolve a wrong-but-plausible file
    after any layout change, and the run would look successful.
    """
    receipts: dict[str, dict] = {}
    reasons: list[str] = []
    for campaign in sorted(set(campaigns)):
        path = receipt_paths.get(campaign)
        if path is None:
            reasons.append(
                f"{campaign}: no measurement receipt was supplied")
            continue
        if not path.is_file():
            reasons.append(
                f"{campaign}: no measurement receipt at {path}")
            continue
        receipt = json.loads(path.read_text())
        if receipt.get("schema") != RECEIPT_SCHEMA:
            reasons.append(
                f"{campaign}: receipt schema is {receipt.get('schema')!r}, "
                f"expected {RECEIPT_SCHEMA!r}")
            continue
        if receipt.get("campaign") != campaign:
            reasons.append(
                f"{campaign}: receipt names campaign "
                f"{receipt.get('campaign')!r}")
            continue
        if receipt.get("completion_status") != "PASS":
            reasons.append(
                f"{campaign}: measurement receipt is "
                f"{receipt.get('completion_status')!r}, not PASS"
                + (f" ({'; '.join(receipt.get('failure_reasons') or [])})"
                   if receipt.get("failure_reasons") else ""))
            continue
        declared = resolver_tags.get(campaign)
        resolved = receipt.get("resolved_complete_root_tags")
        if declared is None:
            reasons.append(
                f"{campaign}: the dataset selector declares no complete-root "
                "tag for this campaign")
            continue
        if resolved != [declared]:
            reasons.append(
                f"{campaign}: receipt resolved {resolved!r}, the selector "
                f"declares {[declared]!r}")
            continue
        receipts[campaign] = {
            "receipt_sha256": sha256(path),
            "completion_status": receipt["completion_status"],
            "expected_complete_root_tag":
                receipt.get("expected_complete_root_tag"),
            "resolved_complete_root_tags": resolved,
        }
    return receipts, reasons


# --------------------------------------------------------------------------
# The class partition
# --------------------------------------------------------------------------

def contract_classes() -> list[str]:
    """The class set, read from the contract. Ruling R10: never a constant."""
    return class_names()


def expected_row_count(rows: list[dict], expected: list[str]) -> tuple[int, list[str]]:
    """(rows the contract requires, series that do not carry every class).

    The count is DERIVED: series times classes, plus one integrated row for
    each series that carries one. Writing 132 here would freeze the class set
    into a number, and a contract with ten classes would then look short by
    twelve rows rather than being ten classes long.
    """
    by_series: dict[tuple, set[str]] = {}
    for row in rows:
        key = (row["flavour"], row["trigger"], row["associate"], row["tune"])
        by_series.setdefault(key, set()).add(row["class"])
    required = set(expected)
    total = 0
    short: list[str] = []
    for key in sorted(by_series):
        seen = by_series[key]
        missing = sorted(required - seen, key=class_order)
        if missing:
            short.append(
                "series " + "/".join(key) + " carries no input row for "
                f"classes {missing}")
        total += len(required) + (1 if INTEGRATED in seen else 0)
    return total, short


def assert_partition(rows: list[dict], expected: list[str]) -> list[str]:
    """Every row's class must be in the v2 contract, and all of it covered.

    The integrated bin is not a percentile class and is allowed beside them.
    A class the contract does not define is a changed emission, not a row to
    drop quietly.
    """
    seen = {row["class"] for row in rows}
    allowed = set(expected) | {INTEGRATED}
    unknown = sorted(seen - allowed, key=lambda c: (len(c), c))
    if unknown:
        return [
            "class partition disagrees with "
            "config/multiplicity_percentile_classes_v2.json: "
            f"unknown classes {unknown}"]
    uncovered = sorted(set(expected) - seen, key=class_order)
    if uncovered:
        return [
            "class partition disagrees with "
            "config/multiplicity_percentile_classes_v2.json: "
            f"no input row for classes {uncovered}"]
    return []


# --------------------------------------------------------------------------
# Rows
# --------------------------------------------------------------------------

def build_rows(report: dict, campaign: str) -> list[dict]:
    """One envelope row per (tune, pair, class), combined by combine_cell."""
    by_cell: dict[tuple, dict[str, dict]] = {}
    for row in report["deltas"]:
        key = (row["flavour"], row["trigger"], row["associate"], row["tune"],
               row["class"])
        by_cell.setdefault(key, {})[row["campaign"]] = row

    rows = []
    for key in sorted(by_cell, key=lambda k: (k[:4], class_order(k[4]))):
        flavour, trigger, associate, tune, cls = key
        cells = by_cell[key]
        combined = combine_cell(cells)
        terms = {}
        for source, term in combined["terms_percent"].items():
            quoted = combined["quoted_arm"].get(source)
            raw = cells.get(quoted) if quoted else None
            terms[source] = {
                "campaign": quoted,
                # S5 is a measured structural zero with no campaign of its
                # own, so its absolute SEMs are zero by construction rather
                # than read from a variation row.
                "delta": raw["delta"] if raw else 0.0,
                "sem_var": raw["variation_sem"] if raw else 0.0,
                "sem_nominal": raw["nominal_sem"] if raw
                               else combined["nominal_yield"] * 0.0,
                "sem_delta": raw["delta_sem"] if raw else 0.0,
                "contribution": term["contribution"]
                                * combined["nominal_yield"] / 100.0,
                "delta_percent": term["delta"],
                "sem_delta_percent": term["sem"],
                "contribution_percent": term["contribution"],
            }
        nominal_sem = next(
            (r["nominal_sem"] for r in cells.values()), 0.0)
        rows.append({
            "campaign": campaign,
            "tune": tune,
            "flavour": flavour,
            "trigger": trigger,
            "associate": associate,
            "observable": OBSERVABLE,
            "class": cls,
            "nominal_yield": combined["nominal_yield"],
            "nominal_sem": nominal_sem,
            "terms": terms,
            "quoted_arm": combined["quoted_arm"],
            "dropped": combined["dropped"],
            "combined_percent": combined["combined_percent"],
            "combined_absolute": combined["combined_absolute"],
        })
    return rows


# --------------------------------------------------------------------------
# Assembly
# --------------------------------------------------------------------------

def producing_commit() -> str:
    try:
        return subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def build(report_path: Path, receipt_paths: dict[str, Path],
          resolver_tags: dict[str, str], campaign: str, nominal_dataset: str,
          boundary_receipt_sha: str) -> tuple[dict, list[str], str]:
    """(envelope, reasons, status). Never raises for a declared refusal."""
    reasons: list[str] = []
    status = "COMPLETE"
    rows: list[dict] = []
    receipts: dict = {}
    expected_rows = 0

    sources = load_json(SOURCES_CONTRACT, SOURCES_SCHEMA)
    drift = agrees_with_combination_map(sources)
    if drift:
        reasons += drift
        status = "FAIL"

    # Every exclusion travels into the envelope with its reason. A reader who
    # asks why S3 is one-sided must find the answer in the artifact, not in a
    # commit message.
    recorded_exclusions, unreasoned = exclusions(sources)
    if unreasoned:
        reasons += unreasoned
        status = "FAIL"

    campaigns, _owner = included_campaigns(sources)
    receipts, receipt_reasons = assert_receipts(
        campaigns, receipt_paths, resolver_tags)
    if receipt_reasons:
        reasons += receipt_reasons
        # A receipt that exists and reports FAIL, or that contradicts its
        # resolver tag, is a contradiction. A receipt that is simply absent is
        # an incomplete input. The two deserve different names.
        contradiction = any(
            "not PASS" in r or "resolved" in r or "schema" in r
            or "names campaign" in r
            for r in receipt_reasons)
        status = "FAIL" if contradiction or status == "FAIL" else "INCOMPLETE"

    if status != "FAIL":
        report = load_json(report_path, DELTA_REPORT_SCHEMA)
        partition = assert_partition(report["deltas"], contract_classes())
        if partition:
            reasons += partition
            status = "FAIL"
        else:
            expected_rows, short = expected_row_count(
                report["deltas"], contract_classes())
            if short:
                reasons += short
                status = "FAIL"
            try:
                rows = build_rows(report, campaign)
            except SourcesIncomplete as error:
                reasons.append(str(error))
                if status == "COMPLETE":
                    status = "INCOMPLETE"
            except (KeyError, ZeroDivisionError, ValueError) as error:
                reasons.append(f"cannot combine: {error}")
                status = "FAIL"

    if status == "COMPLETE" and len(rows) != expected_rows:
        reasons.append(
            f"the envelope holds {len(rows)} rows and "
            "config/multiplicity_percentile_classes_v2.json requires "
            f"{expected_rows}")
        status = "FAIL"
    if status == "COMPLETE" and not rows:
        reasons.append("no envelope row was produced")
        status = "INCOMPLETE"
    if status == "COMPLETE" and not boundary_receipt_sha:
        reasons.append(
            "no nominal boundary-receipt sha256 was supplied; the envelope "
            "cannot be bound to the render it applies to")
        status = "INCOMPLETE"

    envelope = {
        "schema": ENVELOPE_SCHEMA,
        "status": status,
        "missing": reasons,
        "method": METHOD_TAGS,
        "sources": sources["sources"],
        "exclusions": recorded_exclusions,
        "rows": rows,
        "provenance": {
            "producing_commit": producing_commit(),
            "sources_contract_sha256": sha256(SOURCES_CONTRACT),
            "envelope_contract_sha256": sha256(ENVELOPE_CONTRACT),
            "class_contract_sha256": sha256(CLASS_CONTRACT),
            "class_contract_classes": contract_classes(),
            "expected_rows": expected_rows,
            "delta_report_sha256":
                sha256(report_path) if report_path.is_file() else "",
            "measurement_receipts": receipts,
            "resolver_tags": dict(sorted(resolver_tags.items())),
            "nominal_boundary_receipt_sha256": boundary_receipt_sha,
            "nominal_dataset": nominal_dataset,
            "nominal_campaign": campaign,
        },
    }
    return envelope, reasons, status


def promote(envelope: dict, out: Path) -> None:
    """Stage beside the destination, then rename. Never a partial COMPLETE."""
    if "plotting" in out.parts or any(
            part.startswith("plotting") and part != "plotting-syst"
            for part in out.parts):
        raise SystemExit(
            f"REFUSING: an envelope may not be written under a plotting "
            f"output plane: {out}")
    out.parent.mkdir(parents=True, exist_ok=True)
    staged = out.parent / (out.name + ".staging")
    staged.write_text(json.dumps(envelope, indent=1, sort_keys=True) + "\n")
    os.replace(staged, out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--report", type=Path, required=True,
                    help="per_class_deltas.json from harvest_class_report.py")
    ap.add_argument("--receipt", action="append", default=[],
                    metavar="CAMPAIGN=PATH",
                    help="one measurement receipt; repeat once per campaign")
    ap.add_argument("--campaign", required=True,
                    help="the NOMINAL campaign the envelope applies to")
    ap.add_argument("--nominal-dataset", required=True)
    ap.add_argument("--resolver-tags", type=Path, required=True,
                    help="JSON object: campaign -> declared complete-root tag")
    ap.add_argument("--boundary-receipt-sha", default="",
                    help="sha256 of the nominal render's boundary receipt")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    resolver_tags = json.loads(args.resolver_tags.read_text())
    receipt_paths: dict[str, Path] = {}
    for spec in args.receipt:
        name, sep, path = spec.partition("=")
        if not sep or not name or not path:
            raise SystemExit(f"REFUSING: --receipt needs CAMPAIGN=PATH, got {spec!r}")
        receipt_paths[name] = Path(path)
    try:
        envelope, reasons, status = build(
            args.report, receipt_paths, resolver_tags, args.campaign,
            args.nominal_dataset, args.boundary_receipt_sha)
    except EnvelopeRefused as error:
        envelope = {
            "schema": ENVELOPE_SCHEMA,
            "status": error.status,
            "missing": error.reasons,
            "method": METHOD_TAGS,
            "sources": [],
            "exclusions": [],
            "rows": [],
            "provenance": {"producing_commit": producing_commit()},
        }
        reasons, status = error.reasons, error.status

    promote(envelope, args.out)
    print(f"SYSTEMATICS_ENVELOPE status={status} rows={len(envelope['rows'])} "
          f"missing={len(reasons)} out={args.out}")
    for reason in reasons:
        print(f"ENVELOPE_REFUSED {reason}")
    return 0 if status == "COMPLETE" else 5


if __name__ == "__main__":
    raise SystemExit(main())
