// Diagnostic native sparse functional evaluator. The caller authenticates A's
// collection and normalizes its physical THnSparse cells before this engine.
// This emits numerical center/leave functions, not a publication DTO.
#include "statistics.hpp"

#include <algorithm>
#include <array>
#include <cctype>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <optional>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

namespace HR = Hadronization::Reduction;
namespace {

std::vector<std::string> Fields(const std::string& line) {
  std::vector<std::string> fields;
  std::size_t start = 0;
  for (;;) {
    const auto next = line.find('\t',start);
    fields.push_back(line.substr(start,next-start));
    if (next == std::string::npos) return fields;
    start = next+1;
  }
}
void Need(const std::vector<std::string>& fields,std::size_t count) {
  if (fields.size()!=count) throw std::runtime_error("native transport width differs");
}
int Integer(const std::string& token) {
  std::size_t consumed=0;
  const int value=std::stoi(token,&consumed);
  if (consumed!=token.size() || std::to_string(value)!=token)
    throw std::runtime_error("native integer is noncanonical");
  return value;
}
int SourceBlock(const std::string& token) {
  const int block=Integer(token);
  if (block<1 || block>10)
    throw std::runtime_error("native source block is outside the ten-block design");
  return block;
}
double Number(const std::string& token) {
  std::size_t consumed=0;
  const double value=std::stod(token,&consumed);
  if (consumed!=token.size() || !std::isfinite(value))
    throw std::runtime_error("native numerical input is nonfinite/noncanonical");
  return value;
}
std::string Hex(double value) {
  if (!std::isfinite(value)) return "-";
  std::ostringstream output;
  output<<std::hexfloat<<value;
  return output.str();
}
std::string Leaves(const std::vector<double>& values) {
  std::string text;
  for (std::size_t i=0;i<values.size();++i) {
    if (i) text+=';';
    text+=Hex(values[i]);
  }
  return text.empty()?"-":text;
}

using AKey=std::tuple<std::string,int,int>;
using TKey=std::tuple<std::string,std::string,int,int,int>;
using PKey=std::tuple<std::string,std::string,int,int,int,int,int,int>;
using TGroupKey=std::tuple<std::string,std::string,int,int>;
using PGroupKey=std::tuple<std::string,std::string,int,int,int,int,int>;
using GKey=std::tuple<std::string,int,int,std::string,int>;
using HKey=std::tuple<std::string,int,int>;
using EKey=std::pair<std::string,int>;
struct T1 {
  std::array<double,3> count{};
  std::array<double,3> weighted{};
};
struct Weighted {
  double value=0.0;
  double sumw2=0.0;
};
struct ActivityValue {
  int activity=0;
  Weighted measure;
};
struct Data {
  std::string indexSha,scienceSha,analysisSha;
  std::string activityField;
  std::set<std::string> profiles;
  std::set<int> triggerScope,g9Scope,t1Scope;
  std::set<std::pair<int,int>> pairScope;
  std::map<AKey,Weighted> activity;
  std::map<TKey,Weighted> triggers;
  std::map<PKey,Weighted> pairs;
  std::map<GKey,Weighted> g9;
  std::map<HKey,T1> t1;
  std::map<EKey,int> exposure;
  std::map<std::string,std::uint64_t> supportUpper;
  std::set<std::string> tunes;
  int activityBins=0;
};
double ValueOf(const Weighted& cell) { return cell.value; }
template<class Value> double ValueOf(const Value& value) {
  return static_cast<double>(value);
}
template<class Map,class Key> double Get(const Map& values,const Key& key) {
  const auto item=values.find(key);
  return item==values.end()?0.0:ValueOf(item->second);
}

Data ReadData(const std::string& path,const std::string& expectedIndex) {
  std::ifstream input(path);
  std::string line;
  if (!input || !std::getline(input,line) ||
      line!="hadronization_native_primitives_v1")
    throw std::runtime_error("native transport header differs");
  Data data;
  if (!std::getline(input,line)) throw std::runtime_error("native source binding is absent");
  auto fields=Fields(line);Need(fields,4);
  if (fields[0]!="SOURCE" || fields[1]!=expectedIndex)
    throw std::runtime_error("native authenticated index binding differs");
  data.indexSha=fields[1];data.scienceSha=fields[2];data.analysisSha=fields[3];
  bool ended=false;
  while (std::getline(input,line)) {
    fields=Fields(line);
    if (fields==std::vector<std::string>{"END"}) {ended=true;break;}
    if (fields.empty()) throw std::runtime_error("native empty row");
    if (fields[0]=="ACTIVITY_FIELD") {
      Need(fields,2);
      if (!data.activityField.empty() ||
          (fields[1]!="a15_eta4" && fields[1]!="a15_eta1"))
        throw std::runtime_error("native activity field differs");
      data.activityField=fields[1];
    } else if (fields[0]=="SUPPORT_UPPER") {
      Need(fields,3);
      if (fields[2].empty() || fields[2].find_first_not_of("0123456789")!=std::string::npos ||
          fields[2].size()>20 ||
          !data.supportUpper.emplace(fields[1],std::stoull(fields[2])).second ||
          (fields[1]!="activity" && fields[1]!="triggers" &&
           fields[1]!="pairs" && fields[1]!="kinematics"))
        throw std::runtime_error("native support upper-bound domain differs");
    } else if (fields[0]=="PROFILE") {
      Need(fields,2);
      if (!data.profiles.insert(fields[1]).second)
        throw std::runtime_error("native profile scope duplicates");
    } else if (fields[0]=="TRIGGER_SCOPE") {
      Need(fields,2);
      if (!data.triggerScope.insert(Integer(fields[1])).second)
        throw std::runtime_error("native trigger scope duplicates");
    } else if (fields[0]=="PAIR_SCOPE") {
      Need(fields,3);
      if (!data.pairScope.insert({Integer(fields[1]),Integer(fields[2])}).second)
        throw std::runtime_error("native pair scope duplicates");
    } else if (fields[0]=="G9_SCOPE") {
      Need(fields,2);
      if (!data.g9Scope.insert(Integer(fields[1])).second)
        throw std::runtime_error("native G9 scope duplicates");
    } else if (fields[0]=="T1_SCOPE") {
      Need(fields,2);
      if (!data.t1Scope.insert(Integer(fields[1])).second)
        throw std::runtime_error("native T1 scope duplicates");
    } else if (fields[0]=="ACTIVITY") {
      Need(fields,6);
      const AKey key{fields[1],SourceBlock(fields[2]),Integer(fields[3])};
      const Weighted cell{Number(fields[4]),Number(fields[5])};
      if (!data.activity.emplace(key,cell).second || cell.sumw2<0)
        throw std::runtime_error("native activity duplication/Sumw2 differs");
      data.activityBins=std::max(data.activityBins,Integer(fields[3])+1);
      data.tunes.insert(fields[1]);
    } else if (fields[0]=="TRIGGER") {
      Need(fields,8);
      const TKey key{fields[1],fields[2],SourceBlock(fields[3]),Integer(fields[4]),Integer(fields[5])};
      const Weighted cell{Number(fields[6]),Number(fields[7])};
      if (!data.triggers.emplace(key,cell).second || cell.sumw2<0)
        throw std::runtime_error("native trigger duplication/Sumw2 differs");
    } else if (fields[0]=="PAIR") {
      Need(fields,11);
      const PKey key{fields[1],fields[2],SourceBlock(fields[3]),Integer(fields[4]),
        Integer(fields[5]),Integer(fields[6]),Integer(fields[7]),Integer(fields[8])};
      if (std::get<6>(key)!=-1 && std::get<6>(key)!=1)
        throw std::runtime_error("native pair sign differs");
      const Weighted cell{Number(fields[9]),Number(fields[10])};
      if (!data.pairs.emplace(key,cell).second || cell.sumw2<0)
        throw std::runtime_error("native pair duplication/Sumw2 differs");
    } else if (fields[0]=="G9") {
      Need(fields,8);
      const GKey key{fields[1],SourceBlock(fields[2]),Integer(fields[3]),fields[4],Integer(fields[5])};
      const Weighted cell{Number(fields[6]),Number(fields[7])};
      if (!data.g9.emplace(key,cell).second || cell.sumw2<0)
        throw std::runtime_error("native G9 duplication/Sumw2 differs");
    } else if (fields[0]=="T1") {
      Need(fields,10);
      const HKey key{fields[1],SourceBlock(fields[2]),Integer(fields[3])};
      T1 row{{double(Integer(fields[4])),double(Integer(fields[5])),
              double(Integer(fields[6]))},
             {Number(fields[7]),Number(fields[8]),Number(fields[9])}};
      if (!data.t1.emplace(key,row).second)
        throw std::runtime_error("native T1 duplicate key");
    } else if (fields[0]=="EXPOSURE") {
      Need(fields,4);
      const EKey key{fields[1],SourceBlock(fields[2])};
      const int events=Integer(fields[3]);
      if (events<1 || !data.exposure.emplace(key,events).second)
        throw std::runtime_error("native exposure key/count differs");
      data.tunes.insert(fields[1]);
    } else throw std::runtime_error("native transport record differs");
  }
  if (!ended || input.peek()!=std::ifstream::traits_type::eof() ||
      data.exposure.empty() || data.activityField.empty() ||
      data.profiles.empty() || data.triggerScope.empty() || data.pairScope.empty())
    throw std::runtime_error("native transport ending/domain differs");
  for (const auto& tune:data.tunes)
    for (int block=1;block<=10;++block)
      if (!data.exposure.count({tune,block}))
        throw std::runtime_error("native ten-block event exposure is incomplete");
  if (!data.supportUpper.empty()) {
    if (data.supportUpper.size()!=4 ||
        data.supportUpper.at("activity") <
          static_cast<std::uint64_t>(std::accumulate(data.exposure.begin(),
              data.exposure.end(),0ULL,
              [](unsigned long long sum,const auto& item){
                return sum+static_cast<unsigned long long>(item.second); })))
      throw std::runtime_error("native support row upper bounds are incomplete");
  }
  for (const auto& [key,value]:data.activity) {
    (void)value;
    if (!data.exposure.count({std::get<0>(key),std::get<1>(key)}))
      throw std::runtime_error("native activity cell lacks source exposure");
  }
  for (const auto& [key,value]:data.triggers) {
    (void)value;
    if (!data.exposure.count({std::get<1>(key),std::get<2>(key)}))
      throw std::runtime_error("native trigger lacks source exposure");
  }
  for (const auto& [key,value]:data.pairs) {
    (void)value;
    if (!data.exposure.count({std::get<1>(key),std::get<2>(key)}))
      throw std::runtime_error("native pair lacks source exposure");
  }
  for (const auto& [key,value]:data.g9) {
    (void)value;
    if (!data.exposure.count({std::get<0>(key),std::get<1>(key)}))
      throw std::runtime_error("native G9 cell lacks source exposure");
  }
  for (const auto& [key,value]:data.t1) {
    (void)value;
    if (!data.exposure.count({std::get<0>(key),std::get<1>(key)}))
      throw std::runtime_error("native T1 row lacks source exposure");
  }
  return data;
}

struct Point {
  int id=0,classId=0,trigger=0,associate=0,referencePdg=0,bin=-1;
  std::string role,quantity,tune,referenceTune,profile,component,axis;
};
struct Queries {
  int dphiBins=0,g9PtBins=0;
  bool density=false,formulaSeen=false;
  std::vector<std::pair<double,double>> dphiEdges;
  std::string requestSha,scientificRequestSha;
  std::map<std::string,std::string> sourceFamilyDigests;
  std::map<int,HR::ActivityClassSpec> classes;
  std::map<std::tuple<int,std::string,std::string>,std::vector<int>> signAssociates;
  std::vector<Point> points;
};
Queries ReadQueries(const std::string& path,Data& data) {
  std::ifstream input(path);
  std::string line;
  if (!input || !std::getline(input,line) ||
      line!="hadronization_native_points_v1")
    throw std::runtime_error("native point header differs");
  Queries query;
  if (!std::getline(input,line)) throw std::runtime_error("native point binding is absent");
  auto fields=Fields(line);Need(fields,4);
  if (fields!=std::vector<std::string>{"BIND",data.indexSha,data.scienceSha,data.analysisSha})
    throw std::runtime_error("native points/scanned source binding differs");
  bool ended=false;
  while (std::getline(input,line)) {
    fields=Fields(line);
    if (fields==std::vector<std::string>{"END"}) {ended=true;break;}
    if (fields.empty()) throw std::runtime_error("native empty query");
    if (fields[0]=="REQUEST") {
      Need(fields,3);
      const auto digest=[](const std::string& token){
        return token.size()==64 &&
            token.find_first_not_of("0123456789abcdef")==std::string::npos;
      };
      if (!query.requestSha.empty() || !digest(fields[1]) || !digest(fields[2]))
        throw std::runtime_error("native scientific request identity differs");
      query.requestSha=fields[1];query.scientificRequestSha=fields[2];
    } else if (fields[0]=="AXES") {
      Need(fields,4);
      if (query.dphiBins || query.g9PtBins)
        throw std::runtime_error("native query axes duplicate");
      const int activityBins=Integer(fields[1]);
      query.dphiBins=Integer(fields[2]);query.g9PtBins=Integer(fields[3]);
      if (activityBins<data.activityBins || query.dphiBins<1 || query.g9PtBins<1)
        throw std::runtime_error("native requested/scanned axis domain differs");
      data.activityBins=activityBins;
    } else if (fields[0]=="FORMULA") {
      Need(fields,2);
      if (query.formulaSeen || !query.points.empty() ||
          (fields[1]!="projection_formulas_v2" && fields[1]!="projection_formulas_v3"))
        throw std::runtime_error("native formula contract differs");
      query.formulaSeen=true;query.density=fields[1]=="projection_formulas_v3";
    } else if (fields[0]=="DPHI_BIN") {
      Need(fields,4);
      const double low=Number(fields[2]),high=Number(fields[3]);
      if (!query.density || !query.points.empty() ||
          Integer(fields[1])!=static_cast<int>(query.dphiEdges.size()) ||
          query.dphiEdges.size()>=static_cast<std::size_t>(query.dphiBins) ||
          !(high>low) || !std::isfinite(high-low) ||
          (!query.dphiEdges.empty() && query.dphiEdges.back().second!=low))
        throw std::runtime_error("native angular bin domain differs");
      query.dphiEdges.emplace_back(low,high);
    } else if (fields[0]=="FAMILY") {
      Need(fields,3);
      if (!data.tunes.count(fields[1]) || fields[2].size()!=64 ||
          fields[2].find_first_not_of("0123456789abcdef")!=std::string::npos ||
          !query.sourceFamilyDigests.emplace(fields[1],fields[2]).second)
        throw std::runtime_error("native source-family identity differs");
    } else if (fields[0]=="CLASS") {
      Need(fields,5);
      const int id=Integer(fields[1]);
      HR::ActivityClassSpec spec{Integer(fields[2])==1,Integer(fields[3]),Integer(fields[4])};
      if (!query.classes.emplace(id,spec).second)
        throw std::runtime_error("native duplicate class query");
    } else if (fields[0]=="SIGN_ASSOCIATE") {
      Need(fields,5);
      const int trigger=Integer(fields[1]),associate=Integer(fields[4]);
      if (!data.triggerScope.count(trigger) ||
          !data.pairScope.count({trigger,associate}) ||
          (fields[2]!="CHARM" && fields[2]!="BEAUTY") ||
          (fields[3]!="OS" && fields[3]!="SS"))
        throw std::runtime_error("native signed associate is outside scanned scope");
      auto& members=query.signAssociates[{trigger,fields[2],fields[3]}];
      if (std::find(members.begin(),members.end(),associate)!=members.end())
        throw std::runtime_error("native signed associate duplicates");
      members.push_back(associate);
    } else if (fields[0]=="POINT") {
      Need(fields,15);
      Point point;
      point.id=Integer(fields[1]);point.role=fields[2];point.quantity=fields[3];
      point.tune=fields[4];point.referenceTune=fields[5]=="-"?"":fields[5];
      point.profile=fields[6]=="-"?"":fields[6];point.classId=Integer(fields[7]);
      point.trigger=Integer(fields[8]);point.associate=Integer(fields[9]);
      point.referencePdg=Integer(fields[10]);point.component=fields[11];
      point.axis=fields[12]=="-"?"":fields[12];point.bin=Integer(fields[13]);
      if (fields[14]!="TEST_ONLY_DIAGNOSTIC")
        throw std::runtime_error("native diagnostic query marker differs");
      if (point.id!=static_cast<int>(query.points.size()) ||
          !data.tunes.count(point.tune) ||
          (!point.referenceTune.empty() && !data.tunes.count(point.referenceTune)))
        throw std::runtime_error("native point ID/tune domain differs");
      if (!query.dphiBins || !query.g9PtBins || !query.classes.count(point.classId))
        throw std::runtime_error("native point precedes its axis/class declaration");
      if (!point.profile.empty() && !data.profiles.count(point.profile))
        throw std::runtime_error("native point profile is outside scanned scope");
      const bool correlation=point.role=="correlations.charm" ||
          point.role=="correlations.beauty";
      const bool balancing=point.role=="balancing.activity.charm" ||
          point.role=="balancing.activity.beauty" ||
          point.role=="balancing.integrated.charm" ||
          point.role=="balancing.integrated.beauty" ||
          point.role=="balancing.baryon_meson.activity";
      if (correlation &&
          ((query.density && query.dphiEdges.size()!=static_cast<std::size_t>(query.dphiBins)) ||
           point.quantity!=(point.referenceTune.empty()?
                (query.density?"dphi_density_per_trigger":"dphi_per_trigger"):
                "ratio_to_reference_tune")))
        throw std::runtime_error("native correlation formula/axis differs");
      if (!correlation && point.quantity=="dphi_density_per_trigger")
        throw std::runtime_error("native density role differs");
      if (correlation || balancing) {
        if (point.profile.empty() ||
            (correlation && (point.axis!="dphi" || point.bin<0 ||
                             point.bin>=query.dphiBins ||
                             (point.component!="OS" && point.component!="SS" &&
                              point.component!="NET"))) ||
            (balancing && (point.bin!=-1 || !point.axis.empty())))
          throw std::runtime_error("native correlation/balance point shape differs");
        const bool signSum=correlation && point.associate==0 &&
            (point.quantity=="dphi_per_trigger" || point.quantity=="dphi_density_per_trigger") &&
            (point.component=="OS" || point.component=="SS" ||
             point.component=="NET") &&
            point.referencePdg==0 && point.classId==0 &&
            point.referenceTune.empty();
        if (!data.triggerScope.count(point.trigger) ||
            (!signSum && (!data.pairScope.count({point.trigger,point.associate}) ||
                          !data.pairScope.count({point.trigger,-point.associate}))))
          throw std::runtime_error("native point OS/SS pair is outside scanned scope");
        if (point.associate==0 && !signSum)
          throw std::runtime_error("native aggregate correlation identity differs");
        if (signSum) {
          const std::string sector=point.role=="correlations.charm"?"CHARM":"BEAUTY";
          const std::string signComponent=point.component=="NET"?"OS":point.component;
          const auto& members=query.signAssociates.at(
              {point.trigger,sector,signComponent});
          const auto& opposite=query.signAssociates.at(
              {point.trigger,sector,signComponent=="OS"?"SS":"OS"});
          if (members.empty() || members.size()!=opposite.size())
            throw std::runtime_error("native sign-summed domain is incomplete");
          for (int member:members)
            if (std::find(opposite.begin(),opposite.end(),-member)==opposite.end())
              throw std::runtime_error("native sign-summed conjugate differs");
        }
        if (point.role=="balancing.baryon_meson.activity" &&
            (!data.pairScope.count({point.trigger,point.referencePdg}) ||
             !data.pairScope.count({point.trigger,-point.referencePdg})))
          throw std::runtime_error("native P8 meson pair is outside scanned scope");
      } else if (point.role=="multiplicity.composite") {
        if (!point.profile.empty() || point.classId!=0 || point.axis!="nch" ||
            point.bin<0 || point.bin>=data.activityBins)
          throw std::runtime_error("native P1 point shape differs");
      } else if (point.role=="spectra.signed_heavy") {
        if (!point.profile.empty() || point.classId!=0 ||
            (point.axis!="pt" && point.axis!="eta" && point.axis!="phi") ||
            point.bin< -1 || (point.axis=="pt" && point.bin>query.g9PtBins) ||
            !data.g9Scope.count(point.associate))
          throw std::runtime_error("native G9 point shape/scope differs");
      } else if (point.role=="accounting.natural_final_heavy") {
        if (!point.profile.empty() || point.classId!=0 || !point.axis.empty() ||
            point.bin!=-1 ||
            (point.component!="hadron_count" &&
             point.component!="charm_plus_anticharm_constituent_count" &&
             point.component!="beauty_plus_antibeauty_constituent_count") ||
            (point.quantity!="raw_count" &&
             point.quantity!="raw_weighted_sum" &&
             point.quantity!="normalized_yield") ||
            !data.t1Scope.count(point.associate))
          throw std::runtime_error("native T1 point shape/scope differs");
      } else {
        throw std::runtime_error("native point role is unsupported");
      }
      query.points.push_back(point);
    } else throw std::runtime_error("native query record differs");
  }
  if (!ended || input.peek()!=std::ifstream::traits_type::eof() ||
      query.points.empty() || query.classes.empty() || !query.dphiBins ||
      query.sourceFamilyDigests.size()!=data.tunes.size() ||
      query.requestSha.empty())
    throw std::runtime_error("native point ending/domain differs");
  if (query.density && query.dphiEdges.size()!=static_cast<std::size_t>(query.dphiBins))
    throw std::runtime_error("native angular bin domain is incomplete");
  return query;
}

class Evaluator {
 public:
  Evaluator(const Data& data,const Queries& query):data_(data),query_(query) {
    for (const auto& [key,value]:data.triggers) {
      const auto& [profile,tune,block,activity,pdg]=key;
      triggerGroups_[{profile,tune,block,pdg}].push_back({activity,value});
    }
    for (const auto& [key,value]:data.pairs) {
      const auto& [profile,tune,block,activity,trigger,associate,sign,bin]=key;
      pairGroups_[{profile,tune,block,trigger,associate,sign,bin}]
          .push_back({activity,value});
      pairGroups_[{profile,tune,block,trigger,associate,sign,-1}]
          .push_back({activity,value});
    }
  }
  std::optional<double> Value(const Point& point,const std::string& tune,
                              int omit) {
    if (point.role=="multiplicity.composite") {
      const auto& histogram=Histogram(tune,omit);
      const double denominator=HR::Sum(histogram);
      return denominator==0.0?std::nullopt:
          std::optional<double>(histogram[point.bin]/denominator);
    }
    if (point.role=="spectra.signed_heavy") {
      if (!G9Failure(tune,omit,point.associate).empty())return std::nullopt;
      const double denominator=G9Total(tune,omit,point.associate);
      const int queried=point.bin+1;
      return G9(tune,omit,point.associate,point.axis,queried)/denominator;
    }
    if (point.role=="accounting.natural_final_heavy") {
      const int component=point.component=="hadron_count"?0:
          point.component=="charm_plus_anticharm_constituent_count"?1:2;
      std::vector<double> counts,events;
      for (int block=1;block<=10;++block) if (block!=omit) {
        const auto item=data_.t1.find({tune,block,point.associate});
        const T1 value=item==data_.t1.end()?T1{}:item->second;
        counts.push_back(point.quantity=="raw_weighted_sum"?
                         value.weighted[component]:value.count[component]);
        events.push_back(double(Get(data_.exposure,EKey{tune,block})));
      }
      if (point.quantity!="normalized_yield") return HR::Sum(counts);
      const double exposure=HR::Sum(events);
      return exposure==0.0?std::nullopt:std::optional<double>(HR::Sum(counts)/exposure);
    }
    const auto bounds=Class(tune,omit,point.classId);
    if (!bounds || bounds->empty) return std::nullopt;
    if (point.role.rfind("correlations.",0)==0) {
      const double width=query_.density?
          query_.dphiEdges.at(point.bin).second-query_.dphiEdges.at(point.bin).first:1.;
      if (point.associate==0) {
        const double denominator=Trigger(point.profile,tune,omit,*bounds,
                                         point.trigger);
        if (denominator==0.0)return std::nullopt;
        const double numerator=(point.component=="NET"?
            SignPairValue(point,tune,omit,*bounds,"OS",point.bin)-
            SignPairValue(point,tune,omit,*bounds,"SS",point.bin):
            SignPairValue(point,tune,omit,*bounds,point.component,point.bin));
        return (numerator/denominator)/width;
      }
      const double os=Pair(point.profile,tune,omit,*bounds,point.trigger,
                           point.associate,-1,point.bin);
      const double ss=Pair(point.profile,tune,omit,*bounds,point.trigger,
                           -point.associate,1,point.bin);
      const double denominator=Trigger(point.profile,tune,omit,*bounds,point.trigger);
      if (denominator==0.0) return std::nullopt;
      const double numerator=point.component=="OS"?os:
          point.component=="SS"?ss:os-ss;
      return (numerator/denominator)/width;
    }
    const double os=Pair(point.profile,tune,omit,*bounds,point.trigger,
                         point.associate,-1,-1);
    const double ss=Pair(point.profile,tune,omit,*bounds,point.trigger,
                         -point.associate,1,-1);
    const double net=os-ss;
    if (point.role=="balancing.baryon_meson.activity") {
      const double refOs=Pair(point.profile,tune,omit,*bounds,point.trigger,
                              point.referencePdg,-1,-1);
      const double refSs=Pair(point.profile,tune,omit,*bounds,point.trigger,
                              -point.referencePdg,1,-1);
      const double denominator=refOs-refSs;
      return denominator==0.0?std::nullopt:
          std::optional<double>(net/denominator);
    }
    const double denominator=Trigger(point.profile,tune,omit,*bounds,point.trigger);
    return denominator==0.0?std::nullopt:
        std::optional<double>(net/denominator);
  }

