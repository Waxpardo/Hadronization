# Finish-the-harvest session — 2026-08-13 (second session that day)

**The harvest could not be finished, and the arithmetic says so plainly: 18 legs
at ~2.68 h/leg is ~48 h of merge, against a session.** So this session did the
work that was not blocked, and one item of it overturned a published claim.

**One commit, `d5356b8..fd60d53`. Suite 37/37.** No tune advanced.

---

## 0. STATE AT OPEN

| | |
|---|---|
| wall clock | **2026-08-13 09:18 CEST** |
| `stbc-i3` uptime | **10:11** — same boot as the previous session, **no new reboot** |
| merge | **ALIVE**, restarted 07:24, still inside `validate_analysis_outputs.py` |
| promotions | **0 new** (15 of 33 carried from the killed v3 run) |

**The validator was verified working, not assumed.** `rchar` on the
**descendant** doing the I/O advanced +121 MB in 15 s at 22–37 % CPU, ~315 GB
read by 09:35. The parent shell's own `rchar` is frozen by construction and
would have read as a stall — the atime frontier would have been worse.

**~2 h in the validation preamble is normal, checked against history rather than
guessed:** the v3 run still had **0 promotions at 5 h 46 m**. It is a fixed
restart cost — the report is rebuilt from scratch every launch — and it is why a
restart is not free even though the merge itself resumes per directory.

---

## 1. THE E5 TRAP — closed, and it was not where the brief said

**The brief named `/data/alice/ipardoza/extract_species_decomposition.py`. That
is not the path the chain executes.** `tune_extract.sh:15` sets
`T=/data/alice/ipardoza/sigmab_runs/task22`, so **that** copy is what every
chain relaunch would have run. Both copies were byte-identical replicating
readers (`b67f9008…`).

**And the reader was not the only defect on that path.** Reading the invocation
rather than assuming it found two more:

| # | defect | consequence |
|---|---|---|
| 1 | reader is the **replicating** one | E5 reproduced silently |
| 2 | **no `--registry`** passed | the fixed reader cannot dedup without it — it is the only thing that says which trigger a pair file belongs to |
| 3 | `--decay-map decay_parent_map_v1_1.json` | the **retired** map, not v2 with the two species-level splits |

All three fixed. Both old readers archived under
`attic_e5_replicating_extractor_20260813/` with a manifest — **moved, never
deleted**; they are E5's evidence. The fixed reader (`4cd8b6fa…`) is installed at
both paths, and both repo roots were seeded with `config/` and `AnalysisScripts/`
so the reader's own defaults resolve even if a caller forgets the flags.

### The proof, because "correct by construction" has to be demonstrated

`chain_path_proof.sh` runs the **exact** command line from
`tune_extract.sh:run_one` against MONASH `combined_root_1`. Its `per_species.csv`
is **byte-identical** to the committed anchor
`merged_monash_dedup/block_1/per_species.csv`, and it reports
`DEDUPLICATION … beauty [26]x, charm [24]x`.

**Known wart, left deliberately:** the top-level copy resolves its default
artifact path to `/data/alice/AnalysisScripts/…` (the reader takes `parents[1]`
of itself), which does not exist. Invoked without flags it **fails closed**,
rc=1, writing nothing — safe but ugly. Not fixed because the reader's sha is
recorded as provenance in `MONASH_CENTRAL_TABLE.md` §0; changing the file to
improve an error message would invalidate that.

---

## 2. THE CHAIN WATCHERS ARE NOT RELAUNCHED — deliberately

They are dead, and leaving them dead is the better operational call. Two reasons,
both measured from the scripts rather than assumed:

1. **The merge already runs closure for all three tunes** at its end
   (`merge_root_files.sh:202-224`), and with a **stronger** invocation than the
   chain's: it passes `expected_central_events=100000000`, where
   `tune_chain.sh:45` passes only two arguments and gets `-1`. MONASH's chain
   closure log shows exactly that: `expected_central_events=-1`.
2. **Relaunching watchers recreates the contention** that is the documented cause
   of the band MISS — closure competing with the merge for CPU.

> **⚠ A LIMIT ON EVERY CLOSURE VERDICT UNTIL THE CHECKOUT ADVANCES.** The brief
> asked for schema v3 enforced via *the required expected-schema argument*. **That
> argument does not exist on Nikhef.** It is the A4 fix, which lives only in the
> local repo; the frozen checkout's wrapper takes
> `CENTRAL BLOCKS [EXPECTED_CENTRAL_EVENTS]` and has no schema parameter at all.
> Until the merge finishes and the checkout can advance, schema verification is
> **by reading the emitted `analysis_schema` and the 2100/1500 counts** against the
> pre-registration — the same check, but not fail-closed.

---

## 3. E4's MISSING CONTROL — the task inverted its own conclusion

**Asked for:** measure σ̂ across the ten MONASH blocks, expect ~1–2, conclude the
anchor's 4.399 is anomalously broad, supersede the flag-count argument.

