"""Portable fine-species and derived saved-state-family ROOT products."""
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

SCHEMA = "hadronization_family_products_manifest_v2"
PAIR_FIELDS = ("block", "activity_bin", "trigger_pdg", "associate_pdg",
               "sign", "dphi_bin", "count", "sumw2")
TRIGGER_FIELDS = ("block", "activity_bin", "trigger_pdg", "count", "sumw2")
ACTIVITY_FIELDS = ("block", "activity_bin", "count", "sumw2")


def _sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)


def _publish_temp(temporary, path):
    path = Path(path)
    if path.exists() or path.is_symlink():
        raise FileExistsError(path)
    os.link(temporary, path)
    os.unlink(temporary)
    descriptor = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _write_root(path, trees, metadata):
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
        for tree_name, string_fields, integer_fields, real_fields, rows in trees:
            tree = ROOT.TTree(tree_name, "additive primitives")
            strings = {name: ROOT.std.string() for name in string_fields}
            integers = {name: array("i", [0]) for name in integer_fields}
            reals = {name: array("d", [0.0]) for name in real_fields}
            for name, value in strings.items():
                tree.Branch(name, value)
            for name, value in integers.items():
                tree.Branch(name, value, name + "/I")
            for name, value in reals.items():
                tree.Branch(name, value, name + "/D")
            for row in rows:
                for name, value in strings.items(): value.assign(row[name])
                for name, value in integers.items(): value[0] = row[name]
                for name, value in reals.items(): value[0] = row[name]
                tree.Fill()
            tree.Write()
        ROOT.TObjString(_canonical(metadata)).Write("family_product_metadata")
        output.Write()
        output.Close()
        with open(temporary, "rb") as stream:
            os.fsync(stream.fileno())
        _publish_temp(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _pair_rows(primitives):
    return [dict(profile_id=key[0], tune_id=key[1], block=key[2],
                 activity_bin=key[3], trigger_pdg=key[4], associate_pdg=key[5],
                 sign=key[6], dphi_bin=key[7], count=cell.value,
                 sumw2=cell.sumw2)
            for key, cell in sorted(primitives.pairs.items())]


def _group_rows(fine_rows, family_map):
    grouped = {}
    for row in fine_rows:
        destination = family_map.destination_by_member.get(row["associate_pdg"])
        if destination is None:
            raise ValueError("fine primitive is outside the public family map")
        key = (row["profile_id"], row["tune_id"], row["block"],
               row["activity_bin"], row["trigger_pdg"], destination,
               row["sign"], row["dphi_bin"])
        cell = grouped.setdefault(key, [0.0, 0.0])
        cell[0] += row["count"]
        cell[1] += row["sumw2"]
    return [dict(profile_id=key[0], tune_id=key[1], block=key[2],
                 activity_bin=key[3], trigger_pdg=key[4], associate_pdg=key[5],
                 sign=key[6], dphi_bin=key[7], count=value[0], sumw2=value[1])
            for key, value in sorted(grouped.items())]


def _shared_rows(primitives):
    activity = [dict(tune_id=k[0], block=k[1], activity_bin=k[2],
                     count=v.value, sumw2=v.sumw2)
                for k, v in sorted(primitives.activity.items())]
    triggers = [dict(profile_id=k[0], tune_id=k[1], block=k[2],
                     activity_bin=k[3], trigger_pdg=k[4], count=v.value,
                     sumw2=v.sumw2)
                for k, v in sorted(primitives.triggers.items())]
    return activity, triggers


def write_products(output, primitives, family_map, *, source_sha256,
                   analysis_sha256, content_sha256):
    """Write portable fine, family, and shared-denominator products once."""
    if any(len(value) != 64 for value in
           (source_sha256, analysis_sha256, content_sha256)):
        raise ValueError("family product binding digest differs")
    if (len(primitives.selected_pairs) != len(set(primitives.selected_pairs)) or
            {associate for _, associate in primitives.selected_pairs} !=
            set(family_map.members) or
            {trigger for trigger, _ in primitives.selected_pairs} !=
            set(primitives.selected_triggers)):
        raise ValueError("fine product declared pair domain differs")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    fine_dir = output / "fine"
    fine_dir.mkdir()
    fine_rows = _pair_rows(primitives)
    grouped_rows = _group_rows(fine_rows, family_map)
    activity_rows, trigger_rows = _shared_rows(primitives)
    groups = [dict(destination_pdg=destination,
                   family=family_map.family_by_destination[destination],
                   members=list(family_map.members_by_destination[destination]))
              for destination in family_map.destinations]
    common = dict(schema=SCHEMA, runtime_map_sha256=family_map.sha256,
        accepted_full_map_sha256=family_map.accepted_full_map_sha256,
        semantic_groups_sha256=family_map.semantic_groups_sha256,
        source_sha256=source_sha256, analysis_sha256=analysis_sha256,
        content_sha256=content_sha256, block_count=10,
        profiles=list(primitives.profile_ids), activity_field=primitives.activity_field,
        signed_fine_species=list(family_map.members), groups=groups,
        fine_state_identities=[family_map.fine_state_identities[pdg]
            for pdg in sorted(family_map.fine_state_identities)],
        denominator_scope="shared trigger/activity primitives stored once, including zero-partner trigger domains")
    files = {}
    by_species = {pdg: [] for pdg in family_map.members}
    for row in fine_rows:
        by_species[row["associate_pdg"]].append(row)
    pair_tree = lambda rows: [("pair_primitives", ("profile_id", "tune_id"),
        PAIR_FIELDS[:6], PAIR_FIELDS[6:], rows)]
    for pdg in sorted(by_species):
        relative = "fine/pdg-{}.root".format(str(pdg).replace("-", "m"))
        _write_root(output / relative, pair_tree(by_species[pdg]),
                    dict(common, product="FINE_SIGNED_SPECIES", pdg=pdg))
        files[relative] = {"sha256": _sha(output / relative),
                           "bytes": (output / relative).stat().st_size,
                           "rows": len(by_species[pdg])}
    _write_root(output / "families.root", pair_tree(grouped_rows),
                dict(common, product="DERIVED_SAVED_STATE_FAMILIES",
                     destinations=list(family_map.destinations)))
    files["families.root"] = {"sha256": _sha(output / "families.root"),
        "bytes": (output / "families.root").stat().st_size,
        "rows": len(grouped_rows)}
    shared_trees = [
        ("activity_primitives", ("tune_id",), ACTIVITY_FIELDS[:2],
         ACTIVITY_FIELDS[2:], activity_rows),
        ("trigger_primitives", ("profile_id", "tune_id"), TRIGGER_FIELDS[:3],
         TRIGGER_FIELDS[3:], trigger_rows)]
    _write_root(output / "shared.root", shared_trees,
                dict(common, product="SHARED_ACTIVITY_AND_TRIGGER_PRIMITIVES"))
    files["shared.root"] = {"sha256": _sha(output / "shared.root"),
        "bytes": (output / "shared.root").stat().st_size,
        "activity_rows": len(activity_rows), "trigger_rows": len(trigger_rows)}
    manifest = dict(common, fine_species_count=len(by_species),
                    family_destination_count=len(family_map.destinations),
                    files=files)
    manifest["manifest_content_sha256"] = hashlib.sha256(
        _canonical(manifest).encode("ascii")).hexdigest()
    descriptor, temporary = tempfile.mkstemp(prefix=".manifest.", suffix=".tmp",
                                              dir=output)
    try:
        with os.fdopen(descriptor, "w", encoding="ascii", newline="\n") as stream:
            stream.write(_canonical(manifest) + "\n")
            stream.flush(); os.fsync(stream.fileno())
        _publish_temp(temporary, output / "manifest.json")
    finally:
        if os.path.exists(temporary): os.unlink(temporary)
    verify_products(output, _sha(output / "manifest.json"))
    return manifest


def _read_root(path):
    import ROOT
    file = ROOT.TFile.Open(str(path), "READ")
    if not file or file.IsZombie():
        raise ValueError("family ROOT product cannot be opened")
    try:
        metadata = file.Get("family_product_metadata")
        if not metadata:
            raise ValueError("family ROOT product metadata is absent")
        result = {}
        for tree_name, string_fields, integer_fields, real_fields in (
            ("pair_primitives", ("profile_id", "tune_id"), PAIR_FIELDS[:6], PAIR_FIELDS[6:]),
            ("activity_primitives", ("tune_id",), ACTIVITY_FIELDS[:2], ACTIVITY_FIELDS[2:]),
            ("trigger_primitives", ("profile_id", "tune_id"), TRIGGER_FIELDS[:3], TRIGGER_FIELDS[3:])):
            tree = file.Get(tree_name)
            if not tree:
                continue
            rows = []
            for entry in tree:
                rows.append({**{name: str(getattr(entry, name)) for name in string_fields},
                    **{name: int(getattr(entry, name)) for name in integer_fields},
                    **{name: float(getattr(entry, name)) for name in real_fields}})
            result[tree_name] = rows
        return json.loads(str(metadata.GetString())), result
    finally:
        file.Close()


def read_rows(path):
    metadata, trees = _read_root(path)
    return metadata, trees.get("pair_primitives", [])


def verify_products(output, expected_manifest_sha256):
    """Cold, relocation-safe exact-fileset and additive-conservation verifier."""
    output = Path(output)
    manifest_path = output / "manifest.json"
    if _sha(manifest_path) != expected_manifest_sha256:
        raise ValueError("family product manifest pin differs")
    manifest = json.loads(manifest_path.read_text(encoding="ascii"))
    digest = manifest.pop("manifest_content_sha256", None)
    if hashlib.sha256(_canonical(manifest).encode("ascii")).hexdigest() != digest:
        raise ValueError("family product manifest content binding differs")
    manifest["manifest_content_sha256"] = digest
    if manifest.get("schema") != SCHEMA:
        raise ValueError("family product manifest schema differs")
    expected_files = set(manifest["files"]) | {"manifest.json"}
    actual_files = {path.relative_to(output).as_posix() for path in output.rglob("*")
                    if path.is_file()}
    if actual_files != expected_files:
        raise ValueError("family product exact fileset differs")
    fine_rows = []
    fine_pdgs = set()
    common_keys = ("schema", "runtime_map_sha256", "accepted_full_map_sha256",
                   "semantic_groups_sha256", "source_sha256", "analysis_sha256",
                   "content_sha256", "block_count", "profiles", "activity_field",
                   "signed_fine_species", "groups", "fine_state_identities",
                   "denominator_scope")
    for relative, fact in manifest["files"].items():
        path = output / relative
        if path.is_symlink() or not path.is_file() or _sha(path) != fact["sha256"] or \
                path.stat().st_size != fact["bytes"]:
            raise ValueError("family product file fact differs: " + relative)
        metadata, trees = _read_root(path)
        if any(metadata.get(key) != manifest.get(key) for key in common_keys):
            raise ValueError("family product embedded metadata differs")
        if relative.startswith("fine/"):
            rows = trees.get("pair_primitives", [])
            pdg = metadata.get("pdg")
            if metadata.get("product") != "FINE_SIGNED_SPECIES" or \
                    any(row["associate_pdg"] != pdg for row in rows) or \
                    len(rows) != fact["rows"]:
                raise ValueError("fine species product domain differs")
            if pdg in fine_pdgs:
                raise ValueError("duplicate fine species product")
            fine_pdgs.add(pdg)
            fine_rows.extend(rows)
    if (fine_pdgs != set(manifest["signed_fine_species"]) or
            {name for name in manifest["files"] if name.startswith("fine/")} !=
            {"fine/pdg-{}.root".format(str(pdg).replace("-", "m"))
             for pdg in manifest["signed_fine_species"]}):
        raise ValueError("fine species declared coverage differs")
    fine_keys = [(row["profile_id"], row["tune_id"], row["block"],
                  row["activity_bin"], row["trigger_pdg"], row["associate_pdg"],
                  row["sign"], row["dphi_bin"]) for row in fine_rows]
    if len(fine_keys) != len(set(fine_keys)):
        raise ValueError("duplicate fine primitive natural key")
    family_metadata, family_trees = _read_root(output / "families.root")
    family_rows = family_trees.get("pair_primitives", [])
    destination = {member: group["destination_pdg"] for group in manifest["groups"]
                   for member in group["members"]}
    grouped = {}
    for row in fine_rows:
        key = (row["profile_id"], row["tune_id"], row["block"], row["activity_bin"],
               row["trigger_pdg"], destination[row["associate_pdg"]], row["sign"],
               row["dphi_bin"])
        cell = grouped.setdefault(key, [0.0, 0.0]); cell[0] += row["count"]; cell[1] += row["sumw2"]
    observed = {(row["profile_id"], row["tune_id"], row["block"], row["activity_bin"],
                 row["trigger_pdg"], row["associate_pdg"], row["sign"], row["dphi_bin"]):
                (row["count"], row["sumw2"]) for row in family_rows}
    if len(observed) != len(family_rows) or \
            observed != {key: tuple(value) for key, value in grouped.items()}:
        raise ValueError("family product additive conservation differs")
    shared_metadata, shared = _read_root(output / "shared.root")
    if (shared_metadata.get("product") != "SHARED_ACTIVITY_AND_TRIGGER_PRIMITIVES" or
            len(shared.get("activity_primitives", [])) != manifest["files"]["shared.root"]["activity_rows"] or
            len(shared.get("trigger_primitives", [])) != manifest["files"]["shared.root"]["trigger_rows"]):
        raise ValueError("shared denominator product differs")
    activity_keys = [(row["tune_id"], row["block"], row["activity_bin"])
                     for row in shared["activity_primitives"]]
    trigger_keys = [(row["profile_id"], row["tune_id"], row["block"],
                     row["activity_bin"], row["trigger_pdg"])
                    for row in shared["trigger_primitives"]]
    if len(activity_keys) != len(set(activity_keys)) or \
            len(trigger_keys) != len(set(trigger_keys)):
        raise ValueError("duplicate shared primitive natural key")
    return manifest
