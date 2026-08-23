#!/bin/bash
# Advisory only. Prints which owning document corresponds to the paths changed
# since the last commit, and nothing more. It never fails and never blocks.
#
# README.md lists the current document set.
# This tool maps code changes to that set without blocking a commit.

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
      echo "docs/PHYSICS.md (comparison) + docs/PIPELINE.md (contract)" ;;

    generation/*|analysis/*|merging/*|extraction/*|AnalysisScripts/*)
      echo "docs/PIPELINE.md (dataflow) + the component catalog in the internal repository" ;;

    Validation/*)
      echo "the component catalog in the internal repository + docs/PIPELINE.md (gate)" ;;

    # Plotting changes can affect the stage contract and publication outputs.
    "plotting"/*)
      echo "docs/PIPELINE.md (stage) + docs/RESULTS.md (publication output)" ;;

    generation/submit/runCondorJob.sh|tools/render_production_submit.py|tools/resubmit_held.py|tools/campaign*.py)
      echo "docs/PIPELINE.md (campaign) + docs/REPRODUCIBILITY.md (operations)" ;;

    setupEnv.sh|config/dependencies*|Makefile|tools/doctor.sh|tools/run_tests.sh|tools/build_producer.sh)
      echo "docs/REPRODUCIBILITY.md (runtime and checks)" ;;

    tools/*)
      echo "the component catalog in the internal repository; update the owning spine contract when needed" ;;

    tests/*)
      echo "the component catalog in the internal repository when the guarded contract changes" ;;

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
