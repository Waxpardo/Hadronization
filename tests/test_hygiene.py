from pathlib import Path
import importlib.util
import json
import re
import shutil
import subprocess
import tempfile
import unittest

from helpers import ROOT


class LeanTreeContract(unittest.TestCase):
    def tracked_and_new_paths(self):
        output = subprocess.check_output(
            ["git", "-C", str(ROOT), "ls-files", "--cached", "--others",
             "--exclude-standard", "-z"])
        return {item.decode("utf-8") for item in output.split(b"\0") if item}

    def test_visible_topology_and_forbidden_families(self):
        paths = self.tracked_and_new_paths()
        top = {path.split("/", 1)[0] for path in paths}
        expected = {".gitignore", "CITATION.cff", "README.md", "hadronization",
                    "setup.sh", "config", "pipeline", "data", "tests", "docs"}
        self.assertEqual(top, expected)
        forbidden = {"paper", "evidence", "docs2", "environment",
                     "Validation", "contracts", "tools", "generation", "analysis",
                     "merging", "extraction", "plotting"}
        self.assertTrue(forbidden.isdisjoint(top))
        self.assertFalse(any(path == "Makefile" or path.endswith("/Makefile")
                             for path in paths))

    def test_no_tracked_cache_or_build_products(self):
        paths = self.tracked_and_new_paths()
        forbidden_suffixes = (".pyc", ".so", ".d", ".pcm", ".o", ".dylib")
        self.assertFalse(any("__pycache__" in path.split("/") or
                             path.endswith(forbidden_suffixes) or
                             path.endswith(".DS_Store") for path in paths))

    def test_active_runtime_has_no_retired_selector_or_absolute_project_root(self):
        active = [
            ROOT / "hadronization", ROOT / "setup.sh",
            ROOT / "pipeline/generate/submit.py",
            ROOT / "pipeline/generate/runtime.py",
            ROOT / "pipeline/generate/study_contract.py",
            ROOT / "pipeline/generate/study_contract.hpp",
            ROOT / "pipeline/generate/validate_raw.cpp",
            ROOT / "pipeline/generate/producer.cpp",
            ROOT / "pipeline/generate/physics.hpp",
            ROOT / "pipeline/plot/render.cpp",
            ROOT / "pipeline/plot/run.py",
            ROOT / "config/study.json",
            ROOT / "config/plot.json",
        ]
        text = "\n".join(path.read_text(encoding="utf-8") for path in active)
        for token in ("/Users/", "/data/alice/", "HF_SYS_",
                      "HADRONIZATION_BASE",
                      "HADRONIZATION_RESULTS_ROOT"):
            self.assertNotIn(token, text)
        self.assertNotRegex(text, r'os\.environ\s*\[\s*["\']HADRONIZATION_DATASET')
        self.assertNotRegex(text, r'os\.environ\.get\(\s*["\']HADRONIZATION_DATASET')
        for command in ((str(ROOT / "hadronization"), "generate", "--help"),
                        ("python3", str(ROOT / "pipeline/generate/submit.py"),
                         "plan", "--help")):
            help_text = subprocess.check_output(command, text=True).lower()
            self.assertNotIn("--systematic", help_text)
            self.assertNotIn("--variation", help_text)
            self.assertNotIn("--dataset", help_text)

    def test_local_includes_resolve(self):
        sources = list((ROOT / "pipeline").rglob("*.cpp"))
        sources += list((ROOT / "pipeline").rglob("*.hpp"))
        sources += list((ROOT / "pipeline").rglob("*.C"))
        for source in sources:
            for include in re.findall(r'^#include\s+"([^"]+)"',
                                      source.read_text(encoding="utf-8"), re.MULTILINE):
                if include.startswith("Pythia8/") or include.endswith(".h"):
                    continue
                candidates = [source.parent / include,
                              ROOT / "pipeline/generate" / include]
                self.assertTrue(any(path.resolve().is_file() for path in candidates),
                                "{} -> {}".format(source, include))

    def test_only_target_layout_exceptions_exist(self):
        expected_config = {
            "config/study.json", "config/analysis.json", "config/query.json",
            "config/plot.json", "config/plot-dplus.json", "config/plot-all-tune.json",
            "config/site.example.conf",
            "config/tunes/monash.cmnd", "config/tunes/junctions.cmnd",
            "config/tunes/close_packing.cmnd"}
        paths = self.tracked_and_new_paths()
        self.assertEqual({path for path in paths if path.startswith("config/")},
                         expected_config)
        self.assertEqual(
            {path for path in paths if path.startswith("pipeline/analyze/")},
            {"pipeline/analyze/analyze.cpp", "pipeline/analyze/run.py"})
        self.assertEqual(
            {path for path in paths if path.startswith("pipeline/query/")},
            {"pipeline/query/collection.py",
             "pipeline/query/condor.py", "pipeline/query/merge.py",
             "pipeline/query/merge_sparse.hpp",
             "pipeline/query/model.py", "pipeline/query/query.cpp",
             "pipeline/query/row_schema.hpp", "pipeline/query/run.py",
             "pipeline/query/selection.hpp", "pipeline/query/sparse.hpp",
             "pipeline/query/support.py", "pipeline/query/site_probe.py",
             "pipeline/query/publication.py"})
        self.assertEqual(
            {path for path in paths if path.startswith("pipeline/reduce/")},
            {"pipeline/reduce/accounting.py",
             "pipeline/reduce/archive.py", "pipeline/reduce/archive_v4.py",
             "pipeline/reduce/native.py", "pipeline/reduce/support_scan.cpp",
             "pipeline/reduce/native_engine.cpp", "pipeline/reduce/native_runner.py",
             "pipeline/reduce/native_v4.py", "pipeline/reduce/native_v4_result.py",
             "pipeline/reduce/projection.py", "pipeline/reduce/public_v4.py",
             "pipeline/reduce/statistics.hpp", "pipeline/reduce/typed_nodes.py"})
        self.assertEqual(
            {path for path in paths if path.startswith("pipeline/plot/")},
            {"pipeline/plot/render.cpp", "pipeline/plot/run.py"})


if __name__ == "__main__":
    unittest.main()
