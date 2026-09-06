import hashlib
import json
import math
import os
from pathlib import Path
import shlex
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest

from helpers import ROOT, sha256
from test_submission import FIXTURE, declared_array


TABLES = (
    "ancestry", "ancestry_mothers", "closure", "constituents",
    "event_compatibility", "event_ranges", "events", "hard", "heavy",
    "heavy_mothers", "origins", "pairs", "source_blocks", "source_counts",
    "sources", "triggers",
)

EXPECTED_SCHEMA = {
    "ancestry": "event_id:ULong64_t,node_index:Int_t,pdg:Int_t,status:Int_t,mother1:Int_t,mother2:Int_t",
    "ancestry_mothers": "event_id:ULong64_t,node_index:Int_t,edge_ordinal:UInt_t,mother_index:Int_t",
    "closure": "event_id:ULong64_t,trigger_heavy_index:Int_t,associate_heavy_index:Int_t,coefficient:Int_t,visible:UChar_t,dense_category:Int_t",
    "constituents": "event_id:ULong64_t,heavy_index:Int_t,signed_flavour:Int_t,constituent_ordinal:UInt_t,origin:Int_t,resolution:Int_t,matched_hard:Int_t,rejected_hard:Int_t,depth:Int_t",
    "event_compatibility": "event_id:ULong64_t,diagnostic_id:UInt_t,cell_id:UInt_t,value:Int_t",
    "event_ranges": "first_id:ULong64_t,count:ULong64_t,source_id:UInt_t",
    "events": "event_id:ULong64_t,weight:Double_t,a15_eta1:Int_t,a15_eta4:Int_t,process_code:Int_t,pthat:Double_t,hard_scale:Double_t,n_mpi:Int_t",
    "hard": "event_id:ULong64_t,root_index:Int_t,bottom_index:Int_t,pdg:Int_t,status:Int_t,bottom_pdg:Int_t,bottom_status:Int_t,px:Double_t,py:Double_t,pz:Double_t,energy:Double_t",
    "heavy": "event_id:ULong64_t,heavy_index:Int_t,pdg:Int_t,status:Int_t,final:UChar_t,selected:UChar_t,pair_eligible:UChar_t,category:Int_t,is_meson:UChar_t,is_baryon:UChar_t,spin:Int_t,charge3:Int_t,nc:Int_t,ncbar:Int_t,nb:Int_t,nbbar:Int_t,qc:Int_t,qb:Int_t,baryon3:Int_t,strangeness:Int_t,open:UChar_t,hidden:UChar_t,mother1:Int_t,mother2:Int_t,daughter1:Int_t,daughter2:Int_t,px:Double_t,py:Double_t,pz:Double_t,energy:Double_t,mass:Double_t,pt:Double_t,eta:Double_t,rapidity:Double_t,phi:Double_t",
    "heavy_mothers": "event_id:ULong64_t,heavy_index:Int_t,edge_ordinal:UInt_t,mother_index:Int_t",
    "origins": "event_id:ULong64_t,heavy_index:Int_t,sector:Int_t,origin:Int_t,resolution:Int_t,matched_hard:Int_t,rejected_hard:Int_t,depth:Int_t",
    "pairs": "event_id:ULong64_t,trigger_heavy_index:Int_t,associate_heavy_index:Int_t,sign:Int_t,dphi:Double_t,deta:Double_t,trigger_pt:Double_t,associate_pt:Double_t,a15_eta1:Int_t,a15_eta4:Int_t,associate_origin:Int_t,associate_category:Int_t,weight:Double_t",
    "source_blocks": "source_id:UInt_t,assignment_id:UInt_t,block:UInt_t",
    "source_counts": "source_id:UInt_t,family_id:UInt_t,rows:ULong64_t",
    "sources": "source_id:UInt_t,tune:UInt_t,logical_id:ULong64_t,attempt:UInt_t,events:ULong64_t,attempted_events:ULong64_t,sumw:Double_t,sumw2:Double_t,sumabsw:Double_t",
    "triggers": "event_id:ULong64_t,heavy_index:Int_t,sector:Int_t,rejection_mask:UInt_t",
}

CANDIDATE_FIXTURE_DIGEST = "ffc1a0aeb1a86872238f53c7cfebad2eaa70dc5fd6b8c1a1472bcbca250de334"
CANDIDATE_FIXTURE_ROWS = {
    "ancestry": 36, "ancestry_mothers": 0, "closure": 62,
    "constituents": 48, "event_compatibility": 34, "event_ranges": 2,
    "events": 6, "hard": 12, "heavy": 42, "heavy_mothers": 36,
    "origins": 84, "pairs": 38, "source_blocks": 2, "source_counts": 32,
    "sources": 2, "triggers": 10,
}


ORACLE = r'''
#include "TBranch.h"
#include "TFile.h"
#include "TKey.h"
#include "TLeaf.h"
#include "TObjString.h"
#include "TTree.h"
#include <iomanip>
#include <iostream>
#include <locale>
#include <string>

int main(int argc,char**argv){
  if(argc!=2)return 2;TFile file(argv[1],"READ");if(file.IsZombie())return 3;
  std::cout<<"COMP\t"<<file.GetCompressionAlgorithm()<<'\t'<<file.GetCompressionLevel()<<'\n';
  TIter keys(file.GetListOfKeys());while(auto*object=keys()){auto*key=dynamic_cast<TKey*>(object);std::cout<<"KEY\t"<<key->GetName()<<'\t'<<key->GetClassName()<<'\t'<<key->GetCycle()<<'\n';}
  const char* names[]={"ancestry","ancestry_mothers","closure","constituents","event_compatibility","event_ranges","events","hard","heavy","heavy_mothers","origins","pairs","source_blocks","source_counts","sources","triggers"};
  for(const char*name:names){auto*tree=dynamic_cast<TTree*>(file.Get(name));if(!tree)return 4;std::cout<<"SCHEMA\t"<<name<<'\t';TIter branches(tree->GetListOfBranches());bool first=true;while(auto*object=branches()){auto*branch=dynamic_cast<TBranch*>(object);auto*leaf=branch->GetLeaf(branch->GetName());if(!leaf)return 5;if(!first)std::cout<<',';first=false;std::cout<<branch->GetName()<<':'<<leaf->GetTypeName();}std::cout<<'\n';
    for(Long64_t row=0;row<tree->GetEntries();++row){if(tree->GetEntry(row)<=0)return 6;std::cout<<"ROW\t"<<name;TIter values(tree->GetListOfBranches());while(auto*object=values()){auto*branch=dynamic_cast<TBranch*>(object);auto*leaf=branch->GetLeaf(branch->GetName());const std::string type=leaf->GetTypeName();std::cout<<'\t';if(type=="Double_t"){std::cout.imbue(std::locale::classic());std::cout<<std::hexfloat<<std::setprecision(13)<<leaf->GetValue()<<std::defaultfloat;}else if(type=="ULong64_t")std::cout<<static_cast<unsigned long long>(leaf->GetValueLong64());else if(type=="UInt_t")std::cout<<static_cast<unsigned int>(leaf->GetValueLong64());else if(type=="UChar_t")std::cout<<static_cast<unsigned int>(leaf->GetValueLong64());else std::cout<<leaf->GetValueLong64();}std::cout<<'\n';}}
  auto*contract=dynamic_cast<TObjString*>(file.Get("contract"));if(!contract)return 7;std::cout<<"CONTRACT\t"<<contract->GetString().Data()<<'\n';return 0;
}
'''


