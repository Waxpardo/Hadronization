// generated_heavy_flavor_summary.C
//
// Summarize heavy-flavour content in generated-event ROOT trees.
//
// Usage from the Hadronization base:
//   root -l -b -q 'AnalysisScripts/CountEvents/generated_heavy_flavor_summary.C++("RootFiles/HF/MONASH","monash_generated_hf_summary.csv")'
//   root -l -b -q 'AnalysisScripts/CountEvents/generated_heavy_flavor_summary.C++("RootFiles/HF/JUNCTIONS","junctions_generated_hf_summary.csv")'
//   root -l -b -q 'AnalysisScripts/CountEvents/generated_heavy_flavor_summary.C++("RootFiles/HF/CLOSEPACKING","closepacking_generated_hf_summary.csv")'
//
// Full three-tune LaTeX table:
//   root -l -b <<'ROOTCMDS'
//   .L AnalysisScripts/CountEvents/generated_heavy_flavor_summary.C+
//   generated_heavy_flavor_summary_latex_table("RootFiles/HF", "Paper/Tables/generated_heavy_flavor_summary.tex");
//   .q
//   ROOTCMDS
//
// Counting criteria and assumptions:
// - The input is the current unified generated-event tree named "tree" by
//   default, with one entry per event written by the producer.
// - The current producer stores final-state particles only: charm-only hadrons,
//   beauty-only hadrons, Bc hadrons, and pions passing pT >= 0.15 GeV/c and
//   |eta| <= 4.0. The tree is not a full PYTHIA event record.
// - Hadrons are counted by exact PDG ID in the ID branch:
//     B+ 521, B- -521, Lambda_b0 5122, anti-Lambda_b0 -5122,
//     D+ 411, D- -411, Lambda_c+ 4122, anti-Lambda_c- -4122.
// - Each stored particle entry is counted once. The macro does not follow the
//   mother/daughter graph and does not count decay products as their parent.
// - statusSelection="stored" applies no extra status cut because the producer
//   already required particle.isFinal() before writing the particle. Passing
//   statusSelection="positive" additionally requires STATUS > 0 when the STATUS
//   branch is available.
// - countBackend="auto" uses the producer-level histograms for the default
//   stored-particle count. Those histograms are filled from the same accepted
//   final-state particles as the tree and are much faster for full 100M samples.
//   If the histograms are missing, or if statusSelection is not "stored", the
//   macro falls back to reading the tree.
// - NCHARM, NBEAUTY, and NBC in the current producer are final-state accepted
//   heavy-hadron counters, not pre-hadronization parton-level quark counters.
//   Therefore the normalization printed here is the stored accepted heavy-flavour
//   valence content: beauty-only hadron = 1 b/bbar, charm-only hadron = 1 c/cbar,
//   Bc hadron = 1 b/bbar and 1 c/cbar. This is the best normalization available
//   from the current ROOT trees. A true generated parton-level b/c quark count
//   requires the producer to write dedicated quark counters before final-state
//   filtering.

#include <algorithm>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include "TBranch.h"
#include "TChain.h"
#include "TFile.h"
#include "TH1.h"
#include "TString.h"
#include "TSystem.h"
#include "TTree.h"

