# Post-review Tier 1 — verification and correction, 2026-08-13

**Input:** an external adversarial review of `f0e67dc`. **Rule for the session:
verify before fixing.** The reviewer's evidence was strong; nothing was
re-extracted, relabelled or rewritten on the strength of a report alone.

**Nine commits, `f0e67dc..80d84fd`.** Suite 30/30 → **37/37**, seven tests
added, none removed or skipped. The live pipeline, the merge, and the
JUNCTIONS/CLOSEPACKING chains were not touched.

---

## 1. A1 — CONFIRMED. The published decomposition was replicated 24×/26×

**The mechanism, read from the code.** `hFlavourClosure` and
`hFlavourClosureSpecies` are owned by the **trigger**: one accumulator per
distinct trigger PDG (`status_analysis_THnSparse_qq.C:870-879`), written into
**every pair file sharing that trigger** (`:1179-1191`).
`extract_species_decomposition.py` summed all 300 files. It built
`per_pair_species` and never read it — verified dead by grep, two references,
both writes.

**Measured from the committed registry**, not assumed: each of the six charm
triggers appears in **24** pair files, each of the six beauty triggers in
**26**; 144 + 156 = 300.

### The decisive test, and why it did not need the cluster

The merged product lives on Nikhef, so the brief's "extract with dedup and
compare" was not runnable here. A stronger test was available from committed
artifacts alone.

The closure loop weights each associate by `-q_trig · q_assoc` with the charge
taken **in the trigger's own sector**, and skips associates whose charge in that
sector is zero (`:1026-1032`). **So a charm trigger can only ever fill
charm-carrying species, and a beauty trigger only beauty-carrying ones.** Under
replication:

| test on the published `per_species.csv` | result |
|---|---|
| 45 charm-only species divisible by 24 | **45 / 45**, zero violations |
| 42 beauty-only species divisible by 26 | **42 / 42**, zero violations |
| control — charm-only *also* divisible by 26 | only **5 / 45** |
| control — beauty-only *also* divisible by 24 | only **2 / 42** |
| 8 mixed-sector species (B_c, Ξ_bc, Ω_bc) | mixed remainders, as `24C + 26B` predicts |
| gcd over all 94 nonzero totals | **exactly 2** = gcd(24, 26) |

Probability under a correct extraction ≈ 24⁻⁴⁵ · 26⁻⁴² ≈ **10⁻¹²¹**. The
controls matter: without them "divisible by 24" could have been vacuous.

**The defect was in the published numbers, not merely possible in the code.**

### The correction

| quantity | published | corrected | Δ |
|---|---|---|---|
| total | 1,298,655,240 | **53,662,414 … 53,662,828** | ÷ 24.2004 |
| kCentralGround | 52.3388 % | **52.4958 %** | **+0.1570 pp** |
| kExcludedVector | 46.6510 % | **46.4946 %** | **−0.1563 pp** |
| kExcludedExcited | 1.0102 % | **1.0095 %** | −0.0007 pp |
| charm : beauty | 89.2404 : 10.7596 | **89.9852 : 10.0148** | **±0.7448 pp** |
| D⁰ (map v2, split) | 25.2435 % | **25.4542 %** | +0.2107 pp |
| B⁺ (map v2, split) | 2.3035 % | **2.1440 %** | **−0.1595 pp** |

**Within-sector ratios are exactly unchanged** — ratio-of-ratios = 1.000000 for
D⁰/D⁺, D̄⁰/D⁻, Λ_c⁺/D⁰, B⁺/B⁰, Λ_b⁰/B⁰, B⁻/B̄⁰. **The error is confined to
absolute weights and cross-sector quantities.** That is the whole shape of it,
and it is why every previous check missed it.

**The residual ambiguity is stated, not hidden.** The eight beauty-charm species
are fed by both sectors, so `24C + 26B = T` does not determine `C + B` for them.
Bracket: **414 counts of 53.66 M — 0.00077 %**, carried per row.

> **This is a reconstruction, not a re-extraction.** `STATE.md` pending item 9.

### Why every existing check was blind to it

- **`from_species == from_closure`** compares two views of the same files.
  Both are duplicated identically, so it holds exactly through a 24× error.
- **`central == sum(blocks)`** establishes that the addition is exact. Both
  sides carry the same duplicated data. `MONASH_CENTRAL_TABLE.md` read this as
  **"No loss, no duplication"** — the second half was exactly wrong.
