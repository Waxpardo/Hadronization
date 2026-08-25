#!/bin/bash
# Report whether `make check` used the pinned ROOT and an available PYTHIA.
# Source-only tests remain useful elsewhere, but they do not certify the runtime.
# HF_ALLOW_UNPINNED_ENV=1 makes that limited scope explicit in the transcript.
set -uo pipefail

project_base="${1:-${HADRONIZATION_BASE:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}}"
project_base="${project_base%/}"
# Absolutise it. The probe below hands this to the local profile as
# HADRONIZATION_BASE, and a relative argument would make that profile report a
# relative data root -- a defect the caller invented, not one the tree has.
project_base="$(cd "${project_base}" 2>/dev/null && pwd)" || project_base="${1:-.}"

want_root=""
want_pythia=""
if [[ -f "${project_base}/config/dependencies.conf" ]]; then
  want_root="$(sed -n 's/^: "\${HF_ROOT_VERSION:=\([^}]*\)}".*/\1/p' \
    "${project_base}/config/dependencies.conf" | head -1)"
  want_pythia="$(sed -n 's/^: "\${HF_PYTHIA8_VERSION:=\([^}]*\)}".*/\1/p' \
    "${project_base}/config/dependencies.conf" | head -1)"
fi
[[ -z "${want_root}" ]] && want_root="(unreadable from config/dependencies.conf)"
[[ -z "${want_pythia}" ]] && want_pythia="(unreadable from config/dependencies.conf)"

have_root="ABSENT"
root_path="not on PATH"
if command -v root >/dev/null 2>&1; then
  root_path="$(command -v root)"
  have_root="$(root-config --version 2>/dev/null || echo 'UNKNOWN')"
fi

pythia="ABSENT"
if command -v pythia8-config >/dev/null 2>&1; then
  pythia="$(pythia8-config --version 2>/dev/null || echo 'present, version unknown')"
fi

cvmfs="ABSENT"
[[ -d /cvmfs/alice.cern.ch ]] && cvmfs="present"

# ---------------------------------------------------------------------------
# Site profile: the data plane must resolve without the environment.
#
# config/sites/nikhef.conf built every data root from /data/alice/${USER}/hf.
# tools/render_production_submit.py emits `getenv = False` and no
# `environment =` line, so a Condor job starts with an empty environment:
# ${USER} was empty on the execute node, /data/alice//hf collapsed to the shared
# /data/alice/hf, and the first HF_SMOKE3 pilot wrote outside the account
# because that path still resolved. The profiles now refuse instead.
#
# Everything below is therefore BLOCKING, not advisory. After that fix, a
# malformed data root or an account name that resolves empty can only mean a new
# defect, and HF_ALLOW_UNPINNED_ENV does not cover it: an off-pin laptop runtime
# is a declared concession, while a data root that points at the wrong directory
# is a defect wherever it is found.
site_blocking=()
site_guard="${project_base}/config/sites/site_guard.sh"
site="${HADRONIZATION_SITE:-}"
site_profile="(not resolved)"
site_live_root="${HADRONIZATION_DATA_ROOT:-}"
site_probe_root="(not resolved)"
site_probe_account="(not resolved)"
site_stripped_account="(not resolved)"

if [[ ! -f "${site_guard}" ]]; then
  site="${site:-(unknown)}"
  site_blocking+=("the shared site guard is missing: ${site_guard}")
else
  # shellcheck source=/dev/null
  source "${site_guard}"
  [[ -z "${site}" ]] && site="$(hf_site_detect)"
  site_profile="$(hf_site_profile_path "${project_base}" "${site}")"

  # The account name, resolved with no environment at all: an account segment
  # that resolves empty under `env -i` is the condition this block exists for.
  # PATH is passed because `id` is a program and must be found; USER, LOGNAME
  # and HOME are deliberately absent. Call hf_site_account rather than `id`
  # directly, so the verdict cannot report an account the profile would reject:
  # hf_site_account discards output when `id` exits non-zero, and a second copy
  # of that rule here would drift from the one the profiles use.
  site_stripped_account="$(env -i PATH="${PATH}" bash -c \
    'source "$1"; hf_site_account' _ "${site_guard}")"
  if [[ -z "${site_stripped_account}" ]]; then
    site_stripped_account="(empty)"
    site_blocking+=("the account name resolves empty without the environment; 'id -un' produced nothing under env -i")
  fi

  if [[ ! -f "${site_profile}" ]]; then
    site_blocking+=("the ${site} site profile is missing: ${site_profile}")
  else
    # Source the profile setupEnv.sh would source, with the environment stripped.
    # HADRONIZATION_BASE is passed because setupEnv.sh derives it from the
    # location of setupEnv.sh rather than from the environment; the local
    # profile legitimately needs it. Nothing else is passed.
    site_probe_err="$(mktemp)"
    site_probe_out="$(env -i PATH="${PATH}" HADRONIZATION_BASE="${project_base}" \
      bash -c 'source "$1" || exit 3
               printf "%s\n%s\n" "${HADRONIZATION_DATA_ROOT:-}" "${HADRONIZATION_SITE_ACCOUNT:-}"' \
      _ "${site_profile}" 2>"${site_probe_err}")"
    site_probe_status=$?
    site_probe_reason="$(head -1 "${site_probe_err}")"
    rm -f "${site_probe_err}"
    if [[ "${site_probe_status}" -ne 0 ]]; then
      site_probe_root="(refused)"
      site_probe_account="(refused)"
      site_probe_reason="${site_probe_reason#"ERROR: "}"
      site_blocking+=("without the environment: ${site_probe_reason:-${site_profile} exited ${site_probe_status}}")
    else
      site_probe_root="$(printf '%s\n' "${site_probe_out}" | sed -n '1p')"
      site_probe_account="$(printf '%s\n' "${site_probe_out}" | sed -n '2p')"
      [[ -z "${site_probe_account}" ]] &&
        site_probe_account="(none; this profile builds no account segment)"
      site_probe_reason="$(hf_site_root_problem HADRONIZATION_DATA_ROOT \
        "${site_probe_root}")" ||
        site_blocking+=("without the environment, ${site_probe_reason}")
    fi
  fi

  # The value this shell actually carries, when setupEnv.sh has been sourced.
  # An untracked config/site.local.conf and an exported override both land here.
  if [[ -n "${site_live_root}" ]]; then
    site_live_reason="$(hf_site_root_problem HADRONIZATION_DATA_ROOT \
      "${site_live_root}")" ||
      site_blocking+=("in this environment, ${site_live_reason}")
  else
    site_live_root="(not set; setupEnv.sh has not been sourced here)"
  fi
