"""One checked locator for block-resolved query sparsities and exact support.

The index is transport metadata. Its scientific digest excludes file paths and
physical checksums; callers must independently pin the index SHA-256.
"""

import argparse
from array import array
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import sys

ROOT_DIR = Path(__file__).resolve().parents[2]


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(filename))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


q = _load("collection_query", "run.py")
r = q.reduce
FAMILIES = tuple(sorted(q.require_phase_a_layout(r.json_file(ROOT_DIR / "config/query.json"))["sparse"]))
TREES = tuple(sorted(q.require_phase_a_layout(r.json_file(ROOT_DIR / "config/query.json"))["trees"]))
SCHEMA = "hadronization_query_collection_v1"
LINEAGE_SCHEMA = "hadronization_query_collection_source_lineage_v1"
ADMISSION_SCHEMA = "hadronization_query_collection_admission_closure_v1"
MERGE_SCHEMA = "hadronization_query_merge_lineage_v1"


def _root():
    import ROOT
    ROOT.gROOT.SetBatch(True)
    return ROOT


def read_sparse(file, name):
    """Give the returned THnSparse a Python owner for its native allocation.

    ROOT's sparse reader does not attach these objects to the TFile, and
    PyROOT otherwise returns a non-owning proxy. Closing the file or dropping
    that proxy then leaks the histogram. Detach first if a ROOT version does
    attach it, so the file and Python cannot both delete the same object.
    """
    histogram = file.Get(name)
    if histogram and histogram.InheritsFrom("THnSparse"):
        file.GetList().Remove(histogram)
        _root().SetOwnership(histogram, True)
    return histogram


def _fact(path):
    path = Path(path).absolute()
    r.reject_symlink_components(path, "collection artifact")
    r.regular_file(path, "collection artifact")
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": r.sha_file(path)}


def _check_fact(fact):
    r.exact_keys(fact, {"path", "bytes", "sha256"}, "collection file fact")
    path = Path(fact["path"])
    if not path.is_absolute() or _fact(path) != fact:
        raise ValueError("collection file physical identity differs")
    return path


def _members(metadata):
    receipt = metadata["input_receipt"]
    q.validate_parent(receipt)
    binding = receipt["binding"]
    result = []
    for source in receipt["sources"]:
        row = source["manifest_row"]
        result.append({"source_id": source["source_id"], "tune": row["tune"],
                       "tune_ordinal": binding["tune_ordinals"][row["tune"]],
                       "logical_id": row["logical_id"], "block": row["block"],
                       "events": row["successful_events"]})
    if [m["source_id"] for m in result] != binding["source_ids"]:
        raise ValueError("query source-local/global mapping differs")
    return result


def scientific_identity(index):
    return {"schema": "hadronization_query_collection_science_v1",
            "analysis_sha256": index["analysis_sha256"],
            "layout_sha256": index["layout_sha256"],
            "dictionary_body_sha256": index["dictionary_body_sha256"],
            "campaign": index["campaign"], "manifest_sha256": index["manifest_sha256"],
            "tune_ordinals": index["tune_ordinals"], "block_count": index["block_count"],
            "sources": index["sources"],
            "shard_content": [{"ordinal": s["ordinal"],
                               "scientific_content_sha256": s["scientific_content_sha256"]}
                              for s in index["shards"]]}


def _check_members(index, expected_sources):
    sources = [m for s in index["shards"] for m in s["members"]]
    ids = [m["source_id"] for m in sources]
    natural = [(m["tune"], m["logical_id"]) for m in sources]
    if len(ids) != len(set(ids)) or len(natural) != len(set(natural)):
        raise ValueError("duplicate global or natural source identity")
    if sorted(sources, key=lambda m: m["source_id"]) != expected_sources:
        raise ValueError("collection source membership differs from independent expected domain")
    if sources != index["sources"]:
        raise ValueError("collection source mapping differs")
    for member in sources:
        if (member["tune_ordinal"] != index["tune_ordinals"][member["tune"]] or
                member["block"] != member["logical_id"] % index["block_count"] + 1 or
                member["events"] <= 0):
            raise ValueError("collection natural tune/block membership differs")


