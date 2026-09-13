"""Configuration validation and serialization; scientific predicates live in selection.hpp."""

import copy
import math
import re
import hashlib
import json
from pathlib import Path
import importlib.util
from dataclasses import dataclass
from collections.abc import Mapping
from types import MappingProxyType
_support_spec = importlib.util.spec_from_file_location("query_support", Path(__file__).with_name("support.py"))
support = importlib.util.module_from_spec(_support_spec)
_support_spec.loader.exec_module(support)


def validate_profiles(profiles):
    if not isinstance(profiles, (list, tuple)) or not profiles or len(profiles) > 16:
        raise ValueError("analysis profile list must contain 1..16 profiles")
    identifiers = set()
    for profile in profiles:
        if not isinstance(profile, Mapping) or set(profile) != {
                "id", "trigger_pt", "associate_pt", "relative_pt"}:
            raise ValueError("analysis profile fields differ")
        name = profile["id"]
        if (not isinstance(name, str) or
                re.fullmatch(r"[a-z][a-z0-9_]{0,63}", name) is None or
                name in identifiers):
            raise ValueError("analysis profile IDs are malformed or duplicated")
        identifiers.add(name)
        for role in ("trigger_pt", "associate_pt"):
            cut = profile[role]
            if cut is None:
                continue
            if (not isinstance(cut, Mapping) or set(cut) != {"operator", "value"} or
                    cut["operator"] != ">=" or
                    type(cut["value"]) not in (int, float) or
                    not math.isfinite(cut["value"]) or cut["value"] < 0):
                raise ValueError("released pT thresholds require >= and a finite nonnegative value")
        trigger, associate = profile["trigger_pt"], profile["associate_pt"]
        if trigger is not None and associate is not None and trigger["value"] < associate["value"]:
            raise ValueError("configured trigger minimum must be at least associate minimum")
        if profile["relative_pt"] is not None:
            raise ValueError("eventwise relative pT selection is not a released observable")
    return profiles


# Historical rectangular profiles remain readable for immutable old workspaces.
# The current paper profile has no final-hadron pT floor.
def phase_a_profile_kind(profile):
    validate_profiles([profile])
    if (profile["id"] == "inclusive" and profile["trigger_pt"] is None and
            profile["associate_pt"] is None and profile["relative_pt"] is None):
        return "inclusive"
    if (profile["id"] != "inclusive" and
            profile["trigger_pt"] is not None and
            profile["associate_pt"] is not None and
            profile["trigger_pt"]["operator"] == ">=" and
            profile["associate_pt"]["operator"] == ">=" and
            profile["relative_pt"] is None):
        return "ordered_minima"
    raise ValueError("Phase-A profile must be inclusive or a configured independent-minima rectangle")

def validate_phase_a_profiles(profiles, pt_edges=None):
    validate_profiles(profiles)
    kinds = [phase_a_profile_kind(profile) for profile in profiles]
    if kinds[0] != "inclusive" or any(kind != "ordered_minima" for kind in kinds[1:]):
        raise ValueError("Phase-A profiles require inclusive first followed by supported selections")
    if not isinstance(pt_edges, (list, tuple)) or len(pt_edges) < 2 or any(
            type(edge) not in (int, float) or not math.isfinite(edge) for edge in pt_edges) or any(
            a >= b for a, b in zip(pt_edges, pt_edges[1:])):
        raise ValueError("Phase-A release requires a finite ordered pT axis")
    allowed = set(pt_edges[:-1])
    for profile in profiles[1:]:
        if any(profile[role]["value"] not in allowed for role in
               ("trigger_pt", "associate_pt")):
            raise ValueError("Phase-A rectangle minimum is not an exact supported regular-bin lower edge")
    return profiles


def profile_tokens(profile):
    validate_profiles([profile])
    def threshold(role):
        cut = profile[role]
        return "NONE" if cut is None else cut["operator"] + repr(float(cut["value"]))
    return [threshold("trigger_pt"), threshold("associate_pt"),
            profile["relative_pt"] or "NONE"]


