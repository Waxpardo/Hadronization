"""Derive summed baryon-to-meson balancing yields from retained fine species."""

from collections import defaultdict
import csv
import hashlib
import io
import json
import math
import os
from pathlib import Path
import tempfile

from . import archive_v4, family_products, projection as p


ROOT_DIR = Path(__file__).resolve().parents[2]
SCHEMA = "hadronization_baryon_meson_comparison_v1"
RECIPE = ROOT_DIR / "config/baryon-meson-comparison.json"
CLASSIFICATION = ROOT_DIR / "config/heavy-hadron-classification.json"
OBJECT_NAME = "baryon-meson-comparison.root"
CSV_NAME = "baryon-meson-comparison.csv"
SOURCE_SHA256 = p.file_digest(Path(__file__))
OBSERVABLES = ("Y_B", "Y_M", "R_BM", "D")
AVAILABLE = {"AVAILABLE", "AVAILABLE_ZERO_DISPERSION"}

POINT_FIELDS = dict(index="u", tune="s", trigger_pdg="i", sector="s",
                    species="u", meson_species="u", baryon_species="u",
                    trigger_count="d", baryon_os="d", baryon_ss="d",
                    meson_os="d", meson_ss="d", observable="s",
                    center_present="b", center="d", error_present="b",
                    error="d", variance_present="b", variance="d",
                    value_status="s", uncertainty_status="s", reasons="s")
BLOCK_FIELDS = dict(tune="s", trigger_pdg="i", block="u", trigger_count="d",
                    baryon_os="d", baryon_ss="d", meson_os="d",
                    meson_ss="d", baryon_net="d", meson_net="d")
MEMBERSHIP_FIELDS = dict(trigger_pdg="i", sector="s", os_pdg="i", ss_pdg="i",
                         name="s", kind="s", heavy_sign="i", charge3="i")
DELETION_FIELDS = dict(point="u", block="u", present="b", usable="b",
                       leaf="d", mean_present="b", mean="d", factor="d")


def checked_recipe(recipe):
    if (not isinstance(recipe, dict) or set(recipe) != {
            "schema", "profile_id", "ordered_trigger_pdgs"} or
            recipe["schema"] != "hadronization_baryon_meson_comparison_recipe_v1" or
            not isinstance(recipe["profile_id"], str) or not recipe["profile_id"] or
            recipe["ordered_trigger_pdgs"] != [421, 4122, 521, 5122]):
        raise ValueError("baryon/meson comparison recipe differs")
    return recipe


def _catalog(manifest):
    from pipeline.query import model as query_model
    from . import family
    catalog = query_model.checked_heavy_catalog(
        ROOT_DIR / "config/heavy-catalog.json", manifest["heavy_catalog_sha256"])
    if (manifest["heavy_catalog_sha256"] != family.CATALOG_SHA256 or
            catalog["particle_data_sha256"] != family.PARTICLE_DATA_SHA256):
        raise ValueError("baryon/meson comparison particle-data authority differs")
    rows = {row["pdg"]: row for row in catalog["states"]}
    if len(rows) != len(catalog["states"]):
        raise ValueError("heavy-particle catalog repeats a signed state")
    return catalog, rows


def _classification(catalog_meta, catalog, signed):
    """Read and cross-check the independent PYTHIA particle-type registry."""
    from . import family
    raw = CLASSIFICATION.read_bytes()
    value = json.loads(raw)
    canonical = p.canonical(value["states"])
    if (set(value) != {"schema", "generator", "basis", "heavy_catalog_sha256",
                       "particle_data_sha256", "source_audit_sha256",
                       "states_sha256", "states"} or
            value["schema"] != "hadronization_heavy_hadron_classification_v1" or
            value["generator"] != {"name": "PYTHIA", "version": "8.317"} or
            value["basis"] != "particleData.isMeson/isBaryon" or
            value["heavy_catalog_sha256"] != family.CATALOG_SHA256 or
            value["particle_data_sha256"] != catalog_meta["particle_data_sha256"] or
            value["states_sha256"] != hashlib.sha256(canonical.encode("ascii")).hexdigest()):
        raise ValueError("independent PYTHIA classification registry differs")
    rows = value["states"]
    by_pdg = {row.get("pdg"): row for row in rows if isinstance(row, dict)}
    if (len(by_pdg) != len(rows) or sorted(by_pdg) != signed or
            any(set(row) != {"pdg", "name", "kind"} or
                row["kind"] not in ("meson", "baryon") or
                row["name"] != catalog[pdg]["name"] or
                row["kind"] != _kind(pdg)
                for pdg, row in by_pdg.items())):
        raise ValueError("independent PYTHIA classification content differs")
    return value, {pdg: row["kind"] for pdg, row in by_pdg.items()}, hashlib.sha256(raw).hexdigest()


