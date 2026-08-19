# Paul's stack on v3 — the delta enumerated, and a premise that failed

**2026-08-13 (ninth session). Two commits, `a527f02..`. Suite 40/40. No code
changed in `plotting/`.**

A2: **301 Idle, 0 outputs**. Merge alive, validator `JUNCTIONS/slot_829`, same
boot, 0 promotions. Neither touched.

> Two drift notes on the brief: the repo was at **`a527f02`**, not `32b35c7`
> (two commits from the previous session), and the SVG generator is
> `plotting/paper/make_paper_figures.py`, not `tools/make_figures.py`.

---

## 1. E5 EXPOSURE — not exposed, and for a better reason than expected

The brief expected the answer to be "the observable comes from `hCorrelations`,
which is per-pair." True, but incomplete. The per-pair-file write loop
(`status_analysis_THnSparse_qq.C:1179-1191`) replicates **three** classes of
object, and the stack handles each correctly:

| object | replication | how the stack handles it |
|---|---|---|
| `hCorrelations` family | none | summed freely — correct |
| `hTrKinematics` + closure set | **24× / 26×**, trigger-owned | read **one file at a time** (`:3168-3171`); no `Add`/`hadd`/`TFileMerger` anywhere in `plotting/` |
| `summed MULTIPLICITY` | **300×**, event-level | treated as an **identity invariant** — one `central_reference`, all others verified equal (`:1786-1800`) |

`Plot_FlavourClosure.C` reads a **single** pair file and forms its ratio within
it, refusing to draw if the sum rule deviates by >1e-6.

**The finding worth keeping: E5's entry names only the closure histograms, but
`hTrKinematics` and `summed MULTIPLICITY` are replicated by the same loop.**
Anyone summing `hTrKinematics` across pair files reproduces E5 exactly, and the
entry as written would not have warned them. **E5 annotated** with the general
rule: *in a v3 merged directory only the `hCorrelations` family is additive
across files.*

---

## 2. THE DELTA — smaller than expected in five places, larger in one

`docs/PLOTTING_V3_DELTA.md`, committed **before any code was touched**, as the
brief required.

**Measured against the merged product, not assumed:** of the six metadata strings
the contract exact-matches, **only `analysis_schema` differs** between v2 and v3.
Implementation, version, profile, `selector_version` and combinatorics mode are
identical.

**The 7-vs-5 object question needed no work at all** —
`pair_file_object_contract_v1.json` already declares `schema_version_tags
{v2, v3}`, keys the object set on the file's own schema, and fails closed on an
unlisted tag. No strict object enumeration exists in `plotting/`.

Remaining: contract mode is code-side (**B2**), contract keys are `v2_`-prefixed
under `RequireExactKeys` (**B3**), no HF_RUN3_V1 selector entry exists at all
(**B4**), legacy data paths (**B5**).

**B6 is the one that is not configuration.** `thresholdsByTune` derives classes
**per tune from each tune's own MULTIPLICITY** — the per-tune percentile scheme
the axis ruling **rejected** in favour of common absolute N_ch boundaries.

---

## 3. WHY NO CODE WAS WRITTEN — a premise of both rulings is false

The owner ruled B6 → "add a mode alongside" and B3 → "teach a `v3_` prefix",
each with conditions. Both rest on **the v2 path staying reproducible**. Then:

| the v2 config points at | local | Nikhef |
|---|---|---|
| `complete_root_21_06_2026` | **ABSENT** | **ABSENT** |
| `SUBSAMPLES_700/…` | **ABSENT** | **ABSENT** |

- **B3's acceptance test is unrunnable as specified** — "run the v2 config before
  and after and get identical output" needs data that no longer exists. A
  data-free equivalent exists and is the shape
  `test_pair_selection_contract_parity.py` already uses (source- and
  config-level key-set equality), but it is a **different** test and should be
  accepted explicitly, not substituted quietly.
- **B6's rationale is weakened.** Option 1 was chosen to keep the old figures
  regenerable. **They are not regenerable — their inputs are gone.** If
  regenerability was the reason for the larger diff, Option 2 (replace the
  derivation) is now both the smaller diff and the better fit for "a large diff
  is a failure."

**Put back to the owner rather than decided.** Writing the larger diff against a
rationale that no longer holds would be the wrong call in a session whose
governing principle is diff minimality.

---

## 4. READINESS VERDICT

**Nothing in Paul's stack runs on v3 today**, and Task 4 (prove on MONASH) was
therefore not reachable: the stack refuses v3 metadata at
`improvedPlotting_THnSparse.C:908-915` before it opens a histogram.

**When B1–B5 land, adding JUNCTIONS and CLOSEPACKING is configuration, not
code** — the tune loop already keys everything by tune name, so it is two
selector/config entries and a re-run.

**B6 decides everything about the size of this job.** Until it is settled, the
observable figure cannot be produced correctly, because the class definition
would not be the one the paper ruled on.

**Unknown until three-tune data exists:** whether the per-tune residual behaves
as the ruling's 2.91 pp predicts once the observable is binned on it, and
whether any tune's high-multiplicity classes are too sparse for the OS−SS
subtraction to be stable.

---

## 5. NEXT SESSION

1. Owner decision on B6 in light of §3, and on the substitute acceptance test
   for B3.
2. Then B4/B5/B1 (additive: selector entry, v3 config, schema value), B2 and B3
   (small code), B6 (scoped by the decision).
3. Then Task 4 on MONASH — and **look at the figure**, since a stack that runs
   and plots nonsense reports success.
