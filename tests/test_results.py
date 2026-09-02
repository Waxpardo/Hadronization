import copy
from collections import defaultdict
import math
from pathlib import PurePosixPath
import shutil
import statistics
import subprocess
import unittest

from helpers import ROOT, csv_rows, git_blob, load_json, sha256


def close(left, right):
    return math.isclose(left, right, rel_tol=2e-13, abs_tol=2e-15)


def validate_balancing(rows):
    identity_fields = ("tune", "flavour", "trigger", "os_associate",
                       "ss_associate", "quantity", "activity_id", "estimator")
    identities = [tuple(row[field] for field in identity_fields) for row in rows]
    if len(identities) != len(set(identities)):
        raise AssertionError("balancing scientific identity is not unique")
    rounded_status = "available_derived_no_component_counts_trigger_count_rounded_in_source"
    associate_pairs = {("dminus", "dplus"), ("dzerobar", "dzero"),
                       ("lambdacplusbar", "lambdacplus")}
    expected_rounded = {
        (tune, "charm", "dplus", os_associate, ss_associate,
         "balancing_yield", "integrated_0_100", "block_{:02d}".format(index))
        for tune in ("MONASH", "JUNCTIONS", "CLOSEPACKING")
        for os_associate, ss_associate in associate_pairs
        for index in range(1, 11)}
    rounded_rows = [row for row in rows if row["status"] == rounded_status]
    measured_rounded = {
        (row["tune"], row["flavour"], row["trigger"], row["os_associate"],
         row["ss_associate"], row["quantity"], row["activity_id"],
         row["estimator"]) for row in rounded_rows}
    if len(rounded_rows) != 90 or measured_rounded != expected_rounded:
        raise AssertionError("rounded-source identity/status set is not exactly the required 90")
    for row in rows:
        for field in ("n_os", "n_ss", "n_trigger"):
            if row[field] and not row[field].isdigit():
                raise AssertionError("non-integer exact count")
        if row["status"] == rounded_status and row["n_trigger"]:
            raise AssertionError("rounded-source trigger count must be blank")
        if (row["quantity"] == "balancing_yield" and
                row["estimator"].startswith("block_") and
                row["status"] != rounded_status and not row["n_trigger"]):
            raise AssertionError("unexplained blank exact trigger count")

    base_fields = ("tune", "flavour", "trigger", "os_associate",
                   "ss_associate", "activity_id")
    grouped = defaultdict(dict)
    for row in rows:
        grouped[tuple(row[field] for field in base_fields)][
            (row["quantity"], row["estimator"])] = row
    sem_count = ratio_count = 0
    for base, group in grouped.items():
        central = group[("balancing_yield", "central")]
        if central["status"] == "available_count_backed":
            expected = ((int(central["n_os"]) - int(central["n_ss"])) /
                        int(central["n_trigger"]))
            if not close(float(central["value"]), expected):
                raise AssertionError("central count-backed yield arithmetic failed")
        if ("balancing_yield_sem", "central") in group:
            block_rows = [group[("balancing_yield", "block_{:02d}".format(index))]
                          for index in range(1, 11)]
            block_values = [float(row["value"]) for row in block_rows]
            expected_sem = statistics.stdev(block_values) / math.sqrt(10.0)
            if not close(float(group[("balancing_yield_sem", "central")]["value"]),
                         expected_sem):
                raise AssertionError("yield SEM does not reconstruct from blocks")
            if all(row["n_trigger"] for row in block_rows):
                if sum(int(row["n_trigger"]) for row in block_rows) != int(central["n_trigger"]):
                    raise AssertionError("block trigger counts do not close to central")
            sem_count += 1
        if ("balancing_ratio_to_reference", "central") not in group:
            continue
        prefix = (base[0], base[1], base[2], base[5])
        reference = [candidate for candidate, candidate_group in grouped.items()
                     if (candidate[0], candidate[1], candidate[2], candidate[5]) == prefix
                     and ("balancing_yield_sem", "central") in candidate_group
                     and ("balancing_ratio_to_reference", "central") not in candidate_group]
        if len(reference) != 1:
            raise AssertionError("ratio reference is not unique")
        reference_group = grouped[reference[0]]
        expected_central = (float(group[("balancing_yield", "central")]["value"]) /
                            float(reference_group[("balancing_yield", "central")]["value"]))
        if not close(float(group[("balancing_ratio_to_reference", "central")]["value"]),
                     expected_central):
            raise AssertionError("central ratio arithmetic failed")
        ratios = []
        for index in range(1, 11):
            estimator = "block_{:02d}".format(index)
            ratio = float(group[("balancing_ratio_to_reference", estimator)]["value"])
            numerator = float(group[("balancing_yield", estimator)]["value"])
            denominator = float(reference_group[("balancing_yield", estimator)]["value"])
            if not close(ratio, numerator / denominator):
                raise AssertionError("within-block ratio arithmetic failed")
            ratios.append(ratio)
        expected_ratio_sem = statistics.stdev(ratios) / math.sqrt(10.0)
        if not close(float(group[("balancing_ratio_sem", "central")]["value"]),
                     expected_ratio_sem):
            raise AssertionError("ratio SEM does not reconstruct from block ratios")
        ratio_count += 1

    closure_groups = defaultdict(list)
    for group in grouped.values():
        central = group[("balancing_yield", "central")]
        if central["status"] == "available_count_backed":
            closure_groups[(central["tune"], central["flavour"], central["trigger"],
                            central["os_associate"], central["ss_associate"])].append(central)
    for identity, group in closure_groups.items():
        integrated = [row for row in group if row["activity_id"] == "integrated_0_100"]
        classes = [row for row in group if row["activity_id"] != "integrated_0_100"]
        if len(integrated) != 1 or len(classes) != 11:
            raise AssertionError("activity-class topology failed")
        central = integrated[0]
        totals = tuple(sum(int(row[field]) for row in classes)
                       for field in ("n_trigger", "n_os", "n_ss"))
        expected = tuple(int(central[field]) for field in ("n_trigger", "n_os", "n_ss"))
        if totals != expected:
            raise AssertionError("activity count closure failed")
        weighted = sum(float(row["value"]) * int(row["n_trigger"]) for row in classes)
        weighted /= totals[0]
        if not close(weighted, float(central["value"])):
            raise AssertionError("weighted activity yield closure failed")
    if (sem_count, ratio_count) != (240, 150):
        raise AssertionError("balancing semantic coverage changed")


