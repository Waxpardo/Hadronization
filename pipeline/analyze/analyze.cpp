// Lossless raw-v7 to SCHEMA-1 analysis-shard translator and verifier.
#include "physics.hpp"
#include "sha256.hpp"
#include "study_contract.hpp"

#include "TBranch.h"
#include "TFile.h"
#include "TKey.h"
#include "TLeaf.h"
#include "TObjString.h"
#include "TTree.h"
#include "Compression.h"

#include <algorithm>
#include <array>
#include <bitset>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <memory>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <tuple>
#include <type_traits>
#include <utility>
#include <vector>

namespace {

constexpr const char* kSpecSchema = "hadronization_analysis_source_spec_v1";
constexpr const char* kSchemaDigest =
    "3a83a7550c27c3f59989b84eea0204bce45bd9c401744f321758e56f3bf422c9";
constexpr const char* kRegistriesDigest =
    "5462be4f9fed821f6a0c09cda4b461343d1720112f8c76a3afd14ce8130895f3";
constexpr Long64_t kAggregateAutoFlushBytes = 64LL * 1024LL * 1024LL;
constexpr Long64_t kPerTreeAutoFlushBytes = kAggregateAutoFlushBytes / 16LL;
constexpr Int_t kBasketBytes = 32 * 1024;
constexpr ULong64_t kEventFlushInterval = 8192;

enum Family : std::size_t {
  kAncestry = 0, kAncestryMothers, kClosure, kConstituents,
  kEventCompatibility, kEventRanges, kEvents, kHard, kHeavy, kHeavyMothers,
  kOrigins, kPairs, kSourceBlocks, kSourceCounts, kSources, kTriggers,
  kFamilyCount
};

constexpr std::array<const char*, kFamilyCount> kTableNames{{
    "ancestry", "ancestry_mothers", "closure", "constituents",
    "event_compatibility", "event_ranges", "events", "hard", "heavy",
    "heavy_mothers", "origins", "pairs", "source_blocks", "source_counts",
    "sources", "triggers"}};

struct SourceSpec {
  UInt_t sourceId = 0;
  UInt_t tuneOrdinal = 0;
  UInt_t campaignOrdinal = 0;
  ULong64_t logicalId = 0;
  UInt_t attempt = 0;
  Int_t seed = 0;
  ULong64_t events = 0;
  ULong64_t bytes = 0;
  UInt_t block = 0;
  std::string rawSha256, validationReceiptSha256, validationLogSha256;
  std::string tune, storageKey, path, manifestJson;
  std::string producerSha256, producerCommit, effectiveSettingsSha256;
  std::string attemptLedgerSha256, campaign;
};

struct AncestryRow { ULong64_t event_id{}; Int_t node_index{}, pdg{}, status{}, mother1{}, mother2{}; };
struct AncestryMotherRow { ULong64_t event_id{}; Int_t node_index{}; UInt_t edge_ordinal{}; Int_t mother_index{}; };
struct ClosureRow { ULong64_t event_id{}; Int_t trigger_heavy_index{}, associate_heavy_index{}, coefficient{}; UChar_t visible{}; Int_t dense_category{}; };
struct ConstituentRow { ULong64_t event_id{}; Int_t heavy_index{}, signed_flavour{}; UInt_t constituent_ordinal{}; Int_t origin{}, resolution{}, matched_hard{}, rejected_hard{}, depth{}; };
struct CompatibilityRow { ULong64_t event_id{}; UInt_t diagnostic_id{}, cell_id{}; Int_t value{}; };
struct EventRangeRow { ULong64_t first_id{}, count{}; UInt_t source_id{}; };
struct EventRow { ULong64_t event_id{}; Double_t weight{}; Int_t a15_eta1{}, a15_eta4{}, process_code{}; Double_t pthat{}, hard_scale{}; Int_t n_mpi{}; };
struct HardRow { ULong64_t event_id{}; Int_t root_index{}, bottom_index{}, pdg{}, status{}, bottom_pdg{}, bottom_status{}; Double_t px{}, py{}, pz{}, energy{}; };
struct HeavyRow {
  ULong64_t event_id{}; Int_t heavy_index{}, pdg{}, status{}; UChar_t final{}, selected{}, pair_eligible{};
  Int_t category{}; UChar_t is_meson{}, is_baryon{}; Int_t spin{}, charge3{}, nc{}, ncbar{}, nb{}, nbbar{}, qc{}, qb{}, baryon3{}, strangeness{};
  UChar_t open{}, hidden{}; Int_t mother1{}, mother2{}, daughter1{}, daughter2{};
  Double_t px{}, py{}, pz{}, energy{}, mass{}, pt{}, eta{}, rapidity{}, phi{};
};
struct HeavyMotherRow { ULong64_t event_id{}; Int_t heavy_index{}; UInt_t edge_ordinal{}; Int_t mother_index{}; };
struct OriginRow { ULong64_t event_id{}; Int_t heavy_index{}, sector{}, origin{}, resolution{}, matched_hard{}, rejected_hard{}, depth{}; };
struct PairRow {
  ULong64_t event_id{}; Int_t trigger_heavy_index{}, associate_heavy_index{}, sign{};
  Double_t dphi{}, deta{}, trigger_pt{}, associate_pt{}; Int_t a15_eta1{}, a15_eta4{}, associate_origin{}, associate_category{}; Double_t weight{};
};
struct SourceBlockRow { UInt_t source_id{}, assignment_id{}, block{}; };
struct SourceCountRow { UInt_t source_id{}, family_id{}; ULong64_t rows{}; };
struct SourceRow { UInt_t source_id{}, tune{}; ULong64_t logical_id{}; UInt_t attempt{}; ULong64_t events{}, attempted_events{}; Double_t sumw{}, sumw2{}, sumabsw{}; };
struct TriggerRow { ULong64_t event_id{}; Int_t heavy_index{}, sector{}; UInt_t rejection_mask{}; };

#define OUT_U64(T, R, N) (T).Branch(#N, &(R).N, #N "/l")
#define OUT_U32(T, R, N) (T).Branch(#N, &(R).N, #N "/i")
#define OUT_I32(T, R, N) (T).Branch(#N, &(R).N, #N "/I")
#define OUT_U8(T, R, N) (T).Branch(#N, &(R).N, #N "/b")
#define OUT_F64(T, R, N) (T).Branch(#N, &(R).N, #N "/D")
#define IN(T, R, N) (T).SetBranchAddress(#N, &(R).N)

void Branches(TTree& t, AncestryRow& r) { OUT_U64(t,r,event_id); OUT_I32(t,r,node_index); OUT_I32(t,r,pdg); OUT_I32(t,r,status); OUT_I32(t,r,mother1); OUT_I32(t,r,mother2); }
void Branches(TTree& t, AncestryMotherRow& r) { OUT_U64(t,r,event_id); OUT_I32(t,r,node_index); OUT_U32(t,r,edge_ordinal); OUT_I32(t,r,mother_index); }
void Branches(TTree& t, ClosureRow& r) { OUT_U64(t,r,event_id); OUT_I32(t,r,trigger_heavy_index); OUT_I32(t,r,associate_heavy_index); OUT_I32(t,r,coefficient); OUT_U8(t,r,visible); OUT_I32(t,r,dense_category); }
void Branches(TTree& t, ConstituentRow& r) { OUT_U64(t,r,event_id); OUT_I32(t,r,heavy_index); OUT_I32(t,r,signed_flavour); OUT_U32(t,r,constituent_ordinal); OUT_I32(t,r,origin); OUT_I32(t,r,resolution); OUT_I32(t,r,matched_hard); OUT_I32(t,r,rejected_hard); OUT_I32(t,r,depth); }
void Branches(TTree& t, CompatibilityRow& r) { OUT_U64(t,r,event_id); OUT_U32(t,r,diagnostic_id); OUT_U32(t,r,cell_id); OUT_I32(t,r,value); }
void Branches(TTree& t, EventRangeRow& r) { OUT_U64(t,r,first_id); OUT_U64(t,r,count); OUT_U32(t,r,source_id); }
void Branches(TTree& t, EventRow& r) { OUT_U64(t,r,event_id); OUT_F64(t,r,weight); OUT_I32(t,r,a15_eta1); OUT_I32(t,r,a15_eta4); OUT_I32(t,r,process_code); OUT_F64(t,r,pthat); OUT_F64(t,r,hard_scale); OUT_I32(t,r,n_mpi); }
void Branches(TTree& t, HardRow& r) { OUT_U64(t,r,event_id); OUT_I32(t,r,root_index); OUT_I32(t,r,bottom_index); OUT_I32(t,r,pdg); OUT_I32(t,r,status); OUT_I32(t,r,bottom_pdg); OUT_I32(t,r,bottom_status); OUT_F64(t,r,px); OUT_F64(t,r,py); OUT_F64(t,r,pz); OUT_F64(t,r,energy); }
void Branches(TTree& t, HeavyRow& r) {
  OUT_U64(t,r,event_id); OUT_I32(t,r,heavy_index); OUT_I32(t,r,pdg); OUT_I32(t,r,status); OUT_U8(t,r,final); OUT_U8(t,r,selected); OUT_U8(t,r,pair_eligible); OUT_I32(t,r,category); OUT_U8(t,r,is_meson); OUT_U8(t,r,is_baryon); OUT_I32(t,r,spin); OUT_I32(t,r,charge3); OUT_I32(t,r,nc); OUT_I32(t,r,ncbar); OUT_I32(t,r,nb); OUT_I32(t,r,nbbar); OUT_I32(t,r,qc); OUT_I32(t,r,qb); OUT_I32(t,r,baryon3); OUT_I32(t,r,strangeness); OUT_U8(t,r,open); OUT_U8(t,r,hidden); OUT_I32(t,r,mother1); OUT_I32(t,r,mother2); OUT_I32(t,r,daughter1); OUT_I32(t,r,daughter2); OUT_F64(t,r,px); OUT_F64(t,r,py); OUT_F64(t,r,pz); OUT_F64(t,r,energy); OUT_F64(t,r,mass); OUT_F64(t,r,pt); OUT_F64(t,r,eta); OUT_F64(t,r,rapidity); OUT_F64(t,r,phi);
}
void Branches(TTree& t, HeavyMotherRow& r) { OUT_U64(t,r,event_id); OUT_I32(t,r,heavy_index); OUT_U32(t,r,edge_ordinal); OUT_I32(t,r,mother_index); }
void Branches(TTree& t, OriginRow& r) { OUT_U64(t,r,event_id); OUT_I32(t,r,heavy_index); OUT_I32(t,r,sector); OUT_I32(t,r,origin); OUT_I32(t,r,resolution); OUT_I32(t,r,matched_hard); OUT_I32(t,r,rejected_hard); OUT_I32(t,r,depth); }
void Branches(TTree& t, PairRow& r) { OUT_U64(t,r,event_id); OUT_I32(t,r,trigger_heavy_index); OUT_I32(t,r,associate_heavy_index); OUT_I32(t,r,sign); OUT_F64(t,r,dphi); OUT_F64(t,r,deta); OUT_F64(t,r,trigger_pt); OUT_F64(t,r,associate_pt); OUT_I32(t,r,a15_eta1); OUT_I32(t,r,a15_eta4); OUT_I32(t,r,associate_origin); OUT_I32(t,r,associate_category); OUT_F64(t,r,weight); }
void Branches(TTree& t, SourceBlockRow& r) { OUT_U32(t,r,source_id); OUT_U32(t,r,assignment_id); OUT_U32(t,r,block); }
void Branches(TTree& t, SourceCountRow& r) { OUT_U32(t,r,source_id); OUT_U32(t,r,family_id); OUT_U64(t,r,rows); }
void Branches(TTree& t, SourceRow& r) { OUT_U32(t,r,source_id); OUT_U32(t,r,tune); OUT_U64(t,r,logical_id); OUT_U32(t,r,attempt); OUT_U64(t,r,events); OUT_U64(t,r,attempted_events); OUT_F64(t,r,sumw); OUT_F64(t,r,sumw2); OUT_F64(t,r,sumabsw); }
void Branches(TTree& t, TriggerRow& r) { OUT_U64(t,r,event_id); OUT_I32(t,r,heavy_index); OUT_I32(t,r,sector); OUT_U32(t,r,rejection_mask); }

void Read(TTree& t, AncestryRow& r) { IN(t,r,event_id); IN(t,r,node_index); IN(t,r,pdg); IN(t,r,status); IN(t,r,mother1); IN(t,r,mother2); }
void Read(TTree& t, AncestryMotherRow& r) { IN(t,r,event_id); IN(t,r,node_index); IN(t,r,edge_ordinal); IN(t,r,mother_index); }
void Read(TTree& t, ClosureRow& r) { IN(t,r,event_id); IN(t,r,trigger_heavy_index); IN(t,r,associate_heavy_index); IN(t,r,coefficient); IN(t,r,visible); IN(t,r,dense_category); }
void Read(TTree& t, ConstituentRow& r) { IN(t,r,event_id); IN(t,r,heavy_index); IN(t,r,signed_flavour); IN(t,r,constituent_ordinal); IN(t,r,origin); IN(t,r,resolution); IN(t,r,matched_hard); IN(t,r,rejected_hard); IN(t,r,depth); }
void Read(TTree& t, CompatibilityRow& r) { IN(t,r,event_id); IN(t,r,diagnostic_id); IN(t,r,cell_id); IN(t,r,value); }
void Read(TTree& t, EventRangeRow& r) { IN(t,r,first_id); IN(t,r,count); IN(t,r,source_id); }
void Read(TTree& t, EventRow& r) { IN(t,r,event_id); IN(t,r,weight); IN(t,r,a15_eta1); IN(t,r,a15_eta4); IN(t,r,process_code); IN(t,r,pthat); IN(t,r,hard_scale); IN(t,r,n_mpi); }
void Read(TTree& t, HardRow& r) { IN(t,r,event_id); IN(t,r,root_index); IN(t,r,bottom_index); IN(t,r,pdg); IN(t,r,status); IN(t,r,bottom_pdg); IN(t,r,bottom_status); IN(t,r,px); IN(t,r,py); IN(t,r,pz); IN(t,r,energy); }
void Read(TTree& t, HeavyRow& r) {
  IN(t,r,event_id); IN(t,r,heavy_index); IN(t,r,pdg); IN(t,r,status); IN(t,r,final); IN(t,r,selected); IN(t,r,pair_eligible); IN(t,r,category); IN(t,r,is_meson); IN(t,r,is_baryon); IN(t,r,spin); IN(t,r,charge3); IN(t,r,nc); IN(t,r,ncbar); IN(t,r,nb); IN(t,r,nbbar); IN(t,r,qc); IN(t,r,qb); IN(t,r,baryon3); IN(t,r,strangeness); IN(t,r,open); IN(t,r,hidden); IN(t,r,mother1); IN(t,r,mother2); IN(t,r,daughter1); IN(t,r,daughter2); IN(t,r,px); IN(t,r,py); IN(t,r,pz); IN(t,r,energy); IN(t,r,mass); IN(t,r,pt); IN(t,r,eta); IN(t,r,rapidity); IN(t,r,phi);
}
void Read(TTree& t, HeavyMotherRow& r) { IN(t,r,event_id); IN(t,r,heavy_index); IN(t,r,edge_ordinal); IN(t,r,mother_index); }
void Read(TTree& t, OriginRow& r) { IN(t,r,event_id); IN(t,r,heavy_index); IN(t,r,sector); IN(t,r,origin); IN(t,r,resolution); IN(t,r,matched_hard); IN(t,r,rejected_hard); IN(t,r,depth); }
void Read(TTree& t, PairRow& r) { IN(t,r,event_id); IN(t,r,trigger_heavy_index); IN(t,r,associate_heavy_index); IN(t,r,sign); IN(t,r,dphi); IN(t,r,deta); IN(t,r,trigger_pt); IN(t,r,associate_pt); IN(t,r,a15_eta1); IN(t,r,a15_eta4); IN(t,r,associate_origin); IN(t,r,associate_category); IN(t,r,weight); }
void Read(TTree& t, SourceBlockRow& r) { IN(t,r,source_id); IN(t,r,assignment_id); IN(t,r,block); }
void Read(TTree& t, SourceCountRow& r) { IN(t,r,source_id); IN(t,r,family_id); IN(t,r,rows); }
void Read(TTree& t, SourceRow& r) { IN(t,r,source_id); IN(t,r,tune); IN(t,r,logical_id); IN(t,r,attempt); IN(t,r,events); IN(t,r,attempted_events); IN(t,r,sumw); IN(t,r,sumw2); IN(t,r,sumabsw); }
void Read(TTree& t, TriggerRow& r) { IN(t,r,event_id); IN(t,r,heavy_index); IN(t,r,sector); IN(t,r,rejection_mask); }

#undef OUT_U64
#undef OUT_U32
#undef OUT_I32
#undef OUT_U8
#undef OUT_F64
#undef IN

struct Trees {
  std::array<TTree*, kFamilyCount> tree{};
  AncestryRow ancestry; AncestryMotherRow ancestryMothers; ClosureRow closure;
  ConstituentRow constituents; CompatibilityRow compatibility; EventRangeRow ranges;
  EventRow events; HardRow hard; HeavyRow heavy; HeavyMotherRow heavyMothers;
  OriginRow origins; PairRow pairs; SourceBlockRow sourceBlocks;
  SourceCountRow sourceCounts; SourceRow sources; TriggerRow triggers;

