#include "TFile.h"
#include "TKey.h"
#include "TTree.h"
#include <memory>
#include <string>

// TEST_ONLY: turn associate 22 into selected-hard on root 11. The old gate
// omits 20->22 (same sign, different root) and 21->22 (OS, same root).
int main(int argc, char** argv) {
  if (argc != 3) return 2;
  constexpr ULong64_t targetEvent = 844424930131968ULL;
  TFile input(argv[1], "READ"), output(argv[2], "CREATE");
  if (input.IsZombie() || output.IsZombie()) return 3;
  int changedOrigin = 0, omittedSameSign = 0, omittedSameRoot = 0;
  TIter keys(input.GetListOfKeys());
  while (auto* item = keys()) {
    auto* key = dynamic_cast<TKey*>(item);
    if (!key) return 4;
    std::unique_ptr<TObject> object(key->ReadObj());
    output.cd();
    auto* tree = dynamic_cast<TTree*>(object.get());
    const std::string name = key->GetName();
    if (tree && name == "origins") {
      ULong64_t event = 0;
      Int_t index = 0, sector = 0, origin = 0, resolution = 0;
      Int_t matched = 0, rejected = 0, depth = 0;
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
        if (tree->GetEntry(i) <= 0) return 5;
        if (event == targetEvent && index == 22 && sector == 4) {
          origin = 1; resolution = 1; matched = 11; rejected = -1; depth = 1;
          ++changedOrigin;
        }
        if (copy->Fill() < 0) return 6;
      }
      if (copy->Write(name.c_str()) <= 0) return 7;
    } else if (tree && name == "pairs") {
      ULong64_t event = 0;
      Int_t trigger = 0, associate = 0;
      tree->SetBranchAddress("event_id", &event);
      tree->SetBranchAddress("trigger_heavy_index", &trigger);
      tree->SetBranchAddress("associate_heavy_index", &associate);
      std::unique_ptr<TTree> copy(tree->CloneTree(0));
      for (Long64_t i = 0; i < tree->GetEntries(); ++i) {
        if (tree->GetEntry(i) <= 0) return 8;
        if (event == targetEvent && trigger == 20 && associate == 22) {
          ++omittedSameSign;
          continue;
        }
        if (event == targetEvent && trigger == 21 && associate == 22) {
          ++omittedSameRoot;
          continue;
        }
        if (copy->Fill() < 0) return 9;
      }
      if (copy->Write(name.c_str()) <= 0) return 10;
    } else if (tree) {
      std::unique_ptr<TTree> copy(tree->CloneTree(-1, "fast"));
      if (copy->Write(name.c_str()) <= 0) return 11;
    } else if (object->Write(name.c_str()) <= 0) return 12;
  }
  output.Close();
  return changedOrigin == 1 && omittedSameSign == 1 && omittedSameRoot == 1 ? 0 : 13;
}
