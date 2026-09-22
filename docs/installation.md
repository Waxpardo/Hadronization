# Installation

[Documentation index](../README.md#documentation)

## Runtime contract

| Component | Requirement and consumer |
| --- | --- |
| Git | Required for repository identity, build provenance and source-based tests. Use a clone with commit history. |
| Python | Version 3.9 or later according to `doctor`. Python entry points use the standard library and PyROOT. |
| C++ compiler | C++17 support. Scientific builds use optimization, strict warnings and disabled floating-point contraction. |
| ROOT | Required for analysis, query, merge, numerical archives and rendering. Provide `root-config` and matching PyROOT. |
| PYTHIA | Version 8.317 for generation. Provide headers, library, XML data and `pythia8-config`. |
| Bash or zsh | Required to source `setup.sh`. |
| HTCondor | Required only for scheduler execution. Preparation alone does not submit jobs. |
| TeX | Optional for compiled tables. Exports use `booktabs`, `longtable`, `pdflscape` and `siunitx`. |

The prepared cluster route checks ROOT 6.30.01, GCC 14.2.0, PYTHIA 8.317, x86_64 and AlmaLinux 9.6. Its image and CVMFS paths reside in [condor.py](../pipeline/query/condor.py) and the generated bundle. A different operating-system minor version fails its execute-node probe.

Local code has Darwin and Linux publication paths. This does not establish support for every ROOT, compiler or filesystem version. The site resolver checks an exact ROOT version only when `ROOT_VERSION` is set. Always run the commands below on the intended machine.

ROOT and PyROOT must belong to the same installation. A working `root-config` does not prove that Python can import ROOT. The generator additionally checks PYTHIA headers, library, XML data and configuration flags.

## Configure one machine

From the repository root, copy the site template:

```sh
cp config/site.example.conf config/site.conf
```

Edit `config/site.conf` before sourcing it. Replace the example paths with installed software and allocated storage. This file uses `KEY=VALUE` records, not shell syntax. The parser removes optional outer quotes and refuses duplicate keys. The [site table](configuration.md#site-settings) describes each supported key.

For dependencies already on `PATH`, the site file is optional. `setup.sh` resolves software and exports environment variables. It does not install dependencies.

```sh
source ./setup.sh
python3 pipeline/generate/runtime.py json
./hadronization doctor
```

Run the stage-specific environment checks:

```sh
python3 pipeline/generate/runtime.py check --require-root
python3 -c 'import ROOT; print(ROOT.gROOT.GetVersion())'
```

Before generation, require PYTHIA as well:

```sh
python3 pipeline/generate/runtime.py check --require-root --require-pythia
```

A version, library, header or XML mismatch stops resolution. Correct the installation or site configuration before building. Do not substitute unverified binaries in an existing prepared build pack.

## Scratch and outputs

Use real, writable directories without symlink components. Keep raw input, build scratch and published output roots disjoint. Analysis publication requires compatible filesystem placement for its hard-link operation. Query publication checks its own path and filesystem constraints.

Set `TMPDIR` to allocated disk space before running tests or reductions. Avoid a small system temporary volume for ROOT construction. This example creates local scratch under an ignored directory:

```sh
mkdir -p data/work/tmp
export TMPDIR="$PWD/data/work/tmp"
```

A published output destination must be new. Most stages refuse an existing output destination, even when its contents look reusable. The reducer scratch directory must already exist. Analysis has a separate verified resume mode. See [restart rules](workflow.md#restart-and-failure-rules).

## First verification

These commands need no external research data or scheduler:

```sh
python3 pipeline/generate/study_contract.py check
./hadronization generate --purpose inventory
./hadronization verify
```

`verify` runs Python unittest discovery under `tests/`. Tests compile C++ and create temporary synthetic ROOT products when their dependencies exist. Some tests skip without ROOT, PYTHIA, Linux facilities or separately configured fixture collections. Read skipped cases and the final exit status. A successful reduced environment run does not certify an unavailable production runtime.

The [file reference](file-reference.md#tests) identifies the test modules. The [reproducibility guide](reproducibility.md) describes a fresh-cache check and a small synthetic chain.
