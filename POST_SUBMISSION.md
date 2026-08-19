# Post-submission — open, but no paper claim depends on it

**Produced:** 2026-08-04, session v5, at `e690e17`.
**Rule:** nothing here blocks the paper. Nothing here should be worked before
`RELEASE_BLOCKERS.md` is empty. The defence against an endless improvement loop
is that the blocker list is finite and closed; this file is where everything
else waits.

---

## Chain map — established this session, recorded so nobody re-derives it

**Live THnSparse chain** = the five macros `plotting/run_paper_plots.sh`
actually invokes:

| Macro | Reads | Has it run against merged output from *this* pipeline? |
|---|---|---|
| `improvedPlotting_THnSparse.C` (`:307`, `:340`) | `complete_root` | **Yes** — HF_PT2 merged, v4 section 4 (`pair=BplusBcminus.root ... n=10/10`) |
| `Plot_MultiplicityDistribution_PercentileBoundaries.C` (`:419`) | `complete_root` | **Yes** — `multiplicity-boundaries` GREEN, exit 0 |
| `Plot_InclusiveKinematicSpectra_Raw.C` (`:442`, `:465`) | raw + sidecars | **No** — blocked, blocker B3 |
| `FinalAnalysis/Plot_MultiplicityDistributions_TwoSamples.C` (`:492`) | — | Slated for retirement (v4 section 9, item 8) |
| `FinalAnalysis/Plot_SelectedParticleYields_IndependentVsCombined.C` (`:506`) | **`AnalyzedData`** (`:154`) | **No — this is the only live-chain macro reading the legacy product**, and it is exactly the one already slated for retirement |

**Not in the live chain** (no `run_paper_plots.sh` target):
`attic/plotting/improvedPlotting.C`, `Plot_KinematicSpectra_THnSparse.C`,
`Plot_FlavourClosure.C`, `attic/plotting/B_Balancing_GeneralPlotting.C`.

> **Amended 2026-08-17 by the triage pass.** `PlottingWizard.C`,
> `combinedCanvasPlots.C` and `ListHistos.C` were on this list and are now
> removed from `HEAD` — no consumer, no recipe, no recorded run
> (`docs/REMOVALS.md`). **`improvedPlotting.C` was deliberately NOT removed**,
> on the strength of correction 1 below: it reads `complete_root`, the same
> merge product the live path consumes, which makes it a cross-check rather
> than dead code. That sentence is the reason it survived the sweep.

**Two corrections to the framing the brief carried:**

1. The premise "the legacy `AnalyzedData` product" versus merged output is
   **almost inverted**. Only *one* live-chain macro reads `AnalyzedData`
   (`Plot_SelectedParticleYields_IndependentVsCombined.C:154`), plus the dormant
   `PtMultiplicity/Build_HF_CombinedSubsamplesFile.C:1206`. Everything else,
   **including the predecessor `improvedPlotting.C`**, reads `complete_root` —
   the same merge product the live path consumes. This confirms v3 section 8's
   finding at `improvedPlotting.C:246,260` and is why Q4 must be kept.
2. `Plot_FlavourClosure.C` still has no target (v4 section 6b, decided but not
   implemented).

---

## Carried from the handoff's pre-seeded list

- **Audit Q1, Q3, Q6, Q7, Q9** — `docs/audit/REPO_AUDIT_c1bb0d9.md`.
- **`improvedPlotting_THnSparse.C:457`** `GetObjectOrThrow` — returns an
  escaping pointer used by 10 call sites, so it needs a signature change rather
  than a local `delete`. Leak site, dormant path.
- **`Plot_KinematicSpectra_THnSparse.C:394`** — same leak class, not in the live
  chain.
- **`make docs-check`**.
- **Key-level sidecar sweep** beyond what a claim requires. Only
  `merge_provenance.json` has been done (11 keys, clean). The general sweep is
  large; blocker B3 covers the one sidecar a claim actually depends on.
- **Remaining leak sites in dormant macros** — v4 section 7c.

---

## The MONASH 49x merge step — unexplained, but a much sharper target than that

