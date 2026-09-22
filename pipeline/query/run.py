#!/usr/bin/env python3
"""Build and independently verify portable ROOT query workspaces."""

import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]


def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


reduce = load("query_support", "pipeline/query/support.py")
model = load("query_model", "pipeline/query/model.py")


publication = load("query_publication", "pipeline/query/publication.py")
publish_directory = publication.publish_directory
SPARSE_DIGEST_SCHEMA = "hadronization_query_sparse_content_v2"
LEGACY_SPARSE_DIGEST_SCHEMA = "hadronization_query_sparse_content_v1"


def payload_sha(value):
    return reduce.sha_bytes(reduce.canonical(value).encode("ascii"))


def configured_pdgs(analysis):
    registry = analysis["pair_query_registry"]
    values = set(registry["trigger_pdgs"])
    for pdgs in registry["associate_pdgs"].values():
        values.update(pdgs)
    return sorted(values)


def read_dictionary(path):
    payload = reduce.json_file(path)
    reduce.exact_keys(payload, {"schema", "body", "body_sha256", "census"},
                      "campaign PDG dictionary")
    if payload["schema"] != "hadronization_campaign_pdg_dictionary_v1":
        raise ValueError("campaign PDG dictionary schema differs")
    body = payload["body"]
    reduce.exact_keys(body, {"schema", "pdgs"}, "campaign PDG dictionary body")
    pdgs = body["pdgs"]
    if (body["schema"] != "hadronization_campaign_pdg_dictionary_body_v1" or
            not isinstance(pdgs, list) or not pdgs or
            any(type(pdg) is not int or pdg == 0 for pdg in pdgs) or
            pdgs != sorted(set(pdgs)) or payload["body_sha256"] != payload_sha(body) or
            not isinstance(payload["census"], list) or not payload["census"]):
        raise ValueError("campaign PDG dictionary body/digest/census differs")
    return payload


def require_dictionary_consensus(digests):
    if not digests or len(set(digests)) != 1:
        raise ValueError("query workspaces do not share one campaign PDG dictionary digest")
    return digests[0]


def scientific_binding(metadata):
    return {
        "schema": "hadronization_query_scientific_binding_v2",
        "analysis_sha256": metadata["analysis_sha256"],
        "layout_sha256": metadata["layout_sha256"],
        "dictionary_body_sha256": metadata["dictionary_body_sha256"],
        "input_root_sha256": metadata["input_root_sha256"],
        "input_receipt_sha256": metadata["input_receipt_sha256"],
        # The physical receipt pin authenticates the admitted file during build.
        # This canonical digest separately authenticates the complete embedded
        # receipt when a portable workspace is verified without that file.
        "input_receipt_canonical_sha256": payload_sha(metadata["input_receipt"]),
        "input_scientific_identity_sha256": metadata["input_receipt"]["scientific_identity_sha256"],
        "source_subset_digest": metadata["input_receipt"]["binding"]["source_subset_digest"],
    }


def execution_attestation(metadata):
    return {
        "schema": "hadronization_query_execution_attestation_v1",
        "admission_build": metadata["admission_build"],
        "query_build": metadata["query_build"],
    }


def require_phase_a_layout(layout):
    """Require the complete repository-owned Phase-A object/column contract."""
    canonical = reduce.json_file(ROOT / "config/query.json")
    if layout != canonical:
        raise ValueError("query layout differs from the complete canonical Phase-A layout")
    return canonical


def layout_spec(analysis, layout, binding, dictionary,
                content_sha="__QUERY_CONTENT_SHA256__",
                scientific_binding_sha="__QUERY_SCIENTIFIC_BINDING_SHA256__",
                execution_attestation_sha="__QUERY_EXECUTION_ATTESTATION_SHA256__",
                sparse_digest_schema=SPARSE_DIGEST_SCHEMA):
    require_phase_a_layout(layout)
    axes = {}
    def uniform(name, bins, low, high, inclusive=False):
        edges = [low + (high-low)*i/bins for i in range(bins+1)]
        edges[0], edges[-1] = low, high
        axes[name] = (inclusive, edges)
    tune_count = len(binding["tune_ordinals"])
    block_count = binding["block_assignment"]["count"]
    uniform("tune", tune_count, -0.5, tune_count-0.5)
    uniform("block", block_count, 0.5, block_count+0.5)
    for name in ("a15_eta4", "a15_eta1"):
        uniform(name, analysis["axes"]["activity"]["bins"], -0.5,
                analysis["axes"]["activity"]["bins"]-0.5)
    for name in ("pt", "trigger_pt", "associate_pt"):
        axes[name] = (True, analysis["axes"]["pt"]["edges"])
    for name in ("eta", "trigger_eta", "associate_eta", "phi", "dphi"):
        source = analysis["axes"]["eta" if name.endswith("eta") else name]
        uniform(name, source["bins"], source["low"], source["high"], name != "dphi")
    eta = analysis["axes"]["eta"]
    uniform("deta", 2*eta["bins"], eta["low"]-eta["high"], eta["high"]-eta["low"], True)
    uniform("sign", 3, -1.5, 1.5)
    uniform("origin", 5, 0.5, 5.5)
    uniform("category", 6, -0.5, 5.5)
    if sparse_digest_schema not in (SPARSE_DIGEST_SCHEMA, None):
        raise ValueError("query sparse digest schema differs")
    lines = ["hadronization_root_query_spec_v4" if sparse_digest_schema else
             "hadronization_root_query_spec_v3"]
    if analysis["version"] == "2.2.0":
        lines.append("ANALYSIS_VERSION\t2.2.0")
    lines += ["CONTENT_SHA256\t" + content_sha,
             "SCIENTIFIC_BINDING_SHA256\t" + scientific_binding_sha,
             "EXECUTION_ATTESTATION_SHA256\t" + execution_attestation_sha,
             "DICTIONARY_SHA256\t" + dictionary["body_sha256"]]
    if sparse_digest_schema:
        lines.append("SPARSE_DIGEST_SCHEMA\t" + sparse_digest_schema)
    model.validate_phase_a_profiles(analysis["profiles"], analysis["axes"]["pt"]["edges"])
    objects = {"trees": layout["trees"], "sparse": dict(layout["sparse"])}
    for index, profile in enumerate(analysis["profiles"]):
        lines.append("\t".join(["PROFILE", str(index), profile["id"]] + model.profile_tokens(profile)))
    if analysis["version"] == "2.2.0":
        lines.extend("TRIGGER\t{}".format(pdg) for pdg in analysis["pair_query_registry"]["trigger_pdgs"])
        for sector, name in ((4, "charm"), (5, "beauty")):
            lines.extend("ASSOCIATE\t{}\t{}".format(sector, pdg)
                         for pdg in analysis["pair_query_registry"]["associate_pdgs"][name])
    for key, token in (("trees", "TREE"), ("sparse", "SPARSE")):
        for name, fields in sorted(objects[key].items()):
            lines.append("\t".join([token, name] + fields))
    for name, (inclusive, edges) in sorted(axes.items()):
        lines.append("\t".join(["AXIS", name, "inclusive" if inclusive else "halfopen"] +
                               [repr(float(x)) for x in edges]))
    lines.extend("PDG\t{}".format(pdg) for pdg in dictionary["body"]["pdgs"])
    return "\n".join(lines + ["END", ""])


