"""Bounded native THnSparse scan over A's authenticated collection reader.

This module owns numerical primitive scanning, not collection admission or the
scientific model. The caller supplies A's verified collection API and index SHA.
No compact ROOT source, event graph, or renderer input is read here.
"""
from array import array
from dataclasses import dataclass
from pathlib import Path
import bisect
import hashlib
import json
import math
import os
import shlex
import shutil
import subprocess
import tempfile

G9_PT_EDGES = tuple([i / 2 for i in range(101)] +
                    [60,75,100,150,250,500,1000,2000,4000,7000])


@dataclass(frozen=True)
class SparseCell:
    family: str
    partition: str
    tune: str
    block: int
    coordinates: tuple[int, ...]
    value: float
    sumw2: float


@dataclass
class ScanMetrics:
    root_opens: int = 0
    family_passes: int = 0
    occupied_cells: int = 0
    selected_cells: int = 0
    root_bytes: int = 0


class NativeCollection:
    """Verified logical SHARDED/MERGED collection with one physical scan path."""

    def __init__(self, index_path, expected_sha256, collection_api, *,
                 verify_roots=True, fact_cache=None):
        self.api = collection_api
        self.index_path = Path(index_path).absolute()
        self.fact_cache = {} if fact_cache is None else fact_cache
        self.index = collection_api.read(self.index_path, expected_sha256,
                                         verify_roots=verify_roots,
                                         fact_cache=self.fact_cache)
        self.verify_roots = verify_roots
        self.expected_sha256 = expected_sha256
        self.pair_proofs=[]
        for shard in self.index['shards']:
            metadata=json.loads(Path(shard['metadata']['path']).read_text(encoding='utf-8'))
            proof=metadata.get('pair_population_proof')
            analysis_path=Path(shard['workspace_manifest']['path']).parent/'analysis.json'
            analysis_bytes=analysis_path.read_bytes()
            analysis=json.loads(analysis_bytes)
            fields={'schema','state','scientific_binding_sha256','events',
                    'eligible_triggers','zero_partner_triggers','candidate_pairs',
                    'stored_pairs','by_tune_sector_sign'}
            if (hashlib.sha256(analysis_bytes).hexdigest()!=self.index['analysis_sha256'] or
                    analysis.get('version')!='2.2.0' or
                    metadata.get('analysis_sha256')!=self.index['analysis_sha256'] or
                    type(proof) is not dict or set(proof)!=fields or
                    proof['schema']!='hadronization_pair_population_proof_v1' or
                    proof['state']!='PASS' or
                    proof['scientific_binding_sha256']!=metadata.get(
                        'scientific_binding_sha256') or
                    proof['candidate_pairs']!=proof['stored_pairs'] or
                    proof['zero_partner_triggers']>proof['eligible_triggers'] or
                    proof['events']!=sum(m['events'] for m in shard['members']) or
                    any(type(proof[key]) is not int or proof[key]<0 for key in
                        ('events','eligible_triggers','zero_partner_triggers',
                         'candidate_pairs','stored_pairs'))):
                raise ValueError('A v2.2 mandatory pair-population proof is absent or unbound')
            groups=proof['by_tune_sector_sign']
            if (type(groups) is not list or
                    any(type(row) is not dict or set(row)!=
                        {'tune_ordinal','sector','sign','count'} or
                        any(type(row[key]) is not int for key in row) or
                        row['sign'] not in (-1,1) or row['count']<0
                        for row in groups) or
                    len({(row['tune_ordinal'],row['sector'],row['sign'])
                         for row in groups})!=len(groups) or
                    sum(row['count'] for row in groups)!=proof['candidate_pairs']):
                raise ValueError('A v2.2 pair-population sector/sign proof differs')
            body=json.dumps(proof,sort_keys=True,separators=(',',':'),
                            ensure_ascii=True).encode('ascii')
            self.pair_proofs.append(dict(shard_ordinal=shard['ordinal'],
                scientific_binding_sha256=proof['scientific_binding_sha256'],
                proof_sha256=hashlib.sha256(body).hexdigest(),
                events=proof['events'],candidate_pairs=proof['candidate_pairs']))
        self.ordinal_to_tune = {ordinal: tune for tune, ordinal in
                                self.index['tune_ordinals'].items()}
        self.membership = {(m['tune'], m['block']) for m in self.index['sources']}

    def source_lineage(self, requested_tunes=None):
        """Bind A's checked native parent lineage to this exact collection.

        The v2 member field remains the legacy manifest-row digest. A's true
        analyzed per-source content digests are returned separately; neither
        field may be silently substituted for the other.
        """
        if not callable(getattr(self.api, 'source_lineage', None)):
            raise ValueError('authenticated A source-lineage accessor is absent')
        if self.verify_roots:
            lineage = self.api.source_lineage(
                self.index_path,self.expected_sha256,requested_tunes,
                fact_cache=self.fact_cache)
        else:
            lineage = self.api.source_lineage(
                self.index_path,self.expected_sha256,requested_tunes,
                verify_roots=False,fact_cache=self.fact_cache)
        if (type(lineage) is not dict or set(lineage) != {
                'schema','collection_index_sha256',
                'collection_scientific_identity_sha256','collection_state',
                'structural_registry_sha256','accepted_raw_producer_commit',
                'source_selection_digest_semantics',
                'analyzed_source_scientific_content_digests','source_selection'} or
                lineage['schema'] != 'hadronization_query_collection_source_lineage_v1' or
                lineage['collection_index_sha256'] != self.expected_sha256 or
                lineage['collection_scientific_identity_sha256'] !=
                    self.index['scientific_identity_sha256'] or
                lineage['collection_state'] != self.index['state'] or
                lineage['source_selection_digest_semantics'] !=
                    'LEGACY_MANIFEST_ROW_SHA256'):
            raise ValueError('native lineage schema/index/science/semantics differs')
        selection = lineage['source_selection']
        if type(selection) is not dict or set(selection) != {
                'campaign_id','campaign_descriptor_sha256',
                'accepted_manifest_sha256','accepted_plan_digest',
                'accepted_map_digest','members','selected_members_sha256',
                'expected_events_by_tune','provenance_parent_ids'}:
            raise ValueError('native source selection fields differ')
        members = selection['members']
        member_fields = {'source_id','tune_id','logical_id','accepted_attempt',
                         'block_id','successful_events','source_root_sha256',
                         'source_scientific_digest','receipt_sha256'}
        if (type(members) is not list or
                any(type(member) is not dict or set(member) != member_fields
                    for member in members)):
            raise ValueError('native source members differ')
        selected = (set(self.index['tune_ordinals']) if requested_tunes is None
                    else set(requested_tunes))
        expected = [m for m in self.index['sources'] if m['tune'] in selected]
        if (selection['campaign_id'] != self.index['campaign'] or
                selection['accepted_manifest_sha256'] !=
                    self.index['manifest_sha256'] or
                len(members) != len(expected) or
                [(m['source_id'],m['tune_id'],m['logical_id'],m['block_id'],
                  m['successful_events']) for m in members] !=
                [(m['source_id'],m['tune'],m['logical_id'],m['block'],m['events'])
                 for m in expected] or
                hashlib.sha256(json.dumps(members,sort_keys=True,
                    separators=(',',':'),ensure_ascii=True,
                    allow_nan=False).encode('ascii')).hexdigest() !=
                    selection['selected_members_sha256'] or
                selection['expected_events_by_tune'] != [
                    {'tune_id':tune,'count':sum(m['events'] for m in expected
                                               if m['tune']==tune)}
                    for tune in sorted(selected)]):
            raise ValueError('native source selection/index membership differs')
        contents = lineage['analyzed_source_scientific_content_digests']
        if (type(contents) is not list or len(contents) != len(members) or
                any(type(item) is not dict or set(item) != {
                    'source_id','analyzed_source_scientific_digest'}
                    for item in contents) or
                [(item['source_id']) for item in contents] !=
                    [m['source_id'] for m in members] or
                any(type(item['analyzed_source_scientific_digest']) is not str or
                    len(item['analyzed_source_scientific_digest']) != 64 or
                    any(c not in '0123456789abcdef'
                        for c in item['analyzed_source_scientific_digest'])
                    for item in contents)):
            raise ValueError('native analyzed source-content digest domain differs')
        return lineage

    def scan(self, families, tunes, consume, inspect_axes=None):
        """Call consume(cell, axes) once per selected occupied cell.

        Axes are the live ROOT TAxis objects and only valid during the call.
        Selection may be made by consume without materializing dense planes.
        """
        import ROOT
        ROOT.gROOT.SetBatch(True)
        requested_families = tuple(dict.fromkeys(families))
        requested_tunes = set(tunes)
        if not requested_families or not requested_tunes:
            raise ValueError('native scan requires families and tunes')
        if requested_tunes - set(self.index['tune_ordinals']):
            raise ValueError('native scan requested an absent tune')
        paths = {}
        for family in requested_families:
            for path, admitted_family, partition_tunes in self.api.partitions(self.index, family):
                selected = requested_tunes.intersection(partition_tunes)
                if selected:
                    paths.setdefault(path, []).append((admitted_family,selected))
        metrics = ScanMetrics()
        for path, entries in paths.items():
            file = ROOT.TFile.Open(path, 'READ')
            if not file or file.IsZombie():
                raise ValueError('native collection partition cannot open')
            metrics.root_opens += 1
            metrics.root_bytes += Path(path).stat().st_size
            try:
                for family, allowed_tunes in entries:
                    metrics.family_passes += 1
                    partition = next((p for p in self.index['partitions'] if p['root']['path'] == path), None)
                    for hist in self.api.read_family(file, family, partition):
                        if not hist or not hist.InheritsFrom('THnSparse') or not hist.GetCalculateErrors():
                            raise ValueError('native sparse family/Sumw2 differs')
                        axes = tuple(hist.GetAxis(i) for i in range(hist.GetNdimensions()))
                        if tuple(a.GetName() for a in axes[:2]) != ('tune','block'):
                            raise ValueError('native sparse tune/block axis differs')
                        if inspect_axes is not None:
                            inspect_axes(family,axes)
                        coordinates = array('i', [0]*len(axes))
                        for ordinal in range(hist.GetNbins()):
                            value = float(hist.GetBinContent(ordinal,coordinates))
                            sumw2 = float(hist.GetBinError2(ordinal))
                            metrics.occupied_cells += 1
                            if not math.isfinite(value) or not math.isfinite(sumw2) or sumw2 < 0:
                                raise ValueError('nonfinite native sparse cell/Sumw2')
                            tune = self.ordinal_to_tune.get(coordinates[0]-1)
                            block = coordinates[1]
                            if tune is None or (tune,block) not in self.membership:
                                raise ValueError('native sparse occupied tune/block outside admission')
                            if tune not in allowed_tunes:
                                continue
                            cell = SparseCell(family,path,tune,block,
                                              tuple(coordinates),value,sumw2)
                            consume(cell,axes)
                            metrics.selected_cells += 1
            finally:
                file.Close()
        return metrics

