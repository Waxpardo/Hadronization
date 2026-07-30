#!/usr/bin/env python3
"""Regression tests for full-production and Gate-B manifest schemas."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "tools/generate_gate_b_pilots.py"
VALIDATOR = ROOT / "tools/campaign_manifest.py"
TUNES = ("MONASH", "JUNCTIONS", "CLOSEPACKING")


def run(*arguments: str, cwd: Path | None = None, expect: int = 0) -> subprocess.CompletedProcess:
    result = subprocess.run(
        list(arguments), cwd=cwd, text=True, capture_output=True, check=False
    )
    if result.returncode != expect:
        raise AssertionError(
            f"command returned {result.returncode}, expected {expect}: "
            f"{' '.join(arguments)}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def prepare_contract_checkout(root: Path) -> None:
    (root / "config").mkdir(parents=True)
    (root / "SimulationScripts").mkdir()
    for name in (
        "heavy_flavour_species_v1.json",
        "heavy_flavour_pair_registry_v1.json",
        "tune_difference_allowlist_v1.json",
    ):
        shutil.copy2(ROOT / "config" / name, root / "config" / name)
    for tune in TUNES:
        name = f"pythiasettings_Hard_Low_ccbb_{tune}.cmnd"
        shutil.copy2(
            ROOT / "SimulationScripts" / name,
            root / "SimulationScripts" / name,
        )
    run("git", "init", "-q", cwd=root)
    run("git", "config", "user.name", "Manifest Test", cwd=root)
    run("git", "config", "user.email", "manifest-test@example.invalid", cwd=root)
    run("git", "add", "config", "SimulationScripts", cwd=root)
    run("git", "commit", "-q", "-m", "contract fixture", cwd=root)


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="hadronization_manifest_test_") as temporary:
        fixture = Path(temporary)
        prepare_contract_checkout(fixture)
        campaign = "HF_GATEB_manifest_test"
        run(
            "python3",
            str(GENERATOR),
            "--root",
            str(fixture),
            "--campaign",
            campaign,
            "--campaign-ordinal",
            "123",
            "--seed-base",
            "330000001",
        )
        campaign_dir = fixture / "campaigns" / campaign
        valid = run("python3", str(VALIDATOR), "validate", str(campaign_dir))
        assert "Gate-B campaign valid: candidates=9" in valid.stdout

        config_path = campaign_dir / "campaign.json"
        config = json.loads(config_path.read_text())
        config["repository_implementation_commit"] = "0" * 40
        config_path.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n")
        stale = run(
            "python3",
            str(VALIDATOR),
            "validate",
            str(campaign_dir),
            expect=1,
        )
        assert "implementation commit differs" in stale.stderr

    print("campaign-manifest tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
