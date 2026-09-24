"""Native numerical scan contracts independent of compact plot storage."""
from dataclasses import dataclass
import bisect
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from helpers import ROOT


_COLLECTION_PINS={
    'v22-d0-fixture':(
        '2cf84dc3d839139bd5d0501ea1c9861af0510d7fab19adb38b1056963b017c03',
        '379a19c32af3e5764c58ce9b5891e7ff49d8df5fdb9107cd5e6547f1f0f165c1')}


def fixture_index_pin(base,merged=False):
    """Independently frozen pins; a new fixture cannot silently inherit one."""
    if base.name not in _COLLECTION_PINS:
        raise ValueError('unrecognized authenticated TEST_ONLY collection')
    return _COLLECTION_PINS[base.name][int(merged)]


def native_module():
    spec = importlib.util.spec_from_file_location(
        'statistics_native_contract', ROOT / 'pipeline/reduce/native.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FakeAxis:
    def __init__(self, name, edges, labels=None):
        self.name, self.edges, self.labels = name, edges, labels or {}

    def GetName(self): return self.name
    def GetNbins(self): return len(self.edges)-1
    def GetBinLabel(self, coordinate): return self.labels.get(coordinate, '')
    def GetBinCenter(self, coordinate):
        return (self.edges[coordinate-1]+self.edges[coordinate])/2
    def GetBinLowEdge(self, coordinate): return self.edges[coordinate-1]
    def GetBinUpEdge(self, coordinate): return self.edges[coordinate]


@dataclass
class FakeCell:
    tune: str
    block: int
    coordinates: tuple
    value: float
    sumw2: float


class FakeSource:
    def __init__(self, cells, axes):
        self.index = {'tune_ordinals': {'MONASH': 0}}
        self.cells, self.axes = cells, axes

    def scan(self, families, tunes, consume, inspect_axes=None):
        assert families == ('kinematics',)
        if inspect_axes is not None:
            inspect_axes('kinematics',self.axes)
        for cell in self.cells:
            consume(cell, self.axes)
        return len(self.cells)


class NativeStatisticsContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.n = native_module()

    def test_native_admission_rejects_legacy_pair_proof_free_query_shard(self):
        with tempfile.TemporaryDirectory() as temporary:
            base=Path(temporary)
            (base/'analysis.json').write_text(json.dumps({'version':'2.1.0'}))
            (base/'metadata.json').write_text(json.dumps({
                'analysis_sha256':'a'*64,'scientific_binding_sha256':'b'*64}))
            index={'analysis_sha256':'a'*64,'tune_ordinals':{'MONASH':0},
                   'sources':[], 'shards':[{'ordinal':0,'metadata':{'path':str(
                       base/'metadata.json')},'workspace_manifest':{'path':str(
                       base/'manifest.json')},'members':[]}]}
            api=SimpleNamespace(read=lambda *_args,**_kwargs:index)
            with self.assertRaisesRegex(ValueError,'mandatory pair-population proof'):
                self.n.NativeCollection(base/'index.json','a'*64,api)


    def test_no_floor_g9_includes_both_sides_of_point15_and_overflow(self):
        n = self.n
        axes = (FakeAxis('tune', [0, 1]), FakeAxis('block', [0, 1]),
                FakeAxis('pdg', [0, 1], {1: '521'}),
                FakeAxis('pt', [0, .15, .5, 7000]),
                FakeAxis('eta', [-4, 4]), FakeAxis('phi', [-3, 3]))
        cells = [FakeCell('MONASH', 1, (1, 1, 1, 1, 1, 1), 2., 4.),
                 FakeCell('MONASH', 1, (1, 1, 1, 2, 1, 1), 4., 10.),
                 FakeCell('MONASH', 1, (1, 1, 1, 4, 1, 1), 3., 9.)]
        result = n.collect_g9(FakeSource(cells, axes), [521],
                              [-4, 4], [-3, 3])
        for axis in ('eta', 'phi'):
            cell = result.cells[('MONASH', 1, 521, axis, 1)]
            self.assertEqual((cell.value, cell.sumw2), (9., 23.))
        self.assertEqual(result.cells[('MONASH', 1, 521, 'pt', 1)].value,6.)
        self.assertEqual(result.cells[('MONASH', 1, 521, 'pt',len(n.G9_PT_EDGES))].value,3.)
        self.assertEqual(n._histogram_bin(.15, n.G9_PT_EDGES), 1)
        self.assertEqual(n._histogram_bin(7000, n.G9_PT_EDGES),
                         len(n.G9_PT_EDGES)-1)
        self.assertEqual(n._histogram_bin(7000.01, n.G9_PT_EDGES),
                         len(n.G9_PT_EDGES))

    def test_negative_pt_underflow_is_rejected(self):
        n = self.n
        axes = (FakeAxis('tune', [0, 1]), FakeAxis('block', [0, 1]),
                FakeAxis('pdg', [0, 1], {1: '521'}),
                FakeAxis('pt', [0, .15, .5]), FakeAxis('eta', [-4, 4]),
                FakeAxis('phi', [-3, 3]))
        source = FakeSource([FakeCell('MONASH', 1, (1, 1, 1, 0, 1, 1), 1., 1.)], axes)
        with self.assertRaisesRegex(ValueError, 'negative G9 pT underflow'):
            n.collect_g9(source, [521], [-4, 4], [-3, 3])

    def test_no_floor_g9_accepts_non_point15_sparse_edge(self):
        n = self.n
        axes = (FakeAxis('tune', [0, 1]), FakeAxis('block', [0, 1]),
                FakeAxis('pdg', [0, 1], {1: '521'}),
                FakeAxis('pt', [0, .2, .5]), FakeAxis('eta', [-4, 4]),
                FakeAxis('phi', [-3, 3]))
        source = FakeSource([FakeCell('MONASH', 1, (1, 1, 1, 1, 1, 1), 1., 1.)], axes)
        result=n.collect_g9(source, [521], [-4, 4], [-3, 3])
        self.assertEqual(result.cells[('MONASH',1,521,'pt',1)].value,1.)

    def test_g9_configured_species_must_exist_on_physical_sparse_axis(self):
        axes=(FakeAxis('tune',[0,1]),FakeAxis('block',[0,1]),
              FakeAxis('pdg',[0,1],{1:'411'}),
              FakeAxis('pt',[0,.15,.5]),FakeAxis('eta',[-4,4]),
              FakeAxis('phi',[-3,3]))
        with self.assertRaisesRegex(ValueError,'species lacks query axis support'):
            self.n.collect_g9(FakeSource([],axes),[421],[-4,4],[-3,3])

    def test_t1_raw_valence_counts_keep_hidden_heavy_and_bc(self):
        counts=self.n.T1Counts()
        hidden=SimpleNamespace(nc=1,ncbar=1,nb=0,nbbar=0,
                               selected=True,status=83,pt=.15,eta=0.)
        bc=SimpleNamespace(nc=1,ncbar=0,nb=1,nbbar=0,
                           selected=True,status=83,pt=.2,eta=4.)
        counts.add(hidden,2.)
        counts.add(bc,-0.5)
        self.assertEqual((counts.hadrons,counts.charm_constituents,
                          counts.beauty_constituents),(2,3,1))
        self.assertEqual((counts.weighted_hadrons,
                          counts.weighted_charm_constituents,
                          counts.weighted_beauty_constituents),(1.5,3.5,-0.5))
        diagnostics=self.n.RawDiagnostics()
        diagnostics.add_heavy(hidden,2.)
        diagnostics.add_heavy(bc,-0.5)
        self.assertEqual((diagnostics.natural_final_hadrons,
                          diagnostics.charm_constituents,
                          diagnostics.beauty_constituents,
                          diagnostics.strict_selected_final_hadrons),(2,3,1,1))
        self.assertEqual(diagnostics.report()['strict_selected_final_weighted_sum'],
                         (-0.5).hex())

    def test_t1_checks_each_source_range_when_sources_share_tune_block(self):
        n=self.n
        from pipeline.query import collection
        workspace=ROOT/'tests/fixtures/query_multitune/queries/shard-0000'
        metadata=json.loads((workspace/'metadata.json').read_text())
        members=collection._members(metadata)
        members[1]=dict(members[1],block=members[0]['block'])
        source=SimpleNamespace(index={'tune_ordinals':{'MONASH':0},
            'shards':[{'members':members,'query_root':{'path':str(workspace/'query.root')}}]})
        counts,exposure,opened,moments,diagnostics=n.collect_t1(source,
            ['MONASH'],event_activity_field='a15_eta4',include_diagnostics=True)
        self.assertEqual(opened,1)
        self.assertEqual(sum(exposure.values()),30)
        self.assertEqual(exposure['MONASH',members[0]['block']],6)
        self.assertEqual(moments['MONASH',members[0]['block']].events,6)
        self.assertEqual(sum(value.hadrons for value in counts.values()),190)
        self.assertEqual(sum(row.natural_final_hadrons for row in diagnostics.values()),190)
        members[1]=dict(members[1],events=4)
        with self.assertRaisesRegex(ValueError,'source range differs'):
            n.collect_t1(source,['MONASH'],event_activity_field='a15_eta4',
                         include_diagnostics=True)

    def test_all_selected_pair_proof_includes_neutral_sigma_and_primed_xis(self):
        import ROOT as R
        from array import array
        analysis = json.loads((ROOT/'config/analysis.json').read_text())
        registry = analysis['pair_query_registry']['associate_pdgs']
        # Construct exact retained rows independently of query/reduction code.
        particles = [(521, 0, -1), (5212, 0, 1), (-5212, 0, -1),
                     (5312, 0, 1), (-5312, 0, -1), (5322, 0, 1),
                     (-5322, 0, -1), (541, 1, -1), (421, 1, 0),
                     (-4312, -1, 0), (-4322, -1, 0)]
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            for mutant in ('valid', 'missing', 'duplicate', 'wrong_sign', 'wrong_pt'):
                with self.subTest(mutant=mutant):
                    root = base/(mutant+'.root')
                    file = R.TFile(str(root), 'RECREATE')
                    def tree(name, fields, rows):
                        out = R.TTree(name, name)
                        arrays = {key: array(code, [0]) for key, code, leaf in fields}
                        for key, code, leaf in fields:
                            out.Branch(key, arrays[key], key+'/'+leaf)
                        for row in rows:
                            for key, code, leaf in fields:
                                arrays[key][0] = row.get(key, 0)
                            out.Fill()
                        out.Write()
                    event_field = [('event_id','Q','l')]
                    tree('events', event_field + [(key,'d','D') for key in
                        ('weight','pthat','hard_scale')] + [(key,'i','I') for key in
                        ('a15_eta1','a15_eta4','process_code','n_mpi')],
                        [dict(event_id=i,weight=1,pthat=2,hard_scale=2,a15_eta1=1,a15_eta4=1)
                         for i in range(3)])
                    heavy=[]
                    for event, chosen in ((0,particles),(1,particles[:1]),(2,particles[:2])):
                        for index,(pdg,qc,qb) in enumerate(chosen):
                            heavy.append(dict(event_id=event,heavy_index=index,pdg=pdg,
                                qc=qc,qb=qb,nc=max(qc,0),ncbar=max(-qc,0),
                                nb=max(qb,0),nbbar=max(-qb,0),status=83,final=1,selected=1,
                                pair_eligible=int(abs(pdg) not in (5212,5312,5322)),
                                pt=2 if index in (0,8) else .2,
                                eta=5 if event==2 and index==1 else 0,phi=0))
                    tree('heavy',event_field+[(key,'i','I') for key in
                        ('heavy_index','pdg','qc','qb','nc','ncbar','nb','nbbar','status')]+
                        [(key,'B','b') for key in ('final','selected','pair_eligible')]+
                        [(key,'d','D') for key in ('pt','eta','phi')],heavy)
                    triggers=[dict(event_id=event,heavy_index=0,sector=5,rejection_mask=0)
                              for event in range(3)]
                    triggers.insert(1,dict(event_id=0,heavy_index=8,sector=4,rejection_mask=0))
                    tree('triggers',event_field+[(key,'i','I') for key in ('heavy_index','sector')]+
                         [('rejection_mask','I','i')],triggers)
                    pair_rows=[]
                    for trigger,indices in ((0,range(1,8)),(8,(9,10))):
                        for associate in indices:
                            a=heavy[associate];t=heavy[trigger]
                            pair_rows.append(dict(event_id=0,trigger_heavy_index=trigger,
                                associate_heavy_index=associate,associate_origin=2,
                                associate_category=0,sign=-1 if
                                (t['qc']*a['qc']+t['qb']*a['qb'])<0 else 1,
                                trigger_pt=t['pt'],associate_pt=a['pt'],dphi=0,deta=0,
                                weight=1,a15_eta1=1,a15_eta4=1))
                    if mutant=='missing': pair_rows.pop(0)
                    if mutant=='duplicate': pair_rows.insert(1,dict(pair_rows[0]))
                    if mutant=='wrong_sign': pair_rows[0]['sign'] *= -1
                    if mutant=='wrong_pt': pair_rows[0]['associate_pt'] += .1
                    tree('pairs',event_field+[(key,'i','I') for key in
                        ('trigger_heavy_index','associate_heavy_index','associate_origin',
                         'associate_category','sign','a15_eta1','a15_eta4')]+
                        [(key,'d','D') for key in
                         ('trigger_pt','associate_pt','dphi','deta','weight')],pair_rows)
                    tree('closure',event_field+[('coefficient','i','I'),
                         ('dense_category','i','I'),('visible','B','b')],[])
                    tree('event_ranges',[('first_id','Q','l'),('count','Q','l'),
                         ('source_id','I','i')],[dict(first_id=0,count=3,source_id=0)])
                    file.Close()
                    source=SimpleNamespace(expected_sha256='a'*64,
                        index={'tune_ordinals':{'MONASH':0},'shards':[{
                            'query_root':{'path':str(root)},'members':[{
                                'tune':'MONASH','block':1,'events':3}]}]})
                    def scan():
                        return self.n.collect_t1(source,['MONASH'],
                            pair_population_registry=registry,work_root=base/mutant)
                    if mutant!='valid':
                        with self.assertRaisesRegex(ValueError,
                                'missing all-selected pair|all-selected pair duplicate/cache/sign'):
                            scan()
                    else:
                        proof=scan()[-1]
                        self.assertEqual(proof['state'],'PASS')
                        self.assertEqual(proof['blocks'],[dict(tune_id='MONASH',block_id=1,
                            events=3,eligible_triggers=4,zero_partner_triggers=2,
                            candidate_pairs=9,stored_pairs=9)])
                        observed={(p['trigger_pdg'],p['associate_pdg'])
                                  for p in proof['species_counts']}
                        self.assertTrue({(521,pdg) for pdg in
                            (5212,-5212,5312,-5312,5322,-5322)} <= observed)
                        self.assertTrue({(421,-4312),(421,-4322)} <= observed)
                        self.assertNotIn((421,541),observed)

    def test_transport_event_exposure_is_bound_to_authenticated_sources(self):
        n = self.n
        members = [{'tune':'MONASH','block':block,'events':3}
                   for block in range(1,11)]
        source = SimpleNamespace(index={'sources':members,'tune_ordinals':['MONASH'],
            'scientific_identity_sha256':'b'*64,'analysis_sha256':'c'*64},
            expected_sha256='a'*64)
        primitives = n.NativePrimitives({}, {}, {}, n.ScanMetrics(),
            ('inclusive',),'a15_eta4',(411,),((411,-411),))
        g9 = n.G9Primitives({},n.ScanMetrics(),(421,))
        expected = {('MONASH',block):3 for block in range(1,11)}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'native.tsv'
            wrong = dict(expected)
            wrong['MONASH',10] = 4
            with self.assertRaisesRegex(ValueError,'differs from authenticated sources'):
                n.write_native_transport(source,primitives,g9,{},wrong,path)
            self.assertFalse(path.exists())
            primitives.activity['JUNCTIONS',1,0] = n.AdditiveCell(1.,1.,1)
            with self.assertRaisesRegex(ValueError,'lacks authenticated source exposure'):
                n.write_native_transport(source,primitives,g9,{},expected,path)
            primitives.activity.clear()
            receipt = n.write_native_transport(source,primitives,g9,{},expected,path)
            self.assertEqual(receipt['path'],str(path))
            self.assertEqual(path.read_text().count('EXPOSURE\tMONASH\t'),10)

    def test_transport_sums_two_distinct_sources_in_each_original_block(self):
        n = self.n
        members = [dict(source_id=source_id, tune='MONASH',
                        logical_id=logical, block=block, events=events)
                   for block in range(1, 11)
                   for source_id, logical, events in ((block-1, block-1, 2),
                                                      (block+9, block+9, 3))]
        self.assertEqual(len(members), 20)
        self.assertEqual(len({row['source_id'] for row in members}), 20)
        source = SimpleNamespace(index={'sources': members,
            'tune_ordinals': {'MONASH': 0},
            'scientific_identity_sha256': 'b'*64,
            'analysis_sha256': 'c'*64}, expected_sha256='a'*64)
        primitives = n.NativePrimitives({}, {}, {}, n.ScanMetrics(),
            ('inclusive',), 'a15_eta4', (411,), ((411, -411),))
        g9 = n.G9Primitives({}, n.ScanMetrics(), (421,))
        expected = {('MONASH', block): 5 for block in range(1, 11)}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'native.tsv'
            n.write_native_transport(source, primitives, g9, {}, expected, path)
            lines = [line for line in path.read_text().splitlines()
                     if line.startswith('EXPOSURE\t')]
            self.assertEqual(lines,
                [f'EXPOSURE\tMONASH\t{block}\t5' for block in range(1, 11)])
            mutants = {}
            mutants['wrong_total'] = dict(expected)
            mutants['wrong_total']['MONASH', 10] = 4
            mutants['missing_block'] = {key: value for key, value in expected.items()
                                        if key != ('MONASH', 10)}
            mutants['extra_block'] = dict(expected)
            mutants['extra_block']['MONASH', 11] = 1
            mutants['zero_scan_count'] = dict(expected)
            mutants['zero_scan_count']['MONASH', 1] = 0
            mutants['float_scan_count'] = dict(expected)
            mutants['float_scan_count']['MONASH', 1] = 5.0
            for name, totals in mutants.items():
                bad_path = Path(directory) / f'{name}.tsv'
                with self.subTest(name=name), self.assertRaisesRegex(
                        ValueError, 'differs from authenticated sources'):
                    n.write_native_transport(source, primitives, g9, {},
                                             totals, bad_path)
                self.assertFalse(bad_path.exists())
            for name, count in (('zero_source', 0), ('float_source', 2.0),
                                ('bool_source', True)):
                bad_members = [dict(row) for row in members]
                bad_members[0]['events'] = count
                bad_source = SimpleNamespace(index=dict(source.index,
                    sources=bad_members), expected_sha256=source.expected_sha256)
                bad_path = Path(directory) / f'{name}.tsv'
                with self.subTest(name=name), self.assertRaisesRegex(
                        ValueError, 'differs from authenticated sources'):
                    n.write_native_transport(bad_source, primitives, g9, {},
                                             expected, bad_path)
                self.assertFalse(bad_path.exists())

    def test_manifest_3000_source_30_group_transport_control(self):
        n = self.n
        from pipeline.query import collection
        manifest_path = ROOT / 'data/raw_manifest.jsonl'
        self.assertEqual(hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
            '5f354cbc9e0bdfb7ead07adb341d74e4c98f14709d873f8f247585912e2df247')
        rows = [json.loads(line) for line in manifest_path.read_text().splitlines()]
        tunes = {'MONASH': 0, 'JUNCTIONS': 1, 'CLOSEPACKING': 2}
        members = [dict(source_id=source_id, tune=row['tune'],
                        tune_ordinal=tunes[row['tune']],
                        logical_id=row['logical_id'], block=row['block'],
                        events=row['successful_events'])
                   for source_id, row in enumerate(rows)]
        self.assertEqual(len(members), 3000)
        self.assertEqual(len({row['source_id'] for row in members}), 3000)
        self.assertEqual(len({(row['tune'], row['logical_id']) for row in members}), 3000)
        index = dict(sources=members, shards=[dict(members=members)],
                     tune_ordinals=tunes, block_count=10,
                     scientific_identity_sha256='b'*64,
                     analysis_sha256='c'*64)
        collection._check_members(index, members)
        source = SimpleNamespace(index=index, expected_sha256='a'*64)
        groups = {}
        source_counts = {}
        for row in members:
            key = (row['tune'], row['block'])
            groups[key] = groups.get(key, 0) + row['events']
            source_counts[key] = source_counts.get(key, 0) + 1
        self.assertEqual(len(groups), 30)
        self.assertEqual(set(source_counts.values()), {100})
        self.assertEqual(set(groups.values()), {10_000_000})
        primitives = n.NativePrimitives({}, {}, {}, n.ScanMetrics(),
            ('inclusive',), 'a15_eta4', (411,), ((411, -411),))
        g9 = n.G9Primitives({}, n.ScanMetrics(), (421,))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'manifest-control.tsv'
            n.write_native_transport(source, primitives, g9, {}, groups, path)
            exposures = [line for line in path.read_text().splitlines()
                         if line.startswith('EXPOSURE\t')]
            self.assertEqual(len(exposures), 30)
            self.assertEqual(len(set(exposures)), 30)
            parsed = {(parts[1], int(parts[2])): int(parts[3]) for parts in
                      (line.split('\t') for line in exposures)}
            self.assertEqual(parsed, groups)
            wrong = dict(groups)
            wrong['CLOSEPACKING', 10] -= 1
            refused = Path(directory) / 'wrong-total.tsv'
            with self.assertRaisesRegex(ValueError,
                    'differs from authenticated sources'):
                n.write_native_transport(source, primitives, g9, {}, wrong,
                                         refused)
            self.assertFalse(refused.exists())
        duplicate = [dict(row) for row in members]
        duplicate[1]['source_id'] = duplicate[0]['source_id']
        with self.assertRaisesRegex(ValueError, 'duplicate global'):
            collection._check_members(dict(index, sources=duplicate,
                shards=[dict(members=duplicate)]), duplicate)
        missing = members[:-1]
        with self.assertRaisesRegex(ValueError, 'membership'):
            collection._check_members(dict(index, sources=missing,
                shards=[dict(members=missing)]), members)


class AuthenticatedNativeLayoutParity(unittest.TestCase):
    """Optional, independently admitted A TEST_ONLY collection integration."""
    def test_direct_A_lineage_builds_full_natural_paper_request(self):
        configured=os.environ.get('PHASEA_TEST_COLLECTION_DIR')
        if not configured:
            self.skipTest('external TEST_ONLY collection was not supplied')
        from pipeline.query import collection
        from pipeline.reduce import native,projection
        base=Path(configured)
        source=native.NativeCollection(base/'index.json',
            fixture_index_pin(base),
            collection)
        t1,_,_=native.collect_t1(source,['MONASH'])
        species=sorted({key[2] for key in t1})
        analysis_path=ROOT/'config/analysis.json'
        analysis=json.loads(analysis_path.read_text())
        charm_meson=421
        selection=dict(profile_id='inclusive',
            activity_id=analysis['activities'][0]['id'],reference_tune='MONASH',
            trigger_pdgs=[charm_meson,4122,521,5122],
            baryon_meson_trigger_pdgs=[charm_meson,521],
            signed_pdgs=[pdg for sector in
                analysis['pair_query_registry']['associate_pdgs'].values()
                for pdg in sector])
        request=projection.make_native_request(source,analysis_path,
            projection.file_digest(analysis_path),['MONASH'],species,selection)
        value=request.to_dict()
        self.assertEqual(len(request.expected_point_keys),9953)
        correlation={
            (key['curve']['trigger_pdg'],key['curve']['associate_pdg'],
             key['curve']['component'])
            for key in request.expected_point_keys
            if key['curve']['role_id'].startswith('correlations.') and
               key['curve']['quantity']=='dphi_density_per_trigger'}
        for trigger in (421,4122,521,5122):
            for sign in ('OS','SS'):
                self.assertIn((trigger,None,sign),correlation)
        for trigger in (4122,5122):
            for sign in ('OS','SS'):
                self.assertIn((trigger,-trigger,sign),correlation)
        dplus_selection=dict(selection,trigger_pdgs=[411,4122,521,5122],
                             baryon_meson_trigger_pdgs=[411,521])
        dplus=projection.make_native_request(source,analysis_path,
            projection.file_digest(analysis_path),['MONASH'],species,
            dplus_selection)
        dplus_pairs={(key['curve']['trigger_pdg'],
                      key['curve']['associate_pdg'],key['curve']['component'])
                     for key in dplus.expected_point_keys if
                     key['curve']['role_id']=='correlations.charm' and
                     key['curve']['quantity']=='dphi_density_per_trigger'}
        self.assertIn((411,-411,'OS'),dplus_pairs)
        self.assertIn((411,None,'SS'),dplus_pairs)
        self.assertEqual(value['sources'],source.source_lineage(['MONASH'])[
            'source_selection'])
        self.assertEqual(value['bindings']['expected_source_content_sha256'],
                         source.index['scientific_identity_sha256'])
        self.assertEqual(value['execution']['backend_policy'],'REQUIRE_NATIVE')
        self.assertFalse(value['completion']['require_campaign_complete'])
        self.assertEqual({key['curve']['role_id'] for key in
            request.expected_point_keys},set(projection.PAPER_ROLE_IDS))
        full_t1,_,_=native.collect_t1(source,source.index['tune_ordinals'])
        full_species=sorted({key[2] for key in full_t1})
        full=projection.make_native_request(source,analysis_path,
            projection.file_digest(analysis_path),source.index['tune_ordinals'],
            full_species,selection)
        self.assertEqual(len(full.expected_point_keys),45899)
        curves={projection.canonical(key['curve']) for key in full.expected_point_keys}
        def present(curve):return projection.canonical(curve) in curves
        for key in full.expected_point_keys:
            curve=key['curve']
            if curve['role_id'] in ('correlations.charm','correlations.beauty') and \
                    curve['tune_id']!='MONASH' and curve['quantity']=='dphi_density_per_trigger':
                comparison=dict(curve,quantity='ratio_to_reference_tune',
                                reference_tune_id='MONASH')
                self.assertTrue(present(comparison))
        beauty={key['curve']['trigger_pdg']:set() for key in full.expected_point_keys
            if key['curve']['role_id']=='balancing.integrated.beauty'}
        for key in full.expected_point_keys:
            curve=key['curve']
            if curve['role_id']=='balancing.integrated.beauty' and \
                    curve['tune_id']=='MONASH' and curve['reference_tune_id'] is None:
                beauty[curve['trigger_pdg']].add(curve['associate_pdg'])
        self.assertEqual(beauty,{trigger:set(associates) for trigger,associates in
            projection.PAPER_BEAUTY_ASSOCIATES.items()})
        p8={key['curve']['class_id'] for key in full.expected_point_keys
            if key['curve']['role_id']=='balancing.baryon_meson.activity' and
            key['curve']['tune_id']=='MONASH'}
        self.assertEqual(p8,set(range(1,12)))
        g9={key['bins'][0]['index'] for key in full.expected_point_keys
            if key['curve']['role_id']=='spectra.signed_heavy' and
            key['curve']['tune_id']=='MONASH' and
            key['curve']['axis_id']=='pt'}
        self.assertNotIn(-1,g9)
        self.assertIn(len(projection.G9_PT_EDGES)-1,g9)
        observed_t1={key['curve']['associate_pdg'] for key in
            full.expected_point_keys if key['curve']['role_id']==
            'accounting.natural_final_heavy'}
        self.assertEqual(observed_t1,set(full_species))

    def test_checked_A_lineage_preserves_legacy_and_true_digest_roles(self):
        configured = os.environ.get('PHASEA_TEST_COLLECTION_DIR')
        if not configured:
            self.skipTest('external TEST_ONLY collection was not supplied')
        base = Path(configured)
        native = native_module()
        spec = importlib.util.spec_from_file_location(
            'statistics_lineage_collection_reader', ROOT / 'pipeline/query/collection.py')
        collection = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = collection
        spec.loader.exec_module(collection)
        results = []
        for relative, sha in (
                ('index.json',fixture_index_pin(base)),
                ('merged/index.json',fixture_index_pin(base,merged=True))):
            source = native.NativeCollection(base / relative, sha, collection)
            lineage = source.source_lineage()
            self.assertEqual(lineage['collection_index_sha256'],sha)
            self.assertEqual(lineage['collection_state'],'TEST_ONLY')
            self.assertEqual(lineage['source_selection_digest_semantics'],
                             'LEGACY_MANIFEST_ROW_SHA256')
            self.assertEqual(len(lineage['source_selection']['members']),30)
            self.assertEqual(len(lineage['analyzed_source_scientific_content_digests']),30)
            self.assertNotEqual(lineage['source_selection']['members'][0][
                'source_scientific_digest'],
                lineage['analyzed_source_scientific_content_digests'][0][
                    'analyzed_source_scientific_digest'])
            results.append(lineage['source_selection'])
        self.assertEqual(results[0],results[1])
        self.assertEqual(results[0]['selected_members_sha256'],
                         '8c44464379ac179118ad36df21a22764f14959a1b788da066c21ff9128e35427')
        source = native.NativeCollection(base / 'index.json',
            fixture_index_pin(base),
            collection)
        original = source.source_lineage(['MONASH'])
        self.assertEqual(len(original['source_selection']['members']),10)
        changed = dict(original,source_selection_digest_semantics='ANALYZED_CONTENT_SHA256')
        source.api = SimpleNamespace(source_lineage=lambda *_: changed)
        with self.assertRaisesRegex(ValueError,'semantics differs'):
            source.source_lineage(['MONASH'])
        changed = dict(original,collection_scientific_identity_sha256='0'*64)
        source.api = SimpleNamespace(source_lineage=lambda *_: changed)
        with self.assertRaisesRegex(ValueError,'science/semantics differs'):
            source.source_lineage(['MONASH'])
        with self.assertRaisesRegex(ValueError,'trusted SHA-256'):
            native.NativeCollection(base / 'index.json','0'*64,collection)

    def test_direct_event_rows_reproduce_sparse_p1_activity(self):
        configured = os.environ.get('PHASEA_TEST_COLLECTION_DIR')
        if not configured:
            self.skipTest('external TEST_ONLY collection was not supplied')
        import ROOT as root_api
        base = Path(configured)
        native = native_module()
        spec = importlib.util.spec_from_file_location(
            'statistics_p1_collection_reader', ROOT / 'pipeline/query/collection.py')
        collection = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = collection
        spec.loader.exec_module(collection)
        index_sha = fixture_index_pin(base)
        source = native.NativeCollection(base / 'index.json', index_sha, collection)
        sparse = {}
        def consume(cell, axes):
            if cell.family != 'activity':
                return
            names = {axis.GetName(): i for i, axis in enumerate(axes)}
            activity = cell.coordinates[names['a15_eta4']] - 1
            self.assertGreaterEqual(activity, 0)
            key = (cell.tune, cell.block, activity)
            self.assertNotIn(key, sparse)
            sparse[key] = (cell.value, cell.sumw2)
        source.scan(('activity',), source.index['tune_ordinals'], consume)
        rows = {}
        exposure = {}
        for shard in source.index['shards']:
            file = root_api.TFile.Open(shard['query_root']['path'], 'READ')
            self.assertTrue(file and not file.IsZombie())
            try:
                ranges = sorted((int(row.first_id), int(row.first_id)+int(row.count),
                                 shard['members'][int(row.source_id)])
                                for row in file.Get('event_ranges'))
                position = 0
                for row in file.Get('events'):
                    event_id = int(row.event_id)
                    while position < len(ranges) and event_id >= ranges[position][1]:
                        position += 1
                    self.assertLess(position, len(ranges))
                    begin, end, member = ranges[position]
                    self.assertLessEqual(begin, event_id)
                    self.assertLess(event_id, end)
                    activity = int(row.a15_eta4)
                    self.assertGreaterEqual(activity, 0)
                    key = (member['tune'], member['block'], activity)
                    weight = float(row.weight)
                    values = rows.setdefault(key, [0.0, 0.0])
                    values[0] += weight
                    values[1] += weight * weight
                    source_key = key[:2]
                    exposure[source_key] = exposure.get(source_key, 0)+1
            finally:
                file.Close()
        self.assertEqual(set(exposure), source.membership)
        self.assertEqual(sum(exposure.values()), 90)
        self.assertEqual(set(rows), set(sparse))
        for key, (weight, sumw2) in rows.items():
            actual = sparse[key]
            self.assertTrue(math.isclose(weight, actual[0], rel_tol=1e-12,
                                          abs_tol=1e-12), (key, weight, actual))
            self.assertTrue(math.isclose(sumw2, actual[1], rel_tol=1e-12,
                                          abs_tol=1e-12), (key, sumw2, actual))
        _,counted,opened,moments,diagnostics=native.collect_t1(source,
            source.index['tune_ordinals'],event_activity_field='a15_eta4',
            include_diagnostics=True)
        self.assertEqual((opened,counted),(3,exposure))
        self.assertEqual(set(moments),set(exposure))
        for key,moment in moments.items():
            self.assertEqual(moment.events,exposure[key])
            self.assertEqual(sum(moment.activity_counts.values()),moment.events)
            self.assertEqual(sum(moment.n_mpi_counts.values()),moment.events)
            self.assertEqual(sum(moment.process_counts.values()),moment.events)
            self.assertTrue(math.isclose(moment.sumw,
                sum(value[0] for cell,value in rows.items() if cell[:2]==key),
                rel_tol=1e-12,abs_tol=1e-12))
            self.assertTrue(math.isclose(moment.sumw2,
                sum(value[1] for cell,value in rows.items() if cell[:2]==key),
                rel_tol=1e-12,abs_tol=1e-12))
            self.assertGreaterEqual(moment.sumabsw,abs(moment.sumw))
        source_pairs=source_closure=natural=charm=beauty=selected=0
        for shard in source.index['shards']:
            file=root_api.TFile.Open(shard['query_root']['path'],'READ')
            self.assertTrue(file and not file.IsZombie())
            try:
                source_pairs+=int(file.Get('pairs').GetEntries())
                source_closure+=int(file.Get('closure').GetEntries())
                for heavy in file.Get('heavy'):
                    if not (ord(heavy.final) if isinstance(heavy.final,str)
                            else int(heavy.final)):continue
                    natural+=1
                    charm+=int(heavy.nc)+int(heavy.ncbar)
                    beauty+=int(heavy.nb)+int(heavy.nbbar)
                    if ((ord(heavy.selected) if isinstance(heavy.selected,str)
                         else int(heavy.selected)) and 81<=int(heavy.status)<=89
                            and float(heavy.pt)>.15 and abs(float(heavy.eta))<=4.):
                        selected+=1
            finally:file.Close()
        self.assertEqual(sum(value[0] for summary in diagnostics.values()
            for value in summary.origin_pairs.values()),source_pairs)
        self.assertEqual(sum(value[0] for summary in diagnostics.values()
            for value in summary.closure_terms.values()),source_closure)
        self.assertEqual(tuple(sum(getattr(summary,field) for summary in
            diagnostics.values()) for field in ('natural_final_hadrons',
                'charm_constituents','beauty_constituents',
                'strict_selected_final_hadrons')),
            (natural,charm,beauty,selected))

    def test_direct_pair_rows_reproduce_sparse_signed_pair_totals(self):
        configured = os.environ.get('PHASEA_TEST_COLLECTION_DIR')
        if not configured:
            self.skipTest('external TEST_ONLY collection was not supplied')
        import ROOT as root_api
        base = Path(configured)
        native = native_module()
        spec = importlib.util.spec_from_file_location(
            'statistics_pair_collection_reader', ROOT / 'pipeline/query/collection.py')
        collection = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = collection
        spec.loader.exec_module(collection)
        index_sha = fixture_index_pin(base)
        source = native.NativeCollection(base / 'index.json', index_sha, collection)
        sparse = {}
        def consume(cell, axes):
            if cell.family != 'pairs':
                return
            names = {axis.GetName(): i for i, axis in enumerate(axes)}
            coords = cell.coordinates
            trigger = int(axes[names['trigger_pdg']].GetBinLabel(coords[names['trigger_pdg']]))
            associate = int(axes[names['associate_pdg']].GetBinLabel(coords[names['associate_pdg']]))
            if (trigger, associate) != (511, 5212):
                return
            sign = round(axes[names['sign']].GetBinCenter(coords[names['sign']]))
            activity = coords[names['a15_eta4']] - 1
            key = (cell.tune, cell.block, activity, trigger, associate, sign)
            values = sparse.setdefault(key, [0.0, 0.0])
            values[0] += cell.value
            values[1] += cell.sumw2
        source.scan(('pairs',), source.index['tune_ordinals'], consume)
        direct = {}
        for shard in source.index['shards']:
            file = root_api.TFile.Open(shard['query_root']['path'], 'READ')
            self.assertTrue(file and not file.IsZombie())
            try:
                ranges = sorted((int(row.first_id), int(row.first_id)+int(row.count),
                                 shard['members'][int(row.source_id)])
                                for row in file.Get('event_ranges'))
                def heavy_groups():
                    current_id = None
                    current = {}
                    for row in file.Get('heavy'):
                        event_id = int(row.event_id)
                        if current_id is not None and event_id != current_id:
                            yield current_id, current
                            current = {}
                        current_id = event_id
                        current[int(row.heavy_index)] = int(row.pdg)
                    if current_id is not None:
                        yield current_id, current
                groups = iter(heavy_groups())
                heavy_event, heavy_map = next(groups, (None, {}))
                position = 0
                for row in file.Get('pairs'):
                    event_id = int(row.event_id)
                    while heavy_event is not None and heavy_event < event_id:
                        heavy_event, heavy_map = next(groups, (None, {}))
                    self.assertEqual(heavy_event, event_id)
                    trigger = heavy_map[int(row.trigger_heavy_index)]
                    associate = heavy_map[int(row.associate_heavy_index)]
                    if (trigger, associate) != (511, 5212):
                        continue
                    while position < len(ranges) and event_id >= ranges[position][1]:
                        position += 1
                    self.assertLess(position, len(ranges))
                    begin, end, member = ranges[position]
                    self.assertLessEqual(begin, event_id)
                    self.assertLess(event_id, end)
                    key = (member['tune'], member['block'], int(row.a15_eta4),
                           trigger, associate, int(row.sign))
                    values = direct.setdefault(key, [0.0, 0.0])
                    weight = float(row.weight)
                    values[0] += weight
                    values[1] += weight * weight
            finally:
                file.Close()
        self.assertEqual(set(direct), set(sparse))
        self.assertEqual(len(direct), 30)
        for key, expected in direct.items():
            actual = sparse[key]
            self.assertTrue(all(math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-12)
                                for a, b in zip(expected, actual)),
                            (key, expected, actual))

    def test_direct_selected_heavy_rows_reproduce_g9_no_floor_shapes(self):
        configured = os.environ.get('PHASEA_TEST_COLLECTION_DIR')
        if not configured:
            self.skipTest('external TEST_ONLY collection was not supplied')
        import ROOT as root_api
        base = Path(configured)
        native = native_module()
        spec = importlib.util.spec_from_file_location(
            'statistics_g9_collection_reader', ROOT / 'pipeline/query/collection.py')
        collection = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = collection
        spec.loader.exec_module(collection)
        index_sha = fixture_index_pin(base)
        source = native.NativeCollection(base / 'index.json', index_sha, collection)
        analysis = json.loads((ROOT / 'config/analysis.json').read_text())
        def uniform(axis):
            axis = analysis['axes'][axis]
            return tuple(axis['low']+(axis['high']-axis['low'])*i/axis['bins']
                         for i in range(axis['bins']))+(axis['high'],)
        axes = {'pt': native.G9_PT_EDGES, 'eta': uniform('eta'),
                'phi': uniform('phi')}
        species=analysis['g9_species_pdgs']
        self.assertEqual(species,[-5212,-5122,-4122,-521,-421,
                                  421,521,4122,5122,5212])
        sparse = native.collect_g9(source, species, axes['eta'], axes['phi'])
        direct = {}
        def coordinate(value, edges):
            if value < edges[0]:
                return 0
            if value > edges[-1]:
                return len(edges)
            if value == edges[-1]:
                return len(edges)-1
            return bisect.bisect_right(edges, value)
        for shard in source.index['shards']:
            file = root_api.TFile.Open(shard['query_root']['path'], 'READ')
            self.assertTrue(file and not file.IsZombie())
            try:
                ranges = sorted((int(row.first_id), int(row.first_id)+int(row.count),
                                 shard['members'][int(row.source_id)])
                                for row in file.Get('event_ranges'))
                heavy = iter(file.Get('heavy'))
                current = next(heavy, None)
                position = 0
                for event in file.Get('events'):
                    event_id = int(event.event_id)
                    while position < len(ranges) and event_id >= ranges[position][1]:
                        position += 1
                    self.assertLess(position, len(ranges))
                    begin, end, member = ranges[position]
                    self.assertLessEqual(begin, event_id)
                    self.assertLess(event_id, end)
                    while current is not None and int(current.event_id) == event_id:
                        if (int(current.pdg) in species and bool(current.selected) and
                                81 <= int(current.status) <= 89 and
                                float(current.pt) >= 0. and
                                abs(float(current.eta)) <= 4.):
                            for axis in ('pt', 'eta', 'phi'):
                                bin_id = coordinate(float(getattr(current, axis)),
                                                    axes[axis])
                                key = (member['tune'], member['block'], int(current.pdg),
                                       axis, bin_id)
                                values = direct.setdefault(key, [0.0, 0.0])
                                weight = float(event.weight)
                                values[0] += weight
                                values[1] += weight*weight
                        current = next(heavy, None)
                self.assertIsNone(current)
            finally:
                file.Close()
        observed = {key:(value.value,value.sumw2)
                    for key,value in sparse.cells.items()
                    if value.value != 0.0 or value.sumw2 != 0.0}
        self.assertEqual(set(direct), set(observed))
        self.assertTrue(direct)
        for key, expected in direct.items():
            actual = observed[key]
            self.assertTrue(all(math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-12)
                                for a,b in zip(expected,actual)),
                            (key,expected,actual))
        totals={}
        for (tune,block,pdg,axis,_),cell in sparse.cells.items():
            totals[tune,block,pdg,axis]=totals.get((tune,block,pdg,axis),0.)+cell.value
        for tune,block,pdg,axis in totals:
            self.assertAlmostEqual(totals[tune,block,pdg,'pt'],
                                   totals[tune,block,pdg,'eta'])
            self.assertAlmostEqual(totals[tune,block,pdg,'pt'],
                                   totals[tune,block,pdg,'phi'])

    def test_sharded_and_merged_primitives_and_support_are_equivalent(self):
        configured = os.environ.get('PHASEA_TEST_COLLECTION_DIR')
        if not configured:
            self.skipTest('external TEST_ONLY collection was not supplied')
        base = Path(configured)
        native = native_module()
        spec = importlib.util.spec_from_file_location(
            'statistics_collection_reader', ROOT / 'pipeline/query/collection.py')
        collection = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = collection
        spec.loader.exec_module(collection)
        spec = importlib.util.spec_from_file_location(
            'statistics_query_model', ROOT / 'pipeline/query/model.py')
        model = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = model
        spec.loader.exec_module(model)
        analysis = json.loads((ROOT / 'config/analysis.json').read_text())
        snapshots = []
        for relative, sha in (
                ('index.json', fixture_index_pin(base)),
                ('merged/index.json', fixture_index_pin(base,merged=True))):
            source = native.NativeCollection(base / relative, sha, collection)
            primitives = native.collect_primitives(source, model, analysis,
                [p['id'] for p in analysis['profiles']], 'a15_eta4',
                [421,-421,511], [(421,-421),(421,431),(511,5212)])
            def values(mapping):
                return {key:(cell.value,cell.sumw2)
                        for key,cell in mapping.items()}
            counts, events, opened = native.collect_t1(
                source, source.index['tune_ordinals'])
            snapshots.append((values(primitives.activity),
                              values(primitives.triggers),
                              values(primitives.pairs),
                              {key:(value.hadrons,value.charm_constituents,
                                    value.beauty_constituents)
                               for key,value in counts.items()},events))
            self.assertEqual((primitives.metrics.root_opens,
                              primitives.metrics.family_passes,opened),
                             (3,9,3))
            self.assertEqual(sum(value.hadrons for value in counts.values()),570)
            self.assertEqual(sum(events.values()),90)
        for left,right in zip(*snapshots):
            self.assertEqual(set(left),set(right))
            for key in left:
                a,b = left[key],right[key]
                a = a if isinstance(a,tuple) else (a,)
                b = b if isinstance(b,tuple) else (b,)
                self.assertTrue(all(math.isclose(x,y,rel_tol=1e-12,
                                                 abs_tol=1e-12)
                                    for x,y in zip(a,b)),(key,a,b))


if __name__ == '__main__':
    unittest.main()