def create(workspaces, content_pins, expected_sources, output, work_root, test_only=False,
           prepared_pack=None):
    if len(workspaces) != len(content_pins) or not workspaces:
        raise ValueError("one independently supplied content pin is required per shard")
    if output.exists():
        raise ValueError("collection index already exists")
    records = []
    common = None
    for workspace, pin in zip(workspaces, content_pins):
        workspace = Path(workspace).absolute()
        q.verify(workspace, work_root, pin, prepared_pack=prepared_pack)
        metadata = r.json_file(workspace / "metadata.json")
        binding = metadata["input_receipt"]["binding"]
        identity = (metadata["analysis_sha256"], metadata["layout_sha256"],
                    metadata["dictionary_body_sha256"], binding["campaign"],
                    binding["manifest_sha256"], binding["block_assignment"]["count"],
                    tuple(sorted(binding["tune_ordinals"].items())))
        if common is None:
            common = identity
        elif common != identity:
            raise ValueError("query shards have incompatible analysis/geometry/dictionary/campaign")
        records.append({"ordinal": binding["shard_ordinal"],
                        "scientific_content_sha256": pin,
                        "workspace_manifest": _fact(workspace / "manifest.json"),
                        "query_root": _fact(workspace / "query.root"),
                        "metadata": _fact(workspace / "metadata.json"),
                        "members": _members(metadata)})
    if [s["ordinal"] for s in records] != sorted({s["ordinal"] for s in records}):
        raise ValueError("duplicate or unordered query shard ordinal")
    expected = sorted(expected_sources, key=lambda m: m["source_id"])
    index = {"schema": SCHEMA, "layout": "SHARDED", "state": "TEST_ONLY" if test_only else "EXTERNAL_ACCEPTANCE_REQUIRED",
             "analysis_sha256": common[0], "layout_sha256": common[1],
             "dictionary_body_sha256": common[2], "campaign": common[3],
             "manifest_sha256": common[4], "block_count": common[5],
             "tune_ordinals": dict(common[6]), "sources": [m for s in records for m in s["members"]],
             "shards": records, "partitions": []}
    _check_members(index, expected)
    index["scientific_identity_sha256"] = r.sha_bytes(r.canonical(scientific_identity(index)).encode("ascii"))
    _verify_sparse_roots(index)
    r.atomic_json(output, index, exclusive=True)
    return index


def read(path, expected_sha256, verify_roots=True):
    r.lower_sha(expected_sha256, "trusted collection index")
    if r.sha_file(path) != expected_sha256:
        raise ValueError("collection index differs from trusted SHA-256")
    index = r.json_file(path)
    r.exact_keys(index, {"schema", "layout", "state", "analysis_sha256", "layout_sha256",
                         "dictionary_body_sha256", "campaign", "manifest_sha256", "block_count",
                         "tune_ordinals", "sources", "shards", "partitions", "scientific_identity_sha256"},
                 "collection index")
    if (index["schema"] != SCHEMA or index["layout"] not in {"SHARDED", "MERGED"} or
            index["state"] not in {"TEST_ONLY", "EXTERNAL_ACCEPTANCE_REQUIRED"}):
        raise ValueError("collection schema/layout differs")
    if r.sha_bytes(r.canonical(scientific_identity(index)).encode("ascii")) != index["scientific_identity_sha256"]:
        raise ValueError("collection scientific identity differs")
    if [s["ordinal"] for s in index["shards"]] != sorted({s["ordinal"] for s in index["shards"]}):
        raise ValueError("collection shard domain differs")
    _check_members(index, sorted(index["sources"], key=lambda m: m["source_id"]))
    for shard in index["shards"]:
        for key in ("workspace_manifest", "query_root", "metadata"):
            _check_fact(shard[key])
        metadata = r.json_file(Path(shard["metadata"]["path"]))
        if (_members(metadata) != shard["members"] or
                metadata["query_content_sha256"] != shard["scientific_content_sha256"] or
                metadata["dictionary_body_sha256"] != index["dictionary_body_sha256"] or
                metadata["analysis_sha256"] != index["analysis_sha256"] or
                metadata["layout_sha256"] != index["layout_sha256"]):
            raise ValueError("query shard metadata/content membership differs")
    if index["layout"] == "MERGED":
        expected = set(index["tune_ordinals"])
        if {p["tune"] for p in index["partitions"]} != expected or len(index["partitions"]) != len(expected):
            raise ValueError("merged tune partition coverage differs")
        for part in index["partitions"]:
            r.exact_keys(part, {"tune", "families", "root", "cell_digests"}, "merged partition")
            _check_fact(part["root"])
            if set(part["families"]) != set(FAMILIES):
                raise ValueError("merged sparse family coverage differs")
            if set(part["cell_digests"]) != set(FAMILIES):
                raise ValueError("merged sparse content digest coverage differs")
    elif index["partitions"]:
        raise ValueError("sharded index cannot contain merged partitions")
    if verify_roots:
        _verify_sparse_roots(index)
    return index


