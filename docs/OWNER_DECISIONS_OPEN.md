# Open owner decisions — the whole docket, in one place

**Swept 2026-08-20 from branch `systematics-harvest`, drafted at `0dddc83` and
refreshed against `16042f2`.**
**This session decided nothing and executed no option.**

Every decision the repository waits on is below. Each entry gives six things:

1. **the question**, answerable yes/no or by choosing;
2. **what blocks on it** — the document, figure or session that cannot close;
3. **the evidence**, quoted from its artifact with the path;
4. **the options**, with the consequence of each;
5. **a recommendation**, with its reasoning, or a plain statement of none;
6. **the cost** of executing each option.

**How to use it.** Answer an entry in place, or answer it wherever the owner
normally records rulings and cite this section. Each entry is written to be
answerable without opening another file. The paths are there so a claim can be
checked, not because the entry depends on them being read.

**Order.** Section 1 comes first because more downstream work waits on it than on
any other. The order is by how much unblocks, not by how hard the question is.

> `Paper/**` and `Literature/References.bib` are read-only in this work. Of the
> sixteen decisions below, fourteen appear somewhere else in the tree. Two appear
> nowhere, and section 0 marks them **UNTRACKED**.


> ## STATUS 2026-08-20 — eleven ruled, one answered, four still open
>
> **This docket was swept on 2026-08-20 and the owner ruled the same day.** The
> index below carries a status column, and every ruling lives in the document
> that owns the question — not here. This file stays as the record of what was
> asked and on what evidence.
>
> **Still open, and these are what a merge would carry across:**
>
> | # | what is open | why it stayed open |
> |---|---|---|
> | **3** | the freeze contract's shape rule | no ruling was given. 33 figure files stay blocked |
> | **4** | which tree the reproducibility statement resolves to, and whether the manuscript is in it | no ruling was given |
> | **1** | S4's **bound**, not its ruling | the ruling is made and stage 1 is delivered; stages 2 to 4 are a Condor pass this session could not collect |
> | **6** | the Nikhef cleanup **commands** | the two code changes are applied and tested; running §9 is a separate authorization |
> | **9** | §5.3's nine retirement families | put to the owner in answerable form, one line each |
>
> Everything else below is ruled or answered, and the section text records the
> ruling beside the evidence it was made on.

---

## 0. INDEX — every question, in priority order

| # | the question, in one line | status 2026-08-20 |
|---|---|---|
| **1** | Launch S4, the last unmeasured registered source, or declare the counter window not a source — and either way, name its absence in the published verdict? | ◐ RULED, NOT COLLECTED |
| **2** | Which convention defines the paper's observable — diquark-structure, or experiment-comparable? **UNTRACKED** | ✅ RULED |
| **3** | Amend the freeze contract so it admits the shape `HF_RUN3_V1` actually has, or drop the two raw-reading figure families? | ⛔ OPEN |
| **4** | Which git tree does the paper's reproducibility statement resolve to, and is the manuscript inside it? | ⛔ OPEN |
| **5** | Provide the M1–M10 physics review for `docs/review/`, or record it as unavailable? | ✅ CLOSED |
| **6** | Authorize the Nikhef cleanup commands and the two specified code changes? | ◐ PART DONE |
| **7** | Keep two per-flavour multiplicity panels, or move the manuscript to the one combined canvas? | ✅ RULED |
| **8** | Are the two `_215` global summary canvases still wanted? | ✅ RULED |
| **9** | Accept the figure inventory's 106 retirements and 6 supersessions as a block, or review them one by one? | ◐ PART RULED |
| **10** | Resolve the excited-state registry's two design gaps now, or leave stage-1 unimplemented? | ✅ RULED |
| **11** | Commission the `ATTENTION.txt` factor-of-two check, or rule the directory out of scope? | ✅ RULED |
| **12** | Commission a check on whether the paper figures are digest-pinned, or record the hole and ship? | ✅ ANSWERED |
| **13** | Rule the four remaining `COMPONENTS.md` §11 dispositions — Q1, Q2, Q3, Q4? | ✅ RULED |
| **14** | Rename `plotting/improvedPlotting_THnSparse.C`, and if so, when? | ✅ RULED |
| **15** | Restore a running-coupling illustration in the introduction, or drop the line? | ✅ RULED |
| **16** | Does the three-tune table's FINAL status survive the b-baryon advisory's confound being unresolved? **UNTRACKED** | ✅ RULED |

**Already decided — do not re-ask.** Four rulings are recorded in section 17.

---

## 1. S4 — launch it, or declare the counter window not a source?

**The question.** Does S4 run against the current head, or does the paper record
the event-activity counter window as not a systematic source? Either way, does
the published combination name S4's absence?

**What blocks on it.** The published verdict on the paper's central claim.
`docs/SYSTEMATICS.md` §7 states the rule that made this binding:

> **No total until every non-negligible source in a tune's column has a measured
> value.**

`STATE.md` carries the same constraint as the live one: *"no systematic
uncertainty is propagated into any published number yet, and none may be until
every non-negligible source in a tune's column has a measured value."* Release
blocker **B14** (`RELEASE_BLOCKERS.md:1320`) is the manuscript-side form of it.

**⚠ The combination has since run without S4, and this changes the question's
shape rather than closing it.** Commits `10634a3` and `16042f2`, both landed
2026-08-20 while this docket was in draft, deliver
`docs/systematics_results_20260820/VERDICT.md`. A total now exists, and S4 is not
in it.

**The evidence.**

*The pre-registration counts six sources, not seven.*
`docs/SYSTEMATICS_PREREGISTRATION.md:1` is titled *"Systematics — the
pre-registration, six sources"*, and its table at `:102`–`:107` lists S1 to S6.
Seven **campaigns** measure four of them. S4 is source four of six, and its row
at `:105` reads **"pre-registered, DELIBERATELY NOT LAUNCHED"**.

*S4 is still unlaunched at this commit.* `docs/SYSTEMATICS.md` §6:

> **S4 — event-activity counter window — ⛔ REGISTERED, NOT LAUNCHED**

*The combination excludes it, and names no exclusion.*
`docs/systematics_results_20260820/COMBINED_SYSTEMATICS.md` is titled *"The
combined systematic, all seven sources"*. Its per-cell tables list five
contributors — `S1a_mur`, `S1b_muf`, `S2_pdf`, `S3_pthat` and
`S5_class_migration` at a measured zero. Its rules table names S6/A2 as excluded
by owner ruling A2. **`S4` appears nowhere in that document, nor in
`VERDICT.md`.** S5's zero *is* listed rather than omitted, by the §9.5 rule
*"listed rather than omitted"* — S4 is the one registered source neither measured
nor named.

*The margin is what makes this matter.*
`docs/systematics_results_20260820/VERDICT.md` §2:

> **THE CLAIM HOLDS, AT ABOUT 2 SIGMA.** The recorded erase threshold was 0.354 —
> the whole of the effect. The combined systematic reaches 0.160, which is 45 per
> cent of it, so the trend difference survives with roughly a factor of two to
> spare.

The trend difference is **+0.35362** for JUNCTIONS − MONASH, with a total of
0.16051 and a ratio of **2.2**; for CLOSEPACKING − MONASH, **+0.31172** against
0.15512, ratio **2.0**. The same section states that the systematics dominate:
*"Statistically the trend difference is a 27.5 σ effect. With systematics it is a
2.2 σ effect."* A sixth source entering the quadrature moves a 2.0 σ result more
than it would move a 27.5 σ one.

*The reason S4 was held has cleared.* `docs/SYSTEMATICS_PREREGISTRATION.md` §6:

> **Launch condition, stated so nobody has to re-derive it:** after the merge
> exits, the campaign is recorded COMPLETE, and the checkout advance in
> `STATE.md` PENDING #5 has happened. Then render S4 against the new head.