  std::optional<HR::ActivityClassBoundary> Class(const std::string& tune,
                                                  int omit,int classId) {
    const auto key=std::make_tuple(tune,omit,classId);
    const auto prior=boundaries_.find(key);
    if (prior!=boundaries_.end()) return prior->second;
    const auto spec=query_.classes.find(classId);
    if (spec==query_.classes.end())
      throw std::runtime_error("native unknown class ID");
    try {
      const auto boundary=HR::ResolveActivityClass(Histogram(tune,omit),spec->second);
      boundaries_.emplace(key,boundary);
      return boundary;
    } catch (const std::domain_error&) {
      boundaries_.emplace(key,std::nullopt);
      return std::nullopt;
    }
  }

  std::optional<double> ClassWeight(const std::string& tune,int omit,
                                     const HR::ActivityClassBoundary& boundary) {
    if (boundary.empty)return 0.0;
    const auto& histogram=Histogram(tune,omit);
    if (boundary.low<0 || boundary.high>=static_cast<int>(histogram.size()))
      throw std::runtime_error("native class boundary exceeds activity domain");
    return HR::Sum(std::vector<double>(histogram.begin()+boundary.low,
                                        histogram.begin()+boundary.high+1));
  }

  bool MarginResolved(const std::string& tune,int classId) {
    const auto& spec=query_.classes.at(classId);
    if (spec.integrated) return true;
    for (int percentile:{spec.lowPercent,spec.highPercent}) {
      if (percentile==0 || percentile==100) continue;
      const auto key=std::make_pair(tune,percentile);
      auto found=marginResolved_.find(key);
      if (found==marginResolved_.end()) {
        bool resolved=false;
        try {
          const auto audit=HR::AuditActivityThreshold(BlockHistograms(tune),
                                                      percentile);
          resolved=audit.statisticallyResolved &&
              (data_.supportUpper.empty() ||
               NumericallyResolvedActivityThreshold(tune,audit));
        } catch (const std::domain_error&) {
          // Undefined pooled activity remains a point-local unavailable state.
        }
        found=marginResolved_.emplace(key,resolved).first;
      }
      if (!found->second) return false;
    }
    return true;
  }

