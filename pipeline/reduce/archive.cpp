#include <TFile.h>
#include <TKey.h>
#include <TObjString.h>
#include <TTree.h>
#include <algorithm>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <memory>
#include <map>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {
using U = ULong64_t;
std::vector<std::string> Split(const std::string& s, char delimiter='\t') {
  std::vector<std::string> out; std::istringstream in(s); std::string item;
  while (std::getline(in,item,delimiter)) out.push_back(item);
  if (!s.empty() && s.back()==delimiter) out.emplace_back();
  return out;
}
std::string Decode(const std::string& s) {
  if (s=="-") return "";
  if (s.size()%2) throw std::runtime_error("odd hexadecimal text");
  std::string out;
  for (std::size_t i=0;i<s.size();i+=2) {
    const auto token=s.substr(i,2);
    if (token.find_first_not_of("0123456789abcdef")!=std::string::npos)
      throw std::runtime_error("invalid hexadecimal text");
    out.push_back(static_cast<char>(std::stoul(token,nullptr,16)));
  }
  return out;
}
std::string Encode(const std::string& s) {
  if (s.empty()) return "-";
  static const char* h="0123456789abcdef"; std::string out;
  for (unsigned char c:s) {out+=h[c>>4];out+=h[c&15];}
  return out;
}
double Number(const std::string& s) {
  std::size_t consumed=0;
  const double value=std::stod(s,&consumed);
  if(consumed!=s.size()||!std::isfinite(value))
    throw std::runtime_error("invalid finite numerical field");
  return value;
}
bool Boolean(const std::string& s) {
  if(s=="1")return true;
  if(s=="0")return false;
  throw std::runtime_error("archive boolean is not 0 or 1");
}
std::string Hex(double d) {std::ostringstream s;s<<std::hexfloat<<d;return s.str();}
void Need(const std::vector<std::string>& f,std::size_t n) {
  if(f.size()!=n)throw std::runtime_error("archive record width differs");
}

