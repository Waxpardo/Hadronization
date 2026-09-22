# Synthetic ROOT query fixture

These three query workspaces contain 30 synthetic successful events per tune, or 90 events in total. Each tune has one source in each of ten original blocks. Each workspace contains five sparse families and twelve exact support trees.

Shard-local source IDs 0–9 recur in every workspace. Embedded analyzed receipts map them to global source IDs 0–29. `expected-sources.json` defines the complete synthetic domain.

The fixtures exercise collection membership, physical merging and identity checks. Their analysis contract is version 2.1.0. They do not satisfy the current numerical reducer's version 2.2.0 input contract. They are not research data.

Use `tests/fixtures/nonzero_chain_v22/build.py` to construct a current synthetic chain. The [reproducibility guide](../../../docs/reproducibility.md#synthetic-example) gives its prerequisites and commands.