def projection_contract(profile, engine, pt_edges=None):
    validate_profiles([profile])
    validate_phase_a_profiles(
        [profile] if phase_a_profile_kind(profile) == "inclusive" else
        [{"id": "inclusive", "trigger_pt": None, "associate_pt": None,
          "relative_pt": None}, profile], pt_edges)
    if engine not in {"exact_rows", "aligned_sparse"}:
        raise ValueError("unknown query engine")
    if engine == "aligned_sparse":
        for role in ("trigger_pt", "associate_pt"):
            cut = profile[role]
            if cut is not None and (cut["operator"] != ">=" or pt_edges is None or cut["value"] not in pt_edges[:-1]):
                raise ValueError("pT endpoint is not an exact aligned sparse boundary; use exact rows")
    return {"engine": engine, "profile": profile,
            "exactness": "exact_binary64_rows" if engine == "exact_rows" else "aligned_rectangles_only",
            "trigger_denominator": "structural triggers passing trigger cuts, independent of associates"}


def primitive_routes(analysis, archived, backend):
    """Choose exact primitive sources without approximating an endpoint or diagonal."""
    validate_phase_a_profiles(analysis["profiles"], analysis["axes"]["pt"]["edges"])
    if backend not in {"exact_rows", "aligned_sparse", "auto"}:
        raise ValueError("unknown primitive backend")
    result = []
    for profile in analysis["profiles"]:
        eta = analysis["pair_acceptance"]["eta"]["value"]
        axes_match = all(analysis["axes"][name] == archived["axes"][name]
                         for name in ("pt", "eta", "dphi", "activity"))
        eta_axis = archived["axes"]["eta"]
        aligned = axes_match and eta_axis["low"] == -eta and eta_axis["high"] == eta
        cuts = [profile["trigger_pt"]]
        cuts.append(profile["associate_pt"])
        for cut in cuts:
            aligned = aligned and (cut is None or
                (cut["operator"] == ">=" and cut["value"] in archived["axes"]["pt"]["edges"][:-1]))
        if backend == "aligned_sparse" and not aligned:
            raise ValueError("profile {} has no exact aligned sparse route; use exact_rows or auto".format(profile["id"]))
        sparse = aligned and backend != "exact_rows"
        result.append({
            "profile": profile["id"],
            "backend": "aligned_sparse" if sparse else "exact_rows",
            "pair_object": "sparse_pairs" if sparse else "pairs",
            "trigger_object": "sparse_triggers" if sparse else "triggers",
            "exactness": "aligned_rectangles" if sparse else "exact_binary64_rows",
            "primitive_projections": [2, 3, 4, 5],
            "diagnostics": "exact_row_sumabs_fills_and_event_gram",
        })
    return result


