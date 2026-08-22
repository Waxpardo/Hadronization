#!/usr/bin/env python3
"""Static contract checks for paper reference ratios and Nch freezing."""

from __future__ import annotations

import json
import hashlib
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLOTTER = ROOT / "plotting/improvedPlotting_THnSparse.C"
CLOSURE_PLOTTER = ROOT / "plotting/Plot_FlavourClosure.C"
BOUNDARY_UTILS = ROOT / "plotting/MultiplicityBoundaryUtils.h"
BOUNDARY_PLOTTER = (
    ROOT
    / "plotting/Plot_MultiplicityDistribution_PercentileBoundaries.C"
)
RUNNER = ROOT / "plotting/run_paper_plots.sh"
RAW_PLOTTER = ROOT / "plotting/Plot_InclusiveKinematicSpectra_Raw.C"
FIGURE_ACCEPTANCE_MANIFEST = (
    ROOT / "results/provenance/figure_acceptance_manifest_v1.json"
)
PAIR_REGISTRY = ROOT / "config/heavy_flavour_pair_registry_v1.json"
CONFIGURATIONS = (
    ROOT
    / "plotting/configuration_multiplicity_reduced_JUNCTIONS_THnSparse.json",
    ROOT
    / "plotting/configuration_multiplicity_reduced_JUNCTIONS_THnSparse_complete_root.json",
)
REDUCED_CONFIGURATION = CONFIGURATIONS[1]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_configured_references() -> None:
    registry_document = json.loads(PAIR_REGISTRY.read_text())
    registry = {
        row["filename"]: row for row in registry_document["pairs"]
    }
    assert len(registry) == registry_document["pair_count"] == 300

    for path in CONFIGURATIONS:
        configuration = json.loads(path.read_text())
        assert configuration["pair_combinatorics_mode"] == (
            "ordered_conditional_v1"
        )
        assert configuration["same_sign_pair_factor"] == 1.0
        for sector, key in (
            ("beauty", "beauty_correlations_to_analyse"),
            ("charm", "charm_correlations_to_analyse"),
        ):
            for trigger_group in configuration[key]:
                pairs = trigger_group["configs"]
                references: set[int] = set()
                os_associates: list[int] = []
                triggers: set[int] = set()
                for configured in pairs:
                    os_definition = registry[configured["OS"]]
                    ss_definition = registry[configured["SS"]]
                    assert os_definition["sector"] == sector
                    assert ss_definition["sector"] == sector
                    assert os_definition["heavy_sign"] == "OS"
                    assert ss_definition["heavy_sign"] == "SS"
                    assert (
                        os_definition["trigger_pdg"]
                        == ss_definition["trigger_pdg"]
                    )
                    assert (
                        os_definition["associate_pdg"]
                        == -ss_definition["associate_pdg"]
                    )
                    assert (
                        os_definition["reference_meson_pdg"]
                        == ss_definition["reference_meson_pdg"]
                    )
                    triggers.add(int(os_definition["trigger_pdg"]))
                    references.add(
                        int(os_definition["reference_meson_pdg"])
                    )
                    os_associates.append(
                        int(os_definition["associate_pdg"])
                    )
                assert len(triggers) == 1
                assert len(references) == 1
                reference = next(iter(references))
                assert os_associates.count(reference) == 1, (
                    f"{path.name}:{trigger_group['trigger']} must configure "
                    f"exactly one signed reference PDG {reference}"
                )

    reduced = json.loads(REDUCED_CONFIGURATION.read_text())
    assert reduced["calculate_errors"] is True
    assert reduced["nSubSamples"] == 10
    assert reduced["PYTHIA_TUNES"] == [
        "MONASH",
        "JUNCTIONS",
        "CLOSEPACKING",
    ]
    assert [
        row["associateOS"]
        for group in reduced["beauty_correlations_to_analyse"]
        for row in group["configs"]
    ] == ["B-", "Lambda_b"]
    assert [
        row["associateOS"]
        for group in reduced["charm_correlations_to_analyse"]
        for row in group["configs"]
    ] == ["D-", "Lambda_c(+)-bar"]
    assert [
        group["trigger"]
        for group in reduced["beauty_correlations_to_analyse"]
    ] == ["B^{+}"]
    assert [
        group["trigger"]
        for group in reduced["charm_correlations_to_analyse"]
    ] == ["D^{+}"]
    canvases = reduced["canvases_to_be_drawn"]
    assert len(canvases) == 16
    assert all(canvas["canvas_name"].startswith("mini_") for canvas in canvases)
    assert {canvas["TriggerToUse"] for canvas in canvases} == {
        "B^{+}",
        "D^{+}",
    }
    activity_bins = {
        "hDPhiM90_100",
        "hDPhiM80_90",
        "hDPhiM70_80",
        "hDPhiM60_70",
        "hDPhiM50_60",
        "hDPhiM40_50",
        "hDPhiM30_40",
        "hDPhiM20_30",
        "hDPhiM10_20",
        "hDPhiM1_10",
        "hDPhiM0_1",
    }
    assert all(
        activity_bins - set(canvas["bins_to_ignore"])
        == {"hDPhiM1_10"}
        for canvas in canvases
    )
    configured_canvas_names = {
        canvas["canvas_name"] for canvas in canvases
    }
    for global_canvas in reduced["global_canvases_to_be_drawn"]:
        assert set(global_canvas["mini_canvases"]) <= configured_canvas_names
    assert "Sigma_b" not in json.dumps(reduced)
    assert "lambda_sigma" not in json.dumps(reduced)
    assert [
        row["hDPhi"] for row in reduced["histograms_to_analyse"]
    ] == [
        "hDPhiM90_100",
        "hDPhiM80_90",
        "hDPhiM70_80",
        "hDPhiM60_70",
        "hDPhiM50_60",
        "hDPhiM40_50",
        "hDPhiM30_40",
        "hDPhiM20_30",
        "hDPhiM10_20",
        "hDPhiM1_10",
        "hDPhiM0_1",
    ]


