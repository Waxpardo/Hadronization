# Literature positioning — what is already published, and what is ours

**Written 2026-08-18** from a full-text read of the closest prior work, not from
its abstract. Feeds the manuscript introduction and the Codex II prompt.

> **Method note.** Every "remains ours" claim below was checked against the full
> text of arXiv:2507.21014. **One did not survive** and is reclassified. That is
> the reason for reading the body rather than the abstract: the abstract does not
> mention the species decomposition, and the paper does it in detail.

---

## 1. THE CLOSEST PRIOR WORK — arXiv:2507.21014

Sheibani, Pruneau, Gonzalez, Basu, Dobrin, Patley, Nandi, Dash,
*"Probing Partonic Evolution and Hadronization via Balance Functions and
Correlations of Charmed Hadrons"* (hep-ex, 28 July 2025).

**This paper must be cited as the direct antecedent of our observable.** It is
the same construction on the same generator family.

### 1.1 What they do

| | |
|---|---|
| system / energy | pp, **√s = 13 TeV** |
| generator | **PYTHIA 8.3** |
| species | **charm only** — D⁰, D±, D_s±, Λ_c± |
| observable | balance function `B₂^(α\|β̄)(Δy,Δφ) = A₂^(α\|β̄) − A₂^(ᾱ\|β̄)`, with `A₂^(αβ) = C₂^(αβ)/⟨N₁^β⟩` |
| differential in | **Δy and Δφ** |
| acceptance | **none** — "integrated over the full range of transverse momentum production, pT > 0, the full azimuth … as well as the full range of particle production in rapidity" |
| event selection | minimum bias, plus a **p̂_T-reweighted** biased sample (`(p̂_T/p̂_T,Ref)^n`, n = 2 and 8) |
| model variations | **Lund a and b**, `probQQtoQ`, `ProbStoUD`, MPI (`expPow`, `pT0Ref`), `Reconnection` mode 2 |
| uncertainties | **sub-sample technique only** — "the full dataset is divided into several statistically independent sub-samples … the resulting spread is used to calculate the final uncertainties" |

### 1.2 The observable is structurally OUR observable

Their `A₂ = C₂/⟨N₁^β⟩` is a per-trigger normalised associated density, and the
balance function is the opposite-sign minus same-sign difference of it. **That is
the same construction as our balancing yield** `(N_OS − N_SS)/N_trig`, differing
in that they keep it differential in (Δy, Δφ) while we integrate the Δφ spectrum
to a single number per trigger.

**The manuscript must say this plainly rather than let a reader discover it.**
Our contribution is not the invention of the observable.

### 1.3 ⚠ They also integrate it

They present the **cumulative integral of B_s(Δy) over a symmetric rapidity
window**, and quote balance fractions from it — *"Pythia predicts that the
emission of a Λ_c⁺ is expected to be balanced by a D⁰ with a probability of
∼45 %, whereas charm balancing emissions by Λ_c⁻, D⁻, and D_s contribute
approximately 30 %, 20 %, and 5 %"*, with ~85 % of Λ_c⁺ balanced overall in
unbiased events.

So *"integrating the balance function"* is not new either. **What differs is the
axis of integration**: theirs is over rapidity separation; our V-INTEGRATED is
over **multiplicity classes**, which they never bin in.

---

## 2. CLAIM-BY-CLAIM VERIFICATION

