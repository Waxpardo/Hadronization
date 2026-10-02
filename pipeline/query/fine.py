"""Audit and export signed fine heavy species through the collection reader.

The accepted analyzed rows copied into each query shard are the independent
row oracle.  This reader recomputes their weighted final-state census and
compares it with the all-heavy THnSparse, including flow bins.
"""

import argparse
from bisect import bisect_right
import json
import math
from pathlib import Path

from pipeline.query import collection
from pipeline.reduce import native


ROOT_DIR = Path(__file__).resolve().parents[2]


def _add(target, key, value, *, row=False):
    item = target.setdefault(key, [0, 0.0, 0.0])
    if row:
        item[0] += 1
    item[1] += value
    item[2] += value * value if row else 0.0


def _axis_integer(axis, coordinate):
    if not 1 <= coordinate <= axis.GetNbins():
        raise ValueError("fine stage/sign coordinate is outside the declared axis")
    value = axis.GetBinCenter(coordinate)
    if abs(value - round(value)) > 1e-10:
        raise ValueError("fine stage/sign axis is not integral")
    return round(value)


def _integer(value):
    # PyROOT exposes UChar_t branches as one-character strings on some builds.
    return ord(value) if isinstance(value, str) and len(value) == 1 else int(value)


def _exact_rows(index, catalog):
    """Count accepted exact support by tune, original block and signed state."""
    ROOT = collection._root()
    observed = {}
    final = {}
    expected_pairs = {}
    for shard in index["shards"]:
        file = ROOT.TFile.Open(shard["query_root"]["path"], "READ")
        if not file or file.IsZombie():
            raise ValueError("fine exact-support shard cannot open")
        try:
            events, heavy, triggers, ranges = (file.Get(name) for name in
                                               ("events", "heavy", "triggers", "event_ranges"))
            if not events or not heavy or not triggers or not ranges:
                raise ValueError("fine exact-support tree is missing")
            # Exact TTree source_id is shard-local; the receipt supplies its
            # ordered mapping to campaign-global source identities.
            members = dict(enumerate(shard["members"]))
            intervals = []
            for row in ranges:
                first, count, source_id = (int(row.first_id), int(row.count),
                                           int(row.source_id))
                if count <= 0 or source_id not in members:
                    raise ValueError("fine exact source interval differs")
                intervals.append((first, first + count, members[source_id]))
            intervals.sort(key=lambda item: item[0])
            starts = [item[0] for item in intervals]
            if any(left[1] > right[0] for left, right in zip(intervals, intervals[1:])):
                raise ValueError("fine exact source intervals overlap")
            cursor = 0
            have = heavy.GetEntries() > 0
            if have:
                heavy.GetEntry(cursor)
            trigger_cursor = 0
            have_trigger = triggers.GetEntries() > 0
            if have_trigger:
                triggers.GetEntry(trigger_cursor)
            for event in events:
                event_id = int(event.event_id)
                position = bisect_right(starts, event_id) - 1
                if position < 0 or event_id >= intervals[position][1]:
                    raise ValueError("fine exact event lacks a source interval")
                member = intervals[position][2]
                tune, block = member["tune"], member["block"]
                weight = float(event.weight)
                if not math.isfinite(weight):
                    raise ValueError("fine exact event has nonfinite weight")
                particles = {}
                while have and int(heavy.event_id) == event_id:
                    pdg = int(heavy.pdg)
                    state = catalog.get(pdg)
                    if state is None:
                        raise ValueError("observed heavy PDG is absent from catalog")
                    if tuple(int(getattr(heavy, key)) for key in
                             ("nc", "ncbar", "nb", "nbbar")) != tuple(
                                 state[key] for key in ("nc", "ncbar", "nb", "nbbar")):
                        raise ValueError("fine exact constituent content differs")
                    stage = (tune, block, pdg, int(heavy.status),
                             _integer(heavy.selected), _integer(heavy.pair_eligible))
                    identity = int(heavy.heavy_index)
                    if identity in particles:
                        raise ValueError("fine exact event has duplicate heavy identity")
                    particles[identity] = (pdg, int(heavy.status), _integer(heavy.final),
                                           float(heavy.eta))
                    _add(observed, stage, 0.0, row=True)
                    if _integer(heavy.final):
                        _add(final, stage, weight, row=True)
                    cursor += 1
                    have = cursor < heavy.GetEntries()
                    if have:
                        heavy.GetEntry(cursor)
                if have and int(heavy.event_id) < event_id:
                    raise ValueError("fine exact heavy rows are out of event order")
                while have_trigger and int(triggers.event_id) == event_id:
                    if not int(triggers.rejection_mask):
                        identity = int(triggers.heavy_index)
                        sector = "nc" if int(triggers.sector) == 4 else "nb"
                        if int(triggers.sector) not in (4, 5) or identity not in particles:
                            raise ValueError("fine exact trigger sector or identity differs")
                        pdg, status, is_final, eta = particles[identity]
                        if not is_final or not 81 <= status <= 89:
                            raise ValueError("fine exact accepted trigger stage differs")
                        if abs(eta) > 4.0:
                            trigger_cursor += 1
                            have_trigger = trigger_cursor < triggers.GetEntries()
                            if have_trigger:
                                triggers.GetEntry(trigger_cursor)
                            continue
                        trigger_charge = catalog[pdg][sector] - catalog[pdg][sector + "bar"]
                        if abs(trigger_charge) != 1:
                            raise ValueError("fine exact accepted trigger flavour differs")
                        for associate_id, (associate_pdg, associate_status,
                                           associate_final, associate_eta) in particles.items():
                            if (associate_id == identity or not associate_final or
                                    abs(associate_eta) > 4.0):
                                continue
                            associate_charge = (catalog[associate_pdg][sector] -
                                                catalog[associate_pdg][sector + "bar"])
                            product = trigger_charge * associate_charge
                            sign = 0 if product == 0 else (-1 if product < 0 else 1)
                            key = (tune, block, pdg, associate_pdg, associate_status, sign)
                            _add(expected_pairs, key, weight, row=True)
                    trigger_cursor += 1
                    have_trigger = trigger_cursor < triggers.GetEntries()
                    if have_trigger:
                        triggers.GetEntry(trigger_cursor)
                if have_trigger and int(triggers.event_id) < event_id:
                    raise ValueError("fine exact trigger rows are out of event order")
            if have:
                raise ValueError("fine exact heavy rows remain after final event")
            if have_trigger:
                raise ValueError("fine exact trigger rows remain after final event")
        finally:
            file.Close()
    return observed, final, expected_pairs


