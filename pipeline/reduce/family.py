"""Accepted saved-state family map and additive primitive grouping.

The map describes saved generator states.  It is deliberately applied before
normalization and jackknife evaluation; this module never sums ratios, errors,
or normalized spectra.
"""
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re


MAP_SCHEMA = "hadronization_public_saved_state_family_map_v1"
MAP_SHA256 = "9b441d5a6426999e7bd00f2f7935a32f5f97adc28b968c927e880e0249834d82"
ALL_HEAVY_MAP_SHA256 = "f2823dfee8fb11f7d84f2217ccc668df3dbbf8f0f69f61541ca418e105f3ba6f"
ACCEPTED_FULL_MAP_SHA256 = "f7aa4c13a88be93c0dc53b505d4f75d04a679ebfb94c90f022116ae1e87a5466"
ALL_HEAVY_FULL_MAP_SHA256 = "95a205e53baafca8d443a056f16b76026ce640cd14e298bfa62d220c774862e3"
SEMANTIC_GROUPS_SHA256 = "fea9ade870fc827d262a50d1bb8919f1a5a86e293d6f6dac6e18dad3b31714f4"
ALL_HEAVY_GROUPS_SHA256 = "d42da49bf7601b82241584cfb938085ba3599436fcfcb3e0057afe7c986be25f"
FINE_STATE_IDENTITIES_SHA256 = "dd0a48d12adb9a33dc1e4924e09c4b2e953d164edce0055e38b773ed54925110"
ALL_HEAVY_IDENTITIES_SHA256 = "9b6c33f0abc2d2046ba0a314ff670574c4e4e594c1e66d809a6482e4c08c1ef1"
PARTICLE_DATA_SHA256 = "330ba4e7f5a081235b5055f7b312fe6f5c9fe9c95411a845cba7a3e82e67ecca"
GROUP_RECIPE_SCHEMA = "hadronization_saved_state_grouping_recipe_v2"
CATALOG_SHA256 = "2d358f9e0a724602cf467c7d67df5e33d083f3d18196d60202fc450e5aba9433"
CATALOG_STATES_SHA256 = "f9bba3619ffe015346c4d43fe1e56f739371be4e5f9f2c7b82e9139a8458fe7d"
DEFERRED_XI = frozenset({-5324, -5314, -4324, -4314, 4314, 4324, 5314, 5324})
ROOT = Path(__file__).resolve().parents[2]
BASIS = {
    "unit_endpoint": "Exact unit endpoint probability in the pinned generator model; not a measured physical branching fraction",
    "kinematics": "sum saved-state associate primitives at saved kinematics",
    "pair_pt": "inclusive", "triggers": "unchanged",
    "standalone_spectra": "unchanged fine species"}


def file_sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


@dataclass(frozen=True)
class FamilyMap:
    sha256: str
    source_particle_data_sha256: str
    destination_by_member: dict
    members_by_destination: dict
    family_by_destination: dict
    deferred_members: frozenset
    accepted_full_map_sha256: str
    semantic_groups_sha256: str
    fine_state_identities: dict
    recipe_id: str = "approved-saved-state-families"
    catalog_sha256: str = ""
    recipe_bytes: bytes = b""

    @property
    def destinations(self):
        return tuple(self.members_by_destination)

    @property
    def members(self):
        return tuple(self.destination_by_member)