  std::vector<std::string> DenominatorReasons(const Point& point) {
    if (data_.supportUpper.empty() ||
        (point.role=="accounting.natural_final_heavy" &&
         point.quantity!="normalized_yield")) return {};
    std::vector<HR::DenominatorSeries> series;
    const auto append=[&](const std::string& tune,bool reference) {
      const bool classDependent=point.role.rfind("correlations.",0)==0 ||
          point.role.rfind("balancing.",0)==0;
      const auto boundary=classDependent?Class(tune,0,point.classId):
          std::optional<HR::ActivityClassBoundary>{
              HR::ActivityClassBoundary{0,data_.activityBins-1,false}};
      if (!boundary || boundary->empty) return;
      HR::DenominatorSeries denominator;
      denominator.id=(reference?"REFERENCE_":"SOURCE_")+tune+"_INTERNAL";
      // P8 tune comparisons are (A_s/M_s)/(A_r/M_r). M_r moves into
      // the numerator after algebra, so its sign-resolution requirement does
      // not survive as a denominator prerequisite. Existence remains audited.
      denominator.algebraicallySurvives=!(reference &&
          point.role=="balancing.baryon_meson.activity");
      const std::string family=point.role=="multiplicity.composite"?"activity":
          point.role=="spectra.signed_heavy"?"kinematics":
          point.role=="accounting.natural_final_heavy"?"activity":
          point.role=="balancing.baryon_meson.activity"?"pairs":"triggers";
      denominator.exact=point.role=="accounting.natural_final_heavy";
      for (int block=1;block<=10;++block) {
        const auto cell=InternalDenominatorBlock(point,tune,block,*boundary);
        denominator.blocks.push_back(cell.value);
        denominator.absoluteErrorBounds.push_back(
            denominator.exact?0.0:NumericalBound(cell,family));
      }
      series.push_back(std::move(denominator));
      if (reference) {
        HR::DenominatorSeries numerator;
        numerator.id="REFERENCE_"+tune+"_RATIO_NUMERATOR";
        const std::string numeratorFamily=point.role=="multiplicity.composite"?
            "activity":point.role=="spectra.signed_heavy"?"kinematics":"pairs";
        for (int block=1;block<=10;++block) {
          const auto cell=NumeratorBlock(point,tune,block,*boundary);
          numerator.blocks.push_back(cell.value);
          numerator.absoluteErrorBounds.push_back(
              NumericalBound(cell,numeratorFamily));
        }
        series.push_back(std::move(numerator));
      }
    };
    append(point.tune,false);
    if (!point.referenceTune.empty())append(point.referenceTune,true);
    HR::JackknifeResult audit;
    audit.blocks=10;
    HR::AuditDenominators(series,HR::EstimatorPolicy{},audit);
    return audit.reasons;
  }

