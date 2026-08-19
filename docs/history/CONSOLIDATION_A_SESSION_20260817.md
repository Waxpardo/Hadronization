# Consolidation A — reconciliation, disk mapping, and the ledger fix — 2026-08-17

**Suite 48/48 → 49/49 (one new contract test). Wall clock 18:25–2x:xx CEST.**
`stbc-i3` up **4 d 19 h**, `stbc-i1` up **4 d 20 h** — **no reboot** since
2026-08-12.

> **Headline: the scratch reconciliation is complete and it found the record
> in better shape than expected — of everything ever deployed to Nikhef scratch,
> exactly two files differ from tracked content in a way no commit explains, and
> neither is a defect. Ten files that matched nothing were behind published
> numbers and are now anchored. The disk's loose top-level files are
> consolidated with an 82/82 verified manifest pair, and the one size the Aug 12
> inventory deliberately left blank is measured. The seed-ledger collision guard
> can no longer be silently off.**

---

## 1. THE ADVANCE — TAKEN, `43e35be8` → `8650a047`

**`make can-advance` passed CLEAN. No override was used, and none was needed.**

```
CHECKOUT_ADVANCE_ALLOWED queue verified empty; no job can be pinning a commit
```

| | |
|---|---|
| old head | `43e35be876dd5d881a931cb845ab490ab9b97509` |
| **new head** | **`8650a04752ec5d8d2d97a811598027dc0208bdef`** |
| commits carried | **153** |
| method | `git bundle` 2.1 MB, verified locally **and** on arrival, fetched in place, `git merge --ff-only` |
| bundle cut | **at advance time**, 20:11 CEST — not before |

**Both repositories are now identical at `8650a047`.**

### 1.1 The queue had to be emptied first, and it was — legitimately

The gate refused all evening on its **queue branch** (`CHECKOUT_ADVANCE_REFUSED
n job(s) in flight`), never on the pinfile — confirming the pin was already gone.
The last 65 jobs drained over ~2 h, and **the final three hung and were held by
the hang guard**, which is what made the removal a routine authorized action
rather than a wait:

```
5523774.2  HF_HANG_GUARD suspected generator hang: cpu>3600s or wall>14400s
5523775.5  HF_HANG_GUARD  "
5523779.4  HF_HANG_GUARD  "
```

The retry round's own `condor_rm` cleared them, the queue reached a **verified
zero**, and the advance was taken in that window. **The retry clusters were then
submitted and released.** Nothing was overridden and nothing was skipped; the
queue really was empty at the moment the gate was asked.

### 1.2 The hang is tune-localized, and that is a measurement

Of the 67 retry-1 jobs, **8 ran 42–55 min against a 4–6 min MONASH median**, and
**every one of the 8 was JUNCTIONS or CLOSEPACKING — zero MONASH.** Five
completed slowly; the three that crossed 3600 s CPU were **all JUNCTIONS**.

This is `GOLDEN_OUTPUTS.md` N5 seen again from a different angle: *the hang hits
dense-junction topologies — exactly the configurations under study.* It also
means **the documented "264–350 s per job" figure is a MONASH number and should
not be used to budget CR-tune campaigns**; it is off by an order of magnitude for
JUNCTIONS at varied scales.

**Retry-2 clusters, from the submit output and never from a queue scan:**

| campaign | job | cluster |
|---|---|---|
| `HF_SYS_MUR_UP` | JUNCTIONS:75 | **`5526031`** |
| `HF_SYS_MUR_DOWN` | JUNCTIONS:66 | **`5526032`** |
| `HF_SYS_PTHAT_1` | JUNCTIONS:51 | **`5526033`** |

All three rendered at **attempt 2** with the ordinal and card variant **derived
from each campaign's own sidecars** (4/`mur_up`, 5/`mur_down`, 9/`pthat_1p0`) —
never passed — and with `--seed-ledger` given explicitly against the
authoritative ledger.

### 1.3 Post-advance verification — all three checks passed

| check | result |
|---|---|
| suite on Nikhef | **49/49**, ROOT present — **the first green suite ever run from the restructured tree on that machine** |
| guard suite live | **7/7** |
| `make can-advance` after | `CHECKOUT_ADVANCE_ALLOWED`, exit 0 |
| the hook itself | logged its own verdict: `CHECKOUT_ADVANCE_ALLOWED 2026-08-17T20:12:19+02:00 ref=refs/heads/physics-focus 43e35be8 -> 8650a047 (schedd answered and holds nothing)` — after three recorded refusals on 08-09, 08-10 and 08-14 |

