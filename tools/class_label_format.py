#!/usr/bin/env python3
"""The ONE way a multiplicity-class percentile becomes text.

Two generators write class labels: `apply_class_labels.py` owns the committed
plotting configurations, `make_variant_configs.py` owns the variant ones. They
must not be able to format the same percentile differently, so the precision
constant and the formatting function live here and both import them.

`LABEL_DECIMALS` is also emitted into `plotting/GeneratedClassLabelPrecision.h`
so the ROOT macros round the figure-4 inset the same way. One number, three
consumers.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOUNDARIES = ROOT / "config" / "multiplicity_class_boundaries_v1.json"
MB_ANCHOR = ROOT / "AnalysisScripts" / "anchors" / "b4_multiplicity_mb"
LABEL_TUNE = "MONASH"

# THE precision of a displayed class percentile. See E9: at 0 decimals the
# corrected 59.8 and the wrong 59.9 it replaced print as the same string.
LABEL_DECIMALS = 1

# Every generated configuration declares who owns its labels, so neither
# generator has to guess from a filename glob which files are its own.
OWNER_KEY = "label_owner"
OWNER_COMMITTED = "tools/apply_class_labels.py"
OWNER_VARIANTS = "tools/make_variant_configs.py"


def top_percentiles() -> list[float]:
    """100 - (fraction strictly below), one per class boundary, ascending N_ch."""
    boundaries = [c["boundary_nch"]
                  for c in json.loads(BOUNDARIES.read_text())["classes"]]
    rows = csv.DictReader((MB_ANCHOR / f"nch_mb_{LABEL_TUNE}.csv").open())
    dist = {int(r["nch"]): float(r["count"]) for r in rows}
    total = sum(dist.values())
    return [100.0 - 100.0 * sum(c for n, c in dist.items() if n < b) / total
            for b in boundaries]


def format_percentile_range(low: float, high: float) -> str:
    """The one rendering of a percentile interval."""
    return f"{low:.{LABEL_DECIMALS}f}-{high:.{LABEL_DECIMALS}f}%"


def class_percentile_range(index: int, percentiles: list[float]) -> str:
    """Class `index` (1-based, ascending N_ch) spans down to the next boundary."""
    if not 1 <= index <= len(percentiles):
        raise SystemExit(
            f"class index {index} is outside the {len(percentiles)} classes "
            f"defined in {BOUNDARIES.name}")
    high = percentiles[index - 1]
    low = percentiles[index] if index < len(percentiles) else 0.0
    return format_percentile_range(low, high)


def owner_of(document: dict) -> str:
    """Who owns this configuration's labels.

    A configuration with no declaration is a committed one predating the split,
    and belongs to apply_class_labels.py -- the historical default, stated rather
    than assumed.
    """
    return document.get(OWNER_KEY, OWNER_COMMITTED)
