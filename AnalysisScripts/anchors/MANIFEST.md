# Anchors — the raw material behind committed results

**Purpose: every published number's provenance chain must be readable from this
repository alone.** These are inputs and run outputs that previously existed only
in Nikhef scratch, where a cleared filesystem would have broken the chain.

**Copied verbatim, never regenerated.** Each subdirectory says what can be
verified and what cannot.

| directory | what it anchors | provenance |
|---|---|---|
| `extraction_dual/` | every number in `EXTRACTION_CONVENTIONS`, `SECOND_BRANCH_WEIGHT`, `MAP_V2_RESULT`, `B_BARYON_ADVISORY_DIAGNOSTIC`, `SIGMA_B_ORDERING_AND_ADJUDICATION` | **incomplete — tune and input count unrecorded.** See its own MANIFEST |
| `f4_probe/` | `decay_parent_map_v1.json`, `v1_1`, `v2` | **complete and verified** — see §1 |
| `m7b_blocks/` | `docs/M7_BEAUTY_UNRESOLVED_SYSTEMATIC.md` | **complete** — see §2 |
| `m7_blocks/` | the **charm** M7 table in `docs/M7_UNRESOLVED_SYSTEMATIC.md` | **complete and verified** — see §2b |
| `closure_v3_verdicts/` | the two `CANONICAL_PAIR_BLOCK_CLOSURE_PASS` verdicts gating `docs/THREE_TUNE_CENTRAL_TABLE.md` | **complete** — added 2026-08-17, see its own MANIFEST |
| `e5fix_drivers/` | how the three-tune extraction was invoked; the extractor itself is tracked | **complete** — added 2026-08-17, see its own MANIFEST |
| `b4_multiplicity_mb/` | the min-bias `N_ch` dumps **and**, since 2026-08-17, the calibration macro that consumes them | see its own MANIFEST |

---

## 1. `f4_probe/` — the decay-map raw material

| file | what it is |
|---|---|
| `f4_probe_v1.out` | the original probe: 202 species, **dominant channel only** |
| `f4b_probe.out` | the extended probe: **5,576 `F4_CHANNEL` lines**, every channel |
| `pdgs.txt` | the 202 species requested |
| `build_run.log` | build + run manifest of the extended probe, with shas |

**Both maps rebuild from these files, and this is verified rather than
asserted:**

```bash
tools/build_decay_parent_map.py AnalysisScripts/anchors/f4_probe/f4_probe_v1.out \
  --ordinals AnalysisScripts/species_ordinals_v2.json --out /tmp/v11.json
# map_sha256 == dd502a10c5932fff… , the committed decay_parent_map_v1_1.json
```

**Checked 2026-08-11: the rebuild reproduces `dd502a10c5932fff…` exactly**, with
`I1=PASS I2=PASS` and the pre-registered diff counts
(`artifact_rows_changed=101 table_affecting_rows=60`).

`f4b_probe.out` additionally satisfies **C7**: its `F4_SPECIES` and `F4_GATE`
lines are **byte-identical** to `f4_probe_v1.out`'s, which is what proves the
probe was *extended* rather than changed
(`docs/MAP_V2_PREREGISTRATION.md` §3).

> **Consequence for a reviewer: the decay maps are not opaque artifacts.** Both
> can be regenerated from committed inputs with committed tools, and the
> conjugation fix can be re-derived and re-checked independently.

## 2. `m7b_blocks/` — the beauty-M7 block logs

Ten logs, one per canonical block, from Condor cluster `5425788`. Each carries
its own header manifest: host, start/finish, block, sector, checkout commit,
**parametrised macro sha256**, **scratch counts macro sha256**, frozen charm
macro sha256, block manifest sha256, and the production root.

They are the input to:

```bash
extraction/aggregate_m7.py AnalysisScripts/anchors/m7b_blocks/*.log
```

which fail-closes below ten blocks and on mixed sectors, and reproduces the
table in `docs/M7_BEAUTY_UNRESOLVED_SYSTEMATIC.md`.