def admission_closure(index_path, expected_index_sha256, expected_sources_path,
                      expected_sources_sha256, *, work_path=None, expected_work_sha256=None,
                      closure_path=None, expected_closure_sha256=None,
                      merge_receipt_path=None, expected_merge_receipt_sha256=None):
    """Prove exact query-source closure without promoting TEST_ONLY to accepted.

    An externally pinned site-bound work record and collector closure are both
    required for the accepted-campaign qualification. A ledger or aggregate
    count alone cannot provide it.
    """
    index = read(index_path, expected_index_sha256)
    expected_sources_path = Path(expected_sources_path).absolute()
    r.lower_sha(expected_sources_sha256, "trusted expected source domain")
    r.reject_symlink_components(expected_sources_path, "expected source domain")
    r.regular_file(expected_sources_path, "expected source domain")
    if r.sha_file(expected_sources_path) != expected_sources_sha256:
        raise ValueError("expected source domain differs from independent pin")
    expected = r.json_file(expected_sources_path)
    if not isinstance(expected, list) or expected != sorted(index["sources"], key=lambda m: m["source_id"]):
        raise ValueError("exact expected source membership differs from query collection")
    _check_members(index, expected)
    descriptors = set()
    for shard in index["shards"]:
        metadata = r.json_file(Path(shard["metadata"]["path"]))
        binding = metadata["input_receipt"]["binding"]
        descriptors.add(binding["campaign_descriptor_sha256"])
        if binding["manifest_sha256"] != index["manifest_sha256"]:
            raise ValueError("query parent accepted manifest differs")
    if len(descriptors) != 1:
        raise ValueError("query parent campaign descriptor differs across shards")
    campaign_descriptor_sha = descriptors.pop()
    r.lower_sha(campaign_descriptor_sha, "accepted campaign descriptor")
    if (work_path is None) != (expected_work_sha256 is None) or (closure_path is None) != (expected_closure_sha256 is None):
        raise ValueError("admission proof path and independent SHA must be paired")
    if (work_path is None) != (closure_path is None):
        raise ValueError("accepted closure requires both site work and collector manifest")
    if (merge_receipt_path is None) != (expected_merge_receipt_sha256 is None):
        raise ValueError("merge lineage path and independent SHA must be paired")
    parent_index_sha = expected_index_sha256
    if index["layout"] == "MERGED" and merge_receipt_path is not None:
        merge_lineage = verify_merge_lineage(index_path, expected_index_sha256,
                                             merge_receipt_path,
                                             expected_merge_receipt_sha256)
        parent_index_sha = merge_lineage["parent_index_sha256"]
    elif merge_receipt_path is not None:
        raise ValueError("sharded collection cannot carry merge lineage")
    elif index["layout"] == "MERGED" and work_path is not None:
        raise ValueError("accepted merged collection requires pinned merge lineage")
    source_count = len(index["sources"])
    event_count = sum(member["events"] for member in index["sources"])
    qualification = "TEST_ONLY_DOMAIN_CLOSED" if index["state"] == "TEST_ONLY" else "NO_ACCEPTED_CLOSURE"
    work_sha = None
    closure_sha = None
    campaign_sha = None
    acquisition_sha = None
    external_pins_sha = None
    if work_path is not None:
        if index["state"] == "TEST_ONLY":
            raise ValueError("TEST_ONLY collection cannot carry accepted site closure")
        work_path, closure_path = Path(work_path).absolute(), Path(closure_path).absolute()
        for path, pin, label in ((work_path, expected_work_sha256, "site-bound work"),
                                 (closure_path, expected_closure_sha256, "collector closure")):
            r.lower_sha(pin, "trusted " + label)
            r.reject_symlink_components(path, label)
            r.regular_file(path, label)
            if r.sha_file(path) != pin:
                raise ValueError(label + " differs from independent pin")
        work, closure = r.json_file(work_path), r.json_file(closure_path)
        if (work.get("schema") != "hadronization_condor_query_work_v1" or
                work.get("state") != "SITE_BOUND" or
                work.get("storage_semantics") != "POSIX_NOOVERWRITE_VERIFIED" or
                work.get("expected_sources_sha256") != expected_sources_sha256 or
                work.get("campaign_id") != index["campaign"] or
                work.get("source_manifest_sha256") != index["manifest_sha256"] or
                work.get("analysis_sha256") != index["analysis_sha256"] or
                work.get("layout_sha256") != index["layout_sha256"] or
                work.get("tune_ordinals") != index["tune_ordinals"] or
                work.get("block_count") != index["block_count"] or
                work.get("expected_source_count") != source_count or
                work.get("expected_event_count") != event_count or
                not isinstance(work.get("work"), list) or
                any(not isinstance(item, dict) or not isinstance(item.get("root"), dict) or
                    type(item["root"].get("bytes")) is not int for item in work["work"]) or
                work.get("input_file_count") != 2 * len(work["work"]) or
                work.get("input_root_bytes") != sum(
                    item.get("root", {}).get("bytes", 0) for item in work["work"]) or
                [item.get("ordinal") for item in work["work"]] !=
                [shard["ordinal"] for shard in index["shards"]]):
            raise ValueError("site-bound work does not bind exact query campaign domain")
        for shard, item in zip(index["shards"], work["work"]):
            metadata = r.json_file(Path(shard["metadata"]["path"]))
            root, receipt = item.get("root"), item.get("receipt")
            if (not isinstance(root, dict) or not isinstance(receipt, dict) or
                    root.get("sha256") != metadata["input_root_sha256"] or
                    root.get("bytes") != metadata["admission_build"]["root_bytes"] or
                    receipt.get("sha256") != metadata["input_receipt_sha256"]):
                raise ValueError("site work analyzed shard facts differ from query parents")
        for key in ("campaign_sha256", "acquisition_manifest_sha256", "site_admission_sha256"):
            r.lower_sha(work.get(key), "site work " + key)
        if (closure.get("schema") != "hadronization_query_collection_closure_v1" or
                closure.get("state") != "EXTERNALLY_PINNED" or
                closure.get("work_sha256") != expected_work_sha256 or
                closure.get("index_sha256") != parent_index_sha or
                closure.get("scientific_identity_sha256") != index["scientific_identity_sha256"] or
                closure.get("source_count") != source_count or
                closure.get("event_count") != event_count):
            raise ValueError("collector closure does not bind exact query collection")
        r.lower_sha(closure.get("external_pins_sha256"), "collector external pins")
        qualification = "FULL_ACCEPTED_DOMAIN_CLOSED"
        work_sha, closure_sha = expected_work_sha256, expected_closure_sha256
        campaign_sha, acquisition_sha = work["campaign_sha256"], work["acquisition_manifest_sha256"]
        external_pins_sha = closure["external_pins_sha256"]
    natural_members = [[member["source_id"], member["tune"], member["logical_id"],
                        member["block"], member["events"]] for member in expected]
    by_tune = [{"tune": tune, "sources": sum(member["tune"] == tune for member in expected),
                "events": sum(member["events"] for member in expected if member["tune"] == tune)}
               for tune, _ in sorted(index["tune_ordinals"].items(), key=lambda item: item[1])]
    return {"schema": ADMISSION_SCHEMA, "qualification": qualification,
            "domain_complete": True, "index_state": index["state"],
            "collection_index_sha256": expected_index_sha256,
            "collection_scientific_identity_sha256": index["scientific_identity_sha256"],
            "expected_sources_sha256": expected_sources_sha256,
            "natural_members_sha256": r.sha_bytes(r.canonical(natural_members).encode("ascii")),
            "per_tune_source_event_counts": by_tune,
            "source_count": source_count, "event_count": event_count,
            "campaign": index["campaign"], "campaign_sha256": campaign_sha,
            "acquisition_manifest_sha256": acquisition_sha,
            "campaign_descriptor_sha256": campaign_descriptor_sha,
            "accepted_manifest_sha256": index["manifest_sha256"],
            "work_sha256": work_sha, "collector_closure_sha256": closure_sha,
            "external_pins_sha256": external_pins_sha}