def read_parent_binding(path, expected_root_sha, expected_value_sha):
    """Authenticate the immutable parent while reading only its binding row."""
    path = Path(path).absolute()
    p._reducer().reject_symlink_components(path, "baryon/meson parent ROOT")
    p._reducer().regular_file(path, "baryon/meson parent ROOT")
    p.validate(expected_root_sha, "Digest", "parent ROOT SHA-256")
    p.validate(expected_value_sha, "Digest", "parent value SHA-256")
    if p.file_digest(path) != expected_root_sha:
        raise ValueError("baryon/meson parent physical SHA-256 differs")
    import ROOT
    root = ROOT.TFile.Open(str(path), "READ")
    if not root or root.IsZombie():
        raise ValueError("baryon/meson parent ROOT open failed")
    try:
        metadata_object = root.Get("v4_metadata")
        bindings = root.Get("bindings")
        if not metadata_object or not bindings or bindings.GetEntries() != 1:
            raise ValueError("baryon/meson parent binding objects differ")
        metadata = json.loads(str(metadata_object.GetString()))
        if (metadata.get("schema") != "hadronization_self_contained_typed_root_v4" or
                metadata.get("payload_schema") != "hadronization_projection_result_v4" or
                metadata.get("value_sha256") != expected_value_sha):
            raise ValueError("baryon/meson parent logical identity differs")
        bindings.GetEntry(0)
        binding = dict(collection_index_sha256=str(bindings.collection_index_sha256),
            collection_scientific_identity_sha256=str(
                bindings.collection_scientific_identity_sha256))
        if (binding["collection_index_sha256"] != metadata.get(
                "collection_index_sha256") or
                str(bindings.science_content_sha256) != metadata.get(
                    "science_content_sha256") or
                str(bindings.schema) != metadata.get("payload_schema")):
            raise ValueError("baryon/meson parent typed binding differs")
        campaign = ("FULL_ACCEPTED_CAMPAIGN" if
                    str(bindings.admission_qualification) ==
                    "FULL_ACCEPTED_DOMAIN_CLOSED" else "PARTIAL_SAMPLE")
        return dict(schema=metadata["payload_schema"],
            science_content_sha256=metadata["science_content_sha256"],
            campaign_state=campaign, artifact_binding=binding)
    finally:
        root.Close()


def _sector(trigger):
    return "charm" if trigger in (421, 4122) else "beauty"


def _heavy_sign(row, sector):
    return (row["nc"] - row["ncbar"] if sector == "charm"
            else row["nb"] - row["nbbar"])