def query_source_identity():
    return {
        "source_sha256": reduce.sha_file(ROOT / "pipeline/query/query.cpp"),
        "selection_sha256": reduce.sha_file(ROOT / "pipeline/query/selection.hpp"),
        "row_schema_sha256": reduce.sha_file(ROOT / "pipeline/query/row_schema.hpp"),
        "sha256_header_sha256": reduce.sha_file(ROOT / "pipeline/generate/sha256.hpp"),
        "flags": ["-std=c++17", "-O2", "-Wall", "-Wextra", "-Wpedantic", "-Werror", "-ffp-contract=off"],
    }


def load_prepared_pack(pack):
    pack = pack.absolute()
    reduce.reject_symlink_components(pack, "prepared query build pack")
    pack = pack.resolve()
    if not pack.is_dir() or {p.name for p in pack.iterdir()} != {
            "query", "build-receipt.json", "manifest.json"}:
        raise ValueError("prepared query build pack exact fileset differs")
    binary, receipt_path = pack / "query", pack / "build-receipt.json"
    reduce.regular_file(binary, "prepared query executable")
    reduce.regular_file(receipt_path, "prepared query build receipt")
    manifest = reduce.json_file(pack / "manifest.json")
    reduce.exact_keys(manifest, {"schema", "build_id", "binary_bytes", "binary_sha256",
                                 "receipt_sha256", "environment"}, "prepared query manifest")
    receipt = reduce.json_file(receipt_path)
    reduce.exact_keys(receipt, {"schema", "build_id", "build_identity", "binary_sha256"},
                      "prepared query build receipt")
    if (manifest["schema"] != "hadronization_prepared_query_pack_v1" or
            receipt["schema"] != "hadronization_query_build_receipt_v1" or
            manifest["build_id"] != receipt["build_id"] or
            manifest["binary_bytes"] != binary.stat().st_size or
            manifest["binary_sha256"] != reduce.sha_file(binary) or
            receipt["binary_sha256"] != manifest["binary_sha256"] or
            manifest["receipt_sha256"] != reduce.sha_file(receipt_path)):
        raise ValueError("prepared query executable/build receipt identity differs")
    identity = receipt["build_identity"]
    expected = query_source_identity()
    if any(identity.get(key) != value for key, value in expected.items()):
        raise ValueError("prepared query pack source/flags differ from checkout")
    environment = os.environ.copy()
    if (not isinstance(manifest["environment"], dict) or
            any(not isinstance(k, str) or not isinstance(v, str)
                for k, v in manifest["environment"].items())):
        raise ValueError("prepared query runtime environment differs")
    environment.update(manifest["environment"])
    return environment, binary, receipt


