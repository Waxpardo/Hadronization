#!/usr/bin/env bash
# Run the plotting macros that are intended for paper figures.
#
# Usage:
#   ./plotting/run_paper_plots.sh [TARGET ...]
#
# If no target is given, the script runs the current paper plotting suite.

set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  ./plotting/run_paper_plots.sh [TARGET ...]

Targets:
  all                         Current paper suite, beginning with an immutable multiplicity-boundary freeze
  paper                       Alias for all
  smoke                       Reduced canonical pair-plot suite with the same N=10 block-error prescription
  quick                       Alias for smoke
  multiplicity-boundaries     Charged-particle multiplicity plot with percentile boundaries
  multiplicity-compact        MONASH compact multiplicity-percentile plot
  multiplicity-spectrum       Shared raw Nch spectrum with tune/MONASH ratio panel and MONASH inset
  kinematic-spectra           Inclusive raw-tree pT, eta, phi, and multiplicity spectra
  thnsparse                   Full paper THnSparse config with ten-subsample errors
  thnsparse-complete-root     Reduced THnSparse selection with the same central/error provenance
  freeze-boundaries           Freeze/revalidate the full-config multiplicity receipt before plotting
  freeze-boundaries-smoke     Freeze/revalidate the reduced-config receipt before smoke plotting
  audit-subsamples            Scan every full-config observable and report all incomplete N=10 coverage
  legacy-regression           NONCANONICAL: exact stable-main Paul pT/eta recuts with SS factor 0.5
  validate-inputs             Validate central/subsample ROOT objects, manifests, and union consistency
  final-multiplicity          NONCANONICAL legacy-unsealed two-sample comparison
  final-yields                NONCANONICAL legacy-unsealed selected-yield comparison
  list                        Print this target list without running ROOT

Every output-producing target snapshots its output directory before ROOT
runs, then fails closed unless each regenerated canvas has PDF, PNG, and ROOT
macro representations plus checksum-bound final-plot provenance sidecars.
A `canonical_candidate` selector is accepted only for prepublication
validation; its sidecars are forced to publication_eligible=false and every
plot must be regenerated after exact dataset authorization.

Useful environment overrides:
  DATASET_SELECTOR
      default: config/dataset_selector.json; selects raw, central, and block roots
  USE_DATASET_SELECTOR
      default: true; set false only for an explicitly documented diagnostic
  THNSPARSE_CONFIG
      default: plotting/configuration_multiplicity_reduced_JUNCTIONS_THnSparse.json
  THNSPARSE_COMPLETE_ROOT_CONFIG
      default: plotting/configuration_multiplicity_reduced_JUNCTIONS_THnSparse_complete_root.json
  MULTIPLICITY_CONFIG
      default: THNSPARSE_CONFIG; smoke uses its matching reduced config
  MULTIPLICITY_OUTPUT_DIR
      default: plotting/Plots/MultiplicityDistribution
  MULTIPLICITY_NORMALIZE
      default: false
  MULTIPLICITY_STRICT
      default: true
  MULTIPLICITY_COMPACT
      default: false
  KINEMATIC_RAW_BASE
      default: RootFiles/HF
  KINEMATIC_OUTPUT_DIR
      default: plotting/Plots/KinematicSpectra
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
  PLOT_PROVENANCE_DEVELOPMENT
      default: false; true permits a tracked-dirty checkout only for
      explicitly non-release development validation. Canonical release
      plotting remains tracked-clean by default.

Examples:
  ./plotting/run_paper_plots.sh
  ./plotting/run_paper_plots.sh smoke
  ./plotting/run_paper_plots.sh multiplicity-boundaries
  ./plotting/run_paper_plots.sh kinematic-spectra
  ./plotting/run_paper_plots.sh legacy-regression
  THNSPARSE_CONFIG=plotting/configuration_multiplicity_reduced_JUNCTIONS_THnSparse_complete_root.json \
    ./plotting/run_paper_plots.sh thnsparse
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

# Help and target discovery must work in a fresh checkout before ROOT,
# datasets, selector configuration, or environment setup are available.
for argument in "$@"; do
  case "${argument}" in
    -h|--help|help|list)
      usage
      exit 0
      ;;
  esac
done

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
    --selector "${dataset_selector_path}" \
    --checkout "${project_base}"
  eval "$(
    python3 "${project_base}/tools/dataset_selector.py" shell \
      --selector "${dataset_selector_path}" \
      --checkout "${project_base}"
  )"
fi

