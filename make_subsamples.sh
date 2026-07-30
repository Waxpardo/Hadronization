#!/bin/bash
set -euo pipefail

cat >&2 <<'EOF'
The publication workflow does not create random subsamples.

Ten deterministic, disjoint blocks are frozen together with the canonical
manifest and merged by:

  ./merge_root_files.sh FREEZE_DIR ANALYSIS_ROOT ANALYZED_DATA_BASE OUTPUT_TAG

For historical randomized/bootstrap behavior only, use
make_subsamples_legacy.sh. Legacy outputs are not publication inputs.
EOF
exit 2
