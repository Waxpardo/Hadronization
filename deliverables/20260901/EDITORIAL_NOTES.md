# EDITORIAL NOTES — the Overleaf-side matters, and the repository fact for each

Ruling R38: the paper lives in Overleaf and the repository produces files ready
to drop in. Every item below is therefore a matter for the owner. This file
states **what the repository measures**, with the file and line it measures it
at, and leaves the wording to him.

Ruling R34: where the paper text disagrees with a repository value, the
difference is an owner decision and **is never resolved silently**. Section 2
is that list.

The `paper/` snapshot read here is the owner's uncommitted bench working tree
at HEAD `3cccb75`, which is the current Overleaf state as it stands on the
bench. The live Overleaf document may have moved.

---

## 1. Disclosures the repository requires

### 1.1 G5 and G7 omit B_c⁻, and the caption must say so (ruling R43)

G5 and G7 carry **four** beauty associates where G4 and G6 carry five. The
missing one is B_c⁻, and it is missing from the two extreme-class beauty
columns only.

**The repository fact.** RUN-N's V-EXTREMES render refused the Λ̄_b trigger's
B_c⁻ associate in the 90–100 % class: the yield is exactly zero across all ten
blocks with coverage complete (`SUBSAMPLE_COVERAGE_FAILURE`, RUN-N report
§5.3). In 10⁸ JUNCTIONS events **no Λ̄_b trigger has a B_c⁻ associate in that
class**. The cell is empty by physics, so no y-window edit reaches it. R43
removed the associate rather than weakening the render gate; no empty-cell
admission code was written (R35).

The same sentence is **not** needed on G4 or G6, which keep B_c⁻.

### 1.2 The hang rate (ruling R41)

Recorded attempt attrition, per tune, from
`config/cr_holdout_policy_v1.json` (`observations`):

| tune | discarded | attempts | rate |
|---|---|---|---|
| MONASH | 0 | 1,000 | 0.00 % |
| JUNCTIONS | 63 | 1,063 | 5.93 % |
| CLOSEPACKING | 64 | 1,064 | 6.02 % |
| **all three** | **127** | **3,127** | **4.06 %** |

**The repository fact.** Every hang is in PYTHIA's `JunctionSplitting`: an
unbounded accept–reject loop in `splitJunGluons`, reached because the two
junction tunes set `ColourReconnection:allowDoubleJunRem = off`, which removes
the cheap removal path for a connected double-junction system
(`results/validation/generator/PYTHIA_JUNCTION_HANG_20260731.md:100-111`). That
is a deliberate physics setting from the QCD-CR tune, not a configuration
error. Completed files are conditioned **only** on zero hang-triggering events:
a failed attempt promotes no ROOT file, a missing logical slot is regenerated
under a new deterministic seed, and only promoted complete outputs named by the
sealed canonical manifest enter reduction (`config/cr_holdout_policy_v1.json`,
`handling`).

The attrition is disclosed as measured and is **not** corrected away or
converted into an event weight (same field). The hang hits dense-junction
topologies — exactly the configurations under study — which is why the rate
must be reported rather than corrected (`docs/GOLDEN_OUTPUTS.md:1067`, row N5).

**The wording is the owner's call.** R41 accepts these rates and leaves open
whether the disclosure reads "unmeasured" or "bounded, negligible". The
architect's completed-file conditioning bound is on record if the stronger
wording is wanted, and `ARCHITECT_OPEN_ISSUES_20260901.md` §1 argues it is the
highest-value page left to write. **It has not been written or checked**, and
it is not in this package.

### 1.3 The N_ch decay-policy mismatch (ruling R42)

**The repository fact.** The multiplicity counter counts prompt charged
particles under the heavy-hadrons-stable policy. The experimental primary
definition counts heavy-decay daughters, because open-heavy hadrons have
cτ₀ < 1 cm. A paired minimum-bias measurement on PYTHIA 8.317 puts the
undercount at **0.767 %**: (7.040 − 6.986) / 7.040, over 172,825 and 172,429
accepted INEL>0 events
(`results/validation/generator/NCH_DECAY_POLICY_BIAS_8317.md:47-58`; REPORTED
from that record, not re-measured by any recent session).