def _fine_cells(source, catalog, requested_pdg=None):
    totals = {}
    exported = []
    pairs = {}
    def consume(cell, axes):
        names = {axis.GetName(): i for i, axis in enumerate(axes)}
        coordinates = cell.coordinates
        if cell.family == "kinematics":
            pdg = int(axes[names["pdg"]].GetBinLabel(coordinates[names["pdg"]]))
            if pdg not in catalog:
                raise ValueError("fine sparse contains a foreign PDG")
            stage = tuple(_axis_integer(axes[names[field]], coordinates[names[field]])
                          for field in ("status", "selected", "pair_eligible"))
            key = (cell.tune, cell.block, pdg) + stage
            item = totals.setdefault(key, [0, 0.0, 0.0])
            item[0] += 1
            item[1] += cell.value
            item[2] += cell.sumw2
            if pdg == requested_pdg:
                exported.append({"tune": cell.tune, "block": cell.block,
                                 "axis_bins": {axis.GetName(): int(coordinate)
                                               for axis, coordinate in zip(axes, coordinates)},
                                 "sumw": cell.value.hex(), "sumw2": cell.sumw2.hex()})
        elif cell.family == "pairs":
            trigger = int(axes[names["trigger_pdg"]].GetBinLabel(
                coordinates[names["trigger_pdg"]]))
            associate = int(axes[names["associate_pdg"]].GetBinLabel(
                coordinates[names["associate_pdg"]]))
            sector = "nc" if abs(trigger) in (421, 411, 4122) else "nb"
            trigger_charge = (catalog[trigger][sector] - catalog[trigger][sector + "bar"])
            associate_charge = (catalog[associate][sector] - catalog[associate][sector + "bar"])
            product = trigger_charge * associate_charge
            expected = 0 if product == 0 else (-1 if product < 0 else 1)
            sign = _axis_integer(axes[names["sign"]], coordinates[names["sign"]])
            origin = _axis_integer(axes[names["origin"]], coordinates[names["origin"]])
            if sign != expected or (sign == 0 and origin != -1):
                raise ValueError("fine pair flavour sign or inapplicable origin differs")
            status = _axis_integer(axes[names["associate_status"]],
                                   coordinates[names["associate_status"]])
            key = (cell.tune, cell.block, trigger, associate, status, sign)
            item = pairs.setdefault(key, [0, 0.0, 0.0])
            item[0] += 1
            item[1] += cell.value
            item[2] += cell.sumw2
    source.scan(("kinematics", "pairs"), source.index["tune_ordinals"], consume)
    return totals, pairs, exported


