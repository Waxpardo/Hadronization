#!/usr/bin/env python3
"""Render a closed-environment, manifest-only canonical analysis submit file."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

TOOLS_DIRECTORY = str(Path(__file__).resolve().parent)
if TOOLS_DIRECTORY not in sys.path:
    sys.path.insert(0, TOOLS_DIRECTORY)
from validate_analysis_raw_receipt import validate_analysis_raw_receipt

TUNES = ("MONASH", "JUNCTIONS", "CLOSEPACKING")
ROW_SCHEMAS = {
    "hf_canonical_raw_manifest_v2",
    "hf_superseding_canonical_raw_manifest_v3",
}
HEX40 = re.compile(r"[0-9a-f]{40}")
HEX64 = re.compile(r"[0-9a-f]{64}")
SAFE_TOKEN = re.compile(r"[A-Za-z0-9._-]+")


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(16 * 1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def read_rows(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text().splitlines()
        if line.strip()
    ]


def require_path_token(path: Path, label: str) -> None:
    if any(character.isspace() for character in str(path)) or "," in str(path):
        raise ValueError(f"{label} contains whitespace or comma: {path}")


def validate_raw_receipt(
    production: Path, row: dict, raw: Path, raw_sha: str, index: int
) -> tuple[Path, str]:
    relative_value = row.get("raw_validation_receipt_path")
    expected_sha = row.get("raw_validation_receipt_sha256")
    log_relative_value = row.get("raw_validation_log_path")
    expected_log_sha = row.get("raw_validation_log_sha256")
    if (
        not isinstance(relative_value, str)
        or not isinstance(log_relative_value, str)
        or not isinstance(expected_sha, str)
        or not HEX64.fullmatch(expected_sha)
        or not isinstance(expected_log_sha, str)
        or not HEX64.fullmatch(expected_log_sha)
    ):
        raise ValueError(
            f"canonical raw-validation binding is invalid at row {index}"
        )
    relative = Path(relative_value)
    log_relative = Path(log_relative_value)
    if (
        relative.is_absolute()
        or ".." in relative.parts
        or log_relative.is_absolute()
        or ".." in log_relative.parts
    ):
        raise ValueError(
            f"canonical raw-validation path escapes production root "
            f"at row {index}"
        )
    receipt_source = production / relative
    log_source = production / log_relative
    receipt = receipt_source.resolve()
    log = log_source.resolve()
    if (
        receipt_source.is_symlink()
        or log_source.is_symlink()
        or not receipt.is_file()
        or not log.is_file()
        or receipt.parent != log.parent
        or sha256(receipt) != expected_sha
        or sha256(log) != expected_log_sha
    ):
        raise ValueError(
            f"canonical raw-validation evidence is absent or stale "
            f"at row {index}"
        )
    try:
        receipt.relative_to(production)
        log.relative_to(production)
    except ValueError as error:
        raise ValueError(
            f"canonical raw-validation evidence escapes production root "
            f"at row {index}"
        ) from error
    validate_analysis_raw_receipt(
        receipt,
        raw,
        raw_sha,
        expected_sha,
        str(row.get("campaign", "")),
        str(row.get("tune", "")),
        int(row.get("logical_id", -1)),
        expected_log=log,
        expected_log_sha256=expected_log_sha,
    )
    return receipt, expected_sha


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("canonical_manifest", type=Path)
    parser.add_argument("project_base", type=Path)
    parser.add_argument("production_root", type=Path)
    parser.add_argument("analysis_root", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    manifest = args.canonical_manifest.resolve()
    rows = read_rows(manifest)
    tune_counts = {
        tune: sum(row.get("tune") == tune for row in rows)
        for tune in TUNES
    }
    schemas = {row.get("schema") for row in rows}
    if (
        len(set(tune_counts.values())) != 1
        or not tune_counts
        or (jobs_per_tune := next(iter(tune_counts.values()))) < 100
        or jobs_per_tune % 10
        or len(rows) != len(TUNES) * jobs_per_tune
        or len(schemas) != 1
        or not schemas.issubset(ROW_SCHEMAS)
        or (
            schemas == {"hf_canonical_raw_manifest_v2"}
            and jobs_per_tune != 100
        )
    ):
        raise ValueError(
            "canonical analysis requires equal N>=100, N%10=0 tune "
            f"exposure; counts={tune_counts} rows={len(rows)}"
        )
    project = args.project_base.resolve()
    production = args.production_root.resolve()
    analysis = args.analysis_root.resolve()
    output = args.output.resolve()
    for name, path in {
        "project_base": project,
        "production_root": production,
        "analysis_root": analysis,
        "output": output,
    }.items():
        require_path_token(path, name)

    commit = subprocess.check_output(
        ["git", "-C", str(project), "rev-parse", "HEAD"], text=True
    ).strip()
    if not HEX40.fullmatch(commit):
        raise ValueError("analysis checkout commit is invalid")
    dirty = subprocess.check_output(
        [
            "git",
            "-C",
            str(project),
            "status",
            "--porcelain",
            "--untracked-files=no",
        ],
        text=True,
    ).strip()
    if dirty:
        raise ValueError("analysis submit rendering requires a tracked-clean checkout")
    macro = project / "AnalysisScripts/status_analysis_THnSparse_qq.C"
    worker = project / "run_status_analysis.sh"
    for path in (macro, worker):
        if not path.is_file():
            raise FileNotFoundError(f"analysis component is absent: {path}")
    macro_sha = sha256(macro)
    manifest_sha = sha256(manifest)

    identities: set[tuple[str, int]] = set()
    raw_paths: set[Path] = set()
    queue_rows: list[str] = []
    for index, row in enumerate(rows):
        tune_index, slot = divmod(index, jobs_per_tune)
        tune = TUNES[tune_index]
        identity = (tune, slot)
        if (
            row.get("schema") not in ROW_SCHEMAS
            or row.get("tune") != tune
            or row.get("canonical_slot") != slot
            or identity in identities
        ):
            raise ValueError(f"canonical identity/order differs at row {index}")
        identities.add(identity)
        campaign = row.get("campaign")
        logical_id = row.get("logical_id")
        raw_sha = row.get("raw_sha256")
        if (
            not isinstance(campaign, str)
            or not SAFE_TOKEN.fullmatch(campaign)
            or isinstance(logical_id, bool)
            or not isinstance(logical_id, int)
            or logical_id < 0
            or not isinstance(raw_sha, str)
            or not HEX64.fullmatch(raw_sha)
        ):
            raise ValueError(f"unsafe canonical fields at row {index}")
        raw_relative = Path(row["raw_path"])
        if raw_relative.is_absolute() or ".." in raw_relative.parts:
            raise ValueError(f"raw path escapes production root at row {index}")
        raw_source = production / raw_relative
        raw = raw_source.resolve()
        if row["schema"] == "hf_canonical_raw_manifest_v2":
            expected_relative = (
                Path("raw")
                / tune
                / f"hf_{tune}_job{logical_id:03d}.root"
            )
        else:
            source_prefix = row.get("source_production_prefix")
            if (
                not isinstance(source_prefix, str)
                or not SAFE_TOKEN.fullmatch(source_prefix)
                or source_prefix != campaign
            ):
                raise ValueError(
                    f"superseding source prefix differs at row {index}"
                )
            expected_relative = (
                Path(source_prefix)
                / "raw"
                / tune
                / f"hf_{tune}_job{logical_id:03d}.root"
            )
        expected_raw = (production / expected_relative).resolve()
        if raw != expected_raw or raw in raw_paths:
            raise ValueError(f"raw path identity differs at row {index}")
        raw_paths.add(raw)
        if (
            raw_source.is_symlink()
            or not raw.is_file()
            or sha256(raw) != raw_sha
        ):
            raise ValueError(f"raw input is absent or stale: {raw}")
        receipt, receipt_sha = validate_raw_receipt(
            production, row, raw, raw_sha, index
        )
        require_path_token(receipt, "raw_validation_receipt")
        destination = analysis / "per_job" / tune / f"slot_{slot:03d}"
        purpose = f"canonical_slot_{slot:03d}"
        queue_rows.append(
            ",".join(
                (
                    campaign,
                    tune,
                    str(slot),
                    str(logical_id),
                    str(raw),
                    raw_sha,
                    str(destination),
                    commit,
                    macro_sha,
                    purpose,
                    manifest_sha,
                    str(receipt),
                    receipt_sha,
                )
            )
        )

    lines = [
        "universe = vanilla",
        f"executable = {worker}",
        f"initialdir = {project}",
        "getenv = False",
        f'environment = "HADRONIZATION_BASE={project}"',
        "request_cpus = 1",
        "request_memory = 8GB",
        "request_disk = 8GB",
        '+UseOS = "el9"',
        '+JobCategory = "long"',
        (
            f"log = {analysis}/condor_logs/$(TUNE)/"
            "slot_$(CANONICAL_SLOT)_$(Cluster)_$(Process).log"
        ),
        (
            f"output = {analysis}/condor_logs/$(TUNE)/"
            "slot_$(CANONICAL_SLOT)_$(Cluster)_$(Process).out"
        ),
        (
            f"error = {analysis}/condor_logs/$(TUNE)/"
            "slot_$(CANONICAL_SLOT)_$(Cluster)_$(Process).err"
        ),
        "should_transfer_files = NO",
        "max_retries = 0",
        "on_exit_hold = (ExitBySignal == True) || (ExitCode != 0)",
        (
            "arguments = $(RAW_PATH) $(OUTPUT_DIRECTORY) $(CAMPAIGN) "
            "$(TUNE) $(LOGICAL_ID) $(RAW_SHA256) $(ANALYSIS_COMMIT) "
            "$(MACRO_SHA256) $(PURPOSE) $(MANIFEST_SHA256) "
            "$(RAW_VALIDATION_RECEIPT) "
            "$(RAW_VALIDATION_RECEIPT_SHA256)"
        ),
        (
            "queue CAMPAIGN,TUNE,CANONICAL_SLOT,LOGICAL_ID,RAW_PATH,"
            "RAW_SHA256,OUTPUT_DIRECTORY,ANALYSIS_COMMIT,MACRO_SHA256,"
            "PURPOSE,MANIFEST_SHA256,RAW_VALIDATION_RECEIPT,"
            "RAW_VALIDATION_RECEIPT_SHA256 from ("
        ),
        *queue_rows,
        ")",
        "",
    ]
    text = "\n".join(lines)
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        if output.read_text() != text:
            raise ValueError(f"refusing to overwrite stale submit file: {output}")
    else:
        output.write_text(text)
    print(
        "ANALYSIS_SUBMIT_RENDERED "
        f"rows={len(rows)} commit={commit} macro_sha256={macro_sha} "
        f"manifest_sha256={manifest_sha} output={output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
