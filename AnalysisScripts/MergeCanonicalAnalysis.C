#include "GeneratedPairRegistry.h"
#include "MergeAnalysisObjects.C"

#include <TSystem.h>

#include <cstdio>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

int MergeCanonicalAnalysis(const char* slotListPath, const char* perJobRoot,
                           const char* tune, const char* outputDirectory,
                           const char* manifestSha256) {
  std::ifstream slotStream(slotListPath);
  std::vector<int> slots;
  int slot = -1;
  while (slotStream >> slot) slots.push_back(slot);
  if (slots.empty()) {
    std::cerr << "CANONICAL_MERGE_ERROR empty slot list\n";
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
      inputs << perJobRoot << "/" << tune << "/slot_" << std::setw(3)
             << std::setfill('0') << canonicalSlot << "/" << pair.filename
             << "\n";
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
