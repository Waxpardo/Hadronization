// Multiplicity-binned pair yields for the A2 pair-level unresolved systematic.
//
// Pre-registration: docs/A2_PAIR_UNRESOLVED_PREREGISTRATION.md
//
// WHAT IT EMITS. One CSV row per pair file per multiplicity class:
//
//     slot,pair_file,mclass,yield
//
// and nothing else. It deliberately does NOT know which files are OS and which
// are SS: that mapping lives in the signed pair registry
// (config/heavy_flavour_pair_registry_v1.json) and is applied on the Python
// side. Keeping the sign convention out of the ROOT layer means a mislabelled
// file cannot be silently absorbed into a difference here -- the join is
// explicit and fails closed if a filename is not in the registry.
//
// THE OBSERVABLE. hCorrelations axis 6 is
// multiplicity_primary_charged_eta10_v1 (see the production analysis macro,
// correlationValues[6]). The yield is the full-acceptance integral of that
// THnSparse restricted to the class's multiplicity range -- i.e. summed over
// dphi, deta, both etas and both pTs.
//
// Multiplicity classes are FIXED BY THE PRE-REGISTRATION and hard-coded here so
// they cannot drift between baseline and variation:
//     M1 1-9   M2 10-19   M3 20-29   M4 30-39   M5 >=40
//
// Usage:
//   root -l -b -q 'a2_pair_yield.C("SLOT_DIR", 0, "out.csv")'

#include "TFile.h"
#include "THnSparse.h"
#include "TSystemDirectory.h"
#include "TSystemFile.h"
#include "TList.h"
#include "TString.h"
#include <cstdio>

namespace {

// Lower edge (inclusive) of each class; the last class is open-ended.
const int kClassLow[5] = {1, 10, 20, 30, 40};
const int kClassHigh[5] = {9, 19, 29, 39, 1000000};

}  // namespace

void a2_pair_yield(const char* slotDir, int slot, const char* outCsv,
                   bool append = false) {
  TSystemDirectory dir("d", slotDir);
  TList* files = dir.GetListOfFiles();
  if (!files) {
    printf("A2_YIELD_ERROR no listing for %s\n", slotDir);
    return;
  }
  FILE* out = fopen(outCsv, append ? "a" : "w");
  if (!out) {
    printf("A2_YIELD_ERROR cannot open %s\n", outCsv);
    return;
  }
  if (!append) fprintf(out, "slot,pair_file,mclass,yield\n");

  long processed = 0;
  long missing = 0;
  TIter next(files);
  TSystemFile* entry = nullptr;
  while ((entry = static_cast<TSystemFile*>(next()))) {
    TString name = entry->GetName();
    if (entry->IsDirectory() || !name.EndsWith(".root")) continue;
    TFile* f = TFile::Open(TString::Format("%s/%s", slotDir, name.Data()));
    if (!f || f->IsZombie()) {
      printf("A2_YIELD_ERROR open %s\n", name.Data());
      ++missing;
      continue;
    }
    THnSparse* h = dynamic_cast<THnSparse*>(f->Get("hCorrelations"));
    if (!h) {
      // A pair file with no correlation object is a hard error, not a zero:
      // silently emitting 0 would enter the difference as a real deficit.
      printf("A2_YIELD_ERROR missing hCorrelations in %s\n", name.Data());
      ++missing;
      f->Close();
      continue;
    }
    const int multAxis = h->GetNdimensions() - 1;  // axis 6 of 7
    TAxis* axis = h->GetAxis(multAxis);
    double sums[5] = {0, 0, 0, 0, 0};
    // Walk the filled cells once. THnSparse is sparse: iterating cells is far
    // cheaper than projecting, and avoids building a temporary histogram per
    // class per file (300 files x 5 classes x 2 arms).
    const Long64_t filled = h->GetNbins();
    int coords[16];
    for (Long64_t cell = 0; cell < filled; ++cell) {
      const double content = h->GetBinContent(cell, coords);
      if (content == 0.0) continue;
      const double mult = axis->GetBinCenter(coords[multAxis]);
      const int m = static_cast<int>(mult + 0.5);
      for (int c = 0; c < 5; ++c) {
        if (m >= kClassLow[c] && m <= kClassHigh[c]) {
          sums[c] += content;
          break;
        }
      }
    }
    for (int c = 0; c < 5; ++c) {
      fprintf(out, "%d,%s,M%d,%.17g\n", slot, name.Data(), c + 1, sums[c]);
    }
    ++processed;
    f->Close();
  }
  fclose(out);
  printf("A2_YIELD_DONE slot=%d files=%ld missing=%ld\n", slot, processed,
         missing);
}
