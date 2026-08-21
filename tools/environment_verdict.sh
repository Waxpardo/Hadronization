#!/bin/bash
# Report whether `make check` used the pinned ROOT and an available PYTHIA.
# Source-only tests remain useful elsewhere, but they do not certify the runtime.
# HF_ALLOW_UNPINNED_ENV=1 makes that limited scope explicit in the transcript.
set -uo pipefail

project_base="${1:-${HADRONIZATION_BASE:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}}"
project_base="${project_base%/}"

want_root=""
want_pythia=""
if [[ -f "${project_base}/config/dependencies.conf" ]]; then
  want_root="$(sed -n 's/^: "\${HF_ROOT_VERSION:=\([^}]*\)}".*/\1/p' \
    "${project_base}/config/dependencies.conf" | head -1)"
  want_pythia="$(sed -n 's/^: "\${HF_PYTHIA8_VERSION:=\([^}]*\)}".*/\1/p' \
    "${project_base}/config/dependencies.conf" | head -1)"
fi
[[ -z "${want_root}" ]] && want_root="(unreadable from config/dependencies.conf)"
[[ -z "${want_pythia}" ]] && want_pythia="(unreadable from config/dependencies.conf)"

have_root="ABSENT"
root_path="not on PATH"
if command -v root >/dev/null 2>&1; then
  root_path="$(command -v root)"
  have_root="$(root-config --version 2>/dev/null || echo 'UNKNOWN')"
fi

pythia="ABSENT"
if command -v pythia8-config >/dev/null 2>&1; then
  pythia="$(pythia8-config --version 2>/dev/null || echo 'present, version unknown')"
fi

cvmfs="ABSENT"
[[ -d /cvmfs/alice.cern.ch ]] && cvmfs="present"

problems=()
[[ "${have_root}" == "ABSENT" ]] && problems+=("ROOT is not on PATH")
[[ "${have_root}" != "ABSENT" && "${have_root}" != "${want_root}" ]] &&
  problems+=("ROOT is ${have_root}, pinned is ${want_root}")
[[ "${pythia}" == "ABSENT" ]] && problems+=("PYTHIA is absent (no pythia8-config)")
[[ "${pythia}" != "ABSENT" && "${pythia}" != "${want_pythia}" ]] &&
  problems+=("PYTHIA is ${pythia}, pinned is ${want_pythia}")

echo
echo "======================================================================"
echo "ENVIRONMENT VERDICT"
echo "======================================================================"
printf '  %-22s %s\n' "ROOT pinned:" "${want_root}"
printf '  %-22s %s   (%s)\n' "ROOT found:" "${have_root}" "${root_path}"
printf '  %-22s %s\n' "PYTHIA pinned:" "${want_pythia}"
printf '  %-22s %s\n' "PYTHIA found:" "${pythia}"
printf '  %-22s %s\n' "CVMFS alice.cern.ch:" "${cvmfs}"
echo "----------------------------------------------------------------------"

if [[ ${#problems[@]} -eq 0 ]]; then
  echo "  VERDICT: PINNED RUNTIME."
  echo
  echo "  Even so, a green suite is a SOURCE-CONTRACT result. It does not run"
  echo "  the 300-file merged product, the current plotting chain, or the"
  echo "  published extraction. See README S'What make check does not certify'."
  echo "======================================================================"
  exit 0
fi

echo "  VERDICT: OFF-PIN RUNTIME -- this host cannot run the pipeline."
for problem in "${problems[@]}"; do
  echo "    - ${problem}"
done
echo
echo "  A green test suite here certifies the SOURCE CONTRACTS only. It does"
echo "  NOT certify the runtime, and it is not a pipeline result:"
echo "    - the ROOT-dependent tests compiled against an unpinned ROOT;"
echo "    - the PYTHIA runtime contract passes vacuously when PYTHIA is absent;"
echo "    - no test runs the merged product, the plotting chain, or the"
echo "      published extraction."
echo
echo "  To proceed anyway -- which is normal for laptop work -- set:"
echo "      HF_ALLOW_UNPINNED_ENV=1 make check"
echo "  so that the concession is explicit and appears in the transcript."
echo "======================================================================"

if [[ "${HF_ALLOW_UNPINNED_ENV:-0}" == "1" ]]; then
  echo "HF_ALLOW_UNPINNED_ENV=1 -- off-pin environment accepted by declaration."
  echo "This run is NOT a pinned-runtime certification."
  exit 0
fi
exit 1
