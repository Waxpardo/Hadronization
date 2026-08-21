// ---------------------------------------------------------------------------
// Build_HF_AllHistogramSubsampleFile.C
//
// Combine the analyzed heavy-flavour subsample ROOT files into one broad
// inspection file. Unlike Build_HF_CombinedSubsamplesFile.C, which creates a
// compact plot-ready subset, this macro preserves every TH1/TH2/TH3 histogram
// found in the analyzed subsamples.
//
// Output layout:
//   <Flavor>/<Tune>/Metadata
//   <Flavor>/<Tune>/AllHistograms/Sum
//   <Flavor>/<Tune>/AllHistograms/SubsampleMean
//   <Flavor>/<Tune>/AllHistograms/SubsampleSumWithSEM
//   <Flavor>/<Tune>/Correlations/DeltaRapidityDeltaPhi
//
// Sum:
//   bin content = sum over available subsamples.
//
// SubsampleMean:
//   bin content = mean across subsamples, bin error = SEM.
//
// SubsampleSumWithSEM:
//   bin content = sum over available subsamples,
//   bin error   = nSubAvailable * SEM across subsamples.
//
// The correlation section is intentionally generic. If future analyzed files
// contain TH2/TH3 histograms with eta/y/rapidity and phi axes or names, those
// histograms are copied there in addition to the all-histogram directories.
// Current 08-04-2026 analyzed files contain pT-vs-multiplicity TH2 histograms
// but do not yet contain Delta-y/Delta-phi or Delta-eta/Delta-phi pairs, so the
// macro records that absence in metadata instead of fabricating correlations.
//
// Usage (from the repo root):
//
//   Shell one-liner (ACLiC compiled):
//     root -l -b -q 'plotting/PtMultiplicity/Build_HF_AllHistogramSubsampleFile.C+("08-04-2026_100M_Separate",10)'
//
//   Interactive ROOT shell:
//     .L "plotting/PtMultiplicity/Build_HF_AllHistogramSubsampleFile.C"
//     runHFAllHistogramSubsampleFile("08-04-2026_100M_Combined", 10);
//     runHFAllHistogramSubsampleFile("08-04-2026_100M_Separate", 10);
//     runHFAllHistogramSubsampleFile("27-03-2026", 10,
//                                    "AnalyzedData/27-03-2026/custom.root");
// ---------------------------------------------------------------------------

#include <algorithm>
#include <cmath>
#include <iostream>
#include <set>
#include <string>
#include <vector>

#include "TClass.h"
#include "TDirectory.h"
#include "TFile.h"
#include "TH1.h"
#include "TH2.h"
#include "TH3.h"
#include "TKey.h"
#include "TNamed.h"
#include "TROOT.h"
#include "TString.h"
#include "TSystem.h"
#include "TObjString.h"

#include "PlottingPathUtils.h"
#include "../HistogramErrorUtils.h"

namespace {

struct PlotPathBootstrap {
    PlotPathBootstrap() { PlotPathUtils::RegisterMacroPath(__FILE__); }
} gPlotPathBootstrap;

struct SampleFile {
    TFile* file;
    TString path;

    SampleFile() : file(nullptr), path("") {}
};

struct CombineStats {
    int nHistograms;
    int nTH1;
    int nTH2;
    int nTH3;
    int nCorrelations;
    int nSkipped;

