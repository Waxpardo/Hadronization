import importlib.util
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from helpers import ROOT


def load_submit():
    path = ROOT / "pipeline/generate/submit.py"
    spec = importlib.util.spec_from_file_location("nominal_submit", str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def declared_array(source, name):
    match = re.search(r"{}\{{\{{(.*?)\}}\}};".format(name), source, re.DOTALL)
    if not match:
        raise AssertionError("validator array not found: {}".format(name))
    return re.findall(r'"([^"]+)"', match.group(1))


LEAF_TYPES = {
    "I": "Int_t", "D": "Double_t", "S": "Short_t",
    "l": "ULong64_t", "L": "Long64_t",
}


def leaf_branches(source, owner):
    pattern = (r"{}\.Branch\(\s*\"([^\"]+)\"\s*,"
               r"(?:(?!{}\.Branch).)*?\"[^\"]*/([IDSlL])\"")
    return {
        name: LEAF_TYPES[code]
        for name, code in re.findall(pattern.format(owner, owner), source,
                                     re.DOTALL)
    }


def string_constant(source, name):
    match = re.search(
        r"{}\s*=\s*\"([^\"]+)\"".format(re.escape(name)), source)
    if not match:
        raise AssertionError("generated string constant not found: {}".format(name))
    return match.group(1)


def validator_raw_v7_contract(source):
    scalar_block = re.search(r"scalarTypes\{\{(.*?)\}\};", source, re.DOTALL)
    if not scalar_block:
        raise AssertionError("validator scalar type contract not found")
    event = {
        name: type_name
        for name, type_name in re.findall(
            r'\{"([^"]+)",\s*"([^"]+)"\s*,', scalar_block.group(1))
    }
    scalar_names = set(declared_array(source, "scalarBranches"))
    if set(event) != scalar_names:
        raise AssertionError("validator raw-v7 scalar name/type parity mismatch")
    for name in declared_array(source, "integerVectors"):
        event[name] = "vector<int>"
    for array_name in ("doubleVectors", "finalDoubleVector", "hardDoubleVectors"):
        for name in declared_array(source, array_name):
            event[name] = "vector<double>"

    metadata = {}
    for array_name, type_name in (
            ("metadataStrings", "string"), ("metadataInts", "Int_t"),
            ("metadataUnsigned", "ULong64_t"),
            ("metadataLong", "Long64_t"),
            ("metadataDouble", "Double_t")):
        for name in declared_array(source, array_name):
            metadata[name] = type_name
    return event, metadata


def producer_raw_v7_contract(source, generated_header):
    event_match = re.search(
        r'TTree tree\("tree".*?#undef BRANCH_VECTOR', source, re.DOTALL)
    if not event_match:
        raise AssertionError("producer raw-v7 event declaration not found")
    block = event_match.group(0)
    vector_types = {}
    for type_name, declarations in re.findall(
            r"std::vector<(int|double)>\s+([^;]+);", block, re.DOTALL):
        for declaration in declarations.split(","):
            name = declaration.strip()
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
                raise AssertionError(
                    "producer vector declaration parser rejected {!r}".format(name))
            vector_types[name] = "vector<{}>".format(type_name)

    event = leaf_branches(block, "tree")
    for branch_name, variable in re.findall(
            r'tree\.Branch\(\s*"([^"]+)"\s*,\s*&([A-Za-z_][A-Za-z0-9_]*)\s*\);',
            block):
        if variable not in vector_types:
            raise AssertionError(
                "producer raw-v7 vector type is unknown: {}".format(variable))
        event[branch_name] = vector_types[variable]
    for variable in re.findall(r"BRANCH_VECTOR\(([A-Za-z_][A-Za-z0-9_]*)\);", block):
        if variable not in vector_types:
            raise AssertionError(
                "producer raw-v7 macro vector type is unknown: {}".format(variable))
        event[variable] = vector_types[variable]
    event[string_constant(generated_header, "kRawMultiplicityEta10Branch")] = "Int_t"
    event[string_constant(generated_header, "kRawMultiplicityEta40Branch")] = "Int_t"

    metadata_match = re.search(
        r'TTree metadata\("job_metadata".*?metadata\.Fill\(\);',
        source, re.DOTALL)
    if not metadata_match:
        raise AssertionError("producer raw-v7 metadata declaration not found")
    metadata_block = metadata_match.group(0)
    metadata = leaf_branches(metadata_block, "metadata")
    for branch_name in re.findall(
            r'metadata\.Branch\(\s*"([^"]+)"\s*,\s*&[A-Za-z_][A-Za-z0-9_]*\s*\);',
            metadata_block):
        metadata[branch_name] = "string"
    metadata[string_constant(
        generated_header, "kRawTuneAllowlistSchemaBranch")] = "string"
    metadata[string_constant(
        generated_header, "kRawTuneAllowlistSha256Branch")] = "string"
    return event, metadata


def rendered_string_vector(source, name):
    match = re.search(
        r"const std::vector<std::string>\s+{}\s*=\s*\{{(.*?)\}};".format(
            re.escape(name)), source, re.DOTALL)
    if not match:
        raise AssertionError("rendered fixture vector not found: {}".format(name))
    return re.findall(r'"([^"]+)"', match.group(1))


def fixture_raw_v7_contract(source):
    event_block = source[:source.index('TH1D hMultiplicity')]
    event = leaf_branches(event_block, "tree")
    for variable in ("centralName", "wideName"):
        match = re.search(
            r"const std::string\s+{}\s*=.*?;".format(variable),
            event_block, re.DOTALL)
        if not match:
            raise AssertionError("fixture dynamic branch not found: {}".format(variable))
        choices = re.findall(r'"([^"]+)"', match.group(0))
        event[choices[-1]] = "Int_t"
    for name in rendered_string_vector(source, "integerNames"):
        event[name] = "vector<int>"
    for name in rendered_string_vector(source, "doubleNames"):
        event[name] = "vector<double>"

    metadata = {}
    for vector_name, type_name in (
            ("stringNames", "string"), ("intNames", "Int_t"),
            ("unsignedNames", "ULong64_t"), ("longNames", "Long64_t"),
            ("realNames", "Double_t")):
        for name in rendered_string_vector(source, vector_name):
            metadata[name] = type_name
    return event, metadata


def assert_raw_v7_schema_parity(producer_source, validator_source,
                                fixture_source, generated_header):
    producer = producer_raw_v7_contract(producer_source, generated_header)
    validator = validator_raw_v7_contract(validator_source)
    fixture = fixture_raw_v7_contract(fixture_source)
    if producer != validator or producer != fixture:
        raise AssertionError("producer/validator/fixture raw-v7 schema parity mismatch")
    if len(producer[0]) != 110 or len(producer[1]) != 65:
        raise AssertionError("raw-v7 schema cardinality mismatch")


FIXTURE = r'''
#include "physics.hpp"
#include "sha256.hpp"
#include "study_contract.hpp"
#include "TFile.h"
#include "TH1D.h"
#include "TH1I.h"
#include "TObjString.h"
#include "TTree.h"
#include <algorithm>
#include <array>
#include <cstdint>
#include <iomanip>
#include <locale>
#include <map>
#include <sstream>
#include <string>
#include <vector>

using namespace Hadronization;

int main(int argc, char** argv) {
  if (argc != 3) return 2;
  const std::string mode = argv[2];
  const bool counterMutation = mode.rfind("counter_", 0) == 0;
  const bool resolutionEvents = mode == "valid_resolutions" || counterMutation;
  TFile output(argv[1], "RECREATE");
  TTree tree("tree", "fixture");
  ULong64_t eventId = 0;
  Int_t processCode = 121, hardChannel = 4, nMpi = 1;
  Double_t wrongProcessCode = 121.0, weight = 1.0, pthat = 2.0, hardScale = 2.0;
  Int_t mult10 = 0, mult40 = 0, species[6] = {0,0,0,0,0,0};
  Short_t chargeGrid[kLightGridCells] = {0}, baryonGrid[kLightGridCells] = {0};
  Int_t legacyMultiplicity = 0, legacyProcess = 121, nCharm = 2, nBeauty = 0;
  Int_t nBc = 0, qcSum = 0, qbSum = 0, conservation = 1, origin = 1, match = 1;
  std::map<std::string, std::vector<int>> integerVectors;
  std::map<std::string, std::vector<double>> doubleVectors;
  const std::vector<std::string> integerNames = {@INT_VECTORS@};
  const std::vector<std::string> doubleNames = {@DOUBLE_VECTORS@};
  if (mode != "zero") {
    tree.Branch("event_id", &eventId, "event_id/l");
    if (mode == "wrong_type") tree.Branch("process_code", &wrongProcessCode, "process_code/D");
    else tree.Branch("process_code", &processCode, "process_code/I");
    tree.Branch("hard_channel", &hardChannel, "hard_channel/I");
    tree.Branch("event_weight", &weight, "event_weight/D");
    tree.Branch("pthat", &pthat, "pthat/D");
    tree.Branch("hard_scale", &hardScale, "hard_scale/D");
    tree.Branch("n_mpi", &nMpi, "n_mpi/I");
    const std::string centralName = mode == "layout" ?
        "multiplicity_final_charged_nonheavy_eta10_v1" :
        "multiplicity_primary_charged_eta10_v1";
    const std::string wideName = mode == "layout" ?
        "multiplicity_final_charged_nonheavy_eta40_v1" :
        "multiplicity_primary_charged_eta40_v1";
    tree.Branch(centralName.c_str(), &mult10, (centralName + "/I").c_str());
    tree.Branch(wideName.c_str(), &mult40, (wideName + "/I").c_str());
    tree.Branch("multiplicity_central_by_species", species,
                "multiplicity_central_by_species[6]/I");
    tree.Branch("light_charge3_grid", chargeGrid, "light_charge3_grid[128]/S");
    tree.Branch("light_baryon_grid", baryonGrid, "light_baryon_grid[128]/S");
    tree.Branch("MULTIPLICITY", &legacyMultiplicity, "MULTIPLICITY/I");
    tree.Branch("PROCESSCODE", &legacyProcess, "PROCESSCODE/I");
    tree.Branch("NCHARM", &nCharm, "NCHARM/I");
    tree.Branch("NBEAUTY", &nBeauty, "NBEAUTY/I");
    tree.Branch("NBC", &nBc, "NBC/I");
    tree.Branch("final_heavy_qc_sum", &qcSum, "final_heavy_qc_sum/I");
    tree.Branch("final_heavy_qb_sum", &qbSum, "final_heavy_qb_sum/I");
    tree.Branch("heavy_flavour_conservation_ok", &conservation,
                "heavy_flavour_conservation_ok/I");
    tree.Branch("origin_classification_valid", &origin, "origin_classification_valid/I");
    tree.Branch("primary_all_heavy_match_valid", &match,
                "primary_all_heavy_match_valid/I");
    for (const auto& name : integerNames) {
      if (mode == "missing" && name == "heavyPdg") continue;
      tree.Branch(name.c_str(), &integerVectors[name]);
    }
    for (const auto& name : doubleNames) tree.Branch(name.c_str(), &doubleVectors[name]);
  }

  TH1D hMultiplicity("hMULTIPLICITY", "fixture", 10, -0.5, 9.5);
  TH1D hMultiplicityWide("hMULTIPLICITY_ETA40", "fixture", 10, -0.5, 9.5);
  TH1I hProcess("hPROCESS_CODE", "fixture", 1000, -0.5, 999.5);
  hMultiplicity.Sumw2(); hMultiplicityWide.Sumw2();
  std::uint64_t hardConflictsC = 0, hardConflictsB = 0;
  std::uint64_t hardDemotionsC = 0, hardDemotionsB = 0;
  std::uint64_t multiHeavyC = 0, multiHeavyB = 0;
  std::uint64_t allHeavyConflicts = 0, allHeavyDemotions = 0;
  for (int row = 0; row < 3; ++row) {
    for (auto& item : integerVectors) item.second.clear();
    for (auto& item : doubleVectors) item.second.clear();
    eventId = mode == "duplicate_event" ? EventId(3, 0, 0, 0, 0) :
              EventId(3, 0, 0, 0, static_cast<std::uint64_t>(row));
    const bool beautyEvent = mode != "one_channel" && row == 1;
    processCode = beautyEvent ? 123 : 121;
    hardChannel = beautyEvent ? 5 : 4;
    legacyProcess = processCode;
    pthat = mode == "low_pthat" && row == 0 ? 0.5 : 2.0;
    hardScale = mode == "negative_scale" && row == 0 ? -1.0 : 2.0;
    nMpi = mode == "negative_mpi" && row == 0 ? -1 : 1;
    mult10 = row; mult40 = row;
    if (mode == "central_wide" && row == 1) { mult10 = 2; mult40 = 1; }
    std::fill(std::begin(species), std::end(species), 0);
    species[2] = mult10;
    legacyMultiplicity = row;
    if (mode == "central_wide" && row == 1) legacyMultiplicity = mult10;
    const int flavour = hardChannel;
    integerVectors["hard_indices"] = {10, 11};
    integerVectors["hard_bottom_indices"] = {10, 11};
    integerVectors["hard_ids"] = {flavour, -flavour};
    integerVectors["hard_status"] = {-23, -23};
    integerVectors["hard_bottom_ids"] = {flavour, -flavour};
    integerVectors["hard_bottom_status"] = {-23, -23};
    if (mode == "duplicate_root" && row == 0)
      integerVectors["hard_indices"] = {10, 10};
    if (mode == "changed_bottom_valid" && row == 0) {
      integerVectors["hard_bottom_indices"] = {20, 21};
      integerVectors["hard_bottom_ids"] = {421, -421};
      integerVectors["hard_bottom_status"] = {82, 82};
    }
    if (mode == "duplicate_bottom_valid" && row == 0) {
      integerVectors["hard_bottom_indices"] = {30, 30};
      integerVectors["hard_bottom_ids"] = {443, 443};
      integerVectors["hard_bottom_status"] = {82, 82};
    }
    if (mode == "bottom_wrong_sign" && row == 0) {
      integerVectors["hard_bottom_indices"] = {20, 21};
      integerVectors["hard_bottom_ids"] = {-421, 421};
      integerVectors["hard_bottom_status"] = {82, 82};
    }
    if (mode == "bottom_no_constituent" && row == 0) {
      integerVectors["hard_bottom_indices"] = {20, 20};
      integerVectors["hard_bottom_ids"] = {511, 511};
      integerVectors["hard_bottom_status"] = {82, 82};
    }
    if (mode == "bottom_no_audit" && row == 0) {
      integerVectors["hard_bottom_indices"].front() = 999;
      integerVectors["hard_bottom_ids"].front() = 990001;
      integerVectors["hard_bottom_status"].front() = 82;
    }
    for (const std::string name : {"hard_px", "hard_py", "hard_pz"})
      doubleVectors[name] = {0.0, 0.0};
    doubleVectors["hard_e"] = {2.0, 2.0};
    if (mode == "hard_lengths" && row == 0)
      integerVectors["hard_status"].pop_back();
    integerVectors["ancestryIndex"] = {10, 11};
    integerVectors["ancestryPdg"] = {flavour, -flavour};
    integerVectors["ancestryStatus"] = {-23, -23};
    integerVectors["ancestryMother1"] = {0, 0};
    integerVectors["ancestryMother2"] = {0, 0};
    integerVectors["ancestryMotherOffsets"] = {0, 0, 0};
    if (mode == "ancestry_offsets" && row == 0)
      integerVectors["ancestryMotherOffsets"].back() = 1;
    std::vector<int> heavyPdgs = beautyEvent
        ? std::vector<int>{511, -511}
        : std::vector<int>{421, -421};
    if (resolutionEvents && row == 0)
      heavyPdgs = {421, 421, -4422};
    if (resolutionEvents && row == 1)
      heavyPdgs = {511, 511, -511, -511, 5522, -5522};
    integerVectors["heavyMotherOffsets"] = {0};
    integerVectors["heavyConstituentOffsets"] = {0};
    if (mode != "empty_heavy") {
      for (std::size_t slot = 0; slot < heavyPdgs.size(); ++slot) {
        const int heavyPdg = heavyPdgs[slot];
        const auto* state = FindSelectedState(heavyPdg);
        const bool isMesonValue = state ? state->kind == "meson" : false;
        const bool isBaryonValue = state ? state->kind == "baryon" : true;
        const auto content = DecodeHeavyContent(
            heavyPdg, isMesonValue, isBaryonValue);
        const int signedFlavour = content.qc() != 0
            ? (content.qc() > 0 ? 4 : -4)
            : (content.qb() > 0 ? 5 : -5);
        const int hardIndex = signedFlavour > 0 ? 10 : 11;
        const int charge3Value = state ? state->charge3
            : (std::abs(heavyPdg) == 4422 ? (heavyPdg > 0 ? 6 : -6) : 0);
        const int spinTypeValue = state ? state->spin2j1 : 2;
        integerVectors["ID"].push_back(heavyPdg);
        integerVectors["HFCLASS"].push_back(
            content.hasCharm() && content.hasBeauty() ? 45
                : (content.hasBeauty() ? 5 : 4));
        integerVectors["STATUS"].push_back(82);
        integerVectors["MOTHER"].push_back(hardIndex);
        integerVectors["MOTHERID"].push_back(signedFlavour);
        doubleVectors["PT"].push_back(0.0);
        doubleVectors["ETA"].push_back(0.0);
        doubleVectors["Y"].push_back(0.0);
        doubleVectors["PHI"].push_back(0.0);
        doubleVectors["CHARGE"].push_back(charge3Value / 3.0);
        integerVectors["heavyIndex"].push_back(20 + static_cast<int>(slot));
        integerVectors["heavyPdg"].push_back(heavyPdg);
        integerVectors["heavyStatus"].push_back(82);
        integerVectors["heavyStatusAbs"].push_back(82);
        integerVectors["heavyIsFinal"].push_back(1);
        integerVectors["heavyIsMeson"].push_back(isMesonValue ? 1 : 0);
        integerVectors["heavyIsBaryon"].push_back(isBaryonValue ? 1 : 0);
        integerVectors["heavyCharge3"].push_back(charge3Value);
        integerVectors["heavySpinType"].push_back(spinTypeValue);
        integerVectors["heavyMother1"].push_back(hardIndex);
        integerVectors["heavyMother2"].push_back(0);
        integerVectors["heavyDaughter1"].push_back(0);
        integerVectors["heavyDaughter2"].push_back(0);
        integerVectors["heavyMothers"].push_back(hardIndex);
        integerVectors["heavyMotherOffsets"].push_back(
            static_cast<int>(integerVectors["heavyMothers"].size()));
        integerVectors["heavyNc"].push_back(content.nc);
        integerVectors["heavyNcbar"].push_back(content.ncbar);
        integerVectors["heavyNb"].push_back(content.nb);
        integerVectors["heavyNbbar"].push_back(content.nbbar);
        integerVectors["heavyQc"].push_back(content.qc());
        integerVectors["heavyQb"].push_back(content.qb());
        integerVectors["heavyBaryonNumber"].push_back(
            isBaryonValue ? (heavyPdg > 0 ? 1 : -1) : 0);
        integerVectors["heavyStrangeness"].push_back(content.strangeness());
        integerVectors["heavyCentral"].push_back(state ? 1 : 0);
        integerVectors["heavyOpen"].push_back(
            (content.qc() != 0 || content.qb() != 0) ? 1 : 0);
        integerVectors["heavyHidden"].push_back(
            (content.hiddenCharm() || content.hiddenBeauty()) ? 1 : 0);
        integerVectors["heavyStateCategory"].push_back(static_cast<int>(
            ClassifyHeavyStateDetailed(state != nullptr, content,
                                       isMesonValue, spinTypeValue)));
        integerVectors["heavyOriginC"].push_back(content.qc() == 0 ? 0 : 1);
        integerVectors["heavyOriginB"].push_back(content.qb() == 0 ? 0 : 1);
        integerVectors["heavyMatchResolutionC"].push_back(content.qc() == 0 ? 0 : 1);
        integerVectors["heavyMatchResolutionB"].push_back(content.qb() == 0 ? 0 : 1);
        integerVectors["heavyMatchedHardC"].push_back(content.qc() == 0 ? -1 : hardIndex);
        integerVectors["heavyMatchedHardB"].push_back(content.qb() == 0 ? -1 : hardIndex);
        integerVectors["heavyRejectedHardC"].push_back(-1);
        integerVectors["heavyRejectedHardB"].push_back(-1);
        integerVectors["heavyOriginDepthC"].push_back(content.qc() == 0 ? -1 : 1);
        integerVectors["heavyOriginDepthB"].push_back(content.qb() == 0 ? -1 : 1);
        const std::array<std::pair<int, int>, 4> constituents{{
            {4, content.nc}, {-4, content.ncbar},
            {5, content.nb}, {-5, content.nbbar}}};
        for (const auto& constituent : constituents) {
          for (int ordinal = 0; ordinal < constituent.second; ++ordinal) {
            integerVectors["heavyConstituentParentSlot"].push_back(
                static_cast<int>(slot));
            integerVectors["heavyConstituentPdg"].push_back(constituent.first);
            integerVectors["heavyConstituentOrdinal"].push_back(ordinal);
            integerVectors["heavyConstituentOrigin"].push_back(1);
            integerVectors["heavyConstituentMatchResolution"].push_back(1);
            integerVectors["heavyConstituentMatchedHard"].push_back(hardIndex);
            integerVectors["heavyConstituentRejectedHard"].push_back(-1);
            integerVectors["heavyConstituentOriginDepth"].push_back(1);
          }
        }
        integerVectors["heavyConstituentOffsets"].push_back(
            static_cast<int>(integerVectors["heavyConstituentPdg"].size()));
        for (const std::string name : {"heavyPx", "heavyPy", "heavyPz",
                                       "heavyPt", "heavyEta", "heavyY",
                                       "heavyPhi"})
          doubleVectors[name].push_back(0.0);
        doubleVectors["heavyE"].push_back(1.0);
        doubleVectors["heavyMass"].push_back(1.0);
      }
    }
    const std::vector<int> originalMatchedC = integerVectors["heavyMatchedHardC"];
    const std::vector<int> originalMatchedB = integerVectors["heavyMatchedHardB"];
    const CarrierUniquenessResult charmUniqueness = EnforceUniqueFinalHardCarrier(
        integerVectors["heavyIsFinal"], integerVectors["heavyQc"],
        integerVectors["heavyOriginC"], integerVectors["heavyMatchResolutionC"],
        integerVectors["heavyMatchedHardC"]);
    const CarrierUniquenessResult beautyUniqueness = EnforceUniqueFinalHardCarrier(
        integerVectors["heavyIsFinal"], integerVectors["heavyQb"],
        integerVectors["heavyOriginB"], integerVectors["heavyMatchResolutionB"],
        integerVectors["heavyMatchedHardB"]);
    hardConflictsC += charmUniqueness.conflictGroups;
    hardConflictsB += beautyUniqueness.conflictGroups;
    hardDemotionsC += charmUniqueness.demotedMatches;
    hardDemotionsB += beautyUniqueness.demotedMatches;
    for (std::size_t slot = 0; slot < integerVectors["heavyPdg"].size(); ++slot) {
      if (integerVectors["heavyMatchResolutionC"][slot] ==
          static_cast<int>(MatchResolution::kDuplicateHardCarrier))
        integerVectors["heavyRejectedHardC"][slot] = originalMatchedC[slot];
      if (integerVectors["heavyMatchResolutionB"][slot] ==
          static_cast<int>(MatchResolution::kDuplicateHardCarrier))
        integerVectors["heavyRejectedHardB"][slot] = originalMatchedB[slot];
    }
    multiHeavyC += RejectFinalMultiHeavyCarrier(
        integerVectors["heavyIsFinal"], integerVectors["heavyQc"],
        integerVectors["heavyOriginC"], integerVectors["heavyMatchResolutionC"],
        integerVectors["heavyMatchedHardC"], integerVectors["heavyRejectedHardC"]);
    multiHeavyB += RejectFinalMultiHeavyCarrier(
        integerVectors["heavyIsFinal"], integerVectors["heavyQb"],
        integerVectors["heavyOriginB"], integerVectors["heavyMatchResolutionB"],
        integerVectors["heavyMatchedHardB"], integerVectors["heavyRejectedHardB"]);
    std::vector<int> constituentParentFinal;
    for (const int parent : integerVectors["heavyConstituentParentSlot"])
      constituentParentFinal.push_back(integerVectors["heavyIsFinal"][
          static_cast<std::size_t>(parent)]);
    const CarrierUniquenessResult constituentUniqueness =
        EnforceUniqueFinalConstituentHardCarrier(
            integerVectors["heavyConstituentParentSlot"], constituentParentFinal,
            integerVectors["heavyConstituentPdg"],
            integerVectors["heavyConstituentOrigin"],
            integerVectors["heavyConstituentMatchResolution"],
            integerVectors["heavyConstituentMatchedHard"],
            integerVectors["heavyConstituentRejectedHard"]);
    allHeavyConflicts += constituentUniqueness.conflictGroups;
    allHeavyDemotions += constituentUniqueness.demotedMatches;
    if (mode == "status_finality" && row == 0)
      std::fill(integerVectors["heavyIsFinal"].begin(),
                integerVectors["heavyIsFinal"].end(), 0);
    if (mode == "bad_daughter" && row == 0)
      integerVectors["heavyDaughter1"].front() = 999999;
    if (mode == "vector_lengths" && row == 0)
      doubleVectors["heavyPt"].pop_back();
    if (mode == "constituent_offsets" && row == 0)
      integerVectors["heavyConstituentOffsets"].back() += 1;
    if (mode == "mass_inside_tolerance" && row == 0)
      doubleVectors["heavyE"].front() = 1.0 + 5e-9;
    if (mode == "mass_outside_tolerance" && row == 0)
      doubleVectors["heavyE"].front() = 1.0 + 2e-8;
    if (mode == "component_outside_tolerance" && row == 0)
      doubleVectors["heavyPx"].front() = 1e-5;
    nCharm = 0; nBeauty = 0; nBc = 0; qcSum = 0; qbSum = 0;
    for (std::size_t slot = 0; slot < integerVectors["heavyPdg"].size(); ++slot) {
      const bool hasCharm = integerVectors["heavyNc"][slot] +
          integerVectors["heavyNcbar"][slot] > 0;
      const bool hasBeauty = integerVectors["heavyNb"][slot] +
          integerVectors["heavyNbbar"][slot] > 0;
      if (hasCharm && hasBeauty) ++nBc;
      else if (hasCharm) ++nCharm;
      else if (hasBeauty) ++nBeauty;
      if (integerVectors["heavyIsFinal"][slot] != 0) {
        qcSum += integerVectors["heavyQc"][slot];
        qbSum += integerVectors["heavyQb"][slot];
      }
    }
    if (mode == "false_flag" && row == 1) conservation = 0;
    tree.Fill(); hMultiplicity.Fill(mult10, weight);
    hMultiplicityWide.Fill(mult40, weight); hProcess.Fill(processCode);
  }
  if (mode == "corrupt_sumw2") hMultiplicity.GetSumw2()->SetAt(99.0, 1);
  tree.Write(); hMultiplicity.Write(); hMultiplicityWide.Write(); hProcess.Write();

  TTree stability("heavy_stability_audit", "fixture");
  Int_t pdg = 0, isHadron = 1, isMeson = 1, isBaryon = 0, spinType = 1;
  Int_t charge3 = 0, nHeavyCharm = 1, nHeavyBeauty = 0;
  Int_t nc = 0, ncbar = 0, nb = 0, nbbar = 0, qc = 0, qb = 0;
  Int_t strangeness = 0, openHeavy = 1, hiddenHeavy = 0, central = 1;
  Int_t hasAnti = 1, antiVerified = 1, canDecay = 1, originalMayDecay = 1;
  Int_t finalMayDecay = 0; Double_t mass = 1.0, tau0 = 0.0; std::string particleName;
  stability.Branch("pdg", &pdg, "pdg/I"); stability.Branch("name", &particleName);
  stability.Branch("is_hadron", &isHadron, "is_hadron/I");
  stability.Branch("is_meson", &isMeson, "is_meson/I");
  stability.Branch("is_baryon", &isBaryon, "is_baryon/I");
  stability.Branch("spin_type", &spinType, "spin_type/I");
  stability.Branch("charge3", &charge3, "charge3/I");
  stability.Branch("n_charm", &nHeavyCharm, "n_charm/I");
  stability.Branch("n_beauty", &nHeavyBeauty, "n_beauty/I");
  stability.Branch("n_c", &nc, "n_c/I"); stability.Branch("n_cbar", &ncbar, "n_cbar/I");
  stability.Branch("n_b", &nb, "n_b/I"); stability.Branch("n_bbar", &nbbar, "n_bbar/I");
  stability.Branch("q_c", &qc, "q_c/I"); stability.Branch("q_b", &qb, "q_b/I");
  stability.Branch("strangeness", &strangeness, "strangeness/I");
  stability.Branch("open_heavy", &openHeavy, "open_heavy/I");
  stability.Branch("hidden_heavy", &hiddenHeavy, "hidden_heavy/I");
  stability.Branch("central_registry", &central, "central_registry/I");
  stability.Branch("has_antiparticle", &hasAnti, "has_antiparticle/I");
  stability.Branch("antiparticle_verified", &antiVerified, "antiparticle_verified/I");
  stability.Branch("mass", &mass, "mass/D"); stability.Branch("tau0", &tau0, "tau0/D");
  stability.Branch("can_decay", &canDecay, "can_decay/I");
  stability.Branch("original_may_decay", &originalMayDecay, "original_may_decay/I");
  stability.Branch("final_may_decay", &finalMayDecay, "final_may_decay/I");
  std::ostringstream stabilityText; stabilityText.imbue(std::locale::classic());
  stabilityText << "schema=" << kHeavyStabilityAuditSchema << "\n"
                << std::scientific << std::setprecision(17);
  std::map<int, const SelectedState*> selectedStates;
  for (const auto& state : kSelectedStates) selectedStates.emplace(state.pdg, &state);
  for (const int extra : {-5522, -4422, 443, 4422, 5522})
    selectedStates.emplace(extra, nullptr);
  for (const auto& item : selectedStates) {
    if (mode == "missing_selected_stability" && item.first == 5322) continue;
    const SelectedState* state = item.second;
    pdg = item.first;
    isMeson = state ? (state->kind == "meson" ? 1 : 0) : (pdg == 443 ? 1 : 0);
    isBaryon = isMeson == 0 ? 1 : 0;
    spinType = state ? state->spin2j1 : (pdg == 443 ? 3 : 2);
    charge3 = state ? state->charge3
        : (std::abs(pdg) == 4422 ? (pdg > 0 ? 6 : -6) : 0);
    if (pdg == 411) particleName = "D+";
    else if (pdg == -411) particleName = "D-";
    else if (state) particleName = std::string(state->name);
    else if (pdg == 443) particleName = "J/psi";
    else if (pdg == 4422) particleName = "Xi_cc++";
    else if (pdg == -4422) particleName = "Xi_ccbar--";
    else if (pdg == 5522) particleName = "Xi_bb0";
    else particleName = "Xi_bbbar0";
    if (mode == "empty_audit_name" && pdg == 411) particleName.clear();
    hasAnti = pdg == 443 ? 0 : (mode == "antiparticle_flag" ? 0 : 1);
    if (mode == "selected_quantum_mismatch" && std::abs(pdg) == 5322) {
      spinType = 999;
    }
    const auto content = DecodeHeavyContent(pdg, isMeson != 0, isBaryon != 0);
    nc = content.nc; ncbar = content.ncbar; nb = content.nb; nbbar = content.nbbar;
    qc = content.qc(); qb = content.qb();
    nHeavyCharm = nc + ncbar; nHeavyBeauty = nb + nbbar;
    strangeness = content.strangeness();
    openHeavy = (qc != 0 || qb != 0) ? 1 : 0;
    hiddenHeavy = (content.hiddenCharm() || content.hiddenBeauty()) ? 1 : 0;
    central = state ? 1 : 0;
    stability.Fill();
    stabilityText << pdg << '\t' << std::quoted(particleName) << '\t'
                  << isHadron << '\t' << isMeson << '\t' << isBaryon << '\t'
                  << spinType << '\t' << charge3 << '\t' << nHeavyCharm << '\t'
                  << nHeavyBeauty << '\t' << nc << '\t' << ncbar << '\t' << nb
                  << '\t' << nbbar << '\t' << qc << '\t' << qb << '\t'
                  << strangeness << '\t' << openHeavy << '\t' << hiddenHeavy
                  << '\t' << central << '\t' << hasAnti << '\t' << antiVerified
                  << '\t' << mass << '\t' << tau0 << '\t' << canDecay << '\t'
                  << originalMayDecay << '\t' << finalMayDecay << '\n';
  }
  stability.Write();
  std::string stabilitySha = Sha256Hex(stabilityText.str());
  if (mode == "audit") stabilitySha.assign(64, '0');
  TObjString stabilityCanonical(stabilityText.str().c_str());
  stabilityCanonical.Write("heavy_stability_audit_canonical");
  TObjString stabilityShaObject(stabilitySha.c_str());
  stabilityShaObject.Write("heavy_stability_audit_sha256");

  TTree processes("process_counts", "fixture"); Int_t summaryCode = 121;
  ULong64_t summaryCount = mode == "closure" ? 1 :
      (mode == "one_channel" ? 3 : 2);
  processes.Branch("code", &summaryCode, "code/I");
  processes.Branch("count", &summaryCount, "count/l"); processes.Fill();
  if (mode != "one_channel") {
    summaryCode = 123; summaryCount = 1; processes.Fill();
  }
  processes.Write();

  std::map<std::string, std::string> settingValues;
  if (mode != "minimal_settings") {
    for (const auto name : kAuditedPythiaSettingKeys)
      settingValues[std::string(name)] = "0";
  }
  settingValues["HardQCD:hardbbbar"] = "true";
  settingValues["HardQCD:hardccbar"] = "true";
  settingValues["Main:numberOfEvents"] = "3";
  settingValues["PhaseSpace:pTHatMin"] = "2";
  settingValues["Random:seed"] = "130000001";
  settingValues["Random:setSeed"] = "true";
  if (mode == "missing_audited_setting")
    settingValues.erase(std::string(kAuditedPythiaSettingKeys.front()));
  TTree settings("effective_settings", "fixture"); std::string settingName, settingValue;
  settings.Branch("name", &settingName); settings.Branch("value", &settingValue);
  std::ostringstream settingsText; settingsText.imbue(std::locale::classic());
  settingsText << "schema=" << kEffectiveSettingsSchema << "\n";
  for (const auto& row : settingValues) {
    settingName = row.first; settingValue = row.second; settings.Fill();
    settingsText << std::quoted(settingName) << '\t' << std::quoted(settingValue) << '\n';
  }
  settings.Write(); std::string settingsSha = Sha256Hex(settingsText.str());
  if (mode == "settings_digest") settingsSha.assign(64, '0');
  const std::string settingsCanonicalText = mode == "settings_canonical"
      ? settingsText.str() + "drift\n" : settingsText.str();
  TObjString settingsCanonical(settingsCanonicalText.c_str());
  settingsCanonical.Write("effective_settings_canonical");
  TObjString settingsShaObject(settingsSha.c_str());
  settingsShaObject.Write("effective_settings_sha256");

  TTree metadata("job_metadata", "fixture");
  const std::vector<std::string> stringNames = {@METADATA_STRINGS@};
  const std::vector<std::string> intNames = {@METADATA_INTS@};
  const std::vector<std::string> unsignedNames = {@METADATA_UNSIGNED@};
  const std::vector<std::string> longNames = {@METADATA_LONG@};
  const std::vector<std::string> realNames = {@METADATA_DOUBLE@};
  std::map<std::string, std::string> ms; std::map<std::string, Int_t> mi;
  std::map<std::string, ULong64_t> mu; std::map<std::string, Long64_t> ml;
  std::map<std::string, Double_t> md;
  for (const auto& name : stringNames) metadata.Branch(name.c_str(), &ms[name]);
  for (const auto& name : intNames) metadata.Branch(name.c_str(), &mi[name], (name + "/I").c_str());
  for (const auto& name : unsignedNames) metadata.Branch(name.c_str(), &mu[name], (name + "/l").c_str());
  for (const auto& name : longNames) metadata.Branch(name.c_str(), &ml[name], (name + "/L").c_str());
  for (const auto& name : realNames) metadata.Branch(name.c_str(), &md[name], (name + "/D").c_str());
  ms["campaign"] = "HF_RUN3_V1"; ms["raw_schema"] = "hf_primary_ground_raw_v7";
  ms["selector"] = kSelectorVersion; ms["origin_algorithm"] = kOriginAlgorithmVersion;
  ms["species_registry_schema"] = std::string(kSpeciesRegistrySchema);
  ms["species_registry_sha256"] = std::string(kSpeciesRegistrySha256);
  ms["multiplicity_definition"] = std::string(kMultiplicityDefinitionVersion);
  ms["light_compensation_grid_schema"] = kLightCompensationGridSchema;
  ms["tune_difference_allowlist_schema"] = std::string(kTuneDifferenceAllowlistSchema);
  ms["tune_difference_allowlist_sha256"] = std::string(kTuneDifferenceAllowlistSha256);
  ms["heavy_stability_audit_schema"] = kHeavyStabilityAuditSchema;
  ms["heavy_stability_audit_sha256"] = stabilitySha;
  ms["effective_settings_schema"] = kEffectiveSettingsSchema;
  ms["effective_settings_sha256"] = settingsSha;
  ms["primary_all_heavy_match_schema"] = kPrimaryAllHeavyMatchSchema;
  ms["config_sha256"] = std::string(64, 'a'); ms["executable_sha256"] = std::string(64, 'b');
  ms["repository_commit"] = std::string(40, 'c'); ms["repository_dirty"] = "false";
  ms["root_version"] = "fixture"; ms["pythia_version"] = "8.317";
  ms["tune"] = mode == "identity" ? "JUNCTIONS" : "MONASH"; ms["role"] = "primary";
  ms["host"] = "fixture"; ms["condor_cluster"] = ""; ms["condor_process"] = "";
  mi["campaign_ordinal"] = 3; mi["logical_id"] = 0; mi["attempt"] = 0;
  mi["seed"] = 130000001; mi["complete"] = 1;
  mi["root_compression_settings"] = output.GetCompressionSettings();
  mi["root_compression_algorithm"] = output.GetCompressionAlgorithm();
  mi["root_compression_level"] = output.GetCompressionLevel();
  mu["requested_successes"] = 3; mu["attempts"] = 3;
  mu["successful_events"] = mode == "accounting" ? 2 : 3;
  mu["failed_attempts"] = 0; mu["tree_entries"] = 3;
  mu["effective_settings_entries"] = settingValues.size(); mu["peak_rss_kib"] = 1;
  mu["duplicate_hard_carrier_conflict_groups_charm"] = hardConflictsC;
  mu["duplicate_hard_carrier_conflict_groups_beauty"] = hardConflictsB;
  mu["duplicate_hard_carrier_demotions_charm"] = hardDemotionsC;
  mu["duplicate_hard_carrier_demotions_beauty"] = hardDemotionsB;
  mu["multi_heavy_constituent_rejections_charm"] = multiHeavyC;
  mu["multi_heavy_constituent_rejections_beauty"] = multiHeavyB;
  mu["primary_all_heavy_conflict_groups"] = allHeavyConflicts;
  mu["primary_all_heavy_demotions"] = allHeavyDemotions;
  const std::map<std::string, std::string> wrongCounterSource{
      {"duplicate_hard_carrier_conflict_groups_charm",
       "duplicate_hard_carrier_conflict_groups_beauty"},
      {"duplicate_hard_carrier_conflict_groups_beauty",
       "duplicate_hard_carrier_conflict_groups_charm"},
      {"duplicate_hard_carrier_demotions_charm",
       "duplicate_hard_carrier_demotions_beauty"},
      {"duplicate_hard_carrier_demotions_beauty",
       "duplicate_hard_carrier_demotions_charm"},
      {"multi_heavy_constituent_rejections_charm",
       "multi_heavy_constituent_rejections_beauty"},
      {"multi_heavy_constituent_rejections_beauty",
       "multi_heavy_constituent_rejections_charm"},
      {"primary_all_heavy_conflict_groups", "primary_all_heavy_demotions"},
      {"primary_all_heavy_demotions", "primary_all_heavy_conflict_groups"}};
  for (const auto& counter : wrongCounterSource) {
    const std::string& name = counter.first;
    if (mode == "counter_increment_" + name) ++mu[name];
    if (mode == "counter_decrement_" + name) --mu[name];
    if (mode == "counter_zero_" + name) mu[name] = 0;
    if (mode == "counter_wrong_" + name) mu[name] = mu[counter.second];
  }
  if (mode == "true_failure_counter")
    mu["primary_all_heavy_match_failures"] = 1;
  ml["start_unix_seconds"] = 1; ml["end_unix_seconds"] = 2; ml["elapsed_seconds"] = 1;
  md["sum_weights"] = 3.0; md["sum_weights2"] = 3.0; md["phase_space_pthat_min"] = 2.0;
  md["pythia_sigma_gen_mb"] = 1.0; md["pythia_sigma_err_mb"] = 0.0;
  md["pythia_weight_sum"] = 3.0;
  metadata.Fill(); metadata.Write();
  TObjString changed("fixture"); changed.Write("effective_changed_settings");
  TObjString stats("fixture"); stats.Write("pythia_statistics");
  TObjString centralVersion(kMultiplicityCentral.data());
  centralVersion.Write("multiplicity_central_version");
  TObjString wideVersion(kMultiplicityCrossCheck.data());
  wideVersion.Write("multiplicity_crosscheck_version");
  TObjString definition(kMultiplicityDefinitionVersion.data());
  definition.Write("multiplicity_definition");
  TObjString matchVersion(kPrimaryAllHeavyMatchSchema);
  matchVersion.Write("primary_all_heavy_match_version");
  output.Write(); output.Close(); return 0;
}
'''


class SubmissionContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.submit = load_submit()
        try:
            runtime = cls.submit.runtime_contract.resolve(require_root=True)
        except ValueError as error:
            raise unittest.SkipTest("ROOT unavailable for raw validator fixtures: {}".format(error))
        cls.temporary = tempfile.TemporaryDirectory()
        cls.base = Path(cls.temporary.name)
        cls.validator = cls.base / "validate_raw"
        cls.submit.compile_validator(runtime, cls.validator)
        validator_source = (ROOT / "pipeline/generate/validate_raw.cpp").read_text(encoding="utf-8")
        producer_source = (ROOT / "pipeline/generate/producer.cpp").read_text(encoding="utf-8")
        generated_header = (ROOT / "pipeline/generate/study_contract.hpp").read_text(
            encoding="utf-8")
        replacements = {
            "@INT_VECTORS@": declared_array(validator_source, "integerVectors"),
            "@DOUBLE_VECTORS@": (declared_array(validator_source, "doubleVectors") +
                                  declared_array(validator_source, "finalDoubleVector") +
                                  declared_array(validator_source, "hardDoubleVectors")),
            "@METADATA_STRINGS@": declared_array(validator_source, "metadataStrings"),
            "@METADATA_INTS@": declared_array(validator_source, "metadataInts"),
            "@METADATA_UNSIGNED@": declared_array(validator_source, "metadataUnsigned"),
            "@METADATA_LONG@": declared_array(validator_source, "metadataLong"),
            "@METADATA_DOUBLE@": declared_array(validator_source, "metadataDouble"),
        }
        source = FIXTURE
        for token, values in replacements.items():
            source = source.replace(token, ", ".join(json.dumps(value) for value in values))
        assert_raw_v7_schema_parity(
            producer_source, validator_source, source, generated_header)
        cls.producer_source = producer_source
        cls.validator_source = validator_source
        cls.fixture_source = source
        cls.generated_header = generated_header
        source_path = cls.base / "fixture.cpp"
        source_path.write_text(source, encoding="utf-8")
        cls.fixture = cls.base / "fixture"
        environment = dict(__import__("os").environ)
        environment.update(runtime["environment"])
        root_flags = shlex.split(subprocess.check_output(
            [environment["ROOT_CONFIG"], "--cflags", "--libs"],
            text=True, env=environment))
        flags = []
        for flag in root_flags:
            if flag.startswith("-I"):
                flags.extend(["-isystem", flag[2:]])
            else:
                flags.append(flag)
        command = [environment["CXX"], "-std=c++17", "-Wall", "-Wextra",
                   "-Wpedantic", "-Wconversion", "-Wshadow", "-Werror",
                   str(source_path),
                   "-I" + str(ROOT / "pipeline/generate")] + flags + ["-o", str(cls.fixture)]
        subprocess.run(command, check=True, env=environment,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "temporary"):
            cls.temporary.cleanup()

    def make_and_validate(self, mode):
        output = self.base / "{}.root".format(mode)
        subprocess.run([str(self.fixture), str(output), mode], check=True)
        command = [str(self.validator), str(output), "--campaign", "HF_RUN3_V1",
                   "--tune", "MONASH", "--campaign-ordinal", "3",
                   "--logical-id", "0", "--attempt", "0", "--seed", "130000001",
                   "--events", "3", "--pthat-min", "2", "--config-sha256", "a" * 64,
                   "--executable-sha256", "b" * 64, "--repository-commit", "c" * 40,
                   "--pythia-version", "8.317"]
        return subprocess.run(command, text=True, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT)

    def test_validator_accepts_complete_compact_raw_v7_fixture(self):
        result = self.make_and_validate("valid")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("RAW_VALIDATION_PASS", result.stdout)
        self.assertIn('if (pdg == 411) particleName = "D+";',
                      self.fixture_source)
        self.assertIn('{411, "dplus", "Dplus"', self.generated_header)

    def test_validator_rejects_schema_counterfeits_and_branch_mutations(self):
        diagnostics = {
            "zero": "exact 110-branch",
            "missing": "exact 110-branch",
            "wrong_type": "incorrectly typed event branch process_code",
            "layout": "exact 110-branch",
        }
        for mode, diagnostic in diagnostics.items():
            result = self.make_and_validate(mode)
            self.assertNotEqual(result.returncode, 0, mode)
            self.assertIn(diagnostic, result.stdout, (mode, result.stdout))
        mutated = self.producer_source.replace('"seed/I"', '"seed/D"', 1)
        with self.assertRaisesRegex(
                AssertionError, "producer/validator/fixture raw-v7 schema parity"):
            assert_raw_v7_schema_parity(
                mutated, self.validator_source, self.fixture_source,
                self.generated_header)

    def test_validator_rejects_identity_accounting_event_and_audit_mutations(self):
        diagnostics = {
            "identity": "authorization mismatch",
            "accounting": "exact-success/tree-entry",
            "duplicate_event": "duplicate event ID",
            "false_flag": "false required event validity flag",
            "audit": "heavy-stability tree/canonical digest mismatch",
            "closure": "process accounting",
        }
        for mode, diagnostic in diagnostics.items():
            result = self.make_and_validate(mode)
            self.assertNotEqual(result.returncode, 0, mode)
            self.assertIn(diagnostic, result.stdout, (mode, result.stdout))

    def test_validator_rejects_scientific_false_green_mutations(self):
        diagnostics = {
            "minimal_settings": "omits a generated audited setting",
            "missing_audited_setting": "omits a generated audited setting",
            "settings_canonical": "effective-settings digest/cardinality mismatch",
            "settings_digest": "effective-settings digest/cardinality mismatch",
            "corrupt_sumw2": "bin content/Sumw2 differs",
            "low_pthat": "invalid event pTHat/hard-scale/MPI physics",
            "negative_scale": "invalid event pTHat/hard-scale/MPI physics",
            "negative_mpi": "invalid event pTHat/hard-scale/MPI physics",
            "central_wide": "invalid central/wide multiplicity physics",
            "empty_heavy": "vector lengths or offsets are inconsistent",
            "hard_lengths": "hard vector lengths/exact-pair cardinality",
            "vector_lengths": "vector lengths or offsets are inconsistent",
            "constituent_offsets": "vector lengths or offsets are inconsistent",
            "ancestry_offsets": "vector lengths or offsets are inconsistent",
            "one_channel": "lacks a hard charm or beauty channel",
            "missing_selected_stability": "omits selected signed PDG",
            "status_finality": "heavy finality/daughter invariant failed",
            "bad_daughter": "heavy finality/daughter invariant failed",
            "antiparticle_flag": "heavy-stability selected antiparticle invariant failed",
        }
        for mode, diagnostic in diagnostics.items():
            with self.subTest(mode=mode):
                result = self.make_and_validate(mode)
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn(diagnostic, result.stdout)

    def test_validator_rejects_empty_audit_name_with_consistent_digest(self):
        result = self.make_and_validate("empty_audit_name")
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("empty heavy-stability PYTHIA name", result.stdout)
        self.assertNotIn("tree/canonical digest mismatch", result.stdout)

    def test_validator_rejects_selected_quantum_mismatch_independent_of_name(self):
        result = self.make_and_validate("selected_quantum_mismatch")
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("heavy-stability selected-registry parity failed", result.stdout)
        self.assertNotIn("empty heavy-stability PYTHIA name", result.stdout)

    def test_validator_accepts_changed_and_shared_bottom_copy_endpoints(self):
        for mode in ("changed_bottom_valid", "duplicate_bottom_valid"):
            with self.subTest(mode=mode):
                result = self.make_and_validate(mode)
                self.assertEqual(result.returncode, 0, result.stdout)
                self.assertIn("RAW_VALIDATION_PASS", result.stdout)

    def test_validator_rejects_invalid_changed_bottom_copy_endpoints(self):
        diagnostics = {
            "bottom_wrong_sign": "lacks the required signed heavy constituent",
            "bottom_no_constituent": "lacks the required signed heavy constituent",
            "bottom_no_audit": "is absent from the heavy-stability audit",
        }
        for mode, diagnostic in diagnostics.items():
            with self.subTest(mode=mode):
                result = self.make_and_validate(mode)
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn(diagnostic, result.stdout)

    def test_validator_rejects_duplicate_hard_root_identity(self):
        result = self.make_and_validate("duplicate_root")
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("hard root identity is not unique", result.stdout)

    def test_validator_accepts_mass_roundoff_inside_dedicated_tolerance(self):
        result = self.make_and_validate("mass_inside_tolerance")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("RAW_VALIDATION_PASS", result.stdout)

    def test_validator_rejects_mass_and_component_inconsistency(self):
        diagnostics = {
            "mass_outside_tolerance": "heavy mSave/mCalc inconsistency",
            "component_outside_tolerance": "heavy pT component inconsistency",
        }
        for mode, diagnostic in diagnostics.items():
            with self.subTest(mode=mode):
                result = self.make_and_validate(mode)
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn(diagnostic, result.stdout)

    def test_validator_accepts_exact_nonzero_resolution_counters(self):
        result = self.make_and_validate("valid_resolutions")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("RAW_VALIDATION_PASS", result.stdout)

    @staticmethod
    def resolution_counter_names():
        return (
            "duplicate_hard_carrier_conflict_groups_charm",
            "duplicate_hard_carrier_conflict_groups_beauty",
            "duplicate_hard_carrier_demotions_charm",
            "duplicate_hard_carrier_demotions_beauty",
            "multi_heavy_constituent_rejections_charm",
            "multi_heavy_constituent_rejections_beauty",
            "primary_all_heavy_conflict_groups",
            "primary_all_heavy_demotions",
        )

    def assert_resolution_counter_mutations_rejected(self, operation):
        for name in self.resolution_counter_names():
            with self.subTest(operation=operation, counter=name):
                result = self.make_and_validate(
                    "counter_{}_{}".format(operation, name))
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn("resolution counter mismatch {}".format(name),
                              result.stdout)

    def test_validator_rejects_each_incremented_resolution_counter(self):
        self.assert_resolution_counter_mutations_rejected("increment")

    def test_validator_rejects_each_decremented_resolution_counter(self):
        self.assert_resolution_counter_mutations_rejected("decrement")

    def test_validator_rejects_each_zeroed_resolution_counter(self):
        self.assert_resolution_counter_mutations_rejected("zero")

    def test_validator_rejects_each_wrong_family_resolution_counter(self):
        self.assert_resolution_counter_mutations_rejected("wrong")

    def test_validator_still_rejects_nonzero_true_failure_counter(self):
        result = self.make_and_validate("true_failure_counter")
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("nonzero validity counter primary_all_heavy_match_failures",
                      result.stdout)

    def test_complete_accepted_campaign_is_inventory_not_3000_new_attempts(self):
        campaign, study, tunes = self.submit.campaign_inputs()
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            measured = self.submit.inventory(
                campaign, tunes, ROOT / "data/raw_manifest.jsonl",
                ROOT / "data/attempts.csv", base / "raw", base / "work")
            rows = self.submit.plan_rows(campaign, tunes, measured, "continuation")
            self.assertEqual(rows, [])
            self.assertEqual(set(measured["statuses"].values()), {"accepted_missing_local"})

    def test_campaign_tune_ordinals_are_bijective_with_generated_order(self):
        campaign, study, tunes = self.submit.campaign_inputs()
        mutated = json.loads(json.dumps(campaign))
        mutated["seed"]["tune_ordinals"]["MONASH"] = 2
        with self.assertRaisesRegex(ValueError, "ordinal map.*bijective"):
            self.submit.validate_campaign_tunes(mutated, tunes)
        source = (ROOT / "pipeline/generate/submit.py").read_text(encoding="utf-8")
        producer = (ROOT / "pipeline/generate/producer.cpp").read_text(encoding="utf-8")
        self.assertNotIn("TUNE_MODES", source)
        self.assertIn('tune_map[args.tune]["id"]', source)
        self.assertNotIn('if (tune == "MONASH")', producer)

    def test_accepted_inventory_distinguishes_size_observation_from_sha_verification(self):
        campaign, study, tunes = self.submit.campaign_inputs()
        campaign = dict(campaign)
        campaign["logical_jobs_per_tune"] = 1
        tunes = tunes[:1]
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            raw = base / "raw"
            stable = raw / "MONASH/hf_MONASH_job000.root"
            manifest = base / "manifest.jsonl"
            accepted = {
                "tune": "MONASH", "logical_id": 0,
                "raw_storage_key": "MONASH/hf_MONASH_job000.root",
                "bytes": 4,
                "raw_sha256": self.submit.digest_bytes(b"GOOD"),
            }
            manifest.write_text(
                json.dumps(accepted, sort_keys=True, separators=(",", ":")) + "\n",
                encoding="utf-8")
            attempts = base / "attempts.csv"
            attempts.write_text(
                "tune,logical_id,attempt,seed,outcome,raw_storage_key,evidence_status\n",
                encoding="utf-8")

            missing = self.submit.inventory(
                campaign, tunes, manifest, attempts, raw, base / "work")
            self.assertEqual(missing["statuses"][("MONASH", 0)],
                             "accepted_missing_local")
            stable.parent.mkdir(parents=True)
            stable.write_bytes(b"GOOD")
            observed = self.submit.inventory(
                campaign, tunes, manifest, attempts, raw, base / "work")
            self.assertEqual(observed["statuses"][("MONASH", 0)],
                             "accepted_size_observed_sha256_unverified")
            verified = self.submit.inventory(
                campaign, tunes, manifest, attempts, raw, base / "work", True)
            self.assertEqual(verified["statuses"][("MONASH", 0)],
                             "accepted_sha256_verified")
            stable.write_bytes(b"BAD!")
            wrong_hash = self.submit.inventory(
                campaign, tunes, manifest, attempts, raw, base / "work", True)
            self.assertEqual(wrong_hash["statuses"][("MONASH", 0)],
                             "accepted_sha256_mismatch")
            self.assertRegex(wrong_hash["errors"][0], "SHA-256 mismatch")
            stable.write_bytes(b"BAD")
            wrong_size = self.submit.inventory(
                campaign, tunes, manifest, attempts, raw, base / "work", True)
            self.assertEqual(wrong_size["statuses"][("MONASH", 0)],
                             "accepted_size_or_type_mismatch")
            stable.unlink()
            stable.mkdir()
            wrong_type = self.submit.inventory(
                campaign, tunes, manifest, attempts, raw, base / "work", True)
            self.assertEqual(wrong_type["statuses"][("MONASH", 0)],
                             "accepted_size_or_type_mismatch")

    def test_occupied_unregistered_path_refuses_and_reservation_never_reuses(self):
        campaign, study, tunes = self.submit.campaign_inputs()
        campaign = dict(campaign)
        campaign["logical_jobs_per_tune"] = 1
        tunes = tunes[:1]
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            manifest = base / "manifest.jsonl"
            manifest.write_text("", encoding="utf-8")
            attempts = base / "attempts.csv"
            attempts.write_text("tune,logical_id,attempt,seed,outcome,raw_storage_key,evidence_status\n",
                                encoding="utf-8")
            stable = base / "raw/MONASH/hf_MONASH_job000.root"
            stable.parent.mkdir(parents=True)
            stable.write_bytes(b"occupied")
            measured = self.submit.inventory(campaign, tunes, manifest, attempts,
                                             base / "raw", base / "work")
            with self.assertRaisesRegex(ValueError, "refusing overwrite"):
                self.submit.plan_rows(campaign, tunes, measured, "continuation")
            stable.unlink()
            stable.symlink_to(base / "missing-target.root")
            dangling = self.submit.inventory(campaign, tunes, manifest, attempts,
                                             base / "raw", base / "work")
            with self.assertRaisesRegex(ValueError, "refusing overwrite"):
                self.submit.plan_rows(campaign, tunes, dangling, "continuation")
            stable.unlink()
            measured = self.submit.inventory(campaign, tunes, manifest, attempts,
                                             base / "raw", base / "work")
            first = self.submit.plan_rows(campaign, tunes, measured, "continuation")
            self.assertEqual(first[0]["attempt"], 0)
            self.submit.reserve_rows(campaign, first, base / "work", "d" * 64)
            measured = self.submit.inventory(campaign, tunes, manifest, attempts,
                                             base / "raw", base / "work")
            self.assertEqual(self.submit.plan_rows(campaign, tunes, measured, "continuation"), [])
            row = json.loads((base / "work/evidence/MONASH/job000/attempt00/reservation.json").read_text(
                encoding="utf-8"))
            self.assertEqual((row["attempt"], row["seed"], row["state"]),
                             (0, 130000001, "reserved"))

    def test_preworker_hold_is_durable_and_advances_the_next_attempt(self):
        campaign, study, tunes = self.submit.campaign_inputs()
        campaign = dict(campaign)
        campaign["logical_jobs_per_tune"] = 1
        tunes = tunes[:1]
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            manifest = base / "manifest.jsonl"
            manifest.write_text("", encoding="utf-8")
            attempts = base / "attempts.csv"
            attempts.write_text(
                "tune,logical_id,attempt,seed,outcome,raw_storage_key,evidence_status\n",
                encoding="utf-8")
            measured = self.submit.inventory(campaign, tunes, manifest, attempts,
                                             base / "raw", base / "work")
            row = self.submit.plan_rows(campaign, tunes, measured, "continuation")[0]
            self.submit.reserve_rows(campaign, [row], base / "work", "d" * 64)
            args = type("Args", (), {"tune": "MONASH", "logical_id": 0,
                                     "attempt": 0, "state": "held",
                                     "reason": "periodic CPU hold"})()
            outcome = self.submit.record_preworker_outcome(
                args, base / "work", campaign, tunes)
            recorded = json.loads(outcome.read_text(encoding="utf-8"))
            self.assertEqual((recorded["state"], recorded["seed"], recorded["stage"]),
                             ("held", 130000001, "scheduler_before_worker"))
            measured = self.submit.inventory(campaign, tunes, manifest, attempts,
                                             base / "raw", base / "work")
            next_row = self.submit.plan_rows(campaign, tunes, measured, "continuation")[0]
            self.assertEqual((next_row["attempt"], next_row["seed"]), (1, 130100001))

    def test_evidence_path_payload_transition_and_domain_contracts(self):
        campaign, study, tunes = self.submit.campaign_inputs()
        campaign = dict(campaign)
        campaign["logical_jobs_per_tune"] = 1
        tunes = tunes[:1]

        def reserved(base):
            row = {"tune": "MONASH", "logical_id": 0, "attempt": 0,
                   "seed": 130000001,
                   "storage_key": "MONASH/hf_MONASH_job000.root"}
            path, payload = self.submit.reserve_rows(
                campaign, [row], base / "work", "d" * 64)[0]
            return path, payload

        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            path, payload = reserved(base)
            changed = dict(payload, tune="JUNCTIONS")
            self.submit.atomic_json(path, changed)
            with self.assertRaisesRegex(ValueError, "payload identity.*evidence path"):
                self.submit.evidence_records(base / "work", campaign, tunes)

        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            path, payload = reserved(base)
            duplicate = (base / "work/evidence/ZZZ/job000/attempt00/reservation.json")
            self.submit.atomic_json(duplicate, payload, exclusive=True)
            with self.assertRaisesRegex(ValueError, "duplicate attempt evidence identity"):
                self.submit.evidence_records(base / "work", campaign, tunes)

        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            path, payload = reserved(base)
            outcome = {
                "schema": self.submit.OUTCOME_SCHEMA, "state": "failed",
                "campaign": "HF_RUN3_V1", "tune": "MONASH", "logical_id": 0,
                "attempt": 0, "seed": 130000002,
                "storage_key": payload["storage_key"], "stage": "producer",
                "exit_code": 1, "finished_unix_seconds": 2,
            }
            self.submit.atomic_json(path.with_name("outcome.json"), outcome,
                                    exclusive=True)
            with self.assertRaisesRegex(ValueError, "outcome identity/seed"):
                self.submit.evidence_records(base / "work", campaign, tunes)

        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            path = self.submit.evidence_directory(base / "work", "MONASH", 0, 10)
            payload = {
                "schema": self.submit.RESERVATION_SCHEMA, "state": "reserved",
                "campaign": "HF_RUN3_V1", "purpose": "continuation",
                "tune": "MONASH", "logical_id": 0, "attempt": 10,
                "seed": 131000001,
                "storage_key": "MONASH/hf_MONASH_job000.root",
                "plan_sha256": "d" * 64, "reserved_unix_seconds": 1,
            }
            self.submit.atomic_json(path / "reservation.json", payload,
                                    exclusive=True)
            with self.assertRaisesRegex(ValueError, "outside campaign domain"):
                self.submit.evidence_records(base / "work", campaign, tunes)

    def test_reservation_batch_preflight_prevents_late_partial_collision(self):
        campaign, study, tunes = self.submit.campaign_inputs()
        campaign = dict(campaign)
        campaign["logical_jobs_per_tune"] = 2
        rows = [
            {"tune": "MONASH", "logical_id": logical_id, "attempt": 0,
             "seed": 130000001 + logical_id,
             "storage_key": "MONASH/hf_MONASH_job{:03d}.root".format(logical_id)}
            for logical_id in range(2)]
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory) / "work"
            collision = self.submit.evidence_directory(work, "MONASH", 1, 0)
            collision.mkdir(parents=True)
            (collision / "reservation.json").write_text("occupied", encoding="utf-8")
            with self.assertRaisesRegex(FileExistsError, "destination collision"):
                self.submit.reserve_rows(campaign, rows, work, "d" * 64)
            first = self.submit.evidence_directory(work, "MONASH", 0, 0)
            self.assertFalse((first / "reservation.json").exists())

        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory) / "work"
            row = rows[0]
            reservation = self.submit.evidence_directory(
                work, "MONASH", 0, 0) / "reservation.json"
            original_fsync = self.submit.os.fsync
            failed = [False]

            def fail_first_fsync(descriptor):
                if not failed[0]:
                    failed[0] = True
                    raise OSError("injected file fsync failure")
                return original_fsync(descriptor)

            with mock.patch.object(
                    self.submit.os, "fsync", side_effect=fail_first_fsync):
                with self.assertRaisesRegex(OSError, "injected file fsync failure"):
                    self.submit.reserve_rows(
                        campaign, [row], work, "d" * 64)
            self.assertFalse(reservation.exists())
            self.assertFalse(reservation.is_symlink())

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "reservation.json"
            original = b"pre-existing collision bytes\n"
            path.write_bytes(original)
            with self.assertRaises(FileExistsError):
                self.submit.atomic_json(path, {"state": "reserved"}, exclusive=True)
            self.assertEqual(path.read_bytes(), original)

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            temporary = path.with_name(".{}.{}.tmp".format(
                path.name, self.submit.os.getpid()))
            foreign = b"foreign nonexclusive temporary bytes\n"
            temporary.write_bytes(foreign)
            with self.assertRaises(FileExistsError):
                self.submit.atomic_json(path, {"state": "updated"})
            self.assertFalse(path.exists())
            self.assertEqual(temporary.read_bytes(), foreign)

    def test_promotion_is_no_overwrite_and_receipt_failure_is_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            partial = base / "partial.root"
            partial.write_bytes(b"validated fixture")
            stable = base / "raw/MONASH/hf_MONASH_job000.root"
            receipt = {
                "schema": self.submit.RECEIPT_SCHEMA, "state": "PASS",
                "campaign": "HF_RUN3_V1", "tune": "MONASH",
                "logical_id": 0, "attempt": 0, "seed": 130000001,
                "successful_events": 3, "card_sha256": "a" * 64,
                "effective_card_sha256": "b" * 64,
                "study_definition_sha256": "c" * 64,
                "producer_sha256": "d" * 64, "validator_sha256": "e" * 64,
                "repository_commit": "f" * 40,
                "output_bytes": partial.stat().st_size,
                "output_sha256": self.submit.digest_file(partial),
                "target": "MONASH/hf_MONASH_job000.root",
            }
            receipt_path = base / "evidence/validation_receipt.json"
            outcome_path = base / "evidence/outcome.json"
            with mock.patch.object(self.submit, "atomic_json", side_effect=OSError("disk full")):
                with self.assertRaisesRegex(OSError, "disk full"):
                    self.submit.commit_validated_output(
                        partial, stable, receipt_path, outcome_path, receipt)
            self.assertFalse(stable.exists())
            self.submit.commit_validated_output(
                partial, stable, receipt_path, outcome_path, receipt)
            self.assertEqual(stable.read_bytes(), partial.read_bytes())
            stable.write_bytes(b"accepted namespace")
            with self.assertRaisesRegex(RuntimeError, "refusing overwrite"):
                self.submit.promote_no_overwrite(partial, stable, receipt["output_sha256"])
            self.assertEqual(stable.read_bytes(), b"accepted namespace")
            dangling = base / "raw/MONASH/hf_MONASH_job001.root"
            dangling.symlink_to(base / "missing.root")
            with self.assertRaisesRegex(RuntimeError, "refusing overwrite"):
                self.submit.promote_no_overwrite(
                    partial, dangling, receipt["output_sha256"])

        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            partial = base / "partial.root"
            partial.write_bytes(b"validated fixture")
            stable = base / "raw/MONASH/hf_MONASH_job000.root"
            original_unlink = Path.unlink
            def fail_staging_unlink(path, *args, **kwargs):
                if path.name.endswith(".staging"):
                    raise OSError("staging cleanup injection")
                return original_unlink(path, *args, **kwargs)
            with mock.patch.object(Path, "unlink", fail_staging_unlink):
                self.submit.promote_no_overwrite(
                    partial, stable, self.submit.digest_file(partial))
            self.assertEqual(stable.read_bytes(), partial.read_bytes())
            staging = list(stable.parent.glob(".*.staging"))
            self.assertEqual(len(staging), 1)

    def test_scheduler_contract_and_each_liveness_clause_is_active(self):
        campaign, study, tunes = self.submit.campaign_inputs()
        runtime = self.submit.runtime_contract.resolve()
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            rendered = self.submit.render_submit(
                campaign, study, [], runtime, base / "producer", base / "validator",
                base / "raw", base / "work", "continuation")
        self.assertTrue(self.submit.validate_submit_contract(rendered))
        self.assertTrue(self.submit.validate_submit_executable_contract(
            rendered, base / "producer", base / "validator"))
        disagreement = rendered.decode("utf-8").replace(
            "--producer-path {}".format(base / "producer"),
            "--producer-path {}/wrong".format(base), 1)
        with self.assertRaisesRegex(ValueError, "executable-path contract"):
            self.submit.validate_submit_executable_contract(
                disagreement, base / "producer", base / "validator")
        for clause in ("RemoteUserCpu > 3600", "CurrentTime - EnteredCurrentStatus) > 14400",
                       "on_exit_hold = (ExitBySignal == True) || (ExitCode != 0)",
                       "max_retries = 0"):
            mutated = rendered.decode("utf-8").replace(clause, "REMOVED", 1)
            with self.assertRaisesRegex(ValueError, "Condor safety contract"):
                self.submit.validate_submit_contract(mutated)
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory) / "work"
            producer = Path(directory) / "producer"
            validator = Path(directory) / "validator"
            producer.write_text("fixture", encoding="utf-8")
            validator.write_text("fixture", encoding="utf-8")
            producer.chmod(0o700); validator.chmod(0o700)
            condor = self.submit.submission_filesystem_preflight(
                work, producer, validator)
            self.assertEqual(condor, work / "condor")
            self.assertTrue(condor.is_dir())

    def test_default_generate_contacts_nothing_and_submit_no_work_contacts_nothing(self):
        ordinary = subprocess.run([str(ROOT / "hadronization"), "generate"],
                                  cwd="/tmp", text=True, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
        self.assertEqual(ordinary.returncode, 0, ordinary.stderr)
        self.assertIn("jobs=0", ordinary.stdout)
        submitted = subprocess.run([str(ROOT / "hadronization"), "generate", "--submit"],
                                   cwd="/tmp", text=True, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        self.assertEqual(submitted.returncode, 0, submitted.stderr)
        self.assertIn("scheduler not contacted", submitted.stdout)


if __name__ == "__main__":
    unittest.main()
