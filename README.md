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

Generation only describes deterministic nominal work unless `--submit` is
given and an untracked `config/site.conf` configures a scheduler. `analyze`,
`merge`, `reduce`, and `plot` intentionally refuse until ANALYZE-1 or PLOT-1.

Large raw ROOT files and transient work files belong under the ignored
`data/raw/` and `data/work/` trees, including on Nikhef.
