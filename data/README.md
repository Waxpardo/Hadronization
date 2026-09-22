# Data access and inventory

[Documentation index](../README.md#documentation)

This directory contains metadata for the `HF_RUN3_V1` campaign. It does not contain the external research ROOT files or a download client.

| File | Contents |
| --- | --- |
| [campaign.json](campaign.json) | Collision setup, tune order, source factorization, seed and block rules, provenance hashes |
| [raw_manifest.jsonl](raw_manifest.jsonl) | One canonical JSON record for each accepted raw source |
| [attempts.csv](attempts.csv) | Attempt identities, outcomes and evidence classifications |

The manifest lists 3,000 accepted files containing 300 million successful events. It records 284,750,292,184 raw ROOT bytes. Each tune contributes 100 million successful events. These figures describe the inventory, not a fresh measurement of external storage.

The attempt ledger contains 3,127 attempts, including 127 discarded attempts. It does not supply event-trial counts for every attempt. The numerical accounting export preserves that missing state.

## Obtain external inputs

Obtain the raw files and independent checksum records from their data custodian. The repository supplies no public bulk-data locator or access credential. Preserve each manifest-relative file key under the selected raw root.

An analyzed-input route instead requires ROOT shards and matching PASS receipts. It also requires a separately trusted inventory that binds every receipt and ROOT SHA-256, byte count and source identity. The prepared cluster route expects exactly 323 analyzed pairs and 158,720,142,481 ROOT bytes. Its [workflow](../docs/workflow.md#cluster-query-construction) describes the additional admission records.

A query collection requires the original query workspaces, collection index, expected-source list and independent hashes. A merged collection additionally requires its sparse partitions and merge receipts. Keep original query shards because reduction reads their exact support rows.

## Storage policy

Bulk raw, analyzed and query ROOT stay outside ordinary Git. Keep build caches, logs, attempt directories and credentials outside tracked files. The ignore rules do not replace a storage or retention agreement.

The small ROOT files under [tests/fixtures](../tests/fixtures) contain synthetic data. They cannot substitute for the research sample. See [data structures and retention](../docs/data-model.md).