| claim | verdict | evidence from the full text |
|---|---|---|
| **Beauty sector with quark-content signing** | ✅ **REMAINS OURS** | The words *beauty*, *bottom* and *B meson* **do not appear anywhere** in the paper. Their associate list is D⁰, Λ_c⁻, D⁻, D_s, and they explicitly bound it: *"Although other higher charmed mass states exist, they would be challenging in the context of BF studies because the list of final states is open and inclusive."* |
| **Multiplicity-class differential** | ✅ **REMAINS OURS** | No binning in charged-particle multiplicity or event activity anywhere. Their only event-class axis is the p̂_T reweighting (n = 2, 8), which biases hardness, not activity. |
| **Mechanism-family comparison** | ⚠️ **REMAINS OURS, but narrow the wording** | See §2.1 — their "mode 2" is genuinely ambiguous and the claim must be written to hold either way. |
| **Species decomposition of the compensating partner** | ❌ **NOT OURS — they do this** | Figure 9 shows B_s(Δy) for Λ_c as associate with separate curves per balancing species, and the conclusions quote the 45 / 30 / 20 / 5 % split. **This claim must be withdrawn from the manuscript's novelty list and the paper cited for it instead.** Ours differs only in being done in the beauty sector and per multiplicity class. |
| **Measured systematics program** | ✅ **REMAINS OURS** | They report *statistical* uncertainties from sub-sampling and evaluate **no systematic sources**. Our six-source pre-registered programme with measured (not assumed) variations has no counterpart here. Note the sub-sample technique itself is common to both — do not present *that* as ours. |

### 2.1 The colour-reconnection ambiguity — UNRESOLVED FROM THEIR TEXT

The mechanism claim turns on what their colour-reconnection setting is. **The
paper does not say.** The only appearance of it anywhere in the document is one
Table 1 row, quoted verbatim:

> `Reconnection | mode 2 | Color reconnection`

There is **no** PYTHIA settings string (`ColourReconnection:mode` never appears),
**no** citation of a CR model, and **no** occurrence of *junction*, *QCD-based*,
*beyond leading colour*, *CR-BLC*, *gluon move*, *reconnectRange*, *Mode 0* or
*Mode 3* anywhere in the text.

Two readings, with opposite consequences:

| reading | what it is | junctions? |
|---|---|---|
| `ColourReconnection:mode = 2` | PYTHIA's **gluon-move** model | **no** |
| Christiansen–Skands QCD-CR **"Mode 2"** | a tune of `ColourReconnection:mode = 1` | **yes** |

**Inference, stated as inference.** Table 1's other rows are bare PYTHIA
parameter *names* — `expPow`, `pT0Ref`, `probQQtoQ`, `ProbStoUD` — so
`Reconnection` most plausibly denotes `ColourReconnection:mode`, making **mode 2
the junction-free gluon-move model**. That is a reading of the table's
convention, **not** something the paper states, and it should not be asserted in
the manuscript as though it were.

**Write the claim so it holds either way.** Both readings leave intact:

- **close-packing is absent** from their study on any reading;
- there is **no systematic comparison across mechanism families** — at most one
  CR setting alongside Lund-parameter variation, never MONASH vs junctions vs
  close-packing as alternatives;
- the comparison is **not per multiplicity class**, because they have no class axis;
- **beauty** and the **multiplicity differential** stand regardless.

> **Safe wording:** *"a systematic comparison of hadronization mechanism families
> — junction formation and close-packing against the Monash baseline — resolved
> per multiplicity class"*. **Unsafe wording:** *"they do not use junctions"*,
> which their text does not support either way.

---

## 3. WHAT THE INTRODUCTION MUST CONCEDE

1. The balance-function / per-trigger OS−SS construction is **established**, and
   2507.21014 applies it to charm in pp with PYTHIA 8.3.
2. **Integrating** the balance function and quoting balance fractions is
   established (their cumulative-integral figure).
3. **Decomposing the balancing partner by species** is established **in charm**.
4. The **sub-sample uncertainty technique** is shared, not distinctive.

## 4. WHAT SURVIVES AS OURS — the honest four

1. **The beauty sector.** Entirely absent from 2507.21014. Combined with
   quark-content signing of the trigger–associate pair, this is the clearest
   distinction.
2. **The multiplicity-class differential**, on common absolute N_ch classes ruled
   by a frozen boundary artifact — an axis they do not have.
