#!/usr/bin/env bash
# Run the plotting macros that are intended for paper figures.
#
# Usage:
#   ./PlottingScripts/run_paper_plots.sh [TARGET ...]
#
# If no target is given, the script runs the current paper plotting suite.

set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  ./PlottingScripts/run_paper_plots.sh [TARGET ...]

Targets:
  all                         Current paper suite: multiplicity-boundaries + kinematic-spectra + thnsparse
  paper                       Alias for all
  smoke                       Reduced-scope suite; THnSparse checks the production-supported 1-10% class with N=10
  quick                       Alias for smoke
  multiplicity-boundaries     Charged-particle multiplicity plot with percentile boundaries
  multiplicity-compact        MONASH compact multiplicity-percentile plot
  multiplicity-spectrum       Shared raw Nch spectrum with tune/MONASH ratio panel and MONASH inset
  kinematic-spectra           Inclusive raw-tree pT, eta, phi, and multiplicity spectra
  thnsparse                   Full paper THnSparse config with ten-subsample errors
  thnsparse-complete-root     Reduced THnSparse selection with the same central/error provenance
  audit-subsamples            Scan every full-config observable and report all incomplete N=10 coverage
  validate-inputs             Validate central/subsample ROOT objects, manifests, and union consistency
  final-multiplicity          FinalAnalysis two-sample multiplicity comparison
  final-yields                FinalAnalysis selected-particle yield comparison
  list                        Print this target list without running ROOT

Useful environment overrides:
  DATASET_SELECTOR
      default: config/dataset_selector.json; selects raw, central, and block roots
  USE_DATASET_SELECTOR
      default: true; set false only for an explicitly documented diagnostic
  THNSPARSE_CONFIG
      default: PlottingScripts/configuration_multiplicity_reduced_JUNCTIONS_THnSparse.json
  THNSPARSE_COMPLETE_ROOT_CONFIG
      default: PlottingScripts/configuration_multiplicity_reduced_JUNCTIONS_THnSparse_complete_root.json
  MULTIPLICITY_CONFIG
      default: THNSPARSE_COMPLETE_ROOT_CONFIG
  MULTIPLICITY_OUTPUT_DIR
      default: PlottingScripts/Plots/MultiplicityDistribution
  MULTIPLICITY_NORMALIZE
      default: false
  MULTIPLICITY_STRICT
      default: true
  MULTIPLICITY_COMPACT
      default: false
  KINEMATIC_RAW_BASE
      default: RootFiles/HF
  KINEMATIC_OUTPUT_DIR
      default: PlottingScripts/Plots/KinematicSpectra
  KINEMATIC_NORMALIZE
      default: true
  KINEMATIC_STRICT
      default: true
  FINAL_INDEPENDENT_TAG
      default: 12-01-2026
  FINAL_COMBINED_TAG
      default: 27-03-2026
  FINAL_NSUB
      default: 10
  FINAL_NORMALIZE
      default: true

Examples:
  ./PlottingScripts/run_paper_plots.sh
  ./PlottingScripts/run_paper_plots.sh smoke
  ./PlottingScripts/run_paper_plots.sh multiplicity-boundaries
  ./PlottingScripts/run_paper_plots.sh kinematic-spectra
  THNSPARSE_CONFIG=PlottingScripts/configuration_multiplicity_reduced_JUNCTIONS_THnSparse_complete_root.json \
    ./PlottingScripts/run_paper_plots.sh thnsparse
USAGE
}

normalize_bool() {
  case "$1" in
    true|TRUE|True|1|yes|YES|Yes|on|ON|On)
      echo "true"
      ;;
    false|FALSE|False|0|no|NO|No|off|OFF|Off)
      echo "false"
      ;;
    *)
      echo "ERROR: expected boolean value, got '$1'" >&2
      exit 1
      ;;
  esac
}

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_base="${HADRONIZATION_BASE:-$(cd "${script_dir}/.." && pwd)}"
project_base="${project_base%/}"
export HADRONIZATION_BASE="${project_base}"

