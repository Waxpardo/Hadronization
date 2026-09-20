"""Merge original blocks into bounded THnSparse objects in one ROOT file per tune."""

import argparse
from array import array
import hashlib
from pathlib import Path
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
    return c.cell_digest(c._cells(hist))


def _native():
    ROOT = c._root()
    if not hasattr(ROOT, "PhaseAMerge"):
        if not ROOT.gInterpreter.Declare(Path(__file__).with_name("merge_sparse.hpp").read_text()):
            raise ValueError("cannot compile native block merge helper")
    return ROOT.PhaseAMerge


def _empty_like(hist, name):
    ROOT = c._root()
    axes = [hist.GetAxis(i) for i in range(hist.GetNdimensions())]
    result = ROOT.THnSparseD(name, name, len(axes),
        array("i", [a.GetNbins() for a in axes]),
        array("d", [a.GetXmin() for a in axes]),
        array("d", [a.GetXmax() for a in axes]), 16384)
    ROOT.SetOwnership(result, True)
    for i, axis in enumerate(axes):
        axis.Copy(result.GetAxis(i))
        result.GetAxis(i).SetRange(0, 0)
    result.Sumw2()
    return result


def _write_component(target, hist):
    # Fixed buffer preflight throws before ROOT can overflow; no giant clone.
    try:
        _native().SerializedSize(hist, c.MAX_SPARSE_OBJECT_BYTES - 65536)
    except Exception as error:
        raise ValueError("sparse component serialization bound: " + str(error)) from error
    target.cd()
    if hist.Write(hist.GetName()) <= 0:
        raise ValueError("cannot write merged sparse object")
    size = target.GetKey(hist.GetName()).GetObjlen()
    if size > c.MAX_SPARSE_OBJECT_BYTES:
        raise ValueError("merged sparse serialization exceeded bound")
    return size


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
    native = _native()
    publication_started = False
    try:
        for tune, ordinal in sorted(index["tune_ordinals"].items(), key=lambda x: x[1]):
            root_path = stage / ("tune-%02d.root" % ordinal)
            target = ROOT.TFile.Open(str(root_path), "CREATE")
            if not target or target.IsZombie():
                raise ValueError("cannot create merge ROOT")
            family_digests = {}
            objects = {}
            try:
                for family in c.FAMILIES:
                    objects[family] = []
                    family_digest = hashlib.sha256()
                    merged = None
                    baseline = None
                    entries = [0] * index["block_count"]
                    print("MERGE_FAMILY tune=%s family=%s" % (tune, family), flush=True)
                    for shard in index["shards"]:
                        if not any(m["tune"] == tune for m in shard["members"]):
                            continue
                        source = ROOT.TFile.Open(shard["query_root"]["path"], "READ")
                        if not source or source.IsZombie():
                            raise ValueError("cannot open merge source")
                        try:
                            hist = c.read_sparse(source, "sparse_"+family)
                            signature = c._geometry(hist, layout["sparse"][family])
                            if baseline is not None and baseline != signature:
                                raise ValueError("merge geometry/dictionary differs")
                            baseline = signature
                            if merged is None:
                                merged = [_empty_like(hist, "sparse_%s__block_%02d" % (family, block))
                                          for block in range(1, index["block_count"] + 1)]
                            native.Accumulate(hist, merged, ordinal)
                            counts = native.Entries(source, family,
                                [m["tune_ordinal"] for m in shard["members"]],
                                [m["block"] for m in shard["members"]], ordinal, index["block_count"])
                            entries = [old + int(new) for old, new in zip(entries, counts)]
                            del hist
                        finally:
                            source.Close()
                    if merged is None:
                        raise ValueError("tune has no sparse contribution")
                    for block, hist in enumerate(merged, 1):
                        hist.SetEntries(entries[block-1])
                        digest = hashlib.sha256()
                        for coordinates, value, variance in c._cells(hist):
                            line = (c.r.canonical([coordinates, value.hex(), variance.hex()]) + "\n").encode("ascii")
                            digest.update(line)
                            family_digest.update(line)
                        print("MERGE_COMPONENT tune=%s family=%s block=%d cells=%d" %
                              (tune, family, block, hist.GetNbins()), flush=True)
                        size = _write_component(target, hist)
                        objects[family].append({"name": hist.GetName(), "block": block,
                                                "cell_digest": digest.hexdigest(),
                                                "serialized_bytes": size})
                    del hist, merged
                    family_digests[family] = family_digest.hexdigest()
            finally:
                target.Close()
            part = {"tune": tune, "families": list(c.FAMILIES),
                    "root": c._fact(root_path), "cell_digests": family_digests,
                    "sparse_objects": objects}
            # Use the same component-aware verifier as cold collection readers.
            check = dict(index, shards=[], partitions=[part])
            c._verify_sparse_roots(check)
            partitions.append(part)
        merged_index = dict(index)
        merged_index["layout"] = "MERGED"
        merged_index["partitions"] = partitions
        merged_index["merge_elapsed_seconds"] = time.monotonic() - started
        # File locators change on publication; scientific identity does not.
        for part in partitions:
            part["root"]["path"] = str(output / Path(part["root"]["path"]).name)
        merged_index.pop("merge_elapsed_seconds")
        c.r.atomic_json(stage / "index.json", merged_index, exclusive=True)
        receipt = {"schema": c.MERGE_SCHEMA,
                   "parent_index_path": str(Path(index_path).absolute()),
                   "parent_index_sha256": expected_sha256,
                   "merged_index_sha256": c.r.sha_file(stage / "index.json"),
                   "scientific_identity_sha256": index["scientific_identity_sha256"],
                   "expected_sources_sha256": c.r.sha_bytes(
                       c.r.canonical(index["sources"]).encode("ascii")),
                   "partitions": partitions}
        c.r.atomic_json(stage / "merge-receipt.json", receipt, exclusive=True)
        for path in stage.iterdir():
            c.r.fsync_file(path)
        c.r.fsync_directory(stage)
        publication_started = True
        c.q.publish_directory(stage, output)
        c.r.fsync_directory(output.parent)
        c.verify_merge_lineage(output / "index.json", c.r.sha_file(output / "index.json"),
                               output / "merge-receipt.json",
                               c.r.sha_file(output / "merge-receipt.json"),
                               verification_output=output / "merge-verification.json")
        return output / "index.json"
    finally:
        if not publication_started and stage.exists():
            print("MERGE_RETAINED_STAGE=" + str(stage), file=sys.stderr, flush=True)


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
    verify.add_argument("--merge-receipt", type=Path, required=True)
    verify.add_argument("--merge-receipt-sha256", required=True)
    verify.add_argument("--verification-output", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "build":
            path = merge(args.index, args.expected_index_sha256, args.output)
            print("MERGED_COLLECTION_INDEX="+str(path))
            print("MERGED_COLLECTION_SHA256="+c.r.sha_file(path))
            print("MERGE_LINEAGE="+str(path.parent / "merge-receipt.json"))
            print("MERGE_LINEAGE_SHA256="+c.r.sha_file(path.parent / "merge-receipt.json"))
            print("MERGE_VERIFICATION="+str(path.parent / "merge-verification.json"))
            print("MERGE_VERIFICATION_SHA256="+
                  c.r.sha_file(path.parent / "merge-verification.json"))
        else:
            index = c.read(args.index, args.expected_index_sha256,
                           verify_roots=False)
            if index["layout"] != "MERGED":
                raise ValueError("collection is not physically merged")
            c.verify_merge_lineage(args.index, args.expected_index_sha256,
                                   args.merge_receipt,
                                   args.merge_receipt_sha256,
                                   verification_output=args.verification_output)
            print("MERGED_COLLECTION_VERIFIED="+index["scientific_identity_sha256"])
            if args.verification_output is not None:
                print("MERGE_VERIFICATION="+str(args.verification_output.absolute()))
                print("MERGE_VERIFICATION_SHA256="+
                      c.r.sha_file(args.verification_output.absolute()))
    except (OSError, ValueError, KeyError, TypeError) as error:
        print("ERROR: "+str(error), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
