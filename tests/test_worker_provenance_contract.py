#!/usr/bin/env python3
"""End-to-end fake worker tests for immutable production provenance."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

from test_gate_b_submission_contract import (
    prepare_checkout,
    run,
    write_submission_classads,
)


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "tools/campaign_manifest.py"
GENERATOR = ROOT / "tools/generate_gate_b_pilots.py"
RENDERER = ROOT / "tools/render_production_submit.py"


def prepare_worker_checkout(checkout: Path) -> None:
    prepare_checkout(checkout)
    (checkout / "tools").mkdir(exist_ok=True)
    (checkout / "Validation").mkdir(exist_ok=True)
    (checkout / "AnalysisScripts").mkdir(exist_ok=True)
    shutil.copy2(MANIFEST, checkout / "tools/campaign_manifest.py")
    shutil.copy2(ROOT / "runCondorJob.sh", checkout / "runCondorJob.sh")
    (checkout / "setupEnv.sh").write_text("#!/bin/bash\n:\n")
    (checkout / "Validation/validate_raw_output.sh").write_text(
        """#!/bin/bash
set -euo pipefail
if grep -q '^INVALID' "$1"; then
  echo "RAW_VALIDATION_ERROR synthetic invalid output"
  exit 90
fi
echo "RAW_VALIDATION_SUMMARY errors=0 entries=1 successes=$5"
"""
    )
    (checkout / "Validation/ValidateRawOutput.C").write_text(
        "int ValidateRawOutput() { return 0; }\n"
    )
    for name in (
        "HeavyFlavourUtils.h",
        "GeneratedWeakParentRegistry.h",
        "GeneratedHeavyFlavourRegistry.h",
        "GeneratedTuneSettingRegistry.h",
        "Sha256.h",
    ):
        source = ROOT / "SimulationScripts" / name
        if source.exists():
            shutil.copy2(source, checkout / "SimulationScripts" / name)
        else:
            (checkout / "SimulationScripts" / name).write_text("#pragma once\n")
    pair_registry = ROOT / "AnalysisScripts/GeneratedPairRegistry.h"
    if pair_registry.exists():
        shutil.copy2(
            pair_registry,
            checkout / "AnalysisScripts/GeneratedPairRegistry.h",
        )
    else:
        (checkout / "AnalysisScripts/GeneratedPairRegistry.h").write_text(
            "#pragma once\n"
        )
    producer = checkout / "SimulationScripts/heavyflavourcorrelations_status"
    producer.write_text(
        """#!/bin/bash
set -euo pipefail
output="$2"
logical_id="$6"
if [[ "${logical_id}" == "1" ]]; then
  exit 9
fi
if [[ "${logical_id}" == "2" ]]; then
  printf 'INVALID\\n' > "${output}"
  exit 0
