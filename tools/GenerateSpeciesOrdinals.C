// Stage 1: derive the sector-charged species ordinal
// table from a produced raw file's heavy_stability_audit tree.
//
// WHY DERIVED, NOT HAND-WRITTEN. The F4 rule is that mapping tables
// come from PYTHIA's own state, never from a table someone typed. The same
// applies here: the ordinal table is the species axis's index space, and a
// hand-maintained list would drift from the generator the moment PYTHIA moved.
// heavy_stability_audit is written by the producer for every job and its hash
// is already carried into promoted provenance, so deriving from it makes the
// axis reproducible from data that is already sealed.
//
// WHAT "SECTOR-CHARGED" MEANS HERE. open_heavy == 1, i.e. q_c != 0 or q_b != 0.
// Hidden-heavy states (J/psi, Upsilon, chi) carry no net heavy flavour and
// cannot compensate, so they are not on the compensation axis. They are
// counted and reported separately rather than silently dropped.
//
// FAIL-CLOSED (F6). The emitted artifact is the complete admissible set. Any
// sector-charged PDG encountered at analysis time that is absent from it must
// FAIL the run. There is deliberately no overflow bin: an overflow bin is how
// 152 species became invisible in the first place, and reintroducing one under
// a friendlier name would repeat exactly that failure.

// THE CATEGORY COLUMN, and why it is derived through the producer's own header
// rather than reimplemented here. The species axis is validated by summing it
// by category and comparing, bin for bin, against the producer's 6-category
// axis. That check is only meaningful if the two labelings are produced
// independently -- but "independently" must mean independent INPUTS, not
// independently retyped RULES. Retyping the rules here would test whether two
// transcriptions agree, and would drift the first time the producer's
// classification changed. So the rules are shared, via
// ClassifyHeavyStateDetailed, and the independence lives where it belongs: the
// producer classifies from its runtime particle record at fill time, while this
// table classifies from heavy_stability_audit's recorded columns. A mismatch in
// the check therefore points at the ordinal mapping or the fill -- which is
// exactly what the check exists to catch.
#include "../generation/producer/HeavyFlavourUtils.h"

#include "TFile.h"
#include "TTree.h"

#include <algorithm>
#include <cstdio>
#include <cstdint>
#include <string>
#include <vector>

namespace {

struct SpeciesRow {
  int pdg = 0;
  int nCharm = 0;
  int nBeauty = 0;
  int qc = 0;
  int qb = 0;
  int isMeson = 0;
  int isBaryon = 0;
  int spinType = 0;
  int centralRegistry = 0;
  int category = 0;
};

// heavy_stability_audit records totals and net charges, not the four separate
// quark counts HeavyContent carries. They are recoverable exactly, because
// n_charm = nc + ncbar and q_c = nc - ncbar is a 2x2 system with integer
// solutions: nc = (n_charm + q_c)/2, ncbar = (n_charm - q_c)/2. Same for
// beauty. Strangeness is not needed -- no branch of ClassifyHeavyStateDetailed
// reads it.
Hadronization::HeavyContent ContentFromAudit(int nCharm, int nBeauty, int qc,
                                             int qb) {
  Hadronization::HeavyContent content;
  content.nc = (nCharm + qc) / 2;
  content.ncbar = (nCharm - qc) / 2;
  content.nb = (nBeauty + qb) / 2;
  content.nbbar = (nBeauty - qb) / 2;
  return content;
}

const char* CategoryName(int category) {
  switch (category) {
    case 0: return "kCentralGround";
    case 1: return "kHiddenHeavy";
    case 2: return "kMultiplyHeavy";
    case 3: return "kOtherNoncentral";
    case 4: return "kExcludedVector";
    case 5: return "kExcludedExcited";
    default: return "UNKNOWN";
  }
}

// FNV-1a over the canonical serialisation. Self-contained so the artifact can
// be re-derived and re-checked without linking a crypto library into a macro.
std::uint64_t Fnv1a(const std::string& text) {
  std::uint64_t hash = 1469598103934665603ULL;
  for (unsigned char c : text) {
    hash ^= static_cast<std::uint64_t>(c);
    hash *= 1099511628211ULL;
  }
  return hash;
}

}  // namespace