def authenticated_routes(analysis, routes, activity_sparse, observations):
    """Bind actual reader plans to independently verified input object domains.

    Object digests across shards are ordered composites of (ordinal, digest).
    Counts describe the observed input domain, not physical I/O operations.
    """
    def sha(value):
        return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")).hexdigest()
    def bound(cut=None, eta=None):
        return dict(low=None if cut is None and eta is None else float(-eta if eta is not None else cut["value"]).hex(),
                    high=None if eta is None else float(eta).hex(),
                    low_operator=None if cut is None and eta is None else "GE" if eta is not None or cut["operator"] == ">=" else "GT",
                    high_operator=None if eta is None else "LE", units="" if eta is not None else "GeV", domain="PHYSICAL")
    def record(family, profile, objects, route, exactness, predicate, axes=(), diagnostics=()):
        sparse = route in {"NATIVE_ALIGNED_SPARSE", "EXACT_PREFILTERED_SPARSE"}
        digests, cells, rows = [], 0, 0
        for name in objects:
            key = "sparse:" + name[len("sparse_"):] if name.startswith("sparse_") else "tree:" + name
            digests.append(sha([dict(ordinal=o["ordinal"], digest=o["digests"][key]) for o in observations]))
            for observation in observations:
                count = observation["counts"][key]
                if sparse: cells += count
                else: rows += count
        return dict(primitive_family=family, profile_id=profile, source_kind="QUERY_ROOT", route=route, exactness=exactness,
            root_object_names=list(objects), object_content_digests=digests, predicate_sha256=sha(predicate),
            resolved_axis_selection=list(axes), diagnostic_readers=list(diagnostics), observed_input_cells=cells, observed_input_rows=rows)
    result = [record("activity", None, ["sparse_activity" if activity_sparse else "events"],
        "NATIVE_ALIGNED_SPARSE" if activity_sparse else "EXACT_ROWS", "ALIGNED_RECTANGLE" if activity_sparse else "BINARY64_ROWS",
        dict(activities=analysis["activities"], axis=analysis["axes"]["activity"]), diagnostics=[dict(purpose="source_accounting_and_sumabs_fills", route="EXACT_ROWS", objects=["events", "sources", "source_blocks"])])]
    eta = analysis["pair_acceptance"]["eta"]["value"]
    for plan in routes:
        profile = next(p for p in analysis["profiles"] if p["id"] == plan["profile"])
        sparse = plan["backend"] == "aligned_sparse"
        for family in ("pairs", "triggers"):
            pair = family == "pairs"
            axes = []
            for role in (("trigger_pt", "associate_pt") if pair else ("trigger_pt",)):
                cut = profile[role]
                included = [i+1 for i, edge in enumerate(analysis["axes"]["pt"]["edges"][:-1])
                            if cut is None or edge >= cut["value"]] if sparse else []
                axes.append(dict(axis_id=role, predicate=bound(cut), included_regular_bins=included,
                    include_underflow=False, include_overflow=sparse, endpoint_adjustment="NONE"))
            for role in (("trigger_eta", "associate_eta") if pair else ("trigger_eta",)):
                axes.append(dict(axis_id=role, predicate=bound(eta=eta), included_regular_bins=list(range(1,analysis["axes"]["eta"]["bins"]+1)) if sparse else [],
                    include_underflow=False, include_overflow=False, endpoint_adjustment="ARCHIVED_INCLUSIVE_HIGH" if sparse else "NONE"))
            result.append(record(family, profile["id"], [plan["pair_object" if pair else "trigger_object"]],
                "NATIVE_ALIGNED_SPARSE" if sparse else "EXACT_ROWS",
                "ALIGNED_RECTANGLE" if sparse else "BINARY64_ROWS",
                dict(profile=profile if pair else {k: profile[k] for k in ("id", "trigger_pt")}, pair_acceptance=analysis["pair_acceptance"]), axes,
                [dict(purpose="sumabs_fills_event_gram", route="EXACT_ROWS", objects=["events", "heavy", family, "origins"])]))
    for family, objects in [("kinematics", ["events", "heavy"]), ("closure", ["events", "heavy", "closure"]),
                            ("diagnostics", ["events", "sources", "source_blocks", "source_counts", "event_ranges", "heavy", "triggers", "pairs", "origins", "closure", "constituents", "event_compatibility"])]:
        result.append(record(family, None, objects, "EXACT_ROWS", "BINARY64_ROWS", dict(family=family, analysis=analysis)))
    return result


