// Measure the systematic uncertainty from dropping kUnresolved candidates.
//
// WHY THIS EXISTS
//
// Heavy-flavour origin is never tie-broken: a hadron whose heavy quark cannot
// be traced unambiguously to the selected hard subprocess is classified
// kUnresolved and dropped. That is the right call -- a permissive tie-break
// would bias the tune comparison itself -- but dropping is only safe if the
// dropped sample looks like the kept one. It does not.
//
// Two facts, both measured rather than assumed:
//
//   1. The unresolved RATE is strongly tune-dependent. Colour reconnection
//      rearranges colour flow, so ancestry is ambiguous far more often in the
//      CR tunes than in MONASH.
//
//   2. The unresolved SAMPLE is baryon-enriched relative to the resolved one,
//      by a similar factor in every tune.
//
// Since the observable is whether a heavy baryon's balancing partner is a
// baryon, a baryon-enriched loss whose size differs by tune acts directly on
// the measurement. This macro quantifies that: it reports, per tune, the
// baryon fraction with and without the unresolved candidates, and the
// resulting relative shift. That shift is the systematic to quote.
//
// SECTOR PARAMETRISATION
//
// This macro measured CHARM only for its first two generations -- the cuts were
// hard-coded to heavyQc/heavyOriginC. The paper's beauty-baryon story therefore
// had no equivalent systematic at all, which was found while writing the limits
// section rather than while designing the run. The sector is now an argument.
//
// The default is "c", so every pre-existing invocation is unchanged and the
// charm numbers in docs/M7_UNRESOLVED_SYSTEMATIC.md remain reproducible by the
// exact command that produced them. The beauty sector uses heavyQb/heavyOriginB,
// which are the same branches the production analysis reads
// (analysis/status_analysis_THnSparse_qq.C:410-412).
//
// Usage:
//   root -l -b -q 'Validation/MeasureUnresolvedSystematic.C("raw.root","TUNE")'
//   root -l -b -q 'Validation/MeasureUnresolvedSystematic.C("raw.root","TUNE","b")'

#include <TFile.h>
#include <TTree.h>

#include <cstdio>
#include <stdexcept>
#include <string>

int MeasureUnresolvedSystematic(const char* path, const char* tag,
                                const char* sector = "c") {
  // Fail closed on an unknown sector rather than silently defaulting: a typo
  // that fell through to charm would publish charm numbers under a beauty
  // label, which is exactly the kind of silent pass this project refuses.
  const std::string sec(sector);
  if (sec != "c" && sec != "b") {
    std::fprintf(stderr, "unknown sector '%s' (expected \"c\" or \"b\")\n", sector);
    return 1;
  }
  const std::string flavourCharge = (sec == "c") ? "heavyQc" : "heavyQb";
  const std::string origin = (sec == "c") ? "heavyOriginC" : "heavyOriginB";

  TFile input(path, "READ");
  if (input.IsZombie()) {
    std::fprintf(stderr, "cannot open %s\n", path);
    return 1;
  }
  auto* tree = dynamic_cast<TTree*>(input.Get("tree"));
  if (tree == nullptr) {
    std::fprintf(stderr, "missing tree in %s\n", path);
    return 1;
  }
  // Draw returns the number of selected ARRAY ELEMENTS; GetEntries would
  // return the number of events in which any element passes, which
  // double-counts and does not sum correctly across exclusive categories.
  tree->SetEstimate(-1);
  auto count = [&](const std::string& cut) -> Long64_t {
    return static_cast<Long64_t>(tree->Draw(origin.c_str(), cut.c_str(), "goff"));
  };

  const std::string base = "heavyIsFinal && " + flavourCharge + "!=0";
  const Long64_t unresolvedBaryon =
      count(base + " && " + origin + "==0 && heavyIsBaryon");
  const Long64_t unresolvedMeson =
      count(base + " && " + origin + "==0 && heavyIsMeson");
  const Long64_t resolvedBaryon =
      count(base + " && " + origin + "!=0 && heavyIsBaryon");
  const Long64_t resolvedMeson =
      count(base + " && " + origin + "!=0 && heavyIsMeson");

  const Long64_t unresolved = unresolvedBaryon + unresolvedMeson;
  const Long64_t resolved = resolvedBaryon + resolvedMeson;
  if (resolved == 0) {
    std::fprintf(stderr, "no resolved %s candidates in %s\n",
                 sec == "c" ? "charm" : "beauty", path);
    return 1;
  }

  // What the analysis measures: baryon fraction among resolved candidates.
  const double measured = 100.0 * static_cast<double>(resolvedBaryon) /
                          static_cast<double>(resolved);
  // What it would be if the unresolved candidates could be recovered. They
  // cannot -- their origin is genuinely ambiguous -- so this is the bound on
  // what dropping them costs, not a correction to apply.
  const double inclusive =
      100.0 * static_cast<double>(resolvedBaryon + unresolvedBaryon) /
      static_cast<double>(resolved + unresolved);
  const double relativeShift =
      measured > 0.0 ? 100.0 * (inclusive - measured) / measured : 0.0;

  const double unresolvedRate =
      100.0 * static_cast<double>(unresolved) /
      static_cast<double>(resolved + unresolved);
  const double unresolvedBaryonFraction =
      unresolved > 0
          ? 100.0 * static_cast<double>(unresolvedBaryon) /
                static_cast<double>(unresolved)
          : 0.0;

  // sector= is appended, never inserted, so parsers keyed on the existing
  // tokens are unaffected and a charm line remains byte-identical up to it.
  std::printf(
      "UNRESOLVED_SYSTEMATIC tune=%s unresolved_rate_pct=%.4f "
      "unresolved_baryon_pct=%.2f resolved_baryon_pct=%.2f "
      "baryon_enrichment=%.2f measured_baryon_pct=%.4f "
      "inclusive_baryon_pct=%.4f relative_shift_pct=%.4f "
      "unresolved_n=%lld resolved_n=%lld sector=%s\n",
      tag, unresolvedRate, unresolvedBaryonFraction, measured,
      measured > 0.0 ? unresolvedBaryonFraction / measured : 0.0, measured,
      inclusive, relativeShift, unresolved, resolved, sec.c_str());
  return 0;
}
