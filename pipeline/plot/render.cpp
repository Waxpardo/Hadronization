#include "TAxis.h"
#include "TAxisModLab.h"
#include "TCanvas.h"
#include "TColor.h"
#include "TError.h"
#include "TExec.h"
#include "TFile.h"
#include "TGraphErrors.h"
#include "TH1F.h"
#include "THLimitsFinder.h"
#include "TKey.h"
#include "TLatex.h"
#include "TLegend.h"
#include "TLegendEntry.h"
#include "TLine.h"
#include "TNamed.h"
#include "TObjString.h"
#include "TObjArray.h"
#include "TPad.h"
#include "TROOT.h"
#include "TStyle.h"
#include <algorithm>
#include <array>
#include <cctype>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <memory>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <tuple>
#include <vector>

namespace {
std::vector<std::string> Fields(const std::string& line) {
  std::vector<std::string> result;
  std::size_t first = 0;
  while (true) {
    const auto next = line.find('\t', first);
    result.push_back(line.substr(first, next - first));
    if (next == std::string::npos) break;
    first = next + 1;
  }
  return result;
}
void Need(bool condition, const char* message) {
  if (!condition) throw std::runtime_error(message);
}
double Number(std::string& text, bool optional = false) {
  if (optional && text == "-") return std::numeric_limits<double>::quiet_NaN();
  char* end = nullptr;
  const double value = std::strtod(text.c_str(), &end);
  Need(end != text.c_str() && end == text.c_str() + text.size() && std::isfinite(value),
       "invalid finite drawing number");
  // Reconstruct from the value actually consumed, rather than echoing tokens.
  std::ostringstream output;
  output << std::hexfloat << value;
  text = output.str();
  return value;
}
int Integer(const std::string& text) {
  std::size_t used = 0;
  const int value = std::stoi(text, &used);
  Need(used == text.size(), "invalid drawing integer");
  return value;
}
int Color(const std::string& hex) {
  Need(hex.size() == 7 && hex[0] == '#', "invalid RGB identity");
  return TColor::GetColor(hex.c_str());
}
int Marker(const std::string& name) {
  if (name == "filled_circle") return 20;
  if (name == "filled_square") return 21;
  if (name == "filled_up_triangle") return 22;
  if (name == "open_circle") return 24;
  throw std::runtime_error("invalid marker identity");
}
struct Point {
  std::string semanticId, valueStatus, uncertaintyStatus, reasons;
  int bin;
  double scientificX, x, y, error, binLow, binHigh, supportLow, supportHigh;
  std::string state;
};
struct Series {
  std::string key, tune, color, marker, label, legendLabel, mode, emphasis;
  int lineStyle;
  std::vector<Point> points;
};
struct Guide {
  double x1, x2, y1, y2;
  std::string id, color, label;
  int style;
};
struct Annotation { double x, y, size; std::string text; };
struct Panel {
  std::string id, status, title, xTitle, yTitle, note, reusePanel, reuseTune,
      uncertaintyDisplay;
  bool logY = false, logX = false, categoryDividers = true;
  double xLow = 0, xHigh = 1, yLow = 0, yHigh = 1;
  std::array<double, 4> geometry{}, margins{}, legend{};
  std::vector<Annotation> annotations;
  std::vector<Series> series;
  std::vector<Guide> guides;
  std::vector<std::pair<double, std::string>> ticks;
};
struct Page {
  std::string filename, role, information, title, scientificHeader, styleHeader;
  int textPixels, width, height;
  double headerBottom;
  std::vector<Panel> panels;
};
constexpr double kPaperWidthCentimeters = 18.;
constexpr double kPointsPerCentimeter = 72. / 2.54;
constexpr const char* kClassPatternDigest =
    "class_patterns_sha256=862f26b2a3c5d5c88418c6fe61c1a047a35422d8833ebdddf7826b163591fc94";
constexpr const char* kP1WithheldSeDisclosure =
    "Tune-ratio SE unavailable for unresolved sparse-tail denominators; "
    "see ROOT flags";
int BodyTextPixels(const Page& page) {
  const double paperWidthPoints =
      kPaperWidthCentimeters * kPointsPerCentimeter;
  return std::max(page.textPixels,
                  static_cast<int>(std::ceil(9. * page.width /
                                             paperWidthPoints)));
}
int PanelLegendTextPixels(const Page& page) {
  return page.role.find("correlations.") == 0
      ? BodyTextPixels(page) + 2 : BodyTextPixels(page);
}
double CategoryHalfWidth(const Page& page) {
  (void)page;
  return .50;
}
bool ActivityEndpoint(const Series& series) {
  return series.mode == "categories" && series.emphasis == "EXTREME";
}
int ScientificLineWidth(const Series& series) {
  return ActivityEndpoint(series) ? 2 : 1;
}
double ScientificMarkerSize(const Series& series, bool dense) {
  if (dense) return 0;
  if (series.mode == "categories") {
    if (ActivityEndpoint(series)) return 1.5;
    return series.lineStyle == 1 ? 1.3 : .85;
  }
  return 1.1;
}
int TuneRank(const std::string& label) {
  if (label == "MONASH") return 0;
  if (label == "JUNCTIONS") return 1;
  if (label == "CLOSEPACKING") return 2;
  return 3;
}
template <typename T>
void SortTuneSamples(std::vector<std::pair<std::string, T>>& samples) {
  std::stable_sort(samples.begin(), samples.end(),
      [](const auto& left, const auto& right) {
        return TuneRank(left.first) < TuneRank(right.first);
      });
}
int ClassLegendColumns(std::size_t count) {
  return static_cast<int>(std::max<std::size_t>(1,
      std::min<std::size_t>(4, count)));
}
double ClassLegendBottom(std::size_t count) {
  const int columns = ClassLegendColumns(count);
  const int rows = static_cast<int>((count + columns - 1) / columns);
  return .925 - .034 * rows;
}
std::vector<Page> ReadPlan(const std::filesystem::path& path,
                           const std::filesystem::path& record) {
  std::ifstream input(path, std::ios::binary);
  std::ofstream output(record, std::ios::binary | std::ios::trunc);
  Need(bool(input) && bool(output), "cannot open plan/record");
  std::vector<Page> pages;
  std::map<std::string, std::size_t> pageIndex;
  std::map<std::pair<std::string, std::string>, std::size_t> panelIndex;
  std::map<std::tuple<std::string, std::string, std::string>, std::size_t> seriesIndex;
  std::string line;
  Need(bool(std::getline(input, line)), "missing plan header");
  const auto header = Fields(line);
  Need(header.size() == 2 && header[0] == "hadronization_plot_drawing_plan_v9", "plan framing differs");
  output << line << '\n';
  bool ended = false;
  while (std::getline(input, line)) {
    auto f = Fields(line);
    if (f[0] == "END") {
      Need(f.size() == 1, "invalid END");
      ended = true;
      output << "END\n";
      break;
    }
    if (f[0] == "PAGE") {
      Need(f.size() == 13 && !pageIndex.count(f[1]), "page differs");
      Need(std::filesystem::path(f[1]).filename() == f[1] &&
           std::filesystem::path(f[1]).extension() == ".pdf", "unsafe page filename");
      const double headerBottom = Number(f[10]);
      Need(headerBottom > 0 && headerBottom < 1, "invalid title region geometry");
      pageIndex[f[1]] = pages.size();
      pages.push_back({f[1], f[2], f[6], f[7], f[11], f[12], Integer(f[5]),
                       Integer(f[8]), Integer(f[9]), headerBottom, {}});
      Need(pages.back().styleHeader == kClassPatternDigest,
           "class pattern registry digest differs");
    } else {
      Need(f.size() >= 3 && pageIndex.count(f[1]), "unknown page parent");
      Page& page = pages.at(pageIndex.at(f[1]));
      const auto panelKey = std::make_pair(f[1], f[2]);
      if (f[0] == "PANEL") {
        Need(f.size() == 28 && !panelIndex.count(panelKey) &&
             (f[26]=="STANDARD" || f[26]=="CENTERS_ONLY" ||
              f[26]=="DENSE_BAND") &&
             (f[27]=="0" || f[27]=="1"), "panel differs");
        Panel panel;
        panel.id = f[2]; panel.status = f[3]; panel.logY = Integer(f[4]) != 0;
        panel.logX = Integer(f[25]) != 0;
        panel.uncertaintyDisplay=f[26];
        panel.categoryDividers=Integer(f[27]) != 0;
        Need(panel.uncertaintyDisplay ==
             (page.role=="multiplicity.composite" ? "DENSE_BAND" : "STANDARD"),
             "paper uncertainty display identity differs");
        panel.xLow = Number(f[5]); panel.xHigh = Number(f[6]);
        panel.yLow = Number(f[7]); panel.yHigh = Number(f[8]);
        for (int i = 0; i < 4; ++i) {
          panel.geometry[i] = Number(f[9+i]);
          panel.margins[i] = Number(f[17+i]);
          panel.legend[i] = Number(f[21+i]);
        }
        Need(panel.xLow < panel.xHigh && panel.yLow < panel.yHigh &&
             (!panel.logY || panel.yLow > 0) &&
             (!panel.logX || panel.xLow > 0), "invalid zero/log range");
        Need(0 <= panel.geometry[0] && panel.geometry[0] < panel.geometry[2] &&
             panel.geometry[2] <= 1 && 0 <= panel.geometry[1] &&
             panel.geometry[1] < panel.geometry[3] && panel.geometry[3] <= page.headerBottom,
             "clipped title region geometry");
        panel.title = f[13]; panel.xTitle = f[14]; panel.yTitle = f[15]; panel.note = f[16];
        panelIndex[panelKey] = page.panels.size();
        page.panels.push_back(panel);
      } else {
        Need(panelIndex.count(panelKey), "unknown panel parent");
        Panel& panel = page.panels.at(panelIndex.at(panelKey));
        if (f[0] == "ANNOTATION") {
          Need(f.size()==7, "annotation framing differs");
          const double x=Number(f[3]), y=Number(f[4]), size=Number(f[5]);
          Need(x>=0 && x<=1 && y>=0 && y<=1 && size>=10 && size<=100,
               "annotation geometry differs");
          panel.annotations.push_back({x,y,size,f[6]});
        } else if (f[0] == "SERIES") {
          Need(f.size() == 13 &&
               (f[12] == "NORMAL" ||
                (f[12] == "EXTREME" && f[10] == "categories")),
               "series emphasis differs");
          const auto key = std::make_tuple(f[1], f[2], f[3]);
          Need(!seriesIndex.count(key), "duplicate series");
          seriesIndex[key] = panel.series.size();
          panel.series.push_back({f[3], f[4], f[6], f[7], f[9], f[11], f[10], f[12], Integer(f[8]), {}});
        } else if (f[0] == "POINT") {
          Need(f.size() == 19, "point differs");
          const auto key = std::make_tuple(f[1], f[2], f[3]);
          Need(seriesIndex.count(key), "unknown series parent");
          std::array<double, 8> values{};
          for (int i = 0; i < 8; ++i) values[i] = Number(f[6+i], true);
          Need(!std::isfinite(values[3]) || values[3] >= 0, "negative uncertainty");
          const Series& parent = panel.series.at(seriesIndex.at(key));
          const bool scientificFinite = std::isfinite(values[0]);
          const bool displayFinite = std::isfinite(values[1]);
          Need(scientificFinite == displayFinite,
               "scientific/display coordinate availability differs");
          Need(parent.mode == "categories" ||
                   (!scientificFinite || values[0] == values[1]),
               "noncategorical display coordinate differs from science");
          Need(f[17] == "DRAW" || f[17] == "FLOW_BIN" ||
                   f[17] == "EMPTY_SUPPORT" || f[17] == "MISSING_VALUE" ||
                   f[17] == "LOG_NONPOSITIVE",
               "point drawing state differs");
          Need(f[17] != "DRAW" || (displayFinite && std::isfinite(values[2])),
               "drawable point lacks finite coordinates/value");
          panel.series.at(seriesIndex.at(key)).points.push_back(
              {f[4], f[15], f[16], f[18], Integer(f[5]), values[0],
               values[1], values[2], values[3], values[4], values[5],
               values[6], values[7], f[17]});
        } else if (f[0] == "GUIDE") {
          Need(f.size() == 11, "guide differs");
          panel.guides.push_back({Number(f[4]), Number(f[5]), Number(f[6]), Number(f[7]),
                                   f[3], f[8], f[10], Integer(f[9])});
        } else if (f[0] == "TICK") {
          Need(f.size() == 5, "tick differs");
          panel.ticks.emplace_back(Number(f[3]), f[4]);
        } else if (f[0] == "REUSE") {
          Need(f.size() == 5, "inset reference differs");
          panel.reusePanel = f[3]; panel.reuseTune = f[4];
        } else {
          throw std::runtime_error("unknown drawing record");
        }
      }
    }
    for (std::size_t i = 0; i < f.size(); ++i) output << (i ? "\t" : "") << f[i];
    output << '\n';
  }
  Need(ended && !std::getline(input, line) && !pages.empty(), "plan incomplete/trailing");
  output.flush();
  Need(bool(output), "record flush failed");
  return pages;
}
std::string NumberToken(double value) {
  if (!std::isfinite(value)) return "-";
  std::ostringstream output;
  output << std::hexfloat << value;
  return output.str();
}
std::string CanvasName(const Page& page) {
  const std::string suffix = ".pdf";
  Need(page.filename.size() > suffix.size() &&
       page.filename.substr(page.filename.size() - suffix.size()) == suffix,
       "canvas page filename differs");
  return page.filename.substr(0, page.filename.size() - suffix.size());
}
std::string IndexToken(std::size_t value) {
  std::ostringstream output;
  output << std::setw(3) << std::setfill('0') << value;
  return output.str();
}
std::string SafeToken(const std::string& value) {
  std::string result;
  for (const unsigned char character : value) {
    result.push_back(std::isalnum(character) ? static_cast<char>(character) : '_');
  }
  return result.empty() ? "unnamed" : result;
}
std::string PadName(std::size_t panelIndex, const Panel& panel) {
  return "scientific_pad_p" + IndexToken(panelIndex) + "_" + SafeToken(panel.id);
}
std::string FrameName(std::size_t panelIndex) {
  return "scientific_frame_p" + IndexToken(panelIndex);
}
std::string GraphName(std::size_t panelIndex, std::size_t seriesIndex,
                      const std::string& kind, std::size_t runIndex = 0) {
  std::string result = "scientific_graph_p" + IndexToken(panelIndex) +
                       "_s" + IndexToken(seriesIndex) + "_" + kind;
  if (kind == "line" || kind == "band") result += "_r" + IndexToken(runIndex);
  return result;
}
std::string GraphTitle(const Series& series, const std::string& kind) {
  return kind + ":" + series.tune + ":" + series.key;
}
std::string PageIdentity(const Page& page) {
  std::ostringstream output;
  output << "PAGE\t" << page.role << '\t' << page.filename << '\n';
  output << "STYLE\t" << page.styleHeader << '\n';
  for (const auto& panel : page.panels) {
    output << "PANEL\t" << panel.id << '\t' << panel.status << '\n';
    for (const auto& series : panel.series) {
      output << "SERIES\t" << series.key << '\t' << series.tune << '\t'
             << series.lineStyle << '\t' << series.mode << '\n';
      for (const auto& point : series.points) {
        output << "POINT\t" << point.semanticId << '\t' << point.bin << '\t'
               << NumberToken(point.scientificX) << '\t'
               << NumberToken(point.x) << '\t' << NumberToken(point.y) << '\t'
               << NumberToken(point.error) << '\t'
               << NumberToken(point.binLow) << '\t'
               << NumberToken(point.binHigh) << '\t'
               << NumberToken(point.supportLow) << '\t'
               << NumberToken(point.supportHigh) << '\t'
               << point.valueStatus << '\t' << point.uncertaintyStatus << '\t'
               << point.state << '\t' << point.reasons << '\n';
      }
    }
  }
  return output.str();
}
std::string ReadBytes(const std::filesystem::path& path) {
  std::ifstream input(path, std::ios::binary);
  Need(bool(input), "cannot open drawing record");
  std::ostringstream output;
  output << input.rdbuf();
  Need(bool(input) || input.eof(), "cannot read drawing record");
  return output.str();
}
bool Close(double left, double right) {
  return std::isfinite(left) && std::isfinite(right) &&
         std::abs(left - right) <=
             1e-11 * std::max({1.0, std::abs(left), std::abs(right)});
}
bool SameBinary64(double left, double right) {
  std::uint64_t leftBits = 0, rightBits = 0;
  static_assert(sizeof(leftBits) == sizeof(left));
  std::memcpy(&leftBits, &left, sizeof(left));
  std::memcpy(&rightBits, &right, sizeof(right));
  return leftBits == rightBits;
}
bool StoredFloatClose(double left, double right) {
  return std::isfinite(left) && std::isfinite(right) &&
         std::abs(left - right) <=
             1e-6 * std::max({1.0, std::abs(left), std::abs(right)});
}
bool Drawable(const Panel& panel, const Point& point) {
  return point.state == "DRAW" && std::isfinite(point.x) &&
         std::isfinite(point.y) &&
         (!panel.logY || point.y > 0) &&
         (!panel.logX || point.x >= panel.xLow);
}
std::vector<const Series*> SelectedSeries(const Page& page, const Panel& panel,
                                          const std::vector<Page>& pages) {
  std::vector<const Series*> selected;
  if (panel.reusePanel.empty()) {
    for (const auto& series : panel.series) selected.push_back(&series);
    return selected;
  }
  const Panel* source = nullptr;
  for (const Page& other : pages) {
    if (other.role != page.role) continue;
    for (const Panel& candidate : other.panels) {
      if (candidate.id == panel.reusePanel) source = &candidate;
    }
  }
  Need(source != nullptr, "missing inset source panel");
  for (const auto& series : source->series) {
    if (panel.reuseTune == "*" || series.tune == panel.reuseTune)
      selected.push_back(&series);
  }
  return selected;
}
std::vector<double> StatusRailCoordinates(const Page& page, const Panel& panel,
                                          const std::vector<Page>& pages) {
  // The inset repeats the histogram only; its source panel retains all status
  // marks and the page disclosure, without a second rail through class labels.
  if (!panel.reusePanel.empty()) return {};
  // A complete multiplicity campaign can contain thousands of absent tail
  // bins.  A cross for every absent bin aliases into a thick horizontal bar;
  // the exact states remain in the drawing record and numerical ROOT.
  if (page.role == "multiplicity.composite" &&
      page.scientificHeader.empty()) return {};
  std::set<double> unique;
  for (const Series* series : SelectedSeries(page, panel, pages)) {
    for (const Point& point : series->points) {
      if (point.state == "DRAW" || !std::isfinite(point.scientificX) ||
          (page.role.rfind("correlations.",0)==0 &&
           point.state=="LOG_NONPOSITIVE")) continue;
      if (point.scientificX < panel.xLow || point.scientificX > panel.xHigh)
        continue;
      if (panel.logX && point.scientificX <= 0) continue;
      unique.insert(point.scientificX);
    }
  }
  return {unique.begin(), unique.end()};
}
struct ExpectedGraph {
  std::string name, title;
  const Series* series;
  bool dense;
  std::vector<double> x, y, ex, ey;
};
void AddExpectedPoint(ExpectedGraph& graph, double x, double y,
                      double ex = 0, double ey = 0) {
  graph.x.push_back(x); graph.y.push_back(y);
  graph.ex.push_back(ex); graph.ey.push_back(ey);
}
std::vector<ExpectedGraph> ExpectedGraphs(const Page& page,
                                          const Panel& panel,
                                          const Series& series,
                                          std::size_t panelIndex,
                                          std::size_t seriesIndex) {
  const bool categories = series.mode == "categories";
  const bool histogram = series.mode == "histogram";
  const bool dense = histogram && series.points.size() > 40;
  ExpectedGraph points{GraphName(panelIndex, seriesIndex, "points"),
                       GraphTitle(series, "points"), &series, dense, {}, {}, {}, {}};
  std::vector<ExpectedGraph> runs;
  bool breakRun = true;
  for (const Point& point : series.points) {
    if (!Drawable(panel, point)) {
      breakRun = true;
      continue;
    }
    AddExpectedPoint(points, point.x, point.y, 0,
                     std::isfinite(point.error) ? point.error : 0);
    if (breakRun) {
      const std::size_t runIndex = runs.size();
      runs.push_back({GraphName(panelIndex, seriesIndex, "line", runIndex),
                      GraphTitle(series, "line"), &series, dense,
                      {}, {}, {}, {}});
      breakRun = false;
    }
    ExpectedGraph& line = runs.back();
    if (categories) {
      AddExpectedPoint(line, point.x - CategoryHalfWidth(page), point.y);
      AddExpectedPoint(line, point.x + CategoryHalfWidth(page), point.y);
      breakRun = true;
    } else if (histogram && std::isfinite(point.binLow) &&
               std::isfinite(point.binHigh)) {
      AddExpectedPoint(line, panel.logX ? std::max(point.binLow, panel.xLow)
                                        : point.binLow, point.y);
      AddExpectedPoint(line, point.binHigh, point.y);
    } else {
      AddExpectedPoint(line, point.x, point.y);
    }
  }
  if (points.x.empty()) return {};
  std::vector<ExpectedGraph> result;
  if ((dense || !panel.reusePanel.empty()) &&
      panel.uncertaintyDisplay != "CENTERS_ONLY") {
    bool newBand = true;
    double previousHigh = std::numeric_limits<double>::quiet_NaN();
    for (const Point& point : series.points) {
      if (!Drawable(panel, point) || !std::isfinite(point.error) ||
          !std::isfinite(point.binLow) || !std::isfinite(point.binHigh)) {
        newBand = true;
        continue;
      }
      if (newBand || !Close(previousHigh, point.binLow)) {
        const auto number = result.size();
        result.push_back({GraphName(panelIndex, seriesIndex, "band", number),
                          GraphTitle(series, "band"), &series, true,
                          {}, {}, {}, {}});
        newBand = false;
      }
      auto& band = result.back();
      AddExpectedPoint(band, panel.logX ? std::max(point.binLow, panel.xLow)
                                       : point.binLow, point.y, 0, point.error);
      AddExpectedPoint(band, point.binHigh, point.y, 0, point.error);
      previousHigh = point.binHigh;
    }
  }
  if (series.mode != "points")
    result.insert(result.end(), runs.begin(), runs.end());
  result.push_back(std::move(points));
  if (!panel.reusePanel.empty()) return result;
  if (dense) {
    ExpectedGraph markers{GraphName(panelIndex, seriesIndex, "dense_markers"),
                          GraphTitle(series, "dense_markers"), &series, false,
                          {}, {}, {}, {}};
    std::vector<const Point*> visible;
    for (const auto& point : series.points) {
      if (point.x >= panel.xLow && point.x <= panel.xHigh)
        visible.push_back(&point);
    }
    const std::size_t stride = std::max<std::size_t>(1, visible.size() / 18);
    for (std::size_t index = 0; index < visible.size(); index += stride) {
      const Point& point = *visible[index];
      if (Drawable(panel, point))
        AddExpectedPoint(markers, point.x, point.y);
    }
    result.push_back(std::move(markers));
  }
  return result;
}
void VerifyGraph(const TGraphErrors& actual, const ExpectedGraph& expected, bool inset) {
  Need(actual.GetName() == expected.name &&
       actual.GetTitle() == expected.title,
       "scientific graph identity differs from drawing record");
  Need(actual.GetN() == static_cast<int>(expected.x.size()),
       "scientific graph point count differs from drawing record");
  for (int index = 0; index < actual.GetN(); ++index) {
    double x = 0, y = 0;
    actual.GetPoint(index, x, y);
    Need(SameBinary64(x, expected.x[index]) &&
         SameBinary64(y, expected.y[index]) &&
         SameBinary64(actual.GetErrorX(index), expected.ex[index]) &&
         SameBinary64(actual.GetErrorY(index), expected.ey[index]),
         "scientific graph coordinates/errors differ from drawing record");
  }
  const int expectedColor=Color(expected.series->color);
  if (expected.title.rfind("band:",0)==0) {
    const auto* fill=gROOT->GetColor(actual.GetFillColor());
    const auto* base=gROOT->GetColor(expectedColor);
    Need(fill && base && actual.GetFillStyle()==1001 &&
         StoredFloatClose(fill->GetAlpha(),.12) &&
         StoredFloatClose(fill->GetRed(),base->GetRed()) &&
         StoredFloatClose(fill->GetGreen(),base->GetGreen()) &&
         StoredFloatClose(fill->GetBlue(),base->GetBlue()),
         "scientific error-band fill differs");
  }
  const bool styleMatches=
       actual.GetLineColor() == expectedColor &&
       actual.GetMarkerColor() == expectedColor &&
       actual.GetMarkerStyle() == Marker(expected.series->marker) &&
       StoredFloatClose(actual.GetMarkerSize(),
                        inset ? 0.0 : ScientificMarkerSize(*expected.series,
                                             expected.dense)) &&
       actual.GetLineStyle() == expected.series->lineStyle &&
       actual.GetLineWidth() == (inset ? 2 : ScientificLineWidth(*expected.series));
  if (!styleMatches) {
    std::ostringstream message;
    message << "scientific graph style differs from drawing record: "
            << expected.name << " actual=" << actual.GetLineColor() << ","
            << actual.GetMarkerColor() << "," << actual.GetMarkerStyle()
            << "," << actual.GetMarkerSize() << "," << actual.GetLineStyle()
            << "," << actual.GetLineWidth() << " expected=" << expectedColor
            << "," << expectedColor << "," << Marker(expected.series->marker)
            << "," << (inset ? 0.0 : ScientificMarkerSize(*expected.series,expected.dense))
            << "," << expected.series->lineStyle << ","
            << (inset ? 2 : ScientificLineWidth(*expected.series));
    throw std::runtime_error(message.str());
  }
}
struct ExpectedText {
  std::string text;
  double x, y, size, angle;
  int color, align;
};
ExpectedText TextExpectation(const std::string& text, double x, double y,
                             double size, int color = 1, int align = 11,
                             double angle = 0) {
  return {text, x, y, size, angle, color, align};
}
bool PanelHasDrawing(const Page& page, const Panel& panel,
                     const std::vector<Page>& pages,
                     std::size_t panelIndex) {
  const auto selected = SelectedSeries(page, panel, pages);
  for (std::size_t seriesIndex = 0; seriesIndex < selected.size(); ++seriesIndex) {
    if (!ExpectedGraphs(page, panel, *selected[seriesIndex], panelIndex,
                        seriesIndex).empty())
      return true;
  }
  return false;
}
bool CategoricalAxis(const Page& page, const Panel& panel) {
  // Identity is the scientific role, independent of hidden upper-pad labels.
  return page.role.find("balancing.") == 0 && panel.reusePanel.empty();
}
bool SpeciesCategoryAxis(const Page& page) {
  return page.role.rfind("balancing.integrated.", 0) == 0 ||
         page.role.rfind("balancing.activity.", 0) == 0;
}
bool RotateCategoryLabels(const Page& page, const Panel& panel) {
  return panel.ticks.size() >= 5 && !SpeciesCategoryAxis(page) &&
         page.role.rfind("correlations.", 0) != 0;
}
bool SharedXTitle(const Page& page) {
  return page.role.rfind("correlations.", 0) == 0 ||
         page.role == "balancing.baryon_meson.activity" ||
         SpeciesCategoryAxis(page);
}
bool SharedStackYTitle(const Page& page, const Panel& panel) {
  return page.panels.size() == 8 &&
         page.role.rfind("balancing.", 0) == 0 &&
         panel.id.rfind("upper.", 0) == 0;
}
bool SharedRightAxis(const Panel& panel) {
  return panel.geometry[0] > 0 && panel.margins[0] == 0.;
}
double PanelTitleX(const Panel& panel) {
  return panel.margins[0] + (SharedRightAxis(panel) ? .025 : 0.);
}
double JoinedEndLabelOffset(const Page& page, const Panel& panel, double x) {
  if (page.role.rfind("correlations.", 0) != 0) return 0.;
  const double width = (panel.geometry[2]-panel.geometry[0])*page.width;
  const double clearance = 1.35*BodyTextPixels(page)/width;
  if (SharedRightAxis(panel) && SameBinary64(x, panel.xLow)) return clearance;
  if (panel.margins[1] == 0. && panel.geometry[2] < 1. &&
      SameBinary64(x, panel.xHigh)) return -clearance;
  return 0.;
}
double StatusRailY(const Page& page, const Panel& panel) {
  const bool extendedSpecies = panel.ticks.size() > 5 &&
      (page.role.rfind("balancing.integrated.", 0) == 0 ||
       page.role.rfind("balancing.activity.", 0) == 0);
  // Keep status markers above the frame edge, clear of particle typography.
  if (extendedSpecies) {
    const double height = (panel.geometry[3]-panel.geometry[1])*page.height;
    return panel.margins[2] + .75*BodyTextPixels(page)/height;
  }
  return std::max(.03, panel.margins[2] - .005);
}
std::vector<ExpectedText> StateGlyphTexts(
    const Page& page, const Panel& panel, const std::vector<Page>& pages) {
  if (!panel.reusePanel.empty()) return {};
  // Missing/withheld uncertainties remain explicit in the numerical ROOT and
  // drawing record. Question-mark glyphs obscure the compact paper ratio
  // panel and do not add a scientific coordinate.
  if (page.role == "multiplicity.composite" &&
      page.scientificHeader.empty()) return {};
  // Production balancing pages disclose unavailable SE once in the footer;
  // the exact per-point status and reason remain in the drawing record.
  if (page.role.rfind("balancing.", 0) == 0 &&
      page.scientificHeader.empty()) return {};
  // G9 ratio pages can contain many unresolved-reference bins.  Per-point
  // question marks obscure the curve; the panel footer and drawing record
  // retain the same explicit uncertainty state and reason.
  if (page.role == "spectra.signed_heavy") return {};
  std::vector<ExpectedText> result;
  std::set<std::pair<int,int>> occupied;
  const double frameWidth = 1 - panel.margins[0] - panel.margins[1];
  const double frameHeight = 1 - panel.margins[2] - panel.margins[3];
  for (const Series* series : SelectedSeries(page, panel, pages)) {
    for (const Point& point : series->points) {
      if (!Drawable(panel, point) || point.x < panel.xLow ||
          point.x > panel.xHigh || point.y < panel.yLow ||
          point.y > panel.yHigh) continue;
      if (std::isfinite(point.error)) continue;
      const double fx = panel.logX ?
          std::log(point.x / panel.xLow) /
              std::log(panel.xHigh / panel.xLow) :
          (point.x - panel.xLow) / (panel.xHigh - panel.xLow);
      const double fy = panel.logY ?
          std::log(point.y / panel.yLow) /
              std::log(panel.yHigh / panel.yLow) :
          (point.y - panel.yLow) / (panel.yHigh - panel.yLow);
      const double x = panel.margins[0] + frameWidth * fx +
                       (fx > .90 ? -.018 : .011);
      const double y = panel.margins[2] + frameHeight * fy +
                       (fy > .90 ? -.018 : .015);
      if (!occupied.emplace(std::lround(x*24),std::lround(y*20)).second)
        continue;
      result.push_back(TextExpectation(
          "?", x, y, std::max(13, BodyTextPixels(page) - 2), kGray + 2));
    }
  }
  return result;
}
std::vector<double> CategoryCenters(const Panel& panel) {
  std::set<double> centers;
  for (const auto& series : panel.series)
    for (const auto& point : series.points)
      if (std::isfinite(point.scientificX) &&
          point.scientificX >= panel.xLow &&
          point.scientificX <= panel.xHigh)
        centers.insert(point.scientificX);
  return {centers.begin(), centers.end()};
}
std::vector<double> CategoryBoundaries(const Panel& panel) {
  std::set<double> boundaries;
  for (double center : CategoryCenters(panel)) {
    boundaries.insert(center - .5);
    boundaries.insert(center + .5);
  }
  return {boundaries.begin(), boundaries.end()};
}
std::vector<ExpectedText> InsetClassTexts(const Page& page,
                                          const Panel& panel) {
  if (page.role != "multiplicity.composite" ||
      panel.id != "inset.monash_boundaries") return {};
  std::vector<const Guide*> labels;
  for (const auto& guide : panel.guides)
    if (guide.id.rfind("class.", 0) == 0 && !guide.label.empty())
      labels.push_back(&guide);
  const bool partialSample =
      page.scientificHeader == "TEST_ONLY / SYNTHETIC / PARTIAL_SAMPLE";
  Need(partialSample ? labels.size() <= 11 : labels.size() == 11,
       "P1 inset eleven labelled classes absent");
  std::vector<ExpectedText> result;
  const double frameWidth = 1 - panel.margins[0] - panel.margins[1];
  for (std::size_t index = 0; index < labels.size(); ++index) {
    const Guide& guide = *labels[index];
    Need(guide.x2 > guide.x1 && !guide.label.empty() &&
         guide.label.back() == '%' &&
         guide.label.find('[') == std::string::npos,
         "P1 inset percentile slice label differs");
    const double low = std::max(guide.x1, panel.xLow);
    const double high = std::min(guide.x2, panel.xHigh);
    if (high <= low) continue;
    const double center = std::sqrt(low * high);
    const double x = panel.margins[0] + frameWidth *
        std::log(center / panel.xLow) / std::log(panel.xHigh / panel.xLow);
    // Pre-lean places centered vertical labels 20% up the logarithmic frame,
    // at each interval's geometric center. Intervals remain numerics-owned.
    result.push_back(TextExpectation(guide.label, x,
        panel.margins[2] + .20*(1-panel.margins[2]-panel.margins[3]),
        .048*(panel.geometry[3]-panel.geometry[1])*page.height, 1, 22, 90));
  }
  return result;
}
std::vector<std::string> P1InformationLines(const Page& page) {
  if (page.role != "multiplicity.composite") return {};
  const auto titleSplit = page.title.find("; ");
  const auto selectionSplit = page.information.find("; ");
  Need(titleSplit != std::string::npos &&
       selectionSplit != std::string::npos,
       "P1 information cannot be arranged beside the tune key");
  const std::string selection = page.information.substr(selectionSplit + 2);
  const auto etaSplit = selection.find(", |#eta|");
  Need(etaSplit != std::string::npos,
       "P1 charged-light selection cannot be split into lines");
  const std::string population = page.information.substr(0, selectionSplit);
  Need(population ==
           "#it{N}_{ch}: charged-light final-particle activity, heavy flavour excluded",
       "P1 charged-light population caption differs");
  return {"#bf{" + page.title.substr(0, titleSplit) + "}",
          page.title.substr(titleSplit + 2),
          selection.substr(0, etaSplit) + ", " +
              selection.substr(etaSplit + 2),
          "charged-light final particles",
          "heavy flavour excluded"};
}
std::vector<std::string> StatusNoteLines(const std::string& note) {
  std::vector<std::string> result;
  std::size_t start=0;
  while (start<note.size()) {
    const auto split=note.find("; ",start);
    result.push_back(note.substr(start,
        split==std::string::npos ? split : split-start));
    if (split==std::string::npos) break;
    start=split+2;
  }
  return result;
}
double BlankStatusY(const Page& page, const Panel& panel) {
  if (page.role=="spectra.signed_heavy" && panel.id=="g9.ratio")
    return .78;
  return page.role.rfind("balancing.",0)==0 &&
         panel.id.rfind("lower.",0)==0 ? .82 : .54;
}
double BlankNoteY(const Page& page, const Panel& panel) {
  if (page.role=="spectra.signed_heavy" && panel.id=="g9.ratio")
    return .59;
  return page.role.rfind("balancing.",0)==0 &&
         panel.id.rfind("lower.",0)==0 ? .55 : .46;
}
double BlankNoteStep(const Page& page, const Panel& panel) {
  // The G9 ratio pad is shorter than the absolute pad; keep complete status
  // reasons clear of each other and the x axis at publication size.
  return page.role=="spectra.signed_heavy" && panel.id=="g9.ratio"
             ? .10 : .045;
}
// This information column and the tune key occupy disjoint horizontal bands.
// Keep the complete charged-activity caption in the typed page information;
// these shorter lines fit beside the three-entry legend at publication width.
constexpr double P1InformationX = .50;
constexpr std::array<double, 5> kP1InformationY = {{.835, .810, .785, .760, .735}};
constexpr std::array<int, 5> kP1InformationPixels = {{20, 17, 16, 15, 15}};
double CategoryLabelY(const Page& page, const Panel& panel) {
  if (SpeciesCategoryAxis(page)) {
    // Use a common letter baseline, independent of bars and scripts.
    const double height = (panel.geometry[3]-panel.geometry[1])*page.height;
    return panel.margins[2] - 1.65*BodyTextPixels(page)/height;
  }
  return panel.margins[2] -
      (page.role == "balancing.baryon_meson.activity" ? .015 : .025);
}
double PanelTitleY(const Page& page, const Panel& panel) {
  if (page.role.rfind("correlations.",0)==0) {
    const double ph=page.height*(panel.geometry[3]-panel.geometry[1]);
    return 1-panel.margins[3]+
        (panel.id.rfind("correlation.main.",0)==0 ? 1.25 : .35)*BodyTextPixels(page)/ph;
  }
  if (panel.margins[3] > .25 || page.role.rfind("correlations.", 0) == 0)
    return 1 - panel.margins[3] + .035;
  if (page.role.rfind("balancing.integrated.", 0) == 0 &&
      panel.id.rfind("upper.", 0) == 0)
    return 1 - panel.margins[3] + .035;
  return .94;
}
double CategoricalXTitleY(const Page& page) {
  if (page.role.rfind("balancing.integrated.", 0) == 0) return .120;
  if (page.role.rfind("balancing.activity.", 0) == 0) return .105;
  return .075;
}
bool PreserveJoinedLogLabels(const Page& page, const Panel& panel) {
  return page.role.rfind("balancing.", 0) == 0 &&
         page.role.size() >= 6 &&
         page.role.compare(page.role.size() - 6, 6, ".charm") == 0 &&
         panel.id.rfind("upper.", 0) == 0 && panel.logY;
}
struct YAxisLabelPolicy {
  bool suppressFirst = false;
  bool suppressLast = false;
  int optimizedAnchors = -1;
};
YAxisLabelPolicy JoinedYAxisLabelPolicy(const Page& page,
                                        const Panel& panel, bool inset) {
  YAxisLabelPolicy policy;
  policy.suppressFirst = !inset && panel.margins[2] == 0. &&
                         !PreserveJoinedLogLabels(page, panel);
  policy.suppressLast = !inset && panel.margins[3] == 0.;
  if (page.role == "multiplicity.composite" && panel.id == "lower.ratio")
    policy.suppressLast = false;
  // A panel touching one adjacent panel still owns an independent numerical
  // scale.  Preserve its seam label when ROOT's five-primary-division
  // optimization provides only two anchors; suppressing either would leave
  // the scale numerically ambiguous.  Middle rows touch on both sides and
  // inherit the explicitly common scale shown by the end row of their stack.
  if (!inset && !panel.logY &&
      policy.suppressFirst != policy.suppressLast) {
    Double_t optimizedLow = 0., optimizedHigh = 0., width = 0.;
    Int_t intervals = 0;
    THLimitsFinder::Optimize(panel.yLow, panel.yHigh, 5, optimizedLow,
                             optimizedHigh, intervals, width);
    policy.optimizedAnchors = intervals + 1;
    if (policy.optimizedAnchors -
            static_cast<int>(policy.suppressFirst) -
            static_cast<int>(policy.suppressLast) < 2) {
      policy.suppressFirst = false;
      policy.suppressLast = false;
    }
  }
  return policy;
}
void VerifyYAxisLabelPolicyFixtures() {
  Page page;
  Panel panel;
  panel.logY = false;
  panel.margins = {{.20, .035, .22, 0.}};
  panel.yLow = .8417700440987118;
  panel.yHigh = 1.3866668947122398;
  auto policy = JoinedYAxisLabelPolicy(page, panel, false);
  Need(!policy.suppressLast && policy.optimizedAnchors == 2,
       "joined lower linear scale loses its second numeric anchor");
  panel.margins = {{.14, .04, 0., .10}};
  panel.yLow = .009445158099908748;
  panel.yHigh = .010449635455012034;
  policy = JoinedYAxisLabelPolicy(page, panel, false);
  Need(!policy.suppressFirst && policy.optimizedAnchors == 2,
       "joined upper narrow-linear scale loses its first numeric anchor");
  panel.yLow = -.007059155933277776;
  panel.yHigh = .09529859279942896;
  policy = JoinedYAxisLabelPolicy(page, panel, false);
  Need(!policy.suppressFirst && policy.optimizedAnchors == 2,
       "joined upper zero-bearing scale loses its first numeric anchor");
}
bool BeautyCorrelationUsesFullTickValues(const Page& page,
                                         const Panel& panel) {
  return page.role == "correlations.beauty" &&
         panel.id.rfind("correlation.teaching.", 0) == 0 &&
         panel.id.size() >= 10 &&
         panel.id.compare(panel.id.size() - 10, 10, ".inclusive") == 0;
}
bool AxisLabelSuppressed(const TAxis& axis, int labelNumber) {
  const TList* modified = axis.GetModifiedLabels();
  if (modified == nullptr) return false;
  TIter iterator(modified);
  while (const auto* object = iterator()) {
    const auto* label = dynamic_cast<const TAxisModLab*>(object);
    if (label != nullptr && label->GetLabNum() == labelNumber &&
        label->GetSize() == 0.)
      return true;
  }
  return false;
}
double CategoryTickInnerY(const Page& page, const Panel& panel, bool top) {
  // Keep species separators visible on short ratio panels at print size.
  const double frameHeight = (panel.geometry[3]-panel.geometry[1])*page.height*
      (1-panel.margins[2]-panel.margins[3]);
  const double fraction = SpeciesCategoryAxis(page)
      ? .23*BodyTextPixels(page)/frameHeight : .012;
  if (panel.logY) {
    const double factor = std::pow(panel.yHigh / panel.yLow, fraction);
    return top ? panel.yHigh / factor : panel.yLow * factor;
  }
  const double delta = (panel.yHigh - panel.yLow) * fraction;
  return top ? panel.yHigh - delta : panel.yLow + delta;
}
double YTitleX(const Page& page, const Panel& panel) {
  const double base=page.role.find("correlations.")==0 ? .025 :
      (page.role.find("balancing.")==0 && panel.id.rfind("upper.",0)==0 ? .05 : .075);
  const double width=page.width*(panel.geometry[2]-panel.geometry[0]);
  return std::max(.012,base-.3*BodyTextPixels(page)/width);
}
std::vector<ExpectedText> ExpectedPanelTexts(const Page& page,
                                             const Panel& panel,
                                             const std::vector<Page>& pages,
                                             std::size_t panelIndex) {
  std::vector<ExpectedText> result;
  const bool inset = !panel.reusePanel.empty();
  const int textPixels = BodyTextPixels(page);
  const auto xFraction = [&](double value) {
    return panel.logX ? std::log(value / panel.xLow) /
                            std::log(panel.xHigh / panel.xLow)
                      : (value - panel.xLow) / (panel.xHigh - panel.xLow);
  };
  if (!inset && !panel.yTitle.empty() && !SharedStackYTitle(page, panel)) {
    result.push_back(TextExpectation(
        panel.yTitle, YTitleX(page, panel),
        (panel.margins[2] + 1 - panel.margins[3]) / 2,
        textPixels, 1, 23, 90));
  }
  const double frameWidth = 1 - panel.margins[0] - panel.margins[1];
  for (const auto& tick : panel.ticks) {
    const bool rotate = RotateCategoryLabels(page, panel);
    result.push_back(TextExpectation(
        tick.second, panel.margins[0] + frameWidth * xFraction(tick.first) +
            JoinedEndLabelOffset(page, panel, tick.first),
        CategoryLabelY(page, panel), inset ? 14 : textPixels, 1,
        SpeciesCategoryAxis(page) ? 21 : rotate ? 32 : 23, rotate ? 90 : 0));
  }
  for (double coordinate : StatusRailCoordinates(page, panel, pages)) {
    result.push_back(TextExpectation(
        "#times", panel.margins[0] + frameWidth * xFraction(coordinate),
        StatusRailY(page, panel), inset ? 11 : textPixels - 2,
        kGray + 2, 22));
  }
  result.push_back(TextExpectation(panel.title, PanelTitleX(panel),
                                   PanelTitleY(page, panel),
                                   inset ? 15 : textPixels + 1));
  if (page.role == "multiplicity.composite" &&
      panel.id == "upper.distribution" && panel.annotations.empty()) {
    const auto lines = P1InformationLines(page);
    for (std::size_t i = 0; i < lines.size(); ++i)
      result.push_back(TextExpectation(lines[i], P1InformationX,
                                       kP1InformationY.at(i),
                                       kP1InformationPixels.at(i)));
  }
  if (!inset && !panel.xTitle.empty() && !SharedXTitle(page) &&
      !(CategoricalAxis(page,panel) && panel.id.rfind("lower.",0)==0)) {
    const bool p1 = page.role == "multiplicity.composite";
    result.push_back(TextExpectation(
        panel.xTitle, p1 ? 1-panel.margins[1] :
            (panel.margins[0] + 1 - panel.margins[1]) / 2,
        p1 ? (inset ? .08 : .23) :
            (page.role=="spectra.signed_heavy" ? .18 : (inset ? .14 : .09)),
        inset ? 15 : textPixels, 1, p1 ? 33 : 23));
  }
  const bool drawn = PanelHasDrawing(page, panel, pages, panelIndex);
  if (!drawn) {
    result.push_back(TextExpectation(
        panel.status == "NOT_MATERIALIZED"
            ? "NOT_MATERIALIZED"
            : panel.status == "PRESENT_UNDEFINED"
                  ? "PRESENT / UNDEFINED"
            : panel.status == "PRESENT_NO_DRAWABLE_CENTER"
                  ? "PRESENT / NO REGULAR DRAW"
            : panel.logY && panel.status == "AVAILABLE"
                  ? "No positive values on logarithmic axis"
                  : "Unavailable projection",
        .5, BlankStatusY(page,panel), textPixels, 1, 22));
    if (!panel.note.empty()) {
      const auto lines=StatusNoteLines(panel.note);
      for (std::size_t i=0;i<lines.size();++i)
        result.push_back(TextExpectation(lines[i], .5,
                                         BlankNoteY(page,panel)-BlankNoteStep(page,panel)*i,
                                         std::max(12, textPixels - 3),
                                         kGray + 2, 22));
    }
  }
  for (const auto& item : panel.annotations)
    result.push_back(TextExpectation(item.text,item.x,item.y,item.size));
  const auto classTexts = InsetClassTexts(page, panel);
  result.insert(result.end(), classTexts.begin(), classTexts.end());
  const auto stateGlyphs = StateGlyphTexts(page, panel, pages);
  result.insert(result.end(), stateGlyphs.begin(), stateGlyphs.end());
  if (drawn && !panel.note.empty() &&
      !(page.role=="multiplicity.composite" &&
        (panel.id=="upper.distribution" || panel.id=="lower.ratio")) &&
      page.role.rfind("balancing.",0)!=0 &&
      page.role.rfind("correlations.",0)!=0) {
    const bool upperNote = panel.id.rfind("upper.",0)==0 ||
                           panel.id == "g9.absolute";
    const double noteY = upperNote ? .89 : .025;
    result.push_back(TextExpectation(
        panel.note, panel.margins[0], noteY,
        inset ? 11 : textPixels - 3));
  }
  return result;
}
void VerifyTexts(const TList& primitives,
                 const std::vector<ExpectedText>& expected) {
  std::vector<const TLatex*> actual;
  TIter iterator(&primitives);
  while (const auto* primitive = iterator()) {
    if (const auto* text = dynamic_cast<const TLatex*>(primitive))
      actual.push_back(text);
  }
  Need(actual.size() == expected.size(),
       "visible scientific text object set differs from drawing record");
  for (std::size_t index = 0; index < expected.size(); ++index) {
    const TLatex& text = *actual[index];
    const ExpectedText& item = expected[index];
    Need(std::string(text.GetTitle()) == item.text &&
         text.TestBit(TLatex::kTextNDC) &&
         StoredFloatClose(text.GetX(), item.x) &&
         StoredFloatClose(text.GetY(), item.y) &&
         text.GetTextFont() == 43 &&
         StoredFloatClose(text.GetTextSize(), item.size) &&
         text.GetTextColor() == item.color &&
         text.GetTextAlign() == item.align &&
         StoredFloatClose(text.GetTextAngle(), item.angle),
         "visible scientific text differs from drawing record");
  }
}
struct ExpectedLegendEntry {
  std::string label, option;
  const Series* series;
  double markerSize;
  int lineStyle;
};
struct ExpectedLegend {
  std::array<double, 4> geometry;
  int columns;
  double textSize;
  bool checkMargin;
  double margin;
  std::vector<ExpectedLegendEntry> entries;
};
std::vector<std::pair<std::string, const Series*>> PageTuneSamples(const Page& page) {
  std::vector<std::pair<std::string, const Series*>> result;
  std::set<std::string> seen;
  for (const auto& panel : page.panels) for (const auto& series : panel.series)
    if (seen.insert(series.tune).second) result.emplace_back(series.tune, &series);
  SortTuneSamples(result);
  return result;
}
const Panel* TuneLegendPanel(const Page& page) {
  // Pair-sign correlation pages identify their tune in the panel headings.
  for (const auto& panel : page.panels)
    if (panel.id.rfind("correlation.balance.", 0) == 0 ||
        panel.id.rfind("correlation.teaching.", 0) == 0) return nullptr;
  const Panel* target = nullptr;
  for (const auto& panel : page.panels) {
    if (!panel.reusePanel.empty() || panel.series.empty() ||
        panel.id.rfind("lower.", 0) == 0 || panel.id == "g9.ratio") continue;
    if (target == nullptr || panel.geometry[3] > target->geometry[3] ||
        (panel.geometry[3] == target->geometry[3] &&
         panel.geometry[0] > target->geometry[0])) target = &panel;
  }
  return target;
}
int TuneLegendTextPixels(const Page& page) {
  return BodyTextPixels(page) + (page.width > 1500 ? 2 : 0);
}
std::array<double, 4> InsideTuneLegendBox(const Page& page, const Panel& panel,
                                        std::size_t count) {
  // Keep the reference multiplicity key exactly where it was specified.
  if (page.role == "multiplicity.composite" ||
      page.role == "balancing.baryon_meson.activity") return panel.legend;
  if (panel.margins[3] > .25) {
    const double pw=page.width*(panel.geometry[2]-panel.geometry[0]);
    const double ph=page.height*(panel.geometry[3]-panel.geometry[1]);
    const double font=TuneLegendTextPixels(page);
    const double right=1-panel.margins[1]-.025;
    const double width=font*(.62*12+3.)/pw;
    const double height=1.65*font*count/ph;
    const double top=.97;
    return {right-width,top-height,right,top};
  }
  const double pixelWidth = page.width * (panel.geometry[2]-panel.geometry[0]);
  const double pixelHeight = page.height * (panel.geometry[3]-panel.geometry[1]);
  const double font = TuneLegendTextPixels(page);
  const bool correlation = page.role.rfind("correlations.",0)==0;
  const double gapX = (correlation ? 1.5 : .65)*font/pixelWidth;
  const double gapY = (correlation ? 1.25 : .65)*font/pixelHeight;
  const double left = panel.margins[0]+gapX, right = 1-panel.margins[1]-gapX;
  const double bottom = panel.margins[2]+gapY, top = 1-panel.margins[3]-gapY;
  std::size_t longest = 0;
  for (const auto& tune : PageTuneSamples(page)) longest = std::max(longest, tune.first.size());
  const double width = font*(.62*longest+3.)/pixelWidth;
  const double height = 1.65*font*count/pixelHeight;
  Need(width <= right-left && height <= top-bottom,
       "tune legend cannot fit inside scientific frame");
  const auto xNdc = [&](double value) {
    const double fraction = panel.logX ? std::log(std::max(value,panel.xLow)/panel.xLow)/
        std::log(panel.xHigh/panel.xLow) : (value-panel.xLow)/(panel.xHigh-panel.xLow);
    return panel.margins[0]+fraction*(1-panel.margins[0]-panel.margins[1]);
  };
  const auto yNdc = [&](double value) {
    const double fraction = panel.logY ? std::log(std::max(value,panel.yLow)/panel.yLow)/
        std::log(panel.yHigh/panel.yLow) : (value-panel.yLow)/(panel.yHigh-panel.yLow);
    return panel.margins[2]+fraction*(1-panel.margins[2]-panel.margins[3]);
  };
  std::vector<std::array<double, 4>> occupied;
  for (const auto& item : panel.annotations)
    occupied.push_back({item.x,item.y-.3*item.size/pixelHeight,
                       std::min(right,item.x+.56),item.y+item.size/pixelHeight});
  for (const auto& series : panel.series) for (const auto& point : series.points) {
    if (!Drawable(panel, point)) continue;
    double x1 = point.x, x2 = point.x;
    if (series.mode == "categories") { x1 -= CategoryHalfWidth(page); x2 += CategoryHalfWidth(page); }
    if (series.mode == "histogram" && std::isfinite(point.binLow) && std::isfinite(point.binHigh)) {
      x1 = point.binLow; x2 = point.binHigh;
    }
    const double error = std::isfinite(point.error) ? point.error : 0.;
    occupied.push_back({xNdc(x1)-gapX/2, yNdc(point.y-error)-gapY/2,
                        xNdc(x2)+gapX/2, yNdc(point.y+error)+gapY/2});
  }
  // Search the top-right frame first. No opaque legend may hide a curve or
  // its error interval. Only display coordinates enter this layout decision.
  for (int row = 0; row <= 20; ++row) for (int column = 0; column <= 20; ++column) {
    const double x = right-width-(right-left-width)*column/20.;
    const double y = top-height-(top-bottom-height)*row/20.;
    const std::array<double,4> box{{x,y,x+width,y+height}};
    const bool clear = std::none_of(occupied.begin(), occupied.end(), [&](const auto& data) {
      return box[0] < data[2] && box[2] > data[0] && box[1] < data[3] && box[3] > data[1];
    });
    if (clear) return box;
  }
  throw std::runtime_error("no clear in-frame tune legend position for " + page.filename);
}
void VerifyLegendEntry(const TLegendEntry& actual,
                       const ExpectedLegendEntry& expected) {
  Need(std::string(actual.GetLabel()) == expected.label &&
       std::string(actual.GetOption()) == expected.option,
       "scientific legend label/option differs from drawing record");
  const auto* sample = dynamic_cast<const TGraphErrors*>(actual.GetObject());
  const bool neutralLine = expected.option == "l";
  Need(sample != nullptr &&
       sample->GetLineColor() ==
           (neutralLine ? kBlack : Color(expected.series->color)) &&
       sample->GetMarkerColor() ==
           (neutralLine ? kBlack : Color(expected.series->color)) &&
       sample->GetMarkerStyle() == Marker(expected.series->marker) &&
       StoredFloatClose(sample->GetMarkerSize(),
                        neutralLine ? 0. : expected.markerSize) &&
       sample->GetLineStyle() == expected.lineStyle &&
       sample->GetLineWidth() ==
           (neutralLine ? ScientificLineWidth(*expected.series) : 1),
       "scientific legend sample style differs from drawing record");
}
void VerifyLegends(const TList& primitives,
                   const std::vector<ExpectedLegend>& expected) {
  std::vector<const TLegend*> actual;
  TIter iterator(&primitives);
  while (const auto* primitive = iterator()) {
    if (const auto* legend = dynamic_cast<const TLegend*>(primitive))
      actual.push_back(legend);
  }
  Need(actual.size() == expected.size(),
       "scientific legend object set differs from drawing record");
  for (std::size_t index = 0; index < expected.size(); ++index) {
    const TLegend& legend = *actual[index];
    const ExpectedLegend& item = expected[index];
    Need(StoredFloatClose(legend.GetX1NDC(), item.geometry[0]) &&
         StoredFloatClose(legend.GetY1NDC(), item.geometry[1]) &&
         StoredFloatClose(legend.GetX2NDC(), item.geometry[2]) &&
         StoredFloatClose(legend.GetY2NDC(), item.geometry[3]) &&
         legend.GetNColumns() == item.columns &&
         legend.GetBorderSize() == 0 && legend.GetFillStyle() == 0 &&
         legend.GetTextFont() == 43 &&
         StoredFloatClose(legend.GetTextSize(), item.textSize) &&
         (!item.checkMargin || StoredFloatClose(legend.GetMargin(), item.margin)),
         "scientific legend geometry/style differs from drawing record");
    std::vector<const TLegendEntry*> entries;
    TIter entryIterator(legend.GetListOfPrimitives());
    while (const auto* primitive = entryIterator()) {
      const auto* entry = dynamic_cast<const TLegendEntry*>(primitive);
      Need(entry != nullptr, "scientific legend contains a non-entry primitive");
      entries.push_back(entry);
    }
    Need(entries.size() == item.entries.size(),
         "scientific legend entry set differs from drawing record");
    for (std::size_t entryIndex = 0; entryIndex < entries.size(); ++entryIndex)
      VerifyLegendEntry(*entries[entryIndex], item.entries[entryIndex]);
  }
}
std::vector<ExpectedLegend> ExpectedPanelLegends(
    const Page& page, const Panel& panel, const std::vector<Page>& pages,
    std::size_t panelIndex) {
  if (!panel.reusePanel.empty()) return {};
  std::vector<ExpectedLegend> result;
  ExpectedLegend legend{panel.legend, 1, double(PanelLegendTextPixels(page)), true,
                        .12, {}};
  const bool sideLegend = panel.margins[1] > .3;
  if (!sideLegend) {
    legend.columns = panel.id.rfind("correlation.balance.", 0) == 0 ? 2 :
        page.role.find("kinematics.") == 0 ? 3 :
        page.role == "balancing.baryon_meson.activity" ? 2 : 1;
  }
  std::set<std::string> labels;
  const auto selected = SelectedSeries(page, panel, pages);
  for (std::size_t seriesIndex = 0; seriesIndex < selected.size(); ++seriesIndex) {
    const Series* series = selected[seriesIndex];
    if (!ExpectedGraphs(page, panel, *series, panelIndex, seriesIndex).empty() &&
        !series->legendLabel.empty() && series->legendLabel != series->tune &&
        labels.insert(series->legendLabel).second) {
      legend.entries.push_back({series->legendLabel, "lp", series, 1.4,
                                series->lineStyle});
    }
  }
  if (!legend.entries.empty()) result.push_back(std::move(legend));
  if (TuneLegendPanel(page) == &panel) {
    const auto tunes = PageTuneSamples(page);
    if (!tunes.empty()) {
      ExpectedLegend key{InsideTuneLegendBox(page, panel, tunes.size()), 1,
                         double(TuneLegendTextPixels(page)), true, .12, {}};
      for (const auto& tune : tunes)
        key.entries.push_back({tune.first, "lp", tune.second, 1.4, 1});
      result.push_back(std::move(key));
    }
  }
  return result;
}

std::vector<ExpectedLegend> ExpectedCanvasLegends(const Page& page) {
  std::vector<ExpectedLegend> result;
  const int textPixels = BodyTextPixels(page);
  std::map<int, const Series*> classSamples;
  for (const auto& panel : page.panels) for (const auto& series : panel.series)
    classSamples.emplace(series.lineStyle, &series);
  if (page.role.find("balancing.activity.") == 0 && !classSamples.empty()) {
    ExpectedLegend legend{{.05, ClassLegendBottom(classSamples.size()),
                           .99, .925},
                          ClassLegendColumns(classSamples.size()),
                          double(textPixels), true, .64, {}};
    for (const auto& item : classSamples) {
      legend.entries.push_back(
          {item.second->label, "l", item.second,
           ScientificMarkerSize(*item.second, false), item.second->lineStyle});
    }
    result.push_back(std::move(legend));
  }
  return result;
}
std::vector<ExpectedText> ClassKeyTexts(const Page& page) {
  (void)page;
  return {};
}
std::string LogBoundaryLabel(double value) {
  const int exponent=static_cast<int>(std::floor(std::log10(value)+1.e-12));
  const double coefficient=value/std::pow(10.,exponent);
  if (std::abs(coefficient-1.)<1.e-10) return "10^{"+std::to_string(exponent)+"}";
  std::ostringstream text;
  text << std::setprecision(4) << coefficient << "#times10^{" << exponent << "}";
  return text.str();
}
std::vector<ExpectedText> CanvasSupplementTexts(const Page& page) {
  std::vector<ExpectedText> result;
  // Paint seam labels on the canvas so an adjacent pad cannot clip them.
  for (const Panel& panel : page.panels) {
    const double width=panel.geometry[2]-panel.geometry[0];
    const double height=panel.geometry[3]-panel.geometry[1];
    const double x=panel.geometry[0]+width*(panel.margins[0]-.008);
    if (page.role=="multiplicity.composite" && panel.id=="lower.ratio")
      result.push_back(TextExpectation("5",x,
          panel.geometry[3]-height*panel.margins[3],BodyTextPixels(page),1,32));
    if (page.role.rfind("correlations.",0)==0 && panel.logY &&
        panel.margins[2]==0. && !SharedRightAxis(panel))
      result.push_back(TextExpectation(LogBoundaryLabel(panel.yLow),x,
          panel.geometry[1],BodyTextPixels(page),1,32));
  }
  if (page.role.rfind("balancing.",0)==0 ||
      page.role.rfind("correlations.",0)==0) {
    const bool teaching=std::any_of(page.panels.begin(),page.panels.end(),
        [](const Panel& panel) {
          return panel.id.rfind("correlation.teaching.",0)==0 &&
                 panel.uncertaintyDisplay=="CENTERS_ONLY";
        });
    bool exactZero=false, withheld=false;
    for (const Panel& panel : page.panels)
      for (const Series& series : panel.series)
        for (const Point& point : series.points) {
          if (point.state!="DRAW") continue;
          exactZero |= point.uncertaintyStatus=="AVAILABLE_ZERO_DISPERSION";
          withheld |= !std::isfinite(point.error);
        }
    std::string note;
    if (teaching) {
      const std::string disclosure=
          "Statistical errors omitted for display; K10 errors and covariance "
          "saved in ROOT";
      Need(page.information.size()>=disclosure.size() &&
           page.information.compare(page.information.size()-disclosure.size(),
                                    disclosure.size(),disclosure)==0,
           "centers-only teaching disclosure absent");
      note=disclosure;
    } else if (exactZero) {
      note="Exact-zero SE saved in ROOT";
    }
    if (withheld) note += (note.empty() ? "" : "; ") +
        std::string(page.role.rfind("balancing.", 0) == 0 &&
                    page.scientificHeader.empty() ?
                    "SE unavailable for unresolved ratios; see ROOT flags" :
                    "? = withheld SE");
    if (!note.empty())
      result.push_back(TextExpectation(
          note,.015,.045,teaching ? BodyTextPixels(page) : 18,kGray+2));
  }
  if (page.role=="multiplicity.composite") {
    if (page.scientificHeader.empty()) {
      const auto ratio=std::find_if(page.panels.begin(),page.panels.end(),
          [](const Panel& item){return item.id=="lower.ratio";});
      if (ratio!=page.panels.end() && !ratio->note.empty()) {
        Need(ratio->note==kP1WithheldSeDisclosure,
             "paper P1 withheld-SE disclosure differs");
        if (page.panels.front().annotations.empty())
          result.push_back(TextExpectation(ratio->note,.015,.015,14,kGray+2));
      }
      return result;
    }
    const auto parent=std::find_if(page.panels.begin(),page.panels.end(),
        [](const Panel& item){return item.id=="upper.distribution";});
    if (parent!=page.panels.end() && !parent->note.empty())
      result.push_back(TextExpectation(parent->note,.015,.055,16));
    const auto ratio=std::find_if(page.panels.begin(),page.panels.end(),
        [](const Panel& item){return item.id=="lower.ratio";});
    if (ratio!=page.panels.end() && !ratio->note.empty())
      result.push_back(TextExpectation(ratio->note,.015,.035,16));
  }
  double stackBottom=1., stackTop=0., titleX=0.;
  std::string stackTitle;
  for (const auto& panel : page.panels) {
    if (!SharedStackYTitle(page,panel) || panel.yTitle.empty()) continue;
    Need(stackTitle.empty() || stackTitle==panel.yTitle,
         "shared y title differs across tune rows");
    stackTitle=panel.yTitle;
    const double height=panel.geometry[3]-panel.geometry[1];
    stackBottom=std::min(stackBottom,panel.geometry[1]+height*panel.margins[2]);
    stackTop=std::max(stackTop,panel.geometry[3]-height*panel.margins[3]);
    titleX=panel.geometry[0]+YTitleX(page,panel)*(panel.geometry[2]-panel.geometry[0]);
  }
  if (!stackTitle.empty())
    result.push_back(TextExpectation(stackTitle,titleX,(stackBottom+stackTop)/2,
                                     BodyTextPixels(page),1,23,90));
  if (SharedXTitle(page)) {
    double low=1., high=0., frameY=1.;
    std::string title;
    for (const Panel& panel : page.panels) {
      if (panel.xTitle.empty()) continue;
      Need(title.empty() || title==panel.xTitle,
           "shared x title differs across panels");
      title=panel.xTitle;
      const double width=panel.geometry[2]-panel.geometry[0];
      const double height=panel.geometry[3]-panel.geometry[1];
      low=std::min(low,panel.geometry[0]+width*panel.margins[0]);
      high=std::max(high,panel.geometry[2]-width*panel.margins[1]);
      frameY=std::min(frameY,panel.geometry[1]+height*panel.margins[2]);
    }
    if (!title.empty()) {
      const double y=page.role.rfind("correlations.",0)==0 ?
          frameY-2.8*BodyTextPixels(page)/page.height : CategoricalXTitleY(page);
      result.push_back(TextExpectation(title,(low+high)/2,y,
                                       BodyTextPixels(page),1,23));
    }
  }
  for (const Panel& panel : page.panels) {
    if (panel.id.rfind("lower.",0)!=0 ||
        !CategoricalAxis(page,panel) || panel.xTitle.empty() ||
        SharedXTitle(page)) continue;
    const double center=panel.geometry[0]+
        (panel.geometry[2]-panel.geometry[0])*
        (panel.margins[0]+1-panel.margins[1])/2;
    result.push_back(TextExpectation(panel.xTitle,center,
        CategoricalXTitleY(page),
        BodyTextPixels(page),1,23));
  }
  if (page.role=="spectra.signed_heavy") {
    Need(!page.title.empty(), "G9 visible signed-species title is absent");
    result.push_back(TextExpectation(page.title,.16,.95,22));
    std::size_t start=0,index=0;
    while (start<page.information.size() && page.panels.front().annotations.empty()) {
      const auto split=page.information.find("; ",start);
      result.push_back(TextExpectation(page.information.substr(start,
          split==std::string::npos ? split : split-start),
          .16,.10-.025*index,18));
      if (split==std::string::npos) break;
      start=split+2; ++index;
    }
  }
  return result;
}
std::set<int> BandColors(const TPad& pad) {
  std::set<int> colors;
  TIter next(pad.GetListOfPrimitives());
  while (auto* object = next()) {
    if (auto* child = dynamic_cast<TPad*>(object)) {
      const auto nested = BandColors(*child);
      colors.insert(nested.begin(), nested.end());
    } else if (auto* graph = dynamic_cast<TGraphErrors*>(object)) {
      if (std::string(graph->GetTitle()).rfind("band:", 0) == 0)
        colors.insert(graph->GetFillColor());
    }
  }
  return colors;
}
std::string BandAlphaCommand(const TPad& pad) {
  std::ostringstream command;
  for (const int color : BandColors(pad))
    command << "gROOT->GetColor(" << color << ")->SetAlpha(0.12f);";
  return command.str();
}
void WriteCanvas(TCanvas& canvas, const std::string& name) {
  // ROOT 6.30 omits unchanged palettes and drops alpha when reading them.
  // Carry the palette explicitly. The first paint restores only band opacity.
  TColor::DefinedColors();
  auto* colors = gROOT->GetListOfColors();
  TExec alpha("band_alpha", BandAlphaCommand(canvas).c_str());
  canvas.GetListOfPrimitives()->AddFirst(&alpha);
  canvas.GetListOfPrimitives()->Add(colors);
  const auto written = canvas.Write(name.c_str());
  canvas.GetListOfPrimitives()->Remove(colors);
  canvas.GetListOfPrimitives()->Remove(&alpha);
  Need(written > 0, "cannot write named TCanvas");
}
void VerifyBandAlpha(const TCanvas& canvas) {
  const auto* alpha = dynamic_cast<TExec*>(
      canvas.GetListOfPrimitives()->First());
  Need(alpha && std::string(alpha->GetName()) == "band_alpha" &&
       alpha->GetTitle() == BandAlphaCommand(canvas),
       "canvas band-opacity restoration differs");
  // Validate the stored paint command without evaluating arbitrary ROOT code.
  for (const int index : BandColors(canvas)) {
    auto* color = gROOT->GetColor(index);
    Need(color != nullptr, "canvas band color is absent");
    color->SetAlpha(.12f);
  }
}
void VerifyCanvasArchive(const std::filesystem::path& output,
                         const std::filesystem::path& record,
                         const std::vector<Page>& pages) {
  TFile archive((output / "canvases.root").string().c_str(), "READ");
  Need(!archive.IsZombie(), "cannot reopen canvas archive");
  std::set<std::string> expected{"drawing_record"}, observed;
  for (const auto& page : pages) expected.insert(CanvasName(page));
  TIter iterator(archive.GetListOfKeys());
  while (const auto* object = iterator()) {
    const auto* key = dynamic_cast<const TKey*>(object);
    Need(key != nullptr && key->GetCycle() == 1 &&
         observed.insert(key->GetName()).second,
         "canvas archive duplicate key/cycle");
  }
  Need(observed == expected, "canvas archive exact object set differs");
  const auto* archivedRecord =
      dynamic_cast<TObjString*>(archive.Get("drawing_record"));
  Need(archivedRecord != nullptr &&
       archivedRecord->GetString().Data() == ReadBytes(record),
       "canvas archive drawing record differs");
  for (const auto& page : pages) {
    const std::string name = CanvasName(page);
    const auto* canvas = dynamic_cast<TCanvas*>(archive.Get(name.c_str()));
    Need(canvas != nullptr, "named TCanvas is absent from archive");
    VerifyBandAlpha(*canvas);
    const auto* identity = dynamic_cast<TNamed*>(
        canvas->GetListOfPrimitives()->FindObject("drawing_identity"));
    Need(identity != nullptr &&
         identity->GetTitle() == PageIdentity(page),
         "TCanvas identities/values/statuses differ from drawing record");
    Need(canvas->GetTitle() == page.role,
         "TCanvas role differs from drawing record");
    std::set<std::string> expectedPads, observedPads;
    for (std::size_t panelIndex = 0; panelIndex < page.panels.size();
         ++panelIndex) {
      const Panel& panel = page.panels[panelIndex];
      const std::string padName = PadName(panelIndex, panel);
      expectedPads.insert(padName);
      const auto* pad = dynamic_cast<TPad*>(
          canvas->GetListOfPrimitives()->FindObject(padName.c_str()));
      Need(pad != nullptr && pad->GetTitle() == panel.id,
           "named scientific TPad is absent or differs");
      Need(StoredFloatClose(pad->GetXlowNDC(), panel.geometry[0]) &&
           StoredFloatClose(pad->GetYlowNDC(), panel.geometry[1]) &&
           StoredFloatClose(pad->GetWNDC(), panel.geometry[2] - panel.geometry[0]) &&
           StoredFloatClose(pad->GetHNDC(), panel.geometry[3] - panel.geometry[1]) &&
           StoredFloatClose(pad->GetLeftMargin(), panel.margins[0]) &&
           StoredFloatClose(pad->GetRightMargin(), panel.margins[1]) &&
           StoredFloatClose(pad->GetBottomMargin(), panel.margins[2]) &&
           StoredFloatClose(pad->GetTopMargin(), panel.margins[3]) &&
           pad->GetLogx() == panel.logX && pad->GetLogy() == panel.logY &&
           pad->GetTickx() == 1 && pad->GetTicky() == 1 &&
           pad->GetFillColor() == 0 && pad->GetBorderMode() == 0,
           "scientific TPad geometry/style differs from drawing record");
      const auto* frame = dynamic_cast<TH1F*>(
          pad->GetListOfPrimitives()->FindObject(FrameName(panelIndex).c_str()));
      Need(frame != nullptr && std::string(frame->GetTitle()).empty() &&
           Close(frame->GetXaxis()->GetXmin(), panel.xLow) &&
           Close(frame->GetXaxis()->GetXmax(), panel.xHigh) &&
           Close(frame->GetMinimum(), panel.yLow) &&
           Close(frame->GetMaximum(), panel.yHigh),
           "scientific frame ranges differ from drawing record");
      std::set<std::string> observedHistograms;
      std::size_t framePrimitiveCount = 0;
      TIter topologyIterator(pad->GetListOfPrimitives());
      while (const auto* primitive = topologyIterator()) {
        const std::string className = primitive->IsA()->GetName();
        Need(className == "TFrame" || className == "TH1F" ||
             className == "TGraphErrors" || className == "TLatex" ||
             className == "TLegend" || className == "TLine",
             "scientific TPad primitive class differs from drawing record");
        if (className == "TFrame") ++framePrimitiveCount;
        if (className == "TH1F")
          Need(observedHistograms.insert(primitive->GetName()).second,
               "scientific frame object set differs from drawing record");
      }
      Need(framePrimitiveCount == 1 &&
           observedHistograms == std::set<std::string>{
               FrameName(panelIndex), FrameName(panelIndex) + "_copy"},
           "scientific frame object set differs from drawing record");
      const bool inset = !panel.reusePanel.empty();
      if (inset)
        Need(pad->GetFillColor() == 0 && pad->GetFillStyle() == 4000 &&
             pad->GetFrameFillColor() == kWhite &&
             pad->GetFrameFillStyle() == 1001 &&
             pad->GetFrameLineWidth() == 1,
             "percentile inset transparent margin/white frame differs");
      const int textPixels = BodyTextPixels(page);
      const double baseLabelSize = inset ? .055 : textPixels;
      const double expectedXLabelSize =
          (panel.xTitle.empty() || !panel.ticks.empty()) ? 0 : baseLabelSize;
      const bool categoricalAxis = CategoricalAxis(page, panel);
      const bool p1MainAxis = page.role == "multiplicity.composite" &&
          (panel.id == "upper.distribution" || panel.id == "lower.ratio");
      const auto yLabelPolicy = JoinedYAxisLabelPolicy(page, panel, inset);
      const int expectedXDivisions = p1MainAxis ? 507 : inset ? 510 : 505;
      const bool xDivisionsMatch = categoricalAxis
          ? frame->GetXaxis()->GetNdivisions() % 1000000 == 0
          : frame->GetXaxis()->GetNdivisions() % 1000000 ==
                expectedXDivisions;
      if (!xDivisionsMatch) {
        throw std::runtime_error(
            "scientific frame x-axis divisions differ from drawing record: observed=" +
            std::to_string(frame->GetXaxis()->GetNdivisions()) +
            ", expected=" + std::to_string(
                categoricalAxis ? 0 : expectedXDivisions));
      }
      Need(frame->GetXaxis()->GetLabelFont() == (inset ? 42 : 43) &&
           frame->GetYaxis()->GetLabelFont() == (inset ? 42 : 43) &&
           frame->GetXaxis()->GetTitleFont() == (inset ? 42 : 43) &&
           frame->GetYaxis()->GetTitleFont() == (inset ? 42 : 43) &&
           StoredFloatClose(frame->GetXaxis()->GetLabelSize(), expectedXLabelSize) &&
           StoredFloatClose(frame->GetYaxis()->GetLabelSize(),
                            SharedRightAxis(panel) ? 0. : baseLabelSize) &&
           StoredFloatClose(frame->GetXaxis()->GetTitleSize(), inset ? .062 : textPixels) &&
           StoredFloatClose(frame->GetYaxis()->GetTitleSize(), inset ? .060 : textPixels) &&
           frame->GetYaxis()->GetNdivisions() % 1000000 ==
               (page.role == "multiplicity.composite" &&
                panel.id == "upper.distribution" ? 509 : inset ? 503 : 505) &&
           frame->GetYaxis()->GetMoreLogLabels() ==
             (!inset && panel.logY && panel.yHigh / panel.yLow < 10.) &&
           frame->GetYaxis()->GetNoExponent() ==
             BeautyCorrelationUsesFullTickValues(page, panel) &&
           AxisLabelSuppressed(*frame->GetYaxis(), 1) ==
             yLabelPolicy.suppressFirst &&
           AxisLabelSuppressed(*frame->GetYaxis(), -1) ==
             yLabelPolicy.suppressLast &&
           (page.role != "multiplicity.composite" ||
            StoredFloatClose(frame->GetXaxis()->GetTickLength(),
                p1MainAxis ? .025 : .03)) &&
           (!categoricalAxis ||
            StoredFloatClose(frame->GetXaxis()->GetTickLength(), 0.)) &&
           StoredFloatClose(frame->GetXaxis()->GetTitleOffset(), inset ? 1.02 : 1.25) &&
           StoredFloatClose(frame->GetYaxis()->GetTitleOffset(), inset ? 1.05 : 1.6) &&
           std::string(frame->GetXaxis()->GetTitle()) == (inset ? panel.xTitle : "") &&
           std::string(frame->GetYaxis()->GetTitle()) == (inset ? panel.yTitle : ""),
           "scientific frame axis style differs from drawing record");
      std::map<std::string, const ExpectedGraph*> expectedGraphs;
      const auto selected = SelectedSeries(page, panel, pages);
      std::vector<std::vector<ExpectedGraph>> expectedStorage;
      expectedStorage.reserve(selected.size());
      for (std::size_t seriesIndex = 0; seriesIndex < selected.size(); ++seriesIndex) {
        expectedStorage.push_back(ExpectedGraphs(
            page, panel, *selected[seriesIndex], panelIndex, seriesIndex));
        for (const ExpectedGraph& graph : expectedStorage.back()) {
          Need(expectedGraphs.emplace(graph.name, &graph).second,
               "duplicate expected scientific graph name");
        }
      }
      std::set<std::string> observedGraphs;
      TIter primitiveIterator(pad->GetListOfPrimitives());
      while (const auto* primitive = primitiveIterator()) {
        const auto* graph = dynamic_cast<const TGraphErrors*>(primitive);
        if (graph == nullptr) continue;
        const auto found = expectedGraphs.find(graph->GetName());
        Need(found != expectedGraphs.end() &&
             observedGraphs.insert(graph->GetName()).second,
             "scientific graph object set differs from drawing record");
        VerifyGraph(*graph, *found->second, inset);
        std::string drawOption = primitiveIterator.GetOption();
        std::transform(drawOption.begin(), drawOption.end(), drawOption.begin(),
                       [](unsigned char c) { return std::tolower(c); });
        const auto same = drawOption.find("same");
        if (same != std::string::npos) drawOption.erase(same, 4);
        drawOption.erase(std::remove_if(drawOption.begin(), drawOption.end(),
                         [](unsigned char c) { return std::isspace(c); }),
                         drawOption.end());
        const bool errorGraph = found->second->title.rfind("points:", 0) == 0;
        const bool band = found->second->title.rfind("band:", 0) == 0;
        const bool markers = found->second->title.rfind("dense_markers:", 0) == 0;
        const std::string expectedOption = band ? "3" : errorGraph ?
            (panel.uncertaintyDisplay == "CENTERS_ONLY" ? "px" :
             inset || found->second->dense ? "px" : "pz") :
            markers ? "p" : "l";
        Need(drawOption == expectedOption,
             "scientific uncertainty drawing option differs from drawing record");
      }
      Need(observedGraphs.size() == expectedGraphs.size(),
           "scientific graph object set differs from drawing record");
      std::vector<const TLine*> actualGuides;
      TIter guideIterator(pad->GetListOfPrimitives());
      while (const auto* primitive = guideIterator()) {
        if (const auto* line = dynamic_cast<const TLine*>(primitive))
          actualGuides.push_back(line);
      }
      std::vector<const Guide*> expectedGuides;
      for (const auto& guide : panel.guides) {
        if (inset && guide.id.rfind("class.", 0) == 0 &&
            guide.x1 < panel.xLow) continue;
        if (!(guide.x2 < panel.xLow || guide.x1 > panel.xHigh))
          expectedGuides.push_back(&guide);
      }
      const auto boundaries = categoricalAxis ? CategoryBoundaries(panel) :
          std::vector<double>{};
      const std::size_t dividers = panel.categoryDividers && boundaries.size() > 1 ?
          boundaries.size() - 2 : 0;
      Need(actualGuides.size() == expectedGuides.size() +
           2 * boundaries.size() + dividers,
           "scientific guide object set differs from drawing record");
      for (std::size_t index = 0; index < boundaries.size(); ++index) {
        const std::size_t start = 2 * index +
            (panel.categoryDividers && index > 0 ? index - 1 : 0);
        for (int side = 0; side < 2; ++side) {
          const TLine& tick = *actualGuides[start + side];
          const bool top = side == 1;
          Need(SameBinary64(tick.GetX1(), boundaries[index]) &&
               SameBinary64(tick.GetX2(), boundaries[index]) &&
               SameBinary64(tick.GetY1(), top ? panel.yHigh : panel.yLow) &&
               SameBinary64(tick.GetY2(), CategoryTickInnerY(page, panel, top)) &&
               tick.GetLineColor() == kBlack &&
               tick.GetLineStyle() == 1 && tick.GetLineWidth() == 1,
               "categorical boundary tick geometry differs");
        }
        if (panel.categoryDividers && index > 0 &&
            index + 1 < boundaries.size()) {
          const TLine& divider = *actualGuides[start + 2];
          Need(SameBinary64(divider.GetX1(), boundaries[index]) &&
               SameBinary64(divider.GetX2(), boundaries[index]) &&
               SameBinary64(divider.GetY1(), panel.yLow) &&
               SameBinary64(divider.GetY2(), panel.yHigh) &&
               divider.GetLineColor() == kGray+1 &&
               divider.GetLineStyle() == 7 && divider.GetLineWidth() == 1,
               "categorical boundary divider geometry differs");
        }
      }
      for (std::size_t guideIndex = 0; guideIndex < expectedGuides.size();
           ++guideIndex) {
        const TLine& actual = *actualGuides[
            2 * boundaries.size() + dividers + guideIndex];
        const Guide& guide = *expectedGuides[guideIndex];
        const bool insetClass = page.role == "multiplicity.composite" &&
            panel.id == "inset.monash_boundaries" &&
            guide.id.rfind("class.", 0) == 0;
        Need(SameBinary64(actual.GetX1(), guide.x1) &&
             SameBinary64(actual.GetX2(),
                 insetClass ? guide.x1 : guide.x2) &&
             SameBinary64(actual.GetY1(), guide.y1) &&
             SameBinary64(actual.GetY2(), guide.y2) &&
             actual.GetLineColor() == Color(guide.color) &&
             actual.GetLineStyle() == guide.style &&
             actual.GetLineWidth() == 1,
             "scientific guide coordinates/style differ from drawing record");
      }
      VerifyTexts(*pad->GetListOfPrimitives(),
                  ExpectedPanelTexts(page, panel, pages, panelIndex));
      VerifyLegends(*pad->GetListOfPrimitives(),
                    ExpectedPanelLegends(page, panel, pages, panelIndex));
    }
    std::size_t identityCount = 0;
    std::size_t observedPadCount = 0;
    TIter canvasIterator(canvas->GetListOfPrimitives());
    while (const auto* primitive = canvasIterator()) {
      const std::string className = primitive->IsA()->GetName();
      Need(className == "TPad" || className == "TLatex" ||
           className == "TLegend" || className == "TNamed" ||
           className == "TExec",
           "TCanvas primitive class differs from drawing record");
      const auto* pad = dynamic_cast<const TPad*>(primitive);
      if (pad != nullptr) {
        ++observedPadCount;
        Need(observedPads.insert(pad->GetName()).second,
             "scientific TPad object set differs from drawing record");
      }
      if (className == "TNamed") {
        Need(std::string(primitive->GetName()) == "drawing_identity",
             "TCanvas named primitive set differs from drawing record");
        ++identityCount;
      }
      if (className == "TExec")
        Need(primitive == canvas->GetListOfPrimitives()->First(),
             "unexpected canvas executable primitive");
    }
    Need(observedPads == expectedPads,
         "scientific TPad object set differs from drawing record");
    Need(observedPadCount == page.panels.size(),
         "scientific TPad object count differs from drawing record");
    Need(identityCount == 1,
         "TCanvas named primitive set differs from drawing record");
    std::vector<ExpectedText> canvasTexts;
    if (!page.scientificHeader.empty())
      canvasTexts.push_back(TextExpectation(page.scientificHeader,
          .015,.015,std::max(11, BodyTextPixels(page)-4), kGray+2));
    const auto classKey = ClassKeyTexts(page);
    canvasTexts.insert(canvasTexts.end(), classKey.begin(), classKey.end());
    const auto supplements = CanvasSupplementTexts(page);
    canvasTexts.insert(canvasTexts.end(), supplements.begin(), supplements.end());
    VerifyTexts(*canvas->GetListOfPrimitives(), canvasTexts);
    VerifyLegends(*canvas->GetListOfPrimitives(), ExpectedCanvasLegends(page));
  }
}
void Text(double x, double y, const std::string& label, int pixels, int color = 1) {
  TLatex text;
  text.SetNDC(); text.SetTextFont(43); text.SetTextSize(pixels);
  text.SetTextColor(color); text.SetLineWidth(1);
  text.DrawLatex(x, y, label.c_str());
}
void LineStyle(int style) {
  // ROOT PDF converts quarter-point pattern lengths to integer points.
  // Multiples of four keep every dash/gap nonzero in small printed legends.
  // Integer style identity still follows the authenticated 1 + class_id rule.
  static const std::array<const char*, 11> patterns = {{
    "80 8", "40 12", "24 8 12 8 4 8", "24 8 4 8 4 8", "12 8", "4 8",
    "40 8 12 8", "12 8 4 8", "4 16", "24 8 4 8", "4 20"}};
  if (style >= 2 && style <= 12) gStyle->SetLineStyleString(style,patterns[style-2]);
  if (style > 12) {
    std::string pattern = "40 12";
    for (int i=0; i<style-12; ++i) pattern += " 4 12";
    gStyle->SetLineStyleString(style,pattern.c_str());
  }
}
void Style(TGraphErrors& graph, const Series& series, bool dense) {
  graph.SetLineColor(Color(series.color)); graph.SetMarkerColor(Color(series.color));
  graph.SetMarkerStyle(Marker(series.marker));
  graph.SetMarkerSize(ScientificMarkerSize(series, dense));
  LineStyle(series.lineStyle);
  graph.SetLineStyle(series.lineStyle);
  graph.SetLineWidth(ScientificLineWidth(series));
}
void DrawPage(const Page& page, const std::filesystem::path& output,
              const std::vector<Page>& pages, TFile& archive) {
  const std::string canvasName = CanvasName(page);
  const int textPixels = BodyTextPixels(page);
  TCanvas canvas(canvasName.c_str(), page.role.c_str(), page.width, page.height);
  canvas.SetCanvasSize(page.width, page.height);
  // ROOT's PDF driver places the canvas on the requested physical paper.
  // Pixel dimensions only set aspect ratio; treating 100 px as one inch
  // clips every wide manuscript panel at the default A4 boundary.
  gStyle->SetPaperSize(kPaperWidthCentimeters,
                       kPaperWidthCentimeters * page.height / page.width);
  // Destroy owned primitives before their canvas; ROOT removes pad references.
  std::vector<std::unique_ptr<TPad>> pads;
  std::vector<std::unique_ptr<TGraphErrors>> graphs;
  std::vector<std::unique_ptr<TLine>> lines;
  std::vector<std::unique_ptr<TLegend>> legends;
  canvas.SetFillColor(0);
  for (std::size_t index = 0; index < page.panels.size(); ++index) {
    const Panel& panel = page.panels[index];
    const bool inset = !panel.reusePanel.empty();
    const auto& g = panel.geometry;
    const std::string padName = PadName(index, panel);
    pads.emplace_back(std::make_unique<TPad>(padName.c_str(), panel.id.c_str(),
                                             g[0],g[1],g[2],g[3]));
    TPad& pad = *pads.back();
    pad.SetFillColor(0); pad.SetBorderMode(0); pad.SetTicks(1,1);
    if (inset) {
      // Keep the outer inset margin transparent so it cannot mask the parent
      // y axis.  The plotted frame itself stays white, preventing the two
      // spectra and their axis systems from being superimposed.
      pad.SetFillColor(0); pad.SetFillStyle(4000);
      pad.SetFrameFillColor(kWhite); pad.SetFrameFillStyle(1001);
      pad.SetFrameLineWidth(1);
    }
    pad.SetLeftMargin(panel.margins[0]); pad.SetRightMargin(panel.margins[1]);
    pad.SetBottomMargin(panel.margins[2]); pad.SetTopMargin(panel.margins[3]);
    pad.SetLogy(panel.logY); pad.SetLogx(panel.logX); pad.Draw(); pad.cd();
    const auto xFraction = [&](double value) {
      return panel.logX ? std::log(value/panel.xLow)/std::log(panel.xHigh/panel.xLow)
                        : (value-panel.xLow)/(panel.xHigh-panel.xLow);
    };
    TH1F* frame = pad.DrawFrame(panel.xLow, panel.yLow, panel.xHigh, panel.yHigh);
    frame->SetName(FrameName(index).c_str());
    frame->SetTitle(""); frame->SetStats(false);
    for (TAxis* axis : {frame->GetXaxis(), frame->GetYaxis()}) {
      axis->SetLabelFont(inset ? 42 : 43); axis->SetTitleFont(inset ? 42 : 43);
      axis->SetLabelSize(inset ? .055 : textPixels);
      axis->SetTitleSize(inset ? .062 : textPixels);
      axis->SetNdivisions(505); axis->SetMaxDigits(4);
      axis->SetTitleOffset(inset ? 1.02 : 1.25);
    }
    frame->GetYaxis()->SetMoreLogLabels(
        !inset && panel.logY && panel.yHigh / panel.yLow < 10.);
    if (SharedRightAxis(panel)) frame->GetYaxis()->SetLabelSize(0.);
    if (BeautyCorrelationUsesFullTickValues(page, panel))
      frame->GetYaxis()->SetNoExponent(true);
    const auto yLabelPolicy = JoinedYAxisLabelPolicy(page, panel, inset);
    if (yLabelPolicy.suppressFirst)
      frame->GetYaxis()->ChangeLabel(1, -1., 0.);
    if (yLabelPolicy.suppressLast)
      frame->GetYaxis()->ChangeLabel(-1, -1., 0.);
    if (page.role == "multiplicity.composite") {
      const bool mainAxis = panel.id == "upper.distribution" ||
          panel.id == "lower.ratio";
      if (mainAxis) frame->GetXaxis()->SetNdivisions(507);
      if (panel.id == "upper.distribution")
        frame->GetYaxis()->SetNdivisions(509);
      frame->GetXaxis()->SetTickLength(
          mainAxis ? .025 : .03);
    }
    if (CategoricalAxis(page, panel)) {
      // Draw only category boundary ticks, never center or minor ticks.
      frame->GetXaxis()->SetNdivisions(0, false);
      frame->GetXaxis()->SetTickLength(0);
    }
    frame->GetXaxis()->SetTitle("");
    if (panel.xTitle.empty()) frame->GetXaxis()->SetLabelSize(0);
    frame->GetYaxis()->SetTitleOffset(1.6);
    frame->GetYaxis()->SetTitle("");
    if (inset) {
      frame->GetXaxis()->SetTitle(panel.xTitle.c_str());
      frame->GetYaxis()->SetTitle(panel.yTitle.c_str());
      frame->GetXaxis()->SetNdivisions(510);
      frame->GetYaxis()->SetNdivisions(503);
      frame->GetYaxis()->SetTitleSize(.060);
      frame->GetYaxis()->SetTitleOffset(1.05);
    }
    if (!inset && !panel.yTitle.empty() && !SharedStackYTitle(page, panel)) {
      TLatex label; label.SetNDC(); label.SetTextFont(43); label.SetTextSize(textPixels);
      label.SetLineWidth(1);
      label.SetTextAngle(90); label.SetTextAlign(23);
      label.DrawLatex(YTitleX(page, panel),
                      (panel.margins[2]+1-panel.margins[3])/2,panel.yTitle.c_str());
    }
    if (!panel.ticks.empty()) {
      frame->GetXaxis()->SetLabelSize(0);
      const double frameWidth = 1 - panel.margins[0] - panel.margins[1];
      for (const auto& tick : panel.ticks) {
        const bool rotate = RotateCategoryLabels(page, panel);
        TLatex label; label.SetNDC(); label.SetTextFont(43);
        label.SetLineWidth(1);
        label.SetTextSize(inset ? 14 : textPixels);
        label.SetTextAngle(rotate ? 90 : 0);
        label.SetTextAlign(SpeciesCategoryAxis(page) ? 21 : rotate ? 32 : 23);
        const double x = panel.margins[0] + frameWidth * xFraction(tick.first) +
            JoinedEndLabelOffset(page, panel, tick.first);
        label.DrawLatex(x, CategoryLabelY(page, panel), tick.second.c_str());
      }
    }
    if (CategoricalAxis(page, panel)) {
      for (double boundary : CategoryBoundaries(panel)) {
        for (int side = 0; side < 2; ++side) {
          const bool top = side == 1;
          lines.emplace_back(std::make_unique<TLine>(
              boundary, top ? panel.yHigh : panel.yLow,
              boundary, CategoryTickInnerY(page, panel, top)));
          lines.back()->SetLineColor(kBlack);
          lines.back()->SetLineStyle(1);
          lines.back()->SetLineWidth(1);
          lines.back()->Draw();
        }
        if (panel.categoryDividers && boundary > panel.xLow &&
            boundary < panel.xHigh) {
          lines.emplace_back(std::make_unique<TLine>(
              boundary, panel.yLow, boundary, panel.yHigh));
          lines.back()->SetLineColor(kGray+1);
          LineStyle(7);
          lines.back()->SetLineStyle(7);
          lines.back()->SetLineWidth(1);
          lines.back()->Draw();
        }
      }
    }
    const std::vector<const Series*> selected = SelectedSeries(page, panel, pages);
    const double frameWidth = 1 - panel.margins[0] - panel.margins[1];
    for (double coordinate : StatusRailCoordinates(page, panel, pages)) {
      TLatex status; status.SetNDC(); status.SetTextFont(43);
      status.SetTextSize(inset ? 11 : textPixels - 2);
      status.SetTextColor(kGray + 2); status.SetTextAlign(22);
      status.DrawLatex(panel.margins[0] + frameWidth * xFraction(coordinate),
                       StatusRailY(page, panel), "#times");
    }
    Text(PanelTitleX(panel), PanelTitleY(page, panel), panel.title,
         inset ? 15 : textPixels + 1);
    if (page.role == "multiplicity.composite" &&
        panel.id == "upper.distribution" && panel.annotations.empty()) {
      const auto lines = P1InformationLines(page);
      for (std::size_t i = 0; i < lines.size(); ++i)
        Text(P1InformationX, kP1InformationY.at(i), lines[i],
             kP1InformationPixels.at(i));
    }
    if (!inset && !panel.xTitle.empty() && !SharedXTitle(page) &&
        !(CategoricalAxis(page,panel) && panel.id.rfind("lower.",0)==0)) {
      TLatex label; label.SetNDC(); label.SetTextFont(43);
      label.SetLineWidth(1);
      label.SetTextSize(inset ? 15 : textPixels);
      const bool p1 = page.role == "multiplicity.composite";
      label.SetTextAlign(p1 ? 33 : 23);
      label.DrawLatex(p1 ? 1-panel.margins[1] :
          (panel.margins[0]+1-panel.margins[1])/2,
          p1 ? (inset ? .08 : .23) :
              (page.role=="spectra.signed_heavy" ? .18 : (inset ? .14 : .09)),
          panel.xTitle.c_str());
    }
    bool drawn = false;
    for (std::size_t seriesIndex = 0; seriesIndex < selected.size(); ++seriesIndex) {
      const Series* entry = selected[seriesIndex];
      const Series& series = *entry;
      const bool histogram = series.mode == "histogram";
      const bool dense = histogram && series.points.size() > 40;
      const auto expected = ExpectedGraphs(page, panel, series, index, seriesIndex);
      if (expected.empty()) continue;
      drawn = true;
      for (const auto& item : expected) {
        graphs.emplace_back(std::make_unique<TGraphErrors>());
        auto& graph = *graphs.back();
        Style(graph, series, item.dense);
        graph.SetName(item.name.c_str()); graph.SetTitle(item.title.c_str());
        for (std::size_t i = 0; i < item.x.size(); ++i) {
          graph.SetPoint(i, item.x[i], item.y[i]);
          graph.SetPointError(i, item.ex[i], item.ey[i]);
        }
        if (inset) { graph.SetMarkerSize(0); graph.SetLineWidth(2); }
        if (item.title.rfind("band:", 0) == 0) {
          graph.SetFillColorAlpha(Color(series.color), .12);
          graph.SetFillStyle(1001); graph.Draw("3 SAME");
        } else if (item.title.rfind("points:", 0) == 0) {
          graph.Draw(panel.uncertaintyDisplay == "CENTERS_ONLY" || dense || inset
                         ? "PX SAME" : "PZ SAME");
        } else if (item.title.rfind("dense_markers:", 0) == 0) {
          graph.Draw("P SAME");
        } else graph.Draw("L SAME");
      }
    }
    if (!drawn) {
      TLatex status;
      status.SetNDC(); status.SetTextFont(43); status.SetTextSize(textPixels);
      status.SetTextAlign(22);
      status.DrawLatex(.5, BlankStatusY(page,panel),
                       panel.status == "NOT_MATERIALIZED"
                           ? "NOT_MATERIALIZED"
                           : panel.status == "PRESENT_UNDEFINED"
                               ? "PRESENT / UNDEFINED"
                           : panel.status == "PRESENT_NO_DRAWABLE_CENTER"
                               ? "PRESENT / NO REGULAR DRAW"
                           : panel.logY && panel.status == "AVAILABLE"
                               ? "No positive values on logarithmic axis"
                               : "Unavailable projection");
      if (!panel.note.empty()) {
        status.SetTextSize(std::max(12, textPixels - 3));
        status.SetTextColor(kGray + 2);
        const auto lines=StatusNoteLines(panel.note);
        for (std::size_t i=0;i<lines.size();++i)
          status.DrawLatex(.5, BlankNoteY(page,panel)-BlankNoteStep(page,panel)*i,
                           lines[i].c_str());
      }
    }
    for (const auto& item : ExpectedPanelLegends(page, panel, pages, index)) {
      const auto& box=item.geometry;
      legends.emplace_back(std::make_unique<TLegend>(box[0],box[1],box[2],box[3]));
      auto& legend=*legends.back();
      legend.SetBorderSize(0); legend.SetFillStyle(0); legend.SetTextFont(43);
      legend.SetTextSize(item.textSize); legend.SetMargin(item.margin);
      legend.SetNColumns(item.columns);
      for (const auto& entry : item.entries) {
        graphs.emplace_back(std::make_unique<TGraphErrors>());
        Style(*graphs.back(),*entry.series,false);
        graphs.back()->SetLineStyle(entry.lineStyle);
        graphs.back()->SetLineWidth(1);
        graphs.back()->SetMarkerSize(entry.markerSize);
        legend.AddEntry(graphs.back().get(),entry.label.c_str(),entry.option.c_str());
      }
      legend.Draw();
    }
    for (const auto& guide : panel.guides) {
      // Receipt guides outside the displayed support stay in the machine record.
      if (guide.x2 < panel.xLow || guide.x1 > panel.xHigh) continue;
      const bool insetClass = page.role == "multiplicity.composite" &&
          panel.id == "inset.monash_boundaries" &&
          guide.id.rfind("class.", 0) == 0;
      if (insetClass && guide.x1 < panel.xLow) continue;
      lines.emplace_back(std::make_unique<TLine>(
          guide.x1,guide.y1,insetClass ? guide.x1 : guide.x2,guide.y2));
      LineStyle(guide.style);
      lines.back()->SetLineColor(Color(guide.color)); lines.back()->SetLineStyle(guide.style);
      lines.back()->Draw();
    }
    if (inset) {
      // Put the black histogram above the boundary guides, as HIST SAME did
      // in the original inset, without duplicating saved graph primitives.
      std::vector<TObject*> histogramLines;
      TIter primitives(pad.GetListOfPrimitives());
      while (auto* primitive = primitives())
        if (dynamic_cast<TGraphErrors*>(primitive) &&
            std::string(primitive->GetTitle()).rfind("line:", 0) == 0)
          histogramLines.push_back(primitive);
      for (auto* line : histogramLines) {
        pad.GetListOfPrimitives()->Remove(line);
        pad.GetListOfPrimitives()->Add(line, "L SAME");
      }
    }
    for (const auto& item : panel.annotations)
      Text(item.x,item.y,item.text,static_cast<int>(item.size));
    for (const auto& item : InsetClassTexts(page, panel)) {
      TLatex label; label.SetNDC(); label.SetTextFont(43);
      label.SetLineWidth(1);
      label.SetTextSize(item.size); label.SetTextAlign(item.align);
      label.SetTextAngle(item.angle); label.SetTextColor(item.color);
      label.DrawLatex(item.x,item.y,item.text.c_str());
    }
    for (const auto& item : StateGlyphTexts(page, panel, pages))
      Text(item.x, item.y, item.text, static_cast<int>(item.size),
           item.color);
    if (drawn && !panel.note.empty() &&
        !(page.role=="multiplicity.composite" &&
          (panel.id=="upper.distribution" || panel.id=="lower.ratio")) &&
        page.role.rfind("balancing.",0)!=0 &&
        page.role.rfind("correlations.",0)!=0) {
      const bool upperNote = panel.id.rfind("upper.",0)==0 ||
                             panel.id == "g9.absolute";
      const double noteY = upperNote ? .89 : .025;
      Text(panel.margins[0], noteY, panel.note,
           inset ? 11 : textPixels-3, 1);
    }
    pad.RedrawAxis(); canvas.cd();
  }
  if (!page.scientificHeader.empty())
    Text(.015,.015,page.scientificHeader,
         std::max(11,textPixels-4), kGray+2);
  std::map<int,const Series*> classSamples;
  for (const auto& panel : page.panels) for (const auto& series : panel.series)
    classSamples.emplace(series.lineStyle,&series);
  if (page.role.find("balancing.activity.")==0 && !classSamples.empty()) {
    legends.emplace_back(std::make_unique<TLegend>(
        .05, ClassLegendBottom(classSamples.size()), .99, .925));
    auto& legend=*legends.back();
    legend.SetNColumns(ClassLegendColumns(classSamples.size()));
    legend.SetBorderSize(0); legend.SetFillStyle(0);
    legend.SetTextFont(43); legend.SetTextSize(textPixels);
    legend.SetMargin(.64);
    for (const auto& item : classSamples) {
      graphs.emplace_back(std::make_unique<TGraphErrors>());
      Style(*graphs.back(),*item.second,false);
      graphs.back()->SetLineColor(kBlack);
      graphs.back()->SetMarkerColor(kBlack);
      graphs.back()->SetMarkerSize(0.);
      legend.AddEntry(graphs.back().get(),item.second->label.c_str(),"l");
    }
    legend.Draw();
  }
  for (const auto& item : ClassKeyTexts(page))
    Text(item.x, item.y, item.text, static_cast<int>(item.size));
  for (const auto& item : CanvasSupplementTexts(page)) {
    TLatex label;
    label.SetNDC(); label.SetTextFont(43);
    label.SetLineWidth(1);
    label.SetTextSize(item.size); label.SetTextAlign(item.align);
    label.SetTextColor(item.color); label.SetTextAngle(item.angle);
    label.DrawLatex(item.x,item.y,item.text.c_str());
  }
  const std::string savedDash = gStyle->GetLineStyleString(2);
  if (page.role == "multiplicity.composite")
    gStyle->SetLineStyleString(2, "12 12");  // Original ROOT inset dash pattern.
  canvas.Modified(); canvas.Update(); canvas.cd();
  canvas.SaveAs((output/page.filename).string().c_str());
  TNamed identity("drawing_identity", PageIdentity(page).c_str());
  canvas.GetListOfPrimitives()->Add(&identity);
  archive.cd();
  WriteCanvas(canvas, canvasName);
  canvas.GetListOfPrimitives()->Remove(&identity);
  gStyle->SetLineStyleString(2, savedDash.c_str());
}
}  // namespace

