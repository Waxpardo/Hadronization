# Data access and results

[Documentation index](../README.md#documentation)

The `HF_RUN3_V1` result contains 300 million successful events from 3,000 accepted sources. MONASH, JUNCTIONS and CLOSEPACKING each contribute 100 million events in ten original blocks.

## Included results

The [collaboration package](results/manifest.json) contains numerical ROOT, 69 figure PDFs, ROOT canvases, tables and exact manifests. The [numerical report](results/numerical/report.json) records 60,660 points with separate value and uncertainty statuses. The tables retain explicit missing values.

The result uses inclusive pair pT and final triggers from all origins. Its identity recipe keeps 202 signed open-heavy associates separate. The fine query retains all 219 catalog identities, including hidden-heavy states. The [all-tune companion](figures-all-tune) contains 69 PDFs with tune comparisons in the correlation pages.

The paired overview shows seven charm and eight beauty ground-state meson, Lambda and Sigma identities per trigger. Separate single-trigger figures show 28 charm and 43 beauty ground, star and prime identities. The numerical archive keeps all 202 signed open-heavy identities.

Upper baryon-to-meson activity panels use linear vertical axes. Tune-comparison panels for balancing yields and baryon-to-meson ratios use logarithmic axes. ROOT and status records retain unavailable and nonpositive ratios that the logarithmic panels cannot draw.

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

Package verification checks the renderer build identity in the figure manifest. The distributed figures record ROOT 6.30.01, GCC 14.2.0 and Ghostscript 9.54.0 on Linux. Configure the environment as described in [installation](../docs/installation.md). A different renderer identity can require fresh rendering from the same numerical ROOT.

Numerical portable verification does not require the original production filesystem. The verifier writes build files outside the result package.

```sh
mkdir -p data/work/tmp
export TMPDIR="$PWD/data/work/tmp"
PACKAGE_SHA=d5991d574285f430038c025b11681a1faa03793c46a870b376242d38918c7135
./hadronization package verify \
  --package data/results --manifest-sha256 "$PACKAGE_SHA" \
  --work-dir data/work/release-verification
```

The checked-out Git revision supplies the trusted manifest bytes. Record the checked-out commit before verification. The verifier checks every packaged file against the manifest.

To change the presentation, copy `config/plot.json` and edit its display settings. Use the example below with a new output directory. The numerical ROOT and its statistical results remain unchanged.

```sh
cp config/plot.json data/work/custom-plot.json
./hadronization plot render-cold \
  --numerics-root data/results/numerical/numerics.root \
  --expected-root-sha256 e68ef7f1e9daa6bc7a7d2072ed4e0bc0cb6b69427646bcfb32c773158ee144b9 \
  --expected-value-sha256 56309f1e787d03a6a43e6488015358fdfc747072866eeb474ddecbfce1a66bf9 \
  --plot-config data/work/custom-plot.json \
  --work-dir data/work/custom-render --output data/work/custom-figures
```

To verify an all-tune companion, use the matching numerical ROOT and the companion manifest hash. The inclusive example is:

```sh
./hadronization plot verify-render-cold \
  --numerics-root data/results/numerical/numerics.root \
  --expected-root-sha256 e68ef7f1e9daa6bc7a7d2072ed4e0bc0cb6b69427646bcfb32c773158ee144b9 \
  --expected-value-sha256 56309f1e787d03a6a43e6488015358fdfc747072866eeb474ddecbfce1a66bf9 \
  --expected-manifest-sha256 36020df53a7213d81ef26f0ad230f47bfecb404d3904ac94ce05200d12d875fe \
  --plot-config config/plot-all-tune.json \
  --work-dir data/work/all-tune-verification --output data/figures-all-tune
```

## Download merged ROOT

The [GitHub release](https://github.com/Waxpardo/Hadronization/releases/tag/hf-run3-all-origin-20261007) distributes the three completed ROOT files. The files occupy 11,024,344,504 bytes together. Each file contains five sparse families with ten original blocks. The [download manifest](merged-download.json) binds every transfer part and complete ROOT file to its size and SHA-256.

| File | Tune | Bytes |
| --- | --- | --- |
| `tune-00.root` | MONASH | 3,743,012,318 |
| `tune-01.root` | JUNCTIONS | 3,668,024,927 |
| `tune-02.root` | CLOSEPACKING | 3,613,307,259 |

Each file exceeds GitHub's release-asset limit. The downloader concatenates transfer parts to restore the original bytes. This operation does not run ROOT or repeat the scientific merge.

Allow 24 GB of free local storage for ROOT files, cached parts and temporary output. This command needs network access to GitHub. It needs neither site credentials nor ROOT.

```sh
python3 data/fetch-merged.py --output data/work/merged
python3 data/fetch-merged.py --output data/work/merged --verify-only
```

The downloader retains complete parts in `.parts` under the output directory. A restart reuses parts only after checksum verification. It refuses different existing files and symbolic output paths. A failed transfer cannot replace a completed ROOT file. Interrupted partial transfers restart from the affected part.

For parts downloaded through a browser or another transfer tool, use `--local-parts DIRECTORY`. The command checks the same hashes before restoring ROOT files. `--verify-only` reads the complete files without network access or filesystem changes.

## Explore sparse projections

The files retain activity, trigger, pair, kinematic and closure histograms. Object names include the sparse family, original block and physical component. Read the exact names from the index. The [collection index](merged/index.json) lists every object and its block. The [dictionary](merged/dictionary.json) defines signed-PDG ordinals. See the [axis reference](../docs/data-model.md#sparse-axes) before selecting bins.

With PyROOT installed, this example projects the full MONASH activity count from all ten blocks:

```sh
python3 - <<'PYCODE'
import ROOT
import json
from pathlib import Path
ROOT.gROOT.SetBatch(True)
f = ROOT.TFile.Open("data/work/merged/tune-00.root", "READ")
assert f and not f.IsZombie()
total = None
index = json.loads(Path("data/merged/index.json").read_text())
partition = next(p for p in index["partitions"] if p["tune"] == "MONASH")
for item in partition["sparse_objects"]["activity"]:
    h = f.Get(item["name"])
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

The numerical package also includes [selected-state primitives](results/numerical/family-products/paper-fine.root), [identity-mapped primitives](results/numerical/family-products/families.root) and [shared counts](results/numerical/family-products/shared.root). Their [manifest](results/numerical/family-products/manifest.json) binds the exact 202-state recipe. The merged query retains the complete 219-state catalog.

The alternative 82-to-42 family recipe remains supported for a separate reduction. It does not describe the published result.

## External data and retention

[bulk-storage.json](bulk-storage.json) identifies the custodian, access method, checksum inventories and retention rules. The original query collection contains 323 ROOT files and 69,805,257,918 ROOT bytes. The collection index binds their identities and locations. Its `EXTERNAL_ACCEPTANCE_REQUIRED` state describes that index alone; the numerical package separately retains its admission closure.

Raw, analyzed and query inputs require custodian-approved Nikhef access. GitHub downloads of merged ROOT need no Nikhef account. The small files under [tests/fixtures](../tests/fixtures) contain synthetic data and cannot replace the research sample.

Retain accepted raw and analyzed data because sparse histograms do not preserve their full information. Retain query support rows for exact reduction and diagnostics. Preserve active merged files and release assets while their result remains in use. Do not replace a published asset with different bytes under the same name. Move storage only with a new locator record and verified copies.
