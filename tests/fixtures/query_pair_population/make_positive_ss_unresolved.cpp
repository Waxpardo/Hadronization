#include "TFile.h"
#include "TKey.h"
#include "TTree.h"
#include <memory>
#include <string>

int main(int argc, char** argv) {
  if (argc != 3) return 2;
  constexpr ULong64_t targetEvent = 844424930131968ULL;
  constexpr Int_t targetAssociate = 22;
  TFile input(argv[1], "READ"), output(argv[2], "CREATE");
  if (input.IsZombie() || output.IsZombie()) return 3;
  int heavyChanged = 0, originChanged = 0, pairChanged = 0;
  TIter keys(input.GetListOfKeys());
  while (auto* item = keys()) {
    auto* key = dynamic_cast<TKey*>(item);
    if (!key) return 4;
    std::unique_ptr<TObject> object(key->ReadObj());
    output.cd();
    auto* tree = dynamic_cast<TTree*>(object.get());
    const std::string name = key->GetName();
    if (tree && name == "heavy") {
      ULong64_t event = 0; Int_t index = 0; Double_t eta = 0;
      tree->SetBranchAddress("event_id", &event);
      tree->SetBranchAddress("heavy_index", &index);
      tree->SetBranchAddress("eta", &eta);
      std::unique_ptr<TTree> copy(tree->CloneTree(0));
      for (Long64_t i = 0; i < tree->GetEntries(); ++i) {
        if (tree->GetEntry(i) <= 0) return 5;
        if (event == targetEvent && (index == 21 || index == targetAssociate)) { eta = 4.0; ++heavyChanged; }
        if (copy->Fill() < 0) return 6;
      }
      if (copy->Write(name.c_str()) <= 0) return 7;
    } else if (tree && name == "origins") {
      ULong64_t event = 0; Int_t index = 0, sector = 0;
      Int_t origin = 0, resolution = 0, matched = 0, rejected = 0, depth = 0;
      tree->SetBranchAddress("event_id", &event);
      tree->SetBranchAddress("heavy_index", &index);
      tree->SetBranchAddress("sector", &sector);
      tree->SetBranchAddress("origin", &origin);
      tree->SetBranchAddress("resolution", &resolution);
      tree->SetBranchAddress("matched_hard", &matched);
      tree->SetBranchAddress("rejected_hard", &rejected);
      tree->SetBranchAddress("depth", &depth);
      std::unique_ptr<TTree> copy(tree->CloneTree(0));
      for (Long64_t i = 0; i < tree->GetEntries(); ++i) {
        if (tree->GetEntry(i) <= 0) return 8;
        if (event == targetEvent && index == targetAssociate && sector == 4) {
          origin = 0; resolution = 2; matched = -1; rejected = -1; depth = -1;
          ++originChanged;
        }
        if (copy->Fill() < 0) return 9;
      }
      if (copy->Write(name.c_str()) <= 0) return 10;
    } else if (tree && name == "pairs") {
      ULong64_t event = 0; Int_t trigger = 0, associate = 0, denseOrigin = 0;
      Double_t deta = 0;
      tree->SetBranchAddress("event_id", &event);
      tree->SetBranchAddress("trigger_heavy_index", &trigger);
      tree->SetBranchAddress("associate_heavy_index", &associate);
      tree->SetBranchAddress("associate_origin", &denseOrigin);
      tree->SetBranchAddress("deta", &deta);
      std::unique_ptr<TTree> copy(tree->CloneTree(0));
      for (Long64_t i = 0; i < tree->GetEntries(); ++i) {
        if (tree->GetEntry(i) <= 0) return 11;
        if (event == targetEvent) {
          if (associate == targetAssociate) denseOrigin = 5;
          const double triggerEta = (trigger == 20 || trigger == 21) ? 4.0 : 4.1;
          const double associateEta = (associate == 20 || associate == 21 || associate == 22) ? 4.0 : 4.1;
          deta = triggerEta - associateEta;
          ++pairChanged;
        }
        if (copy->Fill() < 0) return 12;
      }
      if (copy->Write(name.c_str()) <= 0) return 13;
    } else if (tree && name == "closure") {
      ULong64_t event = 0; Int_t associate = 0; UChar_t visible = 0;
      tree->SetBranchAddress("event_id", &event);
      tree->SetBranchAddress("associate_heavy_index", &associate);
      tree->SetBranchAddress("visible", &visible);
      std::unique_ptr<TTree> copy(tree->CloneTree(0));
      for (Long64_t i = 0; i < tree->GetEntries(); ++i) {
        if (tree->GetEntry(i) <= 0) return 14;
        if (event == targetEvent && (associate == 21 || associate == targetAssociate)) visible = 1;
        if (copy->Fill() < 0) return 15;
      }
      if (copy->Write(name.c_str()) <= 0) return 16;
    } else if (tree) {
      std::unique_ptr<TTree> copy(tree->CloneTree(-1, "fast"));
      if (copy->Write(name.c_str()) <= 0) return 17;
    } else if (object->Write(name.c_str()) <= 0) return 18;
  }
  output.Close();
  return heavyChanged == 2 && originChanged == 1 && pairChanged == 18 ? 0 : 19;
}
