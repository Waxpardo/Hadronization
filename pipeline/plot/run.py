#!/usr/bin/env python3
"""Verify one compact ROOT and query or export deterministic numerical projections."""

import argparse
import csv
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
ANALYSIS = ROOT / "config/analysis.json"
PLOT_CONFIG = ROOT / "config/plot.json"
EXPORT_SCHEMA = "hadronization_numerical_plot_export_v1"
REQUEST_SCHEMA = "hadronization_plot_request_v1"
DEFAULT_FAMILIES = ("balancing", "correlations", "kinematics",
                    "multiplicity", "sample_counts")
QUERY_FAMILIES = DEFAULT_FAMILIES + (
    "origin", "closure_species", "closure_full_visible",
    "closure_category_dphi")
CSV_FIELDS = (
    "semantic_id", "request_id", "compact_root_sha256",
    "compact_scientific_content_digest", "family", "role_id", "quantity",
    "tune", "reference_tune", "profile", "activity_id", "class_id",
    "percentile_low", "percentile_high", "nch_low", "nch_high",
    "trigger_pdg", "associate_pdg", "reference_pdg", "eligibility_status",
    "component", "axis", "bin_index", "bin_low", "bin_high", "value",
    "value_status", "finite_mc_error", "uncertainty_status", "variance",
    "source_tune_leave_mean", "reference_tune_leave_mean",
    "source_tune_complements", "reference_tune_complements", "reasons",
    "diagnostic", "estimator")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True)


def sha_bytes(value):
    return hashlib.sha256(value).hexdigest()


def sha_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def exact_keys(value, expected, label):
    if not isinstance(value, dict) or set(value) != set(expected):
        raise ValueError("{} field set differs".format(label))


def regular_file(path, label):
    if path.is_symlink() or not path.is_file():
        raise ValueError("{} is not a regular file: {}".format(label, path))


def json_file(path, label="JSON input"):
    regular_file(path, label)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise ValueError("invalid JSON {}: {}".format(path, error)) from error


def load_module(name, path):
    specification = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def reduce_module():
    return load_module("hadronization_plot_reduce_contract",
                       ROOT / "pipeline/reduce/run.py")


def runtime_module():
    return load_module("hadronization_plot_runtime_contract",
                       ROOT / "pipeline/generate/runtime.py")


def reject_symlink_components(path, label):
    absolute = path.absolute()
    current = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        current /= part
        if os.path.lexists(str(current)) and current.is_symlink():
            raise ValueError("{} has a symlink component: {}".format(label, current))


