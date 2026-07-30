#!/usr/bin/env python3
"""Extract and audit the signed heavy-flavour registry against PDG 2025.

The committed reference is deliberately small.  It is reproducibly extracted
from two official PDG files whose URLs and SHA-256 digests are fixed below; the
23 MB SQLite database is not part of the repository.  Exit status 2 means that
all mechanical checks passed but the operational registry still needs physics
review.  It is never a PASS or an owner sign-off.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sqlite3
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REFERENCE_SCHEMA = "pdg_2025_heavy_flavour_species_reference_v1"
REPORT_SCHEMA = "hf_species_registry_pdg_audit_v1"
EXTRACTOR_VERSION = "pdg_2025_species_extractor_v1"
SQLITE_URL = "https://pdg.lbl.gov/2025/api/pdg-2025-v0.2.3.sqlite"
SQLITE_SHA256 = "4f1ecd7d9a55bc05f61618cc4574053c1edc6188fab07bb4bb7ebed69f9ec6d3"
MASS_WIDTH_URL = "https://pdg.lbl.gov/2025/mcdata/mass_width_2025.txt"
MASS_WIDTH_SHA256 = (
    "24df41d7db48d8be875dbc8f69aab95fdf26a0512cd8c033cef2d73cc92c24ef"
)
DEFAULT_REGISTRY = ROOT / "config/heavy_flavour_species_v1.json"
DEFAULT_REFERENCE = ROOT / "config/pdg_2025_species_reference_v1.json"
MASS_TOLERANCE_FLOOR_GEV = 0.005

PARTICLE_SQL = """
SELECT mcid, pdgid, name, cc_type, charge, quantum_j, quantum_p, quantum_c
FROM pdgparticle
WHERE abs(mcid) IN (
  411, 421, 431, 511, 521, 531, 541,
  4112, 4122, 4132, 4212, 4222, 4232, 4312, 4322, 4332,
  5112, 5122, 5132, 5212, 5222, 5232, 5312, 5322, 5332
)
ORDER BY abs(mcid), mcid DESC
""".strip()

XI_B_PRIME_SQL = """
SELECT mcid, pdgid, name, cc_type, charge, quantum_j, quantum_p, quantum_c
FROM pdgparticle
WHERE pdgid = 'B169'
ORDER BY cc_type DESC
""".strip()

XI_B_PRIME_MASS_SQL = """
SELECT p.pdgid, p.description, d.value, d.error_positive, d.error_negative,
       d.unit_text, d.display_value_text, d.value_type, d.edition,
       d.in_summary_table
FROM pdgid AS p
JOIN pdgdata AS d ON d.pdgid_id = p.id
WHERE p.pdgid = 'B169M'
  AND d.edition = '2025'
  AND d.in_summary_table = 1
