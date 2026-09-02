#!/usr/bin/env bash
# Source this file to resolve the same verified runtime used by builds/workers.

_hadronization_setup_fail() {
  printf 'ERROR: setup.sh: %s\n' "$*" >&2
  return 1 2>/dev/null || exit 1
}

if [[ -n "${BASH_SOURCE[0]:-}" ]]; then
  _hadronization_setup_source="${BASH_SOURCE[0]}"
elif [[ -n "${ZSH_VERSION:-}" ]]; then
  _hadronization_setup_source="${(%):-%N}"
else
  _hadronization_setup_fail "cannot determine the sourced file location"
fi
_hadronization_setup_root="$({ cd "$(dirname "${_hadronization_setup_source}")" && pwd -P; })" ||
  _hadronization_setup_fail "cannot resolve the repository root"
_hadronization_runtime_python="${PYTHON:-$(command -v python3)}"
[[ -n "${_hadronization_runtime_python}" ]] ||
  _hadronization_setup_fail "python3 is required to resolve the runtime"
_hadronization_exports="$(${_hadronization_runtime_python} \
  "${_hadronization_setup_root}/pipeline/generate/runtime.py" shell)" ||
  _hadronization_setup_fail "runtime resolution failed"
eval "${_hadronization_exports}" || _hadronization_setup_fail "runtime exports failed"

unset _hadronization_setup_source _hadronization_setup_root
unset _hadronization_runtime_python _hadronization_exports
unset -f _hadronization_setup_fail
