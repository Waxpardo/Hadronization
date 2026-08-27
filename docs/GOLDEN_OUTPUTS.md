# Golden outputs — the behaviour-freeze contract

**Written 2026-08-12 on branch `restructure-prep`, for the external review and
as the acceptance gate for any repository restructure.** Nothing in this
document changes any artifact. It states what must still be true afterwards.

**The claim this document makes on the project's behalf:**

> Every published number in this repository is either (a) regenerable from
> committed inputs with committed tools, or (b) explicitly recorded as not
> regenerable, with the reason. There is no third category.

Category (b) is real and is §5. Listing it is the point — a freeze contract
that quietly omitted the unreproducible entries would be worth less than none.

---

## 0. HOW TO READ AN ENTRY

Every entry carries a **digest** and a **recipe**. A digest alone says "this
file has not changed"; it cannot say the file is still *derivable*. A restructure
can leave every byte in place and still break the derivation — by moving the
input the recipe reads. **The pair is the contract.**

### 0.1 Three kinds of digest, which are not interchangeable

| kind | what it covers | where it appears |
|---|---|---|
| **file sha256** | the bytes on disk, including the `map_sha256` field itself | computed here, 2026-08-12 |
| **`map_sha256`** (internal) | the JSON body *excluding* the `map_sha256` key, `sort_keys=True, indent=2` | inside the decay maps; what the builders print and what the record quotes |
| **content invariant** | a number or count that must reproduce, not a file | e.g. closure 2100/1500, the anchor totals |

> **The record quotes `map_sha256`; this document quotes both.** The truncated
> `dd502a10…` in `EXTRACTION_CONVENTIONS.md`, the superseded private convention-table record, and
> `evidence/MANIFEST.md` is the **internal** digest, **not** the
> file's sha256. They differ, they are both correct, and confusing them is a
> live trap: a reviewer who runs `sha256sum decay_parent_map_v1_1.json` and gets
> `ed148156…` has **not** found a discrepancy.

### 0.2 Verification vocabulary — used strictly

| tag | meaning |
|---|---|
| **VERIFIED-BY-RECORD** | someone ran the recipe and the record says the digest reproduced; the citation is given |
| **DETERMINISTIC-BY-CONSTRUCTION** | the generator provably has no nondeterministic input (no timestamp, host, ordering or PRNG); byte-identity follows, but **nobody has re-run it since** |
| **SELF-CHECKING** | the tool ships a `--check` mode that *is* the verification, and it runs in `make check` |
| **UNVERIFIED** | recipe stated, never scored |
| **UNKNOWN** | classification needs knowledge this session does not have; the question is stated |

**No entry in this document is tagged VERIFIED by this session.** This session
ran no pipelines and no verification jobs, by instruction. Every VERIFIED-BY-RECORD
tag cites someone else's run.

### 0.3 ROOT-generated figures are contracted differently, and deliberately so

**Added 2026-08-13, when the first v3 figure was produced.**

The figures written by `plotting/run_paper_plots.sh` — the `TCanvas` PDF, PNG
and `_MACRO.C` triplets — are **NOT contracted on a byte digest.** They are
contracted on:

> **pinned inputs + pinned ROOT + the recorded command.**

Accepted final scientific bytes have one canonical destination, `results/figures/main/`.
Dated products under `results/validation/plotting/` remain validation evidence.
They require exact dataset and configuration identity, `hTrKinematics` trigger normalization, ten-block uncertainty coverage, a final receipt, and visual review before acceptance.
Every tune comparison is bundle-to-bundle across the complete MONASH, JUNCTIONS, and CLOSEPACKING cards.

The inputs' shas, the ROOT version and build, the host, and the exact invocation
are recorded. The receipt written beside them
(`multiplicity_boundary_receipt_v1.json`) carries its own `payload_sha256` and
**is** digest-contracted, because it is JSON the stack writes itself, and the
stack already refuses to overwrite a differing one.

The reason is not laziness about digests. A ROOT canvas embeds a creation
timestamp and a ROOT version string, and a PDF stream is sensitive to the
font and graphics backend, so **byte-identity across two runs is not a property
this project can promise.** A contract nobody can keep is worse than an honest
weaker one, because the first unexplained failure teaches reviewers to ignore
it. What the recipe does establish is that the same inputs under the same ROOT
reproduce the same **numbers** — and those are pinned, by the receipt and by the
`MULTIPLICITY_BOUNDARY` lines.

> **Do not read a matching figure digest as a stronger claim than this, and do
> not read a differing one as a defect.** The numbers are the contract; the
> rendering is not.

---

## 1. THE GATE

**Set by the owner, 2026-08-12, and quoted rather than extended:**

> *Acceptance gate: suite green + derived artifacts regenerate to recorded
> digests. NOTHING ELSE. No additional verification may be invented for this.*

So, precisely two conditions:

| # | gate condition |
|---|---|
| **G-1** | **`make check` green**, at its pre-restructure count — **30/30** as of `9426f38`, **37/37** as of the post-review fixes (2026-08-13; seven tests added, none removed), with **no test skipped or deleted** to achieve it |
| **G-2** | **every file sha256 in §2 unchanged**, and every **derived** artifact regenerates to it — under whatever path the new layout gives the file |

**Everything else in this document is method, not a further condition.** In
particular:

- `make check` already runs `doctor`, `cards`, `cards-current`, `registry` and
  the suite, so the SELF-CHECKING generators are inside G-1 — they are not an
  extra gate;
- **G-1 has a trap of its own.** Without ROOT the suite reports a *smaller
  denominator* and passes (`tools/run_tests.sh:13-15`). A green run must print
  `ROOT: /path/to/root`. Checking that is part of reading G-1 correctly, not an
  added requirement;
- **`rc=0` is not evidence** — the recipes in §4 each name the output line that
  constitutes their positive check. That is how G-2 is read, not a third gate.

> **G-2 is necessary and not sufficient on its own**, which is why G-1 sits
> beside it: `git mv` preserves every byte and can still break every recipe that
> names a directory. The suite is what notices.

### 1.1 How G-2 is discharged for the decay maps — owner ruling, 2026-08-12

> *R5/R6: run during the acceptance gate — they are the gate for the maps, not
> an addition to it.*

**R5 and R6 (§4) rebuild v1.1 and v2 from the committed probe anchors with the
committed builders.** They are pure Python, take seconds, and need neither ROOT
nor PYTHIA. Running them at the gate is what separates *"the file still has the
right bytes"* from *"the file is still derivable from its inputs"* — and only
the second is a freeze contract. **On the maps, R5/R6 are how G-2 is read.**

Their passing lines promote **G6 and G7** from
**DETERMINISTIC-BY-CONSTRUCTION** to measured.

### 1.2 The path-coupling surface — measured, 2026-08-12

The recipes are not path-agnostic. Measured on `9426f38`:

| measure | count |
|---|---|
| distinct quoted repo-relative paths in `tools/`, `tests/`, root `*.sh`, `Makefile` | **63** |
| total occurrences of those | **138** |
| further files carrying unquoted `Dir/...` forms (`.C`, `.h`, `.cpp`, `.sh`) | **~30** |

Nearly every Python tool resolves as `REPO = Path(__file__).resolve().parents[1]`
then a **hardcoded subdirectory string**. Moving the generated-artifact
directory breaks `generate_species_ordinals_header.py`, `apply_decay_map.py`,
`second_branch_weight.py`, `extract_species_decomposition.py`,
`decompose_with_block_sems.py` and `generate_registry_artifacts.py` — silently
in some, fail-closed in others, and **which is which has not been established.**

> **This was the cost estimate for the restructure, and it belonged in the plan,
> not in a surprise.** See the private restructure plan, Section 4.2.

**The move happened on 2026-08-27 under ruling R19.** The seven generated
artifacts are in `contracts/`; the anchor store is `evidence/`. All six tools
above carry the new strings and the suite stays at 86/86.

---

## 2. THE FROZEN ARTIFACTS

All sha256 values computed **2026-08-12 on `9426f38`**, tree clean.

### 2.1 Species axis — the spine everything else pins to

| id | artifact | file sha256 |
|---|---|---|
| **G1** | `contracts/species_ordinals_v2.json` | `ccec0dbc70f6452d1f4a5c22a37e76ce55b357046094da207469f08534d0e4ce` |
| **G2** | `contracts/GeneratedSpeciesOrdinals.h` | `9f7fe1caab28552af2cb207a3bc38ac5dd3fbc61f77c60a3b652285b3efe8468` |
| **G3** | `contracts/GeneratedPairRegistry.h` | `7d5e7bfdab80163f20f407fccfaad7543099d93a07609614b09eb6d626e985ff` |
| **G4** | `contracts/GeneratedPairObjectContract.h` | `f2a8c8ebb2cbbac9bd269b161cdcf05a13ae0f83679e81ee133647f80310ea10` |

> **G2 changed on 2026-08-27, comment only.** The generated header quotes its
> own source path on line 6, so ruling R19's rename rewrote that comment and the
> file digest with it (`ca33c2ee…` before, `9f7fe1ca…` after). The 202 species,
> the table digest and every ordinal are unchanged; `make registry` and
> `tools/generate_species_ordinals_header.py --check` both report current.
> G1, G3 and G4 keep their 2026-08-12 digests.

**Content invariants:** 202 species; `table_digest_fnv1a64 = 646f310f78126267`;
`audit_rows_total = 219`; `hidden_heavy_excluded = 17`;
`unmapped_policy = fail_closed_no_overflow_bin`.

**G1 is the load-bearing digest of the whole pack.** `646f310f78126267` is
asserted by all three decay maps, by the v3 closure's `species_ordinal_digest`
invariant, and in-file on every merged output. If G1 moves, everything below is
void.

- **G2/G3/G4 recipe (SELF-CHECKING):** `make registry` and
  `python3 tools/generate_species_ordinals_header.py --check`,
  `python3 tools/generate_pair_object_contract.py --check`.
  Positive check: `--check` exits non-zero and prints `*_STALE` on any drift.
- **G1 recipe:** `tools/GenerateSpeciesOrdinals.C` over a
  `heavy_stability_audit` tree. **UNVERIFIED for regeneration** — the input is
  one JUNCTIONS raw file on Nikhef (`HF_PT2_INT/raw/JUNCTIONS/hf_JUNCTIONS_job001.root`,
  sha256 `49657c2c9a25e319513be5cda659a4d5e53bb3944f33bef51702b5660aaa3651`,
  96,578,417 bytes, per `docs/SPECIES_AXIS_VALIDATION.md`). **The fixture is not
  in the repository**; the digest is. See §5.

### 2.2 Decay-parent maps

| id | artifact | file sha256 | internal `map_sha256` |
|---|---|---|---|
| **G5** | historical v1 decay map (**HISTORY — defective; excluded from export**) | `a67e8ae5f853689c010e991859242a77b913787dd30ab3d4c1b68bc05758c00c` | `e343fd8872f9742b84ae3dce5085071c59eb289c1841faef3fff754effadcccb` |
| **G6** | `decay_parent_map_v1_1.json` | `ed1481569dcf94e17a154e00a5eb5c829299d3c1502e04dd036ce5fcaccfe688` | `dd502a10c5932fffa2bb3121296a40532224b4d6910330ea5e044e045089c43f` |
| **G7** | `decay_parent_map_v2.json` (**CURRENT**) | `58081aa2f87cb67141259f2b74a5057777a6c8eaa5049446fd3f47b13a1c84da` | `c9593c9c0a7c4ec2ed6b53462255d4f04dcb4a5f5bd029217f479e5eecbb85fb` |

**G5 is frozen as history and must not be deleted.** It is the artifact
`docs/MAP_V1_CONJUGATION_BUG.md` and private error-ledger entry **E1** are about; deleting
it would delete the evidence for the project's most instructive published error.
It is also, today, a live hazard — see §6, finding F1.

**Recipes** (all local, pure Python, no ROOT, no PYTHIA):

```bash
# G6 — v1.1, the conjugation fix
tools/build_decay_parent_map.py evidence/f4_probe/f4_probe_v1.out \
  --ordinals contracts/species_ordinals_v2.json --out /tmp/v11.json

# G7 — v2, the species-level splits; built on v1.1, never on v1
tools/build_decay_parent_map_v2.py evidence/f4_probe/f4b_probe.out \
  --ordinals contracts/species_ordinals_v2.json \
  --v1 contracts/decay_parent_map_v1_1.json \
  --weights evidence/extraction_dual/per_species.csv \
  --out /tmp/v2.json
```

**Positive checks, not `rc=0`:** `DECAY_PARENT_MAP … map_sha256=dd502a10c5932fff`
plus `CONJUGATION artifact_rows_changed=101 table_affecting_rows=60
involution_pairs=… I1=PASS I2=PASS`; and `MAP_V2_BUILT species=202 split=2
threshold=0.1% sha256=c9593c9c0a7c4ec2` with exactly two `SPLIT` lines
(`D*+ → D⁰ 0.6770 / D⁺ 0.3230`, `D*- → D̄⁰ 0.6770 / D⁻ 0.3230`).

| | |
|---|---|
| G6 status | **VERIFIED-BY-RECORD**, 2026-08-11 — `evidence/MANIFEST.md` §1: *"the rebuild reproduces `dd502a10c5932fff…` exactly"* |
| G7 status | **DETERMINISTIC-BY-CONSTRUCTION** for file bytes |

**Why file-level byte identity is claimable and not merely hoped for:** both
builders end
`args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")`
(`build_decay_parent_map.py:267`, `build_decay_parent_map_v2.py:220`). The
payload carries **no timestamp, no hostname, no path, no PRNG draw** — verified
by reading the payload construction in both. Key order is forced by
`sort_keys`. **The one residual dependency is CPython's float repr**, stable
since 3.1; a non-CPython interpreter is out of contract.

**G7's fourth input is the quarantined anchor.** `--weights` takes
`extraction_dual/per_species.csv`, which is quarantined for charge-resolved use
(§2.4). **This is correct and must not be "fixed" during a restructure:** the
weights select *which* species clear the 0.1 % split threshold, and that
selection is an aggregate question, on which the anchor is sound. Rebuilding G7
against different weights would produce a different, unpinned artifact.

### 2.3 The probe anchors — the maps' raw material

| id | artifact | file sha256 |
|---|---|---|
| **G8** | `anchors/f4_probe/f4_probe_v1.out` | `f2d30a345bd8bed278062296d007f2dc5a4f101cf54f54b719e8caccd7d7cd76` |
| **G9** | `anchors/f4_probe/f4b_probe.out` (5,576 `F4_CHANNEL` lines) | `1525a0e5985b6969ed2cdda616560b8d5222ac338b089fe2343026e806adeb1c` |
| **G10** | `anchors/f4_probe/pdgs.txt` (202 species requested) | `42a88913b4087691c9797bc3baf4212515020ab293ded4dbd3db7d45a4ee2d34` |

**These are the deepest committed inputs in the decay-map chain and they
terminate it.** Regenerating them needs `tools/f4_probe.cc` compiled against the
pinned PYTHIA 8.317 install, which is a personal directory (§5). **A reviewer
does not need to**: the maps rebuild from G8/G9 with committed tools.

**Content invariant, C7:** G9's `F4_SPECIES` and `F4_GATE` lines are
**byte-identical** to G8's — the proof that the probe was *extended*, not
changed. Any restructure that rewrites line endings on these files breaks C7.
**Treat `anchors/**` as binary.**

### 2.4 Extraction anchors

| id | artifact | file sha256 | rows | sum |
|---|---|---|---|---|
| **G11** | `anchors/extraction_dual/per_species.csv` | `6137f6bc1f661ffdf26167a440091229f1466c87e2a8e4b50d096d66c3f45ac1` | 91 | **129,883,844** |
| **G12** | `anchors/extraction_dual/per_category.csv` | `fe8d7dc577c56fd3e4ef9d090ee37b120b578d8fb2e08cdf8a5b08cd2f48db12` | 6 | **129,883,844** |
| **G13** | `anchors/extraction_dual/per_observable.csv` (**SUPERSEDED**) | `46bca45240ffb49662de3b9ab49be157ce2f0a0b08043e67bbe6f70f1d3f6303` | 30 | **129,883,844** |
| **G14** | `anchors/merged_monash_replicated/per_species.csv` (**REPLICATED — see E5**) | `74ecfb6ee659e737caa45822592000f143c4a9e0f0b6365f12f273d33898ce76` | — | **1,298,655,240** |
| **G15** | `anchors/merged_monash_replicated/per_category.csv` (**REPLICATED — see E5**) | `f162686c24b488c6cbd2c37085899be5df139b2e678c8109faeb8c263076e024` | — | — |
| **G14d** | `anchors/merged_monash_replicated/per_species_deduplicated.csv` | regenerable, see R12 | 95 | **53,662,414 … 53,662,828** |
| **G15d** | `anchors/merged_monash_replicated/per_category_deduplicated.csv` | regenerable, see R12 | 4 | — |

> **G14/G15 are the REPLICATED product and are retained as the historical
> record, not as the published decomposition.** Private error-ledger entry **E5**:
> the trigger-owned closure was summed once per pair file, counting each charm
> trigger 24× and each beauty trigger 26×. Their digests still match their files
> — **the digests were never the problem**; a digest certifies that a file has
> not changed, not that the number in it is right.
>
> **G14d/G15d are the corrected reconstruction**, produced by
> `tools/reconstruct_deduplicated_decomposition.py` (**R12**), which verifies the
> sector-divisibility fingerprint before inverting and refuses to run on a table
> that does not carry the defect. They are **not** the output of a live
> re-extraction; that is still outstanding.

**Verified aggregates (the review-facing claim):** G11/G12/G13 all sum to
**129,883,844**, mutually consistent. G14's total is **1,298,655,240** from
1000 merged inputs. G11 and G12 are **map-independent** — keyed by species
ordinal and by structural category, neither of which consults a decay map — so
the E1 conjugation defect never touched them. **G13 is map-dependent and was
computed under the defective v1**, carrying `D⁰ = 45.9475 %` and the 4.49×
charge asymmetry. It is committed as the historical record and **is not a
current result.**

**G11–G13 are NOT regenerable.** Their provenance is unrecoverable: tune, input
count, reader commit and run date were never recorded, and the two prose claims
that survive disagree with each other (`EXTRACTION_CONVENTIONS.md` §6 says
"one directory, 100 inputs"; `HANDOFF_v40` §6 says "four directories"). See §5.
They remain frozen because they are (i) the historical cross-check for totals
and species shares, and (ii) the **regression fixture** for
`extraction/compare_subset_parent.py`.

**G14/G15 recipe** — the full chain, and it spans three stages:

```
merge_root_files.sh  →  merged MONASH central (1000 inputs, 300 pair files)
        ↓
extraction/extract_species_decomposition.py <central_dir> --out <dir> \
    --artifact contracts/species_ordinals_v2.json \
    --decay-map contracts/decay_parent_map_v1_1.json
        ↓
per_species.csv / per_category.csv  (+ per_observable.csv, map-dependent)
```

Positive checks: `SELF_CHECK AGREE worst_relative=<1e-9>` and, when a decay map
is given, `INVARIANCE CONSERVED`. **Status: UNVERIFIED for regeneration** — the
merged central lives on Nikhef, not in the repo. What *is* repo-local is the
committed output G14, and it is the parent fixture for `compare_subset_parent`.

> **`--decay-map` MUST be passed explicitly. Its default is the defective v1.**
> See §6, finding F1. This is a live hazard, not a historical one.

### 2.5 The convention tables

**Current in the superseded private convention-table record, from merged weights**, computed
from G14, total 1,298,655,240, MONASH only:

| quantity | value |
|---|---|
| structural `kCentralGround` | **52.3388 %** |
| structural `kExcludedVector` | **46.6510 %** |
| structural `kExcludedExcited` | **1.0102 %** |
| map-v2 D⁰ | **25.2435 %** |
| map-v2 D̄⁰ | **25.1707 %** |
| map-v2 D⁺ | **13.1408 %** |
| map-v2 D⁻ | **13.1129 %** |
| map-v1.1 D⁰ | **28.1301 %** |
| map-v1.1 D̄⁰ | **28.0467 %** |

**History, from the anchor — `docs/EXTRACTION_CONVENTIONS.md`** (supersession
banner carried; tables stay as history): v1.1 D⁰ 28.1326 %, D̄⁰ 28.0536 %;
**v1 D⁰ 45.9475 % — superseded, do not quote.**

**Recipe:** `extraction/apply_decay_map.py --map <map> --weights <per_species.csv>`.
The tool ships a particle/antiparticle ratio report, **advisory at |ratio−1| > 10 %**
and deliberately not a gate — a hard gate at 1.00 would refuse real physics
(Λ_c sits at 1.026). **Status: DETERMINISTIC-BY-CONSTRUCTION from G14 + G6/G7.**

**The freeze claim that matters here:** every merged-vs-anchor delta is
**≤ 0.017 pp**. That is the expected result and it is *also* the fact that hid
the E4 anchor defect for a generation. **Do not read "nothing moved" as
"nothing needed doing".**

### 2.6 The second-branch number

| basis | anchor | merged | quote |
|---|---|---|---|
| (A) single-hop | 12.8400 % | **12.8341 %** | — |
| (C) chained | 12.8451 % | **12.8396 %** | history |
| (B) exposed | 35.7910 % | 35.7708 % | — |
| **species-level, pre-split** | — | **5.7737 %** | — |
| **species-level, post-split (v2)** | — | **0.0018 %** | ✅ **THE NUMBER** |

> **Quote 0.0018 %.** The 12.84 % survives as *history* — an honest upper bound
> on a question the v1 artifact could not answer. **C6 (residual < 1 %) passes
> by a factor of ~550.** Residual is B_c± alone, 0.0009 % each.

> **⚠ CORRECTED 2026-08-13 (review finding A8): the recipe below does NOT
> produce "THE NUMBER".** `second_branch_weight.py` defaults to the v1.1
> dominant-chain map and contains **no post-split v2 residual calculation** —
> it has no `--mode`, no split awareness, and its only summary line is
> `at_risk_pct`. Run as written it prints **12.8396 %**, the **(C) chained**
> history row, not the **0.0018 %** declared as THE NUMBER.
>
> **So R8 is the recipe for the history row, and is labelled as such.** The
> 0.0018 % post-split figure has **no committed derivation** — it is stated in
> this table and in `docs/SECOND_BRANCH_WEIGHT.md` but no tool here computes
> it. That places it in §5 (recorded as not regenerable), not in the
> regenerable category. It is not re-derived here rather than being guessed at:
> reverse-engineering a published number from its rounded value is how a wrong
> number becomes a certified one.

> ## ✅ RESOLVED 2026-08-13 — the derivation is implemented, and the claim SURVIVES
>
> **The number was not withdrawn, because it turned out to be derivable.**
> `second_branch_weight.py` gains `--v2-map`, which computes the species-level
> residual from the weights and the v2 map's committed `species_level_branches`:
> a species' exposed fraction is `1 − max(branch fraction)`, summed over species
> that were **not** split. **New recipe R8b.**
>
> **It was confirmed, not fitted.** The definition reproduces *three* published
> quantities at once, none of them targeted: pre-split **5.7737 %** (doc:
> 5.7737), post-split **0.0018 %** (doc: 0.0018), and the breakdown **B_c⁺
> 0.000903 % / B_c⁻ 0.000896 %** (doc: "B_c± alone, 0.0009 % each"). One
> agreement could be a coincidence of rounding; three simultaneous ones, including
> a per-species split never quoted as a target, are a derivation. **The rounded
> value was never used as an input.**
>
> **⚠ AND THE NUMBER MOVES UNDER E5.** The residual is carried entirely by
> **B_c±, a MIXED beauty-charm species**, so its share of the total is exactly
> the kind of cross-sector quantity the replication biased. Recomputed on the
> **re-extracted, deduplicated** MONASH central:
>
> | basis | post-split residual | B_c⁻ | B_c⁺ |
> |---|---|---|---|
> | replicated (as published) | **0.0018 %** | 0.000900 % | 0.000879 % |
> | **re-extracted (E5-corrected)** | **0.0017 %** | 0.000838 % | 0.000819 % |
>
> **Quote 0.0017 %** for anything drawn from the corrected extraction. C6
> (residual < 1 %) passes by a factor of ~590. The (C) chained history row moves
> the same way, 12.8396 % → **12.9462 %**, and remains history either way.

**Recipe:** `extraction/second_branch_weight.py --per-species <per_species.csv>`
(defaults: `--decay-map decay_parent_map_v1_1.json`, `--artifact
species_ordinals_v2.json`). Fails closed unless it reproduces the expected
table first. **Status: VERIFIED-BY-RECORD** for the anchor basis
(`anchors/extraction_dual/MANIFEST.md` §1); **DETERMINISTIC-BY-CONSTRUCTION**
for the merged basis.

### 2.7 M7 — charm

> **SCOPE (relabelled 2026-08-13, finding A2): inclusive-level diagnostic.**
> The macro applies no production selection — its only cut is
> `heavyIsFinal && q_sector != 0`. These digests and numbers are sound as an
> inclusive unresolved-origin rate and inclusive baryon-fraction shift. They
> are **not** a bound on the OS−SS pair observable's systematic.

`docs/M7_UNRESOLVED_SYSTEMATIC.md`. 3000 raw files, ~300 M events, cluster
`5402022`, ten jobs.

| tune | unresolved rate % | baryon % measured | baryon % inclusive | **relative shift %** |
|---|---|---|---|---|
| MONASH | 0.0847 ± 0.0003 | 4.6547 ± 0.0013 | 4.6568 ± 0.0013 | **0.0451 ± 0.0008** |
| JUNCTIONS | 1.1530 ± 0.0009 | 17.8488 ± 0.0037 | 17.9469 ± 0.0037 | **0.5497 ± 0.0019** |
| CLOSEPACKING | 1.1355 ± 0.0008 | 17.2888 ± 0.0038 | 17.3774 ± 0.0036 | **0.5125 ± 0.0024** |

Integer counts: unresolved_n 168,003 / 2,317,799 / 2,271,517; resolved_n
198,163,563 / 198,706,525 / 197,779,600; enrichment **1.53× / 1.48× / 1.45×**.

> ### ✅ N7 CLOSED — the charm block logs are anchored, `b74e588`, 2026-08-12
>
> *"Anchor the charm-M7 block logs, verified against the published charm table."*
> **The pack no longer has an unanchored input.**

| id | artifact | file sha256 |
|---|---|---|
| **G36** | `anchors/m7_blocks/m7_block_01.log` | `a457c2b7e4ce36ba3a5f6a2eb53928f1626e828c20a02fe1eb58357d2f44ada9` |
| **G37** | `…m7_block_02.log` | `5732372cbcef4316d197f7401cb82ecc72e0303505e42f65f5d2ec351c15dc0c` |
| **G38** | `…m7_block_03.log` | `22b7e018dc45bc56c63cbd86ad405e9c6d3cd940e4e3df814ebf0cbd9fc29555` |
| **G39** | `…m7_block_04.log` | `fd51911bfd602feb084acd75b6e2cb3f34ddf6de4a3502078d0d8dafb72e0e4c` |
| **G40** | `…m7_block_05.log` | `fa5a471f39cba439400741e1ad1cd1222bfd9eeae0791e7c0d925893d76b9314` |
| **G41** | `…m7_block_06.log` | `a8b3f08879e2abcd011a186b7486988a78c4142e278870ef0d185d6e5935d8e2` |
| **G42** | `…m7_block_07.log` | `86eefbced0a685bdd6a1197a502140bcf40353d58905a031f7dbdb0bb965b46f` |
| **G43** | `…m7_block_08.log` | `499dbe9f6d4a8becb5e09d256f9ff8447c59520a29dd33c83ed52d227cd65e9b` |
| **G44** | `…m7_block_09.log` | `d66c9b28d08f580560241acac24570d0e5c5c3b860495118d2acc6355ba99ed7` |
| **G45** | `…m7_block_10.log` | `339ef575a5b21025d0b3a06b98b8fc2ee2f3fb37a661f9debc6f2f4452afc647` |