ORDER BY d.sort
""".strip()

PDG_INFO_SQL = "SELECT name, value FROM pdginfo ORDER BY name"

REVIEW_GAPS = {
    5212: {
        "code": "SIGMA_B_ZERO_UNMEASURED_MODEL_MASS",
        "summary": (
            "PDG 2025 assigns MCID 5212 and lists Sigma_b0 quantum numbers, "
            "but provides no measured Sigma_b0 mass; its generator mass must "
            "not be described as a measured PDG value."
        ),
    },
    5312: {
        "code": "XI_B_PRIME_MINUS_NO_OFFICIAL_MCID",
        "summary": (
            "PDG 2025 lists the measured Xi_b'(5935)- state and mass but does "
            "not assign it MCID 5312; 5312 remains an operational PYTHIA "
            "mapping requiring physics review."
        ),
    },
    5322: {
        "code": "XI_B_PRIME_ZERO_NO_DIRECT_PDG_STATE_OR_MCID",
        "summary": (
            "PDG 2025 has neither an MCID 5322 assignment nor a directly "
            "listed measured Xi_b-prime-zero state/mass; this operational "
            "PYTHIA entry requires physics review."
        ),
    },
}

QUARK_CHARGE3 = {
    "d": -1,
    "u": 2,
    "s": -1,
    "c": 2,
    "b": -1,
    "t": 2,
}
FLAVOUR_TOKEN = {1: "d", 2: "u", 3: "s", 4: "c", 5: "b", 6: "t"}


def expected_classification(absolute: int) -> dict[str, str]:
    if absolute == 5212:
        return {
            "official_mcid_status": "OFFICIAL_MCID",
            "experimental_state_status": "UNMEASURED_MODEL_PREDICTION",
            "generator_mass_status": "QUARK_MODEL_OR_PYTHIA_ONLY",
        }
    if absolute == 5312:
        return {
            "official_mcid_status": "NO_OFFICIAL_MCID",
            "experimental_state_status": "MEASURED_XI_B_PRIME_MINUS_STATE",
            "generator_mass_status": "COMPARED_TO_MEASURED_PDG_2025_MASS",
        }
    if absolute == 5322:
        return {
            "official_mcid_status": "NO_OFFICIAL_MCID",
            "experimental_state_status": "NO_DIRECTLY_LISTED_MEASURED_STATE",
            "generator_mass_status": "QUARK_MODEL_OR_PYTHIA_ONLY",
        }
    return {
        "official_mcid_status": "OFFICIAL_MCID",
        "experimental_state_status": "MEASURED_PDG_2025",
        "generator_mass_status": "COMPARED_TO_MEASURED_PDG_2025_MASS",
    }


class AuditError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise AuditError(f"cannot read JSON {path}: {error}") from error
    if not isinstance(value, dict):
        raise AuditError(f"top-level JSON value is not an object: {path}")
    return value


def require_snapshot(path: Path, expected: str, label: str) -> None:
    if not path.is_file() or path.is_symlink():
        raise AuditError(f"{label} snapshot is not a regular file: {path}")
    observed = sha256(path)
    if observed != expected:
        raise AuditError(
            f"{label} SHA-256 mismatch: expected {expected}, observed {observed}"
        )


def spin2j1(quantum_j: str | None) -> int | None:
    if quantum_j == "0":
        return 1
    if quantum_j == "1/2":
        return 2
    return None


def anti(token: str) -> str:
    return token[:-3] if token.endswith("bar") else token + "bar"


def decode_operational_numbering(
    signed_pdg: int, kind: str
) -> tuple[list[str], list[int]]:
    absolute = abs(signed_pdg)
    is_anti = signed_pdg < 0
    if kind == "meson":
        heavy = (absolute // 100) % 10
        light = (absolute // 10) % 10
        if heavy not in FLAVOUR_TOKEN or light not in FLAVOUR_TOKEN:
            raise AuditError(f"invalid meson quark digits in {signed_pdg}")
        heavy_is_anti = (heavy % 2 != 0) ^ is_anti
        constituents = [
            FLAVOUR_TOKEN[heavy] + ("bar" if heavy_is_anti else ""),
            FLAVOUR_TOKEN[light] + ("" if heavy_is_anti else "bar"),
        ]
        return constituents, [heavy, light]
    if kind == "baryon":
        digits = [
            (absolute // 1000) % 10,
            (absolute // 100) % 10,
            (absolute // 10) % 10,
        ]
        if any(value not in FLAVOUR_TOKEN for value in digits):
            raise AuditError(f"invalid baryon quark digits in {signed_pdg}")
        suffix = "bar" if is_anti else ""
        return [FLAVOUR_TOKEN[value] + suffix for value in digits], digits
    raise AuditError(f"invalid hadron kind for {signed_pdg}: {kind}")


def parse_registry_valence(value: str) -> list[str]:
    tokens = value.split("(", 1)[0].split()
    if not tokens or any(
        token.removesuffix("bar") not in QUARK_CHARGE3 for token in tokens
    ):
        raise AuditError(f"cannot parse registry valence string: {value!r}")
    return tokens


def charge3(constituents: list[str]) -> int:
    total = 0
    for token in constituents:
        is_anti = token.endswith("bar")
        flavour = token.removesuffix("bar")
        total += QUARK_CHARGE3[flavour] * (-1 if is_anti else 1)
    return total


def heavy_content(constituents: list[str]) -> tuple[int, int]:
    values = {"c": 0, "b": 0}
    for token in constituents:
        is_anti = token.endswith("bar")
        flavour = token.removesuffix("bar")
        if flavour in values:
            values[flavour] += -1 if is_anti else 1
    return values["c"], values["b"]


def parse_mass_width(path: Path) -> dict[int, dict[str, Any]]:
    rows: dict[int, dict[str, Any]] = {}
    for line_number, line in enumerate(
        path.read_text(encoding="ascii").splitlines(), start=1
    ):
        if not line or line.startswith("*") or len(line) < 69:
            continue
        id_fields = [line[start : start + 8].strip() for start in range(0, 32, 8)]
        if not any(id_fields) or not all(
            not value or value.lstrip("-").isdigit() for value in id_fields
        ):
            continue
        mass_text = line[33:51].strip()
        if not mass_text:
            continue
        try:
            mass = float(mass_text)
            error_positive = abs(float(line[52:60].strip()))
            error_negative = abs(float(line[61:69].strip()))
        except ValueError as error:
            raise AuditError(
                f"cannot parse mass_width_2025.txt line {line_number}"
            ) from error
        for value in id_fields:
            if not value:
                continue
            mcid = int(value)
            if mcid in rows:
                raise AuditError(f"duplicate mass-width MCID {mcid}")
            rows[mcid] = {
                "value_gev": mass,
                "error_positive_gev": error_positive,
                "error_negative_gev": error_negative,
                "source": "mass_width_2025.txt",
                "source_line": line_number,
                "source_name_field": line[107:128].strip(),
            }
    return rows


def sqlite_rows(
    connection: sqlite3.Connection, query: str
) -> list[dict[str, Any]]:
    connection.row_factory = sqlite3.Row
    return [dict(row) for row in connection.execute(query)]


def validate_registry_state(state: dict[str, Any]) -> tuple[list[str], list[int]]:
    required = {
        "pdg",
        "name",
        "sector",
        "kind",
        "spin2j1",
        "charge3",
        "qc",
        "qb",
        "valence",
    }
    missing = required - state.keys()
    if missing:
        raise AuditError(f"registry row lacks {sorted(missing)}: {state}")
    pdg = int(state["pdg"])
    constituents, digits = decode_operational_numbering(pdg, str(state["kind"]))
    declared = parse_registry_valence(str(state["valence"]))
    if Counter(constituents) != Counter(declared):
        raise AuditError(
            f"registry valence disagrees with operational numbering for {pdg}: "
            f"{declared} versus {constituents}"
        )
    if charge3(constituents) != int(state["charge3"]):
        raise AuditError(f"registry charge disagrees with valence for {pdg}")
    qc, qb = heavy_content(constituents)
    if (qc, qb) != (int(state["qc"]), int(state["qb"])):
        raise AuditError(f"registry heavy content disagrees with valence for {pdg}")
    expected_spin = 1 if state["kind"] == "meson" else 2
    if int(state["spin2j1"]) != expected_spin:
        raise AuditError(f"registry ground-state spin is invalid for {pdg}")
    return constituents, digits


def extract_reference(
    sqlite_path: Path, mass_width_path: Path, registry_path: Path
) -> dict[str, Any]:
    require_snapshot(sqlite_path, SQLITE_SHA256, "PDG SQLite")
    require_snapshot(mass_width_path, MASS_WIDTH_SHA256, "PDG mass-width")
    registry = read_json(registry_path)
    if registry.get("schema") != "heavy_flavour_species_registry_v1":
        raise AuditError("unexpected operational species-registry schema")
    states = registry.get("signed_states")
    if not isinstance(states, list) or len(states) != 50:
        raise AuditError("operational registry must contain 50 signed states")

    mass_rows = parse_mass_width(mass_width_path)
    with sqlite3.connect(f"file:{sqlite_path}?mode=ro", uri=True) as connection:
        particles = sqlite_rows(connection, PARTICLE_SQL)
        xi_prime = sqlite_rows(connection, XI_B_PRIME_SQL)
        xi_prime_mass_rows = sqlite_rows(connection, XI_B_PRIME_MASS_SQL)
        info = dict(connection.execute(PDG_INFO_SQL))
    if info.get("producer") != "Particle Data Group (PDG)":
        raise AuditError("SQLite snapshot does not identify PDG as producer")
    if info.get("edition") != "2025" or info.get("status") != "production":
        raise AuditError("SQLite snapshot is not the production 2025 edition")

    by_mcid = {
        int(row["mcid"]): row for row in particles if row["mcid"] is not None
    }
    if len(by_mcid) != 46:
        raise AuditError(
            f"expected 46 signed official-MCID rows, found {len(by_mcid)}"
        )
    xi_by_cc = {str(row["cc_type"]): row for row in xi_prime}
    if set(xi_by_cc) != {"P", "A"}:
        raise AuditError("expected particle/antiparticle B169 records")
    if any(row["mcid"] is not None for row in xi_prime):
        raise AuditError("PDG unexpectedly assigned an MCID to B169")
    if len(xi_prime_mass_rows) != 1:
        raise AuditError("expected exactly one summary B169M mass")
    xi_mass = xi_prime_mass_rows[0]
    if xi_mass["unit_text"] != "MeV":
        raise AuditError("unexpected B169M mass unit")

    signed_rows: list[dict[str, Any]] = []
    observed_pdgs: set[int] = set()
    for state in states:
        pdg = int(state["pdg"])
        if pdg == 0 or pdg in observed_pdgs:
            raise AuditError(f"invalid or duplicate registry PDG ID {pdg}")
        observed_pdgs.add(pdg)
        constituents, digits = validate_registry_state(state)
        absolute = abs(pdg)
        review = REVIEW_GAPS.get(absolute)
        official: dict[str, Any] | None
        if absolute == 5312:
            official = xi_by_cc["P" if pdg > 0 else "A"]
        elif absolute == 5322:
            official = None
        else:
            official = by_mcid.get(pdg)
            if official is None:
                raise AuditError(f"official PDG MCID row is missing for {pdg}")

        official_particle = None
        if official is not None:
            observed_spin = spin2j1(official["quantum_j"])
            observed_charge3 = round(float(official["charge"]) * 3.0)
            if observed_spin != int(state["spin2j1"]):
                raise AuditError(f"PDG spin disagrees for {pdg}")
            if observed_charge3 != int(state["charge3"]):
                raise AuditError(f"PDG charge disagrees for {pdg}")
            if absolute not in {5312, 5322} and int(official["mcid"]) != pdg:
                raise AuditError(f"PDG MCID mapping disagrees for {pdg}")
            official_particle = {
                "pdgid": official["pdgid"],
                "canonical_name": official["name"],
                "charge_conjugation_type": official["cc_type"],
                "official_mcid": official["mcid"],
                "charge3": observed_charge3,
                "spin2j1": observed_spin,
                "parity": official["quantum_p"],
            }

        mass: dict[str, Any]
        if absolute == 5312:
            mass = {
                "status": "MEASURED_PDG_2025",
                "value_gev": float(xi_mass["value"]) / 1000.0,
                "error_positive_gev": float(xi_mass["error_positive"]) / 1000.0,
                "error_negative_gev": float(xi_mass["error_negative"]) / 1000.0,
                "source": "pdg-2025-v0.2.3.sqlite:B169M",
                "display_value": xi_mass["display_value_text"],
            }
        elif absolute in {5212, 5322}:
            if absolute in mass_rows:
                raise AuditError(
                    f"unexpected measured mass-width row for unresolved {absolute}"
                )
            mass = {
                "status": "NO_MEASURED_PDG_2025_MASS",
                "value_gev": None,
                "error_positive_gev": None,
                "error_negative_gev": None,
                "source": None,
            }
        else:
            source_mass = mass_rows.get(absolute)
            if source_mass is None:
                raise AuditError(f"mass-width row is missing for MCID {absolute}")
            mass = {"status": "MEASURED_PDG_2025", **source_mass}

        classification = expected_classification(absolute)

        signed_rows.append(
            {
                "signed_pdg": pdg,
                "registry_name": state["name"],
                "sector": state["sector"],
                "kind": state["kind"],
                "spin2j1": int(state["spin2j1"]),
                "charge3": int(state["charge3"]),
                "qc": int(state["qc"]),
                "qb": int(state["qb"]),
                "registry_valence": state["valence"],
                "operational_numbering": {
                    "kind": state["kind"],
                    "quark_digits": digits,
                    "constituents": constituents,
                    "official_mcid_corroborated": (
                        official is not None and official["mcid"] == pdg
                    ),
                },
                "official_particle": official_particle,
                "mass": mass,
                "classification": classification,
                "evidence_state": (
                    "NEEDS_PHYSICS_REVIEW" if review else "CORROBORATED"
                ),
                "review_code": review["code"] if review else None,
            }
        )

    if observed_pdgs != {-int(value) for value in observed_pdgs}:
        raise AuditError("registry lacks an explicit signed antiparticle")
    rows_by_pdg = {int(row["signed_pdg"]): row for row in signed_rows}
    for pdg, row in rows_by_pdg.items():
        partner = rows_by_pdg[-pdg]
        first = row["official_particle"]
        second = partner["official_particle"]
        if first is not None and second is not None:
            if first["pdgid"] != second["pdgid"]:
                raise AuditError(f"PDG antiparticle record mismatch for {pdg}")
            if {first["charge_conjugation_type"], second["charge_conjugation_type"]} != {
                "P",
                "A",
            }:
                raise AuditError(f"PDG charge-conjugation types mismatch for {pdg}")

    review_gaps = [
        {
            "abs_pdg": absolute,
            "signed_pdgs": [-absolute, absolute],
            **REVIEW_GAPS[absolute],
        }
        for absolute in sorted(REVIEW_GAPS)
    ]
    return {
        "schema": REFERENCE_SCHEMA,
        "reference_version": "PDG_2025_HEAVY_FLAVOUR_SPECIES_V1",
        "extractor": {
            "path": "tools/pdg_2025_species_audit.py",
            "version": EXTRACTOR_VERSION,
            "particle_sql": PARTICLE_SQL,
            "xi_b_prime_sql": XI_B_PRIME_SQL,
            "xi_b_prime_mass_sql": XI_B_PRIME_MASS_SQL,
            "pdg_info_sql": PDG_INFO_SQL,
            "mass_width_format": (
                "PDG fixed-width columns 1-32 MCIDs, 34-51 mass, "
                "53-60 positive error, 62-69 negative error, 108-128 name"
            ),
        },
        "sources": {
            "sqlite": {
                "url": SQLITE_URL,
                "sha256": SQLITE_SHA256,
                "repository_copy_committed": False,
            },
            "mass_width": {
                "url": MASS_WIDTH_URL,
                "sha256": MASS_WIDTH_SHA256,
                "repository_copy_committed": False,
            },
        },
        "snapshot_metadata": {
            key: info[key]
            for key in (
                "producer",
                "edition",
                "status",
                "schema_version",
                "citation",
                "license",
                "data_release_timestamp",
            )
            if key in info
        },
        "operational_registry": {
            "schema": registry["schema"],
            "sha256_at_extraction": sha256(registry_path),
            "signed_state_count": len(states),
        },
        "overall_evidence_state": "NEEDS_PHYSICS_REVIEW",
        "review_gaps": review_gaps,
        "signed_species": signed_rows,
    }


def check_reference_structure(reference: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if reference.get("schema") != REFERENCE_SCHEMA:
        failures.append("unexpected PDG reference schema")
    if reference.get("extractor", {}).get("version") != EXTRACTOR_VERSION:
        failures.append("unexpected PDG reference extractor version")
    expected_sources = {
        "sqlite": (SQLITE_URL, SQLITE_SHA256),
        "mass_width": (MASS_WIDTH_URL, MASS_WIDTH_SHA256),
    }
    sources = reference.get("sources", {})
    for name, (url, digest) in expected_sources.items():
        source = sources.get(name, {})
        if source.get("url") != url or source.get("sha256") != digest:
            failures.append(f"{name} source binding is invalid")
        if source.get("repository_copy_committed") is not False:
            failures.append(f"{name} repository-copy policy is invalid")
    extractor = reference.get("extractor", {})
    for key, expected in (
        ("particle_sql", PARTICLE_SQL),
        ("xi_b_prime_sql", XI_B_PRIME_SQL),
        ("xi_b_prime_mass_sql", XI_B_PRIME_MASS_SQL),
        ("pdg_info_sql", PDG_INFO_SQL),
    ):
        if extractor.get(key) != expected:
            failures.append(f"reference does not retain exact {key}")
    metadata = reference.get("snapshot_metadata", {})
    if (
        metadata.get("producer") != "Particle Data Group (PDG)"
        or metadata.get("edition") != "2025"
        or metadata.get("status") != "production"
    ):
        failures.append("PDG snapshot metadata is invalid")
    if reference.get("overall_evidence_state") != "NEEDS_PHYSICS_REVIEW":
        failures.append("PDG reference does not retain its unresolved state")
    return failures


def integer_field(row: dict[str, str], name: str) -> int:
    try:
        return int(row[name])
    except (KeyError, TypeError, ValueError) as error:
        raise AuditError(f"invalid PYTHIA CSV field {name}: {row}") from error


def float_field(row: dict[str, str], name: str) -> float:
    try:
        value = float(row[name])
    except (KeyError, TypeError, ValueError) as error:
        raise AuditError(f"invalid PYTHIA CSV field {name}: {row}") from error
    if not math.isfinite(value):
        raise AuditError(f"non-finite PYTHIA CSV field {name}: {row}")
    return value


def read_pythia_csv(path: Path) -> dict[int, dict[str, str]]:
    if not path.is_file() or path.is_symlink():
        raise AuditError(f"PYTHIA audit CSV is not a regular file: {path}")
    with path.open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    by_pdg: dict[int, dict[str, str]] = {}
    for row in rows:
        pdg = integer_field(row, "pdg")
        if pdg in by_pdg:
            raise AuditError(f"duplicate PYTHIA audit row {pdg}")
        by_pdg[pdg] = row
    return by_pdg


def audit(
    registry_path: Path,
    reference_path: Path,
    pythia_csv_path: Path | None,
    require_pythia: bool,
) -> dict[str, Any]:
    registry = read_json(registry_path)
    reference = read_json(reference_path)
    technical_failures = check_reference_structure(reference)
    states = registry.get("signed_states")
    reference_rows = reference.get("signed_species")
    if not isinstance(states, list):
        raise AuditError("operational registry signed_states is not a list")
    if not isinstance(reference_rows, list):
        raise AuditError("PDG reference signed_species is not a list")
    registry_by_pdg = {int(row["pdg"]): row for row in states}
    reference_by_pdg = {int(row["signed_pdg"]): row for row in reference_rows}
    if len(registry_by_pdg) != len(states):
        technical_failures.append("operational registry has duplicate PDG IDs")
    if len(reference_by_pdg) != len(reference_rows):
        technical_failures.append("PDG reference has duplicate signed PDG IDs")
    if set(registry_by_pdg) != set(reference_by_pdg):
        technical_failures.append(
            "operational registry and PDG reference signed-ID sets differ"
        )

    pythia_by_pdg: dict[int, dict[str, str]] | None = None
    if pythia_csv_path is not None:
        pythia_by_pdg = read_pythia_csv(pythia_csv_path)
        if set(pythia_by_pdg) != set(reference_by_pdg):
            technical_failures.append(
                "PYTHIA audit and PDG reference signed-ID sets differ"
            )
    elif require_pythia:
        technical_failures.append("required installed-PYTHIA audit is absent")

    comparison_rows: list[dict[str, Any]] = []
    for pdg in sorted(set(registry_by_pdg) | set(reference_by_pdg)):
        row_failures: list[str] = []
        state = registry_by_pdg.get(pdg)
        evidence = reference_by_pdg.get(pdg)
        if state is None or evidence is None:
            comparison_rows.append(
                {
                    "signed_pdg": pdg,
                    "state": "FAIL",
                    "failures": ["missing registry or reference row"],
                }
            )
            continue
        try:
            constituents, digits = validate_registry_state(state)
        except AuditError as error:
            row_failures.append(str(error))
            constituents, digits = [], []
        for registry_key, evidence_key in (
            ("name", "registry_name"),
            ("sector", "sector"),
            ("kind", "kind"),
            ("spin2j1", "spin2j1"),
            ("charge3", "charge3"),
            ("qc", "qc"),
            ("qb", "qb"),
            ("valence", "registry_valence"),
        ):
            if state.get(registry_key) != evidence.get(evidence_key):
                row_failures.append(
                    f"registry {registry_key} differs from curated PDG mapping"
                )
        numbering = evidence.get("operational_numbering", {})
        if numbering.get("constituents") != constituents:
            row_failures.append("curated operational constituents are stale")
        if numbering.get("quark_digits") != digits:
            row_failures.append("curated operational quark digits are stale")
        if evidence.get("classification") != expected_classification(abs(pdg)):
            row_failures.append(
                "measured/model/PYTHIA-only classification is invalid"
            )
        official = evidence.get("official_particle")
        if abs(pdg) not in {5312, 5322}:
            if not isinstance(official, dict) or official.get("official_mcid") != pdg:
                row_failures.append("official signed MCID mapping is absent")
        if isinstance(official, dict):
            if official.get("charge3") != int(state["charge3"]):
                row_failures.append("PDG charge differs from registry")
            if official.get("spin2j1") != int(state["spin2j1"]):
                row_failures.append("PDG spin differs from registry")
            if not official.get("canonical_name"):
                row_failures.append("PDG canonical name is empty")
        elif abs(pdg) != 5322:
            row_failures.append("expected PDG particle record is absent")

        pythia_comparison: dict[str, Any] = {"status": "NOT_RUN"}
        pythia = pythia_by_pdg.get(pdg) if pythia_by_pdg is not None else None
        if pythia is not None:
            for key, expected in (
                ("registry_name", state["name"]),
                ("sector", state["sector"]),
                ("kind", state["kind"]),
            ):
                if pythia.get(key) != str(expected):
                    row_failures.append(f"PYTHIA audit {key} mismatch")
            for key, expected in (
                ("charge3", int(state["charge3"])),
                ("spin2j1", int(state["spin2j1"])),
                ("decoded_qc", int(state["qc"])),
                ("decoded_qb", int(state["qb"])),
                ("is_hadron", 1),
                ("is_meson", 1 if state["kind"] == "meson" else 0),
                ("is_baryon", 1 if state["kind"] == "baryon" else 0),
                ("has_antiparticle", 1),
            ):
                if integer_field(pythia, key) != expected:
                    row_failures.append(f"PYTHIA audit {key} mismatch")
            constituent_counts = Counter(
                token.removesuffix("bar") for token in constituents
            )
            for flavour, key in (
                ("d", "n_down_in_code"),
                ("u", "n_up_in_code"),
                ("s", "n_strange_in_code"),
                ("c", "n_charm_in_code"),
                ("b", "n_beauty_in_code"),
            ):
                if integer_field(pythia, key) != constituent_counts[flavour]:
                    row_failures.append(
                        f"PYTHIA {flavour}-quark digit count mismatch"
                    )
            if pythia.get("pythia_result") != "PASS":
                row_failures.append("installed-PYTHIA row did not pass")
            if not pythia.get("pythia_name") or not pythia.get(
                "pythia_conjugate_name"
            ):
                row_failures.append("installed-PYTHIA name/antiparticle is empty")
            partner = (
                pythia_by_pdg.get(-pdg) if pythia_by_pdg is not None else None
            )
            if partner is None or pythia.get("pythia_conjugate_name") != partner.get(
                "pythia_name"
            ):
                row_failures.append("installed-PYTHIA antiparticle name mismatch")
            pythia_mass = float_field(pythia, "mass_gev")
            if pythia_mass <= 0.0:
                row_failures.append("installed-PYTHIA mass is not positive")
            mass = evidence.get("mass", {})
            mass_delta = None
            tolerance = None
            mass_classification = "MODEL_OR_PYTHIA_ONLY_NOT_PDG_MEASUREMENT"
            if mass.get("status") == "MEASURED_PDG_2025":
                pdg_mass = float(mass["value_gev"])
                tolerance = max(
                    MASS_TOLERANCE_FLOOR_GEV,
                    5.0
                    * max(
                        float(mass["error_positive_gev"]),
                        float(mass["error_negative_gev"]),
                    ),
                )
                mass_delta = pythia_mass - pdg_mass
                mass_classification = "COMPARED_TO_MEASURED_PDG_2025"
                if abs(mass_delta) > tolerance:
                    row_failures.append(
                        "installed-PYTHIA mass differs from measured PDG 2025 "
                        f"mass by {mass_delta:.9g} GeV (tolerance {tolerance:.9g})"
                    )
            pythia_comparison = {
                "status": "PASS" if not row_failures else "FAIL",
                "pythia_name": pythia.get("pythia_name"),
                "pythia_conjugate_name": pythia.get("pythia_conjugate_name"),
                "mass_gev": pythia_mass,
                "mass_classification": mass_classification,
                "pdg_mass_delta_gev": mass_delta,
                "pdg_mass_tolerance_gev": tolerance,
            }

        review_code = evidence.get("review_code")
        row_state = (
            "FAIL"
            if row_failures
            else "NEEDS_PHYSICS_REVIEW"
            if review_code
            else "PASS"
        )
        comparison_rows.append(
            {
                "signed_pdg": pdg,
                "registry_name": state.get("name"),
                "pdg_canonical_name": (
                    official.get("canonical_name")
                    if isinstance(official, dict)
                    else None
                ),
                "official_mcid": (
                    official.get("official_mcid")
                    if isinstance(official, dict)
                    else None
                ),
                "operational_numbering": evidence.get(
                    "operational_numbering"
                ),
                "classification": evidence.get("classification"),
                "mass": evidence.get("mass"),
                "pythia": pythia_comparison,
                "state": row_state,
                "review_code": review_code,
                "failures": row_failures,
            }
        )
        technical_failures.extend(
            f"PDG {pdg}: {failure}" for failure in row_failures
        )

    review_issues = reference.get("review_gaps")
    if not isinstance(review_issues, list):
        technical_failures.append("PDG reference review_gaps is not a list")
        review_issues = []
    observed_review_abs = {
        abs(int(row["signed_pdg"]))
        for row in reference_rows
        if row.get("review_code")
    }
    if observed_review_abs != set(REVIEW_GAPS):
        technical_failures.append("PDG reference review-gap set is invalid")
    if technical_failures:
        state = "FAIL"
    elif review_issues:
        state = "NEEDS_PHYSICS_REVIEW"
    else:
        state = "PASS"
    return {
        "schema": REPORT_SCHEMA,
        "state": state,
        "publication_gate_a_pass": state == "PASS",
        "physics_review_required": state == "NEEDS_PHYSICS_REVIEW",
        "owner_signoff_present": False,
        "owner_signoff_authored_or_inferred": False,
        "registry": {
            "path": str(registry_path),
            "sha256": sha256(registry_path),
            "schema": registry.get("schema"),
        },
        "pdg_reference": {
            "path": str(reference_path),
            "sha256": sha256(reference_path),
            "schema": reference.get("schema"),
            "source_bindings": reference.get("sources"),
        },
        "pythia_audit": (
            {
                "path": str(pythia_csv_path),
                "sha256": sha256(pythia_csv_path),
            }
            if pythia_csv_path is not None and pythia_csv_path.is_file()
            else None
        ),
        "technical_failures": technical_failures,
        "review_issues": review_issues,
        "signed_species": comparison_rows,
    }


def write_or_check(path: Path, value: dict[str, Any], check: bool) -> None:
    rendered = json_bytes(value)
    if check:
        if not path.is_file() or path.read_bytes() != rendered:
            raise AuditError(f"generated PDG reference is stale: {path}")
        return
    path.write_bytes(rendered)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    extract_parser = subparsers.add_parser(
        "extract", help="extract the checksum-bound curated PDG reference"
    )
    extract_parser.add_argument("--sqlite", type=Path, required=True)
    extract_parser.add_argument("--mass-width", type=Path, required=True)
    extract_parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    extract_parser.add_argument("--output", type=Path, default=DEFAULT_REFERENCE)
    extract_parser.add_argument("--check", action="store_true")

    check_parser = subparsers.add_parser(
        "check", help="audit registry and optional installed-PYTHIA CSV"
    )
    check_parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    check_parser.add_argument("--reference", type=Path, default=DEFAULT_REFERENCE)
    check_parser.add_argument("--pythia-csv", type=Path)
    check_parser.add_argument("--require-pythia", action="store_true")
    check_parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_arguments()
    try:
        if args.command == "extract":
            reference = extract_reference(
                args.sqlite.resolve(),
                args.mass_width.resolve(),
                args.registry.resolve(),
            )
            write_or_check(args.output.resolve(), reference, args.check)
            print(
                "PDG_REFERENCE_OK "
                f"state={reference['overall_evidence_state']} "
                f"signed_species={len(reference['signed_species'])}"
            )
            return 0
        report = audit(
            args.registry.resolve(),
            args.reference.resolve(),
            args.pythia_csv.resolve() if args.pythia_csv else None,
            args.require_pythia,
        )
        rendered = json_bytes(report)
        if args.output:
            args.output.resolve().write_bytes(rendered)
        print(rendered.decode(), end="")
        return {"PASS": 0, "FAIL": 1, "NEEDS_PHYSICS_REVIEW": 2}[report["state"]]
    except (AuditError, OSError, sqlite3.Error) as error:
        failure = {
            "schema": REPORT_SCHEMA,
            "state": "FAIL",
            "publication_gate_a_pass": False,
            "physics_review_required": False,
            "owner_signoff_present": False,
            "technical_failures": [str(error)],
        }
        rendered = json_bytes(failure)
        output = getattr(args, "output", None)
        # ``extract --output`` names the curated scientific reference itself.
        # A failed extraction/check must never replace that target with an
        # audit-error document.  Only the ``check`` subcommand's optional
        # report path is an appropriate failure-report destination.
        if args.command == "check" and output:
            output.resolve().write_bytes(rendered)
        print(rendered.decode(), end="", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