void Pack(const std::string& transport,const std::string& path) {
  TFile file(path.c_str(),"CREATE","",505);
  if(file.IsZombie())throw std::runtime_error("archive exists or cannot create");
  U id=0,root=0; std::string kind,text;std::vector<U> children;std::vector<std::string> keys;
  TTree nodes("nodes","Deduplicated typed value DAG; children always precede parents");
  nodes.Branch("id",&id);nodes.Branch("kind",&kind);nodes.Branch("text",&text);
  nodes.Branch("children",&children);nodes.Branch("keys",&keys);
  std::string payloadSchema,requestSha,scientificRequestSha,scienceContentSha,packageState,campaignState,
    campaignDescriptorSha,selectedMembersSha,sourceMembersSha,analysisSha,particleSha,activitySha,
    selectionSha,formulaSha,statisticsSha,querySha,uncertaintyScope,inputRootSha,inputContentSha,
    manifestSha,sourceFilesetSha;
  Bool_t hasQuerySha=false;U inputRootBytes=0;
  TTree bindings("archive_bindings","Scientific, configuration, provenance, and input identities");
  std::string g9MetadataJson,g9MetadataSha;bool g9Seen=false;
  TTree g9Science("g9_science","Validated G9 selection and normalization metadata");
  g9Science.Branch("metadata_json",&g9MetadataJson);
  g9Science.Branch("metadata_sha256",&g9MetadataSha);
  bindings.Branch("schema",&payloadSchema);bindings.Branch("request_sha256",&requestSha);
  bindings.Branch("scientific_request_sha256",&scientificRequestSha);bindings.Branch("science_content_sha256",&scienceContentSha);
  bindings.Branch("package_state",&packageState);bindings.Branch("campaign_state",&campaignState);
  bindings.Branch("campaign_descriptor_sha256",&campaignDescriptorSha);bindings.Branch("selected_members_sha256",&selectedMembersSha);
  bindings.Branch("source_members_sha256",&sourceMembersSha);bindings.Branch("analysis_config_sha256",&analysisSha);
  bindings.Branch("particle_registry_sha256",&particleSha);bindings.Branch("activity_definition_sha256",&activitySha);
  bindings.Branch("selection_definitions_sha256",&selectionSha);bindings.Branch("formula_source_sha256",&formulaSha);
  bindings.Branch("statistics_source_sha256",&statisticsSha);bindings.Branch("has_query_source_sha256",&hasQuerySha);
  bindings.Branch("query_source_sha256",&querySha);bindings.Branch("uncertainty_scope",&uncertaintyScope);
  bindings.Branch("input_root_sha256",&inputRootSha);bindings.Branch("input_root_bytes",&inputRootBytes);
  bindings.Branch("input_content_sha256",&inputContentSha);bindings.Branch("manifest_sha256",&manifestSha);
  bindings.Branch("source_fileset_sha256",&sourceFilesetSha);
  U point=0;Long64_t classId=0,trigger=0,associate=0,reference=0,bin=0;
  std::string semantic,pointKeySha,role,tune,referenceTune,profile,activity,quantity,component,axis,units,centerStatus,errorStatus,flow;
  Bool_t hasCenter=false,hasError=false,hasVariance=false,hasLow=false,hasHigh=false;Double_t center=0,error=0,variance=0,low=0,high=0;
  TTree points("points","Natural scientific point keys, independent value/error masks and statuses");
  points.Branch("index",&point);points.Branch("semantic_id",&semantic);points.Branch("point_key_sha256",&pointKeySha);points.Branch("role",&role);
  points.Branch("tune",&tune);points.Branch("reference_tune",&referenceTune);points.Branch("profile",&profile);
  points.Branch("activity",&activity);points.Branch("class_id",&classId);points.Branch("trigger_pdg",&trigger);
  points.Branch("associate_pdg",&associate);points.Branch("reference_pdg",&reference);points.Branch("quantity",&quantity);
  points.Branch("component",&component);points.Branch("axis",&axis);points.Branch("bin",&bin);
  points.Branch("low",&low);points.Branch("high",&high);points.Branch("has_center",&hasCenter);
  points.Branch("center",&center);points.Branch("center_status",&centerStatus);points.Branch("has_error",&hasError);
  points.Branch("error",&error);points.Branch("uncertainty_status",&errorStatus);points.Branch("has_variance",&hasVariance);
  points.Branch("variance",&variance);points.Branch("units",&units);
  points.Branch("flow",&flow);points.Branch("has_low",&hasLow);points.Branch("has_high",&hasHigh);
  U block=0,events=0,fills=0;Double_t sumw=0,sumw2=0,sumabsw=0;std::vector<std::string> components;std::vector<double> values;
  TTree blocks("block_values","Exactly aligned primitive values and exposure by point/tune/source block");
  blocks.Branch("point",&point);blocks.Branch("tune",&tune);blocks.Branch("block",&block);
  blocks.Branch("component_ids",&components);blocks.Branch("values",&values);blocks.Branch("events",&events);
  blocks.Branch("sumw",&sumw);blocks.Branch("sumw2",&sumw2);blocks.Branch("sumabsw",&sumabsw);blocks.Branch("fills",&fills);
  std::string group,covarianceStatus,representation,sourceFamilySha;Bool_t valid=false;Double_t complement=0,mean=0;
  U pointIndex=0,k=0;Long64_t dof=0;
  TTree covariancePoints("covariance_points","Covariance group slots mapped to global scientific points");
  covariancePoints.Branch("group",&group);covariancePoints.Branch("point",&point);
  covariancePoints.Branch("point_index",&pointIndex);covariancePoints.Branch("semantic_id",&semantic);
  covariancePoints.Branch("point_key_sha256",&pointKeySha);covariancePoints.Branch("valid",&valid);
  covariancePoints.Branch("units",&units);covariancePoints.Branch("status",&covarianceStatus);
  covariancePoints.Branch("representation",&representation);covariancePoints.Branch("K",&k);covariancePoints.Branch("dof",&dof);
  TTree factors("covariance_factors","C++ delete-one families, sufficient for every requested covariance");
  factors.Branch("group",&group);factors.Branch("point",&point);factors.Branch("tune",&tune);
  factors.Branch("source_family_sha256",&sourceFamilySha);
  factors.Branch("block",&block);factors.Branch("valid",&valid);factors.Branch("complement",&complement);factors.Branch("leave_mean",&mean);
  U row=0,column=0;TTree covarianceValues("covariance_values","Optional dense covariance values with explicit validity");
  covarianceValues.Branch("group",&group);covarianceValues.Branch("row",&row);covarianceValues.Branch("column",&column);
  covarianceValues.Branch("valid",&valid);covarianceValues.Branch("value",&complement);
  std::ifstream in(transport);std::string line;U next=0,pointNext=0;bool ended=false,bindingSeen=false,capabilitySeen=false;
  if(!std::getline(in,line)||line!="hadronization_typed_root_transport_v1")throw std::runtime_error("archive framing differs");
  while(std::getline(in,line)) {
    const auto f=Split(line);if(f.empty())throw std::runtime_error("empty archive record");
    if(f[0]=="N") {
      Need(f,6);id=std::stoull(f[1]);kind=f[2];text=Decode(f[3]);keys.clear();children.clear();
      if(id!=next++)throw std::runtime_error("node order differs");
      if(f[4]!="-")for(const auto& n:Split(f[4],',')){auto child=std::stoull(n);if(child>=id)throw std::runtime_error("cyclic/forward node reference");children.push_back(child);}
      if(f[5]!="-")for(const auto& k:Split(f[5],','))keys.push_back(Decode(k));
      if(kind=="O"&&keys.size()!=children.size())throw std::runtime_error("object key domain differs");
      nodes.Fill();
    } else if(f[0]=="V") {
      Need(f,3);if(capabilitySeen||f[1]!="SOURCE_FAMILY_SHA256"||f[2]!="1")throw std::runtime_error("archive capability record differs");capabilitySeen=true;
    } else if(f[0]=="H") {
      Need(f,24);if(bindingSeen)throw std::runtime_error("archive bindings repeated");bindingSeen=true;
      payloadSchema=Decode(f[1]);requestSha=Decode(f[2]);scientificRequestSha=Decode(f[3]);scienceContentSha=Decode(f[4]);
      packageState=Decode(f[5]);campaignState=Decode(f[6]);campaignDescriptorSha=Decode(f[7]);selectedMembersSha=Decode(f[8]);
      sourceMembersSha=Decode(f[9]);analysisSha=Decode(f[10]);particleSha=Decode(f[11]);activitySha=Decode(f[12]);selectionSha=Decode(f[13]);
      formulaSha=Decode(f[14]);statisticsSha=Decode(f[15]);hasQuerySha=Boolean(f[16]);querySha=Decode(f[17]);uncertaintyScope=Decode(f[18]);
      inputRootSha=Decode(f[19]);inputRootBytes=std::stoull(f[20]);inputContentSha=Decode(f[21]);manifestSha=Decode(f[22]);sourceFilesetSha=Decode(f[23]);bindings.Fill();
    } else if(f[0]=="M") {
      Need(f,3);if(g9Seen)throw std::runtime_error("G9 scientific metadata repeated");g9Seen=true;
      g9MetadataJson=Decode(f[1]);g9MetadataSha=Decode(f[2]);g9Science.Fill();
    } else if(f[0]=="P") {
      Need(f,31);point=std::stoull(f[1]);if(point!=pointNext++)throw std::runtime_error("point order differs");
      semantic=Decode(f[2]);pointKeySha=Decode(f[3]);role=Decode(f[4]);tune=Decode(f[5]);referenceTune=Decode(f[6]);profile=Decode(f[7]);activity=Decode(f[8]);
      classId=std::stoll(f[9]);trigger=std::stoll(f[10]);associate=std::stoll(f[11]);reference=std::stoll(f[12]);
      quantity=Decode(f[13]);component=Decode(f[14]);axis=Decode(f[15]);bin=std::stoll(f[16]);low=Number(f[17]);high=Number(f[18]);units=Decode(f[19]);
      hasCenter=Boolean(f[20]);center=Number(f[21]);centerStatus=Decode(f[22]);hasError=Boolean(f[23]);error=Number(f[24]);errorStatus=Decode(f[25]);hasVariance=Boolean(f[26]);variance=Number(f[27]);
      flow=Decode(f[28]);hasLow=Boolean(f[29]);hasHigh=Boolean(f[30]);points.Fill();
    } else if(f[0]=="B") {
      Need(f,11);point=std::stoull(f[1]);tune=Decode(f[2]);block=std::stoull(f[3]);components.clear();values.clear();
      if(f[4]!="-")for(const auto& x:Split(f[4],','))components.push_back(Decode(x));
      if(f[5]!="-")for(const auto& x:Split(f[5],','))values.push_back(Number(x));
      if(components.size()!=values.size())throw std::runtime_error("primitive components differ");
      events=std::stoull(f[6]);sumw=Number(f[7]);sumw2=Number(f[8]);sumabsw=Number(f[9]);fills=std::stoull(f[10]);blocks.Fill();
    } else if(f[0]=="G") {
      Need(f,12);group=Decode(f[1]);point=std::stoull(f[2]);pointIndex=std::stoull(f[3]);semantic=Decode(f[4]);pointKeySha=Decode(f[5]);
      valid=Boolean(f[6]);units=Decode(f[7]);covarianceStatus=Decode(f[8]);representation=Decode(f[9]);k=std::stoull(f[10]);dof=std::stoll(f[11]);covariancePoints.Fill();
    } else if(f[0]=="F") {
      Need(f,9);group=Decode(f[1]);point=std::stoull(f[2]);tune=Decode(f[3]);sourceFamilySha=Decode(f[4]);block=std::stoull(f[5]);valid=Boolean(f[6]);complement=Number(f[7]);mean=Number(f[8]);factors.Fill();
    } else if(f[0]=="C") {
      Need(f,6);group=Decode(f[1]);row=std::stoull(f[2]);column=std::stoull(f[3]);valid=Boolean(f[4]);complement=Number(f[5]);covarianceValues.Fill();
    } else if(f[0]=="ROOT") {Need(f,2);root=std::stoull(f[1]);if(root>=next)throw std::runtime_error("root node absent");}
    else if(f[0]=="END") {Need(f,1);ended=true;break;}
    else throw std::runtime_error("unknown archive record");
  }
  if(!ended||std::getline(in,line)||!bindingSeen||!capabilitySeen||
     (payloadSchema=="hadronization_projection_result_v3_g9_science")!=g9Seen)
    throw std::runtime_error("archive incomplete/trailing G9 scientific metadata");
  file.cd();nodes.Write();bindings.Write();points.Write();blocks.Write();covariancePoints.Write();factors.Write();covarianceValues.Write();
  if(g9Seen)g9Science.Write();
  TObjString(std::to_string(root).c_str()).Write("root_node");
  TObjString("hadronization_self_contained_typed_root_v1").Write("archive_schema");
  file.Close();
}