**Recipe:** `extraction/aggregate_m7.py evidence/m7_blocks/*.log` —
same tool as R9, fail-closed below ten blocks and on mixed sectors.
**Status: VERIFIED-BY-RECORD** — the commit message states the logs were
verified against the published charm table.

**Consequence for §2.8:** the beauty anchors' P2 charm-regression is no longer
the *only* repo-local evidence for this table. **Both halves of M7 now stand on
their own committed inputs.**

### 2.8 M7 — beauty

> **SCOPE: inclusive-level diagnostic, exactly as §2.7.** Not a bound on the
> pair observable.

`docs/M7_BEAUTY_UNRESOLVED_SYSTEMATIC.md`. Cluster `5425788`, 10 jobs, all `rc=0`.

| tune | unresolved rate % | baryon % measured | baryon % inclusive | **relative shift %** |
|---|---|---|---|---|
| MONASH | 0.0115 ± 0.0003 | 4.8715 ± 0.0037 | 4.8721 ± 0.0037 | **0.0141 ± 0.0011** |
| JUNCTIONS | 0.1023 ± 0.0011 | 32.0174 ± 0.0115 | 32.0218 ± 0.0115 | **0.0140 ± 0.0008** |
| CLOSEPACKING | 0.0983 ± 0.0011 | 32.3720 ± 0.0068 | 32.3766 ± 0.0068 | **0.0143 ± 0.0007** |

Integer counts: unresolved_n 3,170 / 28,315 / 27,184; resolved_n 27,645,508 /
27,659,509 / 27,631,664; enrichment **2.23× / 1.14× / 1.15×**.

| id | artifact | file sha256 |
|---|---|---|
| **G16** | `anchors/m7b_blocks/m7b_block_01.log` | `5a75aa882853b9368ce065f1ce5b32a32eaff61180c8dbe65a2a006712f487e9` |
| **G17** | `…block_02.log` | `740c8f1ab51386c6907f8e6e15e127b4c6bab2be0ab077b0441fb9d1431ace74` |
| **G18** | `…block_03.log` | `5544e62f1f850acf382b7b1e1c6fb833972be9c268b87bf0cfa1e792fc94e50e` |
| **G19** | `…block_04.log` | `5f74c0d7ec2f48f21a7cb3e60fcc56179319ae4332b1a217518f63128cae1667` |
| **G20** | `…block_05.log` | `90413b23b28f1b03b56aa92a22069281f88fefa0602ace084a734fa1064012ba` |
| **G21** | `…block_06.log` | `b017da833e08f5b2abd6971450840bc039b92386ebe708fda5802b42730d3380` |
| **G22** | `…block_07.log` | `83f21fb4be84b1f6db6556f7c7f90c5099224dd9e4bccf08920f028004054cdb` |
| **G23** | `…block_08.log` | `14e9bc80f220282a054623fcd18de68d4ecfb5c103cac36cff8d8619f455eaea` |
| **G24** | `…block_09.log` | `b698b645b4abebc6a5108d37669786e7662872e1a0c51fdb61bcc7a626f36d90` |
| **G25** | `…block_10.log` | `4e046cac2b0e8fa4b3307030cef497b89986cee9b425695887e36741c49a2cd5` |

**Recipe:** `extraction/aggregate_m7.py evidence/m7b_blocks/*.log`
— fail-closed below ten blocks and on mixed sectors. **Status:
VERIFIED-BY-RECORD** (`anchors/MANIFEST.md` §2 — the aggregator reproduces the
published table; P2 additionally reproduces the *charm* table exactly:
0.0847 / 1.1530 / 1.1355 %, shifts 0.0451 / 0.5497 / 0.5125 %).

**Content invariants inside the logs:** 30 `XCHECK_OK`, zero `XCHECK_FAIL`;
300 counted files per block; all ten carry `# sector=b`; both macro sha256s
(`0d03d191231163a5…` parametrised, `d7be6731b44f5b95…` counts) identical across
all ten.

> **G16–G25 are load-bearing beyond M7b:** P2's charm reproduction is currently
> the *only* repo-local evidence for the charm table of §2.7, whose own logs are
> not committed.

### 2.9 Σ_b raw-count leg

`docs/SIGMA_B_ORDERING_AND_ADJUDICATION.md`. Final at 1000 files: Σ_b
**26.59 % ± 0.24**, Σ*_b **10.51 % ± 0.19**, ground **0.83 % ± 0.11**.
R1 HIT; R3 for Σ*_b HIT (+1.47 % ± 0.47, +3.2 σ); Σ_b null. **The Σ_b physics
gate is passed.**

| id | artifact | file sha256 |
|---|---|---|
| **G26–G35** | `anchors/sigmab_raw/sigmab_block_01..10.log` | `ce9cae18bf5cb6ac…`, `1b7dc9f44f19db49…`, `4c40697e0a89710a…`, `0a6cc4039075981b…`, `e1f3ffdb3c6d2c86…`, `7daca11b0db87cad…`, `58117c4c8d8ed661…`, `e26417b78b9427e9…`, `aa8b6c8146e67f44…`, `83a407718b0ff64a…` |

Full digests are in the manifest block at §7. **Status: UNVERIFIED** — no
aggregator recipe for these logs was found in `tools/`. See §6, finding F2.

### 2.9b MONASH central table — the first tune's numbers, `38bf707`

`docs/MONASH_CENTRAL_TABLE.md`, delivered 2026-08-12. **Closure PASSED at the
registered counts**; the decomposition is FINAL for MONASH.

| registered | required | observed |
|---|---|---|
| **C1** content comparisons | 2100 = 7×300 | **2100** |
| **C2** invariant comparisons | 1500 = 5×300 | **1500** |
| **C4** schema from each file's own `analysis_schema` | `…_v3` | `paul_pair_objects_primary_ground_v3` |
| errors | 0 | **0** |

**Not the 1800/600 failure mode.** Total central entries **1,298,655,240**;
**I3 exact** — the ten blocks sum to the central bin by bin.

**Diquark-structure (primary), block mean % ± SEM (dof = 9):**

| group | block mean % | SEM |
|---|---|---|
| kCentralGround | **52.3388** | 0.0074 |
| kExcludedVector | **46.6510** | 0.0079 |
| kExcludedExcited | **1.0102** | 0.0012 |
| **kMultiplyHeavy** | **0.0000** | 0.0000 |

Sum = **100.0000 %** — this convention **is** a partition.

**Experiment-comparable (map v2), block mean % ± SEM:** D⁰ 25.2435 ± 0.0038,
D̄⁰ 25.1707 ± 0.0070, D⁺ 13.1408 ± 0.0034, D⁻ 13.1129 ± 0.0032,
D_s⁺ 4.2366 ± 0.0015, D_s⁻ 4.2331 ± 0.0017, B⁺ 2.3035 ± 0.0018,
B⁻ 2.3024 ± 0.0026.

> ### ⚠ TWO PAPER-FACING LABELS — owner ruling, 2026-08-12
>
> **1. `kMultiplyHeavy` is ~0 for a stated reason** — see the verification note
> below, which **changes the wording** the ruling provisionally approved.
>
> **2. The experiment-comparable table is a SELECTION, not a partition.** Those
> eight species **do not sum to 100 %** and are not meant to. The diquark-structure
> table above **is** a partition and does sum to 100 %. **The two tables answer
> different questions and have different completeness properties**, and printing
> them adjacently without saying so invites the reader to add up the second one
> and conclude weight is missing. **Ruled 2026-08-12: promote this caveat ABOVE
> the table**, where a reader meets it before adding the column up.

#### ✅ 2.9b-i — the kMultiplyHeavy footnote: verified, corrected, approved

The ruling required *"verify the 192 and the mechanism from the code path before
committing the words."* **Done read-only 2026-08-12. The number was exact; the
mechanism was not what the words said. The wording was replaced before it
reached a committed document.**

**Approved text, to be committed verbatim at point of use in
`MONASH_CENTRAL_TABLE.md` §4a** (full check table: private restructure plan, Section 1.3):

> kMultiplyHeavy 0.0000% — 192 entries of 1,298,655,240 (1.5 × 10⁻⁵ %).
> This category holds hadrons with |q_c| > 1 or |q_b| > 1 — the doubly-
> and triply-heavy baryons Ξ_cc, Ω_cc, Ω_ccc. It is a populated category
> of the partition, not an exclusion; the six categories sum exactly to
> the total. The value is small because doubly-heavy baryon production
> is rare, not because anything was classified out.
>
> B_c⁺ (q_c = +1, q_b = −1, neither above 1) is counted as a ground-state
> species in kCentralGround; the one category excluded by construction is
> kHiddenHeavy (quarkonia), with exactly zero entries.

**The three artifact facts a reader of this contract needs:**

| | |
|---|---|
| `kMultiplyHeavy` selector | `HeavyFlavourUtils.h:357-359` — `|q_c| > 1 \|\| |q_b| > 1` |
| species carrying it | **36** in the ordinal table, catching **192** entries — represented on the axis, rare in the physics |
| B_c⁺ (541) | ordinal 119, `central_registry: 1`, **`kCentralGround`** — inside the primary bin, not a separate one |

> ### The error, and how it was caught — recorded with both sources
>
> **"By construction" reached the approved wording by two independent routes:**
> proposed in a dated private handoff, Section 3.1, from reading the two tables
> without opening the classifier, **and entered the owner's addendum
> independently of that handoff.** Neither derived it from the code.
>
> **Two parties agreed, and agreement was worth nothing** — E1's lesson in a new
> place: *a reimplementation check proves agreement, not correctness.* What
> caught it was a **mechanical requirement to read the code path**, carried by
> the very ruling that carried the error. **The requirement caught its own
> text.**

**Cross-check, independent path:** the superseded private convention-table record (v47) computed
the central from the merged output by a different route and agrees **exactly** —
52.3388 %, 25.2435 %, 13.1408 %.

**Provenance:** chain sha `eae4c0ae3b2dfaaa`; closure script/macro `b8e7c7b7…` /
`044e47e6…`; pinned checkout `43e35be876dd5d881a931cb845ab490ab9b97509`;
reader/artifact/map_v1.1 `b67f9008…` / `ccec0dbc…` / `ed148156…`; 11 directories
× 300 root files, preflight OK; `rc0_count=11 (expect 11)`.

**Status: VERIFIED-BY-RECORD** — this is a delivered measurement with its own
provenance block, not a regenerable artifact. **It is not byte-frozen**: the two
remaining tunes extended it — see 2.9c.

### 2.9c Three-tune central table — the resubmission's central number, FINAL 2026-08-16

`docs/THREE_TUNE_CENTRAL_TABLE.md`. **All three closures PASSED at the
registered counts.** MONASH 2026-08-12; **JUNCTIONS 2026-08-16 11:58:20 CEST**
and **CLOSEPACKING 11:37:27**, both `errors=0`, **2100 / 1500**, schema
`paul_pair_objects_primary_ground_v3`, `relative_tolerance=2e-10`. Both new
lines are recorded verbatim in that document's §0b.

**The two new closures used `expected_central_events=100000000`**, the strong
argument, against MONASH's recorded `-1`. **The A4 expected-schema argument does
not exist on the frozen Nikhef tree**, so the schema was verified by **reading
the emitted `analysis_schema=` value** through
`extraction/pipeline/harvest_tune.py --stage closure`, not by an argument the
wrapper would have enforced.

**Diquark-structure (primary), block mean % ± SEM (dof = 9) — a PARTITION:**

| group | MONASH | JUNCTIONS | CLOSEPACKING |
|---|---|---|---|
| kCentralGround | **52.4959** ± 0.0074 | **58.2318** ± 0.0078 | **54.1697** ± 0.0112 |
| kExcludedVector | **46.4946** ± 0.0079 | **39.9409** ± 0.0083 | **39.9976** ± 0.0105 |
| kExcludedExcited | **1.0095** ± 0.0012 | **1.7821** ± 0.0015 | **5.7745** ± 0.0050 |
| kMultiplyHeavy | **0.0000** ± 0.0000 | **0.0452** ± 0.0004 | **0.0583** ± 0.0007 |

Totals **53,662,416 / 46,311,148 / 46,678,201**; per event **0.5366 / 0.4631 /
0.4668**. **I3 exact for all three tunes**, bin by bin.

> **⚠ The experiment-comparable table in §2 of that document is a SELECTION, not
> a partition.** It sums to ~91 %, deliberately. Do not normalise it.

> **⚠ I2 is NOT clean, and the document says so.** JUNCTIONS carries **3 flagged
> bins** and CLOSEPACKING **1**, against step 2's registered **zero**
> (`PER_TUNE_PROCESSING_PREREGISTRATION.md`). All four are diagnosed and
> jackknifed immaterial — **no row moves by more than 1.19 SEM**.
>
> **✅ RULED 2026-08-20: this is a DEVIATION, not an amendment.** The registered
> expectation of zero flagged bins stands exactly as written, and the four flags
> are reported against it. `PER_TUNE_PROCESSING_PREREGISTRATION.md` is **not**
> edited, because a registration changed after the result stops being one.
> **This entry records the table as FINAL on the closure verdicts plus that
> ruling**, with the caveat, not without it.
> `THREE_TUNE_CENTRAL_TABLE.md` §0 carries the ruling and its measured basis.

**Regeneration recipe** — the table's stdout is the regenerable object:

```bash
extraction/three_tune_table.py \
  MONASH=evidence/merged_monash_dedup \
  JUNCTIONS=evidence/merged_junctions_dedup \
  CLOSEPACKING=evidence/merged_closepacking_dedup
```

| | |
|---|---|
| **stdout sha256** | `a46a7f6b96f668177ee600746e51eadf1dfaabdaceac07c1265ef5d7d0fc930d` |
| inputs | **committed anchors** — the table regenerates from the repository alone. The remote run roots (`tune_runs_e5fix/MONASH/`, `tune_runs_three/{JUNCTIONS,CLOSEPACKING}/` on `stbc-i3`) produce the **same digest**, byte for byte, and are the origin rather than a dependency |
| extractor / artifact / registry / map v2 | `4cd8b6fa…` / `ccec0dbc…` / `ea9b0232…` / `58081aa2…` — **all four identical to 2.9b's** |
| ROOT (extraction) | `v6-30-01-alice5-2` from CVMFS, **on pin** |
| pinned checkout | `43e35be876dd5d881a931cb845ab490ab9b97509` |

**The recipe is checked by `make check`:** `tests/test_three_tune_tables.py`
runs it over all three committed anchors, asserts **every structural cell of
the FINAL table (mean and SEM)**, asserts the partition/selection distinction in
both directions, and asserts **the digest above**. A change that moved the table
without moving this document would fail the suite.

**Status: VERIFIED-BY-RECORD, recipe REGENERABLE.** The digest above is of the
tool's stdout given the three run roots; it is **not** a byte-freeze of the
markdown document, whose prose will be edited.

### 2.10 Closure at v3 scale — a content invariant, not a file

| | **v3 (correct)** | v2 (the trap) |
|---|---|---|
| content comparisons | **2100** = 7 × 300 | 1800 = 6 × 300 |
| invariant comparisons | **1500** = 5 × 300 | 600 = 2 × 300 |

> **⚠ 1800/600 IS FAILURE, NOT SUCCESS.** A v3 run reporting them resolved the
> object set against the v2 sidecar schema, which means `hFlavourClosureSpecies`
> was never closure-checked and the three species provenance strings were never
> identity-checked. The run completes, reports no failures, and has skipped
> exactly the content v3 exists to validate.

**Derived, not asserted**, from `config/pair_file_object_contract_v1.json` at
`1de9bfe`. The derivation is the recipe: count objects with
`closure == "checked"` **and** a histogram-like `root_class` (→ 7), and objects
with `identity_checked == "true"` (→ 5), each × 300 pair files.

**This entry's freeze condition is unusual and must be stated:** the numbers are
**not** frozen against contract edits. Any future contract change that adds a
closure-checked histogram or an identity-checked string **moves them legitimately**.
What is frozen is that **the derivation is re-run rather than the numbers
re-quoted.** A restructure that moves
`config/pair_file_object_contract_v1.json` (13 referencing files) must keep the
derivation runnable.

### 2.11 The bin-level audit trail

`extraction/compare_subset_parent.py` on **G11 (subset) vs G14 (parent)** at expected
scale **9.9986** flags **30 of 88 testable bins at |z| > 4** — robust across
three variance models (binomial 30, Poisson 27, independent-samples 26). 16 bins
deviate >2 %, up to 33 %, median 3.1 %, almost entirely baryons.

**The reference set is pinned in `tests/test_compare_subset_parent.py`**, which
is in the suite and checks three independently-failing things: the known 30-bin
case reproduces; parent-vs-itself flags **nothing**; an injected 10 σ bin **is
caught**. **Status: SELF-CHECKING** — it runs in `make check`.

> **ANNOTATED 2026-08-13 — the recalibration was executed; this invariant is NOT
> rewritten.** "30 of 88" is the **binomial** null and remains the historical
> computation of record; R10 now names it explicitly. Under the robust null the
> same comparison gives **0 of 88** at σ̂ = **4.3990**, largest bin |z| = 2.83
> (R10b). **Both are pinned**, as checks 1 and 4; the test now carries **eight**
> checks, not three — the four new ones cover the MAD null's negative control,
> its injected positive at its *own* scale, its calibration on synthetic binomial
> data (σ̂ → ~1, which is what makes "4.4" readable as 4.4× overdispersed), and
> the counting floor. **The zero does not clear the anchor** — §2.11a.

> This is the audit trail for what the anchor got wrong, **kept as a test rather
> than as prose.** A restructure that breaks this test's fixture paths destroys
> the only executable record of E4.

#### ⚠ 2.11a — the JUNCTIONS I2 recalibration lands on THIS function

**Standing ruling for the next harvest session:** *"I2 recalibration, minimal:
robust empirical cross-block null (MAD-based σ), keep |z| > 4. The binomial null
is retired for pair counts."*

**`decompose_with_block_sems.py:84` does `from compare_subset_parent import
compare`.** I2 and the pinned E4 regression call **the same function**. So the
ruling, read literally, changes the null underneath a test that pins a published
number's audit trail.

**The arithmetic, to size it rather than assert it.** `38bf707` puts the
overdispersion factor at **~4.75** in variance, i.e. **σ inflated ~2.2×**. E4's
flagged set was 30 of 88 bins at |z| > 4 with the largest at z = +11.0 (Σ̄_b⁻)
and z = +11.6 (Ξ*_c⁺). Under a 2.2× wider σ those two land near **z ≈ 5.0 and
5.3 — still flagged** — while the bulk sitting between 4 and 6 drops below
threshold. **The 30-bin set would shrink substantially, and "30 of 88" is quoted
in private error-ledger entry E4, the superseded private convention-table record, Section 5, and
`anchors/extraction_dual/MANIFEST.md`.**

### ✅ RULED 2026-08-12 — and the ruling is better than either option I offered

> *`compare()`: null mode becomes a **REQUIRED** argument — no default. I2 passes
> MAD; the pinned E4 test passes binomial explicitly, commented as deliberately
> pinning the historical computation.*
>
> *Run the recalibrated compare on the E4 case; annotate the three documents
> quoting "30 of 88" with the measured corrected count, dated, **never rewriting
> the original**. State in the same note that **the anchor quarantine STANDS** —
> the verdict rests on localized, physically large deviations, not on the flag
> count.*

I framed this as a choice between adding a mode and replacing the null. **Both
of my options left a default in place, and a default is exactly what encodes a
silent choice** — the same defect as F1, in the same session's other fix. Making
the mode **required** removes it from both call sites at once: neither caller can
inherit a null it did not name, and the pinned test's binomial becomes a
*documented deliberate choice* rather than an inherited accident.

**Consequences for this section:**

- **the content invariant "30 of 88 at |z| > 4" is not rewritten.** It stands as
  the historical computation, with the recalibrated count **annotated beside it,
  dated**;
- **the quarantine verdict does not depend on the recalibration.** It rests on
  deviations that are **localized and physically large** — 16 bins above 2 %, up
  to 33 %, almost entirely baryons — not on how many bins cross a threshold.
  A smaller flag count under a wider null does not soften it;
- **the pinned test stays green by construction**, because it will name binomial
  explicitly.

**JUNCTIONS harvest, first item, one commit + suite. Not the restructure
session.** ✅ **Ordering ruled 2026-08-12: SERIALIZED — restructure first, then
JUNCTIONS on the post-restructure layout.** Both touch
`compare_subset_parent.py`; serializing removes the collision rather than
managing it, and the JUNCTIONS session will find the tool at its new path with
the paths already fixed.

#### ✅ EXECUTED 2026-08-13 — and the ruling's arithmetic did not survive measurement

The mechanism landed exactly as ruled: `null` is a **required keyword-only
argument** of `compare()` with no default anywhere, I2 passes `mad`, and the
pinned E4 test passes `binomial` by name. **The predicted numbers were wrong.**

| | ruling predicted | measured |
|---|---|---|
| σ inflation on the anchor case | ~2.2× | **4.399×** (variance 19.4×) |
| the two largest bins (Ξ*_c⁺, Σ̄_b⁻) | survive at z ≈ 5.3, 5.0 | **z = +2.83, +2.70 — neither survives** |
| flagged set | "shrinks substantially" | **0 of 88** |

**The error was applying the wrong comparison's overdispersion.** The ~2.2×
comes from `38bf707`'s **block-vs-central** figure, measured on clean
comparisons. The anchor-vs-parent comparison is not clean — that is the entire
point of E4 — and its pull distribution is genuinely ~4.4 wide, confirmed by
three independent scale estimators (MAD 4.399, stdev 4.426, IQR/1.349 4.364).

**What the zero means, stated so it cannot be misread as a clearance.** A robust
scale estimated *from the sample* absorbs contamination that is **broad**. The
anchor's defect is 30 of 88 bins displaced *together*: the bulk is the defect,
so nothing stands out from it. **The MAD null sees localized failures and is
blind to broad ones.** The consequence for the pipeline is recorded in
`PER_TUNE_PROCESSING_PREREGISTRATION.md`: **I2 and I3 are not redundant** — I3's
exact block-sum identity is what must catch a broad or uniform displacement.

**Two things the ruling did not anticipate, both now in the tool:**

- **A counting floor.** σ̂ is never allowed below **1.0** for the test statistic.
  The pulls are already in binomial-sigma units, so σ̂ < 1 means *less* dispersed
  than counting statistics permit — impossible for a genuine sample, and the
  signature of a deterministic split. Without the floor, blocks built by exact
  division gave σ̂ = 0.002 and **90 manufactured flags** across a run whose
  binomial pulls never exceeded 0.06. The raw σ̂ is still reported; only the test
  statistic is floored.
- **A calibration check.** On synthetic genuinely-binomial data σ̂ recovers
  **~1.0** (measured 1.017 ± 0.077 over 20 seeds), which is what licenses reading
  σ̂ = 4.4 as "4.4× overdispersed" rather than as an unscaled number.

**The quarantine STANDS**, on exactly the grounds the ruling gave: localized,
physically large deviations, not a flag count.

**This does not affect the MONASH SEMs.** `MONASH_CENTRAL_TABLE.md` §3 records
I3 as exact and the SEMs as unaffected; the misspecified null is a flagging
instrument, not an input to the numbers.

#### ⚠ CORRECTED 2026-08-13, later the same day — the control changes two claims above

**Two statements in this section are wrong, and the corrections point opposite
ways.** Both were fixed by running the control that was never run: comparing the
anchor against **ten genuine 1/10 subsets of the same parent**, like-for-like on
replication.

**1. "The ~2.2× is the block-vs-central overdispersion, measured on clean
comparisons" — wrong on both halves.** Measured directly:

| block-vs-central sweep | σ̂ |
|---|---|
| **deduplicated** blocks (10) | **0.955 ± 0.096** — i.e. no overdispersion at all |
| **replicated** blocks (10) | **4.800 ± 0.519** |

So the honest figure for a clean block comparison is **≈ 1**, not 2.2, and pair
counts at block level turn out to be **binomially dispersed after all**. The
inflation is **replication**: multiplying counts by R scales a binomial pull by
√R, measured at **5.03×** against √24.2 = 4.92 predicted. The recorded "353
flags in 880 at ~4.75× variance" was itself largely an **E5 artifact**, not a
property of the physics.

**2. "The zero is a blind spot, not a clearance" — the simpler explanation is
the right one.** The anchor's peer group is the **replicated** sweep, and against
it the anchor is unremarkable: σ̂ 4.399 vs 4.800 ± 0.519, binomial flags 30 vs a
real-subset range of 32–40, largest deviation 32.99 % vs real subsets reaching
38.02 %. **The MAD null returns zero because there is nothing localized to find,
not because it cannot see.**

**The blind-spot property is still real** — median-centring genuinely removes a
uniform offset, and the A12 fixture demonstrates it — so **I2 and I3 remain
non-redundant** and that guidance stands. It just is not what produced the zero
here.

**Consequence for the quarantine, stated precisely.** The bin-level statistical
evidence for E4 does not survive the control; the quarantine now rests on the
anchor being **unprovenanced** and on its physics result having been
**contradicted by two traceable datasets**. Full detail, and the open question
about the −7.4 σ, are recorded in private error-ledger entry E4. **Nothing there was
rewritten, and this annotation does not lift the quarantine.**

---

### 2.12 Historical deterministic SVG diagnostics — EXCLUDED

The three files recorded here are AI-assisted explanatory graphics generated
from committed tables. Owner ruling 2026-08-21: they are internal diagnostics,
not scientific results or publication figures. Their digests remain recorded
only as historical provenance; neither the graphics nor their private support
code belongs to the publication export.

The private development repository retains the three filenames, generators,
tests, and historical digests. They are intentionally omitted here as public
reproduction targets because none is an accepted scientific output.

> **fig 1 and fig 2 moved again on 2026-08-16 (polish pass), presentation only.**
> fig 1's legend header sat 7 px under the *CentralGround* axis label and read
> as part of the axis row; it was dropped clear. fig 2's value labels were drawn
> **through** the upper error-bar caps in the beauty panel, where the SEM is a
> sixth of the bar height — they now anchor above the error bar rather than
> above the bar. **No number moved**: fig 1's 42 cells were re-checked against
> `THREE_TUNE_CENTRAL_TABLE.md` (0 mismatches) and all three figures remain
> byte-identical across independent runs. fig 3 was unchanged.
>
> **fig 1 and fig 3 moved on 2026-08-16, for different reasons.**
>
> **fig 1 — the reserved slots filled.** JUNCTIONS and CLOSEPACKING anchors
> landed, so the figure now draws three bars per group instead of one and the
> legend no longer says *"not yet merged"*. This is the legitimate move the
> paragraph below anticipated. Its 42 cells — every mean **and** every SEM in
> both panels — were checked against `THREE_TUNE_CENTRAL_TABLE.md` and agree
> exactly. Panel B's rows are now the table's common row set rather than one
> tune's top-8, because each tune's own top-8 is a different set.
>
> **fig 3 — two layout defects found by looking at it.** Its numbers did not
> change. Panel A's staggered boundary labels were drawn *through* the panel
> title, and the residual box was 3 px too short so its last line fell outside
> it; moving the panel down exposed a third, the box covering panel B's
> per-class boundary values. **All three were invisible to the test suite and
> visible immediately in the rendering** — which is the argument for the
> standing rule that every figure is looked at before it is committed.

