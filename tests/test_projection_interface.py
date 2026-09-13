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
        unused, pairs = self.p._reducer().state_registry(self.analysis)
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

    def test_wholly_absent_requested_tune_retains_absolute_and_reference_curves(self):
        request = self.request(('MONASH','JUNCTIONS'))
        keys = [k for k in request.expected_point_keys if k['curve']['tune_id']=='JUNCTIONS']
        self.assertTrue(keys)
        self.assertTrue(any(k['curve']['reference_tune_id']=='MONASH' for k in keys))
        self.assertTrue(any(k['curve']['reference_tune_id'] is None for k in keys))
        request_payload = request.to_dict()
        self.assertEqual({self.p._availability(k, request_payload, self.receipt)[0] for k in keys}, {'NOT_MATERIALIZED'})
        self.assertEqual({m['tune_id'] for m in request.to_dict()['sources']['members']}, {'MONASH'})

    def test_wholly_absent_5122_pair_does_not_shrink_requested_domain(self):
        before = self.request()
        changed = copy.deepcopy(self.receipt)
        domains = changed['scientific_identity']['compact_domains']
        domains['pair_query_dictionary'] = [p for p in domains['pair_query_dictionary'] if p['trigger_pdg']!=5122]
        domains['correlation_dictionary'] = [p for p in domains['correlation_dictionary'] if p['trigger_pdg']!=5122]
        after = self.request(receipt=changed)
        self.assertEqual(before.expected_point_keys, after.expected_point_keys)
        keys = [k for k in after.expected_point_keys if k['curve']['trigger_pdg']==5122]
        self.assertTrue(keys)
        after_payload = after.to_dict()
        self.assertEqual({self.p._availability(k, after_payload, changed)[0] for k in keys}, {'NOT_MATERIALIZED'})
        self.assertTrue(any(p['trigger_pdg']==5122 and p['associate_pdg']==521 and p['sign']=='OS' for p in after.to_dict()['scope']['ordered_associate_pairs']))
        self.assertTrue(any(p['trigger_pdg']==5122 and p['associate_pdg']==-521 and p['sign']=='SS' for p in after.to_dict()['scope']['ordered_associate_pairs']))

    def test_changed_classes_bind_current_analysis_and_report_reprojection(self):
        before = self.request()
        analysis = copy.deepcopy(self.analysis)
        analysis['percentile_intervals'] = [[0,25],[25,100]]
        after = self.request(analysis=analysis)
        self.assertNotEqual(before.request_sha256, after.request_sha256)
        self.assertNotEqual(before.scientific_request_sha256, after.scientific_request_sha256)
        self.assertEqual(after.to_dict()['bindings']['analysis_config_sha256'], self.p.file_digest(self.base/'requested-analysis.json'))
        self.assertNotEqual(after.to_dict()['bindings']['analysis_config_sha256'], self.receipt['scientific_identity']['analysis_request_sha256'])
        keys = [k for k in after.expected_point_keys if k['curve']['class_id'] in (1,2)]
        self.assertTrue(keys)
        after_payload = after.to_dict()
        self.assertEqual({self.p._availability(k, after_payload, self.receipt)[0] for k in keys}, {'UNSUPPORTED_QUERY'})

    def test_activity_pt_metadata_is_derived_and_mutation_changes_identity(self):
        before = self.request()
        analysis = copy.deepcopy(self.analysis)
        analysis['activities'][0]['predicate'] = analysis['activities'][0]['predicate'].replace('pt>0.15','pt>=0.25')
        after = self.request(analysis=analysis)
        self.assertEqual(after.to_dict()['activity']['pt']['low'], float(.25).hex())
        self.assertEqual(after.to_dict()['activity']['pt']['low_operator'], 'GE')
        self.assertNotEqual(before.scientific_request_sha256, after.scientific_request_sha256)
        self.assertNotEqual(after.to_dict()['activity'], self.p.normalized_activity(self.presentation['selection_definitions']['activities'][0]))

    def test_activity_metadata_mutation_is_rejected_at_source_boundary(self):
        from types import SimpleNamespace
        request=self.request();root=self.base/'fixture.root';root.write_bytes(b'identity-only-fixture')
        receipt=copy.deepcopy(self.receipt);receipt['storage_identity']={'root_sha256':self.p.file_digest(root)}
        presentation=copy.deepcopy(self.presentation)
        presentation['selection_definitions']['activities'][0]['predicate']=presentation['selection_definitions']['activities'][0]['predicate'].replace('pt>0.15','pt>0.25')
        source=SimpleNamespace(receipt=receipt,presentation=presentation,root_path=root,
            expected_source_content_sha256=self.p.digest(receipt['scientific_identity']))
        with self.assertRaisesRegex(ValueError,'activity definition differs'):
            self.p.project_result(source,request)

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
                for associate in (-411,-421,-4122)})
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

    def test_first_p4_domain_is_exact_six_channels_eighteen_absolute_twelve_ratios(self):
        request = self.request(('MONASH', 'JUNCTIONS', 'CLOSEPACKING'))
        keys = [k for k in request.expected_point_keys
                if k['curve']['role_id'] == 'balancing.integrated.charm']
        absolute = [k for k in keys if k['curve']['reference_tune_id'] is None]
        ratios = [k for k in keys if k['curve']['reference_tune_id'] == 'MONASH']
        channels = {(k['curve']['trigger_pdg'], k['curve']['associate_pdg'])
                    for k in keys}
        self.assertEqual(channels, {(trigger, associate)
                         for trigger in (411, 4122)
                         for associate in (-411, -421, -4122)})
        self.assertEqual((len(absolute), len(ratios), len(keys)), (18, 12, 30))

    def test_manifest_exposure_classification_distinguishes_unequal_and_missing(self):
        receipt = copy.deepcopy(self.receipt)
        domains = receipt['scientific_identity']['compact_domains']
        def accounting(values):
            receipt['_embedded_block_accounting'] = {'blocks': [
                {'tune': 0, 'block': block, 'successful_events': value}
                for block, value in enumerate(values, 1)]}
            return self.p.tune_design_statuses(receipt)['MONASH']
        self.assertEqual(accounting([100] * 10), 'AVAILABLE')
        self.assertEqual(accounting([100] * 9 + [200]), 'UNEQUAL_DESIGN_EXPOSURE')
        self.assertEqual(accounting([100] * 9), 'INCOMPLETE_BLOCK_SET')
        receipt['_embedded_block_accounting']['blocks'].append(
            {'tune': 0, 'block': 1, 'successful_events': 100})
        with self.assertRaisesRegex(ValueError, 'duplicate tune/block'):
            self.p.tune_design_statuses(receipt)

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
        request['observables']=[dict(quantity='os_minus_ss_per_trigger', formula_version='projection_formulas_v2',output_units='1',component='NONE',joint_point_domain=keys)]
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
        from types import SimpleNamespace
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
        root = self.base / 'source.root'; root.write_bytes(b'bound source fixture')
        receipt = copy.deepcopy(self.receipt)
        receipt['storage_identity'] = dict(root_sha256=self.p.file_digest(root))
        source = SimpleNamespace(receipt=receipt, presentation=self.presentation, root_path=root,
            expected_source_content_sha256=self.p.digest(receipt['scientific_identity']),
            routes=lambda request: original['primitive_routes'])
        with self.assertRaisesRegex(ValueError, 'source selection provenance'):
            self.p.project_result(source, self.p.ProjectionRequest.from_dict(value['request_echo']))

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

    def test_typed_bundle_carries_configs_through_swapped_result_order(self):
        from unittest.mock import patch
        spec = importlib.util.spec_from_file_location('bundle_plot', ROOT / 'pipeline/plot/run.py')
        plot = importlib.util.module_from_spec(spec); spec.loader.exec_module(plot)
        if not hasattr(plot, 'checked_phase_a_typed_result'):
            self.skipTest('P typed bundle adapter is not installed in this S worktree')
        unused, inclusive = self.query_result_fixture(0)
        unused, ordered = self.query_result_fixture(1)
        embedded = dict(pair_acceptance=self.analysis['pair_acceptance'], scientific_projection_source=dict(
            kind='verified_root_query_primitives', primitive_route_receipts=
            inclusive['primitive_routes'][:3] + ordered['primitive_routes'][1:3] + inclusive['primitive_routes'][3:]))
        body = self.p.canonical(embedded).encode('ascii')
        root = self.base / 'bundle.root'; root.write_bytes(b'fixture root identity')
        receipt = copy.deepcopy(self.receipt)
        receipt['scientific_identity']['embedded_receipt_sha256'] = plot.sha_bytes(body)
        receipt['storage_identity'] = dict(root_sha256=self.p.file_digest(root))
        manifest = self.base / 'bundle.json'; manifest.write_text(json.dumps(receipt))
        records, configs = {}, []
        for index, value in enumerate((inclusive, ordered)):
            profile_id = value['request_echo']['profiles'][0]['id']
            config = copy.deepcopy(self.config)
            path = self.base / f'plot-{index}.json'; path.write_text(json.dumps(config)); configs.append(path)
            value['request_echo']['presentation_binding']['plot_config_sha256'] = self.p.file_digest(path)
            value['request_echo']['bindings']['expected_source_content_sha256'] = self.p.digest(receipt['scientific_identity'])
            value['artifact_binding'].update(root_sha256=self.p.file_digest(root), root_bytes=root.stat().st_size,
                root_content_sha256=self.p.digest(receipt['scientific_identity']), manifest_sha256=self.p.file_digest(manifest))
            self.resign_result(value)
            projection = self.p.ProjectionResult.from_dict(value)
            records[index] = (projection, dict(profile=profile_id, profile_kind=('inclusive', 'ordered_minima')[index]), {'campaign':'same'})
        with patch.object(plot, 'checked_phase_a_typed_result', side_effect=lambda key: records[key]), \
                patch.object(plot, '_read_embedded_payload', return_value=(embedded, {'receipt':body})):
            for current in configs:
                forward = plot.checked_phase_a_typed_bundle(0, 1, root, manifest, *configs, current)
                reverse = plot.checked_phase_a_typed_bundle(1, 0, root, manifest, *reversed(configs), current)
                self.assertEqual(forward, reverse)
                self.assertEqual(forward['released_profile_ids'], [p['id'] for p in self.analysis['profiles']])
            with self.assertRaisesRegex(ValueError, 'presentation binding'):
                plot.checked_phase_a_typed_bundle(1, 0, root, manifest, *configs, configs[0])
            with self.assertRaisesRegex(ValueError, 'inclusive and one ordered-minima'):
                plot.checked_phase_a_typed_bundle(0, 0, root, manifest, configs[0], configs[0], configs[0])

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


