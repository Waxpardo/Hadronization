"""Bounded native THnSparse object-add merge behind the collection locator."""

import argparse
from array import array
from bisect import bisect_right
import hashlib
import math
from pathlib import Path
import shutil
import sys
import tempfile
import time

try:
    from . import collection as c
except ImportError:
    import importlib.util
    spec = importlib.util.spec_from_file_location("query_collection", Path(__file__).with_name("collection.py"))
    c = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(c)


def _digest(hist):
    digest = hashlib.sha256()
    for coordinates, value, variance in c._cells(hist):
        digest.update(c.r.canonical([coordinates, value.hex(), variance.hex()]).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def _family_entries(shard):
    """Count fills by natural tune from exact support with bounded range state."""
    tunes = {m["tune_ordinal"] for m in shard["members"]}
    if len(tunes) == 1:
        return None  # Each family histogram's own GetEntries is exact.
    ROOT = c._root()
    file = ROOT.TFile.Open(shard["query_root"]["path"], "READ")
    try:
        def integer(value):
            return ord(value) if isinstance(value, str) and len(value) == 1 else int(value)
        members = {local: member["tune_ordinal"] for local, member in enumerate(shard["members"])}
        ranges = [(int(row.first_id), int(row.count), int(row.source_id)) for row in file.Get("event_ranges")]
        starts = [row[0] for row in ranges]
        counts = {family: {tune: 0 for tune in tunes} for family in c.FAMILIES}
        def tune_for(event_id):
            position = bisect_right(starts, int(event_id)) - 1
            if position < 0 or int(event_id) >= ranges[position][0] + ranges[position][1]:
                raise ValueError("exact support event has no source range")
            return members[ranges[position][2]]
        for tree, family in (("events", "activity"), ("pairs", "pairs"),
                             ("closure", "closure"), ("triggers", "triggers"),
                             ("heavy", "kinematics")):
            rows = file.Get(tree)
            if not rows:
                raise ValueError("required exact support tree is missing")
            for row in rows:
                if tree == "triggers" and integer(row.rejection_mask) != 0:
                    continue
                if tree == "heavy" and not (integer(row.final) and integer(row.selected) and
                                            81 <= integer(row.status) <= 89):
                    continue
                counts[family][tune_for(row.event_id)] += 1
        return counts
    finally:
        file.Close()


def _select_tune(hist, ordinal, entries):
    for axis in range(hist.GetNdimensions()):
        hist.GetAxis(axis).SetRange(0, 0)
    # ProjectionND contracts the selected tune axis. Retain the original
    # campaign geometry so natural tune ordinals remain additive across files.
    selected = hist.Clone(hist.GetName()+"__selected")
    selected.Reset()
    selected.Sumw2()
    for coordinates, value, variance in c._cells(hist):
        if coordinates[0] != ordinal + 1:
            continue
        bins = array("i", coordinates)
        selected.SetBinContent(bins, value)
        selected.SetBinError2(selected.GetBin(bins), variance)
    selected.SetEntries(entries)
    for axis in range(hist.GetNdimensions()):
        hist.GetAxis(axis).SetRange(0, 0)
        selected.GetAxis(axis).SetRange(0, 0)
    if not selected.GetCalculateErrors() or not math.isfinite(selected.GetEntries()):
        raise ValueError("tune projection lost Sumw2")
    return selected


def merge(index_path, expected_sha256, output):
    index = c.read(index_path, expected_sha256)
    if index["layout"] != "SHARDED":
        raise ValueError("physical merge requires a sharded collection")
    output = Path(output).absolute()
    if output.exists():
        raise ValueError("merged collection destination already exists")
    output.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="."+output.name+".stage-", dir=str(output.parent)))
    ROOT = c._root()
    layout = c.r.json_file(c.ROOT_DIR / "config/query.json")
    started = time.monotonic()
    partitions = []
    entry_counts = {s["ordinal"]: _family_entries(s) for s in index["shards"]}
    try:
        for tune, ordinal in sorted(index["tune_ordinals"].items(), key=lambda x: x[1]):
            root_path = stage / ("tune-%02d.root" % ordinal)
            target = ROOT.TFile.Open(str(root_path), "CREATE")
            if not target or target.IsZombie():
                raise ValueError("cannot create merge ROOT")
            family_digests = {}
            try:
                for family in c.FAMILIES:
                    merged = None
                    baseline = None
                    for shard in index["shards"]:
                        if not any(m["tune"] == tune for m in shard["members"]):
                            continue
                        source = ROOT.TFile.Open(shard["query_root"]["path"], "READ")
                        if not source or source.IsZombie():
                            raise ValueError("cannot open merge source")
                        try:
                            hist = source.Get("sparse_"+family)
                            signature = c._geometry(hist, layout["sparse"][family])
                            if baseline is not None and baseline != signature:
                                raise ValueError("merge geometry/dictionary differs")
                            baseline = signature
                            by_tune = entry_counts[shard["ordinal"]]
                            entries = hist.GetEntries() if by_tune is None else by_tune[family][ordinal]
                            selected = _select_tune(hist, ordinal, entries)
                            if c._geometry(selected, layout["sparse"][family]) != signature:
                                raise ValueError("tune projection geometry differs")
                            for coord, _, _ in c._cells(selected):
                                if coord[0] != ordinal + 1:
                                    raise ValueError("tune projection retained foreign cell")
                            if merged is None:
                                merged = selected.Clone("sparse_"+family)
                            else:
                                for axis in range(merged.GetNdimensions()):
                                    merged.GetAxis(axis).SetRange(0, 0)
                                merged.Add(selected)
                            del selected
                        finally:
                            source.Close()
                    if merged is None:
                        raise ValueError("tune has no sparse contribution")
                    for axis in range(merged.GetNdimensions()):
                        merged.GetAxis(axis).SetRange(0, 0)
                    family_digests[family] = _digest(merged)
                    target.cd()
                    if merged.Write("sparse_"+family) <= 0:
                        raise ValueError("cannot write merged sparse object")
                    del merged
            finally:
                target.Close()
            reopened = ROOT.TFile.Open(str(root_path), "READ")
            if not reopened or reopened.IsZombie():
                raise ValueError("cannot reopen merged ROOT")
            try:
                if {key.GetName() for key in reopened.GetListOfKeys()} != {"sparse_"+f for f in c.FAMILIES}:
                    raise ValueError("merged ROOT object set differs")
                for family in c.FAMILIES:
                    hist = reopened.Get("sparse_"+family)
                    c._geometry(hist, layout["sparse"][family])
                    if _digest(hist) != family_digests[family]:
                        raise ValueError("merged ROOT readback content differs")
            finally:
                reopened.Close()
            partitions.append({"tune": tune, "families": list(c.FAMILIES),
                               "root": c._fact(root_path), "cell_digests": family_digests})
        merged_index = dict(index)
        merged_index["layout"] = "MERGED"
        merged_index["partitions"] = partitions
        merged_index["merge_elapsed_seconds"] = time.monotonic() - started
        # File locators change on publication; scientific identity does not.
        for part in partitions:
            part["root"]["path"] = str(output / Path(part["root"]["path"]).name)
        merged_index.pop("merge_elapsed_seconds")
        c.r.atomic_json(stage / "index.json", merged_index, exclusive=True)
        for path in stage.iterdir():
            c.r.fsync_file(path)
        c.r.fsync_directory(stage)
        c.q.publish_directory(stage, output)
        c.r.fsync_directory(output.parent)
        published = c.read(output / "index.json", c.r.sha_file(output / "index.json"))
        if published["scientific_identity_sha256"] != index["scientific_identity_sha256"]:
            raise ValueError("merged scientific identity changed")
        return output / "index.json"
    finally:
        if stage.exists():
            shutil.rmtree(stage)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("build")
    create.add_argument("--index", type=Path, required=True)
    create.add_argument("--expected-index-sha256", required=True)
    create.add_argument("--output", type=Path, required=True)
    verify = commands.add_parser("verify")
    verify.add_argument("--index", type=Path, required=True)
    verify.add_argument("--expected-index-sha256", required=True)
    args = parser.parse_args()
    try:
        if args.command == "build":
            path = merge(args.index, args.expected_index_sha256, args.output)
            print("MERGED_COLLECTION_INDEX="+str(path))
            print("MERGED_COLLECTION_SHA256="+c.r.sha_file(path))
        else:
            index = c.read(args.index, args.expected_index_sha256)
            if index["layout"] != "MERGED":
                raise ValueError("collection is not physically merged")
            print("MERGED_COLLECTION_VERIFIED="+index["scientific_identity_sha256"])
    except (OSError, ValueError, KeyError, TypeError) as error:
        print("ERROR: "+str(error), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