MUTATOR = r'''
#include "TFile.h"
#include "TObjString.h"
#include "TTree.h"
#include <string>

int main(int argc,char**argv){
  if(argc!=4)return 2;
  const std::string mode=argv[3];
  TFile input(argv[1],"READ");if(input.IsZombie())return 3;TFile output(argv[2],"RECREATE");output.SetCompressionAlgorithm(input.GetCompressionAlgorithm());output.SetCompressionLevel(input.GetCompressionLevel());
  const char* names[]={"ancestry","ancestry_mothers","closure","constituents","event_compatibility","event_ranges","events","hard","heavy","heavy_mothers","origins","pairs","source_blocks","source_counts","sources","triggers"};
  for(const char*name:names){auto*source=dynamic_cast<TTree*>(input.Get(name));if(!source)return 4;output.cd();TTree*copy=nullptr;
    if(mode=="missing_field"&&std::string(name)=="events"){source->SetBranchStatus("n_mpi",0);copy=source->CloneTree(-1,"fast");source->SetBranchStatus("*",1);}
    else if(mode=="drop_row"&&std::string(name)=="triggers")copy=source->CloneTree(source->GetEntries()-1,"fast");
    else if((mode=="duplicate_key"||mode=="invalid_domain"||mode=="shuffled_rows")&&std::string(name)=="triggers"){ULong64_t event=0;Int_t heavy=0,sector=0;UInt_t mask=0;source->SetBranchAddress("event_id",&event);source->SetBranchAddress("heavy_index",&heavy);source->SetBranchAddress("sector",&sector);source->SetBranchAddress("rejection_mask",&mask);copy=source->CloneTree(0);for(Long64_t i=0;i<source->GetEntries();++i){source->GetEntry(mode=="shuffled_rows"?source->GetEntries()-1-i:i);if(mode=="invalid_domain"&&i==0)mask=16;copy->Fill();}if(mode=="duplicate_key"){source->GetEntry(source->GetEntries()-1);copy->Fill();}source->ResetBranchAddresses();}
    else if((mode=="broken_join"||mode=="wrong_cache")&&std::string(name)=="pairs"){Int_t associate=0;Double_t triggerPt=0;source->SetBranchAddress("associate_heavy_index",&associate);source->SetBranchAddress("trigger_pt",&triggerPt);copy=source->CloneTree(0);for(Long64_t i=0;i<source->GetEntries();++i){source->GetEntry(i);if(i==0&&mode=="broken_join")associate=999999;if(i==0&&mode=="wrong_cache")triggerPt+=1.0;copy->Fill();}source->ResetBranchAddresses();}
    else if(mode=="wrong_source_block"&&std::string(name)=="source_blocks"){UInt_t block=0;source->SetBranchAddress("block",&block);copy=source->CloneTree(0);for(Long64_t i=0;i<source->GetEntries();++i){source->GetEntry(i);if(i==0)++block;copy->Fill();}source->ResetBranchAddresses();}
    else if(mode=="missing_source"&&std::string(name)=="sources")copy=source->CloneTree(source->GetEntries()-1,"fast");
    else if(mode=="missing_event"&&std::string(name)=="events")copy=source->CloneTree(source->GetEntries()-1,"fast");
    else if(mode=="broken_count"&&std::string(name)=="source_counts"){ULong64_t rows=0;source->SetBranchAddress("rows",&rows);copy=source->CloneTree(0);for(Long64_t i=0;i<source->GetEntries();++i){source->GetEntry(i);if(i==0)++rows;copy->Fill();}source->ResetBranchAddresses();}
    else copy=source->CloneTree(-1,"fast");
    copy->SetName(name);copy->Write();if(mode=="duplicate_cycle"&&std::string(name)=="triggers")copy->Write();delete copy;}
  auto*contract=dynamic_cast<TObjString*>(input.Get("contract"));if(!contract)return 5;std::string contractText=contract->GetString().Data();
  auto mutateDigest=[&](const std::string&prefix){const auto at=contractText.find(prefix);if(at==std::string::npos)return false;const auto value=at+prefix.size();contractText[value]=contractText[value]=='a'?'b':'a';return true;};
  if(mode=="contract_map"&&!mutateDigest("\"map_digest\":\""))return 8;
  if(mode=="dictionary_reference"&&!mutateDigest("\"effective_settings_identity\":\""))return 9;
  if(mode=="dictionary_payload"){const std::string prefix="\"canonical\":\"";const auto at=contractText.find(prefix);if(at==std::string::npos)return 10;contractText.insert(at+prefix.size(),"X");}
  if(mode=="source_reference"){const std::string prefix="\"manifest_row\":{\"accepted_attempt\":";const auto start=contractText.find(prefix);if(start==std::string::npos)return 11;const auto at=contractText.find("\"block\":",start);if(at==std::string::npos)return 12;const auto value=at+8;contractText[value]=contractText[value]=='1'?'2':'1';}
  output.cd();TObjString contractCopy(contractText.c_str());contractCopy.Write("contract");if(mode=="unknown_object"){TObjString extra("not allowed");extra.Write("extra");}output.Close();return 0;
}
'''


