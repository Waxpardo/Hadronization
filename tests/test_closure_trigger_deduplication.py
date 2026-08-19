#!/usr/bin/env python3
"""Regression test for the E5 defect: trigger-owned closure counted once per PAIR.

THE DEFECT. `hFlavourClosure` and `hFlavourClosureSpecies` are owned by the
TRIGGER. The analysis builds one accumulator per distinct trigger PDG and writes
that same object into every pair file sharing that trigger. The extractor summed
every file, so every charm trigger was counted 24 times and every beauty trigger
26 times -- a registry-weighted replication, not a physical total.

WHY THE OLD SELF-CHECKS COULD NOT SEE IT. The species and category views are
duplicated identically, so `from_species == from_closure` holds exactly under
replication; and central == sum(blocks) holds too, because both sides carry the
same duplicated data. A replication-blind invariant cannot detect replication.

Five checks, each able to fail independently:
  1. registry shape       -- the 24x/26x replication is measured, not assumed;
  2. the arithmetic       -- deduplication recovers one copy per trigger;
  3. a negative control   -- unreplicated input is left unchanged;
  4. fail-closed          -- non-identical copies of one trigger are rejected;
  5. the known case       -- the committed MONASH extraction still carries the
                             sector-divisibility fingerprint of replication.

Check 2 is the one that fails against the pre-fix extractor: the old code summed
every file and would return 24x/26x these totals. Check 5 is what proves the
defect was real in the published product rather than merely possible in the code.
"""
import collections
import csv
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "extraction"))
from extract_species_decomposition import (  # noqa: E402
    deduplicate_by_trigger,
    load_registry,
)

REGISTRY = REPO / "config/heavy_flavour_pair_registry_v1.json"
ORDINALS = REPO / "AnalysisScripts/species_ordinals_v2.json"
PUBLISHED = REPO / "AnalysisScripts/anchors/merged_monash_central/per_species.csv"

# Measured from the committed 300-pair registry on 2026-08-13. Pinned so that a
# registry change that alters the replication factors fails loudly here rather
# than silently re-scaling a published table.
EXPECTED_REPLICATION = {"charm": 24, "beauty": 26}
EXPECTED_TRIGGERS_PER_SECTOR = 6

failures = []


def check(label, condition, detail=""):
    if condition:
        print(f"  PASS {label}")
    else:
        print(f"  FAIL {label} {detail}")
        failures.append(label)


# --- 1. registry shape: measure the replication rather than assuming it -------
payload = json.loads(REGISTRY.read_text())
per_trigger = collections.Counter(
    (p["sector"], p["trigger_pdg"]) for p in payload["pairs"])
by_sector = collections.defaultdict(set)
for (sector, _pdg), n in per_trigger.items():
    by_sector[sector].add(n)
triggers_per_sector = collections.Counter(sector for sector, _ in per_trigger)

check("registry: each charm trigger appears in exactly 24 pair files",
      by_sector["charm"] == {EXPECTED_REPLICATION["charm"]}, by_sector["charm"])
check("registry: each beauty trigger appears in exactly 26 pair files",
      by_sector["beauty"] == {EXPECTED_REPLICATION["beauty"]}, by_sector["beauty"])
check("registry: six triggers per sector",
      all(n == EXPECTED_TRIGGERS_PER_SECTOR for n in triggers_per_sector.values()),
      dict(triggers_per_sector))

trigger_of, sector_of = load_registry(REGISTRY)
check("registry loader: 300 filenames map to a trigger", len(trigger_of) == 300,
      len(trigger_of))

# --- 2. the arithmetic: deduplication recovers one copy per trigger ----------
# Give every file the closure of its own trigger, as the analysis does. Each
# trigger gets a distinct signature value so replication is visible in the sum.
signature = {pdg: float(index + 1)
             for index, pdg in enumerate(sorted(set(trigger_of.values())))}
replicated = {name: {7: signature[pdg]} for name, pdg in trigger_of.items()}

total, copies = deduplicate_by_trigger(
    replicated, set(replicated), trigger_of, "species")
want = sum(signature.values())
check("dedup: bin 7 equals the sum over TRIGGERS, not over files",
      total[7] == want, f"got {total[7]} want {want}")

naive = sum(bins[7] for bins in replicated.values())
check("dedup: the naive per-file sum really is inflated (the defect)",
      naive != want and naive == sum(
          signature[pdg] * per_trigger[(sector_of[pdg], pdg)]
          for pdg in signature),
      f"naive={naive} dedup={want}")
check("dedup: replication counts reported per trigger",
      set(copies.values()) == {24, 26}, sorted(set(copies.values())))

# --- 3. negative control: unreplicated input must be left unchanged ----------
one_per_trigger = {}
seen = set()
for name, pdg in sorted(trigger_of.items()):
    if pdg in seen:
        continue
    seen.add(pdg)
    one_per_trigger[name] = {7: signature[pdg]}
solo, _ = deduplicate_by_trigger(
    one_per_trigger, set(one_per_trigger), trigger_of, "species")
check("negative control: already-unique input is unchanged by deduplication",
      solo[7] == want, f"got {solo[7]} want {want}")

# --- 4. fail-closed: copies of one trigger that disagree are rejected --------
corrupted = dict(replicated)
victim = sorted(name for name, pdg in trigger_of.items()
                if pdg == sorted(signature)[0])[1]
corrupted[victim] = {7: signature[trigger_of[victim]] + 1.0}
try:
    deduplicate_by_trigger(corrupted, set(corrupted), trigger_of, "species")
    check("fail-closed: disagreeing copies rejected", False, "no SystemExit raised")
except SystemExit as exc:
    check("fail-closed: disagreeing copies rejected",
          "non-identical" in str(exc) and victim in str(exc), str(exc)[:120])

# --- 5. the known case: the published table still shows the fingerprint ------
# A charm trigger's closure only ever fills charm-carrying species (the analysis
# skips associates whose charge in the trigger's sector is zero), and likewise
# for beauty. So under replication every charm-only species total is divisible
# by 24 and every beauty-only one by 26. Under a correct extraction it would
# not be. This is the evidence that the published product is replicated.
if PUBLISHED.exists() and ORDINALS.exists():
    info = {r["ordinal"]: r for r in json.loads(ORDINALS.read_text())["species"]}
    charm_only, beauty_only = [], []
    for row in csv.DictReader(PUBLISHED.open()):
        ordinal, value = int(row["ordinal"]), int(float(row["total"]))
        rec = info[ordinal]
        if rec["q_c"] and not rec["q_b"]:
            charm_only.append(value)
        elif rec["q_b"] and not rec["q_c"]:
            beauty_only.append(value)
    check("known case: every charm-only species total is divisible by 24",
          bool(charm_only) and all(v % 24 == 0 for v in charm_only),
          f"{sum(v % 24 != 0 for v in charm_only)} of {len(charm_only)} violate")
    check("known case: every beauty-only species total is divisible by 26",
          bool(beauty_only) and all(v % 26 == 0 for v in beauty_only),
          f"{sum(v % 26 != 0 for v in beauty_only)} of {len(beauty_only)} violate")
    # Control: the divisibility is sector-specific, not universal. If most
    # charm-only totals were ALSO divisible by 26 the test above would be
    # vacuous.
    check("known case control: charm-only totals are NOT generally divisible by 26",
          sum(v % 26 != 0 for v in charm_only) > len(charm_only) // 2,
          f"{sum(v % 26 != 0 for v in charm_only)} of {len(charm_only)}")
else:
    check("known case: published extraction present", False, "fixture missing")

print(f"\n{len(failures)} failure(s)")
sys.exit(1 if failures else 0)
