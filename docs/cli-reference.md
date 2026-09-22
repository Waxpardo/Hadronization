# Command reference

[Documentation index](../README.md#documentation)

Run commands from a Git checkout. `./hadronization` dispatches to the stage parsers below. `--help` and `-h` print usage and exit without starting scientific work. Parser defaults are relative to the repository unless stated otherwise.

Options marked **required** need an explicit value. A boolean flag takes no value. Repeatable options append one value per occurrence. Lists consume one or more values. Every SHA option requires the independent expected digest of the named object.

A read-only command can still import Python modules. Python can create bytecode caches unless `PYTHONDONTWRITEBYTECODE=1`. A cache-mutating verifier preserves its scientific inputs. The [workflow](workflow.md) supplies ordered operational examples and prerequisites.

No `condor` subcommand submits to HTCondor directly. Native `condor_submit` and `condor_submit_dag` calls contact the scheduler. Generation contacts its configured scheduler only with `--submit` and a nonempty eligible plan.

## Main command

### `./hadronization doctor`

Report Git, Python and resolved runtime. This is not a complete stage check.

**Side effects:** Read-only.

No command-specific options.

Inspect its syntax before use:

```sh
./hadronization doctor --help
```

### `./hadronization generate`

Inventory by default. With --submit, default purpose becomes continuation and scheduler contact is explicit.

**Side effects:** Read-only by default.

| Option or argument | Type and default | Meaning |
| --- | --- | --- |
| `--submit` | flag, `false` | Explicit scheduler contact after nonempty plan and reservation checks. |
| `--purpose` | string, `none` | Inventory, continuation, recovery or new-campaign intent. Choices: `inventory`, `continuation`, `recovery`, `new`. |

Inspect its syntax before use:

```sh
./hadronization generate --help
```

### `./hadronization verify`

Run the development suite. Tests compile code and create temporary synthetic products.

**Side effects:** Local-mutating.

No command-specific options.

Inspect its syntax before use:

```sh
./hadronization verify --help
```

### `./hadronization clean`

List cache and compiler residue. --apply deletes the listed candidates after path checks.

**Side effects:** Read-only by default.

| Option or argument | Type and default | Meaning |
| --- | --- | --- |
| `--dry-run` | flag, `false` | List cleanup candidates without deletion. |
| `--apply` | flag, `false` | Delete reviewed cleanup candidates. |

Inspect its syntax before use:

```sh
./hadronization clean --help
```

Source: [hadronization](../hadronization).

### `./hadronization analyze plan`

Write a deterministic whole-source packing plan.

**Side effects:** Local-mutating.

| Option or argument | Type and default | Meaning |
| --- | --- | --- |
| `--campaign` | Path, `data/campaign.json` | Campaign descriptor. |
| `--manifest` | Path, `data/raw_manifest.jsonl` | Accepted raw source manifest. |
| `--attempts` | Path, `data/attempts.csv` | Attempt ledger. |
| `--raw-root` | Path, `data/raw` | Root for manifest-relative raw files. |
| `--work-root` | Path, `data/work/analyze` | Writable build and execution scratch. |
| `--output-root` | Path, `data/analyzed` | Published analyzed-file root. |
| `--plan` | Path, `data/work/analyze/plan.json` | Analysis plan file. |
| `--target-bytes` | int, **required** | Positive estimated bytes per analyzed shard. |
| `--rates` | Path, `none` | Measured packing rates JSON. |
| `--tune` | string, repeatable, `none` | Select a tune for analysis planning. |
| `--logical-id` | int, repeatable, `none` | Select a logical source ID. |
| `--source` | string, repeatable, `none` | Select a global source ID. |
| `--replace-plan` | flag, `false` | Permit replacement of the plan file only. |

Inspect its syntax before use:

```sh
./hadronization analyze plan --help
```

### `./hadronization analyze run`

Build and verify analyzed ROOT shards and receipts.

**Side effects:** Local-mutating.

| Option or argument | Type and default | Meaning |
| --- | --- | --- |
| `--plan` | Path, **required** | Analysis plan file. |
| `--raw-root` | Path, `none` | Root for manifest-relative raw files. |
| `--work-root` | Path, `none` | Writable build and execution scratch. |
| `--output-root` | Path, `none` | Published analyzed-file root. |
| `--shard` | int, repeatable, `none` | Select shard ordinal. |
| `--jobs` | int, `1` | Concurrent local analysis workers, 1–32. |
| `--resume` | flag, `true` | Verify and reuse existing complete analyzed pairs. |
| `--no-resume` | flag, absent by default | Disable the default resume mode. Refuse existing analyzed output instead of resuming. |

Inspect its syntax before use:

```sh
./hadronization analyze run --help
```

### `./hadronization analyze verify`

Verify planned or explicit ROOT/receipt pairs. May compile a verifier.

**Side effects:** Local-mutating cache.

| Option or argument | Type and default | Meaning |
| --- | --- | --- |
| `--plan` | Path, `none` | Analysis plan file. |
| `--root` | Path, `none` | ROOT input. Analysis verify also requires its receipt. |
| `--receipt` | Path, `none` | Matching analyzed JSON receipt. |
| `--raw-root` | Path, `none` | Root for manifest-relative raw files. |
| `--work-root` | Path, `none` | Writable build and execution scratch. |
| `--output-root` | Path, `none` | Published analyzed-file root. |
| `--shard` | int, repeatable, `none` | Select shard ordinal. |

Inspect its syntax before use:

```sh
./hadronization analyze verify --help
```

### `./hadronization analyze explain`

Explain a plan. Receipt inspection can compile and invoke the analyzer.

**Side effects:** Read-only or cache-mutating.

| Option or argument | Type and default | Meaning |
| --- | --- | --- |
| `--plan` | Path, `none` | Analysis plan file. |
| `--receipt` | Path, `none` | Matching analyzed JSON receipt. |
| `--shard` | int, repeatable, `none` | Select shard ordinal. |
| `--raw-root` | Path, `none` | Root for manifest-relative raw files. |
| `--work-root` | Path, `none` | Writable build and execution scratch. |

Inspect its syntax before use:

```sh
./hadronization analyze explain --help
```

Source: [pipeline/analyze/run.py](../pipeline/analyze/run.py).

### `./hadronization query prepare-pack`

Build one immutable query binary pack.

**Side effects:** Local-mutating.

| Option or argument | Type and default | Meaning |
| --- | --- | --- |
| `--output` | Path, **required** | Destination. Construction normally requires a new path. |
| `--work-root` | Path, **required** | Writable build and execution scratch. |

Inspect its syntax before use:

```sh
./hadronization query prepare-pack --help
```

### `./hadronization query census`

Scan accepted analyzed pairs and write one campaign dictionary.

**Side effects:** Local-mutating.

| Option or argument | Type and default | Meaning |
| --- | --- | --- |
| `--input` | Path, repeatable, **required** | Analyzed ROOT input. Match receipt ordering. |
| `--receipt` | Path, repeatable, **required** | Matching analyzed JSON receipt. |
| `--accepted-receipt-sha256` | string, repeatable, `none` | Independent accepted parent-receipt SHA-256. |
| `--expected-source-count` | int, **required** | Exact global source count for the census. |
| `--analysis` | Path, `config/analysis.json` | Downstream analysis JSON. |
| `--output` | Path, **required** | Destination. Construction normally requires a new path. |
| `--prepared-pack` | Path, `none` | Verified fixed query binary pack. No build fallback. |
| `--work-root` | Path, **required** | Writable build and execution scratch. |

Inspect its syntax before use:

```sh
./hadronization query census --help
```

### `./hadronization query build`

Construct and publish one verified query workspace.

**Side effects:** Local-mutating.

| Option or argument | Type and default | Meaning |
| --- | --- | --- |
| `--input` | Path, **required** | Analyzed ROOT input. Match receipt ordering. |
| `--receipt` | Path, **required** | Matching analyzed JSON receipt. |
| `--output` | Path, **required** | Destination. Construction normally requires a new path. |
| `--analysis` | Path, `config/analysis.json` | Downstream analysis JSON. |
| `--layout` | Path, `config/query.json` | Exact repository query layout. |
| `--dictionary` | Path, **required** | Campaign-wide signed-PDG dictionary. |
| `--accepted-receipt-sha256` | string, `none` | Independent accepted parent-receipt SHA-256. |
| `--prepared-pack` | Path, `none` | Verified fixed query binary pack. No build fallback. |
| `--work-root` | Path, **required** | Writable build and execution scratch. |

Inspect its syntax before use:

```sh
./hadronization query build --help
```

### `./hadronization query verify`

Verify hashes, exact files, support rows and sparse content.

**Side effects:** Local-mutating cache.

| Option or argument | Type and default | Meaning |
| --- | --- | --- |
| `--workspace` | Path, **required** | Query workspace directory. |
| `--expected-content-sha256` | string, **required** | Independent scientific-content digest for the workspace. |
| `--prepared-pack` | Path, `none` | Verified fixed query binary pack. No build fallback. |
| `--work-root` | Path, **required** | Writable build and execution scratch. |

Inspect its syntax before use:

```sh
./hadronization query verify --help
```

### `./hadronization query scan`

Scan the named archived profile after verification.

**Side effects:** Local-mutating scratch.

| Option or argument | Type and default | Meaning |
| --- | --- | --- |
| `--workspace` | Path, **required** | Query workspace directory. |
| `--expected-content-sha256` | string, **required** | Independent scientific-content digest for the workspace. |
| `--profile` | string, **required** | Named archived profile for a query scan. |
| `--prepared-pack` | Path, `none` | Verified fixed query binary pack. No build fallback. |
| `--work-root` | Path, **required** | Writable build and execution scratch. |

Inspect its syntax before use:

```sh
./hadronization query scan --help
```

Source: [pipeline/query/run.py](../pipeline/query/run.py).

### `./hadronization collection create`

Verify all workspaces and write one source-complete locator.

**Side effects:** Local-mutating.

| Option or argument | Type and default | Meaning |
| --- | --- | --- |
| `--workspace` | Path, repeatable, **required** | Query workspace directory. |
| `--expected-content-sha256` | string, repeatable, **required** | Independent scientific-content digest for the workspace. |
| `--expected-sources` | Path, **required** | Independent ordered expected-source list. |
| `--expected-sources-sha256` | string, **required** | Independent SHA-256 pin for sources. |
| `--output` | Path, **required** | Destination. Construction normally requires a new path. |
| `--work-root` | Path, **required** | Writable build and execution scratch. |
| `--test-only` | flag, `false` | Mark the collection synthetic or partial. |

Inspect its syntax before use:

```sh
./hadronization collection create --help
```

### `./hadronization collection verify`

Verify all indexed files, source membership and sparse layout.

**Side effects:** Read-only.

| Option or argument | Type and default | Meaning |
| --- | --- | --- |
| `--index` | Path, **required** | Collection index JSON. |
| `--expected-index-sha256` | string, **required** | Independent SHA-256 pin for index. |

Inspect its syntax before use:

```sh
./hadronization collection verify --help
```

### `./hadronization collection admit`

Check expected-source, site, collector and merge closure.

**Side effects:** Read-only.

| Option or argument | Type and default | Meaning |
| --- | --- | --- |
| `--index` | Path, **required** | Collection index JSON. |
| `--expected-index-sha256` | string, **required** | Independent SHA-256 pin for index. |
| `--expected-sources` | Path, **required** | Independent ordered expected-source list. |
| `--expected-sources-sha256` | string, **required** | Independent SHA-256 pin for sources. |
| `--site-work` | Path, `none` | Pinned site-bound execution manifest. |
| `--site-work-sha256` | string, `none` | Independent SHA-256 pin for site work. |
| `--collector-closure` | Path, `none` | Pinned collector closure record. |
| `--collector-closure-sha256` | string, `none` | Independent SHA-256 pin for collector closure. |
| `--merge-receipt` | Path, `none` | Physical merge lineage receipt. |
| `--merge-receipt-sha256` | string, `none` | Independent SHA-256 pin for merge receipt. |
| `--merge-verification` | Path, `none` | Exhaustive sparse comparison receipt. |
| `--merge-verification-sha256` | string, `none` | Independent SHA-256 pin for merge verification. |

Inspect its syntax before use:

```sh
./hadronization collection admit --help
```

Source: [pipeline/query/collection.py](../pipeline/query/collection.py).

### `./hadronization merge build`

Write block-resolved sparse partitions and merge receipts.

**Side effects:** Local-mutating.

| Option or argument | Type and default | Meaning |
| --- | --- | --- |
| `--index` | Path, **required** | Collection index JSON. |
| `--expected-index-sha256` | string, **required** | Independent SHA-256 pin for index. |
| `--output` | Path, **required** | Destination. Construction normally requires a new path. |

Inspect its syntax before use:

```sh
./hadronization merge build --help
```

### `./hadronization merge verify`

Compare merged contents with parents. --verification-output writes a new receipt.

**Side effects:** Read-only unless receipt requested.

| Option or argument | Type and default | Meaning |
| --- | --- | --- |
| `--index` | Path, **required** | Collection index JSON. |
| `--expected-index-sha256` | string, **required** | Independent SHA-256 pin for index. |
| `--merge-receipt` | Path, **required** | Physical merge lineage receipt. |
| `--merge-receipt-sha256` | string, **required** | Independent SHA-256 pin for merge receipt. |
| `--verification-output` | Path, `none` | New file for the merge verification receipt. |

Inspect its syntax before use:

```sh
./hadronization merge verify --help
```

Source: [pipeline/query/merge.py](../pipeline/query/merge.py).

### `./hadronization condor prepare`

Prepare an inert pinned source and scheduler bundle.

**Side effects:** Local-mutating.

| Option or argument | Type and default | Meaning |
| --- | --- | --- |
| `--acquisition` | Path, **required** | Accepted analyzed-input acquisition inventory. |
| `--expected-acquisition-sha256` | string, **required** | Independent SHA-256 pin for acquisition. |
| `--dictionary` | Path, **required** | Campaign-wide signed-PDG dictionary. |
| `--expected-dictionary-sha256` | string, **required** | Independent SHA-256 pin for dictionary. |
| `--output` | Path, **required** | Destination. Construction normally requires a new path. |

Inspect its syntax before use:

```sh
./hadronization condor prepare --help
```

### `./hadronization condor bind-site`

Check measured admission and write a new site-bound bundle.

**Side effects:** Local-mutating.

| Option or argument | Type and default | Meaning |
| --- | --- | --- |
| `--bundle` | Path, **required** | Prepared immutable bundle directory. |
| `--pack` | Path, **required** | Qualified Linux binary-pack tar. |
| `--admission` | Path, **required** | Independent measured site admission JSON. |
| `--output` | Path, **required** | Destination. Construction normally requires a new path. |
| `--expected-bundle-sha256` | string, **required** | Independent SHA-256 pin for bundle. |
| `--expected-pack-sha256` | string, **required** | Independent SHA-256 pin for pack. |
| `--expected-admission-sha256` | string, **required** | Independent SHA-256 pin for admission. |

Inspect its syntax before use:

```sh
./hadronization condor bind-site --help
```

### `./hadronization condor preflight`

Check source/runtime/storage bindings. --full-input-hash reads all ROOT bytes.

**Side effects:** Read-only inputs, local scratch.

| Option or argument | Type and default | Meaning |
| --- | --- | --- |
| `--work` | Path, **required** | Site-bound work manifest. |
| `--expected-work-sha256` | string, **required** | Independent SHA-256 pin for work. |
| `--source-tar` | Path, **required** | Frozen source archive. |
| `--pack-tar` | Path, `none` | Qualified binary-pack archive. |
| `--full-input-hash` | flag, `false` | Hash all accepted ROOT bytes during preflight. |

Inspect its syntax before use:

```sh
./hadronization condor preflight --help
```

### `./hadronization condor screen-plan`

Write a representative source plan spanning every tune/block.

**Side effects:** Local-mutating.

| Option or argument | Type and default | Meaning |
| --- | --- | --- |
| `--work` | Path, **required** | Site-bound work manifest. |
| `--expected-work-sha256` | string, **required** | Independent SHA-256 pin for work. |
| `--expected-sources` | Path, **required** | Independent ordered expected-source list. |
| `--input-root` | Path, `none` | Accepted analyzed-input directory. |

Inspect its syntax before use:

```sh
./hadronization condor screen-plan --help
```

### `./hadronization condor worker`

Run one immutable attempt using a transferred fixed binary.

**Side effects:** Local and persistent mutation.

| Option or argument | Type and default | Meaning |
| --- | --- | --- |
| `--work` | Path, **required** | Site-bound work manifest. |
| `--expected-work-sha256` | string, **required** | Independent SHA-256 pin for work. |
| `--ordinal` | int, **required** | Query shard ordinal. |
| `--attempt` | int, **required** | Unique attempt number. Query workers accept 0–2. |
| `--source-tar` | Path, **required** | Frozen source archive. |
| `--source-facts` | Path, `source-files.json` | Source-file hash inventory. |
| `--pack-tar` | Path, **required** | Qualified binary-pack archive. |

Inspect its syntax before use:

```sh
./hadronization condor worker --help
```

### `./hadronization condor collect`

Verify externally accepted attempts and publish exact closure.

**Side effects:** Persistent mutation.

| Option or argument | Type and default | Meaning |
| --- | --- | --- |
| `--work` | Path, **required** | Site-bound work manifest. |
| `--expected-work-sha256` | string, **required** | Independent SHA-256 pin for work. |
| `--expected-sources` | Path, **required** | Independent ordered expected-source list. |
| `--source-tar` | Path, **required** | Frozen source archive. |
| `--pack-tar` | Path, **required** | Qualified binary-pack archive. |
| `--pins` | Path, **required** | Externally accepted query-attempt content pins. |
| `--expected-pins-sha256` | string, **required** | Independent SHA-256 pin for pins. |

Inspect its syntax before use:

```sh
./hadronization condor collect --help
```

### `./hadronization condor collect-screen`

Publish an explicitly TEST_ONLY screened collection.

**Side effects:** Persistent mutation.

| Option or argument | Type and default | Meaning |
| --- | --- | --- |
| `--work` | Path, **required** | Site-bound work manifest. |
| `--expected-work-sha256` | string, **required** | Independent SHA-256 pin for work. |
| `--expected-sources` | Path, **required** | Independent ordered expected-source list. |
| `--source-tar` | Path, **required** | Frozen source archive. |
| `--pack-tar` | Path, **required** | Qualified binary-pack archive. |
| `--pins` | Path, **required** | Externally accepted query-attempt content pins. |
| `--expected-pins-sha256` | string, **required** | Independent SHA-256 pin for pins. |
| `--screen-plan` | Path, **required** | Pinned representative input plan. |
| `--expected-screen-plan-sha256` | string, **required** | Independent SHA-256 pin for screen plan. |

Inspect its syntax before use:

```sh
./hadronization condor collect-screen --help
```

### `./hadronization condor render-collector`

Write a separate pinned collector submit directory.

**Side effects:** Local-mutating.

| Option or argument | Type and default | Meaning |
| --- | --- | --- |
| `--bundle` | Path, **required** | Prepared immutable bundle directory. |
| `--expected-bundle-sha256` | string, **required** | Independent SHA-256 pin for bundle. |
| `--pins` | Path, **required** | Externally accepted query-attempt content pins. |
| `--expected-pins-sha256` | string, **required** | Independent SHA-256 pin for pins. |
| `--output` | Path, **required** | Destination. Construction normally requires a new path. |

Inspect its syntax before use:

```sh
./hadronization condor render-collector --help
```

### `./hadronization condor stage-dag`

Copy a sealed production DAG into fresh writable launch storage.

**Side effects:** Local-mutating.

| Option or argument | Type and default | Meaning |
| --- | --- | --- |
| `--bundle` | Path, **required** | Prepared immutable bundle directory. |
| `--expected-bundle-sha256` | string, **required** | Independent SHA-256 pin for bundle. |
| `--output` | Path, **required** | Destination. Construction normally requires a new path. |

Inspect its syntax before use:

```sh
./hadronization condor stage-dag --help
```

### `./hadronization condor stage-screen-dag`

Stage the pinned representative DAG.

**Side effects:** Local-mutating.

| Option or argument | Type and default | Meaning |
| --- | --- | --- |
| `--bundle` | Path, **required** | Prepared immutable bundle directory. |
| `--expected-bundle-sha256` | string, **required** | Independent SHA-256 pin for bundle. |
| `--screen-plan` | Path, **required** | Pinned representative input plan. |
| `--expected-screen-plan-sha256` | string, **required** | Independent SHA-256 pin for screen plan. |
| `--output` | Path, **required** | Destination. Construction normally requires a new path. |

Inspect its syntax before use:

```sh
./hadronization condor stage-screen-dag --help
```

Source: [pipeline/query/condor.py](../pipeline/query/condor.py).

### `./hadronization reduce run`

Evaluate native statistics and write typed numerical ROOT and exports.

**Side effects:** Local-mutating.

| Option or argument | Type and default | Meaning |
| --- | --- | --- |
| `--collection-index` | Path, **required** | Merged or explicitly synthetic collection locator. |
| `--collection-index-sha` | string, **required** | Independent SHA-256 pin for collection index. |
| `--expected-sources` | Path, **required** | Independent ordered expected-source list. |
| `--expected-sources-sha` | string, **required** | Independent SHA-256 pin for sources. |
| `--analysis` | Path, `config/analysis.json` | Downstream analysis JSON. |
| `--analysis-sha` | string, **required** | Independent SHA-256 pin for analysis. |
| `--request` | Path, `none` | Optional exact numerical request JSON. Requires its hash. |
| `--request-sha` | string, `none` | Independent SHA-256 pin for request. |
| `--work-root` | Path, **required** | Existing writable build and execution scratch directory. |
| `--output-dir` | Path, **required** | New numerical output directory. |
| `--site-work` | Path, `none` | Pinned site-bound execution manifest. |
| `--site-work-sha` | string, `none` | Independent SHA-256 pin for site work. |
| `--collector-closure` | Path, `none` | Pinned collector closure record. |
| `--collector-closure-sha` | string, `none` | Independent SHA-256 pin for collector closure. |
| `--merge-receipt` | Path, `none` | Physical merge lineage receipt. |
| `--merge-receipt-sha` | string, `none` | Independent SHA-256 pin for merge receipt. |
| `--merge-verification` | Path, `none` | Exhaustive sparse comparison receipt. |
| `--merge-verification-sha` | string, `none` | Independent SHA-256 pin for merge verification. |
| `--tunes` | string list, `none` | Requested tune list. Must match full domain for research results. |
| `--profile-id` | string, `inclusive` | Requested profile ID. |
| `--activity-id` | string, `none` | Requested charged-light activity ID. |
| `--reference-tune` | string, `MONASH` | Reference for tune ratios. |
| `--charm-trigger` | int, `421` | Charm-meson PDG, 421 or 411. Choices: `421`, `411`. |
| `--representative` | flag, `false` | Restrict a synthetic request. Refused for full research results. |

Inspect its syntax before use:

```sh
./hadronization reduce run --help
```

### `./hadronization reduce verify`

Check numerical ROOT and report, or a portable numerical package.

**Side effects:** Read-only.

| Option or argument | Type and default | Meaning |
| --- | --- | --- |
| `--mode` | string, `producer` | Producer checks execution. Portable checks self-contained results. Choices: `producer`, `portable`. |
| `--root` | Path, `none` | Numerical ROOT input. Producer mode also requires its report and report hash. |
| `--report` | Path, `none` | Numerical report JSON. |
| `--report-sha` | string, `none` | Independent SHA-256 pin for report. |
| `--package-dir` | Path, `none` | Numerical portable package directory. |
| `--package-manifest-sha` | string, `none` | Independent SHA-256 pin for package manifest. |

Inspect its syntax before use:

```sh
./hadronization reduce verify --help
```

### `./hadronization reduce explain`

Perform the same verification and report resolved provenance.

**Side effects:** Read-only.

| Option or argument | Type and default | Meaning |
| --- | --- | --- |
| `--mode` | string, `producer` | Producer checks execution. Portable checks self-contained results. Choices: `producer`, `portable`. |
| `--root` | Path, `none` | Numerical ROOT input. Producer mode also requires its report and report hash. |
| `--report` | Path, `none` | Numerical report JSON. |
| `--report-sha` | string, `none` | Independent SHA-256 pin for report. |
| `--package-dir` | Path, `none` | Numerical portable package directory. |
| `--package-manifest-sha` | string, `none` | Independent SHA-256 pin for package manifest. |

Inspect its syntax before use:

```sh
./hadronization reduce explain --help
```

Source: [pipeline/reduce/public_v4.py](../pipeline/reduce/public_v4.py).

### `./hadronization plot render-cold`

Render verified numerical ROOT and publish figures.

**Side effects:** Local-mutating.

| Option or argument | Type and default | Meaning |
| --- | --- | --- |
| `--numerics-root` | Path, **required** | Self-contained numerical ROOT input. |
| `--expected-root-sha256` | string, **required** | Independent physical numerical-ROOT SHA-256. |
| `--expected-value-sha256` | string, **required** | Independent decoded numerical-value digest. |
| `--expected-manifest-sha256` | string, `none` | Optional independent figure-manifest SHA-256. |
| `--plot-config` | Path, `config/plot.json` | Exact presentation JSON used by the renderer. |
| `--work-dir` | Path, **required** | Writable archive or renderer scratch. |
| `--output` | Path, **required** | Destination. Construction normally requires a new path. |

Inspect its syntax before use:

```sh
./hadronization plot render-cold --help
```

### `./hadronization plot verify-render-cold`

Reopen every canvas and write verifier attestation in scratch.

**Side effects:** Local-mutating cache.

| Option or argument | Type and default | Meaning |
| --- | --- | --- |
| `--numerics-root` | Path, **required** | Self-contained numerical ROOT input. |
| `--expected-root-sha256` | string, **required** | Independent physical numerical-ROOT SHA-256. |
| `--expected-value-sha256` | string, **required** | Independent decoded numerical-value digest. |
| `--expected-manifest-sha256` | string, `none` | Optional independent figure-manifest SHA-256. |
| `--plot-config` | Path, `config/plot.json` | Exact presentation JSON used by the renderer. |
| `--work-dir` | Path, **required** | Writable archive or renderer scratch. |
| `--output` | Path, **required** | Destination. Construction normally requires a new path. |

Inspect its syntax before use:

```sh
./hadronization plot verify-render-cold --help
```

### `./hadronization plot verify-review-packet`

Check synthetic figure display coverage. This does not qualify research data.

**Side effects:** Local-mutating cache.

| Option or argument | Type and default | Meaning |
| --- | --- | --- |
| `--numerics-root` | Path, **required** | Self-contained numerical ROOT input. |
| `--expected-root-sha256` | string, **required** | Independent physical numerical-ROOT SHA-256. |
| `--expected-value-sha256` | string, **required** | Independent decoded numerical-value digest. |
| `--expected-manifest-sha256` | string, `none` | Optional independent figure-manifest SHA-256. |
| `--plot-config` | Path, `config/plot.json` | Exact presentation JSON used by the renderer. |
| `--work-dir` | Path, **required** | Writable archive or renderer scratch. |
| `--output` | Path, **required** | Destination. Construction normally requires a new path. |

Inspect its syntax before use:

```sh
./hadronization plot verify-review-packet --help
```

Source: [pipeline/plot/run.py](../pipeline/plot/run.py).

### `./hadronization package build`

Copy exact numerical and figure files into a new package.

**Side effects:** Local-mutating.

| Option or argument | Type and default | Meaning |
| --- | --- | --- |
| `--numerical` | Path, **required** | Numerical package directory. |
| `--numerical-manifest-sha256` | string, **required** | Independent SHA-256 pin for numerical manifest. |
| `--figures` | Path, **required** | Figure directory. |
| `--figure-manifest-sha256` | string, **required** | Independent SHA-256 pin for figure manifest. |
| `--plot-config` | Path, `none` | Exact presentation JSON used by the renderer. |
| `--output` | Path, **required** | Destination. Construction normally requires a new path. |

Inspect its syntax before use:

```sh
./hadronization package build --help
```

### `./hadronization package verify`

Check exact package files and invoke numerical and canvas verifiers.

**Side effects:** Local-mutating cache.

| Option or argument | Type and default | Meaning |
| --- | --- | --- |
| `--package` | Path, **required** | Final collaboration package directory. |
| `--manifest-sha256` | string, **required** | Independent SHA-256 pin for manifest. |
| `--work-dir` | Path, **required** | Writable archive or renderer scratch. |

Inspect its syntax before use:

```sh
./hadronization package verify --help
```

Source: [pipeline/release.py](../pipeline/release.py).

### `python3 pipeline/generate/runtime.py`

Resolve dependencies. shell prints exports, json prints a record and check reports status.

**Side effects:** Read-only.

| Option or argument | Type and default | Meaning |
| --- | --- | --- |
| `command` | string, **required** | Select one of the listed operations. Choices: `shell`, `json`, `check`. |
| `--require-root` | flag, `false` | Fail if ROOT is unavailable. |
| `--require-pythia` | flag, `false` | Fail if PYTHIA is unavailable. |

Inspect its syntax before use:

```sh
python3 pipeline/generate/runtime.py --help
```

Source: [pipeline/generate/runtime.py](../pipeline/generate/runtime.py).

### `python3 pipeline/generate/submit.py plan`

Plan generation. --output writes JSON. --build builds. --submit reserves and submits.

**Side effects:** Read-only by default.

| Option or argument | Type and default | Meaning |
| --- | --- | --- |
| `--purpose` | string, `inventory` | Inventory, continuation, recovery or new-campaign intent. Choices: `inventory`, `continuation`, `recovery`, `new`. |
| `--output` | Path, `none` | Destination. Construction normally requires a new path. |
| `--submit` | flag, `false` | Explicit scheduler contact after nonempty plan and reservation checks. |
| `--build` | flag, `false` | Build executables for a nonempty generation plan. |
| `--producer` | Path, `none` | Producer executable override. |
| `--validator` | Path, `none` | Raw validator executable override. |
| `--raw-root` | Path, `none` | Root for manifest-relative raw files. |
| `--work-root` | Path, `none` | Writable build and execution scratch. |
| `--raw-manifest` | Path, `none` | Raw accepted manifest override. |
| `--attempts` | Path, `none` | Attempt ledger. |
| `--verify-accepted-sha256` | flag, `false` | Hash accepted raw files instead of observing size alone. |

Inspect its syntax before use:

```sh
python3 pipeline/generate/submit.py plan --help
```

### `python3 pipeline/generate/submit.py build`

Compile requested producer or validator binaries.

**Side effects:** Local-mutating.

| Option or argument | Type and default | Meaning |
| --- | --- | --- |
| `--component` | string, `all` | Choose validator, producer or both. Choices: `validator`, `producer`, `all`. |
| `--producer` | Path, `none` | Producer executable override. |
| `--validator` | Path, `none` | Raw validator executable override. |

Inspect its syntax before use:

```sh
python3 pipeline/generate/submit.py build --help
```

### `python3 pipeline/generate/submit.py worker`

Execute a reserved generation attempt and publish validated raw output.

**Side effects:** Local and persistent mutation.

| Option or argument | Type and default | Meaning |
| --- | --- | --- |
| `--tune` | string, **required** | Select a tune for analysis planning. |
| `--logical-id` | int, **required** | Select a logical source ID. |
| `--attempt` | int, **required** | Unique attempt number. Query workers accept 0–2. |
| `--seed` | int, **required** | Deterministic attempt seed. |
| `--card-sha256` | string, **required** | Independent SHA-256 pin for card. |
| `--effective-card-sha256` | string, **required** | Independent SHA-256 pin for effective card. |
| `--producer-sha256` | string, **required** | Independent SHA-256 pin for producer. |
| `--validator-sha256` | string, **required** | Independent SHA-256 pin for validator. |
| `--repository-commit` | string, **required** | Expected committed generator source. |
| `--raw-root` | string, **required** | Root for manifest-relative raw files. |
| `--work-root` | string, **required** | Writable build and execution scratch. |
| `--producer-path` | string, **required** | Worker producer executable. |
| `--validator-path` | string, **required** | Worker validator executable. |

Inspect its syntax before use:

```sh
python3 pipeline/generate/submit.py worker --help
```

### `python3 pipeline/generate/submit.py record-outcome`

Record a held or failed preworker attempt outcome.

**Side effects:** Persistent mutation.

| Option or argument | Type and default | Meaning |
| --- | --- | --- |
| `--tune` | string, **required** | Select a tune for analysis planning. |
| `--logical-id` | int, **required** | Select a logical source ID. |
| `--attempt` | int, **required** | Unique attempt number. Query workers accept 0–2. |
| `--state` | string, **required** | Record a held or failed preworker outcome. Choices: `held`, `failed`. |
| `--reason` | string, **required** | Required outcome explanation. |
| `--work-root` | Path, `none` | Writable build and execution scratch. |

Inspect its syntax before use:

```sh
python3 pipeline/generate/submit.py record-outcome --help
```

Source: [pipeline/generate/submit.py](../pipeline/generate/submit.py).

### `python3 pipeline/generate/study_contract.py`

check compares generated header bytes. generate writes the selected header output.

**Side effects:** Read-only check or source mutation.

| Option or argument | Type and default | Meaning |
| --- | --- | --- |
| `command` | string, **required** | Select one of the listed operations. Choices: `generate`, `check`. |
| `--output` | Path, `pipeline/generate/study_contract.hpp` | Destination. Construction normally requires a new path. |

Inspect its syntax before use:

```sh
python3 pipeline/generate/study_contract.py --help
```

Source: [pipeline/generate/study_contract.py](../pipeline/generate/study_contract.py).

### `python3 pipeline/query/site_probe.py`

Measure the execute-node environment and bulk/control no-replace publication. Requires allocated endpoints.

**Side effects:** Persistent probe writes.

| Option or argument | Type and default | Meaning |
| --- | --- | --- |
| `--input-root` | Path, **required** | Accepted analyzed-input directory. |
| `--input-sha256` | string, **required** | Independent SHA-256 pin for input. |
| `--bulk-root` | Path, **required** | Allocated persistent bulk endpoint. |
| `--control-root` | Path, **required** | Separate protected control endpoint. |
| `--root-config` | string, **required** | ROOT configuration executable. |
| `--cxx` | string, **required** | Compiler executable. |
| `--pythia-config` | string, **required** | PYTHIA configuration executable. |
| `--cvmfs-path` | Path, **required** | Required CVMFS location. |
| `--site-conf` | Path, **required** | Site file used for the probe. |
| `--expected-almalinux-version` | string, **required** | Exact expected OS minor version. |
| `--expected-image-path` | Path, **required** | Exact execute-node image path. |

Inspect its syntax before use:

```sh
python3 pipeline/query/site_probe.py --help
```

Source: [pipeline/query/site_probe.py](../pipeline/query/site_probe.py).

## Option coupling and return codes

- `analyze verify` accepts a plan or an explicit ROOT/receipt pair. A lone receipt is not a complete shard.

- `query census` and `collection create` require equal-length ordered input and hash lists.

- Collection admission requires path/hash pairs together. A merged collection requires its merge receipt.

- Full reduction requires site-work and collector closure. An optional explicit request requires `--request-sha`.

- `reduce verify` and `reduce explain` accept either ROOT/report/report-hash inputs or package-directory/package-manifest-hash inputs.

- Figure verification uses the same numerical hashes and presentation configuration as rendering.

- Package construction must receive the exact configuration used for its figure directory.

Successful commands return zero. Argument-parser errors normally return 2. Scientific and file-contract failures normally return 2 outside the Condor boundary. Query transient operating-system failures can return 75. Condor uses 42 for deterministic failure and 75 for classified transient failure.

Compiled C++ executables are implementation interfaces invoked by these Python commands. They do not share an argparse help interface. Their usage and transport formats reside in their source files. Run the public stage commands to preserve provenance and path checks.