namespace GeneratedHeavyFlavorSummaryDetail {

struct Species {
  std::string name;
  int pdg = 0;
  char flavor = ' ';
  Long64_t rawYield = 0;
};

struct TuneSummary {
  std::string label;
  int inputFiles = 0;
  Long64_t totalEvents = 0;
  Long64_t totalBeautyContent = 0;
  Long64_t totalCharmContent = 0;
  Long64_t treeEntriesCrossCheck = 0;
  std::vector<Species> species;
};

bool FillFromProducerHistograms(const std::vector<std::string>& files,
                                const std::string& treeName,
                                std::vector<Species>& species,
                                Long64_t& totalEvents,
                                Long64_t& totalBeautyContent,
                                Long64_t& totalCharmContent,
                                Long64_t& treeEntriesCrossCheck,
                                std::string& failureReason);

std::vector<Species> DefaultSpecies()
{
  return {
    {"B+", 521, 'b', 0},
    {"B-", -521, 'b', 0},
    {"Lambda_b0", 5122, 'b', 0},
    {"anti-Lambda_b0", -5122, 'b', 0},
    {"D+", 411, 'c', 0},
    {"D-", -411, 'c', 0},
    {"Lambda_c+", 4122, 'c', 0},
    {"anti-Lambda_c-", -4122, 'c', 0},
  };
}

bool EndsWith(const std::string& value, const std::string& suffix)
{
  if (value.size() < suffix.size()) return false;
  return value.compare(value.size() - suffix.size(), suffix.size(), suffix) == 0;
}

std::string ExpandPath(const std::string& path)
{
  char* expanded = gSystem->ExpandPathName(path.c_str());
  std::string out = expanded ? expanded : path;
  delete[] expanded;
  return out;
}

std::string GetBaseDir()
{
  const char* env = gSystem->Getenv("HADRONIZATION_BASE");
  if (env && env[0] != '\0') return ExpandPath(env);

  std::ifstream fin("base_path.txt");
  if (fin) {
    std::string line;
    std::getline(fin, line);
    if (!line.empty()) return ExpandPath(line);
  }

  return ExpandPath(".");
}

bool IsAbsolutePath(const std::string& path)
{
  return !path.empty() && path[0] == '/';
}

std::string ResolveFromBase(const std::string& path)
{
  if (path.empty()) return path;
  if (IsAbsolutePath(path)) return ExpandPath(path);
  return ExpandPath(GetBaseDir() + "/" + path);
}

bool IsDirectory(const std::string& path)
{
  void* dir = gSystem->OpenDirectory(path.c_str());
  if (!dir) return false;
  gSystem->FreeDirectory(dir);
  return true;
}

void CollectRootFiles(const std::string& path, std::vector<std::string>& files)
{
  if (IsDirectory(path)) {
    void* dir = gSystem->OpenDirectory(path.c_str());
    if (!dir) return;

    const char* entry = nullptr;
    while ((entry = gSystem->GetDirEntry(dir))) {
      std::string name(entry);
      if (name == "." || name == "..") continue;

      const std::string child = path + "/" + name;
      if (IsDirectory(child)) {
        CollectRootFiles(child, files);
      } else if (EndsWith(name, ".root")) {
        files.push_back(child);
      }
    }

    gSystem->FreeDirectory(dir);
    return;
  }

  if (EndsWith(path, ".root")) {
    files.push_back(path);
  }
}

bool HasQuarkDigit(int particlePdg, int quarkDigit)
{
  int pdg = std::abs(particlePdg);
  if (pdg == quarkDigit) return true;

  pdg /= 10; // drop final spin/excitation digit for hadrons
  if (pdg % 10 == quarkDigit) return true;
  pdg /= 10;
  if (pdg % 10 == quarkDigit) return true;
  pdg /= 10;
  if (pdg % 10 == quarkDigit) return true;

  return false;
}

bool HasBeauty(int pdg)
{
  return HasQuarkDigit(pdg, 5);
}

bool HasCharm(int pdg)
{
  return HasQuarkDigit(pdg, 4);
}

bool PassStatus(Long64_t index,
                const std::vector<Double_t>* status,
                const std::string& statusSelection)
{
  if (statusSelection == "stored") return true;

  if (statusSelection == "positive") {
    if (!status) return true;
    if (index < 0 || static_cast<size_t>(index) >= status->size()) return false;
    return status->at(static_cast<size_t>(index)) > 0.0;
  }

  throw std::runtime_error("Unknown statusSelection '" + statusSelection +
                           "'. Use 'stored' or 'positive'.");
}

std::string ParentDirectory(const std::string& path)
{
  const size_t pos = path.find_last_of('/');
  if (pos == std::string::npos) return "";
  if (pos == 0) return "/";
  return path.substr(0, pos);
}

void EnsureParentDirectory(const std::string& path)
{
  const std::string parent = ParentDirectory(path);
  if (parent.empty()) return;
  gSystem->mkdir(parent.c_str(), kTRUE);
}

std::string CsvEscape(const std::string& value)
{
  bool needsQuotes = false;
  for (char c : value) {
    if (c == '"' || c == ',' || c == '\n' || c == '\r') {
      needsQuotes = true;
      break;
    }
  }

  if (!needsQuotes) return value;

  std::string escaped = "\"";
  for (char c : value) {
    if (c == '"') escaped += "\"\"";
    else escaped += c;
  }
  escaped += "\"";
  return escaped;
}

std::string FormatRate(double value)
{
  if (!std::isfinite(value)) return "n/a";

  std::ostringstream out;
  out << std::scientific << std::setprecision(8) << value;
  return out.str();
}

double SafeDivide(Long64_t numerator, Long64_t denominator)
{
  if (denominator <= 0) return std::numeric_limits<double>::quiet_NaN();
  return static_cast<double>(numerator) / static_cast<double>(denominator);
}

Long64_t RoundedCount(double value)
{
  return static_cast<Long64_t>(std::llround(value));
}

Long64_t HistogramEntries(TH1* h)
{
  if (!h) return 0;
  return RoundedCount(h->GetEntries());
}

Long64_t HistogramIntegralAllBins(TH1* h)
{
  if (!h) return 0;
  return RoundedCount(h->Integral(0, h->GetNbinsX() + 1));
}

Long64_t HistogramPdgYield(TH1* h, int pdg)
{
  if (!h) return 0;
  const int bin = h->FindFixBin(static_cast<double>(pdg));
  return RoundedCount(h->GetBinContent(bin));
}

TuneSummary SummarizeTuneFromProducerHistograms(const std::string& label,
                                                const std::string& inputDir,
                                                const std::string& treeName)
{
  std::vector<std::string> files;
  CollectRootFiles(inputDir, files);
  std::sort(files.begin(), files.end());

  if (files.empty()) {
    throw std::runtime_error("No ROOT files found for " + label + " under " + inputDir);
  }

  TuneSummary summary;
  summary.label = label;
  summary.inputFiles = static_cast<int>(files.size());
  summary.species = DefaultSpecies();

  std::string failureReason;
  const bool ok = FillFromProducerHistograms(files,
                                             treeName,
                                             summary.species,
                                             summary.totalEvents,
                                             summary.totalBeautyContent,
                                             summary.totalCharmContent,
                                             summary.treeEntriesCrossCheck,
                                             failureReason);
  if (!ok) {
    throw std::runtime_error("Could not summarize " + label + " with producer histograms: " + failureReason);
  }

  return summary;
}

void AddTuneSummary(TuneSummary& total, const TuneSummary& part)
{
  if (total.species.empty()) total.species = DefaultSpecies();

  total.inputFiles += part.inputFiles;
  total.totalEvents += part.totalEvents;
  total.totalBeautyContent += part.totalBeautyContent;
  total.totalCharmContent += part.totalCharmContent;
  total.treeEntriesCrossCheck += part.treeEntriesCrossCheck;

  for (size_t i = 0; i < total.species.size() && i < part.species.size(); ++i) {
    total.species[i].rawYield += part.species[i].rawYield;
  }
}

std::string LatexInteger(Long64_t value)
{
  const bool negative = value < 0;
  std::string digits = std::to_string(negative ? -value : value);
  std::string grouped;

  for (size_t i = 0; i < digits.size(); ++i) {
    const size_t remaining = digits.size() - i;
    if (i > 0 && remaining % 3 == 0) {
      grouped += "\\,";
    }
    grouped += digits[i];
  }

  if (negative) grouped = "-" + grouped;
  return "$" + grouped + "$";
}

std::string LatexSpeciesName(const std::string& name)
{
  if (name == "B+") return "$B^{+}$";
  if (name == "B-") return "$B^{-}$";
  if (name == "Lambda_b0") return "$\\Lambda_{b}^{0}$";
  if (name == "anti-Lambda_b0") return "$\\overline{\\Lambda}_{b}^{0}$";
  if (name == "D+") return "$D^{+}$";
  if (name == "D-") return "$D^{-}$";
  if (name == "Lambda_c+") return "$\\Lambda_{c}^{+}$";
  if (name == "anti-Lambda_c-") return "$\\overline{\\Lambda}_{c}^{-}$";
  return name;
}

void WriteLatexSummaryTable(const std::vector<TuneSummary>& tuneSummaries,
                            const TuneSummary& overall,
                            const std::string& outputTex)
{
  EnsureParentDirectory(outputTex);
  std::ofstream tex(outputTex);
  if (!tex) {
    throw std::runtime_error("Could not open LaTeX output for writing: " + outputTex);
  }

  tex << "% Auto-generated by AnalysisScripts/CountEvents/generated_heavy_flavor_summary.C\n";
  tex << "% Requires \\usepackage{booktabs}.\n";
  tex << "\\begin{table}[tbp]\n";
  tex << "\\centering\n";
  tex << "\\caption{Generated-event sample sizes and selected heavy-flavour hadron yields for the three PYTHIA tunes. "
         "The $N_{b+\\bar{b}}$ and $N_{c+\\bar{c}}$ rows denote the accepted final-hadron heavy-flavour valence content stored by the current production, not independent pre-hadronization parton counters.}\n";
  tex << "\\label{tab:generated-heavy-flavour-summary}\n";
  tex << "\\begin{tabular}{lrrrr}\n";
  tex << "\\toprule\n";
  tex << "Quantity";
  for (const TuneSummary& tune : tuneSummaries) {
    tex << " & " << tune.label;
  }
  tex << " & Overall \\\\\n";
  tex << "\\midrule\n";

  auto writeRow = [&](const std::string& label,
                      Long64_t monash,
                      Long64_t junctions,
                      Long64_t closepacking,
                      Long64_t total) {
    tex << label
        << " & " << LatexInteger(monash)
        << " & " << LatexInteger(junctions)
        << " & " << LatexInteger(closepacking)
        << " & " << LatexInteger(total)
        << " \\\\\n";
  };

  writeRow("Events",
           tuneSummaries.at(0).totalEvents,
           tuneSummaries.at(1).totalEvents,
           tuneSummaries.at(2).totalEvents,
           overall.totalEvents);
  writeRow("$N_{b+\\bar{b}}$",
           tuneSummaries.at(0).totalBeautyContent,
           tuneSummaries.at(1).totalBeautyContent,
           tuneSummaries.at(2).totalBeautyContent,
           overall.totalBeautyContent);
  writeRow("$N_{c+\\bar{c}}$",
           tuneSummaries.at(0).totalCharmContent,
           tuneSummaries.at(1).totalCharmContent,
           tuneSummaries.at(2).totalCharmContent,
           overall.totalCharmContent);

  tex << "\\midrule\n";
  for (size_t i = 0; i < overall.species.size(); ++i) {
    writeRow(LatexSpeciesName(overall.species[i].name),
             tuneSummaries.at(0).species.at(i).rawYield,
             tuneSummaries.at(1).species.at(i).rawYield,
             tuneSummaries.at(2).species.at(i).rawYield,
             overall.species.at(i).rawYield);
  }

  tex << "\\bottomrule\n";
  tex << "\\end{tabular}\n";
  tex << "\\end{table}\n";
}

bool FillFromProducerHistograms(const std::vector<std::string>& files,
                                const std::string& treeName,
                                std::vector<Species>& species,
                                Long64_t& totalEvents,
                                Long64_t& totalBeautyContent,
                                Long64_t& totalCharmContent,
                                Long64_t& treeEntriesCrossCheck,
                                std::string& failureReason)
{
  std::vector<Species> localSpecies = species;
  for (Species& row : localSpecies) row.rawYield = 0;

  Long64_t localEvents = 0;
  Long64_t localBeautyContent = 0;
  Long64_t localCharmContent = 0;
  Long64_t localTreeEntries = 0;

  for (const std::string& path : files) {
    TFile input(path.c_str(), "READ");
    if (input.IsZombie()) {
      failureReason = "could not open " + path;
      return false;
    }

    TH1* hMultiplicity = dynamic_cast<TH1*>(input.Get("hMULTIPLICITY"));
    TH1* hCharm = dynamic_cast<TH1*>(input.Get("hidCharm"));
    TH1* hBeauty = dynamic_cast<TH1*>(input.Get("hidBeauty"));
    TH1* hBc = dynamic_cast<TH1*>(input.Get("hidBc"));

    if (!hMultiplicity || !hCharm || !hBeauty || !hBc) {
      failureReason = "missing one of hMULTIPLICITY, hidCharm, hidBeauty, or hidBc in " + path;
      return false;
    }

    localEvents += HistogramEntries(hMultiplicity);
    localBeautyContent += HistogramIntegralAllBins(hBeauty) + HistogramIntegralAllBins(hBc);
    localCharmContent += HistogramIntegralAllBins(hCharm) + HistogramIntegralAllBins(hBc);

    TTree* tree = dynamic_cast<TTree*>(input.Get(treeName.c_str()));
    if (tree) localTreeEntries += tree->GetEntries();

    for (Species& row : localSpecies) {
      TH1* source = (row.flavor == 'b') ? hBeauty : hCharm;
      row.rawYield += HistogramPdgYield(source, row.pdg);
    }
  }

  species = localSpecies;
  totalEvents = localEvents;
  totalBeautyContent = localBeautyContent;
  totalCharmContent = localCharmContent;
  treeEntriesCrossCheck = localTreeEntries;
  return true;
}

} // namespace GeneratedHeavyFlavorSummaryDetail