@dataclass
class AdditiveCell:
    value: float = 0.0
    sumw2: float = 0.0
    occupied_inputs: int = 0

    def add(self, sparse_cell):
        self.value += sparse_cell.value
        self.sumw2 += sparse_cell.sumw2
        self.occupied_inputs += 1

    def add_exact(self, weight):
        self.value += weight
        self.sumw2 += weight * weight
        self.occupied_inputs += 1


@dataclass
class NativePrimitives:
    activity: dict
    triggers: dict
    pairs: dict
    metrics: ScanMetrics
    profile_ids: tuple[str, ...]
    activity_field: str
    selected_triggers: tuple[int, ...]
    selected_pairs: tuple[tuple[int,int], ...]


def collect_primitives(source, model, analysis, profile_ids, activity_field,
                       selected_triggers, selected_pairs, selected_tunes=None):
    """Read standard activity/trigger/pair primitives from physical sparsities.

    A's sole model admits the complete source profile list with its actual pT
    edges before any ROOT open. This is a bounded sparse accumulator indexed by
    tune, original block and activity, never a Python event graph.
    """
    edges = analysis['axes']['pt']['edges']
    model.validate_phase_a_profiles(analysis['profiles'], pt_edges=edges)
    profiles = [p for p in analysis['profiles'] if p['id'] in profile_ids]
    if len(profiles) != len(set(profile_ids)):
        raise ValueError('requested profile is absent or duplicated')
    if activity_field not in ('a15_eta4','a15_eta1'):
        raise ValueError('unknown admitted activity axis')
    triggers = set(selected_triggers)
    pairs = set(tuple(pair) for pair in selected_pairs)
    if not triggers or not pairs:
        raise ValueError('native primitive request is empty')
    activity = {}
    trigger_values = {}
    pair_values = {}

    def add(mapping,key,cell):
        mapping.setdefault(key,AdditiveCell()).add(cell)

    def signed(axis,coordinate):
        label = axis.GetBinLabel(coordinate)
        if not label:
            raise ValueError('sparse signed-PDG label is absent')
        return int(label)

    def pt_pass(axis,coordinate,cut):
        if coordinate == 0:
            raise ValueError('negative pT underflow is outside admitted physics')
        if cut is None:
            return True
        if coordinate == axis.GetNbins()+1:
            return True
        return axis.GetBinLowEdge(coordinate) >= cut['value']

    def physical(axis,coordinate):
        return 1 <= coordinate <= axis.GetNbins()

    def consume(cell,axes):
        names = {axis.GetName(): i for i,axis in enumerate(axes)}
        if activity_field not in names:
            raise ValueError('requested activity sparse axis is absent')
        coords = cell.coordinates
        activity_axis = axes[names[activity_field]]
        if not physical(activity_axis,coords[names[activity_field]]):
            raise ValueError('activity sparse coordinate is outside declared integer domain')
        activity_bin = coords[names[activity_field]]-1
        prefix = (cell.tune,cell.block,activity_bin)
        if cell.family == 'activity':
            add(activity,prefix,cell)
            return
        if cell.family == 'triggers':
            trigger = signed(axes[names['trigger_pdg']],coords[names['trigger_pdg']])
            if trigger not in triggers:
                return
            if not physical(axes[names['trigger_eta']],coords[names['trigger_eta']]):
                return
            for profile in profiles:
                if pt_pass(axes[names['trigger_pt']],coords[names['trigger_pt']],profile['trigger_pt']):
                    add(trigger_values,(profile['id'],)+prefix+(trigger,),cell)
            return
        if cell.family == 'pairs':
            trigger = signed(axes[names['trigger_pdg']],coords[names['trigger_pdg']])
            associate = signed(axes[names['associate_pdg']],coords[names['associate_pdg']])
            if (trigger,associate) not in pairs:
                return
            sign = round(axes[names['sign']].GetBinCenter(coords[names['sign']]))
            if sign not in (-1,1):
                raise ValueError('native pair sign coordinate differs')
            if not all(physical(axes[names[role]],coords[names[role]])
                       for role in ('trigger_eta','associate_eta')):
                return
            if not physical(axes[names['dphi']],coords[names['dphi']]):
                raise ValueError('wrapped dphi sparse coordinate is outside regular axis')
            dphi_bin = coords[names['dphi']]-1
            for profile in profiles:
                if (pt_pass(axes[names['trigger_pt']],coords[names['trigger_pt']],profile['trigger_pt']) and
                    pt_pass(axes[names['associate_pt']],coords[names['associate_pt']],profile['associate_pt'])):
                    add(pair_values,(profile['id'],)+prefix+(trigger,associate,sign,dphi_bin),cell)
            return
        raise ValueError('unexpected primitive sparse family')

    tunes=(source.index['tune_ordinals'] if selected_tunes is None
           else selected_tunes)
    metrics = source.scan(('activity','triggers','pairs'),tunes,consume)
    return NativePrimitives(activity,trigger_values,pair_values,metrics,
        tuple(p['id'] for p in profiles),activity_field,
        tuple(sorted(triggers)),tuple(sorted(pairs)))

