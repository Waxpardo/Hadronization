# B6, the mechanical items, and the first v3 figure — 2026-08-13 (eleventh session)

**Suite 41/41 before and after. The macro compiles under ACLiC before and after
every edit.** The stack now runs end to end on v3 data.

## Remote, one line each

**A2 changed state and it is not good news: all 301 jobs are HELD**, not idle.
`HoldReasonCode 3` — `OnExitHold` fired on `ExitCode 128` for every one of them,
`NumJobStarts=1`, started 15:40 CEST. The stderr's last lines are
`fatal: not a git repository (or any parent up to mount point /data)`, so the
wrapper's provenance `git` call is what returns 128 on the worker. **Diagnosed,
not touched** — the scheduling question is closed and this is a job-wrapper
defect for a session that owns A2.

**The merge is alive** (`merge_root_files.sh`, PID 430646, since 07:24) and has
moved: **JUNCTIONS central is complete** — 304 files, `merge_provenance.json` and
`merged_pair_checksums.json` written 2026-08-12 19:28 — and JUNCTIONS blocks are
at **4 of 10**. MONASH is complete, central + 10 blocks. CLOSEPACKING has
nothing merged.

---

## B6 — the axis replaced, keyed exactly as it was

The owner ruling was *keep the shape, change only the source*, and the diff
honours that literally: `thresholdsByTune[tune][percentile]` is still keyed by
the configured percentile labels, so **`MULTIPLICITY_BOUNDARY` emission, the
`integerThresholds` construction, `RequireDiscretePartitionCoverage`, the class
records and the partition block needed no edits at all.** The population site is
one call where a `ThresholdForPercentile` loop used to be.

The mapping lives in a new header, `plotting/CommonMultiplicityBoundaries.h`,
because **two** consumers resolve the artifact and a duplicated mapping would be
precisely the second definition the artifact forbids.

`thresholds[0.0]` is the one value not in the artifact — the ruled top class is
**open-ended** — and it comes from the **axis's last regular bin**, not from
`ThresholdForPercentile(identity, 0.0)`. That matters: the latter is the last
*populated* bin and is tune-dependent, which would have broken the identity the
whole ruling rests on.

**The three conditions, demonstrated rather than asserted:**

1. **Fail closed.** A 10-class configuration against the 11-class artifact exits
   1: *"Configured multiplicity class count (10) does not match the 11 classes
   defined in … ; refusing to truncate or pad the axis"*.
2. **Identical across tunes.** A one-tune run satisfies the assertion vacuously,
   so it was run over **MONASH + JUNCTIONS** as well:
   `tunes_compared=2 … identical_across_tunes=PASS`, all twelve boundary lines
   agreeing tune for tune. JUNCTIONS central being merged is what made this
   possible today.
3. **Label provenance.** `policy.percentile_label_provenance` says the labels are
   MONASH-MB percentiles and **not** the labelled tune's own;
   `boundary_source` carries the artifact path, its sha256, the class names and
   lower edges, and the `33c9a8c` sha.

**Two consequences that were not optional, and both are the same defect class —
a stale statement about how a number was made:**

- The receipt's `algorithm` said `ascending_discrete_weighted_quantile_v1`. It no
  longer is one. Now `common_absolute_nch_class_boundaries_v1`, which cost two
  lines in `tools/statistical_robustness.py` and its fixture.
- `Plot_MultiplicityDistribution_PercentileBoundaries.C` verified the frozen
  receipt by **recomputing per-tune quantiles** and drew those same quantiles as
  its class decorations. Both would now disagree with the receipt by
  construction. It resolves the artifact instead — one function body, and the
  four call sites are untouched.

The receipt also gained `common_boundary_utility_sha256`: it already pinned the
plotter source and `MultiplicityBoundaryUtils.h`, and the new header would
otherwise have been the one piece of axis-defining code nothing pinned.

## B1 / B4 / B5

New v3 plotting configuration; `hf_run3_v1_candidate` in
`config/dataset_selector.json` plus the matching single-dataset selector.
**`run_paper_plots.sh` needed no edit** — its `canonical_candidate` branch already
forces `publication_eligible=false`, and the configuration is chosen by
`THNSPARSE_COMPLETE_ROOT_CONFIG`. Measured against the merged product,
`analysis_schema` was the only contract value that differed, as enumerated.

The v3 configuration is MONASH-only, because CLOSEPACKING is not merged and a
three-tune file could not run.

## Task 3 — the run

Full record, with the command, shas, ROOT build and cross-checks, in
`docs/plotting_validation/hf_run3_v1_monash_20260813/RUN_RECORD.md`. In short:
exit 0, 8 central and 80 block files validated, every emitted boundary equal to
the artifact, partition exactly 1.0.

Two committed-anchor cross-checks land: the **pair registry sha256** matches
`MONASH_CENTRAL_TABLE.md` exactly, and the **100 M event count** matches. The
observable is confirmed identical — `NCH_PRIMARY_CHARGED_ETA10_V1` in the
generator, `multiplicity_primary_charged_eta10_v1` in the artifact.

**`GOLDEN_OUTPUTS.md` §0.3 is new** and states plainly that ROOT figures are
contracted on pinned inputs + pinned ROOT + recorded command, **not** on a byte
digest, with the reason: a canvas embeds a timestamp and a ROOT version, so
byte-identity is not a promise this project can keep, and an unkeepable contract
teaches reviewers to ignore contracts.

### ⚠ One number the owner should see

The campaign's realised class fractions sit **below** the MB labels at high
activity — the top class holds **4.47 %** of campaign events against an
**8.42 %** MB label, a 3.95 pp residual. A residual is expected and is exactly
what the ruling publishes rather than hides. **The sign is what is unexplained**:
a heavy-flavour-triggered sample would naively sit *above* minimum bias there.
The observable is identical in both, so this is a property of the samples.
`b4_multiplicity_mb/run_meta.txt` shows a `hard` run was made per tune, but
**only the `mb` CSVs were kept**, so the comparison that would settle it is not
in the repository. It does not affect B6 — the boundaries are absolute and
verified — but it should be settled before a per-class number reaches the
manuscript.

### The figure, having actually looked at it

The first attempt drew **one** class, faithfully, because every canvas in the
reduced v2 configuration lists ten of the eleven in `bins_to_ignore`. Nothing in
the stack caught that; looking at the rendering did.

With all eleven drawn the dependence is real and monotonic in charm —
D⁻ balance **0.1889 → 0.2087, +10.5 %** from lowest to highest activity — and
roughly flat in beauty (**+3.5 %**). It is still a weak figure: with *species* on
x and eleven classes overlaid as series, a 10 % trend is barely readable at any
y-range. Recommended, not done: put activity on the x-axis, or plot the ratio to
the integrated class. That is figure design and belongs to whoever owns the
paper figure.

---

## Diff size

`47d6396` is 897 insertions / 22 deletions over 9 files, but **593 of those
insertions are the generated v3 configuration and 166 the new header — both new
files.** The change to existing code is 69 lines in
`improvedPlotting_THnSparse.C`, 35 in the standalone boundary plot, 5 in
`MultiplicityBoundaryUtils.h` and 9 across the two Python files.

## Next session

1. **A2's 301 held jobs** — exit 128 from a `git` call on a worker with no
   repository. Owner's call whether to fix the wrapper or abandon the variation.
2. **The MB-versus-campaign sign question** above, before any per-class number is
   published.
3. **JUNCTIONS** needs only its blocks finished (4/10 today) and one line added
   to `PYTHIA_TUNES`; CLOSEPACKING needs the merge to reach it.
4. The multiplicity figure's *form*, if it is to carry the argument.
