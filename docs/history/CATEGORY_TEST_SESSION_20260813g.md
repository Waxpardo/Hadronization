# The category test, and the harvest driver — 2026-08-13 (seventh session)

**Two commits, `0e5a2ba..a44e3bd`. Suite 39/39 → 40/40.** Brief session, as the
brief allowed.

**A2: 301 jobs Idle, zero outputs, no number.** Same boot on `stbc-i3` (up
15:56); merge alive, validator at `JUNCTIONS/slot_725`.

---

## 1. THE CATEGORY TEST — asked and answered

**What the site actually uses**, surveyed from the pool rather than guessed:

| category | running | idle |
|---|---|---|
| medium | **3649** | 9780 |
| short | 789 | 5520 |
| long | 96 | 804 |
| express | 33 | **70266** |

The ~87 k backlog is almost entirely **express**. `medium` has by far the most
capacity and the best idle:running ratio — and for a 47-second job it is also a
*more* truthful label than `long`.

**Ten jobs edited to `medium`** (the regression, which is the gate, plus nine
permissive); **291 left on `long` as the control**. Six minutes of watching:
**neither arm moved, and nothing went Held**, so the edit is harmless.

### Then one read-only diagnostic settled it properly

`condor_q -better-analyze` on the regression job:

```
 0 slots are rejected by your job's requirements
30 slots reject your job because of their own requirements
 0 slots match and are willing to run your job
51 slots would match if drained
```

**Neither the category nor last session's memory right-sizing was ever the
constraint.** Zero slots reject on this job's requirements. The pool is full;
**51 slots will take these jobs when they drain.**

**No further scheduling work is warranted and none will be done.** The ten stay
on `medium` so the A/B keeps accumulating a longer baseline for free — if they
run first, that is worth knowing; if all 301 start together, the category was
irrelevant, which the analysis above already says.

> Worth keeping: the right-sizing was *not* wasted, it was just not the binding
> constraint. It was also the check that made this diagnosis unambiguous — with
> an 8 GB request still in place, "0 slots rejected by your requirements" would
> not have been the answer.

---

## 2. A REAL GAP, FOUND WHILE STARTING TASK 3

**The repo copy of `extraction/pipeline/tune_extract.sh` still carried the E5
defect.** The Nikhef copy was corrected earlier today; the tracked one was not.

So for anyone deploying from the repo it would have **reintroduced the
replication**: no `--registry` (without which the reader cannot deduplicate at
all) and the retired `decay_parent_map_v1_1.json` instead of v2.

Fixed, and verified functionally identical to the Nikhef copy (`diff` ignoring
comments). **Fixing a script in place on the cluster is not the same as fixing
it** — a lesson worth the entry.

---

## 3. THE HARVEST DRIVER

`extraction/pipeline/harvest_tune.py`. The closure verdict is a **pure function
of the log text**, checked against the pre-registration: 2100 content / 1500
invariant, schema `paul_pair_objects_primary_ground_v3`, errors 0.

**The enforcement has to live here.** Review finding A4 added a required
expected-schema argument to the closure wrapper, but that fix exists only in the
local checkout — **the frozen Nikhef tree the merge is reading does not have
it**, and cannot until the merge finishes. So for the upcoming harvest, the
verdict is enforced on the emitted text.

**Tested against MONASH**, per the brief's standard:

| | |
|---|---|
| MONASH's **real recorded** closure line | PASS |
| committed anchors through the decomposition stage | **I3 exact at 53,662,416**, **I2 clean, 0 flags in 10** |
| recorded values reproduced | **52.4959 / 46.4946 / 1.0095** |

**Seven failure modes each fail independently**, the important one being
**1800/600 with `errors=0`** — the v2-sidecar resolution, which reads as a pass
to anything that greps the error count. The driver names it as that specific
failure mode rather than reporting a generic mismatch. A truncated line
containing only `errors=0` is also rejected, because that is the field a
careless reader checks.

**What is NOT tested end-to-end:** the closure *execution*. MONASH's closure took
**~14.9 h**; re-running it to test a parser would be absurd. The verdict logic is
tested against the real recorded output, and the extraction stage is the chain
path already proven byte-identical to the committed anchors last week.

---

## 4. FOR THE NEXT SESSION

1. `condor_q 5478114 5478127 -af JobStatus | sort | uniq -c`, and note whether
   the ten `medium` jobs started before the 291 `long` ones.
2. When the regression lands: `tools/a2_record_regression.py` first — nothing
   else writes the sentinel, and the analyzer will not run without it.
3. When a tune's merge completes: `harvest_tune.py TUNE --stage closure
   --closure-log …`, then extraction, then `--stage decompose`.
