#!/bin/bash
set -euo pipefail

script_dir="$(cd "$(dirname "$0")" && pwd)"
export HADRONIZATION_BASE="${HADRONIZATION_BASE:-${script_dir}}"
source "${script_dir}/setupEnv.sh"

exec python3 "${script_dir}/tools/resolve_publication_gate_b_signoff.py" "$@"