`STATE.md` PENDING #5 records the advance as taken: *"DONE 2026-08-17 20:12 CEST
— the Nikhef checkout advance is TAKEN. `43e35be8` → `8650a047`, 153 commits,
fast-forward."* All seven campaigns are CLOSED. Every clause of the launch
condition holds.

**S4 needs no generation.** `docs/SYSTEMATICS_PREREGISTRATION.md` §6: *"It is
already in every raw file, so no generation is required — this is a re-analysis
of the existing 3000 files."* The boundary convention is fixed in advance as
percentile-preserving, so the method needs no further decision.

**The expectation is pre-registered and is falsifiable**: *"the per-class
observable should shift only slightly: ≲ 3 %"*, and *"a large shift would indict
the narrow counter … and would mean the paper's multiplicity axis is
fluctuation-dominated."*

**The options.**

| option | consequence |
|---|---|
| **A. Launch S4, then recombine** | The six-source column completes. If the shift is ≲ 3 % the source is small, the axis is vindicated, and the 2.2 σ verdict is confirmed on a complete set. If it is large, the paper's multiplicity axis is indicted and more than a systematic changes |
| **B. Declare the counter window not a source, and record the exclusion** | The published total stands, on a judgement rather than a measurement. `COMBINED_SYSTEMATICS.md` and `VERDICT.md` gain the exclusion and its reason, which they currently lack. A referee may still ask why a registered source was dropped after the other five returned |
| **C. Leave it as it stands** | A verdict at 2.0–2.2 σ remains published with one registered source neither measured nor named. This is the only option that leaves a document silent about what it omits |

**Recommendation: option A, and option B is acceptable only with the exclusion
written down.** Three things drive this. First, the margin: the systematic is 45
per cent of the erase threshold and the result is 2.0–2.2 σ, so a sixth source
entering quadrature can move the verdict. Second, the registered expectation
names one outcome — a large shift — that would change the paper's axis rather
than its error bar, and no judgement call substitutes for measuring that. Third,
S4 needs no generation, which makes it the cheapest of the six sources to run.

**Option C is the one to close regardless of how A and B go.** The §9.5 rule that
governs S5 is *"listed rather than omitted"*, and applying that same rule to S4
costs one row.

**Cost.**

- **Option A.** 3000 analysis jobs, no generation, then a 33-leg merge and its
  closure. `docs/MERGE_V3_BAND_VALIDATION.md` measured the merge cost at this
  scale: 15 legs in 48.6 h. That projects to **~97 h** for 33 legs, against a
  65–77 h band it missed. Closure adds **2 h 04 m to 2 h 22 m per
  tune** (`docs/SYSTEMATICS_HARVEST_RUN_RECORD.md` §14.2). Call it a multi-day
  pipeline, plus queue time against a shared farm. Then one rerun of
  `extraction/combine_per_class.py` and the verdict scripts.
- **Option B.** One ruling, one paragraph in `docs/SYSTEMATICS.md` §6, and one
  row each in `COMBINED_SYSTEMATICS.md` and `VERDICT.md`.
- **Option C.** Free now; the cost lands at referee stage.

---

## 2. The observable definition — which convention? **UNTRACKED**

**The question.** Does the paper's observable definition adopt the
diquark-structure convention or the experiment-comparable convention?

**What blocks on it.** The paper's central number, and the methods text that
release blocker **B1** already owes. `docs/THREE_TUNE_CENTRAL_TABLE.md` publishes
both conventions side by side: §1 *"DIQUARK-STRUCTURE (primary) — a PARTITION,
sums to 100 %"* and §2 *"EXPERIMENT-COMPARABLE (decay map v2, split)"*. The
manuscript must say which one it means.

**No document tracks this as open.** It is stated once, in
`docs/EXTRACTION_CONVENTIONS.md` §3, and appears in no `STATE.md` PENDING row, no
`RELEASE_BLOCKERS.md` entry and no `COMPONENTS.md` §11 question. That is why it
is in this docket.

**The evidence.** `docs/EXTRACTION_CONVENTIONS.md` §3 states the choice and its
stakes:

> **The two conventions are not competing answers; they answer different
> questions.** The structural one says what the generator made. The
> experiment-comparable one says what an experiment would see. **The
> excluded-fraction problem is severe in the first framing and largely dissolves
> in the second** — and which framing the paper's observable definition adopts is
> the decision this table exists to inform. **That decision is the owner's.**

The same section gives the magnitude. Under the structural convention *"nearly
half the compensating flavour is in a category the analysis does not count"*.
Under the experiment-comparable convention *"that weight is not lost — it is
reassigned to the ground states those vectors decay into"*, and **D⁰ alone
carries 45.9 %**, giving *"89 % charm ground states against 11 % beauty ground
states, and there is no large 'excluded' residual"*.

The experiment-comparable convention depends on decay-parent map v2, whose
residual misassignment is **0.0018 %** (`docs/MAP_V2_RESULT.md` §1), down from
the superseded channel-level figure of 12.8451 %.

**The options.**

| option | consequence |
|---|---|
| **A. Diquark-structure as the paper's observable** | The paper reports what the generator made. The excluded-fraction problem is severe and must be stated in the observable definition, not buried. No dependence on the decay map |
| **B. Experiment-comparable as the paper's observable** | The paper reports what an experiment would see. The excluded-fraction problem largely dissolves. The number then depends on decay-parent map v2 and inherits its 0.0018 % residual and its provenance chain |
| **C. Quote both, with one named primary** | Both tables are already computed, so this costs no new measurement. It requires the methods section to explain why two numbers exist and which claim rests on which |

**Recommendation: none.** This is a physics-scope choice about what the paper
measures. The two conventions answer different questions rather than one question
better or worse, and `docs/EXTRACTION_CONVENTIONS.md` §3 says so itself. An agent
recommendation here would be a preference dressed as a finding.

**What can be said without deciding:** both tables exist, both are checked, and
the invariance check in `docs/EXTRACTION_CONVENTIONS.md` §4 confirms that
regrouping conserves the total exactly. Neither option is blocked by missing
work.

**Cost.**

- **Option A or B.** One ruling, then the observable-definition sentence and the
  methods text. Both are `Paper/**` edits, which are owner-action under B1.
- **Option C.** The same, plus a paragraph reconciling the two tables.
- No option needs a new measurement.

---

## 3. The freeze contract — amend it, or drop the raw-reading figures?

**The question.** Does the freeze contract change so it admits the shape
`HF_RUN3_V1` actually has, or do figure 4 and the kinematic panel families come
out of the paper?

**What blocks on it.** Thirty-three figure files, and release blocker **B3**.
`docs/FIGURE_INVENTORY.md` §6.3b:

> **This blocks only the raw-reading macro** — figure 4 and the §7 kinematic
> panels.

That is figure 4 at `Model.tex:130`, one of eight REGENERATE rows, plus the two
BUILD families of §7, **32 files** (`docs/FIGURE_INVENTORY.md` §0). The other
seven REGENERATE rows read merged products and are unaffected.

**The evidence.** The render fails at a gate that is a defect, not a policy
(`docs/FIGURE_INVENTORY.md` §6.3b):

```
ERROR: cannot open file for SHA-256: .../freeze/canonical_raw_validation_receipt.json
```

The mismatch is threefold and the same section states each part:

1. `Plot_InclusiveKinematicSpectra_Raw.C` requires four artifacts;
   `tools/build_canonical_manifest.py` produces the manifest, the ten block files
   and the seal. **`freeze_summary.json` and the validation receipt are written
   nowhere in the repository except test fixtures.**
2. The macro requires `seal.state == "SEALED"`, `seal.validation_receipt_path`
   and `seal.validation_receipt_sha256`. The builder's seal has **none of these
   fields**.
3. The shape rule requires `jobs_per_tune == 100` and
   `successful_events_per_job == 1000000`. **`HF_RUN3_V1` is 1000 jobs × 100 000
   events.**

The third is the deep one, and the inventory says why:

> 100 jobs × 1 M events and 1000 jobs × 100 k events are **the same 100 M per
> tune**, differently decomposed. The contract checks the decomposition, and it
> was written for `campaigns/HF_100M_primaryGround_ccbb_v1` — the only entry in
> `campaigns/` — and never updated for the physics campaign.

**A workaround was refused, and the refusal is evidence.** The same section:

> Producing the two missing artifacts by hand would mean writing
> `successful_events_per_job: 1000000` (false — it is 100 000) and
> `state: "PASS"` on a validation receipt for an exhaustive raw validation that
> was never run. That is fabricated evidence.

**A second defect rides on the same macro.** `docs/FIGURE_INVENTORY.md` §6.2
records that the B6 boundary-artifact update never reached the figure-4 macro:
`Plot_InclusiveKinematicSpectra_Raw.C` computes
`CalculateMultiplicityThreshold(hist, p)` from the passed histogram and *"contains
zero references to the artifact"*. Because the production campaign is HardQCD
with pTHat > 2 rather than minimum bias, the inset *"would draw boundaries from
one distribution and label them with percentiles that are defined on a different
one"*. That fix is already dispositioned — *"fix before rendering"* — so it is a
queued code change, not a decision. It is named here because it is in the cost of
every option that renders figure 4.

**The upstream work is done.** `docs/FIGURE_INVENTORY.md` §6.3: *"the macro is
fixed, compiles on pinned ROOT 6.30/01, the raw data is present (1000 files × 3
tunes), and the label and boundary audits are complete and verified against the
frozen receipt."* The dataset gate cleared on 2026-08-17.

**The options.**

| option | consequence |
|---|---|
| **A. Amend the shape rule and write the two missing producers** | Figure 4 and the 32 kinematic files become renderable. The validation receipt must record a real exhaustive raw validation, so this option contains option B's cost |
| **B. Run the exhaustive raw validation, then amend the shape rule** | The same as A with the evidence produced first, so the receipt states a fact rather than a promise. This is A with its expensive half named honestly |
| **C. Drop figure 4 and the kinematic panels** | 33 figure files leave the paper. Figure 4 is the shared multiplicity spectrum at `Model.tex:130`, and §7's φ panel is the isotropy check the addendum promoted. The paper loses its only inclusive-kinematics evidence |
| **D. Relax the shape rule only, and stub the receipt** | Rejected in the tree already, and correctly: it writes `state: "PASS"` for a validation that never ran |

**Recommendation: option B.** The shape rule must change either way. It checks a
decomposition rather than a total, and its author wrote it for a campaign that is
not the physics campaign. What separates B from A is the order. A validation
receipt built from a real `ValidateRawOutput` pass is a record; one written ahead
of the pass is a formality. The contract exists to make a figure's provenance
checkable, so the order matters. Option D is the one the tree has already refused
by name.

**Cost.**

- **Option A.** Four code changes, all contract-level and all needing tests.
  Amend the shape rule in the macro's resolver. Write `freeze_summary.json` and
  `canonical_raw_validation_receipt.json`. Add the three missing seal fields to
  `tools/build_canonical_manifest.py`. Apply the §6.2 inset fix.
- **Option B.** All of A, plus an exhaustive raw validation over 3000 files. The
  nearest figure on record is the excited-state contract transition at **~56
  CPU-h** for a 10 % campaign (`docs/REGISTRY_AND_MAPPING_PROPOSAL.md`). A
  full-campaign pass is larger by an order of magnitude.
- **Option C.** Two `\includegraphics` removals and their captions, plus a stated
  reason. Owner-action on `Paper/**`.
- **Option D.** Cheapest now; it fabricates evidence.

---

## 4. B8 — which tree, and is the manuscript in it?

**The question.** Which git ref does the paper's reproducibility statement point
at, and does the manuscript live inside that ref?

**What blocks on it.** `REPRODUCIBILITY.md`, the methods section's code
statement, and submission. `RELEASE_BLOCKERS.md:709` states it and says it must
not be left:

> A methods section saying "the code is at github.com/..." has to resolve to the
> tree that produced the figures. Options are merge `physics-focus` into `main`,
> replace `main` with it, or publish from `physics-focus` — **an owner decision,
> not proposed here.** What must not happen is that it stays undecided until
> submission.

**The evidence.**

`main` holds none of the infrastructure. `RELEASE_BLOCKERS.md:709`: *"`main` (the
collaborator PR-merge branch, at `11884cf`) contains none of this infrastructure
— no `Makefile`, no `tools/`, no `docs/`, no `REPRODUCIBILITY.md`, no
`Validation/`."*

The second half is B8b, and it is a separate fact:

> **The manuscript itself is in no branch's index.** It lives at
> `Paper/Heavy_flavour_hadronisation_model_paper/` inside the **`main`** worktree
> and `git ls-files --error-unmatch` fails on it. Seven `.tex` files, 589 lines,
> existing only on one laptop.

`docs/WORKSPACE.md` narrows the problem without deciding it:

> **`main` and `physics-focus` are two refs in one repository, not two
> repositories.** The options B8 lists … are therefore all **ref operations inside
> a single object store** … **This does not decide B8.**

`RELEASE_BLOCKERS.md:709` also names the innocent explanation: *"the paper may be
synced by hand from Overleaf, in which case tracking it in git is the wrong fix
and the right one is recording where the authoritative copy lives."*

**The options — the ref question.**

| option | consequence |
|---|---|
| **A. Merge the working branch into `main`** | The public default branch becomes the tree that produced the figures. `main`'s collaborator history is preserved. A URL with no ref resolves correctly |
| **B. Replace `main`** | The same result with a discontinuous history on the default branch. Collaborator PR references become harder to follow |
| **C. Publish from the working branch by name** | No ref operation. The reproducibility statement must name the branch and the commit, and a reader who drops the ref lands on an empty tree |

**The options — the manuscript question.**

| option | consequence |
|---|---|
| **D. Track the manuscript in the published tree** | The reproducibility statement resolves to code and text together. Wrong if Overleaf is authoritative, because two copies will drift |
| **E. Record where the authoritative copy lives** | Correct if Overleaf is authoritative. The published tree then has no manuscript, which a reader must be told rather than left to discover |

**Recommendation: option A with option E, unless Overleaf is not authoritative.**
The reasoning for A: readers who follow a reproducibility URL do not know the
branch names, and only A makes the bare URL correct. C works, but it puts the
whole burden on one sentence copied accurately. The reasoning for E is
conditional, and the owner holds the deciding fact. If the manuscript is
hand-synced from Overleaf, tracking it in git creates a second authoritative
copy, which is worse than having none. If Overleaf is not in use, D is right and
E is not.

**Cost.**

- **A.** One merge and a push. `docs/WORKSPACE.md` establishes there is no
  cross-repository synchronisation, so no data movement.
- **B.** The same mechanics with history loss on `main`.
- **C.** One sentence, written carefully.
- **D.** One commit, plus a standing discipline that the tracked copy stays
  current.
- **E.** One paragraph in `REPRODUCIBILITY.md`.

---

## 5. The M1–M10 review document

**The question.** Will the owner provide the M1–M10 physics review for
`docs/review/`, or is it recorded as unavailable?

**What blocks on it.** Release blocker **B15**, and the honesty of every citation
that names M1–M10. `RELEASE_BLOCKERS.md:324`:

> **The M1–M10 physics review exists nowhere in the repository.** Entries in this
> file and in `POST_SUBMISSION.md` cite it as a source, so they currently **cite
> an unarchived document**.
>
> > **When the review is provided, it goes into `docs/review/`.** Until then,
> > every citation of M1–M10 is a pointer to something a cold reader cannot open.

`RELEASE_BLOCKERS.md:1345` records what waits on it: *"They are owner-action in
the same class as B1, and they cannot be actioned from this repository while the
review itself is unarchived."*

