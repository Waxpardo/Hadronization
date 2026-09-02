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