  using Components=std::vector<std::pair<std::string,double>>;
  std::optional<Components> BlockPrimitives(const Point& point,
                                             const std::string& tune,int block) {
    if (point.role=="multiplicity.composite")
      return Components{{"activity_bin",ActivityBlock(tune,block,point.bin).value},
                        {"activity_total",ActivityBlock(tune,block,-1).value}};
    if (point.role=="spectra.signed_heavy")
      return Components{{"g9_bin",G9Block(point,tune,block,false).value},
                        {"g9_total",G9Block(point,tune,block,true).value}};
    if (point.role=="accounting.natural_final_heavy") {
      const int component=point.component=="hadron_count"?0:
          point.component=="charm_plus_anticharm_constituent_count"?1:2;
      const auto found=data_.t1.find({tune,block,point.associate});
      const T1 value=found==data_.t1.end()?T1{}:found->second;
      return Components{{"natural_count",value.count[component]},
                        {"natural_weighted_sum",value.weighted[component]},
                        {"event_exposure",double(Get(data_.exposure,EKey{tune,block}))}};
    }
    const auto bounds=Class(tune,0,point.classId);
    if (!bounds || bounds->empty)return std::nullopt;
    const int selectedBin=point.role.rfind("correlations.",0)==0?point.bin:-1;
    const auto os=point.associate==0?
        SignPairBlock(point,tune,block,*bounds,"OS",selectedBin):
        PairBlock(point,tune,block,*bounds,point.associate,-1,selectedBin);
    const auto ss=point.associate==0?
        SignPairBlock(point,tune,block,*bounds,"SS",selectedBin):
        PairBlock(point,tune,block,*bounds,-point.associate,1,selectedBin);
    Components result{{"pair_os",os.value},
                      {"pair_ss",ss.value},
                      {"trigger",TriggerBlock(point,tune,block,*bounds).value}};
    if (point.role=="balancing.baryon_meson.activity") {
      result.emplace_back("reference_pair_os",PairBlock(point,tune,block,*bounds,
                                          point.referencePdg,-1,-1).value);
      result.emplace_back("reference_pair_ss",PairBlock(point,tune,block,*bounds,
                                          -point.referencePdg,1,-1).value);
    }
    return result;
  }

