from pathlib import Path
import re
import subprocess
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
                    "setup.sh", "config", "pipeline", "data", "results", "tests"}
        self.assertEqual(top, expected)
        forbidden = {"paper", "evidence", "docs", "docs2", "environment",
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
            ROOT / "pipeline/generate/producer.cpp",
            ROOT / "pipeline/generate/physics.hpp",
            ROOT / "pipeline/generate/selected_states.hpp",
            ROOT / "pipeline/generate/tune_settings.hpp",
            ROOT / "config/study.json",
        ]
        text = "\n".join(path.read_text(encoding="utf-8") for path in active)
        for token in ("/Users/", "/data/alice/", "HF_SYS_", "--systematics",
                      "card_variant", "HADRONIZATION_BASE",
                      "HADRONIZATION_RESULTS_ROOT"):
            self.assertNotIn(token, text)
        self.assertNotRegex(text, r'os\.environ\s*\[\s*["\']HADRONIZATION_DATASET')
        self.assertNotRegex(text, r'os\.environ\.get\(\s*["\']HADRONIZATION_DATASET')

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
            "config/study.json", "config/site.example.conf",
            "config/tunes/monash.cmnd", "config/tunes/junctions.cmnd",
            "config/tunes/close_packing.cmnd"}
        paths = self.tracked_and_new_paths()
        self.assertEqual({path for path in paths if path.startswith("config/")},
                         expected_config)
        self.assertEqual(
            {path for path in paths if path.startswith("pipeline/analyze/")},
            {"pipeline/analyze/import_accepted.py",
             "pipeline/analyze/reference_analysis.C"})
        self.assertEqual(
            {path for path in paths if path.startswith("pipeline/plot/")},
            {"pipeline/plot/reference_plotting.C"})


if __name__ == "__main__":
    unittest.main()
