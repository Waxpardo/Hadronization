#!/usr/bin/env python3
"""Generate the A2 submit files from the ORIGINAL production submit file.

Deriving the queue lines from the production .sub rather than rebuilding them
keeps every raw path, raw sha, receipt and receipt sha byte-identical to what
production used. The only fields rewritten are the output directory and the
macro sha -- which are exactly the two things that must change.

PARAMETERIZED 2026-08-13 for the tie-break robustness arm. The first version of
this script lived only on the remote with its variation sha, scratch tree and
output roots hard-coded, so a second variation meant editing constants in an
untracked file -- the same shape of problem as an unversioned gate. The
variation is now named on the command line and looked up in the committed
`config/a2_variations_v1.json`, so a submit file cannot carry a sha that no
registered variation claims.

RESOURCE REQUESTS are the measured ones, not the inherited campaign profile:
the job peaks at ~158 MB and runs ~47 s over 60 completed production runs, and
the inherited 8 GB / 8 GB request only matched slots with 8 GB free.

`--deploy-commit` IS REQUIRED, and that is deliberate. `git archive` extracts no
`.git`, so a tree deployed from a tracked commit cannot be asked which commit it
is: provenance in an archived tree is INJECTED, never discovered, and only the
deployer knows it. The first version of this generator omitted the injection and
all 301 jobs of the first campaign died on ExitCode 128 at
`run_status_analysis.sh` `git rev-parse HEAD`. Making it required means the
omission is a usage error at generation time rather than a held cluster.
"""
import argparse
import hashlib
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
VARIATIONS = REPO / "config/a2_variations_v1.json"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--variation", required=True,
                    help="variation name, as registered in "
                         "config/a2_variations_v1.json")
    ap.add_argument("--scratch", type=pathlib.Path, required=True,
                    help="deployed scratch tree holding the variation macro")
    ap.add_argument("--deploy-commit", required=True,
                    help="the tracked commit the scratch tree was archived "
                         "from, injected as "
                         "HADRONIZATION_DEPLOYED_ANALYSIS_COMMIT. Required: an "
                         "archived tree has no .git, so this cannot be "
                         "discovered by the job and must be stated by the "
                         "deployer.")
    ap.add_argument("--base", type=pathlib.Path, required=True,
                    help="external A2 run root; no site-specific default")
    ap.add_argument("--source-sub", type=pathlib.Path, required=True,
                    help="rendered central analysis submit file")
    ap.add_argument("--suffix", default="",
                    help="appended to the run roots and submit filenames, so a "
                         "second variation cannot overwrite the first's outputs")
    ap.add_argument("--slots", type=int, default=100)
    args = ap.parse_args()

    registry = json.loads(VARIATIONS.read_text())
    if args.variation not in registry["variations"]:
        raise SystemExit(
            f"unknown variation {args.variation!r}. Registered: "
            f"{sorted(registry['variations'])}. Adding one is a reviewable "
            "commit to config/a2_variations_v1.json, not a flag.")
    variation_sha = registry["variations"][args.variation]["macro_sha256"]

    # The deployed macro must BE the registered variation. Checking here means a
    # mismatch is caught before 300 jobs run, not after.
    macro = args.scratch / "AnalysisScripts/status_analysis_THnSparse_qq.C"
    deployed = hashlib.sha256(macro.read_bytes()).hexdigest()
    if deployed != variation_sha:
        raise SystemExit(
            f"deployed macro sha256 does not match the registered variation.\n"
            f"  {macro}\n    deployed:   {deployed}\n"
            f"    registered: {variation_sha}  ({args.variation})")
    print(f"variation {args.variation} sha={variation_sha[:16]}... "
          f"scratch={args.scratch}")

    lines = args.source_sub.read_text().splitlines()
    qidx = next(i for i, l in enumerate(lines) if l.startswith("queue "))
    queue_header = lines[qidx]
    rows = [l for l in lines[qidx + 1:] if l and not l.startswith(")")]

    cols = queue_header[len("queue "):].split(" from ")[0].split(",")
    i_tune, i_slot = cols.index("TUNE"), cols.index("CANONICAL_SLOT")
    i_out, i_macro = cols.index("OUTPUT_DIRECTORY"), cols.index("MACRO_SHA256")

    selected = []
    for row in rows:
        f = row.split(",")
        if len(f) != len(cols):
            raise SystemExit(f"row has {len(f)} fields, expected {len(cols)}")
        if int(f[i_slot]) >= args.slots:
            continue
        selected.append(f)

    per_tune = {}
    for f in selected:
        per_tune.setdefault(f[i_tune], []).append(f)
    for tune, rws in sorted(per_tune.items()):
        if len(rws) != args.slots:
            raise SystemExit(f"{tune}: {len(rws)} rows, expected {args.slots}")
    print("selected:", {t: len(r) for t, r in sorted(per_tune.items())})

    def header(mode, permissive):
        env = f"HADRONIZATION_BASE={args.scratch}"
        if permissive:
            env += " HF_A2_PERMISSIVE=1"
        env += (" HADRONIZATION_DEPLOYED_ANALYSIS_COMMIT="
                f"{args.deploy_commit}")
        logs = args.base / "a2_runs" / mode / "condor_logs"
        return f"""universe = vanilla
executable = {args.scratch}/run_status_analysis.sh
initialdir = {args.scratch}
getenv = False
environment = "{env}"
request_cpus = 1
request_memory = 1024MB
request_disk = 2GB
+UseOS = "el9"
+JobCategory = "long"
log = {logs}/$(TUNE)/slot_$(CANONICAL_SLOT)_$(Cluster)_$(Process).log
output = {logs}/$(TUNE)/slot_$(CANONICAL_SLOT)_$(Cluster)_$(Process).out
error = {logs}/$(TUNE)/slot_$(CANONICAL_SLOT)_$(Cluster)_$(Process).err
should_transfer_files = NO
max_retries = 0
on_exit_hold = (ExitBySignal == True) || (ExitCode != 0)
arguments = $(RAW_PATH) $(OUTPUT_DIRECTORY) $(CAMPAIGN) $(TUNE) $(LOGICAL_ID) $(RAW_SHA256) $(ANALYSIS_COMMIT) $(MACRO_SHA256) $(PURPOSE) $(MANIFEST_SHA256) $(RAW_VALIDATION_RECEIPT) $(RAW_VALIDATION_RECEIPT_SHA256)
{queue_header}"""

    def emit(path, mode, permissive, rows_in):
        out = [header(mode, permissive)]
        for f in rows_in:
            g = list(f)
            slot = int(g[i_slot])
            g[i_out] = str(args.base / "a2_runs" / mode / g[i_tune]
                           / f"slot_{slot:03d}")
            g[i_macro] = variation_sha
            out.append(",".join(g))
        out.append(")")
        pathlib.Path(path).write_text("\n".join(out) + "\n")
        print(f"wrote {path}: {len(rows_in)} jobs")

    reg_mode = f"regression{args.suffix}"
    perm_mode = f"permissive{args.suffix}"

    # Regression: ONE job, permissive OFF, MONASH slot_000.
    reg = [f for f in selected if f[i_tune] == "MONASH" and int(f[i_slot]) == 0]
    emit(args.base / f"a2_regression{args.suffix}.sub", reg_mode, False, reg)
    # The measurement: 300 jobs, permissive ON.
    emit(args.base / f"a2_permissive{args.suffix}.sub", perm_mode, True, selected)

    # Log dirs must exist -- Condor will not create them and the job is held if
    # it cannot write its log.
    for mode, rws in ((reg_mode, reg), (perm_mode, selected)):
        for tune in sorted({f[i_tune] for f in rws}):
            (args.base / "a2_runs" / mode / "condor_logs" / tune).mkdir(
                parents=True, exist_ok=True)
    print("log dirs ready")
    return 0


if __name__ == "__main__":
    sys.exit(main())
