#ifndef HISTOGRAM_ERROR_UTILS_H
#define HISTOGRAM_ERROR_UTILS_H

#include <algorithm>
#include <cmath>

#include "TH1.h"
#include "TH1D.h"
#include "TH2.h"
#include "TString.h"

namespace PlotErrorUtils {

inline void EnsureSumw2(TH1* hist)
{
    if (hist && hist->GetSumw2N() == 0) hist->Sumw2();
}

inline double Integral1DAndError(TH1* hist, int binLow, int binHigh, double& err)
{
    err = 0.0;
    if (!hist) return 0.0;

    EnsureSumw2(hist);
    return hist->IntegralAndError(binLow, binHigh, err);
}

inline double Integral2DAndError(TH2* hist,
                                 int xLow,
                                 int xHigh,
                                 int yLow,
                                 int yHigh,
                                 double& err)
{
    err = 0.0;
    if (!hist) return 0.0;

    EnsureSumw2(hist);
    return hist->IntegralAndError(xLow, xHigh, yLow, yHigh, err);
}

inline double RatioError(double numerator,
                         double numeratorErr,
                         double denominator,
                         double denominatorErr)
{
    if (numerator <= 0.0 || denominator <= 0.0) return 0.0;

    double relVar = 0.0;
    if (numeratorErr > 0.0) relVar += (numeratorErr * numeratorErr) / (numerator * numerator);
    if (denominatorErr > 0.0) relVar += (denominatorErr * denominatorErr) / (denominator * denominator);
    return (numerator / denominator) * std::sqrt(relVar);
}

inline TH1D* BuildRatioHistogram(const TH1D* numeratorSource,
                                 const TH1D* denominatorSource,
                                 const char* name,
                                 const char* yTitle)
{
    if (!numeratorSource || !denominatorSource) return nullptr;

    TH1D* numerator = dynamic_cast<TH1D*>(numeratorSource->Clone(Form("%s_num", name)));
    TH1D* denominator = dynamic_cast<TH1D*>(denominatorSource->Clone(Form("%s_den", name)));
    if (!numerator || !denominator) {
        delete numerator;
        delete denominator;
        return nullptr;
    }

    numerator->SetDirectory(nullptr);
    denominator->SetDirectory(nullptr);
    EnsureSumw2(numerator);
    EnsureSumw2(denominator);

    TH1D* ratio = dynamic_cast<TH1D*>(numerator->Clone(name));
    if (!ratio) {
        delete numerator;
        delete denominator;
        return nullptr;
    }

    ratio->SetDirectory(nullptr);
    ratio->Reset("ICES");
    EnsureSumw2(ratio);
    ratio->GetXaxis()->SetTitle(numerator->GetXaxis()->GetTitle());
    ratio->GetYaxis()->SetTitle(yTitle);
    ratio->Divide(numerator, denominator, 1.0, 1.0);

    delete numerator;
    delete denominator;
    return ratio;
}

inline void NormalizeToUnitShape(TH1D* hist)
{
    if (!hist) return;

    EnsureSumw2(hist);
    const int nBins = hist->GetNbinsX();
    const double total = hist->Integral(1, nBins);
    if (total <= 0.0) return;

    for (int bin = 1; bin <= nBins; ++bin) {
        const double count = hist->GetBinContent(bin);
        const double probability = count / total;
        const double remainder = std::max(0.0, total - count);
        const double variance = (count > 0.0 ? (count * remainder) / (total * total * total) : 0.0);
        hist->SetBinContent(bin, probability);
        hist->SetBinError(bin, std::sqrt(std::max(0.0, variance)));
    }
}

} // namespace PlotErrorUtils

#endif
