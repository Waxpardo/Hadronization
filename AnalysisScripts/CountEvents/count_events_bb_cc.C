// count_events_bb_cc.C
//
// Count total number of events in all ROOT files for each tune & channel.
// Assumes each file has a TTree named "tree" with one entry per event.
//
// Usage from the Hadronization base:
//   root -l -b -q 'AnalysisScripts/CountEvents/count_events_bb_cc.C++'

#include <iostream>
#include <vector>
#include <string>
#include <fstream>

#include "TFile.h"
#include "TTree.h"
#include "TH1D.h"
#include "TSystemDirectory.h"
#include "TSystemFile.h"
#include "TList.h"
#include "TCollection.h"  // instead of TIter.h
#include "TString.h"
#include "TSystem.h"

// Resolve Hadronization base path.
TString GetBaseDir()
{
  const char* env = gSystem->Getenv("HADRONIZATION_BASE");
  if (env && env[0] != '\0') return TString(env);

  std::ifstream fin("base_path.txt");
  if (fin) {
    std::string line;
    std::getline(fin, line);
    if (!line.empty()) return TString(line.c_str());
  }

  return TString(".");
}


Long64_t CountEventsInDir(const char* inputDir)
{
  std::cout << ">>> Scanning directory: " << inputDir << std::endl;

  TSystemDirectory dir("inputDir", inputDir);
  TList* fileList = dir.GetListOfFiles();
  if (!fileList) {
    std::cerr << "WARNING: No file list for dir " << inputDir << std::endl;
    return 0;
  }

  fileList->Sort();  // deterministic order

  Long64_t totalEvents = 0;
  int nFiles = 0;

  TIter next(fileList);
  while (TSystemFile* f = (TSystemFile*)next()) {
    TString fname = f->GetName();
    if (f->IsDirectory()) continue;
    if (!fname.EndsWith(".root")) continue;

    TString fullPath = TString::Format("%s/%s", inputDir, fname.Data());

    TFile* fin = TFile::Open(fullPath, "READ");
    if (!fin || fin->IsZombie()) {
      std::cerr << "  [SKIP] Cannot open " << fullPath << std::endl;
      if (fin) fin->Close();
      continue;
    }

    TTree* tree = dynamic_cast<TTree*>(fin->Get("tree"));
    if (!tree) {
      std::cerr << "  [SKIP] TTree 'tree' not found in " << fullPath << std::endl;
      fin->Close();
      continue;
    }

    Long64_t nEntries = tree->GetEntries();
    totalEvents += nEntries;
    ++nFiles;

    std::cout << "  " << fullPath << " : " << nEntries << " events" << std::endl;

    fin->Close();
  }

  std::cout << ">>> Directory: " << inputDir
            << " | files: " << nFiles
            << " | TOTAL events: " << totalEvents << std::endl
            << std::endl;

  return totalEvents;
}

void count_events_bb_cc()
{
  TString base = GetBaseDir();
  Long64_t bbMonash    = CountEventsInDir((base + "/RootFiles/bbbar/MONASH").Data());
  Long64_t bbJunctions = CountEventsInDir((base + "/RootFiles/bbbar/JUNCTIONS").Data());
  Long64_t ccMonash    = CountEventsInDir((base + "/RootFiles/ccbar/MONASH").Data());
  Long64_t ccJunctions = CountEventsInDir((base + "/RootFiles/ccbar/JUNCTIONS").Data());

  std::cout << "================ SUMMARY ================" << std::endl;
  std::cout << "bbbar MONASH    total events: " << bbMonash    << std::endl;
  std::cout << "bbbar JUNCTIONS total events: " << bbJunctions << std::endl;
  std::cout << "ccbar MONASH    total events: " << ccMonash    << std::endl;
  std::cout << "ccbar JUNCTIONS total events: " << ccJunctions << std::endl;
  std::cout << "=========================================" << std::endl;
}
