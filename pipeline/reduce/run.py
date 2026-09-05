#!/usr/bin/env python3
"""Admit a complete lossless shard plan and build/verify its compact plot source."""

import argparse
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import platform
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time


ROOT = Path(__file__).resolve().parents[2]
ANALYSIS = ROOT / "config/analysis.json"
REDUCTION_SCHEMA = "hadronization_compact_plot_source_v1"
RECEIPT_SCHEMA = "hadronization_reduction_receipt_v1"
SPEC_SCHEMA = "hadronization_reduction_spec_v1"
ANALYZER_TABLES = (
    "ancestry", "ancestry_mothers", "closure", "constituents",
    "event_compatibility", "event_ranges", "events", "hard", "heavy",
    "heavy_mothers", "origins", "pairs", "source_blocks", "source_counts",
    "sources", "triggers",
)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True)


def sha_bytes(value):
    return hashlib.sha256(value).hexdigest()


def sha_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def exact_keys(value, expected, label):
    if not isinstance(value, dict) or set(value) != set(expected):
        raise ValueError("{} field set differs".format(label))


def regular_file(path, label):
    if path.is_symlink() or not path.is_file():
        raise ValueError("{} is not a regular file: {}".format(label, path))


def json_file(path):
    regular_file(path, "JSON input")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise ValueError("invalid JSON {}: {}".format(path, error)) from error


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def analyzer_module():
    return load_module("hadronization_analyzer_contract",
                       ROOT / "pipeline/analyze/run.py")


def runtime_module():
    return load_module("hadronization_runtime_contract",
                       ROOT / "pipeline/generate/runtime.py")


def reject_symlink_components(path, label):
    absolute = path.absolute()
    current = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        current /= part
        if os.path.lexists(str(current)) and current.is_symlink():
            raise ValueError("{} has a symlink component: {}".format(label, current))


def safe_child(parent, child, label, must_exist=False):
    reject_symlink_components(parent, label + " root")
    reject_symlink_components(child, label)
    parent = parent.resolve(strict=parent.exists())
    child = child.resolve(strict=must_exist)
    try:
        child.relative_to(parent)
    except ValueError as error:
        raise ValueError("{} is outside declared root".format(label)) from error
    return child