Three caveats belong in the disclosure, and all three are load-bearing:

- **The 0.767 % is minimum bias.** Nobody has measured the magnitude on the
  forced hard-heavy sample. It is **unmeasured, not small**.
- **The classes stay internally consistent**, because the percentile axis is
  built from the same counter for all three tunes.
- **R42 keeps the mismatch as measured and discloses it.** Properly defined and
  disclosed, this is not incorrect physics.

**The post-paper validation campaign.** R42 records one and **nobody has
scheduled it**. The design note matters, because the obvious approach does not
work: a full 3,000-job re-production with decays on cannot be paired event by
event against the production sample, since PYTHIA's single RNG stream means
"same seeds" stops guaranteeing pairing after the first event. The design that
works is a **paired two-pass** run — generate under the production policy,
count N_ch, then decay the stabilised hadrons in the *same* event with
`moreDecays()` and count again. One campaign, paired per event, measures both
the forced-sample bias and the per-class migration on the tune-local axis
exactly, and it could ride a future campaign as a cheap extra counter.

### 1.4 The ten-block statistics (ruling R39)

**The repository fact.** Pooled central value; SEM across ten blocks on nine
degrees of freedom; nonlinear quantities formed inside blocks
(`config/statistical_robustness_v1.json`, `method`). The supervisor approved
this scheme on 2026-08-30 (R39). Two anchors carry it, and each shows a
different half:

- `extraction/harvest_class_axis.py:114-121` is `sample_sem`, which returns
  `sqrt(sum((x-mean)^2) / (n(n-1)))` and refuses fewer than two blocks. With
  ten blocks the denominator is the nine degrees of freedom.
- `tools/build_canonical_manifest.py:281-287` is the **partition**, not the
  SEM: the blocks are `canonical_slot % 10`, so the ten are disjoint and
  exhaust the manifest by construction.

**The error bars in every figure of this package are statistical only.** The
systematics module is paused under R31, so no systematic uncertainty is
computed, drawn or quoted anywhere.

**Two things the owner should know before writing the uncertainty sentence.**

1. `config/statistical_robustness_v1.json` still carries
   `scientific_review_status: PENDING_FINAL_PHYSICS_STATISTICS_REVIEW` with
   `frozen: true`, and states that its boundaries "cannot support a publication
   claim until the final scientific reviewer explicitly accepts them". R39 is
   that acceptance, but the ruling lives in the architect's decision ledger and
   **the contract field still reads PENDING**. Closing that gap is on PHYS-1's
   list (`_briefs/BRIEF_PHYS1_20260901.md`), which runs after WRAP.
2. **No limitations paragraph exists.** Nothing in `docs2/paper/` states what
   the paper may and may not claim without systematics
   (`ARCHITECT_OPEN_ISSUES_20260901.md` §2). The argument that a differential
   MC-to-MC comparison cancels common systematics between tunes is available
   here — the three tunes share the generator, the cuts, the counter and the
   class definition — but it has not been made in writing.

---

## 2. Where the paper text and the repository disagree

Under R34 these are stated, never silently fixed. Each row was read at both
ends this session.

### 2.1 The generator-settings table, `paper/Model.tex:26-46`

| paper row | paper says | the repository measures | site |
|---|---|---|---|
| Collision system | pp | pp | cards `:18-19`, `Beams:idA = 2212`, `Beams:idB = 2212` |
| **Centre-of-mass energy** | **√s = 14 TeV** (`:34`) | **13.6 TeV** — `Beams:eCM = 13600` | all three cards `:17` |
| Beam IDs | 2212 / 2212 | same | cards `:18-19` |
| Baseline tune | `Tune:pp = 14` | same | cards `:20` |
| Hard charm | `HardQCD:hardccbar = on` | same | MONASH `:24` |
| Hard beauty | `HardQCD:hardbbbar = on` | same | MONASH `:25` |
| **Hard-process cut** | **`pTHatMin = 1.`** (`:39`) | **`PhaseSpace:pTHatMin = 2.`** | MONASH `:47`, JUNCTIONS `:68`, CLOSEPACKING `:84` |
| **Events per job** | **10⁶** (`:40`) | **100,000** | `docs/REPRODUCIBILITY.md:133` |
| **Jobs per tune** | **100** (`:41`) | **1,000 canonical slots** | `docs/REPRODUCIBILITY.md:133` |
| Events per tune | 10⁸ | 10⁸ | the product 1,000 × 100,000 |

