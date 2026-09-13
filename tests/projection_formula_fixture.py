"""Archived C++ projection formula oracles, independent of the retired plot CLI.

Only the two literal harnesses and three mathematical boundary tests are kept.
"""

import math
import shlex
import subprocess
from fractions import Fraction
from pathlib import Path

from helpers import ROOT


GEOMETRY_AND_RATIO = r'''
#include "projection.hpp"
#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>
#include <numeric>
#include <string>
#include <vector>
namespace HP=Hadronization::Projection;namespace HR=Hadronization::Reduction;
void family(const std::vector<std::vector<double>>& values,std::size_t component){
 for(std::size_t block=0;block<values.size();++block){if(block)std::cout<<';';
   const double value=values[block][component];
   if(std::isfinite(value))std::cout<<value;else std::cout<<'-';}
 std::cout<<'\n';
}
int main(){
 std::cout<<std::setprecision(17);
 std::cout<<HP::DeltaPhi(-HP::kPi/2,0)<<' '<<HP::DeltaPhi(3*HP::kPi/2,0)<<' '
          <<HP::DeltaPhi(.25,-.75)<<' '
          <<HP::DeltaPhi(.25,HP::AssociatePhi(.25,1.0))<<'\n';
 std::vector<std::vector<double>> a,b;
 HP::BlockSeries referencePrimitive;
 referencePrimitive.exact=true;
 for(int i=0;i<10;++i){
   a.push_back({double(i+2),double(i+5)});
   b.push_back({double(3*i+4),double(i+7)});
   referencePrimitive.values.push_back(double(3*i+4));
   referencePrimitive.absoluteErrorBounds.push_back(0.0);
 }
 auto make=[](const auto& values){return HP::Estimate(
   values,[](const auto& pooled){return HR::Ratio(0,1,pooled);});};
 const auto x=make(a),y=make(b);
 const auto ratio=HP::IndependentRatio(
   x,y,{HP::Denominator("reference_tune_numerator",referencePrimitive)});
 std::cout<<ratio.estimate.center[0]<<' '<<ratio.estimate.covariance[0]<<' '
          <<ratio.estimate.standardError[0]<<' '<<ratio.estimate.leaveMean[0]<<' '
          <<ratio.referenceLeaveMean[0]<<'\n';
 family(ratio.estimate.complements,0);
 family(ratio.referenceComplements,0);

 HP::Domains domains;for(int block=1;block<=10;++block)domains.blockIds.push_back(block);
 HP::Source source(domains);
 for(int block=1;block<=10;++block){
   source.AddCell({2,0,unsigned(block),0,0},{1.0,1.0e16,1.0,2});
   source.AddCell({2,0,unsigned(block),1,0},
                  {0.9999999999999999,1.0e16,1.0,2});
 }
 const auto net=HP::Difference(source.Series(2,0,0,0),source.Series(2,0,1,0));
 std::vector<std::vector<double>> identityBlocks(10,std::vector<double>{1.0});
 auto identity=[](const auto& pooled){return HR::FunctionValue{true,{pooled[0]}, {}};};
 const auto typed=HP::Estimate(identityBlocks,identity,
                              {HP::Denominator("typed_net",net,false)});
 auto dropped=net;dropped.absoluteErrorBounds.clear();
 const auto metadataDrop=HP::Estimate(identityBlocks,identity,
                                      {HP::Denominator("typed_net",dropped,false)});
 auto forced=net;forced.exact=true;
 const auto forcedExact=HP::Estimate(identityBlocks,identity,
                                     {HP::Denominator("typed_net",forced,false)});
 std::cout<<typed.estimate.valueStatus<<' '<<metadataDrop.estimate.valueStatus<<' '
          <<forcedExact.estimate.valueStatus<<' '<<net.values[0]<<' '
          <<net.absoluteErrorBounds[0]<<'\n';

 HR::DenominatorSeries exactZero{"cancelled_zero",std::vector<double>(10,0.0),
                                  {},false,true};
 const auto pooledZero=HP::Estimate(identityBlocks,identity,{exactZero});
 std::vector<double> complementBlocks={9,1,1,1,1,1,1,1,1,-8};
 HR::DenominatorSeries exactComplement{"cancelled_complement",complementBlocks,
                                       {},false,true};
 const auto complementZero=HP::Estimate(identityBlocks,identity,{exactComplement});
 HR::DenominatorSeries numericComplement=exactComplement;
 numericComplement.id="cancelled_numeric_complement";
 numericComplement.exact=false;
 numericComplement.absoluteErrorBounds=std::vector<double>(10,0.0);
 numericComplement.absoluteErrorBounds.back()=0.5;
 const auto complementUnresolved=HP::Estimate(identityBlocks,identity,
                                               {numericComplement});
 std::cout<<pooledZero.estimate.valueStatus<<' '
          <<complementZero.estimate.valueStatus<<' '
          <<complementZero.estimate.uncertaintyStatus<<' '
          <<complementUnresolved.estimate.valueStatus<<' '
          <<complementUnresolved.estimate.uncertaintyStatus<<'\n';

 HR::DenominatorSeries low{"low_information",{20,-1,-1,-1,-1,-1,-1,-1,-1,-1},
                            {},false,true};
 const auto cancelledLow=HP::Estimate(identityBlocks,identity,{low});
 low.algebraicallySurvives=true;
 const auto survivingLow=HP::Estimate(identityBlocks,identity,{low});
 std::cout<<cancelledLow.estimate.valueStatus<<' '
          <<cancelledLow.estimate.uncertaintyStatus<<' '
          <<cancelledLow.estimate.reasons.size()<<' '
          <<survivingLow.estimate.valueStatus<<' '
          <<survivingLow.estimate.uncertaintyStatus<<'\n';

 auto boundary=HP::Estimate(a,[](const auto& pooled){return HR::Ratio(0,1,pooled);},
                            {},{"CLASS_BOUNDARY_UNSTABLE"});
 std::cout<<boundary.estimate.center[0]<<' '<<boundary.estimate.valueStatus<<' '
          <<boundary.estimate.uncertaintyStatus<<' '
          <<boundary.estimate.covariance.size()<<' '<<boundary.diagnostic<<'\n';

 std::vector<std::vector<double>> sourceBlocks,referenceBlocks;
 std::vector<HP::BlockSeries> referenceBins(3);
 for(auto& series:referenceBins)series.exact=true;
 for(int i=0;i<10;++i){
   sourceBlocks.push_back({double(i+2),double(2*i+3),double(i+1)});
   referenceBlocks.push_back({double(2*i+5),0.0,double(i+4)});
   for(std::size_t component=0;component<3;++component){
     referenceBins[component].values.push_back(referenceBlocks.back()[component]);
     referenceBins[component].absoluteErrorBounds.push_back(0.0);
   }
 }
 auto normalized=[](const auto& blocks){
   HP::BlockSeries total;total.exact=true;
   for(const auto& block:blocks){
     total.values.push_back(std::accumulate(block.begin(),block.end(),0.0));
     total.absoluteErrorBounds.push_back(0.0);
   }
   return HP::Estimate(blocks,[](const auto& pooled){return HR::Normalized(0,3,pooled);},
                       {HP::Denominator("total",total)});
 };
 const auto vectorRatio=HP::IndependentRatio(
   normalized(sourceBlocks),normalized(referenceBlocks),
   {HP::Denominator("reference_bin_0",referenceBins[0]),
    HP::Denominator("reference_bin_1",referenceBins[1]),
    HP::Denominator("reference_bin_2",referenceBins[2])});
 std::cout<<HP::ValueStatus(vectorRatio,0)<<' '<<HP::ValueStatus(vectorRatio,1)<<' '
          <<HP::ValueStatus(vectorRatio,2)<<' '
          <<HP::UncertaintyStatus(vectorRatio,0)<<' '
          <<HP::UncertaintyStatus(vectorRatio,1)<<' '
          <<HP::UncertaintyStatus(vectorRatio,2)<<' '
          <<vectorRatio.estimate.covariance[2]<<'\n';
 family(vectorRatio.estimate.complements,0);
 family(vectorRatio.estimate.complements,2);
 family(vectorRatio.referenceComplements,0);
 family(vectorRatio.referenceComplements,2);
 int finiteInvalid=0;for(std::size_t block=0;block<10;++block){
   finiteInvalid+=std::isfinite(vectorRatio.estimate.complements[block][1]);
   finiteInvalid+=std::isfinite(vectorRatio.referenceComplements[block][1]);}
 std::cout<<finiteInvalid<<'\n';
 auto referenceSurviving=exactComplement;
 referenceSurviving.algebraicallySurvives=true;
 const auto referenceComplementFailure=HP::IndependentRatio(
   x,y,{referenceSurviving});
 std::cout<<referenceComplementFailure.estimate.center[0]<<' '
          <<HP::ValueStatus(referenceComplementFailure,0)<<' '
          <<HP::UncertaintyStatus(referenceComplementFailure,0)<<'\n';
}
'''


