#!/usr/bin/env python3
"""Draw S-verified numerical ROOT without computing scientific quantities."""

import argparse
import copy
import fcntl
import gzip
import hashlib
import importlib
import importlib.util
import io
import json
import math
import os
import re
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
PLOT_CONFIG = ROOT / "config/plot.json"
TARGET_CAMPAIGN = ROOT / "data/campaign.json"
TARGET_CAMPAIGN_SHA256 = "cc2c0593d8b48103560bed7ba46fa7f81a8137bae24994c6ef2316dd9265005d"
DRAWING_SCHEMA = "hadronization_plot_drawing_plan_v9"
CANVAS_NAME = "canvases.root"
RECORD_NAME = "drawing-record.tsv.gz"
# Display order only: mesons first, then Lambda, Sigma and Xi baryons.
# Mass orders states within each group (particle/antiparticle equal).
# https://pdg.lbl.gov/2025/mcdata/mass_width_2025.mcd
SPECIES_DISPLAY_ORDER = (421, 411, 431, 521, 511, 531, 541,
                         4122, 4212, 4112, 4222, 4232, 4132,
                         5122, 5222, 5112, 5232, 5132)
P1_WITHHELD_SE_DISCLOSURE = (
    "Tune-ratio SE unavailable for unresolved sparse-tail denominators; "
    "see ROOT flags")
TYPED_POINT_FIELDS = (
    "semantic_id", "role_id", "family", "quantity", "tune",
    "reference_tune", "profile", "activity_id", "class_id",
    "trigger_pdg", "associate_pdg", "reference_pdg", "component", "axis",
    "bin_index", "bin_low", "bin_high", "flow", "units", "value",
    "value_status", "finite_mc_error", "uncertainty_status", "reasons")


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

@contextmanager
def build_lock(path):
    """Serialize one reproducible cache key across cooperating processes."""
    descriptor = os.open(str(path), os.O_CREAT | os.O_RDWR, 0o600)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        yield
    finally:
        fcntl.flock(descriptor, fcntl.LOCK_UN)
        os.close(descriptor)

def cached_build(binary, receipt, identity):
    if not binary.is_file() or not receipt.is_file():
        return None
    try:
        current = json_file(receipt, "plot build receipt")
    except ValueError:
        return None
    if (current.get("build_identity") == identity and
            current.get("binary_sha256") == sha_file(binary)):
        return current
    return None

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
    if (payload["schema"] != "hadronization_plot_presentation_v3" or
            payload["version"] != "3.2.0"):
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
    paper = presets["paper_default"]
    exact_keys(paper, {"families", "trigger_pdgs",
                       "baryon_meson_trigger_pdgs"},
               "paper_default preset")
    charm_meson = paper["trigger_pdgs"][0] if (
        isinstance(paper["trigger_pdgs"], list) and
        paper["trigger_pdgs"]) else None
    if (paper["families"] != ["D", "LambdaC", "B", "LambdaB"] or
            charm_meson not in (421, 411) or
            paper["trigger_pdgs"] != [charm_meson, 4122, 521, 5122] or
            paper["baryon_meson_trigger_pdgs"] != [charm_meson, 521]):
        raise ValueError("paper_default family selection differs")
    if (presets["all_central"] != {"selector": "all_central"} or
            presets["all_registered"] != {"selector": "all_registered"}):
        raise ValueError("complete plot presets differ")
    layout = payload["layout"]
    exact_keys(layout, {"axis_padding_fraction", "facet_dimension",
                        "grid_columns_maximum", "maximum_panels_per_page",
                        "shared_legend_reservation", "text_pixel_size",
                        "physical_width_cm", "minimum_body_text_pt",
                        "categorical_tune_dodge", "p1_inset_geometry",
                        "correlation_view", "activity_category_dividers"},
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
            layout["text_pixel_size"] < 1 or
            layout["physical_width_cm"] != 18.0 or
            layout["minimum_body_text_pt"] != 8.0 or
            layout["p1_inset_geometry"] != [.18, .05, .65, .48] or
            type(layout["activity_category_dividers"]) is not bool or
            layout["correlation_view"] not in
                ("monash_pair_sign", "monash_balance", "all_tune_ratio") or
            layout["categorical_tune_dodge"] != {
                "upper": {"MONASH": -.08, "JUNCTIONS": 0.0,
                          "CLOSEPACKING": .08},
                "lower": {"JUNCTIONS": -.04, "CLOSEPACKING": .04}}):
        raise ValueError("plot layout contract differs")
    styles = payload["style_identities"]
    exact_keys(styles, {"class_line_style_rule", "class_line_patterns",
                        "species_encoding", "tunes", "unity_reference"},
               "plot style identities")
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
            "integrated=1;nonintegrated=2+typed_class_ordinal" or
            styles["unity_reference"] != {
                "color": "neutral_gray", "line": "dotted",
                "role": "reference_only"}):
        raise ValueError("plot style identity differs")
    expected_patterns = [
        (1, "solid"), (2, "80 8"), (3, "40 12"),
        (4, "24 8 12 8 4 8"), (5, "24 8 4 8 4 8"), (6, "12 8"),
        (7, "4 8"), (8, "40 8 12 8"), (9, "12 8 4 8"),
        (10, "4 16"), (11, "24 8 4 8"),
        (12, "4 20")]
    patterns = styles["class_line_patterns"]
    if (not isinstance(patterns, list) or
            [(item.get("root_style"), item.get("dash_pattern"))
             for item in patterns] != expected_patterns or
            patterns[0] != {"root_style": 1, "dash_pattern": "solid",
                            "role": "inclusive"} or
            any(set(item) != {"root_style", "dash_pattern"}
                for item in patterns[1:])):
        raise ValueError("class line-pattern registry differs")
    return payload, sha_file(path)