void generated_heavy_flavor_summary(const char* inputPath = "RootFiles/HF",
                                    const char* outputCsv = "generated_heavy_flavor_summary.csv",
                                    const char* treeName = "tree",
                                    const char* statusSelection = "stored",
                                    const char* countBackend = "auto")
{
  using namespace GeneratedHeavyFlavorSummaryDetail;

  const std::string resolvedInput = ResolveFromBase(inputPath ? inputPath : "");
  const std::string resolvedOutput = ResolveFromBase(outputCsv ? outputCsv : "generated_heavy_flavor_summary.csv");
  const std::string statusMode = statusSelection ? statusSelection : "stored";
  const std::string backendMode = countBackend ? countBackend : "auto";
  const std::string treeNameValue = treeName && treeName[0] != '\0' ? treeName : "tree";

  std::vector<std::string> files;
  CollectRootFiles(resolvedInput, files);
  std::sort(files.begin(), files.end());

  if (files.empty()) {
    throw std::runtime_error("No ROOT files found under input path: " + resolvedInput);
  }

  std::vector<Species> species = DefaultSpecies();

  std::map<int, size_t> speciesByPdg;
  for (size_t i = 0; i < species.size(); ++i) {
    speciesByPdg[species[i].pdg] = i;
  }

  Long64_t totalEvents = 0;
  Long64_t totalBeautyContent = 0;
  Long64_t totalCharmContent = 0;
  Long64_t totalBeautyBranch = 0;
  Long64_t totalCharmBranch = 0;
  Long64_t totalBcBranch = 0;
  Long64_t skippedEntriesWithMissingIds = 0;
  Long64_t treeEntriesCrossCheck = 0;
  bool hasStatus = false;
  bool haveAllBranchCounters = false;
  std::string backendUsed = "tree";

  if (backendMode != "auto" && backendMode != "tree" && backendMode != "histograms") {
    throw std::runtime_error("Unknown countBackend '" + backendMode +
                             "'. Use 'auto', 'tree', or 'histograms'.");
  }

  const bool canTryHistograms = (statusMode == "stored") &&
                               (backendMode == "auto" || backendMode == "histograms");
  bool usedHistograms = false;

  if (canTryHistograms) {
    std::string histogramFailure;
    usedHistograms = FillFromProducerHistograms(files,
                                                treeNameValue,
                                                species,
                                                totalEvents,
                                                totalBeautyContent,
                                                totalCharmContent,
                                                treeEntriesCrossCheck,
                                                histogramFailure);
    if (usedHistograms) {
      backendUsed = "producer histograms";
    } else if (backendMode == "histograms") {
      throw std::runtime_error("Requested histogram backend but could not use it: " + histogramFailure);
    } else {
      std::cout << "WARNING: producer-histogram backend unavailable (" << histogramFailure
                << "); falling back to tree scan.\n";
    }
  }

  if (!usedHistograms) {
    if (backendMode == "histograms" && statusMode != "stored") {
      throw std::runtime_error("Histogram backend only supports statusSelection=\"stored\".");
    }

    TChain chain(treeNameValue.c_str());
    for (const std::string& file : files) {
      chain.Add(file.c_str());
    }

    if (!chain.GetBranch("ID")) {
      throw std::runtime_error("Required branch ID is missing from input tree.");
    }

    std::vector<Int_t>* ids = nullptr;
    std::vector<Double_t>* status = nullptr;
    Int_t nCharmBranch = 0;
    Int_t nBeautyBranch = 0;
    Int_t nBcBranch = 0;

    chain.SetBranchAddress("ID", &ids);

    hasStatus = chain.GetBranch("STATUS") != nullptr;
    if (hasStatus) chain.SetBranchAddress("STATUS", &status);

    const bool hasNCharm = chain.GetBranch("NCHARM") != nullptr;
    const bool hasNBeauty = chain.GetBranch("NBEAUTY") != nullptr;
    const bool hasNBc = chain.GetBranch("NBC") != nullptr;
    haveAllBranchCounters = hasNBeauty && hasNCharm && hasNBc;
    if (hasNCharm) chain.SetBranchAddress("NCHARM", &nCharmBranch);
    if (hasNBeauty) chain.SetBranchAddress("NBEAUTY", &nBeautyBranch);
    if (hasNBc) chain.SetBranchAddress("NBC", &nBcBranch);

    const Long64_t nEntries = chain.GetEntries();
    for (Long64_t iEntry = 0; iEntry < nEntries; ++iEntry) {
      chain.GetEntry(iEntry);
      ++totalEvents;

      if (hasNBeauty) totalBeautyBranch += nBeautyBranch;
      if (hasNCharm) totalCharmBranch += nCharmBranch;
      if (hasNBc) totalBcBranch += nBcBranch;

      if (!ids) {
        ++skippedEntriesWithMissingIds;
        continue;
      }

      for (size_t i = 0; i < ids->size(); ++i) {
        if (!PassStatus(static_cast<Long64_t>(i), hasStatus ? status : nullptr, statusMode)) continue;

        const int pdg = ids->at(i);

        auto found = speciesByPdg.find(pdg);
        if (found != speciesByPdg.end()) {
          species[found->second].rawYield++;
        }

        if (HasBeauty(pdg)) totalBeautyContent++;
        if (HasCharm(pdg)) totalCharmContent++;
      }
    }
  }

  const Long64_t branchBeautyContent = totalBeautyBranch + totalBcBranch;
  const Long64_t branchCharmContent = totalCharmBranch + totalBcBranch;

  std::cout << "\nGenerated heavy-flavour summary\n";
  std::cout << "================================\n";
  std::cout << "Input path: " << resolvedInput << "\n";
  std::cout << "Input files: " << files.size() << "\n";
  std::cout << "Tree: " << treeNameValue << "\n";
  std::cout << "Status selection: " << statusMode << "\n";
  std::cout << "Counting backend: " << backendUsed << "\n";
  std::cout << "Total events processed: " << totalEvents << "\n";
  std::cout << "Stored b/bbar valence content used for normalization: " << totalBeautyContent << "\n";
  std::cout << "Stored c/cbar valence content used for normalization: " << totalCharmContent << "\n";
  if (usedHistograms && treeEntriesCrossCheck > 0) {
    std::cout << "Tree-entry cross-check: " << treeEntriesCrossCheck << "\n";
  }
  if (haveAllBranchCounters) {
    std::cout << "Branch cross-check NBEAUTY + NBC: " << branchBeautyContent << "\n";
    std::cout << "Branch cross-check NCHARM + NBC: " << branchCharmContent << "\n";
  }
  if (skippedEntriesWithMissingIds > 0) {
    std::cout << "WARNING: entries with missing ID vector: " << skippedEntriesWithMissingIds << "\n";
  }
  if (statusMode == "positive" && !hasStatus) {
    std::cout << "WARNING: STATUS branch missing; positive status selection fell back to stored particles.\n";
  }
  if (usedHistograms && treeEntriesCrossCheck > 0 && treeEntriesCrossCheck != totalEvents) {
    std::cout << "WARNING: hMULTIPLICITY event count differs from tree entries.\n";
  }
  if (haveAllBranchCounters &&
      (branchBeautyContent != totalBeautyContent || branchCharmContent != totalCharmContent) &&
      statusMode == "stored") {
    std::cout << "WARNING: branch heavy-flavour counters differ from ID-derived valence content.\n";
  }
  std::cout << "NOTE: these denominators are accepted final-hadron heavy-flavour content, not true pre-hadronization quark counts.\n\n";

  std::cout << std::left
            << std::setw(20) << "particle"
            << std::right
            << std::setw(10) << "PDG ID"
            << std::setw(18) << "raw yield"
            << std::setw(20) << "yield/event"
            << std::setw(24) << "yield/heavy content"
            << "\n";
  std::cout << std::string(92, '-') << "\n";

  for (const Species& row : species) {
    const Long64_t denominator = (row.flavor == 'b') ? totalBeautyContent : totalCharmContent;
    const double perEvent = SafeDivide(row.rawYield, totalEvents);
    const double perHeavy = SafeDivide(row.rawYield, denominator);

    std::cout << std::left
              << std::setw(20) << row.name
              << std::right
              << std::setw(10) << row.pdg
              << std::setw(18) << row.rawYield
              << std::setw(20) << FormatRate(perEvent)
              << std::setw(24) << FormatRate(perHeavy)
              << "\n";
  }
  std::cout << "\n";

  EnsureParentDirectory(resolvedOutput);
  std::ofstream csv(resolvedOutput);
  if (!csv) {
    throw std::runtime_error("Could not open CSV output for writing: " + resolvedOutput);
  }

  csv << "particle_name,pdg_id,heavy_flavor,raw_yield,yield_per_event,"
      << "normalization_count,yield_per_heavy_flavor_content,total_events,"
      << "total_b_or_bbar_content,total_c_or_cbar_content,input_files,status_selection,counting_backend,"
      << "normalization_note\n";

  const std::string normalizationNote =
    "accepted final-hadron heavy-flavour valence content; current tree does not store true pre-hadronization b/c quark counts";

  for (const Species& row : species) {
    const Long64_t denominator = (row.flavor == 'b') ? totalBeautyContent : totalCharmContent;
    const double perEvent = SafeDivide(row.rawYield, totalEvents);
    const double perHeavy = SafeDivide(row.rawYield, denominator);

    csv << CsvEscape(row.name) << ','
        << row.pdg << ','
        << row.flavor << ','
        << row.rawYield << ','
        << FormatRate(perEvent) << ','
        << denominator << ','
        << FormatRate(perHeavy) << ','
        << totalEvents << ','
        << totalBeautyContent << ','
        << totalCharmContent << ','
        << files.size() << ','
        << CsvEscape(statusMode) << ','
        << CsvEscape(backendUsed) << ','
        << CsvEscape(normalizationNote) << '\n';
  }

  csv.close();
  std::cout << "CSV written to: " << resolvedOutput << "\n";
}

