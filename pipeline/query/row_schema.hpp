#ifndef HADRONIZATION_QUERY_ROW_SCHEMA_HPP
#define HADRONIZATION_QUERY_ROW_SCHEMA_HPP
#include <map>
#include <string>
namespace HadronizationQuery {
inline const std::map<std::string, std::string>& ExpectedSchemas() {
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

}  // namespace HadronizationQuery
#endif