int GenerateSpeciesOrdinals(const char* rawPath,
                            const char* outputPath = "species_ordinals_v1.json") {
  TFile* in = TFile::Open(rawPath, "READ");
  if (!in || in->IsZombie()) {
    std::printf("ERROR: cannot open %s\n", rawPath);
    return 2;
  }
  TTree* tree = static_cast<TTree*>(in->Get("heavy_stability_audit"));
  if (!tree) {
    std::printf("ERROR: no heavy_stability_audit tree in %s\n", rawPath);
    return 3;
  }

  int pdg = 0, nCharm = 0, nBeauty = 0, qc = 0, qb = 0;
  int isMeson = 0, isBaryon = 0, spinType = 0;
  int openHeavy = 0, hiddenHeavy = 0, centralRegistry = 0, finalMayDecay = 0;
  tree->SetBranchAddress("pdg", &pdg);
  tree->SetBranchAddress("n_charm", &nCharm);
  tree->SetBranchAddress("n_beauty", &nBeauty);
  tree->SetBranchAddress("q_c", &qc);
  tree->SetBranchAddress("q_b", &qb);
  tree->SetBranchAddress("is_meson", &isMeson);
  tree->SetBranchAddress("is_baryon", &isBaryon);
  tree->SetBranchAddress("spin_type", &spinType);
  tree->SetBranchAddress("open_heavy", &openHeavy);
  tree->SetBranchAddress("hidden_heavy", &hiddenHeavy);
  tree->SetBranchAddress("central_registry", &centralRegistry);
  tree->SetBranchAddress("final_may_decay", &finalMayDecay);

  std::vector<SpeciesRow> rows;
  long long hidden = 0, decayable = 0, total = tree->GetEntries();
  for (Long64_t i = 0; i < total; ++i) {
    tree->GetEntry(i);
    // The whole construction assumes every heavy hadron is stable. If any is
    // not, the compensation decomposition is not a partition and the axis is
    // meaningless. Refuse rather than emit a table that looks fine.
    if (finalMayDecay != 0) {
      std::printf(
          "ERROR: pdg %d has final_may_decay=%d. The species axis assumes all "
          "heavy hadrons are stable; refusing to emit a table.\n",
          pdg, finalMayDecay);
      in->Close();
      return 4;
    }
    if (hiddenHeavy == 1) ++hidden;
    if (openHeavy != 1) continue;
    SpeciesRow row;
    row.pdg = pdg;
    row.nCharm = nCharm;
    row.nBeauty = nBeauty;
    row.qc = qc;
    row.qb = qb;
    row.isMeson = isMeson;
    row.isBaryon = isBaryon;
    row.spinType = spinType;
    row.centralRegistry = centralRegistry;
    row.category = static_cast<int>(Hadronization::ClassifyHeavyStateDetailed(
        centralRegistry == 1,
        ContentFromAudit(nCharm, nBeauty, qc, qb),
        isMeson != 0,
        spinType));
    rows.push_back(row);
  }
  in->Close();

  // Ordinals are assigned by sorted PDG, not by tree order. Tree order is an
  // artifact of PYTHIA's ParticleData iteration and is not a contract; sorted
  // PDG is stable across releases and reproducible by anyone.
  std::sort(rows.begin(), rows.end(),
            [](const SpeciesRow& a, const SpeciesRow& b) { return a.pdg < b.pdg; });

  std::string canonical;
  for (std::size_t i = 0; i < rows.size(); ++i) {
    canonical += std::to_string(i) + ":" + std::to_string(rows[i].pdg) + ";";
  }
  const std::uint64_t digest = Fnv1a(canonical);
  char digestHex[32];
  std::snprintf(digestHex, sizeof(digestHex), "%016llx",
                static_cast<unsigned long long>(digest));

  long long categoryCounts[6] = {0, 0, 0, 0, 0, 0};
  for (const auto& r : rows) {
    if (r.category < 0 || r.category > 5) {
      std::printf("ERROR: pdg %d produced category %d, outside [0,5].\n", r.pdg,
                  r.category);
      return 6;
    }
    ++categoryCounts[r.category];
  }
  // kOtherNoncentral must be empty BY CONSTRUCTION, and saying so here turns a
  // silent assumption into a check that can fail. Every row in this table has
  // open_heavy == 1, so q_c != 0 or q_b != 0, so n_charm + n_beauty > 0, so
  // ClassifyHeavyStateDetailed's final `hasCharm() || hasBeauty()` branch
  // always fires before kOtherNoncentral can be reached. If this ever trips,
  // the audit tree's open_heavy and its charge columns disagree and the axis's
  // selection is not what it claims.
  if (categoryCounts[3] != 0) {
    std::printf(
        "ERROR: %lld species classified kOtherNoncentral, which is "
        "unreachable for an open-heavy table. open_heavy and the charge "
        "columns disagree.\n",
        categoryCounts[3]);
    return 7;
  }

  FILE* out = std::fopen(outputPath, "w");
  if (!out) {
    std::printf("ERROR: cannot write %s\n", outputPath);
    return 5;
  }
  // v2 adds the category column. The index space is UNCHANGED: the digest
  // below is still taken over ordinal:pdg only, so a v1 and a v2 table derived
  // from the same audit tree carry the SAME digest. That is deliberate -- the
  // axis's identity is its ordinal->PDG map, and annotating it must not look
  // like re-indexing it.
  std::fprintf(out, "{\n");
  std::fprintf(out, "  \"schema\": \"hf_species_ordinal_table_v2\",\n");
  std::fprintf(out, "  \"derived_from\": \"heavy_stability_audit\",\n");
  std::fprintf(out, "  \"source_raw\": \"%s\",\n", rawPath);
  std::fprintf(out, "  \"selection\": \"open_heavy==1 (q_c != 0 or q_b != 0)\",\n");
  std::fprintf(out, "  \"ordinal_order\": \"ascending signed PDG\",\n");
  std::fprintf(out, "  \"unmapped_policy\": \"fail_closed_no_overflow_bin\",\n");
  std::fprintf(out, "  \"species_count\": %zu,\n", rows.size());
  std::fprintf(out, "  \"audit_rows_total\": %lld,\n", total);
  std::fprintf(out, "  \"hidden_heavy_excluded\": %lld,\n", hidden);
  std::fprintf(out, "  \"table_digest_fnv1a64\": \"%s\",\n", digestHex);
  std::fprintf(out,
               "  \"category_source\": \"Hadronization::"
               "ClassifyHeavyStateDetailed, SimulationScripts/"
               "HeavyFlavourUtils.h\",\n");
  std::fprintf(out, "  \"category_counts\": {");
  for (int c = 0; c < 6; ++c) {
    std::fprintf(out, "%s\"%s\": %lld", (c == 0) ? "" : ", ", CategoryName(c),
                 categoryCounts[c]);
  }
  std::fprintf(out, "},\n");
  std::fprintf(out, "  \"species\": [\n");
  for (std::size_t i = 0; i < rows.size(); ++i) {
    const SpeciesRow& r = rows[i];
    std::fprintf(out,
                 "    {\"ordinal\": %zu, \"pdg\": %d, \"n_charm\": %d, "
                 "\"n_beauty\": %d, \"q_c\": %d, \"q_b\": %d, \"is_meson\": %d, "
                 "\"is_baryon\": %d, \"spin_type\": %d, \"central_registry\": %d, "
                 "\"category\": %d, \"category_name\": \"%s\"}%s\n",
                 i, r.pdg, r.nCharm, r.nBeauty, r.qc, r.qb, r.isMeson,
                 r.isBaryon, r.spinType, r.centralRegistry, r.category,
                 CategoryName(r.category),
                 (i + 1 == rows.size()) ? "" : ",");
  }
  std::fprintf(out, "  ]\n}\n");
  std::fclose(out);

  long long inRegistry = 0;
  for (const auto& r : rows) inRegistry += (r.centralRegistry == 1);
  std::printf(
      "SPECIES_ORDINAL_TABLE_WRITTEN file=%s species=%zu ordinals=0..%zu "
      "audit_rows=%lld hidden_excluded=%lld in_registry=%lld "
      "outside_registry=%lld digest=%s\n",
      outputPath, rows.size(), rows.empty() ? 0 : rows.size() - 1, total, hidden,
      inRegistry, static_cast<long long>(rows.size()) - inRegistry, digestHex);
  std::printf("SPECIES_ORDINAL_CATEGORIES");
  for (int c = 0; c < 6; ++c) {
    std::printf(" %s=%lld", CategoryName(c), categoryCounts[c]);
  }
  std::printf("\n");
  return 0;
}
