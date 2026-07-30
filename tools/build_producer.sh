#!/bin/bash
set -euo pipefail

project_base="${1:-${HADRONIZATION_BASE:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}}"
project_base="${project_base%/}"
if [[ ! -f "${project_base}/setupEnv.sh" ]]; then
  echo "ERROR: setupEnv.sh not found under ${project_base}" >&2
  exit 2
fi

source "${project_base}/setupEnv.sh" >/dev/null
producer="${project_base}/SimulationScripts/heavyflavourcorrelations_status"
build_root="$(mktemp -d "${TMPDIR:-/tmp}/hadronization-producer.XXXXXX")"
staged_producer="${producer}.partial.$$"
cleanup() {
  rm -f -- "${staged_producer}"
  rm -rf -- "${build_root}"
}
trap cleanup EXIT
rebuilt_producer="${build_root}/heavyflavourcorrelations_status"
make -B -C "${project_base}/SimulationScripts" \
  "PRODUCER_OUTPUT=${rebuilt_producer}" heavyflavourcorrelations_status
if [[ -L "${rebuilt_producer}" || ! -x "${rebuilt_producer}" ]]; then
  echo "ERROR: forced producer rebuild did not create an executable: ${rebuilt_producer}" >&2
  exit 3
fi
rebuilt_sha256="$(sha256sum "${rebuilt_producer}" | awk '{print $1}')"
install -m 0755 "${rebuilt_producer}" "${staged_producer}"
staged_sha256="$(sha256sum "${staged_producer}" | awk '{print $1}')"
if [[ "${staged_sha256}" != "${rebuilt_sha256}" ]]; then
  echo "ERROR: staged producer checksum differs from forced rebuild" >&2
  exit 3
fi
mv -f -- "${staged_producer}" "${producer}"
if [[ -L "${producer}" || ! -x "${producer}" ]]; then
  echo "ERROR: producer build did not create an executable: ${producer}" >&2
  exit 3
fi
installed_sha256="$(sha256sum "${producer}" | awk '{print $1}')"
if [[ "${installed_sha256}" != "${rebuilt_sha256}" ]]; then
  echo "ERROR: installed producer checksum differs from forced rebuild" >&2
  exit 3
fi
echo "PRODUCER_BUILD_READY path=${producer} sha256=${installed_sha256} forced_rebuild=true"
