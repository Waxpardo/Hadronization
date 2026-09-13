#!/usr/bin/env python3
"""Finite local planning and verification for a bounded query collection.

This wrapper never transfers data, submits jobs, builds a query executable, or
accepts scientific content.  It validates caller-pinned local inputs and emits
argv for the accepted query commands.  Collection closure requires a separate
caller-owned content-pin file and writes the collection manifest last.
"""

import argparse
import importlib.util
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
PLAN_SCHEMA = "hadronization_query_campaign_plan_v1"
PINS_SCHEMA = "hadronization_query_campaign_content_pins_v1"
MANIFEST_SCHEMA = "hadronization_query_campaign_manifest_v1"


def load_query():
    spec = importlib.util.spec_from_file_location("campaign_query_api", ROOT / "pipeline/query/run.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


q = load_query()
r = q.reduce


def file_fact(path):
    r.regular_file(path, "campaign artifact")
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": r.sha_file(path)}


def pinned_file(path, expected_bytes, expected_sha256, label):
    r.lower_sha(expected_sha256, label + " SHA256")
    r.reject_symlink_components(path, label)
    r.regular_file(path, label)
    if path.stat().st_size != expected_bytes or r.sha_file(path) != expected_sha256:
        raise ValueError(label + " differs from its accepted physical identity")


def local_path(manifest_path, value):
    path = Path(value)
    if not path.is_absolute():
        path = manifest_path.parent / path
    return path.absolute()


def read_acquisition(path, expected_sha256, maximum_shards, maximum_root_bytes):
    r.lower_sha(expected_sha256, "trusted acquisition manifest")
    r.reject_symlink_components(path, "acquisition manifest")
    r.regular_file(path, "acquisition manifest")
    if r.sha_file(path) != expected_sha256:
        raise ValueError("acquisition manifest differs from trusted digest")
    payload = r.json_file(path)
    if (payload.get("schema") != "phasea_local_input_acquisition_manifest_v1" or
            payload.get("status") != "COMPLETE" or
            not payload.get("manifest_written_last")):
        raise ValueError("acquisition manifest is not complete")
    entries = payload.get("inputs")
    if (type(maximum_shards) is not int or maximum_shards <= 0 or
            not isinstance(entries, list) or not entries or len(entries) > maximum_shards or
            type(maximum_root_bytes) is not int or maximum_root_bytes <= 0):
        raise ValueError("acquisition bounds differ")
    checked, source_ids = [], []
    for item in entries:
        ordinal = item.get("ordinal")
        if type(ordinal) is not int or ordinal < 0:
            raise ValueError("acquisition ordinal differs")
        root_path = local_path(path, item["root_path"])
        receipt_path = local_path(path, item["receipt_path"])
        pinned_file(root_path, item["root_bytes"], item["root_sha256"], "accepted ROOT")
        pinned_file(receipt_path, item["receipt_bytes"], item["receipt_sha256"],
                    "accepted receipt")
        receipt = r.json_file(receipt_path)
        q.validate_parent(receipt)
        storage = receipt["storage_identity"]
        if (receipt["shard_ordinal"] != ordinal or storage["root_bytes"] != item["root_bytes"] or
                storage["root_sha256"] != item["root_sha256"] or
                receipt["binding"]["source_ids"] != storage["source_ids"]):
            raise ValueError("acquired receipt/root binding differs")
        source_ids.extend(receipt["binding"]["source_ids"])
        checked.append({
            "ordinal": ordinal,
            "root": file_fact(root_path),
            "receipt": file_fact(receipt_path),
            "accepted_receipt_sha256": item["receipt_sha256"],
            "source_ids": receipt["binding"]["source_ids"],
        })
    if ([item["ordinal"] for item in checked] != sorted(set(item["ordinal"] for item in checked)) or
            source_ids != sorted(set(source_ids))):
        raise ValueError("acquisition shard/source order differs")
    if sum(item["root"]["bytes"] for item in checked) > maximum_root_bytes:
        raise ValueError("acquisition exceeds the campaign ROOT-byte bound")
    return checked


def make_plan(args):
    r.reject_symlink_components(args.output.absolute(), "campaign plan output")
    if args.output.exists():
        raise ValueError("campaign plan output already exists")
    entries = read_acquisition(args.acquisition_manifest.absolute(),
                               args.expected_acquisition_sha256,
                               args.maximum_shards, args.maximum_root_bytes)
    analysis, analysis_sha256 = q.model.checked_analysis(args.analysis)
    layout = r.json_file(args.layout)
    q.require_phase_a_layout(layout)
    dictionary = q.read_dictionary(args.dictionary)
    if not set(q.configured_pdgs(analysis)).issubset(dictionary["body"]["pdgs"]):
        raise ValueError("campaign dictionary omits configured identities")
    _, _, prepared_receipt = q.load_prepared_pack(args.prepared_pack)
    collection, work = args.collection.absolute(), args.work_root.absolute()
    r.reject_symlink_components(collection, "query campaign collection")
    r.reject_symlink_components(work, "query campaign work root")
    if (collection / "manifest.json").exists():
        raise ValueError("query campaign collection is already closed")
    plan = {
        "schema": PLAN_SCHEMA,
        "state": "FINITE_LOCAL_PLAN",
        "scientific_acceptance": "EXTERNAL_REQUIRED",
        "acquisition_manifest": file_fact(args.acquisition_manifest.absolute()),
        "analysis": file_fact(args.analysis.absolute()),
        "layout": file_fact(args.layout.absolute()),
        "dictionary": file_fact(args.dictionary.absolute()),
        "dictionary_body_sha256": dictionary["body_sha256"],
        "prepared_pack": str(args.prepared_pack.absolute()),
        "prepared_build_id": prepared_receipt["build_id"],
        "collection": str(collection),
        "work_root": str(work),
        "limits": {
            "maximum_shards": args.maximum_shards,
            "maximum_root_bytes": args.maximum_root_bytes,
            "shards": len(entries),
            "root_bytes": sum(item["root"]["bytes"] for item in entries),
        },
        "inputs": entries,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    r.atomic_json(args.output, plan, exclusive=True)
    r.fsync_file(args.output)
    r.fsync_directory(args.output.parent)
    return plan


def read_plan(path, expected_sha256):
    r.lower_sha(expected_sha256, "trusted campaign plan")
    r.reject_symlink_components(path, "query campaign plan")
    r.regular_file(path, "query campaign plan")
    if r.sha_file(path) != expected_sha256:
        raise ValueError("query campaign plan differs from trusted digest")
    plan = r.json_file(path)
    if plan.get("schema") != PLAN_SCHEMA or plan.get("state") != "FINITE_LOCAL_PLAN":
        raise ValueError("query campaign plan schema/state differs")
    for key in ("analysis", "layout", "dictionary"):
        fact = plan[key]
        pinned_file(Path(fact["path"]), fact["bytes"], fact["sha256"], "planned " + key)
    q.require_phase_a_layout(r.json_file(Path(plan["layout"]["path"])))
    dictionary = q.read_dictionary(Path(plan["dictionary"]["path"]))
    if dictionary["body_sha256"] != plan["dictionary_body_sha256"]:
        raise ValueError("planned campaign dictionary body differs")
    _, _, prepared_receipt = q.load_prepared_pack(Path(plan["prepared_pack"]))
    if prepared_receipt["build_id"] != plan["prepared_build_id"]:
        raise ValueError("planned prepared query build differs")
    for item in plan["inputs"]:
        pinned_file(Path(item["root"]["path"]), item["root"]["bytes"],
                    item["root"]["sha256"], "planned accepted ROOT")
        pinned_file(Path(item["receipt"]["path"]), item["receipt"]["bytes"],
                    item["receipt"]["sha256"], "planned accepted receipt")
    return plan


def worker_argv(plan, ordinal):
    selected = [item for item in plan["inputs"] if item["ordinal"] == ordinal]
    if len(selected) != 1:
        raise ValueError("worker ordinal is not uniquely planned")
    item = selected[0]
    output = Path(plan["collection"]) / "shards" / "shard-{:04d}".format(ordinal)
    if output.exists():
        raise ValueError("worker output already exists; verify, never overwrite")
    return [
        sys.executable, "-B", str(ROOT / "hadronization"), "query", "build",
        "--input", item["root"]["path"],
        "--receipt", item["receipt"]["path"],
        "--accepted-receipt-sha256", item["accepted_receipt_sha256"],
        "--analysis", plan["analysis"]["path"],
        "--layout", plan["layout"]["path"],
        "--dictionary", plan["dictionary"]["path"],
        "--prepared-pack", plan["prepared_pack"],
        "--output", str(output),
        "--work-root", str(Path(plan["work_root"]) / "query"),
    ]


def census_argv(plan, output):
    source_ids = [source for item in plan["inputs"] for source in item["source_ids"]]
    if source_ids != list(range(len(source_ids))):
        raise ValueError("census requires the complete contiguous campaign source domain")
    if output.exists():
        raise ValueError("census output already exists")
    command = [sys.executable, "-B", str(ROOT / "hadronization"), "query", "census"]
    for item in plan["inputs"]:
        command.extend(["--input", item["root"]["path"],
                        "--receipt", item["receipt"]["path"],
                        "--accepted-receipt-sha256", item["accepted_receipt_sha256"]])
    command.extend(["--expected-source-count", str(len(source_ids)),
                    "--analysis", plan["analysis"]["path"],
                    "--prepared-pack", plan["prepared_pack"],
                    "--output", str(output.absolute()),
                    "--work-root", str(Path(plan["work_root"]) / "query")])
    return command


def read_content_pins(path, expected_sha256, ordinals):
    r.lower_sha(expected_sha256, "trusted campaign content pins")
    r.reject_symlink_components(path, "campaign content pins")
    r.regular_file(path, "campaign content pins")
    if r.sha_file(path) != expected_sha256:
        raise ValueError("campaign content pins differ from trusted digest")
    payload = r.json_file(path)
    if payload.get("schema") != PINS_SCHEMA or payload.get("scientific_acceptance") != "EXTERNAL":
        raise ValueError("campaign content pins do not carry external authority")
    entries = payload.get("pins")
    if not isinstance(entries, list):
        raise ValueError("campaign content pins differ")
    pins = {}
    for item in entries:
        ordinal, digest = item.get("ordinal"), item.get("scientific_content_sha256")
        if ordinal in pins:
            raise ValueError("duplicate campaign content pin")
        r.lower_sha(digest, "trusted query content")
        pins[ordinal] = digest
    if sorted(pins) != sorted(ordinals):
        raise ValueError("campaign content pin membership differs")
    return pins


def verify_collection(plan, pins_path, expected_pins_sha256):
    ordinals = [item["ordinal"] for item in plan["inputs"]]
    pins = read_content_pins(pins_path, expected_pins_sha256, ordinals)
    collection = Path(plan["collection"])
    shards = collection / "shards"
    r.reject_symlink_components(shards, "query campaign shards")
    expected_names = {"shard-{:04d}".format(ordinal) for ordinal in ordinals}
    if not shards.is_dir() or {path.name for path in shards.iterdir()} != expected_names:
        raise ValueError("query campaign shard fileset differs")
    records, source_ids, dictionaries = [], [], []
    by_ordinal = {item["ordinal"]: item for item in plan["inputs"]}
    for ordinal in ordinals:
        name = "shard-{:04d}".format(ordinal)
        workspace = shards / name
        manifest, _ = q.verify(workspace, Path(plan["work_root"]) / "verify" / name,
                               pins[ordinal], Path(plan["prepared_pack"]))
        metadata = r.json_file(workspace / "metadata.json")
        planned = by_ordinal[ordinal]
        if (metadata["input_receipt_sha256"] != planned["accepted_receipt_sha256"] or
                metadata["input_root_sha256"] != planned["root"]["sha256"] or
                metadata["analysis_sha256"] != plan["analysis"]["sha256"] or
                metadata["layout_sha256"] != plan["layout"]["sha256"] or
                metadata["dictionary_sha256"] != plan["dictionary"]["sha256"]):
            raise ValueError("query campaign worker binding differs from plan")
        members = metadata["input_receipt"]["binding"]["source_ids"]
        if members != planned["source_ids"]:
            raise ValueError("query campaign source binding differs from plan")
        source_ids.extend(members)
        dictionaries.append(metadata["dictionary_body_sha256"])
        records.append({
            "ordinal": ordinal,
            "source_ids": members,
            "scientific_content_sha256": pins[ordinal],
            "manifest": file_fact(workspace / "manifest.json"),
            "query_root": file_fact(workspace / "query.root"),
            "source_rows": manifest["source_rows"],
        })
    expected_sources = [source for item in plan["inputs"] for source in item["source_ids"]]
    if source_ids != expected_sources:
        raise ValueError("query campaign source union differs")
    q.require_dictionary_consensus(dictionaries)
    return records


def close_collection(plan, pins_path, expected_pins_sha256):
    collection = Path(plan["collection"])
    manifest_path = collection / "manifest.json"
    if manifest_path.exists():
        raise ValueError("query campaign manifest already exists")
    records = verify_collection(plan, pins_path, expected_pins_sha256)
    if {path.name for path in collection.iterdir()} != {"shards"}:
        raise ValueError("query campaign collection contains pre-closure extras")
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "state": "VERIFIED_NONPUBLICATION_COLLECTION",
        "scientific_acceptance": "EXTERNAL_REQUIRED",
        "plan_sha256": plan["_trusted_sha256"],
        "content_pins_sha256": expected_pins_sha256,
        "dictionary_body_sha256": plan["dictionary_body_sha256"],
        "source_ids": [source for item in records for source in item["source_ids"]],
        "shards": records,
    }
    r.atomic_json(manifest_path, manifest, exclusive=True)
    r.fsync_file(manifest_path)
    r.fsync_directory(collection)
    if {path.name for path in collection.iterdir()} != {"shards", "manifest.json"}:
        raise ValueError("query campaign exact closed fileset differs")
    return manifest_path


def common_plan_arguments(parser):
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--expected-plan-sha256", required=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    plan = commands.add_parser("plan", help="validate bounded local inputs and freeze a finite plan")
    plan.add_argument("--acquisition-manifest", required=True, type=Path)
    plan.add_argument("--expected-acquisition-sha256", required=True)
    plan.add_argument("--analysis", type=Path, default=ROOT / "config/analysis.json")
    plan.add_argument("--layout", type=Path, default=ROOT / "config/query.json")
    plan.add_argument("--dictionary", required=True, type=Path)
    plan.add_argument("--prepared-pack", required=True, type=Path)
    plan.add_argument("--collection", required=True, type=Path)
    plan.add_argument("--work-root", required=True, type=Path)
    plan.add_argument("--maximum-shards", required=True, type=int)
    plan.add_argument("--maximum-root-bytes", required=True, type=int)
    plan.add_argument("--output", required=True, type=Path)
    worker = commands.add_parser("worker-argv", help="emit one no-overwrite query worker argv")
    common_plan_arguments(worker)
    worker.add_argument("--ordinal", required=True, type=int)
    census = commands.add_parser("census-argv", help="emit one complete-domain census argv")
    common_plan_arguments(census)
    census.add_argument("--output", required=True, type=Path)
    verify = commands.add_parser("verify", help="verify a complete collection against external pins")
    common_plan_arguments(verify)
    verify.add_argument("--content-pins", required=True, type=Path)
    verify.add_argument("--expected-content-pins-sha256", required=True)
    close = commands.add_parser("close", help="verify and write the collection manifest last")
    common_plan_arguments(close)
    close.add_argument("--content-pins", required=True, type=Path)
    close.add_argument("--expected-content-pins-sha256", required=True)
    args = parser.parse_args()
    try:
        if args.command == "plan":
            make_plan(args)
            print("QUERY_CAMPAIGN_PLAN=" + str(args.output.absolute()))
            return 0
        value = read_plan(args.plan.absolute(), args.expected_plan_sha256)
        value["_trusted_sha256"] = args.expected_plan_sha256
        if args.command == "worker-argv":
            print(r.canonical(worker_argv(value, args.ordinal)))
        elif args.command == "census-argv":
            print(r.canonical(census_argv(value, args.output)))
        elif args.command == "verify":
            records = verify_collection(value, args.content_pins.absolute(),
                                        args.expected_content_pins_sha256)
            print("QUERY_CAMPAIGN_VERIFIED shards={}".format(len(records)))
        else:
            path = close_collection(value, args.content_pins.absolute(),
                                    args.expected_content_pins_sha256)
            print("QUERY_CAMPAIGN_CLOSED=" + str(path))
        return 0
    except (OSError, ValueError, KeyError, RuntimeError) as error:
        print("ERROR: " + str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
