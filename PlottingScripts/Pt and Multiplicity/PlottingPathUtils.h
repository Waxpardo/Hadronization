#ifndef PLOTTING_PATH_UTILS_H
#define PLOTTING_PATH_UTILS_H

#include <cstdio>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>

#include "TCollection.h"
#include "TList.h"
#include "TObject.h"
#include "TString.h"
#include "TSystem.h"
#include "TSystemDirectory.h"
#include "TSystemFile.h"

namespace PlotPathUtils {

inline TString& RegisteredMacroBaseDir()
{
    static TString baseDir = "";
    return baseDir;
}

inline TString ResolveAbsolutePath(const char* path)
{
    TString resolved = path ? TString(path) : TString("");
    resolved = resolved.Strip(TString::kBoth);
    if (resolved.Length() == 0) return TString("");

    if (!gSystem->IsAbsoluteFileName(resolved.Data())) {
        resolved = gSystem->ConcatFileName(gSystem->WorkingDirectory(), resolved.Data());
    }

    return gSystem->UnixPathName(resolved);
}

inline TString BaseDirFromMacroPath(const char* macroPath)
{
    TString resolved = ResolveAbsolutePath(macroPath);
    if (resolved.Length() == 0) return TString("");

    TString level1 = gSystem->DirName(resolved.Data()); // Pt and Multiplicity
    TString level2 = gSystem->DirName(level1.Data());   // PlottingScripts
    TString level3 = gSystem->DirName(level2.Data());   // Hadronization
    return gSystem->UnixPathName(level3);
}

inline void RegisterMacroPath(const char* macroPath)
{
    TString baseDir = BaseDirFromMacroPath(macroPath);
    if (baseDir.Length() > 0) RegisteredMacroBaseDir() = baseDir;
}

inline TString GetHadronizationBaseDir()
{
    const char* env = gSystem->Getenv("HADRONIZATION_BASE");
    if (env && env[0] != '\0') return TString(env);

    if (RegisteredMacroBaseDir().Length() > 0) return RegisteredMacroBaseDir();

    const char* candidates[] = {
        "base_path.txt",
        "../base_path.txt",
        "../../base_path.txt",
        nullptr
    };

    for (int i = 0; candidates[i] != nullptr; ++i) {
        std::ifstream fin(candidates[i]);
        if (!fin) continue;

        std::string line;
        std::getline(fin, line);
        if (!line.empty()) return TString(line.c_str());
    }

    return gSystem->UnixPathName(gSystem->WorkingDirectory());
}

inline bool ParseDateTag(const TString& tag, int& year, int& month, int& day)
{
    unsigned int d = 0, m = 0, y = 0;
    if (std::sscanf(tag.Data(), "%u-%u-%u", &d, &m, &y) != 3) return false;
    if (d < 1 || d > 31) return false;
    if (m < 1 || m > 12) return false;
    if (y < 1900) return false;

    day = static_cast<int>(d);
    month = static_cast<int>(m);
    year = static_cast<int>(y);
    return true;
}

inline TString GetAnalyzedDataDir()
{
    return GetHadronizationBaseDir() + "/AnalyzedData";
}

inline TString FindLatestAnalysisDate()
{
    TString analyzedDir = GetAnalyzedDataDir();
    TSystemDirectory dir("AnalyzedData", analyzedDir);
    TList* entries = dir.GetListOfFiles();

    long long bestKey = -1;
    TString latest = "";

    if (entries) {
        TIter next(entries);
        while (TObject* obj = next()) {
            TSystemFile* file = dynamic_cast<TSystemFile*>(obj);
            if (!file || !file->IsDirectory()) continue;

            TString name = file->GetName();
            if (name == "." || name == "..") continue;

            int year = 0, month = 0, day = 0;
            if (!ParseDateTag(name, year, month, day)) continue;

            const long long key = 10000LL * year + 100LL * month + day;
            if (key > bestKey) {
                bestKey = key;
                latest = name;
            }
        }
    }

    if (latest.Length() > 0) return latest;

    TString defaultDir = analyzedDir + "/default";
    if (!gSystem->AccessPathName(defaultDir.Data())) return TString("default");

    return TString("");
}

inline TString ResolveAnalysisDate(const char* requestedTag)
{
    TString tag = requestedTag ? TString(requestedTag) : TString("");
    tag = tag.Strip(TString::kBoth);
    if (tag.Length() > 0) return tag;

    TString latest = FindLatestAnalysisDate();
    if (latest.Length() > 0) {
        std::cout << "No date was provided. Using latest analyzed folder: "
                  << latest << "\n";
        return latest;
    }

    std::cout << "Could not find any dated folder under "
              << GetAnalyzedDataDir() << "\n";
    return TString("");
}

inline TString BuildAnalyzedPrefix(const TString& dateTag,
                                   const char* flavorDir,
                                   const char* prefixStem)
{
    return GetAnalyzedDataDir() + "/" + dateTag + "/" + flavorDir + "/" + prefixStem;
}

inline bool FileExists(const TString& path)
{
    return !gSystem->AccessPathName(path.Data());
}

inline TString ResolveAnalyzedPrefix(const TString& dateTag,
                                     const char* flavorDir,
                                     const std::vector<TString>& prefixStems)
{
    for (const TString& stem : prefixStems) {
        TString prefix = BuildAnalyzedPrefix(dateTag, flavorDir, stem.Data());
        if (FileExists(prefix + "0.root")) return prefix;
    }

    if (prefixStems.empty()) return TString("");
    return BuildAnalyzedPrefix(dateTag, flavorDir, prefixStems.front().Data());
}

inline TString GetPtMultiplicityPlotsDir()
{
    TString plotsDir = GetHadronizationBaseDir() + "/PlottingScripts/Pt and Multiplicity/Plots";
    gSystem->mkdir(plotsDir, true);
    return plotsDir;
}

inline TString BuildPtMultiplicityPlotPath(const char* fileName)
{
    return GetPtMultiplicityPlotsDir() + "/" + TString(fileName);
}

} // namespace PlotPathUtils

#endif