**Deferred 2026-08-05 because no pre-submission decision depends on it, NOT
because it is understood.** The `THnSparse` chunking hypothesis (handoff v7
§9d) was **falsified** this session — see `docs/handoffs/HANDOFF_20260805_v8.md`
§3. Nothing has replaced it. Whoever returns to this starts from here.

**Three constraints, all measured, that any mechanism must satisfy:**

**1. The excess is pure CPU and adds no I/O.** CPU/wall across the scaling
series is 0.70–0.93 in the normal regime and **0.989 / 0.987** at MONASH's 50
and 100 input points. Whatever switches on spends CPU and never waits.

**2. The excess scales as sqrt(N), not as a fixed offset and not with the
work.** Decomposing MONASH into a JUNCTIONS-like baseline plus an excess, using
CPU (`user+sys`) since the excess is pure CPU:

| inputs | MONASH CPU | JUNCTIONS CPU (baseline) | excess |
|---|---|---|---|
| 50 | 4448.89 s | 146.20 s | **4302.69 s** |
| 100 | 6362.98 s | 343.17 s | **6019.81 s** |

**Excess ratio for a doubling = 1.399, against sqrt(2) = 1.414 — within 1.1 %.**
So it is neither a one-off cost nor proportional to the work: **it scales
roughly with the square root of input count and switches on somewhere in
(25, 50].** Wall-clock gives the same ratio, 1.399.

**3. It is MONASH-only.** JUNCTIONS is flat at 11.4–17.0 ms per elementary
merge across a tenfold input range. MONASH matches it at 10 and 25 inputs
(13.55, 12.72 ms) and is 306.0 / 217.2 ms at 50 / 100.

**4. IT DOES NOT REPRODUCE IN v3 — added 2026-08-09, and it is the sharpest of
the four.** The v3 species scaling series measured MONASH at 50 inputs and the
anomaly is simply absent:

| | v2 @50 (HF_PT2_INT) | **v3 @50 (HF_RUN3_V1)** |
|---|---|---|
| per elementary merge | 306.0 ms | **108.29 ms** |
| CPU/wall | **0.989** — the anomaly's signature | **0.716** — normal band |
| wall | 4498.15 s | 1591.88 s |

**v3/v2 = 0.354.** All three v3 points sit in the normal CPU/wall band (0.813,
0.897, 0.716). **Constraint 1 — "the excess is pure CPU" — has no excess to
describe here.**

**Both known biases run the conservative way**, which is what makes this usable:

- **v3 carries strictly MORE content.** It adds the 202-bin
  `hFlavourClosureSpecies` beside an `hFlavourClosure` the contract keeps
  byte-identical. More sparse content, less cost.
- **The v3 point was measured on a batch node**, which is the *slower* host —
  ~2x on per-file rate against the login node the v2 series used. A same-host
  v3 number would be lower still.

**The confounds, stated rather than buried.** The two series are not the same
measurement in three respects: **schema** (v2 vs v3 objects), **campaign**
(HF_PT2_INT vs HF_RUN3_V1 — different events, though **both at 100k events per
input file**, so input counts are directly comparable), and **host**. Any of the
three could carry the effect. What the comparison establishes is **not** that the
species object fixed anything — it is that **the 49x step is not an intrinsic
property of merging 50 MONASH inputs at 100k events each**, which is how it has
been read for four generations.

**Bearing on the untested candidate below:** v3 files carry an *additional*
202-bin sparse, so total per-file sparse content is higher, and the step is
absent. That is weak evidence against any mechanism keyed to aggregate sparse
size — though the candidate is specifically about `hFlavourClosure`'s own bins,
whose *structure* is unchanged while their *contents* differ by campaign. **Not
decisive either way. Still parked; no investigation authorised.**

**Untested candidate, recorded so it is not re-derived:** `THnSparse` bin lookup
uses a `TExMap` hash (`fBins`) with collision chaining; a load-factor threshold
crossing would degrade find-or-create toward a chain scan, and MONASH carries
~1.4–1.9x JUNCTIONS' bin count at equal input counts. **No measurement supports
this. Do not write it up.**