default_thnsparse_config="plotting/configuration_multiplicity_reduced_JUNCTIONS_THnSparse.json"
default_complete_root_config="plotting/configuration_multiplicity_reduced_JUNCTIONS_THnSparse_complete_root.json"

THNSPARSE_CONFIG="${THNSPARSE_CONFIG:-${default_thnsparse_config}}"
THNSPARSE_COMPLETE_ROOT_CONFIG="${THNSPARSE_COMPLETE_ROOT_CONFIG:-${default_complete_root_config}}"
MULTIPLICITY_CONFIG="${MULTIPLICITY_CONFIG:-${THNSPARSE_CONFIG}}"
MULTIPLICITY_OUTPUT_DIR="${MULTIPLICITY_OUTPUT_DIR:-plotting/Plots/MultiplicityDistribution}"
MULTIPLICITY_NORMALIZE="$(normalize_bool "${MULTIPLICITY_NORMALIZE:-false}")"
MULTIPLICITY_STRICT="$(normalize_bool "${MULTIPLICITY_STRICT:-true}")"
MULTIPLICITY_COMPACT="$(normalize_bool "${MULTIPLICITY_COMPACT:-false}")"
KINEMATIC_RAW_BASE="${KINEMATIC_RAW_BASE:-${HADRONIZATION_RAW_BASE:-RootFiles/HF}}"
KINEMATIC_OUTPUT_DIR="${KINEMATIC_OUTPUT_DIR:-plotting/Plots/KinematicSpectra}"
KINEMATIC_NORMALIZE="$(normalize_bool "${KINEMATIC_NORMALIZE:-true}")"
KINEMATIC_STRICT="$(normalize_bool "${KINEMATIC_STRICT:-true}")"
FINAL_INDEPENDENT_TAG="${FINAL_INDEPENDENT_TAG:-12-01-2026}"
FINAL_COMBINED_TAG="${FINAL_COMBINED_TAG:-27-03-2026}"
FINAL_NSUB="${FINAL_NSUB:-10}"
FINAL_NORMALIZE="$(normalize_bool "${FINAL_NORMALIZE:-true}")"
PLOT_PROVENANCE_DEVELOPMENT="$(
  normalize_bool "${PLOT_PROVENANCE_DEVELOPMENT:-false}"
)"
# Final-plot provenance tracking was part of the gate layer and has been
# removed. The per-target blocks below that used to set provenance_enabled are
# forced off here so the plotting targets themselves are untouched.
plot_provenance_tool=""

requested_command=("$0" "$@")
requested_command_display=""
printf -v requested_command_display '%q ' "${requested_command[@]}"
requested_command_display="${requested_command_display% }"

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
      expanded_targets+=("freeze-boundaries" "thnsparse" "multiplicity-boundaries" "kinematic-spectra")
      ;;
    smoke|quick)
      expanded_targets+=("freeze-boundaries-smoke" "thnsparse-complete-root" "multiplicity-boundaries-smoke")
      ;;
    multiplicity-boundaries|multiplicity-compact|multiplicity-spectrum|kinematic-spectra|thnsparse|thnsparse-complete-root|freeze-boundaries|freeze-boundaries-smoke|audit-subsamples|legacy-regression|validate-inputs|final-multiplicity|final-yields)
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

publication_target_requested=false
legacy_diagnostic_requested=false
for target in "${expanded_targets[@]}"; do
  case "${target}" in
    multiplicity-boundaries|multiplicity-boundaries-smoke|multiplicity-compact|multiplicity-spectrum|kinematic-spectra|thnsparse|thnsparse-complete-root|freeze-boundaries|freeze-boundaries-smoke|audit-subsamples)
      publication_target_requested=true
      ;;
    legacy-regression)
      legacy_diagnostic_requested=true
      ;;
  esac
done

if [[ "${legacy_diagnostic_requested}" == "true" &&
      "${#expanded_targets[@]}" -ne 1 ]]; then
  echo "ERROR: a legacy diagnostic must be run as a standalone target." >&2
  exit 1
fi
if [[ "${publication_target_requested}" == "true" ]] &&
   [[ "${HADRONIZATION_DATASET_STATUS:-}" != "canonical" ]] &&
   [[ "${HADRONIZATION_DATASET_STATUS:-}" != "canonical_candidate" ]]; then
  echo "ERROR: canonical plotting/validation is fail-closed." >&2
  echo "       Active dataset status=${HADRONIZATION_DATASET_STATUS:-unset}," >&2
  echo "       publication_eligible=${HADRONIZATION_DATASET_PUBLICATION_ELIGIBLE:-unset}." >&2
  echo "       Select a sealed canonical candidate or an authorized canonical" >&2
  echo "       dataset, or run the noncanonical 'legacy-regression' target." >&2
  exit 1