@dataclass
class T1Counts:
    hadrons: int = 0
    charm_constituents: int = 0
    beauty_constituents: int = 0
    weighted_hadrons: float = 0.0
    weighted_charm_constituents: float = 0.0
    weighted_beauty_constituents: float = 0.0
    _corrections: tuple[float, float, float] = (0.0,0.0,0.0)

    def add(self, row, weight):
        charm = int(row.nc) + int(row.ncbar)
        beauty = int(row.nb) + int(row.nbbar)
        if charm < 0 or beauty < 0 or charm + beauty == 0:
            raise ValueError('natural final heavy row has no valid heavy constituent')
        self.hadrons += 1
        self.charm_constituents += charm
        self.beauty_constituents += beauty
        fields = ('weighted_hadrons','weighted_charm_constituents',
                  'weighted_beauty_constituents')
        corrections = list(self._corrections)
        for i,delta in enumerate((weight,weight*charm,weight*beauty)):
            adjusted = delta - corrections[i]
            new = getattr(self,fields[i]) + adjusted
            corrections[i] = (new - getattr(self,fields[i])) - adjusted
            setattr(self,fields[i],new)
        self._corrections = tuple(corrections)


@dataclass
class EventMoments:
    """Observed, block-local exact-support event accounting."""
    events: int = 0
    sumw: float = 0.0
    sumw2: float = 0.0
    sumabsw: float = 0.0
    activity_counts: dict = None
    n_mpi_counts: dict = None
    process_counts: dict = None
    pthat_sum: float = 0.0
    hard_scale_sum: float = 0.0

    def __post_init__(self):
        self.activity_counts={}
        self.n_mpi_counts={}
        self.process_counts={}

    def add(self,row,weight,activity_field):
        activity=int(getattr(row,activity_field))
        n_mpi=int(row.n_mpi)
        process=int(row.process_code)
        pthat=float(row.pthat)
        hard_scale=float(row.hard_scale)
        if activity<0 or n_mpi<0 or not all(map(math.isfinite,
                (weight,pthat,hard_scale))):
            raise ValueError('native exact event accounting field differs')
        self.events+=1
        self.sumw+=weight
        self.sumw2+=weight*weight
        self.sumabsw+=abs(weight)
        self.activity_counts[activity]=self.activity_counts.get(activity,0)+1
        self.n_mpi_counts[n_mpi]=self.n_mpi_counts.get(n_mpi,0)+1
        self.process_counts[process]=self.process_counts.get(process,0)+1
        self.pthat_sum+=pthat
        self.hard_scale_sum+=hard_scale

    def report(self):
        return dict(events=self.events,sumw=self.sumw.hex(),
            sumw2=self.sumw2.hex(),sumabsw=self.sumabsw.hex(),
            activity_counts=[[key,value] for key,value in
                sorted(self.activity_counts.items())],
            n_mpi_counts=[[key,value] for key,value in
                sorted(self.n_mpi_counts.items())],
            process_counts=[[key,value] for key,value in
                sorted(self.process_counts.items())],
            pthat_sum=self.pthat_sum.hex(),hard_scale_sum=self.hard_scale_sum.hex())


