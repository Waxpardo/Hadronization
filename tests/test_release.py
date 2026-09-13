"""The portable assembler refuses a stale renderer before copying a large package."""

import json
from pathlib import Path
import tempfile
import unittest

from pipeline import release


class PortableAssemblyBoundary(unittest.TestCase):
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