def fixture_source():
    validator = (ROOT / "pipeline/generate/validate_raw.cpp").read_text(encoding="utf-8")
    replacements = {
        "@INT_VECTORS@": declared_array(validator, "integerVectors"),
        "@DOUBLE_VECTORS@": (declared_array(validator, "doubleVectors") +
                              declared_array(validator, "finalDoubleVector") +
                              declared_array(validator, "hardDoubleVectors")),
        "@METADATA_STRINGS@": declared_array(validator, "metadataStrings"),
        "@METADATA_INTS@": declared_array(validator, "metadataInts"),
        "@METADATA_UNSIGNED@": declared_array(validator, "metadataUnsigned"),
        "@METADATA_LONG@": declared_array(validator, "metadataLong"),
        "@METADATA_DOUBLE@": declared_array(validator, "metadataDouble"),
    }
    source = FIXTURE
    for token, values in replacements.items():
        source = source.replace(token, ", ".join(json.dumps(value) for value in values))
    factorization = {
        'if (argc != 3 && argc != 4) return 2;':
            'if (argc < 3 || argc > 8) return 2;',
        'const double mutation = argc == 4 ? std::stod(argv[3]) : 0.0;':
            'const double mutation = 0.0;\n'
            '  const int fixtureLogical = argc >= 4 ? std::stoi(argv[3]) : 0;\n'
            '  const int fixtureAttempt = argc >= 5 ? std::stoi(argv[4]) : 0;\n'
            '  const std::string fixtureTune = argc >= 6 ? argv[5] : "MONASH";\n'
            '  const int fixtureTuneOrdinal = argc >= 7 ? std::stoi(argv[6]) : 0;\n'
            '  const int fixtureCampaignOrdinal = argc >= 8 ? std::stoi(argv[7]) : 3;\n'
            '  const int fixtureSeed = 100000001 + fixtureCampaignOrdinal * 10000000 +\n'
            '      fixtureTuneOrdinal * 1000000 + fixtureAttempt * 100000 + fixtureLogical;',
        'EventId(3, 0, 0, 0, static_cast<std::uint64_t>(row))':
            'EventId(fixtureCampaignOrdinal, fixtureTuneOrdinal, fixtureLogical, '
            'fixtureAttempt, static_cast<std::uint64_t>(row))',
        'settingValues["Random:seed"] = "130000001";':
            'settingValues["Random:seed"] = std::to_string(fixtureSeed);',
        'mi["campaign_ordinal"] = 3; mi["logical_id"] = 0; mi["attempt"] = 0;':
            'mi["campaign_ordinal"] = fixtureCampaignOrdinal; '
            'mi["logical_id"] = fixtureLogical; mi["attempt"] = fixtureAttempt;',
        'mi["seed"] = 130000001; mi["complete"] = 1;':
            'mi["seed"] = fixtureSeed; mi["complete"] = 1;',
        'ms["tune"] = mode == "identity" ? "JUNCTIONS" : "MONASH";':
            'ms["tune"] = mode == "identity" ? "JUNCTIONS" : fixtureTune;',
    }
    for old_text, new_text in factorization.items():
        if source.count(old_text) != 1:
            raise AssertionError("fixture factorization transform changed")
        source = source.replace(old_text, new_text)
    alias_marker = '    legacyMultiplicity = row;'
    if source.count(alias_marker) != 1:
        raise AssertionError("fixture legacy-alias insertion point changed")
    source = source.replace(
        alias_marker,
        alias_marker + '\n    if (mode == "legacy_alias" && row == 0) ++legacyMultiplicity;')
    old = '''std::vector<int> heavyPdgs = beautyEvent
        ? std::vector<int>{511, -511}
        : std::vector<int>{421, -421};'''
    new = '''std::vector<int> heavyPdgs = beautyEvent
        ? std::vector<int>{511, 5212}
        : (row == 2 ? std::vector<int>{411, -411}
                    : std::vector<int>{421, -421, 431, -431, 4112, -4112,
                                       4212, -4212, 4222, -4222, 413, -413,
                                       10411, -10411, 4422, -4422, 443});'''
    if source.count(old) != 1:
        raise AssertionError("fixture heavy-state insertion point changed")
    source = source.replace(old, new)
    replacements = {
        'const bool isMesonValue = state ? state->kind == "meson" : false;':
            'const bool isMesonValue = state ? state->kind == "meson" : '
            '(std::abs(heavyPdg) == 443 || std::abs(heavyPdg) == 413 || '
            'std::abs(heavyPdg) == 10411);',
        'const bool isBaryonValue = state ? state->kind == "baryon" : true;':
            'const bool isBaryonValue = !isMesonValue;',
        'const int spinTypeValue = state ? state->spin2j1 : 2;':
            'const int spinTypeValue = state ? state->spin2j1 : '
            '((std::abs(heavyPdg) == 443 || std::abs(heavyPdg) == 413) ? 3 : '
            '(std::abs(heavyPdg) == 10411 ? 1 : 2));',
        '(std::abs(heavyPdg) == 4422 ? (heavyPdg > 0 ? 6 : -6) : 0);':
            '((std::abs(heavyPdg) == 4422) ? (heavyPdg > 0 ? 6 : -6) : '
            '((std::abs(heavyPdg) == 413 || std::abs(heavyPdg) == 10411) ? '
            '(heavyPdg > 0 ? 3 : -3) : 0));',
        'integerVectors["MOTHER"].push_back(hardIndex);':
            'integerVectors["MOTHER"].push_back(lineageIndex);',
        'integerVectors["MOTHERID"].push_back(signedFlavour);':
            'integerVectors["MOTHERID"].push_back(lineageIndex > 0 ? signedFlavour : 0);',
        'integerVectors["heavyMother1"].push_back(hardIndex);':
            'integerVectors["heavyMother1"].push_back(lineageIndex);',
        'integerVectors["heavyMother2"].push_back(0);':
            'integerVectors["heavyMother2"].push_back(secondLineageIndex);',
        'integerVectors["heavyMothers"].push_back(hardIndex);\n        integerVectors["heavyMotherOffsets"].push_back(\n            static_cast<int>(integerVectors["heavyMothers"].size()));':
            'if (lineageIndex > 0) integerVectors["heavyMothers"].push_back(lineageIndex);\n'
            '        if (secondLineageIndex > 0) integerVectors["heavyMothers"].push_back(secondLineageIndex);\n'
            '        integerVectors["heavyMotherOffsets"].push_back(\n'
            '            static_cast<int>(integerVectors["heavyMothers"].size()));',
        'integerVectors["heavyOriginC"].push_back(content.qc() == 0 ? 0 : 1);':
            'integerVectors["heavyOriginC"].push_back(content.qc() == 0 ? 0 : originCode);',
        'integerVectors["heavyOriginB"].push_back(content.qb() == 0 ? 0 : 1);':
            'integerVectors["heavyOriginB"].push_back(content.qb() == 0 ? 0 : originCode);',
        'integerVectors["heavyMatchResolutionC"].push_back(content.qc() == 0 ? 0 : 1);':
            'integerVectors["heavyMatchResolutionC"].push_back(content.qc() == 0 ? 0 : resolutionCode);',
        'integerVectors["heavyMatchResolutionB"].push_back(content.qb() == 0 ? 0 : 1);':
            'integerVectors["heavyMatchResolutionB"].push_back(content.qb() == 0 ? 0 : resolutionCode);',
        'integerVectors["heavyMatchedHardC"].push_back(content.qc() == 0 ? -1 : hardIndex);':
            'integerVectors["heavyMatchedHardC"].push_back(content.qc() == 0 ? -1 : matchedIndex);',
        'integerVectors["heavyMatchedHardB"].push_back(content.qb() == 0 ? -1 : hardIndex);':
            'integerVectors["heavyMatchedHardB"].push_back(content.qb() == 0 ? -1 : matchedIndex);',
        'integerVectors["heavyOriginDepthC"].push_back(content.qc() == 0 ? -1 : 1);':
            'integerVectors["heavyOriginDepthC"].push_back(content.qc() == 0 ? -1 : depthValue);',
        'integerVectors["heavyOriginDepthB"].push_back(content.qb() == 0 ? -1 : 1);':
            'integerVectors["heavyOriginDepthB"].push_back(content.qb() == 0 ? -1 : depthValue);',
        'integerVectors["heavyConstituentOrigin"].push_back(1);':
            'integerVectors["heavyConstituentOrigin"].push_back(originCode);',
        'integerVectors["heavyConstituentMatchResolution"].push_back(1);':
            'integerVectors["heavyConstituentMatchResolution"].push_back(resolutionCode);',
        'integerVectors["heavyConstituentMatchedHard"].push_back(hardIndex);':
            'integerVectors["heavyConstituentMatchedHard"].push_back(matchedIndex);',
        'integerVectors["heavyConstituentOriginDepth"].push_back(1);':
            'integerVectors["heavyConstituentOriginDepth"].push_back(depthValue);',
        'for (const int extra : {-5522, -4422, 443, 4422, 5522})':
            'for (const int extra : {-10411, -5522, -4422, -413, 413, 443, 4422, 5522, 10411})',
        'isMeson = state ? (state->kind == "meson" ? 1 : 0) : (pdg == 443 ? 1 : 0);':
            'isMeson = state ? (state->kind == "meson" ? 1 : 0) : '
            '((std::abs(pdg) == 443 || std::abs(pdg) == 413 || '
            'std::abs(pdg) == 10411) ? 1 : 0);',
        'spinType = state ? state->spin2j1 : (pdg == 443 ? 3 : 2);':
            'spinType = state ? state->spin2j1 : '
            '((std::abs(pdg) == 443 || std::abs(pdg) == 413) ? 3 : '
            '(std::abs(pdg) == 10411 ? 1 : 2));',
        '(std::abs(pdg) == 4422 ? (pdg > 0 ? 6 : -6) : 0);':
            '((std::abs(pdg) == 4422) ? (pdg > 0 ? 6 : -6) : '
            '((std::abs(pdg) == 413 || std::abs(pdg) == 10411) ? '
            '(pdg > 0 ? 3 : -3) : 0));',
    }
    for old_text, new_text in replacements.items():
        if source.count(old_text) != 1:
            raise AssertionError("fixture transform changed: {}".format(old_text))
        source = source.replace(old_text, new_text)
    hard_marker = '        const int hardIndex = signedFlavour > 0 ? 10 : 11;'
    lineage = r'''
        int lineageIndex = hardIndex, secondLineageIndex = 0;
        int originCode = 1, resolutionCode = 1, matchedIndex = hardIndex, depthValue = 1;
        const int absolutePdg = std::abs(heavyPdg);
        if (row == 0 && absolutePdg != 421) {
          matchedIndex = -1;
          if (absolutePdg == 431) originCode = 2;
          else if (absolutePdg == 4112) originCode = 3;
          else if (absolutePdg == 4212 || absolutePdg == 10411) originCode = 4;
          else originCode = 0;
          if (absolutePdg == 413) {
            lineageIndex = 100 + 2 * static_cast<int>(slot);
            secondLineageIndex = lineageIndex + 1;
            resolutionCode = 2;
          } else if (originCode == 0) {
            lineageIndex = 0; resolutionCode = 3; depthValue = -1;
          } else {
            lineageIndex = 100 + 2 * static_cast<int>(slot);
          }
          if (lineageIndex > 0) {
            const int lineageStatus = originCode == 2 ? 51 :
                (originCode == 3 ? 31 : 61);
            integerVectors["ancestryIndex"].push_back(lineageIndex);
            integerVectors["ancestryPdg"].push_back(signedFlavour);
            integerVectors["ancestryStatus"].push_back(lineageStatus);
            integerVectors["ancestryMother1"].push_back(0);
            integerVectors["ancestryMother2"].push_back(0);
            integerVectors["ancestryMotherOffsets"].push_back(0);
            if (secondLineageIndex > 0) {
              integerVectors["ancestryIndex"].push_back(secondLineageIndex);
              integerVectors["ancestryPdg"].push_back(signedFlavour);
              integerVectors["ancestryStatus"].push_back(lineageStatus);
              integerVectors["ancestryMother1"].push_back(0);
              integerVectors["ancestryMother2"].push_back(0);
              integerVectors["ancestryMotherOffsets"].push_back(0);
            }
          }
        }
'''
    if source.count(hard_marker) != 1:
        raise AssertionError("fixture lineage insertion point changed")
    source = source.replace(hard_marker, hard_marker + lineage)
    marker = '    const std::vector<int> originalMatchedC = integerVectors["heavyMatchedHardC"];'
    boundary = r'''    if (row == 0) {
      // Exact synthetic-digest inputs use canonical local binary64 values.
      // Python independently checks these against the intended analytic kinematics.
      const bool reductionBoundary = false;
      for (std::size_t slot = 0; slot < heavyPdgs.size(); ++slot) {
        const double ptValue = slot == 0 ? 1.0 :
            (reductionBoundary && slot == 2 ? 0.2 : 0.15);
        const double etaValue = slot == 0 ? 4.0 :
            (reductionBoundary && slot <= 2 ? 4.0 : 4.1);
        const double phiValue = slot == 0 ? -1.4 : 2.5;
        const double pxValue = slot == 0 ? 0x1.5c17bbc13570bp-3 :
            (reductionBoundary && slot == 2 ? -0x1.4825ff2d13c64p-3 :
                                             -0x1.ec38fec39da96p-4);
        const double pyValue = slot == 0 ? -0x1.f88cddf44e102p-1 :
            (reductionBoundary && slot == 2 ? 0x1.ea44b494c7780p-4 :
                                              0x1.6fb3876f959ap-4);
        const double pzValue = slot == 0 ? 0x1.b4a3803703631p+4 :
            (reductionBoundary && slot == 1 ? 0x1.05fbb354353b7p+2 :
             reductionBoundary && slot == 2 ? 0x1.5d4f99c59c4f4p+2 :
                                               0x1.218dc7e8ce9f3p+2);
        const double energyValue = slot == 0 ? 0x1.b5397e056f1d4p+4 :
            (reductionBoundary && slot == 1 ? 0x1.0ddba8442df74p+2 :
             reductionBoundary && slot == 2 ? 0x1.635b2ac2a8e58p+2 :
                                               0x1.28b2a2ad3a891p+2);
        const double rapidityValue = slot == 0 ? 0x1.d3ae75b70f271p+1 :
            (reductionBoundary && slot == 1 ? 0x1.0d9c70606ab9ap+1 :
             reductionBoundary && slot == 2 ? 0x1.308aac9253b2cp+1 :
                                               0x1.1a142cead81c3p+1);
        doubleVectors["heavyPx"][slot] = pxValue;
        doubleVectors["heavyPy"][slot] = pyValue;
        doubleVectors["heavyPz"][slot] = pzValue;
        doubleVectors["heavyE"][slot] = energyValue;
        doubleVectors["heavyPt"][slot] = ptValue;
        doubleVectors["heavyEta"][slot] = etaValue;
        doubleVectors["heavyY"][slot] = rapidityValue;
        doubleVectors["heavyPhi"][slot] = phiValue;
        doubleVectors["PT"][slot] = ptValue;
        doubleVectors["ETA"][slot] = etaValue;
        doubleVectors["Y"][slot] = rapidityValue;
        doubleVectors["PHI"][slot] = phiValue;
      }
    }
'''
    if source.count(marker) != 1:
        raise AssertionError("fixture boundary insertion point changed")
    source = source.replace(marker, boundary + marker)
    finality_marker = '    const std::vector<int> originalMatchedC = integerVectors["heavyMatchedHardC"];'
    finality = r'''    if (row == 2) {
      std::fill(integerVectors["heavyStatus"].begin(), integerVectors["heavyStatus"].end(), -82);
      std::fill(integerVectors["heavyStatusAbs"].begin(), integerVectors["heavyStatusAbs"].end(), 82);
      std::fill(integerVectors["STATUS"].begin(), integerVectors["STATUS"].end(), -82);
      std::fill(integerVectors["heavyIsFinal"].begin(), integerVectors["heavyIsFinal"].end(), 0);
    }
'''
    source = source.replace(finality_marker, finality + finality_marker)
    audit_marker = '    tree.Fill(); hMultiplicity.Fill(mult10, weight);'
    audit = r'''    if (mode == "nonempty_mult_audit" && row == 0) {
      integerVectors["multAuditParticleIndex"] = {1};
      integerVectors["multAuditPdg"] = {211};
      integerVectors["multAuditStatus"] = {1};
      integerVectors["multAuditIsHeavy"] = {0};
      doubleVectors["multAuditPt"] = {1.0};
      doubleVectors["multAuditEta"] = {0.0};
    }
'''
    if source.count(audit_marker) != 1:
        raise AssertionError("fixture multiplicity-audit insertion point changed")
    return source.replace(audit_marker, audit + audit_marker)


class AnalysisShardContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT / "pipeline/generate"))
        import runtime
        try:
            cls.runtime = runtime.resolve(require_root=True)
        except ValueError as error:
            raise unittest.SkipTest("ROOT unavailable for analysis fixture: {}".format(error))
        cls.environment = os.environ.copy()
        cls.environment.update(cls.runtime["environment"])
        cls.temporary = tempfile.TemporaryDirectory()
        cls.base = Path(cls.temporary.name).resolve()
        cls.raw_root = cls.base / "raw"
        cls.work_root = cls.base / "work"
        cls.output_root = cls.base / "analyzed"
        cls.split_output_root = cls.base / "analyzed-split"
        cls.raw_paths = [cls.raw_root / "MONASH/not-derived-from-identity.root",
                         cls.raw_root / "MONASH/wide-job-id-0001.root"]
        cls.raw_paths[0].parent.mkdir(parents=True)
        cls.work_root.mkdir()
        cls.output_root.mkdir()
        cls.split_output_root.mkdir()
        cls._compile(fixture_source(), cls.base / "fixture.cpp", cls.base / "fixture")
        cls._compile(ORACLE, cls.base / "oracle.cpp", cls.base / "oracle")
        cls._compile(MUTATOR, cls.base / "mutator.cpp", cls.base / "mutator")
        cls._compile((ROOT / "pipeline/analyze/analyze.cpp").read_text(encoding="utf-8"),
                     cls.base / "analyze.cpp", cls.base / "analyzer",
                     include_generate=True)
        for logical, path in enumerate(cls.raw_paths):
            subprocess.run([str(cls.base / "fixture"), str(path), "valid", str(logical),
                            "0", "MONASH", "0", "3"],
                           check=True, env=cls.environment)
        cls.raw_digests = [sha256(path) for path in cls.raw_paths]
        inspection = subprocess.run(
            [str(cls.base / "analyzer"), "inspect-raw", str(cls.raw_paths[0])],
            check=True, env=cls.environment, text=True, stdout=subprocess.PIPE)
        cls.raw_metadata = json.loads(inspection.stdout)
        cls._write_control_plane()
        cls.plan = cls.work_root / "plan.json"
        cls.plan_copy = cls.work_root / "plan-copy.json"
        for plan in (cls.plan, cls.plan_copy):
            cls._cli("plan", "--campaign", str(cls.campaign_path),
                     "--manifest", str(cls.manifest_path), "--attempts", str(cls.attempts_path),
                     "--raw-root", str(cls.raw_root), "--work-root", str(cls.work_root),
                     "--output-root", str(cls.output_root), "--plan", str(plan),
                     "--target-bytes", "1000000000", check=True)
        if cls.plan.read_bytes() != cls.plan_copy.read_bytes():
            raise AssertionError("identical planning inputs produced different receipts")
        cls._cli("run", "--plan", str(cls.plan), check=True)
        cls.split_plan = cls.work_root / "split-plan.json"
        cls._cli("plan", "--campaign", str(cls.campaign_path),
                 "--manifest", str(cls.manifest_path), "--attempts", str(cls.attempts_path),
                 "--raw-root", str(cls.raw_root), "--work-root", str(cls.work_root),
                 "--output-root", str(cls.split_output_root), "--plan", str(cls.split_plan),
                 "--target-bytes", "1", check=True)
        cls._cli("run", "--plan", str(cls.split_plan), check=True)
        cls.shard = cls.output_root / "HF_RUN3_V1/shard-0000.root"
        cls.receipt = cls.shard.with_suffix(".json")
        cls.oracle = cls._read_oracle(cls.shard)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "temporary"):
            cls.temporary.cleanup()

    @classmethod
    def _compile(cls, source, source_path, output, include_generate=False):
        source_path.write_text(source, encoding="utf-8")
        flags = shlex.split(subprocess.check_output(
            [cls.environment["ROOT_CONFIG"], "--cflags", "--libs"],
            text=True, env=cls.environment))
        command = [cls.environment["CXX"], "-std=c++17", "-Wall", "-Wextra",
                   "-Wpedantic", str(source_path)]
        if include_generate or source_path.name == "fixture.cpp":
            command.append("-I" + str(ROOT / "pipeline/generate"))
        subprocess.run(command + flags + ["-o", str(output)], check=True,
                       env=cls.environment, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)

    @classmethod
    def _write_control_plane(cls):
        control = cls.base / "control"
        data = control / "data"
        config = control / "config"
        data.mkdir(parents=True)
        config.mkdir()
        shutil.copy2(ROOT / "config/study.json", config / "study.json")
        campaign = json.loads((ROOT / "data/campaign.json").read_text(encoding="utf-8"))
        campaign["tune_order"] = ["MONASH"]
        campaign["logical_jobs_per_tune"] = 2
        campaign["successful_events_per_logical_job"] = 3
        campaign["successful_events_per_tune"] = 6
        campaign["blocks"] = {"count": 2, "logical_id_domain": [0, 1],
                              "logical_id_rule": "block=(logical_id%2)+1"}
        campaign["seed"]["attempt_domain"] = [0, 1]
        campaign["seed"]["tune_ordinals"] = {"MONASH": 0}
        campaign["attempt_evidence_inventory"] = {"file_count": 2,
                                                   "sha256": "a" * 64}
        campaign["accepted_source"]["tune_cards"] = {
            "MONASH": campaign["accepted_source"]["tune_cards"]["MONASH"]}
        campaign["accepted_source"]["producer_executable_sha256"] = "b" * 64
        campaign["accepted_source"]["producer_repository_commit"] = "c" * 40
        campaign["accepted_source"]["tune_cards"]["MONASH"][
            "accepted_effective_sha256"] = cls.raw_metadata["effective_settings_sha256"]
        cls.campaign_path = data / "campaign.json"
        cls.campaign_path.write_text(json.dumps(campaign, sort_keys=True), encoding="utf-8")
        rows = []
        storage_keys = ["MONASH/not-derived-from-identity.root",
                        "MONASH/wide-job-id-0001.root"]
        for logical, (path, digest, storage_key) in enumerate(
                zip(cls.raw_paths, cls.raw_digests, storage_keys)):
            rows.append({
                "accepted_attempt": 0, "accepted_seed": 130000001 + logical,
                "block": logical + 1, "bytes": path.stat().st_size,
                "logical_id": logical, "raw_sha256": digest,
                "raw_storage_key": storage_key, "successful_events": 3,
                "tune": "MONASH", "validation_log_sha256": "d" * 64,
                "validation_receipt_sha256": "e" * 64,
            })
        cls.manifest_path = data / "raw_manifest.jsonl"
        cls.manifest_path.write_text(
            "".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n"
                    for row in rows),
            encoding="utf-8")
        cls.attempts_path = data / "attempts.csv"
        cls.attempts_path.write_text(
            "tune,logical_id,attempt,seed,outcome,evidence_status,raw_storage_key\n"
            "MONASH,0,0,130000001,accepted,accepted_manifest_confirmed,"
            "MONASH/not-derived-from-identity.root\n"
            "MONASH,1,0,130000002,accepted,accepted_manifest_confirmed,"
            "MONASH/wide-job-id-0001.root\n", encoding="utf-8")

    @classmethod
    def _cli(cls, *arguments, check=False, environment=None):
        result = subprocess.run([str(ROOT / "hadronization"), "analyze"] + list(arguments),
                                cwd=str(ROOT), env=environment or cls.environment, text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if check and result.returncode:
            raise AssertionError("analyze CLI failed: {}".format(result.stderr))
        return result

    def _single_source_plan(self, label, raw_root, raw_path, output_root,
                            work_root=None):
        work_root = work_root or self.work_root
        control = self.base / "single-controls" / label
        data = control / "data"
        config = control / "config"
        data.mkdir(parents=True)
        config.mkdir()
        shutil.copy2(ROOT / "config/study.json", config / "study.json")
        campaign = json.loads(self.campaign_path.read_text(encoding="utf-8"))
        campaign["logical_jobs_per_tune"] = 1
        campaign["successful_events_per_tune"] = 3
        campaign["blocks"] = {"count": 1, "logical_id_domain": [0, 0],
                              "logical_id_rule": "block=(logical_id%1)+1"}
        campaign["attempt_evidence_inventory"] = {"file_count": 1,
                                                   "sha256": "a" * 64}
        campaign_path = data / "campaign.json"
        campaign_path.write_text(json.dumps(campaign, sort_keys=True), encoding="utf-8")
        storage_key = "MONASH/{}".format(raw_path.name)
        manifest_row = {
            "accepted_attempt": 0, "accepted_seed": 130000001,
            "block": 1, "bytes": raw_path.stat().st_size,
            "logical_id": 0, "raw_sha256": sha256(raw_path),
            "raw_storage_key": storage_key, "successful_events": 3,
            "tune": "MONASH", "validation_log_sha256": "d" * 64,
            "validation_receipt_sha256": "e" * 64,
        }
        manifest = data / "raw_manifest.jsonl"
        manifest.write_text(json.dumps(manifest_row, sort_keys=True,
                                       separators=(",", ":")) + "\n",
                            encoding="utf-8")
        attempts = data / "attempts.csv"
        attempts.write_text(
            "tune,logical_id,attempt,seed,outcome,evidence_status,raw_storage_key\n"
            "MONASH,0,0,130000001,accepted,accepted_manifest_confirmed,{}\n".format(
                storage_key), encoding="utf-8")
        plan = work_root / (label + "-plan.json")
        self._cli("plan", "--campaign", str(campaign_path),
                  "--manifest", str(manifest), "--attempts", str(attempts),
                  "--raw-root", str(raw_root), "--work-root", str(work_root),
                  "--output-root", str(output_root), "--plan", str(plan),
                  "--target-bytes", "1000000000", check=True)
        return plan

    @classmethod
    def _read_oracle(cls, path):
        result = subprocess.run([str(cls.base / "oracle"), str(path)], check=True,
                                env=cls.environment, text=True, stdout=subprocess.PIPE)
        parsed = {"keys": [], "schemas": {}, "rows": {name: [] for name in TABLES}}
        for line in result.stdout.splitlines():
            if not line:
                continue
            kind, *values = line.split("\t")
            if kind == "COMP":
                parsed["compression"] = tuple(map(int, values))
            elif kind == "KEY":
                parsed["keys"].append(tuple(values))
            elif kind == "SCHEMA":
                parsed["schemas"][values[0]] = values[1]
            elif kind == "ROW":
                parsed["rows"][values[0]].append(values[1:])
            elif kind == "CONTRACT":
                parsed["contract"] = json.loads(values[0])
            else:
                raise AssertionError("unknown oracle line: {}".format(line))
        return parsed

    def named_rows(self, name):
        fields = [field.split(":", 1)[0] for field in EXPECTED_SCHEMA[name].split(",")]
        return [dict(zip(fields, row)) for row in self.oracle["rows"][name]]

    def receipt_for_root(self, root_path, label, mutate=None):
        payload = json.loads(self.receipt.read_text(encoding="utf-8"))
        payload["storage_identity"]["root_bytes"] = root_path.stat().st_size
        payload["storage_identity"]["root_sha256"] = sha256(root_path)
        payload["storage_identity_sha256"] = hashlib.sha256(json.dumps(
            payload["storage_identity"], sort_keys=True,
            separators=(",", ":")).encode("utf-8")).hexdigest()
        if mutate is not None:
            mutate(payload)
        receipt_path = root_path.with_name(label + ".json")
        receipt_path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
        return receipt_path

    def test_exact_schema_semantics_and_independent_digest(self):
        self.assertEqual(self.oracle["compression"], (5, 5))
        self.assertEqual(set(self.oracle["schemas"]), set(TABLES))
        self.assertEqual(self.oracle["schemas"], EXPECTED_SCHEMA)
        keys = {(name, kind, int(cycle)) for name, kind, cycle in self.oracle["keys"]}
        self.assertEqual(keys, {(name, "TTree", 1) for name in TABLES} |
                         {("contract", "TObjString", 1)})
        self.assertNotIn("cells", self.oracle["schemas"])
        self.assertNotIn("event_gram", self.oracle["schemas"])
        self.assertEqual(self.oracle["contract"]["streaming"], {
            "aggregate_autoflush_bytes": 64 * 1024 * 1024,
            "basket_bytes": 32 * 1024,
            "event_flush_interval": 8192,
            "per_tree_autoflush_bytes": 4 * 1024 * 1024,
        })

        digest = hashlib.sha256()
        for name in TABLES:
            digest.update(name.encode("ascii") + b"\0")
            for row in self.oracle["rows"][name]:
                for value in row:
                    encoded = value.encode("ascii")
                    digest.update(struct.pack(">Q", len(encoded)))
                    digest.update(encoded)
        receipt = json.loads(self.receipt.read_text(encoding="utf-8"))
        self.assertEqual(digest.hexdigest(), CANDIDATE_FIXTURE_DIGEST)
        self.assertEqual({name: len(rows) for name, rows in self.oracle["rows"].items()},
                         CANDIDATE_FIXTURE_ROWS)
        self.assertEqual(digest.hexdigest(),
                         receipt["scientific_identity"]["scientific_content_digest"])
        self.assertEqual(digest.hexdigest(),
                         self.oracle["contract"]["scientific_content_digest"])

        triggers = self.named_rows("triggers")
        self.assertEqual(len(triggers), 10)
        self.assertEqual(sum(row["rejection_mask"] == "0" for row in triggers), 6)
        self.assertEqual(sum(row["rejection_mask"] == "3" for row in triggers), 4)
        pairs = self.named_rows("pairs")
        self.assertEqual(len(pairs), 38)
        self.assertEqual({float.fromhex(row["trigger_pt"]) for row in pairs},
                         {0.0, 0.15, 1.0})
        self.assertTrue(any(float.fromhex(row["associate_pt"]) < 0.15 for row in pairs))
        self.assertEqual({row["sign"] for row in pairs}, {"-1", "1"})
        self.assertEqual({row["associate_origin"] for row in pairs},
                         {"1", "2", "3", "4", "5"})
        heavy = self.named_rows("heavy")
        heavy_by_key = {(row["event_id"], row["heavy_index"]): row for row in heavy}
        first_event = heavy[0]["event_id"]
        canonical_cases = (
            ("20", 1.0, 4.0, -1.4, {
                "px": float.fromhex("0x1.5c17bbc13570bp-3"),
                "py": float.fromhex("-0x1.f88cddf44e102p-1"),
                "pz": float.fromhex("0x1.b4a3803703631p+4"),
                "energy": float.fromhex("0x1.b5397e056f1d4p+4"),
                "rapidity": float.fromhex("0x1.d3ae75b70f271p+1"),
            }),
            ("21", 0.15, 4.1, 2.5, {
                "px": float.fromhex("-0x1.ec38fec39da96p-4"),
                "py": float.fromhex("0x1.6fb3876f959ap-4"),
                "pz": float.fromhex("0x1.218dc7e8ce9f3p+2"),
                "energy": float.fromhex("0x1.28b2a2ad3a891p+2"),
                "rapidity": float.fromhex("0x1.1a142cead81c3p+1"),
            }),
            (None, 0.15, 4.0, 2.5, {
                "px": float.fromhex("-0x1.ec38fec39da96p-4"),
                "py": float.fromhex("0x1.6fb3876f959ap-4"),
                "pz": float.fromhex("0x1.05fbb354353b7p+2"),
                "energy": float.fromhex("0x1.0ddba8442df74p+2"),
                "rapidity": float.fromhex("0x1.0d9c70606ab9ap+1"),
            }),
            (None, 0.2, 4.0, 2.5, {
                "px": float.fromhex("-0x1.4825ff2d13c64p-3"),
                "py": float.fromhex("0x1.ea44b494c7780p-4"),
                "pz": float.fromhex("0x1.5d4f99c59c4f4p+2"),
                "energy": float.fromhex("0x1.635b2ac2a8e58p+2"),
                "rapidity": float.fromhex("0x1.308aac9253b2cp+1"),
            }),
        )
        for heavy_index, pt, eta, phi, canonical in canonical_cases:
            expected = {
                "px": pt * math.cos(phi),
                "py": pt * math.sin(phi),
                "pz": pt * math.sinh(eta),
            }
            expected["energy"] = math.sqrt(
                1.0 + expected["px"] ** 2 + expected["py"] ** 2 +
                expected["pz"] ** 2)
            expected["rapidity"] = 0.5 * math.log(
                (expected["energy"] + expected["pz"]) /
                (expected["energy"] - expected["pz"]))
            for field, value in expected.items():
                stored = canonical[field]
                tolerance = 256 * max(math.ulp(stored), math.ulp(value))
                self.assertLessEqual(abs(stored - value), tolerance,
                                     (pt, eta, phi, field, stored, value))
            if heavy_index is not None:
                row = heavy_by_key[(first_event, heavy_index)]
                self.assertEqual((float.fromhex(row["pt"]),
                                  float.fromhex(row["eta"]),
                                  float.fromhex(row["phi"]),
                                  float.fromhex(row["mass"])),
                                 (pt, eta, phi, 1.0))
                for field, value in canonical.items():
                    self.assertEqual(float.fromhex(row[field]), value,
                                     (heavy_index, field))
        for row in pairs:
            trigger = heavy_by_key[(row["event_id"], row["trigger_heavy_index"])]
            associate = heavy_by_key[(row["event_id"], row["associate_heavy_index"])]
            delta = float.fromhex(trigger["phi"]) - float.fromhex(associate["phi"])
            expected_dphi = math.fmod(delta + math.pi / 2.0, 2.0 * math.pi)
            if expected_dphi < 0:
                expected_dphi += 2.0 * math.pi
            expected_dphi -= math.pi / 2.0
            observed_dphi = float.fromhex(row["dphi"])
            self.assertEqual(observed_dphi, expected_dphi)
            inverse = float.fromhex(trigger["phi"]) - observed_dphi
            self.assertAlmostEqual(math.remainder(inverse - float.fromhex(associate["phi"]),
                                                   2.0 * math.pi), 0.0, places=14)
        sigma_b_zero = next(row for row in heavy if row["pdg"] == "5212")
        self.assertEqual(sigma_b_zero["pair_eligible"], "0")
        self.assertTrue(any(row["associate_heavy_index"] == sigma_b_zero["heavy_index"]
                            for row in pairs))
        last_event = self.named_rows("events")[-1]["event_id"]
        self.assertTrue(all(row["rejection_mask"] != "0" for row in triggers
                            if row["event_id"] == last_event))
        closure = self.named_rows("closure")
        self.assertEqual({row["dense_category"] for row in closure}, {"0", "1", "2", "3"})
        self.assertEqual({row["visible"] for row in closure}, {"0", "1"})
        constituents = self.named_rows("constituents")
        hidden_index = next(row["heavy_index"] for row in heavy if row["pdg"] == "443")
        self.assertEqual({row["signed_flavour"] for row in constituents
                          if row["heavy_index"] == hidden_index}, {"-4", "4"})
        multiply_keys = {(row["event_id"], row["heavy_index"]) for row in heavy
                         if abs(int(row["pdg"])) == 4422}
        self.assertTrue(all(sum((row["event_id"], row["heavy_index"]) == key
                                for row in constituents) == 2
                            for key in multiply_keys))
        mother_counts = {}
        for row in self.named_rows("heavy_mothers"):
            mother_counts[(row["event_id"], row["heavy_index"])] = (
                mother_counts.get((row["event_id"], row["heavy_index"]), 0) + 1)
        self.assertIn(2, mother_counts.values())
        source = self.named_rows("sources")[0]
        self.assertEqual((source["source_id"], source["logical_id"]), ("0", "0"))
        self.assertEqual({row["block"] for row in self.named_rows("source_blocks")},
                         {"1", "2"})
        metadata = self.oracle["contract"]["source_metadata"]["sources"][0]
        self.assertEqual(metadata["raw_sha256"], self.raw_digests[0])
        self.assertEqual(metadata["raw_storage_key"],
                         "MONASH/not-derived-from-identity.root")
        dictionaries = self.oracle["contract"]["source_metadata"]["dictionaries"]
        self.assertIn(metadata["effective_settings_identity"],
                      dictionaries["effective_settings"])
        self.assertIn(metadata["stability_identity"],
                      dictionaries["heavy_stability"])
        self.assertIn(metadata["pythia_statistics_identity"],
                      dictionaries["pythia_statistics"])

    def test_deterministic_plan_resume_and_no_overwrite(self):
        before = sha256(self.shard)
        resume = self._cli("run", "--plan", str(self.plan), check=True)
        self.assertIn("REUSED shard=0", resume.stdout)
        self.assertEqual(sha256(self.shard), before)
        collision = self._cli("run", "--plan", str(self.plan), "--no-resume")
        self.assertEqual(collision.returncode, 2)
        self.assertIn("collision", collision.stderr)
        verify = self._cli("verify", "--plan", str(self.plan), check=True)
        self.assertIn("VERIFIED shard=0", verify.stdout)
        explain = self._cli("explain", "--receipt", str(self.receipt),
                            "--raw-root", str(self.raw_root),
                            "--work-root", str(self.work_root), check=True)
        self.assertEqual(json.loads(explain.stdout)["state"], "PASS")
        self.assertEqual([sha256(path) for path in self.raw_paths], self.raw_digests)

    def test_factorization_and_unequal_shard_planning_are_data_driven(self):
        base = self.base / "factorization"
        control = base / "control/data"
        config = base / "control/config"
        raw_root = base / "raw"
        output_root = base / "output"
        work_root = base / "work"
        control.mkdir(parents=True)
        config.mkdir()
        shutil.copy2(ROOT / "config/study.json", config / "study.json")
        campaign = json.loads(self.campaign_path.read_text(encoding="utf-8"))
        campaign["tune_order"] = ["MONASH", "JUNCTIONS"]
        campaign["logical_jobs_per_tune"] = 1
        campaign["successful_events_per_logical_job"] = 3
        campaign["successful_events_per_tune"] = 3
        campaign["blocks"] = {"count": 1, "logical_id_domain": [0, 0],
                              "logical_id_rule": "block=(logical_id%1)+1"}
        campaign["seed"]["tune_ordinals"] = {"MONASH": 0, "JUNCTIONS": 1}
        campaign["seed"]["attempt_domain"] = [0, 1]
        campaign["attempt_evidence_inventory"] = {"file_count": 3,
                                                   "sha256": "a" * 64}
        campaign["accepted_source"]["tune_cards"] = {
            tune: json.loads((ROOT / "data/campaign.json").read_text(
                encoding="utf-8"))["accepted_source"]["tune_cards"][tune]
            for tune in campaign["tune_order"]}
        campaign_path = control / "campaign.json"
        campaign_path.write_text(json.dumps(campaign, sort_keys=True), encoding="utf-8")
        descriptors = [("MONASH", 0, 1, 0, "opaque-job-000000.root"),
                       ("JUNCTIONS", 0, 0, 1, "x.root")]
        rows, attempts_rows = [], []
        for tune, logical, attempt, ordinal, filename in descriptors:
            path = raw_root / tune / filename
            path.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run([str(self.base / "fixture"), str(path), "valid",
                            str(logical), str(attempt), tune, str(ordinal), "3"],
                           check=True, env=self.environment)
            seed = 130000001 + ordinal * 1000000 + attempt * 100000 + logical
            storage = "{}/{}".format(tune, filename)
            rows.append({
                "accepted_attempt": attempt, "accepted_seed": seed,
                "block": 1, "bytes": path.stat().st_size,
                "logical_id": logical, "raw_sha256": sha256(path),
                "raw_storage_key": storage, "successful_events": 3,
                "tune": tune, "validation_log_sha256": "b" * 64,
                "validation_receipt_sha256": "c" * 64,
            })
            for prior in range(attempt):
                attempts_rows.append(
                    "{},{},{},{},discarded,inferred_from_accepted_attempt_ordinal,".format(
                        tune, logical, prior,
                        130000001 + ordinal * 1000000 + prior * 100000 + logical))
            attempts_rows.append(
                "{},{},{},{},accepted,accepted_manifest_confirmed,{}".format(
                    tune, logical, attempt, seed, storage))
        manifest = control / "manifest.jsonl"
        manifest.write_text("".join(json.dumps(row, sort_keys=True,
                                               separators=(",", ":")) + "\n"
                                    for row in rows), encoding="utf-8")
        attempts = control / "attempts.csv"
        attempts.write_text(
            "tune,logical_id,attempt,seed,outcome,evidence_status,raw_storage_key\n" +
            "\n".join(attempts_rows) + "\n", encoding="utf-8")
        plan = work_root / "factorization-plan.json"
        result = self._cli(
            "plan", "--campaign", str(campaign_path), "--manifest", str(manifest),
            "--attempts", str(attempts), "--raw-root", str(raw_root),
            "--work-root", str(work_root), "--output-root", str(output_root),
            "--plan", str(plan), "--target-bytes", "1000000000", check=True)
        self.assertIn("SHARDS=1 SOURCES=2", result.stdout)
        self._cli("run", "--plan", str(plan), check=True)
        payload = json.loads(plan.read_text(encoding="utf-8"))
        self.assertEqual([shard["source_ids"] for shard in payload["shards"]],
                         [[0, 1]])
        self.assertEqual([source["manifest_row"]["accepted_attempt"]
                          for source in payload["sources"]], [1, 0])
        receipt = json.loads((output_root / "HF_RUN3_V1/shard-0000.json").read_text(
            encoding="utf-8"))
        self.assertEqual(receipt["binding"]["tune_ordinals"],
                         {"MONASH": 0, "JUNCTIONS": 1})

    def test_incoherent_descriptor_and_manifest_fail_before_plan_creation(self):
        base_campaign = json.loads(self.campaign_path.read_text(encoding="utf-8"))
        base_rows = [json.loads(line) for line in self.manifest_path.read_text(
            encoding="utf-8").splitlines()]
        cases = {}
        campaign = json.loads(json.dumps(base_campaign))
        campaign["seed"]["campaign_ordinal"] = 65536
        cases["campaign-ordinal"] = (campaign, base_rows, "campaign ordinal")
        campaign = json.loads(json.dumps(base_campaign))
        campaign["seed"]["tune_ordinals"]["MONASH"] = 3
        cases["tune-ordinal"] = (campaign, base_rows, "tune ordinals")
        campaign = json.loads(json.dumps(base_campaign))
        campaign["successful_events_per_tune"] += 1
        cases["exposure-total"] = (campaign, base_rows, "exposure is incoherent")
        rows = json.loads(json.dumps(base_rows))
        rows[0]["block"] = 2
        cases["block"] = (base_campaign, rows, "descriptor rule")
        rows = json.loads(json.dumps(base_rows))
        rows[0]["accepted_seed"] += 1
        cases["seed"] = (base_campaign, rows, "accepted seed")
        rows = json.loads(json.dumps(base_rows))
        rows[0]["successful_events"] = 1 << 20
        cases["event-id"] = (base_campaign, rows, "exposure differs")
        rows = json.loads(json.dumps(base_rows))
        rows[1]["logical_id"] = 16384
        cases["logical-domain"] = (base_campaign, rows, "logical ID")
        for label, (campaign, rows, diagnostic) in cases.items():
            control = self.base / "invalid-controls" / label
            control.mkdir(parents=True)
            campaign_path = control / "campaign.json"
            manifest_path = control / "manifest.jsonl"
            plan = self.work_root / ("invalid-" + label + ".json")
            campaign_path.write_text(json.dumps(campaign, sort_keys=True), encoding="utf-8")
            manifest_path.write_text("".join(json.dumps(row, sort_keys=True,
                                                         separators=(",", ":")) + "\n"
                                             for row in rows), encoding="utf-8")
            result = self._cli(
                "plan", "--campaign", str(campaign_path), "--manifest",
                str(manifest_path), "--attempts", str(self.attempts_path),
                "--raw-root", str(self.raw_root), "--work-root", str(self.work_root),
                "--output-root", str(self.base / "invalid-output"), "--plan",
                str(plan), "--target-bytes", "1000")
            self.assertEqual(result.returncode, 2, label)
            self.assertIn(diagnostic, result.stderr, (label, result.stderr))
            self.assertFalse(plan.exists(), label)

    def test_failure_cleanup_partial_collision_symlink_and_promotion_race(self):
        partial_output = self.base / "partial-output"
        partial_plan = self._single_source_plan(
            "partial", self.raw_root, self.raw_paths[0], partial_output)
        partial = partial_output / "HF_RUN3_V1/shard-0000.root"
        partial.parent.mkdir(parents=True)
        partial.write_bytes(b"foreign")
        result = self._cli("run", "--plan", str(partial_plan))
        self.assertEqual(result.returncode, 2)
        self.assertIn("root-only promotion recovery rejected", result.stderr)
        self.assertEqual(partial.read_bytes(), b"foreign")

        link = self.base / "analysis-shard-link.root"
        link.symlink_to(self.shard)
        result = self._cli("verify", "--root", str(link),
                           "--work-root", str(self.work_root),
                           "--raw-root", str(self.raw_root))
        self.assertEqual(result.returncode, 2)
        self.assertIn("symlink component", result.stderr)

        race_output = self.base / "race-output"
        race_plan = self._single_source_plan(
            "race", self.raw_root, self.raw_paths[0], race_output)
        command = [str(ROOT / "hadronization"), "analyze", "run", "--plan",
                   str(race_plan), "--no-resume"]
        processes = [subprocess.Popen(command, cwd=str(ROOT), env=self.environment,
                                      text=True, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE) for unused in range(2)]
        results = [process.communicate() + (process.returncode,) for process in processes]
        self.assertEqual(sorted(result[2] for result in results), [0, 2], results)
        self.assertTrue(any("no-overwrite promotion collision" in result[1] or
                            "foreign or partial final collision" in result[1]
                            for result in results if result[2] == 2), results)
        verify = self._cli("verify", "--plan", str(race_plan), check=True)
        self.assertIn("VERIFIED shard=0", verify.stdout)
        staging = self.work_root / "staging"
        self.assertFalse(staging.exists() and any(staging.iterdir()))

        interruption_output = self.base / "interruption-output"
        interruption_plan = self._single_source_plan(
            "interruption", self.raw_root, self.raw_paths[0], interruption_output)
        environment = dict(self.environment)
        environment["HADRONIZATION_ANALYZE_FAIL_AFTER_ROOT_PROMOTION"] = "1"
        result = self._cli("run", "--plan", str(interruption_plan),
                           environment=environment)
        self.assertEqual(result.returncode, 2)
        self.assertIn("injected interruption after ROOT promotion", result.stderr)
        partial_root = interruption_output / "HF_RUN3_V1/shard-0000.root"
        partial_receipt = partial_root.with_suffix(".json")
        self.assertTrue(partial_root.is_file())
        self.assertFalse(partial_receipt.exists())
        partial_digest = sha256(partial_root)
        recovered = self._cli("run", "--plan", str(interruption_plan), check=True)
        self.assertIn("RECOVERED shard=0", recovered.stdout)
        self.assertEqual(sha256(partial_root), partial_digest)
        self.assertTrue(partial_receipt.is_file())
        self._cli("verify", "--plan", str(interruption_plan), check=True)
        self.assertEqual([sha256(path) for path in self.raw_paths], self.raw_digests)

        cache_work = self.base / "cache-work"
        cache_output = self.base / "cache-output"
        cache_plan = self._single_source_plan(
            "cache", self.raw_root, self.raw_paths[0], cache_output, cache_work)
        self._cli("run", "--plan", str(cache_plan), check=True)
        cached_analyzer = next(path for path in (cache_work / "bin").glob("analyze-*")
                               if path.suffix != ".json")
        substituted = (
            "#!/usr/bin/env python3\nimport os,sys\n"
            "print('substituted cache executed',file=sys.stderr);sys.exit(97)\n")
        cached_analyzer.write_text(substituted, encoding="utf-8")
        cached_analyzer.chmod(0o700)
        verify = self._cli("verify", "--plan", str(cache_plan), check=True)
        self.assertIn("VERIFIED shard=0", verify.stdout)
        self.assertNotEqual(cached_analyzer.read_text(encoding="latin1"), substituted)
        build_receipt = json.loads(cached_analyzer.with_suffix(
            ".build.json").read_text(encoding="utf-8"))
        self.assertEqual(build_receipt["binary_sha256"], sha256(cached_analyzer))
        self.assertFalse((cache_work / "staging").exists() and
                         any((cache_work / "staging").iterdir()))

    def test_receipt_provenance_mutation_is_rejected(self):
        mutant = self.output_root / "receipt-mutant"
        mutant.mkdir()
        root_path = mutant / "shard.root"
        receipt_path = mutant / "shard.json"
        shutil.copy2(self.shard, root_path)
        payload = json.loads(self.receipt.read_text(encoding="utf-8"))
        payload["producer_provenance"]["publication"]["host"] = "foreign-host"
        receipt_path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
        result = self._cli("verify", "--root", str(root_path),
                           "--receipt", str(receipt_path),
                           "--raw-root", str(self.raw_root),
                           "--work-root", str(self.work_root))
        self.assertEqual(result.returncode, 2)
        self.assertIn("producer provenance digest mismatch", result.stderr)

    def test_plan_receipt_root_and_dictionary_cross_binding_is_structural(self):
        mutant_root = self.output_root / "contract-mutants"
        mutant_root.mkdir()
        cases = {
            "contract_map": "ROOT contract binding differs from receipt",
            "dictionary_reference": "dictionary reference is unresolved",
            "dictionary_payload": "dictionary key/payload collision",
            "source_reference": "source metadata/receipt cross-binding differs",
        }
        for mode, diagnostic in cases.items():
            root_path = mutant_root / (mode + ".root")
            subprocess.run([str(self.base / "mutator"), str(self.shard),
                            str(root_path), mode], check=True, env=self.environment)
            receipt_path = self.receipt_for_root(root_path, mode)
            result = self._cli("verify", "--root", str(root_path),
                               "--receipt", str(receipt_path),
                               "--raw-root", str(self.raw_root),
                               "--work-root", str(self.work_root))
            self.assertEqual(result.returncode, 2, mode)
            self.assertIn(diagnostic, result.stderr, (mode, result.stderr))

        top_level = mutant_root / "top-level.json"
        payload = json.loads(self.receipt.read_text(encoding="utf-8"))
        payload["campaign"] = "FOREIGN"
        top_level.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
        result = self._cli("verify", "--root", str(self.shard),
                           "--receipt", str(top_level),
                           "--raw-root", str(self.raw_root),
                           "--work-root", str(self.work_root))
        self.assertEqual(result.returncode, 2)
        self.assertIn("duplicated binding fields", result.stderr)

        nested = mutant_root / "nested.json"
        payload = json.loads(self.receipt.read_text(encoding="utf-8"))
        payload["storage_identity"]["map_digest"] = "0" * 64
        payload["storage_identity_sha256"] = hashlib.sha256(json.dumps(
            payload["storage_identity"], sort_keys=True,
            separators=(",", ":")).encode("utf-8")).hexdigest()
        nested.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
        result = self._cli("verify", "--root", str(self.shard),
                           "--receipt", str(nested),
                           "--raw-root", str(self.raw_root),
                           "--work-root", str(self.work_root))
        self.assertEqual(result.returncode, 2)
        self.assertIn("duplicated binding fields", result.stderr)

    def test_raw_alias_vector_and_phase_a_audit_mutants_are_rejected(self):
        diagnostics = {
            "legacy_alias": "legacy scalar aliases disagree",
            "vector_lengths": "vector lengths or offsets are inconsistent",
            "nonempty_mult_audit": "multiplicity audit vectors exist beyond declared pilot range",
        }
        for mode, diagnostic in diagnostics.items():
            raw_root = self.base / "raw-mutants" / mode
            raw_path = raw_root / "MONASH" / (mode + ".root")
            raw_path.parent.mkdir(parents=True)
            subprocess.run([str(self.base / "fixture"), str(raw_path), mode, "0"],
                           check=True, env=self.environment)
            output = self.base / ("raw-mutant-output-" + mode)
            plan = self._single_source_plan(mode, raw_root, raw_path, output)
            result = self._cli("run", "--plan", str(plan))
            self.assertEqual(result.returncode, 2, mode)
            self.assertIn(diagnostic, result.stderr, (mode, result.stderr))
            self.assertFalse((output / "HF_RUN3_V1").exists())

    def test_source_scientific_identity_survives_regrouping(self):
        combined = json.loads(self.receipt.read_text(encoding="utf-8"))
        split_receipts = [json.loads(path.read_text(encoding="utf-8")) for path in
                          sorted((self.split_output_root / "HF_RUN3_V1").glob("*.json"))]
        combined_digests = combined["scientific_identity"][
            "source_scientific_digests"]
        split_digests = [receipt["scientific_identity"][
            "source_scientific_digests"][0] for receipt in split_receipts]
        self.assertEqual(combined_digests, split_digests)
        self.assertNotEqual(combined["map_digest"], split_receipts[0]["map_digest"])
        self.assertEqual([source["manifest_row"]["logical_id"]
                          for source in combined["sources"]], [0, 1])

    def test_minimal_root_mutants_are_rejected(self):
        analyzer = next(path for path in (self.work_root / "bin").glob("analyze-*")
                        if path.suffix != ".json")
        expected = {
            "unknown_object": "object set",
            "duplicate_cycle": "duplicate ROOT key/cycle",
            "missing_field": "branch order/set",
            "drop_row": "trigger candidate coverage",
            "duplicate_key": "duplicate/nonmonotonic natural key",
            "invalid_domain": "trigger rejection mask/coverage",
            "broken_join": "duplicate/nonmonotonic natural key",
            "broken_count": "source family counts",
            "shuffled_rows": "duplicate/nonmonotonic natural key",
            "wrong_cache": "pair cached authority/semantics",
            "wrong_source_block": "scientific content digest differs",
            "missing_source": "source digest routing is out of domain",
            "missing_event": "event-scoped rows remain after final event",
        }
        mutant_root = self.output_root / "mutants"
        mutant_root.mkdir()
        for mode, diagnostic in expected.items():
            path = mutant_root / (mode + ".root")
            subprocess.run([str(self.base / "mutator"), str(self.shard), str(path), mode],
                           check=True, env=self.environment)
            result = subprocess.run([str(analyzer), "verify", str(path)],
                                    env=self.environment, text=True,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.assertEqual(result.returncode, 2, mode)
            self.assertIn(diagnostic, result.stderr, mode)
        payload = mutant_root / "payload.root"
        shutil.copy2(self.shard, payload)
        with payload.open("r+b") as handle:
            handle.seek(-1, os.SEEK_END)
            value = handle.read(1)
            handle.seek(-1, os.SEEK_END)
            handle.write(bytes([value[0] ^ 1]))
        result = self._cli("verify", "--root", str(payload),
                           "--receipt", str(self.receipt),
                           "--raw-root", str(self.raw_root),
                           "--work-root", str(self.work_root))
        self.assertEqual(result.returncode, 2)
        self.assertIn("SHA-256 differs", result.stderr)
        truncated = mutant_root / "truncated.root"
        payload_bytes = self.shard.read_bytes()
        truncated.write_bytes(payload_bytes[:len(payload_bytes) // 2])
        result = subprocess.run([str(analyzer), "verify", str(truncated)],
                                env=self.environment, text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(result.returncode, 2)
        self.assertIn("analysis shard is zombie/unreadable", result.stderr)


if __name__ == "__main__":
    unittest.main()
