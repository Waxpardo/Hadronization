# REPRODUCE — how each file in this package was made

One page, so that "how was this figure made?" is answered without reading a
session report. Every command below is the command that actually ran, copied
from the script that ran it in the RUN-N4b and RUN-N evidence stores.

Nothing here was produced on the bench. **`R29`: the deployment is the final
architecture and a Mac result is never a substitute for one.** Every figure in
this package was rendered at the Nikhef deployment

```
/data/alice/ipardoza/hf/project/deploys/hadronization-clean-20260822
```

at repository HEAD `6729b3f0b7b94278b06a21943da669d6df737cc0`, and every T1
number at HEAD `fe3262c729ec5a6b942309da45a70efdb2fe7fb4`.

## Before anything

```bash
cd /data/alice/ipardoza/hf/project/deploys/hadronization-clean-20260822
. ./setupEnv.sh
export HADRONIZATION_DATASET=hf_run3_v1_candidate
```

`HADRONIZATION_DATASET` must be exported: the render wrapper names no dataset
and `config/dataset_selector.json` declares no default. The launcher exports
the same variable at `hadronization:90`.

**The suite is the opposite case.** `tools/run_tests.sh` must run with
`HADRONIZATION_DATASET` **unset**; exporting it turns
`test_dataset_selector.py`, `test_dataset_selector_hf_pt2.py` and
`test_measurement_target.py` red. Measured this session.

## G2, G3, G4, G5, G6, G7, G8 — the configuration-driven renders

Each is one call to the confirming wrapper against one generated configuration.
The wrapper prints five `RENDER_VARIANT` lines on success and exits 5 if the
intended configuration is not the loaded one.

```bash
HADRONIZATION_BASE="$PWD" tools/render_balancing_variant.sh \
  plotting/configuration_multiplicity_HF_RUN3_V1_<TAG>.json \
  "$HADRONIZATION_RESULTS_ROOT/HF_RUN3_V1/6729b3f0b7b9/measurements/hf_run3_v1_candidate/render_<TAG>.log"
```

| figures | `<TAG>` | configuration sha256 at the render | render log sha256 |
|---|---|---|---|
| G2, G3 | `VCORRELATIONS` | `e7962d9020e6fdf7473981fc2cc848a0952a28eb4d74f574eb631cfcdbf0ed7d` | `cbb50cf370d16c69719e2c8c1c58aa674cedfbd981e9e39786dd47465471840e` |
| G4, G6 | `VINTEGRATED` | `da461f57a9b46ff628669f27f1071cdd6fb49c59162cee638a7a8d3069dc13b4` | `8582a83555c63ddf717e7a10ae2dd9d88cb9c448310ed382308e256257c2cbd2` |
| G5, G7 | `VEXTREMES` | `4c951e45ce9608c2463cad9b506de98dba70f4f57b0d0343aa6134047b6e9326` | `fa1e4b06aea7782fe9a2fed90f1e9746d904f5563178f5c4c9f9eee415961e2c` |
| G8 | `VBARYONMESON` | `ab975f663346081147be5b45b732afa01d36ef356b581547b08d2dd6cd0bc102` | `66d757e85779468dd3c1931f780797de1bffbf980702b742a1559e38b123a47b` |

**All four configurations still carry those exact sha256 at this package's
HEAD, and nothing under `plotting/` or `tools/` changed between the render HEAD
and this one** (VERIFIED,
`HANDOFF_EVIDENCE_3cccb75_20260901/verify/config_sha_at_head.txt`). A reproducer therefore
needs no archaeology: check the four digests out of the current tree.

The configurations are generated, not hand-written. To regenerate them:

```bash
python3 tools/make_variant_configs.py
```

## G1 and G9 — the explicit launcher targets

```bash
./hadronization plot hf_run3_v1_candidate multiplicity-spectrum   # G1
./hadronization plot hf_run3_v1_candidate kinematic-spectra       # G9
```

