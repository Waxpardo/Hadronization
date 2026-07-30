#!/usr/bin/env python3
"""Render a deterministic Condor submit file from the candidate manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

from campaign_manifest import campaign_slot_contract, effective_card_sha256

TUNES = ("MONASH", "JUNCTIONS", "CLOSEPACKING")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
SAFE_TOKEN = re.compile(r"^[A-Za-z0-9._-]+$")


def reject_condor_unsafe_path(path: Path, label: str) -> None:
    if not re.fullmatch(r"[A-Za-z0-9_./:+-]+", str(path)):
        raise ValueError(f"{label} contains unsupported characters: {path}")


def write_once_or_identical(path: Path, content: str) -> None:
    """Never replace a submit artifact that may already be claimed/queued."""
    encoded = content.encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise ValueError(f"submit output may not be a symlink: {path}")
    if path.exists():
        if not path.is_file() or path.read_bytes() != encoded:
            raise ValueError(
                f"existing submit artifact differs; refusing overwrite: {path}"
            )
        return
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o444)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(encoded)
        stream.flush()
        os.fsync(stream.fileno())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("campaign_dir", type=Path)
    parser.add_argument("project_base", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument(
        "--roles", choices=("primary", "reserve", "pilot", "all"),
        default="primary"
    )
    parser.add_argument(
        "--producer-executable-sha256",
        help=(
            "SHA-256 frozen by the submission receipt; when omitted, hash the "
            "canonical built producer under project_base"
        ),
    )
    parser.add_argument("--retry-tune", choices=TUNES)
    parser.add_argument("--retry-logical-id", type=int)
    parser.add_argument("--retry-attempt", type=int)
    args = parser.parse_args()

    campaign_dir = args.campaign_dir.resolve()
    project_base = args.project_base.resolve()
    if args.output.is_symlink():
        raise ValueError("submit output may not be a symlink")
    output_path = args.output.resolve()
    reject_condor_unsafe_path(project_base, "project_base")
    reject_condor_unsafe_path(campaign_dir, "campaign_dir")
    reject_condor_unsafe_path(output_path, "output")
    campaign = json.loads((campaign_dir / "campaign.json").read_text())
    campaign_slots = None
    primary_limit = None
    if campaign.get("schema") == "hf_campaign_v1":
        campaign_slots, _, primary_limit = campaign_slot_contract(campaign)
    campaign_name = campaign.get("campaign")
    if (
        not isinstance(campaign_name, str)
        or not SAFE_TOKEN.fullmatch(campaign_name)
        or campaign_dir.name != campaign_name
    ):
        raise ValueError("campaign name and campaign-directory basename differ")
    campaign_ordinal = campaign.get("campaign_ordinal")
    if (
        isinstance(campaign_ordinal, bool)
        or not isinstance(campaign_ordinal, int)
        or not 1 <= campaign_ordinal <= 65_535
    ):
        raise ValueError("campaign_ordinal must be an integer in [1,65535]")
    all_rows = [
        json.loads(line)
        for line in (campaign_dir / "candidate_manifest.jsonl").read_text().splitlines()
        if line.strip()
    ]
    retry_values = (
        args.retry_tune,
        args.retry_logical_id,
        args.retry_attempt,
    )
    retry_mode = any(value is not None for value in retry_values)
    if retry_mode and not all(value is not None for value in retry_values):
        raise ValueError(
            "retry rendering requires tune, logical ID, and attempt together"
        )
    if retry_mode:
        if campaign.get("schema") != "hf_campaign_v1":
            raise ValueError("retry rendering requires a full campaign")
        if not 1 <= args.retry_attempt <= 4095:
            raise ValueError(
                "retry attempt must be in [1,4095] for the 12-bit event-ID field"
            )
        base_rows = [
            row
            for row in all_rows
            if row["tune"] == args.retry_tune
            and int(row["logical_id"]) == args.retry_logical_id
        ]
        if len(base_rows) != 1:
            raise ValueError("retry logical candidate is absent or duplicated")
        retry_ledger = [
            row
            for row in (
                json.loads(line)
                for line in (
                    campaign_dir / "seed_ledger.jsonl"
                ).read_text().splitlines()
                if line.strip()
            )
            if row["tune"] == args.retry_tune
            and int(row["logical_id"]) == args.retry_logical_id
            and int(row["attempt"]) == args.retry_attempt
            and row.get("allocation") == "retry"
        ]
        if len(retry_ledger) != 1:
            raise ValueError("retry allocation is absent or duplicated in ledger")
        retry_row = dict(base_rows[0])
        retry_row["attempt"] = int(retry_ledger[0]["attempt"])
        retry_row["seed"] = int(retry_ledger[0]["seed"])
        rows = [retry_row]
    else:
        rows = all_rows
        if args.roles != "all":
            rows = [row for row in rows if row["role"] == args.roles]
        if args.roles == "primary" and campaign_slots is not None:
            expected_primary = len(TUNES) * int(primary_limit)
            if len(rows) != expected_primary:
                raise ValueError(
                    f"expected {expected_primary} primary candidates, "
                    f"found {len(rows)}"
                )
        if args.roles == "all" and campaign_slots is not None:
            expected_all = sum(campaign_slots.values())
            if len(rows) != expected_all:
                raise ValueError(
                    f"expected {expected_all} declared candidates, "
                    f"found {len(rows)}"
                )
        if args.roles == "pilot":
            if campaign.get("schema") != "hf_gate_b_pilot_campaign_v1":
                raise ValueError("pilot rendering requires a Gate-B campaign manifest")
            if len(rows) != 9:
                raise ValueError(
                    f"expected nine Gate-B pilot rows, found {len(rows)}"
                )

    repository_commit = subprocess.check_output(
        ["git", "-C", str(project_base), "rev-parse", "HEAD"], text=True
    ).strip()
    if not re.fullmatch(r"[0-9a-f]{40}", repository_commit):
        raise ValueError("current checkout commit is not a lowercase 40-hex SHA")
    if campaign.get("schema") == "hf_gate_b_pilot_campaign_v1":
        manifest_commit = campaign.get(
            "repository_commit", campaign.get("repository_implementation_commit")
        )
        if manifest_commit != repository_commit:
            raise ValueError("Gate-B manifest commit differs from render checkout")

    producer = project_base / "SimulationScripts/heavyflavourcorrelations_status"
    producer_sha = args.producer_executable_sha256
    if producer_sha is None:
        if not producer.is_file():
            raise ValueError(f"canonical producer is missing: {producer}")
        producer_sha = hashlib.sha256(producer.read_bytes()).hexdigest()
    if not SHA256.fullmatch(producer_sha):
        raise ValueError("producer executable SHA-256 must be 64 lowercase hex")
    if producer.is_file():
        actual_producer_sha = hashlib.sha256(producer.read_bytes()).hexdigest()
        if actual_producer_sha != producer_sha:
            raise ValueError("producer checksum differs from requested render binding")

    lines = [
        "universe = vanilla",
        f"executable = {project_base}/runCondorJob.sh",
        f"initialdir = {project_base}",
        "getenv = False",
        "request_cpus = 1",
        "request_memory = 4GB",
        "request_disk = 4GB",
        '+UseOS = "el9"',
        '+JobCategory = "$(CATEGORY)"',
        f"log = {project_base}/Production/{campaign['campaign']}/condor_logs/$(TUNE)/job_$(LOGICAL_ID)_$(Cluster)_$(Process).log",
        f"output = {project_base}/Production/{campaign['campaign']}/condor_logs/$(TUNE)/job_$(LOGICAL_ID)_$(Cluster)_$(Process).out",
        f"error = {project_base}/Production/{campaign['campaign']}/condor_logs/$(TUNE)/job_$(LOGICAL_ID)_$(Cluster)_$(Process).err",
        "should_transfer_files = NO",
        "hold = True",
        "max_retries = 0",
        "on_exit_hold = (ExitBySignal == True) || (ExitCode != 0)",
        '+HFCampaign = "$(CAMPAIGN)"',
        "+HFCampaignOrdinal = $(CAMPAIGN_ORDINAL)",
        '+HFTune = "$(TUNE)"',
        "+HFLogicalId = $(LOGICAL_ID)",
        '+HFRole = "$(ROLE)"',
        "+HFAttempt = $(ATTEMPT)",
        "+HFSeed = $(SEED)",
        "+HFRequestedSuccesses = $(REQUESTED_SUCCESSES)",
        '+HFPTHat = "$(PTHAT)"',
        "+HFMultiplicityAuditEvents = $(MULT_AUDIT_EVENTS)",
        '+HFRepositoryCommit = "$(REPOSITORY_COMMIT)"',
        '+HFEffectiveCardSHA256 = "$(EFFECTIVE_CARD_SHA256)"',
        (
            '+HFProducerExecutableSHA256 = '
            '"$(PRODUCER_EXECUTABLE_SHA256)"'
        ),
        (
            "arguments = --campaign $(CAMPAIGN) $(CAMPAIGN_ORDINAL) "
            "$(TUNE) $(LOGICAL_ID) $(ROLE) $(ATTEMPT) $(SEED) "
            "$(REQUESTED_SUCCESSES) $(PTHAT) $(MULT_AUDIT_EVENTS) "
            "$(REPOSITORY_COMMIT) $(EFFECTIVE_CARD_SHA256) "
            "$(PRODUCER_EXECUTABLE_SHA256) $(Cluster) $(Process)"
        ),
        (
            "queue CAMPAIGN,CAMPAIGN_ORDINAL,TUNE,LOGICAL_ID,ROLE,ATTEMPT,"
            "SEED,REQUESTED_SUCCESSES,CATEGORY,PTHAT,MULT_AUDIT_EVENTS,"
            "REPOSITORY_COMMIT,EFFECTIVE_CARD_SHA256,"
            "PRODUCER_EXECUTABLE_SHA256 from ("
        ),
    ]
    for row in rows:
        if row.get("campaign") != campaign_name:
            raise ValueError("candidate campaign differs from campaign.json")
        row_ordinal = row.get("campaign_ordinal")
        if (
            isinstance(row_ordinal, bool)
            or not isinstance(row_ordinal, int)
            or row_ordinal != campaign_ordinal
        ):
            raise ValueError("candidate campaign ordinal differs from campaign.json")
        tune = row["tune"]
        if tune not in TUNES:
            raise ValueError(f"unsupported tune in candidate row: {tune}")
        integer_fields = {
            "logical_id": row.get("logical_id"),
            "attempt": row.get("attempt"),
            "seed": row.get("seed"),
            "requested_successes": row.get("requested_successes"),
        }
        for key, value in integer_fields.items():
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError(f"candidate {key} must be an integer")
        if (
            integer_fields["logical_id"] < 0
            or not 0 <= integer_fields["attempt"] <= 4095
            or not 1 <= integer_fields["seed"] <= 900_000_000
            or not 1 <= integer_fields["requested_successes"] <= 1_048_575
        ):
            raise ValueError("candidate numeric field is outside production bounds")
        pthat = str(row.get("pthat_min_override", "NONE"))
        if pthat in {"", "None"}:
            pthat = "NONE"
        if pthat not in {"NONE", "0.5", "1.0", "2.0"}:
            raise ValueError(f"unsupported pTHat override in candidate row: {pthat}")
        audit_events = int(row.get("multiplicity_audit_events", 0))
        if audit_events < 0 or audit_events > int(row["requested_successes"]):
            raise ValueError("invalid multiplicity_audit_events in candidate row")
        expected_card_sha = effective_card_sha256(
            project_base
            / "SimulationScripts"
            / f"pythiasettings_Hard_Low_ccbb_{tune}.cmnd",
            int(row["requested_successes"]),
            pthat,
        )
        if (
            campaign.get("schema") == "hf_gate_b_pilot_campaign_v1"
            and row.get("effective_card_sha256") != expected_card_sha
        ):
            raise ValueError(
                f"effective card checksum differs for {tune}/"
                f"{row['logical_id']}"
            )
        row_commit = row.get("repository_commit", repository_commit)
        if row_commit != repository_commit:
            raise ValueError("candidate repository commit differs from checkout")
        category = row.get(
            "category", "medium" if row["tune"] == "MONASH" else "long"
        )
        if category not in {"short", "medium", "long"}:
            raise ValueError(f"unsupported JobCategory {category!r}")
        lines.append(
            ",".join(
                [
                    campaign_name,
                    str(campaign_ordinal),
                    tune,
                    str(row["logical_id"]),
                    row["role"],
                    str(row["attempt"]),
                    str(row["seed"]),
                    str(row["requested_successes"]),
                    category,
                    pthat,
                    str(audit_events),
                    repository_commit,
                    expected_card_sha,
                    producer_sha,
                ]
            )
        )
    lines.append(")")
    write_once_or_identical(output_path, "\n".join(lines) + "\n")
    print(
        f"PRODUCTION_SUBMIT_RENDERED rows={len(rows)} "
        f"scope={'retry' if retry_mode else args.roles} "
        f"output={output_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