**These digests are pinned differently from the rest of §2, and the difference
matters.** They are frozen against *accidental* change only. A figure whose
underlying table legitimately moves — JUNCTIONS and CLOSEPACKING landing as bars
in fig 1, for instance — **moves these digests on purpose**, and the digest is
then re-recorded here. What is frozen is that **the figure is regenerated from
committed data rather than edited**, and that regeneration is deterministic.

**The third diagnostic recomputes a published table rather than displaying it.** The
per-tune percentile translation in `PRODUCTION_SHAPE_DECISION.md` — the residual
the axis ruling requires be published — is recomputed from the committed MB
samples and reproduces the published values to **< 0.01 pp on all eleven
classes**, with the maximum residual landing on **2.91 pp** exactly. That
agreement is asserted by the test, so the figure and the table cannot drift
apart silently.

Byte determinism proves only that the historical diagnostic bytes can be
reproduced. It does not establish scientific completeness, uncertainty
coverage, ROOT-plot provenance, or suitability for the paper.

> **The scientific result that was deliberately not imitated.** The OS−SS observable versus
> multiplicity class has **no committed table** — it is what the A2 jobs produce
> (`docs/A2_PAIR_UNRESOLVED_RUN_RECORD.md`). The historical diagnostic path
> refused to draw a placeholder. A figure with invented data
> is worse than a missing figure, because a figure travels further than its
> caption.

---

## 3. WHAT IS FROZEN THAT IS NOT AN ARTIFACT

Regeneration contracts that live in code and text, not in a digest:

| # | contract | where |
|---|---|---|
| **C-1** | PYTHIA 8.317, stock upstream tarball `sha256 1ae551d1…45adf`, unmodified, `-std=c++20` | `REPRODUCIBILITY.md` §1, `environment/ROOT_PYTHIA.md` |
| **C-2** | ROOT 6.30/01 ALICE CVMFS build | `REPRODUCIBILITY.md` §1 |
| **C-3** | producer binary sha256 `e54b27bb9e3fcfd42d70193e08e2eacf965cc5081eabb5c42a9971203f130659`, present in all 300 analysis outputs | private phase-4 submission checklist, B2 |
| **C-4** | `seed_derivation_v2`; `SEED_BASE=100_000_001`, strides 10M/1M/100k; ordinal cap **79**, raising rather than truncating | `REPRODUCIBILITY.md` §2 |
| **C-5** | full-production cost **562.5 CPU-hours**, not 390 | `REPRODUCIBILITY.md` §6 |
| **C-6** | campaign HF_RUN3_V1 complete and promoted, **3000/3000**; seed ledger **3557/3557** | `docs/campaigns/HF_RUN3_V1_RECORD.md:753` |
| **C-7** | heavy flavour signed by **quark content, not charge**: `q_c = n_c − n_cbar` | `REPRODUCIBILITY.md` §1 |
| **C-8** | the 34 breach partials were **moved, never deleted**, with a committed manifest | private partials-archive record |

**C-6's ledger is not in this checkout.** It lives under
`/data/alice/ipardoza/Hadronization-full-production/campaigns/*/seed_ledger.jsonl`
— a *different checkout on the same host*. A restructure of the Nikhef disk
must not orphan it. See the private cluster-disk inventory.

---

## 4. THE RECIPES, AS ONE ORDERED LIST

Run from the repository root, tree clean. **Check the named output line, never
`rc`** — ROOT returns 0 when it cannot find a macro's entry point.

> **Paths are post-restructure (2026-08-12) and post-rename (2026-08-27).** The
> six extraction tools moved `tools/` → `extraction/`; the two map builders
> stayed in `tools/`. The artifacts did not move in 2026-08-12: the owner's D4
> override held their directory name, precisely so these recipes' inputs stayed
> put. Ruling R19 of 2026-08-27 retired that name. The four generated headers
> and the three JSON tables are now in `contracts/`, and the anchor store is
> `evidence/`. The recipes below name the post-R19 paths. The executed table is
> retained in the private rename record.

