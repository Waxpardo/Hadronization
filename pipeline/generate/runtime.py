#!/usr/bin/env python3
"""Resolve and verify the one interactive/build/worker runtime contract."""

import argparse
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "config/site.conf"


def site_values(path=SITE):
    values = {}
    if not path.is_file():
        return values
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        match = re.fullmatch(r"([A-Z][A-Z0-9_]*)=(.*)", line)
        if not match:
            raise ValueError("{}:{} is not KEY=VALUE".format(path, number))
        value = match.group(2).strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if match.group(1) in values:
            raise ValueError("{}:{} repeats {}".format(path, number, match.group(1)))
        values[match.group(1)] = value
    return values


def repository_path(value, default):
    path = Path(value) if value else default
    return path if path.is_absolute() else ROOT / path


def command_output(command, arguments):
    try:
        result = subprocess.run([command] + list(arguments), text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                timeout=15)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return result.stdout.strip().splitlines()[0] if result.returncode == 0 and result.stdout.strip() else None


def required_command_output(command, argument, environment, label):
    try:
        result = subprocess.run(
            [command, argument], text=True, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, env=environment, timeout=15)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise ValueError("{} cannot execute {}: {}".format(
            label, argument, error)) from error
    stdout = result.stdout.strip()
    stderr = result.stderr.strip()
    if result.returncode != 0:
        detail = stderr or stdout or "no diagnostic"
        raise ValueError("{} {} failed with status {}: {}".format(
            label, argument, result.returncode, detail))
    if stderr:
        raise ValueError("{} {} wrote a diagnostic to stderr: {}".format(
            label, argument, stderr))
    if not stdout:
        raise ValueError("{} {} returned empty output".format(label, argument))
    if "\0" in stdout:
        raise ValueError("{} {} returned malformed output".format(label, argument))
    return stdout


def config_flag_tokens(output, label):
    if "\n" in output or "\r" in output:
        raise ValueError("{} returned multiline flag output".format(label))
    try:
        tokens = shlex.split(output)
    except ValueError as error:
        raise ValueError("{} returned malformed flags: {}".format(label, error)) from error
    if not tokens:
        raise ValueError("{} returned empty flags".format(label))
    operand_options = {"-I", "-L", "-isystem", "-iquote", "-idirafter",
                       "-F", "-framework", "-Xlinker"}
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if any(ord(character) < 32 or ord(character) == 127 for character in token):
            raise ValueError("{} returned a malformed flag token".format(label))
        if token in operand_options:
            if index + 1 == len(tokens):
                raise ValueError("{} returned {} without an operand".format(label, token))
            operand = tokens[index + 1]
            if token != "-Xlinker" and operand.startswith("-"):
                raise ValueError("{} returned {} without a usable operand".format(
                    label, token))
            index += 2
            continue
        if not token.startswith("-") or token in {"-", "--"}:
            raise ValueError("{} returned a non-flag token: {}".format(label, token))
        index += 1
    return tokens


def flag_directories(tokens, options):
    directories = []
    for index, token in enumerate(tokens):
        for option in options:
            if token == option and index + 1 < len(tokens):
                directories.append(tokens[index + 1])
            elif token.startswith(option) and token != option:
                directories.append(token[len(option):])
    return directories


def require_flag_directory(tokens, options, expected, label):
    expected = expected.resolve()
    matches = []
    for value in flag_directories(tokens, options):
        path = Path(value)
        if path.is_absolute() and path.resolve() == expected:
            matches.append(value)
    if not matches:
        raise ValueError("{} does not name the declared directory {}".format(
            label, expected))


def pythia_header_version(header, expected):
    try:
        text = header.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise ValueError("PYTHIA header is unreadable: {}: {}".format(
            header, error)) from error
    dotted = re.findall(
        r"(?m)^\s*#\s*define\s+PYTHIA_VERSION\s+([0-9]+\.[0-9]+)\s*$", text)
    integer = re.findall(
        r"(?m)^\s*#\s*define\s+PYTHIA_VERSION_INTEGER\s+([0-9]+)\s*$", text)
    expected_integer = expected.replace(".", "")
    if dotted != [expected] or integer != [expected_integer]:
        raise ValueError(
            "PYTHIA header version mismatch: expected {} and {}, found {} and {}".format(
                expected, expected_integer, dotted, integer))


def existing_executable(value, fallback=None):
    candidate = value or fallback
    if not candidate:
        return None
    found = shutil.which(candidate)
    if found:
        return str(Path(found).resolve())
    path = Path(candidate)
    return str(path.resolve()) if path.is_file() and os.access(str(path), os.X_OK) else None


