"""Scientific v2 DTOs and invocation of the sole C++ projection authority.

Python authenticates and decodes ROOT-derived results. It does not evaluate
observable formulas, normalize counts, or reconstruct jackknife covariance.
"""
from dataclasses import dataclass
from functools import cached_property
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
REQUEST_SCHEMA = "hadronization_projection_request_v2"
RESULT_SCHEMA = "hadronization_projection_result_v2"
RESULT_SCHEMA_G9 = "hadronization_projection_result_v3_g9_science"
RESULT_SCHEMA_NATIVE = "hadronization_projection_result_v4"
INTERFACE_SCHEMA = REQUEST_SCHEMA
ESTIMATOR = "pooled_delete_one_source_block_jackknife_v2"
STATUS = "AVAILABLE|AVAILABLE_ZERO_DISPERSION|UNDEFINED|UNSTABLE_DENOMINATOR|WITHHELD_UNCERTAINTY|EMPTY_CLASS|INCOMPLETE_BLOCK_COVERAGE"
ROUTE = "COMPACT_PRIMITIVES|NATIVE_ALIGNED_SPARSE|EXACT_PREFILTERED_SPARSE|EXACT_ROWS"
EXACTNESS = "PREAGGREGATED_REQUEST|ALIGNED_RECTANGLE|EXACT_PREDICATE_THEN_ALIGNED_BINS|BINARY64_ROWS"
PAPER_ROLE_IDS = (
    "multiplicity.composite", "correlations.charm", "correlations.beauty",
    "balancing.integrated.charm", "balancing.integrated.beauty",
    "balancing.activity.charm", "balancing.activity.beauty",
    "balancing.baryon_meson.activity", "spectra.signed_heavy",
    "accounting.natural_final_heavy")
QUANTITIES = {"dphi_per_trigger", "dphi_density_per_trigger", "normalized_distribution", "os_minus_ss_per_trigger", "ratio_to_reference_tune", "baryon_meson_reference_ratio", "baryon_meson_ratio_to_reference_tune", "normalized_spectrum", "spectrum_ratio_to_reference_tune", "raw_count", "raw_weighted_sum", "normalized_yield"}
T1_COMPONENTS = ("hadron_count", "charm_plus_anticharm_constituent_count",
                 "beauty_plus_antibeauty_constituent_count")
COMPONENTS = "OS|SS|OS_MINUS_SS|NONE|" + "|".join(T1_COMPONENTS)
PAPER_CHARM_ASSOCIATES = (-411, -421, -431, -4122,
                          -4112, -4212, -4222, -4132, -4232, -4312, -4322)
PAPER_BEAUTY_ASSOCIATES = {
    521: (-521, -511, -531, -541, 5122, 5112, 5212, 5222, 5132, 5232, 5312, 5322),
    5122: (521, 511, 531, 541, -5122, -5112, -5212, -5222, -5132, -5232, -5312, -5322),
}


def paper_p8_pair(trigger, associate, reference):
    """Require the signed meson parent of the selected baryon channel."""
    if trigger in (411, 421):
        return associate == -4122 and reference == -trigger
    return (trigger, associate, reference) == (521, 5122, -521)


def paper_baryon_meson_channels(analysis, charm):
    """Select Lambda, Sigma and Xi ratios with one common meson per sector."""
    states, pairs = _query_model().observable_pairs(analysis, 'projection_formulas_v4')
    by_pdg = {state['pdg']: state for state in states}
    associates = {charm: PAPER_CHARM_ASSOCIATES,
                  4122: PAPER_CHARM_ASSOCIATES, **PAPER_BEAUTY_ASSOCIATES}
    channels = []
    for trigger in (charm, 4122, 521, 5122):
        for associate in associates[trigger]:
            if by_pdg[associate]['kind'] != 'baryon':
                continue
            matches = [pair for pair in pairs
                       if pair['trigger_pdg'] == trigger and
                       pair['associate_pdg'] == associate and
                       pair['sign'] == -1]
            if len(matches) != 1:
                raise ValueError('paper baryon ratio lacks an eligible OS pair')
            channels.append([trigger, associate,
                             matches[0]['reference_meson_pdg']])
    return channels


def checked_baryon_meson_channels(selection, pairs, states):
    """Bind an explicit ratio domain to eligible opposite-flavour states."""
    channels = selection.get('baryon_meson_channels')
    if channels is None:
        return {(pair['trigger_pdg'], pair['associate_pdg'],
                 pair['reference_meson_pdg']) for pair in pairs
                if pair['trigger_pdg'] in selection['baryon_meson_trigger_pdgs']
                and paper_p8_pair(pair['trigger_pdg'], pair['associate_pdg'],
                                  pair['reference_meson_pdg'])}
    if (not isinstance(channels, list) or not channels or
            any(not isinstance(row, list) or len(row) != 3 or
                any(type(pdg) is not int for pdg in row) for row in channels)):
        raise ValueError('baryon/meson channels require signed integer triples')
    selected = {tuple(row) for row in channels}
    if len(selected) != len(channels):
        raise ValueError('duplicate baryon/meson channel')
    registry = {state['pdg']: state for state in states}
    os_pairs = {(pair['trigger_pdg'], pair['associate_pdg']): pair
                for pair in pairs if pair['sign'] == 'OS'}
    for trigger, associate, reference in selected:
        pair = os_pairs.get((trigger, associate))
        if (trigger not in selection['baryon_meson_trigger_pdgs'] or
                pair is None or (trigger, reference) not in os_pairs or
                registry[associate]['kind'] != 'baryon' or
                registry[reference]['kind'] != 'meson' or
                reference != pair['reference_meson_pdg']):
            raise ValueError('baryon/meson channel differs from signed registry')
    return selected


G9_PT_EDGES = tuple([i / 2 for i in range(101)] +
                    [60,75,100,150,250,500,1000,2000,4000,7000])


def expected_point_units(quantity):
    return {"dphi_per_trigger": "per_trigger_per_bin",
            "dphi_density_per_trigger": "per_trigger_per_radian",
            "normalized_spectrum": "probability_per_bin",
            "raw_count": "count", "raw_weighted_sum": "weighted_count",
            "normalized_yield": "per_event"}.get(quantity, "1")


def observed_support(request, points, materialization):
    present = {canonical(item['point_key']): item['status'] == 'PRESENT'
               for item in materialization}
    by_tune = {}
    for point in points:
        key = point['key']; curve = key['curve']
        if curve['role_id'] != 'multiplicity.composite' or curve['quantity'] != 'normalized_distribution' or curve['reference_tune_id'] is not None:
            continue
        by_tune.setdefault(curve['tune_id'], []).append(point)
    result = []
    for tune in request['scope']['ordered_tunes']:
        selected = by_tune.get(tune, [])
        complete = bool(selected) and all(present[canonical(p['key'])] for p in selected)
        nonzero = sorted(p['key']['bins'][0]['index'] for p in selected
                         if p['center'] is not None and number(p['center']) != 0)
        if not complete:
            nonzero = []
        result.append(dict(role_id='multiplicity.composite', tune_id=tune,
            axis_id='nch', nonzero_bins=nonzero,
            first_nonzero=nonzero[0] if nonzero else None,
            last_nonzero=nonzero[-1] if nonzero else None,
            status='OBSERVED' if complete else 'NOT_MATERIALIZED'))
    return result


def category_order(request, label_by_pdg):
    pair_order = [(p['trigger_pdg'], p['associate_pdg'])
                  for p in request['scope']['ordered_associate_pairs']]
    result = []
    for role in request['scope']['roles']:
        role_id = role['role_id']
        if not role_id.startswith('balancing.'):
            continue
        keys = role['required_curve_keys']
        for trigger in request['scope']['ordered_triggers']:
            available = {c['associate_pdg'] for c in keys
                         if c['trigger_pdg'] == trigger and c['associate_pdg'] is not None}
            if not available:
                continue
            if role_id in ('balancing.integrated.beauty','balancing.activity.beauty'):
                order = [a for a in PAPER_BEAUTY_ASSOCIATES.get(trigger, ()) if a in available]
            else:
                order = list(dict.fromkeys(a for t,a in pair_order if t == trigger and a in available))
            if set(order) != available or any(a not in label_by_pdg for a in order):
                raise ValueError('category order/registry differs from requested signed keys')
            result.append(dict(role_id=role_id,trigger_pdg=trigger,
                               associate_pdgs=order,
                               labels=[label_by_pdg[a] for a in order]))
    return result


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode("ascii")).hexdigest()


def file_digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def hex64(value):
    if type(value) not in (float, int) or not math.isfinite(value):
        raise ValueError("projection binary64 value is not finite")
    return float(value).hex()


def number(token):
    if token is None:
        return None
    validate(token, "Hex64", "binary64")
    return float.fromhex(token)


def nullable(spec):
    return ("nullable", spec)