Four rows disagree. Three of them matter beyond typography.

**√s.** The figures now draw `pp √s = 13.6 TeV` in their information block
(ruling R46), so a document carrying `:34` unchanged would state two different
beam energies, one in the table and one inside every figure. √s = 14 TeV also
appears at `paper/Model.tex:23` and in the G1 caption at `:129`.

**`pTHatMin`.** The threshold is not a detail: the repository chose 2.0 over
1.0 on a measurement, and the measurement is the defence of the percentile
axis. On PYTHIA 8.317, 20,000 events per point
(`results/validation/generator/PTHAT_MULTIPLICITY_SCAN_8317.md:27-33`):

| sample | dN_ch/dη | against minimum bias |
|---|---|---|
| minimum bias (`SoftQCD:inelastic`) | 6.968 | — |
| hard, `pTHatMin = 1.0` | 4.973 | **−28.6 %** |
| hard, `pTHatMin = 2.0` | 6.678 | **−4.2 %** |
| hard, `pTHatMin = 4.0` | 10.492 | +50.6 % |

At 1.0 the percentile classes would slice a distribution whose mean is nearly a
third below the one an experiment slices; at 2.0 they mean what they say. The
minimum-bias reference reproduces ALICE 13 TeV INEL>0 (6.94 ± 0.10), so the
counter is sound and the deficit is physical (`:35-36`). A referee who reads
`pTHatMin = 1.` next to a percentile-class analysis has a real objection, and
the campaign is not open to it.

**The job layout.** 10⁶ × 100 and 100,000 × 1,000 give the same 10⁸, so the
sample size in the paper is right and only the factorisation is wrong. The
factorisation is still worth correcting, because the small-job choice is the
answer to the hang disclosure in §1.2: smaller jobs limit the work lost to a
generator hang (`docs/REPRODUCIBILITY.md:133`).

### 2.2 The N_ch acceptance — the counter is |η| ≤ 1, not |η| ≤ 4

**This is the mismatch the repository has already been bitten by once.**

`paper/Model.tex:51` states the analysis selection as pT ≥ 0.15 GeV/c and
|η| ≤ 4. `paper/Model.tex:53` then defines N_ch "using prompt charged particles
**in the same kinematic acceptance**", and the G1 caption at `:129` writes it
out as |η| ≤ 4.

**The repository fact.** The event-activity classifier uses a **different and
narrower** window. The predicate is

```
CountsNchPrimaryChargedV1(isFinal, isCharged, hasHeavyConstituent, pt, eta, etaMax)
  = isFinal && isCharged && !hasHeavyConstituent && IsMultiplicityKinematic(pt, eta, etaMax)
```

(`generation/producer/HeavyFlavourUtils.h:557-562`, VERIFIED by reading the
enclosing predicate), with `kMultiplicityEtaCentral = 1.0` (`:524`). The
producer writes it as `multiplicity_primary_charged_eta10_v1`
(`generation/producer/heavyflavourcorrelations_status.cpp:713-714`), and
`config/multiplicity_percentile_classes_v2.json` names **that** counter as its
own. A second, wider counter at `kMultiplicityEtaWide = 4.0` (`:525`) is written
as `multiplicity_primary_charged_eta40_v1` and **does not define the classes**.

The header says why the two spellings are dangerous, at the constants
themselves: "a caption took 4.0 from the neighbouring context, and nothing could
notice, because nothing tied the label to the predicate"
(`generation/producer/HeavyFlavourUtils.h:470-474`). `Model.tex:53`'s "in the
same kinematic acceptance" is that sentence happening again.

**Heavy-flavour hadrons are excluded from the count**, for two reasons recorded
at the counting site
(`generation/producer/heavyflavourcorrelations_status.cpp:1026-1030`;
`generation/producer/HeavyFlavourUtils.h:515-521`): they are final here only
because their decays were disabled, and including them would correlate the
event-activity classifier with the heavy-flavour observable it classifies. The
paper must state this exclusion.