> **If this is ever unparked, the cheapest discriminating experiment is now
> obvious:** re-run the v2 *schema* at 50 inputs on HF_RUN3_V1 data, or the v3
> schema on HF_PT2_INT data. Either one separates schema from campaign in a
> single measurement. The v2 series' own inputs are gone, but HF_PT2_INT's
> per-job directories may not be.

### Localising it is a one-literal change, not new instrumentation

**`MergeAnalysisObjects.C:362` already emits per-input progress** —
`Merged i/N files into <path>`, every 10 inputs. It is suppressed only because
**`MergeCanonicalAnalysis.C:73` passes `verbose = false`**. (Handoff v7 §9e's
claim that the macro emits only `CANONICAL_MERGE_SUMMARY` is wrong.)

So: copy the macro to scratch, flip that literal to `true`, run at 50 inputs
through a timestamping wrapper, **and retain the output directory** (see the
harness rule below). That gives 10-input-granularity localisation of the step
for the cost of one 4500 s run and no code written.

---

## Five sibling expected-output literals in the closure wrapper — B12's class, unfired

**Found by the expected-output-literal sweep, 2026-08-08. Deferred: none has
fired, and none gates submission.**

**B12's fix derived one field and left five siblings of the identical class.**
`Validation/validate_pair_block_closure.sh:67` now reads
`object_content_sumw2_closure_checks=$(( closure_content_objects * 300 ))` — the
stale `1500` is genuinely fixed — but the same pinned line still carries:

| literal | what it encodes |
|---|---|
| `central_pair_files=300` | the pair count |
| `block_pair_files=3000` | pair count x 10 blocks |
| `additive_metadata_closure_checks=3600` | pair count x 12 |
| `invariant_metadata_checks=600` | pair count x 2 |
| `source_filter_contract_checks=300` | the pair count |
| the bare `300` inside the derived expression | the pair count again |

**The failure geometry, which is the point:** every one is a function of the
**pair count**, so **all five break simultaneously on a single pair-count
change** — and a future editor will see five failures from one cause and be
tempted to patch them one at a time. This is the same geometry that produced
B12: `7cf9f86` added an object to every pair file and broke `1500`. Adding or
removing a *pair* breaks these.

**The derivation source already exists and is already trusted.**
`AnalysisScripts/GeneratedPairRegistry.h` declares the pair set, and
`tools/merged_pair_provenance.py:57-67` already reads it **and cross-checks the
extracted filename count against the declared `std::array<PairDefinition, N>`
size**, raising if they disagree. Deriving these five from the same source is
the fix; it needs no new contract.

**Sweep non-result, recorded as one:** `validate_pair_block_closure.sh:69` is
the **only** exact-match assertion of another component's output anywhere in the
tree outside `tests/`. No other shell wrapper pins a summary line; the Makefile
pins none. **B9's argument-value sweep would not have found any of this** —
these are output literals, not passed arguments, which is why the two sweeps are
separate exercises.

**Not deferred with these:** the failure-path `rm -f` found in the same file is
**B13 in `RELEASE_BLOCKERS.md`**, fixed at sync.

---

## Harness rule — a diagnostic harness retains its outputs unconditionally

**Recorded 2026-08-05 because the same harness destroyed its own evidence
twice, on two different code paths, and the second time was after the first
was "fixed".**

`/data/alice/ipardoza/scaling_series.sh` (untracked, lives outside the Nikhef
checkout):

1. **Failure path, v1.** The harness `rm -rf`'d its work directory
   unconditionally. v1 passed a placeholder manifest sha, `MergeCanonicalAnalysis.C`
   correctly rejected it, all 8 points failed at ~3 s — **and the harness
   deleted the log that said so.** Self-documented at `scaling_series.sh:7-9`.
2. **Success path, v2 — still live as of this writing.**
   `scaling_series.sh:36` reads
   `if (( RC == 0 )); then rm -rf "$W"; else echo "  RETAINED $W" >> "$OUT"; fi`.
   The fix added retention on failure and left deletion on success. This is
   what deleted the 25- and 50-input MONASH merges — **precisely the two
   directories needed to localise the 49x transition**, and the reason handoff
   v7 §9d could only record the chunking mechanism as *supported*, not
   *established*. The current run deleted them a second time.