def check_plotter_contract() -> None:
    source = PLOTTER.read_text()
    boundary_source = BOUNDARY_UTILS.read_text()
    standalone_source = BOUNDARY_PLOTTER.read_text()
    required_fragments = (
        '#include "../AnalysisScripts/GeneratedPairRegistry.h"',
        "ResolveReferenceAssociateSelection",
        "ReferenceFirstAssociateOrder",
        "EvaluateSubsampleTechnicalCoverage",
        "std::hypot",
        '"reference_meson_pdg"',
        '"pair_registry_sha256"',
        "reference_pdg=",
        "reference_index=",
        "is_reference=",
        "CaptureMultiplicityHistogramIdentity",
        "RequireIdenticalMultiplicityHistogram",
        "FreezeAndValidateMultiplicityDefinitions",
        "multiplicityPercentileThresholdsByTune",
        "status=NOT_APPLICABLE",
        "reason=structural_reference_self_ratio",
        "ValidatePairCombinatoricsForSelectionMode",
        "multiplicity_boundary_receipt_v2.json",
        "WriteMultiplicityBoundaryReceipt",
        "Non-positive value cannot be represented on the configured ",
    )
    for fragment in required_fragments:
        assert fragment in source, f"missing plotting contract: {fragment}"
    assert (
        "SUBSAMPLE_COVERAGE_AUDIT &&\n"
        "         boundaryReceiptDirectories.size() > 1U"
    ) in source
    assert (
        "boundaryReceiptDirectories.empty()\n"
        "            ? std::string()"
    ) in source
    audit_branch = re.search(
        r"if \(configs_from_json\.SUBSAMPLE_COVERAGE_AUDIT\) \{"
        r".*?return 0;\n    \}",
        source,
        flags=re.DOTALL,
    )
    assert audit_branch is not None
    assert "WriteMultiplicityBoundaryReceipt" not in audit_branch.group(0)
    assert (
        source.count("WriteMultiplicityBoundaryReceipt(configs_from_json)")
        == 2
    )
    assert source.count("canvasConfigs.setLogy,") == 4
    point_guard = re.search(
        r"void SetPlotPointOrThrow\(.*?\n\}",
        source,
        flags=re.DOTALL,
    )
    assert point_guard is not None
    assert "logarithmicY && value <= 0.0" in point_guard.group(0)
    assert "lowerEnvelope = value - error" in point_guard.group(0)
    assert "upperEnvelope = value + error" in point_guard.group(0)
    assert "logarithmicY && lowerEnvelope <= 0.0" in point_guard.group(0)
    assert "is clipped by " in point_guard.group(0)
    assert "configured y-axis" in point_guard.group(0)

    forbidden_positional_denominators = (
        "vSubYields[i][0][k]",
        "vYields[i][0][k]",
        "vYields[indexNominatorTUNE][0][k]",
        "vYields[indexDenominatorTUNE][0][k]",
    )
    for fragment in forbidden_positional_denominators:
        assert fragment not in source, (
            f"positional reference denominator returned: {fragment}"
        )
    assert "return hMult->GetBinCenter(hMult->GetNbinsX())" not in source
    assert "valueA == 0.0 || valueB == 0.0" not in source
    assert "refusing first/last-bin fallback" in boundary_source
    for fragment in (
        "must both be exactly zero",
        "ThresholdForPercentile",
        "DiscreteClassRange",
        "RequireDiscretePartitionCoverage",
        "achieved_weighted_fraction",
    ):
        assert fragment in source + boundary_source
    assert '#include "MultiplicityBoundaryUtils.h"' in standalone_source
    assert "threshold+0.5" in standalone_source
    assert "MULTIPLICITY_BOUNDARY_RECEIPT_CONSUMED" in standalone_source

    identity_function = re.search(
        r"inline void RequireIdenticalHistogram\(.*?\n\}",
        boundary_source,
        flags=re.DOTALL,
    )
    assert identity_function is not None
    identity_source = identity_function.group(0)
    for field in ("edges", "contents", "errors", "sumw2", "sumw2Size"):
        assert field in identity_source

    trigger_projection = re.search(
        r"TH1D\* GetTriggerPtHistograms\(.*?\n\}",
        source,
        flags=re.DOTALL,
    )
    assert trigger_projection is not None
    trigger_projection_source = trigger_projection.group(0)
    assert "hTrKinematics->Projection(2" in trigger_projection_source
    assert "hCorrelations->Projection" not in trigger_projection_source

    yield_function = re.search(
        r"Double_t calculateOneYield\(.*?\n\}",
        source,
        flags=re.DOTALL,
    )
    assert yield_function is not None
    yield_source = yield_function.group(0)
    for fragment in (
        "hTrPtOS->Integral()",
        "hTrPtSS->Integral()",
        "hDPhiOS->Scale(1.0 / nTriggersOS)",
        "hDPhiSS->Scale(1.0 / nTriggersSS)",
        "hCorr->Add(hDPhiSS, -1.)",
        "hCorr->Integral()",
    ):
        assert fragment in yield_source, (
            f"yield normalization/subtraction contract missing: {fragment}"
        )
    assert "hDPhiOS->Integral() : 0.0" not in yield_source
    assert "hDPhiSS->Integral() : 0.0" not in yield_source

    for fragment in (
        'GetObjectOrThrow<THnSparseD>(OStree, "hTrKinematics"',
        'GetObjectOrThrow<THnSparseD>(SStree, "hTrKinematics"',
        "GetTriggerPtHistograms(\n                        hTrKinematicsOS",
        "GetTriggerPtHistograms(\n                        hTrKinematicsSS",
    ):
        assert fragment in source, (
            f"pair projection replaced the trigger denominator: {fragment}"
        )

    closure_source = CLOSURE_PLOTTER.read_text()
    for fragment in (
        'GetOrThrow<TH1D>(file, "hFlavourClosureSummary")',
        "const double triggers = summary->GetBinContent(1)",
        "fullPhaseSpace / triggers",
        "inAcceptance / triggers",
        "shape->Scale(1.0 / triggers)",
    ):
        assert fragment in closure_source, (
            f"closure diagnostic lost its dedicated trigger counter: {fragment}"
        )
    assert "const double triggers = closure->Projection" not in closure_source