  explicit Trees(TFile& output) {
    output.cd();
    for (std::size_t i = 0; i < kFamilyCount; ++i) {
      tree[i] = new TTree(kTableNames[i], kTableNames[i]);
      tree[i]->SetDirectory(&output);
      tree[i]->SetAutoSave(0);
      tree[i]->SetAutoFlush(-kPerTreeAutoFlushBytes);
      tree[i]->SetBasketSize("*", kBasketBytes);
    }
    Branches(*tree[kAncestry], ancestry); Branches(*tree[kAncestryMothers], ancestryMothers);
    Branches(*tree[kClosure], closure); Branches(*tree[kConstituents], constituents);
    Branches(*tree[kEventCompatibility], compatibility); Branches(*tree[kEventRanges], ranges);
    Branches(*tree[kEvents], events); Branches(*tree[kHard], hard);
    Branches(*tree[kHeavy], heavy); Branches(*tree[kHeavyMothers], heavyMothers);
    Branches(*tree[kOrigins], origins); Branches(*tree[kPairs], pairs);
    Branches(*tree[kSourceBlocks], sourceBlocks); Branches(*tree[kSourceCounts], sourceCounts);
    Branches(*tree[kSources], sources); Branches(*tree[kTriggers], triggers);
  }
  template <typename R> void Fill(Family family, R& row) {
    (void)row;
    if (tree[family]->Fill() <= 0) throw std::runtime_error("failed to fill output tree");
  }
  void FlushBaskets() {
    for (auto& item : tree) {
      if (item->FlushBaskets() < 0) {
        throw std::runtime_error("failed to flush output tree baskets");
      }
    }
  }
};

std::string JsonEscape(const std::string& value) {
  std::ostringstream out;
  out << '"';
  for (const unsigned char c : value) {
    switch (c) {
      case '"': out << "\\\""; break;
      case '\\': out << "\\\\"; break;
      case '\b': out << "\\b"; break;
      case '\f': out << "\\f"; break;
      case '\n': out << "\\n"; break;
      case '\r': out << "\\r"; break;
      case '\t': out << "\\t"; break;
      default:
        if (c < 0x20U) out << "\\u" << std::hex << std::setw(4) << std::setfill('0') << static_cast<int>(c) << std::dec;
        else out << static_cast<char>(c);
    }
  }
  out << '"';
  return out.str();
}

std::string FloatHex(double value) {
  if (!std::isfinite(value)) throw std::runtime_error("nonfinite binary64 value");
  std::ostringstream out;
  out.imbue(std::locale::classic());
  out << std::hexfloat << std::setprecision(13) << value;
  return out.str();
}

std::vector<std::string> Split(const std::string& line, char delimiter) {
  std::vector<std::string> parts;
  std::size_t start = 0;
  for (;;) {
    const std::size_t next = line.find(delimiter, start);
    parts.push_back(line.substr(start, next == std::string::npos ? next : next - start));
    if (next == std::string::npos) break;
    start = next + 1;
  }
  return parts;
}

std::string HexDecode(const std::string& text) {
  if (text.size() % 2 != 0) throw std::runtime_error("odd hex field in source spec");
  std::string result;
  result.reserve(text.size() / 2);
  const auto digit = [](char c) -> int {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    throw std::runtime_error("non-lowercase-hex source spec field");
  };
  for (std::size_t i = 0; i < text.size(); i += 2) {
    result.push_back(static_cast<char>((digit(text[i]) << 4) | digit(text[i + 1])));
  }
  return result;
}

bool LowerHex(const std::string& value, std::size_t length) {
  return value.size() == length && std::all_of(value.begin(), value.end(), [](char c) {
    return (c >= '0' && c <= '9') || (c >= 'a' && c <= 'f');
  });
}

template <typename T> T ParseUnsigned(const std::string& text, const char* label) {
  std::size_t used = 0;
  unsigned long long value = 0;
  try { value = std::stoull(text, &used); } catch (...) { throw std::runtime_error(std::string("invalid ") + label); }
  if (used != text.size() || value > static_cast<unsigned long long>(std::numeric_limits<T>::max()))
    throw std::runtime_error(std::string("out-of-domain ") + label);
  return static_cast<T>(value);
}

std::vector<SourceSpec> LoadSpecs(const std::string& path) {
  std::ifstream in(path);
  if (!in) throw std::runtime_error("cannot open source spec");
  std::string line;
  if (!std::getline(in, line) || line != kSpecSchema) throw std::runtime_error("source spec schema differs");
  std::vector<SourceSpec> result;
  while (std::getline(in, line)) {
    const auto p = Split(line, '\t');
    if (p.size() != 21U) throw std::runtime_error("source spec field count differs");
    SourceSpec s;
    s.sourceId = ParseUnsigned<UInt_t>(p[0], "source id");
    s.tuneOrdinal = ParseUnsigned<UInt_t>(p[1], "tune ordinal");
    s.campaignOrdinal = ParseUnsigned<UInt_t>(p[2], "campaign ordinal");
    s.logicalId = ParseUnsigned<ULong64_t>(p[3], "logical id");
    s.attempt = ParseUnsigned<UInt_t>(p[4], "attempt");
    s.seed = static_cast<Int_t>(ParseUnsigned<UInt_t>(p[5], "seed"));
    s.events = ParseUnsigned<ULong64_t>(p[6], "events");
    s.bytes = ParseUnsigned<ULong64_t>(p[7], "bytes");
    s.block = ParseUnsigned<UInt_t>(p[8], "block");
    s.rawSha256 = p[9]; s.validationReceiptSha256 = p[10]; s.validationLogSha256 = p[11];
    s.tune = HexDecode(p[12]); s.storageKey = HexDecode(p[13]); s.path = HexDecode(p[14]);
    s.manifestJson = HexDecode(p[15]); s.producerSha256 = p[16]; s.producerCommit = p[17];
    s.effectiveSettingsSha256 = p[18]; s.attemptLedgerSha256 = p[19];
    s.campaign = HexDecode(p[20]);
    for (const auto* digest : {&s.rawSha256, &s.validationReceiptSha256,
                               &s.validationLogSha256, &s.producerSha256,
                               &s.effectiveSettingsSha256, &s.attemptLedgerSha256}) {
      if (!LowerHex(*digest, 64)) throw std::runtime_error("source spec has invalid SHA-256");
    }
    if (!LowerHex(s.producerCommit, 40) || s.events == 0 || s.bytes == 0 || s.block == 0 ||
        s.tuneOrdinal > 3 || s.campaignOrdinal > 65535 || s.logicalId > 16383 ||
        s.attempt > 4095) throw std::runtime_error("source spec identity is outside raw-v7 domain");
    result.push_back(std::move(s));
  }
  if (result.empty()) throw std::runtime_error("source spec is empty");
  for (std::size_t i = 0; i < result.size(); ++i) {
    if ((i && std::tie(result[i-1].tuneOrdinal, result[i-1].logicalId,
        result[i-1].attempt, result[i-1].storageKey) >= std::tie(result[i].tuneOrdinal,
        result[i].logicalId, result[i].attempt, result[i].storageKey))) {
      throw std::runtime_error("source spec is not in canonical source order");
    }
  }
  return result;
}

std::string ReadFile(const std::string& path) {
  std::ifstream in(path, std::ios::binary);
  if (!in) throw std::runtime_error("cannot read file: " + path);
  std::ostringstream out; out << in.rdbuf();
  if (in.bad()) throw std::runtime_error("failed reading file: " + path);
  return out.str();
}

template <typename T> bool MetadataScalar(TTree* tree, const char* name, T& value, const char* type) {
  TBranch* branch = tree ? tree->GetBranch(name) : nullptr;
  TLeaf* leaf = branch ? branch->GetLeaf(name) : nullptr;
  if (!branch || !leaf || !std::string(branch->GetClassName()).empty() ||
      std::string(leaf->GetTypeName()) != type || leaf->GetLenStatic() != 1) return false;
  tree->SetBranchAddress(name, &value);
  const bool ok = tree->GetEntry(0) > 0;
  tree->ResetBranchAddresses();
  return ok;
}

bool MetadataString(TTree* tree, const char* name, std::string& value) {
  TBranch* branch = tree ? tree->GetBranch(name) : nullptr;
  if (!branch) return false;
  const std::string type = branch->GetClassName();
  if (type != "string" && type != "std::string") return false;
  std::string* pointer = nullptr;
  tree->SetBranchAddress(name, &pointer);
  const bool ok = tree->GetEntry(0) > 0 && pointer;
  if (ok) value = *pointer;
  tree->ResetBranchAddresses();
  return ok;
}

std::string InspectRaw(const std::string& path) {
  TFile file(path.c_str(), "READ");
  auto* metadata = dynamic_cast<TTree*>(file.Get("job_metadata"));
  if (file.IsZombie() || !metadata || metadata->GetEntries() != 1) throw std::runtime_error("missing raw job_metadata");
  std::map<std::string, std::string> strings;
  for (const char* name : {"campaign", "tune", "raw_schema", "config_sha256",
                           "executable_sha256", "repository_commit", "repository_dirty",
                           "effective_settings_sha256", "pythia_version"}) {
    if (!MetadataString(metadata, name, strings[name])) throw std::runtime_error(std::string("missing raw metadata ") + name);
  }
  Int_t logical = -1, attempt = -1, seed = -1, complete = 0;
  ULong64_t events = 0, entries = 0, audit = 0;
  if (!MetadataScalar(metadata,"logical_id",logical,"Int_t") ||
      !MetadataScalar(metadata,"attempt",attempt,"Int_t") ||
      !MetadataScalar(metadata,"seed",seed,"Int_t") ||
      !MetadataScalar(metadata,"complete",complete,"Int_t") ||
      !MetadataScalar(metadata,"successful_events",events,"ULong64_t") ||
      !MetadataScalar(metadata,"tree_entries",entries,"ULong64_t") ||
      !MetadataScalar(metadata,"multiplicity_audit_events",audit,"ULong64_t"))
    throw std::runtime_error("incomplete raw scalar metadata");
  std::ostringstream out;
  out << '{';
  bool first = true;
  for (const auto& item : strings) { if (!first) out << ','; first = false; out << JsonEscape(item.first) << ':' << JsonEscape(item.second); }
  out << ",\"attempt\":" << attempt << ",\"complete\":" << complete
      << ",\"logical_id\":" << logical << ",\"multiplicity_audit_events\":" << audit
      << ",\"seed\":" << seed << ",\"successful_events\":" << events
      << ",\"tree_entries\":" << entries << '}';
  return out.str();
}

std::set<std::string> BranchNames(TTree* tree) {
  std::set<std::string> names;
  if (!tree) return names;
  TIter next(tree->GetListOfBranches());
  while (auto* object = next()) names.insert(object->GetName());
  return names;
}

void RequireVector(TTree* tree, const std::string& name, const char* type) {
  TBranch* branch = tree ? tree->GetBranch(name.c_str()) : nullptr;
  if (!branch || std::string(branch->GetClassName()) != type)
    throw std::runtime_error("raw branch type differs: " + name);
}

void RequireScalar(TTree* tree, const std::string& name, const char* type, int length = 1) {
  TBranch* branch = tree ? tree->GetBranch(name.c_str()) : nullptr;
  TLeaf* leaf = branch ? branch->GetLeaf(name.c_str()) : nullptr;
  if (!branch || !leaf || !std::string(branch->GetClassName()).empty() ||
      std::string(leaf->GetTypeName()) != type || leaf->GetLenStatic() != length)
    throw std::runtime_error("raw scalar branch type differs: " + name);
}

const std::array<const char*, 68> kRawIntVectors{{
    "ID","HFCLASS","STATUS","MOTHER","MOTHERID","heavyIndex","heavyPdg",
    "heavyStatus","heavyStatusAbs","heavyIsFinal","heavyIsMeson","heavyIsBaryon",
    "heavyCharge3","heavySpinType","heavyMother1","heavyMother2","heavyDaughter1",
    "heavyDaughter2","heavyMotherOffsets","heavyMothers","heavyNc","heavyNcbar",
    "heavyNb","heavyNbbar","heavyQc","heavyQb","heavyBaryonNumber",
    "heavyStrangeness","heavyCentral","heavyOpen","heavyHidden","heavyStateCategory",
    "heavyOriginC","heavyOriginB","heavyMatchResolutionC","heavyMatchResolutionB",
    "heavyMatchedHardC","heavyMatchedHardB","heavyRejectedHardC","heavyRejectedHardB",
    "heavyOriginDepthC","heavyOriginDepthB","heavyConstituentOffsets",
    "heavyConstituentParentSlot","heavyConstituentPdg","heavyConstituentOrdinal",
    "heavyConstituentOrigin","heavyConstituentMatchResolution",
    "heavyConstituentMatchedHard","heavyConstituentRejectedHard",
    "heavyConstituentOriginDepth","hard_indices","hard_bottom_indices","hard_ids",
    "hard_status","hard_bottom_ids","hard_bottom_status","ancestryIndex","ancestryPdg",
    "ancestryStatus","ancestryMother1","ancestryMother2","ancestryMotherOffsets",
    "ancestryMothers","multAuditParticleIndex","multAuditPdg","multAuditStatus",
    "multAuditIsHeavy"}};
const std::array<const char*, 20> kRawDoubleVectors{{
    "PT","ETA","Y","PHI","CHARGE","heavyPx","heavyPy","heavyPz","heavyE",
    "heavyPt","heavyEta","heavyY","heavyPhi","heavyMass","multAuditPt","multAuditEta",
    "hard_px","hard_py","hard_pz","hard_e"}};

struct RawEvent {
  ULong64_t eventId{}; Int_t processCode{}, hardChannel{}, nMpi{};
  Double_t weight{}, pthat{}, hardScale{}; Int_t mult10{}, mult40{};
  Int_t species[6]{}; Short_t chargeGrid[128]{}, baryonGrid[128]{};
  Int_t legacyMultiplicity{}, legacyProcess{}, nCharm{}, nBeauty{}, nBc{};
  Int_t finalQc{}, finalQb{}, conservation{}, originValid{}, primaryValid{};
  std::map<std::string, std::vector<int>*> ints;
  std::map<std::string, std::vector<double>*> doubles;
  const std::vector<int>& I(const char* name) const { auto found=ints.find(name); if(found==ints.end()||!found->second) throw std::runtime_error(std::string("null raw vector ")+name); return *found->second; }
  const std::vector<double>& D(const char* name) const { auto found=doubles.find(name); if(found==doubles.end()||!found->second) throw std::runtime_error(std::string("null raw vector ")+name); return *found->second; }
};

void BindRaw(TTree* tree, RawEvent& r) {
  if (!tree) throw std::runtime_error("raw event tree is absent");
  for (const char* name : kRawIntVectors) r.ints.emplace(name, nullptr);
  for (const char* name : kRawDoubleVectors) r.doubles.emplace(name, nullptr);
  for (const char* name : kRawIntVectors) RequireVector(tree, name, "vector<int>");
  for (const char* name : kRawDoubleVectors) RequireVector(tree, name, "vector<double>");
  const std::array<std::pair<const char*, const char*>, 19> scalars{{
      {"event_id","ULong64_t"},{"process_code","Int_t"},{"hard_channel","Int_t"},
      {"event_weight","Double_t"},{"pthat","Double_t"},{"hard_scale","Double_t"},
      {"n_mpi","Int_t"},{"multiplicity_primary_charged_eta10_v1","Int_t"},
      {"multiplicity_primary_charged_eta40_v1","Int_t"},{"MULTIPLICITY","Int_t"},
      {"PROCESSCODE","Int_t"},{"NCHARM","Int_t"},{"NBEAUTY","Int_t"},{"NBC","Int_t"},
      {"final_heavy_qc_sum","Int_t"},{"final_heavy_qb_sum","Int_t"},
      {"heavy_flavour_conservation_ok","Int_t"},{"origin_classification_valid","Int_t"},
      {"primary_all_heavy_match_valid","Int_t"}}};
  for (const auto& item : scalars) RequireScalar(tree,item.first,item.second);
  RequireScalar(tree,"multiplicity_central_by_species","Int_t",6);
  RequireScalar(tree,"light_charge3_grid","Short_t",128);
  RequireScalar(tree,"light_baryon_grid","Short_t",128);
  std::set<std::string> expected;
  for (const auto& item : scalars) expected.insert(item.first);
  expected.insert("multiplicity_central_by_species"); expected.insert("light_charge3_grid"); expected.insert("light_baryon_grid");
  for (const char* name : kRawIntVectors) expected.insert(name);
  for (const char* name : kRawDoubleVectors) expected.insert(name);
  if (BranchNames(tree) != expected) throw std::runtime_error("raw event branch set differs");
  tree->SetBranchAddress("event_id",&r.eventId); tree->SetBranchAddress("process_code",&r.processCode);
  tree->SetBranchAddress("hard_channel",&r.hardChannel); tree->SetBranchAddress("event_weight",&r.weight);
  tree->SetBranchAddress("pthat",&r.pthat); tree->SetBranchAddress("hard_scale",&r.hardScale);
  tree->SetBranchAddress("n_mpi",&r.nMpi); tree->SetBranchAddress("multiplicity_primary_charged_eta10_v1",&r.mult10);
  tree->SetBranchAddress("multiplicity_primary_charged_eta40_v1",&r.mult40);
  tree->SetBranchAddress("multiplicity_central_by_species",r.species);
  tree->SetBranchAddress("light_charge3_grid",r.chargeGrid); tree->SetBranchAddress("light_baryon_grid",r.baryonGrid);
  tree->SetBranchAddress("MULTIPLICITY",&r.legacyMultiplicity); tree->SetBranchAddress("PROCESSCODE",&r.legacyProcess);
  tree->SetBranchAddress("NCHARM",&r.nCharm); tree->SetBranchAddress("NBEAUTY",&r.nBeauty); tree->SetBranchAddress("NBC",&r.nBc);
  tree->SetBranchAddress("final_heavy_qc_sum",&r.finalQc); tree->SetBranchAddress("final_heavy_qb_sum",&r.finalQb);
  tree->SetBranchAddress("heavy_flavour_conservation_ok",&r.conservation);
  tree->SetBranchAddress("origin_classification_valid",&r.originValid);
  tree->SetBranchAddress("primary_all_heavy_match_valid",&r.primaryValid);
  for (auto& item : r.ints) tree->SetBranchAddress(item.first.c_str(), &item.second);
  for (auto& item : r.doubles) tree->SetBranchAddress(item.first.c_str(), &item.second);
}

bool BitsEqual(double a, double b) {
  std::uint64_t x = 0, y = 0; std::memcpy(&x,&a,sizeof(x)); std::memcpy(&y,&b,sizeof(y)); return x == y;
}

int TriggerSector(int pdg) {
  switch (pdg) {
    case 411: case -411: case 421: case -421: case 4122: case -4122: return 4;
    case 511: case -511: case 521: case -521: case 5122: case -5122: return 5;
    default: return 0;
  }
}

int SectorCharge(const HeavyRow& h, int sector) { return sector == 4 ? h.qc : h.qb; }

const OriginRow& SectorOrigin(const std::map<std::pair<int,int>,OriginRow>& origins, int index, int sector) {
  const auto found = origins.find({index,sector});
  if (found == origins.end()) throw std::runtime_error("missing sector origin row");
  return found->second;
}

UInt_t TriggerMask(const HeavyRow& h, const OriginRow& origin, int sector) {
  UInt_t mask = 0;
  if (!h.final) mask |= 1U;
  if (!h.selected || !Hadronization::IsDirectPrimaryStatus(h.status)) mask |= 2U;
  if (origin.origin != static_cast<int>(Hadronization::Origin::kSelectedHard) ||
      origin.resolution != static_cast<int>(Hadronization::MatchResolution::kUnique) ||
      origin.matched_hard < 0 || origin.rejected_hard != -1) mask |= 4U;
  if (std::abs(SectorCharge(h,sector)) != 1) mask |= 8U;
  return mask;
}

int DenseCategory(int category) {
  if (category == 0) return 0;
  if (category == 4) return 1;
  if (category == 5) return 2;
  if (category == 2) return 3;
  throw std::runtime_error("sector-charged closure associate has unreachable category");
}

int PairOrigin(const OriginRow& origin, int associateCharge, int triggerCharge, int triggerHard) {
  using Hadronization::Origin;
  if (origin.origin == static_cast<int>(Origin::kSelectedHard)) {
    if (origin.resolution == static_cast<int>(Hadronization::MatchResolution::kUnique) &&
        origin.rejected_hard == -1 && origin.matched_hard >= 0 &&
        origin.matched_hard != triggerHard && associateCharge * triggerCharge < 0) return 1;
    return 0;
  }
  if (origin.matched_hard != -1) throw std::runtime_error("non-selected origin has matched hard index");
  if (origin.origin == static_cast<int>(Origin::kShower)) return 2;
  if (origin.origin == static_cast<int>(Origin::kMPI)) return 3;
  if (origin.origin == static_cast<int>(Origin::kOtherResolved)) return 4;
  if (origin.origin == static_cast<int>(Origin::kUnresolved)) return 5;
  throw std::runtime_error("unknown origin label");
}

std::string OriginalMetadata(TTree* metadata) {
  if (!metadata || metadata->GetEntries() != 1) throw std::runtime_error("job_metadata must have one row");
  const std::set<std::string> nameSet = BranchNames(metadata);
  std::vector<std::string> names(nameSet.begin(), nameSet.end());
  std::ostringstream out; out << '{'; bool first = true;
  for (const auto& name : names) {
    TBranch* branch = metadata->GetBranch(name.c_str());
    if (!first) out << ',';
    first = false;
    out << JsonEscape(name) << ":{";
    const std::string className = branch->GetClassName();
    if (className == "string" || className == "std::string") {
      std::string value; if (!MetadataString(metadata,name.c_str(),value)) throw std::runtime_error("cannot read metadata string");
      out << "\"type\":\"string\",\"value\":" << JsonEscape(value);
    } else {
      TLeaf* leaf = branch->GetLeaf(name.c_str());
      if (!leaf || leaf->GetLenStatic()!=1) throw std::runtime_error("unsupported raw metadata field");
      branch->GetEntry(0);
      const std::string type = leaf->GetTypeName();
      out << "\"type\":" << JsonEscape(type) << ",\"value\":";
      if (type == "Double_t") out << JsonEscape(FloatHex(leaf->GetValue()));
      else out << JsonEscape(std::to_string(leaf->GetValueLong64()));
    }
    out << '}';
  }
  out << '}'; return out.str();
}

std::string ObjectInventory(TFile& file) {
  std::vector<std::tuple<std::string,std::string,int>> keys;
  TIter next(file.GetListOfKeys());
  while (auto* object = next()) {
    auto* key = dynamic_cast<TKey*>(object);
    if (!key) throw std::runtime_error("non-key raw object");
    keys.emplace_back(key->GetName(),key->GetClassName(),key->GetCycle());
  }
  std::sort(keys.begin(),keys.end());
  std::ostringstream out; out << '[';
  for (std::size_t i=0;i<keys.size();++i) { if(i)out<<','; out << "{\"class\":" << JsonEscape(std::get<1>(keys[i])) << ",\"cycle\":" << std::get<2>(keys[i]) << ",\"name\":" << JsonEscape(std::get<0>(keys[i])) << '}'; }
  out << ']'; return out.str();
}

std::string RawObjectString(TFile& file, const char* name) {
  auto* object = dynamic_cast<TObjString*>(file.Get(name));
  if (!object) throw std::runtime_error(std::string("missing raw object ") + name);
  return object->GetString().Data();
}

struct SourceMetadataBuilder {
  std::vector<std::string> sources;
  std::map<std::string,std::string> effective, stability, statistics;
  static void AddUnique(std::map<std::string,std::string>& dictionary,
                        const std::string& identity, const std::string& payload,
                        const char* label) {
    const auto inserted = dictionary.emplace(identity,payload);
    if(!inserted.second && inserted.first->second!=payload)
      throw std::runtime_error(std::string("content-addressed metadata collision: ")+label);
  }
  void Add(TFile& file, TTree* metadata, const SourceSpec& s) {
    const std::string settings = RawObjectString(file,"effective_settings_canonical");
    const std::string settingsChanged = RawObjectString(file,"effective_changed_settings");
    const std::string stabilityText = RawObjectString(file,"heavy_stability_audit_canonical");
    const std::string stats = RawObjectString(file,"pythia_statistics");
    const std::string settingsSha = Hadronization::Sha256Hex(settings);
    const std::string stabilitySha = Hadronization::Sha256Hex(stabilityText);
    const std::string statisticsSha = Hadronization::Sha256Hex(stats);
    AddUnique(effective,settingsSha,"{\"canonical\":"+JsonEscape(settings)+",\"changed\":"+JsonEscape(settingsChanged)+"}","effective settings");
    AddUnique(stability,stabilitySha,"{\"canonical\":"+JsonEscape(stabilityText)+"}","heavy stability");
    AddUnique(statistics,statisticsSha,JsonEscape(stats),"PYTHIA statistics");
    std::ostringstream row;
    row << "{\"accepted_attempt\":" << s.attempt << ",\"accepted_seed\":" << s.seed
        << ",\"attempt_ledger_identity\":" << JsonEscape(s.attemptLedgerSha256)
        << ",\"attempted_exposure_availability\":\"available_in_raw_metadata\""
        << ",\"campaign_identity\":" << JsonEscape(s.campaign)
        << ",\"effective_settings_identity\":" << JsonEscape(settingsSha)
        << ",\"logical_id\":" << s.logicalId << ",\"manifest_row\":" << s.manifestJson
        << ",\"original_raw_metadata\":" << OriginalMetadata(metadata)
        << ",\"pythia_statistics_identity\":" << JsonEscape(statisticsSha)
        << ",\"raw_bytes\":" << s.bytes << ",\"raw_object_cycles\":" << ObjectInventory(file)
        << ",\"raw_sha256\":" << JsonEscape(s.rawSha256)
        << ",\"raw_storage_key\":" << JsonEscape(s.storageKey)
        << ",\"source_id\":" << s.sourceId << ",\"stability_identity\":" << JsonEscape(stabilitySha)
        << ",\"tune\":" << JsonEscape(s.tune)
        << ",\"validation_log_sha256\":" << JsonEscape(s.validationLogSha256)
        << ",\"validation_receipt_sha256\":" << JsonEscape(s.validationReceiptSha256) << '}';
    sources.push_back(row.str());
  }
  static std::string MapJson(const std::map<std::string,std::string>& values) {
    std::ostringstream out; out << '{'; bool first=true;
    for(const auto& item:values){if(!first)out<<',';first=false;out<<JsonEscape(item.first)<<':'<<item.second;} out<<'}';return out.str();
  }
  std::string Json() const {
    std::ostringstream out;
    out << "{\"dictionaries\":{\"effective_settings\":" << MapJson(effective)
        << ",\"heavy_stability\":" << MapJson(stability)
        << ",\"pythia_statistics\":" << MapJson(statistics) << "},\"sources\":[";
    for(std::size_t i=0;i<sources.size();++i){if(i)out<<',';out<<sources[i];} out<<"]}"; return out.str();
  }
};

void ValidateMetadata(TFile& file, const SourceSpec& s, SourceRow& row) {
  auto* metadata = dynamic_cast<TTree*>(file.Get("job_metadata"));
  auto* tree = dynamic_cast<TTree*>(file.Get("tree"));
  if (!metadata || metadata->GetEntries()!=1 || !tree) throw std::runtime_error("raw metadata/tree contract differs");
  std::map<std::string,std::string> text;
  for(const char* name:{"campaign","tune","raw_schema","selector","origin_algorithm",
      "executable_sha256","repository_commit","repository_dirty","effective_settings_sha256"})
    if(!MetadataString(metadata,name,text[name])) throw std::runtime_error(std::string("missing raw metadata ")+name);
  Int_t logical=-1, attempt=-1, seed=-1, complete=0;
  ULong64_t events=0, entries=0, attempts=0, failures=0, audit=0;
  Double_t sumw=0,sumw2=0;
  if(!MetadataScalar(metadata,"logical_id",logical,"Int_t") || !MetadataScalar(metadata,"attempt",attempt,"Int_t") ||
     !MetadataScalar(metadata,"seed",seed,"Int_t") || !MetadataScalar(metadata,"complete",complete,"Int_t") ||
     !MetadataScalar(metadata,"successful_events",events,"ULong64_t") || !MetadataScalar(metadata,"tree_entries",entries,"ULong64_t") ||
     !MetadataScalar(metadata,"attempts",attempts,"ULong64_t") || !MetadataScalar(metadata,"failed_attempts",failures,"ULong64_t") ||
     !MetadataScalar(metadata,"multiplicity_audit_events",audit,"ULong64_t") ||
     !MetadataScalar(metadata,"sum_weights",sumw,"Double_t") || !MetadataScalar(metadata,"sum_weights2",sumw2,"Double_t"))
    throw std::runtime_error("incomplete raw metadata");
  if(text["campaign"]!=s.campaign || text["tune"]!=s.tune || text["raw_schema"]!=Hadronization::kRawSchema ||
     text["selector"]!=Hadronization::kSelectorVersion || text["origin_algorithm"]!=Hadronization::kOriginAlgorithmVersion ||
     text["executable_sha256"]!=s.producerSha256 || text["repository_commit"]!=s.producerCommit || text["repository_dirty"]!="false" ||
     text["effective_settings_sha256"]!=s.effectiveSettingsSha256 || logical!=static_cast<Int_t>(s.logicalId) ||
     attempt!=static_cast<Int_t>(s.attempt) || seed!=s.seed || complete!=1 || events!=s.events || entries!=s.events ||
     static_cast<ULong64_t>(tree->GetEntries())!=s.events || attempts!=events+failures || audit!=0 || !std::isfinite(sumw) ||
     !std::isfinite(sumw2) || sumw2<0) throw std::runtime_error("raw source metadata authorization differs");
  row.source_id=s.sourceId;row.tune=s.tuneOrdinal;row.logical_id=s.logicalId;row.attempt=s.attempt;
  row.events=events;row.attempted_events=attempts;row.sumw=sumw;row.sumw2=sumw2;
}

void RequireLengths(const RawEvent& r) {
  const std::size_t n=r.I("heavyPdg").size();
  for(const char* name:{"ID","HFCLASS","STATUS","MOTHER","MOTHERID","heavyIndex","heavyStatus","heavyStatusAbs","heavyIsFinal","heavyIsMeson","heavyIsBaryon","heavyCharge3","heavySpinType","heavyMother1","heavyMother2","heavyDaughter1","heavyDaughter2","heavyNc","heavyNcbar","heavyNb","heavyNbbar","heavyQc","heavyQb","heavyBaryonNumber","heavyStrangeness","heavyCentral","heavyOpen","heavyHidden","heavyStateCategory","heavyOriginC","heavyOriginB","heavyMatchResolutionC","heavyMatchResolutionB","heavyMatchedHardC","heavyMatchedHardB","heavyRejectedHardC","heavyRejectedHardB","heavyOriginDepthC","heavyOriginDepthB","heavyPx","heavyPy","heavyPz","heavyE","heavyPt","heavyEta","heavyY","heavyPhi","heavyMass"}) {
    const std::size_t size = (r.ints.count(name) ? r.I(name).size() : r.D(name).size());
    if(size!=n) throw std::runtime_error(std::string("raw heavy vector length mismatch: ")+name);
  }
  if(r.I("heavyMotherOffsets").size()!=n+1 || r.I("heavyConstituentOffsets").size()!=n+1 ||
     r.I("heavyMotherOffsets").front()!=0 || r.I("heavyConstituentOffsets").front()!=0 ||
     r.I("heavyMotherOffsets").back()!=static_cast<int>(r.I("heavyMothers").size()) ||
     r.I("heavyConstituentOffsets").back()!=static_cast<int>(r.I("heavyConstituentPdg").size()))
    throw std::runtime_error("raw heavy offset contract differs");
  const std::size_t c=r.I("heavyConstituentPdg").size();
  for(const char* name:{"heavyConstituentParentSlot","heavyConstituentOrdinal","heavyConstituentOrigin","heavyConstituentMatchResolution","heavyConstituentMatchedHard","heavyConstituentRejectedHard","heavyConstituentOriginDepth"})
    if(r.I(name).size()!=c) throw std::runtime_error("raw constituent vector length mismatch");
  const std::size_t a=r.I("ancestryIndex").size();
  for(const char* name:{"ancestryPdg","ancestryStatus","ancestryMother1","ancestryMother2"}) if(r.I(name).size()!=a) throw std::runtime_error("raw ancestry vector length mismatch");
  if(r.I("ancestryMotherOffsets").size()!=a+1 || r.I("ancestryMotherOffsets").front()!=0 ||
     r.I("ancestryMotherOffsets").back()!=static_cast<int>(r.I("ancestryMothers").size())) throw std::runtime_error("raw ancestry offset contract differs");
  const std::size_t h=r.I("hard_indices").size();
  for(const char* name:{"hard_bottom_indices","hard_ids","hard_status","hard_bottom_ids","hard_bottom_status","hard_px","hard_py","hard_pz","hard_e"}) {
    const std::size_t size=(r.ints.count(name)?r.I(name).size():r.D(name).size());if(size!=h)throw std::runtime_error("raw hard vector length mismatch");
  }
  for(const char* name:{"multAuditParticleIndex","multAuditPdg","multAuditStatus","multAuditIsHeavy"}) if(!r.I(name).empty()) throw std::runtime_error("nonempty Phase-A multAudit vector");
  for(const char* name:{"multAuditPt","multAuditEta"}) if(!r.D(name).empty()) throw std::runtime_error("nonempty Phase-A multAudit vector");
}

template <typename T> void RequireFinite(const std::vector<T>& values, const char* name) {
  for(const auto value:values) if(!std::isfinite(value)) throw std::runtime_error(std::string("nonfinite raw vector ")+name);
}

void ValidateAliases(const RawEvent& r) {
  if(r.legacyMultiplicity!=r.mult10 || r.legacyProcess!=r.processCode) throw std::runtime_error("raw scalar alias mismatch");
  const std::size_t n=r.I("heavyPdg").size();
  int nc=0,nb=0,nbc=0,finalQc=0,finalQb=0;
  for(std::size_t i=0;i<n;++i){
    const bool hc=r.I("heavyNc")[i]+r.I("heavyNcbar")[i]>0;
    const bool hb=r.I("heavyNb")[i]+r.I("heavyNbbar")[i]>0;
    if(hc&&hb)++nbc;else if(hc)++nc;else if(hb)++nb;
    const int klass=hc&&hb?45:(hb?5:(hc?4:-1));
    if(r.I("ID")[i]!=r.I("heavyPdg")[i] || r.I("HFCLASS")[i]!=klass ||
       r.I("STATUS")[i]!=r.I("heavyStatus")[i] || r.I("MOTHER")[i]!=r.I("heavyMother1")[i] ||
       r.I("heavyStatusAbs")[i]!=std::abs(r.I("heavyStatus")[i]) ||
       !BitsEqual(r.D("PT")[i],r.D("heavyPt")[i]) || !BitsEqual(r.D("ETA")[i],r.D("heavyEta")[i]) ||
       !BitsEqual(r.D("Y")[i],r.D("heavyY")[i]) || !BitsEqual(r.D("PHI")[i],r.D("heavyPhi")[i]) ||
       r.D("CHARGE")[i] != static_cast<double>(r.I("heavyCharge3")[i])/3.0)
      throw std::runtime_error("raw legacy heavy alias mismatch");
    if(r.I("heavyIsFinal")[i]){finalQc+=r.I("heavyQc")[i];finalQb+=r.I("heavyQb")[i];}
  }
  if(nc!=r.nCharm||nb!=r.nBeauty||nbc!=r.nBc||finalQc!=r.finalQc||finalQb!=r.finalQb||
     r.conservation!=1||r.originValid!=1||r.primaryValid!=1||finalQc!=0||finalQb!=0)
    throw std::runtime_error("raw count/invariant alias mismatch");
}

void ProcessEvent(Trees& out, std::array<ULong64_t,kFamilyCount>& counts,
                  const RawEvent& r, ULong64_t expectedId) {
  if(r.eventId!=expectedId || !std::isfinite(r.weight) || !std::isfinite(r.pthat) ||
     !std::isfinite(r.hardScale) || r.pthat<0 || r.hardScale<0 || r.nMpi<0 || r.mult10<0 || r.mult40<0)
    throw std::runtime_error("raw event scalar contract differs");
  RequireLengths(r); ValidateAliases(r);
  for(const char* name:kRawDoubleVectors) RequireFinite(r.D(name),name);
  out.events={r.eventId,r.weight,r.mult10,r.mult40,r.processCode,r.pthat,r.hardScale,r.nMpi};out.Fill(kEvents,out.events);++counts[kEvents];
  const auto& hi=r.I("hard_indices");
  for(std::size_t i=0;i<hi.size();++i){
    if(i&&hi[i]<=hi[i-1])throw std::runtime_error("raw hard indices are not increasing");
    out.hard={r.eventId,hi[i],r.I("hard_bottom_indices")[i],r.I("hard_ids")[i],r.I("hard_status")[i],r.I("hard_bottom_ids")[i],r.I("hard_bottom_status")[i],r.D("hard_px")[i],r.D("hard_py")[i],r.D("hard_pz")[i],r.D("hard_e")[i]};out.Fill(kHard,out.hard);++counts[kHard];
  }
  const auto& hidx=r.I("heavyIndex");
  std::map<int,HeavyRow> heavy;
  std::map<std::pair<int,int>,OriginRow> origins;
  for(std::size_t i=0;i<hidx.size();++i){
    if(i&&hidx[i]<=hidx[i-1])throw std::runtime_error("raw heavy vector is not increasing by heavy_index");
    const int pdg=r.I("heavyPdg")[i];const auto* state=Hadronization::FindSelectedState(pdg);
    out.heavy={r.eventId,hidx[i],pdg,r.I("heavyStatus")[i],static_cast<UChar_t>(r.I("heavyIsFinal")[i]),static_cast<UChar_t>(r.I("heavyCentral")[i]),static_cast<UChar_t>(state&&state->pairAnalysisEligible),r.I("heavyStateCategory")[i],static_cast<UChar_t>(r.I("heavyIsMeson")[i]),static_cast<UChar_t>(r.I("heavyIsBaryon")[i]),r.I("heavySpinType")[i],r.I("heavyCharge3")[i],r.I("heavyNc")[i],r.I("heavyNcbar")[i],r.I("heavyNb")[i],r.I("heavyNbbar")[i],r.I("heavyQc")[i],r.I("heavyQb")[i],3*r.I("heavyBaryonNumber")[i],r.I("heavyStrangeness")[i],static_cast<UChar_t>(r.I("heavyOpen")[i]),static_cast<UChar_t>(r.I("heavyHidden")[i]),r.I("heavyMother1")[i],r.I("heavyMother2")[i],r.I("heavyDaughter1")[i],r.I("heavyDaughter2")[i],r.D("heavyPx")[i],r.D("heavyPy")[i],r.D("heavyPz")[i],r.D("heavyE")[i],r.D("heavyMass")[i],r.D("heavyPt")[i],r.D("heavyEta")[i],r.D("heavyY")[i],r.D("heavyPhi")[i]};
    for(int value:{r.I("heavyIsFinal")[i],r.I("heavyCentral")[i],r.I("heavyIsMeson")[i],r.I("heavyIsBaryon")[i],r.I("heavyOpen")[i],r.I("heavyHidden")[i]})if(value!=0&&value!=1)throw std::runtime_error("raw heavy boolean domain differs");
    if(r.I("heavyCentral")[i]!=(state?1:0))throw std::runtime_error("raw selected-state alias mismatch");
    out.Fill(kHeavy,out.heavy);++counts[kHeavy];heavy.emplace(hidx[i],out.heavy);
    for(int sector:{4,5}){
      const bool charm=sector==4;
      out.origins={r.eventId,hidx[i],sector,r.I(charm?"heavyOriginC":"heavyOriginB")[i],r.I(charm?"heavyMatchResolutionC":"heavyMatchResolutionB")[i],r.I(charm?"heavyMatchedHardC":"heavyMatchedHardB")[i],r.I(charm?"heavyRejectedHardC":"heavyRejectedHardB")[i],r.I(charm?"heavyOriginDepthC":"heavyOriginDepthB")[i]};
      out.Fill(kOrigins,out.origins);++counts[kOrigins];origins.emplace(std::make_pair(hidx[i],sector),out.origins);
    }
    const int mb=r.I("heavyMotherOffsets")[i],me=r.I("heavyMotherOffsets")[i+1];
    if(mb<0||me<mb||me>static_cast<int>(r.I("heavyMothers").size()))throw std::runtime_error("raw mother offsets are nonmonotonic");
    int previous=-1;
    for(int j=mb;j<me;++j){if(r.I("heavyMothers")[j]<=previous)throw std::runtime_error("raw expanded heavy mothers are not increasing");previous=r.I("heavyMothers")[j];out.heavyMothers={r.eventId,hidx[i],static_cast<UInt_t>(j-mb),r.I("heavyMothers")[j]};out.Fill(kHeavyMothers,out.heavyMothers);++counts[kHeavyMothers];}
    const int cb=r.I("heavyConstituentOffsets")[i],ce=r.I("heavyConstituentOffsets")[i+1];
    if(cb<0||ce<cb||ce>static_cast<int>(r.I("heavyConstituentPdg").size()))throw std::runtime_error("raw constituent offsets are nonmonotonic");
    std::vector<int> order;for(int j=cb;j<ce;++j)order.push_back(j);
    std::sort(order.begin(),order.end(),[&](int a,int b){return std::tie(r.I("heavyConstituentPdg")[a],r.I("heavyConstituentOrdinal")[a])<std::tie(r.I("heavyConstituentPdg")[b],r.I("heavyConstituentOrdinal")[b]);});
    std::set<std::pair<int,int>> seen;
    for(int j:order){if(r.I("heavyConstituentParentSlot")[j]!=static_cast<int>(i)||!seen.emplace(r.I("heavyConstituentPdg")[j],r.I("heavyConstituentOrdinal")[j]).second)throw std::runtime_error("raw constituent parent/key mismatch");out.constituents={r.eventId,hidx[i],r.I("heavyConstituentPdg")[j],static_cast<UInt_t>(r.I("heavyConstituentOrdinal")[j]),r.I("heavyConstituentOrigin")[j],r.I("heavyConstituentMatchResolution")[j],r.I("heavyConstituentMatchedHard")[j],r.I("heavyConstituentRejectedHard")[j],r.I("heavyConstituentOriginDepth")[j]};out.Fill(kConstituents,out.constituents);++counts[kConstituents];}
  }
  const auto& ai=r.I("ancestryIndex");
  for(std::size_t i=0;i<ai.size();++i){if(i&&ai[i]<=ai[i-1])throw std::runtime_error("raw ancestry indices are not increasing");out.ancestry={r.eventId,ai[i],r.I("ancestryPdg")[i],r.I("ancestryStatus")[i],r.I("ancestryMother1")[i],r.I("ancestryMother2")[i]};out.Fill(kAncestry,out.ancestry);++counts[kAncestry];const int b=r.I("ancestryMotherOffsets")[i],e=r.I("ancestryMotherOffsets")[i+1];if(b<0||e<b||e>static_cast<int>(r.I("ancestryMothers").size()))throw std::runtime_error("raw ancestry offsets are nonmonotonic");int previous=-1;for(int j=b;j<e;++j){if(r.I("ancestryMothers")[j]<=previous)throw std::runtime_error("raw expanded ancestry mothers are not increasing");previous=r.I("ancestryMothers")[j];out.ancestryMothers={r.eventId,ai[i],static_cast<UInt_t>(j-b),r.I("ancestryMothers")[j]};out.Fill(kAncestryMothers,out.ancestryMothers);++counts[kAncestryMothers];}}
  for(UInt_t diagnostic=0;diagnostic<4;++diagnostic){const UInt_t cells=diagnostic<2?128:(diagnostic==2?6:9);for(UInt_t cell=0;cell<cells;++cell){int value=0;if(diagnostic==0)value=r.chargeGrid[cell];else if(diagnostic==1)value=r.baryonGrid[cell];else if(diagnostic==2)value=r.species[cell];else {const std::array<int,9> scalar{{r.hardChannel,r.nCharm,r.nBeauty,r.nBc,r.finalQc,r.finalQb,r.conservation,r.originValid,r.primaryValid}};value=scalar[cell];}if(value){out.compatibility={r.eventId,diagnostic,cell,value};out.Fill(kEventCompatibility,out.compatibility);++counts[kEventCompatibility];}}}
  std::vector<TriggerRow> accepted;
  for(const auto& item:heavy){const int sector=TriggerSector(item.second.pdg);if(!sector)continue;const auto& origin=SectorOrigin(origins,item.first,sector);out.triggers={r.eventId,item.first,sector,TriggerMask(item.second,origin,sector)};out.Fill(kTriggers,out.triggers);++counts[kTriggers];if(out.triggers.rejection_mask==0)accepted.push_back(out.triggers);}
  for(const auto& trigger:accepted){const HeavyRow& th=heavy.at(trigger.heavy_index);const OriginRow& to=SectorOrigin(origins,trigger.heavy_index,trigger.sector);const int tq=SectorCharge(th,trigger.sector);for(const auto& item:heavy){const HeavyRow& ah=item.second;if(ah.heavy_index==th.heavy_index)continue;const int aq=SectorCharge(ah,trigger.sector);if(ah.final&&aq!=0){out.closure={r.eventId,th.heavy_index,ah.heavy_index,-tq*aq,static_cast<UChar_t>(std::abs(ah.eta)<=4.0),DenseCategory(ah.category)};out.Fill(kClosure,out.closure);++counts[kClosure];}const auto* state=Hadronization::FindSelectedState(ah.pdg);if(!state||((trigger.sector==4)!=(state->sector=="charm"))||!ah.final||!ah.selected||!Hadronization::IsDirectPrimaryStatus(ah.status))continue;const OriginRow& ao=SectorOrigin(origins,ah.heavy_index,trigger.sector);const int origin=PairOrigin(ao,aq,tq,to.matched_hard);if(!origin)continue;out.pairs={r.eventId,th.heavy_index,ah.heavy_index,(tq*aq<0?-1:1),Hadronization::WrapDeltaPhi(th.phi,ah.phi),th.eta-ah.eta,th.pt,ah.pt,r.mult10,r.mult40,origin,ah.category,r.weight};out.Fill(kPairs,out.pairs);++counts[kPairs];}}
}

void ReplaceExactlyOne(std::string& text,const std::string& needle,const std::string& value){const auto at=text.find(needle);if(at==std::string::npos||text.find(needle,at+needle.size())!=std::string::npos)throw std::runtime_error("contract placeholder cardinality differs");text.replace(at,needle.size(),value);}

// Row-value and key encoders used by the independent reopen pass.
std::string I64(long long v){return std::to_string(v);} std::string U64(unsigned long long v){return std::to_string(v);} std::string F64(double v){return FloatHex(v);}
#define V(...) std::vector<std::string>{__VA_ARGS__}
std::vector<std::string> Values(const AncestryRow&r){return V(U64(r.event_id),I64(r.node_index),I64(r.pdg),I64(r.status),I64(r.mother1),I64(r.mother2));}
std::vector<std::string> Values(const AncestryMotherRow&r){return V(U64(r.event_id),I64(r.node_index),U64(r.edge_ordinal),I64(r.mother_index));}
std::vector<std::string> Values(const ClosureRow&r){return V(U64(r.event_id),I64(r.trigger_heavy_index),I64(r.associate_heavy_index),I64(r.coefficient),U64(r.visible),I64(r.dense_category));}
std::vector<std::string> Values(const ConstituentRow&r){return V(U64(r.event_id),I64(r.heavy_index),I64(r.signed_flavour),U64(r.constituent_ordinal),I64(r.origin),I64(r.resolution),I64(r.matched_hard),I64(r.rejected_hard),I64(r.depth));}
std::vector<std::string> Values(const CompatibilityRow&r){return V(U64(r.event_id),U64(r.diagnostic_id),U64(r.cell_id),I64(r.value));}
std::vector<std::string> Values(const EventRangeRow&r){return V(U64(r.first_id),U64(r.count),U64(r.source_id));}
std::vector<std::string> Values(const EventRow&r){return V(U64(r.event_id),F64(r.weight),I64(r.a15_eta1),I64(r.a15_eta4),I64(r.process_code),F64(r.pthat),F64(r.hard_scale),I64(r.n_mpi));}
std::vector<std::string> Values(const HardRow&r){return V(U64(r.event_id),I64(r.root_index),I64(r.bottom_index),I64(r.pdg),I64(r.status),I64(r.bottom_pdg),I64(r.bottom_status),F64(r.px),F64(r.py),F64(r.pz),F64(r.energy));}
std::vector<std::string> Values(const HeavyRow&r){return V(U64(r.event_id),I64(r.heavy_index),I64(r.pdg),I64(r.status),U64(r.final),U64(r.selected),U64(r.pair_eligible),I64(r.category),U64(r.is_meson),U64(r.is_baryon),I64(r.spin),I64(r.charge3),I64(r.nc),I64(r.ncbar),I64(r.nb),I64(r.nbbar),I64(r.qc),I64(r.qb),I64(r.baryon3),I64(r.strangeness),U64(r.open),U64(r.hidden),I64(r.mother1),I64(r.mother2),I64(r.daughter1),I64(r.daughter2),F64(r.px),F64(r.py),F64(r.pz),F64(r.energy),F64(r.mass),F64(r.pt),F64(r.eta),F64(r.rapidity),F64(r.phi));}
std::vector<std::string> Values(const HeavyMotherRow&r){return V(U64(r.event_id),I64(r.heavy_index),U64(r.edge_ordinal),I64(r.mother_index));}
std::vector<std::string> Values(const OriginRow&r){return V(U64(r.event_id),I64(r.heavy_index),I64(r.sector),I64(r.origin),I64(r.resolution),I64(r.matched_hard),I64(r.rejected_hard),I64(r.depth));}
std::vector<std::string> Values(const PairRow&r){return V(U64(r.event_id),I64(r.trigger_heavy_index),I64(r.associate_heavy_index),I64(r.sign),F64(r.dphi),F64(r.deta),F64(r.trigger_pt),F64(r.associate_pt),I64(r.a15_eta1),I64(r.a15_eta4),I64(r.associate_origin),I64(r.associate_category),F64(r.weight));}
std::vector<std::string> Values(const SourceBlockRow&r){return V(U64(r.source_id),U64(r.assignment_id),U64(r.block));}
std::vector<std::string> Values(const SourceCountRow&r){return V(U64(r.source_id),U64(r.family_id),U64(r.rows));}
std::vector<std::string> Values(const SourceRow&r){return V(U64(r.source_id),U64(r.tune),U64(r.logical_id),U64(r.attempt),U64(r.events),U64(r.attempted_events),F64(r.sumw),F64(r.sumw2),F64(r.sumabsw));}
std::vector<std::string> Values(const TriggerRow&r){return V(U64(r.event_id),I64(r.heavy_index),I64(r.sector),U64(r.rejection_mask));}
#undef V

void AppendUnsignedKey(std::string& key,std::uint64_t value){for(int shift=56;shift>=0;shift-=8)key.push_back(static_cast<char>((value>>shift)&0xffU));}
void AppendSignedKey(std::string& key,std::int64_t value){AppendUnsignedKey(key,static_cast<std::uint64_t>(value)^0x8000000000000000ULL);}
std::string Key(const AncestryRow&r){std::string k;AppendUnsignedKey(k,r.event_id);AppendSignedKey(k,r.node_index);return k;}
std::string Key(const AncestryMotherRow&r){std::string k=Key(AncestryRow{r.event_id,r.node_index});AppendUnsignedKey(k,r.edge_ordinal);return k;}
std::string Key(const ClosureRow&r){std::string k;AppendUnsignedKey(k,r.event_id);AppendSignedKey(k,r.trigger_heavy_index);AppendSignedKey(k,r.associate_heavy_index);return k;}
std::string Key(const ConstituentRow&r){std::string k;AppendUnsignedKey(k,r.event_id);AppendSignedKey(k,r.heavy_index);AppendSignedKey(k,r.signed_flavour);AppendUnsignedKey(k,r.constituent_ordinal);return k;}
std::string Key(const CompatibilityRow&r){std::string k;AppendUnsignedKey(k,r.event_id);AppendUnsignedKey(k,r.diagnostic_id);AppendUnsignedKey(k,r.cell_id);return k;}
std::string Key(const EventRangeRow&r){std::string k;AppendUnsignedKey(k,r.first_id);return k;}
std::string Key(const EventRow&r){std::string k;AppendUnsignedKey(k,r.event_id);return k;}
std::string Key(const HardRow&r){std::string k;AppendUnsignedKey(k,r.event_id);AppendSignedKey(k,r.root_index);return k;}
std::string Key(const HeavyRow&r){std::string k;AppendUnsignedKey(k,r.event_id);AppendSignedKey(k,r.heavy_index);return k;}
std::string Key(const HeavyMotherRow&r){std::string k=Key(HeavyRow{r.event_id,r.heavy_index});AppendUnsignedKey(k,r.edge_ordinal);return k;}
std::string Key(const OriginRow&r){std::string k=Key(HeavyRow{r.event_id,r.heavy_index});AppendSignedKey(k,r.sector);return k;}
std::string Key(const PairRow&r){std::string k;AppendUnsignedKey(k,r.event_id);AppendSignedKey(k,r.trigger_heavy_index);AppendSignedKey(k,r.associate_heavy_index);return k;}
std::string Key(const SourceBlockRow&r){std::string k;AppendUnsignedKey(k,r.source_id);AppendUnsignedKey(k,r.assignment_id);return k;}
std::string Key(const SourceCountRow&r){std::string k;AppendUnsignedKey(k,r.source_id);AppendUnsignedKey(k,r.family_id);return k;}
std::string Key(const SourceRow&r){std::string k;AppendUnsignedKey(k,r.source_id);return k;}
std::string Key(const TriggerRow&r){std::string k;AppendUnsignedKey(k,r.event_id);AppendSignedKey(k,r.heavy_index);return k;}

void UpdateLength(Hadronization::Sha256& digest,const std::string& value){std::array<char,8> length{};std::uint64_t n=value.size();for(int shift=56,i=0;shift>=0;shift-=8,++i)length[i]=static_cast<char>((n>>shift)&0xffU);digest.Update(length.data(),length.size());digest.Update(value);}

template <typename R> void DigestTree(TTree* tree,const char* name,R& row,Hadronization::Sha256& digest){
  Read(*tree,row);digest.Update(name);const char zero='\0';digest.Update(&zero,1);std::string previous;bool first=true;
  for(Long64_t i=0;i<tree->GetEntries();++i){if(tree->GetEntry(i)<=0)throw std::runtime_error(std::string("cannot read output tree ")+name);const std::string key=Key(row);if(!first&&key<=previous)throw std::runtime_error(std::string("duplicate/nonmonotonic natural key in ")+name);first=false;previous=key;for(const auto& value:Values(row))UpdateLength(digest,value);}
  tree->ResetBranchAddresses();
}

std::vector<std::pair<std::string,std::string>> ExpectedFields(Family family){
  static const std::array<std::string,kFamilyCount> specs{{
    "event_id:ULong64_t,node_index:Int_t,pdg:Int_t,status:Int_t,mother1:Int_t,mother2:Int_t",
    "event_id:ULong64_t,node_index:Int_t,edge_ordinal:UInt_t,mother_index:Int_t",
    "event_id:ULong64_t,trigger_heavy_index:Int_t,associate_heavy_index:Int_t,coefficient:Int_t,visible:UChar_t,dense_category:Int_t",
    "event_id:ULong64_t,heavy_index:Int_t,signed_flavour:Int_t,constituent_ordinal:UInt_t,origin:Int_t,resolution:Int_t,matched_hard:Int_t,rejected_hard:Int_t,depth:Int_t",
    "event_id:ULong64_t,diagnostic_id:UInt_t,cell_id:UInt_t,value:Int_t",
    "first_id:ULong64_t,count:ULong64_t,source_id:UInt_t",
    "event_id:ULong64_t,weight:Double_t,a15_eta1:Int_t,a15_eta4:Int_t,process_code:Int_t,pthat:Double_t,hard_scale:Double_t,n_mpi:Int_t",
    "event_id:ULong64_t,root_index:Int_t,bottom_index:Int_t,pdg:Int_t,status:Int_t,bottom_pdg:Int_t,bottom_status:Int_t,px:Double_t,py:Double_t,pz:Double_t,energy:Double_t",
    "event_id:ULong64_t,heavy_index:Int_t,pdg:Int_t,status:Int_t,final:UChar_t,selected:UChar_t,pair_eligible:UChar_t,category:Int_t,is_meson:UChar_t,is_baryon:UChar_t,spin:Int_t,charge3:Int_t,nc:Int_t,ncbar:Int_t,nb:Int_t,nbbar:Int_t,qc:Int_t,qb:Int_t,baryon3:Int_t,strangeness:Int_t,open:UChar_t,hidden:UChar_t,mother1:Int_t,mother2:Int_t,daughter1:Int_t,daughter2:Int_t,px:Double_t,py:Double_t,pz:Double_t,energy:Double_t,mass:Double_t,pt:Double_t,eta:Double_t,rapidity:Double_t,phi:Double_t",
    "event_id:ULong64_t,heavy_index:Int_t,edge_ordinal:UInt_t,mother_index:Int_t",
    "event_id:ULong64_t,heavy_index:Int_t,sector:Int_t,origin:Int_t,resolution:Int_t,matched_hard:Int_t,rejected_hard:Int_t,depth:Int_t",
    "event_id:ULong64_t,trigger_heavy_index:Int_t,associate_heavy_index:Int_t,sign:Int_t,dphi:Double_t,deta:Double_t,trigger_pt:Double_t,associate_pt:Double_t,a15_eta1:Int_t,a15_eta4:Int_t,associate_origin:Int_t,associate_category:Int_t,weight:Double_t",
    "source_id:UInt_t,assignment_id:UInt_t,block:UInt_t",
    "source_id:UInt_t,family_id:UInt_t,rows:ULong64_t",
    "source_id:UInt_t,tune:UInt_t,logical_id:ULong64_t,attempt:UInt_t,events:ULong64_t,attempted_events:ULong64_t,sumw:Double_t,sumw2:Double_t,sumabsw:Double_t",
    "event_id:ULong64_t,heavy_index:Int_t,sector:Int_t,rejection_mask:UInt_t"}};
  std::vector<std::pair<std::string,std::string>> result;for(const auto& token:Split(specs[family],',')){const auto p=Split(token,':');result.emplace_back(p[0],p[1]);}return result;
}

void ValidateTreeSchema(TTree* tree,Family family){if(!tree)throw std::runtime_error(std::string("missing tree ")+kTableNames[family]);const auto fields=ExpectedFields(family);std::vector<std::string> actual;TIter next(tree->GetListOfBranches());while(auto* object=next())actual.push_back(object->GetName());std::vector<std::string> expected;for(const auto& f:fields)expected.push_back(f.first);if(actual!=expected)throw std::runtime_error(std::string("branch order/set differs in ")+kTableNames[family]);for(const auto& f:fields){TBranch* b=tree->GetBranch(f.first.c_str());TLeaf* l=b?b->GetLeaf(f.first.c_str()):nullptr;if(!b||!l||!std::string(b->GetClassName()).empty()||std::string(l->GetTypeName())!=f.second||l->GetLenStatic()!=1)throw std::runtime_error(std::string("branch type differs in ")+kTableNames[family]+"."+f.first);}}

std::string ExtractDigest(const std::string& contract){const std::string prefix="\"scientific_content_digest\":\"";const auto at=contract.find(prefix);if(at==std::string::npos||contract.find(prefix,at+prefix.size())!=std::string::npos)throw std::runtime_error("contract scientific digest field differs");const std::string value=contract.substr(at+prefix.size(),64);if(!LowerHex(value,64)||contract.at(at+prefix.size()+64)!='"')throw std::runtime_error("contract scientific digest value differs");return value;}

struct RootView {
  TFile file; std::array<TTree*,kFamilyCount> tree{};
  explicit RootView(const std::string& path, bool requireContract=true):file(path.c_str(),"READ"){
    if(file.IsZombie())throw std::runtime_error("analysis shard is zombie/unreadable");
    if(file.GetCompressionAlgorithm()!=static_cast<int>(ROOT::RCompressionSetting::EAlgorithm::kZSTD)||file.GetCompressionLevel()!=5)throw std::runtime_error("analysis compression contract differs");
    std::map<std::string,std::pair<std::string,int>> keys;
    TIter next(file.GetListOfKeys());
    while(auto* object=next()){auto* key=dynamic_cast<TKey*>(object);if(!key||!keys.emplace(key->GetName(),std::make_pair(key->GetClassName(),key->GetCycle())).second)throw std::runtime_error("unknown or duplicate ROOT key/cycle");}
    std::set<std::string> expected;for(const char* name:kTableNames)expected.insert(name);if(requireContract)expected.insert("contract");std::set<std::string> actual;for(const auto& item:keys)actual.insert(item.first);if(actual!=expected)throw std::runtime_error("analysis ROOT object set differs");
    for(std::size_t i=0;i<kFamilyCount;++i){if(keys.at(kTableNames[i])!=std::make_pair(std::string("TTree"),1))throw std::runtime_error("analysis tree key class/cycle differs");tree[i]=dynamic_cast<TTree*>(file.Get(kTableNames[i]));ValidateTreeSchema(tree[i],static_cast<Family>(i));}
    if(requireContract&&keys.at("contract")!=std::make_pair(std::string("TObjString"),1))throw std::runtime_error("contract key class/cycle differs");
  }
};

std::pair<std::string,std::array<ULong64_t,kFamilyCount>> DigestAndOrder(RootView& view){Hadronization::Sha256 d;AncestryRow a;AncestryMotherRow am;ClosureRow c;ConstituentRow co;CompatibilityRow cp;EventRangeRow er;EventRow e;HardRow h;HeavyRow he;HeavyMotherRow hm;OriginRow o;PairRow p;SourceBlockRow sb;SourceCountRow sc;SourceRow s;TriggerRow tr;DigestTree(view.tree[kAncestry],"ancestry",a,d);DigestTree(view.tree[kAncestryMothers],"ancestry_mothers",am,d);DigestTree(view.tree[kClosure],"closure",c,d);DigestTree(view.tree[kConstituents],"constituents",co,d);DigestTree(view.tree[kEventCompatibility],"event_compatibility",cp,d);DigestTree(view.tree[kEventRanges],"event_ranges",er,d);DigestTree(view.tree[kEvents],"events",e,d);DigestTree(view.tree[kHard],"hard",h,d);DigestTree(view.tree[kHeavy],"heavy",he,d);DigestTree(view.tree[kHeavyMothers],"heavy_mothers",hm,d);DigestTree(view.tree[kOrigins],"origins",o,d);DigestTree(view.tree[kPairs],"pairs",p,d);DigestTree(view.tree[kSourceBlocks],"source_blocks",sb,d);DigestTree(view.tree[kSourceCounts],"source_counts",sc,d);DigestTree(view.tree[kSources],"sources",s,d);DigestTree(view.tree[kTriggers],"triggers",tr,d);std::array<ULong64_t,kFamilyCount> rows{};for(std::size_t i=0;i<kFamilyCount;++i)rows[i]=view.tree[i]->GetEntries();return {d.FinalHex(),rows};}

template<typename R> std::vector<R> LoadRows(TTree* tree);

template<typename R> UInt_t ScientificSource(const R& row,const std::vector<EventRangeRow>& ranges){
  if constexpr(std::is_same_v<R,SourceRow>||std::is_same_v<R,SourceBlockRow>||std::is_same_v<R,SourceCountRow>)return row.source_id;
  else if constexpr(std::is_same_v<R,EventRangeRow>)return row.source_id;
  else {auto it=std::upper_bound(ranges.begin(),ranges.end(),row.event_id,[](ULong64_t value,const EventRangeRow&r){return value<r.first_id;});if(it==ranges.begin())throw std::runtime_error("scientific source routing failed");--it;if(row.event_id>=it->first_id+it->count)throw std::runtime_error("scientific source routing failed");return it->source_id;}
}

template<typename R> std::vector<std::string> SourceValues(const R& row){
  auto values=Values(row);
  if constexpr(std::is_same_v<R,SourceRow>||std::is_same_v<R,SourceBlockRow>||std::is_same_v<R,SourceCountRow>)values[0]="0";
  else if constexpr(std::is_same_v<R,EventRangeRow>)values[2]="0";
  return values;
}

template<typename R> void SourceDigestTree(TTree* tree,const char* name,R& row,const std::vector<EventRangeRow>& ranges,std::vector<std::unique_ptr<Hadronization::Sha256>>& digests){
  const char zero='\0';for(auto&digest:digests){digest->Update(name);digest->Update(&zero,1);}Read(*tree,row);
  for(Long64_t i=0;i<tree->GetEntries();++i){if(tree->GetEntry(i)<=0)throw std::runtime_error("cannot read source-digest row");const UInt_t source=ScientificSource(row,ranges);if(source>=digests.size())throw std::runtime_error("source digest routing is out of domain");for(const auto&value:SourceValues(row))UpdateLength(*digests[source],value);}tree->ResetBranchAddresses();
}

std::vector<std::string> SourceDigests(RootView& view){
  const auto ranges=LoadRows<EventRangeRow>(view.tree[kEventRanges]);const auto sources=LoadRows<SourceRow>(view.tree[kSources]);std::vector<std::unique_ptr<Hadronization::Sha256>> digests;for(std::size_t i=0;i<sources.size();++i)digests.push_back(std::make_unique<Hadronization::Sha256>());
  AncestryRow a;AncestryMotherRow am;ClosureRow c;ConstituentRow co;CompatibilityRow cp;EventRangeRow er;EventRow e;HardRow h;HeavyRow he;HeavyMotherRow hm;OriginRow o;PairRow p;SourceBlockRow sb;SourceCountRow sc;SourceRow s;TriggerRow tr;
  SourceDigestTree(view.tree[kAncestry],"ancestry",a,ranges,digests);SourceDigestTree(view.tree[kAncestryMothers],"ancestry_mothers",am,ranges,digests);SourceDigestTree(view.tree[kClosure],"closure",c,ranges,digests);SourceDigestTree(view.tree[kConstituents],"constituents",co,ranges,digests);SourceDigestTree(view.tree[kEventCompatibility],"event_compatibility",cp,ranges,digests);SourceDigestTree(view.tree[kEventRanges],"event_ranges",er,ranges,digests);SourceDigestTree(view.tree[kEvents],"events",e,ranges,digests);SourceDigestTree(view.tree[kHard],"hard",h,ranges,digests);SourceDigestTree(view.tree[kHeavy],"heavy",he,ranges,digests);SourceDigestTree(view.tree[kHeavyMothers],"heavy_mothers",hm,ranges,digests);SourceDigestTree(view.tree[kOrigins],"origins",o,ranges,digests);SourceDigestTree(view.tree[kPairs],"pairs",p,ranges,digests);SourceDigestTree(view.tree[kSourceBlocks],"source_blocks",sb,ranges,digests);SourceDigestTree(view.tree[kSourceCounts],"source_counts",sc,ranges,digests);SourceDigestTree(view.tree[kSources],"sources",s,ranges,digests);SourceDigestTree(view.tree[kTriggers],"triggers",tr,ranges,digests);
  std::vector<std::string> result;for(auto&digest:digests)result.push_back(digest->FinalHex());return result;
}

std::string DigestListJson(const std::vector<std::string>& values){std::ostringstream out;out<<'[';for(std::size_t i=0;i<values.size();++i){if(i)out<<',';out<<JsonEscape(values[i]);}out<<']';return out.str();}

template<typename R> std::vector<R> LoadRows(TTree* tree){R row;Read(*tree,row);std::vector<R> result;result.reserve(static_cast<std::size_t>(tree->GetEntries()));for(Long64_t i=0;i<tree->GetEntries();++i){if(tree->GetEntry(i)<=0)throw std::runtime_error("cannot read semantic row");result.push_back(row);}tree->ResetBranchAddresses();return result;}

template<typename R> class EventCursor {
 public:
  explicit EventCursor(TTree* tree):tree_(tree),entries_(tree->GetEntries()){Read(*tree_,row_);}
  std::vector<R> Take(ULong64_t eventId){
    std::vector<R> rows;
    while(true){
      Load();
      if(!loaded_)return rows;
      if(row_.event_id<eventId)throw std::runtime_error("orphan or nonmonotonic event-scoped row");
      if(row_.event_id>eventId)return rows;
      rows.push_back(row_);loaded_=false;++entry_;
    }
  }
  void Finish(){Load();if(loaded_||entry_!=entries_)throw std::runtime_error("event-scoped rows remain after final event");tree_->ResetBranchAddresses();}
 private:
  void Load(){if(!loaded_&&entry_<entries_){if(tree_->GetEntry(entry_)<=0)throw std::runtime_error("cannot read semantic row");loaded_=true;}}
  TTree* tree_;R row_{};Long64_t entry_{},entries_{};bool loaded_{};
};

template<typename R> bool SameRow(const R& left,const R& right){return Values(left)==Values(right);}

void ValidateOriginDecision(int origin,int resolution,int matched,int rejected,int depth,bool applicable){
  using Hadronization::MatchResolution;using Hadronization::Origin;
  if(!applicable){if(origin!=static_cast<int>(Origin::kUnresolved)||resolution!=static_cast<int>(MatchResolution::kNotApplicable)||matched!=-1||rejected!=-1||depth!=-1)throw std::runtime_error("non-applicable origin decision differs");return;}
  if(origin==static_cast<int>(Origin::kSelectedHard)){if(resolution!=static_cast<int>(MatchResolution::kUnique)||matched<0||rejected!=-1||depth<1)throw std::runtime_error("selected-hard origin decision differs");return;}
  if(origin>=static_cast<int>(Origin::kShower)&&origin<=static_cast<int>(Origin::kOtherResolved)){if(resolution!=static_cast<int>(MatchResolution::kUnique)||matched!=-1||rejected!=-1||depth<1)throw std::runtime_error("resolved non-hard origin decision differs");return;}
  if(origin!=static_cast<int>(Origin::kUnresolved)||resolution<static_cast<int>(MatchResolution::kAmbiguous)||resolution>static_cast<int>(MatchResolution::kMultipleHeavyConstituents)||matched!=-1||depth<-1||(resolution==static_cast<int>(MatchResolution::kDuplicateHardCarrier)&&rejected<0)||(resolution>=static_cast<int>(MatchResolution::kAmbiguous)&&resolution<=static_cast<int>(MatchResolution::kBrokenLineage)&&rejected!=-1))throw std::runtime_error("unresolved origin decision differs");
}

void ValidateSemantics(RootView& view){
  const auto sources=LoadRows<SourceRow>(view.tree[kSources]);const auto ranges=LoadRows<EventRangeRow>(view.tree[kEventRanges]);const auto blocks=LoadRows<SourceBlockRow>(view.tree[kSourceBlocks]);const auto declared=LoadRows<SourceCountRow>(view.tree[kSourceCounts]);
  if(sources.empty()||ranges.size()!=sources.size()||blocks.size()!=sources.size()||declared.size()!=sources.size()*kFamilyCount)throw std::runtime_error("source accounting cardinality differs");
  std::map<UInt_t,std::array<ULong64_t,kFamilyCount>> observed;
  for(const auto&s:sources){if(s.source_id>=sources.size()||s.source_id!=&s-&sources[0]||s.events==0||s.attempted_events<s.events||!std::isfinite(s.sumw)||!std::isfinite(s.sumw2)||!std::isfinite(s.sumabsw)||s.sumw2<0||s.sumabsw<0)throw std::runtime_error("source row contract differs");observed[s.source_id][kSources]=1;observed[s.source_id][kSourceBlocks]=1;observed[s.source_id][kEventRanges]=1;observed[s.source_id][kSourceCounts]=kFamilyCount;}
  for(std::size_t i=0;i<ranges.size();++i){if(ranges[i].source_id!=i||ranges[i].count!=sources[i].events||(i&&ranges[i-1].first_id+ranges[i-1].count>ranges[i].first_id))throw std::runtime_error("event range coverage/overlap differs");}
  for (std::size_t i = 0; i < blocks.size(); ++i) {
    if (blocks[i].source_id != i || blocks[i].assignment_id != 0 ||
        blocks[i].block == 0) {
      throw std::runtime_error("source block assignment differs");
    }
  }
  auto sourceFor=[&](ULong64_t event){auto it=std::upper_bound(ranges.begin(),ranges.end(),event,[](ULong64_t value,const EventRangeRow&r){return value<r.first_id;});if(it==ranges.begin())throw std::runtime_error("event outside source ranges");--it;if(event>=it->first_id+it->count)throw std::runtime_error("event outside source ranges");return it->source_id;};
  EventCursor<AncestryRow> ancestry(view.tree[kAncestry]);EventCursor<AncestryMotherRow> ancestryMothers(view.tree[kAncestryMothers]);EventCursor<ClosureRow> closure(view.tree[kClosure]);EventCursor<ConstituentRow> constituents(view.tree[kConstituents]);EventCursor<CompatibilityRow> compatibility(view.tree[kEventCompatibility]);EventCursor<HardRow> hard(view.tree[kHard]);EventCursor<HeavyRow> heavy(view.tree[kHeavy]);EventCursor<HeavyMotherRow> heavyMothers(view.tree[kHeavyMothers]);EventCursor<OriginRow> origins(view.tree[kOrigins]);EventCursor<PairRow> pairs(view.tree[kPairs]);EventCursor<TriggerRow> triggers(view.tree[kTriggers]);
  std::vector<ULong64_t> eventCount(sources.size());std::vector<double> sw(sources.size()),sw2(sources.size()),saw(sources.size());
  EventRow event;Read(*view.tree[kEvents],event);
  for(Long64_t entry=0;entry<view.tree[kEvents]->GetEntries();++entry){
    if(view.tree[kEvents]->GetEntry(entry)<=0)throw std::runtime_error("cannot read event row");
    if(!std::isfinite(event.weight)||!std::isfinite(event.pthat)||!std::isfinite(event.hard_scale)||event.a15_eta1<0||event.a15_eta4<0||event.pthat<0||event.hard_scale<0||event.n_mpi<0)throw std::runtime_error("event value contract differs");
    const UInt_t sid=sourceFor(event.event_id);++eventCount[sid];sw[sid]+=event.weight;sw2[sid]+=event.weight*event.weight;saw[sid]+=std::abs(event.weight);++observed[sid][kEvents];

    const auto eventHard=hard.Take(event.event_id);for(const auto&r:eventHard){for(double value:{r.px,r.py,r.pz,r.energy})if(!std::isfinite(value))throw std::runtime_error("hard value contract differs");}observed[sid][kHard]+=eventHard.size();
    const auto eventHeavy=heavy.Take(event.event_id);std::map<Int_t,HeavyRow> heavyMap;
    for(const auto&h:eventHeavy){if(!std::isfinite(h.px)||!std::isfinite(h.py)||!std::isfinite(h.pz)||!std::isfinite(h.energy)||!std::isfinite(h.mass)||!std::isfinite(h.pt)||!std::isfinite(h.eta)||!std::isfinite(h.rapidity)||!std::isfinite(h.phi)||h.energy<0||h.mass<0||h.pt<0||h.final>1||h.selected>1||h.pair_eligible>1||h.is_meson>1||h.is_baryon>1||h.is_meson==h.is_baryon||h.open>1||h.hidden>1)throw std::runtime_error("heavy row contract differs");const auto* state=Hadronization::FindSelectedState(h.pdg);const auto content=Hadronization::DecodeHeavyContent(h.pdg,h.is_meson!=0,h.is_baryon!=0);const int category=static_cast<int>(Hadronization::ClassifyHeavyStateDetailed(state!=nullptr,content,h.is_meson!=0,h.spin));if(h.selected!=(state?1:0)||h.pair_eligible!=(state&&state->pairAnalysisEligible?1:0)||h.category!=category||h.nc!=content.nc||h.ncbar!=content.ncbar||h.nb!=content.nb||h.nbbar!=content.nbbar||h.qc!=content.qc()||h.qb!=content.qb()||h.baryon3!=(h.is_baryon?(h.pdg>0?3:-3):0)||h.strangeness!=content.strangeness()||h.open!=((h.qc!=0||h.qb!=0)?1:0)||h.hidden!=((content.hiddenCharm()||content.hiddenBeauty())?1:0)||(state&&(h.charge3!=state->charge3||h.spin!=state->spin2j1))||!heavyMap.emplace(h.heavy_index,h).second)throw std::runtime_error("heavy registry/content cache/key differs");}observed[sid][kHeavy]+=eventHeavy.size();
    const auto eventOrigins=origins.Take(event.event_id);std::map<std::pair<Int_t,Int_t>,OriginRow> originMap;
    for(const auto&o:eventOrigins){const auto found=heavyMap.find(o.heavy_index);if(found==heavyMap.end()||(o.sector!=4&&o.sector!=5)||!originMap.emplace(std::make_pair(o.heavy_index,o.sector),o).second)throw std::runtime_error("origin foreign key/domain differs");ValidateOriginDecision(o.origin,o.resolution,o.matched_hard,o.rejected_hard,o.depth,SectorCharge(found->second,o.sector)!=0);}
    for(const auto&item:heavyMap)for(int sector:{4,5})if(!originMap.count({item.first,sector}))throw std::runtime_error("origin sector coverage differs");
    if(eventOrigins.size()!=2*eventHeavy.size())throw std::runtime_error("origin sector coverage differs");
    observed[sid][kOrigins]+=eventOrigins.size();

    const auto eventTriggers=triggers.Take(event.event_id);std::vector<TriggerRow> expectedTriggers;std::vector<TriggerRow> accepted;
    for(const auto&item:heavyMap){const int sector=TriggerSector(item.second.pdg);if(!sector)continue;const auto&origin=originMap.at({item.first,sector});TriggerRow expected{event.event_id,item.first,sector,TriggerMask(item.second,origin,sector)};expectedTriggers.push_back(expected);if(expected.rejection_mask==0)accepted.push_back(expected);}
    if(eventTriggers.size()!=expectedTriggers.size())throw std::runtime_error("trigger candidate coverage differs");
    for(std::size_t i=0;i<eventTriggers.size();++i)if(!SameRow(eventTriggers[i],expectedTriggers[i]))throw std::runtime_error("trigger rejection mask/coverage differs");
    observed[sid][kTriggers]+=eventTriggers.size();

    const auto eventAncestry=ancestry.Take(event.event_id);std::set<Int_t> ancestryKeys;for(const auto&r:eventAncestry)if(!ancestryKeys.insert(r.node_index).second)throw std::runtime_error("ancestry key differs");observed[sid][kAncestry]+=eventAncestry.size();
    const auto eventAncestryMothers=ancestryMothers.Take(event.event_id);for(const auto&r:eventAncestryMothers)if(!ancestryKeys.count(r.node_index))throw std::runtime_error("ancestry mother foreign key differs");observed[sid][kAncestryMothers]+=eventAncestryMothers.size();
    const auto eventHeavyMothers=heavyMothers.Take(event.event_id);for(const auto&r:eventHeavyMothers)if(!heavyMap.count(r.heavy_index))throw std::runtime_error("heavy mother foreign key differs");observed[sid][kHeavyMothers]+=eventHeavyMothers.size();
    const auto eventConstituents=constituents.Take(event.event_id);for(const auto&r:eventConstituents){if(!heavyMap.count(r.heavy_index)||(std::abs(r.signed_flavour)!=4&&std::abs(r.signed_flavour)!=5))throw std::runtime_error("constituent foreign key/domain differs");ValidateOriginDecision(r.origin,r.resolution,r.matched_hard,r.rejected_hard,r.depth,true);}observed[sid][kConstituents]+=eventConstituents.size();
    const auto eventCompatibility=compatibility.Take(event.event_id);for(const auto&r:eventCompatibility){const bool domain=(r.diagnostic_id<2&&r.cell_id<128)||(r.diagnostic_id==2&&r.cell_id<6)||(r.diagnostic_id==3&&r.cell_id<9);if(!domain||r.value==0)throw std::runtime_error("compatibility sparse domain differs");}observed[sid][kEventCompatibility]+=eventCompatibility.size();

    std::vector<PairRow> expectedPairs;std::vector<ClosureRow> expectedClosure;
    for(const auto&trigger:accepted){const HeavyRow&th=heavyMap.at(trigger.heavy_index);const OriginRow&to=originMap.at({trigger.heavy_index,trigger.sector});const int tq=SectorCharge(th,trigger.sector);for(const auto&item:heavyMap){const HeavyRow&ah=item.second;if(ah.heavy_index==th.heavy_index)continue;const int aq=SectorCharge(ah,trigger.sector);if(ah.final&&aq!=0)expectedClosure.push_back({event.event_id,th.heavy_index,ah.heavy_index,-tq*aq,static_cast<UChar_t>(std::abs(ah.eta)<=4.0),DenseCategory(ah.category)});const auto* state=Hadronization::FindSelectedState(ah.pdg);if(!state||((trigger.sector==4)!=(state->sector=="charm"))||!ah.final||!ah.selected||!Hadronization::IsDirectPrimaryStatus(ah.status))continue;const OriginRow&ao=originMap.at({ah.heavy_index,trigger.sector});const int dense=PairOrigin(ao,aq,tq,to.matched_hard);if(!dense)continue;expectedPairs.push_back({event.event_id,th.heavy_index,ah.heavy_index,(tq*aq<0?-1:1),Hadronization::WrapDeltaPhi(th.phi,ah.phi),th.eta-ah.eta,th.pt,ah.pt,event.a15_eta1,event.a15_eta4,dense,ah.category,event.weight});}}
    const auto eventPairs=pairs.Take(event.event_id);if(eventPairs.size()!=expectedPairs.size())throw std::runtime_error("pair coverage differs");for(std::size_t i=0;i<eventPairs.size();++i)if(!SameRow(eventPairs[i],expectedPairs[i]))throw std::runtime_error("pair cached authority/semantics differs");observed[sid][kPairs]+=eventPairs.size();
    const auto eventClosure=closure.Take(event.event_id);if(eventClosure.size()!=expectedClosure.size())throw std::runtime_error("closure coverage differs");for(std::size_t i=0;i<eventClosure.size();++i)if(!SameRow(eventClosure[i],expectedClosure[i]))throw std::runtime_error("closure coefficient/visibility/category differs");observed[sid][kClosure]+=eventClosure.size();
  }
  view.tree[kEvents]->ResetBranchAddresses();ancestry.Finish();ancestryMothers.Finish();closure.Finish();constituents.Finish();compatibility.Finish();hard.Finish();heavy.Finish();heavyMothers.Finish();origins.Finish();pairs.Finish();triggers.Finish();
  for(std::size_t i=0;i<sources.size();++i)if(eventCount[i]!=sources[i].events||!BitsEqual(sw[i],sources[i].sumw)||!BitsEqual(sw2[i],sources[i].sumw2)||!BitsEqual(saw[i],sources[i].sumabsw))throw std::runtime_error("source event/weight accounting differs");
  std::map<std::pair<UInt_t,UInt_t>,ULong64_t> expectedCounts;for(const auto&r:declared){if(r.source_id>=sources.size()||r.family_id>=kFamilyCount||!expectedCounts.emplace(std::make_pair(r.source_id,r.family_id),r.rows).second)throw std::runtime_error("source count key/domain differs");}
  for(const auto&item:observed)for(std::size_t family=0;family<kFamilyCount;++family)if(expectedCounts.at({item.first,static_cast<UInt_t>(family)})!=item.second[family])throw std::runtime_error(std::string("source family counts differ: ")+kTableNames[family]);
}

struct VerificationResult {std::string digest;std::array<ULong64_t,kFamilyCount> rows{};std::vector<std::string> sourceDigests;};

VerificationResult Verify(const std::string& path,bool requireContract=true){RootView view(path);const auto content=DigestAndOrder(view);const auto sourceDigests=SourceDigests(view);ValidateSemantics(view);auto* object=dynamic_cast<TObjString*>(view.file.Get("contract"));if(!object)throw std::runtime_error("missing contract object");const std::string contract=object->GetString().Data();if(contract.find(std::string("\"schema_digest\":\"")+kSchemaDigest+"\"")==std::string::npos||contract.find(std::string("\"registries_digest\":\"")+kRegistriesDigest+"\"")==std::string::npos||contract.find("\"completion\":\"COMPLETE_INDEPENDENT_SHARD\"")==std::string::npos)throw std::runtime_error("contract identity/completion differs");if(requireContract&&(ExtractDigest(contract)!=content.first||contract.find("\"source_scientific_digests\":"+DigestListJson(sourceDigests))==std::string::npos))throw std::runtime_error("scientific content digest differs");return {content.first,content.second,sourceDigests};}

void Summary(const VerificationResult& result){std::cout<<"ANALYSIS_SUMMARY scientific_digest="<<result.digest<<" source_digests=";for(std::size_t i=0;i<result.sourceDigests.size();++i){if(i)std::cout<<',';std::cout<<result.sourceDigests[i];}for(std::size_t i=0;i<kFamilyCount;++i)std::cout<<" rows_"<<kTableNames[i]<<'='<<result.rows[i];std::cout<<'\n';}

std::string BindingJson(const std::string& path) {
  RootView view(path);
  const auto sources = LoadRows<SourceRow>(view.tree[kSources]);
  const auto blocks = LoadRows<SourceBlockRow>(view.tree[kSourceBlocks]);
  const auto ranges = LoadRows<EventRangeRow>(view.tree[kEventRanges]);
  auto* object = dynamic_cast<TObjString*>(view.file.Get("contract"));
  if (!object) throw std::runtime_error("missing contract object");
  std::ostringstream out;
  out << "{\"contract\":" << object->GetString().Data() << ",\"event_ranges\":[";
  for (std::size_t i = 0; i < ranges.size(); ++i) {
    if (i) out << ',';
    out << "{\"count\":" << ranges[i].count << ",\"first_id\":"
        << ranges[i].first_id << ",\"source_id\":" << ranges[i].source_id << '}';
  }
  out << "],\"source_blocks\":[";
  for (std::size_t i = 0; i < blocks.size(); ++i) {
    if (i) out << ',';
    out << "{\"assignment_id\":" << blocks[i].assignment_id << ",\"block\":"
        << blocks[i].block << ",\"source_id\":" << blocks[i].source_id << '}';
  }
  out << "],\"sources\":[";
  for (std::size_t i = 0; i < sources.size(); ++i) {
    if (i) out << ',';
    out << "{\"attempt\":" << sources[i].attempt << ",\"events\":"
        << sources[i].events << ",\"logical_id\":" << sources[i].logical_id
        << ",\"source_id\":" << sources[i].source_id << ",\"tune\":"
        << sources[i].tune << '}';
  }
  out << "]}";
  return out.str();
}

void WriteShard(const std::string& specPath,const std::string& outputPath,const std::string& contractPath){
  const auto specs=LoadSpecs(specPath);if(std::ifstream existing(outputPath);existing.good())throw std::runtime_error("output path already exists");
  TFile output(outputPath.c_str(),"CREATE","lossless analysis shard");
  if(output.IsZombie())throw std::runtime_error("cannot create unique analysis output");
  output.SetCompressionAlgorithm(ROOT::RCompressionSetting::EAlgorithm::kZSTD);
  output.SetCompressionLevel(5);
  Trees trees(output);
  SourceMetadataBuilder metadata;
  for(const auto&s:specs){std::ifstream bytes(s.path,std::ios::binary|std::ios::ate);if(!bytes||static_cast<ULong64_t>(bytes.tellg())!=s.bytes)throw std::runtime_error("raw physical size differs");TFile raw(s.path.c_str(),"READ");if(raw.IsZombie())throw std::runtime_error("raw source is unreadable");ValidateMetadata(raw,s,trees.sources);auto* tree=dynamic_cast<TTree*>(raw.Get("tree"));RawEvent event;BindRaw(tree,event);std::array<ULong64_t,kFamilyCount> counts{};trees.sources.sumabsw=0;for(ULong64_t local=0;local<s.events;++local){if(tree->GetEntry(static_cast<Long64_t>(local))<=0)throw std::runtime_error("cannot read raw event");const ULong64_t eventId=Hadronization::EventId(static_cast<int>(s.campaignOrdinal),static_cast<int>(s.tuneOrdinal),static_cast<int>(s.logicalId),static_cast<int>(s.attempt),local);ProcessEvent(trees,counts,event,eventId);trees.sources.sumabsw+=std::abs(event.weight);if((local+1)%kEventFlushInterval==0)trees.FlushBaskets();}tree->ResetBranchAddresses();if(!std::isfinite(trees.sources.sumabsw))throw std::runtime_error("invalid sumabsw");trees.Fill(kSources,trees.sources);counts[kSources]=1;trees.ranges={Hadronization::EventId(static_cast<int>(s.campaignOrdinal),static_cast<int>(s.tuneOrdinal),static_cast<int>(s.logicalId),static_cast<int>(s.attempt),0),s.events,s.sourceId};trees.Fill(kEventRanges,trees.ranges);counts[kEventRanges]=1;trees.sourceBlocks={s.sourceId,0,s.block};trees.Fill(kSourceBlocks,trees.sourceBlocks);counts[kSourceBlocks]=1;counts[kSourceCounts]=kFamilyCount;for(UInt_t family=0;family<kFamilyCount;++family){trees.sourceCounts={s.sourceId,family,counts[family]};trees.Fill(kSourceCounts,trees.sourceCounts);}metadata.Add(raw,dynamic_cast<TTree*>(raw.Get("job_metadata")),s);trees.FlushBaskets();raw.Close();}
  output.cd();
  if (output.Write() <= 0) throw std::runtime_error("failed to write output trees");
  output.Close();
  {TFile check(outputPath.c_str(),"READ");if(check.IsZombie())throw std::runtime_error("cannot reopen staged shard");for(const char* name:kTableNames)if(!check.Get(name))throw std::runtime_error("staged shard lost a tree on close");}
  RootView incomplete(outputPath,false);const auto content=DigestAndOrder(incomplete);const auto sourceDigests=SourceDigests(incomplete);ValidateSemantics(incomplete);incomplete.file.Close();std::string contract=ReadFile(contractPath);ReplaceExactlyOne(contract,std::string(64,'X'),content.first);ReplaceExactlyOne(contract,"\"__SOURCE_DIGESTS__\"",DigestListJson(sourceDigests));ReplaceExactlyOne(contract,"\"__SOURCE_METADATA__\"",metadata.Json());TFile update(outputPath.c_str(),"UPDATE");if(update.IsZombie())throw std::runtime_error("cannot add staged contract");TObjString object(contract.c_str());if(object.Write("contract")<=0)throw std::runtime_error("cannot write contract object");update.Close();Summary(Verify(outputPath));
}

}  // namespace

int main(int argc,char**argv){try{if(argc==3&&std::string(argv[1])=="inspect-raw"){std::cout<<InspectRaw(argv[2])<<'\n';return 0;}if(argc==3&&std::string(argv[1])=="verify"){Summary(Verify(argv[2]));return 0;}if(argc==3&&std::string(argv[1])=="binding"){std::cout<<BindingJson(argv[2])<<'\n';return 0;}if(argc==5&&std::string(argv[1])=="write"){WriteShard(argv[2],argv[3],argv[4]);return 0;}throw std::runtime_error("usage: analyze {inspect-raw RAW|verify SHARD|binding SHARD|write SPEC OUTPUT CONTRACT}");}catch(const std::exception&error){std::cerr<<"ANALYSIS_ERROR "<<error.what()<<'\n';return 2;}}