def command_tokens(command, argument, environment):
    completed = subprocess.run([command, argument], env=environment, text=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if completed.returncode or completed.stderr.strip():
        raise ValueError("ROOT configuration failed: {}".format(
            completed.stderr.strip() or completed.stdout.strip()))
    return shlex.split(completed.stdout.strip())

def build_renderer(work_root):
    """Build the presentation-only renderer in the existing private cache."""
    runtime = runtime_module().resolve(require_root=True)
    environment = os.environ.copy()
    environment.update(runtime["environment"])
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    source = ROOT / "pipeline/plot/render.cpp"
    identity = {
        "schema": "hadronization_plot_renderer_build_v1",
        "source_sha256": sha_file(source), "compiler": runtime["environment"]["CXX"],
        "root": next(value.split("=", 1)[1] for value in runtime["diagnostics"]
                     if value.startswith("ROOT=")),
        "flags": ["-std=c++17", "-O2", "-Wall", "-Wextra", "-Wpedantic", "-Werror"],
    }
    build_id = sha_bytes(canonical(identity).encode("ascii"))
    binary_root = work_root.resolve(strict=False) / "bin"
    reject_symlink_components(binary_root, "plot renderer work root")
    binary_root.mkdir(parents=True, exist_ok=True)
    binary = binary_root / ("render-" + build_id[:20])
    receipt = binary.with_suffix(".build.json")
    lock = binary.with_suffix(".build.lock")
    with build_lock(lock):
        current = cached_build(binary, receipt, identity)
        if current is not None:
            return environment, binary, current
        for path in (binary, receipt):
            if path.exists() or path.is_symlink():
                path.unlink()
        flags = command_tokens(environment["ROOT_CONFIG"], "--cflags", environment)
        libraries = command_tokens(environment["ROOT_CONFIG"], "--libs", environment)
        descriptor, temporary_name = tempfile.mkstemp(prefix="." + binary.name + ".",
                                                     suffix=".tmp", dir=str(binary_root))
        os.close(descriptor)
        temporary = Path(temporary_name)
        try:
            completed = subprocess.run([environment["CXX"]] + identity["flags"] +
                                       [str(source)] + flags + libraries + ["-o", str(temporary)],
                                       env=environment, text=True, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            if completed.returncode or completed.stdout.strip() or completed.stderr.strip():
                raise ValueError("plot renderer warning-free build failed: {}".format(
                    completed.stderr.strip() or completed.stdout.strip()))
            os.chmod(str(temporary), 0o700)
            os.replace(str(temporary), str(binary))
            fsync_file(binary)
            fsync_directory(binary_root)
        finally:
            if temporary.exists():
                temporary.unlink()
        atomic_json(receipt, {"schema": "hadronization_plot_renderer_build_receipt_v1",
                              "build_id": build_id, "build_identity": identity,
                              "binary_sha256": sha_file(binary)})
        current = cached_build(binary, receipt, identity)
        if current is None:
            raise ValueError("plot renderer cache publication did not validate")
        return environment, binary, current

def typed_point_rows(projection):
    """Flatten validated v2 points without changing their scientific values."""
    payload = (projection.to_dict() if hasattr(projection, "to_dict")
               else projection)

    def decimal(token):
        if token is None:
            return ""
        value = float.fromhex(token)
        if not math.isfinite(value):
            raise ValueError("typed projection contains a nonfinite number")
        if value == 0.0:
            value = 0.0
        return format(value, ".17g")

    rows = []
    for point in payload["points"]:
        key = point["key"]
        curve = key["curve"]
        role = curve["role_id"]
        if role.startswith("balancing."):
            family = "balancing"
        elif role.startswith("correlations."):
            family = "correlations"
        elif role == "multiplicity.composite":
            family = "multiplicity"
        elif role.startswith(("kinematics.", "spectra.")):
            family = "kinematics"
        elif role.startswith("accounting."):
            family = "sample_counts"
        else:
            raise ValueError("typed projection carries an unknown paper role")
        bins = key["bins"]
        if len(bins) > 1:
            raise ValueError("typed point has more than one plotted axis bin")
        axis_bin = bins[0] if bins else None
        row = {
            "semantic_id": point["semantic_id"],
            "role_id": role,
            "family": family,
            "quantity": curve["quantity"],
            "tune": curve["tune_id"],
            "reference_tune": curve["reference_tune_id"] or "",
            "profile": curve["profile_id"] or "",
            "activity_id": curve["activity_id"] or "",
            "class_id": "" if curve["class_id"] is None else str(curve["class_id"]),
            "trigger_pdg": "" if curve["trigger_pdg"] is None else str(curve["trigger_pdg"]),
            "associate_pdg": "" if curve["associate_pdg"] is None else str(curve["associate_pdg"]),
            "reference_pdg": "" if curve["reference_pdg"] is None else str(curve["reference_pdg"]),
            "component": "" if curve["component"] == "NONE" else curve["component"],
            "axis": curve["axis_id"] or "",
            "bin_index": "" if axis_bin is None else str(axis_bin["index"]),
            "bin_low": "" if axis_bin is None else decimal(axis_bin["low"]),
            "bin_high": "" if axis_bin is None else decimal(axis_bin["high"]),
            "flow": "" if axis_bin is None else axis_bin["flow"],
            "units": point["units"],
            "value": decimal(point["center"]),
            "value_status": point["center_status"],
            "finite_mc_error": decimal(point["standard_error"]),
            "uncertainty_status": point["uncertainty_status"],
            "reasons": ",".join(point["reasons"]),
        }
        rows.append({field: row[field] for field in TYPED_POINT_FIELDS})
    return rows

def write_payload(path, payload):
    with path.open("wb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())

def deterministic_gzip(payload):
    output = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=output,
                       compresslevel=9, mtime=0) as handle:
        handle.write(payload)
    return output.getvalue()

def canonical_page_name(role_id, page_index=1, page_count=1):
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-")
    if not role_id or any(character not in allowed for character in role_id):
        raise ValueError("plot role cannot form a canonical page name: {}".format(role_id))
    suffix = "" if page_count == 1 else ".page.{:03d}".format(page_index)
    return role_id + suffix + ".pdf"

def decimal_number(token):
    """The public CSV is decimal; only the private drawing protocol is hex."""
    if token == "":
        return None
    if not isinstance(token, str) or not re.fullmatch(
            r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?", token):
        raise ValueError("invalid public decimal token: {!r}".format(token))
    value = float(token)
    if not math.isfinite(value):
        raise ValueError("nonfinite public decimal")
    return value

def verify_flat_fileset(directory, names, label):
    if (len(names) != len(set(names)) or any(
            not isinstance(name, str) or Path(name).name != name or
            name in {"", ".", ".."} for name in names)):
        raise ValueError(label + " filesystem set differs")
    entries = list(directory.iterdir())
    if (any(path.is_symlink() or not path.is_file() for path in entries) or
            {path.name for path in entries} != set(names)):
        raise ValueError(label + " filesystem set differs")

def _render_numbers(row):
    allowed = {
        "balancing": {"ordered_pair_yield", "os_minus_ss_per_trigger",
                      "baryon_meson_reference_ratio", "ratio_to_reference_tune",
                      "baryon_meson_ratio_to_reference_tune"},
        "correlations": {"dphi_per_trigger", "dphi_density_per_trigger",
                         "ratio_to_reference_tune"},
        "kinematics": {"normalized_distribution", "ratio_to_reference_tune",
                       "normalized_spectrum", "spectrum_ratio_to_reference_tune"},
        "multiplicity": {"normalized_distribution", "ratio_to_reference_tune"},
        "sample_counts": {"exact_t1_count"},
    }
    if row["quantity"] not in allowed.get(row["family"], set()):
        raise ValueError("quantity absent from public emitter contract")
    values = {k: decimal_number(row[k]) for k in
              ("value", "finite_mc_error", "bin_low", "bin_high")}
    has_value = row["value_status"] in {
        "AVAILABLE", "AVAILABLE_ZERO_DISPERSION", "UNSTABLE_DENOMINATOR"}
    has_error = row["uncertainty_status"] in {"AVAILABLE", "AVAILABLE_ZERO_DISPERSION"}
    if has_value != (values["value"] is not None):
        raise ValueError("public value/status relation differs")
    if has_error != (values["finite_mc_error"] is not None) or (has_error and not has_value):
        raise ValueError("public uncertainty/status relation differs")
    if has_error and values["finite_mc_error"] < 0:
        raise ValueError("public uncertainty is negative")
    if row["reference_tune"] and row["tune"] == row["reference_tune"]:
        raise ValueError("fake reference-tune ratio")
    if row["family"] == "balancing":
        if any(row[k] for k in ("bin_index", "bin_low", "bin_high", "axis")):
            raise ValueError("balancing has invented bin support")
    elif row["family"] != "sample_counts":
        if (row.get("flow") in ("", "REGULAR") and
                not re.fullmatch(r"[0-9]+", row["bin_index"])):
            raise ValueError("public histogram bin index differs")
        low, high = values["bin_low"], values["bin_high"]
        if low is None or high is None:
            if (row["family"] != "kinematics" or
                    row.get("flow") in ("", "REGULAR")):
                raise ValueError("public histogram support is absent")
        elif low >= high:
            raise ValueError("public histogram support is reversed")
    if row["family"] == "correlations" and row["component"] not in {"OS", "SS", "OS_MINUS_SS"}:
        raise ValueError("public correlation component differs")
    return values

def _panel_key(row, by_pdg, presentation):
    role = row['role_id']
    if role == 'balancing.baryon_meson.activity':
        return '{}.{}.{}'.format('lower' if row['reference_tune'] else 'upper',
            presentation['trigger_sectors'][row['trigger_pdg']], row['trigger_pdg'])
    if role == 'multiplicity.composite':
        return 'lower.ratio' if row['reference_tune'] else 'upper.distribution'
    if row['family'] == 'correlations':
        layer = 'compare' if row['reference_tune'] else 'main'
        return 'correlation.{}.{}.{}'.format(
            layer, row['trigger_pdg'], row['component'])
    if row['family'] == 'balancing':
        return '{}.{}'.format('lower' if row['reference_tune'] else 'upper',
                              row['trigger_pdg'])
    return 'main'

def _series_identity(row):
    fields = ['quantity','component','trigger_pdg','associate_pdg','reference_pdg',
              'tune','reference_tune','profile','activity_id','axis']
    identity = {k:row[k] for k in fields}
    if row['family'] == 'balancing' and row['role_id'] != 'balancing.baryon_meson.activity':
        # Species are categorical x coordinates in the reference-style panels.
        identity['associate_pdg'] = ''
        identity['reference_pdg'] = ''
        identity['class_id'] = row['class_id']
    elif row['family'] != 'balancing':
        identity['class_id'] = row['class_id']
    return identity

def _padded_range(values, padding, log=False):
    if any(not math.isfinite(v) for v in values):
        raise ValueError('presentation range exceeds finite domain')
    values = [v for v in values if not log or v > 0]
    if not values: return [0.01,1.] if log else [-.5,1.5]
    low,high=min(values),max(values)
    if log:
        factor=math.exp(max(math.log(high)-math.log(low),1.)*max(padding,.04))
        return [max(low/factor,float.fromhex('0x0.0000000000001p-1022')),min(high*factor,sys.float_info.max)]
    if low == high == 0: return [-.5,1.5]
    span=high-low or max(abs(low),1.)
    result=[low-span*max(padding,.04),high+span*max(padding,.04)]
    if not all(math.isfinite(v) for v in result): raise ValueError('presentation range exceeds finite domain')
    return result

def checked_p1_occupied_support(support, series):
    """Use S's authenticated observed extent, while refusing a cropped tail."""
    exact_keys(support, {"low", "high", "positive_low"},
               "P1 occupied support")
    low, high, positive_low = (support[name] for name in
                               ("low", "high", "positive_low"))
    if (any(type(value) not in (int, float) or not math.isfinite(value)
            for value in (low, high, positive_low)) or
            low != 0 or positive_low <= 0 or high <= low or
            high < positive_low):
        raise ValueError("P1 occupied support geometry differs")
    material = [point for item in series for point in item["points"]
                if point["state"] == "DRAW" and point["y"] is not None and
                (point["y"] != 0 or point["error"] not in (None, 0))]
    if any(point["support_high"] is not None and
           point["support_high"] > high for point in material):
        raise ValueError("P1 authenticated support crops materialized tail")
    if any(point["support_low"] is not None and
           point["support_low"] >= 0 and point["support_low"] < positive_low and
           point["support_high"] > positive_low and point["y"] != 0
           for point in material):
        raise ValueError("P1 positive inset misses occupied support")
    return [float(low), float(high)], [float(positive_low),
                                     float(max(high, positive_low + 1.))]

def p1_reference_display_high(series, reference_tune):
    """Return the last occupied unit-bin edge of the reference distribution.

    The numerical archive retains the full 4096-bin support.  The paper
    comparison uses the reference tune's populated range so isolated
    one-event bins in another tune cannot compress the common distribution
    and ratio panels into the left edge of a very wide linear axis.
    """
    reference = [point for item in series if item["tune"] == reference_tune
                 for point in item["points"]
                 if point["state"] == "DRAW" and point["y"] is not None and
                 point["y"] > 0 and point["support_high"] is not None]
    if not reference:
        raise ValueError("P1 reference tune has no positive occupied support")
    high = max(point["support_high"] for point in reference)
    if not math.isfinite(high) or high <= 0:
        raise ValueError("P1 reference display support differs")
    return high

def checked_category_order(declared, present_species, partial, role, trigger):
    if declared is None and not present_species and partial:
        declared = []
    if (not isinstance(declared, list) or
            len(declared) != len(set(declared)) or
            (not present_species.issubset(set(declared)) if partial else
             set(declared) != present_species)):
        raise ValueError('S numerical category order/key set differs: '+
                         role+' '+trigger)
    return list(declared)

def species_display_order(species):
    """Reorder authenticated categories without selecting or combining them."""
    rank = {pdg: index for index, pdg in enumerate(SPECIES_DISPLAY_ORDER)}
    if any(abs(int(pdg)) not in rank for pdg in species):
        raise ValueError('species lacks a baryon-content display order')
    return sorted(species, key=lambda pdg: (rank[abs(int(pdg))], int(pdg) < 0))

def checked_tune_ratio_layout(tunes, reference_tune, rows, role,
                              partial=False):
    """Bind lower-pad topology to authenticated tune/reference rows."""
    if (not tunes or len(tunes) != len(set(tunes)) or
            reference_tune not in tunes):
        raise ValueError("plot tune/reference layout differs")
    ratio_capable = role == "multiplicity.composite" or \
        role.startswith(("balancing.", "correlations.", "spectra."))
    ratio_rows = [row for row in rows if row["reference_tune"]]
    if any(row["reference_tune"] != reference_tune for row in ratio_rows):
        raise ValueError("plot ratio reference identity differs")
    observed = {row["tune"] for row in ratio_rows}
    expected = set(tunes) - {reference_tune} if ratio_capable else set()
    if observed != expected and not (partial and observed.issubset(expected)):
        raise ValueError("plot tune-ratio coverage differs")
    if role.startswith("correlations.") and expected and not partial:
        absolute = {(row["trigger_pdg"], row["component"], row["tune"])
                    for row in rows if not row["reference_tune"]}
        comparisons = {(row["trigger_pdg"], row["component"], row["tune"])
                       for row in ratio_rows}
        required = {(trigger, component, tune)
                    for trigger, component, _ in absolute
                    for tune in expected}
        if comparisons != required:
            raise ValueError("correlation OS/SS/net comparison key set differs")
    return bool(expected)

def categorical_display_x(base, role, class_id, tune, tunes, class_order,
                          dodge, ratio=False):
    """All tune/class markers coincide with their S-owned category center."""
    if role.startswith('balancing.activity.') and class_id not in class_order:
        raise ValueError('activity class display identity differs')
    return base

def resolved_class_styles(classes, patterns):
    """Resolve typed class IDs to unique authenticated ROOT dash styles."""
    integrated = [str(item['id']) for item in classes if item['integrated']]
    if len(integrated) != 1:
        raise ValueError("typed class registry must contain one integrated class")
    ordered = sorted((str(item['id']) for item in classes
                      if not item['integrated']), key=int)
    if len(patterns) < len(ordered) + 1:
        raise ValueError("class pattern registry is too short")
    mapping = {integrated[0]: patterns[0]['root_style']}
    mapping.update({class_id: patterns[index + 1]['root_style']
                    for index, class_id in enumerate(ordered)})
    if mapping[integrated[0]] != 1 or len(set(mapping.values())) != len(mapping):
        raise ValueError("class style registry is not unique/inclusive-solid")
    return mapping


def selected_extreme_class_ids(classes):
    """Select exact saved intervals; never approximate a missing class."""
    requested = ((0., 1.), (40., 50.), (80., 90.))
    regular = {tuple(item['percentile_interval']): str(item['id'])
               for item in classes if not item['integrated']}
    return [regular[interval] for interval in requested if interval in regular]


def correlation_y_title(rows, component='OS'):
    """Label stored per-bin yields or densities without changing values."""
    quantities = {row['quantity'] for row in rows
                  if row['quantity'] != 'ratio_to_reference_tune'}
    if not quantities:
        return 'Correlation yield (units unavailable)'
    if len(quantities) != 1:
        raise ValueError('correlation panel has absent or mixed numerical units')
    quantity = next(iter(quantities))
    expected_units = {'dphi_per_trigger': 'per_trigger_per_bin',
                      'dphi_density_per_trigger': 'per_trigger_per_radian'}
    if quantity not in expected_units or any(
            row['units'] != expected_units[quantity] for row in rows
            if row['quantity'] != 'ratio_to_reference_tune'):
        raise ValueError('correlation quantity and numerical units disagree')
    numerator = ('(#it{N}_{OS}-#it{N}_{SS})' if component == 'OS_MINUS_SS'
                 else '#it{N}_{pair}')
    if quantity == 'dphi_density_per_trigger':
        return '#frac{1}{#it{N}_{trig}} #frac{d'+numerator+'}{d#Delta#varphi} (rad^{-1})'
    if quantity == 'dphi_per_trigger':
        return numerator+' / #it{N}_{trig} (per bin)'
    raise ValueError('unknown correlation numerical units')


def p1_ratio_uncertainty_note(role, panel_id, points, fallback):
    """Keep withheld finite ratio errors visible without per-point glyphs."""
    if (role == 'multiplicity.composite' and panel_id == 'lower.ratio' and
            any(point.get('state') == 'DRAW' and
                point.get('y') is not None and
                math.isfinite(point['y']) and point.get('error') is None
                for point in points)):
        return P1_WITHHELD_SE_DISCLOSURE
    return fallback


def exact_particle_ratio_title(rows, label):
    """Name the signed numerator and denominator of one yield ratio."""
    pairs = {(row['associate_pdg'], row['reference_pdg']) for row in rows
             if row.get('associate_pdg') and row.get('reference_pdg')}
    if not pairs:
        return ''
    if len(pairs) != 1:
        raise ValueError('baryon/meson panel mixes particle yield ratios')
    associate, reference = next(iter(pairs))
    return '{} / {}'.format(
        label(associate), label(reference))

def activity_emphasis(role, class_id, classes):
    if (role.startswith('balancing.activity.') and class_id and
            class_id in selected_extreme_class_ids(classes)):
        return 'EXTREME'
    return 'NORMAL'

def join_ratio_pads(pages):
    """Make each saved absolute/comparison frame share one physical edge."""
    for page in pages:
        by_id={panel['id']:panel for panel in page['panels']}
        for lower_id, lower in by_id.items():
            if lower_id=='lower.ratio': upper_id='upper.distribution'
            elif lower_id=='g9.ratio': upper_id='g9.absolute'
            elif (lower_id.startswith('correlation.balance.') and
                  lower_id.endswith('.lower')):
                upper_id=lower_id[:-len('.lower')]+'.upper'
            elif (lower_id.startswith('correlation.teaching.') and
                  lower_id.endswith('.inclusive')):
                upper_id=lower_id[:-len('.inclusive')]+'.identified'
            elif lower_id.startswith('lower.'):
                upper_id='upper.'+lower_id[len('lower.'):]
            elif lower_id.startswith('correlation.compare.'):
                upper_id='correlation.main.'+lower_id[len('correlation.compare.'):]
            else: continue
            upper=by_id.get(upper_id)
            if upper is None: continue
            if (upper['geometry'][0] != lower['geometry'][0] or
                    upper['geometry'][2] != lower['geometry'][2] or
                    upper['margins'][0] != lower['margins'][0] or
                    upper['margins'][1] != lower['margins'][1] or
                    upper['x_range'] != lower['x_range']):
                raise ValueError('absolute/ratio horizontal plotting edges differ')
            upper['geometry'][1]=lower['geometry'][3]
            upper['margins'][2]=0.
            lower['margins'][3]=0.
            lower['title']=''
            if (page['role']=='correlations.beauty' and
                    lower_id=='correlation.compare.521.OS_MINUS_SS'):
                # Keep the joined border, but separate the upper 0 and
                # comparison 1.6 y labels at manuscript width.
                lower['y_range'][1]=max(lower['y_range'][1],1.8)
            if page['role'].startswith('balancing.'):
                lower['geometry'][1]=.08

def correlation_reference_partners(pairs, trigger):
    partners={}
    for sign,component in ((-1,'OS'),(1,'SS')):
        matches=[pair for pair in pairs
                 if str(pair['trigger_pdg'])==str(trigger) and
                 pair['sign']==sign and
                 abs(pair['associate_pdg'])==
                 abs(pair['reference_meson_pdg'])]
        if len(matches)!=1:
            raise ValueError('typed signed correlation reference '
                             'pair absent/ambiguous: '+str(trigger)+'/'+
                             component)
        partners[component]=matches[0]['associate_pdg']
    return partners


def checked_charm_recipe_binding(scope, config):
    """A/S own the charm recipe; a P alternate may only select matching science."""
    triggers = config['presets']['paper_default']['trigger_pdgs']
    if scope['ordered_triggers'] != triggers:
        raise ValueError('plot charm preset differs from S ordered triggers')
    charm = triggers[0]
    pairs = scope['ordered_associate_pairs']
    for trigger in (charm, 4122):
        selected = [pair for pair in pairs if
                    pair['trigger_pdg'] == trigger and
                    pair['sector'] == 'CHARM']
        if (not selected or any(pair['reference_meson_pdg'] != -charm
                                for pair in selected)):
            raise ValueError('plot charm preset differs from S reference meson')
        reference = {(pair['sign'], pair['associate_pdg']) for pair in
                     selected if abs(pair['associate_pdg']) == charm}
        if reference != {('OS', -charm), ('SS', charm)}:
            raise ValueError('plot charm preset differs from S signed pairs')
    for role in scope['roles']:
        if role['role_id'] != 'balancing.baryon_meson.activity':
            continue
        if any(key['reference_pdg'] != -charm for key in
               role['required_curve_keys'] if key['trigger_pdg'] == charm):
            raise ValueError('plot charm preset differs from S P8 reference')


def checked_paper_pair_profile(payload, config, profile):
    """Bind P2-P8 to A/S's archived no-floor, no-diagonal selection."""
    if payload['schema'] != 'hadronization_projection_result_v4':
        return ''
    if (profile['id'] != 'inclusive' or
            profile['relative_pt'] != 'NONE' or
            profile['minimum_hierarchy'] != 'NONE'):
        raise ValueError('S paper requires inclusive no-diagonal pair profile')
    for field in ('trigger_pt', 'associate_pt'):
        cut = profile[field]
        if (cut['domain'] != 'PHYSICAL' or cut['units'] != 'GeV' or
                any(cut[key] is not None for key in
                    ('low', 'high', 'low_operator', 'high_operator'))):
            raise ValueError('S pair profile carries a fixed pT cut')
    for role in payload['request_echo']['scope']['roles']:
        if role['role_id'].startswith(('balancing.', 'correlations.')) and any(
                key['profile_id'] != profile['id'] for key in
                role['required_curve_keys']):
            raise ValueError('S paper role uses a different pair profile')
    return ('P2-P8: no final-hadron #it{p}_{T} floor; '
            '#it{N}_{trig}: eligible singles')


def focused_extreme_pages(pages, context, padding):
    """Add supplemental P5/P7 views by filtering saved class series only."""
    if len(context.tunes) < 2:
        return []
    selected = selected_extreme_class_ids(context.classes)
    if len(selected) != 3:
        # Other valid class recipes remain renderable. They cannot stand in
        # for any of these exact three requested display intervals.
        return []
    by_id = {str(item['id']): item for item in context.classes}
    descriptions = ['{}-{}%'.format(*(
        format(float(value), '.15g') for value in
        by_id[class_id]['percentile_interval']))
                    for class_id in selected]
    result = []
    for source in pages:
        if source['role'] not in ('balancing.activity.charm',
                                  'balancing.activity.beauty'):
            continue
        upper = [panel for panel in source['panels']
                 if panel['id'].startswith('upper.')]
        if not upper or any(
                not all(any(series['class_id'] == class_id and
                            any(point['state'] == 'DRAW'
                                for point in series['points'])
                            for series in panel['series'])
                        for class_id in selected)
                for panel in upper):
            if not partial_numerics(context):
                raise ValueError('complete activity endpoint drawing absent')
            continue
        page = copy.deepcopy(source)
        page['filename'] = 'supplemental.'+source['role']+'.extremes.pdf'
        page['title'] = ('Selected activity intervals: '+', '.join(descriptions))
        for panel in page['panels']:
            panel['series'] = [series for series in panel['series']
                               if series['class_id'] in selected]
            valid = [point for series in panel['series']
                     for point in series['points']
                     if point['state'] == 'DRAW' and point['y'] is not None]
            signed = any(point['y']-(point['error'] or 0) <= 0
                         for point in valid)
            panel['log_y'] = panel['log_y'] and not signed
            values = [value for point in valid
                      for value in (point['y'],
                                    point['y']-(point['error'] or 0),
                                    point['y']+(point['error'] or 0))]
            if panel['id'].startswith('lower.'):
                values.append(1.)
            panel['y_range'] = _padded_range(values, padding,
                                              panel['log_y'])
            panel['status'] = 'AVAILABLE' if valid else 'NOT_MATERIALIZED'
            missing = sum(point['state'] != 'DRAW'
                          for series in panel['series']
                          for point in series['points'])
            panel['note'] = ('signed y uses linear scale; ' if signed else '') + \
                ('{} missing (#times)'.format(missing) if missing else '')
            panel['guides'] = [guide for guide in panel['guides']
                               if guide['id'] != 'signed_zero']
            if signed:
                panel['guides'].append({'id':'signed_zero',
                    'x_low':panel['x_range'][0],
                    'x_high':panel['x_range'][1],
                    'y_low':0.,'y_high':0.,'color':'#777777',
                    'line_style':7,'label':''})
        result.append(page)
    return result

def tune_separated_activity_pages(pages, tunes):
    """Replace each all-class activity page by three tune rows plus one ratio row."""
    result = []
    for source in pages:
        if source['role'] not in ('balancing.activity.charm',
                                  'balancing.activity.beauty'):
            result.append(source)
            continue
        upper = sorted((panel for panel in source['panels']
                        if panel['id'].startswith('upper.')),
                       key=lambda panel: panel['geometry'][0])
        lower = sorted((panel for panel in source['panels']
                        if panel['id'].startswith('lower.')),
                       key=lambda panel: panel['geometry'][0])
        if len(upper) != 2 or len(lower) != 2 or len(tunes) != 3:
            raise ValueError('three-tune activity page topology differs')
        page = copy.deepcopy(source)
        page['height'] = 2850
        page['panels'] = []
        class_ids = {
            series.get('class_id')
            for panel in upper for series in panel['series']
            if series.get('class_id')
        }
        # Match the science stack to the actual height of the class key.  The
        # two-class extreme pages need only one key row; retaining the
        # eleven-class reservation left a large unused band above the plots.
        class_rows = max(1, (len(class_ids) + 3) // 4)
        class_legend_bottom = .925 - .034 * class_rows
        ratio_bottom, ratio_top = .08, .22
        science_top = class_legend_bottom - .015
        row_height = (science_top - ratio_top) / len(tunes)
        for tune_index, tune in enumerate(tunes):
            row_top = science_top - tune_index * row_height
            row_bottom = row_top - row_height
            for original in upper:
                panel = copy.deepcopy(original)
                trigger = original['id'].split('.', 1)[1]
                panel['id'] = 'upper.{}.{}'.format(tune, trigger)
                panel['geometry'] = [original['geometry'][0], row_bottom,
                                     original['geometry'][2], row_top]
                panel['title'] = original['title'] if tune_index == 0 else ''
                panel['series'] = [series for series in panel['series']
                                   if series['tune'] == tune]
                panel['margins'][2] = 0.
                panel['margins'][3] = .15 if tune_index == 0 else 0.
                page['panels'].append(panel)
        for original in lower:
            panel = copy.deepcopy(original)
            trigger = original['id'].split('.', 1)[1]
            panel['id'] = 'lower.shared.'+trigger
            panel['geometry'] = [original['geometry'][0], ratio_bottom,
                                 original['geometry'][2], ratio_top]
            panel['title'] = ''
            panel['y_title'] = 'TUNE/MONASH'
            panel['margins'][3] = 0.
            page['panels'].append(panel)
        result.append(page)
    return result

def tune_separated_baryon_meson_page(pages, tunes):
    """Add the requested three-row tune view while retaining the overlay page."""
    sources = [page for page in pages
               if page['filename'] ==
               canonical_page_name('balancing.baryon_meson.activity')]
    if len(sources) != 1 or len(tunes) != 3:
        raise ValueError('baryon/meson tune-separated source differs')
    source = sources[0]
    upper = sorted((panel for panel in source['panels']
                    if panel['id'].startswith('upper.')),
                   key=lambda panel: panel['geometry'][0])
    lower = sorted((panel for panel in source['panels']
                    if panel['id'].startswith('lower.')),
                   key=lambda panel: panel['geometry'][0])
    if len(upper) != 2 or len(lower) != 2:
        raise ValueError('baryon/meson source pair topology differs')
    page = copy.deepcopy(source)
    page['filename'] = 'supplemental.balancing.baryon_meson.activity.by_tune.pdf'
    page['height'] = 2850
    page['panels'] = []
    ratio_bottom, ratio_top, science_top = .08, .22, .89
    row_height = (science_top - ratio_top) / len(tunes)
    for tune_index, tune in enumerate(tunes):
        row_top = science_top - tune_index * row_height
        row_bottom = row_top - row_height
        for original in upper:
            panel = copy.deepcopy(original)
            suffix = original['id'][len('upper.'):]
            panel['id'] = 'upper.{}.{}'.format(tune, suffix)
            panel['geometry'] = [original['geometry'][0], row_bottom,
                                 original['geometry'][2], row_top]
            panel['title'] = original['title'] if tune_index == 0 else ''
            panel['series'] = [series for series in panel['series']
                               if series['tune'] == tune]
            for series in panel['series']:
                series['legend_label'] = ''
            panel['margins'][2] = 0.
            panel['margins'][3] = .15 if tune_index == 0 else 0.
            page['panels'].append(panel)
    for original in lower:
        panel = copy.deepcopy(original)
        suffix = original['id'][len('lower.'):]
        panel['id'] = 'lower.shared.'+suffix
        panel['geometry'] = [original['geometry'][0], ratio_bottom,
                             original['geometry'][2], ratio_top]
        panel['title'] = ''
        panel['x_title'] = 'Multiplicity Percentile Interval (%)'
        panel['y_title'] = 'TUNE/MONASH'
        panel['margins'][3] = 0.
        page['panels'].append(panel)
    return page

def apply_display_limits(pages):
    """Change frame limits while retaining every saved point and error."""
    for page in pages:
        for panel in page['panels']:
            if (page['role'] == 'multiplicity.composite' and
                    panel['id'] == 'lower.ratio'):
                lower=[q['y']-(q.get('error') or 0.)
                       for z in panel['series'] for q in z['points']
                       if q.get('y') is not None and q['y'] <= 5.]
                panel['y_range'] = [min([0.]+lower)-.08, 5.]
            if (page['role'].startswith('correlations.') and panel['log_y']
                    and not panel['id'].startswith('correlation.compare.')):
                positive=[q['y'] for z in panel['series'] for q in z['points']
                          if q.get('y') is not None and q['y']>0.]
                floor=min(1.e-5, min(positive)*.8) if positive else 1.e-5
                panel['y_range'] = [floor, max(panel['y_range'][1], floor*10.)]


def synchronize_paired_y_ranges(pages):
    """Give each left/right row one shared y scale without changing its data."""
    for page in pages:
        rows = {}
        for panel in page['panels']:
            if panel.get('reuse'):
                continue
            key = (panel['geometry'][1], panel['geometry'][3])
            rows.setdefault(key, []).append(panel)
        for panels in rows.values():
            if len(panels) != 2:
                continue
            panels.sort(key=lambda panel: panel['geometry'][0])
            if panels[0]['geometry'][2] > panels[1]['geometry'][0]:
                continue
            log_y = all(panel['log_y'] for panel in panels)
            y_range = [min(panel['y_range'][0] for panel in panels),
                       max(panel['y_range'][1] for panel in panels)]
            if log_y and y_range[0] <= 0:
                raise ValueError('paired logarithmic y range is nonpositive')
            for panel in panels:
                panel['log_y'] = log_y
                panel['y_range'] = y_range[:]

def join_paired_columns(pages):
    """Join equal-scale frames and retain one y axis for each paired row."""
    for page in pages:
        rows = {}
        for panel in page['panels']:
            if not panel.get('reuse'):
                rows.setdefault(tuple(panel['geometry'][1::2]), []).append(panel)
        for panels in rows.values():
            if len(panels) != 2:
                continue
            left, right = sorted(panels, key=lambda p: p['geometry'][0])
            if left['geometry'][2] > right['geometry'][0]:
                continue
            if (left['y_range'] != right['y_range'] or
                    left['log_y'] != right['log_y'] or
                    left['margins'][2:] != right['margins'][2:]):
                raise ValueError('paired frames cannot share their y axis')
            start, end = left['geometry'][0], right['geometry'][2]
            outer_left = start + (left['geometry'][2]-start)*left['margins'][0]
            outer_right = end - (end-right['geometry'][0])*right['margins'][1]
            seam = (outer_left+outer_right)/2
            left['geometry'][2] = right['geometry'][0] = seam
            left['margins'][0] = (outer_left-start)/(seam-start)
            left['margins'][1] = right['margins'][0] = 0.
            right['margins'][1] = (end-outer_right)/(end-seam)
            if left['y_title'] != right['y_title']:
                # Different signed baryon/meson ratios share the same scale.
                # Preserve each exact identity beside its trigger title.
                for panel in (left, right):
                    if panel['title']:
                        panel['title'] += ': '+panel['y_title']
                left['y_title'] = 'Balancing yield ratio'
            right['y_title'] = ''

def typed_panel_status(context, rows):
    """Summarize saved materialization and estimator statuses for a blank pad."""
    if not rows:
        return 'NOT_MATERIALIZED', ''
    records = [context.materialization_by_semantic_id[row['semantic_id']]
               for row in rows]
    statuses = {item['status'] for item in records}
    if statuses == {'PRESENT'}:
        status = ('PRESENT_UNDEFINED'
                  if {row['value_status'] for row in rows} == {'UNDEFINED'}
                  else 'PRESENT_NO_DRAWABLE_CENTER')
    elif statuses == {'NOT_MATERIALIZED'}:
        status = 'NOT_MATERIALIZED'
    elif statuses == {'UNSUPPORTED_QUERY'}:
        status = 'UNSUPPORTED_QUERY'
    else:
        status = 'PARTIAL_MATERIALIZATION'
    typed_statuses = sorted({row['value_status'] for row in rows} |
                            {row['uncertainty_status'] for row in rows})
    # Retain the exact source-qualified codes on every point and in ROOT.
    # A facet only needs their distinct typed cause, not one repeated code
    # per source, which otherwise runs across adjacent pads.
    reasons = sorted({reason.split(':', 1)[0] for row in rows
                      for reason in row['reasons'].split(',') if reason} |
                     {reason.split(':', 1)[0] for item in records
                      for reason in item['reason_codes']})
    return status, '; '.join(typed_statuses + reasons)


def compact_paper_status_note(status, note):
    """Fit a typed cause in narrow paper facets; point codes remain exact."""
    codes = [code for code in note.split('; ') if code]
    if status == 'PRESENT_UNDEFINED':
        codes = [code for code in codes
                 if code not in ('UNDEFINED', 'UNDEFINED_CENTER')]
    captions = {'WITHHELD_UNCERTAINTY': 'SE withheld',
                'DENOMINATOR_NUMERICALLY_UNRESOLVED':
                    'denominator unresolved'}
    readable = [captions.get(code, code.replace('_', ' ').lower())
                for code in codes]
    if len(readable) > 2:
        readable = readable[:2] + [str(len(readable)-2)+' more codes in ROOT']
    return ', '.join(readable)


def partial_numerics(value):
    """Keep v3 package incompleteness distinct from v4 campaign sampling."""
    if isinstance(value, dict):
        schema = value['schema']
        package_state = value['package_state']
        campaign_state = value['campaign_state']
    else:
        schema = value.numerics_schema
        package_state = value.package_state
        campaign_state = value.campaign_state
    if schema == 'hadronization_projection_result_v3_g9_science':
        return package_state == 'VALIDATED_PARTIAL'
    if schema == 'hadronization_projection_result_v4':
        if package_state != 'VALIDATED_COMPLETE':
            raise ValueError('v4 numerical package state differs')
        return campaign_state == 'PARTIAL_SAMPLE'
    raise ValueError('unsupported S numerical schema')


def synthetic_provenance(payload):
    return any(isinstance(item, str) and
               item.startswith('TEST_ONLY_SYNTHETIC')
               for item in payload['provenance']['data_limitations'])


def g9_signed_species(curve):
    """The S G9 curve keys store the plotted signed species as associate."""
    if (curve['role_id'] != 'spectra.signed_heavy' or
            curve['trigger_pdg'] is not None or
            curve['associate_pdg'] is None):
        raise ValueError('G9 signed-species curve key differs')
    return curve['associate_pdg']

def target_analysis_caption(payload):
    """Bind preview context to accepted campaign bytes, never synthetic provenance."""
    provenance=payload['provenance']
    synthetic=synthetic_provenance(payload)
    source_campaign=payload['request_echo']['sources']['campaign_id']
    if not synthetic and source_campaign!='HF_RUN3_V1':
        return '{name} {version}; {beam}, #sqrt{{#it{{s}}}} = {energy} TeV'.format(
            name=provenance['generator_name'],
            version=provenance['generator_version'],
            beam=provenance['collision_system'],
            energy=format(float.fromhex(provenance['energy_gev'])/1000,'.15g'))
    reject_symlink_components(TARGET_CAMPAIGN, 'target campaign descriptor')
    if sha_file(TARGET_CAMPAIGN) != TARGET_CAMPAIGN_SHA256:
        raise ValueError('target campaign descriptor SHA256 differs')
    target=json_file(TARGET_CAMPAIGN, 'target campaign descriptor')
    source_tunes = payload['request_echo']['scope']['ordered_tunes']
    if payload['schema'] == 'hadronization_projection_result_v4':
        same_tunes = (len(source_tunes) == len(set(source_tunes)) and
                      set(target['tune_order']) == set(source_tunes))
    else:
        same_tunes = target['tune_order'] == source_tunes
    if (target['schema']!='hadronization_campaign_record_v1' or
            not same_tunes):
        raise ValueError('target campaign scope differs')
    version=target['runtime']['pythia_version']
    beam=target['physics']['beam']
    energy=target['physics']['sqrt_s_gev']
    if (not isinstance(version,str) or not version or
            not isinstance(beam,str) or not beam or
            type(energy) not in (int,float) or energy<=0):
        raise ValueError('target campaign generator/collision differs')
    if not synthetic:
        if (provenance['generator_name'].upper()!='PYTHIA' or
                provenance['generator_version']!=version or
                provenance['collision_system']!=beam or
                float.fromhex(provenance['energy_gev'])!=energy):
            raise ValueError('numerical provenance contradicts target campaign')
    caption='PYTHIA {}; {}, #sqrt{{#it{{s}}}} = {} TeV'.format(
        version, beam, format(energy/1000,'.15g'))
    # Synthetic packets carry their own visible TEST_ONLY marker.  The
    # authenticated target campaign is 13.6 TeV; calling it merely planned
    # here would misdescribe the existing production dataset.
    return caption


def activity_proxy_caption(selection, threshold, eta_window):
    """Describe only the population authenticated by the typed activity cut."""
    if not (selection['charged'] and selection['final'] and
            selection['exclude_heavy_constituents'] and
            selection['pt']['low_operator']=='GT'):
        raise ValueError('P1 typed charged-final activity differs')
    return ('#it{N}_{ch}: charged-light final-particle activity, heavy flavour excluded; '
            '#it{p}_{T} > '+format(threshold,'.15g')+
            ' GeV/c, |#eta| #leq '+format(eta_window,'.15g'))

def sample_caption(payload):
    """Read sample facts from the checksum-bound campaign descriptor."""
    campaign_id = payload['request_echo']['sources']['campaign_id']
    if campaign_id != 'HF_RUN3_V1' and not synthetic_provenance(payload):
        return ['Generator-level sample; selection in numerical provenance']
    if sha_file(TARGET_CAMPAIGN) != TARGET_CAMPAIGN_SHA256:
        raise ValueError('caption campaign descriptor SHA256 differs')
    physics = json_file(TARGET_CAMPAIGN, 'caption campaign')['physics']
    if (physics['hard_processes'] != ['ccbar', 'bbbar'] or
            physics['heavy_hadron_decays'] != 'disabled'):
        raise ValueError('caption heavy-sample definition differs')
    return ['Hard c#bar{c}, b#bar{b}; #hat{p}_{T} #geq '+
            format(physics['pthat_min_gev'], '.15g')+' GeV/c']


def scientific_caption_lines(page, context):
    """Describe persisted selections without selecting or computing an observable."""
    lines = [context.target_analysis_caption]
    lines.extend(context.sample_caption)
    role = page['role']
    if role.startswith(('balancing.', 'correlations.')):
        profile = context.profile_definition
        eta = format(float.fromhex(profile['trigger_eta']['high']), '.15g')
        if profile['trigger_pt']['low'] is None:
            lines.append('|#eta| #leq '+eta)
        else:
            lines.append('Pairs: p_{T}^{trig} #geq '+format(float.fromhex(profile['trigger_pt']['low']), '.15g')+
                         ', p_{T}^{assoc} #geq '+format(float.fromhex(profile['associate_pt']['low']), '.15g')+' GeV/c')
            lines[-1] += '; |#eta| #leq '+eta
    if role=='multiplicity.composite' or '.activity.' in role or role.endswith('.activity'):
        activity=context.activity_selection
        eta_line='|#eta| #leq '+format(float.fromhex(activity['eta_window']), '.15g')
        if eta_line in lines:
            lines.remove(eta_line)
        lines.extend(['N_{ch}: charged light final particles',
            'p_{T} > '+format(float.fromhex(activity['pt']['low']), '.15g')+
            ' GeV/c; |#eta| #leq '+format(float.fromhex(activity['eta_window']), '.15g')])
    if role=='spectra.signed_heavy':
        eta=format(float.fromhex(context.g9_science['eta']['high']), '.15g')
        lines[-1] += '; |#eta| #leq '+eta
        lines.append('Normalized probability per bin')
    if (len(lines)>=3 and lines[-1].startswith('|#eta|')
            and lines[-2].startswith('Hard ')):
        eta_line=lines.pop()
        lines[-1] += '; '+eta_line
    return lines


def add_publication_captions(pages, context):
    """Place sample text inside frames and retain separate column titles."""
    for page in pages:
        panels=[p for p in page['panels'] if not p.get('reuse')]
        top=max(p['geometry'][3] for p in panels)
        row=[p for p in panels if p['geometry'][3]==top]
        target=min(row, key=lambda p:p['geometry'][0])
        lines=scientific_caption_lines(page,context)
        page['scientific_caption']=lines
        for panel in page['panels']: panel['annotations']=[]
        font=max(page['text_pixels'],math.ceil(9*page['width']/(18*72/2.54)))
        if page['role'] == 'spectra.signed_heavy':
            for panel in row:
                ph=page['height']*(panel['geometry'][3]-panel['geometry'][1])
                panel['margins'][3]=1.8*font/ph
        elif page['role'] != 'multiplicity.composite':
            if page['role'].startswith('balancing.'):
                page['height']=max(page['height'],2950 if len(panels)>4 else 1600)
            # Reserve only the column title above the frame. Scientific text
            # is inside the data panel at the selected reference position.
            titled=[p for p in panels if p in row or p['id'].startswith('correlation.main.')]
            for panel in titled:
                ph=page['height']*(panel['geometry'][3]-panel['geometry'][1])
                panel['margins'][3]=(3. if panel['id'].startswith('correlation.main.') else 1.8)*font/ph
        ph=page['height']*(target['geometry'][3]-target['geometry'][1])
        x=target['margins'][0]+.025
        keyfont=font+(2 if page['width']>1500 else 0)
        # ROOT centers legend text in each row. Its visible baseline lies
        # 0.39 font heights below that center with the selected Helvetica font.
        y=1.-target['margins'][3]-1.865*keyfont/ph
        step=1.30*font/ph
        if page['role'].startswith('correlations.'):
            pw=page['width']*(target['geometry'][2]-target['geometry'][0])
            x=target['margins'][0]+1.55*font/pw
            y=1.-target['margins'][3]-2.465*(font+2)/ph
        if page['role']=='spectra.signed_heavy':
            pw=page['width']*(target['geometry'][2]-target['geometry'][0])
            x=target['margins'][0]+2.*font/pw
            # Compensate for the native pixel rounding of spectrum legend rows.
            y += .035*font/ph
        if page['role'].startswith('balancing.') and page['role']!='balancing.baryon_meson.activity':
            x=target['margins'][0]+.32*(1.-target['margins'][0])
        if page['role']=='multiplicity.composite':
            target['legend']=[.76,.705,.95,.825]
            y=.825-(.825-.705)/6.-.39*keyfont/ph
            font=18;step=1.30*font/ph;x=.45
        target['annotations']=[{'x':x,'y':y-i*step,'size':float(font),'text':line}
                               for i,line in enumerate(lines)]
        for panel in panels:
            if panel['id'].startswith('correlation.teaching.') and panel['id'].endswith('.identified'):
                ph=page['height']*(panel['geometry'][3]-panel['geometry'][1])
                pw=page['width']*(panel['geometry'][2]-panel['geometry'][0])
                keyfont=font+2
                top=1.-panel['margins'][3]-1.25*keyfont/ph
                right=1.-panel['margins'][1]-1.5*keyfont/pw
                panel['legend']=[right-4.6*keyfont/pw,
                    top-3.3*keyfont/ph,right,top]
            if page['role']=='balancing.baryon_meson.activity' and panel in row and panel is not target:
                ph=page['height']*(panel['geometry'][3]-panel['geometry'][1])
                pw=page['width']*(panel['geometry'][2]-panel['geometry'][0])
                top=1.-panel['margins'][3]-.65*(font+2)/ph
                panel['legend']=[.035,top-4.95*(font+2)/ph,
                                  .035+(font+2)*10.44/pw,top]
        if page['role']=='multiplicity.composite':
            for panel in page['panels']:
                if panel.get('reuse'):
                    panel['annotations'].append({'x':.24,'y':.85,'size':12.,'text':'MONASH percentile intervals'})
        if page['role']=='spectra.signed_heavy':
            page['title']=page['title'].removeprefix('G9 ').replace(' (1)','')
            for panel in panels:
                panel['x_title']=panel['x_title'].replace(' (1)','')
                panel['note']=''
            flags=[q for p in panels for z in p['series'] for q in z['points']]
            notes=[]
            if any(q['state']=='DRAW' and q['error'] is None for q in flags): notes.append('? = uncertainty unavailable')
            if any(q['state'] not in ('DRAW','LOG_NONPOSITIVE') for q in flags): notes.append('Gaps: undefined or unavailable bins')
            target['annotations'].extend({'x':.56,'y':.74-i*.045,'size':float(font-2),'text':text}
                                         for i,text in enumerate(notes))
        if page['role'].startswith('correlations.'):
            if not any(p['id'].startswith('correlation.teaching.') for p in panels):
                for panel in panels:
                    if panel['id'].startswith('correlation.compare.') and panel['y_title']:
                        panel['y_title']='R_{tune/MONASH}'
            if any(p['id'].startswith('correlation.teaching.') for p in panels):
                for panel in panels:
                    if panel['id'].endswith('.inclusive'):
                        for z in panel['series']: z['legend_label']=''
                        panel['y_title']=panel['y_title'].replace('N}_{OS}', 'N}^{#Sigma}_{OS}').replace('N}_{SS}', 'N}^{#Sigma}_{SS}')
        # Column identifiers remain independent of particle labels and tune keys.
        for index,panel in enumerate(sorted(row,key=lambda p:p['geometry'][0])):
            if panel['title'] and page['role']!='spectra.signed_heavy':
                panel['title']='('+chr(97+index)+') '+panel['title']


def apply_cold_page_style(pages, context):
    """The owner layout applies equally to preview and full science packets."""
    for page in pages:
        if page['role']=='multiplicity.composite':
            page['title']=context.target_analysis_caption
        elif page['role'] != 'spectra.signed_heavy':
            page['title']=''
            science=(getattr(context, 'pair_selection_caption', '')
                     if page['role'].startswith(('balancing.', 'correlations.'))
                     else '')
            teaching=any(panel['id'].startswith('correlation.teaching.') and
                         panel['uncertainty_display']=='CENTERS_ONLY'
                         for panel in page.get('panels', []))
            page['information']=(
                (science+'; ' if science else '')+
                CORRELATION_CENTER_ONLY_DISCLOSURE) if teaching else science
        page['scientific_header']=(
            'TEST_ONLY / SYNTHETIC / PARTIAL_SAMPLE'
            if context.numerics_schema == 'hadronization_projection_result_v4'
            and context.synthetic and context.campaign_state == 'PARTIAL_SAMPLE'
            else 'TEST_ONLY / SYNTHETIC' if context.synthetic else
            'TEST_ONLY PARTIAL_SAMPLE' if context.campaign_state=='PARTIAL_SAMPLE'
            else '')

def p1_uncertainty_display(synthetic):
    # Display the persisted one-standard-error envelope without recomputing
    # the estimator or drawing thousands of overlapping vertical bars.
    return 'DENSE_BAND'

def prelean_inset_geometry(relative, parent, width, height):
    """Map the original nested TPad to this canvas without stretching it.

    Pre-lean: 1800x1650 canvas, main pad height .69; inset .18,.07,.50,.38.
    Preserve its physical aspect when the surrounding current page is taller.
    """
    x0,y0,x1,y1=relative
    left,bottom,right,top=parent
    inset_bottom=bottom+y0*(top-bottom)
    inset_height=(y1-y0)*.69*(1650./1800.)*width/height*(right-left)
    return [left+x0*(right-left),inset_bottom,
            left+x1*(right-left),inset_bottom+inset_height]

CORRELATION_CENTER_ONLY_DISCLOSURE = (
    'Statistical errors omitted for display; K10 errors and covariance '
    'saved in ROOT')

def review_uncertainty_presentation(page):
    """Keep retained K10 errors distinct from errors drawn in a PDF."""
    role=page['role']
    active=[(panel,point) for panel in page['panels']
            for series in panel['series'] for point in series['points']
            if point['state']=='DRAW']
    if not any(point['error'] is not None and point['error']>0
               for _,point in active):
        return role+' lacks retained finite-MC error'
    teaching=[panel for panel in page['panels']
              if panel['id'].startswith('correlation.teaching.')]
    if teaching and any(panel['uncertainty_display']=='CENTERS_ONLY'
                        for panel in teaching):
        if not page['information'].endswith(
                CORRELATION_CENTER_ONLY_DISCLOSURE):
            return role+' centers-only teaching lacks visible SE disclosure'
        return None
    if any(panel['uncertainty_display']!='CENTERS_ONLY' and
           point['error'] is not None and point['error']>0
           for panel,point in active):
        return None
    if role=='multiplicity.composite' and any(
            'SE not drawn' in panel['note'] for panel in page['panels']):
        return None
    return role+' has neither drawn finite-MC errors nor a display disclosure'

def g9_science_caption(science, reference, numerics_schema):
    """Translate S's authenticated G9 selection and normalization into text."""
    current = numerics_schema == 'hadronization_projection_result_v4'
    legacy = numerics_schema == 'hadronization_projection_result_v3_g9_science'
    if not (current or legacy):
        raise ValueError('S G9 numerical schema differs')
    model = ('G9_direct_primary_selected_no_pt_floor_eta4' if current else
             'G9_direct_primary_selected_strict_pt0p15_eta4')
    denominator = ('weighted_all_origin_selected_final_same_signed_species_and_tune'
                   if current else
                   'weighted_selected_final_same_signed_species_and_tune')
    pt_flow = ('negative_underflow_rejected_overflow_in_denominator_and_output'
               if current else
               'underflow_and_overflow_in_denominator_and_output')
    if (science['model_id'] != model or
            science['status_low'] != 81 or science['status_high'] != 89 or
            science['source_family'] != 'kinematics' or
            science['final'] is not True or science['selected'] is not True or
            science['denominator'] != denominator or
            science['normalization'] !=
            'per_bin_probability_no_bin_width_division' or
            science['units'] != 'probability_per_bin' or
            science['ratio'] !=
            'same_bin_probability_over_reference_tune_probability' or
            science['pt_flow'] != pt_flow or
            science['eta_flow'] !=
            'no_materialized_flow_inclusive_upper_endpoint' or
            science['phi_flow'] !=
            'no_materialized_flow_inclusive_upper_endpoint' or
            science['axis_ids'] != ['pt', 'eta', 'phi']):
        raise ValueError('S G9 selection/normalization contract differs')
    pt, eta = science['pt'], science['eta']
    if ((current and (science.get('origin_scope') != 'ALL_ORIGINS' or
                      any(pt[key] is not None for key in
                          ('low', 'high', 'low_operator', 'high_operator')))) or
            (legacy and (pt['low_operator'] != 'GT' or
                         pt['high'] is not None)) or
            eta['low_operator'] != 'GE' or
            eta['high_operator'] != 'LE' or
            float.fromhex(eta['low']) != -float.fromhex(eta['high']) or
            (current and pt['domain'] != 'PHYSICAL') or
            pt['units'] != 'GeV'):
        raise ValueError('S G9 cut predicates differ')
    if current:
        cut = ('G9 direct final {}-{}, all origins, no #it{{p}}_{{T}} floor, '
               '|#eta| #leq {}; #it{{P}}_{{bin}}=#it{{W}}_{{bin}}/#it{{W}}_{{sel}} per species/tune (no bin-width divide)'
               .format(science['status_low'], science['status_high'],
                       format(float.fromhex(eta['high']), '.15g')))
    else:
        cut = ('G9 selected final (status {}-{}), #it{{p}}_{{T}} > {} GeV, '
               '|#eta| #leq {}; #it{{P}}_{{bin}} = #it{{W}}_{{bin}}/#it{{W}}_{{sel}} per species/tune (no bin-width divide)'
               .format(science['status_low'], science['status_high'],
                       format(float.fromhex(pt['low']), '.15g'),
                       format(float.fromhex(eta['high']), '.15g')))
    return cut, '#it{P}_{bin} / #it{P}_{bin,'+reference+'}', 'Probability / bin'

def cold_drawing_inputs(payload, config):
    """Adapt one S-validated numerical DTO to presentation fields only.

    The supplied metadata is part of the archived science payload.  This
    function never opens a campaign file, invokes a projector, or infers an
    unarchived category, support boundary, or particle identity.
    """
    resolved = payload["resolved"]
    if payload['schema'] not in (
            'hadronization_projection_result_v3_g9_science',
            'hadronization_projection_result_v4'):
        raise ValueError('S numerical ROOT lacks typed G9 science record')
    partial = partial_numerics(payload)
    if payload['schema'] == 'hadronization_projection_result_v4':
        checked_charm_recipe_binding(payload['request_echo']['scope'], config)
    g9_science = resolved['g9_science']
    order_records = resolved.get("category_order")
    support_records = resolved.get("observed_support")
    if not isinstance(order_records, list) or not isinstance(support_records, list):
        raise ValueError("S numerical ROOT lacks typed category/support records")
    category_orders = {}
    labels = {}
    for record in order_records:
        pdgs, captions = record["associate_pdgs"], record["labels"]
        if len(pdgs) != len(captions) or len(set(pdgs)) != len(pdgs):
            raise ValueError("numerical category order/label bijection differs")
        role = record["role_id"]
        trigger = str(record["trigger_pdg"])
        if trigger in category_orders.setdefault(role, {}):
            raise ValueError("duplicate numerical category order")
        category_orders[role][trigger] = [str(pdg) for pdg in pdgs]
        for pdg, caption in zip(pdgs, captions):
            if not isinstance(caption, str) or not caption:
                raise ValueError("empty numerical category label")
            previous = labels.setdefault(str(pdg), caption)
            if previous != caption:
                raise ValueError("contradictory numerical species label")
    request = payload["request_echo"]
    nch = next((axis for axis in request["axes"] if axis["id"] == "nch"), None)
    if nch is None:
        raise ValueError("P1 numerical axis is absent")
    support = [item for item in support_records
               if item["role_id"] == "multiplicity.composite" and
               item["axis_id"] == "nch" and item["status"] == "OBSERVED"]
    if not support:
        if not partial:
            raise ValueError("complete numerical P1 occupied support absent")
        occupied = None
    else:
        last = max(item["last_nonzero"] for item in support)
        if last is None or last + 1 >= len(nch["edges"]):
            raise ValueError("P1 occupied support bin index differs")
        positive_edges = [float.fromhex(edge) for edge in nch["edges"]
                          if float.fromhex(edge) > 0]
        if not positive_edges:
            raise ValueError("P1 axis has no positive inset domain")
        occupied = {"low": 0.,
                    "high": float.fromhex(nch["edges"][last + 1]),
                    "positive_low": positive_edges[0]}
    g9_pages = sorted({(g9_signed_species(point["key"]["curve"]),
                        point["key"]["curve"]["axis_id"])
                       for point in payload["points"]
                       if point["key"]["curve"]["role_id"] ==
                       "spectra.signed_heavy"})
    metadata = {"p1_occupied_support": occupied,
                "category_orders": category_orders,
                "species_labels": labels,
                "g9_pages": [{"pdg": pdg, "axis_id": axis}
                             for pdg, axis in g9_pages]}
    scope = request["scope"]
    tunes = scope["ordered_tunes"]
    reference_tune = scope["reference_tune"]
    if reference_tune not in tunes:
        raise ValueError("numerical reference tune is absent")
    profiles = payload["resolved"]["profiles"]
    # A/S fix the scientific profile in the archived request. Presentation
    # config cannot select or silently replace that profile.
    if len(profiles) != 1 or len(request["profiles"]) != 1 or \
            profiles[0]["id"] != request["profiles"][0]["id"]:
        raise ValueError("numerical profile selection is absent/ambiguous")
    profile = profiles[0]
    selected_profile = profile["id"]
    pair_selection_caption = checked_paper_pair_profile(
        payload, config, profile)
    rows = [row for row in typed_point_rows(payload)
            if row["profile"] in ("", selected_profile)]
    if len({row["semantic_id"] for row in rows}) != len(rows):
        raise ValueError("numerical point identity collision")
    classes = [{"id": item["id"],
                "integrated": item["kind"] == "INTEGRATED",
                "percentile_interval": [float.fromhex(value)
                                        for value in item["percentile_interval"]]
                if item["percentile_interval"] is not None else [0., 100.]}
               for item in request["classes"]]
    activity_ids = {row["activity_id"] for row in rows
                    if row["activity_id"]}
    if len(activity_ids) != 1:
        raise ValueError("numerical activity ID is absent/ambiguous")
    activity_id = next(iter(activity_ids))
    activity = request["activity"]
    boundary_activity_id = (activity['semantic_id']
                            if payload['schema'] ==
                            'hadronization_projection_result_v4'
                            else activity_id)
    boundaries = []
    requested_class_ids = [str(item["id"]) for item in classes]
    if len(set(requested_class_ids)) != len(requested_class_ids):
        raise ValueError("numerical class IDs are duplicated")
    for tune in tunes:
        entries = [item for item in payload["resolved"]["class_boundaries"]
                   if item["tune_id"] == tune and
                   item["activity_id"] == boundary_activity_id]
        by_class = {str(item["class_id"]): item for item in entries}
        if len(by_class) != len(entries):
            raise ValueError("duplicate numerical class boundary")
        if entries and set(by_class) != set(requested_class_ids):
            raise ValueError("numerical class boundary key set differs")
        if not entries and not partial:
            raise ValueError("complete numerical class boundaries absent")
        boundaries.append({"tune": tune, "activity_id": activity_id,
                           "classes": [{"id": class_id,
                                        "low": by_class[class_id]["actual_integer_low"],
                                        "high": by_class[class_id]["actual_integer_high"],
                                        "empty": by_class[class_id]["empty"]}
                                       for class_id in requested_class_ids
                                       if class_id in by_class]})
    pairs = [{"trigger_pdg": item["trigger_pdg"],
              "associate_pdg": item["associate_pdg"],
              "reference_meson_pdg": item["reference_meson_pdg"],
              "sector": item["sector"].lower(),
              "sign": -1 if item["sign"] == "OS" else 1}
             for item in scope["ordered_associate_pairs"]]
    provenance = payload["provenance"]
    synthetic = synthetic_provenance(payload)
    generator = {"name": provenance["generator_name"],
                 "version": provenance["generator_version"]}
    collision = {"beam": provenance["collision_system"],
                 "sqrt_s_gev": float.fromhex(provenance["energy_gev"])}
    selection = {"profiles": profiles,
                 "activities": [{"id": activity_id,
                                 "semantic_id": activity["semantic_id"],
                                 "eta_window": float.fromhex(activity["eta_window"])}],
                 "pair_acceptance": {"eta": {
                     "operator": "abs<=",
                     "value": float.fromhex(profile["trigger_eta"]["high"])}}}
    labels = metadata["species_labels"]
    # A missing display name is shown as its authenticated signed PDG number;
    # the renderer never invents a particle name from a local registry.
    for item in pairs:
        for key in ("trigger_pdg", "associate_pdg", "reference_meson_pdg"):
            pdg = item[key]
            labels.setdefault(str(pdg), "PDG " + str(pdg))
    for point in payload["points"]:
        curve = point["key"]["curve"]
        pdg = (g9_signed_species(curve)
               if curve["role_id"] == "spectra.signed_heavy"
               else curve["trigger_pdg"])
        if pdg is not None:
            labels.setdefault(str(pdg), "PDG " + str(pdg))
    if (not isinstance(labels, dict) or
            any(not isinstance(key, str) or not isinstance(value, str) or
                not value for key, value in labels.items())):
        raise ValueError("numerical species labels differ")
    presentation = {
        "scientific_provenance": {"generator": generator,
                                  "collision_system": collision},
        "selection_definitions": selection,
        "activity_boundaries": boundaries,
        "trigger_sectors": {str(item["trigger_pdg"]): item["sector"]
                            for item in pairs},
        "pairs": pairs,
        "correlations": [item for item in pairs
                         if item["sign"] == -1 and
                         abs(item["associate_pdg"]) ==
                         abs(item["reference_meson_pdg"])],
        "species_labels": labels,
    }
    campaign_state = payload["campaign_state"]
    if campaign_state not in ("FULL_ACCEPTED_CAMPAIGN", "PARTIAL_SAMPLE"):
        raise ValueError("numerical campaign state differs")
    event_count = sum(item["count"] for item in
                      request["sources"]["expected_events_by_tune"])
    materialization_by_key = {canonical(item['point_key']): item
                              for item in payload['materialization']}
    materialization_by_semantic_id = {
        point['semantic_id']: materialization_by_key[canonical(point['key'])]
        for point in payload['points']}
    context = SimpleNamespace(
        cold=True, typed=True, request_id=payload["request_sha256"],
        numerics_schema=payload['schema'],
        tunes=tunes, reference_tune=reference_tune,
        profile_id=selected_profile, profile_definition=profile,
        profile_caption=metadata.get("profile_caption", selected_profile),
        pair_selection_caption=pair_selection_caption,
        activity_id=activity_id, public_rows=rows,
        activity_selection=activity,
        materialization_by_semantic_id=materialization_by_semantic_id,
        classes=classes,
        block_ids=request["statistics"]["block_ids"],
        events=event_count,
        activity_threshold=float.fromhex(activity["pt"]["low"]),
        p1_occupied_support=metadata["p1_occupied_support"],
        category_orders=metadata["category_orders"],
        g9_pages=metadata["g9_pages"],
        g9_science=g9_science,
        axes=request["axes"],
        campaign_state=campaign_state,
        synthetic=synthetic,
        target_analysis_caption=target_analysis_caption(payload),
        sample_caption=sample_caption(payload),
        package_state=payload["package_state"],
        sampled_tunes=[item["tune_id"] for item in
                       request["sources"]["expected_events_by_tune"]])
    def role_family(role_id):
        if role_id.startswith("balancing."): return "balancing"
        if role_id.startswith("correlations."): return "correlations"
        if role_id.startswith(("kinematics.", "spectra.")): return "kinematics"
        if role_id.startswith("accounting."): return "sample_counts"
        if role_id == "multiplicity.composite": return "multiplicity"
        raise ValueError("unknown numerical plot role: "+role_id)
    roles = [{"id": item["role_id"],
              "family": role_family(item["role_id"])}
             for item in scope["roles"]
             if not item["role_id"].startswith("accounting.")]
    return context, {"request_id": payload["request_sha256"],
                     "roles": roles, "presentation": presentation}

def species_latex_label(pdg, value):
    """Return ROOT TLatex typography for an authenticated species label."""
    signed_identity = {
        '411':'#it{D}^{+}', '-411':'#it{D}^{-}',
        '421':'#it{D}^{0}', '-421':'#bar{#it{D}}^{0}',
        '431':'#it{D}_{s}^{+}', '-431':'#it{D}_{s}^{-}',
        '4122':'#it{#Lambda}_{c}^{+}',
        '-4122':'#bar{#it{#Lambda}}_{c}^{-}',
        '521':'#it{B}^{+}', '-521':'#it{B}^{-}',
        '511':'#it{B}^{0}', '-511':'#bar{#it{B}}^{0}',
        '531':'#it{B}_{s}^{0}', '-531':'#bar{#it{B}}_{s}^{0}',
        '541':'#it{B}_{c}^{+}', '-541':'#it{B}_{c}^{-}',
        '5122':'#it{#Lambda}_{b}^{0}',
        '-5122':'#bar{#it{#Lambda}}_{b}^{0}',
        '4112':'#it{#Sigma}_{c}^{0}', '-4112':'#bar{#it{#Sigma}}_{c}^{0}',
        '4212':'#it{#Sigma}_{c}^{+}', '-4212':'#bar{#it{#Sigma}}_{c}^{-}',
        '4222':'#it{#Sigma}_{c}^{++}', '-4222':'#bar{#it{#Sigma}}_{c}^{--}',
        '5112':'#it{#Sigma}_{b}^{-}', '-5112':'#bar{#it{#Sigma}}_{b}^{+}',
        '5212':'#it{#Sigma}_{b}^{0}', '-5212':'#bar{#it{#Sigma}}_{b}^{0}',
        '5222':'#it{#Sigma}_{b}^{+}', '-5222':'#bar{#it{#Sigma}}_{b}^{-}',
        '4132':'#it{#Xi}_{c}^{0}', '-4132':'#bar{#it{#Xi}}_{c}^{0}',
        '4232':'#it{#Xi}_{c}^{+}', '-4232':'#bar{#it{#Xi}}_{c}^{-}',
        '5132':'#it{#Xi}_{b}^{-}', '-5132':'#bar{#it{#Xi}}_{b}^{+}',
        '5232':'#it{#Xi}_{b}^{0}', '-5232':'#bar{#it{#Xi}}_{b}^{0}',
        '4312':"#it{#Xi}'_{c}^{0}", '-4312':"#bar{#it{#Xi}}'_{c}^{0}",
        '4322':"#it{#Xi}'_{c}^{+}", '-4322':"#bar{#it{#Xi}}'_{c}^{-}",
        '5312':"#it{#Xi}'_{b}^{-}", '-5312':"#bar{#it{#Xi}}'_{b}^{+}",
        '5322':"#it{#Xi}'_{b}^{0}", '-5322':"#bar{#it{#Xi}}'_{b}^{0}",
        '4332':'#it{#Omega}_{c}^{0}', '-4332':'#bar{#it{#Omega}}_{c}^{0}',
        '5332':'#it{#Omega}_{b}^{-}', '-5332':'#bar{#it{#Omega}}_{b}^{+}',
    }
    if str(pdg) in signed_identity:
        return signed_identity[str(pdg)]
    compact = {
        'Dplus': '#it{D}^{+}', 'Dminus': '#it{D}^{-}',
        'Dzero': '#it{D}^{0}', 'Dzerobar': '#bar{#it{D}}^{0}',
        'Dsplus': '#it{D}_{s}^{+}', 'Dsminus': '#it{D}_{s}^{-}',
        'Lambdacplus': '#it{#Lambda}_{c}^{+}',
        'Lambdacplusbar': '#bar{#it{#Lambda}}_{c}^{-}',
        'Bminus': '#it{B}^{-}', 'Bplus': '#it{B}^{+}',
        'Bzero': '#it{B}^{0}', 'Bzerobar': '#bar{#it{B}}^{0}',
        'Bszero': '#it{B}_{s}^{0}', 'Bszerobar': '#bar{#it{B}}_{s}^{0}',
        'Bcminus': '#it{B}_{c}^{-}', 'Bcplus': '#it{B}_{c}^{+}',
        'Lambdabzero': '#it{#Lambda}_{b}^{0}',
        'Lambdabzerobar': '#bar{#it{#Lambda}}_{b}^{0}',
    }
    return compact.get(value, value)


def reserve_spectrum_tune_key(pages):
    """Add display headroom where a spectrum would intersect its tune key."""
    for page in pages:
        if page['role'] != 'spectra.signed_heavy':
            continue
        panel = next(p for p in page['panels'] if p['id'] == 'g9.absolute')
        tunes = {s['tune'] for s in panel['series']}
        if not tunes:
            continue
        font = max(page['text_pixels'], math.ceil(9*page['width']/(18*72/2.54)))
        font += 2 if page['width'] > 1500 else 0
        width = page['width']*(panel['geometry'][2]-panel['geometry'][0])
        height = page['height']*(panel['geometry'][3]-panel['geometry'][1])
        left, right, bottom, top = panel['margins']
        key_width = font*(.62*max(map(len, tunes))+3.)/width
        x_fraction = (1-right-key_width-.975*font/width-left)/(1-left-right)
        xmin, xmax = panel['x_range']
        key_xmin = xmin+(xmax-xmin)*x_fraction
        occupied = []
        for series in panel['series']:
            for point in series['points']:
                if point['state'] != 'DRAW' or point['y'] is None:
                    continue
                xhigh = point.get('bin_high')
                if xhigh is None:
                    xhigh = point['display_x']
                if xhigh is not None and xhigh >= key_xmin:
                    occupied.append(point['y']+(point['error'] or 0.))
        if not occupied:
            continue
        fraction = (1.65*len(tunes)+1.3)*font/(height*(1-bottom-top))
        if fraction >= 1:
            raise ValueError('spectrum tune key exceeds the frame height')
        low, high = panel['y_range']
        required = (low*math.exp(math.log(max(occupied)/low)/(1-fraction))
                    if panel['log_y'] else low+(max(occupied)-low)/(1-fraction))
        panel['y_range'][1] = max(high, required)


def reserve_annotation_headroom(pages):
    """Reserve vertical display space only over the annotated x intervals."""
    for page in pages:
        if not page['role'].startswith(('balancing.', 'correlations.', 'spectra.signed_heavy')):
            continue
        panels=[p for p in page['panels'] if not p.get('reuse')]
        top=max(p['geometry'][3] for p in panels)
        row=[p for p in panels if p['geometry'][3]==top]
        required=max(p['y_range'][1] for p in row)
        for panel in row:
            pw=page['width']*(panel['geometry'][2]-panel['geometry'][0])
            ph=page['height']*(panel['geometry'][3]-panel['geometry'][1])
            font=max(page['text_pixels'],math.ceil(9*page['width']/(18*72/2.54)))
            left,right,bottom,margin_top=panel['margins']
            boxes=[]
            if panel['annotations']:
                boxes.append((min(a['x'] for a in panel['annotations']),
                              min(a['y'] for a in panel['annotations'])-.7*font/ph,
                              1.-right-.02))
            if panel['id'].endswith('.identified') or page['role']=='balancing.baryon_meson.activity' and not panel['annotations']:
                x,y,x2,_=panel['legend'];boxes.append((x,y-.7*font/ph,x2))
            elif panel is max(row,key=lambda p:p['geometry'][0]) and page['role'].startswith(('balancing.','correlations.')):
                keyfont=font+2
                correlation=page['role'].startswith('correlations.')
                x2=1.-right-(1.5 if correlation else .65)*keyfont/pw
                boxes.append((x2-10.44*keyfont/pw,
                    1.-margin_top-(4.95+(1.95 if correlation else 1.35))*keyfont/ph,x2))
            for x,y,x2 in boxes:
                fraction=(y-bottom)/(1.-margin_top-bottom)
                if fraction<=0:
                    raise ValueError('annotation exceeds frame height: '+page['filename'])
                xmin,xmax=panel['x_range']
                lo=xmin+(x-left)/(1.-left-right)*(xmax-xmin)
                hi=xmin+(x2-left)/(1.-left-right)*(xmax-xmin)
                values=[]
                for series in panel['series']:
                    for q in series['points']:
                        if q['state']!='DRAW' or q['y'] is None:continue
                        qlo=q.get('bin_low');qhi=q.get('bin_high')
                        if qlo is None:qlo=q['display_x']-.45
                        if qhi is None:qhi=q['display_x']+.45
                        if qlo<=hi and qhi>=lo:
                            values.append(q['y']+(q['error'] or 0.))
                if not values:continue
                low=panel['y_range'][0];peak=max(values)
                high=(low*math.exp(math.log(peak/low)/fraction)
                      if panel['log_y'] and peak>low else low+(peak-low)/fraction)
                required=max(required,high)
        # Keep equal scientific scales across columns and stacked tune rows.
        for panel in panels:
            if panel in row or (page['role'].startswith('balancing.') and panel['id'].startswith('upper.')):
                panel['y_range'][1]=required


def drawing_plan(projection, manifest, config):
    if not isinstance(projection, SimpleNamespace) or not projection.cold:
        raise ValueError("paper layout requires S-admitted cold numerics")
    context = projection
    if context.request_id != manifest["request_id"]:
        raise ValueError("projection/layout request identity differs")
    presentation=manifest["presentation"]
    def label(pdg):
        labels = presentation.get("species_labels", {})
        value = labels.get(str(pdg))
        if not isinstance(value, str) or not value:
            raise ValueError("S numerical species display label is absent: "+str(pdg))
        # This is typography only: the species identity and categorical order
        # remain the authenticated signed PDG and label supplied by S.
        return species_latex_label(pdg, value)
    threshold=context.activity_threshold
    provenance=presentation['scientific_provenance']
    header='{name} {version}, {beam}, #sqrt{{#it{{s}}}} = {energy} TeV'.format(
        **provenance['generator'],beam=provenance['collision_system']['beam'],
        energy=format(provenance['collision_system']['sqrt_s_gev']/1000.,'.15g'))
    classes=context.classes
    labels={str(c['id']):'{}-{}'.format(
        *(format(float(value),'.15g') for value in c['percentile_interval']))
        for c in classes}
    order=[str(c['id']) for c in reversed(classes) if not c['integrated']]
    styles={s['id']:s for s in config['style_identities']['tunes']}
    class_styles=resolved_class_styles(
        classes, config['style_identities']['class_line_patterns'])
    class_pattern_digest=sha_bytes(canonical(
        config['style_identities']['class_line_patterns']).encode('ascii'))
    categorical_dodge=config['layout']['categorical_tune_dodge']
    tunes=context.tunes
    reference_tune=context.reference_tune
    if any(tune not in styles for tune in tunes):
        raise ValueError('projection requests a tune without a presentation style')
    definitions=presentation['selection_definitions']
    pair_eta=definitions['pair_acceptance']['eta']
    profile_definition=context.profile_definition
    profile_caption=context.profile_caption
    blocks=len(context.block_ids)
    events=context.events
    base_information=(profile_caption+'; |#eta_{trig,assoc}| '
                      +('#leq ' if pair_eta['operator']=='abs<=' else
                        pair_eta['operator']+' ')
                      +format(pair_eta['value'],'.15g')+
                      '; finite-MC SE: #it{K}='+str(blocks)+
                      ', #it{N}_{evt,total}='+format(events,','))
    by_pdg={p:f for f,ps in config['families'].items() for p in ps}
    assigned={r['id']:[] for r in manifest['roles']}; exclusions=[]
    for r in context.public_rows:
        if not r['role_id']:
            exclusions.append((r['semantic_id'],'NON_NOMINAL_ROLE')); continue
        if (r['role_id'].startswith(('correlations.', 'balancing.')) and
                not r['trigger_pdg']):
            if not partial_numerics(context):
                raise ValueError('complete numerical point lacks a channel key')
            exclusions.append((r['semantic_id'], 'UNBOUND_TEST_CHANNEL'))
            continue
        if r['family'] == 'sample_counts':
            exclusions.append((r['semantic_id'], 'S_OWNS_TABLE_EXPORT'))
            continue
        if r['role_id'] not in assigned: raise ValueError('undeclared render role')
        _render_numbers(r); assigned[r['role_id']].append(r)
    pages=[]; padding=config['layout']['axis_padding_fraction']
    quantities=['os_minus_ss_per_trigger','ratio_to_reference_tune',
                'baryon_meson_reference_ratio','baryon_meson_ratio_to_reference_tune']
    ytitles={'os_minus_ss_per_trigger':'#it{Y} = (#it{N}_{OS}-#it{N}_{SS}) / #it{N}_{trig}',
             'ratio_to_reference_tune':'#it{Y} / #it{Y}_{'+reference_tune+'}',
             'baryon_meson_reference_ratio':'#it{Y}_{assoc} / #it{Y}_{ref}',
             'baryon_meson_ratio_to_reference_tune':'(#it{Y}_{assoc}/#it{Y}_{ref}) / '+reference_tune}
    for role,rows in sorted(assigned.items()):
        family=next(r['family'] for r in manifest['roles'] if r['id']==role)
        if family == 'kinematics':
            continue
        paper = config['presets']['paper_default']
        configured_charm = str(paper['trigger_pdgs'][0])
        if ((family in ('balancing', 'correlations') and
             role.endswith('charm')) or
            role == 'balancing.baryon_meson.activity'):
            science_charm = {r['trigger_pdg'] for r in rows
                             if r['trigger_pdg'] in ('411', '421')}
            if science_charm and configured_charm not in science_charm:
                raise ValueError('configured charm meson lacks S-owned '
                                 'science tuples: '+configured_charm)
        allowed_triggers = {str(value) for value in (
            paper['baryon_meson_trigger_pdgs']
            if role == 'balancing.baryon_meson.activity' else
            paper['trigger_pdgs'])}
        trigger_shown = [r for r in rows if r['trigger_pdg'] in
                         allowed_triggers] if family in ('balancing',
                         'correlations') else rows
        trigger_shown_ids = {r['semantic_id'] for r in trigger_shown}
        exclusions.extend((r['semantic_id'], 'PRESENTATION_TRIGGER_FILTER')
                          for r in rows if r['semantic_id'] not in
                          trigger_shown_ids)
        correlation_view = config['layout']['correlation_view']
        pair_sign_view = (family == 'correlations' and
                          correlation_view == 'monash_pair_sign')
        teaching_view = (family == 'correlations' and
                         correlation_view in ('monash_pair_sign',
                                              'monash_balance'))
        if family == 'correlations':
            unfiltered = trigger_shown
            if pair_sign_view:
                trigger_shown = [r for r in trigger_shown
                    if r['quantity'] in ('dphi_per_trigger',
                                         'dphi_density_per_trigger') and
                    ((r['component'] in ('OS', 'SS') and
                      r['associate_pdg'] == str(-int(r['trigger_pdg']))) or
                     (r['component'] == 'OS_MINUS_SS' and
                      r['associate_pdg'] == ''))]
            else:
                reference_pairs = {(str(p['trigger_pdg']),
                    str(p['associate_pdg'])) for p in presentation['pairs']
                    if p['sign'] == -1 and abs(p['associate_pdg']) ==
                    abs(p['reference_meson_pdg'])}
                trigger_shown = [r for r in trigger_shown
                    if (r['trigger_pdg'], r['associate_pdg']) in reference_pairs]
            selected_ids = {r['semantic_id'] for r in trigger_shown}
            exclusions.extend((r['semantic_id'], 'PRESENTATION_CORRELATION_SCOPE')
                              for r in unfiltered if r['semantic_id'] not in
                              selected_ids)
        if teaching_view:
            shown = [r for r in trigger_shown if r['tune'] == reference_tune and
                     not r['reference_tune']]
            shown_ids = {r['semantic_id'] for r in shown}
            exclusions.extend((r['semantic_id'], 'PRESENTATION_TUNE_FILTER')
                              for r in trigger_shown if r['semantic_id'] not in
                              shown_ids)
        else:
            shown = trigger_shown
        grouped={}
        for r in shown:
            key = ('correlation.teaching.{}.{}'.format(
                r['trigger_pdg'], 'inclusive' if r['associate_pdg'] == ''
                else 'identified') if pair_sign_view else
                'correlation.balance.{}.{}'.format(
                r['trigger_pdg'], 'lower' if r['component'] ==
                'OS_MINUS_SS' else 'upper') if teaching_view else
                _panel_key(r,by_pdg,presentation))
            grouped.setdefault(key,[]).append(r)
        triggers=sorted({r['trigger_pdg'] for r in shown if r['trigger_pdg']},key=lambda p:(abs(int(p)),int(p)<0))
        has_tune_ratios=checked_tune_ratio_layout(
            tunes, reference_tune, rows, role,
            partial=partial_numerics(context))
        if teaching_view:
            has_tune_ratios = False
        recipes=[]; width,height=1100,850
        title=''; information=base_information
        def add(name,geometry,**options): recipes.append((name,geometry,options))
        if family=='balancing' and role!='balancing.baryon_meson.activity':
            integrated='.integrated.' in role
            title=('Multiplicity-integrated' if integrated else 'Multiplicity-dependent')+' '+role.split('.')[-1]+' balancing'
            width,height=1900,1250
            for ti,t in enumerate(triggers):
                left=ti/len(triggers); right=(ti+1)/len(triggers)
                add('upper.'+t,[left,.30 if has_tune_ratios else 0.,right,.89],
                    title=label(t)+' trigger',x_title='',
                    y_title='#it{Y} = #frac{#it{N}_{OS} - #it{N}_{SS}}{#it{N}_{trig}}',categorical=True,
                    log_y=True,ratio=False,legend=False)
                if has_tune_ratios:
                    add('lower.'+t,[left,0.,right,.30],title='',
                        x_title='Associate species',
                        y_title=ytitles['ratio_to_reference_tune'],categorical=True,
                        log_y=False,ratio=True,legend=False)
                else:
                    recipes[-1][2]['x_title']='Associate species'
        elif role=='balancing.baryon_meson.activity':
            title='Balancing baryon / reference-meson ratio versus activity'
            width,height=1900,1250
            for sector_index,sector in enumerate(('charm','beauty')):
                sector_triggers=[t for t in triggers if presentation['trigger_sectors'][t]==sector]
                halves=('upper','lower') if has_tune_ratios else ('upper',)
                for half in halves:
                    for i,t in enumerate(sector_triggers):
                        left=sector_index*.5+i*.5/max(1,len(sector_triggers))
                        right=sector_index*.5+(i+1)*.5/max(1,len(sector_triggers))
                        name='.'.join((half,sector,t)); members=grouped.get(name,[])
                        exact_ratio_title = exact_particle_ratio_title(
                            members, label)
                        add(name,[left,.32 if half=='upper' and has_tune_ratios else 0.,right,
                                  .89 if half=='upper' else .32],
                            title=(label(t)+' trigger: '+exact_ratio_title
                                   if half=='upper' else ''),
                            x_title='' if half=='upper' else
                                'Multiplicity Percentile Interval (%)',
                            y_title=('#it{Y}_{baryon}/#it{Y}_{meson}'
                                     if half=='upper' else 'TUNE/MONASH'),
                            log_y=half=='upper',ratio=half=='lower',legend=False)
        elif role=='multiplicity.composite':
            title=''
            activity=next(item for item in definitions['activities']
                          if item['id']==context.activity_id)
            selection=context.activity_selection
            information=activity_proxy_caption(
                selection, threshold, activity['eta_window'])
            # Retain the pre-lean portrait-like hierarchy: a dominant log-y
            # spectrum, a compact ratio pad and an embedded percentile inset.
            # The numerical archive retains all 4096 bins.  The paper page is
            # later restricted to the reference-tune occupied range so rare
            # single-event bins in another tune do not flatten the comparison.
            width,height=1050,1360
            add('upper.distribution',[0.,.26 if has_tune_ratios else 0.,1.,.98],
                title='',x_title='' if has_tune_ratios else 'Multiplicity #it{N}_{ch}',
                y_title='Normalized event counts',log_y=True,legend=True)
            if has_tune_ratios:
                add('lower.ratio',[0.,0.,1.,.26],title='',x_title='Multiplicity #it{N}_{ch}',y_title='TUNE/'+reference_tune,ratio=True)
            # Original nested-pad placement, retaining its physical aspect.
            add('inset.monash_boundaries',
                prelean_inset_geometry(config['layout']['p1_inset_geometry'],
                    [0.,.26 if has_tune_ratios else 0.,1.,.98],width,height),
                title='',x_title='Multiplicity #it{N}_{ch}',
                y_title='Normalized event counts',inset=True)
        elif family=='correlations':
            sector=role.split('.')[-1]
            title=(('' if pair_sign_view else 'MONASH balance' if teaching_view else
                    'All-tune' if len(tunes)>1 else tunes[0])+' '+sector+
                   ' angular correlations')
            information=(base_information+
                         '; #Delta#varphi = #varphi_{trig}-#varphi_{assoc}')
            if pair_sign_view:
                title=''
                information=(base_information+'; '+
                             CORRELATION_CENTER_ONLY_DISCLOSURE)
            width,height=1900,2600 if has_tune_ratios else 1850
            paper_triggers=[str(value) for value in
                            config['presets']['paper_default']['trigger_pdgs']
                            if presentation['trigger_sectors'][str(value)]==sector]
            for index,trigger in enumerate(paper_triggers):
                left=index/len(paper_triggers);right=(index+1)/len(paper_triggers)
                partners=correlation_reference_partners(
                    presentation['pairs'], trigger)
                if pair_sign_view:
                    add('correlation.teaching.'+trigger+'.identified',
                        [left,.48,right,.97],
                        title=label(trigger)+' trigger (MONASH)',x_title='',
                        y_title=correlation_y_title(shown),
                        log_y=True,legend=True)
                    add('correlation.teaching.'+trigger+'.inclusive',
                        [left,.05,right,.48],title='',
                        x_title='#Delta#varphi (rad)',
                        y_title=correlation_y_title(shown, 'OS_MINUS_SS'),
                        legend=True)
                    continue
                if teaching_view:
                    add('correlation.balance.'+trigger+'.upper',
                        [left,.45,right,.89],
                        title='MONASH '+label(trigger)+' trigger',
                        x_title='',y_title=correlation_y_title(shown),
                        legend=True)
                    add('correlation.balance.'+trigger+'.lower',
                        [left,.08,right,.45],title='',
                        x_title='#Delta#varphi (rad)',
                        y_title=correlation_y_title(shown, 'OS_MINUS_SS'),legend=False)
                    continue
                if has_tune_ratios:
                    geometry={
                        'OS': ((.73,.89),(.62,.72)),
                        'SS': ((.45,.61),(.34,.44)),
                        'OS_MINUS_SS': ((.17,.33),(.04,.16)),
                    }
                else:
                    geometry={
                        'OS': ((.64,.89),None),
                        'SS': ((.36,.61),None),
                        'OS_MINUS_SS': ((.08,.33),None),
                    }
                for component,(main_range,compare_range) in geometry.items():
                    caption=component.replace('OS_MINUS_SS','OS - SS')
                    caption_title=(label(trigger)+' trigger, OS - SS'
                                   if component=='OS_MINUS_SS' else
                                   label(trigger)+' trigger #rightarrow '+
                                   label(partners[component])+', '+component)
                    add('correlation.main.'+trigger+'.'+component,
                        [left,main_range[0],right,main_range[1]],
                        title=caption_title,
                        x_title='' if component!='OS_MINUS_SS' or
                            has_tune_ratios else
                            '#Delta#varphi (rad)',
                        y_title=correlation_y_title(shown, component),legend=False)
                    if compare_range:
                        add('correlation.compare.'+trigger+'.'+component,
                            [left,compare_range[0],right,compare_range[1]],
                            title='',
                            x_title='#Delta#varphi (rad)'
                                if component=='OS_MINUS_SS' else '',
                            y_title=caption+' / '+reference_tune,
                            ratio=True,legend=False)
        if not recipes:
            add('unavailable',[0.,0.,1.,.88],title='Unavailable',x_title='Bin coordinate',y_title='Value')
        header_bottom=.99 if role=='multiplicity.composite' or pair_sign_view else .89
        page={'role':role,'family':family,'page_index':1,'page_count':1,'filename':canonical_page_name(role),
              'text_pixels':config['layout']['text_pixel_size'],'title':title,'information':information,
              'scientific_header':header,
              'style_header':'class_patterns_sha256='+class_pattern_digest,
              'header_bottom':header_bottom,'width':width,'height':height,'panels':[]}
        for name,geometry,options in recipes:
            members=grouped.get(name,[]); groups={}
            present_species={r['associate_pdg'] for r in members
                             if r['associate_pdg']}
            if (family == 'balancing' and
                    role != 'balancing.baryon_meson.activity' and
                    getattr(context, 'cold', False)):
                trigger_key=name.rsplit('.',1)[-1]
                declared=getattr(context, 'category_orders', {}).get(
                    role, {}).get(trigger_key)
                species=checked_category_order(
                    declared, present_species,
                    partial_numerics(context),
                    role, trigger_key)
                species=species_display_order(species)
            else:
                species=(species_display_order(present_species)
                         if options.get('categorical') else
                         sorted(present_species,key=lambda p:abs(int(p))))
            for r in members:
                ident=_series_identity(r);key='|'.join(ident.values())
                groups.setdefault(key,[]).append(r)
            series=[]
            extreme_ids=set(selected_extreme_class_ids(classes))
            for key,values in sorted(groups.items(),key=lambda kv:(
                    kv[1][0]['class_id'] in extreme_ids,
                    tunes.index(kv[1][0]['tune']),
                    int(kv[1][0]['class_id'] or 0),kv[0])):
                ident=_series_identity(values[0]); tune=ident['tune'];cl=ident.get('class_id','')
                points=[]
                for r in values:
                    v=_render_numbers(r); low,high=v['bin_low'],v['bin_high']; sl,sh=low,high
                    if family=='balancing':
                        base=float((species.index(r['associate_pdg']) if options.get('categorical') else order.index(r['class_id']))+1)
                        display_class=(r['class_id'] if role==
                            'balancing.baryon_meson.activity' else cl)
                        scientific_x=base
                        x=categorical_display_x(
                            base,role,display_class,tune,tunes,order,
                            categorical_dodge, bool(r['reference_tune']))
                    else:
                        if family=='kinematics' and role.endswith('.pt') and sl is not None: sl=max(sl,threshold)
                        x=None if sl is None or sh is None or sl>=sh else (sl+sh)/2
                        scientific_x=x
                    state='FLOW_BIN' if family=='kinematics' and low is None else 'EMPTY_SUPPORT' if x is None else 'MISSING_VALUE' if v['value'] is None else 'DRAW'
                    points.append({'semantic_id':r['semantic_id'],'bin':int(r['bin_index']) if r['bin_index'] else -1,
                        'scientific_x':scientific_x,'display_x':x,
                        'x':x,'y':v['value'],'error':v['finite_mc_error'],
                        'bin_low':low,'bin_high':high,'support_low':sl,
                        'support_high':sh,'class_id':r['class_id'],
                        'value_status':r['value_status'],
                        'uncertainty_status':r['uncertainty_status'],
                        'reasons':r['reasons'],'state':state})
                points.sort(key=lambda q:(q['x'] is None,q['x'] or 0,q['semantic_id']))
                class_series=family=='balancing' and '.activity.' in role
                legend_label=labels[cl]+'%' if class_series and cl else tune
                line_style=class_styles.get(cl, 1)
                if family=='correlations':
                    component=ident['component']
                    line_style={'OS':1,'SS':2,'OS_MINUS_SS':7}[component]
                    legend_label=((label(int(ident['trigger_pdg']))+
                                   ' - '+label(-int(ident['trigger_pdg'])
                                   if component=='OS' else
                                   int(ident['trigger_pdg']))
                                   if ident['associate_pdg'] else
                                   ({'OS':'HF opposite sign (OS)',
                                     'SS':'HF same sign (SS)',
                                     'OS_MINUS_SS':'OS - SS'}[component]))
                                  if pair_sign_view else
                                  component if teaching_view else tune)
                if role=='balancing.baryon_meson.activity':
                    line_style=1+species.index(ident['associate_pdg'])
                    legend_label=label(ident['associate_pdg'])+' / '+label(ident['reference_pdg'])
                series.append({'key':key,'identity':ident,'tune':tune,'class_id':cl,
                    'color':({'OS':'#000000','SS':'#000000',
                              'OS_MINUS_SS':'#000000'}[ident['component']]
                             if pair_sign_view else styles[tune]['color']),
                    'marker':('open_circle' if pair_sign_view and ident['component']=='SS' else styles[tune]['marker']),
                    'line_style':(7 if pair_sign_view and ident['component']=='SS' else line_style),'label':legend_label,
                    'emphasis':activity_emphasis(role, cl, classes),
                    'legend_label':legend_label if options.get('legend') and (role!='balancing.baryon_meson.activity' or tune==reference_tune) else '',
                    'draw_mode':'histogram' if family in {'correlations','kinematics','multiplicity'} else 'categories' if options.get('categorical') or role=='balancing.baryon_meson.activity' else 'curve','points':points})
            valid=[q for s in series for q in s['points'] if q['state']=='DRAW']
            log_y=options.get('log_y',False)
            signed_linear=family=='balancing' and any(
                q['y']-(q['error'] or 0)<=0 for q in valid)
            if signed_linear: log_y=False
            bounds=[z for q in valid for z in (q['y'],q['y']-(q['error'] or 0),q['y']+(q['error'] or 0))]
            if options.get('ratio'): bounds.append(1.)
            yr=_padded_range(bounds,padding,log_y)
            xs=[z for q in valid for z in (q['support_low'],q['support_high']) if z is not None]
            xr=[min(xs),max(xs)] if xs else [0.,1.]; ticks=[];note=''
            if family=='balancing' and name!='unavailable':
                tick_labels=[label(p) for p in species] if options.get('categorical') else [labels[c] for c in order]
                xr=[.5,len(tick_labels)+.5] if tick_labels else [.5,1.5]
                # Shared categorical coordinates appear once, below the lower
                # tune-comparison pad; duplicating them cuts into its title.
                if not (has_tune_ratios and name.startswith('upper.')):
                    ticks=[{'x':float(i+1),'label':label}
                           for i,label in enumerate(tick_labels)]
            elif name=='upper.distribution':
                occupied = getattr(context, "p1_occupied_support", None)
                if occupied is None and not partial_numerics(context):
                    raise ValueError("S numerical ROOT lacks authenticated P1 occupied support")
                if (occupied is not None and
                        occupied['high'] <= occupied['positive_low'] and
                        not partial_numerics(context)):
                    raise ValueError('complete numerical P1 positive support absent')
                xr=(checked_p1_occupied_support(occupied, series)[0]
                    if occupied is not None else [0.,1.])
                visible=[q for q in valid if q['x'] is not None and xr[0]<=q['x']<=xr[1]]
                yr=_padded_range([z for q in visible for z in (q['y'],q['y']-(q['error'] or 0),q['y']+(q['error'] or 0))],.10,log_y)
                note='Finite-MC SE band; full bin errors saved in ROOT'
                positive=[q['y'] for q in visible if q['y']>0]
                if log_y and positive:
                    # One decade below the smallest positive visible center;
                    # nearly cancelling lower errors must not set a log floor.
                    yr[0]=max(yr[0],min(positive)/10.)
                    # The paper axis shows the full logarithmic count scale.
                    # Extend farther for a future sample with rarer occupied
                    # bins instead of clipping its authenticated support.
                    # Leave the 10^-8 tick/label clear of the ratio-pad seam.
                    yr[0]=min(yr[0],3e-9)
                    yr[1]=max(yr[1],1.)
                    # The exact errors also remain in ROOT/drawing record.
            if (family=='correlations' and options.get('x_title')) or (family=='kinematics' and role.endswith('.phi')):
                ticks=[{'x':value,'label':label} for value,label in
                       [(-math.pi,'-#pi'),(-math.pi/2,'-#pi/2'),(0.,'0'),
                        (math.pi/2,'#pi/2'),(math.pi,'#pi'),(3*math.pi/2,'3#pi/2')]
                       if xr[0]-1e-12<=value<=xr[1]+1e-12]
            if log_y:
                for q in valid:
                    if q['y']<=0:q['state']='LOG_NONPOSITIVE'
            if signed_linear:
                note='signed y uses linear scale'
            missing=[q for s in series for q in s['points']
                     if q['state']!='DRAW']
            if missing:
                status_note='{} missing (#times)'.format(len(missing))
                if name != 'upper.distribution':
                    note=(note+'; ' if note else '')+status_note
                else:
                    note+='; #times = unavailable'
            state_keys=[]
            if any(q['uncertainty_status']=='AVAILABLE_ZERO_DISPERSION'
                   for q in valid):
                state_keys.append('exact-zero SE saved in ROOT')
            if any(q['error'] is None for q in valid):
                state_keys.append('? = withheld SE')
            if state_keys:
                note=(note+'; ' if note else '')+'; '.join(state_keys)
            note=p1_ratio_uncertainty_note(role,name,valid,note)
            if family=='balancing' and name.startswith('lower.'):
                # The signed zero guide and the upper-pad note already carry
                # this explanation; status crosses show missing points. A
                # second footer collides with the categorical x-title.
                note=''
            # The page information line explains withheld error bars; a
            # second full sentence here would be cut by narrow facet pads.
            small=family=='balancing'
            margins=[.20,.035,.22,.17] if small else [.14,.04,.16,.10]
            legend=[.24,.68,.96,.82] if small else [.59,.69,.95,.85]
            if small and has_tune_ratios and name.startswith('upper.'):
                margins=[.20,.035,.10,.17]
            if small and has_tune_ratios and name.startswith('lower.'):
                margins=[.20,.035,.43,.17]
            if role=='balancing.baryon_meson.activity':
                # The panel-level particle-ratio key is intentionally absent;
                # keep only enough headroom for the trigger title itself.
                margins=[.20,.035,.32,.10]; legend=[.23,.80,.98,.91]
            if family=='correlations':
                margins=[.17,.04,
                         .29 if options.get('x_title') else .13,
                         .10]
                legend=[.48,.63,.96,.93]
                if pair_sign_view:
                    margins[3]=.22
                if teaching_view and name.endswith('.upper'):
                    legend=[.62,.91,.96,.98]
                if pair_sign_view and name.endswith('.identified'):
                    legend=[.20,.62,.66,.75]
                if pair_sign_view and name.endswith('.inclusive'):
                    legend=[.20,.63,.70,.76]
            if name=='upper.distribution':
                margins=[.16,.045,.0,.12]
                legend=[.76,.750,.95,.870]
            if name=='lower.ratio': margins=[.16,.045,.34,.0]
            if valid:
                status='AVAILABLE'
            else:
                status, note = typed_panel_status(context, members)
                note = compact_paper_status_note(status, note)
                if family=='balancing' and name.startswith('lower.'):
                    # The comparison pad is too shallow for both status and
                    # cause text beside categorical labels. Its point codes
                    # remain exact in the ROOT and drawing record.
                    note=''
            panel={'id':name,'status':status,'log_y':log_y,'log_x':False,'geometry':geometry,
                   'x_range':xr,'y_range':yr,'title':options.get('title',''),'x_title':options['x_title'],'y_title':options['y_title'],
                   'note':note,'series':series,'guides':[],'ticks':ticks,'margins':margins,'legend':legend,'reuse':None,
                   'category_dividers':(
                       config['layout']['activity_category_dividers']
                       if role.startswith('balancing.') else True),
                   'uncertainty_display':p1_uncertainty_display(context.synthetic)
                       if role=='multiplicity.composite' else
                       'STANDARD'}
            if options.get('ratio'):
                panel['guides'].append({'id':'unity','x_low':xr[0],'x_high':xr[1],'y_low':1.,'y_high':1.,'color':'#777777','line_style':10,'label':''})
            if signed_linear:
                panel['guides'].append({'id':'signed_zero','x_low':xr[0],
                    'x_high':xr[1],'y_low':0.,'y_high':0.,
                    'color':'#777777','line_style':7,'label':''})
            page['panels'].append(panel)
        if family == 'correlations' and shown:
            axis_ids = {r['axis'] for r in shown}
            if len(axis_ids) != 1:
                raise ValueError('correlation axis is ambiguous')
            axis = next((item for item in context.axes if item['id'] in
                         axis_ids), None)
            if axis is None or len(axis['edges']) < 2:
                raise ValueError('correlation axis is absent')
            domain = [float.fromhex(axis['edges'][0]),
                      float.fromhex(axis['edges'][-1])]
            for panel in page['panels']:
                panel['x_range'] = domain[:]
        if role.startswith('balancing.activity.'):
            for panel in page['panels']:
                panel['geometry'][1] *= .79/.90
                panel['geometry'][3] *= .79/.90
        pages.append(page)
    mult={p['id']:p for page in pages if page['role']=='multiplicity.composite' for p in page['panels']}
    if mult:
        top=mult['upper.distribution']; inset=mult['inset.monash_boundaries']
        # Use the complete populated reference-tune range for the shared
        # linear paper axis. Other tunes retain their complete 4096-bin
        # numerical distributions in ROOT, including farther-tail entries.
        monash_series=[series for series in top['series']
                       if series['tune']==reference_tune]
        top['x_range'][1]=p1_reference_display_high(top['series'], reference_tune)
        active_bounds=[b for activity in presentation['activity_boundaries']
                       if activity['activity_id']==context.activity_id and
                       activity['tune']==reference_tune
                       for b in activity['classes'] if not b['empty']]
        if active_bounds:
            if any(b['low'] is None or b['high'] is None for b in active_bounds):
                raise ValueError('typed P1 class interval lacks an edge')
            rightmost_low=max(b['low'] for b in active_bounds)
            if rightmost_low >= top['x_range'][1]:
                raise ValueError('P1 reference classes exceed display support')
        lower=mult.get('lower.ratio')
        if lower:
            lower['x_range']=top['x_range'][:]
            lower['guides'][0].update(x_low=top['x_range'][0],x_high=top['x_range'][1])
        occupied = getattr(context, "p1_occupied_support", None)
        inset.update(reuse={'panel':'upper.distribution','tune':reference_tune},
            status=top['status'],
            x_range=[1.0,top['x_range'][1]],
            y_range=top['y_range'][:],log_y=True, log_x=True,
            margins=[.18,.065,.25,.20],
            uncertainty_display='DENSE_BAND',
            x_title='Multiplicity #it{N}_{ch}')
        if (occupied is not None and
                occupied['high'] <= occupied['positive_low']):
            inset['status']='NOT_MATERIALIZED'
            inset['note']='No positive occupied #it{N}_{ch} bin in partial sample'
        for activity in presentation['activity_boundaries']:
            if activity['activity_id'] != context.activity_id:
                continue
            tune=activity['tune']
            if tune != reference_tune:
                continue
            for b in activity['classes']:
                class_id = b['id']
                if class_id not in order or b['empty']:
                    continue
                if b['low'] is None:
                    raise ValueError('nonempty numerical class boundary lacks low edge')
                if b['high'] is None or b['high'] < b['low']:
                    raise ValueError('typed P1 class interval has no inclusive upper edge')
                boundary = float(b['low'])
                guide = {
                    'id':'class.'+tune+'.'+class_id,
                    'x_low':boundary,'x_high':float(b['high']+1),
                    'color':styles[tune]['color'],
                    'line_style':class_styles[class_id],
                }
                class_definition=labels[class_id]+'%'
                inset['guides'].append({
                    'id':guide['id'],
                    'x_low':guide['x_low'],'x_high':guide['x_high'],
                    'y_low':inset['y_range'][0],
                    'y_high':inset['y_range'][1],
                    'color':'#666666','line_style':2,
                    'label':class_definition})
    if mult:
        inset['note']=''
        inset['ticks']=[]
        inset_values=[point['y'] for series in monash_series for point in series['points']
                      if point['state']=='DRAW' and point['display_x'] is not None
                      and inset['x_range'][0]<=point['display_x']<=inset['x_range'][1]
                      and point['y']>0]
        if inset_values:
            low=max(min(inset_values)*.5,1e-300)
            inset['y_range']=[low,max(max(inset_values)*3.,low*10.)]
        for guide in inset['guides']:
            guide['y_low']=inset['y_range'][0]
            guide['y_high']=inset['y_range'][1]
    focused = focused_extreme_pages(
        pages, context, config['layout']['axis_padding_fraction'])
    tune_order = [item['id'] for item in
                  config['style_identities']['tunes']]
    pages = tune_separated_activity_pages(pages, tune_order)
    pages.extend(tune_separated_activity_pages(focused, tune_order))
    pages.append(tune_separated_baryon_meson_page(pages, tune_order))
    maximum=config['layout']['maximum_panels_per_page']
    if maximum < 6:
        paginated=[]
        for page in pages:
            panels=page['panels']; count=(len(panels)+maximum-1)//maximum
            for index in range(count):
                part=dict(page, page_index=index+1, page_count=count,
                          filename=canonical_page_name(page['role'],index+1,count),
                          panels=panels[index*maximum:(index+1)*maximum])
                for pi,panel in enumerate(part['panels']):
                    panel['geometry']=[pi/len(part['panels']),0.,(pi+1)/len(part['panels']),.90]
                paginated.append(part)
        pages=paginated
    if getattr(context, 'cold', False) and 'spectra.signed_heavy' in assigned:
        pages.extend(g9_drawing_pages(
            context, assigned['spectra.signed_heavy'], config,
            header, base_information, presentation['species_labels']))
    join_ratio_pads(pages)
    synchronize_paired_y_ranges(pages)
    apply_display_limits(pages)
    for page in pages:
        if page['role'].startswith('correlations.'):
            for panel in page['panels']:
                if panel['geometry'][0]==0:
                    panel['margins'][0] += .05
    join_paired_columns(pages)
    if getattr(context, 'cold', False):
        apply_cold_page_style(pages,context)
        add_publication_captions(pages,context)
    reserve_spectrum_tune_key(pages)
    reserve_annotation_headroom(pages)
    synchronize_paired_y_ranges(pages)
    return {'schema':DRAWING_SCHEMA,'request_id':manifest['request_id'],'pages':pages,'exclusions':sorted(exclusions)}

def g9_drawing_pages(context, rows, config, header, information, labels):
    """Lay out saved signed-species spectra; every number comes from S rows."""
    information, ratio_title, absolute_title = g9_science_caption(
        context.g9_science, context.reference_tune, context.numerics_schema)
    axes = {axis['id']: axis for axis in context.axes}
    tunes = context.tunes
    reference = context.reference_tune
    styles = {style['id']: style for style in config['style_identities']['tunes']}
    pattern_digest = sha_bytes(canonical(
        config['style_identities']['class_line_patterns']).encode('ascii'))
    pages = []
    seen = set()
    for item in context.g9_pages:
        pdg, axis_id = item['pdg'], item['axis_id']
        if (not isinstance(pdg, int) or axis_id not in axes or
                (pdg, axis_id) in seen):
            raise ValueError('G9 signed-species/axis page domain differs')
        seen.add((pdg, axis_id))
        axis = axes[axis_id]
        members = [row for row in rows if row['associate_pdg'] == str(pdg)
                   and row['axis'] == axis_id]
        if not members and not partial_numerics(context):
            raise ValueError('complete numerical G9 page has no points')
        regular_edges = [float.fromhex(edge) for edge in axis['edges']]
        if len(regular_edges) < 2:
            raise ValueError('G9 numerical axis has no regular support')
        drawn_support = [(float(row['bin_low']), float(row['bin_high']))
                         for row in members
                         if row['flow'] == 'REGULAR' and row['value'] and
                         float(row['value']) != 0 and row['bin_low'] and
                         row['bin_high']]
        if drawn_support:
            x_low = min(low for low, _ in drawn_support)
            x_high = max(high for _, high in drawn_support)
        else:
            x_low, x_high = regular_edges[0], regular_edges[-1]
        if x_low >= x_high:
            raise ValueError('G9 display axis is reversed')
        variable = axis['variable'].rsplit('_', 1)[-1]
        if variable in ('eta', 'phi'):
            # These bounded scientific axes must not collapse to the few
            # occupied bins of a sparse partial sample.
            x_low, x_high = regular_edges[0], regular_edges[-1]
        no_floor_pt = (variable == 'pt' and
                       context.numerics_schema ==
                       'hadronization_projection_result_v4')
        log_x = variable == 'pt' and not no_floor_pt
        if no_floor_pt:
            if regular_edges[0] != 0. or regular_edges[1] != .5:
                raise ValueError('G9 no-floor first pT bin support differs')
            x_low = 0.
            x_high = max(x_high, regular_edges[1])
        if log_x:
            # The authenticated pT axis can span several orders of magnitude.
            # A positive center keeps the first regular bin visible; only its
            # drawn left edge is clipped by the renderer at the frame edge.
            positive_centers = [(low + high) / 2 for low, high in drawn_support
                                if (low + high) / 2 > 0]
            if not positive_centers:
                positive_centers = [(low + high) / 2
                                    for low, high in zip(regular_edges,
                                                         regular_edges[1:])
                                    if (low + high) / 2 > 0]
            x_low = min(positive_centers)
        x_title = ({'pt':'#it{p}_{T}', 'eta':'#eta', 'phi':'#varphi'}.get(
            variable, variable) +
            (' (' + axis['units'] + ')' if axis['units'] else ''))
        filename = 'G9_{}_{}.pdf'.format(pdg, axis_id)
        species_label = species_latex_label(
            pdg, labels.get(str(pdg), 'PDG '+str(pdg)))
        if not species_label.strip():
            raise ValueError('G9 signed-species label is empty')
        page = {
            'role':'spectra.signed_heavy', 'family':'kinematics',
            'page_index':1, 'page_count':1, 'filename':filename,
            'text_pixels':config['layout']['text_pixel_size'],
            'title':'G9 '+species_label+' '+x_title,
            'information':information,
            'scientific_header':header,
            'style_header':'class_patterns_sha256='+pattern_digest,
            'header_bottom':.99, 'width':1100, 'height':1200,
            'panels':[],
        }
        for ratio in (False, True):
            selected = [row for row in members
                        if bool(row['reference_tune']) == ratio]
            units = {row['units'] for row in selected if row['units']}
            if len(units) > 1:
                raise ValueError('G9 panel has incompatible saved ordinate units')
            y_unit = next(iter(units), '')
            groups = {}
            for row in selected:
                groups.setdefault(row['tune'], []).append(row)
            series = []
            for tune in tunes:
                if tune not in groups:
                    continue
                points = []
                for row in groups[tune]:
                    values = _render_numbers(row)
                    flow = row['flow']
                    low, high = values['bin_low'], values['bin_high']
                    x = ((low + high) / 2 if low is not None and
                         high is not None and low < high else None)
                    state = ('FLOW_BIN' if flow != 'REGULAR' else
                             'EMPTY_SUPPORT' if x is None else
                             'MISSING_VALUE' if values['value'] is None else
                             'DRAW')
                    points.append({
                        'semantic_id':row['semantic_id'],
                        'bin':int(row['bin_index']) if row['bin_index'] else -1,
                        'scientific_x':x, 'display_x':x, 'x':x,
                        'y':values['value'], 'error':values['finite_mc_error'],
                        'bin_low':low, 'bin_high':high,
                        'support_low':low, 'support_high':high,
                        'class_id':row['class_id'],
                        'value_status':row['value_status'],
                        'uncertainty_status':row['uncertainty_status'],
                        'reasons':row['reasons'], 'state':state,
                    })
                points.sort(key=lambda point:(point['x'] is None,
                                               point['x'] or 0,
                                               point['semantic_id']))
                style = styles[tune]
                series.append({
                    'key':'G9|{}|{}|{}|{}'.format(pdg,axis_id,
                                                 'ratio' if ratio else 'absolute',
                                                 tune),
                    'identity':{'pdg':pdg, 'axis':axis_id, 'tune':tune,
                                'ratio':ratio},
                    'tune':tune, 'class_id':'', 'color':style['color'],
                    'marker':style['marker'], 'line_style':1,
                    'emphasis':'NORMAL',
                    'label':tune, 'legend_label':'' if ratio else tune,
                    'draw_mode':'histogram', 'points':points,
                })
            valid = [point for item in series for point in item['points']
                     if point['state'] == 'DRAW' and point['y'] is not None]
            y_values = [value for point in valid
                        for value in (point['y'],
                                      point['y']-(point['error'] or 0),
                                      point['y']+(point['error'] or 0))]
            if ratio:
                y_values.append(1.)
            log_y = not ratio and variable == 'pt' and bool(valid) and all(
                value > 0 for value in y_values)
            y_range = _padded_range(y_values,
                                    config['layout']['axis_padding_fraction'],
                                    log_y)
            flow_count = sum(row['flow'] != 'REGULAR' for row in selected)
            missing_count = sum(point['state'] == 'MISSING_VALUE'
                                for item in series for point in item['points'])
            note = ('flow bins retained: '+str(flow_count) if flow_count else '')
            if axis_id == 'pt':
                note += ('; ' if note else '')+(
                    '#it{p}_{T}<0 rejected; high overflow counted' if no_floor_pt else
                    '#it{p}_{T} under/overflow in denominator')
            else:
                note += ('; ' if note else '')+'no '+axis_id+' flow bins'
            if missing_count:
                note += ('; ' if note else '')+'missing bins: '+str(missing_count)
            if any(point['state'] == 'DRAW' and point['error'] is None
                   for item in series for point in item['points']):
                note += ('; ' if note else '') + (
                    'SE unavailable for unresolved ratios; see ROOT flags')
            if valid:
                panel_status = 'AVAILABLE'
            else:
                panel_status, note = typed_panel_status(context, selected)
            panel = {
                'id':'g9.ratio' if ratio else 'g9.absolute',
                'status':panel_status,
                'log_y':log_y, 'log_x':log_x,
                'geometry':[0.,.12,1.,.34] if ratio else [0.,.34,1.,.90],
                'x_range':[x_low,x_high], 'y_range':y_range,
                'title':'',
                'x_title':x_title if ratio else '',
                'y_title':ratio_title if ratio else absolute_title,
                'note':(note if not valid or ratio else ''),
                'series':series,
                'category_dividers':True,
                'uncertainty_display':'STANDARD',
                'guides':([{'id':'unity','x_low':x_low,'x_high':x_high,
                            'y_low':1.,'y_high':1.,'color':'#777777',
                            'line_style':10,'label':''}] if ratio else []),
                'ticks':[],
                'margins':[.16,.04,.28,.08] if ratio else [.16,.04,.06,.13],
                'legend':[.53,.69,.95,.87] if ratio else
                         [.53,.86,.95,.98], 'reuse':None,
            }
            page['panels'].append(panel)
        pages.append(page)
    return pages

def drawing_payload(plan):
    lines = [[DRAWING_SCHEMA,plan["request_id"]]]
    for p in plan["pages"]:
        lines.append(["PAGE",p["filename"],p["role"],p["page_index"],p["page_count"],p["text_pixels"],
                      p["information"],p["title"],p["width"],p["height"],p["header_bottom"],
                      p["scientific_header"],p["style_header"]])
        for a in p["panels"]:
            prefix = [p["filename"],a["id"]]
            lines.append(["PANEL"]+prefix+[a["status"],int(a["log_y"])]+a["x_range"]+a["y_range"]+a["geometry"]+
                         [a["title"],a["x_title"],a["y_title"],a["note"]]+a["margins"]+a["legend"]+
                         [int(a["log_x"]),a["uncertainty_display"],
                          int(a["category_dividers"])])
            for caption in a.get("annotations", []):
                lines.append(["ANNOTATION"]+prefix+[caption['x'],caption['y'],caption['size'],caption['text']])
            for s in a["series"]:
                lines.append(["SERIES"]+prefix+[s["key"],s["tune"],s["class_id"] or "-",s["color"],s["marker"],
                                                s["line_style"],s["label"],s["draw_mode"],s["legend_label"],s["emphasis"]])
                for q in s["points"]:
                    lines.append(["POINT"]+prefix+[s["key"],q["semantic_id"],
                        q["bin"],q["scientific_x"],q["display_x"],q["y"],
                        q["error"],q["bin_low"],q["bin_high"],
                        q["support_low"],q["support_high"],
                        q["class_id"] or "-",q["value_status"],
                        q["uncertainty_status"],q["state"],q["reasons"] or "-"])
            for g in a["guides"]:
                lines.append(["GUIDE"]+prefix+[g["id"],g["x_low"],g["x_high"],g["y_low"],g["y_high"],g["color"],g["line_style"],g["label"]])
            for t in a["ticks"]:
                lines.append(["TICK"]+prefix+[t["x"],t["label"]])
            if a["reuse"]:
                lines.append(["REUSE"]+prefix+[a["reuse"]["panel"],a["reuse"]["tune"]])
    lines.append(["END"])
    def token(value):
        if value is None: return "-"
        if type(value) is float:
            if not math.isfinite(value): raise ValueError("nonfinite drawing number")
            return value.hex()
        value = str(value)
        if any(c in value for c in "\t\r\n"): raise ValueError("drawing text contains a delimiter")
        return value
    return ("\n".join("\t".join(token(v) for v in line) for line in lines)+"\n").encode("ascii")

def normalized_drawing_record(payload):
    """Canonicalize numbers reconstructed by C++, never just echo input bytes."""
    numeric = {"PAGE":[10], "PANEL":list(range(5,13))+list(range(17,25)),
               "ANNOTATION":[3,4,5], "POINT":list(range(6,14)), "GUIDE":list(range(4,8)), "TICK":[3]}
    lines=[]
    for line in payload.decode("ascii").splitlines():
        fields=line.split("\t")
        for i in numeric.get(fields[0],[]):
            if fields[i]!="-":
                v=float.fromhex(fields[i])
                if not math.isfinite(v): raise ValueError("nonfinite consumed drawing record")
                fields[i]=v.hex()
        lines.append("\t".join(fields))
    return ("\n".join(lines)+"\n").encode("ascii")

def verify_canvas_archive(binary, environment, directory, record_payload,
                          work_dir):
    with tempfile.TemporaryDirectory(prefix="canvas-verify-",
                                     dir=str(work_dir)) as temporary:
        record = Path(temporary) / "drawing-record.tsv"
        write_payload(record, record_payload)
        completed = subprocess.run(
            [str(binary), "verify", str(directory), str(record)],
            env=environment, text=True, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
    if (completed.returncode or completed.stdout.strip() or
            completed.stderr.strip()):
        raise ValueError("ROOT canvas reopen verification failed: {}".format(
            completed.stderr.strip() or completed.stdout.strip()))

def canonical_root_pdf(payload, filename):
    """Normalize ROOT's single-page classic PDF without touching drawing streams.

    ROOT uses an A4 MediaBox even for a canvas-sized CropBox. Make both physical
    bounds agree, remove private staging paths and timestamps, and rebuild the
    classic cross-reference table from its authenticated object boundaries.
    Unexpected PDF framing is refused rather than guessed.
    """
    ending = re.search(rb"startxref\s+(\d+)\s+%%EOF\s*$", payload)
    if not ending:
        raise ValueError("ROOT PDF classic framing differs")
    offset = int(ending.group(1))
    table = payload[offset:].splitlines()
    if table[0] != b"xref" or not re.fullmatch(rb"0 \d+", table[1]):
        raise ValueError("ROOT PDF xref framing differs")
    count = int(table[1].split()[1])
    entries = table[2:2+count]
    if len(entries) != count or entries[0].split() != [b"0000000000", b"65535", b"f"]:
        raise ValueError("ROOT PDF xref count differs")
    positions = []
    for object_id, entry in enumerate(entries[1:], 1):
        if not re.fullmatch(rb"\d{10} 00000 n ?", entry):
            raise ValueError("ROOT PDF object reference differs")
        positions.append((int(entry.split()[0]), object_id))
    positions.sort()
    output = bytearray(payload[:positions[0][0]])
    rewritten = {}; page_count = 0; info_count = 0
    for index, (start, object_id) in enumerate(positions):
        end = positions[index+1][0] if index+1 < len(positions) else offset
        obj = payload[start:end]
        if not obj.startswith((str(object_id)+" 0 obj\n").encode("ascii")):
            raise ValueError("ROOT PDF object offset differs")
        if re.search(rb"/Type /Page\s", obj):
            crop = re.search(rb"/CropBox (\[[^\]]+\])", obj)
            if crop is None:
                raise ValueError("ROOT PDF canvas bounds missing")
            obj, changed = re.subn(rb"/MediaBox \[[^\]]+\]", b"/MediaBox "+crop.group(1), obj)
            if changed != 1:
                raise ValueError("ROOT PDF media bounds differ")
            page_count += 1
        if b"/CreationDate " in obj:
            obj = re.sub(rb"/(CreationDate|ModDate) \([^\n]*\)",
                         rb"/\1 (D:20000101000000Z)", obj)
            obj, changed = re.subn(rb"/Title \([^\n]*\)",
                                  b"/Title ("+filename.encode("ascii")+b")", obj)
            if changed != 1:
                raise ValueError("ROOT PDF document title differs")
            info_count += 1
        rewritten[object_id] = len(output); output.extend(obj)
    if page_count != 1 or info_count != 1:
        raise ValueError("ROOT PDF single-page metadata differs")
    new_offset = len(output)
    output.extend(("xref\n0 {}\n0000000000 65535 f \n".format(count)).encode("ascii"))
    for object_id in range(1, count):
        output.extend(("{:010d} 00000 n \n".format(rewritten[object_id])).encode("ascii"))
    trailer = b"\n".join(table[2+count:])
    trailer = re.sub(rb"startxref\s+\d+", b"startxref\n"+str(new_offset).encode("ascii"), trailer)
    output.extend(trailer+b"\n")
    return bytes(output)


def pdf_export_runtime():
    """Check the external vector exporter before creating an output stage."""
    for executable in ('gs', 'pdffonts'):
        if shutil.which(executable) is None:
            raise ValueError('PDF export requires '+executable+' on PATH')
    version=subprocess.run(['gs','--version'],check=True,capture_output=True,text=True).stdout.strip()
    if re.fullmatch(r'[0-9]+\.[0-9]+(?:\.[0-9]+)?',version) is None:
        raise ValueError('Ghostscript version response differs')
    return {'policy':'vector_pdf_embedded_fonts_v1', 'ghostscript_version':version}


def verify_pdf_fonts(path):
    """Refuse missing or unembedded fonts in the actual exported PDF."""
    completed=subprocess.run(['pdffonts',str(path)],check=True,
                             capture_output=True,text=True)
    rows=completed.stdout.splitlines()[2:]
    if not rows:
        raise ValueError('PDF has no inspectable font records: '+path.name)
    for row in rows:
        fields=row.split()
        # The five trailing fields are emb, sub, uni, object ID and generation.
        if len(fields)<8 or fields[-5]!='yes':
            raise ValueError('PDF contains an unembedded font: '+path.name)
    return len(rows)


def canonical_export_pdf(payload, identity):
    """Normalize only an optional classic-PDF trailer ID from older exporters."""
    ending=re.search(rb"startxref\s+(\d+)\s+%%EOF\s*$",payload)
    if ending is None or re.fullmatch(r'[0-9a-f]{32}',identity) is None:
        raise ValueError('exported PDF identity framing differs')
    offset=int(ending.group(1))
    if payload[offset:offset+5]!=b'xref\n':
        raise ValueError('exported PDF classic xref differs')
    marker=payload.find(b'\ntrailer\n',offset)
    if marker<0:
        raise ValueError('exported PDF trailer missing')
    trailer=payload[marker:]
    # Ghostscript can encode a 16-byte ID as hex or an escaped literal string.
    token=rb'(?:<[0-9A-Fa-f]{32}>|\((?:\\(?:[0-7]{1,3}|[nrtbf()\\])|[^\\()\r\n])*\))'
    pattern=rb'/ID\s*\[\s*('+token+rb')\s*('+token+rb')\s*\]'
    def replace_id(match):
        for value in match.groups():
            if value.startswith(b'('):
                body=value[1:-1]
                decoded=re.sub(rb'\\([0-7]{1,3}|[nrtbf()\\])',
                    lambda m: bytes([int(m[1],8) & 255]) if m[1][:1] in b'01234567'
                    else {b'n':b'\n',b'r':b'\r',b't':b'\t',b'b':b'\b',b'f':b'\f',
                          b'(':b'(',b')':b')',b'\\':b'\\'}[m[1]],body)
                if len(decoded)!=16:
                    raise ValueError('exported PDF trailer ID length differs')
        return b'/ID [<'+identity.encode()+b'><'+identity.encode()+b'>]'
    fixed,count=re.subn(pattern,replace_id,trailer)
    if count>1 or b'/ID' in re.sub(pattern,b'',trailer):
        raise ValueError('exported PDF trailer ID differs')
    # Only trailer bytes change. Object offsets and startxref stay unchanged.
    return payload[:marker]+fixed


def publication_pdf(path):
    """Embed fonts without rasterizing the scientific drawing."""
    canonical_pdf=canonical_root_pdf(path.read_bytes(),path.name)
    digest=hashlib.sha256(canonical_pdf).hexdigest()
    document_uuid='-'.join((digest[:8],digest[8:12],digest[12:16],
                            digest[16:20],digest[20:32]))
    with tempfile.TemporaryDirectory(prefix='.pdf-export-',dir=str(path.parent)) as tmp:
        source=Path(tmp)/'input.pdf'; output=Path(tmp)/'output.pdf'
        source.write_bytes(canonical_pdf)
        subprocess.run(['gs','-q','-dSAFER','-dBATCH','-dNOPAUSE',
            '-sDEVICE=pdfwrite','-dCompatibilityLevel=1.4',
            '-dEmbedAllFonts=true','-dSubsetFonts=true','-dAutoRotatePages=/None',
            '-dOmitID=true','-dOmitXMP=true',
            '-sDocumentUUID='+document_uuid,
            '-sOutputFile='+str(output),
            '-c','<</NeverEmbed []>> setdistillerparams','-f',str(source),
            '-c','[ /CreationDate (D:20000101000000Z) '
                 '/ModDate (D:20000101000000Z) /DOCINFO pdfmark'],
            check=True,capture_output=True,text=True)
        output.write_bytes(canonical_export_pdf(output.read_bytes(),digest[:32]))
        verify_pdf_fonts(output)
        # This is a private output stage. Final publication still uses the
        # existing no-replace directory operation.
        path.write_bytes(output.read_bytes())


def canonical_root_archive(path, drawing_record):
    """Normalize ROOT container metadata, leaving every object byte intact.

    TFile writes a UUID and wall-clock TDatime into the file header, root
    directory, and TKey headers/index. The parser accepts only the small-file
    layout used here. The fresh-process canvas verifier runs afterwards.
    """
    data = path.read_bytes()
    if len(data) < 128 or data[:4] != b"root":
        raise ValueError("canvas archive is not a ROOT small file")
    version = int.from_bytes(data[4:8], "big")
    begin = int.from_bytes(data[8:12], "big")
    end = int.from_bytes(data[12:16], "big")
    if version >= 1_000_000 or begin < 64 or begin >= end or end != len(data):
        raise ValueError("canvas ROOT header layout differs")
    raw_uuid = data[47:63]
    if len(raw_uuid) != 16 or data.count(raw_uuid) != 2:
        raise ValueError("canvas ROOT UUID layout differs")
    dates = set()
    key_count = 0
    offset = begin
    while offset < end:
        if offset + 14 > end:
            raise ValueError("canvas ROOT key header is truncated")
        size = int.from_bytes(data[offset:offset+4], "big", signed=True)
        if size <= 0 or offset + size > end:
            raise ValueError("canvas ROOT key map differs")
        key_version = int.from_bytes(data[offset+4:offset+6], "big")
        if key_version not in (4, 1004):
            raise ValueError("canvas ROOT key version differs")
        dates.add(data[offset+10:offset+14])
        offset += size
        key_count += 1
    if offset != end or key_count < 3 or len(dates) > key_count:
        raise ValueError("canvas ROOT key map is incomplete")
    canonical_date = (339869696).to_bytes(4, "big")  # 2000-01-01 UTC
    canonical_uuid = hashlib.sha256(drawing_record).digest()[:16]
    result = data.replace(raw_uuid, canonical_uuid)
    for date in dates:
        if result.count(date) < 1:
            raise ValueError("canvas ROOT datetime index differs")
        result = result.replace(date, canonical_date)
    temporary = path.with_name(path.name + ".canonicalizing")
    try:
        with temporary.open("xb") as stream:
            stream.write(result)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        fsync_directory(path.parent)
    finally:
        temporary.unlink(missing_ok=True)

def promote_render_pages(pages, output):
    """Publish regular PDF pages first and the verified manifest last."""
    output.mkdir(mode=0o700)
    try:
        for path in sorted(list(pages.glob("*.pdf")) +
                           [pages / CANVAS_NAME, pages / RECORD_NAME]):
            regular_file(path, "staged render page")
            os.link(str(path), str(output / path.name))
        fsync_directory(output)
        if os.environ.get("HADRONIZATION_RENDER_FAIL_BEFORE_MANIFEST") == "1":
            raise ValueError("injected interruption before render manifest commit")
        os.link(str(pages / "manifest.json"), str(output / "manifest.json"))
        fsync_directory(output)
        fsync_directory(output.parent)
    except Exception:
        if output.exists():
            shutil.rmtree(str(output))
            fsync_directory(output.parent)
        raise

def cold_numerics(args):
    """Read S's frozen ROOT once, with trusted physical and logical digests."""
    path = ROOT / "pipeline/reduce/archive.py"
    if not path.is_file():
        raise ValueError("S cold reader has not been integrated into this tree")
    # Launching run.py by filename puts pipeline/plot, rather than the repository
    # root, on sys.path. Import the verified sibling as a package so its v4
    # reader can resolve its own relative imports on a cold CLI invocation.
    sys.path.insert(0, str(ROOT))
    try:
        archive = importlib.import_module("pipeline.reduce.archive")
    finally:
        sys.path.pop(0)
    if Path(archive.__file__).resolve() != path.resolve():
        raise ValueError("S cold reader resolves outside this source tree")
    if not hasattr(archive, "read"):
        raise ValueError("S cold reader lacks read(source, work, hashes)")
    args.work_dir.mkdir(parents=True, exist_ok=True)
    return archive.read(args.numerics_root, args.work_dir,
                        args.expected_root_sha256,
                        args.expected_value_sha256)

def cold_render_manifest(args, payload, config, config_sha, build, plan,
                         pages, record, pdf_export):
    files = []
    for path in sorted(list(pages.glob("*.pdf")) +
                       [pages / CANVAS_NAME, pages / RECORD_NAME]):
        regular_file(path, "cold plot artifact")
        files.append({"name": path.name, "bytes": path.stat().st_size,
                      "sha256": sha_file(path)})
    return {
        "schema": "hadronization_cold_plot_render_v1",
        "version": "1.0.0", "state": "COMPLETE",
        "campaign_state": payload["campaign_state"],
        "presentation_state": (
            "TEST_ONLY_SYNTHETIC" if synthetic_provenance(payload) else
            "TEST_ONLY_PARTIAL" if payload["campaign_state"] == "PARTIAL_SAMPLE"
            else "FULL_ACCEPTED_CAMPAIGN"),
        "numerics_root": {
            "logical_name": "numerics.root",
            "payload_schema": payload["schema"],
            "sha256": args.expected_root_sha256,
            "bytes": args.numerics_root.stat().st_size,
            "value_sha256": args.expected_value_sha256,
            "science_content_sha256": payload["science_content_sha256"]},
        "plot_config_sha256": config_sha,
        "presentation_scope": {
            "correlation_view": config['layout']['correlation_view'],
            "paper_trigger_pdgs": config['presets']['paper_default'][
                'trigger_pdgs'],
            "baryon_meson_trigger_pdgs": config['presets'][
                'paper_default']['baryon_meson_trigger_pdgs'],
            "exclusion_counts": {reason:sum(item[1] == reason for item in
                plan['exclusions']) for reason in sorted({item[1] for item in
                plan['exclusions']})}},
        "target_campaign": ({"logical_name":"data/campaign.json",
                            "sha256":TARGET_CAMPAIGN_SHA256,
                            "bytes":TARGET_CAMPAIGN.stat().st_size}
                            if synthetic_provenance(payload) or
                            payload['request_echo']['sources']['campaign_id']==
                            'HF_RUN3_V1' else None),
        "source_sha256": {
            name:sha_file(ROOT / name) for name in ((
                "pipeline/plot/run.py", "pipeline/plot/render.cpp",
                "pipeline/reduce/archive.py", "pipeline/reduce/typed_nodes.py",
                "pipeline/reduce/projection.py") +
                (("pipeline/reduce/archive_v4.py",) if payload["schema"] ==
                 "hadronization_projection_result_v4" else ()))},
        "renderer_build": build,
        "pdf_export": pdf_export,
        "drawing_record_sha256": sha_bytes(record),
        "roles": [item["role_id"] for item in
                  payload["request_echo"]["scope"]["roles"]],
        "files": files,
        "filesystem_set": sorted([item["name"] for item in files] +
                                 ["manifest.json"]),
    }

def render_cold(args):
    """Render persisted coordinates/errors/statuses; never run projection."""
    reject_symlink_components(args.numerics_root, "numerics ROOT")
    reject_symlink_components(args.output, "cold plot output")
    output = args.output.resolve(strict=False)
    if output.exists():
        raise ValueError("no-overwrite cold plot output collision")
    config, config_sha = checked_plot_config(args.plot_config)
    pdf_export = pdf_export_runtime()
    payload = cold_numerics(args)
    context, adapter = cold_drawing_inputs(payload, config)
    plan = drawing_plan(context, adapter, config)
    record_expected = drawing_payload(plan)
    output.parent.mkdir(parents=True, exist_ok=True)
    environment, binary, build = build_renderer(args.work_dir)
    stage = Path(tempfile.mkdtemp(prefix="." + output.name + ".cold-stage-",
                                  dir=str(output.parent)))
    try:
        pages = stage / "pages"
        plan_path = stage / "drawing-plan.tsv"
        record_path = stage / "drawing-record.tsv"
        write_payload(plan_path, record_expected)
        completed = subprocess.run([str(binary), str(plan_path), str(pages),
                                    str(record_path)], env=environment,
                                   capture_output=True, text=True)
        if completed.returncode or completed.stdout.strip() or completed.stderr.strip():
            raise ValueError("cold ROOT drawing failed: " +
                             (completed.stderr or completed.stdout))
        record = record_path.read_bytes()
        if normalized_drawing_record(record) != record_expected:
            raise ValueError("cold ROOT drawing record differs")
        canonical_root_archive(pages / CANVAS_NAME, record)
        verify_canvas_archive(binary, environment, pages, record, args.work_dir)
        for page in pages.glob("*.pdf"):
            publication_pdf(page)
        write_payload(pages / RECORD_NAME, deterministic_gzip(record))
        manifest = cold_render_manifest(args, payload, config, config_sha,
                                        build, plan, pages, record, pdf_export)
        atomic_json(pages / "manifest.json", manifest)
        promote_render_pages(pages, output)
        verify_cold_files(args, payload, config_sha, build, plan,
                          output, binary, environment)
    finally:
        shutil.rmtree(stage)
    print("COLD_RENDERED OUTPUT={} ROOT_SHA256={} PAGES={}".format(
        output, args.expected_root_sha256,
        sum(name.endswith(".pdf") for name in manifest["filesystem_set"])))

def verify_cold_files(args, payload, config_sha, build, plan, output,
                      binary, environment):
    expected_manifest = getattr(args, "expected_manifest_sha256", None)
    if expected_manifest is not None and (
            re.fullmatch(r"[0-9a-f]{64}", expected_manifest) is None or
            sha_file(output / "manifest.json") != expected_manifest):
        raise ValueError("trusted cold render manifest SHA256 differs")
    manifest = json_file(output / "manifest.json", "cold plot manifest")
    verify_flat_fileset(output, manifest["filesystem_set"], "cold plots")
    expected_pages = {page["filename"] for page in plan["pages"]}
    actual_pages = {path.name for path in output.glob("*.pdf")}
    if expected_pages != actual_pages:
        raise ValueError("cold page role/fileset differs")
    record = gzip.decompress((output / RECORD_NAME).read_bytes())
    if (manifest["drawing_record_sha256"] != sha_bytes(record) or
            normalized_drawing_record(record) != drawing_payload(plan)):
        raise ValueError("cold drawing record/science binding differs")
    original_build = manifest.get("renderer_build")
    if (not isinstance(original_build, dict) or
            set(original_build) != {"schema", "build_id",
                                    "build_identity", "binary_sha256"} or
            original_build.get("schema") !=
                "hadronization_plot_renderer_build_receipt_v1" or
            original_build.get("build_identity") != build["build_identity"] or
            original_build.get("build_id") != build["build_id"] or
            original_build.get("build_id") != sha_bytes(canonical(
                original_build["build_identity"]).encode("ascii")) or
            not isinstance(original_build.get("binary_sha256"), str) or
            re.fullmatch(r"[0-9a-f]{64}",
                         original_build["binary_sha256"]) is None):
        raise ValueError("original renderer execution receipt differs")
    config, _ = checked_plot_config(args.plot_config)
    pdf_export=manifest.get("pdf_export")
    if (not isinstance(pdf_export,dict) or set(pdf_export)!={'policy','ghostscript_version'} or
            pdf_export.get('policy')!='vector_pdf_embedded_fonts_v1' or
            re.fullmatch(r'[0-9]+\.[0-9]+(?:\.[0-9]+)?',str(pdf_export.get('ghostscript_version'))) is None):
        raise ValueError('PDF export receipt differs')
    for path in output.glob('*.pdf'):
        verify_pdf_fonts(path)
    expected = cold_render_manifest(args, payload, config, config_sha,
                                    original_build, plan, output, record, pdf_export)
    if manifest != expected:
        raise ValueError("cold plot manifest/byte identity differs")
    verify_canvas_archive(binary, environment, output, record, args.work_dir)
    return manifest

def record_verifier_attestation(args, manifest, build, output):
    """Keep this execution separate from the immutable render receipt."""
    receipt = {
        "schema":"hadronization_plot_verifier_attestation_v1",
        "render_manifest_sha256":sha_file(output / "manifest.json"),
        "render_binary_sha256":manifest["renderer_build"]["binary_sha256"],
        "verifier_build_id":build["build_id"],
        "verifier_binary_sha256":build["binary_sha256"],
        "verified_fileset":manifest["filesystem_set"],
    }
    attestation_dir = args.work_dir / "verifier-attestations"
    reject_symlink_components(attestation_dir, "plot verifier attestations")
    attestation_dir.mkdir(parents=True, exist_ok=True)
    path = attestation_dir / (receipt["render_manifest_sha256"][:20] + "-" +
                              receipt["verifier_binary_sha256"][:20] +
                              ".json")
    if path.exists():
        if json_file(path, "plot verifier attestation") != receipt:
            raise ValueError("verifier attestation collision")
    else:
        atomic_json(path, receipt)
    return {"path":str(path), **receipt}


def review_packet_coverage(plan, context, config):
    """Require visible S-owned test points in every approved paper panel."""
    failures = []
    if context.campaign_state != 'PARTIAL_SAMPLE':
        failures.append('review packet must be a test-only partial sample')
    if not getattr(context, 'synthetic', False):
        failures.append('review packet lacks S synthetic provenance')
    expected_tunes = [item['id'] for item in
                      config['style_identities']['tunes']]
    if (len(context.tunes) != len(expected_tunes) or
            set(context.tunes) != set(expected_tunes)):
        failures.append('three-tune style coverage differs')
    paper = config['presets']['paper_default']
    charm_meson = str(paper['trigger_pdgs'][0])
    compared = [tune for tune in expected_tunes
                if tune != context.reference_tune]
    page_map = {page['filename']:page for page in plan['pages']}
    if len(page_map) != len(plan['pages']):
        failures.append('review page filename collision')
    roles = ('multiplicity.composite', 'correlations.charm',
             'correlations.beauty', 'balancing.integrated.charm',
             'balancing.activity.charm', 'balancing.integrated.beauty',
             'balancing.activity.beauty',
             'balancing.baryon_meson.activity')
    def page(name):
        value = page_map.get(name)
        if value is None:
            failures.append(name+' absent')
        elif value['scientific_header'] not in (
                'TEST_ONLY / SYNTHETIC',
                'TEST_ONLY / SYNTHETIC / PARTIAL_SAMPLE'):
            failures.append(name+' lacks synthetic marking')
        return value
    def panel(owner, name):
        if owner is None:
            return None
        value = next((item for item in owner['panels']
                      if item['id'] == name), None)
        if value is None:
            failures.append(owner['filename']+'/'+name+' absent')
        return value
    def visible(item, tune=None, class_id=None):
        if item is None:
            return []
        return [point for series in item['series']
                if tune is None or series['tune'] == tune
                for point in series['points']
                if (class_id is None or point['class_id'] == class_id) and
                point['state'] == 'DRAW'
                and point['y'] is not None]
    def require_points(owner, name, tunes, minimum):
        item = panel(owner, name)
        for tune in tunes:
            if len(visible(item, tune)) < minimum:
                failures.append((owner['filename'] if owner else '?')+
                                '/'+name+'/'+tune+' lacks visible points')
        return item
    canonical = {role:page(canonical_page_name(role)) for role in roles}
    p1 = canonical['multiplicity.composite']
    main = require_points(p1, 'upper.distribution', expected_tunes, 5)
    require_points(p1, 'lower.ratio', compared, 5)
    inset = panel(p1, 'inset.monash_boundaries')
    class_count = len([item for item in context.classes
                       if not item['integrated']])
    if class_count != 11:
        failures.append('current eleven-class review domain differs')
    guides = ([] if main is None else [guide for guide in main['guides']
              if guide['id'].startswith('class.')])
    inset_guides = ([] if inset is None else [guide for guide in inset['guides']
                    if guide['id'].startswith('class.')])
    if (guides or len(inset_guides) != class_count or
            len({guide['x_low'] for guide in inset_guides}) <
            min(8, class_count)):
        failures.append('P1 current class boundaries absent/overlap')
    if len([guide for guide in inset_guides
            if guide['label'].endswith('%') and
            '[' not in guide['label'] and
            guide['x_high'] > guide['x_low']]) != class_count:
        failures.append('P1 inset percentile slice labels incomplete')
    lower=panel(p1,'lower.ratio')
    if (main is not None and inset is not None and lower is not None and
            (main['x_range'] != lower['x_range'] or
             inset['x_range'] != [1., main['x_range'][1]] or
             main['x_range'][0] != 0 or not inset['log_x'] or
             not inset['log_y'])):
        failures.append('P1 full-support aligned x domain differs')
    if main is not None and len([point for point in visible(main,
                                            context.reference_tune)
                                 if point['y'] > 0 and
                                 point['support_low'] is not None and
                                 point['support_low'] > 0]) < 5:
        failures.append('P1 reference positive occupied support invisible')
    for role, triggers in (
            ('correlations.charm', (charm_meson,'4122')),
            ('correlations.beauty', ('521','5122'))):
        owner = canonical[role]
        for trigger in triggers:
            if config['layout']['correlation_view'] == 'monash_pair_sign':
                for suffix, associate, components in (
                        ('identified', str(-int(trigger)), {'OS', 'SS'}),
                        ('inclusive', '', {'OS_MINUS_SS'})):
                    item = require_points(owner,
                        'correlation.teaching.'+trigger+'.'+suffix,
                        [context.reference_tune],
                        6 if suffix == 'identified' else 3)
                    if item is None:
                        continue
                    identities = {(s['identity']['component'],
                                   s['identity']['associate_pdg'])
                                  for s in item['series']}
                    if identities != {(component, associate)
                                      for component in components}:
                        failures.append(role+'/'+trigger+'/'+suffix+
                                        ' signed pair identity differs')
            elif config['layout']['correlation_view'] == 'monash_balance':
                upper = require_points(owner,
                    'correlation.balance.'+trigger+'.upper',
                    [context.reference_tune], 6)
                lower = require_points(owner,
                    'correlation.balance.'+trigger+'.lower',
                    [context.reference_tune], 3)
                if upper is not None and {series['identity']['component']
                        for series in upper['series']} != {'OS','SS'}:
                    failures.append(role+'/'+trigger+' OS/SS overlay differs')
                if lower is not None and {series['identity']['component']
                        for series in lower['series']} != {'OS_MINUS_SS'}:
                    failures.append(role+'/'+trigger+' subtraction differs')
            else:
                for component in ('OS', 'SS', 'OS_MINUS_SS'):
                    require_points(owner,
                        'correlation.main.'+trigger+'.'+component,
                        expected_tunes, 3)
                    require_points(owner,
                        'correlation.compare.'+trigger+'.'+component,
                        compared, 3)
    for role, triggers in (
            ('balancing.integrated.charm', (charm_meson,'4122')),
            ('balancing.integrated.beauty', ('521','5122'))):
        owner = canonical[role]
        for trigger in triggers:
            declared = getattr(context, 'category_orders', {}).get(role, {}).get(trigger)
            if not declared:
                failures.append(role+'/'+trigger+' numerical categories absent')
                continue
            categories = len(declared)
            upper = require_points(owner, 'upper.'+trigger,
                                   expected_tunes, categories-1)
            require_points(owner, 'lower.'+trigger,
                           compared, categories-1)
            if upper is not None and len({point['scientific_x']
                    for point in visible(upper)}) != categories:
                failures.append(role+'/'+trigger+' category coverage differs')
    class_ids = [str(item['id']) for item in context.classes
                 if not item['integrated']]
    for role, triggers in (
            ('balancing.activity.charm', (charm_meson,'4122')),
            ('balancing.activity.beauty', ('521','5122'))):
        owner = canonical[role]
        for trigger in triggers:
            uppers = [require_points(owner,
                      'upper.{}.{}'.format(tune, trigger),
                      [tune], len(class_ids)) for tune in expected_tunes]
            require_points(owner, 'lower.shared.'+trigger,
                           compared, len(class_ids))
            for class_id in class_ids:
                if any(not visible(upper, class_id=class_id)
                       for upper in uppers):
                    failures.append(role+'/'+trigger+'/class '+class_id+
                                    ' lacks visible point')
        focused = page('supplemental.'+role+'.extremes.pdf')
        for trigger in triggers:
            upper = panel(focused, 'upper.'+trigger)
            lower = panel(focused, 'lower.'+trigger)
            for class_id in selected_extreme_class_ids(context.classes):
                if not visible(upper, class_id=class_id):
                    failures.append(role+' focused '+trigger+'/class '+
                                    class_id+' lacks visible point')
                for tune in compared:
                    if not visible(lower, tune=tune, class_id=class_id):
                        failures.append(role+' focused '+trigger+'/'+tune+
                                        '/class '+class_id+
                                        ' comparison lacks visible point')
    p8 = canonical['balancing.baryon_meson.activity']
    for sector,trigger in (('charm',charm_meson),('beauty','521')):
        upper = require_points(p8,'upper.'+sector+'.'+trigger,
                               expected_tunes,len(class_ids))
        lower = require_points(p8,'lower.'+sector+'.'+trigger,
                               compared,len(class_ids)-1)
        if lower is not None:
            for tune in compared:
                points = [point for series in lower['series']
                          if series['tune'] == tune
                          for point in series['points']]
                if len([point for point in points
                        if point['state']=='DRAW']) < len(class_ids) and not any(
                        point['state']=='MISSING_VALUE' for point in points):
                    failures.append('P8 '+sector+'/'+tune+
                                    ' incomplete comparison lacks missing status')
        for class_id in class_ids:
            if not visible(upper,class_id=class_id):
                failures.append('P8 '+sector+'/class '+class_id+
                                ' lacks visible point')
    p8_by_tune = page(
        'supplemental.balancing.baryon_meson.activity.by_tune.pdf')
    for sector,trigger in (('charm',charm_meson),('beauty','521')):
        for tune in expected_tunes:
            require_points(p8_by_tune,
                'upper.{}.{}.{}'.format(tune, sector, trigger),
                [tune], len(class_ids))
        require_points(p8_by_tune,
            'lower.shared.{}.{}'.format(sector, trigger),
            compared, len(class_ids)-1)
    g9 = [owner for owner in plan['pages']
          if owner['role'] == 'spectra.signed_heavy']
    if len(g9) < 2:
        failures.append('representative G9 signed-species pages absent')
    for owner in g9:
        require_points(owner,'g9.absolute',expected_tunes,3)
        require_points(owner,'g9.ratio',compared,3)
    for owner in canonical.values():
        if owner is not None:
            issue=review_uncertainty_presentation(owner)
            if issue:
                failures.append(issue)
    all_points = [point for owner in plan['pages']
                  for item in owner['panels']
                  for series in item['series']
                  for point in series['points']]
    if not any(point['state'] == 'DRAW' and point['y'] < 0
               for point in all_points):
        failures.append('negative synthetic center absent')
    if not any(point['state'] == 'DRAW' and point['y'] == 0
               for point in all_points):
        failures.append('zero synthetic center absent')
    if not any(point['state'] == 'MISSING_VALUE'
               for point in all_points):
        failures.append('missing synthetic point/status rail absent')
    if not any(point['state'] == 'DRAW' and point['error'] is None
               for point in all_points):
        failures.append('withheld synthetic uncertainty case absent')
    if failures:
        raise ValueError('synthetic review coverage failed ({}): {}'.format(
            len(failures), '; '.join(failures[:16])))
    return {'schema':'hadronization_test_only_review_coverage_v1',
            'canonical_paper_pages':len(roles),
            'supplemental_extreme_pages':2,
            'supplemental_baryon_meson_pages':1,
            'representative_g9_pages':len(g9),
            'visible_points':sum(len(visible(item)) for owner in plan['pages']
                                  for item in owner['panels']),
            'p1_class_boundary_guides':len(inset_guides)}


def verify_review_packet(args):
    config, config_sha = checked_plot_config(args.plot_config)
    payload = cold_numerics(args)
    context, adapter = cold_drawing_inputs(payload, config)
    plan = drawing_plan(context, adapter, config)
    environment, binary, build = build_renderer(args.work_dir)
    output = args.output.resolve()
    manifest = verify_cold_files(args, payload, config_sha, build, plan,
                                 output, binary, environment)
    coverage = review_packet_coverage(plan, context, config)
    print(canonical({**coverage, "verifier_attestation":
                     record_verifier_attestation(args, manifest, build,
                                                 output)}))

def verify_render_cold(args):
    config, config_sha = checked_plot_config(args.plot_config)
    payload = cold_numerics(args)
    context, adapter = cold_drawing_inputs(payload, config)
    plan = drawing_plan(context, adapter, config)
    environment, binary, build = build_renderer(args.work_dir)
    manifest = verify_cold_files(args, payload, config_sha, build, plan,
                                 args.output.resolve(), binary, environment)
    attestation = record_verifier_attestation(
        args, manifest, build, args.output.resolve())
    print("COLD_RENDER_VERIFIED OUTPUT={} FILES={}".format(
        args.output.resolve(), len(manifest["filesystem_set"])))
    print(canonical(attestation))

def cold_inputs(parser):
    parser.add_argument("--numerics-root", type=Path, required=True)
    parser.add_argument("--expected-root-sha256", required=True)
    parser.add_argument("--expected-value-sha256", required=True)
    parser.add_argument("--expected-manifest-sha256",
        help="optional independent manifest pin for verification")
    parser.add_argument("--plot-config", type=Path, default=PLOT_CONFIG)
    parser.add_argument("--work-dir", type=Path, required=True,
                        help="renderer and archive build scratch")
    parser.add_argument("--output", type=Path, required=True)

def parser():
    top = argparse.ArgumentParser(
        prog="hadronization plot",
        description="Draw and verify numerical ROOT results without projection")
    sub = top.add_subparsers(dest="command", required=True)
    cold_render_parser = sub.add_parser(
        "render-cold", help="draw verified numerics.root")
    cold_inputs(cold_render_parser)
    cold_verify_parser = sub.add_parser(
        "verify-render-cold", help="reopen every ROOT canvas and verify bytes")
    cold_inputs(cold_verify_parser)
    review_parser = sub.add_parser(
        "verify-review-packet",
        help="check synthetic figure and signed-spectrum display coverage")
    cold_inputs(review_parser)
    return top

def main():
    args = parser().parse_args()
    try:
        if args.command == "render-cold":
            render_cold(args)
        elif args.command == "verify-render-cold":
            verify_render_cold(args)
        else:
            verify_review_packet(args)
        return 0
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        print("ERROR: {}".format(error), file=sys.stderr)
        return 2

if __name__ == "__main__":
    sys.exit(main())
