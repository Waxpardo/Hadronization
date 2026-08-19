// Calibrate NCH_PRIMARY_CHARGED_*_V1 against a published minimum-bias reference.
//
// The production counter yields <dN_ch/deta> ~ 3.8 on the hard-heavy sample.
// That is well below the ~6.9 measured in minimum-bias pp, and the deficit has
// several candidate causes that must be separated before the number can be
// quoted in a paper:
//
//   1. a defect in the counter itself;
//   2. the pT > 0.15 GeV/c threshold (ALICE quotes dN_ch/deta at pT -> 0);
//   3. the production decay policy (ParticleDecays:limitTau0, tau0Max = 0.01 mm,
//      plus programmatic disabling of every heavy-hadron decay), which removes
//      charm/beauty decay daughters that the experimental primary definition
//      counts, since open-heavy hadrons have c*tau0 < 1 cm;
//   4. the exclusion of heavy-flavour hadrons from the count;
//   5. a genuine property of the HardQCD:hardccbar + hardbbbar sample at
//      pTHatMin = 1 GeV, which is not minimum bias.
//
// This macro isolates them. It generates SoftQCD:inelastic at the production
// energy and reports the counter under a ladder of configurations, from the
// experimental convention to the exact production policy. Cause 5 is then the
// only remaining explanation for any residual difference against the hard
// sample, and is quantified separately by rerunning with HardQCD enabled.
//
// Reference: ALICE, Phys. Lett. B 753 (2016) 319, pp at 13 TeV, INEL>0,
// dN_ch/deta(|eta|<0.5) = 6.94 +- 0.10. At 13.6 TeV the expectation is ~2%
// higher, so ~7.0-7.1. The reference uses the primary definition
// (c*tau0 > 1 cm, or descended only from shorter-lived parents) and is
// extrapolated to pT = 0.
//
// Usage:
//   root -l -b -q 'Validation/CalibrateMultiplicityAgainstMinBias.C(20000)'
//   root -l -b -q 'Validation/CalibrateMultiplicityAgainstMinBias.C(20000,true)'  // hard sample

#include "../generation/producer/HeavyFlavourUtils.h"

#include "Pythia8/Pythia.h"

#include "TFile.h"
#include "TH1D.h"

#include <cmath>
#include <cstdio>
#include <string>
#include <vector>

// B4 EXTENSION, 2026-08-09 -- the per-event N_ch distribution.
//
// A2's ladder above reports <N_ch> and dN_ch/deta, which answer "does the
// generator reproduce the reference measurement". B4 asks a different question:
// where do the analysis's percentile class boundaries sit on an MB-anchored
// axis. That needs the DISTRIBUTION, not its mean, and it must be filled on
// the axis the boundaries actually live on.
//
// THE COUNTER MATTERS AND IS EASY TO GET WRONG. The class boundaries are
// defined on NCH_PRIMARY_CHARGED_ETA10_V1: final, charged, NON-heavy-flavour,
// pT > 0.15 GeV/c, |eta| < 1. That is counter index kAnalysisCounter below --
// NOT the |eta|<0.5, pT->0, heavy-inclusive convention A2 compares against the
// ALICE number. A mapping computed on the dN/deta convention would be a
// mapping on the wrong variable, and would look entirely reasonable.

namespace {

struct Counter {
  const char* label;
  double etaMax;
  double ptMin;
  bool excludeHeavy;
  long long total = 0;
};

// INEL>0: at least one charged particle in |eta| < 1, the standard trigger
// condition the reference measurement applies.
bool IsInelGtZero(Pythia8::Pythia& pythia) {
  for (int i = 0; i < pythia.event.size(); ++i) {
    const Pythia8::Particle& p = pythia.event[i];
    if (p.isFinal() && p.isCharged() && std::abs(p.eta()) < 1.0) return true;
  }
  return false;
}

// Index into the counter ladder of the analysis definition
// NCH_PRIMARY_CHARGED_ETA10_V1 (|eta|<1.0, pT>0.15, heavy EXCLUDED). Asserted
// against the ladder at runtime rather than trusted, because reordering the
// ladder is a one-line edit that would silently retarget the histogram.
constexpr std::size_t kAnalysisCounter = 3;

// Common binning for every arm and tune. Fixed here, not per-sample, because
// the whole point is to compare distributions across samples: a per-sample
// range would make the hard and MB histograms incommensurable.
constexpr int kNchBins = 400;
constexpr double kNchLow = -0.5;
constexpr double kNchHigh = 399.5;

}  // namespace

