#!/usr/bin/env python3
"""Keep strict project warnings without diagnosing pinned external headers."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    makefile = (ROOT / "SimulationScripts/Makefile").read_text()
    assert "ROOT_CXXFLAGS_RAW :=" in makefile
    assert "$(patsubst -I%,-isystem %,$(ROOT_CXXFLAGS_RAW))" in makefile
    assert "PYTHIA_CXXFLAGS := -isystem $(PYTHIA8)/include" in makefile
    assert "$(patsubst -I%,-isystem %,$(PYTHIA_CXXFLAGS_RAW))" in makefile
    assert "-Wall -Wextra -Wpedantic -Wconversion -Wshadow" in makefile
    print("external-header warning contract test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