**The rule:** a harness whose purpose is diagnosis retains every output
unconditionally and lets the operator clean up. **You cannot know in advance
which run you will want to inspect** — that is the definition of a diagnostic
run. Deletion-on-success is the worse of the two failure modes, because it
throws away exactly the runs that worked and are therefore worth measuring.

**Corollary for disk:** retention is bounded and cheap here — a scaling stage
is ~1 GB, the whole 8-point series under 10 GB, against `/data/alice` free
space. The deletion was never buying anything that mattered.

**Scope note:** `merge_root_files.sh` already gets this right in the
production direction — it retains stages on failure by design
(`merge_root_files.sh:148,164`) — but it promotes on success, which is correct
for a *production* harness. The distinction is diagnosis vs production, not a
blanket rule against cleanup.

---

## Added this session

- **`flavour-closure` as a target, split from the figure** (v4 section 6b,
  decided, not implemented). The numerical closure check belongs in the
  validation layer where it can fail a run; the plotting target then renders
  what the check already verified. No paper claim currently depends on it —
  `Plot_FlavourClosure.C` produces no figure the manuscript cites.
- **Fossil `1000000` in `Plot_InclusiveKinematicSpectra_Raw.C:501,564,566,575,663`**
  — owner has pre-approved deriving these from the seal. Not a blocker because
  the target it lives in is already blocked by B3; fix them together.
- **`Main:numberOfEvents = 1000000` in all three tune cards.** Cosmetic only:
  the renderer materialises an effective card with `--events` substituted
  (`render_production_submit.py:230`), so production runs 100000. But the
  literal is the same fossil shape as the paper's C2 and will mislead the next
  reader of the cards.
- **Duplicate LaTeX labels in the paper.** Seven figures in `Results.tex` all
  carry `\label{fig:placeholder}` (`:50,:73,:94,:107,:128,:141,:154`).
  A build-quality problem, not a claim problem.
- **Figure path contains a space** — `Model.tex:130`,
  `figures/Kinematic Plots/MultiplicitySpectrum_Shared_shape.png`.
- **`Model.tex:131` caption/definition mismatch.** The caption describes the
  multiplicity figure with `|eta| <= 4`, while `:55` defines the primary
  `N_ch` counter as `|eta| < 1` with `|eta| < 4` only as a cross-check. The
  figure is plotting the cross-check counter. Worth reconciling; no numeric
  claim rests on it today.
- **`Results.tex` narrative omits CLOSEPACKING entirely** (`:162-166` discuss
  only MONASH vs JUNCTIONS) while every figure shows three tunes. Becomes a
  blocker the moment the results text stops being a placeholder.
- **`/data/alice/ipardoza/producer_e54b27bb_HF_PT2.bak`** — copy of the HF_PT2
  producer binary taken before the rebuild, outside the checkout. Safe to
  delete; kept because it is the binary that produced all promoted data.
- **`/data/alice/ipardoza/a2_multiplicity/`** — the A2 wrapper, submit file and
  logs, deliberately outside the checkout so the tree stays clean. Keep until
  B4 is closed.

---

## Per-tune CPU guard — moved here from RELEASE_BLOCKERS.md, 2026-08-05

Owner's decision on the measured tail: the flat 3600 s guard is **not**
killing healthy jobs, so this is production hygiene, not a blocker.
Implement after the post-merge sync, alongside B2 and B9.


Replace the flat `MAX_CPU = 3600` with a per-tune guard at **5x that tune's
measured median**:

| Tune | median | **guard @5x** | observed max (n~100) | est. max @n=1000 | headroom |
|---|---|---|---|---|---|
| MONASH | 377 s | **1885 s** | 649 s (1.72x median) | ~840 s | 2.2x |
| JUNCTIONS | 659 s | **3295 s** | 1046 s (1.59x) | ~1360 s | 2.4x |
| CLOSEPACKING | 989 s | **4945 s** | 1387 s (1.40x) | ~1800 s | 2.8x |

