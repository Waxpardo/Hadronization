#!/bin/bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ ! -f "${project_root}/setupEnv.sh" ]]; then
  echo "ERROR: setupEnv.sh is absent from ${project_root}" >&2
  exit 2
fi

# Gate A must run in the same pinned ROOT/PYTHIA environment as production.
# shellcheck source=/dev/null
SETUPENV_QUIET=1 source "${project_root}/setupEnv.sh"

exec python3 "${project_root}/tools/run_publication_gate_a.py" "$@"
