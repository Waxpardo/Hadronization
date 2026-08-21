#!/bin/bash
# Report what this machine can and cannot do. Never fails: the point is to
# tell you what is missing, not to stop you.
#
# Every path printed here is resolved from config/dependencies.conf and
# config/dependencies.local.conf. If something is wrong, that is where to fix
# it -- no tracked script contains a machine-specific path.

set -uo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_base="$(cd "${script_dir}/.." && pwd)"

ok=0
warn=0
bad=0

say_ok()   { printf '  [ ok ] %s\n' "$1"; ok=$((ok+1)); }
say_warn() { printf '  [warn] %s\n' "$1"; warn=$((warn+1)); }
say_bad()  { printf '  [ NO ] %s\n' "$1"; bad=$((bad+1)); }

echo "Hadronization workspace check"
echo "  checkout: ${project_base}"
echo

echo "Configuration"
if [[ -f "${project_base}/config/dependencies.conf" ]]; then
  say_ok "config/dependencies.conf"
else
  say_bad "config/dependencies.conf is missing"
fi
if [[ -f "${project_base}/config/dependencies.local.conf" ]]; then
  say_ok "config/dependencies.local.conf (machine overrides active)"
else
  say_warn "no config/dependencies.local.conf -- using tracked defaults; 'make setup' to create one"
fi

# Resolve the configured values without running the full environment setup,
# so this works even where CVMFS is absent.
# shellcheck source=/dev/null
if [[ -f "${project_base}/config/dependencies.local.conf" ]]; then
  source "${project_base}/config/dependencies.local.conf" 2>/dev/null || true
fi
# shellcheck source=/dev/null
source "${project_base}/config/dependencies.conf" 2>/dev/null || true

echo
echo "Dependencies"
if [[ -d "${HF_PYTHIA8_PREFIX:-}" ]]; then
  say_ok "PYTHIA ${HF_PYTHIA8_VERSION:-?} at ${HF_PYTHIA8_PREFIX}"
else
  say_bad "PYTHIA prefix not found: ${HF_PYTHIA8_PREFIX:-<unset>}"
fi
if [[ -d "${HF_ROOT_PREFIX:-}" ]]; then
  say_ok "ROOT ${HF_ROOT_VERSION:-?} at ${HF_ROOT_PREFIX}"
else
  say_bad "ROOT prefix not found: ${HF_ROOT_PREFIX:-<unset>}"
fi
if [[ -d /cvmfs/alice.cern.ch ]]; then
  say_ok "CVMFS /cvmfs/alice.cern.ch is mounted"
else
  say_warn "CVMFS is not mounted -- producer builds and ROOT macros will not run here"
fi
for tool in python3 git make; do
  if command -v "${tool}" >/dev/null 2>&1; then
    say_ok "${tool} ($(command -v "${tool}"))"
  else
    say_bad "${tool} not on PATH"
  fi
done
if command -v condor_submit >/dev/null 2>&1; then
  say_ok "condor_submit ($(command -v condor_submit))"
else
  say_warn "condor_submit not on PATH -- submits can be rendered but not queued here"
fi

echo
echo "Storage"
production_root="${HF_PRODUCTION_ROOT:-${project_base}/Production}"
if [[ "${production_root}" == "${project_base}"* ]]; then
  say_warn "production root is inside the checkout (${production_root})"
  printf '         set HF_PRODUCTION_ROOT in config/dependencies.local.conf\n'
else
  say_ok "production root ${production_root}"
fi
if [[ -d "${production_root}" ]]; then
  avail="$(df -Pk "${production_root}" 2>/dev/null | awk 'NR==2 {printf "%.1f", $4/1048576}')"
  if [[ -n "${avail}" ]]; then
    say_ok "free space at production root: ${avail} GiB"
    # ~0.9 GB per 1M events observed; 4 tunes x 100M events ~ 356 GB.
    if awk "BEGIN {exit !(${avail} < 400)}"; then
      say_warn "a full 4-tune 100M/tune campaign needs roughly 360 GiB"
    fi
  fi
else
  say_warn "production root does not exist yet: ${production_root}"
fi

echo
echo "Build products"
if [[ -x "${project_base}/generation/producer/heavyflavourcorrelations_status" ]]; then
  say_ok "producer binary is built"
else
  say_warn "producer not built -- run 'make build' (needs ROOT + PYTHIA)"
fi

echo
echo "Repository"
if git -C "${project_base}" rev-parse HEAD >/dev/null 2>&1; then
  say_ok "git HEAD $(git -C "${project_base}" rev-parse --short HEAD)"
  if [[ -n "$(git -C "${project_base}" status --porcelain=v1 --untracked-files=no)" ]]; then
    say_warn "tracked changes present -- submission is refused until committed"
  else
    say_ok "checkout is tracked-clean"
  fi
else
  say_bad "not a git checkout"
fi

echo
printf 'Summary: %d ok, %d warnings, %d blocking\n' "${ok}" "${warn}" "${bad}"
if (( bad > 0 )); then
  echo "Blocking items must be fixed in config/dependencies.local.conf before"
  echo "the producer can be built or run on this machine."
fi
exit 0
