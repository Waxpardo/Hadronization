#!/usr/bin/env python3
"""Build the LARGEST-heavyIndex tie-break variation from the smallest-index one.

WHY THIS EXISTS. The A2 pre-registration picks the winner of a contested hard
index by SMALLEST `heavyIndex`, chosen because it is deterministic and
uncorrelated with pT. The measured Delta exceeds the pre-registered negligible
threshold for the JUNCTIONS and CLOSEPACKING configuration bundles, and the
pre-registration's own
robustness clause then asks for the opposite tie-break: if the multiplicity
SHAPE survives flipping the direction, the arbitrariness of the choice is
bounded and the systematic stands as measured.

WHY IT PATCHES THE VARIATION MACRO AND NOT THE FROZEN BASELINE. Deriving the
largest-index macro from the already-verified smallest-index macro makes the
diff between the two arms of the robustness check exactly one comparison
operator and its comment. Rebuilding it from the frozen baseline through
`patch_variation.py` would produce the same physics but a diff of 121 lines
against the arm it is being compared with, and `patch_variation.py` on the
remote is in any case STALE -- it still carries the per-job restoration throw
that was removed in `a4df31e6`.

The source sha is ASSERTED, not assumed: a patch applied to the wrong macro is
how a robustness check silently becomes a re-run of something else.
"""
import hashlib
import sys
from pathlib import Path

# The smallest-index variation this is derived from. Registered in
# config/a2_variations_v1.json as `permissive_smallest_index`.
SOURCE_SHA256 = (
    "a4df31e6b6da5098d40b793a0c3616957457b326bcef48538bbe271b05f38553")

OLD = """    // The winner is the row with the SMALLEST heavyIndex -- deterministic, and
    // deliberately uncorrelated with pT so the tie-break cannot inflate the
    // measured shift by preferentially restoring rows that pass the trigger pT
    // cut. heavyIndex is unique within an event.
    std::size_t winner = rows.front();
    for (const std::size_t row : rows) {
      if (heavyIndex[row] < heavyIndex[winner]) winner = row;
    }"""

NEW = """    // The winner is the row with the LARGEST heavyIndex. This is the A2
    // ROBUSTNESS ARM: it is the same rule with the tie-break direction
    // reversed, and it exists to show that the measured multiplicity
    // dependence is a property of restoring one claimant, not an artefact of
    // WHICH claimant the pre-registration happened to name. Like the smallest
    // -index rule it is deterministic and uncorrelated with pT, so neither
    // direction preferentially restores rows that pass the trigger pT cut.
    // heavyIndex is unique within an event, so the winner is unique.
    std::size_t winner = rows.front();
    for (const std::size_t row : rows) {
      if (heavyIndex[row] > heavyIndex[winner]) winner = row;
    }"""


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        print("usage: a2_make_largest_index_variation.py SRC_MACRO DST_MACRO",
              file=sys.stderr)
        return 2

    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    raw = src.read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    if got != SOURCE_SHA256:
        print(f"REFUSING: source macro sha256 is {got}\n"
              f"          expected                {SOURCE_SHA256}\n"
              "This tool derives the largest-index arm from the verified "
              "smallest-index macro. Patching anything else would produce a "
              "variation whose diff against its comparison arm is unknown.",
              file=sys.stderr)
        return 3

    text = raw.decode()
    n = text.count(OLD)
    if n != 1:
        print(f"REFUSING: winner-selection anchor found {n} times, need exactly "
              "1. A patch that silently no-ops is how a variation becomes a "
              "re-run of the arm it is supposed to differ from.", file=sys.stderr)
        return 4

    out = text.replace(OLD, NEW)
    # The two macros must differ in the comparison, not merely in prose.
    if out.count("heavyIndex[row] > heavyIndex[winner]") != 1 or \
       "heavyIndex[row] < heavyIndex[winner]" in out:
        print("REFUSING: the comparison operator was not flipped exactly once.",
              file=sys.stderr)
        return 5

    dst.write_text(out)
    new_sha = hashlib.sha256(dst.read_bytes()).hexdigest()
    print(f"PATCHED  {src} -> {dst}")
    print(f"  source sha256 {got}")
    print(f"  result sha256 {new_sha}")
    print("  diff: the winner comparison operator, and the comment that "
          "explains it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