fi
printf 'VALID\\n' > "${output}"
"""
    )
    for executable in (
        checkout / "runCondorJob.sh",
        checkout / "setupEnv.sh",
        checkout / "Validation/validate_raw_output.sh",
        producer,
        checkout / "tools/campaign_manifest.py",
    ):
        executable.chmod(0o755)
    run(
        "git",
        "add",
        "runCondorJob.sh",
        "setupEnv.sh",
        "tools",
        "Validation",
        "AnalysisScripts",
        "SimulationScripts",
        cwd=checkout,
    )
    run("git", "commit", "-q", "-m", "fake worker runtime", cwd=checkout)


def worker_arguments(
    checkout: Path, campaign_dir: Path, row: dict, producer_sha: str,
    cluster: str, process: str,
) -> list[str]:
    return [
        str(checkout / "runCondorJob.sh"),
        "--campaign",
        row["campaign"],
        str(row["campaign_ordinal"]),
        row["tune"],
        str(row["logical_id"]),
        row["role"],
        str(row["attempt"]),
        str(row["seed"]),
        str(row["requested_successes"]),
        row["pthat_min_override"],
        str(row["multiplicity_audit_events"]),
        row["repository_commit"],
        row["effective_card_sha256"],
        producer_sha,
        cluster,
        process,
    ]


def main() -> int:
    with tempfile.TemporaryDirectory(
        prefix="hadronization_worker_contract_"
    ) as temporary:
        test_root = Path(temporary).resolve()
        checkout = test_root / "checkout"
        checkout.mkdir()
        prepare_worker_checkout(checkout)
        registry_root = test_root / "shared_registry"
        registry_root.mkdir()
        os.environ["HADRONIZATION_SUBMISSION_REGISTRY_ROOT"] = str(
            registry_root
        )
        identity = "github.com/waxpardo/hadronization"
        registry = registry_root / hashlib.sha256(identity.encode()).hexdigest()
        registry.mkdir(parents=True)
        baseline = registry / "reservation_baseline.json"
        baseline.write_text(
            json.dumps(
                {
                    "schema": "hf_submission_registry_baseline_v1",
                    "repository_identity": identity,
                    "reviewer": "Worker Contract Unit Test",
                    "historical_reservations": [],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n"
        )
        baseline.chmod(0o444)
        campaign = "HF_GATEB_worker_contract"
        run(
            sys.executable,
            str(GENERATOR),
            "--root",
            str(checkout),
            "--campaign",
            campaign,
            "--campaign-ordinal",
            "772",
            "--seed-base",
            "450000001",
        )
        campaign_dir = checkout / "campaigns" / campaign
        rows = [
            json.loads(line)
            for line in (
                campaign_dir / "candidate_manifest.jsonl"
            ).read_text().splitlines()
        ]
        producer = checkout / "SimulationScripts/heavyflavourcorrelations_status"
        producer_sha = hashlib.sha256(producer.read_bytes()).hexdigest()
        campaign_root = checkout / "Production" / campaign
        submit = campaign_root / "submit_gate_b.sub"
        run(
            sys.executable,
            str(RENDERER),
            str(campaign_dir),
            str(checkout),
            str(submit),
            "--roles",
            "pilot",
            "--producer-executable-sha256",
            producer_sha,
        )
        claim = run(
            sys.executable,
            str(MANIFEST),
            "claim-submission",
            str(campaign_dir),
            "--checkout-root",
            str(checkout),
            "--production-root",
            str(checkout / "Production"),
            "--submit-file",
            str(submit),
            "--producer",
            str(producer),
            "--producer-executable-sha256",
            producer_sha,
            "--submission-kind",
            "gate_b",
        )
        fake_scheduler = test_root / "fake_scheduler"
        fake_scheduler.mkdir()
        classad_fixture = test_root / "submission_classads.json"
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
        write_submission_classads(
            classad_fixture,
            Path(claim.stdout.strip()),
            checkout,
            11111,
        )
        run(
            sys.executable,
            str(MANIFEST),
            "record-submission",
            claim.stdout.strip(),
            "11111.0 - 11111.8",
            "--checkout-root",
            str(checkout),
        )

        success_row = next(
            row
            for row in rows
            if row["tune"] == "MONASH" and row["logical_id"] == 0
        )
        wrong_scheduler = run(
            *worker_arguments(
                checkout,
                campaign_dir,
                success_row,
                producer_sha,
                "20001",
                "0",
            ),
            expect=1,
        )
        assert "ClusterId differs" in wrong_scheduler.stderr
        success = run(
            *worker_arguments(
                checkout, campaign_dir, success_row, producer_sha, "11111", "0"
            )
        )
        assert "PROMOTED" in success.stdout
        attempt_metadata = (
            campaign_root
            / "attempt_metadata/MONASH/"
            "hf_MONASH_job000_attempt000_11111_0.json"
        )
        attempt_metadata_stat = attempt_metadata.stat()
        assert attempt_metadata_stat.st_mode & 0o777 == 0o444
        assert attempt_metadata_stat.st_nlink == 1
        stable = (
            campaign_root / "raw/MONASH/hf_MONASH_job000.root"
        )
        assert stable.read_bytes() == b"VALID\n"
        validation_receipt = (
            campaign_root
            / "raw_validation/MONASH/job_000/attempt_000/receipt.json"
        )
        assert json.loads(validation_receipt.read_text())["result"] == "PASS"
        attempt_metadata = (
            campaign_root
            / "attempt_metadata/MONASH/"
            "hf_MONASH_job000_attempt000_11111_0.json"
        )
        assert attempt_metadata.is_file()
        assert attempt_metadata.stat().st_nlink == 1
        assert attempt_metadata.stat().st_mode & 0o222 == 0
        idempotent = run(
            *worker_arguments(
                checkout, campaign_dir, success_row, producer_sha, "11111", "0"
            )
        )
        assert "VERIFIED_EXISTING_VALIDATED_OUTPUT" in idempotent.stdout

        producer_fail_row = next(
            row
            for row in rows
            if row["tune"] == "MONASH" and row["logical_id"] == 1
        )
        failed = run(
            *worker_arguments(
                checkout, campaign_dir, producer_fail_row, producer_sha,
                "11111", "1",
            ),
            expect=9,
        )
        assert "partial is not promoted" in failed.stderr
        assert not (
            campaign_root / "raw/MONASH/hf_MONASH_job001.root"
        ).exists()
        duplicate = run(
            *worker_arguments(
                checkout, campaign_dir, producer_fail_row, producer_sha,
                "11111", "1",
            ),
            expect=4,
        )
        assert "immutable attempt sidecar or partial already exists" in (
            duplicate.stderr
        )

        validator_fail_row = next(
            row
            for row in rows
            if row["tune"] == "MONASH" and row["logical_id"] == 2
        )
        validator_failed = run(
            *worker_arguments(
                checkout, campaign_dir, validator_fail_row, producer_sha,
                "11111", "2",
            ),
            expect=6,
        )
        assert "Immutable FAIL receipt" in validator_failed.stderr
        failed_receipt = (
            campaign_root
            / "raw_validation/MONASH/job_002/attempt_000/receipt.json"
        )
        assert json.loads(failed_receipt.read_text())["result"] == "FAIL"

        outside = test_root / "outside_symlink_target"
        outside.mkdir()
        symlink_parent = campaign_root / "raw/JUNCTIONS"
        symlink_parent.symlink_to(outside, target_is_directory=True)
        symlink_row = next(
            row
            for row in rows
            if row["tune"] == "JUNCTIONS" and row["logical_id"] == 0
        )
        symlink_rejected = run(
            *worker_arguments(
                checkout, campaign_dir, symlink_row, producer_sha, "11111", "3"
            ),
            expect=1,
        )
        assert (
            "not a real directory" in symlink_rejected.stderr
            or "outside campaign root" in symlink_rejected.stderr
        )
        assert list(outside.iterdir()) == []

        hardlink_row = next(
            row
            for row in rows
            if row["tune"] == "CLOSEPACKING" and row["logical_id"] == 0
        )
        hardlink_work = (
            campaign_root
            / "work/CLOSEPACKING/job_000/attempt_000/11111_6"
        )
        hardlink_work.mkdir(parents=True)
        os.link(
            producer,
            hardlink_work / "heavyflavourcorrelations_status",
        )
        hardlink_rejected = run(
            *worker_arguments(
                checkout, campaign_dir, hardlink_row, producer_sha, "11111", "6"
            ),
            expect=1,
        )
        assert "snapshot destination already exists" in hardlink_rejected.stderr
        assert not (
            campaign_root
            / "attempt_starts/CLOSEPACKING/job_000/attempt_000.json"
        ).exists()

    print("worker provenance-contract tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
