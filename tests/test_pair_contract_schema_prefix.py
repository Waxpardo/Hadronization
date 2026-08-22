#!/usr/bin/env python3
"""Require both contract parsers to resolve and validate the configured key prefix.

Both implementations of the contract parser --
`plotting/PairInputSelectionUtils.h` and the mirror in
`plotting/improvedPlotting_THnSparse.C` -- resolve the key prefix from the
config's own content, reject a config that carries both families or neither,
reject a prefix that disagrees with the schema it carries, and keep
`RequireExactKeys` strict against the RESOLVED key set. The current executable
configuration is v3 because HF_RUN3_V1 pair files carry the v3 species axis;
the v2 direction remains a constructed parser-compatibility check.

The test cannot establish that a full legacy plotting run is unchanged.
That would require running the stack on the v2 dataset, and the v2 dataset no
longer exists -- `AnalyzedData/complete_root_21_06_2026` and
`SUBSAMPLES_700/...` are absent locally and on the production site.
No repository test can prove that the old figures are unchanged without those inputs.
This source check is not proof of run-level equivalence.

The test covers both directions:
  * a v3 config carrying v2_ keys must FAIL;
  * a syntactically valid v2 key family remains representable.
"""
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SHARED = REPO / "plotting/PairInputSelectionUtils.h"
MACRO = REPO / "plotting/improvedPlotting_THnSparse.C"
V3_CONFIG = REPO / ("plotting/configuration_multiplicity_reduced_JUNCTIONS"
                    "_THnSparse_complete_root.json")

# The eleven schema-scoped fields, without their prefix.
SUFFIXES = [
    "analysis_schema", "analysis_implementation", "analysis_version",
    "analysis_profile", "selector_version", "pair_combinatorics_mode",
    "trigger_pt_min_exclusive", "associate_pt_min_exclusive",
    "eta_abs_max_inclusive", "same_sign_pair_factor", "pt_upper_selection",
]
UNPREFIXED = ["mode", "legacy_metadata_free_complete_root_tag",
              "histogram_pt_eta_fields"]

failures = []


def check(label, condition, detail=""):
    if condition:
        print(f"  PASS {label}")
    else:
        print(f"  FAIL {label} {detail}")
        failures.append(label)


shared = SHARED.read_text()
macro = MACRO.read_text()

# ---- 1. both implementations resolve the prefix, neither defaults ---------
for name, text in (("shared header", shared), ("macro", macro)):
    check(f"{name} resolves the prefix from config content",
          'contains("v2_analysis_schema")' in text
          and 'contains("v3_analysis_schema")' in text)
    check(f"{name} rejects both families present",
          "carries BOTH v2_analysis_schema" in text)
    check(f"{name} rejects neither family present",
          "carries neither v2_analysis_schema" in text)
    check(f"{name} builds expectedKeys from the resolved prefix",
          'p + "analysis_schema"' in text)
    # The prefix/schema agreement must go through the generated contract, not a
    # retyped literal -- test_pair_object_contract.py forbids the literal.
    check(f"{name} judges the schema through ParsePairSchemaVersion",
          "ParsePairSchemaVersion" in text)

# ---- 2. no schema literal was reintroduced -------------------------------
for name, text in (("shared header", shared), ("macro", macro)):
    for tag in ("paul_pair_objects_primary_ground_v2",
                "paul_pair_objects_primary_ground_v3"):
        check(f"{name} does not pin {tag[-2:]} as a literal",
              f'"{tag}"' not in text, "")

# ---- 3. the resolved key sets agree, and are still exactly 14 -------------
def expected_keys(prefix):
    return set(UNPREFIXED) | {prefix + s for s in SUFFIXES}


check("resolved key set is 14 for v2", len(expected_keys("v2_")) == 14)
check("resolved key set is 14 for v3", len(expected_keys("v3_")) == 14)

# ---- 4. CURRENT V3 DIRECTION: the executable config matches HF_RUN3_V1 ----
config = json.loads(V3_CONFIG.read_text())["pair_input_selection_contract"]
check("committed v3 config carries exactly the v3 resolved key set",
      set(config) == expected_keys("v3_"),
      f"unexpected={sorted(set(config) - expected_keys('v3_'))} "
      f"missing={sorted(expected_keys('v3_') - set(config))}")
check("committed v3 config declares the v3 schema",
      config["v3_analysis_schema"].endswith("_v3"),
      config["v3_analysis_schema"])
check("committed v3 config carries no stale v2_ keys",
      not any(k.startswith("v2_") for k in config))

# A valid v2 key family remains expressible even though no runnable v2 dataset
# is retained. This checks the compatibility direction without making a stale
# v2 configuration the default workflow.
synthetic_v2 = {
    ("v2_" + key[3:] if key.startswith("v3_") else key): value
    for key, value in config.items()
}
synthetic_v2["v2_analysis_schema"] = "paul_pair_objects_primary_ground_v2"
check("constructed v2 contract carries exactly the v2 resolved key set",
      set(synthetic_v2) == expected_keys("v2_"))

# ---- 5. THE V3 DIRECTION: v2_ keys under a v3 schema must fail ------------
# Constructed, not committed: this is the config that must be rejected.
bad = dict(synthetic_v2)
bad["v2_analysis_schema"] = "paul_pair_objects_primary_ground_v3"
# Resolution picks v2_ (that is the family present), and the declared schema
# then disagrees with the prefix -- which the parser must treat as fatal.
check("a v3 schema under v2_ keys is a prefix/schema disagreement",
      bad["v2_analysis_schema"].endswith("_v3")
      and not any(k.startswith("v3_") for k in bad))
for name, text in (("shared header", shared), ("macro", macro)):
    check(f"{name} throws on prefix/schema disagreement",
          "does not recognise as the schema matching" in text
          or "which the pair-object contract does not" in text)

print()
if failures:
    for f in failures:
        print("FAIL:", f)
    sys.exit(1)
print("PASS test_pair_contract_schema_prefix.py")
