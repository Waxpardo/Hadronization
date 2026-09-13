"""Typed request to authenticated native diagnostic query mapping."""
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest

from pipeline.reduce import native_runner


class NativeRunnerMapping(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_projection_interface import ProjectionInterfaceContract
        cls.fixture=ProjectionInterfaceContract()
        cls.fixture.setUpClass()

    def setUp(self):
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.temporary=tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base=Path(self.temporary.name)

    def test_exact_natural_point_query_is_bound_to_A_science_and_axes(self):
        request=self.fixture.request()
        source=SimpleNamespace(expected_sha256='a'*64,index={
            'scientific_identity_sha256':request.to_dict()['bindings'][
                'expected_source_content_sha256'],
            'analysis_sha256':request.to_dict()['bindings']['analysis_config_sha256']})
        path=self.base/'points.tsv'
        receipt=native_runner.native_point_query(request,source,path)
        rows=path.read_text().splitlines()
        self.assertEqual(receipt['points'],len(request.expected_point_keys))
        self.assertEqual(len([row for row in rows if row.startswith('POINT\t')]),
                         len(request.expected_point_keys))
        self.assertEqual(rows[1].split('\t'),['BIND','a'*64,
            source.index['scientific_identity_sha256'],
            source.index['analysis_sha256']])
        self.assertTrue(any(row.split('\t')[2]=='spectra.signed_heavy'
                            for row in rows if row.startswith('POINT\t')))
        self.assertTrue(any(row.split('\t')[2]=='accounting.natural_final_heavy'
                            for row in rows if row.startswith('POINT\t')))
        with self.assertRaises(FileExistsError):
            native_runner.native_point_query(request,source,path)
        source.index['scientific_identity_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'scientific identity differs'):
            native_runner.native_point_query(request,source,self.base/'wrong.tsv')

    def test_diagnostic_reader_requires_request_family_and_every_middle_leaf(self):
        request,unused,unused_routes=self.fixture.result_fixture()
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
                lines.append('Q\tMONASH\t{}\t{}\t{}\tRESOLVED\t0\t0\t0\t0x1.0p+0'.format(
                    family,klass['id'],omit))
        lines.append('END')
        path=self.base/'diagnostic.tsv'
        path.write_text('\n'.join(lines)+'\n')
        rows,factors=native_runner.read_native_diagnostic(path,request)
        self.assertEqual((len(rows),len(factors)),(3,30))
        self.assertEqual(native_runner.verify_native_diagnostic_stream(path,request),
                         dict(points=3,factors=30,boundaries=11*len(value['classes']),available_errors=0,
                              withheld_errors=3))
        missing=self.base/'missing-middle.tsv'
        missing.write_text('\n'.join(line for line in lines
            if not line.startswith('F\t1\tMONASH\t'+family+'\t5\t'))+'\n')
        with self.assertRaisesRegex(ValueError,'incomplete'):
            native_runner.read_native_diagnostic(missing,request)
        with self.assertRaisesRegex(ValueError,'identity differs'):
            native_runner.verify_native_diagnostic_stream(missing,request)
        wrong=self.base/'wrong-family.tsv'
        wrong.write_text('\n'.join(line.replace('\t'+family+'\t5\t',
            '\t'+'0'*64+'\t5\t') if line.startswith('F\t1\t') else line
            for line in lines)+'\n')
        with self.assertRaisesRegex(ValueError,'source-family identity differs'):
            native_runner.read_native_diagnostic(wrong,request)
        with self.assertRaisesRegex(ValueError,'identity differs'):
            native_runner.verify_native_diagnostic_stream(wrong,request)

    def test_block_primitive_reader_requires_every_bound_additive_component(self):
        request,_,_=self.fixture.result_fixture()
        family=native_runner.p.digest(request.to_dict()['sources']['members'])
        moments={('MONASH',block):SimpleNamespace(events=20,sumw=20.)
                 for block in range(1,11)}
        lines=['hadronization_native_block_primitives_v1',
            'BIND\t{}\t{}'.format(request.request_sha256,
                                    request.scientific_request_sha256)]
        for point in range(len(request.expected_point_keys)):
            for block in range(1,11):
                lines.append('B\t{}\tMONASH\t{}\t{}\t20\tAVAILABLE\t'
                    'pair_os;pair_ss;trigger\t0x0p+0;0x0p+0;0x1p+0'.format(
                        point,family,block))
        lines.append('END')
        path=self.base/'blocks.tsv'
        path.write_text('\n'.join(lines)+'\n')
        self.assertEqual(native_runner.verify_native_block_primitives_stream(
            path,request,moments),dict(rows=30,unresolved=0))
        path.write_text('\n'.join(line for line in lines if not line.startswith(
            'B\t1\tMONASH\t'+family+'\t5\t'))+'\n')
        with self.assertRaisesRegex(ValueError,'identity differs'):
            native_runner.verify_native_block_primitives_stream(path,request,moments)
        path.write_text('\n'.join(line.replace('pair_os;pair_ss;trigger',
            'pair_os;trigger;pair_ss') if line.startswith('B\t1\t') else line
            for line in lines)+'\n')
        with self.assertRaisesRegex(ValueError,'semantic domain differs'):
            native_runner.verify_native_block_primitives_stream(path,request,moments)

    def test_denominator_reader_requires_ordered_K10_parent_values(self):
        request,_,_=self.fixture.result_fixture()
        lines=['hadronization_native_denominator_parents_v1',
            'BIND\t{}\t{}'.format(request.request_sha256,
                                    request.scientific_request_sha256)]
        for point in range(len(request.expected_point_keys)):
            lines.append('D\t{}\ttrigger\t1\tAVAILABLE\t0xap+0\t{}\t{}'.format(
                point,';'.join(['AVAILABLE']*10),';'.join(['0x9p+0']*10)))
        lines.append('END')
        path=self.base/'denominators.tsv'
        path.write_text('\n'.join(lines)+'\n')
        self.assertEqual(native_runner.verify_native_denominator_stream(
            path,request,{}),dict(rows=3,undefined=0,unstable=0))
        path.write_text('\n'.join(line for line in lines if not line.startswith(
            'D\t1\t'))+'\n')
        with self.assertRaisesRegex(ValueError,'semantic parent order differs'):
            native_runner.verify_native_denominator_stream(path,request,{})
        path.write_text('\n'.join(line.replace('AVAILABLE\t0xap+0',
            'UNDEFINED\t0xap+0') if line.startswith('D\t1\t') else line
            for line in lines)+'\n')
        with self.assertRaisesRegex(ValueError,'status/value mask differs'):
            native_runner.verify_native_denominator_stream(path,request,{})

    def test_denominator_parent_is_bound_to_observed_block_primitives(self):
        request,_,_=self.fixture.result_fixture()
        family=native_runner.p.digest(request.to_dict()['sources']['members'])
        blocks=self.base/'observed-blocks.tsv'
        block_lines=['hadronization_native_block_primitives_v1',
            'BIND\t{}\t{}'.format(request.request_sha256,
                                    request.scientific_request_sha256)]
        denominators=self.base/'observed-denominators.tsv'
        denominator_lines=['hadronization_native_denominator_parents_v1',
            'BIND\t{}\t{}'.format(request.request_sha256,
                                    request.scientific_request_sha256)]
        for point in range(len(request.expected_point_keys)):
            for block in range(1,11):
                block_lines.append('B\t{}\tMONASH\t{}\t{}\t20\tAVAILABLE\t'
                    'pair_os;pair_ss;trigger\t0x0p+0;0x0p+0;0x1p+0'.format(
                        point,family,block))
            denominator_lines.append('D\t{}\ttrigger\t1\tAVAILABLE\t'
                '0x1.4p+3\t{}\t{}'.format(point,';'.join(['AVAILABLE']*10),
                                            ';'.join(['0x1.2p+3']*10)))
        blocks.write_text('\n'.join(block_lines+['END'])+'\n')
        denominators.write_text('\n'.join(denominator_lines+['END'])+'\n')
        self.assertEqual(native_runner.verify_native_denominator_stream(
            denominators,request,{},blocks)['rows'],3)
        denominator_lines[3]=denominator_lines[3].replace('0x1.4p+3','0x1.6p+3')
        denominators.write_text('\n'.join(denominator_lines+['END'])+'\n')
        with self.assertRaisesRegex(ValueError,'pooled primitive algebra differs'):
            native_runner.verify_native_denominator_stream(
                denominators,request,{},blocks)


if __name__=='__main__':unittest.main()
