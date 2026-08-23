#!/usr/bin/env python3
"""Draw the systematic band beside the statistical error, per class.

A SEPARATE COMPOSITION STEP, NOT A CHANGE TO THE PLOTTER. Ruling R7 keeps the
overlay outside `improvedPlotting_THnSparse.C`: that macro renders the nominal
canvases, its source sha256 is recorded in every boundary receipt, and a
figure with a band must stay distinguishable from the same figure without one.
This script reads what the plotter already produced -- its UNCERTAINTY_MATRIX
log -- adds the envelope, and writes a NEW canvas into the plotting-syst
plane. It never opens the nominal plane for writing and never edits a nominal
canvas.

WHAT IT DRAWS. One panel per tune: the per-class quantity with its statistical
error bar, and the combined systematic as a band around each point. The
observable is whatever the envelope declares, and the envelope must declare
ONE:

  balancing_yield   the per-trigger balancing yield, class by class
  balancing_ratio   the Lambda_b / B- balancing-yield ratio, class by class

WHY THE OBSERVABLE IS CHECKED AND NOT ASSUMED. A per-class yield systematic
may not be propagated into the ratio. Lambda_b and B- share their triggers and
their events, so part of every variation cancels inside the ratio, and adding
the two yield systematics in quadrature would double-count exactly the part
that cancels. `extraction/combine_derived.py` states the rule and implements
the alternative: recompute the derived quantity from each variation's own
render and difference it against the nominal. So this script refuses to draw a
ratio band from yield rows rather than producing a plausible wrong figure.

PRESENTATION IS NOT DECIDED. Band against box, and combined against
per-source, are open questions for the owner at writing time. The combined
total band is implemented. `DRAW_PER_SOURCE` renders one band per source
instead; it is a code-level switch, default off, and no caller can set it.

STATISTICAL-ONLY INPUTS SAY SO. A class the envelope does not cover is drawn
with its statistical error alone and is labelled STAT-ONLY on the canvas and
in the manifest. A reader must never have to guess which points carry a band.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
for _extra in (ROOT_DIR / "extraction",):
    if str(_extra) not in sys.path:
        sys.path.insert(0, str(_extra))

from combine_per_class import baryon_meson_ratio  # noqa: E402
from harvest_class_axis import class_order, parse_log  # noqa: E402

ENVELOPE_SCHEMA = "hadronization_systematics_envelope_v1"
OBSERVABLES = ("balancing_yield", "balancing_ratio")
OUTPUT_PLANE_NAME = "plotting-syst"

# Presentation switch, deliberately not exposed on the command line. The owner
# rules on band against box and on combined against per-source at writing
# time; until then the combined total band is what this renders.
DRAW_PER_SOURCE = False


class OverlayRefused(Exception):
    """A refusal that names its reason. Never a warning, never a default."""


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_envelope(path: Path) -> dict:
    if not path.is_file():
        raise OverlayRefused(f"no envelope at {path}")
    envelope = json.loads(path.read_text())
    if envelope.get("schema") != ENVELOPE_SCHEMA:
        raise OverlayRefused(
            f"envelope declares {envelope.get('schema')!r}, "
            f"expected {ENVELOPE_SCHEMA!r}")
    if envelope.get("status") != "COMPLETE":
        raise OverlayRefused(
            f"envelope status is {envelope.get('status')!r}, expected "
            f"'COMPLETE'; missing={envelope.get('missing')}")
    if not envelope.get("rows"):
        raise OverlayRefused("a COMPLETE envelope with no row cannot be drawn")
    return envelope


def declared_observable(envelope: dict) -> str:
    observables = {row.get("observable") for row in envelope["rows"]}
    if len(observables) != 1:
        raise OverlayRefused(
            "an envelope must declare exactly one observable, found "
            f"{sorted(o for o in observables if o)}")
    observable = observables.pop()
    if observable not in OBSERVABLES:
        raise OverlayRefused(
            f"unsupported observable {observable!r}; this renderer draws "
            + " and ".join(OBSERVABLES))
    return observable


def assert_output_plane(plane: Path) -> None:
    if plane.name != OUTPUT_PLANE_NAME:
        raise OverlayRefused(
            f"the overlay writes only under a {OUTPUT_PLANE_NAME} plane, "
            f"not {plane}")
    if "plotting" in [part for part in plane.parts[:-1]]:
        raise OverlayRefused(
            f"the overlay may not write beneath a plotting plane: {plane}")


def nominal_points(log_text: str, observable: str) -> dict[tuple, dict]:
    """(tune, class) -> {value, stat}. The statistical error, class by class."""
    rows = parse_log(log_text)
    points: dict[tuple, dict] = {}
    for key, row in rows.items():
        flavour, trigger, tune, associate, cls = key
        if observable == "balancing_ratio":
            if row.get("is_reference") == "true":
                continue
            try:
                ratio = baryon_meson_ratio(row)
            except (ValueError, ZeroDivisionError, KeyError):
                continue
            points[(tune, associate, cls)] = {
                "value": ratio["ratio"], "stat": ratio["ratio_sem"]}
        else:
            if row.get("status") != "PASS":
                continue
            points[(tune, associate, cls)] = {
                "value": float(row["central_yield"]),
                "stat": float(row["yield_sem"])}
    return points


def compose(envelope: dict, points: dict[tuple, dict], observable: str
            ) -> list[dict]:
    """One drawable point per class, with its band or its STAT-ONLY label."""
    by_key = {
        (row["tune"], row["associate"], row["class"]): row
        for row in envelope["rows"]}
    drawable = []
    for key in sorted(points, key=lambda k: (k[0], k[1], class_order(k[2]))):
        tune, associate, cls = key
        point = points[key]
        row = by_key.get(key)
        entry = {
            "tune": tune, "associate": associate, "class": cls,
            "observable": observable,
            "value": point["value"], "stat": point["stat"],
        }
        if row is None:
            entry.update(systematic=0.0, systematic_percent=0.0,
                         statistical_only=True,
                         label="STAT-ONLY")
        else:
            entry.update(
                systematic=abs(row["combined_percent"]) * abs(point["value"])
                / 100.0,
                systematic_percent=row["combined_percent"],
                statistical_only=False,
                label="STAT+SYST",
                terms={
                    name: term["contribution_percent"]
                    for name, term in row.get("terms", {}).items()},
                dropped=row.get("dropped", []))
        drawable.append(entry)
    return drawable


def macro_function_name(stem: str) -> str:
    """ROOT runs the function named after the file, so the two must agree."""
    name = "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in stem)
    return name if not name[:1].isdigit() else f"m_{name}"


def macro_text(drawable: list[dict], observable: str, stamp: dict,
               function_name: str) -> str:
    """A self-contained ROOT macro. Every canvas carries the stamp."""
    tunes = sorted({d["tune"] for d in drawable})
    lines = [
        "// Generated by plotting/render_systematics_overlay.py.",
        f"// envelope_sha256 {stamp['envelope_sha256']}",
        f"// producing_commit {stamp['producing_commit']}",
        "// Do not edit: regenerate through ./hadronization plot "
        "--systematics.",
        f"void {function_name}() {{",
        "  gStyle->SetOptStat(0);",
        f'  TCanvas c("systematics_overlay", "systematics overlay", '
        f'{420 * max(1, len(tunes))}, 420);',
        f"  c.Divide({max(1, len(tunes))}, 1);",
    ]
    for index, tune in enumerate(tunes, start=1):
        entries = [d for d in drawable if d["tune"] == tune]
        n = len(entries)
        lines += [
            f"  c.cd({index});",
            f'  TH1F* frame{index} = gPad->DrawFrame(0.5, {_low(entries)}, '
            f'{n + 0.5}, {_high(entries)});',
            f'  frame{index}->SetTitle("{tune};multiplicity class;'
            f'{observable}");',
            f"  TGraphErrors* stat{index} = new TGraphErrors({n});",
            f"  TGraphErrors* syst{index} = new TGraphErrors({n});",
        ]
        for point_index, entry in enumerate(entries):
            x = point_index + 1
            lines += [
                f"  stat{index}->SetPoint({point_index}, {x}, "
                f"{entry['value']!r});",
                f"  stat{index}->SetPointError({point_index}, 0, "
                f"{entry['stat']!r});",
                f"  syst{index}->SetPoint({point_index}, {x}, "
                f"{entry['value']!r});",
                f"  syst{index}->SetPointError({point_index}, 0.28, "
                f"{entry['systematic']!r});",
            ]
        lines += [
            f"  syst{index}->SetFillStyle(3004);",
            f"  syst{index}->SetFillColor(kAzure + 1);",
            f'  syst{index}->Draw("5 SAME");',
            f"  stat{index}->SetMarkerStyle(20);",
            f'  stat{index}->Draw("P SAME");',
        ]
        only = [e["class"] for e in entries if e["statistical_only"]]
        if only:
            lines.append(
                f'  TLatex* note{index} = new TLatex(); '
                f'note{index}->SetNDC(); note{index}->SetTextSize(0.03); '
                f'note{index}->DrawLatex(0.14, 0.86, '
                f'"STAT-ONLY: {" ".join(only)}");')
    lines += [
        # The stamp belongs to the canvas, not to whichever pad was last
        # active: a reader must find it on the figure however it is cropped.
        "  c.cd(0);",
        "  TLatex* stampText = new TLatex(); stampText->SetNDC();",
        "  stampText->SetTextSize(0.020);",
        f'  stampText->DrawLatex(0.02, 0.005, "envelope '
        f'{stamp["envelope_sha256"][:16]} commit '
        f'{stamp["producing_commit"][:12]}");',
        f'  c.SaveAs("{stamp["pdf"]}");',
        f'  c.SaveAs("{stamp["png"]}");',
        '  printf("OVERLAY_RENDERED\\n");',
        "}",
    ]
    return "\n".join(lines) + "\n"


def _span(entries: list[dict]) -> tuple[float, float]:
    """The drawn range, from the data alone.

    An axis anchored at zero would be a presentation decision, and
    presentation is the owner's at writing time.
    """
    low = min(e["value"] - e["stat"] - e["systematic"] for e in entries)
    high = max(e["value"] + e["stat"] + e["systematic"] for e in entries)
    margin = 0.1 * ((high - low) or abs(high) or 1.0)
    return low - margin, high + margin


def _low(entries: list[dict]) -> float:
    return _span(entries)[0]


def _high(entries: list[dict]) -> float:
    return _span(entries)[1]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--envelope", type=Path, required=True)
    ap.add_argument("--output-plane", type=Path, required=True)
    ap.add_argument("--campaign", required=True)
    ap.add_argument("--commit", required=True)
    ap.add_argument("--nominal-log", type=Path, required=True,
                    help="the nominal render log carrying UNCERTAINTY_MATRIX rows")
    ap.add_argument("targets", nargs="*", help="accepted and recorded")
    args = ap.parse_args()

    try:
        assert_output_plane(args.output_plane)
        envelope = load_envelope(args.envelope)
        observable = declared_observable(envelope)
        if not args.nominal_log.is_file():
            raise OverlayRefused(f"no nominal render log at {args.nominal_log}")
        points = nominal_points(
            args.nominal_log.read_text(errors="replace"), observable)
        if not points:
            raise OverlayRefused(
                f"the nominal log carries no {observable} point to draw")
        drawable = compose(envelope, points, observable)
    except OverlayRefused as error:
        print(f"OVERLAY_REFUSED {error}", file=sys.stderr)
        return 4

    if DRAW_PER_SOURCE:
        print("OVERLAY_PER_SOURCE enabled", file=sys.stderr)

    args.output_plane.mkdir(parents=True, exist_ok=True)
    envelope_sha = sha256(args.envelope)
    prefix = f"systematics_overlay_{args.campaign}_{observable}"
    stamp = {
        "envelope_sha256": envelope_sha,
        "producing_commit": args.commit,
        "pdf": str(args.output_plane / f"{prefix}.pdf"),
        "png": str(args.output_plane / f"{prefix}.png"),
    }

    macro = args.output_plane / f"{prefix}.C"
    macro.write_text(
        macro_text(drawable, observable, stamp, macro_function_name(prefix)))

    manifest = args.output_plane / f"{prefix}_manifest.json"
    manifest.write_text(json.dumps({
        "schema": "hadronization_systematics_overlay_manifest_v1",
        "campaign": args.campaign,
        "observable": observable,
        "envelope": str(args.envelope),
        "envelope_sha256": envelope_sha,
        "producing_commit": args.commit,
        "output_plane": str(args.output_plane),
        "requested_targets": args.targets,
        "draw_per_source": DRAW_PER_SOURCE,
        "presentation": "combined total band; band against box and "
                        "per-source rendering remain owner decisions",
        "statistical_only_points": [
            {"tune": d["tune"], "associate": d["associate"],
             "class": d["class"]}
            for d in drawable if d["statistical_only"]],
        "points": drawable,
    }, indent=1, sort_keys=True) + "\n")

    root = shutil.which("root")
    if root is None:
        print(
            "OVERLAY_MACRO_ONLY root is absent; the macro and manifest are "
            f"written and no canvas was drawn: {macro}")
        return 0
    result = subprocess.run(
        [root, "-l", "-b", "-q", str(macro)],
        cwd=str(args.output_plane), text=True, capture_output=True,
        check=False)
    if result.returncode != 0 or "OVERLAY_RENDERED" not in result.stdout:
        print(result.stdout, file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        print("OVERLAY_REFUSED the ROOT canvas did not render",
              file=sys.stderr)
        return 4
    print(
        f"OVERLAY_RENDERED campaign={args.campaign} observable={observable} "
        f"points={len(drawable)} "
        f"stat_only={sum(1 for d in drawable if d['statistical_only'])} "
        f"envelope_sha256={envelope_sha} plane={args.output_plane}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