def _root_byte(value):
    return ord(value) if isinstance(value, str) and len(value) == 1 else int(value)


@dataclass
class RawDiagnostics:
    """Observed support-row summaries, retaining original integer categories."""
    origin_pairs: dict = None
    closure_terms: dict = None
    natural_final_hadrons: int = 0
    natural_final_weighted_sum: float = 0.0
    charm_constituents: int = 0
    charm_constituent_weighted_sum: float = 0.0
    beauty_constituents: int = 0
    beauty_constituent_weighted_sum: float = 0.0
    strict_selected_final_hadrons: int = 0
    strict_selected_final_weighted_sum: float = 0.0

    def __post_init__(self):
        self.origin_pairs={}
        self.closure_terms={}

    def add_pair(self,row,event_weight):
        key=(int(row.associate_origin),int(row.associate_category),int(row.sign))
        count,weighted=self.origin_pairs.get(key,(0,0.0))
        self.origin_pairs[key]=(count+1,weighted+event_weight)

    def add_closure(self,row,event_weight):
        key=(int(row.dense_category),int(_root_byte(row.visible)),int(row.coefficient))
        count,weighted=self.closure_terms.get(key,(0,0.0))
        self.closure_terms[key]=(count+1,weighted+event_weight*key[2])

    def add_heavy(self,row,event_weight):
        charm=int(row.nc)+int(row.ncbar)
        beauty=int(row.nb)+int(row.nbbar)
        if charm<0 or beauty<0:
            raise ValueError('T1 negative heavy constituent count')
        self.natural_final_hadrons+=1
        self.natural_final_weighted_sum+=event_weight
        self.charm_constituents+=charm
        self.charm_constituent_weighted_sum+=event_weight*charm
        self.beauty_constituents+=beauty
        self.beauty_constituent_weighted_sum+=event_weight*beauty
        if _root_byte(row.selected) and 81<=int(row.status)<=89 and \
                float(row.pt)>.15 and abs(float(row.eta))<=4.:
            self.strict_selected_final_hadrons+=1
            self.strict_selected_final_weighted_sum+=event_weight

    def report(self):
        return dict(natural_final_hadrons=self.natural_final_hadrons,
                    natural_final_weighted_sum=self.natural_final_weighted_sum.hex(),
                    charm_constituents=self.charm_constituents,
                    charm_constituent_weighted_sum=self.charm_constituent_weighted_sum.hex(),
                    beauty_constituents=self.beauty_constituents,
                    beauty_constituent_weighted_sum=self.beauty_constituent_weighted_sum.hex(),
                    strict_selected_final_hadrons=self.strict_selected_final_hadrons,
                    strict_selected_final_weighted_sum=self.strict_selected_final_weighted_sum.hex(),
                    origin_pairs=[dict(origin=key[0],category=key[1],
                    sign=key[2],rows=value[0],weighted_sum=value[1].hex())
                    for key,value in sorted(self.origin_pairs.items())],
                    closure_terms=[dict(category=key[0],visible=bool(key[1]),
                    coefficient=key[2],rows=value[0],weighted_sum=value[1].hex())
                    for key,value in sorted(self.closure_terms.items())])


