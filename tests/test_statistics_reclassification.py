"""Independent exact oracle for delete-one activity reclassification."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from helpers import ROOT


ORACLE = r'''
#include "statistics.hpp"
#include <array>
#include <cassert>
#include <cmath>
#include <vector>
int main() {
  namespace HR=Hadronization::Reduction;
  std::vector<std::vector<HR::ActivityAtom>> blocks;
  for (int k=1;k<=10;++k) {
    auto counts=k==1?std::array<int,3>{10,0,0}:
                k==10?std::array<int,3>{8,2,0}:
                      std::array<int,3>{4,1,5};
    std::vector<HR::ActivityAtom> atoms;
    for (int bin=0;bin<3;++bin)
      atoms.push_back({double(counts[bin]),
                       double((bin==1?5:bin==2?1:0)*counts[bin]),
                       double(bin>0?counts[bin]:0)});
    blocks.push_back(atoms);
  }
  auto result=HR::ReclassifiedActivityRatio(blocks,{false,0,50});
  assert(std::abs(result.center-9.0/5.0)<1e-15);
  assert(result.pooledBoundary.low==1 && result.pooledBoundary.high==2);
  assert(result.complements.size()==10);
  assert(result.deleteOneBoundaries[0].low==2 &&
         result.deleteOneBoundaries[9].low==2);
  assert(std::abs(result.complements[0]-1)<1e-15 &&
         std::abs(result.complements[9]-1)<1e-15);
  for(int k=1;k<9;++k)
    assert(std::abs(result.complements[k]-20.0/11.0)<1e-15);
  assert(std::abs(result.leaveMean-91.0/55.0)<1e-15);
  assert(std::abs(result.variance-2916.0/3025.0)<1e-14);
  assert(result.uncertaintyStatus=="WITHHELD_UNCERTAINTY");
  assert(result.reasons==std::vector<std::string>{"CLASS_BOUNDARY_UNSTABLE"});
  // A negative source weight is valid when every pooled and omitted
  // activity histogram remains nonnegative.
  blocks[0][0].measure=-1;
  auto signedWeights=HR::ReclassifiedActivityRatio(blocks,{false,0,50});
  assert(signedWeights.centerStatus=="AVAILABLE");
  std::vector<std::vector<HR::ActivityAtom>> empty(
      10,std::vector<HR::ActivityAtom>{{1,0,0},{0,0,0},{0,0,0}});
  auto emptyClass=HR::ReclassifiedActivityRatio(empty,{false,0,50});
  assert(emptyClass.pooledBoundary.empty);
  assert(emptyClass.centerStatus=="EMPTY_CLASS");
  // Equal block populations keep the integer boundary fixed, but a tie at
  // the target has zero through-margin and must withhold its statistical
  // resolution. A one-sided population resolves both margin sides.
  std::vector<std::vector<double>> tied(10,std::vector<double>{1,1});
  auto unresolved=HR::AuditActivityThreshold(tied,50);
  assert(unresolved.pooledThreshold==0);
  assert(!unresolved.statisticallyResolved);
  assert(unresolved.throughMargins.size()==10 &&
         unresolved.throughMargins[0]==0.0);
  std::vector<std::vector<double>> separated(10,std::vector<double>{10,0});
  auto resolved=HR::AuditActivityThreshold(separated,50);
  assert(resolved.pooledThreshold==0);
  assert(resolved.statisticallyResolved);
  assert(resolved.belowMargins[0]==-5.0 &&
         resolved.throughMargins[0]==5.0);
}
'''


class ActivityReclassificationOracle(unittest.TestCase):
    def test_boundary_and_membership_recomputed_per_omitted_block(self):
        compiler = shutil.which('c++')
        if compiler is None:
            self.skipTest('C++ compiler is unavailable')
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            source = path / 'oracle.cpp'
            binary = path / 'oracle'
            source.write_text(ORACLE)
            compile = subprocess.run(
                [compiler, '-std=c++17', '-O2', '-Wall', '-Wextra', '-Werror',
                 '-ffp-contract=off', '-I'+str(ROOT/'pipeline/reduce'),
                 str(source), '-o', str(binary)], capture_output=True, text=True)
            self.assertEqual((compile.returncode, compile.stderr), (0, ''))
            run = subprocess.run([str(binary)], capture_output=True, text=True)
            self.assertEqual((run.returncode, run.stderr), (0, ''))


if __name__ == '__main__':
    unittest.main()
