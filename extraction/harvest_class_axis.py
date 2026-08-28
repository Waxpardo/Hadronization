#!/usr/bin/env python3
"""Parse tune-local percentile classes from an UNCERTAINTY_MATRIX log.

The `bin` histogram name encodes the class; no separate field carries it:

    hDPhiM90_100            class c1, tune-local percentile window 90-100
    hDPhiM0_1               class c11, tune-local percentile window 0-1
    hDPhiM00_100            the multiplicity-INTEGRATED bin

`p` is the decimal point. The five-field key prevents window-label collisions.

The window is a top percentile, so a high percentile means low N_ch. `c1` is
the lowest-activity class and `c11` is the highest.

Every tune resolves its own percentile edges from its own merged summed
MULTIPLICITY histogram. No minimum-bias tune and no common absolute N_ch
boundary defines another tune's classes, so no fixed N_ch range belongs here.
`config/multiplicity_percentile_classes_v2.json` holds the windows and the tie
rule: a threshold integer belongs to the lower-activity class, and the adjacent
higher-activity class starts at that integer plus one. Under ruling R10 that
file is the ONE source of the class set. `contract_classes`, `class_names`,
`class_count`, `class_bins` and `class_by_window` below read it, and no module
in this repository may enumerate the classes itself.

`LEGACY_CLASS_BIN` below still parses the retired `hDPhic<N>_MB<lo>_<hi>` names.
Those labels carry the percentile edges of one retired axis.
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLASS_CONTRACT = ROOT / "config" / "multiplicity_percentile_classes_v2.json"

CLASS_BIN = re.compile(r"^hDPhiM(?P<lo>\d+)_(?P<hi>\d+)$")
LEGACY_CLASS_BIN = re.compile(
    r"^hDPhi(?P<cls>c\d+)_MB(?P<lo>[0-9p]+)_(?P<hi>[0-9p]+)$")
INTEGRATED = "MB"
INTEGRATED_BIN = "hDPhiM00_100"
UNCERTAINTY_MATRIX_SCHEMA = "hadronization_uncertainty_matrix_v2"


def contract_classes() -> list[dict]:
    """The class rows of the contract, in contract order.

    Ruling R10 makes `config/multiplicity_percentile_classes_v2.json` the ONE
    place the class set is written down. Every count, label and window below
    comes from here, so changing the class set means editing that file and
    regenerating -- never editing an enumeration in code.
    """
    return json.loads(CLASS_CONTRACT.read_text())["classes"]


def class_names() -> list[str]:
    """c1..cN in contract order, ascending event activity."""
    return [row["class"] for row in contract_classes()]


def class_count() -> int:
    return len(contract_classes())


def class_bins() -> dict[str, str]:
    """class name -> its histogram bin label, for example c1 -> M90_100."""
    return {row["class"]: row["bin"] for row in contract_classes()}


def class_by_window() -> dict[tuple[float, float], str]:
    """(percentile_min, percentile_max) -> class name."""
    return {(float(row["percentile_min"]), float(row["percentile_max"])):
            row["class"] for row in contract_classes()}


# Read once at import. An unreadable or malformed contract stops every consumer
# here rather than letting one of them guess a class set.
CLASS_BY_WINDOW = class_by_window()


def percentile(token: str) -> float:
    """`88p197` -> 88.197. `p` is the decimal point in a ROOT object name."""
    return float(token.replace("p", "."))


def parse_bin(name: str) -> tuple[str, float, float]:
    """(class, window_low, window_high). Raises on an unparsed name.

    Fail closed: an unrecognised bin name is a changed emission, not a row to
    skip quietly.
    """
    if name == INTEGRATED_BIN:
        return INTEGRATED, 0.0, 100.0
    m = CLASS_BIN.match(name)
    if m:
        window = (percentile(m.group("lo")), percentile(m.group("hi")))
        if window in CLASS_BY_WINDOW:
            return CLASS_BY_WINDOW[window], *window
    # Read-only compatibility for archived pre-rebuild logs. New configs never
    # emit this MONASH-MB form.
    m = LEGACY_CLASS_BIN.match(name)
    if m:
        return m.group("cls"), percentile(m.group("lo")), percentile(m.group("hi"))
    raise ValueError(f"unparsed UNCERTAINTY_MATRIX bin name: {name!r}")


def class_order(cls: str) -> int:
    """c1 < c2 < ... < cN < MB. Sorting on the string puts c10 before c2."""
    return 999 if cls == INTEGRATED else int(cls[1:])


def sample_sem(values: list[float]) -> float:
    """Sample SEM over aligned blocks: sqrt(sum((x-mean)^2) / n(n-1))."""
    if len(values) < 2:
        raise ValueError(f"need at least two blocks for a sample SEM, got {len(values)}")
    mean = sum(values) / len(values)
    return math.sqrt(
        sum((value - mean) ** 2 for value in values)
        / (len(values) * (len(values) - 1)))


def _context(fields: dict[str, str], cls: str) -> str:
    return f"{fields.get('tune', '<missing tune>')}/{cls}"


def _block_vector(fields: dict[str, str], cls: str, field: str,
                  block_count: int, *, allow_na: bool = False
                  ) -> list[float] | None:
    context = _context(fields, cls)
    if field not in fields:
        raise ValueError(f"{context} {field}: field is absent")
    raw = fields[field]
    if raw == "NA":
        if allow_na:
            return None
        raise ValueError(f"{context} {field}: NA is forbidden")
    tokens = raw.split(",")
    if len(tokens) != block_count:
        raise ValueError(
            f"{context} {field}: expected {block_count} elements, got {len(tokens)}")
    try:
        values = [float(token) for token in tokens]
    except ValueError as error:
        raise ValueError(f"{context} {field}: malformed numeric vector {raw!r}") from error
    if any(not math.isfinite(value) for value in values):
        raise ValueError(f"{context} {field}: vector contains a non-finite value")
    return values


def _summary_sem(fields: dict[str, str], cls: str, field: str,
                 values: list[float]) -> None:
    context = _context(fields, cls)
    try:
        observed = float(fields[field])
    except (KeyError, ValueError) as error:
        raise ValueError(f"{context} {field}: absent or malformed summary SEM") from error
    if not math.isfinite(observed) or observed < 0.0:
        raise ValueError(f"{context} {field}: summary SEM is non-finite or negative")
    expected = sample_sem(values)
    if not math.isclose(observed, expected, rel_tol=5e-15, abs_tol=0.0):
        raise ValueError(
            f"{context} {field}: {observed:.17g} disagrees with block-vector "
            f"SEM {expected:.17g}")


def _validate_block_contract(fields: dict[str, str], cls: str) -> None:
    context = _context(fields, cls)
    if fields.get("schema") != UNCERTAINTY_MATRIX_SCHEMA:
        raise ValueError(
            f"{context} schema: expected {UNCERTAINTY_MATRIX_SCHEMA!r}, "
            f"got {fields.get('schema')!r}")
    try:
        block_count = int(fields["block_count"])
    except (KeyError, ValueError) as error:
        raise ValueError(f"{context} block_count: absent or malformed") from error
    if block_count < 2:
        raise ValueError(f"{context} block_count: expected at least 2, got {block_count}")
    if fields.get("is_reference") not in {"true", "false"}:
        raise ValueError(f"{context} is_reference: expected true or false")

    yields = _block_vector(fields, cls, "block_yields", block_count)
    assert yields is not None
    _summary_sem(fields, cls, "yield_sem", yields)
    is_reference = fields["is_reference"] == "true"
    ratios = _block_vector(
        fields, cls, "block_ratios", block_count, allow_na=is_reference)
    if is_reference:
        if ratios is not None:
            raise ValueError(f"{context} block_ratios: reference row must be NA")
        if fields.get("ratio_sem") != "NA":
            raise ValueError(f"{context} ratio_sem: reference row must be NA")
    else:
        assert ratios is not None
        _summary_sem(fields, cls, "ratio_sem", ratios)

    fields["block_count"] = block_count
    fields["block_yields"] = yields
    fields["block_ratios"] = ratios


def _validate_ratios_against_reference(
    rows: dict[tuple[str, str, str, str, str], dict]
) -> None:
    grouped: dict[tuple[str, str, str, str], list[tuple[tuple, dict]]] = {}
    for key, row in rows.items():
        group = (key[0], key[1], key[2], key[4])
        grouped.setdefault(group, []).append((key, row))
    for group, members in grouped.items():
        references = [(key, row) for key, row in members
                      if row["is_reference"] == "true"]
        if len(references) != 1:
            tune, cls = group[2], group[3]
            raise ValueError(
                f"{tune}/{cls} block_yields: expected exactly one reference row, "
                f"got {len(references)}")
        _, reference = references[0]
        for key, row in members:
            if row["is_reference"] == "true":
                continue
            for block, (numerator, denominator, ratio) in enumerate(zip(
                    row["block_yields"], reference["block_yields"],
                    row["block_ratios"]), start=1):
                if denominator == 0.0:
                    raise ValueError(
                        f"{key[2]}/{key[4]} block_ratios: reference yield is zero "
                        f"in block {block}")
                expected = numerator / denominator
                if ratio != expected:
                    raise ValueError(
                        f"{key[2]}/{key[4]} block_ratios: block {block} is "
                        f"{ratio:.17g}, expected same-block ratio {expected:.17g}")


def parse_log(text: str, *, validate_block_contract: bool = True
              ) -> dict[tuple[str, str, str, str, str], dict]:
    """Every UNCERTAINTY_MATRIX row, keyed on the five-field identity.

    Current consumers validate the v2 block-vector contract by default. The
    opt-out exists only for explicit integrity checks over archived logs; it
    must never feed endpoint or covariance arithmetic.
    """
    rows: dict[tuple[str, str, str, str, str], dict] = {}
    for line in text.splitlines():
        if not line.startswith("UNCERTAINTY_MATRIX"):
            continue
        fields = dict(t.split("=", 1) for t in line.split() if "=" in t)
        cls, low, high = parse_bin(fields["bin"])
        fields["class"] = cls
        fields["percentile_low"], fields["percentile_high"] = low, high
        # Compatibility aliases for archived extraction tables.
        fields["mb_low"], fields["mb_high"] = low, high
        if validate_block_contract:
            _validate_block_contract(fields, cls)
        key = (fields["flavour"], fields["trigger"], fields["tune"],
               fields["associate"], cls)
        if key in rows:
            raise ValueError(f"duplicate identity in one log: {key}")
        rows[key] = fields
    if validate_block_contract:
        _validate_ratios_against_reference(rows)
    return rows


def significant_figures(printed: str) -> int:
    """How many significant figures a printed value actually records.

    Split the exponent off first: `9.35056e-05` records 6, and counting the
    exponent's digits would ask for a precision the log never carried.
    """
    mantissa = printed.split("e")[0].split("E")[0]
    digits = len(mantissa.replace("-", "").replace(".", "").lstrip("0"))
    return max(digits, 1)


def agrees_at_recorded_precision(a: str, b: str) -> bool:
    """Compare two printed values at the precision of the LESS precise one.

    This introduces no numeric tolerance. It is the figure branch's own method
    for comparing logs written by macros that printed different digit counts,
    and a real disagreement at the recorded precision still fails.
    """
    if a == b:
        return True
    digits = min(significant_figures(a), significant_figures(b))
    fmt = "%%.%dg" % digits
    return fmt % float(a) == fmt % float(b)


# ---------------------------------------------------------------------------
# THE RESOLVER ASSERTION.
#
# THE DEFECT IT CLOSES, 2026-08-19. Five variation renders loaded the
# configuration they were given, echoed its sha, passed every assertion written
# about class windows, boundary artifact and bin names -- and read the CENTRAL
# campaign's data. The sealed dataset selector exports
# HADRONIZATION_COMPLETE_ROOT_TAG, and the driver passes it to the macro, where
# it wins over the configuration's own directories.
#
# THE CONFIGURATION IS A REQUEST. THE RESOLVER LINE IS THE ANSWER. The answer
# was in the first twenty lines of every log from the first render, and nothing
# read it until the numbers looked wrong.
# ---------------------------------------------------------------------------

RESOLVER = re.compile(
    r"^(?P<sector>Beauty|Charm) (?P<kind>central|subsample) resolver "
    r"(?P<tune>\w+): base=(?P<base>[^,\s]+)(?:,\s*tag=(?P<tag>\S+))?$")


def resolved_campaigns(log_text: str) -> dict[str, set[str]]:
    """Campaign tags the render actually resolved, by resolver kind.

    Reads `tag=complete_root_<CAMPAIGN>` for central resolvers and the
    `SUBSAMPLES_<CAMPAIGN>` element of the subsample base.
    """
    found: dict[str, set[str]] = {"central": set(), "subsample": set()}
    for line in log_text.splitlines():
        m = RESOLVER.match(line.strip())
        if not m:
            continue
        if m.group("kind") == "central":
            tag = m.group("tag") or ""
            if tag.startswith("complete_root_"):
                found["central"].add(tag[len("complete_root_"):])
        else:
            for part in m.group("base").split("/"):
                if part.startswith("SUBSAMPLES_"):
                    found["subsample"].add(part[len("SUBSAMPLES_"):])
    return found


def assert_resolved_campaign(log_text: str, campaign: str) -> dict[str, set[str]]:
    """Refuse a render whose resolved input is not the campaign requested.

    Fail closed on absence too: a log with no resolver line is a log that
    cannot answer the question, which is not the same as an answer.
    """
    found = resolved_campaigns(log_text)
    if not found["central"] and not found["subsample"]:
        raise ValueError(
            "RESOLVER ASSERTION: the log carries no resolver line, so the "
            "dataset it read cannot be established from it")
    wrong = {kind: sorted(tags - {campaign})
             for kind, tags in found.items() if tags - {campaign}}
    if wrong:
        raise ValueError(
            f"RESOLVER ASSERTION FAILED: requested {campaign!r}, but the render "
            f"resolved {wrong}. The configuration is a request; this line is "
            "the answer.")
    if campaign not in found["central"]:
        raise ValueError(
            f"RESOLVER ASSERTION: no central resolver named {campaign!r}; "
            f"central resolvers named {sorted(found['central'])}")
    return found
