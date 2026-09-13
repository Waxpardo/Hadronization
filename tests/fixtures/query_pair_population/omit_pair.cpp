#include "TFile.h"
#include "TKey.h"
#include "TTree.h"
#include <cstdint>
#include <memory>
#include <string>

int main(int argc, char** argv) {
  if (argc != 6) return 2;
  const auto event = static_cast<ULong64_t>(std::stoull(argv[3]));
  const int trigger = std::stoi(argv[4]);
  const int associate = std::stoi(argv[5]);
  TFile input(argv[1], "READ"), output(argv[2], "CREATE");
  if (input.IsZombie() || output.IsZombie()) return 3;
  int omitted = 0;
  TIter keys(input.GetListOfKeys());
  while (auto* item = keys()) {
    auto* key = dynamic_cast<TKey*>(item);
    if (!key) return 4;
    std::unique_ptr<TObject> object(key->ReadObj());
    output.cd();
    auto* tree = dynamic_cast<TTree*>(object.get());
    if (tree && std::string(key->GetName()) == "pairs") {
      ULong64_t rowEvent = 0;
      Int_t rowTrigger = 0, rowAssociate = 0;
      tree->SetBranchAddress("event_id", &rowEvent);
      tree->SetBranchAddress("trigger_heavy_index", &rowTrigger);
      tree->SetBranchAddress("associate_heavy_index", &rowAssociate);
      std::unique_ptr<TTree> copy(tree->CloneTree(0));
      for (Long64_t i = 0; i < tree->GetEntries(); ++i) {
        if (tree->GetEntry(i) <= 0) return 5;
        if (rowEvent == event && rowTrigger == trigger && rowAssociate == associate) {
          ++omitted;
          continue;
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
  return omitted == 1 ? 0 : 10;
}
