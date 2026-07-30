#!/bin/bash
set -euo pipefail

project_base="${1:-${HADRONIZATION_BASE:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}}"
project_base="${project_base%/}"
if [[ ! -f "${project_base}/setupEnv.sh" ]]; then
  echo "ERROR: setupEnv.sh not found under ${project_base}" >&2
  exit 2
fi

source "${project_base}/setupEnv.sh" >/dev/null
make -C "${project_base}/SimulationScripts" heavyflavourcorrelations_status
producer="${project_base}/SimulationScripts/heavyflavourcorrelations_status"
if [[ ! -x "${producer}" ]]; then
  echo "ERROR: producer build did not create an executable: ${producer}" >&2
  exit 3
fi
echo "PRODUCER_BUILD_READY path=${producer} sha256=$(sha256sum "${producer}" | awk '{print $1}')"
