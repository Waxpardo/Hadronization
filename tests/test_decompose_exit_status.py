#!/usr/bin/env python3
"""Require decompose_with_block_sems.py to report both I2 and I3 by status.

An I2 failure must not exit successfully when I3 passes.

I2's binomial null is known to be
misspecified for event-clustered pair counts (docs/MONASH_CENTRAL_TABLE.md S3:
353 flags in 880 comparisons, ~5x overdispersion), so real runs legitimately
flag. The fix is that flagging must reach the caller, with an EXPLICIT
`--i2-advisory` opt-out that appears in the command line and therefore in the
transcript. Silence is what is forbidden, not flagging.

Three checks:
  1. I3 clean + I2 clean            -> exit 0;
  2. I3 clean + I2 flags            -> exit 4   (this is what fails pre-fix);
  3. I3 clean + I2 flags + advisory -> exit 0, and says so in the output.

"""
import csv
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TOOL = REPO / "extraction/decompose_with_block_sems.py"
SOURCE = REPO / "AnalysisScripts/anchors/merged_monash_replicated/per_species.csv"

failures = []


def check(label, condition, detail=""):
    if condition:
        print(f"  PASS {label}")
    else:
        print(f"  FAIL {label} {detail}")
        failures.append(label)


def write_csv(path: Path, totals, cats):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["ordinal", "category", "category_name", "total"])
        for ordinal in sorted(totals):
            cat, name = cats[ordinal]
            w.writerow([ordinal, cat, name, repr(float(totals[ordinal]))])


def build(rundir: Path, skew: bool):
    """Ten blocks that sum EXACTLY to central (I3 always passes).

    With skew=False every block is an even tenth, so block-vs-central sits at
    the expected scale of 10 and I2 is quiet. With skew=True block 1 carries
    ~5 % instead of 10 %, which I2's z-test flags hard -- while the blocks
    still sum to the central exactly, so I3 stays clean and the two checks are
    genuinely independent.
    """
    rows = list(csv.DictReader(SOURCE.open()))
    cats = {int(r["ordinal"]): (r["category"], r["category_name"]) for r in rows}
    central = {int(r["ordinal"]): int(float(r["total"])) for r in rows}
    blocks = [dict.fromkeys(central, 0) for _ in range(10)]
    for ordinal, value in central.items():
        first = value // 20 if skew else value // 10
        rest = value - first
        share = rest // 9
        blocks[0][ordinal] = first
        for i in range(1, 10):
            blocks[i][ordinal] = share
        blocks[9][ordinal] += rest - share * 9
    for ordinal in central:
        assert sum(b[ordinal] for b in blocks) == central[ordinal]
    write_csv(rundir / "central/per_species.csv", central, cats)
    for i, b in enumerate(blocks, 1):
        write_csv(rundir / f"block_{i}/per_species.csv", b, cats)


def run(rundir: Path, *extra):
    return subprocess.run(
        [sys.executable, str(TOOL), str(rundir), "--tune", "TEST", *extra],
        capture_output=True, text=True)


with tempfile.TemporaryDirectory() as tmp:
    clean, skewed = Path(tmp) / "clean", Path(tmp) / "skewed"
    build(clean, skew=False)
    build(skewed, skew=True)

    r = run(clean)
    check("I3 clean + I2 clean exits 0", r.returncode == 0,
          f"rc={r.returncode}\n{r.stdout[-600:]}{r.stderr[-400:]}")
    check("clean run reports I3 PASS", "I3 block-sum == central : PASS" in r.stdout,
          r.stdout[:200])

    r = run(skewed)
    check("I3 clean + I2 flags exits 4 (THE REGRESSION)", r.returncode == 4,
          f"rc={r.returncode} -- pre-fix this was 0\n{r.stdout[-600:]}")
    check("I2 failure names itself in the output", "I2 FAIL" in r.stdout,
          r.stdout[-300:])
    check("I3 is still clean in the skewed fixture, so the two are independent",
          "I3 block-sum == central : PASS" in r.stdout, r.stdout[:200])

    r = run(skewed, "--i2-advisory")
    check("--i2-advisory downgrades to 0", r.returncode == 0,
          f"rc={r.returncode}\n{r.stdout[-600:]}")
    check("advisory declares itself rather than passing silently",
          "I2 ADVISORY" in r.stdout and "not a pass" in r.stdout, r.stdout[-300:])

print(f"\n{len(failures)} failure(s)")
sys.exit(1 if failures else 0)
