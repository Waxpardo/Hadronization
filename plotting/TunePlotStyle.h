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

// OWNER STYLING MANDATE, 2026-08-18. Tune identity is COLOUR + MARKER, and it is
// the same in every figure that overlays the three tunes:
//
//     MONASH        black   + circle   (20)
//     JUNCTIONS     blue    + square   (21)
//     CLOSEPACKING  purple  + triangle (22)
//
// and ALL THREE draw SOLID. Line style is reserved for distinctions WITHIN a
// tune -- multiplicity class above all -- so that a reader never has to ask
// whether a dashed curve means a different tune or a different class. Before
// this, JUNCTIONS was dashed and CLOSEPACKING dotted, so line style meant two
// things at once on the same canvas.
constexpr Color_t kMonashColour = kBlack;
constexpr Color_t kJunctionsColour = kBlue + 1;
// Purple rather than the previous kMagenta+1: magenta sits close to red in
// print and reads as a warm colour beside blue, while kViolet+1 stays clearly
// separated from both black and blue.
constexpr Color_t kClosepackingColour = kViolet + 1;
constexpr Color_t kUnknownTuneColour = kGray + 2;

constexpr Style_t kMonashMarker = 20;      // filled circle
constexpr Style_t kJunctionsMarker = 21;   // filled square
constexpr Style_t kClosepackingMarker = 22; // filled triangle
constexpr Style_t kUnknownTuneMarker = 24;

// Every tune draws solid. This is a rule, not a default.
constexpr Style_t kTuneLineStyle = 1;

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

// Kept so existing call sites need no edit, but it now returns SOLID for every
// tune. Tune identity is carried by colour and marker; line style is not
// available to it.
inline Style_t TuneLineStyle(const std::string& /*tune*/)
{
  return kTuneLineStyle;
}

// ---------------------------------------------------------------------------
// DENSE-SPECTRUM MODE, owner ruling 2026-08-18.
//
// The mandate above -- tune identity is colour + MARKER -- is right where it was
// written: a balancing panel holds two points per tune, and the marker is what
// tells them apart. Applied unchanged to the kinematic spectra it produced the
// opposite of its intent. Those histograms carry ~170 bins, so every bin drew a
// marker, the markers touched, and each tune became a SOLID RIBBON four to five
// times the line width with no histogram line visible at all. The reference tune
// was buried under the others and the apparent spread between tunes was set by
// marker size rather than by the data.
//
// So the rule is conditioned on density rather than abandoned:
//
//     FEW POINTS PER CURVE (balancing family)  -> markers, as mandated
//     DENSE CURVES (fig 4 + the 30 panels)     -> LINES ONLY
//
// In dense mode the tune's marker does not disappear from the figure; it moves
// to the LEGEND, which is the one place it is needed and the one place it can
// never collide with data. `kDenseSpectrumMarker` is ROOT's single-pixel marker
// 1: drawing is suppressed while the object still carries a valid marker, so
// nothing downstream has to special-case a zero.
//
// Colour still separates the tunes on the canvas, and the class ladder below is
// untouched -- dense mode changes markers, never colour and never line style.
constexpr Style_t kDenseSpectrumMarker = 1;   // ROOT's single-pixel dot
constexpr float kDenseSpectrumMarkerSize = 0.0f;

// Marker for a drawn curve. `dense` is a property of the FIGURE, not the tune,
// so it is passed in rather than inferred here.
inline Style_t SpectrumMarker(bool dense, const std::string& tune)
{
  return dense ? kDenseSpectrumMarker : TuneMarker(tune);
}

inline float SpectrumMarkerSize(bool dense, float normalSize)
{
  return dense ? kDenseSpectrumMarkerSize : normalSize;
}

// The reference tune is the denominator of every ratio panel, so it is the one
// curve a reader looks for first. Overlaid curves that agree to within a line
// width can only show the topmost, so the reference is drawn LAST.
//
// This is z-ORDER on a single pad. It is unrelated to the rejected MONASH-first
// PANEL ordering of the balancing canvas (RUN_RECORD 2026-08-16, variant B),
// which was about which row sits where and was refused because it separated the
// two ratio panels the paper compares.
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