fi
if [[ "${HADRONIZATION_DATASET_STATUS:-}" == "canonical" ]] &&
   [[ "${HADRONIZATION_DATASET_PUBLICATION_ELIGIBLE:-}" != "true" ]]; then
  echo "ERROR: canonical status requires exact publication authorization." >&2
  exit 1
fi
if [[ "${HADRONIZATION_DATASET_STATUS:-}" == "canonical_candidate" ]] &&
   [[ "${HADRONIZATION_DATASET_PUBLICATION_ELIGIBLE:-}" != "false" ]]; then
  echo "ERROR: canonical_candidate must remain publication-ineligible." >&2
  exit 1
fi
if [[ "${legacy_diagnostic_requested}" == "true" ]] &&
   { [[ "${HADRONIZATION_DATASET_STATUS:-}" != "legacy_regression_default" ]] ||
     [[ "${HADRONIZATION_DATASET_PUBLICATION_ELIGIBLE:-}" != "false" ]]; }; then
  echo "ERROR: legacy diagnostics require the explicit nonpublication legacy selector." >&2
  exit 1
fi

canonical_pair_provenance_mode="canonical-pair"
canonical_raw_provenance_mode="canonical-raw"
if [[ "${HADRONIZATION_DATASET_STATUS:-}" == "canonical_candidate" ]]; then
  canonical_pair_provenance_mode="canonical-validation-pair"
  canonical_raw_provenance_mode="canonical-validation-raw"
  echo "PREPUBLICATION_CANONICAL_VALIDATION"
  echo "  Outputs are deliberately publication_eligible=false and must be"
  echo "  regenerated after scientific-review and project-owner authorization."
fi

if [ ! -d "${project_base}/plotting" ]; then
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
.L plotting/improvedPlotting_THnSparse.C+
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