  using Parents=std::vector<std::pair<std::string,bool>>;
  static Parents ParentDomain(const Point& point) {
    if (point.quantity=="raw_count" || point.quantity=="raw_weighted_sum")return {};
    if (point.quantity=="normalized_yield")return {{"accepted_event_exposure",true}};
    if (point.quantity=="normalized_distribution" ||
        point.quantity=="normalized_spectrum")return {{"normalization_total",true}};
    if (point.quantity=="dphi_per_trigger" || point.quantity=="dphi_density_per_trigger" ||
        point.quantity=="os_minus_ss_per_trigger")return {{"trigger",true}};
    if (point.quantity=="spectrum_ratio_to_reference_tune")
      return {{"source_normalization_total",true},
              {"reference_normalization_total",true},
              {"reference_tune_bin_"+std::to_string(point.bin),true}};
    if (point.quantity=="baryon_meson_reference_ratio")
      return {{"shared_trigger",false},{"reference_os_minus_ss",true}};
    if (point.quantity=="baryon_meson_ratio_to_reference_tune")
      return {{"source_shared_trigger",false},
              {"source_meson_os_minus_ss",true},
              {"reference_shared_trigger",false},
              {"reference_meson_os_minus_ss",false},
              {"reference_tune_numerator_os_minus_ss",true}};
    if (point.quantity=="ratio_to_reference_tune") {
      if (point.role=="multiplicity.composite")
        return {{"reference_tune_bin_"+std::to_string(point.bin),true}};
      if (point.role.rfind("correlations.",0)==0) {
        std::string component=point.component=="NET"?"OS_MINUS_SS":point.component;
        std::transform(component.begin(),component.end(),component.begin(),
                       [](unsigned char c){return static_cast<char>(std::tolower(c));});
        return {{"reference_tune_"+component,true}};
      }
      return {{"reference_tune_os_minus_ss",true}};
    }
    throw std::runtime_error("native denominator parent formula is absent");
  }

  std::optional<double> ParentValue(const Point& point,const std::string& name,
                                    int omit) {
    const bool reference=name.rfind("reference_",0)==0 &&
        name!="reference_os_minus_ss";
    const std::string& tune=reference?point.referenceTune:point.tune;
    if (tune.empty())throw std::runtime_error("native denominator reference tune is absent");
    if (name=="normalization_total" || name=="source_normalization_total" ||
        name=="reference_normalization_total") {
      if (point.role=="multiplicity.composite")return HR::Sum(Histogram(tune,omit));
      if (point.role=="spectra.signed_heavy")
        return G9Total(tune,omit,point.associate);
      throw std::runtime_error("native normalization parent role differs");
    }
    if (name=="accepted_event_exposure") {
      std::vector<double> values;
      for (int block=1;block<=10;++block)if(block!=omit)
        values.push_back(double(Get(data_.exposure,EKey{tune,block})));
      return HR::Sum(values);
    }
    if (name.rfind("reference_tune_bin_",0)==0 ||
        (name.rfind("reference_tune_",0)==0 &&
         name!="reference_tune_numerator_os_minus_ss"))
      return Value(point,point.referenceTune,omit);
    const auto bounds=Class(tune,omit,point.classId);
    if (!bounds || bounds->empty)return std::nullopt;
    if (name=="trigger" || name=="shared_trigger" ||
        name=="source_shared_trigger" || name=="reference_shared_trigger")
      return Trigger(point.profile,tune,omit,*bounds,point.trigger);
    const auto net=[&](int associate){
      return Pair(point.profile,tune,omit,*bounds,point.trigger,associate,-1,-1)-
             Pair(point.profile,tune,omit,*bounds,point.trigger,-associate,1,-1);
    };
    if (name=="reference_os_minus_ss" ||
        name=="source_meson_os_minus_ss" ||
        name=="reference_meson_os_minus_ss")return net(point.referencePdg);
    if (name=="reference_tune_numerator_os_minus_ss")return net(point.associate);
    throw std::runtime_error("native denominator parent name differs");
  }

