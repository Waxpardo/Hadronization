#!/bin/bash
# Global setupEnv.sh for HRP_clean (works for Code/ and MasterThesisNikhef)

# IMPORTANT: do NOT use 'set -u' here; ALICE login.sh expects some vars to be unset.
set -e
set -o pipefail

# 1. Get alienv from ALICE CVMFS
if [ -f /cvmfs/alice.cern.ch/etc/login.sh ]; then
  # Temporarily ensure nounset is off in case the parent shell had it
  set +u 2>/dev/null || true
  # shellcheck source=/dev/null
  source /cvmfs/alice.cern.ch/etc/login.sh
else
  echo "ERROR: /cvmfs/alice.cern.ch/etc/login.sh not found."
  exit 1
fi

# 2. Load ROOT and PYTHIA into THIS shell (no subshells)
eval "$(alienv printenv VO_ALICE@ROOT::v6-30-01-alice5-2)"
eval "$(alienv printenv VO_ALICE@pythia::v8311-3)"

if [[ "${SETUPENV_QUIET:-0}" -ne 1 ]]; then
  echo "Environment set:"
  echo "  which root:        $(command -v root || echo 'not found')"
  echo "  which root-config: $(command -v root-config || echo 'not found')"
  echo "  PYTHIA8:           ${PYTHIA8:-'(not set)'}"
fi
