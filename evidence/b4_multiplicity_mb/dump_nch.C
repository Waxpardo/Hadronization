// Dump an MB N_ch histogram to CSV so the percentile table can be recomputed
// without ROOT.
//
// USE BIN CENTRES, NOT LOW EDGES. The axis is [-0.5, 399.5] with unit bins, so
// bin 1 is N_ch = 0 and its LOW EDGE is -0.5. Labelling by low edge and
// rounding turns N_ch = 0 into "-1", which silently moves 872 MONASH events out
// of the first class. That is the same half-integer-edge trap the boundary
// derivation already recorded once (FindBin on a half-integer edge); it is
// written down here because it bit a second time.
void dump_nch(const char* in, const char* out){
  TFile f(in);
  TList* keys = f.GetListOfKeys();
  TIter it(keys); TKey* k; TH1* h = nullptr; TString hname;
  while((k=(TKey*)it())){
    TObject* o = f.Get(k->GetName());
    if(o && o->InheritsFrom("TH1")){ h=(TH1*)o; hname=k->GetName(); break; }
  }
  if(!h){ printf("NO_TH1 in %s\n", in); return; }
  if(h->GetBinContent(0)!=0 || h->GetBinContent(h->GetNbinsX()+1)!=0){
    printf("REFUSING %s: under/overflow is non-zero and would be dropped\n", in);
    return;
  }
  FILE* fp = fopen(out,"w");
  fprintf(fp,"nch,count\n");
  double tot=0;
  for(int i=1;i<=h->GetNbinsX();++i){
    double c=h->GetBinContent(i);
    if(c!=0) fprintf(fp,"%d,%.17g\n",(int)llround(h->GetBinCenter(i)),c);
    tot+=c;
  }
  fclose(fp);
  printf("DUMPED %s hist=%s entries=%.0f integral=%.0f\n",
         out, hname.Data(), h->GetEntries(), tot);
}
