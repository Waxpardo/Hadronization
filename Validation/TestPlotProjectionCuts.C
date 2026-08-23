#include "../plotting/improvedPlotting_THnSparse.C"
#include "../plotting/GeneratedMultiplicityPercentileClasses.h"

#include <TMemFile.h>
#include <THnSparse.h>

#include <cmath>
#include <functional>
#include <iostream>
#include <memory>
#include <stdexcept>

namespace {

PairInputSelectionContract CentralPairSelectionContract() {
  return ParsePairInputSelectionContract(json{
      {"mode", "v2_metadata_or_tagged_legacy_recuts_v1"},
      {"legacy_metadata_free_complete_root_tag",
       "complete_root_21_06_2026"},
      {"histogram_pt_eta_fields", "legacy_recuts_only_v1"},
      {"v2_analysis_schema", "paul_pair_objects_primary_ground_v2"},
      {"v2_analysis_implementation",
       "one_pass_primary_ground_pair_analysis_v2"},
      {"v2_analysis_version", "status_analysis_THnSparse_qq_v2"},
      {"v2_analysis_profile", "central_primary_ground_v1"},
      {"v2_selector_version",
       "hard_trigger_primary_ground__primary_ground_associate_v1"},
      {"v2_pair_combinatorics_mode", "ordered_conditional_v1"},
      {"v2_trigger_pt_min_exclusive", 1.0},
      {"v2_associate_pt_min_exclusive", 0.15},
      {"v2_eta_abs_max_inclusive", 4.0},
      {"v2_same_sign_pair_factor", 1.0},
      {"v2_pt_upper_selection", "none"}});
}

void WriteV2SelectionMetadata(TFile& file,
                              Double_t associatePtMin = 0.15) {
  file.cd();
  TObjString("paul_pair_objects_primary_ground_v2")
      .Write("analysis_schema");
  TObjString("one_pass_primary_ground_pair_analysis_v2")
      .Write("analysis_implementation");
  TObjString("status_analysis_THnSparse_qq_v2")
      .Write("analysis_version");
  TObjString("central_primary_ground_v1").Write("analysis_profile");
  TObjString(Hadronization::kAssociateOriginCategorySchema)
      .Write("associate_origin_category_schema");
  TObjString(Hadronization::kAssociateOriginCategoryLabels)
      .Write("associate_origin_category_labels");
  TObjString("hard_trigger_primary_ground__primary_ground_associate_v1")
      .Write("selector_version");
  TObjString("ordered_conditional_v1").Write("pair_combinatorics_mode");
  TParameter<double>("trigger_pt_min_exclusive", 1.0).Write();
  TParameter<double>("associate_pt_min_exclusive", associatePtMin).Write();
  TParameter<double>("eta_abs_max_inclusive", 4.0).Write();
  TParameter<double>("same_sign_pair_factor", 1.0).Write();
  file.Flush();
}

bool Throws(const std::function<void()>& operation) {
  try {
    operation();
  } catch (const std::runtime_error&) {
    return true;
  }
  return false;
}

bool CheckedMultiplicityOrderIsValid(const std::string& path,
                                     bool hasIntegratedBin) {
  std::ifstream input(path);
  if (!input) return false;
  json configuration;
  input >> configuration;
  ParsePairInputSelectionContract(
      configuration.at("pair_input_selection_contract"));

  // Ruling R10: the class set comes from
  // config/multiplicity_percentile_classes_v2.json through the generated
  // header, so this check cannot go on passing against a retired axis.
  const std::vector<std::pair<Double_t, Double_t>> expected = {
      HADRONIZATION_MULTIPLICITY_PERCENTILE_WINDOWS};
  const auto& bins = configuration.at("histograms_to_analyse");
  const std::size_t offset = hasIntegratedBin ? 1U : 0U;
  if (bins.size() != expected.size() + offset) return false;
  if (hasIntegratedBin &&
      (bins[0].at("multiplicityMin").get<Double_t>() != 0.0 ||
       bins[0].at("multiplicityMax").get<Double_t>() != 100.0)) {
    return false;
  }
  for (std::size_t index = 0; index < expected.size(); ++index) {
    const auto& bin = bins[index + offset];
    if (bin.at("multiplicityMin").get<Double_t>() !=
            expected[index].first ||
        bin.at("multiplicityMax").get<Double_t>() !=
            expected[index].second) {
      return false;
    }
  }
  return true;
}

}  // namespace

