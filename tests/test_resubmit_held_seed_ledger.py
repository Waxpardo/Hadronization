#!/usr/bin/env python3
"""Contract tests for the seed-ledger requirement in tools/resubmit_held.py.

The ledger is the only thing that can refuse a seed an earlier attempt already
burned. It used to be an optional argument with no default, so a retry rendered
without it ran with the collision guard OFF -- and a collision it would have
caught leaves no trace: the duplicated events are internally consistent, carry a
valid sidecar, and no downstream validator can tell them from independent draws.
The failure is therefore invisible in exactly the way that matters, and the only
place it can be caught is at the point of rendering.

What these tests pin is not "the flag exists" but the property that made the
silent-off state possible: the tool cannot run without SAYING which guard state
it is in. Omission is refused, the opt-out must carry a reason, and the chosen
state is printed in the dry run -- which is the run an operator reads before
applying.

A default ledger path was rejected deliberately and that choice is pinned here
too: it would have made a retry against the WRONG ledger look served, which is
worse than a missing argument, because it reads as a guard that ran.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "resubmit_held.py"


def make_campaign(root: Path) -> None:
    """A campaign whose sidecars are complete enough to reach the summary.

    The names must match campaign_status.ATTEMPT_STEM or the attempt is skipped
    and the ordinal reads as underivable, which would return before the lines
    these tests are about.
    """
    metadata = root / "HF_TEST" / "attempt_metadata" / "MONASH"
    metadata.mkdir(parents=True)
    for job in range(2):
        name = f"hf_MONASH_job{job:03d}_attempt0_5500000_{job}.json"
        (metadata / name).write_text(
            json.dumps(
                {
                    "campaign": "HF_TEST",
                    "campaign_ordinal": 2,
                    "attempt": 0,
                    "logical_id": job,
                    "card_variant": "NONE",
                }
            )
        )


def fake_condor(bin_dir: Path) -> None:
    """A condor_q that reports an empty held queue.

    resubmit_held hard-fails when condor_q is absent -- deliberately, because a
    missing condor once meant a retry rendered while the hung job kept its slot.
    That check sits before the lines under test, so these tests supply a condor_q
    rather than weaken the tool to accommodate them.
    """
    bin_dir.mkdir(parents=True, exist_ok=True)
    probe = bin_dir / "condor_q"
    probe.write_text("#!/bin/sh\nexit 0\n")
    probe.chmod(0o755)


def run_cli(tmp: Path, *extra: str) -> subprocess.CompletedProcess:
    bin_dir = tmp / "bin"
    fake_condor(bin_dir)
    env = dict(os.environ)
    env["PATH"] = f"{bin_dir}{os.pathsep}{env.get('PATH', '')}"
    env.pop("HADRONIZATION_BASE", None)
    return subprocess.run(
        [
            sys.executable, str(TOOL), "HF_TEST",
            "--jobs", "2", "--events", "100", "--attempt", "1",
            "--production-root", str(tmp), *extra,
        ],
        capture_output=True, text=True, env=env,
    )


def test_omitting_the_ledger_entirely_is_refused() -> None:
    """The defect: no ledger, no complaint, guard silently off."""
    with tempfile.TemporaryDirectory() as tmp:
        make_campaign(Path(tmp))
        result = run_cli(Path(tmp))
        assert result.returncode == 2, (result.returncode, result.stdout)
        assert "--seed-ledger" in result.stderr, result.stderr
        assert "--no-ledger" in result.stderr, result.stderr


def test_a_ledger_is_accepted_and_reports_the_guard_on() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        make_campaign(Path(tmp))
        ledger = Path(tmp) / "burned_seeds.txt"
        ledger.write_text("")
        result = run_cli(Path(tmp), "--seed-ledger", str(ledger))
        assert result.returncode == 0, (result.returncode, result.stderr)
        assert "collision guard ON" in result.stdout, result.stdout


def test_the_opt_out_is_accepted_and_states_its_reason() -> None:
    """Opting out is allowed, but never silently: the reason is in the output."""
    with tempfile.TemporaryDirectory() as tmp:
        make_campaign(Path(tmp))
        result = run_cli(Path(tmp), "--no-ledger", "scratch campaign, discarded")
        assert result.returncode == 0, (result.returncode, result.stderr)
        assert "collision guard OFF" in result.stdout, result.stdout
        assert "scratch campaign, discarded" in result.stdout, result.stdout


def test_an_empty_reason_is_not_a_stated_one() -> None:
    """--no-ledger '' would otherwise satisfy the requirement while saying nothing."""
    with tempfile.TemporaryDirectory() as tmp:
        make_campaign(Path(tmp))
        for blank in ("", "   "):
            result = run_cli(Path(tmp), "--no-ledger", blank)
            assert result.returncode == 2, (blank, result.returncode)
            assert "non-empty reason" in result.stderr, result.stderr


def test_a_ledger_and_an_opt_out_together_are_refused() -> None:
    """Passing both leaves the actual guard state ambiguous to the reader."""
    with tempfile.TemporaryDirectory() as tmp:
        make_campaign(Path(tmp))
        ledger = Path(tmp) / "burned_seeds.txt"
        ledger.write_text("")
        result = run_cli(
            Path(tmp), "--seed-ledger", str(ledger), "--no-ledger", "why"
        )
        assert result.returncode == 2, result.returncode
        assert "not allowed with" in result.stderr, result.stderr


def test_the_requirement_holds_in_dry_run_too() -> None:
    """A dry run that skipped the check would preview a guard state it will not use.

    The dry run is what an operator reads before --apply, so it has to be the
    same shape as the apply. This is the run in which the omission was invisible.
    """
    with tempfile.TemporaryDirectory() as tmp:
        make_campaign(Path(tmp))
        result = run_cli(Path(tmp))
        assert "--apply" not in result.stdout
        assert result.returncode == 2, result.returncode


def main() -> int:
    test_omitting_the_ledger_entirely_is_refused()
    test_a_ledger_is_accepted_and_reports_the_guard_on()
    test_the_opt_out_is_accepted_and_states_its_reason()
    test_an_empty_reason_is_not_a_stated_one()
    test_a_ledger_and_an_opt_out_together_are_refused()
    test_the_requirement_holds_in_dry_run_too()
    print("resubmit_held seed-ledger tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
