#!/usr/bin/env python3
"""A failed boundary-receipt gate must publish nothing.

`PolishProposal.mixed_preamendment_20260817T224548` is a directory that holds
some files from a rejected run and some from an accepted one. It exists because
writeCanvasToFiles wrote straight into the published directory and the receipt
gate ran afterwards, so a throwing gate landed on an already-rewritten
directory. A digest taken from such a directory is worse than no digest: it is
indistinguishable from a good one.

plotting/StagedOutputs.h moves gate-guarded outputs to a staging directory
beside the destination and promotes them only once the gate has passed. This
test compiles that header and drives it through both outcomes.

The header is deliberately ROOT-free so this costs a plain g++ invocation.
"""

import os
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HEADER = ROOT / "plotting" / "StagedOutputs.h"

DRIVER = r"""
#include "StagedOutputs.h"

#include <cstdio>
#include <fstream>
#include <iostream>
#include <string>

using Hadronization::StagedOutputs::Staging;
using Hadronization::StagedOutputs::StagingDirFor;
using Hadronization::StagedOutputs::MakeDirectories;
using Hadronization::StagedOutputs::EntriesOf;

namespace {

void Write(const std::string& path, const std::string& text)
{
  std::ofstream out(path);
  out << text;
}

std::string Read(const std::string& path)
{
  std::ifstream in(path);
  if (!in) return "<absent>";
  std::string all((std::istreambuf_iterator<char>(in)),
                  std::istreambuf_iterator<char>());
  return all;
}

// Stands in for the run: stage the canvases, then consult the gate.
// gatePasses=false models WriteMultiplicityBoundaryReceipt throwing.
void RunOnce(Staging& staging, const std::string& dest, const std::string& body,
             bool gatePasses)
{
  const std::string stage = staging.Stage(dest);
  Write(stage + "/canvas_PNG.png", body);
  Write(stage + "/canvas_PDF.pdf", body);
  Write(stage + "/canvas_MACRO.C", body);
  if (!gatePasses) {
    // The gate threw. Control never reaches Promote(); the staging is simply
    // abandoned, exactly as an exception would abandon it.
    return;
  }
  staging.Promote();
}

int failures = 0;
void Check(bool ok, const std::string& what)
{
  if (!ok) { std::cout << "FAIL: " << what << "\n"; ++failures; }
}

}  // namespace

int main(int argc, char** argv)
{
  if (argc < 2) { std::cerr << "need a scratch dir\n"; return 2; }
  const std::string base = argv[1];
  const std::string dest = base + "/PolishProposal";

  // A previously published, accepted run.
  MakeDirectories(dest);
  Write(dest + "/canvas_PNG.png", "ACCEPTED");
  Write(dest + "/canvas_PDF.pdf", "ACCEPTED");
  Write(dest + "/canvas_MACRO.C", "ACCEPTED");

  // ---- 1. gate FAILS -------------------------------------------------------
  {
    Staging staging;
    RunOnce(staging, dest, "REJECTED", /*gatePasses=*/false);

    Check(Read(dest + "/canvas_PNG.png") == "ACCEPTED",
          "published PNG must be untouched by a rejected run");
    Check(Read(dest + "/canvas_PDF.pdf") == "ACCEPTED",
          "published PDF must be untouched by a rejected run");
    Check(Read(dest + "/canvas_MACRO.C") == "ACCEPTED",
          "published .C must be untouched by a rejected run");
    Check(EntriesOf(dest).size() == 3,
          "a rejected run must not add files to the published directory");
    // The rejected bytes exist, but only in staging -- never mixed in.
    Check(Read(StagingDirFor(dest) + "/canvas_PNG.png") == "REJECTED",
          "rejected output should sit in staging, not nowhere");
  }

  // ---- 2. gate PASSES ------------------------------------------------------
  {
    Staging staging;
    RunOnce(staging, dest, "PROMOTED", /*gatePasses=*/true);

    Check(Read(dest + "/canvas_PNG.png") == "PROMOTED",
          "a passing run must publish its PNG");
    Check(Read(dest + "/canvas_PDF.pdf") == "PROMOTED",
          "a passing run must publish its PDF");
    Check(Read(dest + "/canvas_MACRO.C") == "PROMOTED",
          "a passing run must publish its .C");
    Check(EntriesOf(dest).size() == 3,
          "promotion must not leave extra files behind");
    Check(EntriesOf(StagingDirFor(dest)).empty(),
          "staging must be emptied by promotion");
  }

  // ---- 3. a rejected run AFTER a good one still publishes nothing ----------
  {
    Staging staging;
    RunOnce(staging, dest, "REJECTED_AGAIN", /*gatePasses=*/false);
    Check(Read(dest + "/canvas_PNG.png") == "PROMOTED",
          "a later rejected run must not overwrite the published figure");
  }

  // ---- 4. stale staging from an aborted run is not carried into a promote --
  {
    Staging staging;
    const std::string stage = staging.Stage(dest);
    // Only one of the three is rewritten this run.
    Write(stage + "/canvas_PNG.png", "FRESH");
    staging.Promote();
    Check(Read(dest + "/canvas_PNG.png") == "FRESH",
          "the fresh file is published");
    Check(Read(dest + "/canvas_PDF.pdf") == "PROMOTED",
          "untouched published files survive a partial promote");
    // The abandoned REJECTED_AGAIN staging must NOT have been promoted here.
    Check(Read(dest + "/canvas_MACRO.C") == "PROMOTED",
          "an earlier aborted run's staging must never be promoted later");
  }

  if (failures == 0) std::cout << "staged-outputs tests passed\n";
  return failures == 0 ? 0 : 1;
}
"""


def main() -> int:
    if not HEADER.exists():
        print(f"missing {HEADER}", file=sys.stderr)
        return 1

    compiler = shutil.which("g++") or shutil.which("clang++")
    if compiler is None:
        print("SKIP: no C++ compiler available")
        return 0

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        source = tmp_path / "driver.cpp"
        source.write_text(DRIVER)
        binary = tmp_path / "driver"

        compile_cmd = [
            compiler,
            "-std=c++17",
            "-Wall",
            "-Wextra",
            f"-I{HEADER.parent}",
            str(source),
            "-o",
            str(binary),
        ]
        compiled = subprocess.run(
            compile_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        if compiled.returncode != 0:
            print("compilation of the staging driver failed:")
            print(f"  {shlex.join(compile_cmd)}")
            print(compiled.stdout.decode(errors="replace"))
            return 1

        scratch = tmp_path / "scratch"
        scratch.mkdir()
        run = subprocess.run(
            [str(binary), str(scratch)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        output = run.stdout.decode(errors="replace")
        if run.returncode != 0:
            print("staged-outputs behaviour is wrong:")
            print(output)
            return 1
        print(output.strip())

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
