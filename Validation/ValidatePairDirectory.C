#include "../AnalysisScripts/GeneratedPairRegistry.h"
#include "../SimulationScripts/GeneratedHeavyFlavourRegistry.h"
#include "../SimulationScripts/HeavyFlavourUtils.h"

#include <TFile.h>
#include <TH1.h>
#include <THnSparse.h>
#include <TObjString.h>
#include <TParameter.h>
#include <TSystem.h>

#include <algorithm>
#include <cmath>
#include <cstring>
#include <iostream>
#include <map>
#include <set>
#include <string>
#include <vector>

namespace {

struct SparseTotals {
  double content = 0.0;
  double errorSquared = 0.0;
};

bool NearlyEqual(double first, double second,
                 double relativeTolerance = 1e-10) {
  return std::abs(first - second) <=
         relativeTolerance * std::max({1.0, std::abs(first), std::abs(second)});
}

SparseTotals ValidateSparse(THnSparse* histogram, const std::string& path,
                            int& errors) {
  bool valid = true;
  SparseTotals totals;
  std::vector<Int_t> coordinates(histogram->GetNdimensions());
  for (Long64_t bin = 0; bin < histogram->GetNbins(); ++bin) {
    const double content = histogram->GetBinContent(bin, coordinates.data());
    const double error = histogram->GetBinError(bin);
    if (!std::isfinite(content) || !std::isfinite(error)) {
      std::cerr << "PAIR_VALIDATION_ERROR non-finite sparse bin in " << path
                << "\n";
      ++errors;
      valid = false;
      break;
    }
    totals.content += content;
    totals.errorSquared += error * error;
    for (int axis = 0; axis < histogram->GetNdimensions(); ++axis) {
      if (coordinates[axis] <= 0 ||
          coordinates[axis] > histogram->GetAxis(axis)->GetNbins()) {
        std::cerr << "PAIR_VALIDATION_ERROR sparse under/overflow in " << path
                  << " axis=" << axis << "\n";
        ++errors;
        valid = false;
        break;
      }
    }
  }
  if (!valid) return {};
  return totals;
}

bool ValidateOriginClosure(THnSparse* correlation, THnSparse* byOrigin,
                           const std::string& path, int& errors) {
  using Coordinate = std::vector<Int_t>;
  std::map<Coordinate, SparseTotals> decomposed;
  std::vector<Int_t> originCoordinates(byOrigin->GetNdimensions());
  for (Long64_t bin = 0; bin < byOrigin->GetNbins(); ++bin) {
    const double content =
        byOrigin->GetBinContent(bin, originCoordinates.data());
    const double error = byOrigin->GetBinError(bin);
    Coordinate key(originCoordinates.begin(), originCoordinates.begin() + 7);
    auto& total = decomposed[key];
    total.content += content;
    total.errorSquared += error * error;
  }

  bool valid = true;
  std::set<Coordinate> seen;
  std::vector<Int_t> coordinates(correlation->GetNdimensions());
  for (Long64_t bin = 0; bin < correlation->GetNbins(); ++bin) {
    const double content =
        correlation->GetBinContent(bin, coordinates.data());
    const double error = correlation->GetBinError(bin);
    const Coordinate key(coordinates.begin(), coordinates.end());
    seen.insert(key);
    const auto found = decomposed.find(key);
    if (found == decomposed.end() ||
        !NearlyEqual(content, found->second.content) ||
        !NearlyEqual(error * error, found->second.errorSquared)) {
      std::cerr << "PAIR_VALIDATION_ERROR associate-origin closure mismatch in "
                << path << "\n";
      ++errors;
      valid = false;
      break;
    }
  }
  if (valid) {
    for (const auto& [key, total] : decomposed) {
      if (!seen.count(key) &&
          (!NearlyEqual(total.content, 0.0) ||
           !NearlyEqual(total.errorSquared, 0.0))) {
        std::cerr
            << "PAIR_VALIDATION_ERROR origin component without inclusive bin in "
            << path << "\n";
        ++errors;
        valid = false;
        break;
      }
    }
  }
  return valid;
}

}  // namespace

