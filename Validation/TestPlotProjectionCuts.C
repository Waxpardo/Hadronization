#include "../PlottingScripts/improvedPlotting_THnSparse.C"

#include <THnSparse.h>

#include <cmath>
#include <iostream>
#include <memory>
#include <stdexcept>

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

  std::unique_ptr<TH1D> projectedCorrelation(
      GetCorrelationHistograms(&correlation, cuts, "cutTest"));
  std::unique_ptr<TH1D> projectedTrigger(
      GetTriggerPtHistograms(&trigger, cuts, "cutTest"));
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
    std::unique_ptr<TH1D> invalid(
        GetCorrelationHistograms(&correlation, unsupported, "invalid"));
  } catch (const std::runtime_error&) {
    rejectedUnsupportedPhi = true;
  }
  if (!rejectedUnsupportedPhi) {
    std::cerr << "PLOT_PROJECTION_TEST_ERROR unsupported phi cut accepted\n";
    return 2;
  }

  if (!IsIntegratedMultiplicityBin(cuts)) {
    std::cerr << "PLOT_PROJECTION_TEST_ERROR integrated-bin detection\n";
    return 3;
  }
  BinsFromTHnSparse nonIntegrated = cuts;
  nonIntegrated.multiplicityMin = 1.0;
  nonIntegrated.multiplicityMax = 10.0;
  if (IsIntegratedMultiplicityBin(nonIntegrated)) {
    std::cerr << "PLOT_PROJECTION_TEST_ERROR nonintegrated bin accepted\n";
    return 4;
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
    return 5;
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
    return 6;
  }

  std::cout << "PLOT_PROJECTION_TEST_PASS numerator=1 denominator=1"
            << " block_sem=" << correlationWithSEM.GetBinError(1) << "\n";
  return 0;
}
