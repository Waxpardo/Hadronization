#!/usr/bin/env python3
"""Display filtering never becomes axis loosening.

THE DEFECT THIS CLOSES. Two variant figures show a subset of the multiplicity
axis. The obvious way to build them -- delete the unwanted classes from
`histograms_to_analyse` -- is refused by the axis contract, and that refusal is
correct: a figure showing two of eleven classes, with nothing on it saying so,
is exactly the silent re-binning the B6 family exists to prevent.

So the axis stays whole and the filtering is display-only. This test pins the
four properties that make that safe:

  (a) the FULL axis is still configured and validated -- every contract class is
      present in every variant, so removing one is still refused;
  (b) a filter may never leave zero drawn bins;
  (c) the self-declaration is DERIVED, so changing the artifact changes it;
  (d) the declaration's ranges come from the contract, not from the config's
      transcribed multiplicityMin/multiplicityMax.

(d) is here because the first version of the generator read the config's own
numbers and printed 59.9 for a boundary the artifact puts at 59.8 -- E9's defect
reproduced by the very generator meant to prevent it.
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLOTTING = ROOT / "plotting"
BOUNDARIES = ROOT / "config" / "multiplicity_percentile_classes_v2.json"
sys.path.insert(0, str(ROOT / "tools"))
from class_label_format import format_percentile_range  # noqa: E402
GENERATOR = ROOT / "tools" / "make_variant_configs.py"

def artifact_class_count() -> int:
    return len(json.loads(BOUNDARIES.read_text())["classes"])


def artifact_classes() -> list[dict]:
    return json.loads(BOUNDARIES.read_text())["classes"]


# How many bins each variant DRAWS. The closure variant draws every class and
# the integrated bin, so its count is derived: ruling R10 forbids writing the
# class count down a second time.
VARIANTS = {
    "configuration_multiplicity_HF_RUN3_V1_VEXTREMES.json": 2,
    "configuration_multiplicity_HF_RUN3_V1_VINTEGRATED.json": 1,
    "configuration_multiplicity_HF_RUN3_V1_VINTEGRATED_CLOSURE.json":
        artifact_class_count() + 1,
}


def drawn_of(doc: dict) -> list[str]:
    ignore = set()
    for canvas in doc.get("canvases_to_be_drawn", []):
        ignore |= set(canvas.get("bins_to_ignore", []))
    return [b["hDPhi"] for b in doc["histograms_to_analyse"]
            if b["hDPhi"] not in ignore]


def main() -> int:
    failures: list[str] = []
    n_classes = artifact_class_count()

    # The structural assertions run FIRST and the drift check last. Ordered the
    # other way, every hand-edit fails as "drifted" and the assertions below are
    # never reached -- so a mutation test could not tell whether they work.
    for name, expected_drawn in VARIANTS.items():
        path = PLOTTING / name
        if not path.exists():
            failures.append(f"{name}: missing")
            continue
        doc = json.loads(path.read_text())
        bins = doc["histograms_to_analyse"]

        # (a) the full artifact axis is present, whatever is drawn
        classes = [b for b in bins
                   if not (b["multiplicityMin"] == 0.0
                           and b["multiplicityMax"] == 100.0)]
        if len(classes) != n_classes:
            failures.append(
                f"{name}: carries {len(classes)} classes, artifact defines "
                f"{n_classes}; the full axis must stay configured")

        # (b) something is drawn
        drawn = drawn_of(doc)
        if not drawn:
            failures.append(f"{name}: display filter leaves nothing drawn")
        if len(drawn) != expected_drawn:
            failures.append(
                f"{name}: draws {len(drawn)} bins, expected {expected_drawn}")

        # the declaration exists whenever something is filtered
        declaration = doc.get("axis_declaration", "")
        if len(drawn) < len(bins) and not declaration:
            failures.append(f"{name}: filtered but carries no axis_declaration")

    # (d) the declaration carries the authoritative tune-local windows.
    closure = json.loads(
        (PLOTTING / "configuration_multiplicity_HF_RUN3_V1_VINTEGRATED_CLOSURE.json"
         ).read_text())
    decl = closure.get("axis_declaration", "")
    for row in artifact_classes():
        label = format_percentile_range(row["percentile_min"],
                                        row["percentile_max"])
        if label not in decl:
            failures.append(
                f"declaration should carry the contract's {label} class: "
                f"{decl!r}")

    # (c) derived, not fixed: perturb the artifact and the label must follow.
    with tempfile.TemporaryDirectory() as tmp:
        sandbox = Path(tmp) / "repo"
        subprocess.run(["cp", "-R", str(ROOT), str(sandbox)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        art = sandbox / "config" / "multiplicity_percentile_classes_v2.json"
        doc = json.loads(art.read_text())
        # Move the top class's requested edge; the derived declaration follows.
        # The new edge is one point above whatever the contract holds, so this
        # mutation is a real change for any class set (ruling R10).
        doc["classes"][-1]["percentile_max"] += 1.0
        art.write_text(json.dumps(doc, indent=2) + "\n")
        run = subprocess.run(
            [sys.executable, str(sandbox / "tools" / "make_variant_configs.py")],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=str(sandbox))
        if run.returncode != 0:
            failures.append(
                "generator failed on a perturbed artifact: "
                + run.stdout.decode(errors="replace")[-400:])
        else:
            moved = json.loads(
                (sandbox / "plotting" /
                 "configuration_multiplicity_HF_RUN3_V1_VEXTREMES.json").read_text()
            ).get("axis_declaration", "")
            if moved == declaration_baseline():
                failures.append(
                    "axis_declaration did not change when the boundary "
                    f"artifact changed; it is not derived: {moved!r}")

    check = subprocess.run([sys.executable, str(GENERATOR), "--check"],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if check.returncode != 0:
        failures.append("variant configs drifted from their generator:\n"
                        + check.stdout.decode(errors="replace"))

    if failures:
        for line in failures:
            print("FAIL: " + line)
        return 1
    print("display filter: full axis configured, filter non-empty, "
          "declaration derived from the artifact")
    return 0


def declaration_baseline() -> str:
    return json.loads(
        (PLOTTING / "configuration_multiplicity_HF_RUN3_V1_VEXTREMES.json"
         ).read_text())["axis_declaration"]


if __name__ == "__main__":
    raise SystemExit(main())