DATASET_SELECTOR="${DATASET_SELECTOR:-config/dataset_selector.json}"
dataset_selector_path="${DATASET_SELECTOR}"
if [[ "${dataset_selector_path}" != /* ]]; then
  dataset_selector_path="${project_base}/${dataset_selector_path}"
fi
if [[ "${USE_DATASET_SELECTOR:-true}" == "true" ]]; then
  python3 "${project_base}/tools/dataset_selector.py" validate \
    --selector "${dataset_selector_path}"
  eval "$(
    python3 "${project_base}/tools/dataset_selector.py" shell \
      --selector "${dataset_selector_path}"
  )"
fi

default_thnsparse_config="PlottingScripts/configuration_multiplicity_reduced_JUNCTIONS_THnSparse.json"
default_complete_root_config="PlottingScripts/configuration_multiplicity_reduced_JUNCTIONS_THnSparse_complete_root.json"

THNSPARSE_CONFIG="${THNSPARSE_CONFIG:-${default_thnsparse_config}}"
THNSPARSE_COMPLETE_ROOT_CONFIG="${THNSPARSE_COMPLETE_ROOT_CONFIG:-${default_complete_root_config}}"
MULTIPLICITY_CONFIG="${MULTIPLICITY_CONFIG:-${THNSPARSE_COMPLETE_ROOT_CONFIG}}"
MULTIPLICITY_OUTPUT_DIR="${MULTIPLICITY_OUTPUT_DIR:-PlottingScripts/Plots/MultiplicityDistribution}"
MULTIPLICITY_NORMALIZE="$(normalize_bool "${MULTIPLICITY_NORMALIZE:-false}")"
MULTIPLICITY_STRICT="$(normalize_bool "${MULTIPLICITY_STRICT:-true}")"
MULTIPLICITY_COMPACT="$(normalize_bool "${MULTIPLICITY_COMPACT:-false}")"
KINEMATIC_RAW_BASE="${KINEMATIC_RAW_BASE:-${HADRONIZATION_RAW_BASE:-RootFiles/HF}}"
KINEMATIC_OUTPUT_DIR="${KINEMATIC_OUTPUT_DIR:-PlottingScripts/Plots/KinematicSpectra}"
KINEMATIC_NORMALIZE="$(normalize_bool "${KINEMATIC_NORMALIZE:-true}")"
KINEMATIC_STRICT="$(normalize_bool "${KINEMATIC_STRICT:-true}")"
FINAL_INDEPENDENT_TAG="${FINAL_INDEPENDENT_TAG:-12-01-2026}"
FINAL_COMBINED_TAG="${FINAL_COMBINED_TAG:-27-03-2026}"
FINAL_NSUB="${FINAL_NSUB:-10}"
FINAL_NORMALIZE="$(normalize_bool "${FINAL_NORMALIZE:-true}")"

if [ "$#" -eq 0 ]; then
  set -- all
fi

expanded_targets=()
for target in "$@"; do
  case "${target}" in
    -h|--help|help)
      usage
      exit 0
      ;;
    list)
      usage
      exit 0
      ;;
    all|paper)
      expanded_targets+=("multiplicity-boundaries" "kinematic-spectra" "thnsparse")
      ;;
    smoke|quick)
      expanded_targets+=("multiplicity-boundaries" "kinematic-spectra" "thnsparse-complete-root")
      ;;
    multiplicity-boundaries|multiplicity-compact|multiplicity-spectrum|kinematic-spectra|thnsparse|thnsparse-complete-root|audit-subsamples|validate-inputs|final-multiplicity|final-yields)
      expanded_targets+=("${target}")
      ;;
    *)
      echo "ERROR: unknown paper plot target '${target}'" >&2
      echo >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [ ! -d "${project_base}/PlottingScripts" ]; then
  echo "ERROR: HADRONIZATION_BASE does not look like a Hadronization checkout: ${project_base}" >&2
  exit 1
fi

cd "${project_base}"

if [ -f "${project_base}/setupEnv.sh" ]; then
  export SETUPENV_QUIET="${SETUPENV_QUIET:-1}"
  # shellcheck disable=SC1091
  source "${project_base}/setupEnv.sh"
fi

if ! command -v root >/dev/null 2>&1; then
  echo "ERROR: ROOT command 'root' was not found in PATH." >&2
  echo "       Source the project/cluster environment first, or check setupEnv.sh." >&2
  exit 1
fi

require_file() {
  local path="$1"
  if [ ! -f "${path}" ]; then
    echo "ERROR: required file not found: ${path}" >&2
    exit 1
  fi
}

require_integer() {
  local name="$1"
  local value="$2"
  if ! [[ "${value}" =~ ^[0-9]+$ ]]; then
    echo "ERROR: ${name} must be an integer, got '${value}'" >&2
    exit 1
  fi
}

run_thnsparse() {
  local config="$1"
  local label="$2"

  require_file "${config}"

  echo
  echo "==> Running ${label}"
  echo "    config: ${config}"

  root -l -b <<ROOTCMDS
.L PlottingScripts/improvedPlotting_THnSparse.C+
int __paper_plot_result = 0;
try {
  __paper_plot_result = improvedPlotting_THnSparse("${config}");
} catch (const std::exception& error) {
  std::cerr << "ERROR: " << error.what() << std::endl;
  __paper_plot_result = 1;
} catch (...) {
  std::cerr << "ERROR: unknown exception while running improvedPlotting_THnSparse" << std::endl;
  __paper_plot_result = 1;
}
if (__paper_plot_result != 0) { gSystem->Exit(__paper_plot_result); }
.q
ROOTCMDS
}

run_subsample_coverage_audit() {
  require_file "${THNSPARSE_CONFIG}"
  if ! command -v jq >/dev/null 2>&1; then
    echo "ERROR: audit-subsamples requires jq." >&2
    return 1
  fi

  local audit_config
  audit_config="$(mktemp "${TMPDIR:-/tmp}/hadronization-thnsparse-audit.XXXXXX.json")"
  jq \
    '.subsample_coverage_audit = true
     | .subsample_error_bins_to_exclude = []
     | .draw_correlation_plots = false' \
    "${THNSPARSE_CONFIG}" > "${audit_config}"

  local status=0
  set +e
  run_thnsparse "${audit_config}" "full THnSparse subsample-coverage audit"
  status=$?
  set -e
  rm -f -- "${audit_config}"
  return "${status}"
}

run_multiplicity_boundaries() {
  local compact="${1:-${MULTIPLICITY_COMPACT}}"
  require_file "${MULTIPLICITY_CONFIG}"

  echo
  echo "==> Running multiplicity-boundaries"
  echo "    config: ${MULTIPLICITY_CONFIG}"
  echo "    output: ${MULTIPLICITY_OUTPUT_DIR}"
  echo "    compact MONASH: ${compact}"

  root -l -b <<ROOTCMDS
.L PlottingScripts/Plot_MultiplicityDistribution_PercentileBoundaries.C+
int __multiplicity_plot_result = 0;
try {
  Plot_MultiplicityDistribution_PercentileBoundaries("${MULTIPLICITY_CONFIG}", "${MULTIPLICITY_OUTPUT_DIR}", ${MULTIPLICITY_NORMALIZE}, ${MULTIPLICITY_STRICT}, ${compact});
} catch (const std::exception& error) {
  std::cerr << "ERROR: " << error.what() << std::endl;
  __multiplicity_plot_result = 1;
} catch (...) {
  std::cerr << "ERROR: unknown exception while running Plot_MultiplicityDistribution_PercentileBoundaries" << std::endl;
  __multiplicity_plot_result = 1;
}
if (__multiplicity_plot_result != 0) { gSystem->Exit(__multiplicity_plot_result); }
.q
ROOTCMDS
}

run_kinematic_spectra() {
  echo
  echo "==> Running kinematic-spectra"
  echo "    raw input: ${KINEMATIC_RAW_BASE}"
  echo "    output: ${KINEMATIC_OUTPUT_DIR}"

  root -l -b <<ROOTCMDS
.L PlottingScripts/Plot_InclusiveKinematicSpectra_Raw.C+
int __kinematic_plot_result = 0;
try {
  Plot_InclusiveKinematicSpectra_Raw("${KINEMATIC_RAW_BASE}", "${KINEMATIC_OUTPUT_DIR}", ${KINEMATIC_NORMALIZE}, ${KINEMATIC_STRICT});
} catch (const std::exception& error) {
  std::cerr << "ERROR: " << error.what() << std::endl;
  __kinematic_plot_result = 1;
} catch (...) {
  std::cerr << "ERROR: unknown exception while running Plot_InclusiveKinematicSpectra_Raw" << std::endl;
  __kinematic_plot_result = 1;
}
if (__kinematic_plot_result != 0) { gSystem->Exit(__kinematic_plot_result); }
.q
ROOTCMDS
}

run_multiplicity_spectrum() {
  echo
  echo "==> Running multiplicity-spectrum"
  echo "    raw input: ${KINEMATIC_RAW_BASE}"
  echo "    output: ${KINEMATIC_OUTPUT_DIR}"

  root -l -b <<ROOTCMDS
.L PlottingScripts/Plot_InclusiveKinematicSpectra_Raw.C+
int __multiplicity_spectrum_result = 0;
try {
  Plot_InclusiveMultiplicitySpectrum_Raw("${KINEMATIC_RAW_BASE}", "${KINEMATIC_OUTPUT_DIR}", ${KINEMATIC_NORMALIZE}, ${KINEMATIC_STRICT});
} catch (const std::exception& error) {
  std::cerr << "ERROR: " << error.what() << std::endl;
  __multiplicity_spectrum_result = 1;
} catch (...) {
  std::cerr << "ERROR: unknown exception while running Plot_InclusiveMultiplicitySpectrum_Raw" << std::endl;
  __multiplicity_spectrum_result = 1;
}
if (__multiplicity_spectrum_result != 0) { gSystem->Exit(__multiplicity_spectrum_result); }
.q
ROOTCMDS
}

run_final_multiplicity() {
  require_file "PlottingScripts/FinalAnalysis/Plot_MultiplicityDistributions_TwoSamples.C"
  require_integer "FINAL_NSUB" "${FINAL_NSUB}"

  echo
  echo "==> Running final-multiplicity"
  echo "    independent: ${FINAL_INDEPENDENT_TAG}"
  echo "    combined:    ${FINAL_COMBINED_TAG}"
  echo "    nSub:        ${FINAL_NSUB}"
  echo "    normalize:   ${FINAL_NORMALIZE}"

  root -l -b -q \
    "PlottingScripts/FinalAnalysis/Plot_MultiplicityDistributions_TwoSamples.C(\"${FINAL_INDEPENDENT_TAG}\",\"${FINAL_COMBINED_TAG}\",${FINAL_NSUB},${FINAL_NORMALIZE})"
}

run_final_yields() {
  require_file "PlottingScripts/FinalAnalysis/Plot_SelectedParticleYields_IndependentVsCombined.C"
  require_integer "FINAL_NSUB" "${FINAL_NSUB}"

  echo
  echo "==> Running final-yields"
  echo "    independent: ${FINAL_INDEPENDENT_TAG}"
  echo "    combined:    ${FINAL_COMBINED_TAG}"
  echo "    nSub:        ${FINAL_NSUB}"

  root -l -b -q \
    "PlottingScripts/FinalAnalysis/Plot_SelectedParticleYields_IndependentVsCombined.C(\"${FINAL_INDEPENDENT_TAG}\",\"${FINAL_COMBINED_TAG}\",${FINAL_NSUB})"
}

echo "Hadronization base: ${project_base}"
echo "Targets: ${expanded_targets[*]}"

for target in "${expanded_targets[@]}"; do
  case "${target}" in
    multiplicity-boundaries)
      run_multiplicity_boundaries "${MULTIPLICITY_COMPACT}"
      ;;
    multiplicity-compact)
      run_multiplicity_boundaries true
      ;;
    multiplicity-spectrum)
      run_multiplicity_spectrum
      ;;
    kinematic-spectra)
      run_kinematic_spectra
      ;;
    thnsparse)
      run_thnsparse "${THNSPARSE_CONFIG}" "thnsparse"
      ;;
    thnsparse-complete-root)
      run_thnsparse "${THNSPARSE_COMPLETE_ROOT_CONFIG}" "thnsparse-complete-root"
      ;;
    audit-subsamples)
      run_subsample_coverage_audit
      ;;
    validate-inputs)
      "${project_base}/PlottingScripts/validate_thnsparse_inputs.sh"
      ;;
    final-multiplicity)
      run_final_multiplicity
      ;;
    final-yields)
      run_final_yields
      ;;
  esac
done

echo
echo "Paper plotting targets completed."
