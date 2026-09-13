import copy
import csv
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tempfile
import unittest

from helpers import ROOT, load_json, sha256


EXPECTED_ROWS = {
    "balancing.csv": 24768,
    "correlations.csv": 172800,
    "kinematics.csv": 9360,
    "multiplicity.csv": 40960,
    "sample_counts.csv": 1350,
}
LEGACY_ANALYSIS = ROOT / "tests/fixtures/analysis_v1_compact.json"
LEGACY_ANALYSIS_SHA256 = "2d386155e65a35951dbd9545b9f157b2f643b20ab81282cc0a38d2fa3fb5e4f9"


def close(left, right):
    return math.isclose(left, right, rel_tol=2e-13, abs_tol=2e-15)


def identity(path):
    return {"bytes": path.stat().st_size, "sha256": sha256(path)}


def validate_direct_compact(manifest):
    direct = manifest["direct_compact"]
    if (direct["schema"] != "hadronization_direct_compact_result_v1" or
            direct["state"] != "PUBLICATION_ELIGIBLE" or
            direct["estimator_policy"] != "pooled_delete_one_source_block_jackknife_v2"):
        raise AssertionError("direct compact state or estimator differs")
    roles = {"results/data/nominal.root": "compact_statistical_plot_source",
             "results/data/nominal.json": "compact_reduction_receipt"}
    artifacts = direct["artifacts"]
    if len(artifacts) != 2 or {entry["path"] for entry in artifacts} != set(roles):
        raise AssertionError("direct compact artifact set differs")
    for entry in artifacts:
        path = ROOT / entry["path"]
        if (path.is_symlink() or not path.is_file() or
                entry["role"] != roles[entry["path"]] or
                entry["producer"] != "pipeline/reduce/run.py" or
                entry["consumer"] != "pipeline/plot/run.py" or
                identity(path) != {key: entry[key] for key in ("bytes", "sha256")}):
            raise AssertionError("direct compact artifact binding differs")
    receipt = load_json("results/data/nominal.json")
    if receipt["state"] != direct["state"]:
        raise AssertionError("direct compact receipt state differs")
    for name in ("scientific_identity", "storage_identity", "producer_provenance"):
        digest = hashlib.sha256(json.dumps(
            receipt[name], sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        if digest != receipt[name + "_sha256"] or digest != direct[name + "_sha256"]:
            raise AssertionError("direct compact nested identity differs")
    scientific = receipt["scientific_identity"]
    for name in ("analysis_request_sha256", "scientific_content_digest",
                 "input_lineage_sha256", "parent_plan_digest", "parent_map_digest",
                 "compact_domains_sha256"):
        if scientific[name] != direct[name]:
            raise AssertionError("direct compact scientific binding differs")
    storage = receipt["storage_identity"]
    root_entry = next(entry for entry in artifacts if entry["path"].endswith(".root"))
    if (storage["root_sha256"] != root_entry["sha256"] or
            storage["root_bytes"] != root_entry["bytes"] or
            not 0 < storage["root_bytes"] < 89128960 or
            storage["compression"] != {"algorithm": "ZSTD", "level": 5} or
            storage["object_set"] != ["cells", "event_gram", "metadata", "receipt"]):
        raise AssertionError("direct compact physical identity differs")
    if (sha256(LEGACY_ANALYSIS) != LEGACY_ANALYSIS_SHA256 or
            scientific["analysis_request_sha256"] != LEGACY_ANALYSIS_SHA256 or
            scientific["events"] != 300000000 or scientific["sources"] != 3000):
        raise AssertionError("direct compact request or exposure differs")


def validate_package(manifest, check_files=True):
    if (manifest["schema"], manifest["version"], manifest["state"], manifest["status"]) != (
            "hadronization_result_package_v2", 2, "COMPLETE", "inclusive_pipeline_complete"):
        raise AssertionError("result package state/schema differs")
    if manifest["scope"] != {
            "analysis_profile": "inclusive",
            "claim": "inclusive pipeline-completion output",
            "presentation_preset": "paper_default",
            "relative_pt": {"deferred": False, "status": "not_in_scope"},
            "systematic_uncertainty": "disabled_and_absent",
            "uncertainty": "statistical_only"}:
        raise AssertionError("result package scope differs")
    validate_direct_compact(manifest)
    numerical = manifest["numerical_export"]
    render = manifest["plot_render"]
    if (numerical["schema"] != "hadronization_numerical_plot_export_v2" or
            numerical["version"] != "2.0.0" or numerical["state"] != "COMPLETE"):
        raise AssertionError("numerical export state/schema differs")
    if (render["schema"] != "hadronization_plot_render_v1" or
            render["version"] != "1.0.0" or render["state"] != "COMPLETE"):
        raise AssertionError("render state/schema differs")
    if (render["request_id"] != numerical["request_id"] or
            render["numerical_exports_sha256"] != numerical["numerical_exports_sha256"] or
            render["path_independent_files_sha256"] != numerical["numerical_exports_sha256"]):
        raise AssertionError("numerical/render identity binding differs")
    roles = render["roles"]
    if len(roles) != 42 or len({item["id"] for item in roles}) != 42:
        raise AssertionError("render role topology differs")
    if any(item["path"] != "results/plots/" + item["id"] + ".pdf" or
           item["pages"] != 1 for item in roles):
        raise AssertionError("render role path/page mapping differs")
    artifacts = manifest["artifacts"]
    listed = {entry["path"] for entry in artifacts}
    if len(artifacts) != 53 or len(listed) != 53:
        raise AssertionError("result artifact topology differs")
    required = ({"results/data/nominal.root", "results/data/nominal.json",
                 "results/numerical/manifest.json", "results/plots/manifest.json",
                 "results/plots/drawing-record.tsv"} |
                {item["path"] for item in numerical["files"]} |
                {item["path"] for item in roles})
    if listed != required:
        raise AssertionError("result artifact declarations differ")
    if not check_files:
        return
    actual = {path.relative_to(ROOT).as_posix() for path in (ROOT / "results").rglob("*")
              if path.is_file() and path != ROOT / "results/manifest.json"}
    if actual != listed:
        raise AssertionError("result filesystem differs from manifest")
    for entry in artifacts:
        pure = PurePosixPath(entry["path"])
        if pure.is_absolute() or ".." in pure.parts or pure.parts[0] != "results":
            raise AssertionError("unsafe result artifact path")
        if not entry["producer"] or not entry["consumer"]:
            raise AssertionError("result producer/consumer is absent")
        path = ROOT / entry["path"]
        if path.is_symlink() or identity(path) != {
                key: entry[key] for key in ("bytes", "sha256")}:
            raise AssertionError("result artifact identity differs")
    tracked = set(subprocess.run(
        ["git", "ls-files", "results"], cwd=ROOT, check=True,
        text=True, stdout=subprocess.PIPE).stdout.splitlines())
    if tracked != listed | {"results/manifest.json"}:
        raise AssertionError("tracked result set differs")


class ResultContract(unittest.TestCase):
    def test_package_manifest_scope_roles_paths_and_hashes(self):
        validate_package(load_json("results/manifest.json"))
        self.assertFalse((ROOT / "results/measurement").exists())
        self.assertFalse((ROOT / "results/tables").exists())

    def test_package_and_compact_binding_mutations_fail(self):
        changes = [
            lambda value: value["scope"]["relative_pt"].update(deferred=True),
            lambda value: value["artifacts"].pop(),
            lambda value: value["plot_render"].update(numerical_exports_sha256="0" * 64),
            lambda value: value["plot_render"]["roles"].pop(),
            lambda value: value["direct_compact"].update(input_lineage_sha256="0" * 64),
            lambda value: value["direct_compact"]["artifacts"][0].update(sha256="0" * 64),
        ]
        for change in changes:
            mutant = copy.deepcopy(load_json("results/manifest.json"))
            change(mutant)
            with self.assertRaises(AssertionError):
                validate_package(mutant, check_files=False)

    def test_child_manifests_exact_sets_and_digest_bindings(self):
        package = load_json("results/manifest.json")
        numerical = load_json("results/numerical/manifest.json")
        rendered = load_json("results/plots/manifest.json")
        self.assertEqual(identity(ROOT / "results/numerical/manifest.json"), {
            key: package["numerical_export"]["manifest"][key]
            for key in ("bytes", "sha256")})
        self.assertEqual(identity(ROOT / "results/plots/manifest.json"), {
            key: package["plot_render"]["manifest"][key]
            for key in ("bytes", "sha256")})
        self.assertEqual(set(numerical["filesystem_set"]), {
            path.name for path in (ROOT / "results/numerical").iterdir()})
        self.assertEqual(set(rendered["filesystem_set"]), {
            path.name for path in (ROOT / "results/plots").iterdir()})
        hashes = []
        for item in numerical["files"]:
            path = ROOT / "results/numerical" / item["name"]
            self.assertEqual(identity(path), {key: item[key] for key in ("bytes", "sha256")})
            hashes.append(item["sha256"])
        digest = hashlib.sha256(json.dumps(
            hashes, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        self.assertEqual(digest, numerical["numerical_exports_sha256"])
        self.assertEqual(rendered["drawing_record_sha256"],
                         sha256(ROOT / "results/plots/drawing-record.tsv"))
        self.assertEqual(rendered["roles"], sorted(item["id"] for item in numerical["roles"]))
        for item in rendered["files"]:
            self.assertEqual(identity(ROOT / "results/plots" / item["name"]),
                             {key: item[key] for key in ("bytes", "sha256")})

    def test_numerical_rows_and_renderer_consumed_values_are_exact(self):
        numerical = ROOT / "results/numerical"
        expected = {}
        for name, row_count in EXPECTED_ROWS.items():
            with (numerical / name).open(newline="") as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(len(rows), row_count, name)
            for row in rows:
                self.assertNotIn(row["semantic_id"], expected)
                if row["value"]:
                    self.assertTrue(math.isfinite(float(row["value"])))
                if row["finite_mc_error"]:
                    self.assertGreaterEqual(float(row["finite_mc_error"]), 0)
                if row["role_id"]:
                    expected[row["semantic_id"]] = (
                        None if not row["value"] else float(row["value"]),
                        None if not row["finite_mc_error"] else float(row["finite_mc_error"]))
        observed = {}
        with (ROOT / "results/plots/drawing-record.tsv").open() as stream:
            for line in stream:
                fields = line.rstrip("\n").split("\t")
                if fields[0] != "POINT":
                    continue
                self.assertNotIn(fields[4], observed)
                observed[fields[4]] = (
                    None if fields[7] == "-" else float.fromhex(fields[7]),
                    None if fields[8] == "-" else float.fromhex(fields[8]))
        self.assertEqual(len(observed), 76640)
        self.assertEqual(observed, expected)

    def test_pdf_integrity(self):
        pdfinfo = shutil.which("pdfinfo")
        if not pdfinfo:
            self.skipTest("pdfinfo unavailable")
        plots = sorted((ROOT / "results/plots").glob("*.pdf"))
        self.assertEqual(len(plots), 42)
        for path in plots:
            result = subprocess.run([pdfinfo, str(path)], text=True,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.assertEqual(result.returncode, 0, (path, result.stderr))
            self.assertRegex(result.stdout, r"(?m)^Pages:\s+1$")

    def test_canonical_compact_public_consumer_preserves_negative_and_zero(self):
        receipt = load_json("results/data/nominal.json")
        root_sha = receipt["storage_identity"]["root_sha256"]
        scientific_digest = receipt["scientific_identity"]["scientific_content_digest"]
        activity = "charged_light_sector_activity_a15_v1_eta4"
        with (ROOT / "results/numerical/correlations.csv").open(newline="") as stream:
            correlations = [row for row in csv.DictReader(stream)
                            if row["tune"] == "MONASH" and row["activity_id"] == activity
                            and row["profile"] == "inclusive" and row["class_id"] == "1"
                            and row["trigger_pdg"] == "521" and row["associate_pdg"] == "-521"
                            and row["bin_index"] == "23"]
        self.assertEqual({row["component"] for row in correlations},
                         {"OS", "SS", "OS_MINUS_SS"})
        for row in correlations:
            self.assertEqual(row["compact_root_sha256"], root_sha)
            self.assertEqual(row["compact_scientific_content_digest"], scientific_digest)
            self.assertEqual((row["value_status"], row["uncertainty_status"]),
                             ("AVAILABLE", "AVAILABLE"))
        correlation = {row["component"]: row for row in correlations}
        self.assertTrue(close(float(correlation["OS"]["value"]), 3 / 61542))
        self.assertTrue(close(float(correlation["SS"]["value"]), 6 / 61542))
        self.assertTrue(close(float(correlation["OS_MINUS_SS"]["value"]), -1 / 20514))
        self.assertEqual(len(correlation["OS_MINUS_SS"]["source_tune_complements"].split(";")), 10)
        with (ROOT / "results/numerical/multiplicity.csv").open(newline="") as stream:
            multiplicity = [row for row in csv.DictReader(stream)
                            if row["tune"] == "MONASH" and row["activity_id"] == activity
                            and row["bin_index"] == "4095"]
        self.assertEqual(len(multiplicity), 1)
        self.assertEqual((multiplicity[0]["value"], multiplicity[0]["variance"],
                          multiplicity[0]["finite_mc_error"]), ("0", "0", "0"))


if __name__ == "__main__":
    unittest.main()
