#!/bin/bash
# Global setupEnv.sh for Hadronization

# IMPORTANT: do NOT use 'set -e' or 'set -u' here; this script is sourced, so
# set -e would exit the parent shell on any error, and ALICE login.sh expects
# some vars to be unset.
setupenv_restore_errexit=0
setupenv_restore_nounset=0
case "$-" in
  *e*)
    setupenv_restore_errexit=1
    set +e
    ;;
esac
case "$-" in
  *u*)
    setupenv_restore_nounset=1
    set +u
    ;;
esac

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -n "${HADRONIZATION_BASE:-}" && -d "${HADRONIZATION_BASE%/}/PlottingScripts" ]]; then
  HADRONIZATION_BASE="${HADRONIZATION_BASE%/}"
elif [ -f "${SCRIPT_DIR}/base_path.txt" ]; then
  HADRONIZATION_BASE="$(cat "${SCRIPT_DIR}/base_path.txt")"
else
  HADRONIZATION_BASE="${SCRIPT_DIR}"
fi
HADRONIZATION_BASE="${HADRONIZATION_BASE%/}"
export HADRONIZATION_BASE

# 1. Get alienv from ALICE CVMFS (only available on the cluster)
if [ -f /cvmfs/alice.cern.ch/etc/login.sh ]; then
  # Temporarily ensure nounset is off in case the parent shell had it
  set +u 2>/dev/null || true
  # shellcheck source=/dev/null
  source /cvmfs/alice.cern.ch/etc/login.sh

  # 2. Load ROOT and PYTHIA into THIS shell (no subshells)
  eval "$(alienv printenv VO_ALICE@ROOT::v6-30-01-alice5-2 2>/dev/null)"
  eval "$(alienv printenv VO_ALICE@pythia::v8315-alice1-23 2>/dev/null)"

  # Some Nikhef non-interactive shells cannot initialise alienv's Tcl
  # interpreter. Keep batch plotting reproducible by falling back to the same
  # EL9 ROOT build and its runtime dependencies directly from CVMFS.
  if ! command -v root >/dev/null 2>&1; then
    gcc_package="/cvmfs/alice.cern.ch/el9-x86_64/Packages/GCC-Toolchain/v12.2.0-alice1-9"
    root_package="/cvmfs/alice.cern.ch/el9-x86_64/Packages/ROOT/v6-30-01-alice5-2"
    root_runtime_libs="${gcc_package}/lib64"
    root_runtime_libs="${root_runtime_libs}:/cvmfs/alice.cern.ch/el9-x86_64/Packages/TBB/v2021.5.0-13/lib"
    root_runtime_libs="${root_runtime_libs}:/cvmfs/alice.cern.ch/el9-x86_64/Packages/OpenSSL/v1.1.1m-7/lib"
    root_runtime_libs="${root_runtime_libs}:/cvmfs/alice.cern.ch/el9-x86_64/Packages/GSL/v1.16-10/lib"
    root_runtime_libs="${root_runtime_libs}:/cvmfs/alice.cern.ch/el9-x86_64/Packages/FreeType/v2.10.1-12/lib"
    root_runtime_libs="${root_runtime_libs}:/cvmfs/alice.cern.ch/el9-x86_64/Packages/libpng/v1.6.34-13/lib"
    root_runtime_libs="${root_runtime_libs}:/cvmfs/alice.cern.ch/el9-x86_64/Packages/lzma/v5.2.3-9/lib"
    root_runtime_libs="${root_runtime_libs}:/cvmfs/alice.cern.ch/el9-x86_64/Packages/libxml2/v2.9.3-9/lib"
    root_runtime_libs="${root_runtime_libs}:/cvmfs/alice.cern.ch/el9-x86_64/Packages/XRootD/v5.6.6-11/lib"
    root_runtime_libs="${root_runtime_libs}:/cvmfs/alice.cern.ch/el9-x86_64/Packages/protobuf/v21.9-13/lib"
    root_runtime_libs="${root_runtime_libs}:/cvmfs/alice.cern.ch/el9-x86_64/Packages/FFTW3/v3.3.9-14/lib"
    export LD_LIBRARY_PATH="${root_runtime_libs}:${root_package}/lib${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}"
    export PATH="${gcc_package}/bin:${PATH}"
    export ROOT_DYN_PATH="${root_package}/lib"
    # shellcheck source=/dev/null
    source "${root_package}/bin/thisroot.sh"
  fi

  # alienv can fail to initialise its Tcl interpreter in non-interactive
  # Nikhef shells.  In that case, pin the same PYTHIA 8.315 CVMFS package
  # directly so builds and Condor wrappers do not depend on an interactive
  # login having populated PYTHIA8 first.
  if [[ -z "${PYTHIA8:-}" ]] || ! command -v pythia8-config >/dev/null 2>&1; then
    pythia_package="/cvmfs/alice.cern.ch/el9-x86_64/Packages/pythia/v8315-alice1-23"
    if [[ ! -x "${pythia_package}/bin/pythia8-config" ]]; then
      echo "ERROR: pinned PYTHIA package is unavailable: ${pythia_package}" >&2
      return 1 2>/dev/null || exit 1
    fi
    export PYTHIA8="${pythia_package}"
    export PATH="${pythia_package}/bin:${PATH}"
    export LD_LIBRARY_PATH="${pythia_package}/lib${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}"
  fi
else
  echo "WARNING: CVMFS not available — ROOT and PYTHIA not loaded via alienv."
  echo "         Run this script on the Nikhef cluster to get the full environment."
fi

if [[ "${SETUPENV_QUIET:-0}" -ne 1 ]]; then
  echo "Environment set:"
  echo "  which root:        $(command -v root || echo 'not found')"
  echo "  which root-config: $(command -v root-config || echo 'not found')"
  echo "  PYTHIA8:           ${PYTHIA8:-'(not set)'}"
fi

if [[ "${setupenv_restore_errexit}" -eq 1 ]]; then
  set -e
fi
if [[ "${setupenv_restore_nounset}" -eq 1 ]]; then
  set -u
fi
