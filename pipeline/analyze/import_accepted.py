#!/usr/bin/env python3
"""Import the accepted HF_RUN3_V1 artifacts as a migration baseline.

This transitional program never reads event ROOT files and never writes into a
checkout.  Every historical source location is supplied explicitly and the
complete output is written below a new, empty staging directory.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import shlex
import shutil
import statistics
from collections import Counter, defaultdict
from pathlib import Path


TUNES = ("MONASH", "JUNCTIONS", "CLOSEPACKING")
TUNE_INDEX = {name: index for index, name in enumerate(TUNES)}
SEED_BASE = 100_000_001
CAMPAIGN_ORDINAL = 3
CAMPAIGN_STRIDE = 10_000_000
TUNE_STRIDE = 1_000_000
ATTEMPT_STRIDE = 100_000
RENDER_HEAD = "6729b3f0b7b94278b06a21943da669d6df737cc0"
COUNT_HEAD = "fe3262c729ec5a6b942309da45a70efdb2fe7fb4"
FREEZE_SHA256 = "fcd96eaebd4dc11f071a2c8db8849f6a4cc19b764622a796664e524b27d0fc80"

BALANCING_LOGS = (
    "render_VBARYONMESON.log",
    "render_VCORRELATIONS.log",
    "render_VEXTREMES.log",
    "render_VINTEGRATED.log",
    "render_VINTEGRATED_CLOSURE.log",
)
ALL_LOGS = (
    "render_VBARYONMESON.log",
    "render_VCORRELATIONS.log",
    "render_VEXTREMES.log",
    "render_VINTEGRATED.log",
    "render_VINTEGRATED_CLOSURE.log",
    "target_multiplicity_spectrum.log",
    "target_kinematic_spectra.log",
)

SPECIES = (
    "Bplus", "Bminus", "Lambdab", "Lambdabbar", "Sigmabzero",
    "Sigmabzerobar", "Dplus", "Dminus", "Lambdacplus", "Lambdacplusbar",
)
SPECIES_TOKEN = {
    "Bplus": "bplus", "Bminus": "bminus", "Lambdab": "lambdab",
    "Lambdabbar": "lambdabbar", "Sigmabzero": "sigmabzero",
    "Sigmabzerobar": "sigmabzerobar", "Dplus": "dplus",
    "Dminus": "dminus", "Lambdacplus": "lambdacplus",
    "Lambdacplusbar": "lambdacplusbar",
}
PDG = {
    "Bplus": 521, "Bminus": -521, "Lambdab": 5122, "Lambdabbar": -5122,
    "Sigmabzero": 5212, "Sigmabzerobar": -5212, "Dplus": 411,
    "Dminus": -411, "Lambdacplus": 4122, "Lambdacplusbar": -4122,
}

PAIR_FILES = {
    "BplusBcminus": "BplusBcplus", "BplusBminus": "BplusBplus",
    "BplusBszerobar": "BplusBszero", "BplusBzerobar": "BplusBzero",
    "BplusLb": "BplusLbbar", "DplusDminus": "DplusDplus",
    "DplusDzerobar": "DplusDzero", "DplusLambdacplusbar": "DplusLambdacplus",
    "LambdacplusDminus": "LambdacplusDplus",
    "LambdacplusDzerobar": "LambdacplusDzero",
    "LambdacplusLambdacplusbar": "LambdacplusLambdacplus",
    "LbbarBcminus": "LbbarBcplus", "LbbarBminus": "LbbarBplus",
    "LbbarBszerobar": "LbbarBszero", "LbbarBzerobar": "LbbarBzero",
    "LbbarLb": "LbbarLbbar",
}
PAIR_PARTICLES = {
    "Bplus": "bplus", "Bminus": "bminus", "Bplus": "bplus",
    "Bcminus": "bcminus", "Bcplus": "bcplus", "Bszerobar": "bszerobar",
    "Bszero": "bszero", "Bzerobar": "bzerobar", "Bzero": "bzero",
    "Lb": "lambdab", "Lbbar": "lambdabbar", "Dplus": "dplus",
    "Dminus": "dminus", "Dzerobar": "dzerobar", "Dzero": "dzero",
    "Lambdacplus": "lambdacplus", "Lambdacplusbar": "lambdacplusbar",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_identity(path: Path) -> dict[str, object]:
    return {"bytes": path.stat().st_size, "sha256": sha256(path)}


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, fieldnames: tuple[str, ...], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def fmt(value: float | int | str | None) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"nonfinite output value: {value}")
        return repr(value)
    return str(value)


def exact_count_token(token: str, *, source: str) -> str:
    """Return an exact non-negative decimal count without numeric coercion."""
    if not re.fullmatch(r"[0-9]+", token):
        raise ValueError(f"{source} is not an exact decimal integer token: {token!r}")
    return token


def source_entry(name: str, role: str, path: Path) -> dict[str, object]:
    return {"name": name, "role": role, **file_identity(path)}


def load_source_manifest(path: Path) -> list[dict[str, object]]:
    if sha256(path) != FREEZE_SHA256:
        raise ValueError(f"sealed manifest SHA-256 mismatch: {path}")
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    if len(rows) != 3000:
        raise ValueError(f"sealed manifest has {len(rows)} rows, expected 3000")
    return rows


def seed(tune: str, logical_id: int, attempt: int) -> int:
    return (SEED_BASE + CAMPAIGN_ORDINAL * CAMPAIGN_STRIDE
            + TUNE_INDEX[tune] * TUNE_STRIDE + attempt * ATTEMPT_STRIDE + logical_id)


def build_raw_manifest(source_rows: list[dict[str, object]], path: Path) -> list[dict[str, object]]:
    output = []
    equality_source = set()
    equality_output = set()
    for row in source_rows:
        tune = str(row["tune"])
        logical_id = int(row["logical_id"])
        attempt = int(row["attempt"])
        accepted_seed = int(row["seed"])
        if accepted_seed != seed(tune, logical_id, attempt):
            raise ValueError(f"seed mismatch for {tune}/{logical_id}")
        raw_path = Path(str(row["raw_path"]))
        try:
            raw_storage_key = raw_path.relative_to("raw").as_posix()
        except ValueError as exc:
            raise ValueError(f"nonportable raw path: {raw_path}") from exc
        item = {
            "tune": tune,
            "logical_id": logical_id,
            "block": (logical_id % 10) + 1,
            "accepted_attempt": attempt,
            "accepted_seed": accepted_seed,
            "raw_storage_key": raw_storage_key,
            "bytes": int(row["raw_bytes"]),
            "raw_sha256": str(row["raw_sha256"]),
            "successful_events": int(row["requested_successes"]),
            "validation_log_sha256": str(row["raw_validation_log_sha256"]),
            "validation_receipt_sha256": str(row["raw_validation_receipt_sha256"]),
        }
        equality_source.add((tune, logical_id, str(row["raw_sha256"]), int(row["raw_bytes"]),
                             attempt, accepted_seed))
        equality_output.add((tune, logical_id, item["raw_sha256"], item["bytes"],
                             attempt, accepted_seed))
        output.append(item)
    output.sort(key=lambda row: (TUNE_INDEX[str(row["tune"])], int(row["logical_id"])))
    if equality_source != equality_output or len(equality_source) != 3000:
        raise ValueError("portable manifest is not one-to-one with sealed source")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        for row in output:
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
    return output


def scheduler_inventory(root: Path | None) -> tuple[dict[tuple[str, int], list[Path]], dict[str, object] | None]:
    if root is None:
        return {}, None
    grouped: dict[tuple[str, int], list[Path]] = defaultdict(list)
    inventory_lines = []
    pattern = re.compile(r"job_(\d+)_(\d+)_(\d+)\.log$")
    for tune in TUNES:
        for path in sorted((root / tune).glob("*.log")):
            match = pattern.fullmatch(path.name)
            if not match:
                raise ValueError(f"unexpected scheduler log name: {path}")
            grouped[(tune, int(match.group(1)))].append(path)
            rel = path.relative_to(root).as_posix()
            inventory_lines.append(f"{rel}\t{path.stat().st_size}\t{sha256(path)}\n")
    payload = "".join(inventory_lines).encode("utf-8")
    return grouped, {"file_count": len(inventory_lines), "sha256": hashlib.sha256(payload).hexdigest()}


def log_timestamp(path: Path) -> tuple[int, int, int, int, int, int]:
    match = re.search(r"^000 \([^\n]+\) (\d{4})-(\d\d)-(\d\d) (\d\d):(\d\d):(\d\d)",
                      path.read_text(encoding="utf-8", errors="strict"), re.MULTILINE)
    if not match:
        raise ValueError(f"scheduler log lacks submission event: {path}")
    return tuple(int(value) for value in match.groups())  # type: ignore[return-value]


def build_attempts(source_rows: list[dict[str, object]], scheduler_root: Path | None,
                   path: Path) -> tuple[list[dict[str, object]], dict[str, object] | None]:
    grouped, inventory = scheduler_inventory(scheduler_root)
    rows = []
    for accepted in sorted(source_rows, key=lambda r: (TUNE_INDEX[str(r["tune"])], int(r["logical_id"]))):
        tune = str(accepted["tune"])
        logical_id = int(accepted["logical_id"])
        accepted_attempt = int(accepted["attempt"])
        logs = sorted(grouped.get((tune, logical_id), []), key=log_timestamp) if grouped else []
        accepted_receipt = Path(str(accepted["attempt_receipt_path"])).stem
        accepted_match = re.search(r"_(\d+)_(\d+)$", accepted_receipt)
        accepted_log = None
        if accepted_match:
            suffix = f"_{accepted_match.group(1)}_{accepted_match.group(2)}.log"
            accepted_log = next((candidate for candidate in logs if candidate.name.endswith(suffix)), None)
        if logs:
            if len(logs) != accepted_attempt + 1 or accepted_log is None or logs[-1] != accepted_log:
                raise ValueError(f"scheduler attempt sequence mismatch for {tune}/{logical_id}")
            for prior in logs[:-1]:
                text = prior.read_text(encoding="utf-8")
                if "012 (" not in text or "009 (" not in text:
                    raise ValueError(f"discarded scheduler log lacks held/aborted evidence: {prior}")
            accepted_text = accepted_log.read_text(encoding="utf-8")
            if "005 (" not in accepted_text or "Normal termination (return value 0)" not in accepted_text:
                raise ValueError(f"accepted scheduler log lacks successful termination: {accepted_log}")
        for attempt in range(accepted_attempt + 1):
            is_accepted = attempt == accepted_attempt
            rows.append({
                "tune": tune,
                "logical_id": logical_id,
                "attempt": attempt,
                "seed": seed(tune, logical_id, attempt),
                "outcome": "accepted" if is_accepted else "discarded",
                "evidence_status": (
                    "accepted_manifest_and_scheduler_log_confirmed" if is_accepted and logs else
                    "accepted_manifest_confirmed" if is_accepted else
                    "scheduler_log_confirmed" if logs else
                    "inferred_from_accepted_attempt_ordinal"
                ),
                "raw_storage_key": (Path(str(accepted["raw_path"])).relative_to("raw").as_posix()
                                    if is_accepted else ""),
            })
    fields = ("tune", "logical_id", "attempt", "seed", "outcome", "evidence_status", "raw_storage_key")
    write_csv(path, fields, rows)
    return rows, inventory


def parse_kv(line: str, prefix: str) -> dict[str, str]:
    result = {}
    for token in shlex.split(line[len(prefix):].strip()):
        if "=" not in token:
            raise ValueError(f"malformed {prefix} token: {token}")
        key, value = token.split("=", 1)
        result[key] = value
    return result


def deduplicate_structured(logs_dir: Path, prefix: str, names: tuple[str, ...]) -> tuple[list[dict[str, str]], int]:
    unique: dict[tuple[str, ...], dict[str, str]] = {}
    duplicates = 0
    for name in names:
        for line in (logs_dir / name).read_text(encoding="utf-8").splitlines():
            if not line.startswith(prefix):
                continue
            row = parse_kv(line, prefix)
            identity = (row["tune"], row["flavour"], row["trigger"], row["associate"],
                        row["bin"].removeprefix("hDPhi"))
            previous = unique.get(identity)
            if previous is None:
                unique[identity] = row
            elif previous == row:
                duplicates += 1
            else:
                raise ValueError(f"conflicting {prefix.strip()} identity {identity}")
    return list(unique.values()), duplicates


def pair_particles(os_file: str) -> tuple[str, str, str]:
    stem = Path(os_file).stem
    if stem not in PAIR_FILES:
        raise ValueError(f"unknown accepted OS pair file: {os_file}")
    trigger = next((name for name in ("Lambdacplus", "Bplus", "Dplus", "Lbbar") if stem.startswith(name)), None)
    if trigger is None:
        raise ValueError(f"cannot split pair file: {os_file}")
    os_associate = stem[len(trigger):]
    ss_stem = PAIR_FILES[stem]
    ss_associate = ss_stem[len(trigger):]
    return PAIR_PARTICLES[trigger], PAIR_PARTICLES[os_associate], PAIR_PARTICLES[ss_associate]


def activity_lookup(receipt: dict[str, object]) -> dict[tuple[str, str], tuple[str, float, float, int, int]]:
    result = {}
    tunes = receipt["tunes"]
    if not isinstance(tunes, dict):
        raise ValueError("boundary receipt tune map malformed")
    for tune in TUNES:
        tune_data = tunes[tune]
        classes = tune_data["classes"]  # type: ignore[index]
        for item in classes:
            low = float(item["percentile_min"])
            high = float(item["percentile_max"])
            key = f"M{fmt(low).removesuffix('.0')}_{fmt(high).removesuffix('.0')}"
            result[(tune, key)] = (f"percentile_{fmt(low).removesuffix('.0')}_{fmt(high).removesuffix('.0')}",
                                    low, high, int(item["nch_min_inclusive"]), int(item["nch_max_inclusive"]))
        maximum = max(int(item["nch_max_inclusive"]) for item in classes)
        result[(tune, "M00_100")] = ("integrated_0_100", 0.0, 100.0, 0, maximum)
    return result


def close(a: float, b: float, *, rel: float = 2e-14, absolute: float = 2e-16) -> bool:
    return math.isclose(a, b, rel_tol=rel, abs_tol=absolute)


def build_balancing(logs_dir: Path, boundary_path: Path, path: Path) -> dict[str, int]:
    matrices, duplicate_count = deduplicate_structured(logs_dir, "UNCERTAINTY_MATRIX", BALANCING_LOGS)
    counts, count_duplicates = deduplicate_structured(logs_dir, "PAIR_COUNTS", BALANCING_LOGS)
    if len(matrices) != 240 or duplicate_count != 182:
        raise ValueError(f"balancing diagnostics differ: {len(matrices)} unique, {duplicate_count} duplicates")
    count_map = {(r["tune"], r["flavour"], r["trigger"], r["associate"], r["bin"]): r for r in counts}
    boundaries = activity_lookup(json.loads(boundary_path.read_text(encoding="utf-8")))
    output = []
    emitted_central: set[tuple[str, str, str, str, str]] = set()
    yield_blocks: dict[tuple[str, str, str, str, str], list[float]] = {}
    reference_blocks: dict[tuple[str, str, str, str], list[float]] = {}
    rounded_block_trigger_rows = 0
    rounded_block_trigger_identities: set[tuple[str, str, str, str, str]] = set()
    for matrix in matrices:
        if matrix["is_reference"] == "true":
            bin_id = matrix["bin"].removeprefix("hDPhi")
            activity_id = boundaries[(matrix["tune"], bin_id)][0]
            reference_blocks[(matrix["tune"], matrix["flavour"].lower(), matrix["trigger"], activity_id)] = [
                float(value) for value in matrix["block_yields"].split(",")]
    rows_sorted = sorted(matrices, key=lambda r: (TUNE_INDEX[r["tune"]], r["flavour"], r["trigger"],
                                                   int(r["reference_index"]), r["associate"], r["bin"]))
    for matrix in rows_sorted:
        bin_id = matrix["bin"].removeprefix("hDPhi")
        activity_id, percentile_low, percentile_high, nch_low, nch_high = boundaries[(matrix["tune"], bin_id)]
        count = count_map.get((matrix["tune"], matrix["flavour"], matrix["trigger"],
                               matrix["associate"], bin_id))
        if count is None:
            raise ValueError(f"missing PAIR_COUNTS for {matrix}")
        trigger, os_associate, ss_associate = pair_particles(count["os_file"])
        central = float(matrix["central_yield"])
        n_os = exact_count_token(count["n_os"], source="PAIR_COUNTS n_os")
        n_ss = exact_count_token(count["n_ss"], source="PAIR_COUNTS n_ss")
        n_trigger = exact_count_token(count["n_trig"], source="PAIR_COUNTS n_trig")
        count_yield = (int(n_os) - int(n_ss)) / int(n_trigger)
        if not close(central, count_yield):
            raise ValueError(f"central balancing arithmetic mismatch: {matrix}")
        block_yields = [float(value) for value in matrix["block_yields"].split(",")]
        block_trigger_tokens = matrix["block_triggers"].split(",")
        if len(block_yields) != 10 or len(block_trigger_tokens) != 10:
            raise ValueError("balancing estimator does not expose ten blocks")
        sem = statistics.stdev(block_yields) / math.sqrt(10.0)
        if not close(sem, float(matrix["yield_sem"])):
            raise ValueError(f"yield SEM mismatch: {matrix}")
        identity = (matrix["tune"], matrix["flavour"].lower(), trigger, os_associate, activity_id)
        yield_blocks[identity] = block_yields
        emitted_central.add(identity)
        common = {
            "tune": matrix["tune"], "flavour": matrix["flavour"].lower(), "trigger": trigger,
            "os_associate": os_associate, "ss_associate": ss_associate, "activity_id": activity_id,
            "percentile_low": fmt(percentile_low), "percentile_high": fmt(percentile_high),
            "nch_low": nch_low, "nch_high": nch_high,
        }
        output.append({**common, "quantity": "balancing_yield", "estimator": "central",
                       "n_os": n_os, "n_ss": n_ss, "n_trigger": n_trigger,
                       "value": fmt(central), "status": "available_count_backed"})
        for index, (block_yield, block_trigger_token) in enumerate(
                zip(block_yields, block_trigger_tokens), 1):
            if re.fullmatch(r"[0-9]+", block_trigger_token):
                block_trigger = block_trigger_token
                block_status = "available_derived_no_component_counts"
            else:
                # Exactness is a property of the accepted source representation.
                # A rounded floating/scientific token must not become an apparent
                # integer merely because its parsed float happens to be integral.
                if not re.fullmatch(
                        r"(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?",
                        block_trigger_token):
                    raise ValueError(
                        f"unsupported non-integer block trigger token: {block_trigger_token!r}")
                parsed_block_trigger = float(block_trigger_token)
                if not math.isfinite(parsed_block_trigger) or parsed_block_trigger < 0:
                    raise ValueError(
                        f"invalid non-negative block trigger token: {block_trigger_token!r}")
                block_trigger = ""
                block_status = (
                    "available_derived_no_component_counts_trigger_count_rounded_in_source")
                rounded_block_trigger_rows += 1
                rounded_block_trigger_identities.add(identity)
            output.append({**common, "quantity": "balancing_yield", "estimator": f"block_{index:02d}",
                           "n_os": "", "n_ss": "", "n_trigger": block_trigger,
                           "value": fmt(block_yield), "status": block_status})
        output.append({**common, "quantity": "balancing_yield_sem", "estimator": "central",
                       "n_os": "", "n_ss": "", "n_trigger": "", "value": matrix["yield_sem"],
                       "status": "available_derived"})
        if matrix["is_reference"] == "false":
            reference = float(matrix["reference_yield"])
            ratios = [float(value) for value in matrix["block_ratios"].split(",")]
            reference_key = (matrix["tune"], matrix["flavour"].lower(), matrix["trigger"], activity_id)
            reference_values = reference_blocks.get(reference_key)
            if reference_values is None:
                raise ValueError(f"missing reference block yields: {reference_key}")
            for block_yield, reference_yield, ratio in zip(block_yields, reference_values, ratios):
                if not close(block_yield / reference_yield, ratio):
                    raise ValueError(f"within-block ratio mismatch: {matrix}")
            ratio_sem = statistics.stdev(ratios) / math.sqrt(10.0)
            if not close(ratio_sem, float(matrix["ratio_sem"])):
                raise ValueError(f"ratio SEM mismatch: {matrix}")
            output.append({**common, "quantity": "balancing_ratio_to_reference", "estimator": "central",
                           "n_os": "", "n_ss": "", "n_trigger": "", "value": fmt(central / reference),
                           "status": "available_derived"})
            for index, ratio in enumerate(ratios, 1):
                output.append({**common, "quantity": "balancing_ratio_to_reference",
                               "estimator": f"block_{index:02d}", "n_os": "", "n_ss": "",
                               "n_trigger": "", "value": fmt(ratio), "status": "available_derived"})
            output.append({**common, "quantity": "balancing_ratio_sem", "estimator": "central",
                           "n_os": "", "n_ss": "", "n_trigger": "", "value": matrix["ratio_sem"],
                           "status": "available_derived"})
    # PAIR_COUNTS exposes additional exact central yields that the accepted
    # figure set did not decorate with a ten-block uncertainty matrix.
    for count in count_map.values():
        trigger, os_associate, ss_associate = pair_particles(count["os_file"])
        activity_id, percentile_low, percentile_high, nch_low, nch_high = boundaries[(count["tune"], count["bin"])]
        identity = (count["tune"], count["flavour"].lower(), trigger, os_associate, activity_id)
        if identity in emitted_central:
            continue
        n_os = exact_count_token(count["n_os"], source="PAIR_COUNTS n_os")
        n_ss = exact_count_token(count["n_ss"], source="PAIR_COUNTS n_ss")
        n_trigger = exact_count_token(count["n_trig"], source="PAIR_COUNTS n_trig")
        value = (int(n_os) - int(n_ss)) / int(n_trigger)
        output.append({
            "tune": count["tune"], "flavour": count["flavour"].lower(), "trigger": trigger,
            "os_associate": os_associate, "ss_associate": ss_associate, "quantity": "balancing_yield",
            "activity_id": activity_id, "percentile_low": fmt(percentile_low),
            "percentile_high": fmt(percentile_high), "nch_low": nch_low, "nch_high": nch_high,
            "estimator": "central", "n_os": n_os, "n_ss": n_ss,
            "n_trigger": n_trigger, "value": fmt(value), "status": "available_count_backed",
        })
        emitted_central.add(identity)
    closure_groups: dict[tuple[str, str, str, str], list[dict[str, str]]] = defaultdict(list)
    trigger_groups: dict[tuple[str, str, str, str], set[int]] = defaultdict(set)
    for count in count_map.values():
        trigger, os_associate, _ = pair_particles(count["os_file"])
        closure_groups[(count["tune"], count["flavour"], trigger, os_associate)].append(count)
        trigger_groups[(count["tune"], count["flavour"], trigger, count["bin"])].add(int(count["n_trig"]))
    if any(len(values) != 1 for values in trigger_groups.values()):
        raise ValueError("trigger denominators differ between associates for a shared source class")
    closure_count = 0
    for identity, group in closure_groups.items():
        integrated = [row for row in group if row["bin"] == "M00_100"]
        classes = [row for row in group if row["bin"] != "M00_100"]
        if len(integrated) != 1 or len(classes) != 11:
            raise ValueError(f"activity-class topology mismatch: {identity}")
        total_triggers = sum(int(row["n_trig"]) for row in classes)
        total_os = sum(int(row["n_os"]) for row in classes)
        total_ss = sum(int(row["n_ss"]) for row in classes)
        central = integrated[0]
        if (total_triggers, total_os, total_ss) != (
                int(central["n_trig"]), int(central["n_os"]), int(central["n_ss"])):
            raise ValueError(f"activity count closure mismatch: {identity}")
        weighted = sum(((int(row["n_os"]) - int(row["n_ss"])) / int(row["n_trig"]))
                       * int(row["n_trig"]) for row in classes) / total_triggers
        integrated_yield = (int(central["n_os"]) - int(central["n_ss"])) / int(central["n_trig"])
        if not close(weighted, integrated_yield):
            raise ValueError(f"weighted activity-yield closure mismatch: {identity}")
        closure_count += 1
    fields = ("tune", "flavour", "trigger", "os_associate", "ss_associate", "quantity",
              "activity_id", "percentile_low", "percentile_high", "nch_low", "nch_high",
              "estimator", "n_os", "n_ss", "n_trigger", "value", "status")
    quantity_order = {"balancing_yield": 0, "balancing_yield_sem": 1,
                      "balancing_ratio_to_reference": 2, "balancing_ratio_sem": 3}
    output.sort(key=lambda row: (TUNE_INDEX[str(row["tune"])], str(row["flavour"]), str(row["trigger"]),
                                 str(row["os_associate"]), float(row["percentile_low"]),
                                 quantity_order[str(row["quantity"])], str(row["estimator"])))
    write_csv(path, fields, output)
    if rounded_block_trigger_rows != 90 or len(rounded_block_trigger_identities) != 9:
        raise ValueError(
            "rounded block-trigger topology differs from 90 rows across 9 identities: "
            f"rows={rounded_block_trigger_rows} identities={len(rounded_block_trigger_identities)}")
    return {"reported_entries": len(matrices) + duplicate_count, "unique_identities": len(matrices),
            "exact_duplicates": duplicate_count, "conflicts": 0, "pair_count_exact_duplicates": count_duplicates,
            "output_rows": len(output), "activity_closure_identities": closure_count,
            "shared_trigger_denominator_identities": len(trigger_groups),
            "unique_pair_count_identities": len(count_map),
            "rounded_block_trigger_rows_omitted": rounded_block_trigger_rows,
            "rounded_block_trigger_identities": len(rounded_block_trigger_identities)}


def parse_macro(text: str, *, linewise: bool) -> dict[str, dict[str, object]]:
    """Parse numeric TH1D state using one parser in either of two scan modes."""
    array_pattern = re.compile(r"Double_t\s+(\w+)\[\d+\]\s*=\s*\{([^}]*)\};")
    uniform_pattern = re.compile(
        r'TH1D\s*\*(\w+)\s*=\s*new TH1D\("([^"]+)","[^"]*",(\d+),([^,;]+),([^;]+)\);')
    variable_pattern = re.compile(
        r'TH1D\s*\*(\w+)\s*=\s*new TH1D\("([^"]+)","[^"]*",(\d+),\s*(\w+)\s*\);')
    value_pattern = re.compile(r"(\w+)->SetBin(Content|Error)\((\d+),([^\)]+)\);")
    units = text.splitlines() if linewise else [text]
    arrays: dict[str, list[float]] = {}
    histograms: dict[str, dict[str, object]] = {}
    for unit in units:
        for match in array_pattern.finditer(unit):
            arrays[match.group(1)] = [float(value.strip()) for value in match.group(2).split(",") if value.strip()]
        for match in variable_pattern.finditer(unit):
            variable, name, bins, array_name = match.groups()
            edges = arrays.get(array_name)
            if edges is None:
                raise ValueError(f"histogram references unknown edge array {array_name}")
            if len(edges) != int(bins) + 1:
                raise ValueError(f"wrong edge count for {name}")
            histograms[variable] = {"name": name, "edges": edges, "content": {}, "error": {}}
        for match in uniform_pattern.finditer(unit):
            variable, name, bins_text, low_text, high_text = match.groups()
            bins = int(bins_text)
            low = float(low_text)
            high = float(high_text)
            edges = [low + (high - low) * index / bins for index in range(bins + 1)]
            histograms[variable] = {"name": name, "edges": edges, "content": {}, "error": {}}
        for match in value_pattern.finditer(unit):
            variable, kind, bin_text, value_text = match.groups()
            if variable not in histograms:
                continue
            target = "content" if kind == "Content" else "error"
            histograms[variable][target][int(bin_text)] = float(value_text)  # type: ignore[index]
    return histograms


def macro_completeness(text: str, histograms: dict[str, dict[str, object]],
                       path: Path) -> dict[str, int]:
    """Orthogonally account for constructors and supported numeric mutations."""
    constructor_starts = list(re.finditer(r"\bnew\s+TH1D\s*\(", text))
    constructor_statements = list(re.finditer(
        r'TH1D\s*\*\w+\s*=\s*new\s+TH1D\("[^"]+","[^"]*",\d+,'
        r'(?:[^,;]+,[^;]+|\s*\w+\s*)\);', text))
    if len(constructor_starts) != len(constructor_statements):
        raise ValueError(
            f"unsupported or unaccounted TH1D constructor in accepted macro: {path}")
    if len(histograms) != len(constructor_starts):
        raise ValueError(f"TH1D constructor variables are not one-to-one in accepted macro: {path}")

    mutation_starts = list(re.finditer(r"\b\w+\s*->\s*SetBin(?:Content|Error)\s*\(", text))
    mutation_statements = list(re.finditer(
        r"\b(\w+)\s*->\s*SetBin(Content|Error)\s*\(\s*(\d+)\s*,\s*([^\)]+)\s*\)\s*;",
        text))
    if len(mutation_starts) != len(mutation_statements):
        raise ValueError(
            f"unsupported or unaccounted SetBinContent/SetBinError mutation: {path}")
    parser_shaped_mutations = list(re.finditer(
        r"(\w+)->SetBin(Content|Error)\((\d+),([^\)]+)\);", text))
    if len(parser_shaped_mutations) != len(mutation_starts):
        raise ValueError(f"macro parser does not consume every supported bin mutation: {path}")
    unknown_targets = sorted({match.group(1) for match in mutation_statements
                              if match.group(1) not in histograms})
    if unknown_targets:
        raise ValueError(f"numeric mutations target unparsed histograms in {path}: {unknown_targets}")

    # These ROOT methods can change numeric histogram state without a direct
    # SetBinContent/SetBinError statement. The accepted migration does not
    # interpret them, so their presence is a source-interpretation conflict.
    unsupported = sorted({match.group(1) for match in re.finditer(
        r"\b\w+\s*->\s*(FillN?|AddBinContent|SetContent|SetError|SetBins|Scale|"
        r"Add|Divide|Multiply|Rebin|Reset|Sumw2)\s*\(", text)})
    if unsupported:
        raise ValueError(f"unsupported numeric histogram mutation forms in {path}: {unsupported}")
    return {"macro_th1d_constructors_accounted": len(constructor_starts),
            "macro_set_bin_mutations_accounted": len(mutation_starts)}


def checked_macro(path: Path) -> tuple[dict[str, dict[str, object]], dict[str, int]]:
    text = path.read_text(encoding="utf-8")
    primary = parse_macro(text, linewise=False)
    linewise = parse_macro(text, linewise=True)
    if primary != linewise:
        raise ValueError(f"whole-text and linewise macro scan modes disagree: {path}")
    return primary, macro_completeness(text, primary, path)


def hist_value(histogram: dict[str, object], field: str, index: int) -> float:
    return float(histogram[field].get(index, 0.0))  # type: ignore[union-attr]


def build_correlations(logs_dir: Path, artifact_root: Path, path: Path) -> dict[str, int]:
    source = []
    log_path = logs_dir / "render_VCORRELATIONS.log"
    for line in log_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("CORRELATION_BIN_UNCERTAINTY"):
            source.append(parse_kv(line, "CORRELATION_BIN_UNCERTAINTY"))
    if len(source) != 1200:
        raise ValueError(f"accepted correlation log has {len(source)} rows, expected 1200")
    output = []
    identities = set()
    source_values: dict[tuple[str, str, int], tuple[float, float]] = {}
    context_pattern = re.compile(r"(BEAUTY|CHARM)_MONASH_(.+)\.root_(OSminusSS|OS|SS)$")
    for row in source:
        match = context_pattern.fullmatch(row["context"])
        if not match:
            raise ValueError(f"unknown correlation context: {row['context']}")
        flavour, pair, context_raw = match.groups()
        trigger, os_associate, _ = pair_particles(f"{pair}.root")
        context = {"OS": "os", "SS": "ss", "OSminusSS": "os_minus_ss"}[context_raw]
        index = int(row["bin"])
        low = -1.570796 + (index - 1) * (4.712389 + 1.570796) / 100.0
        high = -1.570796 + index * (4.712389 + 1.570796) / 100.0
        identity = (flavour.lower(), trigger, os_associate, context, index)
        if identity in identities:
            raise ValueError(f"duplicate correlation identity: {identity}")
        identities.add(identity)
        source_values[(pair, context, index)] = (float(row["central"]), float(row["stdError"]))
        output.append({
            "tune": "MONASH", "flavour": flavour.lower(), "trigger": trigger,
            "associate": os_associate, "context": context, "activity_id": "integrated_0_100",
            "bin_index": index, "dphi_low": fmt(low), "dphi_high": fmt(high),
            "value": row["central"], "stat_error": row["stdError"],
            "status": "available_central_sem_only",
        })
    # Accepted canvas macros are a deliberately lower-precision second view.
    macro_views = {
        "CHARM": (artifact_root / "G2_G3/CHARMCorrelations_MONASH_MACRO.C",
                  ("DplusDminus", "LambdacplusDminus")),
        "BEAUTY": (artifact_root / "G2_G3/BEAUTYCorrelations_MONASH_MACRO.C",
                   ("BplusBminus", "LbbarBminus")),
    }
    checked_values = 0
    constructor_count = 0
    mutation_count = 0
    for _, (macro_path, pairs) in macro_views.items():
        parsed, completeness = checked_macro(macro_path)
        histograms = list(parsed.values())
        constructor_count += completeness["macro_th1d_constructors_accounted"]
        mutation_count += completeness["macro_set_bin_mutations_accounted"]
        os_hists = [hist for hist in histograms if str(hist["name"]).startswith("hDPhiOS_copy")]
        ss_hists = [hist for hist in histograms if str(hist["name"]).startswith("hDPhiSS_copy")]
        diff_hists = [hist for hist in histograms if "_sub_copy" in str(hist["name"])]
        if tuple(map(len, (os_hists, ss_hists, diff_hists))) != (2, 2, 2):
            raise ValueError(f"unexpected accepted correlation macro topology: {macro_path}")
        for pair_index, pair in enumerate(pairs):
            for context, histogram in (("os", os_hists[pair_index]), ("ss", ss_hists[pair_index]),
                                       ("os_minus_ss", diff_hists[pair_index])):
                edges = histogram["edges"]
                if len(edges) != 101 or not close(float(edges[0]), -1.570796) or not close(float(edges[-1]), 4.712389):
                    raise ValueError(f"correlation macro axis mismatch: {macro_path}")
                for index in (1, 25, 50, 75, 100):
                    central, error = source_values[(pair, context, index)]
                    if not math.isclose(hist_value(histogram, "content", index), central, rel_tol=8e-7, abs_tol=8e-11):
                        raise ValueError(f"correlation macro central mismatch: {pair}/{context}/{index}")
                    if not math.isclose(hist_value(histogram, "error", index), error, rel_tol=8e-7, abs_tol=8e-11):
                        raise ValueError(f"correlation macro error mismatch: {pair}/{context}/{index}")
                    checked_values += 2
    output.sort(key=lambda r: (r["flavour"], r["trigger"], r["associate"], r["context"], r["bin_index"]))
    fields = ("tune", "flavour", "trigger", "associate", "context", "activity_id",
              "bin_index", "dphi_low", "dphi_high", "value", "stat_error", "status")
    write_csv(path, fields, output)
    return {"rows": len(output), "unique_identities": len(identities),
            "macro_crosscheck_values": checked_values, "source_macros": len(macro_views),
            "selected_histogram_constructors": 12,
            "macro_th1d_constructors_accounted": constructor_count,
            "macro_set_bin_mutations_accounted": mutation_count}


def build_multiplicity(artifact_root: Path, path: Path) -> dict[str, int]:
    macro = artifact_root / "G1/MultiplicitySpectrum_Shared_shape.C"
    histograms, completeness = checked_macro(macro)
    selected = {}
    pattern = re.compile(r"hPlot_MultiplicitySpectrum_Shared_shape_(MONASH|JUNCTIONS|CLOSEPACKING)__")
    for histogram in histograms.values():
        match = pattern.match(str(histogram["name"]))
        if match:
            selected[match.group(1)] = histogram
    if set(selected) != set(TUNES):
        raise ValueError("accepted multiplicity macro lacks one selected tune histogram")
    rows = []
    for tune in TUNES:
        histogram = selected[tune]
        edges = histogram["edges"]
        if len(edges) != 4097:
            raise ValueError("multiplicity histogram does not have 4096 bins")
        for index in range(1, 4097):
            value = hist_value(histogram, "content", index)
            error = hist_value(histogram, "error", index)
            rows.append({"tune": tune, "bin_index": index, "nch_low": fmt(float(edges[index - 1])),
                         "nch_high": fmt(float(edges[index])), "count_or_content": "", "stat_error": "",
                         "normalized_value": fmt(value), "normalized_error": fmt(error),
                         "status": "available_normalized_only" if value or error else "empty_bin"})
    fields = ("tune", "bin_index", "nch_low", "nch_high", "count_or_content", "stat_error",
              "normalized_value", "normalized_error", "status")
    write_csv(path, fields, rows)
    return {"rows": len(rows), "bins_per_tune": 4096, "source_macros": 1,
            "selected_histogram_constructors": len(selected), **completeness}


def build_kinematics(artifact_root: Path, path: Path) -> dict[str, int]:
    rows = []
    constructor_count = 0
    mutation_count = 0
    selected_constructor_count = 0
    expected_bins = {"pt": 110, "eta": 100, "phi": 100}
    source_obs = {"pt": "pT", "eta": "eta", "phi": "phi"}
    for observable in ("pt", "eta", "phi"):
        source_observable = source_obs[observable]
        for species in SPECIES:
            macro = artifact_root / f"G9/{source_observable}/Inclusive_{source_observable}_{species}_shape.C"
            histograms, completeness = checked_macro(macro)
            constructor_count += completeness["macro_th1d_constructors_accounted"]
            mutation_count += completeness["macro_set_bin_mutations_accounted"]
            selected = {}
            prefix = f"hPlot_Inclusive_{source_observable}_{species}_shape_"
            for histogram in histograms.values():
                name = str(histogram["name"])
                for tune in TUNES:
                    if name.startswith(prefix + tune + "__"):
                        selected[tune] = histogram
            if set(selected) != set(TUNES):
                raise ValueError(f"accepted kinematic macro lacks tune histogram: {macro}")
            selected_constructor_count += len(selected)
            for tune in TUNES:
                histogram = selected[tune]
                edges = histogram["edges"]
                if len(edges) != expected_bins[observable] + 1:
                    raise ValueError(f"wrong accepted kinematic bin count: {macro}")
                for index in range(1, len(edges)):
                    value = hist_value(histogram, "content", index)
                    error = hist_value(histogram, "error", index)
                    rows.append({"tune": tune, "species": SPECIES_TOKEN[species], "pdg": PDG[species],
                                 "observable": observable, "bin_index": index,
                                 "bin_low": fmt(float(edges[index - 1])), "bin_high": fmt(float(edges[index])),
                                 "count_or_content": "", "stat_error": "", "normalized_value": fmt(value),
                                 "normalized_error": fmt(error),
                                 "status": "available_normalized_only" if value or error else "empty_bin"})
    rows.sort(key=lambda r: (TUNE_INDEX[str(r["tune"])], r["species"], r["observable"], r["bin_index"]))
    fields = ("tune", "species", "pdg", "observable", "bin_index", "bin_low", "bin_high",
              "count_or_content", "stat_error", "normalized_value", "normalized_error", "status")
    write_csv(path, fields, rows)
    return {"rows": len(rows), "source_macros": 30,
            "selected_histogram_constructors": selected_constructor_count,
            "macro_th1d_constructors_accounted": constructor_count,
            "macro_set_bin_mutations_accounted": mutation_count}


def build_sample_counts(artifact_root: Path, csv_path: Path, tex_path: Path) -> dict[str, int]:
    quantity_definitions = (
        ("events", "Successful generated events", None, "events"),
        ("final_heavy_hadrons", "Final heavy hadrons", None, "hadrons"),
        ("charm_constituent_sum", "Charm plus anticharm constituent sum", None, "constituents"),
        ("beauty_constituent_sum", "Beauty plus antibeauty constituent sum", None, "constituents"),
        ("bplus_hadrons", "B+ hadrons", 521, "hadrons"),
        ("bminus_hadrons", "B- hadrons", -521, "hadrons"),
        ("lambdab_hadrons", "Lambda_b hadrons", 5122, "hadrons"),
        ("lambdabbar_hadrons", "anti-Lambda_b hadrons", -5122, "hadrons"),
        ("dplus_hadrons", "D+ hadrons", 411, "hadrons"),
        ("dminus_hadrons", "D- hadrons", -411, "hadrons"),
        ("lambdacplus_hadrons", "Lambda_c+ hadrons", 4122, "hadrons"),
        ("lambdacplusbar_hadrons", "anti-Lambda_c hadrons", -4122, "hadrons"),
    )
    source_species = {
        "bplus_hadrons": "Bplus", "bminus_hadrons": "Bminus", "lambdab_hadrons": "Lambdab",
        "lambdabbar_hadrons": "Lambdabbar", "dplus_hadrons": "Dplus", "dminus_hadrons": "Dminus",
        "lambdacplus_hadrons": "Lambdacplus", "lambdacplusbar_hadrons": "Lambdacplusbar",
    }
    rows = []
    values_by_quantity: dict[str, dict[str, int]] = defaultdict(dict)
    labels = {}
    for tune in TUNES:
        source = json.loads((artifact_root / f"T1/t1_{tune}.json").read_text(encoding="utf-8"))
        if source["tune"] != tune or int(source["events"]) != 100_000_000:
            raise ValueError(f"sample count source identity mismatch: {tune}")
        values = {
            "events": int(source["events"]), "final_heavy_hadrons": int(source["final_heavy_hadrons"]),
            "charm_constituent_sum": int(source["content_sums"]["charm"]),
            "beauty_constituent_sum": int(source["content_sums"]["beauty"]),
        }
        values.update({key: int(source["species_yields"][source_name]) for key, source_name in source_species.items()})
        for quantity, label, pdg, unit in quantity_definitions:
            value = values[quantity]
            values_by_quantity[quantity][tune] = value
            labels[quantity] = label
            rows.append({"tune": tune, "quantity": quantity, "quantity_label": label,
                         "pdg": "" if pdg is None else pdg, "value": value, "unit": unit,
                         "status": "available_exact_count"})
    fields = ("tune", "quantity", "quantity_label", "pdg", "value", "unit", "status")
    write_csv(csv_path, fields, rows)
    tex_lines = [
        "% Generated deterministically from results/measurement/sample_counts.csv.",
        "\\begin{tabular}{lrrr}",
        "\\hline",
        "Quantity & MONASH & JUNCTIONS & CLOSEPACKING \\\\",
        "\\hline",
    ]
    for quantity, _, _, _ in quantity_definitions:
        label = labels[quantity].replace("_", "\\_")
        values = values_by_quantity[quantity]
        tex_lines.append(f"{label} & {values['MONASH']} & {values['JUNCTIONS']} & {values['CLOSEPACKING']} \\\\")
    tex_lines.extend(["\\hline", "\\end{tabular}", ""])
    tex_path.parent.mkdir(parents=True, exist_ok=True)
    tex_path.write_text("\n".join(tex_lines), encoding="utf-8")
    return {"rows": len(rows), "quantities_per_tune": len(quantity_definitions)}


def plot_specs() -> list[dict[str, str]]:
    specs = [
        {"record": "G1", "local": "G1/MultiplicitySpectrum_Shared_shape.pdf",
         "old": "KinematicSpectra/Multiplicity/MultiplicitySpectrum_Shared_shape.pdf",
         "new": "multiplicity_distribution.pdf",
         "macro_local": "G1/MultiplicitySpectrum_Shared_shape.C",
         "macro_old": "KinematicSpectra/Multiplicity/MultiplicitySpectrum_Shared_shape.C"},
        {"record": "G2", "local": "G2_G3/CHARMCorrelations_MONASH_PDF.pdf",
         "old": "THnSparse/Correlations/CHARMCorrelations_MONASH_PDF.pdf",
         "new": "correlation_charm_monash.pdf",
         "macro_local": "G2_G3/CHARMCorrelations_MONASH_MACRO.C",
         "macro_old": "THnSparse/Correlations/CHARMCorrelations_MONASH_MACRO.C"},
        {"record": "G3", "local": "G2_G3/BEAUTYCorrelations_MONASH_PDF.pdf",
         "old": "THnSparse/Correlations/BEAUTYCorrelations_MONASH_PDF.pdf",
         "new": "correlation_beauty_monash.pdf",
         "macro_local": "G2_G3/BEAUTYCorrelations_MONASH_MACRO.C",
         "macro_old": "THnSparse/Correlations/BEAUTYCorrelations_MONASH_MACRO.C"},
    ]
    balancing = (
        ("G4", "G4_G6", "VariantIntegrated", "global_balancing_plots_integrated_charm", "balancing_integrated_charm.pdf"),
        ("G5", "G5_G7", "VariantExtremes", "global_balancing_plots_multiplicity_charm", "balancing_activity_charm.pdf"),
        ("G6", "G4_G6", "VariantIntegrated", "global_balancing_plots_integrated_beauty", "balancing_integrated_beauty.pdf"),
        ("G7", "G5_G7", "VariantExtremes", "global_balancing_plots_multiplicity_beauty", "balancing_activity_beauty.pdf"),
        ("G8", "G8", "VariantBaryonMeson", "global_balancing_baryon_over_meson_ratio_multiplicity",
         "balancing_baryon_meson_ratio_activity.pdf"),
    )
    for record, local_dir, old_dir, stem, new in balancing:
        specs.append({"record": record, "local": f"{local_dir}/{stem}_PDF.pdf",
                      "old": f"{old_dir}/{stem}_PDF.pdf", "new": new,
                      "macro_local": f"{local_dir}/{stem}_MACRO.C",
                      "macro_old": f"{old_dir}/{stem}_MACRO.C"})
    for observable in ("pT", "eta", "phi"):
        for species in SPECIES:
            base = f"Inclusive_{observable}_{species}_shape"
            specs.append({"record": "G9", "local": f"G9/{observable}/{base}.pdf",
                          "old": f"KinematicSpectra/Inclusive/{observable}/{base}.pdf",
                          "new": f"kinematics_{observable.lower()}_{SPECIES_TOKEN[species]}.pdf",
                          "macro_local": f"G9/{observable}/{base}.C",
                          "macro_old": f"KinematicSpectra/Inclusive/{observable}/{base}.C"})
    if len(specs) != 38 or len({spec["new"] for spec in specs}) != 38:
        raise AssertionError("canonical plot specification must contain 38 unique names")
    return specs


def acceptance_records(artifact_root: Path) -> tuple[dict[str, dict[str, object]], list[dict[str, object]]]:
    records = {}
    source_entries = []
    for record_id in [f"G{index}" for index in range(1, 10)]:
        path = artifact_root / f"records/RUNN4B_{record_id}.json"
        record = json.loads(path.read_text(encoding="utf-8"))
        if record["id"] != record_id or record["deployed_head"] != RENDER_HEAD:
            raise ValueError(f"acceptance-record identity mismatch: {path}")
        records[record_id] = record
        source_entries.append(source_entry(f"acceptance_records/RUNN4B_{record_id}.json", "acceptance_record", path))
    count_path = artifact_root / "records/RUNN_T1.json"
    count_record = json.loads(count_path.read_text(encoding="utf-8"))
    if count_record["deployed_head"] != COUNT_HEAD:
        raise ValueError("T1 acceptance-record head mismatch")
    records["T1"] = count_record
    source_entries.append(source_entry("acceptance_records/RUNN_T1.json", "acceptance_record", count_path))
    return records, source_entries


def validate_record_output(record: dict[str, object], accepted_name: str, local_path: Path) -> None:
    outputs = {str(item["name"]): item for item in record["outputs"]}  # type: ignore[index]
    if accepted_name not in outputs:
        raise ValueError(f"accepted artifact absent from record: {accepted_name}")
    expected = outputs[accepted_name]
    actual = file_identity(local_path)
    if actual != {"bytes": int(expected["bytes"]), "sha256": str(expected["sha256"])}:
        raise ValueError(f"accepted artifact hash/size mismatch: {accepted_name}")


def collect_and_copy_accepted_artifacts(artifact_root: Path, plots_dir: Path) -> tuple[list[dict[str, object]], list[dict[str, str]]]:
    records, sources = acceptance_records(artifact_root)
    mappings = []
    plots_dir.mkdir(parents=True, exist_ok=True)
    seen_sources = {str(item["name"]) for item in sources}
    for spec in plot_specs():
        pdf_path = artifact_root / spec["local"]
        macro_path = artifact_root / spec["macro_local"]
        record = records[spec["record"]]
        validate_record_output(record, spec["old"], pdf_path)
        validate_record_output(record, spec["macro_old"], macro_path)
        shutil.copyfile(pdf_path, plots_dir / spec["new"])
        for logical_name, role, source_path in (
            (f"accepted_outputs/{spec['old']}", "accepted_plot_pdf", pdf_path),
            (f"accepted_outputs/{spec['macro_old']}", "accepted_canvas_macro", macro_path),
        ):
            if logical_name not in seen_sources:
                sources.append(source_entry(logical_name, role, source_path))
                seen_sources.add(logical_name)
        mappings.append({"old_name": spec["old"], "new_name": f"results/plots/{spec['new']}"})
    count_record = records["T1"]
    for tune in TUNES:
        name = f"t1_{tune}.json"
        local_path = artifact_root / f"T1/{name}"
        validate_record_output(count_record, name, local_path)
        sources.append(source_entry(f"accepted_outputs/{name}", "accepted_sample_count", local_path))
    return sources, mappings


def parse_card(path: Path) -> dict[str, str]:
    settings = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].split("!", 1)[0].strip()
        if "=" in line:
            key, value = line.split("=", 1)
            settings[key.strip()] = value.strip()
    return settings


def make_campaign(source_rows: list[dict[str, object]], freeze_path: Path, scheduler: dict[str, object] | None,
                  definition_root: Path) -> dict[str, object]:
    common_fields = (
        "campaign", "campaign_ordinal", "multiplicity_audit_events", "origin_algorithm",
        "producer_executable_sha256", "raw_schema", "repository_commit", "requested_successes",
        "schema", "selector", "tune_difference_allowlist_schema", "tune_difference_allowlist_sha256",
    )
    common = {}
    for field in common_fields:
        values = {json.dumps(row[field], sort_keys=True) for row in source_rows}
        if len(values) != 1:
            raise ValueError(f"sealed source common field is not common: {field}")
        common[field] = source_rows[0][field]
    card_digests = {tune: {str(row["effective_card_sha256"]) for row in source_rows if row["tune"] == tune}
                    for tune in TUNES}
    if any(len(values) != 1 for values in card_digests.values()):
        raise ValueError("effective card digest varies within a tune")
    study = json.loads((definition_root / "config/study.json").read_text(encoding="utf-8"))
    if study.get("schema") != "hadronization_study_v1" or study.get("scope", {}).get("variation_selection") is not False:
        raise ValueError("current nominal study definition is incomplete")
    cards = {}
    definition_entries = []
    card_names = {"MONASH": "monash.cmnd", "JUNCTIONS": "junctions.cmnd",
                  "CLOSEPACKING": "close_packing.cmnd"}
    for tune in TUNES:
        rel = f"config/tunes/{card_names[tune]}"
        card_path = definition_root / rel
        settings = parse_card(card_path)
        required = {"Beams:eCM": "13600", "HardQCD:hardccbar": "on", "HardQCD:hardbbbar": "on",
                    "PhaseSpace:pTHatMin": "2."}
        if any(settings.get(key) != value for key, value in required.items()):
            raise ValueError(f"current tune card physics identity mismatch: {card_path}")
        cards[tune] = {"accepted_effective_sha256": next(iter(card_digests[tune])),
                       "current_definition_sha256": sha256(card_path)}
        definition_entries.append((rel, card_path))
    producer = definition_root / "pipeline/generate/producer.cpp"
    producer_text = producer.read_text(encoding="utf-8")
    if "StabilizeHeavyHadrons" not in producer_text or "mayDecay(id, false)" not in producer_text:
        raise ValueError("current runtime/decay definition is incomplete")
    definition_entries.extend((
        ("config/study.json", definition_root / "config/study.json"),
        ("pipeline/generate/producer.cpp", producer),
        ("pipeline/generate/physics.hpp", definition_root / "pipeline/generate/physics.hpp"),
        ("pipeline/generate/selected_states.hpp", definition_root / "pipeline/generate/selected_states.hpp"),
        ("pipeline/generate/tune_settings.hpp", definition_root / "pipeline/generate/tune_settings.hpp"),
    ))
    return {
        "schema": "hadronization_campaign_record_v1", "version": 1, "campaign": "HF_RUN3_V1",
        "tune_order": list(TUNES), "logical_jobs_per_tune": 1000,
        "successful_events_per_logical_job": 100_000, "successful_events_per_tune": 100_000_000,
        "blocks": {"count": 10, "logical_id_rule": "block=(logical_id%10)+1", "logical_id_domain": [0, 999]},
        "seed": {"schema": "seed_derivation_v2",
                 "formula": "100000001+campaign_ordinal*10000000+tune_ordinal*1000000+attempt*100000+logical_id",
                 "campaign_ordinal": 3, "tune_ordinals": {tune: TUNE_INDEX[tune] for tune in TUNES},
                 "attempt_domain": [0, 9]},
        "physics": {"beam": "pp", "sqrt_s_gev": 13600, "hard_processes": ["ccbar", "bbbar"],
                    "pthat_min_gev": 2.0, "heavy_hadron_decays": "disabled"},
        "runtime": {"pythia_version": "8.317"},
        "accepted_source": {"raw_manifest_sha256": sha256(freeze_path),
                            "raw_manifest_schema": common["schema"], "raw_schema": common["raw_schema"],
                            "producer_repository_commit": common["repository_commit"],
                            "producer_executable_sha256": common["producer_executable_sha256"],
                            "origin_algorithm": common["origin_algorithm"], "selector": common["selector"],
                            "tune_difference_allowlist": {"schema": common["tune_difference_allowlist_schema"],
                                                          "sha256": common["tune_difference_allowlist_sha256"]},
                            "tune_cards": cards},
        "current_interpretation_definitions": {
            "role": "interpretation_only_not_claimed_as_accepted_producer",
            "files": [{"path": rel, **file_identity(path)} for rel, path in definition_entries],
        },
        "attempt_evidence_inventory": scheduler or {"file_count": 0, "status": "not_supplied"},
        "systematic_uncertainties": "disabled",
        "held_attempt_policy": "record_and_disclose_no_correction",
    }


DATA_README = """# Data plane