int main(int argc, char** argv) {
  try {
    Need(argc == 4,
         "usage: render PLAN OUTPUT DRAWING_RECORD | render verify OUTPUT DRAWING_RECORD");
    gROOT->SetBatch(true); gStyle->SetOptStat(0); gErrorIgnoreLevel = kWarning;
    VerifyYAxisLabelPolicyFixtures();
    if (std::string(argv[1]) == "verify") {
      const std::filesystem::path output(argv[2]), record(argv[3]);
      const auto pages = ReadPlan(record, "/dev/null");
      VerifyCanvasArchive(output, record, pages);
      return 0;
    }
    const std::filesystem::path plan(argv[1]), output(argv[2]), record(argv[3]);
    Need(!std::filesystem::exists(output), "output collision");
    std::filesystem::create_directory(output);
    const auto pages = ReadPlan(plan, record);
    // ROOT serializes its file name into several directory/key records. A
    // stable relative name keeps staging-directory randomness out of bytes.
    std::filesystem::current_path(output);
    TFile archive("canvases.root", "CREATE");
    Need(!archive.IsZombie(), "cannot create canvas archive");
    for (const auto& page : pages) DrawPage(page, output, pages, archive);
    archive.cd();
    TObjString drawingRecord(ReadBytes(record).c_str());
    Need(drawingRecord.Write("drawing_record") > 0,
         "cannot write archived drawing record");
    archive.Close();
  } catch (const std::exception& error) {
    std::cerr << "ERROR: " << error.what() << '\n'; return 2;
  }
  return 0;
}
