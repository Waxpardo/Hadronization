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

STAGED_DIR="$ROOT/$CAMPAIGN/config"
PLOTS="$ROOT/$CAMPAIGN/plots"
mkdir -p "$STAGED_DIR" "$PLOTS"
STAGED="$STAGED_DIR/$(basename "$CONFIG")"
FACTS="$ROOT/$CAMPAIGN/staged_configuration_facts.json"

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
pathlib.Path(facts_path).write_text(json.dumps({
    "write_path_readback": plots,
    "writing_canvases": sorted(writing),
    "write_names": names,
    "bin_labels": bins,
    "expected_uncertainty_matrix_rows": len(bins) * 12,
    "axes_widened": widen,
}, indent=2, sort_keys=True) + "\n")
print(f"staged {dst} write_path={plots} canvases={len(writing)} "
      f"bins={len(bins)} widened_axes={widen} names={names} purpose=measurement")
PY
[ $? -eq 0 ] || { echo "REFUSING: staging did not verify" >&2; exit 3; }

WINDOW_START=$(( $(date +%s) - 1 ))

HADRONIZATION_BASE="$BASE" \
DATASET_SELECTOR="$SELECTOR" \
HADRONIZATION_MEASUREMENT_ROOT="$ROOT/$CAMPAIGN" \
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
  --measurement-root "$ROOT/$CAMPAIGN" \
  --window-start "$WINDOW_START" --window-end "$WINDOW_END" \
  "${TREES[@]}" \
  --expect "config/$(basename "$CONFIG")" \
  "${EXPECT[@]}" \
  --out "$ROOT/$CAMPAIGN/output_assertion.json"
ASSERT_RC=$?

RECEIPT="$ROOT/$CAMPAIGN/measurement_receipt.json"
python3 - "$RECEIPT" "$CAMPAIGN" "$RC" "$LOG" "$STAGED" "$ASSERT_RC" "$FACTS" \
         "$ROOT/$CAMPAIGN/output_assertion.json" "$WINDOW_START" "$WINDOW_END" <<'PY'
import hashlib, json, pathlib, sys, datetime
(receipt, campaign, rc, log, staged, assert_rc, facts, assertion,
 w_start, w_end) = sys.argv[1:11]
text = pathlib.Path(log).read_text(errors="replace")
resolved = sorted({line.split("tag=")[1].strip()
                   for line in text.splitlines()
                   if "central resolver" in line and "tag=" in line})
rows = sum(1 for l in text.splitlines() if l.startswith("UNCERTAINTY_MATRIX"))
facts_data = json.loads(pathlib.Path(facts).read_text())
pathlib.Path(receipt).write_text(json.dumps({
    "schema": "hadronization_measurement_receipt_v2",
    "purpose": "measurement",
    "publication_eligible": False,
    "campaign": campaign,
    "render_exit_status": int(rc),
    "output_assertion_exit_status": int(assert_rc),
    "output_assertion": json.loads(pathlib.Path(assertion).read_text())
                        if pathlib.Path(assertion).exists() else None,
    "render_window": [int(w_start), int(w_end)],
    "uncertainty_matrix_rows": rows,
    "expected_uncertainty_matrix_rows":
        facts_data["expected_uncertainty_matrix_rows"],
    "staged_configuration_facts": facts_data,
    "resolved_complete_root_tags": resolved,
    "staged_configuration_sha256":
        hashlib.sha256(pathlib.Path(staged).read_bytes()).hexdigest(),
    "log_sha256": hashlib.sha256(pathlib.Path(log).read_bytes()).hexdigest(),
    "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
}, indent=2, sort_keys=True) + "\n")
print(f"receipt purpose=measurement rc={rc} output_assertion_rc={assert_rc} "
      f"rows={rows}/{facts_data['expected_uncertainty_matrix_rows']} "
      f"resolved={resolved}")
PY

# The render's status and the output assertion are separate facts and both must
# hold. A render that succeeded into the wrong directory is not a success.
if [ "$RC" -ne 0 ]; then
  echo "RENDER_MEASUREMENT campaign=$CAMPAIGN rc=$RC output_assertion=$ASSERT_RC"
  exit "$RC"
fi
echo "RENDER_MEASUREMENT campaign=$CAMPAIGN rc=$RC output_assertion=$ASSERT_RC"
exit "$ASSERT_RC"
