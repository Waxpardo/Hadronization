# Sealing HF_RUN3_V1, and what the open gate revealed — 2026-08-17 (late)

**Suite 50/50 → 51/51 (one new contract test). Wall clock 20:55–2x:xx CEST.**
Local `physics-focus` `46bfd40` → this session; Nikhef checkout unmoved at
`8650a047` (no advance work). **Retry clusters `5526031`–`5526033` all converged;
the queue is empty and the systematics campaigns are COMPLETE at 2100/2100** —
300 raw files in each of seven campaigns. *The harvest is a separate session and
was not started.*

> **Headline: HF_RUN3_V1 is sealed and authorized — `canonical`,
> `publication_eligible: true` — on facts re-measured this session rather than
> inherited. Opening that gate then exposed the next one, and it is a defect
> rather than a policy: the repository's own manifest builder produces a freeze
> that its own figure macro rejects, on three independent counts. The
> balancing-yield E5 question is resolved SAFE, structurally.**

---

## 1. The seal — `docs/HF_RUN3_V1_PUBLICATION_AUTHORIZATION.md`

### 1.1 The freeze already existed, and was verified rather than rebuilt

`tools/build_canonical_manifest.py` **refused to overwrite** an existing freeze —
correct behaviour — so the session validated the 2026-08-09 artifact instead:

| check | result |
|---|---|
| seal schema | `hf_canonical_freeze_seal_v2` |
| rows / per tune / blocks | **3000 / 1000 / 10** |
| seal's `canonical_manifest_sha256` vs the file | **identical**, `fcd96eae…` |
| ten `block_*.jsonl` summed vs manifest rows | **3000 = 3000** |
| 12-row sha256 spot-check against disk | **12/12 MATCH** |
| newest raw mtime per tune vs freeze time | all **before** the freeze |

> **A previous session reported this freeze missing.** It was looking inside the
> scratch figure deploy, which was built from a tarball of *tracked* files, and
> `/campaigns/` is gitignored — so the artifact was never absent, only invisible
> there. Recorded because the correction matters more than the mistake: "absent"
> and "not in this copy" are different findings.

### 1.2 Counts re-measured this session

3000 raw `.root`, 3000 `.sha256` sidecars, 3000 `attempt_metadata` receipts,
3000 `raw_validation` job directories.

> **One number looked like a defect and was not.** A first pass read
> 2999 / 3062 / 3063 `raw_validation` entries. That was `ls` printing directory
> headers and blank separators across 1000 directories, not a shortfall — the
> layout is `job<NNN>/attempt<NNN>/` and every tune holds exactly 1000 job
> directories. Chased to the bottom before sealing, because a seal that cites a
> number nobody checked is the thing this whole discipline exists to avoid.

**Merge: 33/33, and the sum agrees with the DISTINCT leg count.** 15 lines in
`merge_v3.log` + 18 in `merge_v6.log` = 33, and 33 distinct (tune, block) pairs.
That agreement is the load-bearing part: the merge was killed by the 08-12 reboot
at 15/33 and restarted twice, so a re-promotion would have pushed the sum above
the distinct count. It did not.

**Closure: one PASS marker per tune, and the verdict line is byte-identical
between the merge's own sequential pass and the separately-launched runs**
(the latter committed at `AnalysisScripts/anchors/closure_v3_verdicts/`). Two
independent passes agreeing exactly is stronger than either alone.

### 1.3 The promotion, and a drift the new test caught immediately

Both `config/dataset_selector.json` and `config/dataset_selector_hf_run3_v1.json`
carry the row, **verbatim and twice**. Both were promoted.

`tests/test_dataset_selector_row_agreement.py` pins that they agree — and **found
a pre-existing drift on its first run**: `hf_pt2_int_candidate`'s `interpretation`
differed between the two files. Prose only, no operational field affected, but
that is precisely the seed the test exists to catch. Reconciled to the richer of
the two wordings, which carries a "regenerate from HF_RUN3_V1 before any paper
use" warning the shorter one had dropped.

The test also asserts that any `publication_eligible` row cites an authorization
document that **exists and still hashes to the recorded digest** — the selector
validator stopped enforcing those fields, so nothing else checked that an
authorization had not been edited since it was cited.

**The key stays `hf_run3_v1_candidate`** although the status is now `canonical`:
it is exported as `HADRONIZATION_DATASET_ID` and may already appear in written
provenance, so renaming would orphan those records. The key is an identifier;
`status` carries the claim.

## 2. ⛔ The gate moved rather than opened — and the next one is a defect

With the dataset canonical, figure 4 got past the selector and failed here:

```
ERROR: cannot open file for SHA-256: .../freeze/canonical_raw_validation_receipt.json
```

