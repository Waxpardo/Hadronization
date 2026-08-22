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
`config/multiplicity_percentile_classes_v2.json` holds the eleven windows and
the tie rule: a threshold integer belongs to the lower-activity class, and the
adjacent higher-activity class starts at that integer plus one.

`LEGACY_CLASS_BIN` below still parses the retired `hDPhic<N>_MB<lo>_<hi>` names.
Those labels carry the percentile edges of one retired axis.
"""

from __future__ import annotations

import re

CLASS_BIN = re.compile(r"^hDPhiM(?P<lo>\d+)_(?P<hi>\d+)$")
LEGACY_CLASS_BIN = re.compile(
    r"^hDPhi(?P<cls>c\d+)_MB(?P<lo>[0-9p]+)_(?P<hi>[0-9p]+)$")
CLASS_BY_WINDOW = {
    (90.0, 100.0): "c1", (80.0, 90.0): "c2",
    (70.0, 80.0): "c3", (60.0, 70.0): "c4",
    (50.0, 60.0): "c5", (40.0, 50.0): "c6",
    (30.0, 40.0): "c7", (20.0, 30.0): "c8",
    (10.0, 20.0): "c9", (1.0, 10.0): "c10",
    (0.0, 1.0): "c11",
}
INTEGRATED = "MB"


def percentile(token: str) -> float:
    """`88p197` -> 88.197. `p` is the decimal point in a ROOT object name."""
    return float(token.replace("p", "."))


def parse_bin(name: str) -> tuple[str, float, float]:
    """(class, window_low, window_high). Raises on an unparsed name.

    Fail closed: an unrecognised bin name is a changed emission, not a row to
    skip quietly.
    """
    if name == "hDPhiM00_100":
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
    """c1 < c2 < ... < c11 < MB. Sorting on the string puts c10 before c2."""
    return 999 if cls == INTEGRATED else int(cls[1:])


def parse_log(text: str) -> dict[tuple[str, str, str, str, str], dict[str, str]]:
    """Every UNCERTAINTY_MATRIX row, keyed on the five-field identity."""
    rows: dict[tuple[str, str, str, str, str], dict[str, str]] = {}
    for line in text.splitlines():
        if not line.startswith("UNCERTAINTY_MATRIX"):
            continue
        fields = dict(t.split("=", 1) for t in line.split() if "=" in t)
        cls, low, high = parse_bin(fields["bin"])
        fields["class"] = cls
        fields["percentile_low"], fields["percentile_high"] = low, high
        # Compatibility aliases for archived extraction tables.
        fields["mb_low"], fields["mb_high"] = low, high
        key = (fields["flavour"], fields["trigger"], fields["tune"],
               fields["associate"], cls)
        if key in rows:
            raise ValueError(f"duplicate identity in one log: {key}")
        rows[key] = fields
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
