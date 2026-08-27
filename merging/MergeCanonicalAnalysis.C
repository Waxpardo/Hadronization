#include "../contracts/GeneratedPairRegistry.h"
#include "MergeAnalysisObjects.C"

#include <TSystem.h>

#include <cstdio>
#include <algorithm>
#include <cctype>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <set>
#include <string>
#include <vector>

int MergeCanonicalAnalysis(const char* slotListPath, const char* perJobRoot,
                           const char* tune, const char* outputDirectory,
                           const char* manifestSha256,
                           int expectedSlotCount) {
  std::ifstream slotStream(slotListPath);
  std::vector<int> slots;
  int slot = -1;
  while (slotStream >> slot) slots.push_back(slot);
  const std::set<std::string> allowedTunes = {
      "MONASH", "JUNCTIONS", "CLOSEPACKING"};
  const std::set<int> uniqueSlots(slots.begin(), slots.end());
  const std::string manifestSha(manifestSha256);
  const bool validManifestSha =
      manifestSha.size() == 64 &&
      std::all_of(
          manifestSha.begin(), manifestSha.end(), [](unsigned char character) {
            return std::isdigit(character) ||
                   (character >= 'a' && character <= 'f');
          });
  if (expectedSlotCount <= 0 ||
      static_cast<int>(slots.size()) != expectedSlotCount ||
      uniqueSlots.size() != slots.size() ||
      std::any_of(slots.begin(), slots.end(),
                  [](int value) { return value < 0; }) ||
      !allowedTunes.count(tune) || !validManifestSha) {
    std::cerr << "CANONICAL_MERGE_ERROR invalid slot/tune/manifest contract\n";
    return 1;
  }
  if (gSystem->mkdir(outputDirectory, true) != 0 &&
      gSystem->AccessPathName(outputDirectory)) {
    std::cerr << "CANONICAL_MERGE_ERROR cannot create output directory\n";
    return 2;
  }

  for (const auto& pair : Hadronization::kPairDefinitions) {
    std::ostringstream temporary;
    temporary << gSystem->TempDirectory() << "/hf_merge_" << gSystem->GetPid()
              << "_" << pair.triggerPdg << "_" << pair.associatePdg
              << ".txt";
    std::ofstream inputs(temporary.str());
    for (const int canonicalSlot : slots) {
      std::ostringstream inputPath;
      inputPath << perJobRoot << "/" << tune << "/slot_" << std::setw(3)
                << std::setfill('0') << canonicalSlot << "/"
                << pair.filename;
      if (gSystem->AccessPathName(inputPath.str().c_str())) {
        std::cerr << "CANONICAL_MERGE_ERROR missing manifest input "
                  << inputPath.str() << "\n";
        return 3;
      }
      inputs << inputPath.str() << "\n";
    }
    inputs.close();
    const std::string output =
        std::string(outputDirectory) + "/" + std::string(pair.filename);
    const int status = MergeAnalysisObjects(
        temporary.str().c_str(), output.c_str(), false, manifestSha256);
    gSystem->Unlink(temporary.str().c_str());
    if (status != 0) {
      std::cerr << "CANONICAL_MERGE_ERROR file=" << pair.filename
                << " status=" << status << "\n";
      return 3;
    }
  }
  std::cout << "CANONICAL_MERGE_SUMMARY tune=" << tune
            << " slots=" << slots.size()
            << " files=" << Hadronization::kPairDefinitions.size()
            << " output=" << outputDirectory << "\n";
  return 0;
}
