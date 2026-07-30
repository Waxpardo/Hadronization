#!/usr/bin/env python3
"""Regression tests for full-production and Gate-B manifest schemas."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "tools/generate_gate_b_pilots.py"
VALIDATOR = ROOT / "tools/campaign_manifest.py"
TUNES = ("MONASH", "JUNCTIONS", "CLOSEPACKING")


def approve_pthat_spec_for_fixture(path: Path) -> None:
    payload = json.loads(path.read_text())
    payload["scientific_review_status"] = "APPROVED_GATE_B_OWNER_REVIEW"
    payload["scientific_review"] = {
        "decision": "APPROVE_PTHAT_SENSITIVITY_SPEC",
        "reviewer": "Independent Physics Reviewer",
        "reviewer_role":
            "project_owner_or_designated_physics_statistics_reviewer",
        "decision_utc": datetime.now(timezone.utc).isoformat(),
        "rationale":
            "Synthetic approval exists only inside an isolated test checkout.",
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def run(
    *arguments: str, cwd: Path | None = None, expect: int = 0
) -> subprocess.CompletedProcess:
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
    (root / "tools").mkdir()
    for name in (
        "heavy_flavour_species_v1.json",
        "heavy_flavour_pair_registry_v1.json",
        "tune_difference_allowlist_v1.json",
        "pthat_sensitivity_v1.json",
    ):
        shutil.copy2(ROOT / "config" / name, root / "config" / name)
    shutil.copy2(
        ROOT / "tools/evaluate_pthat_sensitivity.py",
        root / "tools/evaluate_pthat_sensitivity.py",
    )
    pending = run(
        "python3",
        str(GENERATOR),
        "--root",
        str(root),
        "--campaign",
        "pending_review_must_fail",
        "--campaign-ordinal",
        "122",
        "--seed-base",
        "329000001",
        expect=1,
    )
    assert "pre-pilot scientific approval" in pending.stderr
    approve_pthat_spec_for_fixture(
        root / "config/pthat_sensitivity_v1.json"
    )
    for tune in TUNES:
        name = f"pythiasettings_Hard_Low_ccbb_{tune}.cmnd"
        shutil.copy2(
            ROOT / "SimulationScripts" / name,
            root / "SimulationScripts" / name,
        )
    run("git", "init", "-q", cwd=root)
    run("git", "config", "user.name", "Manifest Test", cwd=root)
    run("git", "config", "user.email", "manifest-test@example.invalid", cwd=root)
    run("git", "add", "config", "SimulationScripts", "tools", cwd=root)
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
        fixture_spec = fixture / "config/pthat_sensitivity_v1.json"
        approved_spec = fixture_spec.read_bytes()
        fixture_spec.write_bytes(
            (ROOT / "config/pthat_sensitivity_v1.json").read_bytes()
        )
        pending_validation = run(
            "python3",
            str(VALIDATOR),
            "validate",
            str(campaign_dir),
            expect=1,
        )
        assert "pre-pilot scientific approval" in pending_validation.stderr
        fixture_spec.write_bytes(approved_spec)
        first_candidate = json.loads(
            (campaign_dir / "candidate_manifest.jsonl").read_text().splitlines()[0]
        )
        assert len(first_candidate["effective_card_sha256"]) == 64
        assert len(first_candidate["repository_commit"]) == 40

        (fixture / "analysis_tool.txt").write_text("descendant analysis tool\n")
        run("git", "add", "analysis_tool.txt", cwd=fixture)
        run("git", "commit", "-q", "-m", "analysis-only descendant", cwd=fixture)
        exact = run(
            "python3",
            str(VALIDATOR),
            "validate",
            str(campaign_dir),
            expect=1,
        )
        assert "implementation commit differs" in exact.stderr
        ancestor = run(
            "python3",
            str(VALIDATOR),
            "validate",
            str(campaign_dir),
            "--implementation-policy",
            "ancestor",
        )
        assert "Gate-B campaign valid: candidates=9" in ancestor.stdout

        config_path = campaign_dir / "campaign.json"
        config = json.loads(config_path.read_text())
        config["repository_commit"] = "0" * 40
        config["repository_implementation_commit"] = "0" * 40
        config_path.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n")
        stale = run(
            "python3",
            str(VALIDATOR),
            "validate",
            str(campaign_dir),
            "--implementation-policy",
            "ancestor",
            expect=1,
        )
        assert (
            "campaign commit" in stale.stderr
            or "not an ancestor" in stale.stderr
        )

    print("campaign-manifest tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
