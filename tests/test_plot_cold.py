"""Cold drawing boundary mutants; no published result cache is required."""

import importlib.util
import json
import math
from pathlib import Path
import subprocess
import shutil
import shlex
import sys
import tempfile
import time
from types import SimpleNamespace
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "phasea_plot_cold_contract", ROOT / "pipeline/plot/run.py")
plot = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(plot)


class ColdDrawingBoundary(unittest.TestCase):
    @unittest.skipUnless(shutil.which('root-config'), 'ROOT development files required')
    def test_final_y_axes_keep_legible_numeric_anchors(self):
        # These ranges exercise the two published failures: a narrow linear
        # spectrum that formerly had only two labels, and a sub-decade log
        # panel whose automatic labels bunched near its lower boundary.
        source = r'''#define main render_program_main
#include "pipeline/plot/render.cpp"
#undef main
int main() {
  Page page{}; page.width=1900; page.height=1600; page.textPixels=18;
  Panel panel{}; panel.geometry={0.,.32,.54,.895};
  panel.margins={.185,0.,.06,.115};
  panel.yLow=.008; panel.yHigh=.013;
  auto ticks=YMajorTicks(page,panel);
  if (ticks.size()<4 || ticks.front().value>.009 ||
      ticks.back().value<.012) return 1;
  panel.yLow=.0068070796899526555;
  panel.yHigh=.013095221543846035;
  ticks=YMajorTicks(page,panel);
  if (ticks.size()<5 || ticks.front().value>.008 ||
      ticks.back().value<.012) return 6;
  panel.logY=true; panel.yLow=.042; panel.yHigh=.196;
  ticks=YMajorTicks(page,panel);
  if (ticks.size()<3 || ticks.size()>5 ||
      ticks.front().value>.05 || ticks.back().value<.15) return 2;
  for (std::size_t i=1;i<ticks.size();++i)
    if ((YTickFraction(panel,ticks[i].value)-
         YTickFraction(panel,ticks[i-1].value))*YFramePixels(page,panel)<
        1.4*YTickTextPixels(page,panel)) return 3;
  panel.geometry={0.,.08,.54,.32}; panel.margins={.185,0.,.32,0.};
  panel.logY=false; panel.yLow=.786; panel.yHigh=3.858;
  ticks=YMajorTicks(page,panel);
  if (ticks.size()!=3 || ticks[0].label!="1" ||
      ticks[1].label!="2" || ticks[2].label!="3") return 4;
  panel.geometry={0.,.32,.54,.895}; panel.margins={.185,0.,.06,.115};
  panel.logY=true; panel.yLow=1.e-7; panel.yHigh=.5;
  ticks=YMajorTicks(page,panel);
  if (ticks.size()<5 || ticks[0].label!="10^{-7}" ||
      ticks.back().label!="10^{-1}") return 5;
  page.height=2400;
  panel.geometry={0.,.25,1.,.98};
  panel.margins={.08,.04,0.,.02};
  panel.yLow=1.e-9; panel.yHigh=1.;
  ticks=YMajorTicks(page,panel);
  if (ticks.size()!=9 || ticks[0].label!="10^{-8}" ||
      ticks[4].label!="10^{-4}" || ticks[8].label!="1") return 7;
  page.width=1900; page.height=2600; page.textPixels=18;
  panel.geometry={0.,.44,.545,.61};
  panel.margins={.2018348623853211,0.,0.,.2307692307692308};
  panel.logY=false;
  panel.yLow=.00019223735786008463;
  panel.yHigh=.002851517567546;
  ticks=YMajorTicks(page,panel);
  if (ticks.size()<3 || ticks.front().label!="0.0005") return 8;
  for (const auto& tick:ticks)
    if (tick.label.find("#times")!=std::string::npos) return 9;
  // Joined panels with an identical range must retain one common major step.
  page.width=2800; page.height=2850; page.textPixels=34;
  panel.geometry={0.,.612,1.,.808};
  panel.margins={.095,.0271429,0.,.10956};
  panel.logY=false;
  panel.yLow=-.017516291789465045;
  panel.yHigh=.40848741927917398;
  const auto topTicks=YMajorTicks(page,panel);
  page.panels.push_back(panel);
  panel.geometry={0.,.416,1.,.612};
  panel.margins={.095,.0271429,0.,0.};
  page.panels.push_back(panel);
  const auto middleTicks=YMajorTicks(page,panel);
  const auto harmonizedTopTicks=YMajorTicks(page,page.panels[0]);
  if (topTicks.size()<3 || middleTicks.size()<3 ||
      harmonizedTopTicks.size()!=middleTicks.size()) return 14;
  for (std::size_t i=0;i<middleTicks.size();++i)
    if (!Close(harmonizedTopTicks[i].value,middleTicks[i].value) ||
        harmonizedTopTicks[i].label!=middleTicks[i].label) return 24;
  if (harmonizedTopTicks.front().label!="0" ||
      harmonizedTopTicks.back().label!="0.4") return 25;
  if (YTickTextAlign(page,page.panels[0],harmonizedTopTicks.front().value)!=31 ||
      YTickTextAlign(page,page.panels[1],harmonizedTopTicks.back().value)!=33)
    return 26;
  page.panels.clear();
  // Logarithmic tune/reference axes must always label the unit reference.
  panel.geometry={0.,.08,1.,.22};
  panel.margins={.095,.0271429,.43,0.};
  page.role="balancing.integrated.beauty";
  panel.logY=true; panel.id="lower.521"; panel.reusePanel="lower.5122";
  panel.yLow=.415506; panel.yHigh=78.834042;
  ticks=YMajorTicks(page,panel);
  if (ticks.size()<3 ||
      std::none_of(ticks.begin(),ticks.end(),[](const YMajorTick& tick) {
        return Close(tick.value,1.);
      })) return 15;
  // Unity at a joined edge is clipped instead of being forced into the seam.
  page.height=1200; page.textPixels=34;
  panel.geometry={0.,.5,1.,.7};
  panel.margins={.095,.0271429,0.,.1};
  panel.reusePanel.clear(); panel.yLow=1.; panel.yHigh=100.;
  ticks=YMajorTicks(page,panel);
  if (std::any_of(ticks.begin(),ticks.end(),[](const YMajorTick& tick) {
        return Close(tick.value,1.);
      })) return 16;
  // A panel that physically fits only two anchors remains a valid fallback.
  page.height=1000; page.textPixels=34;
  panel.geometry={0.,.4,1.,.6};
  panel.margins={.1,.03,.25,.25}; panel.logY=false;
  panel.yLow=0.; panel.yHigh=1.;
  ticks=YMajorTicks(page,panel);
  if (ticks.size()!=2) return 17;
  // A joined scale with room for three labels retries a clean subdivision
  // after both seam-edge anchors are clipped.
  page.width=1900; page.height=1000; page.textPixels=34;
  panel.geometry={0.,.1,1.,.3};
  panel.margins={.1,.03,0.,0.}; panel.logY=false;
  panel.yLow=0.; panel.yHigh=.3;
  ticks=YMajorTicks(page,panel);
  if (ticks.size()!=3 || !Close(ticks[0].value,.05) ||
      !Close(ticks[1].value,.15) || !Close(ticks[2].value,.25)) return 18;
  // Narrow and broad logarithmic comparison panels keep three round anchors
  // and retain the unit reference when it is drawable.
  page.height=1000; page.textPixels=34; page.role="correlations.beauty";
  panel.geometry={0.,.1,1.,.36}; panel.margins={.1,.03,.13,0.};
  panel.logY=true; panel.id="correlation.compare.521.SS";
  panel.yLow=.0608809; panel.yHigh=6.75912;
  ticks=YMajorTicks(page,panel);
  if (ticks.size()!=3 || !Close(ticks[0].value,.1) ||
      !Close(ticks[1].value,1.) || !Close(ticks[2].value,4.)) return 19;
  page.role="correlations.charm";
  panel.id="correlation.compare.421.SS";
  panel.yLow=.623551; panel.yHigh=1.52942;
  ticks=YMajorTicks(page,panel);
  if (ticks.size()!=3 || !Close(ticks[1].value,1.)) return 20;
  panel.geometry={0.,.1,1.,.412}; panel.margins={.1,.03,.29,0.};
  panel.id="correlation.compare.421.OS_MINUS_SS";
  panel.yLow=.437976; panel.yHigh=1.5061;
  ticks=YMajorTicks(page,panel);
  if (ticks.size()!=3 || !Close(ticks.back().value,1.)) return 21;
  // The actual beauty SS correlation geometry keeps its deep rotated fraction
  // clear of seven-character fixed-decimal tick labels.
  page.width=1900; page.height=2600; page.textPixels=18;
  page.role="correlations.beauty";
  panel.id="correlation.main.521.SS";
  panel.geometry={0x0p+0,0x1.c28f5c28f5c29p-2,
                  0x1.170a3d70a3d71p-1,0x1.3851eb851eb85p-1};
  panel.margins={0x1.9d5b98a919d5cp-3,0x0p+0,0x0p+0,
                 0x1.d89d89d89d89fp-3};
  panel.logY=false;
  panel.yLow=-0x1.672b40aab4522p-14;
  panel.yHigh=0x1.2f04baa0f5cfap-10;
  panel.yTitle="#frac{1}{#it{N}_{trig}} #frac{d#it{N}_{pair}}{d#Delta#varphi} (rad^{-1})";
  const double longScaleTitleX=YTitleX(page,panel);
  // The old negative anchor clipped dN at the page edge. Keep the long-scale
  // title at its positive page-safe anchor, then verify actual PDF ink.
  if (!Close(longScaleTitleX,.006)) return 22;
  // The ordinary correlation scale keeps the established title position.
  panel.id="correlation.main.521.OS";
  panel.yLow=-0x1.f1f6c278aa7cep-9;
  panel.yHigh=0x1.b1bf900ebfe3cp-3;
  const double shortScaleTitleX=YTitleX(page,panel);
  if (shortScaleTitleX<.01 ||
      shortScaleTitleX<=longScaleTitleX) return 23;
  page.role="balancing.activity.charm";
  page.filename="supplemental.balancing.activity.charm.trigger-421.pdf";
  page.panels.resize(4); panel.id="upper.MONASH.421";
  if (!SharedStackYTitle(page,panel)) return 10;
  panel.id="lower.shared.421";
  if (SharedStackYTitle(page,panel)) return 11;
  page.role="balancing.integrated.charm"; panel.id="upper.421";
  if (SharedStackYTitle(page,panel)) return 12;
  page.width=4300;
  if (PaperWidthCentimeters(page)<40. || BodyTextPixels(page)>36) return 13;
  return 0;
}
'''
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cpp, binary = root / 'yaxis.cpp', root / 'yaxis'
            cpp.write_text(source)
            flags = shlex.split(subprocess.check_output(
                ['root-config', '--cflags', '--libs'], text=True))
            built = subprocess.run(
                ['c++', '-std=c++17', '-I', str(ROOT), str(cpp),
                 '-o', str(binary)] + flags, capture_output=True, text=True)
            self.assertEqual(built.returncode, 0, built.stderr)
            run = subprocess.run([str(binary)], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)

    @unittest.skipUnless(shutil.which('root-config'), 'ROOT development files required')
    def test_panel_letters_follow_visual_geometry_and_leave_titles_semantic(self):
        source = r'''#define main render_program_main
#include "pipeline/plot/render.cpp"
#undef main
int main() {
  Page page{}; page.width=1900; page.height=1600; page.textPixels=18;
  page.panels.resize(5);
  page.panels[0].id="lower.right";
  page.panels[0].geometry={.5,.1,1.,.5};
  page.panels[1].id="top.right";
  page.panels[1].geometry={.5,.5,1.,.9};
  page.panels[2].id="inset";
  page.panels[2].geometry={.2,.6,.4,.8};
  page.panels[2].reusePanel="top.left";
  page.panels[3].id="top.left";
  page.panels[3].geometry={0.,.5,.5,.9};
  page.panels[4].id="lower.left";
  page.panels[4].geometry={0.,.1,.5,.5};
  for (auto& panel:page.panels) panel.margins={.15,.04,.12,.08};
  const auto labels=PanelLabelAssignments(page);
  if (labels.size()!=4) return 1;
  const std::array<std::size_t,4> indices={{3,1,4,0}};
  const std::array<const char*,4> texts={{"a)","b)","c)","d)"}};
  const std::array<std::size_t,4> rows={{0,0,1,1}};
  const std::array<std::size_t,4> columns={{0,1,0,1}};
  for (std::size_t i=0;i<labels.size();++i)
    if (labels[i].panelIndex!=indices[i] || labels[i].text!=texts[i] ||
        labels[i].row!=rows[i] || labels[i].column!=columns[i]) return 2;
  const auto exactUpperLeft=[&](std::size_t index) {
    const auto& panel=page.panels[index];
    const auto label=PanelLabelText(page,index);
    const double pixels=PanelLabelPixels(page,panel);
    const double width=page.width*(panel.geometry[2]-panel.geometry[0]);
    const double height=page.height*(panel.geometry[3]-panel.geometry[1]);
    const double xTickLength=page.role=="multiplicity.composite" ? .025 : .03;
    double expectedInset=0.;
    for (const auto& peer:page.panels) {
      if (!peer.reusePanel.empty()) continue;
      const double peerWidth=page.width*(peer.geometry[2]-peer.geometry[0]);
      const double tickSize=page.filename.find(".trigger-")!=std::string::npos
          ? .015*std::min(1.,1900./page.width) : .03;
      expectedInset=std::max(expectedInset,tickSize*
          (1.-peer.margins[2]-peer.margins[3])*peerWidth+
          .15*PanelLabelPixels(page,peer)+1.);
    }
    const double expectedX=panel.margins[0]+expectedInset/width;
    const double expectedY=1-panel.margins[3]-xTickLength-.25*pixels/height;
    return label.align==13 && Close(label.x,expectedX) && Close(label.y,expectedY) &&
        label.x<.30 && label.y>.75;
  };
  const auto label=PanelLabelText(page,3);
  if (label.text!="a)" || !exactUpperLeft(3)) return 3;
  page.role="multiplicity.composite";
  page.panels[4].id="lower.ratio";
  if (!exactUpperLeft(4)) return 11;
  page.role.clear();
  page.panels[4].id="lower.left";
  page.role="spectra.signed_heavy";
  page.panels[3].id="g9.absolute";
  if (!exactUpperLeft(3)) return 12;
  page.role="balancing.baryon_meson.activity";
  page.filename="balancing.baryon_meson.activity.pdf";
  page.panels[3].id="upper.charm.421";
  if (!exactUpperLeft(3) || !exactUpperLeft(1)) return 13;
  page.role="balancing.integrated.charm";
  page.filename="balancing.integrated.charm.pdf";
  page.panels[3].id="upper.421";
  page.panels[1].id="upper.4122";
  if (!exactUpperLeft(3) || !exactUpperLeft(1)) return 14;
  page.filename="supplemental.balancing.integrated.charm.trigger-421.pdf";
  if (!exactUpperLeft(3)) return 15;
  page.role="balancing.activity.charm";
  page.filename="supplemental.balancing.activity.charm.trigger-421.pdf";
  page.panels[3].id="upper.MONASH.421";
  if (!exactUpperLeft(3)) return 16;
  page.filename="supplemental.balancing.activity.charm.extremes.trigger-421.pdf";
  if (!exactUpperLeft(3)) return 17;
  page.role="balancing.activity.beauty";
  page.filename="balancing.activity.beauty.pdf";
  page.panels[3].id="upper.MONASH.521";
  page.panels[1].id="upper.MONASH.5122";
  if (!exactUpperLeft(3) || !exactUpperLeft(1)) return 18;
  page.role="correlations.charm";
  page.filename="correlations.charm.pdf";
  page.panels[3].id="correlation.main.421.OS";
  if (!exactUpperLeft(3)) return 19;
  // A scientific legend that occupied the new label anchor must move while
  // retaining its dimensions and clearing the exact reserved ink envelope.
  page.role.clear();
  page.panels[3].legend={.18,.78,.36,.88};
  const auto rawLegend=page.panels[3].legend;
  const auto reserved=PanelLabelReservedBox(page,3);
  if (!BoxesOverlap(rawLegend,reserved)) return 20;
  const auto movedLegend=PanelScientificLegendBox(page,page.panels[3],3);
  if (BoxesOverlap(movedLegend,reserved) ||
      !Close(movedLegend[2]-movedLegend[0],rawLegend[2]-rawLegend[0]) ||
      !Close(movedLegend[3]-movedLegend[1],rawLegend[3]-rawLegend[1]) ||
      movedLegend==rawLegend) return 21;
  page.role="balancing.baryon_meson.activity";
  const auto movedTuneLegend=InsideTuneLegendBox(page,page.panels[3],3);
  if (BoxesOverlap(movedTuneLegend,reserved) || movedTuneLegend==rawLegend)
    return 22;
  page.role.clear();
  page.panels[3].id="upper.left";
  if (SemanticPanelTitle("(a) #it{B}^{+} trigger")!=
      "#it{B}^{+} trigger") return 4;
  if (SemanticPanelTitle("#it{D}^{0} trigger")!=
      "#it{D}^{0} trigger") return 5;
  if (SemanticPanelTitle("(A) title")!="(A) title" ||
      AlphabeticPanelLabel(25)!="z)" ||
      AlphabeticPanelLabel(26)!="aa)") return 6;
  TLatex actual;
  actual.SetNDC(); actual.SetTextFont(43); actual.SetTextSize(label.size);
  actual.SetTextAlign(label.align); actual.SetTextColor(label.color);
  actual.SetTextAngle(label.angle); actual.SetTitle(label.text.c_str());
  actual.SetX(label.x); actual.SetY(label.y);
  TList primitives; primitives.Add(&actual);
  VerifyTexts(primitives,{label});
  actual.SetTitle("b)");
  try { VerifyTexts(primitives,{label}); return 7; }
  catch (const std::runtime_error&) {}
  actual.SetTitle(label.text.c_str());
  TLatex duplicate=actual; primitives.Add(&duplicate);
  try { VerifyTexts(primitives,{label}); return 8; }
  catch (const std::runtime_error&) {}
  primitives.Clear();
  try { VerifyTexts(primitives,{label}); return 9; }
  catch (const std::runtime_error&) {}
  page.panels[1].geometry={0.,.5,1.,.9};
  try { (void)PanelLabelAssignments(page); }
  catch (const std::runtime_error&) { return 0; }
  return 10;
}
'''
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cpp, binary = root / 'panel_labels.cpp', root / 'panel_labels'
            cpp.write_text(source)
            flags = shlex.split(subprocess.check_output(
                ['root-config', '--cflags', '--libs'], text=True))
            built = subprocess.run(
                ['c++', '-std=c++17', '-I', str(ROOT), str(cpp),
                 '-o', str(binary)] + flags, capture_output=True, text=True)
            self.assertEqual(built.returncode, 0, built.stderr)
            run = subprocess.run([str(binary)], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)

    @unittest.skipUnless(shutil.which('root-config'), 'ROOT development files required')
    def test_native_panel_occupancy_does_not_connect_marker_only_points(self):
        source = r'''#define main render_program_main
#include "pipeline/plot/render.cpp"
#undef main
int main() {
  Page page{}; page.role="balancing.baryon_meson.activity";
  page.width=1900; page.height=1600; page.textPixels=34;
  Panel panel{}; panel.id="lower.beauty.5122";
  panel.geometry={.5,0.,1.,.2}; panel.margins={0.,.04,.2,0.};
  panel.xLow=.5; panel.xHigh=11.5; panel.yLow=.5; panel.yHigh=145.;
  panel.logY=true;
  Series series{}; series.mode="categories"; series.tune="MONASH";
  for (const auto& value : std::vector<std::pair<double,double>>{{1.,8.},{10.,80.}}) {
    Point point{}; point.x=value.first; point.y=value.second;
    point.error=0.; point.state="DRAW"; series.points.push_back(point);
  }
  panel.series.push_back(series);
  const auto boxes=PanelDataBoxes(page,panel,0);
  const double first=PanelXCoordinate(panel,1.);
  const double second=PanelXCoordinate(panel,10.);
  for (const auto& box : boxes)
    if (box[0]<first && box[2]>second) return 1;
  // The two category-bin handle line graphs and both individual point boxes
  // must still contribute real occupied geometry.
  if (boxes.size()!=8) return 2;
  return 0;
}
'''
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cpp, binary = root / 'panel_occupancy.cpp', root / 'panel_occupancy'
            cpp.write_text(source)
            flags = shlex.split(subprocess.check_output(
                ['root-config', '--cflags', '--libs'], text=True))
            built = subprocess.run(
                ['c++', '-std=c++17', '-I', str(ROOT), str(cpp),
                 '-o', str(binary)] + flags, capture_output=True, text=True)
            self.assertEqual(built.returncode, 0, built.stderr)
            run = subprocess.run([str(binary)], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)

    @unittest.skipUnless(shutil.which('root-config'), 'ROOT development files required')
    def test_native_panel_label_uses_common_corner_anchor_without_changing_ranges(self):
        source = r'''#define main render_program_main
#include "pipeline/plot/render.cpp"
#undef main
int main() {
  Page page{}; page.role="correlations.beauty";
  page.filename="correlations.beauty.pdf";
  page.width=1900; page.height=2850; page.textPixels=18;
  Panel panel{}; panel.id="correlation.compare.5122.SS";
  panel.geometry={.5,.32,1.,.42}; panel.margins={0.,.04,0.,0.};
  panel.xLow=-1.5707963267948966; panel.xHigh=4.71238898038469;
  // Display preparation reserves the tighter left-corner label.  The native
  // renderer must preserve that prepared range and clear the same real point.
  panel.yLow=.06088085489355096; panel.yHigh=12.456076181822445;
  panel.logY=true;
  Series series{}; series.mode="histogram"; series.tune="CLOSEPACKING";
  Point point{}; point.x=-1.413716694115407; point.y=4.545770498718472;
  point.error=std::numeric_limits<double>::quiet_NaN(); point.state="DRAW";
  point.binLow=-1.5707963267948966; point.binHigh=-1.2566370614359172;
  series.points.push_back(point); panel.series.push_back(series);
  page.panels.push_back(panel);
  const double low=page.panels[0].yLow,high=page.panels[0].yHigh;
  const auto base=BasePanelLabelText(page,0);
  const auto label=PanelLabelText(page,0);
  const double width=page.width*(panel.geometry[2]-panel.geometry[0]);
  if (label.x!=base.x || label.y!=base.y || label.size!=24 ||
      !Close((label.x-panel.margins[0])*width,
             PanelLabelLeftInsetPixels(page))) return 1;
  if (page.panels[0].yLow!=low || page.panels[0].yHigh!=high) return 2;
  const auto box=PanelLabelReservedBox(page,0);
  for (const auto& data:PanelDataBoxes(page,page.panels[0],0))
    if (BoxesOverlap(box,data)) return 3;
  const std::vector<Page> none;
  for (const auto& glyph:StateGlyphTexts(page,page.panels[0],none))
    if (BoxesOverlap(box,TextInkBox(page,page.panels[0],glyph))) return 4;

  // The protected multiplicity ceiling and common physical anchor remain
  // exact; display preparation, not renderer roaming, owns any clearance.
  Page multiplicity{}; multiplicity.role="multiplicity.composite";
  multiplicity.filename="multiplicity.composite.pdf";
  multiplicity.width=1900; multiplicity.height=2350; multiplicity.textPixels=18;
  Panel ratio{}; ratio.id="lower.ratio"; ratio.geometry={0.,.06,1.,.24};
  ratio.margins={.16,.04,.25,0.}; ratio.xLow=0.; ratio.xHigh=350.;
  ratio.yLow=1./36.; ratio.yHigh=2.5; ratio.logY=true;
  Series curve{}; curve.mode="histogram";
  for (const auto& item:std::vector<std::pair<double,double>>{{0.,4.},{10.,1.}}) {
    Point p{};p.x=item.first;p.y=item.second;p.error=0.;p.state="DRAW";
    p.binLow=item.first;p.binHigh=item.first+10.;curve.points.push_back(p);
  }
  ratio.series.push_back(curve);multiplicity.panels.push_back(ratio);
  (void)PanelLabelText(multiplicity,0);
  if (multiplicity.panels[0].yHigh!=2.5) return 5;
  // A shifted short spectrum caption must not acquire a fictitious .56-pad
  // width.  Its tune key fits in the native top-right space at unchanged size.
  Page spectrum{}; spectrum.filename="G9_-5122_phi.pdf";
  spectrum.role="spectra.signed_heavy"; spectrum.width=1100;
  spectrum.height=1200; spectrum.textPixels=18;
  Panel absolute{}; absolute.id="g9.absolute";
  absolute.geometry={0.,.34,1.,.90};
  absolute.margins={.16,.04,0.,1.8*20./672.};
  absolute.annotations={
      {.22404740259740258,.8919642857142857,20.,
       "PYTHIA 8.317; pp, #sqrt{#it{s}} = 13.6 TeV"},
      {.22404740259740258,.8532738095238095,20.,
       "Hard c#bar{c}, b#bar{b}; #hat{p}_{T} #geq 2 GeV/c; |#eta| #leq 4"},
      {.22404740259740258,.8145833333333333,20.,
       "Normalized probability per bin"}};
  for (const std::string tune : {"MONASH","JUNCTIONS","CLOSEPACKING"}) {
    Series sample{}; sample.tune=tune; absolute.series.push_back(sample);
  }
  spectrum.panels.push_back(absolute);
  const auto key=InsideTuneLegendBox(spectrum,spectrum.panels[0],3);
  if (!Close(key[2],1.-.04-.65*20./1100.) ||
      !Close(key[3],1.-1.8*20./672.-.65*20./672.)) return 6;
  for (const auto& box:PanelAnnotationBoxes(spectrum,spectrum.panels[0]))
    if (BoxesOverlap(key,box)) return 7;
  return 0;
}
'''
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cpp, binary = root / 'panel_label_move.cpp', root / 'panel_label_move'
            cpp.write_text(source)
            flags = shlex.split(subprocess.check_output(
                ['root-config', '--cflags', '--libs'], text=True))
            built = subprocess.run(
                ['c++', '-std=c++17', '-I', str(ROOT), str(cpp),
                 '-o', str(binary)] + flags, capture_output=True, text=True)
            self.assertEqual(built.returncode, 0, built.stderr)
            run = subprocess.run([str(binary)], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)

    @unittest.skipUnless(shutil.which('root-config'), 'ROOT development files required')
    def test_native_panel_label_ignores_nondrawable_log_domain_points(self):
        source = r'''#define main render_program_main
#include "pipeline/plot/render.cpp"
#undef main
int main() {
  Page page{};page.width=1000;page.height=1000;page.textPixels=18;
  page.filename="domain.pdf";
  Panel panel{};panel.id="ratio";panel.geometry={0.,0.,1.,1.};
  panel.margins={.15,.04,.12,.08};panel.xLow=0.;panel.xHigh=10.;
  panel.yLow=.1;panel.yHigh=10.;panel.logY=true;
  Series series{};series.mode="points";
  for (const auto& item:std::vector<std::pair<double,double>>{{1.,0.},{2.,-1.},{20.,9.}}) {
    Point point{};point.x=item.first;point.y=item.second;point.error=0.;
    point.state="DRAW";series.points.push_back(point);
  }
  panel.series.push_back(series);page.panels.push_back(panel);
  const auto base=BasePanelLabelText(page,0);
  const auto label=PanelLabelText(page,0);
  if (label.x!=base.x || label.y!=base.y) return 1;
  if (!PanelDataBoxes(page,page.panels[0],0).empty()) return 2;
  if (page.panels[0].yLow!=.1 || page.panels[0].yHigh!=10.) return 3;
  return 0;
}
'''
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cpp, binary = root / 'panel_label_domain.cpp', root / 'panel_label_domain'
            cpp.write_text(source)
            flags = shlex.split(subprocess.check_output(
                ['root-config', '--cflags', '--libs'], text=True))
            built = subprocess.run(
                ['c++', '-std=c++17', '-I', str(ROOT), str(cpp),
                 '-o', str(binary)] + flags, capture_output=True, text=True)
            self.assertEqual(built.returncode, 0, built.stderr)
            run = subprocess.run([str(binary)], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)

    @unittest.skipUnless(shutil.which('root-config'), 'ROOT development files required')
    def test_native_band_gaps_and_unavailable_errors(self):
        # A known bin topology supplies the oracle independently of the
        # renderer's serialized drawing-record verifier.
        source = r'''#define main render_program_main
#include "pipeline/plot/render.cpp"
#undef main
int main() {
  Page page{}; page.role="correlations.beauty";
  Panel panel{}; panel.logY=true; panel.xLow=0.; panel.xHigh=43.;
  panel.yLow=1.e-6; panel.yHigh=10.; panel.uncertaintyDisplay="DENSE_BAND";
  Series series{}; series.mode="histogram"; series.tune="MONASH";
  for (int i=0;i<43;++i) {
    Point q{}; q.bin=i; q.x=i+.5; q.y=1.; q.error=.2;
    q.binLow=i; q.binHigh=i+1.; q.state="DRAW";
    series.points.push_back(q);
  }
  series.points[3].state="LOG_NONPOSITIVE"; series.points[3].y=0.;
  series.points[7].error=std::numeric_limits<double>::quiet_NaN();
  series.points[10].state="MISSING_VALUE";
  series.points[14].binLow=14.25;
  const auto graphs=ExpectedGraphs(page,panel,series,0,0);
  const std::vector<std::pair<double,double>> ranges={{0,3},{4,7},{8,10},{11,14},{14.25,43}};
  std::size_t bands=0; bool central=false;
  for (const auto& g:graphs) {
    if (g.title.rfind("band:",0)==0) {
      if (bands>=ranges.size() || g.x.front()!=ranges[bands].first ||
          g.x.back()!=ranges[bands].second || g.x.size()%2) return 1;
      for (std::size_t i=0;i<g.x.size();i+=2) {
        if (g.y[i]!=1. || g.ey[i]!=.2 || g.y[i+1]!=1. || g.ey[i+1]!=.2) return 2;
        if (i && g.x[i]!=g.x[i-1]) return 3;
      }
      ++bands;
    }
    if (g.title.rfind("points:",0)==0) {
      central=true;
      if (g.x.size()!=41 || std::find(g.x.begin(),g.x.end(),7.5)==g.x.end()) return 4;
    }
    if (g.title.rfind("dense_markers:",0)==0 &&
        std::find(g.x.begin(),g.x.end(),10.5)!=g.x.end()) return 5;
  }
  if (LogBoundaryLabel(1.e-5)!="10^{-5}" ||
      LogBoundaryLabel(8.e-9)!="8#times10^{-9}") return 7;
  panel.id="correlation.teaching.521.identified";
  panel.yLow=1.e-5;panel.margins[0]=.2;
  page.panels={panel};
  const auto text=CanvasSupplementTexts(page);
  if (text.empty() || text.front().text!="10^{-5}") return 8;
  Page shortPage{};shortPage.role="correlations.charm";
  shortPage.width=1900;shortPage.height=2600;shortPage.textPixels=34;
  Panel shortPanel{};shortPanel.id="correlation.main.421.SS";
  shortPanel.geometry={0.,.4,.55,.6};
  shortPanel.margins[3]=3.*34./520.;
  const double baseline=PanelTitleY(shortPage,shortPanel);
  if (baseline+34./520.>=1. || baseline<=1.-shortPanel.margins[3]+34./520.) return 9;
  Page speciesRatioPage{};speciesRatioPage.role="balancing.baryon_meson.activity";
  speciesRatioPage.width=1900;speciesRatioPage.height=1600;speciesRatioPage.textPixels=34;
  Panel speciesRatioPanel{};speciesRatioPanel.id="upper.beauty.521";
  speciesRatioPanel.margins[3]=.067;
  for (double height : {.4,.57,.7}) {
    speciesRatioPanel.geometry={0.,0.,.54,height};
    const double clearance=(PanelTitleY(speciesRatioPage,speciesRatioPanel)-
        (1.-speciesRatioPanel.margins[3]))*1600.*height;
    if (clearance<.5*34. || clearance>.75*34.) return 15;
  }
  Page ratioPage{}; ratioPage.role="balancing.activity.charm";
  Panel ratioPanel{}; ratioPanel.id="lower.shared.421";
  ratioPanel.logY=false; ratioPanel.margins={.2,.04,.2,0.};
  for (const auto& bounds : std::vector<std::pair<double,double>>{
      {.84177,1.38667},{-.08,2.5},{-.1,38.},{-.2,4.4},
      {-9.985178551920804,149.29991045093084}}) {
    ratioPanel.yLow=bounds.first; ratioPanel.yHigh=bounds.second;
    Double_t low=0.,high=0.,width=0.;Int_t intervals=0;
    THLimitsFinder::Optimize(bounds.first,bounds.second,
        YAxisDivisions(ratioPage,ratioPanel,false)%100,low,high,intervals,width);
    const auto labels=JoinedYAxisLabelPolicy(ratioPage,ratioPanel,false);
    const int visible=intervals+1-labels.suppressFirst-labels.suppressLast;
    if (visible<3 || visible>6 || width<=0.) return 10;
    if (ratioPanel.yLow!=bounds.first || ratioPanel.yHigh!=bounds.second) return 11;
  }
  ratioPage.role="multiplicity.composite";
  ratioPanel.id="lower.ratio";
  ratioPanel.yLow=-.08;ratioPanel.yHigh=2.5;
  ratioPage.panels={ratioPanel};
  const auto boundary=CanvasSupplementTexts(ratioPage);
  if (boundary.empty() || boundary.front().text!="2.5" ||
      !JoinedYAxisLabelPolicy(ratioPage,ratioPanel,false).suppressLast) return 12;
  // A short panel must not clip a title with bars, primes and neutral signs.
  // Its page anchor stays fixed when ownership moves out of the small pad.
  gROOT->SetBatch(true);
  Page titled{}; titled.role="balancing.activity.beauty";
  titled.width=1900; titled.height=2850; titled.textPixels=34;
  Panel small{}; small.id="upper.MONASH.5122";
  small.geometry={.54,.55,1.,.75}; small.margins={0.,.04,0.,.15};
  small.title="(b) #it{#Lambda}_{b}^{0} trigger: #bar{#it{#Xi}}_{b}^{'0}";
  titled.panels={small};
  const auto titles=CanvasPanelTitleTexts(titled);
  if (titles.size()!=1 ||
      titles[0].text!="#it{#Lambda}_{b}^{0} trigger: #bar{#it{#Xi}}_{b}^{'0}" ||
      std::abs(titles[0].x-(.54+.46*.025))>1.e-12 ||
      std::abs(titles[0].y-(.55+.20*.94))>1.e-12 ||
      titles[0].size!=BodyTextPixels(titled)+1) return 16;
  TCanvas titleCanvas("title_bounds","title_bounds",1900,2850);
  VerifyCanvasTitleBounds(titleCanvas,titled);
  titled.panels[0].geometry={.54,.98,1.,1.};
  bool refused=false;
  try { VerifyCanvasTitleBounds(titleCanvas,titled); }
  catch (const std::exception&) { refused=true; }
  if (!refused) return 17;
  Page activity{}; activity.role="balancing.activity.charm";
  activity.filename="supplemental.balancing.activity.charm.extremes.pdf";
  activity.width=1900;activity.height=2950;activity.textPixels=18;
  Panel topKey{};topKey.id="upper.MONASH.4122";
  topKey.geometry={.54,.6,1.,.9};topKey.margins={0.,.04,0.,.1};
  topKey.xLow=.5;topKey.xHigh=7.5;topKey.yLow=0.;topKey.yHigh=10.;
  topKey.annotations.push_back({.02,.3,18.,"scientific text"});
  Panel middle=topKey;middle.id="upper.JUNCTIONS.4122";
  middle.geometry={.54,.3,1.,.6};middle.annotations.clear();
  for (int style=2;style<=4;++style) {
    Series item{};item.tune="MONASH";item.lineStyle=style;
    item.label=style==2 ? "0-1%" : style==3 ? "40-50%" : "80-90%";
    item.mode="categories";item.marker="none";
    topKey.series.push_back(item);item.tune="JUNCTIONS";
    Point q{};q.x=6.;q.y=8.;q.error=.2;q.state="DRAW";
    item.points.push_back(q);middle.series.push_back(item);
  }
  activity.panels={topKey,middle};
  const auto key=ActivityClassKey(activity);
  if (key.first!=&activity.panels[1] || key.second[3]>=.75) return 18;
  const double font=TuneLegendTextPixels(activity);
  if (!ClassKeyClearsData(activity,*key.first,key.second,
      .65*font/(1900*.46),.65*font/(2950*.3))) return 19;
  return bands==ranges.size() && central ? 0 : 6;
}
'''
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); cpp=root/'band.cpp'; binary=root/'band'
            cpp.write_text(source)
            flags=shlex.split(subprocess.check_output(['root-config','--cflags','--libs'],text=True))
            built = subprocess.run(['c++','-std=c++17','-I',str(ROOT),str(cpp),'-o',str(binary)]+flags,
                                   capture_output=True,text=True)
            self.assertEqual(built.returncode, 0, built.stderr)
            subprocess.run([str(binary)],check=True,capture_output=True,text=True)

    @unittest.skipUnless(shutil.which('root-config') and shutil.which('pdftoppm'),
                         'ROOT and Poppler required')
    def test_panel_title_glyphs_render_above_short_pad_boundary(self):
        # The visible oracle is independent of the renderer's text inventory:
        # the bar/prime/superscript must put raster ink above the panel top.
        source = r'''#define main render_program_main
#include "pipeline/plot/render.cpp"
#undef main
int main(int argc, char** argv) {
  if (argc != 2) return 1;
  gROOT->SetBatch(true); gStyle->SetOptStat(0); gErrorIgnoreLevel=kWarning;
  const std::filesystem::path output(argv[1]);
  std::filesystem::create_directory(output);
  std::filesystem::current_path(output);
  Page page{}; page.filename="title.pdf";
  page.role="balancing.activity.beauty";
  page.width=600; page.height=600; page.textPixels=34;
  Panel panel{}; panel.id="upper.MONASH.5122";
  panel.geometry={.1,.4,.9,.6}; panel.margins={.12,.04,.12,.15};
  panel.xLow=0.; panel.xHigh=1.; panel.yLow=0.; panel.yHigh=1.;
  panel.title="(b) #it{#Lambda}_{b}^{0}: #bar{#it{#Xi}}_{b}^{'0}";
  page.panels={panel};
  std::vector<Page> pages={page};
  TFile archive("canvases.root","CREATE");
  DrawPage(page,".",pages,archive); archive.Close();
  return 0;
}
'''
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); cpp=root/'title.cpp'; binary=root/'title'
            cpp.write_text(source)
            flags=shlex.split(subprocess.check_output(
                ['root-config','--cflags','--libs'],text=True))
            built=subprocess.run(
                ['c++','-std=c++17','-I',str(ROOT),str(cpp),'-o',str(binary)]+flags,
                capture_output=True,text=True)
            self.assertEqual(built.returncode,0,built.stderr)
            subprocess.run([str(binary),str(root/'out')],check=True,
                           capture_output=True,text=True)
            subprocess.run(['pdftoppm','-gray','-singlefile','-scale-to-x','1200',
                            '-scale-to-y','-1',str(root/'out/title.pdf'),
                            str(root/'title')],check=True,capture_output=True)
            payload=(root/'title.pgm').read_bytes()
            magic,width,height,maxval,pixels=payload.split(maxsplit=4)
            self.assertEqual((magic,int(width),int(maxval)),(b'P5',1200,255))
            height=int(height); width=int(width)
            # ROOT places the square canvas at the bottom of its default PDF
            # sheet.  Panel top is y=0.6 NDC within that canvas.  Ink in the
            # preceding 3.5% band can only come from uncut title glyphs.
            panel_top=height-round(.6*width)
            y0=panel_top-round(.035*width); y1=panel_top-2
            x0=round(.10*width); x1=round(.78*width)
            dark=sum(pixels[y*width+x] < 245
                     for y in range(y0,y1) for x in range(x0,x1))
            occupied=[y for y in range(height)
                      if any(pixels[y*width+x] < 245 for x in range(x0,x1))]
            runs=[]
            for y in occupied:
                if not runs or y > runs[-1][-1]+1: runs.append([y])
                else: runs[-1].append(y)
            self.assertGreater(
                dark,30,
                f'title glyphs were clipped at panel top; image={width}x{height}; '
                f'occupied row runs={[(r[0],r[-1]) for r in runs]}')

    @unittest.skipUnless(shutil.which('root-config'), 'ROOT development files required')
    def test_each_canvas_restores_band_color_and_alpha_in_a_fresh_process(self):
        source = r'''#define main render_program_main
#include "pipeline/plot/render.cpp"
#undef main
int main(int argc, char** argv) {
  gROOT->SetBatch(true);
  if (argc != 3) return 1;
  if (std::string(argv[1]) == "write") {
    TFile file(argv[2], "CREATE");
    for (int i=0;i<2;++i) {
      TCanvas canvas(("canvas"+std::to_string(i)).c_str(), "", 400, 400);
      TGraphErrors graph(2);
      graph.SetTitle("band:fixture");
      graph.SetPoint(0,0.,1.); graph.SetPoint(1,1.,1.);
      graph.SetPointError(0,0.,.2); graph.SetPointError(1,0.,.2);
      graph.SetFillColorAlpha(TColor::GetColor("#0077BB"), .12);
      graph.SetFillStyle(1001); graph.Draw("A3");
      canvas.Update(); file.cd(); WriteCanvas(canvas, canvas.GetName());
    }
    file.Close(); return 0;
  }
  TFile file(argv[2], "READ");
  for (int i=0;i<2;++i) {
    auto* canvas=dynamic_cast<TCanvas*>(file.Get(("canvas"+std::to_string(i)).c_str()));
    if (!canvas) return 2;
    // Ordinary collaborator usage must restore opacity without our verifier.
    canvas->Draw(); canvas->Modified(); canvas->Update();
    for (const int index : BandColors(*canvas)) {
      auto* color=gROOT->GetColor(index);
      if (!color || !StoredFloatClose(color->GetAlpha(),.12) ||
          !StoredFloatClose(color->GetGreen(),119./255.) ||
          !StoredFloatClose(color->GetBlue(),187./255.)) return 3;
    }
    VerifyBandAlpha(*canvas);
    auto* alpha=dynamic_cast<TExec*>(canvas->GetListOfPrimitives()->First());
    alpha->SetTitle("gROOT->GetColor(1)->SetAlpha(0.5f);");
    try { VerifyBandAlpha(*canvas); return 4; } catch (const std::runtime_error&) {}
  }
  return 0;
}
'''
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); cpp=root/'palette.cpp'; binary=root/'palette'
            cpp.write_text(source)
            flags=shlex.split(subprocess.check_output(['root-config','--cflags','--libs'],text=True))
            built=subprocess.run(['c++','-std=c++17','-I',str(ROOT),str(cpp),'-o',str(binary)]+flags,
                                 capture_output=True,text=True)
            self.assertEqual(built.returncode,0,built.stderr)
            for mode in ('write','read'):
                result=subprocess.run([str(binary),mode,str(root/'canvases.root')],
                                      capture_output=True,text=True)
                self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    @unittest.skipUnless(shutil.which('gs') and shutil.which('pdffonts') and
                         shutil.which('root-config'), 'ROOT, Ghostscript and Poppler required')
    def test_pdf_embedding_rejects_unembedded_and_is_repeatable(self):
        try:
            import ROOT as native
        except ImportError:
            self.skipTest('PyROOT required')
        native.gROOT.SetBatch(True)
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); original=root/'original.pdf'
            canvas=native.TCanvas('font_test','',600,500)
            latex=native.TLatex(); latex.SetNDC(); latex.DrawLatex(.2,.5,'#Delta#varphi; #Lambda_{b}^{0}')
            canvas.SaveAs(str(original)); canvas.Close()
            with self.assertRaisesRegex(ValueError,'unembedded'):
                plot.verify_pdf_fonts(original)
            products=[]
            for name in ('first','second'):
                if products: time.sleep(1.05)  # Cross the exporter clock quantum.
                directory=root/name; directory.mkdir(); path=directory/'figure.pdf'
                path.write_bytes(original.read_bytes()); plot.publication_pdf(path)
                self.assertGreater(plot.verify_pdf_fonts(path),0)
                products.append(path.read_bytes())
            self.assertEqual(products[0],products[1])

    def test_export_trailer_identity_preserves_objects_and_refuses_malformed_id(self):
        prefix=b'%PDF-1.4\n1 0 obj\n<</Title (/ID is ordinary text)>>\nendobj\n'
        def pdf(identifier):
            return prefix+b'xref\n0 2\n0000000000 65535 f \n0000000009 00000 n \ntrailer\n<< /Size 2 '+identifier+b' >>\nstartxref\n'+str(len(prefix)).encode()+b'\n%%EOF\n'
        identity='ab'*16
        source=pdf(b'/ID [<'+b'01'*16+b'><'+b'23'*16+b'>]')
        expected=pdf(b'/ID [<'+identity.encode()+b'><'+identity.encode()+b'>]')
        self.assertEqual(plot.canonical_export_pdf(source,identity),expected)
        self.assertEqual(plot.canonical_export_pdf(pdf(b''),identity),pdf(b''))
        self.assertEqual(len(expected),len(source))
        for value in (b'(abcdefghijklmnop)',rb'(abc\050\051\134\n\r\t\b\fghijk)',
                      b'('+b'\\377'*16+b')'):
            self.assertEqual(plot.canonical_export_pdf(pdf(b'/ID ['+value+value+b']'),identity),expected)
            self.assertEqual(plot.canonical_export_pdf(pdf(b'/ID ['+value+b'<'+b'01'*16+b'>]'),identity),expected)
        for malformed in (b'/ID [<01><23>]',b'/ID (bad)',b'/ID [<'+b'zz'*16+b'><'+b'01'*16+b'>]',
                          b'/ID [(short)(short)]',b'/ID [(abcdefghijklmnop)(unterminated]',
                          b'/ID [(abcdefghijklmnop)(abcdefghijklmnop)(abcdefghijklmnop)]',
                          b'/ID [(abcdefghijklmnop)(abcdefghijklmnop)] /ID (bad)'):
            with self.assertRaisesRegex(ValueError,'trailer ID'):
                plot.canonical_export_pdf(pdf(malformed),identity)

    def test_spectrum_key_headroom_keeps_data_and_ratio_scale(self):
        import copy
        absolute = {'id':'g9.absolute', 'geometry':[0.,.34,1.,.9],
                    'margins':[.16,.04,0.,.13], 'x_range':[-3.,3.],
                    'y_range':[.0099,.0101], 'log_y':False,
                    'series':[{'tune':tune, 'points':[
                        {'state':'DRAW','y':.01008,'error':.000015,
                         'bin_high':3.,'display_x':2.9},
                        {'state':'MISSING_VALUE','y':None,'error':None}]} for tune in
                              ['MONASH','JUNCTIONS','CLOSEPACKING']]}
        ratio = {'id':'g9.ratio', 'y_range':[.97,1.04], 'series':[]}
        page = {'role':'spectra.signed_heavy', 'text_pixels':18,
                'width':1100, 'height':1200, 'panels':[absolute,ratio]}
        original = copy.deepcopy(page)
        plot.reserve_spectrum_tune_key([page])
        self.assertGreater(absolute['y_range'][1],.0101)
        self.assertEqual(absolute['y_range'][0],.0099)
        self.assertEqual(absolute['series'],original['panels'][0]['series'])
        self.assertEqual(ratio,original['panels'][1])

    def test_in_frame_spectrum_caption_reserves_space_without_changing_data(self):
        import copy
        absolute={'id':'g9.absolute','geometry':[0.,.34,1.,.9],
            'margins':[.16,.04,0.,.06],'x_range':[-3.,3.],
            'y_range':[.0099,.0101],'log_y':False,
            'annotations':[{'x':.2,'y':.8,'size':20.,'text':'Sample'},
                           {'x':.2,'y':.7,'size':20.,'text':'Acceptance'}],
            'series':[{'points':[{'state':'DRAW','y':.01008,'error':.000015,
                'bin_low':-3.,'bin_high':3.,'display_x':0.}]}]}
        ratio={'id':'g9.ratio','geometry':[0.,0.,1.,.34],
               'y_range':[.97,1.04],'series':[]}
        page={'role':'spectra.signed_heavy','text_pixels':18,
              'width':1100,'height':1200,'panels':[absolute,ratio]}
        original=copy.deepcopy(page)
        plot.reserve_annotation_headroom([page])
        lo,hi=absolute['y_range']
        envelope=(.010095-lo)/(hi-lo)*.94
        self.assertLess(envelope,.7)
        self.assertEqual(absolute['series'],original['panels'][0]['series'])
        self.assertEqual(ratio,original['panels'][1])

    def test_panel_label_moves_complete_annotation_block_without_rewriting_it(self):
        import copy
        panel={'id':'g9.absolute','geometry':[0.,.34,1.,.9],
               'margins':[.16,.04,0.,.06], 'annotations':[], 'reuse':None}
        page={'role':'spectra.signed_heavy','filename':'G9_421_eta.pdf',
              'text_pixels':18,'width':1100,'height':1200,'panels':[panel]}
        label=plot.panel_label_reserved_box(page,panel)
        panel['annotations']=[
            {'x':label[0],'y':.88,'size':20.,'text':'PYTHIA 8.317'},
            {'x':label[0],'y':.84,'size':20.,'text':'Hard sample'}]
        before=copy.deepcopy(panel['annotations'])
        self.assertTrue(plot.boxes_overlap(
            plot.annotation_box(page,panel,panel['annotations']),label))
        plot.move_annotation_blocks_from_panel_labels([page])
        after=panel['annotations']
        self.assertFalse(plot.boxes_overlap(
            plot.annotation_box(page,panel,after),label))
        self.assertEqual([a['text'] for a in after],[a['text'] for a in before])
        dx=[a['x']-b['x'] for a,b in zip(after,before)]
        dy=[a['y']-b['y'] for a,b in zip(after,before)]
        self.assertTrue(dx[0] or dy[0])
        self.assertTrue(all(abs(value-dx[0])<1.e-12 for value in dx))
        self.assertTrue(all(abs(value-dy[0])<1.e-12 for value in dy))
        self.assertAlmostEqual(after[0]['y']-after[1]['y'],
                               before[0]['y']-before[1]['y'])

    def test_final_layout_preserves_fixed_ratio_range_and_complete_stack_scale(self):
        ratio={'id':'lower.ratio','log_y':True,
               'y_range':[1./36.,2.5], 'reuse':None}
        page={'role':'multiplicity.composite','filename':'multiplicity.composite.pdf',
              'panels':[ratio]}
        plot.verify_common_comparison_y_ranges([page])
        self.assertEqual(ratio['y_range'],[1./36.,2.5])
        panels=[]
        for tune,row in zip(('MONASH','JUNCTIONS','CLOSEPACKING'),range(3)):
            for pdg,column in ((521,0),(5122,1)):
                panels.append({'id':f'upper.{tune}.{pdg}',
                    'geometry':[column/2.,.3-row*.1,(column+1)/2.,.4-row*.1],
                    'y_range':[-.01,.14], 'log_y':False, 'reuse':None})
        activity={'role':'balancing.activity.beauty',
                  'filename':'balancing.activity.beauty.pdf','panels':panels}
        plot.verify_common_comparison_y_ranges([activity])
        panels[-1]['y_range'][1]=.15
        with self.assertRaisesRegex(ValueError,'common y scale'):
            plot.verify_common_comparison_y_ranges([activity])

    def test_corner_anchor_headroom_preserves_cap_and_bounds_real_clearance(self):
        beauty_panel={'id':'correlation.compare.5122.SS','geometry':[.5,.32,1.,.42],
            'margins':[0.,.04,0.,0.], 'x_range':[-math.pi/2,3*math.pi/2],
            'y_range':[.06088085489355096,6.759116416652745],
            'log_x':False,'log_y':True,'reuse':None,'annotations':[],
            'series':[{'draw_mode':'histogram','points':[{
                'state':'DRAW','display_x':-1.413716694115407,
                'bin_low':-math.pi/2,'bin_high':-1.2566370614359172,
                'y':4.545770498718472,'error':None}]}]}
        beauty={'role':'correlations.beauty','filename':'correlations.beauty.pdf',
                'width':1900,'height':2850,'text_pixels':18,
                'panels':[beauty_panel]}
        plot.reserve_panel_label_data_headroom([beauty])
        # A closer label now intersects this first bin.  Permit only the
        # modest required headroom, not the former 486.98 range regression.
        self.assertGreater(beauty_panel['y_range'][1],6.759116416652745)
        self.assertLess(beauty_panel['y_range'][1],13.)

        multiplicity_panel={'id':'lower.ratio','geometry':[0.,.06,1.,.24],
            'margins':[.16,.04,.25,0.], 'x_range':[0.,350.],
            'y_range':[1./36.,2.5], 'log_x':False,'log_y':True,
            'reuse':None,'annotations':[],
            'series':[{'draw_mode':'histogram','points':[{
                'state':'DRAW','display_x':5.,'bin_low':0.,'bin_high':10.,
                'y':4.,'error':0.}]}]}
        multiplicity={'role':'multiplicity.composite',
            'filename':'multiplicity.composite.pdf','width':1900,'height':2350,
            'text_pixels':18,'panels':[multiplicity_panel]}
        plot.reserve_panel_label_data_headroom([multiplicity])
        self.assertEqual(multiplicity_panel['y_range'][1],2.5)

        # A real charm-correlation geometry whose upper-left data occupy the
        # fixed anchor receives bounded display clearance, while the renderer
        # coordinate remains immutable.
        charm_panel={'id':'correlation.compare.4122.OS',
            'geometry':[.5,.52,1.,.62], 'margins':[0.,.04,0.,0.],
            'x_range':[-math.pi/2,3*math.pi/2], 'y_range':[.58,1.32],
            'log_x':False,'log_y':False,'reuse':None,'annotations':[],
            'series':[{'draw_mode':'histogram','points':[{
                'state':'DRAW','display_x':-1.3,'bin_low':-1.4,'bin_high':-1.2,
                'y':1.30,'error':.02}]}]}
        charm={'role':'correlations.charm','filename':'correlations.charm.pdf',
               'width':1900,'height':2600,'text_pixels':18,
               'panels':[charm_panel]}
        plot.reserve_panel_label_data_headroom([charm])
        self.assertGreater(charm_panel['y_range'][1],1.32)
        label=plot.panel_label_reserved_box(charm,charm_panel)
        panel_height=charm['height']*(charm_panel['geometry'][3]-
                                      charm_panel['geometry'][1])
        frame_height=1.-charm_panel['margins'][2]-charm_panel['margins'][3]
        fraction=(1.32-charm_panel['y_range'][0]) / (
            charm_panel['y_range'][1]-charm_panel['y_range'][0])
        native_top=(charm_panel['margins'][2]+fraction*frame_height+
                    .34*plot.body_text_pixels(charm)/panel_height)
        self.assertLessEqual(native_top+1./panel_height,label[1]+1.e-12)

    def test_panel_label_headroom_counts_ink_outside_stored_bin(self):
        panel={'id':'upper','geometry':[0.,0.,1.,1.],
               'margins':[.16,.04,.1,.05],'x_range':[0.,10.],
               'y_range':[0.,1.],'log_x':False,'log_y':False,
               'reuse':None,'annotations':[],'series':[]}
        page={'role':'spectra.signed_heavy','filename':'ink.pdf',
              'width':1100,'height':700,'text_pixels':18,'panels':[panel]}
        label=plot.panel_label_reserved_box(page,panel)
        # The numerical bin misses the label, but the marker's visible ink
        # reaches it. Preparation must match the native reopen validator.
        x=(label[0]-.003-panel['margins'][0])/.8*10.
        panel['series']=[{'draw_mode':'histogram','points':[{
            'state':'DRAW','display_x':x,'bin_low':x-.001,
            'bin_high':x+.001,'y':.97,'error':.01}]}]
        self.assertLess(panel['series'][0]['points'][0]['bin_high'],
                        (label[0]-.16)/.8*10.)
        plot.reserve_panel_label_data_headroom([page])
        self.assertGreater(panel['y_range'][1],1.)
        self.assertLess(panel['y_range'][1],1.3)
        top=.1+.85*.98/panel['y_range'][1]+.34*plot.body_text_pixels(page)/700.
        self.assertLess(top,label[1])

    def test_spectrum_key_preserves_an_already_clear_frame(self):
        import copy
        panel = {'id':'g9.absolute', 'geometry':[0.,.34,1.,.9],
                 'margins':[.16,.04,0.,.13], 'x_range':[0.,250.],
                 'y_range':[-.01,.2], 'log_y':False,
                 'series':[{'tune':tune, 'points':[
                     {'state':'DRAW','y':.1,'error':.002,
                      'bin_high':5.,'display_x':2.5},
                     {'state':'DRAW','y':0.,'error':None,
                      'bin_high':250.,'display_x':249.}]} for tune in
                           ['MONASH','JUNCTIONS','CLOSEPACKING']]}
        page = {'role':'spectra.signed_heavy','text_pixels':18,
                'width':1100,'height':1200,'panels':[panel]}
        original = copy.deepcopy(page)
        plot.reserve_spectrum_tune_key([page])
        self.assertEqual(page,original)

    def test_dense_flat_spectrum_has_physical_clearance_for_publication_key(self):
        # The native legend uses 9-point body text at 18 cm paper width.
        # A dense flat spectrum cannot provide a spare horizontal gap.
        for top_margin in (.13, .2321428571428571):
            panel = {'id':'g9.absolute', 'geometry':[0.,.34,1.,.90],
                     'margins':[.16,.04,0.,top_margin],
                     'x_range':[-math.pi,math.pi], 'y_range':[.0097,.0103],
                     'log_y':False, 'series':[{'tune':tune,'points':[
                         {'state':'DRAW','y':.01,'error':.0002,
                          'display_x':-math.pi+(i+.5)*2*math.pi/100,
                          'bin_high':-math.pi+(i+1)*2*math.pi/100}
                         for i in range(100)]} for tune in
                         ('MONASH','JUNCTIONS','CLOSEPACKING')]}
            page = {'role':'spectra.signed_heavy','text_pixels':18,
                    'width':1100,'height':1200,'panels':[panel]}
            plot.reserve_spectrum_tune_key([page])
            low,high = panel['y_range']
            clearance = (high-.0102)/(high-low)*672*(1-top_margin)
            # Three rows, plus native frame and error-envelope separation.
            self.assertGreaterEqual(clearance, (1.65*3+.975)*20)

    def test_class_pattern_digest_matches_native_renderer(self):
        config,_=plot.checked_plot_config(ROOT/'config/plot.json')
        digest=plot.sha_bytes(plot.canonical(
            config['style_identities']['class_line_patterns']).encode())
        self.assertIn('class_patterns_sha256='+digest,
                      (ROOT/'pipeline/plot/render.cpp').read_text())

    def test_density_label_requires_explicit_numerical_units(self):
        self.assertEqual(plot.correlation_y_title([]),
                         'Correlation yield (units unavailable)')
        row = {'quantity':'dphi_per_trigger','units':'per_trigger_per_bin'}
        self.assertIn('per bin',plot.correlation_y_title([row]))
        row['quantity']='dphi_density_per_trigger'
        with self.assertRaisesRegex(ValueError,'units disagree'):
            plot.correlation_y_title([row])
        row['units']='per_trigger_per_radian'
        self.assertIn('d#Delta#varphi',plot.correlation_y_title([row]))
        self.assertIn('N}_{OS}',plot.correlation_y_title([row],'OS_MINUS_SS'))
        with self.assertRaisesRegex(ValueError,'mixed numerical units'):
            plot.correlation_y_title([row,{'quantity':'dphi_per_trigger',
                                          'units':'per_trigger_per_bin'}])

    def test_compact_caption_deduplicates_only_equal_eta_acceptance(self):
        context=SimpleNamespace(target_analysis_caption='PYTHIA 8.317',
            sample_caption=['Hard c and b'], profile_definition={
                'trigger_eta':{'high':float(4).hex()},
                'trigger_pt':{'low':None}}, activity_selection={
                'pt':{'low':float(.15).hex()},'eta_window':float(4).hex()})
        lines=plot.scientific_caption_lines({'role':'balancing.activity.charm'},context)
        self.assertEqual(sum(line.count('|#eta|') for line in lines),1)
        self.assertIn('p_{T} > 0.15 GeV/c; |#eta| #leq 4',lines)
        context.activity_selection['eta_window']=float(1).hex()
        lines=plot.scientific_caption_lines({'role':'balancing.activity.charm'},context)
        self.assertIn('|#eta| #leq 4',lines)
        self.assertIn('p_{T} > 0.15 GeV/c; |#eta| #leq 1',lines)

    def test_threshold_caption_keeps_pair_and_activity_cuts_distinct(self):
        context=SimpleNamespace(target_analysis_caption='PYTHIA 8.317',
            sample_caption=['Hard c and b'], profile_definition={
                'trigger_eta':{'high':float(4).hex()},
                'trigger_pt':{'low':float(1).hex()},
                'associate_pt':{'low':float(.15).hex()}}, activity_selection={
                'pt':{'low':float(.15).hex()},'eta_window':float(4).hex()})
        for role in ('correlations.charm', 'balancing.integrated.beauty',
                     'balancing.activity.charm', 'balancing.baryon_meson.activity'):
            lines=plot.scientific_caption_lines({'role':role},context)
            text=' '.join(lines)
            self.assertIn('p_{T}^{trig} #geq 1',text)
            self.assertIn('p_{T}^{assoc} #geq 0.15 GeV/c',text)
            self.assertEqual(text.count('|#eta|'),1)
            if 'activity' in role:
                self.assertIn('p_{T} > 0.15 GeV/c',text)
        context.activity_selection['eta_window']=float(1).hex()
        lines=plot.scientific_caption_lines({'role':'balancing.activity.charm'},context)
        self.assertEqual(' '.join(lines).count('|#eta|'),2)
        context.profile_definition['trigger_pt']['low']=None
        lines=plot.scientific_caption_lines({'role':'correlations.charm'},context)
        self.assertNotIn('Pairs:', ' '.join(lines))

    def test_baryon_comparison_views_preserve_signed_rows_and_canonical_page(self):
        rows = [dict(trigger_pdg=str(t), associate_pdg=str(a),
                     reference_pdg=str(r), value='0.2') for t,a,r in (
                         (421,-4122,-421), (4122,-4122,-421),
                         (421,-4132,-421), (4122,-4132,-421),
                         (521,5122,-521), (5122,-5122,521),
                         (521,5132,-521), (5122,-5132,521))]
        config,_ = plot.checked_plot_config(ROOT/'config/plot.json')
        presentation = {'trigger_sectors': {'421':'charm','4122':'charm',
                                            '521':'beauty','5122':'beauty'}}
        views = plot.baryon_meson_views(rows, presentation,
                                       config['presets']['paper_default'])
        self.assertEqual(len(views),5)
        self.assertEqual(views[0][1], [rows[0],rows[4]])
        self.assertEqual(views[0][2], [421,521])
        by_name = {name:(members,triggers) for name,members,triggers in views[1:]}
        members,triggers = by_name['supplemental.balancing.baryon_meson.activity.beauty.5132.by_trigger.pdf']
        self.assertEqual(triggers,[521,5122])
        self.assertEqual(members,[rows[6],rows[7]])
        for _,members,_ in views:
            for row in members:
                self.assertTrue(any(row is original for original in rows))

    def test_display_limits_keep_clipped_points_and_errors(self):
        import copy
        panels=[{'id':'lower.ratio','y_range':[-.2,18.], 'log_y':False,
                 'series':[{'points':[{'y':17.,'error':2.}]}]},
                {'id':'correlation.teaching.421.identified',
                 'y_range':[1e-10,.1], 'log_y':True,
                 'series':[{'points':[{'y':1e-8,'error':1e-9}]}]}]
        original=copy.deepcopy(panels)
        plot.apply_display_limits([
            {'role':'multiplicity.composite','panels':[panels[0]]},
            {'role':'correlations.charm','panels':[panels[1]]}])
        self.assertEqual(panels[0]['y_range'],[-.08,2.5])
        self.assertEqual(panels[1]['y_range'],[8e-9,.1])
        for before,after in zip(original,panels):
            self.assertEqual(before['series'],after['series'])

    def test_log_ratio_axes_preserve_signed_science_and_upper_panels(self):
        import copy
        points = [dict(semantic_id=str(i), state='DRAW', y=y, error=error,
                       value_status='VALID', uncertainty_status='AVAILABLE')
                  for i, (y,error) in enumerate(((0.,.2),(-.4,.3),(.1,.3),(1.,.1),(20.,2.)))]
        points.append(dict(semantic_id='missing',state='MISSING_VALUE',y=None,error=None))
        upper = dict(id='upper.421',log_y=False,y_range=[-.5,21.],
                     series=[dict(points=copy.deepcopy(points))],guides=[])
        panels = [upper] + [dict(id=key,log_y=False,y_range=[-.5,21.],
                   series=[dict(points=copy.deepcopy(points))],guides=[
                   dict(id='unity',y_low=1.,y_high=1.),
                   dict(id='signed_zero',y_low=0.,y_high=0.)])
                   for key in ('lower.shared.421','correlation.compare.421.OS', 'g9.ratio')]
        before = copy.deepcopy(panels)
        config = dict(layout=dict(tune_ratio_y_scale='log',axis_padding_fraction=.08))
        plot.apply_tune_ratio_scale([dict(role='balancing.activity.charm',panels=panels)],config)
        self.assertEqual(panels[0], before[0])
        for panel, original in zip(panels[1:], before[1:]):
            self.assertTrue(panel['log_y'])
            self.assertGreater(panel['y_range'][0],0.)
            self.assertLess(panel['y_range'][0],.1)
            self.assertGreater(panel['y_range'][1],22.)
            self.assertEqual([g['id'] for g in panel['guides']],['unity'])
            for actual, old in zip(panel['series'][0]['points'],original['series'][0]['points']):
                for key in old:
                    if key!='state':self.assertEqual(actual[key],old[key])
                self.assertEqual(actual['state'],'LOG_NONPOSITIVE' if old['y'] is not None and old['y']<=0 else old['state'])
        panel=copy.deepcopy(before[1]);panel['id']='lower.ratio'
        plot.apply_tune_ratio_scale([dict(role='multiplicity.composite',panels=[panel])],config)
        self.assertEqual(panel['y_range'][1],2.5)
        config['layout']['tune_ratio_y_scale']='linear'
        unchanged=copy.deepcopy(before)
        plot.apply_tune_ratio_scale([dict(role='test',panels=unchanged)],config)
        self.assertEqual(unchanged,before)

    def test_focused_intervals_never_use_nearby_class(self):
        classes=[{'id':'5','integrated':False,'percentile_interval':[0.,2.]},
                 {'id':'7','integrated':False,'percentile_interval':[40.,50.]},
                 {'id':'9','integrated':False,'percentile_interval':[90.,100.]}]
        self.assertEqual(plot.selected_extreme_class_ids(classes),['7'])
        self.assertEqual(plot.focused_extreme_pages([],SimpleNamespace(
            tunes=['MONASH','JUNCTIONS'],classes=classes),.08),[])

    def test_species_display_order_groups_content_and_preserves_signed_membership(self):
        charm = ['-411', '-421', '-431', '-4122', '-4112', '-4212',
                 '-4222', '-4132', '-4232', '-4332']
        beauty = ['-521', '-511', '-531', '-541', '5122', '5112',
                  '5222', '5132', '5232', '5332']
        self.assertEqual(plot.species_display_order(charm),
                         ['-421','-411','-431','-4122','-4212','-4112',
                          '-4222','-4232','-4132','-4332'])
        self.assertEqual(plot.species_display_order(beauty),
                         ['-521','-511','-531','-541','5122','5222',
                          '5112','5232','5132','5332'])
        for species in (charm, beauty):
            opposite = [str(-int(pdg)) for pdg in species]
            self.assertEqual(plot.species_display_order(opposite),
                [str(-int(pdg)) for pdg in plot.species_display_order(species)])
            self.assertCountEqual(plot.species_display_order(species),species)
        with self.assertRaisesRegex(ValueError, 'baryon-content'):
            plot.species_display_order(['999999'])

    def test_full_catalog_labels_keep_excitation_and_conjugation(self):
        states=json.loads((ROOT/'config/heavy-catalog.json').read_text())['states']
        states=[s for s in states if s['nc']!=s['ncbar'] or s['nb']!=s['nbbar']]
        self.assertEqual(len(states),202)
        for state in states:
            label=plot.species_latex_label(state['pdg'],state['name'])
            self.assertIn('#it{',label)
            if '*' in state['name']:self.assertIn('*',label)
            if "'" in state['name']:self.assertIn("'",label)
            if 'bar' in state['name']:self.assertIn('#bar{',label)
            self.assertEqual(label.count('{'),label.count('}'))
        self.assertEqual(len(plot.species_display_order([str(s['pdg']) for s in states])),202)
        self.assertEqual(plot.species_latex_label(-10421,'D*_0bar0'),
                         '#bar{#it{D}}_{0}^{*0}')

    def test_separate_species_pdfs_are_exact_point_subsets(self):
        import copy
        role='balancing.integrated.charm'
        order=plot.species_display_order([str(-s) for s in
            (421,411,431,4122,413,423,433,4112,4212,4222,4132,4312,4314)])
        panels=[]
        original={}
        for trigger in ('421','4122'):
            for prefix in ('upper.','lower.shared.'):
                points=[dict(semantic_id=prefix+trigger+':'+pdg,
                    scientific_x=float(i),display_x=float(i),x=float(i),
                    y=float(i)/10,error=.001,state='DRAW')
                    for i,pdg in enumerate(order,1)]
                original.update((p['semantic_id'],copy.deepcopy(p)) for p in points)
                panels.append(dict(id=prefix+trigger,series=[dict(points=points)],
                    ticks=[dict(x=i,label=pdg) for i,pdg in enumerate(order,1)],
                    guides=[],x_range=[.5,len(order)+.5],y_range=[0,2],
                    geometry=[0,.1,.5,.9],margins=[.2,0,.1,.1],
                    title='Trigger',status='AVAILABLE'))
        source=dict(role=role,filename='balancing_integrated_charm.pdf',width=1900,panels=panels)
        config=json.loads((ROOT/'config/plot.json').read_text())
        pages=plot.balancing_species_views([source],SimpleNamespace(
            category_orders={role:{'421':order,'4122':order}}),config)
        self.assertEqual(len(pages),3)
        self.assertEqual(len({p['filename'] for p in pages}),len(pages))
        self.assertTrue(all(p['page_count']==p['page_index']==1 for p in pages))
        for panel in pages[0]['panels']:
            self.assertEqual([t['label'] for t in panel['ticks']],['-421','-411','-431','-4122','-4212','-4112','-4222'])
        seen=[]
        for page in pages[1:]:
            self.assertNotIn('.part-',page['filename'])
            self.assertEqual(len(page['panels']),2)
            for panel in page['panels']:
                self.assertEqual(len(panel['ticks']),len(order))
                self.assertEqual((panel['geometry'][0],panel['geometry'][2]),(0.,1.))
                for point in panel['series'][0]['points']:
                    before=original[point['semantic_id']]
                    for field in ('semantic_id','y','error','state'):
                        self.assertEqual(point[field],before[field])
                    seen.append(point['semantic_id'])
        self.assertCountEqual(seen,original)

    def test_display_selection_excludes_higher_numbered_states(self):
        config=json.loads((ROOT/'config/plot.json').read_text())
        selected=set(config['layout']['balancing_species_views']['expanded_abs_pdgs'])
        self.assertEqual(len(selected),71)
        self.assertTrue({421,423,431,433,4122,4312,4314,511,513,5312,5314} <= selected)
        self.assertTrue({415,425,435,4124,10411,10413,14122,20413,515,10513,20513}.isdisjoint(selected))

    def test_excited_partners_follow_each_ground_state(self):
        self.assertEqual(plot.species_display_order(
            ['-531','-523','-513','-521','-511','-533']),
            ['-521','-523','-511','-513','-531','-533'])
        self.assertEqual(plot.species_display_order(
            ['4314','4132','4322','4232','4324','4312']),
            ['4232','4322','4324','4132','4312','4314'])
        self.assertEqual(plot.species_display_order(
            ['-5114','-5212','-5224','-5222','-5214','-5112']),
            ['-5222','-5224','-5212','-5214','-5112','-5114'])

    def test_complete_species_axis_preserves_physical_text_size(self):
        page=dict(filename='supplemental.balancing.activity.beauty.trigger-521.pdf',
                  width=4300,text_pixels=18)
        self.assertAlmostEqual(plot.paper_width_cm(page),18*43/19)
        self.assertEqual(plot.body_text_pixels(page),34)
        page.update(width=1900)
        self.assertEqual(plot.body_text_pixels(page),34)

    def test_individual_species_views_refuse_unbound_numerical_grouping(self):
        config=json.loads((ROOT/'config/plot.json').read_text())
        context=SimpleNamespace(cold=True,parent_artifact_digests=['0'*64])
        with self.assertRaisesRegex(ValueError,'pinned numerical grouping'):
            plot.balancing_species_views([],context,config)
        context.parent_artifact_digests=[config['layout'][
            'balancing_species_views']['grouping_recipe_sha256']]
        self.assertEqual(plot.balancing_species_views([],context,config),[])

    def test_species_subset_keeps_undefined_ratio_materialization(self):
        point=dict(semantic_id='ratio',state='MISSING_VALUE',
            value_status='UNDEFINED',uncertainty_status='UNDEFINED_CENTER',
            reasons='ZERO_DENOMINATOR')
        context=SimpleNamespace(materialization_by_semantic_id={
            'ratio':dict(status='PRESENT',reason_codes=[])})
        panel=dict(id='lower.shared.421',series=[dict(points=[point])])
        plot.selected_panel_status(panel,context,[])
        self.assertEqual(panel['status'],'PRESENT_UNDEFINED')
        self.assertEqual(panel['note'],'')
        panel['id']='upper.421'
        plot.selected_panel_status(panel,context,[])
        self.assertIn('zero denominator',panel['note'])

    def test_joined_columns_have_equal_width_and_do_not_change_data(self):
        import copy
        panels=[]
        for index in range(2):
            panels.append(dict(id=str(index),geometry=[index*.5,.3,(index+1)*.5,.9],
                margins=[.2,.035,0.,.17],y_range=[.1,10.],log_y=True,
                y_title='Balancing yield',title='Trigger '+str(index),
                series=[{'points':[{'semantic_id':str(index),'y':1.,'error':.2}]}]))
        original=copy.deepcopy(panels)
        plot.join_paired_columns([{'panels':panels}])
        left,right=panels
        self.assertEqual(left['geometry'][2],right['geometry'][0])
        self.assertEqual((left['margins'][1],right['margins'][0]),(0.,0.))
        self.assertAlmostEqual((left['geometry'][2]-left['geometry'][0])*
            (1-left['margins'][0]),(right['geometry'][2]-right['geometry'][0])*
            (1-right['margins'][1]))
        self.assertEqual(right['y_title'],'')
        for actual,before in zip(panels,original):
            for field in ('series','y_range','log_y','title'):
                self.assertEqual(actual[field],before[field])
        right['y_range']=[.1,11.]
        with self.assertRaisesRegex(ValueError,'share their y axis'):
            plot.join_paired_columns([{'panels':panels}])

    def test_joined_baryon_ratio_panels_keep_each_signed_identity(self):
        panels=[dict(geometry=[i*.5,.3,(i+1)*.5,.9],margins=[.2,.035,0.,.17],
            y_range=[0.,1.],log_y=False,title='trigger '+str(i),
            y_title='signed ratio '+str(i)) for i in range(2)]
        plot.join_paired_columns([{'panels':panels}])
        self.assertEqual(panels[0]['y_title'],'Balancing yield ratio')
        self.assertEqual(panels[1]['y_title'],'')
        for i,panel in enumerate(panels):
            self.assertIn('signed ratio '+str(i),panel['title'])

    def test_public_cold_command_imports_reader_from_external_cwd(self):
        with tempfile.TemporaryDirectory(dir=ROOT.parent) as directory:
            external = Path(directory)
            result = subprocess.run([
                sys.executable, str(ROOT / 'hadronization'), 'plot',
                'render-cold', '--numerics-root',
                str(external / 'missing.root'), '--expected-root-sha256',
                '0' * 64, '--expected-value-sha256', '0' * 64,
                '--work-dir', str(external / 'work'), '--output',
                str(external / 'output')], cwd=external,
                capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn('v4 ROOT differs from trusted physical hash', result.stderr)
            self.assertNotIn('ModuleNotFoundError', result.stderr)

    def test_p1_owner_inset_is_large_lower_left(self):
        config, _ = plot.checked_plot_config(ROOT / "config/plot.json")
        self.assertEqual(config["layout"]["p1_inset_geometry"],
                         [.18, .05, .65, .48])
        self.assertEqual(config['layout']['correlation_view'],
                         'monash_pair_sign')
        self.assertEqual(config['presets']['paper_default']['trigger_pdgs'][0],
                         421)

    def test_p1_nested_inset_preserves_reference_physical_aspect(self):
        relative=[.15,.05,.62,.48]
        original=plot.nested_inset_geometry(relative,[0.,.31,1.,1.],1800,1650)
        for actual,expected in zip(original,[.15,.31+.05*.69,.62,.31+.48*.69]):
            self.assertAlmostEqual(actual,expected)
        original_aspect=(original[2]-original[0])*1800/((original[3]-original[1])*1650)
        for width,height,parent in ((1050,1360,[0.,.26,1.,.98]),
                                     (1050,1360,[0.,0.,1.,.98])):
            mapped=plot.nested_inset_geometry(relative,parent,width,height)
            self.assertAlmostEqual((mapped[2]-mapped[0])*width/
                                   ((mapped[3]-mapped[1])*height),original_aspect)
            self.assertAlmostEqual((mapped[1]-parent[1])/(parent[3]-parent[1]),.05)

    def test_centers_only_teaching_discloses_hidden_nonzero_errors(self):
        point={'state':'DRAW','error':.2}
        panel={'id':'correlation.teaching.421.identified',
               'uncertainty_display':'CENTERS_ONLY',
               'series':[{'points':[point]}]}
        page={'role':'correlations.charm','panels':[panel],
              'information':'Exact-zero SE saved in ROOT'}
        self.assertIn('lacks visible SE disclosure',
                      plot.review_uncertainty_presentation(page))
        page['information']=(
            'P2-P8: no final-hadron pT floor; '+
            plot.CORRELATION_CENTER_ONLY_DISCLOSURE)
        self.assertIsNone(plot.review_uncertainty_presentation(page))
        panel['uncertainty_display']='STANDARD'
        page['information']=''
        self.assertIsNone(plot.review_uncertainty_presentation(page))
        point['error']=0.
        self.assertIn('lacks retained finite-MC error',
                      plot.review_uncertainty_presentation(page))

    def test_identified_subtraction_pad_keeps_the_shared_frame(self):
        upper = dict(id='correlation.teaching.4122.identified',
            geometry=[.5,.48,1.,.97], margins=[.17,.04,.13,.10],
            x_range=[-1.,1.])
        lower = dict(id='correlation.teaching.4122.subtraction',
            geometry=[.5,.05,1.,.48], margins=[.17,.04,.29,.10],
            x_range=[-1.,1.])
        plot.join_ratio_pads([dict(role='correlations.charm',panels=[upper,lower])])
        self.assertEqual(upper['margins'][2], 0.)
        self.assertEqual(lower['margins'][3], 0.)
        self.assertEqual(upper['geometry'][1], lower['geometry'][3])

    def test_identified_subtraction_never_selects_all_associate_sum(self):
        rows = []
        for trigger in (411, 421, 4122, 521, 5122):
            for associate in (str(-trigger), '', '-431'):
                for component in ('OS', 'SS', 'OS_MINUS_SS'):
                    rows.append(dict(trigger_pdg=str(trigger),
                        associate_pdg=associate, component=component,
                        quantity='dphi_density_per_trigger'))
        selected = plot.identified_correlation_rows(rows)
        self.assertEqual(len(selected), 15)
        for trigger in (411, 421, 4122, 521, 5122):
            members = [r for r in selected if r['trigger_pdg']==str(trigger)]
            self.assertEqual({r['component'] for r in members},
                             {'OS', 'SS', 'OS_MINUS_SS'})
            self.assertEqual({r['associate_pdg'] for r in members},
                             {str(-trigger)})
        self.assertTrue(all(any(row is original for original in rows)
                            for row in selected))
        # Missing native subtraction stays missing; never substitute a sum.
        missing = [row for row in rows if not (
            row['trigger_pdg']=='4122' and row['associate_pdg']=='-4122'
            and row['component']=='OS_MINUS_SS')]
        self.assertFalse(any(row['trigger_pdg']=='4122' and
                             row['component']=='OS_MINUS_SS'
                             for row in plot.identified_correlation_rows(missing)))

    def test_dplus_and_all_tune_are_explicit_presentation_alternates(self):
        config, _ = plot.checked_plot_config(ROOT / "config/plot.json")
        dplus, _ = plot.checked_plot_config(ROOT / "config/plot-dplus.json")
        all_tune, _ = plot.checked_plot_config(ROOT / "config/plot-all-tune.json")
        self.assertEqual(dplus['presets']['paper_default']['trigger_pdgs'],
                         [411, 4122, 521, 5122])
        self.assertEqual(dplus['layout']['correlation_view'],
                         'monash_pair_sign')
        self.assertEqual(all_tune['presets']['paper_default']['trigger_pdgs'],
                         [421, 4122, 521, 5122])
        self.assertEqual(all_tune['layout']['correlation_view'],
                         'all_tune_ratio')
        config['presets']['paper_default']['trigger_pdgs'][0] = 411
        config['presets']['paper_default']['baryon_meson_trigger_pdgs'][0] = 411
        config['layout']['correlation_view'] = 'all_tune_ratio'
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            path = Path(directory) / 'plot.json'
            path.write_text(json.dumps(config), encoding='utf-8')
            checked, _ = plot.checked_plot_config(path)
        self.assertEqual(checked['layout']['correlation_view'],
                         'all_tune_ratio')

    def test_p1_authenticated_extent_retains_observed_tail(self):
        series = [{"points": [
            {"state": "DRAW", "y": 0.3, "error": 0.01,
             "support_low": 0., "support_high": 1.},
            {"state": "DRAW", "y": 0.0002, "error": None,
             "support_low": 163., "support_high": 164.},
            {"state": "DRAW", "y": 0., "error": 0.,
             "support_low": 4095., "support_high": 4096.},
        ]}]
        main, inset = plot.checked_p1_occupied_support(
            {"low": 0., "positive_low": 1., "high": 164.}, series)
        self.assertEqual(main, [0., 164.])
        self.assertEqual(inset, [1., 164.])
        with self.assertRaisesRegex(ValueError, "crops materialized tail"):
            plot.checked_p1_occupied_support(
                {"low": 0., "positive_low": 1., "high": 163.}, series)
        with self.assertRaisesRegex(ValueError, "geometry"):
            plot.checked_p1_occupied_support(
                {"low": 1., "positive_low": 1., "high": 164.}, series)

    def test_p1_finite_withheld_ratio_error_has_visible_disclosure(self):
        points = [
            {'state': 'DRAW', 'y': 1.2, 'error': .1},
            {'state': 'DRAW', 'y': .8, 'error': None},
            {'state': 'MISSING', 'y': None, 'error': None},
        ]
        self.assertEqual(plot.p1_ratio_uncertainty_note(
            'multiplicity.composite', 'lower.ratio', points, 'old note'),
            plot.P1_WITHHELD_SE_DISCLOSURE)
        self.assertNotIn('?', plot.P1_WITHHELD_SE_DISCLOSURE)
        self.assertEqual(plot.p1_ratio_uncertainty_note(
            'multiplicity.composite', 'upper.distribution', points,
            'old note'), 'old note')

    def test_p1_paper_range_uses_complete_reference_support(self):
        series = [
            {"tune": "MONASH", "points": [
                {"state": "DRAW", "y": 0.3, "support_high": 1.},
                {"state": "DRAW", "y": 1e-8, "support_high": 374.},
                {"state": "MISSING", "y": None, "support_high": 4096.},
            ]},
            {"tune": "CLOSEPACKING", "points": [
                {"state": "DRAW", "y": 1e-8, "support_high": 2109.},
            ]},
        ]
        self.assertEqual(
            plot.p1_reference_display_high(series, "MONASH"), 374.)
        with self.assertRaisesRegex(ValueError, "no positive occupied"):
            plot.p1_reference_display_high(series, "ABSENT")

    def test_category_order_preserves_signed_five_channel_beauty(self):
        order = ["-521", "-511", "-531", "-541", "5122"]
        self.assertEqual(plot.checked_category_order(
            order, set(order), False, "balancing.integrated.beauty", "521"),
            order)
        self.assertEqual(plot.checked_category_order(
            order, {"-521", "-511"}, True,
            "balancing.integrated.beauty", "521"), order)
        for mutant in (order[:-1], order[:-1] + ["-5122"],
                       order[:-1] + ["-521"]):
            with self.subTest(mutant=mutant), self.assertRaises(ValueError):
                plot.checked_category_order(
                    mutant, set(order), False,
                    "balancing.integrated.beauty", "521")

    def test_correlation_requires_all_three_component_comparisons(self):
        components = ("OS", "SS", "OS_MINUS_SS")
        rows = [{"trigger_pdg": "411", "component": component,
                 "tune": "MONASH", "reference_tune": ""}
                for component in components]
        rows += [{"trigger_pdg": "411", "component": component,
                  "tune": "JUNCTIONS", "reference_tune": "MONASH"}
                 for component in components]
        self.assertTrue(plot.checked_tune_ratio_layout(
            ["MONASH", "JUNCTIONS"], "MONASH", rows,
            "correlations.charm"))
        with self.assertRaisesRegex(ValueError, "OS/SS/net"):
            plot.checked_tune_ratio_layout(
                ["MONASH", "JUNCTIONS"], "MONASH", rows[:-1],
                "correlations.charm")

    def test_reference_correlation_captions_use_registered_component_sign(self):
        for expected in (
                {421: (-421, 421), 4122: (-421, 421),
                 521: (-521, 521), 5122: (521, -521)},
                {411: (-411, 411), 4122: (-411, 411),
                 521: (-521, 521), 5122: (521, -521)}):
            registered = []
            for trigger, (opposite, same) in expected.items():
                for sign, associate in ((-1, opposite), (1, same)):
                    registered.append({"trigger_pdg": trigger, "sign": sign,
                                       "associate_pdg": associate,
                                       "reference_meson_pdg": abs(associate)})
            for trigger, (opposite, same) in expected.items():
                self.assertEqual(plot.correlation_reference_partners(
                    registered, trigger), {"OS": opposite, "SS": same})
            with self.assertRaisesRegex(ValueError, "reference pair"):
                plot.correlation_reference_partners(registered[:-1], 5122)

    def test_charm_presentation_preset_must_match_s_science_recipe(self):
        d0, _ = plot.checked_plot_config(ROOT / 'config/plot.json')
        dplus, _ = plot.checked_plot_config(ROOT / 'config/plot-dplus.json')

        def science_scope(charm):
            return {'ordered_triggers': [charm, 4122, 521, 5122],
                    'ordered_associate_pairs': [
                        {'trigger_pdg': trigger, 'sector': 'CHARM',
                         'reference_meson_pdg': -charm,
                         'associate_pdg': associate, 'sign': sign}
                        for trigger in (charm, 4122)
                        for sign, associate in (('OS', -charm),
                                                ('SS', charm))],
                    'roles': [{'role_id':
                               'balancing.baryon_meson.activity',
                               'required_curve_keys': [{'trigger_pdg': charm,
                                 'associate_pdg': -4122,
                                 'reference_pdg': -charm}]}]}

        d0_scope = science_scope(421)
        dplus_scope = science_scope(411)
        plot.checked_charm_recipe_binding(d0_scope, d0)
        plot.checked_charm_recipe_binding(dplus_scope, dplus)
        with self.assertRaisesRegex(ValueError, 'ordered triggers'):
            plot.checked_charm_recipe_binding(d0_scope, dplus)
        wrong_reference = json.loads(json.dumps(d0_scope))
        wrong_reference['ordered_associate_pairs'][0][
            'reference_meson_pdg'] = -411
        with self.assertRaisesRegex(ValueError, 'reference meson'):
            plot.checked_charm_recipe_binding(wrong_reference, d0)
        wrong_sign = json.loads(json.dumps(d0_scope))
        wrong_sign['ordered_associate_pairs'][0]['associate_pdg'] = 421
        with self.assertRaisesRegex(ValueError, 'signed pairs'):
            plot.checked_charm_recipe_binding(wrong_sign, d0)
        wrong_p8 = json.loads(json.dumps(d0_scope))
        wrong_p8['roles'][0]['required_curve_keys'][0][
            'reference_pdg'] = -411
        with self.assertRaisesRegex(ValueError, 'P8 reference'):
            plot.checked_charm_recipe_binding(wrong_p8, d0)

    def test_paper_profile_is_archived_inclusive_or_independent_minima(self):
        d0, _ = plot.checked_plot_config(ROOT / 'config/plot.json')
        dplus, _ = plot.checked_plot_config(ROOT / 'config/plot-dplus.json')
        cut = {'domain': 'PHYSICAL', 'units': 'GeV', 'low': None,
               'high': None, 'low_operator': None, 'high_operator': None}
        profile = {'id': 'inclusive',
                   'relative_pt': 'NONE',
                   'minimum_hierarchy': 'NONE',
                   'trigger_pt': dict(cut), 'associate_pt': dict(cut)}
        payload = {'schema': 'hadronization_projection_result_v4',
                   'request_echo': {'scope': {'roles': [{
                       'role_id': 'correlations.charm',
                       'required_curve_keys': [{
                           'profile_id': 'inclusive'}]}, {
                       'role_id': 'balancing.baryon_meson.activity',
                       'required_curve_keys': [{
                           'profile_id': 'inclusive'}]}]}}}
        caption = plot.checked_paper_pair_profile(payload, d0, profile)
        self.assertIn('No final-hadron #it{p}_{T} floor', caption)
        self.assertNotIn('#geq', caption)
        self.assertIn('eligible singles', caption)
        self.assertEqual(plot.checked_paper_pair_profile(
            payload, dplus, profile), caption)
        for mutation, message in (
                (dict(profile, relative_pt='TRIGGER_GE_ASSOCIATE'),
                 'no-diagonal'),
                (dict(profile, trigger_pt=dict(cut, low='0x1p-1')),
                 'unsupported pT cut')):
            with self.assertRaisesRegex(ValueError, message):
                plot.checked_paper_pair_profile(payload, d0, mutation)
        rectangle = dict(profile, id='pt_1_0p15',
            minimum_hierarchy='TRIGGER_MIN_GE_ASSOCIATE_MIN',
            trigger_pt=dict(cut, low=float(1).hex(), low_operator='GE'),
            associate_pt=dict(cut, low=float(.15).hex(), low_operator='GE'))
        cut_payload = json.loads(json.dumps(payload))
        for role in cut_payload['request_echo']['scope']['roles']:
            role['required_curve_keys'][0]['profile_id']='pt_1_0p15'
        caption = plot.checked_paper_pair_profile(cut_payload, d0, rectangle)
        self.assertIn('p_{T}^{trig} #geq 1', caption)
        self.assertIn('p_{T}^{assoc} #geq 0.15 GeV/c', caption)
        for mutation in (
            dict(rectangle, relative_pt='TRIGGER_GT_ASSOCIATE'),
            dict(rectangle, associate_pt=dict(rectangle['associate_pt'],
                                              low=float(2).hex())),
            dict(rectangle, trigger_pt=dict(rectangle['trigger_pt'],
                                            low_operator='GT')),
            dict(rectangle, trigger_pt=dict(rectangle['trigger_pt'],
                                            high=float(10).hex())),
            dict(rectangle, trigger_pt=dict(rectangle['trigger_pt'], low='inf'))):
            with self.assertRaises(ValueError):
                plot.checked_paper_pair_profile(cut_payload, d0, mutation)
        wrong_role = json.loads(json.dumps(payload))
        wrong_role['request_echo']['scope']['roles'][0][
            'required_curve_keys'][0]['profile_id'] = 'trigger_ge_associate'
        with self.assertRaisesRegex(ValueError, 'different pair profile'):
            plot.checked_paper_pair_profile(wrong_role, d0, profile)

    def test_negative_center_and_withheld_error_remain_distinct(self):
        row = {"family": "balancing", "quantity": "os_minus_ss_per_trigger",
               "value": "-2", "value_status": "AVAILABLE",
               "finite_mc_error": "", "uncertainty_status":
               "WITHHELD_UNCERTAINTY", "bin_index": "", "bin_low": "",
               "bin_high": "", "axis": "", "reference_tune": "",
               "tune": "MONASH"}
        value = plot._render_numbers(row)
        self.assertEqual(value["value"], -2.)
        self.assertIsNone(value["finite_mc_error"])
        wrong = dict(row, uncertainty_status="AVAILABLE")
        with self.assertRaisesRegex(ValueError, "uncertainty/status"):
            plot._render_numbers(wrong)

    def test_finite_v4_covariance_leaf_cannot_become_a_plotted_error(self):
        curve = {
            "role_id": "balancing.integrated.charm",
            "quantity": "os_minus_ss_per_trigger",
            "tune_id": "MONASH", "reference_tune_id": None,
            "profile_id": "inclusive", "activity_id": None,
            "class_id": None, "trigger_pdg": 421,
            "associate_pdg": -4122, "reference_pdg": -421,
            "component": "NONE", "axis_id": None,
        }
        point = {"semantic_id": "diagnostic-only", "key": {
            "curve": curve, "bins": []}, "units": "yield / trigger",
            "center": "0x1p-1", "center_status": "AVAILABLE",
            "standard_error": None,
            "uncertainty_status": "WITHHELD_UNCERTAINTY",
            "reasons": ["INCOMPLETE_BLOCK_COVERAGE"]}
        payload = {"points": [point], "covariance": [{
            "independent_families": [{
                "finite_mask": [[True]], "usable_mask": [False],
                "complements": [["0x1p-2"]]}]}]}
        row = plot.typed_point_rows(payload)[0]
        self.assertEqual(row["finite_mc_error"], "")
        self.assertIsNone(plot._render_numbers(row)["finite_mc_error"])
        point["standard_error"] = "0x1p-2"
        leaked = plot.typed_point_rows(payload)[0]
        with self.assertRaisesRegex(ValueError, "uncertainty/status"):
            plot._render_numbers(leaked)

    def test_focused_extremes_preserve_all_class_canonical_page(self):
        import copy
        classes = [{"id": "0", "integrated": True,
                    "percentile_interval": [0., 100.]}]
        intervals = [(0.,1.),(1.,10.)]+[(float(i),float(i+10))
                                                 for i in range(10,100,10)]
        classes += [{"id": str(index), "integrated": False,
                     "percentile_interval": list(interval)}
                    for index,interval in enumerate(intervals,1)]
        self.assertEqual(plot.selected_extreme_class_ids(classes),
                         ["1", "6", "10"])
        panel = {"id": "upper.411", "series": [
            {"class_id": str(index), "marker": "filled_circle",
             "points": [{"state": "DRAW",
             "y": float(index), "error": None}]}
            for index in range(1, 12)],
            "log_y": True, "x_range": [.5, 3.5],
            "y_range": [0.1, 20.], "guides": [], "note": "",
            "status": "AVAILABLE"}
        lower = copy.deepcopy(panel)
        lower['id'] = 'lower.shared.411'
        canonical = {"role": "balancing.activity.charm",
                     "panels": [panel, lower], "title": "all classes"}
        context = SimpleNamespace(
            tunes=["MONASH", "JUNCTIONS", "CLOSEPACKING"],
            classes=classes, package_state="VALIDATED_PARTIAL",
            campaign_state="PARTIAL_SAMPLE",
            numerics_schema="hadronization_projection_result_v3_g9_science")
        pages = plot.focused_extreme_pages([canonical], context, .08)
        self.assertEqual(len(pages), 1)
        self.assertEqual([series["class_id"] for series in
                          pages[0]["panels"][0]["series"]], ["1", "6", "10"])
        self.assertEqual(len(canonical["panels"][0]["series"]), 11)
        self.assertEqual({series['marker'] for series in
                          pages[0]['panels'][0]['series']}, {'filled_circle'})
        self.assertEqual({series['marker'] for series in
                          pages[0]['panels'][1]['series']}, {'filled_circle'})
        self.assertEqual({series['marker'] for series in panel['series']},
                         {'filled_circle'})
        self.assertIn("supplemental", pages[0]["filename"])

    def test_activity_marker_removal_preserves_values_and_other_roles(self):
        import copy
        point = {'y': .2, 'error': .03, 'state': 'DRAW'}
        series = {'marker': 'filled_circle', 'line_style': 2,
                  'color': '#000000', 'points': [point]}
        activity = {'role': 'balancing.activity.charm', 'panels': [
            {'id': panel_id, 'series': [copy.deepcopy(series)]}
            for panel_id in ('upper.MONASH', 'lower.shared')]}
        integrated = copy.deepcopy(activity)
        integrated['role'] = 'balancing.integrated.charm'
        pages = [activity, integrated]
        before = copy.deepcopy(pages)
        plot.activity_lines_without_markers(pages)
        for panel in activity['panels']:
            self.assertEqual(panel['series'][0]['marker'], 'none')
        self.assertEqual(integrated, before[1])
        for panel in activity['panels']:
            panel['series'][0]['marker'] = 'filled_circle'
        self.assertEqual(pages, before)

    def test_extreme_emphasis_uses_typed_intervals_not_caption(self):
        classes = [
            {"id": "0", "integrated": True,
             "percentile_interval": [0., 100.]},
            {"id": "7", "integrated": False,
             "percentile_interval": [0., 1.]},
            {"id": "2", "integrated": False,
             "percentile_interval": [40., 50.]},
            {"id": "9", "integrated": False,
             "percentile_interval": [80., 90.]},
        ]
        self.assertEqual(plot.selected_extreme_class_ids(classes),
                         ["7", "2", "9"])
        self.assertEqual([plot.activity_emphasis(
            "balancing.activity.charm", class_id, classes)
            for class_id in ("0", "7", "2", "9")],
            ["NORMAL", "EXTREME", "EXTREME", "EXTREME"])

    def test_baryon_meson_axis_names_exact_signed_particle_yields(self):
        labels = {'-4122': '#bar{#it{#Lambda}}_{c}^{-}',
                  '-421': '#bar{#it{D}}^{0}'}
        rows = [{'associate_pdg': '-4122', 'reference_pdg': '-421'},
                {'associate_pdg': '-4122', 'reference_pdg': '-421'}]
        self.assertEqual(plot.exact_particle_ratio_title(
            rows, labels.__getitem__),
            '#bar{#it{#Lambda}}_{c}^{-} / #bar{#it{D}}^{0}')
        with self.assertRaisesRegex(ValueError, 'mixes particle yield ratios'):
            plot.exact_particle_ratio_title(rows + [{
                'associate_pdg': '5122', 'reference_pdg': '-521'}],
                labels.get)

    def test_sparse_protocol_fixture_cannot_pass_style_review_gate(self):
        classes = [{"id": "0", "integrated": True,
                    "percentile_interval": [0., 100.]},
                   {"id": "1", "integrated": False,
                    "percentile_interval": [0., 10.]},
                   {"id": "2", "integrated": False,
                    "percentile_interval": [90., 100.]}]
        context = SimpleNamespace(
            campaign_state="PARTIAL_SAMPLE",
            tunes=["MONASH", "JUNCTIONS", "CLOSEPACKING"],
            reference_tune="MONASH", classes=classes)
        config, _ = plot.checked_plot_config(ROOT / "config/plot.json")
        with self.assertRaisesRegex(ValueError,
                                    "synthetic review coverage failed"):
            plot.review_packet_coverage({"pages": []}, context, config)

    def test_category_tunes_and_classes_share_scientific_centers(self):
        tunes = ["MONASH", "JUNCTIONS", "CLOSEPACKING"]
        for tune in tunes:
            self.assertEqual(plot.categorical_display_x(
                7., "balancing.baryon_meson.activity", "7", tune,
                tunes, ["7"], {}, ratio=tune != "MONASH"), 7.)
            self.assertEqual(plot.categorical_display_x(
                3., "balancing.integrated.charm", "0", tune,
                tunes, ["0"], {}, ratio=tune != "MONASH"), 3.)

    def test_joined_ratio_frames_share_edges_and_drop_lower_title(self):
        upper={"id":"upper.411","geometry":[0.,.31,.5,.89],
               "margins":[.2,.035,.1,.17],"x_range":[.5,3.5]}
        lower={"id":"lower.411","geometry":[0.,0.,.5,.30],
               "margins":[.2,.035,.43,.17],"x_range":[.5,3.5],
               "title":"duplicate"}
        pages=[{"role":"balancing.integrated.charm",
                "panels":[upper,lower]}]
        plot.join_ratio_pads(pages)
        self.assertEqual(upper['geometry'][1],lower['geometry'][3])
        self.assertEqual(upper['margins'][2],0.)
        self.assertEqual(lower['margins'][3],0.)
        self.assertEqual(lower['geometry'][1],.08)
        self.assertEqual(lower['title'],'')
        self.assertEqual(upper['x_range'],lower['x_range'])

    def test_joined_beauty_net_ratio_has_tick_label_headroom(self):
        upper={"id":"correlation.main.521.OS_MINUS_SS",
               "geometry":[0.,.45,.5,.69],"margins":[.08,.02,0.,.1],
               "x_range":[-1.,4.]}
        lower={"id":"correlation.compare.521.OS_MINUS_SS",
               "geometry":[0.,.32,.5,.44],"margins":[.08,.02,.13,0.],
               "x_range":[-1.,4.],"y_range":[.95,1.64],"title":""}
        plot.join_ratio_pads([{"role":"correlations.beauty",
                               "panels":[upper,lower]}])
        self.assertEqual(upper['geometry'][1],lower['geometry'][3])
        self.assertEqual(lower['y_range'][1],1.8)

    def test_p8_shared_x_frames_join_without_a_gap(self):
        upper={"id":"upper.charm.421", "geometry":[0.,.32,.5,.89],
               "margins":[.20,.035,.29,.21], "x_range":[.5,3.5]}
        lower={"id":"lower.charm.421", "geometry":[0.,0.,.5,.32],
               "margins":[.20,.035,.29,.21], "x_range":[.5,3.5],
               "title":"old"}
        plot.join_ratio_pads([{"role":"balancing.baryon_meson.activity",
                               "panels":[upper,lower]}])
        self.assertEqual(upper['geometry'][1], lower['geometry'][3])
        self.assertEqual(upper['margins'][2], 0.)
        self.assertEqual(lower['margins'][3], 0.)
        self.assertEqual(lower['geometry'][1], .08)
        self.assertEqual(upper['x_range'], lower['x_range'])
        self.assertEqual(lower['title'], '')

    def test_activity_pages_are_three_tune_rows_plus_one_shared_ratio_row(self):
        tunes = ['MONASH', 'JUNCTIONS', 'CLOSEPACKING']
        def panel(id_, left, right, series):
            return {'id': id_, 'geometry': [left, .3, right, .89],
                    'title': id_, 'series': series,
                    'margins': [.2, .035, .1, .17],
                    'y_title': 'old'}
        series = [{'tune': tune} for tune in tunes]
        source = {'role': 'balancing.activity.charm', 'height': 1250,
                  'panels': [
                      panel('upper.421', 0., .5, series),
                      panel('upper.4122', .5, 1., series),
                      panel('lower.421', 0., .5, series[1:]),
                      panel('lower.4122', .5, 1., series[1:])]}
        page = plot.tune_separated_activity_pages([source], tunes)[0]
        self.assertEqual([item['id'] for item in page['panels']], [
            'upper.MONASH.421', 'upper.MONASH.4122',
            'upper.JUNCTIONS.421', 'upper.JUNCTIONS.4122',
            'upper.CLOSEPACKING.421', 'upper.CLOSEPACKING.4122',
            'lower.shared.421', 'lower.shared.4122'])
        for row, tune in zip((page['panels'][0:2], page['panels'][2:4],
                              page['panels'][4:6]), tunes):
            self.assertTrue(all({entry['tune'] for entry in item['series']} ==
                                {tune} for item in row))
        for column in (0, 1):
            stack = [page['panels'][column + 2 * row]
                     for row in range(4)]
            for upper, lower in zip(stack, stack[1:]):
                self.assertAlmostEqual(upper['geometry'][1],
                                       lower['geometry'][3])
        self.assertEqual({item['y_title'] for item in page['panels'][-2:]},
                         {'TUNE/MONASH'})
        self.assertEqual([item['title'] for item in page['panels'][:6]],
                         ['upper.421', 'upper.4122', '', '', '', ''])

        source['filename'] = 'supplemental.balancing.activity.charm.extremes.pdf'
        supplemental = plot.tune_separated_activity_pages([source], tunes)[0]
        self.assertEqual(supplemental['filename'], source['filename'])
        self.assertEqual(len(supplemental['panels']), 8)

    def test_tune_separated_baryon_meson_page_keeps_one_shared_ratio_row(self):
        tunes = ['MONASH', 'JUNCTIONS', 'CLOSEPACKING']
        def panel(id_, left, right, series):
            return {'id': id_, 'geometry': [left, .32, right, .89],
                    'title': id_, 'x_title': 'old', 'y_title': 'old',
                    'series': series, 'margins': [.2, .035, .29, .21]}
        series = [{'tune': tune} for tune in tunes]
        source = {'role': 'balancing.baryon_meson.activity',
                  'filename': 'balancing.baryon_meson.activity.pdf',
                  'height': 1250, 'panels': [
                      panel('upper.charm.421', 0., .5, series),
                      panel('upper.beauty.521', .5, 1., series),
                      panel('lower.charm.421', 0., .5, series[1:]),
                      panel('lower.beauty.521', .5, 1., series[1:])]}
        page = plot.tune_separated_baryon_meson_page([source], tunes)
        self.assertEqual(page['filename'],
                         'supplemental.balancing.baryon_meson.activity.by_tune.pdf')
        self.assertEqual(len(page['panels']), 8)
        self.assertEqual([item['id'] for item in page['panels'][-2:]],
                         ['lower.shared.charm.421',
                          'lower.shared.beauty.521'])
        self.assertTrue(all(item['x_title'] ==
            'Multiplicity Percentile Interval (%)' for item in page['panels'][-2:]))
        self.assertTrue(all(item['y_title'] == 'TUNE/MONASH'
                            for item in page['panels'][-2:]))
        self.assertEqual([item['title'] for item in page['panels'][:6]],
                         ['upper.charm.421', 'upper.beauty.521',
                          '', '', '', ''])
        self.assertTrue(all(not series['legend_label']
                            for item in page['panels'][:-2]
                            for series in item['series']))

    def test_species_typography_covers_representative_mesons_and_baryons(self):
        self.assertEqual(plot.species_latex_label(421, 'Dzero'), '#it{D}^{0}')
        self.assertEqual(plot.species_latex_label(-421, 'Dzerobar'),
                         '#bar{#it{D}}^{0}')
        self.assertEqual(plot.species_latex_label(5212, 'PDG 5212'),
                         '#it{#Sigma}_{b}^{0}')
        self.assertEqual(plot.species_latex_label(-5212, 'PDG -5212'),
                         '#bar{#it{#Sigma}}_{b}^{0}')

    def test_left_and_right_facets_receive_one_shared_y_range(self):
        left = {'geometry': [0., .2, .5, .8], 'y_range': [1., 3.],
                'log_y': False}
        right = {'geometry': [.5, .2, 1., .8], 'y_range': [-2., 2.],
                 'log_y': False}
        plot.synchronize_paired_y_ranges([{'panels': [right, left]}])
        self.assertEqual(left['y_range'], [-2., 3.])
        self.assertEqual(right['y_range'], [-2., 3.])

    def test_activity_category_dividers_are_default_off(self):
        for name in ('plot.json', 'plot-dplus.json', 'plot-all-tune.json'):
            config, unused = plot.checked_plot_config(ROOT / 'config' / name)
            self.assertFalse(config['layout']['activity_category_dividers'])

    def test_owner_style_applies_to_preview_and_full_campaign(self):
        self.assertEqual(plot.p1_uncertainty_display(True),'DENSE_BAND')
        self.assertEqual(plot.p1_uncertainty_display(False),'DENSE_BAND')
        pages=[{'role':role,'title':'old heading',
                'information':'typed details','scientific_header':'old'}
               for role in ('multiplicity.composite','correlations.charm',
                            'spectra.signed_heavy')]
        preview=SimpleNamespace(target_analysis_caption='Target analysis',
                                synthetic=True,campaign_state='PARTIAL_SAMPLE',
                                numerics_schema='hadronization_projection_result_v3_g9_science')
        plot.apply_cold_page_style(pages,preview)
        self.assertEqual([p['title'] for p in pages],
                         ['Target analysis','','old heading'])
        self.assertEqual(pages[1]['information'],'')
        self.assertEqual(pages[2]['information'],'typed details')
        self.assertTrue(all(p['scientific_header']==
                            'TEST_ONLY / SYNTHETIC' for p in pages))
        full=SimpleNamespace(target_analysis_caption='PYTHIA 8.317',
                             synthetic=False,campaign_state='FULL_ACCEPTED_CAMPAIGN',
                             numerics_schema='hadronization_projection_result_v4')
        plot.apply_cold_page_style(pages,full)
        self.assertEqual([p['title'] for p in pages],
                         ['PYTHIA 8.317','','old heading'])
        self.assertTrue(all(p['scientific_header']=='' for p in pages))
        full.pair_selection_caption = 'P2-P8: no final-hadron #it{p}_{T} floor'
        plot.apply_cold_page_style(pages,full)
        self.assertEqual(pages[1]['information'],
                         full.pair_selection_caption)
        self.assertEqual(pages[2]['information'],'typed details')
        v4_partial=SimpleNamespace(target_analysis_caption='Target analysis',
            synthetic=True,campaign_state='PARTIAL_SAMPLE',
            numerics_schema='hadronization_projection_result_v4')
        plot.apply_cold_page_style(pages,v4_partial)
        self.assertTrue(all(p['scientific_header']==
            'TEST_ONLY / SYNTHETIC / PARTIAL_SAMPLE' for p in pages))

    def test_g9_signed_header_and_typed_no_draw_statuses(self):
        config,_=plot.checked_plot_config(ROOT / 'config/plot.json')
        science={
            'model_id':'G9_direct_primary_selected_no_pt_floor_eta4',
            'source_family':'kinematics','final':True,'selected':True,
            'status_low':81,'status_high':89,'origin_scope':'ALL_ORIGINS',
            'pt':{'domain':'PHYSICAL','units':'GeV','low':None,'high':None,
                  'low_operator':None,'high_operator':None},
            'eta':{'low':float(-4).hex(),'high':float(4).hex(),
                   'low_operator':'GE','high_operator':'LE'},
            'denominator':'weighted_all_origin_selected_final_same_signed_species_and_tune',
            'normalization':'per_bin_probability_no_bin_width_division',
            'units':'probability_per_bin',
            'ratio':'same_bin_probability_over_reference_tune_probability',
            'pt_flow':'negative_underflow_rejected_overflow_in_denominator_and_output',
            'eta_flow':'no_materialized_flow_inclusive_upper_endpoint',
            'phi_flow':'no_materialized_flow_inclusive_upper_endpoint',
            'axis_ids':['pt','eta','phi']}
        context=SimpleNamespace(g9_science=science,reference_tune='MONASH',
            numerics_schema='hadronization_projection_result_v4',
            axes=[{'id':'eta','variable':'g9_eta','units':'1',
                   'edges':[float(x).hex() for x in (-4,0,4)]}],
            tunes=['MONASH','JUNCTIONS'],
            g9_pages=[{'pdg':5212,'axis_id':'eta'}],
            materialization_by_semantic_id={})
        def row(semantic_id,ratio,value,value_status,uncertainty,reason):
            return {'semantic_id':semantic_id,'associate_pdg':'5212',
                    'axis':'eta','tune':'JUNCTIONS' if ratio else 'MONASH',
                    'reference_tune':'MONASH' if ratio else '',
                    'family':'kinematics','quantity':'normalized_spectrum'
                    if not ratio else 'spectrum_ratio_to_reference_tune',
                    'flow':'REGULAR','bin_low':'-4','bin_high':'0',
                    'bin_index':'0','class_id':'','units':'probability_per_bin',
                    'value':value,'value_status':value_status,
                    'finite_mc_error':'','uncertainty_status':uncertainty,
                    'reasons':reason}
        rows=[row('absolute',False,'','UNDEFINED',
                  'WITHHELD_UNCERTAINTY','G9_NONPOSITIVE_TOTAL'),
              row('ratio',True,'','UNDEFINED',
                  'WITHHELD_UNCERTAINTY','G9_NONPOSITIVE_TOTAL')]
        context.materialization_by_semantic_id={
            item['semantic_id']:{'status':'PRESENT','reason_codes':[]}
            for item in rows}
        pages=plot.g9_drawing_pages(context,rows,config,'TEST_ONLY','typed',
                                    {'5212':'#Sigma_{b}^{+}'})
        plot.apply_cold_page_style(pages,SimpleNamespace(
            numerics_schema='hadronization_projection_result_v4',
            synthetic=True,campaign_state='PARTIAL_SAMPLE'))
        self.assertEqual(pages[0]['title'],'G9 #it{#Sigma}_{b}^{0} #eta (1)')
        self.assertTrue(all(p['status']=='PRESENT_UNDEFINED'
                            for p in pages[0]['panels']))
        self.assertTrue(all('WITHHELD_UNCERTAINTY' in p['note'] and
                            'G9_NONPOSITIVE_TOTAL' in p['note']
                            for p in pages[0]['panels']))
        for item in rows:
            context.materialization_by_semantic_id[item['semantic_id']]={
                'status':'NOT_MATERIALIZED',
                'reason_codes':['ABSENT_SELECTED_SPECIES']}
        absent=plot.g9_drawing_pages(context,rows,config,'TEST_ONLY','typed',
                                     {'5212':'#Sigma_{b}^{+}'})[0]
        self.assertTrue(all(p['status']=='NOT_MATERIALIZED'
                            for p in absent['panels']))
        self.assertTrue(all('ABSENT_SELECTED_SPECIES' in p['note']
                            for p in absent['panels']))
        rows[0]['value']='0'
        rows[0]['value_status']='AVAILABLE'
        rows[0]['reasons']=''
        context.materialization_by_semantic_id['absolute']={
            'status':'PRESENT','reason_codes':[]}
        zero=plot.g9_drawing_pages(context,rows,config,'TEST_ONLY','typed',
                                   {'5212':'#Sigma_{b}^{+}'})[0]
        self.assertEqual(zero['panels'][0]['status'],'AVAILABLE')
        self.assertEqual(zero['panels'][0]['series'][0]['points'][0]['y'],0.)
        self.assertEqual(zero['panels'][0]['x_range'],[-4.,4.])

    def test_blank_paper_pad_uses_typed_materialization_not_drawability(self):
        row={'semantic_id':'point','value_status':'UNDEFINED',
             'uncertainty_status':'WITHHELD_UNCERTAINTY',
             'reasons':'ZERO_DENOMINATOR'}
        context=SimpleNamespace(materialization_by_semantic_id={
            'point':{'status':'PRESENT','reason_codes':[]}})
        self.assertEqual(plot.typed_panel_status(context,[row]),
            ('PRESENT_UNDEFINED',
             'UNDEFINED; WITHHELD_UNCERTAINTY; ZERO_DENOMINATOR'))
        self.assertEqual(plot.typed_panel_status(context,[
            dict(row,value_status='AVAILABLE')])[0],
            'PRESENT_NO_DRAWABLE_CENTER')
        compact=plot.typed_panel_status(context,[
            dict(row,reasons='DENOMINATOR_NUMERICALLY_UNRESOLVED:SOURCE_MONASH_INTERNAL'),
            dict(row,reasons='DENOMINATOR_NUMERICALLY_UNRESOLVED:SOURCE_JUNCTIONS_INTERNAL')])[1]
        self.assertEqual(compact,
            'UNDEFINED; WITHHELD_UNCERTAINTY; DENOMINATOR_NUMERICALLY_UNRESOLVED')
        self.assertEqual(plot.compact_paper_status_note(
            'PRESENT_UNDEFINED',compact),
            'SE withheld, denominator unresolved')
        self.assertEqual(plot.compact_paper_status_note(
            'PRESENT_UNDEFINED',compact+'; UNDEFINED_CENTER'),
            'SE withheld, denominator unresolved')
        context.materialization_by_semantic_id['point']={
            'status':'NOT_MATERIALIZED',
            'reason_codes':['ABSENT_SELECTED_SPECIES']}
        status,note=plot.typed_panel_status(context,[row])
        self.assertEqual(status,'NOT_MATERIALIZED')
        self.assertIn('ABSENT_SELECTED_SPECIES',note)
        self.assertEqual(plot.typed_panel_status(context,[]),
                         ('NOT_MATERIALIZED',''))

    def test_p1_caption_describes_typed_proxy_without_primary_overclaim(self):
        selection={'charged':True,'final':True,
                   'exclude_heavy_constituents':True,
                   'pt':{'low_operator':'GT'}}
        caption=plot.activity_proxy_caption(selection,0.15,4.0)
        self.assertIn('Charged primaries',caption)
        self.assertNotIn('(study definition)',caption)
        self.assertIn('heavy flavour excluded',caption)
        self.assertIn('#it{p}_{T} > 0.15 GeV/c',caption)
        self.assertIn('|#eta| #leq 4',caption)
        self.assertNotIn('primary',caption)
        with self.assertRaisesRegex(ValueError,'typed charged-final activity'):
            plot.activity_proxy_caption(dict(selection,final=False),0.15,4.0)

    def test_target_campaign_preview_uses_actual_energy_and_full_context_checked(self):
        payload={'schema':'hadronization_projection_result_v3_g9_science',
                 'request_echo':{'scope':{'ordered_tunes':
                     ['MONASH','JUNCTIONS','CLOSEPACKING']},
                     'sources':{'campaign_id':'TEST'}},
                 'provenance':{'data_limitations':
                     ['TEST_ONLY_SYNTHETIC_NO_PHYSICS'],
                     'generator_name':'TEST_ONLY','generator_version':'2',
                     'collision_system':'TEST_ONLY','energy_gev':float(0).hex()}}
        self.assertEqual(plot.target_analysis_caption(payload),
            'PYTHIA 8.317; pp, #sqrt{#it{s}} = 13.6 TeV')
        payload['provenance']['data_limitations']=[]
        payload['request_echo']['sources']['campaign_id']='HF_RUN3_V1'
        with self.assertRaisesRegex(ValueError,'contradicts target campaign'):
            plot.target_analysis_caption(payload)
        payload['request_echo']['sources']['campaign_id']='FUTURE_CAMPAIGN'
        self.assertEqual(plot.target_analysis_caption(payload),
            'TEST_ONLY 2; TEST_ONLY, #sqrt{#it{s}} = 0 TeV')

    def test_v4_partial_campaign_is_distinct_from_complete_package(self):
        v4 = {'schema':'hadronization_projection_result_v4',
              'package_state':'VALIDATED_COMPLETE',
              'campaign_state':'PARTIAL_SAMPLE'}
        self.assertTrue(plot.partial_numerics(v4))
        with self.assertRaisesRegex(ValueError, 'v4 numerical package state'):
            plot.partial_numerics(dict(v4, package_state='VALIDATED_PARTIAL'))
        v3 = dict(v4, schema='hadronization_projection_result_v3_g9_science')
        self.assertFalse(plot.partial_numerics(v3))
        self.assertTrue(plot.partial_numerics(dict(v3,
            package_state='VALIDATED_PARTIAL')))

    def test_v4_tune_permutation_keeps_target_caption(self):
        payload={'schema':'hadronization_projection_result_v4',
                 'request_echo':{'scope':{'ordered_tunes':
                     ['CLOSEPACKING','JUNCTIONS','MONASH']},
                     'sources':{'campaign_id':'HF_RUN3_V1'}},
                 'provenance':{'data_limitations':
                     ['TEST_ONLY_SYNTHETIC_NO_PHYSICS'],
                     'generator_name':'PYTHIA','generator_version':'8.317',
                     'collision_system':'pp','energy_gev':float(13600).hex()}}
        self.assertEqual(plot.target_analysis_caption(payload),
            'PYTHIA 8.317; pp, #sqrt{#it{s}} = 13.6 TeV')
        payload['provenance']['data_limitations'] = []
        self.assertEqual(plot.target_analysis_caption(payload),
            'PYTHIA 8.317; pp, #sqrt{#it{s}} = 13.6 TeV')
        payload['request_echo']['scope']['ordered_tunes'] = [
            'CLOSEPACKING','JUNCTIONS','JUNCTIONS']
        with self.assertRaisesRegex(ValueError, 'target campaign scope'):
            plot.target_analysis_caption(payload)

    def test_g9_signed_species_uses_archived_associate_key(self):
        curve = {"role_id": "spectra.signed_heavy",
                 "trigger_pdg": None, "associate_pdg": -5122}
        self.assertEqual(plot.g9_signed_species(curve), -5122)
        with self.assertRaisesRegex(ValueError, "G9 signed-species"):
            plot.g9_signed_species(dict(curve, trigger_pdg=5122))

    def test_g9_caption_uses_typed_science_record(self):
        science = {
            'model_id':'G9_direct_primary_selected_strict_pt0p15_eta4',
            'source_family':'kinematics','final':True,'selected':True,
            'status_low':81,'status_high':89,
            'pt':{'low':float(.15).hex(),'high':None,
                  'low_operator':'GT','units':'GeV'},
            'eta':{'low':float(-4.).hex(),'high':float(4.).hex(),
                   'low_operator':'GE','high_operator':'LE'},
            'denominator':'weighted_selected_final_same_signed_species_and_tune',
            'normalization':'per_bin_probability_no_bin_width_division',
            'units':'probability_per_bin',
            'ratio':'same_bin_probability_over_reference_tune_probability',
            'pt_flow':'underflow_and_overflow_in_denominator_and_output',
            'eta_flow':'no_materialized_flow_inclusive_upper_endpoint',
            'phi_flow':'no_materialized_flow_inclusive_upper_endpoint',
            'axis_ids':['pt','eta','phi'],
        }
        legacy_schema = 'hadronization_projection_result_v3_g9_science'
        current_schema = 'hadronization_projection_result_v4'
        caption, ratio, absolute = plot.g9_science_caption(
            science, 'MONASH', legacy_schema)
        self.assertIn('status 81-89', caption)
        self.assertIn('G9 selected final', caption)
        self.assertIn('#it{p}_{T} > 0.15 GeV', caption)
        self.assertIn('|#eta| #leq 4', caption)
        self.assertIn('per species/tune', caption)
        self.assertEqual(ratio, '#it{P}_{bin} / #it{P}_{bin,MONASH}')
        self.assertEqual(absolute, 'Probability / bin')
        with self.assertRaisesRegex(ValueError, 'G9 selection'):
            plot.g9_science_caption(dict(science,
                denominator='per_trigger_pair_profile'), 'MONASH', legacy_schema)
        with self.assertRaisesRegex(ValueError, 'G9 selection'):
            plot.g9_science_caption(science, 'MONASH', current_schema)
        current = dict(science,
            model_id='G9_direct_primary_selected_no_pt_floor_eta4',
            origin_scope='ALL_ORIGINS',
            pt={'domain':'PHYSICAL','units':'GeV','low':None,'high':None,
                'low_operator':None,'high_operator':None},
            denominator='weighted_all_origin_selected_final_same_signed_species_and_tune',
            pt_flow='negative_underflow_rejected_overflow_in_denominator_and_output')
        caption, ratio, absolute = plot.g9_science_caption(
            current, 'MONASH', current_schema)
        self.assertIn('all origins, no #it{p}_{T} floor', caption)
        self.assertNotIn('0.15', caption)
        self.assertIn('per species/tune', caption)
        self.assertEqual(ratio, '#it{P}_{bin} / #it{P}_{bin,MONASH}')
        self.assertEqual(absolute, 'Probability / bin')
        for mutation in (
                dict(current, origin_scope='SELECTED_HARD'),
                dict(current, pt=dict(current['pt'], low=float(.15).hex())),
                dict(current, pt=dict(current['pt'], domain='SELECTED'))):
            with self.assertRaisesRegex(ValueError, 'G9 cut'):
                plot.g9_science_caption(mutation, 'MONASH', current_schema)
        with self.assertRaisesRegex(ValueError, 'G9 selection'):
            plot.g9_science_caption(dict(current, status_low=80),
                                    'MONASH', current_schema)


if __name__ == "__main__":
    unittest.main()