**The 30 `XCHECK_OK` lines are in these logs** — the per-block cross-check
between the counting macro and the percentage macro. A reviewer can confirm the
provenance claims without access to Nikhef.

---

## 2b. `m7_blocks/` — the CHARM-M7 block logs

Ten logs from `/data/alice/ipardoza/m7_runs/block_01..10/`, fetched
2026-08-12. The charm counterpart of §2: until now the **beauty** table's raw
material was anchored while the **charm** table — the one the beauty work was
validated against — rested on scratch only.

```bash
extraction/aggregate_m7.py AnalysisScripts/anchors/m7_blocks/*.log
```

**Verified, not asserted.** The committed logs reproduce the published charm
table exactly, which is P2 of `docs/M7_BEAUTY_PREREGISTRATION.md`:

| tune | unres rate % | relative shift % |
|---|---|---|
| MONASH | **0.0847** ± 0.0003 | **0.0451** ± 0.0008 |
| JUNCTIONS | **1.1530** ± 0.0009 | **0.5497** ± 0.0019 |
| CLOSEPACKING | **1.1355** ± 0.0008 | **0.5125** ± 0.0024 |

| file | sha256 |
|---|---|
| `m7_block_01.log` | `a457c2b7e4ce36ba3a5f6a2eb53928f1626e828c20a02fe1eb58357d2f44ada9` |
| `m7_block_02.log` | `5732372cbcef4316d197f7401cb82ecc72e0303505e42f65f5d2ec351c15dc0c` |
| `m7_block_03.log` | `22b7e018dc45bc56c63cbd86ad405e9c6d3cd940e4e3df814ebf0cbd9fc29555` |
| `m7_block_04.log` | `fd51911bfd602feb084acd75b6e2cb3f34ddf6de4a3502078d0d8dafb72e0e4c` |
| `m7_block_05.log` | `fa5a471f39cba439400741e1ad1cd1222bfd9eeae0791e7c0d925893d76b9314` |
| `m7_block_06.log` | `a8b3f08879e2abcd011a186b7486988a78c4142e278870ef0d185d6e5935d8e2` |
| `m7_block_07.log` | `86eefbced0a685bdd6a1197a502140bcf40353d58905a031f7dbdb0bb965b46f` |
| `m7_block_08.log` | `499dbe9f6d4a8becb5e09d256f9ff8447c59520a29dd33c83ed52d227cd65e9b` |
| `m7_block_09.log` | `d66c9b28d08f580560241acac24570d0e5c5c3b860495118d2acc6355ba99ed7` |
| `m7_block_10.log` | `339ef575a5b21025d0b3a06b98b8fc2ee2f3fb37a661f9debc6f2f4452afc647` |

**Regeneration recipe** (the `GOLDEN_OUTPUTS.md` form): run the command above
against these ten files at these shas, with `extraction/aggregate_m7.py` at the
committed revision. It fail-closes below ten blocks and on mixed sectors.

---

## 3. WHAT IS STILL NOT ANCHORED

| gap | status |
|---|---|
| **the merge log and run manifest** | the merge is **still running**; commit at completion. `docs/MERGE_V3_BAND_VALIDATION.md` is the timing record because **the log carries no timestamps** — every timing there is reconstructed from filesystem mtimes and cannot be re-derived once scratch is cleared |
| **`extraction_dual` provenance** | **unrecoverable.** Tune and input count are inherited from prose that disagrees with itself. Superseded by the post-merge extraction, which must write an invocation manifest |
| ~~**Task 2 outputs** (`sigmab_runs/`)~~ | ✅ **ANCHORED** — all ten block logs are in `sigmab_raw/` |
| ~~**M7 charm block logs**~~ | ✅ **ANCHORED 2026-08-12** (`b74e588`) — `m7_blocks/`, ten logs, verified against the published charm table; digests G36–G45 in `docs/GOLDEN_OUTPUTS.md` |
