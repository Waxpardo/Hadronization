#include "statistics.hpp"
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
#include <locale>
#include <map>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <tuple>
#include <unordered_map>
#include <utility>
#include <vector>

namespace HR = Hadronization::Reduction;

namespace {

constexpr const char* kSpecSchema = "hadronization_reduction_spec_v1";
constexpr const char* kCompactSchema = "hadronization_compact_plot_source_v1";
constexpr double kPi = 3.141592653589793238462643383279502884;

class Sha256 {
 public:
  Sha256() { Reset(); }
  void Update(const void* input, std::size_t size) {
    const auto* bytes = static_cast<const std::uint8_t*>(input);
    bitLength_ += static_cast<std::uint64_t>(size) * 8U;
    while (size > 0) {
      const std::size_t take = std::min(size, block_.size() - blockSize_);
      std::memcpy(block_.data() + blockSize_, bytes, take);
      blockSize_ += take;
      bytes += take;
      size -= take;
      if (blockSize_ == block_.size()) {
        Transform(block_.data());
        blockSize_ = 0;
      }
    }
  }
  void Update(const std::string& value) { Update(value.data(), value.size()); }
  std::string FinalHex() {
    const std::uint64_t originalBits = bitLength_;
    const std::uint8_t one = 0x80;
    Update(&one, 1);
    const std::uint8_t zero = 0;
    while (blockSize_ != 56) Update(&zero, 1);
    std::array<std::uint8_t, 8> length{};
    for (int index = 0; index < 8; ++index) {
      length[7 - index] = static_cast<std::uint8_t>(originalBits >> (index * 8));
    }
    Update(length.data(), length.size());
    std::ostringstream output;
    output << std::hex << std::setfill('0');
    for (const std::uint32_t word : state_) output << std::setw(8) << word;
    return output.str();
  }
 private:
  static std::uint32_t Rotate(std::uint32_t value, unsigned amount) {
    return (value >> amount) | (value << (32U - amount));
  }
  void Reset() {
    state_ = {0x6a09e667U, 0xbb67ae85U, 0x3c6ef372U, 0xa54ff53aU,
              0x510e527fU, 0x9b05688cU, 0x1f83d9abU, 0x5be0cd19U};
    blockSize_ = 0;
    bitLength_ = 0;
  }
  void Transform(const std::uint8_t* block) {
    static constexpr std::array<std::uint32_t, 64> constants{{
      0x428a2f98U,0x71374491U,0xb5c0fbcfU,0xe9b5dba5U,0x3956c25bU,0x59f111f1U,0x923f82a4U,0xab1c5ed5U,
      0xd807aa98U,0x12835b01U,0x243185beU,0x550c7dc3U,0x72be5d74U,0x80deb1feU,0x9bdc06a7U,0xc19bf174U,
      0xe49b69c1U,0xefbe4786U,0x0fc19dc6U,0x240ca1ccU,0x2de92c6fU,0x4a7484aaU,0x5cb0a9dcU,0x76f988daU,
      0x983e5152U,0xa831c66dU,0xb00327c8U,0xbf597fc7U,0xc6e00bf3U,0xd5a79147U,0x06ca6351U,0x14292967U,
      0x27b70a85U,0x2e1b2138U,0x4d2c6dfcU,0x53380d13U,0x650a7354U,0x766a0abbU,0x81c2c92eU,0x92722c85U,
      0xa2bfe8a1U,0xa81a664bU,0xc24b8b70U,0xc76c51a3U,0xd192e819U,0xd6990624U,0xf40e3585U,0x106aa070U,
      0x19a4c116U,0x1e376c08U,0x2748774cU,0x34b0bcb5U,0x391c0cb3U,0x4ed8aa4aU,0x5b9cca4fU,0x682e6ff3U,
      0x748f82eeU,0x78a5636fU,0x84c87814U,0x8cc70208U,0x90befffaU,0xa4506cebU,0xbef9a3f7U,0xc67178f2U}};
    std::array<std::uint32_t, 64> words{};
    for (std::size_t index = 0; index < 16; ++index) {
      words[index] = (static_cast<std::uint32_t>(block[index * 4]) << 24U) |
                     (static_cast<std::uint32_t>(block[index * 4 + 1]) << 16U) |
                     (static_cast<std::uint32_t>(block[index * 4 + 2]) << 8U) |
                     static_cast<std::uint32_t>(block[index * 4 + 3]);
    }
    for (std::size_t index = 16; index < words.size(); ++index) {
      const std::uint32_t s0 = Rotate(words[index - 15], 7) ^
                               Rotate(words[index - 15], 18) ^
                               (words[index - 15] >> 3U);
      const std::uint32_t s1 = Rotate(words[index - 2], 17) ^
                               Rotate(words[index - 2], 19) ^
                               (words[index - 2] >> 10U);
      words[index] = words[index - 16] + s0 + words[index - 7] + s1;
    }
    auto working = state_;
    for (std::size_t index = 0; index < words.size(); ++index) {
      const std::uint32_t s1 = Rotate(working[4], 6) ^ Rotate(working[4], 11) ^ Rotate(working[4], 25);
      const std::uint32_t choose = (working[4] & working[5]) ^ (~working[4] & working[6]);
      const std::uint32_t temporary1 = working[7] + s1 + choose + constants[index] + words[index];
      const std::uint32_t s0 = Rotate(working[0], 2) ^ Rotate(working[0], 13) ^ Rotate(working[0], 22);
      const std::uint32_t majority = (working[0] & working[1]) ^ (working[0] & working[2]) ^ (working[1] & working[2]);
      const std::uint32_t temporary2 = s0 + majority;
      working[7] = working[6]; working[6] = working[5]; working[5] = working[4];
      working[4] = working[3] + temporary1; working[3] = working[2];
      working[2] = working[1]; working[1] = working[0]; working[0] = temporary1 + temporary2;
    }
    for (std::size_t index = 0; index < state_.size(); ++index) state_[index] += working[index];
  }
  std::array<std::uint32_t, 8> state_{};
  std::array<std::uint8_t, 64> block_{};
  std::size_t blockSize_ = 0;
  std::uint64_t bitLength_ = 0;
};

std::string Sha(const std::string& value) {
  Sha256 digest;
  digest.Update(value);
  return digest.FinalHex();
}

std::vector<std::string> Split(const std::string& line, char delimiter = '\t') {
  std::vector<std::string> values;
  std::size_t start = 0;
  while (true) {
    const std::size_t at = line.find(delimiter, start);
    values.push_back(line.substr(start, at == std::string::npos ? at : at - start));
    if (at == std::string::npos) return values;
    start = at + 1;
  }
}

std::string HexDecode(const std::string& value) {
  if (value.size() % 2 != 0) throw std::runtime_error("odd hex field");
  std::string result(value.size() / 2, '\0');
  const auto digit = [](char character) -> int {
    if (character >= '0' && character <= '9') return character - '0';
    if (character >= 'a' && character <= 'f') return character - 'a' + 10;
    throw std::runtime_error("invalid lowercase hex field");
  };
  for (std::size_t index = 0; index < result.size(); ++index) {
    result[index] = static_cast<char>((digit(value[index * 2]) << 4) |
                                      digit(value[index * 2 + 1]));
  }
  return result;
}

std::string HexEncode(const std::string& value) {
  static constexpr char digits[] = "0123456789abcdef";
  std::string result;
  result.reserve(value.size() * 2);
  for (const unsigned char character : value) {
    result.push_back(digits[character >> 4U]);
    result.push_back(digits[character & 0x0fU]);
  }
  return result;
}

double Double(const std::string& value) {
  std::size_t consumed = 0;
  const double result = std::stod(value, &consumed);
  if (consumed != value.size() || !std::isfinite(result)) {
    throw std::runtime_error("invalid finite floating field");
  }
  return result;
}

long long Integer(const std::string& value) {
  std::size_t consumed = 0;
  const long long result = std::stoll(value, &consumed);
  if (consumed != value.size()) throw std::runtime_error("invalid integer field");
  return result;
}

std::string JsonEscape(const std::string& value) {
  std::ostringstream output;
  for (const unsigned char character : value) {
    switch (character) {
      case '"': output << "\\\""; break;
      case '\\': output << "\\\\"; break;
      case '\b': output << "\\b"; break;
      case '\f': output << "\\f"; break;
      case '\n': output << "\\n"; break;
      case '\r': output << "\\r"; break;
      case '\t': output << "\\t"; break;
      default:
        if (character < 0x20U) {
          output << "\\u" << std::hex << std::setw(4) << std::setfill('0')
                 << static_cast<int>(character) << std::dec;
        } else {
          output << static_cast<char>(character);
        }
    }
  }
  return output.str();
}

void ReplaceOne(std::string& value, const std::string& target,
                const std::string& replacement) {
  const std::size_t at = value.find(target);
  if (at == std::string::npos || value.find(target, at + target.size()) != std::string::npos) {
    throw std::runtime_error("template placeholder cardinality differs: " + target);
  }
  value.replace(at, target.size(), replacement);
}

void ReplaceAll(std::string& value, const std::string& target,
                const std::string& replacement) {
  std::size_t at = 0;
  std::size_t count = 0;
  while ((at = value.find(target, at)) != std::string::npos) {
    value.replace(at, target.size(), replacement);
    at += replacement.size();
    ++count;
  }
  if (count == 0) {
    throw std::runtime_error("template placeholder is absent: " + target);
  }
}

std::string DoubleHex(double value) {
  if (!std::isfinite(value)) throw std::runtime_error("nonfinite compact value");
  std::ostringstream output;
  output.imbue(std::locale::classic());
  output << std::hexfloat << value;
  return output.str();
}

std::string JsonDouble(double value) {
  if (!std::isfinite(value)) throw std::runtime_error("nonfinite JSON value");
  std::ostringstream output;
  output.imbue(std::locale::classic());
  output << std::setprecision(std::numeric_limits<double>::max_digits10) << value;
  return output.str();
}

void DigestField(Sha256& digest, const std::string& value) {
  std::array<unsigned char, 8> size{};
  std::uint64_t length = value.size();
  for (int index = 0; index < 8; ++index) {
    size[7 - index] = static_cast<unsigned char>(length >> (index * 8));
  }
  digest.Update(size.data(), size.size());
  digest.Update(value);
}

struct Accumulator {
  double sum = 0.0;
  double correction = 0.0;
  double sumabs = 0.0;
  double sumabsCorrection = 0.0;
  double sumw2 = 0.0;
  double sumw2Correction = 0.0;
  std::uint64_t fills = 0;
  void Add(double value) {
    if (!std::isfinite(value)) throw std::runtime_error("nonfinite contribution");
    auto compensatedAdd=[](double contribution,double& total,double& residual){
      const double next=total+contribution;
      if(std::abs(total)>=std::abs(contribution))residual+=(total-next)+contribution;
      else residual+=(contribution-next)+total;
      total=next;
    };
    compensatedAdd(value,sum,correction);
    compensatedAdd(std::abs(value),sumabs,sumabsCorrection);
    compensatedAdd(value*value,sumw2,sumw2Correction);
    ++fills;
    if (!std::isfinite(sum) || !std::isfinite(correction) ||
        !std::isfinite(sumabs) || !std::isfinite(sumabsCorrection) ||
        !std::isfinite(sumw2) || !std::isfinite(sumw2Correction)) {
      throw std::runtime_error("nonfinite numerical accumulation");
    }
  }
  double Value() const { return sum + correction; }
  double SumAbs() const { return sumabs + sumabsCorrection; }
  double SumW2() const { return sumw2 + sumw2Correction; }
  double ErrorBound() const {
    if (fills < 2) return 0.0;
    constexpr double unit = 0x1p-53;
    const double operations = static_cast<double>(2 * fills + 2);
    if (operations * unit >= 1.0) return std::numeric_limits<double>::infinity();
    return operations * unit / (1.0 - operations * unit) * SumAbs();
  }
};

struct CellKey {
  std::uint32_t projection = 0, scope = 0, block = 0, bin = 0, component = 0;
  auto Tie() const { return std::tie(projection, scope, block, bin, component); }
  bool operator<(const CellKey& other) const { return Tie() < other.Tie(); }
};

struct GramKey {
  std::uint32_t projection = 0, scope = 0, block = 0, left = 0, right = 0;
  auto Tie() const { return std::tie(projection, scope, block, left, right); }
  bool operator<(const GramKey& other) const { return Tie() < other.Tie(); }
};

struct GramFamily {
  int opposite = 0;
  int same = 0;
  int trigger = 0;
  int referenceOpposite = 0;
  int referenceSame = 0;
};

struct Profile { int id = 0; std::string name; bool triggerCut = false, associateCut = false; double triggerPt = 0.0, associatePt = 0.0; };
struct Activity { int id = 0; std::string name, field; };
struct Class { int id = 0, lowPercent = 0, highPercent = 100; bool integrated = false; };
struct State { int pdg = 0; std::string id, sector; bool eligible = false; int qc = 0, qb = 0; };
struct Pair { int id = 0, trigger = 0, associate = 0, sign = 0, reference = 0; bool central = false; };
struct Correlation { int id = 0, trigger = 0, associate = 0; };
struct Scope { int id = 0; std::string family, tune, profile, activity; int classId = -1; };
struct Source { int shard = 0, local = 0, global = 0, tune = 0, block = 0; std::uint64_t logical = 0; unsigned attempt = 0; std::uint64_t events = 0; std::string tuneName, manifest; };
struct Shard { int ordinal = 0; std::string path, scientificDigest; int sourceCount = 0; std::uint64_t rows = 0; std::map<std::string, std::uint64_t> rowCounts; std::vector<Source> sources; };

struct Spec {
  std::map<std::string, std::string> settings;
  std::vector<double> ptEdges;
  std::vector<Profile> profiles;
  std::vector<Activity> activities;
  std::vector<Class> classes;
  std::vector<State> states;
  std::vector<Pair> pairs;
  std::vector<Correlation> correlations;
  std::vector<int> g9;
  std::vector<Scope> scopes;
  std::vector<Shard> shards;
};

const std::map<std::string, std::string>& ExpectedSchemas();

Spec ReadSpec(const std::string& path) {
  std::ifstream input(path);
  if (!input) throw std::runtime_error("cannot open reduction spec");
  std::string line;
  if (!std::getline(input, line) || line != kSpecSchema) {
    throw std::runtime_error("reduction spec schema differs");
  }
  Spec spec;
  bool ended = false;
  while (std::getline(input, line)) {
    if (line.empty()) throw std::runtime_error("empty reduction spec line");
    const auto fields = Split(line);
    if (fields[0] == "END" && fields.size() == 1) { ended = true; break; }
    if (fields[0] == "SETTING" && fields.size() == 3) {
      if (!spec.settings.emplace(fields[1], fields[2]).second) throw std::runtime_error("duplicate setting");
    } else if (fields[0] == "PTEDGE" && fields.size() == 2) {
      spec.ptEdges.push_back(Double(fields[1]));
    } else if (fields[0] == "PROFILE" && fields.size() == 5) {
      Profile value; value.id = Integer(fields[1]); value.name = fields[2];
      value.triggerCut = fields[3] != "NONE"; value.associateCut = fields[4] != "NONE";
      if (value.triggerCut) value.triggerPt = Double(fields[3]);
      if (value.associateCut) value.associatePt = Double(fields[4]);
      spec.profiles.push_back(value);
    } else if (fields[0] == "ACTIVITY" && fields.size() == 4) {
      spec.activities.push_back({static_cast<int>(Integer(fields[1])), fields[2], fields[3]});
    } else if (fields[0] == "CLASS" && fields.size() == 5) {
      spec.classes.push_back({static_cast<int>(Integer(fields[1])), static_cast<int>(Integer(fields[2])), static_cast<int>(Integer(fields[3])), Integer(fields[4]) != 0});
    } else if (fields[0] == "STATE" && fields.size() == 7) {
      spec.states.push_back({static_cast<int>(Integer(fields[1])), fields[2], fields[3], Integer(fields[4]) != 0, static_cast<int>(Integer(fields[5])), static_cast<int>(Integer(fields[6]))});
    } else if (fields[0] == "PAIR" && fields.size() == 7) {
      spec.pairs.push_back({static_cast<int>(Integer(fields[1])), static_cast<int>(Integer(fields[2])), static_cast<int>(Integer(fields[3])), static_cast<int>(Integer(fields[4])), static_cast<int>(Integer(fields[5])), Integer(fields[6]) != 0});
    } else if (fields[0] == "CORRELATION" && fields.size() == 4) {
      spec.correlations.push_back({static_cast<int>(Integer(fields[1])), static_cast<int>(Integer(fields[2])), static_cast<int>(Integer(fields[3]))});
    } else if (fields[0] == "G9" && fields.size() == 2) {
      spec.g9.push_back(static_cast<int>(Integer(fields[1])));
    } else if (fields[0] == "SCOPE" && fields.size() == 7) {
      spec.scopes.push_back({static_cast<int>(Integer(fields[1])), fields[2], fields[3], fields[4], fields[5], static_cast<int>(Integer(fields[6]))});
    } else if (fields[0] == "SHARD" && fields.size() == 6) {
      spec.shards.push_back({static_cast<int>(Integer(fields[1])), HexDecode(fields[2]), fields[3], static_cast<int>(Integer(fields[4])), static_cast<std::uint64_t>(Integer(fields[5])), {}, {}});
    } else if (fields[0] == "ROW" && fields.size() == 4) {
      if (spec.shards.empty() || spec.shards.back().ordinal != Integer(fields[1]) ||
          !spec.shards.back().rowCounts.emplace(fields[2], static_cast<std::uint64_t>(Integer(fields[3]))).second) {
        throw std::runtime_error("row accounting precedes its shard or is duplicated");
      }
    } else if (fields[0] == "SOURCE" && fields.size() == 11) {
      if (spec.shards.empty() || spec.shards.back().ordinal != Integer(fields[1])) throw std::runtime_error("source precedes owning shard");
      Source source;
      source.shard = Integer(fields[1]); source.local = Integer(fields[2]); source.global = Integer(fields[3]);
      source.tune = Integer(fields[4]); source.block = Integer(fields[5]); source.logical = Integer(fields[6]);
      source.attempt = Integer(fields[7]); source.events = Integer(fields[8]);
      source.tuneName = HexDecode(fields[9]); source.manifest = HexDecode(fields[10]);
      spec.shards.back().sources.push_back(source);
    } else {
      throw std::runtime_error("unknown or malformed reduction spec record");
    }
  }
  if (!ended || input.peek() != std::ifstream::traits_type::eof()) throw std::runtime_error("reduction spec has trailing/missing END");
  const std::set<std::string> expectedSettings = {
      "analysis_sha256", "plan_digest", "map_digest", "parent_shard_set_digest",
      "publication_state", "block_count", "activity_bins", "dphi_bins",
      "dphi_low", "dphi_high", "eta_low", "eta_high", "phi_low", "phi_high",
      "compact_domains_template", "input_lineage", "input_lineage_sha256",
      "metadata_template", "receipt_template"};
  std::set<std::string> observed;
  for (const auto& item : spec.settings) observed.insert(item.first);
  if (observed != expectedSettings || spec.profiles.empty() ||
      spec.profiles.size() > 16 ||
      spec.activities.size() != 2 || spec.pairs.size() != 300 ||
      spec.correlations.size() != 4 || spec.g9.size() != 10 ||
      spec.shards.empty() || spec.ptEdges.size() < 2) {
    throw std::runtime_error("reduction spec completeness differs");
  }
  for (const auto& shard : spec.shards) {
    std::set<std::string> rowNames;
    for (const auto& item : shard.rowCounts) rowNames.insert(item.first);
    std::set<std::string> expectedRowNames;
    for (const auto& item : ExpectedSchemas()) expectedRowNames.insert(item.first);
    if (shard.sources.size() != static_cast<std::size_t>(shard.sourceCount) ||
        rowNames != expectedRowNames) throw std::runtime_error("shard source/row accounting differs");
  }
  return spec;
}

const std::map<std::string, std::string>& ExpectedSchemas() {
  static const std::map<std::string, std::string> schemas = {
    {"ancestry","event_id:ULong64_t,node_index:Int_t,pdg:Int_t,status:Int_t,mother1:Int_t,mother2:Int_t"},
    {"ancestry_mothers","event_id:ULong64_t,node_index:Int_t,edge_ordinal:UInt_t,mother_index:Int_t"},
    {"closure","event_id:ULong64_t,trigger_heavy_index:Int_t,associate_heavy_index:Int_t,coefficient:Int_t,visible:UChar_t,dense_category:Int_t"},
    {"constituents","event_id:ULong64_t,heavy_index:Int_t,signed_flavour:Int_t,constituent_ordinal:UInt_t,origin:Int_t,resolution:Int_t,matched_hard:Int_t,rejected_hard:Int_t,depth:Int_t"},
    {"event_compatibility","event_id:ULong64_t,diagnostic_id:UInt_t,cell_id:UInt_t,value:Int_t"},
    {"event_ranges","first_id:ULong64_t,count:ULong64_t,source_id:UInt_t"},
    {"events","event_id:ULong64_t,weight:Double_t,a15_eta1:Int_t,a15_eta4:Int_t,process_code:Int_t,pthat:Double_t,hard_scale:Double_t,n_mpi:Int_t"},
    {"hard","event_id:ULong64_t,root_index:Int_t,bottom_index:Int_t,pdg:Int_t,status:Int_t,bottom_pdg:Int_t,bottom_status:Int_t,px:Double_t,py:Double_t,pz:Double_t,energy:Double_t"},
    {"heavy","event_id:ULong64_t,heavy_index:Int_t,pdg:Int_t,status:Int_t,final:UChar_t,selected:UChar_t,pair_eligible:UChar_t,category:Int_t,is_meson:UChar_t,is_baryon:UChar_t,spin:Int_t,charge3:Int_t,nc:Int_t,ncbar:Int_t,nb:Int_t,nbbar:Int_t,qc:Int_t,qb:Int_t,baryon3:Int_t,strangeness:Int_t,open:UChar_t,hidden:UChar_t,mother1:Int_t,mother2:Int_t,daughter1:Int_t,daughter2:Int_t,px:Double_t,py:Double_t,pz:Double_t,energy:Double_t,mass:Double_t,pt:Double_t,eta:Double_t,rapidity:Double_t,phi:Double_t"},
    {"heavy_mothers","event_id:ULong64_t,heavy_index:Int_t,edge_ordinal:UInt_t,mother_index:Int_t"},
    {"origins","event_id:ULong64_t,heavy_index:Int_t,sector:Int_t,origin:Int_t,resolution:Int_t,matched_hard:Int_t,rejected_hard:Int_t,depth:Int_t"},
    {"pairs","event_id:ULong64_t,trigger_heavy_index:Int_t,associate_heavy_index:Int_t,sign:Int_t,dphi:Double_t,deta:Double_t,trigger_pt:Double_t,associate_pt:Double_t,a15_eta1:Int_t,a15_eta4:Int_t,associate_origin:Int_t,associate_category:Int_t,weight:Double_t"},
    {"source_blocks","source_id:UInt_t,assignment_id:UInt_t,block:UInt_t"},
    {"source_counts","source_id:UInt_t,family_id:UInt_t,rows:ULong64_t"},
    {"sources","source_id:UInt_t,tune:UInt_t,logical_id:ULong64_t,attempt:UInt_t,events:ULong64_t,attempted_events:ULong64_t,sumw:Double_t,sumw2:Double_t,sumabsw:Double_t"},
    {"triggers","event_id:ULong64_t,heavy_index:Int_t,sector:Int_t,rejection_mask:UInt_t"},
  };
  return schemas;
}

std::string TreeSchema(TTree* tree) {
  std::ostringstream output;
  TIter branches(tree->GetListOfBranches());
  bool first = true;
  while (auto* object = branches()) {
    auto* branch = dynamic_cast<TBranch*>(object);
    auto* leaf = branch == nullptr ? nullptr : branch->GetLeaf(branch->GetName());
    if (leaf == nullptr) throw std::runtime_error("ROOT branch has no scalar leaf");
    if (!first) output << ',';
    first = false;
    output << branch->GetName() << ':' << leaf->GetTypeName();
  }
  return output.str();
}

void ValidateLosslessFile(TFile& file, const Shard& shard) {
  if (file.IsZombie()) throw std::runtime_error("analysis shard is zombie/unreadable");
  if (file.GetCompressionAlgorithm() != static_cast<int>(ROOT::RCompressionSetting::EAlgorithm::kZSTD) || file.GetCompressionLevel() != 5) {
    throw std::runtime_error("analysis shard compression differs");
  }
  std::map<std::string, std::pair<std::string, int>> keys;
  TIter iterator(file.GetListOfKeys());
  while (auto* object = iterator()) {
    auto* key = dynamic_cast<TKey*>(object);
    if (key == nullptr || !keys.emplace(key->GetName(), std::make_pair(key->GetClassName(), key->GetCycle())).second) {
      throw std::runtime_error("duplicate ROOT key/cycle in analysis shard");
    }
  }
  if (keys.size() != ExpectedSchemas().size() + 1 || keys["contract"] != std::make_pair(std::string("TObjString"), 1)) {
    throw std::runtime_error("analysis shard exact object set differs");
  }
  for (const auto& expected : ExpectedSchemas()) {
    if (keys[expected.first] != std::make_pair(std::string("TTree"), 1)) throw std::runtime_error("analysis shard key class/cycle differs: " + expected.first);
    auto* tree = dynamic_cast<TTree*>(file.Get(expected.first.c_str()));
    if (tree == nullptr || TreeSchema(tree) != expected.second) throw std::runtime_error("analysis shard branch order/set differs: " + expected.first);
  }
  for (const auto& expected : ExpectedSchemas()) {
    const auto entries = dynamic_cast<TTree*>(file.Get(expected.first.c_str()))->GetEntries();
    if (entries < 0 || static_cast<std::uint64_t>(entries) != shard.rowCounts.at(expected.first)) {
      throw std::runtime_error("analysis shard receipt row accounting differs: " + expected.first);
    }
  }
  std::uint64_t rows = 0;
  for (const auto& item : shard.rowCounts) {
    if (item.second > std::numeric_limits<std::uint64_t>::max() - rows) throw std::runtime_error("analysis shard row accounting overflows");
    rows += item.second;
  }
  if (rows != shard.rows) throw std::runtime_error("analysis shard total row accounting differs");
  auto* contract = dynamic_cast<TObjString*>(file.Get("contract"));
  if (contract == nullptr) throw std::runtime_error("analysis shard contract is absent");
  const std::string text = contract->GetString().Data();
  const std::array<std::string, 4> bindings{{
      "\"schema\":\"hadronization_lossless_analysis_v1\"",
      "\"scientific_content_digest\":\"" + shard.scientificDigest + "\"",
      "\"shard_ordinal\":" + std::to_string(shard.ordinal),
      "\"completion\":\"COMPLETE_INDEPENDENT_SHARD\""}};
  for (const auto& binding : bindings) if (text.find(binding) == std::string::npos) throw std::runtime_error("analysis shard contract binding differs");
}

template <typename T>
void Branch(TTree* tree, const char* name, T* value) {
  if (tree->SetBranchAddress(name, value) < 0) throw std::runtime_error(std::string("cannot bind branch ") + tree->GetName() + "." + name);
}

bool AlmostEqual(double left, double right) {
  if (left == right) return true;
  const double scale = std::max({1.0, std::abs(left), std::abs(right)});
  return std::abs(left - right) <= 32.0 * std::numeric_limits<double>::epsilon() * scale;
}

}  // namespace

