#!/usr/bin/env python3
"""Assert the V-INTEGRATED closure: summed per-class counts == integrated counts.

Reads the `PAIR_COUNTS` lines the plotting macro emits for every (tune, species,
bin) and checks, per species per tune:

    sum over the eleven classes of N_OS   ==   N_OS of the M00_100 bin
    sum over the eleven classes of N_SS   ==   N_SS of the M00_100 bin
    sum over the eleven classes of N_trig ==   N_trig of the M00_100 bin

The two sides come from DIFFERENT routes -- eleven restricted THnSparse
projections summed, against one unrestricted projection -- so agreement is a
real check that the classes tile the multiplicity axis, not an identity.

INTEGER-EXACT, no tolerance. The counts are unweighted for this campaign
(measured over 1.2M events), so
the contents are exact integers in doubles and exact equality is the right
comparison. A mismatch means the classes do not tile the sample -- a dropped
class, a bins_to_ignore entry, an off-by-one on a boundary bin -- and the fix is
the axis, never an epsilon.

WHAT THE TOOL REFUSES, AND WHY EACH REFUSAL EXISTS.

A closure assertion that reports success on a log it never checked is worse than
no assertion, because it is quoted as evidence. Every refusal below closes a
measured defect, not a speculative one:

  MISSING KEYS / EXTRA KEYS   The expected identity set is DERIVED from the
      closure configuration -- PYTHIA_TUNES times the configured `associateOS`
      entries -- and every configured OS filename must resolve to exactly one
      row of the pair registry. A render that dropped a pair reduced the checked
      set silently, and `keys=N` alone never said which N.
  MISSING BINS / EXTRA BINS   Per identity the bin set must be exactly the
      contract's class bins plus the integrated bin. An eleven-class log crashed
      on a leaked loop variable (ledger D3); a log short one class now says so
      by name.
  DUPLICATE (key,bin)         Repeated identities overwrote last-wins, so a
      corrupt repeat could hide a correct row or the reverse (ledger DA1-017).
  NOTHING CHECKED             `checked == 0` printed EXACT keys=0 and exited 0
      (ledger D4).
  NO INTEGRATED BIN ANYWHERE  Rows present but no identity carrying M00_100 left
      the class map unbound and raised at the summary line (ledger D3, and the
      final review's NameError path).
  NON-INTEGRAL COUNT          The unit-weight precondition is tested on EVERY
      per-class count, not only on the sums: +0.5 and -0.5 in two classes of one
      identity cancel into an integral sum and passed unreported
      (ledger DA1-016).

The docstring's justification for comparing with no tolerance is the unit-weight
precondition, so the precondition is tested where it is assumed.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLOSURE_CONFIG = (ROOT / "plotting" /
                  "configuration_multiplicity_HF_RUN3_V1_VINTEGRATED_CLOSURE.json")
PAIR_REGISTRY = ROOT / "config" / "heavy_flavour_pair_registry_v1.json"
CLASS_CONTRACT = ROOT / "config" / "multiplicity_percentile_classes_v2.json"

INTEGRATED_BIN = "M00_100"
LINE = re.compile(r"^PAIR_COUNTS\s+(.*)$")
COUNT_FIELDS = ("n_os", "n_ss", "n_trig")

# The configuration key that carries each flavour's trigger groups, and the
# FLAVOUR string the macro prints beside it. `calculateYieldsVector` is called
# once per flavour with these literals (improvedPlotting_THnSparse.C:6499-6500)
# and selects the matching configuration block
# (`improvedPlotting_THnSparse.C:4141-4142`, parsed from these very keys at
# `:3267` and `:3318`), so the pairing is the macro's own and not a
# convention invented here.
FLAVOUR_KEYS = {
    "BEAUTY": "beauty_correlations_to_analyse",
    "CHARM": "charm_correlations_to_analyse",
}


class ClosureRefusal(Exception):
    """A named refusal. Every non-zero exit of this tool raises one."""


def class_bins(contract: Path = CLASS_CONTRACT) -> list[str]:
    """The class bin labels, in contract order.

    Ruling R10 makes config/multiplicity_percentile_classes_v2.json the one
    place the class set is written down, so the expected bin set is read from
    there and never enumerated in this file.
    """
    return [row["bin"] for row in json.loads(contract.read_text())["classes"]]


def expected_bins(contract: Path = CLASS_CONTRACT) -> set[str]:
    return set(class_bins(contract)) | {INTEGRATED_BIN}


def expected_keys(config: Path = CLOSURE_CONFIG,
                  registry: Path = PAIR_REGISTRY) -> set[tuple]:
    """The identity set the log must carry, derived from the configuration.

    PYTHIA_TUNES times every configured (trigger, associateOS, OS) of both
    flavour blocks. Each configured OS filename must resolve to exactly one
    pair-registry row; a filename the registry does not carry, or carries twice,
    is refused here rather than leaving a pair silently out of the checked set.
    """
    document = json.loads(config.read_text())
    tunes = list(document["PYTHIA_TUNES"])
    if not tunes:
        raise ClosureRefusal(
            f"closure configuration {config.name} declares no PYTHIA_TUNES")

    rows_per_filename: dict[str, int] = {}
    for row in json.loads(registry.read_text())["pairs"]:
        name = row["filename"]
        rows_per_filename[name] = rows_per_filename.get(name, 0) + 1

    keys: set[tuple] = set()
    for flavour, section in FLAVOUR_KEYS.items():
        for group in document.get(section, []):
            for configured in group.get("configs", []):
                os_file = configured["OS"]
                found = rows_per_filename.get(os_file, 0)
                if found != 1:
                    raise ClosureRefusal(
                        f"configured OS file {os_file!r} of {section} resolves "
                        f"to {found} pair-registry rows; exactly one is required")
                for tune in tunes:
                    keys.add((tune, flavour, configured["trigger"],
                              configured["associateOS"], os_file))
    if not keys:
        raise ClosureRefusal(
            f"closure configuration {config.name} registers no trigger/associate "
            f"pair; there is nothing to close")
    return keys


def parse(path: Path) -> list[dict]:
    rows = []
    for raw in path.read_text(errors="replace").splitlines():
        match = LINE.match(raw.strip())
        if not match:
            continue
        fields = {}
        for token in match.group(1).split():
            if "=" in token:
                key, value = token.split("=", 1)
                fields[key] = value
        rows.append(fields)
    return rows


def index_rows(rows: list[dict]) -> dict[tuple, dict[str, dict]]:
    """(tune, flavour, trigger, associate, os_file) -> bin -> row.

    The macro prints the configured OS filename, so the basename is taken and a
    path-carrying log reads under the same identity set.
    """
    by_key: dict[tuple, dict[str, dict]] = defaultdict(dict)
    duplicates: list[str] = []
    for row in rows:
        key = (row.get("tune"), row.get("flavour"), row.get("trigger"),
               row.get("associate"), Path(row.get("os_file", "")).name)
        label = row.get("bin")
        if label in by_key[key]:
            duplicates.append(f"{key} bin={label}")
        by_key[key][label] = row
    if duplicates:
        raise ClosureRefusal(
            "duplicate (key,bin) rows; a repeated identity overwrites its "
            "predecessor last-wins:\n   " + "\n   ".join(duplicates[:10]))
    return dict(by_key)


def check_key_set(present: set[tuple], wanted: set[tuple]) -> None:
    missing = sorted(wanted - present)
    extra = sorted(present - wanted)
    if missing:
        raise ClosureRefusal(
            f"the log is missing {len(missing)} configured identities, first:\n"
            "   " + "\n   ".join(str(key) for key in missing[:10]))
    if extra:
        raise ClosureRefusal(
            f"the log carries {len(extra)} identities the configuration does not "
            f"register, first:\n   "
            + "\n   ".join(str(key) for key in extra[:10]))


def check_bins(key: tuple, present: set[str], wanted: set[str]) -> None:
    missing = sorted(wanted - present)
    extra = sorted(present - wanted)
    if missing:
        raise ClosureRefusal(f"{key} is missing bins: {', '.join(missing)}")
    if extra:
        raise ClosureRefusal(
            f"{key} carries unregistered bins: {', '.join(extra)}")


def run(log: Path, config: Path = CLOSURE_CONFIG,
        registry: Path = PAIR_REGISTRY,
        contract: Path = CLASS_CONTRACT,
        stream=None) -> int:
    """Assert the closure, or raise ClosureRefusal. Returns the keys checked.

    `stream` resolves at call time, not at import: a default of `sys.stdout`
    binds the interpreter's original stream and ignores a later redirect.
    """
    stream = sys.stdout if stream is None else stream
    rows = parse(log)
    if not rows:
        raise ClosureRefusal(f"no PAIR_COUNTS lines found in {log}")

    wanted_keys = expected_keys(config, registry)
    wanted_bins = expected_bins(contract)
    by_key = index_rows(rows)
    check_key_set(set(by_key), wanted_keys)

    if not any(INTEGRATED_BIN in bins for bins in by_key.values()):
        raise ClosureRefusal(
            f"no identity carries the integrated bin {INTEGRATED_BIN}; there is "
            f"no integrated side to close against")

    print(f"{'tune':<13}{'trigger':<18}{'associate':<24}"
          f"{'sum(class) OS-SS':>20}{'integrated OS-SS':>20}{'exact':>7}",
          file=stream)

    failures: list[str] = []
    non_integral: list[tuple] = []
    checked = 0
    class_counts: set[int] = set()

    for key in sorted(wanted_keys):
        bins = by_key[key]
        check_bins(key, set(bins), wanted_bins)
        classes = {label: row for label, row in bins.items()
                   if label != INTEGRATED_BIN}
        class_counts.add(len(classes))

        # Every individual count, not only the sums: two classes carrying +0.5
        # and -0.5 add to an integer and hid the violated precondition.
        for label, row in bins.items():
            for field in COUNT_FIELDS:
                value = float(row[field])
                if value != int(value):
                    non_integral.append((key, label, field, value))

        sums = {field: sum(float(row[field]) for row in classes.values())
                for field in COUNT_FIELDS}
        integrated = {field: float(bins[INTEGRATED_BIN][field])
                      for field in COUNT_FIELDS}

        exact = all(sums[field] == integrated[field] for field in COUNT_FIELDS)
        checked += 1
        tune, _flavour, trigger, associate, _os_file = key
        print(f"{tune:<13}{trigger:<18}{associate:<24}"
              f"{sums['n_os'] - sums['n_ss']:>20.0f}"
              f"{integrated['n_os'] - integrated['n_ss']:>20.0f}"
              f"{'YES' if exact else 'NO':>7}", file=stream)
        if not exact:
            for field in COUNT_FIELDS:
                if sums[field] != integrated[field]:
                    failures.append(
                        f"{tune} {trigger}->{associate} {field}: "
                        f"sum(classes)={sums[field]:.17g} "
                        f"integrated={integrated[field]:.17g} "
                        f"delta={sums[field]-integrated[field]:.17g}")

    print(file=stream)
    print(f"classes per key: {sorted(class_counts)}   keys checked: {checked}",
          file=stream)

    if checked == 0:
        raise ClosureRefusal(
            "no identity was checked; a closure that verified nothing must not "
            "report EXACT")
    if non_integral:
        raise ClosureRefusal(
            "NON-INTEGRAL COUNTS (unit-weight precondition violated):\n   "
            + "\n   ".join(f"{key} {label} {field} = {value!r}"
                           for key, label, field, value in non_integral[:10]))
    if failures:
        raise ClosureRefusal("CLOSURE FAILED:\n   " + "\n   ".join(failures))

    print(f"V_INTEGRATED_CLOSURE=EXACT keys={checked} "
          f"(integer-exact, no tolerance applied)", file=stream)
    return checked


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Assert the V-INTEGRATED closure over a render log.")
    parser.add_argument("log", type=Path,
                        help="render log carrying PAIR_COUNTS lines")
    parser.add_argument("--config", type=Path, default=CLOSURE_CONFIG,
                        help="closure configuration the identity set is derived "
                             "from (default: the tracked V-INTEGRATED closure "
                             "configuration)")
    parser.add_argument("--registry", type=Path, default=PAIR_REGISTRY,
                        help="pair registry each configured OS file resolves "
                             "against")
    parser.add_argument("--class-contract", type=Path, default=CLASS_CONTRACT,
                        help="multiplicity class contract the bin set comes from")
    args = parser.parse_args(argv)

    try:
        run(args.log, args.config, args.registry, args.class_contract)
    except ClosureRefusal as refusal:
        print(f"V_INTEGRATED_CLOSURE=REFUSED {refusal}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
