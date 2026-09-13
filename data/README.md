# Data plane

The data plane has four objects:

1. `campaign.json` owns campaign-wide identities, seed/block rules, runtime
   facts, accepted-source provenance, and current-definition bindings.
2. `raw_manifest.jsonl` lists the 3,000 accepted raw files in tune/logical-job
   order. Each `raw_storage_key` is portable and relative to `data/raw/`.
3. `attempts.csv` records every accepted or discarded submitted attempt and
   its deterministic seed.
4. `raw/` holds large untracked ROOT objects addressed by those portable keys.

`work/` is ignored transient scratch and durable attempt-evidence space. The
public cleanup command only removes old scratch for attempts explicitly marked
accepted; it never traverses `raw/` or removes reservation/outcome evidence.
Neither `raw/` nor `work/` is created by repository verification.

The accepted analyzed ROOT and receipts are a separate externally pinned input
plane. The query work manifest records every expected path, SHA-256 and byte
size and is hashed before a worker opens an analyzed ROOT. The original query
shards contain both sparse families and exact support; they remain retrievable
after the one-partition-per-tune physical merge. A collector closure pins the
original sharded index and independent accepted-attempt custody. The merge
receipt pins the transformed index/ROOT without rewriting that closure. The
large analyzed, query, merged and execution planes stay outside ordinary Git.
Each retained object needs an immutable locator, custodian, SHA/size,
dependencies and explicit retention period. Local TEST_ONLY fixtures have no
production acceptance authority.
