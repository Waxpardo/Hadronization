# Rebuild migration

## Sources retained

- The deterministic publication projection supplies the clean source baseline
  and fresh history.
- Paul Veen PR 13 supplies the historical tune-local percentile definition.
- The current closeout tree supplies later safety contracts and the private
  provenance archive.
- Existing Nikhef production, reduction, merged, and harvest bytes remain in
  place and are addressed through site-relative selectors.

## Sources not merged

The old `main`, `closeout`, systematics-harvest, and publication histories are
not merged into one graph. Their divergent commits include experiments,
generated artifacts, private records, and superseded scientific decisions.
They remain recoverable archives, not runnable dependencies of this checkout.

## Promotion sequence

1. Build and test this source locally with `./hadronization check --portable`.
2. Deploy the tracked tree to a new Nikhef checkout without changing external
   campaign directories.
3. Copy the existing canonical freeze records once into
   `HADRONIZATION_DATA_ROOT/project/runs/<campaign>/freeze`, then run the
   pinned site check and dataset resolution on Nikhef.
4. Recompute per-tune multiplicity receipts and rerun affected nominal and
   variation plots/extractions. Old common-axis results remain superseded.
5. Make the validated clean repository the GitHub `main` source of truth.
6. Archive the old working repositories read-only after remote and Nikhef
   provenance links have been recorded.

No old figure, multiplicity-boundary receipt, per-class extraction, or
systematic result is promoted merely because its input ROOT files remain
valid. Anything conditioned on the superseded common absolute axis must be
regenerated under the tune-local definition.