def build_tool(work, prepared_pack=None):
    if prepared_pack is not None:
        return load_prepared_pack(prepared_pack)
    runtime = reduce.runtime_module().resolve(require_root=True)
    environment = os.environ.copy()
    environment.update(runtime["environment"])
    source = ROOT / "pipeline/query/query.cpp"
    identity = {
        "schema": "hadronization_query_build_v1",
        **query_source_identity(),
        "compiler": runtime["environment"]["CXX"],
        "runtime": runtime["diagnostics"],
    }
    build_id = reduce.sha_bytes(reduce.canonical(identity).encode("ascii"))
    reduce.reject_symlink_components(work, "query work root")
    binary_root = work / "bin"
    binary_root.mkdir(parents=True, exist_ok=True)
    binary = binary_root / ("query-" + build_id[:20])
    receipt_path = binary.with_suffix(".build.json")
    with reduce.build_lock(binary.with_suffix(".build.lock")):
        current = reduce.cached_build(binary, receipt_path, identity)
        if current is not None:
            return environment, binary, current
        descriptor, name = tempfile.mkstemp(prefix=".query-", dir=str(binary_root))
        os.close(descriptor)
        temporary = Path(name)
        try:
            flags = reduce.command_tokens(environment["ROOT_CONFIG"], "--cflags", environment)
            libraries = reduce.command_tokens(environment["ROOT_CONFIG"], "--libs", environment)
            command = [environment["CXX"]] + identity["flags"] + [str(source)] + flags + libraries + ["-o", str(temporary)]
            result = subprocess.run(command, env=environment, text=True, capture_output=True)
            if result.returncode or result.stdout or result.stderr:
                raise ValueError("query warning-clean build failed: " + result.stdout + result.stderr)
            os.replace(str(temporary), str(binary))
        finally:
            if temporary.exists():
                temporary.unlink()
        receipt = {"schema": "hadronization_query_build_receipt_v1", "build_id": build_id,
                   "build_identity": identity, "binary_sha256": reduce.sha_file(binary)}
        reduce.atomic_json(receipt_path, receipt, exclusive=False)
        return environment, binary, receipt


def execute(binary, arguments, environment):
    result = subprocess.run([str(binary)] + [str(x) for x in arguments],
                            env=environment, capture_output=True, text=True)
    if result.returncode or result.stderr:
        raise ValueError("query operation failed: " + result.stdout + result.stderr)
    return result.stdout


def admit_input(source, receipt_path, work, accepted_pin=None, prepared=False):
    source, receipt_path = source.resolve(), receipt_path.resolve()
    reduce.regular_file(source, "accepted analyzed ROOT")
    reduce.regular_file(receipt_path, "accepted analyzed receipt")
    if accepted_pin is not None:
        reduce.lower_sha(accepted_pin, "accepted analyzed receipt pin")
        if reduce.sha_file(receipt_path) != accepted_pin:
            raise ValueError("analyzed receipt differs from independently accepted pin")
        receipt = reduce.json_file(receipt_path)
        validate_parent(receipt)
        storage = receipt["storage_identity"]
        if (source.stat().st_size != storage["root_bytes"] or
                reduce.sha_file(source) != storage["root_sha256"]):
            raise ValueError("accepted analyzed ROOT physical identity differs")
        admission = {"schema": "hadronization_pinned_analyzed_admission_v1",
                     "receipt_sha256": accepted_pin,
                     "root_sha256": storage["root_sha256"],
                     "root_bytes": storage["root_bytes"]}
        return receipt, admission, {"root_sha256": storage["root_sha256"],
                                    "root_bytes": storage["root_bytes"],
                                    "receipt_sha256": accepted_pin}
    if prepared:
        raise ValueError("prepared-pack mode requires an independently accepted receipt SHA256")
    analyzer_module = reduce.analyzer_module()
    analyzer, analyzer_environment, analyzer_build, _ = reduce.build_analyzer_admission(
        analyzer_module, work)
    receipt = analyzer_module.verify_receipt(receipt_path, source, analyzer=analyzer,
                                             environment=analyzer_environment)
    storage = receipt["storage_identity"]
    return receipt, analyzer_build, {"root_sha256": storage["root_sha256"],
                                    "root_bytes": storage["root_bytes"],
                                    "receipt_sha256": reduce.sha_file(receipt_path)}


def prepare_pack(args):
    output, work = args.output.absolute(), args.work_root.absolute()
    reduce.reject_symlink_components(output, "prepared query build pack output")
    reduce.reject_symlink_components(work, "query work root")
    if output.exists():
        raise ValueError("prepared query build pack output already exists")
    environment, binary, receipt = build_tool(work)
    output.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix="."+output.name+".staging-", dir=str(output.parent)))
    publication_started = False
    try:
        shutil.copy2(str(binary), str(staging / "query"))
        reduce.atomic_json(staging / "build-receipt.json", receipt, exclusive=True)
        kept_environment = {key: environment[key] for key in
                            ("PATH", "ROOTSYS", "LD_LIBRARY_PATH", "DYLD_LIBRARY_PATH",
                             "ROOT_DYN_PATH", "ROOT_INCLUDE_PATH", "PYTHONPATH")
                            if key in environment}
        reduce.atomic_json(staging / "manifest.json", {
            "schema": "hadronization_prepared_query_pack_v1",
            "build_id": receipt["build_id"],
            "binary_bytes": (staging / "query").stat().st_size,
            "binary_sha256": reduce.sha_file(staging / "query"),
            "receipt_sha256": reduce.sha_file(staging / "build-receipt.json"),
            "environment": kept_environment,
        }, exclusive=True)
        load_prepared_pack(staging)
        for artifact in staging.iterdir():
            reduce.fsync_file(artifact)
        reduce.fsync_directory(staging)
        publication_started = True
        publish_directory(staging, output)
        reduce.fsync_directory(output.parent)
        print("QUERY_PREPARED_PACK="+str(output)+" BUILD_ID="+receipt["build_id"])
    finally:
        if not publication_started and staging.exists():
            shutil.rmtree(str(staging))