NESTED_RATIO = r'''
#define main plot_engine_main
#include "projection.cpp"
#undef main
int main(int argc, char** argv) {
  if (argc != 2) return 2;
  const std::string mode = argv[1];
  HP::Domains d;
  for (int k = 1; k <= 10; ++k) d.blockIds.push_back(k);
  d.tunes = {"MONASH", "JUNCTIONS", "CLOSEPACKING"};
  d.activities = {"charged_light_sector_activity_a15_v1_eta4"};
  d.triggers = {421};
  d.pairs = {{0,421,-4122,-1,-421,true,"charm"},
             {1,421,4122,1,-421,true,"charm"},
             {2,421,-421,-1,-421,true,"charm"},
             {3,421,421,1,-421,true,"charm"},
             {4,421,-4132,-1,-421,true,"charm"},
             {5,421,4132,1,-421,true,"charm"}};
  d.classes = {{0,true,0,100},{1,false,0,10}};
  const bool boundary = mode.find("boundary") != std::string::npos;
  for (int tune = 0; tune < 3; ++tune) {
    d.scopes.push_back({tune,"pair",d.tunes[tune],"inclusive",d.activities[0],
                        boundary ? 1 : 0});
    d.boundaries.push_back({tune,0,1,0,5,
        !(mode == "reference_boundary_unstable" && tune == 0),
        !(mode == "source_boundary_unresolved" && tune == 1),false});
  }
  HP::Source source(d);
  try {
    for (unsigned tune = 0; tune < 3; ++tune) {
      for (unsigned block = 1; block <= 10; ++block) {
        const double i = block - 1;
        double b = tune == 0 ? 10 : 20;
        double m = tune == 0 ? (block == 1 ? 20 : -1) : 10;
        double t = 100;
        if (mode == "regular") {
          b = tune == 0 ? 3*i+4 : i+2;
          m = tune == 0 ? i+7 : i+5;
        }
        if (mode == "ma_unstable" && tune == 1) m = block == 1 ? 20 : -1;
        if (mode == "bm_unstable" && tune == 0) b = block == 1 ? 20 : -1;
        if (mode == "mm_zero" && tune == 0) m = 0;
        if (mode == "mm_leave_zero" && tune == 0) m = block == 1 ? 20 : 0;
        if (mode == "mm_nonfinite" && tune == 0 && block == 1)
          m = std::numeric_limits<double>::quiet_NaN();
        if ((mode == "source_trigger_zero" && tune == 1) ||
            (mode == "reference_trigger_zero" && tune == 0)) t = 0;
        if (mode == "trigger_low" || mode == "trigger_leave_zero")
          t = block == 1 ? 20 : (mode == "trigger_low" ? -1 : 0);
        const auto add = [&](unsigned projection, unsigned bin, double value) {
          source.AddCell({projection,tune,block,bin,0},
                         {value,std::abs(value),value*value,1});
        };
        const bool missingTrigger =
            (mode == "source_trigger_missing" && tune == 1) ||
            (mode == "reference_trigger_missing" && tune == 0);
        if (!missingTrigger) add(3,0,t);
        add(2,0,b+7); add(2,1,7);
        if (!(mode == "mm_missing" && tune == 0)) {
          // OS/SS remain nonnegative in every finite net fixture.
          add(2,2,m < 0 ? 7 : m+7); add(2,3,m < 0 ? 7-m : 7);
        }
        add(2,4,(tune == 0 ? 10 : 20)+7); add(2,5,7);
      }
    }
    Request request;
    request.referenceTune = "MONASH";
    EmitBalancing(std::cout, source, request);
  } catch (const std::exception& error) {
    std::cout << "REJECTED " << error.what() << '\n';
  }
}
'''


