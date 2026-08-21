#!/usr/bin/env python3
"""Contract tests for the campaign ordinal tools/resubmit_held.py renders with.

B9: the tool passed the literal "1" to the renderer with no way to override it,
so any campaign not using ordinal 1 got its retries stamped with a different
ordinal from the jobs they complete. The ordinal is packed into the event ID,
so that lands two campaigns' events inside a single merge, and no downstream
validator would trace the mismatch back to the retry. HF_PT2_INT is ordinal 2
and exposed it on the first retry.

What these tests pin is not "the flag exists" but the property that made the
defect possible: the ordinal is derived from the jobs already on disk, and an
explicit value that contradicts them is refused rather than honoured.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "resubmit_held.py"
sys.path.insert(0, str(ROOT / "tools"))

import resubmit_held  # noqa: E402


def make_campaign(root: Path, ordinals: list[int]) -> Path:
    """A campaign directory whose attempt sidecars carry the given ordinals."""
    campaign_root = root / "HF_TEST"
    metadata = campaign_root / "attempt_metadata" / "MONASH"
    metadata.mkdir(parents=True)
    for index, ordinal in enumerate(ordinals):
        (metadata / f"job{index:03d}.json").write_text(
            json.dumps(
                {
                    "campaign": "HF_TEST",
                    "campaign_ordinal": ordinal,
                    "attempt": 0,
                    "logical_id": index,
                }
            )
        )
    return campaign_root


def run_cli(production_root: Path, *extra: str) -> subprocess.CompletedProcess:
    # These tests are about the ordinal, so they take the stated opt-out from
    # the seed-ledger requirement rather than carrying a ledger of their own.
    # The requirement itself is pinned in test_resubmit_held_seed_ledger.py.
    return subprocess.run(
        [
            sys.executable, str(TOOL), "HF_TEST",
            "--jobs", "2", "--events", "100", "--attempt", "1",
            "--no-ledger", "ordinal contract test, renders nothing",
            "--production-root", str(production_root), *extra,
        ],
        capture_output=True, text=True,
    )


def test_derives_unanimous_ordinal() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        campaign_root = make_campaign(Path(tmp), [2, 2, 2])
        ordinal, observed = resubmit_held.campaign_ordinal_on_disk(campaign_root)
        assert ordinal == 2, ordinal
        assert observed == {2}, observed


def test_no_metadata_is_underivable_rather_than_defaulting_to_one() -> None:
    """The old literal made "no evidence" and "ordinal 1" indistinguishable."""
    with tempfile.TemporaryDirectory() as tmp:
        campaign_root = make_campaign(Path(tmp), [])
        ordinal, observed = resubmit_held.campaign_ordinal_on_disk(campaign_root)
        assert ordinal is None, ordinal
        assert observed == set(), observed


def test_disagreeing_metadata_is_not_resolved_by_guessing() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        campaign_root = make_campaign(Path(tmp), [2, 3])
        ordinal, observed = resubmit_held.campaign_ordinal_on_disk(campaign_root)
        assert ordinal is None, ordinal
        assert observed == {2, 3}, observed


def test_cli_refuses_an_override_that_contradicts_disk() -> None:
    """The exact B9 failure: ordinal 1 rendered against an ordinal-2 campaign."""
    with tempfile.TemporaryDirectory() as tmp:
        make_campaign(Path(tmp), [2, 2])
        result = run_cli(Path(tmp), "--campaign-ordinal", "1")
        assert result.returncode == 1, result.returncode
        assert "disagrees with ordinal 2" in result.stderr, result.stderr


def test_cli_refuses_when_the_ordinal_cannot_be_derived() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        make_campaign(Path(tmp), [])
        result = run_cli(Path(tmp))
        assert result.returncode == 1, result.returncode
        assert "--campaign-ordinal" in result.stderr, result.stderr


def main() -> int:
    test_derives_unanimous_ordinal()
    test_no_metadata_is_underivable_rather_than_defaulting_to_one()
    test_disagreeing_metadata_is_not_resolved_by_guessing()
    test_cli_refuses_an_override_that_contradicts_disk()
    test_cli_refuses_when_the_ordinal_cannot_be_derived()
    print("resubmit_held ordinal tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