def build_inventory(index_path, index_sha256, *, requested_pdg=None):
    model = collection.q.model
    analysis, analysis_sha = model.checked_analysis(ROOT_DIR / "config/analysis-all-heavy.json")
    binding = analysis["retained_heavy_catalog"]
    catalog_data = model.checked_heavy_catalog(ROOT_DIR / binding["path"], binding["sha256"])
    catalog = {item["pdg"]: item for item in catalog_data["states"]}
    family_binding = analysis["associate_family_map"]
    family_map = json.loads((ROOT_DIR / family_binding["path"]).read_text())
    paper_members = {pdg for group in family_map["groups"] for pdg in group["members"]}
    if requested_pdg is not None and requested_pdg not in catalog:
        raise ValueError("requested fine signed species is not in the catalog")
    source = native.NativeCollection(index_path, index_sha256, collection)
    if source.index["analysis_sha256"] != analysis_sha:
        raise ValueError("fine collection is not the all-heavy analysis")
    observed, final, expected_pairs = _exact_rows(source.index, catalog)
    fine, pairs, exported = _fine_cells(source, catalog, requested_pdg)
    if set(final) != set(fine):
        missing = sorted(set(final) - set(fine))[:8]
        extra = sorted(set(fine) - set(final))[:8]
        raise ValueError("fine final-stage key coverage differs: missing={} extra={}".format(
            missing, extra))
    for key, expected in final.items():
        actual = fine[key]
        if any(not math.isclose(expected[i], actual[i], rel_tol=2e-10, abs_tol=1e-12)
               for i in (1, 2)):
            raise ValueError("fine weighted row/sparse closure differs for {}".format(key))
    if set(expected_pairs) != set(pairs):
        raise ValueError("fine pair category coverage differs: missing={} extra={}".format(
            sorted(set(expected_pairs) - set(pairs))[:8],
            sorted(set(pairs) - set(expected_pairs))[:8]))
    for key, expected in expected_pairs.items():
        actual = pairs[key]
        if any(not math.isclose(expected[i], actual[i], rel_tol=2e-10, abs_tol=1e-12)
               for i in (1, 2)):
            raise ValueError("fine weighted pair/sparse closure differs for {}".format(key))
    states = []
    for pdg, state in catalog.items():
        any_rows = sum(value[0] for key, value in observed.items() if key[2] == pdg)
        final_rows = sum(value[0] for key, value in final.items() if key[2] == pdg)
        direct = sum(value[0] for key, value in final.items()
                     if key[2] == pdg and 81 <= key[3] <= 89 and key[4] == 1)
        pair_rows = sum(value[0] for key, value in expected_pairs.items()
                        if key[3] == pdg)
        paper_pair_rows = sum(value[0] for key, value in expected_pairs.items()
                              if key[3] == pdg and pdg in paper_members and
                              81 <= key[4] <= 89 and key[5] != 0)
        cells = sum(value[0] for key, value in fine.items() if key[2] == pdg)
        states.append({"pdg": pdg, "name": state["name"],
                       "observed_rows": any_rows, "final_rows": final_rows,
                       "nonfinal_rows": any_rows - final_rows,
                       "selected_direct_final_rows": direct,
                       "retained_pair_rows": pair_rows,
                       "paper_grouped_pair_rows": paper_pair_rows,
                       "paper_group_member": pdg in paper_members,
                       "fine_occupied_cells": cells,
                       "coverage": ("unobserved" if not any_rows else
                                    "history_only" if not final_rows else
                                    "retained_final")})
    return {"schema": "hadronization_all_heavy_fine_inventory_v1",
            "collection_index_sha256": index_sha256,
            "analysis_sha256": analysis_sha,
            "catalog_sha256": binding["sha256"],
            "state_count": len(states), "observed_identity_count": sum(
                state["observed_rows"] > 0 for state in states),
            "final_identity_count": sum(state["final_rows"] > 0 for state in states),
            "retained_final_rows": sum(value[0] for value in final.values()),
            "retained_pair_rows": sum(value[0] for value in expected_pairs.values()),
            "pair_category_count": len(pairs),
            "pair_by_tune_block_trigger_associate_status_sign": [
                {"tune": key[0], "block": key[1], "trigger_pdg": key[2],
                 "associate_pdg": key[3], "associate_status": key[4], "sign": key[5],
                 "exact_pair_rows": expected_pairs[key][0], "sumw": pairs[key][1].hex(),
                 "sumw2": pairs[key][2].hex(), "occupied_cells": pairs[key][0]}
                for key in sorted(expected_pairs)],
            "states": states,
            "fine_by_tune_block_pdg_stage": [
                {"tune": key[0], "block": key[1], "pdg": key[2],
                 "status": key[3], "selected": key[4], "pair_eligible": key[5],
                 "final_rows": final[key][0], "sumw": fine[key][1].hex(),
                 "sumw2": fine[key][2].hex(), "occupied_cells": fine[key][0]}
                for key in sorted(final)],
            "exported_pdg": requested_pdg, "exported_cells": exported}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--index-sha256", required=True)
    parser.add_argument("--pdg", type=int,
                        help="include every occupied fine cell of this signed species")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = build_inventory(args.index, args.index_sha256,
                              requested_pdg=args.pdg)
    collection.r.atomic_json(args.output, payload, exclusive=True)
    print("FINE_INVENTORY=" + str(args.output))


if __name__ == "__main__":
    main()