3. **Systematic comparison across hadronization mechanism families** (junctions,
   close-packing) *resolved per multiplicity class* — worded per §2.1 so it holds
   whichever way their "mode 2" resolves.
4. **A measured systematic-uncertainty programme.**

> **Sharpest single sentence for the introduction:** the balance-function
> construction and its charm application exist; **what does not exist is the same
> observable in the beauty sector, resolved in event activity, and compared
> across hadronization mechanism families rather than across Lund parameters.**

---

## 5. THE ADJACENT CITATION SET

| reference | what it is | why it is cited |
|---|---|---|
| **arXiv:2408.16447** — Földvári, Varga, Vértesi, *"Event-activity-dependent beauty-baryon enhancement in simulations with color junctions"* | model study, **beauty and charm**, **colour junctions** (CR-BLC), **event-activity differential** | **The closest work on our axes** — beauty + junctions + event activity together. It is a **baryon-to-meson ratio** study, not a balance function, and that is the distinction to state. Cite whenever junction-driven beauty-baryon enhancement is invoked. |
| **arXiv:2602.03637** — Behera, Khuntia, *"Jet-associated Balance Functions of Charged and Identified Hadrons in pp Collisions at √s = 13.6 TeV using PYTHIA8"* | model study, **light flavour** (π, K, p), balance functions **inside jets**, **binned in jet charged multiplicity**, CR-tune comparison | Balance functions **at our exact energy**, and **multiplicity-differential** — but jet-frame and light-flavour. Cite to show multiplicity-differential balance functions exist, and to place ours as heavy-flavour and event-activity rather than jet-multiplicity. |
| **arXiv:2410.19416** — ALICE, charm meson–baryon azimuthal correlations | **measurement**, charm correlations | The experimental anchor for charm correlation measurements; grounds the feasibility argument. |
| **JHEP 04 (2026) 164** — close-packing, light flavour | close-packing mechanism, light flavour | The mechanism paper behind the CLOSEPACKING tune; cite where the mechanism is introduced. |

> **Positioning against 2602.03637 needs care.** It is at 13.6 TeV, uses balance
> functions, and *is* multiplicity-differential. The distinctions are real —
> light flavour, jet frame, jet multiplicity rather than event activity — but
> "multiplicity-differential balance functions are new" would be **false** as
> stated and must not appear.

---

## 5.1 REVISED INTRO FRAMING — extend, do not claim

The introduction should position this work as **extending** their charm
balance-function programme, not as introducing the observable:

> *Balance functions of charmed hadrons in pp collisions have been studied with
> PYTHIA 8.3 [2507.21014], including the decomposition of which species balances
> a given trigger. We extend that programme in four directions: to the **beauty
> sector** with quark-content signing of the trigger–associate pair; to an
> **event-multiplicity differential** on common absolute N_ch classes; to
> **discrimination between hadronization mechanism families** rather than
> parameter variation within one; and with a **measured systematic-uncertainty
> programme**.*

Their Λ_c split (Fig 9; D⁰ ≈ 45 %, Λ_c⁻ 30 %, D⁻ 20 %, D_s 5 %) is **cited as
the antecedent**. Ours differs in being resolved **per multiplicity class** and
**across mechanisms**, where theirs is a single static decomposition.

## 6. FOR THE CODEX II PROMPT

- Do **not** claim the observable, its integral, or the species decomposition as
  novel. Claim the **sector**, the **axis**, the **mechanism comparison**, and the
  **systematics**.
- Cite 2507.21014 in the first paragraph that introduces the balancing yield.
- Cite 2408.16447 wherever junctions and beauty baryons appear together.
- Cite 2602.03637 wherever "multiplicity-differential balance function" is said.
- The Λ_c balance fractions (45/30/20/5 %) are a **published comparison point**;
  our charm numbers can be checked against them, and any disagreement is a
  finding worth reporting rather than smoothing.