def _histogram_bin(value, edges):
    """Return a ROOT-style flow/regular coordinate for a physical value."""
    if not math.isfinite(value):
        raise ValueError('nonfinite exact heavy coordinate')
    if value < edges[0]:
        return 0
    if value > edges[-1]:
        return len(edges)
    if value == edges[-1]:
        return len(edges)-1
    return bisect.bisect_right(edges,value)


def _aligned_sparse_bin(axis, coordinate, edges):
    if coordinate == 0:
        return 0
    if coordinate == axis.GetNbins()+1:
        return len(edges)
    low, high = axis.GetBinLowEdge(coordinate), axis.GetBinUpEdge(coordinate)
    if not low < high:
        raise ValueError('native sparse bin is nonascending')
    first = _histogram_bin(low,edges)
    last = _histogram_bin(math.nextafter(high,-math.inf),edges)
    if first != last or not 1 <= first < len(edges):
        raise ValueError('native sparse bin crosses a requested output boundary')
    return first


def _compile_support_scan(work_root):
    source = Path(__file__).with_name('support_scan.cpp')
    root_config = os.environ.get('ROOT_CONFIG') or shutil.which('root-config')
    compiler = os.environ.get('CXX') or shutil.which('c++')
    if not root_config or not compiler:
        raise ValueError('compiled exact-support reader requires ROOT and C++ compiler')
    work_root = Path(work_root).absolute()
    work_root.mkdir(parents=True, exist_ok=True)
    cflags = shlex.split(subprocess.check_output([root_config, '--cflags'], text=True))
    libraries = shlex.split(subprocess.check_output([root_config, '--libs'], text=True))
    identity = hashlib.sha256(json.dumps([hashlib.sha256(source.read_bytes()).hexdigest(),
        compiler, cflags, libraries], sort_keys=True).encode()).hexdigest()
    binary = work_root / ('support-scan-' + identity[:20])
    if not binary.is_file():
        command = [compiler, *cflags, '-O2', '-Wall', '-Wextra', '-Wpedantic',
            '-Werror', '-ffp-contract=off', str(source), '-o', str(binary), *libraries]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode or result.stdout or result.stderr:
            raise ValueError('compiled exact-support reader build failed: ' +
                             result.stdout + result.stderr)
    return binary


