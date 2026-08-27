#!/usr/bin/env python3
"""The CLI surface derives, refuses, or names. It never guesses.

WHY THIS FILE EXISTS. The HF_SMOKE3 campaign was the first run to build its own
raw files from the clean repository, so it was the first run to reach several
`./hadronization` surfaces at all. It found a family of defects with one shape:
a surface that guessed a path, took a silent default, or refused while naming
the wrong thing. Each check below drives the real CLI in a sandbox checkout and
requires the derivation, the refusal, or the name.

THE SANDBOX. Every entry symlinks to this checkout except `setupEnv.sh`, which
stands in for the site and dependency planes, and whatever one file the case is
about. That keeps each case fast, identical on every host, and unable to write
into this working tree. `tools/run_tests.sh` fails the whole suite if a test
mutates the resolved `plotting/Plots`, which is the reason the plot cases below
build their own `plotting/` rather than symlinking this one.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UNIFIED_CLI = ROOT / "hadronization"
TUNES = ("MONASH", "JUNCTIONS", "CLOSEPACKING")
SMOKE_SELECTOR = ROOT / "config/dataset_selector_hf_smoke3.json"

_STUB_SETUP_ENV = """# Sandbox stand-in for setupEnv.sh.
export HADRONIZATION_SITE=local
export HADRONIZATION_DATA_ROOT="${HADRONIZATION_DATA_ROOT:?}"
export HADRONIZATION_RESULTS_ROOT="${HADRONIZATION_DATA_ROOT}/project/results"
export HADRONIZATION_ANALYSIS_ROOT="${HADRONIZATION_DATA_ROOT}/hadronization_analysis"
export HADRONIZATION_MERGED_ROOT="${HADRONIZATION_DATA_ROOT}/hadronization_merged"
export HADRONIZATION_SYSTEMATICS_ROOT="${HADRONIZATION_DATA_ROOT}/systematics_harvest"
export HF_PRODUCTION_ROOT="${HADRONIZATION_DATA_ROOT}/hadronization_production"
"""

failures: list[str] = []


def check(label: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"  PASS {label}")
    else:
        print(f"  FAIL {label} {detail}")
        failures.append(label)


def sandbox(tmp: str, cli_text: str | None = None,
            replace: dict | None = None, git: bool = False) -> Path:
    """A checkout that differs from this one only where the case requires."""
    base = Path(tmp) / "checkout"
    base.mkdir()
    replace = replace or {}
    tops = {rel.split("/")[0] for rel in replace}
    for entry in sorted(ROOT.iterdir()):
        if entry.name not in ({".git", "setupEnv.sh", "hadronization"} | tops):
            (base / entry.name).symlink_to(entry)
    for top in sorted(tops):
        (base / top).mkdir(exist_ok=True)
        dropped = {rel.split("/", 1)[1] for rel in replace
                   if rel.startswith(top + "/") and replace[rel] is None}
        for entry in sorted((ROOT / top).iterdir()):
            if entry.name not in dropped:
                (base / top / entry.name).symlink_to(entry)
    for rel, text in replace.items():
        if text is None:
            continue
        target = base / rel
        if target.is_symlink():
            target.unlink()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)
        target.chmod(0o755)
    (base / "setupEnv.sh").write_text(_STUB_SETUP_ENV)
    cli = base / "hadronization"
    cli.write_text(cli_text if cli_text is not None
                   else UNIFIED_CLI.read_text())
    cli.chmod(0o755)
    if git:
        # The plot planes read the commit. Never the real repository: a test
        # must not be able to write into it.
        for command in (["init", "-q"],
                        ["-c", "user.name=t", "-c", "user.email=t@t",
                         "commit", "-q", "--allow-empty", "-m", "sandbox"]):
            subprocess.run(["git", "-C", str(base), *command], check=True,
                           capture_output=True)
    return base


def raw_fixture(data: Path, campaign: str, jobs: int = 10) -> Path:
    """A promoted raw tree with the sidecars and metadata the freeze reads."""
    campaign_root = data / "hadronization_production" / campaign
    for tune in TUNES:
        (campaign_root / "raw" / tune).mkdir(parents=True, exist_ok=True)
        (campaign_root / "attempt_metadata" / tune).mkdir(
            parents=True, exist_ok=True)
        for job in range(jobs):
            path = campaign_root / "raw" / tune / f"hf_{tune}_job{job:03d}.root"
            path.write_bytes(f"{campaign}/{tune}/{job}".encode())
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            path.with_suffix(path.suffix + ".sha256").write_text(
                f"{digest}  {path.name}\n")
            # requested_successes and seed come from the promoted attempt's
            # metadata; a row without it is refused as incomplete.
            (campaign_root / "attempt_metadata" / tune
             / f"{tune}_job{job:03d}_attempt000.json").write_text(json.dumps({
                 "tune": tune, "logical_id": job, "attempt": 0,
                 "producer_exit": 0, "requested_successes": 20000,
                 "seed": 100000001 + job, "campaign_ordinal": 11,
                 "role": "primary", "effective_card_sha256": "0" * 64,
                 "producer_executable_sha256": "1" * 64,
                 "repository_commit": "2" * 40,
                 "multiplicity_audit_events": 0, "pthat_min_override": "2.0",
             }))
    return campaign_root


def run_cli(base: Path, data: Path, args: list[str],
            env_extra: dict | None = None) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env.update(HADRONIZATION_DATA_ROOT=str(data),
               HADRONIZATION_DATASET_SELECTOR=str(SMOKE_SELECTOR))
    for name in ("HADRONIZATION_BASE", "THNSPARSE_COMPLETE_ROOT_CONFIG",
                 "THNSPARSE_CONFIG", "MULTIPLICITY_CONFIG",
                 "HADRONIZATION_MEASUREMENT_CONFIG",
                 "HADRONIZATION_MEASUREMENT_ROOT"):
        env.pop(name, None)
    env.update(env_extra or {})
    return subprocess.run(["bash", str(base / "hadronization"), *args],
                          env=env, text=True, capture_output=True)


# --- Phase 1: the freeze root ---------------------------------------------
#
# THE DEFECT THIS CLOSES. `hadronization:192` passed the selector's
# campaign-scoped HADRONIZATION_PRODUCTION_ROOT to
# tools/build_canonical_manifest.py, whose line 87 joins the campaign on again.
# `./hadronization freeze hf_smoke3` refused with
# `no raw directory: .../HF_SMOKE3/HF_SMOKE3/raw`. Every run before HF_SMOKE3
# reused a pre-rebuild manifest, so no run had reached this surface.
#
# The tool keeps re-joining and the CLI passes the base root, because the tool
# is the side with other callers: `make manifest` (Makefile:239) passes no
# --production-root and relies on the tool's HF_PRODUCTION_ROOT default, which
# is the base root, and the tool's own contract note (:36-39) says manifest
# paths are relative to the campaign directory.

def test_freeze_produces_a_manifest_from_a_raw_tree() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = sandbox(tmp)
        data = Path(tmp) / "data"
        raw_fixture(data, "HF_SMOKE3")
        got = run_cli(base, data, ["freeze", "hf_smoke3"])
        freeze = data / "project/runs/HF_SMOKE3/freeze"
        check("freeze writes a manifest from a raw tree",
              got.returncode == 0, f"rc={got.returncode} {got.stderr[:300]}")
        check("...naming no doubled campaign segment",
              "HF_SMOKE3/HF_SMOKE3" not in got.stderr, got.stderr[:300])
        manifest = freeze / "canonical_manifest.jsonl"
        check("...and the manifest exists", manifest.is_file(), str(manifest))
        if manifest.is_file():
            rows = [json.loads(line) for line in
                    manifest.read_text().splitlines() if line.strip()]
            check("...carrying one row per promoted raw file",
                  len(rows) == 30, f"{len(rows)} rows")
            check("...whose raw paths are relative to the campaign directory",
                  all(row["raw_path"].startswith("raw/") for row in rows),
                  str(rows[0]["raw_path"]) if rows else "no rows")
        check("...and the seal is written",
              (freeze / "freeze_seal.json").is_file(), str(freeze))
        check("...with ten block manifests",
              len(list(freeze.glob("block_*.jsonl"))) == 10,
              str(sorted(p.name for p in freeze.glob("block_*.jsonl"))))


def test_freeze_refuses_a_row_that_is_not_campaign_scoped() -> None:
    """The base root is derived from the row, so the row has to fit."""
    document = json.loads(SMOKE_SELECTOR.read_text())
    row = document["datasets"]["hf_smoke3"]
    row["production_root"] = "${HADRONIZATION_DATA_ROOT}/hadronization_production"
    with tempfile.TemporaryDirectory() as tmp:
        base = sandbox(tmp)
        data = Path(tmp) / "data"
        raw_fixture(data, "HF_SMOKE3")
        selector = Path(tmp) / "selector.json"
        selector.write_text(json.dumps(document))
        got = run_cli(base, data, ["freeze", "hf_smoke3"],
                      {"HADRONIZATION_DATASET_SELECTOR": str(selector)})
    check("freeze refuses a row whose production_root is not campaign-scoped",
          got.returncode != 0, f"rc={got.returncode} {got.stdout[:200]}")
    check("...naming the campaign and the root it was given",
          "HF_SMOKE3" in got.stderr and "hadronization_production" in got.stderr,
          got.stderr[:400])
    check("...and writes no manifest",
          not (data / "project/runs/HF_SMOKE3/freeze"
               / "canonical_manifest.jsonl").is_file(), "a manifest appeared")


def test_freeze_does_not_pass_the_campaign_scoped_root() -> None:
    """Read the source too: the doubled join must not come back."""
    text = UNIFIED_CLI.read_text()
    block = text[text.index("  freeze)"):]
    block = block[:block.index("  render-analysis)")]
    check("the freeze branch passes no campaign-scoped production root",
          '--production-root "${HADRONIZATION_PRODUCTION_ROOT}"' not in block,
          block[-400:])
    check("...and derives the base from the row",
          'freeze_production_base="$(dirname "${HADRONIZATION_PRODUCTION_ROOT}")"'
          in block, block[-400:])


# --- Phase 2: the plot run-slot -------------------------------------------
#
# THE DEFECT THIS CLOSES. prepare_plot_output_plane scopes the output target
# per campaign and commit but routes it through one checkout-local symlink,
# plotting/Plots. A deploy that last plotted another campaign refused and named
# no way forward. The refusal on IMPLICIT change is correct and stays; the
# explicit `plot-slot` command is the way through, and it moves the old pointer
# aside rather than deleting it.
#
# Every case below builds its own plotting/ directory. tools/run_tests.sh
# snapshots the resolved plotting/Plots and fails the suite if a test changes
# it, and symlinking this checkout's plotting/ would put the real link in reach.
FULL_SELECTOR = ROOT / "config/dataset_selector.json"


def plot_sandbox(tmp: str, cli_text: str | None = None) -> tuple[Path, Path]:
    base = sandbox(tmp, cli_text, replace={"plotting/Plots": None}, git=True)
    return base, Path(tmp) / "data"


def held_slot(base: Path, data: Path, campaign: str) -> Path:
    """Point the slot at another run, the way a previous deploy left it."""
    commit = subprocess.run(["git", "-C", str(base), "rev-parse",
                             "--short=12", "HEAD"],
                            capture_output=True, text=True,
                            check=True).stdout.strip()
    target = data / "project/results" / campaign / commit / "plotting"
    target.mkdir(parents=True, exist_ok=True)
    (base / "plotting/Plots").symlink_to(target)
    return target


def test_an_implicit_slot_change_is_refused() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base, data = plot_sandbox(tmp)
        held = held_slot(base, data, "HF_SMOKE3")
        got = run_cli(base, data, ["plot", "hf_run3_v1_candidate", "all"],
                      {"HADRONIZATION_DATASET_SELECTOR": str(FULL_SELECTOR)})
        link = base / "plotting/Plots"
        # A non-zero status alone proves nothing here: plotting continues into
        # run_paper_plots.sh, which fails on its own on a host without ROOT.
        # Require the refusal itself, and require the slot to be unmoved.
        check("plotting refuses to change the slot implicitly",
              got.returncode != 0 and "Nothing was changed." in got.stderr,
              f"rc={got.returncode} {got.stderr[:300]}")
        check("...naming the target found and the target expected",
              str(held) in got.stderr and "HF_RUN3_V1" in got.stderr,
              got.stderr[:400])
        check("...and naming the command that migrates it",
              "plot-slot hf_run3_v1_candidate" in got.stderr, got.stderr[:400])
        check("...leaving the slot where it was",
              link.is_symlink() and Path(os.readlink(link)) == held,
              str(link.is_symlink() and os.readlink(link)))


def test_the_explicit_migration_repoints_and_records() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base, data = plot_sandbox(tmp)
        held = held_slot(base, data, "HF_SMOKE3")
        commit = held.parent.name
        got = run_cli(base, data, ["plot-slot", "hf_run3_v1_candidate"],
                      {"HADRONIZATION_DATASET_SELECTOR": str(FULL_SELECTOR)})
        link = base / "plotting/Plots"
        expected = data / "project/results/HF_RUN3_V1" / commit / "plotting"
        check("plot-slot repoints the link", got.returncode == 0,
              f"rc={got.returncode} {got.stderr[:300]}")
        check("...to the resolved campaign's target",
              link.is_symlink() and Path(os.readlink(link)) == expected,
              str(link.is_symlink() and os.readlink(link)))
        check("...printing the target it left",
              f"PLOT_SLOT_OLD_TARGET={held}" in got.stdout, got.stdout[:400])
        check("...and the target it took",
              f"PLOT_SLOT_NEW_TARGET={expected}" in got.stdout, got.stdout[:400])
        asides = sorted(p.name for p in (base / "plotting").iterdir()
                        if p.name.startswith("Plots."))
        check("...moving the old pointer aside under the run it held",
              asides == [f"Plots.HF_SMOKE3-{commit}.superseded-"
                         f"{__import__('datetime').date.today():%Y%m%d}"],
              str(asides))
        check("...as a pointer to the old target, not a copy",
              bool(asides) and Path(os.readlink(
                  base / "plotting" / asides[0])) == held,
              str(asides))


def test_a_migration_does_not_touch_the_target_files() -> None:
    """A sealed run is reachable only through its target, which never moves."""
    with tempfile.TemporaryDirectory() as tmp:
        base, data = plot_sandbox(tmp)
        held = held_slot(base, data, "HF_SMOKE3")
        sealed = held / "sealed_canvas.pdf"
        sealed.write_bytes(b"a sealed render")
        before = hashlib.sha256(sealed.read_bytes()).hexdigest()
        got = run_cli(base, data, ["plot-slot", "hf_run3_v1_candidate"],
                      {"HADRONIZATION_DATASET_SELECTOR": str(FULL_SELECTOR)})
        check("the migration succeeds", got.returncode == 0, got.stderr[:300])
        check("...and the superseded run's files are still there",
              sealed.is_file()
              and hashlib.sha256(sealed.read_bytes()).hexdigest() == before,
              f"{sealed} changed or vanished")
        check("...and the old target itself was not moved",
              held.is_dir(), str(held))


def test_the_migration_refuses_to_overwrite_a_recorded_pointer() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base, data = plot_sandbox(tmp)
        held = held_slot(base, data, "HF_SMOKE3")
        commit = held.parent.name
        aside = (base / "plotting" /
                 f"Plots.HF_SMOKE3-{commit}.superseded-"
                 f"{__import__('datetime').date.today():%Y%m%d}")
        aside.symlink_to(data / "project/results/HF_SMOKE3/older/plotting")
        got = run_cli(base, data, ["plot-slot", "hf_run3_v1_candidate"],
                      {"HADRONIZATION_DATASET_SELECTOR": str(FULL_SELECTOR)})
        link = base / "plotting/Plots"
        check("the migration refuses rather than overwrite a recorded pointer",
              got.returncode != 0, f"rc={got.returncode} {got.stdout[:200]}")
        check("...naming the pointer it would have replaced",
              aside.name in got.stderr, got.stderr[:300])
        check("...and moves nothing",
              link.is_symlink() and Path(os.readlink(link)) == held,
              str(link.is_symlink() and os.readlink(link)))


def test_a_migration_to_the_same_target_changes_nothing() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base, data = plot_sandbox(tmp)
        got = run_cli(base, data, ["plot-slot", "hf_run3_v1_candidate"],
                      {"HADRONIZATION_DATASET_SELECTOR": str(FULL_SELECTOR)})
        check("plot-slot creates the link when the slot is empty",
              got.returncode == 0, got.stderr[:300])
        again = run_cli(base, data, ["plot-slot", "hf_run3_v1_candidate"],
                        {"HADRONIZATION_DATASET_SELECTOR": str(FULL_SELECTOR)})
        asides = [p.name for p in (base / "plotting").iterdir()
                  if p.name.startswith("Plots.")]
        check("...and says so rather than superseding itself",
              again.returncode == 0
              and "PLOT_SLOT_UNCHANGED=" in again.stdout, again.stdout[:300])
        check("...recording no superseded pointer", asides == [], str(asides))


# --- Phase 3: the plot configurations --------------------------------------
#
# THE DEFECT THIS CLOSES. plotting/run_paper_plots.sh defaulted THNSPARSE_CONFIG
# and THNSPARSE_COMPLETE_ROOT_CONFIG to the reduced JUNCTIONS files, and
# MULTIPLICITY_CONFIG inherited the first. `plot KEY all` took them silently for
# any campaign. This is I3's rule applied to the publication path: derive from
# the resolved campaign, refuse by name, honour an explicit variable.
#
# The cases use HADRONIZATION_REQUEST_PREFLIGHT_ONLY, which is the driver's own
# explicit no-render result, so nothing starts ROOT and nothing is written.
RUN3_COMPLETE_ROOT = ("configuration_multiplicity_HF_RUN3_V1"
                      "_THREETUNE_THnSparse_complete_root.json")


def plot_preflight(tmp: str, key: str, target: str,
                   drop: str | None = None,
                   env_extra: dict | None = None
                   ) -> subprocess.CompletedProcess:
    replace: dict = {"plotting/Plots": None}
    if drop is not None:
        replace[f"plotting/{drop}"] = None
    base = sandbox(tmp, replace=replace, git=True)
    env = {"HADRONIZATION_DATASET_SELECTOR": str(FULL_SELECTOR),
           "HADRONIZATION_REQUEST_PREFLIGHT_ONLY": "1"}
    env.update(env_extra or {})
    return run_cli(base, Path(tmp) / "data", ["plot", key, target], env)


def test_the_plot_configuration_is_derived_from_the_campaign() -> None:
    """Presence of the derived file decides the run, so it is the file read."""
    with tempfile.TemporaryDirectory() as tmp:
        present = plot_preflight(tmp, "hf_run3_v1_candidate",
                                 "thnsparse-complete-root")
    check("a target whose derived configuration exists is accepted",
          "REQUEST_PREFLIGHT_ONLY status=PASS" in present.stdout,
          f"rc={present.returncode} {present.stderr[:300]}")
    with tempfile.TemporaryDirectory() as tmp:
        absent = plot_preflight(tmp, "hf_run3_v1_candidate",
                                "thnsparse-complete-root",
                                drop=RUN3_COMPLETE_ROOT)
    check("...and refused when that same file is the only thing missing",
          absent.returncode == 2, f"rc={absent.returncode} {absent.stdout[:200]}")
    check("...naming the derived path it looked for",
          f"plotting/{RUN3_COMPLETE_ROOT}" in absent.stderr,
          absent.stderr[:400])
    check("...and naming the variable that answers it",
          "THNSPARSE_COMPLETE_ROOT_CONFIG" in absent.stderr, absent.stderr[:400])


def test_a_campaign_without_a_configuration_is_refused_by_name() -> None:
    """HF_SMOKE3 has no THREETUNE configuration. Refusing is the right answer."""
    with tempfile.TemporaryDirectory() as tmp:
        got = plot_preflight(tmp, "hf_smoke3", "all")
    check("plot all refuses a campaign with no derived configuration",
          got.returncode == 2, f"rc={got.returncode} {got.stdout[:200]}")
    check("...naming both derived paths",
          "plotting/configuration_multiplicity_HF_SMOKE3_THREETUNE_"
          "THnSparse.json" in got.stderr
          and "plotting/harvest_configs/configuration_multiplicity_HF_SMOKE3"
          "_THREETUNE_THnSparse.json" in got.stderr, got.stderr[:500])
    check("...and offering no reduced fallback",
          "reduced_JUNCTIONS" not in got.stderr, got.stderr[:500])


def test_an_explicit_plot_configuration_is_honoured() -> None:
    """The reduced files stay reachable, but only by naming them."""
    reduced = "plotting/configuration_multiplicity_reduced_JUNCTIONS"
    with tempfile.TemporaryDirectory() as tmp:
        got = plot_preflight(tmp, "hf_smoke3", "all", env_extra={
            "THNSPARSE_CONFIG": f"{reduced}_THnSparse.json",
            "THNSPARSE_COMPLETE_ROOT_CONFIG":
                f"{reduced}_THnSparse_complete_root.json"})
    check("an explicitly named configuration is used for a campaign with none",
          "REQUEST_PREFLIGHT_ONLY status=PASS" in got.stdout,
          f"rc={got.returncode} {got.stderr[:400]}")


def test_a_run_derives_only_the_configurations_its_targets_read() -> None:
    """A measurement run is not refused for a publication file it never opens.

    HF_RUN3_V1 has a complete-root configuration and no plain THnSparse one, so
    this property is the difference between a working measurement path and a
    refused one.
    """
    with tempfile.TemporaryDirectory() as tmp:
        measurement = plot_preflight(tmp, "hf_run3_v1_candidate",
                                     "thnsparse-complete-root")
    check("a complete-root target does not require the plain configuration",
          "REQUEST_PREFLIGHT_ONLY status=PASS" in measurement.stdout,
          f"rc={measurement.returncode} {measurement.stderr[:300]}")
    with tempfile.TemporaryDirectory() as tmp:
        publication = plot_preflight(tmp, "hf_run3_v1_candidate", "all")
    check("...while a target that does require it is refused, naming it",
          publication.returncode == 2
          and "THNSPARSE_CONFIG" in publication.stderr,
          f"rc={publication.returncode} {publication.stderr[:300]}")


def test_the_driver_carries_no_reduced_configuration_default() -> None:
    text = (ROOT / "plotting/run_paper_plots.sh").read_text()
    for name in ("default_thnsparse_config=", "default_complete_root_config="):
        check(f"the driver defines no {name.rstrip('=')}",
              name not in text, name)


# --- Phase 4: the defaults sweep -------------------------------------------
#
# Every configuration default plotting/run_paper_plots.sh still carries, with
# the showing that places each target it feeds. MEASUREMENT-PLANE means the
# target can reach an accepted or a measurement root: the campaign- and
# commit-scoped plot plane below plotting/Plots, or HADRONIZATION_MEASUREMENT_ROOT.
# DEVELOPMENT-ONLY means it cannot, and the showing says where its output goes
# instead. A measurement-plane variable carries no default. A development-only
# one may, and the showing is recorded here rather than in prose.
#
# CONSUMER SEARCH, measured 2026-08-27. docs/GOLDEN_OUTPUTS.md names only
# campaign-scoped configurations and mentions none of RootFiles/HF, 12-01-2026,
# 27-03-2026 or FinalAnalysis; `git ls-files plotting/FinalAnalysis` tracks the
# two macros and no output. No tracked artifact was produced through any
# default below. History is recorded, not rewritten.
DRIVER = ROOT / "plotting/run_paper_plots.sh"

SWEEP = (
    ("THNSPARSE_CONFIG", ("thnsparse", "freeze-boundaries"),
     "measurement-plane",
     "renders and freezes into the campaign-scoped plot plane"),
    ("THNSPARSE_COMPLETE_ROOT_CONFIG",
     ("thnsparse-complete-root", "measure-balancing",
      "multiplicity-boundaries-smoke", "freeze-boundaries-smoke"),
     "measurement-plane",
     "measure-balancing writes under HADRONIZATION_MEASUREMENT_ROOT; the "
     "others render into the plot plane"),
    ("MULTIPLICITY_CONFIG", ("multiplicity-boundaries", "multiplicity-compact"),
     "measurement-plane",
     "writes MULTIPLICITY_OUTPUT_DIR, which defaults inside plotting/Plots"),
    ("KINEMATIC_RAW_BASE", ("multiplicity-spectrum", "kinematic-spectra"),
     "measurement-plane",
     "reads raw files and writes KINEMATIC_OUTPUT_DIR, inside plotting/Plots"),
    ("FINAL_INDEPENDENT_TAG", ("final-multiplicity", "final-yields"),
     "development-only",
     "both macros write GetHadronizationBaseDir()/plotting/FinalAnalysis/Plots, "
     "a checkout-local directory that is not the plot plane and holds no "
     "tracked file"),
    ("FINAL_COMBINED_TAG", ("final-multiplicity", "final-yields"),
     "development-only", "as FINAL_INDEPENDENT_TAG"),
    ("FINAL_NSUB", ("final-multiplicity", "final-yields"),
     "development-only", "as FINAL_INDEPENDENT_TAG"),
)

# Targets that read no configuration default at all, with why.
NO_CONFIG_TARGETS = {
    "audit-subsamples": "reads the freeze and the subsample base only",
    "legacy-regression": "gated to the legacy_regression_default status, "
                         "which is publication-ineligible by contract",
    "validate-inputs": "runs plotting/validate_thnsparse_inputs.sh, which "
                       "writes nothing",
}


def accepted_targets() -> set[str]:
    """Every target the driver can run, read from the driver, not listed here.

    Two sources: the alternation of directly nameable targets, and the group
    expansions. multiplicity-boundaries-smoke reaches a run only through the
    smoke group, so an alternation-only reading would miss it.
    """
    text = DRIVER.read_text()
    targets: set[str] = set()
    for line in text.splitlines():
        stripped = line.strip()
        if (stripped.endswith(")") and "|" in stripped
                and "measure-balancing" in stripped
                and "audit-subsamples" in stripped):
            targets |= set(stripped[:-1].split("|"))
        if stripped.startswith("expanded_targets+=("):
            targets |= {name for name in
                        stripped[stripped.index("(") + 1:-1].replace(
                            '"', "").split()
                        if "$" not in name}
    return targets


def test_the_sweep_covers_every_target_the_driver_accepts() -> None:
    """A new target cannot escape the classification by being added quietly."""
    accepted = accepted_targets()
    check("the driver's accepted-target list was read", bool(accepted),
          "no target alternation found in the driver")
    classified = {t for _, targets, _, _ in SWEEP for t in targets}
    classified |= set(NO_CONFIG_TARGETS)
    check("every accepted target carries a classification",
          accepted <= classified, str(sorted(accepted - classified)))
    check("...and nothing is classified that the driver does not accept",
          classified <= accepted, str(sorted(classified - accepted)))


def test_no_measurement_plane_variable_carries_a_default() -> None:
    text = DRIVER.read_text()
    for name, targets, plane, showing in SWEEP:
        if plane != "measurement-plane":
            continue
        # `${NAME:-` with anything but an empty or another-variable value is a
        # default. The derivations assign through printf -v, not through :-.
        literal = f'{name}="${{{name}:-'
        line = next((l for l in text.splitlines() if l.startswith(literal)), "")
        remainder = line[len(literal):] if line else ""
        defaulted = bool(remainder) and not remainder.startswith(("}", "${"))
        check(f"{name} carries no literal default ({', '.join(targets)})",
              not defaulted, line)


def test_a_development_only_default_writes_outside_every_plane() -> None:
    """The showing for the three FINAL_* defaults, per target, not per script."""
    for target, macro in (
            ("final-multiplicity",
             "plotting/FinalAnalysis/Plot_MultiplicityDistributions_TwoSamples.C"),
            ("final-yields",
             "plotting/FinalAnalysis/Plot_SelectedParticleYields_IndependentVsCombined.C")):
        source = (ROOT / macro).read_text()
        check(f"{target} writes only below plotting/FinalAnalysis/Plots",
              'GetHadronizationBaseDir() + "/plotting/FinalAnalysis/Plots"'
              in source, macro)
        check(f"...so {target} reaches no plot plane",
              "plotting/Plots/" not in source
              and "HADRONIZATION_MEASUREMENT_ROOT" not in source, macro)
    tracked = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "plotting/FinalAnalysis"],
        capture_output=True, text=True, check=True).stdout.split()
    check("...and that directory holds no tracked output",
          all(name.endswith(".C") for name in tracked), str(tracked))


def test_nothing_can_reach_the_legacy_sample_by_default() -> None:
    """The raw base has no fallback, and two rules stand in front of it.

    REACHABILITY, measured 2026-08-27. The RootFiles/HF fallback that this
    checks the absence of was not reachable in the tracked tree. Both routes to
    it are closed by rules that already existed, and both are asserted here so
    that removing one is visible:

      1. tools/dataset_selector.py refuses a canonical row with no raw_base;
      2. with USE_DATASET_SELECTOR=false the publication gate refuses a
         raw-reading target, for an unset dataset status.

    The fallback was therefore a latent hazard rather than a live defect, and
    the driver's own refusal is defence in depth. Saying so is the point: a
    check that claimed to exercise the guard would be claiming a reachability
    this tree does not have.
    """
    # The comment above the refusal names the removed value, so read the code
    # lines only. A comment that records a defect is not the defect.
    code = [line for line in DRIVER.read_text().splitlines()
            if line.strip() and not line.lstrip().startswith("#")]
    check("the driver carries no legacy raw-base fallback",
          not [line for line in code if "RootFiles/HF" in line],
          str([line for line in code if "RootFiles/HF" in line])[:200])

    document = json.loads((ROOT / "config/dataset_selector_hf_run3_v1.json")
                          .read_text())
    document["datasets"]["hf_run3_v1_candidate"]["raw_base"] = ""
    with tempfile.TemporaryDirectory() as tmp:
        base = sandbox(tmp, replace={"plotting/Plots": None}, git=True)
        selector = Path(tmp) / "selector.json"
        selector.write_text(json.dumps(document))
        row = run_cli(base, Path(tmp) / "data",
                      ["plot", "hf_run3_v1_candidate", "kinematic-spectra"],
                      {"HADRONIZATION_DATASET_SELECTOR": str(selector),
                       "HADRONIZATION_REQUEST_PREFLIGHT_ONLY": "1"})
    check("rule 1: a canonical row with no raw_base is refused by the selector",
          row.returncode != 0 and "requires raw_base" in row.stderr,
          f"rc={row.returncode} {row.stderr[:300]}")

    # Rule 2 is a driver rule, so drive the driver: ./hadronization always
    # resolves a dataset first and never reaches USE_DATASET_SELECTOR=false.
    with tempfile.TemporaryDirectory() as tmp:
        base = sandbox(tmp, replace={"plotting/Plots": None}, git=True)
        environment = dict(os.environ)
        environment.update(USE_DATASET_SELECTOR="false",
                           HADRONIZATION_REQUEST_PREFLIGHT_ONLY="1",
                           HADRONIZATION_BASE=str(base))
        for name in ("KINEMATIC_RAW_BASE", "HADRONIZATION_RAW_BASE",
                     "HADRONIZATION_DATASET_STATUS"):
            environment.pop(name, None)
        loose = subprocess.run(
            ["bash", str(base / "plotting/run_paper_plots.sh"),
             "kinematic-spectra"],
            env=environment, text=True, capture_output=True)
    check("rule 2: with no selector the publication gate refuses first",
          loose.returncode != 0
          and "fail-closed" in loose.stderr, f"rc={loose.returncode} "
          f"{loose.stderr[:300]}")


def test_a_target_that_reads_no_raw_files_is_not_refused_for_one() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = sandbox(tmp, replace={"plotting/Plots": None}, git=True)
        got = run_cli(base, Path(tmp) / "data",
                      ["plot", "hf_run3_v1_candidate", "thnsparse-complete-root"],
                      {"HADRONIZATION_DATASET_SELECTOR": str(FULL_SELECTOR),
                       "HADRONIZATION_REQUEST_PREFLIGHT_ONLY": "1"})
    check("a target that reads no raw files is unaffected by the raw base",
          "REQUEST_PREFLIGHT_ONLY status=PASS" in got.stdout,
          f"rc={got.returncode} {got.stderr[:300]}")


def main() -> int:
    tests = [value for name, value in sorted(globals().items())
             if name.startswith("test_") and callable(value)]
    for test in tests:
        test()
    print(f"\n{len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