def _sparse_content_equal(sharded, merged):
    """Compare the complete occupied cell domain and additive Sumw2 per tune.

    Object-add can change binary64 reduction order.  A 1e-12 relative/absolute
    tolerance bounds that arithmetic only; it never permits missing cells.
    """
    ROOT = _root()
    for family in FAMILIES:
        for tune, ordinal in sorted(sharded["tune_ordinals"].items(), key=lambda x: x[1]):
            expected = {}
            for shard in sharded["shards"]:
                if not any(member["tune"] == tune for member in shard["members"]):
                    continue
                file = ROOT.TFile.Open(shard["query_root"]["path"], "READ")
                if not file or file.IsZombie():
                    raise ValueError("merge parent sparse ROOT cannot open")
                try:
                    for coordinates, value, variance in _cells(read_sparse(file, "sparse_" + family)):
                        if coordinates[0] == ordinal + 1:
                            old = expected.setdefault(coordinates, ([], []))
                            old[0].append(value)
                            old[1].append(variance)
                finally:
                    file.Close()
            part = next(p for p in merged["partitions"] if p["tune"] == tune)
            file = ROOT.TFile.Open(part["root"]["path"], "READ")
            if not file or file.IsZombie():
                raise ValueError("merge child sparse ROOT cannot open")
            try:
                actual = {coordinates: (value, variance)
                          for coordinates, value, variance in _cells(read_sparse(file, "sparse_" + family))}
            finally:
                file.Close()
            if set(expected) != set(actual):
                raise ValueError("merged sparse occupied cell domain differs from shards")
            for key, (values, variances) in expected.items():
                if not (math.isclose(math.fsum(values), actual[key][0], rel_tol=1e-12, abs_tol=1e-12) and
                        math.isclose(math.fsum(variances), actual[key][1], rel_tol=1e-12, abs_tol=1e-12)):
                    raise ValueError("merged sparse cell/Sumw2 differs from shards")


