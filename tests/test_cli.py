import os
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from helpers import ROOT


class CliContract(unittest.TestCase):
    def run_cli(self, *arguments, cwd="/tmp"):
        return subprocess.run([str(ROOT / "hadronization")] + list(arguments),
                              cwd=cwd, text=True, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)

    def test_root_relative_doctor_and_help_surface(self):
        doctor = self.run_cli("doctor")
        self.assertEqual(doctor.returncode, 0, doctor.stderr)
        self.assertIn("REQUIRED repository: OK", doctor.stdout)
        self.assertIn("REQUIRED Python: OK", doctor.stdout)
        self.assertIn("RUNTIME ROOT=", doctor.stdout)
        help_result = self.run_cli("--help")
        self.assertEqual(help_result.returncode, 0)
        for command in ("doctor", "generate", "analyze", "merge", "reduce",
                        "plot", "verify", "clean"):
            self.assertIn(command, help_result.stdout)

    def test_unavailable_stages_refuse_without_fallthrough(self):
        expected = {"analyze": "ANALYZE-1", "merge": "ANALYZE-1",
                    "reduce": "ANALYZE-1", "plot": "PLOT-1"}
        for command, successor in expected.items():
            result = self.run_cli(command)
            self.assertEqual(result.returncode, 3)
            self.assertEqual(
                result.stderr.strip(),
                "ERROR: {} not implemented until {}".format(command, successor))
        unknown = self.run_cli("retired-command")
        self.assertEqual(unknown.returncode, 2)

    def test_setup_is_idempotent_and_has_no_dataset_dependency(self):
        script = r'''
unset HADRONIZATION_DATASET
source "$1"
first="$PATH"
source "$1"
test "$first" = "$PATH"
test -z "${HADRONIZATION_DATASET+x}"
'''
        result = subprocess.run(["/bin/bash", "-c", script, "bash",
                                 str(ROOT / "setup.sh")], text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_clean_defaults_dry_and_protects_raw(self):
        with tempfile.TemporaryDirectory() as directory:
            checkout = Path(directory) / "checkout"
            checkout.mkdir()
            shutil.copy2(str(ROOT / "hadronization"), str(checkout / "hadronization"))
            (checkout / ".DS_Store").write_text("residue", encoding="utf-8")
            cache = checkout / "module/__pycache__"
            cache.mkdir(parents=True)
            (cache / "x.pyc").write_bytes(b"cache")
            raw = checkout / "data/raw"
            raw.mkdir(parents=True)
            protected = raw / "unique.so"
            protected.write_bytes(b"raw")
            completed = checkout / "data/work/evidence/MONASH/job000/attempt00"
            scratch = completed / "scratch"
            scratch.mkdir(parents=True)
            (scratch / "partial.root").write_bytes(b"scratch")
            (completed / "outcome.json").write_text(json.dumps({
                "state": "accepted", "finished_unix_seconds": 1,
                "cleanup_after_days": 1}), encoding="utf-8")
            active = checkout / "data/work/evidence/MONASH/job001/attempt00"
            (active / "scratch").mkdir(parents=True)
            (active / "scratch/partial.root").write_bytes(b"active")
            (active / "outcome.json").write_text(json.dumps({
                "state": "submitted", "finished_unix_seconds": 1,
                "cleanup_after_days": 1}), encoding="utf-8")
            dry = subprocess.run([str(checkout / "hadronization"), "clean"],
                                 cwd="/tmp", text=True, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
            self.assertEqual(dry.returncode, 0, dry.stderr)
            self.assertTrue((checkout / ".DS_Store").exists())
            self.assertIn("REMOVE .DS_Store", dry.stdout)
            self.assertNotIn("data/raw", dry.stdout)
            self.assertIn("data/work/evidence/MONASH/job000/attempt00/scratch", dry.stdout)
            self.assertNotIn("job001/attempt00/scratch", dry.stdout)
            applied = subprocess.run(
                [str(checkout / "hadronization"), "clean", "--apply"],
                cwd="/tmp", text=True, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            self.assertEqual(applied.returncode, 0, applied.stderr)
            self.assertFalse((checkout / ".DS_Store").exists())
            self.assertFalse(cache.exists())
            self.assertEqual(protected.read_bytes(), b"raw")
            self.assertFalse(scratch.exists())
            self.assertTrue((completed / "outcome.json").is_file())
            self.assertTrue((active / "scratch/partial.root").is_file())

    def test_clean_refuses_symlink_escape_before_removing_anything(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            checkout = base / "checkout"
            outside = base / "outside"
            checkout.mkdir()
            outside.mkdir()
            sentinel = outside / "sentinel"
            sentinel.write_text("unique", encoding="utf-8")
            shutil.copy2(str(ROOT / "hadronization"), str(checkout / "hadronization"))
            (checkout / ".DS_Store").write_text("residue", encoding="utf-8")
            attempt = checkout / "data/work/evidence/MONASH/job000/attempt00"
            attempt.mkdir(parents=True)
            (attempt / "outcome.json").write_text(json.dumps({
                "state": "accepted", "finished_unix_seconds": 1,
                "cleanup_after_days": 1}), encoding="utf-8")
            (attempt / "scratch").symlink_to(outside, target_is_directory=True)
            result = subprocess.run(
                [str(checkout / "hadronization"), "clean", "--apply"],
                cwd="/tmp", text=True, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            self.assertEqual(result.returncode, 2)
            self.assertIn("resolves outside repository", result.stderr)
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "unique")
            self.assertTrue((checkout / ".DS_Store").exists())
            self.assertTrue((attempt / "scratch").is_symlink())

    def test_runtime_resolver_is_shared_verified_and_scrubbed_environment_safe(self):
        path = ROOT / "pipeline/generate/runtime.py"
        spec = importlib.util.spec_from_file_location("runtime_contract", str(path))
        runtime = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(runtime)
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = base / "root"
            pythia = base / "pythia"
            gcc = base / "gcc"
            for path in (root / "bin", root / "lib", pythia / "bin", pythia / "lib",
                         pythia / "include", pythia / "share/Pythia8/xmldoc",
                         gcc / "bin", gcc / "lib64"):
                path.mkdir(parents=True, exist_ok=True)
            root_config = root / "bin/root-config"
            root_config.write_text(
                "#!/bin/sh\ncase \"$1\" in --version) echo 6.30.01;; --libdir) echo \"$2ROOT/lib\";; --prefix) echo \"$2ROOT\";; esac\n"
                .replace("$2ROOT", str(root)), encoding="utf-8")
            root_command = root / "bin/root"
            root_command.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            pythia_config = pythia / "bin/pythia8-config"
            pythia_config.write_text(
                "#!/bin/sh\ncase \"$1\" in --version) echo 8.317;; --prefix) echo \"{}\";; esac\n".format(
                    pythia), encoding="utf-8")
            compiler = gcc / "bin/g++"
            compiler.write_text("#!/bin/sh\necho fake-g++\n", encoding="utf-8")
            for executable in (root_config, root_command, pythia_config, compiler):
                executable.chmod(0o755)
            (pythia / "lib/libpythia8.so").write_bytes(b"fixture")
            (pythia / "share/Pythia8/xmldoc/Index.xml").write_text("<index/>", encoding="utf-8")
            values = {
                "ROOT_PREFIX": str(root), "ROOT_VERSION": "6.30.01",
                "PYTHIA8_PREFIX": str(pythia), "PYTHIA8_VERSION": "8.317",
                "PYTHIA8_GCC_PREFIX": str(gcc), "CXX": str(compiler),
                "RAW_ROOT": str(base / "raw"), "WORK_ROOT": str(base / "work"),
            }
            resolved = runtime.resolve(values, {"PATH": "/usr/bin:/bin"},
                                       require_root=True, require_pythia=True)
            environment = resolved["environment"]
            self.assertEqual(environment["PYTHIA8DATA"],
                             str((pythia / "share/Pythia8/xmldoc").resolve()))
            self.assertTrue(environment["PATH"].startswith(str((gcc / "bin").resolve())))
            self.assertTrue(environment["LD_LIBRARY_PATH"].startswith(
                str((gcc / "lib64").resolve()) + os.pathsep
                + str((pythia / "lib").resolve())))
            (pythia / "share/Pythia8/xmldoc/Index.xml").unlink()
            with self.assertRaisesRegex(ValueError, "Index.xml"):
                runtime.resolve(values, {"PATH": "/usr/bin:/bin"},
                                require_root=True, require_pythia=True)


if __name__ == "__main__":
    unittest.main()
