#!/usr/bin/env python3
"""Assemble the F4 decay-parent artifact from the PYTHIA-linked probe's output.

WHAT F4 IS FOR. The extraction's experiment-comparable regrouping needs to know,
for each of the 202 sector-charged species, what the generator says it decays
into. Nothing else unblocks that regrouping: the diquark-structure grouping comes
free from the ordinal table's category column, but the decay-parent convention --
the one an experiment can compare against -- needs the generator's own tables.

DERIVED, NEVER HAND-WRITTEN. A typed-in map is not acceptable, because a hand
table drifts silently from the generator it claims to
describe. Every row here comes from `f4_probe`, linked against the **pinned
8.317 install** the producer itself links against.

THE GATE THAT HAD TO PASS FIRST. The producer disables decays for every heavy
hadron (`heavyflavourcorrelations_status.cpp:373`). If disabling also cleared the
channel tables, the map would have to be derived BEFORE the stabilisation pass --
both paths were open. **Measured: all 202
species keep every channel after `mayDecay(id,false)`**, so the map derives in
the state the analysis actually runs in. The probe re-checks this on every run
and this assembler refuses output if the verdict is not `READABLE_AFTER_DISABLE`.

FAIL-CLOSED, on four conditions:

  - the probe's gate verdict must be `READABLE_AFTER_DISABLE`;
  - the probe must have run against the expected PYTHIA version;
  - the species set must be **exactly** the ordinal table's -- no missing, no
    extra. The ordinal table is itself derived from a raw file's
    `heavy_stability_audit` tree, so set-equality against it is set-equality
    against the stability tree;
  - no species may report `ABSENT_FROM_PARTICLE_DATA`.

Usage:
  tools/build_decay_parent_map.py PROBE_OUT --ordinals species_ordinals.json \\
      --out decay_parent_map.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

SCHEMA = "hf_decay_parent_map_v1_1"
EXPECTED_PYTHIA = "8.317"

# --- CONJUGATION -------------------------------------------------------------
# PYTHIA stores ONE decay table per particle and derives the antiparticle by
# conjugation: particleDataEntryPtr(-413) returns the +413 entry. The probe
# therefore reports UNCONJUGATED products for negative ids, and v1 recorded them
# verbatim -- which mapped D*- and D*bar0 to D0 instead of D0bar and put a 4.49x
# charge asymmetry into the published table. See docs/MAP_V1_CONJUGATION_BUG.md.
#
# The probe's record is CORRECT AS A RECORD; conjugation is interpretation, so
# it lives here and the probe output stays untouched raw material.

GAUGE_SELF_CONJUGATE = {21, 22, 23, 25}


def self_conjugate(pdg: int) -> bool:
    """True if the species has no distinct antiparticle.

    Decided from the PDG code's quark digits rather than a hand-written list:
    a flavourless neutral meson has equal quark digits (pi0 111, eta 221,
    eta' 331, rho0 113, omega 223, phi 333, J/psi 443, Upsilon 553).
    """
    a = abs(pdg)
    if a in GAUGE_SELF_CONJUGATE:
        return True
    if 81 <= a <= 100:            # PYTHIA internal / string placeholder codes
        return True
    s = str(a)
    if len(s) == 3:
        return s[0] == s[1]
    if len(s) == 4:
        return s[0] == "0" and s[1] == s[2]     # excited meson; baryons never
    if len(s) >= 5:
        return s[-3] == s[-2]
    return False


def conjugate_products(products: list[int]) -> list[int]:
    return [p if self_conjugate(p) else -p for p in products]


def heavy_flavour_sign(pdg: int) -> tuple[int, int]:
    """(heavy flavour 4/5/0, quantum-number sign) in the PRODUCTION convention.

    THE CONVENTION IS NOT THIS FILE'S TO CHOOSE. It is fixed by
    `generation/producer/HeavyFlavourUtils.h`: `q_c = n_c - n_cbar`,
    `q_b = n_b - n_bbar`, with the quark content decoded from the PDG digits by
    `DecodeHeavyContent`. Two rules follow from that decoding:

      * **Baryons.** A positive baryon code is made of QUARKS, so a positive
        beauty baryon has `q_b = +1`. Lambda_b0 (5122) -> +1.
      * **Mesons.** For a positive meson code the larger-flavour constituent is
        a quark when its digit is EVEN and an antiquark when ODD. Charm is 4
        (even) so D+ (411) has `q_c = +1`; beauty is 5 (odd) so B+ (521) is
        `u bbar` and has `q_b = -1`.

    CORRECTED 2026-08-13. This function previously read
    "the sign follows the code for mesons and for charm baryons, but INVERTS for
    beauty baryons". That is backwards on both counts: relative to production it
    inverted beauty MESONS (returning +1 for B+ where production gives -1) and
    inverted beauty BARYONS (returning -1 for Lambda_b0 where production gives
    +1). Charm was, and remains, correct.

    The old error was invisible because the I2 check below compared this helper
    against ITSELF -- parent and daughter both inverted, so the comparison
    passed by common inversion. `assert_production_convention()` now pins it to
    the production values instead.
    """
    # Digit extraction mirrors DecodeHeavyContent exactly: n_q1 n_q2 n_q3 are
    # the three quark digits, and n_q1 == 0 is what distinguishes a meson from a
    # baryon. Slicing the decimal STRING by length was wrong for five-digit
    # excited BARYONS -- 14122 (Lambda_c(2593)+) was read as a meson made of
    # digits (1,2), returned "not heavy", and was then skipped by I2 entirely.
    # Two species were invisible to the invariant that way.
    identifier = abs(pdg)
    if identifier < 100:
        return 0, 0
    q1 = (identifier // 1000) % 10
    q2 = (identifier // 100) % 10
    q3 = (identifier // 10) % 10
    is_baryon = q1 != 0
    quarks = [q1, q2, q3] if is_baryon else [q2, q3]
    heavy = max((q for q in quarks if q in (4, 5)), default=0)
    if heavy == 0:
        return 0, 0
    sign = 1 if pdg > 0 else -1
    # Mesons only: an odd heavy digit in a positive code is an ANTIquark.
    # Baryon codes are all-quark, so they take the code's sign unchanged.
    if not is_baryon and heavy % 2 != 0:
        sign = -sign
    return heavy, sign


def assert_production_convention(ordinals: Path) -> int:
    """Pin `heavy_flavour_sign` to the production convention, not to itself.

    WHY THIS EXISTS. I2 below compares a parent's sign to its daughter's using
    this same helper. If the helper is inverted, both sides invert and I2 passes
    -- which is exactly what happened. A self-consistent check certifies
    self-consistency and nothing else.

    `species_ordinals_v2.json` carries `q_c`/`q_b` for all 202 species, computed
    by the production classifier (`tools/GenerateSpeciesOrdinals.C` over
    `Hadronization::DecodeHeavyContent`) at table-generation time. It is the
    production convention MATERIALISED, and it is an independent artifact from
    this file. Comparing against it is what makes the advertised absolute q_b
    convention checkable.
    """
    payload = json.loads(Path(ordinals).read_text())
    mismatches = []
    blind = []
    checked = 0
    for row in payload["species"]:
        pdg = int(row["pdg"])
        heavy, sign = heavy_flavour_sign(pdg)
        q_c, q_b = int(row["q_c"]), int(row["q_b"])
        if heavy == 0:
            # NOT a skip. If production signs this species and the helper calls
            # it flavourless, I2 will silently pass over it -- an unchecked row
            # looks exactly like a clean one. That is how +-14122 stayed
            # invisible.
            if q_c or q_b:
                blind.append((row["pdg"], q_c, q_b))
            continue
        # A species carrying beauty is signed by q_b; otherwise by q_c. The
        # magnitude may exceed 1 for doubly-heavy baryons, so compare the SIGN.
        want = q_b if heavy == 5 else q_c
        if want == 0:
            continue
        checked += 1
        want_sign = 1 if want > 0 else -1
        if sign != want_sign:
            mismatches.append((row["pdg"], row.get("name", "?"), heavy, sign,
                               want_sign))
    if blind:
        raise SystemExit(
            f"FAIL-CLOSED I2a: heavy_flavour_sign reports no heavy flavour for "
            f"{len(blind)} species that production signs: {blind[:6]}. I2 skips "
            f"rows the helper calls flavourless, so these would never be "
            f"checked at all."
        )
    if mismatches:
        shown = ", ".join(f"{p} (got {g}, production {w})"
                          for p, _n, _h, g, w in mismatches[:6])
        raise SystemExit(
            f"FAIL-CLOSED I2a: heavy_flavour_sign disagrees with the production "
            f"convention on {len(mismatches)} of {checked} species: {shown}. "
            f"The convention is fixed by generation/producer/HeavyFlavourUtils.h "
            f"and materialised in {ordinals}; this helper does not get to "
            f"differ from it."
        )
    return checked


def parse_probe(text: str) -> tuple[dict, list[dict]]:
    meta: dict = {}
    rows: list[dict] = []
    for line in text.splitlines():
        if line.startswith("F4_PYTHIA_VERSION"):
            meta["pythia_version"] = line.split()[1]
        elif line.startswith("F4_GATE "):
            kv = dict(t.split("=", 1) for t in line.split()[1:] if "=" in t)
            meta["gate"] = kv
        elif line.startswith("F4_SPECIES "):
            kv = dict(t.split("=", 1) for t in line.split()[1:] if "=" in t)
            rows.append(kv)
    return meta, rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("probe_out", type=Path)
    ap.add_argument("--ordinals", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    meta, rows = parse_probe(args.probe_out.read_text())

    gate = meta.get("gate", {})
    if gate.get("verdict") != "READABLE_AFTER_DISABLE":
        raise SystemExit(
            f"FAIL-CLOSED: probe gate verdict is {gate.get('verdict')!r}; the map "
            "may not be derived after the stabilisation pass. The proposal's "
            "other path (derive before stabilisation) applies instead."
        )
    if meta.get("pythia_version") != EXPECTED_PYTHIA:
        raise SystemExit(
            f"FAIL-CLOSED: probe ran against PYTHIA {meta.get('pythia_version')!r}, "
            f"expected {EXPECTED_PYTHIA}"
        )

    ordinals = json.loads(args.ordinals.read_text())
    want = {int(r["pdg"]): int(r["ordinal"]) for r in ordinals["species"]}
    got = {int(r["pdg"]) for r in rows}

    missing = sorted(set(want) - got)
    extra = sorted(got - set(want))
    if missing or extra:
        raise SystemExit(
            f"FAIL-CLOSED: species set differs from the ordinal table "
            f"(itself derived from heavy_stability_audit). "
            f"missing={missing[:8]} extra={extra[:8]}"
        )

    absent = [r["pdg"] for r in rows if r.get("status") == "ABSENT_FROM_PARTICLE_DATA"]
    if absent:
        raise SystemExit(
            f"FAIL-CLOSED: {len(absent)} species absent from PYTHIA's particle "
            f"data: {absent[:8]}"
        )

    species = []
    raw_products: dict[int, list[int]] = {}
    conjugated_rows = 0
    for r in sorted(rows, key=lambda x: want[int(x["pdg"])]):
        pdg = int(r["pdg"])
        products = r.get("dominant_products", "-")
        as_read = ([] if products in ("-", "")
                   else [int(x) for x in products.split(":")])
        raw_products[pdg] = as_read
        # Antiparticle parents only. PYTHIA handed us the PARTICLE's products.
        stored = conjugate_products(as_read) if pdg < 0 else list(as_read)
        if stored != as_read:
            conjugated_rows += 1
        species.append({
            "ordinal": want[pdg],
            "pdg": pdg,
            "name": r.get("name", ""),
            "channels": int(r.get("channels", 0)),
            "dominant_branching_ratio": float(r.get("dominant_br", 0.0)),
            "dominant_products": stored,
            "products_as_probed": as_read if pdg < 0 else None,
            "status": r.get("status", ""),
        })

    # ---- I1 INVOLUTION, permanent and fail-closed --------------------------
    # An antiparticle row's stored products must be exactly the conjugation of
    # its particle row's products. This is the check that would have caught the
    # v1 defect on the day it was built.
    by_pdg = {s["pdg"]: s for s in species}
    involution_pairs = 0
    for pdg, s in by_pdg.items():
        if pdg >= 0:
            continue
        mate = by_pdg.get(-pdg)
        if mate is None:
            raise SystemExit(f"FAIL-CLOSED I1: {pdg} has no particle row")
        expected = conjugate_products(raw_products[-pdg])
        if s["dominant_products"] != expected:
            raise SystemExit(
                f"FAIL-CLOSED I1 involution: {s['name']} ({pdg}) stores "
                f"{s['dominant_products']}, conjugation of its particle row "
                f"gives {expected}"
            )
        involution_pairs += 1

    # ---- I2a: the helper itself, against PRODUCTION -------------------------
    # Run I2a first because a shared sign inversion would make I2 pass incorrectly.
    # Production values provide the independent sign convention.
    convention_rows = assert_production_convention(args.ordinals)

    # ---- I2 HEAVY-QUARK SIGN on EVERY row ----------------------------------
    # A weak decay may change heavy flavour but cannot keep it and flip its sign.
    for s in species:
        ph, ps = heavy_flavour_sign(s["pdg"])
        if ph == 0:
            continue
        for p in s["dominant_products"]:
            if p not in want:
                continue
            dh, ds = heavy_flavour_sign(p)
            if dh == ph and ds != ps:
                raise SystemExit(
                    f"FAIL-CLOSED I2 heavy-quark sign: {s['name']} ({s['pdg']}, "
                    f"flavour={ph} sign={ps}) -> {p} (flavour={dh} sign={ds})"
                )

    payload = {
        "schema": SCHEMA,
        "derived_from": "PYTHIA particleData, pinned install, via tools/f4_probe",
        "pythia_version": meta["pythia_version"],
        "gate": {
            "question": "do decay channels remain readable after mayDecay(id,false)?",
            "verdict": gate.get("verdict"),
            "species_with_channels": int(gate.get("with_channels", 0)),
            "probed": int(gate.get("probed", 0)),
            "survived": int(gate.get("survived", 0)),
            "consequence": (
                "channels survive stabilisation, so the map derives AFTER the "
                "stabilisation pass -- the proposal's primary path"
            ),
        },
        "ordinal_table_digest_fnv1a64": ordinals["table_digest_fnv1a64"],
        "species_count": len(species),
        "unmapped_policy": "fail_closed_species_set_must_equal_ordinal_table",
        "conjugation": {
            "applied_to": "antiparticle parents (pdg < 0)",
            "rows_conjugated": conjugated_rows,
            "involution_pairs_checked": involution_pairs,
            "supersedes": "hf_decay_parent_map_v1, which stored PYTHIA's "
                          "unconjugated products for antiparticle parents",
            "reference": "docs/MAP_V1_CONJUGATION_BUG.md",
        },
        "species": species,
    }
    body = json.dumps(payload, indent=2, sort_keys=True)
    payload["map_sha256"] = hashlib.sha256(body.encode()).hexdigest()
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    with_products = sum(1 for s in species if s["dominant_products"])
    # Table-affecting rows: the in-table heavy daughter changed identity. This
    # is the count that moves weight between bins, and it is much smaller than
    # the number of rows whose stored products changed.
    def heavy_daughter(prods):
        for p in prods:
            if p in want:
                return p
        return None
    table_affecting = sum(
        1 for s in species if s["pdg"] < 0
        and heavy_daughter(raw_products[s["pdg"]]) != heavy_daughter(s["dominant_products"])
    )
    print(f"DECAY_PARENT_MAP species={len(species)} "
          f"with_dominant_channel={with_products} "
          f"pythia={payload['pythia_version']} "
          f"gate={payload['gate']['verdict']} "
          f"map_sha256={payload['map_sha256'][:16]}")
    print(f"CONJUGATION artifact_rows_changed={conjugated_rows} "
          f"table_affecting_rows={table_affecting} "
          f"involution_pairs={involution_pairs} I1=PASS I2=PASS "
          f"I2a=PASS({convention_rows} vs production)")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
