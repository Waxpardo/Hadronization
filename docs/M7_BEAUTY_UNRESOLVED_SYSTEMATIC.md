# M7 beauty — the unresolved-origin systematic in the beauty sector

> # ⚠ SCOPE — this is an INCLUSIVE-LEVEL diagnostic, NOT a bound on the pair observable
>
> **Relabelled 2026-08-13 (external review finding A2). The measurement is
> sound; the claim attached to it was not.**
>
> `Validation/MeasureUnresolvedSystematic.C` counts **every final open-heavy
> hadron** — its only cut is `heavyIsFinal && q_sector != 0`. It applies
> **none** of the production selection: not direct-primary, not central
> ground-state, not acceptance, not trigger pT, not multiplicity, not pairing,
> not OS−SS. Its "resolved" population is merely `origin != 0`, which includes
> origins that would **not** be accepted as selected-hard triggers.
>
> **What these numbers therefore are:** the inclusive rate of unresolved-origin
> open-heavy hadrons, and the shift in the **inclusive** baryon fraction if
> those hadrons could be recovered. Both are real, both are measured at full
> scale, and both are worth having.
>
> **What they are NOT: a bound on the systematic of the OS−SS pair
> observable.** A global rate cannot bound a multiplicity-localized effect.
> Concretely: if unresolved trigger candidates sit preferentially in the
> highest-multiplicity class and preferentially have same-sign partners, the
> inclusive rate and baryon fraction can stay at the quoted sub-percent level
> while the high-multiplicity OS−SS yield moves substantially. Nothing here
> excludes that.
>
> **Do not cite this document as the unresolved-origin systematic on the
> observable.** That measurement is pending and scoped in the private branch-state record.



**Status: MEASURED at full scale, n=10 blocks per tune, three tunes.** Closes
the gap named in the dated private generational handoff, Section 2.2 — the systematic
existed for charm only, because the macro cut on `heavyQc`.

Pre-registration: `docs/M7_BEAUTY_PREREGISTRATION.md`, committed **before**
deployment or submission. Charm companion: `docs/M7_UNRESOLVED_SYSTEMATIC.md`.

---

## 1. THE TABLE

Central values from **pooled counts** over all ten blocks; uncertainties are the
**block SEM** over n=10 (`stdev/√10`). 1000 files per tune, 300 per block-job.

| tune | unresolved rate % | baryon % (measured) | baryon % (inclusive) | **relative shift %** |
|---|---|---|---|---|
| **MONASH** | 0.0115 ± 0.0003 | 4.8715 ± 0.0037 | 4.8721 ± 0.0037 | **0.0141 ± 0.0011** |
| **JUNCTIONS** | 0.1023 ± 0.0011 | 32.0174 ± 0.0115 | 32.0218 ± 0.0115 | **0.0140 ± 0.0008** |
| **CLOSEPACKING** | 0.0983 ± 0.0011 | 32.3720 ± 0.0068 | 32.3766 ± 0.0068 | **0.0143 ± 0.0007** |

Integer counts and the enrichment of the dropped sample:

| tune | unresolved_n | resolved_n | unresolved baryon % | enrichment |
|---|---|---|---|---|
| MONASH | 3,170 | 27,645,508 | 10.852 | **2.23×** |
| JUNCTIONS | 28,315 | 27,659,509 | 36.387 | 1.14× |
| CLOSEPACKING | 27,184 | 27,631,664 | 37.066 | 1.15× |

> **The systematic to quote for beauty is ~0.014 %, and it is the same in all
> three tunes.** For charm the same quantity is 0.045 % (MONASH) to 0.55 % (CR)
> — tune-*dependent* by an order of magnitude. **Beauty's is both smaller and
> flat.**

---

## 2. SCORED AGAINST THE PRE-REGISTRATION

| # | registered | outcome |
|---|---|---|
| **B1** | unresolved RATE: CR ≫ MONASH | **HIT.** 0.1023 / 0.0983 vs 0.0115 — a factor **8.9** |
| **B2** | relative SHIFT: CR ≫ MONASH | **MISS. The shift is FLAT** — 0.0140 / 0.0143 / 0.0141, all three inside one SEM of each other |
| **B3** | unresolved sample baryon-enriched, all tunes | **HIT.** 1.14× / 1.15× / **2.23×** — but the tune ordering is the reverse of B1's |
| **B4** | beauty counts ≪ charm, so relatively larger SEMs | **HIT.** resolved_n 27.6 M vs charm 198 M (7.2×); the shift's fractional SEM is **4.9 %** for beauty against **0.47 %** for charm |

**B2 is reported as a miss, not rationalised.** It did not invert — MONASH is
not *larger* — it went flat, which the pre-registration did not contemplate.

---

## 3. WHY B2 FAILED — AN EXACT IDENTITY, THEN AN OBSERVATION

**The algebra first, because it is certain.** With *f_r* the resolved baryon
fraction, *f_u* the unresolved baryon fraction and *r* the unresolved rate:

```
inclusive = f_r(1-r) + f_u·r
relative shift = (inclusive - measured)/measured = r · (f_u/f_r - 1) = r · (enrichment - 1)
```

**This is an identity, not an approximation.** It reproduces all six published
values — three beauty, three charm — to their printed precision:

| tune | r | E−1 | r·(E−1) | reported |
|---|---|---|---|---|
| MONASH (b) | 0.0115 | 1.2277 | 0.0141 | 0.0141 |
| JUNCTIONS (b) | 0.1023 | 0.1365 | 0.0140 | 0.0140 |
| CLOSEPACKING (b) | 0.0983 | 0.1450 | 0.0143 | 0.0143 |

**Now the observation.** B2 followed from B1 only under the tacit assumption
that enrichment is roughly tune-independent — which is what charm does
(1.45–1.53, a 5 % spread). **In beauty it is not:** MONASH's enrichment excess
is **9.00×** that of JUNCTIONS, while its rate is **8.90×** smaller.

**The two factors are inverse to within 1 %, so their product — the systematic —
is flat.**

> **Whether that near-exact reciprocity is mechanism or coincidence is a physics
> question, and it is the owner's to answer, not mine.** What is established
> here: the identity is exact, the two ratios are 8.90 and 9.00, and the
> resulting shift is constant across tunes to within its SEM. **n=3 tunes is not
> a demonstration of a law.**

**Consequence for the paper either way:** the beauty unresolved-origin
systematic does **not** differ by tune, so unlike charm it **cannot bias a
tune comparison** — it shifts all three tunes by the same 0.014 %. That is a
stronger statement than a small systematic, and it is the useful one.

---

## 4. THE MONASH-ZERO CONTINGENCY DID NOT FIRE

The owner's instruction provided for MONASH beauty being **exactly zero**
unresolved across all ten blocks, in which case the SEM degenerates and a
one-sided 95 % Poisson upper limit (~3.0 events) was to be quoted with the
result declared *bounded, not measured*.

**It does not apply. MONASH beauty unresolved_n = 3,170 over the ten blocks**,
with a well-defined block SEM.

**Where the zero came from:** the single-file pre-flight read
(`hf_MONASH_job000.root`) gave ub=0, um=0, and that was carried into the
pre-registration as the n=1 structural read. **At 1000 files it is 3,170 — about
3.2 per file.** A zero on one file was a small-number artefact, not the tune's
behaviour. **Recorded because the n=1 reading nearly became an assumption about
the measurement.**

---

## 5. THE BEAUTY-BARYON EFFECT, IN PASSING

Not what M7 measures, but it falls out of the same counts and is larger than the
charm equivalent:

| | MONASH | CR tunes | CR/MONASH |
|---|---|---|---|
| **beauty** baryon fraction % | 4.87 | 32.02 / 32.37 | **6.6×** |
| charm baryon fraction % | 4.65 | 17.85 / 17.29 | 3.8× |

**Colour reconnection moves the beauty baryon fraction by 6.6×, against 3.8× for
charm.** Quoted as an observation from the M7 counts; the paper's own extraction
is the place this belongs, not here.

---

## 6. METHOD AND PROVENANCE

| | |
|---|---|
| macro | `Validation/MeasureUnresolvedSystematic.C`, sector-parametrised, sha256 `0d03d191231163a5…` |
| counts macro | scratch `m7_counts.C`, sha256 `d7be6731b44f5b95…` |
| driver | `m7b_runs/m7b_block.sh`, one canonical block per job so the job boundary and the n=10 SEM boundary coincide |
| cluster | `5425788`, 10 jobs, all `rc=0` |
| aggregator | `extraction/aggregate_m7.py`, fail-closed below 10 blocks and on mixed sectors |

**Positive checks, all passed before any number was read out:**

| check | result |
|---|---|
| charm regression (P1) | parametrised macro at `sector="c"` reproduces the **frozen** charm-only macro field-for-field — **EXACT** |
| aggregator regression (P2) | reproduces the published charm table exactly: 0.0847 / 1.1530 / 1.1355 %, shifts 0.0451 / 0.5497 / 0.5125 % |
| beauty distinct (P3) | resolved_n 27,806 vs charm 197,743 on the same file — the sector argument takes effect |
| per-block cross-check (P4) | **30 `XCHECK_OK`** (3 tunes × 10 blocks), zero `XCHECK_FAIL`; counts macro and percentage macro agree, and both report the same sector |
| completeness | **300 counted files in every block**, 300 count lines each; all ten logs `# sector=b`; both macro sha256 identical across all ten |
| n=10 (P5) | aggregator fail-closes below ten blocks; ten present |

**The frozen checkout was never modified.** Macros were deployed to scratch
`/data/alice/ipardoza/m7b_runs/`; the checkout was read for `setupEnv.sh` and
the block manifests only. Jobs carried
`Requirements = (Machine != "wn-sate-072...")`, keeping them off the node the
3000-directory gate was running on. **No seeds burned** — this reads existing
raw files.