namespace {

struct Range { std::uint64_t first = 0, count = 0; unsigned source = 0; };
struct EventRow { ULong64_t event = 0; double weight = 0.0; int eta1 = 0, eta4 = 0; };
struct HeavyRow {
  ULong64_t event = 0; int index = 0, pdg = 0, status = 0; unsigned char final = 0, selected = 0, pairEligible = 0;
  int category = 0, nc = 0, ncbar = 0, nb = 0, nbbar = 0, qc = 0, qb = 0;
  double pt = 0.0, eta = 0.0, phi = 0.0;
};
struct TriggerRow { ULong64_t event = 0; int heavy = 0, sector = 0; unsigned mask = 0; };
struct OriginRow {
  ULong64_t event = 0;
  int heavy = 0, sector = 0, origin = 0, resolution = 0;
  int matchedHard = -1, rejectedHard = -1, depth = -1;
};
struct PairRow {
  ULong64_t event = 0; int trigger = 0, associate = 0, sign = 0; double dphi = 0.0, deta = 0.0, triggerPt = 0.0, associatePt = 0.0;
  int eta1 = 0, eta4 = 0, origin = 0, category = 0; double weight = 0.0;
};
struct ClosureRow { ULong64_t event = 0; int trigger = 0, associate = 0, coefficient = 0; unsigned char visible = 0; int category = 0; };

struct Boundary {
  int low = 0, high = 0;
  bool stable = true, resolved = true, empty = false;
};

struct ActivityReceipt {
  int tune = 0, activity = 0;
  std::map<int, int> pooledThreshold;
  std::map<int, std::vector<int>> complementThreshold;
  std::map<int, std::vector<double>> belowMargins;
  std::map<int, std::vector<double>> throughMargins;
  std::map<int, bool> resolved;
  std::vector<Boundary> classes;
};

std::string JsonStringValue(const std::string& json, const std::string& key);

struct BlockAccounting {
  std::uint64_t sources = 0;
  std::uint64_t successfulEvents = 0;
  std::uint64_t attemptedEvents = 0;
  Accumulator sumw;
  Accumulator sumw2;
  Accumulator sumabsw;
};

class Reducer {
 public:
  explicit Reducer(Spec spec) : spec_(std::move(spec)) { Initialize(); }
  void Run(const std::string& output);

 private:
  void Initialize();
  void InspectShard(const Shard& shard);
  void FirstPass(const Shard& shard);
  void ResolveActivities();
  void MaterializeActivityCells();
  void SecondPass(const Shard& shard);
  void ProcessEvent(int tune, int block, const EventRow& event,
                    const std::vector<HeavyRow>& heavy,
                    const std::vector<OriginRow>& origins,
                    const std::vector<TriggerRow>& triggers,
                    const std::vector<PairRow>& pairs,
                    const std::vector<ClosureRow>& closure);
  void BuildGram(int tune, int block, const EventRow& event,
                 const std::vector<HeavyRow>& heavy,
                 const std::vector<TriggerRow>& triggers,
                 const std::vector<PairRow>& pairs);
  void FinalizeDynamicCells();
  std::string ActivityJson() const;
  std::string AccountingJson() const;
  std::string DynamicJson() const;
  std::string EstimatorAuditJson() const;
  std::string ScientificDigest() const;
  std::pair<std::string, std::string> Write(
      const std::string& output, const std::string& activityJson,
      const std::string& dynamicJson, const std::string& estimatorJson,
      const std::string& scientificDigest);
  int SourceForEvent(const Shard& shard, std::uint64_t event,
                     const std::vector<Range>& ranges) const;
  bool ProfileTrigger(const Profile& profile, double pt) const {
    return !profile.triggerCut || pt > profile.triggerPt;
  }
  bool ProfileAssociate(const Profile& profile, double pt) const {
    return !profile.associateCut || pt > profile.associatePt;
  }
  bool InClass(int tune, int activity, int classId, int value) const;
  int PairScope(int tune, int profile, int activity, int classId) const;
  int IntegratedScope(int tune, int profile) const;
  int ActivityScope(int tune, int activity) const;
  int TuneScope(int tune) const;
  int DphiBin(double value) const;
  int UniformInclusiveBin(double value, double low, double high, int bins) const;
  int PtBin(double value) const;
  void AddCell(std::uint32_t projection, std::uint32_t scope,
               std::uint32_t block, std::uint32_t bin,
               std::uint32_t component, double value) {
    cells_[{projection, scope, block, bin, component}].Add(value);
  }
  const HeavyRow& Heavy(const std::unordered_map<int, std::size_t>& lookup,
                        const std::vector<HeavyRow>& rows, int index,
                        const char* role) const;

