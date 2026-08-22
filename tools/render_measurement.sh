#!/bin/bash
# Render one campaign through the MEASUREMENT target.
#
# Usage: render_measurement.sh CAMPAIGN CONFIG SELECTOR MEASUREMENT_ROOT LOG
#
# It stages a copy of the configuration whose canvas `write_path` fields are
# forced under the measurement root, reads those fields back out of the staged
# file, and after the render asserts on the OUTPUT SIDE that nothing landed in
# a publication path.
#
# THREE PLACES THIS PIPELINE HAS BEEN WRONG, and the rule they share:
#
#   the resolver line   the configuration is a request; the resolver line is
#                       the answer (run record 18)
#   the exit status     $? read after an echo is a value from a place that
#                       happens to hold one, not the render's status (17.4)
#   the output path     nine mutation tests, every one of them before the
#                       render, all passing while three canvases landed in a
#                       publication path (19.1)
#
# A GATE ON THE REQUEST CANNOT CERTIFY THE RESULT. Each fix reads the artifact
# the step actually produced.
#
# THE OUTPUT PATH, specifically. `writeCanvasToFiles` takes `writePath` from a
# NESTED configuration field -- one per entry of `canvases_to_be_drawn` and of
# `global_canvases_to_be_drawn` (improvedPlotting_THnSparse.C:215,265). A
# top-level `write_path` key is read by nothing.
set -uo pipefail

CAMPAIGN="${1:?campaign required}"
CONFIG="${2:?configuration required}"
SELECTOR="${3:?selector required}"
ROOT="${4:?measurement root required}"
LOG="${5:?log path required}"
BASE="${HADRONIZATION_BASE:?HADRONIZATION_BASE required}"
# Set to the entry artifact to add the multiplicity-integrated bin, which the
# eleven-class configuration does not carry.
INTEGRATED_BIN="${MEASUREMENT_INTEGRATED_BIN:-}"