def census(args):
    if len(args.input) != len(args.receipt):
        raise ValueError("census requires one receipt per input")
    pins = args.accepted_receipt_sha256 or []
    if pins and len(pins) != len(args.input):
        raise ValueError("census requires one accepted receipt SHA256 per input")
    if args.expected_source_count <= 0:
        raise ValueError("census expected source count must be positive")
    environment, binary, build_receipt = build_tool(args.work_root.absolute(), args.prepared_pack)
    analysis, analysis_sha = model.checked_analysis(args.analysis)
    model.validate_phase_a_profiles(analysis["profiles"], analysis["axes"]["pt"]["edges"])
    observed, records, sources, common = set(), [], [], None
    for index, (source, receipt_path) in enumerate(zip(args.input, args.receipt)):
        receipt, _, physical = admit_input(source, receipt_path, args.work_root.absolute(),
                                           pins[index] if pins else None,
                                           prepared=args.prepared_pack is not None)
        binding = receipt["binding"]
        identity = (binding["campaign"], binding["manifest_sha256"],
                    tuple(sorted(binding["tune_ordinals"].items())))
        if common is None:
            common = identity
        if identity != common:
            raise ValueError("census inputs do not share one campaign identity")
        sources.extend(binding["source_ids"])
        transcript = execute(binary, ["census", source.resolve()], environment)
        lines = transcript.splitlines()
        if not lines or lines[0] != "QUERY_CENSUS_V1" or lines[-1] != "CENSUS_COMPLETE":
            raise ValueError("query census transcript differs")
        values, pdgs = {}, []
        for line in lines[1:-1]:
            key, value = line.split("\t")
            if key == "PDG":
                pdgs.append(int(value))
            elif key in {"HEAVY_ROWS", "CLOSURE_ROWS"} and key not in values:
                values[key] = int(value)
            else:
                raise ValueError("unknown/duplicate query census record")
        if set(values) != {"HEAVY_ROWS", "CLOSURE_ROWS"} or pdgs != sorted(set(pdgs)):
            raise ValueError("query census counts/PDGs differ")
        if (values["HEAVY_ROWS"] != receipt["rows"]["heavy"] or
                values["CLOSURE_ROWS"] != receipt["rows"]["closure"]):
            raise ValueError("query census row counts differ from accepted receipt")
        observed.update(pdgs)
        records.append({"shard_ordinal": binding["shard_ordinal"],
                        "source_ids": binding["source_ids"],
                        "input_root_sha256": physical["root_sha256"],
                        "input_root_bytes": physical["root_bytes"],
                        "input_receipt_sha256": physical["receipt_sha256"],
                        "heavy_rows": values["HEAVY_ROWS"],
                        "closure_rows": values["CLOSURE_ROWS"],
                        "observed_pdgs": pdgs})
    if sources != list(range(args.expected_source_count)):
        raise ValueError("census source membership is not the exact expected campaign domain")
    configured = configured_pdgs(analysis)
    body = {"schema": "hadronization_campaign_pdg_dictionary_body_v1",
            "pdgs": sorted(observed | set(configured))}
    payload = {"schema": "hadronization_campaign_pdg_dictionary_v1",
               "body": body, "body_sha256": payload_sha(body),
               "census": [{"schema": "hadronization_campaign_pdg_census_v1",
                           "campaign": common[0], "manifest_sha256": common[1],
                           "analysis_sha256": analysis_sha,
                           "expected_source_count": args.expected_source_count,
                           "configured_pdgs": configured,
                           "query_build_id": build_receipt["build_id"],
                           "inputs": records}]}
    output = args.output.absolute()
    reduce.reject_symlink_components(output, "campaign PDG dictionary output")
    if output.exists():
        raise ValueError("campaign PDG dictionary output already exists")
    output.parent.mkdir(parents=True, exist_ok=True)
    reduce.atomic_json(output, payload, exclusive=True)
    read_dictionary(output)
    print("QUERY_CENSUS_DICTIONARY="+str(output)+" PDGS="+str(len(body["pdgs"]))+
          " BODY_SHA256="+payload["body_sha256"])


