# Per-tune processing — pre-registration

**Written and committed BEFORE the first tune's blocks finished merging.**
Applies **identically** to MONASH, JUNCTIONS and CLOSEPACKING; it is not
re-tuned between tunes.

Three steps per tune, in order. **A failure at step 1 or 2 stops that tune's
step 3** — a decomposition built on a tune that failed closure or integrity is
not a number, it is a guess with error bars.

---

## STEP 1 — closure at scale

`Validation/validate_pair_block_closure.sh CENTRAL BLOCK_BASE v3`, which requires
`combined_root_1` … `combined_root_10` to exist for that tune.

**The third argument is the schema the campaign requires and is mandatory**
(private error-ledger review finding A4). Without it the gate derived its
expected counts from the data's own declaration, so a complete v2 directory
passed at 1800/600 — the state README calls a failure.

Counts pre-registered in `docs/CLOSURE_V3_PREREGISTRATION.md` (derived
2026-08-09 at `1de9bfe`, not re-quoted here):

| # | expectation |
|---|---|
| **C1** | content comparisons = **2100** exactly (7 × 300) |
| **C2** | invariant comparisons = **1500** exactly (5 × 300) |
| **C3** | **zero** closure failures and **zero** identity failures |
| **C4** | if the counts come back **1800 / 600**, the run resolved the object set from the **sidecar JSON** (`…_v2`) instead of each file's own `analysis_schema` (`…_v3`) — **that is FAILURE, not success** |

**Sum rule = 1 at 1e-9.**

**Any deviation ⇒ STOP for that tune, report the numbers verbatim, do not
proceed to steps 2–3.** The v2-era numbers are the specific trap: they are a
*plausible-looking* pass.

---

## STEP 2 — block-vs-central integrity

`extraction/compare_subset_parent.py` for **each of the ten blocks against its own
central**, per tune. Thirty comparisons in total.

**This is a much stronger test than the anchor case, and the reason matters.**
Each block is 100 of the same 1000 inputs the central merged, so the blocks are
**true subsets by construction** — not an inherited claim. The binomial model
therefore applies exactly.

| # | expectation |
|---|---|
| **I1** | measured scale ≈ **10.0** for every block (tool fail-closes beyond ±5 %) |
| **I2** | **zero flagged bins at \|z\| > 4**, all 30 comparisons |
| **I3** | the ten blocks partition the central: **Σ over blocks = central, exactly**, bin by bin |

**Expected false-positive rate makes I2 sharp:** 88 testable bins × 30
comparisons × P(|z|>4) ≈ **0.16 bins**. **Any flag at all is notable**; two or
more is a finding.

**I3 is the decisive one** — it is exact arithmetic, not statistics. If the ten
blocks do not sum to the central bin-for-bin, the block decomposition is not a
partition of the central and the SEMs would be over ten non-independent things.

**Flagged bins ⇒ report before trusting that tune's SEMs.**

---

## STEP 3 — species decomposition with block SEMs

Ten blocks per tune, **both conventions**: diquark-structure (primary) and
experiment-comparable via **map v2** (`c9593c9c0a7c4ec2…`).

**Method, fixed here so it cannot drift between tunes:**

- **Every nonlinear quantity is formed INSIDE a block before averaging.** A
  fraction is computed per block from that block's own counts; the ten fractions
  are then averaged. **Never a ratio of summed numerators to summed
  denominators** — that is a different estimator with a different (smaller,
  wrong) variance.
- **SEM = stdev(ten block values) / √10, dof = 9.** Sample standard deviation,
  not population.
- **Central values from pooled counts**, quoted beside the block mean; where the
  two differ materially that is itself reportable (it measures block-size
  imbalance).
- **Full provenance manifest** beside the outputs: tune, input directories,
  input count, macro/tool sha256s, map sha256, reader sha256, env vars per the
  analysis contract, and the merged-object shas.

**Registered expectations, structure only:**

| # | expectation |
|---|---|
| **S1** | the ten per-block fractions are mutually consistent — **χ²/dof ≈ 1** against their own SEM; a χ²/dof ≫ 1 means the blocks are not exchangeable and the SEM understates |
| **S2** | block mean and pooled central agree within ~1 SEM |
| **S3** | **CR tunes differ from MONASH** in the baryon-partner fractions — this is the physics the paper is about, and the direction is not pre-judged here |

**No numeric prediction for the fractions themselves.** They are the
measurement.

---

## WHAT THE ANCHOR EXPERIENCE CHANGES ABOUT THIS

The anchor's aggregates agreed with its parent to **< 0.02 pp** while 30 of 88
bins were inconsistent, 16 of them by more than 2 %
(private error-ledger entry E4). **Step 2 exists because of that**: aggregate
agreement is not bin agreement, and the decomposition is a bin-level product.

> **ANNOTATED 2026-08-13.** "30 of 88" is the retired binomial null; step 2's I2
> now uses a robust median-centred, MAD-scaled null, under which the same anchor
> comparison flags **0 of 88** (σ̂ = 4.399, max |z| = 2.83). **The point of this
> section is unchanged and so is the quarantine** — see private error-ledger entry E4 for
> why zero measures a blind spot for *broad* defects rather than the anchor's
> health. **What it means for step 2 going forward:** I2 detects *localized*
> bin-level failures; a uniform or sector-wide displacement is invisible to it,
> and **I3 — the exact block-sum identity — is the check that must catch that.**
> The two are not redundant and neither alone is sufficient.

**Step 2 runs before step 3 for every tune, including the ones that look fine.**
