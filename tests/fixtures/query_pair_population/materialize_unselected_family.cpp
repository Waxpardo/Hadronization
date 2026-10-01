#include "TFile.h"
#include "TKey.h"
#include "TTree.h"
#include <memory>
#include <string>

// TEST_ONLY: expose one unselected vector and one unselected baryon excitation
// inside acceptance. Their cached selected/pair-eligible flags remain zero and
// no legacy pair rows are added; v2.3 must reconstruct them from retained rows.
int main(int argc, char** argv) {
  if (argc != 3) return 2;
  constexpr ULong64_t targetEvent = 844424930131968ULL;
  TFile input(argv[1], "READ"), output(argv[2], "CREATE");
  if (input.IsZombie() || output.IsZombie()) return 3;
  int vectorChanged = 0, baryonChanged = 0;
  TIter keys(input.GetListOfKeys());
  while (auto* item = keys()) {
    auto* key = dynamic_cast<TKey*>(item);
    if (!key) return 4;
    std::unique_ptr<TObject> object(key->ReadObj());
    output.cd();
    auto* tree = dynamic_cast<TTree*>(object.get());
    const std::string name = key->GetName();
    if (tree && name == "heavy") {
      ULong64_t event = 0;
      Int_t index = 0, pdg = 0;
      UChar_t selected = 0, pairEligible = 0;
      Double_t eta = 0;
      tree->SetBranchAddress("event_id", &event);
      tree->SetBranchAddress("heavy_index", &index);
      tree->SetBranchAddress("pdg", &pdg);
      tree->SetBranchAddress("selected", &selected);
      tree->SetBranchAddress("pair_eligible", &pairEligible);
      tree->SetBranchAddress("eta", &eta);
      std::unique_ptr<TTree> copy(tree->CloneTree(0));
      for (Long64_t i = 0; i < tree->GetEntries(); ++i) {
        if (tree->GetEntry(i) <= 0) return 5;
        if (event == targetEvent && index == 30) {
          if (selected || pairEligible) return 6;
          pdg = 423; eta = 0.4; ++vectorChanged;
        } else if (event == targetEvent && index == 32) {
          if (selected || pairEligible) return 7;
          pdg = 4334; eta = 0.6; ++baryonChanged;
        }
        if (copy->Fill() < 0) return 8;
      }
      if (copy->Write(name.c_str()) <= 0) return 9;
    } else if (tree) {
      std::unique_ptr<TTree> copy(tree->CloneTree(-1, "fast"));
      if (copy->Write(name.c_str()) <= 0) return 10;
    } else if (object->Write(name.c_str()) <= 0) return 11;
  }
  output.Close();
  return vectorChanged == 1 && baryonChanged == 1 ? 0 : 12;
}
