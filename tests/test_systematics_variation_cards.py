#!/usr/bin/env python3
"""Contract tests for the systematics variation machinery.

Three defects motivated these, and the tests pin the properties that made each
possible rather than the fix.

1. THE WORKER COULD NOT RUN AT ALL. The 2026-08-12 restructure moved
   runCondorJob.sh from the repository root into generation/submit/ without
   updating its `dirname $0` derivation of project_base, so it resolved to
   <checkout>/generation/submit and every job exited 3 at the
   required-component check. Nothing caught it because the Nikhef checkout is
   still at the pre-restructure commit, so no production job has ever been
   launched from the restructured layout -- the first one would have been a
   systematics variation. The test asserts the derivation, not the fix, so the
   next move of this file fails here instead of on a worker node.

2. A VARIATION THAT VARIES SOMETHING ELSE, OR NOTHING. A hand-edited card is a
   card whose difference from the nominal nobody checked, and both failure
   modes look like a physics result. Re-derived here independently of the
   generator: parse both cards, diff the key sets.

3. A CARD KEY THE PRODUCER REJECTS. The producer throws on any configured key
   outside kAuditedPythiaSettingKeys, which would fail every job of a campaign
   after the queue wait rather than at generation time.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Same directory as this driver, so no path setup is needed.
from sandbox_tree import tracked_files, tracked_names

ROOT = Path(__file__).resolve().parents[1]
WORKER = ROOT / "generation" / "submit" / "runCondorJob.sh"
GENERATOR = ROOT / "tools" / "make_systematic_cards.py"
RENDERER = ROOT / "tools" / "render_production_submit.py"

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
sys.path.insert(0, str(ROOT / "tools"))

import make_systematic_cards  # noqa: E402
from campaign import CARD_VARIANT_NONE, PUBLISHED_TUNES, resolve_card_path  # noqa: E402

FAKE_SHA = "a" * 64
DECLARED = json.loads(
    (ROOT / "config" / "systematics_variations_v1.json").read_text()
)


def test_generated_cards_are_current() -> None:
    """The cards on disk are what the declaration says they should be."""
    result = subprocess.run(
        [sys.executable, str(GENERATOR), "--check"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_each_card_differs_from_its_nominal_in_exactly_one_setting() -> None:
    """Re-derived independently of the generator that wrote the cards."""
    legal = make_systematic_cards.audited_keys(ROOT)
    for variation in DECLARED["variations"]:
        name = str(variation["name"])
        setting = str(variation["setting"])
        value = str(variation["value"])
        for tune in PUBLISHED_TUNES:
            nominal_path = resolve_card_path(ROOT, tune, CARD_VARIANT_NONE)
            varied_path = resolve_card_path(ROOT, tune, name)
            assert varied_path.is_file(), varied_path
            nominal = make_systematic_cards.parse_card(
                nominal_path.read_text(), nominal_path.name
            )
            varied = make_systematic_cards.parse_card(
                varied_path.read_text(), varied_path.name
            )
            differing = {
                key
                for key in set(nominal) | set(varied)
                if nominal.get(key) != varied.get(key)
            }
            assert differing == {setting}, (name, tune, sorted(differing))
            assert varied[setting] == value, (name, tune, varied[setting])
            # Varying nothing is the failure that would read as a null result.
            assert nominal.get(setting) != value, (name, tune)
            unaudited = set(varied) - legal
            assert not unaudited, (name, tune, sorted(unaudited))


def test_variation_settings_are_not_licensed_to_differ_across_tunes() -> None:
    """The point of the separate config file.

    These keys are audited so the producer accepts them, but they are NOT in
    the tune allowlist -- so the cross-tune audit still requires one varied
    value shared by all three tunes, which is what a variation is. Putting them
    in allowed_tune_differences would have licensed a card that varied the
    scale for JUNCTIONS only.
    """
    allowlist = json.loads(
        (ROOT / "config" / "tune_difference_allowlist_v1.json").read_text()
    )
    classified = (
        set(allowlist["common_required_card_values"])
        | set(allowlist["allowed_tune_differences"])
        | set(allowlist["allowed_per_job_differences"])
    )
    variation_only = make_systematic_cards.variation_settings(ROOT)
    assert variation_only, "no systematic variation settings declared"
    assert not (variation_only & classified), sorted(variation_only & classified)


def test_generated_header_audits_the_variation_settings() -> None:
    """The producer's compiled key list must contain them, or it throws."""
    header = (
        ROOT / "generation" / "registries" / "GeneratedTuneSettingRegistry.h"
    ).read_text()
    for key in sorted(make_systematic_cards.variation_settings(ROOT)):
        assert f'"{key}"' in header, key


