void setCanvasMargins(TCanvas *canvas, double_t LeftMargin, double_t RightMargin, double_t TopMargin, double_t BottomMargin) {
  canvas->SetLeftMargin(LeftMargin);
  canvas->SetRightMargin(RightMargin);
  canvas->SetTopMargin(TopMargin);
  canvas->SetBottomMargin(BottomMargin);
}

int reproduceCanvasPadError() {

// Create canvas
TCanvas* canvas = new TCanvas("canvas", "canvas", 800, 600);

 Double_t eps = 0.03; // Adjust this value as needed

// Set pad coordinates
Double_t x1_c00 = 0.05;
Double_t x2_c00 = 0.50;
Double_t y1_c00 = 0.60;
Double_t y2_c00 = 1.0;

Double_t x1_c01 = 0.50;
Double_t x2_c01 = 0.95;
Double_t y1_c01 = 0.60;
Double_t y2_c01 = 1.0;

Double_t x1_c10 = 0.05;
Double_t x2_c10 = 0.50;
Double_t y1_c10 = 0.20;
Double_t y2_c10 = 0.60;

Double_t x1_c11 = 0.50;
Double_t x2_c11 = 0.95;
Double_t y1_c11 = 0.20;
Double_t y2_c11 = 0.60;

Double_t x1_c20mini = 0.05;
Double_t x2_c20mini = 0.50;
Double_t y1_c20mini = 0.10;
Double_t y2_c20mini = 0.20;

Double_t x1_c21mini = 0.50;
Double_t x2_c21mini = 0.95;
Double_t y1_c21mini = 0.10;
Double_t y2_c21mini = 0.20;

// Create pads
TPad* c00_yields = new TPad("c00_yields", "yields for JUNCTIONS beauty", x1_c00, y1_c00, x2_c00, y2_c00);
TPad* c01_yields = new TPad("c01_yields", "yields for JUNCTIONS beauty", x1_c01, y1_c01, x2_c01, y2_c01);
TPad* c10_yields = new TPad("c10_yields", "yields for MONASH charm", x1_c10, y1_c10, x2_c10, y2_c10);
TPad* c11_yields = new TPad("c11_yields", "yields for MONASH charm", x1_c11, y1_c11, x2_c11, y2_c11);
TPad* c20mini_yields = new TPad("c20mini_yields", "yields ratio for beauty", x1_c20mini, y1_c20mini, x2_c20mini, y2_c20mini);
TPad* c21mini_yields = new TPad("c21mini_yields", "yields ratio for charm", x1_c21mini, y1_c21mini, x2_c21mini, y2_c21mini);

// Set margins
c00_yields->SetRightMargin(eps);
c01_yields->SetLeftMargin(eps);
c10_yields->SetRightMargin(eps);
c11_yields->SetLeftMargin(eps);
c20mini_yields->SetRightMargin(eps);
c21mini_yields->SetLeftMargin(eps);

 c00_yields->SetTopMargin(0);
 c00_yields->SetBottomMargin(0);
 c01_yields->SetTopMargin(0);
 c01_yields->SetBottomMargin(0);
 c10_yields->SetTopMargin(0);
 c10_yields->SetBottomMargin(0);
 c11_yields->SetTopMargin(0);
 c11_yields->SetBottomMargin(0);
 c20mini_yields->SetTopMargin(0);
 c20mini_yields->SetBottomMargin(0);
 c21mini_yields->SetTopMargin(0);
 c21mini_yields->SetBottomMargin(0);

// Draw pads
canvas->cd();
c00_yields->Draw();
c01_yields->Draw();
c10_yields->Draw();
c11_yields->Draw();
c20mini_yields->Draw();
c21mini_yields->Draw();

// Fill histograms
TH1F* histogram_c00 = new TH1F("histogram_c00", "Histogram for c00", 10, 0, 11);
TH1F* histogram_c01 = new TH1F("histogram_c01", "Histogram for c01", 10, 0, 11);
TH1F* histogram_c10 = new TH1F("histogram_c10", "Histogram for c10", 10, 0, 11);
TH1F* histogram_c11 = new TH1F("histogram_c11", "Histogram for c11", 10, 0, 11);
TH1F* histogram_c20mini = new TH1F("histogram_c20mini", "Histogram for c20mini", 10, 0, 11);
TH1F* histogram_c21mini = new TH1F("histogram_c21mini", "Histogram for c21mini", 10, 0, 11);

// Fill histograms with random data
histogram_c00->FillRandom("gaus", 1000);
histogram_c01->FillRandom("expo", 1000);
histogram_c10->FillRandom("gaus", 1000);
histogram_c11->FillRandom("expo", 1000);
histogram_c20mini->FillRandom("gaus", 1000);
histogram_c21mini->FillRandom("expo", 1000);

// Draw histograms
c00_yields->cd();
histogram_c00->Draw();

c01_yields->cd();
histogram_c01->Draw();

c10_yields->cd();
histogram_c10->Draw();

c11_yields->cd();
histogram_c11->Draw();

c20mini_yields->cd();
histogram_c20mini->Draw();

c21mini_yields->cd();
histogram_c21mini->Draw();

// Update canvas
canvas->Update();
 
  

  
  
  return 0;

}
