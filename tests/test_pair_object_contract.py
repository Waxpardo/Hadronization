#!/usr/bin/env python3
"""The pair-file object contract is the single source of truth.

Three hand-maintained copies of the pair-file object list had drifted apart,
and the copy that drifted was the ten-block closure's, so hFlavourClosure was
never closure-checked. These tests exist so that cannot recur.

Deliberately, the expectations here are derived from the *producer* and from
the contract's own invariants, never from the consumers under test. A fixture
that agrees with the code it checks cannot catch the code being wrong: the
1,000,000-event fossil survived for exactly that reason, because
tests/test_plot_dataset_integration.py restated the literal instead of the
contract.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "config/pair_file_object_contract_v1.json"
HEADER = ROOT / "AnalysisScripts/GeneratedPairObjectContract.h"
GENERATOR = ROOT / "tools/generate_pair_object_contract.py"
PRODUCER = ROOT / "analysis/status_analysis_THnSparse_qq.C"


def objects() -> list[dict]:
    return json.loads(CONTRACT.read_text())["objects"]


def test_header_is_current() -> None:
    result = subprocess.run(
        [sys.executable, str(GENERATOR), "--check"],
        text=True, capture_output=True,
    )
    assert result.returncode == 0, (
        "AnalysisScripts/GeneratedPairObjectContract.h is stale; regenerate "
        f"with tools/generate_pair_object_contract.py\n{result.stderr}"
    )


def test_closure_wrapper_derives_its_count_instead_of_pinning_it() -> None:
    """B12: no hardcoded count that is a function of the contract.

    validate_pair_block_closure.sh pinned
    object_content_sumw2_closure_checks=1500 inside an exact-match expected
    summary. b01536b took the real count to 1800 by adding hFlavourClosure to
    the closure's objects and never opened the wrapper, so the gate rejected a
    strictly more complete validation -- after a 6 h 44 m merge.

    test_no_consumer_restates_the_list covered the .C consumers only, which is
    precisely why nothing caught it: the wrapper restated a count *derived
    from* the list, in shell, outside that test's scope.
    """
    wrapper = (ROOT / "Validation/validate_pair_block_closure.sh").read_text()
    pinned = re.findall(r"object_content_sumw2_closure_checks=(\d+)", wrapper)
    assert not pinned, (
        "validate_pair_block_closure.sh pins "
        f"object_content_sumw2_closure_checks={pinned[0]} as a literal. That "
        "count is (closure-checked additive_content objects) x 300 and must be "
        "derived from config/pair_file_object_contract_v1.json, or it goes "
        "stale at the next contract change exactly as B12 did."
    )


def test_no_consumer_restates_the_list() -> None:
    """The consumers must filter the contract, not restate names.

    The shell wrapper is in scope because its absence from it is why B12
    existed. Its syntax has no braced initialiser, so the count-pinning test
    above is the one that bites for it; listing it here catches a future
    enumeration as well.
    """
    consumers = [
        ROOT / "Validation/ValidatePairDirectory.C",
        ROOT / "Validation/ValidatePairBlockClosure.C",
        ROOT / "Validation/validate_pair_block_closure.sh",
        ROOT / "plotting/Validate_THnSparse_Production.C",
    ]
    # Objects whose names may legitimately appear for reasons other than
    # rebuilding the list: the closure names two invariants it compares
    # against contract constants.
    allowed = {
        "associate_origin_category_schema",
        "associate_origin_category_labels",
    }
    content = {row["name"] for row in objects()
               if row["merge_semantics"] != "invariant"} - allowed
    for path in consumers:
        text = path.read_text()
        # Strip comments: the explanatory comments naturally name objects.
        text = re.sub(r"//[^\n]*", "", text)
        text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
        # Python judges comment with '#', and their docstrings legitimately
        # name the literal when explaining why it is gone.
        if path.suffix == ".py":
            text = re.sub(r"#[^\n]*", "", text)
            text = re.sub(r'""".*?"""', "", text, flags=re.S)
        # Naming one object to assert something specific about it is
        # per-object logic, not a copy of the list: ValidatePairDirectory.C
        # checks each sparse's own dimensionality and Sumw2 contract, and the
        # closure reads "input_events" to compare against the expected event
        # count. What must not recur is a second *enumeration* of which
        # objects exist, so the check is for a braced initialiser holding two
        # or more contract names.
        for block in re.findall(r"\{[^{}]*\}", text):
            named = {name for name in content if f'"{name}"' in block}
            assert len(named) < 2, (
                f"{path.name} enumerates contract objects "
                f"{sorted(named)} in a literal list instead of filtering the "
                "generated contract"
            )


def test_contract_matches_the_producer() -> None:
    """Every object the analysis can emit must be in the contract.

    A merged pair file only shows what one campaign happened to produce, so it
    cannot reveal an object written under conditions HF_PT2 never hit. This
    reads the producer instead.
    """
    text = PRODUCER.read_text()
    written = set(re.findall(r'->Write\("([^"]+)"\)', text))
    written |= set(re.findall(r'Write\("([^"]+)"\)', text))
    known = {row["name"] for row in objects()}
    missing = {
        name for name in written
        if name not in known and not name.startswith("h_")
    }
    assert not missing, (
        "status_analysis_THnSparse_qq.C writes objects absent from the "
        f"contract: {sorted(missing)}"
    )


def test_closure_and_presence_are_independent_and_coherent() -> None:
    for row in objects():
        name = row["name"]
        if row["closure"] == "checked":
            assert row["merge_semantics"] != "invariant", (
                f"{name}: an invariant object has no sum to close")
            assert row["presence"] == "required", (
                f"{name}: a conditional object cannot be unconditionally "
                "closure-checked")
        assert row["closure_reason"], f"{name}: closure_reason is empty"


def test_closure_content_object_count() -> None:
    """The number the ten-block closure reports per pair file, PER SCHEMA.

    object_content_sumw2_closure_checks / 300 must equal the count for the
    schema the data declares. Before the contract it was 5, because
    hFlavourClosure was missing from ValidatePairBlockClosure.C:266-268.

    These lists are deliberately NOT derived from the contract: a fixture that
    agrees with the code it checks cannot catch that code being wrong, which
    is the whole reason this test exists. An object silently dropped from the
    contract fails here.
    """
    payload = contract()
    versions = payload["schema_versions"]

    def content_for(version: str) -> list[str]:
        index = versions.index(version)
        return sorted(
            row["name"] for row in payload["objects"]
            if row["closure"] == "checked"
            and row["merge_semantics"] == "additive_content"
            and versions.index(row.get("since_schema", versions[0])) <= index
        )

    v2_expected = [
        "hAsKinematics",
        "hCorrelations",
        "hCorrelationsByOrigin",
        "hFlavourClosure",
        "hTrKinematics",
        "summed MULTIPLICITY",
    ]
    assert content_for("v2") == v2_expected, content_for("v2")
    # v3 adds the species-resolved parallel and drops nothing. hFlavourClosure
    # in particular must survive: the ratified design keeps it byte-identical
    # rather than widening it, because its merge cost carries the unexplained
    # 49x step.
    assert content_for("v3") == sorted(
        v2_expected + ["hFlavourClosureSpecies"]), content_for("v3")


def test_species_object_is_v3_only_and_parallel_not_a_replacement() -> None:
    payload = contract()
    row = next(r for r in payload["objects"]
               if r["name"] == "hFlavourClosureSpecies")
    assert row["since_schema"] == "v3", (
        "hFlavourClosureSpecies must be v3-only; requiring it of v2 would fail "
        "every correct v2 directory"
    )
    assert row["closure"] == "checked", (
        "the species object is summed across the ten blocks like its parallel, "
        "so it must be closure-checked -- an object added to the contract and "
        "not taught to the closure is how hFlavourClosure went unchecked"
    )
    original = next(r for r in payload["objects"]
                    if r["name"] == "hFlavourClosure")
    assert "since_schema" not in original, (
        "hFlavourClosure must remain present from the oldest schema; the "
        "species axis is a PARALLEL object, not a replacement"
    )


def test_closure_wrapper_derives_its_count_for_the_declared_schema() -> None:
    """The wrapper's derived count must be a function of the schema too.

    Deriving over every contract row would demand seven content checks from a
    correct v2 directory that carries six -- the same class of error as the
    pinned 1500, one version later. The wrapper must read the schema the macro
    reports and filter on since_schema.
    """
    wrapper = (ROOT / "Validation/validate_pair_block_closure.sh").read_text()
    assert "since_schema" in wrapper, (
        "validate_pair_block_closure.sh derives its object count without "
        "filtering on since_schema, so it will demand the v3 count from a v2 "
        "directory"
    )
    assert "analysis_schema=" in wrapper, (
        "the wrapper must read the schema the closure reports rather than "
        "assuming one"
    )


def test_flavour_closure_summary_is_exempt_with_a_stated_reason() -> None:
    row = next(r for r in objects() if r["name"] == "hFlavourClosureSummary")
    assert row["presence"] == "conditional"
    assert row["closure"] == "exempt"
    reason = row["closure_reason"]
    assert "SetBinContent" in reason and "Sumw2" in reason, (
        "the reason must record that the summary carries no meaningful Sumw2"
    )
    assert "weightedTriggers" in reason, (
        "the reason must record that it is written conditionally"
    )


def test_every_identity_checked_object_is_taught_to_the_closure() -> None:
    """An object marked identity_checked must have an expected value.

    THE DEFECT THIS PREVENTS. The closure's identity list used to be two
    hand-written names. An object could be added to the contract and silently
    never checked -- which is precisely the shape of the hFlavourClosure gap,
    one axis over. The set is now derived from the contract, and the closure
    owns only the expected VALUE per name, which is a compile-time constant
    and cannot come from JSON. This test pins the two halves together.
    """
    closure = (ROOT / "Validation/ValidatePairBlockClosure.C").read_text()
    marked = [row["name"] for row in objects() if row.get("identity_checked")]
    assert marked, "no object is identity_checked; the axis has gone missing"
    for name in marked:
        assert f'"{name}"' in closure, (
            f"the contract marks {name} identity_checked but "
            "ValidatePairBlockClosure.C has no expected value for it, so it "
            "would report a failure rather than check it"
        )


def test_identity_checked_objects_are_invariant_and_required() -> None:
    """Identity across blocks is meaningless for anything that is summed."""
    for row in objects():
        if not row.get("identity_checked"):
            continue
        assert row["merge_semantics"] == "invariant", (
            f"{row['name']}: an additive object's blocks differ by design, so "
            "asserting they are identical would always fail"
        )
        assert row["presence"] == "required", (
            f"{row['name']}: a conditional object cannot be unconditionally "
            "identity-checked"
        )


def test_species_legibility_objects_are_registered_and_v3_only() -> None:
    """F5 legibility: the axis must be decodable without this repository.

    The ordinal -> PDG map travels in every output file. Being written is not
    enough -- an object the contract does not know is rejected by the
    allowlist as 'unexpected', and an object no checker sees is the
    hFlavourClosure failure again.
    """
    by_name = {row["name"]: row for row in objects()}
    for name in ("species_ordinal_schema", "species_ordinal_labels",
                 "species_ordinal_digest"):
        assert name in by_name, f"{name} is written but not in the contract"
        row = by_name[name]
        assert row["since_schema"] == "v3", (
            f"{name} must be v3-only; a v2 file does not carry it")
        assert row.get("identity_checked"), (
            f"{name} must be identity-checked: two blocks filled against "
            "different ordinal tables would sum bins that do not mean the "
            "same thing")


def test_statistical_robustness_accepts_schemas_by_membership() -> None:
    """The last v3 gate: statistical_robustness must not exact-match the schema.

    It compared observed analysis_schema against a single value from
    config/statistical_robustness_v1.json, so a correct v3 file the object
    contract accepts would have been rejected there. It now checks MEMBERSHIP
    of the contract's declared tags, fail-closed on anything else.

    Note what is deliberately NOT asserted: the v2 literal still appears in
    validate_spec's expected_contracts, and correctly so -- that assertion
    checks what the SPEC FILE declares, not what a data file carries. Adding
    this module to the no-pin judge list would have failed on that legitimate
    line, so the data path is pinned directly instead.
    """
    tool = (ROOT / "tools/statistical_robustness.py").read_text()
    assert "ACCEPTED_ANALYSIS_SCHEMAS" in tool, (
        "statistical_robustness.py must derive the accepted schema set from "
        "the pair-object contract"
    )
    assert "schema_version_tags" in tool, (
        "the accepted set must come from the contract's schema_version_tags, "
        "not from a list restated in the tool"
    )
    # The exact-match dict must no longer carry it.
    body = tool.split("exact_strings = {", 1)
    assert len(body) == 2, "exact_strings block not found"
    block = body[1].split("}", 1)[0]
    assert '"analysis_schema"' not in block, (
        "analysis_schema is back in exact_strings; an exact match against one "
        "configured string rejects every correct file of any other schema"
    )


def main() -> int:
    # main() collects from globals(), so it must be INVOKED from the very end
    # of the file -- see the dispatcher there. It used to be invoked here, at
    # the midpoint, which silently ran only the tests defined above it: tests
    # appended later were collected by nothing and reported as passing. A
    # runner that cannot say how many tests it ran cannot be caught doing this,
    # so the count is printed.
    ran = 0
    for name, function in sorted(globals().items()):
        if name.startswith("test_") and callable(function):
            function()
            ran += 1
    print(f"pair-object-contract tests passed tests={ran} "
          f"objects={len(objects())}")
    return 0


# ---------------------------------------------------------------------------
# Schema versioning (F5 coexistence).
#
# The contract is exact-match in BOTH directions, so a contract that learned a
# v3 object would fail every correct v2 directory unless the object set is
# keyed on the schema the file itself declares. These tests pin the properties
# that make that safe, and they are written against the contract's invariants
# rather than against the generated header, so a header that drifted from the
# contract fails here rather than passing by agreeing with itself.
# ---------------------------------------------------------------------------


def contract() -> dict:
    return json.loads(CONTRACT.read_text())


def test_schema_versions_are_declared_oldest_first_with_unique_tags() -> None:
    payload = contract()
    versions = payload["schema_versions"]
    tags = payload["schema_version_tags"]
    assert versions, "schema_versions must not be empty"
    assert len(set(versions)) == len(versions), f"duplicates in {versions}"
    assert set(tags) == set(versions), (
        f"schema_version_tags keys {sorted(tags)} do not cover "
        f"schema_versions {sorted(versions)}"
    )
    # Two versions sharing one analysis_schema string would make a file
    # unattributable, and the selection would silently pick one.
    assert len(set(tags.values())) == len(tags), (
        f"two schema versions share one analysis_schema tag: {tags}"
    )


def test_every_since_schema_names_a_declared_version() -> None:
    payload = contract()
    versions = set(payload["schema_versions"])
    for row in payload["objects"]:
        since = row.get("since_schema", payload["schema_versions"][0])
        assert since in versions, (
            f"{row['name']}: since_schema {since!r} is not a declared version"
        )


def test_parse_is_fail_closed_for_unknown_schema() -> None:
    """An unrecognised analysis_schema must not resolve to any version.

    A default here -- newest or oldest -- is precisely how a contract change
    reaches one consumer and not its siblings. The generated parser must end
    in an unconditional `return false`.
    """
    text = HEADER.read_text()
    body = text.split("inline bool ParsePairSchemaVersion", 1)[1]
    body = body.split("\n}", 1)[0]
    tags = set(contract()["schema_version_tags"].values())
    for tag in tags:
        assert f'"{tag}"' in body, f"{tag} is not recognised by the parser"
    assert body.rstrip().endswith("return false;"), (
        "ParsePairSchemaVersion must fall through to `return false`, so an "
        "unknown schema fails closed instead of defaulting to a version"
    )


def test_no_consumer_pins_a_single_analysis_schema_literal() -> None:
    """The admissible schemas are the contract's list, not a literal.

    Validation/ValidatePairDirectory.C carried
    kRequiredAnalysisSchema = "paul_pair_objects_primary_ground_v2", which made
    the schema a constant rather than an axis: a correct v3 directory would
    have been rejected there whatever the object contract said. Consumers that
    JUDGE a directory must go through ParsePairSchemaVersion. The producer is
    exempt -- it writes exactly one schema, and that is its job.
    """
    judges = [
        ROOT / "Validation/ValidatePairDirectory.C",
        ROOT / "Validation/ValidatePairBlockClosure.C",
        ROOT / "plotting/Validate_THnSparse_Production.C",
        # Added by the v2-pin sweep. Each of these pinned the v2 schema string
        # and would have rejected a correct v3 directory at its own layer,
        # after the object contract had already accepted it.
        ROOT / "plotting/PairInputSelectionUtils.h",
        ROOT / "plotting/improvedPlotting_THnSparse.C",
        ROOT / "tools/validate_analysis_outputs.py",
    ]
    tags = set(contract()["schema_version_tags"].values())
    for path in judges:
        text = path.read_text()
        for tag in tags:
            # A bare literal in a judging consumer is the defect. Mentioning
            # the tag in a comment is fine; comparing against it is not.
            for line in text.splitlines():
                stripped = line.strip()
                # '#' is here because a Python judge joined this list in the
                # v2-pin sweep, and its comments legitimately name the literal
                # when explaining why the pin is gone.
                if (stripped.startswith("//") or stripped.startswith("*")
                        or stripped.startswith("#")):
                    continue
                assert f'"{tag}"' not in line, (
                    f"{path.name} pins the schema literal {tag!r} in code:\n"
                    f"  {stripped}\n"
                    "Judge the file through ParsePairSchemaVersion instead."
                )


def test_version_masks_are_monotonic_from_since_schema() -> None:
    """An object exists from its since_schema onward, never in a gap.

    The header encodes membership as a bitmask; a non-contiguous mask would
    mean an object present in v2, absent in v3 and back in v4, which no
    consumer is written to expect.
    """
    payload = contract()
    versions = payload["schema_versions"]
    text = HEADER.read_text()
    for row in payload["objects"]:
        since = row.get("since_schema", versions[0])
        expected = 0
        for index in range(versions.index(since), len(versions)):
            expected |= 1 << index
        literal = "0b" + format(expected, f"0{len(versions)}b")
        block = text.split('{"' + row["name"] + '",', 1)
        assert len(block) == 2, f"{row['name']} missing from the header"
        entry = block[1].split("}", 1)[0]
        assert literal in entry, (
            f"{row['name']}: expected mask {literal} for since_schema "
            f"{since!r}, header entry was:\n{entry}"
        )


if __name__ == "__main__":
    raise SystemExit(main())