int ValidatePairDirectory(const char* directory, bool requireAll = true) {
  int errors = 0;
  auto fail = [&](const std::string& message) {
    std::cerr << "PAIR_VALIDATION_ERROR " << message << "\n";
    ++errors;
  };
  std::set<std::string> expected;
  for (const auto& pair : Hadronization::kPairDefinitions) {
    expected.insert(std::string(pair.filename));
  }

  std::set<std::string> found;
  void* handle = gSystem->OpenDirectory(directory);
  if (!handle) {
    fail(std::string("cannot open directory ") + directory);
    return errors;
  }
  while (const char* entry = gSystem->GetDirEntry(handle)) {
    const std::string name(entry);
    if (name.size() > 5 && name.substr(name.size() - 5) == ".root") {
      found.insert(name);
    }
  }
  gSystem->FreeDirectory(handle);
  if (requireAll && found != expected) {
    for (const auto& missing : expected) {
      if (!found.count(missing)) fail("missing expected file " + missing);
    }
    for (const auto& extra : found) {
      if (!expected.count(extra)) fail("unexpected ROOT file " + extra);
    }
  }

  std::map<int, std::pair<Long64_t, double>> triggerTotals;
  for (const auto& pair : Hadronization::kPairDefinitions) {
    const std::string path =
        std::string(directory) + "/" + std::string(pair.filename);
    if (gSystem->AccessPathName(path.c_str())) {
      if (requireAll) continue;
      continue;
    }
    TFile file(path.c_str(), "READ");
    if (file.IsZombie()) {
      fail("zombie file " + path);
      continue;
    }
    auto* multiplicity = dynamic_cast<TH1*>(file.Get("summed MULTIPLICITY"));
    auto* trigger = dynamic_cast<THnSparse*>(file.Get("hTrKinematics"));
    auto* associate = dynamic_cast<THnSparse*>(file.Get("hAsKinematics"));
    auto* correlation = dynamic_cast<THnSparse*>(file.Get("hCorrelations"));
    auto* byOrigin = dynamic_cast<THnSparse*>(
        file.Get("hCorrelationsByOrigin"));
    if (!multiplicity || !trigger || !associate || !correlation || !byOrigin) {
      fail("missing required histogram object in " + path);
      continue;
    }
    if (trigger->GetNdimensions() != 4 ||
        associate->GetNdimensions() != 4 ||
        correlation->GetNdimensions() != 7 ||
        byOrigin->GetNdimensions() != 8) {
      fail("THnSparse dimensionality mismatch in " + path);
    }
    if (multiplicity->GetBinContent(0) != 0.0 ||
        multiplicity->GetBinContent(multiplicity->GetNbinsX() + 1) != 0.0) {
      fail("multiplicity under/overflow in " + path);
    }
    const SparseTotals triggerTotalsHistogram =
        ValidateSparse(trigger, path + ":hTrKinematics", errors);
    const SparseTotals associateTotalsHistogram =
        ValidateSparse(associate, path + ":hAsKinematics", errors);
    const SparseTotals correlationTotalsHistogram =
        ValidateSparse(correlation, path + ":hCorrelations", errors);
    const SparseTotals originTotalsHistogram =
        ValidateSparse(byOrigin, path + ":hCorrelationsByOrigin", errors);
    ValidateOriginClosure(correlation, byOrigin, path, errors);

    auto* schema = dynamic_cast<TObjString*>(file.Get("analysis_schema"));
    auto* selector = dynamic_cast<TObjString*>(file.Get("selector_version"));
    auto* speciesSha =
        dynamic_cast<TObjString*>(file.Get("species_registry_sha256"));
    auto* pairSha =
        dynamic_cast<TObjString*>(file.Get("pair_registry_sha256"));
    auto* triggerPdg =
        dynamic_cast<TParameter<int>*>(file.Get("trigger_pdg"));
    auto* associatePdg =
        dynamic_cast<TParameter<int>*>(file.Get("associate_pdg"));
    auto* triggerCount =
        dynamic_cast<TParameter<Long64_t>*>(file.Get("trigger_count"));
    auto* triggerWeights =
        dynamic_cast<TParameter<double>*>(file.Get("trigger_sum_weights"));
    auto* pairCount =
        dynamic_cast<TParameter<Long64_t>*>(file.Get("pair_count"));
    auto* pairWeights =
        dynamic_cast<TParameter<double>*>(file.Get("pair_sum_weights"));
    if (!schema || schema->GetString() != "paul_pair_objects_primary_ground_v1" ||
        !selector ||
        selector->GetString() != Hadronization::kSelectorVersion ||
        !speciesSha ||
        speciesSha->GetString() != Hadronization::kSpeciesRegistrySha256 ||
        !pairSha ||
        pairSha->GetString() != Hadronization::kPairRegistrySha256 ||
        !triggerPdg || triggerPdg->GetVal() != pair.triggerPdg ||
        !associatePdg || associatePdg->GetVal() != pair.associatePdg ||
        !triggerCount || !triggerWeights || !pairCount || !pairWeights ||
        !std::isfinite(triggerWeights->GetVal()) ||
        !std::isfinite(pairWeights->GetVal())) {
      fail("metadata contract mismatch in " + path);
      continue;
    }
    if (!NearlyEqual(triggerTotalsHistogram.content,
                     triggerWeights->GetVal()) ||
        !NearlyEqual(associateTotalsHistogram.content,
                     pairWeights->GetVal()) ||
        !NearlyEqual(correlationTotalsHistogram.content,
                     pairWeights->GetVal()) ||
        !NearlyEqual(originTotalsHistogram.content, pairWeights->GetVal())) {
      fail("histogram integral/metadata mismatch in " + path);
    }
    const auto total =
        std::make_pair(triggerCount->GetVal(), triggerWeights->GetVal());
    const auto previous = triggerTotals.find(pair.triggerPdg);
    if (previous == triggerTotals.end()) {
      triggerTotals[pair.triggerPdg] = total;
    } else if (previous->second != total) {
      fail("shared trigger denominator differs across pair files for PDG " +
           std::to_string(pair.triggerPdg));
    }
  }
  std::cout << "PAIR_DIRECTORY_VALIDATION errors=" << errors
            << " expected_files=" << expected.size()
            << " found_root_files=" << found.size() << "\n";
  return errors;
}
