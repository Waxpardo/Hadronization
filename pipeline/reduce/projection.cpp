#include "projection.hpp"
#include "../query/selection.hpp"

#include "TFile.h"
#include "TKey.h"
#include "TList.h"
#include "TObjString.h"
#include "TTree.h"

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <tuple>
#include <utility>
#include <vector>

namespace HP = Hadronization::Projection;
namespace HR = Hadronization::Reduction;

namespace {

double UniformEdge(const HP::Axis& axis, int bin) {
  if (bin == axis.bins) return axis.high;
  const double width = (axis.high - axis.low) / static_cast<double>(axis.bins);
  // Canonical export edges retain the accepted single-rounding arithmetic
  // independently of whether a compiler contracts an implicit multiply-add.
  return std::fma(width, static_cast<double>(bin), axis.low);
}

std::vector<std::string> Fields(const std::string& line) {
  std::vector<std::string> fields;
  std::size_t first = 0;
  while (true) {
    const auto next = line.find('\t', first);
    fields.push_back(line.substr(first, next - first));
    if (next == std::string::npos) break;
    first = next + 1;
  }
  return fields;
}

int Integer(const std::string& value) {
  std::size_t used = 0;
  const long parsed = std::stol(value, &used);
  if (used != value.size() || parsed < std::numeric_limits<int>::min() ||
      parsed > std::numeric_limits<int>::max()) {
    throw std::runtime_error("integer field is outside its exact domain");
  }
  return static_cast<int>(parsed);
}

double Number(const std::string& value) {
  return HadronizationQuery::ReadFiniteDouble(value);
}

bool Boolean(const std::string& value) {
  if (value == "1") return true;
  if (value == "0") return false;
  throw std::runtime_error("boolean field is not 0 or 1");
}

void Need(const std::vector<std::string>& fields, std::size_t size,
          const std::string& label) {
  if (fields.size() != size) {
    throw std::runtime_error(label + " field count differs");
  }
}

struct Request {
  HP::Domains domains;
  std::set<std::string> families;
  std::set<int> paperTriggers;
  std::set<int> baryonMesonTriggers;
  std::string referenceTune;
  std::string profileId;
  std::string activityId;
};

Request ReadRequest(const std::string& path) {
  std::ifstream input(path);
  if (!input) throw std::runtime_error("cannot open projection request");
  std::string line;
  if (!std::getline(input, line) || line != "hadronization_plot_engine_request_v2") {
    throw std::runtime_error("projection request framing differs");
  }
  Request request;
  while (std::getline(input, line) && line != "END") {
    const auto field = Fields(line);
    if (field.empty()) throw std::runtime_error("empty projection request record");
    if (field[0] == "PAPER_OUTPUT_ONLY") {
      Need(field, 2, field[0]);
      if (request.domains.paperOutputOnly || field[1] != "1")
        throw std::runtime_error("paper output request differs");
      request.domains.paperOutputOnly = true;
    } else if (field[0] == "FAMILY") {
      Need(field, 2, field[0]);
      if (!request.families.insert(field[1]).second) {
        throw std::runtime_error("duplicate projection family request");
      }
    } else if (field[0] == "PAPER_TRIGGER") {
      Need(field, 2, field[0]);
      if (!request.paperTriggers.insert(Integer(field[1])).second) {
        throw std::runtime_error("duplicate paper trigger request");
      }
    } else if (field[0] == "BARYON_MESON_TRIGGER") {
      Need(field, 2, field[0]);
      if (!request.baryonMesonTriggers.insert(Integer(field[1])).second) {
        throw std::runtime_error("duplicate baryon/meson trigger request");
      }
    } else if (field[0] == "REFERENCE_TUNE") {
      Need(field, 2, field[0]);
      if (!request.referenceTune.empty()) {
        throw std::runtime_error("duplicate reference tune request");
      }
      request.referenceTune = field[1];
    } else if (field[0] == "PAPER_PROFILE") {
      Need(field, 2, field[0]);
      if (!request.profileId.empty()) {
        throw std::runtime_error("duplicate paper profile request");
      }
      request.profileId = field[1];
    } else if (field[0] == "PAPER_ACTIVITY") {
      Need(field, 2, field[0]);
      if (!request.activityId.empty()) {
        throw std::runtime_error("duplicate paper activity request");
      }
      request.activityId = field[1];
    } else if (field[0] == "BLOCK") {
      Need(field, 2, field[0]);
      request.domains.blockIds.push_back(Integer(field[1]));
    } else if (field[0] == "TUNE") {
      Need(field, 2, field[0]);
      request.domains.tunes.push_back(field[1]);
    } else if (field[0] == "TUNE_DESIGN") {
      Need(field, 3, field[0]);
      if (field[2] != "AVAILABLE" && field[2] != "INCOMPLETE_BLOCK_SET" &&
          field[2] != "UNEQUAL_DESIGN_EXPOSURE") {
        throw std::runtime_error("unknown tune design status");
      }
      if (!request.domains.tuneDesignStatus.emplace(field[1], field[2]).second) {
        throw std::runtime_error("duplicate tune design status");
      }
    } else if (field[0] == "PROFILE") {
      Need(field, 2, field[0]);
      request.domains.profiles.push_back(field[1]);
    } else if (field[0] == "ACTIVITY") {
      Need(field, 2, field[0]);
      request.domains.activities.push_back(field[1]);
    } else if (field[0] == "SCOPE") {
      Need(field, 7, field[0]);
      request.domains.scopes.push_back(
          {Integer(field[1]), field[2], field[3], field[4] == "-" ? "" : field[4],
           field[5] == "-" ? "" : field[5], Integer(field[6])});
    } else if (field[0] == "PAIR") {
      Need(field, 8, field[0]);
      request.domains.pairs.push_back(
          {Integer(field[1]), Integer(field[2]), Integer(field[3]),
           Integer(field[4]), Integer(field[5]), Boolean(field[6]), field[7]});
    } else if (field[0] == "TRIGGER") {
      Need(field, 3, field[0]);
      if (Integer(field[1]) != static_cast<int>(request.domains.triggers.size())) {
        throw std::runtime_error("trigger IDs are not canonical");
      }
      request.domains.triggers.push_back(Integer(field[2]));
    } else if (field[0] == "CORRELATION") {
      Need(field, 4, field[0]);
      if (Integer(field[1]) != static_cast<int>(request.domains.correlations.size())) {
        throw std::runtime_error("correlation IDs are not canonical");
      }
      request.domains.correlations.emplace_back(Integer(field[2]), Integer(field[3]));
    } else if (field[0] == "G9") {
      Need(field, 3, field[0]);
      if (Integer(field[1]) != static_cast<int>(request.domains.g9Species.size())) {
        throw std::runtime_error("G9 IDs are not canonical");
      }
      request.domains.g9Species.push_back(Integer(field[2]));
    } else if (field[0] == "CLOSURE_SPECIES") {
      Need(field, 3, field[0]);
      if (Integer(field[1]) != static_cast<int>(request.domains.closureSpecies.size())) {
        throw std::runtime_error("closure-species IDs are not canonical");
      }
      request.domains.closureSpecies.push_back(Integer(field[2]));
    } else if (field[0] == "T1_SPECIES") {
      Need(field, 3, field[0]);
      if (Integer(field[1]) != static_cast<int>(request.domains.t1Species.size())) {
        throw std::runtime_error("T1-species IDs are not canonical");
      }
      request.domains.t1Species.push_back(Integer(field[2]));
    } else if (field[0] == "ORIGIN") {
      Need(field, 3, field[0]);
      if (Integer(field[1]) != static_cast<int>(request.domains.origins.size())) {
        throw std::runtime_error("origin IDs are not canonical");
      }
      request.domains.origins.push_back(field[2]);
    } else if (field[0] == "CLOSURE_CATEGORY") {
      Need(field, 3, field[0]);
      if (Integer(field[1]) !=
          static_cast<int>(request.domains.closureCategories.size())) {
        throw std::runtime_error("closure-category IDs are not canonical");
      }
      request.domains.closureCategories.push_back(field[2]);
    } else if (field[0] == "CLASS") {
      Need(field, 5, field[0]);
      request.domains.classes.push_back({Integer(field[1]), Boolean(field[2]),
                                         Integer(field[3]), Integer(field[4])});
    } else if (field[0] == "BOUNDARY") {
      Need(field, 9, field[0]);
      request.domains.boundaries.push_back(
          {Integer(field[1]), Integer(field[2]), Integer(field[3]),
           Integer(field[4]), Integer(field[5]), Boolean(field[6]),
           Boolean(field[7]), Boolean(field[8])});
    } else if (field[0] == "AXIS") {
      Need(field, 5, field[0]);
      HP::Axis* axis = nullptr;
      if (field[1] == "dphi") axis = &request.domains.dphi;
      if (field[1] == "eta") axis = &request.domains.eta;
      if (field[1] == "phi") axis = &request.domains.phi;
      if (axis == nullptr) throw std::runtime_error("unknown uniform axis");
      axis->bins = Integer(field[2]);
      axis->low = Number(field[3]);
      axis->high = Number(field[4]);
    } else if (field[0] == "PTEDGE") {
      Need(field, 2, field[0]);
      request.domains.pt.edges.push_back(Number(field[1]));
    } else if (field[0] == "ACTIVITY_BINS") {
      Need(field, 2, field[0]);
      request.domains.activityBins = Integer(field[1]);
    } else if (field[0] == "EVENTS") {
      Need(field, 2, field[0]);
      request.domains.events = static_cast<std::uint64_t>(std::stoull(field[1]));
    } else {
      throw std::runtime_error("unknown projection request record: " + field[0]);
    }
  }
  if (line != "END" || request.families.empty() ||
      request.paperTriggers.empty() || request.baryonMesonTriggers.empty() ||
      request.referenceTune.empty() || request.profileId.empty() ||
      request.activityId.empty()) {
    throw std::runtime_error("projection request is incomplete");
  }
  if (std::find(request.domains.profiles.begin(), request.domains.profiles.end(),
                request.profileId) == request.domains.profiles.end() ||
      std::find(request.domains.activities.begin(), request.domains.activities.end(),
                request.activityId) == request.domains.activities.end()) {
    throw std::runtime_error("paper profile/activity is outside compact domains");
  }
  for (const auto& design : request.domains.tuneDesignStatus) {
    if (std::find(request.domains.tunes.begin(), request.domains.tunes.end(),
                  design.first) == request.domains.tunes.end()) {
      throw std::runtime_error("tune design status names an unknown tune");
    }
  }
  return request;
}

HP::Source LoadSource(const std::string& path, HP::Domains domains) {
  TFile file(path.c_str(), "READ");
  if (file.IsZombie()) throw std::runtime_error("cannot open compact ROOT");
  std::set<std::string> keys;
  TIter iterator(file.GetListOfKeys());
  while (const auto* object = iterator()) {
    const auto* key = dynamic_cast<const TKey*>(object);
    if (key == nullptr || key->GetCycle() != 1 ||
        !keys.insert(key->GetName()).second) {
      throw std::runtime_error("compact ROOT has a duplicate key/cycle");
    }
  }
  if (keys != std::set<std::string>({"cells", "event_gram", "metadata", "receipt"})) {
    throw std::runtime_error("compact ROOT exact object set differs");
  }
  auto* cells = dynamic_cast<TTree*>(file.Get("cells"));
  if (cells == nullptr || dynamic_cast<TTree*>(file.Get("event_gram")) == nullptr ||
      dynamic_cast<TObjString*>(file.Get("metadata")) == nullptr ||
      dynamic_cast<TObjString*>(file.Get("receipt")) == nullptr) {
    throw std::runtime_error("compact ROOT object types differ");
  }
  UInt_t projection = 0, scope = 0, block = 0, bin = 0, component = 0;
  Double_t value = 0.0, absolute = 0.0, sumw2 = 0.0;
  ULong64_t fills = 0;
  const std::vector<std::pair<const char*, void*>> branches = {
      {"projection_id", &projection}, {"scope_id", &scope},
      {"block", &block}, {"bin", &bin}, {"component", &component},
      {"value", &value}, {"sumabs", &absolute}, {"row_sumw2", &sumw2},
      {"fills", &fills}};
  for (const auto& branch : branches) {
    if (cells->SetBranchAddress(branch.first, branch.second) < 0) {
      throw std::runtime_error(std::string("compact cell branch missing: ") +
                               branch.first);
    }
  }
  HP::Source source(std::move(domains));
  for (Long64_t entry = 0; entry < cells->GetEntries(); ++entry) {
    if (cells->GetEntry(entry) <= 0) throw std::runtime_error("cannot read compact cell");
    source.AddCell({projection, scope, block, bin, component},
                   {value, absolute, sumw2, fills});
  }
  return source;
}

std::string Float(double value) {
  if (!std::isfinite(value)) return "-";
  std::ostringstream output;
  output << std::hexfloat << value;
  return output.str();
}

std::string Join(const std::vector<std::string>& values) {
  std::ostringstream output;
  for (std::size_t index = 0; index < values.size(); ++index) {
    if (index != 0) output << ',';
    output << values[index];
  }
  return output.str().empty() ? "-" : output.str();
}

std::string Complements(const std::vector<std::vector<double>>& values,
                        std::size_t component) {
  if (values.empty()) return "-";
  std::ostringstream output;
  for (std::size_t index = 0; index < values.size(); ++index) {
    if (index != 0) output << ';';
    output << (component < values[index].size() ? Float(values[index][component]) : "-");
  }
  return output.str();
}

std::string CovarianceRow(const HP::ProjectionResult& projected,
                          std::size_t component,
                          std::size_t first = 0,
                          std::size_t count = 0) {
  const auto& result = projected.estimate;
  const std::size_t dimension = result.center.size();
  if (count == 0) count = dimension;
  if (component >= dimension ||
      first > dimension || count > dimension - first ||
      result.covariance.size() != dimension * dimension ||
      !HP::AvailableUncertainty(
          HP::UncertaintyStatus(projected, component))) return "-";
  std::ostringstream output;
  bool emitted = false;
  for (std::size_t column = first; column < first + count; ++column) {
    if (emitted) output << ';';
    output << (HP::AvailableUncertainty(HP::UncertaintyStatus(projected, column))
                   ? Float(result.covariance[component * dimension + column]) : "-");
    emitted = true;
  }
  return emitted ? output.str() : "-";
}

const HP::ClassDefinition& Class(const HP::Domains& domains, int id) {
  const auto found = std::find_if(domains.classes.begin(), domains.classes.end(),
                                  [&](const auto& value) { return value.id == id; });
  if (found == domains.classes.end()) throw std::runtime_error("class ID is unknown");
  return *found;
}

const HP::Boundary* Boundary(const HP::Domains& domains, const HP::Scope& scope) {
  if (scope.classId < 0 || scope.activity.empty()) return nullptr;
  const auto tune = std::find(domains.tunes.begin(), domains.tunes.end(), scope.tune);
  const auto activity = std::find(domains.activities.begin(), domains.activities.end(),
                                  scope.activity);
  if (tune == domains.tunes.end() || activity == domains.activities.end()) return nullptr;
  const int tuneId = static_cast<int>(tune - domains.tunes.begin());
  const int activityId = static_cast<int>(activity - domains.activities.begin());
  const auto found = std::find_if(domains.boundaries.begin(), domains.boundaries.end(),
                                  [&](const auto& value) {
                                    return value.tuneId == tuneId &&
                                           value.activityId == activityId &&
                                           value.classId == scope.classId;
                                  });
  return found == domains.boundaries.end() ? nullptr : &*found;
}

void Emit(std::ostream& output, const HP::Domains& domains, const HP::Row& row,
          const HP::ProjectionResult& projected, std::size_t index,
          std::size_t covarianceFirst = 0,
          std::size_t covarianceCount = 0) {
  if (domains.paperOutputOnly && row.roleId.empty()) return;
  const auto& result = projected.estimate;
  const auto* boundary = row.classId < 0 ? nullptr : Boundary(
      domains, HP::Scope{-1, "pair", row.tune, row.profile, row.activity, row.classId});
  const auto& klass = row.classId < 0 ? HP::ClassDefinition{} : Class(domains, row.classId);
  const std::string value = index < result.center.size() ? Float(result.center[index]) : "-";
  const std::string error = index < result.standardError.size()
                                ? Float(result.standardError[index]) : "-";
  const std::string variance = index < result.diagonalVariance.size()
                                   ? Float(result.diagonalVariance[index])
                                   : "-";
  const std::string leave = index < result.leaveMean.size()
                                ? Float(result.leaveMean[index]) : "-";
  const std::string referenceLeave = index < projected.referenceLeaveMean.size()
                                         ? Float(projected.referenceLeaveMean[index])
                                         : "-";
  const bool emptyClass = boundary != nullptr && boundary->empty;
  if (emptyClass && (value != "-" || error != "-" || variance != "-")) {
    throw std::runtime_error("empty class carries nonempty numerical output");
  }
  const std::string valueStatus = emptyClass ? "EMPTY_CLASS" : HP::ValueStatus(projected, index);
  const std::string uncertaintyStatus = emptyClass ? "EMPTY_CLASS" : HP::UncertaintyStatus(projected, index);
  output << "D\t" << row.family << '\t' << row.semanticId << '\t'
         << (row.roleId.empty() ? "-" : row.roleId) << '\t' << row.quantity << '\t'
         << row.tune << '\t' << (row.referenceTune.empty() ? "-" : row.referenceTune)
         << '\t' << (row.profile.empty() ? "-" : row.profile) << '\t'
         << (row.activity.empty() ? "-" : row.activity) << '\t' << row.classId
         << '\t' << (row.classId < 0 ? -1 : klass.percentileLow) << '\t'
         << (row.classId < 0 ? -1 : klass.percentileHigh) << '\t'
         << (boundary == nullptr ? -1 : boundary->low) << '\t'
         << (boundary == nullptr ? -1 : boundary->high) << '\t' << row.triggerPdg
         << '\t' << row.associatePdg << '\t' << row.referencePdg << '\t'
         << (row.component.empty() ? "-" : row.component) << '\t'
         << (row.axis.empty() ? "-" : row.axis) << '\t' << row.binIndex << '\t'
         << Float(row.binLow) << '\t' << Float(row.binHigh) << '\t' << value << '\t'
         << valueStatus << '\t' << error << '\t' << uncertaintyStatus
         << '\t' << variance << '\t' << leave << '\t' << referenceLeave << '\t'
         << Complements(result.complements, index) << '\t'
         << Complements(projected.referenceComplements, index) << '\t'
         << Join(HP::Reasons(projected, index)) << '\t'
         << (projected.diagnostic.empty() ? "-" : projected.diagnostic) << '\t'
         << result.policy << '\t'
         << CovarianceRow(projected, index,
                          domains.paperOutputOnly ? index : covarianceFirst,
                          domains.paperOutputOnly ? 1 : covarianceCount)
         << '\n';
  if (!row.roleId.empty()) {
    const auto emitBlocks = [&](const std::string& tune,
                                const std::vector<std::vector<double>>& values) {
      for (std::size_t block = 0; block < values.size(); ++block) {
        output << "B\t" << row.semanticId << '\t' << tune << '\t' << block + 1 << '\t';
        for (std::size_t component = 0; component < values[block].size(); ++component) {
          if (component) output << ';';
          output << Float(values[block][component]);
        }
        output << '\n';
      }
    };
    emitBlocks(row.tune, index < projected.componentBlockInputs.size()
        ? projected.componentBlockInputs[index] : projected.blockInputs);
    if (!row.referenceTune.empty()) {
      emitBlocks(row.referenceTune, index < projected.referenceComponentBlockInputs.size()
          ? projected.referenceComponentBlockInputs[index] : projected.referenceBlockInputs);
    }
    std::vector<std::size_t> auditIndices;
    if (projected.componentDenominatorAuditIndices.empty()) {
      for (std::size_t audit = 0; audit < result.denominatorAudits.size(); ++audit) {
        auditIndices.push_back(audit);
      }
    } else {
      if (index >= projected.componentDenominatorAuditIndices.size()) {
        throw std::runtime_error("component denominator audit domain differs");
      }
      auditIndices = projected.componentDenominatorAuditIndices[index];
    }
    std::set<std::string> auditIds;
    for (const auto auditIndex : auditIndices) {
      if (auditIndex >= result.denominatorAudits.size()) {
        throw std::runtime_error("component denominator audit reference is absent");
      }
      const auto& audit = result.denominatorAudits[auditIndex];
      if (!auditIds.insert(audit.id).second) {
        throw std::runtime_error("duplicate component denominator audit reference");
      }
      std::string status = "AVAILABLE";
      std::array<std::string, 10> leaveStatus;
      leaveStatus.fill("AVAILABLE");
      for (const auto& reason : HP::Reasons(projected, index)) {
        const std::string suffix = ":" + audit.id;
        if (reason.size() >= suffix.size() && reason.compare(reason.size()-suffix.size(), suffix.size(), suffix) == 0) {
          if (reason.rfind("DENOMINATOR_STATISTICALLY_UNRESOLVED:", 0) == 0) status = "UNSTABLE_DENOMINATOR";
          else if (reason.rfind("POOLED_DENOMINATOR", 0) == 0 || reason.rfind("DENOMINATOR_NUMERICALLY_UNRESOLVED:", 0) == 0) status = "UNDEFINED";
        }
        for (int block = 1; block <= 10; ++block) {
          const std::string blockSuffix = suffix + ":" + std::to_string(block);
          if (reason.rfind("LEAVE_DENOMINATOR_", 0) == 0 && reason.size() >= blockSuffix.size() &&
              reason.compare(reason.size()-blockSuffix.size(), blockSuffix.size(), blockSuffix) == 0) {
            leaveStatus[block-1] = "UNDEFINED";
          }
        }
      }
      // A zero primitive denominator is undefined even when algebra cancels it.
      if (audit.pooled == 0.0) status = "UNDEFINED";
      output << "A\t" << row.semanticId << '\t' << audit.id << '\t'
             << int(audit.algebraicallySurvives) << '\t' << Float(audit.pooled) << '\t' << status << '\t';
      for (int block = 0; block < 10; ++block) {
        if (block) output << ';';
        output << leaveStatus[block];
      }
      output << '\n';
    }
  }
}

const HP::Scope& FindScope(const HP::Domains& domains, std::string_view family,
                           std::string_view tune, std::string_view profile = "",
                           std::string_view activity = "", int classId = -1) {
  const auto found = std::find_if(domains.scopes.begin(), domains.scopes.end(),
                                  [family, tune, profile, activity, classId](
                                      const auto& scope) {
    return std::string_view(scope.family) == family && std::string_view(scope.tune) == tune &&
           std::string_view(scope.profile) == profile &&
           std::string_view(scope.activity) == activity && scope.classId == classId;
  });
  if (found == domains.scopes.end()) throw std::runtime_error("requested scope is absent");
  return *found;
}

int TriggerId(const HP::Domains& domains, int pdg) {
  const auto found = std::find(domains.triggers.begin(), domains.triggers.end(), pdg);
  if (found == domains.triggers.end()) throw std::runtime_error("trigger PDG is absent");
  return static_cast<int>(found - domains.triggers.begin());
}

const HP::Pair& Pair(const HP::Domains& domains, int trigger, int associate) {
  const auto found = std::find_if(domains.pairs.begin(), domains.pairs.end(),
                                  [&](const auto& pair) {
    return pair.triggerPdg == trigger && pair.associatePdg == associate;
  });
  if (found == domains.pairs.end()) throw std::runtime_error("ordered pair is absent");
  return *found;
}

std::string Identity(const std::string& quantity, const HP::Scope& scope,
                     int trigger = 0, int associate = 0,
                     const std::string& suffix = {}) {
  std::ostringstream value;
  value << quantity << "/tune=" << scope.tune;
  if (!scope.profile.empty()) value << "/profile=" << scope.profile;
  if (!scope.activity.empty()) value << "/activity=" << scope.activity;
  if (scope.classId >= 0) value << "/class=" << scope.classId;
  if (trigger != 0) value << "/trigger=" << trigger;
  if (associate != 0) value << "/associate=" << associate;
  if (!suffix.empty()) value << '/' << suffix;
  return value.str();
}

HP::ProjectionResult PairYield(const HP::Source& source, const HP::Scope& scope,
                               const HP::Pair& pair) {
  const auto denominator = source.Series(
      3, scope.id, TriggerId(source.Domain(), pair.triggerPdg), 0);
  return HP::Estimate(source.BlockVectors({{2, scope.id, pair.id, 0},
                                           {3, scope.id,
                                            TriggerId(source.Domain(), pair.triggerPdg), 0}}),
                      [](const auto& value) { return HR::Ratio(0, 1, value); },
                      {HP::Denominator("trigger", denominator)},
                      HP::BoundaryReasons(source.Domain(), scope));
}

HP::BlockSeries PairNet(const HP::Source& source, const HP::Scope& scope,
                        const HP::Pair& opposite) {
  const auto& same = Pair(source.Domain(), opposite.triggerPdg,
                          -opposite.associatePdg);
  return HP::Difference(source.Series(2, scope.id, opposite.id, 0),
                        source.Series(2, scope.id, same.id, 0));
}

HP::ProjectionResult Balance(const HP::Source& source, const HP::Scope& scope,
                             const HP::Pair& opposite) {
  const auto& same = Pair(source.Domain(), opposite.triggerPdg,
                          -opposite.associatePdg);
  const int triggerId = TriggerId(source.Domain(), opposite.triggerPdg);
  const auto denominator = source.Series(3, scope.id, triggerId, 0);
  return HP::Estimate(source.BlockVectors({{2, scope.id, opposite.id, 0},
                                           {2, scope.id, same.id, 0},
                                           {3, scope.id, triggerId, 0}}),
                      [](const auto& value) {
                        if (value[2] == 0.0) {
                          return HR::FunctionValue{false, {}, "POOLED_DENOMINATOR_ZERO"};
                        }
                        return HR::FunctionValue{true,
                                                  {(value[0] - value[1]) / value[2]}, {}};
                      }, {HP::Denominator("trigger", denominator)},
                      HP::BoundaryReasons(source.Domain(), scope));
}

HP::ProjectionResult ReferenceRatio(const HP::Source& source,
                                    const HP::Scope& scope,
                                    const HP::Pair& opposite) {
  const auto& same = Pair(source.Domain(), opposite.triggerPdg,
                          -opposite.associatePdg);
  const auto& referenceOs = Pair(source.Domain(), opposite.triggerPdg,
                                 opposite.referencePdg);
  const auto& referenceSs = Pair(source.Domain(), opposite.triggerPdg,
                                 -opposite.referencePdg);
  const auto reference = HP::Difference(
      source.Series(2, scope.id, referenceOs.id, 0),
      source.Series(2, scope.id, referenceSs.id, 0));
  const auto trigger = source.Series(
      3, scope.id, TriggerId(source.Domain(), opposite.triggerPdg), 0);
  return HP::Estimate(
      source.BlockVectors({{2, scope.id, opposite.id, 0},
                           {2, scope.id, same.id, 0},
                           {2, scope.id, referenceOs.id, 0},
                           {2, scope.id, referenceSs.id, 0},
                           {3, scope.id, TriggerId(source.Domain(), opposite.triggerPdg), 0}}),
      [](const auto& value) {
        if (value[2] - value[3] == 0.0) {
          return HR::FunctionValue{false, {}, "POOLED_DENOMINATOR_ZERO"};
        }
        return HR::FunctionValue{true,
                                  {(value[0] - value[1]) / (value[2] - value[3])}, {}};
      }, {HP::Denominator("shared_trigger", trigger, false),
          HP::Denominator("reference_os_minus_ss", reference)},
      HP::BoundaryReasons(source.Domain(), scope));
}

HP::ProjectionResult NestedReferenceRatio(const HP::Source& source,
                                          const HP::Scope& scope,
                                          const HP::Scope& referenceScope,
                                          const HP::Pair& opposite) {
  const auto& domains = source.Domain();
  const auto& same = Pair(domains, opposite.triggerPdg, -opposite.associatePdg);
  const auto& mesonOs = Pair(domains, opposite.triggerPdg, opposite.referencePdg);
  const auto& mesonSs = Pair(domains, opposite.triggerPdg, -opposite.referencePdg);
  const int trigger = TriggerId(domains, opposite.triggerPdg);
  const auto primitives = [&](const HP::Scope& selected) {
    return source.BlockVectors({{2, selected.id, opposite.id, 0},
                                {2, selected.id, same.id, 0},
                                {2, selected.id, mesonOs.id, 0},
                                {2, selected.id, mesonSs.id, 0},
                                {3, selected.id, trigger, 0}});
  };
  const auto sourceBlocks = primitives(scope);
  const auto referenceBlocks = primitives(referenceScope);
  const auto pool = [](const auto& blocks) {
    std::vector<double> totals(blocks.front().size());
    for (std::size_t component = 0; component < totals.size(); ++component) {
      std::vector<double> column;
      for (const auto& block : blocks) column.push_back(block[component]);
      totals[component] = HR::Sum(column);
    }
    return totals;
  };
  const auto sourcePool = pool(sourceBlocks);
  const auto referencePool = pool(referenceBlocks);
  // R = B_A*M_M/(M_A*B_M). Both triggers and M_M must still exist
  // in the original B/M parents; only M_A and B_M survive as denominators.
  const auto functional = [](const auto& a, const auto& m) {
    if (!HR::FiniteVector(a) || !HR::FiniteVector(m)) {
      return HR::FunctionValue{false, {}, "NONFINITE_INPUT"};
    }
    if (a[4] == 0.0 || m[4] == 0.0 || a[2] - a[3] == 0.0 ||
        m[2] - m[3] == 0.0 || m[0] - m[1] == 0.0) {
      return HR::FunctionValue{false, {}, "POOLED_DENOMINATOR_ZERO"};
    }
    return HR::FunctionValue{true,
        {(a[0] - a[1]) * (m[2] - m[3]) /
         ((a[2] - a[3]) * (m[0] - m[1]))}, {}};
  };
  auto output = HP::Estimate(sourceBlocks, [&](const auto& a) {
    return functional(a, referencePool);
  }, {HP::Denominator("source_shared_trigger",
                       source.Series(3, scope.id, trigger, 0), false),
      HP::Denominator("source_meson_os_minus_ss", PairNet(source, scope, mesonOs))},
     HP::BoundaryReasons(domains, scope));
  const auto reference = HP::Estimate(referenceBlocks, [&](const auto& m) {
    return functional(sourcePool, m);
  }, {HP::Denominator("reference_shared_trigger",
                       source.Series(3, referenceScope.id, trigger, 0), false),
      HP::Denominator("reference_meson_os_minus_ss",
                       PairNet(source, referenceScope, mesonOs), false),
      HP::Denominator("reference_tune_numerator_os_minus_ss",
                       PairNet(source, referenceScope, opposite))},
     HP::BoundaryReasons(domains, referenceScope));
  auto& result = output.estimate;
  const auto& other = reference.estimate;
  output.referenceComplements = other.complements;
  output.referenceLeaveMean = other.leaveMean;
  output.referenceBlockInputs = reference.blockInputs;
  for (const auto& reason : other.reasons) HR::AddReason(result, reason);
  result.denominatorAudits.insert(result.denominatorAudits.end(),
                                  other.denominatorAudits.begin(),
                                  other.denominatorAudits.end());
  result.cancelledParentDiagnostics.insert(result.cancelledParentDiagnostics.end(),
      other.cancelledParentDiagnostics.begin(), other.cancelledParentDiagnostics.end());
  output.diagnostic += ";" + reference.diagnostic +
                       ";exact_two_independent_tune_delete_one_families";
  if (result.center.empty() || other.center.empty()) {
    if (result.valueStatus == "UNAVAILABLE" || !result.center.empty()) {
      result.valueStatus = other.valueStatus;
    }
    result.center.clear();
    result.covariance.clear();
    result.diagonalVariance.clear();
    result.standardError.clear();
    result.uncertaintyStatus = "UNAVAILABLE";
    return output;
  }
  if (other.valueStatus == "UNSTABLE_DENOMINATOR") {
    result.valueStatus = "UNSTABLE_DENOMINATOR";
  }
  if (!HP::AvailableUncertainty(result.uncertaintyStatus) ||
      !HP::AvailableUncertainty(other.uncertaintyStatus)) {
    if (HP::AvailableUncertainty(result.uncertaintyStatus)) {
      result.uncertaintyStatus = other.uncertaintyStatus;
    }
    result.covariance.clear();
    result.diagonalVariance.clear();
    result.standardError.clear();
    return output;
  }
  // Each PooledDeleteOne call centers its own exact nonlinear family and
  // supplies its (K-1)/K contribution. Independent samples add covariances.
  result.covariance[0] += other.covariance[0];
  result.diagonalVariance[0] += other.diagonalVariance[0];
  if (!std::isfinite(result.covariance[0])) {
    HR::AddReason(result, "COVARIANCE_ARITHMETIC_FAILURE");
    result.uncertaintyStatus = "COVARIANCE_ARITHMETIC_FAILURE";
    result.covariance.clear();
    result.diagonalVariance.clear();
    result.standardError.clear();
    return output;
  }
  result.standardError[0] = std::sqrt(result.covariance[0]);
  result.uncertaintyStatus = result.covariance[0] == 0.0
      ? "AVAILABLE_ZERO_DISPERSION" : "AVAILABLE";
  return output;
}

std::string BalanceRole(const HP::Scope& scope, const HP::Pair& pair,
                        bool referenceRatio, const Request& request) {
  if (scope.profile != request.profileId ||
      scope.activity != request.activityId ||
      request.paperTriggers.count(pair.triggerPdg) == 0) return {};
  if (referenceRatio && scope.classId > 0 &&
      request.baryonMesonTriggers.count(pair.triggerPdg) != 0 &&
      (((pair.triggerPdg == 411 || pair.triggerPdg == 421) &&
        pair.associatePdg == -4122 && pair.referencePdg == -pair.triggerPdg) ||
       (pair.triggerPdg == 521 && pair.associatePdg == 5122 && pair.referencePdg == -521))) {
    return "balancing.baryon_meson.activity";
  }
  if (!referenceRatio && scope.classId == 0) {
    if (pair.sector == "charm" &&
        ((pair.triggerPdg != 411 && pair.triggerPdg != 421 &&
          pair.triggerPdg != 4122) ||
         (pair.associatePdg != -411 && pair.associatePdg != -421 &&
          pair.associatePdg != -4122))) {
      return {};
    }
    return "balancing.integrated." + pair.sector;
  }
  if (!referenceRatio) return "balancing.activity." + pair.sector;
  return {};
}

void EmitBalancing(std::ostream& output, const HP::Source& source,
                   const Request& request) {
  const auto& domains = source.Domain();
  for (const auto& scope : domains.scopes) {
    if (scope.family != "pair") continue;
    for (const auto& pair : domains.pairs) {
      const auto yield = PairYield(source, scope, pair);
      HP::Row row{"balancing", Identity("ordered_pair_yield", scope,
                                        pair.triggerPdg, pair.associatePdg), {},
                  "ordered_pair_yield", scope.tune, {}, scope.profile,
                  scope.activity, scope.classId, -1, -1, -1, -1,
                  pair.triggerPdg, pair.associatePdg, pair.referencePdg, {}, {}, -1,
                  std::numeric_limits<double>::quiet_NaN(),
                  std::numeric_limits<double>::quiet_NaN()};
      Emit(output, domains, row, yield, 0);
      if (pair.sign != -1) continue;
      const auto balance = Balance(source, scope, pair);
      row.semanticId = Identity("os_minus_ss_per_trigger", scope, pair.triggerPdg,
                                pair.associatePdg);
      row.roleId = BalanceRole(scope, pair, false, request);
      row.quantity = "os_minus_ss_per_trigger";
      Emit(output, domains, row, balance, 0);
      if (std::abs(pair.associatePdg) == std::abs(pair.referencePdg)) continue;
      const auto ratio = ReferenceRatio(source, scope, pair);
      row.semanticId = Identity("baryon_meson_reference_ratio", scope,
                                pair.triggerPdg, pair.associatePdg,
                                "reference=" + std::to_string(pair.referencePdg));
      row.roleId = BalanceRole(scope, pair, true, request);
      row.quantity = "baryon_meson_reference_ratio";
      Emit(output, domains, row, ratio, 0);
    }
  }
  const std::string& referenceTune = request.referenceTune;
  if (std::find(domains.tunes.begin(), domains.tunes.end(), referenceTune) ==
      domains.tunes.end()) {
    throw std::runtime_error("configured reference tune is absent");
  }
  for (const auto& scope : domains.scopes) {
    if (scope.family != "pair" || scope.tune == referenceTune) continue;
    const auto& referenceScope = FindScope(domains, "pair", referenceTune,
                                           scope.profile, scope.activity,
                                           scope.classId);
    for (const auto& pair : domains.pairs) {
      if (pair.sign != -1) continue;
      const auto absolute = Balance(source, scope, pair);
      const auto reference = Balance(source, referenceScope, pair);
      const auto tuneRatio = HP::IndependentRatio(
          absolute, reference,
          {HP::Denominator("reference_tune_os_minus_ss",
                           PairNet(source, referenceScope, pair))});
      HP::Row row{"balancing",
                  Identity("os_minus_ss_ratio_to_reference_tune", scope,
                           pair.triggerPdg, pair.associatePdg,
                           "reference_tune=" + referenceTune),
                  BalanceRole(scope, pair, false, request),
                  "ratio_to_reference_tune",
                  scope.tune, referenceTune, scope.profile, scope.activity,
                  scope.classId, -1, -1, -1, -1, pair.triggerPdg,
                  pair.associatePdg, pair.referencePdg, {}, {}, -1,
                  std::numeric_limits<double>::quiet_NaN(),
                  std::numeric_limits<double>::quiet_NaN()};
      Emit(output, domains, row, tuneRatio, 0);
      if (std::abs(pair.associatePdg) == std::abs(pair.referencePdg)) continue;
      const auto tuneReferenceRatio = NestedReferenceRatio(
          source, scope, referenceScope, pair);
      row.semanticId = Identity("baryon_meson_ratio_to_reference_tune", scope,
                                pair.triggerPdg, pair.associatePdg,
                                "reference_pdg=" +
                                    std::to_string(pair.referencePdg) +
                                    "/reference_tune=" + referenceTune);
      row.roleId = BalanceRole(scope, pair, true, request);
      row.quantity = "baryon_meson_ratio_to_reference_tune";
      Emit(output, domains, row, tuneReferenceRatio, 0);
    }
  }
}

HP::ProjectionResult Correlation(const HP::Source& source, const HP::Scope& scope,
                                 int correlationId) {
  const auto& domains = source.Domain();
  const int bins = domains.dphi.bins;
  const int trigger = domains.correlations.at(correlationId).first;
  const int triggerId = TriggerId(domains, trigger);
  std::vector<std::tuple<std::uint32_t, std::uint32_t,
                         std::uint32_t, std::uint32_t>> coordinates;
  for (int component = 0; component < 2; ++component) {
    for (int bin = 0; bin < bins; ++bin) {
      coordinates.emplace_back(4, scope.id, correlationId * bins + bin, component);
    }
  }
  coordinates.emplace_back(3, scope.id, triggerId, 0);
  const auto denominator = source.Series(3, scope.id, triggerId, 0);
  auto projected = HP::Estimate(source.BlockVectors(coordinates), [bins](const auto& value) {
    if (value.back() == 0.0) {
      return HR::FunctionValue{false, {}, "POOLED_DENOMINATOR_ZERO"};
    }
    std::vector<double> projected;
    projected.reserve(static_cast<std::size_t>(3 * bins));
    for (int bin = 0; bin < bins; ++bin) projected.push_back(value[bin] / value.back());
    for (int bin = 0; bin < bins; ++bin) {
      projected.push_back(value[bins + bin] / value.back());
    }
    for (int bin = 0; bin < bins; ++bin) {
      projected.push_back((value[bin] - value[bins + bin]) / value.back());
    }
    return HR::FunctionValue{true, projected, {}};
  }, {HP::Denominator("trigger", denominator)},
     HP::BoundaryReasons(source.Domain(), scope));
  // Each angular point needs OS, SS and its dedicated trigger, all additive.
  projected.componentBlockInputs.resize(static_cast<std::size_t>(3 * bins));
  for (int component = 0; component < 3 * bins; ++component) {
    const int bin = component % bins;
    for (const auto& block : projected.blockInputs) {
      projected.componentBlockInputs[component].push_back({block[bin], block[bins + bin], block.back()});
    }
  }
  projected.blockInputs.clear();
  return projected;
}

void EmitCorrelations(std::ostream& output, const HP::Source& source,
                      const Request& request) {
  const auto& domains = source.Domain();
  for (const auto& scope : domains.scopes) {
    if (scope.family != "pair") continue;
    for (std::size_t correlation = 0; correlation < domains.correlations.size();
         ++correlation) {
      const auto result = Correlation(source, scope, static_cast<int>(correlation));
      const auto identity = domains.correlations[correlation];
      const auto& pair = Pair(domains, identity.first, identity.second);
      for (int component = 0; component < 3; ++component) {
        const std::string label = component == 0 ? "OS" :
                                  component == 1 ? "SS" : "OS_MINUS_SS";
        for (int bin = 0; bin < domains.dphi.bins; ++bin) {
          HP::Row row{"correlations",
                      Identity("dphi_" + label, scope, identity.first,
                               identity.second, "bin=" + std::to_string(bin)),
                      scope.profile == request.profileId &&
                              scope.activity == request.activityId &&
                              scope.classId == 0 &&
                              request.paperTriggers.count(identity.first) != 0
                          ? "correlations." + pair.sector
                          : "",
                      "dphi_per_trigger", scope.tune, {}, scope.profile,
                      scope.activity, scope.classId, -1, -1, -1, -1,
                      identity.first, identity.second, 0, label, "dphi", bin,
                      UniformEdge(domains.dphi, bin),
                      UniformEdge(domains.dphi, bin + 1)};
          Emit(output, domains, row, result,
               static_cast<std::size_t>(component * domains.dphi.bins + bin),
               static_cast<std::size_t>(component * domains.dphi.bins),
               static_cast<std::size_t>(domains.dphi.bins));
        }
      }
    }
  }
}

HP::ProjectionResult Normalized(const HP::Source& source, std::uint32_t projection,
                                const HP::Scope& scope, int firstBin, int count) {
  std::vector<std::tuple<std::uint32_t, std::uint32_t,
                         std::uint32_t, std::uint32_t>> coordinates;
  std::vector<HP::BlockSeries> components;
  components.reserve(static_cast<std::size_t>(count));
  for (int bin = 0; bin < count; ++bin) {
    coordinates.emplace_back(projection, scope.id, firstBin + bin, 0);
    components.push_back(source.Series(projection, scope.id, firstBin + bin, 0));
  }
  const auto total = HP::Total(components);
  auto result = HP::Estimate(source.BlockVectors(coordinates),
                      [count](const auto& value) {
                        return HR::Normalized(0, static_cast<std::size_t>(count), value);
                      }, {HP::Denominator("normalization_total", total)},
                      HP::BoundaryReasons(source.Domain(), scope));
  // A normalized bin's additive sufficient inputs are its count and total.
  result.componentBlockInputs.resize(static_cast<std::size_t>(count));
  for (int bin = 0; bin < count; ++bin) {
    for (std::size_t block = 0; block < result.blockInputs.size(); ++block) {
      result.componentBlockInputs[bin].push_back({result.blockInputs[block][bin], total.values[block]});
    }
  }
  result.blockInputs.clear();
  return result;
}

void EmitKinematics(std::ostream& output, const HP::Source& source) {
  const auto& domains = source.Domain();
  const int ptBins = static_cast<int>(domains.pt.edges.size()) + 1;
  const int stride = ptBins + domains.eta.bins + domains.phi.bins;
  for (const auto& tune : domains.tunes) {
    const auto& scope = FindScope(domains, "tune", tune);
    for (std::size_t species = 0; species < domains.g9Species.size(); ++species) {
      for (int axisId = 0; axisId < 3; ++axisId) {
        const std::string axis = axisId == 0 ? "pt" : axisId == 1 ? "eta" : "phi";
        const int count = axisId == 0 ? ptBins :
                          axisId == 1 ? domains.eta.bins : domains.phi.bins;
        const int offset = axisId == 0 ? 0 :
                           axisId == 1 ? ptBins : ptBins + domains.eta.bins;
        const int first = static_cast<int>(species) * stride + offset;
        const auto result = Normalized(source, 9, scope, first, count);
        for (int bin = 0; bin < count; ++bin) {
          double low = std::numeric_limits<double>::quiet_NaN();
          double high = std::numeric_limits<double>::quiet_NaN();
          if (axisId == 0) {
            if (bin == 0) high = domains.pt.edges.front();
            else if (bin + 1 == count) low = domains.pt.edges.back();
            else {
              low = domains.pt.edges[bin - 1];
              high = domains.pt.edges[bin];
            }
          } else {
            const auto& selected = axisId == 1 ? domains.eta : domains.phi;
            low = UniformEdge(selected, bin);
            high = UniformEdge(selected, bin + 1);
          }
          HP::Row row{"kinematics",
                      Identity("g9_normalized_" + axis, scope, 0,
                               domains.g9Species[species], "bin=" + std::to_string(bin)),
                      {},
                      "normalized_distribution", tune, {}, {}, {}, -1, -1, -1,
                      -1, -1, 0, domains.g9Species[species], 0, {}, axis, bin,
                      low, high};
          Emit(output, domains, row, result, static_cast<std::size_t>(bin));
        }
      }
    }
  }
}

void EmitMultiplicity(std::ostream& output, const HP::Source& source,
                      const Request& request) {
  const auto& domains = source.Domain();
  const std::string& referenceTune = request.referenceTune;
  if (std::find(domains.tunes.begin(), domains.tunes.end(), referenceTune) ==
      domains.tunes.end()) {
    throw std::runtime_error("configured reference tune is absent");
  }
  for (const auto& activity : domains.activities) {
    const auto& referenceScope = FindScope(domains, "activity", referenceTune, {}, activity);
    const auto reference = Normalized(source, 1, referenceScope, 0,
                                      domains.activityBins);
    for (const auto& tune : domains.tunes) {
      const auto& scope = FindScope(domains, "activity", tune, {}, activity);
      const auto result = tune == referenceTune
          ? reference : Normalized(source, 1, scope, 0, domains.activityBins);
      for (int bin = 0; bin < domains.activityBins; ++bin) {
        HP::Row row{"multiplicity",
                    Identity("g1_normalized", scope, 0, 0,
                             "bin=" + std::to_string(bin)),
                    activity == request.activityId
                        ? "multiplicity.composite" : "",
                    "normalized_distribution", tune, {}, {},
                    activity, -1, -1, -1, -1, -1, 0, 0, 0, {}, "nch", bin,
                    static_cast<double>(bin), static_cast<double>(bin + 1)};
        Emit(output, domains, row, result, static_cast<std::size_t>(bin));
      }
      if (tune == referenceTune) continue;
      std::vector<HR::DenominatorSeries> referenceBins;
      referenceBins.reserve(static_cast<std::size_t>(domains.activityBins));
      for (int bin = 0; bin < domains.activityBins; ++bin) {
        referenceBins.push_back(HP::Denominator(
            "reference_tune_bin_" + std::to_string(bin),
            source.Series(1, referenceScope.id, bin, 0)));
      }
      const auto ratio = HP::IndependentRatio(result, reference, referenceBins);
      for (int bin = 0; bin < domains.activityBins; ++bin) {
        HP::Row row{"multiplicity",
                    Identity("g1_ratio_to_reference_tune", scope, 0, 0,
                             "reference_tune=" + referenceTune +
                                 "/bin=" + std::to_string(bin)),
                    activity == request.activityId
                        ? "multiplicity.composite" : "",
                    "ratio_to_reference_tune", tune, referenceTune, {}, activity,
                    -1, -1, -1, -1, -1, 0, 0, 0, {}, "nch", bin,
                    static_cast<double>(bin), static_cast<double>(bin + 1)};
        Emit(output, domains, row, ratio, static_cast<std::size_t>(bin));
      }
    }
  }
}

void EmitSampleCounts(std::ostream& output, const HP::Source& source) {
  const auto& domains = source.Domain();
  const std::array<std::string, 3> components = {
      "hadron_count", "charm_plus_anticharm_constituent_count",
      "beauty_plus_antibeauty_constituent_count"};
  for (const auto& tune : domains.tunes) {
    const auto& scope = FindScope(domains, "tune", tune);
    for (std::size_t species = 0; species < domains.t1Species.size(); ++species) {
      std::vector<std::tuple<std::uint32_t, std::uint32_t,
                             std::uint32_t, std::uint32_t>> coordinates;
      for (std::uint32_t component = 0; component < components.size(); ++component) {
        coordinates.emplace_back(10, scope.id, species, component);
      }
      const auto result = HP::Estimate(source.BlockVectors(coordinates),
                                       [](const auto& value) {
                                         return HR::FunctionValue{true, value, {}};
                                       });
      for (std::size_t component = 0; component < components.size(); ++component) {
        HP::Row row{"sample_counts",
                    Identity("t1_" + components[component], scope, 0,
                             domains.t1Species[species]), {}, "exact_t1_count", tune,
                    {}, {}, {}, -1, -1, -1, -1, -1, 0,
                    domains.t1Species[species], 0, components[component], {}, -1,
                    std::numeric_limits<double>::quiet_NaN(),
                    std::numeric_limits<double>::quiet_NaN()};
        Emit(output, domains, row, result, component);
      }
    }
  }
}

HP::ProjectionResult ScalarPerTrigger(const HP::Source& source, int projection,
                                      const HP::Scope& scope, int bin,
                                      int trigger, int component = 0) {
  const int triggerId = TriggerId(source.Domain(), trigger);
  const auto& denominatorScope = FindScope(
      source.Domain(), "pair", scope.tune, scope.profile,
      "charged_light_sector_activity_a15_v1_eta4", 0);
  const auto denominator = source.Series(3, denominatorScope.id, triggerId, 0);
  return HP::Estimate(source.BlockVectors(
                          {{static_cast<std::uint32_t>(projection), scope.id, bin,
                            static_cast<std::uint32_t>(component)},
                           {3, denominatorScope.id, triggerId, 0}}),
                      [](const auto& value) { return HR::Ratio(0, 1, value); },
                      {HP::Denominator("trigger", denominator)});
}

void EmitDiagnostics(std::ostream& output, const HP::Source& source,
                     const std::set<std::string>& families) {
  const auto& domains = source.Domain();
  for (const auto& scope : domains.scopes) {
    if (scope.family != "integrated_profile") continue;
    if (families.count("origin") != 0) {
      for (const auto& pair : domains.pairs) {
        for (std::size_t origin = 0; origin < domains.origins.size(); ++origin) {
          const int bin = pair.id * static_cast<int>(domains.origins.size()) +
                          static_cast<int>(origin);
          const auto result = ScalarPerTrigger(source, 5, scope, bin,
                                               pair.triggerPdg);
          HP::Row row{"origin", Identity("origin_" + domains.origins[origin], scope,
                                         pair.triggerPdg, pair.associatePdg), {},
                      "origin_fraction_per_trigger", scope.tune, {}, scope.profile,
                      {}, -1, -1, -1, -1, -1, pair.triggerPdg, pair.associatePdg,
                      0, domains.origins[origin], {}, -1,
                      std::numeric_limits<double>::quiet_NaN(),
                      std::numeric_limits<double>::quiet_NaN()};
          Emit(output, domains, row, result, 0);
        }
      }
    }
    if (families.count("closure_species") != 0) {
      for (std::size_t trigger = 0; trigger < domains.triggers.size(); ++trigger) {
        for (std::size_t species = 0; species < domains.closureSpecies.size(); ++species) {
          const int bin = static_cast<int>(trigger * domains.closureSpecies.size() +
                                           species);
          const auto result = ScalarPerTrigger(source, 7, scope, bin,
                                               domains.triggers[trigger]);
          HP::Row row{"closure_species",
                      Identity("closure_species", scope, domains.triggers[trigger],
                               domains.closureSpecies[species]), {},
                      "closure_species_per_trigger", scope.tune, {}, scope.profile,
                      {}, -1, -1, -1, -1, -1, domains.triggers[trigger],
                      domains.closureSpecies[species], 0, {}, {}, -1,
                      std::numeric_limits<double>::quiet_NaN(),
                      std::numeric_limits<double>::quiet_NaN()};
          Emit(output, domains, row, result, 0);
        }
      }
    }
    if (families.count("closure_full_visible") != 0) {
      for (std::size_t trigger = 0; trigger < domains.triggers.size(); ++trigger) {
        for (int component = 0; component < 2; ++component) {
          const auto result = ScalarPerTrigger(source, 8, scope,
                                               static_cast<int>(trigger),
                                               domains.triggers[trigger], component);
          const std::string label = component == 0 ? "full" : "visible";
          HP::Row row{"closure_full_visible",
                      Identity("closure_" + label, scope, domains.triggers[trigger]),
                      {}, "closure_per_trigger", scope.tune, {}, scope.profile, {},
                      -1, -1, -1, -1, -1, domains.triggers[trigger], 0, 0, label,
                      {}, -1, std::numeric_limits<double>::quiet_NaN(),
                      std::numeric_limits<double>::quiet_NaN()};
          Emit(output, domains, row, result, 0);
        }
      }
    }
    if (families.count("closure_category_dphi") != 0) {
      for (std::size_t trigger = 0; trigger < domains.triggers.size(); ++trigger) {
        for (std::size_t category = 0; category < domains.closureCategories.size();
             ++category) {
          for (int dphi = 0; dphi < domains.dphi.bins; ++dphi) {
            const int bin = static_cast<int>(
                trigger * domains.closureCategories.size() * domains.dphi.bins +
                category * domains.dphi.bins + dphi);
            const auto result = ScalarPerTrigger(source, 6, scope, bin,
                                                 domains.triggers[trigger]);
            HP::Row row{"closure_category_dphi",
                        Identity("closure_category_" +
                                     domains.closureCategories[category],
                                 scope, domains.triggers[trigger], 0,
                                 "bin=" + std::to_string(dphi)), {},
                        "closure_category_per_trigger", scope.tune, {}, scope.profile,
                        {}, -1, -1, -1, -1, -1, domains.triggers[trigger], 0, 0,
                        domains.closureCategories[category], "dphi", dphi,
                        UniformEdge(domains.dphi, dphi),
                        UniformEdge(domains.dphi, dphi + 1)};
            Emit(output, domains, row, result, 0);
          }
        }
      }
    }
  }
}

void WriteEmbeddedReceipt(const std::string& root, const std::string& output) {
  TFile file(root.c_str(), "READ");
  if (file.IsZombie()) throw std::runtime_error("cannot open compact ROOT");
  const auto* receipt = dynamic_cast<TObjString*>(file.Get("receipt"));
  if (receipt == nullptr) throw std::runtime_error("compact embedded receipt is absent");
  std::ofstream stream(output, std::ios::binary);
  if (!stream) throw std::runtime_error("cannot write embedded receipt readback");
  stream << receipt->GetString().Data();
  stream.flush();
  if (!stream) throw std::runtime_error("cannot flush embedded receipt readback");
}

std::array<double, 10> ReadFamily(const std::string& token) {
  std::array<double, 10> values{};
  std::istringstream input(token);
  std::string item;
  std::size_t index = 0;
  while (std::getline(input, item, ';')) {
    if (index == values.size()) throw std::runtime_error("joint family exceeds K10");
    values[index++] = Number(item);
  }
  if (index != values.size()) throw std::runtime_error("joint family is not K10");
  return values;
}

// Private transport from this C++ emitter, never collaborator CSV authority.
// Requested dense submatrices and ROOT factors use exactly the same operation.
void WriteJoint(const std::string& enginePath, const std::string& requestPath,
                const std::string& rootPath) {
  std::ifstream engine(enginePath);
  std::string line;
  if (!std::getline(engine, line) || line != "hadronization_plot_engine_output_v1") {
    throw std::runtime_error("joint engine framing differs");
  }
  std::map<std::string, HP::JointPoint> points;
  while (std::getline(engine, line) && line != "END") {
    const auto f = Fields(line);
    if (f[0] == "R") { Need(f, 4, "joint role"); continue; }
    if (f[0] == "B" || f[0] == "A") { Need(f, 5, "joint primitive receipt"); continue; }
    Need(f, 35, "joint engine point");
    if (f[0] != "D" || f[33] != HR::kEstimatorPolicy) {
      throw std::runtime_error("joint point type/policy differs");
    }
    HP::JointPoint point;
    point.id = f[2];
    point.valid = HP::AvailableUncertainty(f[25]);
    if (point.valid) {
      if (f[22] == "-" || f[24] == "-" || f[26] == "-") {
        throw std::runtime_error("joint uncertainty lacks center/variance");
      }
      point.complements.emplace(f[5], ReadFamily(f[29]));
      point.means.emplace(f[5], Number(f[27]));
      if (f[6] != "-") {
        if (f[5] == f[6]) throw std::runtime_error("joint reference aliases source");
        point.complements.emplace(f[6], ReadFamily(f[30]));
        point.means.emplace(f[6], Number(f[28]));
      } else if (f[28] != "-" || f[30] != "-") {
        throw std::runtime_error("joint reference family is unbound");
      }
      HP::ValidateJointPoint(point);
      const double actual = HP::JointCovariance(point, point);
      const double expected = Number(f[26]);
      const double error = Number(f[24]);
      const double bound = std::max(1e-30, 1e-12 * std::abs(expected));
      if (std::abs(actual - expected) > bound ||
          std::abs(error * error - expected) > bound) {
        throw std::runtime_error("joint diagonal differs from scientific emitter");
      }
    }
    if (!points.emplace(point.id, point).second) {
      throw std::runtime_error("joint engine point is duplicate");
    }
  }
  if (line != "END") throw std::runtime_error("joint engine completion absent");
  struct Group { std::string id, representation; std::vector<std::string> ids, engineIds; };
  std::vector<Group> groups;
  std::ifstream request(requestPath);
  if (!std::getline(request, line) || line != "hadronization_joint_request_v2") {
    throw std::runtime_error("joint request framing differs");
  }
  std::set<std::string> groupIds;
  while (std::getline(request, line) && line != "END") {
    const auto f = Fields(line);
    if (f[0] == "G") {
      Need(f, 3, "joint group");
      if (!groupIds.insert(f[1]).second ||
          (f[2] != "DENSE" && f[2] != "DELETE_ONE_FACTORS")) {
        throw std::runtime_error("joint group identity/representation differs");
      }
      groups.push_back({f[1], f[2], {}, {}});
    } else if (f[0] == "P" && !groups.empty()) {
      Need(f, 3, "joint requested point");
      auto& group = groups.back();
      if (f[1].empty() || std::find(group.ids.begin(), group.ids.end(), f[1]) != group.ids.end()) {
        throw std::runtime_error("joint requested point is duplicate");
      }
      if (f[2] != "-" && points.count(f[2]) == 0) {
        throw std::runtime_error("joint requested point absent from emitter");
      }
      group.ids.push_back(f[1]); group.engineIds.push_back(f[2]);
    } else throw std::runtime_error("joint request record differs");
  }
  if (line != "END" || groups.empty()) throw std::runtime_error("joint request incomplete");
  TFile root(rootPath.c_str(), "CREATE", "", 505);
  if (root.IsZombie()) throw std::runtime_error("joint ROOT already exists/cannot create");
  std::ofstream out(rootPath + ".tsv", std::ios::binary);
  if (!out) throw std::runtime_error("joint readback cannot be created");
  std::string groupId, pointId, tune;
  UInt_t index = 0, column = 0, block = 0;
  Bool_t valid = false;
  double value = 0.0, mean = 0.0;
  TTree domain("points", "Exact requested point domain and uncertainty mask");
  domain.Branch("group", &groupId); domain.Branch("point", &pointId);
  domain.Branch("index", &index); domain.Branch("valid", &valid);
  TTree factors("delete_one_families", "Aligned independent source families; prefactor 9/10");
  factors.Branch("group", &groupId); factors.Branch("point", &pointId);
  factors.Branch("index", &index); factors.Branch("tune", &tune);
  factors.Branch("block", &block); factors.Branch("complement", &value);
  factors.Branch("leave_mean", &mean);
  TTree dense("covariance", "C++ requested joint covariance with explicit validity");
  dense.Branch("group", &groupId); dense.Branch("row", &index);
  dense.Branch("column", &column); dense.Branch("valid", &valid);
  dense.Branch("value", &value);
  out << "hadronization_joint_result_v2\n";
  for (const auto& group : groups) {
    if (group.ids.empty()) throw std::runtime_error("joint requested group is empty");
    groupId = group.id;
    out << "G\t" << group.id << '\t' << group.representation << '\t' << group.ids.size() << '\n';
    std::vector<HP::JointPoint> selected;
    for (std::size_t i = 0; i < group.ids.size(); ++i) {
      selected.push_back(group.engineIds[i] == "-" ? HP::JointPoint{group.ids[i], false, {}, {}}
                                                   : points.at(group.engineIds[i]));
      const auto& point = selected.back();
      index = static_cast<UInt_t>(i); pointId = group.ids[i]; valid = point.valid;
      domain.Fill();
      out << "P\t" << group.id << '\t' << i << '\t' << pointId << '\t' << int(valid) << '\n';
      for (const auto& family : point.complements) {
        tune = family.first; mean = point.means.at(tune);
        for (block = 1; block <= 10; ++block) {
          value = family.second[block - 1]; factors.Fill();
          out << "F\t" << group.id << '\t' << i << '\t' << tune << '\t' << block
              << '\t' << Float(value) << '\t' << Float(mean) << '\n';
        }
      }
    }
    if (group.representation == "DENSE") {
      for (index = 0; index < selected.size(); ++index) {
        for (column = 0; column < selected.size(); ++column) {
          const double covariance = HP::JointCovariance(selected[index], selected[column]);
          valid = std::isfinite(covariance); value = valid ? covariance : 0.0;
          dense.Fill();
          out << "C\t" << group.id << '\t' << index << '\t' << column << '\t'
              << Float(covariance) << '\n';
        }
      }
    }
  }
  domain.Write(); factors.Write(); dense.Write();
  TObjString policy(HR::kEstimatorPolicy); policy.Write("estimator_policy");
  out << "END\n"; out.flush();
  if (!out) throw std::runtime_error("joint readback flush failed");
  root.Close();
}

void Run(const std::string& root, const std::string& requestPath,
         const std::string& outputPath) {
  Request request = ReadRequest(requestPath);
  HP::Source source = LoadSource(root, std::move(request.domains));
  std::ofstream output(outputPath, std::ios::binary | std::ios::trunc);
  if (!output) throw std::runtime_error("cannot create projection output");
  output << "hadronization_plot_engine_output_v1\n";
  for (const auto& role : HP::NominalRoles(source.Domain())) {
    output << "R\t" << role.id << '\t' << role.family << '\t' << role.selector << '\n';
  }
  for (const auto& boundary : source.Domain().boundaries) {
    const auto& tune = source.Domain().tunes.at(boundary.tuneId);
    const auto& activity = source.Domain().activities.at(boundary.activityId);
    const auto& scope = FindScope(source.Domain(), "activity", tune, {}, activity);
    std::uint64_t events = 0;
    std::vector<double> weights;
    if (!boundary.empty) {
      for (int bin = boundary.low; bin <= boundary.high; ++bin) {
        for (int block : source.Domain().blockIds) {
          const auto cell = source.Cell({1, static_cast<std::uint32_t>(scope.id),
              static_cast<std::uint32_t>(block), static_cast<std::uint32_t>(bin), 0});
          if (std::numeric_limits<std::uint64_t>::max() - events < cell.fills) {
            throw std::runtime_error("class event count overflow");
          }
          events += cell.fills; weights.push_back(cell.value);
        }
      }
    }
    output << "L\t" << tune << '\t' << activity << '\t' << boundary.classId << '\t'
           << Float(HR::Sum(weights)) << '\t' << events << '\t' << boundary.low << '\t' << boundary.high << '\n';
  }
  if (request.families.count("balancing") != 0) {
    EmitBalancing(output, source, request);
  }
  if (request.families.count("correlations") != 0) {
    EmitCorrelations(output, source, request);
  }
  if (request.families.count("kinematics") != 0) EmitKinematics(output, source);
  if (request.families.count("multiplicity") != 0) {
    EmitMultiplicity(output, source, request);
  }
  if (request.families.count("sample_counts") != 0) EmitSampleCounts(output, source);
  EmitDiagnostics(output, source, request.families);
  output << "END\n";
  output.flush();
  if (!output) throw std::runtime_error("cannot flush projection output");
}

}  // namespace

int main(int argc, char** argv) {
  try {
    if (argc == 5 && std::string(argv[1]) == "joint") {
      WriteJoint(argv[2], argv[3], argv[4]);
      return 0;
    }
    if (argc != 4) {
      throw std::runtime_error("usage: plot-engine ROOT REQUEST OUTPUT | "
                               "plot-engine embedded ROOT OUTPUT");
    }
    if (std::string(argv[1]) == "embedded") {
      WriteEmbeddedReceipt(argv[2], argv[3]);
      return 0;
    }
    Run(argv[1], argv[2], argv[3]);
    return 0;
  } catch (const std::exception& error) {
    std::cerr << "ERROR: " << error.what() << '\n';
    return 2;
  }
}
