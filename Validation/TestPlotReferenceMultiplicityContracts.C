#include "../PlottingScripts/improvedPlotting_THnSparse.C"

#include <TMemFile.h>

#include <cmath>
#include <filesystem>
#include <functional>
#include <iostream>
#include <limits>
#include <memory>
#include <vector>

namespace {

bool ThrowsRuntimeError(const std::function<void()>& operation) {
  try {
    operation();
  } catch (const std::runtime_error&) {
    return true;
  }
  return false;
}

PairInputSelectionContract TestSelectionContract() {
  PairInputSelectionContract contract;
  contract.mode = "v2_metadata_or_tagged_legacy_recuts_v1";
  contract.legacyMetadataFreeCompleteRootTag =
      "complete_root_21_06_2026";
  contract.pairCombinatoricsMode = "ordered_conditional_v1";
  contract.sameSignPairFactor = 1.0;
  return contract;
}

void WritePairIdentity(
    TFile& file,
    const TriggerAssociateOSandSS& configured,
    bool isOS,
    Int_t referencePdgOffset = 0
) {
  file.cd();
  TObjString(std::string(Hadronization::kPairRegistrySha256).c_str())
      .Write("pair_registry_sha256");
  TObjString("beauty").Write("heavy_sector");
  TObjString(isOS ? "OS" : "SS").Write("heavy_sign");
  TParameter<int>("trigger_pdg", configured.triggerPdg).Write();
  TParameter<int>(
      "associate_pdg",
      isOS ? configured.associateOSPdg : configured.associateSSPdg)
      .Write();
  TParameter<int>(
      "reference_meson_pdg",
      configured.referenceMesonPdg + referencePdgOffset)
      .Write();
  file.Flush();
}

TriggerAssociateOSandSS BeautyPair(
    const std::string& associateOS,
    const std::string& associateSS,
    const std::string& osFile,
    const std::string& ssFile
) {
  return ResolveConfiguredPairFromRegistry(
      "beauty", "B^{+}", "B^{+}",
      associateOS, associateSS, osFile, ssFile);
}

void WriteMultiplicityFile(
    const std::filesystem::path& path,
    const TH1D& source
) {
  std::filesystem::create_directories(path.parent_path());
  TFile output(path.c_str(), "RECREATE");
  if (output.IsZombie()) {
    throw std::runtime_error(
        "cannot create toy multiplicity file " + path.string());
  }
  std::unique_ptr<TH1D> histogram(
      static_cast<TH1D*>(source.Clone("summed MULTIPLICITY")));
  histogram->SetDirectory(nullptr);
  output.cd();
  histogram->Write("summed MULTIPLICITY");
  output.Close();
}

struct TemporaryDirectory {
  std::filesystem::path path;
  ~TemporaryDirectory() {
    std::error_code error;
    std::filesystem::remove_all(path, error);
  }
};

}  // namespace

