# Open questions

What is unresolved, what the repository can already show, what closing it would
require, and who owns the decision. Nothing here is a defect the repository can
fix by itself; each item needs a person to decide.

This page is public on purpose. A repository that shows its open questions
survives a referee better than one that hides them. Every fact below was
re-measured by session WRAP at HEAD rather than copied from the architect's
list.

The source list is `ARCHITECT_OPEN_ISSUES_20260901.md`, held outside this
repository.

---

## 0. The manuscript's Model section contradicts the campaign (ruling R50)

**Ranked first by the architect, above every item below.** `paper/Model.tex`
describes a different simulation from the one that produced the figures.

| `paper/Model.tex` | the cards and the campaign |
|---|---|
| √s = 14 TeV (prose `:23`, table `:34`) | `Beams:eCM = 13600` → **13.6 TeV** |
| `PhaseSpace:pTHatMin = 1.` (`:39`) | `PhaseSpace:pTHatMin = 2.` |
| 10⁶ events per job × 100 jobs (`:40-41`) | 100,000 × 1,000 |

**What the repository shows.** Every row is measured at both ends in
`deliverables/20260901/EDITORIAL_NOTES.md` §2.1, with the card and line that
carries each value. The beam-energy row is the sharpest: the figures now print
`pp √s = 13.6 TeV` in their information block under ruling R46, so the document
as it stands would state two different beam energies, one in its table and one
inside every figure. `pTHatMin = 2.` was a measured choice, not a default — at
1.0 the mean `dN_ch/dη` sits 28.6 % below minimum bias, which would distort the
very distribution the percentile classes slice.

**What closing it requires.** Four edits in Overleaf. Under rulings R34 and R38
no session edits `paper/`; the corrections are recorded for the owner to apply.

**Owner.** The owner.

---

## 1. No systematic uncertainties, and no paper-facing statement of that limit

**What the repository shows.** Ruling R31 paused the systematics module and
left it intact and toggleable;
[../systematics/STATUS.md](../systematics/STATUS.md) explains the pause
internally and
[../systematics/REACTIVATION.md](../systematics/REACTIVATION.md) is the work
list. The figures carry ten-block statistical uncertainties only
([../physics/STATISTICS.md](../physics/STATISTICS.md)).

**The gap.** Nothing under `docs2/paper/` states what the paper may and may not
claim without systematics. WRAP measured this: the only mentions of
"systematic" in `docs2/paper/` concern the two retired trees and a card-digest
repair, not the scope of the claim.

**What closing it requires.** A limitations paragraph. The argument is
available and is probably right — the three tunes share the generator, the
cuts, the counter and the class definition, so common systematics largely
cancel in a tune-to-tune double ratio — but it must be made, not assumed. It is
a framing decision, not new computation.

**Owner.** The owner, with the supervisor.

---

## 2. The statistics contract declares itself unreviewed

**What the repository shows, measured at HEAD.**
`config/statistical_robustness_v1.json` carries `"frozen": true` (`:3`) and
`"scientific_review_status": "PENDING_FINAL_PHYSICS_STATISTICS_REVIEW"` (`:4`),
and its `fixed_nch_rationale` (`:5`) says the boundaries "cannot support a
publication claim until the final scientific reviewer explicitly accepts them".
Ruling **R39** records the supervisor approving the ten-block scheme, but that
approval lives only in the decision ledger outside this repository.

**The discrepancy.** The repository publishes numbers under a contract whose
own status field says it is not cleared to support publication.

**What closing it requires.** One of two acts, and the choice is not a
session's to make: either the contract's status field moves — it is a
`config/` file, and the R31 paused list names `tools/statistical_robustness.py`
rather than this config, so it may be editable — or `docs2/` records precisely
why it cannot move and where the approval actually lives. **WRAP did not edit
the contract.**

**Owner.** The owner, with the supervisor who made the R39 approval.

---

## 3. Two paper figures have no producer

**What the repository shows.** `paper/Results.tex:170` and `:182` include
`figures/YieldsBalancing/globalCanvasYieldsPDF_215.pdf` and
`figures/BaryonMesonRelativeYieldsBalancing/globalCanvasRelativeYieldsPDF_215.pdf`.
Both files exist in the tree and both are thesis-era **two-tune** figures
sitting inside a three-tune paper. No target in this repository produces
either.

**Coverage, measured.** The draft carries eleven `\includegraphics`; one
(`Introduction-figures/runningCouplingQCD.png`) is illustrative. Of the ten
physics figures, **eight are produced by this repository and two are not.**
The draft compiles only because the old files are in the tree.

**What closing it requires.** A content decision: either those sections come
out, or something produces three-tune replacements — which is real work, not
editorial.

**Owner.** The owner.

---

## 4. The public repository has no licence

**What the repository shows, measured at HEAD.** `git ls-files | grep -i
license` returns nothing. `CITATION.cff` states that authorship, author order,
affiliations, release identity and licensing are provisional and require
approval.

**Why it matters now.** The repository is public. Without a licence, default
copyright applies and nobody may legally reuse the code that accompanies the
paper — the opposite of what a companion repository is for. Several journals
now ask.

**What closing it requires.** One file, and the agreement of everyone with a
claim to the work.

**Owner.** The owner and the collaborators.

---

## 5. Thirty G9 figures have no destination

**What the repository shows, measured at HEAD.** The kinematic spectra are
produced, mirrored and packaged: `deliverables/20260901/figures/Kinematic
Plots/` holds **exactly thirty** `Inclusive_{pT,eta,phi}_<species>_shape.pdf`
files, ten species × three observables, as
[../pipeline/FIGURES.md](../pipeline/FIGURES.md) `:17` and `:28-33` describe.
The thirty-first file in that directory is G1's multiplicity spectrum, not a G9
figure. The current draft includes **none** of the thirty.

**What closing it requires.** A decision on where they go — supplementary
material, an appendix, a QA figure — or a decision that they are not
deliverables and should stop being carried as such.

**Owner.** The owner.

---

## 6. One copy of the data plane

**What the repository shows.** The raw campaign is 3,000 files and
284,750,292,184 bytes (≈265 GiB) under `/data/alice/ipardoza`, with its seal
intact. The campaign is regenerable in principle, because the seeds are
recorded and PYTHIA is deterministic: `docs/REPRODUCIBILITY.md:302` records
**562.5 CPU-hours** for event generation, and the merge and analysis chain runs
on top of that.

**Why it is a question.** That is a recoverable position, not a safe one. It is
worth being a decision rather than a discovery.

**Owner.** The owner.

---

## Where the related records are

- The deferred work list, and why none of it blocks the paper:
  [DEFERRED.md](DEFERRED.md).
- The rulings index, including R31, R39, R41 and R50: [RULINGS.md](RULINGS.md).
- The discard-bias argument, drafted and unratified:
  [../physics/DISCARD_BIAS.md](../physics/DISCARD_BIAS.md).
- The full editorial list the owner applies in Overleaf, including item 0 above
  and the disclosures rulings R41, R42, R43 and R46 require:
  `deliverables/20260901/EDITORIAL_NOTES.md`.
