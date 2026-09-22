#include "selection.hpp"
#include "row_schema.hpp"
#include "../generate/sha256.hpp"
#include "TFile.h"
#include "TAxis.h"
#include "THnSparse.h"
#include "TKey.h"
#include "TLeaf.h"
#include "TObjString.h"
#include "TTree.h"
#include "Compression.h"

#include <algorithm>
#include <array>
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
#include <utility>
#include <vector>

namespace {
using U64 = std::uint64_t;
using Values = std::map<std::string, double>;
struct Axis { std::vector<double> edges; bool inclusive = false; };
struct Layout {
  std::map<std::string, std::vector<std::string>> trees, sparse;
  std::map<std::string, Axis> axes;
  std::set<int> pdgs;
  std::set<int> triggerPdgs;
  std::map<int,std::set<int>> associatePdgs;
  std::vector<HadronizationQuery::Profile> profiles;
  std::string text, analysisVersion, contentSha, scientificBindingSha, executionAttestationSha,
              dictionarySha, sparseDigestSchema;
};

std::vector<std::string> Split(const std::string& text) {
  std::vector<std::string> result;
  std::istringstream stream(text);
  for (std::string value; std::getline(stream, value, '\t');) result.push_back(value);
  return result;
}

std::string ReadText(const std::string& path) {
  std::ifstream input(path);
  if (!input) throw std::runtime_error("cannot read " + path);
  return {std::istreambuf_iterator<char>(input), std::istreambuf_iterator<char>()};
}

Layout ReadLayout(const std::string& text) {
  Layout layout; layout.text = text;
  std::istringstream input(text);
  std::string line;
  if (!std::getline(input, line) ||
      (line != "hadronization_root_query_spec_v3" && line != "hadronization_root_query_spec_v4"))
    throw std::runtime_error("query spec schema differs");
  const bool legacySpec=line=="hadronization_root_query_spec_v3";
  if (legacySpec) layout.sparseDigestSchema="hadronization_query_sparse_content_v1";
  bool ended = false;
  while (std::getline(input, line)) {
    const auto fields = Split(line);
    if (fields == std::vector<std::string>{"END"}) { ended = true; break; }
    if (fields.size() == 2 && fields[0] == "ANALYSIS_VERSION" && layout.analysisVersion.empty() && fields[1]=="2.2.0") {
      layout.analysisVersion=fields[1];
    } else if (fields.size() == 2 && fields[0] == "CONTENT_SHA256" && layout.contentSha.empty()) {
      layout.contentSha=fields[1];
    } else if (fields.size() == 2 && fields[0] == "SCIENTIFIC_BINDING_SHA256" && layout.scientificBindingSha.empty()) {
      layout.scientificBindingSha=fields[1];
    } else if (fields.size() == 2 && fields[0] == "EXECUTION_ATTESTATION_SHA256" && layout.executionAttestationSha.empty()) {
      layout.executionAttestationSha=fields[1];
    } else if (fields.size() == 2 && fields[0] == "DICTIONARY_SHA256" && layout.dictionarySha.empty()) {
      layout.dictionarySha=fields[1];
    } else if (fields.size() == 2 && fields[0] == "SPARSE_DIGEST_SCHEMA" &&
               layout.sparseDigestSchema.empty() && !legacySpec &&
               fields[1] == "hadronization_query_sparse_content_v2") {
      layout.sparseDigestSchema=fields[1];
    } else if (fields.size() == 6 && fields[0] == "PROFILE") {
      layout.profiles.push_back(HadronizationQuery::ReadProfile(
          std::stoi(fields[1]),fields[2],fields[3],fields[4],fields[5]));
    } else if (fields.size() >= 3 && (fields[0] == "TREE" || fields[0] == "SPARSE")) {
      auto& target = fields[0] == "TREE" ? layout.trees : layout.sparse;
      if (!target.emplace(fields[1], std::vector<std::string>(fields.begin()+2, fields.end())).second)
        throw std::runtime_error("duplicate query object");
    } else if (fields.size() >= 5 && fields[0] == "AXIS") {
      Axis axis; axis.inclusive = fields[2] == "inclusive";
      if (!axis.inclusive && fields[2] != "halfopen") throw std::runtime_error("axis endpoint differs");
      for (std::size_t i=3; i<fields.size(); ++i) {
        const double value=HadronizationQuery::ReadFiniteDouble(fields[i]);
        if (!std::isfinite(value) ||
            (!axis.edges.empty() && value <= axis.edges.back())) throw std::runtime_error("axis edges differ");
        axis.edges.push_back(value);
      }
      if (!layout.axes.emplace(fields[1], axis).second) throw std::runtime_error("duplicate axis");
    } else if (fields.size() == 2 && fields[0] == "TRIGGER") {
      const int pdg=std::stoi(fields[1]);
      if (pdg==0 || !layout.triggerPdgs.insert(pdg).second)
        throw std::runtime_error("duplicate/invalid trigger PDG in query spec");
    } else if (fields.size() == 3 && fields[0] == "ASSOCIATE") {
      const int sector=std::stoi(fields[1]),pdg=std::stoi(fields[2]);
      if ((sector!=4 && sector!=5) || pdg==0 || !layout.associatePdgs[sector].insert(pdg).second)
        throw std::runtime_error("duplicate/invalid associate PDG in query spec");
    } else if (fields.size() == 2 && fields[0] == "PDG") {
      std::size_t consumed=0; const int pdg=std::stoi(fields[1],&consumed);
      if (consumed!=fields[1].size() || std::to_string(pdg)!=fields[1] || pdg==0 ||
          (!layout.pdgs.empty() && pdg<=*layout.pdgs.rbegin()) || !layout.pdgs.insert(pdg).second)
        throw std::runtime_error("noncanonical/unsorted campaign PDG dictionary");
    } else throw std::runtime_error("unknown query spec record");
  }
  if (!ended || input.peek() != std::istringstream::traits_type::eof() || layout.pdgs.empty() ||
      layout.sparseDigestSchema != (legacySpec ? "hadronization_query_sparse_content_v1" :
                                                "hadronization_query_sparse_content_v2") ||
      (layout.analysisVersion=="2.2.0" && (layout.triggerPdgs.empty() ||
       layout.associatePdgs[4].empty() || layout.associatePdgs[5].empty())))
    throw std::runtime_error("query spec ending differs");
  Axis species;
  for (std::size_t i=0;i<=layout.pdgs.size();++i)
    species.edges.push_back(static_cast<double>(i)-0.5);
  for (const std::string name:{"pdg","trigger_pdg","associate_pdg"})
    if (!layout.axes.emplace(name,species).second)
      throw std::runtime_error("query spec declares reserved dictionary axis");
  return layout;
}

class Rows {
 public:
  explicit Rows(TFile& file, const std::string& name) {
    tree = dynamic_cast<TTree*>(file.Get(name.c_str()));
    if (!tree) throw std::runtime_error("missing exact tree " + name);
  }
  bool Next() {
    if (++index == tree->GetEntries()) return false;
    if (tree->GetEntry(index) <= 0) throw std::runtime_error("cannot read exact row");
    return true;
  }
  TLeaf* Leaf(const std::string& name) const {
    auto* leaf = tree->GetLeaf(name.c_str());
    if (!leaf) throw std::runtime_error("missing exact column " + name);
    return leaf;
  }
  double D(const std::string& name) const {
    const double value = Leaf(name)->GetValue();
    if (!std::isfinite(value)) throw std::runtime_error("nonfinite exact coordinate " + name);
    return value;
  }
  U64 U(const std::string& name) const { return static_cast<U64>(Leaf(name)->GetValueLong64()); }
  int I(const std::string& name) const { return static_cast<int>(Leaf(name)->GetValueLong64()); }
  TTree* tree = nullptr;
  Long64_t index = -1;
};

struct Source { int tune=0, block=0; U64 events=0, seen=0, logical=0; };
struct Range { U64 first=0, count=0; int source=0; };
struct Ownership {
  std::map<int, Source> sources;
  std::vector<Range> ranges;
  explicit Ownership(TFile& file,const Layout& layout) {
    const int tuneCount=static_cast<int>(layout.axes.at("tune").edges.size()-1);
    const int blockCount=static_cast<int>(layout.axes.at("block").edges.size()-1);
    Rows rows(file,"sources");
    while (rows.Next()) {
      const int id=rows.I("source_id"), tune=rows.I("tune");
      if (id != static_cast<int>(sources.size()) || tune < 0 || tune >= tuneCount ||
          !sources.emplace(id,Source{tune,0,rows.U("events"),0,rows.U("logical_id")}).second)
        throw std::runtime_error("source identity differs");
    }
    Rows blocks(file,"source_blocks");
    while (blocks.Next()) {
      auto& source=sources.at(blocks.I("source_id"));
      const int block=blocks.I("block");
      if (source.block || block!=static_cast<int>(source.logical%blockCount+1) || blocks.I("assignment_id")!=0)
        throw std::runtime_error("source block duplication/domain differs");
      source.block=block;
    }
    Rows intervals(file,"event_ranges");
    while (intervals.Next()) {
      Range range{intervals.U("first_id"), intervals.U("count"), intervals.I("source_id")};
      if (!range.count || range.first > std::numeric_limits<U64>::max()-range.count ||
          !sources.count(range.source) || (!ranges.empty() && range.first < ranges.back().first+ranges.back().count))
        throw std::runtime_error("source event range differs");
      ranges.push_back(range);
    }
    if (sources.empty() || ranges.empty()) throw std::runtime_error("source coverage is empty");
    for (const auto& item:sources) if (!item.second.block) throw std::runtime_error("source block is missing");
  }
  Source& For(U64 event) {
    auto it=std::upper_bound(ranges.begin(),ranges.end(),event,
                           [](U64 value,const Range& range){return value<range.first;});
    if (it==ranges.begin()) throw std::runtime_error("event has no source range");
    --it;
    if (event-it->first>=it->count) throw std::runtime_error("event lies in source range gap");
    return sources.at(it->source);
  }
  void Finish() const {
    for (const auto& item:sources) if (item.second.events!=item.second.seen)
      throw std::runtime_error("source event coverage differs");
  }
};

struct Particle {
  int pdg=0,status=0,final=0,selected=0,pairEligible=0,qc=0,qb=0,category=0;
  double pt=0,eta=0,phi=0;
};
struct OriginDecision { int origin=0,resolution=0,matched=-1,rejected=-1,depth=-1; };

void CheckOrigin(const OriginDecision& o,U64 event,int index,int sector) {
  const bool selected=o.origin==1 && o.resolution==1 && o.matched>=0 && o.rejected==-1 && o.depth>=1;
  const bool resolved=o.origin>=2 && o.origin<=4 && o.resolution==1 && o.matched==-1 && o.rejected==-1 && o.depth>=1;
  const bool unresolved=o.origin==0 && o.resolution>=2 && o.resolution<=6 && o.matched==-1 && o.depth>=-1 &&
      ((o.resolution==5 && o.rejected>=0) || (o.resolution>=2 && o.resolution<=4 && o.rejected==-1) || o.resolution==6);
  if (!selected && !resolved && !unresolved)
    throw std::runtime_error("malformed mandatory pair provenance event="+std::to_string(event)+
                             " heavy="+std::to_string(index)+" sector="+std::to_string(sector));
}

struct PairProof {
  U64 events=0,eligibleTriggers=0,zeroPartnerTriggers=0,candidates=0,stored=0;
  std::map<std::tuple<int,int,int>,U64> byTuneSectorSign;
  std::string Json(const std::string& binding) const {
    std::ostringstream out;
    out<<"{\"schema\":\"hadronization_pair_population_proof_v1\",\"state\":\"PASS\","
       <<"\"scientific_binding_sha256\":\""<<binding<<"\",\"events\":"<<events
       <<",\"eligible_triggers\":"<<eligibleTriggers
       <<",\"zero_partner_triggers\":"<<zeroPartnerTriggers
       <<",\"candidate_pairs\":"<<candidates<<",\"stored_pairs\":"<<stored<<",\"by_tune_sector_sign\":[";
    bool first=true;
    for (const auto& item:byTuneSectorSign) {
      if (!first) out<<',';
      first=false;
      out<<"{\"tune_ordinal\":"<<std::get<0>(item.first)
         <<",\"sector\":"<<std::get<1>(item.first)
         <<",\"sign\":"<<std::get<2>(item.first)
         <<",\"count\":"<<item.second<<'}';
    }
    out<<"]}"; return out.str();
  }
  std::string CanonicalJson(const std::string& binding) const {
    std::ostringstream out;
    out<<"{\"by_tune_sector_sign\":[";
    bool first=true;
    for (const auto& item:byTuneSectorSign) {
      if (!first) out<<',';
      first=false;
      out<<"{\"count\":"<<item.second
         <<",\"sector\":"<<std::get<1>(item.first)
         <<",\"sign\":"<<std::get<2>(item.first)
         <<",\"tune_ordinal\":"<<std::get<0>(item.first)<<'}';
    }
    out<<"],\"candidate_pairs\":"<<candidates
       <<",\"eligible_triggers\":"<<eligibleTriggers
       <<",\"events\":"<<events
       <<",\"schema\":\"hadronization_pair_population_proof_v1\""
       <<",\"scientific_binding_sha256\":\""<<binding
       <<"\",\"state\":\"PASS\",\"stored_pairs\":"<<stored
       <<",\"zero_partner_triggers\":"<<zeroPartnerTriggers<<'}';
    return out.str();
  }
};
using Histograms = std::map<std::string,std::unique_ptr<THnSparseD>>;
struct Plane {
  Layout layout;
  Histograms histograms;
  std::map<int,int> dictionary;
  explicit Plane(TFile&,Layout requested) : layout(std::move(requested)) {
    for (const int pdg:layout.pdgs) dictionary.emplace(pdg,static_cast<int>(dictionary.size()));
    for (const auto& object:layout.sparse) {
      std::vector<int> bins; std::vector<double> low,high;
      for (const auto& name:object.second) {
        const auto& axis=layout.axes.at(name);
        bins.push_back(static_cast<int>(axis.edges.size()-1));
        low.push_back(axis.edges.front()); high.push_back(axis.edges.back());
      }
      const std::string name="sparse_"+object.first;
      auto histogram=std::make_unique<THnSparseD>(name.c_str(),name.c_str(),
          static_cast<int>(bins.size()),bins.data(),low.data(),high.data());
      histogram->Sumw2();
      for (std::size_t i=0;i<object.second.size();++i) {
        const auto& axisName=object.second[i];
        histogram->SetBinEdges(static_cast<int>(i),layout.axes.at(axisName).edges.data());
        auto* axis=histogram->GetAxis(static_cast<int>(i));
        axis->SetName(axisName.c_str()); axis->SetTitle(axisName.c_str());
        if (axisName=="pdg" || axisName=="trigger_pdg" || axisName=="associate_pdg")
          for (const auto& entry:dictionary) axis->SetBinLabel(entry.second+1,std::to_string(entry.first).c_str());
      }
      histograms.emplace(object.first,std::move(histogram));
    }
  }
  void RequirePdg(int pdg) const {
    if (!dictionary.count(pdg)) throw std::runtime_error("unknown PDG outside frozen campaign dictionary: "+std::to_string(pdg));
  }
  void Fill(const std::string& name,const Values& values,double weight) {
    std::vector<double> coordinates;
    for (const auto& field:layout.sparse.at(name)) {
      double value=values.at(field);
      if (!std::isfinite(value) || !std::isfinite(weight)) throw std::runtime_error("nonfinite sparse fill");
      if (field=="pdg" || field=="trigger_pdg" || field=="associate_pdg") value=dictionary.at(static_cast<int>(value));
      const auto& axis=layout.axes.at(field);
      if (axis.inclusive && value==axis.edges.back()) value=std::nextafter(value,axis.edges.front());
      coordinates.push_back(value);
    }
    histograms.at(name)->Fill(coordinates.data(),weight);
  }
};

void ParticleValues(Values& values,const Particle& particle,const std::string& prefix) {
  values[prefix+"pdg"]=particle.pdg; values[prefix+"pt"]=particle.pt;
  values[prefix+"eta"]=particle.eta; values[prefix+"phi"]=particle.phi;
}

PairProof Populate(TFile& file,Plane& plane) {
  Ownership ownership(file,plane.layout);
  Rows events(file,"events"),heavy(file,"heavy"),triggers(file,"triggers"),
       pairs(file,"pairs"),closure(file,"closure"),origins(file,"origins");
  bool haveHeavy=heavy.Next(),haveTrigger=triggers.Next(),havePair=pairs.Next(),
       haveClosure=closure.Next(),haveOrigin=origins.Next();
  PairProof proof;
  U64 previous=0; bool first=true;
  while (events.Next()) {
    const U64 event=events.U("event_id");
    if (!first && event<=previous) throw std::runtime_error("exact event ordering differs");
    first=false; previous=event;
    auto& source=ownership.For(event); ++source.seen;
    ++proof.events;
    const double weight=events.D("weight");
    Values base{{"tune",source.tune},{"block",source.block},
                {"a15_eta4",events.I("a15_eta4")},{"a15_eta1",events.I("a15_eta1")}};
    plane.Fill("activity",base,weight);
    std::map<int,Particle> particles;
    while (haveHeavy && heavy.U("event_id")==event) {
      Particle particle{heavy.I("pdg"),heavy.I("status"),heavy.I("final"),
          heavy.I("selected"),heavy.I("pair_eligible"),heavy.I("qc"),heavy.I("qb"),
          heavy.I("category"),heavy.D("pt"),heavy.D("eta"),heavy.D("phi")};
      plane.RequirePdg(particle.pdg);
      if (!particles.emplace(heavy.I("heavy_index"),particle).second) throw std::runtime_error("duplicate heavy key");
      if (heavy.I("final") && heavy.I("selected") && heavy.I("status")>=81 && heavy.I("status")<=89) {
        auto values=base; ParticleValues(values,particle,""); plane.Fill("kinematics",values,weight);
      }
      haveHeavy=heavy.Next();
    }
    std::map<std::pair<int,int>,OriginDecision> originMap;
    while (haveOrigin && origins.U("event_id")==event) {
      const int index=origins.I("heavy_index"),sector=origins.I("sector");
      if (!particles.count(index) || (sector!=4 && sector!=5) ||
          !originMap.emplace(std::make_pair(index,sector),OriginDecision{
              origins.I("origin"),origins.I("resolution"),origins.I("matched_hard"),
              origins.I("rejected_hard"),origins.I("depth")}).second)
        throw std::runtime_error("pair provenance foreign/duplicate key event="+std::to_string(event));
      haveOrigin=origins.Next();
    }
    std::map<std::pair<int,int>,int> expectedPairs;
    std::set<int> acceptedTriggers;
    while (haveTrigger && triggers.U("event_id")==event) {
      if (!triggers.I("rejection_mask")) {
        const int triggerIndex=triggers.I("heavy_index"),sector=triggers.I("sector");
        const auto& trigger=particles.at(triggerIndex);
        if (plane.layout.analysisVersion=="2.2.0" && ((sector!=4 && sector!=5) || !acceptedTriggers.insert(triggerIndex).second ||
            !trigger.final || !trigger.selected || trigger.status<81 || trigger.status>89 ||
            (sector==4 ? std::abs(trigger.qc) : std::abs(trigger.qb))!=1 ||
            !plane.layout.triggerPdgs.count(trigger.pdg)))
          throw std::runtime_error("accepted trigger structural key differs event="+std::to_string(event));
        const auto found=originMap.find({triggerIndex,sector});
        if (plane.layout.analysisVersion=="2.2.0" && found==originMap.end()) throw std::runtime_error("missing mandatory trigger provenance event="+std::to_string(event));
        if (plane.layout.analysisVersion=="2.2.0") CheckOrigin(found->second,event,triggerIndex,sector);
        if (plane.layout.analysisVersion=="2.2.0" && found->second.origin!=1)
          throw std::runtime_error("accepted trigger hard-root provenance differs event="+std::to_string(event));
        auto values=base; ParticleValues(values,trigger,"trigger_");
        plane.Fill("triggers",values,weight);
        if (plane.layout.analysisVersion=="2.2.0" && std::abs(trigger.eta)<=4.0) {
          ++proof.eligibleTriggers;
          U64 partners=0;
          for (const auto& item:particles) {
            const auto& associate=item.second;
            if (item.first==triggerIndex || !associate.final || !associate.selected ||
                !associate.pairEligible || associate.status<81 || associate.status>89 ||
                std::abs(associate.eta)>4.0 ||
                !plane.layout.associatePdgs.at(sector).count(associate.pdg) ||
                (sector==4 ? associate.qc : associate.qb)==0) continue;
            const auto origin=originMap.find({item.first,sector});
            if (origin==originMap.end())
              throw std::runtime_error("missing mandatory associate provenance event="+std::to_string(event)+
                                       " heavy="+std::to_string(item.first));
            CheckOrigin(origin->second,event,item.first,sector);
            const int sign=(sector==4 ? trigger.qc*associate.qc : trigger.qb*associate.qb)<0?-1:1;
            if (!expectedPairs.emplace(std::make_pair(triggerIndex,item.first),sign).second)
              throw std::runtime_error("duplicate candidate pair key event="+std::to_string(event));
            ++proof.candidates; ++partners;
            ++proof.byTuneSectorSign[{source.tune,sector,sign}];
          }
          if (!partners) ++proof.zeroPartnerTriggers;
        }
      }
      haveTrigger=triggers.Next();
    }
    std::set<std::pair<int,int>> observedPairs;
    while (havePair && pairs.U("event_id")==event) {
      auto values=base;
      const int triggerIndex=pairs.I("trigger_heavy_index"),associateIndex=pairs.I("associate_heavy_index");
      const auto& trigger=particles.at(triggerIndex);
      const auto& associate=particles.at(associateIndex);
      const auto expected=expectedPairs.find({triggerIndex,associateIndex});
      if (expected!=expectedPairs.end()) {
        if (!observedPairs.insert({triggerIndex,associateIndex}).second)
          throw std::runtime_error("duplicate in-domain pair event="+std::to_string(event)+
                                   " trigger="+std::to_string(triggerIndex)+" associate="+std::to_string(associateIndex));
        constexpr double pi=3.14159265358979323846;
        const double dphi=std::fmod(trigger.phi-associate.phi+2.5*pi,2.0*pi)-0.5*pi;
        if (pairs.I("sign")!=expected->second || pairs.D("dphi")!=dphi ||
            pairs.D("deta")!=trigger.eta-associate.eta ||
            pairs.D("trigger_pt")!=trigger.pt || pairs.D("associate_pt")!=associate.pt ||
            pairs.D("weight")!=weight || pairs.I("associate_category")!=associate.category ||
            pairs.I("a15_eta1")!=events.I("a15_eta1") || pairs.I("a15_eta4")!=events.I("a15_eta4"))
          throw std::runtime_error("in-domain pair cached authority differs event="+std::to_string(event)+
                                   " trigger="+std::to_string(triggerIndex)+" associate="+std::to_string(associateIndex));
        ++proof.stored;
      } else if (acceptedTriggers.count(triggerIndex) && triggerIndex!=associateIndex &&
                 std::abs(trigger.eta)<=4.0 && std::abs(associate.eta)<=4.0 &&
                 associate.final && associate.selected && associate.pairEligible &&
                 associate.status>=81 && associate.status<=89 &&
                 plane.layout.associatePdgs.at(trigger.qc!=0?4:5).count(associate.pdg))
        throw std::runtime_error("extra in-domain pair event="+std::to_string(event)+
                                 " trigger="+std::to_string(triggerIndex)+" associate="+std::to_string(associateIndex)+
                                 " trigger_pdg="+std::to_string(trigger.pdg)+" associate_pdg="+std::to_string(associate.pdg));
      ParticleValues(values,trigger,"trigger_"); ParticleValues(values,associate,"associate_");
      if (pairs.D("trigger_pt")!=trigger.pt || pairs.D("associate_pt")!=associate.pt || pairs.D("weight")!=weight)
        throw std::runtime_error("exact pair cache differs");
      values["sign"]=pairs.I("sign"); values["dphi"]=pairs.D("dphi"); values["deta"]=pairs.D("deta");
      values["origin"]=pairs.I("associate_origin"); values["category"]=pairs.I("associate_category");
      plane.Fill("pairs",values,weight);
      havePair=pairs.Next();
    }
    if (observedPairs.size()!=expectedPairs.size())
      for (const auto& candidate:expectedPairs)
        if (!observedPairs.count(candidate.first))
          throw std::runtime_error("missing in-domain pair event="+std::to_string(event)+
                                   " trigger="+std::to_string(candidate.first.first)+
                                   " associate="+std::to_string(candidate.first.second)+
                                   " trigger_pdg="+std::to_string(particles.at(candidate.first.first).pdg)+
                                   " associate_pdg="+std::to_string(particles.at(candidate.first.second).pdg)+
                                   " sign="+std::to_string(candidate.second));
    while (haveClosure && closure.U("event_id")==event) {
      auto values=base;
      const auto& trigger=particles.at(closure.I("trigger_heavy_index"));
      const auto& associate=particles.at(closure.I("associate_heavy_index"));
      ParticleValues(values,trigger,"trigger_"); ParticleValues(values,associate,"associate_");
      // The accepted ordered-dphi convention, evaluated from retained binary64 phi.
      const double pi=std::acos(-1.0);
      double dphi=std::fmod(trigger.phi-associate.phi+2.5*pi,2*pi);
      if (dphi<0) dphi+=2*pi;
      values["dphi"]=dphi-0.5*pi; values["category"]=closure.I("dense_category");
      plane.Fill("closure",values,weight*closure.I("coefficient")); haveClosure=closure.Next();
    }
    for (const auto& cursor:std::vector<std::pair<Rows*,bool>>{
         {&heavy,haveHeavy},{&triggers,haveTrigger},{&pairs,havePair},{&closure,haveClosure},{&origins,haveOrigin}})
      if (cursor.second && cursor.first->U("event_id")<event) throw std::runtime_error("orphan exact row");
  }
  if (haveHeavy || haveTrigger || havePair || haveClosure || haveOrigin) throw std::runtime_error("trailing exact rows");
  ownership.Finish();
  return proof;
}

void CheckHistogram(const THnSparseD& expected,const THnSparseD& actual) {
  if (!actual.GetCalculateErrors() || expected.GetNdimensions()!=actual.GetNdimensions() ||
      expected.GetNbins()!=actual.GetNbins() || expected.GetEntries()!=actual.GetEntries())
    throw std::runtime_error("sparse Sumw2/shape/fill count differs");
  for (int i=0;i<expected.GetNdimensions();++i) {
    const auto* e=expected.GetAxis(i); const auto* a=actual.GetAxis(i);
    if (e->GetNbins()!=a->GetNbins() || std::string(e->GetName())!=a->GetName())
      throw std::runtime_error("sparse axis identity differs");
    for (int b=1;b<=e->GetNbins()+1;++b)
      if (e->GetBinLowEdge(b)!=a->GetBinLowEdge(b) ||
          std::string(e->GetBinLabel(b))!=a->GetBinLabel(b)) throw std::runtime_error("sparse axis/dictionary differs");
  }
  std::vector<int> ebin(expected.GetNdimensions()),abin(actual.GetNdimensions());
  for (Long64_t b=0;b<expected.GetNbins();++b)
    if (expected.GetBinContent(b,ebin.data())!=actual.GetBinContent(b,abin.data()) ||
        ebin!=abin || expected.GetBinError2(b)!=actual.GetBinError2(b))
      throw std::runtime_error("sparse cells/Sumw2 differ from exact rows");
}

void DigestField(Hadronization::Sha256& digest,const std::string& value) {
  const U64 length=value.size();
  std::array<unsigned char,8> bytes{};
  for (unsigned i=0;i<8;++i) bytes[7-i]=static_cast<unsigned char>(length>>(8*i));
  digest.Update(reinterpret_cast<const char*>(bytes.data()),bytes.size()); digest.Update(value);
}

std::string DoubleBits(double value) {
  static_assert(sizeof(double)==sizeof(U64),"binary64 required");
  U64 bits=0;std::memcpy(&bits,&value,sizeof(bits));
  std::ostringstream result;result<<std::hex<<std::setfill('0')<<std::setw(16)<<bits;
  return result.str();
}

std::string TreeDigest(TFile& file,const std::string& name,const std::vector<std::string>& fields) {
  Rows rows(file,name);Hadronization::Sha256 digest;
  DigestField(digest,"hadronization_query_tree_content_v1");DigestField(digest,name);
  DigestField(digest,std::to_string(rows.tree->GetEntries()));
  std::vector<TLeaf*> leaves;
  for (const auto& field:fields) {
    auto* leaf=rows.Leaf(field);leaves.push_back(leaf);
    DigestField(digest,field);DigestField(digest,leaf->GetTypeName());
    DigestField(digest,std::to_string(leaf->GetLenStatic()));
  }
  while (rows.Next()) for (auto* leaf:leaves) {
    const std::string type=leaf->GetTypeName();
    DigestField(digest,type=="Double_t"?DoubleBits(leaf->GetValue()):
                (type=="ULong64_t"?std::to_string(static_cast<U64>(leaf->GetValueLong64())):
                                   std::to_string(leaf->GetValueLong64())));
  }
  return digest.FinalHex();
}

std::string ExpectedLabel(const Layout& layout,const std::string& axisName,int bin) {
  if (axisName!="pdg" && axisName!="trigger_pdg" && axisName!="associate_pdg") return "";
  if (bin<1 || bin>static_cast<int>(layout.pdgs.size())) return "";
  auto item=layout.pdgs.begin();std::advance(item,bin-1);return std::to_string(*item);
}

void ValidateSparseLayout(const THnSparseD& histogram,const std::string& family,
                          const std::vector<std::string>& fields,const Layout& layout) {
  const std::string objectName="sparse_"+family;
  if (std::string(histogram.GetName())!=objectName || std::string(histogram.GetTitle())!=objectName ||
      histogram.GetNdimensions()!=static_cast<int>(fields.size()) || !histogram.GetCalculateErrors() ||
      !std::isfinite(histogram.GetEntries()))
    throw std::runtime_error("sparse declared object/shape/Sumw2/entries differs");
  for (int a=0;a<histogram.GetNdimensions();++a) {
    const auto* axis=histogram.GetAxis(a);const auto& field=fields.at(a);
    const auto& declared=layout.axes.at(field);
    const auto* stored=axis->GetXbins();
    if (std::string(axis->GetName())!=field || std::string(axis->GetTitle())!=field ||
        axis->GetNbins()!=static_cast<int>(declared.edges.size()-1) ||
        stored->GetSize()!=static_cast<int>(declared.edges.size()) ||
        axis->GetXmin()!=declared.edges.front() || axis->GetXmax()!=declared.edges.back())
      throw std::runtime_error("sparse declared axis identity differs");
    for (int edge=0;edge<stored->GetSize();++edge)
      if (stored->At(edge)!=declared.edges.at(edge))
        throw std::runtime_error("sparse stored regular edge differs from declared layout");
    for (int bin=0;bin<=axis->GetNbins()+1;++bin)
      if (std::string(axis->GetBinLabel(bin))!=ExpectedLabel(layout,field,bin))
        throw std::runtime_error("sparse regular/flow label differs from declared layout");
  }
}

using SparseCells = std::map<std::vector<int>,std::pair<double,double>>;

SparseCells ReadSparseCells(const THnSparseD& histogram) {
  SparseCells cells;
  for (Long64_t b=0;b<histogram.GetNbins();++b) {
    std::vector<int> coordinates(histogram.GetNdimensions());
    const double value=histogram.GetBinContent(b,coordinates.data());
    const double variance=histogram.GetBinError2(b);
    for (int a=0;a<histogram.GetNdimensions();++a)
      if (coordinates[a]<0 || coordinates[a]>histogram.GetAxis(a)->GetNbins()+1)
        throw std::runtime_error("sparse scientific coordinate lies outside flow domain");
    if (!std::isfinite(value) || !std::isfinite(variance) || variance<0 ||
        !cells.emplace(coordinates,std::make_pair(value,variance)).second)
      throw std::runtime_error("invalid/duplicate sparse scientific cell");
  }
  return cells;
}

void DigestSparseCells(Hadronization::Sha256& digest,const SparseCells& cells) {
  DigestField(digest,std::to_string(cells.size()));
  for (const auto& cell:cells) {
    for (const int coordinate:cell.first) DigestField(digest,std::to_string(coordinate));
    DigestField(digest,DoubleBits(cell.second.first));DigestField(digest,DoubleBits(cell.second.second));
  }
}

std::string SparseDigestV2(const THnSparseD& histogram,const std::string& family,
                           const std::vector<std::string>& fields,const Layout& layout) {
  ValidateSparseLayout(histogram,family,fields,layout);
  Hadronization::Sha256 digest;
  DigestField(digest,"hadronization_query_sparse_content_v2");
  DigestField(digest,histogram.GetName());DigestField(digest,histogram.GetTitle());
  DigestField(digest,std::to_string(histogram.GetNdimensions()));
  DigestField(digest,DoubleBits(histogram.GetEntries()));
  DigestField(digest,"Sumw2");
  for (int a=0;a<histogram.GetNdimensions();++a) {
    const auto* axis=histogram.GetAxis(a);const auto& declared=layout.axes.at(fields.at(a));
    DigestField(digest,axis->GetName());DigestField(digest,axis->GetTitle());
    DigestField(digest,std::to_string(axis->GetNbins()));
    DigestField(digest,declared.inclusive?"inclusive_upper_endpoint":"halfopen_upper_endpoint");
    DigestField(digest,"explicit_underflow_bin_0_and_overflow_bin_n_plus_1");
    for (const double edge:declared.edges) DigestField(digest,DoubleBits(edge));
    for (int b=0;b<=axis->GetNbins()+1;++b) DigestField(digest,axis->GetBinLabel(b));
  }
  DigestSparseCells(digest,ReadSparseCells(histogram));
  return digest.FinalHex();
}

enum class LegacyFlowEncoding { RuntimeAccessor, Root640PhiOverflow };

double LegacyEdge(const TAxis& axis,int bin,LegacyFlowEncoding encoding) {
  if (encoding==LegacyFlowEncoding::Root640PhiOverflow && std::string(axis.GetName())=="phi" &&
      axis.GetNbins()==100 && bin==101 && DoubleBits(axis.GetXbins()->At(100))=="400921fb54442d18") {
    U64 bits=0x400921fb54442d19ULL;double value=0;std::memcpy(&value,&bits,sizeof(value));return value;
  }
  return axis.GetBinLowEdge(bin);
}

std::string SparseDigestV1(const THnSparseD& histogram,const std::string& family,
                           const std::vector<std::string>& fields,const Layout& layout,
                           LegacyFlowEncoding encoding) {
  ValidateSparseLayout(histogram,family,fields,layout);
  Hadronization::Sha256 digest;
  DigestField(digest,"hadronization_query_sparse_content_v1");
  DigestField(digest,histogram.GetName());DigestField(digest,histogram.GetTitle());
  DigestField(digest,std::to_string(histogram.GetNdimensions()));
  DigestField(digest,DoubleBits(histogram.GetEntries()));DigestField(digest,"Sumw2");
  for (int a=0;a<histogram.GetNdimensions();++a) {
    const auto* axis=histogram.GetAxis(a);
    DigestField(digest,axis->GetName());DigestField(digest,axis->GetTitle());
    DigestField(digest,std::to_string(axis->GetNbins()));
    for (int b=0;b<=axis->GetNbins()+1;++b) {
      DigestField(digest,DoubleBits(LegacyEdge(*axis,b,encoding)));
      DigestField(digest,axis->GetBinLabel(b));
    }
  }
  DigestSparseCells(digest,ReadSparseCells(histogram));return digest.FinalHex();
}

std::string ContentSha(const std::string& identities) {
  Hadronization::Sha256 digest;digest.Update(identities);return digest.FinalHex();
}

std::string SerializeIdentities(const std::map<std::string,std::string>& identities) {
  std::string result="{";
  for (const auto& identity:identities) {
    if (result.size()>1) result+=',';
    result+='"'+identity.first+"\":\""+identity.second+'"';
  }
  return result+'}';
}

std::string ContentDigestsFor(TFile& file,const Layout& layout,const Histograms* derived,
                              LegacyFlowEncoding legacyEncoding) {
  const auto validSha=[](const std::string& value) {
    return value.size()==64 && value.find_first_not_of("0123456789abcdef")==std::string::npos;
  };
  if (!validSha(layout.scientificBindingSha) || !validSha(layout.executionAttestationSha) ||
      !validSha(layout.dictionarySha))
    throw std::runtime_error("query scientific/execution/dictionary digest is absent or malformed");
  // Scientific content binds rows, sparse cells, accepted input/model/schema and
  // the global dictionary. Executable/build volatility is attested separately.
  std::map<std::string,std::string> identities{{"dictionary",layout.dictionarySha},
                                               {"scientific_binding",layout.scientificBindingSha}};
  for (const auto& tree:layout.trees) identities["tree:"+tree.first]=TreeDigest(file,tree.first,tree.second);
  for (const auto& sparse:layout.sparse) {
    const auto* histogram=derived?derived->at(sparse.first).get():
        dynamic_cast<THnSparseD*>(file.Get(("sparse_"+sparse.first).c_str()));
    if (!histogram) throw std::runtime_error("missing scientific sparse object");
    identities["sparse:"+sparse.first]=layout.sparseDigestSchema=="hadronization_query_sparse_content_v2"?
        SparseDigestV2(*histogram,sparse.first,sparse.second,layout):
        SparseDigestV1(*histogram,sparse.first,sparse.second,layout,legacyEncoding);
  }
  return SerializeIdentities(identities);
}

std::string ContentDigests(TFile& file,const Layout& layout,const Histograms* derived=nullptr) {
  const auto runtime=ContentDigestsFor(file,layout,derived,LegacyFlowEncoding::RuntimeAccessor);
  if (layout.sparseDigestSchema=="hadronization_query_sparse_content_v2" ||
      ContentSha(runtime)==layout.contentSha) return runtime;
  const auto root640=ContentDigestsFor(file,layout,derived,LegacyFlowEncoding::Root640PhiOverflow);
  if (ContentSha(root640)==layout.contentSha) return root640;
  throw std::runtime_error("legacy sparse identity matches no explicitly supported encoding");
}

std::string CanonicalContentDigests(TFile& file,const Layout& layout,const Histograms* derived=nullptr) {
  Layout canonical=layout;
  canonical.sparseDigestSchema="hadronization_query_sparse_content_v2";
  return ContentDigestsFor(file,canonical,derived,LegacyFlowEncoding::RuntimeAccessor);
}

void ReplaceUnique(std::string& text,const std::string& token,const std::string& value) {
  const auto position=text.find(token);
  if (position==std::string::npos || text.find(token,position+token.size())!=std::string::npos)
    throw std::runtime_error("query scientific identity placeholder differs");
  text.replace(position,token.size(),value);
}

void WriteText(const std::string& path,const std::string& value) {
  std::ofstream output(path,std::ios::trunc);output<<value;output.close();
  if (!output) throw std::runtime_error("cannot write query scientific identity");
}

void Verify(const std::string& path,const Layout& layout) {
  TFile file(path.c_str(),"READ");
  if (file.IsZombie() || file.GetCompressionAlgorithm()!=5 || file.GetCompressionLevel()!=5)
    throw std::runtime_error("query ROOT compression/unreadable file");
  std::map<std::string,std::string> expected{{"query_spec","TObjString"},{"metadata","TObjString"}};
  for (const auto& tree:layout.trees) expected[tree.first]="TTree";
  for (const auto& histogram:layout.sparse) expected["sparse_"+histogram.first]="THnSparseT<TArrayD>";
  std::map<std::string,std::string> actual;
  TIter keys(file.GetListOfKeys());
  while (auto* object=keys()) {
    auto* key=dynamic_cast<TKey*>(object);
    if (!key || key->GetCycle()!=1 || !actual.emplace(key->GetName(),key->GetClassName()).second)
      throw std::runtime_error("query duplicate key/cycle");
  }
  if (actual!=expected) throw std::runtime_error("query exact object set differs");
  auto* spec=dynamic_cast<TObjString*>(file.Get("query_spec"));
  if (!spec || spec->GetString().Data()!=layout.text) throw std::runtime_error("query embedded axis/config identity differs");
  auto* metadata=dynamic_cast<TObjString*>(file.Get("metadata"));
  if (!metadata) throw std::runtime_error("query metadata is absent");
  Hadronization::Sha256 metadataDigest;
  metadataDigest.Update(metadata->GetString().Data());
  std::cout<<"METADATA_SHA256\t"<<metadataDigest.FinalHex()<<'\n';
  for (const auto& tree:layout.trees) {
    Rows rows(file,tree.first);
    if (rows.tree->GetListOfBranches()->GetEntries()!=static_cast<int>(tree.second.size()))
      throw std::runtime_error("query exact branch set differs");
    std::map<std::string,std::string> schema;
    std::istringstream fields(HadronizationQuery::ExpectedSchemas().at(tree.first));
    for (std::string field;std::getline(fields,field,',');) {
      const auto delimiter=field.find(':');
      schema.emplace(field.substr(0,delimiter),field.substr(delimiter+1));
    }
    for (const auto& field:tree.second) {
      auto* leaf=rows.Leaf(field);
      if (schema.at(field)!=leaf->GetTypeName() || leaf->GetLenStatic()!=1 || leaf->GetLeafCount())
        throw std::runtime_error("query exact scalar column type differs");
    }
    std::cout<<"TREE\t"<<tree.first<<'\t'<<rows.tree->GetEntries()<<'\n';
  }
  const std::string identities=ContentDigests(file,layout),sha=ContentSha(identities);
  const std::string metadataText=metadata->GetString().Data();
  if (layout.contentSha!=sha ||
      metadataText.find("\"query_content_digests\":"+identities)==std::string::npos ||
      metadataText.find("\"query_content_sha256\":\""+sha+"\"")==std::string::npos)
    throw std::runtime_error("query internal scientific content digest differs");
  std::cout<<"SCIENTIFIC_CONTENT_SHA256\t"<<sha<<'\n';
  std::cout<<"CANONICAL_SCIENTIFIC_CONTENT_SHA256\t"
           <<ContentSha(CanonicalContentDigests(file,layout))<<'\n';
  Plane plane(file,layout); const auto proof=Populate(file,plane);
  if (layout.analysisVersion=="2.2.0" &&
      metadataText.find("\"pair_population_proof\":"+proof.Json(layout.scientificBindingSha))==std::string::npos &&
      metadataText.find("\"pair_population_proof\":"+proof.CanonicalJson(layout.scientificBindingSha))==std::string::npos)
    throw std::runtime_error("query pair population proof differs from exact rows");
  std::cout<<"PAIR_POPULATION_PROOF\t"<<proof.Json(layout.scientificBindingSha)<<'\n';
  for (const auto& item:plane.histograms) {
    auto* histogram=dynamic_cast<THnSparseD*>(file.Get(("sparse_"+item.first).c_str()));
    if (!histogram) throw std::runtime_error("missing sparse histogram");
    CheckHistogram(*item.second,*histogram);
    std::cout<<"SPARSE\t"<<item.first<<'\t'<<histogram->GetNbins()<<'\t'<<histogram->GetEntries()<<'\n';
  }
  std::cout<<"QUERY_VERIFIED\n";
}

void Build(const std::string& source,const std::string& output,Layout layout,
           const std::string& metadataPath,const std::string& specPath) {
  TFile input(source.c_str(),"READ");
  if (input.IsZombie()) throw std::runtime_error("cannot open exact input");
  Plane plane(input,layout); const auto proof=Populate(input,plane);
  const auto identities=ContentDigests(input,layout,&plane.histograms);
  layout.contentSha=ContentSha(identities);
  ReplaceUnique(layout.text,"__QUERY_CONTENT_SHA256__",layout.contentSha);
  std::string metadata=ReadText(metadataPath);
  ReplaceUnique(metadata,"\"__QUERY_CONTENT_DIGESTS__\"",identities);
  ReplaceUnique(metadata,"__QUERY_CONTENT_SHA256__",layout.contentSha);
  ReplaceUnique(metadata,"\"__PAIR_POPULATION_PROOF__\"",proof.Json(layout.scientificBindingSha));
  TFile file(output.c_str(),"CREATE","",ROOT::CompressionSettings(ROOT::RCompressionSetting::EAlgorithm::kZSTD,5));
  if (file.IsZombie()) throw std::runtime_error("cannot create query ROOT (no overwrite)");
  for (const auto& entry:layout.trees) {
    Rows rows(input,entry.first);
    rows.tree->SetBranchStatus("*",0);
    for (const auto& field:entry.second) { rows.Leaf(field); rows.tree->SetBranchStatus(field.c_str(),1); }
    file.cd(); std::unique_ptr<TTree> copy(rows.tree->CloneTree(0));
    copy->SetDirectory(&file); copy->SetAutoSave(0); copy->SetAutoFlush(-4*1024*1024);
    while (rows.Next()) if (copy->Fill()<0) throw std::runtime_error("cannot fill exact query tree");
    if (copy->Write()<=0) throw std::runtime_error("cannot write exact query tree");
    rows.tree->SetBranchStatus("*",1);
  }
  file.cd();
  for (const auto& histogram:plane.histograms) histogram.second->Write();
  TObjString spec(layout.text.c_str()); spec.Write("query_spec");
  TObjString meta(metadata.c_str()); meta.Write("metadata");
  file.Close(); Verify(output,layout);
  WriteText(metadataPath,metadata);WriteText(specPath,layout.text);
}

// Read-only campaign qualification primitive. It never books or writes query
// objects: the coordinator combines every admitted shard result with configured
// identities, then freezes one dictionary for all construction workers.
void Census(const std::string& path) {
  TFile file(path.c_str(),"READ");
  if (file.IsZombie()) throw std::runtime_error("cannot open census input");
  Rows heavy(file,"heavy"), closure(file,"closure");
  bool haveHeavy=heavy.Next(),haveClosure=closure.Next();
  U64 heavyRows=0,closureRows=0; std::set<int> pdgs;
  while (haveHeavy) {
    const U64 event=heavy.U("event_id");
    std::map<int,int> particles;
    while (haveHeavy && heavy.U("event_id")==event) {
      const int index=heavy.I("heavy_index"),pdg=heavy.I("pdg");
      if (pdg==0 || !particles.emplace(index,pdg).second)
        throw std::runtime_error("census heavy identity differs");
      pdgs.insert(pdg);++heavyRows;haveHeavy=heavy.Next();
    }
    if (haveClosure && closure.U("event_id")<event)
      throw std::runtime_error("census orphan closure row");
    while (haveClosure && closure.U("event_id")==event) {
      pdgs.insert(particles.at(closure.I("trigger_heavy_index")));
      pdgs.insert(particles.at(closure.I("associate_heavy_index")));
      ++closureRows;haveClosure=closure.Next();
    }
  }
  if (haveClosure) throw std::runtime_error("census trailing closure row");
  std::cout<<"QUERY_CENSUS_V1\nHEAVY_ROWS\t"<<heavyRows<<"\nCLOSURE_ROWS\t"<<closureRows<<'\n';
  for (const int pdg:pdgs) std::cout<<"PDG\t"<<pdg<<'\n';
  std::cout<<"CENSUS_COMPLETE\n";
}

// This primitive scan exposes exact selected row identities, not a second
// implementation of balancing ratios or their covariance.
void Scan(const std::string& path,const HadronizationQuery::Profile& profile) {
  TFile file(path.c_str(),"READ");
  if (file.IsZombie()) throw std::runtime_error("cannot open query rows");
  Rows rows(file,"pairs");
  while (rows.Next()) if (profile.Pair(rows.D("trigger_pt"),rows.D("associate_pt")))
    std::cout<<rows.U("event_id")<<'\t'<<rows.I("trigger_heavy_index")<<'\t'
             <<rows.I("associate_heavy_index")<<'\n';
}
}  // namespace

