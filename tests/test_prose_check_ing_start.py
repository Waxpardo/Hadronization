#!/usr/bin/env python3
"""The ING-START check must read grammar, not the last three letters.

WHY THIS EXISTS. `tools/prose_check.py` flags a sentence that opens with a
gerund, because that shape hides the agent: "Lowering the axis would have needed
six decades" never says who lowers it.

The check finds the shape by looking for a first word that ends in "ing". The
suffix is not the grammar. "Nothing else changed" opens with a pronoun and names
its agent, and the checker flagged it in `docs/FIGURE_INVENTORY.md` 3.1d. The
same suffix catches nouns (king, thing, string, spring, wing), the preposition
"during", and bare imperatives whose stem ends in "ing" (bring, ring, sing). The
standard ASKS for the imperative, so flagging those inverts the rule.

A stoplist of those first words closes the false positive. This test pins both
directions, because a stoplist that swallowed real gerunds would be worse than
the flag it removes.

MUTATION EVIDENCE, recorded 2026-08-18. Emptying ING_START_STOPLIST makes the
first case fail:
    NOT-FLAGGED case wrongly flagged: Nothing else changed.
"""

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "tools" / "prose_check.py"

# Sentences that must NOT flag. Each opens with a word ending in "ing" that is
# not a gerund.
CLEAN = [
    "Nothing else changed.",
    "Something else changed.",
    "Everything else changed.",
    "During the render the node stayed quiet.",
    "Bring the file to the node.",
    "Ring the node before you submit.",
    "String comparison found the mismatch.",
]

# Sentences that MUST flag. Each opens with a real gerund.
GERUND = [
    "Running the merge takes one hour.",
    "Lowering the axis would have needed six decades.",
    "Ringing the node twice wastes a pass.",
]


def run(text):
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as fh:
        fh.write(text + "\n")
        path = fh.name
    result = subprocess.run([sys.executable, str(CHECKER), path],
                            capture_output=True, text=True)
    Path(path).unlink()
    return result.stdout + result.stderr


def main() -> int:
    errors = 0

    for sentence in CLEAN:
        out = run(sentence)
        if "ING-START" in out:
            print(f"NOT-FLAGGED case wrongly flagged: {sentence}")
            errors += 1

    for sentence in GERUND:
        out = run(sentence)
        if "ING-START" not in out:
            print(f"GERUND case missed: {sentence}")
            errors += 1

    print(f"PROSE_CHECK_ING_START clean={len(CLEAN)} gerund={len(GERUND)} "
          f"errors={errors} status=" + ("PASS" if not errors else "FAIL"))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
