#ifndef HADRONIZATION_TUNE_PLOT_STYLE_H
#define HADRONIZATION_TUNE_PLOT_STYLE_H

#include <string>

#include "Rtypes.h"
#include "TColor.h"
#include "TStyle.h"

namespace HadronizationPlotStyle {

inline bool IsKnownTune(const std::string& tune)
{
  return tune == "MONASH" || tune == "JUNCTIONS" || tune == "CLOSEPACKING";
}

// Every three-tune figure uses colour and marker for tune identity:
//
//     MONASH        black   + circle   (20)
//     JUNCTIONS     blue    + square   (21)
//     CLOSEPACKING  purple  + triangle (22)
//
// Every tune draws solid. Line style identifies multiplicity classes within a tune.
constexpr Color_t kMonashColour = kBlack;
constexpr Color_t kJunctionsColour = kBlue + 1;
// Violet remains distinct from black and blue in print.
constexpr Color_t kClosepackingColour = kViolet + 1;
constexpr Color_t kUnknownTuneColour = kGray + 2;

constexpr Style_t kMonashMarker = 20;      // filled circle
constexpr Style_t kJunctionsMarker = 21;   // filled square
constexpr Style_t kClosepackingMarker = 22; // filled triangle
constexpr Style_t kUnknownTuneMarker = 24;

// Every tune draws solid. This is a rule, not a default.
constexpr Style_t kTuneLineStyle = 1;

// CLASS IDENTITY INSIDE ONE PANEL (ruling R45, checklist item 1).
//
// A V-EXTREMES panel draws two multiplicity classes at the SAME x position,
// one per associate. Colour and shape are already spent on the tune, so the
// only attribute left is the marker's FILL: the lowest-activity class draws
// the open counterpart of its tune's marker, the highest draws the filled one.
// Shape still reads the tune and fill reads the class, and neither identity
// costs the other.
//
// THE PALETTE IS UNCHANGED (O3). No colour moves and no filled marker moves;
// this derives the open counterpart of the three markers above rather than
// tabulating a second set, so the palette stays the single source. The pairs
// are ROOT's own: 20/24 circle, 21/25 square, 22/26 triangle.
//
// WHY NOT LINE STYLE, which the ladder below already provides. Because that
// ladder never reaches these figures: `MultiplicityClassLineStyle` in
// improvedPlotting_THnSparse.C matches bin names against the prefix "hDPhic"
// and every configured bin is named "hDPhiM<lo>_<hi>", so it returns 1 for
// every bin of every tracked V-configuration and both extreme classes draw
// solid. That is recorded as a found defect, not repaired here: repairing it
// would give eleven line styles to every canvas that draws eleven classes,
// which is a change no checklist item asks for.
constexpr Style_t kMonashOpenMarker = 24;      // open circle
constexpr Style_t kJunctionsOpenMarker = 25;   // open square
constexpr Style_t kClosepackingOpenMarker = 26; // open triangle

inline Style_t OpenTuneMarker(Style_t filledMarker)
{
  if (filledMarker == kMonashMarker) return kMonashOpenMarker;
  if (filledMarker == kJunctionsMarker) return kJunctionsOpenMarker;
  if (filledMarker == kClosepackingMarker) return kClosepackingOpenMarker;
  return filledMarker;
}

inline Color_t TuneColor(const std::string& tune)
{
  if (tune == "MONASH") return kMonashColour;
  if (tune == "JUNCTIONS") return kJunctionsColour;
  if (tune == "CLOSEPACKING") return kClosepackingColour;
  return kUnknownTuneColour;
}

inline Style_t TuneMarker(const std::string& tune)
{
  if (tune == "MONASH") return kMonashMarker;
  if (tune == "JUNCTIONS") return kJunctionsMarker;
  if (tune == "CLOSEPACKING") return kClosepackingMarker;
  return kUnknownTuneMarker;
}

// Keep the existing interface while returning solid for every tune.
inline Style_t TuneLineStyle(const std::string& /*tune*/)
{
  return kTuneLineStyle;
}

// Dense spectra suppress data markers because adjacent markers merge into a ribbon:
//
//     FEW POINTS PER CURVE (balancing family)  -> markers, as mandated
//     DENSE CURVES (fig 4 + the 30 panels)     -> LINES ONLY
//
// The legend retains the tune marker. Colour and line style remain unchanged.
constexpr Style_t kDenseSpectrumMarker = 1;   // ROOT's single-pixel dot
constexpr float kDenseSpectrumMarkerSize = 0.0f;

// `dense` describes the figure, so callers supply it independently of the tune.
inline Style_t SpectrumMarker(bool dense, const std::string& tune)
{
  return dense ? kDenseSpectrumMarker : TuneMarker(tune);
}

inline float SpectrumMarkerSize(bool dense, float normalSize)
{
  return dense ? kDenseSpectrumMarkerSize : normalSize;
}

// Draw the ratio denominator last so an overlapping reference curve stays visible.
inline bool IsReferenceTune(const std::string& tune) { return tune == "MONASH"; }

// ---------------------------------------------------------------------------
// Line style carries the multiplicity class.
//
// The ladder lives here rather than in the plotting configurations, for the same
// reason the class LABELS do: two copies drift. The configurations' own
// `dependency_line_styles` block gave c1 and c11 BOTH style 1, so the lowest and
// highest classes -- the two V-EXTREMES draws -- were indistinguishable.
//
// Styles 1..10 are ROOT's predefined patterns. An eleventh is registered
// explicitly because eleven classes need eleven distinguishable lines.
constexpr Style_t kExtraClassLineStyle = 11;
constexpr const char* kExtraClassLineStyleDashes = "40 20 10 20";

inline void RegisterClassLineStyles()
{
  if (gStyle) {
    gStyle->SetLineStyleString(kExtraClassLineStyle, kExtraClassLineStyleDashes);
  }
}

// classIndex is 1-based in ASCENDING N_ch, matching the boundary artifact's own
// order, so the mapping is derived from the axis rather than from a table.
inline Style_t ClassLineStyle(int classIndex)
{
  if (classIndex < 1) return 1;
  if (classIndex <= 10) return static_cast<Style_t>(classIndex);
  return kExtraClassLineStyle;
}

template <typename T>
inline void ApplyTuneLineAndMarker(T* object,
                                   const std::string& tune,
                                   bool applyTuneLineStyle = true,
                                   bool openMarker = false)
{
  if (!object) return;
  object->SetLineColor(TuneColor(tune));
  object->SetMarkerColor(TuneColor(tune));
  const Style_t marker = TuneMarker(tune);
  object->SetMarkerStyle(openMarker ? OpenTuneMarker(marker) : marker);
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