def collect_t1(source, selected_tunes, boundary_axes=None, *, row_upper_bounds=False,
               event_activity_field=None, include_diagnostics=False, work_root=None,
               pair_population_registry=None):
    """One compiled exact-support pass for additive T1, exposure and diagnostics."""
    selected_tunes = set(selected_tunes)
    verify_pairs = pair_population_registry is not None
    if verify_pairs and (set(pair_population_registry) != {'charm', 'beauty'} or
            any(not values or len(values) != len(set(values)) or
                any(type(pdg) is not int or pdg == 0 for pdg in values)
                for values in pair_population_registry.values())):
        raise ValueError('all-selected support pair registry differs')
    if not selected_tunes or selected_tunes - set(source.index['tune_ordinals']):
        raise ValueError('T1 requested an absent tune')
    if event_activity_field not in (None, 'a15_eta4', 'a15_eta1'):
        raise ValueError('T1 event accounting activity field differs')
    if boundary_axes is not None and (set(boundary_axes) != {'pt', 'eta', 'phi'} or
                                      tuple(boundary_axes['pt']) != G9_PT_EDGES):
        raise ValueError('G9 exact boundary axes differ')
    if work_root is None:
        temporary = tempfile.TemporaryDirectory(prefix='hadronization-support-')
        work = Path(temporary.name)
    else:
        temporary = None
        work = Path(work_root).absolute()
        work.mkdir(parents=True, exist_ok=True)
    try:
        binary = _compile_support_scan(work)
        mapping = work / 'support-map.tsv'
        output = work / 'support-scan.tsv'
        for path in (mapping, output):
            if path.exists() or path.is_symlink():
                raise FileExistsError(path)
        included = [shard for shard in source.index['shards']
                    if any(member['tune'] in selected_tunes for member in shard['members'])]
        with mapping.open('x', encoding='utf-8', newline='\n') as stream:
            for shard in included:
                root = shard['query_root']['path']
                if '\t' in root or '\n' in root or ' ' in root:
                    raise ValueError('support ROOT path cannot enter compiled map')
                stream.write('SHARD\t' + root + '\n')
                if verify_pairs:
                    for sector, name in ((4, 'charm'), (5, 'beauty')):
                        for pdg in pair_population_registry[name]:
                            stream.write('ASSOCIATE\t{}\t{}\n'.format(sector, pdg))
                for local, member in enumerate(shard['members']):
                    for token in (member['tune'],):
                        if not token or any(char.isspace() for char in token):
                            raise ValueError('support tune token differs')
                    stream.write('MEMBER\t{}\t{}\t{}\t{}\n'.format(
                        local, member['tune'], member['block'], member['events']))
        field = 'eta1' if event_activity_field == 'a15_eta1' else 'eta4'
        command = [str(binary), str(mapping), field, str(output)]
        if verify_pairs:
            command.append('all-selected')
        completed = subprocess.run(command,
                                   capture_output=True, text=True)
        if completed.returncode or completed.stdout or completed.stderr:
            raise ValueError('compiled exact-support reader failed: ' +
                             completed.stdout + completed.stderr)
        result, event_totals, moments, diagnostics = {}, {}, {}, {}
        boundaries = {}
        opened = None
        upper = {}
        pair_proofs, pair_counts = {}, {}
        seen = set()
        with output.open(encoding='ascii') as stream:
            if stream.readline().rstrip('\n') != 'hadronization_support_scan_v1':
                raise ValueError('compiled exact-support output schema differs')
            for raw in stream:
                fields = raw.rstrip('\n').split('\t')
                if fields == ['END']:
                    break
                kind = fields[0]
                if kind == 'OPEN' and len(fields) == 2:
                    opened = int(fields[1])
                elif kind == 'UPPER' and len(fields) == 3:
                    upper[fields[1]] = int(fields[2])
                elif verify_pairs and kind == 'PAIR_PROOF' and len(fields) == 8:
                    key = (fields[1], int(fields[2]))
                    row = dict(zip(('events', 'eligible_triggers', 'zero_partner_triggers',
                                    'candidate_pairs', 'stored_pairs'), map(int, fields[3:])))
                    if (key in pair_proofs or min(row.values()) < 0 or
                            row['candidate_pairs'] != row['stored_pairs'] or
                            row['zero_partner_triggers'] > row['eligible_triggers']):
                        raise ValueError('all-selected pair-population proof differs')
                    pair_proofs[key] = row
                elif verify_pairs and kind == 'PAIR_COUNT' and len(fields) == 6:
                    key = (fields[1], *map(int, fields[2:5]))
                    if key in pair_counts or int(fields[5]) <= 0:
                        raise ValueError('all-selected pair-population species count differs')
                    pair_counts[key] = int(fields[5])
                elif kind == 'MOMENT' and len(fields) == 9:
                    key = (fields[1], int(fields[2]))
                    if key in moments:
                        raise ValueError('duplicate exact event moment')
                    m = EventMoments()
                    m.events = int(fields[3])
                    (m.sumw, m.sumw2, m.sumabsw, m.pthat_sum,
                     m.hard_scale_sum) = tuple(float.fromhex(x) for x in fields[4:9])
                    moments[key] = m
                    event_totals[key] = m.events
                elif kind in ('ACTIVITY', 'NMPI', 'PROCESS') and len(fields) == 5:
                    key = (fields[1], int(fields[2]))
                    target = {'ACTIVITY': 'activity_counts', 'NMPI': 'n_mpi_counts',
                              'PROCESS': 'process_counts'}[kind]
                    bucket = getattr(moments[key], target)
                    value = int(fields[3])
                    if value in bucket:
                        raise ValueError('duplicate exact event category')
                    bucket[value] = int(fields[4])
                elif kind == 'T1' and len(fields) == 10:
                    key = (fields[1], int(fields[2]), int(fields[3]))
                    if key in result:
                        raise ValueError('duplicate exact T1 key')
                    result[key] = T1Counts(hadrons=int(fields[4]),
                        charm_constituents=int(fields[5]), beauty_constituents=int(fields[6]),
                        weighted_hadrons=float.fromhex(fields[7]),
                        weighted_charm_constituents=float.fromhex(fields[8]),
                        weighted_beauty_constituents=float.fromhex(fields[9]))
                elif kind == 'DIAG' and len(fields) == 11:
                    key = (fields[1], int(fields[2]))
                    if key in diagnostics:
                        raise ValueError('duplicate exact diagnostic key')
                    diagnostics[key] = RawDiagnostics(
                        natural_final_hadrons=int(fields[3]),
                        natural_final_weighted_sum=float.fromhex(fields[4]),
                        charm_constituents=int(fields[5]),
                        charm_constituent_weighted_sum=float.fromhex(fields[6]),
                        beauty_constituents=int(fields[7]),
                        beauty_constituent_weighted_sum=float.fromhex(fields[8]),
                        strict_selected_final_hadrons=int(fields[9]),
                        strict_selected_final_weighted_sum=float.fromhex(fields[10]))
                elif kind in ('ORIGIN', 'CLOSURE') and len(fields) == 8:
                    key = (fields[1], int(fields[2]))
                    summary = diagnostics.setdefault(key, RawDiagnostics())
                    grouping = summary.origin_pairs if kind == 'ORIGIN' else summary.closure_terms
                    group = (int(fields[3]), int(fields[4]), int(fields[5]))
                    if group in grouping:
                        raise ValueError('duplicate exact diagnostic group')
                    grouping[group] = (int(fields[6]), float.fromhex(fields[7]))
                elif kind == 'BOUNDARY' and len(fields) == 8:
                    if boundary_axes is not None and fields[1] in selected_tunes:
                        state = (fields[1], int(fields[2]), int(fields[3]))
                        for axis_name, coordinate in zip(('pt', 'eta', 'phi'), fields[4:7]):
                            bin_id = _histogram_bin(float.fromhex(coordinate),
                                                    boundary_axes[axis_name])
                            boundaries.setdefault(state + (axis_name, bin_id),
                                                  AdditiveCell()).add_exact(float.fromhex(fields[7]))
                else:
                    raise ValueError('compiled exact-support output record differs')
                seen.add(kind)
            else:
                raise ValueError('compiled exact-support output lacks END')
        if opened != len(included) or set(upper) != {'activity', 'triggers', 'pairs', 'kinematics'}:
            raise ValueError('compiled exact-support input coverage differs')
        expected = {(m['tune'], m['block']) for shard in included
                    for m in shard['members'] if m['tune'] in selected_tunes}
        if expected != {key for key in moments if key[0] in selected_tunes}:
            raise ValueError('compiled exact-support tune/block exposure differs')
        if verify_pairs:
            if (set(pair_proofs) != set(moments) or
                    any(row['events'] != moments[key].events or row['stored_pairs'] !=
                        sum(count for group, count in pair_counts.items() if group[:2] == key)
                        for key, row in pair_proofs.items())):
                raise ValueError('all-selected pair proof source/species closure differs')
            pair_proof = dict(schema='hadronization_all_selected_pair_population_v1',
                state='PASS', collection_index_sha256=source.expected_sha256,
                registry_sha256=hashlib.sha256(json.dumps(pair_population_registry,
                    sort_keys=True, separators=(',', ':')).encode('ascii')).hexdigest(),
                scan_sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
                blocks=[dict(tune_id=k[0], block_id=k[1], **v)
                    for k, v in sorted(pair_proofs.items()) if k[0] in selected_tunes],
                species_counts=[dict(tune_id=k[0], block_id=k[1], trigger_pdg=k[2],
                    associate_pdg=k[3], count=v) for k, v in sorted(pair_counts.items())
                    if k[0] in selected_tunes])
        result = {key: row for key, row in result.items() if key[0] in selected_tunes}
        event_totals = {key: row for key, row in event_totals.items() if key[0] in selected_tunes}
        moments = {key: row for key, row in moments.items() if key[0] in selected_tunes}
        diagnostics = {key: row for key, row in diagnostics.items() if key[0] in selected_tunes}
        if boundary_axes is None:
            value = (result, event_totals, opened, upper) if row_upper_bounds else (
                result, event_totals, opened)
        else:
            value = (result, event_totals, boundaries, opened, upper) if row_upper_bounds else (
                result, event_totals, boundaries, opened)
        if event_activity_field is not None:
            value += (moments,)
        if include_diagnostics:
            value += (diagnostics,)
        if verify_pairs:
            value += (pair_proof,)
        return value
    finally:
        if temporary is not None:
            temporary.cleanup()


