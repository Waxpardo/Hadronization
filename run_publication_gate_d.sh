#!/bin/bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export HADRONIZATION_BASE="${HADRONIZATION_BASE:-${project_root}}"

if [[ -f "${project_root}/setupEnv.sh" ]]; then
  export SETUPENV_QUIET="${SETUPENV_QUIET:-1}"
  # shellcheck disable=SC1091
  source "${project_root}/setupEnv.sh"
fi

exec python3 "${project_root}/tools/run_publication_gate_d.py" "$@"