> ### The installer fix passed its first real test, and the test was sharper than expected
>
> The hook installed on 2026-08-10 carried this warning **in its own body**:
>
> > *"⚠ THIS COPY HAS BEEN EDITED IN PLACE, 2026-08-10, and the installer does
> > not know about the edit. RE-RUNNING `install_checkout_guard_hook.sh` WILL
> > SILENTLY REVERT THE DETACHED-RUN PIN BLOCK BELOW. The in-tree fix is
> > authorized only after the freeze lifts."*
>
> **The freeze has now lifted and the in-tree fix is exactly what the advance
> delivered**, so re-running the installer became the authorized action. It was
> run, and the result is the point: comparing the pre-advance hook against the
> freshly installed one **on non-comment lines only**, the entire difference is
> the line-wrapping of two `echo` strings inside a refusal message.
>
> **The detached-run pin block survived intact** — `PINFILE="${GIT_DIR_PATH}/checkout_pin"`,
> existence-based, fail-closed, checked *before* the queue probe. The
> hand-patched gap is now carried by the tracked installer, and the warning it
> carried is retired by having been made false.
>
> The pre-advance hook was **archived, not overwritten**, at
> `hadronization/archive/gate_artifacts/reference-transaction.preadvance_20260817`
> (`2340a88f…` → `e62aa428…`).

## 2. THE SEED-LEDGER FIX — `4306fa2`

`resubmit_held.py --seed-ledger` was **optional with no default**. A retry
rendered without it ran with the collision guard **off and said nothing about
it** — and that failure is invisible afterwards: the duplicated events are
internally consistent, carry a valid sidecar, and no downstream validator can
tell them from independent draws. Rendering is the only place it can be caught.

**Now exactly one of `--seed-ledger` and `--no-ledger REASON` is required**, in
dry runs too, so the dry run previews the same guard state the apply will use.
The chosen state is printed either way.

**A default ledger path was rejected deliberately** and the reason is in the
source: it would make a retry against the *wrong* ledger look served, which is
worse than a missing argument because it reads as a guard that ran.

> **The test was verified against the pre-fix tool**, which is the only way to
> know a regression test tests anything. Pre-fix, the omission case exits **0**
> on a clean-looking dry run with no mention anywhere that the guard was off —
> the silent-off state, reproduced.

The Makefile always passed `--seed-ledger`; the exposure was **direct CLI
invocation**, which is how the systematics retries are run.

## 3. THE SCRATCH RECONCILIATION — `docs/SCRATCH_RECONCILIATION.md`

**Compared by content, not by path.** The Aug 12 restructure moved most of these
files while the Nikhef checkout stayed at the pre-restructure `43e35be8`, so a
path-based comparison would have reported nearly everything missing. Every
deployed file was hashed and looked up against every blob at `HEAD`, at
`43e35be8`, and — where neither matched — across the last 400 commits.

### 3.1 "Both nodes" is one filesystem, and that was checked

`/data/alice` is the **same NFS mount** (`data-02:/alice`) on `stbc-i1` and
`stbc-i3`; `$HOME` is `/user/ipardoza` on both. **There is one scratch area, not
two.** The only node-local artifact found anywhere is an empty `/tmp` directory
on i3 from July. Reaching i1 needs the jump host from the laptop —
`ssh -o ProxyJump=nikhef ipardoza@stbc-i1.nikhef.nl` — because the key is not
forwarded and `ssh stbc-i1` *from* i3 is refused by publickey.

### 3.2 What matched

| | |
|---|---|
| the 7 scratch-deployed tools | all match tracked content; the deploy pattern is deliberate and stays |
| **the 10 charm-M7 block logs** | **byte-identical to anchors G36–G45** — N7 was closed Aug 12 and this is the first check back against the scratch originals |
| both A2 variation macros | `a4df31e6…` and `4e491134…`, exactly the two **admissible** entries in `config/a2_variations_v1.json` |
| the 4 E5 extractor files | match tracked `HEAD`; the superseded replicating reader `b67f9008…` is recoverable from history at `003da54b` |
| the plotting run tree | 93 files: 80 at `e0b9aba`, 3 at current `HEAD`, 10 build products. **Zero locally-modified source** |

### 3.3 The two that differ, and why neither was committed

**`tune_extract.sh`** — 19 changed lines, and **every one is a comment**.
Filtering the diff to non-comment lines returns empty. The executable content is
identical, and the *tracked* wording is the better of the two: it records that
the Nikhef copy was corrected first and the repo copy second. Committing the
deployed version would replace the more informative comment with the less
informative one. **Archived with the diff recorded.**

**`a2_make_subs.py`** — the pre-parameterization first version. The decisive
fact is the sha it hard-codes: `VARIATION_SHA = "22120383…"`, which
`a2_variations_v1.json` lists under **`superseded`** as
`permissive_smallest_index_guarded` — the **E7** arm whose per-job throw selected
on the outcome variable and discarded 49 of 100 MONASH jobs. Entries under
`superseded` are explicitly inadmissible. So it generated an arm that produced no
admissible result, and its tracked successor already records its existence and
its defect. **Archived with the diff recorded.**