def verify_merge_lineage(index_path, expected_index_sha256, receipt_path,
                         expected_receipt_sha256):
    """Verify a transformation receipt against both independently pinned layouts."""
    receipt_path = Path(receipt_path).absolute()
    r.lower_sha(expected_receipt_sha256, "trusted merge lineage")
    if r.sha_file(receipt_path) != expected_receipt_sha256:
        raise ValueError("merge lineage differs from independent pin")
    receipt = r.json_file(receipt_path)
    r.exact_keys(receipt, {"schema", "parent_index_path", "parent_index_sha256",
                           "merged_index_sha256", "scientific_identity_sha256",
                           "expected_sources_sha256", "partitions"}, "merge lineage")
    if receipt["schema"] != MERGE_SCHEMA or receipt["merged_index_sha256"] != expected_index_sha256:
        raise ValueError("merge lineage child index differs")
    parent = read(Path(receipt["parent_index_path"]), receipt["parent_index_sha256"])
    child = read(index_path, expected_index_sha256)
    if (parent["layout"] != "SHARDED" or child["layout"] != "MERGED" or
            child["state"] != parent["state"] or
            child["scientific_identity_sha256"] != parent["scientific_identity_sha256"] or
            receipt["scientific_identity_sha256"] != parent["scientific_identity_sha256"] or
            receipt["expected_sources_sha256"] != r.sha_bytes(
                r.canonical(parent["sources"]).encode("ascii")) or
            receipt["partitions"] != child["partitions"] or
            {key: value for key, value in child.items() if key not in ("layout", "partitions")} !=
            {key: value for key, value in parent.items() if key not in ("layout", "partitions")}):
        raise ValueError("merge lineage parent/content/domain differs")
    _sparse_content_equal(parent, child)
    return receipt