#### Tail characterised properly — the +30 % heuristic was too pessimistic

Measured on the **healthy population only** (CPU < 3500 s, excluding the 8 guard
kills that were contaminating the earlier per-tune maxima):

| Tune | n | median | p90 | p99 | obs max | log-sd |
|---|---|---|---|---|---|---|
| MONASH | 100 | 372 s | 397 s | 591 s | 649 s | 0.098 |
| JUNCTIONS | 95 | 618 s | 723 s | 950 s | 1046 s | 0.122 |
| CLOSEPACKING | 97 | 914 s | 1274 s | 1340 s | 1387 s | 0.190 |

**These distributions are tight** — log-sd 0.10-0.19, and p99.9/median only
1.36-1.91. **A healthy job has never exceeded ~1.9x its tune's median.**

*Fit caveat, stated because the guard depends on it:* lognormal is a mediocre
fit. Predicted p99 vs observed is 471/591 for MONASH (**under** by 20 %),
868/950 for JUNCTIONS (under 9 %), 1510/1340 for CLOSEPACKING (**over** by
13 %). So the p99.9 figures are indicative, not precise.

**Better estimator, used below:** anchor on the observed maximum at n~100 and
scale by the ratio of order statistics, `exp((z_0.999 - z_0.99) * sd)`:

| Tune | obs max (n~100) | **est. max at n=1000** | earlier +30 % guess |
|---|---|---|---|
| MONASH | 649 s | **~700 s** | 840 s |
| JUNCTIONS | 1046 s | **~1150 s** | 1360 s |
| CLOSEPACKING | 1387 s | **~1600 s** | 1800 s |

**Why 5x median.** Against the estimated n=1000 maxima, 5x gives headroom of
**2.7x / 2.7x / 2.9x — uniform across tunes**, where the flat 3600 s gives
5.1x / 3.1x / 2.25x.

**But a second correction, against my own earlier recommendation: the collateral
risk from the flat guard is lower than I claimed.** I said CLOSEPACKING's
headroom was 2.6x and "thin". Measured against the *healthy* distribution it is
**2.25x at n=1000** — thinner still in ratio, but in absolute terms a healthy
CLOSEPACKING job would have to run **2.6x its own p99.9** to be caught. On this
evidence the flat guard is **not** currently killing healthy jobs, and the case
for changing it is uniformity and future-proofing, not an active defect.
**Recommend it as a low-priority production hygiene change, not a blocker.**

**CORRECTION to the rationale: net CPU spent on hangs goes UP, not down.**
The proposal tightens MONASH and loosens CLOSEPACKING, but **MONASH has had
zero hangs across two campaigns**, so tightening it saves nothing observed,
while loosening CLOSEPACKING means each of its hangs burns 4945 s instead of
3600 s. For the observed mix:

- flat 3600 s: 8 x 3600 = **8.0 CPU-h**
- proposed: 5 x 3295 + 3 x 4945 = **8.7 CPU-h**

**So justify this on collateral-risk grounds, not CPU savings.** The real
argument is that CLOSEPACKING's 2.6x headroom is thin enough to kill healthy
jobs at 1000-job scale, and that killing a healthy CR job is far more costly
than the ~9 % extra CPU a hang burns — it removes an event sample from the
tune whose baryon physics the paper is about, and forces a retry round.


---

## A fourth arm isolating close packing — preserved with its cheapest shape

**Not proposed, not decided.** Recorded so the option survives with its
*cheapest* shape rather than its most expensive one.

**Why it would be wanted.** No contrast in the current three-arm design isolates
close packing. MONASH ↔ CLOSEPACKING is the best controlled — it holds every
Lund and flavour-composition parameter at Monash values (measured, `B5` in
`RELEASE_BLOCKERS.md`) — but still varies CR, close packing, strange junctions
and `pT0Ref` together. Isolating close packing needs an arm differing *only* by
`ClosePacking:doClosePacking`.