def _configured_recipe(value, actual, raw):
    """Admit a subset of independently pinned model-unit endpoints."""
    if set(value) != {"schema", "version", "id", "source_catalog",
                      "endpoint_evidence", "basis", "unlisted_species", "groups"} or \
            value["schema"] != GROUP_RECIPE_SCHEMA or value["version"] != "2.0.0" or \
            not isinstance(value["id"], str) or \
            not re.fullmatch(r"[a-z][a-z0-9_-]{0,63}", value["id"]):
        raise ValueError("grouping recipe schema, version or identity differs")
    if value["source_catalog"] != {"sha256": CATALOG_SHA256,
                                   "states_sha256": CATALOG_STATES_SHA256} or \
            value["endpoint_evidence"] != {
                "generator": "PYTHIA 8.317",
                "particle_data_sha256": PARTICLE_DATA_SHA256,
                "approved_runtime_map_sha256": ALL_HEAVY_MAP_SHA256,
                "approved_full_map_sha256": ALL_HEAVY_FULL_MAP_SHA256} or \
            value["basis"] != BASIS or value["unlisted_species"] != \
            "retained in fine THnSparse; excluded from this grouped result":
        raise ValueError("grouping recipe catalog, endpoint evidence or basis differs")
    from pipeline.query import model as query_model
    catalog = query_model.checked_heavy_catalog(ROOT / "config/heavy-catalog.json",
                                                 CATALOG_SHA256)
    catalog_by_pdg = {row["pdg"]: row for row in catalog["states"]}
    evidence = checked_family_map(ROOT / "config/associate-family-runtime-all-heavy.json",
                                  ALL_HEAVY_MAP_SHA256)
    groups = value["groups"]
    if not isinstance(groups, list) or not groups:
        raise ValueError("grouping recipe has no destinations")
    by_member, by_destination, family_by_destination = {}, {}, {}
    for group in groups:
        if type(group) is not dict or set(group) != {"destination_pdg", "family", "members"}:
            raise ValueError("grouping recipe destination fields differ")
        destination, members = group["destination_pdg"], group["members"]
        if (type(destination) is not int or destination not in
                evidence.members_by_destination or destination in by_destination or
                group["family"] != evidence.family_by_destination[destination] or
                not isinstance(members, list) or not members or
                any(type(member) is not int for member in members) or
                len(set(members)) != len(members) or
                not set(members) <= set(evidence.members_by_destination[destination]) or
                any(member in by_member or member not in catalog_by_pdg
                    for member in members)):
            raise ValueError("grouping recipe member has no approved unit endpoint")
        by_destination[destination] = tuple(members)
        family_by_destination[destination] = group["family"]
        by_member.update((member, destination) for member in members)
    for destination, members in by_destination.items():
        if (-destination not in by_destination or
                {-member for member in members} != set(by_destination[-destination])):
            raise ValueError("grouping recipe charge-conjugate coverage differs")
    semantic = hashlib.sha256(json.dumps(groups, sort_keys=True,
        separators=(",", ":"), ensure_ascii=True).encode("ascii")).hexdigest()
    identities = {pdg: evidence.fine_state_identities[pdg] for pdg in by_member
                  if pdg in evidence.fine_state_identities}
    if any(identities[pdg]["name"] != catalog_by_pdg[pdg]["name"] for pdg in identities):
        raise ValueError("grouping recipe identity differs from authenticated catalog")
    return FamilyMap(actual, PARTICLE_DATA_SHA256, by_member, by_destination,
                     family_by_destination, frozenset(set(evidence.members) - set(by_member)),
                     ALL_HEAVY_FULL_MAP_SHA256, semantic, identities,
                     value["id"], CATALOG_SHA256, raw)


