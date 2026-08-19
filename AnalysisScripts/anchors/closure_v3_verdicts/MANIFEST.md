# `closure_v3_verdicts/` — the JUNCTIONS and CLOSEPACKING closure evidence

**What this anchors:** the two `CANONICAL_PAIR_BLOCK_CLOSURE_PASS` verdicts that
gate `docs/THREE_TUNE_CENTRAL_TABLE.md`. The verdicts were quoted in the session
records; **the logs they were read from lived only in Nikhef scratch**
(`/data/alice/ipardoza/closure_runs/`) until this copy. Same gap N7 had for the
charm-M7 logs, and closed the same way: copied verbatim, never regenerated.

Copied 2026-08-17 from `/data/alice/ipardoza/closure_runs/`, sha-verified on
arrival.

| file | sha256 | what it is |
|---|---|---|
| `closure_HF_RUN3_V1_JUNCTIONS_20260815_220840.log` | `6d2b8e…` see below | the JUNCTIONS closure run |
| `closure_HF_RUN3_V1_CLOSEPACKING_20260815_220842.log` | see below | the CLOSEPACKING closure run |
| `verdict_line_JUNCTIONS.txt` | see below | the summary line, extracted by the waiter |
| `verdict_line_CLOSEPACKING.txt` | see below | ditto |
| `closure_waiter.log` | see below | dated record of when each closure process exited |
| `closure_waiter.sh` | see below | the watcher itself |

Run `sha256sum *` in this directory; the values are pinned in
`docs/GOLDEN_OUTPUTS.md` alongside the other anchors.

## The verdict, identical for both tunes

```
PAIR_BLOCK_CLOSURE errors=0 analysis_schema=paul_pair_objects_primary_ground_v3
central_pair_files=300 block_pair_files=3000
object_content_sumw2_closure_checks=2100 additive_metadata_closure_checks=3600
invariant_metadata_checks=1500 source_filter_contract_checks=300
expected_central_events=100000000 relative_tolerance=2e-10
```

**These are the counts `docs/CLOSURE_V3_PREREGISTRATION.md` registered in
advance**, which is what makes the PASS meaningful rather than self-reported.

## Why `closure_waiter.sh` is here and not just its output

The closure launches were **detached**, so no shell held their exit status. The
waiter exists because *absence of the summary line plus a recorded exit time* is
the only way to tell a killed closure from one still running — a silent log tail
is ambiguous, and the ambiguity is what the waiter removes.

It deliberately **does not rule on the verdict**. That is
`extraction/pipeline/harvest_tune.py --stage closure`, which checks the emitted
counts against the pre-registration. The waiter only records that a summary line
exists and when the process ended. Keeping the recorder and the adjudicator
separate is why a waiter bug cannot manufacture a PASS.
