# Figure 3, and one bounded fix to the A2 queue — 2026-08-13 (sixth session)

**Two commits, `f96f37e..bafffcf`. Suite 39/39** throughout.

**The A2 jobs never started**, so this was the Task-1 idle branch followed by
Task 2. No A2 number exists.

---

## 0. STATE

| | open 14:31 | close 14:43 |
|---|---|---|
| `stbc-i3` | up 15:24, same boot | unchanged, **no reboot** |
| A2 jobs | **301 Idle**, 0 outputs | **301 Idle** |
| merge | alive, `JUNCTIONS/slot_611` | alive, `slot_650` |

---

## 1. THE BOUNDED A2 CHECK — the requests were 52× oversized

The brief allowed one check: are the submit file's requested resources larger
than these jobs actually need? **They were, by a lot.**

Measured across **60 completed production analysis jobs** — the same macro on
the same inputs:

| | observed | requested |
|---|---|---|
| memory | min 15 MB, median 80 MB, **max 158 MB** | **8192 MB** |
| disk | ~31 MB of output | **8192 MB** |
| runtime | **~47 s** (31 s user + 3 s sys) | `JobCategory = "long"` |

The profile was inherited wholesale from the campaign submit file, where it was
presumably sized for a different job. **An 8 GB request only matches slots with
8 GB free**, which in a pool running ~4,800 jobs against ~87,000 idle is a real
constraint.

**Adjusted in place with `condor_qedit`** to **1024 MB / 2 GB** — still 6.5×
the observed memory peak and ~65× the output size. All 301 jobs took the edit.
**This is not a resubmit**: the jobs keep their cluster ids, their queue
position, and their provenance.

> **`JobCategory = "long"` was left alone**, deliberately. A 47-second job in a
> "long" class is plausibly also costing matches, but the category maps to site
> policy I cannot read from here, and it sits close enough to the
> "don't change accounting groups" instruction that guessing was the wrong move.
> **Recorded as an observation for the owner, not acted on.**

Nothing else was touched. No resubmission.

---

## 2. FIGURE 3 — and the artifact that had to be committed first

The brief's standard is **"recomputed from committed artifacts, never
transcribed."** The artifacts behind the multiplicity class definition **were not
in the repo** — they lived only at `/data/alice/ipardoza/b4_mapping/out/`. So
meeting the standard meant committing them first, not transcribing the table.

**New anchor `AnalysisScripts/anchors/b4_multiplicity_mb`**: the three per-tune
minimum-bias N_ch histograms (4.3 kB each), their CSV dumps, the dumper, and the
original run provenance. **MONASH's 172,429 events is the count the axis ruling
cites** for the boundary derivation — which is how the right artifact was
identified rather than assumed.

The figure then **recomputes** the paper-facing translation table and reproduces
it to **< 0.01 pp on all eleven classes**, with the maximum residual landing on
**2.91 pp** exactly.

### The labelling bug — the same trap, twice

The first recomputation disagreed with the published table **on exactly one
row**: c1 read **0.51 %** against the published **0.00 %**, everything else
exact. That shape is seductive — it looks like a one-row disagreement in the
data.

**It was a labelling bug in my dumper.** The axis is `[-0.5, 399.5]` with unit
bins, so **bin 1 is N_ch = 0 and its low edge is −0.5**. Dumping by low edge and
rounding turns N_ch = 0 into "−1", moving **872 MONASH events** out of the first
class. Every other boundary counts that bin either way, so only c1 moved.

`dump_nch.C` now uses **bin centres** and **refuses outright** if under/overflow
is non-empty.

> **The boundary derivation had already recorded one half-integer-edge
> off-by-one** — `FindBin(2.5)` returning the bin *above* the edge. Half-integer
> boundaries are the point of the design (no integer N_ch is ambiguous) and they
> are also where the mistakes live. **Twice now.** Written into the anchor
> manifest so the third time is caught faster.

### What the figure shows

- **Panel A** — the common absolute N_ch boundaries as bands, each labelled with
  its MONASH-MB percentile. Boundary labels are **staggered into two rows**: the
  low-N_ch boundaries are only ~19 px apart at this scale, so single-row labels
  sat within a few pixels of each other. **Found by reading back the drawn
  geometry, not by eye** — and the first check's "11 collisions" was a false
  positive from the intentional value-over-percentile stacking, so the geometry
  had to be read properly rather than trusted.
- **Panel B** — each tune's percentile minus MONASH's, per class, against the
  ±3 pp band.

**The distinction the ruling insists on is on the figure's face:** the residual
is **not** the ±3 pp criterion passing. That criterion asked whether *per-tune*
boundaries coincide — they do not. This is how far a *common* boundary's meaning
drifts. The test asserts that sentence is present.

Digest `9bf61215…96a8e109`, recorded in `GOLDEN_OUTPUTS.md` §2.12 with figs 1
and 2; recipe R13.

---

## 3. NOT DONE

- **No A2 result.** 301 jobs Idle; the gate remains unsatisfied and enforced.
- **No further figures.** The remaining certain ones (OS−SS versus multiplicity,
  the systematics summary) need data that does not exist. `--figure ossvsmult`
  still fails closed.
- The three-tune harvest, disk consolidation, `Paper/**`: untouched.

---

## 4. FOR THE NEXT SESSION

1. `condor_q 5478114 5478127 -af JobStatus | sort | uniq -c`. The jobs now
   request 1 GB / 2 GB; if they are still idle after this, the constraint is the
   pool, not the profile, and `JobCategory` is the remaining lever — **an owner
   call.**
2. When the regression lands: `tools/a2_record_regression.py` first. Nothing
   else can write the sentinel, and the analyzer will not run without it.
3. Fig 1 gains its other two tunes with **no layout work** — commit their
   per-species anchors, extend the two dicts, re-run, re-record the digest.
