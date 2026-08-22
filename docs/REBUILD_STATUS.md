# Rebuild status

**Current contract date:** 2026-08-22

The executable source of truth is `README.md`, `docs/DECISIONS.md`,
`docs/ARCHITECTURE.md`, the v2 multiplicity class contract, the CR holdout
policy, and the code/tests they name.

The clean rebuild deliberately retains old run records, manuscript drafts,
tables, and validation receipts as provenance. They describe the computation
that produced their bytes; they are not current scientific products. In
particular, any record under `results/`, dated run records, figure inventories,
golden-output registers and preregistrations under `docs/`, the blocked
manuscript under `paper/`, or receipt with schema
`hadronization_multiplicity_boundary_receipt_v1` remains historical because it
used the now-superseded common absolute multiplicity axis.

No old per-class number or figure is promoted into the rebuilt result set.
Nominal and variation reductions may reuse validated raw/pair bytes, but every
class-dependent extraction, uncertainty combination, plot, and receipt must be
regenerated with tune-local percentile thresholds. A new accepted result must
carry a v2 boundary receipt and the digest of
`config/multiplicity_percentile_classes_v2.json`.

The old common-boundary JSON/header and its zero-migration S5 result were
removed from this tree. Their bytes remain available in the archived source
repositories if a historical audit needs them.
