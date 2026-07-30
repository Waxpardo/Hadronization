#include "../AnalysisScripts/GeneratedPairRegistry.h"
#include "../AnalysisScripts/AssociateOriginCategoryContract.h"

#include "TFile.h"
#include "TH1.h"
#include "THnSparse.h"
#include "TObjString.h"
#include "TParameter.h"

#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <memory>
#include <sstream>
#include <string>
#include <utility>
#include <vector>

namespace {

using Coordinate = std::vector<Int_t>;
using BinTotal = std::pair<double, double>;

bool NearlyEqual(double first, double second,
                 double relativeTolerance = 2e-10) {
  return std::abs(first - second) <=
         relativeTolerance *
             std::max({1.0, std::abs(first), std::abs(second)});
}

template <typename T>
T Parameter(TFile& file, const char* name, bool& ok) {
  auto* value = dynamic_cast<TParameter<T>*>(file.Get(name));
  if (!value) {
    ok = false;
    return T{};
  }
  return value->GetVal();
}

std::string ObjectString(TFile& file, const char* name, bool& ok) {
  auto* value = dynamic_cast<TObjString*>(file.Get(name));
  if (!value) {
    ok = false;
    return {};
  }
  return value->GetString().Data();
}

std::map<Coordinate, BinTotal> SparseBins(THnSparse* histogram, bool& ok) {
  std::map<Coordinate, BinTotal> values;
  if (!histogram) {
    ok = false;
    return values;
  }
  std::vector<Int_t> coordinate(histogram->GetNdimensions());
  for (Long64_t bin = 0; bin < histogram->GetNbins(); ++bin) {
    const double content =
        histogram->GetBinContent(bin, coordinate.data());
    const double errorSquared = histogram->GetBinError2(bin);
    if (!std::isfinite(content) || !std::isfinite(errorSquared) ||
        errorSquared < 0.0) {
      ok = false;
      return {};
    }
    values[coordinate] = {content, errorSquared};
  }
  return values;
}

bool SparseEqualsBlockSum(
    THnSparse* central, const std::vector<THnSparse*>& blocks) {
  bool ok = true;
  std::map<Coordinate, BinTotal> expected = SparseBins(central, ok);
  if (!ok) return false;
  std::map<Coordinate, BinTotal> observed;
  for (THnSparse* block : blocks) {
    const auto values = SparseBins(block, ok);
    if (!ok) return false;
    for (const auto& [coordinate, total] : values) {
      observed[coordinate].first += total.first;
      observed[coordinate].second += total.second;
    }
  }
  for (const auto& [coordinate, total] : expected) {
    if (!NearlyEqual(total.first, observed[coordinate].first) ||
        !NearlyEqual(total.second, observed[coordinate].second)) {
      return false;
    }
  }
  for (const auto& [coordinate, total] : observed) {
    if (!expected.count(coordinate) &&
        (!NearlyEqual(total.first, 0.0) ||
         !NearlyEqual(total.second, 0.0))) {
      return false;
    }
  }
  return true;
}

double HistogramErrorSquared(TH1* histogram, int bin) {
  if (histogram->GetSumw2N() > 0) {
    return histogram->GetSumw2()->At(bin);
  }
  const double error = histogram->GetBinError(bin);
  return error * error;
}

bool HistogramEqualsBlockSum(TH1* central,
                             const std::vector<TH1*>& blocks) {
  if (!central) return false;
  for (TH1* block : blocks) {
    if (!block || block->GetNbinsX() != central->GetNbinsX()) return false;
  }
  for (int bin = 0; bin <= central->GetNbinsX() + 1; ++bin) {
    double content = 0.0;
    double errorSquared = 0.0;
    for (TH1* block : blocks) {
      content += block->GetBinContent(bin);
      errorSquared += HistogramErrorSquared(block, bin);
    }
    if (!NearlyEqual(central->GetBinContent(bin), content) ||
        !NearlyEqual(HistogramErrorSquared(central, bin),
                     errorSquared)) {
      return false;
    }
  }
  return true;
}

struct Estimate {
  bool valid = false;
  double central = std::numeric_limits<double>::quiet_NaN();
  double mean = std::numeric_limits<double>::quiet_NaN();
  double sem = std::numeric_limits<double>::quiet_NaN();
};

Estimate Summarize(double central, const std::vector<double>& values) {
  Estimate result;
  result.central = central;
  if (!std::isfinite(central) || values.size() != 10 ||
      !std::all_of(values.begin(), values.end(),
                   [](double value) { return std::isfinite(value); })) {
    return result;
  }
  double mean = 0.0;
  for (double value : values) mean += value;
  mean /= values.size();
  double squared = 0.0;
  for (double value : values) {
    const double delta = value - mean;
    squared += delta * delta;
  }
  const double sem =
      std::sqrt(squared / (values.size() * (values.size() - 1.0)));
  if (!std::isfinite(sem) || sem < 0.0) return result;
  result.valid = true;
  result.mean = mean;
  result.sem = sem;
  return result;
}

std::string CentralDirectory(const std::string& root,
                             const std::string& tune) {
  return root + "/complete_root_GATE_D_" + tune;
}

std::string BlockDirectory(const std::string& root,
                           const std::string& tune, int block) {
  std::ostringstream path;
  path << root << "/SUBSAMPLES/combined_root_subSamples_" << tune
       << "/combined_root_" << block;
  return path.str();
}

struct PairValues {
  Long64_t centralTriggerCount = 0;
  double centralTrigger = 0.0;
  double centralPair = 0.0;
  std::vector<Long64_t> blockTriggerCount;
  std::vector<double> blockTrigger;
  std::vector<double> blockPair;
};

}  // namespace