def checked_family_map(path, expected_sha256=MAP_SHA256, *, accepted=True):
    """Load an exact release fixture or a caller-pinned grouping recipe."""
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError("grouping recipe is not a regular file")
    raw = path.read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    if actual != expected_sha256:
        raise ValueError("accepted family-map SHA256 differs")
    value = json.loads(raw)
    if value.get("schema") == GROUP_RECIPE_SCHEMA:
        return _configured_recipe(value, actual, raw)
    if expected_sha256 not in (MAP_SHA256, ALL_HEAVY_MAP_SHA256):
        raise ValueError("unrecognized sealed family-map fixture")
    all_heavy = expected_sha256 == ALL_HEAVY_MAP_SHA256
    full_sha = ALL_HEAVY_FULL_MAP_SHA256 if all_heavy else ACCEPTED_FULL_MAP_SHA256
    groups_sha = ALL_HEAVY_GROUPS_SHA256 if all_heavy else SEMANTIC_GROUPS_SHA256
    identities_sha = ALL_HEAVY_IDENTITIES_SHA256 if all_heavy else FINE_STATE_IDENTITIES_SHA256
    required = {"accepted_full_map_sha256", "basis", "counts",
                "deferred_signed_pdgs", "fine_state_identities",
                "fine_state_identities_sha256", "groups", "limitations", "schema",
                "semantic_groups_sha256", "source_model", "version"}
    if set(value) != required or value["schema"] != MAP_SCHEMA or \
            value["version"] != ("1.1.0" if all_heavy else "1.0.0"):
        raise ValueError("public family-map schema/version differs")
    if value["accepted_full_map_sha256"] != full_sha or \
            value["semantic_groups_sha256"] != groups_sha or \
            value["source_model"] != {
                "generator": "PYTHIA 8.317",
                "particle_data_sha256": PARTICLE_DATA_SHA256} or \
            value["basis"] != BASIS:
        raise ValueError("accepted family-map model/table basis differs")
    if value["counts"] != {"signed_members": sum(len(group["members"])
                                                   for group in value["groups"]),
            "signed_destinations": len(value["groups"]),
            "deferred_signed_xi_excitation_members": len(value["deferred_signed_pdgs"])}:
        raise ValueError("accepted family-map counts differ")
    semantic = hashlib.sha256(json.dumps(value["groups"], sort_keys=True,
        separators=(",", ":"), ensure_ascii=True).encode("ascii")).hexdigest()
    if semantic != groups_sha:
        raise ValueError("public family-map semantic groups differ")
    identities = value["fine_state_identities"]
    identity_digest = hashlib.sha256(json.dumps(identities, sort_keys=True,
        separators=(",", ":"), ensure_ascii=True).encode("ascii")).hexdigest()
    if (identity_digest != identities_sha or
            value["fine_state_identities_sha256"] != identity_digest or
            not isinstance(identities, list) or
            any(type(row) is not dict or set(row) != {"pdg", "id", "name", "spin2j1"}
                or type(row["pdg"]) is not int or type(row["spin2j1"]) is not int
                or row["spin2j1"] <= 0 or not isinstance(row["id"], str)
                or not row["id"] or not isinstance(row["name"], str) or not row["name"]
                for row in identities) or
            len({row["pdg"] for row in identities}) != len(identities) or
            len({row["id"] for row in identities}) != len(identities) or
            len({row["name"] for row in identities}) != len(identities)):
        raise ValueError("public fine-state catalog identities differ")

    destination_by_member = {}
    members_by_destination = {}
    family_by_destination = {}
    for group in value["groups"]:
        if set(group) != {"destination_pdg", "family", "members"}:
            raise ValueError("family group fields differ")
        destination = group["destination_pdg"]
        members = group["members"]
        if type(destination) is not int or destination == 0 or \
                not isinstance(group["family"], str) or not group["family"] or \
                not isinstance(members, list) or not members or destination not in members or \
                len(set(members)) != len(members) or destination in members_by_destination:
            raise ValueError("family group destination/member structure differs")
        if any(type(member) is not int or member == 0 or
               (member > 0) != (destination > 0) or
               member in destination_by_member for member in members):
            raise ValueError("family member sign/uniqueness differs")
        members_by_destination[destination] = tuple(members)
        family_by_destination[destination] = group["family"]
        destination_by_member.update((member, destination) for member in members)
    if (len(members_by_destination) != value["counts"]["signed_destinations"] or
            len(destination_by_member) != value["counts"]["signed_members"] or
            len(members_by_destination) != 42):
        raise ValueError("family map coverage differs")
    for destination, members in members_by_destination.items():
        if -destination not in members_by_destination or \
                tuple(-member for member in reversed(members)) != \
                tuple(reversed(members_by_destination[-destination])) or \
                family_by_destination[destination] != family_by_destination[-destination]:
            # Compare as sets below as the sealed order is not a physics rule.
            if {-member for member in members} != set(members_by_destination[-destination]) or \
                    family_by_destination[destination] != family_by_destination[-destination]:
                raise ValueError("family charge-conjugate coverage differs")

    deferred = value["deferred_signed_pdgs"]
    expected_deferred = set() if all_heavy else set(DEFERRED_XI)
    if not isinstance(deferred, list) or set(deferred) != expected_deferred or \
            len(deferred) != len(expected_deferred):
        raise ValueError("deferred family domain differs")
    if any(abs(member) in {4114, 4214, 4224} and
           abs(destination_by_member[member]) == 4122 for member in destination_by_member):
        raise ValueError("forbidden Sigma-to-Lambda family membership")
    if all_heavy and any(destination_by_member.get(pdg) != destination
                         for pdg, destination in {
                             4314: 4132, 4324: 4232, 5314: 5132, 5324: 5232,
                             -4314: -4132, -4324: -4232,
                             -5314: -5132, -5324: -5232}.items()):
        raise ValueError("pinned Xi-star unit endpoints differ")
    return FamilyMap(actual, PARTICLE_DATA_SHA256, destination_by_member,
                     members_by_destination, family_by_destination,
                     frozenset(deferred), full_sha,
                     groups_sha,
                     {row["pdg"]: row for row in identities},
                     "approved-pythia-endpoints" if all_heavy else "historical-saved-state-families",
                     CATALOG_SHA256 if all_heavy else "", raw)


def group_additive_rows(rows, family_map):
    """Sum fine full/block primitives by destination with strict coverage.

    Each natural key must contain exactly one row for every signed member.
    Trigger denominators are checked equal and carried once per grouped row.
    """
    required = {"tune", "block", "trigger_pdg", "associate_pdg", "sign",
                "count", "sumw2", "trigger_count"}
    natural = {}
    for row in rows:
        if set(row) != required or row["associate_pdg"] not in family_map.destination_by_member:
            raise ValueError("fine family primitive row/domain differs")
        if row["sign"] not in (-1, 1) or row["block"] not in range(1, 11) or \
                any(type(row[key]) not in (int, float) for key in
                    ("count", "sumw2", "trigger_count")) or row["sumw2"] < 0:
            raise ValueError("fine family primitive value differs")
        destination = family_map.destination_by_member[row["associate_pdg"]]
        key = (row["tune"], row["block"], row["trigger_pdg"], destination,
               row["sign"])
        if row["associate_pdg"] in natural.setdefault(key, {}):
            raise ValueError("duplicate fine family primitive member")
        natural[key][row["associate_pdg"]] = row
    result = []
    for key, by_member in sorted(natural.items()):
        expected = set(family_map.members_by_destination[key[3]])
        if set(by_member) != expected:
            raise ValueError("missing fine family primitive member")
        denominators = {row["trigger_count"] for row in by_member.values()}
        if len(denominators) != 1:
            raise ValueError("family members carry inconsistent trigger denominator")
        result.append(dict(tune=key[0], block=key[1], trigger_pdg=key[2],
                           associate_pdg=key[3], sign=key[4],
                           count=sum(row["count"] for row in by_member.values()),
                           sumw2=sum(row["sumw2"] for row in by_member.values()),
                           trigger_count=denominators.pop()))
    return result
