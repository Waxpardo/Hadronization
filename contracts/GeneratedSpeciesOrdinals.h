// GENERATED FILE -- DO NOT EDIT.
//
// Regenerate with:
//   python3 tools/generate_species_ordinals_header.py
//
// Source of truth: contracts/species_ordinals_v2.json,
// itself derived from a raw file's heavy_stability_audit tree by
// tools/GenerateSpeciesOrdinals.C. The axis's index space comes from
// PYTHIA's own recorded state, never from a hand-written list.
//
// FAIL-CLOSED (F6). This table is the COMPLETE admissible set. Any
// sector-charged PDG absent from it must FAIL the run. There is
// deliberately no overflow bin: an overflow bin is how 152 species
// became invisible in the first place.
#ifndef HADRONIZATION_GENERATED_SPECIES_ORDINALS_H
#define HADRONIZATION_GENERATED_SPECIES_ORDINALS_H

#include <array>
#include <cstddef>

namespace Hadronization {

inline constexpr const char* kSpeciesOrdinalSchema =
    "hf_species_ordinal_table_v2";
// FNV-1a over the canonical ordinal:pdg serialisation. Identifies the
// AXIS, so it is unchanged by adding annotation columns.
inline constexpr const char* kSpeciesOrdinalDigest =
    "646f310f78126267";
inline constexpr int kSpeciesOrdinalCount = 202;

// Category as the PRODUCER's own ClassifyHeavyStateDetailed assigns
// it, computed from heavy_stability_audit's recorded columns rather
// than from the runtime particle record. Summing the species axis by
// this column must reproduce the 6-category axis bin for bin; the two
// labelings share their rules but not their inputs, which is what
// makes that check mean something.
struct SpeciesOrdinalRow {
  int pdg;
  int category;
};

// Indexed BY ORDINAL, in ascending signed PDG order.
inline constexpr std::array<SpeciesOrdinalRow, 202>
    kSpeciesOrdinals = {{
    {-20543, 4},  // 0 kExcludedVector
    {-20533, 4},  // 1 kExcludedVector
    {-20523, 4},  // 2 kExcludedVector
    {-20513, 4},  // 3 kExcludedVector
    {-20433, 4},  // 4 kExcludedVector
    {-20423, 4},  // 5 kExcludedVector
    {-20413, 4},  // 6 kExcludedVector
    {-14122, 5},  // 7 kExcludedExcited
    {-10543, 4},  // 8 kExcludedVector
    {-10541, 5},  // 9 kExcludedExcited
    {-10533, 4},  // 10 kExcludedVector
    {-10531, 5},  // 11 kExcludedExcited
    {-10523, 4},  // 12 kExcludedVector
    {-10521, 5},  // 13 kExcludedExcited
    {-10513, 4},  // 14 kExcludedVector
    {-10511, 5},  // 15 kExcludedExcited
    {-10433, 4},  // 16 kExcludedVector
    {-10431, 5},  // 17 kExcludedExcited
    {-10423, 4},  // 18 kExcludedVector
    {-10421, 5},  // 19 kExcludedExcited
    {-10413, 4},  // 20 kExcludedVector
    {-10411, 5},  // 21 kExcludedExcited
    {-5554, 2},  // 22 kMultiplyHeavy
    {-5544, 2},  // 23 kMultiplyHeavy
    {-5542, 2},  // 24 kMultiplyHeavy
    {-5534, 2},  // 25 kMultiplyHeavy
    {-5532, 2},  // 26 kMultiplyHeavy
    {-5524, 2},  // 27 kMultiplyHeavy
    {-5522, 2},  // 28 kMultiplyHeavy
    {-5514, 2},  // 29 kMultiplyHeavy
    {-5512, 2},  // 30 kMultiplyHeavy
    {-5444, 2},  // 31 kMultiplyHeavy
    {-5442, 2},  // 32 kMultiplyHeavy
    {-5434, 5},  // 33 kExcludedExcited
    {-5432, 5},  // 34 kExcludedExcited
    {-5424, 5},  // 35 kExcludedExcited
    {-5422, 5},  // 36 kExcludedExcited
    {-5414, 5},  // 37 kExcludedExcited
    {-5412, 5},  // 38 kExcludedExcited
    {-5342, 5},  // 39 kExcludedExcited
    {-5334, 5},  // 40 kExcludedExcited
    {-5332, 0},  // 41 kCentralGround
    {-5324, 5},  // 42 kExcludedExcited
    {-5322, 0},  // 43 kCentralGround
    {-5314, 5},  // 44 kExcludedExcited
    {-5312, 0},  // 45 kCentralGround
    {-5242, 5},  // 46 kExcludedExcited
    {-5232, 0},  // 47 kCentralGround
    {-5224, 5},  // 48 kExcludedExcited
    {-5222, 0},  // 49 kCentralGround
    {-5214, 5},  // 50 kExcludedExcited
    {-5212, 0},  // 51 kCentralGround
    {-5142, 5},  // 52 kExcludedExcited
    {-5132, 0},  // 53 kCentralGround
    {-5122, 0},  // 54 kCentralGround
    {-5114, 5},  // 55 kExcludedExcited
    {-5112, 0},  // 56 kCentralGround
    {-4444, 2},  // 57 kMultiplyHeavy
    {-4434, 2},  // 58 kMultiplyHeavy
    {-4432, 2},  // 59 kMultiplyHeavy
    {-4424, 2},  // 60 kMultiplyHeavy
    {-4422, 2},  // 61 kMultiplyHeavy
    {-4414, 2},  // 62 kMultiplyHeavy
    {-4412, 2},  // 63 kMultiplyHeavy
    {-4334, 5},  // 64 kExcludedExcited
    {-4332, 0},  // 65 kCentralGround
    {-4324, 5},  // 66 kExcludedExcited
    {-4322, 0},  // 67 kCentralGround
    {-4314, 5},  // 68 kExcludedExcited
    {-4312, 0},  // 69 kCentralGround
    {-4232, 0},  // 70 kCentralGround
    {-4224, 5},  // 71 kExcludedExcited
    {-4222, 0},  // 72 kCentralGround
    {-4214, 5},  // 73 kExcludedExcited
    {-4212, 0},  // 74 kCentralGround
    {-4132, 0},  // 75 kCentralGround
    {-4124, 5},  // 76 kExcludedExcited
    {-4122, 0},  // 77 kCentralGround
    {-4114, 5},  // 78 kExcludedExcited
    {-4112, 0},  // 79 kCentralGround
    {-545, 5},  // 80 kExcludedExcited
    {-543, 4},  // 81 kExcludedVector
    {-541, 0},  // 82 kCentralGround
    {-535, 5},  // 83 kExcludedExcited
    {-533, 4},  // 84 kExcludedVector
    {-531, 0},  // 85 kCentralGround
    {-525, 5},  // 86 kExcludedExcited
    {-523, 4},  // 87 kExcludedVector
    {-521, 0},  // 88 kCentralGround
    {-515, 5},  // 89 kExcludedExcited
    {-513, 4},  // 90 kExcludedVector
    {-511, 0},  // 91 kCentralGround
    {-435, 5},  // 92 kExcludedExcited
    {-433, 4},  // 93 kExcludedVector
    {-431, 0},  // 94 kCentralGround
    {-425, 5},  // 95 kExcludedExcited
    {-423, 4},  // 96 kExcludedVector
    {-421, 0},  // 97 kCentralGround
    {-415, 5},  // 98 kExcludedExcited
    {-413, 4},  // 99 kExcludedVector
    {-411, 0},  // 100 kCentralGround
    {411, 0},  // 101 kCentralGround
    {413, 4},  // 102 kExcludedVector
    {415, 5},  // 103 kExcludedExcited
    {421, 0},  // 104 kCentralGround
    {423, 4},  // 105 kExcludedVector
    {425, 5},  // 106 kExcludedExcited
    {431, 0},  // 107 kCentralGround
    {433, 4},  // 108 kExcludedVector
    {435, 5},  // 109 kExcludedExcited
    {511, 0},  // 110 kCentralGround
    {513, 4},  // 111 kExcludedVector
    {515, 5},  // 112 kExcludedExcited
    {521, 0},  // 113 kCentralGround
    {523, 4},  // 114 kExcludedVector
    {525, 5},  // 115 kExcludedExcited
    {531, 0},  // 116 kCentralGround
    {533, 4},  // 117 kExcludedVector
    {535, 5},  // 118 kExcludedExcited
    {541, 0},  // 119 kCentralGround
    {543, 4},  // 120 kExcludedVector
    {545, 5},  // 121 kExcludedExcited
    {4112, 0},  // 122 kCentralGround
    {4114, 5},  // 123 kExcludedExcited
    {4122, 0},  // 124 kCentralGround
    {4124, 5},  // 125 kExcludedExcited
    {4132, 0},  // 126 kCentralGround
    {4212, 0},  // 127 kCentralGround
    {4214, 5},  // 128 kExcludedExcited
    {4222, 0},  // 129 kCentralGround
    {4224, 5},  // 130 kExcludedExcited
    {4232, 0},  // 131 kCentralGround
    {4312, 0},  // 132 kCentralGround
    {4314, 5},  // 133 kExcludedExcited
    {4322, 0},  // 134 kCentralGround
    {4324, 5},  // 135 kExcludedExcited
    {4332, 0},  // 136 kCentralGround
    {4334, 5},  // 137 kExcludedExcited
    {4412, 2},  // 138 kMultiplyHeavy
    {4414, 2},  // 139 kMultiplyHeavy
    {4422, 2},  // 140 kMultiplyHeavy
    {4424, 2},  // 141 kMultiplyHeavy
    {4432, 2},  // 142 kMultiplyHeavy
    {4434, 2},  // 143 kMultiplyHeavy
    {4444, 2},  // 144 kMultiplyHeavy
    {5112, 0},  // 145 kCentralGround
    {5114, 5},  // 146 kExcludedExcited
    {5122, 0},  // 147 kCentralGround
    {5132, 0},  // 148 kCentralGround
    {5142, 5},  // 149 kExcludedExcited
    {5212, 0},  // 150 kCentralGround
    {5214, 5},  // 151 kExcludedExcited
    {5222, 0},  // 152 kCentralGround
    {5224, 5},  // 153 kExcludedExcited
    {5232, 0},  // 154 kCentralGround
    {5242, 5},  // 155 kExcludedExcited
    {5312, 0},  // 156 kCentralGround
    {5314, 5},  // 157 kExcludedExcited
    {5322, 0},  // 158 kCentralGround
    {5324, 5},  // 159 kExcludedExcited
    {5332, 0},  // 160 kCentralGround
    {5334, 5},  // 161 kExcludedExcited
    {5342, 5},  // 162 kExcludedExcited
    {5412, 5},  // 163 kExcludedExcited
    {5414, 5},  // 164 kExcludedExcited
    {5422, 5},  // 165 kExcludedExcited
    {5424, 5},  // 166 kExcludedExcited
    {5432, 5},  // 167 kExcludedExcited
    {5434, 5},  // 168 kExcludedExcited
    {5442, 2},  // 169 kMultiplyHeavy
    {5444, 2},  // 170 kMultiplyHeavy
    {5512, 2},  // 171 kMultiplyHeavy
    {5514, 2},  // 172 kMultiplyHeavy
    {5522, 2},  // 173 kMultiplyHeavy
    {5524, 2},  // 174 kMultiplyHeavy
    {5532, 2},  // 175 kMultiplyHeavy
    {5534, 2},  // 176 kMultiplyHeavy
    {5542, 2},  // 177 kMultiplyHeavy
    {5544, 2},  // 178 kMultiplyHeavy
    {5554, 2},  // 179 kMultiplyHeavy
    {10411, 5},  // 180 kExcludedExcited
    {10413, 4},  // 181 kExcludedVector
    {10421, 5},  // 182 kExcludedExcited
    {10423, 4},  // 183 kExcludedVector
    {10431, 5},  // 184 kExcludedExcited
    {10433, 4},  // 185 kExcludedVector
    {10511, 5},  // 186 kExcludedExcited
    {10513, 4},  // 187 kExcludedVector
    {10521, 5},  // 188 kExcludedExcited
    {10523, 4},  // 189 kExcludedVector
    {10531, 5},  // 190 kExcludedExcited
    {10533, 4},  // 191 kExcludedVector
    {10541, 5},  // 192 kExcludedExcited
    {10543, 4},  // 193 kExcludedVector
    {14122, 5},  // 194 kExcludedExcited
    {20413, 4},  // 195 kExcludedVector
    {20423, 4},  // 196 kExcludedVector
    {20433, 4},  // 197 kExcludedVector
    {20513, 4},  // 198 kExcludedVector
    {20523, 4},  // 199 kExcludedVector
    {20533, 4},  // 200 kExcludedVector
    {20543, 4},  // 201 kExcludedVector
}};

// Fail-closed lookup. Returns false for any PDG absent from the
// table; callers must abort rather than substitute a bin.
inline bool SpeciesOrdinalFor(int pdg, int& ordinal) {
  std::size_t low = 0;
  std::size_t high = kSpeciesOrdinals.size();
  while (low < high) {
    const std::size_t middle = low + (high - low) / 2;
    const int candidate = kSpeciesOrdinals[middle].pdg;
    if (candidate == pdg) {
      ordinal = static_cast<int>(middle);
      return true;
    }
    if (candidate < pdg) {
      low = middle + 1;
    } else {
      high = middle;
    }
  }
  return false;
}

// The producer category for an ordinal, for the summation check.
inline int SpeciesCategoryForOrdinal(int ordinal) {
  if (ordinal < 0 || ordinal >= kSpeciesOrdinalCount) return -1;
  return kSpeciesOrdinals[static_cast<std::size_t>(ordinal)].category;
}

// F5 LEGIBILITY. Written into every output file so the axis can be
// decoded without this repository.
inline constexpr const char* kSpeciesOrdinalLabels =
    "{\"0\":-20543,\"1\":-20533,\"2\":-20523,\"3\":-20513,\"4\":-20433,"
    "\"5\":-20423,\"6\":-20413,\"7\":-14122,\"8\":-10543,\"9\":-10541,"
    "\"10\":-10533,\"11\":-10531,\"12\":-10523,\"13\":-10521,\"14\":-10513,"
    "\"15\":-10511,\"16\":-10433,\"17\":-10431,\"18\":-10423,\"19\":-10421,"
    "\"20\":-10413,\"21\":-10411,\"22\":-5554,\"23\":-5544,\"24\":-5542,"
    "\"25\":-5534,\"26\":-5532,\"27\":-5524,\"28\":-5522,\"29\":-5514,\"30\":-5512,"
    "\"31\":-5444,\"32\":-5442,\"33\":-5434,\"34\":-5432,\"35\":-5424,\"36\":-5422,"
    "\"37\":-5414,\"38\":-5412,\"39\":-5342,\"40\":-5334,\"41\":-5332,\"42\":-5324,"
    "\"43\":-5322,\"44\":-5314,\"45\":-5312,\"46\":-5242,\"47\":-5232,\"48\":-5224,"
    "\"49\":-5222,\"50\":-5214,\"51\":-5212,\"52\":-5142,\"53\":-5132,\"54\":-5122,"
    "\"55\":-5114,\"56\":-5112,\"57\":-4444,\"58\":-4434,\"59\":-4432,\"60\":-4424,"
    "\"61\":-4422,\"62\":-4414,\"63\":-4412,\"64\":-4334,\"65\":-4332,\"66\":-4324,"
    "\"67\":-4322,\"68\":-4314,\"69\":-4312,\"70\":-4232,\"71\":-4224,\"72\":-4222,"
    "\"73\":-4214,\"74\":-4212,\"75\":-4132,\"76\":-4124,\"77\":-4122,\"78\":-4114,"
    "\"79\":-4112,\"80\":-545,\"81\":-543,\"82\":-541,\"83\":-535,\"84\":-533,"
    "\"85\":-531,\"86\":-525,\"87\":-523,\"88\":-521,\"89\":-515,\"90\":-513,"
    "\"91\":-511,\"92\":-435,\"93\":-433,\"94\":-431,\"95\":-425,\"96\":-423,"
    "\"97\":-421,\"98\":-415,\"99\":-413,\"100\":-411,\"101\":411,\"102\":413,"
    "\"103\":415,\"104\":421,\"105\":423,\"106\":425,\"107\":431,\"108\":433,"
    "\"109\":435,\"110\":511,\"111\":513,\"112\":515,\"113\":521,\"114\":523,"
    "\"115\":525,\"116\":531,\"117\":533,\"118\":535,\"119\":541,\"120\":543,"
    "\"121\":545,\"122\":4112,\"123\":4114,\"124\":4122,\"125\":4124,\"126\":4132,"
    "\"127\":4212,\"128\":4214,\"129\":4222,\"130\":4224,\"131\":4232,\"132\":4312,"
    "\"133\":4314,\"134\":4322,\"135\":4324,\"136\":4332,\"137\":4334,\"138\":4412,"
    "\"139\":4414,\"140\":4422,\"141\":4424,\"142\":4432,\"143\":4434,\"144\":4444,"
    "\"145\":5112,\"146\":5114,\"147\":5122,\"148\":5132,\"149\":5142,\"150\":5212,"
    "\"151\":5214,\"152\":5222,\"153\":5224,\"154\":5232,\"155\":5242,\"156\":5312,"
    "\"157\":5314,\"158\":5322,\"159\":5324,\"160\":5332,\"161\":5334,\"162\":5342,"
    "\"163\":5412,\"164\":5414,\"165\":5422,\"166\":5424,\"167\":5432,\"168\":5434,"
    "\"169\":5442,\"170\":5444,\"171\":5512,\"172\":5514,\"173\":5522,\"174\":5524,"
    "\"175\":5532,\"176\":5534,\"177\":5542,\"178\":5544,\"179\":5554,"
    "\"180\":10411,\"181\":10413,\"182\":10421,\"183\":10423,\"184\":10431,"
    "\"185\":10433,\"186\":10511,\"187\":10513,\"188\":10521,\"189\":10523,"
    "\"190\":10531,\"191\":10533,\"192\":10541,\"193\":10543,\"194\":14122,"
    "\"195\":20413,\"196\":20423,\"197\":20433,\"198\":20513,\"199\":20523,"
    "\"200\":20533,\"201\":20543}";

}  // namespace Hadronization

#endif  // HADRONIZATION_GENERATED_SPECIES_ORDINALS_H