run_boundary_freeze() {
  local config="$1"
  local label="$2"
  require_file "${config}"

  echo
  echo "==> Freezing ${label} multiplicity boundaries"
  echo "    config: ${config}"

  # The declaration must stay on one line and the call must sit inside the try
  # block, exactly as run_thnsparse does it. Splitting "int x =" from its
  # initialiser across two heredoc lines makes cling lose the variable, so the
  # guard below never evaluated: the target printed "Error evaluating
  # expression (__boundary_freeze_result != 0)" and still exited 0, which made
  # every PASS from it uninformative. These boundaries define the percentile
  # classes the whole three-tune comparison is sliced on.
  root -l -b <<ROOTCMDS
.L plotting/improvedPlotting_THnSparse.C+
int __boundary_freeze_result = 0;
try {
  __boundary_freeze_result = freezeMultiplicityBoundaries_THnSparse("${config}");
} catch (const std::exception& error) {
  std::cerr << "ERROR: " << error.what() << std::endl;
  __boundary_freeze_result = 1;
} catch (...) {
  std::cerr << "ERROR: unknown exception while freezing multiplicity boundaries" << std::endl;
  __boundary_freeze_result = 1;
}
if (__boundary_freeze_result != 0) { gSystem->Exit(__boundary_freeze_result); }
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

prepare_legacy_regression_config() {
  local legacy_config="$1"
  jq \
    '.pair_combinatorics_mode = "legacy_identical_ss_half_v1"
     | .same_sign_pair_factor = 0.5
     | .pair_input_selection_contract.mode = "tagged_legacy_recuts_only_v1"' \
    "${THNSPARSE_COMPLETE_ROOT_CONFIG}" > "${legacy_config}"
}

run_legacy_regression() {
  local legacy_config="$1"
  echo
  echo "NONCANONICAL_LEGACY_REGRESSION"
  echo "  This target is diagnostic only and is ineligible for publication."
  echo "  Exact stable-main Paul projection recuts are applied to both"
  echo "  correlation numerators and trigger-normalization denominators."
  echo "  selection_mode=tagged_legacy_recuts_only_v1"
  echo "  pair_combinatorics_mode=legacy_identical_ss_half_v1"
  echo "  same_sign_pair_factor=0.5"
  local status=0
  set +e
  run_thnsparse "${legacy_config}" "NONCANONICAL legacy regression"
  status=$?
  set -e
  return "${status}"
}

run_multiplicity_boundaries() {
  local config="${1:-${MULTIPLICITY_CONFIG}}"
  local compact="${2:-${MULTIPLICITY_COMPACT}}"
  require_file "${config}"

  echo
  echo "==> Running multiplicity-boundaries"
  echo "    config: ${config}"
  echo "    output: ${MULTIPLICITY_OUTPUT_DIR}"
  echo "    compact MONASH: ${compact}"

  root -l -b <<ROOTCMDS
.L plotting/Plot_MultiplicityDistribution_PercentileBoundaries.C+
int __multiplicity_plot_result = 0;
try {
  Plot_MultiplicityDistribution_PercentileBoundaries("${config}", "${MULTIPLICITY_OUTPUT_DIR}", ${MULTIPLICITY_NORMALIZE}, ${MULTIPLICITY_STRICT}, ${compact});
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
.L plotting/Plot_InclusiveKinematicSpectra_Raw.C+
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
.L plotting/Plot_InclusiveKinematicSpectra_Raw.C+
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
  require_file "plotting/FinalAnalysis/Plot_MultiplicityDistributions_TwoSamples.C"
  require_integer "FINAL_NSUB" "${FINAL_NSUB}"

  echo
  echo "==> Running final-multiplicity"
  echo "    independent: ${FINAL_INDEPENDENT_TAG}"
  echo "    combined:    ${FINAL_COMBINED_TAG}"
  echo "    nSub:        ${FINAL_NSUB}"
  echo "    normalize:   ${FINAL_NORMALIZE}"

  root -l -b -q \
    "plotting/FinalAnalysis/Plot_MultiplicityDistributions_TwoSamples.C(\"${FINAL_INDEPENDENT_TAG}\",\"${FINAL_COMBINED_TAG}\",${FINAL_NSUB},${FINAL_NORMALIZE})"
}

run_final_yields() {
  require_file "plotting/FinalAnalysis/Plot_SelectedParticleYields_IndependentVsCombined.C"
  require_integer "FINAL_NSUB" "${FINAL_NSUB}"

  echo
  echo "==> Running final-yields"
  echo "    independent: ${FINAL_INDEPENDENT_TAG}"
  echo "    combined:    ${FINAL_COMBINED_TAG}"
  echo "    nSub:        ${FINAL_NSUB}"

  root -l -b -q \
    "plotting/FinalAnalysis/Plot_SelectedParticleYields_IndependentVsCombined.C(\"${FINAL_INDEPENDENT_TAG}\",\"${FINAL_COMBINED_TAG}\",${FINAL_NSUB})"
}

echo "Hadronization base: ${project_base}"
echo "Targets: ${expanded_targets[*]}"

for target in "${expanded_targets[@]}"; do
  provenance_enabled=false
  provenance_mode=""
  provenance_config=""
  provenance_boundary=false
  provenance_state=""
  provenance_output_roots=()
  legacy_config_to_remove=""

  case "${target}" in
    thnsparse)
      provenance_enabled=true
      provenance_mode="${canonical_pair_provenance_mode}"
      provenance_config="${THNSPARSE_CONFIG}"
      provenance_boundary=true
      ;;
    thnsparse-complete-root)
      provenance_enabled=true
      provenance_mode="${canonical_pair_provenance_mode}"
      provenance_config="${THNSPARSE_COMPLETE_ROOT_CONFIG}"
      provenance_boundary=true
      ;;
    multiplicity-boundaries|multiplicity-compact)
      provenance_enabled=true
      provenance_mode="${canonical_pair_provenance_mode}"
      provenance_config="${MULTIPLICITY_CONFIG}"
      provenance_boundary=true
      provenance_output_roots+=("${MULTIPLICITY_OUTPUT_DIR}")
      ;;
    multiplicity-boundaries-smoke)
      provenance_enabled=true
      provenance_mode="${canonical_pair_provenance_mode}"
      provenance_config="${THNSPARSE_COMPLETE_ROOT_CONFIG}"
      provenance_boundary=true
      provenance_output_roots+=("${MULTIPLICITY_OUTPUT_DIR}")
      ;;
    multiplicity-spectrum|kinematic-spectra)
      provenance_enabled=true
      provenance_mode="${canonical_raw_provenance_mode}"
      provenance_output_roots+=("${KINEMATIC_OUTPUT_DIR}")
      ;;
    legacy-regression)
      if ! command -v jq >/dev/null 2>&1; then
        echo "ERROR: legacy diagnostics require jq." >&2
        exit 1
      fi
      require_file "${THNSPARSE_COMPLETE_ROOT_CONFIG}"
      legacy_config_to_remove="$(
        mktemp "${TMPDIR:-/tmp}/hadronization-legacy-regression.XXXXXX.json"
      )"
      prepare_legacy_regression_config "${legacy_config_to_remove}"
      provenance_enabled=true
      provenance_mode="legacy-pair"
      provenance_config="${legacy_config_to_remove}"
      provenance_boundary=true
      ;;
    final-multiplicity|final-yields)
      provenance_enabled=true
      provenance_mode="legacy-unsealed"
      provenance_output_roots+=("plotting/FinalAnalysis/Plots")
      ;;
  esac

  if [[ "${provenance_enabled}" == "true" && -n "${plot_provenance_tool}" ]]; then
    provenance_state="$(
      mktemp "${TMPDIR:-/tmp}/hadronization-plot-provenance.XXXXXX.json"
    )"
    rm -f -- "${provenance_state}"
    snapshot_arguments=(
      snapshot
      --checkout "${project_base}"
      --state "${provenance_state}"
    )
    if [[ -n "${provenance_config}" ]]; then
      snapshot_arguments+=(--config "${provenance_config}")
    fi
    for output_root in "${provenance_output_roots[@]}"; do
      snapshot_arguments+=(--output-root "${output_root}")
    done
    python3 "${plot_provenance_tool}" "${snapshot_arguments[@]}"
  fi

  case "${target}" in
    multiplicity-boundaries)
      run_multiplicity_boundaries "${MULTIPLICITY_CONFIG}" "${MULTIPLICITY_COMPACT}"
      ;;
    multiplicity-boundaries-smoke)
      run_multiplicity_boundaries "${THNSPARSE_COMPLETE_ROOT_CONFIG}" "${MULTIPLICITY_COMPACT}"
      ;;
    multiplicity-compact)
      run_multiplicity_boundaries "${MULTIPLICITY_CONFIG}" true
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
    freeze-boundaries)
      run_boundary_freeze "${THNSPARSE_CONFIG}" "full-paper"
      ;;
    freeze-boundaries-smoke)
      run_boundary_freeze \
        "${THNSPARSE_COMPLETE_ROOT_CONFIG}" "reduced-smoke"
      ;;
    audit-subsamples)
      run_subsample_coverage_audit
      ;;
    legacy-regression)
      run_legacy_regression "${legacy_config_to_remove}"
      ;;
    validate-inputs)
      "${project_base}/plotting/validate_thnsparse_inputs.sh"
      ;;
    final-multiplicity)
      run_final_multiplicity
      ;;
    final-yields)
      run_final_yields
      ;;
  esac

  if [[ "${provenance_enabled}" == "true" && -n "${plot_provenance_tool}" ]]; then
    record_arguments=(
      record
      --checkout "${project_base}"
      --state "${provenance_state}"
      --target "${target}"
      --command "${requested_command_display}"
      --mode "${provenance_mode}"
    )
    if [[ "${USE_DATASET_SELECTOR:-true}" == "true" ]]; then
      record_arguments+=(--selector "${dataset_selector_path}")
    fi
    if [[ -n "${provenance_config}" ]]; then
      record_arguments+=(--config "${provenance_config}")
    fi
    if [[ -n "${HADRONIZATION_ANALYZED_DATA_BASE:-}" ]]; then
      record_arguments+=(
        --analyzed-data-base "${HADRONIZATION_ANALYZED_DATA_BASE}"
      )
    fi
    if [[ -n "${HADRONIZATION_COMPLETE_ROOT_TAG:-}" ]]; then
      record_arguments+=(
        --complete-root-tag "${HADRONIZATION_COMPLETE_ROOT_TAG}"
      )
    fi
    if [[ -n "${HADRONIZATION_SUBSAMPLE_BASE:-}" ]]; then
      record_arguments+=(
        --subsample-base "${HADRONIZATION_SUBSAMPLE_BASE}"
      )
    fi
    if [[ -n "${HADRONIZATION_PRODUCTION_ROOT:-}" ]]; then
      record_arguments+=(
        --production-root "${HADRONIZATION_PRODUCTION_ROOT}"
      )
    fi
    if [[ "${provenance_boundary}" == "true" ]]; then
      record_arguments+=(--require-boundary-receipt)
    fi
    if [[ "${PLOT_PROVENANCE_DEVELOPMENT}" == "true" ]]; then
      record_arguments+=(--development)
    fi
    python3 "${plot_provenance_tool}" "${record_arguments[@]}"
    rm -f -- "${provenance_state}"
  fi
  if [[ -n "${legacy_config_to_remove}" ]]; then
    rm -f -- "${legacy_config_to_remove}"
  fi
done

echo
echo "Paper plotting targets completed."
