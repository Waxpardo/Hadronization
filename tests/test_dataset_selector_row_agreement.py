#!/usr/bin/env python3
"""Per-campaign selector files must not drift from the combined one.

`config/dataset_selector.json` carries every dataset row; each
`config/dataset_selector_<campaign>.json` carries one of them again, verbatim,
so a target can be pointed at a single dataset with DATASET_SELECTOR. The row is
therefore stored TWICE, and nothing until now compared the copies.

That is the shape the multiplicity-boundary artifact warns about in its own
text -- "two definitions drift, and the axis is the thing every per-multiplicity
number is conditioned on". Here the stakes are the same in kind: a dataset row
records publication eligibility and the authorization behind it, and a promotion
applied to one file and not the other would leave two different answers to "is
this dataset publishable", selected by which file a runner happened to be given.

The 2026-08-17 seal touched both files. This test is what keeps the next one
from touching only one.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMBINED = ROOT / "config" / "dataset_selector.json"


def per_campaign_selectors() -> list[Path]:
    return sorted(p for p in (ROOT / "config").glob("dataset_selector_*.json"))


def test_every_per_campaign_row_matches_the_combined_one() -> None:
    combined = json.loads(COMBINED.read_text())["datasets"]
    checked = 0
    for path in per_campaign_selectors():
        rows = json.loads(path.read_text())["datasets"]
        for name, row in rows.items():
            assert name in combined, \
                f"{path.name} defines dataset {name!r} absent from the combined file"
            assert row == combined[name], (
                f"{path.name} row {name!r} has drifted from "
                f"{COMBINED.name}; a promotion was applied to one file only"
            )
            checked += 1
    assert checked, "no per-campaign selector rows were found to compare"


def test_active_dataset_of_each_file_is_one_it_defines() -> None:
    for path in [COMBINED, *per_campaign_selectors()]:
        doc = json.loads(path.read_text())
        active = doc["active_dataset"]
        if active is None:
            # A declared null is the refusal contract, not a dangling pointer:
            # the resolver raises and lists its keys rather than picking one.
            # Only the combined file may do this -- a per-campaign file carries
            # one row, so naming the file already names the dataset.
            assert path == COMBINED, \
                f"{path.name} declares no active_dataset; only the combined file may"
            continue
        assert active in doc["datasets"], \
            f"{path.name} points active_dataset at {active!r}, which it does not define"


def test_publication_eligible_rows_carry_a_real_authorization() -> None:
    """Eligibility without a resolvable, hash-matching authorization is a claim.

    The selector validator stopped enforcing these fields -- they were moved to
    the gate layer -- so nothing else checks that the cited document exists or
    that its recorded digest still describes it. An authorization that has been
    edited since it was cited is worse than none: it reads as reviewed.
    """
    for path in [COMBINED, *per_campaign_selectors()]:
        for name, row in json.loads(path.read_text())["datasets"].items():
            if not row.get("publication_eligible"):
                continue
            cited = row.get("publication_authorization")
            digest = row.get("publication_authorization_sha256")
            assert cited, f"{name} is publication_eligible with no authorization"
            assert isinstance(digest, str) and len(digest) == 64, \
                f"{name} authorization sha256 is not a sha256"
            document = ROOT / cited
            assert document.is_file(), \
                f"{name} cites a missing authorization: {cited}"
            actual = hashlib.sha256(document.read_bytes()).hexdigest()
            assert actual == digest, (
                f"{name} authorization {cited} has changed since it was cited "
                f"(recorded {digest[:16]}..., actual {actual[:16]}...)"
            )


def main() -> int:
    test_every_per_campaign_row_matches_the_combined_one()
    test_active_dataset_of_each_file_is_one_it_defines()
    test_publication_eligible_rows_carry_a_real_authorization()
    print("dataset selector row-agreement tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
