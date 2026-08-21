#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_base="${HADRONIZATION_BASE:-$(cd "${script_dir}/.." && pwd)}"
project_base="${project_base%/}"
export HADRONIZATION_BASE="${project_base}"

configuration="${1:-plotting/configuration_multiplicity_reduced_JUNCTIONS_THnSparse.json}"
report="${2:-plotting/validation/final_thnsparse_input_validation.json}"

cd "${project_base}"

if [ -f "${project_base}/setupEnv.sh" ]; then
  export SETUPENV_QUIET="${SETUPENV_QUIET:-1}"
  # shellcheck disable=SC1091
  source "${project_base}/setupEnv.sh"
fi

if ! command -v root >/dev/null 2>&1; then
  echo "ERROR: ROOT command 'root' was not found in PATH." >&2
  exit 1
fi

root -l -b <<ROOTCMDS
.L plotting/Validate_THnSparse_Production.C+
int validation_result = 0;
try {
  validation_result = Validate_THnSparse_Production("${configuration}", "${report}");
} catch (const std::exception& error) {
  std::cerr << "ERROR: " << error.what() << std::endl;
  validation_result = 1;
} catch (...) {
  std::cerr << "ERROR: unknown exception during THnSparse production validation" << std::endl;
  validation_result = 1;
}
if (validation_result != 0) { gSystem->Exit(validation_result); }
.q
ROOTCMDS

echo "THnSparse production validation completed: ${report}"
