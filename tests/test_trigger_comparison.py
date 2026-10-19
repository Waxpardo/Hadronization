"""Joint-block trigger comparisons, invalid inputs and typed ROOT round trips."""
import copy
import json
import math
from pathlib import Path
import shutil
import tempfile
import unittest

from pipeline.reduce import trigger_comparison as tc

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which('root-config'), 'ROOT is required')
class TriggerComparison(unittest.TestCase):
    def test_paired_cancellation_and_scale(self):
        blocks = [[float(i), 100., float(i), 100.] for i in range(1, 11)]
        same = tc.estimate(blocks)
        self.assertEqual(float.fromhex(same['center']), 1.)
        self.assertEqual(float.fromhex(same['error']), 0.)
        self.assertEqual(same['uncertainty_status'], 'AVAILABLE_ZERO_DISPERSION')
        doubled = tc.estimate([[a,b,2*c,d] for a,b,c,d in blocks])
        self.assertEqual(float.fromhex(doubled['center']), 2.)
        wrong = tc.estimate([[blocks[i][0],100.,blocks[(i+1)%10][2],100.] for i in range(10)])
        self.assertGreater(float.fromhex(wrong['error']), 0.)

    def test_center_and_uncertainty_remain_distinct(self):
        zero = tc.estimate([[0.,100.,10.,100.]]*10)
        self.assertIsNone(zero['center'])
        negative = tc.estimate([[10.,100.,-5.,100.]]*10)
        self.assertEqual(float.fromhex(negative['center']), -.5)
        sparse = tc.estimate([[1.,100.,1.,100.]]+[[0.,100.,1.,100.]]*9)
        self.assertEqual(float.fromhex(sparse['center']), 10.)
        self.assertNotIn(sparse['uncertainty_status'], tc.AVAILABLE)
        self.assertIsNone(sparse['error'])

    def test_exact_primitives_and_recipe(self):
        for rows in ([[1.,10.,1.,10.]]*9, [[1.5,10.,1.,10.]]*10,
                     [[math.inf,10.,1.,10.]]*10):
            with self.assertRaises(ValueError): tc.estimate(rows)
        recipe = json.loads((ROOT/'config/trigger-comparison.json').read_text())
        tc.checked_recipe(recipe)
        recipe['sectors'][0]['associate_pairs'].append(recipe['sectors'][0]['associate_pairs'][0])
        with self.assertRaises(ValueError): tc.checked_recipe(recipe)

    def test_block_identity_and_event_weights(self):
        parent = {'block_values': [dict(block_id=i,tune_id='MONASH',events=10,
            sumw=(10.).hex(),sumw2=(10.).hex(),sumabsw=(10.).hex(),
            additive_components=[dict(id=k,value=v.hex()) for k,v in
                [('pair_os',3.),('pair_ss',1.),('trigger',5.)]]) for i in range(1,11)]}
        blocks,_ = tc._parent_blocks(parent,'MONASH')
        self.assertEqual(blocks,[[2.,5.]]*10)
        for field,value in [('block_id',1),('sumw2',(11.).hex()),('tune_id','JUNCTIONS')]:
            mutant=copy.deepcopy(parent); mutant['block_values'][1][field]=value
            with self.assertRaises(ValueError): tc._parent_blocks(mutant,'MONASH')

    def test_root_roundtrip_and_no_replace(self):
        recipe=json.loads((ROOT/'config/trigger-comparison.json').read_text())
        result=tc.estimate([[float(i),100.,float(i+1),100.] for i in range(1,11)])
        point=dict(index=0,semantic_id='point',sector='charm',tune='MONASH',slot=1,
            numerator_trigger=4122,denominator_trigger=421,numerator_associate=-421,
            denominator_associate=-421,numerator_id='n',denominator_id='d',
            source_family_sha256='0'*64,**result)
        value=dict(schema=tc.SCHEMA,recipe=recipe,points=[point],covariance=[[result['variance']]])
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'comparison.root'; digest=tc.write(value,path)
            self.assertEqual(tc.read(path,digest),value)
            with self.assertRaises(FileExistsError): tc.write(value,path)
            with self.assertRaises(ValueError): tc.read(path,'0'*64)
            import ROOT as rt
            f=rt.TFile.Open(str(path),'UPDATE')
            c=f.Get('covariance'); c.SetBinContent(1,1,999.)
            c.Write('',rt.TObject.kOverwrite); f.Close()
            with self.assertRaisesRegex(ValueError,'covariance content'):
                tc.read(path,tc.p.file_digest(path))

    def test_signed_parent_selection_and_population_mismatch(self):
        recipe=json.loads((ROOT/'config/trigger-comparison.json').read_text())
        recipe['sectors'][0]['associate_pairs']=[[-421,-421]]
        recipe['sectors'][1]['associate_pairs']=[[521,-521]]
        points=[]
        for sector in recipe['sectors']:
            for side in ('numerator','denominator'):
                associate=sector['associate_pairs'][0][0 if side=='numerator' else 1]
                curve=dict(role_id='balancing.integrated.'+sector['id'],
                    quantity='os_minus_ss_per_trigger',reference_tune_id=None,
                    class_id=0,profile_id='inclusive',tune_id='MONASH',
                    trigger_pdg=sector[side+'_trigger'],associate_pdg=associate)
                rows=[dict(block_id=i,tune_id='MONASH',events=10,sumw=(10.).hex(),
                    sumw2=(10.).hex(),sumabsw=(10.).hex(),event_moments_sha256=str(i),
                    additive_components=[dict(id=k,value=v.hex()) for k,v in
                        [('pair_os',3.),('pair_ss',1.),('trigger',5.)]]) for i in range(1,11)]
                points.append(dict(key=dict(curve=curve,bins=[]),
                    semantic_id=sector['id']+side,block_values=rows))
        parent=dict(schema='hadronization_projection_result_v4',request_sha256='r',
            campaign_state='COMPLETE',points=points,resolved=dict(category_order=[]),
            request_echo=dict(classes=[dict(id=0,kind='INTEGRATED')],
                sources=dict(members=[dict(tune_id='MONASH')]),
                scope=dict(ordered_tunes=['MONASH'])))
        result=tc.derive(parent,recipe,'a'*64,'b'*64)
        self.assertEqual(len(result['points']),2)
        self.assertEqual([float.fromhex(q['center']) for q in result['points']],[1.,1.])
        self.assertEqual(result['covariance'],[[0.0.hex()]*2]*2)
        tc.verify(result,parent,'a'*64,'b'*64)
        mutant=copy.deepcopy(parent); mutant['points'][2]['key']['curve']['associate_pdg']=-521
        with self.assertRaisesRegex(ValueError,'not materialized'):
            tc.derive(mutant,recipe,'a'*64,'b'*64)
        mutant=copy.deepcopy(parent); mutant['points'][0]['block_values'][0]['event_moments_sha256']='other'
        with self.assertRaisesRegex(ValueError,'populations differ'):
            tc.derive(mutant,recipe,'a'*64,'b'*64)

    def test_full_drawing_roundtrip_and_shared_title(self):
        from pipeline.plot import run as plot
        from types import SimpleNamespace
        import subprocess
        recipe=json.loads((ROOT/'config/trigger-comparison.json').read_text())
        tunes=['CLOSEPACKING','JUNCTIONS','MONASH']
        points=[]
        labels={str(x):'PDG '+str(x) for x in [421,4122,521,5122]}
        for sector in recipe['sectors']:
            for slot,(a,b) in enumerate(sector['associate_pairs'],1):
                labels.update({str(x):'PDG '+str(x) for x in (a,b)})
                for tune in tunes:
                    points.append(dict(semantic_id=sector['id']+str(slot)+tune,
                        sector=sector['id'],slot=slot,tune=tune,center=(1.1).hex(),
                        error=(.01).hex(),value_status='AVAILABLE',
                        uncertainty_status='AVAILABLE',reasons=[]))
        value=dict(recipe=recipe,tunes=tunes,points=points)
        context=SimpleNamespace(target_analysis_caption='TEST ONLY',
            sample_caption=['Hard test sample'],profile_definition={
                'trigger_eta':{'high':(4.).hex()},'trigger_pt':{'low':None}})
        config,_=plot.checked_plot_config(ROOT/'config/plot.json')
        page=plot.trigger_comparison_page(value,context,{'presentation':{'species_labels':labels}},config)
        self.assertEqual([s['tune'] for s in page['panels'][0]['series']],
                         ['MONASH','JUNCTIONS','CLOSEPACKING'])
        with tempfile.TemporaryDirectory() as td:
            work=Path(td);env,binary,_=plot.build_renderer(work)
            expected=plot.drawing_payload(dict(request_id='test-comparison',pages=[page]))
            plan=work/'plan.tsv';plan.write_bytes(expected)
            subprocess.run([str(binary),str(plan),str(work/'pages'),str(work/'record.tsv')],
                           check=True,capture_output=True,env=env)
            record=(work/'record.tsv').read_bytes()
            self.assertEqual(plot.normalized_drawing_record(record),expected)
            plot.verify_canvas_archive(binary,env,work/'pages',record,work)
            import ROOT as rt
            f=rt.TFile.Open(str(work/'pages/canvases.root'))
            labels=[]
            def visit(obj):
                if obj.InheritsFrom('TLatex'): labels.append(str(obj.GetTitle()))
                if obj.InheritsFrom('TPad'):
                    for child in obj.GetListOfPrimitives(): visit(child)
            for key in f.GetListOfKeys():
                obj=key.ReadObj()
                if obj.InheritsFrom('TCanvas'):visit(obj)
            f.Close()
            self.assertEqual(labels.count('Associate Species'),1)
