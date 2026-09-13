#ifndef HADRONIZATION_QUERY_SPARSE_HPP
#define HADRONIZATION_QUERY_SPARSE_HPP

#include "selection.hpp"
#include "THnSparse.h"
#include "TAxis.h"
#include <map>
#include <set>
#include <vector>

namespace HadronizationQuery {

inline void ClearSparseRanges(THnSparseD& histogram) {
  // Axis ranges are mutable ROOT state and may have been persisted in a file.
  // Start each selection from the complete domain, including all flow bins.
  for (int index=0; index<histogram.GetNdimensions(); ++index)
    histogram.GetAxis(index)->SetRange(0, 0);
}

inline TAxis& SparseAxis(THnSparseD& histogram, const std::string& field) {
  TAxis* result = nullptr;
  for (int index=0; index<histogram.GetNdimensions(); ++index) {
    auto* candidate = histogram.GetAxis(index);
    if (field == candidate->GetName()) {
      if (result != nullptr) throw std::runtime_error("duplicate sparse axis identity");
      result = candidate;
    }
  }
  if (result == nullptr) throw std::runtime_error("missing sparse axis " + field);
  return *result;
}

// Apply the same offline rectangular selection used by conventional ROOT
// analysis macros: set the retained sparse-axis bins before projecting.  The
// threshold must be an exact lower bin edge, so no requested minimum is
// silently rounded to a different physical selection.  High-pT overflow is
// retained because the source domain has no finite physics upper cut.
inline void SelectThreshold(THnSparseD& histogram, const std::string& field,
                            const Threshold& cut) {
  auto& axis = SparseAxis(histogram, field);
  if (axis.GetXmin()!=0.0) throw std::runtime_error("sparse pT physical domain differs");
  int first = 1;
  if (cut.enabled) {
    first = axis.FindFixBin(cut.value);
    if (!cut.inclusive || first<1 || first>axis.GetNbins() ||
        axis.GetBinLowEdge(first)!=cut.value) {
      throw std::runtime_error("pT threshold is not sparse-exact");
    }
  }
  axis.SetRange(first, axis.GetNbins()+1);
}

inline void SelectPhysicalEta(THnSparseD& histogram,
                              const std::string& field, double bound) {
  auto& axis = SparseAxis(histogram, field);
  if (axis.GetXmin()!=-bound || axis.GetXmax()!=bound)
    throw std::runtime_error("inclusive eta boundary is not sparse-exact");
  axis.SetRange(1, axis.GetNbins());
}

// ROOT category-bin numbers are local storage addresses. Resolve each input's
// signed PDG labels before combining primitives; never add category bins by index.
class NaturalSparseRows {
 public:
  NaturalSparseRows(THnSparseD& histogram, const std::vector<std::string>& fields)
      : histogram_(histogram), coordinates_(fields.size()) {
    if (histogram.GetNdimensions()!=static_cast<int>(fields.size()) || !histogram.GetCalculateErrors())
      throw std::runtime_error("sparse dimensions/Sumw2 differ");
    for (std::size_t i=0;i<fields.size();++i) {
      auto* axis=histogram.GetAxis(static_cast<int>(i));
      if (axis->GetName()!=fields[i] || !indices_.emplace(fields[i],i).second)
        throw std::runtime_error("sparse ordered axis identity differs");
      if (fields[i]=="pdg" || fields[i]=="trigger_pdg" || fields[i]=="associate_pdg") {
        std::set<int> unique;
        for (int bin=1;bin<=axis->GetNbins();++bin) {
          const std::string label=axis->GetBinLabel(bin);
          std::size_t consumed=0; int pdg=0;
          try { pdg=std::stoi(label,&consumed); }
          catch (const std::exception&) { throw std::runtime_error("missing/invalid sparse PDG label"); }
          if (consumed!=label.size() || std::to_string(pdg)!=label || pdg==0 || !unique.insert(pdg).second)
            throw std::runtime_error("duplicate/noncanonical sparse PDG label");
          pdgs_[fields[i]][bin]=pdg;
        }
      }
    }
  }
  bool Next() {
    while (++row_ < histogram_.GetNbins()) {
      value=histogram_.GetBinContent(row_,coordinates_.data());
      bool selected=true;
      for (int index=0; index<histogram_.GetNdimensions(); ++index) {
        const auto* axis=histogram_.GetAxis(index);
        if (axis->TestBit(TAxis::kAxisRange) &&
            (coordinates_[index]<axis->GetFirst() ||
             coordinates_[index]>axis->GetLast())) {
          selected=false;
          break;
        }
      }
      if (!selected) continue;
      sumw2=histogram_.GetBinError2(row_);
      if (!std::isfinite(value) || !std::isfinite(sumw2) || sumw2<0)
        throw std::runtime_error("nonfinite sparse primitive");
      return true;
    }
    return false;
  }
  const TAxis& Axis(const std::string& field) const { return *histogram_.GetAxis(indices_.at(field)); }
  int Bin(const std::string& field) const { return coordinates_.at(indices_.at(field)); }
  int Pdg(const std::string& field) const {
    const auto& labels=pdgs_.at(field);const auto found=labels.find(Bin(field));
    if (found==labels.end()) throw std::runtime_error("categorical sparse flow has no natural identity");
    return found->second;
  }
  int Integer(const std::string& field) const {
    const auto& axis=Axis(field); const int bin=Bin(field);
    if (bin<1 || bin>axis.GetNbins()) throw std::runtime_error("integer sparse flow is outside admitted domain");
    const double value=axis.GetBinCenter(bin);
    if (value!=std::floor(value) || axis.GetBinWidth(bin)!=1.0)
      throw std::runtime_error("sparse integer axis differs");
    return static_cast<int>(value);
  }
  bool InPhysicalEta(const std::string& field,double bound) const {
    const auto& axis=Axis(field);
    if (axis.GetXmin()!=-bound || axis.GetXmax()!=bound)
      throw std::runtime_error("inclusive eta boundary is not sparse-exact");
    return Bin(field)>=1 && Bin(field)<=axis.GetNbins();
  }
  bool PassThreshold(const std::string& field,const Threshold& cut) const {
    const auto& axis=Axis(field);
    if (axis.GetXmin()!=0.0) throw std::runtime_error("sparse pT physical domain differs");
    int first=1;
    if (cut.enabled) {
      first=axis.FindFixBin(cut.value);
      if (!cut.inclusive || first<1 || first>axis.GetNbins() || axis.GetBinLowEdge(first)!=cut.value)
        throw std::runtime_error("pT threshold is not sparse-exact");
    }
    return Bin(field)>=first; // Retain true high overflow; reject nonphysical pT<0.
  }
  double value=0.0,sumw2=0.0;
 private:
  THnSparseD& histogram_;
  std::map<std::string,std::size_t> indices_;
  std::map<std::string,std::map<int,int>> pdgs_;
  std::vector<int> coordinates_;
  Long64_t row_=-1;
};

} // namespace HadronizationQuery
#endif
