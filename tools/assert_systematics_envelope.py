#!/usr/bin/env python3
"""Validate one systematics envelope before anything renders it.

THE CONSUMER SIDE OF RULING R7. `./hadronization plot --systematics PATH` is
the only route by which a systematic reaches a figure, and this tool is the
gate on that route. It reads an explicit path. There is no default, no
discovery, and no environment fallback: fail-closed rule 1 says a resolver
that answers a question nobody asked will answer it wrongly, and the wrong
answer looks exactly like a right one.

FOUR THINGS MUST HOLD, and each refusal names the field that failed:

  path        the file exists and parses
  schema      it declares hadronization_systematics_envelope_v1
  status      it is COMPLETE -- an INCOMPLETE envelope carries whatever it
              could derive and must never be drawn
  provenance.nominal_boundary_receipt_sha256
              it equals the sha256 of the multiplicity-boundary receipt the
              NOMINAL render wrote. An envelope bound to a different render
              describes different class edges, so its band would sit on the
              wrong classes.

The boundary receipt is located, never guessed: exactly one
`multiplicity_boundary_receipt_v2.json` must exist under the nominal plotting
plane, which is the plotter's own invariant -- it refuses to run unless
exactly one global-canvas output directory holds the receipt.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ENVELOPE_SCHEMA = "hadronization_systematics_envelope_v1"
BOUNDARY_RECEIPT_NAME = "multiplicity_boundary_receipt_v2.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def refuse(field: str, detail: str) -> int:
    print(f"ENVELOPE_INVALID field={field} {detail}", file=sys.stderr)
    return 3


def find_boundary_receipt(plane: Path) -> tuple[Path | None, str]:
    if not plane.is_dir():
        return None, f"the nominal plotting plane is absent: {plane}"
    found = sorted(plane.rglob(BOUNDARY_RECEIPT_NAME))
    if not found:
        return None, (
            f"no {BOUNDARY_RECEIPT_NAME} under the nominal plotting plane "
            f"{plane}; render the nominal figures first")
    if len(found) > 1:
        return None, (
            f"{len(found)} boundary receipts under {plane}; exactly one is "
            "required and the plotter writes exactly one")
    return found[0], ""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--envelope", type=Path, required=True)
    ap.add_argument("--nominal-plot-plane", type=Path, required=True,
                    help="the nominal plotting plane for this campaign and commit")
    args = ap.parse_args()

    path = args.envelope
    if not path.is_file():
        return refuse("path", f"no envelope at {path}")
    try:
        envelope = json.loads(path.read_text())
    except json.JSONDecodeError as error:
        return refuse("path", f"{path} is not JSON: {error}")

    if envelope.get("schema") != ENVELOPE_SCHEMA:
        return refuse(
            "schema",
            f"envelope declares {envelope.get('schema')!r}, "
            f"expected {ENVELOPE_SCHEMA!r}")

    status = envelope.get("status")
    if status != "COMPLETE":
        missing = envelope.get("missing") or []
        return refuse(
            "status",
            f"envelope status is {status!r}, expected 'COMPLETE'"
            + (f"; missing={missing}" if missing else ""))

    provenance = envelope.get("provenance")
    if not isinstance(provenance, dict):
        return refuse("provenance", "envelope carries no provenance block")

    claimed = provenance.get("nominal_boundary_receipt_sha256")
    if not claimed:
        return refuse(
            "provenance.nominal_boundary_receipt_sha256",
            "envelope names no nominal boundary receipt")

    receipt, problem = find_boundary_receipt(args.nominal_plot_plane)
    if receipt is None:
        return refuse("provenance.nominal_boundary_receipt_sha256", problem)

    actual = sha256(receipt)
    if actual != claimed:
        return refuse(
            "provenance.nominal_boundary_receipt_sha256",
            f"envelope claims {claimed}, the nominal render's {receipt.name} "
            f"is {actual}")

    if not envelope.get("rows"):
        return refuse("rows", "a COMPLETE envelope with no row cannot be drawn")

    print(
        f"ENVELOPE_VALID schema={ENVELOPE_SCHEMA} status=COMPLETE "
        f"rows={len(envelope['rows'])} sha256={sha256(path)} "
        f"boundary_receipt={actual}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