### 2.3 The p_T cuts are exclusive, and the trigger cut is not stated

**The repository fact**, read in the enclosing predicate
(`generation/producer/HeavyFlavourUtils.h:483-487`, VERIFIED):

```
IsCentralKinematic(pt, eta, trigger)
  = pt > (trigger ? kCentralPtMinTrigger : kCentralPtMinAssociate)
    && std::abs(eta) <= kCentralEtaAbsMax
```

with `kCentralPtMinTrigger = 1.0`, `kCentralPtMinAssociate = 0.15`,
`kCentralEtaAbsMax = 4.0` (`:477-479`). So:

- **trigger p_T > 1.0 GeV/c**, strictly greater;
- **associate p_T > 0.15 GeV/c**, strictly greater;
- **|η| ≤ 4.0**, inclusive, for both.

The constants are written into every merged pair file under the names
`trigger_pt_min_exclusive`, `associate_pt_min_exclusive` and
`eta_abs_max_inclusive` (`analysis/status_analysis_THnSparse_qq.C:1314-1316`) —
the exclusivity is in the field names, deliberately.

`paper/Model.tex:51` writes `p_T ≥ 0.15` (inclusive) for all final-state
particles and **does not mention the 1.0 GeV/c trigger cut at all**. Two
corrections: `≥` becomes `>`, and the trigger threshold needs stating.

### 2.4 The tune colour in six captions: JUNCTIONS is blue, not red

**The repository fact.** The palette is compiled and frozen under owner
decision O3 (`plotting/TunePlotStyle.h:24-27`, VERIFIED by reading):

| tune | colour | marker |
|---|---|---|
| MONASH | black (`kBlack`) | filled circle (20) |
| **JUNCTIONS** | **blue (`kBlue + 1`)** | filled square (21) |
| CLOSEPACKING | violet (`kViolet + 1`) | filled triangle (22) |

Six caption sites in the snapshot say otherwise:
`paper/Results.tex:93`, `:106`, `:127` and `:140` each read "JUNCTIONS (red)";
`:153` reads "RED = JUNCTIONS"; `:183` reads "Junctions (red or blue)". MONASH
black and CLOSEPACKING purple are correct throughout.

On the extremes canvases (G5, G7) the **marker fill** carries the multiplicity
class and the colour still carries the tune: the lowest-activity class draws the
open counterpart of its tune's marker and the highest draws the filled one
(`plotting/TunePlotStyle.h`, `OpenTuneMarker`). The canvas legend now names that
convention, so a caption need only not contradict it.

---

## 3. What the captions must now carry (rulings R46, R45)

The owner ruled the ROOT panel titles **off**. Identification is now stated
once each: one canvas information block (generator, system, √s, and the
axis-coverage sentence), one column header per column, one in-frame row label
per single-tune panel, and one canvas legend per canvas.

**Nothing was lost, only deduplicated — but what the figure no longer repeats,
the caption must now carry.** FIG-1D enumerated every fact in every retired
title and gave each one a destination; the list below is the set whose
destination is the caption
(`FIG1D_EVIDENCE_0e98a5b_20260901/phaseA/INFORMATION_LOSS_MAP.md` §6).

| figure | the caption must state |
|---|---|
| G2, G3 | that the panels are opposite-sign and same-sign azimuthal correlations; the multiplicity scope 0–100 %; that the lower row is the OS−SS difference; the trigger of each column, in words |
| G4, G6 | that the yields are multiplicity-integrated; that the columns are the meson-trigger and baryon-trigger groups; that the rows are the three tunes; that the bottom row is the tune ratio to MONASH |
| G5, G7 | the same, plus that only the lowest (90–100 %) and highest (0–1 %) N_ch classes are drawn and that open and filled markers separate them; **and the R43 disclosure of §1.1** |
| G8 | that the columns are the two flavours; that the quantity is the baryon-over-meson balancing-yield ratio; **which baryon each column plots** — Λ_b⁰ for beauty, Λ̄_c⁻ for charm; that the x axis is the tune-local multiplicity class |