def source_lineage(index_path, expected_sha256, requested_tunes=None):
    """Project old compact source-selection fields from checked native parents.

    `read` authenticates the locator, physical query artifacts and native ROOT
    objects. Every field here then comes from its embedded admitted analyzed
    receipt; no raw-file or validation-receipt bytes are independently opened.
    """
    index = read(index_path, expected_sha256)
    tunes = index["tune_ordinals"]
    if requested_tunes is None:
        selected = set(tunes)
    elif (not isinstance(requested_tunes, (list, tuple)) or not requested_tunes or
          len(requested_tunes) != len(set(requested_tunes)) or
          any(tune not in tunes for tune in requested_tunes)):
        raise ValueError("requested lineage tunes differ from verified collection")
    else:
        selected = set(requested_tunes)
    common = None
    members, parents, source_content_digests = [], [], []
    for shard in index["shards"]:
        metadata = r.json_file(Path(shard["metadata"]["path"]))
        receipt = metadata["input_receipt"]
        q.validate_parent(receipt)
        binding, scientific = receipt["binding"], receipt["scientific_identity"]
        producer_commit = scientific["lossless_dependency_identity"][
            "accepted_raw_definition"]["producer_repository_commit"]
        if not isinstance(producer_commit, str) or not re.fullmatch(r"[0-9a-f]{40}", producer_commit):
            raise ValueError("accepted raw producer Git OID differs")
        source_digests = scientific["source_scientific_digests"]
        if len(source_digests) != len(receipt["sources"]):
            raise ValueError("analyzed source scientific digest alignment differs")
        identity = (receipt["campaign"], binding["campaign_descriptor_sha256"],
                    binding["manifest_sha256"], binding["plan_digest"],
                    binding["map_digest"], scientific["structural_registries_digest"],
                    producer_commit)
        if common is None:
            common = identity
        elif identity != common:
            raise ValueError("collection parent campaign/plan/map/registry lineage differs")
        if (binding["shard_ordinal"] != shard["ordinal"] or
                binding["manifest_sha256"] != index["manifest_sha256"] or
                receipt["scientific_identity_sha256"] != r.sha_bytes(
                    r.canonical(scientific).encode("ascii"))):
            raise ValueError("collection shard receipt scientific parent differs")
        parents.append(receipt["scientific_identity_sha256"])
        for source, content_digest in zip(receipt["sources"], source_digests):
            r.lower_sha(content_digest, "accepted analyzed per-source scientific content")
            row = source["manifest_row"]
            if row["tune"] not in selected:
                continue
            source_content_digests.append({"source_id": source["source_id"],
                                           "analyzed_source_scientific_digest": content_digest})
            members.append({"source_id": source["source_id"], "tune_id": row["tune"],
                            "logical_id": row["logical_id"],
                            "accepted_attempt": row["accepted_attempt"],
                            "block_id": row["block"],
                            "successful_events": row["successful_events"],
                            "source_root_sha256": row["raw_sha256"],
                            "source_scientific_digest": r.sha_bytes(
                                r.canonical(row).encode("ascii")),
                            "receipt_sha256": row["validation_receipt_sha256"]})
    members.sort(key=lambda item: item["source_id"])
    source_content_digests.sort(key=lambda item: item["source_id"])
    if ([item["source_id"] for item in source_content_digests] !=
            [item["source_id"] for item in members] or
            len(members) != len({member["source_id"] for member in members}) or
            [(m["source_id"], m["tune_id"], m["logical_id"], m["block_id"], m["successful_events"])
             for m in members] !=
            [(m["source_id"], m["tune"], m["logical_id"], m["block"], m["events"])
             for m in sorted(index["sources"], key=lambda item: item["source_id"])
             if m["tune"] in selected]):
        raise ValueError("source lineage and verified collection membership differ")
    selection = {"campaign_id": common[0], "campaign_descriptor_sha256": common[1],
                 "accepted_manifest_sha256": common[2], "accepted_plan_digest": common[3],
                 "accepted_map_digest": common[4], "members": members,
                 "selected_members_sha256": r.sha_bytes(r.canonical(members).encode("ascii")),
                 "expected_events_by_tune": [
                     {"tune_id": tune, "count": sum(m["successful_events"] for m in members
                                                   if m["tune_id"] == tune)}
                     for tune in sorted(selected)],
                 "provenance_parent_ids": sorted(set(parents))}
    return {"schema": LINEAGE_SCHEMA, "collection_index_sha256": expected_sha256,
            "collection_scientific_identity_sha256": index["scientific_identity_sha256"],
            "collection_state": index["state"], "structural_registry_sha256": common[5],
            "accepted_raw_producer_commit": common[6],
            "source_selection_digest_semantics": "LEGACY_MANIFEST_ROW_SHA256",
            "analyzed_source_scientific_content_digests": source_content_digests,
            "source_selection": selection}


