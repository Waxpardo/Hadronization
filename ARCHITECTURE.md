# Architecture — what this repository measures, and how

**Written for a physicist who has never used ROOT or PYTHIA.** Nothing here
needs to be run to be understood. For *how to rebuild the numbers*, see
[`README.md`](README.md). For *where the project stands*, see
[`STATE.md`](STATE.md).

---

## 1. THE QUESTION, IN ONE PARAGRAPH

When a heavy quark (charm or beauty) is produced in a proton–proton collision,
it is produced together with its antiquark partner. Each of the two ends up
inside a hadron. **If one of them ends up inside a *baryon*, what does the other
one end up in — a baryon too, or a meson?**

That correlation is sensitive to how quarks are assembled into hadrons
(*hadronisation*), and in particular to **colour reconnection** — the mechanism
by which colour-charge connections between partons are rearranged before
hadronisation. We compare three PYTHIA tunes:

| tune | headline difference |
|---|---|
| **MONASH** | the baseline; no junction-forming reconnection |
| **JUNCTIONS** | reconnection that can form string junctions — which favour baryons |
| **CLOSEPACKING** | a different reconnection model, close-packing of strings |

> ### This comparison is BUNDLE-to-BUNDLE. Junction formation cannot be isolated.
>
> **Stated here, at first use, because this document previously contradicted
> itself** (review finding A13.4): it said the tunes "differ in exactly that
> machinery", asserted "They do", and then conceded in the next paragraph that
> the result could not be attributed to junctions. Both cannot be true. **The
> concession is the correct half**, and the claim of an isolated mechanism is
> withdrawn.
>
> **Measured from `config/tune_difference_allowlist_v1.json`: 28 allowed tune
> differences across nine parameter families**, of which only 8 are
> `ColourReconnection`. The rest are `ClosePacking` (7), `StringZ` (3),
> `StringFlav` (3), `BeamRemnants` (2), `StringFragmentation` (2), `StringPT`
> (1), `MultipartonInteractions` (1) and `Ropewalk` (1). **`StringFlav` and
> `StringZ` set baryon production and the fragmentation function directly** —
> they are not incidental to a baryon observable, they are alternative
> explanations for it.
>
> So the honest claim is: **these three tune bundles differ in their heavy-baryon
> partnering, and this measures by how much.** Attributing that difference to
> junction formation specifically would need a single-switch variation, which
> this campaign does not contain. Also recorded in `REPRODUCIBILITY.md` §5.

**What the paper quantifies** is therefore the size of the bundle-to-bundle
difference in the OS−SS partnering observable, not a mechanism attribution.

---

## 2. THE TWO PROGRAMS

**PYTHIA** is an event generator: a simulation that produces individual
proton–proton collisions, particle by particle, from first principles plus
tuned phenomenological models. We use **version 8.317, unmodified, built from
the official upstream tarball** whose checksum is recorded. It writes out a full
record of every particle in every event, including which particle came from
which.

**ROOT** is the analysis and storage framework used in particle physics. It
provides the file format (`.root`), the histogram types, and the C++ interpreter
that runs the analysis macros. We use **6.30/01**.

**Why the analysis is two programs and not one.** Generation is expensive and
happens once; analysis is cheap and is re-run whenever a question changes.
Keeping them separate means a new question does not require regenerating
300 million events. The boundary between them is a **raw file**: PYTHIA writes
it, everything downstream only reads it.

---

## 3. THE PIPELINE — five stages

```
  ┌─────────────┐   raw/          ┌─────────────┐   per_job/       ┌─────────┐
  │ 1 GENERATE  │ ──3000 files──▶ │ 2 ANALYSE   │ ──3000 dirs────▶ │ 3 MERGE │
  │  PYTHIA     │   300M events   │  one pass   │   ×300 files     │         │
  └─────────────┘                 └─────────────┘                  └────┬────┘
                                                                        │
                    ┌──────────┐        ┌────────────┐    3 centrals    │
                    │ 5 PLOT   │ ◀───── │ 4 EXTRACT  │ ◀── + 30 blocks ─┘
                    └──────────┘        └────────────┘
```

### Stage 1 — `generation/` — make the events

| | |
|---|---|
| **input** | a *tune card* (`generation/cards/*.cmnd`): the complete PYTHIA configuration |
| **what happens** | PYTHIA simulates collisions at 13.6 TeV. For every heavy quark it records which hadron finally carries it, and the full ancestry chain that got it there |
| **output** | `raw/<TUNE>/hf_<TUNE>_jobNNN.root` — **1000 files per tune, 100 000 events each** |

**Every job records what it ran against** — the commit, the card's checksum, the
producer binary's checksum, the random seed — and refuses to start if any of
them has moved. That is why a number can be traced back to the exact code that
made it.

### Stage 2 — `analysis/` — reduce events to pair counts

