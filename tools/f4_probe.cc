// F4 -- the decay-parent probe, against the PINNED PYTHIA 8.317 install.
//
// STEP 1 IS A GATE, and the proposal says so: the map may only be derived after
// the stabilisation pass if decay channels REMAIN READABLE once
// `mayDecay(id,false)` has been applied. The producer disables decays for every
// heavy hadron (heavyflavourcorrelations_status.cpp:373), so if disabling also
// clears the channel tables, the map has to be derived BEFORE stabilisation
// instead. The proposal records both paths; this probe decides which one is
// live, by measurement rather than by reading the PYTHIA source.
//
// STEP 2, only if step 1 passes: for every sector-charged species in the
// ordinal table, the dominant decay channel and its branching fraction, taken
// from the generator's own tables. Never hand-written -- that is the whole
// point of F4 and the reason the proposal forbids a typed-in map.
//
// Emits machine-readable lines; the JSON artifact is assembled by the caller so
// that hashing and species-set validation happen in one place.
//
// Build (flags mirror generation/producer/Makefile:39-53):
//   g++ -O2 -std=c++17 -isystem $PYTHIA8/include f4_probe.cc \
//       -L$PYTHIA8/lib -lpythia8 -Wl,-rpath,$PYTHIA8/lib -o f4_probe

#include "Pythia8/Pythia.h"

#include <cstdio>
#include <fstream>
#include <string>
#include <vector>

int main(int argc, char** argv) {
  if (argc < 2) {
    std::fprintf(stderr, "usage: f4_probe PDG_LIST_FILE\n");
    return 2;
  }

  Pythia8::Pythia pythia("", false);
  // No event generation: only the particle database is needed. init() is not
  // called, so nothing about the beam configuration can influence the tables.
  Pythia8::ParticleData& pdt = pythia.particleData;

  std::printf("F4_PYTHIA_VERSION %.3f\n", PYTHIA_VERSION);

  std::vector<int> pdgs;
  {
    std::ifstream in(argv[1]);
    int id = 0;
    while (in >> id) pdgs.push_back(id);
  }
  std::printf("F4_SPECIES_REQUESTED n=%zu\n", pdgs.size());

  // ---- STEP 1: the readability gate ----------------------------------------
  // Probe on species that actually have channels, then disable and re-read.
  int probed = 0, survived = 0, hadChannels = 0;
  for (const int id : pdgs) {
    auto entry = pdt.particleDataEntryPtr(id);  // shared_ptr in 8.3x
    if (!entry) continue;
    const int before = entry->sizeChannels();
    if (before <= 0) continue;
    ++hadChannels;
    const bool originalMayDecay = entry->mayDecay();
    pdt.mayDecay(id, false);
    const int after = entry->sizeChannels();
    pdt.mayDecay(id, originalMayDecay);
    ++probed;
    if (after == before) ++survived;
    if (probed <= 5) {
      std::printf("F4_GATE_SAMPLE pdg=%d channels_before=%d channels_after=%d\n",
                  id, before, after);
    }
  }
  std::printf("F4_GATE with_channels=%d probed=%d survived=%d verdict=%s\n",
              hadChannels, probed, survived,
              (probed > 0 && survived == probed) ? "READABLE_AFTER_DISABLE"
                                                 : "NOT_READABLE");
  if (probed == 0 || survived != probed) {
    std::printf("F4_STOP the map must derive BEFORE the stabilisation pass\n");
    return 0;  // Not an error: a measured answer, and the other recorded path.
  }

  // ---- STEP 2: the dominant channel per species ------------------------------
  // Disabled exactly as production does, to prove the map is derivable in the
  // state the analysis actually runs in.
  for (const int id : pdgs) pdt.mayDecay(id, false);

  for (const int id : pdgs) {
    auto entry = pdt.particleDataEntryPtr(id);  // shared_ptr in 8.3x
    if (!entry) {
      std::printf("F4_SPECIES pdg=%d status=ABSENT_FROM_PARTICLE_DATA\n", id);
      continue;
    }
    const int nch = entry->sizeChannels();
    if (nch <= 0) {
      std::printf("F4_SPECIES pdg=%d name=%s channels=0 status=STABLE_OR_NO_TABLE\n",
                  id, entry->name(id).c_str());
      continue;
    }
    int bestIndex = -1;
    double bestBr = -1.0;
    for (int c = 0; c < nch; ++c) {
      const double br = entry->channel(c).bRatio();
      if (br > bestBr) { bestBr = br; bestIndex = c; }
    }
    std::string products;
    if (bestIndex >= 0) {
      const auto& ch = entry->channel(bestIndex);
      for (int k = 0; k < ch.multiplicity(); ++k) {
        if (k) products += ":";
        products += std::to_string(ch.product(k));
      }
    }
    std::printf("F4_SPECIES pdg=%d name=%s channels=%d dominant_br=%.10g "
                "dominant_products=%s status=OK\n",
                id, entry->name(id).c_str(), nch, bestBr,
                products.empty() ? "-" : products.c_str());
  }
  std::printf("F4_DONE\n");
  return 0;
}