def validate_parent(receipt):
    """Check the portable admitted receipt without pretending to reopen its parent ROOT."""
    analyzer = reduce.analyzer_module()
    reduce.exact_keys(receipt, {"schema", "state", "campaign", "plan_digest", "map_digest",
        "shard_ordinal", "binding", "sources", "rows", "scientific_identity",
        "scientific_identity_sha256", "storage_identity", "storage_identity_sha256",
        "producer_provenance", "producer_provenance_sha256"}, "query admitted receipt")
    if receipt["schema"] != analyzer.RECEIPT_SCHEMA or receipt["state"] != "PASS":
        raise ValueError("query parent receipt is not admitted")
    for key in ("scientific_identity", "storage_identity", "producer_provenance"):
        if receipt[key+"_sha256"] != reduce.sha_bytes(reduce.canonical(receipt[key]).encode("ascii")):
            raise ValueError("query parent nested identity digest differs")
    scientific, storage, binding = (receipt[key] for key in
                                    ("scientific_identity", "storage_identity", "binding"))
    if (scientific["schema_digest"] != analyzer.SCHEMA_DIGEST or
            scientific["raw_mapping_digest"] != analyzer.RAW_MAPPING_DIGEST or
            scientific["structural_registries_digest"] != analyzer.REGISTRIES_DIGEST or
            scientific["lossless_dependency_identity_sha256"] != reduce.sha_bytes(
                reduce.canonical(scientific["lossless_dependency_identity"]).encode("ascii"))):
        raise ValueError("query parent lossless contract differs")
    sources = receipt["sources"]
    if not isinstance(sources, list) or not sources:
        raise ValueError("query parent source list is empty")
    for source in sources:
        reduce.exact_keys(source, {"source_id", "estimated_output_bytes", "manifest_row"},
                          "query parent source")
        reduce.exact_keys(source["manifest_row"], analyzer.MANIFEST_FIELDS, "query parent manifest row")
    source_ids = [source["source_id"] for source in sources]
    rows = [source["manifest_row"] for source in sources]
    subset_sha = reduce.sha_bytes(reduce.canonical(rows).encode("ascii"))
    if (source_ids != sorted(set(source_ids)) or storage["source_ids"] != source_ids or
            binding["source_ids"] != source_ids or
            binding["source_subset_digest"] != subset_sha or
            scientific["source_subset_digest"] != subset_sha):
        raise ValueError("query parent source subset identity differs")
    for key in ("campaign", "plan_digest", "map_digest", "shard_ordinal"):
        if receipt[key] != binding[key]:
            raise ValueError("query parent duplicated binding differs")
    for key in ("map_digest", "shard_ordinal", "target_bytes"):
        if storage[key] != binding[key]:
            raise ValueError("query parent storage binding differs")
    if binding["lossless_dependency_identity_sha256"] != scientific["lossless_dependency_identity_sha256"]:
        raise ValueError("query parent dependency binding differs")
    assignment = binding["block_assignment"]
    count = assignment["count"]
    tunes = binding["tune_ordinals"]
    if (type(count) is not int or count <= 0 or
            assignment["logical_id_rule"] != "block=(logical_id%{})+1".format(count) or
            not isinstance(tunes, dict) or not tunes or
            sorted(tunes.values()) != list(range(len(tunes)))):
        raise ValueError("query parent statistical/tune topology differs")
    for row in rows:
        if (type(row["logical_id"]) is not int or row["logical_id"] < 0 or
                row["tune"] not in tunes or row["block"] != row["logical_id"] % count + 1 or
                type(row["successful_events"]) is not int or row["successful_events"] <= 0):
            raise ValueError("query parent manifest topology differs")
    if (set(receipt["rows"]) != set(analyzer.TABLES) or
            any(type(n) is not int or n < 0 for n in receipt["rows"].values()) or
            receipt["rows"]["events"] != sum(row["successful_events"] for row in rows) or
            receipt["rows"]["sources"] != len(rows)):
        raise ValueError("query parent row accounting differs")


