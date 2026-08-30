#!/usr/bin/env python3
"""The T1 counting macro is exercised against hand-computed events.

WHY A FIXTURE AND NOT A SPOT CHECK. The sample table is a paper number, and the
two ways to get it wrong are both silent: counting the net-valence checksums
(which are zero in a good event, finding F55) and counting over a branch that
is not there (which reads as zero). Neither shows up as an error. So the tree
here is built with the producer's exact branch names and types
(generation/producer/heavyflavourcorrelations_status.cpp:706-781), three events
are hand-computed, and every output number is asserted.

THE THREE EVENTS, AND WHAT EACH ONE IS FOR.

  1. A B+ and a D-, both final, plus a NON-FINAL Lambda_b. The non-final record
     must be excluded from every count -- it is an intermediate state the
     producer stores because it applies no isFinal gate at storage (`:1071`).

  2. A J/psi-like record: nc=1, ncbar=1, final. It contributes 2 to the charm
     content sum and 0 to all eight species rows. This is owner decision O2's
     distinction made executable: the content sums count heavy QUARKS bound in
     final heavy hadrons, so a hidden-charm state carries two of them, while the
     species rows are exact PDG matches and it is none of them.

  3. A Lambda_b-bar and a Lambda_c+, both final, to cover the baryon rows and
     the conjugate signs.

The last case asserts the branch-presence preflight: a tree missing one required
branch must be refused BY NAME, never counted as zero.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MACRO = ROOT / "tools" / "count_generated_sample.C"

# (pdg, isFinal, nc, ncbar, nb, nbbar), per event.
EVENTS = [
    [
        (521, 1, 0, 0, 0, 1),     # B+ = (u b-bar): one b-bar
        (-411, 1, 0, 1, 0, 0),    # D- = (d c-bar): one c-bar
        (5122, 0, 1, 0, 1, 0),    # Lambda_b, NOT final: excluded everywhere
    ],
    [
        (443, 1, 1, 1, 0, 0),     # J/psi-like: hidden charm, 2 charm quarks
    ],
    [
        (-5122, 1, 0, 0, 1, 0),   # Lambda_b-bar
        (4122, 1, 1, 0, 0, 0),    # Lambda_c+
    ],
]

# Hand-computed from EVENTS, over heavyIsFinal == 1 only.
EXPECTED_EVENTS = 3
EXPECTED_FINAL_HEAVY_HADRONS = 5          # 2 + 1 + 2
EXPECTED_CHARM_CONTENT = 1 + 2 + 1        # D- ; J/psi ; Lambda_c+
EXPECTED_BEAUTY_CONTENT = 1 + 0 + 1       # B+ ; -- ; Lambda_b-bar
EXPECTED_YIELDS = {
    "Bplus": 1,
    "Bminus": 0,
    "Lambdab": 0,                          # the only Lambda_b is NOT final
    "Lambdabbar": 1,
    "Dplus": 0,
    "Dminus": 1,
    "Lambdacplus": 1,
    "Lambdacplusbar": 0,
}

BRANCHES = ("heavyPdg", "heavyIsFinal", "heavyNc", "heavyNcbar",
            "heavyNb", "heavyNbbar")

WRITER = r"""
#include "TFile.h"
#include "TTree.h"
#include <vector>
void write_fixture(const char* path, const char* skip)
{{
    TFile file(path, "RECREATE");
    TTree tree("tree", "synthetic heavy-flavour fixture");
    std::vector<int> heavyPdg, heavyIsFinal, heavyNc, heavyNcbar,
                     heavyNb, heavyNbbar;
    const std::string omit = skip;
    if (omit != "heavyPdg")     tree.Branch("heavyPdg", &heavyPdg);
    if (omit != "heavyIsFinal") tree.Branch("heavyIsFinal", &heavyIsFinal);
    if (omit != "heavyNc")      tree.Branch("heavyNc", &heavyNc);
    if (omit != "heavyNcbar")   tree.Branch("heavyNcbar", &heavyNcbar);
    if (omit != "heavyNb")      tree.Branch("heavyNb", &heavyNb);
    if (omit != "heavyNbbar")   tree.Branch("heavyNbbar", &heavyNbbar);
{fills}
    tree.Write();
    file.Close();
}}
"""


def _fill_block() -> str:
    lines = []
    for event in EVENTS:
        lines.append("    heavyPdg.clear(); heavyIsFinal.clear();")
        lines.append("    heavyNc.clear(); heavyNcbar.clear();")
        lines.append("    heavyNb.clear(); heavyNbbar.clear();")
        for pdg, final, nc, ncbar, nb, nbbar in event:
            lines.append(f"    heavyPdg.push_back({pdg});")
            lines.append(f"    heavyIsFinal.push_back({final});")
            lines.append(f"    heavyNc.push_back({nc});")
            lines.append(f"    heavyNcbar.push_back({ncbar});")
            lines.append(f"    heavyNb.push_back({nb});")
            lines.append(f"    heavyNbbar.push_back({nbbar});")
        lines.append("    tree.Fill();")
    return "\n".join(lines)


def _root(*args: str) -> subprocess.CompletedProcess:
    root = shutil.which("root")
    if root is None:
        raise RuntimeError("ROOT is required for the sample-counting test")
    return subprocess.run([root, "-l", "-b", "-q", *args],
                          cwd=ROOT, text=True, capture_output=True, check=False)


def _write_fixture(scratch: Path, skip: str = "") -> Path:
    source = scratch / "write_fixture.C"
    source.write_text(WRITER.format(fills=_fill_block()))
    target = scratch / f"fixture_{skip or 'complete'}.root"
    result = _root(f'{source}("{target}","{skip}")')
    if not target.exists():
        raise AssertionError(
            f"fixture was not written:\n{result.stdout}\n{result.stderr}")
    return target


def test_every_output_number_is_the_hand_computed_one(scratch: Path) -> None:
    fixture = _write_fixture(scratch)
    out = scratch / "counts.json"
    result = _root(f'{MACRO}("{fixture}","{out}","FIXTURE")')
    assert out.exists(), (
        f"the macro wrote no JSON:\n{result.stdout}\n{result.stderr}")

    payload = json.loads(out.read_text())
    assert payload["events"] == EXPECTED_EVENTS, payload["events"]
    assert payload["final_heavy_hadrons"] == EXPECTED_FINAL_HEAVY_HADRONS, \
        payload["final_heavy_hadrons"]
    assert payload["content_sums"]["charm"] == EXPECTED_CHARM_CONTENT, \
        payload["content_sums"]
    assert payload["content_sums"]["beauty"] == EXPECTED_BEAUTY_CONTENT, \
        payload["content_sums"]
    assert payload["species_yields"] == EXPECTED_YIELDS, \
        payload["species_yields"]
    assert payload["tune"] == "FIXTURE"
    assert payload["definitions"]["record"] == "docs2/physics/SAMPLE_COUNTING.md"

    tex = Path(str(out) + ".tex").read_text()
    assert "$N_{\\mathrm{ev}}$ & 3 \\\\" in tex, tex
    # Owner decision O2: the acceptance superscript does not survive.
    assert "^{\\mathrm{acc}}" not in tex, tex
    assert "$N_{c+\\bar c}$ & 4 \\\\" in tex, tex
    assert "$N_{b+\\bar b}$ & 2 \\\\" in tex, tex


def test_the_hidden_charm_record_is_content_only(scratch: Path) -> None:
    """Owner decision O2, executable.

    The J/psi-like record adds two charm quarks to the content sum and appears
    in none of the eight species rows. Asserted as the difference the record
    makes, so a change to either rule shows up here.
    """
    payload = json.loads((scratch / "counts.json").read_text())
    open_charm = payload["species_yields"]["Dminus"] + \
        payload["species_yields"]["Lambdacplus"]
    assert open_charm == 2, open_charm
    assert payload["content_sums"]["charm"] == open_charm + 2, \
        "the hidden-charm state must contribute exactly two charm quarks"


def test_a_missing_branch_is_refused_by_name(scratch: Path) -> None:
    """A count over an absent branch is a silent zero, so it is refused."""
    for branch in BRANCHES:
        fixture = _write_fixture(scratch, skip=branch)
        out = scratch / f"counts_missing_{branch}.json"
        result = _root(f'{MACRO}("{fixture}","{out}","FIXTURE")')
        combined = result.stdout + result.stderr
        assert not out.exists(), f"{branch}: the macro wrote a count anyway"
        assert "GENERATED_SAMPLE_COUNT_REFUSED" in combined, combined
        assert branch in combined, f"{branch} is not named in the refusal"


def main() -> int:
    with tempfile.TemporaryDirectory() as name:
        scratch = Path(name)
        test_every_output_number_is_the_hand_computed_one(scratch)
        test_the_hidden_charm_record_is_content_only(scratch)
        test_a_missing_branch_is_refused_by_name(scratch)
    print("generated-sample counting: 3 hand-computed events, "
          f"{len(BRANCHES)} branch refusals")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
