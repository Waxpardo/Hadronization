#!/usr/bin/env python3
"""Prevent the Paul plotting adapter and shared selector contract from drifting."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MACRO = ROOT / "PlottingScripts/improvedPlotting_THnSparse.C"
SHARED = ROOT / "PlottingScripts/PairInputSelectionUtils.h"


def function_slice(text: str, anchor: str, next_anchor: str) -> str:
    start = text.index(anchor)
    end = text.index(next_anchor, start)
    return text[start:end]


def quoted_initializer(text: str, anchor: str) -> list[str]:
    start = text.index(anchor)
    opening = text.index("{", start)
    closing = text.index("};", opening)
    return re.findall(r'"([^"]+)"', text[opening:closing])


def main() -> int:
    macro = MACRO.read_text()
    shared = SHARED.read_text()

    macro_validation = function_slice(
        macro,
        "PairSelectionProjectionMode ValidatePairInputSelectionContract(",
        "void RequireMatchingPairSelectionModes(",
    )
    shared_validation = function_slice(
        shared,
        "inline ProjectionMode ValidateSelectionMetadata(",
        "inline const char* ProjectionModeName(",
    )
    macro_objects = quoted_initializer(
        macro_validation, "requiredV2Objects"
    )
    shared_objects = quoted_initializer(shared_validation, "required")
    assert macro_objects == shared_objects
    assert len(macro_objects) == 12
    assert "associate_origin_category_schema" in macro_objects
    assert "associate_origin_category_labels" in macro_objects

    macro_parser = function_slice(
        macro,
        "PairInputSelectionContract ParsePairInputSelectionContract(",
        "CONFIGS readConfig(",
    )
    shared_parser = function_slice(
        shared,
        "inline SelectionContract ParseSelectionContract(",
        "inline std::string ReadString(",
    )
    macro_keys = set(quoted_initializer(macro_parser, "expectedKeys"))
    shared_keys = set(quoted_initializer(shared_parser, "expectedKeys"))
    assert macro_keys == shared_keys
    assert len(macro_keys) == 14

    mode_literals = {
        "v2_metadata_or_tagged_legacy_recuts_v1",
        "tagged_legacy_recuts_only_v1",
    }
    for literal in mode_literals:
        assert literal in macro
        assert literal in shared

    canonical_literals = {
        "legacy_recuts_only_v1",
        "paul_pair_objects_primary_ground_v2",
        "one_pass_primary_ground_pair_analysis_v2",
        "status_analysis_THnSparse_qq_v2",
        "central_primary_ground_v1",
        "hard_trigger_primary_ground__primary_ground_associate_v1",
        "ordered_conditional_v1",
    }
    for literal in canonical_literals:
        assert literal in macro_parser
        assert literal in shared_parser

    print(
        "pair-selection contract parity test passed "
        f"metadata_objects={len(macro_objects)} json_fields={len(macro_keys)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
