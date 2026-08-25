#!/bin/bash
# Global setupEnv.sh for Hadronization
#
# Dependency locations and pinned versions live in config/dependencies.conf,
# not in this script.  Override machine-specific paths in
# config/dependencies.local.conf (untracked) or by exporting the variables
# before sourcing this file.  See config/dependencies.local.conf.example.

# IMPORTANT: do NOT use 'set -e' or 'set -u' here; this script is sourced, so
# set -e would exit the parent shell on any error, and ALICE login.sh expects
# some vars to be unset.
setupenv_restore_errexit=0
setupenv_restore_nounset=0
case "$-" in
  *e*)
    setupenv_restore_errexit=1
    set +e
    ;;
esac
case "$-" in
  *u*)
    setupenv_restore_nounset=1
    set +u
    ;;
esac

# Put the caller's shell options back before refusing. A sourced script cannot
# force its caller to stop; it can only return a status, and a caller with
# `set -e` acts on that status only while errexit is on. The block above turns
# errexit off, so a refusal that returns without this call leaves the caller
# running AND leaves its errexit off for the rest of the job. That is what
# happened on the first HF_SMOKE3 pilot: the PYTHIA refusal below printed its
# error and generation/submit/runCondorJob.sh ran the producer anyway.
#
# SCOPE. Only the site-resolution refusals call this, and the normal exit at the
# end of the file. The eleven dependency and runtime refusals below -- the PYTHIA
# one among them -- still return with the caller's errexit off, so they still do
# not stop a worker. Closing that is a separate change and is reported, not made
# here.
setupenv_restore_shell_flags() {
  if [[ "${setupenv_restore_errexit}" -eq 1 ]]; then
    set -e
  fi
  if [[ "${setupenv_restore_nounset}" -eq 1 ]]; then
    set -u
  fi
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -n "${HADRONIZATION_BASE:-}" && -d "${HADRONIZATION_BASE%/}/plotting" ]]; then
  HADRONIZATION_BASE="${HADRONIZATION_BASE%/}"
elif [ -f "${SCRIPT_DIR}/base_path.txt" ]; then
  HADRONIZATION_BASE="$(cat "${SCRIPT_DIR}/base_path.txt")"
else
  HADRONIZATION_BASE="${SCRIPT_DIR}"
fi
HADRONIZATION_BASE="${HADRONIZATION_BASE%/}"
export HADRONIZATION_BASE

# Resolve the execution site before dependency and dataset paths. Nikhef is the
# authoritative full-pipeline environment; local is a source-development
# profile. A user may override either with config/site.local.conf or exported
# variables, without editing tracked files.
setupenv_site_guard="${SCRIPT_DIR}/config/sites/site_guard.sh"
if [[ ! -f "${setupenv_site_guard}" ]]; then
  echo "ERROR: the shared site guard is missing: ${setupenv_site_guard}" >&2
  setupenv_restore_shell_flags
  return 1 2>/dev/null || exit 1
fi
# shellcheck source=/dev/null
source "${setupenv_site_guard}"
if [[ -z "${HADRONIZATION_SITE:-}" ]]; then
  HADRONIZATION_SITE="$(hf_site_detect)"
fi
setupenv_site_conf="${SCRIPT_DIR}/config/sites/${HADRONIZATION_SITE}.conf"
setupenv_site_local_conf="${SCRIPT_DIR}/config/site.local.conf"
setupenv_site_status=0
# Name the file that supplied the values. An untracked config/site.local.conf
# replaces the tracked profile, so a message that says "the local site profile"
# would point the reader at a tracked file that never ran.
if [[ -f "${setupenv_site_local_conf}" ]]; then
  setupenv_site_source="config/site.local.conf"
  # shellcheck source=/dev/null
  source "${setupenv_site_local_conf}"
  setupenv_site_status=$?
elif [[ -f "${setupenv_site_conf}" ]]; then
  setupenv_site_source="config/sites/${HADRONIZATION_SITE}.conf"
  # shellcheck source=/dev/null
  source "${setupenv_site_conf}"
  setupenv_site_status=$?
else
  echo "ERROR: unknown HADRONIZATION_SITE=${HADRONIZATION_SITE}; expected a profile at ${setupenv_site_conf}" >&2
  setupenv_restore_shell_flags
  return 1 2>/dev/null || exit 1
fi
# A profile that refuses must stop the run. Read its status; a sourced file can
# report a refusal only this way.
if [[ "${setupenv_site_status}" -ne 0 ]]; then
  echo "ERROR: ${setupenv_site_source} refused; no dependency, dataset or output path is set up." >&2
  setupenv_restore_shell_flags
  return 1 2>/dev/null || exit 1
