# Reproduction and verification

[Documentation index](../README.md#documentation)

## Preserve identities

Record the source commit and tree before execution:

```sh
git rev-parse HEAD HEAD^{tree}
git status --short
```

Keep the campaign, configuration and external input hashes with the run. A file's SHA-256 identifies bytes. A scientific-content digest identifies normalized scientific content. An execution receipt identifies the program and environment. These identities are not interchangeable.

Supply expected hashes from a separate reviewed record. A new hash beside a changed output only identifies its current bytes. It does not restore lost authority.

This Python command computes a file hash without loading the complete file into memory:

```sh
python3 - "$INPUT_FILE" <<'PYCODE'
import hashlib
import sys
from pathlib import Path
h = hashlib.sha256()
with Path(sys.argv[1]).open('rb') as stream:
    for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b''):
        h.update(chunk)
print(h.hexdigest())
PYCODE
```

Set `INPUT_FILE` to a regular file first. Compare the result with the independent expected digest.

## Fresh execution

Use a clean Git checkout with the documented runtime. Set a fresh scratch root and workspace-backed `TMPDIR`. Run `doctor`, the required runtime checks and `study_contract.py check`. Run `./hadronization verify` and inspect skipped cases.

Follow the [workflow](workflow.md) with external inputs from their checksum-bound inventory. Keep original source blocks unchanged. Do not equate new query shards with independent statistical blocks.

For full reduction, preserve accepted site-work and collector-closure records. A collection index alone cannot establish full production closure. A synthetic or partial result must retain its qualification in reports and figures.

A source-only download can support inspection. It cannot supply Git provenance or bulk data. The [merged-data downloader](../data/fetch-merged.py) retrieves the completed sparse ROOT files. It does not download raw, analyzed or query support rows.

## Synthetic example

This example needs ROOT, PyROOT, a C++17 compiler and Git history. It creates synthetic raw inputs and runs analysis, query construction and physical merging. It does not generate a research sample with PYTHIA.

`NONZERO_CHAIN_BASE` must be an absolute new directory. Its parent must already exist and have no symlink components. Do not select a directory containing other data.

```sh
mkdir -p data/work/tmp
export TMPDIR="$PWD/data/work/tmp"
export NONZERO_CHAIN_BASE="$PWD/data/work/nonzero-example"
python3 tests/fixtures/nonzero_chain_v22/build.py
export NONZERO_CHAIN_REPORT="$NONZERO_CHAIN_BASE/oracle.json"
python3 tests/fixtures/nonzero_chain_v22/oracle.py
```

The builder creates three tune domains with ten original blocks. `NONZERO_CHAIN_SOURCES_PER_BLOCK` accepts 1 or 2 and defaults to 1. The standalone oracle reads the declared block-object inventory. It independently sums the complete sparse domain and Sumw2, then compares them with the source-query domain.

The resulting collection has `TEST_ONLY` state. Its `merged/index.json` and `expected-sources.json` can exercise `reduce run` without production site records. Supply independently recorded hashes for these files and `config/analysis.json`. Do not use `--representative` to claim complete figure coverage.

The prebuilt [query fixture](../tests/fixtures/query_multitune/TEST_ONLY.md) exercises collection and merge contracts. Its version differs from the current numerical input model. Use the builder above for the current model.

## Verification boundaries

| Command | What it checks | What it does not establish |
| --- | --- | --- |
| `analyze verify` | Shard contract, receipts, rows and provenance bindings | Availability of every unselected source |
| `query verify` | Exact workspace, hashes, support rows and sparse reconstruction | Independent custody of a caller-supplied content pin |
| `collection verify` | Member files, dictionaries, axes and source closure | Full site admission without its separate records |
| `merge verify` | Complete sparse cell domain, contents, Sumw2 and parent lineage | Permission to delete original support rows |
| `collection admit` | Independent expected-source and execution closure | A new campaign from incomplete data |
| `reduce verify --mode producer` | Numerical data plus source and external execution bindings | Future availability of external storage |
| `reduce verify --mode portable` | Self-contained numerical content and exact exports | External execution inputs |
| `plot verify-render-cold` | Reopened canvas semantics, file hashes and source/runtime bindings | Human readability or scientific model adequacy |
| `package verify` | Exact package files, numerical verification and canvas verification | External execution revalidation |

## Copy outputs

Copy the final collaboration package as one directory, including its manifest and selected plot configuration. Preserve the package-manifest SHA-256 separately. Run `package verify` at the destination with the matching source and a fresh verifier scratch directory.

The numerical package uses relative file locators for its required contents. External execution locators remain recorded but are not opened in portable mode. The final package verifier still checks renderer source hashes and build identity. “Portable” therefore does not mean independent of ROOT, compiler or repository source.

For bulk collection relocation, preserve all file bytes. Update only physical locators in a new collection index and record its new hash. Its scientific identity can remain unchanged. Re-run collection verification and obtain the required independent acceptance records for the new locations.

## Retention and Git

Keep bulk raw, analyzed and query ROOT outside ordinary Git. Keep all files required by active collection indexes. Merged sparse ROOT cannot replace query support rows or full analyzed ancestry.

Keep the source commit, configuration, numerical ROOT, exports, canvases, PDFs and compact manifests with a research result. Keep credentials, build packs, scratch, controller state and logs outside tracked collaboration products. See the [retention table](data-model.md#lifetimes-and-retention).

The cleanup command removes reproducible local residue. It does not determine the retention needs of scientific information. Review `clean --dry-run` before any `clean --apply` operation.