template<class T> void Bind(TTree& tree,const char* name,T* address) {
  if(tree.SetBranchAddress(name,address)<0)throw std::runtime_error("archive branch type/name differs");
}
void Dump(const std::string& path,const std::string& transport,bool scienceOnly=false) {
  TFile file(path.c_str(),"READ");if(file.IsZombie())throw std::runtime_error("archive unreadable");
  std::vector<std::string> names;TIter iter(file.GetListOfKeys());while(auto* object=iter()) {
    auto* key=dynamic_cast<TKey*>(object);if(!key||key->GetCycle()!=1)throw std::runtime_error("archive object cycle differs");names.push_back(key->GetName());
  }
  std::sort(names.begin(),names.end());
  const bool hasG9=std::find(names.begin(),names.end(),"g9_science")!=names.end();
  std::vector<std::string> expectedNames{"archive_bindings","archive_schema","block_values","covariance_factors","covariance_points","covariance_values","nodes","points","root_node"};
  if(hasG9){expectedNames.push_back("g9_science");std::sort(expectedNames.begin(),expectedNames.end());}
  if(names!=expectedNames)throw std::runtime_error("archive exact object set differs");
  auto* schema=dynamic_cast<TObjString*>(file.Get("archive_schema"));auto* root=dynamic_cast<TObjString*>(file.Get("root_node"));
  if(!schema||!root||schema->GetString()!="hadronization_self_contained_typed_root_v1")throw std::runtime_error("archive schema differs");
  std::ofstream out(transport);out<<(scienceOnly?"hadronization_typed_science_v1\n":"hadronization_typed_root_transport_v1\n");
  auto* factorCapability=dynamic_cast<TTree*>(file.Get("covariance_factors"));
  if(!factorCapability)throw std::runtime_error("archive covariance-factor tree absent");
  out<<"V\tSOURCE_FAMILY_SHA256\t"<<(factorCapability->GetBranch("source_family_sha256")?1:0)<<'\n';
  const std::map<std::string,std::vector<std::string>> branches={
    {"nodes",{"id","kind","text","children","keys"}},
    {"archive_bindings",{"schema","request_sha256","scientific_request_sha256","science_content_sha256","package_state","campaign_state","campaign_descriptor_sha256","selected_members_sha256","source_members_sha256","analysis_config_sha256","particle_registry_sha256","activity_definition_sha256","selection_definitions_sha256","formula_source_sha256","statistics_source_sha256","has_query_source_sha256","query_source_sha256","uncertainty_scope","input_root_sha256","input_root_bytes","input_content_sha256","manifest_sha256","source_fileset_sha256"}},
    {"g9_science",{"metadata_json","metadata_sha256"}},
    {"points",{"index","semantic_id","point_key_sha256","role","tune","reference_tune","profile","activity","class_id","trigger_pdg","associate_pdg","reference_pdg","quantity","component","axis","bin","low","high","units","has_center","center","center_status","has_error","error","uncertainty_status","has_variance","variance","flow","has_low","has_high"}},
    {"block_values",{"point","tune","block","component_ids","values","events","sumw","sumw2","sumabsw","fills"}},
    {"covariance_points",{"group","point","point_index","semantic_id","point_key_sha256","valid","units","status","representation","K","dof"}},
    {"covariance_factors",{"group","point","tune","source_family_sha256","block","valid","complement","leave_mean"}},
    {"covariance_values",{"group","row","column","valid","value"}}};
  auto tree=[&](const char* name)->TTree&{
    auto* t=dynamic_cast<TTree*>(file.Get(name));if(!t)throw std::runtime_error("archive tree absent");
    std::vector<std::string> actual;TIter branch(t->GetListOfBranches());while(auto* b=branch())actual.push_back(b->GetName());
    auto expected=branches.at(name);std::sort(actual.begin(),actual.end());std::sort(expected.begin(),expected.end());
    if(name==std::string("covariance_factors")) {
      auto legacy=expected;legacy.erase(std::find(legacy.begin(),legacy.end(),"source_family_sha256"));
      if(actual!=expected&&actual!=legacy)throw std::runtime_error("archive exact branch set differs");
    } else if(actual!=expected)throw std::runtime_error("archive exact branch set differs");
    return *t;};
  U id=0;std::string *kind=nullptr,*text=nullptr;std::vector<U>* children=nullptr;std::vector<std::string>* keys=nullptr;
  auto& nodes=tree("nodes");Bind(nodes,"id",&id);Bind(nodes,"kind",&kind);Bind(nodes,"text",&text);Bind(nodes,"children",&children);Bind(nodes,"keys",&keys);
  if(!scienceOnly)for(Long64_t i=0;i<nodes.GetEntries();++i){nodes.GetEntry(i);out<<"N\t"<<id<<'\t'<<*kind<<'\t'<<Encode(*text)<<'\t';if(children->empty())out<<'-';else for(std::size_t j=0;j<children->size();++j)out<<(j?",":"")<<children->at(j);out<<'\t';if(keys->empty())out<<'-';else for(std::size_t j=0;j<keys->size();++j)out<<(j?",":"")<<Encode(keys->at(j));out<<'\n';}
  std::string *payloadSchema=nullptr,*requestSha=nullptr,*scientificRequestSha=nullptr,*scienceContentSha=nullptr,*packageState=nullptr,*campaignState=nullptr,
    *campaignDescriptorSha=nullptr,*selectedMembersSha=nullptr,*sourceMembersSha=nullptr,*analysisSha=nullptr,*particleSha=nullptr,*activitySha=nullptr,
    *selectionSha=nullptr,*formulaSha=nullptr,*statisticsSha=nullptr,*querySha=nullptr,*uncertaintyScope=nullptr,*inputRootSha=nullptr,*inputContentSha=nullptr,
    *manifestSha=nullptr,*sourceFilesetSha=nullptr;
  Bool_t hasQuerySha=false;U inputRootBytes=0;auto& bindings=tree("archive_bindings");
  Bind(bindings,"schema",&payloadSchema);Bind(bindings,"request_sha256",&requestSha);Bind(bindings,"scientific_request_sha256",&scientificRequestSha);
  Bind(bindings,"science_content_sha256",&scienceContentSha);Bind(bindings,"package_state",&packageState);Bind(bindings,"campaign_state",&campaignState);
  Bind(bindings,"campaign_descriptor_sha256",&campaignDescriptorSha);Bind(bindings,"selected_members_sha256",&selectedMembersSha);
  Bind(bindings,"source_members_sha256",&sourceMembersSha);Bind(bindings,"analysis_config_sha256",&analysisSha);
  Bind(bindings,"particle_registry_sha256",&particleSha);Bind(bindings,"activity_definition_sha256",&activitySha);
  Bind(bindings,"selection_definitions_sha256",&selectionSha);Bind(bindings,"formula_source_sha256",&formulaSha);
  Bind(bindings,"statistics_source_sha256",&statisticsSha);Bind(bindings,"has_query_source_sha256",&hasQuerySha);Bind(bindings,"query_source_sha256",&querySha);
  Bind(bindings,"uncertainty_scope",&uncertaintyScope);Bind(bindings,"input_root_sha256",&inputRootSha);Bind(bindings,"input_root_bytes",&inputRootBytes);
  Bind(bindings,"input_content_sha256",&inputContentSha);Bind(bindings,"manifest_sha256",&manifestSha);Bind(bindings,"source_fileset_sha256",&sourceFilesetSha);
  if(bindings.GetEntries()!=1||bindings.GetEntry(0)<=0)throw std::runtime_error("archive binding row differs");
  out<<"H";for(auto* s:{payloadSchema,requestSha,scientificRequestSha,scienceContentSha,packageState,campaignState,campaignDescriptorSha,selectedMembersSha,
      sourceMembersSha,analysisSha,particleSha,activitySha,selectionSha,formulaSha,statisticsSha})out<<'\t'<<Encode(*s);
  out<<'\t'<<int(hasQuerySha)<<'\t'<<Encode(*querySha)<<'\t'<<Encode(*uncertaintyScope)<<'\t'<<Encode(*inputRootSha)<<'\t'<<inputRootBytes
     <<'\t'<<Encode(*inputContentSha)<<'\t'<<Encode(*manifestSha)<<'\t'<<Encode(*sourceFilesetSha)<<'\n';
  if(hasG9!=( *payloadSchema=="hadronization_projection_result_v3_g9_science"))
    throw std::runtime_error("G9 scientific metadata/schema capability differs");
  U point=0;Long64_t classId=0,trigger=0,associate=0,reference=0,bin=0;
  std::string *semantic=nullptr,*pointKeySha=nullptr,*role=nullptr,*tune=nullptr,*referenceTune=nullptr,*profile=nullptr,*activity=nullptr,*quantity=nullptr,*component=nullptr,*axis=nullptr,*units=nullptr,*centerStatus=nullptr,*errorStatus=nullptr,*flow=nullptr;
  Bool_t hasCenter=false,hasError=false,hasVariance=false,hasLow=false,hasHigh=false;Double_t center=0,error=0,variance=0,low=0,high=0;
  auto& points=tree("points");Bind(points,"index",&point);Bind(points,"semantic_id",&semantic);Bind(points,"point_key_sha256",&pointKeySha);Bind(points,"role",&role);Bind(points,"tune",&tune);Bind(points,"reference_tune",&referenceTune);Bind(points,"profile",&profile);Bind(points,"activity",&activity);Bind(points,"class_id",&classId);Bind(points,"trigger_pdg",&trigger);Bind(points,"associate_pdg",&associate);Bind(points,"reference_pdg",&reference);Bind(points,"quantity",&quantity);Bind(points,"component",&component);Bind(points,"axis",&axis);Bind(points,"bin",&bin);Bind(points,"low",&low);Bind(points,"high",&high);Bind(points,"units",&units);Bind(points,"has_center",&hasCenter);Bind(points,"center",&center);Bind(points,"center_status",&centerStatus);Bind(points,"has_error",&hasError);Bind(points,"error",&error);Bind(points,"uncertainty_status",&errorStatus);Bind(points,"has_variance",&hasVariance);Bind(points,"variance",&variance);Bind(points,"flow",&flow);Bind(points,"has_low",&hasLow);Bind(points,"has_high",&hasHigh);
  for(Long64_t i=0;i<points.GetEntries();++i){points.GetEntry(i);out<<"P\t"<<point;for(auto* s:{semantic,pointKeySha,role,tune,referenceTune,profile,activity})out<<'\t'<<Encode(*s);out<<'\t'<<classId<<'\t'<<trigger<<'\t'<<associate<<'\t'<<reference;for(auto* s:{quantity,component,axis})out<<'\t'<<Encode(*s);out<<'\t'<<bin<<'\t'<<Hex(low)<<'\t'<<Hex(high)<<'\t'<<Encode(*units)<<'\t'<<int(hasCenter)<<'\t'<<Hex(center)<<'\t'<<Encode(*centerStatus)<<'\t'<<int(hasError)<<'\t'<<Hex(error)<<'\t'<<Encode(*errorStatus)<<'\t'<<int(hasVariance)<<'\t'<<Hex(variance)<<'\t'<<Encode(*flow)<<'\t'<<int(hasLow)<<'\t'<<int(hasHigh)<<'\n';}
  U block=0,events=0,fills=0;Double_t sumw=0,sumw2=0,sumabsw=0;std::vector<std::string>* components=nullptr;std::vector<double>* values=nullptr;
  auto& blocks=tree("block_values");Bind(blocks,"point",&point);Bind(blocks,"tune",&tune);Bind(blocks,"block",&block);Bind(blocks,"component_ids",&components);Bind(blocks,"values",&values);Bind(blocks,"events",&events);Bind(blocks,"sumw",&sumw);Bind(blocks,"sumw2",&sumw2);Bind(blocks,"sumabsw",&sumabsw);Bind(blocks,"fills",&fills);
  for(Long64_t i=0;i<blocks.GetEntries();++i){blocks.GetEntry(i);out<<"B\t"<<point<<'\t'<<Encode(*tune)<<'\t'<<block<<'\t';if(components->empty())out<<'-';else for(std::size_t j=0;j<components->size();++j)out<<(j?",":"")<<Encode(components->at(j));out<<'\t';if(values->empty())out<<'-';else for(std::size_t j=0;j<values->size();++j)out<<(j?",":"")<<Hex(values->at(j));out<<'\t'<<events<<'\t'<<Hex(sumw)<<'\t'<<Hex(sumw2)<<'\t'<<Hex(sumabsw)<<'\t'<<fills<<'\n';}
  std::string *group=nullptr,*covarianceStatus=nullptr,*representation=nullptr;Bool_t valid=false;U pointIndex=0,k=0;Long64_t dof=0;
  auto& covariancePoints=tree("covariance_points");Bind(covariancePoints,"group",&group);Bind(covariancePoints,"point",&point);
  Bind(covariancePoints,"point_index",&pointIndex);Bind(covariancePoints,"semantic_id",&semantic);Bind(covariancePoints,"point_key_sha256",&pointKeySha);
  Bind(covariancePoints,"valid",&valid);Bind(covariancePoints,"units",&units);Bind(covariancePoints,"status",&covarianceStatus);
  Bind(covariancePoints,"representation",&representation);Bind(covariancePoints,"K",&k);Bind(covariancePoints,"dof",&dof);
  for(Long64_t i=0;i<covariancePoints.GetEntries();++i){covariancePoints.GetEntry(i);out<<"G\t"<<Encode(*group)<<'\t'<<point<<'\t'<<pointIndex
    <<'\t'<<Encode(*semantic)<<'\t'<<Encode(*pointKeySha)<<'\t'<<int(valid)<<'\t'<<Encode(*units)<<'\t'<<Encode(*covarianceStatus)
    <<'\t'<<Encode(*representation)<<'\t'<<k<<'\t'<<dof<<'\n';}
  if(hasG9){
    std::string *json=nullptr,*sha=nullptr;auto& metadata=tree("g9_science");
    Bind(metadata,"metadata_json",&json);Bind(metadata,"metadata_sha256",&sha);
    if(metadata.GetEntries()!=1||metadata.GetEntry(0)<=0)
      throw std::runtime_error("G9 scientific metadata row differs");
    out<<"M\t"<<Encode(*json)<<'\t'<<Encode(*sha)<<'\n';
  }
  Double_t complement=0,mean=0;std::string sourceFamilyShaValue;std::string* sourceFamilySha=&sourceFamilyShaValue;
  auto& factors=tree("covariance_factors");Bind(factors,"group",&group);Bind(factors,"point",&point);Bind(factors,"tune",&tune);
  const bool hasSourceFamilySha=factors.GetBranch("source_family_sha256")!=nullptr;
  if(hasSourceFamilySha)Bind(factors,"source_family_sha256",&sourceFamilySha);
  Bind(factors,"block",&block);Bind(factors,"valid",&valid);Bind(factors,"complement",&complement);Bind(factors,"leave_mean",&mean);
  for(Long64_t i=0;i<factors.GetEntries();++i){if(!hasSourceFamilySha)sourceFamilyShaValue.clear();factors.GetEntry(i);out<<"F\t"<<Encode(*group)<<'\t'<<point<<'\t'<<Encode(*tune)<<'\t'<<Encode(*sourceFamilySha)<<'\t'<<block<<'\t'<<int(valid)<<'\t'<<Hex(complement)<<'\t'<<Hex(mean)<<'\n';}
  U row=0,column=0;auto& covarianceValues=tree("covariance_values");Bind(covarianceValues,"group",&group);Bind(covarianceValues,"row",&row);
  Bind(covarianceValues,"column",&column);Bind(covarianceValues,"valid",&valid);Bind(covarianceValues,"value",&complement);
  for(Long64_t i=0;i<covarianceValues.GetEntries();++i){covarianceValues.GetEntry(i);out<<"C\t"<<Encode(*group)<<'\t'<<row<<'\t'<<column
    <<'\t'<<int(valid)<<'\t'<<Hex(complement)<<'\n';}
  if(!scienceOnly)out<<"ROOT\t"<<root->GetString()<<'\n';
  out<<"END\n";
}
}
int main(int argc,char** argv) {
  try {if(argc!=4)throw std::runtime_error("usage: archive pack|dump|science input output");
    if(std::string(argv[1])=="pack")Pack(argv[2],argv[3]);
    else if(std::string(argv[1])=="dump")Dump(argv[2],argv[3]);
    else if(std::string(argv[1])=="science")Dump(argv[2],argv[3],true);
    else throw std::runtime_error("unknown archive command");
  }catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}
}