int main(int argc,char** argv) {
  try {
    if (argc==3 && std::string(argv[1])=="census") {
      Census(argv[2]); return 0;
    }
    if (argc==6 && std::string(argv[1])=="build") {
      Build(argv[3],argv[4],ReadLayout(ReadText(argv[2])),argv[5],argv[2]); return 0;
    }
    if (argc==4 && std::string(argv[1])=="verify") {
      Verify(argv[3],ReadLayout(ReadText(argv[2]))); return 0;
    }
    if (argc==4 && std::string(argv[1])=="content") {
      TFile file(argv[3],"READ");
      if (file.IsZombie()) throw std::runtime_error("cannot inspect scientific content");
      const auto layout=ReadLayout(ReadText(argv[2]));
      const auto identities=ContentDigests(file,layout);
      std::cout<<"CONTENT_DIGESTS\t"<<identities<<'\n'
               <<"SCIENTIFIC_CONTENT_SHA256\t"<<ContentSha(identities)<<'\n'
               <<"CANONICAL_SCIENTIFIC_CONTENT_SHA256\t"
               <<ContentSha(CanonicalContentDigests(file,layout))<<'\n';return 0;
    }
    if (argc==6 && std::string(argv[1])=="scan") {
      const std::string name=(std::string(argv[3])=="NONE" && std::string(argv[4])=="NONE")?
                             "inclusive":"rectangle";
      Scan(argv[2],HadronizationQuery::ReadProfile(0,name,argv[3],argv[4],argv[5])); return 0;
    }
    throw std::runtime_error("usage: query census ROOT | build SPEC INPUT OUTPUT METADATA | verify SPEC ROOT | scan ROOT TRIGGER_CUT ASSOCIATE_CUT RELATIVE");
  } catch (const std::exception& error) { std::cerr<<"ERROR: "<<error.what()<<'\n'; return 2; }
}