  Spec spec_;
  int blocks_ = 0, activityBins_ = 0, dphiBins_ = 0, maxTune_ = -1;
  double dphiLow_ = 0.0, dphiHigh_ = 0.0, etaLow_ = 0.0, etaHigh_ = 0.0, phiLow_ = 0.0, phiHigh_ = 0.0;
  std::map<int, State> stateByPdg_;
  std::map<std::pair<int, int>, Pair> pairByIdentity_;
  std::map<int, int> triggerIndex_;
  std::map<std::pair<int, int>, int> correlationByIdentity_;
  std::map<std::tuple<std::string, std::string, std::string, int>, int> scopeLookup_;
  std::map<std::tuple<int, int, int, int>, int> pairScopeIds_;
  std::map<std::pair<int, int>, int> tuneActivityScope_;
  std::map<std::pair<int, int>, int> tuneProfileScope_;
  std::map<int, int> tuneScope_;
  std::map<int, bool> tuneDesignComplete_;
  std::array<int, 300> gramFamilyForPair_{};
  std::array<int, 12> referenceGramFamily_{};
  std::vector<GramFamily> gramFamilies_;
  std::vector<Accumulator> activityHistogram_;
  std::vector<std::uint64_t> exposure_;
  std::vector<ActivityReceipt> activityReceipts_;
  std::vector<BlockAccounting> blockAccounting_;
  std::map<CellKey, Accumulator> cells_;
  std::map<GramKey, Accumulator> gram_;
  std::map<std::tuple<std::uint32_t, std::uint32_t, int, int>, Accumulator> closureSpecies_;
  std::map<std::tuple<std::uint32_t, std::uint32_t, int>, std::array<Accumulator, 3>> t1_;
  std::set<int> closurePdgs_, t1Pdgs_;
  std::uint64_t totalEvents_ = 0, totalSources_ = 0, inputBytes_ = 0;
};

void Reducer::Initialize() {
  blocks_ = static_cast<int>(Integer(spec_.settings.at("block_count")));
  activityBins_ = static_cast<int>(Integer(spec_.settings.at("activity_bins")));
  dphiBins_ = static_cast<int>(Integer(spec_.settings.at("dphi_bins")));
  dphiLow_ = Double(spec_.settings.at("dphi_low")); dphiHigh_ = Double(spec_.settings.at("dphi_high"));
  etaLow_ = Double(spec_.settings.at("eta_low")); etaHigh_ = Double(spec_.settings.at("eta_high"));
  phiLow_ = Double(spec_.settings.at("phi_low")); phiHigh_ = Double(spec_.settings.at("phi_high"));
  if (blocks_ != 10) {
    throw std::runtime_error("this reducer release requires K=10/dof=9 in every mode");
  }
  if (activityBins_ != 4096 || dphiBins_ != 100 ||
      dphiLow_ != -kPi / 2.0 || dphiHigh_ != 3.0 * kPi / 2.0 ||
      etaLow_ != -4.0 || etaHigh_ != 4.0 || phiLow_ != -kPi || phiHigh_ != kPi) {
    throw std::runtime_error("reduction numerical domain differs");
  }
  for (const auto& state : spec_.states) {
    if (!stateByPdg_.emplace(state.pdg, state).second) throw std::runtime_error("duplicate state PDG");
  }
  std::vector<int> triggers;
  for (const auto& pair : spec_.pairs) {
    if (pair.id != static_cast<int>(pairByIdentity_.size()) ||
        !pairByIdentity_.emplace(std::make_pair(pair.trigger, pair.associate), pair).second) {
      throw std::runtime_error("pair registry identity/order differs");
    }
    triggers.push_back(pair.trigger);
  }
  std::sort(triggers.begin(), triggers.end()); triggers.erase(std::unique(triggers.begin(), triggers.end()), triggers.end());
  const std::vector<int> configuredOrder = {411,-411,421,-421,4122,-4122,511,-511,521,-521,5122,-5122};
  for (std::size_t index = 0; index < configuredOrder.size(); ++index) triggerIndex_[configuredOrder[index]] = static_cast<int>(index);
  if (triggers.size() != triggerIndex_.size()) throw std::runtime_error("trigger registry count differs");
  for (const auto& correlation : spec_.correlations) {
    correlationByIdentity_[{correlation.trigger, correlation.associate}] = correlation.id;
  }
  gramFamilyForPair_.fill(-1);
  referenceGramFamily_.fill(-1);
  for (const auto& opposite : spec_.pairs) if (opposite.sign == -1) {
    const auto same = pairByIdentity_.find({opposite.trigger, -opposite.associate});
    const auto referenceOpposite = pairByIdentity_.find({opposite.trigger, opposite.reference});
    const auto referenceSame = pairByIdentity_.find({opposite.trigger, -opposite.reference});
    if (same == pairByIdentity_.end() || same->second.sign != 1 ||
        referenceOpposite == pairByIdentity_.end() || referenceOpposite->second.sign != -1 ||
        referenceSame == pairByIdentity_.end() || referenceSame->second.sign != 1) {
      throw std::runtime_error("OS/SS/reference Gram registry differs");
    }
    const int family = static_cast<int>(gramFamilies_.size());
    gramFamilies_.push_back({opposite.id, same->second.id,
                             300 + triggerIndex_.at(opposite.trigger),
                             referenceOpposite->second.id,
                             referenceSame->second.id});
    for (const int pair : {opposite.id, same->second.id}) {
      if (gramFamilyForPair_.at(static_cast<std::size_t>(pair)) != -1) {
        throw std::runtime_error("pair belongs to more than one Gram family");
      }
      gramFamilyForPair_.at(static_cast<std::size_t>(pair)) = family;
    }
    if (opposite.id == referenceOpposite->second.id) {
      const int trigger = triggerIndex_.at(opposite.trigger);
      if (referenceGramFamily_.at(static_cast<std::size_t>(trigger)) != -1) {
        throw std::runtime_error("trigger has more than one reference Gram family");
      }
      referenceGramFamily_.at(static_cast<std::size_t>(trigger)) = family;
    }
  }
  if (gramFamilies_.size() != 150 ||
      std::any_of(gramFamilyForPair_.begin(), gramFamilyForPair_.end(), [](int value){ return value < 0; }) ||
      std::any_of(referenceGramFamily_.begin(), referenceGramFamily_.end(), [](int value){ return value < 0; })) {
    throw std::runtime_error("Gram family coverage differs");
  }
  std::map<std::string, int> tuneOrdinal;
  for (const auto& shard : spec_.shards) for (const auto& source : shard.sources) {
    const auto inserted = tuneOrdinal.emplace(source.tuneName, source.tune);
    if (!inserted.second && inserted.first->second != source.tune) throw std::runtime_error("tune ordinal alias differs");
    maxTune_ = std::max(maxTune_, source.tune);
  }
  for (const auto& scope : spec_.scopes) {
    const auto tune = tuneOrdinal.find(scope.tune);
    if (tune == tuneOrdinal.end()) throw std::runtime_error("scope tune is not admitted");
    if (scope.family == "pair") {
      const auto profile = std::find_if(spec_.profiles.begin(), spec_.profiles.end(), [&](const auto& value){ return value.name == scope.profile; });
      const auto activity = std::find_if(spec_.activities.begin(), spec_.activities.end(), [&](const auto& value){ return value.name == scope.activity; });
      if (profile == spec_.profiles.end() || activity == spec_.activities.end()) throw std::runtime_error("scope profile/activity differs");
      scopeLookup_[{scope.tune, scope.profile, scope.activity, scope.classId}] = scope.id;
      pairScopeIds_[{tune->second, profile->id, activity->id, scope.classId}] = scope.id;
    } else if (scope.family == "integrated_profile") {
      const auto profile = std::find_if(spec_.profiles.begin(), spec_.profiles.end(), [&](const auto& value){ return value.name == scope.profile; });
      if (profile == spec_.profiles.end()) throw std::runtime_error("integrated scope profile differs");
      tuneProfileScope_[{tune->second, profile->id}] = scope.id;
    } else if (scope.family == "activity") {
      const auto activity = std::find_if(spec_.activities.begin(), spec_.activities.end(), [&](const auto& value){ return value.name == scope.activity; });
      if (activity == spec_.activities.end()) throw std::runtime_error("activity scope differs");
      tuneActivityScope_[{tune->second, activity->id}] = scope.id;
    } else if (scope.family == "tune") {
      tuneScope_[tune->second] = scope.id;
    }
  }
  const std::size_t histogramSize = static_cast<std::size_t>(maxTune_ + 1) * blocks_ * spec_.activities.size() * activityBins_;
  activityHistogram_.resize(histogramSize);
  exposure_.assign(static_cast<std::size_t>(maxTune_ + 1) * blocks_, 0);
  blockAccounting_.resize(static_cast<std::size_t>(maxTune_ + 1) * blocks_);
  for (const auto& shard : spec_.shards) {
    totalSources_ += shard.sources.size();
    std::ifstream input(shard.path, std::ios::binary | std::ios::ate);
    if (!input) throw std::runtime_error("cannot stat admitted shard");
    inputBytes_ += static_cast<std::uint64_t>(input.tellg());
  }
}

int Reducer::PairScope(int tune, int profile, int activity, int classId) const {
  const auto found = pairScopeIds_.find({tune, profile, activity, classId});
  if (found == pairScopeIds_.end()) throw std::runtime_error("pair scope is undeclared");
  return found->second;
}
int Reducer::IntegratedScope(int tune, int profile) const { return tuneProfileScope_.at({tune, profile}); }
int Reducer::ActivityScope(int tune, int activity) const { return tuneActivityScope_.at({tune, activity}); }
int Reducer::TuneScope(int tune) const { return tuneScope_.at(tune); }

std::size_t ActivityOffset(int tune, int block, int activity, int bin,
                           int blocks, int activities, int bins) {
  return (((static_cast<std::size_t>(tune) * blocks + (block - 1)) * activities + activity) * bins + bin);
}

int Reducer::SourceForEvent(const Shard& shard, std::uint64_t event,
                            const std::vector<Range>& ranges) const {
  const auto found = std::upper_bound(ranges.begin(), ranges.end(), event,
      [](std::uint64_t value, const Range& range) { return value < range.first; });
  if (found == ranges.begin()) throw std::runtime_error("event is before every declared range");
  const auto& range = *std::prev(found);
  if (event < range.first || event - range.first >= range.count || range.source >= shard.sources.size()) {
    throw std::runtime_error("event does not map to one admitted source range");
  }
  return static_cast<int>(range.source);
}

void Reducer::InspectShard(const Shard& shard) {
  TFile file(shard.path.c_str(), "READ");
  ValidateLosslessFile(file, shard);
  auto* sources = dynamic_cast<TTree*>(file.Get("sources"));
  UInt_t sourceId = 0, tune = 0, attempt = 0; ULong64_t logical = 0, events = 0, attempted = 0; Double_t sumw = 0, sumw2 = 0, sumabs = 0;
  Branch(sources,"source_id",&sourceId); Branch(sources,"tune",&tune); Branch(sources,"logical_id",&logical); Branch(sources,"attempt",&attempt);
  Branch(sources,"events",&events); Branch(sources,"attempted_events",&attempted); Branch(sources,"sumw",&sumw); Branch(sources,"sumw2",&sumw2); Branch(sources,"sumabsw",&sumabs);
  if (sources->GetEntries() != static_cast<Long64_t>(shard.sources.size())) throw std::runtime_error("source row count differs from plan");
  for (Long64_t row = 0; row < sources->GetEntries(); ++row) {
    if (sources->GetEntry(row) <= 0) throw std::runtime_error("cannot read source row");
    const auto& expected = shard.sources.at(static_cast<std::size_t>(row));
    if (sourceId != static_cast<UInt_t>(row) || expected.local != static_cast<int>(sourceId) || tune != static_cast<UInt_t>(expected.tune) || logical != expected.logical || attempt != expected.attempt || events != expected.events || attempted < events || !std::isfinite(sumw) || !std::isfinite(sumw2) || !std::isfinite(sumabs) || sumw2 < 0 || sumabs < std::abs(sumw)) {
      throw std::runtime_error("source identity/exposure/weight accounting differs");
    }
    auto& accounting = blockAccounting_.at(
        static_cast<std::size_t>(expected.tune) * blocks_ + expected.block - 1);
    ++accounting.sources;
    accounting.successfulEvents += events;
    accounting.attemptedEvents += attempted;
    accounting.sumw.Add(sumw);
    accounting.sumw2.Add(sumw2);
    accounting.sumabsw.Add(sumabs);
  }
  auto* blocks = dynamic_cast<TTree*>(file.Get("source_blocks"));
  UInt_t assignment = 0, block = 0;
  Branch(blocks,"source_id",&sourceId); Branch(blocks,"assignment_id",&assignment); Branch(blocks,"block",&block);
  if (blocks->GetEntries() != static_cast<Long64_t>(shard.sources.size())) throw std::runtime_error("source-block row count differs");
  for (Long64_t row = 0; row < blocks->GetEntries(); ++row) {
    if (blocks->GetEntry(row) <= 0) throw std::runtime_error("cannot read source-block row");
    if (sourceId != static_cast<UInt_t>(row) || assignment != 0 || block != static_cast<UInt_t>(shard.sources.at(row).block)) throw std::runtime_error("source-block assignment differs");
  }
  auto* counts = dynamic_cast<TTree*>(file.Get("source_counts"));
  UInt_t family = 0; ULong64_t count = 0;
  Branch(counts,"source_id",&sourceId); Branch(counts,"family_id",&family); Branch(counts,"rows",&count);
  const auto& schemas = ExpectedSchemas();
  std::vector<std::string> families;
  families.reserve(schemas.size());
  for (const auto& item : schemas) families.push_back(item.first);
  std::map<std::string, std::uint64_t> familyTotals;
  if (counts->GetEntries() != static_cast<Long64_t>(shard.sources.size() * families.size())) throw std::runtime_error("source-count cardinality differs");
  for (Long64_t row = 0; row < counts->GetEntries(); ++row) {
    if (counts->GetEntry(row) <= 0 || sourceId != static_cast<UInt_t>(row / static_cast<Long64_t>(families.size())) ||
        family != static_cast<UInt_t>(row % static_cast<Long64_t>(families.size()))) throw std::runtime_error("source-count natural key/domain differs");
    familyTotals[families.at(family)] += count;
    const std::string& name = families.at(family);
    if ((name == "events" && count != shard.sources.at(sourceId).events) ||
        ((name == "event_ranges" || name == "source_blocks" || name == "sources") && count != 1) ||
        (name == "source_counts" && count != families.size())) throw std::runtime_error("source-count structural ownership differs");
  }
  if (familyTotals != shard.rowCounts) throw std::runtime_error("source-count/global row closure differs");
}

std::vector<Range> ReadRanges(TFile& file, const Shard& shard) {
  auto* tree = dynamic_cast<TTree*>(file.Get("event_ranges"));
  ULong64_t first = 0, count = 0; UInt_t source = 0;
  Branch(tree,"first_id",&first); Branch(tree,"count",&count); Branch(tree,"source_id",&source);
  std::vector<Range> ranges;
  std::vector<std::uint64_t> counts(shard.sources.size(), 0);
  for (Long64_t row = 0; row < tree->GetEntries(); ++row) {
    if (tree->GetEntry(row) <= 0 || count == 0 || source >= shard.sources.size() || first > std::numeric_limits<std::uint64_t>::max() - count) throw std::runtime_error("event range domain differs");
    if (!ranges.empty() && first < ranges.back().first + ranges.back().count) throw std::runtime_error("event ranges overlap or are unsorted");
    ranges.push_back({first,count,source}); counts[source] += count;
  }
  for (std::size_t index = 0; index < counts.size(); ++index) if (counts[index] != shard.sources[index].events) throw std::runtime_error("event range/source exposure closure differs");
  return ranges;
}

void BindEvent(TTree* tree, EventRow& row) {
  Branch(tree,"event_id",&row.event); Branch(tree,"weight",&row.weight); Branch(tree,"a15_eta1",&row.eta1); Branch(tree,"a15_eta4",&row.eta4);
}

void Reducer::FirstPass(const Shard& shard) {
  TFile file(shard.path.c_str(), "READ");
  const auto ranges = ReadRanges(file, shard);
  auto* tree = dynamic_cast<TTree*>(file.Get("events")); EventRow event; BindEvent(tree,event);
  std::vector<std::uint64_t> sourceEvents(shard.sources.size(), 0);
  std::vector<Accumulator> sourceWeights(shard.sources.size());
  std::uint64_t previous = 0; bool first = true;
  for (Long64_t row = 0; row < tree->GetEntries(); ++row) {
    if (tree->GetEntry(row) <= 0) throw std::runtime_error("cannot read event row");
    if ((!first && event.event <= previous) || !std::isfinite(event.weight) || event.eta1 < 0 || event.eta4 < 0 || event.eta1 >= activityBins_ || event.eta4 >= activityBins_) throw std::runtime_error("consumed event row order/domain differs");
    first = false; previous = event.event;
    const int local = SourceForEvent(shard,event.event,ranges); const auto& source = shard.sources.at(local);
    ++sourceEvents[local]; sourceWeights[local].Add(event.weight); ++totalEvents_; ++exposure_.at(static_cast<std::size_t>(source.tune) * blocks_ + source.block - 1);
    const std::array<int,2> values{{event.eta4,event.eta1}};
    for (int activity = 0; activity < 2; ++activity) activityHistogram_.at(ActivityOffset(source.tune,source.block,activity,values[activity],blocks_,2,activityBins_)).Add(event.weight);
  }
  auto* sources=dynamic_cast<TTree*>(file.Get("sources"));UInt_t sourceId=0;Double_t sumw=0,sumw2=0,sumabs=0;Branch(sources,"source_id",&sourceId);Branch(sources,"sumw",&sumw);Branch(sources,"sumw2",&sumw2);Branch(sources,"sumabsw",&sumabs);for(Long64_t row=0;row<sources->GetEntries();++row){if(sources->GetEntry(row)<=0||sourceId!=static_cast<UInt_t>(row))throw std::runtime_error("cannot reread source weight accounting");const auto& accumulated=sourceWeights.at(static_cast<std::size_t>(row));if(sourceEvents.at(static_cast<std::size_t>(row))!=shard.sources.at(static_cast<std::size_t>(row)).events||!AlmostEqual(accumulated.Value(),sumw)||!AlmostEqual(accumulated.SumW2(),sumw2)||!AlmostEqual(accumulated.SumAbs(),sumabs))throw std::runtime_error("event/source weight accounting differs");}
}

int Threshold(const std::vector<double>& histogram, int percentile) {
  if (percentile < 0 || percentile > 100) throw std::runtime_error("percentile out of domain");
  const double total = HR::Sum(histogram);
  if (!(total > 0.0) || !std::isfinite(total) || std::any_of(histogram.begin(), histogram.end(), [](double value){ return value < 0.0 || !std::isfinite(value); })) throw std::runtime_error("ACTIVITY_MEASURE_UNDEFINED");
  const double target = (100.0 - percentile) / 100.0 * total;
  Accumulator cumulative;
  for (std::size_t bin = 0; bin < histogram.size(); ++bin) {
    cumulative.Add(histogram[bin]);
    if (cumulative.Value() >= target) return static_cast<int>(bin);
  }
  return static_cast<int>(histogram.size() - 1);
}

void Reducer::ResolveActivities() {
  for (int tune = 0; tune <= maxTune_; ++tune) {
    bool hasTune = false; for (const auto& shard : spec_.shards) for (const auto& source : shard.sources) if (source.tune == tune) hasTune = true;
    if (!hasTune) continue;
    const auto begin = exposure_.begin() + static_cast<std::size_t>(tune) * blocks_;
    const auto end = begin + blocks_;
    const bool designComplete=!std::any_of(begin,end,[](auto value){return value==0;})&&std::all_of(begin,end,[&](auto value){return value==*begin;});
    tuneDesignComplete_[tune]=designComplete;
    if (spec_.settings.at("publication_state") == "PUBLICATION_ELIGIBLE" && !designComplete) throw std::runtime_error("Phase-A tune blocks lack ten equal successful-event exposures");
    for (int activity = 0; activity < 2; ++activity) {
      ActivityReceipt receipt; receipt.tune=tune; receipt.activity=activity;
      std::vector<double> pooled(activityBins_,0.0);
      for (int bin=0;bin<activityBins_;++bin) {
        std::vector<double> blockValues;
        blockValues.reserve(blocks_);
        for (int block=1;block<=blocks_;++block) {
          blockValues.push_back(activityHistogram_[ActivityOffset(tune,block,activity,bin,blocks_,2,activityBins_)].Value());
        }
        pooled[bin]=HR::Sum(blockValues);
      }
      std::set<int> percentiles;
      for (const auto& klass:spec_.classes) { percentiles.insert(klass.lowPercent); percentiles.insert(klass.highPercent); }
      for (const int percentile:percentiles) {
        const int threshold=Threshold(pooled,percentile); receipt.pooledThreshold[percentile]=threshold;
        bool resolved=true;
        std::vector<int> leaves; leaves.reserve(blocks_);
        for (int removed=1;removed<=blocks_;++removed) {
          std::vector<double> complement(activityBins_);
          for(int bin=0;bin<activityBins_;++bin){std::vector<double> remaining;remaining.reserve(blocks_-1);for(int retained=1;retained<=blocks_;++retained)if(retained!=removed)remaining.push_back(activityHistogram_[ActivityOffset(tune,retained,activity,bin,blocks_,2,activityBins_)].Value());complement[bin]=HR::Sum(remaining);}
          try { leaves.push_back(Threshold(complement,percentile)); }
          catch (const std::runtime_error& error) {
            if (std::string(error.what()) != "ACTIVITY_MEASURE_UNDEFINED" || designComplete) throw;
            leaves.push_back(-1);
            resolved=false;
          }
        }
        receipt.complementThreshold[percentile]=leaves;
        if(percentile>0&&percentile<100){
          const double q=(100.0-percentile)/100.0; std::vector<double> r(blocks_),l(blocks_);
          for(int block=1;block<=blocks_;++block){Accumulator below,through,total;for(int bin=0;bin<activityBins_;++bin){const double value=activityHistogram_[ActivityOffset(tune,block,activity,bin,blocks_,2,activityBins_)].Value();total.Add(value);if(bin<threshold)below.Add(value);if(bin<=threshold)through.Add(value);}r[block-1]=through.Value()-q*total.Value();l[block-1]=below.Value()-q*total.Value();}
          const double sr=HR::Sum(r),sl=HR::Sum(l),mr=sr/blocks_,ml=sl/blocks_;std::vector<double> vrTerms,vlTerms;vrTerms.reserve(blocks_);vlTerms.reserve(blocks_);for(int block=0;block<blocks_;++block){vrTerms.push_back((r[block]-mr)*(r[block]-mr));vlTerms.push_back((l[block]-ml)*(l[block]-ml));}const double vr=static_cast<double>(blocks_)/(blocks_-1)*HR::Sum(vrTerms),vl=static_cast<double>(blocks_)/(blocks_-1)*HR::Sum(vlTerms);const double critical=2.2621571628540993;resolved=resolved&&sr>critical*std::sqrt(vr)&&-sl>critical*std::sqrt(vl);
          receipt.throughMargins[percentile]=r;
          receipt.belowMargins[percentile]=l;
        }
        receipt.resolved[percentile]=resolved;
      }
      for(const auto& klass:spec_.classes){Boundary boundary;if(klass.integrated){boundary.low=0;boundary.high=activityBins_-1;}else{boundary.low=klass.highPercent==100?0:receipt.pooledThreshold.at(klass.highPercent)+1;boundary.high=klass.lowPercent==0?activityBins_-1:receipt.pooledThreshold.at(klass.lowPercent);boundary.empty=boundary.low>boundary.high;for(const int percentile:{klass.lowPercent,klass.highPercent}){if(percentile>0&&percentile<100){const auto& leaves=receipt.complementThreshold.at(percentile);if(std::any_of(leaves.begin(),leaves.end(),[&](int value){return value!=receipt.pooledThreshold.at(percentile);}))boundary.stable=false;if(!receipt.resolved.at(percentile))boundary.resolved=false;}}}receipt.classes.push_back(boundary);}
      activityReceipts_.push_back(receipt);
    }
  }
}

bool Reducer::InClass(int tune,int activity,int classId,int value) const {
  const auto found=std::find_if(activityReceipts_.begin(),activityReceipts_.end(),[&](const auto& receipt){return receipt.tune==tune&&receipt.activity==activity;});
  if(found==activityReceipts_.end()||classId<0||classId>=static_cast<int>(found->classes.size()))throw std::runtime_error("class receipt is absent");
  const auto& boundary=found->classes[classId];return !boundary.empty&&value>=boundary.low&&value<=boundary.high;
}

void Reducer::MaterializeActivityCells(){for(int tune=0;tune<=maxTune_;++tune)if(tuneScope_.count(tune))for(int block=1;block<=blocks_;++block)for(int activity=0;activity<2;++activity)for(int bin=0;bin<activityBins_;++bin){const auto& value=activityHistogram_[ActivityOffset(tune,block,activity,bin,blocks_,2,activityBins_)];if(value.fills!=0)cells_[{1,static_cast<std::uint32_t>(ActivityScope(tune,activity)),static_cast<std::uint32_t>(block),static_cast<std::uint32_t>(bin),0}]=value;}}

void BindHeavy(TTree* tree, HeavyRow& row){
  Branch(tree,"event_id",&row.event);Branch(tree,"heavy_index",&row.index);Branch(tree,"pdg",&row.pdg);Branch(tree,"status",&row.status);Branch(tree,"final",&row.final);Branch(tree,"selected",&row.selected);Branch(tree,"pair_eligible",&row.pairEligible);Branch(tree,"category",&row.category);Branch(tree,"nc",&row.nc);Branch(tree,"ncbar",&row.ncbar);Branch(tree,"nb",&row.nb);Branch(tree,"nbbar",&row.nbbar);Branch(tree,"qc",&row.qc);Branch(tree,"qb",&row.qb);Branch(tree,"pt",&row.pt);Branch(tree,"eta",&row.eta);Branch(tree,"phi",&row.phi);
}
void BindTrigger(TTree* tree,TriggerRow& row){Branch(tree,"event_id",&row.event);Branch(tree,"heavy_index",&row.heavy);Branch(tree,"sector",&row.sector);Branch(tree,"rejection_mask",&row.mask);}
void BindOrigin(TTree* tree,OriginRow& row){Branch(tree,"event_id",&row.event);Branch(tree,"heavy_index",&row.heavy);Branch(tree,"sector",&row.sector);Branch(tree,"origin",&row.origin);Branch(tree,"resolution",&row.resolution);Branch(tree,"matched_hard",&row.matchedHard);Branch(tree,"rejected_hard",&row.rejectedHard);Branch(tree,"depth",&row.depth);}
void BindPair(TTree* tree,PairRow& row){Branch(tree,"event_id",&row.event);Branch(tree,"trigger_heavy_index",&row.trigger);Branch(tree,"associate_heavy_index",&row.associate);Branch(tree,"sign",&row.sign);Branch(tree,"dphi",&row.dphi);Branch(tree,"deta",&row.deta);Branch(tree,"trigger_pt",&row.triggerPt);Branch(tree,"associate_pt",&row.associatePt);Branch(tree,"a15_eta1",&row.eta1);Branch(tree,"a15_eta4",&row.eta4);Branch(tree,"associate_origin",&row.origin);Branch(tree,"associate_category",&row.category);Branch(tree,"weight",&row.weight);}
void BindClosure(TTree* tree,ClosureRow& row){Branch(tree,"event_id",&row.event);Branch(tree,"trigger_heavy_index",&row.trigger);Branch(tree,"associate_heavy_index",&row.associate);Branch(tree,"coefficient",&row.coefficient);Branch(tree,"visible",&row.visible);Branch(tree,"dense_category",&row.category);}

const HeavyRow& Reducer::Heavy(const std::unordered_map<int,std::size_t>& lookup,const std::vector<HeavyRow>& rows,int index,const char* role)const{const auto found=lookup.find(index);if(found==lookup.end())throw std::runtime_error(std::string(role)+" heavy join is missing");return rows.at(found->second);}

int Reducer::DphiBin(double value)const{if(!std::isfinite(value)||value<dphiLow_||!(value<dphiHigh_))throw std::runtime_error("dphi is outside exact half-open axis");const double scaled=(value-dphiLow_)/(dphiHigh_-dphiLow_)*dphiBins_;const int bin=static_cast<int>(scaled);if(bin<0||bin>=dphiBins_)throw std::runtime_error("dphi binning failed");return bin;}
int Reducer::UniformInclusiveBin(double value,double low,double high,int bins)const{if(!std::isfinite(value)||value<low||value>high)return -1;if(value==high)return bins-1;const int bin=static_cast<int>((value-low)/(high-low)*bins);return bin>=0&&bin<bins?bin:-1;}
int Reducer::PtBin(double value)const{if(!std::isfinite(value))throw std::runtime_error("G9 pt is nonfinite");if(value<spec_.ptEdges.front())return 0;if(value>spec_.ptEdges.back())return static_cast<int>(spec_.ptEdges.size());if(value==spec_.ptEdges.back())return static_cast<int>(spec_.ptEdges.size()-1);const auto upper=std::upper_bound(spec_.ptEdges.begin(),spec_.ptEdges.end(),value);return static_cast<int>(upper-spec_.ptEdges.begin());}

void Reducer::SecondPass(const Shard& shard){
  TFile file(shard.path.c_str(),"READ");const auto ranges=ReadRanges(file,shard);
  auto* eventsTree=dynamic_cast<TTree*>(file.Get("events"));auto* heavyTree=dynamic_cast<TTree*>(file.Get("heavy"));auto* originTree=dynamic_cast<TTree*>(file.Get("origins"));auto* triggerTree=dynamic_cast<TTree*>(file.Get("triggers"));auto* pairTree=dynamic_cast<TTree*>(file.Get("pairs"));auto* closureTree=dynamic_cast<TTree*>(file.Get("closure"));
  EventRow event;HeavyRow heavyRow;OriginRow originRow;TriggerRow triggerRow;PairRow pairRow;ClosureRow closureRow;BindEvent(eventsTree,event);BindHeavy(heavyTree,heavyRow);BindOrigin(originTree,originRow);BindTrigger(triggerTree,triggerRow);BindPair(pairTree,pairRow);BindClosure(closureTree,closureRow);
  Long64_t hi=0,oi=0,ti=0,pi=0,ci=0;bool hv=heavyTree->GetEntries()>0,ov=originTree->GetEntries()>0,tv=triggerTree->GetEntries()>0,pv=pairTree->GetEntries()>0,cv=closureTree->GetEntries()>0;if(hv)heavyTree->GetEntry(0);if(ov)originTree->GetEntry(0);if(tv)triggerTree->GetEntry(0);if(pv)pairTree->GetEntry(0);if(cv)closureTree->GetEntry(0);
  for(Long64_t ei=0;ei<eventsTree->GetEntries();++ei){if(eventsTree->GetEntry(ei)<=0)throw std::runtime_error("cannot reread event");const int local=SourceForEvent(shard,event.event,ranges);const auto& source=shard.sources.at(local);std::vector<HeavyRow> heavy;std::vector<OriginRow> origins;std::vector<TriggerRow> triggers;std::vector<PairRow> pairs;std::vector<ClosureRow> closure;
    while(hv&&heavyRow.event==event.event){heavy.push_back(heavyRow);++hi;hv=hi<heavyTree->GetEntries();if(hv&&heavyTree->GetEntry(hi)<=0)throw std::runtime_error("cannot stream heavy row");}
    while(ov&&originRow.event==event.event){origins.push_back(originRow);++oi;ov=oi<originTree->GetEntries();if(ov&&originTree->GetEntry(oi)<=0)throw std::runtime_error("cannot stream origin row");}
    while(tv&&triggerRow.event==event.event){triggers.push_back(triggerRow);++ti;tv=ti<triggerTree->GetEntries();if(tv&&triggerTree->GetEntry(ti)<=0)throw std::runtime_error("cannot stream trigger row");}
    while(pv&&pairRow.event==event.event){pairs.push_back(pairRow);++pi;pv=pi<pairTree->GetEntries();if(pv&&pairTree->GetEntry(pi)<=0)throw std::runtime_error("cannot stream pair row");}
    while(cv&&closureRow.event==event.event){closure.push_back(closureRow);++ci;cv=ci<closureTree->GetEntries();if(cv&&closureTree->GetEntry(ci)<=0)throw std::runtime_error("cannot stream closure row");}
    if((hv&&heavyRow.event<event.event)||(ov&&originRow.event<event.event)||(tv&&triggerRow.event<event.event)||(pv&&pairRow.event<event.event)||(cv&&closureRow.event<event.event))throw std::runtime_error("consumed event-scoped rows are shuffled or orphaned");
    ProcessEvent(source.tune,source.block,event,heavy,origins,triggers,pairs,closure);
  }
  if(hv||ov||tv||pv||cv)throw std::runtime_error("consumed rows remain after final event");
}

void Reducer::ProcessEvent(int tune,int block,const EventRow& event,const std::vector<HeavyRow>& heavy,const std::vector<OriginRow>& origins,const std::vector<TriggerRow>& triggers,const std::vector<PairRow>& pairs,const std::vector<ClosureRow>& closure){
  std::unordered_map<int,std::size_t> lookup;int previous=std::numeric_limits<int>::min();for(std::size_t i=0;i<heavy.size();++i){const auto& row=heavy[i];if(row.index<=previous||row.event!=event.event||!std::isfinite(row.pt)||!std::isfinite(row.eta)||!std::isfinite(row.phi)||row.final>1||row.selected>1||row.pairEligible>1||row.category<0||row.category>5||row.nc<0||row.ncbar<0||row.nb<0||row.nbbar<0)throw std::runtime_error("consumed heavy row order/domain differs");previous=row.index;lookup.emplace(row.index,i);if(row.final){auto& totals=t1_[{static_cast<std::uint32_t>(TuneScope(tune)),static_cast<std::uint32_t>(block),row.pdg}];totals[0].Add(event.weight);totals[1].Add(event.weight*(row.nc+row.ncbar));totals[2].Add(event.weight*(row.nb+row.nbbar));t1Pdgs_.insert(row.pdg);}const auto g9=std::find(spec_.g9.begin(),spec_.g9.end(),row.pdg);if(g9!=spec_.g9.end()&&row.final&&row.selected&&row.status>0&&std::abs(row.status)>=81&&std::abs(row.status)<=89&&row.pt>0.15&&std::abs(row.eta)<=4.0){const int species=static_cast<int>(g9-spec_.g9.begin());const int ptBins=static_cast<int>(spec_.ptEdges.size()+1);const int etaBin=UniformInclusiveBin(row.eta,etaLow_,etaHigh_,100);const int phiBin=UniformInclusiveBin(row.phi,phiLow_,phiHigh_,100);if(etaBin<0||phiBin<0)throw std::runtime_error("G9 inclusive endpoint binning differs");AddCell(9,TuneScope(tune),block,species*(ptBins+200)+PtBin(row.pt),0,event.weight);AddCell(9,TuneScope(tune),block,species*(ptBins+200)+ptBins+etaBin,0,event.weight);AddCell(9,TuneScope(tune),block,species*(ptBins+200)+ptBins+100+phiBin,0,event.weight);}}
  std::map<std::pair<int,int>,const OriginRow*> originMap;int previousHeavy=std::numeric_limits<int>::min(),previousSector=std::numeric_limits<int>::min();for(const auto& row:origins){if(row.event!=event.event||row.heavy<previousHeavy||(row.heavy==previousHeavy&&row.sector<=previousSector)||(row.sector!=4&&row.sector!=5)||row.origin<0||row.origin>4||row.resolution<0||row.resolution>6||lookup.count(row.heavy)==0)throw std::runtime_error("consumed origin row order/domain differs");if(row.heavy!=previousHeavy){previousHeavy=row.heavy;previousSector=std::numeric_limits<int>::min();}previousSector=row.sector;const auto& particle=Heavy(lookup,heavy,row.heavy,"origin");const int charge=row.sector==4?particle.qc:particle.qb;const bool applicable=charge!=0;const bool selected=row.origin==1&&row.resolution==1&&row.matchedHard>=0&&row.rejectedHard==-1&&row.depth>=1;const bool resolved=row.origin>=2&&row.origin<=4&&row.resolution==1&&row.matchedHard==-1&&row.rejectedHard==-1&&row.depth>=1;const bool rejectedValid=(row.resolution==5&&row.rejectedHard>=0)||(row.resolution>=2&&row.resolution<=4&&row.rejectedHard==-1)||row.resolution==6;const bool unresolved=row.origin==0&&row.resolution>=2&&row.resolution<=6&&row.matchedHard==-1&&row.depth>=-1&&rejectedValid;const bool inapplicable=row.origin==0&&row.resolution==0&&row.matchedHard==-1&&row.rejectedHard==-1&&row.depth==-1;if((applicable&&!(selected||resolved||unresolved))||(!applicable&&!inapplicable)||!originMap.emplace(std::make_pair(row.heavy,row.sector),&row).second)throw std::runtime_error("consumed origin decision differs");}if(origins.size()!=2*heavy.size())throw std::runtime_error("consumed origin sector coverage differs");for(const auto& particle:heavy)for(int sector:{4,5})if(originMap.count({particle.index,sector})==0)throw std::runtime_error("consumed origin sector coverage differs");
  auto direct=[](const HeavyRow& particle){return particle.selected&&particle.status>0&&std::abs(particle.status)>=81&&std::abs(particle.status)<=89;};
  std::unordered_map<int,unsigned> triggerMask;previous=std::numeric_limits<int>::min();for(const auto& row:triggers){if(row.heavy<=previous||row.event!=event.event||row.mask>15||(row.sector!=4&&row.sector!=5))throw std::runtime_error("consumed trigger row order/domain differs");previous=row.heavy;const auto& particle=Heavy(lookup,heavy,row.heavy,"trigger");if(triggerIndex_.count(particle.pdg)==0)throw std::runtime_error("trigger PDG outside configured registry");const int expectedSector=stateByPdg_.at(particle.pdg).sector=="charm"?4:5;if(row.sector!=expectedSector)throw std::runtime_error("trigger sector differs");const auto& origin=*originMap.at({row.heavy,row.sector});unsigned expectedMask=0;if(!particle.final)expectedMask|=1;if(!direct(particle))expectedMask|=2;if(origin.origin!=1||origin.resolution!=1||origin.matchedHard<0||origin.rejectedHard!=-1)expectedMask|=4;if(std::abs(row.sector==4?particle.qc:particle.qb)!=1)expectedMask|=8;if(row.mask!=expectedMask)throw std::runtime_error("trigger cached authority differs");triggerMask[row.heavy]=row.mask;}
  previous=std::numeric_limits<int>::min();int previousTrigger=std::numeric_limits<int>::min();for(const auto& row:pairs){if(row.event!=event.event||row.trigger<previousTrigger||(row.trigger==previousTrigger&&row.associate<=previous)||!std::isfinite(row.dphi)||!std::isfinite(row.deta)||!std::isfinite(row.triggerPt)||!std::isfinite(row.associatePt)||!std::isfinite(row.weight)||row.origin<1||row.origin>5||row.category<0||row.category>5)throw std::runtime_error("consumed pair row order/domain differs");if(row.trigger!=previousTrigger){previousTrigger=row.trigger;previous=std::numeric_limits<int>::min();}previous=row.associate;const auto& trigger=Heavy(lookup,heavy,row.trigger,"pair trigger");const auto& associate=Heavy(lookup,heavy,row.associate,"pair associate");if(row.trigger==row.associate||triggerMask.count(row.trigger)==0||triggerMask.at(row.trigger)!=0||!associate.final||!direct(associate))throw std::runtime_error("pair structural ownership differs");const auto query=pairByIdentity_.find({trigger.pdg,associate.pdg});const int sector=stateByPdg_.at(trigger.pdg).sector=="charm"?4:5;const int triggerCharge=sector==4?trigger.qc:trigger.qb,associateCharge=sector==4?associate.qc:associate.qb;const auto& triggerOrigin=*originMap.at({row.trigger,sector});const auto& associateOrigin=*originMap.at({row.associate,sector});int expectedOrigin=0;if(associateOrigin.origin==1){if(associateOrigin.resolution==1&&associateOrigin.rejectedHard==-1&&associateOrigin.matchedHard>=0&&associateOrigin.matchedHard!=triggerOrigin.matchedHard&&associateCharge*triggerCharge<0)expectedOrigin=1;}else if(associateOrigin.origin==2)expectedOrigin=2;else if(associateOrigin.origin==3)expectedOrigin=3;else if(associateOrigin.origin==4)expectedOrigin=4;else if(associateOrigin.origin==0)expectedOrigin=5;if(query==pairByIdentity_.end()||query->second.sign!=row.sign||expectedOrigin==0||row.origin!=expectedOrigin||!AlmostEqual(row.triggerPt,trigger.pt)||!AlmostEqual(row.associatePt,associate.pt)||!AlmostEqual(row.deta,trigger.eta-associate.eta)||row.eta1!=event.eta1||row.eta4!=event.eta4||!AlmostEqual(row.weight,event.weight)||row.category!=associate.category)throw std::runtime_error("pair cached authority/registry semantics differ");double expected=std::fmod(trigger.phi-associate.phi+2.5*kPi,2.0*kPi);if(expected<0)expected+=2.0*kPi;expected-=0.5*kPi;if(!AlmostEqual(row.dphi,expected))throw std::runtime_error("ordered dphi sign/inverse differs");}
  BuildGram(tune,block,event,heavy,triggers,pairs);
  const std::array<int,2> activityValue{{event.eta4,event.eta1}};
  for(const auto& row:triggers)if(row.mask==0){const auto& trigger=Heavy(lookup,heavy,row.heavy,"trigger");if(std::abs(trigger.eta)<=4.0)for(const auto& profile:spec_.profiles)if(ProfileTrigger(profile,trigger.pt))for(int activity=0;activity<2;++activity)for(const auto& klass:spec_.classes)if(InClass(tune,activity,klass.id,activityValue[activity]))AddCell(3,PairScope(tune,profile.id,activity,klass.id),block,triggerIndex_.at(trigger.pdg),0,event.weight);}
  for(const auto& row:pairs){const auto& trigger=Heavy(lookup,heavy,row.trigger,"pair trigger");const auto& associate=Heavy(lookup,heavy,row.associate,"pair associate");if(std::abs(trigger.eta)>4.0||std::abs(associate.eta)>4.0)continue;const auto& query=pairByIdentity_.at({trigger.pdg,associate.pdg});for(const auto& profile:spec_.profiles)if(ProfileTrigger(profile,trigger.pt)&&ProfileAssociate(profile,associate.pt)){const int integrated=IntegratedScope(tune,profile.id);AddCell(5,integrated,block,query.id*5+(row.origin-1),0,event.weight);for(int activity=0;activity<2;++activity)for(const auto& klass:spec_.classes)if(InClass(tune,activity,klass.id,activityValue[activity])){const int scope=PairScope(tune,profile.id,activity,klass.id);AddCell(2,scope,block,query.id,0,event.weight);for(const auto& correlation:spec_.correlations)if(correlation.trigger==trigger.pdg&&(associate.pdg==correlation.associate||associate.pdg==-correlation.associate)){const int component=associate.pdg==correlation.associate?0:1;AddCell(4,scope,block,correlation.id*dphiBins_+DphiBin(row.dphi),component,event.weight);}}}}
  std::map<int,std::vector<const ClosureRow*>> closureByTrigger;previousTrigger=std::numeric_limits<int>::min();previous=std::numeric_limits<int>::min();for(const auto& row:closure){if(row.event!=event.event||row.trigger<previousTrigger||(row.trigger==previousTrigger&&row.associate<=previous)||row.coefficient==0||row.visible>1||row.category<0||row.category>3)throw std::runtime_error("consumed closure row order/domain differs");if(row.trigger!=previousTrigger){previousTrigger=row.trigger;previous=std::numeric_limits<int>::min();}previous=row.associate;Heavy(lookup,heavy,row.trigger,"closure trigger");const auto& associate=Heavy(lookup,heavy,row.associate,"closure associate");const int dense=associate.category==0?0:(associate.category==4?1:(associate.category==5?2:(associate.category==2?3:-1)));if(triggerMask.count(row.trigger)==0||triggerMask.at(row.trigger)!=0||!associate.final||row.trigger==row.associate||row.visible!=(std::abs(associate.eta)<=4.0?1:0)||row.category!=dense)throw std::runtime_error("closure ownership/visible/category semantics differ");closureByTrigger[row.trigger].push_back(&row);}
  for(const auto& group:closureByTrigger){const auto& trigger=Heavy(lookup,heavy,group.first,"closure trigger");if(std::abs(trigger.eta)>4.0)continue;for(const auto& profile:spec_.profiles)if(ProfileTrigger(profile,trigger.pt)){const int scope=IntegratedScope(tune,profile.id);Accumulator full,visible;for(const auto* row:group.second){const auto& associate=Heavy(lookup,heavy,row->associate,"closure associate");const double contribution=event.weight*row->coefficient;full.Add(contribution);if(row->visible){visible.Add(contribution);closurePdgs_.insert(associate.pdg);closureSpecies_[{static_cast<std::uint32_t>(scope),static_cast<std::uint32_t>(block),triggerIndex_.at(trigger.pdg),associate.pdg}].Add(contribution);double dphi=std::fmod(trigger.phi-associate.phi+2.5*kPi,2*kPi);if(dphi<0)dphi+=2*kPi;dphi-=.5*kPi;AddCell(6,scope,block,triggerIndex_.at(trigger.pdg)*4*dphiBins_+row->category*dphiBins_+DphiBin(dphi),0,contribution);}}if(!AlmostEqual(full.Value(),event.weight))throw std::runtime_error("full closure does not equal trigger denominator");AddCell(8,scope,block,triggerIndex_.at(trigger.pdg),0,full.Value());AddCell(8,scope,block,triggerIndex_.at(trigger.pdg),1,visible.Value());}}
}

void Reducer::BuildGram(int tune,int block,const EventRow& event,const std::vector<HeavyRow>& heavy,const std::vector<TriggerRow>& triggers,const std::vector<PairRow>& pairs){
  std::unordered_map<int,std::size_t> lookup;for(std::size_t index=0;index<heavy.size();++index)lookup[heavy[index].index]=index;
  const std::array<int,2> activityValue{{event.eta4,event.eta1}};
  for(const auto& profile:spec_.profiles){std::unordered_map<int,Accumulator> vector;
    for(const auto& row:triggers)if(row.mask==0){const auto& particle=Heavy(lookup,heavy,row.heavy,"Gram trigger");if(std::abs(particle.eta)<=4.0&&ProfileTrigger(profile,particle.pt))vector[300+triggerIndex_.at(particle.pdg)].Add(event.weight);}
    for(const auto& row:pairs){const auto& trigger=Heavy(lookup,heavy,row.trigger,"Gram pair trigger");const auto& associate=Heavy(lookup,heavy,row.associate,"Gram pair associate");if(std::abs(trigger.eta)<=4.0&&std::abs(associate.eta)<=4.0&&ProfileTrigger(profile,trigger.pt)&&ProfileAssociate(profile,associate.pt))vector[pairByIdentity_.at({trigger.pdg,associate.pdg}).id].Add(event.weight);}
    std::vector<unsigned char> touched(gramFamilies_.size(), 0);
    for (const auto& item : vector) if (item.second.Value() != 0.0) {
      if (item.first < 300) touched.at(static_cast<std::size_t>(gramFamilyForPair_.at(static_cast<std::size_t>(item.first)))) = 1;
      else touched.at(static_cast<std::size_t>(referenceGramFamily_.at(static_cast<std::size_t>(item.first - 300)))) = 1;
    }
    for(int activity=0;activity<2;++activity)for(const auto& klass:spec_.classes){if(!InClass(tune,activity,klass.id,activityValue[activity]))continue;const int scope=PairScope(tune,profile.id,activity,klass.id);
      auto add=[&](int left,int right){if(left>right)std::swap(left,right);const double value=vector[left].Value()*vector[right].Value();if(value!=0.0)gram_[{2,static_cast<std::uint32_t>(scope),static_cast<std::uint32_t>(block),static_cast<std::uint32_t>(left),static_cast<std::uint32_t>(right)}].Add(value);};
      for(std::size_t familyIndex=0;familyIndex<gramFamilies_.size();++familyIndex)if(touched[familyIndex]){const auto& family=gramFamilies_[familyIndex];const int o=family.opposite,s=family.same,t=family.trigger,ro=family.referenceOpposite,rs=family.referenceSame;if(o==ro){add(o,o);add(o,s);add(o,t);add(s,s);add(s,t);add(t,t);}else{add(o,o);add(o,s);add(s,s);add(o,t);add(s,t);add(o,ro);add(o,rs);add(s,ro);add(s,rs);}}
    }
  }
}

void Reducer::FinalizeDynamicCells(){
  std::map<int,int> closureIndex;int index=0;for(int pdg:closurePdgs_)closureIndex[pdg]=index++;
  for(const auto& item:closureSpecies_){const auto& [scope,block,trigger,pdg]=item.first;cells_[{7,scope,block,static_cast<std::uint32_t>(trigger*closureIndex.size()+closureIndex.at(pdg)),0}]=item.second;}
  std::map<int,int> t1Index;index=0;for(int pdg:t1Pdgs_)t1Index[pdg]=index++;
  for(const auto& item:t1_){const auto& [scope,block,pdg]=item.first;for(int component=0;component<3;++component)if(item.second[component].fills!=0)cells_[{10,scope,block,static_cast<std::uint32_t>(t1Index.at(pdg)),static_cast<std::uint32_t>(component)}]=item.second[component];}
}

std::string Reducer::ActivityJson()const{
  std::ostringstream out;out<<'[';for(std::size_t i=0;i<activityReceipts_.size();++i){if(i)out<<',';const auto& receipt=activityReceipts_[i];out<<"{\"activity_id\":"<<receipt.activity<<",\"classes\":[";for(std::size_t j=0;j<receipt.classes.size();++j){if(j)out<<',';const auto& boundary=receipt.classes[j];out<<"{\"empty\":"<<(boundary.empty?"true":"false")<<",\"high\":"<<boundary.high<<",\"low\":"<<boundary.low<<",\"resolved\":"<<(boundary.resolved?"true":"false")<<",\"stable\":"<<(boundary.stable?"true":"false")<<'}';}out<<"],\"thresholds\":[";bool first=true;for(const auto& threshold:receipt.pooledThreshold){if(!first)out<<',';first=false;out<<"{\"below_margins\":[";const auto below=receipt.belowMargins.find(threshold.first);if(below!=receipt.belowMargins.end())for(std::size_t j=0;j<below->second.size();++j){if(j)out<<',';out<<JsonDouble(below->second[j]);}out<<"],\"complements\":[";const auto& leaves=receipt.complementThreshold.at(threshold.first);for(std::size_t j=0;j<leaves.size();++j){if(j)out<<',';out<<leaves[j];}out<<"],\"percentile\":"<<threshold.first<<",\"pooled\":"<<threshold.second<<",\"resolved\":"<<(receipt.resolved.at(threshold.first)?"true":"false")<<",\"through_margins\":[";const auto through=receipt.throughMargins.find(threshold.first);if(through!=receipt.throughMargins.end())for(std::size_t j=0;j<through->second.size();++j){if(j)out<<',';out<<JsonDouble(through->second[j]);}out<<"]}";}out<<"],\"tune\":"<<receipt.tune<<'}';}out<<']';return out.str();
}

std::string Reducer::AccountingJson()const{std::ostringstream out;out<<"{\"blocks\":[";bool first=true;for(int tune=0;tune<=maxTune_;++tune)if(tuneScope_.count(tune))for(int block=1;block<=blocks_;++block){if(!first)out<<',';first=false;const auto& value=blockAccounting_.at(static_cast<std::size_t>(tune)*blocks_+block-1);out<<"{\"attempted_events\":"<<value.attemptedEvents<<",\"block\":"<<block<<",\"sources\":"<<value.sources<<",\"successful_events\":"<<value.successfulEvents<<",\"sumabsw\":"<<JsonDouble(value.sumabsw.Value())<<",\"sumw\":"<<JsonDouble(value.sumw.Value())<<",\"sumw2\":"<<JsonDouble(value.sumw2.Value())<<",\"tune\":"<<tune<<'}';}out<<"],\"summation\":\"Neumaier compensated binary64; cells retain sumabs,row_sumw2,fills\"}";return out.str();}

std::string Reducer::DynamicJson()const{std::ostringstream out;out<<"{\"closure_species_pdgs\":[";bool first=true;for(int pdg:closurePdgs_){if(!first)out<<',';first=false;out<<pdg;}out<<"],\"t1_all_final_pdgs\":[";first=true;for(int pdg:t1Pdgs_){if(!first)out<<',';first=false;out<<pdg;}out<<"]}";return out.str();}

std::string Reducer::EstimatorAuditJson()const{
  std::map<std::string,std::uint64_t> valueStatuses,uncertaintyStatuses;std::uint64_t evaluated=0;double maxNormalizedNull=0.0;
  for(int tune=0;tune<=maxTune_;++tune){bool present=tuneScope_.count(tune)!=0;if(!present)continue;for(const auto& profile:spec_.profiles)for(int activity=0;activity<2;++activity)for(const auto& klass:spec_.classes){const int scope=PairScope(tune,profile.id,activity,klass.id);const auto activityReceipt=std::find_if(activityReceipts_.begin(),activityReceipts_.end(),[&](const auto& value){return value.tune==tune&&value.activity==activity;});std::vector<std::string> classReasons;if(!klass.integrated){const auto& boundary=activityReceipt->classes.at(klass.id);if(!boundary.stable)classReasons.push_back("CLASS_BOUNDARY_UNSTABLE");if(!boundary.resolved)classReasons.push_back("CLASS_BOUNDARY_UNRESOLVED");}
      if(!tuneDesignComplete_.at(tune))classReasons.push_back("INCOMPLETE_BLOCK_SET");
      for(const auto& os:spec_.pairs)if(os.sign==-1){const int o=os.id,s=pairByIdentity_.at({os.trigger,-os.associate}).id,t=300+triggerIndex_.at(os.trigger),ro=pairByIdentity_.at({os.trigger,os.reference}).id,rs=pairByIdentity_.at({os.trigger,-os.reference}).id;std::vector<std::vector<double>> vectors(blocks_,std::vector<double>(5,0.0));std::vector<HR::DenominatorSeries> denominators={{"shared_trigger",std::vector<double>(blocks_),std::vector<double>(blocks_),false,false},{"reference_net",std::vector<double>(blocks_),std::vector<double>(blocks_),true,false}};for(int b=1;b<=blocks_;++b){auto value=[&](int bin){const auto found=cells_.find({2,static_cast<std::uint32_t>(scope),static_cast<std::uint32_t>(b),static_cast<std::uint32_t>(bin),0});return found==cells_.end()?0.0:found->second.Value();};auto error=[&](int bin){const auto found=cells_.find({2,static_cast<std::uint32_t>(scope),static_cast<std::uint32_t>(b),static_cast<std::uint32_t>(bin),0});return found==cells_.end()?0.0:found->second.ErrorBound();};auto triggerValue=[&](){const auto found=cells_.find({3,static_cast<std::uint32_t>(scope),static_cast<std::uint32_t>(b),static_cast<std::uint32_t>(triggerIndex_.at(os.trigger)),0});return found==cells_.end()?0.0:found->second.Value();};auto triggerError=[&](){const auto found=cells_.find({3,static_cast<std::uint32_t>(scope),static_cast<std::uint32_t>(b),static_cast<std::uint32_t>(triggerIndex_.at(os.trigger)),0});return found==cells_.end()?0.0:found->second.ErrorBound();};vectors[b-1]={value(o),value(s),triggerValue(),value(ro),value(rs)};denominators[0].blocks[b-1]=vectors[b-1][2];denominators[0].absoluteErrorBounds[b-1]=triggerError();denominators[1].blocks[b-1]=vectors[b-1][3]-vectors[b-1][4];denominators[1].absoluteErrorBounds[b-1]=error(ro)+error(rs);}
        (void)t;const auto result=HR::PooledDeleteOne(vectors,[](const auto& z)->HR::FunctionValue{const double denominator=z[3]-z[4];if(denominator==0.0)return{false,{},"POOLED_DENOMINATOR_ZERO"};return{true,{(z[0]-z[1])/denominator},{}};},denominators,{},classReasons);++valueStatuses[result.valueStatus];++uncertaintyStatuses[result.uncertaintyStatus];++evaluated;}
    }}
  // Exercise the same vector covariance path on every available G9 species/axis.
  const int ptBins=static_cast<int>(spec_.ptEdges.size()+1),perSpecies=ptBins+200;for(int tune=0;tune<=maxTune_;++tune)if(tuneScope_.count(tune))for(int species=0;species<static_cast<int>(spec_.g9.size());++species)for(const auto& axis:std::vector<std::pair<int,int>>{{0,ptBins},{ptBins,100},{ptBins+100,100}}){std::vector<std::vector<double>> blocks(blocks_,std::vector<double>(axis.second));for(int b=1;b<=blocks_;++b)for(int bin=0;bin<axis.second;++bin){const auto found=cells_.find({9,static_cast<std::uint32_t>(TuneScope(tune)),static_cast<std::uint32_t>(b),static_cast<std::uint32_t>(species*perSpecies+axis.first+bin),0});if(found!=cells_.end())blocks[b-1][bin]=found->second.Value();}const std::vector<std::string> reasons=tuneDesignComplete_.at(tune)?std::vector<std::string>{}:std::vector<std::string>{"INCOMPLETE_BLOCK_SET"};const auto result=HR::PooledDeleteOne(blocks,[&](const auto& values){return HR::Normalized(0,axis.second,values);},{},{},reasons);if(!result.covariance.empty())maxNormalizedNull=std::max(maxNormalizedNull,HR::CovarianceNullResidual(result.covariance,axis.second,std::vector<double>(axis.second,1.0)));}
  std::ostringstream out;out<<"{\"evaluated_scalar_groups\":"<<evaluated<<",\"maximum_normalized_covariance_null_residual\":"<<JsonDouble(maxNormalizedNull)<<",\"policy_id\":\""<<HR::kEstimatorPolicy<<"\",\"uncertainty_status_counts\":{";bool first=true;for(const auto& item:uncertaintyStatuses){if(!first)out<<',';first=false;out<<'\"'<<JsonEscape(item.first)<<"\":"<<item.second;}out<<"},\"value_status_counts\":{";first=true;for(const auto& item:valueStatuses){if(!first)out<<',';first=false;out<<'\"'<<JsonEscape(item.first)<<"\":"<<item.second;}out<<"}}";return out.str();
}

std::string Reducer::ScientificDigest()const{
  Sha256 digest;digest.Update(std::string("cells\0",6));for(const auto& item:cells_){for(const auto& field:std::vector<std::string>{std::to_string(item.first.projection),std::to_string(item.first.scope),std::to_string(item.first.block),std::to_string(item.first.bin),std::to_string(item.first.component),DoubleHex(item.second.Value()),DoubleHex(item.second.SumAbs()),DoubleHex(item.second.SumW2()),std::to_string(item.second.fills)})DigestField(digest,field);}digest.Update(std::string("event_gram\0",11));for(const auto& item:gram_){for(const auto& field:std::vector<std::string>{std::to_string(item.first.projection),std::to_string(item.first.scope),std::to_string(item.first.block),std::to_string(item.first.left),std::to_string(item.first.right),DoubleHex(item.second.Value())})DigestField(digest,field);}return digest.FinalHex();
}

std::pair<std::string,std::string> Reducer::Write(const std::string& output,const std::string& activityJson,const std::string& dynamicJson,const std::string& estimatorJson,const std::string& scientificDigest){
  std::ostringstream metrics;metrics<<"{\"cells\":"<<cells_.size()<<",\"event_gram\":"<<gram_.size()<<",\"events\":"<<totalEvents_<<",\"input_bytes\":"<<inputBytes_<<",\"sources\":"<<totalSources_<<'}';
  const std::string accountingJson=AccountingJson();
  std::string domains=HexDecode(spec_.settings.at("compact_domains_template"));
  ReplaceOne(domains,"\"__DOMAIN_DYNAMIC_SPECIES__\"",dynamicJson);
  ReplaceAll(domains,"\"__CLOSURE_SPECIES_COUNT__\"",std::to_string(closurePdgs_.size()));
  ReplaceAll(domains,"\"__T1_SPECIES_COUNT__\"",std::to_string(t1Pdgs_.size()));
  ReplaceOne(domains,"\"__CLOSURE_BIN_COUNT__\"",std::to_string(12U*closurePdgs_.size()));
  const std::string domainsSha=Sha(domains);
  const std::string lineage=HexDecode(spec_.settings.at("input_lineage"));
  const std::string lineageSha=Sha(lineage);
  if(lineageSha!=spec_.settings.at("input_lineage_sha256")||lineageSha!=spec_.settings.at("parent_shard_set_digest"))throw std::runtime_error("compact input-lineage binding differs before write");
  std::string metadata=HexDecode(spec_.settings.at("metadata_template")),receipt=HexDecode(spec_.settings.at("receipt_template"));
  for(auto* target:{&metadata,&receipt}){ReplaceOne(*target,"\"__ACTIVITY_RECEIPTS__\"",activityJson);ReplaceOne(*target,"\"__BLOCK_ACCOUNTING__\"",accountingJson);ReplaceOne(*target,"\"__COMPACT_DOMAINS__\"",domains);ReplaceOne(*target,"__COMPACT_DOMAINS_SHA256__",domainsSha);ReplaceOne(*target,"\"__INPUT_LINEAGE__\"",lineage);ReplaceOne(*target,"\"__ESTIMATOR_AUDIT__\"",estimatorJson);ReplaceOne(*target,"\"__METRICS__\"",metrics.str());ReplaceOne(*target,"__SCIENTIFIC_DIGEST__",scientificDigest);}
  ReplaceOne(receipt,"__ACTIVITY_RECEIPTS_SHA256__",Sha(activityJson));ReplaceOne(receipt,"__BLOCK_ACCOUNTING_SHA256__",Sha(accountingJson));
  TFile file(output.c_str(),"CREATE","",ROOT::CompressionSettings(ROOT::RCompressionSetting::EAlgorithm::kZSTD,5));if(file.IsZombie())throw std::runtime_error("cannot create staged compact ROOT");
  UInt_t projection=0,scope=0,block=0,bin=0,component=0;Double_t value=0,sumabs=0,rowSumw2=0;ULong64_t fills=0;TTree cells("cells","compact block primitives");cells.SetDirectory(&file);cells.Branch("projection_id",&projection,"projection_id/i");cells.Branch("scope_id",&scope,"scope_id/i");cells.Branch("block",&block,"block/i");cells.Branch("bin",&bin,"bin/i");cells.Branch("component",&component,"component/i");cells.Branch("value",&value,"value/D");cells.Branch("sumabs",&sumabs,"sumabs/D");cells.Branch("row_sumw2",&rowSumw2,"row_sumw2/D");cells.Branch("fills",&fills,"fills/l");cells.SetAutoSave(0);cells.SetAutoFlush(-4*1024*1024);for(const auto& item:cells_){projection=item.first.projection;scope=item.first.scope;block=item.first.block;bin=item.first.bin;component=item.first.component;value=item.second.Value();sumabs=item.second.SumAbs();rowSumw2=item.second.SumW2();fills=item.second.fills;cells.Fill();}
  UInt_t left=0,right=0;Double_t cross=0;TTree gram("event_gram","event-aggregated scalar cross products");gram.SetDirectory(&file);gram.Branch("projection_id",&projection,"projection_id/i");gram.Branch("scope_id",&scope,"scope_id/i");gram.Branch("block",&block,"block/i");gram.Branch("left",&left,"left/i");gram.Branch("right",&right,"right/i");gram.Branch("cross",&cross,"cross/D");gram.SetAutoSave(0);gram.SetAutoFlush(-4*1024*1024);for(const auto& item:gram_){projection=item.first.projection;scope=item.first.scope;block=item.first.block;left=item.first.left;right=item.first.right;cross=item.second.Value();gram.Fill();}
  file.cd();cells.Write();gram.Write();TObjString metadataObject(metadata.c_str());metadataObject.Write("metadata");TObjString receiptObject(receipt.c_str());receiptObject.Write("receipt");file.Close();if(file.IsZombie())throw std::runtime_error("compact ROOT close failed");return{Sha(metadata),Sha(receipt)};
}

void Reducer::Run(const std::string& output){for(const auto& shard:spec_.shards)InspectShard(shard);for(const auto& shard:spec_.shards)FirstPass(shard);ResolveActivities();MaterializeActivityCells();for(const auto& shard:spec_.shards)SecondPass(shard);FinalizeDynamicCells();const std::string activity=ActivityJson(),accounting=AccountingJson(),dynamic=DynamicJson(),estimator=EstimatorAuditJson(),digest=ScientificDigest();const auto payloadDigests=Write(output,activity,dynamic,estimator,digest);const std::string metadataTemplate=HexDecode(spec_.settings.at("metadata_template"));std::string domains=HexDecode(spec_.settings.at("compact_domains_template"));ReplaceOne(domains,"\"__DOMAIN_DYNAMIC_SPECIES__\"",dynamic);ReplaceAll(domains,"\"__CLOSURE_SPECIES_COUNT__\"",std::to_string(closurePdgs_.size()));ReplaceAll(domains,"\"__T1_SPECIES_COUNT__\"",std::to_string(t1Pdgs_.size()));ReplaceOne(domains,"\"__CLOSURE_BIN_COUNT__\"",std::to_string(12U*closurePdgs_.size()));std::cout<<"REDUCTION_SUMMARY cells="<<cells_.size()<<" event_gram="<<gram_.size()<<" events="<<totalEvents_<<" sources="<<totalSources_<<" input_bytes="<<inputBytes_<<" scientific_digest="<<digest<<" activity_receipts_sha256="<<Sha(activity)<<" block_accounting_sha256="<<Sha(accounting)<<" compact_domains_sha256="<<Sha(domains)<<" input_lineage_sha256="<<spec_.settings.at("input_lineage_sha256")<<" dynamic_species_hex="<<HexEncode(dynamic)<<" analysis_sha256="<<spec_.settings.at("analysis_sha256")<<" plan_digest="<<spec_.settings.at("plan_digest")<<" map_digest="<<spec_.settings.at("map_digest")<<" parent_shard_set_digest="<<spec_.settings.at("parent_shard_set_digest")<<" publication_state="<<spec_.settings.at("publication_state")<<" metadata_sha256="<<payloadDigests.first<<" embedded_receipt_sha256="<<payloadDigests.second<<" build_id="<<JsonStringValue(metadataTemplate,"reducer_build_id")<<'\n';}

std::string ExtractJsonValue(const std::string& json,const std::string& key) {
  if (json.size() < 2 || json.front() != '{' || json.back() != '}') {
    throw std::runtime_error("compact JSON object type differs");
  }
  int depth = 0;
  for (std::size_t index = 0; index < json.size(); ++index) {
    const char character = json[index];
    if (character == '{' || character == '[') {
      ++depth;
      continue;
    }
    if (character == '}' || character == ']') {
      --depth;
      continue;
    }
    if (character != '"') continue;
    std::size_t end = index + 1;
    bool escaped = false;
    for (; end < json.size(); ++end) {
      if (!escaped && json[end] == '"') break;
      escaped = !escaped && json[end] == '\\';
      if (json[end] != '\\') escaped = false;
    }
    if (end >= json.size()) throw std::runtime_error("unterminated JSON string");
    const bool member = depth == 1 && json.substr(index + 1, end - index - 1) == key &&
                        end + 1 < json.size() && json[end + 1] == ':';
    index = end;
    if (!member) continue;
    const std::size_t start = end + 2;
    if (start >= json.size()) throw std::runtime_error("compact JSON value is truncated");
    if (json[start] == '"') {
      std::size_t valueEnd = start + 1;
      escaped = false;
      for (; valueEnd < json.size(); ++valueEnd) {
        if (!escaped && json[valueEnd] == '"') {
          return json.substr(start, valueEnd - start + 1);
        }
        escaped = !escaped && json[valueEnd] == '\\';
        if (json[valueEnd] != '\\') escaped = false;
      }
      throw std::runtime_error("unterminated JSON string value");
    }
    if (json[start] == '[' || json[start] == '{') {
      int containerDepth = 0;
      bool quoted = false;
      escaped = false;
      for (std::size_t valueEnd = start; valueEnd < json.size(); ++valueEnd) {
        const char valueCharacter = json[valueEnd];
        if (quoted) {
          if (!escaped && valueCharacter == '"') quoted = false;
          escaped = !escaped && valueCharacter == '\\';
          if (valueCharacter != '\\') escaped = false;
          continue;
        }
        if (valueCharacter == '"') quoted = true;
        else if (valueCharacter == '[' || valueCharacter == '{') ++containerDepth;
        else if ((valueCharacter == ']' || valueCharacter == '}') &&
                 --containerDepth == 0) {
          return json.substr(start, valueEnd - start + 1);
        }
      }
      throw std::runtime_error("unterminated JSON container value");
    }
    const auto valueEnd = json.find_first_of(",}", start);
    if (valueEnd == std::string::npos) throw std::runtime_error("unterminated JSON scalar value");
    return json.substr(start, valueEnd - start);
  }
  throw std::runtime_error("compact JSON object lacks " + key);
}
std::string JsonStringValue(const std::string& json,const std::string& key){const std::string value=ExtractJsonValue(json,key);if(value.size()<2||value.front()!='\"'||value.back()!='\"')throw std::runtime_error("compact receipt string type differs");return value.substr(1,value.size()-2);}
std::uint64_t JsonUnsignedValue(const std::string& json,const std::string& key){const std::string value=ExtractJsonValue(json,key);const long long parsed=Integer(value);if(parsed<0)throw std::runtime_error("negative compact metric");return static_cast<std::uint64_t>(parsed);}

std::vector<std::string> JsonArrayElements(const std::string& json,
                                           const std::string& key) {
  const std::string value = ExtractJsonValue(json, key);
  if (value.size() < 2 || value.front() != '[' || value.back() != ']') {
    throw std::runtime_error("compact JSON array type differs: " + key);
  }
  std::vector<std::string> result;
  std::size_t start = 1;
  int depth = 0;
  bool quoted = false;
  bool escaped = false;
  for (std::size_t index = 1; index + 1 < value.size(); ++index) {
    const char character = value[index];
    if (quoted) {
      if (!escaped && character == '"') quoted = false;
      escaped = !escaped && character == '\\';
      if (character != '\\') escaped = false;
      continue;
    }
    if (character == '"') {
      quoted = true;
    } else if (character == '[' || character == '{') {
      ++depth;
    } else if (character == ']' || character == '}') {
      --depth;
    } else if (character == ',' && depth == 0) {
      if (index == start) throw std::runtime_error("empty compact JSON array element");
      result.push_back(value.substr(start, index - start));
      start = index + 1;
    }
  }
  if (start + 1 < value.size()) result.push_back(value.substr(start, value.size() - start - 1));
  return result;
}

std::vector<std::uint64_t> JsonUnsignedArray(const std::string& json,
                                             const std::string& key) {
  std::vector<std::uint64_t> result;
  for (const auto& element : JsonArrayElements(json, key)) {
    const long long value = Integer(element);
    if (value < 0) throw std::runtime_error("negative compact JSON array value");
    result.push_back(static_cast<std::uint64_t>(value));
  }
  return result;
}

struct MaterializedDomain {
  std::set<UInt_t> scopes;
  std::set<UInt_t> components;
  std::uint64_t bins = 0;
};

struct CompactDomains {
  std::set<UInt_t> blocks;
  std::map<UInt_t, MaterializedDomain> cells;
  UInt_t gramProjection = 0;
  std::set<UInt_t> gramScopes;
  std::set<std::uint64_t> gramTermCodes;
  std::uint64_t gramTermMultiplier = 0;
  std::string payload;
  std::string lineage;
  std::string dynamicSpecies;
  std::uint64_t lineageShards = 0;
  std::uint64_t lineageSources = 0;
};

CompactDomains ReadCompactDomains(const std::string& metadata,
                                  const std::string& receipt) {
  CompactDomains result;
  result.payload = ExtractJsonValue(metadata, "compact_domains");
  result.lineage = ExtractJsonValue(metadata, "input_lineage");
  if (ExtractJsonValue(receipt, "compact_domains") != result.payload ||
      ExtractJsonValue(receipt, "input_lineage") != result.lineage) {
    throw std::runtime_error("compact contract payload cross-binding differs");
  }
  const std::string domainsSha = Sha(result.payload);
  const std::string lineageSha = Sha(result.lineage);
  if (JsonStringValue(metadata, "compact_domains_sha256") != domainsSha ||
      JsonStringValue(receipt, "compact_domains_sha256") != domainsSha ||
      JsonStringValue(metadata, "input_lineage_sha256") != lineageSha ||
      JsonStringValue(receipt, "input_lineage_sha256") != lineageSha ||
      JsonStringValue(metadata, "parent_shard_set_digest") != lineageSha ||
      JsonStringValue(receipt, "parent_shard_set_digest") != lineageSha) {
    throw std::runtime_error("compact contract payload digest/cross-binding differs");
  }
  if (JsonStringValue(result.payload, "domain_schema") !=
      "hadronization_compact_domain_contract_v1" ||
      JsonStringValue(result.lineage, "lineage_schema") !=
      "hadronization_compact_input_lineage_v1") {
    throw std::runtime_error("compact domain/lineage schema differs");
  }
  const auto blockValues = JsonUnsignedArray(result.payload, "block_ids");
  if (blockValues.size() != 10) throw std::runtime_error("compact K10 block domain differs");
  for (std::size_t index = 0; index < blockValues.size(); ++index) {
    if (blockValues[index] != index + 1) throw std::runtime_error("compact K10 block order differs");
    result.blocks.insert(static_cast<UInt_t>(blockValues[index]));
  }
  const auto projections = JsonArrayElements(result.payload, "projection_dictionary");
  if (projections.size() != 10) throw std::runtime_error("compact projection dictionary count differs");
  for (std::size_t index = 0; index < projections.size(); ++index) {
    const auto& projection = projections[index];
    const auto identifier = JsonUnsignedValue(projection, "id");
    if (identifier != index + 1 || identifier > std::numeric_limits<UInt_t>::max()) {
      throw std::runtime_error("compact projection dictionary ID/order differs");
    }
    MaterializedDomain domain;
    domain.bins = JsonUnsignedValue(projection, "bin_count");
    for (const auto value : JsonUnsignedArray(projection, "scope_ids")) {
      if (value > std::numeric_limits<UInt_t>::max()) throw std::runtime_error("compact scope ID overflows");
      domain.scopes.insert(static_cast<UInt_t>(value));
    }
    for (const auto value : JsonUnsignedArray(projection, "component_ids")) {
      if (value > std::numeric_limits<UInt_t>::max()) throw std::runtime_error("compact component ID overflows");
      domain.components.insert(static_cast<UInt_t>(value));
    }
    if (domain.scopes.empty() || domain.components.empty() ||
        !result.cells.emplace(static_cast<UInt_t>(identifier), std::move(domain)).second) {
      throw std::runtime_error("compact projection materialized domain differs");
    }
  }
  const std::string gram = ExtractJsonValue(result.payload, "event_gram_dictionary");
  result.gramProjection = static_cast<UInt_t>(JsonUnsignedValue(gram, "projection_id"));
  result.gramTermMultiplier = JsonUnsignedValue(gram, "term_code_multiplier");
  for (const auto value : JsonUnsignedArray(gram, "scope_ids")) {
    if (value > std::numeric_limits<UInt_t>::max()) throw std::runtime_error("compact Gram scope overflows");
    result.gramScopes.insert(static_cast<UInt_t>(value));
  }
  const auto componentIds = JsonUnsignedArray(gram, "component_ids");
  bool componentOrder = componentIds.size() == 312;
  for (std::size_t index = 0; index < componentIds.size(); ++index) {
    if (componentIds[index] != index) componentOrder = false;
  }
  if (!componentOrder) {
    throw std::runtime_error("compact Gram component dictionary differs");
  }
  for (const auto value : JsonUnsignedArray(gram, "allowed_term_codes")) {
    result.gramTermCodes.insert(value);
  }
  if (result.gramProjection != 2 || result.gramScopes.empty() ||
      result.gramTermMultiplier != 512 || result.gramTermCodes.size() != 1314) {
    throw std::runtime_error("compact Gram materialized domain differs");
  }
  result.dynamicSpecies = ExtractJsonValue(result.payload, "dynamic_species");
  const auto shards = JsonArrayElements(result.lineage, "shards");
  const auto sources = JsonArrayElements(result.lineage, "sources");
  if (JsonUnsignedValue(result.lineage, "shard_count") != shards.size() ||
      JsonUnsignedValue(result.lineage, "source_count") != sources.size() ||
      shards.empty() || sources.empty()) {
    throw std::runtime_error("compact lineage count differs");
  }
  std::vector<std::uint64_t> orderedSources;
  for (std::size_t index = 0; index < shards.size(); ++index) {
    std::ostringstream expectedName;
    expectedName << "shard-" << std::setw(4) << std::setfill('0') << index
                 << ".root";
    std::ostringstream expectedReceipt;
    expectedReceipt << "shard-" << std::setw(4) << std::setfill('0') << index
                    << ".json";
    if (JsonUnsignedValue(shards[index], "ordinal") != index ||
        JsonStringValue(shards[index], "root_name") != expectedName.str() ||
        JsonStringValue(shards[index], "receipt_name") != expectedReceipt.str()) {
      throw std::runtime_error("compact lineage shard order/name differs");
    }
    const auto members = JsonUnsignedArray(shards[index], "source_ids");
    orderedSources.insert(orderedSources.end(), members.begin(), members.end());
  }
  if (orderedSources.size() != sources.size()) {
    throw std::runtime_error("compact lineage source membership count differs");
  }
  for (std::size_t index = 0; index < sources.size(); ++index) {
    if (orderedSources[index] != index ||
        JsonUnsignedValue(sources[index], "source_id") != index) {
      throw std::runtime_error("compact lineage source membership/order differs");
    }
  }
  result.lineageShards = shards.size();
  result.lineageSources = sources.size();
  return result;
}

void VerifyCompact(const std::string& path){
  TFile file(path.c_str(),"READ");if(file.IsZombie())throw std::runtime_error("compact ROOT is zombie/unreadable");if(file.GetCompressionAlgorithm()!=static_cast<int>(ROOT::RCompressionSetting::EAlgorithm::kZSTD)||file.GetCompressionLevel()!=5)throw std::runtime_error("compact ROOT compression differs");std::map<std::string,std::pair<std::string,int>> keys;TIter iterator(file.GetListOfKeys());while(auto* object=iterator()){auto* key=dynamic_cast<TKey*>(object);if(key==nullptr||!keys.emplace(key->GetName(),std::make_pair(key->GetClassName(),key->GetCycle())).second)throw std::runtime_error("compact duplicate ROOT key/cycle");}const std::map<std::string,std::pair<std::string,int>> expected{{"cells",{"TTree",1}},{"event_gram",{"TTree",1}},{"metadata",{"TObjString",1}},{"receipt",{"TObjString",1}}};if(keys!=expected)throw std::runtime_error("compact exact object set/cycle differs");auto* cells=dynamic_cast<TTree*>(file.Get("cells"));auto* gram=dynamic_cast<TTree*>(file.Get("event_gram"));const std::string cellsSchema="projection_id:UInt_t,scope_id:UInt_t,block:UInt_t,bin:UInt_t,component:UInt_t,value:Double_t,sumabs:Double_t,row_sumw2:Double_t,fills:ULong64_t";const std::string gramSchema="projection_id:UInt_t,scope_id:UInt_t,block:UInt_t,left:UInt_t,right:UInt_t,cross:Double_t";if(TreeSchema(cells)!=cellsSchema||TreeSchema(gram)!=gramSchema)throw std::runtime_error("compact table branch order/set differs");
  auto* metadata=dynamic_cast<TObjString*>(file.Get("metadata"));auto* receiptObject=dynamic_cast<TObjString*>(file.Get("receipt"));if(metadata==nullptr||receiptObject==nullptr)throw std::runtime_error("compact metadata objects are absent");const std::string metadataText=metadata->GetString().Data(),receipt=receiptObject->GetString().Data();const CompactDomains domains=ReadCompactDomains(metadataText,receipt);
  UInt_t projection=0,scope=0,block=0,bin=0,component=0;Double_t value=0,sumabs=0,rowSumw2=0;ULong64_t fills=0;Branch(cells,"projection_id",&projection);Branch(cells,"scope_id",&scope);Branch(cells,"block",&block);Branch(cells,"bin",&bin);Branch(cells,"component",&component);Branch(cells,"value",&value);Branch(cells,"sumabs",&sumabs);Branch(cells,"row_sumw2",&rowSumw2);Branch(cells,"fills",&fills);Sha256 digest;digest.Update(std::string("cells\0",6));std::tuple<UInt_t,UInt_t,UInt_t,UInt_t,UInt_t> previousCell{};bool first=true;for(Long64_t row=0;row<cells->GetEntries();++row){if(cells->GetEntry(row)<=0)throw std::runtime_error("cannot read compact cell");const auto key=std::make_tuple(projection,scope,block,bin,component);const auto declared=domains.cells.find(projection);const bool outside=declared==domains.cells.end()||declared->second.scopes.count(scope)==0||domains.blocks.count(block)==0||bin>=declared->second.bins||declared->second.components.count(component)==0;if((!first&&key<=previousCell)||outside||!std::isfinite(value)||!std::isfinite(sumabs)||!std::isfinite(rowSumw2)||sumabs<0||rowSumw2<0||fills==0||sumabs+64*std::numeric_limits<double>::epsilon()*std::max(1.0,sumabs)<std::abs(value))throw std::runtime_error(outside?"compact cell key is outside the exact declared domain":"compact cell natural key/numerical domain differs");first=false;previousCell=key;for(const auto& field:std::vector<std::string>{std::to_string(projection),std::to_string(scope),std::to_string(block),std::to_string(bin),std::to_string(component),DoubleHex(value),DoubleHex(sumabs),DoubleHex(rowSumw2),std::to_string(fills)})DigestField(digest,field);}
  UInt_t left=0,right=0;Double_t cross=0;Branch(gram,"projection_id",&projection);Branch(gram,"scope_id",&scope);Branch(gram,"block",&block);Branch(gram,"left",&left);Branch(gram,"right",&right);Branch(gram,"cross",&cross);digest.Update(std::string("event_gram\0",11));std::tuple<UInt_t,UInt_t,UInt_t,UInt_t,UInt_t> previousGram{};first=true;for(Long64_t row=0;row<gram->GetEntries();++row){if(gram->GetEntry(row)<=0)throw std::runtime_error("cannot read compact Gram row");const auto key=std::make_tuple(projection,scope,block,left,right);const std::uint64_t term=static_cast<std::uint64_t>(left)*domains.gramTermMultiplier+right;const bool outside=projection!=domains.gramProjection||domains.gramScopes.count(scope)==0||domains.blocks.count(block)==0||left>right||domains.gramTermCodes.count(term)==0;if((!first&&key<=previousGram)||outside||!std::isfinite(cross))throw std::runtime_error(outside?"compact Gram key is outside the exact declared domain":"compact Gram natural key/numerical domain differs");first=false;previousGram=key;for(const auto& field:std::vector<std::string>{std::to_string(projection),std::to_string(scope),std::to_string(block),std::to_string(left),std::to_string(right),DoubleHex(cross)})DigestField(digest,field);}
  const std::string scientific=digest.FinalHex();if(metadataText.find("\"schema\":\""+std::string(kCompactSchema)+"\"")==std::string::npos||JsonStringValue(metadataText,"scientific_content_digest")!=scientific||JsonStringValue(receipt,"scientific_content_digest")!=scientific)throw std::runtime_error("compact scientific digest differs");
  const std::string analysisSha=JsonStringValue(metadataText,"analysis_request_sha256"),planDigest=JsonStringValue(metadataText,"parent_plan_digest"),mapDigest=JsonStringValue(metadataText,"parent_map_digest"),parentDigest=JsonStringValue(metadataText,"parent_shard_set_digest"),publicationState=JsonStringValue(metadataText,"publication_state"),buildId=JsonStringValue(metadataText,"reducer_build_id");
  if(JsonStringValue(receipt,"analysis_request_sha256")!=analysisSha||JsonStringValue(receipt,"parent_plan_digest")!=planDigest||JsonStringValue(receipt,"parent_map_digest")!=mapDigest||JsonStringValue(receipt,"parent_shard_set_digest")!=parentDigest||JsonStringValue(receipt,"state")!=publicationState||JsonStringValue(receipt,"reducer_build_id")!=buildId||JsonStringValue(receipt,"estimator_policy_id")!=HR::kEstimatorPolicy)throw std::runtime_error("compact embedded identity binding differs");
  const std::string activity=ExtractJsonValue(receipt,"activity_receipts"),accounting=ExtractJsonValue(receipt,"block_accounting");if(JsonStringValue(receipt,"activity_receipts_sha256")!=Sha(activity)||JsonStringValue(receipt,"block_accounting_sha256")!=Sha(accounting)||ExtractJsonValue(metadataText,"activity_receipts")!=activity||ExtractJsonValue(metadataText,"block_accounting")!=accounting)throw std::runtime_error("compact metadata payload digest differs");const std::string metrics=ExtractJsonValue(receipt,"metrics");const auto eventCount=JsonUnsignedValue(metrics,"events"),sourceCount=JsonUnsignedValue(metrics,"sources"),inputBytes=JsonUnsignedValue(metrics,"input_bytes");if(JsonUnsignedValue(metrics,"cells")!=static_cast<std::uint64_t>(cells->GetEntries())||JsonUnsignedValue(metrics,"event_gram")!=static_cast<std::uint64_t>(gram->GetEntries())||sourceCount!=domains.lineageSources)throw std::runtime_error("compact metric row/lineage counts differ");std::cout<<"REDUCTION_SUMMARY cells="<<cells->GetEntries()<<" event_gram="<<gram->GetEntries()<<" events="<<eventCount<<" sources="<<sourceCount<<" input_bytes="<<inputBytes<<" scientific_digest="<<scientific<<" activity_receipts_sha256="<<Sha(activity)<<" block_accounting_sha256="<<Sha(accounting)<<" compact_domains_sha256="<<Sha(domains.payload)<<" input_lineage_sha256="<<Sha(domains.lineage)<<" dynamic_species_hex="<<HexEncode(domains.dynamicSpecies)<<" analysis_sha256="<<analysisSha<<" plan_digest="<<planDigest<<" map_digest="<<mapDigest<<" parent_shard_set_digest="<<parentDigest<<" publication_state="<<publicationState<<" metadata_sha256="<<Sha(metadataText)<<" embedded_receipt_sha256="<<Sha(receipt)<<" build_id="<<buildId<<'\n';
}

std::uint64_t StressRandom(std::uint64_t& state) {
  state += 0x9e3779b97f4a7c15ULL;
  std::uint64_t value = state;
  value = (value ^ (value >> 30U)) * 0xbf58476d1ce4e5b9ULL;
  value = (value ^ (value >> 27U)) * 0x94d049bb133111ebULL;
  return value ^ (value >> 31U);
}

double StressUnit(std::uint64_t& state) {
  return static_cast<double>(StressRandom(state) >> 11U) * 0x1.0p-53;
}

std::pair<std::string,std::string> ReadStressSpec(const std::string& path) {
  std::ifstream input(path);
  if (!input) throw std::runtime_error("cannot open compact stress spec");
  std::vector<std::string> lines;
  for (std::string line; std::getline(input, line);) lines.push_back(line);
  if (lines.size() != 4 ||
      lines[0] != "hadronization_compact_stress_spec_v1" ||
      lines[3] != "END") {
    throw std::runtime_error("compact stress spec framing differs");
  }
  const auto metadata = Split(lines[1]);
  const auto receipt = Split(lines[2]);
  if (metadata.size() != 2 || metadata[0] != "METADATA" ||
      receipt.size() != 2 || receipt[0] != "RECEIPT") {
    throw std::runtime_error("compact stress spec payload differs");
  }
  return {HexDecode(metadata[1]), HexDecode(receipt[1])};
}

void WriteStressCompact(const std::string& specPath, const std::string& output) {
  auto templates = ReadStressSpec(specPath);
  const CompactDomains domains = ReadCompactDomains(templates.first,
                                                      templates.second);
  TFile file(output.c_str(), "CREATE", "",
             ROOT::CompressionSettings(
                 ROOT::RCompressionSetting::EAlgorithm::kZSTD, 5));
  if (file.IsZombie()) throw std::runtime_error("cannot create stress compact ROOT");
  Sha256 digest;
  digest.Update(std::string("cells\0", 6));
  UInt_t projection=0,scope=0,block=0,bin=0,component=0;
  Double_t value=0,sumabs=0,rowSumw2=0;
  ULong64_t fills=0;
  TTree cells("cells", "compact block primitives");
  cells.SetDirectory(&file);
  cells.Branch("projection_id",&projection,"projection_id/i");cells.Branch("scope_id",&scope,"scope_id/i");cells.Branch("block",&block,"block/i");cells.Branch("bin",&bin,"bin/i");cells.Branch("component",&component,"component/i");cells.Branch("value",&value,"value/D");cells.Branch("sumabs",&sumabs,"sumabs/D");cells.Branch("row_sumw2",&rowSumw2,"row_sumw2/D");cells.Branch("fills",&fills,"fills/l");cells.SetAutoSave(0);cells.SetAutoFlush(-4*1024*1024);
  std::uint64_t randomState=0x5245445543453155ULL;
  std::uint64_t cellRows = 0;
  for (const auto& declared : domains.cells) {
    projection = declared.first;
    for (const UInt_t declaredScope : declared.second.scopes) {
      scope = declaredScope;
      for (const UInt_t declaredBlock : domains.blocks) {
        block = declaredBlock;
        for (std::uint64_t declaredBin = 0;
             declaredBin < declared.second.bins; ++declaredBin) {
          bin = static_cast<UInt_t>(declaredBin);
          for (const UInt_t declaredComponent : declared.second.components) {
            component = declaredComponent;
            value=2.0*StressUnit(randomState)-1.0;sumabs=std::abs(value)+0.01*StressUnit(randomState)+1e-12;rowSumw2=value*value+0.01*StressUnit(randomState)+1e-12;fills=1ULL+StressRandom(randomState)%17ULL;cells.Fill();for(const auto& field:std::vector<std::string>{std::to_string(projection),std::to_string(scope),std::to_string(block),std::to_string(bin),std::to_string(component),DoubleHex(value),DoubleHex(sumabs),DoubleHex(rowSumw2),std::to_string(fills)})DigestField(digest,field);
            ++cellRows;
          }
        }
      }
    }
  }
  digest.Update(std::string("event_gram\0",11));
  UInt_t left=0,right=0;Double_t cross=0;
  TTree gram("event_gram","event-aggregated scalar cross products");gram.SetDirectory(&file);gram.Branch("projection_id",&projection,"projection_id/i");gram.Branch("scope_id",&scope,"scope_id/i");gram.Branch("block",&block,"block/i");gram.Branch("left",&left,"left/i");gram.Branch("right",&right,"right/i");gram.Branch("cross",&cross,"cross/D");gram.SetAutoSave(0);gram.SetAutoFlush(-4*1024*1024);
  projection = domains.gramProjection;
  std::uint64_t gramRows = 0;
  for (const UInt_t declaredScope : domains.gramScopes) {
    scope = declaredScope;
    for (const UInt_t declaredBlock : domains.blocks) {
      block = declaredBlock;
      for (const std::uint64_t term : domains.gramTermCodes) {
        left = static_cast<UInt_t>(term / domains.gramTermMultiplier);
        right = static_cast<UInt_t>(term % domains.gramTermMultiplier);
        cross=2.0*StressUnit(randomState)-1.0;gram.Fill();for(const auto& field:std::vector<std::string>{std::to_string(projection),std::to_string(scope),std::to_string(block),std::to_string(left),std::to_string(right),DoubleHex(cross)})DigestField(digest,field);
        ++gramRows;
      }
    }
  }
  const std::string scientific=digest.FinalHex();
  std::string metadata = templates.first;
  std::string receipt = templates.second;
  ReplaceOne(metadata, "\"__SCIENTIFIC_DIGEST__\"", "\""+scientific+"\"");
  ReplaceOne(receipt, "\"__SCIENTIFIC_DIGEST__\"", "\""+scientific+"\"");
  file.cd();cells.Write();gram.Write();TObjString metadataObject(metadata.c_str());metadataObject.Write("metadata");TObjString receiptObject(receipt.c_str());receiptObject.Write("receipt");file.Close();if(file.IsZombie())throw std::runtime_error("stress compact ROOT close failed");
  VerifyCompact(output);
  std::ifstream input(output,std::ios::binary|std::ios::ate);if(!input)throw std::runtime_error("cannot stat stress compact ROOT");std::cout<<"STRESS_SUMMARY bytes="<<static_cast<std::uint64_t>(input.tellg())<<" cells="<<cellRows<<" event_gram="<<gramRows<<" lineage_sources="<<domains.lineageSources<<" lineage_shards="<<domains.lineageShards<<'\n';
}

int Main(int argc,char** argv){if(argc<2)throw std::runtime_error("usage: reduce <reduce|verify|stress> ...");const std::string command=argv[1];if(command=="reduce"){if(argc!=4)throw std::runtime_error("usage: reduce reduce SPEC OUTPUT");Reducer reducer(ReadSpec(argv[2]));reducer.Run(argv[3]);return 0;}if(command=="verify"){if(argc!=3)throw std::runtime_error("usage: reduce verify ROOT");VerifyCompact(argv[2]);return 0;}if(command=="stress"){if(argc!=4)throw std::runtime_error("usage: reduce stress SPEC ROOT");WriteStressCompact(argv[2],argv[3]);return 0;}throw std::runtime_error("unknown reducer command");}

}  // namespace

int main(int argc,char** argv){try{return Main(argc,argv);}catch(const std::exception& error){std::cerr<<"ERROR: "<<error.what()<<'\n';return 2;}}
