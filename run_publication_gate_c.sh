#!/bin/bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

exec python3 "${project_root}/tools/run_publication_gate_c.py" "$@"