# Exact accepted v2 IDL: nullable fields remain mandatory. Unknown keys fail.
SCHEMAS = {
    "SourceProfile": dict(id="Id", trigger_pt=nullable(dict(operator=">|>=", value="Finite")), associate_pt=nullable(dict(operator=">|>=", value="Finite")), relative_pt=nullable("=trigger_pt>associate_pt")),
    "SourceSelectionDefinitions": dict(profiles=["SourceProfile"], pair_acceptance=dict(eta=dict(operator="=abs<=", value="Finite"), roles="=ordered structural trigger and associate", dphi_sign="=trigger_phi-associate_phi"), axes=dict(pt=dict(edges=["Finite"], endpoint_rule="Text"), eta=dict(bins="Count", low="Finite", high="Finite", endpoint_rule="Text")), structural_registry_sha256="Digest"),
    "RangePredicate": dict(low=nullable("Hex64"), low_operator=nullable("GT|GE"), high=nullable("Hex64"), high_operator=nullable("LT|LE"), units="Text", domain="=PHYSICAL"),
    "Profile": dict(id="Id", trigger_pt="RangePredicate", associate_pt="RangePredicate", trigger_eta="RangePredicate", associate_eta="RangePredicate", relative_pt="NONE|TRIGGER_GT_ASSOCIATE", minimum_hierarchy="NONE|TRIGGER_MIN_GT_ASSOCIATE_MIN|TRIGGER_MIN_GE_ASSOCIATE_MIN", structural_acceptance_id="Id", origin_filter=nullable(["Id"]), category_filter=nullable(["Id"])),
    "ActivityRequest": dict(semantic_id="Id", definition_digest="Digest", stored_field="Id", eta_window="Hex64", charged="True", final="True", exclude_heavy_constituents="True", pt="RangePredicate"),
    "ClassRequest": dict(id="Int", kind="INTEGRATED|TUNE_LOCAL_PERCENTILE|ABSOLUTE_INTEGER", percentile_interval=nullable(["Hex64"]), integer_interval=nullable(["Int"]), boundary_policy_id="Id"),
    "AxisRequest": dict(id="Id", variable="Id", units="Text", edges=["Hex64"], low_endpoint="INCLUSIVE|EXCLUSIVE", high_endpoint="INCLUSIVE|EXCLUSIVE", underflow="RETAIN|REJECT", overflow="RETAIN|REJECT", angular_wrap=nullable(dict(low="Hex64", high="Hex64"))),
    "PairKey": dict(trigger_pdg="PDG", associate_pdg="PDG", sector="CHARM|BEAUTY", sign="OS|SS", reference_meson_pdg="PDG"),
    "PanelScientificKey": dict(role_id="Id", trigger_pdg=nullable("PDG"), quantity="Quantity", component=COMPONENTS),
    "CurveKey": dict(role_id="Id", tune_id="Id", reference_tune_id=nullable("Id"), profile_id=nullable("Id"), activity_id=nullable("Id"), class_id=nullable("Int"), trigger_pdg=nullable("PDG"), associate_pdg=nullable("PDG"), reference_pdg=nullable("PDG"), quantity="Quantity", component=COMPONENTS, axis_id=nullable("Id")),
    "PointKey": dict(curve="CurveKey", bins=[dict(axis_id="Id", index="Int", low=nullable("Hex64"), high=nullable("Hex64"), flow="REGULAR|UNDERFLOW|OVERFLOW")]),
    "RoleRequest": dict(role_id="Id", ordered_panels=["PanelScientificKey"], required_curve_keys=["CurveKey"]),
    "ObservableRequest": dict(quantity="Quantity", formula_version="Id", output_units="Text", component=COMPONENTS, joint_point_domain=["PointKey"]),
    "CovarianceRequest": dict(id="Id", ordered_point_keys=["PointKey"], representation="DENSE|DELETE_ONE_FACTORS", required_cross_groups=["Id"]),
    "Member": dict(source_id="Count", tune_id="Id", logical_id="Count", accepted_attempt="Count", block_id="Count", successful_events="Count", source_root_sha256="Digest", source_scientific_digest="Digest", receipt_sha256="Digest"),
    "TuneCount": dict(tune_id="Id", count="Count"),
    "SourceSelection": dict(campaign_id="Id", campaign_descriptor_sha256="Digest", accepted_manifest_sha256="Digest", accepted_plan_digest="Digest", accepted_map_digest="Digest", members=["Member"], selected_members_sha256="Digest", expected_events_by_tune=["TuneCount"], provenance_parent_ids=["Digest"]),
    "ProjectionRequest": dict(schema="="+REQUEST_SCHEMA, science_contract=dict(analyzer_schema="Id", structural_registry_sha256="Digest", estimator_policy_id="="+ESTIMATOR, formula_contract_version="projection_formulas_v2|projection_formulas_v3|projection_formulas_v4"), sources="SourceSelection", scope=dict(mode="PAPER|EXPLORATORY", roles=["RoleRequest"], ordered_tunes=["Id"], reference_tune=nullable("Id"), ordered_triggers=["PDG"], ordered_associate_pairs=["PairKey"]), profiles=["Profile"], activity="ActivityRequest", classes=["ClassRequest"], axes=["AxisRequest"], observables=["ObservableRequest"], statistics=dict(block_assignment_sha256="Digest", block_ids=["Count"], expected_K="Count", uncertainty="=FINITE_MC_DELETE_ONE", covariance_groups=["CovarianceRequest"]), execution=dict(backend_policy="AUTO|EXACT_ROWS|REQUIRE_NATIVE", permitted_routes=[ROUTE], required_capabilities=["Id"]), completion=dict(require_campaign_complete="Bool", require_all_requested_points="True", permitted_scientific_statuses=[STATUS]), bindings=dict(analysis_config_sha256="Digest", particle_registry_sha256="Digest", activity_definition_sha256="Digest", expected_source_content_sha256="Digest"), presentation_binding=dict(layout_contract_version="Id", plot_config_sha256="Digest")),
    "ResolvedClass": dict(tune_id="Id", activity_id="Id", class_id="Int", requested="ClassRequest", actual_integer_low="Int", actual_integer_high="Int", event_weight="Hex64", events="Count", empty="Bool", boundary_status="Id", coverage_status="Id", boundary_receipt_sha256="Digest"),
    "AxisSelection": dict(axis_id="Id", predicate="RangePredicate", included_regular_bins=["Count"], include_underflow="Bool", include_overflow="Bool", endpoint_adjustment="NONE|ARCHIVED_INCLUSIVE_HIGH"),
    "PrimitiveRoute": dict(primitive_family="Id", profile_id=nullable("Id"), source_kind="COMPACT_ROOT|QUERY_ROOT|ACCEPTED_ANALYZED_ROOT|TEST_ONLY_SYNTHETIC", route=ROUTE, exactness=EXACTNESS, root_object_names=["Id"], object_content_digests=["Digest"], predicate_sha256="Digest", resolved_axis_selection=["AxisSelection"], diagnostic_readers=[dict(purpose="Id", route=ROUTE, objects=["Id"])], observed_input_cells="Count", observed_input_rows="Count"),
    "ParentReceipt": dict(natural_key="Id", exists="Bool", materialized="Bool", content_digest="Digest", coverage_status="Id"),
    "DenominatorReceipt": dict(natural_key="Id", pooled_value=nullable("Hex64"), status=STATUS, retained_after_algebra="Bool", delete_one_statuses=[STATUS], policy_id="Id"),
    "BlockPrimitiveReceipt": dict(tune_id="Id", block_id="Count", additive_components=[dict(id="Id", value="Hex64")], events="Count", sumw="Hex64", sumw2="Hex64", sumabsw="Hex64", fills="Count", event_gram_content_digest="Digest"),
    "PointResult": dict(key="PointKey", semantic_id="Digest", units="Text", center=nullable("Hex64"), center_status=STATUS, standard_error=nullable("Hex64"), variance=nullable("Hex64"), uncertainty_status=STATUS, reasons=["Id"], semantic_parents=["ParentReceipt"], denominator_receipts=["DenominatorReceipt"], block_values=["BlockPrimitiveReceipt"], covariance_group_ids=["Id"]),
    "DeleteOneFamily": dict(tune_id="Id", source_family_digest="Digest", block_ids=["Count"], complements=[[nullable("Hex64")]], leave_mean=[nullable("Hex64")], covariance_prefactor="Hex64"),
    "CovarianceDiagnostics": dict(symmetry_max_abs="Hex64", minimum_eigenvalue=nullable("Hex64"), maximum_null_residual=nullable("Hex64"), accepted_rounding_bound="Hex64", valid_dimension="Count", method_id="Id", status="PASS|FAIL|NOT_EVALUATED"),
    "CovarianceResult": dict(id="Id", ordered_point_keys=["PointKey"], valid_mask=["Bool"], units_by_point=["Text"], status="AVAILABLE_FULL|AVAILABLE_PARTIAL|UNAVAILABLE", estimator_policy_id="="+ESTIMATOR, K="Count", dof="Count", independent_families=["DeleteOneFamily"], representation="DENSE|DELETE_ONE_FACTORS", dense_rows=nullable([[nullable("Hex64")]]), factors_root_object=nullable("Id"), content_sha256="Digest", rank_bound="Count", numerical_diagnostics="CovarianceDiagnostics"),
    "RuntimeIdentity": dict(os="Text", architecture="Text", root_version="Text", compiler_id="Text", compiler_version="Text", effective_cpp_standard="Text", compile_flags=["Text"], link_flags=["Text"], dependency_recipe_sha256="Digest"),
    "Provenance": dict(campaign_descriptor_sha256="Digest", source_members_sha256="Digest", analysis_config_sha256="Digest", particle_registry_sha256="Digest", selection_definitions_sha256="Digest", source_selection_definitions="SourceSelectionDefinitions", activity_definition_sha256="Digest", producer_commit="GitOid", integrated_science_commit="GitOid", formula_source_sha256="Digest", statistics_source_sha256="Digest", query_source_sha256=nullable("Digest"), normalized_runtime_id="Digest", runtime="RuntimeIdentity", build_recipe_sha256="Digest", observed_binary_sha256="Digest", generator_name="Text", generator_version="Text", collision_system="Text", energy_gev="Hex64", successful_events_by_tune=["TuneCount"], attempted_events_by_tune=["TuneCount"], uncertainty_scope="=FINITE_MC_ONLY", data_limitations=["Id"], parent_artifact_digests=["Digest"]),
    "CapabilityReceipt": dict(capability_id="Id", supported="Bool", reason=nullable("Id"), source_fields=[dict(object="Id", column_or_axis="Id")], supported_profile_ids=["Id"], supported_activity_ids=["Id"], supported_axes=["AxisRequest"], structural_acceptance_id="Id", allowed_predicates=["RECTANGLE|EXACT_RANGE|TRIGGER_GT_ASSOCIATE"], requires_protected_rebuild="Bool"),
    "ProjectionResult": dict(schema="="+RESULT_SCHEMA, request_echo="ProjectionRequest", request_sha256="Digest", scientific_request_sha256="Digest", source_receipt="SourceSelection", resolved=dict(profiles=["Profile"], axes=["AxisRequest"], class_boundaries=["ResolvedClass"], signed_pairs=["PairKey"], expected_point_keys=["PointKey"], observed_support=[dict(role_id="Id", tune_id="Id", axis_id="Id", nonzero_bins=["Count"], first_nonzero=nullable("Count"), last_nonzero=nullable("Count"), status="OBSERVED|NOT_MATERIALIZED|TEST_ONLY_LITERAL")], category_order=[dict(role_id="Id", trigger_pdg="PDG", associate_pdgs=["PDG"], labels=["Text"])]), primitive_routes=["PrimitiveRoute"], points=["PointResult"], covariance=["CovarianceResult"], materialization=[dict(point_key="PointKey", status="PRESENT|NOT_MATERIALIZED|UNSUPPORTED_QUERY", reason_codes=["Id"])], package_state="VALIDATED_COMPLETE|VALIDATED_PARTIAL", campaign_state="FULL_ACCEPTED_CAMPAIGN|PARTIAL_SAMPLE", science_content_sha256="Digest", provenance="Provenance", capability_receipt=["CapabilityReceipt"], artifact_binding=dict(root_sha256="Digest", root_bytes="Count", root_content_sha256="Digest", manifest_sha256="Digest", source_fileset_sha256="Digest")),
}

# v2 remains readable.  The new result version adds a G9-specific scientific
# record without changing the numerical request or the identities of its points.
import copy
SCHEMAS["G9Science"] = dict(
    model_id="=G9_direct_primary_selected_strict_pt0p15_eta4",
    source_family="=kinematics", final="True", selected="True",
    status_low="Count", status_high="Count",
    pt="RangePredicate", eta="RangePredicate",
    signed_species_pdgs=["PDG"], axis_ids=["Id"],
    denominator="=weighted_selected_final_same_signed_species_and_tune",
    normalization="=per_bin_probability_no_bin_width_division",
    units="=probability_per_bin",
    pt_flow="=underflow_and_overflow_in_denominator_and_output",
    eta_flow="=no_materialized_flow_inclusive_upper_endpoint",
    phi_flow="=no_materialized_flow_inclusive_upper_endpoint",
    ratio="=same_bin_probability_over_reference_tune_probability")
SCHEMAS["G9ScienceNoFloor"] = dict(
    model_id="=G9_direct_primary_selected_no_pt_floor_eta4",
    source_family="=kinematics", final="True", selected="True",
    status_low="Count", status_high="Count", origin_scope="=ALL_ORIGINS",
    pt="RangePredicate", eta="RangePredicate",
    signed_species_pdgs=["PDG"], axis_ids=["Id"],
    denominator="=weighted_all_origin_selected_final_same_signed_species_and_tune",
    normalization="=per_bin_probability_no_bin_width_division",
    units="=probability_per_bin",
    pt_flow="=negative_underflow_rejected_overflow_in_denominator_and_output",
    eta_flow="=no_materialized_flow_inclusive_upper_endpoint",
    phi_flow="=no_materialized_flow_inclusive_upper_endpoint",
    ratio="=same_bin_probability_over_reference_tune_probability")
SCHEMAS["ProjectionResultG9"] = copy.deepcopy(SCHEMAS["ProjectionResult"])
SCHEMAS["ProjectionResultG9"]["schema"] = "=" + RESULT_SCHEMA_G9
SCHEMAS["ProjectionResultG9"]["resolved"]["g9_science"] = "G9Science"
SCHEMAS["EventMomentReceiptV4"] = dict(
    schema="=hadronization_event_weight_moments_v1", tune_id="Id",
    block_id="Count", source_members_sha256="Digest",
    scope="=SELECTED_ACCEPTED_SOURCE_EVENTS_BEFORE_OBSERVABLE_CUTS",
    events="Count",sumw="Hex64",sumw2="Hex64",sumabsw="Hex64",
    event_weight_terms="Count",content_sha256="Digest")
SCHEMAS["SupportDiagnosticReceiptV4"] = dict(
    schema="=hadronization_observed_support_diagnostics_v1",
    tune_id="Id",block_id="Count",event_moments_sha256="Digest",
    activity_counts=[dict(activity_bin="Count",events="Count")],
    n_mpi_counts=[dict(n_mpi="Count",events="Count")],
    process_counts=[dict(process_code="Int",events="Count")],
    pthat_sum="Hex64",hard_scale_sum="Hex64",
    natural_final_hadrons="Count",natural_final_weighted_sum="Hex64",
    charm_constituents="Count",charm_constituent_weighted_sum="Hex64",
    beauty_constituents="Count",beauty_constituent_weighted_sum="Hex64",
    strict_selected_final_hadrons="Count",
    strict_selected_final_weighted_sum="Hex64",
    origin_pairs=[dict(origin="Int",category="Int",sign="Int",
                       rows="Count",weighted_sum="Hex64")],
    closure_terms=[dict(category="Int",visible="Bool",coefficient="Int",
                        rows="Count",weighted_sum="Hex64")],
    content_sha256="Digest")
SCHEMAS["ClassBoundaryDeletionV4"] = dict(tune_id="Id",class_id="Int",
    omitted_block="Count",source_family_digest="Digest",
    status="RESOLVED|UNRESOLVED",low=nullable("Int"),
    high=nullable("Int"),empty="Bool",
    weighted_measure=nullable("Hex64"),content_sha256="Digest")
SCHEMAS["BlockPrimitiveReceiptV4"] = dict(tune_id="Id",block_id="Count",
    additive_components=[dict(id="Id",value="Hex64")],events="Count",
    sumw="Hex64",sumw2="Hex64",sumabsw="Hex64",
    event_weight_terms="Count",event_moments_sha256="Digest")
SCHEMAS["PointResultV4"] = copy.deepcopy(SCHEMAS["PointResult"])
SCHEMAS["PointResultV4"]["block_values"] = ["BlockPrimitiveReceiptV4"]
SCHEMAS["DeleteOneFamilyV4"] = copy.deepcopy(SCHEMAS["DeleteOneFamily"])
SCHEMAS["DeleteOneFamilyV4"]["finite_mask"] = [["Bool"]]
SCHEMAS["DeleteOneFamilyV4"]["usable_mask"] = ["Bool"]
SCHEMAS["CovarianceResultV4"] = copy.deepcopy(SCHEMAS["CovarianceResult"])
SCHEMAS["CovarianceResultV4"]["independent_families"] = ["DeleteOneFamilyV4"]
SCHEMAS["CollectionFileReceiptV4"] = dict(file_id="Id",
    role="QUERY_SHARD_ROOT|MERGED_SPARSE_ROOT|SHARD_METADATA|SHARD_MANIFEST",
    shard_ordinal=nullable("Count"),tune_id=nullable("Id"),
    sha256="Digest",bytes="Count")
SCHEMAS["CollectionBindingV4"] = dict(kind="=QUERY_COLLECTION",
    collection_schema="=hadronization_query_collection_v1",
    layout="SHARDED|MERGED",
    collection_state="TEST_ONLY|EXTERNAL_ACCEPTANCE_REQUIRED",
    collection_index_sha256="Digest",
    collection_index_bytes="Count",
    collection_scientific_identity_sha256="Digest",
    member_files=["CollectionFileReceiptV4"],member_files_sha256="Digest",
    pair_proofs=[dict(shard_ordinal="Count",
        scientific_binding_sha256="Digest",proof_sha256="Digest",
        events="Count",candidate_pairs="Count")],
    pair_proofs_sha256="Digest",
    merged_partitions=[dict(tune_id="Id",root_sha256="Digest",
        families=[dict(id="Id",cell_digest="Digest")])],
    merged_partitions_sha256="Digest")
SCHEMAS["AdmissionClosureV4"] = dict(
    schema="=hadronization_query_collection_admission_closure_v1",
    qualification="TEST_ONLY_DOMAIN_CLOSED|NO_ACCEPTED_CLOSURE|FULL_ACCEPTED_DOMAIN_CLOSED",
    index_state="TEST_ONLY|EXTERNAL_ACCEPTANCE_REQUIRED",
    collection_index_sha256="Digest",
    collection_scientific_identity_sha256="Digest",
    expected_sources_sha256="Digest",natural_members_sha256="Digest",
    per_tune_source_event_counts=[dict(tune="Id",sources="Count",events="Count")],
    campaign="Id",campaign_descriptor_sha256="Digest",
    accepted_manifest_sha256="Digest",source_count="Count",
    event_count="Count",domain_complete="Bool",
    work_sha256=nullable("Digest"),collector_closure_sha256=nullable("Digest"),
    external_pins_sha256=nullable("Digest"),
    acquisition_manifest_sha256=nullable("Digest"),
    campaign_sha256=nullable("Digest"))
SCHEMAS["GeneratorEventTrialsV4"] = dict(tune_id="Id",
    scope="=ALL_SUBMITTED_CAMPAIGN_ATTEMPTS",count=nullable("Count"),
    status="AVAILABLE|UNAVAILABLE",reason_codes=["Id"])