@dataclass
class G9Primitives:
    cells: dict
    metrics: ScanMetrics
    species_pdgs: tuple[int, ...]


def collect_g9(source, species_pdgs, eta_edges, phi_edges,
               selected_tunes=None):
    """Reduce all-origin direct selected-final G9 with no physical pT floor."""
    species = set(species_pdgs)
    if not species or len(species) != len(tuple(species_pdgs)):
        raise ValueError('G9 species request is empty or duplicated')
    if len(eta_edges) < 2 or len(phi_edges) < 2:
        raise ValueError('G9 coordinate axes are empty')
    result = {}

    def admit_axes(family,axes):
        named={axis.GetName():axis for axis in axes}
        pdg_axis=named.get('pdg')
        if family!='kinematics' or pdg_axis is None:
            raise ValueError('G9 sparse species axis is absent')
        labels={int(pdg_axis.GetBinLabel(index))
                for index in range(1,pdg_axis.GetNbins()+1)
                if pdg_axis.GetBinLabel(index)}
        if not species.issubset(labels):
            raise ValueError('G9 configured signed species lacks query axis support')

    def consume(cell,axes):
        names = {axis.GetName(): i for i,axis in enumerate(axes)}
        for required in ('pdg','pt','eta','phi'):
            if required not in names:
                raise ValueError('G9 sparse axis is missing')
        coord = cell.coordinates
        pdg_label = axes[names['pdg']].GetBinLabel(coord[names['pdg']])
        if not pdg_label:
            raise ValueError('G9 species label is missing')
        pdg = int(pdg_label)
        if pdg not in species:
            return
        pt_axis = axes[names['pt']]
        pt_coord = coord[names['pt']]
        if pt_coord == 0:
            raise ValueError('negative G9 pT underflow is invalid input')
        if (1 <= pt_coord <= pt_axis.GetNbins() and
                pt_axis.GetBinLowEdge(pt_coord) < 0.):
            raise ValueError('G9 physical pT axis crosses negative values')
        eta_axis = axes[names['eta']]
        eta_coord = coord[names['eta']]
        if not 1 <= eta_coord <= eta_axis.GetNbins():
            return
        eta_low = eta_axis.GetBinLowEdge(eta_coord)
        eta_high = eta_axis.GetBinUpEdge(eta_coord)
        if eta_high <= -4. or eta_low > 4.:
            return
        if eta_low < -4. or eta_high > 4.:
            raise ValueError('native eta bin crosses G9 acceptance')
        for axis_name,edges in (('pt',G9_PT_EDGES),('eta',eta_edges),('phi',phi_edges)):
            source_axis = axes[names[axis_name]]
            source_coord = coord[names[axis_name]]
            if axis_name != 'pt' and not 1 <= source_coord <= source_axis.GetNbins():
                continue
            try:
                output_bin = _aligned_sparse_bin(source_axis,source_coord,edges)
            except ValueError as error:
                raise ValueError('G9 {} sparse coordinate {} [{},{}] differs from requested output axis'.format(
                    axis_name,source_coord,source_axis.GetBinLowEdge(source_coord),
                    source_axis.GetBinUpEdge(source_coord))) from error
            key = (cell.tune,cell.block,pdg,axis_name,output_bin)
            result.setdefault(key,AdditiveCell()).add(cell)

    tunes=(source.index['tune_ordinals'] if selected_tunes is None
           else selected_tunes)
    metrics = source.scan(('kinematics',),tunes,consume,
                          inspect_axes=admit_axes)
    return G9Primitives(result,metrics,tuple(sorted(species)))


