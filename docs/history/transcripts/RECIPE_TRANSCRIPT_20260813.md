# Golden Output recipe transcript — 2026-08-13

**Every repo-only recipe executed EXACTLY as written in `docs/GOLDEN_OUTPUTS.md`
§4**, after the A8 fixes (executable bits, R7's `--mode split`, R8's relabel).
No recipe was rewritten to make it run, and no `python3` prefix was substituted
for a missing executable bit — that substitution is what the previous review had
to do, and it is what R6/R7/R10 now no longer need.

## Verdicts

| # | ran | notes |
|---|---|---|
| R1–R4b | ✅ | registry, both generated-header `--check`s, both card targets |
| R5 | ✅ | `map_sha256=dd502a10c5932fff`, `I1=PASS I2=PASS I2a=PASS(202 vs production)` |
| R6 | ✅ | `sha256=c9593c9c0a7c4ec2 split=2` — **was exit 126, permission denied** |
| R7 | ✅ | D⁰ **25.2435** — **was exit 126**, and as previously written produced the v1.1 shares (28.1301) because `--mode` defaults to `dominant` |
| R8 | ✅ | `at_risk_pct=12.8396` — the **(C) chained history** row, now labelled as such |
| R9 / R9b | ✅ | beauty and charm M7 tables reproduced from committed logs |
| R10 | ✅ **rc=1 BY DESIGN** | `flagged=30 tested=88` — the documented positive check. It exits non-zero *because* it flags; the harness's rc==0 verdict is the wrong test here, which is `rc=0 is not evidence` running in the other direction |
| R11 | ✅ | `35/35 passed` |
| R12 | ✅ | new: the E5 deduplication reconstruction |

**Not run:** §3b, which begins with `make submit-smoke` — it renders and submits
jobs and writes campaign/ledger state. It also needs the pinned PYTHIA/CVMFS/
Condor environment, which this host does not have.

**Environment caveat, stated because the transcript would otherwise imply
more than it shows:** ROOT here is **6.38.04 from Homebrew**, not the pinned
6.30.01, and there is no PYTHIA. Every recipe above is pure Python except R11.
See `docs/GOLDEN_OUTPUTS.md` §4 on what `make check` does not certify (A7).

---

