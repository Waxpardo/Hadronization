"""Accepted saved-state family map and additive primitive grouping.

The map describes saved generator states.  It is deliberately applied before
normalization and jackknife evaluation; this module never sums ratios, errors,
or normalized spectra.
"""
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path


MAP_SCHEMA = "architect_accepted_saved_state_group_map_v1"
MAP_SHA256 = "f7aa4c13a88be93c0dc53b505d4f75d04a679ebfb94c90f022116ae1e87a5466"
PARTICLE_DATA_SHA256 = "330ba4e7f5a081235b5055f7b312fe6f5c9fe9c95411a845cba7a3e82e67ecca"
DEFERRED_XI = frozenset({-5324, -5314, -4324, -4314, 4314, 4324, 5314, 5324})


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
    inventory_pdgs: frozenset

    @property
    def destinations(self):
        return tuple(self.members_by_destination)

    @property
    def members(self):
        return tuple(self.destination_by_member)


def checked_family_map(path, expected_sha256=MAP_SHA256, *, accepted=True):
    """Load the one owner-accepted 74-member map, failing closed on drift."""
    path = Path(path)
    actual = file_sha256(path)
    if actual != expected_sha256 or (accepted and expected_sha256 != MAP_SHA256):
        raise ValueError("accepted family-map SHA256 differs")
    value = json.loads(path.read_text(encoding="utf-8"))
    required = {"candidate_map_sha256", "counts", "groups", "inventory",
                "kinematic_basis", "limitations", "pair_pt", "schema",
                "source_particle_data", "standalone_spectra", "status",
                "supersedes_ruling_sha256", "triggers", "unit_basis"}
    if set(value) != required or value["schema"] != MAP_SCHEMA or \
            value["status"] != "ACCEPTED_FOR_BOUNDED_IMPLEMENTATION_NOT_PRODUCTION":
        raise ValueError("accepted family-map schema/status differs")
    if value["source_particle_data"].get("sha256") != PARTICLE_DATA_SHA256 or \
            value["unit_basis"] != (
                "Exact unit endpoint probability in pinned PYTHIA 8.317 model, "
                "not measured physical BR=1") or \
            value["kinematic_basis"] != "sum_saved_state_associate_primitives_at_saved_kinematics" or \
            value["pair_pt"] != "inclusive" or value["triggers"] != "unchanged" or \
            value["standalone_spectra"] != "unchanged_fine_species":
        raise ValueError("accepted family-map model/table basis differs")
    if value["counts"] != {
            "additional_signed_members": 32, "anchors": 42,
            "catalog_signed_states": 219,
            "deferred_signed_xi_excitation_members": 8,
            "grouped_signed_members": 74, "other_excluded_states": 137}:
        raise ValueError("accepted family-map counts differ")

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
    if len(members_by_destination) != 42 or len(destination_by_member) != 74:
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

    inventory = value["inventory"]
    inventory_pdgs = [row.get("pdg") for row in inventory]
    if len(inventory_pdgs) != 219 or len(set(inventory_pdgs)) != 219 or \
            any(type(pdg) is not int or pdg == 0 for pdg in inventory_pdgs):
        raise ValueError("family inventory coverage differs")
    accepted = set()
    deferred = set()
    for row in inventory:
        disposition = row.get("disposition")
        if disposition in {"ACCEPT_ANCHOR", "ACCEPT_PINNED_MODEL_UNIT_SAVED_STATE"}:
            accepted.add(row["pdg"])
            if row.get("destination_pdg") != destination_by_member.get(row["pdg"]):
                raise ValueError("family inventory endpoint differs")
        elif disposition == "DEFER_UNPLOTTED_XI_EXCITATION_TO_PHASE_B":
            deferred.add(row["pdg"])
            if row.get("destination_pdg") is not None:
                raise ValueError("deferred state was assigned a family endpoint")
    if accepted != set(destination_by_member) or deferred != set(DEFERRED_XI):
        raise ValueError("accepted/deferred family inventory differs")
    if any(abs(member) in {4114, 4214, 4224} and
           abs(destination_by_member[member]) == 4122 for member in destination_by_member):
        raise ValueError("forbidden Sigma-to-Lambda family membership")
    return FamilyMap(actual, PARTICLE_DATA_SHA256, destination_by_member,
                     members_by_destination, family_by_destination,
                     frozenset(deferred), frozenset(inventory_pdgs))


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