def write_native_transport(source, primitives, g9, t1, event_totals, path,
                           row_upper_bounds=None,selected_tunes=None):
    """Serialize authenticated additive cells for the C++ numerical engine.

    This records primitive values in exact binary64 hex. It performs no
    normalization, OS-minus-SS subtraction, class membership, or covariance.
    The collection index and A's scientific identity are the parent binding.
    """
    path = Path(path).absolute()
    if path.exists() or path.is_symlink():
        raise FileExistsError(path)
    if path.parent.is_symlink() or not path.parent.is_dir():
        raise ValueError('native transport parent is absent or a symlink')
    tunes=(set(source.index['tune_ordinals']) if selected_tunes is None
           else set(selected_tunes))
    if not tunes or tunes-set(source.index['tune_ordinals']):
        raise ValueError('native transport requested tune domain differs')
    selected_members=[member for member in source.index['sources']
                      if member['tune'] in tunes]
    expected_exposure = {}
    for member in selected_members:
        count = member['events']
        if type(count) is not int or count < 1:
            raise ValueError('native event exposure differs from authenticated sources')
        key = (member['tune'], member['block'])
        expected_exposure[key] = expected_exposure.get(key, 0) + count
    if ({tune for tune, _ in expected_exposure} != tunes or
            not isinstance(event_totals, dict) or
            any(type(count) is not int or count < 1
                for count in event_totals.values()) or
            event_totals != expected_exposure):
        raise ValueError('native event exposure differs from authenticated sources')
    for mapping, tune_index, block_index in (
            (primitives.activity, 0, 1), (primitives.triggers, 1, 2),
            (primitives.pairs, 1, 2), (g9.cells, 0, 1), (t1, 0, 1)):
        if any((key[tune_index], key[block_index]) not in expected_exposure
               for key in mapping):
            raise ValueError('native primitive lacks authenticated source exposure')
    def number(value):
        if type(value) not in (int,float) or not math.isfinite(value):
            raise ValueError('nonfinite native transport value')
        return float(value).hex()
    def cell(value):
        if value.sumw2 < 0:
            raise ValueError('negative native transport Sumw2')
        return number(value.value),number(value.sumw2)
    lines = ['hadronization_native_primitives_v1',
             'SOURCE\t{}\t{}\t{}'.format(source.expected_sha256,
                source.index['scientific_identity_sha256'],
                source.index['analysis_sha256'])]
    lines.append('ACTIVITY_FIELD\t'+primitives.activity_field)
    if row_upper_bounds is not None:
        if set(row_upper_bounds) != {'activity','triggers','pairs','kinematics'} or \
                any(type(count) is not int or count < 0
                    for count in row_upper_bounds.values()):
            raise ValueError('native support row upper bounds differ')
        for family,count in sorted(row_upper_bounds.items()):
            lines.append('SUPPORT_UPPER\t{}\t{}'.format(family,count))
    for profile in primitives.profile_ids:
        lines.append('PROFILE\t'+profile)
    for trigger in primitives.selected_triggers:
        lines.append('TRIGGER_SCOPE\t'+str(trigger))
    for trigger,associate in primitives.selected_pairs:
        lines.append('PAIR_SCOPE\t{}\t{}'.format(trigger,associate))
    for species in g9.species_pdgs:
        lines.append('G9_SCOPE\t'+str(species))
    for species in sorted({key[2] for key in t1}):
        lines.append('T1_SCOPE\t'+str(species))
    for (tune,block,activity),value in sorted(primitives.activity.items()):
        lines.append('ACTIVITY\t{}\t{}\t{}\t{}\t{}'.format(
            tune,block,activity,*cell(value)))
    for (profile,tune,block,activity,trigger),value in sorted(primitives.triggers.items()):
        lines.append('TRIGGER\t{}\t{}\t{}\t{}\t{}\t{}\t{}'.format(
            profile,tune,block,activity,trigger,*cell(value)))
    for (profile,tune,block,activity,trigger,associate,sign,dphi),value in sorted(primitives.pairs.items()):
        lines.append('PAIR\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}'.format(
            profile,tune,block,activity,trigger,associate,sign,dphi,*cell(value)))
    for (tune,block,species,axis,bin_id),value in sorted(g9.cells.items()):
        lines.append('G9\t{}\t{}\t{}\t{}\t{}\t{}\t{}'.format(
            tune,block,species,axis,bin_id,*cell(value)))
    for (tune,block,species),value in sorted(t1.items()):
        lines.append('T1\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}'.format(
            tune,block,species,value.hadrons,value.charm_constituents,
            value.beauty_constituents,number(value.weighted_hadrons),
            number(value.weighted_charm_constituents),
            number(value.weighted_beauty_constituents)))
    for (tune,block),events in sorted(event_totals.items()):
        if type(events) is not int or events < 0:
            raise ValueError('invalid native event exposure')
        lines.append('EXPOSURE\t{}\t{}\t{}'.format(tune,block,events))
    lines.append('END')
    descriptor,temporary_name = tempfile.mkstemp(prefix='.'+path.name+'.',
                                                 suffix='.tmp',dir=path.parent)
    try:
        with os.fdopen(descriptor,'w',encoding='ascii',newline='\n') as stream:
            stream.write('\n'.join(lines)+'\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_name,path)
    finally:
        if os.path.exists(temporary_name):
            os.unlink(temporary_name)
    return dict(path=str(path),records=len(lines)-3,
                bytes=path.stat().st_size)