def check_runner_modes() -> None:
    source = RUNNER.read_text()
    for fragment in (
        "legacy-regression",
        "tagged_legacy_recuts_only_v1",
        "legacy_identical_ss_half_v1",
        ".same_sign_pair_factor = 0.5",
        "HADRONIZATION_DATASET_PUBLICATION_ELIGIBLE",
        "canonical plotting/validation is fail-closed",
        "canonical-validation-pair",
        "PREPUBLICATION_CANONICAL_VALIDATION",
    ):
        assert fragment in source
    smoke_case = re.search(
        r"smoke\|quick\)\n(?P<body>.*?)\n      ;;",
        source,
        flags=re.DOTALL,
    )
    assert smoke_case is not None
    smoke_body = smoke_case.group("body")
    assert "freeze-boundaries-smoke" in smoke_body
    assert "thnsparse-complete-root" in smoke_body
    assert "multiplicity-boundaries-smoke" in smoke_body
    assert "kinematic-spectra" not in smoke_body

    raw_source = RAW_PLOTTER.read_text()
    assert (
        "Nch definition: final charged non-heavy particles, "
        "pT > 0.15 GeV/c, |eta| <= 1"
    ) in raw_source
    assert "|eta| <= 4 (not prompt multiplicity)" not in raw_source

    assert "no target writes\nchecksum-bound acceptance sidecars" in source
    assert 'plot_provenance_tool=""' in source