| | |
|---|---|
| **input** | one raw file |
| **what happens** | for every event, find the heavy hadrons; decide which is the *trigger* and which is the *associate*; classify both; fill histograms |
| **output** | one directory of **300 "pair files"**, one per (trigger species, associate species) combination |

**This is where the physics definitions live.** Three of them matter:

- **Heavy flavour is signed by quark content, not by electric charge.** The
  charm content of a hadron is `q_c = n_c − n_cbar`. So `B⁺` has `q_b = −1`
  while `Λ_b⁰` has `q_b = +1` — they are an *opposite-sign* pair. **This is easy
  to get backwards.**
- **The trigger must have resolved hard-scattering ancestry; the associate need
  not.** That asymmetry is deliberate: requiring it of both would delete the
  same-sign term by construction.
- **Ambiguous ancestry is never guessed.** If the record cannot say which hard
  quark a hadron carries, it is marked `kUnresolved`. A permissive tie-break
  would bias the very tune comparison being made.

  > **CORRECTED 2026-08-13 — this said unresolved hadrons are "dropped". They
  > are not, in general** (review finding A2). Only **trigger** candidates are
  > removed, and only because a trigger must have selected-hard ancestry.
  > **Unresolved associates remain eligible** — associates are not required to
  > carry hard ancestry at all, which is the deliberate asymmetry described just
  > above.
  >
  > **The cost is NOT bounded by `docs/M7_UNRESOLVED_SYSTEMATIC.md`**, which
  > this line used to cite as though it were. M7 is an *inclusive-level*
  > diagnostic over single particles; it does not apply the trigger/associate
  > selection and cannot bound a multiplicity-localized OS−SS effect. See that
  > document's own scope banner, and `STATE.md` for the pair-level measurement
  > that is still pending.

### Stage 3 — `merging/` — combine 3000 directories into 33 objects

| | |
|---|---|
| **input** | 3000 per-job directories |
| **what happens** | add the histograms together, in two groupings |
| **output** | per tune: **one "central"** (all 1000 files) **and ten "blocks"** (100 files each) |

**Why ten blocks, and why it is the whole statistical design.** The blocks are
ten *disjoint, exhaustive* subsets of the **input files**, assigned by

```text
block = canonical_slot % 10          # tools/build_canonical_manifest.py
```

Every nonlinear quantity is computed **inside** a block, and the spread across
the ten gives the uncertainty (the standard error, 9 degrees of freedom).

> **CORRECTED 2026-08-13 — these are FILE/JOB blocks, not event-ID blocks**
> (review finding A3). This document and `REPRODUCIBILITY.md` both said
> `event_id % 10`. They were wrong; `analysis/Analysis_README.md` had it right
> all along. Each analysis job processes **all** events in its assigned input
> file, and the event-modulo filter is **off** by default
> (`run_status_analysis.sh`: `event_filter_modulo=0`, `remainder=-1`).
>
> **The two designs are not interchangeable.** File blocking keeps a job's
> events together, so a per-job or per-batch effect — a seed family, a tune
> initialisation, a host — shows up as **between-block scatter**. Event-modulo
> blocking would spread that same effect across all ten blocks and shrink the
> apparent spread. **File blocking is therefore the conservative choice**: it
> lets job-level structure inflate the SEM rather than hiding it. It is also
> the one actually implemented, which matters more.
>
> A third party who followed the old text would build different blocks and
> could get different errors from identical data.

> **This matters because the quantities are ratios.** The uncertainty on a ratio
> is not obtainable by propagating bin errors when the numerator and denominator
> share events. Ten repeats of the whole measurement give the honest spread.
> **The central and the ten blocks must agree exactly** — the blocks sum to the
> central, bin by bin — and that identity is checked before any number is read
> out. Note what that identity does and does not establish: it shows the
> addition is exact. It cannot show the entries are unique
> (`docs/ERROR_RECORD.md` E5).

**THE PUBLISHED CENTRAL ESTIMATOR IS THE POOLED ONE.** Stated here because the
choice was previously ambiguous across documents (review finding A10):

| quantity | how it is formed |
|---|---|
| **central value** | from the **complete pooled union** of all files for that tune — a ratio of summed numerator to summed denominator |
| **uncertainty** | **SEM across the ten block estimators**, sample stdev / √10, dof 9 |

**It is NOT the unweighted mean of the ten block ratios.** That is a different
estimator, and with unequal block denominators it gives a different answer. The
code is consistent on this — `extraction/aggregate_m7.py` pools its counts,
the plotter computes the pooled yield, and `analysis/Analysis_README.md` says
so explicitly. `extraction/decompose_with_block_sems.py` prints the block mean
**beside** the pooled value precisely so that a material divergence is visible;
where they differ, that is reportable, not a rounding detail.

### Stage 4 — `extraction/` — turn histograms into the paper's numbers