def prepend(current, values):
    result = []
    for value in list(values) + current.split(os.pathsep):
        if value and value not in result:
            result.append(value)
    return os.pathsep.join(result)


def resolve(values=None, base_environment=None, require_root=False,
            require_pythia=False, verify=True):
    values = dict(site_values() if values is None else values)
    base = dict(os.environ if base_environment is None else base_environment)
    environment = {}
    diagnostics = []
    raw_root = repository_path(values.get("RAW_ROOT"), ROOT / "data/raw").resolve()
    work_root = repository_path(values.get("WORK_ROOT"), ROOT / "data/work").resolve()
    environment["HADRONIZATION_RAW_ROOT"] = str(raw_root)
    environment["HADRONIZATION_WORK_ROOT"] = str(work_root)

    root_prefix = Path(values["ROOT_PREFIX"]).resolve() if values.get("ROOT_PREFIX") else None
    root_config = existing_executable(
        values.get("ROOT_CONFIG"),
        str(root_prefix / "bin/root-config") if root_prefix else shutil.which("root-config"))
    root_command = existing_executable(
        values.get("ROOT"),
        str(root_prefix / "bin/root") if root_prefix else shutil.which("root"))
    if root_config:
        reported = command_output(root_config, ["--version"])
        expected = values.get("ROOT_VERSION")
        if verify and expected and reported != expected:
            raise ValueError("ROOT version mismatch: expected {}, reported {}".format(expected, reported))
        root_lib = command_output(root_config, ["--libdir"])
        if root_prefix is None:
            prefix = command_output(root_config, ["--prefix"])
            root_prefix = Path(prefix).resolve() if prefix else Path(root_config).parents[1]
        environment.update({
            "ROOTSYS": str(root_prefix), "ROOT_CONFIG": root_config,
            "ROOT": root_command or str(root_prefix / "bin/root"),
        })
        diagnostics.append("ROOT={}".format(reported or "unreported"))
    elif require_root:
        raise ValueError("ROOT runtime requires ROOT_CONFIG/root-config")
    else:
        root_lib = None
        diagnostics.append("ROOT=unavailable")

    pythia_prefix = Path(values["PYTHIA8_PREFIX"]).resolve() if values.get("PYTHIA8_PREFIX") else None
    pythia_config = existing_executable(
        values.get("PYTHIA8_CONFIG"),
        str(pythia_prefix / "bin/pythia8-config") if pythia_prefix else shutil.which("pythia8-config"))
    pythia_cxxflags = []
    pythia_libs = []
    if pythia_config:
        expected = values.get("PYTHIA8_VERSION", "8.317")
        if not re.fullmatch(r"[0-9]+\.[0-9]+", expected):
            raise ValueError("PYTHIA expected version is malformed: {}".format(expected))
        label = "PYTHIA runtime configuration"
        reported = required_command_output(
            pythia_config, "--version", base, label)
        reported_prefix_text = required_command_output(
            pythia_config, "--prefix", base, label)
        if "\n" in reported or "\r" in reported or not re.fullmatch(
                r"[0-9]+\.[0-9]+", reported):
            raise ValueError("{} --version returned malformed output: {}".format(
                label, reported))
        reported_prefix = Path(reported_prefix_text)
        if ("\n" in reported_prefix_text or "\r" in reported_prefix_text or
                not reported_prefix.is_absolute()):
            raise ValueError("{} --prefix returned a non-absolute path: {}".format(
                label, reported_prefix_text))
        reported_prefix = reported_prefix.resolve()
        if pythia_prefix is None:
            pythia_prefix = reported_prefix
        elif reported_prefix != pythia_prefix:
            raise ValueError("{} prefix mismatch: declared {}, reported {}".format(
                label, pythia_prefix, reported_prefix))
        if verify and reported != expected:
            raise ValueError("PYTHIA version mismatch: expected {}, reported {}".format(
                expected, reported))
        cxxflags_output = required_command_output(
            pythia_config, "--cxxflags", base, label)
        libs_output = required_command_output(
            pythia_config, "--libs", base, label)
        pythia_cxxflags = config_flag_tokens(
            cxxflags_output, "PYTHIA runtime configuration --cxxflags")
        pythia_libs = config_flag_tokens(
            libs_output, "PYTHIA runtime configuration --libs")
        data = Path(values.get("PYTHIA8DATA", str(pythia_prefix / "share/Pythia8/xmldoc"))).resolve()
        header = pythia_prefix / "include/Pythia8/Pythia.h"
        libraries = [pythia_prefix / "lib/libpythia8.so",
                     pythia_prefix / "lib/libpythia8.dylib"]
        if verify and not header.is_file():
            raise ValueError("PYTHIA header is absent: {}".format(header))
        if verify:
            pythia_header_version(header, expected)
        if verify and not (data / "Index.xml").is_file():
            raise ValueError("PYTHIA8DATA has no Index.xml: {}".format(data))
        if verify and not any(path.is_file() for path in libraries):
            raise ValueError("PYTHIA shared library is absent under {}".format(pythia_prefix / "lib"))
        if verify:
            require_flag_directory(
                pythia_cxxflags, ("-isystem", "-I"),
                pythia_prefix / "include", "PYTHIA --cxxflags")
            require_flag_directory(
                pythia_libs, ("-L",), pythia_prefix / "lib", "PYTHIA --libs")
            if "-lpythia8" not in pythia_libs:
                raise ValueError("PYTHIA --libs does not contain -lpythia8")
        environment.update({
            "PYTHIA8": str(pythia_prefix), "PYTHIA8_PREFIX": str(pythia_prefix),
            "PYTHIA8_CONFIG": pythia_config, "PYTHIA8DATA": str(data),
            "PYTHIA8_VERSION": expected,
        })
        diagnostics.append("PYTHIA={}".format(reported or "unreported"))
    elif require_pythia:
        raise ValueError("generation runtime requires PYTHIA8_CONFIG or PYTHIA8_PREFIX")
    else:
        diagnostics.append("PYTHIA=unavailable")

    cxx = existing_executable(values.get("CXX"), shutil.which("c++") or shutil.which("g++"))
    python = existing_executable(values.get("PYTHON"), sys.executable)
    if not cxx:
        raise ValueError("runtime requires a C++ compiler")
    if not python:
        raise ValueError("runtime requires Python")
    environment.update({"CXX": cxx, "PYTHON": python})

    path_prefixes = []
    library_prefixes = []
    include_prefixes = []
    pythia_gcc = Path(values["PYTHIA8_GCC_PREFIX"]).resolve() if values.get("PYTHIA8_GCC_PREFIX") else None
    root_gcc = Path(values["ROOT_GCC_PREFIX"]).resolve() if values.get("ROOT_GCC_PREFIX") else None
    if root_prefix:
        path_prefixes.append(str(root_prefix / "bin"))
        if root_lib:
            library_prefixes.append(root_lib)
    if root_gcc:
        path_prefixes.append(str(root_gcc / "bin"))
        library_prefixes.append(str(root_gcc / "lib64"))
    runtime_dirs = [item for item in values.get("ROOT_RUNTIME_LIB_DIRS", "").split(os.pathsep) if item]
    library_prefixes.extend(runtime_dirs)
    if pythia_prefix:
        path_prefixes.append(str(pythia_prefix / "bin"))
        library_prefixes.insert(0, str(pythia_prefix / "lib"))
        include_prefixes.append(str(pythia_prefix / "include"))
    if pythia_gcc:
        path_prefixes.append(str(pythia_gcc / "bin"))
        library_prefixes.insert(0, str(pythia_gcc / "lib64"))
    for label, paths in (("runtime PATH", path_prefixes),
                         ("runtime library", library_prefixes)):
        if verify:
            missing = [path for path in paths if not Path(path).is_dir()]
            if missing:
                raise ValueError("{} directory missing: {}".format(label, missing[0]))
    environment["PATH"] = prepend(base.get("PATH", ""), reversed(path_prefixes))
    if library_prefixes:
        environment["LD_LIBRARY_PATH"] = prepend(
            base.get("LD_LIBRARY_PATH", ""), library_prefixes)
    if include_prefixes:
        environment["ROOT_INCLUDE_PATH"] = prepend(
            base.get("ROOT_INCLUDE_PATH", ""), include_prefixes)
    if root_lib:
        environment["ROOT_DYN_PATH"] = prepend(base.get("ROOT_DYN_PATH", ""), [root_lib])
    diagnostics.append("CXX={}".format(command_output(cxx, ["--version"]) or cxx))
    return {"environment": environment, "diagnostics": diagnostics,
            "site_configured": bool(values),
            "pythia_cxxflags": pythia_cxxflags, "pythia_libs": pythia_libs}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("shell", "json", "check"))
    parser.add_argument("--require-root", action="store_true")
    parser.add_argument("--require-pythia", action="store_true")
    args = parser.parse_args()
    try:
        result = resolve(require_root=args.require_root,
                         require_pythia=args.require_pythia)
        if args.command == "shell":
            for key, value in sorted(result["environment"].items()):
                print("export {}={}".format(key, shlex.quote(value)))
        elif args.command == "json":
            print(json.dumps(result, sort_keys=True))
        else:
            print("RUNTIME_OK {}".format(" ".join(result["diagnostics"])))
        return 0
    except (OSError, ValueError) as error:
        print("ERROR: {}".format(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
