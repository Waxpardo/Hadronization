#!/usr/bin/env python3
"""Contract tests for tools/render_production_submit.py.

The renderer no longer consumes a sealed candidate manifest. It takes
(tune, jobs, events) and derives everything else, so these tests check the
properties that actually matter: the same command gives the same file, seeds
never collide, the liveness guard is present, and a burned seed is refused.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RENDERER = ROOT / "tools" / "render_production_submit.py"
FAKE_SHA = "a" * 64

# A campaign this test invents must not take an ordinal the project has
# claimed: tools/render_production_submit.py reads
# config/campaign_ordinals_v1.json and refuses one, which is the point of the
# registry. The value is a literal rather than a computation over the registry,
# so a reader can check it by eye; the assertion below fails loudly, and says
# what to do, if the registry ever grows to hold it.
FIXTURE_ORDINAL = 12


def assert_fixture_ordinal_is_free() -> None:
    registry = json.loads(
        (ROOT / "config/campaign_ordinals_v1.json").read_text())
    held = {entry["ordinal"] for entry in registry["ordinals"]}
    assert FIXTURE_ORDINAL not in held, (
        f"config/campaign_ordinals_v1.json now claims ordinal "
        f"{FIXTURE_ORDINAL}; raise FIXTURE_ORDINAL in this file to an ordinal "
        f"the registry does not hold, and update the burned-seed literal that "
        f"is derived from it")


def make_checkout(directory: Path) -> Path:
    """A clean throwaway checkout holding the tune cards.

    The renderer refuses to run from a dirty checkout, so it cannot be pointed
    at the working tree during development. Building a committed temp repo
    keeps these tests independent of local edits while still exercising the
    real git path.
    """
    checkout = directory / "checkout"
    (checkout / "generation" / "cards").mkdir(parents=True)
    for card in (ROOT / "generation" / "cards").glob("pythiasettings_Hard_Low_ccbb_*.cmnd"):
        shutil.copy2(card, checkout / "generation" / "cards" / card.name)
    for command in (
        ["git", "init", "-q"],
        ["git", "config", "user.email", "test@example.invalid"],
        ["git", "config", "user.name", "test"],
        ["git", "add", "-A"],
        ["git", "commit", "-qm", "cards"],
    ):
        subprocess.run(command, cwd=checkout, check=True, capture_output=True)
    return checkout


def render(
    checkout: Path, output: Path, *extra: str, expect: int = 0
) -> subprocess.CompletedProcess:
    result = subprocess.run(
        [
            sys.executable, str(RENDERER), str(checkout), str(output),
            "--campaign", "RENDERTEST",
            "--campaign-ordinal", str(FIXTURE_ORDINAL),
            "--jobs", "3", "--events", "100000",
            "--producer-executable-sha256", FAKE_SHA,
            *extra,
        ],
        text=True, capture_output=True, check=False,
    )
    assert result.returncode == expect, result.stderr
    return result


def queue_rows(submit: Path) -> list[str]:
    return [
        line.strip()
        for line in submit.read_text().splitlines()
        if line.strip().startswith("RENDERTEST,")
    ]


def test_liveness_guard_present() -> None:
    """on_exit_hold cannot catch a job that never exits; periodic_hold can."""
    with tempfile.TemporaryDirectory() as directory:
        checkout = make_checkout(Path(directory))
        submit = Path(directory) / "prod.sub"
        render(checkout, submit)
        text = submit.read_text()
        assert "periodic_hold = (JobStatus == 2)" in text
        assert "RemoteUserCpu > 3600" in text
        assert "(CurrentTime - EnteredCurrentStatus) > 14400" in text
        assert "periodic_hold_reason" in text
        assert "on_exit_hold" in text

        custom = Path(directory) / "custom.sub"
        render(checkout, custom, "--max-cpu-seconds", "600")
        assert "RemoteUserCpu > 600" in custom.read_text()


def test_deterministic_and_seeds_unique() -> None:
    with tempfile.TemporaryDirectory() as directory:
        checkout = make_checkout(Path(directory))
        first = Path(directory) / "a.sub"
        second = Path(directory) / "b.sub"
        render(checkout, first)
        render(checkout, second)
        assert first.read_bytes() == second.read_bytes()

        rows = queue_rows(first)
        assert len(rows) == 9, rows
        seeds = [row.split(",")[6] for row in rows]
        assert len(set(seeds)) == len(seeds), seeds
        assert {row.split(",")[2] for row in rows} == {
            "MONASH", "JUNCTIONS", "CLOSEPACKING"
        }


def test_all_four_tunes_render() -> None:
    """MONASH, JUNCTIONS, CLOSEPACKING and the matched JUNCTIONS variant."""
    with tempfile.TemporaryDirectory() as directory:
        checkout = make_checkout(Path(directory))
        submit = Path(directory) / "variants.sub"
        render(
            checkout, submit,
            "--tune", "JUNCTIONS", "--tune", "JUNCTIONS_MATCHED",
            "--tune", "CLOSEPACKING", "--tune", "MONASH",
        )
        rows = queue_rows(submit)
        assert len({row.split(",")[2] for row in rows}) == 4
        seeds = [row.split(",")[6] for row in rows]
        assert len(set(seeds)) == len(seeds)
        # A variant must not silently reuse its parent's effective card.
        cards = {row.split(",")[2]: row.split(",")[12] for row in rows}
        assert cards["JUNCTIONS"] != cards["JUNCTIONS_MATCHED"]
        assert cards["MONASH"] != cards["JUNCTIONS_MATCHED"]


def test_cpu_guard_must_be_reachable() -> None:
    """A CPU limit above the wall backstop would never fire."""
    with tempfile.TemporaryDirectory() as directory:
        checkout = make_checkout(Path(directory))
        result = render(
            checkout, Path(directory) / "bad.sub",
            "--max-cpu-seconds", "9000", "--max-runtime-seconds", "600",
            expect=1,
        )
        assert "unreachable" in result.stderr


def test_write_once() -> None:
    with tempfile.TemporaryDirectory() as directory:
        checkout = make_checkout(Path(directory))
        submit = Path(directory) / "once.sub"
        render(checkout, submit)
        render(checkout, submit)  # identical content is accepted
        result = render(checkout, submit, "--max-cpu-seconds", "900", expect=1)
        assert "refusing overwrite" in result.stderr


def test_seed_ledger_refuses_burned_seed() -> None:
    with tempfile.TemporaryDirectory() as directory:
        ledger = Path(directory) / "burned.txt"
        # seed_derivation_v2: the render helper passes
        # --campaign-ordinal FIXTURE_ORDINAL, so the first seed is
        # SEED_BASE + 12*CAMPAIGN_STRIDE = 220000001, not the v1 value
        # 100000001. Pinning the v1 value would make this test pass vacuously
        # -- no collision, no refusal, and the guard goes untested.
        ledger.write_text("# previously used\n220000001\n")
        checkout = make_checkout(Path(directory))
        result = render(
            checkout, Path(directory) / "ledger.sub",
            "--seed-ledger", str(ledger), expect=1,
        )
        assert "already burned" in result.stderr


def main() -> int:
    assert_fixture_ordinal_is_free()
    test_liveness_guard_present()
    test_deterministic_and_seeds_unique()
    test_all_four_tunes_render()
    test_cpu_guard_must_be_reachable()
    test_write_once()
    test_seed_ledger_refuses_burned_seed()
    print("submit rendering tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
