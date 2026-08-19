# HF_RUN3_V1 — publication authorization

**Granted by the owner 2026-08-17.** This document is the authorization the
dataset selector cites. Its sha256 is recorded in
`config/dataset_selector.json` and `config/dataset_selector_hf_run3_v1.json` as
`publication_authorization_sha256`.

**Effect:** `hf_run3_v1_candidate` moves from `canonical_candidate` /
`publication_eligible: false` to **`canonical` / `publication_eligible: true`**.
Figures and tables derived from this campaign become eligible for the
manuscript.

---

## 1. THE PRECONDITIONS THE OWNER CITED

| # | precondition | state |
|---|---|---|
| 1 | closure PASS ×3 at the registered counts | met |
| 2 | the three-tune central table FINAL | met |
| 3 | 3000/3000 receipts | met |
| 4 | merge 33/33 | met |
| 5 | E5-corrected extraction | met |
| 6 | suites green | met |

## 2. WHAT WAS RE-VERIFIED BEFORE SEALING — 2026-08-17

**These are facts checked in the sealing session, not inherited from earlier
records.** A seal that restates prior claims adds a signature but no evidence.

### 2.1 Counts, on disk

| quantity | measured | expected |
|---|---|---|
| promoted raw `.root` | **3000** (1000 × 3 tunes) | 3000 |
| `.root.sha256` sidecars | **3000** | 3000 |
| `attempt_metadata` receipts | **3000** | 3000 |
| `raw_validation` job directories | **3000** | 3000 |

> A first pass appeared to show 2999 / 3062 / 3063 `raw_validation` entries. That
> was an artifact of `ls` printing directory headers and blank separators, not a
> shortfall: the layout is `raw_validation/<TUNE>/job<NNN>/attempt<NNN>/`, and all
> three tunes hold exactly 1000 job directories. Recorded because the first
> number looked like a defect and was not one.

### 2.2 The merge

| quantity | measured |
|---|---|
| `PROMOTED_MERGE` lines, `merge_v3.log` | 15 |
| `PROMOTED_MERGE` lines, `merge_v6.log` | 18 |
| sum | **33** |
| **distinct** (tune, block) legs promoted | **33** |

**The sum and the distinct count agree**, which is the load-bearing check: the
merge was killed by the 2026-08-12 reboot at 15/33 and restarted twice, so a
re-promotion would have inflated the sum above the distinct count. It did not.

### 2.3 Closure

Exactly one `CANONICAL_PAIR_BLOCK_CLOSURE_PASS` marker per tune — MONASH,
JUNCTIONS, CLOSEPACKING — and the verdict line reads:

```
PAIR_BLOCK_CLOSURE errors=0 analysis_schema=paul_pair_objects_primary_ground_v3
central_pair_files=300 block_pair_files=3000
object_content_sumw2_closure_checks=2100 additive_metadata_closure_checks=3600
invariant_metadata_checks=1500 source_filter_contract_checks=300
expected_central_events=100000000 relative_tolerance=2e-10
```

**The merge's own closure pass and the separately-launched closure runs produce a
byte-identical verdict line.** The independent runs' logs are committed at
`AnalysisScripts/anchors/closure_v3_verdicts/`; the merge's line was read from
`merge_runs/HF_RUN3_V1_merge/` this session. Two independent passes agreeing
exactly is stronger than either alone.

### 2.4 The freeze artifact

**It already existed, built 2026-08-09 17:35, and was verified rather than
rebuilt.** `tools/build_canonical_manifest.py` refuses to overwrite an existing
freeze, which is correct behaviour and is why this session validated the
artifact instead of regenerating it.

| check | result |
|---|---|
| `freeze_seal.json` schema | `hf_canonical_freeze_seal_v2` |
| rows | **3000**, 1000 per tune, 10 blocks |
| total requested successes | 300,000,000 |
| `canonical_manifest_sha256` in the seal vs the file | **identical** — `fcd96eae…` |
| ten `block_*.jsonl` rows summed vs manifest rows | **3000 = 3000** |
| producer sha in every row | `e54b27bb9e3f…` — contract **C-3** |

**Validity against the bytes on disk.** The newest raw file in every tune predates
the freeze (MONASH Aug 9 08:09, JUNCTIONS Aug 9 16:12, CLOSEPACKING Aug 9 15:14,
freeze Aug 9 17:35), so the campaign was complete and stable when it was taken
and nothing has touched it since. **A twelve-row sha256 spot-check — first, second,
middle and last job of each tune — matched the files on disk in all twelve cases.**

> **Not done, and stated rather than implied:** the manifest's 3000 checksums were
> **not** exhaustively recomputed. They were written and verified at promotion
> time, each with a `raw_validation` receipt, and the spot-check above confirms
> the recorded values still describe the bytes. A full re-hash is ~270 GB of NFS
> reads; `tools/build_canonical_manifest.py --rehash` is the switch if a future
> reviewer wants it.

## 3. WHAT THIS AUTHORIZATION DOES NOT COVER

- **The systematics campaigns.** `HF_SYS_*` completed 2100/2100 on 2026-08-17 but
  are a separate dataset and are **not** authorized by this document. Their
  harvest is a separate session.
- **Figure promotion.** Eligibility is necessary, not sufficient. Every figure
  still owes its own house contract — recomputation from committed artifacts,
  determinism, recorded command and ROOT version, and a visual review.
- **The manuscript's prose.** `docs/FIGURE_INVENTORY.md` §4 and
  `plotting/PAPER_FIGURE_PROVENANCE.md` carry open owner decisions and stale
  captions that this authorization does not touch.

## 4. A NOTE ON THE DATASET KEY

The selector key stays **`hf_run3_v1_candidate`** even though the status is now
`canonical`. The key is exported as `HADRONIZATION_DATASET_ID` and may already
appear in the provenance of artifacts produced under it; renaming it would
orphan those records. **The key is an identifier; `status` carries the claim.**
