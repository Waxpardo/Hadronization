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
            ROOT / "pipeline/generate/runtime.py",
            ROOT / "pipeline/generate/study_contract.py",
            ROOT / "pipeline/generate/study_contract.hpp",
            ROOT / "pipeline/generate/validate_raw.cpp",
            ROOT / "pipeline/generate/producer.cpp",
            ROOT / "pipeline/generate/physics.hpp",
            ROOT / "config/study.json",
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
            "config/study.json", "config/analysis.json", "config/site.example.conf",
            "config/tunes/monash.cmnd", "config/tunes/junctions.cmnd",
            "config/tunes/close_packing.cmnd"}
        paths = self.tracked_and_new_paths()
        self.assertEqual({path for path in paths if path.startswith("config/")},
                         expected_config)
        self.assertEqual(
            {path for path in paths if path.startswith("pipeline/analyze/")},
            {"pipeline/analyze/analyze.cpp",
             "pipeline/analyze/import_accepted.py",
             "pipeline/analyze/run.py",
             "pipeline/analyze/reference_analysis.C"})
        self.assertEqual(
            {path for path in paths if path.startswith("pipeline/reduce/")},
            {"pipeline/reduce/reduce.cpp", "pipeline/reduce/run.py",
             "pipeline/reduce/statistics.hpp"})
        self.assertEqual(
            {path for path in paths if path.startswith("pipeline/plot/")},
            {"pipeline/plot/reference_plotting.C"})

    def test_importer_metadata_builders_match_the_retained_plane(self):
        path = ROOT / "pipeline/analyze/import_accepted.py"
        spec = importlib.util.spec_from_file_location("accepted_importer", str(path))
        importer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(importer)
        self.assertEqual(importer.DATA_README,
                         (ROOT / "data/README.md").read_text(encoding="utf-8"))
        campaign = json.loads((ROOT / "data/campaign.json").read_text(encoding="utf-8"))
        self.assertEqual(
            campaign["current_interpretation_definitions"]["files"],
            importer.current_definition_entries(ROOT))
        result = json.loads((ROOT / "results/manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(result["current_study_definition"],
                         importer.current_study_definition(ROOT))

    def test_importer_parity_gate_rejects_an_omitted_definition_record(self):
        path = ROOT / "pipeline/analyze/import_accepted.py"
        spec = importlib.util.spec_from_file_location("accepted_importer_mutation", str(path))
        importer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(importer)
        campaign = json.loads((ROOT / "data/campaign.json").read_text(encoding="utf-8"))
        campaign["current_interpretation_definitions"]["files"].pop()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            (output / "data").mkdir()
            (output / "results").mkdir()
            (output / "data/campaign.json").write_text(
                json.dumps(campaign), encoding="utf-8")
            (output / "data/README.md").write_text(importer.DATA_README, encoding="utf-8")
            shutil.copyfile(ROOT / "results/manifest.json", output / "results/manifest.json")
            with self.assertRaisesRegex(ValueError, "definition record"):
                importer.validate_metadata_parity(output, ROOT)


if __name__ == "__main__":
    unittest.main()