def verify(workspace, work, expected_content_sha256, prepared_pack=None):
    # The trust anchor is supplied by the caller's accepted build/source ledger,
    # never taken from the potentially replaced workspace we are admitting.
    reduce.lower_sha(expected_content_sha256, "trusted expected query content")
    reduce.reject_symlink_components(workspace, "query workspace")
    manifest = reduce.json_file(workspace / "manifest.json")
    manifest_fields = {"schema", "state", "artifacts", "source_rows",
                       "input_root_sha256", "elapsed_seconds", "scientific_content_sha256"}
    if manifest.get("schema") == "hadronization_query_workspace_v3":
        manifest_fields.add("sparse_digest_schema")
    reduce.exact_keys(manifest, manifest_fields, "query manifest")
    if manifest["schema"] not in {"hadronization_query_workspace_v2",
                                  "hadronization_query_workspace_v3"}:
        raise ValueError("query manifest schema differs")
    if manifest["scientific_content_sha256"] != expected_content_sha256:
        raise ValueError("query scientific content differs from trusted expected identity")
    required = {"query.root", "query.tsv", "analysis.json", "layout.json", "dictionary.json", "metadata.json"}
    names = [item["path"] for item in manifest["artifacts"]]
    if len(names) != len(set(names)) or set(names) != required:
        raise ValueError("query manifest artifact role set differs")
    expected = {"manifest.json"} | required
    if {p.name for p in workspace.iterdir()} != expected:
        raise ValueError("query exact output set differs")
    for item in manifest["artifacts"]:
        reduce.exact_keys(item, {"path", "bytes", "sha256"}, "query artifact")
        if Path(item["path"]).name != item["path"]:
            raise ValueError("query artifact path is not a direct child")
        path = workspace / item["path"]
        reduce.regular_file(path, "query artifact")
        if path.stat().st_size != item["bytes"] or reduce.sha_file(path) != item["sha256"]:
            raise ValueError("query artifact identity differs")
    analysis, archived_analysis_sha = model.checked_analysis(workspace / "analysis.json")
    layout = reduce.json_file(workspace / "layout.json")
    require_phase_a_layout(layout)
    dictionary = read_dictionary(workspace / "dictionary.json")
    metadata = reduce.json_file(workspace / "metadata.json")
    metadata_fields = {"schema", "state", "query_content_digests",
                                 "query_content_sha256", "analysis_sha256", "layout_sha256",
                                 "dictionary_sha256", "dictionary_body_sha256",
                                 "input_root_sha256", "input_receipt_sha256", "input_receipt",
                                 "admission_build", "query_build", "scientific_binding",
                                 "scientific_binding_sha256", "execution_attestation",
                                 "execution_attestation_sha256", "source_topology", "admission",
                                 "exactness"}
    if metadata.get("schema") == "hadronization_query_metadata_v4":
        metadata_fields.add("sparse_digest_schema")
    if analysis["version"] == "2.2.0" or "pair_population_proof" in metadata:
        metadata_fields.add("pair_population_proof")
    reduce.exact_keys(metadata, metadata_fields, "query metadata")
    parent = metadata["input_receipt"]
    validate_parent(parent)
    legacy = metadata["schema"] == "hadronization_query_metadata_v3"
    current = metadata["schema"] == "hadronization_query_metadata_v4"
    digest_schema = (LEGACY_SPARSE_DIGEST_SCHEMA if legacy else
                     metadata.get("sparse_digest_schema"))
    if ((not legacy and not current) or
            (legacy and manifest["schema"] != "hadronization_query_workspace_v2") or
            (current and (manifest["schema"] != "hadronization_query_workspace_v3" or
                          digest_schema != SPARSE_DIGEST_SCHEMA or
                          manifest.get("sparse_digest_schema") != digest_schema)) or
            metadata["state"] != "NONPUBLICATION_PARTIAL" or manifest["state"] != metadata["state"]):
        raise ValueError("query workspace state/schema differs")
    if (metadata["input_root_sha256"] != manifest["input_root_sha256"] or
            metadata["input_root_sha256"] != parent["storage_identity"]["root_sha256"] or
            manifest["source_rows"] != parent["rows"]):
        raise ValueError("query parent source identity/counts differ")
    proof = metadata.get("pair_population_proof")
    if proof is not None:
        reduce.exact_keys(proof, {"schema", "state", "scientific_binding_sha256", "events",
                                  "eligible_triggers", "zero_partner_triggers", "candidate_pairs",
                                  "stored_pairs", "by_tune_sector_sign"}, "pair population proof")
    if analysis["version"] == "2.2.0" and (proof is None or
            proof["schema"] != "hadronization_pair_population_proof_v1" or
            proof["state"] != "PASS" or
            proof["scientific_binding_sha256"] != metadata["scientific_binding_sha256"] or
            proof["events"] != sum(row["manifest_row"]["successful_events"] for row in parent["sources"]) or
            proof["candidate_pairs"] != proof["stored_pairs"] or
            any(type(proof[key]) is not int or proof[key] < 0 for key in
                ("events", "eligible_triggers", "zero_partner_triggers", "candidate_pairs", "stored_pairs"))):
        raise ValueError("query pair population proof binding/counts differ")
    if (metadata.get("source_topology") != "shard_local_rows_with_admitted_global_binding" or
            metadata["analysis_sha256"] != archived_analysis_sha or
            metadata["layout_sha256"] != reduce.sha_file(workspace / "layout.json") or
            metadata["dictionary_sha256"] != reduce.sha_file(workspace / "dictionary.json") or
            metadata["dictionary_body_sha256"] != dictionary["body_sha256"]):
        raise ValueError("query archived configuration identity differs")
    topology = parent["binding"]
    content_sha = reduce.sha_bytes(reduce.canonical(metadata["query_content_digests"]).encode("ascii"))
    binding = scientific_binding(metadata)
    attestation = execution_attestation(metadata)
    if (content_sha != metadata["query_content_sha256"] or
            content_sha != manifest["scientific_content_sha256"] or
            metadata["scientific_binding"] != binding or
            metadata["scientific_binding_sha256"] != payload_sha(binding) or
            metadata["execution_attestation"] != attestation or
            metadata["execution_attestation_sha256"] != payload_sha(attestation) or
            metadata["query_content_digests"].get("scientific_binding") != payload_sha(binding) or
            metadata["query_content_digests"].get("dictionary") != dictionary["body_sha256"]):
        raise ValueError("query independent scientific content binding differs")
    if (workspace / "query.tsv").read_text() != layout_spec(
            analysis, layout, topology, dictionary, content_sha,
            metadata["scientific_binding_sha256"], metadata["execution_attestation_sha256"],
            None if legacy else digest_schema):
        raise ValueError("query serialized scientific/axis config differs")
    environment, binary, build_receipt = build_tool(work, prepared_pack)
    if prepared_pack is not None and metadata["query_build"] != build_receipt:
        raise ValueError("query execution attestation differs from explicit prepared build receipt")
    output = execute(binary, ["verify", workspace / "query.tsv", workspace / "query.root"], environment)
    if "QUERY_VERIFIED\n" not in output:
        raise ValueError("query verifier completion is absent")
    proof_lines = [line.split("\t", 1)[1] for line in output.splitlines()
                   if line.startswith("PAIR_POPULATION_PROOF\t")]
    if analysis["version"] == "2.2.0" and (len(proof_lines) != 1 or json.loads(proof_lines[0]) != proof):
        raise ValueError("query pair population proof was not independently recomputed")
    if "SCIENTIFIC_CONTENT_SHA256\t" + content_sha + "\n" not in output:
        raise ValueError("query recomputed scientific content identity differs")
    canonical_lines = [line.split("\t", 1)[1] for line in output.splitlines()
                       if line.startswith("CANONICAL_SCIENTIFIC_CONTENT_SHA256\t")]
    if (len(canonical_lines) != 1 or
            (current and canonical_lines[0] != content_sha)):
        raise ValueError("query canonical scientific content identity differs")
    reduce.lower_sha(canonical_lines[0], "canonical query scientific content")
    if "METADATA_SHA256\t" + reduce.sha_file(workspace / "metadata.json") + "\n" not in output:
        raise ValueError("query embedded/external metadata identity differs")
    for name in layout["trees"]:
        if "TREE\t{}\t{}\n".format(name, manifest["source_rows"][name]) not in output:
            raise ValueError("query retained row count differs from admitted parent")
    return manifest, output


