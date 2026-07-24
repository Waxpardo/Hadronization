#ifndef HADRONIZATION_SEED_UTILS_H
#define HADRONIZATION_SEED_UTILS_H

#include <cstdint>
#include <stdexcept>
#include <string>

inline std::uint64_t ParseUnsignedSeedInput(const char* value, const char* name) {
  std::size_t pos = 0;
  const std::string text(value ? value : "");
  const std::uint64_t parsed = std::stoull(text, &pos);
  if (pos != text.size()) {
    throw std::invalid_argument(std::string(name) + " contains non-numeric characters");
  }
  return parsed;
}

inline std::uint64_t SplitMix64(std::uint64_t x) {
  x += 0x9e3779b97f4a7c15ULL;
  x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL;
  x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL;
  return x ^ (x >> 31);
}

inline int DeterministicPythiaSeed(std::uint64_t seedInput1,
                                   std::uint64_t seedInput2) {
  std::uint64_t mixed = seedInput1;
  mixed ^= seedInput2 + 0x9e3779b97f4a7c15ULL + (mixed << 6) + (mixed >> 2);
  mixed = SplitMix64(mixed);

  // PYTHIA accepts integer seeds in [1, 900000000].
  return 1 + static_cast<int>(mixed % 900000000ULL);
}

#endif