| # | command | positive check |
|---|---|---|
| R1 | `make registry` | no `STALE`; exits 0 |
| R2 | `python3 tools/generate_species_ordinals_header.py --check` | absence of `SPECIES_ORDINALS_STALE` |
| R3 | `python3 tools/generate_pair_object_contract.py --check` | absence of the stale marker |
| R4 | `make cards && make cards-current` | both exit 0 |
| R5 | `tools/build_decay_parent_map.py evidence/f4_probe/f4_probe_v1.out --ordinals contracts/species_ordinals_v2.json --out /tmp/v11.json` | `map_sha256=dd502a10c5932fff`, `I1=PASS I2=PASS`, `artifact_rows_changed=101 table_affecting_rows=60` |
| R6 | `tools/build_decay_parent_map_v2.py evidence/f4_probe/f4b_probe.out --ordinals contracts/species_ordinals_v2.json --v1 contracts/decay_parent_map_v1_1.json --weights evidence/extraction_dual/per_species.csv --out /tmp/v2.json` | `sha256=c9593c9c0a7c4ec2`, `split=2`, exactly two `SPLIT` lines |
| R7 | `extraction/apply_decay_map.py --map contracts/decay_parent_map_v2.json --weights evidence/merged_monash_replicated/per_species.csv --mode split` | `TOTAL 1298655240 INVARIANCE CONSERVED`; D⁰ **25.2435**, D̄⁰ 25.1707, D⁺ 13.1408, D⁻ 13.1129 |
| R8 | `extraction/second_branch_weight.py --per-species evidence/merged_monash_replicated/per_species.csv` | `SECOND_BRANCH_DONE at_risk_pct=12.8396 concentration_top4=97.81%` — the **(C) chained history** row of §2.6, **not** "THE NUMBER" |
| **R8b** | same, plus `--v2-map contracts/decay_parent_map_v2.json` | `SECOND_BRANCH_V2 presplit_pct=5.7644 postsplit_residual_pct=0.0018 residual_species=2` — **THE NUMBER**, with B_c⁻/B_c⁺ named as the whole residual. (Pre-split reads 5.7644 not 5.7737 because it is recomputed on the *merged* weights, not the anchor's baked-in ones — that is the tool working, not disagreeing.) |
| R9 | `extraction/aggregate_m7.py evidence/m7b_blocks/*.log` | reproduces §2.8 (beauty); fail-closes below 10 blocks |
| **R9b** | `extraction/aggregate_m7.py evidence/m7_blocks/*.log` | reproduces §2.7 (charm) — **new: the charm logs were anchored in `b74e588`** |
| R10 | `extraction/compare_subset_parent.py evidence/extraction_dual/per_species.csv evidence/merged_monash_replicated/per_species.csv --null binomial --expect-scale 9.9986` | **30** bins flagged, `rc=1` by design |
| **R10b** | same, `--null mad` instead | **0** bins flagged, `sigma^ = 4.3990`, `rc=0` — the recalibrated null of 2026-08-13. **rc=0 here is NOT a clean bill of health**: see §2.11a |
| R11 | `make test` | **45/45**, ROOT present *(was 39/39 when this row was written; the denominator moves as tests are added — what is pinned is that every test passes and ROOT is present)* |
| **R13 retired** | historical SVG diagnostic path | Owner ruling 2026-08-21: excluded from the publication contract; its old digests remain in §2.12 only as provenance. |
| **R12** | `tools/reconstruct_deduplicated_decomposition.py` | `charm 24x, beauty 26x`; `87 species invert exactly, 8 ... bracketed`; total `53,662,413.8 .. 53,662,827.8`; writes G14d/G15d |
| **R14** | `extraction/three_tune_table.py MONASH=<rundir> JUNCTIONS=<rundir> CLOSEPACKING=<rundir>` | §2.9c's table; stdout sha256 `a46a7f6b96f66817…fc930d`. On the committed anchor alone (`MONASH=evidence/merged_monash_dedup`) it reproduces §2.9b's MONASH column, which is what `test_three_tune_tables.py` pins |
| **R15** | `extraction/bbaryon_tune_advisory.py MONASH=<rundir> JUNCTIONS=<rundir> CLOSEPACKING=<rundir>` | the b-baryon advisory. MONASH Σ_b⁺ **1.6377**, Σ_b⁰ 1.5858, Ξ'_b⁰ 1.7572, Λ_b⁰ 1.0124. **`rc=0` always — it is an advisory and never fails**, so its exit status is not a verdict |

**R11 has a trap of its own**, documented in `tools/run_tests.sh:13-15`: without
ROOT, `make check` reports a *smaller denominator* and looks healthy on a laptop
while failing on the cluster. **A green run must show `ROOT: /path/to/root`.**

---

## 5. WHAT CANNOT BE REGENERATED — state this to the reviewer

| # | item | why | consequence |
|---|---|---|---|
| **N1** | `extraction_dual/` (G11–G13) | source directory held the three CSVs and **nothing else** — no log, manifest or invocation record. Tune, input count, reader commit and date are unrecoverable; surviving prose disagrees (100 inputs vs four directories) | frozen as history + regression fixture; **superseded for every number** by G14 |
| **N2** | merge timing / the 65–77 h band | the merge log **carries no timestamps**; every timing in the private merge-band validation record is reconstructed from filesystem mtimes and **cannot be re-derived once scratch is cleared** | ⚠ **the restructure must not clear merge scratch before the band is scored** |
| **N3** | the PYTHIA install | personal directory, no container; tarball checksum recorded, nothing rebuilds it | a third party must build PYTHIA themselves |
| **N4** | the junction hang | 1 M events on 8.315 with a byte-identical card and the exact seed of a hung job **did not hang** | identical inputs, different behaviour; mechanism unexplained |
| **N5** | discarded jobs | the hang hits dense-junction topologies — exactly the configurations under study | the discard rate must be **reported, not corrected away** |
| **N6** | G1's source fixture | one JUNCTIONS raw file on Nikhef; digest recorded, file not committed | G1 regenerates only with Nikhef access |
| ~~**N7**~~ | ~~M7 **charm** block logs~~ | — | ✅ **CLOSED 2026-08-12, `b74e588`.** Anchored as G36–G45 (§2.7), verified against the published charm table. **Left on this table struck through rather than deleted: a gap that was closed is part of the provenance story, and a reader of an older handoff needs to find its resolution** |

> **N2 is time-critical and outranks every other item in this document.** It is
> the one entry where *doing nothing* still destroys evidence, because the
> evidence is filesystem metadata on a scratch area. **No consolidation touches
> merge scratch until the band is scored.**

---

## 6. FINDINGS RAISED WHILE BUILDING THIS CONTRACT

Recorded here and in the prep handoff **for the main line to act on**. This
session changed no code and no main-line document.

### F1 — the extraction reader's `--decay-map` default is the defective v1

The historical reader once selected the excluded defective v1 decay map by
default. **v1 is the map that does not conjugate antiparticle decays** — private
error-ledger entry **E1**, 17.8 pp on D⁰.

**Why no existing check catches it.** `load_decay_grouping` fails closed on a
digest mismatch — but it compares `ordinal_table_digest_fnv1a64`, which is
**`646f310f78126267` in v1, v1.1 *and* v2 alike**. The check cannot distinguish
them. The invariance check then passes too, because **conjugation errors move
weight between bins and conserve the total exactly** — E1's stated reason every
aggregate check missed it the first time.

**Blast radius, bounded honestly:** `per_species.csv` and `per_category.csv` are
map-independent, so **G14/G15 are unaffected**. The map-dependent output is
`per_observable.csv` — precisely the file the anchor manifest already flags as
superseded-because-computed-under-v1. **The live pipeline is safe**:
`extraction/pipeline/tune_extract.sh` passes `--decay-map …/decay_parent_map_v1_1.json`
explicitly. **The hazard is an interactive or reviewer invocation**, which would
silently regenerate the 45.95 % table with every check green.

> ### ✅ RULED 2026-08-12 — the v1 default is a reproduction hazard
>
> **Fix in the restructure session: remove the default, make `--decay-map`
> required. One line + suite. No separate ceremony.**
>
> The private restructure plan, Section 1.2, carries the scope and flags the residual that
> sits four lines away: with the argument required, a **mistyped or stale** path
> still takes the false branch of `if args.decay_map.exists():` at `:278`,
> leaving `decay_verdict = "SKIPPED"` and `rc=0`. Same function, no extra
> ceremony to close while already there. **Executor's call.**

**Not fixed on this branch** — it is docs-only, and the ruling places the change
in the restructure session.

### F2 — the Σ_b block logs have no committed aggregator

G26–G35 are anchored, and `docs/SIGMA_B_ORDERING_AND_ADJUDICATION.md` quotes
numbers derived from them, but no tool in `tools/` was found that consumes
`anchors/sigmab_raw/*.log` the way `aggregate_m7.py` consumes the M7b logs.
**This makes §2.9 the one physics-gate result in the pack with anchored inputs
and no repo-local recipe.** Classified **UNKNOWN**, not "missing": the
aggregation may live in a doc as an arithmetic derivation this session did not
locate. **Question for the owner:** is there one, and should it be committed?

### F3 — G13 is quarantined-but-cited, and the citation is load-bearing

`per_observable.csv` is superseded, but it remains the **only** committed
artifact carrying the pre-fix experiment-comparable grouping — i.e. the evidence
that E1 was real and how large it was. **Any deletion sweep that reads
"superseded" as "deletable" destroys the E1 evidence.** Same shape as G5. Both
are marked **history — never delete** in the census.

---

## 7. DIGEST MANIFEST — the machine-checkable form

The gate is **digest-keyed, not path-keyed**, because a restructure changes
paths by definition. Regenerate this block after any accepted restructure with
the new paths; the right-hand column must be unchanged.

```
ccec0dbc70f6452d1f4a5c22a37e76ce55b357046094da207469f08534d0e4ce  species_ordinals_v2.json
cac0a757ec7bdca04f2390668334733488d95bba14b3f22be2e0216980ad86c2  systematics_results_20260819/per_class_deltas.json
37aae5bdad84dc6652399b2c77ddc6ae9c6c91df5073df6af1510d560315befd  systematics_results_20260819/tune_separation.json
b1b5954812398d748297111ab64375d2abecfb4d04b3e98ff3ccdf8d9890087e  systematics_results_20260819/ratio_trend.json
e8fe560f378161c8d8ee45f5919cc1ff9ca3984b4a109ce02763968067ade023  systematics_results_20260820/per_class_deltas_seven.json
8a8a26b8e676145a210cddd6952b23fc69c57cebfc3733fac0d1d810870cfc57  systematics_results_20260820/per_class_combination.json
7ecedf3abf5e8d65c99d1d3ea1be8bfd53b0d8e67796211c6650b7e8485a5d5a  systematics_results_20260820/verdict.json
db34411a3fd06b6c6eaecdfb253e3ffe9dfa13bbfb65163bd3d61e1a8d9e1bb1  systematics_results_20260820/per_category_final_two.json
70e07e49d8feeeda9cef5738b2cfaab4ef467a25db511e95e80caf2e38e4bb78  systematics_results_20260819/per_class_deltas.csv
f507f6250e63d82c9c34e088abe4ec16b17359e3b0a54fcdb54e17cd67653d7b  vintegrated_closure.log (nominal arm, figure_deploy_20260817)
690f2dc5694fa8639582e7ff2a5dd42f392c66ab2ccdf1268e9e5974e65afe68  render_HF_RUN3_V1.log (per-class control)
9f7fe1caab28552af2cb207a3bc38ac5dd3fbc61f77c60a3b652285b3efe8468  GeneratedSpeciesOrdinals.h
7d5e7bfdab80163f20f407fccfaad7543099d93a07609614b09eb6d626e985ff  GeneratedPairRegistry.h
f2a8c8ebb2cbbac9bd269b161cdcf05a13ae0f83679e81ee133647f80310ea10  GeneratedPairObjectContract.h
a67e8ae5f853689c010e991859242a77b913787dd30ab3d4c1b68bc05758c00c  historical_defective_decay_map
ed1481569dcf94e17a154e00a5eb5c829299d3c1502e04dd036ce5fcaccfe688  decay_parent_map_v1_1.json
58081aa2f87cb67141259f2b74a5057777a6c8eaa5049446fd3f47b13a1c84da  decay_parent_map_v2.json
f2d30a345bd8bed278062296d007f2dc5a4f101cf54f54b719e8caccd7d7cd76  f4_probe/f4_probe_v1.out
1525a0e5985b6969ed2cdda616560b8d5222ac338b089fe2343026e806adeb1c  f4_probe/f4b_probe.out
42a88913b4087691c9797bc3baf4212515020ab293ded4dbd3db7d45a4ee2d34  f4_probe/pdgs.txt
6137f6bc1f661ffdf26167a440091229f1466c87e2a8e4b50d096d66c3f45ac1  extraction_dual/per_species.csv
fe8d7dc577c56fd3e4ef9d090ee37b120b578d8fb2e08cdf8a5b08cd2f48db12  extraction_dual/per_category.csv
46bca45240ffb49662de3b9ab49be157ce2f0a0b08043e67bbe6f70f1d3f6303  extraction_dual/per_observable.csv
74ecfb6ee659e737caa45822592000f143c4a9e0f0b6365f12f273d33898ce76  merged_monash_replicated/per_species.csv
f162686c24b488c6cbd2c37085899be5df139b2e678c8109faeb8c263076e024  merged_monash_replicated/per_category.csv
5a75aa882853b9368ce065f1ce5b32a32eaff61180c8dbe65a2a006712f487e9  m7b_blocks/m7b_block_01.log
740c8f1ab51386c6907f8e6e15e127b4c6bab2be0ab077b0441fb9d1431ace74  m7b_blocks/m7b_block_02.log
5544e62f1f850acf382b7b1e1c6fb833972be9c268b87bf0cfa1e792fc94e50e  m7b_blocks/m7b_block_03.log
5f74c0d7ec2f48f21a7cb3e60fcc56179319ae4332b1a217518f63128cae1667  m7b_blocks/m7b_block_04.log
90413b23b28f1b03b56aa92a22069281f88fefa0602ace084a734fa1064012ba  m7b_blocks/m7b_block_05.log
b017da833e08f5b2abd6971450840bc039b92386ebe708fda5802b42730d3380  m7b_blocks/m7b_block_06.log
83f21fb4be84b1f6db6556f7c7f90c5099224dd9e4bccf08920f028004054cdb  m7b_blocks/m7b_block_07.log
14e9bc80f220282a054623fcd18de68d4ecfb5c103cac36cff8d8619f455eaea  m7b_blocks/m7b_block_08.log
b698b645b4abebc6a5108d37669786e7662872e1a0c51fdb61bcc7a626f36d90  m7b_blocks/m7b_block_09.log
4e046cac2b0e8fa4b3307030cef497b89986cee9b425695887e36741c49a2cd5  m7b_blocks/m7b_block_10.log
a457c2b7e4ce36ba3a5f6a2eb53928f1626e828c20a02fe1eb58357d2f44ada9  m7_blocks/m7_block_01.log
5732372cbcef4316d197f7401cb82ecc72e0303505e42f65f5d2ec351c15dc0c  m7_blocks/m7_block_02.log
22b7e018dc45bc56c63cbd86ad405e9c6d3cd940e4e3df814ebf0cbd9fc29555  m7_blocks/m7_block_03.log
fd51911bfd602feb084acd75b6e2cb3f34ddf6de4a3502078d0d8dafb72e0e4c  m7_blocks/m7_block_04.log
fa5a471f39cba439400741e1ad1cd1222bfd9eeae0791e7c0d925893d76b9314  m7_blocks/m7_block_05.log
a8b3f08879e2abcd011a186b7486988a78c4142e278870ef0d185d6e5935d8e2  m7_blocks/m7_block_06.log
86eefbced0a685bdd6a1197a502140bcf40353d58905a031f7dbdb0bb965b46f  m7_blocks/m7_block_07.log
499dbe9f6d4a8becb5e09d256f9ff8447c59520a29dd33c83ed52d227cd65e9b  m7_blocks/m7_block_08.log
d66c9b28d08f580560241acac24570d0e5c5c3b860495118d2acc6355ba99ed7  m7_blocks/m7_block_09.log
339ef575a5b21025d0b3a06b98b8fc2ee2f3fb37a661f9debc6f2f4452afc647  m7_blocks/m7_block_10.log
ce9cae18bf5cb6accd705ab0c0c08ec727ae989ca152eecffae5651ab792ee31  sigmab_raw/sigmab_block_01.log
1b7dc9f44f19db498cebcd453287a51a86bf524c3b0dc5e90fa782ba5c273fbe  sigmab_raw/sigmab_block_02.log
4c40697e0a89710ca21aa004c70c9c96d600d98b48348a7fd638f098f8da2396  sigmab_raw/sigmab_block_03.log
0a6cc4039075981b64e2bdb66c0fcf472edfd19da10571e6b493036a9ed2d590  sigmab_raw/sigmab_block_04.log
e1f3ffdb3c6d2c8614895ad015ff1e784010381515cd6dd333d602e3ed9668cc  sigmab_raw/sigmab_block_05.log
7daca11b0db87cadcd5baf4ef4609db196ea58858cbdcfdccc8fc7c04ae14581  sigmab_raw/sigmab_block_06.log
58117c4c8d8ed661a6dad16914635e540f11f2ec564e01bdde6ad5fff59a1b13  sigmab_raw/sigmab_block_07.log
e26417b78b9427e90e9b8c5d21ea32e217bc6ad6d76de3a001cd5f8c364a8f3b  sigmab_raw/sigmab_block_08.log
aa8b6c8146e67f44d4f4d0dff7b85c3f802502bdd9e7a603139034cd6e57ae0b  sigmab_raw/sigmab_block_09.log
83a407718b0ff64aa271759ac97048e3ab29c3b17c4e2aa761b5d33a924f23f1  sigmab_raw/sigmab_block_10.log
```

---

## 8. WHAT THIS DOCUMENT DOES NOT COVER

**Stated so a reader does not mistake its silence for coverage.**

1. **The three-tune cross-tune table** — the resubmission's central number.
   **MONASH landed 2026-08-12 (`38bf707`) and is §2.9b.** JUNCTIONS and
   CLOSEPACKING have not. **When the cross-tune table lands it becomes the most
   important entry in this document and it is not here yet.**
2. **`Paper/**`** — out of scope by instruction, untouched, unexamined.
3. **Plotting outputs.** `plotting/PAPER_FIGURE_PROVENANCE.md` exists;
   whether the paper figures are digest-pinned anywhere was **not established**.
   **UNKNOWN** — see the private restructure plan, Section 8.1 Q2.
4. **Any claim that a recipe was run.** None were, this session, by instruction.

---

## 9. THE RAW-TREE FIGURE FAMILY — recipe, and what is not yet golden

**Added 2026-08-17.** Figure 4 (shared charged-multiplicity spectrum) and the
per-species pT/η/φ panels, from the sealed and authorized HF_RUN3_V1 freeze.

### 9.1 The recipe

```bash
# on Nikhef, pinned stack
export HADRONIZATION_BASE=<checkout>
export DATASET_SELECTOR=config/dataset_selector_hf_run3_v1.json
source setupEnv.sh                      # ROOT 6.30/01, v6-30-01-alice5-2
bash plotting/run_paper_plots.sh kinematic-spectra
```

**One invocation produces all of them.** `Plot_InclusiveKinematicSpectra_Raw`
draws the multiplicity spectrum *and* the 30 `Inclusive_{pT,eta,phi}_<species>`
panels from the same tune data; the `multiplicity-spectrum` target is a strict
subset that makes only the first. Both make the identical `DrawOverlay` call for
the multiplicity figure — same directory, same stem, same flags — so nothing is
gained by running the subset separately.

| pinned input | value |
|---|---|
| freeze manifest sha256 | `fcd96eaebd4dc11f071a2c8db8849f6a4cc19b764622a796664e524b27d0fc80` |
| authorization | `docs/HF_RUN3_V1_PUBLICATION_AUTHORIZATION.md`, sha256 `309bd99caeab0e92…` |
| raw base | `/data/alice/ipardoza/hadronization_production/HF_RUN3_V1/raw` |
| ROOT | **6.30/01** |

**The contract line the render must print**, from the actual run:

```
CANONICAL_FREEZE_CONTRACT manifest_sha256=fcd96eae… tunes=3 jobs_per_tune=1000
  events_per_job=100000 events_per_tune=100000000 rows=3000 blocks=10
  validation_log=absent shape=derived
```

> **Every invocation re-checksums all 3000 raw files (~270 GB over NFS), and
> that is deliberate.** It is the same exhaustive verification
> `Validation/validate_canonical_manifest.sh` performs, done by the consumer
> itself. It dominates the runtime — roughly 40 minutes — and **no caching or
> skip mechanism is to be built around it** (owner ruling).

### 9.2 DIGESTS — the corrected render, 2026-08-18

Rendered on `stbc-i3`, wall clock 00:25 CEST 2026-08-18, from the E10 fix
(`29f443f`). The superseded 2026-08-17 render was **overwritten in place** at
the same paths, so no file with a caption-ready name carries the wrong label:

| | before (superseded) | after (this render) |
|---|---|---|
| `Multiplicity/MultiplicitySpectrum_Shared_shape.png` | `4d7ab97ebd19729858e5b63e1dc9de3ff81b2e6f2c18c19560d416c92aa4ac52` | `7385fbdfa4616d8fe445e69b91de251853a4ba5d2cadcfe3297c8b04c195343d` |
| mtime | 2026-08-17 23:25:17 | 2026-08-18 00:25:36 |
| size | 91 687 B | 94 742 B |
| η caption | `\|η\| ≤ 4` ← wrong | `\|η\| ≤ 1, primary charged, heavy flavour excluded` |

**Contract line printed by this run**, verbatim:

```
CANONICAL_FREEZE_CONTRACT manifest_sha256=fcd96eaebd4dc11f071a2c8db8849f6a4cc19b764622a796664e524b27d0fc80
  tunes=3 jobs_per_tune=1000 events_per_job=100000 events_per_tune=100000000
  rows=3000 blocks=10 validation_log=absent shape=derived
COMMON_MULTIPLICITY_BOUNDARIES_CONSUMED sha256=3b0554fe6c291a26ba03b0524975892754e9a0e75896b203c24d05e853d195b5
  classes=11 label_provenance=MONASH_MB_recomputed
```

Per-tune, from the same log: **1000 files and 100 000 000 tree entries each**;
selected particles MONASH 39 421 891, JUNCTIONS 37 697 473, CLOSEPACKING 36 150 008.

#### Figure 4 — shared charged-multiplicity spectrum ❌ SUPERSEDED

> **These two rows are historical.** They are the 0-dp-inset render. Superseded
> **2026-08-18 01:20:19** by the 1-dp re-render — see §9.4. The physics,
> caption, √s and closed loop were all correct here; **only the inset precision
> changed**. Retained so the supersession chain is readable, **not for quotation**.

| file | sha256 | status |
|---|---|---|
| `Multiplicity/MultiplicitySpectrum_Shared_shape.pdf` | `800a97b43d6fe9e937ede31ad259aaec54809b25c7aca9c5c7af9a213284f6e3` | ❌ superseded by `23e170bc…` |
| `Multiplicity/MultiplicitySpectrum_Shared_shape.png` | `7385fbdfa4616d8fe445e69b91de251853a4ba5d2cadcfe3297c8b04c195343d` | ❌ superseded by `c9683cee…` |

#### The 30 per-species panels (60 files) ⏳ SUPERSEDED-PENDING

> **These 60 rows are on notice.** The panels carry no √s and no acceptance
> statement (§9.3), and the caption fix re-renders all 30. **Every digest below
> will change.** They are recorded as the pre-fix baseline, so the supersession
> is checkable rather than asserted.
>
> The table digests **png and pdf only** — 60 files, not the 90 that would
> include each panel's generated `.C`.

| file | sha256 |
|---|---|
| `Inclusive/eta/Inclusive_eta_Bminus_shape.pdf` | `44682263ea63c89fead8a7530afa403bf1cf1abd2f1d044080b95d70cc41f24d` |
| `Inclusive/eta/Inclusive_eta_Bminus_shape.png` | `42ab5b0161839fda02443c80a25e684e1f36ee441ab093ad9f1760f37e8a9de4` |
| `Inclusive/eta/Inclusive_eta_Bplus_shape.pdf` | `10fe4cb02d9c0fae8a504dbeb59d9a09babec1afd734399a4d443faa2c468f9c` |
| `Inclusive/eta/Inclusive_eta_Bplus_shape.png` | `4ca0ce5e51bef6b94e3fe54e3082ffc5314c43782e7e89e0a929d48dd487daf3` |
| `Inclusive/eta/Inclusive_eta_Dminus_shape.pdf` | `21f52698991eaf4002cf8ead430dc72de37e7de950201a676b3ec8f856ec0454` |
| `Inclusive/eta/Inclusive_eta_Dminus_shape.png` | `53dadea1494a743eb94d3f2e43c967ff16b2c5cd4baa2c6a8f19340d374dcbd0` |
| `Inclusive/eta/Inclusive_eta_Dplus_shape.pdf` | `283f632d2087374b37e53cef6822156a9e3a16184215057f98aa5c4e705a0f26` |
| `Inclusive/eta/Inclusive_eta_Dplus_shape.png` | `61fa2ca6d8167ac2673c41438fd4a55a0cbc1488989cc22ea200cb1264613f36` |
| `Inclusive/eta/Inclusive_eta_Lambdab_shape.pdf` | `aaea503da7e859b4104e4ff6de0be2f8525c0d5fdb7952b48900649e4c6da856` |
| `Inclusive/eta/Inclusive_eta_Lambdab_shape.png` | `5416af10eb404b276bea7ae5a1ce0c08ecc0b14e0cc7fb25117152305a497345` |
| `Inclusive/eta/Inclusive_eta_Lambdabbar_shape.pdf` | `bb45a4a65dbcc5c72f7b50598b07c07e534465c6a956042a82aad22211e0869e` |
| `Inclusive/eta/Inclusive_eta_Lambdabbar_shape.png` | `d1278863540f681560b4f4c302fa38a1187311876b4d77075f0ba168b9edbd1d` |
| `Inclusive/eta/Inclusive_eta_Lambdacplus_shape.pdf` | `26189df117b0318ade043f11d459ab2b1c1fa15df771f159875a0dc9f86808e9` |
| `Inclusive/eta/Inclusive_eta_Lambdacplus_shape.png` | `3ca360f2057641bdc4d8d859b16692588142f40db3b3530528ffa03e076279f9` |
| `Inclusive/eta/Inclusive_eta_Lambdacplusbar_shape.pdf` | `6801c65e201bf0a775b50d853e06385ddb177c7d80718604b5307b2db3e25922` |
| `Inclusive/eta/Inclusive_eta_Lambdacplusbar_shape.png` | `30cdd6aeb245d060a751e5de9737b2c78e1d498d5493dcb06aaf306117bae71e` |
| `Inclusive/eta/Inclusive_eta_Sigmabzero_shape.pdf` | `06f04bc28355324b47dd20c63d4cfa119f424f5344ee0c9a5aaa9932cf51b2c7` |
| `Inclusive/eta/Inclusive_eta_Sigmabzero_shape.png` | `aecc91e16d79cb5d7cdfabb018a5bc481b0a6929ad36d3e70aed72a709d3bcce` |
| `Inclusive/eta/Inclusive_eta_Sigmabzerobar_shape.pdf` | `8b6078757f72400f39feddd46a4f4fc52b3d79c763500183e033c6720719d019` |
| `Inclusive/eta/Inclusive_eta_Sigmabzerobar_shape.png` | `0dc52cf2c2a1beab77394edea056759465cb25a3d78567d12c9e40f38a1d0066` |
| `Inclusive/pT/Inclusive_pT_Bminus_shape.pdf` | `f53436c5a007b5c160ccdc3a8710d955c5474c9fac39f9ba8dcf4d0e7df23895` |
| `Inclusive/pT/Inclusive_pT_Bminus_shape.png` | `97628d69eae5b9fabfac33331bf2d5330850512ee2083cb2a929bc8b92e7ef2f` |
| `Inclusive/pT/Inclusive_pT_Bplus_shape.pdf` | `f57b2187dbd79c077e370322c4831600aa642793ed1003764ce85ce42d8d638c` |
| `Inclusive/pT/Inclusive_pT_Bplus_shape.png` | `58b8890084970e7c9e73b703a94c8a20183b411e1ce12fb7a48acdf143212902` |
| `Inclusive/pT/Inclusive_pT_Dminus_shape.pdf` | `344c0e184dbfe2310631be9f9aeb893c7c122460eff54724ccb2b24fb994cd1a` |
| `Inclusive/pT/Inclusive_pT_Dminus_shape.png` | `64685fe2323269efaf74aa9042cf73a0b833c9798e9cd369ad5b9470e1ee2320` |
| `Inclusive/pT/Inclusive_pT_Dplus_shape.pdf` | `22d0b34670f6a7fdbc3d55a0b2a41efd09b9aec6f57bb5ef2f08816e9bf9646c` |
| `Inclusive/pT/Inclusive_pT_Dplus_shape.png` | `f1075bc9726cfdb93dceb9309616b10f913162b926d68f4f535c3d751383a3bb` |
| `Inclusive/pT/Inclusive_pT_Lambdab_shape.pdf` | `204ef5c5dd0a4482b2fab2dc62698c1fbf6d2d032565472ea54808db76b396a6` |
| `Inclusive/pT/Inclusive_pT_Lambdab_shape.png` | `153b950ff375f9fcb4b2e98e95b3c41a7884537d67922362d7ae788ac185b253` |
| `Inclusive/pT/Inclusive_pT_Lambdabbar_shape.pdf` | `480a93f6e3aa380cb8b5741310435733543b1456ea17706e8216012867827169` |
| `Inclusive/pT/Inclusive_pT_Lambdabbar_shape.png` | `2eaee94c42d4b3f05f4b861f28e5e2c3e23c887a736efb0d1086c75794e81501` |
| `Inclusive/pT/Inclusive_pT_Lambdacplus_shape.pdf` | `af5d35d58342a780061077f148e8389a85222cba7bde9d8bced906fcf5396163` |
| `Inclusive/pT/Inclusive_pT_Lambdacplus_shape.png` | `6312e8d64f15bbe1cec68de540707cabc89dfcea2679913806e946e17c052ab1` |
| `Inclusive/pT/Inclusive_pT_Lambdacplusbar_shape.pdf` | `7b04a62f1d259a73eb553aaca6f76c2a77c97468d8d0b5e384b21ceff0cbd375` |
| `Inclusive/pT/Inclusive_pT_Lambdacplusbar_shape.png` | `c1005e5818cff75302cf49f0964a036c3599d4e8cb5b58672c1fe6ea04ac27f0` |
| `Inclusive/pT/Inclusive_pT_Sigmabzero_shape.pdf` | `9881a36c4ec5dfe05c36045f4736ce89a29188c2591aede0f78a51ebbb2dfbf8` |
| `Inclusive/pT/Inclusive_pT_Sigmabzero_shape.png` | `3708ab148c63d07d8435d59f5e0aafba62d153e45f39ea6245991b7f2937e732` |
| `Inclusive/pT/Inclusive_pT_Sigmabzerobar_shape.pdf` | `6a95c2768026202121c1be970769f513c55a97b305dfd91ef73c27925b48a3cd` |
| `Inclusive/pT/Inclusive_pT_Sigmabzerobar_shape.png` | `e4cfc113c41d063c59e25511866e0a9e8940ed37c9c4d619db3f79daddebfe9d` |
| `Inclusive/phi/Inclusive_phi_Bminus_shape.pdf` | `b8fa054a12bb5c8c63c7b16f1899efcb25676f32f749cbc0036e6915022963e2` |
| `Inclusive/phi/Inclusive_phi_Bminus_shape.png` | `dd1c432500550bbd79e787b2389ea60a25e5c6eef36747cacd5adfc161502522` |
| `Inclusive/phi/Inclusive_phi_Bplus_shape.pdf` | `66da34dea0bdc897172118f129e15cc013056af7e205f879839f0d3966a676dc` |
| `Inclusive/phi/Inclusive_phi_Bplus_shape.png` | `fe37753f178a8afe83f390d02881674e201005de3f08efa98df576615e522a54` |
| `Inclusive/phi/Inclusive_phi_Dminus_shape.pdf` | `05770bb7764b37259fbe5bbb3cdeebd5b96780f32268d4e32905a8d7ad40296a` |
| `Inclusive/phi/Inclusive_phi_Dminus_shape.png` | `3761304dbc59493ff4b46bd18beea31df9d7be3d232d4b673e209cb9f06e1956` |
| `Inclusive/phi/Inclusive_phi_Dplus_shape.pdf` | `79ccd873bac6cc9b5c278ad44a25a2f89a9fe87a746aa4763e84c167711e4cf9` |
| `Inclusive/phi/Inclusive_phi_Dplus_shape.png` | `07fdb70e97865eaa6421da664ba674f7ddb793b6059d6655dfdb36031caeec1b` |
| `Inclusive/phi/Inclusive_phi_Lambdab_shape.pdf` | `f5c1410467e405177b1af82b93f0eee050f643428d1afd58a3edd3a61266045f` |
| `Inclusive/phi/Inclusive_phi_Lambdab_shape.png` | `2f1343bba499256a39858339b340e63cd79ccfc71d5925face15ecb50ce2604e` |
| `Inclusive/phi/Inclusive_phi_Lambdabbar_shape.pdf` | `cafe0bdbfa5d7aa1fea2d2e7d83ef26a16360de901816c79479a85c398e56eb9` |
| `Inclusive/phi/Inclusive_phi_Lambdabbar_shape.png` | `c8a8f7cdd63342cce84948270828f4ba11680fbedc5ab68cfbaa14ece3166f7e` |
| `Inclusive/phi/Inclusive_phi_Lambdacplus_shape.pdf` | `25b225c18edeb63fdcf1f616175ad8e8510abbe274635b689a48f0bc3db95080` |
| `Inclusive/phi/Inclusive_phi_Lambdacplus_shape.png` | `df90c4001743e9c29405331f8ac3327b5266f232ed1335fe83069f18bf11e6b7` |
| `Inclusive/phi/Inclusive_phi_Lambdacplusbar_shape.pdf` | `c3b3cbc04591dd00aab3da340033648f0f1e46f6c0f82c5073182be201f5d850` |
| `Inclusive/phi/Inclusive_phi_Lambdacplusbar_shape.png` | `310bdaa5970d7955ef52e8d35daf36c2bfa30e742c8ed91fd9f7ae5adb7a6d62` |
| `Inclusive/phi/Inclusive_phi_Sigmabzero_shape.pdf` | `28cc13a7695ef428792832e847c4b69ee8ae10a16c0ddc6e0c09ae508800903e` |
| `Inclusive/phi/Inclusive_phi_Sigmabzero_shape.png` | `0595c100e1235496361943d6dd71310ec2734be643d4a81c4ba0c459122d27a7` |
| `Inclusive/phi/Inclusive_phi_Sigmabzerobar_shape.pdf` | `874831b69247ef7b522f0b24dbbc24876ffeca2a9c2315adb07759bc525c54ff` |
| `Inclusive/phi/Inclusive_phi_Sigmabzerobar_shape.png` | `22fbce49585e2678d35637b07c36b8db1026cab6303e3b08abb4acfb68009a73` |

### 9.3 CAPTION-READINESS — what these digests are, and are not

A digest freezes bytes; it does not certify a caption. Against paper-checklist
section D, this render splits into two groups.

**Figure 4 — caption-ready on the E10 axis, with ONE outstanding amendment.**
Verified by opening the PNG and by extracting every text primitive from the
ROOT-generated `.C`. It carries, verbatim:

```
PYTHIA 8
pp, #sqrt{s} = 13.6 TeV
#it{p}_{T} > 0.15 GeV/#it{c}
|#eta| #leq 1, primary charged, heavy flavour excluded
```

E10 is fixed on the figure. Two things remain, neither a defect in the drawn
numbers:

1. **The inset percentiles are still at 0 decimals** — `88-100%`, `81-88%`,
   `66-81%`, `60-66%`, `50-60%`, `43-50%`, `35-43%`, `26-35%`, `17-26%`,
   `8-17%`, `0-8%`. Amendment (i) landed **after** this render started, so it is
   not in these bytes. Note `60-66%` and `50-60%`: at 0 dp, class c4's lower
   edge and c5's upper edge both print as `60`, which is exactly the collision
   that made E9's 59.9 → 59.8 correction invisible. **A re-render is required
   before figure 4 is quoted with the corrected class labels.**
2. `%g` on `kMultiplicityEtaCentral` renders **`|η| ≤ 1`**, not `|η| ≤ 1.0`.
   The value derives correctly from the counter's constant, which is E10's
   point; whether the manuscript wants the trailing decimal is an owner call.

> ### ✅ ITEM 1 CLOSED — re-rendered 2026-08-18, amendment (i) applied
>
> The re-render completed and passed its gate. **The inset now carries all
> eleven classes at one decimal**, read out of the generated `.C`:
>
> ```
> 88.2-100.0%  80.6-88.2%  65.9-80.6%  59.8-65.9%  50.3-59.8%  43.0-50.3%
> 34.6-43.0%   26.2-34.6%  17.1-26.2%  8.4-17.1%   0.0-8.4%
> ```
>
> **`59.8-65.9%` and `50.3-59.8%` are now distinguishable**, which is the whole
> point of amendment (i): at 0 dp both edges printed `60` and E9's correction was
> invisible on the figure. The η caption is unchanged and still derived from
> `kMultiplicityEtaCentral`.
>
> **These digests supersede the `7385fbdf…` set above for figure 4:**
>
> | file | sha256 |
> |---|---|
> | `Multiplicity/MultiplicitySpectrum_Shared_shape.png` | `c9683cee4ff85fe51d0e51b45058ba12caf4d3c8ffd3d3c406bd3715f20d42a8` |
> | `…_shape.pdf` | `23e170bcba4a34124b949d46ec0a990a946b954a1ec2f856b1990596dd581e25` |
> | `…_shape.C` | `c44b074455004b06a9cf276c1790811d00a2c8838362cf56a6697ae9ee076486` |
>
> **Item 2 (`|η| ≤ 1` vs `|η| ≤ 1.0`) remains open and is an owner call.**
>
> ⚠ **The PDF digest is not reproducible.** Rendering the same canvas twice from
> identical inputs gives a byte-identical **PNG** and a differing **PDF**
> (`6aca1aa0…` → `817d6c72…` on the polish canvas), because a PDF embeds a
> creation timestamp. **Byte-reproducibility claims must pin the PNG.** The
> three-tune reference reproduced exactly in an earlier session because the PNG
> happened to be the file compared — right by luck, now by rule.

**The 30 per-species panels — NOT caption-ready. New finding, 2026-08-18.**
Every one of the 30 carries **exactly one** text primitive: its own species
title, e.g. `Inclusive generated #it{D}^{+}`. Checked mechanically across all
30 `.C` files:

| check | result |
|---|---|
| panels containing a `13.6 TeV` string | **0 / 30** |
| panels stating status 81–89 / direct primary hadronisation products | **0 / 30** |
| panels stating `pT > 0.15` or `\|η\| ≤ 4` | **0 / 30** |
| panels carrying any text beyond the species title | **0 / 30** |
| species labels in physics notation, not routing identifiers | **30 / 30** ✅ |

The cause is structural, not accidental: `DrawSimulationInfoBlock` has exactly
**one** call site, inside the multiplicity branch of `DrawOverlay`. The species
panels never had an info block to omit.

This contradicts the run record's §1.2, which prescribes the wording these
panels are to carry — *"inclusive spectra of direct primary hadronisation
products (status 81–89), pT > 0.15 GeV/c, |η| ≤ 4.0"* — and it matters more
than usual here, because §1.2 also rules that the acceptance must be presented
as the spectrum's **domain**. The drawn domains do exactly that and are correct
(η spans exactly ±4 on all ten, φ exactly ±π, pT displayed through 50 GeV/c),
but nothing on the panel says so.

**Not fixed in this session.** The pre-authorised polish was enumerated as
amendments (i) and (ii) with "no other visual changes", and adding a caption
block to 30 paper figures is neither. It is recorded here as an owner decision,
and the §9.2 digests are entered as *bytes rendered*, not as *figures cleared
for quotation*.


---

## 9.4 CURRENT DIGESTS — reconciled 2026-08-18

Two sessions worked this figure family in overlap. This section is the single
place to read what is current; §9.2 is retained as the superseded baseline.

### 9.4.1 Figure 4 — the 1-dp re-render ✅ CURRENT

`plotting/run_paper_plots.sh multiplicity-spectrum`, wrapper PID 1060713 on
`stbc-i3`, completed **2026-08-18 01:20:19 +0200**. Log `fig4_render2.log`
carries exactly one `CANONICAL_FREEZE_CONTRACT` line and one completion marker
— a single clean run, not a re-entry.

| file | sha256 | supersedes |
|---|---|---|
| `Multiplicity/MultiplicitySpectrum_Shared_shape.png` | `c9683cee4ff85fe51d0e51b45058ba12caf4d3c8ffd3d3c406bd3715f20d42a8` | `7385fbdf…` |
| `Multiplicity/MultiplicitySpectrum_Shared_shape.pdf` | `23e170bcba4a34124b949d46ec0a990a946b954a1ec2f856b1990596dd581e25` | `800a97b4…` |
| `Multiplicity/MultiplicitySpectrum_Shared_shape.C` | `c44b074455004b06a9cf276c1790811d00a2c8838362cf56a6697ae9ee076486` | `b99b5523…` |

**Verified this session, not inherited:**

| check | result |
|---|---|
| contract line | `manifest_sha256=fcd96eae… tunes=3 jobs_per_tune=1000 rows=3000 blocks=10` ✅ |
| per tune | 1000 files, 100 000 000 multiplicity entries, all three ✅ |
| boundaries artifact consumed | `3b0554fe…`, `classes=11 label_provenance=MONASH_MB_recomputed` ✅ |
| inset precision | **1 dp on all eleven**; `59.8-65.9%` and `50.3-59.8%` are distinct ✅ |
| caption | `\|#eta\| #leq 1, primary charged, heavy flavour excluded` ✅ |
| √s | `pp, #sqrt{s} = 13.6 TeV` ✅ |
| closed loop vs frozen receipt | worst \|Δ\| = **0.000465**, tolerance 0.0005, **PASS on all 11** ✅ |

The 1-dp labels are *derived*, not transcribed: c4's `59.8-65.9%` comes from
`59.849561 → 59.8` and `65.937284 → 65.9` at the generator's single precision
constant. **At 0 dp both c4's lower edge and c5's upper edge printed `60`**, so
E9's correction was invisible on the very figure it corrected. That is now
visible.

> **Open, owner call:** `%g` renders `|η| ≤ 1`, not `|η| ≤ 1.0`. The value
> derives correctly from `kMultiplicityEtaCentral`; only the trailing decimal is
> in question.

### 9.4.2 Polish-proposal canvas — FINAL, gate PASSED ✅

The balancing canvas with amendments (i) and (ii) applied. Written to
`plotting/Plots/PolishProposal/`, 2026-08-18 00:49:29.

| file | sha256 |
|---|---|
| `…_THREETUNE_POLISH_PROPOSAL_PNG.png` | `f2973994e803b1382a001294bb50695d48d80cec4c8bc575aa98514ca9354918` |
| `…_THREETUNE_POLISH_PROPOSAL_PDF.pdf` | `817d6c72be6ec110b685caacd28e16f527c3a29b43116283495f46de90cafd69` |
| `multiplicity_boundary_receipt_v1.json` | `b331e0b65acffe894625cec1bc1a2bf3fcfdc0e1fd29b2b3b099488e52c5dba3` |

**Gate status: `completion_status = PASS`.** The receipt is self-consistent —
every sha it claims was recomputed from the file it names:

| receipt field | claimed | recomputed | |
|---|---|---|---|
| `plotter_source_sha256` | `cff0e90fba638fb3…` | `cff0e90fba638fb3…` | ✅ |
| `configuration_sha256` | `0d0bf6d4a4927b48…` | `0d0bf6d4a4927b48…` | ✅ |

`configuration_path` = `plotting/configuration_multiplicity_HF_RUN3_V1_THREETUNE_POLISH_PROPOSAL.json`.

> **Not a committed reference.** This is the owner-evaluation artifact for the
> polish; it becomes a reference only on sign-off.

### 9.4.4 The three-tune reference, re-rendered for the class labels — 2026-08-19

The committed byte-reproducible reference moved because the legend text moved.

| | sha256 |
|---|---|
| old, rendered from the stale-label configuration | `545499157bf7d4a204a157738cd892c5ae8f1668a7d739ad00270e3f9309fcd1` |
| **new, the committed reference** | `8776a1fff6a425a2f3551d56ecb355d9d58b8b182075655f6304d0bdac40caf3` |
| receipt | `7941f21fc49bbdfde85b96d269811328ce9ff7d53edf56477f2969aee3530539`, `completion_status = PASS` |

**The receipt is self-consistent**, both claims recomputed from the files they
name:

| receipt field | claimed | recomputed | |
|---|---|---|---|
| `plotter_source_sha256` | `684555300d2144ba…` | `684555300d2144ba…` | ✅ |
| `configuration_sha256` | `22caef48362e92a7…` | `22caef48362e92a7…` | ✅ |

Both fields were stale before this render, and for different reasons. The
configuration sha moved with the label correction. The plotter sha had been
stale since the figure work changed the macro, and the old receipt still named
`6dace2025d1edf37…`.

**THE LABEL CORRECTION MOVED NO NUMBER.** All 132 `UNCERTAINTY_MATRIX` rows were
compared before and after over `central_yield`, `yield_sem`, `reference_yield`,
`central_triggers`, `block_triggers`, `finite_yields`, `ratio_sem`,
`yield_status` and `status`. **Zero disagreements.**

The comparison is at the precision the less precise log records. The current
macro prints 17 significant figures and the 2026-08-17 render printed six, so a
byte comparison of the two logs reports every row as different and none of it is
a difference in a value. The PNG changes because the legend is drawn on it.

**Regeneration:**

```bash
HADRONIZATION_BASE=<deploy> \
DATASET_SELECTOR=config/dataset_selector_hf_run3_v1.json \
THNSPARSE_COMPLETE_ROOT_CONFIG=plotting/configuration_multiplicity_HF_RUN3_V1_THREETUNE_THnSparse_complete_root.json \
bash plotting/run_paper_plots.sh thnsparse-complete-root
```

The previous output directory is archived rather than overwritten, because the
boundary-receipt gate refuses to overwrite a frozen receipt:
`THnSparseCompleteRoot_HF_RUN3_V1.prelabelfix_20260819T182643`.

### 9.4.3 CONVENTION — the PNG is the sole byte-reproducibility anchor

A PDF embeds a creation timestamp, so re-rendering identical inputs yields a
byte-identical **PNG** and a **differing PDF** — observed directly on this
canvas (`6aca1aa0…` → `817d6c72…`). **Reproducibility claims pin the PNG.**

> **CORRECTED 2026-08-18. This section previously said "the `.C` is generated
> source and is reproducible like the PNG". That was wrong, and it was wrong in
> the direction that matters — it invited a `.C` digest to be quoted as evidence
> of determinism.**
>
> Re-rendering figure 4 from unchanged inputs gave PNG `c9683cee…` **identical**,
> `.C` `c44b0744…` → `bf18e618…` **differing**. The files are the same size and
> differ on **exactly one line**:
>
> ```
> -//=========  (Tue Aug 18 01:20:19 2026) by ROOT version 6.30/01
> +//=========  (Tue Aug 18 02:44:04 2026) by ROOT version 6.30/01
> ```
>
> `TCanvas::SaveSource` stamps its own generation time, exactly as the PDF
> writer does. The claim was asserted from what the artifact *is* — generated
> source, therefore deterministic — rather than measured, which is the same
> mistake in method as E9 and E10 wearing a third costume.

**The rule, corrected:** the **PNG is the only byte-reproducibility anchor**.
The **PDF** and the **`.C`** are *delivery and inspection artifacts*: their
digests identify a delivered file and must never be used to assert determinism.
A `.C` digest changing across two runs is expected and is not evidence of a
changed figure — compare the PNGs, or diff the `.C` ignoring its header line.

### 9.4.3a CONVENTION — presentation changes are previewed before a render pass

A full raw-tree pass costs ~55 minutes of exhaustive re-checksumming that is
deliberately not cached. Spending one to discover that a caption sits on the
legend is waste, and it happened: the species acceptance block was verified
present on 30/30 panels by text extraction and was still illegible, because
**presence and legibility are different checks and neither substitutes for the
other**.

> **Validate a presentation change locally, against the real generated `.C`,
> before committing to a render.** The `.C` reconstructs the canvas with the
> real data, the real legend and the real axis ranges. Copy it, change only the
> coordinates or strings under test, run it under any local ROOT, and look.
> Geometry is what is being checked, so an off-pin ROOT is fine — this is not a
> physics result and no digest from it is ever recorded.

Used to place the acceptance block bottom-left (`f5d93b1`): the pT panel is the
tightest case because the curve sweeps the lower left on a log axis, and the
preview showed the text clearing it by about 0.05 in NDC before any cluster time
was spent.

### 9.4.4 What is NOT recorded here, and why

An inherited summary described the species panels as "90 files, rollups
`ba6e0bed…` / `857f29df…` / `639942e9…`". **No such digests exist in this
repository, and no 90-file rollup was ever written** — §9.2 holds 60 individual
rows, png and pdf only. Those three values are therefore **not** entered
anywhere: a digest is quoted only for a file that exists, from a run that passed
its own gate.

### 9.4.5 The 30 species panels — CAPTIONED, render #3, 2026-08-18

Supersedes the 60 rows in §9.2, which were the pre-caption baseline.
`plotting/run_paper_plots.sh kinematic-spectra`, wrapper PID 2949209 on
`stbc-i3`, completed 10:12:20 +0200. Per tune: 1000 files, 100 000 000 tree
entries, selected particles MONASH 39 421 891 / JUNCTIONS 37 697 473 /
CLOSEPACKING 36 150 008 — **identical to the pre-caption pass**, so the
caption work did not touch the physics.

**Verified, both checks, because presence and legibility are different things:**

| check | result |
|---|---|
| panels carrying √s, status window, pT and η | **30 / 30** ✅ |
| occurrences of the forbidden word *prompt* | **0** ✅ |
| block placed bottom-left (NDC y = 0.400, 0.356, 0.312, 0.268) | ✅ all panels |
| eyes-on pT / η / φ — legible, clear of legend and data | ✅ |
| φ flatness re-check | ✅ flat, all three tunes ~0.010 |
| **fig 4 PNG unchanged by this pass** | `c9683cee…` **byte-identical** ✅ |

The drawn block, verbatim:

```
PYTHIA 8
pp, #sqrt{s} = 13.6 TeV
direct primary hadronisation products (status 81-89)
#it{p}_{T} > 0.15 GeV/#it{c}, |#eta| #leq 4
```

Every constant derives from the symbol the filling predicate evaluates —
`kCentralPtMinAssociate`, `kCentralEtaAbsMax`, `kDirectPrimaryStatus{Min,Max}` —
after `5f3f381` refactored those predicates off their literals. See E10's
refinement: same value is not same symbol.

#### Figure 4 (unchanged, listed for the chain)

| file | sha256 |
|---|---|
| `Multiplicity/MultiplicitySpectrum_Shared_shape.pdf` | `d11494f02c654def26abf8a3467d1edcca0a4981d32140c5b2c9178be41ef77f` |
| `Multiplicity/MultiplicitySpectrum_Shared_shape.png` | `c9683cee4ff85fe51d0e51b45058ba12caf4d3c8ffd3d3c406bd3715f20d42a8` |

#### The 30 captioned panels (60 files)

| file | sha256 |
|---|---|
| `Inclusive/eta/Inclusive_eta_Bminus_shape.pdf` | `62406d3b3a48fd19d0797a2737a2b18d8a7d129b86c755382f8da64544166ec9` |
| `Inclusive/eta/Inclusive_eta_Bminus_shape.png` | `5ebc62558de4c82e4e7b4ad31c391226e7a3aead8471ac685bf80d77f1a527cc` |
| `Inclusive/eta/Inclusive_eta_Bplus_shape.pdf` | `37a1d3ec16052c87ddcff05d262d47c12fa2835facaf388f12cad2c875397aa0` |
| `Inclusive/eta/Inclusive_eta_Bplus_shape.png` | `d653fa3dc9ab89307e69ca3e5978186b887484ee6e590b2fd15f0650736a4a37` |
| `Inclusive/eta/Inclusive_eta_Dminus_shape.pdf` | `0027bd5ab7054aaf70e5cb20b4f64c5a35d673ced4311490c0d9ae028510d6af` |
| `Inclusive/eta/Inclusive_eta_Dminus_shape.png` | `4a1d7d19c7748864fedc04ba7d07a9284c2fb51aa102674cd1d5b71f239edd7e` |
| `Inclusive/eta/Inclusive_eta_Dplus_shape.pdf` | `113e5151a1ef00fc0c2d030960138f3b5f729bba817d33c2ddff0aab2d84adeb` |
| `Inclusive/eta/Inclusive_eta_Dplus_shape.png` | `395d8aa63ec96eaac3f650d2befb1c9d9a612c80ed5089aa298ec14a69a54f94` |
| `Inclusive/eta/Inclusive_eta_Lambdab_shape.pdf` | `747d9758ccbed6bd35b7aa1151bfea0e1d27727c23e37041cf1e2c43ec99656d` |
| `Inclusive/eta/Inclusive_eta_Lambdab_shape.png` | `8ca2379360c01f5c9409dee4dbae2625b92809009de1158574d3e55a98abdbfe` |
| `Inclusive/eta/Inclusive_eta_Lambdabbar_shape.pdf` | `e5544d76c910556d9bf335b6f3602292864033ac0c35604d828427d8b3a84d8d` |
| `Inclusive/eta/Inclusive_eta_Lambdabbar_shape.png` | `12c9b34ddf05360d99c6490b8479e03787716872344091504a4013bfc8f61ed5` |
| `Inclusive/eta/Inclusive_eta_Lambdacplus_shape.pdf` | `bbd561b2d9d452284fc9f1ad4a6d534948a4021da7c5b42f7936287f2a494839` |
| `Inclusive/eta/Inclusive_eta_Lambdacplus_shape.png` | `ab9ef94c6794390617889ed9a728b8540e13f4611b8162a4ce0c8c1efd07f959` |
| `Inclusive/eta/Inclusive_eta_Lambdacplusbar_shape.pdf` | `93d84ca4f0519231e3f6bf1dfad05fac60b90ae458a74c5e787cea83eae88de1` |
| `Inclusive/eta/Inclusive_eta_Lambdacplusbar_shape.png` | `d36cc6501fb0cb539b51751a98f2414168e93a3203cf377defe37537da9e1b04` |
| `Inclusive/eta/Inclusive_eta_Sigmabzero_shape.pdf` | `8a141b48acf2468b07a954c17a8ef97c7f1d6ade1a147e95be9c88644e8ba78e` |
| `Inclusive/eta/Inclusive_eta_Sigmabzero_shape.png` | `a8694dcfe9c1d87090bfc70e9c2f20166ff92ba9cbd109d2d188f33b6be36af2` |
| `Inclusive/eta/Inclusive_eta_Sigmabzerobar_shape.pdf` | `42581eaf243f7eb8401805593c1474148bbb89b1152a2d8e217cb4a8f309ec7e` |
| `Inclusive/eta/Inclusive_eta_Sigmabzerobar_shape.png` | `00a3ff01036471315e6681c80e9736e0fe0aba404f843e3bb18b6d7bea35e515` |
| `Inclusive/pT/Inclusive_pT_Bminus_shape.pdf` | `aa2040c15ef99ec160ddc0253e1a41936e15bdb9a9ac0ae9ea1e2716514cb3fc` |
| `Inclusive/pT/Inclusive_pT_Bminus_shape.png` | `14e22dff2c3154fad5bb6128c4b4db99ab7157d7eff565820fa6f6cb32af565d` |
| `Inclusive/pT/Inclusive_pT_Bplus_shape.pdf` | `c865f8ab2b61d11480f0de07adac0d39293b7d316074598eeedb4b34eac9faa4` |
| `Inclusive/pT/Inclusive_pT_Bplus_shape.png` | `d69e3171f2f471788c8367735ccd9e8c9c8544565402aacd8105b2ea97bdbcc0` |
| `Inclusive/pT/Inclusive_pT_Dminus_shape.pdf` | `9062438b3b204e63f1ad53366bf01d753bbec44614cb582f5da4218b8cd2e7c3` |
| `Inclusive/pT/Inclusive_pT_Dminus_shape.png` | `ed06838d1fc22ca7860a9d87fb543811e256f9bc38e79fb390413dcc77f32890` |
| `Inclusive/pT/Inclusive_pT_Dplus_shape.pdf` | `5dce044bf95a529b9988275418f0dbfb5c28d292fc1bc3506cf574bdc6b569eb` |
| `Inclusive/pT/Inclusive_pT_Dplus_shape.png` | `f664cdbac40773d82668e6fa65dec626b2c1584729f970665221a749e88228e7` |
| `Inclusive/pT/Inclusive_pT_Lambdab_shape.pdf` | `1abdf14c1df436c9ba5240c240b7170ce3be08dbdb0c90f3bc35c9648f5c4169` |
| `Inclusive/pT/Inclusive_pT_Lambdab_shape.png` | `6e2489bb645eb4c8445d4bede8d396ff4a1bfe492ec79c73f5422551837e3b57` |
| `Inclusive/pT/Inclusive_pT_Lambdabbar_shape.pdf` | `40839bfe55010a5615204d0c21da4c466c86f3c31ab8e81d064058eac7c97c74` |
| `Inclusive/pT/Inclusive_pT_Lambdabbar_shape.png` | `7954644d8850ecacf42ba66c62298908906771ec312f683be7fe8a2f9fba59e2` |
| `Inclusive/pT/Inclusive_pT_Lambdacplus_shape.pdf` | `48bccb4cfe80895f95c7534f19684978e4973cfff9fb893b5fb0f2bb57f54810` |
| `Inclusive/pT/Inclusive_pT_Lambdacplus_shape.png` | `65b633ee4c400f84fe984028eff88836982136ebe968089af232ddc9901c814c` |
| `Inclusive/pT/Inclusive_pT_Lambdacplusbar_shape.pdf` | `7f57ca14cba14489ee45202697035d9b83975940ba4d65d028aa362f79a0fac7` |
| `Inclusive/pT/Inclusive_pT_Lambdacplusbar_shape.png` | `4bc89d44cacae40260d79d904f7dd3b51422e30c751c00772db4dccd96aac866` |
| `Inclusive/pT/Inclusive_pT_Sigmabzero_shape.pdf` | `6c3dd76233db07ba04a4a36629e8183075c2dc27cc55fc13d019dd62af6d76f9` |
| `Inclusive/pT/Inclusive_pT_Sigmabzero_shape.png` | `2345bf310d815339972f85207bd813384cd12d2e9a2f019be2521d1f0b2b8ec9` |
| `Inclusive/pT/Inclusive_pT_Sigmabzerobar_shape.pdf` | `42c1d2898a008a60130bfa90f02e39e83ebd44e72ef2b525a2a012926ffa24f8` |
| `Inclusive/pT/Inclusive_pT_Sigmabzerobar_shape.png` | `ca799f96d584a64fe76a7fa57406a92ef48e0e50d70b3171dddbf73477aeb841` |
| `Inclusive/phi/Inclusive_phi_Bminus_shape.pdf` | `fdfc551062e44c443412b72788ad2ed9d9147addb267c205262162be203c0465` |
| `Inclusive/phi/Inclusive_phi_Bminus_shape.png` | `16cf203cd2eecd2877977cd4a76933ee2609da5a0a4f11a25ff14f2933125637` |
| `Inclusive/phi/Inclusive_phi_Bplus_shape.pdf` | `f4be30340fd42a2ab619483819653d7b6eeafa9d4381cddaa020801347104df2` |
| `Inclusive/phi/Inclusive_phi_Bplus_shape.png` | `e0123755cbe885eaf41220ee3b6d0e79845fc25e6ea47848d07d25e0f81b95ac` |
| `Inclusive/phi/Inclusive_phi_Dminus_shape.pdf` | `58169bf0873b80c238a0930cbd5ee10f71ca9fc0697d26e3e60a5343e67e02bf` |
| `Inclusive/phi/Inclusive_phi_Dminus_shape.png` | `74fbc1834dcd2e4fe90035645bd8af849af2146173f9555b346a63de1234f3ae` |
| `Inclusive/phi/Inclusive_phi_Dplus_shape.pdf` | `c6e82bb061a214f28d7920a795e5b38272997d1fc74e7f79f36e6d23a688dd12` |
| `Inclusive/phi/Inclusive_phi_Dplus_shape.png` | `849f18b8652111445182b309f5b0c2781e88b4237c92c9cc1f136fcd3f72cd08` |
| `Inclusive/phi/Inclusive_phi_Lambdab_shape.pdf` | `06f6101fc2d9db3f5b9ebdbc56f0b2c95912ad0b89cafd430b9df19fc3ad3e07` |
| `Inclusive/phi/Inclusive_phi_Lambdab_shape.png` | `a5366977708f11047fcf165f5caf4c4a84e443e5f1db160b4c13016102a01b71` |
| `Inclusive/phi/Inclusive_phi_Lambdabbar_shape.pdf` | `b45f6a5554dbf8dba94028e2513d46ccbb7b91e47b19c7c0ef27f22f9612fae5` |
| `Inclusive/phi/Inclusive_phi_Lambdabbar_shape.png` | `c4d31a657b8335b0a1222b423af94d6de64654ff6507e13cdf64370a7aed9365` |
| `Inclusive/phi/Inclusive_phi_Lambdacplus_shape.pdf` | `b9a3a9b1324d37eb0abd7aad438c718deecf599c8bd816733956c1634e003238` |
| `Inclusive/phi/Inclusive_phi_Lambdacplus_shape.png` | `5f2beb7d4a124cabea236c41212a195fc3b79a67741b1b723817fedbba67bda4` |
| `Inclusive/phi/Inclusive_phi_Lambdacplusbar_shape.pdf` | `9bf8731f176eb6c80a050c591956154b79128e3bb97762f205dc14066c0bc6e6` |
| `Inclusive/phi/Inclusive_phi_Lambdacplusbar_shape.png` | `7b304e54f8e7c82538ab748c4f652a66148fbed6757e378bd79df0a659ed647a` |
| `Inclusive/phi/Inclusive_phi_Sigmabzero_shape.pdf` | `30339afd299422e518fdcb3eb1dd7aea3bda900559821d67da9e4e922c9f32e8` |
| `Inclusive/phi/Inclusive_phi_Sigmabzero_shape.png` | `6caca8abf44bc3879deecc46a78e56746483bf7a19c1ae3a031e0a1e1b0d4ebe` |
| `Inclusive/phi/Inclusive_phi_Sigmabzerobar_shape.pdf` | `b8569647c593004e34e22c18264e4a57343e3b55cb16c2ee4941ea0a51b58762` |
| `Inclusive/phi/Inclusive_phi_Sigmabzerobar_shape.png` | `2717aa63b61dd729e8bd05de882dfd20841ccd665be1baa29a70d8f1d594dbca` |

---

## 9.5 THE BALANCING-YIELD VARIANT FAMILY — three views, under owner evaluation

Three views of one observable. **None is a down-selection of another**; all three
are developed to publication standard and the choice is the owner's.

All three configure the **full eleven-class axis**, which the axis contract
validates before anything is drawn. V-EXTREMES and V-INTEGRATED differ only in
what they **display**, through the same `bins_to_ignore` mechanism every canvas
family uses, and each declares its own coverage on the figure.

| variant | configured axis | drawn | self-declaration | PNG sha256 | receipt |
|---|---|---|---|---|---|
| **V-FULL** | 11 classes | 11 | *(none — shows the whole axis)* | `f2973994e803b1382a001294bb50695d48d80cec4c8bc575aa98514ca9354918` | `b331e0b6…` PASS |
| **V-EXTREMES** | 11 classes | 2 | `2 of 11 N_ch classes shown: lowest (88.2-100.0%), highest (0.0-8.4%)` | `7b65ecd5f032939a901000ef196596e5324b2d252352ada88691dc20205269d6` | PASS |
| **V-INTEGRATED** | 11 classes **+** integrated | 1 | `multiplicity integrated, 0.0-100.0%` | `f5e146e8baa379f844a4ea38e2e83401761b85099fcba8b150f6dc7218244412` | PASS |

### 9.5.0 Legend amendment — supersession chain, 2026-08-18

The balancing legends never called `SetTextSize`, so ROOT auto-scaled them by row
count in a fixed box: eleven entries small, two larger, **one filling the box**.
`kBalancingLegendTextSize = 0.017` is now set at all four legend sites.

**The value is measured, not chosen.** Rendering V-FULL's own canvas with an
explicit size and comparing PNGs byte-for-byte against the auto-scaled render,
the reproducing plateau is **[0.016, 0.018]** — ROOT quantises to integer font
pixels — and **0.017 is its centre**. The multi-entry reference is therefore
unchanged by construction.

| variant | before amendment | after | changed? |
|---|---|---|---|
| V-EXTREMES png | `ee2b1ccd8a6747c9…` | `7b65ecd5f032939a…` | **yes** — its 2-entry legend was also auto-scaled larger than V-FULL's |
| V-INTEGRATED png | `df82510f54ed70f8…` | `f5e146e8baa379f8…` | **yes** — this is the fix |
| V-FULL png | `f2973994e803b138…` | *(not re-rendered)* | expected unchanged; verified at merge, item C/D of the private merge checklist |

New PDFs: V-EXTREMES `d911ce6d0dafd958…`, V-INTEGRATED `a829c4742df4308a…`.
Both receipts `PASS` with plotter `7187073727dee765…`.

**The values did not move, and that was asserted rather than assumed:** all three
identity assertions were re-run on the NEW renders and report IDENTICAL
(§9.5.2). A legend constant cannot change a number, and this confirms it did not.

> **First attempt was refused, correctly.** Re-rendering into the existing
> directories tripped the receipt gate — *"Existing multiplicity-boundary receipt
> differs; refusing to overwrite a frozen publication definition"* — because the
> plotter sha had changed. **The staged outputs were not promoted and the
> published PNGs kept their original bytes and mtimes.** That is precisely the
> mixed-directory failure `StagedOutputs` was built to prevent, working in
> production. The superseded evaluation artifacts were then **archived, not
> deleted**, as `VariantExtremes.preamendment_20260818T112014` and
> `VariantIntegrated.preamendment_20260818T112014`.

PDFs, recorded to identify the delivered file and **not** to assert determinism
(§9.4.3): V-EXTREMES `dff06d9a5236034c19e4d91ac235f3ae1b38d19594ebf2a82481f54958a7558c`,
V-INTEGRATED `d4ad916fb7d499cfd065aca93eea53c91f5141f19164aeae2862c0fcfb9f3fb2`.

Both new receipts pin `plotter_source_sha256 = a623fdef9131d8ce…` with
`configuration_sha256` `cfa2c5dc08010f9f…` (V-EXTREMES) and
`aedbf4737ea0a6be…` (V-INTEGRATED). Both were promoted only after the gate
passed: `STAGED_OUTPUTS_PROMOTED files=3 after=multiplicity_boundary_receipt_PASS`,
with no staging directory left behind.

### 9.5.1 The recipes — and the variable name that matters

> ⚠ **The target reads `THNSPARSE_COMPLETE_ROOT_CONFIG`, not `THNSPARSE_CONFIG`.**
> Setting the latter is silently ignored and the run falls back to the DEFAULT
> reduced configuration. That happened once, and it was caught only because the
> default declares a v2 pair schema against v3 inputs, so an unrelated gate
> tripped — with a compatible default it would have produced a plausible figure
> from the wrong configuration. **Use the launcher, which hashes the intended
> configuration and compares it to the sha the macro echoes, and dies on a
> mismatch.**

```bash
# on Nikhef, pinned stack, from the deploy
export HADRONIZATION_BASE=<deploy>
export DATASET_SELECTOR=config/dataset_selector_hf_run3_v1.json
source setupEnv.sh

tools/render_balancing_variant.sh \
  plotting/configuration_multiplicity_HF_RUN3_V1_VEXTREMES.json   vextremes.log
tools/render_balancing_variant.sh \
  plotting/configuration_multiplicity_HF_RUN3_V1_VINTEGRATED.json vintegrated.log
```

The launcher prints `RENDER_VARIANT config_confirmed=OK` only when the loaded
configuration sha equals the intended one. Both variants above carry that line.

Configurations are **generated**, never hand-written:
`python3 tools/make_variant_configs.py` (`--check` in the suite via
`tests/test_variant_configs.py` and `tests/test_display_filter.py`).

### 9.5.2 The identity assertions — filtering changed the view and nothing else

Run by `tools/assert_variant_identity.py`, comparing the printed 17-significant-digit
values with **no numeric tolerance**:

| assertion | points | result |
|---|---|---|
| V-EXTREMES vs the 11-class closure run, classes c1 and c11 | 24 | **IDENTICAL**, exact string equality |
| V-INTEGRATED vs the closure run, integrated bin | 12 | **IDENTICAL**, exact string equality |
| V-EXTREMES vs V-FULL (signed off) | 24 | **IDENTICAL at every digit V-FULL's log records** |

The third is a weaker statement than the first two *only because of the log*:
V-FULL was rendered before the macro printed at 17 significant figures, so its
log carries ROOT's default 6. The variant values are re-printed to that
precision and compared exactly — no tolerance is introduced, and a real
disagreement at the recorded precision would still fail. The exact leg is
carried by the closure run, which uses the same eleven-class axis and the
current macro.


---

## 9.6 STYLING MANDATE — the balancing family re-rendered, 2026-08-18

Owner mandate: tune identity is **colour + marker only**, all three tunes draw
**solid**, and line style is reserved for the multiplicity class. Constants live
in `plotting/TunePlotStyle.h` and nowhere else.

| tune | colour | ROOT index | marker | line |
|---|---|---|---|---|
| MONASH | black | `kBlack` = 1 | 20 circle | solid |
| JUNCTIONS | blue | `kBlue+1` = 601 | 21 square | solid |
| CLOSEPACKING | **purple** | `kViolet+1` = **881** | 22 triangle | solid |

Class ladder `ClassLineStyle(i)` = 1…10 for c1–c10 and a registered 11th pattern
(`"40 20 10 20"`) for c11, so **all eleven are distinct**. This replaced the
configurations' `dependency_line_styles` block, which was a second copy of the
axis and had drifted: it gave **c1 and c11 both style 1**, making the two classes
V-EXTREMES draws indistinguishable.

| variant | before styling | after | receipt |
|---|---|---|---|
| V-FULL | `f2973994e803b138…` → `7b65ecd5…`* | `0cf807b6750894c9…` | PASS |
| V-EXTREMES | `7b65ecd5f032939a…` | `63906e847f243c79…` | PASS |
| V-INTEGRATED | `f5e146e8baa379f8…` | `88fdb62845ccbcb6…` | PASS |

\* V-FULL was not re-rendered by the legend amendment; its chain runs
`f2973994…` → `0cf807b6…` (styling).

All three receipts pin plotter `003a39e3997b943f…`; all three promoted only
after the gate (`STAGED_OUTPUTS_PROMOTED files=3 after=…PASS`); no staging left
behind. Pre-styling artifacts archived as `*.prestyle_20260818T114842`.

### 9.6.1 Styling moved no number — asserted, not assumed

| assertion | points | result |
|---|---|---|
| styled V-EXTREMES vs **pre-styling** closure run | 24 | **IDENTICAL**, exact 17-digit |
| styled V-EXTREMES vs **styled** V-FULL | 24 | **IDENTICAL**, exact 17-digit |

> **MERGE_CHECKLIST item D is closed early.** It existed because V-FULL's log
> carried only 6 significant figures, so the V-EXTREMES-vs-V-FULL identity was
> exact only through the closure-run leg. The styled V-FULL logs 17, and the
> direct comparison is now **exact by string equality**. The item can be struck
> rather than carried to merge.
>
> **CORRECTED AT MERGE.** The claim above was true of the DATA and not of the
> TOOL. `tools/assert_variant_identity.py` still ran its V-FULL leg through a
> `compare_rounded` helper that re-printed each value at the source's precision,
> so the assertion it actually made was the weaker one, against a log that had
> carried 17 significant figures since the styling re-render. The leg now uses
> the same exact comparison as the other two, and the rounded helper is deleted
> so it cannot be reached again. All three legs now report exact string
> equality:
>
> | leg | points | result |
> |---|---|---|
> | V-EXTREMES vs the 11-class closure run | 24 | **IDENTICAL**, exact 17-digit |
> | V-EXTREMES vs V-FULL | 24 | **IDENTICAL**, exact 17-digit |
> | V-INTEGRATED vs the closure run | 12 | **IDENTICAL**, exact 17-digit |
>
> The two logs the V-FULL leg names are one file: `polish_render3.log` and
> `vfull_styled.log` share sha256 `05ad157f67c36f60b435…`.

---

## 9.7 THE STYLED KINEMATIC PASS — render #4, 2026-08-18 ⚑ RENDERED, NOT CLEARED

The tune-palette mandate of §9.6 applied to the raw-tree family: figure 4 and the
30 species panels re-rendered so the kinematic figures carry the same tune
identity as the balancing family, plus the owner's transparent inset.

| | |
|---|---|
| invocation | `bash plotting/run_paper_plots.sh kinematic-spectra`, deploy `/data/alice/ipardoza/figure_deploy_20260817` |
| host / PIDs | `stbc-i3`; wrapper **3576674**, `root` 3576748, `root.exe` **3576749**, PGID **3576674** |
| started / ended | 11:48:43 -> ~13:12 CEST, **~84 min** (~44 min re-checksum, ~40 min fill) |
| log | `kinematics_render4.log` |
| sources | `Plot_InclusiveKinematicSpectra_Raw.C` `467bf8ac...`, `TunePlotStyle.h` `6a7a7201...`, `run_paper_plots.sh` `e5e68489...` — **byte-identical to the worktree at `0a8dd9b`** |
| staging | none left behind |

### 9.7.1 Styling moved no number — measured, not assumed

**Every physics quantity is identical to render #3 (SS9.4.5).**

| quantity | render #3 | render #4 | |
|---|---|---|---|
| MONASH selected particles | 39 421 891 | **39 421 891** | OK |
| JUNCTIONS selected particles | 37 697 473 | **37 697 473** | OK |
| CLOSEPACKING selected particles | 36 150 008 | **36 150 008** | OK |
| per tune | 1000 files, 100 000 000 entries | **identical, all three** | OK |
| freeze manifest | `fcd96eae...` | **`fcd96eae...`** | OK |
| boundaries artifact | `3b0554fe...`, `classes=11`, `MONASH_MB_recomputed` | **identical** | OK |

**Contract line printed by this run, verbatim:**

```
CANONICAL_FREEZE_CONTRACT manifest_sha256=fcd96eaebd4dc11f071a2c8db8849f6a4cc19b764622a796664e524b27d0fc80
  tunes=3 jobs_per_tune=1000 events_per_job=100000 events_per_tune=100000000
  rows=3000 blocks=10 validation_log=absent shape=derived
```

**Closed loop, re-verified independently this session** — recomputed from
`config/multiplicity_class_boundaries_v1.json` against the MB anchor
(172 429 events) and compared to the frozen receipt: **worst |D| = 0.000465**
against tolerance 0.0005, **PASS on all eleven**, every per-class residual
reproducing the recorded table to the digit. This check is a property of the
committed artifacts, not of the render, and it did not move.

**Mechanical panel checks — all pass, 30/30:** sqrt(s), status window, pT and eta
each present on 30/30; **0** occurrences of *prompt*; block NDC y unchanged at
0.400 / 0.356 / 0.312 / 0.268; species titles in physics notation 30/30, routing
identifiers 0/30. **Inset precision holds at 1 dp on all eleven classes**, with
`59.8-65.9%` and `50.3-59.8%` distinct. **phi flat at ~0.010, all three tunes.**

### 9.7.2 EYES ON — three presentation findings, all for the owner

> **The mechanical checks all passed and the figures are still not clearable.
> That is the point of eyes-on being a separate check.**

**FINDING 1 — the markers saturate figure 4.** On a ~170-bin spectrum every bin
draws a marker, so the three tunes render as **solid ribbons of overlapping
markers with no histogram line visible at all**. JUNCTIONS' squares and
CLOSEPACKING's triangles merge into continuous bands roughly 4-5x the line
width, and **MONASH — the reference tune — is largely occluded** behind
CLOSEPACKING through the populated range. The apparent tune separation is
inflated by marker size rather than by data.

> **Reported, not fixed.** The mandate that produces this is correct for the
> balancing canvases, where a panel holds two points and markers are exactly what
> distinguishes the tunes. It is the *density* of the kinematic spectra that
> breaks it. **No sparse-marker scheme was improvised — the owner rules.**

**FINDING 2 — the caption text is struck by the data on 4 of the 30 panels.**
Checked on **all 30**, not sampled: chromatic (blue/purple) pixels inside the
measured bounding boxes of the four caption lines.

| outcome | count | panels |
|---|---|---|
| **struck — legibility damaged** | **4** | pT Lc+, Lc-bar, Sb0, Sb0-bar |
| grazing — curve enters the band, glyphs legible | 2 | pT D+, D- |
| clean | **24** | all 10 eta, all 10 phi, pT B+, B-, Lb, Lb-bar |

On the four struck panels the tail of `(status 81-89)` is overlapped by markers
and error bars; on Sigma_b^0 the `-89)` is destroyed. **This is a regression
introduced by this pass**: `f5d93b1` placed the block bottom-left with a preview
showing it clearing the curve by ~0.05 in NDC (SS9.4.3a), and the markers this
pass adds consume that clearance. The pT panels are affected because they are the
log-y case whose curve sweeps the lower left — exactly the tightest case
SS9.4.3a named.

**FINDING 3 — the transparent inset, and what it revealed.** The mandate was to
stop hiding collisions behind an opaque fill. It worked: the main-panel spectra
are now visible crossing the inset's **top-right corner**, which the opaque
version concealed. Two further collisions are visible inside the inset and are
**pre-existing, not caused by the transparency** — both strings were introduced
by `272dd01`, well before it:

1. the inset subtitle **`labels: MONASH min-bias percentiles` is struck through
   by the inset's own top frame line and its tick marks**;
2. the rightmost class label **`0.0-8.4%` is struck through by the inset's own
   MONASH curve**, obscuring the `4%`.

> **These two were present in render #3 and were not caught**, because that
> session's fig-4 eyes-on was directed at the inset's *precision* — the 1-dp
> amendment — and the digest and text-extraction checks it was paired with cannot
> see a line crossing a glyph. Recorded plainly so the record shows when they
> entered, not just when they were noticed.

### 9.7.3 DIGESTS — figure 4, and the supersession chain

| file | sha256 |
|---|---|
| `Multiplicity/MultiplicitySpectrum_Shared_shape.png` | `b65874f1e64ea810d10cfe823a493734e9f59a2ee4d23299fee6fa8290190f3e` |
| `Multiplicity/MultiplicitySpectrum_Shared_shape.pdf` | `69897a82630cf50ab6462f32d553211a4acd805dbbc0894f6e732140b3435fa9` |
| `Multiplicity/MultiplicitySpectrum_Shared_shape.C` | `57cfbf19b583600bd6783a4b5e93205df116bc8645abeb6a171f6563739e726f` |

**Figure 4 chain, complete:** `4d7ab97e...` (wrong eta caption) -> `7385fbdf...`
(E10 fixed, 0-dp inset) -> `c9683cee...` (1-dp inset) -> **`b65874f1...` (styled
palette + transparent inset, THIS render)**.

**The 30 styled panels (60 files)** supersede the SS9.4.5 set entry-for-entry.

| file | sha256 |
|---|---|
| `Inclusive/eta/Inclusive_eta_Bminus_shape.pdf` | `0a4f2cff1a4e2432cdc1669b43f3c4d63dbd40ce2a0aa3adb2c4ebc70ced9668` |
| `Inclusive/eta/Inclusive_eta_Bminus_shape.png` | `a5c844b5252c7952cac9b5796886941a4542604e32dc1f9b7e9fd2021eb1e836` |
| `Inclusive/eta/Inclusive_eta_Bplus_shape.pdf` | `6450d328ea8210d97c3d7a8a985409c4e1a6a89fd92fb509f4807df38bfa3d28` |
| `Inclusive/eta/Inclusive_eta_Bplus_shape.png` | `dedc57760df70060825467aab9b5c0b955ce68d3b67791bc135bc3470100cb25` |
| `Inclusive/eta/Inclusive_eta_Dminus_shape.pdf` | `3c724f4c3585b8d542577c606a42fb14c61b9c76d0a253d5a2978d4b56ed0392` |
| `Inclusive/eta/Inclusive_eta_Dminus_shape.png` | `3b0e78615d84539633614cea246656e6a5075c9f94d9641a39dbe7f679c0e435` |
| `Inclusive/eta/Inclusive_eta_Dplus_shape.pdf` | `9625817f9ff196dc78adcbdc4a18093ba63e586a6a638d83778c8230f0d92ecf` |
| `Inclusive/eta/Inclusive_eta_Dplus_shape.png` | `3e8281b93eea1c6a0df76fe6dae6479afe6e85961550276e0a6138ccb9e7a801` |
| `Inclusive/eta/Inclusive_eta_Lambdab_shape.pdf` | `bfd29f4b08a1a9cac0e2b420aa8168206e52d766111882bb8fab42a95ecb9a82` |
| `Inclusive/eta/Inclusive_eta_Lambdab_shape.png` | `720a2414484ac226409a698a72d584b1553c2e0c830a19c94e0449b3ce980f64` |
| `Inclusive/eta/Inclusive_eta_Lambdabbar_shape.pdf` | `a3c4e6ab066a16e411ab812274daf74b94f369d54c98bc34051f4892beac38ae` |
| `Inclusive/eta/Inclusive_eta_Lambdabbar_shape.png` | `76172daf3c02ddf86dc79ab8f57e89abe7c3a9657e22b18372bf9d7a270a68c1` |
| `Inclusive/eta/Inclusive_eta_Lambdacplus_shape.pdf` | `5865442e075501bbe61e4939343b46598e135ea4ae8d245d0f23caebf595b58b` |
| `Inclusive/eta/Inclusive_eta_Lambdacplus_shape.png` | `c3be44b546ace1b361a37b698432201fc2918524f370629902fab10af3b2860b` |
| `Inclusive/eta/Inclusive_eta_Lambdacplusbar_shape.pdf` | `b12a018b502a9f1535d6d3d610f0256e5f12d4787b5575db5963c8b76edcc7cd` |
| `Inclusive/eta/Inclusive_eta_Lambdacplusbar_shape.png` | `28026fde4342bd45e45a9c5d9f972ddf4180ca9c114bb3626fa0ed8e86802107` |
| `Inclusive/eta/Inclusive_eta_Sigmabzero_shape.pdf` | `a6c7e44a97a83027dd186007bf08815c9c264d85cc301fa1228b93690f806330` |
| `Inclusive/eta/Inclusive_eta_Sigmabzero_shape.png` | `eb787531961a2b9593c5aa85f2e7433b5ea9474ca6e522ce47305f5aa082a358` |
| `Inclusive/eta/Inclusive_eta_Sigmabzerobar_shape.pdf` | `73d6818af0a2e23be1856a76dd82043f1bbbff82bfa0f8b670eb840a6563a447` |
| `Inclusive/eta/Inclusive_eta_Sigmabzerobar_shape.png` | `8a8df0f84cbeda8f1e1f658192ee67910c3a3d43f27a301da8bb1b57731b49b6` |
| `Inclusive/pT/Inclusive_pT_Bminus_shape.pdf` | `bf5cec072c1d93b0a9d3cb95974e413516396b1ff25c4df5de96b048bd2eadb9` |
| `Inclusive/pT/Inclusive_pT_Bminus_shape.png` | `df32271859c056b035056e45e6c4ae0d84a091729e7cc50d7920dd4f8b46224c` |
| `Inclusive/pT/Inclusive_pT_Bplus_shape.pdf` | `05e368af488a94347459e3f72b3e17042bac06395ebd0b1f9de1d9982bf6da3d` |
| `Inclusive/pT/Inclusive_pT_Bplus_shape.png` | `1f83f3bb375889955c26065251f92e524b4b391e987083a56b42c6e2af1739e5` |
| `Inclusive/pT/Inclusive_pT_Dminus_shape.pdf` | `180dce5cf4f5e3ad35863aa3b4051e7f74045b407c78e1315b78c485f06d92b5` |
| `Inclusive/pT/Inclusive_pT_Dminus_shape.png` | `804c47b24d28aa589a541dbd478625189392abf589197d95066224c12d2ee571` |
| `Inclusive/pT/Inclusive_pT_Dplus_shape.pdf` | `b1fdb44249d71152307ff01688ad25d7c836750ebf893c66d9b3555fd4805d52` |
| `Inclusive/pT/Inclusive_pT_Dplus_shape.png` | `2b2cb539be56b9d82d643cc0ecc4323da153c3ff4786887058f6873309de3221` |
| `Inclusive/pT/Inclusive_pT_Lambdab_shape.pdf` | `0352a4f5950293e229d81b432b0aec1fe8a5919b280cdba47ebacc01e1ee4bb4` |
| `Inclusive/pT/Inclusive_pT_Lambdab_shape.png` | `9695904d41e0b390dff354fb4640cf03ecf721c0c14c5ee3161d1de39a60544b` |
| `Inclusive/pT/Inclusive_pT_Lambdabbar_shape.pdf` | `6f469332b09da11f0075faa58c85db3320ec2e68883202ceb450033248570cf7` |
| `Inclusive/pT/Inclusive_pT_Lambdabbar_shape.png` | `76278493873c1715a2108f7e0135394f93ab43faa9a3ad31416cf90f2eb03b20` |
| `Inclusive/pT/Inclusive_pT_Lambdacplus_shape.pdf` | `c65596862140fea0cdf6b942ce2310a55a83e0b5a0f6e63d40cb30611bac69ce` |
| `Inclusive/pT/Inclusive_pT_Lambdacplus_shape.png` | `7503e72998ff456ea0a35d00696e8e99038d73f3079ee5257ef145b5df3cf2b0` |
| `Inclusive/pT/Inclusive_pT_Lambdacplusbar_shape.pdf` | `49e362f8836ff5a51559eda7b6b4379b3bb34117fe82daee4417303be77e5f01` |
| `Inclusive/pT/Inclusive_pT_Lambdacplusbar_shape.png` | `3a8448927462183a2c7746f49d00ca3edbe964d43b30ff00e57af8fc0fdf4551` |
| `Inclusive/pT/Inclusive_pT_Sigmabzero_shape.pdf` | `8ca719fa1ea7e9457e65633e5e0514da1b3a0becad03387c38532119b7028ef3` |
| `Inclusive/pT/Inclusive_pT_Sigmabzero_shape.png` | `a1e2f1571758dc6f2358ad1cd67e73ee7047ce5eaed0890f6d7db8dab65c9fe7` |
| `Inclusive/pT/Inclusive_pT_Sigmabzerobar_shape.pdf` | `4a2febe76721a427a349b03856f1e05bb72e1182d0696d95303c440f7575ec20` |
| `Inclusive/pT/Inclusive_pT_Sigmabzerobar_shape.png` | `e176795f2a4d58549a483460e738996f1810d7a46e41c159478c90ef4718cd2b` |
| `Inclusive/phi/Inclusive_phi_Bminus_shape.pdf` | `b2cb8b31096142e02b273eacf7f6b9e3223a7e31caa7cc425beb48fed955e0c0` |
| `Inclusive/phi/Inclusive_phi_Bminus_shape.png` | `6532a561e8825e5732422bd4735a5b0d0800e0d35b68b0b6862793b05feaca9d` |
| `Inclusive/phi/Inclusive_phi_Bplus_shape.pdf` | `4dce10d367afab8965658550a347234e9984355707e4dc1f9737fcea4be5b5a5` |
| `Inclusive/phi/Inclusive_phi_Bplus_shape.png` | `d87641b2c6de0b7ea0ae9733c9e2a28de48160d806a4eae3aa8aec4783c41774` |
| `Inclusive/phi/Inclusive_phi_Dminus_shape.pdf` | `488388bb2c410650aaa99ff16827bb80f3199d2b1a139df4f1a0e7ba94ac572f` |
| `Inclusive/phi/Inclusive_phi_Dminus_shape.png` | `d55d4456de2c90645619dbe2ee7ce43af69f3c1cb983eb5ba558abc8ac0b72b6` |
| `Inclusive/phi/Inclusive_phi_Dplus_shape.pdf` | `d89d4306a6c2084341d0419b144f04f3d1c4f593e4a240ce86272663fd12812d` |
| `Inclusive/phi/Inclusive_phi_Dplus_shape.png` | `83045b7f0e9fec47cf0b1495779f20ba925ad03bd9915c81075a41c68460244b` |
| `Inclusive/phi/Inclusive_phi_Lambdab_shape.pdf` | `7968cefeab03e4fea3472ff8fc9c7e21792cf485114aef2aa557f21508f7a1e2` |
| `Inclusive/phi/Inclusive_phi_Lambdab_shape.png` | `46cf2c500799ae0057156ad78b30e342a116ecd79628068a1bc2254b52270351` |
| `Inclusive/phi/Inclusive_phi_Lambdabbar_shape.pdf` | `dbfd78fe569678e7a7db83924834c33596854ab41991dcd1532e5fd930302536` |
| `Inclusive/phi/Inclusive_phi_Lambdabbar_shape.png` | `a83a061c907c9182cdd99e4fd52d95bc7ac7a4718079a08cec2927dbc5dee18e` |
| `Inclusive/phi/Inclusive_phi_Lambdacplus_shape.pdf` | `df0b6e780bf6bed7d55c1d765d30d1e8ad46c109c2ee3e7e26475f74eb7f2ee3` |
| `Inclusive/phi/Inclusive_phi_Lambdacplus_shape.png` | `631935b8593546814f1d0d5db56cdd9666eedaabeb52a571b5c641526bfe2714` |
| `Inclusive/phi/Inclusive_phi_Lambdacplusbar_shape.pdf` | `93fc0a6489c825a24443e534d79b008d2aa31ec5ede9dde18da6842c63ea5757` |
| `Inclusive/phi/Inclusive_phi_Lambdacplusbar_shape.png` | `1f345bb1409d581ef3b6b078dda3f1d675191afc555a26febb0c9ff3fa3c32fe` |
| `Inclusive/phi/Inclusive_phi_Sigmabzero_shape.pdf` | `20ec361022c74e5057db95579c50e807039d3ed8e4c5f3fdb0ef08503076ff92` |
| `Inclusive/phi/Inclusive_phi_Sigmabzero_shape.png` | `97a4e71321df287dd6c7dff13ce427559c0a046dd58fe51eaaf201078c753393` |
| `Inclusive/phi/Inclusive_phi_Sigmabzerobar_shape.pdf` | `af85c96893d29087f0068c5edeee8d8830c4523f9b1ba007c9c404f6ed758512` |
| `Inclusive/phi/Inclusive_phi_Sigmabzerobar_shape.png` | `b27f4932b6f0ed3a447258291627ada82a1f0b71fa0ba20164b078e367369e28` |

> **Status: RENDERED, NOT CLEARED FOR QUOTATION.** The bytes are recorded because
> the run passed its own gates and its numbers are unchanged. The three findings
> above are presentation rulings for the owner; figure 4 and the four struck pT
> panels should not be quoted until they are ruled on.

---

## 9.8 THE BARYON/MESON RATIO — built 2026-08-18 ⚑ PROPOSAL, awaiting owner sign-off

The figure `FIGURE_INVENTORY.md` §3.3b said could not be rendered without an
owner presentation ruling. It is rendered here as a PROPOSAL: the quantity, the
axis and the estimator are all derived, and what remains for the owner is whether
this is the figure the manuscript should carry.

| | |
|---|---|
| observable | balancing-yield ratio **Lambda_b / B-** and **Lambda_c-bar / D-**, per multiplicity class |
| configuration | `plotting/configuration_multiplicity_HF_RUN3_V1_VBARYONMESON.json` (GENERATED) |
| launcher | `tools/render_balancing_variant.sh`, `config_confirmed=OK` |
| gate | `STAGED_OUTPUTS_PROMOTED files=3 after=multiplicity_boundary_receipt_PASS` |
| staging left | none |
| **PNG** | **`4d38492feb91ab8fc00f91230e7c8e47b29882f025d32a41e42b80d9fca33201`** |
| receipt | `683fb10ce30b2b0e848c0122abcc00e1dd732abb542f95fc7a5b37e173e65451`, `completion_status = PASS` |

**The denominator is not named in the configuration.** It is resolved at run time
from the pair registry's signed `referenceMesonPdg`, and
`ResolveReferenceAssociateSelection` throws unless exactly one configured
associate carries it. The run confirms the resolution in its own log —
`reference_pdg=-411 reference_index=0` for charm — so the meson divided is the
registry's, not a filename in a config.

**Sigma stays deferred, asymmetrically.** Beauty could be added today
(`BplusSigmabzero.root` and its conjugate are in the freeze, in the short trigger
form this configuration consumes); charm could not, because the D+ trigger has no
Sigma_c counterpart. See `FIGURE_INVENTORY.md` §3.3b.

### 9.8.1 What the figure shows

MONASH is near-level across the class axis while both CR tunes rise with
activity. Beauty **Lambda_b / B-** climbs from ~0.22 in the lowest class to ~0.55
in the highest, against MONASH's ~0.17. MONASH itself declines gently rather than
sitting flat, by −0.02453 ± 0.00739 at 3.3 σ; the double ratio reaches **~3.4**
(JUNCTIONS/MONASH) and **~3.1** (CLOSEPACKING/MONASH). Charm is the same shape,
smaller: **~1.7** and **~1.4**. Baryon enhancement growing with multiplicity is
the paper's claim, and this is the figure that states it per class.

**Eyes on:** tune identity correct (MONASH black/circle, JUNCTIONS blue/square,
CLOSEPACKING purple/triangle, all solid); legend identifies all three tunes and
is clear of the data; the x axis carries the DERIVED percentile classes; the two
tune-ratio panels sit adjacent at the bottom, which is the property the
2026-08-16 ruling refused to give up.

### 9.8.2 Four defects this build exposed, all pre-existing

> **A figure that had never been rendered was not a figure with no problems.**

| # | defect | evidence |
|---|---|---|
| 1 | **SEGFAULT.** Both baryon/meson functions read `vBinsToIgnore[0]` to decide whether anything is ignored — an out-of-bounds read when the list is empty. Fixed by asking `empty()` first | crash on the first render; sibling `drawBalancingPlots` uses `isInVector` and never had it |
| 2 | **CLIPPED double ratio.** The reviewed yield window `[0.6, 2.5]` does not hold the baryon/meson double ratio | the render named the point: envelope `[2.7116, 2.8484]`, `Lambda_b`, `hDPhic9`. Window widened to `[0, 4]` |
| 3 | **Three identical panels, each captioned with a different tune.** The function has no `vCanvasTUNES` filter and draws every configured tune on any canvas | one panel per flavour now, which is the function's actual shape |
| 4 | **Drifted axis label.** `…TUNERatios` was moved onto `DisplayLabelForMultiplicityBin` and still carries the raw-name line commented out beneath the fix; the plain function was left behind | yield panels printed `hDPhic1_MB88p197_100` above ratio panels printing `88.2-100.0%` |

**Defect 2 is the one to keep.** `SetPlotPointOrThrow` turned a paper figure that
would have been silently cropped into a render that refused to finish and said
which point and which class. The y window is therefore evidence, not taste.

---

## 9.9 ANGULAR CORRELATIONS — rendered 2026-08-18, and the family proved untouched

| | |
|---|---|
| configuration | `plotting/configuration_multiplicity_HF_RUN3_V1_VCORRELATIONS.json` (GENERATED, ISOLATED) |
| gate | `STAGED_OUTPUTS_PROMOTED files=9 after=multiplicity_boundary_receipt_PASS` |
| `BEAUTYCorrelations_MONASH_PNG.png` | `cc2abc21b620ea059975c7f7604c9fd8d2903f7aa6b4e50513a7d075e3161f6e` |
| `CHARMCorrelations_MONASH_PNG.png` | `0cc2a0ac71881580f6a04ee6117b876c69bbcb4eb9fee8598b5e04ebd3a409e4` |

**Nothing about these canvases was authored.** Pad layout, log-y and the output
stem are hard-coded in `improvedPlotting_THnSparse.C`, and the stem is exactly
the manuscript's filename. The MONASH label is honest by construction: the draw
is gated on `TUNE == "MONASH"`.

**What DID have to change, and why it is isolated.** The macro's gate names four
OS pair files, and two of them are **baryon-TRIGGERED** — `LambdacplusDminus`
and `LbbarBminus`, the opposite direction to the balancing family's
`D+ -> Lambda_c-bar`. Registering pairs changes the analysed pair set, which
feeds `ResolveReferenceAssociateSelection` and the reference meson the block
uncertainties rest on. So this configuration is separate, writes to its own
directory, and the balancing configurations are untouched.

> **Without those two registrations a flag flip renders a HALF-EMPTY figure and
> reports success** — the canvas has a meson pad and a baryon pad per flavour.
> The generator refuses to emit a configuration that leaves any of the four
> unregistered, so that failure cannot reach a render.

### 9.9.1 THE GUARD — three independent legs, all pass

| leg | result |
|---|---|
| the balancing canvas rendered under this configuration vs the **signed-off V-INTEGRATED** | **BYTE-IDENTICAL PNG**, `88fdb62845ccbcb6…` on both |
| every shared `UNCERTAINTY_MATRIX` value | **14 keys vs 12, 12 shared, ZERO differing** at 17-digit string equality; the two extras are exactly the pairs registered |
| `tools/assert_variant_identity.py`, re-run unchanged | **IDENTICAL** on all three legs, `RC=0` |

The first leg is the strongest available statement, because the PNG is this
project's byte-reproducibility anchor (§9.4.3) rather than an agreement to some
number of digits.

> **The first attempt at leg 2 reported two MONASH values moving, and was wrong.**
> It keyed on `(tune, associate, bin)`, which collides as soon as two trigger
> groups share an associate: the `Lambda_b-bar` entry for `B-` overwrote the `B+`
> one, so it compared different quantities and called the difference a
> regression. Keying on the trigger as well takes the count to zero.
>
> **THE CORRECTED KEY, for anyone who compares these logs again:**
>
> ```
> (flavour, trigger, tune, associate, bin)
> ```
>
> The `UNCERTAINTY_MATRIX` line carries all five fields. Drop the trigger and two
> different measurements collapse onto one entry as soon as two trigger groups
> share an associate. Drop the flavour and the same happens across flavours.
> Recorded because the failure mode is generic — **an assertion is only as good
> as its key**, and this one would have raised a false STOP.

### 9.9.2 Eyes on

Four trigger pads, all populated: `B^{+}` and `#bar{#Lambda}_{b}^{0}` for beauty,
`D^{+}` and `#Lambda_{c}^{+}` for charm. Away-side peak at Δφ ≈ π in every pad;
SS flat and consistent with combinatorial; OS−SS near zero at Δφ ≈ 0. The method
note `0-100%, 10-block SEM` is on the figure. The baryon-triggered pads carry
visibly larger errors, as their statistics imply.

**One presentation note for the owner:** the `OS` / `SS` legend sits on the data
near Δφ ≈ 2 on the charm pads. It is legible, and it was not moved, because the
pad geometry is hard-coded in the macro and moving it is a presentation ruling.

---

## 9.10 RENDER #5 — dense-spectrum mode and the inset fixes ✅ THE FIGURE IS FIXED, 4 PANELS ARE NOT

The pass that acts on §9.7.2's three findings. Wrapper PID **3759785**,
`root.exe` **3759935**, PGID **3759785**, started 14:14:15 CEST, log
`kinematics_render5.log`, 0 compile errors, no staging left behind.

### 9.10.1 Styling moved no number — again asserted

| quantity | render #4 | render #5 | |
|---|---|---|---|
| MONASH selected particles | 39 421 891 | **39 421 891** | OK |
| JUNCTIONS selected particles | 37 697 473 | **37 697 473** | OK |
| CLOSEPACKING selected particles | 36 150 008 | **36 150 008** | OK |
| freeze manifest | `fcd96eae…` | **`fcd96eae…`** | OK |
| boundaries artifact | `3b0554fe…` | **`3b0554fe…`** | OK |
| closed loop | worst \|Δ\| 0.000465, PASS ×11 | **unchanged** — re-derived from the committed artifacts | OK |

**Mechanical panel battery, 30/30:** √s, status window, pT and η each 30/30; **0**
occurrences of *prompt*; block NDC y unchanged at 0.400 / 0.356 / 0.312 / 0.268;
routing identifiers **0/30**. **Inset still 1 dp on all eleven**, `59.8-65.9%` and
`50.3-59.8%` distinct. **φ flat at ~0.010.**

**Dense mode is confirmed in the bytes, not just in the source.** The generated
`.C` files now emit **three** `SetMarkerStyle` calls — 20, 21, 22 — and all three
are `entry->`, i.e. the LEGEND. Render #4 emitted fourteen. The drawn histograms
carry marker 1, which ROOT omits because it is the default. **The tune marker is
in the legend and nowhere else**, which is exactly the ruling.

### 9.10.2 ✅ Figure 4 — all four defects closed

| defect (§9.7.2) | render #5 |
|---|---|
| marker ribbons, MONASH occluded | ✅ **gone.** Clean thin lines; MONASH is drawn LAST and is visible throughout |
| spectra crossing the inset frame | ✅ **gone.** The frame stops at N_ch 72.6 and the earliest crossing is N_ch 77 |
| subtitle struck by the inset's own frame ticks | ✅ **clear.** Top margin 0.12 → 0.20 drops the frame to NDC 0.80 |
| `0.0-8.4%` struck by the inset's own curve | ✅ **clear.** Label height 0.34 → 0.20 of the log range |

| file | sha256 |
|---|---|
| `Multiplicity/MultiplicitySpectrum_Shared_shape.png` | `85a2488a28a4d3b40872d60cca78e633cf282647bafd176ea5675fdac3691b67` |
| `Multiplicity/MultiplicitySpectrum_Shared_shape.pdf` | `563544279034c73fd20d6c732ff7f2915fae7062019914cc822b106091f37f85` |
| `Multiplicity/MultiplicitySpectrum_Shared_shape.C` | `ec96a95705e3342dd65faa3482607dc1d41730b95f335c064efaf78b2da97207` |

**Figure 4 chain:** `4d7ab97e…` → `7385fbdf…` → `c9683cee…` → `b65874f1…` →
**`85a2488a…`**.

> **Residual, reported not fixed.** Where CLOSEPACKING agrees with MONASH to
> within a line width — the low-N_ch half — only the topmost curve shows, and
> that is now MONASH. Three coincident curves at one line width cannot all be
> visible; the ratio panel carries the difference. A line-width ladder
> (CLOSEPACKING 6 / JUNCTIONS 4 / MONASH 2) was previewed and does make all three
> visible, at the cost of bands 3× the line width — a milder version of the
> ribbon this pass removed. **Left for the owner rather than chosen here.**

### 9.10.3 ⚑ THE PANEL CAPTION IS STILL STRUCK ON 4 OF 30 — the fix helped and did not finish

`tools/check_panel_caption_collisions.py` on all 30, expecting 30/30 clean:

| panel | render #4 | render #5 | |
|---|---|---|---|
| `pT_Lambdacplusbar` | 997 | **747** | ⚑ still struck |
| `pT_Lambdacplus` | 989 | **683** | ⚑ still struck |
| `pT_Sigmabzero` | 739 | **622** | ⚑ still struck |
| `pT_Sigmabzerobar` | 698 | **563** | ⚑ still struck |
| `pT_Dminus` | 210 | **85** | grazing, legible |
| `pT_Dplus` | 105 | **24** | grazing, legible |
| the other 24 | 0 | **0** | clean |

**Why it did not finish, established by eyes-on rather than inferred from the
count.** On Σb⁰ the tail of `(status 81-89)` is overlapped by **error bars**, not
by markers. Dense mode removed the markers; the E1 uncertainty bars remain, and
in the sparse high-pT tail of the low-statistics baryons they are tall enough to
reach the caption on their own. The four struck panels are exactly the four
lowest-statistics species.

> **So the remaining fix is not a styling constant.** The options are to move the
> block, to shorten the caption, or to stop drawing error bars on these panels —
> and the third would remove uncertainty information from a paper figure to make
> room for text, which is not a trade this session will make unasked.
> **Owner call.** The other 26 panels are clear, and figure 4 is clear.

### 9.10.4 DIGESTS — the 30 panels (60 files)

Supersede the §9.7.3 set entry-for-entry.

| file | sha256 |
|---|---|
| `Inclusive/eta/Inclusive_eta_Bminus_shape.pdf` | `e6876277bad6eee5175a60e6123dbc84bf0a17b0f0bfaafeb978ce55b4146cb9` |
| `Inclusive/eta/Inclusive_eta_Bminus_shape.png` | `09f715342d0d4535e1154cc018d6b84d8a8f5ea891bee0c3a24cf652a232633f` |
| `Inclusive/eta/Inclusive_eta_Bplus_shape.pdf` | `d2d64da170d3536863aaa1c2bb9cde0c4db6e5f913174a285a312302a407df0f` |
| `Inclusive/eta/Inclusive_eta_Bplus_shape.png` | `9f0aa99019b458aab368737c7ebd461382adb7cdcc08aa03fcb366dab08d957a` |
| `Inclusive/eta/Inclusive_eta_Dminus_shape.pdf` | `fea867b06a6728bbf481e530bf2a220a47de367c24c3c22dfaae79e10e30abe5` |
| `Inclusive/eta/Inclusive_eta_Dminus_shape.png` | `60d1d9b658ad82174ff5ef7fc80cf60b47852f109f8c2175b99d79d2734a2e69` |
| `Inclusive/eta/Inclusive_eta_Dplus_shape.pdf` | `110d5a1035ecb23e2c79ae426b7072ecd50d9a1cb0a9eb2ad70e37001f709caa` |
| `Inclusive/eta/Inclusive_eta_Dplus_shape.png` | `ecebe94d9f1332a8f99cc95644c2b916dc468722f69e490e0371832a3c2eb5de` |
| `Inclusive/eta/Inclusive_eta_Lambdab_shape.pdf` | `1e43c46a5b2cb38613849083ff9b71ea1b5ded94eb37187bcfd92c1d206de871` |
| `Inclusive/eta/Inclusive_eta_Lambdab_shape.png` | `aa097b26cc883c5374a564d9d4559d5a056b54f938dc0f98bf5d8e9fb99636ce` |
| `Inclusive/eta/Inclusive_eta_Lambdabbar_shape.pdf` | `97b50ad150695f48ca4723e476c0b788f47d7eca8c6b783d761eb106315f6d31` |
| `Inclusive/eta/Inclusive_eta_Lambdabbar_shape.png` | `70a0581e8f44f81e6e4aef414a339e7ec31a0e6913aa00b0cfc8912fe7f67a7d` |
| `Inclusive/eta/Inclusive_eta_Lambdacplus_shape.pdf` | `8227365a5dc60c2a577419dd43b295da0bf053dea16b81b0508817abf18c5683` |
| `Inclusive/eta/Inclusive_eta_Lambdacplus_shape.png` | `a54f6a25ed27f5516fced8d258687355ef806970acda2c28f0a9c3aed20eb975` |
| `Inclusive/eta/Inclusive_eta_Lambdacplusbar_shape.pdf` | `7f1338473750335486b4dccabf0791b34f97f5199ed7150c32fc20feea54de63` |
| `Inclusive/eta/Inclusive_eta_Lambdacplusbar_shape.png` | `97de7a7e34e93df70df2f3827907bfb3ae1e6853840ced607dafb92ca2c5cfef` |
| `Inclusive/eta/Inclusive_eta_Sigmabzero_shape.pdf` | `b8e5d10a02748a92289521af4015a1422877cccbd2f2fb1c137c495812c07f59` |
| `Inclusive/eta/Inclusive_eta_Sigmabzero_shape.png` | `869b7656a4984af637e4048736fb699040a1433510da212045fbbec39f77be30` |
| `Inclusive/eta/Inclusive_eta_Sigmabzerobar_shape.pdf` | `2b38674a4ea072a0a014413f65c1fef145d647f50ebbbaf4647d3ac70cae73b9` |
| `Inclusive/eta/Inclusive_eta_Sigmabzerobar_shape.png` | `8a81a712c7ec96cb2a31eb4846e1e9d0907b5e7cb16c9da9f3d0ba9f79c0ca29` |
| `Inclusive/pT/Inclusive_pT_Bminus_shape.pdf` | `dd99a8fc9b206a1b406d9e0a9d593f4593f13588a63168de5b57ebd2cd3de4b7` |
| `Inclusive/pT/Inclusive_pT_Bminus_shape.png` | `7ce12c5fcd76c34ac7eca498b46ead2b61f5ef9c7fb66d1963317556772e84bb` |
| `Inclusive/pT/Inclusive_pT_Bplus_shape.pdf` | `a8478347d3bb2b0fe7816e7bf428e49faa3e530c11d30a965b41e0e37d2a0cb3` |
| `Inclusive/pT/Inclusive_pT_Bplus_shape.png` | `ed6c8de718f378a6ecca3b29cb0faa46fe0a87815b9d6d907596bd4443f86bba` |
| `Inclusive/pT/Inclusive_pT_Dminus_shape.pdf` | `5db7061e9a9076750ea203d3c4dcc5d5b917c42e7a44475d941f66b1f010052e` |
| `Inclusive/pT/Inclusive_pT_Dminus_shape.png` | `8a2703d5b9ac0267948d7f6e1aec028d24730a45b32d1a71da1debad80b8a6c0` |
| `Inclusive/pT/Inclusive_pT_Dplus_shape.pdf` | `9ad0ed0716b7d99f6f165353fb03c3c7ee724e081516c39ae73d3a8cca93bfe0` |
| `Inclusive/pT/Inclusive_pT_Dplus_shape.png` | `e88dd9835281aa61075e56bdb9bafe08a5e5313d1afab3a712bf4417e58e021c` |
| `Inclusive/pT/Inclusive_pT_Lambdab_shape.pdf` | `f9fddd99ac25347da936e790d3ba1b9239e282100532e50c041fc3c7a8902db4` |
| `Inclusive/pT/Inclusive_pT_Lambdab_shape.png` | `d08693e634c320c13ce82ca4fa6ca109f2854d57e8215f5da92cce3cc550bfeb` |
| `Inclusive/pT/Inclusive_pT_Lambdabbar_shape.pdf` | `4b42ccbf6b3278c6558b96324e6894cf092d69d8907e1045a6833d8f2cd8fe28` |
| `Inclusive/pT/Inclusive_pT_Lambdabbar_shape.png` | `d1b2687a7cfda3b3b88fc31d273d6b569cbfb685050c8a6833cdfc8893dcc9eb` |
| `Inclusive/pT/Inclusive_pT_Lambdacplus_shape.pdf` | `b373cb139c407a0f4dc4b3161a3d9781b4fae319e86be6a05bf4263702ceeab2` |
| `Inclusive/pT/Inclusive_pT_Lambdacplus_shape.png` | `bcfc11df5b16b301fae9118a2df1fb951427fbacc3d4679a8a82154577855423` |
| `Inclusive/pT/Inclusive_pT_Lambdacplusbar_shape.pdf` | `256a9d6818ca471e4d9b2982caff169b2059d4d8cf21ecc29f087a27a0ae16b5` |
| `Inclusive/pT/Inclusive_pT_Lambdacplusbar_shape.png` | `5b55f9ad9ff447bbdeb7c4f71d129e35573dd1f639b2237428f6fc69ac9152be` |
| `Inclusive/pT/Inclusive_pT_Sigmabzero_shape.pdf` | `2376e281127fe57adaf235222d0f2b755ba4e47424a816ba976a5c0a1a320c88` |
| `Inclusive/pT/Inclusive_pT_Sigmabzero_shape.png` | `1fe47b6b40cefda6cbfefe73667310cfe9578a734903e420df9df754d852807a` |
| `Inclusive/pT/Inclusive_pT_Sigmabzerobar_shape.pdf` | `fc895dc8b0f46433e0f716f541327930d438b212ab5951e84466b83649918b16` |
| `Inclusive/pT/Inclusive_pT_Sigmabzerobar_shape.png` | `208139066f0635f23a08e232d99e673473a486f22c47b0196109e9f92e6db087` |
| `Inclusive/phi/Inclusive_phi_Bminus_shape.pdf` | `e3c88808e2755fd8ec80254b2593df1232b80b21339cf91968f9ef0876c9fe0f` |
| `Inclusive/phi/Inclusive_phi_Bminus_shape.png` | `40810d976220435f3b4f17bae01271b0d810bfaf81903efd4b5639d2191e1c10` |
| `Inclusive/phi/Inclusive_phi_Bplus_shape.pdf` | `3856d7fc38c3bd6249c82374e9bb6a46ec44ec0f6d2eb827eeab928aa13f4adc` |
| `Inclusive/phi/Inclusive_phi_Bplus_shape.png` | `ab65a8192c862a6a2687197b2a5955a2cecf4f03f0d06b53582e838c9259fdc4` |
| `Inclusive/phi/Inclusive_phi_Dminus_shape.pdf` | `96f8a4a59cdbf9f565d04085e8d43d55d21981dcad49f769fc7b94ddbd5c9860` |
| `Inclusive/phi/Inclusive_phi_Dminus_shape.png` | `21af374cbfdf3b07529109fe7a4054b3513d7f991fd2bf3d163ee54deaa99b1c` |
| `Inclusive/phi/Inclusive_phi_Dplus_shape.pdf` | `4d7ade2e036c8fe33a7e9b05a907c25e224057f9e177c9621b96b5b742e3d154` |
| `Inclusive/phi/Inclusive_phi_Dplus_shape.png` | `2401313b10d429fd845a68b43a0e2c97e373ab8ee6c7b0d387c3a741eb408dcd` |
| `Inclusive/phi/Inclusive_phi_Lambdab_shape.pdf` | `0a42e815cd3a3c345d6d3fa6534e5f588742264c1c60a113ca0639f6cd7a32a9` |
| `Inclusive/phi/Inclusive_phi_Lambdab_shape.png` | `30e01de9de83597cd5091a78c4e856bf8483a0722a817c2c5e37bd475c858af5` |
| `Inclusive/phi/Inclusive_phi_Lambdabbar_shape.pdf` | `72baa133317baf56a0048a8f552a9a6e5d334c943e1c6afef8df3756941cbcb3` |
| `Inclusive/phi/Inclusive_phi_Lambdabbar_shape.png` | `e75fb4c82915a619a49af3f957baa9a30e968f4a04c0f1b6440306a4271113c8` |
| `Inclusive/phi/Inclusive_phi_Lambdacplus_shape.pdf` | `53f9a5180989753eff3e0da7546b36ab882c6568d68d89ffd58ad58566218be4` |
| `Inclusive/phi/Inclusive_phi_Lambdacplus_shape.png` | `3a54aabe9d1d672ae654383d7525d4f787d9c20dea902beee0ad8f6d38e693c2` |
| `Inclusive/phi/Inclusive_phi_Lambdacplusbar_shape.pdf` | `fc81c27a4dd14a043fc44b53acf41d44a3206e6ccf430e4c704552974748ee7e` |
| `Inclusive/phi/Inclusive_phi_Lambdacplusbar_shape.png` | `4a097dacc3fb104f323abdbd4211244999a3ad9eab634e89e741a9b73f9cc516` |
| `Inclusive/phi/Inclusive_phi_Sigmabzero_shape.pdf` | `1c649f19774a4f7f18658ec51760abdc59d58b39a989a6332a3c2c0ad83b993b` |
| `Inclusive/phi/Inclusive_phi_Sigmabzero_shape.png` | `ea885d7cb454eee1dcb5a472e964f011c396b5159815e6d8862e7fc04ac94630` |
| `Inclusive/phi/Inclusive_phi_Sigmabzerobar_shape.pdf` | `302449326c0dadb0a577f9c20793c8adbfbe6d1362fe675de1549dab47f7bd14` |
| `Inclusive/phi/Inclusive_phi_Sigmabzerobar_shape.png` | `e2912ecbb6b38f25a6de3c3124f1f4d4b0616206d75b3dc2e6aaec23c95a1c66` |

---

## 9.11 THE CORRELATION LEGEND — placed by measurement, 2026-08-18

§9.9.2 recorded one presentation defect: the OS/SS legend sat on the charm data
near Δφ ≈ 2. This render fixes it. The macro applies the same rule the species
panels use, rather than a new fixed position.

`PadRegionIsClear` reads the drawn OS and SS histograms, includes the error
bars, and works in the pad's own coordinates. `gPad` supplies the margins, the
axis ranges and the log-y flag. The macro tries the reviewed upper-right box
first and falls back to upper-left.

**All four pads chose upper-left.** The log records the decision per pad:

```
CORRELATION_LEGEND_ANCHOR x0=0.16 position=upper-left     (×4)
```

That is the away-side peak reaching into the upper right on every pad, beauty
as well as charm. The near side is the dip, so the upper left is empty.

| file | sha256 | supersedes |
|---|---|---|
| `BEAUTYCorrelations_MONASH_PNG.png` | `7238982cd877a16cdd8eb61df50238fc0dd410f1b1a7dd2beac67f00e54392ad` | `cc2abc21…` |
| `CHARMCorrelations_MONASH_PNG.png` | `b426fd7f900a42186146ae642b2bff6c9ebc35c62e965637b821d7ed86d30f88` | `0cc2a0ac…` |
| `BEAUTYCorrelations_MONASH_PDF.pdf` | `261bce28551d0d91f9d614d770916c462b1f258ff03914c03959cf9b347ff255` | — |
| `CHARMCorrelations_MONASH_PDF.pdf` | `6fa553eb4ed01668a83da428cdcd2013d30e748a1b82f1293873b43ec41528ed` | — |

### 9.11.1 The guard, re-run

The balancing canvas this configuration renders as a by-product is
`88fdb62845ccbcb623bf908a0ff0eedc8a822194a3c05dfbb5483882da1d4990`. That is
**byte-identical** to the signed-off V-INTEGRATED artifact. The legend change
therefore moved no number. The gate passed and promoted nine files. No staging remained.

### 9.11.2 Eyes on

The legend clears the data on all four pads. The away-side peak at Δφ ≈ π, the
flat SS distribution and the OS−SS subtraction all match §9.9.2.

> **One anomaly, recorded because the compiler caught it and a reader would not.**
> The first insertion put `PadRegionIsClear` inside a block comment that holds a
> legend-entry example. The compile failed with an undeclared identifier at the
> call site. The helper now sits at file scope, confirmed by counting `/*` and
> `*/` before its definition.

---

## 9.12 RENDER #6 — the anchor ladder, and a defect it exposed in the checker

Render #6 applied the descending anchor ladder. Wrapper PID **3953937**,
`root.exe` **3954009**, PGID **3953937**, started 16:00:48 CEST, log
`kinematics_render6.log`, 0 compile errors, no staging left behind. Outputs
archived on the deploy as `KinematicSpectra.render6_20260818T172555`.

**Its panels are superseded by render #7 (§9.13).** This section records the
battery, the ladder result and one finding. It does not list the 60 panel
digests, because §9.13 replaces them and a superseded digest invites a
quotation.

### 9.12.1 The battery

| quantity | recorded | render #6 | |
|---|---|---|---|
| MONASH selected particles | 39 421 891 | **39 421 891** | OK |
| JUNCTIONS selected particles | 37 697 473 | **37 697 473** | OK |
| CLOSEPACKING selected particles | 36 150 008 | **36 150 008** | OK |
| freeze manifest | `fcd96eae…` | **`fcd96eae…`** | OK |
| boundaries artifact | `3b0554fe…` | **`3b0554fe…`** | OK |

**Figure 4 is byte-identical to render #5**, at
`85a2488a28a4d3b40872d60cca78e633cf282647bafd176ea5675fdac3691b67`. The ladder
acts on the species panels only, and `DrawMultiplicityOverlayWithRatio` never
sees it. A styling change that touches one family and leaves the other
bit-for-bit identical is the cleanest form the assertion takes.

### 9.12.2 The ladder did what the preview said it would

The preview predicted 24 panels at 0.400, four relocating, and two with no clear
baseline. The render logged exactly that:

| baseline | panels |
|---|---|
| 0.400 | **26** — the 24 clear panels plus the 2 that found no clear baseline |
| 0.346 | **2** — pT D⁺, pT D⁻ |
| 0.302 | **2** — pT Λc⁺, pT Σb⁰ |
| `NO_CLEAR_BASELINE` | **2** — pT Λ̄c⁻, pT Σ̄b⁰ |

The two failures are the two panels the preview named. **No value differed from
its prediction.**

### 9.12.3 ⚑ THE FINDING — the pixel checker went blind when the caption moved

Run against render #6, `tools/check_panel_caption_collisions.py` reported **six**
strikes: the same six as render #5, at almost the same pixel counts. Eyes on the
pT Σb⁰ panel showed a caption at 0.302 that clears the data completely.

**The tool was measuring the boxes the relocated panels had left behind.** It
carried the four baselines as constants — 0.400, 0.356, 0.312, 0.268 — which held
only while every panel put its caption in one place. On a relocated panel it was
scanning empty space that the curve happens to cross.

> **A checker with a hidden assumption fails silently in the direction that looks
> like a defect.** It did not crash and it did not report nonsense. It reported a
> plausible number that agreed with the previous render, which is the hardest
> kind of wrong answer to notice.

The tool now reads the baselines from each panel's own generated `.C`. Re-run:

| set | before the fix | after the fix |
|---|---|---|
| render #6 | 24 clean, 6 struck | **28 clean, 2 struck** — pT Λ̄c⁻ and pT Σ̄b⁰, the two `NO_CLEAR_BASELINE` panels |
| render #5 | 24 clean, 6 struck | **unchanged** — same panels, same pixel counts |

Render #5 is the control: every panel there shares one caption position, so the
old assumption held and the fix moves nothing.

**So render #6's true result is 28 of 30**, and the two that remain are the two
the ladder could not reach inside the frame. That is the measurement that sent
the caption above the frame in §9.13.

---

## 9.13 RENDER #7 — the caption leaves the frame ✅ 30 OF 30 CLEAN, FIGURE FAMILY FINAL

The pass that closes the caption defect. Wrapper PID **190354**, `root.exe`
**190517**, PGID **190354**, started 17:26 CEST, log `kinematics_render7.log`,
0 compile errors, no staging left behind.

### 9.13.1 The battery

| quantity | recorded | render #7 | |
|---|---|---|---|
| MONASH selected particles | 39 421 891 | **39 421 891** | OK |
| JUNCTIONS selected particles | 37 697 473 | **37 697 473** | OK |
| CLOSEPACKING selected particles | 36 150 008 | **36 150 008** | OK |
| freeze manifest | `fcd96eae…` | **`fcd96eae…`** | OK |
| boundaries artifact | `3b0554fe…`, `classes=11`, `MONASH_MB_recomputed` | **identical** | OK |
| closed loop, re-derived this session | worst \|Δ\| 0.000465, PASS ×11 | **worst \|Δ\| 0.000465, 11/11 PASS** | OK |
| text primitives: √s, status, pT, η | 30/30 each | **30/30 each** | OK |
| occurrences of *prompt* | 0 | **0** | OK |
| routing identifiers in titles | 0/30 | **0/30** | OK |
| inset labels at 1 dp, all eleven distinct | yes | **yes**, `59.8-65.9%` and `50.3-59.8%` separate | OK |
| φ flatness | flat at ~0.010 | **0.01000 per tune**, scatter 4.0–4.4 % | OK |

### 9.13.2 ✅ 30 OF 30 — the pixel checker

```
CAPTION_BOX_CALIBRATION reference=Inclusive_eta_Dplus_shape.png canvas=856x652 lines=4
   line 0 ndc_y=0.900  x=[167,229]
   line 1 ndc_y=0.856  x=[194,299]
   line 2 ndc_y=0.812  x=[167,553]
   line 3 ndc_y=0.768  x=[204,342]
PANEL_CAPTION_COLLISION panels=30 clean=30 struck=0
```

The checker calibrated itself to the new baselines. That is the fix of §9.12.3
working. It followed the caption instead of measuring where the caption used to
be.

**The render's own guard agrees, on every panel:**

```
30 x  baseline=0.9  caption_bottom=0.738  frame_top=0.72  boxes_clear=1  status=ABOVE_FRAME
```

**Eyes on** pT Σ̄b⁰, η D⁺ and φ B⁺. Caption above the frame and legible on all
three; legend inside the frame and clear of the data; η domain exactly ±4, φ
exactly ±π. pT Σ̄b⁰ is the panel that had **no clear baseline anywhere inside the
frame**, and it is now clean.

### 9.13.3 The two rules, their constants, and why each was chosen

**RULE 1 — the anchor.** Superseded for the caption by rule 2, and kept as a
guard. It searched a descending ladder: 0.400, then 0.346, then 0.302. It took the
first baseline whose four per-line boxes cleared the drawn bins and their error
bars.

Two of its constants matter to a later reader.

The footprint is **four boxes, one per line**. The widths are 0.073, 0.154, 0.451
and 0.205, measured by `tools/check_panel_caption_collisions.py`. A single
rectangle around all four lines claims the white space beside the three short
ones. It then reads a passing curve as a collision.

The clearance test uses the **displayed** x range, not the full axis. The macro
bins the pT panels to 7000 GeV/c and draws them to 50. `GetXmin` and `GetXmax`
would therefore scan bins no reader sees.

**The ruled fallback was top-left, and measurement refused it.** Every one of
the 30 panels blocks a top-left baseline of 0.760. The pT spectra peak in the
upper left. The η and φ distributions are plateaus that fill the upper half. A
preview put the block on the pT peak, which is worse than the defect. So the
ladder descends. It reached **28 of 30** (§9.12.2).

**RULE 2 — the headroom.** The caption sits **above the frame**. This session measured two options on render #5's generated files before building
either.

| | option A: lower the y-axis | option B: caption above the frame |
|---|---|---|
| reaches 30/30 | per panel | **by construction** |
| pT Λ̄c⁻ | needs **1.52** extra decades | no change needed |
| pT Σ̄b⁰ | needs **5.69** extra decades | no change needed |
| pT D⁺ / D⁻ / Σb⁰ / Λc⁺ | 0.20 / 0.37 / 0.80 / 1.26 decades | no change needed |
| the 24 clear panels | 0.00 decades | frame height −20.5 % |
| linear η and φ panels | rule asks for a **negative** minimum, measured −1.18e-3 and −2.83e-3 on the η Σb pair | unaffected |
| uniformity | three caption positions, and an axis range that varies per panel | **one caption position on all 30** |

This session chose option B. Nearly six decades of empty axis under one panel is
a figure a reader can misread. A normalised-entries axis cannot carry a negative
minimum. Option B also cannot fail at any statistics, so it holds for later
campaigns and not only for this freeze.

**Its constants come from the geometry and from a preview.** The title baseline is
0.965. A first caption baseline of 0.920 put the block under the title's
descender. Σ̄b⁰ carries a subscript. The gap is now 0.065, and the first baseline
is **0.900**. Four lines at 0.044, plus one glyph height below the last,
put the caption's lowest edge at **0.738**. A top margin of **0.28** sets the
frame top at **0.720** and clears it by 0.018.

The legend keeps its place **as a fraction of the frame**, which shrank. It sat
at 0.705–0.855 inside a frame running 0.14 to 0.87, which is 0.774 to 0.979 of
the frame height. The macro preserves those fractions.

### 9.13.4 DIGESTS — figure 4 and the supersession chain

| file | sha256 |
|---|---|
| `Multiplicity/MultiplicitySpectrum_Shared_shape.png` | `85a2488a28a4d3b40872d60cca78e633cf282647bafd176ea5675fdac3691b67` |
| `Multiplicity/MultiplicitySpectrum_Shared_shape.pdf` | `6466eb44f867031438e7d1209d4c747a280b43b76e9040c7e4a82f9cf070e12b` |
| `Multiplicity/MultiplicitySpectrum_Shared_shape.C` | `39e918ed69a13f5a607a4ba7cbad3d187bbafb9aa552cfcc61f73629b7d61b05` |

> **Figure 4's PNG is byte-identical across renders #5, #6 and #7.** Both rules
> act on the species panels, and `DrawMultiplicityOverlayWithRatio` never sees
> them. The `.pdf` and `.C` differ by their embedded timestamps, which §9.4.3
> already records as the reason the PNG is the sole byte-reproducibility anchor.
>
> **Figure 4 chain, complete:** `4d7ab97e…` (wrong η caption) → `7385fbdf…`
> (E10 fixed, 0-dp inset) → `c9683cee…` (1-dp inset) → `b65874f1…` (styled
> palette, transparent inset) → **`85a2488a…`** (dense-spectrum mode, three inset
> fixes), held through #6 and #7.

**The 30 panels (60 files)** supersede the §9.10.4 set entry-for-entry.

| file | sha256 |
|---|---|
| `Inclusive/eta/Inclusive_eta_Bminus_shape.pdf` | `20ddbb919f103929d802f0bdac34cc5d5bfe1e15db030fe0c94727ee60f5d0c0` |
| `Inclusive/eta/Inclusive_eta_Bminus_shape.png` | `1d74d4b62882c0539c4b8f723189f7d1783dcebb2bf4b5c0fffd2a981de3579c` |
| `Inclusive/eta/Inclusive_eta_Bplus_shape.pdf` | `4b52c795e09806d9a0c9ac1a3603428d2fe593f3679848c36e3f69c63fb48190` |
| `Inclusive/eta/Inclusive_eta_Bplus_shape.png` | `3f28e91a94e7ba6e172295ac78562e374172ad39813b970dcef965736e173e43` |
| `Inclusive/eta/Inclusive_eta_Dminus_shape.pdf` | `ae3058afc8dd51e711fa64b957842db3812818a405d2224cb81627c6d691e97b` |
| `Inclusive/eta/Inclusive_eta_Dminus_shape.png` | `c377f6417ecb2a117a8f286c0e8c316a04481aaa1a8312fadb53aa88a97ea649` |
| `Inclusive/eta/Inclusive_eta_Dplus_shape.pdf` | `48231313b1cbbc321671adfb176a92774fd76d19a3d4d2572096d727510be94c` |
| `Inclusive/eta/Inclusive_eta_Dplus_shape.png` | `7e6e7702932e788f19b698b13dd633648f1bb7a30519a0c782e9dddf70551dbf` |
| `Inclusive/eta/Inclusive_eta_Lambdab_shape.pdf` | `68225d55bc010eea9f10aef05fa7443d254ecd1e1c8ea35f8fd2c7cce2a02df8` |
| `Inclusive/eta/Inclusive_eta_Lambdab_shape.png` | `7a7e57786c67340d9c0f1e131046a6bf25a468e56757a0d523a9c3a49ca1c469` |
| `Inclusive/eta/Inclusive_eta_Lambdabbar_shape.pdf` | `df741d4285a5b25c596bd60a667915d1769c138f0c530ce1669107fcac646f4f` |
| `Inclusive/eta/Inclusive_eta_Lambdabbar_shape.png` | `9608ca72ab22b149b6162aadcad2bb07fc94b549232ae83c4096423752ebd636` |
| `Inclusive/eta/Inclusive_eta_Lambdacplus_shape.pdf` | `327fcc3e3eaf46fe406cbf0bab35cd39bb8fe4b58661dc0a9aef7f862ba2e92a` |
| `Inclusive/eta/Inclusive_eta_Lambdacplus_shape.png` | `5a7e9efaa387a0f9f5607ec052d35d5afa5ede908f0c85ed542e468bcc907b77` |
| `Inclusive/eta/Inclusive_eta_Lambdacplusbar_shape.pdf` | `bbe92cfe4e640655c4d473906acfc45b5a8985623e584bbaa9bb0eb9f37ba9dd` |
| `Inclusive/eta/Inclusive_eta_Lambdacplusbar_shape.png` | `7aca7ec1e56c54c85a3dc5e7a4fc583d96b12f414505b7d61e6f17a8cc376c20` |
| `Inclusive/eta/Inclusive_eta_Sigmabzero_shape.pdf` | `bbdefb9d94e0330f2bc418187b66ead9d048c9299b4c4f8406b38559289d1cae` |
| `Inclusive/eta/Inclusive_eta_Sigmabzero_shape.png` | `bd32b2cf1bfed0bf424b44245b3c08068375ae1b81e7259a13c7075e638e335a` |
| `Inclusive/eta/Inclusive_eta_Sigmabzerobar_shape.pdf` | `c0b0bcb3d705f902d664ec7b49593cb9a1165153a9576a0b84cf775c1860bac6` |
| `Inclusive/eta/Inclusive_eta_Sigmabzerobar_shape.png` | `18de23890eb2ad00300e1b5c497221d3765de31e56b21b617b00ac276a1565de` |
| `Inclusive/pT/Inclusive_pT_Bminus_shape.pdf` | `ec7fcd621d86e7e9a736be5b6a4887b7ed7d971b8b6a2721945a8687dda0b63a` |
| `Inclusive/pT/Inclusive_pT_Bminus_shape.png` | `7b5de2323be5e327bdf1c52d869cb5c1939e2c53426b7f13923f8f5ef8be28f7` |
| `Inclusive/pT/Inclusive_pT_Bplus_shape.pdf` | `e7513ca5578b98d4521ab78f08f7b0f5a1c650cae004ae65aa05dffc57e91311` |
| `Inclusive/pT/Inclusive_pT_Bplus_shape.png` | `4a4af00d1314a5129f4e6f92fb15f88774b4081e1da5acf07c2471d020e2f8bc` |
| `Inclusive/pT/Inclusive_pT_Dminus_shape.pdf` | `b2b75d767414d4c482a9a132d1bfe52db3e12036ceaf79f4713cd71dce09505a` |
| `Inclusive/pT/Inclusive_pT_Dminus_shape.png` | `b5a331ce977b0ffa3c5084b5df540a48a28035aa98d0fcb4ac8fc3f7014b5f27` |
| `Inclusive/pT/Inclusive_pT_Dplus_shape.pdf` | `1a4ca3b0edb036fac97c53991bd89a91ae863bc855e168b8e114a1c7ea672abc` |
| `Inclusive/pT/Inclusive_pT_Dplus_shape.png` | `8614915462ba45f26eefc3a375e6239a7fb1712f1c3212be84e72dd2b1742e0b` |
| `Inclusive/pT/Inclusive_pT_Lambdab_shape.pdf` | `031bd3f6c080a02108884ac9f2d897ef072f523c8ccb06e7633647b5380ef045` |
| `Inclusive/pT/Inclusive_pT_Lambdab_shape.png` | `428e0f0beed36da3de97b2af8633442396db803dbf94818ca4c3c03d22277951` |
| `Inclusive/pT/Inclusive_pT_Lambdabbar_shape.pdf` | `eb245f8367cb71b8f63391a15883ab8e2a174721df37e9c0980731d4e6bc3c17` |
| `Inclusive/pT/Inclusive_pT_Lambdabbar_shape.png` | `f67db7a522d9bbd81c8a74c180ee0a318aecd24bb7ff6d94050c3f68182181e6` |
| `Inclusive/pT/Inclusive_pT_Lambdacplus_shape.pdf` | `bcaf6bdd6ba0e5e9ff33ebac74050aaf6b1d7b5394937997da356f1a74af9026` |
| `Inclusive/pT/Inclusive_pT_Lambdacplus_shape.png` | `603e4743d4ed7043482779789e238809502781aca1cc63f61216b7053075e883` |
| `Inclusive/pT/Inclusive_pT_Lambdacplusbar_shape.pdf` | `c5b6f2bd26d19e0cf63bd52b315d59814c9de09b14ad44269d192a05c9d50563` |
| `Inclusive/pT/Inclusive_pT_Lambdacplusbar_shape.png` | `0fe67c3ade8acc2199a98c9027549c855e2f729e5eec1d9a61c600e581a7feba` |
| `Inclusive/pT/Inclusive_pT_Sigmabzero_shape.pdf` | `9e27ebfb17481e8cb6855b9f3ed1a906da027a9bfbb88079a5b2e11ddbc5b7ee` |
| `Inclusive/pT/Inclusive_pT_Sigmabzero_shape.png` | `cfcb7cc269a97f96abf23858fa437ec1ddea45757b4d20d86fedbad29bdb8967` |
| `Inclusive/pT/Inclusive_pT_Sigmabzerobar_shape.pdf` | `848d7a27257685997de7b3ac88ea632dc5627dc467e7c38de71d006ed5c1b6be` |
| `Inclusive/pT/Inclusive_pT_Sigmabzerobar_shape.png` | `f62dd2029cd6a29666963130f89c4b149333bc1fe78228118bb82af62653a0d9` |
| `Inclusive/phi/Inclusive_phi_Bminus_shape.pdf` | `97e9b75cde7e2a3306eef4587a34dcb89e1c403f1ab8bda1b75650fbb60efb9c` |
| `Inclusive/phi/Inclusive_phi_Bminus_shape.png` | `7ec646d8728d912a90210c30f6cd7ab86ea6db7e6ec4f45d0bcd1f7e28e78e98` |
| `Inclusive/phi/Inclusive_phi_Bplus_shape.pdf` | `befe0895c1fbe502888932e5bdced469d7bb1446f82e1f92c9ea3950337261ac` |
| `Inclusive/phi/Inclusive_phi_Bplus_shape.png` | `34d423d2a56dae841e455207c613581bfb686ef9c5fd344862f72b36b69c0ff7` |
| `Inclusive/phi/Inclusive_phi_Dminus_shape.pdf` | `43cb25b693963b4a8d50da8e407c4d37369287075b9d82977591046f432888f6` |
| `Inclusive/phi/Inclusive_phi_Dminus_shape.png` | `319915f63e2212e59e345bc5d24262692cd18e6d0291dff292f8c1808ae6f355` |
| `Inclusive/phi/Inclusive_phi_Dplus_shape.pdf` | `95aa4b5f1aa08ea2661326e923c6da42660716603707f2200577d5447d13ae4a` |
| `Inclusive/phi/Inclusive_phi_Dplus_shape.png` | `eb619417a415ee28603edcfa8d6783de8e3d194b94acb61ece6a37f766d0eec0` |
| `Inclusive/phi/Inclusive_phi_Lambdab_shape.pdf` | `2ddd08b85d1f4deb2010b3156d1bd8688e3ea6e28ca0c1f212e11c45e58f484b` |
| `Inclusive/phi/Inclusive_phi_Lambdab_shape.png` | `c03f551d4d3a342e46380ba2e390193cba995112a5c75baae0a346eb7a0d9d28` |
| `Inclusive/phi/Inclusive_phi_Lambdabbar_shape.pdf` | `0ca5f3089021abca5cd143489c2c868c7777ffdec36f129ce695370e8e1c7809` |
| `Inclusive/phi/Inclusive_phi_Lambdabbar_shape.png` | `31a7ed8fae96565b0501e69ebe64ff049ee998667b629613f212ad8a31a32ca7` |
| `Inclusive/phi/Inclusive_phi_Lambdacplus_shape.pdf` | `8fcf1336daeacae9fe8fc57be6549f362cf946650d79a693cbf26af2981ec6fa` |
| `Inclusive/phi/Inclusive_phi_Lambdacplus_shape.png` | `6d66d352e47b739d17fbeacecf4158b9ca3bed16e75fd925ce007e51a647ca3f` |
| `Inclusive/phi/Inclusive_phi_Lambdacplusbar_shape.pdf` | `7480704e7fc2a41b96a38f2455ed4cb9df30bedd8b3dc535fc823118e659b8ed` |
| `Inclusive/phi/Inclusive_phi_Lambdacplusbar_shape.png` | `1dd3dc8770e1026d172b1279795b35ded33a79236fad8c704c7b48b0d2b54f6e` |
| `Inclusive/phi/Inclusive_phi_Sigmabzero_shape.pdf` | `5e14270eaf312bdf961ede1b1bca1223bda26c2bcc2328a3a1ec51f3eb972ee0` |
| `Inclusive/phi/Inclusive_phi_Sigmabzero_shape.png` | `84f753dbba205b77d8642a73c8d3e908c5df8b7fe3ee29aece605ac62a44b016` |
| `Inclusive/phi/Inclusive_phi_Sigmabzerobar_shape.pdf` | `4cbc7da7a5987c66664603a33e2bfbe31bdce847b9e7b9fd58c36f01b33fb86b` |
| `Inclusive/phi/Inclusive_phi_Sigmabzerobar_shape.png` | `3840ca14ab55bd45a4cfcde6ee189d7f9dd7aaa60e64a5779c76eb60b737ed81` |
3. ~~**Plotting outputs.** … **UNKNOWN**~~ — **ANSWERED 2026-08-20. Two of three
   relevant committed validation outputs are digest-pinned and verified; one is not.** §8.1
   below carries the measurement. The UNKNOWN is closed.
4. **Any claim that a recipe was run.** None were, this session, by instruction.

### 8.1 Figure digest pinning — MEASURED 2026-08-20, and one gap found

**The private branch-state record's Q2 asked whether any figure *output* carries a
recorded digest.** After excluding the three internal explanatory SVGs, two of
three relevant committed validation outputs do. Every recorded digest was
recomputed from the committed bytes rather than read.

| output | where its digest is recorded | verified |
|---|---|---|
| `…_THREETUNE_PNG.png` | `results/validation/plotting/hf_run3_v1_threetune_20260816/RUN_RECORD.md:37` | ✅ **match** |
| `…_THREETUNE_POLISHED_PNG.png` | the same record, `:230` | ✅ **match** |
| **`…_MONASH_PNG.png`** | **nowhere** | ⛔ **unrecorded** |

**The gap, stated exactly.**
`results/validation/plotting/hf_run3_v1_monash_20260813/global_balancing_plots_multiplicity_HF_RUN3_V1_MONASH_PNG.png`
is committed and its sha256 is
`e13fceba1776e26a0a85df60c7cf163b7b4e309265e480b4f3b0acb17e997053`. **That
string appears in no file in this repository.** Its run record pins the plotting
configuration, the class-boundary artifact and the pair registry — every
**input** — and does not pin the **output**.

**So the freeze contract's figure-side hole is real but small, and it is one
file rather than a class.** The later three-tune record pins its canvases; the
earlier MONASH record predates that practice.

**Two things this measurement does not claim.**

1. **`plotting/PAPER_FIGURE_PROVENANCE.md` carries no digest at all** — zero
   64-hex strings in the file. It is a provenance narrative, not a pin, and it
   should not be read as one.
2. **No `.provenance.json` sidecar is committed anywhere.**
   `tools/final_plot_provenance.py` writes one beside every PDF, PNG and
   generated ROOT macro, and binds every output checksum into a run receipt, but
   **none of those sidecars or receipts is in the repository.** The mechanism
   pins outputs at render time; what reaches `HEAD` is the digest a human copied
   into a run record. That is why the MONASH gap was possible.

**The remedy, and it is deliberately not applied here.** Recording the MONASH
digest now would pin a byte string to a figure nobody re-rendered to check, which
records agreement with itself. **The honest fix is to re-render that canvas and
record the receipt**, and it belongs with the figure work that §6.3b currently
blocks. Recorded as a gap rather than closed by writing the number down.


### 2.10 The five closed variation campaigns — decomposition, 2026-08-19

| | |
|---|---|
| product | `results/systematics/20260819/per_category_deltas.json` |
| sha256 | `06bb639200ff01ae150baada8c86e737848da6888592a1b5aeddb7a3d3054981` |
| rendered | `results/systematics/20260819/PER_CATEGORY_DELTAS.md` |
| inputs | `/data/alice/ipardoza/sys_runs/HF_SYS_*/` on Nikhef, 165 directories |
| instrument | the four shas of §2.4, unchanged: reader `4cd8b6fa…`, artifact `ccec0dbc…`, map v2 `58081aa2…`, registry `ea9b0232…` |
| nominal arm | the committed anchors `evidence/merged_{monash,junctions,closepacking}_dedup`, central and ten blocks |

**Regeneration, from the repository plus the Nikhef run root:**

```bash
extraction/harvest_deltas.py \
  --sys-runs /data/alice/ipardoza/sys_runs \
  --anchors evidence \
  --campaigns HF_SYS_MUR_UP HF_SYS_MUR_DOWN HF_SYS_MUF_DOWN \
              HF_SYS_PTHAT_1 HF_SYS_PTHAT_4 \
  --json-out results/systematics/20260819/per_category_deltas.json
```

**Status: DETERMINISTIC-BY-CONSTRUCTION from the run root.** The nominal half
is committed, so the control in `tests/test_harvest_deltas.py` runs from the
repository alone and reproduces `THREE_TUNE_CENTRAL_TABLE.md` §1 to the last
digit.

---

### 2.13 The five closed variation campaigns — per-class and integrated balancing yields, 2026-08-19

| | |
|---|---|
| product | `results/systematics/20260819/per_class_deltas.json` |
| sha256 | `cac0a757ec7bdca04f2390668334733488d95bba14b3f22be2e0216980ad86c2` |
| flat form | `results/systematics/20260819/per_class_deltas.csv`, sha256 `70e07e49d8feeeda9cef5738b2cfaab4ef467a25db511e95e80caf2e38e4bb78` |
| rendered | `results/systematics/20260819/PER_CLASS_DELTAS.md` |
| instrument | `plotting/improvedPlotting_THnSparse.C` sha256 `6dace2025d1edf37…`, through the `measure-balancing` target |
| nominal arm | `figure_deploy_20260817/vintegrated_closure.log`, sha256 `f507f6250e63d82c9c34e088abe4ec16b17359e3b0a54fcdb54e17cd67653d7b`, 144 rows, 2026-08-18 10:18 |
| control | `sys_runs_plot5/render_HF_RUN3_V1.log`, sha256 `690f2dc5694fa8639582e7ff2a5dd42f392c66ab2ccdf1268e9e5974e65afe68` |
| integrated bin | `config/integrated_multiplicity_bin_v1.json`, copied from the closure configuration `793344f36257e72f…` |
| inputs | `complete_root_HF_SYS_*_<TUNE>` and their ten `combined_root_subSamples_<TUNE>` directories, in `/data/alice/ipardoza/hadronization_merged` |

**Regeneration, in two stages.** The renders need Nikhef; the arithmetic does
not.

```bash
# 1. On stbc-i1, six renders through the measurement target.
export HADRONIZATION_BASE=/data/alice/ipardoza/sys_plot_deploy
export MEASUREMENT_WIDEN_AXES=1
export MEASUREMENT_INTEGRATED_BIN=$HADRONIZATION_BASE/config/integrated_multiplicity_bin_v1.json
export MEASUREMENT_PUBLICATION_TREES=$(find /data/alice/ipardoza -maxdepth 4 -type d -name Plots | paste -sd:)
tools/render_measurement.sh HF_RUN3_V1 \
  plotting/configuration_multiplicity_HF_RUN3_V1_THREETUNE_THnSparse_complete_root.json \
  config/dataset_selector_hf_run3_v1.json /data/alice/ipardoza/measurements_v3 render.log
# then once per campaign with its harvest_configs/ configuration and selector row
```

```bash
# 2. Anywhere, from the six logs.
extraction/harvest_class_report.py \
  --nominal vintegrated_closure.log --control render_HF_RUN3_V1.log \
  --variation HF_SYS_MUR_UP=render_HF_SYS_MUR_UP.log \
  --variation HF_SYS_MUR_DOWN=render_HF_SYS_MUR_DOWN.log \
  --variation HF_SYS_MUF_DOWN=render_HF_SYS_MUF_DOWN.log \
  --variation HF_SYS_PTHAT_1=render_HF_SYS_PTHAT_1.log \
  --variation HF_SYS_PTHAT_4=render_HF_SYS_PTHAT_4.log \
  --out results/systematics/20260819/per_class_deltas.json
extraction/write_per_class_report.py \
  --report results/systematics/20260819/per_class_deltas.json \
  --out-markdown tables.md \
  --out-csv results/systematics/20260819/per_class_deltas.csv
```

**Status: REPRODUCIBLE FROM THE LOGS, RE-RENDERABLE ONLY ON NIKHEF.** Stage 2 is
deterministic from the six logs. Stage 1 needs the merged products, which §5 of
this document already lists as not regenerable.

**The control runs in the suite, on real rows.** `tests/fixtures/` carries the
twelve integrated `UNCERTAINTY_MATRIX` rows and the twelve resolver lines from
the nominal, the control and `HF_SYS_PTHAT_4`.
`tests/test_per_class_control.py` reproduces the control agreement and one real
delta from them, so the check runs every suite rather than once.

**Two renders print different digit counts for the same count.** The
figure-branch plotter writes `13656517` and this branch's writes `1.36565e+07`.
The comparison uses agreement at the recorded precision, which is the figure
branch's own method. A string comparison would report a difference that is not
there.

**F4 — GOLDEN_OUTPUTS carries two sections numbered 2.10.** The one at "Closure
at v3 scale" and the one at "The five closed variation campaigns —
decomposition". This entry takes 2.13 to avoid a third collision. Renumbering is
left alone here because the references to these sections live in other
documents.

---

### 2.14 The MONASH-to-JUNCTIONS tune separation, 2026-08-19

| | |
|---|---|
| product | `results/systematics/20260819/tune_separation.json` |
| sha256 | `37aae5bdad84dc6652399b2c77ddc6ae9c6c91df5073df6af1510d560315befd` |
| rendered | `results/systematics/20260819/TUNE_SEPARATION.md` |
| input | `figure_deploy_20260817/vintegrated_closure.log`, sha256 `f507f6250e63d82c9c34e088abe4ec16b17359e3b0a54fcdb54e17cd67653d7b` |
| instrument | `extraction/write_tune_separation.py` |

**Regeneration, from the one log:**

```bash
extraction/write_tune_separation.py \
  --nominal vintegrated_closure.log \
  --out-json results/systematics/20260819/tune_separation.json \
  --out-markdown TUNE_SEPARATION_tables.md
```

**Status: DETERMINISTIC FROM ONE LOG.** It reads the sealed nominal and nothing
else. No variation campaign enters it, which is why it exists while the
combination does not.

**Three observables, twelve classes: the B⁺–B⁻ and B⁺–Λ_b balancing yields and
the Λ_b/B⁻ ratio.** The ratio takes the plotter's `ratio_sem` rather than
propagating the two yield SEMs, because numerator and denominator share their
triggers and their events.

**The class axis runs opposite to its label.** `c1` is `N_ch` 0 to 2 and `c11`
is `N_ch` 33 and above, because the window label is a top percentile.
`tests/test_harvest_class_axis.py` holds that against
`config/multiplicity_class_boundaries_v1.json`.

### 2.15 The per-class combination — BUILT, NOT RUN

| | |
|---|---|
| instrument | `extraction/combine_per_class.py` |
| product | **none. It refuses.** |
| refusal | `COMBINATION_REFUSED missing=HF_SYS_MUF_UP,HF_SYS_PDF_CTEQ6L1` |
| tests | `tests/test_combine_per_class.py`, 25 hand-computed checks |

**Recorded here as an absence on purpose.** A tool that exists and produces
nothing is easy to mistake for a tool that was never written, and the next
session needs to know the wiring is done and tested.

**To run it once all seven campaigns hold deltas:**

```bash
extraction/harvest_class_report.py --nominal … --control … \
  --variation HF_SYS_MUF_UP=… --variation HF_SYS_PDF_CTEQ6L1=… \
  … --out per_class_deltas.json
extraction/combine_per_class.py \
  --report per_class_deltas.json \
  --out results/systematics/20260819/per_class_combination.json
```

It applies owner amendment A1 and A2, pre-registration §9.1 and §2.5, and S5's
measured zero. It adds no rule of its own.

---

### 2.16 The Λ_b/B⁻ multiplicity trend, 2026-08-19

| | |
|---|---|
| product | `results/systematics/20260819/ratio_trend.json` |
| sha256 | `b1b5954812398d748297111ab64375d2abecfb4d04b3e98ff3ccdf8d9890087e` |
| rendered | `results/systematics/20260819/RATIO_TREND.md` |
| input | `figure_deploy_20260817/vintegrated_closure.log`, sha256 `f507f6250e63d82c9c34e088abe4ec16b17359e3b0a54fcdb54e17cd67653d7b` |
| instrument | `extraction/write_ratio_trend.py` over `extraction/ratio_trend.py` |
| tests | `tests/test_ratio_trend.py`, 22 hand-computed checks |

**Regeneration, from the one log:**

```bash
extraction/write_ratio_trend.py \
  --nominal vintegrated_closure.log \
  --out-json results/systematics/20260819/ratio_trend.json \
  --out-markdown RATIO_TREND_tables.md
```

**Status: DETERMINISTIC FROM ONE LOG.** No variation campaign enters it, which
is why it exists while the combination does not.

**Two estimators, and the model-free one is the measurement.** `R(c11) − R(c1)`
subtracts two rows and needs no fit and no x-axis convention. The weighted
straight line in class index is a summary, and its χ²/ndf of 8.18 for JUNCTIONS
records that a line does not describe that tune.

**The fit's x-axis is the class index**, which is not equally spaced in `N_ch`:
`c1` spans three units and `c11` is open above its 32.5 edge, so it holds N_ch
33 and above. A slope "per class" is therefore not a physical `d(ratio)/dN_ch`.

---

### 2.17 All seven campaigns — combination and verdict, 2026-08-20

> **2026-08-21 correction.** The `verdict.json` digest below is schema v2 and
> supersedes the 2026-08-20 v1 digest after applying the documented nominal-
> plus-variation SEM rule. The campaign inputs and central values did not
> change. The dated run record remains historical evidence and is not edited.

| product | sha256 |
|---|---|
| `systematics_results_20260820/per_class_deltas_seven.json` | `e8fe560f378161c8d8ee45f5919cc1ff9ca3984b4a109ce02763968067ade023` |
| `systematics_results_20260820/per_class_deltas_seven.csv` | `94ca520244e8d2f7f8a609bcead9eea1b83ca5da04ebb27e5a51acab761c6437` |
| `systematics_results_20260820/per_class_combination.json` | `8a8a26b8e676145a210cddd6952b23fc69c57cebfc3733fac0d1d810870cfc57` |
| `systematics_results_20260820/per_class_combination.csv` | `0f51596de6567346dc408dbd4cacae170cc548a2a545a3d6e741af198d70214d` |
| `systematics_results_20260820/verdict.json` | `7ecedf3abf5e8d65c99d1d3ea1be8bfd53b0d8e67796211c6650b7e8485a5d5a` |
| `systematics_results_20260820/per_category_final_two.json` | `db34411a3fd06b6c6eaecdfb253e3ffe9dfa13bbfb65163bd3d61e1a8d9e1bb1` |

**Inputs — the render logs.** The nominal is unchanged at
`f507f6250e63d82c…`. The five variation logs of 2026-08-19 are unchanged. The
three rendered 2026-08-20:

| log | sha256 |
|---|---|
| control `render_HF_RUN3_V1.log` | `5cdcbfbba2474dfb9cf87730f882459176e0be2ecc14d32126e89637cd908906` |
| `render_HF_SYS_MUF_UP.log` | `eed5be6e5e67c94604eee0a29d38dbe3498183347dafeb10a3848e86aabcd74e` |
| `render_HF_SYS_PDF_CTEQ6L1.log` | `f9439e9e0a4e97da156741957cc9c0e009be2cf2610876085228c155b064cf88` |

**Regeneration, in three stages.** Only the first needs Nikhef.

```bash
# 1. On stbc-i1: extraction and renders for the two campaigns, plus the control.
SYS_EXTRACT_PARALLEL=6 bash systematics_harvest/sys_extract.sh HF_SYS_MUF_UP
SYS_EXTRACT_PARALLEL=6 bash systematics_harvest/sys_extract.sh HF_SYS_PDF_CTEQ6L1
# renders: MEASUREMENT_WIDEN_AXES=1, MEASUREMENT_INTEGRATED_BIN set, per GOLDEN_OUTPUTS 2.13
```

```bash
# 2. Anywhere, from the eight logs.
extraction/harvest_class_report.py --nominal vintegrated_closure.log \
  --control render_HF_RUN3_V1.log --variation <CAMPAIGN>=<LOG> x7 \
  --out per_class_deltas_seven.json
extraction/combine_per_class.py --report per_class_deltas_seven.json \
  --out per_class_combination.json
extraction/write_verdict.py --nominal vintegrated_closure.log \
  --variation <CAMPAIGN>=<LOG> x7 --out-json verdict.json --out-markdown VERDICT_tables.md
```

```bash
# 3. The renderers.
extraction/write_combination_report.py --combination per_class_combination.json \
  --out-markdown COMBINED_tables.md --out-csv per_class_combination.csv
extraction/write_per_class_report.py --report per_class_deltas_seven.json \
  --out-markdown tables.md --out-csv per_class_deltas_seven.csv
```

**Status: STAGES 2 AND 3 ARE DETERMINISTIC FROM THE EIGHT LOGS.** Stage 1 needs
the merged products, which §5 lists as not regenerable.

**The systematic on a difference is computed ON the difference.** For every
source the quantity is recomputed from that source's own render and differenced
against the nominal, so whatever cancels inside it has cancelled before the
combination. Borrowing a single tune's per-class systematic would double-count
the part that cancels.

**Two controls, not one.** The control render reproduces the sealed nominal on
all 144 rows, and it is **byte-identical to the 2026-08-19 control**, so the
five logs rendered then and the three rendered now come from one instrument.

**The campaign configurations are generated.** `tools/make_harvest_configs.py`
derives all seven from the central by six field substitutions, and reproduces the
five pre-existing files byte-for-byte.
