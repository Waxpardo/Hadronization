#!/usr/bin/env python3
"""Exercise and require canonical central-versus-ten-block closure."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

# Same directory as this driver, so no path setup is needed.
from sandbox_tree import tracked_paths


ROOT = Path(__file__).resolve().parents[1]



def _extract_command(text: str, needle: str) -> str:
    """Return the full backslash-continued command line containing `needle`."""
    lines = text.splitlines()
    starts = [i for i, line in enumerate(lines) if needle in line]
    if len(starts) != 1:
        raise AssertionError(
            f"expected exactly one invocation of {needle}, found {len(starts)}"
        )
    index = starts[0]
    collected = [lines[index]]
    while collected[-1].rstrip().endswith("\\"):
        index += 1
        collected.append(lines[index])
    return "\n".join(collected)


def _run_call_site(merge_text: str) -> list[str]:
    """Execute the driver's closure invocation against a recording stub.

    Returns the argument vector the callee actually receives. The driver's
    variables are bound to sentinels so that a wrong slot is unmistakable
    rather than merely a different-looking string.
    """
    command = _extract_command(
        merge_text, '"${project_base}/Validation/validate_pair_block_closure.sh"'
    )
    # Drop the `if ! ` that opens it and the redirect that closes it; what is
    # left is the invocation exactly as the driver spells it.
    command = command.strip()
    if command.startswith("if ! "):
        command = command[len("if ! "):]
    cut = command.find('>"${closure_stage}"')
    if cut == -1:
        raise AssertionError("closure invocation no longer redirects to the stage file")
    command = command[:cut]

    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        (base / "Validation").mkdir()
        stub = base / "Validation" / "validate_pair_block_closure.sh"
        stub.write_text('#!/bin/bash\nprintf "%s\\n" "$@"\n')
        stub.chmod(0o755)
        script = "\n".join([
            "set -euo pipefail",
            f'project_base="{base}"',
            'analyzed_data_base="/SENTINEL_DATA"',
            'output_tag="SENTINEL_TAG"',
            'tune="SENTINEL_TUNE"',
            'canonical_events_per_tune="SENTINEL_EVENTS"',
            'expected_pair_schema="SENTINEL_SCHEMA"',
            'expected_pair_schema_tag="SENTINEL_SCHEMA_RESOLVED"',
            command,
        ])
        result = subprocess.run(
            ["bash", "-c", script], text=True, capture_output=True, check=False
        )
    if result.returncode != 0:
        raise AssertionError(
            f"the driver's closure invocation would not run:\n{result.stderr}"
        )
    return result.stdout.splitlines()


def assert_driver_calls_closure_correctly(merge_text: str) -> None:
    argv = _run_call_site(merge_text)
    if len(argv) != 4:
        raise AssertionError(
            "validate_pair_block_closure.sh takes CENTRAL BLOCKS EXPECTED_SCHEMA "
            f"[EXPECTED_CENTRAL_EVENTS]; the driver passes {len(argv)} arguments: {argv}"
        )
    central, blocks, schema, events = argv
    assert "complete_root_SENTINEL_TAG_SENTINEL_TUNE" in central, central
    assert "combined_root_subSamples_SENTINEL_TUNE" in blocks, blocks
    if schema == "SENTINEL_EVENTS":
        raise AssertionError(
            "REGRESSION: the driver passes the event count where the closure gate "
            "requires EXPECTED_SCHEMA. This is the 2026-08-13 defect; it wastes a "
            "whole campaign's merging before it is discovered."
        )
    if schema != "SENTINEL_SCHEMA":
        raise AssertionError(
            f"argument 3 must be the caller-stated schema, got {schema!r}"
        )
    if events != "SENTINEL_EVENTS":
        raise AssertionError(
            f"argument 4 must be the per-tune event count, got {events!r}"
        )


def assert_expected_schema_has_no_default(merge_text: str) -> None:
    """The schema input must fail closed, and must do so before the work."""
    if "HADRONIZATION_EXPECTED_PAIR_SCHEMA:-}" not in merge_text:
        raise AssertionError(
            "HADRONIZATION_EXPECTED_PAIR_SCHEMA must be read with an empty "
            "default so that absence is detectable; any other default silently "
            "picks a schema on the campaign's behalf"
        )
    guard = _extract_command(merge_text, 'expected_pair_schema="${HADRONIZATION_EXPECTED_PAIR_SCHEMA')
    lines = merge_text.splitlines()
    start = lines.index(guard)
    end = start
    while lines[end].strip() != "fi":
        end += 1
    block = "\n".join(lines[start:end + 1])

    env = {k: v for k, v in os.environ.items()
           if k != "HADRONIZATION_EXPECTED_PAIR_SCHEMA"}
    absent = subprocess.run(
        ["bash", "-c", block], text=True, capture_output=True, check=False, env=env
    )
    if absent.returncode == 0:
        raise AssertionError(
            "the driver accepted an absent HADRONIZATION_EXPECTED_PAIR_SCHEMA; "
            "a required input with no refusal is not required"
        )
    if "HADRONIZATION_EXPECTED_PAIR_SCHEMA is required" not in absent.stderr:
        raise AssertionError(
            f"refusal must name the missing input; got:\n{absent.stderr}"
        )
    env["HADRONIZATION_EXPECTED_PAIR_SCHEMA"] = "v3"
    present = subprocess.run(
        ["bash", "-c", block], text=True, capture_output=True, check=False, env=env
    )
    if present.returncode != 0:
        raise AssertionError(
            f"the driver refused a valid schema tag:\n{present.stderr}"
        )


def assert_the_check_can_fail(merge_text: str) -> None:
    """Negative control: re-break the call site, and require a failure.

    A gate that has never been seen to fail is not known to be a gate. This
    reproduces the exact 2026-08-13 mutation -- delete the schema argument --
    and requires assert_driver_calls_closure_correctly to reject it.
    """
    broken = merge_text.replace('       "${expected_pair_schema}" \\\n', "", 1)
    if broken == merge_text:
        raise AssertionError("could not construct the mutation; the call site moved")
    try:
        assert_driver_calls_closure_correctly(broken)
    except AssertionError:
        return
    raise AssertionError(
        "MUTATION SURVIVED: removing the schema argument left this test green, "
        "which is precisely the hole that let the defect ship"
    )



def _closure_call_sites() -> list[tuple[Path, str]]:
    """Every shell invocation of the closure wrapper in the tree.

    Two call sites have now shipped broken -- merge_root_files.sh passing the
    event count into the schema slot, and tune_chain.sh passing two arguments
    to a gate that requires three. Both were invisible to a test that looked at
    one file. Enumerating the callers is what stops a third.
    """
    sites: list[tuple[Path, str]] = []
    # Every tracked shell script, not every file on this disk. The sweep stays
    # over the tree so a new caller is enumerated; git decides what is in it,
    # which also drops .git without a name rule.
    tracked = tracked_paths(ROOT)
    for path in sorted(p for p in ROOT.rglob("*.sh") if p in tracked):
        if path.name == "validate_pair_block_closure.sh":
            continue
        for line in path.read_text().splitlines():
            stripped = line.strip()
            if "validate_pair_block_closure.sh" not in stripped:
                continue
            # A line that HASHES the closure script is not a line that RUNS it.
            # Both spellings are matched: the tree uses `shasum -a 256` (macOS
            # ships no `sha256sum`), and an archived caller may still use the
            # other, so neither spelling can turn a digest line into a site.
            if (stripped.startswith("#")
                    or "shasum" in stripped
                    or "sha256sum" in stripped):
                continue
            sites.append((path, line))
    return sites


def _argv_of(text: str, needle: str) -> list[str]:
    """Run one invocation against a stub, binding every variable to a sentinel."""
    command = _extract_command(text, needle).strip()
    if command.startswith("if ! "):
        command = command[len("if ! "):]
    for cut in ('>"${closure_stage}"', '>> "$LOG"', ">>\"$LOG\""):
        index = command.find(cut)
        if index != -1:
            command = command[:index]
            break
    names = sorted(set(re.findall(r"\$\{?([A-Za-z_][A-Za-z_0-9]*)\}?", command)))
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        (base / "Validation").mkdir()
        stub = base / "Validation" / "validate_pair_block_closure.sh"
        stub.write_text('#!/bin/bash\nprintf "%s\\n" "$@"\n')
        stub.chmod(0o755)
        bindings = [f'{name}="SENTINEL_{name.upper()}"' for name in names]
        # Replace the callee wherever it resolves from -- a bare relative path
        # in one caller, an expansion of ${project_base} in another.
        invocation = re.sub(
            r"""[^\s"']*validate_pair_block_closure\.sh""", str(stub), command, count=1
        )
        script = "\n".join(["set -uo pipefail"] + bindings + [invocation])
        result = subprocess.run(
            ["bash", "-c", script], text=True, capture_output=True, check=False
        )
    if result.returncode != 0:
        raise AssertionError(f"invocation would not run:\n{result.stderr}")
    return result.stdout.splitlines()


