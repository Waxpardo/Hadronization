# Canonical campaign data contract

`campaign.json`, `raw_manifest.jsonl`, and `attempts.csv` are the portable,
tracked HF_RUN3_V1 campaign record. Paths in the manifest are storage keys
relative to `data/raw/`; they are not checkout-local source paths.

`data/raw/` and `data/work/` are intentionally absent and ignored. DATA-1 will
provision those physical work planes on Nikhef. No placeholder file belongs in
either scientific-data directory.