def fsync_file(path):
    descriptor = os.open(str(path), os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def fsync_directory(path):
    descriptor = os.open(str(path), os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def atomic_json(path, value, exclusive=True):
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = (canonical(value) + "\n").encode("ascii")
    with tempfile.NamedTemporaryFile(prefix="." + path.name + ".",
                                     dir=str(path.parent), delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    try:
        if exclusive:
            os.link(str(temporary), str(path))
            fsync_directory(path.parent)
        else:
            os.replace(str(temporary), str(path))
            fsync_directory(path.parent)
    finally:
        if temporary.exists():
            temporary.unlink()


def checked_analysis(path):
    path = path.resolve()
    regular_file(path, "analysis request")
    payload = json_file(path)
    expected = {
        "schema", "version", "base_study", "lossless_input", "axes",
        "profiles", "pair_acceptance", "activities", "percentile_intervals",
        "integrated_interval", "activity_policy", "pair_query_registry",
        "correlations", "projection_recipes", "g9_species_pdgs",
        "estimator_policy", "compact_domain_registries", "compact_storage",
    }
    exact_keys(payload, expected, "analysis request")
    if payload["schema"] != "hadronization_downstream_analysis_request_v1":
        raise ValueError("analysis request schema differs")
    if payload["version"] != "1.0.0":
        raise ValueError("analysis request version differs")
    if payload["lossless_input"] != {
            "schema": "hadronization_lossless_analysis_v1",
            "schema_digest": "3a83a7550c27c3f59989b84eea0204bce45bd9c401744f321758e56f3bf422c9",
            "structural_registries_digest":
                "5462be4f9fed821f6a0c09cda4b461343d1720112f8c76a3afd14ce8130895f3"}:
        raise ValueError("analysis lossless-input contract differs")
    if payload["base_study"] != {
            "schema": "hadronization_study_v1",
            "sha256": "d3eac08d732dd5d9642b650ac69cb3512bf3245ae450387e57ace7690a8ef4f5"}:
        raise ValueError("analysis request base-study binding differs")
    study = ROOT / "config/study.json"
    if sha_file(study) != payload["base_study"]["sha256"]:
        raise ValueError("accepted base-study bytes differ")
    profiles = payload["profiles"]
    if not isinstance(profiles, list) or not profiles or len(profiles) > 16:
        raise ValueError("analysis profile list is empty or exceeds its bounded domain")
    profile_ids = []
    for profile in profiles:
        exact_keys(profile, {"id", "trigger_pt", "associate_pt"},
                   "analysis profile")
        identifier = profile["id"]
        if (not isinstance(identifier, str) or
                re.fullmatch(r"[a-z][a-z0-9_]{0,63}", identifier) is None or
                identifier in profile_ids):
            raise ValueError("analysis profile IDs are malformed or duplicated")
        profile_ids.append(identifier)
        for role in ("trigger_pt", "associate_pt"):
            predicate = profile[role]
            if predicate is None:
                continue
            exact_keys(predicate, {"operator", "value"},
                       "analysis profile threshold")
            value = predicate["value"]
            if (predicate["operator"] != ">" or type(value) not in (int, float) or
                    not math.isfinite(value) or value < 0):
                raise ValueError("analysis profiles support only strict finite "
                                 "nonnegative pT thresholds")
    activities = payload["activities"]
    expected_activities = [
        {"id": "charged_light_sector_activity_a15_v1_eta4",
         "semantic_id": "charged_light_sector_activity_a15_v1",
         "physical_field": "a15_eta4", "eta_window": 4.0,
         "role": "nominal",
         "raw_definition_id": "primary_charged_light_hadron_level_v1",
         "predicate": "positive/final, nonzero charge, no charm/beauty "
                      "constituent, finite kinematics, pt>0.15, abs(eta)<=4"},
        {"id": "charged_light_sector_activity_a15_v1_eta1",
         "semantic_id": "charged_light_sector_activity_a15_v1",
         "physical_field": "a15_eta1", "eta_window": 1.0,
         "role": "parity",
         "raw_definition_id": "primary_charged_light_hadron_level_v1",
         "predicate": "positive/final, nonzero charge, no charm/beauty "
                      "constituent, finite kinematics, pt>0.15, abs(eta)<=1"},
    ]
    if activities != expected_activities:
        raise ValueError("analysis activity mapping differs")
    intervals = payload["percentile_intervals"]
    if (not isinstance(intervals, list) or not intervals or
            any(not isinstance(item, list) or len(item) != 2 or
                any(type(value) is not int for value in item) or
                not 0 <= item[0] < item[1] <= 100 for item in intervals) or
            any(intervals[index][1] != intervals[index + 1][0]
                for index in range(len(intervals) - 1)) or
            intervals[0][0] != 0 or intervals[-1][1] != 100):
        raise ValueError("analysis percentile intervals are not one ordered partition")
    if payload["integrated_interval"] != [0, 100]:
        raise ValueError("analysis integrated interval differs")
    axes = payload["axes"]
    exact_keys(axes, {"activity", "dphi", "eta", "phi", "pt"},
               "analysis axes")
    if (axes["activity"] != {
            "bins": 4096, "integer_domain": [0, 4095],
            "endpoint_rule": "each nonnegative integer is one regular bin"} or
            axes["dphi"] != {
            "bins": 100, "low": -1.5707963267948966,
            "high": 4.71238898038469,
            "endpoint_rule": "low inclusive, high exclusive",
            "semantic": "wrap(trigger_phi-associate_phi) in [-pi/2,3pi/2)"} or
            axes["eta"] != {
                "bins": 100, "low": -4.0, "high": 4.0,
                "endpoint_rule":
                    "both physical endpoints inclusive; high occupies last bin"} or
            axes["phi"] != {
                "bins": 100, "low": -3.141592653589793,
                "high": 3.141592653589793,
                "endpoint_rule":
                    "both physical endpoints inclusive; high occupies last bin"}):
        raise ValueError("analysis exact axis contract differs")
    exact_keys(axes["pt"], {"edges", "endpoint_rule"}, "analysis pT axis")
    pt_edges = axes["pt"]["edges"]
    if (not isinstance(pt_edges, list) or len(pt_edges) < 2 or
            any(type(value) not in (int, float) or not math.isfinite(value)
                for value in pt_edges) or
            any(float(pt_edges[index]) >= float(pt_edges[index + 1])
                for index in range(len(pt_edges) - 1)) or
            axes["pt"]["endpoint_rule"] !=
            "low inclusive, high inclusive; underflow and overflow retained"):
        raise ValueError("analysis pT axis differs")
    if payload["pair_acceptance"] != {
            "eta": {"operator": "abs<=", "value": 4.0},
            "roles": "ordered structural trigger and associate",
            "dphi_sign": "trigger_phi-associate_phi"}:
        raise ValueError("analysis pair acceptance differs")
    if payload["activity_policy"] != {
            "threshold": "first integer n whose ascending weighted cumulative "
                         "is >= (100-p)/100 of total",
            "tie_rule": "threshold belongs to the lower-activity class",
            "weight_convention": "signed event weight; every aggregate bin must "
                                 "be nonnegative and total positive",
            "complement_rule": "resolve every tune-local delete-one-block boundary; "
                               "instability or unresolved margin withholds "
                               "unconditional class uncertainty"}:
        raise ValueError("analysis activity policy differs")
    query = payload["pair_query_registry"]
    exact_keys(query, {"expansion", "trigger_pdgs", "associate_pdgs",
                       "reference_meson_by_trigger", "expected_count",
                       "central_eligibility_source"},
               "analysis pair-query registry")
    triggers = query["trigger_pdgs"]
    associates = query["associate_pdgs"]
    references = query["reference_meson_by_trigger"]
    if (query["expansion"] !=
            "ordered Cartesian product within sector in listed order" or
            not isinstance(triggers, list) or len(triggers) != 12 or
            any(type(value) is not int for value in triggers) or
            len(set(triggers)) != len(triggers) or
            not isinstance(associates, dict) or
            set(associates) != {"charm", "beauty"} or
            any(not isinstance(values, list) or not values or
                any(type(value) is not int for value in values) or
                len(set(values)) != len(values)
                for values in associates.values()) or
            not isinstance(references, dict) or
            set(references) != {str(value) for value in triggers} or
            any(type(value) is not int for value in references.values()) or
            query["expected_count"] != 300 or
            query["central_eligibility_source"] !=
            "lossless structural selected-state registry"):
        raise ValueError("analysis pair-query registry differs")
    correlations = payload["correlations"]
    exact_keys(correlations, {"tunes", "identities", "components",
                              "difference_recipe"}, "analysis correlations")
    identities = correlations["identities"]
    if (correlations["tunes"] != "all admitted tunes" or
            correlations["components"] != ["OS", "SS"] or
            correlations["difference_recipe"] != "OS-SS" or
            not isinstance(identities, list) or len(identities) != 4 or
            any(not isinstance(item, list) or len(item) != 2 or
                any(type(value) is not int for value in item)
                for item in identities) or
            len({tuple(item) for item in identities}) != len(identities)):
        raise ValueError("analysis correlation registry differs")
    expected_recipes = [
        "G1_activity_eta1_eta4",
        "G9_direct_primary_selected_strict_pt0p15_eta4",
        "T1_all_final_heavy_no_acceptance", "ordered_pair_scalars",
        "configured_dphi_correlations", "origin_integrated",
        "closure_full_visible_eta4_no_associate_pt_floor",
        "closure_species_integrated", "closure_category_dphi_integrated",
    ]
    if payload["projection_recipes"] != expected_recipes:
        raise ValueError("analysis projection recipes differ")
    if payload["g9_species_pdgs"] != [
            -5212, -5122, -4122, -521, -411, 411, 521, 4122, 5122, 5212]:
        raise ValueError("analysis G9 registry differs")
    policy = payload["estimator_policy"]
    exact_keys(policy, {"id", "release_block_count", "variance_dof",
                        "center", "covariance", "bias_correction",
                        "denominator_resolution_alpha",
                        "phase_a_t9_two_sided_quantile", "quantile_algorithm",
                        "cancelled_parent_rule", "class_boundary_statuses",
                        "display_label"}, "analysis estimator policy")
    if (policy.get("id") != "pooled_delete_one_source_block_jackknife_v2" or
            policy.get("release_block_count") != 10 or
            policy.get("variance_dof") != 9 or
            policy.get("denominator_resolution_alpha") != 0.05 or
            policy.get("phase_a_t9_two_sided_quantile") !=
            2.2621571628540993 or policy.get("bias_correction") is not False or
            policy.get("center") != "g(sum(block_vectors))" or
            policy.get("covariance") !=
            "(K-1)/K times sum outer(delete_one-leave_mean)" or
            policy.get("quantile_algorithm") !=
            "accepted STATISTICS-1 binary64 t9 constant; this release supports "
            "K=10 only" or
            policy.get("cancelled_parent_rule") !=
            "exact/numerical existence applies to every semantic denominator; "
            "statistical resolution and complement sign screens apply only to "
            "algebraically surviving denominators" or
            policy.get("class_boundary_statuses") !=
            ["CLASS_BOUNDARY_UNSTABLE", "CLASS_BOUNDARY_UNRESOLVED"] or
            not isinstance(policy.get("display_label"), str) or
            not policy["display_label"]):
        raise ValueError("analysis estimator policy differs")
    registries = payload["compact_domain_registries"]
    exact_keys(registries, {"projection_ids", "origin_ids",
                            "closure_category_ids",
                            "correlation_component_ids",
                            "closure_full_visible_component_ids",
                            "g9_axis_ids", "t1_component_ids",
                            "gram_component_kinds"},
               "analysis compact-domain registries")
    expected_registries = {
        "projection_ids": [
            {"id": 1, "name": "activity_hist", "scope_family": "activity"},
            {"id": 2, "name": "ordered_pair_scalar", "scope_family": "pair"},
            {"id": 3, "name": "trigger_scalar", "scope_family": "pair"},
            {"id": 4, "name": "dphi_correlation", "scope_family": "pair"},
            {"id": 5, "name": "origin", "scope_family": "integrated_profile"},
            {"id": 6, "name": "closure_category_dphi",
             "scope_family": "integrated_profile"},
            {"id": 7, "name": "closure_species",
             "scope_family": "integrated_profile"},
            {"id": 8, "name": "closure_full_visible",
             "scope_family": "integrated_profile"},
            {"id": 9, "name": "G9", "scope_family": "tune"},
            {"id": 10, "name": "T1", "scope_family": "tune"},
        ],
        "origin_ids": [
            {"id": 0, "label": "selected_hard_companion"},
            {"id": 1, "label": "shower"},
            {"id": 2, "label": "MPI"},
            {"id": 3, "label": "other_resolved"},
            {"id": 4, "label": "unresolved"},
        ],
        "closure_category_ids": [
            {"id": 0, "label": "selected_ground"},
            {"id": 1, "label": "excluded_vector"},
            {"id": 2, "label": "excluded_excited"},
            {"id": 3, "label": "multiply_heavy"},
        ],
        "correlation_component_ids": [
            {"id": 0, "label": "OS"}, {"id": 1, "label": "SS"}],
        "closure_full_visible_component_ids": [
            {"id": 0, "label": "full"},
            {"id": 1, "label": "visible"}],
        "g9_axis_ids": [
            {"id": 0, "label": "pt",
             "flow": "explicit underflow and overflow slots"},
            {"id": 1, "label": "eta",
             "flow": "no materialized flow slots"},
            {"id": 2, "label": "phi",
             "flow": "no materialized flow slots"},
        ],
        "t1_component_ids": [
            {"id": 0, "label": "hadron_count"},
            {"id": 1, "label": "charm_plus_anticharm_constituent_count"},
            {"id": 2, "label": "beauty_plus_antibeauty_constituent_count"},
        ],
        "gram_component_kinds": [
            {"id": 0, "label": "ordered_pair_count",
             "source": "pair_query_ids"},
            {"id": 1, "label": "trigger_denominator",
             "source": "trigger_ids"},
        ],
    }
    if registries != expected_registries:
        raise ValueError("analysis compact-domain registries differ")
    storage = payload["compact_storage"]
    exact_keys(storage, {"schema", "tables", "metadata_objects",
                         "compression", "maximum_complete_default_bytes",
                         "sparse_rule", "pooled_copy", "summation"},
               "analysis compact storage")
    if (storage.get("schema") != REDUCTION_SCHEMA or
            storage.get("tables") != ["cells", "event_gram"] or
            storage.get("metadata_objects") != ["metadata", "receipt"] or
            storage.get("compression") != {"algorithm": "ZSTD", "level": 5} or
            storage.get("maximum_complete_default_bytes") != 50 * 1024 * 1024 or
            storage.get("sparse_rule") !=
            "absence inside a declared domain is exact zero; absence outside is "
            "NOT_MATERIALIZED" or storage.get("pooled_copy") is not False or
            storage.get("summation") !=
            "Neumaier compensated binary64 with recorded absolute sums and "
            "operation counts"):
        raise ValueError("analysis compact-storage contract differs")
    return payload, sha_file(path)


def lower_sha(value, label):
    if (not isinstance(value, str) or len(value) != 64 or
            any(character not in "0123456789abcdef" for character in value)):
        raise ValueError("{} is not a lowercase SHA-256".format(label))


def admit_receipt(plan, shard, root_path, receipt_path, analyze):
    regular_file(root_path, "accepted analysis shard")
    receipt = json_file(receipt_path)
    exact_keys(receipt, {
        "schema", "state", "campaign", "plan_digest", "map_digest",
        "shard_ordinal", "binding", "sources", "rows", "scientific_identity",
        "scientific_identity_sha256", "storage_identity",
        "storage_identity_sha256", "producer_provenance",
        "producer_provenance_sha256"}, "accepted shard receipt")
    if receipt["schema"] != analyze.RECEIPT_SCHEMA or receipt["state"] != "PASS":
        raise ValueError("accepted shard receipt is not PASS")
    expected_sources = [plan["sources"][item] for item in shard["source_ids"]]
    dependency = receipt["scientific_identity"].get("lossless_dependency_identity")
    if not isinstance(dependency, dict):
        raise ValueError("accepted shard dependency identity is absent")
    campaign = analyze.json_file(Path(plan["campaign_descriptor"]))
    adapter = analyze.campaign_adapter(campaign)
    expected_dependency = analyze.lossless_dependency_identity(
        campaign, adapter, [item["manifest_row"] for item in expected_sources])
    if dependency != expected_dependency:
        raise ValueError("accepted shard dependency/commit marker differs")
    dependency_sha = sha_bytes(canonical(dependency).encode("ascii"))
    expected_binding = analyze.shard_binding(plan, shard, dependency_sha)
    if (receipt["binding"] != expected_binding or
            receipt["sources"] != expected_sources or
            receipt["campaign"] != plan["campaign"] or
            receipt["plan_digest"] != plan["plan_digest"] or
            receipt["map_digest"] != plan["map_digest"] or
            receipt["shard_ordinal"] != shard["ordinal"]):
        raise ValueError("accepted shard receipt/plan/source binding differs")
    storage = receipt["storage_identity"]
    exact_keys(storage, {"compression", "map_digest", "ordering", "root_bytes",
                         "root_sha256", "shard_ordinal", "source_ids",
                         "target_bytes"}, "accepted shard storage identity")
    if (receipt["storage_identity_sha256"] !=
            sha_bytes(canonical(storage).encode("ascii")) or
            storage["compression"] != {"algorithm": "ZSTD", "level": 5} or
            storage["ordering"] != "canonical_natural_key_v1" or
            storage["source_ids"] != shard["source_ids"] or
            storage["root_bytes"] != root_path.stat().st_size or
            storage["root_sha256"] != sha_file(root_path)):
        raise ValueError("accepted shard physical identity differs")
    scientific = receipt["scientific_identity"]
    exact_keys(scientific, {
        "lossless_dependency_identity", "lossless_dependency_identity_sha256",
        "raw_mapping_digest", "raw_schema", "schema_digest",
        "scientific_content_digest", "source_scientific_digests",
        "source_subset_digest", "structural_registries_digest"},
        "accepted shard scientific identity")
    if (receipt["scientific_identity_sha256"] !=
            sha_bytes(canonical(scientific).encode("ascii")) or
            scientific["lossless_dependency_identity_sha256"] != dependency_sha or
            scientific["schema_digest"] != plan["schema_digest"] or
            scientific["structural_registries_digest"] != plan["registries_digest"] or
            scientific["source_subset_digest"] != sha_bytes(canonical(
                [item["manifest_row"] for item in expected_sources]).encode("ascii")) or
            len(scientific["source_scientific_digests"]) != len(expected_sources)):
        raise ValueError("accepted shard scientific identity differs")
    lower_sha(scientific["scientific_content_digest"], "shard scientific digest")
    for value in scientific["source_scientific_digests"]:
        lower_sha(value, "source scientific digest")
    if (not isinstance(receipt["rows"], dict) or
            set(receipt["rows"]) != set(ANALYZER_TABLES) or
            any(type(value) is not int or value < 0
                for value in receipt["rows"].values())):
        raise ValueError("accepted shard row accounting differs")
    provenance = receipt["producer_provenance"]
    exact_keys(provenance, {"producer_identity", "publication"},
               "accepted shard producer provenance")
    if (receipt["producer_provenance_sha256"] !=
            sha_bytes(canonical(provenance).encode("ascii"))):
        raise ValueError("accepted shard producer provenance differs")
    producer = provenance["producer_identity"]
    exact_keys(producer, {"analyzer", "compiler", "raw_pre_sha256", "root",
                          "validator"}, "accepted shard producer identity")
    for role in ("analyzer", "validator"):
        exact_keys(producer[role], {"binary_sha256", "build_identity",
                                    "build_receipt_sha256", "source_sha256"},
                   "accepted shard {} identity".format(role))
        for key, value in producer[role].items():
            lower_sha(value, "accepted shard {} {}".format(role, key))
    expected_raw = {item["manifest_row"]["raw_storage_key"]:
                    item["manifest_row"]["raw_sha256"]
                    for item in expected_sources}
    if producer["raw_pre_sha256"] != expected_raw:
        raise ValueError("accepted shard producer raw-input identity differs")
    publication = provenance["publication"]
    exact_keys(publication, {"elapsed_seconds", "host", "mode"},
               "accepted shard publication provenance")
    if (type(publication["elapsed_seconds"]) not in (int, float) or
            not math.isfinite(publication["elapsed_seconds"]) or
            publication["elapsed_seconds"] < 0 or
            not isinstance(publication["host"], str) or not publication["host"] or
            publication["mode"] not in {"normal", "root_only_recovery"} or
            not isinstance(producer["compiler"], str) or not producer["compiler"] or
            not isinstance(producer["root"], str) or not producer["root"]):
        raise ValueError("accepted shard producer publication differs")
    return receipt


def exact_shard_set(plan, output_root, analyze):
    campaign_dir = safe_child(output_root, output_root / plan["campaign"],
                              "accepted shard directory", must_exist=True)
    expected = set()
    admitted = []
    for shard in plan["shards"]:
        root_path = campaign_dir / "shard-{:04d}.root".format(shard["ordinal"])
        receipt_path = campaign_dir / "shard-{:04d}.json".format(shard["ordinal"])
        expected.update((root_path.name, receipt_path.name))
        admitted.append((shard, root_path, receipt_path))
    observed = set()
    for path in campaign_dir.iterdir():
        if path.is_symlink() or not path.is_file():
            raise ValueError("unknown non-regular shard-set entry: {}".format(path))
        observed.add(path.name)
    if observed != expected:
        missing = sorted(expected - observed)
        foreign = sorted(observed - expected)
        raise ValueError("exact shard-set closure differs: missing={} foreign={}".format(
            missing, foreign))
    return admitted


def publication_state(plan, analyze, partial):
    campaign = analyze.json_file(Path(plan["campaign_descriptor"]))
    adapter = analyze.campaign_adapter(campaign)
    manifest = analyze.load_manifest(Path(plan["manifest"]), campaign, adapter)
    selected = [item["manifest_row"] for item in plan["sources"]]
    complete = selected == manifest
    if not complete and not partial:
        raise ValueError("plan is a subset of the complete campaign manifest; rerun with "
                         "--partial for NONPUBLICATION_PARTIAL output")
    if complete and partial:
        raise ValueError("--partial is false labeling for a complete campaign plan")
    return "PUBLICATION_ELIGIBLE" if complete else "NONPUBLICATION_PARTIAL"


def state_registry(analysis):
    study = json_file(ROOT / "config/study.json")
    states = study["selected_states"]
    by_pdg = {item["pdg"]: item for item in states}
    query = analysis["pair_query_registry"]
    pairs = []
    for trigger in query["trigger_pdgs"]:
        if trigger not in by_pdg or not by_pdg[trigger]["pair_analysis_eligible"]:
            raise ValueError("pair trigger registry is not structurally eligible")
        sector = by_pdg[trigger]["sector"]
        trigger_charge = (by_pdg[trigger]["qc"] if sector == "charm"
                          else by_pdg[trigger]["qb"])
        for associate in query["associate_pdgs"][sector]:
            state = by_pdg.get(associate)
            if state is None or state["sector"] != sector:
                raise ValueError("pair associate registry differs from structural states")
            associate_charge = state["qc"] if sector == "charm" else state["qb"]
            pairs.append({
                "id": len(pairs), "trigger_pdg": trigger,
                "associate_pdg": associate,
                "sign": -1 if trigger_charge * associate_charge < 0 else 1,
                "reference_meson_pdg": int(
                    query["reference_meson_by_trigger"][str(trigger)]),
                "central_eligible": bool(state["pair_analysis_eligible"]),
                "sector": sector,
            })
    if len(pairs) != query["expected_count"] or len(pairs) != 300:
        raise ValueError("expanded pair registry is not the required 300 queries")
    return states, pairs


def scopes_for(tune_names, analysis):
    scopes = []
    def add(family, tune, profile=None, activity=None, class_id=None):
        scopes.append({"id": len(scopes), "family": family, "tune": tune,
                       "profile": profile, "activity": activity,
                       "class_id": class_id})
    class_count = 1 + len(analysis["percentile_intervals"])
    for tune in tune_names:
        for profile in analysis["profiles"]:
            for activity in analysis["activities"]:
                for class_id in range(class_count):
                    add("pair", tune, profile["id"], activity["id"], class_id)
    for tune in tune_names:
        for profile in analysis["profiles"]:
            add("integrated_profile", tune, profile["id"])
    for tune in tune_names:
        for activity in analysis["activities"]:
            add("activity", tune, activity=activity["id"])
    for tune in tune_names:
        add("tune", tune)
    return scopes


def input_lineage(plan, admitted, receipts):
    shards = []
    for (shard, root_path, receipt_path), receipt in zip(admitted, receipts):
        shards.append({
            "ordinal": shard["ordinal"],
            "root_name": root_path.name,
            "receipt_name": receipt_path.name,
            "root_sha256": receipt["storage_identity"]["root_sha256"],
            "root_bytes": receipt["storage_identity"]["root_bytes"],
            "receipt_scientific_identity_sha256":
                receipt["scientific_identity_sha256"],
            "source_ids": shard["source_ids"],
        })
    sources = []
    for source_id, source in enumerate(plan["sources"]):
        if source.get("source_id") != source_id:
            raise ValueError("analysis-plan source IDs are not canonical")
        sources.append({"source_id": source_id,
                        "manifest_row": source["manifest_row"]})
    return {
        "lineage_schema": "hadronization_compact_input_lineage_v1",
        "campaign": {
            "id": plan["campaign"],
            "descriptor_name": Path(plan["campaign_descriptor"]).name,
            "descriptor_sha256": plan["campaign_descriptor_sha256"],
            "lossless_identity_sha256":
                plan["campaign_lossless_identity_sha256"],
        },
        "accepted_manifest": {
            "name": Path(plan["manifest"]).name,
            "sha256": plan["manifest_sha256"],
            "source_subset_sha256": plan["source_subset_digest"],
            "raw_mapping_sha256": plan["raw_mapping_digest"],
        },
        "attempt_ledger": {
            "name": Path(plan["attempts"]).name,
            "sha256": plan["attempt_ledger_sha256"],
        },
        "analysis_plan": {"schema": plan["schema"],
                          "sha256": plan["plan_digest"]},
        "shard_map": {"sha256": plan["map_digest"],
                      "target_bytes": plan["target_bytes"]},
        "lossless_contract": {
            "schema_sha256": plan["schema_digest"],
            "registries_sha256": plan["registries_digest"],
            "dependency_identity_sha256":
                plan["lossless_dependency_identity_sha256"],
        },
        "block_assignment": plan["block_assignment"],
        "tune_ordinals": plan["tune_ordinals"],
        "shard_count": len(shards),
        "source_count": len(sources),
        "shards": shards,
        "sources": sources,
    }


def _domain_dynamic(dynamic_species):
    if dynamic_species == "__DOMAIN_DYNAMIC_SPECIES__":
        return (dynamic_species, "__CLOSURE_SPECIES_COUNT__",
                "__T1_SPECIES_COUNT__")
    exact_keys(dynamic_species, {"closure_species_pdgs", "t1_all_final_pdgs"},
               "compact dynamic-PDG dictionaries")
    for key in ("closure_species_pdgs", "t1_all_final_pdgs"):
        values = dynamic_species[key]
        if (not isinstance(values, list) or
                any(type(value) is not int for value in values) or
                values != sorted(set(values))):
            raise ValueError("compact dynamic-PDG dictionary differs: {}".format(key))
    return (dynamic_species, len(dynamic_species["closure_species_pdgs"]),
            len(dynamic_species["t1_all_final_pdgs"]))


def compact_domains(analysis, analysis_sha, pairs, scopes, dynamic_species):
    dynamic, closure_species_count, t1_species_count = _domain_dynamic(
        dynamic_species)
    registries = analysis["compact_domain_registries"]
    trigger_dictionary = [
        {"id": identifier, "signed_pdg": pdg}
        for identifier, pdg in enumerate(
            analysis["pair_query_registry"]["trigger_pdgs"])]
    correlation_dictionary = [
        {"id": identifier, "trigger_pdg": values[0],
         "associate_pdg": values[1]}
        for identifier, values in enumerate(
            analysis["correlations"]["identities"])]
    class_dictionary = [{"id": 0, "integrated": True,
                         "percentile_interval": analysis["integrated_interval"]}]
    class_dictionary.extend(
        {"id": identifier, "integrated": False,
         "percentile_interval": interval}
        for identifier, interval in enumerate(
            analysis["percentile_intervals"], 1))
    scope_dictionary = list(scopes)
    tune_dictionary = []
    for scope in scope_dictionary:
        if (scope["family"] == "tune" and
                scope["tune"] not in tune_dictionary):
            tune_dictionary.append(scope["tune"])
    scope_ids = {
        family: [item["id"] for item in scope_dictionary
                 if item["family"] == family]
        for family in {item["scope_family"]
                       for item in registries["projection_ids"]}
    }
    scalar = [{"id": 0, "label": "additive_statistic"}]
    activity_bins = analysis["axes"]["activity"]["bins"]
    dphi_bins = analysis["axes"]["dphi"]["bins"]
    pt_storage_bins = len(analysis["axes"]["pt"]["edges"]) + 1
    g9_per_species = pt_storage_bins + 200
    projections = []

    def add(identifier, bin_count, dimensions, components):
        declared = registries["projection_ids"][identifier - 1]
        if declared["id"] != identifier:
            raise ValueError("projection registry IDs are not canonical")
        projections.append({
            "id": identifier,
            "name": declared["name"],
            "allowed_scope_families": [declared["scope_family"]],
            "scope_ids": scope_ids[declared["scope_family"]],
            "bin_count": bin_count,
            "bin_layout": {"packing": "row_major", "dimensions": dimensions},
            "component_dictionary": components,
            "component_ids": [item["id"] for item in components],
        })

    add(1, activity_bins,
        [{"id": "activity_bin", "size": activity_bins, "stride": 1}], scalar)
    add(2, len(pairs),
        [{"id": "pair_query_id", "size": len(pairs), "stride": 1}], scalar)
    add(3, len(trigger_dictionary),
        [{"id": "trigger_id", "size": len(trigger_dictionary), "stride": 1}],
        scalar)
    add(4, len(correlation_dictionary) * dphi_bins,
        [{"id": "correlation_id", "size": len(correlation_dictionary),
          "stride": dphi_bins},
         {"id": "dphi_bin", "size": dphi_bins, "stride": 1}],
        registries["correlation_component_ids"])
    add(5, len(pairs) * len(registries["origin_ids"]),
        [{"id": "pair_query_id", "size": len(pairs),
          "stride": len(registries["origin_ids"])},
         {"id": "origin_id", "size": len(registries["origin_ids"]),
          "stride": 1}], scalar)
    add(6, len(trigger_dictionary) * len(
        registries["closure_category_ids"]) * dphi_bins,
        [{"id": "trigger_id", "size": len(trigger_dictionary),
          "stride": len(registries["closure_category_ids"]) * dphi_bins},
         {"id": "closure_category_id",
          "size": len(registries["closure_category_ids"]),
          "stride": dphi_bins},
         {"id": "dphi_bin", "size": dphi_bins, "stride": 1}], scalar)
    add(7, (len(trigger_dictionary) * closure_species_count
            if type(closure_species_count) is int
            else "__CLOSURE_BIN_COUNT__"),
        [{"id": "trigger_id", "size": len(trigger_dictionary),
          "stride": closure_species_count},
         {"id": "closure_species_pdg_id", "size": closure_species_count,
          "stride": 1}], scalar)
    add(8, len(trigger_dictionary),
        [{"id": "trigger_id", "size": len(trigger_dictionary), "stride": 1}],
        registries["closure_full_visible_component_ids"])
    add(9, len(analysis["g9_species_pdgs"]) * g9_per_species,
        [{"id": "g9_species_id", "size": len(analysis["g9_species_pdgs"]),
          "stride": g9_per_species},
         {"id": "g9_axis_storage_bin", "size": g9_per_species,
          "stride": 1}], scalar)
    add(10, t1_species_count,
        [{"id": "t1_signed_pdg_id", "size": t1_species_count, "stride": 1}],
        registries["t1_component_ids"])

    pair_lookup = {(item["trigger_pdg"], item["associate_pdg"]): item
                   for item in pairs}
    terms = set()
    for opposite in pairs:
        if opposite["sign"] != -1:
            continue
        same = pair_lookup[(opposite["trigger_pdg"],
                            -opposite["associate_pdg"])]
        reference_opposite = pair_lookup[(opposite["trigger_pdg"],
                                          opposite["reference_meson_pdg"])]
        reference_same = pair_lookup[(opposite["trigger_pdg"],
                                      -opposite["reference_meson_pdg"])]
        trigger_id = 300 + next(
            item["id"] for item in trigger_dictionary
            if item["signed_pdg"] == opposite["trigger_pdg"])
        o, s = opposite["id"], same["id"]
        ro, rs = reference_opposite["id"], reference_same["id"]
        candidates = ([(o, o), (o, s), (o, trigger_id), (s, s),
                       (s, trigger_id), (trigger_id, trigger_id)]
                      if o == ro else
                      [(o, o), (o, s), (s, s), (o, trigger_id),
                       (s, trigger_id), (o, ro), (o, rs), (s, ro), (s, rs)])
        terms.update(tuple(sorted(term)) for term in candidates)
    gram_components = [
        {"id": item["id"], "kind_id": 0,
         "pair_query_id": item["id"],
         "trigger_pdg": item["trigger_pdg"],
         "associate_pdg": item["associate_pdg"]}
        for item in pairs]
    gram_components.extend(
        {"id": 300 + item["id"], "kind_id": 1,
         "trigger_id": item["id"], "trigger_pdg": item["signed_pdg"]}
        for item in trigger_dictionary)
    term_multiplier = 512
    return {
        "domain_schema": "hadronization_compact_domain_contract_v1",
        "analysis_request_sha256": analysis_sha,
        "sparse_rule": analysis["compact_storage"]["sparse_rule"],
        "block_ids": list(range(1, analysis["estimator_policy"][
            "release_block_count"] + 1)),
        "tune_dictionary": tune_dictionary,
        "scope_dictionary": scope_dictionary,
        "class_dictionary": class_dictionary,
        "axes": analysis["axes"],
        "profiles": analysis["profiles"],
        "activities": analysis["activities"],
        "trigger_dictionary": trigger_dictionary,
        "pair_query_dictionary": pairs,
        "origin_dictionary": registries["origin_ids"],
        "closure_category_dictionary": registries["closure_category_ids"],
        "correlation_dictionary": correlation_dictionary,
        "correlation_component_dictionary":
            registries["correlation_component_ids"],
        "closure_full_visible_component_dictionary":
            registries["closure_full_visible_component_ids"],
        "g9_species_dictionary": [
            {"id": identifier, "signed_pdg": pdg}
            for identifier, pdg in enumerate(analysis["g9_species_pdgs"])],
        "g9_axis_dictionary": [
            {**registries["g9_axis_ids"][0], "offset": 0,
             "storage_bins": pt_storage_bins,
             "underflow_id": 0,
             "regular_bin_ids": [1, pt_storage_bins - 2],
             "overflow_id": pt_storage_bins - 1,
             "endpoint_rule": analysis["axes"]["pt"]["endpoint_rule"]},
            {**registries["g9_axis_ids"][1], "offset": pt_storage_bins,
             "storage_bins": 100,
             "endpoint_rule": analysis["axes"]["eta"]["endpoint_rule"]},
            {**registries["g9_axis_ids"][2], "offset": pt_storage_bins + 100,
             "storage_bins": 100,
             "endpoint_rule": analysis["axes"]["phi"]["endpoint_rule"]},
        ],
        "t1_component_dictionary": registries["t1_component_ids"],
        "dynamic_species": dynamic,
        "projection_dictionary": projections,
        "event_gram_dictionary": {
            "projection_id": 2,
            "allowed_scope_families": ["pair"],
            "scope_ids": scope_ids["pair"],
            "component_kinds": registries["gram_component_kinds"],
            "component_dictionary": gram_components,
            "component_ids": [item["id"] for item in gram_components],
            "term_order": "left<=right",
            "term_code": "left*512+right",
            "term_code_multiplier": term_multiplier,
            "allowed_term_codes": [left * term_multiplier + right
                                   for left, right in sorted(terms)],
        },
    }


def stress_compact_payloads(analysis, analysis_sha):
    """Build a full-shape synthetic contract for the bounded storage gate."""
    tune_names = ["MONASH", "JUNCTIONS", "CLOSEPACKING"]
    scopes = scopes_for(tune_names, analysis)
    states, pairs = state_registry(analysis)
    species = {item["pdg"] for item in states}
    candidate = 100000
    while len(species) < 202:
        species.add(candidate)
        if len(species) < 202:
            species.add(-candidate)
        candidate += 1
    dynamic = {"closure_species_pdgs": sorted(species),
               "t1_all_final_pdgs": sorted(species)}
    domains = compact_domains(analysis, analysis_sha, pairs, scopes, dynamic)
    validate_compact_domains(domains, analysis, analysis_sha)

    def identity(label):
        return sha_bytes(("hadronization-reduce-stress-v1:" + label).encode("ascii"))

    tune_ordinals = {name: ordinal for ordinal, name in enumerate(tune_names)}
    sources = []
    for source_id in range(3000):
        tune_ordinal, logical_id = divmod(source_id, 1000)
        tune = tune_names[tune_ordinal]
        sources.append({
            "source_id": source_id,
            "manifest_row": {
                "accepted_attempt": source_id % 3,
                "accepted_seed": 130000001 + tune_ordinal * 1000000 + logical_id,
                "block": logical_id % 10 + 1,
                "bytes": 900000000 + source_id * 7919 % 100000000,
                "logical_id": logical_id,
                "raw_sha256": identity("raw:{}".format(source_id)),
                "raw_storage_key": "{}/job{:04d}.root".format(tune, logical_id),
                "successful_events": 100000,
                "tune": tune,
                "validation_log_sha256": identity(
                    "validation-log:{}".format(source_id)),
                "validation_receipt_sha256": identity(
                    "validation-receipt:{}".format(source_id)),
            },
        })
    shard_sizes = [10] * 93 + [9] * 230
    shards = []
    first = 0
    for ordinal, count in enumerate(shard_sizes):
        members = list(range(first, first + count))
        shards.append({
            "ordinal": ordinal,
            "root_name": "shard-{:04d}.root".format(ordinal),
            "receipt_name": "shard-{:04d}.json".format(ordinal),
            "root_sha256": identity("shard-root:{}".format(ordinal)),
            "root_bytes": sum(sources[item]["manifest_row"]["bytes"]
                              for item in members) // 2,
            "receipt_scientific_identity_sha256": identity(
                "shard-scientific:{}".format(ordinal)),
            "source_ids": members,
        })
        first += count
    if first != len(sources):
        raise ValueError("stress lineage source partition differs")
    lineage = {
        "lineage_schema": "hadronization_compact_input_lineage_v1",
        "campaign": {
            "id": "HF_RUN3_V1",
            "descriptor_name": "campaign.json",
            "descriptor_sha256": identity("campaign-descriptor"),
            "lossless_identity_sha256": identity("campaign-lossless"),
        },
        "accepted_manifest": {
            "name": "raw_manifest.jsonl",
            "sha256": identity("accepted-manifest"),
            "source_subset_sha256": sha_bytes(canonical(
                [item["manifest_row"] for item in sources]).encode("ascii")),
            "raw_mapping_sha256": identity("raw-mapping"),
        },
        "attempt_ledger": {"name": "attempts.csv",
                           "sha256": identity("attempt-ledger")},
        "analysis_plan": {
            "schema": "hadronization_analysis_shard_plan_v1",
            "sha256": identity("analysis-plan"),
        },
        "shard_map": {"sha256": identity("shard-map"),
                      "target_bytes": 512 * 1024 * 1024},
        "lossless_contract": {
            "schema_sha256": identity("lossless-schema"),
            "registries_sha256": identity("lossless-registries"),
            "dependency_identity_sha256": identity("lossless-dependency"),
        },
        "block_assignment": {"count": 10,
                             "logical_id_domain": [0, 999],
                             "logical_id_rule": "block=(logical_id%10)+1"},
        "tune_ordinals": tune_ordinals,
        "shard_count": len(shards), "source_count": len(sources),
        "shards": shards, "sources": sources,
    }
    lineage_sha = validate_input_lineage(lineage)
    domain_sha = sha_bytes(canonical(domains).encode("ascii"))
    activity = []
    for tune in tune_names:
        for definition in analysis["activities"]:
            activity.append({
                "semantic_id": definition["id"], "tune": tune,
                "class_ids": list(range(1 + len(analysis[
                    "percentile_intervals"]))),
                "thresholds": [1000 + tune_ordinals[tune] * 100 + value
                               for value in range(len(analysis[
                                   "percentile_intervals"]) - 1)],
                "source_count": 1000, "successful_events": 100000000,
            })
    accounting = {
        "summation": analysis["compact_storage"]["summation"],
        "blocks": [
            {"tune": tune, "block": block, "sources": 100,
             "successful_events": 10000000}
            for tune in tune_names for block in range(1, 11)],
    }
    estimator = {"policy_id": analysis["estimator_policy"]["id"],
                 "block_count": 10, "dof": 9,
                 "stress_contract": "full_shape_storage_only"}
    metrics = {"cells": 1664280, "event_gram": 946080,
               "events": 300000000, "sources": 3000,
               "input_bytes": sum(item["root_bytes"] for item in shards)}
    activity_sha = sha_bytes(canonical(activity).encode("ascii"))
    accounting_sha = sha_bytes(canonical(accounting).encode("ascii"))
    plan_sha = lineage["analysis_plan"]["sha256"]
    map_sha = lineage["shard_map"]["sha256"]
    build_id = identity("stress-build")
    common = {
        "analysis_request_sha256": analysis_sha,
        "parent_plan_digest": plan_sha,
        "parent_map_digest": map_sha,
        "parent_shard_set_digest": lineage_sha,
        "reducer_build_id": build_id,
        "scientific_content_digest": "__SCIENTIFIC_DIGEST__",
        "compact_domains": domains,
        "compact_domains_sha256": domain_sha,
        "input_lineage": lineage,
        "input_lineage_sha256": lineage_sha,
        "activity_receipts": activity,
        "block_accounting": accounting,
        "estimator_audit": estimator,
        "metrics": metrics,
    }
    metadata = {
        **common,
        "schema": REDUCTION_SCHEMA,
        "publication_state": "PUBLICATION_ELIGIBLE",
        "base_study": analysis["base_study"],
        "lossless_input": analysis["lossless_input"],
        "estimator_policy": analysis["estimator_policy"],
        "sparse_rule": analysis["compact_storage"]["sparse_rule"],
        "pooled_copy": False,
    }
    embedded = {
        **common,
        "schema": RECEIPT_SCHEMA,
        "state": "PUBLICATION_ELIGIBLE",
        "activity_receipts_sha256": activity_sha,
        "block_accounting_sha256": accounting_sha,
        "estimator_policy_id": analysis["estimator_policy"]["id"],
    }
    return metadata, embedded


def write_stress_spec(path, analysis_path=ANALYSIS):
    analysis, analysis_sha = checked_analysis(analysis_path)
    metadata, embedded = stress_compact_payloads(analysis, analysis_sha)
    path.write_text("\n".join((
        "hadronization_compact_stress_spec_v1",
        "METADATA\t" + hexadecimal(canonical(metadata)),
        "RECEIPT\t" + hexadecimal(canonical(embedded)),
        "END", "")), encoding="ascii")


def build_metadata(analysis, analysis_sha, plan, publication, states, pairs,
                   scopes, parent_digest, build_id, domain_template,
                   lineage, lineage_sha):
    return {
        "schema": REDUCTION_SCHEMA,
        "analysis_request_sha256": analysis_sha,
        "base_study": analysis["base_study"],
        "lossless_input": analysis["lossless_input"],
        "parent_plan_digest": plan["plan_digest"],
        "parent_map_digest": plan["map_digest"],
        "parent_shard_set_digest": parent_digest,
        "reducer_build_id": build_id,
        "publication_state": publication,
        "estimator_policy": analysis["estimator_policy"],
        "compact_domains": "__COMPACT_DOMAINS__",
        "compact_domains_sha256": "__COMPACT_DOMAINS_SHA256__",
        "input_lineage": "__INPUT_LINEAGE__",
        "input_lineage_sha256": lineage_sha,
        "sparse_rule": analysis["compact_storage"]["sparse_rule"],
        "pooled_copy": False,
        "activity_receipts": "__ACTIVITY_RECEIPTS__",
        "block_accounting": "__BLOCK_ACCOUNTING__",
        "estimator_audit": "__ESTIMATOR_AUDIT__",
        "metrics": "__METRICS__",
        "scientific_content_digest": "__SCIENTIFIC_DIGEST__",
    }


def hexadecimal(value):
    return value.encode("utf-8").hex()


def float_text(value):
    return float(value).hex()


def write_spec(path, plan, admitted, receipts, analysis, analysis_sha,
               publication, states, pairs, scopes, parent_digest, build_id,
               domain_template, lineage, lineage_sha):
    metadata = build_metadata(analysis, analysis_sha, plan, publication, states,
                              pairs, scopes, parent_digest, build_id,
                              domain_template, lineage, lineage_sha)
    embedded = {
        "schema": RECEIPT_SCHEMA,
        "state": publication,
        "analysis_request_sha256": analysis_sha,
        "parent_plan_digest": plan["plan_digest"],
        "parent_map_digest": plan["map_digest"],
        "parent_shard_set_digest": parent_digest,
        "reducer_build_id": build_id,
        "scientific_content_digest": "__SCIENTIFIC_DIGEST__",
        "compact_domains": "__COMPACT_DOMAINS__",
        "compact_domains_sha256": "__COMPACT_DOMAINS_SHA256__",
        "input_lineage": "__INPUT_LINEAGE__",
        "input_lineage_sha256": lineage_sha,
        "activity_receipts": "__ACTIVITY_RECEIPTS__",
        "block_accounting": "__BLOCK_ACCOUNTING__",
        "estimator_audit": "__ESTIMATOR_AUDIT__",
        "metrics": "__METRICS__",
        "activity_receipts_sha256": "__ACTIVITY_RECEIPTS_SHA256__",
        "block_accounting_sha256": "__BLOCK_ACCOUNTING_SHA256__",
        "estimator_policy_id": analysis["estimator_policy"]["id"],
    }
    lines = [SPEC_SCHEMA,
             "SETTING\tanalysis_sha256\t{}".format(analysis_sha),
             "SETTING\tplan_digest\t{}".format(plan["plan_digest"]),
             "SETTING\tmap_digest\t{}".format(plan["map_digest"]),
             "SETTING\tparent_shard_set_digest\t{}".format(parent_digest),
             "SETTING\tpublication_state\t{}".format(publication),
             "SETTING\tblock_count\t{}".format(plan["block_assignment"]["count"]),
             "SETTING\tactivity_bins\t{}".format(analysis["axes"]["activity"]["bins"]),
             "SETTING\tdphi_bins\t{}".format(analysis["axes"]["dphi"]["bins"]),
             "SETTING\tdphi_low\t{}".format(float_text(analysis["axes"]["dphi"]["low"])),
             "SETTING\tdphi_high\t{}".format(float_text(analysis["axes"]["dphi"]["high"])),
             "SETTING\teta_low\t{}".format(float_text(analysis["axes"]["eta"]["low"])),
             "SETTING\teta_high\t{}".format(float_text(analysis["axes"]["eta"]["high"])),
             "SETTING\tphi_low\t{}".format(float_text(analysis["axes"]["phi"]["low"])),
             "SETTING\tphi_high\t{}".format(float_text(analysis["axes"]["phi"]["high"])),
             "SETTING\tcompact_domains_template\t{}".format(
                 hexadecimal(canonical(domain_template))),
             "SETTING\tinput_lineage\t{}".format(
                 hexadecimal(canonical(lineage))),
             "SETTING\tinput_lineage_sha256\t{}".format(lineage_sha),
             "SETTING\tmetadata_template\t{}".format(hexadecimal(canonical(metadata))),
             "SETTING\treceipt_template\t{}".format(hexadecimal(canonical(embedded)))]
    for edge in analysis["axes"]["pt"]["edges"]:
        lines.append("PTEDGE\t{}".format(float_text(edge)))
    for index, profile in enumerate(analysis["profiles"]):
        trigger = profile["trigger_pt"]
        associate = profile["associate_pt"]
        lines.append("PROFILE\t{}\t{}\t{}\t{}".format(
            index, profile["id"],
            "NONE" if trigger is None else float_text(trigger["value"]),
            "NONE" if associate is None else float_text(associate["value"])))
    for index, activity in enumerate(analysis["activities"]):
        lines.append("ACTIVITY\t{}\t{}\t{}".format(
            index, activity["id"], activity["physical_field"]))
    lines.append("CLASS\t0\t0\t100\t1")
    for index, interval in enumerate(analysis["percentile_intervals"], 1):
        lines.append("CLASS\t{}\t{}\t{}\t0".format(
            index, interval[0], interval[1]))
    for item in states:
        lines.append("STATE\t{}\t{}\t{}\t{}\t{}\t{}".format(
            item["pdg"], item["id"], item["sector"],
            int(item["pair_analysis_eligible"]), item["qc"], item["qb"]))
    for item in pairs:
        lines.append("PAIR\t{id}\t{trigger_pdg}\t{associate_pdg}\t{sign}\t"
                     "{reference_meson_pdg}\t{central_eligible}".format(
                         **{**item, "central_eligible":
                            int(item["central_eligible"])}))
    for index, pair in enumerate(analysis["correlations"]["identities"]):
        lines.append("CORRELATION\t{}\t{}\t{}".format(index, pair[0], pair[1]))
    for pdg in analysis["g9_species_pdgs"]:
        lines.append("G9\t{}".format(pdg))
    for item in scopes:
        lines.append("SCOPE\t{}\t{}\t{}\t{}\t{}\t{}".format(
            item["id"], item["family"], item["tune"],
            item["profile"] if item["profile"] is not None else "-",
            item["activity"] if item["activity"] is not None else "-",
            item["class_id"] if item["class_id"] is not None else -1))
    for (shard, root_path, unused_receipt), receipt in zip(admitted, receipts):
        del unused_receipt
        scientific = receipt["scientific_identity"]
        lines.append("SHARD\t{}\t{}\t{}\t{}\t{}".format(
            shard["ordinal"], hexadecimal(str(root_path)),
            scientific["scientific_content_digest"],
            len(shard["source_ids"]),
            sum(receipt["rows"].values())))
        for name in ANALYZER_TABLES:
            lines.append("ROW\t{}\t{}\t{}".format(
                shard["ordinal"], name, receipt["rows"][name]))
        for local_id, source_id in enumerate(shard["source_ids"]):
            source = plan["sources"][source_id]["manifest_row"]
            lines.append("SOURCE\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}".format(
                shard["ordinal"], local_id, source_id,
                plan["tune_ordinals"][source["tune"]], source["block"],
                source["logical_id"], source["accepted_attempt"],
                source["successful_events"], hexadecimal(source["tune"]),
                hexadecimal(canonical(source))))
    lines.append("END")
    path.write_text("\n".join(lines) + "\n", encoding="ascii")


def command_tokens(command, argument, environment):
    completed = subprocess.run([command, argument], env=environment, text=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if completed.returncode or completed.stderr.strip():
        raise ValueError("ROOT configuration failed: {}".format(
            completed.stderr.strip() or completed.stdout.strip()))
    return shlex.split(completed.stdout.strip())


def build_reducer(work_root):
    runtime = runtime_module().resolve(require_root=True)
    environment = os.environ.copy()
    environment.update(runtime["environment"])
    source = ROOT / "pipeline/reduce/reduce.cpp"
    header = ROOT / "pipeline/reduce/statistics.hpp"
    identity = {
        "schema": "hadronization_reducer_build_v1",
        "source_sha256": sha_file(source), "statistics_sha256": sha_file(header),
        "compiler": runtime["environment"]["CXX"],
        "root": next(item.split("=", 1)[1] for item in runtime["diagnostics"]
                     if item.startswith("ROOT=")),
        "flags": ["-std=c++17", "-O2", "-Wall", "-Wextra", "-Wpedantic", "-Werror"],
    }
    build_id = sha_bytes(canonical(identity).encode("ascii"))
    bin_root = work_root / "bin"
    bin_root.mkdir(parents=True, exist_ok=True)
    binary = bin_root / ("reduce-" + build_id[:20])
    receipt = binary.with_suffix(".build.json")
    if binary.is_file() and receipt.is_file():
        current = json_file(receipt)
        if (current.get("build_identity") == identity and
                current.get("binary_sha256") == sha_file(binary)):
            return environment, binary, current
        binary.unlink()
        receipt.unlink()
    flags = command_tokens(environment["ROOT_CONFIG"], "--cflags", environment)
    libraries = command_tokens(environment["ROOT_CONFIG"], "--libs", environment)
    temporary = binary.with_name("." + binary.name + ".tmp")
    command = [environment["CXX"]] + identity["flags"] + [
        "-I" + str(ROOT / "pipeline/generate"),
        "-I" + str(ROOT / "pipeline/reduce"), str(source)] + flags + libraries + [
        "-o", str(temporary)]
    completed = subprocess.run(command, env=environment, text=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if completed.returncode or completed.stdout.strip() or completed.stderr.strip():
        if temporary.exists():
            temporary.unlink()
        raise ValueError("reducer warning-free build failed: {}".format(
            completed.stderr.strip() or completed.stdout.strip()))
    os.chmod(str(temporary), 0o700)
    os.replace(str(temporary), str(binary))
    fsync_file(binary)
    build_receipt = {"schema": "hadronization_reducer_build_receipt_v1",
                     "build_id": build_id, "build_identity": identity,
                     "binary_sha256": sha_file(binary)}
    atomic_json(receipt, build_receipt, exclusive=False)
    return environment, binary, build_receipt


def parent_shard_set_digest(lineage):
    return sha_bytes(canonical(lineage).encode("ascii"))


def parse_summary(stdout):
    lines = [line for line in stdout.splitlines()
             if line.startswith("REDUCTION_SUMMARY ")]
    if len(lines) != 1:
        raise ValueError("reducer emitted no unique summary")
    values = {}
    for token in lines[0].split()[1:]:
        key, value = token.split("=", 1)
        values[key] = value
    expected = {"cells", "event_gram", "events", "sources", "input_bytes",
                "scientific_digest", "activity_receipts_sha256",
                "block_accounting_sha256", "compact_domains_sha256",
                "input_lineage_sha256", "dynamic_species_hex",
                "analysis_sha256", "plan_digest", "map_digest",
                "parent_shard_set_digest", "publication_state",
                "metadata_sha256", "embedded_receipt_sha256", "build_id"}
    if set(values) != expected:
        raise ValueError("reducer summary field set differs")
    digest_fields = {"scientific_digest", "activity_receipts_sha256",
                     "block_accounting_sha256", "compact_domains_sha256",
                     "input_lineage_sha256",
                     "analysis_sha256", "plan_digest", "map_digest",
                     "parent_shard_set_digest", "metadata_sha256",
                     "embedded_receipt_sha256", "build_id"}
    for key in digest_fields:
        lower_sha(values[key], "reducer {}".format(key))
    dynamic_hex = values["dynamic_species_hex"]
    if (not dynamic_hex or len(dynamic_hex) % 2 or
            any(character not in "0123456789abcdef" for character in dynamic_hex)):
        raise ValueError("reducer dynamic-species payload is not lowercase hex")
    try:
        values["dynamic_species"] = json.loads(bytes.fromhex(
            dynamic_hex).decode("ascii"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise ValueError("reducer dynamic-species payload is invalid") from error
    del values["dynamic_species_hex"]
    if values["publication_state"] not in {"PUBLICATION_ELIGIBLE",
                                            "NONPUBLICATION_PARTIAL"}:
        raise ValueError("reducer publication state differs")
    for key in expected - digest_fields - {"publication_state",
                                            "dynamic_species_hex"}:
        values[key] = int(values[key])
    return values


def validate_summary_binding(summary, plan, analysis_sha, parent_digest,
                             publication, build_id):
    expected = {"analysis_sha256": analysis_sha,
                "plan_digest": plan["plan_digest"],
                "map_digest": plan["map_digest"],
                "parent_shard_set_digest": parent_digest,
                "input_lineage_sha256": parent_digest,
                "publication_state": publication,
                "build_id": build_id}
    for key, value in expected.items():
        if summary[key] != value:
            raise ValueError("compact embedded {} binding differs".format(key))


def run_binary(binary, environment, arguments, label):
    completed = subprocess.run([str(binary)] + list(arguments), env=environment,
                               text=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    if completed.returncode:
        raise ValueError("{} failed: {}".format(label, completed.stderr.strip()))
    if completed.stderr.strip():
        raise ValueError("{} wrote a diagnostic: {}".format(
            label, completed.stderr.strip()))
    return completed


def output_paths(plan, analysis_sha, parent_digest, output_root):
    stem = "plot-source-{}-{}".format(analysis_sha[:12], parent_digest[:12])
    directory = output_root / plan["campaign"]
    return directory / (stem + ".root"), directory / (stem + ".json")


def reduction_receipt(plan, analysis_sha, parent_digest, publication,
                      root_path, summary, build, elapsed, source_count,
                      domains, lineage):
    scientific = {
        "analysis_request_sha256": analysis_sha,
        "parent_plan_digest": plan["plan_digest"],
        "parent_map_digest": plan["map_digest"],
        "parent_shard_set_digest": parent_digest,
        "scientific_content_digest": summary["scientific_digest"],
        "activity_receipts_sha256": summary["activity_receipts_sha256"],
        "block_accounting_sha256": summary["block_accounting_sha256"],
        "compact_domains": domains,
        "compact_domains_sha256": summary["compact_domains_sha256"],
        "input_lineage": lineage,
        "input_lineage_sha256": summary["input_lineage_sha256"],
        "metadata_sha256": summary["metadata_sha256"],
        "embedded_receipt_sha256": summary["embedded_receipt_sha256"],
        "reducer_build_id": summary["build_id"],
        "cells": summary["cells"], "event_gram": summary["event_gram"],
        "events": summary["events"], "sources": summary["sources"],
    }
    storage = {"compression": {"algorithm": "ZSTD", "level": 5},
               "root_bytes": root_path.stat().st_size,
               "root_sha256": sha_file(root_path),
               "object_set": ["cells", "event_gram", "metadata", "receipt"]}
    provenance = {"build": build, "elapsed_seconds": elapsed,
                  "host": platform.node(), "python": platform.python_version(),
                  "source_count": source_count,
                  "input_bytes": summary["input_bytes"]}
    return {
        "schema": RECEIPT_SCHEMA, "state": publication,
        "scientific_identity": scientific,
        "scientific_identity_sha256": sha_bytes(canonical(scientific).encode("ascii")),
        "storage_identity": storage,
        "storage_identity_sha256": sha_bytes(canonical(storage).encode("ascii")),
        "producer_provenance": provenance,
        "producer_provenance_sha256": sha_bytes(canonical(provenance).encode("ascii")),
    }


def validate_input_lineage(lineage, expected_sha=None):
    exact_keys(lineage, {"lineage_schema", "campaign", "accepted_manifest",
                         "attempt_ledger", "analysis_plan", "shard_map",
                         "lossless_contract", "block_assignment",
                         "tune_ordinals", "shard_count", "source_count",
                         "shards", "sources"}, "compact input lineage")
    if lineage["lineage_schema"] != "hadronization_compact_input_lineage_v1":
        raise ValueError("compact input-lineage schema differs")
    exact_keys(lineage["campaign"], {"id", "descriptor_name",
                                     "descriptor_sha256",
                                     "lossless_identity_sha256"},
               "compact lineage campaign")
    exact_keys(lineage["accepted_manifest"], {"name", "sha256",
                                               "source_subset_sha256",
                                               "raw_mapping_sha256"},
               "compact lineage accepted manifest")
    exact_keys(lineage["attempt_ledger"], {"name", "sha256"},
               "compact lineage attempt ledger")
    exact_keys(lineage["analysis_plan"], {"schema", "sha256"},
               "compact lineage analysis plan")
    exact_keys(lineage["shard_map"], {"sha256", "target_bytes"},
               "compact lineage shard map")
    exact_keys(lineage["lossless_contract"], {"schema_sha256",
                                               "registries_sha256",
                                               "dependency_identity_sha256"},
               "compact lineage lossless contract")
    for container, keys in (
            (lineage["campaign"], ("descriptor_sha256",
                                   "lossless_identity_sha256")),
            (lineage["accepted_manifest"], ("sha256",
                                             "source_subset_sha256",
                                             "raw_mapping_sha256")),
            (lineage["attempt_ledger"], ("sha256",)),
            (lineage["analysis_plan"], ("sha256",)),
            (lineage["shard_map"], ("sha256",)),
            (lineage["lossless_contract"], ("schema_sha256",
                                             "registries_sha256",
                                             "dependency_identity_sha256"))):
        for key in keys:
            lower_sha(container[key], "compact lineage {}".format(key))
    for container, key in ((lineage["campaign"], "descriptor_name"),
                           (lineage["accepted_manifest"], "name"),
                           (lineage["attempt_ledger"], "name")):
        name = container[key]
        if (not isinstance(name, str) or not name or Path(name).name != name or
                name in {".", ".."}):
            raise ValueError("compact lineage portable name differs")
    assignment = lineage["block_assignment"]
    exact_keys(assignment, {"count", "logical_id_domain", "logical_id_rule"},
               "compact lineage block assignment")
    if (assignment["count"] != 10 or
            assignment["logical_id_rule"] !=
            "block=(logical_id%10)+1" or
            not isinstance(assignment["logical_id_domain"], list) or
            len(assignment["logical_id_domain"]) != 2):
        raise ValueError("compact lineage is not the release K10 assignment")
    tune_ordinals = lineage["tune_ordinals"]
    if (not isinstance(tune_ordinals, dict) or not tune_ordinals or
            any(not isinstance(name, str) or not name or type(value) is not int
                for name, value in tune_ordinals.items()) or
            sorted(tune_ordinals.values()) != list(range(len(tune_ordinals)))):
        raise ValueError("compact lineage tune ordinals differ")
    shards = lineage["shards"]
    sources = lineage["sources"]
    if (type(lineage["shard_count"]) is not int or
            lineage["shard_count"] != len(shards) or not shards or
            type(lineage["source_count"]) is not int or
            lineage["source_count"] != len(sources) or not sources):
        raise ValueError("compact lineage counts differ")
    concatenated = []
    for ordinal, shard in enumerate(shards):
        exact_keys(shard, {"ordinal", "root_name", "receipt_name",
                           "root_sha256", "root_bytes",
                           "receipt_scientific_identity_sha256", "source_ids"},
                   "compact lineage shard")
        if (shard["ordinal"] != ordinal or
                shard["root_name"] != "shard-{:04d}.root".format(ordinal) or
                shard["receipt_name"] != "shard-{:04d}.json".format(ordinal) or
                type(shard["root_bytes"]) is not int or
                shard["root_bytes"] < 1 or
                not isinstance(shard["source_ids"], list) or
                not shard["source_ids"] or
                any(type(value) is not int for value in shard["source_ids"])):
            raise ValueError("compact lineage shard member/order differs")
        lower_sha(shard["root_sha256"], "compact lineage shard ROOT")
        lower_sha(shard["receipt_scientific_identity_sha256"],
                  "compact lineage shard receipt")
        concatenated.extend(shard["source_ids"])
    if concatenated != list(range(len(sources))):
        raise ValueError("compact lineage source membership/order differs")
    manifest_keys = {"accepted_attempt", "accepted_seed", "block", "bytes",
                     "logical_id", "raw_sha256", "raw_storage_key",
                     "successful_events", "tune", "validation_log_sha256",
                     "validation_receipt_sha256"}
    logical_domain = assignment["logical_id_domain"]
    manifest_rows = []
    source_order = []
    for source_id, source in enumerate(sources):
        exact_keys(source, {"source_id", "manifest_row"},
                   "compact lineage source")
        row = source["manifest_row"]
        exact_keys(row, manifest_keys, "compact lineage manifest row")
        raw_key = row["raw_storage_key"]
        if (source["source_id"] != source_id or
                row["tune"] not in tune_ordinals or
                type(row["logical_id"]) is not int or
                not logical_domain[0] <= row["logical_id"] <= logical_domain[1] or
                type(row["block"]) is not int or
                row["block"] != row["logical_id"] % 10 + 1 or
                type(row["accepted_attempt"]) is not int or
                row["accepted_attempt"] < 0 or
                type(row["accepted_seed"]) is not int or
                row["accepted_seed"] < 1 or
                type(row["successful_events"]) is not int or
                row["successful_events"] < 1 or
                type(row["bytes"]) is not int or row["bytes"] < 1 or
                not isinstance(raw_key, str) or not raw_key or
                raw_key.startswith("/") or "\\" in raw_key or
                ".." in Path(raw_key).parts):
            raise ValueError("compact lineage source manifest identity differs")
        for key in ("raw_sha256", "validation_log_sha256",
                    "validation_receipt_sha256"):
            lower_sha(row[key], "compact lineage source {}".format(key))
        manifest_rows.append(row)
        source_order.append((tune_ordinals[row["tune"]], row["logical_id"]))
    if (source_order != sorted(set(source_order)) or
            lineage["accepted_manifest"]["source_subset_sha256"] !=
            sha_bytes(canonical(manifest_rows).encode("ascii"))):
        raise ValueError("compact lineage source subset/order digest differs")
    digest = sha_bytes(canonical(lineage).encode("ascii"))
    if expected_sha is not None and digest != expected_sha:
        raise ValueError("compact input-lineage payload digest differs")
    return digest


def validate_compact_domains(domains, analysis, analysis_sha):
    if not isinstance(domains, dict):
        raise ValueError("compact domain payload is not an object")
    tunes = domains.get("tune_dictionary")
    if (not isinstance(tunes, list) or not tunes or
            any(not isinstance(value, str) or not value for value in tunes) or
            len(set(tunes)) != len(tunes)):
        raise ValueError("compact domain tune dictionary differs")
    expected_scopes = scopes_for(tunes, analysis)
    if domains.get("scope_dictionary") != expected_scopes:
        raise ValueError("compact domain scope dictionary differs")
    dynamic = domains.get("dynamic_species")
    _domain_dynamic(dynamic)
    unused_states, pairs = state_registry(analysis)
    del unused_states
    expected = compact_domains(analysis, analysis_sha, pairs, expected_scopes,
                               dynamic)
    if domains != expected:
        raise ValueError("compact machine-readable domain contract differs")
    return sha_bytes(canonical(domains).encode("ascii"))


def verify_output(root_path, receipt_path, analysis_path, work_root):
    analysis, analysis_sha = checked_analysis(analysis_path)
    regular_file(root_path, "compact ROOT")
    receipt = json_file(receipt_path)
    exact_keys(receipt, {"schema", "state", "scientific_identity",
                         "scientific_identity_sha256", "storage_identity",
                         "storage_identity_sha256", "producer_provenance",
                         "producer_provenance_sha256"}, "reduction receipt")
    if (receipt["schema"] != RECEIPT_SCHEMA or
            receipt["state"] not in {"PUBLICATION_ELIGIBLE",
                                     "NONPUBLICATION_PARTIAL"}):
        raise ValueError("reduction receipt state/schema differs")
    scientific = receipt["scientific_identity"]
    storage = receipt["storage_identity"]
    provenance = receipt["producer_provenance"]
    exact_keys(scientific, {"analysis_request_sha256", "parent_plan_digest",
                            "parent_map_digest", "parent_shard_set_digest",
                            "scientific_content_digest",
                            "activity_receipts_sha256",
                            "block_accounting_sha256",
                            "compact_domains", "compact_domains_sha256",
                            "input_lineage", "input_lineage_sha256",
                            "metadata_sha256",
                            "embedded_receipt_sha256", "reducer_build_id",
                            "cells", "event_gram",
                            "events", "sources"},
               "reduction scientific identity")
    exact_keys(storage, {"compression", "root_bytes", "root_sha256",
                         "object_set"}, "reduction storage identity")
    exact_keys(provenance, {"build", "elapsed_seconds", "host", "python",
                            "source_count", "input_bytes"},
               "reduction producer provenance")
    build = provenance["build"]
    exact_keys(build, {"schema", "build_id", "build_identity",
                       "binary_sha256"}, "reduction build receipt")
    exact_keys(build["build_identity"], {"schema", "source_sha256",
                                         "statistics_sha256", "compiler",
                                         "root", "flags"},
               "reduction build identity")
    if (build["schema"] != "hadronization_reducer_build_receipt_v1" or
            build["build_identity"]["schema"] !=
            "hadronization_reducer_build_v1" or
            build["build_id"] != scientific["reducer_build_id"] or
            build["build_id"] != sha_bytes(canonical(
                build["build_identity"]).encode("ascii"))):
        raise ValueError("reduction build provenance differs")
    for key in ("source_sha256", "statistics_sha256"):
        lower_sha(build["build_identity"][key],
                  "reduction build {}".format(key))
    lower_sha(build["binary_sha256"], "reduction binary")
    if (type(provenance["elapsed_seconds"]) not in (int, float) or
            not math.isfinite(provenance["elapsed_seconds"]) or
            provenance["elapsed_seconds"] < 0 or
            type(provenance["source_count"]) is not int or
            provenance["source_count"] < 1 or
            type(provenance["input_bytes"]) is not int or
            provenance["input_bytes"] < 1 or
            not isinstance(provenance["host"], str) or
            not provenance["host"] or
            not isinstance(provenance["python"], str) or
            not provenance["python"]):
        raise ValueError("reduction producer metrics differ")
    if (receipt["scientific_identity_sha256"] !=
            sha_bytes(canonical(scientific).encode("ascii")) or
            receipt["storage_identity_sha256"] !=
            sha_bytes(canonical(storage).encode("ascii")) or
            receipt["producer_provenance_sha256"] !=
            sha_bytes(canonical(provenance).encode("ascii"))):
        raise ValueError("reduction receipt nested digest differs")
    domain_sha = validate_compact_domains(scientific["compact_domains"],
                                          analysis, analysis_sha)
    lineage_sha = validate_input_lineage(scientific["input_lineage"],
                                         scientific["input_lineage_sha256"])
    if (scientific["compact_domains_sha256"] != domain_sha or
            scientific["input_lineage_sha256"] != lineage_sha or
            scientific["parent_shard_set_digest"] != lineage_sha):
        raise ValueError("reduction receipt compact contract binding differs")
    if scientific.get("analysis_request_sha256") != analysis_sha:
        raise ValueError("analysis request changed since reduction")
    if (storage.get("compression") != {"algorithm": "ZSTD", "level": 5} or
            storage.get("object_set") !=
            ["cells", "event_gram", "metadata", "receipt"]):
        raise ValueError("compact ROOT storage contract differs")
    if (storage.get("root_bytes") != root_path.stat().st_size or
            storage.get("root_sha256") != sha_file(root_path)):
        raise ValueError("compact ROOT physical identity differs")
    environment, binary, current_build = build_reducer(work_root)
    for key in ("source_sha256", "statistics_sha256"):
        if (build["build_identity"][key] !=
                current_build["build_identity"][key]):
            raise ValueError("reduction receipt/current reducer source differs")
    completed = run_binary(binary, environment,
                           ["verify", str(root_path)], "compact ROOT verifier")
    summary = parse_summary(completed.stdout)
    comparisons = {
        "cells": "cells", "event_gram": "event_gram", "events": "events",
        "sources": "sources", "scientific_content_digest": "scientific_digest",
        "activity_receipts_sha256": "activity_receipts_sha256",
        "block_accounting_sha256": "block_accounting_sha256",
        "compact_domains_sha256": "compact_domains_sha256",
        "input_lineage_sha256": "input_lineage_sha256",
        "metadata_sha256": "metadata_sha256",
        "embedded_receipt_sha256": "embedded_receipt_sha256",
        "analysis_request_sha256": "analysis_sha256",
        "parent_plan_digest": "plan_digest",
        "parent_map_digest": "map_digest",
        "parent_shard_set_digest": "parent_shard_set_digest",
        "reducer_build_id": "build_id",
    }
    for receipt_key, summary_key in comparisons.items():
        if scientific.get(receipt_key) != summary[summary_key]:
            raise ValueError("compact ROOT scientific digest/readback differs: {}".format(
                receipt_key))
    if receipt["state"] != summary["publication_state"]:
        raise ValueError("compact ROOT publication state differs")
    if (provenance["source_count"] != summary["sources"] or
            provenance["input_bytes"] != summary["input_bytes"]):
        raise ValueError("compact ROOT producer metrics differ")
    if (summary["dynamic_species"] !=
            scientific["compact_domains"]["dynamic_species"]):
        raise ValueError("compact ROOT dynamic-PDG dictionaries differ")
    return receipt, summary


def run(args):
    analyze = analyzer_module()
    plan_path = args.plan.resolve()
    plan = analyze.checked_plan(plan_path)
    analysis, analysis_sha = checked_analysis(args.analysis)
    if (plan["block_assignment"]["count"] !=
            analysis["estimator_policy"]["release_block_count"]):
        raise ValueError("this reducer release requires K=10/dof=9 in every mode")
    analyzed_root = Path(args.analyzed_root or plan["output_root"]).resolve()
    work_root = Path(args.work_root or ROOT / "data/work/reduce").resolve(strict=False)
    output_root = Path(args.output_root or ROOT / "data/work/reduced").resolve(strict=False)
    safe_child(work_root, work_root, "reducer work root")
    safe_child(output_root, output_root, "reducer output root")
    admitted = exact_shard_set(plan, analyzed_root, analyze)
    receipts = [admit_receipt(plan, shard, root_path, receipt_path, analyze)
                for shard, root_path, receipt_path in admitted]
    source_ids = [source_id for shard in plan["shards"]
                  for source_id in shard["source_ids"]]
    if source_ids != list(range(len(plan["sources"]))):
        raise ValueError("source membership is not exact once-only closure")
    publication = publication_state(plan, analyze, args.partial)
    lineage = input_lineage(plan, admitted, receipts)
    validate_input_lineage(lineage)
    parent_digest = parent_shard_set_digest(lineage)
    states, pairs = state_registry(analysis)
    tune_names = [name for name, unused in sorted(
        plan["tune_ordinals"].items(), key=lambda item: item[1])]
    scopes = scopes_for(tune_names, analysis)
    domain_template = compact_domains(
        analysis, analysis_sha, pairs, scopes, "__DOMAIN_DYNAMIC_SPECIES__")
    environment, binary, build = build_reducer(work_root)
    root_path, receipt_path = output_paths(plan, analysis_sha, parent_digest,
                                           output_root)
    safe_child(output_root, root_path, "compact ROOT output")
    safe_child(output_root, receipt_path, "compact receipt output")
    if root_path.exists() and receipt_path.exists():
        if args.no_resume:
            raise ValueError("no-overwrite compact promotion collision")
        verify_output(root_path, receipt_path, args.analysis, work_root)
        print("REUSED ROOT={} RECEIPT={} STATE={}".format(
            root_path, receipt_path, publication))
        return
    root_path.parent.mkdir(parents=True, exist_ok=True)
    if root_path.exists() and not receipt_path.exists():
        if args.no_resume:
            raise ValueError("root-only compact promotion collision")
        completed = run_binary(binary, environment, ["verify", str(root_path)],
                               "root-only recovery verifier")
        summary = parse_summary(completed.stdout)
        validate_summary_binding(summary, plan, analysis_sha, parent_digest,
                                 publication, build["build_id"])
        rebuilt = reduction_receipt(plan, analysis_sha, parent_digest, publication,
                                    root_path, summary, build, 0.0,
                                    len(plan["sources"]),
                                    compact_domains(analysis, analysis_sha, pairs,
                                                    scopes,
                                                    summary["dynamic_species"]),
                                    lineage)
        atomic_json(receipt_path, rebuilt, exclusive=True)
        print("RECOVERED ROOT={} RECEIPT={} STATE={}".format(
            root_path, receipt_path, publication))
        return
    if receipt_path.exists() or root_path.exists():
        raise ValueError("foreign or partial compact final collision")
    staging_root = work_root / "staging"
    staging_root.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="reduce-", dir=str(staging_root)))
    try:
        spec_path = stage / "spec.tsv"
        staged_root = stage / "plot-source.root"
        write_spec(spec_path, plan, admitted, receipts, analysis, analysis_sha,
                   publication, states, pairs, scopes, parent_digest,
                   build["build_id"], domain_template, lineage, parent_digest)
        started = time.monotonic()
        completed = run_binary(binary, environment,
                               ["reduce", str(spec_path), str(staged_root)],
                               "reducer")
        elapsed = time.monotonic() - started
        summary = parse_summary(completed.stdout)
        validate_summary_binding(summary, plan, analysis_sha, parent_digest,
                                 publication, build["build_id"])
        run_binary(binary, environment, ["verify", str(staged_root)],
                   "staged compact verifier")
        if (publication == "PUBLICATION_ELIGIBLE" and
                staged_root.stat().st_size >=
                analysis["compact_storage"]["maximum_complete_default_bytes"]):
            raise ValueError("complete compact ROOT violates strict <50 MiB gate")
        fsync_file(staged_root)
        os.link(str(staged_root), str(root_path))
        fsync_directory(root_path.parent)
        if os.environ.get("HADRONIZATION_REDUCE_FAIL_AFTER_ROOT_PROMOTION") == "1":
            raise ValueError("injected interruption after compact ROOT promotion")
        receipt = reduction_receipt(plan, analysis_sha, parent_digest, publication,
                                    root_path, summary, build, elapsed,
                                    len(plan["sources"]),
                                    compact_domains(analysis, analysis_sha, pairs,
                                                    scopes,
                                                    summary["dynamic_species"]),
                                    lineage)
        atomic_json(receipt_path, receipt, exclusive=True)
        verified, unused_summary = verify_output(root_path, receipt_path,
                                                  args.analysis, work_root)
        del verified, unused_summary
        print("REDUCED ROOT={} RECEIPT={} STATE={} BYTES={} CELLS={} GRAM={}".format(
            root_path, receipt_path, publication, root_path.stat().st_size,
            summary["cells"], summary["event_gram"]))
    finally:
        shutil.rmtree(str(stage), ignore_errors=True)
        if staging_root.exists() and not any(staging_root.iterdir()):
            staging_root.rmdir()


def verify(args):
    receipt, summary = verify_output(args.root.resolve(), args.receipt.resolve(),
                                     args.analysis.resolve(), args.work_root.resolve())
    print("VERIFIED ROOT={} STATE={} CELLS={} GRAM={} SCIENTIFIC_DIGEST={}".format(
        args.root.resolve(), receipt["state"], summary["cells"],
        summary["event_gram"], summary["scientific_digest"]))


def explain(args):
    receipt, unused = verify_output(args.root.resolve(), args.receipt.resolve(),
                                    args.analysis.resolve(), args.work_root.resolve())
    del unused
    print(json.dumps(receipt, sort_keys=True, indent=2))


def parser():
    top = argparse.ArgumentParser(prog="hadronization reduce", description=__doc__)
    sub = top.add_subparsers(dest="command", required=True)
    run_parser = sub.add_parser("run", help="admit one exact plan and reduce all shards")
    run_parser.add_argument("--plan", type=Path, required=True)
    run_parser.add_argument("--analysis", type=Path, default=ANALYSIS)
    run_parser.add_argument("--analyzed-root", type=Path)
    run_parser.add_argument("--work-root", type=Path)
    run_parser.add_argument("--output-root", type=Path)
    run_parser.add_argument("--partial", action="store_true")
    run_parser.add_argument("--no-resume", action="store_true")
    verify_parser = sub.add_parser("verify", help="verify compact physical and scientific identity")
    verify_parser.add_argument("--root", type=Path, required=True)
    verify_parser.add_argument("--receipt", type=Path, required=True)
    verify_parser.add_argument("--analysis", type=Path, default=ANALYSIS)
    verify_parser.add_argument("--work-root", type=Path,
                               default=ROOT / "data/work/reduce")
    explain_parser = sub.add_parser("explain", help="verify and display the compact receipt")
    explain_parser.add_argument("--root", type=Path, required=True)
    explain_parser.add_argument("--receipt", type=Path, required=True)
    explain_parser.add_argument("--analysis", type=Path, default=ANALYSIS)
    explain_parser.add_argument("--work-root", type=Path,
                                default=ROOT / "data/work/reduce")
    return top


def main():
    args = parser().parse_args()
    try:
        if args.command == "run":
            run(args)
        elif args.command == "verify":
            verify(args)
        else:
            explain(args)
        return 0
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        print("ERROR: {}".format(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
