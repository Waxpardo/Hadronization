#!/usr/bin/env python3
"""Build, plan, submit, or execute the nominal generation campaign."""

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
TUNE_MODES = {
    "MONASH": "monash",
    "JUNCTIONS": "junctions",
    "CLOSEPACKING": "closepacking",
}


def digest_bytes(value):
    return hashlib.sha256(value).hexdigest()


def digest_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def site_values(path):
    """Read the deliberately small KEY=VALUE site-file format."""
    values = {}
    if not path.is_file():
        return values
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        match = re.fullmatch(r"([A-Z][A-Z0-9_]*)=(.*)", line)
        if not match:
            raise ValueError("{}:{} is not KEY=VALUE".format(path, number))
        value = match.group(2).strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        values[match.group(1)] = value
    return values


def repository_path(value, default):
    path = Path(value) if value else default
    return path if path.is_absolute() else ROOT / path


def campaign_inputs():
    campaign = load_json(ROOT / "data/campaign.json")
    study = load_json(ROOT / "config/study.json")
    if study.get("schema") != "hadronization_study_v1":
        raise ValueError("unsupported study schema")
    scope = study.get("scope", {})
    if scope.get("variation_selection") is not False:
        raise ValueError("nominal study must make variation selection impossible")
    if scope.get("systematic_uncertainty") != "disabled_and_absent":
        raise ValueError("nominal study must exclude systematic uncertainty")
    if campaign.get("systematic_uncertainties") != "disabled":
        raise ValueError("campaign does not declare systematic uncertainty disabled")
    tune_rows = study.get("tunes", [])
    if [row.get("name") for row in tune_rows] != campaign.get("tune_order"):
        raise ValueError("study and campaign tune order differ")
    return campaign, study, tune_rows


def next_attempts():
    attempts = {}
    with (ROOT / "data/attempts.csv").open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            key = (row["tune"], int(row["logical_id"]))
            attempts[key] = max(attempts.get(key, -1), int(row["attempt"]))
    return {key: value + 1 for key, value in attempts.items()}


def seed_for(campaign, tune, logical_id, attempt):
    seed = campaign["seed"]
    value = (100000001 + int(seed["campaign_ordinal"]) * 10000000
             + int(seed["tune_ordinals"][tune]) * 1000000
             + attempt * 100000 + logical_id)
    low, high = seed["attempt_domain"]
    if not low <= attempt <= high or not 1 <= value <= 900000000:
        raise ValueError("derived attempt or seed is outside the campaign domain")
    return value


def materialized_card(card, events):
    text = card.read_text(encoding="utf-8")
    updated, count = re.subn(
        r"(?m)^(\s*Main:numberOfEvents\s*=\s*)[0-9]+(\s*)$",
        r"\g<1>{}\g<2>".format(events), text)
    if count != 1:
        raise ValueError("{} does not define Main:numberOfEvents exactly once".format(card))
    return updated.encode("utf-8")


def plan_rows(campaign, tune_rows):
    attempt_map = next_attempts()
    logical_jobs = int(campaign["logical_jobs_per_tune"])
    events = int(campaign["successful_events_per_logical_job"])
    rows = []
    for tune_row in tune_rows:
        tune = tune_row["name"]
        card = ROOT / tune_row["card"]
        if not card.is_file():
            raise ValueError("missing tune card: {}".format(card))
        card_sha = digest_file(card)
        effective_sha = digest_bytes(materialized_card(card, events))
        for logical_id in range(logical_jobs):
            attempt = attempt_map[(tune, logical_id)]
            rows.append({
                "tune": tune,
                "logical_id": logical_id,
                "attempt": attempt,
                "seed": seed_for(campaign, tune, logical_id, attempt),
                "block": logical_id % 10 + 1,
                "storage_key": "{}/hf_{}_job{:03d}.root".format(
                    tune, tune, logical_id),
                "card_sha256": card_sha,
                "effective_card_sha256": effective_sha,
            })
    return rows


