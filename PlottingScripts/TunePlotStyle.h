#ifndef HADRONIZATION_TUNE_PLOT_STYLE_H
#define HADRONIZATION_TUNE_PLOT_STYLE_H

#include <string>

#include "Rtypes.h"
#include "TColor.h"

namespace HadronizationPlotStyle {

inline bool IsKnownTune(const std::string& tune)
{
  return tune == "MONASH" || tune == "JUNCTIONS" || tune == "CLOSEPACKING";
}

inline Color_t TuneColor(const std::string& tune)
{
  if (tune == "MONASH") return kBlack;
  if (tune == "JUNCTIONS") return kBlue + 1;
  if (tune == "CLOSEPACKING") return kMagenta + 1;
  return kGray + 2;
}

inline Style_t TuneMarker(const std::string& tune)
{
  if (tune == "MONASH") return 20;
  if (tune == "JUNCTIONS") return 21;
  if (tune == "CLOSEPACKING") return 22;
  return 24;
}

inline Style_t TuneLineStyle(const std::string& tune)
{
  if (tune == "MONASH") return 1;
  if (tune == "JUNCTIONS") return 2;
  if (tune == "CLOSEPACKING") return 7;
  return 1;
}

template <typename T>
inline void ApplyTuneLineAndMarker(T* object,
                                   const std::string& tune,
                                   bool applyTuneLineStyle = true)
{
  if (!object) return;
  object->SetLineColor(TuneColor(tune));
  object->SetMarkerColor(TuneColor(tune));
  object->SetMarkerStyle(TuneMarker(tune));
  if (applyTuneLineStyle) object->SetLineStyle(TuneLineStyle(tune));
}

template <typename T>
inline void ApplyTuneFill(T* object, const std::string& tune, Style_t fillStyle = 0)
{
  if (!object) return;
  object->SetFillColor(TuneColor(tune));
  object->SetFillStyle(fillStyle);
}

} // namespace HadronizationPlotStyle

#endif