SCHEMAS["CampaignAccountingV4"] = dict(
    schema="=hadronization_campaign_accounting_v4",
    scope="=ACCEPTED_LEDGER_ONLY_NO_QUERY_CLOSURE",
    input_sha256=dict(campaign="Digest",raw_manifest="Digest",attempts="Digest"),
    campaign_id="Id",counts=dict(accepted_sources="Count",attempts="Count",
        accepted_attempts="Count",discarded_attempts="Count",
        successful_events="Count"),
    by_tune=[dict(tune_id="Id",sources="Count",successful_events="Count",
        submitted_attempts="Count",accepted_attempts="Count",
        discarded_attempts="Count")],
    by_block=[dict(tune_id="Id",block_id="Count",sources="Count",
                   successful_events="Count")],
    attempt_evidence=[dict(outcome="Id",evidence_status="Id",count="Count")],
    generator_event_trials_by_tune=["GeneratorEventTrialsV4"])
SCHEMAS["ProvenanceV4"] = copy.deepcopy(SCHEMAS["Provenance"])
del SCHEMAS["ProvenanceV4"]["attempted_events_by_tune"]
SCHEMAS["ProvenanceV4"]["campaign_accounting"] = "CampaignAccountingV4"
SCHEMAS["ProjectionResultV4"] = copy.deepcopy(SCHEMAS["ProjectionResultG9"])
SCHEMAS["ProjectionResultV4"]["schema"] = "=" + RESULT_SCHEMA_NATIVE
SCHEMAS["ProjectionResultV4"]["resolved"]["g9_science"] = nullable("G9ScienceNoFloor")
SCHEMAS["ProjectionResultV4"]["points"] = ["PointResultV4"]
SCHEMAS["ProjectionResultV4"]["covariance"] = ["CovarianceResultV4"]
SCHEMAS["ProjectionResultV4"]["event_moment_receipts"] = ["EventMomentReceiptV4"]
SCHEMAS["ProjectionResultV4"]["support_diagnostic_receipts"] = ["SupportDiagnosticReceiptV4"]
SCHEMAS["ProjectionResultV4"]["class_boundary_deletions"] = ["ClassBoundaryDeletionV4"]
SCHEMAS["ProjectionResultV4"]["provenance"] = "ProvenanceV4"
SCHEMAS["ProjectionResultV4"]["artifact_binding"] = "CollectionBindingV4"
SCHEMAS["ProjectionResultV4"]["admission_closure"] = "AdmissionClosureV4"


def g9_science_legacy(request):
    """The admitted Phase-A G9 model, expressed independently of plot labels."""
    role = next((r for r in request["scope"]["roles"]
                 if r["role_id"] == "spectra.signed_heavy"), None)
    if role is None:
        raise ValueError("G9 scientific role is absent")
    species = sorted({c["associate_pdg"] for c in role["required_curve_keys"]
                      if c["associate_pdg"] is not None})
    if not species:
        raise ValueError("G9 signed species are absent")
    return dict(model_id="G9_direct_primary_selected_strict_pt0p15_eta4",
        source_family="kinematics", final=True, selected=True,
        status_low=81, status_high=89,
        pt=range_predicate(.15, low_operator="GT"),
        eta=range_predicate(-4., 4., "GE", "LE", ""),
        signed_species_pdgs=species, axis_ids=["pt", "eta", "phi"],
        denominator="weighted_selected_final_same_signed_species_and_tune",
        normalization="per_bin_probability_no_bin_width_division",
        units="probability_per_bin",
        pt_flow="underflow_and_overflow_in_denominator_and_output",
        eta_flow="no_materialized_flow_inclusive_upper_endpoint",
        phi_flow="no_materialized_flow_inclusive_upper_endpoint",
        ratio="same_bin_probability_over_reference_tune_probability")


def g9_science(request):
    """The current all-origin, no-floor direct-hadron G9 marginal."""
    legacy=g9_science_legacy(request)
    return dict(legacy,model_id="G9_direct_primary_selected_no_pt_floor_eta4",
        origin_scope="ALL_ORIGINS",pt=range_predicate(),
        denominator="weighted_all_origin_selected_final_same_signed_species_and_tune",
        pt_flow="negative_underflow_rejected_overflow_in_denominator_and_output")


def validate_g9_science(request, resolved, *, legacy=False):
    expected = g9_science_legacy(request) if legacy else g9_science(request)
    if resolved != expected:
        raise ValueError("resolved G9 selection/normalization differs from the admitted model")
    axes = {axis["id"]: axis for axis in request["axes"]}
    if set(expected["axis_ids"]) - set(axes):
        raise ValueError("G9 scientific axes are absent")
    for axis_id in expected["axis_ids"]:
        axis = axes[axis_id]
        if axis["variable"] != "selected_final_heavy_" + axis_id:
            raise ValueError("G9 axis variable differs from selected-final model")
        flow = axis_id == "pt"
        if (axis["low_endpoint"],axis["high_endpoint"],axis["underflow"],axis["overflow"]) != (
                "INCLUSIVE","INCLUSIVE",("RETAIN" if legacy else "REJECT") if flow else "REJECT",
                "RETAIN" if flow else "REJECT"):
            raise ValueError("G9 axis flow/endpoint model differs")
    if (number(axes["eta"]["edges"][0]) != -4. or
            number(axes["eta"]["edges"][-1]) != 4.):
        raise ValueError("G9 eta acceptance differs")


def validate(value, spec, path="projection"):
    if isinstance(spec, tuple):
        if value is not None:
            validate(value, spec[1], path)
        return
    if isinstance(spec, list):
        if type(value) is not list:
            raise ValueError(path + " must be a list")
        for index, item in enumerate(value):
            validate(item, spec[0], path + "[{}]".format(index))
        return
    if isinstance(spec, dict):
        if type(value) is not dict or set(value) != set(spec):
            raise ValueError(path + " exact fields differ")
        for key, item in spec.items():
            validate(value[key], item, path + "." + key)
        return
    if spec in SCHEMAS:
        validate(value, SCHEMAS[spec], path)
        return
    good = False
    if spec in ("Int", "Count", "PDG"):
        good = type(value) is int and -(1 << 63) <= value < (1 << 64)
        good = good and (spec != "Count" or value >= 0) and (spec != "PDG" or value != 0)
    elif spec == "Finite":
        good = type(value) in (int, float) and math.isfinite(value)
    elif spec in ("Bool", "True"):
        good = type(value) is bool and (spec != "True" or value)
    elif spec in ("Id", "Text"):
        good = isinstance(value, str) and (spec == "Text" or bool(value)) and not any(c in value for c in "\t\r\n\x00")
    elif spec == "Quantity":
        good = isinstance(value, str) and value in QUANTITIES
    elif spec in ("Digest", "GitOid"):
        good = isinstance(value, str) and re.fullmatch(r"[0-9a-f]{%d}" % (64 if spec == "Digest" else 40), value) is not None
    elif spec == "Hex64":
        try:
            good = isinstance(value, str) and math.isfinite(float.fromhex(value)) and float.fromhex(value).hex() == value
        except (ValueError, OverflowError):
            good = False
    elif spec.startswith("="):
        good = value == spec[1:]
    elif "|" in spec:
        good = isinstance(value, str) and value in spec.split("|")
    if not good:
        raise ValueError(path + " invalid " + spec)


def unique(values, label, key=canonical, nonempty=True):
    keys = [key(value) for value in values]
    if (nonempty and not keys) or len(set(keys)) != len(keys):
        raise ValueError(label + " is empty or duplicate")
    return set(keys)


@dataclass(frozen=True)
class ProjectionRequest:
    """Canonical serialized storage prevents mutable nested DTO state."""
    serialized: str

    @classmethod
    def from_dict(cls, payload, *, cold=False):
        request = cls(canonical(payload))
        request.validate(cold=cold)
        return request

    def to_dict(self):
        return json.loads(self.serialized)

    @cached_property
    def request_sha256(self):
        return hashlib.sha256(self.serialized.encode("ascii")).hexdigest()

    @cached_property
    def scientific_request_sha256(self):
        p = self.to_dict()
        for key in ("execution", "presentation_binding", "completion"):
            p.pop(key)
        p["bindings"].pop("expected_source_content_sha256")
        p["bindings"].pop("analysis_config_sha256")
        p["sources"].pop("provenance_parent_ids")
        scope = p["scope"]
        for key in ("ordered_tunes", "ordered_triggers", "ordered_associate_pairs"):
            scope[key] = sorted(scope[key], key=canonical)
        scope["roles"] = sorted([dict(role_id=r["role_id"], required_curve_keys=sorted(r["required_curve_keys"], key=canonical)) for r in scope["roles"]], key=canonical)
        for key in ("profiles", "classes", "axes", "observables"):
            p[key] = sorted(p[key], key=canonical)
        for observable in p["observables"]:
            observable["joint_point_domain"] = sorted(observable["joint_point_domain"], key=canonical)
        for group in p["statistics"]["covariance_groups"]:
            group["ordered_point_keys"] = sorted(group["ordered_point_keys"], key=canonical)
            group["required_cross_groups"].sort()
            group.pop("representation")
        p["statistics"]["covariance_groups"].sort(key=canonical)
        return digest(p)

    @property
    def expected_point_keys(self):
        return sorted([point for observable in self.to_dict()["observables"] for point in observable["joint_point_domain"]], key=canonical)

    def validate(self, *, cold=False):
        p = self.to_dict()
        if canonical(p) != self.serialized:
            raise ValueError("projection request serialization is not canonical")
        validate(p, "ProjectionRequest")
        scope, statistics = p["scope"], p["statistics"]
        for key in ("ordered_tunes", "ordered_triggers", "ordered_associate_pairs", "roles"):
            unique(scope[key], "request " + key)
        tunes = set(scope["ordered_tunes"])
        if scope["reference_tune"] is not None and scope["reference_tune"] not in tunes:
            raise ValueError("request reference tune is absent")
        if scope["mode"] == "PAPER" and not set(scope["ordered_triggers"]).issubset({411, 421, 521, 4122, 5122}):
            raise ValueError("paper triggers differ from the accepted signed scope")
        if statistics["expected_K"] != 10 or statistics["block_ids"] != list(range(1, 11)):
            raise ValueError("projection requires exact K10 source-block domain")
        source = p["sources"]
        unique(source["members"], "source membership", key=lambda x: x["source_id"], nonempty=False)
        if source["members"] != sorted(source["members"], key=lambda x: x["source_id"]) or digest(source["members"]) != source["selected_members_sha256"]:
            raise ValueError("source membership identity/order differs")
        source_tunes = {m["tune_id"] for m in source["members"]}
        expected_events = {t: sum(m["successful_events"] for m in source["members"] if m["tune_id"] == t) for t in source_tunes}
        if (not source_tunes.issubset(tunes) or source["expected_events_by_tune"] != [dict(tune_id=t, count=expected_events[t]) for t in sorted(source_tunes)] or any(m["block_id"] not in statistics["block_ids"] for m in source["members"])):
            raise ValueError("source tune/block/event accounting differs")
        unique(scope["roles"], "requested role IDs", lambda r: r["role_id"])
        for field in ("profiles", "classes", "axes"):
            unique(p[field], "requested " + field + " IDs", lambda item: item["id"])
        for klass in p["classes"]:
            interval = klass["integer_interval"] if klass["kind"] == "ABSOLUTE_INTEGER" else klass["percentile_interval"]
            other = klass["percentile_interval"] if klass["kind"] == "ABSOLUTE_INTEGER" else klass["integer_interval"]
            if interval is None or len(interval) != 2 or other is not None:
                raise ValueError("requested class interval contract differs")
            ends = interval if klass["kind"] == "ABSOLUTE_INTEGER" else list(map(number, interval))
            if ends[0] >= ends[1] or (klass["kind"] != "ABSOLUTE_INTEGER" and not 0 <= ends[0] < ends[1] <= 100):
                raise ValueError("requested class interval is unordered")
        for axis in p["axes"]:
            edges = list(map(number, axis["edges"]))
            if len(edges) < 2 or any(a >= b for a, b in zip(edges, edges[1:])):
                raise ValueError("projection axis edges are not strictly ordered")
        for profile in p["profiles"]:
            for role in ("trigger_pt", "associate_pt", "trigger_eta", "associate_eta"):
                r = profile[role]
                if (r["low"] is None) != (r["low_operator"] is None) or (r["high"] is None) != (r["high_operator"] is None):
                    raise ValueError("range endpoint operator is unbound")
                if role.endswith("_pt") and r["low"] is not None and number(r["low"]) < 0:
                    raise ValueError("pT thresholds require a finite nonnegative value")
                if r["low"] is not None and r["high"] is not None and number(r["low"]) >= number(r["high"]):
                    raise ValueError("projection range is unordered")
            hierarchy=profile["minimum_hierarchy"]
            if hierarchy != "NONE":
                trigger_low=profile["trigger_pt"]["low"]
                associate_low=profile["associate_pt"]["low"]
                if (trigger_low is None or associate_low is None or
                        (number(trigger_low) <= number(associate_low)
                         if hierarchy == "TRIGGER_MIN_GT_ASSOCIATE_MIN" else
                         number(trigger_low) < number(associate_low))):
                    raise ValueError("projection minimum hierarchy differs")
            if profile["id"] == "relative_pt" and (profile["relative_pt"] != "TRIGGER_GT_ASSOCIATE" or profile["trigger_pt"]["low"] is not None or profile["associate_pt"]["low"] is not None):
                raise ValueError("relative_pt must preserve its floor-free strict predicate")
        if scope["mode"] == "PAPER" and not cold:
            pt_axis = next((axis for axis in p["axes"] if axis["id"] == "query_pt"), None)
            if pt_axis is None:
                raise ValueError("Phase-A request lacks its pT axis")
            validate_typed_phase_a_profiles(p["profiles"],
                                            list(map(number, pt_axis["edges"])))
        axes = {a["id"]: a for a in p["axes"]}
        formula = p['science_contract']['formula_contract_version']
        if formula in ('projection_formulas_v3', 'projection_formulas_v4'):
            for observable in p['observables']:
                if (observable['formula_version'] != formula or
                        observable['output_units'] != expected_point_units(observable['quantity']) or
                        any(k['curve']['quantity'] != observable['quantity'] or
                            k['curve']['component'] != observable['component']
                            for k in observable['joint_point_domain'])):
                    raise ValueError('observable formula/quantity/units binding differs')
        signed_pairs = scope["ordered_associate_pairs"]
        for point in self.expected_point_keys:
            curve = point["curve"]
            if curve['role_id'].startswith('correlations.'):
                absolute = ('dphi_density_per_trigger' if formula in ('projection_formulas_v3', 'projection_formulas_v4')
                            else 'dphi_per_trigger')
                if (curve['quantity'] != ('ratio_to_reference_tune' if curve['reference_tune_id'] else absolute) or
                        curve['axis_id'] != 'dphi' or axes['dphi']['units'] != 'rad' or
                        len(point['bins']) != 1 or point['bins'][0]['flow'] != 'REGULAR'):
                    raise ValueError('correlation formula/quantity/axis binding differs')
            elif curve['quantity'] == 'dphi_density_per_trigger':
                raise ValueError('density quantity requires a correlation role')
            if curve["role_id"].startswith("correlations.") and curve["associate_pdg"] is None:
                sector = curve["role_id"].rsplit(".", 1)[1].upper()
                trigger = curve["trigger_pdg"]
                components = (("OS", "SS") if
                              curve["component"] == "OS_MINUS_SS" else
                              (curve["component"],))
                def complete_sign(component):
                    contributors = [pair for pair in signed_pairs
                                    if pair["trigger_pdg"] == trigger and
                                    pair["sector"] == sector and
                                    pair["sign"] == component]
                    conjugates = {-pair["associate_pdg"]
                                  for pair in signed_pairs
                                  if pair["trigger_pdg"] == trigger and
                                  pair["sector"] == sector and
                                  pair["sign"] != component}
                    return (bool(contributors) and
                            {pair["associate_pdg"] for pair in contributors} ==
                            conjugates)
                complete = all(complete_sign(component)
                               for component in components)
                if (curve["quantity"] not in ("dphi_per_trigger", "dphi_density_per_trigger") or
                        curve["reference_tune_id"] is not None or
                        curve["component"] not in
                            ("OS", "SS", "OS_MINUS_SS") or
                        curve["reference_pdg"] is not None or
                        curve["class_id"] != 0 or curve["axis_id"] != "dphi" or
                        not complete):
                    raise ValueError("registry-bound correlation sign sum differs")
            if curve["tune_id"] not in tunes or (curve["reference_tune_id"] is not None and curve["reference_tune_id"] not in tunes):
                raise ValueError("point names an unrequested tune")
            if curve["class_id"] is not None and curve["class_id"] not in {c["id"] for c in p["classes"]}:
                raise ValueError("point names an unrequested class")
            if curve["profile_id"] is not None and curve["profile_id"] not in {c["id"] for c in p["profiles"]}:
                raise ValueError("point names an unrequested profile")
            if curve["axis_id"] is None:
                if point["bins"]:
                    raise ValueError("scalar point carries axis bins")
            else:
                if curve["axis_id"] not in axes or len(point["bins"]) != 1:
                    raise ValueError("point axis domain differs")
                axis, cell = axes[curve["axis_id"]], point["bins"][0]
                n_bins = len(axis["edges"]) - 1
                expected = {
                    "UNDERFLOW": (-1, None, axis["edges"][0]),
                    "OVERFLOW": (n_bins, axis["edges"][-1], None),
                }
                if cell["flow"] == "REGULAR" and 0 <= cell["index"] < n_bins:
                    expected_cell = (cell["index"], axis["edges"][cell["index"]],
                                     axis["edges"][cell["index"] + 1])
                else:
                    expected_cell = expected.get(cell["flow"])
                if (cell["axis_id"] != axis["id"] or expected_cell is None or
                        (cell["index"], cell["low"], cell["high"]) != expected_cell or
                        (cell["flow"] == "UNDERFLOW" and axis["underflow"] != "RETAIN") or
                        (cell["flow"] == "OVERFLOW" and axis["overflow"] != "RETAIN")):
                    raise ValueError("point bin differs from requested exact axis")
        domain = unique(self.expected_point_keys, "expected natural point domain")
        curves = [curve for role in scope["roles"] for curve in role["required_curve_keys"]]
        if unique(curves, "requested natural curve domain") != {canonical(x["curve"]) for x in self.expected_point_keys}:
            raise ValueError("requested point/curve domain differs")
        for group in statistics["covariance_groups"]:
            if not unique(group["ordered_point_keys"], "covariance point domain").issubset(domain):
                raise ValueError("covariance request names a foreign point")
        unique(statistics["covariance_groups"], "covariance groups", key=lambda x: x["id"])


