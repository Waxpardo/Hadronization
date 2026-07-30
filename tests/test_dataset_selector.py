#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/dataset_selector.py"
SELECTOR = ROOT / "config/dataset_selector.json"


def main() -> int:
    result = subprocess.run(
        [sys.executable, str(TOOL), "validate", "--selector", str(SELECTOR)],
        check=True,
        text=True,
        capture_output=True,
    )
    assert "active=legacy_21_06_2026" in result.stdout
    shell = subprocess.run(
        [sys.executable, str(TOOL), "shell", "--selector", str(SELECTOR)],
        check=True,
        text=True,
        capture_output=True,
    ).stdout
    assert "HADRONIZATION_COMPLETE_ROOT_TAG=complete_root_21_06_2026" in shell
    assert "HADRONIZATION_SUBSAMPLE_BASE=" in shell

    payload = json.loads(SELECTOR.read_text())
    payload["datasets"]["bad"] = {
        **payload["datasets"]["legacy_21_06_2026"],
        "status": "canonical",
        "campaign": None,
    }
    payload["active_dataset"] = "bad"
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "bad.json"
        path.write_text(json.dumps(payload))
        failed = subprocess.run(
            [sys.executable, str(TOOL), "validate", "--selector", str(path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        assert failed.returncode != 0
    print("dataset-selector tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
