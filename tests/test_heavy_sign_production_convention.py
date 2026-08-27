#!/usr/bin/env python3
"""Require `heavy_flavour_sign` to match the production convention.

The builder once inverted beauty mesons and baryons relative to HeavyFlavourUtils.h.

The builder's I2 invariant compares a parent's sign to
its daughter's using this same helper on both sides. An inverted helper inverts
both sides, so I2 passed by common inversion. **A check written in terms of the
thing it is checking cannot fail.** The committed map values never changed
because the only species splits are charm-only -- so the defect was silent in
the artifacts and live only in the advertised absolute q_b convention.

The production definition is `q_c = n_c - n_cbar`, `q_b = n_b - n_bbar`.
`DecodeHeavyContent` derives these values from PDG digits.
Baryon codes are all-quark, so a positive beauty
baryon has q_b = +1. For mesons the larger-flavour constituent is a quark when
its digit is even and an antiquark when odd, so B+ (521) is `u bbar`, q_b = -1.

Four checks:
  1. the worked examples the production tests themselves use;
  2. all 202 species against `species_ordinals_v2.json` (production q_c/q_b);
  3. a negative control -- an inverted helper must be REJECTED, or check 2
     would pass for any helper;
  4. charm was never wrong, and must stay right.

"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
from build_decay_parent_map import (  # noqa: E402
    assert_production_convention,
    heavy_flavour_sign,
)

ORDINALS = REPO / "contracts/species_ordinals_v2.json"

# The production convention, stated as values rather than as a rule, so that a
# future "simplification" of the rule has to face the examples.
#   pdg  -> (heavy flavour, sign)
WORKED_EXAMPLES = {
    521: (5, -1),    # B+ = u bbar, so q_b = -1.
    -521: (5, +1),   # B-
    511: (5, -1),    # B0   = d bbar
    -511: (5, +1),   # B0bar
    5122: (5, +1),   # Lambda_b0 = udb, so q_b = +1.
    -5122: (5, -1),  # Lambda_b0bar
    411: (4, +1),    # D+   = c dbar  -> q_c = +1
    -411: (4, -1),   # D-
    421: (4, +1),    # D0   = c ubar
    4122: (4, +1),   # Lambda_c+ = udc
    -4122: (4, -1),  # Lambda_c+bar
}

failures = []


def check(label, condition, detail=""):
    if condition:
        print(f"  PASS {label}")
    else:
        print(f"  FAIL {label} {detail}")
        failures.append(label)


# --- 1. worked examples -------------------------------------------------------
wrong = {pdg: (heavy_flavour_sign(pdg), want)
         for pdg, want in WORKED_EXAMPLES.items()
         if heavy_flavour_sign(pdg) != want}
check("worked examples match the production convention", not wrong,
      "; ".join(f"{p}: got {g} want {w}" for p, (g, w) in list(wrong.items())[:4]))

# Stated separately because these two are the ones that were backwards.
check("B+ has q_b = -1 (meson, odd heavy digit -> antiquark)",
      heavy_flavour_sign(521) == (5, -1), heavy_flavour_sign(521))
check("Lambda_b0 has q_b = +1 (baryon code is all-quark)",
      heavy_flavour_sign(5122) == (5, +1), heavy_flavour_sign(5122))

# --- 2. all 202 species against the production artifact ----------------------
try:
    checked = assert_production_convention(ORDINALS)
    check("all species agree with production q_c/q_b", checked >= 200,
          f"only {checked} rows were testable")
except SystemExit as exc:
    check("all species agree with production q_c/q_b", False, str(exc)[:200])

# --- 3. negative control: an inverted helper must be REJECTED ----------------
# Without this, check 2 would pass for a helper that is wrong in the same way
# the artifact is -- which is precisely the failure mode being fixed.
import build_decay_parent_map as builder  # noqa: E402

original = builder.heavy_flavour_sign


def inverted(pdg):
    heavy, sign = original(pdg)
    return (heavy, -sign) if heavy == 5 else (heavy, sign)


builder.heavy_flavour_sign = inverted
try:
    assert_production_convention(ORDINALS)
    check("negative control: an inverted beauty helper is rejected", False,
          "the inverted helper was ACCEPTED")
except SystemExit as exc:
    check("negative control: an inverted beauty helper is rejected",
          "FAIL-CLOSED I2a" in str(exc), str(exc)[:120])
finally:
    builder.heavy_flavour_sign = original

# --- 4. charm was never wrong ------------------------------------------------
payload = json.loads(ORDINALS.read_text())
charm_bad = []
for row in payload["species"]:
    if row["n_beauty"] or not row["q_c"]:
        continue
    heavy, sign = heavy_flavour_sign(int(row["pdg"]))
    if heavy != 4 or sign != (1 if row["q_c"] > 0 else -1):
        charm_bad.append(row["pdg"])
check("charm-only species were correct before and remain correct",
      not charm_bad, charm_bad[:6])

print(f"\n{len(failures)} failure(s)")
sys.exit(1 if failures else 0)