    CombineStats()
        : nHistograms(0), nTH1(0), nTH2(0), nTH3(0), nCorrelations(0), nSkipped(0)
    {}
};

TDirectory* EnsureSubDir(TDirectory* parent, const char* name)
{
    if (!parent || !name || name[0] == '\0') return nullptr;

    if (TDirectory* existing = parent->GetDirectory(name)) return existing;
    return parent->mkdir(name);
}

void WriteNamed(TDirectory* dir, const char* name, const char* title)
{
    if (!dir) return;
    dir->cd();
    TNamed named(name, title ? title : "");
    named.Write();
}

TString CleanPathPart(const TString& input)
{
    TString cleaned = input;
    cleaned.ReplaceAll("\\", "_");
    cleaned.ReplaceAll(":", "_");
    cleaned.ReplaceAll(";", "_");
    cleaned.ReplaceAll(" ", "_");
    return cleaned;
}

TDirectory* EnsurePath(TDirectory* rootDir, const TString& relPath)
{
    if (!rootDir) return nullptr;

    TString path = relPath;
    path = path.Strip(TString::kBoth, '/');
    if (path.IsNull()) return rootDir;

    TDirectory* current = rootDir;
    TObjArray* parts = path.Tokenize("/");
    if (!parts) return current;

    for (int i = 0; i < parts->GetEntriesFast(); ++i) {
        TObjString* partObj = dynamic_cast<TObjString*>(parts->At(i));
        if (!partObj) continue;
        TString part = CleanPathPart(partObj->GetString());
        if (part.IsNull()) continue;
        current = EnsureSubDir(current, part.Data());
        if (!current) break;
    }

    delete parts;
    return current;
}

TString DirPart(const TString& relPath)
{
    const Ssiz_t slash = relPath.Last('/');
    if (slash == kNPOS) return TString("");
    TString dir = relPath;
    dir.Remove(slash);
    return dir;
}

TString BasePart(const TString& relPath)
{
    const Ssiz_t slash = relPath.Last('/');
    if (slash == kNPOS) return CleanPathPart(relPath);
    TString base = relPath;
    base.Remove(0, slash + 1);
    return CleanPathPart(base);
}

void WriteHistogramAtPath(TDirectory* parent, TH1* hist, const TString& relPath)
{
    if (!parent || !hist) return;

    TDirectory* targetDir = EnsurePath(parent, DirPart(relPath));
    if (!targetDir) return;

    targetDir->cd();
    hist->SetName(BasePart(relPath).Data());
    hist->Write();
}

TString LowerNoSpace(const TString& input)
{
    TString lower = input;
    lower.ToLower();
    lower.ReplaceAll(" ", "");
    lower.ReplaceAll("_", "");
    lower.ReplaceAll("-", "");
    return lower;
}

bool ContainsAny(const TString& text, const std::vector<TString>& tokens)
{
    for (const TString& token : tokens) {
        if (text.Contains(token)) return true;
    }
    return false;
}

TString HistogramSearchText(const TH1* hist, const TString& relPath)
{
    TString text = relPath;
    if (hist) {
        text += " ";
        text += hist->GetName();
        text += " ";
        text += hist->GetTitle();
        text += " ";
        text += hist->GetXaxis() ? hist->GetXaxis()->GetTitle() : "";
        text += " ";
        text += hist->GetYaxis() ? hist->GetYaxis()->GetTitle() : "";
        if (hist->GetDimension() >= 3) {
            text += " ";
            text += hist->GetZaxis() ? hist->GetZaxis()->GetTitle() : "";
        }
    }
    return LowerNoSpace(text);
}

bool LooksLikeRapidityPhiCorrelation(const TH1* hist, const TString& relPath)
{
    if (!hist || hist->GetDimension() < 2) return false;

    const TString text = HistogramSearchText(hist, relPath);
    const bool hasPhi = ContainsAny(text, {"phi", "#phi", "dphi", "deltaphi", "#delta#phi"});
    const bool hasRapidity =
        ContainsAny(text, {"eta", "#eta", "rapidity", "dy", "deta", "deltay", "deltaeta", "#delta#eta"});
    const bool hasCorrelation =
        ContainsAny(text, {"corr", "correlation", "delta", "#delta", "dphi", "deta", "dy"});

    return hasPhi && hasRapidity && hasCorrelation;
}

bool IsSupportedHistogram(const TObject* obj)
{
    const TH1* hist = dynamic_cast<const TH1*>(obj);
    if (!hist) return false;
    const int dim = hist->GetDimension();
    return dim >= 1 && dim <= 3;
}

void CollectHistogramPaths(TDirectory* dir,
                           const TString& prefix,
                           std::vector<TString>& paths)
{
    if (!dir) return;

    TIter next(dir->GetListOfKeys());
    while (TObject* keyObj = next()) {
        TKey* key = dynamic_cast<TKey*>(keyObj);
        if (!key) continue;

        TObject* obj = key->ReadObj();
        if (!obj) continue;

        const TString name = key->GetName();
        const TString relPath = prefix.IsNull() ? name : prefix + "/" + name;

        if (obj->InheritsFrom(TDirectory::Class())) {
            CollectHistogramPaths(dynamic_cast<TDirectory*>(obj), relPath, paths);
        } else if (IsSupportedHistogram(obj)) {
            paths.push_back(relPath);
        }

        delete obj;
    }
}

std::vector<TString> UniqueSortedHistogramPaths(const std::vector<SampleFile>& samples)
{
    std::vector<TString> paths;
    for (const SampleFile& sample : samples) {
        if (!sample.file) continue;
        CollectHistogramPaths(sample.file, "", paths);
    }

    std::sort(paths.begin(), paths.end());
    paths.erase(std::unique(paths.begin(), paths.end()), paths.end());
    return paths;
}

TH1* GetHistogram(TFile* file, const TString& relPath)
{
    if (!file) return nullptr;
    return dynamic_cast<TH1*>(file->Get(relPath.Data()));
}

bool CompatibleAxes(const TH1* ref, const TH1* other)
{
    if (!ref || !other) return false;
    if (ref->GetDimension() != other->GetDimension()) return false;
    if (ref->GetNbinsX() != other->GetNbinsX()) return false;
    if (ref->GetXaxis()->GetXmin() != other->GetXaxis()->GetXmin()) return false;
    if (ref->GetXaxis()->GetXmax() != other->GetXaxis()->GetXmax()) return false;

    if (ref->GetDimension() >= 2) {
        if (ref->GetNbinsY() != other->GetNbinsY()) return false;
        if (ref->GetYaxis()->GetXmin() != other->GetYaxis()->GetXmin()) return false;
        if (ref->GetYaxis()->GetXmax() != other->GetYaxis()->GetXmax()) return false;
    }

    if (ref->GetDimension() >= 3) {
        if (ref->GetNbinsZ() != other->GetNbinsZ()) return false;
        if (ref->GetZaxis()->GetXmin() != other->GetZaxis()->GetXmin()) return false;
        if (ref->GetZaxis()->GetXmax() != other->GetZaxis()->GetXmax()) return false;
    }

    return true;
}

TH1* CloneEmptyLike(const TH1* ref, const char* name, const char* titleSuffix)
{
    if (!ref) return nullptr;

    TH1* clone = dynamic_cast<TH1*>(ref->Clone(name));
    if (!clone) return nullptr;

    clone->SetDirectory(nullptr);
    clone->Reset("ICES");
    PlotErrorUtils::EnsureSumw2(clone);

    TString title = ref->GetTitle();
    if (titleSuffix && titleSuffix[0] != '\0') {
        if (!title.IsNull()) title += " ";
        title += titleSuffix;
    }
    clone->SetTitle(title.Data());
    return clone;
}

TH1* BuildSummedHistogram(const std::vector<TH1*>& hists,
                          const TString& relPath)
{
    TH1* ref = nullptr;
    for (TH1* hist : hists) {
        if (hist) {
            ref = hist;
            break;
        }
    }
    if (!ref) return nullptr;

    TH1* summed = CloneEmptyLike(ref, BasePart(relPath).Data(), "(sum over subsamples)");
    if (!summed) return nullptr;

    for (TH1* hist : hists) {
        if (!hist) continue;
        PlotErrorUtils::EnsureSumw2(hist);
        summed->Add(hist);
    }

    return summed;
}

TH1* BuildSubsampleStatisticHistogram(const std::vector<TH1*>& hists,
                                      const TString& relPath,
                                      bool scaleToAvailableSubsampleSum)
{
    TH1* ref = nullptr;
    for (TH1* hist : hists) {
        if (hist) {
            ref = hist;
            break;
        }
    }
    if (!ref) return nullptr;

    const char* suffix = scaleToAvailableSubsampleSum
        ? "(sum with subsample SEM as bin errors)"
        : "(subsample mean with SEM as bin errors)";
    TH1* out = CloneEmptyLike(ref, BasePart(relPath).Data(), suffix);
    if (!out) return nullptr;

    const int nCells = ref->GetNcells();
    for (int globalBin = 0; globalBin < nCells; ++globalBin) {
        std::vector<double> values;
        values.reserve(hists.size());

        for (TH1* hist : hists) {
            if (!hist) continue;
            values.push_back(hist->GetBinContent(globalBin));
        }

        if (values.empty()) continue;

        double mean = 0.0;
        for (double value : values) mean += value;
        mean /= static_cast<double>(values.size());

        double sem = 0.0;
        if (values.size() > 1) {
            double var = 0.0;
            for (double value : values) var += (value - mean) * (value - mean);
            sem = std::sqrt(var / (values.size() * (values.size() - 1)));
        }

        const double scale = scaleToAvailableSubsampleSum
            ? static_cast<double>(values.size())
            : 1.0;
        out->SetBinContent(globalBin, scale * mean);
        out->SetBinError(globalBin, scale * sem);
    }

    return out;
}

TString ResolvePrefixForFlavor(const TString& dateTag,
                               const TString& flavorTag,
                               const char* tuneTag)
{
    if (flavorTag == "Charm") {
        return PlotPathUtils::ResolveAnalyzedPrefix(
            dateTag,
            "Charm",
            {TString::Format("hf_%s_sub", tuneTag),
             TString::Format("ccbar_%s_sub", tuneTag)}
        );
    }

    return PlotPathUtils::ResolveAnalyzedPrefix(
        dateTag,
        "Beauty",
        {TString::Format("hf_%s_sub", tuneTag),
         TString::Format("bbbar_%s_sub", tuneTag)}
    );
}

bool LoadSampleFiles(const TString& prefix,
                     int nSub,
                     std::vector<SampleFile>& samples)
{
    samples.assign(nSub, SampleFile());

    bool openedAny = false;
    for (int iSub = 0; iSub < nSub; ++iSub) {
        const TString fileName = TString::Format("%s%d.root", prefix.Data(), iSub);
        TFile* file = TFile::Open(fileName, "READ");
        if (!file || file->IsZombie()) {
            std::cout << "Missing or unreadable subsample: " << fileName << "\n";
            if (file) {
                file->Close();
                delete file;
            }
            continue;
        }

        samples[iSub].file = file;
        samples[iSub].path = fileName;
        openedAny = true;
    }

    return openedAny;
}

void CloseSampleFiles(std::vector<SampleFile>& samples)
{
    for (SampleFile& sample : samples) {
        if (!sample.file) continue;
        sample.file->Close();
        delete sample.file;
        sample.file = nullptr;
    }
}

void WriteInputFileMetadata(TDirectory* metadataDir,
                            const std::vector<SampleFile>& samples)
{
    TDirectory* inputDir = EnsureSubDir(metadataDir, "InputFiles");
    if (!inputDir) return;

    for (size_t i = 0; i < samples.size(); ++i) {
        const TString name = TString::Format("sub%zu", i);
        const TString path = samples[i].file ? samples[i].path : TString("MISSING");
        WriteNamed(inputDir, name.Data(), path.Data());
    }
}

void CountDimension(CombineStats& stats, const TH1* hist)
{
    if (!hist) return;
    ++stats.nHistograms;
    if (hist->GetDimension() == 1) ++stats.nTH1;
    else if (hist->GetDimension() == 2) ++stats.nTH2;
    else if (hist->GetDimension() == 3) ++stats.nTH3;
}

void WriteStatsMetadata(TDirectory* metadataDir, const CombineStats& stats)
{
    WriteNamed(metadataDir,
               "HistogramCount",
               TString::Format("%d total, %d TH1, %d TH2, %d TH3",
                               stats.nHistograms,
                               stats.nTH1,
                               stats.nTH2,
                               stats.nTH3).Data());
    WriteNamed(metadataDir,
               "CorrelationCandidateCount",
               TString::Format("%d", stats.nCorrelations).Data());
    WriteNamed(metadataDir,
               "SkippedHistogramCount",
               TString::Format("%d", stats.nSkipped).Data());
}

bool BuildFlavorTuneContent(const TString& dateTag,
                            const TString& flavorTag,
                            const char* tuneTag,
                            int nSub,
                            TDirectory* outFile)
{
    const TString prefix = ResolvePrefixForFlavor(dateTag, flavorTag, tuneTag);
    if (prefix.IsNull()) {
        std::cout << "Could not resolve input prefix for " << flavorTag
                  << ", " << tuneTag << "\n";
        return false;
    }

    std::vector<SampleFile> samples;
    if (!LoadSampleFiles(prefix, nSub, samples)) {
        std::cout << "No readable subsamples for " << flavorTag
                  << " " << tuneTag << "\n";
        return false;
    }

    TDirectory* flavorDir = EnsureSubDir(outFile, flavorTag.Data());
    TDirectory* tuneDir = EnsureSubDir(flavorDir, tuneTag);
    TDirectory* metadataDir = EnsureSubDir(tuneDir, "Metadata");
    TDirectory* allDir = EnsureSubDir(tuneDir, "AllHistograms");
    TDirectory* sumDir = EnsureSubDir(allDir, "Sum");
    TDirectory* meanDir = EnsureSubDir(allDir, "SubsampleMean");
    TDirectory* sumSemDir = EnsureSubDir(allDir, "SubsampleSumWithSEM");
    TDirectory* correlationDir = EnsureSubDir(tuneDir, "Correlations");
    TDirectory* dyDphiDir = EnsureSubDir(correlationDir, "DeltaRapidityDeltaPhi");
    TDirectory* dyDphiSumSemDir = EnsureSubDir(dyDphiDir, "SubsampleSumWithSEM");
    TDirectory* dyDphiSumDir = EnsureSubDir(dyDphiDir, "Sum");

    WriteNamed(metadataDir, "DateTag", dateTag.Data());
    WriteNamed(metadataDir, "TuneTag", tuneTag);
    WriteNamed(metadataDir, "FlavorTag", flavorTag.Data());
    WriteNamed(metadataDir, "InputPrefix", prefix.Data());
    WriteNamed(metadataDir,
               "ReferenceMotivation",
               "Two-particle correlation references motivate C(Delta eta,Delta phi) "
               "or C(Delta y,Delta phi) TH2 histograms and optional TH3 histograms "
               "differential in pT, multiplicity, or another event/particle variable.");
    WriteNamed(metadataDir,
               "SubsampleUncertaintyRule",
               "SubsampleMean uses mean+-SEM per bin. SubsampleSumWithSEM stores "
               "the available-subsample sum with nAvailable*SEM as the bin error.");
    WriteInputFileMetadata(metadataDir, samples);

    const std::vector<TString> paths = UniqueSortedHistogramPaths(samples);
    CombineStats stats;

    for (const TString& path : paths) {
        std::vector<TH1*> hists;
        hists.reserve(samples.size());

        TH1* refHist = nullptr;
        bool incompatible = false;

        for (const SampleFile& sample : samples) {
            TH1* hist = GetHistogram(sample.file, path);
            if (!hist) continue;

            if (!refHist) {
                refHist = hist;
            } else if (!CompatibleAxes(refHist, hist)) {
                incompatible = true;
                break;
            }
            hists.push_back(hist);
        }

        if (!refHist || incompatible) {
            ++stats.nSkipped;
            std::cout << "Skipping incompatible or missing histogram path: "
                      << path << "\n";
            continue;
        }

        CountDimension(stats, refHist);

        TH1* summed = BuildSummedHistogram(hists, path);
        TH1* mean = BuildSubsampleStatisticHistogram(hists, path, false);
        TH1* sumWithSem = BuildSubsampleStatisticHistogram(hists, path, true);

        if (summed) WriteHistogramAtPath(sumDir, summed, path);
        if (mean) WriteHistogramAtPath(meanDir, mean, path);
        if (sumWithSem) WriteHistogramAtPath(sumSemDir, sumWithSem, path);

        if (LooksLikeRapidityPhiCorrelation(refHist, path)) {
            ++stats.nCorrelations;
            if (summed) WriteHistogramAtPath(dyDphiSumDir, summed, path);
            if (sumWithSem) WriteHistogramAtPath(dyDphiSumSemDir, sumWithSem, path);
        }

        delete summed;
        delete mean;
        delete sumWithSem;
    }

    if (stats.nCorrelations == 0) {
        WriteNamed(dyDphiDir,
                   "NoRapidityPhiCorrelationInputsFound",
                   "No TH2/TH3 histogram in the analyzed subsamples had eta/y/rapidity "
                   "and phi correlation labels or axes. The current reduced analyzed "
                   "files cannot reconstruct the attached-reference-style Delta-y/Delta-phi "
                   "or Delta-eta/Delta-phi surfaces; future analysis outputs with those "
                   "histograms will be combined here automatically.");
    }

    WriteStatsMetadata(metadataDir, stats);
    CloseSampleFiles(samples);
    return stats.nHistograms > 0;
}

TString DefaultOutputPath(const TString& dateTag)
{
    return PlotPathUtils::GetAnalyzedDataDir() + "/" + dateTag
         + "/hf_all_combined_histograms.root";
}

} // namespace

