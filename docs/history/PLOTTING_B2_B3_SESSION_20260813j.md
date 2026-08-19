# B2, B3 and the single axis definition — 2026-08-13 (tenth session)

**Three commits, `a527f02..594816e`. Suite 40/40 → 41/41.** The macro compiles
under ACLiC before and after every edit.

A2: **301 Idle, 0 outputs**. Merge alive, `JUNCTIONS/slot_829`, 0 promotions,
same boot. Neither touched.

---

## What landed

**B3 — the contract prefix.** Both parsers resolve the key prefix from the
config's own content: never defaulted, never guessed. Both families present, or
neither, is fatal; a prefix disagreeing with the schema it carries is fatal;
`RequireExactKeys` stays strict against the **resolved** set. **The committed v2
configs are untouched and still resolve to the identical 14 keys.**

> **The repo's own guard caught my first attempt.** I retyped both schema
> literals into a helper, and `test_pair_object_contract.py` failed with *"pins
> the schema literal … Judge the file through ParsePairSchemaVersion instead."*
> That guard is the v2-pin sweep's residue and it was exactly right — the
> agreement check now goes through `ParsePairSchemaVersion`, so the
> pair-object contract remains the single place that knows the tags.

**B2 — the mode.** `v3_metadata_only_v1` added to both metadata-admitting
predicates. **The predicate name `AllowsV2` was deliberately left alone**: it
means "metadata-bearing, as opposed to metadata-free legacy", it is internal, and
renaming ripples through both implementations and the parity test for no
behavioural gain. The lying-name concern that drove the `v3_` config prefix is
specifically about **config** keys, which get copied and adapted.

**The axis now has ONE definition.**
`config/multiplicity_class_boundaries_v1.json` carries the ruled boundaries.
`make_paper_figures.py` reads it instead of the literal it used to hold, and
**figure 3 regenerates byte-identically** (`9bf61215…96a8e109`) — which is the
proof that the artifact carries exactly what the literal did, not merely
something similar. The percentile labels are deliberately **not** stored: they
are recomputed from the committed MB samples, so a label cannot drift from the
sample it describes.

**`tests/test_pair_contract_schema_prefix.py`** — 22 checks, both directions, and
a docstring that states what it establishes **and what it cannot**: that a full
plotting run is unchanged, which no test here can prove now.

**STATE.md gains the second category README defines.** Every figure in
`PAPER_FIGURE_PROVENANCE.md` is permanently non-regenerable — its inputs are
gone. Recorded with the consequence spelled out: **any "keep this path so the old
figures stay regenerable" argument is void**, which already cost one ruling.

---

## What did NOT land, and why

**B6 — the derivation replacement.** Not done. The surgical point is
`improvedPlotting_THnSparse.C:1848`, where `thresholdsByTune[tune][percentile]`
is populated from `ThresholdForPercentile(...)`, inside a ~375-line function
woven with receipt emission and partition validation.

**The unresolved question is what the map should be keyed by** once classes are
defined by absolute boundaries rather than requested percentiles: the downstream
emits `MULTIPLICITY_BOUNDARY` per percentile and builds `integerThresholds` from
the same keys. Getting that wrong would silently redefine the axis that every
per-multiplicity number in the paper is conditioned on — so it is left for a
session that can both decide it and run the stack afterwards, rather than
written blind at the end of this one.

**B1 / B4 / B5** are additive and mechanical but pointless before B6 — the
classes would be wrong. **Task 4 (the MONASH run)** is blocked on all of it.

**The per-tune derivation remains readable at `33c9a8c30fa97c9281e26ecbd6d1becc1afb9c21`**,
recorded in the enumeration doc in advance of the removal so the sha is fixed
before the branch disappears.

---

## Next session

1. Decide the B6 map keying, then replace the derivation to read
   `config/multiplicity_class_boundaries_v1.json`. Compile with
   `root -l -b -q -e '.L plotting/improvedPlotting_THnSparse.C+'` — it works
   locally and catches syntax and type errors in seconds.
2. Then B1/B4/B5 (v3 config, selector entry, paths), then the MONASH run.
3. **Look at the rendered figure**, and cross-check it against the committed
   MONASH anchors before believing it.
