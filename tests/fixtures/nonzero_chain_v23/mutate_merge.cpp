#include "TFile.h"
#include "TAxis.h"
#include "THnSparse.h"
#include "TKey.h"

#include <memory>
#include <string>
#include <vector>

int main(int argc, char** argv) {
  if (argc != 5) return 2;
  TFile input(argv[1], "READ"), output(argv[2], "CREATE");
  if (input.IsZombie() || output.IsZombie()) return 3;
  const std::string target = argv[3], mode = argv[4];
  TIter keys(input.GetListOfKeys());
  while (auto* item = keys()) {
    auto* key = dynamic_cast<TKey*>(item);
    std::unique_ptr<TObject> object(key->ReadObj());
    if (target == key->GetName()) {
      auto* histogram = dynamic_cast<THnSparseD*>(object.get());
      if (!histogram) return 4;
      if (mode == "content") {
        histogram->SetBinContent(Long64_t{0}, histogram->GetBinContent(Long64_t{0}) + 1.0);
      } else if (mode == "sumw2") {
        histogram->SetBinError2(0, histogram->GetBinError2(0) + 1.0);
      } else if (mode == "entries") {
        histogram->SetEntries(histogram->GetEntries() + 1.0);
      } else if (mode == "coordinate") {
        std::unique_ptr<THnSparseD> replacement(
            dynamic_cast<THnSparseD*>(histogram->Clone()));
        replacement->Reset();
        replacement->Sumw2();
        std::vector<int> coordinates(histogram->GetNdimensions());
        for (Long64_t bin = 0; bin < histogram->GetNbins(); ++bin) {
          const double value = histogram->GetBinContent(bin, coordinates.data());
          const double variance = histogram->GetBinError2(bin);
          if (bin == 0)
            coordinates.back() = histogram->GetAxis(histogram->GetNdimensions() - 1)->GetNbins() + 1;
          const Long64_t destination = replacement->GetBin(coordinates.data(), true);
          replacement->SetBinContent(destination, value);
          replacement->SetBinError2(destination, variance);
        }
        replacement->SetEntries(histogram->GetEntries());
        object.reset(replacement.release());
      } else {
        return 5;
      }
    }
    output.cd();
    if (object->Write(key->GetName()) <= 0) return 6;
  }
  output.Close();
  return 0;
}