def fsync_file(path):
    descriptor = os.open(str(path), os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def fsync_directory(path):
    descriptor = os.open(str(path), os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def atomic_json(path, value):
    payload = (canonical(value) + "\n").encode("ascii")
    with tempfile.NamedTemporaryFile(prefix="." + path.name + ".",
                                     dir=str(path.parent), delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    try:
        os.link(str(temporary), str(path))
        fsync_directory(path.parent)
    finally:
        if temporary.exists():
            temporary.unlink()


def checked_plot_config(path):
    reject_symlink_components(path, "plot presentation config")
    path = path.resolve()
    payload = json_file(path, "plot presentation config")
    exact_keys(payload, {"schema", "version", "families", "presets", "layout",
                         "style_identities"}, "plot presentation config")
    if (payload["schema"] != "hadronization_plot_presentation_v1" or
            payload["version"] != "1.0.0"):
        raise ValueError("plot presentation schema/version differs")
    families = payload["families"]
    required = {"D", "B", "LambdaC", "LambdaB", "Ds", "Bs", "Bc",
                "Sigma", "Xi", "XiPrime", "Omega"}
    if (not isinstance(families, dict) or set(families) != required or
            any(not isinstance(name, str) or not name for name in families)):
        raise ValueError("plot family registry differs")
    seen = set()
    for name, pdgs in families.items():
        if (not isinstance(pdgs, list) or not pdgs or
                any(type(pdg) is not int or pdg == 0 for pdg in pdgs) or
                len(pdgs) != len(set(pdgs)) or
                any(-pdg not in pdgs for pdg in pdgs)):
            raise ValueError("plot family {} is not charge-complete".format(name))
        overlap = seen.intersection(pdgs)
        if overlap:
            raise ValueError("plot family registry duplicates signed PDGs: {}".format(
                sorted(overlap)))
        seen.update(pdgs)
    presets = payload["presets"]
    exact_keys(presets, {"paper_default", "all_central", "all_registered"},
               "plot presets")
    if presets["paper_default"] != {
            "families": ["D", "LambdaC", "B", "LambdaB"]}:
        raise ValueError("paper_default family selection differs")
    if (presets["all_central"] != {"selector": "all_central"} or
            presets["all_registered"] != {"selector": "all_registered"}):
        raise ValueError("complete plot presets differ")
    layout = payload["layout"]
    exact_keys(layout, {"axis_padding_fraction", "facet_dimension",
                        "grid_columns_maximum", "maximum_panels_per_page",
                        "shared_legend_reservation", "text_pixel_size"},
               "plot layout")
    if (type(layout["maximum_panels_per_page"]) is not int or
            layout["maximum_panels_per_page"] < 1 or
            type(layout["grid_columns_maximum"]) is not int or
            layout["grid_columns_maximum"] < 1 or
            layout["facet_dimension"] != "associate_family" or
            layout["shared_legend_reservation"] != "page_top" or
            type(layout["axis_padding_fraction"]) not in (int, float) or
            not 0.0 <= layout["axis_padding_fraction"] <= 1.0 or
            type(layout["text_pixel_size"]) is not int or
            layout["text_pixel_size"] < 1):
        raise ValueError("plot layout contract differs")
    styles = payload["style_identities"]
    exact_keys(styles, {"class_line_style_rule", "species_encoding", "tunes",
                        "unity_reference"}, "plot style identities")
    expected_tunes = [
        {"id": "MONASH", "color": "#000000", "marker": "filled_circle",
         "line": "solid"},
        {"id": "JUNCTIONS", "color": "#0072B2", "marker": "filled_square",
         "line": "solid"},
        {"id": "CLOSEPACKING", "color": "#D55E00",
         "marker": "filled_up_triangle", "line": "solid"},
    ]
    if (styles["tunes"] != expected_tunes or
            styles["species_encoding"] != "facet_only" or
            styles["class_line_style_rule"] !=
            "root_line_style=1+class_id" or
            styles["unity_reference"] != {
                "color": "neutral_gray", "line": "dashed",
                "role": "reference_only"}):
        raise ValueError("plot style identity differs")
    return payload, sha_file(path)


def checked_plot_request(path):
    payload = json_file(path, "plot request")
    exact_keys(payload, {"schema", "preset", "include", "exclude"},
               "plot request")
    if payload["schema"] != REQUEST_SCHEMA:
        raise ValueError("plot request schema differs")
    for name in ("include", "exclude"):
        if (not isinstance(payload[name], list) or
                any(not isinstance(value, str) or not value
                    for value in payload[name])):
            raise ValueError("plot request {} differs".format(name))
    if not isinstance(payload["preset"], str):
        raise ValueError("plot request preset differs")
    return payload


def resolve_selection(config, domains, preset, includes, excludes):
    if preset not in config["presets"]:
        raise ValueError("unknown plot preset: {}".format(preset))
    for label, tokens in (("include", includes), ("exclude", excludes)):
        unknown = sorted(set(tokens) - set(config["families"]))
        if unknown:
            raise ValueError("unknown {} family token(s): {}".format(label, unknown))
        if len(tokens) != len(set(tokens)):
            raise ValueError("duplicate {} family token".format(label))
    conflict = sorted(set(includes).intersection(excludes))
    if conflict:
        raise ValueError("contradictory include/exclude token(s): {}".format(conflict))
    pairs = domains["pair_query_dictionary"]
    pair_pdgs = {item["associate_pdg"] for item in pairs}
    configured_pdgs = {pdg for values in config["families"].values()
                       for pdg in values}
    if configured_pdgs != pair_pdgs:
        raise ValueError("plot families do not exactly partition compact associates")
    by_pdg = {}
    for item in pairs:
        previous = by_pdg.setdefault(item["associate_pdg"],
                                     item["central_eligible"])
        if previous is not item["central_eligible"]:
            raise ValueError("compact associate eligibility is inconsistent")
    definition = config["presets"][preset]
    eligibility = "all_registered" if preset == "all_registered" else "central"
    if "families" in definition:
        selected_families = list(definition["families"])
    else:
        selected_families = list(config["families"])
    for token in includes:
        if token in selected_families:
            raise ValueError("include token is already selected: {}".format(token))
        selected_families.append(token)
    for token in excludes:
        if token not in selected_families:
            raise ValueError("exclude token is not selected: {}".format(token))
        selected_families.remove(token)
    if not selected_families:
        raise ValueError("plot request selects no presentation family")
    selected_pdgs = []
    for token in selected_families:
        for pdg in config["families"][token]:
            if eligibility == "all_registered" or by_pdg[pdg]:
                selected_pdgs.append(pdg)
    if any(-pdg not in selected_pdgs for pdg in selected_pdgs):
        raise ValueError("resolved selection is not charge-conjugate complete")
    selected_pair_ids = [item["id"] for item in pairs
                         if item["associate_pdg"] in set(selected_pdgs)]
    noncentral = sorted(pdg for pdg in selected_pdgs if not by_pdg[pdg])
    expected_noncentral = sorted(pdg for pdg, central in by_pdg.items() if not central)
    if eligibility == "all_registered" and noncentral != expected_noncentral:
        raise ValueError("all_registered does not expose the exact noncentral set")
    if eligibility == "central" and noncentral:
        raise ValueError("central selection contains noncentral states")
    result = {
        "schema": "hadronization_resolved_plot_selection_v1",
        "preset": preset,
        "include": list(includes),
        "exclude": list(excludes),
        "eligibility": eligibility,
        "eligibility_status": ("ALL_REGISTERED_WITH_NONCENTRAL_DIAGNOSTICS"
                               if eligibility == "all_registered" else
                               "CENTRAL_ONLY"),
        "family_tokens": selected_families,
        "signed_pdgs": selected_pdgs,
        "pair_ids": selected_pair_ids,
        "noncentral_signed_pdgs": noncentral,
    }
    result["selection_id"] = sha_bytes(canonical(result).encode("ascii"))
    return result


def command_tokens(command, argument, environment):
    completed = subprocess.run([command, argument], env=environment, text=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if completed.returncode or completed.stderr.strip():
        raise ValueError("ROOT configuration failed: {}".format(
            completed.stderr.strip() or completed.stdout.strip()))
    return shlex.split(completed.stdout.strip())


def build_engine(work_root):
    runtime = runtime_module().resolve(require_root=True)
    environment = os.environ.copy()
    environment.update(runtime["environment"])
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    source = ROOT / "pipeline/plot/plot.cpp"
    header = ROOT / "pipeline/plot/projection.hpp"
    statistics = ROOT / "pipeline/reduce/statistics.hpp"
    identity = {
        "schema": "hadronization_plot_engine_build_v1",
        "source_sha256": sha_file(source),
        "projection_sha256": sha_file(header),
        "statistics_sha256": sha_file(statistics),
        "compiler": runtime["environment"]["CXX"],
        "root": next(value.split("=", 1)[1] for value in runtime["diagnostics"]
                     if value.startswith("ROOT=")),
        "flags": ["-std=c++17", "-O2", "-Wall", "-Wextra", "-Wpedantic",
                  "-Werror"],
    }
    build_id = sha_bytes(canonical(identity).encode("ascii"))
    work_root = work_root.resolve(strict=False)
    reject_symlink_components(work_root, "plot work root")
    binary_root = work_root / "bin"
    binary_root.mkdir(parents=True, exist_ok=True)
    binary = binary_root / ("plot-" + build_id[:20])
    receipt = binary.with_suffix(".build.json")
    if binary.is_file() and receipt.is_file():
        current = json_file(receipt, "plot build receipt")
        if (current.get("build_identity") == identity and
                current.get("binary_sha256") == sha_file(binary)):
            return environment, binary, current
        binary.unlink()
        receipt.unlink()
    flags = command_tokens(environment["ROOT_CONFIG"], "--cflags", environment)
    libraries = command_tokens(environment["ROOT_CONFIG"], "--libs", environment)
    temporary = binary.with_name("." + binary.name + ".tmp")
    command = [environment["CXX"]] + identity["flags"] + [
        "-I" + str(ROOT / "pipeline/plot"),
        "-I" + str(ROOT / "pipeline/reduce"), str(source)] + flags + libraries + [
        "-o", str(temporary)]
    completed = subprocess.run(command, env=environment, text=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if completed.returncode or completed.stdout.strip() or completed.stderr.strip():
        if temporary.exists():
            temporary.unlink()
        raise ValueError("plot-engine warning-free build failed: {}".format(
            completed.stderr.strip() or completed.stdout.strip()))
    os.chmod(str(temporary), 0o700)
    os.replace(str(temporary), str(binary))
    fsync_file(binary)
    build_receipt = {
        "schema": "hadronization_plot_engine_build_receipt_v1",
        "build_id": build_id,
        "build_identity": identity,
        "binary_sha256": sha_file(binary),
    }
    payload = (canonical(build_receipt) + "\n").encode("ascii")
    with tempfile.NamedTemporaryFile(prefix="." + receipt.name + ".",
                                     dir=str(receipt.parent), delete=False) as handle:
        temporary_receipt = Path(handle.name)
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(str(temporary_receipt), str(receipt))
    fsync_directory(receipt.parent)
    return environment, binary, build_receipt


def number(value):
    return float(value).hex()


def write_engine_request(path, receipt, families):
    domains = receipt["scientific_identity"]["compact_domains"]
    lines = ["hadronization_plot_engine_request_v1"]
    lines.extend("FAMILY\t{}".format(value) for value in families)
    lines.extend("BLOCK\t{}".format(value) for value in domains["block_ids"])
    lines.extend("TUNE\t{}".format(value) for value in domains["tune_dictionary"])
    lines.extend("PROFILE\t{}".format(value["id"]) for value in domains["profiles"])
    lines.extend("ACTIVITY\t{}".format(value["id"])
                 for value in domains["activities"])
    for scope in domains["scope_dictionary"]:
        lines.append("SCOPE\t{id}\t{family}\t{tune}\t{profile}\t{activity}\t{class_id}".format(
            **{**scope,
               "profile": scope["profile"] if scope["profile"] is not None else "-",
               "activity": scope["activity"] if scope["activity"] is not None else "-",
               "class_id": scope["class_id"] if scope["class_id"] is not None else -1}))
    for pair in domains["pair_query_dictionary"]:
        lines.append("PAIR\t{id}\t{trigger_pdg}\t{associate_pdg}\t{sign}\t"
                     "{reference_meson_pdg}\t{central_eligible}\t{sector}".format(
                         **{**pair, "central_eligible":
                            int(pair["central_eligible"])}))
    for trigger in domains["trigger_dictionary"]:
        lines.append("TRIGGER\t{id}\t{signed_pdg}".format(**trigger))
    for correlation in domains["correlation_dictionary"]:
        lines.append("CORRELATION\t{id}\t{trigger_pdg}\t{associate_pdg}".format(
            **correlation))
    for species in domains["g9_species_dictionary"]:
        lines.append("G9\t{id}\t{signed_pdg}".format(**species))
    for index, pdg in enumerate(domains["dynamic_species"]["closure_species_pdgs"]):
        lines.append("CLOSURE_SPECIES\t{}\t{}".format(index, pdg))
    for index, pdg in enumerate(domains["dynamic_species"]["t1_all_final_pdgs"]):
        lines.append("T1_SPECIES\t{}\t{}".format(index, pdg))
    for origin in domains["origin_dictionary"]:
        lines.append("ORIGIN\t{id}\t{label}".format(**origin))
    for category in domains["closure_category_dictionary"]:
        lines.append("CLOSURE_CATEGORY\t{id}\t{label}".format(**category))
    for klass in domains["class_dictionary"]:
        lines.append("CLASS\t{}\t{}\t{}\t{}".format(
            klass["id"], int(klass["integrated"]),
            klass["percentile_interval"][0], klass["percentile_interval"][1]))
    embedded_receipts = receipt.get("_embedded_activity_receipts")
    if embedded_receipts is None:
        embedded_receipts = receipt["scientific_identity"].get("activity_receipts")
    if embedded_receipts is None:
        raise ValueError("verified receipt lacks activity boundary receipts")
    for activity in embedded_receipts:
        for class_id, boundary in enumerate(activity["classes"]):
            lines.append("BOUNDARY\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}".format(
                activity["tune"], activity["activity_id"], class_id,
                boundary["low"], boundary["high"], int(boundary["stable"]),
                int(boundary["resolved"]), int(boundary["empty"])))
    axes = domains["axes"]
    for name in ("dphi", "eta", "phi"):
        axis = axes[name]
        lines.append("AXIS\t{}\t{}\t{}\t{}".format(
            name, axis["bins"], number(axis["low"]), number(axis["high"])))
    lines.extend("PTEDGE\t{}".format(number(value))
                 for value in axes["pt"]["edges"])
    lines.append("ACTIVITY_BINS\t{}".format(axes["activity"]["bins"]))
    lines.append("EVENTS\t{}".format(receipt["scientific_identity"]["events"]))
    lines.append("END")
    path.write_text("\n".join(lines) + "\n", encoding="ascii")


def admit(root_path, receipt_path, analysis_path, work_root):
    for path, label in ((root_path, "compact ROOT"),
                        (receipt_path, "compact receipt"),
                        (analysis_path, "analysis request")):
        reject_symlink_components(path, label)
    reducer = reduce_module()
    receipt, summary = reducer.verify_output(root_path, receipt_path,
                                             analysis_path, work_root / "reduce")
    if receipt["state"] != "PUBLICATION_ELIGIBLE":
        raise ValueError("plot export requires PUBLICATION_ELIGIBLE compact input")
    # The embedded activity receipt is read back by the reducer verifier and is
    # digest-bound to the external scientific identity. Keep it transient only.
    environment, binary, unused = reducer.build_reducer(work_root / "reduce")
    completed = reducer.run_binary(binary, environment, ["verify", str(root_path)],
                                   "compact activity-receipt readback")
    del completed, unused
    oracle = _read_embedded_payload(root_path, work_root)
    if oracle["activity_receipts"] != summary.get("activity_receipts",
                                                   oracle["activity_receipts"]):
        raise ValueError("compact activity receipt readback differs")
    receipt["_embedded_activity_receipts"] = oracle["activity_receipts"]
    receipt["_embedded_block_accounting"] = oracle["block_accounting"]
    return receipt, summary


def _read_embedded_payload(root_path, work_root):
    environment, binary, unused_build = build_engine(work_root)
    del unused_build
    output = work_root / "embedded-receipt.json"
    completed = subprocess.run([str(binary), "embedded", str(root_path), str(output)],
                               env=environment, text=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if completed.returncode or not output.is_file():
        raise ValueError("compact embedded receipt readback failed: {}".format(
            completed.stderr.strip() or completed.stdout.strip()))
    payload = json_file(output, "embedded compact receipt")
    output.unlink()
    return payload


def engine_rows(root_path, receipt, families, work_root):
    environment, binary, build = build_engine(work_root)
    with tempfile.TemporaryDirectory(prefix="plot-engine-",
                                     dir=str(work_root)) as directory:
        temporary = Path(directory)
        request = temporary / "request.tsv"
        output = temporary / "output.tsv"
        write_engine_request(request, receipt, families)
        completed = subprocess.run([str(binary), str(root_path), str(request),
                                    str(output)], env=environment, text=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if completed.returncode or completed.stdout.strip() or completed.stderr.strip():
            raise ValueError("plot engine failed: {}".format(
                completed.stderr.strip() or completed.stdout.strip()))
        lines = output.read_text(encoding="ascii").splitlines()
    if not lines or lines[0] != "hadronization_plot_engine_output_v1" or \
            lines[-1] != "END":
        raise ValueError("plot engine output framing differs")
    roles = []
    rows = []
    for line in lines[1:-1]:
        fields = line.split("\t")
        if fields[0] == "R":
            if len(fields) != 4:
                raise ValueError("plot role record differs")
            roles.append({"id": fields[1], "family": fields[2],
                          "selector": fields[3]})
            continue
        if fields[0] != "D" or len(fields) != 34:
            raise ValueError("plot numerical row differs")
        values = fields[1:]
        names = ("family", "semantic_id", "role_id", "quantity", "tune",
                 "reference_tune", "profile", "activity_id", "class_id",
                 "percentile_low", "percentile_high", "nch_low", "nch_high",
                 "trigger_pdg", "associate_pdg", "reference_pdg", "component",
                 "axis", "bin_index", "bin_low", "bin_high", "value",
                 "value_status", "finite_mc_error", "uncertainty_status",
                 "variance", "source_tune_leave_mean",
                 "reference_tune_leave_mean", "source_tune_complements",
                 "reference_tune_complements", "reasons", "diagnostic", "estimator")
        row = dict(zip(names, values))
        rows.append(row)
    if len({role["id"] for role in roles}) != len(roles):
        raise ValueError("plot role IDs collide")
    if len({row["semantic_id"] for row in rows}) != len(rows):
        raise ValueError("plot semantic IDs collide")
    return roles, rows, build


def float_text(token):
    if token == "-":
        return ""
    value = float.fromhex(token)
    if not math.isfinite(value):
        raise ValueError("plot engine emitted a nonfinite value")
    if value == 0.0:
        value = 0.0
    return format(value, ".17g")


def complement_text(token):
    if token == "-":
        return ""
    return ";".join(float_text(value) if value != "-" else ""
                    for value in token.split(";"))


def public_row(row, request_id, root_sha, scientific_digest, eligibility):
    converted = dict(row)
    for name in ("bin_low", "bin_high", "value", "finite_mc_error", "variance",
                 "source_tune_leave_mean", "reference_tune_leave_mean"):
        converted[name] = float_text(converted[name])
    for name in ("source_tune_complements", "reference_tune_complements"):
        converted[name] = complement_text(converted[name])
    for name in ("role_id", "reference_tune", "profile", "activity_id",
                 "component", "axis", "reasons", "diagnostic"):
        if converted[name] == "-":
            converted[name] = ""
    for name in ("class_id", "percentile_low", "percentile_high", "nch_low",
                 "nch_high", "bin_index"):
        if converted[name] == "-1":
            converted[name] = ""
    for name in ("trigger_pdg", "associate_pdg", "reference_pdg"):
        if converted[name] == "0":
            converted[name] = ""
    converted.update({
        "request_id": request_id,
        "compact_root_sha256": root_sha,
        "compact_scientific_content_digest": scientific_digest,
        "eligibility_status": eligibility,
    })
    return {field: converted.get(field, "") for field in CSV_FIELDS}


def filter_rows(rows, selection, arguments=None):
    selected_pdgs = set(selection["signed_pdgs"])
    filtered = []
    for row in rows:
        associate = int(row["associate_pdg"])
        if row["family"] in {"balancing", "correlations"} and associate != 0:
            if associate not in selected_pdgs:
                continue
        if arguments is not None:
            if arguments.tune and row["tune"] != arguments.tune:
                continue
            if arguments.profile and row["profile"] != arguments.profile:
                continue
            if arguments.activity and row["activity_id"] != arguments.activity:
                continue
            if arguments.class_id is not None and \
                    int(row["class_id"]) != arguments.class_id:
                continue
            if arguments.bin is not None and int(row["bin_index"]) != arguments.bin:
                continue
            if arguments.pair:
                trigger, associate_query = map(int, arguments.pair.split(":"))
                if (int(row["trigger_pdg"]) != trigger or
                        int(row["associate_pdg"]) != associate_query):
                    continue
        filtered.append(row)
    return filtered


def compact_scale(receipt):
    domains = receipt["scientific_identity"]["compact_domains"]
    accounting = receipt["_embedded_block_accounting"]
    blocks = accounting["blocks"]
    tune_names = domains["tune_dictionary"]
    per_tune = []
    for tune_id, tune in enumerate(tune_names):
        selected = [item for item in blocks if item["tune"] == tune_id]
        per_tune.append({
            "tune": tune,
            "successful_events": sum(item["successful_events"]
                                     for item in selected),
            "sources": sum(item["sources"] for item in selected),
            "blocks": [{"block": item["block"],
                        "successful_events": item["successful_events"],
                        "sources": item["sources"]} for item in selected],
        })
    return {
        "successful_events_total": receipt["scientific_identity"]["events"],
        "sources_total": receipt["scientific_identity"]["sources"],
        "tunes": per_tune,
        "block_ids": domains["block_ids"],
        "class_count": len(domains["class_dictionary"]),
        "class_dictionary": domains["class_dictionary"],
        "pair_count": len(domains["pair_query_dictionary"]),
        "g9_species_count": len(domains["g9_species_dictionary"]),
    }


def layout_primitives(config, selection, rows):
    layout = config["layout"]
    tokens = selection["family_tokens"]
    maximum = layout["maximum_panels_per_page"]
    columns_maximum = layout["grid_columns_maximum"]
    by_pdg = {pdg: token for token in tokens
              for pdg in config["families"][token]}
    ranges = {"facet.associate_family.{}".format(token): [] for token in tokens}
    for row in rows:
        if row["family"] != "balancing" or row["value"] == "-":
            continue
        facet = by_pdg.get(int(row["associate_pdg"]))
        if facet is None:
            continue
        value = float.fromhex(row["value"])
        error = 0.0 if row["finite_mc_error"] == "-" else \
            float.fromhex(row["finite_mc_error"])
        ranges["facet.associate_family." + facet].append((value - error,
                                                           value + error))
    pages = []
    selection_short = selection["selection_id"][:16]
    for first in range(0, len(tokens), maximum):
        page_tokens = tokens[first:first + maximum]
        count = len(page_tokens)
        columns = min(columns_maximum, count)
        rows_count = (count + columns - 1) // columns
        page_number = len(pages) + 1
        facets = []
        for offset, token in enumerate(page_tokens):
            facet_id = "facet.associate_family." + token
            values = ranges[facet_id]
            facets.append({
                "facet_id": facet_id,
                "family_token": token,
                "order": first + offset,
                "grid_row": offset // columns,
                "grid_column": offset % columns,
                "axis_range_input": {
                    "valid_points": len(values),
                    "minimum_value_minus_uncertainty": (
                        None if not values else min(value[0] for value in values)),
                    "maximum_value_plus_uncertainty": (
                        None if not values else max(value[1] for value in values)),
                    "padding_fraction": layout["axis_padding_fraction"],
                },
            })
        pages.append({
            "page_id": "page.{}.{:03d}".format(selection_short, page_number),
            "output_role": "plot.{}.{}.page.{:03d}".format(
                selection["preset"], selection_short, page_number),
            "page_number": page_number,
            "grid_rows": rows_count,
            "grid_columns": columns,
            "shared_legend_reservation": layout["shared_legend_reservation"],
            "text_pixel_size": layout["text_pixel_size"],
            "facets": facets,
        })
    roles = [page["output_role"] for page in pages]
    if len(roles) != len(set(roles)):
        raise ValueError("layout page roles collide")
    return {"schema": "hadronization_plot_layout_primitives_v1",
            "maximum_panels_per_page": maximum,
            "facet_dimension": layout["facet_dimension"], "pages": pages}


def write_csv(path, rows):
    with path.open("w", encoding="ascii", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS,
                                lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        handle.flush()
        os.fsync(handle.fileno())


def write_tex(path, rows):
    selected = [row for row in rows if row["family"] == "sample_counts"]
    selected.sort(key=lambda row: (row["semantic_id"], row["tune"]))
    lines = [r"\begin{tabular}{lll}",
             r"Semantic ID & Tune & Exact count \\", r"\hline"]
    for row in selected:
        label = row["semantic_id"].replace("_", r"\_")
        numeric = float.fromhex(row["value"])
        if not numeric.is_integer():
            raise ValueError("T1 exact count is not an integer")
        value = str(int(numeric))
        lines.append("{} & {} & {} \\\\".format(label, row["tune"], value))
    lines.append(r"\end{tabular}")
    with path.open("w", encoding="ascii", newline="") as handle:
        handle.write("\n".join(lines) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def verify_export(directory, expected_request_id=None):
    reject_symlink_components(directory, "plot export directory")
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError("plot export is not a regular directory")
    manifest_path = directory / "manifest.json"
    manifest = json_file(manifest_path, "plot export manifest")
    exact_keys(manifest, {"schema", "version", "state", "compact_input",
                          "analysis_request_sha256", "plot_config_sha256",
                          "resolved_selection", "request_id", "roles",
                          "layout_primitives", "files", "filesystem_set",
                          "numerical_exports_sha256", "build"},
               "plot export manifest")
    if (manifest["schema"] != EXPORT_SCHEMA or manifest["version"] != "1.0.0" or
            manifest["state"] != "COMPLETE"):
        raise ValueError("plot export manifest state/schema differs")
    if expected_request_id is not None and manifest["request_id"] != expected_request_id:
        raise ValueError("plot export request identity differs")
    request_identity = {
        "schema": REQUEST_SCHEMA,
        "analysis_request_sha256": manifest["analysis_request_sha256"],
        "compact_scientific_content_digest": manifest["compact_input"][
            "scientific_content_digest"],
        "plot_config_sha256": manifest["plot_config_sha256"],
        "resolved_selection": manifest["resolved_selection"],
        "families": list(DEFAULT_FAMILIES),
    }
    if manifest["request_id"] != sha_bytes(canonical(request_identity).encode(
            "ascii")):
        raise ValueError("plot export request digest differs")
    expected = set(manifest["filesystem_set"])
    observed = {path.name for path in directory.iterdir()
                if path.is_file() and not path.is_symlink()}
    if any(path.is_symlink() or not path.is_file() for path in directory.iterdir()):
        raise ValueError("plot export contains a non-regular entry")
    if observed != expected or expected != {"manifest.json"}.union(
            item["name"] for item in manifest["files"]):
        raise ValueError("plot export exact filesystem set differs")
    payload_hashes = []
    expected_payload_names = {family + ".csv" for family in DEFAULT_FAMILIES}
    expected_payload_names.add("sample_counts.tex")
    if {item.get("name") for item in manifest["files"]} != expected_payload_names:
        raise ValueError("plot export payload set differs")
    semantic_ids = set()
    for item in manifest["files"]:
        exact_keys(item, {"name", "family", "bytes", "sha256"},
                   "plot export file")
        path = directory / item["name"]
        if path.stat().st_size != item["bytes"] or sha_file(path) != item["sha256"]:
            raise ValueError("plot export file identity differs: {}".format(item["name"]))
        payload_hashes.append(item["sha256"])
        if path.suffix == ".csv":
            with path.open(newline="", encoding="ascii") as handle:
                reader = csv.DictReader(handle)
                if reader.fieldnames != list(CSV_FIELDS):
                    raise ValueError("plot CSV schema differs: {}".format(item["name"]))
                for row in reader:
                    if (row["request_id"] != manifest["request_id"] or
                            row["compact_root_sha256"] !=
                            manifest["compact_input"]["root_sha256"] or
                            row["compact_scientific_content_digest"] !=
                            manifest["compact_input"]["scientific_content_digest"] or
                            row["family"] != item["family"] or
                            not row["semantic_id"] or
                            row["semantic_id"] in semantic_ids):
                        raise ValueError("plot CSV row identity differs: {}".format(
                            item["name"]))
                    semantic_ids.add(row["semantic_id"])
    if manifest["numerical_exports_sha256"] != sha_bytes(
            canonical(payload_hashes).encode("ascii")):
        raise ValueError("plot numerical export digest differs")
    roles = manifest["roles"]
    if len({role["id"] for role in roles}) != len(roles):
        raise ValueError("plot manifest role collision")
    page_roles = [page["output_role"] for page in
                  manifest["layout_primitives"]["pages"]]
    if len(page_roles) != len(set(page_roles)):
        raise ValueError("plot manifest page-role collision")
    scale = manifest["compact_input"]["scale"]
    if (sum(item["successful_events"] for item in scale["tunes"]) !=
            scale["successful_events_total"] or
            sum(item["sources"] for item in scale["tunes"]) !=
            scale["sources_total"] or
            any([item["block"] for item in tune["blocks"]] != scale["block_ids"]
                for tune in scale["tunes"])):
        raise ValueError("plot compact scale accounting differs")
    return manifest


def resolved_arguments(args, config, domains):
    if args.plot_request:
        reject_symlink_components(args.plot_request, "plot request")
    file_request = checked_plot_request(args.plot_request.resolve()) \
        if args.plot_request else None
    if file_request is not None and args.preset is not None and \
            args.preset != file_request["preset"]:
        raise ValueError("CLI and plot-request presets contradict")
    preset = args.preset or (file_request["preset"] if file_request else
                             "paper_default")
    includes = ((file_request["include"] if file_request else []) +
                list(args.include))
    excludes = ((file_request["exclude"] if file_request else []) +
                list(args.exclude))
    return resolve_selection(config, domains, preset, includes, excludes)


def prepare(args, families):
    for path, label in ((args.root, "compact ROOT"),
                        (args.receipt, "compact receipt"),
                        (args.analysis, "analysis request")):
        reject_symlink_components(path, label)
    root_path = args.root.resolve()
    receipt_path = args.receipt.resolve()
    analysis_path = args.analysis.resolve()
    work_root = args.work_dir.resolve(strict=False)
    work_root.mkdir(parents=True, exist_ok=True)
    receipt, summary = admit(root_path, receipt_path, analysis_path, work_root)
    config, config_sha = checked_plot_config(args.plot_config)
    domains = receipt["scientific_identity"]["compact_domains"]
    selection = resolved_arguments(args, config, domains)
    request_identity = {
        "schema": REQUEST_SCHEMA,
        "analysis_request_sha256": receipt["scientific_identity"][
            "analysis_request_sha256"],
        "compact_scientific_content_digest": receipt["scientific_identity"][
            "scientific_content_digest"],
        "plot_config_sha256": config_sha,
        "resolved_selection": selection,
        "families": list(families),
    }
    request_id = sha_bytes(canonical(request_identity).encode("ascii"))
    roles, rows, build = engine_rows(root_path, receipt, families, work_root)
    return (root_path, receipt, summary, config, config_sha, selection,
            request_id, roles, rows, build)


def export(args):
    prepared = prepare(args, DEFAULT_FAMILIES)
    (root_path, receipt, unused_summary, config, config_sha, selection,
     request_id, roles, rows, build) = prepared
    del unused_summary
    reject_symlink_components(args.output, "plot export output")
    output = args.output.resolve(strict=False)
    if output.exists():
        if args.reuse:
            manifest = verify_export(output, request_id)
            print("RESOLVED_SELECTION {}".format(canonical(selection)))
            print("REUSED OUTPUT={} REQUEST_ID={}".format(output,
                                                           manifest["request_id"]))
            return
        raise ValueError("no-overwrite plot export collision: {}".format(output))
    output.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="." + output.name + ".plot-stage-",
                                 dir=str(output.parent)))
    created_output = False
    try:
        selected = filter_rows(rows, selection)
        root_sha = receipt["storage_identity"]["root_sha256"]
        scientific = receipt["scientific_identity"]["scientific_content_digest"]
        eligibility = selection["eligibility_status"]
        public = [public_row(row, request_id, root_sha, scientific, eligibility)
                  for row in selected]
        public.sort(key=lambda row: row["semantic_id"])
        files = []
        for family in DEFAULT_FAMILIES:
            path = stage / (family + ".csv")
            write_csv(path, [row for row in public if row["family"] == family])
            files.append({"name": path.name, "family": family,
                          "bytes": path.stat().st_size, "sha256": sha_file(path)})
        tex = stage / "sample_counts.tex"
        write_tex(tex, selected)
        files.append({"name": tex.name, "family": "sample_counts",
                      "bytes": tex.stat().st_size, "sha256": sha_file(tex)})
        layout = layout_primitives(config, selection, selected)
        manifest = {
            "schema": EXPORT_SCHEMA,
            "version": "1.0.0",
            "state": "COMPLETE",
            "compact_input": {
                "root_sha256": root_sha,
                "root_bytes": receipt["storage_identity"]["root_bytes"],
                "scientific_content_digest": scientific,
                "scientific_identity_sha256": receipt[
                    "scientific_identity_sha256"],
                "publication_state": receipt["state"],
                "scale": compact_scale(receipt),
            },
            "analysis_request_sha256": receipt["scientific_identity"][
                "analysis_request_sha256"],
            "plot_config_sha256": config_sha,
            "resolved_selection": selection,
            "request_id": request_id,
            "roles": roles,
            "layout_primitives": layout,
            "files": files,
            "filesystem_set": sorted([item["name"] for item in files] +
                                     ["manifest.json"]),
            "numerical_exports_sha256": sha_bytes(canonical(
                [item["sha256"] for item in files]).encode("ascii")),
            "build": build,
        }
        atomic_json(stage / "manifest.json", manifest)
        verify_export(stage, request_id)
        output.mkdir(mode=0o700)
        created_output = True
        for item in files:
            os.link(str(stage / item["name"]), str(output / item["name"]))
        fsync_directory(output)
        if os.environ.get("HADRONIZATION_PLOT_FAIL_BEFORE_MANIFEST") == "1":
            raise ValueError("injected interruption before plot manifest commit")
        os.link(str(stage / "manifest.json"), str(output / "manifest.json"))
        fsync_directory(output)
        fsync_directory(output.parent)
        verify_export(output, request_id)
        created_output = False
        print("RESOLVED_SELECTION {}".format(canonical(selection)))
        print("EXPORTED OUTPUT={} REQUEST_ID={} FILES={}".format(
            output, request_id, len(files) + 1))
    finally:
        if created_output and output.exists():
            shutil.rmtree(str(output))
            fsync_directory(output.parent)
        if stage.exists():
            shutil.rmtree(str(stage))


def query(args):
    prepared = prepare(args, (args.family,))
    (unused_root, receipt, unused_summary, unused_config, unused_config_sha,
     selection, request_id, roles, rows, unused_build) = prepared
    del (unused_root, unused_summary, unused_config, unused_config_sha, unused_build)
    domains = receipt["scientific_identity"]["compact_domains"]
    if args.tune and args.tune not in domains["tune_dictionary"]:
        raise ValueError("requested tune is NOT_MATERIALIZED")
    if args.profile and args.profile not in {item["id"] for item in
                                             domains["profiles"]}:
        raise ValueError("requested profile is NOT_MATERIALIZED")
    if args.activity and args.activity not in {item["id"] for item in
                                                domains["activities"]}:
        raise ValueError("requested activity is NOT_MATERIALIZED")
    if args.class_id is not None and args.class_id not in {
            item["id"] for item in domains["class_dictionary"]}:
        raise ValueError("requested class is NOT_MATERIALIZED")
    if args.bin is not None and args.bin < 0:
        raise ValueError("requested bin is outside its domain")
    if args.pair:
        try:
            trigger, associate = map(int, args.pair.split(":"))
        except ValueError as error:
            raise ValueError("--pair must be TRIGGER_PDG:ASSOCIATE_PDG") from error
        pair = next((item for item in receipt["scientific_identity"][
            "compact_domains"]["pair_query_dictionary"]
                     if item["trigger_pdg"] == trigger and
                     item["associate_pdg"] == associate), None)
        if pair is None:
            raise ValueError("requested ordered pair is NOT_MATERIALIZED")
        if not pair["central_eligible"] and not args.diagnostic_pdg:
            raise ValueError("noncentral pair requires --diagnostic-pdg")
        selection = dict(selection)
        selection["signed_pdgs"] = sorted({associate, -associate})
        selection["pair_ids"] = [pair["id"]]
        selection["noncentral_signed_pdgs"] = (
            [] if pair["central_eligible"] else sorted({associate, -associate}))
        selection["eligibility_status"] = "EXACT_PDG_DIAGNOSTIC"
        selection["selection_id"] = sha_bytes(canonical({
            key: value for key, value in selection.items()
            if key != "selection_id"}).encode("ascii"))
    query_identity = {
        "base_request_id": request_id,
        "family": args.family,
        "tune": args.tune,
        "profile": args.profile,
        "activity": args.activity,
        "class_id": args.class_id,
        "pair": args.pair,
        "diagnostic_pdg": args.diagnostic_pdg,
        "bin": args.bin,
        "resolved_selection": selection,
    }
    request_id = sha_bytes(canonical(query_identity).encode("ascii"))
    selected = filter_rows(rows, selection, args)
    payload = {
        "schema": "hadronization_plot_query_result_v1",
        "request_id": request_id,
        "compact_scientific_content_digest": receipt["scientific_identity"][
            "scientific_content_digest"],
        "compact_scale": compact_scale(receipt),
        "resolved_selection": selection,
        "roles": roles,
        "query_status": "AVAILABLE" if selected else "NOT_MATERIALIZED",
        "row_count": len(selected),
        "rows": [public_row(
            row, request_id, receipt["storage_identity"]["root_sha256"],
            receipt["scientific_identity"]["scientific_content_digest"],
            selection["eligibility_status"]) for row in selected],
    }
    print(json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=True))


def verify(args):
    reject_symlink_components(args.output, "plot export output")
    manifest = verify_export(args.output.resolve())
    print("VERIFIED OUTPUT={} REQUEST_ID={} FILES={}".format(
        args.output.resolve(), manifest["request_id"],
        len(manifest["filesystem_set"])))


def common(parser):
    parser.add_argument("--root", type=Path, required=True,
                        help="verified compact plot-source ROOT")
    parser.add_argument("--receipt", type=Path, required=True,
                        help="matching compact reduction receipt")
    parser.add_argument("--analysis", type=Path, default=ANALYSIS)
    parser.add_argument("--plot-config", type=Path, default=PLOT_CONFIG)
    parser.add_argument("--plot-request", type=Path)
    parser.add_argument("--preset", choices=("paper_default", "all_central",
                                              "all_registered"))
    parser.add_argument("--include", action="append", default=[])
    parser.add_argument("--exclude", action="append", default=[])
    parser.add_argument("--work-dir", type=Path, default=Path(
        tempfile.gettempdir()) / "hadronization-plot-v1")


def parser():
    top = argparse.ArgumentParser(prog="hadronization plot", description=__doc__)
    sub = top.add_subparsers(dest="command", required=True)
    query_parser = sub.add_parser("query", help="verify and query numerical projections")
    common(query_parser)
    query_parser.add_argument("--family", choices=QUERY_FAMILIES, required=True)
    query_parser.add_argument("--tune")
    query_parser.add_argument("--profile")
    query_parser.add_argument("--activity")
    query_parser.add_argument("--class-id", type=int)
    query_parser.add_argument("--pair", help="exact TRIGGER_PDG:ASSOCIATE_PDG diagnostic")
    query_parser.add_argument("--diagnostic-pdg", action="store_true")
    query_parser.add_argument("--bin", type=int)
    export_parser = sub.add_parser("export", help="write deterministic CSV/TeX exports")
    common(export_parser)
    export_parser.add_argument("--output", type=Path, required=True)
    export_parser.add_argument("--reuse", action="store_true")
    verify_parser = sub.add_parser("verify", help="verify an exact completed export set")
    verify_parser.add_argument("--output", type=Path, required=True)
    return top


def main():
    args = parser().parse_args()
    try:
        if args.command == "query":
            query(args)
        elif args.command == "export":
            export(args)
        else:
            verify(args)
        return 0
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        print("ERROR: {}".format(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
