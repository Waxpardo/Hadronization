"""Architect v4's observed moments, collection fileset and attempt scopes."""
import copy
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

from helpers import ROOT
from pipeline.reduce import accounting,archive,archive_v4,native_runner,native_v4,native_v4_result,projection as p


class NativeV4Metadata(unittest.TestCase):
    def test_nonzero_two_family_native_root_preserves_shared_reference(self):
        configured=os.environ.get('PHASEA_TEST_V4_NONZERO_ROOT')
        if not configured:self.skipTest('frozen two-family v4 proof was not supplied')
        root=Path(configured)
        value=archive.read(root,root.parent,
            '350ae387db810e496d38ccee821f0c2bbbd38cf2e366a9bd4a956d7ecfe83b7d',
            '5bab3eb7ba54636b15d7262c86777adfc6acdc332d3c4311dff640ac13ee8ce0')
        group=value['covariance'][0]
        self.assertEqual(group['valid_mask'],[True]*3)
        self.assertEqual({family['tune_id'] for family in
            group['independent_families']},{'JUNCTIONS','MONASH'})
        self.assertTrue(all(p.number(point['variance'])>0
            for point in value['points']))
        def covariance(i,j):
            return .9*sum(sum((p.number(row[i])-p.number(
                family['leave_mean'][i]))*(p.number(row[j])-p.number(
                family['leave_mean'][j])) for row in family['complements'])
                for family in group['independent_families']
                if family['usable_mask'][i] and family['usable_mask'][j])
        self.assertEqual(covariance(0,1),0.)
        self.assertNotEqual(covariance(0,2),0.)
        self.assertNotEqual(covariance(1,2),0.)
        for index,point in enumerate(value['points']):
            self.assertAlmostEqual(covariance(index,index),
                                   p.number(point['variance']),places=14)
        forged=copy.deepcopy(value)
        forged['points'][2]['variance']=(1.).hex()
        forged['points'][2]['standard_error']=(1.).hex()
        forged['science_content_sha256']=p.digest({k:forged[k] for k in (
            'scientific_request_sha256','resolved','points','covariance',
            'materialization','event_moment_receipts',
            'support_diagnostic_receipts','class_boundary_deletions')})
        with self.assertRaisesRegex(ValueError,'factor diagonal differs'):
            p.ProjectionResult.from_dict(forged,cold=True)

    def test_authenticated_dzero_admission_receipt_matches_native_request(self):
        configured=os.environ.get('PHASEA_TEST_COLLECTION_DIR')
        if not configured or Path(configured).name!='v22-d0-fixture':
            self.skipTest('frozen v2.2 D0 TEST_ONLY collection was not supplied')
        from pipeline.query import collection
        base=Path(configured)
        source=native_runner.n.NativeCollection(base/'index.json',
            '2cf84dc3d839139bd5d0501ea1c9861af0510d7fab19adb38b1056963b017c03',
            collection)
        receipt=native_v4.admission_closure(source,
            base/'expected-sources.json',
            '29bc0d6645baa8701a4f22a52f181484f17416a1a2496fdbbbb881d9956e1b54')
        self.assertEqual(receipt['qualification'],'TEST_ONLY_DOMAIN_CLOSED')
        self.assertEqual((receipt['source_count'],receipt['event_count']),(30,90))
        self.assertEqual(receipt, json.loads((base/
            'ADMISSION_CLOSURE_TEST_ONLY.json').read_text()))
        native_run=os.environ.get('PHASEA_TEST_NATIVE_RUN_DIR')
        if native_run:
            request=json.loads(Path(json.loads((Path(native_run)/
                'receipt.json').read_text())['request_path']).read_text())
            natural=sorted([[m['source_id'],m['tune_id'],m['logical_id'],
                             m['block_id'],m['successful_events']]
                            for m in request['sources']['members']],
                           key=lambda row:row[0])
            self.assertEqual(receipt['natural_members_sha256'],p.digest(natural))

    def test_full_request_refuses_test_only_merged_collection_before_numerics(self):
        configured=os.environ.get('PHASEA_TEST_COLLECTION_DIR')
        native_run=os.environ.get('PHASEA_TEST_NATIVE_RUN_DIR')
        if not configured or not native_run:
            self.skipTest('v2.2 merged TEST_ONLY collection/native request was not supplied')
        base=Path(configured)
        request=json.loads(Path(json.loads((Path(native_run)/'receipt.json').read_text())[
            'request_path']).read_text())
        request['completion']['require_campaign_complete']=True
        request=p.ProjectionRequest.from_dict(request,cold=True)
        index=base/'merged/index.json'
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError,'full paper result requires the authenticated MERGED'):
                native_runner.run_diagnostic(index,p.file_digest(index),
                    ROOT/'config/analysis.json',p.file_digest(ROOT/'config/analysis.json'),
                    request,Path(directory))
            self.assertEqual(list(Path(directory).iterdir()),[])

    def _fixture_v4(self):
        from test_projection_interface import ProjectionInterfaceContract
        fixture=ProjectionInterfaceContract();fixture.setUpClass();fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        request,value,routes=fixture.result_fixture()
        req=request.to_dict()
        req['statistics']['covariance_groups'][0][
            'representation']='DELETE_ONE_FACTORS'
        request=p.ProjectionRequest.from_dict(req)
        req=request.to_dict()
        value['request_echo']=req
        value['request_sha256']=request.request_sha256
        value['scientific_request_sha256']=request.scientific_request_sha256
        for point in value['points']:
            point['semantic_id']=p.semantic_id(request,point['key'])
        group=value['covariance'][0]
        group.update(representation='DELETE_ONE_FACTORS',dense_rows=None,
                     factors_root_object='covariance_factors')
        moments={('MONASH',block):SimpleNamespace(events=20,
            sumw=0.,sumw2=0.,sumabsw=0.) for block in range(1,11)}
        receipts=native_v4.event_moment_receipts(request,moments)
        by_block={row['block_id']:row for row in receipts}
        value['schema']=p.RESULT_SCHEMA_NATIVE
        value['event_moment_receipts']=receipts
        diagnostics=[]
        for receipt in receipts:
            body=dict(schema='hadronization_observed_support_diagnostics_v1',
                tune_id='MONASH',block_id=receipt['block_id'],
                event_moments_sha256=receipt['content_sha256'],
                activity_counts=[dict(activity_bin=0,events=20)],
                n_mpi_counts=[dict(n_mpi=0,events=20)],
                process_counts=[dict(process_code=121,events=20)],
                pthat_sum=(0.).hex(),hard_scale_sum=(0.).hex(),
                natural_final_hadrons=0,natural_final_weighted_sum=(0.).hex(),
                charm_constituents=0,charm_constituent_weighted_sum=(0.).hex(),
                beauty_constituents=0,beauty_constituent_weighted_sum=(0.).hex(),
                strict_selected_final_hadrons=0,
                strict_selected_final_weighted_sum=(0.).hex(),
                origin_pairs=[],closure_terms=[])
            diagnostics.append(dict(body,content_sha256=p.digest(body)))
        value['support_diagnostic_receipts']=diagnostics
        deletions=[]
        for klass in value['resolved']['class_boundaries']:
            klass['boundary_status']='RESOLVED'
            klass['coverage_status']='COMPLETE_K10'
            for omitted in range(11):
                body=dict(tune_id='MONASH',class_id=klass['class_id'],
                    omitted_block=omitted,
                    source_family_digest=p.digest(req['sources']['members']),
                    status='RESOLVED',low=klass['actual_integer_low'],
                    high=klass['actual_integer_high'],empty=klass['empty'],
                    weighted_measure=klass['event_weight'])
                deletions.append(dict(body,content_sha256=p.digest(body)))
        value['class_boundary_deletions']=deletions
        value['resolved']['g9_science']=None
        for point in value['points']:
            for block in point['block_values']:
                moment=by_block[block['block_id']]
                del block['fills'];del block['event_gram_content_digest']
                for field in ('events','sumw','sumw2','sumabsw','event_weight_terms'):
                    block[field]=moment[field]
                block['event_moments_sha256']=moment['content_sha256']
        files=[dict(file_id='shard_0000_'+suffix,role=role,
            shard_ordinal=0,tune_id=None,sha256='a'*64,bytes=1)
            for suffix,role in (('root','QUERY_SHARD_ROOT'),
                ('metadata','SHARD_METADATA'),('manifest','SHARD_MANIFEST'))]
        files.sort(key=lambda row:row['file_id'])
        value['artifact_binding']=dict(kind='QUERY_COLLECTION',
            collection_schema='hadronization_query_collection_v1',
            layout='SHARDED',collection_state='TEST_ONLY',
            collection_index_sha256='a'*64,
            collection_index_bytes=1,
            collection_scientific_identity_sha256=req['bindings'][
                'expected_source_content_sha256'],member_files=files,
            member_files_sha256=p.digest(files),
            pair_proofs=[dict(shard_ordinal=0,
                scientific_binding_sha256='a'*64,proof_sha256='a'*64,
                events=200,candidate_pairs=0)],
            pair_proofs_sha256=p.digest([dict(shard_ordinal=0,
                scientific_binding_sha256='a'*64,proof_sha256='a'*64,
                events=200,candidate_pairs=0)]),
            merged_partitions=[],merged_partitions_sha256=p.digest([]))
        value['admission_closure']=dict(
            schema='hadronization_query_collection_admission_closure_v1',
            qualification='TEST_ONLY_DOMAIN_CLOSED',index_state='TEST_ONLY',
            collection_index_sha256='a'*64,
            collection_scientific_identity_sha256=req['bindings'][
                'expected_source_content_sha256'],
            expected_sources_sha256='a'*64,
            natural_members_sha256=p.digest(sorted([
                [member['source_id'],member['tune_id'],member['logical_id'],
                 member['block_id'],member['successful_events']]
                for member in req['sources']['members']],key=lambda row:row[0])),
            per_tune_source_event_counts=[dict(tune='MONASH',sources=10,events=200)],
            campaign='TEST',campaign_descriptor_sha256=req['sources'][
                'campaign_descriptor_sha256'],
            accepted_manifest_sha256=req['sources']['accepted_manifest_sha256'],
            source_count=10,event_count=200,domain_complete=True,
            work_sha256=None,collector_closure_sha256=None,
            external_pins_sha256=None,acquisition_manifest_sha256=None,
            campaign_sha256=None)
        for group in value['covariance']:
            for family in group['independent_families']:
                family['finite_mask']=[[leaf is not None for leaf in row]
                    for row in family['complements']]
                family['usable_mask']=[group['valid_mask'][slot] and
                    all(row[slot] is not None for row in family['complements'])
                    for slot in range(len(group['valid_mask']))]
            group['numerical_diagnostics'].update(
                method_id='K10_FACTOR_DIAGONAL_CHECK',status='PASS',
                accepted_rounding_bound=p.hex64(1e-12),
                valid_dimension=sum(group['valid_mask']))
            group['content_sha256']=p.digest({k:v for k,v in group.items()
                if k!='content_sha256'})
        provenance=value['provenance']
        del provenance['attempted_events_by_tune']
        provenance['campaign_descriptor_sha256']=req['sources'][
            'campaign_descriptor_sha256']
        provenance['successful_events_by_tune']=req['sources'][
            'expected_events_by_tune']
        provenance['campaign_accounting']=dict(
            schema='hadronization_campaign_accounting_v4',
            scope='ACCEPTED_LEDGER_ONLY_NO_QUERY_CLOSURE',
            input_sha256=dict(campaign='a'*64,raw_manifest='a'*64,
                              attempts='a'*64),campaign_id='TEST',
            counts=dict(accepted_sources=10,attempts=10,accepted_attempts=10,
                discarded_attempts=0,successful_events=200),
            by_tune=[dict(tune_id='MONASH',sources=10,successful_events=200,
                submitted_attempts=10,accepted_attempts=10,
                discarded_attempts=0)],
            by_block=[dict(tune_id='MONASH',block_id=block,sources=1,
                successful_events=20) for block in range(1,11)],
            attempt_evidence=[dict(outcome='accepted',
                evidence_status='TEST_ONLY_LITERAL',count=10)],
            generator_event_trials_by_tune=[dict(tune_id='MONASH',
                scope='ALL_SUBMITTED_CAMPAIGN_ATTEMPTS',count=None,
                status='UNAVAILABLE',reason_codes=[
                    'EVENT_TRIAL_COUNTS_NOT_RECORDED_IN_VERIFIED_INPUTS'])])
        value['science_content_sha256']=p.digest({k:value[k] for k in (
            'scientific_request_sha256','resolved','points','covariance',
            'materialization','event_moment_receipts',
            'support_diagnostic_receipts','class_boundary_deletions')})
        p.ProjectionResult.from_dict(value,request,routes)
        return request,value,routes

    def test_v4_fixture_rejects_legacy_gram_cross_block_and_attempt_status_mutants(self):
        request,value,routes=self._fixture_v4()
        changed=copy.deepcopy(value)
        changed['points'][0]['block_values'][0]['event_moments_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'block/event moment reference'):
            p.ProjectionResult.from_dict(changed,request,routes)
        changed=copy.deepcopy(value)
        changed['event_moment_receipts'].pop(4)
        with self.assertRaisesRegex(ValueError,'moment tune/block domain'):
            p.ProjectionResult.from_dict(changed,request,routes)
        changed=copy.deepcopy(value)
        altered=changed['event_moment_receipts'][0]
        altered['source_members_sha256']='0'*64
        altered['content_sha256']=p.digest({k:v for k,v in altered.items()
            if k!='content_sha256'})
        with self.assertRaisesRegex(ValueError,'moment membership/content/exposure'):
            p.ProjectionResult.from_dict(changed,request,routes)
        changed=copy.deepcopy(value)
        altered=changed['support_diagnostic_receipts'][0]
        altered['pthat_sum']=(1.).hex()
        with self.assertRaisesRegex(ValueError,'support diagnostic moments/content'):
            p.ProjectionResult.from_dict(changed,request,routes)
        changed=copy.deepcopy(value)
        changed['points'][0]['block_values'][0]['event_gram_content_digest']='a'*64
        with self.assertRaisesRegex(ValueError,'exact fields differ'):
            p.ProjectionResult.from_dict(changed,request,routes)
        changed=copy.deepcopy(value)
        changed['artifact_binding']['member_files'].pop(1)
        changed['artifact_binding']['member_files_sha256']=p.digest(
            changed['artifact_binding']['member_files'])
        with self.assertRaisesRegex(ValueError,'shard/partition role domain'):
            p.ProjectionResult.from_dict(changed,request,routes)
        changed=copy.deepcopy(value)
        changed['class_boundary_deletions'].pop(4)
        with self.assertRaisesRegex(ValueError,'class boundary deletion domain'):
            p.ProjectionResult.from_dict(changed,request,routes)
        changed=copy.deepcopy(value)
        trial=changed['provenance']['campaign_accounting'][
            'generator_event_trials_by_tune'][0]
        trial.update(count=0,status='AVAILABLE')
        with self.assertRaisesRegex(ValueError,'event-trial status/value'):
            p.ProjectionResult.from_dict(changed,request,routes)
        trial['reason_codes']=[]
        with self.assertRaisesRegex(ValueError,'coverage evidence is absent'):
            p.ProjectionResult.from_dict(changed,request,routes)

    def test_v4_cold_rejects_full_promotion_and_resealed_factor_mutants(self):
        request,value,routes=self._fixture_v4()
        promoted=copy.deepcopy(value)
        promoted['campaign_state']='FULL_ACCEPTED_CAMPAIGN'
        with self.assertRaisesRegex(ValueError,'TEST_ONLY query collection'):
            p.ProjectionResult.from_dict(promoted,request,routes,cold=True)

        def reseal(payload):
            for group in payload['covariance']:
                group['content_sha256']=p.digest({k:v for k,v in group.items()
                    if k!='content_sha256'})
            payload['science_content_sha256']=p.digest({k:payload[k] for k in (
                'scientific_request_sha256','resolved','points','covariance',
                'materialization','event_moment_receipts',
                'support_diagnostic_receipts','class_boundary_deletions')})

        forged=copy.deepcopy(value)
        point=forged['points'][1]
        point['uncertainty_status']='AVAILABLE'
        point['variance']=(1.).hex()
        point['standard_error']=(1.).hex()
        reseal(forged)
        with self.assertRaisesRegex(ValueError,'factor diagonal differs'):
            p.ProjectionResult.from_dict(forged,request,routes,cold=True)

        forged=copy.deepcopy(value)
        forged['covariance'][0]['independent_families'][0]['leave_mean'][1]=(
            1.).hex()
        reseal(forged)
        with self.assertRaisesRegex(ValueError,'family mean differs'):
            p.ProjectionResult.from_dict(forged,request,routes,cold=True)

        nonzero=copy.deepcopy(value)
        family=nonzero['covariance'][0]['independent_families'][0]
        leaves=[float(i) for i in range(10)]
        mean=sum(leaves)/10
        variance=.9*sum((leaf-mean)**2 for leaf in leaves)
        for block,leaf in enumerate(leaves):
            family['complements'][block][1]=leaf.hex()
        family['leave_mean'][1]=mean.hex()
        nonzero['points'][1]['uncertainty_status']='AVAILABLE'
        nonzero['points'][1]['variance']=variance.hex()
        nonzero['points'][1]['standard_error']=(variance**.5).hex()
        reseal(nonzero)
        p.ProjectionResult.from_dict(nonzero,request,routes,cold=True)
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory)/'nonzero-factor-v4.root'
            written=archive.write(nonzero,output,directory)
            cold=archive.read(output,directory,written['root_sha256'],
                              written['value_sha256'])
            self.assertEqual(p.digest(cold),p.digest(nonzero))

    def test_v4_full_state_requires_exact_site_closure_and_ledger_domain(self):
        request,value,routes=self._fixture_v4()
        # A valid-looking closure still cannot promote a one-tune sharded
        # fixture into the paper's complete merged campaign.
        closed=copy.deepcopy(value)
        closed['artifact_binding']['collection_state']='EXTERNAL_ACCEPTANCE_REQUIRED'
        proof=closed['admission_closure']
        proof.update(index_state='EXTERNAL_ACCEPTANCE_REQUIRED',
            qualification='FULL_ACCEPTED_DOMAIN_CLOSED',
            work_sha256='1'*64,collector_closure_sha256='2'*64,
            external_pins_sha256='3'*64,
            acquisition_manifest_sha256='4'*64,campaign_sha256='5'*64)
        closed['campaign_state']='FULL_ACCEPTED_CAMPAIGN'
        with self.assertRaisesRegex(ValueError,'MERGED 3000-source three-tune domain'):
            p.ProjectionResult.from_dict(closed,request,routes,cold=True)
        for mutation,reason in (
                (lambda x:x['admission_closure'].update(domain_complete=False),
                 'full campaign lacks authenticated admission closure'),
                (lambda x:x['admission_closure'].update(
                    collector_closure_sha256=None),
                 'full campaign lacks authenticated admission closure'),
                (lambda x:x['admission_closure'].update(source_count=9),
                 'admission closure source membership'),
                ):
            mutant=copy.deepcopy(closed)
            mutation(mutant)
            with self.subTest(reason=reason),self.assertRaisesRegex(
                    ValueError,reason):
                p.ProjectionResult.from_dict(mutant,request,routes,cold=True)

    def test_v4_cold_preserves_finite_deletions_when_class_error_is_withheld(self):
        request,value,routes=self._fixture_v4()
        # The existing native reclassification oracle has pooled 9/5 and
        # deletion estimates 1, 20/11 (eight times), 1. Its error is withheld
        # solely because the selected class changes under omission.
        leaves=[1.]+[20/11]*8+[1.]
        value['points'][0]['center']=(9/5).hex()
        family=value['covariance'][0]['independent_families'][0]
        for block,leaf in enumerate(leaves):
            family['complements'][block][0]=leaf.hex()
            family['finite_mask'][block][0]=True
        family['leave_mean'][0]=(sum(leaves)/10).hex()
        self.assertFalse(family['usable_mask'][0])
        self.assertFalse(value['covariance'][0]['valid_mask'][0])
        value['covariance'][0]['content_sha256']=p.digest({k:v for k,v
            in value['covariance'][0].items() if k!='content_sha256'})
        value['science_content_sha256']=p.digest({k:value[k] for k in (
            'scientific_request_sha256','resolved','points','covariance',
            'materialization','event_moment_receipts',
            'support_diagnostic_receipts','class_boundary_deletions')})
        p.ProjectionResult.from_dict(value,request,routes,cold=True)
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory)/'class-unstable-leaves-v4.root'
            receipt=archive.write(value,output,directory)
            cold=archive.read(output,directory,receipt['root_sha256'],
                              receipt['value_sha256'])
            self.assertEqual(cold['points'][0]['center'],(9/5).hex())
            self.assertEqual(cold['points'][0]['uncertainty_status'],
                             'WITHHELD_UNCERTAINTY')
            persisted=cold['covariance'][0]['independent_families'][0]
            self.assertEqual([float.fromhex(row[0]) for row in
                              persisted['complements']],leaves)
            self.assertEqual([row[0] for row in persisted['finite_mask']],
                             [True]*10)
            self.assertFalse(persisted['usable_mask'][0])

    def test_v4_direct_root_tables_and_typed_dag_survive_cold_reopen(self):
        request,value,routes=self._fixture_v4()
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory)/'numerics-v4.root'
            receipt=archive.write(value,output,directory)
            self.assertEqual(receipt['schema'],
                             'hadronization_self_contained_typed_root_v4')
            self.assertEqual(receipt['direct_tables']['event_moments'],10)
            self.assertEqual(receipt['direct_tables']['block_values'],30)
            cold=archive.read(output,directory,receipt['root_sha256'],
                              receipt['value_sha256'])
            self.assertEqual(p.digest(cold),p.digest(value))
            archive_v4.export(output,receipt['root_sha256'],
                              receipt['value_sha256'],Path(directory)/'exports')
            accounting_csv=(Path(directory)/'exports/accounting.csv').read_text()
            self.assertIn('SELECTED_ACCEPTED_QUERY_SOURCES',accounting_csv)
            self.assertIn('ACCEPTED_LEDGER_ONLY_NO_QUERY_CLOSURE',accounting_csv)
            self.assertIn('UNAVAILABLE',accounting_csv)
            self.assertIn('EVENT_TRIAL_COUNTS_NOT_RECORDED_IN_VERIFIED_INPUTS',
                          accounting_csv)
            accounting_tex=(Path(directory)/'exports/accounting.tex').read_text()
            self.assertIn('selected query',accounting_tex)
            self.assertIn('all submitted attempts',accounting_tex)
            self.assertIn('unavailable',accounting_tex)
            with self.assertRaisesRegex(ValueError,'trusted hash'):
                archive.read(output,directory,'0'*64,receipt['value_sha256'])
            import ROOT as root_api
            file=root_api.TFile.Open(str(output),'UPDATE')
            file.Delete('event_moments;*')
            file.Close()
            with self.assertRaisesRegex(ValueError,'exact object domain'):
                archive_v4.read(output,p.file_digest(output),
                                receipt['value_sha256'])

    def test_checked_campaign_ledger_separates_jobs_successes_and_unknown_trials(self):
        report=accounting.inventory(ROOT/'data/campaign.json',
            'cc2c0593d8b48103560bed7ba46fa7f81a8137bae24994c6ef2316dd9265005d',
            ROOT/'data/raw_manifest.jsonl',
            '5f354cbc9e0bdfb7ead07adb341d74e4c98f14709d873f8f247585912e2df247',
            ROOT/'data/attempts.csv',
            'c550fffb652d0ff71945ee128cfc8fe475d9b1d64433454e9073fd2076c5d8d9')
        result=native_v4.campaign_accounting(report)
        self.assertEqual([(row['tune_id'],row['submitted_attempts'],
            row['accepted_attempts'],row['discarded_attempts'])
            for row in result['by_tune']],
            [('MONASH',1000,1000,0),('JUNCTIONS',1063,1000,63),
             ('CLOSEPACKING',1064,1000,64)])
        self.assertEqual(result['counts']['successful_events'],300000000)
        self.assertTrue(all(row['count'] is None and row['status']=='UNAVAILABLE'
            and row['scope']=='ALL_SUBMITTED_CAMPAIGN_ATTEMPTS'
            for row in result['generator_event_trials_by_tune']))

    def test_moment_receipts_bind_original_member_domain_and_signed_weights(self):
        from test_projection_interface import ProjectionInterfaceContract
        fixture=ProjectionInterfaceContract();fixture.setUpClass();fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        request=fixture.request()
        moments={('MONASH',block):SimpleNamespace(events=20,
            sumw=-2. if block==1 else 0.,sumw2=4.,sumabsw=2.)
            for block in range(1,11)}
        receipts=native_v4.event_moment_receipts(request,moments)
        self.assertEqual(len(receipts),10)
        self.assertEqual(receipts[0]['sumw'],(-2.).hex())
        self.assertEqual(receipts[1]['sumw'],(0.).hex())
        self.assertEqual(receipts[0]['content_sha256'],p.digest({k:v for k,v
            in receipts[0].items() if k!='content_sha256'}))
        del moments['MONASH',5]
        with self.assertRaisesRegex(ValueError,'tune/block domain differs'):
            native_v4.event_moment_receipts(request,moments)

    def test_authenticated_fixture_collection_has_exact_shard_and_partition_files(self):
        configured=os.environ.get('PHASEA_TEST_COLLECTION_DIR')
        if not configured:self.skipTest('external TEST_ONLY collection was not supplied')
        api=native_runner._load('v4_fixture_collection','pipeline/query/collection.py')
        base=Path(configured)
        bindings=[]
        for folder,layout,count in ((base,'SHARDED',9),
                                    (base/'merged','MERGED',12)):
            index=folder/'index.json'
            source=native_runner.n.NativeCollection(index,p.file_digest(index),api)
            binding=native_v4.collection_binding(source)
            bindings.append(binding)
            self.assertEqual((binding['layout'],len(binding['member_files'])),
                             (layout,count))
            self.assertEqual(binding['collection_index_bytes'],index.stat().st_size)
            self.assertEqual(binding['member_files_sha256'],
                             p.digest(binding['member_files']))
            changed=copy.deepcopy(binding)
            changed['member_files'].pop(1)
            self.assertNotEqual(changed['member_files_sha256'],
                                p.digest(changed['member_files']))
        self.assertEqual(bindings[0]['collection_scientific_identity_sha256'],
                         bindings[1]['collection_scientific_identity_sha256'])
        self.assertNotEqual(bindings[0]['collection_index_sha256'],
                            bindings[1]['collection_index_sha256'])

    def test_v4_sharded_merged_native_result_science_and_k10_are_identical(self):
        configured=os.environ.get('PHASEA_TEST_COLLECTION_DIR')
        native_run=os.environ.get('PHASEA_TEST_NATIVE_RUN_DIR')
        if not configured or not native_run:
            self.skipTest('external TEST_ONLY collection/native run was not supplied')
        base=Path(configured)
        sharded=json.loads((Path(native_run)/'receipt.json').read_text())
        request=p.ProjectionRequest.from_dict(json.loads(Path(
            sharded['request_path']).read_text()),cold=True)
        analysis_path=ROOT/'config/analysis.json'
        analysis=json.loads(analysis_path.read_text())
        api=native_runner._load('v4_parity_collection',
                                'pipeline/query/collection.py')
        sources=[]
        for index in (base/'index.json',base/'merged/index.json'):
            sources.append(native_runner.n.NativeCollection(
                index,p.file_digest(index),api))
        bindings=[native_v4.collection_binding(source) for source in sources]
        self.assertEqual([(item['layout'],len(item['member_files']))
                          for item in bindings],[('SHARDED',9),('MERGED',12)])
        self.assertNotEqual(bindings[0]['collection_index_sha256'],
                            bindings[1]['collection_index_sha256'])
        self.assertEqual(bindings[0]['collection_scientific_identity_sha256'],
                         bindings[1]['collection_scientific_identity_sha256'])
        self.assertEqual(sources[0].source_lineage(
            request.to_dict()['scope']['ordered_tunes'])['source_selection'],
            sources[1].source_lineage(
            request.to_dict()['scope']['ordered_tunes'])['source_selection'])
        with tempfile.TemporaryDirectory() as directory:
            merged=native_runner.run_diagnostic(base/'merged/index.json',
                bindings[1]['collection_index_sha256'],analysis_path,
                p.file_digest(analysis_path),request,Path(directory))
            for field in ('request_sha256','scientific_request_sha256',
                          'diagnostic_sha256','block_primitive_sha256',
                          'denominator_sha256'):
                self.assertEqual(sharded[field],merged[field],field)
            def science(run):
                moments={(row['tune_id'],row['block_id']):SimpleNamespace(
                    events=row['events'],sumw=float.fromhex(row['sumw']),
                    sumw2=float.fromhex(row['sumw2']),
                    sumabsw=float.fromhex(row['sumabsw']),
                    activity_counts=dict(row['activity_counts']))
                    for row in run['event_block_moments']}
                return native_v4_result.from_verified_diagnostic(
                    request,run,moments,None,None,None,None,analysis,
                    science_only=True)
            left,right=science(sharded),science(merged)
            key=lambda point:p.canonical(point['key'])
            point_view=lambda value:{key(point):point for point in value['points']}
            self.assertEqual(point_view(left),point_view(right))
            self.assertEqual(len(point_view(left)),len(request.expected_point_keys))
            def factors(value):
                result={}
                for group in value['covariance']:
                    keys=[p.canonical(item) for item in group['ordered_point_keys']]
                    result[group['id']]=dict(
                        mask=dict(zip(keys,group['valid_mask'])),
                        families={(family['tune_id'],family['source_family_digest']):
                            dict(leave_mean=dict(zip(keys,family['leave_mean'])),
                                 complements={block:dict(zip(keys,leaves))
                                     for block,leaves in zip(family['block_ids'],
                                                             family['complements'])})
                            for family in group['independent_families']})
                return result
            self.assertEqual(factors(left),factors(right))
            for field in ('event_moment_receipts',
                          'support_diagnostic_receipts',
                          'class_boundaries','class_boundary_deletions',
                          'materialization'):
                self.assertEqual(left[field],right[field],field)
            self.assertEqual(left['covariance'],right['covariance'])
            self.assertEqual(p.digest(left),p.digest(right))
            bounded_root=os.environ.get('PHASEA_TEST_V4_BOUNDED_ROOT')
            if bounded_root:
                root_sha=os.environ['PHASEA_TEST_V4_BOUNDED_ROOT_SHA256']
                value_sha=os.environ['PHASEA_TEST_V4_BOUNDED_VALUE_SHA256']
                saved=archive.read(Path(bounded_root),directory,
                    root_sha,value_sha)
                self.assertEqual(saved['request_sha256'],request.request_sha256)
                full=[]
                for source,binding,run in zip(sources,bindings,
                                              (sharded,merged)):
                    definitions,routes=native_v4.primitive_routes(
                        source,request,analysis)
                    self.assertEqual(definitions,saved['provenance'][
                        'source_selection_definitions'])
                    moments={(row['tune_id'],row['block_id']):SimpleNamespace(
                        events=row['events'],sumw=float.fromhex(row['sumw']),
                        sumw2=float.fromhex(row['sumw2']),
                        sumabsw=float.fromhex(row['sumabsw']),
                        activity_counts=dict(row['activity_counts']))
                        for row in run['event_block_moments']}
                    dto=native_v4_result.from_verified_diagnostic(request,
                        run,moments,binding,saved['provenance'],routes,
                        saved['capability_receipt'],analysis,
                        campaign_state='PARTIAL_SAMPLE',
                        admission_closure=native_v4.admission_closure(source,
                            base/'expected-sources.json',p.file_digest(
                                base/'expected-sources.json')))
                    full.append(dto.to_dict())
                self.assertEqual(full[0],saved)
                self.assertNotEqual(full[0]['artifact_binding'],
                                    full[1]['artifact_binding'])
                self.assertNotEqual(full[0]['primitive_routes'],
                                    full[1]['primitive_routes'])
                self.assertEqual(full[0]['science_content_sha256'],
                                 full[1]['science_content_sha256'])
                self.assertEqual(full[0]['points'],full[1]['points'])
                self.assertEqual(full[0]['covariance'],full[1]['covariance'])

    def test_native_bounded_science_assembly_preserves_cpp_values_without_provenance(self):
        configured=os.environ.get('PHASEA_TEST_NATIVE_RUN_DIR')
        if not configured:self.skipTest('external native TEST_ONLY run was not supplied')
        base=Path(configured)
        run=json.loads((base/'receipt.json').read_text())
        request=p.ProjectionRequest.from_dict(json.loads(Path(
            run['request_path']).read_text()),cold=True)
        moments={(row['tune_id'],row['block_id']):SimpleNamespace(
            events=row['events'],sumw=float.fromhex(row['sumw']),
            sumw2=float.fromhex(row['sumw2']),
            sumabsw=float.fromhex(row['sumabsw']),
            activity_counts=dict(row['activity_counts']))
            for row in run['event_block_moments']}
        analysis=json.loads((ROOT/'config/analysis.json').read_text())
        science=native_v4_result.from_verified_diagnostic(request,run,moments,
            None,None,None,None,analysis,science_only=True)
        self.assertEqual(len(science['points']),len(request.expected_point_keys))
        self.assertEqual(len(science['class_boundary_deletions']),
            len(request.to_dict()['scope']['ordered_tunes'])*
            len(request.to_dict()['classes'])*11)
        self.assertEqual(len(science['event_moment_receipts']),len(moments))
        first=next(line.split('\t') for line in Path(
            run['diagnostic_path']).read_text().splitlines()
            if line.startswith('R\t'))
        self.assertEqual(science['points'][0]['center'],
                         None if first[3]=='-' else float.fromhex(first[3]).hex())
        curve=science['points'][0]['key']['curve']
        self.assertEqual(len(science['points'][0]['block_values']),
                         10*(1+(curve['reference_tune_id'] is not None)))
        self.assertEqual({row['status'] for row in science[
            'class_boundary_deletions']}-{'RESOLVED','UNRESOLVED'},set())


if __name__=='__main__':unittest.main()