fi
: "${HADRONIZATION_RESULTS_ROOT:=${HADRONIZATION_DATA_ROOT:-}/project/results}"
# Check every root that survived, whatever supplied it. config/site.local.conf
# replaces the tracked profile and its refusals, and an exported value beats
# both, so a shape that the tracked profiles refuse can still arrive here. The
# siblings are checked too: config/site.local.conf.example invites the reader to
# set HF_PRODUCTION_ROOT on its own, and that variable decides where hundreds of
# gigabytes of raw campaign output land.
if ! hf_site_check_root "${setupenv_site_source}" HADRONIZATION_DATA_ROOT \
     "${HADRONIZATION_DATA_ROOT:-}"; then
  setupenv_restore_shell_flags
  return 1 2>/dev/null || exit 1
fi
# The siblings are checked when they carry a value. config/site.local.conf
# replaces the tracked profile, and it may legitimately leave a sibling unset
# for a run that never reaches that plane; a value that IS set has to be usable.
for setupenv_root_name in HADRONIZATION_ANALYSIS_ROOT HADRONIZATION_MERGED_ROOT \
    HADRONIZATION_SYSTEMATICS_ROOT HADRONIZATION_RESULTS_ROOT HF_PRODUCTION_ROOT; do
  eval "setupenv_root_value=\"\${${setupenv_root_name}:-}\""
  [[ -z "${setupenv_root_value}" ]] && continue
  if ! hf_site_check_root "${setupenv_site_source}" "${setupenv_root_name}" \
       "${setupenv_root_value}"; then
    unset setupenv_root_name setupenv_root_value
    setupenv_restore_shell_flags
    return 1 2>/dev/null || exit 1
  fi
done
unset setupenv_root_name setupenv_root_value
# HADRONIZATION_SITE_ACCOUNT records the account name a profile put into the
# data root, so `hadronization site` and the environment verdict can name it.
# The local profile builds no account segment and leaves it unset.
export HADRONIZATION_SITE HADRONIZATION_SITE_ACCOUNT HADRONIZATION_DATA_ROOT
export HADRONIZATION_ANALYSIS_ROOT HADRONIZATION_MERGED_ROOT
export HADRONIZATION_SYSTEMATICS_ROOT HADRONIZATION_RESULTS_ROOT
export HF_PRODUCTION_ROOT

# 0. Resolve dependency locations.
#
# The local override is sourced first: every entry uses ": ${NAME:=value}", so
# whichever file runs first wins, and an already-exported environment variable
# beats both.  Precedence is environment > local > tracked defaults.
setupenv_default_conf="${SCRIPT_DIR}/config/dependencies.conf"
setupenv_local_conf="${SCRIPT_DIR}/config/dependencies.local.conf"
if [[ -n "${HADRONIZATION_DEPENDENCIES_CONF:-}" ]]; then
  if [[ ! -f "${HADRONIZATION_DEPENDENCIES_CONF}" ]]; then
    echo "ERROR: HADRONIZATION_DEPENDENCIES_CONF does not exist: ${HADRONIZATION_DEPENDENCIES_CONF}" >&2
    return 1 2>/dev/null || exit 1
  fi
  # shellcheck source=/dev/null
  source "${HADRONIZATION_DEPENDENCIES_CONF}"
else
  if [[ -f "${setupenv_local_conf}" ]]; then
    # shellcheck source=/dev/null
    source "${setupenv_local_conf}"
  fi
  if [[ ! -f "${setupenv_default_conf}" ]]; then
    echo "ERROR: dependency configuration is missing: ${setupenv_default_conf}" >&2
    return 1 2>/dev/null || exit 1
  fi
  # shellcheck source=/dev/null
  source "${setupenv_default_conf}"
fi