### 3.4 What was committed — `56e013a`

Ten files that matched nothing tracked and sat behind published numbers:

- **`closure_v3_verdicts/`** — the two `CANONICAL_PAIR_BLOCK_CLOSURE_PASS`
  verdicts that gate `THREE_TUNE_CENTRAL_TABLE.md`. The verdicts were quoted in
  session records; **the logs were committed nowhere.** Same gap N7 had, closed
  the same way.
- **`e5fix_drivers/`** — the extractor was tracked, but not *how it was invoked*:
  run root, subsample directory, tune order.

### 3.5 ⚠ One of my own corrections, `6390e19`

`56e013a` also anchored `b4_mapping/macro/CalibrateMultiplicityAgainstMinBias.C`
because it matched no tracked content. **It matched none because it differs from
the tracked `Validation/CalibrateMultiplicityAgainstMinBias.C` by exactly one
line** — the include path `SimulationScripts/` vs `generation/producer/`, which
the Aug 12 restructure moved. The b4 run is from Aug 9 and predates it.

So it is the **pre-restructure form of a tracked file**, and anchoring it put a
second, older copy under a second path where the two can drift. **Removed, and
archived in place with the diff recorded.**

> **The copy did establish something worth keeping: the macro is NOT unrun.**
> `b4_mapping/logs/` holds six completed runs — `{mb,hard} × three tunes` — each
> ending `B4_RUN_EXIT=0`, with six `nch_*.root` outputs. The MONASH mb run
> produced **51.201** (|η|<4) and **12.948** (|η|<1), the counters
> `NCH_DECAY_POLICY_BIAS_8317.md` quotes as the measured input S4 needs.
> **`STATE.md`'s "WRITTEN — UNRUN — AVAILABLE" table is therefore wrong about
> it**, and is struck through rather than silently edited, because other sessions
> have read that table.

### 3.6 One expected artifact was gone, and that is correct

The **stale JUNCTIONS partial** this session was authorised to archive **no
longer exists**. The merge consumed and promoted it:
`complete_root_HF_RUN3_V1_JUNCTIONS` is present, and all three tunes plus
`SUBSAMPLES_HF_RUN3_V1` are complete. The Aug 12 inventory's warning — that a
sweep matching `*.partial.*` would delete a running merge's output — was never
tested, because the merge finished the job properly.

## 4. THE DISK — `docs/DATA_LAYOUT.md`, inventory refreshed

**The one size the Aug 12 walk deliberately left blank is now measured.** That
walk recorded, as a choice rather than an oversight, that
`hadronization_analysis/` had no size: `readdir` on ~3000 live slot directories
would have stamped atimes that corrupt the merge's frontier probe *and* report
the walk itself as merge progress. **The merge completed today at 16:16 CEST, so
the walk is safe. It is 94 G.**

| tree | Aug 12 | Aug 17 |
|---|---|---|
| `hadronization_production/` | 304 G | **495 G** — +195 G of `HF_SYS_*` |
| `hadronization_merged/` | 41 G | **88 G** |
| `hadronization_analysis/` | *not walked* | **94 G** |
| free / used | 1.1 T / 97 % | **784 G / 98 %** |

**The systematics program was costed at ≈ 193 G before it was spent. It measures
195 G.** Within 1 % of the pre-registration.

**Physical consolidation: 79 loose top-level files moved** into
`/data/alice/ipardoza/hadronization/`, with a before/after sha256 manifest pair
in which **all 82 files hash identically — zero lost, zero altered.** The three
`systematics_*.bundle` were deliberately left in place (live until convergence),
which is the 82 − 79. Both of the inventory's "must not be swept up" items were
respected: the seven deployed tool copies moved **as a group, still outside the
checkout**, and the C-3 binary backup went to `archive/binaries/`.

## 5. BOUNDARIES

No `Paper/**`. No systematics harvest. The deploy at `72ca4e39` was **read but
never written** — its jobs verify that commit at startup. `b-hadron-fractions/`
untouched. `merge_runs/`, `archive/` and `a2_runs/` frozen, unread except for
`ls`. Nothing deleted anywhere.

## 6. FOR THE NEXT SESSION

1. **The scratch-directory consolidation is NOT done.** 40 directories, 234 M
   total, are enumerated and manifested (3826 files hashed) but **the move was
   refused by the local permission gate**, not by any project rule. It is a
   single `mv` per directory into `hadronization/scratch/`, and the path
   translation table in `DATA_LAYOUT.md` §3 already anticipates them.
2. **`STATE.md` PENDING #12** records, without building it, the guard
   improvement this session made concrete.
3. **The systematics campaigns are still converging.** Their harvest is a
   separate session, and the deploy must not move until then.