def prepare_query_attempt_root(output, work):
    """Create confined private staging outside accepted collection membership."""
    reduce.reject_symlink_components(output, "query output")
    reduce.reject_symlink_components(work, "query work root")
    work.mkdir(parents=True, exist_ok=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    reduce.reject_symlink_components(output, "query output")
    reduce.reject_symlink_components(work, "query work root")
    if not work.is_dir() or not output.parent.is_dir():
        raise ValueError("query work/output parent is not a directory")
    if output.exists():
        raise ValueError("query output already exists; use verify, never overwrite")
    attempts = reduce.safe_child(work, work / "attempts", "query attempt area")
    attempts.mkdir(exist_ok=True)
    attempts = reduce.safe_child(work, attempts, "query attempt area", must_exist=True)
    if not same_filesystem(attempts, output.parent):
        raise ValueError("query attempt area and output parent are on different filesystems")
    return attempts


def same_filesystem(first, second):
    return first.stat().st_dev == second.stat().st_dev


def create_query_stage(output, work):
    attempts = prepare_query_attempt_root(output, work)
    staging = Path(tempfile.mkdtemp(prefix="." + output.name + ".staging-", dir=str(attempts)))
    return reduce.safe_child(attempts, staging, "query private stage", must_exist=True)


def preserve_query_failure(staging, output, error):
    """Best-effort bounded evidence; never removes or replaces an earlier stage."""
    if not staging.is_dir() or staging.is_symlink():
        return  # A completed-but-unacknowledged rename must not recreate a stage.
    record = {
        "schema": "hadronization_query_failed_stage_v1",
        "state": "PRESERVED_FAILED_ATTEMPT",
        "output": str(output),
        "error_type": type(error).__name__,
        "error": str(error)[:4096],
        "recorded_unix": time.time(),
    }
    try:
        reduce.atomic_json(staging / "failure.json", record, exclusive=True)
        reduce.fsync_file(staging / "failure.json")
        reduce.fsync_directory(staging)
    except (OSError, ValueError):
        pass


def build(args):
    source, receipt_path = args.input.resolve(), args.receipt.resolve()
    output, work = args.output.absolute(), args.work_root.absolute()
    attempts = prepare_query_attempt_root(output, work)
    analysis, analysis_sha = model.checked_analysis(args.analysis)
    model.validate_phase_a_profiles(analysis["profiles"], analysis["axes"]["pt"]["edges"])
    layout = reduce.json_file(args.layout)
    require_phase_a_layout(layout)
    dictionary = read_dictionary(args.dictionary)
    if not set(configured_pdgs(analysis)).issubset(dictionary["body"]["pdgs"]):
        raise ValueError("campaign PDG dictionary omits configured identities")
    if output.exists():
        raise ValueError("query output already exists; use verify, never overwrite")
    started = time.monotonic()
    accepted_pin = getattr(args, "accepted_receipt_sha256", None)
    receipt, analyzer_build, physical = admit_input(source, receipt_path, work, accepted_pin,
                                                    prepared=args.prepared_pack is not None)
    environment, binary, build_receipt = build_tool(work, args.prepared_pack)
    metadata = {
        "schema": "hadronization_query_metadata_v4", "state": "NONPUBLICATION_PARTIAL",
        "sparse_digest_schema": SPARSE_DIGEST_SCHEMA,
        "query_content_digests": "__QUERY_CONTENT_DIGESTS__",
        "query_content_sha256": "__QUERY_CONTENT_SHA256__",
        "pair_population_proof": "__PAIR_POPULATION_PROOF__",
        "analysis_sha256": analysis_sha, "layout_sha256": reduce.sha_file(args.layout),
        "dictionary_sha256": reduce.sha_file(args.dictionary),
        "dictionary_body_sha256": dictionary["body_sha256"],
        "input_root_sha256": physical["root_sha256"],
        "input_receipt_sha256": physical["receipt_sha256"],
        "input_receipt": receipt, "admission_build": analyzer_build, "query_build": build_receipt,
        "scientific_binding": "__QUERY_SCIENTIFIC_BINDING__",
        "scientific_binding_sha256": "__QUERY_SCIENTIFIC_BINDING_SHA256__",
        "execution_attestation": "__QUERY_EXECUTION_ATTESTATION__",
        "execution_attestation_sha256": "__QUERY_EXECUTION_ATTESTATION_SHA256__",
        "source_topology": "shard_local_rows_with_admitted_global_binding",
        "admission": {"mode": "PINNED_ACCEPTED_ROOT" if accepted_pin else "CURRENT_SEMANTIC_RECHECK",
                      "accepted_receipt_sha256": accepted_pin},
        "exactness": "exact binary64 rows; optional independent-minima rectangles require aligned sparse edges",
    }
    metadata["scientific_binding"] = scientific_binding(metadata)
    metadata["scientific_binding_sha256"] = payload_sha(metadata["scientific_binding"])
    metadata["execution_attestation"] = execution_attestation(metadata)
    metadata["execution_attestation_sha256"] = payload_sha(metadata["execution_attestation"])
    spec = layout_spec(analysis, layout, receipt["binding"], dictionary,
                       scientific_binding_sha=metadata["scientific_binding_sha256"],
                       execution_attestation_sha=metadata["execution_attestation_sha256"])
    # Lock the destination name and commit the complete directory with manifest last.
    with reduce.build_lock(work / ("publish-" + reduce.sha_bytes(str(output).encode()) + ".lock")):
        if output.exists():
            raise ValueError("query output already exists")
        staging = Path(tempfile.mkdtemp(prefix="." + output.name + ".staging-", dir=str(attempts)))
        staging = reduce.safe_child(attempts, staging, "query private stage", must_exist=True)
        try:
            (staging / "query.tsv").write_text(spec, encoding="ascii")
            shutil.copyfile(str(args.analysis), str(staging / "analysis.json"))
            shutil.copyfile(str(args.layout), str(staging / "layout.json"))
            shutil.copyfile(str(args.dictionary), str(staging / "dictionary.json"))
            reduce.atomic_json(staging / "metadata.json", metadata, exclusive=True)
            transcript = execute(binary, ["build", staging / "query.tsv", source,
                                          staging / "query.root", staging / "metadata.json"], environment)
            completed_metadata = reduce.json_file(staging / "metadata.json")
            if (reduce.sha_file(source) != metadata["input_root_sha256"] or
                    reduce.sha_file(receipt_path) != metadata["input_receipt_sha256"]):
                raise ValueError("query input changed during projection")
            for artifact in staging.iterdir():
                reduce.fsync_file(artifact)
            artifacts = [{"path": p.name, "bytes": p.stat().st_size, "sha256": reduce.sha_file(p)}
                         for p in sorted(staging.iterdir())]
            manifest = {"schema": "hadronization_query_workspace_v3", "state": "NONPUBLICATION_PARTIAL",
                        "sparse_digest_schema": SPARSE_DIGEST_SCHEMA,
                        "artifacts": artifacts, "source_rows": receipt["rows"],
                        "input_root_sha256": metadata["input_root_sha256"],
                        "scientific_content_sha256": completed_metadata["query_content_sha256"],
                        "elapsed_seconds": time.monotonic()-started}
            reduce.atomic_json(staging / "manifest.json", manifest, exclusive=True)
            verify(staging, work, completed_metadata["query_content_sha256"], args.prepared_pack)
            reduce.fsync_directory(staging)
            publish_directory(staging, output)
            reduce.fsync_directory(output.parent)
            print(transcript, end="")
            print("QUERY_WORKSPACE=" + str(output))
        except BaseException as error:
            preserve_query_failure(staging, output, error)
            raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prepared = commands.add_parser("prepare-pack", help="build one immutable executable/receipt pack for later workers")
    prepared.add_argument("--output", required=True, type=Path)
    census_parser = commands.add_parser("census", help="freeze one campaign-wide signed-PDG dictionary without constructing query files")
    census_parser.add_argument("--input", required=True, action="append", type=Path)
    census_parser.add_argument("--receipt", required=True, action="append", type=Path)
    census_parser.add_argument("--accepted-receipt-sha256", action="append")
    census_parser.add_argument("--expected-source-count", required=True, type=int)
    census_parser.add_argument("--analysis", type=Path, default=ROOT / "config/analysis.json")
    census_parser.add_argument("--output", required=True, type=Path)
    create = commands.add_parser("build", help="derive a verified exact-row and sparse workspace from one admitted shard")
    create.add_argument("--input", required=True, type=Path)
    create.add_argument("--receipt", required=True, type=Path)
    create.add_argument("--output", required=True, type=Path)
    create.add_argument("--analysis", type=Path, default=ROOT / "config/analysis.json")
    create.add_argument("--layout", type=Path, default=ROOT / "config/query.json")
    create.add_argument("--dictionary", required=True, type=Path,
                        help="campaign-wide census dictionary used unchanged by every shard")
    create.add_argument("--accepted-receipt-sha256",
                        help="independently trusted prior PASS receipt; still checks complete ROOT hash and bindings")
    check = commands.add_parser("verify", help="rederive every sparse cell and Sumw2 from exact rows")
    check.add_argument("--workspace", type=Path, required=True)
    check.add_argument("--expected-content-sha256", required=True,
                       help="trusted content digest from the accepted producer/source ledger")
    scan = commands.add_parser("scan", help="emit exact pair natural keys passing a named pT profile")
    scan.add_argument("--workspace", type=Path, required=True)
    scan.add_argument("--expected-content-sha256", required=True)
    scan.add_argument("--profile", required=True)
    # Projection is provided by the statistics layer.
    projection = None
    for command in (create, check, scan, census_parser):
        command.add_argument("--prepared-pack", type=Path,
                             help="explicit executable/build receipt pack; absence or mismatch refuses and never rebuilds")
    for command in (prepared, create, check, scan, census_parser):
        command.add_argument("--work-root", type=Path, required=True, help="external reproducible build/cache directory")
    args = parser.parse_args()
    try:
        if args.command == "prepare-pack":
            prepare_pack(args)
        elif args.command == "census":
            census(args)
        elif args.command == "build":
            build(args)
        else:
            _, output = verify(args.workspace, args.work_root, args.expected_content_sha256,
                               args.prepared_pack)
            if args.command == "verify":
                print(output, end="")
            else:
                profiles = reduce.json_file(args.workspace / "analysis.json")["profiles"]
                selected = [p for p in profiles if p["id"] == args.profile]
                if len(selected) != 1:
                    raise ValueError("unknown query profile")
                archived_analysis = reduce.json_file(args.workspace / "analysis.json")
                model.phase_a_profile_kind(selected[0])
                model.projection_contract(selected[0], "exact_rows",
                                          archived_analysis["axes"]["pt"]["edges"])
                environment, binary, _ = build_tool(args.work_root, args.prepared_pack)
                print(execute(binary, ["scan", args.workspace / "query.root"] +
                              model.profile_tokens(selected[0]), environment), end="")
        return 0
    except OSError as error:
        print("ERROR: " + str(error), file=sys.stderr)
        return 75 if error.errno in reduce.TRANSIENT_ERRNOS else 2
    except (ValueError, KeyError, RuntimeError, subprocess.CalledProcessError) as error:
        print("ERROR: " + str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