# 1. Get alienv from ALICE CVMFS (only available on the cluster)
if [ -f /cvmfs/alice.cern.ch/etc/login.sh ]; then
  # Temporarily ensure nounset is off in case the parent shell had it
  set +u 2>/dev/null || true
  # shellcheck source=/dev/null
  source /cvmfs/alice.cern.ch/etc/login.sh

  # 2. Load ROOT into THIS shell (no subshells).
  #
  # PYTHIA is deliberately NOT loaded through alienv.  The generator is now a
  # locally built stock upstream release rather than a CVMFS package, and an
  # alienv-provided PYTHIA would silently take precedence on PATH and
  # LD_LIBRARY_PATH over the configured one.
  if [[ -n "${HF_ROOT_ALIENV_PACKAGE:-}" ]]; then
    eval "$(alienv printenv "${HF_ROOT_ALIENV_PACKAGE}" 2>/dev/null)"
  fi

  # Some Nikhef non-interactive shells cannot initialise alienv's Tcl
  # interpreter. Keep batch plotting reproducible by falling back to the same
  # EL9 ROOT build and its runtime dependencies directly from CVMFS.
  if ! command -v root >/dev/null 2>&1; then
    gcc_package="${HF_ROOT_GCC_PREFIX}"
    root_package="${HF_ROOT_PREFIX}"
    if [[ ! -x "${root_package}/bin/thisroot.sh" && ! -f "${root_package}/bin/thisroot.sh" ]]; then
      echo "ERROR: pinned ROOT package is unavailable: ${root_package}" >&2
      echo "       Set HF_ROOT_PREFIX in config/dependencies.local.conf." >&2
      return 1 2>/dev/null || exit 1
    fi
    root_runtime_libs=""
    for setupenv_lib_dir in "${HF_ROOT_RUNTIME_LIB_DIRS[@]}"; do
      root_runtime_libs="${root_runtime_libs:+${root_runtime_libs}:}${setupenv_lib_dir}"
    done
    unset setupenv_lib_dir
    export LD_LIBRARY_PATH="${root_runtime_libs}:${root_package}/lib${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}"
    export PATH="${gcc_package}/bin:${PATH}"
    export ROOT_DYN_PATH="${root_package}/lib"
    # shellcheck source=/dev/null
    source "${root_package}/bin/thisroot.sh"
  fi

  # 3. Pin PYTHIA from the dependency configuration.
  #
  # This block is unconditional.  It used to run only when alienv had failed to
  # populate PYTHIA8, which was safe while both routes resolved to the same
  # CVMFS package; it is not safe now that the configured PYTHIA differs from
  # anything alienv might supply.
  pythia_package="${HF_PYTHIA8_PREFIX%/}"
  pythia_gcc_package="${HF_PYTHIA8_GCC_PREFIX%/}"
  if [[ ! -x "${pythia_package}/bin/pythia8-config" ]]; then
    echo "ERROR: pinned PYTHIA package is unavailable: ${pythia_package}" >&2
    echo "       Set HF_PYTHIA8_PREFIX in config/dependencies.local.conf." >&2
    return 1 2>/dev/null || exit 1
  fi
  if [[ ! -x "${pythia_gcc_package}/bin/g++" ]]; then
    echo "ERROR: pinned PYTHIA compiler runtime is unavailable: ${pythia_gcc_package}" >&2
    return 1 2>/dev/null || exit 1
  fi
  if [[ ! -f "${pythia_package}/share/Pythia8/xmldoc/Index.xml" ]]; then
    echo "ERROR: pinned PYTHIA data are unavailable: ${pythia_package}/share/Pythia8/xmldoc/Index.xml" >&2
    return 1 2>/dev/null || exit 1
  fi
  if [[ ! -e "${pythia_package}/lib/libpythia8.so" ]]; then
    echo "ERROR: pinned PYTHIA shared library is unavailable: ${pythia_package}/lib/libpythia8.so" >&2
    return 1 2>/dev/null || exit 1
  fi
  export PYTHIA8="${pythia_package}"
  export PYTHIA8DATA="${pythia_package}/share/Pythia8/xmldoc"
  export PATH="${pythia_gcc_package}/bin:${pythia_package}/bin:${PATH}"
  export LD_LIBRARY_PATH="${pythia_gcc_package}/lib64:${pythia_package}/lib${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}"
  export ROOT_INCLUDE_PATH="${pythia_package}/include${ROOT_INCLUDE_PATH:+:${ROOT_INCLUDE_PATH}}"

  # alienv may provide a usable library/config executable without exporting
  # the XML data directory. Never let PYTHIA fall back to a compiled-in path
  # from the package build host.
  if [[ -n "${PYTHIA8:-}" && -z "${PYTHIA8DATA:-}" ]]; then
    pythia_data_candidate="${PYTHIA8%/}/share/Pythia8/xmldoc"
    if [[ -f "${pythia_data_candidate}/Index.xml" ]]; then
      export PYTHIA8DATA="${pythia_data_candidate}"
    else
      echo "ERROR: PYTHIA8DATA is unset and no runtime XML data exist under ${pythia_data_candidate}" >&2
      return 1 2>/dev/null || exit 1
    fi
  fi
  if [[ -n "${PYTHIA8DATA:-}" && ! -f "${PYTHIA8DATA%/}/Index.xml" ]]; then
    echo "ERROR: PYTHIA8DATA does not contain Index.xml: ${PYTHIA8DATA}" >&2
    return 1 2>/dev/null || exit 1
  fi

  # 4. Assert the pinned versions.
  #
  # A CVMFS package path encoded its own version, so a silent substitution was
  # impossible.  A locally built prefix carries no such guarantee: rebuilding
  # in place would change the generator while every recorded path stayed
  # identical.  Ask the tools what they actually are.
  setupenv_pythia_actual="$("${pythia_package}/bin/pythia8-config" --version 2>/dev/null)"
  if [[ "${setupenv_pythia_actual}" != "${HF_PYTHIA8_VERSION}" ]]; then
    echo "ERROR: PYTHIA version mismatch under ${pythia_package}" >&2
    echo "       configured HF_PYTHIA8_VERSION=${HF_PYTHIA8_VERSION}" >&2
    echo "       reported by pythia8-config=${setupenv_pythia_actual:-'(none)'}" >&2
    return 1 2>/dev/null || exit 1
  fi
  if command -v root-config >/dev/null 2>&1; then
    setupenv_root_actual="$(root-config --version 2>/dev/null)"
    if [[ "${setupenv_root_actual}" != "${HF_ROOT_VERSION}" ]]; then
      echo "ERROR: ROOT version mismatch" >&2
      echo "       configured HF_ROOT_VERSION=${HF_ROOT_VERSION}" >&2
      echo "       reported by root-config=${setupenv_root_actual:-'(none)'}" >&2
      return 1 2>/dev/null || exit 1
    fi
  fi