**Found:** the anchor is entirely ordinary, and the reason is E5.

**The subtlety that decides it.** The anchor and its parent are **both
replicated-era** products. Multiplying counts by R scales a binomial pull by
**√R** and leaves fractional deviations untouched. So the anchor's peer group is
the **replicated** block sweep. Comparing it against the deduplicated blocks
would compare a √24.2-inflated width to an uninflated one and call the difference
a defect.

| sweep | σ̂ |
|---|---|
| deduplicated blocks (10) | **0.955 ± 0.096** |
| **replicated blocks (10)** — the peer group | **4.800 ± 0.519** |

Measured inflation **5.03×** against **√24.2 = 4.92** predicted.

| metric E4 cites | ten genuine 1/10 subsets | **anchor** | |
|---|---|---|---|
| σ̂ | 4.800, range [4.02, 5.65] | **4.399** | inside |
| binomial flags \|z\|>4 | mean 35.3, range [32, 40] | **30** | **below the range** |
| bins deviating >2 % | mean 31.8, range [25, 37] | **29** | inside |
| largest deviation | mean 27.50 %, up to 38.02 % | **32.99 %** | inside |

**"30 of 88" is not an anomaly — genuine blocks give 32–40. "Up to 33 %" is not
an anomaly — genuine blocks reach 38 %.** A 33 % swing in a bin expecting ~10
counts is counting noise.

**What it overturns and what it does not.** It removes the **bin-level
statistical** evidence for the quarantine. It does **not** lift the quarantine
and this session did not lift it: the anchor is **unprovenanced**, and its
physics result was **contradicted by two traceable datasets**. Neither is a
statistical claim.

**The question left deliberately open.** If the anchor is statistically ordinary,
the **−7.4 σ** it produced needs another explanation. A significance computed on
replicated counts would be inflated by the same ~5×, turning ~1.5 σ into 7.4 σ.
**That is a hypothesis, not a finding — it was not checked**, and whether to
check it is the owner's call. **E4 and E5 may be one defect seen twice.**

Committed as `tools/anchor_width_control.py` with the ten replicated block CSVs,
so it regenerates. It carries its own consistency check: fractional deviations
come out identical between the two sweeps, exactly as replication-invariance
predicts.

### Two things I recorded earlier the same day are corrected

- **"The ~2.2× is the block-vs-central overdispersion on clean comparisons"** —
  wrong. Deduplicated blocks give **0.955**; pair counts at block level are
  binomially dispersed after all, and the recorded "353 flags in 880 at ~4.75×
  variance" was itself largely an **E5 artifact**.
- **"The zero is a blind spot, not a clearance"** — wrong explanation. The MAD
  null returns zero because **there is nothing localized to find**. The
  blind-spot property is real and the I2/I3 non-redundancy guidance stands; it
  is just not what produced this zero.

---

## 4. THE BAND — MISS, closed

Owner ruling recorded verbatim in `MERGE_V3_BAND_VALIDATION.md`: 15 legs in
48.6 h (8.35 h one-time gate + 40.25 h merge work, ~2.68 h/leg) projects to
~97 h against a 65–77 h ceiling; cause closure/merge CPU contention;
additionally interrupted by the reboot at 15/33. **Not to be re-scored against
the restarted run.**

---

## 5. NOT DELIVERED — the brief's central deliverable among them

- **No tune advanced.** JUNCTIONS is still central + blocks 1–3; CLOSEPACKING
  still has nothing. **No closure verdict is possible for either.**
- **The three-tune table does not exist.** MONASH's re-extracted values remain
  authoritative and were reused, not re-run.
- **The b-baryon asymmetry advisory table** needs the same three tunes. Not
  produced.
- **Idle-waiting was declined**, per the brief: at ~2.68 h/leg the remaining 18
  legs are ~48 h, so nothing was going to land in this window.

---

## 6. FOR THE NEXT SESSION

1. **Time and uptime first.** The reboot pattern is Jul 8 / Jul 16 / Aug 12 at
   ~23:0x. If the merge is dead, restart it — it resumes per directory, and the
   ~2 h validation preamble is the price.
2. **Expect ~48 h of merge from 2026-08-13 07:24**, so completion around
   **2026-08-15** absent another reboot.
3. **Closure comes free with the merge**, for all three tunes, with the stronger
   `expected_central_events` argument. Read the verdicts from
   `hadronization_analysis/HF_RUN3_V1/validation/pair_block_closure_*.log`
   against the 2100/1500 pre-registration; the schema argument is unavailable
   until the checkout advances.
4. **Extraction is now safe by construction** — `bash tune_extract.sh TUNE`, or
   drive it directly. Verify the header says `map_v2_sha` and `registry_sha`.
5. **Then the three-tune table**, FINAL only if closure passed and integrity is
   clean for all three.
6. **The −7.4 σ question** from §3 is open and is an owner decision.
