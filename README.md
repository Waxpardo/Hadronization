# Hadronization

This project asks how three complete nominal PYTHIA tune bundles change
heavy-flavour balancing and selected inclusive observables in pp collisions at
13.6 TeV. The tracked result is statistical-only: systematic uncertainty is
disabled and absent.

The visible flow is `config/` → `pipeline/generate/` → `data/` →
`pipeline/analyze/` → `pipeline/plot/` → `results/`. `results/` is the single
canonical tracked result plane. The accepted migration baseline is present;
the consolidated direct analyzer and CSV-only renderer are not yet
implemented.

Quick checks:

    ./hadronization doctor
    ./hadronization verify
    source ./setup.sh
    ./hadronization generate

`pipeline/generate/study_contract.py generate` is the only writer for the
study-derived C++ header; use its `check` command in review and build paths.
`generate` is an inventory by default. A completed accepted campaign reports no
work. Explicit `--purpose continuation --submit` is the only scheduler path and
durably reserves each attempt first; a scheduler hold before worker startup is
recorded with `pipeline/generate/submit.py record-outcome` after inspecting the
Condor event log.

Generation only describes deterministic nominal work unless `--submit` is
given and an untracked `config/site.conf` configures a scheduler. `analyze`,
`merge`, `reduce`, and `plot` intentionally refuse until ANALYZE-1 or PLOT-1.

Large raw ROOT files and transient work files belong under the ignored
`data/raw/` and `data/work/` trees, including on Nikhef. `hadronization clean`
is dry-run by default and only proposes old scratch belonging to an explicitly
accepted attempt; raw files and durable attempt evidence are outside its scope.
