# Count — T1, the generated-sample table

Two ROOT macros produce T1. What they count and why is in
[../physics/SAMPLE_COUNTING.md](../physics/SAMPLE_COUNTING.md); this page is the
operating record.

## The counting macro

```
root -l -b -q 'tools/count_generated_sample.C("<input>","<out.json>","MONASH")'
```

`<input>` is a raw file, a directory of them, or a text file listing one path
per line (`tools/count_generated_sample.C:3-7`). Run it once per tune.

It writes a JSON of schema `hadronization_generated_sample_count_v1` and a TeX
table body beside it. The JSON carries `tune`, `input`, `input_file_count`,
`events`, `final_heavy_hadrons`, `content_sums` (charm and beauty),
`species_yields` (eight rows), and a `definitions` block
(`tools/count_generated_sample.C:230-269`).

The `definitions` block is the point. It states in the artifact itself what was
counted, what was deliberately not counted, that no kinematic acceptance
applies, and what the decay policy was — so a reader of the JSON alone can see
the ruling-R37 definition without opening this repository.

## The branch preflight

Six branches are required: `heavyPdg`, `heavyIsFinal`, `heavyNc`, `heavyNcbar`,
`heavyNb`, `heavyNbbar` (`tools/count_generated_sample.C:58-61`).

Every one is checked by name with `GetBranch` **before a single entry is read**,
and an absent branch is refused by name (`:168-185`). This is the caution the
file exists for: a missing branch in a `TChain` reads as a silent zero, and a
table of zeros is a publishable-looking artifact. A refusal prints
`GENERATED_SAMPLE_COUNT_REFUSED` (`:301`).

## The merged-counter helper

```
root -l -b -q 'tools/read_merged_event_counts.C("<merged.root>")'
```

The analysis writes two event counts, and they answer different questions
(`analysis/status_analysis_THnSparse_qq.C:1329-1332`):

- `source_input_events` is `chain.GetEntries()` — every event the analysis read.
- `input_events` is `selectedEvents` — every event it analysed.

They differ only under the event-modulo filter, which this campaign disables.
Reading one of them and calling it `N_ev` would therefore be right by accident,
and would go on being quoted if a later campaign turned the filter on. The
helper reads **both**, refuses to report a number when they disagree
(`MERGED_EVENT_COUNTS_REFUSED`, `tools/read_merged_event_counts.C:51`), and
prints `MERGED_EVENT_COUNTS n_ev=…` on agreement (`:60`).

A disagreement is not an error. It is the modulo filter working, and it means
`N_ev` is ambiguous for that file: the caller must say which of the two the
table wants (`tools/read_merged_event_counts.C:16-18`).

## The gate

`tests/test_count_generated_sample.py` asserts every number the macro produces
against three hand-computed events. It is a ROOT-dependent driver and fails,
rather than skips, on a shell without ROOT.