def _axis_signature(axis):
    return (axis.GetName(), tuple(axis.GetBinLowEdge(i) for i in range(1, axis.GetNbins()+2)),
            tuple(axis.GetBinLabel(i) for i in range(1, axis.GetNbins()+1)))


def _geometry(histogram, expected_fields):
    if not histogram or histogram.GetNdimensions() != len(expected_fields) or not histogram.GetCalculateErrors():
        raise ValueError("missing sparse family/dimensions/Sumw2")
    signatures = tuple(_axis_signature(histogram.GetAxis(i)) for i in range(histogram.GetNdimensions()))
    if tuple(s[0] for s in signatures) != tuple(expected_fields):
        raise ValueError("sparse ordered axis names differ")
    return signatures


def _cells(histogram):
    coordinates = array("i", [0]*histogram.GetNdimensions())
    for i in range(histogram.GetNbins()):
        value = histogram.GetBinContent(i, coordinates)
        variance = histogram.GetBinError2(i)
        if not math.isfinite(value) or not math.isfinite(variance) or variance < 0:
            raise ValueError("nonfinite sparse cell/Sumw2")
        yield tuple(coordinates), value, variance


def _verify_sparse_roots(index):
    ROOT = _root()
    layout = r.json_file(ROOT_DIR / "config/query.json")
    q.require_phase_a_layout(layout)
    baseline = {}
    source_map = {(m["tune_ordinal"], m["block"]) for m in index["sources"]}
    paths = [(s["query_root"]["path"], {(m["tune_ordinal"], m["block"]) for m in s["members"]}, True, None)
             for s in index["shards"]]
    paths += [(p["root"]["path"], {(index["tune_ordinals"][p["tune"]], m["block"])
                                      for m in index["sources"] if m["tune"] == p["tune"]}, False, p)
              for p in index["partitions"]]
    for path, allowed, is_shard, partition in paths:
        file = ROOT.TFile.Open(path, "READ")
        if not file or file.IsZombie():
            raise ValueError("cannot open collection ROOT")
        try:
            keys = {key.GetName(): key.GetClassName() for key in file.GetListOfKeys()}
            expected_keys = {"sparse_"+family for family in FAMILIES}
            if is_shard:
                expected_keys |= set(TREES) | {"query_spec", "metadata"}
            if set(keys) != expected_keys:
                raise ValueError("required exact support/sparse object set differs")
            if is_shard:
                for tree in TREES:
                    rows = file.Get(tree)
                    if (keys[tree] != "TTree" or not rows or
                            [branch.GetName() for branch in rows.GetListOfBranches()] != layout["trees"][tree]):
                        raise ValueError("required exact support tree schema differs")
            for family in FAMILIES:
                hist = read_sparse(file, "sparse_"+family)
                signature = _geometry(hist, layout["sparse"][family])
                if family in baseline and baseline[family] != signature:
                    raise ValueError("sparse geometry/dictionary differs across collection")
                baseline[family] = signature
                for coord, _, _ in _cells(hist):
                    key = (coord[0]-1, coord[1])
                    if key not in allowed or key not in source_map:
                        raise ValueError("sparse occupied tune/block lies outside receipt membership")
                if partition is not None:
                    digest = hashlib.sha256()
                    for coordinates, value, variance in _cells(hist):
                        digest.update(r.canonical([coordinates, value.hex(), variance.hex()]).encode("ascii"))
                        digest.update(b"\n")
                    if digest.hexdigest() != partition["cell_digests"][family]:
                        raise ValueError("merged sparse readback digest differs")
        finally:
            file.Close()