int TestPlotProjectionCuts() {
  const Int_t correlationBins[7] = {16, 16, 16, 16, 100, 100, 128};
  const Double_t correlationMinimum[7] = {
      -M_PI / 2.0, -8.0, -8.0, -8.0, 0.0, 0.0, -0.5};
  const Double_t correlationMaximum[7] = {
      3.0 * M_PI / 2.0, 8.0, 8.0, 8.0, 100.0, 100.0, 127.5};
  THnSparseD correlation("testCorrelation", "test", 7, correlationBins,
                         correlationMinimum, correlationMaximum);
  correlation.Sumw2();

  const Int_t triggerBins[4] = {16, 16, 100, 128};
  const Double_t triggerMinimum[4] = {-M_PI, -8.0, 0.0, -0.5};
  const Double_t triggerMaximum[4] = {M_PI, 8.0, 100.0, 127.5};
  THnSparseD trigger("testTrigger", "test", 4, triggerBins, triggerMinimum,
                     triggerMaximum);
  trigger.Sumw2();

  const Double_t acceptedCorrelation[7] = {0.1, 0.2, 0.0, 0.0,
                                           5.0, 1.0, 10.0};
  const Double_t highPtCorrelation[7] = {0.1, 0.2, 0.0, 0.0,
                                         25.0, 1.0, 10.0};
  const Double_t highEtaCorrelation[7] = {0.1, 0.2, 5.0, 0.0,
                                          5.0, 1.0, 10.0};
  correlation.Fill(acceptedCorrelation);
  correlation.Fill(highPtCorrelation);
  correlation.Fill(highEtaCorrelation);

  const Double_t acceptedTrigger[4] = {0.1, 0.0, 5.0, 10.0};
  const Double_t highPtTrigger[4] = {0.1, 0.0, 25.0, 10.0};
  const Double_t highEtaTrigger[4] = {0.1, 5.0, 5.0, 10.0};
  trigger.Fill(acceptedTrigger);
  trigger.Fill(highPtTrigger);
  trigger.Fill(highEtaTrigger);

  BinsFromTHnSparse cuts{};
  cuts.triggerPhiMin = -M_PI;
  cuts.triggerPhiMax = M_PI;
  cuts.assocPhiMin = -M_PI;
  cuts.assocPhiMax = M_PI;
  cuts.triggerEtaMin = -4.0;
  cuts.triggerEtaMax = 4.0;
  cuts.assocEtaMin = -4.0;
  cuts.assocEtaMax = 4.0;
  cuts.triggerPtMin = 1.0;
  cuts.triggerPtMax = 20.0;
  cuts.assocPtMin = 0.0;
  cuts.assocPtMax = 100.0;
  cuts.multiplicityMin = 0.0;
  cuts.multiplicityMax = 100.0;

  std::unique_ptr<TH1D> projectedCorrelation(GetCorrelationHistograms(
      &correlation, cuts,
      PairSelectionProjectionMode::kLegacyPlotRecutsV1, "cutTest"));
  std::unique_ptr<TH1D> projectedTrigger(GetTriggerPtHistograms(
      &trigger, cuts,
      PairSelectionProjectionMode::kLegacyPlotRecutsV1, "cutTest"));
  if (projectedCorrelation->Integral() != 1.0 ||
      projectedTrigger->Integral() != 1.0) {
    std::cerr << "PLOT_PROJECTION_TEST_ERROR correlation="
              << projectedCorrelation->Integral()
              << " trigger=" << projectedTrigger->Integral() << "\n";
    return 1;
  }

  bool rejectedUnsupportedPhi = false;
  try {
    BinsFromTHnSparse unsupported = cuts;
    unsupported.triggerPhiMin = -1.0;
    std::unique_ptr<TH1D> invalid(GetCorrelationHistograms(
        &correlation, unsupported,
        PairSelectionProjectionMode::kLegacyPlotRecutsV1, "invalid"));
  } catch (const std::runtime_error&) {
    rejectedUnsupportedPhi = true;
  }
  if (!rejectedUnsupportedPhi) {
    std::cerr << "PLOT_PROJECTION_TEST_ERROR unsupported phi cut accepted\n";
    return 2;
  }

  THnSparseD v2Correlation(
      "v2Correlation", "test", 7, correlationBins,
      correlationMinimum, correlationMaximum);
  THnSparseD v2Trigger(
      "v2Trigger", "test", 4, triggerBins, triggerMinimum, triggerMaximum);
  v2Correlation.Sumw2();
  v2Trigger.Sumw2();
  v2Correlation.Fill(acceptedCorrelation);
  v2Correlation.Fill(highPtCorrelation);
  v2Trigger.Fill(acceptedTrigger);
  v2Trigger.Fill(highPtTrigger);
  std::unique_ptr<TH1D> projectedV2Correlation(
      GetCorrelationHistograms(
          &v2Correlation, cuts,
          PairSelectionProjectionMode::kUpstreamSelectedV2, "v2"));
  std::unique_ptr<TH1D> projectedV2Trigger(
      GetTriggerPtHistograms(
          &v2Trigger, cuts,
          PairSelectionProjectionMode::kUpstreamSelectedV2, "v2"));
  if (projectedV2Correlation->Integral() != 2.0 ||
      projectedV2Trigger->Integral() != 2.0) {
    std::cerr
        << "PLOT_PROJECTION_TEST_ERROR v2 high-pT entry was re-cut"
        << " correlation=" << projectedV2Correlation->Integral()
        << " trigger=" << projectedV2Trigger->Integral() << "\n";
    return 3;
  }

  const PairInputSelectionContract selectionContract =
      CentralPairSelectionContract();
  TMemFile v2MetadataFile("v2MetadataFile.root", "RECREATE");
  WriteV2SelectionMetadata(v2MetadataFile);
  if (ValidatePairInputSelectionContract(
          &v2MetadataFile, selectionContract,
          "canonical_complete_root_v2", "v2MetadataFile.root") !=
      PairSelectionProjectionMode::kUpstreamSelectedV2) {
    std::cerr << "PLOT_PROJECTION_TEST_ERROR v2 metadata not selected\n";
    return 4;
  }

  TMemFile mismatchedMetadataFile(
      "mismatchedMetadataFile.root", "RECREATE");
  WriteV2SelectionMetadata(mismatchedMetadataFile, 0.2);
  if (!Throws([&]() {
        ValidatePairInputSelectionContract(
            &mismatchedMetadataFile, selectionContract,
            "canonical_complete_root_v2",
            "mismatchedMetadataFile.root");
      })) {
    std::cerr
        << "PLOT_PROJECTION_TEST_ERROR metadata mismatch accepted\n";
    return 5;
  }

  TMemFile partialMetadataFile("partialMetadataFile.root", "RECREATE");
  partialMetadataFile.cd();
  TObjString("paul_pair_objects_primary_ground_v2")
      .Write("analysis_schema");
  partialMetadataFile.Flush();
  if (!Throws([&]() {
        ValidatePairInputSelectionContract(
            &partialMetadataFile, selectionContract,
            "complete_root_21_06_2026",
            "partialMetadataFile.root");
      })) {
    std::cerr
        << "PLOT_PROJECTION_TEST_ERROR partial metadata used legacy fallback\n";
    return 6;
  }

  TMemFile legacyMetadataFreeFile(
      "legacyMetadataFreeFile.root", "RECREATE");
  if (ValidatePairInputSelectionContract(
          &legacyMetadataFreeFile, selectionContract,
          "complete_root_21_06_2026",
          "legacyMetadataFreeFile.root") !=
      PairSelectionProjectionMode::kLegacyPlotRecutsV1) {
    std::cerr
        << "PLOT_PROJECTION_TEST_ERROR legacy recut mode unavailable\n";
    return 7;
  }
  if (!Throws([&]() {
        ValidatePairInputSelectionContract(
            &legacyMetadataFreeFile, selectionContract,
            "unreviewed_metadata_free_tag",
            "legacyMetadataFreeFile.root");
      })) {
    std::cerr
        << "PLOT_PROJECTION_TEST_ERROR untagged metadata-free input accepted\n";
    return 8;
  }
  if (!Throws([&]() {
        RequireMatchingPairSelectionModes(
            PairSelectionProjectionMode::kUpstreamSelectedV2,
            PairSelectionProjectionMode::kLegacyPlotRecutsV1,
            "toy mixed central/block");
      })) {
    std::cerr
        << "PLOT_PROJECTION_TEST_ERROR mixed selection modes accepted\n";
    return 9;
  }

  if (!IsIntegratedMultiplicityBin(cuts)) {
    std::cerr << "PLOT_PROJECTION_TEST_ERROR integrated-bin detection\n";
    return 10;
  }
  BinsFromTHnSparse nonIntegrated = cuts;
  nonIntegrated.multiplicityMin = 1.0;
  nonIntegrated.multiplicityMax = 10.0;
  if (IsIntegratedMultiplicityBin(nonIntegrated)) {
    std::cerr << "PLOT_PROJECTION_TEST_ERROR nonintegrated bin accepted\n";
    return 11;
  }
  CONFIGS canvasConfig{};
  canvasConfigs smokeCanvas{};
  smokeCanvas.FLAVOUR = "CHARM";
  smokeCanvas.TriggerToUse = "D^{+}";
  smokeCanvas.vBinsToIgnore = {"hDPhiM90_100"};
  canvasConfig.vCanvasConfigs.push_back(smokeCanvas);
  if (IsBinUsedByAnyCanvas(
          canvasConfig, "CHARM", "D^{+}", "hDPhiM90_100") ||
      !IsBinUsedByAnyCanvas(
          canvasConfig, "CHARM", "D^{+}", "hDPhiM1_10") ||
      IsBinUsedByAnyCanvas(
          canvasConfig, "BEAUTY", "B^{+}", "hDPhiM1_10")) {
    std::cerr << "PLOT_PROJECTION_TEST_ERROR canvas-bin selection\n";
    return 12;
  }

  const std::map<double, double> toyThresholds = {
      {100.0, 0.0}, {90.0, 1.0}, {80.0, 2.0},
      {70.0, 3.0},  {60.0, 4.0}, {50.0, 5.0},
      {40.0, 6.0},  {30.0, 7.0}, {20.0, 8.0},
      {10.0, 9.0},  {1.0, 10.0}, {0.0, 11.0}};
  const std::vector<std::pair<double, double>> percentileClasses = {
      HADRONIZATION_MULTIPLICITY_PERCENTILE_WINDOWS};
  std::pair<double, double> previousRange = {-1.0, -1.0};
  for (std::size_t index = 0; index < percentileClasses.size(); ++index) {
    const auto range = GetDiscreteMultiplicityRange(
        toyThresholds, percentileClasses[index].first,
        percentileClasses[index].second);
    if (index != 0 && range.first != previousRange.second + 1.0) {
      std::cerr
          << "PLOT_PROJECTION_TEST_ERROR overlapping/gapped Nch classes\n";
      return 13;
    }
    previousRange = range;
  }
  const auto integratedRange =
      GetDiscreteMultiplicityRange(toyThresholds, 0.0, 100.0);
  if (integratedRange.first != 0.0 ||
      integratedRange.second != 11.0) {
    std::cerr
        << "PLOT_PROJECTION_TEST_ERROR integrated Nch range mismatch\n";
    return 14;
  }

  const std::string base = FindHadronizationBase();
  if (!CheckedMultiplicityOrderIsValid(
          JoinPath(
              {base, "plotting",
               "configuration_multiplicity_reduced_JUNCTIONS_THnSparse.json"}),
          true) ||
      !CheckedMultiplicityOrderIsValid(
          JoinPath(
              {base, "plotting",
               "configuration_multiplicity_reduced_JUNCTIONS_THnSparse_complete_root.json"}),
          false)) {
    std::cerr
        << "PLOT_PROJECTION_TEST_ERROR checked multiplicity ordering\n";
    return 15;
  }

  TH1D correlationWithSEM("correlationWithSEM", "test", 2, 0.0, 2.0);
  correlationWithSEM.SetBinContent(1, 5.5);
  std::vector<std::vector<Double_t>> blockBinValues(3);
  for (Int_t value = 1; value <= 10; ++value) {
    blockBinValues[1].push_back(static_cast<Double_t>(value));
    blockBinValues[2].push_back(0.0);
  }
  ApplyCorrelationSubsampleSEM(
      &correlationWithSEM, blockBinValues, 10, "projection_test");
  const Double_t expectedSEM = std::sqrt(82.5 / 9.0) / std::sqrt(10.0);
  if (std::abs(correlationWithSEM.GetBinError(1) - expectedSEM) > 1e-12 ||
      correlationWithSEM.GetBinError(2) != 0.0) {
    std::cerr << "PLOT_PROJECTION_TEST_ERROR block SEM="
              << correlationWithSEM.GetBinError(1)
              << " expected=" << expectedSEM << "\n";
    return 16;
  }

  std::cout << "PLOT_PROJECTION_TEST_PASS legacy=1 v2_high_pt=2"
            << " block_sem=" << correlationWithSEM.GetBinError(1) << "\n";
  return 0;
}