def nested_rational_oracle(regular=False):
    """Exact arithmetic on independently specified additive net counts."""
    ba = [i + 2 for i in range(10)] if regular else [20] * 10
    ma = [i + 5 for i in range(10)] if regular else [10] * 10
    bm = [3 * i + 4 for i in range(10)] if regular else [10] * 10
    mm = [i + 7 for i in range(10)] if regular else [20] + [-1] * 9
    a, c, b, d = map(sum, (ba, ma, bm, mm))
    center = Fraction(a * d, c * b)
    source = [Fraction((a - x) * d, (c - y) * b)
              for x, y in zip(ba, ma)]
    reference = [Fraction(a * (d - y), c * (b - x))
                 for x, y in zip(bm, mm)]
    means = [sum(family) / 10 for family in (source, reference)]
    contributions = [Fraction(9, 10) * sum((v - mean) ** 2 for v in family)
                     for family, mean in zip((source, reference), means)]
    variance = sum(contributions)
    paired = [Fraction((a-ba[k])*(d-mm[k]), (c-ma[k])*(b-bm[k]))
              for k in range(10)]
    joint = source + reference
    joint_scatter = sum((v - sum(joint)/20) ** 2 for v in joint)
    parent_m = [Fraction(b-x, d-y) for x, y in zip(bm, mm)]
    parent_mean = sum(parent_m) / 10
    parent_variance = Fraction(9, 10) * sum((v-parent_mean)**2 for v in parent_m)
    mutants = {
        "paired_block": Fraction(9, 10) * sum((v-sum(paired)/10)**2 for v in paired),
        "pooled_20": Fraction(19, 20) * joint_scatter,
        "combined_centering": Fraction(9, 10) * joint_scatter,
        "wrong_factor": variance / Fraction(9, 10),
        "delta_denominator": contributions[0] + Fraction(a, c)**2 *
                             parent_variance / Fraction(b, d)**4,
        "raw_source_mean": sum(Fraction(a-x, c-y) for x, y in zip(ba, ma))/10,
        "bias_corrected_center": 10*center - 9*means[0],
    }
    return center, source, reference, means, contributions, variance, mutants


