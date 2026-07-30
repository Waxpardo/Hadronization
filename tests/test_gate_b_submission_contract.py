#!/usr/bin/env python3
"""Fail-closed regression tests for Gate-B runtime/submission provenance."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "tools/campaign_manifest.py"
GENERATOR = ROOT / "tools/generate_gate_b_pilots.py"
RENDERER = ROOT / "tools/render_production_submit.py"
TUNES = ("MONASH", "JUNCTIONS", "CLOSEPACKING")
sys.path.insert(0, str(ROOT / "tools"))
import campaign_manifest as contract  # noqa: E402
import run_publication_gate_b as gate_b  # noqa: E402



def _pending_pthat_spec_bytes() -> bytes:
    """An unapproved copy of the shipped pTHat specification.

    The repository's specification now carries a real Gate-B owner approval, so
    any "must be blocked" case has to derive its own unapproved copy instead of
    assuming the shipped artifact is unapproved.
    """
    spec = json.loads((ROOT / "config/pthat_sensitivity_v1.json").read_text())
    spec["scientific_review_status"] = "PENDING_GATE_B_OWNER_REVIEW"
    spec["scientific_review"] = {
        "decision": "PENDING",
        "reviewer": None,
        "reviewer_role": None,
        "decision_utc": None,
        "rationale": "Unapproved copy used to prove the gate blocks it.",
    }
    return (json.dumps(spec, indent=2, sort_keys=True) + "\n").encode()


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
            f"{' '.join(arguments)}\nstdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    return result


def prepare_checkout(root: Path) -> None:
    (root / "config").mkdir(parents=True)
    (root / "SimulationScripts").mkdir()
    for name in (
        "heavy_flavour_species_v1.json",
        "heavy_flavour_pair_registry_v1.json",
        "tune_difference_allowlist_v1.json",
        "pthat_sensitivity_v1.json",
    ):
        shutil.copy2(ROOT / "config" / name, root / "config" / name)
    approve_pthat_spec_for_fixture(
        root / "config/pthat_sensitivity_v1.json"
    )
    for tune in TUNES:
        name = f"pythiasettings_Hard_Low_ccbb_{tune}.cmnd"
        shutil.copy2(
            ROOT / "SimulationScripts" / name,
            root / "SimulationScripts" / name,
        )
    producer = root / "SimulationScripts/heavyflavourcorrelations_status"
    producer.write_text("#!/bin/sh\nexit 0\n")
    producer.chmod(0o755)
    gate_contract_files = {
        "tools/run_publication_gate_a.py",
        "tools/run_publication_gate_c.py",
        "tools/evaluate_pthat_sensitivity.py",
    }
    for specification in contract._gate_c_expected_specs(ROOT).values():
        gate_contract_files.update(specification["inputs"])
    for relative in sorted(gate_contract_files):
        source = ROOT / relative
        if not source.is_file():
            raise AssertionError(f"Gate fixture source is absent: {source}")
        destination = root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    (root / ".gitignore").write_text(
        "Production/\neffective.cmnd\nportable.root\nportable.root.sha256\n"
    )
    run("git", "init", "-q", cwd=root)
    run("git", "config", "user.name", "Submission Test", cwd=root)
    run(
        "git",
        "config",
        "user.email",
        "submission-test@example.invalid",
        cwd=root,
    )
    run(
        "git",
        "remote",
        "add",
        "origin",
        "https://github.com/Waxpardo/Hadronization.git",
        cwd=root,
    )
    run("git", "add", ".", cwd=root)
    run("git", "commit", "-q", "-m", "submission fixture", cwd=root)
    head = run("git", "rev-parse", "HEAD", cwd=root).stdout.strip()
    run(
        "git",
        "update-ref",
        "refs/remotes/origin/main",
        head,
        cwd=root,
    )


def write_submission_classads(
    output: Path,
    claim_path: Path,
    checkout: Path,
    cluster_id: int,
) -> None:
    claim = json.loads(claim_path.read_text())
    rows = []
    for process_id, allocation in enumerate(claim["allocations"]):
        rows.append(
            {
                "ClusterId": cluster_id,
                "ProcId": process_id,
                "JobStatus": 5,
                "Cmd": str(checkout / "runCondorJob.sh"),
                "Iwd": str(checkout),
                "Args": contract._expected_condor_args(
                    allocation,
                    cluster_id,
                    process_id,
                    claim["campaign"],
                ),
                "HFCampaign": claim["campaign"],
                "HFCampaignOrdinal": allocation["campaign_ordinal"],
                "HFTune": allocation["tune"],
                "HFLogicalId": allocation["logical_id"],
                "HFRole": allocation["role"],
                "HFAttempt": allocation["attempt"],
                "HFSeed": allocation["seed"],
                "HFRequestedSuccesses":
                    allocation["requested_successes"],
                "HFPTHat": allocation["pthat_min_override"],
                "HFMultiplicityAuditEvents":
                    allocation["multiplicity_audit_events"],
                "HFRepositoryCommit": allocation["repository_commit"],
                "HFEffectiveCardSHA256":
                    allocation["effective_card_sha256"],
                "HFProducerExecutableSHA256":
                    allocation["producer_executable_sha256"],
            }
        )
    output.write_text(json.dumps(rows, sort_keys=True) + "\n")


def main() -> int:
    with tempfile.TemporaryDirectory(
        prefix="hadronization_gate_b_submission_test_"
    ) as temporary:
        fixture = Path(temporary).resolve()
        prepare_checkout(fixture)
        test_home = fixture / "test_home"
        test_home.mkdir()
        with (fixture / ".git/info/exclude").open("a") as stream:
            stream.write(
                "test_home/\nfake_scheduler/\nsubmission_classads.json\n"
            )
        os.environ["HOME"] = str(test_home)
        os.environ["HADRONIZATION_SUBMISSION_REGISTRY_ROOT"] = str(
            test_home / "shared_submission_registry"
        )
        fake_scheduler = fixture / "fake_scheduler"
        fake_scheduler.mkdir()
        classad_fixture = fixture / "submission_classads.json"
        condor_q = fake_scheduler / "condor_q"
        condor_q.write_text(
            "#!/usr/bin/env python3\n"
            "import os\n"
            "print(open(os.environ['HF_TEST_CLASSADS_PATH']).read(), end='')\n"
        )
        condor_q.chmod(0o755)
        os.environ["HF_TEST_CLASSADS_PATH"] = str(classad_fixture)
        os.environ["PATH"] = (
            str(fake_scheduler)
            + os.pathsep
            + os.environ.get("PATH", "")
        )
        registry = (
            Path(os.environ["HADRONIZATION_SUBMISSION_REGISTRY_ROOT"])
            / hashlib.sha256(
                b"github.com/waxpardo/hadronization"
            ).hexdigest()
        )
        registry.mkdir(parents=True)
        baseline = registry / "reservation_baseline.json"
        baseline.write_text(
            json.dumps(
                {
                    "schema": "hf_submission_registry_baseline_v1",
                    "repository_identity":
                        "github.com/waxpardo/hadronization",
                    "reviewer": "Submission Contract Unit Test",
                    "historical_reservations": [],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n"
        )
        baseline.chmod(0o444)
        campaign = "HF_GATEB_submission_contract_test"
        run(
            sys.executable,
            str(GENERATOR),
            "--root",
            str(fixture),
            "--campaign",
            campaign,
            "--campaign-ordinal",
            "771",
            "--seed-base",
            "440000001",
        )
        campaign_dir = fixture / "campaigns" / campaign
        rows = [
            json.loads(line)
            for line in (
                campaign_dir / "candidate_manifest.jsonl"
            ).read_text().splitlines()
        ]
        row = rows[0]
        producer = fixture / "SimulationScripts/heavyflavourcorrelations_status"
        producer_sha = hashlib.sha256(producer.read_bytes()).hexdigest()

        authorization_arguments = [
            sys.executable,
            str(MANIFEST),
            "authorize",
            str(campaign_dir),
            campaign,
            row["tune"],
            str(row["logical_id"]),
            row["role"],
            str(row["attempt"]),
            str(row["seed"]),
            str(row["requested_successes"]),
            "--campaign-ordinal",
            str(row["campaign_ordinal"]),
            "--pthat-min-override",
            row["pthat_min_override"],
            "--multiplicity-audit-events",
            str(row["multiplicity_audit_events"]),
            "--repository-commit",
            row["repository_commit"],
            "--effective-card-sha256",
            row["effective_card_sha256"],
            "--producer-executable-sha256",
            producer_sha,
            "--checkout-root",
            str(fixture),
        ]
        fixture_spec = fixture / "config/pthat_sensitivity_v1.json"
        approved_spec = fixture_spec.read_bytes()
        fixture_spec.write_bytes(_pending_pthat_spec_bytes())
        pending_authorization = run(
            *authorization_arguments,
            expect=1,
        )
        assert (
            "pre-pilot scientific approval"
            in pending_authorization.stderr
        )
        fixture_spec.write_bytes(approved_spec)
        authorization = run(*authorization_arguments)
        assert "CAMPAIGN_ALLOCATION_AUTHORIZED" in authorization.stdout
        missing_claim = run(
            *authorization_arguments,
            "--require-submission-claim",
            expect=1,
        )
        assert "submission claim is absent" in missing_claim.stderr

        wrong_pthat = run(
            sys.executable,
            str(MANIFEST),
            "authorize",
            str(campaign_dir),
            campaign,
            row["tune"],
            str(row["logical_id"]),
            row["role"],
            str(row["attempt"]),
            str(row["seed"]),
            str(row["requested_successes"]),
            "--campaign-ordinal",
            str(row["campaign_ordinal"]),
            "--pthat-min-override",
            "2.0",
            "--multiplicity-audit-events",
            str(row["multiplicity_audit_events"]),
            "--repository-commit",
            row["repository_commit"],
            "--effective-card-sha256",
            row["effective_card_sha256"],
            "--producer-executable-sha256",
            producer_sha,
            "--checkout-root",
            str(fixture),
            expect=1,
        )
        assert "pTHat override differs" in wrong_pthat.stderr

        effective_card = fixture / "effective.cmnd"
        run(
            sys.executable,
            str(MANIFEST),
            "materialize-effective-card",
            str(
                fixture
                / "SimulationScripts"
                / "pythiasettings_Hard_Low_ccbb_MONASH.cmnd"
            ),
            str(effective_card),
            str(row["requested_successes"]),
            row["pthat_min_override"],
            row["effective_card_sha256"],
        )
        assert (
            hashlib.sha256(effective_card.read_bytes()).hexdigest()
            == row["effective_card_sha256"]
        )

        campaign_root = fixture / "Production" / campaign
        campaign_root.mkdir(parents=True)
        submit_file = campaign_root / "submit_gate_b.sub"
        run(
            sys.executable,
            str(RENDERER),
            str(campaign_dir),
            str(fixture),
            str(submit_file),
            "--roles",
            "pilot",
            "--producer-executable-sha256",
            producer_sha,
        )
        rendered = submit_file.read_text()
        assert "getenv = False" in rendered
        assert "getenv = True" not in rendered
        assert producer_sha in rendered
        assert row["effective_card_sha256"] in rendered

        claim = run(
            sys.executable,
            str(MANIFEST),
            "claim-submission",
            str(campaign_dir),
            "--checkout-root",
            str(fixture),
            "--production-root",
            str(fixture / "Production"),
            "--submit-file",
            str(submit_file),
            "--producer",
            str(producer),
            "--producer-executable-sha256",
            producer_sha,
            "--submission-kind",
            "gate_b",
        )
        claim_path = Path(claim.stdout.strip())
        assert claim_path.is_file()
        unrecorded_authorization = run(
            *authorization_arguments,
            "--require-submission-claim",
            "--cluster-id",
            "12345",
            "--process-id",
            "0",
            expect=1,
        )
        assert "submission record is absent" in unrecorded_authorization.stderr
        write_submission_classads(
            classad_fixture, claim_path, fixture, 12345
        )
        submitted = run(
            sys.executable,
            str(MANIFEST),
            "record-submission",
            str(claim_path),
            "12345.0 - 12345.8",
            "--checkout-root",
            str(fixture),
        )
        submitted_record = json.loads(Path(submitted.stdout.strip()).read_text())
        assert submitted_record["state"] == "condor_submit_succeeded"
        campaign_config = json.loads(
            (campaign_dir / "campaign.json").read_text()
        )
        _, _, gate_b_submission = gate_b.validate_submission(
            campaign_dir,
            campaign_root,
            campaign_config,
            rows,
        )
        assert (
            gate_b_submission["classad_evidence_sha256"]
            == submitted_record["classad_evidence_sha256"]
        )
        claimed_authorization = run(
            *authorization_arguments,
            "--require-submission-claim",
            "--cluster-id",
            "12345",
            "--process-id",
            "0",
        )
        assert "CAMPAIGN_ALLOCATION_AUTHORIZED" in claimed_authorization.stdout
        duplicate = run(
            sys.executable,
            str(MANIFEST),
            "claim-submission",
            str(campaign_dir),
            "--checkout-root",
            str(fixture),
            "--production-root",
            str(fixture / "Production"),
            "--submit-file",
            str(submit_file),
            "--producer",
            str(producer),
            "--producer-executable-sha256",
            producer_sha,
            "--submission-kind",
            "gate_b",
            expect=1,
        )
        assert "already claimed" in duplicate.stderr

        run("git", "add", "campaigns", cwd=fixture)
        run("git", "commit", "-q", "-m", "archive first campaign", cwd=fixture)
        second_checkout = fixture / "second_checkout"
        run("git", "clone", "-q", str(fixture), str(second_checkout))
        run(
            "git",
            "remote",
            "set-url",
            "origin",
            "https://github.com/Waxpardo/Hadronization.git",
            cwd=second_checkout,
        )
        second_campaign = "HF_GATEB_seed_reuse_test"
        run(
            sys.executable,
            str(GENERATOR),
            "--root",
            str(second_checkout),
            "--campaign",
            second_campaign,
            "--campaign-ordinal",
            "772",
            "--seed-base",
            "440000001",
        )
        second_dir = second_checkout / "campaigns" / second_campaign
        second_root = second_checkout / "Production" / second_campaign
        second_root.mkdir(parents=True)
        second_submit = second_root / "submit_gate_b.sub"
        run(
            sys.executable,
            str(RENDERER),
            str(second_dir),
            str(second_checkout),
            str(second_submit),
            "--roles",
            "pilot",
            "--producer-executable-sha256",
            producer_sha,
        )
        seed_reuse = run(
            sys.executable,
            str(MANIFEST),
            "claim-submission",
            str(second_dir),
            "--checkout-root",
            str(second_checkout),
            "--production-root",
            str(second_checkout / "Production"),
            "--submit-file",
            str(second_submit),
            "--producer",
            str(
                second_checkout
                / "SimulationScripts"
                / "heavyflavourcorrelations_status"
            ),
            "--producer-executable-sha256",
            producer_sha,
            "--submission-kind",
            "gate_b",
            expect=1,
        )
        assert "seed reuse blocked" in seed_reuse.stderr

        payload = fixture / "portable.root"
        payload.write_bytes(b"ROOT fixture\n")
        run(
            sys.executable,
            str(MANIFEST),
            "write-checksum-sidecar",
            str(payload),
        )
        sidecar = Path(f"{payload}.sha256")
        expected = hashlib.sha256(payload.read_bytes()).hexdigest()
        assert sidecar.read_text() == f"{expected}  {payload.name}\n"
        assert str(payload.parent) not in sidecar.read_text()
        promotion_source = fixture / "validated.partial.root"
        promotion_target = fixture / "published.root"
        promotion_source.write_bytes(b"validated bytes\n")
        run(
            sys.executable,
            str(MANIFEST),
            "promote-output",
            str(promotion_source),
            str(promotion_target),
        )
        assert not promotion_source.exists()
        assert promotion_target.read_bytes() == b"validated bytes\n"
        competing_source = fixture / "competing.partial.root"
        competing_source.write_bytes(b"different bytes\n")
        collision = run(
            sys.executable,
            str(MANIFEST),
            "promote-output",
            str(competing_source),
            str(promotion_target),
            expect=1,
        )
        assert "destination already exists" in collision.stderr
        assert competing_source.read_bytes() == b"different bytes\n"
        assert promotion_target.read_bytes() == b"validated bytes\n"

    controlled_environment = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("HADRONIZATION_")
    }
    controlled_environment["HADRONIZATION_FORCE_FAILURES"] = "1"
    rejected = subprocess.run(
        [
            str(ROOT / "runCondorJob.sh"),
            "--campaign",
            "environment_rejection_test",
            "1",
            "MONASH",
            "0",
            "pilot",
            "0",
            "123",
            "10",
            "1.0",
            "10",
            "0" * 40,
            "0" * 64,
            "0" * 64,
            "12345",
            "0",
        ],
        text=True,
        capture_output=True,
        env=controlled_environment,
        check=False,
    )
    assert rejected.returncode == 3
    assert "forbidden inherited campaign control" in rejected.stderr

    print("Gate-B submission-contract tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
