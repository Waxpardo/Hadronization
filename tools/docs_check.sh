#!/bin/bash
# Advisory only. Prints which owning document corresponds to the paths changed
# since the last commit, and nothing more. It never fails and never blocks.
#
# The convention it serves is in README.md ("Which document owns what"): a code
# change and its documentation change land in the same commit. A hook that
# failed on every commit would be bypassed within a week, so this only tells
# you where to look.

set -uo pipefail

project_base="${1:-${HADRONIZATION_BASE:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}}"
project_base="${project_base%/}"
cd "${project_base}" || exit 0

changed="$(git diff --name-only HEAD -- 2>/dev/null; git diff --cached --name-only 2>/dev/null)"
changed="$(printf '%s\n' "${changed}" | sort -u | sed '/^$/d')"

if [[ -z "${changed}" ]]; then
  echo "docs-check: no uncommitted changes."
  exit 0
fi

owner_for() {
  case "$1" in
    generation/cards/*.cmnd|config/tune_difference_allowlist_v1.json)
      echo "REPRODUCIBILITY.md (physics contract) + docs/DESIGN_AND_RATIONALE.md (why)" ;;
    generation/*|analysis/*|merging/*|extraction/*|AnalysisScripts/*)
      echo "that directory's README.md; docs/DESIGN_AND_RATIONALE.md if a contract moved" ;;
    Validation/*)
      echo "docs/DESIGN_AND_RATIONALE.md -- validator contracts are design (see 3.13)" ;;
    plotting/*)
      echo "plotting/README.md" ;;
    generation/submit/runCondorJob.sh|tools/render_production_submit.py|tools/resubmit_held.py|tools/campaign*.py)
      echo "Condor_README.md (operations)" ;;
    setupEnv.sh|config/dependencies*|Makefile|tools/doctor.sh|tools/run_tests.sh|tools/build_producer.sh)
      echo "docs/WORKSPACE.md (machine setup, what runs where)" ;;
    tools/*)
      echo "README.md repository-roles list; docs/DESIGN_AND_RATIONALE.md if a rule changed" ;;
    tests/*)
      echo "(usually none -- but if a contract changed, so did its design entry)" ;;
    *.md)
      echo "(documentation itself)" ;;
    *)
      echo "(no owner mapped)" ;;
  esac
}

echo "docs-check: changed paths and the document that owns each area."
echo "            Advisory. A code change and its docs land in the same commit."
echo
printf '%s\n' "${changed}" | while IFS= read -r f; do
  printf '  %-52s -> %s\n' "${f}" "$(owner_for "${f}")"
done

if printf '%s\n' "${changed}" | grep -qvE '\.md$' && \
   ! printf '%s\n' "${changed}" | grep -qE '\.md$'; then
  echo
  echo "  NOTE: code changed and no .md did. If that is right, fine -- a"
  echo "        refactor with no behaviour change needs no document. If a"
  echo "        behaviour or contract moved, write it down before committing."
fi
exit 0