def assert_every_caller_passes_a_schema() -> None:
    sites = _closure_call_sites()
    if not sites:
        raise AssertionError("no closure call sites found; the search is wrong")
    for path, line in sites:
        argv = _argv_of(path.read_text(), line.strip().split("validate_pair_block_closure.sh")[0]
                        + "validate_pair_block_closure.sh")
        rel = path.relative_to(ROOT)
        if len(argv) < 3:
            raise AssertionError(
                f"{rel} calls the closure gate with {len(argv)} arguments; "
                f"EXPECTED_SCHEMA is required as the third: {argv}"
            )
        if argv[2].lstrip("-").isdigit():
            raise AssertionError(
                f"{rel} passes the number {argv[2]!r} where EXPECTED_SCHEMA belongs; "
                "this is the 2026-08-13 defect"
            )
        if "EVENTS" in argv[2].upper():
            raise AssertionError(
                f"{rel} passes {argv[2]!r} -- an event count -- into the schema slot"
            )
    print(f"closure call sites checked: {len(sites)}")


def main() -> int:
    macro = ROOT / "Validation/ValidatePairBlockClosure.C"
    wrapper = ROOT / "Validation/validate_pair_block_closure.sh"
    merge = ROOT / "merging" / "merge_root_files.sh"
    macro_text = macro.read_text()
    wrapper_text = wrapper.read_text()
    merge_text = merge.read_text()
    assert "Hadronization::kPairDefinitions" in macro_text
    # This used to assert the literal '"hCorrelationsByOrigin"' appeared in the
    # macro. That pinned the implementation -- a hand-written list -- rather
    # than the behaviour, so it went red the moment the list was replaced by
    # the generated contract in b01536b, even though the closure's coverage had
    # strictly increased. It is the same failure mode as a fixture derived from
    # the code under test: assert what must be true of the product, not how the
    # source happens to spell it.
    contract = json.loads(
        (ROOT / "config/pair_file_object_contract_v1.json").read_text()
    )
    closure_checked = {
        row["name"] for row in contract["objects"]
        if row["closure"] == "checked"
        and row["merge_semantics"] == "additive_content"
    }
    assert "hCorrelationsByOrigin" in closure_checked
    assert "hFlavourClosure" in closure_checked, (
        "hFlavourClosure must stay closure-checked; it was silently skipped "
        "until b01536b"
    )
    assert "Hadronization::ClosureCheckedObjects" in macro_text, (
        "the closure must filter the generated contract, not restate names"
    )
    assert '"associate_origin_category_schema"' in macro_text
    assert '"associate_origin_category_labels"' in macro_text
    assert "InvariantObjectStringMatches" in macro_text
    assert "GetBinError2" in macro_text
    assert "GetSumw2()->At" in macro_text
    assert "central_pair_files=300 block_pair_files=3000" in wrapper_text
    # NOT `invariant_metadata_checks=600`. That literal was this test's own
    # copy of a number that is a function of the contract -- two hand-listed
    # objects x 300 -- and it went stale the moment v3 added the three
    # species-axis legibility objects, taking the real count to 1500. It is
    # the same defect as B12's pinned 1500, in the test rather than the
    # wrapper. The wrapper must DERIVE the count from the contract's
    # identity_checked axis, so that is what is asserted.
    assert "invariant_metadata_checks=$(( identity_objects * 300 ))" in (
        wrapper_text), (
        "validate_pair_block_closure.sh must derive invariant_metadata_checks "
        "from the contract's identity_checked axis rather than pinning it; a "
        "pinned count goes stale at the next contract change"
    )
    assert "identity_checked" in wrapper_text, (
        "the wrapper must read the identity_checked axis, not a hand-listed "
        "pair of object names"
    )
    assert "Hadronization::IdentityCheckedObjects" in macro_text, (
        "the closure must derive WHICH objects are identity-checked from the "
        "contract; a hand-written list is how an object gets added and "
        "silently never checked"
    )
    # THE OPS CORRECTION, and it cost eleven hours of cluster time.
    #
    # This assertion used to be the whole of this test's interest in the merge
    # driver: that the string "validate_pair_block_closure.sh" appears in it.
    # A TEST THAT ASSERTS A CALLEE'S NAME CERTIFIES NOTHING ABOUT THE CALL.
    # When 8f410a43 made EXPECTED_SCHEMA a required third argument, the driver
    # kept passing ${canonical_events_per_tune} into that slot; the name was
    # still there, the suite stayed green at 52/52, and the driver's closure
    # loop could not have succeeded once between 2026-08-13 and 2026-08-18.
    # HF_SYS_MUR_UP performed all 33 merges and died at the gate with zero
    # markers before anyone looked at the arguments.
    #
    # So the name check stays -- it is cheap -- but it is no longer the check.
    # What follows EXECUTES the driver's own invocation against a recording
    # stub and inspects the argument vector that actually arrives.
    assert "validate_pair_block_closure.sh" in merge_text
    assert_driver_calls_closure_correctly(merge_text)
    assert_expected_schema_has_no_default(merge_text)
    assert_the_check_can_fail(merge_text)
    assert_every_caller_passes_a_schema()

    root = shutil.which("root")
    if root is None:
        raise RuntimeError("ROOT is required for the pair-block closure test")
    result = subprocess.run(
        [
            root,
            "-l",
            "-b",
            "-q",
            "-e",
            ".L Validation/ValidatePairBlockClosure.C",
            "-e",
            "gSystem->Exit(TestPairBlockClosureArithmetic());",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    output = result.stdout + result.stderr
    marker = (
        "PAIR_BLOCK_CLOSURE_TEST errors=0 "
        "exact_content_sumw2_sum_accepted=true "
        "histogram_mutation_rejected=true "
        "sparse_mutation_rejected=true"
    )
    if result.returncode != 0 or marker not in output:
        raise AssertionError(f"pair-block closure test failed:\n{output}")
    print("pair-block closure test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