def checked_analysis(path):
    path = path.resolve()
    support.regular_file(path, "analysis request")
    payload = support.json_file(path)
    # One immutable accepted historical request, not an open-ended v1 bypass.
    # Keep its schema/body/SHA intact so archived receipts are never rewritten.
    if payload.get("schema") == "hadronization_downstream_analysis_request_v1":
        historical_sha = "2d386155e65a35951dbd9545b9f157b2f643b20ab81282cc0a38d2fa3fb5e4f9"
        if support.sha_file(path) != historical_sha:
            raise ValueError("untrusted historical analysis identity")
        raise ValueError("historical analysis request is not a released Phase-A model")
    version = payload.get("version")
    if version not in {"2.0.0", "2.1.0", "2.2.0"}:
        raise ValueError("analysis request version differs")
    d0_default = version in {"2.1.0", "2.2.0"}
    expected = {
        "schema", "version", "base_study", "lossless_input", "axes",
        "profiles", "pair_acceptance", "activities", "percentile_intervals",
        "integrated_interval", "activity_policy", "pair_query_registry",
        "correlations", "projection_recipes", "g9_species_pdgs",
        "estimator_policy", "compact_domain_registries", "compact_storage",
    }
    if d0_default:
        expected.add("paper_defaults")
    support.exact_keys(payload, expected, "analysis request")
    if payload["schema"] != "hadronization_downstream_analysis_request_v2":
        raise ValueError("analysis request schema differs")
    selected_charm = 411
    if d0_default:
        paper = payload["paper_defaults"]
        support.exact_keys(paper, {"charm_meson_pdg", "selectable_charm_meson_pdgs",
                                   "historical_charm_meson_pdg", "p8_charm_tuple"},
                           "Phase-A paper charm recipe")
        selected_charm = paper["charm_meson_pdg"]
        if (type(selected_charm) is not int or selected_charm not in (421, 411) or
                paper["selectable_charm_meson_pdgs"] != [421, 411] or
                paper["historical_charm_meson_pdg"] != 411 or
                paper["p8_charm_tuple"] != [selected_charm, -4122, -selected_charm]):
            raise ValueError("Phase-A paper charm recipe differs")
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
    study = support.ROOT / "config/study.json"
    if support.sha_file(study) != payload["base_study"]["sha256"]:
        raise ValueError("accepted base-study bytes differ")
    validate_phase_a_profiles(payload["profiles"], payload["axes"]["pt"]["edges"])
    if version in {"2.0.0", "2.1.0"} and (len(payload["profiles"]) < 2 or any(
            phase_a_profile_kind(profile) != "ordered_minima"
            for profile in payload["profiles"][1:])):
        raise ValueError("historical analysis version requires aligned rectangular profiles")
    # The repository-owned v2.2 default has only inclusive. A separately
    # hashed request may add named, independent-minima rectangles.
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
    support.exact_keys(axes, {"activity", "dphi", "eta", "phi", "pt"},
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
    support.exact_keys(axes["pt"], {"edges", "endpoint_rule"}, "analysis pT axis")
    pt_edges = axes["pt"]["edges"]
    if (not isinstance(pt_edges, list) or len(pt_edges) < 2 or
            any(type(value) not in (int, float) or not math.isfinite(value)
                for value in pt_edges) or
            any(float(pt_edges[index]) >= float(pt_edges[index + 1])
                for index in range(len(pt_edges) - 1)) or
            axes["pt"]["endpoint_rule"] !=
            "low inclusive, high inclusive; underflow and overflow retained"):
        raise ValueError("analysis pT axis differs")
    acceptance = payload["pair_acceptance"]
    support.exact_keys(acceptance, {"eta", "roles", "dphi_sign"}, "analysis pair acceptance")
    support.exact_keys(acceptance["eta"], {"operator", "value"}, "analysis pair eta selection")
    eta_max = acceptance["eta"]["value"]
    if (acceptance["roles"] != "ordered structural trigger and associate" or
            acceptance["dphi_sign"] != "trigger_phi-associate_phi" or
            acceptance["eta"]["operator"] != "abs<=" or
            type(eta_max) not in (int, float) or not math.isfinite(eta_max) or eta_max <= 0):
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
    support.exact_keys(query, {"expansion", "trigger_pdgs", "associate_pdgs",
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
    if d0_default:
        for pdg in (421, -421, 411, -411):
            if pdg not in triggers or pdg not in associates["charm"]:
                raise ValueError("signed D0/D+ query domain differs")
        if references["4122"] != -selected_charm or references["-4122"] != selected_charm:
            raise ValueError("selected charm-baryon meson reference/sign differs")
    correlations = payload["correlations"]
    support.exact_keys(correlations, {"tunes", "identities", "components",
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
    if d0_default and identities != [
            [521, -521], [5122, 521],
            [selected_charm, -selected_charm], [4122, -selected_charm]]:
        raise ValueError("selected charm correlations differ")
    expected_recipes = [
        "G1_activity_eta1_eta4",
        ("G9_direct_primary_selected_no_pt_floor_eta4" if version == "2.2.0"
         else "G9_direct_primary_selected_strict_pt0p15_eta4"),
        "T1_all_final_heavy_no_acceptance", "ordered_pair_scalars",
        "configured_dphi_correlations", "origin_integrated",
        "closure_full_visible_eta4_no_associate_pt_floor",
        "closure_species_integrated", "closure_category_dphi_integrated",
    ]
    if payload["projection_recipes"] != expected_recipes:
        raise ValueError("analysis projection recipes differ")
    g9 = payload["g9_species_pdgs"]
    if d0_default:
        historical_other_eight = {-5212, -5122, -4122, -521,
                                  521, 4122, 5122, 5212}
        if (not isinstance(g9, list) or len(g9) not in (10, 12) or
                any(type(pdg) is not int for pdg in g9)):
            raise ValueError("analysis G9 selected signed species differ")
        configured = set(g9)
        if (len(configured) != len(g9) or
                g9 != sorted(g9) or
                not historical_other_eight <= configured or
                {selected_charm, -selected_charm} - configured or
                configured - (historical_other_eight | {421, -421, 411, -411}) or
                any((pdg not in triggers and pdg not in associates["charm"] and
                     pdg not in associates["beauty"])
                    for pdg in g9)):
            raise ValueError("analysis G9 selected signed species differ")
    elif g9 != [-5212, -5122, -4122, -521, -411, 411, 521, 4122, 5122, 5212]:
        raise ValueError("historical analysis G9 registry differs")
    policy = payload["estimator_policy"]
    support.exact_keys(policy, {"id", "release_block_count", "variance_dof",
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
    support.exact_keys(registries, {"projection_ids", "origin_ids",
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
    support.exact_keys(storage, {"schema", "tables", "metadata_objects",
                         "compression", "maximum_complete_default_bytes",
                         "sparse_rule", "pooled_copy", "summation"},
               "analysis compact storage")
    if (storage.get("schema") != "hadronization_compact_plot_source_v1" or
            storage.get("tables") != ["cells", "event_gram"] or
            storage.get("metadata_objects") != ["metadata", "receipt"] or
            storage.get("compression") != {"algorithm": "ZSTD", "level": 5} or
            storage.get("maximum_complete_default_bytes") != 85 * 1024 * 1024 or
            storage.get("sparse_rule") !=
            "absence inside a declared domain is exact zero; absence outside is "
            "NOT_MATERIALIZED" or storage.get("pooled_copy") is not False or
            storage.get("summation") !=
            "Neumaier compensated binary64 with recorded absolute sums and "
            "operation counts"):
        raise ValueError("analysis compact-storage contract differs")
    return payload, support.sha_file(path)


def select_charm_meson_recipe(analysis, meson_pdg, include_alternate_g9=False):
    """Derive one coherent D0/D+ analysis request before hashing or projection."""
    if (analysis.get("version") not in {"2.1.0", "2.2.0"} or type(meson_pdg) is not int or
            meson_pdg not in (421, 411) or type(include_alternate_g9) is not bool):
        raise ValueError("unsupported Phase-A charm-meson recipe")
    selected = copy.deepcopy(analysis)
    selected["paper_defaults"]["charm_meson_pdg"] = meson_pdg
    selected["paper_defaults"]["p8_charm_tuple"] = [meson_pdg, -4122, -meson_pdg]
    selected["pair_query_registry"]["reference_meson_by_trigger"].update({
        "4122": -meson_pdg, "-4122": meson_pdg})
    selected["correlations"]["identities"] = [
        [521, -521], [5122, 521], [meson_pdg, -meson_pdg],
        [4122, -meson_pdg]]
    other_eight = {-5212, -5122, -4122, -521, 521, 4122, 5122, 5212}
    species = {meson_pdg, -meson_pdg}
    if include_alternate_g9:
        alternate = 411 if meson_pdg == 421 else 421
        species.update((alternate, -alternate))
    selected["g9_species_pdgs"] = sorted(other_eight | species)
    return selected


def compatible_interpretation(construction, requested):
    """Prove that a new pinned recipe uses only content retained by a query.

    The query keeps its original whole-file analysis digest.  Only supported
    post-query profiles and the tune-local percentile recipe are interpretive.
    Every other normalized field remains construction content or provenance.
    """
    if not isinstance(construction, Mapping) or not isinstance(requested, Mapping):
        raise ValueError("query/request normalized model is absent")
    if set(construction) != set(requested):
        raise ValueError("query/request normalized model fields differ")
    for field in construction:
        if field in {"profiles", "percentile_intervals"}:
            continue
        if construction[field] != requested[field]:
            raise ValueError("requested analysis changes unretained query content: " + field)
    validate_phase_a_profiles(requested["profiles"], construction["axes"]["pt"]["edges"])
    if requested["profiles"][0] != construction["profiles"][0]:
        raise ValueError("requested analysis changes inclusive query profile")
    # Both validated models have contiguous percentile partitions.  The
    # retained event-activity support permits a new boundary calculation.
    return {"schema": "hadronization_query_interpretation_compatibility_v1",
            "construction_content_sha256": hashlib.sha256(
                json.dumps({key: construction[key] for key in construction
                            if key not in {"profiles", "percentile_intervals"}},
                           sort_keys=True, separators=(",", ":"),
                           ensure_ascii=True).encode("ascii")).hexdigest(),
            "profile_ids": [profile["id"] for profile in requested["profiles"]],
            "percentile_intervals": requested["percentile_intervals"]}


def state_registry(analysis):
    """Expand signed structural pair identities from the one study model."""
    study = support.json_file(support.ROOT / "config/study.json")
    states = study["selected_states"]
    by_pdg = {item["pdg"]: item for item in states}
    query = analysis["pair_query_registry"]
    pairs = []
    for trigger in query["trigger_pdgs"]:
        if trigger not in by_pdg or not by_pdg[trigger]["pair_analysis_eligible"]:
            raise ValueError("pair trigger registry is not structurally eligible")
        sector = by_pdg[trigger]["sector"]
        trigger_charge = by_pdg[trigger]["qc"] if sector == "charm" else by_pdg[trigger]["qb"]
        for associate in query["associate_pdgs"][sector]:
            state = by_pdg.get(associate)
            if state is None or state["sector"] != sector:
                raise ValueError("pair associate registry differs from structural states")
            associate_charge = state["qc"] if sector == "charm" else state["qb"]
            pairs.append({"id": len(pairs), "trigger_pdg": trigger,
                          "associate_pdg": associate,
                          "sign": -1 if trigger_charge * associate_charge < 0 else 1,
                          "reference_meson_pdg": int(query["reference_meson_by_trigger"][str(trigger)]),
                          "central_eligible": bool(state["pair_analysis_eligible"]),
                          "sector": sector})
    if len(pairs) != query["expected_count"] or len(pairs) != 300:
        raise ValueError("expanded pair registry is not the required 300 queries")
    return states, pairs


def _freeze(value):
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return value


@dataclass(frozen=True)
class NormalizedModel:
    """Read-only released interpretation; historical study bytes remain separate."""

    analysis: Mapping
    sha256: str

    @property
    def pt_edges(self):
        return self.analysis["axes"]["pt"]["edges"]

    def profile(self, identifier):
        selected = [profile for profile in self.analysis["profiles"] if profile["id"] == identifier]
        if len(selected) != 1:
            raise ValueError("unknown or duplicated analysis profile")
        return selected[0]

    def to_dict(self):
        def thaw(value):
            if isinstance(value, Mapping):
                return {key: thaw(item) for key, item in value.items()}
            if isinstance(value, tuple):
                return [thaw(item) for item in value]
            return value
        return thaw(self.analysis)


def load_normalized(path):
    payload, digest = checked_analysis(Path(path))
    return NormalizedModel(_freeze(payload), digest)
