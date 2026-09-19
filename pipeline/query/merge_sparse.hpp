#ifndef HADRONIZATION_MERGE_SPARSE_HPP
#define HADRONIZATION_MERGE_SPARSE_HPP
#include <TBufferFile.h>
#include <TFile.h>
#include <THnSparse.h>
#include <TTreeReader.h>
#include <TTreeReaderValue.h>
#include <algorithm>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>

namespace PhaseAMerge {
// Never allow a serialization preflight to grow into ROOT's 30/31-bit limits.
inline char* RefuseGrowth(char*, size_t, size_t) {
    throw std::runtime_error("sparse component exceeds serialization bound");
}
inline int SerializedSize(THnSparseD* hist, int limit) {
    if (limit <= 0 || limit > 512*1024*1024 || hist->GetChunkSize() > 16384 ||
        hist->GetNdimensions() > 15)
        throw std::runtime_error("unsupported sparse serialization bound/geometry");
    TBufferFile buffer(TBuffer::kWrite, limit);
    buffer.SetReAllocFunc(RefuseGrowth);
    hist->Streamer(buffer);
    return buffer.Length();
}
inline void Accumulate(THnSparseD* source, const std::vector<THnSparseD*>& blocks, int tune) {
    std::vector<int> coord(source->GetNdimensions());
    for (Long64_t bin=0; bin<source->GetNbins(); ++bin) {
        const double value=source->GetBinContent(bin, coord.data());
        if (coord[0] != tune+1) continue;
        if (coord[1] < 1 || coord[1] > int(blocks.size()))
            throw std::runtime_error("sparse block outside original domain");
        auto* target=blocks.at(coord[1]-1);
        const auto out=target->GetBin(coord.data(), true);
        target->SetBinContent(out, target->GetBinContent(out)+value);
        target->SetBinError2(out, target->GetBinError2(out)+source->GetBinError2(bin));
    }
}
inline std::vector<Long64_t> Entries(TFile* file, const std::string& family,
        const std::vector<int>& tunes, const std::vector<int>& blocks, int tune, int count) {
    struct Range {ULong64_t first,end;UInt_t source;};
    std::vector<Range> ranges;
    TTreeReader rr("event_ranges",file);
    TTreeReaderValue<ULong64_t> first(rr,"first_id"), size(rr,"count");
    TTreeReaderValue<UInt_t> source(rr,"source_id");
    while(rr.Next()) ranges.push_back({*first,*first+*size,*source});
    const auto tree=family=="activity" ? "events" : family=="kinematics" ? "heavy" : family.c_str();
    TTreeReader rows(tree,file);
    TTreeReaderValue<ULong64_t> event(rows,"event_id");
    std::unique_ptr<TTreeReaderValue<UInt_t>> rejected;
    std::unique_ptr<TTreeReaderValue<UChar_t>> final,selected;
    std::unique_ptr<TTreeReaderValue<Int_t>> status;
    if(family=="triggers") rejected.reset(new TTreeReaderValue<UInt_t>(rows,"rejection_mask"));
    if(family=="kinematics") {
        final.reset(new TTreeReaderValue<UChar_t>(rows,"final"));
        selected.reset(new TTreeReaderValue<UChar_t>(rows,"selected"));
        status.reset(new TTreeReaderValue<Int_t>(rows,"status"));
    }
    std::vector<Long64_t> result(count,0);
    while(rows.Next()) {
        if(rejected && **rejected != 0) continue;
        if(final && !(**final && **selected && **status>=81 && **status<=89)) continue;
        auto at=std::upper_bound(ranges.begin(),ranges.end(),*event,
            [](ULong64_t id,const Range& range){return id<range.first;});
        if(at==ranges.begin() || *event >= (--at)->end)
            throw std::runtime_error("support event has no source range");
        if(tunes.at(at->source)==tune) ++result.at(blocks.at(at->source)-1);
    }
    if(rows.GetEntryStatus()!=TTreeReader::kEntryBeyondEnd)
        throw std::runtime_error("cannot read sparse entry support");
    return result;
}
}
#endif
