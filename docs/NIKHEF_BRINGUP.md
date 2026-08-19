# Nikhef bring-up checklist

The shell pipeline has been rewired and no longer references any deleted
module. **None of the ROOT/PYTHIA paths have been executed** — that is
impossible off-cluster. What follows is the order to bring it up on Nikhef,
smallest irreversible step first.

What *is* verified, on macOS with no ROOT: argument validation and every guard
rail in `runCondorJob.sh`, submit rendering at full scale (4000 rows, 4000
unique seeds), tune-card minimality, registry currency, and 21/21 contract
tests.

---

## 1. Workspace

```bash
make setup      # then edit config/dependencies.local.conf
make doctor
```

`make doctor` must report zero blocking items. On Nikhef the two that block off
cluster — the PYTHIA prefix and the CVMFS ROOT package — resolve.

**Set `HF_PRODUCTION_ROOT`** to a directory under `/data/alice`. It defaults to
`<checkout>/Production`, which would put ~360 GB of raw output inside the git
working tree.

Confirm free space before the full campaign. `/data/alice` was last seen at 96%
used with 1.6 TB free; four tunes at 100M events each is roughly 360 GB.

## 2. Build

```bash
make build
make check
```

`make build` is the first thing that exercises the 8.317 migration and the
rpath fix end to end. It must produce zero warnings.

## 3. Settle the CLOSEPACKING question

```bash
root -l -b -q 'Validation/AuditTuneSettings.C'
```

Card text shows CLOSEPACKING restating what look like the Monash fragmentation
values while MONASH leaves them to `Tune:pp = 14`. If the resolved values match,
**MONASH vs CLOSEPACKING is already unconfounded for baryon observables** — a
materially different claim from the one the paper draft currently concedes.
This macro reads the values PYTHIA actually resolves. Do not assert it from the
cards.

## 4. Re-establish Gate-A calibration on 8.317

```bash
root -l -b -q 'Validation/CalibrateMultiplicityAgainstMinBias.C(20000,false,10.0,false)'
```

Expect `dN_ch/deta ~ 6.97` against ALICE `6.94 +/- 0.10`. This was measured on
8.317 already; re-run it after the rebuild so the number belongs to the binary
that will produce.

## 5. Single-job smoke test

Before any batch, run one job by hand — this is the first execution of the
rewritten worker:

```bash
./generation/submit/runCondorJob.sh --campaign SMOKE 1 MONASH 0 primary 0 100000001 1000 \
  NONE 0 $(git rev-parse HEAD) \
  $(python3 tools/campaign.py card-sha256 \
      generation/cards/pythiasettings_Hard_Low_ccbb_MONASH.cmnd --events 1000) \
  $(sha256sum SimulationScripts/heavyflavourcorrelations_status | awk '{print $1}') \
  0 0
```

1000 events, seconds to run. Confirm it prints `PROMOTED`, that the raw file
and its `.sha256` sidecar exist under `$HF_PRODUCTION_ROOT/SMOKE/raw/MONASH/`,
and that the attempt metadata and validation receipt were written. Repeat once
for `JUNCTIONS_MATCHED` — that tune has never been run at all.

Then delete the SMOKE campaign directory; those seeds are burned, so record
them or use a throwaway ledger.

## 6. Preliminary campaign

```bash
make submit-prelim CAMPAIGN=HF_RUN3_PRELIM
condor_submit submit_HF_RUN3_PRELIM_prelim.sub
```

200 jobs, 5M events per tune, ~18 GB. Its purposes, in order:

1. prove the pipeline end to end under Condor;
2. exercise the wall-time guard against the junction hang — JUNCTIONS and
   CLOSEPACKING are the tunes that wedge, and at 100k events a hang now costs
   a tenth of what it did;
3. show whether MONASH, JUNCTIONS, CLOSEPACKING and JUNCTIONS_MATCHED separate
   at all on the baryon-partner observable.

Record the held-job count. A job held by `periodic_hold` is a suspected hang;
that rate is the first real measurement of it, since the 1.1e-6/event figure is
an incident count, not a measurement, and is in ~1.2% tension with 4M events of
clean running.

## 7. Full campaign

Only after the preliminary analyses cleanly:

```bash
make submit-full CAMPAIGN=HF_RUN3_V1
condor_submit submit_HF_RUN3_V1_full.sub
```

4000 jobs, 100M events per tune, 400M total.

---

## Still outstanding, not blocking submission

- **`statistical_robustness.py` (2761 lines)** and
  **`evaluate_pthat_sensitivity.py` (2124 lines)** are untouched and oversized.
  Both were left alone deliberately: rewriting error-bar code without deciding
  what it should compute risks a physics error rather than a style one.
- **No systematic uncertainties** are computed anywhere. The unresolved-fraction
  sensitivity is tune-dependent and currently unpropagated.
- **The pTHat decision** remains unresolved. Percentile multiplicity classes
  must not appear in a figure, or be described as comparable to experimental
  multiplicity classes, until it is.
- **No LICENSE**, no CI, no container, no DOI.