class ProjectionFormulaOracles:

    @classmethod
    def _compile(cls, source, source_path, output, include_generate=False,
                 include_plot=False, root=True):
        source_path.write_text(source, encoding="utf-8")
        command = [cls.environment["CXX"], "-std=c++17", "-O2", "-Wall",
                   "-Wextra", "-Wpedantic", "-Werror", str(source_path)]
        if include_generate:
            command.append("-I" + str(ROOT / "pipeline/generate"))
        if include_plot:
            command.append("-I" + str(ROOT / "pipeline/reduce"))
        if root:
            command += shlex.split(subprocess.check_output(
                [cls.environment["ROOT_CONFIG"], "--cflags", "--libs"],
                text=True, env=cls.environment))
        completed = subprocess.run(command + ["-o", str(output)],
                                   env=cls.environment, text=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if completed.returncode or completed.stdout.strip() or completed.stderr.strip():
            raise AssertionError("fixture compile failed: {}".format(
                completed.stderr.strip() or completed.stdout.strip()))


    def _nested_rows(self, mode):
        output = subprocess.check_output([str(self.base / "nested"), mode],
                                         text=True, env=self.environment)
        if output.startswith("REJECTED"):
            return output.strip()
        names = {4: "quantity", 5: "tune", 15: "associate", 22: "value",
                 23: "value_status", 24: "error", 25: "uncertainty_status",
                 26: "variance", 27: "source_mean", 28: "reference_mean",
                 29: "source", 30: "reference", 31: "reasons", 32: "diagnostic"}
        return [{name: line.split("\t")[index] for index, name in names.items()}
                for line in output.splitlines()]


    def test_nested_final_functional_exact_oracles_and_mutants(self):
        for regular in (False, True):
            with self.subTest(regular=regular):
                rows = self._nested_rows("regular" if regular else "counterexample")
                row = next(r for r in rows if r["quantity"] ==
                           "baryon_meson_ratio_to_reference_tune" and
                           r["tune"] == "JUNCTIONS" and r["associate"] == "-4122")
                center, source, reference, means, contributions, variance, mutants = \
                    nested_rational_oracle(regular)
                self.assertEqual(row["value_status"], "AVAILABLE")
                self.assertEqual(row["uncertainty_status"], "AVAILABLE")
                self.assertEqual(row["reasons"], "-")
                for key, expected in (("value", center), ("variance", variance),
                                      ("source_mean", means[0]),
                                      ("reference_mean", means[1])):
                    self.assertAlmostEqual(float.fromhex(row[key]), float(expected),
                                           places=15)
                self.assertAlmostEqual(float.fromhex(row["error"]),
                                       math.sqrt(float(variance)), places=15)
                for key, expected in (("source", source), ("reference", reference)):
                    actual = list(map(float.fromhex, row[key].split(";")))
                    self.assertEqual(len(actual), 10)
                    for found, wanted in zip(actual, expected):
                        self.assertAlmostEqual(found, float(wanted), places=15)
                self.assertEqual(sum(contributions), variance)
                if not regular:
                    self.assertEqual(center, Fraction(11, 50))
                    self.assertEqual(source, [Fraction(11, 50)] * 10)
                    self.assertEqual(reference, [Fraction(-1, 5)] +
                                     [Fraction(4, 15)] * 9)
                    self.assertEqual(contributions, [0, Fraction(441, 2500)])
                    self.assertEqual(variance, Fraction(441, 2500))
                    self.assertEqual(Fraction(21, 50)**2, variance)
                    direct = next(r for r in rows if r["quantity"] ==
                                  "baryon_meson_reference_ratio" and
                                  r["tune"] == "MONASH" and
                                  r["associate"] == "-4122")
                    self.assertEqual(direct["value_status"], "UNSTABLE_DENOMINATOR")
                    self.assertEqual(direct["uncertainty_status"],
                                     "DENOMINATOR_STATISTICALLY_UNRESOLVED")
                else:
                    # The counterexample has a constant source family and equal
                    # family means. This asymmetric oracle distinguishes those
                    # otherwise surviving paired/combined-centering mutants.
                    for name, mutant in mutants.items():
                        expected = center if name in {
                            "raw_source_mean", "bias_corrected_center"} else variance
                        self.assertNotEqual(mutant, expected, name)
                        self.assertGreater(abs(float(mutant-expected)), 1e-10, name)


    def test_nested_semantic_parent_roles_statuses_and_locality(self):
        controls = {
            "mm_zero": ("DENOMINATOR_NUMERICALLY_UNRESOLVED", "UNAVAILABLE",
                        "DENOMINATOR_NUMERICALLY_UNRESOLVED:reference_meson_os_minus_ss"),
            "mm_missing": ("POOLED_DENOMINATOR_ZERO", "UNAVAILABLE",
                           "POOLED_DENOMINATOR_ZERO:reference_meson_os_minus_ss"),
            "mm_leave_zero": ("AVAILABLE", "LEAVE_DENOMINATOR_ZERO",
                              "LEAVE_DENOMINATOR_NUMERICALLY_UNRESOLVED:reference_meson_os_minus_ss:1"),
            "ma_unstable": ("UNSTABLE_DENOMINATOR", "DENOMINATOR_STATISTICALLY_UNRESOLVED",
                            "DENOMINATOR_STATISTICALLY_UNRESOLVED:source_meson_os_minus_ss"),
            "bm_unstable": ("UNSTABLE_DENOMINATOR", "DENOMINATOR_STATISTICALLY_UNRESOLVED",
                            "DENOMINATOR_STATISTICALLY_UNRESOLVED:reference_tune_numerator_os_minus_ss"),
            "reference_boundary_unstable": ("AVAILABLE", "CLASS_BOUNDARY_UNSTABLE",
                                            "CLASS_BOUNDARY_UNSTABLE"),
            "source_boundary_unresolved": ("AVAILABLE", "CLASS_BOUNDARY_UNRESOLVED",
                                           "CLASS_BOUNDARY_UNRESOLVED"),
            "trigger_leave_zero": ("AVAILABLE", "LEAVE_DENOMINATOR_ZERO",
                                   "LEAVE_DENOMINATOR_NUMERICALLY_UNRESOLVED:source_shared_trigger:1"),
        }
        for tune in ("source", "reference"):
            for state, status in (("zero", "DENOMINATOR_NUMERICALLY_UNRESOLVED"),
                                  ("missing", "POOLED_DENOMINATOR_ZERO")):
                controls[tune + "_trigger_" + state] = (
                    status, "UNAVAILABLE", status + ":" + tune + "_shared_trigger")
        for mode, (value_status, uncertainty_status, reason) in controls.items():
            with self.subTest(mode=mode):
                rows = self._nested_rows(mode)
                nested = [r for r in rows if r["quantity"] ==
                          "baryon_meson_ratio_to_reference_tune"]
                row = next(r for r in nested if r["tune"] == "JUNCTIONS" and
                           r["associate"] == "-4122")
                self.assertEqual(row["value_status"], value_status)
                self.assertEqual(row["uncertainty_status"], uncertainty_status)
                self.assertIn(reason, row["reasons"].split(","))
                self.assertEqual(row["error"], "-")
                self.assertEqual(row["variance"], "-")
                if value_status in {"AVAILABLE", "UNSTABLE_DENOMINATOR"}:
                    self.assertTrue(math.isfinite(float.fromhex(row["value"])))
                    self.assertEqual(len(row["source"].split(";")), 10)
                    self.assertEqual(len(row["reference"].split(";")), 10)
                else:
                    self.assertEqual(row["value"], "-")
                if "boundary" in mode:
                    self.assertIn("fixed_pooled_boundary_delete_one", row["diagnostic"])
                if mode == "bm_unstable":
                    adjacent = next(r for r in nested if r["tune"] == "JUNCTIONS" and
                                    r["associate"] == "-4132")
                    self.assertEqual(adjacent["uncertainty_status"], "AVAILABLE")
                if mode.startswith("source_") or mode == "ma_unstable":
                    adjacent = next(r for r in nested if r["tune"] == "CLOSEPACKING" and
                                    r["associate"] == "-4122")
                    self.assertEqual(adjacent["uncertainty_status"], "AVAILABLE")
        self.assertEqual(self._nested_rows("mm_nonfinite"),
                         "REJECTED compact cell is duplicate or numerically invalid")
        low = next(r for r in self._nested_rows("trigger_low") if r["quantity"] ==
                   "baryon_meson_ratio_to_reference_tune" and r["tune"] == "JUNCTIONS")
        self.assertEqual((low["value_status"], low["uncertainty_status"]),
                         ("AVAILABLE", "AVAILABLE"))
        self.assertAlmostEqual(float.fromhex(low["error"]), 0.42, places=15)


    def test_independent_tune_ratio_geometry_and_mutants(self):
        output = subprocess.check_output([str(self.base / "geometry")],
                                         text=True).splitlines()
        geometry = list(map(float, output[0].split()))
        self.assertEqual(geometry[0], -math.pi / 2)
        self.assertEqual(geometry[1], -math.pi / 2)
        self.assertEqual(geometry[2:], [1.0, 1.0])
        self.assertNotEqual(round(math.pi, 6), math.pi)
        ratio, covariance, error, source_mean, reference_mean = map(
            float, output[1].split())
        first_n = [float(index + 2) for index in range(10)]
        first_d = [float(index + 5) for index in range(10)]
        second_n = [float(3 * index + 4) for index in range(10)]
        second_d = [float(index + 7) for index in range(10)]
        def estimate(numerators, denominators):
            center = sum(numerators) / sum(denominators)
            leaves = [(sum(numerators) - numerators[index]) /
                      (sum(denominators) - denominators[index])
                      for index in range(10)]
            mean = sum(leaves) / 10.0
            variance = 0.9 * sum((value - mean) ** 2 for value in leaves)
            return center, leaves, variance
        first = estimate(first_n, first_d)
        second = estimate(second_n, second_d)
        expected = first[0] / second[0]
        source_family = [value / second[0] for value in first[1]]
        reference_family = [first[0] / value for value in second[1]]
        expected_source_mean = sum(source_family) / 10.0
        expected_reference_mean = sum(reference_family) / 10.0
        source_bias_corrected_center = 10.0 * expected - 9.0 * expected_source_mean
        expected_covariance = 0.9 * (
            sum((value - expected_source_mean) ** 2
                for value in source_family) +
            sum((value - expected_reference_mean) ** 2
                for value in reference_family))
        linearized = (first[2] / second[0] ** 2 +
                      first[0] ** 2 * second[2] / second[0] ** 4)
        paired = [first[1][index] / second[1][index] for index in range(10)]
        paired_mean = sum(paired) / 10.0
        paired_covariance = 0.9 * sum((value - paired_mean) ** 2 for value in paired)
        combined_mean = sum(source_family + reference_family) / 20.0
        combined_centering = 0.9 * sum(
            (value - combined_mean) ** 2
            for value in source_family + reference_family)
        wrong_factor = expected_covariance / 0.9
        pooled_family = source_family + reference_family
        pooled_mean = sum(pooled_family) / len(pooled_family)
        pooled_tune_deletion = 19.0 / 20.0 * sum(
            (value - pooled_mean) ** 2 for value in pooled_family)
        third_n = [float(2 * index + 5) for index in range(10)]
        third_d = [float(index + 9) for index in range(10)]
        third = estimate(third_n, third_d)
        third_family = [value / second[0] for value in third[1]]
        pooled_thirty = source_family + reference_family + third_family
        pooled_thirty_mean = sum(pooled_thirty) / 30.0
        pooled_thirty_covariance = 29.0 / 30.0 * sum(
            (value - pooled_thirty_mean) ** 2 for value in pooled_thirty)
        self.assertAlmostEqual(ratio, expected, places=15)
        self.assertNotAlmostEqual(ratio, source_bias_corrected_center, places=12)
        self.assertAlmostEqual(covariance, expected_covariance, places=15)
        self.assertAlmostEqual(error, math.sqrt(expected_covariance), places=15)
        self.assertAlmostEqual(source_mean, expected_source_mean, places=15)
        self.assertAlmostEqual(reference_mean, expected_reference_mean, places=15)
        self.assertAlmostEqual(expected_covariance, 0.0017791710298199297,
                               places=16)
        self.assertAlmostEqual(linearized, 0.0017662834141002417, places=16)
        for mutant in (linearized, paired_covariance, combined_centering,
                       wrong_factor, pooled_tune_deletion,
                       pooled_thirty_covariance):
            self.assertNotAlmostEqual(mutant, expected_covariance, places=10)
        exported_source = list(map(float, output[2].split(";")))
        exported_reference = list(map(float, output[3].split(";")))
        self.assertEqual(exported_source, source_family)
        self.assertEqual(exported_reference, reference_family)
        self.assertNotEqual(exported_source, first[1])
        self.assertNotEqual(exported_reference, second[1])

        typed, dropped, forced, net_value, net_bound = output[4].split()
        self.assertEqual(typed, "DENOMINATOR_NUMERICALLY_UNRESOLVED")
        self.assertEqual((dropped, forced), ("AVAILABLE", "AVAILABLE"))
        self.assertNotEqual(float(net_value), 0.0)
        self.assertGreater(float(net_bound), abs(float(net_value)))
        pooled, cancelled_value, cancelled_uncertainty, numerical_value, \
            numerical_uncertainty = output[5].split()
        self.assertEqual(pooled, "POOLED_DENOMINATOR_ZERO")
        self.assertEqual(cancelled_value, "AVAILABLE")
        self.assertEqual(cancelled_uncertainty, "LEAVE_DENOMINATOR_ZERO")
        self.assertEqual(numerical_value, "AVAILABLE")
        self.assertEqual(numerical_uncertainty,
                         "LEAVE_DENOMINATOR_NUMERICALLY_UNRESOLVED")
        cancelled_value, cancelled_uncertainty, cancelled_reasons, \
            surviving_value, surviving_uncertainty = output[6].split()
        self.assertEqual((cancelled_value, cancelled_uncertainty,
                          cancelled_reasons),
                         ("AVAILABLE", "AVAILABLE_ZERO_DISPERSION", "0"))
        self.assertEqual(surviving_value, "UNSTABLE_DENOMINATOR")
        self.assertEqual(surviving_uncertainty,
                         "DENOMINATOR_STATISTICALLY_UNRESOLVED")
        boundary_value, value_status, uncertainty_status, covariance_size, diagnostic = \
            output[7].split()
        self.assertAlmostEqual(float(boundary_value), first[0], places=15)
        self.assertEqual(value_status, "AVAILABLE")
        self.assertEqual(uncertainty_status, "CLASS_BOUNDARY_UNSTABLE")
        self.assertEqual(covariance_size, "0")
        self.assertEqual(diagnostic, "fixed_pooled_boundary_delete_one")

        vector_status = output[8].split()
        self.assertEqual(vector_status[:3],
                         ["AVAILABLE", "POOLED_DENOMINATOR_ZERO", "AVAILABLE"])
        self.assertEqual(vector_status[3:6],
                         ["AVAILABLE", "UNAVAILABLE", "AVAILABLE"])
        vector_covariance = float(vector_status[6])
        source_zero = list(map(float, output[9].split(";")))
        source_two = list(map(float, output[10].split(";")))
        reference_zero = list(map(float, output[11].split(";")))
        reference_two = list(map(float, output[12].split(";")))
        mean_source_zero = sum(source_zero) / 10.0
        mean_source_two = sum(source_two) / 10.0
        mean_reference_zero = sum(reference_zero) / 10.0
        mean_reference_two = sum(reference_two) / 10.0
        reconstructed = 0.9 * sum(
            (source_zero[index] - mean_source_zero) *
            (source_two[index] - mean_source_two) +
            (reference_zero[index] - mean_reference_zero) *
            (reference_two[index] - mean_reference_two)
            for index in range(10))
        self.assertAlmostEqual(vector_covariance, reconstructed, places=15)
        self.assertNotEqual(vector_covariance, 0.0)
        self.assertEqual(output[13], "0")
        retained_center, retained_value_status, retained_uncertainty_status = \
            output[14].split()
        self.assertAlmostEqual(float(retained_center), expected, places=15)
        self.assertEqual(retained_value_status, "UNSTABLE_DENOMINATOR")
        self.assertEqual(retained_uncertainty_status, "LEAVE_DENOMINATOR_ZERO")
