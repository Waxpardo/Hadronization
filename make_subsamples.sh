#!/bin/bash
set -euo pipefail

if [[ "$#" -eq 1 && ("$1" == "-h" || "$1" == "--help") ]]; then
  cat <<'EOF'
Usage:
  ./make_subsamples.sh FREEZE_DIR PRODUCTION_ROOT ANALYSIS_ROOT ANALYZED_DATA_BASE [OUTPUT_TAG]

Compatibility entry point for the publication workflow. It delegates to
merge_root_files.sh, which validates the sealed canonical or explicitly
authorised superseding manifest and creates its ten exact, deterministic,
disjoint equal-exposure blocks. The first-stage freeze has 100 jobs per tune;
a superseding manifest may have an equal N>=100 per tune divisible by ten.
No random/bootstrap partition is permitted for paper inputs.
EOF
  exit 0
fi

if [[ "$#" -lt 4 || "$#" -gt 5 ]]; then
  echo "ERROR: publication subsamples require the sealed canonical arguments; use --help" >&2
  exit 2
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "${script_dir}/merge_root_files.sh" "$@"
