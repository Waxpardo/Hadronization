#include "../contracts/GeneratedPairRegistry.h"
#include "../contracts/GeneratedPairObjectContract.h"
#include "../contracts/AssociateOriginCategoryContract.h"
#include "../contracts/GeneratedSpeciesOrdinals.h"

#include <TFile.h>
#include <TAxis.h>
#include <TH1.h>
#include <TH1D.h>
#include <THnSparse.h>
#include <TObjString.h>
#include <TParameter.h>

#include <algorithm>
#include <cmath>
#include <iostream>
#include <map>
#include <memory>
#include <set>
#include <string>
#include <string_view>
#include <type_traits>
#include <utility>
#include <vector>

namespace PairBlockClosure {

constexpr int kBlockCount = 10;
constexpr double kMergeRelativeTolerance = 2e-10;
using Coordinate = std::vector<Int_t>;
using BinTotal = std::pair<double, double>;
using SparseBinMap = std::map<Coordinate, BinTotal>;

bool NearlyEqual(double first, double second) {
  return std::isfinite(first) && std::isfinite(second) &&
         std::abs(first - second) <=
             kMergeRelativeTolerance *
                 std::max({1.0, std::abs(first), std::abs(second)});
}

bool AxesEqual(const TAxis* first, const TAxis* second) {
  if (!first || !second || first->GetNbins() != second->GetNbins()) {
    return false;
  }
  for (int bin = 1; bin <= first->GetNbins() + 1; ++bin) {
    if (first->GetBinLowEdge(bin) != second->GetBinLowEdge(bin)) {
      return false;
    }
  }
  return true;
}

double HistogramErrorSquared(TH1* histogram, int bin) {
  return histogram->GetSumw2()->At(bin);
}

bool HistogramEqualsBlockSum(TH1* central,
                             const std::vector<TH1*>& blocks) {
  if (!central || central->GetSumw2N() != central->GetNcells() ||
      blocks.size() != kBlockCount) {
    return false;
  }
  for (TH1* block : blocks) {
    if (!block || block->GetDimension() != central->GetDimension() ||
        block->GetNcells() != central->GetNcells() ||
        block->GetSumw2N() != block->GetNcells() ||
        !AxesEqual(central->GetXaxis(), block->GetXaxis())) {
      return false;
    }
  }
  double blockEntries = 0.0;
  for (TH1* block : blocks) blockEntries += block->GetEntries();
  if (!NearlyEqual(central->GetEntries(), blockEntries)) return false;
  for (int bin = 0; bin < central->GetNcells(); ++bin) {
    const double centralContent = central->GetBinContent(bin);
    const double centralErrorSquared =
        HistogramErrorSquared(central, bin);
    double content = 0.0;
    double errorSquared = 0.0;
    for (TH1* block : blocks) {
      content += block->GetBinContent(bin);
      errorSquared += HistogramErrorSquared(block, bin);
    }
    if (!NearlyEqual(centralContent, content) ||
        !NearlyEqual(centralErrorSquared, errorSquared)) {
      return false;
    }
  }
  return true;
}

SparseBinMap SparseBins(THnSparse* histogram, bool& valid) {
  SparseBinMap values;
  if (!histogram) {
    valid = false;
    return values;
  }
  std::vector<Int_t> coordinate(histogram->GetNdimensions());
  for (Long64_t bin = 0; bin < histogram->GetNbins(); ++bin) {
    const double content =
        histogram->GetBinContent(bin, coordinate.data());
    const double errorSquared = histogram->GetBinError2(bin);
    if (!std::isfinite(content) || !std::isfinite(errorSquared) ||
        errorSquared < 0.0) {
      valid = false;
      return {};
    }
    values[coordinate] = {content, errorSquared};
  }
  return values;
}

bool SparseAxesEqual(THnSparse* first, THnSparse* second) {
  if (!first || !second ||
      first->GetNdimensions() != second->GetNdimensions()) {
    return false;
  }
  for (int axis = 0; axis < first->GetNdimensions(); ++axis) {
    if (!AxesEqual(first->GetAxis(axis), second->GetAxis(axis))) {
      return false;
    }
  }
  return true;
}

bool SparseEqualsBlockSum(THnSparse* central,
                          const std::vector<THnSparse*>& blocks) {
  if (!central || !central->GetCalculateErrors() ||
      blocks.size() != kBlockCount) {
    return false;
  }
  for (THnSparse* block : blocks) {
    if (!block || !block->GetCalculateErrors() ||
        !SparseAxesEqual(central, block)) {
      return false;
    }
  }
  double blockEntries = 0.0;
  for (THnSparse* block : blocks) blockEntries += block->GetEntries();
  if (!NearlyEqual(central->GetEntries(), blockEntries)) return false;

  bool valid = true;
  const SparseBinMap expected = SparseBins(central, valid);
  if (!valid) return false;
  SparseBinMap observed;
  for (THnSparse* block : blocks) {
    const SparseBinMap values = SparseBins(block, valid);
    if (!valid) return false;
    for (const auto& [coordinate, total] : values) {
      observed[coordinate].first += total.first;
      observed[coordinate].second += total.second;
    }
  }
  for (const auto& [coordinate, total] : expected) {
    const auto found = observed.find(coordinate);
    const BinTotal sum =
        found == observed.end() ? BinTotal{} : found->second;
    if (!NearlyEqual(total.first, sum.first) ||
        !NearlyEqual(total.second, sum.second)) {
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

// TFile::Get hands ownership to the caller for anything that does not
// inherit TH1, because only TH1 participates in TH1::AddDirectory adoption.
// TParameter, TObjString and THnSparse are all in that category. Not deleting
// them leaked ~6 MB per pair file here, which crossed the 2.00 GiB user-slice
// cgroup cap partway through the 300-file loop and killed the merge.
// TH1 is the exception and must NOT be deleted: it belongs to the TFile and
// goes when the file closes.
template <typename T>
bool ParameterValue(TFile& file, const char* name, T& value) {
  const std::unique_ptr<TObject> owned(file.Get(name));
  auto* parameter = dynamic_cast<TParameter<T>*>(owned.get());
  if (!parameter) return false;
  value = parameter->GetVal();
  return true;
}

bool ObjectStringValue(TFile& file, const char* name, std::string& value) {
  const std::unique_ptr<TObject> owned(file.Get(name));
  auto* object = dynamic_cast<TObjString*>(owned.get());
  if (!object) return false;
  value = object->GetString().Data();
  return true;
}

bool InvariantObjectStringMatches(TFile& central,
                                  const std::vector<TFile*>& blocks,
                                  const char* name,
                                  const char* expected) {
  std::string centralValue;
  if (!ObjectStringValue(central, name, centralValue) ||
      centralValue != expected) {
    return false;
  }
  for (TFile* block : blocks) {
    std::string blockValue;
    if (!block || !ObjectStringValue(*block, name, blockValue) ||
        blockValue != centralValue) {
      return false;
    }
  }
  return true;
}

template <typename T>
bool AdditiveParameterEqualsBlockSum(
    TFile& central, const std::vector<TFile*>& blocks, const char* name) {
  T expected{};
  if (!ParameterValue(central, name, expected)) return false;
  T observed{};
  for (TFile* block : blocks) {
    T value{};
    if (!block || !ParameterValue(*block, name, value)) return false;
    observed += value;
  }
  if constexpr (std::is_floating_point_v<T>) {
    return NearlyEqual(expected, observed);
  }
  return expected == observed;
}

std::string PairPath(const std::string& directory,
                     const std::string_view filename) {
  return directory + "/" + std::string(filename);
}

std::string BlockDirectory(const std::string& base, int block) {
  return base + "/combined_root_" + std::to_string(block);
}

}  // namespace PairBlockClosure

// The caller supplies the required campaign schema.
// A default derived from the central file could validate the wrong schema.
int ValidatePairBlockClosure(const char* centralDirectory,
                             const char* blockBaseDirectory,
                             Long64_t expectedCentralEvents = -1,
                             const char* expectedSchema = nullptr) {
  using namespace PairBlockClosure;
  const std::string centralBase =
      centralDirectory ? centralDirectory : "";
  const std::string blockBase =
      blockBaseDirectory ? blockBaseDirectory : "";
  const std::string requiredSchema = expectedSchema ? expectedSchema : "";
  int errors = 0;
  int centralPairFiles = 0;
  int blockPairFiles = 0;
  int objectClosureChecks = 0;
  int additiveMetadataClosureChecks = 0;
  int invariantMetadataChecks = 0;
  int sourceFilterContractChecks = 0;
  auto fail = [&](const std::string& message) {
    std::cerr << "PAIR_BLOCK_CLOSURE_ERROR " << message << "\n";
    ++errors;
  };
  if (centralBase.empty() || blockBase.empty() ||
      expectedCentralEvents == 0 || expectedCentralEvents < -1) {
    fail("invalid directory or expected-event argument");
  }
  if (requiredSchema.empty()) {
    fail(
        "EXPECTED_SCHEMA is required and was not supplied; this gate does not "
        "derive the required schema from the data it is checking");
  } else {
    Hadronization::PairSchemaVersion requiredParsed;
    if (!Hadronization::ParsePairSchemaVersion(requiredSchema, requiredParsed)) {
      fail("unknown EXPECTED_SCHEMA '" + requiredSchema + "'");
    }
  }

  // These three lists were hand-maintained here and had drifted from the
  // pair-file contract: sparseObjects omitted hFlavourClosure, which
  // 7cf9f86 added to every pair file, so the ten-block closure silently
  // skipped it. They now come from the generated contract, which is the
  // single source of truth shared with the pair-directory allowlist and the
  // plotting-input validator.
  //
  // The three lists are keyed on the schema the data actually declares. They
  // are resolved once, from the first central file, and every later file must
  // agree: the closure compares a central against its own ten blocks, so a
  // directory that mixed schemas is not a closure at all and must not be
  // silently summed. Unknown or missing schema is fatal, never a default.
  bool schemaResolved = false;
  Hadronization::PairSchemaVersion schemaVersion =
      Hadronization::PairSchemaVersion::kV2;
  std::string schemaTag;
  std::set<std::string> longAdditiveParameters;
  std::set<std::string> doubleAdditiveParameters;
  std::set<std::string> sparseObjects;
  auto adoptSchema = [&](TFile& file, const std::string& path) {
    std::string declared;
    if (!ObjectStringValue(file, "analysis_schema", declared)) {
      fail("no analysis_schema in " + path);
      return false;
    }
    if (!schemaResolved) {
      Hadronization::PairSchemaVersion parsed;
      if (!Hadronization::ParsePairSchemaVersion(declared, parsed)) {
        fail("unknown analysis_schema '" + declared + "' in " + path +
             "; refusing to guess which object contract applies");
        return false;
      }
      // THE CAMPAIGN GATE. Adopting the declared schema is right for checking
      // internal consistency; it is not a requirement. This is where the
      // requirement is applied -- before a single count is derived, so the
      // 1800/600 arithmetic is never even reached for a v2 directory that a v3
      // campaign asked for.
      if (!requiredSchema.empty() && declared != requiredSchema) {
        fail("analysis_schema '" + declared + "' in " + path +
             " but the campaign requires '" + requiredSchema +
             "'. This is the 1800/600 failure mode: a complete, internally "
             "consistent dataset of the WRONG schema.");
        return false;
      }
      schemaVersion = parsed;
      schemaTag = declared;
      schemaResolved = true;
      longAdditiveParameters = Hadronization::ClosureCheckedScalars(
          "TParameter<Long64_t>", schemaVersion);
      doubleAdditiveParameters = Hadronization::ClosureCheckedScalars(
          "TParameter<double>", schemaVersion);
      sparseObjects =
          Hadronization::ClosureCheckedObjects("THnSparse", schemaVersion);
      return true;
    }
    if (declared != schemaTag) {
      fail("analysis_schema '" + declared + "' in " + path +
           " differs from '" + schemaTag +
           "' adopted for this closure; a mixed-schema directory is not a "
           "closure");
      return false;
    }
    return true;
  };

  for (const auto& definition : Hadronization::kPairDefinitions) {
    const std::string centralPath =
        PairPath(centralBase, definition.filename);
    std::unique_ptr<TFile> central(TFile::Open(centralPath.c_str(), "READ"));
    if (!central || central->IsZombie()) {
      fail("missing or unreadable central pair file " + centralPath);
      continue;
    }
    ++centralPairFiles;
    if (!adoptSchema(*central, centralPath)) continue;

    std::vector<std::unique_ptr<TFile>> ownedBlocks;
    std::vector<TFile*> blocks;
    bool filesOk = true;
    for (int block = 1; block <= kBlockCount; ++block) {
      const std::string path =
          PairPath(BlockDirectory(blockBase, block), definition.filename);
      std::unique_ptr<TFile> file(TFile::Open(path.c_str(), "READ"));
      if (!file || file->IsZombie()) {
        fail("missing or unreadable block pair file " + path);
        filesOk = false;
        break;
      }
      ++blockPairFiles;
      if (!adoptSchema(*file, path)) {
        filesOk = false;
        break;
      }
      blocks.push_back(file.get());
      ownedBlocks.push_back(std::move(file));
    }
    if (!filesOk) continue;

    // Deliberately NOT owned here: TH1 is adopted by the TFile via
    // TH1::AddDirectory, which is left at its default kTRUE in this macro, so
    // deleting it would be a double free.
    auto* centralMultiplicity =
        dynamic_cast<TH1*>(central->Get("summed MULTIPLICITY"));
    std::vector<TH1*> blockMultiplicities;
    for (TFile* block : blocks) {
      blockMultiplicities.push_back(
          dynamic_cast<TH1*>(block->Get("summed MULTIPLICITY")));
    }
    ++objectClosureChecks;
    if (!HistogramEqualsBlockSum(centralMultiplicity,
                                 blockMultiplicities)) {
      fail("summed MULTIPLICITY content/Sumw2 closure differs for " +
           centralPath);
    }
    for (const std::string& objectName : sparseObjects) {
      // Owned here, not by the TFile. These are the large ones: across the
      // 300 pair files hTrKinematics and hFlavourClosure average ~49k and
      // ~47k filled bins each.
      const std::unique_ptr<TObject> ownedCentral(
          central->Get(objectName.c_str()));
      auto* centralSparse =
          dynamic_cast<THnSparse*>(ownedCentral.get());
      std::vector<std::unique_ptr<TObject>> ownedBlockSparses;
      std::vector<THnSparse*> blockSparses;
      for (TFile* block : blocks) {
        ownedBlockSparses.emplace_back(block->Get(objectName.c_str()));
        blockSparses.push_back(
            dynamic_cast<THnSparse*>(ownedBlockSparses.back().get()));
      }
      ++objectClosureChecks;
      if (!SparseEqualsBlockSum(centralSparse, blockSparses)) {
        fail(objectName +
             " content/Sumw2 closure differs for " + centralPath);
      }
    }

    for (const std::string& parameter : longAdditiveParameters) {
      ++additiveMetadataClosureChecks;
      if (!AdditiveParameterEqualsBlockSum<Long64_t>(
              *central, blocks, parameter.c_str())) {
        fail(parameter +
             " central/block additive closure differs for " +
             centralPath);
      }
    }
    for (const std::string& parameter : doubleAdditiveParameters) {
      ++additiveMetadataClosureChecks;
      if (!AdditiveParameterEqualsBlockSum<double>(
              *central, blocks, parameter.c_str())) {
        fail(parameter +
             " central/block additive closure differs for " +
             centralPath);
      }
    }
    // WHICH objects are identity-checked is DERIVED from the contract, not
    // listed here. This pair used to be hand-written, which meant an object
    // could be added to the contract and silently never checked -- the exact
    // shape of the hFlavourClosure gap, one axis over. The contract now says
    // identity_checked, and the only thing this file still owns is the
    // EXPECTED VALUE for each name, which is a compile-time constant and
    // cannot come from JSON.
    //
    // The mapping must cover the derived set exactly. A name the contract
    // marks identity_checked and this table does not know is a FAILURE, not a
    // skip: silently not checking it is the defect being prevented.
    const std::map<std::string, const char*> identityExpectations = {
        {"associate_origin_category_schema",
         Hadronization::kAssociateOriginCategorySchema},
        {"associate_origin_category_labels",
         Hadronization::kAssociateOriginCategoryLabels},
        {"species_ordinal_schema", Hadronization::kSpeciesOrdinalSchema},
        {"species_ordinal_labels", Hadronization::kSpeciesOrdinalLabels},
        {"species_ordinal_digest", Hadronization::kSpeciesOrdinalDigest},
    };
    for (const auto& name :
         Hadronization::IdentityCheckedObjects(schemaVersion)) {
      const auto expectation = identityExpectations.find(name);
      if (expectation == identityExpectations.end()) {
        fail("the contract marks " + name +
             " identity_checked but this closure has no expected value for "
             "it, so it would go unchecked. Teach it here rather than "
             "dropping the check.");
        continue;
      }
      ++invariantMetadataChecks;
      if (!InvariantObjectStringMatches(*central, blocks, name.c_str(),
                                        expectation->second)) {
        fail(name + " central/block invariant metadata differs for " +
             centralPath);
      }
    }

    bool filterOk = true;
    std::string centralFilter;
    int centralModulo = -1;
    int centralRemainder = -2;
    Long64_t centralEvents = -1;
    Long64_t centralSourceEvents = -1;
    int centralInputFiles = -1;
    filterOk =
        ObjectStringValue(*central, "event_filter_schema", centralFilter) &&
        ParameterValue(*central, "event_filter_modulo", centralModulo) &&
        ParameterValue(*central, "event_filter_remainder",
                       centralRemainder) &&
        ParameterValue(*central, "input_events", centralEvents) &&
        ParameterValue(*central, "source_input_events",
                       centralSourceEvents) &&
        ParameterValue(*central, "input_file_count", centralInputFiles);
    const bool centralContract =
        filterOk && centralFilter == "all_events_v1" &&
        centralModulo == 0 && centralRemainder == -1 &&
        centralEvents > 0 && centralSourceEvents == centralEvents &&
        centralInputFiles > 0 &&
        (expectedCentralEvents < 0 ||
         centralEvents == expectedCentralEvents);

    bool allEventBlocks = true;
    bool moduloBlocks = true;
    Long64_t blockEventSum = 0;
    Long64_t blockSourceEventSum = 0;
    int blockInputFileSum = 0;
    for (int index = 0; index < kBlockCount; ++index) {
      std::string filter;
      int modulo = -1;
      int remainder = -2;
      Long64_t events = -1;
      Long64_t sourceEvents = -1;
      int inputFiles = -1;
      const bool ok =
          ObjectStringValue(*blocks[index], "event_filter_schema", filter) &&
          ParameterValue(*blocks[index], "event_filter_modulo", modulo) &&
          ParameterValue(*blocks[index], "event_filter_remainder",
                         remainder) &&
          ParameterValue(*blocks[index], "input_events", events) &&
          ParameterValue(*blocks[index], "source_input_events",
                         sourceEvents) &&
          ParameterValue(*blocks[index], "input_file_count", inputFiles);
      if (!ok || events <= 0 || sourceEvents <= 0 || inputFiles <= 0) {
        filterOk = false;
      }
      allEventBlocks =
          allEventBlocks && ok && filter == "all_events_v1" &&
          modulo == 0 && remainder == -1 && sourceEvents == events;
      moduloBlocks =
          moduloBlocks && ok &&
          filter == "unsigned_event_id_modulo_v1" &&
          modulo == kBlockCount && remainder == index &&
          sourceEvents == centralSourceEvents &&
          inputFiles == centralInputFiles;
      blockEventSum += events;
      blockSourceEventSum += sourceEvents;
      blockInputFileSum += inputFiles;
    }
    const bool sourceContract =
        centralContract && filterOk &&
        (allEventBlocks || moduloBlocks) &&
        blockEventSum == centralEvents &&
        ((allEventBlocks &&
          blockSourceEventSum == centralSourceEvents &&
          blockInputFileSum == centralInputFiles) ||
         moduloBlocks);
    ++sourceFilterContractChecks;
    if (!sourceContract) {
      fail("central/ten-block event-source/filter contract differs for " +
           centralPath);
    }
    ++additiveMetadataClosureChecks;
    if ((allEventBlocks &&
         blockInputFileSum != centralInputFiles) ||
        (moduloBlocks &&
         blockInputFileSum != kBlockCount * centralInputFiles)) {
      fail("input_file_count central/block contract differs for " +
           centralPath);
    }
    ++additiveMetadataClosureChecks;
    if ((allEventBlocks &&
         blockSourceEventSum != centralSourceEvents) ||
        (moduloBlocks &&
         blockSourceEventSum !=
             kBlockCount * centralSourceEvents)) {
      fail("source_input_events central/block contract differs for " +
           centralPath);
    }
  }

  // The adopted schema is REPORTED because the object count is a function of
  // it: the wrapper derives its expected count from the contract, and without
  // knowing which version the data declared it would derive the count for the
  // wrong one the first time an object is added to a newer schema. Reporting
  // it keeps the wrapper and the macro reading one source of truth, which is
  // the same principle that removed the pinned 1500 in the first place.
  std::cout
      << "PAIR_BLOCK_CLOSURE errors=" << errors
      << " analysis_schema=" << (schemaTag.empty() ? "NONE" : schemaTag)
      << " central_pair_files=" << centralPairFiles
      << " block_pair_files=" << blockPairFiles
      << " object_content_sumw2_closure_checks=" << objectClosureChecks
      << " additive_metadata_closure_checks="
      << additiveMetadataClosureChecks
      << " invariant_metadata_checks=" << invariantMetadataChecks
      << " source_filter_contract_checks=" << sourceFilterContractChecks
      << " expected_central_events=" << expectedCentralEvents
      << " relative_tolerance=" << kMergeRelativeTolerance << "\n";
  return errors;
}

int TestPairBlockClosureArithmetic() {
  using namespace PairBlockClosure;
  TH1D centralMultiplicity("central_multiplicity", "", 5, 0.0, 5.0);
  centralMultiplicity.Sumw2();
  std::vector<std::unique_ptr<TH1D>> ownedMultiplicities;
  std::vector<TH1*> multiplicities;

  const Int_t dimensions = 2;
  const Int_t bins[dimensions] = {5, 5};
  const Double_t minimum[dimensions] = {0.0, 0.0};
  const Double_t maximum[dimensions] = {5.0, 5.0};
  THnSparseD centralSparse("central_sparse", "", dimensions, bins, minimum,
                           maximum);
  centralSparse.Sumw2();
  std::vector<std::unique_ptr<THnSparseD>> ownedSparses;
  std::vector<THnSparse*> sparses;
  for (int block = 0; block < kBlockCount; ++block) {
    auto multiplicity =
        std::make_unique<TH1D>(
            ("multiplicity_" + std::to_string(block)).c_str(), "", 5, 0.0,
            5.0);
    multiplicity->Sumw2();
    multiplicity->Fill(block % 5 + 0.5, block + 1.0);
    centralMultiplicity.Add(multiplicity.get());
    multiplicities.push_back(multiplicity.get());
    ownedMultiplicities.push_back(std::move(multiplicity));

    auto sparse = std::make_unique<THnSparseD>(
        ("sparse_" + std::to_string(block)).c_str(), "", dimensions, bins,
        minimum, maximum);
    sparse->Sumw2();
    Double_t coordinate[dimensions] = {
        static_cast<Double_t>(block % 5) + 0.5,
        static_cast<Double_t>((block + 1) % 5) + 0.5};
    sparse->Fill(coordinate, block + 1.0);
    centralSparse.Add(sparse.get());
    sparses.push_back(sparse.get());
    ownedSparses.push_back(std::move(sparse));
  }

  int errors = 0;
  if (!HistogramEqualsBlockSum(&centralMultiplicity, multiplicities) ||
      !SparseEqualsBlockSum(&centralSparse, sparses)) {
    std::cerr << "PAIR_BLOCK_CLOSURE_TEST exact block sum was rejected\n";
    ++errors;
  }
  multiplicities.front()->Fill(4.5, 3.0);
  Double_t mutation[dimensions] = {4.5, 4.5};
  sparses.front()->Fill(mutation, 3.0);
  const bool histogramMutationRejected =
      !HistogramEqualsBlockSum(&centralMultiplicity, multiplicities);
  const bool sparseMutationRejected =
      !SparseEqualsBlockSum(&centralSparse, sparses);
  if (!histogramMutationRejected || !sparseMutationRejected) {
    std::cerr << "PAIR_BLOCK_CLOSURE_TEST mutated block sum was accepted\n";
    ++errors;
  }
  std::cout
      << "PAIR_BLOCK_CLOSURE_TEST errors=" << errors
      << " exact_content_sumw2_sum_accepted="
      << (errors == 0 ? "true" : "false")
      << " histogram_mutation_rejected="
      << (histogramMutationRejected ? "true" : "false")
      << " sparse_mutation_rejected="
      << (sparseMutationRejected ? "true" : "false") << "\n";
  return errors;
}