```text
RECIPE TRANSCRIPT  2026-08-12T23:48:45Z
commit : 8f410a43b5dc194a05d17f774a5ae393377c0d91
tree   : 6 modified paths
host   : Darwin 24.6.0 arm64
python : Python 3.13.12
root   : /opt/homebrew/bin/root  6.38.04
======================================================================

=== R1 ===============================================
$ make registry
registry artifacts current: 50 signed states, 300 signed pairs
--- rc=0   expect: no STALE
--- VERDICT: ran clean

=== R2 ===============================================
$ python3 tools/generate_species_ordinals_header.py --check
SPECIES_ORDINALS_CURRENT species=202 digest=646f310f78126267
--- rc=0   expect: no *_STALE
--- VERDICT: ran clean

=== R3 ===============================================
$ python3 tools/generate_pair_object_contract.py --check
PAIR_OBJECT_CONTRACT_CURRENT objects=66
--- rc=0   expect: no stale marker
--- VERDICT: ran clean

=== R4 ===============================================
$ make cards
TUNE_CARD_DIFFERENCE StringFragmentation:doStrangeJunctions MONASH=<PYTHIA_DEFAULT> JUNCTIONS=<PYTHIA_DEFAULT> CLOSEPACKING=on
TUNE_CARD_DIFFERENCE StringFragmentation:enhanceStrangeJunction MONASH=<PYTHIA_DEFAULT> JUNCTIONS=<PYTHIA_DEFAULT> CLOSEPACKING=0.540
TUNE_CARD_DIFFERENCE StringPT:sigma MONASH=<PYTHIA_DEFAULT> JUNCTIONS=0.335 CLOSEPACKING=0.335
TUNE_CARD_DIFFERENCE StringZ:aLund MONASH=<PYTHIA_DEFAULT> JUNCTIONS=0.36 CLOSEPACKING=0.68
TUNE_CARD_DIFFERENCE StringZ:bLund MONASH=<PYTHIA_DEFAULT> JUNCTIONS=0.56 CLOSEPACKING=0.98
TUNE_CARD_DIFFERENCE StringZ:useOldAExtra MONASH=<PYTHIA_DEFAULT> JUNCTIONS=<PYTHIA_DEFAULT> CLOSEPACKING=off
--- rc=0   expect: both exit 0
--- VERDICT: ran clean

=== R4b ===============================================
$ make cards-current
CARD_CONFIG_CURRENT every card matches the declared values
--- rc=0   expect: both exit 0
--- VERDICT: ran clean

=== R5 ===============================================
$ tools/build_decay_parent_map.py AnalysisScripts/anchors/f4_probe/f4_probe_v1.out --ordinals AnalysisScripts/species_ordinals_v2.json --out /tmp/v11.json
DECAY_PARENT_MAP species=202 with_dominant_channel=202 pythia=8.317 gate=READABLE_AFTER_DISABLE map_sha256=dd502a10c5932fff
CONJUGATION artifact_rows_changed=101 table_affecting_rows=60 involution_pairs=101 I1=PASS I2=PASS I2a=PASS(202 vs production)
wrote /tmp/v11.json
--- rc=0   expect: map_sha256=dd502a10c5932fff, I1=PASS I2=PASS
--- VERDICT: ran clean

=== R6 ===============================================
$ tools/build_decay_parent_map_v2.py AnalysisScripts/anchors/f4_probe/f4b_probe.out --ordinals AnalysisScripts/species_ordinals_v2.json --v1 AnalysisScripts/decay_parent_map_v1_1.json --weights AnalysisScripts/anchors/extraction_dual/per_species.csv --out /tmp/v2.json
MAP_V2_BUILT species=202 split=2 threshold=0.1% sha256=c9593c9c0a7c4ec2
  SPLIT D*-        Dbar0=0.6770 D-=0.3230
  SPLIT D*+        D0=0.6770 D+=0.3230
--- rc=0   expect: sha256=c9593c9c0a7c4ec2, split=2
--- VERDICT: ran clean

=== R7 ===============================================
$ extraction/apply_decay_map.py --map AnalysisScripts/decay_parent_map_v2.json --weights AnalysisScripts/anchors/merged_monash_central/per_species.csv --mode split
  FLAG    4424: antiparticle bin EMPTY (particle 48)
  FLAG    4434: antiparticle bin EMPTY (particle 48)
  FLAG    5342: antiparticle bin EMPTY (particle 26)
  FLAG    5412: antiparticle bin EMPTY (particle 26)
  FLAG    5422: antiparticle bin EMPTY (particle 26)
ADVISORY_FLAGGED 11
--- rc=0   expect: D0 25.2435 (needs --mode split)
--- VERDICT: ran clean

=== R8 ===============================================
$ extraction/second_branch_weight.py --per-species AnalysisScripts/anchors/merged_monash_central/per_species.csv
B*_c+               3   0.2020           45928      36650.544  0.0028
B*_c-               3   0.2020           42798      34152.804  0.0026
B_c-                2   0.2020           20418      16293.564  0.0013
B_c+                2   0.2020           19942      15913.716  0.0012

SECOND_BRANCH_DONE at_risk_pct=12.8396 concentration_top4=97.81%
--- rc=0   expect: at_risk_pct=12.8396 -- the (C) chained HISTORY row, not THE NUMBER
--- VERDICT: ran clean

=== R9 ===============================================
$ extraction/aggregate_m7.py AnalysisScripts/anchors/m7b_blocks/m7b_block_01.log AnalysisScripts/anchors/m7b_blocks/m7b_block_02.log AnalysisScripts/anchors/m7b_blocks/m7b_block_03.log AnalysisScripts/anchors/m7b_blocks/m7b_block_04.log AnalysisScripts/anchors/m7b_blocks/m7b_block_05.log AnalysisScripts/anchors/m7b_blocks/m7b_block_06.log AnalysisScripts/anchors/m7b_blocks/m7b_block_07.log AnalysisScripts/anchors/m7b_blocks/m7b_block_08.log AnalysisScripts/anchors/m7b_blocks/m7b_block_09.log AnalysisScripts/anchors/m7b_blocks/m7b_block_10.log
counts and baryon enrichment of the dropped sample:
  CLOSEPACKING   unresolved_n=    27184  resolved_n=  27631664  unresolved_baryon%= 37.066  enrichment= 1.15x
  JUNCTIONS      unresolved_n=    28315  resolved_n=  27659509  unresolved_baryon%= 36.387  enrichment= 1.14x
  MONASH         unresolved_n=     3170  resolved_n=  27645508  unresolved_baryon%= 10.852  enrichment= 2.23x

SEM is over the ten canonical blocks (n=10); central values are from pooled counts, not averaged ratios.
--- rc=0   expect: reproduces 2.8 beauty; fail-closes below 10 blocks
--- VERDICT: ran clean

=== R9b ===============================================
$ extraction/aggregate_m7.py AnalysisScripts/anchors/m7_blocks/m7_block_01.log AnalysisScripts/anchors/m7_blocks/m7_block_02.log AnalysisScripts/anchors/m7_blocks/m7_block_03.log AnalysisScripts/anchors/m7_blocks/m7_block_04.log AnalysisScripts/anchors/m7_blocks/m7_block_05.log AnalysisScripts/anchors/m7_blocks/m7_block_06.log AnalysisScripts/anchors/m7_blocks/m7_block_07.log AnalysisScripts/anchors/m7_blocks/m7_block_08.log AnalysisScripts/anchors/m7_blocks/m7_block_09.log AnalysisScripts/anchors/m7_blocks/m7_block_10.log
counts and baryon enrichment of the dropped sample:
  CLOSEPACKING   unresolved_n=  2271517  resolved_n= 197779600  unresolved_baryon%= 25.091  enrichment= 1.45x
  JUNCTIONS      unresolved_n=  2317799  resolved_n= 198706525  unresolved_baryon%= 26.358  enrichment= 1.48x
  MONASH         unresolved_n=   168003  resolved_n= 198163563  unresolved_baryon%=  7.134  enrichment= 1.53x

SEM is over the ten canonical blocks (n=10); central values are from pooled counts, not averaged ratios.
--- rc=0   expect: reproduces 2.7 charm
--- VERDICT: ran clean

=== R10 ===============================================
$ extraction/compare_subset_parent.py AnalysisScripts/anchors/extraction_dual/per_species.csv AnalysisScripts/anchors/merged_monash_central/per_species.csv --expect-scale 9.9986
      71                     167952       1696848     169708.7   -4.50
     102                   11621688     116061528   11607790.1    4.30
     113                     932022       9356828     935814.8   -4.13
     128                     172632       1742088     174233.4   -4.04
     100                   13310136     132942888   13296164.2    4.04
SUBSET_PARENT_COMPARE flagged=30 tested=88 scale=9.9986
--- rc=1   expect: exactly 30 bins flagged
--- VERDICT: FAILED (rc=1)

=== R12 ===============================================
$ tools/reconstruct_deduplicated_decomposition.py
PUBLISHED (replicated) total : 1,298,655,240
DEDUPLICATED total           : 53,662,413.8 .. 53,662,827.8
  residual ambiguity         : 414.0 counts (0.000771 %)
  inflation factor           : 24.2003 .. 24.2005
wrote /Users/wax/Documents/Research/Projects/Hadronization-physics-focus/AnalysisScripts/anchors/merged_monash_central/per_species_deduplicated.csv
wrote /Users/wax/Documents/Research/Projects/Hadronization-physics-focus/AnalysisScripts/anchors/merged_monash_central/per_category_deduplicated.csv
--- rc=0   expect: charm 24x beauty 26x; 87 exact + 8 bracketed
--- VERDICT: ran clean

=== R11 (make test) ===================================
$ make test
  PASS test_statistical_robustness.py
  PASS test_submit_rendering.py
  PASS test_validate_raw_output_strict_compile.py
  35/35 passed
--- rc=0
--- VERDICT: ran clean

======================================================================
SUMMARY: 13 ran clean, 1 failed
```
