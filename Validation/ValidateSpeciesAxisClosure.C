// Validates the species axis against the category axis it refines.
//
// THE TWO CHECKS, both exact.
//
//   1. The closure sum rule still closes to 1 within 1e-9. The species object
//      is filled from the same loop as hFlavourClosure, so if adding it
//      perturbed the weights at all, the sum rule is where it shows.
//
//   2. hFlavourClosureSpecies, summed by category, reproduces hFlavourClosure
//      BIN FOR BIN.
//
// WHY CHECK 2 IS NOT TAUTOLOGICAL. The two labelings share their RULES --
// ClassifyHeavyStateDetailed -- but not their INPUTS. hFlavourClosure's
// category comes from the producer's runtime heavy_state_category branch,
// computed per particle as the event was analysed. The species axis's category
// comes from the ordinal table, which was derived offline from a raw file's
// heavy_stability_audit tree. Agreement therefore tests the ordinal mapping
// and the fill, which is what it exists to test; retyping the rules here
// instead would only have tested that two transcriptions agree.
//
// A MISMATCH IS A STOP, QUANTIFIED, NEVER PATCHED. This macro reports the
// worst offender with its bin coordinates so the discrepancy can be
// characterised rather than absorbed.

#include "../contracts/GeneratedSpeciesOrdinals.h"

#include "TFile.h"
#include "TH1D.h"
#include "THnSparse.h"
#include "TObjString.h"

#include <cmath>
#include <cstdio>
#include <map>
#include <memory>
#include <string>
#include <vector>

namespace {

// Relative tolerance for the summation comparison. The species object sums
// many ordinals into one category bin, so the additions happen in a different
// ORDER from the category object's single fills. That is a floating-point
// difference of order the machine epsilon times the number of terms, not a
// physics difference; 1e-12 relative is far tighter than any real defect and
// far looser than bit-identity, which would be the wrong thing to demand.
constexpr double kRelativeTolerance = 1e-12;

struct BinKey {
  int i0, i1, i2, i3, category;
  bool operator<(const BinKey& other) const {
    if (i0 != other.i0) return i0 < other.i0;
    if (i1 != other.i1) return i1 < other.i1;
    if (i2 != other.i2) return i2 < other.i2;
    if (i3 != other.i3) return i3 < other.i3;
    return category < other.category;
  }
};

struct Sums {
  double content = 0.0;
  double sumw2 = 0.0;
};

bool AxesMatch(THnSparseD& a, THnSparseD& b, int axis, std::string& why) {
  auto* axisA = a.GetAxis(axis);
  auto* axisB = b.GetAxis(axis);
  if (axisA->GetNbins() != axisB->GetNbins()) {
    why = "axis " + std::to_string(axis) + " bin count " +
          std::to_string(axisA->GetNbins()) + " vs " +
          std::to_string(axisB->GetNbins());
    return false;
  }
  for (int bin = 0; bin <= axisA->GetNbins(); ++bin) {
    const double edgeA = axisA->GetBinLowEdge(bin + 1);
    const double edgeB = axisB->GetBinLowEdge(bin + 1);
    if (std::abs(edgeA - edgeB) > 1e-12 * std::max(1.0, std::abs(edgeA))) {
      why = "axis " + std::to_string(axis) + " edge " + std::to_string(bin) +
            ": " + std::to_string(edgeA) + " vs " + std::to_string(edgeB);
      return false;
    }
  }
  return true;
}

}  // namespace