**`Plot_InclusiveKinematicSpectra_Raw.C` requires a five-artifact sealed freeze;
`tools/build_canonical_manifest.py` produces three.** Three independent
mismatches:

1. **Missing artifacts.** `freeze_summary.json` and
   `canonical_raw_validation_receipt.json` are written **nowhere in the
   repository except test fixtures**.
2. **Missing seal fields.** The macro requires `state: "SEALED"`,
   `validation_receipt_path`, `validation_receipt_sha256`. The builder's seal has
   none of them.
3. **Shape.** First-stage requires `jobs_per_tune == 100` **and**
   `successful_events_per_job == 1000000`. Superseding requires ≥ 110 jobs **and
   a union of ≥ 2 source freezes**. **HF_RUN3_V1 is 1000 jobs × 100 000 events**
   and fits neither.

> **The shape rule is the deep one, and it is a decomposition mismatch, not a
> size one.** 100 × 1 M and 1000 × 100 k are the same **100 M per tune**. The
> contract checks how that total is divided, and it was written for
> `campaigns/HF_100M_primaryGround_ccbb_v1` — still the only entry in
> `campaigns/` — and never updated for the physics campaign.

**Not worked around, deliberately.** Hand-writing the two missing artifacts means
declaring `successful_events_per_job: 1000000` (false — it is 100 000) and
`state: "PASS"` for an exhaustive raw validation that never ran. That is
fabricated evidence.

**Scope of the blocker: the raw-reading macro only** — figure 4 and the kinematic
panels. `improvedPlotting_THnSparse.C` reads merged products and does not consume
the freeze at all.

## 3. ✅ The balancing-yield E5 question — SAFE, structurally

**The interesting part is that the family DOES touch the replicated object.** The
yield is per-trigger normalised: numerator `hCorrelations` (per-pair, safe),
denominator `nTriggers` from **`hTrKinematics`** — the trigger-owned object
replicated 24×/26× across pair files.

Safety is therefore not "it avoids the object" but **"it is read once per pair
file and never summed"**:

- each configured pair opens exactly one OS and one SS file;
- the only two histogram `Add()` calls are OS−SS **within** a pair;
- a uniqueness guard **throws** on `"Duplicate configured pair identity"` — the
  only configuration that could produce cross-file replication is refused;
- the multiplicity read dedups by path and captures an identity, not a sum.

**Point three is what makes it structural rather than incidental.**

## 3b. ✅ One figure DID render, and it reproduces exactly

`improvedPlotting_THnSparse.C` does not consume the freeze, so the THnSparse
family was never blocked by §2. The three-tune multiplicity canvas was rendered
on pinned ROOT 6.30/01 from the sealed dataset, and its PNG is **byte-identical
to the committed POLISHED reference** from 2026-08-16 — across a different
session, a different deploy tree, and the promotion itself. The boundary receipt
differs in two leaves: an embedded deploy path, and the hash covering it.

**Two standing concerns close with it.** Every `UNCERTAINTY_MATRIX` row reports
`finite_yields=10 status=PASS`, so the **610 incomplete ten-subsample coverage
cases** belonged to the legacy dataset, not merged v3. And the class axis is live
and correct in the figure — legend and internal bin names carry the artifact's MB
percentiles (`hDPhic10_MB8p422_17p124`), matching the independent closed-loop
recomputation to the digit.

**Looked at it.** The physics reads correctly: both CR tunes push the baryon
ratios well above unity — JUNCTIONS/MONASH Λ_b to ≈ 2.3 — while the meson ratios
sit at or below 1. But it is **not publication-presentable**: raw identifier
species labels, a two-point categorical x-axis with each class drawn as a
full-width rule, no x title or √s, and a bare "yield" ordinate. Presentation, not
correctness, and already present in the committed reference. Recorded as owner
items in the inventory §3.1b.

## 4. Boundaries respected

`Paper/**` read-only. No systematics harvest — the campaigns finished this
session and were left alone. No advance work; Nikhef stayed at `8650a047`.
Deploy `72ca4e39` untouched. The frozen checkout received only the gitignored
freeze path, leaving it tracked-clean.

## 5. For the next session

1. **The freeze-contract mismatch (§2) is the one blocker on figure 4 and the
   kinematic panels.** It is a design decision — either the shape rule admits the
   1000 × 100 k decomposition, or a superseding-style freeze is built for a
   single campaign, or the raw macro learns a canonical path that does not
   require the two unproduced artifacts.
2. **The systematics harvest** is now unblocked by data: 2100/2100 complete.
3. **Four owner decisions** remain open in `docs/FIGURE_INVENTORY.md` §4 and §5.4.
