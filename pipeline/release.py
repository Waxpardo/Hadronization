"""Assemble and verify one exact portable numerical/figure file set."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

from pipeline.query.run import publish_directory

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "hadronization_portable_collaboration_package_v1"


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_pinned(path, expected):
    if sha(path) != expected:
        raise ValueError("package input manifest differs from independent pin")
    return json.loads(path.read_text(encoding="utf-8"))


def fact(path):
    if not path.is_file() or path.is_symlink():
        raise ValueError("package artifact is not a regular file: " + str(path))
    return {"bytes": path.stat().st_size, "sha256": sha(path)}


def config_locator(path):
    name = path.name
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*\.json", name):
        raise ValueError("selected plot config has an unsafe package name")
    return "config/" + name


def file_map(numerical, figures, numerical_manifest, figures_manifest,
             plot_config=None, plot_config_name=None):
    plot_config = Path(plot_config) if plot_config is not None else ROOT / "config/plot.json"
    plot_config_name = plot_config_name or config_locator(plot_config)
    if plot_config_name != config_locator(plot_config):
        raise ValueError("selected plot config locator differs")
    if numerical_manifest.get("schema") != "hadronization_public_v4_portable_package_v1":
        raise ValueError("numerical package schema differs")
    if figures_manifest.get("schema") != "hadronization_cold_plot_render_v1":
        raise ValueError("figure package schema differs")
    if figures_manifest["numerics_root"]["sha256"] != numerical_manifest["root_sha256"]:
        raise ValueError("figures do not bind the numerical ROOT")
    report = json.loads((numerical / "report.json").read_text(encoding="utf-8"))
    if (figures_manifest["numerics_root"]["value_sha256"] !=
            report["root"]["value_sha256"]):
        raise ValueError("figures do not bind the numerical value digest")
    if fact(plot_config)["sha256"] != figures_manifest["plot_config_sha256"]:
        raise ValueError("selected plot configuration differs from figure manifest")
    source_hashes = figures_manifest.get("source_sha256")
    if (not isinstance(source_hashes, dict) or not source_hashes or
            any(Path(name).is_absolute() or ".." in Path(name).parts or
                not (ROOT / name).is_file() or sha(ROOT / name) != digest
                for name, digest in source_hashes.items())):
        raise ValueError("figure source differs from current package source")
    names = {"numerical/package-manifest.json": numerical / "package-manifest.json",
             "figures/manifest.json": figures / "manifest.json",
             plot_config_name: plot_config}
    for name in numerical_manifest["files"]:
        path = numerical / name
        if fact(path) != numerical_manifest["files"][name]:
            raise ValueError("numerical package source differs: " + name)
        names["numerical/" + name] = path
    for item in figures_manifest["files"]:
        path = figures / item["name"]
        if fact(path) != {"bytes": item["bytes"], "sha256": item["sha256"]}:
            raise ValueError("figure package source differs: " + item["name"])
        names["figures/" + item["name"]] = path
    for relative, path in names.items():
        if (Path(relative).is_absolute() or ".." in Path(relative).parts or
                Path(relative).as_posix() != relative):
            raise ValueError("unsafe package locator")
        fact(path)
    return names


def verify(package, manifest_sha, work_dir):
    package = package.resolve(strict=True)
    if any(path.is_symlink() for path in package.rglob("*")):
        raise ValueError("collaboration package contains a symlink")
    manifest = read_pinned(package / "manifest.json", manifest_sha)
    if manifest.get("schema") != SCHEMA or not isinstance(manifest.get("files"), dict):
        raise ValueError("collaboration package schema differs")
    actual = {p.relative_to(package).as_posix() for p in package.rglob("*") if p.is_file()}
    if actual != set(manifest["files"]) | {"manifest.json"}:
        raise ValueError("collaboration package exact fileset differs")
    for name, expected in manifest["files"].items():
        if fact(package / name) != expected:
            raise ValueError("collaboration package artifact differs: " + name)
    numerical = package / "numerical"
    figures = package / "figures"
    numeric_manifest = read_pinned(numerical / "package-manifest.json",
                                   manifest["files"]["numerical/package-manifest.json"]["sha256"])
    figure_manifest = read_pinned(figures / "manifest.json",
                                  manifest["files"]["figures/manifest.json"]["sha256"])
    config = manifest.get("plot_config")
    if (not isinstance(config, dict) or set(config) != {"path", "sha256"} or
            not isinstance(config["path"], str) or
            config["path"] not in manifest["files"] or
            config["path"] != config_locator(Path(config["path"])) or
            config["sha256"] != manifest["files"][config["path"]]["sha256"]):
        raise ValueError("collaboration selected plot config locator/pin differs")
    selected_config = package / config["path"]
    expected_names = file_map(numerical, figures, numeric_manifest, figure_manifest,
                              selected_config, config["path"])
    if set(expected_names) != set(manifest["files"]):
        raise ValueError("collaboration manifest is not complete")
    commands = [
        [str(ROOT / "hadronization"), "reduce", "verify", "--mode", "portable",
         "--package-dir", str(numerical), "--package-manifest-sha",
         manifest["files"]["numerical/package-manifest.json"]["sha256"]],
        [str(ROOT / "hadronization"), "plot", "verify-render-cold",
         "--numerics-root", str(numerical / "numerics.root"),
         "--expected-root-sha256", figure_manifest["numerics_root"]["sha256"],
         "--expected-value-sha256", figure_manifest["numerics_root"]["value_sha256"],
         "--expected-manifest-sha256", manifest["files"]["figures/manifest.json"]["sha256"],
         "--plot-config", str(selected_config),
         "--work-dir", str(work_dir), "--output", str(figures)]
    ]
    for command in commands:
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode:
            raise ValueError("portable authority rejected package: " + result.stderr[-1000:])
    return {"schema": SCHEMA, "status": "PORTABLE_SCIENCE_AND_FIGURES_VERIFIED",
            "external_execution": "NOT_CHECKED_EXTERNAL",
            "file_count": len(manifest["files"]), "manifest_sha256": manifest_sha}


def build(numerical, numerical_sha, figures, figures_sha, output, plot_config=None):
    if output.exists():
        raise ValueError("collaboration package path already exists")
    numeric_manifest = read_pinned(numerical / "package-manifest.json", numerical_sha)
    figure_manifest = read_pinned(figures / "manifest.json", figures_sha)
    plot_config = Path(plot_config) if plot_config is not None else ROOT / "config/plot.json"
    locator = config_locator(plot_config)
    paths = file_map(numerical, figures, numeric_manifest, figure_manifest,
                     plot_config, locator)
    output.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="." + output.name + ".stage-", dir=output.parent))
    try:
        for name, source in paths.items():
            target = stage / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        files = {name: fact(stage / name) for name in sorted(paths)}
        (stage / "manifest.json").write_text(json.dumps({
            "schema": SCHEMA, "state": "EXACT_PORTABLE_FILESET",
            "numerical_manifest_sha256": numerical_sha,
            "figure_manifest_sha256": figures_sha,
            "plot_config": {"path": locator,
                            "sha256": files[locator]["sha256"]},
            "presentation_state": figure_manifest["presentation_state"],
            "files": files}, sort_keys=True, separators=(",", ":")) + "\n")
        publish_directory(stage, output)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return sha(output / "manifest.json")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    make = subs.add_parser("build")
    make.add_argument("--numerical", type=Path, required=True)
    make.add_argument("--numerical-manifest-sha256", required=True)
    make.add_argument("--figures", type=Path, required=True)
    make.add_argument("--figure-manifest-sha256", required=True)
    make.add_argument("--plot-config", type=Path,
                      help="exact config supplied to plot render-cold; defaults to config/plot.json")
    make.add_argument("--output", type=Path, required=True)
    check = subs.add_parser("verify")
    check.add_argument("--package", type=Path, required=True)
    check.add_argument("--manifest-sha256", required=True)
    check.add_argument("--work-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "build":
            digest = build(args.numerical, args.numerical_manifest_sha256,
                           args.figures, args.figure_manifest_sha256, args.output,
                           args.plot_config)
            print("COLLABORATION_PACKAGE={} SHA256={}".format(args.output, digest))
        else:
            print(json.dumps(verify(args.package, args.manifest_sha256, args.work_dir),
                             sort_keys=True))
    except (OSError, ValueError, KeyError, TypeError) as error:
        print("ERROR: " + str(error), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
