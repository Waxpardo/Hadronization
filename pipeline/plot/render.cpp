#include "TAxis.h"
#include "TCanvas.h"
#include "TColor.h"
#include "TError.h"
#include "TFile.h"
#include "TGraphErrors.h"
#include "TH1F.h"
#include "TKey.h"
#include "TLatex.h"
#include "TLegend.h"
#include "TLegendEntry.h"
#include "TLine.h"
#include "TNamed.h"
#include "TObjString.h"
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
struct Panel {
  std::string id, status, title, xTitle, yTitle, note, reusePanel, reuseTune,
      uncertaintyDisplay;
  bool logY = false, logX = false;
  double xLow = 0, xHigh = 1, yLow = 0, yHigh = 1;
  std::array<double, 4> geometry{}, margins{}, legend{};
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
    "class_patterns_sha256=e171e4a18c8c169cbe78e738fbed586e21b0b8320e1ce0efd17dcbb3c2662d76";
int BodyTextPixels(const Page& page) {
  const double paperWidthPoints =
      kPaperWidthCentimeters * kPointsPerCentimeter;
  return std::max(page.textPixels,
                  static_cast<int>(std::ceil(8. * page.width /
                                             paperWidthPoints)));
}
int PanelLegendTextPixels(const Page& page) {
  return page.role.find("correlations.") == 0
      ? page.textPixels : BodyTextPixels(page);
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
int TuneLegendColumns(std::size_t count) {
  return static_cast<int>(std::max<std::size_t>(1,
      std::min<std::size_t>(3, count)));
}
double TuneLegendLeft(std::size_t count) {
  return .99 - .16 * TuneLegendColumns(count);
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
  return .897 - .026 * rows;
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
  Need(header.size() == 2 && header[0] == "hadronization_plot_drawing_plan_v7", "plan framing differs");
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
        Need(f.size() == 27 && !panelIndex.count(panelKey) &&
             (f[26]=="STANDARD" || f[26]=="CENTERS_ONLY" ||
              f[26]=="DENSE_BAND"), "panel differs");
        Panel panel;
        panel.id = f[2]; panel.status = f[3]; panel.logY = Integer(f[4]) != 0;
        panel.logX = Integer(f[25]) != 0;
        panel.uncertaintyDisplay=f[26];
        const bool teaching=panel.id.rfind("correlation.teaching.",0)==0;
        Need(teaching ? panel.uncertaintyDisplay=="CENTERS_ONLY" :
             (page.role=="multiplicity.composite") ==
             (panel.uncertaintyDisplay!="STANDARD"),
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
        if (f[0] == "SERIES") {
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
  if (kind == "line") result += "_r" + IndexToken(runIndex);
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
  if (!panel.reusePanel.empty()) return runs;
  std::vector<ExpectedGraph> result;
  if (series.mode != "points") {
    result.insert(result.end(), runs.begin(), runs.end());
  }
  result.push_back(std::move(points));
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
      if (std::isfinite(point.x) && std::isfinite(point.y) &&
          (!panel.logY || point.y > 0))
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
std::vector<ExpectedText> StateGlyphTexts(
    const Page& page, const Panel& panel, const std::vector<Page>& pages) {
  if (!panel.reusePanel.empty()) return {};
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
        .044*(panel.geometry[3]-panel.geometry[1])*page.height, 1, 22, 90));
  }
  const double pixels=(panel.geometry[3]-panel.geometry[1])*page.height;
  result.push_back(TextExpectation("#bf{"+panel.reuseTune+" tune-local percentile classes}",
      .02,.965,.054*pixels,1,13));
  result.push_back(TextExpectation("thresholds: "+panel.reuseTune+
      (partialSample ? " synthetic fixture" : " production sample"),
      .02,.895,.042*pixels,1,13));
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
           "N_{ch}: charged-light final-particle activity, heavy flavour excluded",
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
constexpr std::array<double, 5> kP1InformationY = {{.850, .825, .800, .775, .750}};
constexpr std::array<int, 5> kP1InformationPixels = {{20, 17, 16, 15, 15}};
double CategoryTickInnerY(const Panel& panel, bool top) {
  constexpr double fraction = .012;
  if (panel.logY) {
    const double factor = std::pow(panel.yHigh / panel.yLow, fraction);
    return top ? panel.yHigh / factor : panel.yLow * factor;
  }
  const double delta = (panel.yHigh - panel.yLow) * fraction;
  return top ? panel.yHigh - delta : panel.yLow + delta;
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
  if (!inset && !panel.yTitle.empty()) {
    result.push_back(TextExpectation(
        panel.yTitle, page.role.find("correlations.") == 0 ? .045 :
            (page.role.find("balancing.") == 0 &&
             panel.id.rfind("upper.", 0) == 0 ? .05 : .075),
        (panel.margins[2] + 1 - panel.margins[3]) / 2,
        textPixels, 1, 23, 90));
  }
  const double frameWidth = 1 - panel.margins[0] - panel.margins[1];
  for (const auto& tick : panel.ticks) {
    result.push_back(TextExpectation(
        tick.second, panel.margins[0] + frameWidth * xFraction(tick.first),
        panel.margins[2] - .025, inset ? 14 : textPixels, 1,
        panel.ticks.size() >= 5 ? 32 : 23,
        panel.ticks.size() >= 5 ? 90 : 0));
  }
  for (double coordinate : StatusRailCoordinates(page, panel, pages)) {
    result.push_back(TextExpectation(
        "#times", panel.margins[0] + frameWidth * xFraction(coordinate),
        std::max(.03, panel.margins[2] - .005), inset ? 11 : textPixels - 2,
        kGray + 2, 22));
  }
  result.push_back(TextExpectation(panel.title, panel.margins[0], .94,
                                   inset ? 15 : textPixels + 1));
  if (page.role == "multiplicity.composite" &&
      panel.id == "upper.distribution") {
    const auto lines = P1InformationLines(page);
    for (std::size_t i = 0; i < lines.size(); ++i)
      result.push_back(TextExpectation(lines[i], P1InformationX,
                                       kP1InformationY.at(i),
                                       kP1InformationPixels.at(i)));
  }
  if (!inset && !panel.xTitle.empty() &&
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
  if (!panel.reusePanel.empty() ||
      !PanelHasDrawing(page, panel, pages, panelIndex)) return {};
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
        !series->legendLabel.empty() && labels.insert(series->legendLabel).second) {
      legend.entries.push_back({series->legendLabel, "lp", series, 1.4,
                                series->lineStyle});
    }
  }
  if (legend.entries.empty()) return {};
  if (std::all_of(legend.entries.begin(), legend.entries.end(),
                  [](const auto& entry) { return TuneRank(entry.label) < 3; }))
    std::stable_sort(legend.entries.begin(), legend.entries.end(),
        [](const auto& left, const auto& right) {
          return TuneRank(left.label) < TuneRank(right.label);
        });
  return {legend};
}
std::vector<ExpectedLegend> ExpectedCanvasLegends(const Page& page) {
  std::vector<ExpectedLegend> result;
  const int textPixels = BodyTextPixels(page);
  std::vector<std::pair<std::string, const Series*>> tuneSamples;
  std::set<std::string> tuneIds;
  std::map<int, const Series*> classSamples;
  for (const auto& panel : page.panels) for (const auto& series : panel.series) {
    if (tuneIds.insert(series.tune).second)
      tuneSamples.emplace_back(series.tune, &series);
    classSamples.emplace(series.lineStyle, &series);
  }
  SortTuneSamples(tuneSamples);
  const bool teachingCorrelation = std::any_of(page.panels.begin(),
      page.panels.end(), [](const Panel& item) {
        return item.id.rfind("correlation.balance.", 0) == 0 ||
               item.id.rfind("correlation.teaching.", 0) == 0;
      });
  if ((page.role.find("balancing.") == 0 ||
       (page.role.find("correlations.") == 0 && !teachingCorrelation)) &&
      !tuneSamples.empty()) {
    const bool activity = page.role.find("balancing.activity.")==0;
    ExpectedLegend legend{{TuneLegendLeft(tuneSamples.size()),
                          activity ? .909 : .956, .99,
                          activity ? .950 : .995},
                          TuneLegendColumns(tuneSamples.size()),
                          double(textPixels + 2), false, 0, {}};
    for (const auto& tune : tuneSamples) {
      legend.entries.push_back({tune.first, "lp", tune.second, 1.4, 1});
    }
    result.push_back(std::move(legend));
  }
  if (page.role.find("balancing.activity.") == 0 && !classSamples.empty()) {
    ExpectedLegend legend{{.05, ClassLegendBottom(classSamples.size()),
                           .99, .897},
                          ClassLegendColumns(classSamples.size()),
                          double(std::max(18, textPixels - 4)), true, .64, {}};
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
std::vector<ExpectedText> CanvasSupplementTexts(const Page& page) {
  std::vector<ExpectedText> result;
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
                           std::string("? = withheld SE");
    if (!note.empty())
      result.push_back(TextExpectation(
          note,.015,.045,teaching ? BodyTextPixels(page) : 18,kGray+2));
  }
  if (page.role=="multiplicity.composite") {
    const auto parent=std::find_if(page.panels.begin(),page.panels.end(),
        [](const Panel& item){return item.id=="upper.distribution";});
    if (parent!=page.panels.end() && !parent->note.empty())
      result.push_back(TextExpectation(parent->note,.015,.055,16));
    const auto ratio=std::find_if(page.panels.begin(),page.panels.end(),
        [](const Panel& item){return item.id=="lower.ratio";});
    if (ratio!=page.panels.end() && !ratio->note.empty())
      result.push_back(TextExpectation(ratio->note,.015,.035,16));
  }
  for (const Panel& panel : page.panels) {
    if (panel.id.rfind("lower.",0)!=0 ||
        !CategoricalAxis(page,panel) || panel.xTitle.empty()) continue;
    const double center=panel.geometry[0]+
        (panel.geometry[2]-panel.geometry[0])*
        (panel.margins[0]+1-panel.margins[1])/2;
    result.push_back(TextExpectation(panel.xTitle,center,
        page.role=="balancing.baryon_meson.activity" ? .045 : .075,
        BodyTextPixels(page),1,23));
  }
  if (page.role=="spectra.signed_heavy") {
    Need(!page.title.empty(), "G9 visible signed-species title is absent");
    result.push_back(TextExpectation(page.title,.16,.95,22));
    std::size_t start=0,index=0;
    while (start<page.information.size()) {
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
        Need(pad->GetFillStyle() == 4000 && pad->GetFrameFillStyle() == 0 &&
             pad->GetFrameLineWidth() == 1,
             "percentile inset transparency differs from reference");
      const int textPixels = BodyTextPixels(page);
      const double baseLabelSize = inset ? .055 : textPixels;
      const double expectedXLabelSize =
          (panel.xTitle.empty() || !panel.ticks.empty()) ? 0 : baseLabelSize;
      const bool categoricalAxis = CategoricalAxis(page, panel);
      const bool p1MainAxis = page.role == "multiplicity.composite" &&
          (panel.id == "upper.distribution" || panel.id == "lower.ratio");
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
           StoredFloatClose(frame->GetYaxis()->GetLabelSize(), baseLabelSize) &&
           StoredFloatClose(frame->GetXaxis()->GetTitleSize(), inset ? .062 : textPixels) &&
           StoredFloatClose(frame->GetYaxis()->GetTitleSize(), inset ? .060 : textPixels) &&
           frame->GetYaxis()->GetNdivisions() % 1000000 ==
               (page.role == "multiplicity.composite" &&
                panel.id == "upper.distribution" ? 509 : inset ? 503 : 505) &&
           frame->GetYaxis()->GetMoreLogLabels() ==
             (!inset && panel.logY && panel.yHigh / panel.yLow < 10.) &&
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
      const std::size_t dividers = boundaries.size() > 1 ?
          boundaries.size() - 2 : 0;
      Need(actualGuides.size() == expectedGuides.size() +
           2 * boundaries.size() + dividers,
           "scientific guide object set differs from drawing record");
      for (std::size_t index = 0; index < boundaries.size(); ++index) {
        const std::size_t start = 2 * index + (index > 0 ? index - 1 : 0);
        for (int side = 0; side < 2; ++side) {
          const TLine& tick = *actualGuides[start + side];
          const bool top = side == 1;
          Need(SameBinary64(tick.GetX1(), boundaries[index]) &&
               SameBinary64(tick.GetX2(), boundaries[index]) &&
               SameBinary64(tick.GetY1(), top ? panel.yHigh : panel.yLow) &&
               SameBinary64(tick.GetY2(), CategoryTickInnerY(panel, top)) &&
               tick.GetLineColor() == kBlack &&
               tick.GetLineStyle() == 1 && tick.GetLineWidth() == 1,
               "categorical boundary tick geometry differs");
        }
        if (index > 0 && index + 1 < boundaries.size()) {
          const TLine& divider = *actualGuides[start + 2];
          Need(SameBinary64(divider.GetX1(), boundaries[index]) &&
               SameBinary64(divider.GetX2(), boundaries[index]) &&
               SameBinary64(divider.GetY1(), panel.yLow) &&
               SameBinary64(divider.GetY2(), panel.yHigh) &&
               divider.GetLineColor() == kGray+1 &&
               divider.GetLineStyle() == 3 && divider.GetLineWidth() == 1,
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
           className == "TLegend" || className == "TNamed",
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
  text.SetNDC(); text.SetTextFont(43); text.SetTextSize(pixels); text.SetTextColor(color);
  text.DrawLatex(x, y, label.c_str());
}
void LineStyle(int style) {
  // ROOT PDF converts quarter-point pattern lengths to integer points.
  // Multiples of four keep every dash/gap nonzero in small printed legends.
  // Integer style identity still follows the authenticated 1 + class_id rule.
  static const std::array<const char*, 11> patterns = {{
    "24 12", "4 8", "24 8 4 8", "24 8 4 8 4 8", "12 8", "40 12",
    "40 8 12 8", "12 8 4 8", "4 16", "24 8 12 8 4 8", "12 8 12 8 4 8"}};
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
      // TPad::SetFillStyle(0) in the reference normalizes to 4000 (transparent).
      pad.SetFillStyle(4000); pad.SetFrameFillStyle(0); pad.SetFrameLineWidth(1);
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
    if (!inset && !panel.yTitle.empty()) {
      TLatex label; label.SetNDC(); label.SetTextFont(43); label.SetTextSize(textPixels);
      label.SetTextAngle(90); label.SetTextAlign(23);
      label.DrawLatex(page.role.find("correlations.")==0 ? .045 :
                          (page.role.find("balancing.")==0 &&
                           panel.id.rfind("upper.",0)==0 ? .05 : .075),
                      (panel.margins[2]+1-panel.margins[3])/2,panel.yTitle.c_str());
    }
    if (!panel.ticks.empty()) {
      frame->GetXaxis()->SetLabelSize(0);
      const double frameWidth = 1 - panel.margins[0] - panel.margins[1];
      for (const auto& tick : panel.ticks) {
        TLatex label; label.SetNDC(); label.SetTextFont(43);
        label.SetTextSize(inset ? 14 : textPixels);
        label.SetTextAngle(panel.ticks.size() >= 5 ? 90 : 0); label.SetTextAlign(panel.ticks.size() >= 5 ? 32 : 23);
        const double x = panel.margins[0] + frameWidth * xFraction(tick.first);
        label.DrawLatex(x, panel.margins[2] - .025, tick.second.c_str());
      }
    }
    if (CategoricalAxis(page, panel)) {
      for (double boundary : CategoryBoundaries(panel)) {
        for (int side = 0; side < 2; ++side) {
          const bool top = side == 1;
          lines.emplace_back(std::make_unique<TLine>(
              boundary, top ? panel.yHigh : panel.yLow,
              boundary, CategoryTickInnerY(panel, top)));
          lines.back()->SetLineColor(kBlack);
          lines.back()->SetLineStyle(1);
          lines.back()->SetLineWidth(1);
          lines.back()->Draw();
        }
        if (boundary > panel.xLow && boundary < panel.xHigh) {
          lines.emplace_back(std::make_unique<TLine>(
              boundary, panel.yLow, boundary, panel.yHigh));
          lines.back()->SetLineColor(kGray+1);
          lines.back()->SetLineStyle(3);
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
                       std::max(.03, panel.margins[2] - .005), "#times");
    }
    Text(panel.margins[0], .94, panel.title, inset ? 15 : textPixels + 1);
    if (page.role == "multiplicity.composite" &&
        panel.id == "upper.distribution") {
      const auto lines = P1InformationLines(page);
      for (std::size_t i = 0; i < lines.size(); ++i)
        Text(P1InformationX, kP1InformationY.at(i), lines[i],
             kP1InformationPixels.at(i));
    }
    if (!inset && !panel.xTitle.empty() &&
        !(CategoricalAxis(page,panel) && panel.id.rfind("lower.",0)==0)) {
      TLatex label; label.SetNDC(); label.SetTextFont(43);
      label.SetTextSize(inset ? 15 : textPixels);
      const bool p1 = page.role == "multiplicity.composite";
      label.SetTextAlign(p1 ? 33 : 23);
      label.DrawLatex(p1 ? 1-panel.margins[1] :
          (panel.margins[0]+1-panel.margins[1])/2,
          p1 ? (inset ? .08 : .23) :
              (page.role=="spectra.signed_heavy" ? .18 : (inset ? .14 : .09)),
          panel.xTitle.c_str());
    }
    const auto& box = panel.legend;
    legends.emplace_back(std::make_unique<TLegend>(box[0],box[1],box[2],box[3]));
    TLegend& legend = *legends.back();
    legend.SetBorderSize(0); legend.SetFillStyle(0); legend.SetTextFont(43);
    legend.SetTextSize(PanelLegendTextPixels(page)); legend.SetMargin(.12);
    const bool sideLegend = panel.margins[1] > .3;
    if (!sideLegend) legend.SetNColumns(
      panel.id.rfind("correlation.balance.", 0) == 0 ? 2 :
      page.role.find("kinematics.")==0 ? 3 :
      page.role == "balancing.baryon_meson.activity" ? 2 : 1);
    std::set<std::string> legendLabels;
    std::vector<std::pair<std::string,TGraphErrors*>> legendSamples;
    bool drawn = false;
    for (std::size_t seriesIndex = 0; seriesIndex < selected.size(); ++seriesIndex) {
      const Series* entry = selected[seriesIndex];
      const Series& series = *entry;
      const bool categories = series.mode == "categories";
      const bool histogram = series.mode == "histogram";
      const bool dense = histogram && series.points.size() > 40;
      graphs.emplace_back(std::make_unique<TGraphErrors>());
      TGraphErrors* errors = graphs.back().get(); Style(*errors,series,dense);
      errors->SetName(GraphName(index, seriesIndex, "points").c_str());
      errors->SetTitle(GraphTitle(series, "points").c_str());
      std::vector<std::unique_ptr<TGraphErrors>> runs;
      bool breakRun = true;
      for (const Point& point : series.points) {
        if (!Drawable(panel, point)) {
          breakRun = true; continue;
        }
        const int i = errors->GetN();
        errors->SetPoint(i, point.x, point.y);
        errors->SetPointError(i, 0, std::isfinite(point.error) ? point.error : 0);
        if (breakRun) {
          runs.emplace_back(std::make_unique<TGraphErrors>());
          Style(*runs.back(),series,dense);
          const std::size_t runIndex = runs.size() - 1;
          runs.back()->SetName(
              GraphName(index, seriesIndex, "line", runIndex).c_str());
          runs.back()->SetTitle(GraphTitle(series, "line").c_str());
          breakRun = false;
        }
        TGraphErrors& line = *runs.back();
        if (categories) {
          line.SetPoint(line.GetN(), point.x - CategoryHalfWidth(page), point.y);
          line.SetPoint(line.GetN(), point.x + CategoryHalfWidth(page), point.y);
          breakRun=true;
        } else if (histogram && std::isfinite(point.binLow) &&
                   std::isfinite(point.binHigh)) {
          line.SetPoint(line.GetN(),
                        panel.logX ? std::max(point.binLow, panel.xLow)
                                   : point.binLow, point.y);
          line.SetPoint(line.GetN(), point.binHigh, point.y);
        } else {
          line.SetPoint(line.GetN(), point.x, point.y);
        }
      }
      if (errors->GetN() == 0) continue;
      drawn = true;
      if (inset) {
        for (auto& line : runs) {
          line->SetMarkerSize(0); line->SetLineWidth(2);
          line->Draw("L SAME"); graphs.push_back(std::move(line));
        }
        continue;
      }
      if (dense && panel.uncertaintyDisplay != "CENTERS_ONLY") {
        // A translucent 1-SE envelope preserves all persisted uncertainties
        // for high-bin-count curves without a vertical-bar forest. The full
        // TGraphErrors is still archived and checked point by point.
        errors->SetFillColorAlpha(Color(series.color), .08);
        errors->SetFillStyle(1001);
        errors->Draw("3 SAME");
      }
      if (panel.uncertaintyDisplay == "CENTERS_ONLY")
        errors->Draw("PX SAME");
      if (series.mode != "points") {
        for (auto& line : runs) {
          line->Draw("L SAME"); graphs.push_back(std::move(line));
        }
      }
      if (!dense && panel.uncertaintyDisplay != "CENTERS_ONLY")
        errors->Draw("PZ SAME");
      if (dense) {
        graphs.emplace_back(std::make_unique<TGraphErrors>());
        Style(*graphs.back(),series,false);
        graphs.back()->SetName(
            GraphName(index, seriesIndex, "dense_markers").c_str());
        graphs.back()->SetTitle(GraphTitle(series, "dense_markers").c_str());
        std::vector<Point> visible;
        for (const auto& point:series.points)
          if (point.x>=panel.xLow && point.x<=panel.xHigh) visible.push_back(point);
        const std::size_t stride = std::max<std::size_t>(1, visible.size()/18);
        for (std::size_t i=0; i<visible.size(); i+=stride) {
          const auto& point=visible[i];
          if (Drawable(panel, point))
            graphs.back()->SetPoint(graphs.back()->GetN(),point.x,point.y);
        }
        graphs.back()->Draw("P SAME");
      }
      // A sample retains tune marker identity even when dense bins omit markers.
      graphs.emplace_back(std::make_unique<TGraphErrors>());
      Style(*graphs.back(),series,false);
      graphs.back()->SetMarkerSize(1.4);
      if (!series.legendLabel.empty() && legendLabels.insert(series.legendLabel).second)
        legendSamples.emplace_back(series.legendLabel, graphs.back().get());
    }
    if (std::all_of(legendSamples.begin(), legendSamples.end(),
                    [](const auto& sample) { return TuneRank(sample.first) < 3; }))
      SortTuneSamples(legendSamples);
    for (const auto& sample : legendSamples)
      legend.AddEntry(sample.second, sample.first.c_str(), "lp");
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
    if (!inset && drawn && !legendLabels.empty()) legend.Draw();
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
        if (dynamic_cast<TGraphErrors*>(primitive)) histogramLines.push_back(primitive);
      for (auto* line : histogramLines) {
        pad.GetListOfPrimitives()->Remove(line);
        pad.GetListOfPrimitives()->Add(line, "L SAME");
      }
    }
    for (const auto& item : InsetClassTexts(page, panel)) {
      TLatex label; label.SetNDC(); label.SetTextFont(43);
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
  std::vector<std::pair<std::string,const Series*>> tuneSamples;
  std::set<std::string> tuneSampleIds;
  std::map<int,const Series*> classSamples;
  for (const auto& panel : page.panels) for (const auto& series : panel.series) {
    if (tuneSampleIds.insert(series.tune).second)
      tuneSamples.emplace_back(series.tune,&series);
    classSamples.emplace(series.lineStyle,&series);
  }
  SortTuneSamples(tuneSamples);
  const bool teachingCorrelation = std::any_of(page.panels.begin(),
      page.panels.end(), [](const Panel& item) {
        return item.id.rfind("correlation.balance.", 0) == 0 ||
               item.id.rfind("correlation.teaching.", 0) == 0;
      });
  if ((page.role.find("balancing.") == 0 ||
       (page.role.find("correlations.") == 0 && !teachingCorrelation)) &&
      !tuneSamples.empty()) {
    const bool activity = page.role.find("balancing.activity.")==0;
    legends.emplace_back(std::make_unique<TLegend>(
        TuneLegendLeft(tuneSamples.size()), activity ? .909 : .956,
        .99, activity ? .950 : .995));
    auto& legend=*legends.back();
    legend.SetNColumns(TuneLegendColumns(tuneSamples.size()));
    legend.SetBorderSize(0); legend.SetFillStyle(0);
    legend.SetTextFont(43); legend.SetTextSize(textPixels+2);
    for (const auto& tune : tuneSamples) {
      graphs.emplace_back(std::make_unique<TGraphErrors>());
      Style(*graphs.back(),*tune.second,false);
      graphs.back()->SetLineStyle(1); graphs.back()->SetLineWidth(1);
      graphs.back()->SetMarkerSize(1.4);
      legend.AddEntry(graphs.back().get(),tune.first.c_str(),"lp");
    }
    legend.Draw();
  }
  if (page.role.find("balancing.activity.")==0 && !classSamples.empty()) {
    legends.emplace_back(std::make_unique<TLegend>(
        .05, ClassLegendBottom(classSamples.size()), .99, .897));
    auto& legend=*legends.back();
    legend.SetNColumns(ClassLegendColumns(classSamples.size()));
    legend.SetBorderSize(0); legend.SetFillStyle(0);
    legend.SetTextFont(43); legend.SetTextSize(std::max(18, textPixels-4));
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
    label.SetTextSize(item.size); label.SetTextAlign(item.align);
    label.SetTextColor(item.color);
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
  Need(canvas.Write(canvasName.c_str()) > 0, "cannot write named TCanvas");
  canvas.GetListOfPrimitives()->Remove(&identity);
  gStyle->SetLineStyleString(2, savedDash.c_str());
}
}  // namespace

int main(int argc, char** argv) {
  try {
    Need(argc == 4,
         "usage: render PLAN OUTPUT DRAWING_RECORD | render verify OUTPUT DRAWING_RECORD");
    gROOT->SetBatch(true); gStyle->SetOptStat(0); gErrorIgnoreLevel = kWarning;
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
