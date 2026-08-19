#!/bin/bash
# Run the Python contract tests.
#
# This exists as a script rather than a Makefile loop for one reason: the
# environment. Five of these tests compile or run a ROOT macro and raise
# "ROOT is required" rather than skipping, so they need setupEnv.sh sourced.
# Sourcing inside a multi-line make recipe does not work -- the environment is
# lost across the backslash continuations, with `;`, with `&&`, and with
# .ONESHELL alike, though the identical prologue works in a single-line recipe.
# The Makefile already delegates `doctor` and `build` to scripts for their own
# reasons; this follows that pattern and sidesteps the problem entirely.
#
# The failure this prevents is a quiet one: without ROOT, `make check` reports
# 21/21 on a laptop and 16/21 on the cluster for the same commit -- and the
# machine that cannot run the pipeline is the one that looks healthy.

set -uo pipefail

project_base="${1:-${HADRONIZATION_BASE:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}}"
project_base="${project_base%/}"

# Non-fatal: a machine with no CVMFS still runs the standard-library-only
# tests exactly as before, it just skips the ROOT-dependent ones.
if [[ -f "${project_base}/setupEnv.sh" ]]; then
  # shellcheck source=/dev/null
  SETUPENV_QUIET=1 source "${project_base}/setupEnv.sh" >/dev/null 2>&1 || true
fi

if command -v root >/dev/null 2>&1; then
  echo "  ROOT: $(command -v root)"
else
  echo "  ROOT: not found -- the 5 ROOT-dependent tests will fail, not skip."
  echo "        This is expected off-cluster; it is NOT a green run."
fi

failed=0
total=0
for t in "${project_base}"/tests/test_*.py; do
  total=$((total + 1))
  # HADRONIZATION_BASE is unset per test: runCondorJob.sh refuses to inherit
  # campaign control from the environment and the tests assert that.
  # setupEnv.sh exports it, which is exactly why this `env -u` is needed.
  if env -u HADRONIZATION_BASE "${PYTHON:-python3}" "${t}" >/dev/null 2>&1; then
    printf '  PASS %s\n' "$(basename "${t}")"
  else
    printf '  FAIL %s\n' "$(basename "${t}")"
    failed=$((failed + 1))
  fi
done

echo "  $((total - failed))/${total} passed"
exit $(( failed == 0 ? 0 : 1 ))