def semantic_id(request, key):
    return digest(dict(scientific_request_sha256=request.scientific_request_sha256, point_key=key))


def range_predicate(low=None, high=None, low_operator=None, high_operator=None, units="GeV"):
    return dict(low=None if low is None else hex64(low), high=None if high is None else hex64(high),
                low_operator=low_operator, high_operator=high_operator, units=units, domain="PHYSICAL")


def normalized_profile(profile, eta, structural):
    if profile.get("relative_pt") is not None:
        raise ValueError("eventwise pair pT predicate is not current science")
    def pt(role):
        cut = profile[role]
        return range_predicate() if cut is None else range_predicate(cut["value"], low_operator={">": "GT", ">=": "GE"}[cut["operator"]])
    acceptance = range_predicate(-eta, eta, "GE", "LE", "")
    return dict(id=profile["id"], trigger_pt=pt("trigger_pt"), associate_pt=pt("associate_pt"),
                trigger_eta=acceptance, associate_eta=acceptance,
                relative_pt="TRIGGER_GT_ASSOCIATE" if profile.get("relative_pt") else "NONE",
                minimum_hierarchy="TRIGGER_MIN_GE_ASSOCIATE_MIN" if profile["trigger_pt"] is not None and profile["associate_pt"] is not None else "NONE",
                structural_acceptance_id=structural, origin_filter=None, category_filter=None)


def typed_source_profile(profile):
    """Decode the DTO through the same source profile policy used at admission."""
    validate(profile, "Profile")
    def cut(role):
        value = profile[role]
        if value["high"] is not None or value["high_operator"] is not None:
            raise ValueError("Phase-A profile must be an ordered-minima rectangle")
        if value["low"] is None:
            if value != range_predicate():
                raise ValueError("Phase-A unbounded pT predicate differs")
            return None
        if value["low_operator"] not in ("GE", "GT") or value["units"] != "GeV":
            raise ValueError("Phase-A pT predicate differs")
        return dict(operator={"GE": ">=", "GT": ">"}[value["low_operator"]], value=number(value["low"]))
    if profile["relative_pt"] != "NONE":
        raise ValueError("eventwise pair pT predicate is not current science")
    source = dict(id=profile["id"], trigger_pt=cut("trigger_pt"), associate_pt=cut("associate_pt"),
                  relative_pt=None)
    eta = number(profile["trigger_eta"]["high"])
    if eta is None or eta <= 0 or profile != normalized_profile(source, eta, profile["structural_acceptance_id"]):
        raise ValueError("typed Phase-A profile is not an inclusive or ordered-minima rectangle")
    return source


def typed_phase_a_profile_kind(profile):
    return _query_model().phase_a_profile_kind(typed_source_profile(profile))


def validate_typed_phase_a_profiles(profiles, pt_edges):
    source_profiles = [typed_source_profile(p) for p in profiles]
    # A ProjectionRequest is intentionally a one-profile numerical slice of a
    # query collection.  Query construction validates the complete ordered
    # profile list (inclusive first, followed by aligned rectangles), whereas
    # the typed projection seam must also admit any one member of that already
    # authenticated list on its own.
    if len(source_profiles) == 1:
        _query_model().phase_a_profile_kind(source_profiles[0])
        for role in ("trigger_pt", "associate_pt"):
            threshold = source_profiles[0][role]
            if threshold is not None and threshold["value"] not in pt_edges[:-1]:
                raise ValueError("Phase-A rectangle minimum is not an aligned pT edge")
    else:
        _query_model().validate_phase_a_profiles(source_profiles, pt_edges=pt_edges)


def source_selection_definitions(receipt, pair_acceptance):
    scientific = receipt["scientific_identity"]
    domains = scientific["compact_domains"]
    return dict(profiles=domains["profiles"], pair_acceptance=pair_acceptance,
                axes={key: domains["axes"][key] for key in ("pt", "eta")},
                structural_registry_sha256=scientific["input_lineage"]["lossless_contract"]["registries_sha256"])


def validate_profile_routes(profiles, structural, definitions, routes):
    """Check reader semantics independently of receipt generation and DTO hashes.

    The original numeric source definitions are retained so their authenticated
    predicate hashes can be checked without losing JSON integer/float identity.
    Bundle admission separately binds these definitions and routes to ROOT.
    """
    validate(definitions, "SourceSelectionDefinitions")
    _query_model().validate_profiles(definitions["profiles"])
    if structural != definitions["structural_registry_sha256"]:
        raise ValueError("source selection structural provenance differs")
    selected = [r for r in routes if r["primitive_family"] in ("pairs", "triggers")]
    if not selected:
        if any(r["source_kind"] == "QUERY_ROOT" for r in routes):
            raise ValueError("source selection pair/trigger routes are missing")
        return  # Compact requests can explicitly report unsupported projections.
    expected_domain = {(f, p["id"]) for p in profiles for f in ("pairs", "triggers")}
    if unique(selected, "profile primitive routes", lambda r: (r["primitive_family"], r["profile_id"])) != expected_domain:
        raise ValueError("source selection pair/trigger route domain differs")
    acceptance = definitions["pair_acceptance"]
    eta = acceptance["eta"]["value"]
    edges, eta_axis = definitions["axes"]["pt"]["edges"], definitions["axes"]["eta"]
    if (len(edges) < 2 or edges[0] != 0 or any(a >= b for a, b in zip(edges, edges[1:])) or
            eta <= 0 or eta_axis["bins"] < 1 or eta_axis["low"] >= eta_axis["high"]):
        raise ValueError("source selection axis domain differs")
    for profile in profiles:
        original = next((p for p in definitions["profiles"] if p["id"] == profile["id"]), None)
        if original is None or normalized_profile(original, eta, structural) != profile:
            raise ValueError("requested profile differs from source selection provenance")
        for family in ("pairs", "triggers"):
            record = next(r for r in selected if (r["primitive_family"], r["profile_id"]) == (family, profile["id"]))
            pair = family == "pairs"
            predicate = dict(profile=original if pair else {k: original[k] for k in ("id", "trigger_pt")},
                             pair_acceptance=acceptance)
            if record["source_kind"] != "QUERY_ROOT" or record["predicate_sha256"] != digest(predicate):
                raise ValueError(f"{family} primitive predicate differs from source selection provenance")
            sparse = record["route"] in ("NATIVE_ALIGNED_SPARSE", "EXACT_PREFILTERED_SPARSE")
            prefiltered = pair and original["relative_pt"] is not None
            expected_route = ("EXACT_PREFILTERED_SPARSE" if prefiltered else "NATIVE_ALIGNED_SPARSE") if sparse else "EXACT_ROWS"
            if record["route"] != expected_route:
                raise ValueError(f"{family} primitive route differs from source selection")
            expected_axes = []
            for role in (("trigger_pt", "associate_pt") if pair else ("trigger_pt",)):
                cut = original[role]
                if sparse and not prefiltered and cut is not None and (cut["operator"] != ">=" or cut["value"] not in edges[:-1]):
                    raise ValueError("source selection pT endpoint is not sparse-exact")
                first = 1 if prefiltered or cut is None else next((i+1 for i, edge in enumerate(edges[:-1]) if edge >= cut["value"]), len(edges))
                expected_axes.append(dict(axis_id=role, predicate=profile[role],
                    included_regular_bins=list(range(first, len(edges))) if sparse else [],
                    include_underflow=False, include_overflow=sparse, endpoint_adjustment="NONE"))
            if sparse and (eta_axis["low"] != -eta or eta_axis["high"] != eta):
                raise ValueError("source selection eta endpoint is not sparse-exact")
            for role in (("trigger_eta", "associate_eta") if pair else ("trigger_eta",)):
                expected_axes.append(dict(axis_id=role, predicate=profile[role],
                    included_regular_bins=list(range(1, eta_axis["bins"]+1)) if sparse else [],
                    include_underflow=False, include_overflow=False,
                    endpoint_adjustment="ARCHIVED_INCLUSIVE_HIGH" if sparse else "NONE"))
            if record["resolved_axis_selection"] != expected_axes:
                raise ValueError(f"{family} resolved axis selections/bins differ from source selection provenance")


def validate_result_source(projection, receipt, embedded):
    """Bind a decoded DTO to the independently authenticated ROOT source body."""
    value = projection.to_dict()
    request = value["request_echo"]
    definitions = source_selection_definitions(receipt, embedded["pair_acceptance"])
    if canonical(value["provenance"]["source_selection_definitions"]) != canonical(definitions):
        raise ValueError("typed source selection provenance differs from authenticated ROOT")
    if value["source_receipt"] != source_selection(receipt, request["scope"]["ordered_tunes"]):
        raise ValueError("typed source member selection differs from authenticated ROOT")
    source = embedded.get("scientific_projection_source", {})
    if source.get("kind") != "verified_root_query_primitives":
        raise ValueError("typed source lacks authenticated query primitive routes")
    profiles = {p["id"] for p in request["profiles"]}
    routes = [r for r in source["primitive_route_receipts"] if r["profile_id"] is None or r["profile_id"] in profiles]
    if value["primitive_routes"] != routes:
        raise ValueError("typed primitive routes differ from authenticated ROOT")
    validate_profile_routes(request["profiles"], request["science_contract"]["structural_registry_sha256"], definitions, routes)


def normalized_activity(activity):
    predicate = activity.get("predicate", "")
    match = re.fullmatch(r"positive/final, nonzero charge, no charm/beauty constituent, finite kinematics, pt(>=|>)([0-9.]+), abs\(eta\)<=([0-9.]+)", predicate)
    if match is None or float(match[3]) != activity["eta_window"]:
        raise ValueError("authenticated activity predicate/eta definition differs")
    return dict(semantic_id=activity["semantic_id"], definition_digest=digest(activity), stored_field=activity["physical_field"],
        eta_window=hex64(activity["eta_window"]), charged=True, final=True, exclude_heavy_constituents=True,
        pt=range_predicate(float(match[2]), low_operator="GE" if match[1] == ">=" else "GT"))


