from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from helpers import ROOT


class SubmissionContract(unittest.TestCase):
    def test_render_is_deterministic_and_nominal_only(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            first = base / "first.sub"
            second = base / "second.sub"
            raw = base / "raw"
            work = base / "work"
            producer = base / "not-built-producer"
            common = [
                sys.executable, str(ROOT / "pipeline/generate/submit.py"), "plan",
                "--raw-root", str(raw), "--work-root", str(work),
                "--producer", str(producer),
            ]
            for output in (first, second):
                result = subprocess.run(common + ["--output", str(output)],
                                        cwd=str(ROOT), text=True,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("jobs=3000", result.stdout)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            text = first.read_text(encoding="utf-8")
            self.assertEqual(sum(line.startswith(("MONASH ", "JUNCTIONS ",
                                                  "CLOSEPACKING "))
                                 for line in text.splitlines()), 3000)
            self.assertNotIn("--systematics", text)
            self.assertNotIn("card-variant", text)
            self.assertIn("getenv = False", text)
            self.assertIn(" worker ", text)

    def test_default_plan_never_requires_or_contacts_scheduler(self):
        result = subprocess.run(
            [str(ROOT / "hadronization"), "generate"], cwd="/tmp", text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PLAN campaign=HF_RUN3_V1 jobs=3000", result.stdout)
        self.assertNotIn("submitted", result.stdout.lower())

    def test_submit_requires_explicit_site_configuration(self):
        self.assertFalse((ROOT / "config/site.conf").exists())
        result = subprocess.run(
            [str(ROOT / "hadronization"), "generate", "--submit"],
            cwd="/tmp", text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("requires configured config/site.conf", result.stderr)


if __name__ == "__main__":
    unittest.main()
