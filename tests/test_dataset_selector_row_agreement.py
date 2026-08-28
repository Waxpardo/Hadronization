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

# Same directory as this driver, so no path setup is needed.
from sandbox_tree import tracked_paths

ROOT = Path(__file__).resolve().parents[1]
COMBINED = ROOT / "config" / "dataset_selector.json"


def per_campaign_selectors() -> list[Path]:
    """Every TRACKED per-campaign selector, found by pattern rather than name.

    The pattern stays broad so a selector added later is compared rather than
    ignored. An untracked local file is not one this repository must agree
    with, and before the intersection one could fail this gate on its own.
    """
    tracked = tracked_paths(ROOT, "config")
    return sorted(p for p in (ROOT / "config").glob("dataset_selector_*.json")
                  if p in tracked)


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


def rows_citing_an_authorization() -> dict[str, tuple[str, object, bool]]:
    """Every row that names an authorization document, from both file layouts.

    A row that names none is absent here. `publication_authorization` is null
    for a dataset that answers to no document, and a null is not a claim. A
    path IS a claim, whatever the eligibility beside it.
    """
    rows: dict[str, tuple[str, object, bool]] = {}
    for path in [COMBINED, *per_campaign_selectors()]:
        for name, row in json.loads(path.read_text())["datasets"].items():
            cited = row.get("publication_authorization")
            if not cited:
                continue
            rows[name] = (cited, row.get("publication_authorization_sha256"),
                          bool(row.get("publication_eligible")))
    return rows


def verify_cited_authorizations() -> set[str]:
    """Check every cited authorization and return the rows actually checked.

    The returned set is the enforcement evidence:
    `test_the_pin_is_checked_on_rows_that_cannot_be_published` compares it
    against the rows that carry a citation, so a guard that quietly narrows
    this loop fails that test instead of passing silently.
    """
    verified: set[str] = set()
    for name, (cited, digest, _eligible) in sorted(
            rows_citing_an_authorization().items()):
        assert isinstance(digest, str) and len(digest) == 64, \
            f"{name} cites {cited} with no sha256"
        document = ROOT / cited
        assert document.is_file(), \
            f"{name} cites a missing authorization: {cited}"
        actual = hashlib.sha256(document.read_bytes()).hexdigest()
        assert actual == digest, (
            f"{name} authorization {cited} has changed since it was cited "
            f"(recorded {digest[:16]}..., actual {actual[:16]}...)"
        )
        verified.add(name)
    return verified


def test_publication_eligible_rows_carry_a_real_authorization() -> None:
    """Eligibility without a resolvable, hash-matching authorization is a claim.

    The selector validator stopped enforcing these fields -- they were moved to
    the gate layer -- so nothing else checks that the cited document exists or
    that its recorded digest still describes it. An authorization that has been
    edited since it was cited is worse than none: it reads as reviewed.
    """
    cited = rows_citing_an_authorization()
    for name, row in json.loads(COMBINED.read_text())["datasets"].items():
        if row.get("publication_eligible"):
            assert name in cited, \
                f"{name} is publication_eligible with no authorization"
    assert verify_cited_authorizations(), "no row cites an authorization"


def test_the_pin_is_checked_on_rows_that_cannot_be_published() -> None:
    """A pin that cannot fail is fail-open, so eligibility must not gate it.

    Seven systematic-variation rows cite the pre-registration that designed
    them and carry `publication_eligible: false`. The check above once skipped
    every ineligible row, so those seven digests could drift with nothing to
    catch it. They did: `382b85d` of 2026-08-21 rewrote seven `STATE.md`
    references in `docs/SYSTEMATICS_PREREGISTRATION.md` and left the pin on the
    superseded bytes, where it stayed unenforced until brief Q re-pinned it.
    This test fails if that eligibility skip returns.
    """
    citing = rows_citing_an_authorization()
    ineligible = {name for name, (_c, _d, eligible) in citing.items()
                  if not eligible}
    assert ineligible, (
        "expected the systematic-variation rows to cite the pre-registration; "
        "if they no longer do, this contract needs re-stating, not deleting"
    )
    unchecked = ineligible - verify_cited_authorizations()
    assert not unchecked, (
        "these rows cite an authorization that nothing verifies: "
        f"{sorted(unchecked)}. An eligibility guard has been restored, and "
        "their pin can no longer fail."
    )


def main() -> int:
    test_every_per_campaign_row_matches_the_combined_one()
    test_active_dataset_of_each_file_is_one_it_defines()
    test_publication_eligible_rows_carry_a_real_authorization()
    test_the_pin_is_checked_on_rows_that_cannot_be_published()
    print("dataset selector row-agreement tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