def source_selection(receipt, requested_tunes=None):
    lineage = receipt["scientific_identity"]["input_lineage"]
    members = []
    for source in lineage["sources"]:
        row = source["manifest_row"]
        if requested_tunes is not None and row["tune"] not in requested_tunes:
            continue
        members.append(dict(source_id=source["source_id"], tune_id=row["tune"], logical_id=row["logical_id"],
            accepted_attempt=row["accepted_attempt"], block_id=row["block"], successful_events=row["successful_events"],
            source_root_sha256=row["raw_sha256"], source_scientific_digest=digest(row), receipt_sha256=row["validation_receipt_sha256"]))
    members.sort(key=lambda x: x["source_id"])
    tunes = sorted({m["tune_id"] for m in members})
    return dict(campaign_id=lineage["campaign"]["id"], campaign_descriptor_sha256=lineage["campaign"]["descriptor_sha256"],
        accepted_manifest_sha256=lineage["accepted_manifest"]["sha256"], accepted_plan_digest=lineage["analysis_plan"]["sha256"],
        accepted_map_digest=lineage["shard_map"]["sha256"], members=members, selected_members_sha256=digest(members),
        expected_events_by_tune=[dict(tune_id=t, count=sum(m["successful_events"] for m in members if m["tune_id"] == t)) for t in tunes],
        provenance_parent_ids=sorted({s["receipt_scientific_identity_sha256"] for s in lineage["shards"]}))


def uniform_edges(axis):
    # Serialization of the archived axis uses the C++ UniformEdge single
    # rounding convention; this is axis metadata, never observable algebra.
    from fractions import Fraction
    low, high, bins = float(axis["low"]), float(axis["high"]), axis["bins"]
    width = Fraction.from_float((high - low) / bins)
    edges = [hex64(float(Fraction.from_float(low) + width * i)) for i in range(bins)]
    return edges + [hex64(high)]


def root_uniform_edges(axis):
    """Use ROOT TAxis bin lows for direct G9 eta/phi marginals."""
    low, high, bins = float(axis['low']), float(axis['high']), axis['bins']
    return [hex64(low+i*(high-low)/bins) for i in range(bins)] + [hex64(high)]


def make_request(receipt, presentation, config, config_sha, roles, selection,
                 expected_source_content_sha256, requested_tunes, requested_analysis,
                 requested_analysis_path, requested_analysis_sha256, covariance_groups=None):
    """Enumerate the natural domain from admitted configuration BEFORE rows."""
    native=receipt.get('_native_collection_context')
    if native is None:
        scientific = receipt["scientific_identity"]
        if expected_source_content_sha256 != digest(scientific):
            raise ValueError("projection source differs from the trusted invocation binding")
        domains, lineage = scientific["compact_domains"], scientific["input_lineage"]
        requested_sources=source_selection(receipt,requested_tunes)
        block_assignment_sha=digest(lineage['block_assignment'])
        campaign_complete=receipt['state']=='PUBLICATION_ELIGIBLE'
    else:
        if expected_source_content_sha256!=native['scientific_identity_sha256'] or \
                native['selected_tunes']!=list(requested_tunes):
            raise ValueError('native collection/request source binding differs')
        domains=dict(dynamic_species=dict(t1_all_final_pdgs=native['t1_species']))
        lineage=dict(lossless_contract=dict(registries_sha256=native[
            'structural_registry_sha256']))
        requested_sources=native['source_selection']
        block_assignment_sha=native['block_assignment_sha256']
        campaign_complete=native['collection_state']=='EXTERNAL_ACCEPTANCE_REQUIRED'
    # The renderer's plot preset has no authority over numerical selection.
    # This explicit scope is supplied by the scientific invocation and checked
    # against A's normalized analysis model before the point domain is built.
    required_scope = {"profile_id", "activity_id", "reference_tune",
                      "trigger_pdgs", "baryon_meson_trigger_pdgs", "signed_pdgs"}
    if (not isinstance(selection, dict) or
            set(selection) not in (required_scope,
                                  required_scope | {'baryon_meson_channels'})):
        raise ValueError("explicit numerical scope fields differ")
    paper = selection
    tunes = list(requested_tunes)
    profile_id, activity_id = paper["profile_id"], paper["activity_id"]
    analysis_path = Path(requested_analysis_path)
    if (file_digest(analysis_path) != requested_analysis_sha256 or
            json.loads(analysis_path.read_text(encoding="utf-8")) != requested_analysis):
        raise ValueError("current requested analysis differs from trusted input identity")
    study_path = ROOT / "config/study.json"
    particle_registry = file_digest(study_path)
    if requested_analysis["base_study"]["sha256"] != particle_registry:
        raise ValueError("current particle registry differs from requested analysis binding")
    definitions = requested_analysis
    _query_model().validate_phase_a_profiles(
        definitions["profiles"], pt_edges=definitions["axes"]["pt"]["edges"])
    profiles_by_id = {p["id"]: p for p in definitions["profiles"]}
    activities_by_id = {a["id"]: a for a in definitions["activities"]}
    if profile_id not in profiles_by_id or activity_id not in activities_by_id:
        raise ValueError("numerical profile/activity is absent from analysis")
    if (paper["reference_tune"] not in tunes or
            len(tunes) != len(set(tunes)) or not tunes):
        raise ValueError("numerical reference/ordered tune domain differs")
    allowed_triggers = set(definitions["pair_query_registry"]["trigger_pdgs"])
    allowed_associates = {p for sector in definitions["pair_query_registry"]["associate_pdgs"].values()
                          for p in sector}
    for field, allowed in (("trigger_pdgs", allowed_triggers),
                           ("baryon_meson_trigger_pdgs", allowed_triggers),
                           ("signed_pdgs", allowed_associates)):
        selected = paper[field]
        if (not isinstance(selected, list) or not selected or
                any(type(p) is not int for p in selected) or
                len(selected) != len(set(selected)) or set(selected) - allowed):
            raise ValueError("numerical signed-PDG scope differs: " + field)
    if set(paper["baryon_meson_trigger_pdgs"]) - set(paper["trigger_pdgs"]):
        raise ValueError("numerical baryon/meson trigger scope differs")
    profile = profiles_by_id[profile_id]
    activity = activities_by_id[activity_id]
    structural = lineage["lossless_contract"]["registries_sha256"]
    if structural != _reducer().analyzer_module().REGISTRIES_DIGEST:
        raise ValueError("source structural registry differs from current analyzer contract")
    eta = definitions.get("pair_acceptance", presentation["selection_definitions"]["pair_acceptance"])["eta"]["value"]
    selected_states, requested_pairs = _query_model().observable_pairs(
        requested_analysis, 'projection_formulas_v4')
    if native is not None and any(
            pair["trigger_pdg"] in paper["trigger_pdgs"] and
            pair["associate_pdg"] not in paper["signed_pdgs"]
            for pair in requested_pairs):
        raise ValueError("inclusive heavy-flavour sign sum requires every eligible associate")
    g9_species = definitions["g9_species_pdgs"]
    dynamic = domains.get("dynamic_species")
    registered_g9={state['pdg'] for state in selected_states
                   if state['sector'] in ('charm','beauty')}
    if (not isinstance(g9_species, list) or not g9_species or
            len(g9_species) != len(set(g9_species)) or
            any(type(pdg) is not int or pdg not in registered_g9
                for pdg in g9_species)):
        raise ValueError("G9 signed species request differs")
    if not isinstance(dynamic, dict) or "t1_all_final_pdgs" not in dynamic:
        raise ValueError("authenticated T1 natural signed-species domain is absent")
    t1_species = dynamic["t1_all_final_pdgs"]
    if (not isinstance(t1_species, list) or not t1_species or
            t1_species != sorted(set(t1_species)) or
            any(type(pdg) is not int or pdg == 0 for pdg in t1_species)):
        raise ValueError("authenticated T1 natural signed-species domain differs")
    pairs = [dict(trigger_pdg=p["trigger_pdg"], associate_pdg=p["associate_pdg"],
                  reference_meson_pdg=p["reference_meson_pdg"], sign="OS" if p["sign"] == -1 else "SS", sector=p["sector"].upper())
             for p in requested_pairs if p["associate_pdg"] in paper["signed_pdgs"] and p["trigger_pdg"] in paper["trigger_pdgs"]]
    # Put identified charm categories in meson/baryon order in the request.
    # Cold archives retain their selected set; display may reorder that set.
    def pair_order(pair):
        charm = pair['sector'] == 'CHARM'
        associate = pair['associate_pdg']
        if pair['sign'] == 'SS':
            associate = -associate
        rank = (PAPER_CHARM_ASSOCIATES.index(associate)
                if charm and associate in PAPER_CHARM_ASSOCIATES else
                len(PAPER_CHARM_ASSOCIATES))
        return pair['trigger_pdg'], rank, canonical(pair)
    pairs.sort(key=pair_order)
    ratio_channels = checked_baryon_meson_channels(paper, pairs, selected_states)
    classes = [dict(id=i, kind="INTEGRATED" if i == 0 else "TUNE_LOCAL_PERCENTILE",
                    percentile_interval=list(map(hex64, interval)), integer_interval=None,
                    boundary_policy_id="pooled_tune_local_integer_percentile_v1")
               for i, interval in enumerate([requested_analysis["integrated_interval"]] + requested_analysis["percentile_intervals"])]
    requested_axes = requested_analysis["axes"]
    axes = [dict(id="dphi", variable="trigger_phi_minus_associate_phi", units="rad",
                 edges=uniform_edges(requested_axes["dphi"]), low_endpoint="INCLUSIVE", high_endpoint="EXCLUSIVE",
                 underflow="REJECT", overflow="REJECT", angular_wrap=dict(low=hex64(requested_axes["dphi"]["low"]), high=hex64(requested_axes["dphi"]["high"]))),
            dict(id="nch", variable=activity["physical_field"], units="count", edges=[hex64(i) for i in range(requested_axes["activity"]["bins"]+1)],
                 low_endpoint="INCLUSIVE", high_endpoint="EXCLUSIVE", underflow="REJECT", overflow="REJECT", angular_wrap=None),
            dict(id="query_pt", variable="authenticated_sparse_pt", units="GeV", edges=[hex64(x) for x in requested_axes["pt"]["edges"]],
                 low_endpoint="INCLUSIVE", high_endpoint="INCLUSIVE", underflow="RETAIN", overflow="RETAIN", angular_wrap=None),
            dict(id="pt", variable="selected_final_heavy_pt", units="GeV", edges=[hex64(x) for x in G9_PT_EDGES],
                 low_endpoint="INCLUSIVE", high_endpoint="INCLUSIVE", underflow="REJECT", overflow="RETAIN", angular_wrap=None),
            dict(id="eta", variable="selected_final_heavy_eta", units="1", edges=root_uniform_edges(requested_axes["eta"]),
                 low_endpoint="INCLUSIVE", high_endpoint="INCLUSIVE", underflow="REJECT", overflow="REJECT", angular_wrap=None),
            dict(id="phi", variable="selected_final_heavy_phi", units="rad", edges=root_uniform_edges(requested_axes["phi"]),
                 low_endpoint="INCLUSIVE", high_endpoint="INCLUSIVE", underflow="REJECT", overflow="REJECT", angular_wrap=None)]
    axis_map = {a["id"]: a for a in axes}
    if {r["id"] for r in roles} != set(PAPER_ROLE_IDS) or len(roles) != len(PAPER_ROLE_IDS):
        raise ValueError("declared paper role registry differs from the accepted requested domain")
    # Required roles are a scientific contract, never the subset of emitted rows.
    roles = [dict(id=role_id) for role_id in PAPER_ROLE_IDS]
    role_requests, all_points = [], []
    for role in roles:
        curves = []
        role_id = role["id"]
        def add(tune, quantity, trigger=None, associate=None, reference=None, component="NONE", class_id=None, axis=None, tune_reference=None):
            curve = dict(role_id=role_id, tune_id=tune, reference_tune_id=tune_reference,
                profile_id=profile_id if trigger is not None else None,
                activity_id=None if role_id in ("spectra.signed_heavy", "accounting.natural_final_heavy") else activity_id,
                class_id=class_id, trigger_pdg=trigger, associate_pdg=associate, reference_pdg=reference,
                quantity=quantity, component=component, axis_id=axis)
            curves.append(curve)
            bins = [] if axis is None else [dict(axis_id=axis, index=i, low=lo, high=hi, flow="REGULAR")
                for i, (lo, hi) in enumerate(zip(axis_map[axis]["edges"], axis_map[axis]["edges"][1:]))]
            if role_id == "spectra.signed_heavy" and axis == "pt":
                bins = ([dict(axis_id="pt",index=-1,low=None,
                             high=axis_map["pt"]["edges"][0],flow="UNDERFLOW")]
                        if axis_map['pt']['underflow']=='RETAIN' else []) + bins + [
                    dict(axis_id="pt",index=len(axis_map["pt"]["edges"])-1,
                         low=axis_map["pt"]["edges"][-1],high=None,
                         flow="OVERFLOW")]
            all_points.extend([dict(curve=curve, bins=[])] if axis is None else [dict(curve=curve, bins=[b]) for b in bins])
        for tune in tunes:
            if role_id == "spectra.signed_heavy":
                for species in g9_species:
                    for axis in ("pt", "eta", "phi"):
                        add(tune,"normalized_spectrum",associate=species,axis=axis)
                        if tune != paper["reference_tune"]:
                            add(tune,"spectrum_ratio_to_reference_tune",
                                associate=species,axis=axis,
                                tune_reference=paper["reference_tune"])
                continue
            if role_id == "accounting.natural_final_heavy":
                for species in t1_species:
                    for component in T1_COMPONENTS:
                        add(tune,"raw_count",associate=species,component=component)
                        add(tune,"raw_weighted_sum",associate=species,component=component)
                    add(tune,"normalized_yield",associate=species,
                        component="hadron_count")
                continue
            if role_id == "multiplicity.composite":
                add(tune, "normalized_distribution", axis="nch")
                if tune != paper["reference_tune"]:
                    add(tune, "ratio_to_reference_tune", axis="nch", tune_reference=paper["reference_tune"])
                continue
            if (native is not None and role_id.startswith("correlations.") and
                    tune == paper["reference_tune"]):
                sector = role_id.rsplit(".", 1)[1].upper()
                for trigger in paper["trigger_pdgs"]:
                    if not any(p["trigger_pdg"] == trigger and p["sector"] == sector
                               for p in pairs):
                        continue
                    identified = {p["sign"]: p["associate_pdg"] for p in pairs
                                  if p["trigger_pdg"] == trigger and
                                  p["sector"] == sector and
                                  abs(p["associate_pdg"]) == abs(trigger)}
                    if identified != {"OS": -trigger, "SS": trigger}:
                        raise ValueError("identified correlation pair is absent")
                    for component in ("OS", "SS", "OS_MINUS_SS"):
                        # A null associate is an explicit, registry-bound sum
                        # over every eligible signed associate in this flavour sector.
                        add(tune, "dphi_density_per_trigger", trigger, None,
                            component=component, class_id=0, axis="dphi")
                    if abs(trigger) in (4122, 5122):
                        for component in ("OS", "SS"):
                            add(tune, "dphi_density_per_trigger", trigger, -trigger,
                                component=component, class_id=0, axis="dphi")
            for pair in pairs:
                if pair["sign"] != "OS":
                    continue
                t, a, ref = pair["trigger_pdg"], pair["associate_pdg"], pair["reference_meson_pdg"]
                if role_id.startswith("correlations."):
                    if pair["sector"].lower() != role_id.rsplit(".", 1)[1] or abs(a) != abs(ref):
                        continue
                    for component in ("OS", "SS", "OS_MINUS_SS"):
                        add(tune, "dphi_density_per_trigger", t, a, component=component, class_id=0, axis="dphi")
                        if tune != paper["reference_tune"]:
                            add(tune, "ratio_to_reference_tune", t, a, component=component,
                                class_id=0, axis="dphi", tune_reference=paper["reference_tune"])
                elif role_id == "balancing.baryon_meson.activity":
                    if (t, a, ref) not in ratio_channels:
                        continue
                    for c in classes:
                        if c["id"] == 0:
                            continue
                        add(tune, "baryon_meson_reference_ratio", t, a, ref, class_id=c["id"])
                        if tune != paper["reference_tune"]:
                            add(tune, "baryon_meson_ratio_to_reference_tune", t, a, ref, class_id=c["id"], tune_reference=paper["reference_tune"])
                elif role_id.endswith("." + pair["sector"].lower()):
                    # Identified balancing categories share one definition
                    # across integrated and activity-resolved products.
                    # The C++ estimator obtains SS from each OS conjugate.
                    if (role_id in ("balancing.integrated.beauty", "balancing.activity.beauty") and
                            a not in PAPER_BEAUTY_ASSOCIATES.get(t, ())):
                        continue
                    if (role_id in ("balancing.integrated.charm", "balancing.activity.charm") and
                            (t not in (411, 421, 4122) or
                             a not in PAPER_CHARM_ASSOCIATES)):
                        continue
                    for c in classes:
                        if (".integrated." in role_id) != (c["id"] == 0):
                            continue
                        add(tune, "os_minus_ss_per_trigger", t, a, ref, class_id=c["id"])
                        if tune != paper["reference_tune"]:
                            add(tune, "ratio_to_reference_tune", t, a, ref, class_id=c["id"], tune_reference=paper["reference_tune"])
        curves.sort(key=canonical)
        panels = {canonical(dict(role_id=role_id, trigger_pdg=c["trigger_pdg"], quantity=c["quantity"], component=c["component"])) for c in curves}
        role_requests.append(dict(role_id=role_id, ordered_panels=[json.loads(x) for x in sorted(panels)], required_curve_keys=curves))
    all_points.sort(key=canonical)
    observable_groups = {}
    for point in all_points:
        c = point["curve"]
        observable_groups.setdefault((c["quantity"], c["component"]), []).append(point)
    activity_request = normalized_activity(activity)
    if covariance_groups is None:
        covariance_groups = [dict(id="joint_requested_domain", ordered_point_keys=all_points, representation="DELETE_ONE_FACTORS", required_cross_groups=[r["role_id"] for r in role_requests])]
    source_route = (dict(kind='verified_root_query_primitives') if native is not None
                    else receipt.get("_verified_projection_source", {}))
    # A paper request backed by query primitives must prove native reads.
    # Explicit exact-row query products remain diagnostic inputs.
    requested_backend = "aligned_sparse" if source_route.get("kind") == "verified_root_query_primitives" else "auto"
    return ProjectionRequest.from_dict(dict(schema=REQUEST_SCHEMA,
        science_contract=dict(analyzer_schema="hadronization_lossless_analysis_v1", structural_registry_sha256=structural, estimator_policy_id=ESTIMATOR, formula_contract_version="projection_formulas_v4"),
        sources=requested_sources, scope=dict(mode="PAPER", roles=role_requests, ordered_tunes=tunes,
            reference_tune=paper["reference_tune"], ordered_triggers=paper["trigger_pdgs"], ordered_associate_pairs=pairs),
        profiles=[normalized_profile(profile, eta, structural)], activity=activity_request, classes=classes, axes=axes,
        observables=[dict(quantity=q, formula_version="projection_formulas_v4", output_units=expected_point_units(q), component=c, joint_point_domain=points) for (q, c), points in sorted(observable_groups.items())],
        statistics=dict(block_assignment_sha256=block_assignment_sha, block_ids=list(range(1, 11)), expected_K=10, uncertainty="FINITE_MC_DELETE_ONE", covariance_groups=covariance_groups),
        execution=dict(backend_policy={"auto": "AUTO", "exact_rows": "EXACT_ROWS", "aligned_sparse": "REQUIRE_NATIVE"}[requested_backend], permitted_routes=ROUTE.split("|"), required_capabilities=["paper_observables", "joint_covariance"]),
        completion=dict(require_campaign_complete=campaign_complete, require_all_requested_points=True, permitted_scientific_statuses=STATUS.split("|")),
        bindings=dict(analysis_config_sha256=requested_analysis_sha256, particle_registry_sha256=particle_registry, activity_definition_sha256=activity_request["definition_digest"], expected_source_content_sha256=expected_source_content_sha256),
        presentation_binding=dict(layout_contract_version="paper_layout_v2", plot_config_sha256=config_sha)))