**The evidence.** The same section lists four manuscript-side items recorded
independently, so B15 is not empty even without the document:

- **B1** — the methods section describes a different study.
- **B5** — tune-difference counts, both wrong as measured.
- **B8** — this docket's section 4.
- **The Σ_b naming requirement** — *"whatever the paper calls 'Σ_b' must read
  `Σ_b^±`, because Σ_b⁰ is excluded from central results."*

**The options.**

| option | consequence |
|---|---|
| **A. Provide the review** | It lands in `docs/review/`, the citations resolve, and B15's remaining findings become actionable |
| **B. Record it as unavailable and strip the citations** | Every M1–M10 citation is rewritten to name the finding rather than the source, or removed. Nothing then cites a document a reader cannot open. The findings already recorded independently survive |
| **C. Leave it** | Citations continue to point at a document that does not exist, in a repository whose stated contract is that every claim is checkable |

**Recommendation: option A if the document exists, option B otherwise.** Only the
owner knows which. Avoid option C. It is the single case in this repository where
a document asserts a source it cannot show. That is the failure mode the rest of
the machinery guards against.

**Cost.**

- **A.** One file copy plus a commit.
- **B.** A sweep of `RELEASE_BLOCKERS.md` and `POST_SUBMISSION.md` for M1–M10
  references, rewriting each. Bounded and mechanical.
- **C.** Free now, paid at review.

---

## 6. Nikhef cleanup and the two specified code changes

**The question.** Does an execution session run the commands in
`docs/NIKHEF_CLEANUP_PLAN.md` §9, and apply the two changes specified in §11?

**What blocks on it.** 18.8 G of disk on a volume at 98 % full, and the route a
reviewer takes to regenerate the numbers.

**The evidence.**

*The volume.* `docs/NIKHEF_CLEANUP_PLAN.md` §0: *"Filesystem: `data-02:/alice`,
32 T, 914 G available, 98 % used."* §1: *"Recoverable once the preconditions
hold: 18.8 G. Recoverable after acceptance: 496.7 G."*

*The preconditions are now three, not four.* §2 lists four. Precondition 4 —
*"The owner has answered the seed question in §8"* — is answered (section 17.2 of
this docket). Precondition 1, both campaigns closed, is met: commit `0dddc83`
reports all seven campaigns CLOSED. Preconditions 2 and 3 are mechanical —
`extraction/combine_per_class.py` exits 0, and no live process holds the path.
The execution session verifies both with the probe in §9.1.

*The first specified change is the reviewer-facing one.* §11.1 and run record
§23.4:

> **`extraction/pipeline/tune_chain.sh:63`** invokes
> `/data/alice/ipardoza/tune_extract.sh`, which the 2026-08-17 consolidation
> moved. Every published number still regenerates from committed anchors, so
> nothing is unreproducible today. **The route from merged ROOT files back to
> those numbers cannot run as written**, and that is the route a reviewer takes
> when the anchors are the thing in question.

*The second is a correctness guard.* §11.2:

> `config/dataset_selector.json` currently sets `"active_dataset":
> "legacy_21_06_2026"`, a row whose `publication_eligible` is `false`. **Make the
> resolver refuse when no dataset is named** … **A silent default is what let
> five variation renders read the central campaign.**

The same section names what it unlocks: *"The legacy row protects
`RootFiles/HF/`'s 326.6 G (§4.2). The decision to move the default off that row
is what makes the largest directory on this volume recoverable."*

**The options.**

| option | consequence |
|---|---|
| **A. Authorize both the cleanup and the two changes** | 18.8 G returns, the regeneration route runs as written, and the resolver stops answering a question nobody asked. The 496.7 G stays until acceptance regardless |
| **B. Authorize the two code changes only** | The defects close; the disk stays at 98 % |
| **C. Authorize the cleanup only** | Space returns; the reviewer-facing route stays broken |
| **D. Defer all of it** | Both defects stand. The volume has 914 G free, so this is survivable and not free |

**Recommendation: option A, with the two code changes taking priority.** The two
changes carry a correctness consequence; the cleanup carries a capacity one. Only
the first can mislead a reviewer. §11.2 also carries a sequencing note — *"Do not
apply this while the merges run"* — and the merges are now finished, so the
window that held it is open.

**Cost.**

- **The two changes.** For the chain: one line in
  `extraction/pipeline/tune_chain.sh:63`, and the same line in the deployed
  copy. Add a path-existence assertion over its `bash <path>` lines. For the
  resolver: remove the fallback, raise with the valid keys, and add the two
  tests §11.2 specifies.
- **The cleanup.** One execution session running §9 in order: the precondition
  probe, the git copy in §9.2, then archive-verify-remove in §9.3. Every command
  is written out.
- **Deferral.** Free now.

---

## 7. Two multiplicity panels, or one combined canvas?

**The question.** Does the manuscript keep separate charm and beauty
multiplicity-dependent canvases, or move to the single combined canvas the
current workflow produces?

**What blocks on it.** Two of the manuscript's ten active figures —
`Results.tex:105` and `Results.tex:139` — and their captions. Both are
OWNER-DECIDE rows in `docs/FIGURE_INVENTORY.md` §1.

**The evidence.** `docs/FIGURE_INVENTORY.md` §4.1:

> `Results.tex:105` and `:139` include **separate** charm and beauty
> multiplicity-dependent canvases. **The current workflow produces one combined
> canvas** (`global_balancing_plots_multiplicity_PDF.pdf`); there is no current
> generator output with the two draft names.

Verified against the configurations at this commit: every multiplicity
configuration emits one canvas. `plotting/configuration_multiplicity.json:2069`
and `plotting/configuration_multiplicity_HF_RUN3_V1_THREETUNE_THnSparse_complete_root.json:1661`
both carry a single `write_name` of the form
`global_balancing_plots_multiplicity*`, with no per-flavour variant anywhere in
`plotting/`.

**A trap is recorded, and it must not be walked into.**
`docs/FIGURE_INVENTORY.md` §4.1:

> **This must not be resolved silently** — the reduced smoke output *does*
> produce similarly-named files and is **validation-only**; substituting it would
> put a one-activity-class plot where the paper claims a full multiplicity
> dependence.

**The options.**

| option | consequence |
|---|---|
| **A. Move the manuscript to the one combined canvas** | Two `\includegraphics` lines and two captions become one of each. No plotting change. The charm and beauty panels then share a canvas, which is how the current three-tune figure already reads |
| **B. Emit two per-flavour canvases** | The manuscript keeps its structure. A configuration change is needed to split the canvas, and the split output needs its own validation render and receipt |

**Recommendation: option A.** The reasoning is that the combined canvas is the
output the pipeline actually produces and has already validated — the three-tune
render of 2026-08-16 came back byte-identical on an independent re-render
(`docs/SUPERVISOR_CHANGE_REPORT.md` §9.3). Option B adds a configuration variant
that exists only to match a draft layout, and every new render carries its own
receipt and visual review. The manuscript edit is two lines; the plotting change
is a new artifact with a new provenance chain.

**Cost.**

- **A.** Two `\includegraphics` lines and their captions replaced by one.
  Owner-action on `Paper/**`.
- **B.** A configuration change in `plotting/configuration_multiplicity*.json` to
  emit per-flavour canvases, one render, one receipt, one visual review, plus the
  two captions rewritten.

---

## 8. The two `_215` global canvases

**The question.** Are `globalCanvasYieldsPDF_215.pdf` and
`globalCanvasRelativeYieldsPDF_215.pdf` still wanted in the paper?

**What blocks on it.** `Results.tex:170` and `Results.tex:182`, the last two
OWNER-DECIDE rows in `docs/FIGURE_INVENTORY.md` §1.

**The evidence.** `docs/FIGURE_INVENTORY.md` §4.2:

> `Results.tex:170` and `:182` include `globalCanvasYieldsPDF_215.pdf` and
> `globalCanvasRelativeYieldsPDF_215.pdf`, which are **legacy
> `Balancing_and_Sampling` products**. No current generator emits them.
>
> **Named replacement if dropped:** the per-flavour canvases of §3.3 carry the
> same content in current form.

`STATE.md` states the wider constraint under *PERMANENTLY NOT REGENERABLE*, and
it covers everything from that era. The v2 plotting configuration points at
`AnalyzedData/complete_root_21_06_2026` and
`AnalyzedData/SUBSAMPLES_700/combined_root_subSamples`, and *"both are absent
locally and on Nikhef"* (measured 2026-08-13, `docs/PLOTTING_V3_DELTA.md` §2b).
Nothing can refresh the legacy files. A keep decision therefore means writing a
new generator, not re-running an old one.

`docs/REPO_FILE_CENSUS.md` §5 also flags the source directory as carrying an
unresolved caveat — see section 11 of this docket.

**The options.**

| option | consequence |
|---|---|
| **A. Drop both figures** | Two `\includegraphics` lines and two captions come out. The named replacement in §3.3 carries the same content, so no claim is lost |
| **B. Write a generator against merged v3** | The summary canvases return in current form. New code, new artifacts, a render, a receipt and a visual review, for figures whose content §3.3 already covers |

**Recommendation: option A.** The inventory names a replacement that already
exists and already carries the same content in current form. Option B pays for a
new generator that reproduces a summary view of numbers the paper shows
elsewhere. Nobody can reuse the legacy files, because their input dataset is
gone.

**Cost.**

- **A.** Two `\includegraphics` removals and their captions. Owner-action on
  `Paper/**`.
- **B.** A new generator written against merged v3, plus its render, receipt and
  visual review, plus the captions kept.

---

## 9. The 106 retirements and 6 supersessions

**The question.** Does the owner accept `docs/FIGURE_INVENTORY.md` §5 as a block,
or review the retirements individually?

**What blocks on it.** The manuscript still points at dead-dataset files.
`docs/FIGURE_INVENTORY.md` §8:

> It does not edit `Paper/**`. Every ⚑ row is a paper decision, and the manuscript
> still points at dead-dataset files until the owner acts on §4 and §5.

`docs/SUPERVISOR_CHANGE_REPORT.md` §9.3 gives the count: *"106 retirements and 6
supersessions carry the ⚑ owner mark and have not been executed against the
manuscript."*

**The evidence.** The 106 split into three groups, each with a stated reason.

*Ten belong to a different paper* (§5.2): ten `.eps` files from a
chiral-magnetic-effect / AVFD analysis, *"never referenced by any
`\includegraphics`, and no observable in this paper corresponds to them. **No
replacement needed.**"* These are template leftovers and carry no judgement.

*Ninety-five are superseded exploratory plots* (§5.3), each with a stated ground.
The largest family is 30 `Ratio_*_MONASH_vs_JUNCTIONS_*` files, retired because
*"the analysis is now **three**-tune, and the class axis is the committed
11-class common-absolute partition, not 20 % slices"*. Two 18-file families of
single-particle spectra carry the ground *"pre-v3 dataset"*.

*One is the commented-out introduction figure* — section 15 of this docket.

*The six supersessions* (§5.1) each name their replacement, including
`plotting/paper/figures/fig3_multiplicity_classes.svg` for the class axis and
`fig1_species_decomposition.svg` for the species comparison.

**The options.**

| option | consequence |
|---|---|
| **A. Accept §5 as a block** | The manuscript edit becomes mechanical. The retirements are recorded with reasons already written, so a referee question resolves against the inventory |
| **B. Review individually** | Every retirement gets an owner's eye. 106 rows at a stated reason each |
| **C. Review §5.3 only, accept §5.2 and §5.1** | The ten template leftovers and the six named supersessions pass on their own evidence. The 95 judgement calls get owner review |

**Recommendation: option C.** The three groups differ in kind. §5.2 is a factual
claim needing no judgement: those ten files belong to another analysis and no
`\includegraphics` names them. §5.1 names a specific replacement for each of six.
§5.3 is where a retirement could be wrong, because it retires figures on the
grounds that a superseding view exists. That is the judgement worth an owner's
eye, and option C spends attention where it can change an outcome.

**Cost.**

- **A.** One ruling. The manuscript edits are the same under every option and are
  owner-action.
- **B.** 106 rows reviewed.
- **C.** 95 rows reviewed, in nine families with a shared reason each, so the real
  unit is closer to nine decisions than 95.

---

## 10. The excited-state registry — two design gaps

**The question.** Does the owner resolve the two design gaps in
`docs/REGISTRY_AND_MAPPING_PROPOSAL.md` so stage-1 can be implemented, or does
stage-1 stay unimplemented?

**What blocks on it.** The staged excited-state proposal, which
`RELEASE_BLOCKERS.md:216` carries as a gate-list entry:

> **Two open design gaps remain owner questions**, both stated in the proposal and
> neither resolved: the **§0a/§4B eligibility conflict** (dissolved in stage-1 by
> construction, live again in stage-2) and the **`ValidateRawInputs` contract
> transition** (~56 CPU-h now against 562.5 later).

**The evidence.**

*Gap (a), eligibility.* `docs/REGISTRY_AND_MAPPING_PROPOSAL.md`: *"Option B's
excited associates cannot pass eligibility through the ground-state registry, and
the registry is the one thing §0a says must not move."* The candidate shape is a
separate associate-membership set that *"keeps `FindGroundState` strict, keeps the
category axis intact, and keeps `AuditSpeciesRegistry`'s assertion true"*. The
proposal declines to decide: *"**Open owner question. Not resolved here.** It
touches a validator and the analysis eligibility contract, which is above this
document's remit."*

*Gap (b), the contract transition.* The same document: *"`ValidateRawInputs` pins
`species_registry_sha256` and its siblings to **compiled constants**. **Any
registry change therefore makes the new analysis reject every existing raw
file**."* Two options are priced there — versioned acceptance (cheap, with the
risk that *"a validator that accepts two contracts is a validator that can accept
the wrong one"*) or regenerating the 10 % campaign at **~56 CPU-h**.

**The cost framing in the tree is now stale, and this matters to the decision.**
The proposal argues *"This is the standing argument for implementing before full
production. Doing it after means regenerating the full campaign (562.5 CPU-h)
instead of the 10 % one, a **10x** difference."* Full production has since
completed and sealed — `HF_RUN3_V1` is `canonical` with
`publication_eligible: true` (`docs/HF_RUN3_V1_PUBLICATION_AUTHORIZATION.md`). The
cheap window the argument depends on has closed. Any registry change now faces
the 562.5 CPU-h figure or versioned acceptance, not the ~56 CPU-h one.

**The options.**

| option | consequence |
|---|---|
| **A. Resolve both gaps and implement stage-1 with versioned acceptance** | Stage-1 lands without regenerating anything. The validator then accepts two contracts, and the rationale must be in-tree, as the proposal requires |
| **B. Resolve both gaps and regenerate at the new registry** | Correctness with no validator ambiguity, at full-campaign cost now that the 10 % window has closed |
| **C. Leave stage-1 unimplemented for this paper** | Nothing changes. The proposal stays staged, and the excited-state question moves past submission |

**Recommendation: option C for this paper.** The stale cost framing above is the
reason. The proposal argued for acting before full production, because acting
after costs ten times more. Production is now sealed, so that argument points the
other way. Neither remaining option is cheap, and no figure or table in this
docket's other fifteen sections waits on stage-1.

**Cost.**

- **A.** Two design rulings, the implementation, and an in-tree rationale for
  dual-contract acceptance.
- **B.** The same, plus regeneration. The proposal prices the full campaign at
  **562.5 CPU-h**.
- **C.** One line recording the deferral and its reason.

---

## 11. The `ATTENTION.txt` factor of two

**The question.** Does anything published depend on the `Balancing_and_Sampling`
double-counting caveat, and does the owner commission the check?