class JointCovarianceContract(unittest.TestCase):
    def test_cpp_full_joint_covariance_shared_reference_and_independent_families(self):
        compiler=shutil.which('c++')
        if compiler is None: self.skipTest('C++ unavailable')
        source=r'''
#include "projection.hpp"
#include <iostream>
#include <iomanip>
using namespace Hadronization::Projection;
JointPoint point(std::string id, std::vector<std::pair<std::string,int>> families) {
  JointPoint p; p.id=id; p.valid=true;
  for (const auto& f:families) {
    std::array<double,10> a{}; for(int k=0;k<10;++k)a[k]=f.second*(k+1);
    p.complements[f.first]=a; p.means[f.first]=f.second*5.5;
  }
  return p;
}
int main() {
  std::vector<JointPoint> p{point("OS",{{"MONASH",1}}),point("SS",{{"MONASH",2}}),
    point("OS-SS",{{"MONASH",-1}}),point("J/M class1",{{"JUNCTIONS",3},{"MONASH",4}}),
    point("C/M class2",{{"CLOSEPACKING",5},{"MONASH",6}}),point("independent",{{"OTHER",7}}),
    point("zero dispersion",{{"MONASH",0}})};
  std::cout<<std::hexfloat;
  for (const auto& a:p) {for(const auto& b:p)std::cout<<JointCovariance(a,b)<<' ';std::cout<<'\n';}
  JointPoint missing; missing.id="withheld";
  if(!std::isnan(JointCovariance(p[0],missing)))return 2;
  p[0].means["MONASH"]+=1;
  try{JointCovariance(p[0],p[0]);return 3;}catch(const std::exception&){}
}
'''
        with tempfile.TemporaryDirectory() as temporary:
            base=Path(temporary); (base/'joint.cpp').write_text(source)
            completed=subprocess.run([compiler,'-std=c++17','-Wall','-Wextra','-Werror','-ffp-contract=off',
                '-I'+str(ROOT/'pipeline/reduce'),str(base/'joint.cpp'),'-o',str(base/'joint')],capture_output=True,text=True)
            self.assertEqual((completed.returncode,completed.stderr),(0,''))
            completed=subprocess.run([str(base/'joint')],capture_output=True,text=True)
            self.assertEqual((completed.returncode,completed.stderr),(0,''))
        matrix=[[float.fromhex(v) for v in line.split()] for line in completed.stdout.splitlines()]
        families=[{'MONASH':1},{'MONASH':2},{'MONASH':-1},{'JUNCTIONS':3,'MONASH':4},
                  {'CLOSEPACKING':5,'MONASH':6},{'OTHER':7},{'MONASH':0}]
        dispersion=Fraction(9,10)*sum((Fraction(k)-Fraction(11,2))**2 for k in range(1,11))
        for i,a in enumerate(families):
            for j,b in enumerate(families):
                expected=dispersion*sum(v*b.get(t,0) for t,v in a.items())
                self.assertAlmostEqual(matrix[i][j],float(expected),delta=max(1e-12,abs(float(expected))*1e-14))
        self.assertGreater(matrix[3][4],0) # Shared MONASH reference is counted exactly once.
        self.assertEqual(matrix[0][5],0)
        self.assertEqual(matrix[6][6],0)
        self.assertLess(matrix[0][2],0)

    def test_unequal_exposure_withholds_error_without_erasing_pooled_center(self):
        compiler = shutil.which('c++')
        if compiler is None: self.skipTest('C++ unavailable')
        source = r'''
#include "projection.hpp"
#include <iostream>
using namespace Hadronization::Projection;
using namespace Hadronization::Reduction;
int main() {
  Domains d; d.tuneDesignStatus["JUNCTIONS"]="UNEQUAL_DESIGN_EXPOSURE";
  Scope s; s.tune="JUNCTIONS"; s.classId=0;
  std::vector<std::vector<double>> blocks;
  for (int b=1;b<=10;++b) blocks.push_back({double(3*b+1),double(b),double(5*b+7)});
  auto result=Estimate(blocks,[](const auto& x){
    return FunctionValue{true,{(x[0]-x[1])/x[2]}, {}};
  },{},BoundaryReasons(d,s));
  if (result.estimate.center.size()!=1 || !std::isfinite(result.estimate.center[0])) return 2;
  if (result.estimate.valueStatus!="AVAILABLE") return 3;
  if (result.estimate.uncertaintyStatus!="UNEQUAL_DESIGN_EXPOSURE") return 4;
  if (!result.estimate.standardError.empty() || !result.estimate.covariance.empty()) return 5;
  std::cout << std::hexfloat << result.estimate.center[0] << '\n';
}
'''
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary); (base/'design.cpp').write_text(source)
            completed = subprocess.run([compiler, '-std=c++17', '-Wall', '-Wextra',
                '-Werror', '-ffp-contract=off', '-I'+str(ROOT/'pipeline/reduce'),
                str(base/'design.cpp'), '-o', str(base/'design')],
                capture_output=True, text=True)
            self.assertEqual((completed.returncode, completed.stderr), (0, ''))
            completed = subprocess.run([str(base/'design')], capture_output=True, text=True)
        self.assertEqual((completed.returncode, completed.stderr), (0, ''))
        pooled = (sum(3*b+1 for b in range(1,11)) - sum(range(1,11))) / \
                 sum(5*b+7 for b in range(1,11))
        self.assertEqual(float.fromhex(completed.stdout.strip()), pooled)

    def test_final_tune_ratio_screens_only_surviving_denominators(self):
        compiler = shutil.which('c++')
        if compiler is None: self.skipTest('C++ unavailable')
        source = r'''
#include "projection.hpp"
#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
namespace P=Hadronization::Projection; namespace R=Hadronization::Reduction;
using V=std::vector<double>; using M=std::vector<V>;
R::DenominatorSeries denominator(const M& blocks,const std::string& id,int component){
  R::DenominatorSeries value; value.id=id; value.exact=true;
  for(const auto& block:blocks)value.blocks.push_back(component==3?block[0]-block[1]:block[component]);
  return value;
}
int main(){
  M source(10,V{10,0,20}),reference(10,V{10,0,1});reference[0][2]=1000;
  auto balance=[](const V& x){return R::FunctionValue{true,{(x[0]-x[1])/x[2]}, {}};};
  auto a=P::Estimate(source,balance,{denominator(source,"source_trigger",2)});
  auto m=P::Estimate(reference,balance,{denominator(reference,"reference_trigger",2)});
  auto final=P::IndependentRatio(a,m,{denominator(reference,"reference_tune_os_minus_ss",3)});
  if(P::ValueStatus(final,0)!="AVAILABLE" || P::UncertaintyStatus(final,0)!="AVAILABLE")return 2;
  if(!P::Reasons(final,0).empty())return 3;
  if(final.estimate.center.size()!=1 || final.estimate.covariance.size()!=1 ||
     final.estimate.standardError.size()!=1)return 4;
  if(std::find(final.estimate.cancelledParentDiagnostics.begin(),
               final.estimate.cancelledParentDiagnostics.end(),"reference_trigger")==
     final.estimate.cancelledParentDiagnostics.end())return 5;
  M noSourceTrigger=source;for(auto& block:noSourceTrigger)block[2]=0;
  auto badSource=P::IndependentRatio(
      P::Estimate(noSourceTrigger,balance,{denominator(noSourceTrigger,"source_trigger",2)}),m,
      {denominator(reference,"reference_tune_os_minus_ss",3)});
  if(P::ValueStatus(badSource,0)=="AVAILABLE")return 6;
  M noReferenceNet=reference;for(auto& block:noReferenceNet)block[0]=block[1];
  auto badReference=P::IndependentRatio(
      a,P::Estimate(noReferenceNet,balance,{denominator(noReferenceNet,"reference_trigger",2)}),
      {denominator(noReferenceNet,"reference_tune_os_minus_ss",3)});
  if(P::ValueStatus(badReference,0)=="AVAILABLE")return 7;
  std::cout<<std::setprecision(17)<<final.estimate.center[0]<<' '
           <<final.estimate.covariance[0]<<' '<<final.estimate.standardError[0]<<'\n';
}
'''
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary); (base/'final-ratio.cpp').write_text(source)
            completed = subprocess.run([compiler, '-std=c++17', '-Wall', '-Wextra',
                '-Werror', '-ffp-contract=off', '-I'+str(ROOT/'pipeline/reduce'),
                str(base/'final-ratio.cpp'), '-o', str(base/'final-ratio')],
                capture_output=True, text=True)
            self.assertEqual((completed.returncode, completed.stderr), (0, ''))
            completed = subprocess.run([str(base/'final-ratio')], capture_output=True, text=True)
        self.assertEqual((completed.returncode, completed.stderr), (0, ''))
        center, variance, error = map(float, completed.stdout.split())
        self.assertEqual(center, 1009/200)
        self.assertAlmostEqual(variance, 998001/40000, places=14)
        self.assertAlmostEqual(error, 999/200, places=14)


from projection_formula_fixture import (GEOMETRY_AND_RATIO,NESTED_RATIO,
                                        ProjectionFormulaOracles)


class ScientificProjectionFormulaContract(ProjectionFormulaOracles,unittest.TestCase):
    """Only the small pre-existing C++ formula fixtures; no production/plot run."""
    @classmethod
    def setUpClass(cls):
        import os
        p=load_interface()
        try: runtime=p._reducer().runtime_module().resolve(require_root=True)
        except ValueError as error: raise unittest.SkipTest(str(error))
        cls.environment=os.environ.copy();cls.environment.update(runtime['environment'])
        cls.temporary=tempfile.TemporaryDirectory();cls.base=Path(cls.temporary.name)
        cls._compile(GEOMETRY_AND_RATIO,cls.base/'geometry.cpp',
                     cls.base/'geometry',include_plot=True,root=False)
        cls._compile(NESTED_RATIO,cls.base/'nested.cpp',
                     cls.base/'nested',include_plot=True)

    @classmethod
    def tearDownClass(cls): cls.temporary.cleanup()

if __name__=='__main__': unittest.main()
