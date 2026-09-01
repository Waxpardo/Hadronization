import csv
import hashlib
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
BASE_HEAD = "a2a2f6551d98b989ce67b75fce4bcf87e386ba0f"
TUNES = ("MONASH", "JUNCTIONS", "CLOSEPACKING")
TUNE_INDEX = {name: index for index, name in enumerate(TUNES)}


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(relative):
    with (ROOT / relative).open(encoding="utf-8") as handle:
        return json.load(handle)


def csv_rows(relative):
    with (ROOT / relative).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def git_blob(relative):
    return subprocess.check_output(
        ["git", "-C", str(ROOT), "show", "{}:{}".format(BASE_HEAD, relative)])


def parse_card(path):
    settings = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].split("!", 1)[0].strip()
        if "=" in line:
            key, value = line.split("=", 1)
            settings[key.strip()] = value.strip()
    return settings
