// ListHistos.C
// Usage inside ROOT:
//   .L ListHistos.C
//   ListHistos("ccbar_MONASH_sub0.root");
//   ListHistos("ccbar_JUNCTIONS_sub0.root");

#include "TFile.h"
#include "TKey.h"
#include "TClass.h"
#include "TH1.h"
#include "TH2.h"
#include <iostream>

void ListHistos(const char* filename)
{
    TFile* f = TFile::Open(filename, "READ");
    if (!f || f->IsZombie()) {
        std::cout << "Cannot open file: " << filename << std::endl;
        return;
    }

    std::cout << "\n=== File: " << filename << " ===" << std::endl;

    TIter nextkey(f->GetListOfKeys());
    TKey* key;
    while ((key = (TKey*)nextkey())) {
        TObject* obj = key->ReadObj();
        if (!obj) continue;

        TString cname = obj->ClassName();
        TString oname = obj->GetName();

        if (cname.BeginsWith("TH1") || cname.BeginsWith("TH2")) {
            std::cout << "  " << cname << " : " << oname << std::endl;
        }
    }

    f->Close();
}