case "$ROOT" in
  *plotting/Plots/*)
    echo "REFUSING: measurement root is inside the publication tree: $ROOT" >&2
    exit 3;;
esac
[ -e "$LOG" ] && { echo "REFUSING: $LOG exists" >&2; exit 3; }

if [ "${HADRONIZATION_MEASUREMENT_ROOT_EXACT:-0}" = "1" ]; then
  CAMPAIGN_ROOT="$ROOT"
else
  CAMPAIGN_ROOT="$ROOT/$CAMPAIGN"
fi

STAGED_DIR="$CAMPAIGN_ROOT/config"
PLOTS="$CAMPAIGN_ROOT/plots"
mkdir -p "$STAGED_DIR" "$PLOTS"
STAGED="$STAGED_DIR/$(basename "$CONFIG")"
FACTS="$CAMPAIGN_ROOT/staged_configuration_facts.json"

python3 - "$BASE/$CONFIG" "$STAGED" "$PLOTS" "$FACTS" "$INTEGRATED_BIN" \
         "${MEASUREMENT_WIDEN_AXES:-0}" <<'PY'
import json, sys, pathlib
src, dst, plots, facts_path, integrated, widen_flag = sys.argv[1:7]
widen = widen_flag == "1"
config = json.loads(pathlib.Path(src).read_text())

# A top-level `write_path` is a key the plotter does not read. Setting one is
# what put three canvases in a publication path on 2026-08-19. Remove it rather
# than leave a second place that looks like it holds the answer.
config.pop("write_path", None)

forced = []
for section in ("canvases_to_be_drawn", "global_canvases_to_be_drawn"):
    for entry in config.get(section, []):
        if entry.get("write"):
            entry["write_path"] = plots
            forced.append(f"{section}/{entry['canvas_name']}")

# THE AXIS IS A FRAME, NOT A NUMBER. The ratio panels carry a y-axis chosen to
# frame the CENTRAL campaign, and the plotter refuses to draw an uncertainty
# envelope that the configured axis would clip -- correctly, because a
# publication figure must not crop its own error band. A variation is under no
# obligation to fit inside the central's frame: HF_SYS_MUR_UP reaches 2.5949 on
# an axis that stops at 2.5, and HF_SYS_PTHAT_1 reaches down to 0.5469 on an
# axis that starts at 0.6.
#
# Widening the frame cannot move a measured value. Every UNCERTAINTY_MATRIX row
# is emitted at improvedPlotting_THnSparse.C:3739, and the first canvas is drawn
# at :4015 -- the numbers are printed before any axis is applied. The control
# re-rendered with these widened axes reproduces all 144 rows unchanged, which
# is the check rather than the claim.
if widen:
    for entry in config.get("canvases_to_be_drawn", []):
        lo, hi = entry.get("y_min_axis"), entry.get("y_max_axis")
        if lo is None or hi is None or not hi > lo:
            continue
        if entry.get("set_log_y"):
            entry["y_min_axis"], entry["y_max_axis"] = lo / 100.0, hi * 100.0
        else:
            span = hi - lo
            entry["y_min_axis"] = lo - 2.0 * span if lo < 0 else max(0.0, lo - 2.0 * span)
            entry["y_max_axis"] = hi + 2.0 * span

if integrated:
    artifact = json.loads(pathlib.Path(integrated).read_text())
    entry = artifact["entry"]
    labels = [h["binLabel"] for h in config["histograms_to_analyse"]]
    if entry["binLabel"] not in labels:
        config["histograms_to_analyse"].append(entry)

config["purpose"] = "measurement"
pathlib.Path(dst).write_text(json.dumps(config, indent=2) + "\n")

# --- READ IT BACK OUT OF THE STAGED FILE ---------------------------------
# Not out of the dict just written: the requirement is that the file the macro
# will open carries the value, and only reopening it tests that.
staged = json.loads(pathlib.Path(dst).read_text())
if "write_path" in staged:
    sys.exit("STAGING FAILED: a top-level write_path survived")
writing, wrong = [], []
for section in ("canvases_to_be_drawn", "global_canvases_to_be_drawn"):
    for entry in staged.get(section, []):
        if entry.get("write"):
            writing.append(entry["canvas_name"])
            if entry.get("write_path") != plots:
                wrong.append((entry["canvas_name"], entry.get("write_path")))
if wrong:
    sys.exit(f"STAGING FAILED: canvases still point elsewhere: {wrong}")
if not writing:
    sys.exit("STAGING FAILED: no canvas writes, so the render proves nothing")

names = sorted({e["write_name"]
                for s in ("canvases_to_be_drawn", "global_canvases_to_be_drawn")
                for e in staged.get(s, []) if e.get("write")})
bins = [h["binLabel"] for h in staged["histograms_to_analyse"]]
expected_identities = []
for flavour, section in (
    ("BEAUTY", "beauty_correlations_to_analyse"),
    ("CHARM", "charm_correlations_to_analyse"),
):
    for trigger_group in staged[section]:
        trigger = trigger_group["trigger"]
        for tune in staged["PYTHIA_TUNES"]:
            for associate in trigger_group["configs"]:
                for histogram in staged["histograms_to_analyse"]:
                    expected_identities.append("|".join((
                        flavour, trigger, tune, associate["associateOS"],
                        histogram["hDPhi"],
                    )))
if len(expected_identities) != len(set(expected_identities)):
    sys.exit("STAGING FAILED: duplicate expected uncertainty identities")
pathlib.Path(facts_path).write_text(json.dumps({
    "write_path_readback": plots,
    "writing_canvases": sorted(writing),
    "write_names": names,
    "bin_labels": bins,
    "expected_uncertainty_matrix_rows": len(expected_identities),
    "expected_uncertainty_identities": sorted(expected_identities),
    "axes_widened": widen,
}, indent=2, sort_keys=True) + "\n")
print(f"staged {dst} write_path={plots} canvases={len(writing)} "
      f"bins={len(bins)} widened_axes={widen} names={names} purpose=measurement")
PY
[ $? -eq 0 ] || { echo "REFUSING: staging did not verify" >&2; exit 3; }

WINDOW_START=$(( $(date +%s) - 1 ))

HADRONIZATION_BASE="$BASE" \
DATASET_SELECTOR="$SELECTOR" \
HADRONIZATION_MEASUREMENT_ROOT="$CAMPAIGN_ROOT" \
THNSPARSE_COMPLETE_ROOT_CONFIG="${STAGED#$BASE/}" \
  bash "$BASE/plotting/run_paper_plots.sh" measure-balancing > "$LOG" 2>&1
RC=$?          # THE RENDER'S OWN STATUS. Nothing may run before this line.

WINDOW_END=$(( $(date +%s) + 1 ))

# --- THE OUTPUT-SIDE ASSERTION -------------------------------------------
EXPECT=()
while IFS= read -r n; do
  EXPECT+=(--expect "plots/${n}_PDF.pdf" --expect "plots/${n}_PNG.png" \
           --expect "plots/${n}_MACRO.C")
done < <(python3 -c 'import json,sys
print("\n".join(json.load(open(sys.argv[1]))["write_names"]))' "$FACTS")

# Publication trees: the deploy is always walked, and MEASUREMENT_PUBLICATION_TREES
# adds a colon-separated list of trees outside it. The figure deploy holds the
# sealed artifacts and lives outside $BASE, so a scan of $BASE alone would leave
# the tree that matters most uncovered.
TREES=(--scan-base "$BASE")
if [ -n "${MEASUREMENT_PUBLICATION_TREES:-}" ]; then
  while IFS= read -r t; do
    [ -n "$t" ] && TREES+=(--publication-tree "$t")
  done < <(printf '%s\n' "${MEASUREMENT_PUBLICATION_TREES//:/$'\n'}")
fi

python3 "$BASE/tools/assert_measurement_outputs.py" \
  --measurement-root "$CAMPAIGN_ROOT" \
  --window-start "$WINDOW_START" --window-end "$WINDOW_END" \
  "${TREES[@]}" \
  --expect "config/$(basename "$CONFIG")" \
  "${EXPECT[@]}" \
  --out "$CAMPAIGN_ROOT/output_assertion.json"
ASSERT_RC=$?

RECEIPT="$CAMPAIGN_ROOT/measurement_receipt.json"
python3 "$BASE/tools/write_measurement_receipt.py" \
  --receipt "$RECEIPT" --campaign "$CAMPAIGN" --render-status "$RC" \
  --log "$LOG" --staged "$STAGED" --assertion-status "$ASSERT_RC" \
  --facts "$FACTS" --assertion "$CAMPAIGN_ROOT/output_assertion.json" \
  --window-start "$WINDOW_START" --window-end "$WINDOW_END" \
  --expected-tag "${HADRONIZATION_COMPLETE_ROOT_TAG:?complete-root tag required}"
RECEIPT_RC=$?

# The render's status and the output assertion are separate facts and both must
# hold. A render that succeeded into the wrong directory is not a success.
if [ "$RC" -ne 0 ]; then
  echo "RENDER_MEASUREMENT campaign=$CAMPAIGN rc=$RC output_assertion=$ASSERT_RC receipt=$RECEIPT_RC"
  exit "$RC"
fi
if [ "$ASSERT_RC" -ne 0 ]; then
  echo "RENDER_MEASUREMENT campaign=$CAMPAIGN rc=$RC output_assertion=$ASSERT_RC receipt=$RECEIPT_RC"
  exit "$ASSERT_RC"
fi
echo "RENDER_MEASUREMENT campaign=$CAMPAIGN rc=$RC output_assertion=$ASSERT_RC receipt=$RECEIPT_RC"
exit "$RECEIPT_RC"