void runHFAllHistogramSubsampleFile(const char* dateTag = "",
                                    int nSub = 10,
                                    const char* outputPath = "")
{
    gROOT->SetBatch(kTRUE);

    const TString resolvedDate = PlotPathUtils::ResolveAnalysisDate(dateTag);
    if (resolvedDate.IsNull()) return;

    TString outPath = outputPath ? TString(outputPath) : TString("");
    outPath = outPath.Strip(TString::kBoth);
    if (outPath.IsNull()) outPath = DefaultOutputPath(resolvedDate);

    if (!gSystem->IsAbsoluteFileName(outPath.Data())) {
        outPath = gSystem->ConcatFileName(gSystem->WorkingDirectory(), outPath.Data());
    }
    outPath = gSystem->UnixPathName(outPath);

    const TString outDir = gSystem->DirName(outPath.Data());
    gSystem->mkdir(outDir, true);

    TFile* outFile = TFile::Open(outPath, "RECREATE");
    if (!outFile || outFile->IsZombie()) {
        std::cout << "Could not create output file: " << outPath << "\n";
        if (outFile) {
            outFile->Close();
            delete outFile;
        }
        return;
    }

    WriteNamed(outFile,
               "FileDescription",
               "All TH1/TH2/TH3 histograms from analyzed heavy-flavour subsamples, "
               "combined as raw sums and as subsample-uncertainty histograms.");
    WriteNamed(outFile,
               "CorrelationReference",
               "Designed to carry reference-style Delta-y/Delta-phi or Delta-eta/Delta-phi "
               "TH2 surfaces and optional TH3 differential correlations when those histograms "
               "exist in the analyzed subsample inputs.");

    bool wroteAnything = false;
    wroteAnything |= BuildFlavorTuneContent(resolvedDate, "Charm", "MONASH", nSub, outFile);
    wroteAnything |= BuildFlavorTuneContent(resolvedDate, "Charm", "JUNCTIONS", nSub, outFile);
    wroteAnything |= BuildFlavorTuneContent(resolvedDate, "Charm", "CLOSEPACKING", nSub, outFile);
    wroteAnything |= BuildFlavorTuneContent(resolvedDate, "Beauty", "MONASH", nSub, outFile);
    wroteAnything |= BuildFlavorTuneContent(resolvedDate, "Beauty", "JUNCTIONS", nSub, outFile);
    wroteAnything |= BuildFlavorTuneContent(resolvedDate, "Beauty", "CLOSEPACKING", nSub, outFile);

    outFile->Write();
    outFile->Close();
    delete outFile;

    if (wroteAnything) {
        std::cout << "Wrote combined all-histogram file to:\n  "
                  << outPath << "\n";
    } else {
        std::cout << "No content was written to " << outPath << "\n";
    }
}

// Filename-matching entry point so ACLiC + syntax works from the shell:
//   root -l -b -q 'plotting/PtMultiplicity/Build_HF_AllHistogramSubsampleFile.C+("08-04-2026_100M_Separate",10)'
void Build_HF_AllHistogramSubsampleFile(const char* dateTag = "",
                                        int nSub = 10,
                                        const char* outPath = "")
{
    runHFAllHistogramSubsampleFile(dateTag, nSub, outPath);
}