def _kind(pdg):
    """Standard PDG low-digit classification used by the producer registry."""
    return "baryon" if (abs(pdg) // 1000) % 10 else "meson"


def membership(manifest, recipe):
    checked_recipe(recipe)
    catalog, rows = _catalog(manifest)
    signed = manifest["signed_fine_species"]
    if (len(signed) != 202 or signed != sorted(signed) or
            set(signed) - set(rows)):
        raise ValueError("retained fine-species domain differs")
    classification, kinds, classification_sha = _classification(catalog, rows, signed)
    result = []
    domains = {}
    for trigger in recipe["ordered_trigger_pdgs"]:
        sector = _sector(trigger)
        trigger_sign = _heavy_sign(rows[trigger], sector)
        selected = []
        for pdg in signed:
            state = rows[pdg]
            if sector == "charm" and (state["nb"] or state["nbbar"]):
                continue
            sign = _heavy_sign(state, sector)
            if trigger_sign * sign >= 0:
                continue
            selected.append(pdg)
            result.append(dict(trigger_pdg=trigger, sector=sector, os_pdg=pdg,
                ss_pdg=-pdg, name=state["name"], kind=kinds[pdg],
                heavy_sign=sign, charge3=state["charge3"]))
        expected = 42 if sector == "charm" else 59
        if (len(selected) != expected or len(set(selected)) != expected or
                set(selected) & {-pdg for pdg in selected}):
            raise ValueError("baryon/meson eligible associate domain differs")
        domains[trigger] = selected
    checked_membership(result, rows, domains, kinds)
    return catalog, domains, result, classification, classification_sha


def checked_membership(records, catalog, domains, kinds=None):
    kinds = kinds or {pdg: _kind(pdg) for pdg in catalog}
    expected = []
    for trigger, selected in domains.items():
        sector = _sector(trigger)
        for pdg in selected:
            state = catalog[pdg]
            expected.append(dict(trigger_pdg=trigger, sector=sector, os_pdg=pdg,
                ss_pdg=-pdg, name=state["name"], kind=kinds[pdg],
                heavy_sign=_heavy_sign(state, sector), charge3=state["charge3"]))
    if records != expected:
        raise ValueError("baryon/meson signed membership or classification differs")
    return records


def _native():
    import ROOT
    if not hasattr(ROOT, "HadronizationBaryonMeson"):
        ROOT.gInterpreter.AddIncludePath(str(ROOT_DIR))
        if not ROOT.gInterpreter.Declare(r'''
#include "pipeline/reduce/statistics.hpp"
#include <TFile.h>
#include <TTreeReader.h>
#include <TTreeReaderValue.h>
#include <map>
#include <set>
#include <tuple>
namespace HadronizationBaryonMeson {
using namespace Hadronization::Reduction;
struct PairCell { std::string tune; int trigger=0,associate=0,sign=0,block=0; double count=0; };
struct TriggerCell { std::string tune; int trigger=0,block=0; double count=0; };
std::vector<PairCell> Pairs(const std::string& path,const std::string& profile,
                            const std::vector<int>& triggers) {
  std::set<int> wanted(triggers.begin(),triggers.end());
  using Key=std::tuple<std::string,int,int,int,int>;
  std::map<Key,double> sums;
  TFile file(path.c_str(),"READ"); if(file.IsZombie()) throw std::runtime_error("fine ROOT open failed");
  TTreeReader r("pair_primitives",&file);
  TTreeReaderValue<std::string> p(r,"profile_id"),t(r,"tune_id");
  TTreeReaderValue<int> tr(r,"trigger_pdg"),a(r,"associate_pdg"),sg(r,"sign"),b(r,"block");
  TTreeReaderValue<double> n(r,"count"),w2(r,"sumw2");
  while(r.Next()) { if(*p!=profile || !wanted.count(*tr)) continue;
    if(*n!=*w2 || *n<0 || *n!=std::floor(*n) || *b<1 || *b>10)
      throw std::runtime_error("fine pair primitive contract differs");
    sums[{*t,*tr,*a,*sg,*b}]+=*n;
  }
  std::vector<PairCell> out; out.reserve(sums.size());
  for(const auto& [key,value]:sums) out.push_back({std::get<0>(key),std::get<1>(key),
      std::get<2>(key),std::get<3>(key),std::get<4>(key),value});
  return out;
}
std::vector<TriggerCell> Triggers(const std::string& path,const std::string& profile,
                                  const std::vector<int>& triggers) {
  std::set<int> wanted(triggers.begin(),triggers.end());
  using Key=std::tuple<std::string,int,int>; std::map<Key,double> sums;
  TFile file(path.c_str(),"READ"); if(file.IsZombie()) throw std::runtime_error("shared ROOT open failed");
  TTreeReader r("trigger_primitives",&file);
  TTreeReaderValue<std::string> p(r,"profile_id"),t(r,"tune_id");
  TTreeReaderValue<int> tr(r,"trigger_pdg"),b(r,"block");
  TTreeReaderValue<double> n(r,"count"),w2(r,"sumw2");
  while(r.Next()) { if(*p!=profile || !wanted.count(*tr)) continue;
    if(*n!=*w2 || *n<0 || *n!=std::floor(*n) || *b<1 || *b>10)
      throw std::runtime_error("trigger primitive contract differs");
    sums[{*t,*tr,*b}]+=*n;
  }
  std::vector<TriggerCell> out; out.reserve(sums.size());
  for(const auto& [key,value]:sums) out.push_back({std::get<0>(key),std::get<1>(key),
      std::get<2>(key),value});
  return out;
}
DenominatorSeries Parent(const std::vector<std::vector<double>>& b,unsigned column,
                         const std::string& id) {
  DenominatorSeries d; d.id=id; d.exact=true; d.algebraicallySurvives=true;
  for(const auto& row:b) d.blocks.push_back(row[column]); return d;
}
JackknifeResult Yields(const std::vector<std::vector<double>>& b) {
  return PooledDeleteOne(b,[](const auto& x)->FunctionValue {
    if(x[2]==0.) return {false,{},"POOLED_DENOMINATOR_ZERO"};
    return {true,{x[0]/x[2],x[1]/x[2],(x[1]-x[0])/x[2]}, {}};
  },{Parent(b,2,"trigger_count")});
}
JackknifeResult Ratio(const std::vector<std::vector<double>>& b) {
  return PooledDeleteOne(b,[](const auto& x)->FunctionValue {
    if(x[1]==0.) return {false,{},"POOLED_DENOMINATOR_ZERO"};
    return {true,{x[0]/x[1]}, {}};
  },{Parent(b,1,"meson_net_count")});
}
}
'''):
            raise RuntimeError("native baryon/meson comparison compilation failed")
    return ROOT


def _result(result, slots):
    def vector(values):
        return [float(x).hex() for x in values] if len(values) else None
    centers = vector(result.center)
    errors = vector(result.standardError)
    variances = vector(result.diagonalVariance)
    leaves = [vector(row) for row in result.complements]
    means = vector(result.leaveMean)
    return {name: dict(center=None if centers is None else centers[i],
                       error=None if errors is None else errors[i],
                       variance=None if variances is None else variances[i],
                       value_status=str(result.valueStatus),
                       uncertainty_status=str(result.uncertaintyStatus),
                       reasons=list(map(str, result.reasons)),
                       leaves=[None if row is None else row[i] for row in leaves],
                       leave_mean=None if means is None else means[i])
            for i, name in enumerate(slots)}


def estimate(blocks):
    if (len(blocks) != 10 or any(len(row) != 3 or any(
            not math.isfinite(x) or x != int(x) or abs(x) >= 2**53
            for x in row) for row in blocks)):
        raise ValueError("baryon/meson comparison requires exact K10 primitives")
    root = _native()
    matrix = root.std.vector("std::vector<double>")()
    for row in blocks:
        values = root.std.vector("double")()
        for value in row:
            values.push_back(value)
        matrix.push_back(values)
    result = _result(root.HadronizationBaryonMeson.Yields(matrix),
                     ("Y_B", "Y_M", "D"))
    result.update(_result(root.HadronizationBaryonMeson.Ratio(matrix), ("R_BM",)))
    return result


def _extract(products, manifest, recipe, catalog, domains):
    root = _native()
    triggers = root.std.vector("int")()
    for trigger in recipe["ordered_trigger_pdgs"]:
        triggers.push_back(trigger)
    pairs = defaultdict(float)
    for row in root.HadronizationBaryonMeson.Pairs(
            str(products / "paper-fine.root"), recipe["profile_id"], triggers):
        tune, trigger, associate = str(row.tune), int(row.trigger), int(row.associate)
        sector = _sector(trigger)
        qprod = _heavy_sign(catalog[trigger], sector) * _heavy_sign(catalog[associate], sector)
        if qprod == 0 or qprod * int(row.sign) <= 0:
            raise ValueError("fine pair heavy-flavour sign differs")
        pairs[tune, trigger, associate, int(row.block)] += float(row.count)
    denominators = defaultdict(float)
    for row in root.HadronizationBaryonMeson.Triggers(
            str(products / "shared.root"), recipe["profile_id"], triggers):
        denominators[str(row.tune), int(row.trigger), int(row.block)] += float(row.count)
    tunes = sorted({key[0] for key in denominators}, key=lambda x:
                   ("MONASH", "JUNCTIONS", "CLOSEPACKING").index(x)
                   if x in ("MONASH", "JUNCTIONS", "CLOSEPACKING") else 99)
    if tunes != ["MONASH", "JUNCTIONS", "CLOSEPACKING"]:
        raise ValueError("baryon/meson comparison tune domain differs")
    block_rows = []
    grouped = {}
    for tune in tunes:
        for trigger in recipe["ordered_trigger_pdgs"]:
            by_kind = {kind: {sign: [0.] * 10 for sign in ("os", "ss")}
                       for kind in ("baryon", "meson")}
            for associate in domains[trigger]:
                kind = _kind(associate)
                for block in range(1, 11):
                    by_kind[kind]["os"][block-1] += pairs[tune, trigger, associate, block]
                    by_kind[kind]["ss"][block-1] += pairs[tune, trigger, -associate, block]
            blocks = []
            for block in range(1, 11):
                bo, bs = by_kind["baryon"]["os"][block-1], by_kind["baryon"]["ss"][block-1]
                mo, ms = by_kind["meson"]["os"][block-1], by_kind["meson"]["ss"][block-1]
                trigger_count = denominators[tune, trigger, block]
                blocks.append([bo-bs, mo-ms, trigger_count])
                block_rows.append(dict(tune=tune, trigger_pdg=trigger, block=block,
                    trigger_count=trigger_count, baryon_os=bo, baryon_ss=bs,
                    meson_os=mo, meson_ss=ms, baryon_net=bo-bs, meson_net=mo-ms))
            grouped[tune, trigger] = (blocks, by_kind)
    return tunes, grouped, block_rows


def derive(parent, root_sha, value_sha, products, manifest_sha, recipe):
    """Derive the compact comparison from verified public numerical products."""
    checked_recipe(recipe)
    products = Path(products).absolute()
    manifest = family_products.verify_products(products, manifest_sha)
    if (manifest["schema"] != family_products.ALL_HEAVY_SCHEMA or
            manifest["block_count"] != 10 or recipe["profile_id"] not in manifest["profiles"] or
            manifest["source_sha256"] != parent["artifact_binding"][
                "collection_index_sha256"] or
            manifest["content_sha256"] != parent["artifact_binding"][
                "collection_scientific_identity_sha256"]):
        raise ValueError("family products do not bind to the numerical result")
    catalog_meta, catalog = _catalog(manifest)
    _, domains, members, classification, classification_sha = membership(manifest, recipe)
    tunes, grouped, block_rows = _extract(products, manifest, recipe, catalog, domains)
    points = []
    for tune in tunes:
        for trigger in recipe["ordered_trigger_pdgs"]:
            blocks, by_kind = grouped[tune, trigger]
            estimates = estimate(blocks)
            totals = dict(trigger_count=math.fsum(row[2] for row in blocks),
                baryon_os=math.fsum(by_kind["baryon"]["os"]),
                baryon_ss=math.fsum(by_kind["baryon"]["ss"]),
                meson_os=math.fsum(by_kind["meson"]["os"]),
                meson_ss=math.fsum(by_kind["meson"]["ss"]))
            counts = dict(species=len(domains[trigger]),
                meson_species=sum(_kind(x) == "meson" for x in domains[trigger]),
                baryon_species=sum(_kind(x) == "baryon" for x in domains[trigger]))
            for observable in OBSERVABLES:
                points.append(dict(index=len(points), tune=tune, trigger_pdg=trigger,
                    sector=_sector(trigger), observable=observable, **counts, **totals,
                    **estimates[observable]))
    covariance = []
    for a in points:
        row = []
        for b in points:
            if (a["uncertainty_status"] not in AVAILABLE or
                    b["uncertainty_status"] not in AVAILABLE):
                token = None
            elif a["tune"] != b["tune"]:
                token = 0.0.hex()
            else:
                am, bm = float.fromhex(a["leave_mean"]), float.fromhex(b["leave_mean"])
                token = (.9 * math.fsum((float.fromhex(x)-am)*(float.fromhex(y)-bm)
                                        for x, y in zip(a["leaves"], b["leaves"]))).hex()
            row.append(token)
        covariance.append(row)
    return dict(schema=SCHEMA, parent_root_sha256=root_sha,
        parent_value_sha256=value_sha, parent_science_content_sha256=parent["science_content_sha256"],
        family_manifest_sha256=manifest_sha, family_manifest_content_sha256=manifest["manifest_content_sha256"],
        family_product_sha256={name: fact["sha256"] for name, fact in manifest["files"].items()},
        heavy_catalog_sha256=manifest["heavy_catalog_sha256"],
        particle_data_sha256=catalog_meta["particle_data_sha256"],
        classification_sha256=classification_sha,
        classification_states_sha256=classification["states_sha256"],
        classification_source_audit_sha256=classification["source_audit_sha256"],
        recipe=recipe, recipe_sha256=p.digest(recipe), tunes=tunes,
        derivation_source_sha256=SOURCE_SHA256,
        estimator=p.ESTIMATOR, K=10, units="dimensionless",
        statistics_header_sha256=p.file_digest(ROOT_DIR / "pipeline/reduce/statistics.hpp"),
        campaign_state=parent["campaign_state"], membership=members,
        block_primitives=block_rows, points=points, covariance=covariance)


def _rows(value):
    point_rows, deletion_rows = [], []
    for point in value["points"]:
        row = {key: point[key] for key in POINT_FIELDS if key in point}
        row["reasons"] = ";".join(point["reasons"])
        for name in ("center", "error", "variance"):
            row[name + "_present"] = point[name] is not None
            row[name] = 0. if point[name] is None else float.fromhex(point[name])
        point_rows.append(row)
        for block, leaf in enumerate(point["leaves"], 1):
            mean = point["leave_mean"]
            usable = point["uncertainty_status"] in AVAILABLE and leaf is not None
            deletion_rows.append(dict(point=point["index"], block=block,
                present=leaf is not None, usable=usable,
                leaf=0. if leaf is None else float.fromhex(leaf),
                mean_present=mean is not None, mean=0. if mean is None else float.fromhex(mean),
                factor=(math.sqrt(.9)*(float.fromhex(leaf)-float.fromhex(mean))
                        if usable else 0.)))
    return point_rows, deletion_rows


def csv_bytes(value):
    stream = io.StringIO(newline="")
    fields = ["tune", "trigger_pdg", "sector", "species", "meson_species",
              "baryon_species", "Y_B", "Y_B_error", "Y_M", "Y_M_error",
              "R_BM", "R_BM_error", "D", "D_error", "value_status",
              "uncertainty_status"]
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    by_key = {(x["tune"], x["trigger_pdg"], x["observable"]): x
              for x in value["points"]}
    for tune in value["tunes"]:
        for trigger in value["recipe"]["ordered_trigger_pdgs"]:
            source = by_key[tune, trigger, "R_BM"]
            row = {key: source[key] for key in fields[:6]}
            for observable in OBSERVABLES:
                point = by_key[tune, trigger, observable]
                row[observable] = "" if point["center"] is None else repr(float.fromhex(point["center"]))
                row[observable + "_error"] = "" if point["error"] is None else repr(float.fromhex(point["error"]))
            row["value_status"] = source["value_status"]
            row["uncertainty_status"] = source["uncertainty_status"]
            writer.writerow(row)
    return stream.getvalue().encode("ascii")


def write(value, output):
    output = Path(output).absolute()
    p._reducer().reject_symlink_components(output, "baryon/meson comparison output")
    if output.exists() or output.is_symlink():
        raise FileExistsError(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    import ROOT
    descriptor, name = tempfile.mkstemp(prefix=".baryon-meson-", suffix=".root", dir=output.parent)
    os.close(descriptor); temporary = Path(name)
    try:
        root = ROOT.TFile.Open(str(temporary), "RECREATE")
        if not root or root.IsZombie():
            raise ValueError("baryon/meson comparison ROOT creation failed")
        ROOT.TObjString(p.canonical(value)).Write("payload")
        ROOT.TObjString(p.digest(value)).Write("value_sha256")
        row_sets = (("points", POINT_FIELDS, _rows(value)[0]),
                    ("block_primitives", BLOCK_FIELDS, value["block_primitives"]),
                    ("membership", MEMBERSHIP_FIELDS, value["membership"]),
                    ("deletions", DELETION_FIELDS, _rows(value)[1]))
        for name, fields, rows in row_sets:
            tree, holders = archive_v4._tree(ROOT, name, fields)
            for row in rows:
                archive_v4._fill(tree, holders, row)
            tree.Write()
        n = len(value["points"])
        covariance = ROOT.TH2D("covariance", "Joint covariance;Point;Point", n, 0, n, n, 0, n)
        valid = ROOT.TH2I("covariance_valid", "Covariance validity;Point;Point", n, 0, n, n, 0, n)
        for i, row in enumerate(value["covariance"], 1):
            for j, token in enumerate(row, 1):
                covariance.SetBinContent(i, j, 0. if token is None else float.fromhex(token))
                valid.SetBinContent(i, j, int(token is not None))
        covariance.Write(); valid.Write(); root.Close()
        read(temporary, p.file_digest(temporary))
        with temporary.open("rb") as stream:
            os.fsync(stream.fileno())
        os.link(temporary, output)
    finally:
        temporary.unlink(missing_ok=True)
    return p.file_digest(output)


def read(path, expected_sha):
    path = Path(path).absolute()
    p._reducer().reject_symlink_components(path, "baryon/meson comparison ROOT")
    p._reducer().regular_file(path, "baryon/meson comparison ROOT")
    p.validate(expected_sha, "Digest", "baryon/meson comparison SHA-256")
    if p.file_digest(path) != expected_sha:
        raise ValueError("baryon/meson comparison physical SHA-256 differs")
    import ROOT
    root = ROOT.TFile.Open(str(path))
    if not root or root.IsZombie():
        raise ValueError("baryon/meson comparison ROOT open failed")
    try:
        expected_objects = {"payload", "value_sha256", "points", "block_primitives",
                            "membership", "deletions", "covariance", "covariance_valid"}
        keys = list(root.GetListOfKeys())
        if any(key.GetCycle() != 1 for key in keys) or {key.GetName() for key in keys} != expected_objects:
            raise ValueError("baryon/meson comparison ROOT object set differs")
        value = json.loads(str(root.Get("payload").GetString()))
        if (value.get("schema") != SCHEMA or
                value.get("derivation_source_sha256") != SOURCE_SHA256 or
                p.digest(value) != str(root.Get("value_sha256").GetString())):
            raise ValueError("baryon/meson comparison value identity differs")
        checked_recipe(value["recipe"])
        row_sets = (("points", POINT_FIELDS, _rows(value)[0]),
                    ("block_primitives", BLOCK_FIELDS, value["block_primitives"]),
                    ("membership", MEMBERSHIP_FIELDS, value["membership"]),
                    ("deletions", DELETION_FIELDS, _rows(value)[1]))
        for name, fields, rows in row_sets:
            tree = root.Get(name)
            if tree.GetEntries() != len(rows) or {b.GetName() for b in tree.GetListOfBranches()} != set(fields):
                raise ValueError("baryon/meson comparison typed row domain differs")
            for actual, expected in zip(tree, rows):
                for field, kind in fields.items():
                    observed = getattr(actual, field)
                    observed = str(observed) if kind == "s" else float(observed) if kind == "d" else int(observed)
                    if observed != expected[field]:
                        raise ValueError("baryon/meson comparison typed value differs: " + field)
        n = len(value["points"])
        for i, row in enumerate(value["covariance"], 1):
            for j, token in enumerate(row, 1):
                if (root.Get("covariance_valid").GetBinContent(i, j) != int(token is not None) or
                        root.Get("covariance").GetBinContent(i, j) !=
                        (0. if token is None else float.fromhex(token))):
                    raise ValueError("baryon/meson comparison covariance content differs")
        if root.Get("covariance").GetNbinsX() != n or root.Get("covariance").GetNbinsY() != n:
            raise ValueError("baryon/meson comparison covariance domain differs")
        return value
    finally:
        root.Close()


def verify(value, parent, root_sha, value_sha, products, manifest_sha):
    expected = derive(parent, root_sha, value_sha, products, manifest_sha, value["recipe"])
    def equal(left, right):
        if isinstance(left, dict):
            return (isinstance(right, dict) and set(left) == set(right) and
                    all(equal(item, right[key]) for key, item in left.items()))
        if isinstance(left, list):
            return (isinstance(right, list) and len(left) == len(right) and
                    all(equal(a, b) for a, b in zip(left, right)))
        if (isinstance(left, str) and isinstance(right, str) and
                left.startswith(("0x", "-0x")) and
                right.startswith(("0x", "-0x"))):
            return math.isclose(float.fromhex(left), float.fromhex(right),
                                rel_tol=5e-11, abs_tol=2e-15)
        return left == right
    if not equal(value, expected):
        raise ValueError("baryon/meson comparison differs from fine-primitive reconstruction")
    return value
