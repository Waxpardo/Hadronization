# Data availability

**Release state: PUBLIC-BLOCKED.** This statement describes what is present in
this source checkout. It does not promise access to external campaign storage.

## Committed compact evidence

Git contains the analysis and plotting source, scientific configurations,
compact extraction anchors, machine-readable result tables, selected
validation records, digests, and source-contract tests. Those files support
the committed-evidence recipes in `README.md` and `docs/REPRODUCIBILITY.md`.

The committed evidence can reproduce selected species-decomposition tables,
the multiplicity boundaries, stored systematics reports, and source-contract
verdicts. It cannot recreate the publication dataset or an accepted scientific
figure set. The figure-acceptance manifest currently accepts none of P1--P8.

## External merged and reduced products

The selected reduction outputs, central merged products, ten disjoint block
merges, and most ROOT-rendered candidates are external to Git. Dataset selector
key `HF_RUN3_V1` names the authorized campaign, but the selected files are not
included and have no public retrieval route in this repository.

Exact publication reruns require these products for extraction,
central-to-block closure, and plotting. A future archive must bind
their file list and digests to the selector and figure-acceptance records.

Signed dataset selectors and historical plotting configurations retain exact
external locator strings. Fixtures and immutable run or result records do the
same when a locator identifies the input consumed by a recorded run. Those
strings are provenance, not portable defaults, credentials, or a discovery
service. Live tools and setup instructions require explicit local roots and
contain no personal storage default.

## External raw campaign data

For each of MONASH, JUNCTIONS, and CLOSEPACKING, the campaign record reports
1,000 files by 100,000 events. The three bundles total 3,000 raw files and 300
million generated events. It reports approximately 270 GB of raw data. The raw files, their
sealed manifest, and the historical burned-seed ledger remain external.

The attempt-level and partial-job evidence needed to test the generator-hang
selection bias is also external. The retained record reports 0 discarded
attempts in 1,000 for MONASH, 63 in 1,063 for JUNCTIONS, and 64 in 1,064 for
CLOSEPACKING, with the hang in `JunctionSplitting`. Git does not contain the
evidence needed to test whether completion is conditionally independent of
multiplicity, signed species, topology, or balancing observables.

Git alone cannot recount or rehash that union, repeat reduction and merging,
or audit historical seed reuse. The repository names no public archive, DOI,
preservation service, or recovery authority.

## What Git alone can and cannot reproduce

| From Git alone | Status |
|---|---|
| Inspect scientific definitions and complete-tune configurations | Supported |
| Run the source-contract suite | Supported on a compatible Python host |
| Rebuild selected compact-evidence tables and reports | Supported |
| Verify tracked artifact digests | Supported |
| Recreate the raw campaign | Not supported |
| Establish event-content independence of generator completion | Not supported; attempt/partial evidence and a preregistered bias study are absent |
| Recreate selected central and ten-block merges | Not supported |
| Rerun exact publication plotting | Not supported |
| Reproduce accepted P1--P8 figure bytes | Not supported; no role is accepted |

Public access, long-term preservation, and archive identity are release
blockers. `environment/ROOT_PYTHIA.md` records the runtime boundary.
