#!/usr/bin/env python3
"""The one way a tune-local multiplicity percentile becomes text.

Two generators write class labels: `apply_class_labels.py` owns the committed
plotting configurations, `make_variant_configs.py` owns the variant ones. They
must not be able to format the same percentile differently, so the precision
constant and the formatting function live here and both import them.

`LABEL_DECIMALS` is also emitted into `plotting/GeneratedClassLabelPrecision.h`
so the ROOT macros round the figure-4 inset the same way. One number, three
consumers.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOUNDARIES = ROOT / "config" / "multiplicity_percentile_classes_v2.json"
LABEL_TUNE = "PER_TUNE"

# THE precision of a displayed class percentile. See E9: at 0 decimals the
# corrected 59.8 and the wrong 59.9 it replaced print as the same string.
LABEL_DECIMALS = 0

# Every generated configuration declares who owns its labels, so neither
# generator has to guess from a filename glob which files are its own.
OWNER_KEY = "label_owner"
OWNER_COMMITTED = "tools/apply_per_tune_multiplicity_contract.py"
OWNER_VARIANTS = "tools/make_variant_configs.py"


def top_percentiles() -> list[float]:
    """Upper top-percentile edge for c1..c11, in ascending activity."""
    classes = json.loads(BOUNDARIES.read_text())["classes"]
    return [float(row["percentile_max"]) for row in classes]


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
