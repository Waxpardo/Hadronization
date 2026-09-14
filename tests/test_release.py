"""The portable assembler refuses a stale renderer before copying a large package."""

import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from pipeline import release


class PortableAssemblyBoundary(unittest.TestCase):
    def _fixture(self, base, config):
        numerical, figures = base / "numerical", base / "figures"
        numerical.mkdir(); figures.mkdir()
        (numerical / "report.json").write_text(json.dumps({
            "root": {"value_sha256": "a" * 64}}))
        numeric_manifest = numerical / "package-manifest.json"
        numeric_manifest.write_text(json.dumps({
            "schema": "hadronization_public_v4_portable_package_v1",
            "root_sha256": "b" * 64,
            "files": {"report.json": release.fact(numerical / "report.json")}}))
        figure_manifest = figures / "manifest.json"
        figure_manifest.write_text(json.dumps({
            "schema": "hadronization_cold_plot_render_v1",
            "numerics_root": {"sha256": "b" * 64,
                              "value_sha256": "a" * 64},
            "plot_config_sha256": release.sha(config),
            "source_sha256": {"pipeline/plot/run.py":
                              release.sha(release.ROOT / "pipeline/plot/run.py")},
            "presentation_state": "TEST_ONLY_SYNTHETIC", "files": []}))
        return numerical, figures, numeric_manifest, figure_manifest

    def test_selected_nondefault_config_is_packaged_and_bound(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            config = release.ROOT / "config/plot-all-tune.json"
            numerical, figures, numeric_pin, figure_pin = self._fixture(base, config)
            output = base / "collaboration"
            digest = release.build(numerical, release.sha(numeric_pin), figures,
                                   release.sha(figure_pin), output, config)
            manifest = json.loads((output / "manifest.json").read_text())
            locator = "config/plot-all-tune.json"
            self.assertEqual(manifest["plot_config"], {
                "path": locator, "sha256": release.sha(config)})
            self.assertEqual(release.sha(output / locator), release.sha(config))
            self.assertEqual(digest, release.sha(output / "manifest.json"))
            self.assertNotIn("config/plot.json", manifest["files"])

    def test_publisher_failure_preserves_complete_nested_package(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            config = release.ROOT / "config/plot-all-tune.json"
            numerical, figures, numeric_pin, figure_pin = self._fixture(base, config)
            output = base / "collaboration"
            def interrupted(stage, destination):
                destination.mkdir(mode=0o000)
                raise KeyboardInterrupt("TEST_ONLY after reservation")
            try:
                with mock.patch.object(release, "publish_directory", side_effect=interrupted):
                    with self.assertRaises(KeyboardInterrupt):
                        release.build(numerical, release.sha(numeric_pin), figures,
                                      release.sha(figure_pin), output, config)
                stages = list(base.glob(".collaboration.stage-*"))
                self.assertEqual(len(stages), 1)
                self.assertTrue((stages[0] / "manifest.json").is_file())
                self.assertTrue((stages[0] / "config/plot-all-tune.json").is_file())
                self.assertEqual(output.stat().st_mode & 0o777, 0)
                with self.assertRaises((OSError, ValueError)):
                    release.verify(output, "a" * 64, base / "work")
            finally:
                if output.exists(): output.chmod(0o700)

    def test_wrong_or_missing_selected_config_and_wrong_root_refuse(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            config = release.ROOT / "config/plot-all-tune.json"
            numerical, figures, numeric_pin, figure_pin = self._fixture(base, config)
            output = base / "collaboration"
            with self.assertRaisesRegex(ValueError, "selected plot configuration differs"):
                release.build(numerical, release.sha(numeric_pin), figures,
                              release.sha(figure_pin), output,
                              release.ROOT / "config/plot.json")
            with self.assertRaisesRegex(ValueError, "not a regular file"):
                release.build(numerical, release.sha(numeric_pin), figures,
                              release.sha(figure_pin), output, base / "missing.json")
            self.assertFalse(output.exists())
            figure = json.loads(figure_pin.read_text())
            figure["numerics_root"]["sha256"] = "c" * 64
            figure_pin.write_text(json.dumps(figure))
            with self.assertRaisesRegex(ValueError, "numerical ROOT"):
                release.build(numerical, release.sha(numeric_pin), figures,
                              release.sha(figure_pin), output, config)
            self.assertFalse(output.exists())

    def test_relocated_package_refuses_missing_or_resealed_wrong_config(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            config = release.ROOT / "config/plot-all-tune.json"
            numerical, figures, numeric_pin, figure_pin = self._fixture(base, config)
            output = base / "collaboration"
            release.build(numerical, release.sha(numeric_pin), figures,
                          release.sha(figure_pin), output, config)
            config_copy = output / "config/plot-all-tune.json"
            config_copy.unlink()
            with self.assertRaisesRegex(ValueError, "exact fileset differs"):
                release.verify(output, release.sha(output / "manifest.json"),
                               base / "work")
            config_copy.write_bytes((release.ROOT / "config/plot.json").read_bytes())
            manifest = json.loads((output / "manifest.json").read_text())
            manifest["files"]["config/plot-all-tune.json"] = release.fact(config_copy)
            manifest["plot_config"]["sha256"] = release.sha(config_copy)
            (output / "manifest.json").write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "selected plot configuration differs"):
                release.verify(output, release.sha(output / "manifest.json"),
                               base / "work")

    def test_stale_figure_source_refuses_before_package_publication(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            numerical, figures = base / "numerical", base / "figures"
            numerical.mkdir(); figures.mkdir()
            (numerical / "report.json").write_text(json.dumps({
                "root": {"value_sha256": "a" * 64}}))
            numeric_manifest = numerical / "package-manifest.json"
            numeric_manifest.write_text(json.dumps({
                "schema": "hadronization_public_v4_portable_package_v1",
                "root_sha256": "b" * 64, "files": {}}))
            figure_manifest = figures / "manifest.json"
            figure_manifest.write_text(json.dumps({
                "schema": "hadronization_cold_plot_render_v1",
                "numerics_root": {"sha256": "b" * 64,
                                  "value_sha256": "a" * 64},
                "plot_config_sha256": release.sha(release.ROOT / "config/plot.json"),
                "source_sha256": {"pipeline/plot/run.py": "c" * 64},
                "files": []}))
            destination = base / "must-not-exist"
            with self.assertRaisesRegex(ValueError, "figure source differs"):
                release.build(numerical, release.sha(numeric_manifest),
                              figures, release.sha(figure_manifest), destination)
            self.assertFalse(destination.exists())


if __name__ == "__main__":
    unittest.main()