**What blocks on it.** Nothing closes on it, and that is the point — it is
tracked in `STATE.md` under *"THE TWO OPEN QUESTIONS THAT ARE NOBODY'S TASK
YET"*, Q1:

> `docs/history/studies/Balancing_and_Sampling/ATTENTION.txt` records that
> double-counting is *not* implemented from 23 December onwards, that results
> "will have to be divided by 2 manually", and ends *"remains to be checked"*.
> **Nothing in the tree says it was checked.** Does it affect anything published?

**The evidence.** `docs/REPO_FILE_CENSUS.md` §5 classifies the file and states
the stake plainly:

> `ATTENTION.txt` | **HISTORY — read before touching** | records that
> double-counting is **not** implemented from 23 Dec onwards and results "will
> have to be divided by 2 manually". **An unresolved correctness caveat, not a
> note.** It ends *"remains to be checked"* and nothing in the tree says it was.

And:

> **`ATTENTION.txt` deserves an owner decision on its own, separate from the
> restructure.** Either the double-counting factor is irrelevant here (the note
> guesses the trigger normalisation cancels it) or it is a live factor-of-two on
> anything derived from this directory. **The file says nobody checked.**

**What bounds the exposure.** The two `_215` canvases in section 8 are the only
manuscript figures that come from this directory, and they are already
OWNER-DECIDE. If section 8 goes to option A, the manuscript's dependence on
`Balancing_and_Sampling` ends and this question becomes historical.

**The options.**

| option | consequence |
|---|---|
| **A. Commission the check** | The caveat resolves either way and stops being an unresolved correctness note in a repository whose contract is that every claim is checkable |
| **B. Rule the directory out of scope, conditional on section 8 option A** | If the `_215` canvases leave the paper, nothing published derives from the directory, and the caveat is history rather than exposure. This must be recorded, not assumed |
| **C. Leave it** | An unresolved factor of two stays unresolved and untracked against any specific claim |

**Recommendation: option B, decided together with section 8.** The question's
whole weight comes from whether a published number descends from that directory,
and section 8 decides that. If the `_215` canvases go, option B costs a sentence
and is correct. If they stay, option A becomes necessary and the check must
precede the figure. Section 8 therefore makes this question either free or
mandatory, and no reason exists to spend the check before knowing which.

**Cost.**

- **A.** A read of the double-counting logic in
  `docs/history/studies/Balancing_and_Sampling/doubleCounting.C` against what the
  quoted numbers used, and a recorded verdict.
- **B.** One paragraph, conditional on section 8.
- **C.** Free now.

---

## 12. Are the paper figures digest-pinned?

**The question.** Does the owner commission a check on whether any paper figure
output carries a recorded digest, or record the hole and proceed?

**What blocks on it.** The completeness of the reproducibility contract on the
figure side. `docs/GOLDEN_OUTPUTS.md` §8 names it as one of the things the
contract does not cover:

> **Plotting outputs.** `plotting/PAPER_FIGURE_PROVENANCE.md` exists; whether the
> paper figures are digest-pinned anywhere was **not established**. **UNKNOWN**

`STATE.md` carries it as Q2 of the two questions that are nobody's task:
*"**Are the paper figures digest-pinned anywhere?** … If not, the freeze contract
has a hole on the figure side."*

**The evidence that the hole may be smaller than it reads.** Two facts bear on
it and neither closes it.

`docs/GOLDEN_OUTPUTS.md` §0.3 states that *"ROOT-generated figures are contracted
differently, and deliberately so"*. For part of the set a missing digest may
therefore be design rather than omission.

An independent re-render already came back byte-identical.
`docs/SUPERVISOR_CHANGE_REPORT.md` §9.3 records that the three-tune figure's PNG
returned *"byte-identical to the 2026-08-16 committed version, across a different
session and a different deploy tree"*. That demonstrates determinism for one
figure. It establishes nothing about where a digest sits.

**The options.**

| option | consequence |
|---|---|
| **A. Commission the check** | The answer is known. If figures are pinned, §8 item 3 closes. If not, the hole is measured and can be filled or accepted knowingly |
| **B. Record the hole and proceed** | The contract ships with a stated gap on the figure side. Honest, and weaker than the code side |

**Recommendation: option A.** The reasoning is that this is a question with a
cheap definite answer, not a trade-off. Two documents carry it as UNKNOWN, and
UNKNOWN is the one state that costs something every time a reader meets it.
Whether the answer then needs work is a separate decision that cannot be taken
until the answer exists.

**Cost.**

- **A.** A sweep of `plotting/PAPER_FIGURE_PROVENANCE.md`, the receipts under
  `docs/plotting_validation/`, and `docs/GOLDEN_OUTPUTS.md` §2.12 for a recorded
  figure digest. The check reads; it computes nothing.
- **B.** One sentence.

---

## 13. The four remaining `COMPONENTS.md` §11 dispositions

**The question.** Four file-disposition questions, each answerable on its own.
`docs/COMPONENTS.md` §11 lists six. Section 14 of this docket carries Q5, and
section 17.3 records Q6 as decided.

**What blocks on it.** `docs/COMPONENTS.md` §11 closing. Nothing downstream waits
on any of the four, which is why they sit here rather than higher.

**The evidence, per question, quoted from `docs/COMPONENTS.md` §11.**

**Q1 — `analysis/status_analysis_qq.C`.**

> functionally a member of the split chain — its only consumer,
> `qq_draw_2D_correlations.C`, is in `attic/split_chain/`. Should it move there,
> or is it kept in `analysis/` on purpose?

*Options:* move it to `attic/split_chain/`, so the directory holds the whole
chain; or keep it in `analysis/` and record why. *Consequence of moving:* `attic/`
keeps meaning "no live consumer". *Consequence of keeping:* one file in
`analysis/` has no live consumer, which the next census will re-raise.
*Recommendation:* move it. The stated criterion in §10 is that `attic/` means no
live consumer, and this file has none outside the attic. *Cost:* one `git mv` and
a `RENAMES.md` row.

**Q2 — `plotting/FinalAnalysis/`.**

> `POST_SUBMISSION.md` schedules both macros for retirement *after* submission.
> Retire now and drop the two `run_paper_plots.sh` targets, or leave as
> scheduled? **The name's "Final" survives only as long as the directory does.**

*Options:* retire now, or leave as scheduled. *Consequence of retiring now:* two
`run_paper_plots.sh` targets go, and a directory named "Final" that is not final
stops being confusing. *Consequence of leaving:* the schedule already covers it,
and nothing breaks. *Recommendation:* leave as scheduled. The retirement is
already recorded with a trigger, and moving it earlier changes a runner during a
figure campaign. *Cost:* retiring now is one directory move plus two target
removals plus the README edits; leaving is free.

**Q3 — `generated_heavy_flavor_summary.C`.**

> measurement-provenance for a published table, sitting in `attic/`. Should it
> move to `Validation/` or beside the A9 document, so "attic" keeps meaning "no
> live consumer"?

*The stake:* §10 records that *"it produced a table that is published right now
— `Paper/Tables/generated_heavy_flavor_summary.tex`"*. Nobody can re-point it,
because *"it reads `hidCharm`/`hidBeauty`/`hidBc` histograms and a tree named
`tree`, none of which exist in raw schema v7"*. *Options:* move it beside
`docs/A9_PAPER_TABLE_REGENERATION.md`; move it to `Validation/`; leave it.
*Consequence of leaving:* provenance for a published table sits in a directory
named for dead code. *Recommendation:* move it beside the A9 document. It is
provenance for a specific published table, not a validator, so it belongs with
the document that explains it. *Cost:* one `git mv`, a `RENAMES.md` row, and one
path reference in `docs/A9_PAPER_TABLE_REGENERATION.md`.

**Q4 — `attic/plotting/plotting_documentation.md`.**