- **`compare_subset_parent.py`** (E4's remedy) compares at an *expected scale
  factor*, with both sides replicated identically.
- **The duplication was known and misjudged.** `DESIGN_AND_RATIONALE.md` called
  it a "storage wart, not a correctness problem" at a stale factor of **18**.

> **The lesson: a self-check built from two views of the same file cannot detect
> anything the file does to both of them.**

---

## 2. Machinery fixes — each with the test that fails without it

| # | fix | the test, and what it catches pre-fix |
|---|---|---|
| **A12** | `decompose_with_block_sems.py` exit status reports I2, not only I3. `--i2-advisory` is the explicit opt-out | Ten blocks summing **exactly** to the central (I3 clean) with block 1 at 5 % (I2 flags). Pre-fix **rc=0**, 3 failures; post-fix **rc=4** |
| **A11** | `heavy_flavour_sign()` beauty convention corrected; validated against `species_ordinals_v2.json` (production `q_c`/`q_b`) **before** I2 runs | Worked examples as values: B⁺ → −1, Λ_b⁰ → +1. Pre-fix both inverted. Negative control rejects an inverted helper — without it the check passes for any helper |
| **A5** | Extraction requires the exact registry filename **set**, zero `PROJ_ERROR`, an exact projection count, and an existing decay map | A directory of 299 correct files + 1 stray: a naive count sees 300 and accepts; the set comparison rejects. Both asserted |
| **A4** | Closure gate takes a **required** expected-schema argument, enforced in wrapper *and* macro | Pre-fix a two-argument invocation was valid. The macro's check runs before any count is derived, so 1800/600 is never reached |
| **A8** | Four scripts `chmod +x`; R7 gains `--mode split`; R8 relabelled | Mode bits and shebangs pinned; R7/R8 corrections pinned. Pre-fix R6/R7/R10 exited **126** |
| **A7** | `make check` ends with an environment verdict and **fails** off-pin unless `HF_ALLOW_UNPINNED_ENV=1` | A fabricated on-pin environment passes with no escape hatch — so the off-pin failure is about the pin, not a script that always fails |

**A11 found a second defect while being fixed.** The helper sliced the decimal
string by length, reading five-digit excited **baryons** as mesons. ±14122
(Λ_c(2593)⁺) returned "not heavy" and **I2 skipped both rows entirely** — an
unchecked row is indistinguishable from a clean one. Digit extraction now
mirrors `DecodeHeavyContent`; coverage 200 → **202**.

**No committed map value changed**, verified rather than asserted: R5 rebuilds
v1.1 to `dd502a10c5932fff` and R6 rebuilds v2 to `c9593c9c0a7c4ec2`, both
byte-identical by `diff`, before and after the parsing change. The STOP
condition was not reached.

---

## 3. Recipes — every repo-only one executed as written

Transcript: `docs/history/transcripts/RECIPE_TRANSCRIPT_20260813.md`. **14 ran.**
R6, R7 and R10 no longer need a `python3` prefix to substitute for a missing
mode bit — that substitution is what the review had to do.

**R10 exits rc=1 by design** (it flags 30 bins); its documented positive check
`flagged=30 tested=88` is satisfied. Recorded because an `rc==0` verdict is the
wrong test there — `rc=0 is not evidence` running in the other direction.

**Two recipes were wrong, not just unrunnable:**
- **R7** defaulted to `dominant` mode and reproduced the v1.1 shares
  (D⁰ 28.1301) while claiming the v2 split shares (25.2435).
- **R8** does not compute what it was cited for. It prints
  `at_risk_pct=12.8396`, the **(C) chained history** row. The **0.0018 %**
  declared as THE NUMBER **has no committed derivation** and is now recorded as
  such. It was **not** reverse-engineered from its rounded value: that is how a
  wrong number becomes a certified one.

---

## 4. Documentation — the corrections that unblock reproduction

- **A3.** Blocks are **FILE/JOB** blocks (`canonical_slot % 10`), not
  `event_id % 10`. The event-modulo filter is off by default. File blocking
  retains job-level effects as **between-block scatter** rather than averaging
  them away, which makes it the **conservative** choice — and the implemented
  one. A third party following the old text would build different blocks.
- **A10.** The published central estimator is declared: **pooled union for the
  central, block SEM for the uncertainty** — *not* the mean of block ratios.
  Verified consistent in code (`Analysis_README`, `aggregate_m7.py`, the
  plotter) before declaring it; only the top-level contract disagreed.
- **A13.4.** The tune-causality contradiction is gone. Measured: **28 allowed
  differences across nine families, only 8 `ColourReconnection`**; `StringFlav`
  and `StringZ` set baryon production directly. **Bundle-to-bundle; junction
  formation cannot be isolated.**
- **A13.6.** "Experiment-comparable" defined at first use as a
  branching-weighted particle-level regrouping, with what is *not* modelled
  listed. **"What a detector would reconstruct" is withdrawn.**
- **A2.** M7 relabelled everywhere as an **inclusive-level** diagnostic.
  Verified: its only cut is `heavyIsFinal && q_sector != 0`. The prose claim
  that unresolved hadrons are "dropped" is corrected — only **trigger**
  candidates are; associates remain eligible.
- **B2/B3.** The stale 18× duplication note, the v2 schema-of-record row, the
  "No loss, no duplication" claim, and README's "entire extraction chain".

---

## 5. What this session did NOT establish

Stated because a correction record that reads as a clean bill of health is
worth less than none.

- **The corrected table has not been re-extracted.** It is an exact arithmetic
  inversion of the committed replicated CSV. The fixed extractor has never run
  against the 300 merged pair files.
- **Block SEMs are still the replicated ones.** `MONASH_CENTRAL_TABLE.md`'s
  SEM column was computed on the replicated product and is not corrected here.
- **The pair-level unresolved systematic does not exist yet** — scoped in
  `STATE.md`, not measured.
- **The environment was off-pin throughout**: ROOT 6.38.04 against a pinned
  6.30.01, no PYTHIA, no CVMFS. Every recipe run here is pure Python except
  `make test`. This is exactly the condition A7 now makes visible.
- **Untouched by instruction:** the plotting build (A6), `Paper/**` (A9),
  JUNCTIONS/CLOSEPACKING harvests — the last of which now *wait* for the
  corrected extractor.