def validate_axis(table, group_fields, index, low, high, expected_groups,
                  expected_edges):
    groups = defaultdict(list)
    for row in table:
        groups[tuple(row[field] for field in group_fields)].append(row)
    if len(groups) != expected_groups:
        raise AssertionError("axis group count mismatch")
    for identity, rows in groups.items():
        rows.sort(key=lambda row: int(row[index]))
        edges = expected_edges(identity) if callable(expected_edges) else expected_edges
        if len(rows) != len(edges) - 1:
            raise AssertionError("axis group has wrong exact bin count")
        if [int(row[index]) for row in rows] != list(range(1, len(edges))):
            raise AssertionError("non-contiguous/duplicate result bin")
        for position, row in enumerate(rows):
            if (not close(float(row[low]), float(edges[position])) or
                    not close(float(row[high]), float(edges[position + 1]))):
                raise AssertionError("axis group edge sequence differs from study contract")
        for left, right in zip(rows, rows[1:]):
            if not close(float(left[high]), float(right[low])):
                raise AssertionError("result bins overlap or leave a gap")


def validate_table_parity(sample, tex):
    expected_lines = []
    for label in [row["quantity_label"] for row in sample if row["tune"] == "MONASH"]:
        selected = {row["tune"]: row for row in sample if row["quantity_label"] == label}
        tex_label = label.replace("_", r"\_")
        expected_lines.append("{} & {} \\\\".format(
            tex_label, " & ".join(selected[tune]["value"]
                                    for tune in ("MONASH", "JUNCTIONS", "CLOSEPACKING"))))
    actual = [line for line in tex.splitlines()
              if line.endswith(r"\\") and not line.startswith("Quantity &")]
    if actual != expected_lines:
        raise AssertionError("sample-count table transcription differs from CSV")


