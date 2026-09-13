"""Cold direct ROOT diagnostic receipt without source collection or TSV."""
import csv
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from pipeline.reduce import native_archive, native_runner


class NativeArchiveContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:import ROOT  # noqa: F401
        except ImportError:raise unittest.SkipTest('ROOT unavailable')
        from test_projection_interface import ProjectionInterfaceContract
        cls.fixture=ProjectionInterfaceContract()
        cls.fixture.setUpClass()

    def setUp(self):
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.temporary=tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base=Path(self.temporary.name).resolve()

    def test_typed_points_factors_and_boundaries_survive_cold_reopen(self):
        request,_,_=self.fixture.result_fixture()
        value=request.to_dict()
        family=native_runner.p.digest(value['sources']['members'])
        lines=['hadronization_native_engine_diagnostic_v2',
            'BIND\t{}\t{}'.format(request.request_sha256,
                                    request.scientific_request_sha256)]
        for point_id in range(len(request.expected_point_keys)):
            lines.append('R\t{}\tUNDEFINED\t-\tWITHHELD_UNCERTAINTY\t-\t-\t{}\t-\tUNDEFINED_CENTER\t-'.format(
                point_id,';'.join(['-']*10)))
            for block in range(1,11):
                lines.append('F\t{}\tMONASH\t{}\t{}\t0\t-\t-\t-'.format(
                    point_id,family,block))
        for klass in sorted(value['classes'],key=lambda item:item['id']):
            for omit in range(11):
                lines.append('Q\tMONASH\t{}\t{}\t{}\tRESOLVED\t0\t0\t0\t0x1p+0'.format(
                    family,klass['id'],omit))
        lines.append('END')
        diagnostic=self.base/'diagnostic.tsv'
        diagnostic.write_text('\n'.join(lines)+'\n')
        root=self.base/'diagnostic.root'
        receipt=native_archive.write(diagnostic,request,'a'*64,root)
        self.assertEqual((receipt['points'],receipt['factors'],receipt['boundaries']),
                         (3,30,11*len(value['classes'])))
        import ROOT
        opened=ROOT.TFile.Open(str(root),'READ')
        try:
            group=opened.Get('covariance_points')
            self.assertEqual(group.GetEntries(),3)
            self.assertEqual({str(branch.GetName()) for branch in
                              group.GetListOfBranches()},set(native_archive.GROUP_FIELDS))
            group.GetEntry(1)
            self.assertEqual((int(group.slot),int(group.point),bool(group.valid)),
                             (1,1,False))
        finally:opened.Close()
        diagnostic.rename(self.base/'hidden-diagnostic.tsv')
        command=[sys.executable,'-c',
            'import json,sys;from pipeline.reduce import native_archive;'
            'print(json.dumps(native_archive.read(sys.argv[1],sys.argv[2]),sort_keys=True))',
            str(root),receipt['root_sha256']]
        cold=subprocess.run(command,capture_output=True,text=True)
        self.assertEqual(cold.returncode,0,cold.stderr)
        self.assertEqual(json.loads(cold.stdout)['points'],3)
        export=native_archive.export_tables(root,receipt['root_sha256'],
            self.base/'points.csv',self.base/'summary.tex',self.base/'missing.csv')
        self.assertEqual(export['points'],3)
        with (self.base/'points.csv').open(newline='') as stream:
            point_rows=list(csv.DictReader(stream))
        self.assertEqual(len(point_rows),3)
        self.assertTrue(all(row['center_hex64']=='UNAVAILABLE' and
                            row['standard_error_hex64']=='UNAVAILABLE'
                            for row in point_rows))
        with (self.base/'missing.csv').open(newline='') as stream:
            self.assertEqual(len(list(csv.DictReader(stream))),3)
        self.assertIn('TEST_ONLY',(self.base/'summary.tex').read_text())
        with self.assertRaisesRegex(ValueError,'trusted physical hash'):
            native_archive.read(root,'0'*64)


if __name__=='__main__':unittest.main()
