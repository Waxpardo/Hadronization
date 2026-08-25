# Shared refusal logic for every site profile in this directory.
#
# Each config/sites/*.conf sources this file, and so does
# tools/environment_verdict.sh. It defines functions and sets no variables, so
# sourcing it more than once changes nothing.
#
# Why it exists. config/sites/nikhef.conf built every data root from
# /data/alice/${USER}/hf. tools/render_production_submit.py emits
# `getenv = False` and no `environment =` line, so a Condor job starts with an
# empty environment: ${USER} expands to nothing on the execute node,
# /data/alice//hf collapses to the shared /data/alice/hf, and the first
# HF_SMOKE3 pilot resolved that path, failed to find PYTHIA below it, and wrote
# outside the account. The path was valid, so nothing refused. That is the
# fallback trap in PRACTICE section 12: an empty variable inside a path leaves a
# path that still resolves.
#
# The functions below therefore refuse instead of substituting a value: no
# default of any shape stands behind a data root. hf_site_detect is the one
# exception and it is about site SELECTION, not about a path -- it answers
# `local` on any host without Nikhef storage and CVMFS.

hf_site_refuse() {
  # $1 the file that supplied the value, $2... the reason. Always returns 1.
  # Name the file rather than the site: an untracked config/site.local.conf
  # replaces the tracked profile, and a message naming the site would send the
  # reader to a file that never ran.
  local hf_site_source="$1"
  shift
  printf 'ERROR: cannot resolve the data plane from %s: %s\n' \
    "${hf_site_source}" "$*" >&2
  printf '       No default stands behind this value. Correct it where it is\n' >&2
  printf '       set and run again.\n' >&2
  return 1
}

hf_site_account() {
  # Print the account name, taken from the process credential instead of the
  # environment. `id -un` reads the effective user id, so it needs no
  # environment variable and it answers correctly inside a Condor job started
  # with getenv = False. Print nothing when it cannot answer; the caller
  # refuses.
  local hf_site_account_value
  hf_site_account_value="$(id -un 2>/dev/null)" || hf_site_account_value=""
  printf '%s' "${hf_site_account_value}"
}

hf_site_root_problem() {
  # $1 variable name, $2 resolved value. Print the reason the value is unusable
  # and return 1, or print nothing and return 0. The rules live here once:
  # config/sites/*.conf refuse with them and tools/environment_verdict.sh
  # reports with them. A value is unusable when it is empty, relative, carries
  # an empty path segment, ends with a separator, carries a . or .. segment, or
  # contains a newline. Every one of those still names a real directory, which
  # is why each has to be refused rather than resolved.
  local hf_site_var="$1" hf_site_value="$2"
  if [[ -z "${hf_site_value}" ]]; then
    printf '%s is empty' "${hf_site_var}"
    return 1
  fi
  if [[ "${hf_site_value}" != /* ]]; then
    printf '%s is relative, so it resolves against the current directory: %s=%s' \
      "${hf_site_var}" "${hf_site_var}" "${hf_site_value}"
    return 1
  fi
  if [[ "${hf_site_value}" == *//* ]]; then
    printf '%s carries an empty path segment, which collapses to a different directory: %s=%s' \
      "${hf_site_var}" "${hf_site_var}" "${hf_site_value}"
    return 1
  fi
  if [[ "${hf_site_value}" == */ ]]; then
    printf '%s ends with a separator, so every child path below it carries an empty segment: %s=%s' \
      "${hf_site_var}" "${hf_site_var}" "${hf_site_value}"
    return 1
  fi
  if [[ "${hf_site_value}" == */../* || "${hf_site_value}" == */.. \
        || "${hf_site_value}" == */./* || "${hf_site_value}" == */. ]]; then
    printf '%s carries a . or .. segment, so it names a directory other than the one it reads as: %s=%s' \
      "${hf_site_var}" "${hf_site_var}" "${hf_site_value}"
    return 1
  fi
  if [[ "${hf_site_value}" == *$'\n'* ]]; then
    printf '%s contains a newline, which no tool that reports a path can quote: %s' \
      "${hf_site_var}" "${hf_site_var}"
    return 1
  fi
  return 0
}

hf_site_require_account_dir() {
  # $1 the file that supplied the value, $2 the storage parent, $3 the account.
  #
  # The pool-account guard. `id -un` answers which account THIS PROCESS runs
  # as, not which account submitted the job. Under a pool, glidein or
  # uid-mapped account it returns a different name, and the root built from it
  # is absolute, carries no empty segment and ends in no separator, so every
  # shape rule above accepts it. The directory is what separates the two cases:
  # an account with storage has one and a pool account does not.
  # generation/submit/runCondorJob.sh runs `mkdir -p` on the resolved root, so
  # without this assertion a wrong account creates its own tree and the job
  # succeeds into a directory nobody will look in. The same assertion catches a
  # typo in an exported HADRONIZATION_DATA_ROOT and a storage mount that did
  # not come up on the execute node.
  local hf_site_source="$1" hf_site_parent="$2" hf_site_name="$3"
  local hf_site_dir="${hf_site_parent%/}/${hf_site_name}"
  [[ -d "${hf_site_dir}" ]] && return 0
  hf_site_refuse "${hf_site_source}" \
    "the data directory of account '${hf_site_name}' does not exist: ${hf_site_dir}; \`id -un\` names the account this process runs as, not the account that submitted the job"
  return 1
}

hf_site_check_root() {
  # $1 the file that supplied the value, $2 variable name, $3 resolved value.
  # Refuse every shape that names a valid but wrong location.
  local hf_site_source="$1" hf_site_var="$2" hf_site_value="$3" hf_site_why
  hf_site_why="$(hf_site_root_problem "${hf_site_var}" "${hf_site_value}")" && return 0
  hf_site_refuse "${hf_site_source}" "${hf_site_why}"
  return 1
}

hf_site_detect() {
  # Print the site name for this host. setupEnv.sh and tools/environment_verdict.sh
  # both need it, and a second copy of the rule would drift from the first.
  if [[ -d /data/alice && -d /cvmfs/alice.cern.ch ]]; then
    printf 'nikhef'
  else
    printf 'local'
  fi
}

hf_site_profile_path() {
  # $1 checkout base, $2 site name. Print the file setupEnv.sh would source.
  # An untracked config/site.local.conf replaces the tracked profile entirely.
  local hf_site_base="$1" hf_site_name="$2"
  if [[ -f "${hf_site_base}/config/site.local.conf" ]]; then
    printf '%s' "${hf_site_base}/config/site.local.conf"
  else
    printf '%s' "${hf_site_base}/config/sites/${hf_site_name}.conf"
  fi
}