def check_figure_acceptance_manifest() -> None:
    document = json.loads(FIGURE_ACCEPTANCE_MANIFEST.read_text())
    assert document["schema"] == (
        "hadronization_figure_acceptance_manifest_v1"
    )
    assert document["overall_status"] == "blocked"
    assert document["accepted_figure_count"] == 0
    assert document["candidate_figure_count"] == 8
    assert document["accepted_outputs"] == []
    assert document["internal_explanatory_graphics"] == {
        "count": 3,
        "classification": "excluded historical or explanatory artifacts",
        "used_as_scientific_candidates": False,
        "promoted_or_modified_by_this_audit": False,
    }

    dataset = document["dataset_contract"]
    assert dataset["dataset_key"] == "hf_run3_v1_candidate"
    assert dataset["campaign"] == "HF_RUN3_V1"
    assert dataset["publication_eligible"] is True
    assert dataset["sqrt_s_tev"] == 13.6
    assert dataset["tunes"] == [
        "MONASH",
        "JUNCTIONS",
        "CLOSEPACKING",
    ]
    assert dataset["block_count"] == 10
    for key in ("selector_path", "authorization_path"):
        digest_key = key.replace("path", "sha256")
        assert sha256(ROOT / dataset[key]) == dataset[digest_key]

    shared = document["shared_contracts"]
    assert shared["pair_observable"] == {
        "trigger_denominator": "hTrKinematics",
        "same_sign_factor": 1.0,
        "subtraction": "OS - SS",
        "integrated_region": "full Delta phi",
        "statistical_uncertainty": (
            "SEM across ten disjoint blocks; OS - SS is formed "
            "inside each block"
        ),
    }
    assert shared["multiplicity_boundaries"]["common_across_tunes"] is False
    assert "derived independently for each tune" in (
        shared["multiplicity_boundaries"]["definition"])
    assert shared["multiplicity_boundaries"]["classes"] == [
        f"c{index}" for index in range(1, 12)
    ]
    for contract in (
        shared["pair_registry"],
        shared["species_registry"],
        shared["multiplicity_boundaries"],
    ):
        assert sha256(ROOT / contract["path"]) == contract["sha256"]

    blocker_ids = {row["id"] for row in document["release_blockers"]}
    assert blocker_ids == {
        "B1_EXTERNAL_INPUTS_UNAVAILABLE",
        "B2_FINAL_BYTES_AND_RECEIPTS_ABSENT",
        "B3_DERIVED_UNCERTAINTY_FORMULA",
        "B4_S4_SYSTEMATIC_INCOMPLETE",
        "B5_RECORDED_RENDER_NOT_CURRENT_REPRODUCTION",
        "B6_INTEGRATED_CLOSURE_LOG_ABSENT",
        "B7_PAIR_METADATA_SCHEMA_DISAGREEMENT",
        "B8_HARVEST_CONFIGURATION_DRIFT",
    }

    roles = document["roles"]
    assert [row["figure_id"] for row in roles] == [
        f"P{index}" for index in range(1, 9)
    ]
    required_fields = {
        "producer",
        "configuration",
        "dataset_selector_key",
        "dataset_authorized",
        "central_input_identity",
        "ten_block_identity_and_coverage",
        "environment",
        "machine_readable_numerical_source",
        "candidate_outputs",
        "caption_source",
        "visual_review",
        "accepted_outputs",
        "retrieval_requirement",
    }
    for role in roles:
        assert role["status"] == "candidate"
        assert role["dataset_selector_key"] == dataset["dataset_key"]
        assert role["dataset_authorized"] is True
        assert role["accepted_outputs"] == []
        assert required_fields <= role.keys()
        assert role["visual_review"]["result"] == "blocked"
        source = ROOT / role["producer"]["source"]
        assert sha256(source) == role["producer"]["source_sha256"]
        configuration = role["configuration"]
        if configuration.get("path"):
            assert sha256(ROOT / configuration["path"]) == (
                configuration["sha256"]
            )
        for alternative in configuration.get("alternatives", []):
            assert sha256(ROOT / alternative["path"]) == (
                alternative["sha256"]
            )
        for numerical_source in role["machine_readable_numerical_source"]:
            assert sha256(ROOT / numerical_source["path"]) == (
                numerical_source["sha256"]
            )


def main() -> int:
    check_configured_references()
    check_plotter_contract()
    check_runner_modes()
    check_figure_acceptance_manifest()
    cpp_test = (
        ROOT / "Validation/TestPlotReferenceMultiplicityContracts.C"
    )
    assert cpp_test.is_file()
    print("plot reference/multiplicity static contracts passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