def make_native_request(source, analysis_path, analysis_sha256, selected_tunes,
                        t1_species, selection, plot_config_path=None):
    """Build the paper natural domain directly from A's admitted collection.

    The observed natural-final T1 species must come from the exact support
    scan.  This factory does not synthesize a compact reduction receipt.
    """
    selected_tunes=list(selected_tunes)
    if not selected_tunes or len(selected_tunes)!=len(set(selected_tunes)) or \
            set(selected_tunes)-set(source.index['tune_ordinals']):
        raise ValueError('native request tune selection differs from A collection')
    t1_species=list(t1_species)
    if not t1_species or t1_species!=sorted(set(t1_species)) or \
            any(type(pdg) is not int or pdg==0 for pdg in t1_species):
        raise ValueError('native request T1 observed species differ')
    analysis_path=Path(analysis_path)
    if file_digest(analysis_path)!=analysis_sha256:
        raise ValueError('native request analysis bytes differ from pin')
    analysis=json.loads(analysis_path.read_text(encoding='utf-8'))
    checked,checked_sha=_query_model().checked_analysis(analysis_path)
    if checked_sha!=analysis_sha256 or checked!=analysis:
        raise ValueError('native request normalized A analysis differs')
    construction_path=Path(source.index['shards'][0]['workspace_manifest']['path']).parent/'analysis.json'
    if file_digest(construction_path)!=source.index['analysis_sha256']:
        raise ValueError('native request query construction analysis differs')
    construction,construction_sha=_query_model().checked_analysis(construction_path)
    if construction_sha!=source.index['analysis_sha256']:
        raise ValueError('native request query construction model differs')
    _query_model().compatible_interpretation(construction,analysis)
    lineage=source.source_lineage(selected_tunes)
    if lineage['collection_index_sha256']!=source.expected_sha256 or \
            lineage['collection_scientific_identity_sha256']!=source.index[
                'scientific_identity_sha256']:
        raise ValueError('native request A lineage binding differs')
    members=lineage['source_selection']['members']
    block_assignment_sha=digest([dict(tune_id=member['tune_id'],
        source_id=member['source_id'],block_id=member['block_id']) for member in members])
    native=dict(scientific_identity_sha256=source.index['scientific_identity_sha256'],
        selected_tunes=selected_tunes,t1_species=t1_species,
        structural_registry_sha256=lineage['structural_registry_sha256'],
        source_selection=lineage['source_selection'],
        block_assignment_sha256=block_assignment_sha,
        collection_state=lineage['collection_state'])
    if plot_config_path is None:plot_config_path=ROOT/'config/plot.json'
    plot_config_path=Path(plot_config_path)
    plot_config=json.loads(plot_config_path.read_text(encoding='utf-8'))
    plot_sha=file_digest(plot_config_path)
    return make_request(dict(_native_collection_context=native),
        dict(selection_definitions=analysis),plot_config,plot_sha,
        [dict(id=role) for role in PAPER_ROLE_IDS],selection,
        source.index['scientific_identity_sha256'],selected_tunes,analysis,
        analysis_path,analysis_sha256)


