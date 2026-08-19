#!/bin/bash
set -euo pipefail

if [[ "$#" -eq 1 && ("$1" == "-h" || "$1" == "--help") ]]; then
  cat <<'EOF'
Usage:
  ./merging/make_subsamples.sh FREEZE_DIR PRODUCTION_ROOT ANALYSIS_ROOT ANALYZED_DATA_BASE [OUTPUT_TAG]

Compatibility entry point for the publication workflow. It delegates to
merge_root_files.sh, which validates the sealed canonical or explicitly
authorised superseding manifest and creates its ten exact, deterministic,
disjoint equal-exposure blocks. Every tune must contribute the same number of
jobs, at least ten and divisible by ten -- merge_root_files.sh:63,66-67 and
tools/validate_analysis_outputs.py:112-113. Jobs per tune is a campaign
parameter, not a contract constant; the canonical production shape is 1000
per tune (docs/DESIGN_AND_RATIONALE.md:263).
No random/bootstrap partition is permitted for paper inputs.
EOF
  exit 0
fi

if [[ "$#" -lt 4 || "$#" -gt 5 ]]; then
  echo "ERROR: publication subsamples require the sealed canonical arguments; use --help" >&2
  exit 2
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "${script_dir}/merging/merge_root_files.sh" "$@"
