# `e5fix_drivers/` — the drivers behind the three-tune extraction

**What this anchors:** the shell and Python drivers that produced the JUNCTIONS
and CLOSEPACKING columns of `docs/THREE_TUNE_CENTRAL_TABLE.md`, and the E5
re-extraction of MONASH before them.

The *extractor* was already tracked
(`extraction/extract_species_decomposition.py`, sha `4cd8b6fa…`, the
trigger-deduplicating one). **These drivers were not** — they lived only in
`/data/alice/ipardoza/extractor_e5fix/`. Without them the repository records what
was extracted but not how it was invoked: which run root, which subsample
directory, which tunes, in which order.

Copied verbatim 2026-08-17, sha-verified on arrival.

| file | what it does |
|---|---|
| `run_extract.sh` | one extraction: a merged directory in, a run directory out |
| `run_blocks.sh` | the ten blocks for one tune |
| `run_three_tune.sh` | JUNCTIONS and CLOSEPACKING, central + ten blocks each |
| `verify_e5.py` | the E5 check itself — that the trigger-owned closure histograms are counted once, not once per pair file |

## The one thing to read before reusing these

`run_three_tune.sh` writes to a **fresh run root** (`tune_runs_three/`), and says
why in its own header: the 2026-08-13 outputs under `tune_runs_e5fix/` are left
untouched **so JUNCTIONS central can be cross-checked against its independent
earlier extraction.** Pointing these scripts at an existing run root destroys
that cross-check. The paths inside are Nikhef absolute paths and are kept as they
were rather than parameterised — this is an anchor, not a tool.

## What E5 was

The closure histograms are **trigger-owned** and were written into every pair
file sharing that trigger, so summing files counted each charm trigger 24× and
each beauty trigger 26×. Only the signed registry says which trigger a file
belongs to, which is why `--registry` is not optional in the extraction. Full
account in `docs/ERROR_RECORD.md` E5; the superseded replicating reader
(sha `b67f9008…`) is recoverable from history at `003da54b` and is also held on
Nikhef under `attic_e5_replicating_extractor_20260813/`.