`campaign.json`, `raw_manifest.jsonl`, `attempts.csv`, and portable raw objects
under ignored `raw/` are the canonical data objects. `work/` is ignored scratch.
"""


def result_artifact(path: Path, output_root: Path, *, producer: str, consumer: str,
                    old_name: str | None = None) -> dict[str, object]:
    result = {"path": path.relative_to(output_root).as_posix(), **file_identity(path),
              "producer": producer, "consumer": consumer}
    if old_name is not None:
        result["old_accepted_name"] = old_name
    return result


def validate_staging(output: Path) -> None:
    json.loads((output / "data/campaign.json").read_text(encoding="utf-8"))
    json.loads((output / "results/manifest.json").read_text(encoding="utf-8"))
    for line in (output / "data/raw_manifest.jsonl").read_text(encoding="utf-8").splitlines():
        json.loads(line)
    for path in sorted(output.rglob("*.csv")):
        with path.open(encoding="utf-8", newline="") as handle:
            list(csv.DictReader(handle))
    manifest = json.loads((output / "results/manifest.json").read_text(encoding="utf-8"))
    declared = {item["path"] for item in manifest["artifacts"]}
    actual = {path.relative_to(output).as_posix() for subtree in ("measurement", "plots", "tables")
              for path in (output / "results" / subtree).rglob("*") if path.is_file()}
    if declared != actual:
        raise ValueError(f"result manifest/file set mismatch: declared={declared ^ actual}")
    for item in manifest["artifacts"]:
        path = output / item["path"]
        if file_identity(path) != {"bytes": item["bytes"], "sha256": item["sha256"]}:
            raise ValueError(f"staged artifact identity mismatch: {path}")


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze-manifest", type=Path, required=True)
    parser.add_argument("--freeze-seal", type=Path, required=True)
    parser.add_argument("--logs-dir", type=Path, required=True)
    parser.add_argument("--scheduler-logs", type=Path)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--definition-root", type=Path, required=True)
    parser.add_argument("--import-starting-head", required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = arguments()
    output = args.output.resolve()
    if output.exists():
        raise SystemExit(f"refusing to write existing staging/output path: {output}")
    output.mkdir(parents=True)
    source_rows = load_source_manifest(args.freeze_manifest)
    raw_rows = build_raw_manifest(source_rows, output / "data/raw_manifest.jsonl")
    attempts, scheduler = build_attempts(source_rows, args.scheduler_logs, output / "data/attempts.csv")
    campaign = make_campaign(source_rows, args.freeze_manifest, scheduler, args.definition_root)
    write_json(output / "data/campaign.json", campaign)
    (output / "data/README.md").write_text(DATA_README, encoding="utf-8")

    measurement = output / "results/measurement"
    boundary_path = args.artifact_root / "G5_G7/multiplicity_boundary_receipt_v2.json"
    diagnostics = {
        "balancing": build_balancing(args.logs_dir, boundary_path, measurement / "balancing.csv"),
        "correlations": build_correlations(args.logs_dir, args.artifact_root, measurement / "correlations.csv"),
        "multiplicity": build_multiplicity(args.artifact_root, measurement / "multiplicity.csv"),
        "kinematics": build_kinematics(args.artifact_root, measurement / "kinematics.csv"),
        "sample_counts": build_sample_counts(args.artifact_root, measurement / "sample_counts.csv",
                                               output / "results/tables/sample_counts.tex"),
    }
    macro_diagnostics = (diagnostics["correlations"], diagnostics["multiplicity"],
                         diagnostics["kinematics"])
    diagnostics["macro_completeness"] = {
        "source_macros": sum(item["source_macros"] for item in macro_diagnostics),
        "selected_histogram_constructors": sum(
            item["selected_histogram_constructors"] for item in macro_diagnostics),
        "th1d_constructors_accounted": sum(
            item["macro_th1d_constructors_accounted"] for item in macro_diagnostics),
        "set_bin_content_or_error_mutations_accounted": sum(
            item["macro_set_bin_mutations_accounted"] for item in macro_diagnostics),
        "unsupported_numeric_mutation_forms": 0,
        "verification_method": "one_regex_parser_two_scan_modes_plus_orthogonal_lexical_accounting",
    }
    if diagnostics["macro_completeness"]["source_macros"] != 33:
        raise ValueError("accepted G1/G2/G3/G9 macro inventory does not contain 33 sources")
    source_artifacts, plot_mappings = collect_and_copy_accepted_artifacts(
        args.artifact_root, output / "results/plots")
    source_artifacts.extend((
        source_entry("freeze/canonical_manifest.jsonl", "sealed_raw_freeze", args.freeze_manifest),
        source_entry("freeze/freeze_seal.json", "sealed_raw_freeze_seal", args.freeze_seal),
        source_entry("accepted_outputs/multiplicity_boundary_receipt_v2.json", "activity_boundary_receipt", boundary_path),
    ))
    for name in ALL_LOGS:
        source_artifacts.append(source_entry(f"accepted_logs/{name}", "accepted_render_log", args.logs_dir / name))
    source_artifacts.sort(key=lambda item: str(item["name"]))
    if len({item["name"] for item in source_artifacts}) != len(source_artifacts):
        raise ValueError("duplicate source-artifact logical name")

    old_names = {item["new_name"]: item["old_name"] for item in plot_mappings}
    artifacts = []
    for path in sorted(measurement.glob("*.csv")):
        artifacts.append(result_artifact(path, output, producer="pipeline/analyze/import_accepted.py",
                                         consumer="canonical measurement parity and analysis consumers"))
    for path in sorted((output / "results/plots").glob("*.pdf")):
        rel = path.relative_to(output).as_posix()
        artifacts.append(result_artifact(path, output, producer=f"accepted render {RENDER_HEAD}",
                                         consumer="reviewed figure and publication consumers",
                                         old_name=old_names[rel]))
    table_path = output / "results/tables/sample_counts.tex"
    artifacts.append(result_artifact(table_path, output, producer="pipeline/analyze/import_accepted.py",
                                     consumer="sample-count table presentation"))
    data_files = {}
    for name in ("campaign.json", "raw_manifest.jsonl", "attempts.csv"):
        data_files[f"data/{name}"] = file_identity(output / f"data/{name}")
    manifest = {
        "schema": "hadronization_result_package_v1", "version": 1, "status": "migration_baseline",
        "campaign": {"id": "HF_RUN3_V1", "data_files": data_files},
        "import_commit": {"strategy": "git_commit_containing_this_manifest",
                          "starting_head": args.import_starting_head, "manifest_self_hash": None},
        "accepted_identities": {"figure_render_head_g1_g9": RENDER_HEAD,
                                "sample_count_head_t1": COUNT_HEAD,
                                "result_root_key": "HF_RUN3_V1/6729b3f0b7b9",
                                "source_freeze_sha256": FREEZE_SHA256},
        "source_locator": "/data/alice/ipardoza/hf/project/results/HF_RUN3_V1/6729b3f0b7b9",
        "source_artifacts": source_artifacts,
        "plot_name_mapping": plot_mappings,
        "artifacts": artifacts,
        "numeric_schema": "migration_accepted_double_text_v1",
        "observable_version": "hf_balancing_and_correlations_frozen_v1",
        "statistics_version": "ten_block_sample_sem_v1",
        "systematics": "disabled_not_included",
        "discarded_attempts": "recorded_no_correction",
        "validation": {
            "raw_rows": len(raw_rows), "attempt_rows": len(attempts),
            "discarded_by_tune": {tune: sum(row["tune"] == tune and row["outcome"] == "discarded"
                                                   for row in attempts) for tune in TUNES},
            "diagnostics": diagnostics,
        },
        "migration_limitations": [
            "balancing block rows expose accepted yields and exact trigger denominators where preserved, but not block OS/SS component counts",
            "90 D-plus integrated block rows omit n_trigger because the accepted log preserved 30 unique tune/block denominators only as rounded scientific text; their accepted block yields, ratios, and statistical SEMs are retained, and ANALYZE-1 will recover exact block sufficient statistics directly",
            "accepted logs expose one trigger denominator only after the renderer's OS/SS-denominator equality guard",
            "correlation bins expose central values and ten-block SEM, not the ten block-bin values",
            "multiplicity and kinematic canvas macros expose normalized content/error, not underlying raw counts",
            "portable raw rows omit common campaign fields, derivable block/seed fields, and nonportable source paths",
            "this baseline preserves accepted historical values and does not claim the current import head rendered them",
        ],
    }
    write_json(output / "results/manifest.json", manifest)
    validate_staging(output)


if __name__ == "__main__":
    main()
