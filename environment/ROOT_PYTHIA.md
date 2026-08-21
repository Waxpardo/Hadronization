# ROOT and PYTHIA runtime

This project distinguishes the scientific runtime pin from a portable build
promise. The pin is precise; a complete portable environment is not supplied.

## Pinned scientific runtime

| component | required identity | enforcement |
|---|---|---|
| PYTHIA | 8.317, unmodified official source tarball | Source digest and prefix in `config/dependencies.conf`; exact version checked on the recorded CVMFS path. |
| ROOT | 6.30.01, recorded ALICE package build | Exact version checked by the environment verdict. |
| C++ | C++20 producer build | `tools/build_producer.sh` and the Makefile. |
| Python | Python 3 | Source-contract, registry, extraction, and audit tools. |
| Batch/storage | HTCondor plus external campaign storage | Needed only for full campaign generation and reduction. |

The official PYTHIA source SHA-256 is
`1ae551d14dac495ddfe6b344792035ebe410fe6c6004d44a335e0ece0e745adf`.
The dependency file records the complete package paths used by the pinned
cluster environment.

## Configure a machine

From a case-sensitive checkout root:

```sh
make setup
```

Edit the untracked `config/dependencies.local.conf`; do not place a personal or
cluster path in tracked defaults. Then run:

```sh
source ./setupEnv.sh
make doctor
make build
make check
```

`make doctor` reports availability and returns success. Build and check targets
remain authoritative for refusal behavior.

## Off-pin source-contract work

On a host without the recorded ALICE CVMFS stack, this declaration permits
source-contract work only:

```sh
HF_ALLOW_UNPINNED_ENV=1 make check
```

It does not certify that work performed under the escape hatch used PYTHIA
8.317, external input identity, campaign production, or publication figures.
Without the escape hatch, the environment verdict checks both non-CVMFS ROOT
and PYTHIA versions exactly. The repository still provides no portable, tested
PYTHIA build recipe or container. That gap is a release/reproduction boundary.

## External inputs

Full reproduction requires the selected raw manifest, 3,000 raw files, reduced
pair products, central and ten-block merged products, historical seed ledger,
and authorized dataset selector. No machine-specific default supplies them.
See `docs/DATA_AVAILABILITY.md` for the Git/external boundary.
