// T1: N_ev from a merged analysis file, read from BOTH counters (finding F64).
//
//   root -l -b -q 'tools/read_merged_event_counts.C("<merged.root>")'
//
// The analysis writes two event counts, and they answer different questions
// (analysis/status_analysis_THnSparse_qq.C:1329-1332):
//
//   source_input_events = chain.GetEntries()  -- every event the analysis read
//   input_events        = selectedEvents      -- every event it ANALYSED
//
// They differ only under the event-modulo filter, which is disabled for this
// campaign. Reading one of them and calling it N_ev would therefore be right by
// accident, and would go on being quoted if a later campaign turned the filter
// on. This reads both and refuses to report a number when they disagree.
//
// A disagreement is not necessarily an error: it is the modulo filter doing its
// job. What it means is that "N_ev" is ambiguous for that file, and the caller
// has to say which of the two the table wants.

#include "TFile.h"
#include "TParameter.h"

#include <iostream>
#include <string>

int read_merged_event_counts(const char* mergedFile)
{
    TFile file(mergedFile, "READ");
    if (file.IsZombie()) {
        std::cerr << "MERGED_EVENT_COUNTS_REFUSED cannot open " << mergedFile
                  << std::endl;
        return 1;
    }

    const char* const names[2] = {"input_events", "source_input_events"};
    Long64_t values[2] = {0, 0};

    for (int i = 0; i < 2; ++i) {
        auto* parameter =
            dynamic_cast<TParameter<Long64_t>*>(file.Get(names[i]));
        if (parameter == nullptr) {
            std::cerr << "MERGED_EVENT_COUNTS_REFUSED " << mergedFile
                      << " carries no TParameter<Long64_t> named '" << names[i]
                      << "'" << std::endl;
            return 1;
        }
        values[i] = parameter->GetVal();
    }

    if (values[0] != values[1]) {
        std::cerr << "MERGED_EVENT_COUNTS_REFUSED input_events=" << values[0]
                  << " != source_input_events=" << values[1]
                  << ". The two differ only under the event-modulo filter, "
                     "which this campaign disables; with it on, N_ev is "
                     "ambiguous and the caller must name which count the table "
                     "reports." << std::endl;
        return 1;
    }

    std::cout << "MERGED_EVENT_COUNTS n_ev=" << values[0]
              << " input_events=" << values[0]
              << " source_input_events=" << values[1]
              << " agree=yes" << std::endl;
    return 0;
}
