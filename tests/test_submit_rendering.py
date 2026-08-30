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

# Same directory as this driver, so no path setup is needed.
from sandbox_tree import tracked_names

ROOT = Path(__file__).resolve().parents[1]
RENDERER = ROOT / "tools" / "render_production_submit.py"
FAKE_SHA = "a" * 64

sys.path.insert(0, str(ROOT / "tools"))
from campaign import PUBLISHED_TUNES  # noqa: E402

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
    """A clean throwaway checkout holding the tracked tune cards.

    The renderer refuses to run from a dirty checkout, so it cannot be pointed
    at the working tree during development. Building a committed temp repo
    keeps these tests independent of local edits while still exercising the
    real git path.

    The copy admits tracked cards only. `tests/sandbox_tree.py` states the
    rule and the incident behind it: an untracked card beside the tracked
    ones would be committed here and would decide what these cases measure.
    """
    checkout = directory / "checkout"
    (checkout / "generation" / "cards").mkdir(parents=True)
    tracked = tracked_names(ROOT, "generation/cards")
    for card in sorted(
            (ROOT / "generation" / "cards").glob(
                "pythiasettings_Hard_Low_ccbb_*.cmnd")):
        if card.name in tracked:
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


def test_every_published_tune_renders_with_its_own_card() -> None:
    """One row set per published tune, each carrying a distinct effective card.

    Ruling R32 of 2026-08-30 removed the fourth, matched tune, so this covers
    three rather than four. What it protects is unchanged and is why the case
    exists: a tune must not silently reuse another tune's effective card, which
    is the `effective_card_sha256` column the renderer writes.

    The tune list comes from `campaign.PUBLISHED_TUNES`, so a tune added or
    removed there is covered here without a second edit.
    """
    with tempfile.TemporaryDirectory() as directory:
        checkout = make_checkout(Path(directory))
        submit = Path(directory) / "variants.sub"
        arguments: list[str] = []
        for tune in PUBLISHED_TUNES:
            arguments += ["--tune", tune]
        render(checkout, submit, *arguments)

        rows = queue_rows(submit)
        assert {row.split(",")[2] for row in rows} == set(PUBLISHED_TUNES)
        seeds = [row.split(",")[6] for row in rows]
        assert len(set(seeds)) == len(seeds)

        cards = {row.split(",")[2]: row.split(",")[12] for row in rows}
        assert len(set(cards.values())) == len(PUBLISHED_TUNES), cards


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


def test_the_checkout_carries_only_tracked_cards() -> None:
    """Both sides come from the tree, so this holds on every host."""
    with tempfile.TemporaryDirectory() as directory:
        checkout = make_checkout(Path(directory))
        got = {p.name for p in (checkout / "generation/cards").iterdir()}
    want = {name for name in tracked_names(ROOT, "generation/cards")
            if name.startswith("pythiasettings_Hard_Low_ccbb_")
            and name.endswith(".cmnd")}
    assert got == want, sorted(got ^ want)


def main() -> int:
    assert_fixture_ordinal_is_free()
    test_the_checkout_carries_only_tracked_cards()
    test_liveness_guard_present()
    test_deterministic_and_seeds_unique()
    test_every_published_tune_renders_with_its_own_card()
    test_cpu_guard_must_be_reachable()
    test_write_once()
    test_seed_ledger_refuses_burned_seed()
    print("submit rendering tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