def command_output(command):
    result = subprocess.run(command, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    if result.returncode:
        raise RuntimeError("{} failed: {}".format(command[0], result.stderr.strip()))
    return shlex.split(result.stdout.strip())


def build_producer(values, output, overrides):
    cxx = overrides.get("cxx") or values.get("CXX") or shutil.which("c++")
    root_config = (overrides.get("root_config") or values.get("ROOT_CONFIG")
                   or shutil.which("root-config"))
    pythia_config = (overrides.get("pythia8_config")
                     or values.get("PYTHIA8_CONFIG")
                     or shutil.which("pythia8-config"))
    pythia_prefix = overrides.get("pythia8_prefix") or values.get("PYTHIA8_PREFIX")
    if not cxx or not root_config or (not pythia_config and not pythia_prefix):
        raise RuntimeError(
            "generator build requires C++, root-config, and PYTHIA8_CONFIG or PYTHIA8_PREFIX")
    root_flags = command_output([root_config, "--cflags"])
    root_libdir = subprocess.check_output([root_config, "--libdir"], text=True).strip()
    root_aux = command_output([root_config, "--auxlibs"])
    if pythia_config:
        pythia_flags = command_output([pythia_config, "--cxxflags"])
        pythia_libs = command_output([pythia_config, "--libs"])
    else:
        prefix = Path(pythia_prefix)
        pythia_flags = ["-I" + str(prefix / "include")]
        pythia_libs = ["-L" + str(prefix / "lib"), "-lpythia8",
                       "-Wl,-rpath," + str(prefix / "lib")]
    output.parent.mkdir(parents=True, exist_ok=True)
    command = ([cxx, "-O2", "-std=c++17", "-Wall", "-Wextra", "-Wpedantic",
                "-Wconversion", "-Wshadow", str(ROOT / "pipeline/generate/producer.cpp"),
                "-I" + str(ROOT / "pipeline/generate")] + root_flags + pythia_flags
               + ["-L" + root_libdir, "-lTree", "-lHist", "-lRIO", "-lCore"]
               + root_aux + pythia_libs + ["-o", str(output)])
    result = subprocess.run(command)
    if result.returncode:
        raise RuntimeError("producer build failed with exit {}".format(result.returncode))
    return command


def render_submit(campaign, rows, values, producer, raw_root, work_root):
    commit = subprocess.check_output(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()
    producer_sha = digest_file(producer) if producer.is_file() else "UNBUILT"
    python = values.get("PYTHON") or sys.executable
    worker = ROOT / "pipeline/generate/submit.py"
    lines = [
        "# deterministic nominal generation plan",
        "# campaign={} study_sha256={}".format(
            campaign["campaign"], digest_file(ROOT / "config/study.json")),
        "universe = vanilla",
        "executable = {}".format(python),
        "arguments = {} worker --tune $(tune) --logical-id $(logical_id) --attempt $(attempt) --seed $(seed) --card-sha256 $(card_sha256) --effective-card-sha256 $(effective_card_sha256) --producer-sha256 {} --repository-commit {} --raw-root {} --work-root {}".format(
            worker, producer_sha, commit, raw_root, work_root),
        "getenv = False",
        "log = {}/condor/$(tune)-$(logical_id)-$(attempt).log".format(work_root),
        "output = {}/condor/$(tune)-$(logical_id)-$(attempt).out".format(work_root),
        "error = {}/condor/$(tune)-$(logical_id)-$(attempt).err".format(work_root),
        "request_cpus = 1",
        "queue tune,logical_id,attempt,seed,block,storage_key,card_sha256,effective_card_sha256 from (",
    ]
    for row in rows:
        lines.append("{tune} {logical_id} {attempt} {seed} {block} {storage_key} {card_sha256} {effective_card_sha256}".format(**row))
    lines.extend([")", ""])
    return "\n".join(lines).encode("utf-8")


def validate_root_file(root_command, path, events):
    code = (
        'TFile f("{}","READ"); auto t=(TTree*)f.Get("tree"); '
        'auto m=(TTree*)f.Get("job_metadata"); '
        'int rc=(f.IsZombie()||!t||!m||t->GetEntries()!={}||m->GetEntries()!=1); '
        'gSystem->Exit(rc);'.format(str(path).replace('"', '\\"'), events))
    result = subprocess.run([root_command, "-l", "-b", "-q", "-e", code])
    if result.returncode:
        raise RuntimeError("ROOT validation rejected {}".format(path))


def worker(args):
    campaign, study, tune_rows = campaign_inputs()
    tune_map = {row["name"]: row for row in tune_rows}
    if args.tune not in tune_map or args.logical_id < 0:
        raise ValueError("invalid tune or logical id")
    if args.logical_id >= int(campaign["logical_jobs_per_tune"]):
        raise ValueError("logical id outside campaign")
    if seed_for(campaign, args.tune, args.logical_id, args.attempt) != args.seed:
        raise ValueError("seed does not match the campaign formula")
    actual_commit = subprocess.check_output(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()
    if actual_commit != args.repository_commit:
        raise RuntimeError("checkout moved after the plan was rendered")
    if subprocess.check_output(["git", "-C", str(ROOT), "status", "--porcelain"], text=True):
        raise RuntimeError("worker refuses a checkout with tracked or untracked changes")
    values = site_values(ROOT / "config/site.conf")
    producer = repository_path(values.get("PRODUCER"), ROOT / "data/work/bin/producer")
    if not producer.is_file() or digest_file(producer) != args.producer_sha256:
        raise RuntimeError("producer executable digest mismatch")
    card = ROOT / tune_map[args.tune]["card"]
    if digest_file(card) != args.card_sha256:
        raise RuntimeError("tune-card digest mismatch")
    effective = materialized_card(card, int(campaign["successful_events_per_logical_job"]))
    if digest_bytes(effective) != args.effective_card_sha256:
        raise RuntimeError("materialized tune-card digest mismatch")
    raw_root = Path(args.raw_root).resolve()
    work_root = Path(args.work_root).resolve()
    stable = raw_root / args.tune / "hf_{}_job{:03d}.root".format(
        args.tune, args.logical_id)
    if stable.exists():
        raise RuntimeError("stable output already exists; refusing overwrite: {}".format(stable))
    work = work_root / args.tune / "job{:03d}".format(args.logical_id) / "attempt{:02d}".format(args.attempt)
    work.mkdir(parents=True, mode=0o700, exist_ok=False)
    partial = work / "partial.root"
    (work / Path(tune_map[args.tune]["card"]).name).write_bytes(effective)
    env = os.environ.copy()
    for key in list(env):
        if key == "HADRONIZATION_DATASET" or key.startswith("HADRONIZATION_"):
            env.pop(key, None)
    env.update({
        "HADRONIZATION_CONFIG_SHA256": args.effective_card_sha256,
        "HADRONIZATION_EXECUTABLE_SHA256": args.producer_sha256,
        "HADRONIZATION_REPOSITORY_COMMIT": args.repository_commit,
        "HADRONIZATION_REPOSITORY_DIRTY": "false",
    })
    command = [str(producer), TUNE_MODES[args.tune], str(partial), str(args.seed),
               campaign["campaign"], str(campaign["seed"]["campaign_ordinal"]),
               str(args.logical_id), "primary", str(args.attempt)]
    result = subprocess.run(command, cwd=str(work), env=env)
    if result.returncode:
        raise RuntimeError("producer exited {}; partial not promoted".format(result.returncode))
    root_command = values.get("ROOT") or shutil.which("root")
    if not root_command:
        raise RuntimeError("ROOT is required to validate before promotion")
    validate_root_file(root_command, partial,
                       int(campaign["successful_events_per_logical_job"]))
    output_sha = digest_file(partial)
    stable.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.link(str(partial), str(stable))
    except OSError as error:
        raise RuntimeError("atomic no-overwrite promotion failed: {}".format(error))
    if digest_file(stable) != output_sha:
        raise RuntimeError("promoted output digest changed")
    receipt = {
        "schema": "hf_raw_validation_receipt_v4",
        "state": "PASS",
        "campaign": campaign["campaign"],
        "tune": args.tune,
        "logical_id": args.logical_id,
        "attempt": args.attempt,
        "seed": args.seed,
        "successful_events": int(campaign["successful_events_per_logical_job"]),
        "card_sha256": args.card_sha256,
        "effective_card_sha256": args.effective_card_sha256,
        "producer_sha256": args.producer_sha256,
        "repository_commit": args.repository_commit,
        "output_bytes": stable.stat().st_size,
        "output_sha256": output_sha,
    }
    receipt_path = stable.with_suffix(".receipt.json")
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n",
                            encoding="utf-8")
    partial.unlink()
    shutil.rmtree(str(work))
    print("PROMOTED {}".format(stable))


def parser():
    top = argparse.ArgumentParser(description=__doc__)
    sub = top.add_subparsers(dest="command", required=True)
    plan = sub.add_parser("plan")
    plan.add_argument("--output", type=Path)
    plan.add_argument("--submit", action="store_true")
    plan.add_argument("--build", action="store_true")
    plan.add_argument("--producer", type=Path)
    plan.add_argument("--raw-root", type=Path)
    plan.add_argument("--work-root", type=Path)
    plan.add_argument("--cxx")
    plan.add_argument("--root-config")
    plan.add_argument("--pythia8-config")
    plan.add_argument("--pythia8-prefix")
    build = sub.add_parser("build")
    build.add_argument("--output", type=Path)
    build.add_argument("--cxx")
    build.add_argument("--root-config")
    build.add_argument("--pythia8-config")
    build.add_argument("--pythia8-prefix")
    run = sub.add_parser("worker")
    run.add_argument("--tune", required=True)
    run.add_argument("--logical-id", type=int, required=True)
    run.add_argument("--attempt", type=int, required=True)
    run.add_argument("--seed", type=int, required=True)
    run.add_argument("--card-sha256", required=True)
    run.add_argument("--effective-card-sha256", required=True)
    run.add_argument("--producer-sha256", required=True)
    run.add_argument("--repository-commit", required=True)
    run.add_argument("--raw-root", required=True)
    run.add_argument("--work-root", required=True)
    return top


def main():
    args = parser().parse_args()
    try:
        values = site_values(ROOT / "config/site.conf")
        if args.command == "worker":
            worker(args)
            return 0
        work_root = repository_path(values.get("WORK_ROOT"), ROOT / "data/work")
        output = (args.output if getattr(args, "output", None)
                  else work_root / "bin/producer")
        overrides = {name: getattr(args, name, None) for name in
                     ("cxx", "root_config", "pythia8_config", "pythia8_prefix")}
        if args.command == "build":
            command = build_producer(values, output, overrides)
            print("BUILT {}".format(output))
            print("BUILD_COMMAND {}".format(" ".join(shlex.quote(x) for x in command)))
            return 0
        campaign, study, tune_rows = campaign_inputs()
        if args.submit and not (ROOT / "config/site.conf").is_file():
            raise RuntimeError("--submit requires configured config/site.conf")
        raw_root = (args.raw_root or repository_path(values.get("RAW_ROOT"), ROOT / "data/raw")).resolve()
        work_root = (args.work_root or work_root).resolve()
        producer = (args.producer or repository_path(values.get("PRODUCER"), work_root / "bin/producer")).resolve()
        if args.build or (args.submit and not producer.is_file()):
            build_producer(values, producer, overrides)
        rows = plan_rows(campaign, tune_rows)
        rendered = render_submit(campaign, rows, values, producer, raw_root, work_root)
        plan_sha = digest_bytes(rendered)
        destination = args.output
        if args.submit and destination is None:
            destination = work_root / "generate.sub"
        if destination is not None:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(rendered)
        print("PLAN campaign={} jobs={} raw_root={} work_root={}".format(
            campaign["campaign"], len(rows), raw_root, work_root))
        print("PLAN_SHA256={}".format(plan_sha))
        if destination is not None:
            print("PLAN_FILE={}".format(destination))
        if args.submit:
            submit_command = values.get("SCHEDULER_SUBMIT")
            if not submit_command:
                raise RuntimeError("--submit requires SCHEDULER_SUBMIT in config/site.conf")
            if not producer.is_file() or "UNBUILT" in rendered.decode("utf-8", errors="ignore"):
                raise RuntimeError("--submit requires a built producer")
            result = subprocess.run(shlex.split(submit_command) + [str(destination)])
            if result.returncode:
                raise RuntimeError("scheduler submit exited {}".format(result.returncode))
        return 0
    except (KeyError, OSError, RuntimeError, ValueError) as error:
        print("ERROR: {}".format(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
