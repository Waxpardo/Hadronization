"""Evidence-path admission for the published synthetic whole-chain fixture."""

import contextlib
import copy
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tests/fixtures/nonzero_chain_v22"


def load_tool(name):
    spec = importlib.util.spec_from_file_location("nonzero_" + name, TOOLS / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class NonzeroFixturePathAdmission(unittest.TestCase):
    def test_builder_requires_explicit_fresh_nonsymlink_base(self):
        build = load_tool("build")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            with patch.dict(os.environ, {"NONZERO_CHAIN_BASE": ""}):
                with self.assertRaisesRegex(ValueError, "NONZERO_CHAIN_BASE"):
                    build.claim_fresh_base()
            existing = root / "sealed"
            existing.mkdir()
            sentinel = existing / "sentinel"
            sentinel.write_bytes(b"accepted evidence")
            with patch.dict(os.environ, {"NONZERO_CHAIN_BASE": str(existing)}), \
                    patch.object(build.AnalysisShardContract, "setUpClass") as compile_start:
                with self.assertRaises(FileExistsError):
                    build.main()
                compile_start.assert_not_called()
            self.assertEqual(sentinel.read_bytes(), b"accepted evidence")
            link = root / "link"
            link.symlink_to(existing, target_is_directory=True)
            with patch.dict(os.environ, {"NONZERO_CHAIN_BASE": str(link / "fresh")}):
                with self.assertRaisesRegex(ValueError, "symlink"):
                    build.claim_fresh_base()
            fresh = root / "fresh"
            with patch.dict(os.environ, {"NONZERO_CHAIN_BASE": str(fresh)}):
                self.assertEqual(build.claim_fresh_base(), fresh)
            self.assertTrue(fresh.is_dir())
            with patch.dict(os.environ, {"NONZERO_CHAIN_BASE": str(fresh)}):
                with self.assertRaises(FileExistsError):
                    build.claim_fresh_base()

    def test_oracle_requires_explicit_input_and_exclusive_report(self):
        oracle = load_tool("oracle")
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory).resolve() / "fixture"
            base.mkdir()
            with patch.dict(os.environ, {"NONZERO_CHAIN_BASE": ""}):
                with self.assertRaisesRegex(ValueError, "NONZERO_CHAIN_BASE"):
                    oracle.admitted_paths()
            with patch.dict(os.environ, {"NONZERO_CHAIN_BASE": str(base)}, clear=True):
                admitted, report = oracle.admitted_paths()
                self.assertEqual(admitted, base)
                self.assertEqual(report, base / "oracle.json")
                oracle.publish_report(report, {"check": "first"})
                before = report.read_bytes()
                with self.assertRaises(FileExistsError):
                    oracle.admitted_paths()
                with self.assertRaises(FileExistsError):
                    oracle.publish_report(report, {"check": "replacement"})
                self.assertEqual(report.read_bytes(), before)
                alternate = base / "second.json"
                with patch.dict(os.environ, {"NONZERO_CHAIN_REPORT": str(alternate)}):
                    self.assertEqual(oracle.admitted_paths()[1], alternate)
                report_link = base / "report-link.json"
                report_link.symlink_to(report)
                with patch.dict(os.environ, {"NONZERO_CHAIN_REPORT": str(report_link)}):
                    with self.assertRaisesRegex(ValueError, "nonsymlinked"):
                        oracle.admitted_paths()
            link = Path(directory).resolve() / "linked"
            link.symlink_to(base, target_is_directory=True)
            with patch.dict(os.environ, {"NONZERO_CHAIN_BASE": str(link)}):
                with self.assertRaisesRegex(ValueError, "nonsymlinked"):
                    oracle.admitted_paths()


class NonzeroFixtureEndToEndOracle(unittest.TestCase):
    """Build the small current chain once and exercise the standalone oracle."""

    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.base = Path(cls.temporary.name).resolve() / "current-chain"
        build = load_tool("build")
        build.SOURCES_PER_BLOCK = 1
        with patch.dict(os.environ, {"NONZERO_CHAIN_BASE": str(cls.base)}), \
                contextlib.redirect_stdout(io.StringIO()):
            build.main()
        cls.root_mutator = cls.base / "merge-mutator"
        source = (TOOLS / "mutate_merge.cpp").read_text()
        build.AnalysisShardContract._compile(
            source, cls.base / "merge-mutator.cpp", cls.root_mutator)
        cls.mutator_environment = build.AnalysisShardContract.environment
        cls.oracle = load_tool("oracle")

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_current_synthetic_chain_oracle_runs_through_completion(self):
        report = self.base / "standalone-oracle.json"
        with patch.dict(os.environ, {"NONZERO_CHAIN_BASE": str(self.base),
                                     "NONZERO_CHAIN_REPORT": str(report)}), \
                contextlib.redirect_stdout(io.StringIO()):
            self.oracle.main()
        payload = json.loads(report.read_text())
        self.assertEqual(payload["schema"], "nonzero_chain_v22_independent_row_oracle_v1")
        self.assertEqual(len(payload["sparse_physical_equality"]), 15)

    def _write_root_mutant(self, source, destination, target, mode):
        subprocess.run([str(self.root_mutator), str(source), str(destination), target, mode],
                       check=True, env=self.mutator_environment, capture_output=True)

    def test_oracle_refuses_inventory_cell_sumw2_and_entry_mutants(self):
        index_path = self.base / "merged/index.json"
        original_bytes = index_path.read_bytes()
        original = json.loads(original_bytes)
        part = original["partitions"][0]
        family = sorted(part["sparse_objects"])[0]
        target = part["sparse_objects"][family][0]["name"]
        cases = []
        missing = copy.deepcopy(original)
        missing["partitions"][0]["sparse_objects"][family].pop()
        cases.append(("missing", missing))
        duplicated = copy.deepcopy(original)
        duplicated["partitions"][0]["sparse_objects"][family].append(
            copy.deepcopy(duplicated["partitions"][0]["sparse_objects"][family][-1]))
        cases.append(("duplicated", duplicated))
        for mode in ("coordinate", "content", "sumw2", "entries"):
            mutated = copy.deepcopy(original)
            source = Path(part["root"]["path"])
            destination = self.base / ("mutant-" + mode + ".root")
            self._write_root_mutant(source, destination, target, mode)
            mutated["partitions"][0]["root"]["path"] = str(destination)
            cases.append((mode, mutated))
        try:
            for mode, value in cases:
                with self.subTest(mode=mode):
                    index_path.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")))
                    with self.assertRaises(AssertionError):
                        self.oracle.sparse_equality(self.base)
        finally:
            index_path.write_bytes(original_bytes)