def partitions(index, family):
    if family not in FAMILIES:
        raise ValueError("unknown sparse family")
    if index["layout"] == "SHARDED":
        return [(s["query_root"]["path"], family, tuple(sorted({m["tune"] for m in s["members"]})))
                for s in index["shards"]]
    return [(p["root"]["path"], family, (p["tune"],)) for p in index["partitions"]]


def iter_support(index, tree):
    """Stream exact rows with their immutable shard identity; local IDs never join across shards."""
    if tree not in TREES:
        raise ValueError("unknown exact support tree")
    ROOT = _root()
    for shard in index["shards"]:
        file = ROOT.TFile.Open(shard["query_root"]["path"], "READ")
        if not file or file.IsZombie():
            raise ValueError("cannot open exact support shard")
        try:
            rows = file.Get(tree)
            if not rows:
                raise ValueError("required exact support object is missing")
            fields = [branch.GetName() for branch in rows.GetListOfBranches()]
            for row in rows:
                yield shard["ordinal"], {field: getattr(row, field) for field in fields}
        finally:
            file.Close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    create_parser = commands.add_parser("create")
    create_parser.add_argument("--workspace", type=Path, action="append", required=True)
    create_parser.add_argument("--expected-content-sha256", action="append", required=True)
    create_parser.add_argument("--expected-sources", type=Path, required=True)
    create_parser.add_argument("--expected-sources-sha256", required=True)
    create_parser.add_argument("--output", type=Path, required=True)
    create_parser.add_argument("--work-root", type=Path, required=True)
    create_parser.add_argument("--test-only", action="store_true")
    verify_parser = commands.add_parser("verify")
    verify_parser.add_argument("--index", type=Path, required=True)
    verify_parser.add_argument("--expected-index-sha256", required=True)
    admit_parser = commands.add_parser("admit")
    admit_parser.add_argument("--index", type=Path, required=True)
    admit_parser.add_argument("--expected-index-sha256", required=True)
    admit_parser.add_argument("--expected-sources", type=Path, required=True)
    admit_parser.add_argument("--expected-sources-sha256", required=True)
    admit_parser.add_argument("--site-work", type=Path)
    admit_parser.add_argument("--site-work-sha256")
    admit_parser.add_argument("--collector-closure", type=Path)
    admit_parser.add_argument("--collector-closure-sha256")
    admit_parser.add_argument("--merge-receipt", type=Path)
    admit_parser.add_argument("--merge-receipt-sha256")
    args = parser.parse_args()
    try:
        if args.command == "create":
            if r.sha_file(args.expected_sources) != args.expected_sources_sha256:
                raise ValueError("expected source manifest differs from independent pin")
            sources = r.json_file(args.expected_sources)
            index = create(args.workspace, args.expected_content_sha256, sources,
                           args.output, args.work_root, args.test_only)
            print("COLLECTION_INDEX="+str(args.output.absolute()))
        elif args.command == "verify":
            index = read(args.index, args.expected_index_sha256)
            print("COLLECTION_VERIFIED="+index["scientific_identity_sha256"])
        else:
            proof = admission_closure(args.index, args.expected_index_sha256,
                args.expected_sources, args.expected_sources_sha256,
                work_path=args.site_work,
                expected_work_sha256=args.site_work_sha256,
                closure_path=args.collector_closure,
                expected_closure_sha256=args.collector_closure_sha256,
                merge_receipt_path=args.merge_receipt,
                expected_merge_receipt_sha256=args.merge_receipt_sha256)
            print(r.canonical(proof))
    except (OSError, ValueError, KeyError, TypeError) as error:
        print("ERROR: "+str(error), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
