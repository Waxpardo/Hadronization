# Anchor extraction `extraction_dual` — manifest

> ## ⛔ QUARANTINED FOR CHARGE-RESOLVED USE — 2026-08-11
>
> **Do not use these weights for ANY baryon-sector or charge-resolved
> quantity.** Against the merged MONASH central at scale **9.999**,
> `extraction/compare_subset_parent.py` flags **30 of 88 testable bins at |z| > 4**,
> **16 of them deviating by more than 2 % and up to 33 %**, median 3.1 %.
> **The large deviations are almost entirely baryons**; flagged mesons deviate
> sub-percent. Σ̄_b⁻ is +10.4 % (z = +11.0); Ξ*_c⁺ is +6.3 % (z = +11.6).
>
> *Deflated 2026-08-13 (private error-ledger entry **E6**, ÷5.03 for E5 replication):
> z = +11.0 → **+2.19**, z = +11.6 → **+2.31**, and the −7.4 σ below →
> **−1.47 σ**. **The percentages do not move** — a uniform factor cancels in a
> ratio. Genuine 1/10 subsets of the same replicated data give 32–40 flags where
> this anchor gives 30.*
>
> **This supersedes the first characterisation ("one bin"), which examined only
> the six Σ_b bins.**
>
> **ANNOTATED 2026-08-13 — recalibrated null, count NOT rewritten.** The flag
> count above is the binomial null, which was retired for pair counts that day.
> Under the robust null now used for integrity work (median-centred, MAD-scaled
> σ) the same comparison flags **0 of 88**: the measured width is **σ̂ = 4.399**
> binomial sigmas and the largest bin reaches **|z| = 2.83**.
>
> **THIS DOES NOT LIFT THE QUARANTINE — it is a property of the instrument, not
> of the data.** A robust width estimated from the sample absorbs a defect that
> is *broad*, and this one is: 30 of 88 bins displaced together, so no single bin
> stands out from a bulk that is itself displaced. The quarantine rests on the
> **size and locality of the deviations — 16 bins above 2 %, up to 33 %, almost
> entirely baryons — which are unchanged.** Both counts are pinned as checks 1
> and 4 of `tests/test_compare_subset_parent.py`.
>
> It produced a **−7.4 σ result that two traceable datasets contradict**
> (`docs/SIGMA_B_ORDERING_AND_ADJUDICATION.md` §2b, private error-ledger entry E4).
>
> **The AGGREGATES are verified sound** — recomputed on the merged central the
> second-branch number moves 12.8451 → 12.8396 % and map-v2 D⁰ 25.2425 →
> 25.2435 %. **Nothing published from these files needs revision**, and they
> remain valid as the historical cross-check for totals and species shares.
>
> **No archaeology.** The provenance is unrecoverable (§2) and the merged
> extraction supersedes these files entirely.

**These three CSVs are the weights behind every number in
`docs/EXTRACTION_CONVENTIONS.md`, `docs/SECOND_BRANCH_WEIGHT.md`,
`docs/MAP_V2_RESULT.md` and `docs/B_BARYON_ADVISORY_DIAGNOSTIC.md`.** Until
2026-08-11 they existed only as uncommitted files in Nikhef scratch, so no
number in this repository could be reproduced from the repository alone.

Committed for the external review. **Copied verbatim — not regenerated.**

| | |
|---|---|
| source | `stbc:/data/alice/ipardoza/f3_runs/extraction_dual/` |
| copied | 2026-08-11 |
| produced by | `extraction/extract_species_decomposition.py` |

---

## 1. VERIFIABLE FACTS — computed from the files, not asserted

| file | rows | sum | sha256 |
|---|---|---|---|
| `per_species.csv` | 91 | **129,883,844** (`total`) | `6137f6bc1f661ffdf26167a440091229f1466c87e2a8e4b50d096d66c3f45ac1` |
| `per_category.csv` | 6 | **129,883,844** (`from_species`) | `fe8d7dc577c56fd3e4ef9d090ee37b120b578d8fb2e08cdf8a5b08cd2f48db12` |
| `per_observable.csv` | 30 | **129,883,844** (`total`) | `46bca45240ffb49662de3b9ab49be157ce2f0a0b08043e67bbe6f70f1d3f6303` |

**All three sum to the same total — mutually consistent.** That total is the one
quoted throughout the extraction documents.

**To reproduce any published table from these files:**

```bash
extraction/apply_decay_map.py --map AnalysisScripts/decay_parent_map_v1_1.json \
  --weights AnalysisScripts/anchors/extraction_dual/per_species.csv
extraction/second_branch_weight.py \
  --per-species AnalysisScripts/anchors/extraction_dual/per_species.csv
```

Both fail closed unless they reproduce the expected table first.

---

## 2. ⚠ WHAT IS NOT RECORDED — state this plainly to a reviewer

**The source directory contained these three CSVs and NOTHING ELSE** — no log,
no manifest, no invocation record. The following are therefore **not recoverable
from any artifact**:

- **which tune** produced them;
- **which analysis directories**, or how many;
- the **reader commit** and its arguments;
- the **date** of the run.

**The only claim on record is prose:** `docs/EXTRACTION_CONVENTIONS.md` §6 states
*"MONASH only, one directory, 100 inputs"*, while
the dated private generational handoff, Section 6, says *"exact on four directories — all
MONASH, all one tune"*. **These agree on MONASH and single-tune; they disagree on
the directory count, and nothing in the artifact settles it.**

> **Do not treat the tune or the input count as verified.** They are inherited
> from handoff prose. Every downstream document that says "MONASH anchor" rests
> on this, and it is why those documents label the scope a limitation rather
> than a result.

**This is fixed going forward, not retroactively:** the post-merge extraction
must write an invocation manifest beside its outputs, per the standing
invocation-manifest rule. **Regenerating these particular numbers is not
possible without knowing the inputs**, which is the point.

---

## 3. ⚠ `per_observable.csv` IS SUPERSEDED

It carries the experiment-comparable grouping **as computed under decay map
v1**, which did not conjugate antiparticle decays
(`docs/MAP_V1_CONJUGATION_BUG.md`) — so it contains the **D⁰ = 45.95 %** figure
and the 4.49× charge asymmetry.

**It is committed as the historical record, not as a current result.** The
current tables are regenerated from `per_species.csv` with map **v1.1**
(conjugation fixed) or **v2** (splits); see `docs/MAP_V2_RESULT.md` §3.

`per_species.csv` and `per_category.csv` are **map-independent** — they are keyed
by species ordinal and by structural category, neither of which consults the
decay map — and are therefore unaffected by the v1 defect.
