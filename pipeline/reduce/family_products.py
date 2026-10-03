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
GROUPED_SCHEMA = "hadronization_family_products_manifest_v3"
ALL_HEAVY_SCHEMA = "hadronization_family_products_manifest_v4"
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
    path = Path(path).absolute()
    if path.exists() or path.is_symlink():
        raise FileExistsError(path)
    temporary = str(path.parent / ("." + path.name + ".tmp"))
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    os.close(descriptor)
    original_directory = Path.cwd()
    try:
        os.chdir(path.parent)
        output = ROOT.TFile.Open(Path(temporary).name + "?reproducible", "RECREATE")
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
        os.chdir(original_directory)
        if os.path.exists(temporary):
            os.unlink(temporary)


def _pair_rows(primitives):
    return [dict(profile_id=key[0], tune_id=key[1], block=key[2],
                 activity_bin=key[3], trigger_pdg=key[4], associate_pdg=key[5],
                 sign=key[6], dphi_bin=key[7], count=cell.value,
                 sumw2=cell.sumw2)
            for key, cell in sorted(primitives.pairs.items())]


def _iter_pair_rows(primitives):
    for key in sorted(primitives.pairs):
        cell = primitives.pairs[key]
        yield dict(profile_id=key[0], tune_id=key[1], block=key[2],
                   activity_bin=key[3], trigger_pdg=key[4], associate_pdg=key[5],
                   sign=key[6], dphi_bin=key[7], count=cell.value,
                   sumw2=cell.sumw2)


def _group_cells(fine_rows, family_map):
    grouped = {}
    for row in fine_rows:
        destination = family_map.destination_by_member.get(row["associate_pdg"])
        if destination is None:
            continue
        key = (row["profile_id"], row["tune_id"], row["block"],
               row["activity_bin"], row["trigger_pdg"], destination,
               row["sign"], row["dphi_bin"])
        cell = grouped.setdefault(key, [0.0, 0.0])
        cell[0] += row["count"]
        cell[1] += row["sumw2"]
    return grouped


def _iter_group_rows(grouped):
    for key in sorted(grouped):
        value = grouped[key]
        yield dict(profile_id=key[0], tune_id=key[1], block=key[2],
                   activity_bin=key[3], trigger_pdg=key[4], associate_pdg=key[5],
                   sign=key[6], dphi_bin=key[7], count=value[0], sumw2=value[1])


