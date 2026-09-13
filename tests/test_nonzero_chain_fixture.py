"""Evidence-path admission for the published synthetic whole-chain fixture."""

import importlib.util
import os
from pathlib import Path
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
