# Architecture

## Control plane and data plane

Git is the control plane: source, scientific contracts, schemas, registries,
selectors, and tests. Nikhef storage is the data plane: raw ROOT files,
seed ledgers, canonical freezes, per-job reductions, merged objects, and
harvest outputs. Plot outputs are routed through an ignored `plotting/Plots`
symlink to `project/results/<campaign>/<commit>/plotting`. Mutable state never
lives in the checkout. A checkout can be
replaced without moving the data plane, and a laptop can disappear without
interrupting the pipeline.

Systematic renders use the same top-level command but a separate output
contract. `plot <variation> measure-balancing` stages every nested canvas path
under
`project/results/<campaign>/<commit>/measurements/<dataset>/`, then verifies
the produced files and publication trees before writing a non-publication
measurement receipt. Each selector names its campaign-specific three-tune
harvest configuration. The staged audit copy widens nominal display frames so
a legitimate systematic shift is not clipped; uncertainty rows are calculated
before axes are applied and the receipt requires the exact configured identity
set and complete-root tag. It never uses the publication symlink as its output
path.

```text
tracked checkout
  generation cards + producer
          |
          v
external production root / raw / receipts
          |
          v
external project/runs / seed ledger + sealed canonical manifest
          |
          v
external analysis root / per_job
          |
          v
external merged root / central + block_01..block_10
          |
          +--> extraction + systematics harvest
          |
          `--> plotting + receipts + selected results
```

## Stage ownership

| Stage | Source | External outputs | Transition authority |
|---|---|---|---|
| Generation | `generation/`, tune/config registries | promoted raw files and attempt receipts | successful producer exit, strict ROOT validation, no-clobber promotion |
| Freeze | `tools/build_canonical_manifest.py` | canonical manifest and ten block manifests | complete equal-tune exposure and unique canonical slots |
| Reduction | `analysis/`, `tools/render_analysis_submit.py` | one pair directory per canonical slot | manifest membership, raw schema, source and card provenance |
| Merge | `merging/`, `Validation/` | three central directories and thirty block directories | exact input count, pair schema, manifests, central/block numerical closure |
| Extraction | `extraction/` | tables, deltas, uncertainty products | named dataset, complete input inventory, explicit estimator |
| Plotting | `plotting/` | figures and boundary receipts | named dataset, per-tune class receipt, coverage and range checks |

## Multiplicity boundary

The JSON configuration carries percentile windows. At plot initialization, the
plotter opens every configured pair input for one tune and requires their
`summed MULTIPLICITY` histograms to be byte-identical in binning, contents,
errors, and `Sumw2`. It derives that tune's thresholds once, validates the
integer partition, records the source hash and achieved fractions, and reuses
the frozen map for all pairs and all canvases. Another tune repeats that process
independently.

An optional pair-level `multiplicity_scope` narrows the domain of a genuinely
unavailable observable (currently Bc pairs: integrated and 0–1% only). The
calculation records unavailable errors outside that domain, and both yield and
tune-ratio renderers omit those points. They are never converted to zero and
never allowed through the finite-value guard.

## Execution profiles

`setupEnv.sh` resolves a tracked site profile, then dependency pins. Dataset
selectors expand site variables only after the profile is loaded. The root
`hadronization` command is the only operator-facing interface; stage scripts
remain independently callable for debugging and receipts.