fi

problems=()
[[ "${have_root}" == "ABSENT" ]] && problems+=("ROOT is not on PATH")
[[ "${have_root}" != "ABSENT" && "${have_root}" != "${want_root}" ]] &&
  problems+=("ROOT is ${have_root}, pinned is ${want_root}")
[[ "${pythia}" == "ABSENT" ]] && problems+=("PYTHIA is absent (no pythia8-config)")
[[ "${pythia}" != "ABSENT" && "${pythia}" != "${want_pythia}" ]] &&
  problems+=("PYTHIA is ${pythia}, pinned is ${want_pythia}")

echo
echo "======================================================================"
echo "ENVIRONMENT VERDICT"
echo "======================================================================"
printf '  %-22s %s\n' "ROOT pinned:" "${want_root}"
printf '  %-22s %s   (%s)\n' "ROOT found:" "${have_root}" "${root_path}"
printf '  %-22s %s\n' "PYTHIA pinned:" "${want_pythia}"
printf '  %-22s %s\n' "PYTHIA found:" "${pythia}"
printf '  %-22s %s\n' "CVMFS alice.cern.ch:" "${cvmfs}"
echo "----------------------------------------------------------------------"
printf '  %-22s %s\n' "site:" "${site}"
printf '  %-22s %s\n' "site profile:" "${site_profile}"
printf '  %-22s %s\n' "data root here:" "${site_live_root}"
printf '  %-22s %s\n' "data root, env -i:" "${site_probe_root}"
printf '  %-22s %s\n' "account, env -i:" "${site_stripped_account}"
printf '  %-22s %s\n' "account in the root:" "${site_probe_account}"
echo "----------------------------------------------------------------------"

if [[ ${#site_blocking[@]} -ne 0 ]]; then
  echo "  VERDICT: SITE PROFILE DEFECT -- the data plane does not resolve safely."
  for site_problem in "${site_blocking[@]}"; do
    echo "    - ${site_problem}"
  done
  echo
  echo "  This is blocking. A data root that carries an empty path segment is a"
  echo "  valid path to the wrong directory: /data/alice//hf collapses to the"
  echo "  shared /data/alice/hf. The site profiles refuse that shape, so reaching"
  echo "  this verdict means the refusal has been removed or bypassed."
  echo "  HF_ALLOW_UNPINNED_ENV declares an off-pin RUNTIME. It does not apply"
  echo "  here and does not suppress this."
  echo "======================================================================"
  exit 1
fi

if [[ ${#problems[@]} -eq 0 ]]; then
  echo "  VERDICT: PINNED RUNTIME."
  echo
  echo "  Even so, a green suite is a SOURCE-CONTRACT result. It does not run"
  echo "  the 300-file merged product, the current plotting chain, or the"
  echo "  published extraction. See README S'What make check does not certify'."
  echo "======================================================================"
  exit 0
fi

echo "  VERDICT: OFF-PIN RUNTIME -- this host cannot run the pipeline."
for problem in "${problems[@]}"; do
  echo "    - ${problem}"
done
echo
echo "  A green test suite here certifies the SOURCE CONTRACTS only. It does"
echo "  NOT certify the runtime, and it is not a pipeline result:"
echo "    - the ROOT-dependent tests compiled against an unpinned ROOT;"
echo "    - the PYTHIA runtime contract passes vacuously when PYTHIA is absent;"
echo "    - no test runs the merged product, the plotting chain, or the"
echo "      published extraction."
echo
echo "  To proceed anyway -- which is normal for laptop work -- set:"
echo "      HF_ALLOW_UNPINNED_ENV=1 make check"
echo "  so that the concession is explicit and appears in the transcript."
echo "======================================================================"

if [[ "${HF_ALLOW_UNPINNED_ENV:-0}" == "1" ]]; then
  echo "HF_ALLOW_UNPINNED_ENV=1 -- off-pin environment accepted by declaration."
  echo "This run is NOT a pinned-runtime certification."
  exit 0
fi
exit 1