def validate_native_v4_receipts(result,request):
    """Cold-check v4's shared moments, collection inventory and ledger scopes."""
    groups={}
    for member in request['sources']['members']:
        groups.setdefault((member['tune_id'],member['block_id']),[]).append(member)
    moments=result['event_moment_receipts']
    if unique(moments,'event moment receipts',lambda r:(r['tune_id'],r['block_id']))!=set(groups):
        raise ValueError('event moment tune/block domain differs')
    for receipt in moments:
        key=(receipt['tune_id'],receipt['block_id'])
        members=sorted(groups[key],key=lambda m:m['source_id'])
        body={field:value for field,value in receipt.items()
              if field!='content_sha256'}
        if receipt['source_members_sha256']!=digest(members) or \
                receipt['content_sha256']!=digest(body) or \
                receipt['events']!=sum(m['successful_events'] for m in members) or \
                receipt['event_weight_terms']!=receipt['events'] or \
                number(receipt['sumw2'])<0 or number(receipt['sumabsw'])<0 or \
                number(receipt['sumabsw'])+1e-12<abs(number(receipt['sumw'])):
            raise ValueError('event moment membership/content/exposure differs')
    diagnostic=result['support_diagnostic_receipts']
    if unique(diagnostic,'support diagnostic receipts',lambda r:(r['tune_id'],r['block_id']))!=set(groups):
        raise ValueError('support diagnostic tune/block domain differs')
    moment_by_group={(r['tune_id'],r['block_id']):r for r in moments}
    for item in diagnostic:
        key=(item['tune_id'],item['block_id'])
        body={field:value for field,value in item.items()
              if field!='content_sha256'}
        if item['event_moments_sha256']!=moment_by_group[key]['content_sha256'] or \
                item['content_sha256']!=digest(body) or \
                any(sum(row['events'] for row in item[name])!=moment_by_group[key]['events']
                    for name in ('activity_counts','n_mpi_counts','process_counts')):
            raise ValueError('support diagnostic moments/content differs')
    deletions=result['class_boundary_deletions']
    boundary_domain={(tune,klass['id'],omit) for tune in
        request['scope']['ordered_tunes'] for klass in request['classes']
        for omit in range(11)}
    if unique(deletions,'class boundary deletion receipts',lambda row:(
            row['tune_id'],row['class_id'],row['omitted_block']))!=boundary_domain:
        raise ValueError('class boundary deletion domain differs')
    full_boundaries={(row['tune_id'],row['class_id']):row for row in
                     result['resolved']['class_boundaries']}
    for item in deletions:
        family=digest([member for member in request['sources']['members']
            if member['tune_id']==item['tune_id']])
        body={key:value for key,value in item.items() if key!='content_sha256'}
        resolved=item['status']=='RESOLVED'
        if item['source_family_digest']!=family or \
                item['content_sha256']!=digest(body) or \
                resolved!=(item['low'] is not None and item['high'] is not None
                          and item['weighted_measure'] is not None):
            raise ValueError('class deletion source/value/content differs')
        if item['omitted_block']==0:
            full=full_boundaries[item['tune_id'],item['class_id']]
            if full['boundary_status']!=item['status'] or \
                    full['actual_integer_low']!=(item['low'] if resolved else -1) or \
                    full['actual_integer_high']!=(item['high'] if resolved else -1) or \
                    full['empty']!=item['empty'] or \
                    full['event_weight']!=(item['weighted_measure']
                                           if resolved else hex64(0)):
                raise ValueError('full class/deletion boundary differs')
    binding=result['artifact_binding']
    if (binding['collection_state']=='TEST_ONLY' and
            result['campaign_state']!='PARTIAL_SAMPLE'):
        raise ValueError('TEST_ONLY query collection cannot claim full accepted campaign')
    closure=result['admission_closure']
    selected=request['sources']['members']
    natural=sorted([[member['source_id'],member['tune_id'],
                     member['logical_id'],member['block_id'],
                     member['successful_events']] for member in selected],
                   key=lambda row:row[0])
    tune_counts={t:(sum(member['tune_id']==t for member in selected),
                    sum(member['successful_events'] for member in selected
                        if member['tune_id']==t))
                 for t in request['scope']['ordered_tunes']}
    closure_counts={row['tune']:(row['sources'],row['events'])
                    for row in closure['per_tune_source_event_counts']}
    if (closure['index_state']!=binding['collection_state'] or
            closure['collection_index_sha256']!=binding[
                'collection_index_sha256'] or
            closure['collection_scientific_identity_sha256']!=binding[
                'collection_scientific_identity_sha256'] or
            closure['campaign']!=request['sources']['campaign_id'] or
            closure['campaign_descriptor_sha256']!=request['sources'][
                'campaign_descriptor_sha256'] or
            closure['accepted_manifest_sha256']!=request['sources'][
                'accepted_manifest_sha256'] or
            closure['natural_members_sha256']!=digest(natural) or
            len(closure_counts)!=len(closure['per_tune_source_event_counts']) or
            closure_counts!=tune_counts or
            closure['source_count']!=len(selected) or
            closure['event_count']!=sum(m['successful_events'] for m in selected)):
        raise ValueError('admission closure source membership or campaign binding differs')
    if binding['collection_state']=='TEST_ONLY' and (
            closure['qualification']!='TEST_ONLY_DOMAIN_CLOSED' or
            any(closure[name] is not None for name in (
                'work_sha256','collector_closure_sha256',
                'external_pins_sha256','acquisition_manifest_sha256',
                'campaign_sha256'))):
        raise ValueError('TEST_ONLY admission closure cannot claim site acceptance')
    if result['campaign_state']=='FULL_ACCEPTED_CAMPAIGN' and (
            closure['qualification']!='FULL_ACCEPTED_DOMAIN_CLOSED' or
            closure['index_state']!='EXTERNAL_ACCEPTANCE_REQUIRED' or
            not closure['domain_complete'] or
            any(closure[name] is None for name in (
                'work_sha256','collector_closure_sha256',
                'external_pins_sha256','acquisition_manifest_sha256',
                'campaign_sha256'))):
        raise ValueError('full campaign lacks authenticated admission closure')
    if result['campaign_state']=='FULL_ACCEPTED_CAMPAIGN' and (
            binding['layout']!='MERGED' or
            closure['source_count']!=len(request['sources']['members']) or
            len(request['scope']['ordered_tunes'])!=3 or
            set(request['scope']['ordered_tunes'])!=
                {'MONASH','JUNCTIONS','CLOSEPACKING'}):
        raise ValueError('full paper result requires complete MERGED three-tune domain')
    if (result['campaign_state']=='FULL_ACCEPTED_CAMPAIGN' and
            not request['completion']['require_campaign_complete']):
        raise ValueError('full paper result lacks a campaign-complete request')
    files=binding['member_files']
    pair_proofs=binding['pair_proofs']
    proof_ordinals=[row['shard_ordinal'] for row in pair_proofs]
    if (binding['pair_proofs_sha256']!=digest(pair_proofs) or
            proof_ordinals!=sorted(set(proof_ordinals)) or
            sum(row['events'] for row in pair_proofs)!=closure['event_count']):
        raise ValueError('collection v2.2 pair proof domain/content differs')
    if (files!=sorted(files,key=lambda row:row['file_id']) or
            len({row['file_id'] for row in files})!=len(files) or
            binding['member_files_sha256']!=digest(files) or
            binding['collection_index_bytes']==0 or not files):
        raise ValueError('collection ordered member inventory differs')
    shards={}
    partitions=set()
    partition_ids=set()
    for row in files:
        if row['bytes']==0:
            raise ValueError('collection member byte size differs')
        if row['role']=='MERGED_SPARSE_ROOT':
            if binding['layout']!='MERGED' or row['shard_ordinal'] is not None or \
                    row['tune_id'] is None or not re.fullmatch(
                        r'partition_[0-9]{4}_root',row['file_id']) or \
                    row['tune_id'] in partitions:
                raise ValueError('collection merged partition identity differs')
            partitions.add(row['tune_id'])
            partition_ids.add(int(row['file_id'][10:14]))
        else:
            ordinal=row['shard_ordinal']
            suffix={'QUERY_SHARD_ROOT':'root','SHARD_METADATA':'metadata',
                    'SHARD_MANIFEST':'manifest'}[row['role']]
            if ordinal is None or row['tune_id'] is not None or \
                    row['file_id']!='shard_{:04d}_{}'.format(ordinal,suffix):
                raise ValueError('collection shard member identity differs')
            shards.setdefault(ordinal,set()).add(row['role'])
    if (not shards or any(roles!={'QUERY_SHARD_ROOT','SHARD_METADATA',
                                   'SHARD_MANIFEST'} for roles in shards.values()) or
            (binding['layout']=='MERGED')!=bool(partitions) or
            partition_ids!=set(range(len(partition_ids)))):
        raise ValueError('collection shard/partition role domain differs')
    if set(shards)!=set(proof_ordinals):
        raise ValueError('collection v2.2 pair proofs do not cover admitted shards')
    merged=binding['merged_partitions']
    if (binding['merged_partitions_sha256']!=digest(merged) or
            len(merged)!=len(partitions) or
            {row['tune_id'] for row in merged}!=partitions or
            any({family['id'] for family in row['families']}!=
                {'activity','closure','kinematics','pairs','triggers'} or
                len(row['families'])!=5 or
                row['families']!=sorted(row['families'],key=lambda f:f['id']) or
                not any(file['role']=='MERGED_SPARSE_ROOT' and
                        file['tune_id']==row['tune_id'] and
                        file['sha256']==row['root_sha256'] for file in files)
                for row in merged)):
        raise ValueError('merged five-family partition identity/content differs')
    if result['campaign_state']=='FULL_ACCEPTED_CAMPAIGN' and (
            set(shards)!=set(range(323)) or len(partitions)!=3 or
            partitions!=set(request['scope']['ordered_tunes'])):
        raise ValueError('full paper result requires 323 authenticated shards and three merged partitions')
    provenance=result['provenance']
    if provenance['successful_events_by_tune']!=request['sources']['expected_events_by_tune']:
        raise ValueError('selected successful-event exposure differs')
    accounting=provenance['campaign_accounting']
    if accounting['campaign_id']!=request['sources']['campaign_id'] or \
            provenance['campaign_descriptor_sha256']!=request['sources'][
                'campaign_descriptor_sha256']:
        raise ValueError('campaign accounting/request identity differs')
    tunes=accounting['by_tune']
    if unique(tunes,'campaign accounting tunes',lambda row:row['tune_id'])!=\
            unique(accounting['generator_event_trials_by_tune'],
                   'campaign generator event trials',lambda row:row['tune_id']):
        raise ValueError('campaign event-trial tune domain differs')
    counts=accounting['counts']
    if result['campaign_state']=='FULL_ACCEPTED_CAMPAIGN' and (
            counts['accepted_sources']!=closure['source_count'] or
            counts['successful_events']!=closure['event_count'] or
            {row['tune_id']:(row['sources'],row['successful_events'])
                for row in tunes}!=closure_counts):
        raise ValueError('full admission closure differs from accepted campaign ledger')
    if (sum(row['sources'] for row in tunes)!=counts['accepted_sources'] or
            sum(row['successful_events'] for row in tunes)!=counts['successful_events'] or
            sum(row['accepted_attempts'] for row in tunes)!=counts['accepted_attempts'] or
            sum(row['discarded_attempts'] for row in tunes)!=counts['discarded_attempts'] or
            sum(row['submitted_attempts'] for row in tunes)!=counts['attempts'] or
            counts['attempts']!=counts['accepted_attempts']+counts['discarded_attempts'] or
            any(row['submitted_attempts']!=row['accepted_attempts']+
                row['discarded_attempts'] or row['sources']!=row['accepted_attempts']
                for row in tunes)):
        raise ValueError('campaign job-attempt accounting differs')
    by_block=accounting['by_block']
    if len({(row['tune_id'],row['block_id']) for row in by_block})!=len(by_block):
        raise ValueError('campaign block accounting identity differs')
    for tune in tunes:
        rows=[row for row in by_block if row['tune_id']==tune['tune_id']]
        if sum(row['sources'] for row in rows)!=tune['sources'] or \
                sum(row['successful_events'] for row in rows)!=tune['successful_events']:
            raise ValueError('campaign block/tune accounting differs')
    evidence=accounting['attempt_evidence']
    if (len({(row['outcome'],row['evidence_status']) for row in evidence})!=
            len(evidence) or sum(row['count'] for row in evidence)!=counts['attempts'] or
            any(row['outcome'] not in ('accepted','discarded') for row in evidence)):
        raise ValueError('campaign attempt evidence differs')
    for trial in accounting['generator_event_trials_by_tune']:
        if (trial['status']=='UNAVAILABLE')!=(trial['count'] is None) or \
                (trial['status']=='UNAVAILABLE')!=bool(trial['reason_codes']):
            raise ValueError('campaign generator event-trial status/value differs')
        if trial['status']=='AVAILABLE':
            raise ValueError('campaign generator event-trial coverage evidence is absent')


