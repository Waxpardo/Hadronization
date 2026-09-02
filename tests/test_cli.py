import os
import importlib.util
import json
from pathlib import Path
import shlex
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
        for command in ("analyze", "merge", "reduce", "plot"):
            result = self.run_cli(command)
            self.assertEqual(result.returncode, 3)
            self.assertEqual(
                result.stderr.strip(),
                "ERROR: {} direct stage is not yet implemented".format(command))
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
            for path in (root / "bin", root / "lib", root / "include",
                         pythia / "bin", pythia / "lib",
                         pythia / "include/Pythia8", pythia / "share/Pythia8/xmldoc",
                         gcc / "bin", gcc / "lib64"):
                path.mkdir(parents=True, exist_ok=True)
            root_config = root / "bin/root-config"
            root_config.write_text(
                "#!/bin/sh\ncase \"$1\" in --version) echo 6.30.01;; "
                "--libdir) echo \"$2ROOT/lib\";; --prefix) echo \"$2ROOT\";; "
                "--cflags) echo \"-I$2ROOT/include\";; "
                "--libs) echo \"-L$2ROOT/lib -lROOTDataFrame\";; "
                "--auxlibs) echo -ldl;; esac\n"
                .replace("$2ROOT", str(root)), encoding="utf-8")
            root_command = root / "bin/root"
            root_command.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            pythia_config = pythia / "bin/pythia8-config"

            valid_cxxflags = "-O2 -std=c++11 -I{}".format(pythia / "include")
            valid_libs = "-L{} -Wl,-rpath,{} -lpythia8 -ldl".format(
                pythia / "lib", pythia / "lib")

            def write_pythia_config(version="8.317", prefix=None,
                                     cxxflags=None, libraries=None,
                                     stderr_option=None):
                outputs = {
                    "--version": version,
                    "--prefix": str(pythia if prefix is None else prefix),
                    "--cxxflags": valid_cxxflags if cxxflags is None else cxxflags,
                    "--libs": valid_libs if libraries is None else libraries,
                }
                lines = ["#!/bin/sh", "case \"$1\" in"]
                for option in ("--version", "--prefix", "--cxxflags", "--libs"):
                    line = "{}) printf '%s\\n' {}".format(
                        option, shlex.quote(outputs[option]))
                    if stderr_option == option:
                        line += "; printf '%s\\n' diagnostic >&2"
                    lines.append(line + ";;")
                lines.extend(["*) exit 2;;", "esac", ""])
                pythia_config.write_text("\n".join(lines), encoding="utf-8")
                pythia_config.chmod(0o755)

            write_pythia_config()
            compiler = gcc / "bin/g++"
            compiler.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            for executable in (root_config, root_command, pythia_config, compiler):
                executable.chmod(0o755)
            (pythia / "lib/libpythia8.so").write_bytes(b"fixture")
            (pythia / "share/Pythia8/xmldoc/Index.xml").write_text("<index/>", encoding="utf-8")
            header = pythia / "include/Pythia8/Pythia.h"

            def write_header(version="8.317", integer="8317"):
                header.write_text(
                    "#define PYTHIA_VERSION {}\n"
                    "#define PYTHIA_VERSION_INTEGER {}\n".format(version, integer),
                    encoding="utf-8")

            write_header()
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
            self.assertEqual(resolved["pythia_cxxflags"],
                             shlex.split(valid_cxxflags))
            self.assertEqual(resolved["pythia_libs"], shlex.split(valid_libs))

            portable_values = dict(values)
            portable_values.pop("PYTHIA8_PREFIX")
            portable_values["PYTHIA8_CONFIG"] = str(pythia_config)
            portable = runtime.resolve(
                portable_values, {"PATH": "/usr/bin:/bin"},
                require_root=True, require_pythia=True)
            self.assertEqual(portable["environment"]["PYTHIA8_PREFIX"],
                             str(pythia.resolve()))

            # Flag consumption must use the resolver's validated snapshot. A
            # later broken config query cannot inject diagnostic words into g++.
            write_pythia_config(cxxflags="Error: broken configuration",
                                 libraries="Error: broken configuration")
            submit_path = ROOT / "pipeline/generate/submit.py"
            submit_spec = importlib.util.spec_from_file_location(
                "submit_runtime_contract", str(submit_path))
            submit = importlib.util.module_from_spec(submit_spec)
            submit_spec.loader.exec_module(submit)
            compile_command = submit.compile_producer(resolved, base / "producer")
            self.assertFalse(any("Error:" in token or "configuration" in token
                                 for token in compile_command))
            self.assertIn("-I" + str(pythia / "include"), compile_command)

            def rejected(pattern, **configuration):
                write_pythia_config(**configuration)
                with self.assertRaisesRegex(ValueError, pattern):
                    runtime.resolve(values, {"PATH": "/usr/bin:/bin"},
                                    require_root=True, require_pythia=True)

            rejected("prefix", prefix="Error: cannot find valid configuration")
            rejected("non-flag token", cxxflags="Error: broken configuration")
            rejected("diagnostic to stderr", stderr_option="--cxxflags")
            rejected("prefix mismatch", prefix=base / "wrong-prefix")
            rejected("version mismatch", version="8.316")
            rejected("empty output", cxxflags="")
            rejected("malformed flags", cxxflags="'-Iunterminated")
            rejected("declared directory", cxxflags="-O2 -std=c++11")
            rejected("declared directory", cxxflags="-I" + str(base / "wrong/include"))
            rejected("empty output", libraries="")
            rejected("declared directory", libraries="-lpythia8 -ldl")
            rejected("declared directory", libraries="-L" + str(base / "wrong/lib") +
                     " -lpythia8")
            rejected("-lpythia8", libraries="-L{} -ldl".format(pythia / "lib"))

            write_pythia_config()
            header.unlink()
            with self.assertRaisesRegex(ValueError, "header is absent"):
                runtime.resolve(values, {"PATH": "/usr/bin:/bin"},
                                require_root=True, require_pythia=True)
            write_header(version="8.316", integer="8316")
            with self.assertRaisesRegex(ValueError, "header version mismatch"):
                runtime.resolve(values, {"PATH": "/usr/bin:/bin"},
                                require_root=True, require_pythia=True)
            write_header()

            index = pythia / "share/Pythia8/xmldoc/Index.xml"
            index.unlink()
            with self.assertRaisesRegex(ValueError, "Index.xml"):
                runtime.resolve(values, {"PATH": "/usr/bin:/bin"},
                                require_root=True, require_pythia=True)
            index.write_text("<index/>", encoding="utf-8")
            library = pythia / "lib/libpythia8.so"
            library.unlink()
            with self.assertRaisesRegex(ValueError, "shared library"):
                runtime.resolve(values, {"PATH": "/usr/bin:/bin"},
                                require_root=True, require_pythia=True)

            arrow = ("/cvmfs/alice.cern.ch/el9-x86_64/Packages/arrow/"
                     "v14.0.1-alice1-19/lib")
            site = runtime.site_values(ROOT / "config/site.example.conf")
            self.assertIn(arrow, site["ROOT_RUNTIME_LIB_DIRS"].split(os.pathsep))


if __name__ == "__main__":
    unittest.main()
