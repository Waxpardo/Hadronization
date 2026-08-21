# The b-baryon particle/antiparticle advisory — diagnostic ladder

> ## ⚠ ITS NUMBERS ARE SUPERSEDED — 2026-08-11. Its CONCLUSION is confirmed.
>
> **Every ratio in this document was computed on the anchor extraction, whose
> baryon sector is now quarantined** (30 of 88 bins inconsistent with the merged
> parent, 16 deviating >2 % and up to 33 %, concentrated in baryons —
> `AnalysisScripts/anchors/extraction_dual/MANIFEST.md`, private error-ledger
> E4). **This is precisely the sector this document is about, so treat its
> individual numbers as indicative only.**
>
> *(2026-08-13: "30 of 88" is the retired binomial null. Under the robust null
> the same comparison flags 0 of 88 — a blind spot for broad defects, since the
> displacement is sector-wide, **not** a clearance. The quarantine and this
> supersession both stand; see private error-ledger entry E4.)*
>
> **The conclusion survives, because it was re-measured independently.**
> `docs/SIGMA_B_ORDERING_AND_ADJUDICATION.md` reproduces the spin-sorted pattern
> on (a) the merged MONASH central and (b) **1000 files of raw event records with
> no analysis chain at all**: Σ_b **26.59 % ± 0.24**, Σ*_b **10.51 % ± 0.19**,
> ground **0.83 % ± 0.11**, growing ~1.6× toward forward |η|. **Verdict: physics,
> remnant-fed.**
>
> **Quote the raw-count table, not this one.** Step 3's ladder logic — "excited
> far out of line with ground leans machinery" — reached the right place for the
> wrong reason: the machinery was clean and the *dataset* was not.

**Verdict: the asymmetry is REAL IN THE RAW WEIGHTS, not introduced by the map —
but by the owner's own step-3 criterion it leans MACHINERY, so it is reported
rather than parked.** Step 2 could not be run; see §2.

Triggered by `extraction/apply_decay_map.py`'s advisory, which flagged
Λ_b⁰/Λ̄_b⁰ = 1.111 after the conjugation fix (`docs/MAP_V1_CONJUGATION_BUG.md`).
Ladder specified by the owner; executed in order, then stopped.

**Scope: the MONASH anchor extraction only** (`extraction_dual`). **Not three
tunes.** This matters and is the reason step 2 is blocked.

---

## 1. STEP 1 — raw or map-introduced? **RAW. Continue.**

Particle/antiparticle ratios computed **directly from `per_species.csv`, with no
map applied at all**:

| species | kind | particle | anti | ratio |
|---|---|---|---|---|
| **Λ_b⁰** | ground | 158,262 | 157,092 | **1.007** |
| Ξ_b⁰ | ground | 29,822 | 28,210 | 1.057 |
| Ξ_b⁻ | ground | 29,562 | 27,378 | 1.080 |
| **Σ_b⁻** | excited | 16,640 | 9,958 | **1.671** |
| **Σ_b⁰** | excited | 16,510 | 9,932 | **1.662** |
| Σ*_b⁰ | excited | 24,180 | 20,358 | 1.188 |
| D⁰ | ground | 13,315,752 | 13,298,376 | 1.001 |
| B⁰ | ground | 938,548 | 936,156 | 1.003 |

**The map is exonerated.** The asymmetry exists before any mapping.

> **And it explains the advisory's shape.** Raw **Λ_b⁰ is 1.007 — symmetric.**
> The 1.111 the advisory reported is *inherited*: the map chains the strongly
> asymmetric Σ_b/Σ*_b **into** the Λ_b bin, exactly as designed. **The advisory
> was pointing at a real feature of the input, through a correct mapping.**

---

## 2. STEP 2 — per-tune decomposition: **CANNOT BE RUN. Blocked, not skipped.**

Junction baryon-number transport predicts **CR tunes ≫ MONASH**. That test needs
three tunes.

**The anchor extraction is single-tune.** `docs/EXTRACTION_CONVENTIONS.md` §6
records it as MONASH only; the merged three-tune output does not exist yet (the
merge is running). **Step 2 is deferred to the post-merge extraction**, where it
is cheap — the same script over three tunes' `per_species.csv`.

> **What can be said now, and it is not nothing: the asymmetry is present in
> MONASH — the tune WITHOUT colour reconnection or junctions.** Whatever
> produces it does not require the junction transport mechanism, because that
> mechanism is not active in this sample. **Whether some other transport is
> responsible is a physics question and the owner's.**

**A provenance gap found while checking this, and it matters for review:**
`f3_runs/extraction_dual/` contains **only three CSVs — no log, no manifest, no
record of which directories or tune produced them.** The tune is known only from
handoff prose. **The weights behind every number in
`docs/EXTRACTION_CONVENTIONS.md` have no committed provenance.** See §5.

---

## 3. STEP 3 — ground vs excited: **FAR out of line ⇒ leans MACHINERY**

Asymmetry *A* = (p−a)/(p+a), σ from Poisson counts.