int CalibrateMultiplicityAgainstMinBias(int events = 20000,
                                        bool hardSample = false,
                                        double tau0MaxMm = 0.01,
                                        bool disableHeavyDecays = true,
                                        double pTHatMin = 1.0,
                                        const char* nchOutputPath = "",
                                        const char* tuneLabel = "",
                                        const char* cardPath = "") {
  Pythia8::Pythia pythia;
  pythia.readString("Beams:idA = 2212");
  pythia.readString("Beams:idB = 2212");
  pythia.readString("Beams:eCM = 13600.");

  // B4: the mapping must be measured under the TUNE'S OWN settings, not
  // Monash's. Without a card this macro is Tune:pp = 14 for every arm, so a
  // "per tune" scan would silently produce three identical MONASH samples --
  // and the tune label alone would make the output look correct.
  //
  // Card first, macro overrides after: the card carries the tune bundle
  // (StringZ/StringFlav/ColourReconnection/ClosePacking/pT0Ref) plus a
  // pTHatMin and Main:numberOfEvents this macro must not inherit.
  const bool haveCard = std::string(cardPath).size() > 0;
  if (haveCard) {
    if (!pythia.readFile(cardPath)) {
      std::printf("ERROR: cannot read tune card %s\n", cardPath);
      return 6;
    }
    std::printf("B4_TUNE_CARD=%s label=%s\n", cardPath, tuneLabel);
  } else {
    pythia.readString("Tune:pp = 14");
    std::printf("B4_TUNE_CARD=<none, Tune:pp=14> label=%s\n", tuneLabel);
  }

  if (hardSample) {
    pythia.readString("HardQCD:hardccbar = on");
    pythia.readString("HardQCD:hardbbbar = on");
    pythia.readString("PhaseSpace:pTHatMin = " + std::to_string(pTHatMin));
  } else {
    // A card leaves HardQCD on; minimum bias must switch it off explicitly or
    // the "MB" arm is still a hard sample wearing an MB label.
    pythia.readString("HardQCD:hardccbar = off");
    pythia.readString("HardQCD:hardbbbar = off");
    pythia.readString("SoftQCD:inelastic = on");
  }
  pythia.readString("ParticleDecays:limitTau0 = on");
  pythia.readString("ParticleDecays:tau0Max = " + std::to_string(tau0MaxMm));
  pythia.readString("Random:setSeed = on");
  pythia.readString("Random:seed = 20260730");
  pythia.readString("Print:quiet = on");

  int heavyDisabled = 0;
  if (disableHeavyDecays) {
    for (auto it = pythia.particleData.begin(); it != pythia.particleData.end();
         ++it) {
      const auto& e = it->second;
      if (!e->isHadron()) continue;
      if (e->nQuarksInCode(4) == 0 && e->nQuarksInCode(5) == 0) continue;
      pythia.particleData.mayDecay(it->first, false);
      ++heavyDisabled;
    }
  }

  if (!pythia.init()) {
    std::printf("ERROR: PYTHIA init failed\n");
    return 3;
  }

  // Ladder: experimental convention -> exact production policy.
  std::vector<Counter> counters = {
      {"|eta|<0.5, pT>0     , heavy incl.", 0.5, 0.0, false},
      {"|eta|<0.5, pT>0.15  , heavy incl.", 0.5, 0.15, false},
      {"|eta|<0.5, pT>0.15  , heavy EXCL.", 0.5, 0.15, true},
      {"|eta|<1.0, pT>0.15  , heavy EXCL.", 1.0, 0.15, true},
      {"|eta|<4.0, pT>0.15  , heavy EXCL.", 4.0, 0.15, true},
  };

  // B4: fail closed if the ladder is reordered under us. The histogram must be
  // filled on NCH_PRIMARY_CHARGED_ETA10_V1 and nothing else.
  const Counter& analysis = counters[kAnalysisCounter];
  if (analysis.etaMax != 1.0 || analysis.ptMin != 0.15 || !analysis.excludeHeavy) {
    std::printf(
        "ERROR: counter[%zu] is not NCH_PRIMARY_CHARGED_ETA10_V1 "
        "(got etaMax=%.2f ptMin=%.2f excludeHeavy=%d). The ladder was "
        "reordered; fix kAnalysisCounter before trusting any mapping.\n",
        kAnalysisCounter, analysis.etaMax, analysis.ptMin,
        analysis.excludeHeavy ? 1 : 0);
    return 4;
  }

  const bool writeNch = std::string(nchOutputPath).size() > 0;
  const std::string histName =
      std::string("hNch_") + (hardSample ? "hard" : "mb") +
      (std::string(tuneLabel).empty() ? "" : std::string("_") + tuneLabel);
  TH1D nch(histName.c_str(),
           "NCH_PRIMARY_CHARGED_ETA10_V1;N_{ch};events",
           kNchBins, kNchLow, kNchHigh);
  nch.SetDirectory(nullptr);
  nch.Sumw2();

  long long accepted = 0;
  int generated = 0;
  while (generated < events) {
    if (!pythia.next()) continue;
    ++generated;
    if (!IsInelGtZero(pythia)) continue;
    ++accepted;
    long long analysisNch = 0;  // B4: per-EVENT, on the analysis counter only
    for (int i = 0; i < pythia.event.size(); ++i) {
      const Pythia8::Particle& p = pythia.event[i];
      if (!p.isFinal() || !p.isCharged()) continue;
      const bool heavy = pythia.particleData.nQuarksInCode(p.id(), 4) != 0 ||
                         pythia.particleData.nQuarksInCode(p.id(), 5) != 0;
      for (std::size_t ci = 0; ci < counters.size(); ++ci) {
        Counter& c = counters[ci];
        if (c.excludeHeavy && heavy) continue;
        if (p.pT() > c.ptMin && std::abs(p.eta()) <= c.etaMax) {
          ++c.total;
          if (ci == kAnalysisCounter) ++analysisNch;
        }
      }
    }
    nch.Fill(static_cast<double>(analysisNch));
  }

  if (writeNch) {
    // Overflow is a silent truncation of the high tail, which is exactly the
    // region the top percentile class lives in. Report it rather than let a
    // mapping be computed on a clipped distribution.
    const double overflow = nch.GetBinContent(nch.GetNbinsX() + 1);
    if (overflow > 0.0) {
      std::printf(
          "WARNING: %.0f events above N_ch = %.0f went to overflow; the top "
          "class boundary would be computed on a truncated tail.\n",
          overflow, kNchHigh);
    }
    TFile out(nchOutputPath, "RECREATE");
    if (out.IsZombie()) {
      std::printf("ERROR: cannot write %s\n", nchOutputPath);
      return 5;
    }
    nch.Write();
    out.Close();
    std::printf(
        "NCH_DISTRIBUTION_WRITTEN file=%s hist=%s entries=%.0f mean=%.4f "
        "overflow=%.0f sample=%s tune=%s\n",
        nchOutputPath, histName.c_str(), nch.GetEntries(), nch.GetMean(),
        overflow, hardSample ? "hard" : "mb", tuneLabel);
  }

  std::printf("\n===== N_ch CALIBRATION =====\n");
  std::printf("sample            : %s\n",
              hardSample ? "HardQCD ccbar+bbbar" : "SoftQCD:inelastic (MB)");
  if (hardSample) std::printf("pTHatMin          : %.2f GeV\n", pTHatMin);
  std::printf("sqrt(s)           : 13.6 TeV\n");
  std::printf("tau0Max           : %.4g mm\n", tau0MaxMm);
  std::printf("heavy decays      : %s (%d entries)\n",
              disableHeavyDecays ? "DISABLED" : "enabled", heavyDisabled);
  std::printf("events generated  : %d, INEL>0 accepted: %lld\n", generated,
              accepted);
  std::printf("\n%-38s %10s %12s\n", "counter", "<N_ch>", "dN_ch/deta");
  for (const auto& c : counters) {
    const double mean =
        accepted > 0 ? static_cast<double>(c.total) / accepted : 0.0;
    std::printf("%-38s %10.3f %12.3f\n", c.label, mean,
                mean / (2.0 * c.etaMax));
  }
  std::printf("\nreference (ALICE 13 TeV, INEL>0, |eta|<0.5, pT->0): 6.94 +- 0.10\n");
  std::printf("expectation at 13.6 TeV                          : ~7.0-7.1\n");

  // Verdict on the top row, which is the like-for-like comparison.
  const double dndeta = accepted > 0 ? counters[0].total /
                                           (2.0 * counters[0].etaMax * accepted)
                                     : 0.0;
  int status = 0;
  if (!hardSample) {
    if (dndeta > 6.0 && dndeta < 8.0) {
      std::printf("\nVERDICT: counter reproduces the minimum-bias reference. "
                  "The low value on the hard sample is NOT a counter defect.\n");
    } else {
      // Fail closed: Gate A uses this return value, so a drifting or broken
      // counter must block the gate rather than print a warning.
      std::printf("\nVERDICT: counter does NOT reproduce the minimum-bias "
                  "reference (got %.2f). Investigate before production.\n",
                  dndeta);
      status = 1;
    }
  }
  std::printf("============================\n\n");
  return status;
}
