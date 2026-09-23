"""Native C++ diagnostic bridge: source scope and deletion-local class oracle."""
from pathlib import Path
from fractions import Fraction
import math
import shutil
import subprocess
import tempfile
import unittest

from helpers import ROOT


class NativeEngineContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler=shutil.which('c++')
        if compiler is None:
            raise unittest.SkipTest('C++ compiler is unavailable')
        cls.temporary=tempfile.TemporaryDirectory()
        cls.base=Path(cls.temporary.name)
        cls.binary=cls.base/'native-engine'
        completed=subprocess.run([compiler,'-std=c++17','-O2','-Wall','-Wextra',
            '-Wpedantic','-Werror','-ffp-contract=off',
            '-I'+str(ROOT/'pipeline/reduce'),
            str(ROOT/'pipeline/reduce/native_engine.cpp'),'-o',str(cls.binary)],
            capture_output=True,text=True)
        if (completed.returncode,completed.stderr)!=(0,''):
            raise AssertionError(completed.stderr)

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def inputs(self):
        sha='a'*64
        primitive=['hadronization_native_primitives_v1',
            'SOURCE\t'+'\t'.join([sha,'b'*64,'c'*64]),
            'ACTIVITY_FIELD\ta15_eta4','PROFILE\tinclusive',
            'TRIGGER_SCOPE\t411','PAIR_SCOPE\t411\t-411',
            'PAIR_SCOPE\t411\t411']
        for block in range(1,11):
            counts=[10,0,0] if block==1 else [8,2,0] if block==10 else [4,1,5]
            for bin_id,count in enumerate(counts):
                if count==0:continue
                primitive.append('ACTIVITY\tMONASH\t{}\t{}\t{}\t{}'.format(
                    block,bin_id,float(count).hex(),float(count).hex()))
                if bin_id:
                    primitive.append('TRIGGER\tinclusive\tMONASH\t{}\t{}\t411\t{}\t{}'.format(
                        block,bin_id,float(count).hex(),float(count).hex()))
                    os_count=(5 if bin_id==1 else 1)*count
                    primitive.append('PAIR\tinclusive\tMONASH\t{}\t{}\t411\t-411\t-1\t0\t{}\t{}'.format(
                        block,bin_id,float(os_count).hex(),float(os_count).hex()))
            primitive.append('EXPOSURE\tMONASH\t{}\t10'.format(block))
        primitive.append('END')
        points=['hadronization_native_points_v1',
            'BIND\t'+'\t'.join([sha,'b'*64,'c'*64]),
            'REQUEST\t'+'e'*64+'\t'+'f'*64,
            'AXES\t3\t1\t110','FAMILY\tMONASH\t'+'d'*64,'CLASS\t0\t1\t0\t100',
            'CLASS\t1\t0\t0\t50',
            'POINT\t0\tbalancing.activity.charm\tos_minus_ss_per_trigger\tMONASH\t-\tinclusive\t1\t411\t-411\t-411\tNONE\t-\t-1\tTEST_ONLY_DIAGNOSTIC',
            'END']
        source=self.base/'primitives.tsv';source.write_text('\n'.join(primitive)+'\n')
        query=self.base/'points.tsv';query.write_text('\n'.join(points)+'\n')
        return sha,source,query

    def test_extended_signed_species_use_pooled_counts_and_joint_deletions(self):
        # Explicit PDGs are an independent oracle for the new channel domain.
        charm=(-431,-4112,-4212,-4222,-4132,-4232)
        channels=[(t,a,'charm') for t in (421,4122) for a in charm]
        channels += [(521,a,'beauty') for a in (5112,5222,5132,5232)]
        channels += [(5122,a,'beauty') for a in (-5112,-5222,-5132,-5232)]
        sha='a'*64
        primitives=['hadronization_native_primitives_v1',
            'SOURCE\t'+'\t'.join([sha,'b'*64,'c'*64]),
            'ACTIVITY_FIELD\ta15_eta4','PROFILE\tinclusive']
        for trigger in (421,4122,521,5122):
            primitives.append(f'TRIGGER_SCOPE\t{trigger}')
        for trigger,associate,_ in channels:
            for signed in (associate,-associate):
                primitives.append(f'PAIR_SCOPE\t{trigger}\t{signed}')
        expected=[]
        for block in range(1,11):
            primitives += [f'ACTIVITY\tMONASH\t{block}\t1\t{float(200).hex()}\t{float(200).hex()}',
                           f'EXPOSURE\tMONASH\t{block}\t200']
            for trigger in (421,4122,521,5122):
                count=float(100+block).hex()
                primitives.append(f'TRIGGER\tinclusive\tMONASH\t{block}\t1\t{trigger}\t{count}\t{count}')
            for index,(trigger,associate,_) in enumerate(channels):
                for signed,sign,count in [(associate,-1,(index+2)*block+40),
                                          (-associate,1,block+index+3)]:
                    value=float(count).hex()
                    primitives.append(f'PAIR\tinclusive\tMONASH\t{block}\t1\t{trigger}\t{signed}\t{sign}\t0\t{value}\t{value}')
        query=['hadronization_native_points_v1',
            'BIND\t'+'\t'.join([sha,'b'*64,'c'*64]),
            'REQUEST\t'+'e'*64+'\t'+'f'*64,
            'AXES\t3\t1\t110','FAMILY\tMONASH\t'+'d'*64,
            'CLASS\t0\t1\t0\t100']
        for index,(trigger,associate,sector) in enumerate(channels):
            query.append(f'POINT\t{index}\tbalancing.integrated.{sector}\tos_minus_ss_per_trigger\tMONASH\t-\tinclusive\t0\t{trigger}\t{associate}\t0\tNONE\t-\t-1\tTEST_ONLY_DIAGNOSTIC')
            numerators=[(index+1)*block+37-index for block in range(1,11)]
            total=sum(numerators);denominator=sum(100+b for b in range(1,11))
            leaves=[Fraction(total-n,denominator-100-b)
                    for b,n in enumerate(numerators,1)]
            mean=sum(leaves)/10
            variance=Fraction(9,10)*sum((v-mean)**2 for v in leaves)
            expected.append((Fraction(total,denominator),variance,leaves))
        source=self.base/'extended-primitives.tsv'
        source.write_text('\n'.join(primitives+['END'])+'\n')
        points=self.base/'extended-points.tsv'
        points.write_text('\n'.join(query+['END'])+'\n')
        output=self.base/'extended-result.tsv'
        run=subprocess.run([str(self.binary),str(source),sha,str(points),str(output)],
                           capture_output=True,text=True)
        self.assertEqual((run.returncode,run.stderr),(0,''))
        rows=[line.split('\t') for line in output.read_text().splitlines()
              if line.startswith('R\t')]
        self.assertEqual(len(rows),len(channels))
        for row,(center,variance,leaves) in zip(rows,expected):
            self.assertEqual((row[2],row[4]),('AVAILABLE','AVAILABLE'))
            self.assertAlmostEqual(float.fromhex(row[3]),float(center),places=14)
            self.assertTrue(math.isclose(float.fromhex(row[10]),float(variance),rel_tol=1e-12))
            for actual,expected_leaf in zip(row[7].split(';'),leaves):
                self.assertAlmostEqual(float.fromhex(actual),float(expected_leaf),places=14)

    def test_cplusplus_reclassifies_numerator_and_denominator_per_omission(self):
        sha,source,query=self.inputs()
        output=self.base/'result.tsv'
        run=subprocess.run([str(self.binary),str(source),sha,str(query),str(output)],
                           capture_output=True,text=True)
        self.assertEqual((run.returncode,run.stderr),(0,''))
        row=output.read_text().splitlines()[2].split('\t')
        self.assertEqual((row[0],row[2],row[4],row[5],row[9]),
                         ('R','AVAILABLE','WITHHELD_UNCERTAINTY','-',
                          'CLASS_BOUNDARY_UNSTABLE'))
        self.assertAlmostEqual(float.fromhex(row[3]),9/5,places=15)
        leaves=[float.fromhex(x) for x in row[7].split(';')]
        self.assertEqual(len(leaves),10)
        self.assertAlmostEqual(leaves[0],1,places=15)
        self.assertAlmostEqual(leaves[-1],1,places=15)
        for leaf in leaves[1:-1]:
            self.assertAlmostEqual(leaf,20/11,places=15)
        self.assertAlmostEqual(sum(leaves)/10,91/55,places=15)
        self.assertTrue(math.isclose(float.fromhex(row[10]),2916/3025,
                                     rel_tol=1e-14))
        boundaries={int(fields[4]):fields for fields in
            (line.split('\t') for line in output.read_text().splitlines()
             if line.startswith('Q\t')) if fields[3]=='1'}
        self.assertEqual(set(boundaries),set(range(11)))
        self.assertEqual([boundaries[omit][5:9] for omit in (0,1,2,10)],
            [['RESOLVED','1','2','0'],['RESOLVED','2','2','0'],
             ['RESOLVED','1','2','0'],['RESOLVED','2','2','0']])
        self.assertEqual([float.fromhex(boundaries[omit][9])
            for omit in (0,1,2,10)],[50.,40.,44.,40.])

    def test_bound_K10_factors_reconstruct_valid_P1_variance(self):
        sha,source,query=self.inputs()
        lines=query.read_text().splitlines()
        lines=[line if not line.startswith('POINT\t') else
            'POINT\t0\tmultiplicity.composite\tnormalized_distribution\tMONASH\t-\t-\t0\t0\t0\t0\tNONE\tnch\t0\tTEST_ONLY_DIAGNOSTIC'
            for line in lines]
        query.write_text('\n'.join(lines)+'\n')
        output=self.base/'p1-factors.tsv'
        blocks=self.base/'p1-primitives.tsv'
        denominators=self.base/'p1-denominators.tsv'
        run=subprocess.run([str(self.binary),str(source),sha,str(query),
                            str(output),str(blocks),str(denominators)],
                           capture_output=True,text=True)
        self.assertEqual((run.returncode,run.stderr),(0,''))
        lines=output.read_text().splitlines()
        self.assertEqual(lines[0],'hadronization_native_engine_diagnostic_v2')
        row=lines[2].split('\t')
        factors=[line.split('\t') for line in lines if line.startswith('F\t')]
        self.assertEqual(len(factors),10)
        self.assertEqual([int(f[4]) for f in factors],list(range(1,11)))
        self.assertEqual({(f[2],f[3],f[5]) for f in factors},
                         {('MONASH','d'*64,'1')})
        leaves=[float.fromhex(f[6]) for f in factors]
        mean=float.fromhex(factors[0][7])
        reconstructed=sum(float.fromhex(f[8])**2 for f in factors)
        self.assertTrue(math.isclose(mean,sum(leaves)/10,rel_tol=1e-15))
        self.assertTrue(math.isclose(reconstructed,float.fromhex(row[10]),
                                      rel_tol=1e-14,abs_tol=1e-30))
        primitive_rows=[line.split('\t') for line in blocks.read_text().splitlines()
                        if line.startswith('B\t')]
        self.assertEqual(len(primitive_rows),10)
        self.assertEqual([int(item[4]) for item in primitive_rows],list(range(1,11)))
        self.assertEqual({(item[2],item[3],item[5],item[6],item[7])
            for item in primitive_rows},{('MONASH','d'*64,'10',
                                          'AVAILABLE','activity_bin;activity_total')})
        self.assertEqual([[float.fromhex(token) for token in item[8].split(';')]
            for item in (primitive_rows[0],primitive_rows[1],primitive_rows[-1])],
            [[10.,10.],[4.,10.],[8.,10.]])
        parent=[line.split('\t') for line in denominators.read_text().splitlines()
                if line.startswith('D\t')]
        self.assertEqual(len(parent),1)
        self.assertEqual(parent[0][:5],
            ['D','0','normalization_total','1','AVAILABLE'])
        self.assertEqual(float.fromhex(parent[0][5]),100.)
        self.assertEqual(parent[0][6].split(';'),['AVAILABLE']*10)
        self.assertEqual([float.fromhex(token) for token in
                          parent[0][7].split(';')],[90.]*10)

    def test_g9_shape_requires_positive_total_and_nonnegative_aggregate_bins(self):
        sha,source,query=self.inputs()
        lines=query.read_text().splitlines()
        lines=[line if not line.startswith('POINT\t') else
            'POINT\t0\tspectra.signed_heavy\tnormalized_spectrum\tMONASH\t-\t-\t0\t0\t421\t0\tNONE\tpt\t0\tTEST_ONLY_DIAGNOSTIC'
            for line in lines]
        query.write_text('\n'.join(lines)+'\n')
        original=source.read_text().splitlines()
        original.insert(4,'G9_SCOPE\t421')
        def evaluate(pt,eta,label):
            rows=original[:-1]
            for block in range(1,11):
                rows.append(f'G9\tMONASH\t{block}\t421\tpt\t1\t{pt.hex()}\t0x1p+0')
                rows.append(f'G9\tMONASH\t{block}\t421\teta\t1\t{(eta if block==1 else pt).hex()}\t0x1p+0')
                rows.append(f'G9\tMONASH\t{block}\t421\tphi\t1\t{pt.hex()}\t0x1p+0')
            source.write_text('\n'.join(rows+['END'])+'\n')
            output=self.base/f'g9-{label}.tsv'
            run=subprocess.run([str(self.binary),str(source),sha,str(query),str(output)],
                               capture_output=True,text=True)
            self.assertEqual((run.returncode,run.stderr),(0,''))
            return output.read_text().splitlines()[2].split('\t')
        positive=evaluate(1.,1.,'positive')
        self.assertEqual((positive[2],float.fromhex(positive[3])),('AVAILABLE',1.))
        zero=evaluate(0.,0.,'zero')
        self.assertEqual((zero[2],zero[9]),('UNDEFINED','G9_NONPOSITIVE_TOTAL'))
        negative=evaluate(1.,-20.,'negative')
        self.assertEqual((negative[2],negative[9]),('UNDEFINED','G9_NEGATIVE_AGGREGATE_BIN'))

    def test_positive_beauty_baryon_P8_sign_and_meson_parent(self):
        sha='a'*64
        primitive=['hadronization_native_primitives_v1',
            'SOURCE\t'+'\t'.join([sha,'b'*64,'c'*64]),
            'ACTIVITY_FIELD\ta15_eta4','PROFILE\tinclusive',
            'TRIGGER_SCOPE\t5122']
        for associate in (-531,531,-521,521):
            primitive.append('PAIR_SCOPE\t5122\t{}'.format(associate))
        for block in range(1,11):
            primitive.extend((
                'ACTIVITY\tMONASH\t{}\t1\t0x1p+0\t0x1p+0'.format(block),
                'TRIGGER\tinclusive\tMONASH\t{}\t1\t5122\t0x1p+0\t0x1p+0'.format(block),
                'PAIR\tinclusive\tMONASH\t{}\t1\t5122\t-531\t-1\t0\t0x1p+0\t0x1p+0'.format(block),
                'PAIR\tinclusive\tMONASH\t{}\t1\t5122\t531\t1\t0\t0x1.8p+1\t0x1.2p+3'.format(block),
                'PAIR\tinclusive\tMONASH\t{}\t1\t5122\t-521\t-1\t0\t0x1p+2\t0x1p+4'.format(block),
                'EXPOSURE\tMONASH\t{}\t1'.format(block)))
        source=self.base/'p8-sign-primitives.tsv'
        source.write_text('\n'.join(primitive+['END'])+'\n')
        query=self.base/'p8-sign-points.tsv'
        query.write_text('\n'.join([
            'hadronization_native_points_v1',
            'BIND\t'+'\t'.join([sha,'b'*64,'c'*64]),
            'REQUEST\t'+'e'*64+'\t'+'f'*64,
            'AXES\t2\t1\t110','FAMILY\tMONASH\t'+'d'*64,
            'CLASS\t0\t1\t0\t100',
            'POINT\t0\tbalancing.baryon_meson.activity\tbaryon_meson_reference_ratio\tMONASH\t-\tinclusive\t0\t5122\t-531\t-521\tNONE\t-\t-1\tTEST_ONLY_DIAGNOSTIC',
            'END'])+'\n')
        output=self.base/'p8-sign-result.tsv'
        blocks=self.base/'p8-sign-blocks.tsv'
        denominators=self.base/'p8-sign-denominators.tsv'
        run=subprocess.run([str(self.binary),str(source),sha,str(query),
                            str(output),str(blocks),str(denominators)],
                           capture_output=True,text=True)
        self.assertEqual((run.returncode,run.stderr),(0,''))
        row=output.read_text().splitlines()[2].split('\t')
        self.assertEqual(row[2],'AVAILABLE')
        self.assertEqual(float.fromhex(row[3]),-.5)
        first_block=next(line.split('\t') for line in blocks.read_text().splitlines()
                         if line.startswith('B\t'))
        self.assertEqual(first_block[7],
            'pair_os;pair_ss;trigger;reference_pair_os;reference_pair_ss')
        self.assertEqual([float.fromhex(token) for token in first_block[8].split(';')],
                         [1.,3.,1.,4.,0.])
        parents=[line.split('\t') for line in denominators.read_text().splitlines()
                 if line.startswith('D\t')]
        self.assertEqual([(row[2],float.fromhex(row[5])) for row in parents],
                         [('shared_trigger',10.),('reference_os_minus_ss',40.)])
        source.write_text(source.read_text().replace(
            'EXPOSURE\tMONASH\t1\t1',
            'PAIR\tinclusive\tMONASH\t1\t1\t5122\t521\t1\t0\t0x1p+2\t0x1p+4\nEXPOSURE\tMONASH\t1\t1'))
        # A single SS fill changes the parent but does not erase the valid numerator.
        second=self.base/'p8-sign-changed.tsv'
        rerun=subprocess.run([str(self.binary),str(source),sha,str(query),str(second)],
                             capture_output=True,text=True)
        self.assertEqual((rerun.returncode,rerun.stderr),(0,''))
        self.assertEqual(float.fromhex(second.read_text().splitlines()[2].split('\t')[3]),
                         -20/36)

    def test_dzero_p8_uses_signed_valence_os_ss_and_antidzero_parent(self):
        sha='a'*64
        primitive=['hadronization_native_primitives_v1',
            'SOURCE\t'+'\t'.join([sha,'b'*64,'c'*64]),
            'ACTIVITY_FIELD\ta15_eta4','PROFILE\tinclusive',
            'TRIGGER_SCOPE\t421']
        for associate in (-4122,4122,-421,421):
            primitive.append(f'PAIR_SCOPE\t421\t{associate}')
        for block in range(1,11):
            primitive.extend((
                f'ACTIVITY\tMONASH\t{block}\t1\t0x1p+0\t0x1p+0',
                f'TRIGGER\tinclusive\tMONASH\t{block}\t1\t421\t0x1p+0\t0x1p+0',
                f'PAIR\tinclusive\tMONASH\t{block}\t1\t421\t-4122\t-1\t0\t0x1p+0\t0x1p+0',
                f'PAIR\tinclusive\tMONASH\t{block}\t1\t421\t4122\t1\t0\t0x1.8p+1\t0x1.2p+3',
                f'PAIR\tinclusive\tMONASH\t{block}\t1\t421\t-421\t-1\t0\t0x1p+2\t0x1p+4',
                f'EXPOSURE\tMONASH\t{block}\t1'))
        source=self.base/'d0-p8-primitives.tsv'
        source.write_text('\n'.join(primitive+['END'])+'\n')
        query=self.base/'d0-p8-points.tsv'
        query.write_text('\n'.join([
            'hadronization_native_points_v1',
            'BIND\t'+'\t'.join([sha,'b'*64,'c'*64]),
            'REQUEST\t'+'e'*64+'\t'+'f'*64,
            'AXES\t2\t1\t110','FAMILY\tMONASH\t'+'d'*64,
            'CLASS\t0\t1\t0\t100',
            'POINT\t0\tbalancing.baryon_meson.activity\tbaryon_meson_reference_ratio\tMONASH\t-\tinclusive\t0\t421\t-4122\t-421\tNONE\t-\t-1\tTEST_ONLY_DIAGNOSTIC',
            'END'])+'\n')
        output=self.base/'d0-p8-result.tsv'
        blocks=self.base/'d0-p8-blocks.tsv'
        parents=self.base/'d0-p8-parents.tsv'
        run=subprocess.run([str(self.binary),str(source),sha,str(query),
                            str(output),str(blocks),str(parents)],
                           capture_output=True,text=True)
        self.assertEqual((run.returncode,run.stderr),(0,''))
        row=output.read_text().splitlines()[2].split('\t')
        self.assertEqual((row[2],float.fromhex(row[3])),('AVAILABLE',-.5))
        first=next(line.split('\t') for line in blocks.read_text().splitlines()
                   if line.startswith('B\t'))
        self.assertEqual(first[7],
            'pair_os;pair_ss;trigger;reference_pair_os;reference_pair_ss')
        self.assertEqual([float.fromhex(x) for x in first[8].split(';')],
                         [1.,3.,1.,4.,0.])
        denominator=[line.split('\t') for line in parents.read_text().splitlines()
                     if line.startswith('D\t')]
        self.assertEqual([(x[2],x[4],float.fromhex(x[5]))
                          for x in denominator],
                         [('shared_trigger','AVAILABLE',10.),
                          ('reference_os_minus_ss','AVAILABLE',40.)])
        # A valid same-sign D0 pair subtracts from the reference parent.
        changed=source.read_text().replace('EXPOSURE\tMONASH\t1\t1',
            'PAIR\tinclusive\tMONASH\t1\t1\t421\t421\t1\t0\t0x1p+2\t0x1p+4\nEXPOSURE\tMONASH\t1\t1')
        source.write_text(changed)
        second=self.base/'d0-p8-changed.tsv'
        rerun=subprocess.run([str(self.binary),str(source),sha,str(query),
                              str(second)],capture_output=True,text=True)
        self.assertEqual((rerun.returncode,rerun.stderr),(0,''))
        self.assertEqual(float.fromhex(second.read_text().splitlines()[2].split('\t')[3]),
                         -20/36)

    def test_dzero_multitune_p2_p8_nonzero_shared_reference_factors(self):
        sha='a'*64
        primitive=['hadronization_native_primitives_v1',
            'SOURCE\t'+'\t'.join([sha,'b'*64,'c'*64]),
            'ACTIVITY_FIELD\ta15_eta4','PROFILE\tinclusive',
            'TRIGGER_SCOPE\t421']
        primitive += [f'PAIR_SCOPE\t421\t{associate}'
                      for associate in (-4122,4122,-421,421)]
        for tune in ('MONASH','JUNCTIONS'):
            for block in range(1,11):
                trigger=10.+block if tune=='MONASH' else 12.+2*block
                meson=4.+block if tune=='MONASH' else 5.+block/2
                baryon_os=1. if tune=='MONASH' else 3.+block/2
                baryon_ss=3.+block if tune=='MONASH' else 1.
                rows=[('ACTIVITY',tune,block,0,2.),
                      ('ACTIVITY',tune,block,1,trigger)]
                for _,t,b,activity,value in rows:
                    primitive.append(f'ACTIVITY\t{t}\t{b}\t{activity}\t{value.hex()}\t{value.hex()}')
                primitive.append(f'TRIGGER\tinclusive\t{tune}\t{block}\t1\t421\t{trigger.hex()}\t{trigger.hex()}')
                for associate,sign,value in ((-421,-1,meson),(421,1,1.),
                                              (-4122,-1,baryon_os),(4122,1,baryon_ss)):
                    primitive.append(f'PAIR\tinclusive\t{tune}\t{block}\t1\t421\t{associate}\t{sign}\t0\t{value.hex()}\t{value.hex()}')
                primitive.append(f'EXPOSURE\t{tune}\t{block}\t10')
        source=self.base/'d0-multitune-primitives.tsv'
        source.write_text('\n'.join(primitive+['END'])+'\n')
        query=['hadronization_native_points_v1',
            'BIND\t'+'\t'.join([sha,'b'*64,'c'*64]),
            'REQUEST\t'+'e'*64+'\t'+'f'*64,
            'AXES\t2\t1\t110','FAMILY\tMONASH\t'+'d'*64,
            'FAMILY\tJUNCTIONS\t'+'c'*64,'CLASS\t0\t1\t0\t100']
        for point_id,(role,quantity,tune,reference,associate,parent,component,axis,bin_id) in enumerate((
                ('correlations.charm','dphi_per_trigger','MONASH','-',-421,-421,'NET','dphi',0),
                ('correlations.charm','dphi_per_trigger','JUNCTIONS','-',-421,-421,'NET','dphi',0),
                ('correlations.charm','ratio_to_reference_tune','JUNCTIONS','MONASH',-421,-421,'NET','dphi',0),
                ('balancing.baryon_meson.activity','baryon_meson_reference_ratio','MONASH','-',-4122,-421,'NONE','-',-1),
                ('balancing.baryon_meson.activity','baryon_meson_reference_ratio','JUNCTIONS','-',-4122,-421,'NONE','-',-1),
                ('balancing.baryon_meson.activity','baryon_meson_ratio_to_reference_tune','JUNCTIONS','MONASH',-4122,-421,'NONE','-',-1))):
            query.append(f'POINT\t{point_id}\t{role}\t{quantity}\t{tune}\t{reference}\tinclusive\t0\t421\t{associate}\t{parent}\t{component}\t{axis}\t{bin_id}\tTEST_ONLY_DIAGNOSTIC')
        point_path=self.base/'d0-multitune-points.tsv'
        point_path.write_text('\n'.join(query+['END'])+'\n')
        output=self.base/'d0-multitune-result.tsv'
        run=subprocess.run([str(self.binary),str(source),sha,str(point_path),
                            str(output)],capture_output=True,text=True)
        self.assertEqual((run.returncode,run.stderr),(0,''))
        rows={int(fields[1]):fields for fields in (line.split('\t') for line in
            output.read_text().splitlines() if line.startswith('R\t'))}
        self.assertEqual(set(rows),set(range(6)))
        self.assertTrue(all(row[2]=='AVAILABLE' and row[4]=='AVAILABLE'
                            for row in rows.values()))
        self.assertLess(float.fromhex(rows[3][3]),0.)
        self.assertGreater(float.fromhex(rows[4][3]),0.)
        self.assertNotEqual(float.fromhex(rows[5][3]),0.)
        factors={(int(f[1]),f[2],int(f[4])):float.fromhex(f[8]) for f in
            (line.split('\t') for line in output.read_text().splitlines()
             if line.startswith('F\t'))}
        self.assertEqual(len(factors),80)
        shared=sum(factors[3,'MONASH',block]*factors[5,'MONASH',block]
                   for block in range(1,11))
        self.assertNotEqual(shared,0.)

    def test_dzero_p2_analyzed_row_oracle_counts_zero_associate_triggers(self):
        # Each tuple is one independently classified analyzed trigger, followed
        # by its signed, dphi-bin-zero associates. The second D0 in every block
        # has no associate but must remain in the per-trigger denominator.
        analyzed_blocks = [((421, (-421,)), (421, ())) for _ in range(10)]
        trigger_count = sum(len(block) for block in analyzed_blocks)
        os_count = sum(associate == -421 for block in analyzed_blocks
                       for _, associates in block for associate in associates)
        ss_count = sum(associate == 421 for block in analyzed_blocks
                       for _, associates in block for associate in associates)
        self.assertEqual((trigger_count, os_count, ss_count), (20, 10, 0))
        sha = 'a' * 64
        primitive = ['hadronization_native_primitives_v1',
            'SOURCE\t' + '\t'.join([sha, 'b'*64, 'c'*64]),
            'ACTIVITY_FIELD\ta15_eta4', 'PROFILE\tinclusive',
            'TRIGGER_SCOPE\t421', 'PAIR_SCOPE\t421\t-421',
            'PAIR_SCOPE\t421\t421']
        for block_id, rows in enumerate(analyzed_blocks, 1):
            block_os = sum(a == -421 for _, associates in rows for a in associates)
            block_ss = sum(a == 421 for _, associates in rows for a in associates)
            primitive.extend((
                f'ACTIVITY\tMONASH\t{block_id}\t1\t0x1p+1\t0x1p+2',
                f'TRIGGER\tinclusive\tMONASH\t{block_id}\t1\t421\t{float(len(rows)).hex()}\t{float(len(rows)).hex()}',
                f'PAIR\tinclusive\tMONASH\t{block_id}\t1\t421\t-421\t-1\t0\t{float(block_os).hex()}\t{float(block_os).hex()}',
                f'PAIR\tinclusive\tMONASH\t{block_id}\t1\t421\t421\t1\t0\t{float(block_ss).hex()}\t{float(block_ss).hex()}',
                f'EXPOSURE\tMONASH\t{block_id}\t2'))
        source = self.base / 'd0-p2-zero-associate-primitives.tsv'
        source.write_text('\n'.join(primitive + ['END']) + '\n')
        query = self.base / 'd0-p2-zero-associate-points.tsv'
        point = ('POINT\t{}\tcorrelations.charm\tdphi_per_trigger\tMONASH'
                 '\t-\tinclusive\t0\t421\t-421\t0\t{}\tdphi\t0'
                 '\tTEST_ONLY_DIAGNOSTIC')
        query.write_text('\n'.join([
            'hadronization_native_points_v1',
            'BIND\t' + '\t'.join([sha, 'b'*64, 'c'*64]),
            'REQUEST\t' + 'e'*64 + '\t' + 'f'*64,
            'AXES\t2\t1\t110', 'FAMILY\tMONASH\t' + 'd'*64,
            'CLASS\t0\t1\t0\t100',
            'SIGN_ASSOCIATE\t421\tCHARM\tOS\t-421',
            'SIGN_ASSOCIATE\t421\tCHARM\tSS\t421',
            point.format(0, 'OS'), point.format(1, 'SS'),
            point.format(2, 'NET'),
            ('POINT\t3\tcorrelations.charm\tdphi_per_trigger\tMONASH'
             '\t-\tinclusive\t0\t421\t0\t0\tNET\tdphi\t0'
             '\tTEST_ONLY_DIAGNOSTIC'), 'END']) + '\n')
        output = self.base / 'd0-p2-zero-associate-results.tsv'
        blocks = self.base / 'd0-p2-zero-associate-blocks.tsv'
        parents = self.base / 'd0-p2-zero-associate-parents.tsv'
        run = subprocess.run([str(self.binary), str(source), sha, str(query),
                              str(output), str(blocks), str(parents)],
                             capture_output=True, text=True)
        self.assertEqual((run.returncode, run.stderr), (0, ''))
        points = [line.split('\t') for line in output.read_text().splitlines()
                  if line.startswith('R\t')]
        self.assertEqual([row[2] for row in points], ['AVAILABLE']*4)
        self.assertEqual([float.fromhex(row[3]) for row in points],
                         [os_count/trigger_count, ss_count/trigger_count,
                          (os_count-ss_count)/trigger_count,
                          (os_count-ss_count)/trigger_count])
        block_rows = [line.split('\t') for line in blocks.read_text().splitlines()
                      if line.startswith('B\t')]
        self.assertEqual([float.fromhex(x) for x in block_rows[0][8].split(';')],
                         [1., 0., 2.])
        parent_rows = [line.split('\t') for line in parents.read_text().splitlines()
                       if line.startswith('D\t')]
        self.assertEqual({(row[2], float.fromhex(row[5])) for row in parent_rows},
                         {('trigger', 20.)})

    def test_p8_cancelled_reference_parent_and_surviving_source_parent(self):
        sha='a'*64
        for trigger in (411,421):
            with self.subTest(trigger=trigger):
                reference=-trigger
                primitive=['hadronization_native_primitives_v1',
                    'SOURCE\t'+'\t'.join([sha,'b'*64,'c'*64]),
                    'ACTIVITY_FIELD\ta15_eta4',
                    'SUPPORT_UPPER\tactivity\t2000',
                    'SUPPORT_UPPER\tkinematics\t0',
                    'SUPPORT_UPPER\tpairs\t2000',
                    'SUPPORT_UPPER\ttriggers\t2000',
                    'PROFILE\tinclusive',f'TRIGGER_SCOPE\t{trigger}']
                for associate in (-4122,4122,reference,trigger):
                    primitive.append(f'PAIR_SCOPE\t{trigger}\t{associate}')
                for tune in ('MONASH','JUNCTIONS'):
                    for block in range(1,11):
                        baryon=10 if tune=='MONASH' else 20
                        meson=(-17 if block==1 else 2) if tune=='MONASH' else 10
                        primitive.extend((
                            f'ACTIVITY\t{tune}\t{block}\t0\t0x1.9p+6\t0x1.9p+6',
                            f'EXPOSURE\t{tune}\t{block}\t100',
                            f'TRIGGER\tinclusive\t{tune}\t{block}\t0\t{trigger}\t0x1.9p+6\t0x1.9p+6',
                            f'PAIR\tinclusive\t{tune}\t{block}\t0\t{trigger}\t-4122\t-1\t0\t{float(baryon).hex()}\t{float(baryon).hex()}',
                            f'PAIR\tinclusive\t{tune}\t{block}\t0\t{trigger}\t{reference if meson>=0 else trigger}\t{-1 if meson>=0 else 1}\t0\t{float(abs(meson)).hex()}\t{float(abs(meson)).hex()}'))
                source=self.base/f'p8-cancelled-{trigger}-primitives.tsv'
                source.write_text('\n'.join(primitive+['END'])+'\n')
                query=self.base/f'p8-cancelled-{trigger}-points.tsv'
                query.write_text('\n'.join([
                    'hadronization_native_points_v1',
                    'BIND\t'+'\t'.join([sha,'b'*64,'c'*64]),
                    'REQUEST\t'+'e'*64+'\t'+'f'*64,
                    'AXES\t1\t1\t110',
                    'FAMILY\tJUNCTIONS\t'+'c'*64,
                    'FAMILY\tMONASH\t'+'d'*64,
                    'CLASS\t0\t1\t0\t100',
                    f'POINT\t0\tbalancing.baryon_meson.activity\tbaryon_meson_ratio_to_reference_tune\tJUNCTIONS\tMONASH\tinclusive\t0\t{trigger}\t-4122\t{reference}\tNONE\t-\t-1\tTEST_ONLY_DIAGNOSTIC',
                    'END'])+'\n')
                output=self.base/f'p8-cancelled-{trigger}-result.tsv'
                denominators=self.base/f'p8-cancelled-{trigger}-parents.tsv'
                run=subprocess.run([str(self.binary),str(source),sha,str(query),
                                    str(output),self.base/f'p8-cancelled-{trigger}-blocks.tsv',
                                    str(denominators)],capture_output=True,text=True)
                self.assertEqual((run.returncode,run.stderr),(0,''))
                row=next(line.split('\t') for line in output.read_text().splitlines()
                         if line.startswith('R\t'))
                self.assertEqual(row[2:3]+row[4:5],['AVAILABLE','AVAILABLE'])
                self.assertAlmostEqual(float.fromhex(row[3]),.02,places=15)
                self.assertEqual(row[9],'-')
                parents=[line.split('\t') for line in
                         denominators.read_text().splitlines()
                         if line.startswith('D\t')]
                reference_parent=next(item for item in parents if item[2]==
                                      'reference_meson_os_minus_ss')
                self.assertEqual(reference_parent[3:5],['0','AVAILABLE'])
                self.assertEqual(float.fromhex(reference_parent[5]),1.)
                changed=source.read_text().replace(
                    f'PAIR\tinclusive\tJUNCTIONS\t1\t0\t{trigger}\t{reference}\t-1\t0\t{float(10).hex()}\t{float(10).hex()}',
                    f'PAIR\tinclusive\tJUNCTIONS\t1\t0\t{trigger}\t{trigger}\t1\t0\t{float(17).hex()}\t{float(17).hex()}')
                for block in range(2,11):
                    changed=changed.replace(
                        f'PAIR\tinclusive\tJUNCTIONS\t{block}\t0\t{trigger}\t{reference}\t-1\t0\t{float(10).hex()}\t{float(10).hex()}',
                        f'PAIR\tinclusive\tJUNCTIONS\t{block}\t0\t{trigger}\t{reference}\t-1\t0\t{float(2).hex()}\t{float(2).hex()}')
                self.assertNotEqual(changed,source.read_text())
                source.write_text(changed)
                failed=self.base/f'p8-surviving-{trigger}-result.tsv'
                rerun=subprocess.run([str(self.binary),str(source),sha,str(query),
                                      str(failed)],capture_output=True,text=True)
                self.assertEqual((rerun.returncode,rerun.stderr),(0,''))
                denied=next(line.split('\t') for line in failed.read_text().splitlines()
                            if line.startswith('R\t'))
                self.assertEqual(denied[4],'WITHHELD_UNCERTAINTY')
                self.assertIn('SOURCE_JUNCTIONS_INTERNAL',denied[9])

    def test_independent_tune_families_and_shared_reference_covariance(self):
        sha,source,query=self.inputs()
        content=source.read_text().splitlines()
        second=[line.replace('\tMONASH\t','\tJUNCTIONS\t') for line in content
                if line.startswith(('ACTIVITY\t','EXPOSURE\t'))]
        source.write_text('\n'.join(content[:-1]+second+['END'])+'\n')
        query.write_text('\n'.join([
            'hadronization_native_points_v1',
            'BIND\t'+'\t'.join([sha,'b'*64,'c'*64]),
            'REQUEST\t'+'e'*64+'\t'+'f'*64,
            'AXES\t3\t1\t110',
            'FAMILY\tJUNCTIONS\t'+'c'*64,
            'FAMILY\tMONASH\t'+'d'*64,
            'CLASS\t0\t1\t0\t100',
            'POINT\t0\tmultiplicity.composite\tnormalized_distribution\tMONASH\t-\t-\t0\t0\t0\t0\tNONE\tnch\t0\tTEST_ONLY_DIAGNOSTIC',
            'POINT\t1\tmultiplicity.composite\tnormalized_distribution\tJUNCTIONS\t-\t-\t0\t0\t0\t0\tNONE\tnch\t0\tTEST_ONLY_DIAGNOSTIC',
            'POINT\t2\tmultiplicity.composite\tratio_to_reference_tune\tJUNCTIONS\tMONASH\t-\t0\t0\t0\t0\tNONE\tnch\t0\tTEST_ONLY_DIAGNOSTIC',
            'END'])+'\n')
        output=self.base/'two-independent-families.tsv'
        run=subprocess.run([str(self.binary),str(source),sha,str(query),str(output)],
                           capture_output=True,text=True)
        self.assertEqual((run.returncode,run.stderr),(0,''))
        rows=[line.split('\t') for line in output.read_text().splitlines()
              if line.startswith('R\t')]
        self.assertEqual(len(rows),3)
        self.assertEqual([row[4] for row in rows],['AVAILABLE']*3)
        factors={(int(f[1]),f[2],int(f[4])):float.fromhex(f[8]) for f in
            (line.split('\t') for line in output.read_text().splitlines()
             if line.startswith('F\t'))}
        self.assertEqual(len(factors),40)
        self.assertEqual({t for i,t,b in factors if i==0},{'MONASH'})
        self.assertEqual({t for i,t,b in factors if i==1},{'JUNCTIONS'})
        self.assertEqual({t for i,t,b in factors if i==2},
                         {'MONASH','JUNCTIONS'})
        def covariance(i,j):
            return sum(factors[i,t,b]*factors[j,t,b] for t in
                ('MONASH','JUNCTIONS') for b in range(1,11)
                if (i,t,b) in factors and (j,t,b) in factors)
        self.assertEqual(covariance(0,1),0.0)
        self.assertNotEqual(covariance(0,2),0.0)
        self.assertNotEqual(covariance(1,2),0.0)
        for index,row in enumerate(rows):
            self.assertTrue(math.isclose(covariance(index,index),
                float.fromhex(row[5]),rel_tol=1e-13,abs_tol=1e-30))

    def test_statistically_unresolved_surviving_denominator_keeps_center(self):
        sha='a'*64
        primitive=['hadronization_native_primitives_v1',
            'SOURCE\t'+'\t'.join([sha,'b'*64,'c'*64]),
            'ACTIVITY_FIELD\ta15_eta4',
            'SUPPORT_UPPER\tactivity\t100',
            'SUPPORT_UPPER\tkinematics\t0',
            'SUPPORT_UPPER\tpairs\t0',
            'SUPPORT_UPPER\ttriggers\t0',
            'PROFILE\tinclusive','TRIGGER_SCOPE\t411',
            'PAIR_SCOPE\t411\t-411','PAIR_SCOPE\t411\t411']
        for block in range(1,11):
            weight=-7.5 if block==1 else 1.
            primitive.append('ACTIVITY\tMONASH\t{}\t0\t{}\t{}'.format(
                block,weight.hex(),(weight*weight).hex()))
            primitive.append('EXPOSURE\tMONASH\t{}\t10'.format(block))
        source=self.base/'unresolved-denominator-primitives.tsv'
        source.write_text('\n'.join(primitive+['END'])+'\n')
        query=self.base/'unresolved-denominator-points.tsv'
        query.write_text('\n'.join([
            'hadronization_native_points_v1',
            'BIND\t'+'\t'.join([sha,'b'*64,'c'*64]),
            'REQUEST\t'+'e'*64+'\t'+'f'*64,
            'AXES\t1\t1\t110','FAMILY\tMONASH\t'+'d'*64,
            'CLASS\t0\t1\t0\t100',
            'POINT\t0\tmultiplicity.composite\tnormalized_distribution\tMONASH\t-\t-\t0\t0\t0\t0\tNONE\tnch\t0\tTEST_ONLY_DIAGNOSTIC',
            'END'])+'\n')
        output=self.base/'unresolved-denominator-result.tsv'
        run=subprocess.run([str(self.binary),str(source),sha,str(query),str(output)],
                           capture_output=True,text=True)
        self.assertEqual((run.returncode,run.stderr),(0,''))
        row=output.read_text().splitlines()[2].split('\t')
        self.assertEqual((row[2],row[4]),
                         ('UNSTABLE_DENOMINATOR','WITHHELD_UNCERTAINTY'))
        self.assertEqual(float.fromhex(row[3]),1.)
        self.assertIn('DENOMINATOR_STATISTICALLY_UNRESOLVED:',row[9])

    def test_missing_ss_scope_cannot_masquerade_as_zero(self):
        sha,source,query=self.inputs()
        content=source.read_text().replace('PAIR_SCOPE\t411\t411\n','')
        source.write_text(content)
        output=self.base/'rejected.tsv'
        run=subprocess.run([str(self.binary),str(source),sha,str(query),str(output)],
                           capture_output=True,text=True)
        self.assertNotEqual(run.returncode,0)
        self.assertIn('outside scanned scope',run.stderr)

    def test_missing_original_block_exposure_cannot_masquerade_as_zero(self):
        sha,source,query=self.inputs()
        source.write_text(source.read_text().replace('EXPOSURE\tMONASH\t10\t10\n',''))
        output=self.base/'missing-block.tsv'
        run=subprocess.run([str(self.binary),str(source),sha,str(query),str(output)],
                           capture_output=True,text=True)
        self.assertNotEqual(run.returncode,0)
        self.assertIn('ten-block event exposure is incomplete',run.stderr)

    def test_out_of_design_source_block_is_rejected(self):
        sha,source,query=self.inputs()
        source.write_text(source.read_text().replace('EXPOSURE\tMONASH\t10\t10',
                                                     'EXPOSURE\tMONASH\t11\t10'))
        output=self.base/'block-eleven.tsv'
        run=subprocess.run([str(self.binary),str(source),sha,str(query),str(output)],
                           capture_output=True,text=True)
        self.assertNotEqual(run.returncode,0)
        self.assertIn('outside the ten-block design',run.stderr)

    def test_unsupported_point_role_does_not_fall_through_to_balance_formula(self):
        sha,source,query=self.inputs()
        query.write_text(query.read_text().replace('balancing.activity.charm',
                                                   'balancing.unknown'))
        output=self.base/'unsupported-role.tsv'
        run=subprocess.run([str(self.binary),str(source),sha,str(query),str(output)],
                           capture_output=True,text=True)
        self.assertNotEqual(run.returncode,0)
        self.assertIn('point role is unsupported',run.stderr)

    def test_out_of_domain_binned_point_is_rejected(self):
        sha,source,query=self.inputs()
        content=query.read_text().replace('balancing.activity.charm',
            'multiplicity.composite').replace('os_minus_ss_per_trigger',
            'normalized_distribution').replace('\t-\tinclusive\t1\t411\t-411\t-411\tNONE\t-\t-1\t',
            '\t-\t-\t0\t0\t0\t0\tNONE\tnch\t3\t')
        query.write_text(content)
        output=self.base/'out-of-domain-point.tsv'
        run=subprocess.run([str(self.binary),str(source),sha,str(query),str(output)],
                           capture_output=True,text=True)
        self.assertNotEqual(run.returncode,0)
        self.assertIn('P1 point shape differs',run.stderr)

    def test_exposed_tune_with_no_occupied_activity_is_a_missing_point(self):
        sha,source,query=self.inputs()
        lines=source.read_text().splitlines()
        lines=[line for line in lines if not line.startswith(('ACTIVITY\t','TRIGGER\t','PAIR\t'))]
        source.write_text('\n'.join(lines)+'\n')
        query.write_text('\n'.join([
            'hadronization_native_points_v1',
            'BIND\t'+'\t'.join([sha,'b'*64,'c'*64]),
            'REQUEST\t'+'e'*64+'\t'+'f'*64,
            'AXES\t3\t1\t110','FAMILY\tMONASH\t'+'d'*64,'CLASS\t0\t1\t0\t100',
            'POINT\t0\tmultiplicity.composite\tnormalized_distribution\tMONASH\t-\t-\t0\t0\t0\t0\tNONE\tnch\t0\tTEST_ONLY_DIAGNOSTIC',
            'END'])+'\n')
        output=self.base/'empty-activity.tsv'
        run=subprocess.run([str(self.binary),str(source),sha,str(query),str(output)],
                           capture_output=True,text=True)
        self.assertEqual((run.returncode,run.stderr),(0,''))
        row=output.read_text().splitlines()[2].split('\t')
        self.assertEqual((row[2],row[4],row[9]),
                         ('UNDEFINED','WITHHELD_UNCERTAINTY','UNDEFINED_CENTER'))

    def test_stable_integer_boundary_with_unresolved_margin_withholds_error(self):
        sha,source,query=self.inputs()
        lines=source.read_text().splitlines()
        lines=[line for line in lines if not line.startswith(
            ('ACTIVITY\t','TRIGGER\t','PAIR\t'))]
        self.assertEqual(lines.pop(),'END')
        for block in range(1,11):
            for bin_id in (0,1):
                lines.append(f'ACTIVITY\tMONASH\t{block}\t{bin_id}\t'+
                             '0x1.0000000000000p+0\t0x1.0000000000000p+0')
            lines.append(f'TRIGGER\tinclusive\tMONASH\t{block}\t1\t411\t'+
                         '0x1.0000000000000p+0\t0x1.0000000000000p+0')
            lines.append(f'PAIR\tinclusive\tMONASH\t{block}\t1\t411\t-411\t-1\t0\t'+
                         '0x1.0000000000000p+0\t0x1.0000000000000p+0')
        source.write_text('\n'.join(lines+['END'])+'\n')
        output=self.base/'unresolved-margin.tsv'
        run=subprocess.run([str(self.binary),str(source),sha,str(query),str(output)],
                           capture_output=True,text=True)
        self.assertEqual((run.returncode,run.stderr),(0,''))
        row=output.read_text().splitlines()[2].split('\t')
        self.assertEqual((row[2],row[4],row[9]),
                         ('AVAILABLE','WITHHELD_UNCERTAINTY',
                          'CLASS_BOUNDARY_UNRESOLVED'))
        self.assertEqual(float.fromhex(row[3]),1.0)

    def test_stable_t9_margin_inside_numeric_bound_withholds_class_error(self):
        sha,source,query=self.inputs()
        query.write_text(query.read_text().replace('CLASS\t1\t0\t0\t50',
                                                   'CLASS\t1\t0\t50\t100'))
        lines=[line for line in source.read_text().splitlines()
               if not line.startswith(('ACTIVITY\t','TRIGGER\t','PAIR\t'))]
        self.assertEqual(lines.pop(),'END')
        tiny=1.+2.**-51
        for block in range(1,11):
            for bin_id,weight in ((0,1.),(1,tiny)):
                lines.append('ACTIVITY\tMONASH\t{}\t{}\t{}\t{}'.format(
                    block,bin_id,weight.hex(),(weight*weight).hex()))
            lines.append('TRIGGER\tinclusive\tMONASH\t{}\t1\t411\t{}\t{}'.format(
                block,float(1.).hex(),float(1.).hex()))
            lines.append('PAIR\tinclusive\tMONASH\t{}\t1\t411\t-411\t-1\t0\t{}\t{}'.format(
                block,float(1.).hex(),float(1.).hex()))
        source.write_text('\n'.join(lines+['END'])+'\n')
        def evaluate(name):
            output=self.base/name
            run=subprocess.run([str(self.binary),str(source),sha,str(query),str(output)],
                               capture_output=True,text=True)
            self.assertEqual((run.returncode,run.stderr),(0,''))
            return output.read_text().splitlines()[2].split('\t')
        unbounded=evaluate('small-margin-unbounded.tsv')
        self.assertEqual(unbounded[4],'AVAILABLE_ZERO_DISPERSION',unbounded)
        lines[3:3]=['SUPPORT_UPPER\tactivity\t100',
                    'SUPPORT_UPPER\tkinematics\t0',
                    'SUPPORT_UPPER\tpairs\t10',
                    'SUPPORT_UPPER\ttriggers\t10']
        source.write_text('\n'.join(lines+['END'])+'\n')
        bounded=evaluate('small-margin-bounded.tsv')
        self.assertEqual((bounded[2],bounded[4],bounded[9]),
                         ('AVAILABLE','WITHHELD_UNCERTAINTY',
                          'CLASS_BOUNDARY_UNRESOLVED'))


if __name__=='__main__':
    unittest.main()
