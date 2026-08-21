#!/usr/bin/env python3
"""The synchronized manuscript must expose the unresolved scientific P0."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"


def main() -> int:
    main_tex = (PAPER / "hfBalancingModelPaper.tex").read_text()
    observables = (PAPER / "Observables.tex").read_text()
    model = (PAPER / "Model.tex").read_text()
    results = (PAPER / "Results.tex").read_text()
    summary = (PAPER / "Summary.tex").read_text()
    physics = (ROOT / "docs" / "PHYSICS.md").read_text()

    assert "PUBLIC-BLOCKED MANUSCRIPT" in main_tex
    assert "one derived-error implementation does" not in main_tex
    assert "tune-dependent generator-hang" in main_tex

    combined = " ".join((results + summary).split())
    for required in (
        "0 hangs in 1,000",
        "63 in 1,063 (5.93\\%)",
        "64 in 1,064 (6.02\\%)",
        "JunctionSplitting",
        "event content and the published observables has not been measured",
    ):
        assert required in combined, required

    for required in (
        "0.7670\\%",
        "exactly zero",
        "forced hard-heavy sample",
    ):
        assert required in " ".join((model + summary).split()), required

    assert "full $\\dphi$ axis" in observables
    assert "21 August 2026" in observables
    assert "does not alter earlier frozen" in physics
    assert "regional-integral claim" in observables

    print("manuscript blockers: P0 visible, multiplicity qualified, full-axis ruled")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