**The cheap shape: a standalone paired campaign.** CLOSEPACKING and CLOSEPACKING
with `doClosePacking = off`, **100 jobs each, equal exposure by construction**,
run as its own campaign. This sidesteps `build_canonical_manifest.py:119,128`'s
equal-exposure constraint rather than requiring a change to it, and never
touches the main campaign. **~55 CPU-hours** at CLOSEPACKING's measured 989 s
per job.

Compare the expensive shape — adding a fourth arm to the main campaign at full
statistics — at **275 CPU-hours**, taking the campaign from 562.5 to ~837.

**What is not free either way.** The audit counted **at least 14 hardcoded
three-tune sites** (`merge_root_files.sh:186,202`, `tools/campaign.py:34`,
`tools/validate_analysis_outputs.py:20`, `tools/statistical_robustness.py:39`,
`tools/generate_registry_artifacts.py:359`, `tools/validate_tune_cards.py:10`,
four `PlottingScripts` sites, two test files). Each is a place a fourth tune is
silently dropped or trips an exposure check. **The one-line `TuneOrdinal()`
addition is the smallest part of the work, not the whole of it.** The 2-bit tune
field does hold four and `JUNCTIONS_MATCHED` is ruled out of production, so no
schema widening is needed.

**Classification: referee-response option, not first submission.**

---

## Merge hygiene: an "accept pre-computed gate report" option

**Recorded 2026-08-09 as hygiene, not acted on. Owner ruling: the double-gate
cost is accepted and `merge_root_files.sh` is not modified.**

`merge_root_files.sh:80-83` runs `tools/validate_analysis_outputs.py`
unconditionally at the top of every invocation, writing
`${analysis_root}/validation/analysis_output_manifest_validation.json`. A
standalone gate run writes elsewhere, so the cost is paid twice — **21–33 h each
time**, and again on every resume.

**Why it was accepted rather than optimised:** the standalone run is the
checkpoint that protects a ~3-day merge from launching onto bad data, and the
internal run is the production path's own bookkeeping. **Modifying the
production script on the eve of its largest run, to save redundant insurance, is
the wrong trade.** The totals fit — 65–77 h against a 96 h ceiling — so nothing
forces the change.

**The option, for later:** accept a pre-computed report via a flag, validating
that its `canonical_manifest_sha256`, `analysis_root` and `checkout` match the
current invocation, and **failing closed** on any mismatch or on a report older
than the newest promoted directory. That last condition is the hard part and the
reason this is hygiene rather than an obvious win: a stale-report acceptance
would silently merge unvalidated data, which is strictly worse than paying the
21–33 h.

**Resume amplifies it:** every interruption re-pays the internal gate before
reaching the first unmerged directory. See `docs/MERGE_V3_PREREGISTRATION.md` §6.

---

## Measure the junction-remnant heavy-diquark rate (M2's open half)

**Recorded 2026-08-09 as an option. Not pursued. No paper claim depends on it —
by ruling, the channel may appear only as explicitly speculative.**

`docs/M2_PROBQQ1TOQQ0JOIN.md` settles that `probQQ1toQQ0join` is indexed by the
heavier quark **in the diquark**, so Λ_c and Λ_b with light `(ud)` diquarks both
take index 0 and the charm/beauty entries never fire for them. **One channel
survives:** in junction topologies the diquark is built from the **remnant ends
of the two lowest-momentum legs** (`StringFragmentation.cc:2399`, legs
`:2112-2117`, remnants `:2344/:2347`), so a heavy quark **can** land inside the
diquark and select index 2 or 3.

**The code establishes the path exists; nothing here measures how often it is
taken.** That is the open half of M2, and it is a physics question rather than a
code question.

**How it would be measured:** a linked probe against the pinned 8.317 install
instrumenting `makeDiquark` call sites — count, per junction baryon, the flavour
composition of the diquark actually formed, and report the fraction where
`idMax ≥ 4`. Same shape as F4's probe (**and the same open dependency**: whether
PYTHIA retains what the probe needs under the analysis's `mayDecay` settings).

**Why it is worth doing eventually:** it is the difference between "a speculative
channel" and "a measured sub-percent effect that can be dismissed in a clause" —
or, if the rate is not small, an actual mechanism for the observed difference.
