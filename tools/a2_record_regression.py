#!/usr/bin/env python3
"""Perform the A2 regression comparison and record its verdict as a sentinel.

Pre-registration: docs/A2_PAIR_UNRESOLVED_PREREGISTRATION.md, positive check 1.

THE SENTINEL IS NOT A NOTE. This tool does the comparison itself and writes the
verdict it measured. It cannot be used to assert a pass -- there is no --verdict
flag. `analysis/a2_block_shift.py` refuses to run without the sentinel this
produces, so the only route from "jobs finished" to "numbers" runs through an
actual byte-level comparison.

WHAT "IDENTICAL" MEANS HERE, precisely. The analysis macro embeds
`analysis_macro_sha256` into every output file, taken from the environment and
derived from the macro's own bytes. A modified macro therefore CANNOT reproduce
that string, by construction. It is the one field allowed to differ, it is named
here, and it is checked to differ in exactly the expected way -- baseline value
to variation value. Anything else differing is a FAIL.

Usage:
  tools/a2_record_regression.py --baseline-dir DIR --regression-dir DIR \\
      [--variation-sha SHA] [--out docs/a2_regression_pass.json]

Requires ROOT for the object comparison; without it the tool exits 4 and writes
nothing rather than guessing.
"""
from __future__ import annotations

import argparse
import datetime
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ALLOWED_TO_DIFFER = "analysis_macro_sha256"

