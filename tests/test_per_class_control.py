#!/usr/bin/env python3
"""The per-class control, on real log rows rather than on constructed ones.

WHY A FIXTURE AND NOT A CONSTRUCTED LOG. The control that licenses every delta
is that the measurement target, re-rendering the sealed central, reproduces the
sealed nominal exactly. That ran once on the cluster on 2026-08-19. A test built
from invented rows would exercise the arithmetic and certify nothing about the
instrument, so `tests/fixtures/` carries the twelve multiplicity-integrated rows
and the twelve resolver lines from three real logs:

    integrated_rows_nominal.log         vintegrated_closure.log, sha256 f507f625...
                                        figure_deploy_20260817, 2026-08-18 10:18
    integrated_rows_control.log         sys_runs_plot5/render_HF_RUN3_V1.log,
                                        sha256 690f2dc5..., 2026-08-19 16:09
    integrated_rows_HF_SYS_PTHAT_4.log  sys_runs_plot5/render_HF_SYS_PTHAT_4.log,
                                        sha256 7922626e..., 2026-08-19 16:05

THE HARD CASE IS IN THE FIXTURE. The two renders print different digit counts:
the figure-branch plotter writes `13656517` where this branch's writes
`1.36565e+07`. Both record the same count at six figures. A comparison that
demanded string equality would fail on a difference that is not there, and one
with a numeric tolerance would accept a difference that is.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "extraction"))
FIXTURES = REPO / "tests/fixtures"

from harvest_class_axis import (agrees_at_recorded_precision,  # noqa: E402
                                assert_resolved_campaign, parse_log)
from harvest_yield_deltas import is_unresolved, yield_delta  # noqa: E402

failures = []


def check(label, condition, detail=""):
    if condition:
        print(f"  PASS {label}")
    else:
        print(f"  FAIL {label} {detail}")
        failures.append(label)


def load(name):
    # Explicit legacy-only parsing: these byte-preserved 2026-08-19 fixtures
    # predate the block-vector schema and exercise integrated-yield integrity,
    # never endpoint or covariance arithmetic. Current consumers use the
    # strict default and refuse these logs.
    return parse_log(
        (FIXTURES / f"integrated_rows_{name}.log").read_text(),
        validate_block_contract=False)


nominal, control = load("nominal"), load("control")
variation = load("HF_SYS_PTHAT_4")

check("the nominal fixture holds twelve integrated rows", len(nominal) == 12,
      str(len(nominal)))
check("the control fixture holds twelve integrated rows", len(control) == 12,
      str(len(control)))
check("every row parses to the integrated class",
      {k[4] for k in nominal} == {"MB"}, str({k[4] for k in nominal}))
check("the three logs share one row identity set",
      set(nominal) == set(control) == set(variation))

# --- THE CONTROL ----------------------------------------------------------
disagreements = [
    (key, field, nominal[key][field], control[key][field])
    for key in nominal
    for field in ("central_yield", "yield_sem", "central_triggers")
    if not agrees_at_recorded_precision(nominal[key][field], control[key][field])
]
check("the control reproduces the nominal on every integrated row",
      disagreements == [], str(disagreements[:2]))

# The digit-count case, named explicitly so a change to the comparison method
# cannot pass this file quietly.
CHARM = ("CHARM", "D^{+}", "MONASH", "D-", "MB")
check("the two renders print the trigger count differently",
      nominal[CHARM]["central_triggers"] != control[CHARM]["central_triggers"],
      f'{nominal[CHARM]["central_triggers"]} vs {control[CHARM]["central_triggers"]}')
check("and they agree at the precision both record",
      agrees_at_recorded_precision(nominal[CHARM]["central_triggers"],
                                   control[CHARM]["central_triggers"]))
check("a genuinely different count still fails the comparison",
      not agrees_at_recorded_precision("13656517", "13756517"))

# --- THE RESOLVER ---------------------------------------------------------
for name, campaign in (("nominal", "HF_RUN3_V1"), ("control", "HF_RUN3_V1"),
                       ("HF_SYS_PTHAT_4", "HF_SYS_PTHAT_4")):
    text = (FIXTURES / f"integrated_rows_{name}.log").read_text()
    found = assert_resolved_campaign(text, campaign)
    check(f"{name} resolved {campaign}", found["central"] == {campaign},
          str(found))

try:
    assert_resolved_campaign(
        (FIXTURES / "integrated_rows_control.log").read_text(), "HF_SYS_PTHAT_4")
    check("the control log is refused for the wrong campaign", False, "no raise")
except ValueError:
    check("the control log is refused for the wrong campaign", True)

# --- ONE REAL DELTA, END TO END -------------------------------------------
# CHARM D^{+}-D- MONASH, integrated: PTHAT_4 against the nominal.
n, v = nominal[CHARM], variation[CHARM]
delta, sem = yield_delta(float(v["central_yield"]), float(v["yield_sem"]),
                         float(n["central_yield"]), float(n["yield_sem"]))
check("the real integrated PTHAT_4 charm delta is +0.00960004",
      "%.6g" % delta == "0.00960004", "%.17g" % delta)
check("its SEM(Delta) is 0.000357629",
      "%.6g" % sem == "0.000357629", "%.17g" % sem)
check("it is resolved at 2 SEM", is_unresolved(delta, sem) is False,
      f"significance {abs(delta)/sem:.2f}")

print(f"\n{'FAILED: ' + ', '.join(failures) if failures else 'ALL CHECKS PASS'}")
sys.exit(1 if failures else 0)
