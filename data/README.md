# Data access and results

[Documentation index](../README.md#documentation)

The `HF_RUN3_V1` result contains 300 million successful events from 3,000 accepted sources. MONASH, JUNCTIONS and CLOSEPACKING each contribute 100 million events in ten original blocks.

## Included results

The [collaboration package](results/manifest.json) contains the numerical ROOT, 41 figure PDFs, ROOT canvases, tables and exact manifests. The [numerical report](results/numerical/report.json) records 49,050 points with separate value and uncertainty statuses. Missing values remain explicit.

| Product | Location | Use |
| --- | --- | --- |
| Numerical authority | [numerics.root](results/numerical/numerics.root) | Values, covariance factors, statuses and provenance |
| Figure package | [figures](results/figures) | Paper figures, supporting views and signed heavy-hadron spectra |
| Tables | [exports](results/numerical/exports) | Accounting, exact CSV values, TeX tables and missing states |
| Selected presentation | [plot.json](results/config/plot.json) | Exact configuration for the distributed figures |
| Source inventory | [raw_manifest.jsonl](raw_manifest.jsonl) | Accepted raw identities, original blocks, bytes and SHA-256 values |
| Sample definition | [campaign.json](campaign.json) | Collision setup, tunes, source rules and provenance |
| Attempt inventory | [attempts.csv](attempts.csv) | 3,127 attempts, including 127 discarded attempts |

The raw inventory records 284,750,292,184 ROOT bytes. The attempt ledger does not provide event-trial counts for every attempt. The accounting table preserves this missing state.

## Verify or change figures

Package verification needs the matching renderer runtime: ROOT 6.30.01 and GCC 14.2.0. Configure the environment as described in [installation](../docs/installation.md). The verifier writes its build files outside the result package.

```sh
mkdir -p data/work/tmp
export TMPDIR="$PWD/data/work/tmp"
PACKAGE_SHA=4f716d6e77845658d37037349645ae17da83f9913f5ed5f4a530ee8980b45270
./hadronization package verify \
  --package data/results --manifest-sha256 "$PACKAGE_SHA" \
  --work-dir data/work/release-verification
```

The checked-out Git revision supplies the trusted manifest bytes. Compare that revision with the release tag before verification. The verifier checks every packaged file against the manifest.

To change the presentation, copy `config/plot.json` and edit its display settings. Use the example below with a new output directory. The numerical ROOT and its statistical results remain unchanged.

```sh
cp config/plot.json data/work/custom-plot.json
./hadronization plot render-cold \
  --numerics-root data/results/numerical/numerics.root \
  --expected-root-sha256 e9962a266ce5c033f72f68ec65dfbea1aa9e140911094d5fec37e298b076818b \
  --expected-value-sha256 d6c2b76aa44432caf55b734854558fdfda5ffb0339ca8b397e5298472d3b1143 \
  --plot-config data/work/custom-plot.json \
  --work-dir data/work/custom-render --output data/work/custom-figures
```

## Download merged ROOT

The [GitHub release](https://github.com/Waxpardo/Hadronization/releases/tag/hf-run3-v1-20260922) distributes the three completed ROOT files. The files occupy 7,001,982,338 bytes together. Each file contains five sparse families with ten original blocks. The [download manifest](merged-download.json) binds every transfer part and complete ROOT file to its size and SHA-256.

| File | Tune | Bytes |
| --- | --- | --- |
| `tune-00.root` | MONASH | 2,351,995,149 |
| `tune-01.root` | JUNCTIONS | 2,404,877,890 |
| `tune-02.root` | CLOSEPACKING | 2,245,109,299 |

Each file exceeds GitHub's release-asset limit. The downloader concatenates transfer parts to restore the original bytes. This operation does not run ROOT or repeat the scientific merge.

Allow 15 GB of free local storage for ROOT files, cached parts and temporary output. This command needs network access to GitHub. It needs neither site credentials nor ROOT.

```sh
python3 data/fetch-merged.py --output data/work/merged
python3 data/fetch-merged.py --output data/work/merged --verify-only
```

The downloader retains complete parts in `.parts` under the output directory. A restart reuses parts only after checksum verification. It refuses different existing files and symbolic output paths. A failed transfer cannot replace a completed ROOT file. Interrupted partial transfers restart from the affected part.

For parts downloaded through a browser or another transfer tool, use `--local-parts DIRECTORY`. The command checks the same hashes before restoring ROOT files. `--verify-only` reads the complete files without network access or filesystem changes.

## Explore sparse projections

The files retain activity, trigger, pair, kinematic and closure histograms. Object names follow `sparse_FAMILY__block_NN`, where `NN` ranges from `01` to `10`. The [collection index](merged/index.json) lists every object and its block. The [dictionary](merged/dictionary.json) defines signed-PDG ordinals. See the [axis reference](../docs/data-model.md#sparse-axes) before selecting bins.

With PyROOT installed, this example projects the full MONASH activity count from all ten blocks:

```sh
python3 - <<'PYCODE'
import ROOT
ROOT.gROOT.SetBatch(True)
f = ROOT.TFile.Open("data/work/merged/tune-00.root", "READ")
assert f and not f.IsZombie()
total = None
for block in range(1, 11):
    h = f.Get("sparse_activity__block_%02d" % block)
    assert h and h.GetAxis(2).GetName() == "a15_eta4"
    ROOT.SetOwnership(h, True)
    projection = h.Projection(2)
    projection.SetDirectory(0)
    if total is None:
        total = projection
    else:
        total.Add(projection)
    del h
count = total.Integral(0, total.GetNbinsX() + 1)
assert count == 100000000
print("MONASH events:", int(count))
f.Close()
PYCODE
```

Keep block contributions separate when constructing a new estimator. THnSparse Sumw2 errors are not the jackknife covariance. Use the [statistical method](../docs/science.md#jackknife-and-covariance) for nonlinear estimates and tune comparisons.

Merged files support new projections within their stored axes. They do not contain the query support TTrees. The production reducer still needs those exact rows for its complete estimators and provenance checks. A new scientific selection can require reduction from retained query files, but it does not require generation or merging.

## External data and retention

[bulk-storage.json](bulk-storage.json) identifies the custodian, access method, checksum inventories and retention rules. The original query collection contains 323 ROOT files and 66,635,305,537 ROOT bytes. The collection index binds their identities and locations. Its `EXTERNAL_ACCEPTANCE_REQUIRED` state describes that index alone; the numerical package separately retains its admission closure.

Raw, analyzed and query inputs require custodian-approved Nikhef access. GitHub downloads of merged ROOT need no Nikhef account. The small files under [tests/fixtures](../tests/fixtures) contain synthetic data and cannot replace the research sample.

Retain accepted raw and analyzed data because sparse histograms do not preserve their full information. Retain query support rows for exact reduction and diagnostics. Preserve active merged files and release assets while their result remains in use. Do not replace a published asset with different bytes under the same name. Move storage only with a new locator record and verified copies.