int TestPlotReferenceMultiplicityContracts() {
  const PairInputSelectionContract mixedContract =
      TestSelectionContract();
  PairInputSelectionContract legacyOnlyContract = mixedContract;
  legacyOnlyContract.mode =
      "tagged_legacy_recuts_only_v1";
  ValidatePairCombinatoricsForSelectionMode(
      PairSelectionProjectionMode::kUpstreamSelectedV2,
      "ordered_conditional_v1", 1.0, mixedContract,
      "canonical-v2-test.root");
  ValidatePairCombinatoricsForSelectionMode(
      PairSelectionProjectionMode::kLegacyPlotRecutsV1,
      "legacy_identical_ss_half_v1", 0.5, legacyOnlyContract,
      "tagged-legacy-test.root");
  if (!ThrowsRuntimeError([&]() {
        ValidatePairCombinatoricsForSelectionMode(
            PairSelectionProjectionMode::kUpstreamSelectedV2,
            "legacy_identical_ss_half_v1", 0.5,
            mixedContract, "v2-with-legacy-factor.root");
      }) ||
      !ThrowsRuntimeError([&]() {
        ValidatePairCombinatoricsForSelectionMode(
            PairSelectionProjectionMode::kLegacyPlotRecutsV1,
            "ordered_conditional_v1", 1.0,
            legacyOnlyContract, "legacy-with-v2-factor.root");
      })) {
    std::cerr
        << "PLOT_REFERENCE_MULTIPLICITY_TEST_ERROR "
        << "pair selection/combinatorics cross-mode rejection\n";
    return 1;
  }

  const Double_t zeroNumeratorError =
      propagateRatioError(0.0, 2.0, 0.4, 0.3);
  const Double_t normalRatioError =
      propagateRatioError(4.0, 2.0, 0.4, 0.2);
  if (std::abs(zeroNumeratorError - 0.2) > 1e-15 ||
      std::abs(normalRatioError - std::sqrt(0.08)) > 1e-15 ||
      std::isfinite(propagateRatioError(1.0, 0.0, 0.1, 0.1)) ||
      std::isfinite(propagateRatioError(1.0, 2.0, -0.1, 0.1))) {
    std::cerr
        << "PLOT_REFERENCE_MULTIPLICITY_TEST_ERROR "
        << "absolute ratio-error propagation contract\n";
    return 1;
  }

  TH1D pointGuard("pointGuard", "", 1, 0.0, 1.0);
  SetPlotPointOrThrow(
      &pointGuard, 1, 2.0, 0.5, true, true,
      1.0, 3.0, "valid logarithmic envelope");
  if (std::abs(pointGuard.GetBinContent(1) - 2.0) > 1e-15 ||
      std::abs(pointGuard.GetBinError(1) - 0.5) > 1e-15 ||
      !ThrowsRuntimeError([&]() {
        SetPlotPointOrThrow(
            &pointGuard, 1, 1.0, 1.0, true, true,
            0.1, 3.0, "non-positive log envelope");
      }) ||
      !ThrowsRuntimeError([&]() {
        SetPlotPointOrThrow(
            &pointGuard, 1, 0.5, 0.6, true, false,
            0.0, 2.0, "lower axis clipping");
      }) ||
      !ThrowsRuntimeError([&]() {
        SetPlotPointOrThrow(
            &pointGuard, 1, 1.5, 0.6, true, false,
            0.0, 2.0, "upper axis clipping");
      }) ||
      !ThrowsRuntimeError([&]() {
        SetPlotPointOrThrow(
            &pointGuard, 1, 1.0, 0.1, true, false,
            2.0, 1.0, "invalid axis ordering");
      })) {
    std::cerr
        << "PLOT_REFERENCE_MULTIPLICITY_TEST_ERROR "
        << "plotted uncertainty-envelope guard\n";
    return 1;
  }

  const SubsampleStatistics goodStats{10, 1.0, 0.5, 0.2};
  const SubsampleStatistics notApplicableStats{0, 0.0, 0.0, 0.0};
  const SubsampleTechnicalCoverage referenceCoverage =
      EvaluateSubsampleTechnicalCoverage(
          0.4, 0.4,
          std::numeric_limits<Double_t>::quiet_NaN(),
          goodStats, notApplicableStats, 10, true, true);
  const SubsampleTechnicalCoverage derivedCoverage =
      EvaluateSubsampleTechnicalCoverage(
          0.2, 0.4, 0.5,
          goodStats, goodStats, 10, false, true);
  const SubsampleTechnicalCoverage zeroDenominatorCoverage =
      EvaluateSubsampleTechnicalCoverage(
          0.2, 0.0,
          std::numeric_limits<Double_t>::quiet_NaN(),
          goodStats, goodStats, 10, false, true);
  const SubsampleStatistics nonDegenerateZeroSem{
      10, 1.0, 0.5, 0.0};
  const SubsampleTechnicalCoverage zeroSemCoverage =
      EvaluateSubsampleTechnicalCoverage(
          0.2, 0.4, 0.5,
          nonDegenerateZeroSem, goodStats, 10, false, true);
  if (!referenceCoverage.complete ||
      !referenceCoverage.ratioComplete ||
      !derivedCoverage.complete ||
      zeroDenominatorCoverage.ratioComplete ||
      zeroDenominatorCoverage.complete ||
      zeroSemCoverage.yieldComplete ||
      zeroSemCoverage.complete) {
    std::cerr
        << "PLOT_REFERENCE_MULTIPLICITY_TEST_ERROR "
        << "authoritative technical-coverage predicate\n";
    return 2;
  }

  const TriggerAssociateOSandSS baryon = BeautyPair(
      "Lambda_b", "Lambda_b-bar",
      "BplusLb.root", "BplusLbbar.root");
  const TriggerAssociateOSandSS reference = BeautyPair(
      "B-", "B^{+}",
      "BplusBminus.root", "BplusBplus.root");
  const TriggerAssociateOSandSS strangeMeson = BeautyPair(
      "B_s^0-bar", "B_s^0",
      "BplusBszerobar.root", "BplusBszero.root");

  const std::vector<TriggerAssociateOSandSS> shuffled = {
      baryon, strangeMeson, reference};
  const ReferenceAssociateSelection selection =
      ResolveReferenceAssociateSelection(
          shuffled, "shuffled B+ test configuration");
  if (selection.index != 2U || selection.pdg != -521) {
    std::cerr
        << "PLOT_REFERENCE_MULTIPLICITY_TEST_ERROR "
        << "reference was inferred from position rather than registry\n";
    return 2;
  }
  const std::vector<Int_t> order =
      ReferenceFirstAssociateOrder(shuffled.size(), selection.index);
  if (order != std::vector<Int_t>({2, 0, 1})) {
    std::cerr
        << "PLOT_REFERENCE_MULTIPLICITY_TEST_ERROR "
        << "reference-first processing changed configured indices\n";
    return 3;
  }
  if (!ThrowsRuntimeError([&]() {
        ResolveReferenceAssociateSelection(
            std::vector<TriggerAssociateOSandSS>{
                baryon, strangeMeson},
            "missing-reference test");
      }) ||
      !ThrowsRuntimeError([&]() {
        ResolveReferenceAssociateSelection(
            std::vector<TriggerAssociateOSandSS>{
                reference, reference},
            "duplicate-reference test");
      })) {
    std::cerr
        << "PLOT_REFERENCE_MULTIPLICITY_TEST_ERROR "
        << "absent/duplicate reference was accepted\n";
    return 4;
  }

  const TriggerAssociateOSandSS charmReference =
      ResolveConfiguredPairFromRegistry(
          "charm", "D^{+}", "D^{+}", "D-", "D^{+}",
          "DplusDminus.root", "DplusDplus.root");
  if (charmReference.triggerPdg != 411 ||
      charmReference.associateOSPdg != -411 ||
      charmReference.referenceMesonPdg != -411) {
    std::cerr
        << "PLOT_REFERENCE_MULTIPLICITY_TEST_ERROR "
        << "signed charm reference mapping is wrong\n";
    return 4;
  }

  const PairInputSelectionContract contract = TestSelectionContract();
  TMemFile canonicalOS("canonicalOS.root", "RECREATE");
  WritePairIdentity(canonicalOS, reference, true);
  ValidateConfiguredPairFileIdentity(
      &canonicalOS, PairSelectionProjectionMode::kUpstreamSelectedV2,
      contract, "canonical_complete_root_v2", reference, true,
      "beauty", "canonicalOS.root");

  TMemFile wrongReference("wrongReference.root", "RECREATE");
  WritePairIdentity(wrongReference, reference, true, 1042);
  if (!ThrowsRuntimeError([&]() {
        ValidateConfiguredPairFileIdentity(
            &wrongReference,
            PairSelectionProjectionMode::kUpstreamSelectedV2,
            contract, "canonical_complete_root_v2", reference, true,
            "beauty", "wrongReference.root");
      })) {
    std::cerr
        << "PLOT_REFERENCE_MULTIPLICITY_TEST_ERROR "
        << "wrong signed reference_meson_pdg was accepted\n";
    return 5;
  }

  TMemFile incompleteIdentity("incompleteIdentity.root", "RECREATE");
  incompleteIdentity.cd();
  TParameter<int>(
      "reference_meson_pdg", reference.referenceMesonPdg)
      .Write();
  incompleteIdentity.Flush();
  if (!ThrowsRuntimeError([&]() {
        ValidateConfiguredPairFileIdentity(
            &incompleteIdentity,
            PairSelectionProjectionMode::kUpstreamSelectedV2,
            contract, "canonical_complete_root_v2", reference, true,
            "beauty", "incompleteIdentity.root");
      })) {
    std::cerr
        << "PLOT_REFERENCE_MULTIPLICITY_TEST_ERROR "
        << "partial pair identity was accepted\n";
    return 6;
  }

  TMemFile exactLegacy("exactLegacy.root", "RECREATE");
  ValidateConfiguredPairFileIdentity(
      &exactLegacy,
      PairSelectionProjectionMode::kLegacyPlotRecutsV1,
      contract, "complete_root_21_06_2026", reference, true,
      "beauty", "exactLegacy.root");
  if (!ThrowsRuntimeError([&]() {
        ValidateConfiguredPairFileIdentity(
            &exactLegacy,
            PairSelectionProjectionMode::kLegacyPlotRecutsV1,
            contract, "unreviewed_legacy_tag", reference, true,
            "beauty", "exactLegacy.root");
      })) {
    std::cerr
        << "PLOT_REFERENCE_MULTIPLICITY_TEST_ERROR "
        << "untagged legacy identity fallback was accepted\n";
    return 7;
  }

  const TriggerAssociateOSandSS nonLegacyRegistryPair = BeautyPair(
      "Sigma_b-", "Sigma_b-bar",
      "pair_beauty_trig_Bplus_assoc_Sigmabminus.root",
      "pair_beauty_trig_Bplus_assoc_Sigmabminusbar.root");
  if (nonLegacyRegistryPair.legacyRegistryFilenames ||
      !ThrowsRuntimeError([&]() {
        ValidateConfiguredPairFileIdentity(
            &exactLegacy,
            PairSelectionProjectionMode::kLegacyPlotRecutsV1,
            contract, "complete_root_21_06_2026",
            nonLegacyRegistryPair, true,
            "beauty", "nonLegacyRegistryPair.root");
      })) {
    std::cerr
        << "PLOT_REFERENCE_MULTIPLICITY_TEST_ERROR "
        << "non-legacy registry filename used metadata-free fallback\n";
    return 8;
  }

  const Double_t edges[5] = {-0.5, 0.5, 1.5, 2.5, 3.5};
  TH1D multiplicityA("multiplicityA", "", 4, edges);
  multiplicityA.Sumw2();
  for (Int_t value = 0; value < 4; ++value) {
    for (Int_t count = 0; count <= value; ++count) {
      multiplicityA.Fill(static_cast<Double_t>(value));
    }
  }
  const MultiplicityHistogramIdentity identityA =
      CaptureMultiplicityHistogramIdentity(
          &multiplicityA, "multiplicityA");
  std::map<double, int> partitionThresholds;
  for (const double percentile :
       std::vector<double>{0.0, 50.0, 100.0}) {
    partitionThresholds[percentile] =
        HadronizationMultiplicity::ThresholdForPercentile(
            identityA, percentile, "partition test");
  }
  const std::vector<std::pair<double, double>> twoClasses = {
      {50.0, 100.0}, {0.0, 50.0}};
  HadronizationMultiplicity::RequireDiscretePartitionCoverage(
      twoClasses, partitionThresholds);
  std::map<int, int> coverageCount;
  for (const auto& interval : twoClasses) {
    const auto range =
        HadronizationMultiplicity::DiscreteClassRange(
            partitionThresholds, interval.first, interval.second);
    for (int nch = range.first; nch <= range.second; ++nch) {
      ++coverageCount[nch];
    }
  }
  for (int nch = partitionThresholds.at(100.0);
       nch <= partitionThresholds.at(0.0); ++nch) {
    if (coverageCount[nch] != 1) {
      std::cerr
          << "PLOT_REFERENCE_MULTIPLICITY_TEST_ERROR "
          << "discrete class coverage/disjointness\n";
      return 9;
    }
  }
  if (!ThrowsRuntimeError([&]() {
        HadronizationMultiplicity::RequireDiscretePartitionCoverage(
            {{60.0, 100.0}, {0.0, 50.0}},
            partitionThresholds);
      })) {
    std::cerr
        << "PLOT_REFERENCE_MULTIPLICITY_TEST_ERROR "
        << "percentile partition gap was accepted\n";
    return 9;
  }
  std::unique_ptr<TH1D> nonzeroUnderflow(
      static_cast<TH1D*>(multiplicityA.Clone("nonzeroUnderflow")));
  nonzeroUnderflow->SetBinContent(0, 1.0);
  if (!ThrowsRuntimeError([&]() {
        CaptureMultiplicityHistogramIdentity(
            nonzeroUnderflow.get(), "nonzeroUnderflow");
      })) {
    std::cerr
        << "PLOT_REFERENCE_MULTIPLICITY_TEST_ERROR "
        << "nonzero multiplicity underflow was accepted\n";
    return 9;
  }
  std::unique_ptr<TH1D> multiplicitySame(
      static_cast<TH1D*>(multiplicityA.Clone("multiplicitySame")));
  const MultiplicityHistogramIdentity identitySame =
      CaptureMultiplicityHistogramIdentity(
          multiplicitySame.get(), "multiplicitySame");
  RequireIdenticalMultiplicityHistogram(
      identityA, identitySame,
      "multiplicityA", "multiplicitySame");

  std::unique_ptr<TH1D> changedContent(
      static_cast<TH1D*>(multiplicityA.Clone("changedContent")));
  changedContent->SetBinContent(
      2, changedContent->GetBinContent(2) + 1.0);
  if (!ThrowsRuntimeError([&]() {
        RequireIdenticalMultiplicityHistogram(
            identityA,
            CaptureMultiplicityHistogramIdentity(
                changedContent.get(), "changedContent"),
            "multiplicityA", "changedContent");
      })) {
    std::cerr
        << "PLOT_REFERENCE_MULTIPLICITY_TEST_ERROR "
        << "different multiplicity contents were accepted\n";
    return 9;
  }

  std::unique_ptr<TH1D> changedSumw2(
      static_cast<TH1D*>(multiplicityA.Clone("changedSumw2")));
  changedSumw2->SetBinError(
      2, changedSumw2->GetBinError(2) + 0.25);
  if (!ThrowsRuntimeError([&]() {
        RequireIdenticalMultiplicityHistogram(
            identityA,
            CaptureMultiplicityHistogramIdentity(
                changedSumw2.get(), "changedSumw2"),
            "multiplicityA", "changedSumw2");
      })) {
    std::cerr
        << "PLOT_REFERENCE_MULTIPLICITY_TEST_ERROR "
        << "different multiplicity errors/Sumw2 were accepted\n";
    return 10;
  }

  const Double_t changedEdges[5] = {-0.5, 0.5, 1.6, 2.5, 3.5};
  TH1D changedBinning("changedBinning", "", 4, changedEdges);
  changedBinning.Sumw2();
  for (Int_t bin = 0; bin <= 5; ++bin) {
    changedBinning.SetBinContent(bin, multiplicityA.GetBinContent(bin));
    changedBinning.SetBinError(bin, multiplicityA.GetBinError(bin));
  }
  if (!ThrowsRuntimeError([&]() {
        RequireIdenticalMultiplicityHistogram(
            identityA,
            CaptureMultiplicityHistogramIdentity(
                &changedBinning, "changedBinning"),
            "multiplicityA", "changedBinning");
      })) {
    std::cerr
        << "PLOT_REFERENCE_MULTIPLICITY_TEST_ERROR "
        << "different multiplicity bin edges were accepted\n";
    return 11;
  }

  TH1D empty("emptyMultiplicity", "", 4, edges);
  if (!ThrowsRuntimeError([&]() {
        CaptureMultiplicityHistogramIdentity(&empty, "emptyMultiplicity");
      }) ||
      !ThrowsRuntimeError([&]() {
        GetMultiplicityThreshold(&empty, 50.0);
      }) ||
      !ThrowsRuntimeError([&]() {
        GetMultiplicityThreshold(&multiplicityA, -1.0);
      })) {
    std::cerr
        << "PLOT_REFERENCE_MULTIPLICITY_TEST_ERROR "
        << "empty distribution or invalid percentile used a fallback\n";
    return 12;
  }

  std::unique_ptr<TH1D> nonFinite(
      static_cast<TH1D*>(multiplicityA.Clone("nonFinite")));
  nonFinite->SetBinContent(
      1, std::numeric_limits<Double_t>::quiet_NaN());
  if (!ThrowsRuntimeError([&]() {
        CaptureMultiplicityHistogramIdentity(
            nonFinite.get(), "nonFinite");
      })) {
    std::cerr
        << "PLOT_REFERENCE_MULTIPLICITY_TEST_ERROR "
        << "non-finite multiplicity bin was accepted\n";
    return 13;
  }

  for (const Double_t percentile :
       std::vector<Double_t>{0.0, 1.0, 10.0, 50.0, 100.0}) {
    const Double_t threshold =
        GetMultiplicityThreshold(&multiplicityA, percentile);
    if (!std::isfinite(threshold)) {
      std::cerr
          << "PLOT_REFERENCE_MULTIPLICITY_TEST_ERROR "
          << "valid threshold is non-finite\n";
      return 14;
    }
  }

  TemporaryDirectory temporary{
      std::filesystem::temp_directory_path() /
      ("hadronization_plot_contract_" +
       std::to_string(gSystem->GetPid()))};
  if (!std::filesystem::create_directory(temporary.path)) {
    std::cerr
        << "PLOT_REFERENCE_MULTIPLICITY_TEST_ERROR "
        << "could not create unique temporary directory\n";
    return 15;
  }
  const std::string centralTag = "complete_root_TEST";
  const std::filesystem::path centralDirectory =
      temporary.path / (centralTag + "_MONASH");
  const std::string blockBase =
      (temporary.path / "SUBSAMPLES/combined_root_subSamples").string();
  WriteMultiplicityFile(
      centralDirectory / reference.OS, multiplicityA);
  WriteMultiplicityFile(
      centralDirectory / reference.SS, multiplicityA);
  for (Int_t block = 1; block <= 2; ++block) {
    const std::filesystem::path blockDirectory =
        std::filesystem::path(blockBase + "_MONASH") /
        ("combined_root_" + std::to_string(block));
    TH1D blockHistogram(
        ("blockMultiplicity" + std::to_string(block)).c_str(),
        "", 4, edges);
    blockHistogram.Sumw2();
    for (Int_t value = 0; value < 4; ++value) {
      for (Int_t count = 0; count < block + value; ++count) {
        blockHistogram.Fill(static_cast<Double_t>(value));
      }
    }
    WriteMultiplicityFile(
        blockDirectory / reference.OS, blockHistogram);
    WriteMultiplicityFile(
        blockDirectory / reference.SS, blockHistogram);
  }
  const std::map<
      std::string, std::vector<TriggerAssociateOSandSS>> beautyConfigs = {
      {"B^{+}", {reference}}};
  BinsFromTHnSparse integratedBin{};
  integratedBin.multiplicityMin = 0.0;
  integratedBin.multiplicityMax = 100.0;
  const auto frozen = FreezeAndValidateMultiplicityDefinitions(
      temporary.path.string(), {"MONASH"},
      centralTag, centralTag, blockBase, blockBase,
      2, true, beautyConfigs, {}, {integratedBin});
  if (frozen.at("MONASH").size() != 2U ||
      frozen.at("MONASH").count(0.0) != 1U ||
      frozen.at("MONASH").count(100.0) != 1U) {
    std::cerr
        << "PLOT_REFERENCE_MULTIPLICITY_TEST_ERROR "
        << "tune-level thresholds were not frozen\n";
    return 16;
  }

  WriteMultiplicityFile(
      centralDirectory / reference.SS, *changedContent);
  if (!ThrowsRuntimeError([&]() {
        FreezeAndValidateMultiplicityDefinitions(
            temporary.path.string(), {"MONASH"},
            centralTag, centralTag, blockBase, blockBase,
            2, false, beautyConfigs, {}, {integratedBin});
      })) {
    std::cerr
        << "PLOT_REFERENCE_MULTIPLICITY_TEST_ERROR "
        << "central OS/SS multiplicity mismatch was accepted\n";
    return 17;
  }
  WriteMultiplicityFile(
      centralDirectory / reference.SS, multiplicityA);

  const std::filesystem::path secondBlockSS =
      std::filesystem::path(blockBase + "_MONASH") /
      "combined_root_2" / reference.SS;
  WriteMultiplicityFile(secondBlockSS, *changedSumw2);
  if (!ThrowsRuntimeError([&]() {
        FreezeAndValidateMultiplicityDefinitions(
            temporary.path.string(), {"MONASH"},
            centralTag, centralTag, blockBase, blockBase,
            2, true, beautyConfigs, {}, {integratedBin});
      })) {
    std::cerr
        << "PLOT_REFERENCE_MULTIPLICITY_TEST_ERROR "
        << "within-block Sumw2 mismatch was accepted\n";
    return 18;
  }

  std::cout
      << "PLOT_REFERENCE_MULTIPLICITY_TEST_SUMMARY "
      << "reference_resolution=PASS signed_metadata=PASS "
      << "legacy_gate=PASS multiplicity_identity=PASS "
      << "pair_combinatorics=PASS "
      << "boundary_partition=PASS "
      << "tune_and_block_freeze=PASS "
      << "absolute_ratio_error=PASS "
      << "plot_envelope=PASS "
      << "technical_coverage=PASS "
      << "fallback_rejection=PASS\n";
  return 0;
}