def _group_rows(fine_rows, family_map):
    return list(_iter_group_rows(_group_cells(fine_rows, family_map)))


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
                   analysis_sha256, content_sha256, analysis_version="2.3.0",
                   trigger_selection="historical_hard_root", catalog_pdgs=None):
    """Write portable fine, family, and shared-denominator products once."""
    if any(len(value) != 64 for value in
           (source_sha256, analysis_sha256, content_sha256)):
        raise ValueError("family product binding digest differs")
    configurable = analysis_version in ("2.4.0", "2.5.0")
    all_heavy = analysis_version == "2.5.0"
    if all_heavy:
        from pipeline.query import model as query_model
        catalog = query_model.checked_heavy_catalog(
            query_model.support.ROOT / "config/heavy-catalog.json",
            _family.CATALOG_SHA256)
        expected_catalog = [state["pdg"] for state in catalog["states"]]
        if (catalog_pdgs != expected_catalog or
                trigger_selection not in ("all_origins", "historical_hard_root")):
            raise ValueError("complete fine catalog or trigger selection differs")
    fine_domain = {associate for _, associate in primitives.selected_pairs}
    if (len(primitives.selected_pairs) != len(set(primitives.selected_pairs)) or
            (not set(family_map.members) <= fine_domain if configurable else
             fine_domain != set(family_map.members)) or
            {trigger for trigger, _ in primitives.selected_pairs} !=
            set(primitives.selected_triggers)):
        raise ValueError("fine product declared pair domain differs")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    if not all_heavy:
        (output / "fine").mkdir()
    fine_rows = None if all_heavy else _pair_rows(primitives)
    grouped_rows = None if all_heavy else _group_rows(fine_rows, family_map)
    activity_rows, trigger_rows = _shared_rows(primitives)
    groups = [dict(destination_pdg=destination,
                   family=family_map.family_by_destination[destination],
                   members=list(family_map.members_by_destination[destination]))
              for destination in family_map.destinations]
    common = dict(schema=ALL_HEAVY_SCHEMA if all_heavy else
                  GROUPED_SCHEMA if configurable else SCHEMA,
        runtime_map_sha256=family_map.sha256,
        accepted_full_map_sha256=family_map.accepted_full_map_sha256,
        semantic_groups_sha256=family_map.semantic_groups_sha256,
        source_sha256=source_sha256, analysis_sha256=analysis_sha256,
        content_sha256=content_sha256, block_count=10,
        profiles=list(primitives.profile_ids), activity_field=primitives.activity_field,
        signed_fine_species=sorted(fine_domain), groups=groups,
        fine_state_identities=[family_map.fine_state_identities[pdg]
            for pdg in sorted(family_map.fine_state_identities)],
        denominator_scope="shared trigger/activity primitives stored once, including zero-partner trigger domains")
    if all_heavy:
        common["trigger_selection"] = trigger_selection
        common["fine_authority"] = dict(
            collection_index_sha256=source_sha256,
            catalog_sha256=_family.CATALOG_SHA256,
            signed_catalog_states=expected_catalog,
            sparse_families=["kinematics", "pairs"],
            storage="merged query THnSparse by signed PDG; paper-fine primitives are a selected derivative")
    files = {}
    if configurable:
        common["grouping_recipe_id"] = family_map.recipe_id
        # The historical 74-member recipe predates the complete heavy catalog.
        # The broad fine collection has its own independently pinned catalog.
        common["heavy_catalog_sha256"] = (_family.CATALOG_SHA256 if all_heavy else
                                           family_map.catalog_sha256)
        if (not family_map.recipe_bytes or hashlib.sha256(
                family_map.recipe_bytes).hexdigest() != family_map.sha256):
            raise ValueError("grouping recipe bytes differ from pinned map")
        recipe_path = output / "grouping-recipe.json"
        with recipe_path.open("xb") as stream:
            stream.write(family_map.recipe_bytes)
        files["grouping-recipe.json"] = {"sha256": family_map.sha256,
                                         "bytes": len(family_map.recipe_bytes)}
    independent = (dict(schema="hadronization_fine_pair_primitives_v1",
        source_sha256=source_sha256, content_sha256=content_sha256,
        profiles=list(primitives.profile_ids), activity_field=primitives.activity_field)
        if configurable else common)
    by_species = {pdg: [] for pdg in fine_domain}
    if not all_heavy:
        for row in fine_rows:
            by_species[row["associate_pdg"]].append(row)
    pair_tree = lambda rows: [("pair_primitives", ("profile_id", "tune_id"),
        PAIR_FIELDS[:6], PAIR_FIELDS[6:], rows)]
    if all_heavy:
        relative = "paper-fine.root"
        _write_root(output / relative, pair_tree(_iter_pair_rows(primitives)),
                    dict(independent, product="PAPER_FINE_PAIR_PRIMITIVES",
                         signed_species=sorted(by_species),
                         trigger_selection=trigger_selection))
        files[relative] = {"sha256": _sha(output / relative),
                           "bytes": (output / relative).stat().st_size,
                           "rows": len(primitives.pairs)}
    else:
        for pdg in sorted(by_species):
            relative = "fine/pdg-{}.root".format(str(pdg).replace("-", "m"))
            _write_root(output / relative, pair_tree(by_species[pdg]),
                        dict(independent, product="FINE_SIGNED_SPECIES", pdg=pdg))
            files[relative] = {"sha256": _sha(output / relative),
                               "bytes": (output / relative).stat().st_size,
                               "rows": len(by_species[pdg])}
    if all_heavy:
        grouped_cells = _group_cells(_iter_pair_rows(primitives), family_map)
        grouped_count = len(grouped_cells)
        grouped_rows = _iter_group_rows(grouped_cells)
    else:
        grouped_count = len(grouped_rows)
    _write_root(output / "families.root", pair_tree(grouped_rows),
                dict(common, product="DERIVED_SAVED_STATE_FAMILIES",
                     destinations=list(family_map.destinations)))
    if all_heavy:
        del grouped_cells, grouped_rows
    files["families.root"] = {"sha256": _sha(output / "families.root"),
        "bytes": (output / "families.root").stat().st_size,
        "rows": grouped_count}
    shared_trees = [
        ("activity_primitives", ("tune_id",), ACTIVITY_FIELDS[:2],
         ACTIVITY_FIELDS[2:], activity_rows),
        ("trigger_primitives", ("profile_id", "tune_id"), TRIGGER_FIELDS[:3],
         TRIGGER_FIELDS[3:], trigger_rows)]
    _write_root(output / "shared.root", shared_trees,
                dict(independent, product="SHARED_ACTIVITY_AND_TRIGGER_PRIMITIVES"))
    files["shared.root"] = {"sha256": _sha(output / "shared.root"),
        "bytes": (output / "shared.root").stat().st_size,
        "activity_rows": len(activity_rows), "trigger_rows": len(trigger_rows)}
    manifest = dict(common, fine_species_count=len(by_species),
                    family_destination_count=len(family_map.destinations),
                    files=files)
    if all_heavy:
        manifest["fine_catalog_species_count"] = len(expected_catalog)
        manifest["paper_pair_species_count"] = len(by_species)
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


