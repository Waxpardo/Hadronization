#!/usr/bin/env bash
# Render one balancing-canvas variant, and refuse to be quiet about which
# configuration was actually used.
#
# THE DEFECT THIS CLOSES. run_paper_plots.sh reads the complete-root config from
# THNSPARSE_COMPLETE_ROOT_CONFIG. Exporting the neighbouring THNSPARSE_CONFIG
# instead is silently ignored: the run falls back to the DEFAULT reduced config
# and renders something nobody asked for. That happened, and it was caught only
# because the default declares a v2 pair schema while the inputs are v3, so an
# unrelated gate tripped. With a compatible default it would have produced a
# plausible figure from the wrong configuration.
#
# So the intended configuration's sha256 is computed BEFORE the run, and the
# sha the macro echoes is compared against it afterwards. Mismatch is fatal.
#
# usage: tools/render_balancing_variant.sh <config-path-relative-to-base> <logfile>
set -euo pipefail

CONFIG="${1:?config path required}"
LOG="${2:?log path required}"
BASE="${HADRONIZATION_BASE:?HADRONIZATION_BASE must be set}"

cd "${BASE}"
[ -f "${CONFIG}" ] || { echo "FATAL: no such config: ${CONFIG}" >&2; exit 2; }

INTENDED="$(sha256sum "${CONFIG}" | cut -d' ' -f1)"
echo "RENDER_VARIANT config=${CONFIG}"
echo "RENDER_VARIANT intended_sha256=${INTENDED}"

# The variable name is the whole point: this target reads
# THNSPARSE_COMPLETE_ROOT_CONFIG, not THNSPARSE_CONFIG.
THNSPARSE_COMPLETE_ROOT_CONFIG="${CONFIG}" \
  bash plotting/run_paper_plots.sh thnsparse-complete-root > "${LOG}" 2>&1 || {
    echo "FATAL: render failed; see ${LOG}" >&2
    tr -d '\0' < "${LOG}" | grep -iE 'error|fatal' | head -5 >&2 || true
    exit 3
  }

LOADED="$(tr -d '\0' < "${LOG}" \
  | sed -n 's/.*configuration_sha256 = \([0-9a-f]\{64\}\).*/\1/p' | head -1)"
LOADED_PATH="$(tr -d '\0' < "${LOG}" \
  | sed -n 's/^ *config: *\(.*\)$/\1/p' | head -1)"

echo "RENDER_VARIANT loaded_path=${LOADED_PATH}"
echo "RENDER_VARIANT loaded_sha256=${LOADED:-<none>}"

if [ -z "${LOADED}" ]; then
  echo "FATAL: the run echoed no configuration_sha256; cannot confirm which" \
       "configuration was used" >&2
  exit 4
fi
if [ "${LOADED}" != "${INTENDED}" ]; then
  echo "FATAL: configuration mismatch." >&2
  echo "  intended ${CONFIG}" >&2
  echo "           ${INTENDED}" >&2
  echo "  loaded   ${LOADED_PATH}" >&2
  echo "           ${LOADED}" >&2
  echo "  A silent fallback to the default configuration is exactly what this" >&2
  echo "  check exists to prevent." >&2
  exit 5
fi
echo "RENDER_VARIANT config_confirmed=OK"