int ValidateGateDPilotAnalysis(const char* analysisRoot) {
  const std::vector<std::string> tunes = {
      "MONASH", "JUNCTIONS", "CLOSEPACKING"};
  int errors = 0;
  int centralPairFiles = 0;
  int blockPairFiles = 0;
  int objectClosureChecks = 0;
  int triggerNormalizationComparisons = 0;
  int finiteYieldRows = 0;
  int finiteBalancingRows = 0;
  int finiteBaryonRatioRows = 0;
  int finiteTuneRatioRows = 0;
  int finiteBaryonTuneDoubleRatioRows = 0;
  int yieldRows = 0;
  int balancingRows = 0;
  int baryonRatioRows = 0;
  int tuneRatioRows = 0;
  int baryonTuneDoubleRatioRows = 0;
  int zeroYieldSemRows = 0;
  int nonfiniteYieldRows = 0;
  int zeroBalancingSemRows = 0;
  int nonfiniteBalancingRows = 0;
  int zeroBaryonRatioSemRows = 0;
  int nonfiniteBaryonRatioRows = 0;
  int zeroBaryonRatioDenominators = 0;
  int zeroTuneRatioErrorRows = 0;
  int nonfiniteTuneRatioRows = 0;
  int zeroBaryonTuneDoubleRatioErrorRows = 0;
  int nonfiniteBaryonTuneDoubleRatioRows = 0;
  bool bzeroSigmaFound = false;
  std::map<std::string,
           std::map<std::pair<int, int>, PairValues>> allValues;
  std::map<std::string,
           std::map<std::pair<int, int>, Estimate>> balancingEstimates;
  std::map<std::string,
           std::map<std::pair<int, int>, Estimate>> baryonRatioEstimates;

  auto fail = [&](const std::string& message) {
    std::cerr << "GATE_D_ANALYSIS_ERROR " << message << "\n";
    ++errors;
  };

  for (const auto& definition : Hadronization::kPairDefinitions) {
    if (definition.triggerPdg == 511 &&
        definition.associatePdg == 5212 &&
        definition.heavySign == "OS" &&
        definition.filename == "BzeroSigmabzero.root") {
      bzeroSigmaFound = true;
    }
  }
  if (!bzeroSigmaFound) {
    fail("corrected B0/Sigma_b0 pair-registry identity is absent");
  }

  for (const std::string& tune : tunes) {
    for (const auto& definition : Hadronization::kPairDefinitions) {
      const std::string filename(definition.filename);
      const std::string centralPath =
          CentralDirectory(analysisRoot, tune) + "/" + filename;
      std::unique_ptr<TFile> central(TFile::Open(centralPath.c_str(), "READ"));
      if (!central || central->IsZombie()) {
        fail("missing central pair file " + centralPath);
        continue;
      }
      ++centralPairFiles;
      bool metadataOk = true;
      const std::string centralFilter =
          ObjectString(*central, "event_filter_schema", metadataOk);
      const std::string centralOriginCategorySchema =
          ObjectString(*central, "associate_origin_category_schema",
                       metadataOk);
      const std::string centralOriginCategoryLabels =
          ObjectString(*central, "associate_origin_category_labels",
                       metadataOk);
      const int centralModulo =
          Parameter<int>(*central, "event_filter_modulo", metadataOk);
      const int centralRemainder =
          Parameter<int>(*central, "event_filter_remainder", metadataOk);
      const Long64_t centralEvents =
          Parameter<Long64_t>(*central, "input_events", metadataOk);
      const Long64_t sourceEvents =
          Parameter<Long64_t>(*central, "source_input_events", metadataOk);
      const double centralWeights =
          Parameter<double>(*central, "input_sum_weights", metadataOk);
      const Long64_t closureFailures =
          Parameter<Long64_t>(
              *central, "primary_all_heavy_closure_failures", metadataOk);
      PairValues values;
      values.centralTriggerCount =
          Parameter<Long64_t>(*central, "trigger_count", metadataOk);
      values.centralTrigger =
          Parameter<double>(*central, "trigger_sum_weights", metadataOk);
      values.centralPair =
          Parameter<double>(*central, "pair_sum_weights", metadataOk);
      if (!metadataOk || centralFilter != "all_events_v1" ||
          centralOriginCategorySchema !=
              Hadronization::kAssociateOriginCategorySchema ||
          centralOriginCategoryLabels !=
              Hadronization::kAssociateOriginCategoryLabels ||
          centralModulo != 0 || centralRemainder != -1 ||
          centralEvents != 1000000 || sourceEvents != 1000000 ||
          closureFailures != 0 || values.centralTriggerCount < 0 ||
          !std::isfinite(centralWeights)) {
        fail("central metadata/filter contract mismatch in " + centralPath);
        continue;
      }

      std::vector<std::unique_ptr<TFile>> blockFiles;
      std::vector<TH1*> multiplicities;
      std::vector<THnSparse*> triggers;
      std::vector<THnSparse*> associates;
      std::vector<THnSparse*> correlations;
      std::vector<THnSparse*> origins;
      Long64_t blockEventSum = 0;
      double blockWeightSum = 0.0;
      bool blockContractOk = true;
      for (int block = 1; block <= 10; ++block) {
        const std::string blockPath =
            BlockDirectory(analysisRoot, tune, block) + "/" + filename;
        std::unique_ptr<TFile> file(TFile::Open(blockPath.c_str(), "READ"));
        if (!file || file->IsZombie()) {
          fail("missing block pair file " + blockPath);
          blockContractOk = false;
          break;
        }
        ++blockPairFiles;
        bool ok = true;
        const std::string filter =
            ObjectString(*file, "event_filter_schema", ok);
        const std::string originCategorySchema =
            ObjectString(*file, "associate_origin_category_schema", ok);
        const std::string originCategoryLabels =
            ObjectString(*file, "associate_origin_category_labels", ok);
        const int modulo =
            Parameter<int>(*file, "event_filter_modulo", ok);
        const int remainder =
            Parameter<int>(*file, "event_filter_remainder", ok);
        const Long64_t events =
            Parameter<Long64_t>(*file, "input_events", ok);
        const Long64_t source =
            Parameter<Long64_t>(*file, "source_input_events", ok);
        const Long64_t failures = Parameter<Long64_t>(
            *file, "primary_all_heavy_closure_failures", ok);
        const double weight =
            Parameter<double>(*file, "input_sum_weights", ok);
        const Long64_t triggerCount =
            Parameter<Long64_t>(*file, "trigger_count", ok);
        const double triggerWeight =
            Parameter<double>(*file, "trigger_sum_weights", ok);
        const double pairWeight =
            Parameter<double>(*file, "pair_sum_weights", ok);
        if (!ok || filter != "unsigned_event_id_modulo_v1" ||
            originCategorySchema != centralOriginCategorySchema ||
            originCategoryLabels != centralOriginCategoryLabels ||
            modulo != 10 || remainder != block - 1 || events <= 0 ||
            source != 1000000 || failures != 0 ||
            triggerCount < 0 ||
            !std::isfinite(weight) || !std::isfinite(triggerWeight) ||
            !std::isfinite(pairWeight)) {
          fail("block metadata/filter contract mismatch in " + blockPath);
          blockContractOk = false;
          break;
        }
        blockEventSum += events;
        blockWeightSum += weight;
        values.blockTriggerCount.push_back(triggerCount);
        values.blockTrigger.push_back(triggerWeight);
        values.blockPair.push_back(pairWeight);
        multiplicities.push_back(
            dynamic_cast<TH1*>(file->Get("summed MULTIPLICITY")));
        triggers.push_back(
            dynamic_cast<THnSparse*>(file->Get("hTrKinematics")));
        associates.push_back(
            dynamic_cast<THnSparse*>(file->Get("hAsKinematics")));
        correlations.push_back(
            dynamic_cast<THnSparse*>(file->Get("hCorrelations")));
        origins.push_back(
            dynamic_cast<THnSparse*>(file->Get("hCorrelationsByOrigin")));
        blockFiles.push_back(std::move(file));
      }
      if (!blockContractOk) continue;
      if (blockEventSum != centralEvents ||
          !NearlyEqual(blockWeightSum, centralWeights)) {
        fail("ten-block event/weight union differs from central in " +
             centralPath);
      }
      const bool multiplicityClosure = HistogramEqualsBlockSum(
          dynamic_cast<TH1*>(central->Get("summed MULTIPLICITY")),
          multiplicities);
      const bool triggerClosure = SparseEqualsBlockSum(
          dynamic_cast<THnSparse*>(central->Get("hTrKinematics")),
          triggers);
      const bool associateClosure = SparseEqualsBlockSum(
          dynamic_cast<THnSparse*>(central->Get("hAsKinematics")),
          associates);
      const bool correlationClosure = SparseEqualsBlockSum(
          dynamic_cast<THnSparse*>(central->Get("hCorrelations")),
          correlations);
      const bool originClosure = SparseEqualsBlockSum(
          dynamic_cast<THnSparse*>(
              central->Get("hCorrelationsByOrigin")),
          origins);
      objectClosureChecks += 5;
      if (!multiplicityClosure || !triggerClosure || !associateClosure ||
          !correlationClosure || !originClosure) {
        fail("central histograms differ from ten-block union in " +
             centralPath);
      }

      std::vector<double> yields;
      for (std::size_t block = 0; block < values.blockPair.size(); ++block) {
        const double denominator = values.blockTrigger[block];
        yields.push_back(
            denominator > 0.0
                ? values.blockPair[block] / denominator
                : std::numeric_limits<double>::quiet_NaN());
      }
      const Estimate yield = Summarize(
          values.centralTrigger > 0.0
              ? values.centralPair / values.centralTrigger
              : std::numeric_limits<double>::quiet_NaN(),
          yields);
      ++yieldRows;
      if (yield.valid) {
        ++finiteYieldRows;
        if (yield.sem == 0.0) ++zeroYieldSemRows;
      } else {
        ++nonfiniteYieldRows;
      }
      std::cout << std::setprecision(17)
                << "GATE_D_YIELD tune=" << tune
                << " trigger=" << definition.triggerPdg
                << " associate=" << definition.associatePdg
                << " sign=" << definition.heavySign
                << " finite_blocks="
                << std::count_if(yields.begin(), yields.end(),
                                 [](double value) {
                                   return std::isfinite(value);
                                 })
                << " central=" << yield.central
                << " sem=" << yield.sem << "\n";
      allValues[tune][{definition.triggerPdg,
                       definition.associatePdg}] = values;
    }

    for (const auto& definition : Hadronization::kPairDefinitions) {
      if (definition.heavySign != "OS") continue;
      const auto osKey =
          std::make_pair(definition.triggerPdg, definition.associatePdg);
      const auto ssKey =
          std::make_pair(definition.triggerPdg, -definition.associatePdg);
      const auto os = allValues[tune].find(osKey);
      const auto ss = allValues[tune].find(ssKey);
      if (os == allValues[tune].end() || ss == allValues[tune].end()) {
        fail("OS/SS registry counterpart is absent");
        continue;
      }
      const PairValues& osValues = os->second;
      const PairValues& ssValues = ss->second;
      ++triggerNormalizationComparisons;
      if (osValues.centralTriggerCount != ssValues.centralTriggerCount ||
          !NearlyEqual(osValues.centralTrigger, ssValues.centralTrigger)) {
        fail("OS/SS central trigger normalizations differ");
        continue;
      }
      std::vector<double> blocks;
      for (int block = 0; block < 10; ++block) {
        ++triggerNormalizationComparisons;
        if (osValues.blockTriggerCount[block] !=
                ssValues.blockTriggerCount[block] ||
            !NearlyEqual(osValues.blockTrigger[block],
                         ssValues.blockTrigger[block])) {
          fail("OS/SS block trigger normalizations differ");
          blocks.push_back(
              std::numeric_limits<double>::quiet_NaN());
          continue;
        }
        const double denominator = osValues.blockTrigger[block];
        blocks.push_back(
            denominator > 0.0
                ? (osValues.blockPair[block] -
                   ssValues.blockPair[block]) /
                      denominator
                : std::numeric_limits<double>::quiet_NaN());
      }
      const Estimate balancing = Summarize(
          osValues.centralTrigger > 0.0
              ? (osValues.centralPair - ssValues.centralPair) /
                    osValues.centralTrigger
              : std::numeric_limits<double>::quiet_NaN(),
          blocks);
      balancingEstimates[tune][osKey] = balancing;
      ++balancingRows;
      if (balancing.valid) {
        ++finiteBalancingRows;
        if (balancing.sem == 0.0) ++zeroBalancingSemRows;
      } else {
        ++nonfiniteBalancingRows;
      }
      std::cout << std::setprecision(17)
                << "GATE_D_BALANCING tune=" << tune
                << " trigger=" << definition.triggerPdg
                << " associate_os=" << definition.associatePdg
                << " finite_blocks="
                << std::count_if(blocks.begin(), blocks.end(),
                                 [](double value) {
                                   return std::isfinite(value);
                                 })
                << " central=" << balancing.central
                << " sem=" << balancing.sem << "\n";

      if (definition.associateKind != "baryon") continue;
      const auto referenceOsKey = std::make_pair(
          definition.triggerPdg, definition.referenceMesonPdg);
      const auto referenceSsKey = std::make_pair(
          definition.triggerPdg, -definition.referenceMesonPdg);
      const auto referenceOs = allValues[tune].find(referenceOsKey);
      const auto referenceSs = allValues[tune].find(referenceSsKey);
      if (referenceOs == allValues[tune].end() ||
          referenceSs == allValues[tune].end()) {
        fail("baryon/reference-meson registry counterpart is absent");
        continue;
      }
      std::vector<double> ratios;
      bool zeroBlockDenominator = false;
      for (int block = 0; block < 10; ++block) {
        const double numerator =
            osValues.blockPair[block] - ssValues.blockPair[block];
        const double denominator =
            referenceOs->second.blockPair[block] -
            referenceSs->second.blockPair[block];
        if (denominator == 0.0) zeroBlockDenominator = true;
        ratios.push_back(
            denominator != 0.0
                ? numerator / denominator
                : std::numeric_limits<double>::quiet_NaN());
      }
      const double centralDenominator =
          referenceOs->second.centralPair -
          referenceSs->second.centralPair;
      if (centralDenominator == 0.0 || zeroBlockDenominator) {
        ++zeroBaryonRatioDenominators;
      }
      const Estimate ratio = Summarize(
          centralDenominator != 0.0
              ? (osValues.centralPair - ssValues.centralPair) /
                    centralDenominator
              : std::numeric_limits<double>::quiet_NaN(),
          ratios);
      baryonRatioEstimates[tune][osKey] = ratio;
      ++baryonRatioRows;
      if (ratio.valid) {
        ++finiteBaryonRatioRows;
        if (ratio.sem == 0.0) ++zeroBaryonRatioSemRows;
      } else {
        ++nonfiniteBaryonRatioRows;
      }
      std::cout << std::setprecision(17)
                << "GATE_D_BARYON_RATIO tune=" << tune
                << " trigger=" << definition.triggerPdg
                << " baryon_os=" << definition.associatePdg
                << " reference_os=" << definition.referenceMesonPdg
                << " finite_blocks="
                << std::count_if(ratios.begin(), ratios.end(),
                                 [](double value) {
                                   return std::isfinite(value);
                                 })
                << " central=" << ratio.central
                << " sem=" << ratio.sem << "\n";
    }
  }

  for (const std::string& numerator :
       {"JUNCTIONS", "CLOSEPACKING"}) {
    for (const auto& [key, numeratorEstimate] :
         balancingEstimates[numerator]) {
      const auto denominator =
          balancingEstimates["MONASH"].find(key);
      if (denominator == balancingEstimates["MONASH"].end()) continue;
      const Estimate& denominatorEstimate = denominator->second;
      bool valid =
          numeratorEstimate.valid && denominatorEstimate.valid &&
          numeratorEstimate.central != 0.0 &&
          denominatorEstimate.central != 0.0;
      double ratio = std::numeric_limits<double>::quiet_NaN();
      double error = std::numeric_limits<double>::quiet_NaN();
      if (valid) {
        ratio =
            numeratorEstimate.central / denominatorEstimate.central;
        error = std::abs(ratio) *
                std::sqrt(
                    std::pow(numeratorEstimate.sem /
                                 numeratorEstimate.central,
                             2) +
                    std::pow(denominatorEstimate.sem /
                                 denominatorEstimate.central,
                             2));
        valid = std::isfinite(ratio) && std::isfinite(error) &&
                error >= 0.0;
      }
      if (valid) ++finiteTuneRatioRows;
      ++tuneRatioRows;
      if (valid) {
        if (error == 0.0) ++zeroTuneRatioErrorRows;
      } else {
        ++nonfiniteTuneRatioRows;
      }
      std::cout << std::setprecision(17)
                << "GATE_D_INDEPENDENT_TUNE_RATIO numerator="
                << numerator << " denominator=MONASH"
                << " trigger=" << key.first
                << " associate_os=" << key.second
                << " central=" << ratio
                << " error=" << error
                << " propagation=independent_quadrature\n";
    }
  }

  for (const std::string& numerator :
       {"JUNCTIONS", "CLOSEPACKING"}) {
    for (const auto& [key, numeratorEstimate] :
         baryonRatioEstimates[numerator]) {
      const auto denominator =
          baryonRatioEstimates["MONASH"].find(key);
      if (denominator == baryonRatioEstimates["MONASH"].end()) continue;
      const Estimate& denominatorEstimate = denominator->second;
      bool valid =
          numeratorEstimate.valid && denominatorEstimate.valid &&
          numeratorEstimate.central != 0.0 &&
          denominatorEstimate.central != 0.0;
      double ratio = std::numeric_limits<double>::quiet_NaN();
      double error = std::numeric_limits<double>::quiet_NaN();
      if (valid) {
        ratio =
            numeratorEstimate.central / denominatorEstimate.central;
        error = std::abs(ratio) *
                std::sqrt(
                    std::pow(numeratorEstimate.sem /
                                 numeratorEstimate.central,
                             2) +
                    std::pow(denominatorEstimate.sem /
                                 denominatorEstimate.central,
                             2));
        valid = std::isfinite(ratio) && std::isfinite(error) &&
                error >= 0.0;
      }
      if (valid) ++finiteBaryonTuneDoubleRatioRows;
      ++baryonTuneDoubleRatioRows;
      if (valid) {
        if (error == 0.0) ++zeroBaryonTuneDoubleRatioErrorRows;
      } else {
        ++nonfiniteBaryonTuneDoubleRatioRows;
      }
      std::cout << std::setprecision(17)
                << "GATE_D_INDEPENDENT_BARYON_TUNE_DOUBLE_RATIO numerator="
                << numerator << " denominator=MONASH"
                << " trigger=" << key.first
                << " matching_associate_os=" << key.second
                << " central=" << ratio
                << " error=" << error
                << " propagation=independent_quadrature\n";
    }
  }

  std::cout << "GATE_D_ANALYSIS_SUMMARY errors=" << errors
            << " central_pair_files=" << centralPairFiles
            << " block_pair_files=" << blockPairFiles
            << " object_closure_checks=" << objectClosureChecks
            << " trigger_normalization_comparisons="
            << triggerNormalizationComparisons
            << " yield_rows=" << yieldRows
            << " balancing_rows=" << balancingRows
            << " baryon_ratio_rows=" << baryonRatioRows
            << " independent_tune_ratio_rows=" << tuneRatioRows
            << " independent_baryon_tune_double_ratio_rows="
            << baryonTuneDoubleRatioRows
            << " finite_yield_rows=" << finiteYieldRows
            << " finite_balancing_rows=" << finiteBalancingRows
            << " finite_baryon_ratio_rows=" << finiteBaryonRatioRows
            << " finite_independent_tune_ratio_rows="
            << finiteTuneRatioRows
            << " finite_independent_baryon_tune_double_ratio_rows="
            << finiteBaryonTuneDoubleRatioRows
            << " zero_yield_sem_rows=" << zeroYieldSemRows
            << " nonfinite_yield_rows=" << nonfiniteYieldRows
            << " zero_balancing_sem_rows=" << zeroBalancingSemRows
            << " nonfinite_balancing_rows=" << nonfiniteBalancingRows
            << " zero_baryon_ratio_sem_rows="
            << zeroBaryonRatioSemRows
            << " nonfinite_baryon_ratio_rows="
            << nonfiniteBaryonRatioRows
            << " zero_baryon_ratio_denominators="
            << zeroBaryonRatioDenominators
            << " zero_tune_ratio_error_rows="
            << zeroTuneRatioErrorRows
            << " nonfinite_tune_ratio_rows="
            << nonfiniteTuneRatioRows
            << " zero_baryon_tune_double_ratio_error_rows="
            << zeroBaryonTuneDoubleRatioErrorRows
            << " nonfinite_baryon_tune_double_ratio_rows="
            << nonfiniteBaryonTuneDoubleRatioRows
            << " bzero_sigma_filename_correct="
            << (bzeroSigmaFound ? "true" : "false") << "\n";
  return errors;
}
