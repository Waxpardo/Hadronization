import math
from pathlib import Path
import re
import statistics
import unittest

from helpers import ROOT, csv_rows, git_blob, load_json, sha256


class ResultContract(unittest.TestCase):
    def test_manifest_is_exact_complete_set_and_bytes_match(self):
        manifest = load_json("results/manifest.json")
        artifacts = manifest["artifacts"]
        self.assertEqual(len(artifacts), 44)
        listed = {entry["path"] for entry in artifacts}
        actual = {
            path.relative_to(ROOT).as_posix()
            for directory in ("measurement", "plots", "tables")
            for path in (ROOT / "results" / directory).rglob("*")
            if path.is_file()
        }
        self.assertEqual(actual, listed)
        for entry in artifacts:
            path = ROOT / entry["path"]
            self.assertEqual(path.stat().st_size, entry["bytes"], entry["path"])
            self.assertEqual(sha256(path), entry["sha256"], entry["path"])
            self.assertEqual(path.read_bytes(), git_blob(entry["path"]), entry["path"])

    def test_measurement_topology_and_exact_count_tokens(self):
        expected = {
            "balancing.csv": 5016,
            "correlations.csv": 1200,
            "multiplicity.csv": 12288,
            "kinematics.csv": 9300,
            "sample_counts.csv": 36,
        }
        for name, count in expected.items():
            self.assertEqual(len(csv_rows("results/measurement/" + name)), count)
        for row in csv_rows("results/measurement/balancing.csv"):
            for field in ("n_os", "n_ss", "n_trigger"):
                if row[field]:
                    self.assertRegex(row[field], r"^[0-9]+$")
        for name in ("kinematics.csv", "multiplicity.csv"):
            for row in csv_rows("results/measurement/" + name):
                if row["count_or_content"]:
                    self.assertRegex(row["count_or_content"], r"^[0-9]+$")
        for row in csv_rows("results/measurement/sample_counts.csv"):
            self.assertRegex(row["value"], r"^[0-9]+$")
        rounded = [row for row in csv_rows("results/measurement/balancing.csv")
                   if not row["n_trigger"] and "rounded_in_source" in row["status"]]
        self.assertEqual(len(rounded), 90)
        self.assertEqual({row["trigger"] for row in rounded}, {"dplus"})

    def test_count_backed_balancing_arithmetic(self):
        rows = csv_rows("results/measurement/balancing.csv")
        checked = 0
        for row in rows:
            if (row["quantity"] == "balancing_yield" and row["n_os"]
                    and row["n_ss"] and row["n_trigger"]):
                expected = ((int(row["n_os"]) - int(row["n_ss"])) /
                            int(row["n_trigger"]))
                self.assertAlmostEqual(float(row["value"]), expected, places=15)
                checked += 1
        self.assertEqual(checked, 576)

    def test_ten_block_sem_and_within_block_ratio_contract(self):
        rows = csv_rows("results/measurement/balancing.csv")
        base_fields = ("tune", "flavour", "trigger", "os_associate",
                       "ss_associate", "activity_id")
        grouped = {}
        for row in rows:
            key = tuple(row[field] for field in base_fields) + (row["quantity"],)
            grouped.setdefault(key, {})[row["estimator"]] = float(row["value"])
        sem_checked = 0
        for row in rows:
            if row["quantity"] not in ("balancing_yield_sem", "balancing_ratio_sem"):
                continue
            source_quantity = ("balancing_yield" if row["quantity"] == "balancing_yield_sem"
                               else "balancing_ratio_to_reference")
            source = grouped[tuple(row[field] for field in base_fields) +
                             (source_quantity,)]
            values = [source["block_{:02d}".format(index)] for index in range(1, 11)]
            expected = statistics.stdev(values) / math.sqrt(10.0)
            self.assertAlmostEqual(float(row["value"]), expected, places=15)
            sem_checked += 1
        self.assertEqual(sem_checked, 390)


if __name__ == "__main__":
    unittest.main()