| figure | target | render log sha256 |
|---|---|---|
| G1 | `multiplicity-spectrum` | `6f97ed6cdfc23cd612e40e1762ad7ee0e57a80f4c28723f60a5c8d87d567c613` |
| G9 | `kinematic-spectra` | `4ff7c0346e78f7263f59f37a4db972bb41f5151df3bd11e70bc0c774186b9358` |

**The order is binding: `multiplicity-spectrum` before `kinematic-spectra`.**
The two targets share the G1 stem and the second rewrites it. RUN-N2 measured
that rewrite from the ROOT timestamps in the delivered `.C` and `.pdf`
(finding F-N2-1), and `docs2/pipeline/RENDER.md` states the order.

## T1 — the generated-sample counts

Produced by RUN-N at HEAD `fe3262c729ec`, against the raw plane through the
sealed canonical manifest for the counts and the merged products for `N_ev`.
Nothing has re-counted them since; RUN-N4 and RUN-N4b re-rendered figures only.

```bash
for TUNE in MONASH JUNCTIONS CLOSEPACKING; do
  root -l -b -q "tools/count_generated_sample.C(\"$EV/count/filelist_${TUNE}.txt\",\"$EV/count/t1_${TUNE}.json\",\"${TUNE}\")"
  root -l -b -q "tools/read_merged_event_counts.C(\"$MERGED/complete_root_HF_RUN3_V1_${TUNE}/BplusBminus.root\")"
done
```

with

```
EV=/data/alice/ipardoza/hf/project/RUNN_EVIDENCE_fe3262c_20260830
MERGED=/data/alice/ipardoza/hf/hadronization_merged
```

| | |
|---|---|
| `tools/count_generated_sample.C` sha256 | `ffb0ff3b20883cfd41374802f23fedaa810a5733ef25094903da4a13181d6f39` |
| `tools/read_merged_event_counts.C` sha256 | `88657e8471d0aae6424e401b3ba3be92b2ca303884b7ad30b581a3d5c04e948a` |
| chain log sha256 | `2b69f10adbc838732db04445b887611fd4548f6ee5df2a999021d173b0e1c005` |
| elapsed, per tune | about 2,500 s |

Both merged counters, `input_events` and `source_input_events`, are read and
asserted equal; the tool refuses a number when they disagree. All three tunes
printed `n_ev=100000000 input_events=100000000 source_input_events=100000000
agree=yes`.

`tables/T1_generated_sample.tex` was assembled on the bench by this session
from the three certified `.tex` bodies. It runs no macro and reads no ROOT
file.

## The rename, which is a handoff step and not a render step

The correlation canvas builds its stem from the flavour token, which is upper
case in the macro — `Form("%sCorrelations_MONASH", FLAVOUR)`
(`plotting/improvedPlotting_THnSparse.C:5181`). The render writes
`CHARMCorrelations_MONASH_PDF.pdf` and `BEAUTYCorrelations_MONASH_PDF.pdf`;
the manuscript includes `Charm…` and `Beauty…`.

This package renames `CHARM` → `Charm` and `BEAUTY` → `Beauty`, and changes
nothing else in either name. The bytes are untouched: both files carry the same
sha256 before and after the rename, which `MANIFEST.md` records and the
build check asserts.

## What certifies that the style pass moved no number

RUN-N4b rendered every target once at `6729b3f` and proved, for each of the
five configurations, that every `PAIR_COUNTS` and `UNCERTAINTY_MATRIX` row is
sequence-identical to RUN-N4's — 1,530 and 422 rows. RUN-N4 had already proved
its own logs identical to RUN-N, RUN-N2 and RUN-N3, so the chain reaches the
certified predecessors unbroken. For G1 and G9 the per-tune
`files=1000 … entries=100000000` lines and the
`MULTIPLICITY_PER_TUNE_BOUNDARIES … status=PASS` line equal RUN-N4's exactly,
including the selected-particle counts re-derived from 265 GiB of raw data.

REPORTED from `RUNN4B_REPORT_20260901.md` and
`RUNN4_EVIDENCE_6729b3f_20260901/`; this session re-ran none of it.