def _verify_all_heavy_stream(output, manifest):
    """Cold exact product check with one grouped accumulator, not ROOT row lists."""
    import ROOT
    if set(manifest['files']) != {'grouping-recipe.json', 'paper-fine.root',
                                   'families.root', 'shared.root'}:
        raise ValueError('all-heavy product fileset differs')
    for relative, fact in manifest['files'].items():
        path = output / relative
        if (path.is_symlink() or not path.is_file() or
                path.stat().st_size != fact['bytes'] or _sha(path) != fact['sha256']):
            raise ValueError('family product file fact differs: ' + relative)

    common_keys = ('schema','runtime_map_sha256','accepted_full_map_sha256',
        'semantic_groups_sha256','source_sha256','analysis_sha256',
        'content_sha256','block_count','profiles','activity_field',
        'signed_fine_species','groups','fine_state_identities',
        'denominator_scope','grouping_recipe_id','heavy_catalog_sha256',
        'trigger_selection','fine_authority')
    independent = {key:manifest[key] for key in
        ('source_sha256','content_sha256','profiles','activity_field')}
    independent['schema'] = 'hadronization_fine_pair_primitives_v1'

    def opened(relative, expected):
        file = ROOT.TFile.Open(str(output / relative), 'READ')
        if not file or file.IsZombie():
            raise ValueError('family ROOT product cannot be opened')
        metadata = file.Get('family_product_metadata')
        if not metadata:
            file.Close(); raise ValueError('family ROOT product metadata is absent')
        value = json.loads(str(metadata.GetString()))
        if any(value.get(key) != expected[key] for key in expected):
            file.Close(); raise ValueError('family product embedded metadata differs')
        return file, value

    destination = {member:group['destination_pdg'] for group in manifest['groups']
                   for member in group['members']}
    grouped = {}
    fine, metadata = opened('paper-fine.root', independent)
    try:
        if (metadata.get('product') != 'PAPER_FINE_PAIR_PRIMITIVES' or
                metadata.get('trigger_selection') != manifest['trigger_selection'] or
                metadata.get('signed_species') != manifest['signed_fine_species']):
            raise ValueError('paper fine primitive product differs')
        tree = fine.Get('pair_primitives')
        if not tree or tree.GetEntries() != manifest['files']['paper-fine.root']['rows']:
            raise ValueError('paper fine primitive row count differs')
        previous = None
        for row in tree:
            key = (str(row.profile_id),str(row.tune_id),int(row.block),
                int(row.activity_bin),int(row.trigger_pdg),
                int(row.associate_pdg),int(row.sign),int(row.dphi_bin))
            if previous is not None and key <= previous:
                raise ValueError('duplicate or unordered fine primitive natural key')
            previous = key
            if key[5] not in manifest['signed_fine_species']:
                raise ValueError('fine primitive species differs')
            target = destination.get(key[5])
            if target is not None:
                family_key = key[:5] + (target,) + key[6:]
                cell = grouped.setdefault(family_key,[0.0,0.0])
                cell[0] += float(row.count); cell[1] += float(row.sumw2)
    finally:
        fine.Close()

    family, metadata = opened('families.root',
                              {key:manifest[key] for key in common_keys})
    try:
        if (metadata.get('product') != 'DERIVED_SAVED_STATE_FAMILIES' or
                metadata.get('destinations') !=
                [group['destination_pdg'] for group in manifest['groups']]):
            raise ValueError('derived family product identity differs')
        tree = family.Get('pair_primitives')
        if not tree or tree.GetEntries() != manifest['files']['families.root']['rows']:
            raise ValueError('family primitive row count differs')
        previous = None
        for row in tree:
            key = (str(row.profile_id),str(row.tune_id),int(row.block),
                int(row.activity_bin),int(row.trigger_pdg),
                int(row.associate_pdg),int(row.sign),int(row.dphi_bin))
            if previous is not None and key <= previous:
                raise ValueError('duplicate or unordered family primitive natural key')
            previous = key
            if grouped.pop(key,None) != [float(row.count),float(row.sumw2)]:
                raise ValueError('family product additive conservation differs')
        if grouped:
            raise ValueError('family product additive conservation differs')
    finally:
        family.Close()

    shared, metadata = opened('shared.root', independent)
    try:
        if metadata.get('product') != 'SHARED_ACTIVITY_AND_TRIGGER_PRIMITIVES':
            raise ValueError('shared denominator product differs')
        for name, fields, expected in (
            ('activity_primitives',('tune_id','block','activity_bin'),
             manifest['files']['shared.root']['activity_rows']),
            ('trigger_primitives',('profile_id','tune_id','block',
                                   'activity_bin','trigger_pdg'),
             manifest['files']['shared.root']['trigger_rows'])):
            tree = shared.Get(name)
            if not tree or tree.GetEntries() != expected:
                raise ValueError('shared denominator product differs')
            previous = None
            for row in tree:
                key = tuple(str(getattr(row,field)) if field.endswith('_id')
                            else int(getattr(row,field)) for field in fields)
                if previous is not None and key <= previous:
                    raise ValueError('duplicate shared primitive natural key')
                previous = key
    finally:
        shared.Close()
    return manifest


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
    if manifest.get("schema") not in (SCHEMA, GROUPED_SCHEMA, ALL_HEAVY_SCHEMA):
        raise ValueError("family product manifest schema differs")
    all_heavy = manifest["schema"] == ALL_HEAVY_SCHEMA
    configurable = manifest["schema"] in (GROUPED_SCHEMA, ALL_HEAVY_SCHEMA)
    if all_heavy:
        from pipeline.query import model as query_model
        authority = manifest.get("fine_authority")
        if (not isinstance(authority, dict) or
                authority.get("collection_index_sha256") != manifest["source_sha256"] or
                authority.get("catalog_sha256") != _family.CATALOG_SHA256 or
                authority.get("sparse_families") != ["kinematics", "pairs"] or
                authority.get("signed_catalog_states") != [state["pdg"] for state in
                    query_model.checked_heavy_catalog(
                        _family.ROOT / "config/heavy-catalog.json",
                        _family.CATALOG_SHA256)["states"]] or
                manifest.get("fine_catalog_species_count") != len(authority["signed_catalog_states"]) or
                manifest.get("paper_pair_species_count") != manifest.get("fine_species_count") or
                manifest.get("trigger_selection") not in
                    ("all_origins", "historical_hard_root")):
            raise ValueError("complete fine THnSparse authority differs")
    if configurable:
        recipe_fact = manifest["files"].get("grouping-recipe.json")
        if (not isinstance(recipe_fact, dict) or
                recipe_fact.get("sha256") != manifest.get("runtime_map_sha256")):
            raise ValueError("grouping recipe file/pin differs")
        admitted = _family.checked_family_map(output / "grouping-recipe.json",
                                               manifest["runtime_map_sha256"])
        admitted_groups = [dict(destination_pdg=destination,
                                family=admitted.family_by_destination[destination],
                                members=list(admitted.members_by_destination[destination]))
                           for destination in admitted.destinations]
        if (admitted_groups != manifest.get("groups") or
                admitted.recipe_id != manifest.get("grouping_recipe_id") or
                manifest.get("heavy_catalog_sha256") != _family.CATALOG_SHA256):
            raise ValueError("grouping recipe/manifest model differs")
    expected_files = set(manifest["files"]) | {"manifest.json"}
    actual_files = {path.relative_to(output).as_posix() for path in output.rglob("*")
                    if path.is_file()}
    if actual_files != expected_files:
        raise ValueError("family product exact fileset differs")
    if all_heavy:
        return _verify_all_heavy_stream(output, manifest)
    fine_rows = []
    fine_pdgs = set()
    common_keys = ("schema", "runtime_map_sha256", "accepted_full_map_sha256",
                   "semantic_groups_sha256", "source_sha256", "analysis_sha256",
                   "content_sha256", "block_count", "profiles", "activity_field",
                   "signed_fine_species", "groups", "fine_state_identities",
                   "denominator_scope")
    if configurable:
        common_keys += ("grouping_recipe_id", "heavy_catalog_sha256")
    if all_heavy:
        common_keys += ("trigger_selection", "fine_authority")
    independent = {key: manifest[key] for key in
                   ("source_sha256", "content_sha256", "profiles", "activity_field")}
    if configurable:
        independent["schema"] = "hadronization_fine_pair_primitives_v1"
    for relative, fact in manifest["files"].items():
        path = output / relative
        if path.is_symlink() or not path.is_file() or _sha(path) != fact["sha256"] or \
                path.stat().st_size != fact["bytes"]:
            raise ValueError("family product file fact differs: " + relative)
        if relative == "grouping-recipe.json":
            continue
        metadata, trees = _read_root(path)
        expected = (independent if configurable and
                    (relative.startswith("fine/") or relative == "shared.root" or
                     relative == "paper-fine.root")
                    else {key: manifest[key] for key in common_keys})
        if any(metadata.get(key) != value for key, value in expected.items()):
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
        if relative == "paper-fine.root":
            rows = trees.get("pair_primitives", [])
            if (not all_heavy or metadata.get("product") != "PAPER_FINE_PAIR_PRIMITIVES" or
                    metadata.get("trigger_selection") != manifest["trigger_selection"] or
                    metadata.get("signed_species") != manifest["signed_fine_species"] or
                    len(rows) != fact["rows"]):
                raise ValueError("paper fine primitive product differs")
            fine_pdgs.update(metadata["signed_species"])
            fine_rows.extend(rows)
    if (fine_pdgs != set(manifest["signed_fine_species"]) or
            {name for name in manifest["files"] if name.startswith("fine/")} !=
            (set() if all_heavy else
             {"fine/pdg-{}.root".format(str(pdg).replace("-", "m"))
              for pdg in manifest["signed_fine_species"]})):
        raise ValueError("fine species declared coverage differs")
    fine_keys = [(row["profile_id"], row["tune_id"], row["block"],
                  row["activity_bin"], row["trigger_pdg"], row["associate_pdg"],
                  row["sign"], row["dphi_bin"]) for row in fine_rows]
    if len(fine_keys) != len(set(fine_keys)):
        raise ValueError("duplicate fine primitive natural key")
    family_metadata, family_trees = _read_root(output / "families.root")
    if (family_metadata.get("product") != "DERIVED_SAVED_STATE_FAMILIES" or
            family_metadata.get("destinations") !=
            [group["destination_pdg"] for group in manifest["groups"]]):
        raise ValueError("derived family product identity differs")
    family_rows = family_trees.get("pair_primitives", [])
    destination = {member: group["destination_pdg"] for group in manifest["groups"]
                   for member in group["members"]}
    grouped = {}
    for row in fine_rows:
        if row["associate_pdg"] not in destination:
            continue
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