| | |
|---|---|
| **input** | the merged central and its ten blocks |
| **what happens** | project onto the species axis; group species into observables; compute shares and their block errors |
| **output** | the decomposition tables |

**The species axis** is a list of **202 heavy hadron species**, fixed in advance
and digest-pinned (`646f310f78126267`). Every merged file carries that digest
inside it, so a file and the axis it was filled against cannot drift apart
silently.

**The two groupings — and they answer different questions.** This is the single
most important thing to understand about the results:

> ### "Experiment-comparable" — the precise definition, at first use
>
> **It means: a branching-fraction-weighted regrouping of particle-level
> species onto the ground state each one decays into.** That is all it means.
>
> **What it does NOT include** (review finding A13.6). It does **not** simulate:
> decay kinematics; detector acceptance; reconstruction efficiency; resolution;
> or migration of the pair observable between multiplicity bins. Nothing here is
> passed through a detector model, because there is no detector model.
>
> **The phrase "what a detector would reconstruct" is withdrawn.** It claimed a
> detector simulation the project does not have and never had. The map folds
> species weights through branching fractions at truth level — useful, and a
> long way from a reconstructed yield.

| | **diquark-structure** | **experiment-comparable** |
|---|---|---|
| groups by | what the generator actually made | which ground state each species decays into, weighted by branching fraction |
| e.g. `D*⁰` | its own category (an excited vector) | folded into `D⁰`, which it decays to |
| completeness | **a partition** — the categories sum to 100 % | **a selection** — the rows do *not* sum to 100 % |
| the awkward fact it exposes | ~47 % of the compensating flavour sits in states the central selector excludes | that weight is not lost, it is reassigned to the ground states those states decay into |
| **not modelled** | — | decay kinematics, acceptance, efficiency, resolution, bin migration |

> **Neither is more correct.** The structural one says what happened; the
> experiment-comparable one says which ground states the weight would arrive at.
> **The project publishes both, always** — and labels the second as a selection
> wherever it appears, because a reader who sums its column and finds less than
> 100 % will otherwise think weight went missing.

### Stage 5 — `plotting/` — figures

Reads the merged outputs and produces the paper figures.
`plotting/run_paper_plots.sh` is the entry point.

---

## 4. WHAT KEEPS THE ANSWER HONEST

Five mechanisms, each of which has caught something real:

| mechanism | what it does |
|---|---|
| **Pinning** | the generator version, the producer binary's checksum, the card's checksum and the commit are all recorded per job and re-checked by the worker. A rebuild between submission and execution stops the job |
| **Closure** | the ten blocks must sum to the central exactly — **2100 content comparisons and 1500 invariant comparisons**, and the counts themselves are checked, because a run resolving against the wrong schema would report 1800/600 and *look* like a pass |
| **Fail-closed tools** | tools refuse rather than guess: no overflow bin for an unmapped species, no fabricated uncertainty from a single block, no non-integer input to a counting model |
| **Pre-registration** | expectations are written down *before* the run, so a result cannot be quietly reinterpreted afterwards. Misses are recorded as misses |
| **The error record** | `docs/ERROR_RECORD.md` names every mistake that reached a number, who caught it, and the check that now prevents it. **It is bidirectional on purpose** |

> **The lesson the project paid most for**, and the reason `ERROR_RECORD.md`
> exists: *a reimplementation check proves agreement, not correctness.* Two
> independent implementations of the same misreading agree perfectly. What
> caught the decay-map defect was a check on the **physics** — every decay
> product must carry the parent's heavy-quark sign — not a check on internal
> consistency.

---

## 5. WHERE THINGS ARE

| directory | stage | holds |
|---|---|---|
| `generation/` | 1 | the PYTHIA producer, the tune cards, Condor submission |
| `analysis/` | 2 | the one-pass reduction |
| `merging/` | 3 | the merge driver and its ROOT macros |
| `extraction/` | 4 | the species decomposition, decay maps, block SEMs |
| `plotting/` | 5 | figure macros and their configurations |
| `AnalysisScripts/` | — | **the frozen artifacts**: the species axis, the decay maps, and `anchors/` — committed inputs and run outputs that make every published number reproducible from this repository alone |
| `Validation/` | — | ROOT audits and the closure checks |
| `tools/` | — | campaign management, submission rendering, guards, `doctor` |
| `config/` | — | signed registries and contracts |
| `tests/` | — | 30 Python contract tests + 5 C++ |
| `docs/` | — | the active record |
| `docs/history/` | — | session archaeology: handoffs, audits, superseded studies |
| `attic/` | — | code with no live consumer, **kept rather than deleted** |

**`AnalysisScripts/` keeps its old name deliberately.** It holds the frozen
artifacts, and 63 references across the tools and tests resolve against that
path. Moving it would buy tidiness at the cost of touching every recipe that
regenerates a published number.