def test_campaign_ordinals_and_names_are_unique() -> None:
    ordinals = [int(v["campaign_ordinal"]) for v in DECLARED["variations"]]
    campaigns = [str(v["campaign"]) for v in DECLARED["variations"]]
    assert len(set(ordinals)) == len(ordinals), ordinals
    assert len(set(campaigns)) == len(campaigns), campaigns
    # Ordinals 0 and 3 are burned by HF_SMOKE and HF_RUN3_V1.
    assert not ({0, 3} & set(ordinals)), sorted({0, 3} & set(ordinals))


# --------------------------------------------------------------------------
# The worker
# --------------------------------------------------------------------------


def run_worker(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", str(WORKER), "--campaign", *args],
        capture_output=True, text=True,
    )


def worker_args(card_variant: str = CARD_VARIANT_NONE) -> list[str]:
    return [
        "PROBE", "9", "MONASH", "0", "primary", "0", "123", "1000",
        "NONE", "0", "0" * 40, FAKE_SHA, "b" * 64, card_variant, "1", "0",
    ]


def test_worker_resolves_project_base_to_the_checkout_root() -> None:
    """The launch-blocking regression, pinned.

    The worker gets as far as the required-component check and names the path
    it looked in. That path is the evidence: before the fix it read
    <checkout>/generation/submit/generation/producer/..., which exists nowhere.
    """
    result = run_worker(*worker_args())
    assert result.returncode != 0
    message = result.stdout + result.stderr
    assert "generation/submit/generation" not in message, message
    # Either the producer is absent (a laptop) or the run proceeds past this
    # point (a built checkout). Both are fine; resolving into generation/submit
    # is not.
    if "required component missing" in message:
        assert (
            f"{ROOT}/generation/producer/heavyflavourcorrelations_status"
            in message
        ), message


def test_worker_requires_the_card_variant_argument() -> None:
    """The 15-argument form is refused rather than shifting cluster/process."""
    result = run_worker(*[a for a in worker_args() if a != CARD_VARIANT_NONE])
    assert result.returncode == 2
    assert "CARD_VARIANT" in result.stdout + result.stderr


def test_worker_rejects_an_unsafe_card_variant() -> None:
    """The variant becomes part of a path."""
    for bad in ("Upper", "with space", "../escape", "trailing-"):
        result = run_worker(*worker_args(bad))
        assert result.returncode == 2, (bad, result.stdout, result.stderr)
        assert "card_variant" in result.stdout + result.stderr, bad


# --------------------------------------------------------------------------
# The renderer
# --------------------------------------------------------------------------


def make_checkout(directory: Path) -> Path:
    """A clean throwaway checkout: the tracked nominal AND variation cards.

    The copy admits tracked cards only, at both levels. `tests/sandbox_tree.py`
    states the rule and the incident behind it: a copytree of the real
    `systematics/` carries every untracked card a local generator run left
    there, and `git add -A` below commits it.
    """
    checkout = directory / "checkout"
    cards = checkout / "generation" / "cards"
    cards.mkdir(parents=True)
    tracked = tracked_names(ROOT, "generation/cards")
    for card in sorted((ROOT / "generation" / "cards").glob(
        "pythiasettings_Hard_Low_ccbb_*.cmnd"
    )):
        if card.name in tracked:
            shutil.copy2(card, cards / card.name)
    (cards / "systematics").mkdir()
    for name in tracked_files(ROOT, "generation/cards/systematics"):
        target = cards / "systematics" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(
            ROOT / "generation" / "cards" / "systematics" / name, target)
    for command in (
        ["git", "init", "-q"],
        ["git", "config", "user.email", "test@example.invalid"],
        ["git", "config", "user.name", "test"],
        ["git", "add", "-A"],
        ["git", "commit", "-qm", "cards"],
    ):
        subprocess.run(command, cwd=checkout, check=True, capture_output=True)
    return checkout


def render(checkout: Path, output: Path, *extra: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            sys.executable, str(RENDERER), str(checkout), str(output),
            "--campaign", "HF_SYS_TEST",
            "--campaign-ordinal", str(FIXTURE_ORDINAL),
            "--jobs", "1", "--events", "1000",
            "--producer-executable-sha256", FAKE_SHA, *extra,
        ],
        capture_output=True, text=True,
    )


