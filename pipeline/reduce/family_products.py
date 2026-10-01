"""Consolidated fine-species and derived-family ROOT product writer."""
from array import array
import hashlib
import json
import os
from pathlib import Path
import tempfile
import importlib.util
import sys

_family_spec = importlib.util.spec_from_file_location(
    "family_products_model", Path(__file__).with_name("family.py"))
_family = importlib.util.module_from_spec(_family_spec)
sys.modules[_family_spec.name] = _family
_family_spec.loader.exec_module(_family)
group_additive_rows = _family.group_additive_rows


SCHEMA = "hadronization_family_products_manifest_v1"
FIELDS = ("block", "trigger_pdg", "associate_pdg", "sign", "count",
          "sumw2", "trigger_count")


def _sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)


def _write_root(path, rows, metadata):
    import ROOT
    ROOT.gROOT.SetBatch(True)
    path = Path(path)
    if path.exists() or path.is_symlink():
        raise FileExistsError(path)
    descriptor, temporary = tempfile.mkstemp(prefix="." + path.name + ".",
                                              suffix=".tmp", dir=path.parent)
    os.close(descriptor)
    try:
        output = ROOT.TFile.Open(temporary, "RECREATE")
        if not output or output.IsZombie():
            raise ValueError("family ROOT output cannot be created")
        tree = ROOT.TTree("pair_primitives", "additive pair primitives")
        tune = ROOT.std.string()
        scalar = {name: array("i", [0]) for name in FIELDS[:4]}
        real = {name: array("d", [0.0]) for name in FIELDS[4:]}
        tree.Branch("tune", tune)
        for name, value in scalar.items():
            tree.Branch(name, value, name + "/I")
        for name, value in real.items():
            tree.Branch(name, value, name + "/D")
        for row in rows:
            tune.assign(row["tune"])
            for name, value in scalar.items(): value[0] = row[name]
            for name, value in real.items(): value[0] = row[name]
            tree.Fill()
        ROOT.TObjString(_canonical(metadata)).Write("family_product_metadata")
        tree.Write()
        output.Close()
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary): os.unlink(temporary)


def write_products(output, fine_rows, family_map, *, source_sha256,
                   analysis_sha256, content_sha256):
    """Write one file per signed fine species and one derived family file."""
    if any(len(value) != 64 for value in
           (source_sha256, analysis_sha256, content_sha256)):
        raise ValueError("family product binding digest differs")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    fine = output / "fine"
    fine.mkdir()
    by_species = {}
    for row in fine_rows:
        by_species.setdefault(row["associate_pdg"], []).append(row)
    if set(by_species) != set(family_map.members):
        raise ValueError("fine product species coverage differs")
    common = dict(schema=SCHEMA, map_sha256=family_map.sha256,
                  source_sha256=source_sha256, analysis_sha256=analysis_sha256,
                  content_sha256=content_sha256, block_count=10,
                  denominator_scope="common trigger key carried once per row")
    files = {}
    for pdg in sorted(by_species):
        relative = "fine/pdg-{}.root".format(str(pdg).replace("-", "m"))
        _write_root(output / relative, by_species[pdg],
                    dict(common, product="FINE_SIGNED_SPECIES", pdg=pdg))
        files[relative] = {"sha256": _sha(output / relative),
                           "bytes": (output / relative).stat().st_size,
                           "rows": len(by_species[pdg])}
    grouped = group_additive_rows(fine_rows, family_map)
    relative = "families.root"
    _write_root(output / relative, grouped,
                dict(common, product="DERIVED_SAVED_STATE_FAMILIES",
                     destinations=list(family_map.destinations)))
    files[relative] = {"sha256": _sha(output / relative),
                       "bytes": (output / relative).stat().st_size,
                       "rows": len(grouped)}
    manifest = dict(common, fine_species_count=len(by_species),
                    family_destination_count=len(family_map.destinations),
                    files=files)
    manifest["manifest_content_sha256"] = hashlib.sha256(
        _canonical(manifest).encode("ascii")).hexdigest()
    path = output / "manifest.json"
    path.write_text(_canonical(manifest) + "\n", encoding="ascii")
    return manifest


def read_rows(path):
    """Cold round-trip reader used by the verifier and bounded proof."""
    import ROOT
    file = ROOT.TFile.Open(str(path), "READ")
    if not file or file.IsZombie():
        raise ValueError("family ROOT product cannot be opened")
    try:
        tree = file.Get("pair_primitives")
        metadata = file.Get("family_product_metadata")
        if not tree or not metadata:
            raise ValueError("family ROOT product schema differs")
        rows = []
        for row in tree:
            rows.append(dict(tune=str(row.tune), **{
                name: int(getattr(row, name)) for name in FIELDS[:4]}, **{
                name: float(getattr(row, name)) for name in FIELDS[4:]}))
        return json.loads(str(metadata.GetString())), rows
    finally:
        file.Close()