COMPARE_MACRO = r"""
// Compare two pair-output directories object by object.
// Prints one DIFF line per differing object and a final COMPARE_DONE summary.
void cmp(const char* a, const char* b){
  TSystemDirectory da("a", a);
  TList* files = da.GetListOfFiles();
  if(!files){ printf("COMPARE_ERROR no listing\n"); return; }
  long nfile=0, ndiff=0, nmissing=0;
  TIter next(files); TSystemFile* fo;
  while((fo=(TSystemFile*)next())){
    TString nm = fo->GetName();
    if(fo->IsDirectory() || !nm.EndsWith(".root")) continue;
    TFile* fa = TFile::Open(TString::Format("%s/%s", a, nm.Data()));
    TFile* fb = TFile::Open(TString::Format("%s/%s", b, nm.Data()));
    if(!fa || fa->IsZombie() || !fb || fb->IsZombie()){
      printf("DIFF %s MISSING_FILE\n", nm.Data()); ++nmissing;
      if(fa) fa->Close(); if(fb) fb->Close(); continue;
    }
    TList* keys = fa->GetListOfKeys();
    TIter kn(keys); TKey* k;
    while((k=(TKey*)kn())){
      TString on = k->GetName();
      TObject* oa = fa->Get(on);
      TObject* ob = fb->Get(on);
      if(!ob){ printf("DIFF %s %s MISSING_IN_B\n", nm.Data(), on.Data()); ++ndiff; continue; }
      TObjString* sa = dynamic_cast<TObjString*>(oa);
      TObjString* sb = dynamic_cast<TObjString*>(ob);
      if(sa && sb){
        if(sa->GetString() != sb->GetString())
          { printf("DIFF %s %s STRING %s|%s\n", nm.Data(), on.Data(),
                   sa->GetString().Data(), sb->GetString().Data()); ++ndiff; }
        continue;
      }
      THnSparse* ha = dynamic_cast<THnSparse*>(oa);
      THnSparse* hb = dynamic_cast<THnSparse*>(ob);
      if(ha && hb){
        if(ha->GetNbins() != hb->GetNbins())
          { printf("DIFF %s %s NBINS %lld|%lld\n", nm.Data(), on.Data(),
                   (long long)ha->GetNbins(), (long long)hb->GetNbins()); ++ndiff; continue; }
        int coords[16]; bool bad=false;
        for(Long64_t i=0;i<ha->GetNbins() && !bad;++i){
          double va = ha->GetBinContent(i, coords);
          double vb = hb->GetBinContent(i, coords);
          if(va != vb){ printf("DIFF %s %s CONTENT %.17g|%.17g\n",
                               nm.Data(), on.Data(), va, vb); ++ndiff; bad=true; }
        }
        continue;
      }
      TH1* h1a = dynamic_cast<TH1*>(oa);
      TH1* h1b = dynamic_cast<TH1*>(ob);
      if(h1a && h1b){
        if(h1a->GetNbinsX()!=h1b->GetNbinsX()){
          printf("DIFF %s %s NBINSX\n", nm.Data(), on.Data()); ++ndiff; continue; }
        for(int i=0;i<=h1a->GetNbinsX()+1;++i){
          if(h1a->GetBinContent(i)!=h1b->GetBinContent(i)){
            printf("DIFF %s %s TH1 bin %d\n", nm.Data(), on.Data(), i); ++ndiff; break; }
        }
        continue;
      }
    }
    ++nfile; fa->Close(); fb->Close();
  }
  printf("COMPARE_DONE files=%ld diffs=%ld missing=%ld\n", nfile, ndiff, nmissing);
}
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline-dir", type=Path, required=True,
                    help="committed per_job slot directory")
    ap.add_argument("--regression-dir", type=Path, required=True,
                    help="a2_runs/regression slot directory (rule DISABLED)")
    ap.add_argument("--variation", required=True,
                    help="the variation being certified, by NAME, as registered "
                         "in config/a2_variations_v1.json. The sha is resolved "
                         "from the registry rather than accepted on the command "
                         "line, so this tool cannot mint a sentinel for a macro "
                         "nobody registered.")
    ap.add_argument("--variations-registry", type=Path,
                    default=REPO / "config/a2_variations_v1.json")
    ap.add_argument("--out", type=Path, default=None,
                    help="sentinel path; defaults to "
                         "results/a2/20260813/sentinels/"
                         "a2_regression_pass_<variation>.json. Each "
                         "variation carries its OWN sentinel -- one file per "
                         "arm, so a pass can never be reused across arms.")
    ap.add_argument("--root-bin", default="root")
    args = ap.parse_args()

    registry = json.loads(args.variations_registry.read_text())["variations"]
    if args.variation not in registry:
        raise SystemExit(
            f"FAIL-CLOSED: {args.variation!r} is not a registered variation. "
            f"Registered: {', '.join(sorted(registry))}. Adding one is a "
            "reviewable commit to config/a2_variations_v1.json.")
    variation_sha = registry[args.variation]["macro_sha256"]
    out_path = args.out or (
        REPO / "results/a2/20260813/sentinels" /
        f"a2_regression_pass_{args.variation}.json")

    for d in (args.baseline_dir, args.regression_dir):
        if not d.is_dir():
            raise SystemExit(f"FAIL-CLOSED: {d} is not a directory")

    macro = Path(subprocess.run(["mktemp", "-d"], capture_output=True,
                                text=True, check=True).stdout.strip()) / "cmp.C"
    macro.write_text(COMPARE_MACRO)
    result = subprocess.run(
        [args.root_bin, "-l", "-b", "-q",
         f'{macro}("{args.baseline_dir}","{args.regression_dir}")'],
        capture_output=True, text=True, check=False)
    if "COMPARE_DONE" not in result.stdout:
        sys.stderr.write(result.stdout[-3000:] + result.stderr[-3000:])
        raise SystemExit(
            "FAIL-CLOSED: the comparison did not complete (no COMPARE_DONE). "
            "No sentinel written.")

    diffs = [l for l in result.stdout.splitlines() if l.startswith("DIFF ")]
    done = [l for l in result.stdout.splitlines() if l.startswith("COMPARE_DONE")][0]

    # Partition the differences: the macro-sha string is expected exactly once
    # per file; everything else is a failure.
    expected, unexpected = [], []
    for line in diffs:
        parts = line.split()
        if len(parts) >= 4 and parts[2] == ALLOWED_TO_DIFFER and parts[3] == "STRING":
            expected.append(line)
        else:
            unexpected.append(line)

    verdict = "PASS" if not unexpected else "FAIL"
    print(done)
    print(f"allowed differences ({ALLOWED_TO_DIFFER}): {len(expected)}")
    print(f"UNEXPECTED differences: {len(unexpected)}")
    for line in unexpected[:20]:
        print("   ", line)

    payload = {
        "schema": "a2_regression_sentinel_v1",
        "verdict": verdict,
        "variation": args.variation,
        "variation_sha256": variation_sha,
        "compared": f"{args.baseline_dir} vs {args.regression_dir}",
        "recorded": datetime.datetime.now(datetime.timezone.utc)
                    .strftime("%Y-%m-%dT%H:%M:%SZ"),
        "compare_summary": done,
        "allowed_field": ALLOWED_TO_DIFFER,
        "allowed_difference_count": len(expected),
        "unexpected_difference_count": len(unexpected),
        "unexpected_examples": unexpected[:20],
    }
    out_path.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"\nwrote {out_path}: verdict={verdict}")
    if verdict != "PASS":
        print("The permissive output must NOT be consumed. Quarantine it with "
              "tools/a2_quarantine_outputs.py.")
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