class ResultContract(unittest.TestCase):
    def test_manifest_schema_roles_safe_paths_bytes_and_pdf_integrity(self):
        manifest = load_json("results/manifest.json")
        self.assertEqual(manifest["schema"], "hadronization_result_package_v1")
        self.assertEqual(manifest["status"], "migration_baseline")
        self.assertEqual(manifest["systematics"], "disabled_not_included")
        self.assertEqual(manifest["discarded_attempts"], "recorded_no_correction")
        self.assertEqual(manifest["numeric_schema"], "migration_accepted_double_text_v1")
        self.assertEqual(manifest["statistics_version"], "ten_block_sample_sem_v1")
        self.assertIsNone(manifest["import_commit"]["manifest_self_hash"])
        artifacts = manifest["artifacts"]
        self.assertEqual(len(artifacts), 44)
        listed = {entry["path"] for entry in artifacts}
        actual = {path.relative_to(ROOT).as_posix()
                  for directory in ("measurement", "plots", "tables")
                  for path in (ROOT / "results" / directory).rglob("*") if path.is_file()}
        self.assertEqual(actual, listed)
        for entry in artifacts:
            pure = PurePosixPath(entry["path"])
            self.assertFalse(pure.is_absolute())
            self.assertNotIn("..", pure.parts)
            self.assertIn(pure.parts[:2], {("results", "measurement"),
                                           ("results", "plots"), ("results", "tables")})
            self.assertTrue(entry["producer"] and entry["consumer"])
            path = ROOT / entry["path"]
            self.assertEqual(path.stat().st_size, entry["bytes"])
            self.assertEqual(sha256(path), entry["sha256"])
            self.assertEqual(path.read_bytes(), git_blob(entry["path"]))
        pdfinfo = shutil.which("pdfinfo")
        if not pdfinfo:
            self.skipTest("pdfinfo unavailable")
        plots = sorted((ROOT / "results/plots").glob("*.pdf"))
        self.assertEqual(len(plots), 38)
        for path in plots:
            result = subprocess.run([pdfinfo, str(path)], text=True,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.assertEqual(result.returncode, 0, (path, result.stderr))
            self.assertRegex(result.stdout, r"(?m)^Pages:\s+1$")

    def test_balancing_arithmetic_ratios_sems_and_closures(self):
        validate_balancing(csv_rows("results/measurement/balancing.csv"))

    def test_all_measurement_identities_bins_counts_and_table_parity(self):
        study = load_json("config/study.json")
        def uniform(specification):
            low = float(specification["low"])
            high = float(specification["high"])
            bins = int(specification["bins"])
            return [low + (high - low) * index / bins for index in range(bins + 1)]
        correlation = csv_rows("results/measurement/correlations.csv")
        validate_axis(correlation, ("tune", "flavour", "trigger", "associate",
                                     "context", "activity_id"),
                      "bin_index", "dphi_low", "dphi_high", 12,
                      uniform(study["observables"]["correlations"]["delta_phi"]))
        multiplicity = csv_rows("results/measurement/multiplicity.csv")
        validate_axis(multiplicity, ("tune",), "bin_index", "nch_low", "nch_high", 3,
                      uniform(study["observables"]["multiplicity"]["binning"]))
        kinematics = csv_rows("results/measurement/kinematics.csv")
        axes = study["observables"]["inclusive_kinematics"]["axes"]
        kinematic_edges = {
            name: ([float(value) for value in axis["edges"]]
                   if axis["kind"] == "variable" else uniform(axis))
            for name, axis in axes.items()
        }
        validate_axis(kinematics, ("tune", "species", "pdg", "observable"),
                      "bin_index", "bin_low", "bin_high", 90,
                      lambda identity: kinematic_edges[identity[-1]])
        for table in (multiplicity, kinematics):
            for row in table:
                if row["count_or_content"] and not row["count_or_content"].isdigit():
                    self.fail("exact measurement count is not an integer token")
        sample = csv_rows("results/measurement/sample_counts.csv")
        self.assertEqual(len(sample), 36)
        self.assertEqual(len({(row["tune"], row["quantity"]) for row in sample}), 36)
        self.assertTrue(all(row["value"].isdigit() for row in sample))
        validate_table_parity(sample, (ROOT / "results/tables/sample_counts.tex").read_text(
            encoding="utf-8"))

    def test_semantic_gates_reject_independent_measurement_mutations(self):
        balancing = csv_rows("results/measurement/balancing.csv")
        wrong_ratio = copy.deepcopy(balancing)
        row = next(row for row in wrong_ratio
                   if row["quantity"] == "balancing_ratio_to_reference" and
                   row["estimator"] == "block_01")
        row["value"] = str(float(row["value"]) * 1.01)
        with self.assertRaisesRegex(AssertionError, "within-block ratio"):
            validate_balancing(wrong_ratio)
        blank = copy.deepcopy(balancing)
        row = next(row for row in blank if row["quantity"] == "balancing_yield" and
                   row["estimator"] == "block_01" and row["n_trigger"])
        row["n_trigger"] = ""
        with self.assertRaisesRegex(AssertionError, "unexplained blank"):
            validate_balancing(blank)
        rounded = copy.deepcopy(balancing)
        row = next(row for row in rounded if row["status"] == "available_count_backed")
        row["status"] = "available_derived_no_component_counts_trigger_count_rounded_in_source"
        with self.assertRaisesRegex(AssertionError, "rounded-source"):
            validate_balancing(rounded)
        wrong_rounded_identity = copy.deepcopy(balancing)
        row = next(row for row in wrong_rounded_identity
                   if row["status"] ==
                   "available_derived_no_component_counts_trigger_count_rounded_in_source")
        row["activity_id"] = "wrong_activity"
        with self.assertRaisesRegex(AssertionError, "rounded-source identity"):
            validate_balancing(wrong_rounded_identity)

        correlations = csv_rows("results/measurement/correlations.csv")
        duplicated = copy.deepcopy(correlations)
        duplicated[1]["bin_index"] = duplicated[0]["bin_index"]
        with self.assertRaisesRegex(AssertionError, "non-contiguous/duplicate"):
            validate_axis(duplicated, ("tune", "flavour", "trigger", "associate",
                                       "context", "activity_id"),
                          "bin_index", "dphi_low", "dphi_high", 12,
                          [float(row["dphi_low"]) for row in correlations[:1]] +
                          [float(row["dphi_high"]) for row in correlations[:100]])
        study = load_json("config/study.json")
        corr_axis = study["observables"]["correlations"]["delta_phi"]
        expected_edges = [
            float(corr_axis["low"]) +
            (float(corr_axis["high"]) - float(corr_axis["low"])) * index /
            int(corr_axis["bins"])
            for index in range(int(corr_axis["bins"]) + 1)]
        missing_bin = copy.deepcopy(correlations)
        first_identity = tuple(missing_bin[0][field] for field in
                               ("tune", "flavour", "trigger", "associate",
                                "context", "activity_id"))
        del missing_bin[next(index for index, row in enumerate(missing_bin)
                             if tuple(row[field] for field in
                                      ("tune", "flavour", "trigger", "associate",
                                       "context", "activity_id")) == first_identity)]
        with self.assertRaisesRegex(AssertionError, "wrong exact bin count"):
            validate_axis(missing_bin, ("tune", "flavour", "trigger", "associate",
                                        "context", "activity_id"),
                          "bin_index", "dphi_low", "dphi_high", 12,
                          expected_edges)
        wrong_edge = copy.deepcopy(correlations)
        wrong_edge[0]["dphi_high"] = str(float(wrong_edge[0]["dphi_high"]) + 0.001)
        with self.assertRaisesRegex(AssertionError, "edge sequence"):
            validate_axis(wrong_edge, ("tune", "flavour", "trigger", "associate",
                                       "context", "activity_id"),
                          "bin_index", "dphi_low", "dphi_high", 12,
                          expected_edges)
        sample = csv_rows("results/measurement/sample_counts.csv")
        tex = (ROOT / "results/tables/sample_counts.tex").read_text(encoding="utf-8")
        with self.assertRaisesRegex(AssertionError, "transcription"):
            validate_table_parity(sample, tex.replace("226634887", "226634888", 1))


if __name__ == "__main__":
    unittest.main()