  std::string G9Status(const std::string& tune,int omit,int pdg) {
    return G9Failure(tune,omit,pdg);
  }
 private:
  bool NumericallyResolvedActivityThreshold(
      const std::string& tune,const HR::ActivityThresholdAudit& audit) const {
    const double fraction=(100.0-audit.percentile)/100.0;
    std::vector<double> below,through,belowErrors,throughErrors,arithmeticTerms;
    for (int block=1;block<=10;++block) {
      const auto counts=static_cast<std::uint64_t>(
          Get(data_.exposure,EKey{tune,block}));
      const auto lower=ActivityRangeBlock(tune,block,audit.pooledThreshold-1);
      const auto upper=ActivityRangeBlock(tune,block,audit.pooledThreshold);
      const auto total=ActivityRangeBlock(tune,block,data_.activityBins-1);
      const double totalError=NumericalBound(total,"activity",counts);
      below.push_back(lower.value-fraction*total.value);
      through.push_back(upper.value-fraction*total.value);
      belowErrors.push_back(NumericalBound(lower,"activity",counts)+
          fraction*totalError);
      throughErrors.push_back(NumericalBound(upper,"activity",counts)+
          fraction*totalError);
      arithmeticTerms.push_back(std::abs(lower.value)+std::abs(upper.value)+
                                2.0*fraction*std::abs(total.value));
    }
    const double lower=HR::Sum(below),upper=HR::Sum(through);
    const double arithmetic=16.0*std::numeric_limits<double>::epsilon()*
                            HR::Sum(arithmeticTerms);
    return std::isfinite(lower) && std::isfinite(upper) &&
        -lower>HR::Sum(belowErrors)+arithmetic &&
        upper>HR::Sum(throughErrors)+arithmetic;
  }
  double NumericalBound(const Weighted& cell,const std::string& family,
                        std::optional<std::uint64_t> rowsOverride={}) const {
    const auto rows=rowsOverride.value_or(data_.supportUpper.at(family));
    if (!std::isfinite(cell.sumw2) || cell.sumw2<0.0 ||
        (cell.value!=0.0 && cell.sumw2==0.0) ||
        (rows==0 && cell.sumw2!=0.0))
      return std::numeric_limits<double>::infinity();
    // Cauchy bounds the unrecorded raw absolute weight sum by sqrt(N*Sumw2),
    // where N is the authenticated exact-support row count for this family
    // across all shards. It intentionally overbounds every selected block.
    constexpr double unit=0x1p-53;
    const double operations=4.0*static_cast<double>(rows)+4.0;
    if (operations*unit>=1.0)
      return std::numeric_limits<double>::infinity();
    const double upperSquares=std::nextafter(cell.sumw2/(1.0-operations*unit),
                                             std::numeric_limits<double>::infinity());
    const double sumabs=std::sqrt(static_cast<double>(rows)*upperSquares);
    return HR::AccumulationErrorBound(sumabs,rows);
  }
  static Weighted GroupSum(const std::vector<ActivityValue>& cells,
                           const HR::ActivityClassBoundary& bounds) {
    std::vector<double> values,squares;
    for (const auto& cell:cells) if (bounds.low<=cell.activity &&
                                    cell.activity<=bounds.high) {
      values.push_back(cell.measure.value);
      squares.push_back(cell.measure.sumw2);
    }
    return {HR::Sum(values),HR::Sum(squares)};
  }
  Weighted ActivityBlock(const std::string& tune,int block,int selectedBin) const {
    if (selectedBin>=0) {
      const auto found=data_.activity.find({tune,block,selectedBin});
      return found==data_.activity.end()?Weighted{}:found->second;
    }
    const EKey key{tune,block};
    const auto cached=activityTotals_.find(key);
    if (cached!=activityTotals_.end())return cached->second;
    std::vector<double> values,squares;
    for (int bin=0;bin<data_.activityBins;++bin) {
      const auto item=data_.activity.find({tune,block,bin});
      if (item==data_.activity.end())continue;
      values.push_back(item->second.value);
      squares.push_back(item->second.sumw2);
    }
    return activityTotals_.emplace(key,Weighted{HR::Sum(values),
                                                HR::Sum(squares)}).first->second;
  }
  Weighted ActivityRangeBlock(const std::string& tune,int block,int lastBin) const {
    std::vector<double> values,squares;
    for (int bin=0;bin<=lastBin;++bin) {
      const auto item=data_.activity.find({tune,block,bin});
      if (item==data_.activity.end())continue;
      values.push_back(item->second.value);
      squares.push_back(item->second.sumw2);
    }
    return {HR::Sum(values),HR::Sum(squares)};
  }
  Weighted TriggerBlock(const Point& point,const std::string& tune,int block,
                        const HR::ActivityClassBoundary& boundary) const {
    const auto found=triggerGroups_.find({point.profile,tune,block,point.trigger});
    return found==triggerGroups_.end()?Weighted{}:GroupSum(found->second,boundary);
  }
  Weighted PairBlock(const Point& point,const std::string& tune,int block,
                     const HR::ActivityClassBoundary& boundary,int associate,
                     int sign,int bin) const {
    const auto found=pairGroups_.find({point.profile,tune,block,point.trigger,
                                      associate,sign,bin});
    return found==pairGroups_.end()?Weighted{}:GroupSum(found->second,boundary);
  }
  const std::vector<int>& SignMembers(const Point& point,
                                      const std::string& component) const {
    const std::string sector=point.role=="correlations.charm"?"CHARM":"BEAUTY";
    return query_.signAssociates.at({point.trigger,sector,component});
  }
  Weighted SignPairBlock(const Point& point,const std::string& tune,int block,
                         const HR::ActivityClassBoundary& boundary,
                         const std::string& component,int bin) const {
    std::vector<double> values,squares;
    const int sign=component=="OS"?-1:1;
    for (int associate:SignMembers(point,component)) {
      const auto cell=PairBlock(point,tune,block,boundary,associate,sign,bin);
      values.push_back(cell.value);squares.push_back(cell.sumw2);
    }
    return {HR::Sum(values),HR::Sum(squares)};
  }
  double SignPairValue(const Point& point,const std::string& tune,int omit,
                       const HR::ActivityClassBoundary& boundary,
                       const std::string& component,int bin) const {
    std::vector<double> values;
    const int sign=component=="OS"?-1:1;
    for (int associate:SignMembers(point,component))
      values.push_back(Pair(point.profile,tune,omit,boundary,point.trigger,
                            associate,sign,bin));
    return HR::Sum(values);
  }
  Weighted PairNumeratorBlock(const Point& point,const std::string& tune,int block,
                              const HR::ActivityClassBoundary& boundary,
                              int associate,int bin) const {
    if (point.role.rfind("correlations.",0)==0 && associate==0) {
      if (point.component!="NET")
        return SignPairBlock(point,tune,block,boundary,point.component,bin);
      const auto os=SignPairBlock(point,tune,block,boundary,"OS",bin);
      const auto ss=SignPairBlock(point,tune,block,boundary,"SS",bin);
      return {os.value-ss.value,os.sumw2+ss.sumw2};
    }
    const auto os=PairBlock(point,tune,block,boundary,associate,-1,bin);
    const auto ss=PairBlock(point,tune,block,boundary,-associate,1,bin);
    if (point.role.rfind("correlations.",0)==0 && point.component=="OS")return os;
    if (point.role.rfind("correlations.",0)==0 && point.component=="SS")return ss;
    return {os.value-ss.value,os.sumw2+ss.sumw2};
  }
  Weighted G9Block(const Point& point,const std::string& tune,int block,
                   bool total) const {
    const HKey key{tune,block,point.associate};
    if (total) {
      const auto cached=g9BlockTotals_.find(key);
      if (cached!=g9BlockTotals_.end())return cached->second;
    } else {
      const auto found=data_.g9.find({tune,block,point.associate,
                                      point.axis,point.bin+1});
      return found==data_.g9.end()?Weighted{}:found->second;
    }
    std::vector<double> values,squares;
    const int first=total?0:point.bin+1;
    const int last=total?query_.g9PtBins+1:first;
    for (int bin=first;bin<=last;++bin) {
      const auto item=data_.g9.find({tune,block,point.associate,
                                     total?"pt":point.axis,bin});
      if (item==data_.g9.end())continue;
      values.push_back(item->second.value);
      squares.push_back(item->second.sumw2);
    }
    return g9BlockTotals_.emplace(key,Weighted{HR::Sum(values),
                                               HR::Sum(squares)}).first->second;
  }
  Weighted InternalDenominatorBlock(const Point& point,const std::string& tune,
                                    int block,const HR::ActivityClassBoundary& boundary) const {
    if (point.role=="multiplicity.composite")return ActivityBlock(tune,block,-1);
    if (point.role=="spectra.signed_heavy")return G9Block(point,tune,block,true);
    if (point.role=="accounting.natural_final_heavy")
      return {double(Get(data_.exposure,EKey{tune,block})),0.0};
    if (point.role=="balancing.baryon_meson.activity")
      return PairNumeratorBlock(point,tune,block,boundary,point.referencePdg,-1);
    return TriggerBlock(point,tune,block,boundary);
  }
  Weighted NumeratorBlock(const Point& point,const std::string& tune,int block,
                          const HR::ActivityClassBoundary& boundary) const {
    if (point.role=="multiplicity.composite")
      return ActivityBlock(tune,block,point.bin);
    if (point.role=="spectra.signed_heavy")return G9Block(point,tune,block,false);
    return PairNumeratorBlock(point,tune,block,boundary,point.associate,
                              point.role.rfind("correlations.",0)==0?point.bin:-1);
  }
  const std::vector<std::vector<double>>& BlockHistograms(
      const std::string& tune) {
    const auto found=blockHistograms_.find(tune);
    if (found!=blockHistograms_.end()) return found->second;
    std::vector<std::vector<double>> blocks(
        10,std::vector<double>(data_.activityBins,0.0));
    for (int block=1;block<=10;++block)
      for (int bin=0;bin<data_.activityBins;++bin)
        blocks[block-1][bin]=Get(data_.activity,AKey{tune,block,bin});
    return blockHistograms_.emplace(tune,std::move(blocks)).first->second;
  }
  static void AddInClass(const std::vector<ActivityValue>& cells,
                         const HR::ActivityClassBoundary& bounds,
                         std::vector<double>& values) {
    const auto first=std::lower_bound(cells.begin(),cells.end(),bounds.low,
        [](const auto& cell,int low){return cell.activity<low;});
    for (auto cursor=first;cursor!=cells.end() && cursor->activity<=bounds.high;
         ++cursor)
      values.push_back(cursor->measure.value);
  }
  const std::vector<double>& Histogram(const std::string& tune,int omit) {
    const auto key=std::make_pair(tune,omit);
    const auto found=histograms_.find(key);
    if (found!=histograms_.end()) return found->second;
    std::vector<double> values;
    values.reserve(data_.activityBins);
    for (int bin=0;bin<data_.activityBins;++bin)
      values.push_back(Activity(tune,omit,bin));
    return histograms_.emplace(key,std::move(values)).first->second;
  }
  double G9Total(const std::string& tune,int omit,int pdg) {
    const auto key=std::make_tuple(tune,omit,pdg);
    const auto found=g9Totals_.find(key);
    if (found!=g9Totals_.end()) return found->second;
    std::vector<double> values;
    values.reserve(query_.g9PtBins+2);
    for (int bin=0;bin<=query_.g9PtBins+1;++bin)
      values.push_back(G9(tune,omit,pdg,"pt",bin));
    return g9Totals_.emplace(key,HR::Sum(values)).first->second;
  }
  std::string G9Failure(const std::string& tune,int omit,int pdg) {
    const auto key=std::make_tuple(tune,omit,pdg);
    const auto found=g9Failures_.find(key);
    if (found!=g9Failures_.end())return found->second;
    std::set<std::pair<std::string,int>> bins;
    for (const auto& [cell,value]:data_.g9) {
      (void)value;
      if (std::get<0>(cell)==tune && std::get<2>(cell)==pdg)
        bins.insert({std::get<3>(cell),std::get<4>(cell)});
    }
    std::string reason;
    for (const auto& [axis,bin]:bins) {
      if (G9(tune,omit,pdg,axis,bin)<0.0) {
        reason="G9_NEGATIVE_AGGREGATE_BIN";
        break;
      }
    }
    if (reason.empty() && !(G9Total(tune,omit,pdg)>0.0))
      reason="G9_NONPOSITIVE_TOTAL";
    return g9Failures_.emplace(key,reason).first->second;
  }
  double Activity(const std::string& tune,int omit,int bin) const {
    std::vector<double> values;
    for (int block=1;block<=10;++block) if (block!=omit)
      values.push_back(Get(data_.activity,AKey{tune,block,bin}));
    return HR::Sum(values);
  }
  double Trigger(const std::string& profile,const std::string& tune,int omit,
                 const HR::ActivityClassBoundary& bounds,int pdg) const {
    std::vector<double> values;
    for (int block=1;block<=10;++block) if (block!=omit) {
      const auto group=triggerGroups_.find({profile,tune,block,pdg});
      if (group!=triggerGroups_.end()) AddInClass(group->second,bounds,values);
    }
    return HR::Sum(values);
  }
  double Pair(const std::string& profile,const std::string& tune,int omit,
              const HR::ActivityClassBoundary& bounds,int trigger,int associate,
              int sign,int selectedBin) const {
    std::vector<double> values;
    for (int block=1;block<=10;++block) if (block!=omit) {
      const auto group=pairGroups_.find({profile,tune,block,trigger,associate,
                                         sign,selectedBin});
      if (group!=pairGroups_.end()) AddInClass(group->second,bounds,values);
    }
    return HR::Sum(values);
  }
  double G9(const std::string& tune,int omit,int pdg,
            const std::string& axis,int bin) const {
    std::vector<double> values;
    for (int block=1;block<=10;++block) if (block!=omit)
      values.push_back(Get(data_.g9,GKey{tune,block,pdg,axis,bin}));
    return HR::Sum(values);
  }
  const Data& data_;
  const Queries& query_;
  std::map<TGroupKey,std::vector<ActivityValue>> triggerGroups_;
  std::map<PGroupKey,std::vector<ActivityValue>> pairGroups_;
  std::map<std::string,std::vector<std::vector<double>>> blockHistograms_;
  std::map<std::pair<std::string,int>,bool> marginResolved_;
  std::map<std::pair<std::string,int>,std::vector<double>> histograms_;
  std::map<std::tuple<std::string,int,int>,double> g9Totals_;
  std::map<std::tuple<std::string,int,int>,std::string> g9Failures_;
  mutable std::map<EKey,Weighted> activityTotals_;
  mutable std::map<HKey,Weighted> g9BlockTotals_;
  std::map<std::tuple<std::string,int,int>,
           std::optional<HR::ActivityClassBoundary>> boundaries_;
};

void Evaluate(const Data& data,const Queries& query,const std::string& path,
              const std::string& blockPath,const std::string& denominatorPath) {
  std::ofstream output(path);
  if (!output) throw std::runtime_error("cannot open native diagnostic output");
  std::ofstream blocks;
  if (!blockPath.empty()) {
    blocks.open(blockPath);
    if (!blocks)throw std::runtime_error("cannot open native block output");
    blocks<<"hadronization_native_block_primitives_v1\n";
    blocks<<"BIND\t"<<query.requestSha<<'\t'<<query.scientificRequestSha<<'\n';
  }
  std::ofstream denominators;
  if (!denominatorPath.empty()) {
    denominators.open(denominatorPath);
    if (!denominators)throw std::runtime_error("cannot open native denominator output");
    denominators<<"hadronization_native_denominator_parents_v1\n";
    denominators<<"BIND\t"<<query.requestSha<<'\t'<<query.scientificRequestSha<<'\n';
  }
  output<<"hadronization_native_engine_diagnostic_v2\n";
  output<<"BIND\t"<<query.requestSha<<'\t'<<query.scientificRequestSha<<'\n';
  Evaluator evaluator(data,query);
  for (const auto& point:query.points) {
    const auto g9SourceFailure=point.role=="spectra.signed_heavy"?
        evaluator.G9Status(point.tune,0,point.associate):std::string{};
    const auto g9ReferenceFailure=point.role=="spectra.signed_heavy" &&
        !point.referenceTune.empty()?
        evaluator.G9Status(point.referenceTune,0,point.associate):std::string{};
    const auto base=evaluator.Value(point,point.tune,0);
    std::optional<double> reference;
    if (!point.referenceTune.empty())
      reference=evaluator.Value(point,point.referenceTune,0);
    double center=0.0;
    bool hasCenter=false;
    if (point.referenceTune.empty()) {
      if (base) {center=*base;hasCenter=true;}
    } else if (base && reference && *reference!=0.0) {
      center=*base / *reference;hasCenter=true;
    }
    const auto denominatorReasons=evaluator.DenominatorReasons(point);
    const bool denominatorValueFailure=std::any_of(
        denominatorReasons.begin(),denominatorReasons.end(),[](const auto& reason){
          return reason.rfind("POOLED_DENOMINATOR_ZERO:",0)==0 ||
                 reason.rfind("DENOMINATOR_NUMERICALLY_UNRESOLVED:",0)==0; });
    const bool denominatorStatisticalFailure=std::any_of(
        denominatorReasons.begin(),denominatorReasons.end(),[](const auto& reason){
          return reason.rfind("DENOMINATOR_STATISTICALLY_UNRESOLVED:",0)==0; });
    if (denominatorValueFailure)hasCenter=false;
    const auto centerSourceBoundary=evaluator.Class(point.tune,0,point.classId);
    const auto centerReferenceBoundary=point.referenceTune.empty()?
        std::optional<HR::ActivityClassBoundary>{}:
        evaluator.Class(point.referenceTune,0,point.classId);
    std::vector<double> sourceLeaves,referenceLeaves;
    bool unstable=false,g9LeafFailure=false;
    for (int block=1;block<=10;++block) {
      if (point.role=="spectra.signed_heavy")
        g9LeafFailure=g9LeafFailure ||
            !evaluator.G9Status(point.tune,block,point.associate).empty() ||
            (!point.referenceTune.empty() &&
             !evaluator.G9Status(point.referenceTune,block,point.associate).empty());
      const auto leaf=evaluator.Value(point,point.tune,block);
      if (point.referenceTune.empty())
        sourceLeaves.push_back(leaf.value_or(std::numeric_limits<double>::quiet_NaN()));
      else
        sourceLeaves.push_back(!leaf || !reference || *reference==0.0?
            std::numeric_limits<double>::quiet_NaN():*leaf / *reference);
      if (point.classId>0) {
        const auto boundary=evaluator.Class(point.tune,block,point.classId);
        unstable=unstable || !boundary || !centerSourceBoundary ||
          boundary->low!=centerSourceBoundary->low ||
          boundary->high!=centerSourceBoundary->high ||
          boundary->empty!=centerSourceBoundary->empty;
      }
      if (!point.referenceTune.empty()) {
        const auto referenceLeaf=evaluator.Value(point,point.referenceTune,block);
        referenceLeaves.push_back(!base || !referenceLeaf || *referenceLeaf==0.0?
            std::numeric_limits<double>::quiet_NaN():*base / *referenceLeaf);
        if (point.classId>0) {
          const auto boundary=evaluator.Class(point.referenceTune,block,point.classId);
          unstable=unstable || !boundary || !centerReferenceBoundary ||
            boundary->low!=centerReferenceBoundary->low ||
            boundary->high!=centerReferenceBoundary->high ||
            boundary->empty!=centerReferenceBoundary->empty;
        }
      }
    }
    const auto familyVariance=[](const std::vector<double>& leaves) {
      if (!HR::FiniteVector(leaves)) return std::numeric_limits<double>::quiet_NaN();
      const double mean=HR::Sum(leaves)/10.0;
      std::vector<double> squared;
      for (const double leaf:leaves) squared.push_back((leaf-mean)*(leaf-mean));
      return 0.9*HR::Sum(squared);
    };
    const double variance=familyVariance(sourceLeaves)+
        (referenceLeaves.empty()?0.0:familyVariance(referenceLeaves));
    const bool marginResolved=point.classId<=0 ||
        (evaluator.MarginResolved(point.tune,point.classId) &&
         (point.referenceTune.empty() ||
          evaluator.MarginResolved(point.referenceTune,point.classId)));
    const bool deterministic=point.role=="accounting.natural_final_heavy" &&
        point.quantity!="normalized_yield";
    const bool valid=hasCenter && std::isfinite(variance) && !unstable &&
        marginResolved && !deterministic && denominatorReasons.empty();
    output<<"R\t"<<point.id<<'\t'
          <<(hasCenter?(denominatorStatisticalFailure?"UNSTABLE_DENOMINATOR":
                     "AVAILABLE"):"UNDEFINED")<<'\t'
          <<(hasCenter?Hex(center):"-")<<'\t'
          <<(valid?(variance==0.0?"AVAILABLE_ZERO_DISPERSION":"AVAILABLE"):
              "WITHHELD_UNCERTAINTY")<<'\t'
          <<(valid?Hex(variance):"-")<<'\t'
          <<(valid?Hex(std::sqrt(variance)):"-")<<'\t'
          <<Leaves(sourceLeaves)<<'\t'<<Leaves(referenceLeaves)<<'\t'
          <<(deterministic?"DETERMINISTIC_ACCOUNTING":
              unstable?"CLASS_BOUNDARY_UNSTABLE":
              !marginResolved?"CLASS_BOUNDARY_UNRESOLVED":
              !g9SourceFailure.empty()?g9SourceFailure:
              !g9ReferenceFailure.empty()?g9ReferenceFailure:
              g9LeafFailure?"G9_INVALID_DELETE_ONE":
              !denominatorReasons.empty()?denominatorReasons.front():
              !hasCenter?"UNDEFINED_CENTER":
              !std::isfinite(variance)?"UNDEFINED_LEAF":"-")<<'\t'
          <<Hex(variance)<<'\n';
    const auto emitFamily=[&](const std::string& tune,
                              const std::vector<double>& leaves) {
      if (leaves.empty()) return;
      if (leaves.size()!=10)throw std::runtime_error("native factor K10 domain differs");
      const bool finite=HR::FiniteVector(leaves);
      const double mean=finite?HR::Sum(leaves)/10.0:
          std::numeric_limits<double>::quiet_NaN();
      for (int block=1;block<=10;++block) {
        const double leaf=leaves[block-1];
        const bool active=valid && finite;
        output<<"F\t"<<point.id<<'\t'<<tune<<'\t'
              <<query.sourceFamilyDigests.at(tune)<<'\t'<<block<<'\t'
              <<int(active)<<'\t'<<Hex(leaf)<<'\t'<<Hex(mean)<<'\t'
              <<(active?Hex(std::sqrt(0.9)*(leaf-mean)):"-")<<'\n';
      }
    };
    emitFamily(point.tune,sourceLeaves);
    if (!point.referenceTune.empty())
      emitFamily(point.referenceTune,referenceLeaves);
    if (blocks) {
      const auto emitBlocks=[&](const std::string& tune){
        for (int block=1;block<=10;++block) {
          const auto components=evaluator.BlockPrimitives(point,tune,block);
          blocks<<"B\t"<<point.id<<'\t'<<tune<<'\t'
                <<query.sourceFamilyDigests.at(tune)<<'\t'<<block<<'\t'
                <<data.exposure.at({tune,block})<<'\t'
                <<(components?"AVAILABLE":"UNDEFINED")<<'\t';
          if (!components)blocks<<"-\t-\n";
          else {
            for (std::size_t index=0;index<components->size();++index)
              blocks<<(index?";":"")<<components->at(index).first;
            blocks<<'\t';
            for (std::size_t index=0;index<components->size();++index)
              blocks<<(index?";":"")<<Hex(components->at(index).second);
            blocks<<'\n';
          }
        }
      };
      emitBlocks(point.tune);
      if (!point.referenceTune.empty())emitBlocks(point.referenceTune);
    }
    if (denominators) {
      const auto status=[](const std::optional<double>& value){
        return !value?"UNDEFINED":*value==0.0?"UNSTABLE_DENOMINATOR":"AVAILABLE";
      };
      for (const auto& [name,retained]:Evaluator::ParentDomain(point)) {
        const auto pooled=evaluator.ParentValue(point,name,0);
        denominators<<"D\t"<<point.id<<'\t'<<name<<'\t'<<int(retained)
                    <<'\t'<<status(pooled)<<'\t'
                    <<(pooled?Hex(*pooled):"-")<<'\t';
        for (int block=1;block<=10;++block) {
          if (block>1)denominators<<';';
          denominators<<status(evaluator.ParentValue(point,name,block));
        }
        denominators<<'\t';
        for (int block=1;block<=10;++block) {
          if (block>1)denominators<<';';
          const auto value=evaluator.ParentValue(point,name,block);
          denominators<<(value?Hex(*value):"-");
        }
        denominators<<'\n';
      }
    }
  }
  for (const auto& tune:data.tunes)
    for (const auto& [classId,spec]:query.classes) {
      (void)spec;
      for (int omit=0;omit<=10;++omit) {
        const auto boundary=evaluator.Class(tune,omit,classId);
        const auto weight=boundary?evaluator.ClassWeight(tune,omit,*boundary):
            std::optional<double>{};
        output<<"Q\t"<<tune<<'\t'<<query.sourceFamilyDigests.at(tune)
              <<'\t'<<classId<<'\t'<<omit<<'\t'
              <<(boundary?"RESOLVED":"UNRESOLVED")<<'\t'
              <<(boundary?std::to_string(boundary->low):"-")<<'\t'
              <<(boundary?std::to_string(boundary->high):"-")<<'\t'
              <<(boundary?int(boundary->empty):1)<<'\t'
              <<(weight?Hex(*weight):"-")<<'\n';
      }
    }
  output<<"END\n";
  if (blocks)blocks<<"END\n";
  if (denominators)denominators<<"END\n";
}
}

int main(int argc,char** argv) {
  try {
    if (argc<5 || argc>7)
      throw std::runtime_error("usage: native_engine primitives index_sha points output [blocks] [denominators]");
    auto data=ReadData(argv[1],argv[2]);
    const auto queries=ReadQueries(argv[3],data);
    Evaluate(data,queries,argv[4],argc>=6?argv[5]:"",argc==7?argv[6]:"");
    return 0;
  } catch (const std::exception& error) {
    std::cerr<<error.what()<<'\n';
    return 1;
  }
}