int ValidateSpeciesAxisClosure(const char* path) {
  int errors = 0;
  auto fail = [&](const std::string& message) {
    std::printf("SPECIES_AXIS_ERROR %s\n", message.c_str());
    ++errors;
  };

  std::unique_ptr<TFile> file(TFile::Open(path, "READ"));
  if (!file || file->IsZombie()) {
    std::printf("SPECIES_AXIS_ERROR cannot open %s\n", path);
    return 2;
  }

  auto* category = dynamic_cast<THnSparseD*>(file->Get("hFlavourClosure"));
  auto* species = dynamic_cast<THnSparseD*>(file->Get("hFlavourClosureSpecies"));
  if (!category || !species) {
    std::printf("SPECIES_AXIS_ERROR missing hFlavourClosure(%p) or "
                "hFlavourClosureSpecies(%p) in %s\n",
                static_cast<void*>(category), static_cast<void*>(species),
                path);
    return 3;
  }

  // The legibility objects must travel with the file: F5's condition is that a
  // reader can decode the axis without the repository.
  for (const char* name : {"species_ordinal_schema", "species_ordinal_labels",
                           "species_ordinal_digest"}) {
    if (!dynamic_cast<TObjString*>(file->Get(name))) {
      fail(std::string("missing legibility object ") + name);
    }
  }
  auto* digest = dynamic_cast<TObjString*>(file->Get("species_ordinal_digest"));
  if (digest && digest->GetString() != Hadronization::kSpeciesOrdinalDigest) {
    fail("file was filled against ordinal table digest " +
         std::string(digest->GetString().Data()) + " but this build carries " +
         std::string(Hadronization::kSpeciesOrdinalDigest) +
         "; the axes are not comparable");
  }

  // ---------------------------------------------------------------------
  // The first four axes must be identical, or "bin for bin" is meaningless.
  // ---------------------------------------------------------------------
  if (species->GetNdimensions() != 5 || category->GetNdimensions() != 5) {
    fail("both objects must be 5-dimensional");
    return errors;
  }
  for (int axis = 0; axis < 4; ++axis) {
    std::string why;
    if (!AxesMatch(*category, *species, axis, why)) {
      fail("shared axes differ: " + why);
    }
  }
  if (species->GetAxis(4)->GetNbins() != Hadronization::kSpeciesOrdinalCount) {
    fail("species axis has " +
         std::to_string(species->GetAxis(4)->GetNbins()) +
         " bins, expected " +
         std::to_string(Hadronization::kSpeciesOrdinalCount));
  }
  if (category->GetAxis(4)->GetNbins() != 6) {
    fail("category axis has " +
         std::to_string(category->GetAxis(4)->GetNbins()) +
         " bins, expected 6");
  }
  if (errors != 0) return errors;

  // ---------------------------------------------------------------------
  // CHECK 2: sum the species axis by category and compare bin for bin.
  // ---------------------------------------------------------------------
  std::map<BinKey, Sums> summed;
  std::vector<int> coordinates(5);
  long long unmapped = 0;
  for (Long64_t bin = 0; bin < species->GetNbins(); ++bin) {
    const double content = species->GetBinContent(bin, coordinates.data());
    const double sumw2 = species->GetBinError2(bin);
    // THnSparse bin indices are 1-based; ordinal 0 lives in bin 1.
    const int ordinal = coordinates[4] - 1;
    const int mapped = Hadronization::SpeciesCategoryForOrdinal(ordinal);
    if (mapped < 0) {
      ++unmapped;
      continue;
    }
    BinKey key{coordinates[0], coordinates[1], coordinates[2], coordinates[3],
               mapped + 1};
    Sums& target = summed[key];
    target.content += content;
    target.sumw2 += sumw2;
  }
  if (unmapped != 0) {
    fail(std::to_string(unmapped) +
         " filled species bins carry an ordinal outside the table; the axis "
         "and the table disagree");
  }

  long long compared = 0;
  double worstContent = 0.0;
  double worstSumw2 = 0.0;
  BinKey worstKey{0, 0, 0, 0, 0};
  for (Long64_t bin = 0; bin < category->GetNbins(); ++bin) {
    const double content = category->GetBinContent(bin, coordinates.data());
    const double sumw2 = category->GetBinError2(bin);
    BinKey key{coordinates[0], coordinates[1], coordinates[2], coordinates[3],
               coordinates[4]};
    auto found = summed.find(key);
    const double gotContent = (found == summed.end()) ? 0.0
                                                      : found->second.content;
    const double gotSumw2 = (found == summed.end()) ? 0.0
                                                    : found->second.sumw2;
    const double scale = std::max(std::abs(content), 1e-300);
    const double deviation = std::abs(gotContent - content) / scale;
    const double sumw2Scale = std::max(std::abs(sumw2), 1e-300);
    const double sumw2Deviation = std::abs(gotSumw2 - sumw2) / sumw2Scale;
    if (deviation > worstContent) {
      worstContent = deviation;
      worstKey = key;
    }
    if (sumw2Deviation > worstSumw2) worstSumw2 = sumw2Deviation;
    ++compared;
    if (found != summed.end()) summed.erase(found);
  }
  // Anything left is a bin the species axis filled and the category axis did
  // not. That direction matters as much as the other: it would mean the
  // species object saw a compensating hadron the category object missed.
  long long extra = 0;
  for (const auto& [key, sums] : summed) {
    if (std::abs(sums.content) > 0.0) {
      ++extra;
      if (extra <= 3) {
        fail("species-only bin (" + std::to_string(key.i0) + "," +
             std::to_string(key.i1) + "," + std::to_string(key.i2) + "," +
             std::to_string(key.i3) + ",cat=" + std::to_string(key.category) +
             ") content " + std::to_string(sums.content) +
             " has no counterpart in hFlavourClosure");
      }
    }
  }
  if (extra > 3) {
    fail(std::to_string(extra) + " species-only bins in total");
  }
  if (worstContent > kRelativeTolerance) {
    fail("worst content deviation " + std::to_string(worstContent) +
         " exceeds " + std::to_string(kRelativeTolerance) + " at bin (" +
         std::to_string(worstKey.i0) + "," + std::to_string(worstKey.i1) +
         "," + std::to_string(worstKey.i2) + "," +
         std::to_string(worstKey.i3) + ",cat=" +
         std::to_string(worstKey.category) + ")");
  }
  if (worstSumw2 > kRelativeTolerance) {
    fail("worst Sumw2 deviation " + std::to_string(worstSumw2) +
         " exceeds " + std::to_string(kRelativeTolerance));
  }

  // ---------------------------------------------------------------------
  // CHECK 2b: the CATEGORY MARGINAL, which actually exercises aggregation.
  //
  // Why this is here. The bin-for-bin check above is necessary but, at fixture
  // statistics, weakly exercised: the correlation space is 100 x 100 x nPt x
  // 4096, so a filled (dphi,deta,pt,Nch,category) cell almost always holds a
  // SINGLE species, and "summing" it is then a copy. That verifies the ordinal
  // -> category mapping and the fill land in the right place, but it does not
  // test many-to-one addition at all. Integrating the fine axes away forces
  // every one of the 202 ordinals into one of 6 category totals, which does.
  // ---------------------------------------------------------------------
  double speciesByCategory[6] = {0, 0, 0, 0, 0, 0};
  double categoryTotals[6] = {0, 0, 0, 0, 0, 0};
  long long ordinalsContributing[6] = {0, 0, 0, 0, 0, 0};
  for (Long64_t bin = 0; bin < species->GetNbins(); ++bin) {
    const double content = species->GetBinContent(bin, coordinates.data());
    const int mapped =
        Hadronization::SpeciesCategoryForOrdinal(coordinates[4] - 1);
    if (mapped >= 0 && mapped < 6) {
      speciesByCategory[mapped] += content;
      ++ordinalsContributing[mapped];
    }
  }
  for (Long64_t bin = 0; bin < category->GetNbins(); ++bin) {
    const double content = category->GetBinContent(bin, coordinates.data());
    const int index = coordinates[4] - 1;
    if (index >= 0 && index < 6) categoryTotals[index] += content;
  }
  double worstMarginal = 0.0;
  long long maxTermsInOneCategory = 0;
  for (int index = 0; index < 6; ++index) {
    const double scale = std::max(std::abs(categoryTotals[index]), 1e-300);
    const double deviation =
        std::abs(speciesByCategory[index] - categoryTotals[index]) / scale;
    if (deviation > worstMarginal) worstMarginal = deviation;
    if (ordinalsContributing[index] > maxTermsInOneCategory) {
      maxTermsInOneCategory = ordinalsContributing[index];
    }
  }
  // A tolerance ten times looser than the bin-for-bin one, because this sum
  // has many more terms and therefore more accumulated rounding. Still far
  // tighter than any real defect.
  if (worstMarginal > kRelativeTolerance * 10.0) {
    fail("worst category-marginal deviation " + std::to_string(worstMarginal) +
         " exceeds " + std::to_string(kRelativeTolerance * 10.0));
  }

  // ---------------------------------------------------------------------
  // CHECK 1: the closure sum rule, read back from the summary object.
  // ---------------------------------------------------------------------
  double closure = -1.0;
  auto* summary = dynamic_cast<TH1D*>(file->Get("hFlavourClosureSummary"));
  if (summary) {
    const double weightedTriggers = summary->GetBinContent(1);
    const double fullPhaseSpace = summary->GetBinContent(2);
    if (weightedTriggers > 0.0) {
      closure = fullPhaseSpace / weightedTriggers;
      if (std::abs(closure - 1.0) > 1e-9) {
        fail("closure sum rule " + std::to_string(closure) +
             " deviates from 1 by more than 1e-9");
      }
    }
  }

  std::printf(
      "SPECIES_AXIS_CLOSURE errors=%d file=%s category_bins=%lld "
      "species_bins=%lld compared=%lld species_only=%lld unmapped=%lld "
      "worst_content_deviation=%.3e worst_sumw2_deviation=%.3e "
      "worst_marginal_deviation=%.3e max_ordinals_in_one_category=%lld "
      "closure_sum_rule=%.15f\n",
      errors, path, static_cast<long long>(category->GetNbins()),
      static_cast<long long>(species->GetNbins()), compared, extra, unmapped,
      worstContent, worstSumw2, worstMarginal, maxTermsInOneCategory, closure);
  return errors;
}
