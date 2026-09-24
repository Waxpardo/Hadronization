"""Independent kill tests for the scientific request domain and C++ covariance."""
import copy
from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from helpers import ROOT


def load_interface():
    spec = importlib.util.spec_from_file_location('projection_v2_contract', ROOT / 'pipeline/reduce/projection.py')
    value = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = value
    spec.loader.exec_module(value)
    return value


class ProjectionInterfaceContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = load_interface()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.analysis = json.loads((ROOT / 'config/analysis.json').read_text())
        self.analysis['axes']['dphi'].update(bins=2, low=-1., high=1.)
        self.analysis['axes']['activity']['bins'] = 3
        self.analysis['percentile_intervals'] = [[0, 50], [50, 100]]
        self.config = json.loads((ROOT / 'config/plot.json').read_text())
        self.roles = [{'id': x} for x in ['multiplicity.composite', 'correlations.charm', 'correlations.beauty',
            'balancing.integrated.charm', 'balancing.integrated.beauty', 'balancing.activity.charm',
            'balancing.activity.beauty', 'balancing.baryon_meson.activity',
            'spectra.signed_heavy', 'accounting.natural_final_heavy']]
        self.selection = dict(profile_id='inclusive',
            activity_id=self.analysis['activities'][0]['id'], reference_tune='MONASH',
            trigger_pdgs=[411,4122,521,5122],
            baryon_meson_trigger_pdgs=[411,521],
            signed_pdgs=[p for values in self.analysis['pair_query_registry']['associate_pdgs'].values() for p in values])
        unused, pairs = self.p._query_model().state_registry(self.analysis)
        h = 'a' * 64
        lineage = dict(lossless_contract={'registries_sha256': self.p._reducer().analyzer_module().REGISTRIES_DIGEST},
            block_assignment={'count': 10}, campaign={'id': 'TEST', 'descriptor_sha256': h},
            accepted_manifest={'sha256': h}, analysis_plan={'sha256': h}, shard_map={'sha256': h},
            shards=[{'receipt_scientific_identity_sha256': h}], sources=[])
        for i in range(10):
            lineage['sources'].append(dict(source_id=i, manifest_row=dict(tune='MONASH', logical_id=i, accepted_attempt=0,
                block=i+1, successful_events=20, raw_sha256=h, validation_receipt_sha256=h)))
        domains = dict(block_ids=list(range(1,11)), tune_dictionary=['MONASH'], profiles=self.analysis['profiles'],
            activities=self.analysis['activities'], axes=self.analysis['axes'], pair_query_dictionary=pairs,
            dynamic_species=dict(closure_species_pdgs=[411,421,521],
                                 t1_all_final_pdgs=[-521,-411,411,421,521,4122,5122]),
            class_dictionary=[dict(id=i, integrated=i==0, percentile_interval=v) for i,v in
                enumerate([[0,100]] + self.analysis['percentile_intervals'])],
            correlation_dictionary=[dict(trigger_pdg=p['trigger_pdg'], associate_pdg=p['associate_pdg']) for p in pairs
                if p['sign']==-1 and abs(p['associate_pdg'])==abs(p['reference_meson_pdg'])])
        self.receipt = dict(state='NONPUBLICATION_PARTIAL', scientific_identity=dict(analysis_request_sha256=h,
            input_lineage=lineage, compact_domains=domains))
        self.presentation = dict(selection_definitions=copy.deepcopy(self.analysis))

    def request(self, tunes=('MONASH',), analysis=None, receipt=None):
        analysis = analysis or self.analysis; receipt = receipt or self.receipt
        path = self.base / 'requested-analysis.json'
        path.write_text(json.dumps(analysis))
        return self.p.make_request(receipt, self.presentation, self.config, self.p.digest(self.config),
            self.roles, self.selection, self.p.digest(receipt['scientific_identity']), list(tunes), analysis,
            path, self.p.file_digest(path))

    def test_density_identity_and_eligible_central_pair_domain(self):
        value=self.request().to_dict()
        self.assertEqual(value['science_contract']['formula_contract_version'],'projection_formulas_v3')
        pairs=value['scope']['ordered_associate_pairs']
        self.assertTrue(pairs)
        self.assertFalse(any(abs(p['associate_pdg']) in (5212,5312,5322) for p in pairs))
        # Broad diagnostic storage is preserved by the query registry.
        self.assertTrue(any(abs(p['associate_pdg'])==5212 for p in self.p._query_model().state_registry(self.analysis)[1]))
        density=[o for o in value['observables'] if o['quantity']=='dphi_density_per_trigger']
        self.assertTrue(density)
        self.assertTrue(all(o['output_units']=='per_trigger_per_radian' for o in density))
        for field,wrong in (('output_units','per_trigger_per_bin'),('formula_version','projection_formulas_v2')):
            forged=copy.deepcopy(value)
            next(o for o in forged['observables'] if o['quantity']=='dphi_density_per_trigger')[field]=wrong
            with self.assertRaisesRegex(ValueError,'formula/quantity/units'):
                self.p.ProjectionRequest.from_dict(forged,cold=True)
        forged=copy.deepcopy(value);forged['science_contract']['formula_contract_version']='projection_formulas_v2'
        with self.assertRaisesRegex(ValueError,'correlation formula'):
            self.p.ProjectionRequest.from_dict(forged,cold=True)

    def test_g9_metadata_binds_selected_final_predicate_normalization_and_flow(self):
        request = self.request().to_dict()
        metadata = self.p.g9_science(request)
        self.p.validate(metadata, 'G9ScienceNoFloor')
        self.p.validate_g9_science(request, metadata)
        self.assertIsNone(metadata['pt']['low_operator'])
        self.assertIsNone(metadata['pt']['low'])
        self.assertEqual(metadata['origin_scope'], 'ALL_ORIGINS')
        self.assertEqual((metadata['status_low'],metadata['status_high']), (81,89))
        self.assertEqual(metadata['normalization'],
                         'per_bin_probability_no_bin_width_division')
        for field, substitute in (('status_low',80),('pt_flow','drop_overflow'),
                                  ('denominator','event_count'),('origin_scope','PRIMARY_ONLY')):
            changed = copy.deepcopy(metadata)
            changed[field] = substitute
            with self.subTest(field=field), self.assertRaisesRegex(ValueError,
                    'resolved G9 selection/normalization'):
                self.p.validate_g9_science(request,changed)




    def test_activity_pt_metadata_is_derived_and_mutation_changes_identity(self):
        before = self.request()
        analysis = copy.deepcopy(self.analysis)
        analysis['activities'][0]['predicate'] = analysis['activities'][0]['predicate'].replace('pt>0.15','pt>=0.25')
        after = self.request(analysis=analysis)
        self.assertEqual(after.to_dict()['activity']['pt']['low'], float(.25).hex())
        self.assertEqual(after.to_dict()['activity']['pt']['low_operator'], 'GE')
        self.assertNotEqual(before.scientific_request_sha256, after.scientific_request_sha256)
        self.assertNotEqual(after.to_dict()['activity'], self.p.normalized_activity(self.presentation['selection_definitions']['activities'][0]))


    def test_nominal_p8_exact_signed_channel_scope_excludes_neutral_mesons(self):
        request=self.request(('MONASH','JUNCTIONS'))
        keys=[k for k in request.expected_point_keys if k['curve']['role_id']=='balancing.baryon_meson.activity']
        self.assertEqual({(k['curve']['trigger_pdg'],k['curve']['associate_pdg'],k['curve']['reference_pdg']) for k in keys},
                         {(411,-4122,-411),(521,5122,-521)})
        self.assertEqual(len(keys),2*2*3) # Two channels, two classes, M absolute plus J absolute/ratio.

    def test_dzero_default_and_dplus_alternate_have_distinct_signed_science_keys(self):
        from pipeline.query import model
        analysis=model.select_charm_meson_recipe(self.analysis,421)
        self.presentation['selection_definitions']=copy.deepcopy(analysis)
        self.selection['trigger_pdgs']=[421,4122,521,5122]
        self.selection['baryon_meson_trigger_pdgs']=[421,521]
        default=self.request(analysis=analysis)
        default_keys=default.expected_point_keys
        def curves(keys,role):
            return {self.p.canonical(key['curve']):key['curve'] for key in keys
                    if key['curve']['role_id']==role}.values()
        correlation=list(curves(default_keys,'correlations.charm'))
        self.assertEqual({item['trigger_pdg'] for item in correlation},
                         {421,4122})
        self.assertEqual({item['associate_pdg'] for item in correlation},
                         {-421})
        for role in ('balancing.integrated.charm',
                     'balancing.activity.charm'):
            channels={(item['trigger_pdg'],item['associate_pdg'])
                      for item in curves(default_keys,role)}
            self.assertEqual(channels,{(trigger,associate)
                for trigger in (421,4122)
                for associate in (-411,-421,-431,-4122,-4112,-4212,
                                  -4222,-4132,-4232)})
        p8={(item['trigger_pdg'],item['associate_pdg'],
             item['reference_pdg']) for item in curves(
                 default_keys,'balancing.baryon_meson.activity')}
        self.assertEqual(p8,{(421,-4122,-421),(521,5122,-521)})
        pairs={(item['trigger_pdg'],item['associate_pdg']):item['sign']
               for item in default.to_dict()['scope'][
                   'ordered_associate_pairs']}
        self.assertEqual({pair:pairs[pair] for pair in
            ((421,-4122),(421,4122),(421,-421),(421,421),
             (4122,-421),(4122,421))},
            {(421,-4122):'OS',(421,4122):'SS',
             (421,-421):'OS',(421,421):'SS',
             (4122,-421):'OS',(4122,421):'SS'})
        self.selection['trigger_pdgs']=[411,4122,521,5122]
        self.selection['baryon_meson_trigger_pdgs']=[411,521]
        alternate_analysis=model.select_charm_meson_recipe(analysis,411)
        self.presentation['selection_definitions']=copy.deepcopy(
            alternate_analysis)
        alternate=self.request(analysis=alternate_analysis)
        self.assertNotEqual(default.scientific_request_sha256,
                            alternate.scientific_request_sha256)
        self.assertEqual({item['trigger_pdg'] for item in curves(
            alternate.expected_point_keys,'correlations.charm')},{411,4122})
        self.assertEqual({item['associate_pdg'] for item in curves(
            alternate.expected_point_keys,'correlations.charm')},{-411})
        self.assertEqual({(item['trigger_pdg'],item['associate_pdg'],
                           item['reference_pdg']) for item in curves(
            alternate.expected_point_keys,'balancing.baryon_meson.activity')},
            {(411,-4122,-411),(521,5122,-521)})

    def test_extended_baryon_domain_preserves_existing_points_and_exact_signs(self):
        self.selection['trigger_pdgs'] = [421, 4122, 521, 5122]
        self.selection['baryon_meson_trigger_pdgs'] = [421, 521]
        old = {self.p.canonical(key) for key in self.request().expected_point_keys}
        self.selection['baryon_meson_trigger_pdgs'] = [421, 4122, 521, 5122]
        channels = self.p.paper_baryon_meson_channels(self.analysis, 421)
        self.selection['baryon_meson_channels'] = channels
        expected = {(trigger, -baryon, -421)
                    for trigger in (421, 4122)
                    for baryon in (4122, 4112, 4212, 4222, 4132, 4232)}
        expected |= {(521, baryon, -521)
                     for baryon in (5122, 5112, 5222, 5132, 5232)}
        expected |= {(5122, -baryon, 521)
                     for baryon in (5122, 5112, 5222, 5132, 5232)}
        self.assertEqual({tuple(row) for row in channels}, expected)
        request = self.request()
        new = {self.p.canonical(key) for key in request.expected_point_keys}
        self.assertTrue(old < new)
        added = [json.loads(key)['curve'] for key in new-old]
        self.assertTrue(all(curve['role_id'] == 'balancing.baryon_meson.activity'
                            for curve in added))
        self.assertEqual(len(new-old), 20*2)
        keys = [key['curve'] for key in request.expected_point_keys
                if key['curve']['role_id'] == 'balancing.baryon_meson.activity']
        self.assertEqual({(key['trigger_pdg'],key['associate_pdg'],key['reference_pdg'])
                          for key in keys}, expected)

    def test_extended_baryon_domain_rejects_sign_reference_and_state_mutants(self):
        self.selection['trigger_pdgs'] = [421, 4122, 521, 5122]
        self.selection['baryon_meson_trigger_pdgs'] = [421, 4122, 521, 5122]
        for channel in ([421,4122,-421], [521,5132,521],
                        [521,5212,-521], [421,-421,-421],
                        [5122,-5132,-521], [421,-4132,-431]):
            with self.subTest(channel=channel):
                self.selection['baryon_meson_channels'] = [channel]
                with self.assertRaisesRegex(ValueError, 'signed registry'):
                    self.request()
        self.selection['baryon_meson_channels'] = [[421,-4132,-421]]*2
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            self.request()

    def test_g9_dzero_default_and_dplus_extra_are_registry_derived(self):
        analysis=copy.deepcopy(self.analysis)
        analysis['g9_species_pdgs']=[-5212,-5122,-4122,-521,-421,
                                     421,521,4122,5122,5212]
        default=self.request(analysis=analysis)
        default_species=self.p.g9_science(default.to_dict())['signed_species_pdgs']
        self.assertEqual(default_species,analysis['g9_species_pdgs'])
        self.assertEqual(len(default_species),10)
        self.assertEqual({-421,421} & set(default_species),{-421,421})
        self.assertFalse({-411,411} & set(default_species))
        extra=copy.deepcopy(analysis)
        extra['g9_species_pdgs']=sorted(default_species+[-411,411])
        enlarged=self.request(analysis=extra)
        self.assertEqual(self.p.g9_science(enlarged.to_dict())[
            'signed_species_pdgs'],extra['g9_species_pdgs'])
        self.assertNotEqual(default.scientific_request_sha256,
                            enlarged.scientific_request_sha256)
        for request,count in ((default,10),(enlarged,12)):
            curves={self.p.canonical(key['curve']):key['curve']
                    for key in request.expected_point_keys
                    if key['curve']['role_id']=='spectra.signed_heavy'}
            self.assertEqual({curve['associate_pdg'] for curve in curves.values()},
                             set(self.p.g9_science(request.to_dict())[
                                 'signed_species_pdgs']))
            self.assertEqual(len(curves),count*3) # Three shape axes per signed species.
        invalid=copy.deepcopy(extra)
        invalid['g9_species_pdgs'].append(999999)
        with self.assertRaisesRegex(ValueError,'G9 signed species request differs'):
            self.request(analysis=invalid)

    def test_extended_balancing_domain_has_exact_species_signs_and_classes(self):
        request = self.request(('MONASH', 'JUNCTIONS', 'CLOSEPACKING'))
        charm = (-411, -421, -431, -4122, -4112, -4212, -4222, -4132, -4232)
        beauty = {521: (-521, -511, -531, -541, 5122, 5112, 5222, 5132, 5232),
                  5122: (521, 511, 531, 541, -5122, -5112, -5222, -5132, -5232)}
        states = {s['pdg']:s for s in json.loads(
            (ROOT/'config/study.json').read_text())['selected_states']}
        scope = request.to_dict()['scope']['ordered_associate_pairs']
        signs = {(p['trigger_pdg'],p['associate_pdg']):p['sign'] for p in scope}
        expected = {'charm':{411:charm,4122:charm}, 'beauty':beauty}
        labels = {pdg:state['name'] for pdg,state in states.items()}
        order = self.p.category_order(request.to_dict(),labels)
        for sector, channels in expected.items():
            for kind, classes in [('integrated',{0}),('activity',{1,2})]:
                role = 'balancing.'+kind+'.'+sector
                curves = [k['curve'] for k in request.expected_point_keys
                          if k['curve']['role_id']==role]
                self.assertEqual({(c['trigger_pdg'],c['associate_pdg']) for c in curves},
                    {(t,a) for t,associates in channels.items() for a in associates})
                for trigger,associates in channels.items():
                    self.assertEqual(next(r['associate_pdgs'] for r in order
                        if r['role_id']==role and r['trigger_pdg']==trigger),list(associates))
                    for associate in associates:
                        self.assertTrue(states[associate]['pair_analysis_eligible'])
                        self.assertEqual(signs[trigger,associate],'OS')
                        self.assertEqual(signs[trigger,-associate],'SS')
                        selected = [c for c in curves if c['trigger_pdg']==trigger
                                    and c['associate_pdg']==associate]
                        self.assertEqual({c['class_id'] for c in selected},classes)
                        for klass in classes:
                            rows=[c for c in selected if c['class_id']==klass]
                            self.assertEqual({(c['tune_id'],c['reference_tune_id']) for c in rows},
                                {('MONASH',None),('JUNCTIONS',None),('CLOSEPACKING',None),
                                 ('JUNCTIONS','MONASH'),('CLOSEPACKING','MONASH')})
                self.assertEqual(len(curves),90*len(classes))

    def test_cold_category_order_preserves_previous_identified_subset(self):
        request = self.request().to_dict()
        request['scope']['ordered_associate_pairs'].sort(key=self.p.canonical)
        for role in request['scope']['roles']:
            if role['role_id'].startswith('balancing.'):
                role['required_curve_keys']=[c for c in role['required_curve_keys']
                    if c['associate_pdg'] in (-411,-421,-4122,-521,-511,-531,-541,
                                              5122,521,511,531,541,-5122)]
        labels={p['associate_pdg']:str(p['associate_pdg']) for p in
                request['scope']['ordered_associate_pairs']}
        order=self.p.category_order(request,labels)
        self.assertEqual(next(r['associate_pdgs'] for r in order if
            r['role_id']=='balancing.integrated.beauty' and r['trigger_pdg']==521),
            [-521,-511,-531,-541,5122])
        legacy_charm=list(dict.fromkeys(p['associate_pdg'] for p in
            request['scope']['ordered_associate_pairs'] if p['trigger_pdg']==411
            and p['associate_pdg'] in (-411,-421,-4122)))
        self.assertEqual(next(r['associate_pdgs'] for r in order if
            r['role_id']=='balancing.integrated.charm' and r['trigger_pdg']==411),legacy_charm)


    def test_phase_a_release_rejects_relative_and_strict_profiles(self):
        for profile in (dict(id='relative_pt',trigger_pt=None,associate_pt=None,relative_pt='trigger_pt>associate_pt'),
                        dict(id='historical_strict_1p0_0p15',trigger_pt=dict(operator='>',value=1.),associate_pt=dict(operator='>',value=.15),relative_pt=None)):
            analysis=copy.deepcopy(self.analysis);analysis['profiles']=[profile]
            self.selection['profile_id']=profile['id']
            with self.assertRaisesRegex(ValueError,'Phase-A profile|relative/diagonal pT selection|released pT thresholds|eventwise relative pT selection'):
                self.request(analysis=analysis)

    def test_missing_emitter_role_cannot_shrink_request(self):
        self.roles.pop()
        with self.assertRaisesRegex(ValueError,'paper role registry'):
            self.request()

    def test_registry_binding_mutation_is_rejected(self):
        analysis = copy.deepcopy(self.analysis); analysis['base_study']['sha256']='0'*64
        with self.assertRaisesRegex(ValueError, 'particle registry'):
            self.request(analysis=analysis)

    def test_explicit_backend_preference_is_not_scientific_identity(self):
        before = self.request(); payload=before.to_dict(); payload['execution']['backend_policy']='EXACT_ROWS'
        after = self.p.ProjectionRequest.from_dict(payload)
        self.assertNotEqual(before.request_sha256, after.request_sha256)
        self.assertEqual(before.scientific_request_sha256, after.scientific_request_sha256)

    def test_plot_preset_cannot_change_scientific_domain(self):
        before = self.request()
        self.config['presets']['paper_default']['families'] = ['Omega']
        after = self.request()
        self.assertEqual(before.expected_point_keys, after.expected_point_keys)
        self.assertEqual(before.scientific_request_sha256,
                         after.scientific_request_sha256)
        self.assertNotEqual(before.request_sha256, after.request_sha256)
        self.selection['trigger_pdgs'] = [411, 4122]
        self.selection['baryon_meson_trigger_pdgs'] = [411]
        narrowed = self.request()
        self.assertNotEqual(before.scientific_request_sha256,
                            narrowed.scientific_request_sha256)

    def test_non_monash_reference_changes_ratio_identity_and_family(self):
        baseline = self.request(('MONASH','JUNCTIONS','CLOSEPACKING'))
        self.selection['reference_tune'] = 'JUNCTIONS'
        changed = self.request(('MONASH','JUNCTIONS','CLOSEPACKING'))
        ratios = [key for key in changed.expected_point_keys
                  if key['curve']['role_id'] == 'balancing.integrated.beauty'
                  and key['curve']['reference_tune_id'] is not None]
        self.assertTrue(ratios)
        self.assertEqual({key['curve']['reference_tune_id'] for key in ratios},
                         {'JUNCTIONS'})
        self.assertEqual({key['curve']['tune_id'] for key in ratios},
                         {'MONASH','CLOSEPACKING'})
        self.assertNotEqual(baseline.scientific_request_sha256,
                            changed.scientific_request_sha256)
        self.assertEqual(len({self.p.semantic_id(changed,key) for key in ratios}),
                         len(ratios))

    def test_dto_unknown_keys_noncanonical_float_and_block_misalignment_fail(self):
        request=self.request()
        for mutate in (lambda p:p.update(unknown=1), lambda p:p['profiles'][0]['trigger_eta'].update(low='-0x1p+2'),
                       lambda p:p['statistics']['block_ids'].reverse()):
            payload=request.to_dict(); mutate(payload)
            with self.assertRaises(ValueError): self.p.ProjectionRequest.from_dict(payload)
        detached=request.to_dict(); detached['scope']['ordered_tunes'].append('MUTANT')
        self.assertEqual(request.to_dict()['scope']['ordered_tunes'], ['MONASH'])

    def result_fixture(self):
        p=self.p
        request=self.request().to_dict()
        keys=[k for o in request['observables'] for k in o['joint_point_domain']
              if k['curve']['role_id']=='balancing.integrated.beauty'][:3]
        request['scope']['roles']=[dict(role_id='balancing.integrated.beauty', ordered_panels=[], required_curve_keys=[k['curve'] for k in keys])]
        request['observables']=[dict(quantity='os_minus_ss_per_trigger', formula_version=request['science_contract']['formula_contract_version'],output_units='1',component='NONE',joint_point_domain=keys)]
        request['statistics']['covariance_groups']=[dict(id='joint',ordered_point_keys=keys,representation='DENSE',required_cross_groups=['balancing.integrated.beauty'])]
        req=p.ProjectionRequest.from_dict(request)
        def specimen(spec):
            if isinstance(spec,tuple): return None
            if isinstance(spec,list): return []
            if isinstance(spec,dict): return {k:specimen(v) for k,v in spec.items()}
            if spec in p.SCHEMAS: return specimen(p.SCHEMAS[spec])
            if spec.startswith('='): return spec[1:]
            if '|' in spec: return spec.split('|')[0]
            return {'Digest':'a'*64,'GitOid':'1'*40,'Hex64':float(0).hex(),'Count':0,'Int':0,'PDG':521,
                    'Finite':0.,'Bool':False,'True':True,'Text':'test','Id':'test','Quantity':'os_minus_ss_per_trigger'}[spec]
        points=[]
        for i,k in enumerate(keys):
            point=specimen('PointResult'); point.update(key=k,semantic_id=p.semantic_id(req,k),units='1',
                center=p.hex64(-2 if i==0 else 0) if i!=2 else None,
                center_status='AVAILABLE' if i!=2 else 'UNDEFINED',
                standard_error=p.hex64(0) if i==1 else None,variance=p.hex64(0) if i==1 else None,
                uncertainty_status='AVAILABLE_ZERO_DISPERSION' if i==1 else 'WITHHELD_UNCERTAINTY',
                covariance_group_ids=['joint'],reasons=['CLASS_BOUNDARY_UNSTABLE'] if i==0 else [])
            point['block_values']=[dict(specimen('BlockPrimitiveReceipt'),tune_id='MONASH',block_id=b,
                additive_components=[dict(id='count',value=p.hex64(b))]) for b in range(1,11)]
            denominator=dict(natural_key=p.canonical(k)+"/parent=trigger", pooled_value=p.hex64(55),
                status="AVAILABLE", retained_after_algebra=True, delete_one_statuses=["AVAILABLE"]*10, policy_id=p.ESTIMATOR)
            point['denominator_receipts']=[denominator]
            point['semantic_parents']=[dict(natural_key=denominator['natural_key'], exists=True, materialized=True,
                content_digest=p.digest(denominator), coverage_status="COMPLETE_K10")]
            points.append(point)
        cov=specimen('CovarianceResult');cov.update(id='joint',ordered_point_keys=keys,valid_mask=[False,True,False],
            units_by_point=['1']*3,status='AVAILABLE_PARTIAL',K=10,dof=9,representation='DENSE',
            dense_rows=[[None,None,None],[None,p.hex64(0),None],[None,None,None]],rank_bound=1,
            independent_families=[dict(tune_id='MONASH',source_family_digest=p.digest(request['sources']['members']),block_ids=list(range(1,11)),
                complements=[[None,p.hex64(0),None] for _ in range(10)],leave_mean=[None,p.hex64(0),None],covariance_prefactor=p.hex64(.9))])
        cov['content_sha256']=p.digest({k:v for k,v in cov.items() if k!='content_sha256'})
        route=specimen('PrimitiveRoute');route.update(primitive_family='compact_primitives',root_object_names=['cells'],object_content_digests=['a'*64])
        value=specimen('ProjectionResult');value.update(request_echo=request,request_sha256=req.request_sha256,scientific_request_sha256=req.scientific_request_sha256,
            source_receipt=request['sources'],points=points,covariance=[cov],primitive_routes=[route],
            materialization=[dict(point_key=k,status='PRESENT',reason_codes=[]) for k in keys],
            package_state='VALIDATED_COMPLETE',campaign_state='PARTIAL_SAMPLE')
        value['resolved']=dict(profiles=request['profiles'],axes=request['axes'],signed_pairs=request['scope']['ordered_associate_pairs'],
            expected_point_keys=req.expected_point_keys,class_boundaries=[dict(specimen('ResolvedClass'),tune_id='MONASH',class_id=c['id'],requested=c) for c in request['classes']],
            observed_support=p.observed_support(request,points,value['materialization']),
            category_order=p.category_order(request,{pair['associate_pdg']:str(pair['associate_pdg'])
                for pair in request['scope']['ordered_associate_pairs']}))
        value['capability_receipt']=[dict(specimen('CapabilityReceipt'),capability_id=c) for c in request['execution']['required_capabilities']]
        for name in ('analysis_config_sha256','particle_registry_sha256','activity_definition_sha256'):
            value['provenance'][name]=request['bindings'][name]
        value['provenance']['normalized_runtime_id']=p.digest(value['provenance']['runtime'])
        value['provenance']['selection_definitions_sha256']=p.digest(dict(
            profiles=request['profiles'], activity=request['activity'], classes=request['classes']))
        value['provenance']['source_selection_definitions']=p.source_selection_definitions(
            self.receipt, self.analysis['pair_acceptance'])
        value['artifact_binding']['root_content_sha256']=request['bindings']['expected_source_content_sha256']
        value['science_content_sha256']=p.digest({k:value[k] for k in ('scientific_request_sha256','resolved','points','covariance','materialization')})
        return req,value,[route]

    def test_independent_negative_center_withheld_error_zero_and_undefined_states(self):
        req,value,routes=self.result_fixture()
        result=self.p.ProjectionResult.from_dict(value,req,routes).to_dict()
        self.assertEqual(result['points'][0]['center'],float(-2).hex())
        self.assertIsNone(result['points'][0]['standard_error'])
        self.assertEqual(result['points'][1]['standard_error'],float(0).hex())
        self.assertIsNone(result['points'][2]['center'])
        self.assertEqual(result['package_state'],'VALIDATED_COMPLETE')
        self.assertEqual(result['covariance'][0]['valid_mask'],[False,True,False])

    def test_synthetic_route_cannot_claim_campaign_or_science_capability(self):
        req,value,unused=self.result_fixture()
        route=value['primitive_routes'][0]
        route.update(source_kind='TEST_ONLY_SYNTHETIC',route='EXACT_ROWS',
                     exactness='BINARY64_ROWS')
        value['provenance']['generator_name']='TEST_ONLY_SYNTHETIC_LITERAL_GENERATOR'
        value['provenance']['data_limitations'].append('TEST_ONLY_SYNTHETIC_NO_PHYSICS')
        self.p.ProjectionResult.from_dict(value,req,[route])
        for mutate in (lambda v:v.update(campaign_state='FULL_ACCEPTED_CAMPAIGN'),
                       lambda v:v['capability_receipt'][0].update(supported=True),
                       lambda v:v['provenance'].update(generator_name='PRODUCTION')):
            changed=copy.deepcopy(value);mutate(changed)
            with self.assertRaisesRegex(ValueError,
                'TEST_ONLY_SYNTHETIC route cannot claim production/campaign acceptance'):
                self.p.ProjectionResult.from_dict(changed)

    def test_resigned_omission_state_route_and_covariance_mutants_fail(self):
        req,original,routes=self.result_fixture()
        mutants=[lambda v:v['points'].pop(),lambda v:v['materialization'].pop(),
            lambda v:v['resolved']['expected_point_keys'].pop(),
            lambda v:v['points'][0].update(center=None),
            lambda v:v['points'][0].update(standard_error=float(0).hex(),variance=float(0).hex()),
            lambda v:v['points'][1]['block_values'].pop(),
            lambda v:v['points'][1]['covariance_group_ids'].clear(),
            lambda v:v['covariance'][0]['valid_mask'].__setitem__(0,True),
            lambda v:v['covariance'][0]['independent_families'][0]['block_ids'].reverse(),
            lambda v:v['primitive_routes'][0].update(route='NATIVE_ALIGNED_SPARSE',exactness='ALIGNED_RECTANGLE')]
        for mutate in mutants:
            value=copy.deepcopy(original);mutate(value)
            for cov in value['covariance']:cov['content_sha256']=self.p.digest({k:v for k,v in cov.items() if k!='content_sha256'})
            value['science_content_sha256']=self.p.digest({k:value[k] for k in ('scientific_request_sha256','resolved','points','covariance','materialization')})
            with self.assertRaises(ValueError):self.p.ProjectionResult.from_dict(value,req,routes)

    def query_result_fixture(self, profile_index=1):
        if profile_index==1 and len(self.analysis['profiles'])==1:
            self.analysis['profiles'].append(dict(id='ordered_minima',
                trigger_pt=dict(operator='>=',value=1.0),
                associate_pt=dict(operator='>=',value=.15),relative_pt=None))
            self.receipt['scientific_identity']['compact_domains']['profiles'] = copy.deepcopy(self.analysis['profiles'])
            self.presentation['selection_definitions']['profiles'] = copy.deepcopy(self.analysis['profiles'])
        self.selection['profile_id'] = self.analysis['profiles'][profile_index]['id']
        req, value, unused = self.result_fixture()
        model = self.p._query_model()
        plans = model.primitive_routes(self.analysis, self.analysis, 'aligned_sparse')
        names = ['sparse:activity', 'sparse:pairs', 'sparse:triggers'] + [
            'tree:' + name for name in ('events', 'sources', 'source_blocks', 'event_ranges',
                                       'source_counts', 'heavy', 'triggers', 'pairs', 'origins',
                                       'closure', 'constituents', 'event_compatibility')]
        observations = [dict(ordinal=0, digests={n:'a'*64 for n in names}, counts={n:17 for n in names})]
        routes = model.authenticated_routes(self.analysis, plans, True, observations)
        value['primitive_routes'] = [r for r in routes if r['profile_id'] in (None, req.to_dict()['profiles'][0]['id'])]
        return req, self.p.ProjectionResult.from_dict(value).to_dict()

    def resign_result(self, value):
        req = self.p.ProjectionRequest.from_dict(value['request_echo'])
        value.update(request_sha256=req.request_sha256, scientific_request_sha256=req.scientific_request_sha256)
        value['resolved']['profiles'] = copy.deepcopy(value['request_echo']['profiles'])
        for point in value['points']:
            point['semantic_id'] = self.p.semantic_id(req, point['key'])
        value['provenance']['selection_definitions_sha256'] = self.p.digest(dict(
            profiles=value['request_echo']['profiles'], activity=value['request_echo']['activity'],
            classes=value['request_echo']['classes']))
        value['science_content_sha256'] = self.p.digest({k:value[k] for k in (
            'scientific_request_sha256', 'resolved', 'points', 'covariance', 'materialization')})

    def test_resigned_profile_relabel_fails_dto_plot_and_source_boundaries(self):
        req, original = self.query_result_fixture()
        value = copy.deepcopy(original)
        profile = value['request_echo']['profiles'][0]
        profile['trigger_pt']['low'], profile['associate_pt']['low'] = map(self.p.hex64, (2.5, .5))
        self.resign_result(value)
        with self.assertRaisesRegex(ValueError, 'source selection provenance'):
            self.p.ProjectionResult.from_dict(value)
        spec = importlib.util.spec_from_file_location('relabel_plot', ROOT / 'pipeline/plot/run.py')
        plot = importlib.util.module_from_spec(spec); spec.loader.exec_module(plot)
        if hasattr(plot, 'checked_phase_a_typed_result'):
            path = self.base / 'relabeled.json'; path.write_text(json.dumps(value))
            with self.assertRaisesRegex(ValueError, 'source selection provenance'):
                plot.checked_phase_a_typed_result(path)

    def test_pairs_and_triggers_independently_bind_predicates_bins_and_flow(self):
        req, original = self.query_result_fixture()
        for family in ('pairs', 'triggers'):
            mutations = [lambda r: r.update(predicate_sha256='0'*64),
                         lambda r: r['resolved_axis_selection'][0]['included_regular_bins'].pop(0),
                         lambda r: r['resolved_axis_selection'][0].update(include_overflow=False),
                         lambda r: r['resolved_axis_selection'][0].update(include_underflow=True),
                         lambda r: r['resolved_axis_selection'][0]['predicate'].update(low=self.p.hex64(2.5))]
            for mutate in mutations:
                value = copy.deepcopy(original)
                route = next(r for r in value['primitive_routes'] if r['primitive_family'] == family)
                mutate(route); self.resign_result(value)
                with self.subTest(family=family, route=route), self.assertRaisesRegex(ValueError, family + ' .*source selection provenance'):
                    self.p.ProjectionResult.from_dict(value)
        value = copy.deepcopy(original)
        pairs = next(r for r in value['primitive_routes'] if r['primitive_family'] == 'pairs')
        triggers = next(r for r in value['primitive_routes'] if r['primitive_family'] == 'triggers')
        triggers['resolved_axis_selection'].append(copy.deepcopy(pairs['resolved_axis_selection'][1]))
        with self.assertRaisesRegex(ValueError, 'triggers resolved axis'):
            self.p.ProjectionResult.from_dict(value)
        triggers['resolved_axis_selection'].pop()
        triggers['predicate_sha256'] = pairs['predicate_sha256']
        with self.assertRaisesRegex(ValueError, 'triggers primitive predicate'):
            self.p.ProjectionResult.from_dict(value)

    def test_source_binding_rejects_coherently_rewritten_selection_and_routes(self):
        req, original = self.query_result_fixture()
        source_receipt = copy.deepcopy(self.receipt)
        embedded = dict(pair_acceptance=self.analysis['pair_acceptance'], scientific_projection_source=dict(
            kind='verified_root_query_primitives', primitive_route_receipts=original['primitive_routes']))
        self.p.validate_result_source(self.p.ProjectionResult.from_dict(original), self.receipt, embedded)
        # Even a coherent, freshly generated different selection cannot reuse the old source authority.
        self.analysis['profiles'][1]['trigger_pt']['value'] = 2.5
        self.analysis['profiles'][1]['associate_pt']['value'] = .5
        self.receipt['scientific_identity']['compact_domains']['profiles'] = copy.deepcopy(self.analysis['profiles'])
        unused, changed = self.query_result_fixture()
        with self.assertRaisesRegex(ValueError, 'source selection provenance differs from authenticated ROOT'):
            receipt = copy.deepcopy(self.receipt)
            receipt['scientific_identity']['compact_domains']['profiles'] = original['provenance']['source_selection_definitions']['profiles']
            self.p.validate_result_source(self.p.ProjectionResult.from_dict(changed), receipt, embedded)
        mutated = copy.deepcopy(original)
        mutated['primitive_routes'][1]['object_content_digests'] = ['b'*64]
        with self.assertRaisesRegex(ValueError, 'primitive routes differ from authenticated ROOT'):
            self.p.validate_result_source(self.p.ProjectionResult.from_dict(mutated), source_receipt, embedded)

    def test_source_dto_and_plot_phase_a_policy_parity(self):
        spec = importlib.util.spec_from_file_location('policy_plot', ROOT / 'pipeline/plot/run.py')
        plot = importlib.util.module_from_spec(spec); spec.loader.exec_module(plot)
        model = self.p._query_model()
        inclusive = copy.deepcopy(self.analysis['profiles'][0])
        ordered = dict(id='ordered_minima',trigger_pt=dict(operator='>=',value=1.0),
                       associate_pt=dict(operator='>=',value=.15),relative_pt=None)
        request = self.request().to_dict()
        request['profiles'].append(self.p.normalized_profile(
            ordered, 4., request['science_contract']['structural_registry_sha256']))
        self.p.ProjectionRequest.from_dict(request)  # A selected one-profile slice and a canonical ordered list are valid DTOs.
        negative = copy.deepcopy(ordered); negative['associate_pt']['value'] = -.5
        negative_both = copy.deepcopy(ordered)
        negative_both['trigger_pt']['value'], negative_both['associate_pt']['value'] = -.1, -.5
        extra = copy.deepcopy(ordered); extra['id'] = 'second_minima'
        strict = copy.deepcopy(ordered); strict['trigger_pt']['operator'] = '>'
        malformed = copy.deepcopy(ordered); malformed['id'] = 'Bad Profile'
        equal = copy.deepcopy(ordered); equal['trigger_pt']['value'] = .15
        cases = [([inclusive], True), ([ordered], True), ([inclusive, ordered], True),
                 ([], False), ([ordered, inclusive], False), ([ordered, extra], False),
                 ([inclusive, ordered, extra], True), ([negative], False), ([negative_both], False),
                 ([strict], False), ([malformed], False), ([equal], True)]
        for profiles, accepted in cases:
            typed = [self.p.normalized_profile(p, 4., 'a'*64) for p in profiles]
            for label, validator, payload in (('source', lambda x: model.validate_phase_a_profiles(
                    x, self.analysis['axes']['pt']['edges']), profiles),
                                       ('typed', lambda x: self.p.validate_typed_phase_a_profiles(
                    x, self.analysis['axes']['pt']['edges']), typed)):
                with self.subTest(profiles=profiles, validator=label):
                    source_accepts = accepted and not (
                        label == 'source' and
                        len(profiles) == 1 and profiles[0].get('id') != 'inclusive')
                    if source_accepts: validator(payload)
                    else:
                        with self.assertRaises(ValueError): validator(payload)
            if len(profiles) == 1 and hasattr(plot, 'typed_profile_kind'):
                if accepted: self.assertEqual(plot.typed_profile_kind(typed[0]), model.phase_a_profile_kind(profiles[0]))
                else:
                    with self.assertRaises(ValueError): plot.typed_profile_kind(typed[0])
            if not accepted:
                req, value, unused = self.result_fixture()
                value['request_echo']['profiles'] = typed
                with self.assertRaises(ValueError): self.p.ProjectionRequest.from_dict(value['request_echo'])
                with self.assertRaises(ValueError): self.p.ProjectionResult.from_dict(value)



if __name__ == '__main__':
    unittest.main()