else
  echo "WARNING: CVMFS not available — ROOT and PYTHIA not loaded via alienv."
  echo "         Run this script on the Nikhef cluster to get the full environment."
fi

# Where production output is written.  Deliberately separate from the code
# checkout: raw output for a 100M-event-per-tune campaign runs to hundreds of
# gigabytes and must not live inside a git working tree.  Set
# HF_PRODUCTION_ROOT in config/dependencies.local.conf on any machine with real
# storage; the in-checkout default only suits a smoke test.
: "${HF_PRODUCTION_ROOT:=${HADRONIZATION_BASE}/Production}"
# By this point HF_PRODUCTION_ROOT may come from the environment, from
# config/dependencies.local.conf, from the site profile, or from the default
# just applied, so the message names every place worth looking.
if ! hf_site_check_root \
     "config/dependencies.local.conf, ${setupenv_site_source}, or the environment" \
     HF_PRODUCTION_ROOT "${HF_PRODUCTION_ROOT}"; then
  setupenv_restore_shell_flags
  return 1 2>/dev/null || exit 1
fi
export HF_PRODUCTION_ROOT

# The pins and their resolved prefixes must cross the process boundary. The
# unified command invokes Make, which launches the doctor, build scripts and
# validators in child shells; leaving a site-profile prefix shell-local made a
# fresh Nikhef checkout work in the parent but appear unconfigured to `make
# check`.
export HF_PYTHIA8_PREFIX HF_PYTHIA8_VERSION HF_PYTHIA8_GCC_PREFIX
export HF_ROOT_PREFIX HF_ROOT_VERSION HF_ROOT_GCC_PREFIX HF_ROOT_ALIENV_PACKAGE

if [[ "${SETUPENV_QUIET:-0}" -ne 1 ]]; then
  echo "Environment set:"
  echo "  which root:        $(command -v root || echo 'not found')"
  echo "  which root-config: $(command -v root-config || echo 'not found')"
  echo "  PYTHIA8:           ${PYTHIA8:-'(not set)'}"
  echo "  PYTHIA8DATA:       ${PYTHIA8DATA:-'(not set)'}"
  echo "  PYTHIA8 version:   ${HF_PYTHIA8_VERSION:-'(not set)'}"
  echo "  ROOT version:      ${HF_ROOT_VERSION:-'(not set)'}"
  echo "  production root:   ${HF_PRODUCTION_ROOT}"
fi

unset setupenv_default_conf setupenv_local_conf
unset setupenv_site_conf setupenv_site_local_conf
unset setupenv_site_guard setupenv_site_status setupenv_site_source
unset setupenv_pythia_actual setupenv_root_actual

setupenv_restore_shell_flags
unset -f setupenv_restore_shell_flags
unset -f hf_site_refuse hf_site_account hf_site_check_root hf_site_root_problem
unset -f hf_site_detect hf_site_profile_path