`pp √s = 13.6 TeV` and the generator identity are **drawn in the information
block** and need not be repeated in the caption — but see §2.1, because the
table at `Model.tex:34` currently contradicts the block.

Two further caption facts the figures cannot state for themselves:

- **The multiplicity classes are resolved per tune**, each from its own merged
  `summed MULTIPLICITY` histogram, so absolute N_ch thresholds differ between
  tunes and are allowed to (`config/multiplicity_percentile_classes_v2.json`,
  `definition`; `plotting/improvedPlotting_THnSparse.C:2765-2772`). A caption
  that implies a common absolute axis would be wrong.
- **The error bars are statistical only** (§1.4).

---

## 4. Figures this repository does not produce

The coverage claim should be exact, so that no future session hunts for a
producer that does not exist. Of the eleven `\includegraphics` paths in the
snapshot, **eight are campaign products and all eight are in this package**.
The other three are not repository products:

| figure | its Overleaf directory | included at | what it is |
|---|---|---|---|
| `globalCanvasYieldsPDF_215.pdf` | figures/YieldsBalancing | `paper/Results.tex:170` | thesis-era, two tunes. No G-row produces it and no repository target names it. |
| `globalCanvasRelativeYieldsPDF_215.pdf` | figures/BaryonMesonRelativeYieldsBalancing | `paper/Results.tex:182` | the same |
| `runningCouplingQCD.png` | figures/Introduction-figures | `paper/Introduction.tex:8`, **commented out** | **owner-supplied illustrative material**, not a repository product. Now recorded as such in `docs2/paper/DELIVERABLES.md` (architect finding P1). |

The second column is the directory **Overleaf** keeps each file in, and it is
written without a code span on purpose: these three are not in this package.
`deliverables/20260901/figures/` holds only what the repository produced, so a
path written there as a code span would read as a package path and would be
absent. The full Overleaf paths are in `docs2/paper/DELIVERABLES.md`, which is
the byte-exact name manifest and the right place for them.

**The two `_215` figures are a content decision that has never been taken.**
They are two-tune thesis figures sitting inside a three-tune paper, and the
draft compiles only because the old files are in the tree. Either those sections
come out, or something must produce three-tune replacements — which is real
work, not editorial. This is the one place where "every figure the paper needs
is produced" is not yet true: precisely, it is **eight of ten physics figures**
(`ARCHITECT_OPEN_ISSUES_20260901.md` §4).

**One correction to the architect's coverage table.** It lists
`runningCouplingQCD.png` among the draft's includes. At `paper/Introduction.tex`
the whole figure environment is **commented out**: lines `:6-11` each begin with
`%`, the `\includegraphics` at `:8` among them. The file is present on the bench
at `paper/figures/Introduction-figures/runningCouplingQCD.png` (60,074 bytes).
So the draft currently includes **ten** figures, not eleven, and whether the
running-coupling figure returns is an owner decision. Measured this session.

---

## 5. Decisions still open, which this package does not take

- **The thirty G9 kinematic spectra have no destination.** They are produced,
  certified and delivered in `figures/Kinematic Plots/`, and the current draft
  includes none of them. Either they earn a place — supplementary material, an
  appendix, a QA figure — or they are not deliverables
  (`ARCHITECT_OPEN_ISSUES_20260901.md` §6). This package carries them so the
  decision can be taken with the files in hand.
- **G8's charm panel shares beauty's y-range**, so charm's data occupies the
  lower fifth of its panel. The common range is what makes the two flavours
  comparable. The architect's recommendation is to keep it and let the caption
  say so; it is the owner's call
  (`ARCHITECT_REVIEW_RUNN4B_20260901.md`, "the remaining presentational
  question").
- **The repository has no licence.** `git ls-files` finds no `LICENSE`, and
  `CITATION.cff` states that authorship, author order, affiliations, release
  identity and licensing are provisional and require approval. The repository is
  public. Without a licence, default copyright applies and nobody may legally
  reuse the code accompanying the paper
  (`ARCHITECT_OPEN_ISSUES_20260901.md` §5).
