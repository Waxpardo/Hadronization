#!/bin/bash
# Run every Python contract-test driver in one prepared environment.
# Some drivers compile or execute ROOT macros and fail when ROOT is absent.
# This script sources setupEnv.sh once because Makefile recipe lines use separate shells.

set -uo pipefail

project_base="${1:-${HADRONIZATION_BASE:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}}"
project_base="${project_base%/}"

# Environment setup can fail here because the tests report their own dependencies.
if [[ -f "${project_base}/setupEnv.sh" ]]; then
  # shellcheck source=/dev/null
  SETUPENV_QUIET=1 source "${project_base}/setupEnv.sh" >/dev/null 2>&1 || true
fi

# Count ROOT requirements from the test sources so the warning cannot drift.
root_dependent=$(grep -rl 'ROOT is required for' "${project_base}/tests" \
                 2>/dev/null | wc -l | tr -d ' ')
if command -v root >/dev/null 2>&1; then
  echo "  ROOT: $(command -v root)"
else
  echo "  ROOT: not found -- the ${root_dependent} ROOT-dependent tests will fail, not skip."
  echo "        This is expected off-cluster; it is NOT a green run."
fi

failed=0
total=0

# A contract suite is read-only with respect to scientific results. On Nikhef,
# plotting/Plots is an ignored symlink into the external result plane, so a
# test that accidentally renders can mutate published bytes while leaving Git
# clean. Snapshot the resolved tree content (paths + SHA-256) and fail the
# entire suite if any test changes it.
test_output_plane="$(python3 - "${project_base}/plotting/Plots" <<'PY'
import pathlib, sys
path = pathlib.Path(sys.argv[1])
print(path.resolve() if path.exists() or path.is_symlink() else "")
PY
)"
snapshot_output_plane() {
  python3 - "$1" <<'PY'
import hashlib, pathlib, sys
digest = hashlib.sha256()
if sys.argv[1]:
    root = pathlib.Path(sys.argv[1])
    if root.is_dir():
        for path in sorted(p for p in root.rglob("*") if p.is_file()):
            digest.update(path.relative_to(root).as_posix().encode())
            digest.update(b"\0")
            digest.update(hashlib.sha256(path.read_bytes()).digest())
print(digest.hexdigest())
PY
}
test_output_plane_before="$(snapshot_output_plane "${test_output_plane}")"

for t in "${project_base}"/tests/test_*.py; do
  total=$((total + 1))
  # Each driver starts without HADRONIZATION_BASE because worker tests enforce that boundary.
  if env -u HADRONIZATION_BASE "${PYTHON:-python3}" "${t}" >/dev/null 2>&1; then
    printf '  PASS %s\n' "$(basename "${t}")"
  else
    printf '  FAIL %s\n' "$(basename "${t}")"
    failed=$((failed + 1))
  fi
done

test_output_plane_after="$(snapshot_output_plane "${test_output_plane}")"
if [[ "${test_output_plane_after}" != "${test_output_plane_before}" ]]; then
  echo "  FAIL external scientific output plane changed during tests: ${test_output_plane}"
  failed=$((failed + 1))
else
  echo "  PASS external scientific output plane unchanged"
fi

echo "  $((total - failed))/${total} passed"
exit $(( failed == 0 ? 0 : 1 ))