@dataclass(frozen=True)
class ProjectionResult:
    serialized: str

    @classmethod
    def from_dict(cls, payload, request=None, expected_routes=None, *, cold=False):
        result = cls(canonical(payload))
        result.validate(request, expected_routes, cold=cold)
        return result

    def to_dict(self):
        return json.loads(self.serialized)

    @property
    def request(self):
        return ProjectionRequest.from_dict(self.to_dict()["request_echo"])

    def validate(self, request=None, expected_routes=None, *, cold=False):
        p = self.to_dict()
        v4 = p.get("schema") == RESULT_SCHEMA_NATIVE
        if v4:
            validate(p, "ProjectionResultV4")
        elif p.get("schema") == RESULT_SCHEMA_G9:
            validate(p, "ProjectionResultG9")
        else:
            validate(p, "ProjectionResult")
        req = ProjectionRequest.from_dict(p["request_echo"], cold=cold)
        if request is not None and req.serialized != request.serialized:
            raise ValueError("projection request echo differs from the invocation")
        request = req.to_dict()
        if v4 and any(profile["relative_pt"] != "NONE" or
                      profile["minimum_hierarchy"] == "TRIGGER_MIN_GT_ASSOCIATE_MIN"
                      for profile in request["profiles"]):
            raise ValueError("current native v4 profile cannot carry a diagonal or strict-minimum predicate")
        if v4 and (any(route['route']=='EXACT_PREFILTERED_SPARSE'
                       for route in p['primitive_routes']) or
                   any('TRIGGER_GT_ASSOCIATE' in receipt['allowed_predicates']
                       for receipt in p['capability_receipt'])):
            raise ValueError('current native v4 route/capability cannot carry a diagonal predicate')
        if p["schema"] == RESULT_SCHEMA_G9 or (v4 and any(
                role['role_id']=='spectra.signed_heavy' for role in
                request['scope']['roles'])):
            validate_g9_science(request, p["resolved"]["g9_science"],
                                legacy=p["schema"] == RESULT_SCHEMA_G9)
        elif v4 and p['resolved']['g9_science'] is not None:
            raise ValueError('unrequested v4 G9 science metadata differs')
        if v4 and p['resolved']['g9_science'] is not None:
            g9_routes=[route for route in p['primitive_routes']
                       if route['primitive_family']=='kinematics']
            if (len(g9_routes)!=1 or g9_routes[0]['profile_id'] is not None or
                    g9_routes[0]['route']!='NATIVE_ALIGNED_SPARSE' or
                    g9_routes[0]['predicate_sha256']!=digest(
                        p['resolved']['g9_science'])):
                raise ValueError('current G9 route predicate/source identity differs')
        if p["request_sha256"] != req.request_sha256 or p["scientific_request_sha256"] != req.scientific_request_sha256:
            raise ValueError("projection request digest differs")
        if p["source_receipt"] != request["sources"] or (
                p["artifact_binding"]["collection_scientific_identity_sha256"]
                if v4 else p["artifact_binding"]["root_content_sha256"]) != \
                request["bindings"]["expected_source_content_sha256"]:
            raise ValueError("projection source authentication differs")
        if v4:
            validate_native_v4_receipts(p,request)
        expected = req.expected_point_keys
        if p["resolved"]["expected_point_keys"] != expected:
            raise ValueError("resolved expected natural domain differs")
        domain = {canonical(k) for k in expected}
        if unique(p["points"], "point results", lambda x: canonical(x["key"])) != domain or unique(p["materialization"], "point materialization", lambda x: canonical(x["point_key"])) != domain:
            raise ValueError("projection exact requested point domain differs")
        if expected_routes is not None and p["primitive_routes"] != expected_routes:
            raise ValueError("actual authenticated primitive routes differ")
        unique(p["primitive_routes"], "primitive routes", lambda x: (x["primitive_family"], x["profile_id"]))
        for route in p["primitive_routes"]:
            if route["route"] not in request["execution"]["permitted_routes"] or len(route["root_object_names"]) != len(route["object_content_digests"]) or not route["root_object_names"]:
                raise ValueError("primitive route/object binding differs")
            exactness = dict(COMPACT_PRIMITIVES="PREAGGREGATED_REQUEST", NATIVE_ALIGNED_SPARSE="ALIGNED_RECTANGLE", EXACT_PREFILTERED_SPARSE="EXACT_PREDICATE_THEN_ALIGNED_BINS", EXACT_ROWS="BINARY64_ROWS")
            if route["exactness"] != exactness[route["route"]]:
                raise ValueError("primitive route exactness differs")
        synthetic_routes = [route for route in p["primitive_routes"]
                            if route["source_kind"] == "TEST_ONLY_SYNTHETIC"]
        if synthetic_routes and (
                len(synthetic_routes) != len(p["primitive_routes"]) or
                any(route["route"] != "EXACT_ROWS" for route in synthetic_routes) or
                p["campaign_state"] != "PARTIAL_SAMPLE" or
                request["completion"]["require_campaign_complete"] or
                p["provenance"]["generator_name"] != "TEST_ONLY_SYNTHETIC_LITERAL_GENERATOR" or
                "TEST_ONLY_SYNTHETIC_NO_PHYSICS" not in p["provenance"]["data_limitations"] or
                any(capability["supported"] for capability in p["capability_receipt"])):
            raise ValueError("TEST_ONLY_SYNTHETIC route cannot claim production/campaign acceptance")
        if (p["resolved"]["profiles"] != request["profiles"] or p["resolved"]["axes"] != request["axes"] or
                p["resolved"]["signed_pairs"] != request["scope"]["ordered_associate_pairs"]):
            raise ValueError("resolved request predicates/axes/signed pairs differ")
        support = p['resolved']['observed_support']
        if unique(support, 'observed support', lambda s:(s['role_id'],s['tune_id'],s['axis_id']),nonempty=False) != \
                {(s['role_id'],s['tune_id'],s['axis_id']) for s in observed_support(request,p['points'],p['materialization'])}:
            raise ValueError('observed support domain differs')
        for stored, expected_support in zip(support, observed_support(request,p['points'],p['materialization'])):
            if stored != expected_support and not (stored['status']=='TEST_ONLY_LITERAL' and
                    p['campaign_state']=='PARTIAL_SAMPLE' and
                    stored['nonzero_bins']==sorted(set(stored['nonzero_bins'])) and
                    stored['first_nonzero']==(stored['nonzero_bins'][0] if stored['nonzero_bins'] else None) and
                    stored['last_nonzero']==(stored['nonzero_bins'][-1] if stored['nonzero_bins'] else None)):
                raise ValueError('observed support differs from saved point values')
        category = p['resolved']['category_order']
        labels = {}
        for item in category:
            if len(item['associate_pdgs']) != len(item['labels']):
                raise ValueError('category labels differ from signed categories')
            for pdg,label in zip(item['associate_pdgs'],item['labels']):
                if pdg in labels and labels[pdg] != label:
                    raise ValueError('signed category label identity differs')
                labels[pdg] = label
        if category != category_order(request,labels):
            raise ValueError('category order differs from requested signed keys')
        expected_classes = {(t, c["id"]) for t in request["scope"]["ordered_tunes"] for c in request["classes"]}
        if unique(p["resolved"]["class_boundaries"], "resolved class boundaries", lambda c: (c["tune_id"],c["class_id"])) != expected_classes:
            raise ValueError("resolved requested class domain differs")
        if unique(p["capability_receipt"], "required capability receipts", lambda c:c["capability_id"]) != set(request["execution"]["required_capabilities"]):
            raise ValueError("required capability receipt domain differs")
        provenance = p["provenance"]
        if provenance["selection_definitions_sha256"] != digest(dict(
                profiles=request["profiles"], activity=request["activity"], classes=request["classes"])):
            raise ValueError("provenance selection definitions differ from requested predicates")
        if v4 or not cold:
            validate_profile_routes(request["profiles"], request["science_contract"]["structural_registry_sha256"],
                                    provenance["source_selection_definitions"], p["primitive_routes"])
        for name in ("analysis_config_sha256", "particle_registry_sha256", "activity_definition_sha256"):
            if provenance[name] != request["bindings"][name]:
                raise ValueError("provenance current request binding differs")
        if digest(provenance["runtime"]) != provenance["normalized_runtime_id"]:
            raise ValueError("normalized runtime identity differs")
        materialization = {canonical(x["point_key"]): x for x in p["materialization"]}
        by_key = {canonical(x["key"]): x for x in p["points"]}
        group_key_sets = {g["id"]: {canonical(k) for k in g["ordered_point_keys"]} for g in request["statistics"]["covariance_groups"]}
        for point in p["points"]:
            if point["semantic_id"] != semantic_id(req, point["key"]):
                raise ValueError("semantic point identity differs")
            if point["units"] != expected_point_units(point["key"]["curve"]["quantity"]):
                raise ValueError("point scientific units differ")
            memberships = [g["id"] for g in request["statistics"]["covariance_groups"] if canonical(point["key"]) in group_key_sets[g["id"]]]
            if point["covariance_group_ids"] != memberships:
                raise ValueError("point covariance membership differs")
            if point["center_status"] not in request["completion"]["permitted_scientific_statuses"] or point["uncertainty_status"] not in request["completion"]["permitted_scientific_statuses"]:
                raise ValueError("point scientific state is not permitted")
            if point["center_status"] in ("UNDEFINED", "EMPTY_CLASS", "INCOMPLETE_BLOCK_COVERAGE") and point["center"] is not None:
                raise ValueError("undefined point carries a center")
            present = materialization[canonical(point["key"])]["status"] == "PRESENT"
            if present:
                curve = point["key"]["curve"]
                families = {curve["tune_id"]} | ({curve["reference_tune_id"]} if curve["reference_tune_id"] is not None else set())
                expected_blocks = {(t,b) for t in families for b in range(1,11)}
                if unique(point["block_values"], "point primitive block receipts", lambda b:(b["tune_id"],b["block_id"])) != expected_blocks:
                    raise ValueError("point primitive K10 family domain differs")
                if v4:
                    moment_index={(r['tune_id'],r['block_id']):r for r in
                                  p['event_moment_receipts']}
                    for block in point['block_values']:
                        receipt=moment_index[block['tune_id'],block['block_id']]
                        if block['event_moments_sha256']!=receipt['content_sha256'] or \
                                any(block[field]!=receipt[field] for field in
                                    ('events','sumw','sumw2','sumabsw',
                                     'event_weight_terms')):
                            raise ValueError('point block/event moment reference differs')
                        components=block['additive_components']
                        if len({c['id'] for c in components})!=len(components):
                            raise ValueError('point additive component identity differs')
            validate_point_denominators(point, present)
            available = point["uncertainty_status"] in ("AVAILABLE", "AVAILABLE_ZERO_DISPERSION")
            if available != (point["standard_error"] is not None and point["variance"] is not None):
                raise ValueError("independent uncertainty status/value differs")
            if not available and (point["standard_error"] is not None or point["variance"] is not None):
                raise ValueError("withheld uncertainty carries an error")
            if point["center_status"] in ("AVAILABLE", "AVAILABLE_ZERO_DISPERSION", "UNSTABLE_DENOMINATOR") and point["center"] is None:
                raise ValueError("available/unstable central value is missing")
            if available and point["center"] is None:
                raise ValueError("uncertainty exists without a center")
            if available:
                error, variance = number(point["standard_error"]), number(point["variance"])
                if error < 0 or variance < 0 or not math.isclose(error * error, variance, rel_tol=1e-12, abs_tol=1e-30):
                    raise ValueError("variance/error relation differs")
                if (point["uncertainty_status"] == "AVAILABLE_ZERO_DISPERSION") != (variance == 0):
                    raise ValueError("zero dispersion state differs")
            if materialization[canonical(point["key"])]["status"] != "PRESENT" and (point["center"] is not None or available):
                raise ValueError("nonmaterialized point carries invented science")
        groups = {g["id"]: g for g in request["statistics"]["covariance_groups"]}
        if unique(p["covariance"], "covariance results", lambda x: x["id"]) != set(groups):
            raise ValueError("requested covariance group domain differs")
        for cov in p["covariance"]:
            g = groups[cov["id"]]
            if cov["ordered_point_keys"] != g["ordered_point_keys"] or cov["representation"] != g["representation"] or (cov["K"], cov["dof"]) != (10, 9):
                raise ValueError("joint covariance domain/policy differs")
            selected = [by_key[canonical(k)] for k in cov["ordered_point_keys"]]
            mask = [x["uncertainty_status"] in ("AVAILABLE", "AVAILABLE_ZERO_DISPERSION") for x in selected]
            state = "AVAILABLE_FULL" if all(mask) else "AVAILABLE_PARTIAL" if any(mask) else "UNAVAILABLE"
            if cov["valid_mask"] != mask or cov["status"] != state or cov["units_by_point"] != [x["units"] for x in selected]:
                raise ValueError("joint covariance validity mask/status differs")
            n = len(selected)
            if cov["representation"] == "DENSE":
                matrix = cov["dense_rows"]
                if matrix is None or len(matrix) != n or any(len(r) != n for r in matrix):
                    raise ValueError("joint covariance matrix dimensions differ")
                for i, row in enumerate(matrix):
                    for j, value in enumerate(row):
                        if (value is not None) != (mask[i] and mask[j]):
                            raise ValueError("joint covariance null mask differs")
                        if value is not None and not math.isclose(number(value), number(matrix[j][i]), rel_tol=1e-12, abs_tol=1e-30):
                            raise ValueError("joint covariance symmetry differs")
                    if mask[i] and not math.isclose(number(row[i]), number(selected[i]["variance"]), rel_tol=1e-12, abs_tol=1e-30):
                        raise ValueError("joint covariance diagonal differs")
            elif cov["dense_rows"] is not None or cov["factors_root_object"] is None:
                raise ValueError("ROOT factor representation differs")
            unique(cov["independent_families"], "independent covariance families", lambda x: x["tune_id"], nonempty=any(mask))
            factor_variance=[0.0]*n
            for family in cov["independent_families"]:
                if family["block_ids"] != list(range(1, 11)) or family["covariance_prefactor"] != hex64(.9) or len(family["complements"]) != 10 or any(len(r) != n for r in family["complements"]) or len(family["leave_mean"]) != n:
                    raise ValueError("joint independent-family block alignment differs")
                if family["source_family_digest"] != digest([m for m in request["sources"]["members"] if m["tune_id"] == family["tune_id"]]):
                    raise ValueError("independent family source identity differs")
                for i, point in enumerate(selected):
                    curve = point["key"]["curve"]
                    participates = mask[i] and family["tune_id"] in {curve["tune_id"], curve["reference_tune_id"]}
                    if v4:
                        leaves=[row[i] for row in family['complements']]
                        finite=[leaf is not None for leaf in leaves]
                        if (len(family['finite_mask'])!=10 or
                                any(len(row)!=n for row in family['finite_mask']) or
                                len(family['usable_mask'])!=n or
                                [row[i] for row in family['finite_mask']]!=finite or
                                family['usable_mask'][i]!=participates):
                            raise ValueError('independent family finite/usable masks differ')
                        in_family=family['tune_id'] in {
                            curve['tune_id'],curve['reference_tune_id']}
                        if not in_family and (any(finite) or
                                family['leave_mean'][i] is not None):
                            raise ValueError('foreign deletion family carries leaves')
                        if participates and not all(finite):
                            raise ValueError('usable covariance family lacks finite leaves')
                        expected_mean=(math.fsum(number(leaf) for leaf in leaves)/10
                                       if all(finite) else None)
                        actual_mean=family['leave_mean'][i]
                        if (actual_mean is None)!=(expected_mean is None) or (
                                expected_mean is not None and not math.isclose(
                                    number(actual_mean),expected_mean,
                                    rel_tol=1e-12,abs_tol=1e-30)):
                            raise ValueError('delete-one family mean differs from finite leaves')
                        if participates:
                            mean=number(actual_mean)
                            factor_variance[i]+=0.9*math.fsum(
                                (number(leaf)-mean)**2 for leaf in leaves)
                    elif (family["leave_mean"][i] is not None) != participates or any((row[i] is not None) != participates for row in family["complements"]):
                        raise ValueError("independent family point null mask differs")
            needed_families = {t for point, valid in zip(selected,mask) if valid for t in (point["key"]["curve"]["tune_id"],point["key"]["curve"]["reference_tune_id"]) if t is not None}
            if v4:
                needed_families |= {f['tune_id'] for f in cov['independent_families']
                    if any(any(row) for row in f['finite_mask'])}
                for i,point in enumerate(selected):
                    if mask[i] and (not math.isclose(factor_variance[i],
                            number(point['variance']),rel_tol=1e-12,
                            abs_tol=1e-30) or not math.isclose(
                            math.sqrt(factor_variance[i]),
                            number(point['standard_error']),rel_tol=1e-12,
                            abs_tol=1e-30)):
                        raise ValueError('factor diagonal differs from point variance/error')
                diagnostics=cov['numerical_diagnostics']
                if (diagnostics['method_id']!='K10_FACTOR_DIAGONAL_CHECK' or
                        diagnostics['status']!='PASS' or
                        diagnostics['valid_dimension']!=sum(mask) or
                        diagnostics['accepted_rounding_bound']!=hex64(1e-12)):
                    raise ValueError('factor diagonal diagnostic claim differs')
            if {f["tune_id"] for f in cov["independent_families"]} != needed_families:
                raise ValueError("independent covariance family domain differs")
            if cov["rank_bound"] > 9 * len(cov["independent_families"]):
                raise ValueError("joint covariance rank bound differs")
            payload = {k: v for k, v in cov.items() if k != "content_sha256"}
            if digest(payload) != cov["content_sha256"]:
                raise ValueError("joint covariance content identity differs")
        complete = all(x["status"] == "PRESENT" for x in p["materialization"])
        if p["package_state"] != ("VALIDATED_COMPLETE" if complete else "VALIDATED_PARTIAL"):
            raise ValueError("projection materialization completion differs")
        if request["completion"]["require_campaign_complete"] and p["campaign_state"] != "FULL_ACCEPTED_CAMPAIGN":
            raise ValueError("projection requires full accepted campaign exposure")
        content = {k: p[k] for k in ("scientific_request_sha256", "resolved", "points", "covariance", "materialization")}
        if v4:
            content['event_moment_receipts']=p['event_moment_receipts']
            content['support_diagnostic_receipts']=p['support_diagnostic_receipts']
            content['class_boundary_deletions']=p['class_boundary_deletions']
        if digest(content) != p["science_content_sha256"]:
            raise ValueError("projection result scientific content identity differs")


_REDUCER = None
_QUERY_MODEL = None
def _query_model():
    global _QUERY_MODEL
    if _QUERY_MODEL is None:
        spec = importlib.util.spec_from_file_location(
            "projection_query_model", ROOT / "pipeline/query/model.py")
        _QUERY_MODEL = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_QUERY_MODEL)
    return _QUERY_MODEL

def _reducer():
    global _REDUCER
    if _REDUCER is None:
        spec = importlib.util.spec_from_file_location("projection_io_helpers", ROOT / "pipeline/query/support.py")
        _REDUCER = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_REDUCER)
    return _REDUCER


def expected_denominator_parents(key):
    """Declared C++ formula parents, in deterministic emission order."""
    curve = key["curve"]
    quantity = curve["quantity"]
    if quantity in ("ordered_pair_yield", "os_minus_ss_per_trigger", "dphi_per_trigger", "dphi_density_per_trigger"):
        return [("trigger", True)]
    if quantity in ("normalized_distribution", "normalized_spectrum"):
        return [("normalization_total", True)]
    if quantity == "spectrum_ratio_to_reference_tune":
        return [("source_normalization_total", True),
                ("reference_normalization_total", True),
                ("reference_tune_bin_" + str(key["bins"][0]["index"]), True)]
    if quantity in ("raw_count", "raw_weighted_sum"):
        return []
    if quantity == "normalized_yield":
        return [("accepted_event_exposure", True)]
    if quantity == "baryon_meson_reference_ratio":
        return [("shared_trigger", False), ("reference_os_minus_ss", True)]
    if quantity == "baryon_meson_ratio_to_reference_tune":
        return [("source_shared_trigger", False), ("source_meson_os_minus_ss", True),
                ("reference_shared_trigger", False), ("reference_meson_os_minus_ss", False),
                ("reference_tune_numerator_os_minus_ss", True)]
    if quantity == "ratio_to_reference_tune":
        if curve["role_id"] == "multiplicity.composite":
            if len(key["bins"]) != 1 or key["bins"][0]["axis_id"] != "nch":
                raise ValueError("multiplicity denominator bin identity differs")
            return [("reference_tune_bin_" + str(key["bins"][0]["index"]), True)]
        if curve["role_id"].startswith("correlations."):
            return [("reference_tune_" + curve["component"].lower(), True)]
        return [("reference_tune_os_minus_ss", True)]
    raise ValueError("point denominator formula contract is absent")


def validate_point_denominators(point, present):
    expected = [(canonical(point["key"]) + "/parent=" + name, survives)
                for name, survives in expected_denominator_parents(point["key"])] if present else []
    receipts = point["denominator_receipts"]
    if [(d["natural_key"], d["retained_after_algebra"]) for d in receipts] != expected:
        raise ValueError("point denominator reference domain/order differs")
    expected_parents = []
    for denominator in receipts:
        if len(denominator["delete_one_statuses"]) != 10:
            raise ValueError("denominator K10 status domain differs")
        if denominator["policy_id"] != ESTIMATOR:
            raise ValueError("point denominator policy differs")
        expected_parents.append(dict(natural_key=denominator["natural_key"],
            exists=denominator["status"] != "UNDEFINED", materialized=True,
            content_digest=digest(denominator), coverage_status="COMPLETE_K10"))
    if point["semantic_parents"] != expected_parents:
        raise ValueError("point denominator parent content binding differs")
