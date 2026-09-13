#include "TFile.h"
#include "TKey.h"
#include "TTree.h"
#include <memory>
#include <string>

int main(int argc, char** argv) {
  if (argc != 3) return 2;
  constexpr ULong64_t targetEvent = 844424930131968ULL;
  TFile input(argv[1], "READ"), output(argv[2], "CREATE");
  if (input.IsZombie() || output.IsZombie()) return 3;
  int changed = 0;
  TIter keys(input.GetListOfKeys());
  while (auto* item = keys()) {
    auto* key = dynamic_cast<TKey*>(item);
    if (!key) return 4;
    std::unique_ptr<TObject> object(key->ReadObj());
    output.cd();
    auto* tree = dynamic_cast<TTree*>(object.get());
    if (tree && std::string(key->GetName()) == "origins") {
      ULong64_t event = 0; Int_t index = 0, sector = 0, resolution = 0;
      tree->SetBranchAddress("event_id", &event);
      tree->SetBranchAddress("heavy_index", &index);
      tree->SetBranchAddress("sector", &sector);
      tree->SetBranchAddress("resolution", &resolution);
      std::unique_ptr<TTree> copy(tree->CloneTree(0));
      for (Long64_t i = 0; i < tree->GetEntries(); ++i) {
        if (tree->GetEntry(i) <= 0) return 5;
        if (event == targetEvent && index == 22 && sector == 4) {
          resolution = 1; // unresolved origin must not masquerade as unique
          ++changed;
        }
        if (copy->Fill() < 0) return 6;
      }
      if (copy->Write(key->GetName()) <= 0) return 7;
    } else if (tree) {
      std::unique_ptr<TTree> copy(tree->CloneTree(-1, "fast"));
      if (copy->Write(key->GetName()) <= 0) return 8;
    } else if (object->Write(key->GetName()) <= 0) return 9;
  }
  output.Close();
  return changed == 1 ? 0 : 10;
}