def test_renderer_pins_the_variant_card_not_the_nominal() -> None:
    """The sha in the submit file must be the variation's, or the worker's
    materialisation check would fail closed -- which is the safe direction, but
    it would fail 300 jobs at once after the queue wait."""
    with tempfile.TemporaryDirectory() as tmp:
        checkout = make_checkout(Path(tmp))
        nominal_out = Path(tmp) / "nominal.sub"
        variant_out = Path(tmp) / "variant.sub"
        assert render(checkout, nominal_out).returncode == 0
        result = render(checkout, variant_out, "--card-variant", "mur_up")
        assert result.returncode == 0, result.stderr

        nominal_text = nominal_out.read_text()
        variant_text = variant_out.read_text()
        assert "CARD_VARIANT" in variant_text
        assert "+HFCardVariant" in variant_text
        assert ",mur_up" in variant_text
        assert ",NONE" in nominal_text
        # Same tune, same events, different card => different pinned sha.
        def shas(text: str) -> set[str]:
            return {
                field
                for line in text.splitlines()
                if line.startswith("  HF_SYS_TEST,")
                for field in line.split(",")
                if len(field) == 64 and field != FAKE_SHA
            }
        assert shas(nominal_text) and shas(variant_text)
        assert not (shas(nominal_text) & shas(variant_text)), (
            shas(nominal_text), shas(variant_text)
        )


def test_renderer_refuses_an_unsafe_variant_and_a_missing_card() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        checkout = make_checkout(Path(tmp))
        bad = render(
            checkout, Path(tmp) / "bad.sub", "--card-variant", "NotAToken"
        )
        assert bad.returncode != 0
        assert "card-variant" in bad.stderr
        absent = render(
            checkout, Path(tmp) / "absent.sub", "--card-variant", "no_such_card"
        )
        assert absent.returncode != 0
        assert "no tune card" in absent.stderr


# --------------------------------------------------------------------------
# Retries
# --------------------------------------------------------------------------


def make_campaign(root: Path, variants: list[str | None]) -> Path:
    """A campaign whose attempt sidecars carry the given card variants."""
    campaign_root = root / "HF_SYS_TEST"
    metadata = campaign_root / "attempt_metadata" / "MONASH"
    metadata.mkdir(parents=True)
    for index, variant in enumerate(variants):
        payload = {
            "campaign": "HF_SYS_TEST",
            "campaign_ordinal": 4,
            "attempt": 0,
            "logical_id": index,
        }
        if variant is not None:
            payload["card_variant"] = variant
        (metadata / f"job{index:03d}.json").write_text(json.dumps(payload))
    return campaign_root


def test_retry_derives_the_card_variant_from_disk() -> None:
    """A retry that silently drew the nominal card would dilute the variation
    toward "no systematic", and every such job would be internally consistent,
    so nothing downstream could flag it."""
    import resubmit_held

    with tempfile.TemporaryDirectory() as tmp:
        campaign_root = make_campaign(Path(tmp), ["mur_up", "mur_up", "mur_up"])
        variant, observed = resubmit_held.card_variant_on_disk(campaign_root)
        assert variant == "mur_up", variant
        assert observed == {"mur_up"}, observed


def test_retry_refuses_a_campaign_carrying_two_variants() -> None:
    import resubmit_held

    with tempfile.TemporaryDirectory() as tmp:
        campaign_root = make_campaign(Path(tmp), ["mur_up", "muf_up"])
        variant, observed = resubmit_held.card_variant_on_disk(campaign_root)
        assert variant is None, variant
        assert observed == {"mur_up", "muf_up"}, observed


def test_sidecars_predating_the_variant_field_read_as_nominal() -> None:
    """Every campaign before 2026-08-17 is nominal by construction, so a
    missing key is NONE rather than unknown -- otherwise an old campaign's
    retry would become underivable."""
    import resubmit_held

    with tempfile.TemporaryDirectory() as tmp:
        campaign_root = make_campaign(Path(tmp), [None, None])
        variant, observed = resubmit_held.card_variant_on_disk(campaign_root)
        assert variant == CARD_VARIANT_NONE, variant
        assert observed == {CARD_VARIANT_NONE}, observed


def test_the_checkout_carries_only_tracked_cards() -> None:
    """Both sides come from the tree, so this holds on every host."""
    with tempfile.TemporaryDirectory() as directory:
        checkout = make_checkout(Path(directory))
        cards = checkout / "generation/cards"
        got = {p.name for p in cards.iterdir()}
        variations = {p.name for p in (cards / "systematics").iterdir()}
    want = {name for name in tracked_names(ROOT, "generation/cards")
            if name.startswith("pythiasettings_Hard_Low_ccbb_")
            and name.endswith(".cmnd")} | {"systematics"}
    assert got == want, sorted(got ^ want)
    want_variations = set(tracked_names(ROOT, "generation/cards/systematics"))
    assert variations == want_variations, \
        sorted(variations ^ want_variations)


def main() -> int:
    assert_fixture_ordinal_is_free()
    failures = 0
    for name, function in sorted(globals().items()):
        if not name.startswith("test_") or not callable(function):
            continue
        try:
            function()
        except Exception as error:  # noqa: BLE001
            failures += 1
            print(f"FAIL {name}: {error}")
        else:
            print(f"ok   {name}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