> (485 lines) — plan **D5** ruled *"fold into `plotting/README.md`, attic the root
> copy"*. `RENAMES.md` records the attic move; **nothing records the fold**, and
> `plotting/README.md` (536 lines) never mentions it. Was the content folded, or
> is unique plotting documentation sitting in the attic?

*This is the substantive one*, and `docs/SUPERVISOR_CHANGE_REPORT.md` §9.4 says
so: *"Q4 is the substantive one."* *Options:* diff the two documents and fold
what is missing; or rule the attic copy superseded and record the examination.
*Consequence of not checking:* 485 lines of plotting documentation may be
reachable only through `attic/`. *Recommendation:* diff them. This is the only
one of the four where the answer could be that information is lost, and a diff
answers it definitively. *Cost:* one comparison of two documents, then either a
fold or one recorded sentence.

---

## 14. The `improvedPlotting_THnSparse.C` rename

**The question.** Does `plotting/improvedPlotting_THnSparse.C` get renamed, and
if so, when?

**What blocks on it.** `docs/COMPONENTS.md` §11 Q5 and §12.2. Nothing else — the
name is a convention violation, not a defect.

**The evidence.** `docs/COMPONENTS.md` §12.2 prices it in four parts:

1. *"ROOT's convention ties the entry-point function to the basename … and the
   macro embeds its own filename at `:385` and `:1334` for repo-root detection. A
   file-only rename would leave the old function name inside the new file — worse
   than the defect."*
2. *"`tools/statistical_robustness.py:669` checks **every**
   `multiplicity_boundary_receipt_v1.json` against
   `sha256(plotting/improvedPlotting_THnSparse.C)`. The shipped three-tune
   canvas's receipt records `6dace202…`. Changing the bytes does not re-pin a
   digest — **it invalidates committed receipts for a figure rendered on
   2026-08-16.**"*
3. Two further pins move with it:
   `config/multiplicity_class_boundaries_v1.json` names it in the
   `single_definition_note`, and
   `docs/plotting_validation/hf_run3_v1_threetune_20260816/RUN_RECORD.md` records
   it as the plotter source.
4. *"The figure set is not frozen."*

**The recommendation already in the tree.** §12.2 states one, and it is the
owner's to accept:

> rename to `plotting/Plot_PairBalancing_THnSparse.C` — matching the sibling
> `Plot_<What>_<How>.C` convention — **in a dedicated commit after the figure set
> is frozen and the campaign is recorded COMPLETE**, re-rendering the canvas so
> the receipt and the run record are regenerated rather than patched.

**The options.**

| option | consequence |
|---|---|
| **A. Rename after the figure set is frozen, with a re-render** | The convention violation goes, and the receipt is regenerated rather than patched. Blocked until the figure set freezes, which sections 1, 3, 7 and 8 of this docket bear on |
| **B. Rename now** | Committed receipts for a figure rendered 2026-08-16 are invalidated, and a provenance record is edited to accommodate a cosmetic change |
| **C. Never rename; record the exception** | One file keeps a non-conforming name. `docs/COMPONENTS.md` §12 already documents the exemption class for frozen names, so this is a one-line addition to an existing category |

**Recommendation: option A, and option C is a defensible second.** A is the only
option that regenerates the receipt rather than patching it. C is acceptable
because §12 already established that 67 files carry frozen names, on the grounds
that renaming them would edit a reproducibility claim. This file meets exactly
that test. Option B is the one §12.2 rejects by name — *"editing a provenance
record to accommodate a cosmetic change, which is the one thing this repository's
contract is built to prevent."*

**Cost.**

- **A.** One `git mv`. Rename the entry-point function. Update the two embedded
  filename references at `:385` and `:1334`, and the two pins in
  `config/multiplicity_class_boundaries_v1.json` and the run record. Then
  re-render the three-tune canvas so its receipt and run record regenerate.
- **B.** The same edits, minus the re-render, plus invalidated receipts.
- **C.** One row in `docs/COMPONENTS.md` §12.

---

## 15. `runningCouplingQCD.png`

**The question.** Does the introduction carry a running-coupling illustration, or
does the commented-out line come out?

**What blocks on it.** One commented-out line at `Introduction.tex:20`, and the
last of the 106 ⚑ retirements.

**The evidence.** `docs/FIGURE_INVENTORY.md` §5.4:

> Already commented out at `Introduction.tex:20`. **Owner question:** restore a
> running-coupling illustration in the introduction, or drop the line? Nothing in
> the current analysis depends on it.

**The options.**

| option | consequence |
|---|---|
| **A. Drop the line** | One commented-out line goes. Nothing in the analysis depends on it |
| **B. Restore an illustration** | The introduction gains a pedagogical figure. The existing file is from the retired set, so a current source is needed |

**Recommendation: option A.** The reasoning is that the line is already commented
out, which is a previous decision left unfinished rather than an open question,
and the inventory records that nothing depends on it. If the introduction wants
the figure, that is a writing decision made while writing the introduction, not a
figure-inventory decision.

**Cost.**

- **A.** One line deleted. Owner-action on `Paper/**`.
- **B.** A current running-coupling figure sourced or drawn, plus its caption and
  attribution.

---

## 16. The b-baryon advisory's confound **UNTRACKED**

**The question.** Does `docs/THREE_TUNE_CENTRAL_TABLE.md` §5 stay an advisory,
or does the paper make a claim from it?

**What blocks on it.** Nothing closes on it. It sits here because it is a physics
result with a stated confound, no recorded owner ruling, and no document listing
it as open. `STATE.md` PENDING #6 still reads *"Advisory step 2 — per-tune
b-baryon ratios, one table"* as outstanding, though §5 delivers exactly that
table. The one tracker that names it is stale in the wrong direction.

**The evidence.** `docs/THREE_TUNE_CENTRAL_TABLE.md` §5 records that the
pre-registration failed in the opposite direction:

> **MONASH — the tune with no colour reconnection and no junctions — carries the
> asymmetry** (Σ_b and Ξ'_b at **1.59–1.78**, tens of SEM from unity). **Both CR
> tunes are consistent with symmetric** (0.98–1.05).

And the confound, which the section says is not a footnote:

> The CR tunes also re-tune `StringFlav` and `StringZ`, so "CR removes it" is
> **not** established; "the CR *tunes* do not show it" is. The CR tunes also carry
> far more b-baryon statistics (Σ_b⁺: 130,011 and 68,419 against MONASH's 6,402),
> so the near-unity values are the better-measured ones.

The section's own disposition: *"**Advisory only. It is not a gate and it fails
nothing.**"*

**The options.**

| option | consequence |
|---|---|
| **A. Keep it advisory and out of the paper** | The result stays internal. A referee cannot ask about a claim that is not made |
| **B. Report it with the confound stated** | A striking measurement enters the paper — 0 of 13 species match the pre-registration, in both CR tunes — carrying an explicit statement that the tune bundle prevents attributing it to colour reconnection |
| **C. Resolve the confound first** | Attribution becomes possible. It needs a tune that varies colour reconnection alone, which is a new production |

**Recommendation: none on the physics.** Whether a confounded result belongs in
this paper is a judgement about what the paper claims, and `STATE.md` already
records the tune-bundle confound as *"Documented, not resolved"* under NOT
PLANNED. What can be said: option C requires a production that no plan in this
repository contains, so the real choice is between A and B.

**Cost.**

- **A.** Nothing.
- **B.** One results paragraph and the confound sentence. Owner-action on
  `Paper/**`.
- **C.** A new tune card and a full generation campaign.

---

## 17. ALREADY DECIDED — do not re-ask

Four rulings are made. They are recorded here so no session re-opens them, and
each notes where the tree still reads as open.

### 17.1 The I2 flags are a deviation, not an amendment

**Ruled.** The four I2 flags on JUNCTIONS and CLOSEPACKING are recorded as a
deviation from `docs/PER_TUNE_PROCESSING_PREREGISTRATION.md` step 2. The
pre-registration is **not** amended.

**What this settles.** `docs/THREE_TUNE_CENTRAL_TABLE.md` keeps its FINAL status.
The registered expectation of zero flagged bins stands as written, and the
document reports the departure rather than retro-fitting it. §3d and §3e of that
document hold the measured basis, and this ruling does not change it:

- The three JUNCTIONS flags sit inside `kMultiplyHeavy`, a category contributing
  **12 of 116** testable bins where MONASH contributed **0 of 88**.
- That subpopulation's block scatter is **1.60×** binomial, against ~1.0
  elsewhere.
- A jackknife dropping the flagged blocks moves **no quoted row by more than
  1.19 SEM or 0.006 pp**.

**Why this is the right shape.** `docs/THREE_TUNE_CENTRAL_TABLE.md` §7 names the
hazard in amending instead: *"retuning a null until it stops flagging is how a
real defect gets normalised away."* A deviation record keeps the original
expectation legible.

**Four places still read as open** and need updating to match:
`docs/THREE_TUNE_CENTRAL_TABLE.md` §7 item 3 and its §0 note, `STATE.md` PENDING
item 2, `docs/GOLDEN_OUTPUTS.md:655`, and
`docs/SUPERVISOR_CHANGE_REPORT.md` §9.4.

### 17.2 The seed collision is closed with no action

**Ruled.** The two seed collisions need no remedial action.

**What this settles.** `docs/NIKHEF_CLEANUP_PLAN.md` §10.4's outstanding impact
ruling, and precondition 4 of §2, which reads *"The owner has answered the seed
question in §8."* That precondition is now met.

**The basis, from `docs/NIKHEF_CLEANUP_PLAN.md` §8.3.** *"No published or
variation campaign shares a seed with the archived campaign. `HF_RUN3_V1` and all
seven `HF_SYS_*` return an empty intersection."* The two collisions are
`100200001` (`HF_SMOKE2`, attempt 2) and `100400001` (`HF_PT2`, attempt 4), both
in smoke campaigns. The cause is measured: `HF_100M_primaryGround_ccbb_v1`,
`HF_PT2` and `HF_SMOKE2` share `campaign_ordinal` 1, and the ordinal selects the
seed band. *"From ordinal 3 onward each campaign holds its own ten-million band"*,
so construction closes the defect for every campaign the paper uses.

**One mechanical point survives the ruling**, from §10.4: if the archived
campaign's 500 seeds are ever to be made unavailable, append them **through
`tools/campaign.py`, never by hand**.

### 17.3 `docs/history/**` is excluded from the publication export

**Ruled.** `docs/history/**` does not leave the private tree in the publication
export.

**What this settles.** `docs/COMPONENTS.md` §11 Q6, and the flag in
`docs/SUPERVISOR_CHANGE_REPORT.md` §9.5 that *"the publication disposition of
`docs/history/**` is flagged as an owner decision and not acted on."*

**The list does not yet carry it.** `docs/PUBLICATION_EXPORT_EXCLUSIONS.md` holds
one entry, the ASD-STE100 PDF. The ruling needs an entry there, and that file
names four things an entry must give:

1. the path, the date, and what kind of file it is;
2. why it must not leave the private tree;
3. the mechanism that enforces the exclusion, and the command that shows the
   mechanism working;
4. whether the file is already in git history.

**The fourth item needs care here.** `docs/history/**` **is already in git
history**. That file is explicit that its own mechanism does not cover the case:
*"A file that is already committed needs a different remedy, and this list does
not provide one."* Excluding `docs/history/**` from an export is therefore a
different operation from the `.gitignore` rule that covers the PDF. The entry
must name the mechanism that does it.

### 17.4 The supervisor report's method paragraph is included

**Ruled.** `docs/SUPERVISOR_CHANGE_REPORT.md` §10, *Working method*, is included
in the report.

**What this settles.** The placeholder at `docs/SUPERVISOR_CHANGE_REPORT.md:1248`
reads:

```
<<OWNER: method paragraph — include or remove>>
```

The ruling is include. The placeholder is still in the file at this commit and
needs replacing with the paragraph.

---

## 18. WHAT THIS DOCUMENT DOES NOT DO

**Stated so its silence is not mistaken for coverage.**

1. **It decides nothing and executes nothing.** Every recommendation is a
   recommendation. This session carried out no option, and changed no manuscript,
   configuration or contract file to reflect one.
2. **It does not touch `Paper/**` or `Literature/References.bib`.** Sections 2,
   4, 7, 8, 9, 15 and 16 all end in manuscript edits. Every one of those is
   owner-action.
3. **It does not re-derive the evidence it quotes.** Each number comes from the
   artifact named beside it, at commit `16042f2`. This session measured two
   things for itself: the `restructure-prep` comparison in section 19, and the
   test suite at **63/63 passed** with ROOT resolved.
4. **It does not track execution.** A ruling belongs in the document that owns
   the question. This docket records that a question exists, not that anyone
   answered it.

### 18.1 The prose check, and its false positives

`python3 tools/prose_check.py docs/OWNER_DECISIONS_OPEN.md` returns **58 flags**
at this commit, down from 98 on the first draft. Five of the 58 come from this
subsection itself. The standard requires each flag fixed or recorded as a false
positive, and this session fixed every flag that names prose written for the
docket. The remainder fall into four classes, all of them artifacts of the
checker meeting this document's shape:

1. **Quoted material.** This docket quotes other documents verbatim, because a
   decision must turn on the artifact's own words rather than a paraphrase. A
   long or passive sentence inside a quotation cannot be rewritten without
   falsifying the quotation. Most LONG and PASSIVE flags are of this class.
2. **Lists counted as one paragraph.** The LONG-PARA flags at the option
   descriptions, the cost lists and §18 count a numbered or bulleted list as a
   single paragraph. The standard asks for a vertical list in exactly these
   places (*"Use a vertical list for more than three parallel items"*).
3. **Section references split as sentences.** The sentence splitter treats
   `§10.4` and `PLAN.md` as sentence ends, so it reports fragments that begin
   mid-sentence.
4. **`Nothing` read as an `-ing` start.** One ING-START flag matches the word
   `Nothing`.

---

## 19. `restructure-prep` — it holds nothing

**Measured at `1b1b081`, this commit.** The branch holds nothing that is not
already on `systematics-harvest`.

| check | result |
|---|---|
| `git merge-base --is-ancestor restructure-prep systematics-harvest` | **YES** |
| `git rev-list systematics-harvest..restructure-prep --count` | **0** |
| `git merge-base --is-ancestor restructure-prep main` | **NO** |
| `git merge-base --is-ancestor restructure-prep physics-focus` | **YES** |

It is a strict ancestor of `systematics-harvest`, so no commit on it is unique.
It is **not** an ancestor of `main`, the pre-restructure collaborator branch.
That divergence is release blocker **B8**, section 4 of this docket, and not a
property of this branch.

**The content check, because ancestry alone does not prove nothing was dropped.**
The blob sets differ: `restructure-prep` carries 381 blobs, `systematics-harvest`
carries 731, and **146** blobs exist at `restructure-prep` but not in the current
tree. Each of those 146 falls into one of two classes, by whether a file of that
name still exists:

| class | count |
|---|---|
| an older revision of a file that still exists | **139** |
| no file of that name on `systematics-harvest` | **7** |

**All seven are recorded removals.** Six are `docs/REMOVALS.md` R1–R6 —
`PlottingWizard.C`, `combinedCanvasPlots.C`, `ListHistos.C`,
`reproduceCanvasPadError.C`, `count_events.sh` and `count_events_bb_cc.C` — each
with a written reason. The seventh, `README.txt`, is `RENAMES.md` §4, *"a 1 KB
compatibility shim"*.

**Conclusion: `restructure-prep` is a stale pointer.** Deleting it loses nothing.
This document does not delete it.