void generated_heavy_flavor_summary_latex_table(const char* inputBaseDir = "RootFiles/HF",
                                                const char* outputTex = "Paper/Tables/generated_heavy_flavor_summary.tex",
                                                const char* treeName = "tree")
{
  using namespace GeneratedHeavyFlavorSummaryDetail;

  const std::string resolvedInputBase = ResolveFromBase(inputBaseDir ? inputBaseDir : "RootFiles/HF");
  const std::string resolvedOutput = ResolveFromBase(outputTex ? outputTex : "generated_heavy_flavor_summary.tex");
  const std::string treeNameValue = treeName && treeName[0] != '\0' ? treeName : "tree";

  const std::vector<std::string> tuneNames = {"MONASH", "JUNCTIONS", "CLOSEPACKING"};
  std::vector<TuneSummary> tuneSummaries;
  tuneSummaries.reserve(tuneNames.size());

  TuneSummary overall;
  overall.label = "Overall";
  overall.species = DefaultSpecies();

  std::cout << "\nGenerated heavy-flavour LaTeX table summary\n";
  std::cout << "===========================================\n";
  std::cout << "Input base: " << resolvedInputBase << "\n";
  std::cout << "Tree: " << treeNameValue << "\n";
  std::cout << "Counting backend: producer histograms\n\n";

  for (const std::string& tuneName : tuneNames) {
    const std::string tuneDir = resolvedInputBase + "/" + tuneName;
    TuneSummary summary = SummarizeTuneFromProducerHistograms(tuneName, tuneDir, treeNameValue);

    std::cout << std::left << std::setw(14) << tuneName
              << " files=" << std::setw(4) << summary.inputFiles
              << " events=" << summary.totalEvents
              << " b+bbar content=" << summary.totalBeautyContent
              << " c+cbar content=" << summary.totalCharmContent;
    if (summary.treeEntriesCrossCheck > 0) {
      std::cout << " tree entries=" << summary.treeEntriesCrossCheck;
    }
    std::cout << "\n";

    AddTuneSummary(overall, summary);
    tuneSummaries.push_back(summary);
  }

  std::cout << std::left << std::setw(14) << "Overall"
            << " files=" << std::setw(4) << overall.inputFiles
            << " events=" << overall.totalEvents
            << " b+bbar content=" << overall.totalBeautyContent
            << " c+cbar content=" << overall.totalCharmContent;
  if (overall.treeEntriesCrossCheck > 0) {
    std::cout << " tree entries=" << overall.treeEntriesCrossCheck;
  }
  std::cout << "\n\n";

  WriteLatexSummaryTable(tuneSummaries, overall, resolvedOutput);
  std::cout << "LaTeX table written to: " << resolvedOutput << "\n";
  std::cout << "NOTE: b+bbar and c+cbar are accepted final-hadron valence-content counts from the current production, not true pre-hadronization parton counters.\n";
}
