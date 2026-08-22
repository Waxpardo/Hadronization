#!/usr/bin/env python3
"""Require the noninteractive CVMFS fallback to bind PYTHIA runtime data."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    setup = (ROOT / "setupEnv.sh").read_text()
    expected_data = '${pythia_package}/share/Pythia8/xmldoc'
    assert f'export PYTHIA8DATA="{expected_data}"' in setup
    assert f'[[ ! -f "{expected_data}/Index.xml" ]]' in setup
    assert 'pythia_data_candidate="${PYTHIA8%/}/share/Pythia8/xmldoc"' in setup
    assert (
        '[[ -n "${PYTHIA8DATA:-}" && ! -f '
        '"${PYTHIA8DATA%/}/Index.xml" ]]'
    ) in setup
    assert 'PYTHIA8DATA:       ${PYTHIA8DATA:-\'(not set)\'}' in setup
    assert (
        "export HF_PYTHIA8_PREFIX HF_PYTHIA8_VERSION HF_PYTHIA8_GCC_PREFIX"
        in setup
    )
    print("setup environment contract test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
