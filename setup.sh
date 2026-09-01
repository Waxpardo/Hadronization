#!/usr/bin/env bash
# Source this file to expose optional site runtime prefixes. It writes nothing.

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
_hadronization_site_file="${_hadronization_setup_root}/config/site.conf"

if [[ -f "${_hadronization_site_file}" ]]; then
  # shellcheck source=/dev/null
  source "${_hadronization_site_file}" ||
    _hadronization_setup_fail "site configuration failed: ${_hadronization_site_file}"
fi

_hadronization_prepend_path() {
  [[ -d "$1" ]] || return 0
  case ":${PATH}:" in
    *":$1:"*) ;;
    *) PATH="$1:${PATH}" ;;
  esac
}

if [[ -n "${ROOT_PREFIX:-}" ]]; then
  [[ -d "${ROOT_PREFIX}" ]] ||
    _hadronization_setup_fail "ROOT_PREFIX does not exist: ${ROOT_PREFIX}"
  ROOTSYS="${ROOT_PREFIX}"
  export ROOTSYS
  _hadronization_prepend_path "${ROOT_PREFIX}/bin"
fi
if [[ -n "${PYTHIA8_PREFIX:-}" ]]; then
  [[ -d "${PYTHIA8_PREFIX}" ]] ||
    _hadronization_setup_fail "PYTHIA8_PREFIX does not exist: ${PYTHIA8_PREFIX}"
  PYTHIA8="${PYTHIA8_PREFIX}"
  export PYTHIA8
  _hadronization_prepend_path "${PYTHIA8_PREFIX}/bin"
fi
export PATH
[[ -z "${PYTHON:-}" ]] || export PYTHON
[[ -z "${CXX:-}" ]] || export CXX
[[ -z "${ROOT_CONFIG:-}" ]] || export ROOT_CONFIG
[[ -z "${PYTHIA8_CONFIG:-}" ]] || export PYTHIA8_CONFIG

unset _hadronization_setup_source _hadronization_setup_root _hadronization_site_file
unset -f _hadronization_prepend_path _hadronization_setup_fail