> **⚠ ANNOTATED 2026-08-13 — divide every σ in this table by ~5.03.**
> Private error-ledger entry **E6**: these counts are replicated-era extraction
> weights, and replication scales a Poisson/binomial significance by **√R**
> (measured 5.03×). **The ratios and the *A* percentages are unchanged** — a
> uniform factor cancels in both — so the *pattern* this table is read for
> survives intact. Only the σ column deflates:
>
> | as recorded | deflated |
> |---|---|
> | 2.1 σ (Λ_b⁰) | 0.4 σ |
> | 9.2 σ (Λ_c⁺) | 1.8 σ |
> | 7–9 σ (Ξ_b) | 1.4–1.8 σ |
> | 10–18 σ (Σ*_b) | 2.0–3.6 σ |
> | 31–41 σ (Σ_b) | **6.2–8.2 σ** |
> | 16–19 σ (Ξ'_b) | 3.2–3.8 σ |
> | 16 σ (Ω_b⁻) | 3.2 σ |
>
> **The document's conclusion does not depend on the σ column** — it is a
> *ranking* argument (excited far out of line with ground), and the ranking is
> carried by the ratios, which do not move. **The spin-1/2 Σ_b block remains
> significant even deflated.** This is an annotation of the arithmetic, not a
> reopening: the document is already marked SUPERSEDED for its individual
> numbers, and its conclusion was re-measured independently on raw generator
> records (R1/R2), which are unaffected.

| group | species | ratio | *A* | significance |
|---|---|---|---|---|
| **ground** | Λ_b⁰ | 1.007 | **0.37 %** | 2.1 σ |
| ground | Λ_c⁺ | 1.011 | 0.57 % | 9.2 σ |
| ground | Ξ_c⁺ / Ξ_c⁰ | 1.003 / 0.994 | 0.15 % / −0.31 % | 1–2 σ |
| ground | Ξ_b⁰ / Ξ_b⁻ | 1.057 / 1.080 | 2.8 % / 3.8 % | 7–9 σ |
| **excited, spin-3/2** | Σ*_b⁻ / Σ*_b⁺ / Σ*_b⁰ | 1.108 / 1.096 / 1.188 | 4.6–8.6 % | 10–18 σ |
| **excited, spin-1/2** | **Σ_b⁻ / Σ_b⁰ / Σ_b⁺** | **1.671 / 1.662 / 1.468** | **19–25 %** | **31–41 σ** |
| excited, spin-1/2 | Ξ'_b⁻ / Ξ'_b⁰ | 1.611 / 1.800 | 23–29 % | 16–19 σ |
| ground (low stats) | Ω_b⁻ | 3.375 | 54 % | 16 σ |

**Σ_b at 25 % against Λ_b at 0.37 % is ~68× out of line, at 41 σ. This is not
statistics.** By the owner's criterion — *excited far out of line with ground
leans machinery* — **machinery is implicated, so this does not park.**

### The pattern is structured, and the structure is the finding

Sorting by **light-diquark spin** rather than by excitation:

| light diquark | states | asymmetry |
|---|---|---|
| **spin-0** (antisymmetric) | Λ_b, Ξ_b | **0.4 – 3.8 %** |
| **spin-1** (symmetric) | Σ_b, Ξ'_b, Ω_b, Σ*_b | **4.6 – 54 %** |

**The split tracks the light-diquark spin, not the excitation energy and not the
heavy quark.** Given that this project's primary convention *is* a
diquark-structure grouping, a diquark-correlated artefact is exactly the kind of
thing that would matter, and exactly the kind that could be either real
fragmentation behaviour or a counting error.

### Aggregate balance — no gross conservation violation

| sector | particle | anti | ratio |
|---|---|---|---|
| charm meson | 55,362,120 | 55,232,400 | 1.002 |
| charm baryon | 2,687,784 | 2,624,328 | 1.024 |
| **beauty meson** | 6,647,812 | 6,656,000 | **0.999** |
| **beauty baryon** | 354,692 | 318,708 | **1.113** |
| beauty ALL | 7,002,504 | 6,974,708 | 1.004 |

**Mesons are symmetric in both sectors; baryons are not, and beauty baryons far
less so than charm baryons.** Totals stay near unity only because mesons
outnumber baryons ~19:1.

---

## 4. CAVEAT THAT CONSTRAINS EVERY NUMBER ABOVE

**These are extraction weights — the species decomposition of the compensation
observable — NOT inclusive yields.** A particle/antiparticle asymmetry here is
not necessarily a yield asymmetry: it can also arise from the trigger side of
the pair selection. **A spin-dependent pattern is precisely what a
selection-side effect could look like**, so the yield interpretation is not
assumed. Distinguishing them would need the inclusive yields, which this
artifact does not carry.

---

## 5. WHAT I RECOMMEND, AND WHAT I DID NOT DO

**Not parked to POST_SUBMISSION**, because the owner's step-3 criterion
implicates machinery. **Also not escalated as a bug** — I have no evidence of an
error, only a pattern that the criterion says warrants attention.

**Cheapest discriminating next steps, in order:**

1. **Step 2 on the merged output** (three tunes). If the CR tunes show the same
   ~25 %, junction transport is not the driver — MONASH already says as much.
2. **Compare against inclusive yields** for the same species, which settles §4's
   ambiguity: if inclusive Σ_b is symmetric and only the compensation weight is
   asymmetric, the effect is selection-side.

**Bounded here as instructed; the ladder was run and stopped.** The excited
b-baryon weight cannot move a published number — Σ_b + Ξ'_b + Ω_b together are
**~0.06 % of total weight**.

**Provenance action for the external review:** `extraction_dual`'s three CSVs
should be **committed with a manifest** recording tune, directories, input
count, and the reader's commit. As it stands, the anchor of every published
table number is an uncommitted file in scratch with no recorded origin.
