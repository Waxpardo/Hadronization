// Exact-support accounting for the native ROOT collection reader.
// This is an additive input scanner; observable formulas remain in native_engine.cpp.
#include <TFile.h>
#include <TTree.h>
#include <TLeaf.h>
#include <RtypesCore.h>

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <stdexcept>
#include <string>
#include <tuple>
#include <vector>

namespace {
using Key = std::pair<std::string, unsigned>;
using HeavyKey = std::tuple<std::string, unsigned, int>;
using OriginKey = std::tuple<std::string, unsigned, int, int, int>;
using ClosureKey = std::tuple<std::string, unsigned, int, int, int>;
struct Member {std::string tune; unsigned block; std::uint64_t events;};
struct Shard {std::string path; std::map<unsigned, Member> members;};
struct Range {std::uint64_t first, end; unsigned local; std::uint64_t observed=0;};
struct Event {ULong64_t event_id; Double_t weight,pthat,hard_scale; Int_t a15_eta1,a15_eta4,process_code,n_mpi;};
struct Heavy {ULong64_t event_id; Int_t pdg,status,nc,ncbar,nb,nbbar; UChar_t final,selected; Double_t pt,eta,phi;};
struct Pair {ULong64_t event_id; Int_t associate_origin,associate_category,sign;};
struct Closure {ULong64_t event_id; Int_t coefficient,dense_category; UChar_t visible;};
struct RangeRow {ULong64_t first_id,count; UInt_t source_id;};
struct T1 {std::uint64_t hadrons=0,charm=0,beauty=0; double weighted[3]={},correction[3]={};
  void add(int nc,int nb,double weight) {
    if(nc<0||nb<0||nc+nb==0) throw std::runtime_error("natural final heavy constituent differs");
    ++hadrons; charm+=static_cast<unsigned>(nc); beauty+=static_cast<unsigned>(nb);
    const double delta[3]={weight,weight*nc,weight*nb};
    for(int i=0;i<3;++i){double adjusted=delta[i]-correction[i];double next=weighted[i]+adjusted;
      correction[i]=(next-weighted[i])-adjusted;weighted[i]=next;}
  }
};
struct Moments {std::uint64_t events=0; double sumw=0,sumw2=0,sumabsw=0,pthat=0,hard_scale=0;
  std::map<int,std::uint64_t> activity,nmpi,process;
  void add(const Event& row,bool eta1) {
    int a=eta1?row.a15_eta1:row.a15_eta4;
    if(a<0||row.n_mpi<0||!std::isfinite(row.weight)||!std::isfinite(row.pthat)||
       !std::isfinite(row.hard_scale)) throw std::runtime_error("exact event accounting field differs");
    ++events;sumw+=row.weight;sumw2+=row.weight*row.weight;sumabsw+=std::abs(row.weight);
    ++activity[a];++nmpi[row.n_mpi];++process[row.process_code];
    pthat+=row.pthat;hard_scale+=row.hard_scale;
  }
};
struct Diag {std::uint64_t natural=0,charm=0,beauty=0,strict=0;
  double natural_w=0,charm_w=0,beauty_w=0,strict_w=0;};
struct Group {std::uint64_t rows=0;double weighted=0;};
struct Boundary {std::string tune;unsigned block;int pdg;double pt,eta,phi,weight;};

template<class T> void Bind(TTree* tree,const char* name,const char* type,T* destination){
  TLeaf* leaf=tree->GetLeaf(name);
  if(!leaf||std::string(leaf->GetTypeName())!=type||tree->SetBranchAddress(name,destination)<0)
    throw std::runtime_error(std::string("required exact support field/type differs: ")+tree->GetName()+"."+name);
}
TTree* Tree(TFile& file,const char* name){auto* tree=file.Get<TTree>(name);
  if(!tree)throw std::runtime_error(std::string("required exact support tree absent: ")+name);
  return tree;}
std::vector<Shard> Inputs(const std::string& path){
  std::ifstream in(path);if(!in)throw std::runtime_error("support map absent");
  std::vector<Shard> shards;std::string tag;
  while(in>>tag){
    if(tag=="SHARD"){
      std::string name;in>>name;
      if(!in||name.find('\t')!=std::string::npos)
        throw std::runtime_error("support shard locator differs");
      shards.push_back({name,{}});
    }
    else if(tag=="MEMBER"){
      if(shards.empty())throw std::runtime_error("support member precedes shard");
      unsigned local,block;std::string tune;std::uint64_t events;in>>local>>tune>>block>>events;
      if(!in||tune.empty()||block==0||events==0||!shards.back().members.emplace(
         local,Member{tune,block,events}).second)throw std::runtime_error("repeated/invalid support source");
    } else throw std::runtime_error("support map record differs");
  }
  if(shards.empty())throw std::runtime_error("support map has no shards");
  return shards;
}
void Scan(const std::vector<Shard>& shards,bool eta1,const std::string& output){
  std::map<Key,Moments> moments;std::map<HeavyKey,T1> t1;std::map<Key,Diag> diagnostics;
  std::map<OriginKey,Group> origins;std::map<ClosureKey,Group> closures;
  std::vector<Boundary> boundaries;
  std::map<std::string,std::uint64_t> upper;
  std::uint64_t opened=0;
  for(const auto& shard:shards){
    TFile file(shard.path.c_str(),"READ");if(file.IsZombie())throw std::runtime_error("support ROOT cannot open");
    ++opened;
    TTree *events=Tree(file,"events"),*heavy=Tree(file,"heavy"),*pairs=Tree(file,"pairs"),
          *closure=Tree(file,"closure"),*ranges=Tree(file,"event_ranges");
    upper["activity"]+=static_cast<std::uint64_t>(events->GetEntries());
    upper["triggers"]+=static_cast<std::uint64_t>(Tree(file,"triggers")->GetEntries());
    upper["pairs"]+=static_cast<std::uint64_t>(pairs->GetEntries());
    upper["kinematics"]+=static_cast<std::uint64_t>(heavy->GetEntries());
    RangeRow rr{};Bind(ranges,"first_id","ULong64_t",&rr.first_id);
    Bind(ranges,"count","ULong64_t",&rr.count);Bind(ranges,"source_id","UInt_t",&rr.source_id);
    std::vector<Range> intervals;std::map<unsigned,bool> seen;
    for(Long64_t i=0;i<ranges->GetEntries();++i){ranges->GetEntry(i);
      auto found=shard.members.find(rr.source_id);
      if(found==shard.members.end()||seen[rr.source_id]||rr.count!=found->second.events||
         rr.first_id+rr.count<rr.first_id)throw std::runtime_error("support source range differs/repeats");
      seen[rr.source_id]=true;intervals.push_back({rr.first_id,rr.first_id+rr.count,rr.source_id,0});
    }
    if(seen.size()!=shard.members.size())throw std::runtime_error("support source range missing");
    std::sort(intervals.begin(),intervals.end(),[](auto& a,auto& b){return a.first<b.first;});
    for(std::size_t i=1;i<intervals.size();++i)if(intervals[i-1].end>intervals[i].first)
      throw std::runtime_error("support source ranges overlap");
    Event ev{};Bind(events,"event_id","ULong64_t",&ev.event_id);
    Bind(events,"weight","Double_t",&ev.weight);Bind(events,"a15_eta1","Int_t",&ev.a15_eta1);
    Bind(events,"a15_eta4","Int_t",&ev.a15_eta4);Bind(events,"process_code","Int_t",&ev.process_code);
    Bind(events,"n_mpi","Int_t",&ev.n_mpi);Bind(events,"pthat","Double_t",&ev.pthat);
    Bind(events,"hard_scale","Double_t",&ev.hard_scale);
    Heavy h{};Bind(heavy,"event_id","ULong64_t",&h.event_id);Bind(heavy,"pdg","Int_t",&h.pdg);
    Bind(heavy,"status","Int_t",&h.status);Bind(heavy,"nc","Int_t",&h.nc);
    Bind(heavy,"ncbar","Int_t",&h.ncbar);Bind(heavy,"nb","Int_t",&h.nb);
    Bind(heavy,"nbbar","Int_t",&h.nbbar);Bind(heavy,"final","UChar_t",&h.final);
    Bind(heavy,"selected","UChar_t",&h.selected);Bind(heavy,"pt","Double_t",&h.pt);
    Bind(heavy,"eta","Double_t",&h.eta);Bind(heavy,"phi","Double_t",&h.phi);
    Pair pair{};Bind(pairs,"event_id","ULong64_t",&pair.event_id);
    Bind(pairs,"associate_origin","Int_t",&pair.associate_origin);
    Bind(pairs,"associate_category","Int_t",&pair.associate_category);
    Bind(pairs,"sign","Int_t",&pair.sign);
    Closure cl{};Bind(closure,"event_id","ULong64_t",&cl.event_id);
    Bind(closure,"coefficient","Int_t",&cl.coefficient);
    Bind(closure,"dense_category","Int_t",&cl.dense_category);
    Bind(closure,"visible","UChar_t",&cl.visible);
    Long64_t hi=0,pi=0,ci=0;
    auto next_h=[&](){if(hi<heavy->GetEntries()){heavy->GetEntry(hi++);return true;}return false;};
    auto next_p=[&](){if(pi<pairs->GetEntries()){pairs->GetEntry(pi++);return true;}return false;};
    auto next_c=[&](){if(ci<closure->GetEntries()){closure->GetEntry(ci++);return true;}return false;};
    bool has_h=next_h(),has_p=next_p(),has_c=next_c();
    std::size_t range_at=0;ULong64_t previous=0;bool first=true;
    for(Long64_t i=0;i<events->GetEntries();++i){events->GetEntry(i);
      if((!first&&ev.event_id<=previous)||!std::isfinite(ev.weight))
        throw std::runtime_error("support event order/weight differs");
      first=false;previous=ev.event_id;
      while(range_at<intervals.size()&&ev.event_id>=intervals[range_at].end)++range_at;
      if(range_at==intervals.size()||ev.event_id<intervals[range_at].first)
        throw std::runtime_error("support event lacks source range");
      auto& range=intervals[range_at];++range.observed;
      const auto& member=shard.members.at(range.local);Key key{member.tune,member.block};
      moments[key].add(ev,eta1);
      if((has_p&&pair.event_id<ev.event_id)||(has_c&&cl.event_id<ev.event_id)||
         (has_h&&h.event_id<ev.event_id))throw std::runtime_error("orphan/out-of-order support row");
      while(has_p&&pair.event_id==ev.event_id){
        auto& group=origins[{member.tune,member.block,pair.associate_origin,
                             pair.associate_category,pair.sign}];
        ++group.rows;group.weighted+=ev.weight;has_p=next_p();}
      while(has_c&&cl.event_id==ev.event_id){
        auto& group=closures[{member.tune,member.block,cl.dense_category,
                              static_cast<int>(cl.visible!=0),cl.coefficient}];
        ++group.rows;group.weighted+=ev.weight*cl.coefficient;has_c=next_c();}
      while(has_h&&h.event_id==ev.event_id){
        if(h.final){
          int nc=h.nc+h.ncbar,nb=h.nb+h.nbbar;
          if(nc<0||nb<0)throw std::runtime_error("T1 negative heavy constituent count");
          auto& d=diagnostics[key];++d.natural;d.natural_w+=ev.weight;
          d.charm+=static_cast<unsigned>(nc);d.charm_w+=ev.weight*nc;
          d.beauty+=static_cast<unsigned>(nb);d.beauty_w+=ev.weight*nb;
          if(h.selected&&h.status>=81&&h.status<=89&&h.pt>.15&&std::abs(h.eta)<=4.){
            ++d.strict;d.strict_w+=ev.weight;}
          t1[{member.tune,member.block,h.pdg}].add(nc,nb,ev.weight);
          if(h.selected&&h.status>=81&&h.status<=89&&h.pt==.15&&std::abs(h.eta)<=4.)
            boundaries.push_back({member.tune,member.block,h.pdg,h.pt,h.eta,h.phi,ev.weight});
        }
        has_h=next_h();
      }
    }
    if(has_h||has_p||has_c)throw std::runtime_error("support rows remain after final event");
    for(const auto& range:intervals)if(range.observed!=range.end-range.first)
      throw std::runtime_error("support source exposure differs");
  }
  std::ofstream out(output);if(!out)throw std::runtime_error("support output cannot create");
  out<<std::hexfloat;
  out<<"hadronization_support_scan_v1\n";
  out<<"OPEN\t"<<opened<<'\n';
  for(const auto& [name,count]:upper)out<<"UPPER\t"<<name<<'\t'<<count<<'\n';
  for(const auto& [key,m]:moments){
    out<<"MOMENT\t"<<key.first<<'\t'<<key.second<<'\t'<<m.events<<'\t'
       <<m.sumw<<'\t'<<m.sumw2<<'\t'<<m.sumabsw<<'\t'<<m.pthat<<'\t'<<m.hard_scale<<'\n';
    for(const auto& [a,n]:m.activity)out<<"ACTIVITY\t"<<key.first<<'\t'<<key.second<<'\t'<<a<<'\t'<<n<<'\n';
    for(const auto& [a,n]:m.nmpi)out<<"NMPI\t"<<key.first<<'\t'<<key.second<<'\t'<<a<<'\t'<<n<<'\n';
    for(const auto& [a,n]:m.process)out<<"PROCESS\t"<<key.first<<'\t'<<key.second<<'\t'<<a<<'\t'<<n<<'\n';
  }
  for(const auto& [key,x]:t1)out<<"T1\t"<<std::get<0>(key)<<'\t'<<std::get<1>(key)<<'\t'
    <<std::get<2>(key)<<'\t'<<x.hadrons<<'\t'<<x.charm<<'\t'<<x.beauty<<'\t'
    <<x.weighted[0]<<'\t'<<x.weighted[1]<<'\t'<<x.weighted[2]<<'\n';
  for(const auto& [key,x]:diagnostics)out<<"DIAG\t"<<key.first<<'\t'<<key.second<<'\t'
    <<x.natural<<'\t'<<x.natural_w<<'\t'<<x.charm<<'\t'<<x.charm_w<<'\t'
    <<x.beauty<<'\t'<<x.beauty_w<<'\t'<<x.strict<<'\t'<<x.strict_w<<'\n';
  for(const auto& [key,x]:origins)out<<"ORIGIN\t"<<std::get<0>(key)<<'\t'<<std::get<1>(key)<<'\t'
    <<std::get<2>(key)<<'\t'<<std::get<3>(key)<<'\t'<<std::get<4>(key)<<'\t'
    <<x.rows<<'\t'<<x.weighted<<'\n';
  for(const auto& [key,x]:closures)out<<"CLOSURE\t"<<std::get<0>(key)<<'\t'<<std::get<1>(key)<<'\t'
    <<std::get<2>(key)<<'\t'<<std::get<3>(key)<<'\t'<<std::get<4>(key)<<'\t'
    <<x.rows<<'\t'<<x.weighted<<'\n';
  for(const auto& x:boundaries)out<<"BOUNDARY\t"<<x.tune<<'\t'<<x.block<<'\t'
    <<x.pdg<<'\t'<<x.pt<<'\t'<<x.eta<<'\t'<<x.phi<<'\t'<<x.weight<<'\n';
  out<<"END\n";if(!out)throw std::runtime_error("support output write failed");
}
} // namespace

int main(int argc,char** argv){
  try{if(argc!=4)throw std::runtime_error("usage: support-scan map eta1|eta4 output");
    const std::string field=argv[2];if(field!="eta1"&&field!="eta4")
      throw std::runtime_error("support activity field differs");
    Scan(Inputs(argv[1]),field=="eta1",argv[3]);return 0;
  }catch(const std::exception& error){std::cerr<<"ERROR: "<<error.what()<<'\n';return 2;}
}
