# Rulings — an index

The ledgers are canonical. They live in the project archive outside this
repository, as `DECISION_ENTRIES_20260827.md` (R19–R30),
`DECISION_ENTRIES_20260830.md` (R31–R42),
`DECISION_ENTRIES_20260831.md` (R43–R47) and
`DECISION_ENTRIES_20260901.md` (R48–R50). This page is an index, not a copy: it
gives one line per ruling so a reader can tell which ledger entry to open.

Do not quote a ruling from this page. Open the ledger entry.

## R19–R30 (2026-08-27 to 2026-08-29)

| id | one line |
|---|---|
| R19 | Retire the `AnalysisScripts/` name; the contracts move to `contracts/`, the anchors to `evidence/` |
| R20 | The pipeline map is a living document, revised at every acceptance review |
| R21 | Keep `sigmab_raw`: it is the evidence behind the published Σ_b table |
| R22 | Rewrite the 34 dangling citations; restore no purged internal record |
| R23 | Do not keep the duplicate `references/` bibliography copy; it moves to the archive |
| R24 | Schedule the S10.1 producer-reproduction run; move the other eight unreached `Validation/` macros internal |
| R25 | Wire `tools/merge_supervisor.sh` into `./hadronization merge` |
| R26 | The three unparried PR-13 behaviours are retired with a record, not restored |
| R27 | Repair the stale `ValidationReports/` citations only where no digest pin covers card bytes |
| R28 | Paper-only completion: audit first, then one plan, adversarially reviewed |
| R29 | The Nikhef deployment is the final architecture; the local rebuild is the authoring bench |
| R30 | Every test, gate and script earns its place by the paper output it protects |

## R31–R42 (2026-08-30)

| id | one line |
|---|---|
| R31 | Systematics development is paused; the module stays intact and toggleable |
| R32 | The JUNCTIONS-only fourth tune (`JUNCTIONS_MATCHED`) is removed, with a record |
| R33 | `docs2/` is the documentation home; stale documents are updated or removed |
| R34 | The Overleaf paper is the guidance for what the repository must produce |
| R35 | After consolidation the only remaining work is writing the paper |
| R36 | PR 13 is the reference baseline, not authority |
| R37 | The sample table is regenerated from the current campaign, with its definitions stated |
| R38 | The repository requires no integration with the paper; `paper/` is reference only |
| R39 | The ten-block statistics scheme is approved |
| R40 | Balancing figures carry two trigger columns — lightest meson and lightest baryon per flavour — with the legacy associate set by default and no cross-flavour observable |
| R41 | The hang rates are acceptable and are disclosed |
| R42 | The `N_ch` decay-policy mismatch stays as measured and is disclosed; a validation campaign is noted for after the paper |

## R43–R47 (2026-08-31 to 2026-09-01)

| id | one line |
|---|---|
| R43 | B_c⁻ leaves the two extreme-class beauty columns (G5/G7); the integrated figures keep it |
| R44 | Deliverables are reviewed locally, then published to GitHub; the owner pushes, after the archive branch exists |
| R45 | One session performs every figure correction and a full style pass, against a written checklist |
| R46 | Figure identification: panel titles off, each fact stated once — information block, column header, row label, one canvas legend |
| R47 | Sequencing: RUN-N4 → owner figure review → ARCH-1 → HANDOFF → WRAP → PHYS-1 → final adversarial review |

## R48–R50 (2026-09-01)

| id | one line |
|---|---|
| R48 | One session at a time on a checkout; a brief that follows another names the predecessor's exit commit as its entry pin |
| R49 | Three process rules from ARCH-1, now binding: lock records are evidence; a stale `.git/index.lock` is an entry-gate item; the bare-anchor convention is adopted |
| R50 | The manuscript's Model section is the highest item on the paper's path — `paper/Model.tex` states a beam energy, a `pTHatMin` and a job factorisation the campaign contradicts |

All four ranges are listed complete: twelve entries in R19–R30, twelve in
R31–R42, five in R43–R47 and three in R48–R50.

## Where each ruling is applied in `docs2/`

| ruling | page |
|---|---|
| R25 | [../pipeline/MERGE.md](../pipeline/MERGE.md) |
| R31 | [../systematics/STATUS.md](../systematics/STATUS.md) |
| R33 | [../INDEX.md](../INDEX.md) |
| R37, O2 | [../physics/SAMPLE_COUNTING.md](../physics/SAMPLE_COUNTING.md), [../pipeline/COUNT.md](../pipeline/COUNT.md) |
| R38 | [../paper/DELIVERABLES.md](../paper/DELIVERABLES.md) |
| R39 | [../physics/STATISTICS.md](../physics/STATISTICS.md) |
| R40 | [../pipeline/RENDER.md](../pipeline/RENDER.md), [../pipeline/VERIFY.md](../pipeline/VERIFY.md) |
| R41 | [../pipeline/PRODUCE.md](../pipeline/PRODUCE.md), [CAMPAIGN_TRUTH.md](../paper/CAMPAIGN_TRUTH.md) |
| R42 | [../physics/MULTIPLICITY.md](../physics/MULTIPLICITY.md) |
| R43 | [../paper/DELIVERABLES.md](../paper/DELIVERABLES.md) |
| R45, R46 | [../pipeline/STYLE.md](../pipeline/STYLE.md) |
| R48, R49 | recorded as practice in the project's `PRACTICE.md` §15.5, outside this repository; the defects that produced them are in [ARCHITECT_LEDGER.md](ARCHITECT_LEDGER.md) |
| R50 | [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md) |

## Owner decisions O1–O5

The consolidation plan carries a separate owner-decision register, O1–O5. It is
not renumbered here. O1 (campaign parameters) is written up in
[../paper/CAMPAIGN_TRUTH.md](../paper/CAMPAIGN_TRUTH.md); O2 (the T1 wording) in
[../physics/SAMPLE_COUNTING.md](../physics/SAMPLE_COUNTING.md); O5 (the
`JUNCTIONS_MATCHED` annotation) in
[../systematics/REACTIVATION.md](../systematics/REACTIVATION.md).
