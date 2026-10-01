"""Independent bounded checks for the v2.3 selected=0 family chain."""
from array import array
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import sys

ROOT_DIR = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT_DIR))
from pipeline.reduce import archive_v4, family_products


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    base = Path(os.environ["FAMILY_CHAIN_BASE"]).resolve()
    if not base.is_dir() or any(path.is_symlink() for path in (base, *base.parents)):
        raise ValueError("FAMILY_CHAIN_BASE must be an existing nonsymlink directory")
    import ROOT
    ROOT.gROOT.SetBatch(True)
    numerical = base / os.environ.get("FAMILY_NUMERICAL_NAME", "numerical")
    rendered_dir = base / os.environ.get("FAMILY_RENDERED_NAME", "rendered")
    selected_zero = {423: 0, -423: 0, 4334: 0, -4334: 0}
    pair_sums = {pdg: 0.0 for pdg in selected_zero}
    proof_candidates = 0
    activity_digests, trigger_digests, kinematics_digests = [], [], []
    for ordinal in range(3):
        workspace = base / "queries" / f"shard-{ordinal:04d}"
        metadata = json.loads((workspace / "metadata.json").read_text())
        proof = metadata["pair_population_proof"]
        assert proof["state"] == "PASS" and proof["candidate_pairs"] == proof["stored_pairs"]
        proof_candidates += proof["candidate_pairs"]
        activity_digests.append(metadata["query_content_digests"]["sparse:activity"])
        trigger_digests.append(metadata["query_content_digests"]["sparse:triggers"])
        kinematics_digests.append(metadata["query_content_digests"]["sparse:kinematics"])
        file = ROOT.TFile.Open(str(workspace / "query.root"), "READ")
        assert file and not file.IsZombie()
        for row in file.Get("heavy"):
            pdg = int(row.pdg)
            if pdg in selected_zero:
                selected = ord(row.selected) if isinstance(row.selected, str) else int(row.selected)
                eligible = ord(row.pair_eligible) if isinstance(row.pair_eligible, str) else int(row.pair_eligible)
                assert (selected, eligible) == (0, 0)
                selected_zero[pdg] += 1
        sparse = file.Get("sparse_pairs")
        names = {sparse.GetAxis(i).GetName(): i for i in range(sparse.GetNdimensions())}
        coordinates = array("i", [0] * sparse.GetNdimensions())
        for index in range(sparse.GetNbins()):
            value = float(sparse.GetBinContent(index, coordinates))
            label = sparse.GetAxis(names["associate_pdg"]).GetBinLabel(
                coordinates[names["associate_pdg"]])
            if label and int(label) in pair_sums:
                pair_sums[int(label)] += value
        file.Close()
    assert all(value > 0 for value in selected_zero.values())
    assert all(value != 0 and math.isfinite(value) for value in pair_sums.values())
    report = json.loads((numerical / "report.json").read_text())
    manifest = json.loads((numerical / "package-manifest.json").read_text())
    family = family_products.verify_products(numerical / "family-products",
        report["family_products"]["manifest_sha256"])
    relocated = base / "relocated-family-products"
    shutil.copytree(numerical / "family-products", relocated)
    relocated_family = family_products.verify_products(
        relocated, report["family_products"]["manifest_sha256"])
    assert relocated_family == family
    value = archive_v4.read(numerical / "numerics.root",
        report["root"]["root_sha256"], report["root"]["value_sha256"])
    status_pairs = {(row["center_status"], row["uncertainty_status"])
                    for row in value["points"]}
    available_errors = [float.fromhex(row["standard_error"]) for row in value["points"]
                        if row["uncertainty_status"] in
                        ("AVAILABLE", "AVAILABLE_ZERO_DISPERSION")]
    assert ("AVAILABLE", "AVAILABLE") in status_pairs
    assert any(status != "AVAILABLE" for _, status in status_pairs)
    assert any(error == 0.0 for error in available_errors)
    assert any(error > 0.0 for error in available_errors)
    assert value["covariance"]
    boundary_rows = value["class_boundary_deletions"]
    boundary_domains = {}
    for row in boundary_rows:
        boundary_domains.setdefault((row["tune_id"], row["class_id"]), set()).add(
            (row["status"], row["low"], row["high"]))
    changed_boundaries = sum(len(rows) > 1 for rows in boundary_domains.values())
    assert changed_boundaries
    rendered = json.loads((rendered_dir / "manifest.json").read_text())
    assert rendered["state"] == "COMPLETE"
    result = {
        "schema": "nonzero_chain_v23_selected_zero_oracle_v1",
        "analysis_sha256": report["analysis_sha256"],
        "proof_candidate_pairs": proof_candidates,
        "selected_zero_rows": selected_zero,
        "selected_zero_sparse_pair_sums": pair_sums,
        "fine_species_count": family["fine_species_count"],
        "family_destination_count": family["family_destination_count"],
        "family_manifest_sha256": report["family_products"]["manifest_sha256"],
        "relocated_family_verification": "PASS",
        "covariance_groups": len(value["covariance"]),
        "status_pairs": sorted(map(list, status_pairs)),
        "available_zero_uncertainties": sum(error == 0.0 for error in available_errors),
        "available_nonzero_uncertainties": sum(error > 0.0 for error in available_errors),
        "changed_boundary_evidence": changed_boundaries,
        "renderer_manifest_sha256": sha(rendered_dir / "manifest.json"),
        "package_manifest_sha256": sha(numerical / "package-manifest.json"),
        "package_family_files": sum(name.startswith("family-products/") for name in manifest["files"]),
        "unchanged_family_digests": {
            "activity": activity_digests, "triggers": trigger_digests,
            "kinematics": kinematics_digests},
    }
    output = Path(os.environ.get("FAMILY_CHAIN_REPORT", base / "oracle.json"))
    with output.open("x") as stream:
        json.dump(result, stream, sort_keys=True, indent=2); stream.write("\n")
    print(json.dumps(result, sort_keys=True))

if __name__ == "__main__":
    main()
