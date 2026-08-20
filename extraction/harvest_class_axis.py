#!/usr/bin/env python3
"""The class axis of the plotter's UNCERTAINTY_MATRIX log, and its parsing rule.

The class is NOT a separate field. It is encoded in the histogram name carried
by `bin`, and a session that read `binFromTHnSparse.hDPhi` as a Delta-phi index
from the variable's name got this wrong for a day (run record 17.4, corrected
in 18.1). Read the name:

    hDPhic1_MB88p197_100    class c1,  MONASH-MB percentile window 88.197-100
    hDPhic11_MB0_8p422      class c11, window 0-8.422
    hDPhiM00_100            the multiplicity-INTEGRATED bin

`p` is the decimal point. The key keeps all five fields GOLDEN_OUTPUTS 9.9.1
requires, with the class in place of the raw bin string, so that a variation's
window label cannot collide with the central's.

THE PERCENTILE RUNS THE OTHER WAY FROM THE MULTIPLICITY, AND THE LABEL INVITES
THE OPPOSITE READING. The window is a TOP percentile -- the fraction of
minimum-bias events ABOVE the boundary -- so a high percentile is a LOW N_ch.
The render log states the mapping outright:

    MULTIPLICITY_BOUNDARY percentile=100     nch=0
    MULTIPLICITY_BOUNDARY percentile=88.197  nch=2
    MULTIPLICITY_BOUNDARY percentile=8.422   nch=32
    MULTIPLICITY_BOUNDARY percentile=0       nch=4095

So `c1`, labelled `MB88p197_100`, is N_ch 0 to 2, the LOWEST multiplicity, and
`c11`, labelled `MB0_8p422`, is N_ch 33 and above, the HIGHEST. That agrees with
`config/multiplicity_class_boundaries_v1.json`, where `c1` spans [-0.5, 2.5) and
`c11` is open-ended above 32.5. Reading the label as an ordinary percentile
inverts every per-class trend in the tables.
"""

from __future__ import annotations

import re

CLASS_BIN = re.compile(r"^hDPhi(?P<cls>c\d+)_MB(?P<lo>[0-9p]+)_(?P<hi>[0-9p]+)$")
INTEGRATED_BIN = re.compile(r"^hDPhiM(?P<lo>\d+)_(?P<hi>\d+)$")
INTEGRATED = "MB"


def percentile(token: str) -> float:
    """`88p197` -> 88.197. `p` is the decimal point in a ROOT object name."""
    return float(token.replace("p", "."))


def parse_bin(name: str) -> tuple[str, float, float]:
    """(class, window_low, window_high). Raises on an unparsed name.

    Fail closed: an unrecognised bin name is a changed emission, not a row to
    skip quietly.
    """
    m = CLASS_BIN.match(name)
    if m:
        return m.group("cls"), percentile(m.group("lo")), percentile(m.group("hi"))
    m = INTEGRATED_BIN.match(name)
    if m:
        return INTEGRATED, float(m.group("lo")), float(m.group("hi"))
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
        fields["class"], fields["mb_low"], fields["mb_high"] = cls, low, high
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
