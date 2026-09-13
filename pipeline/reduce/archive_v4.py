"""Version-aware direct typed ROOT backbone for the canonical v4 result.

The value DAG is a lossless typed view, and each numerical/source/accounting
table is independently checked against it on cold read. No input collection or
engine sidecar is needed for interpretation.
"""
from array import array
import csv
import io
import json
import math
import os
from pathlib import Path
import tempfile

from . import projection as p, typed_nodes

SCHEMA='hadronization_self_contained_typed_root_v4'

FIELDS={
 'bindings':dict(schema='s',request_sha256='s',science_content_sha256='s',
    collection_kind='s',collection_state='s',collection_index_sha256='s',
    collection_index_bytes='u',collection_scientific_identity_sha256='s',
    member_files_sha256='s',source_members_sha256='s',
    admission_qualification='s',admission_expected_sources_sha256='s',
    admission_natural_members_sha256='s',
    campaign_scope='s',campaign_attempts='u',campaign_successful_events='u'),
 'points':dict(index='u',semantic_id='s',point_key_sha256='s',role='s',
    tune='s',quantity='s',component='s',axis='s',bin='i',units='s',
    center_status='s',center_present='b',center='d',
    uncertainty_status='s',variance_present='b',variance='d',
    error_present='b',error='d'),
 'event_moments':dict(tune='s',block='u',source_members_sha256='s',scope='s',
    events='u',sumw='d',sumw2='d',sumabsw='d',event_weight_terms='u',
    content_sha256='s'),
 'support_diagnostics':dict(tune='s',block='u',event_moments_sha256='s',
    natural_final_hadrons='u',natural_final_weighted_sum='d',
    charm_constituents='u',charm_constituent_weighted_sum='d',
    beauty_constituents='u',beauty_constituent_weighted_sum='d',
    strict_selected_final_hadrons='u',
    strict_selected_final_weighted_sum='d',
    pthat_sum='d',hard_scale_sum='d',content_sha256='s'),
 'diagnostic_activity':dict(tune='s',block='u',activity_bin='u',events='u'),
 'diagnostic_n_mpi':dict(tune='s',block='u',n_mpi='u',events='u'),
 'diagnostic_process':dict(tune='s',block='u',process_code='i',events='u'),
 'diagnostic_origin':dict(tune='s',block='u',origin='i',category='i',
    sign='i',rows='u',weighted_sum='d'),
 'diagnostic_closure':dict(tune='s',block='u',category='i',visible='b',
    coefficient='i',rows='u',weighted_sum='d'),
 'block_values':dict(point='u',tune='s',block='u',events='u',sumw='d',
    sumw2='d',sumabsw='d',event_weight_terms='u',event_moments_sha256='s'),
 'block_components':dict(point='u',tune='s',block='u',component_id='s',
    value='d'),
 'denominator_parents':dict(point='u',ordinal='u',natural_key='s',
    status='s',retained_after_algebra='b',pooled_present='b',
    pooled_value='d',policy_id='s'),
 'denominator_deletions':dict(point='u',parent_ordinal='u',block='u',
    status='s'),
 'covariance_points':dict(group_id='s',slot='u',point='u',valid='b',
    units='s'),
 'covariance_factors':dict(group_id='s',slot='u',tune='s',
    source_family_sha256='s',block='u',finite='b',valid='b',leaf='d',
    leave_mean='d',centered_factor='d'),
 'class_boundaries':dict(tune='s',activity='s',class_id='i',low='i',
    high='i',events='u',event_weight='d',empty='b',status='s',
    content_sha256='s'),
 'class_boundary_deletions':dict(tune='s',class_id='i',omitted_block='u',
    source_family_sha256='s',status='s',low_present='b',low='i',
    high_present='b',high='i',empty='b',weight_present='b',
    weighted_measure='d',content_sha256='s'),
 'collection_members':dict(file_id='s',role='s',shard_present='b',
    shard_ordinal='u',tune_present='b',tune='s',sha256='s',bytes='u'),
 'campaign_tunes':dict(tune='s',sources='u',successful_events='u',
    submitted_attempts='u',accepted_attempts='u',discarded_attempts='u'),
 'campaign_trials':dict(tune='s',scope='s',count_present='b',count='u',
    status='s',reason_codes='s'),
 'campaign_attempt_evidence':dict(outcome='s',evidence_status='s',count='u'),
 'selected_tune_exposure':dict(tune='s',successful_events='u'),
 'materialization':dict(point='u',status='s',reason_codes='s'),
 'g9_science':dict(metadata_json='s',metadata_sha256='s')}


def _num(token):
    return 0. if token is None else float.fromhex(token)


def _rows(value,name):
    points=value['points'];binding=value['artifact_binding']
    provenance=value['provenance'];accounting=provenance['campaign_accounting']
    if name=='bindings':
        yield dict(schema=value['schema'],request_sha256=value['request_sha256'],
            science_content_sha256=value['science_content_sha256'],
            collection_kind=binding['kind'],
            collection_state=binding['collection_state'],
            collection_index_sha256=binding['collection_index_sha256'],
            collection_index_bytes=binding['collection_index_bytes'],
            collection_scientific_identity_sha256=binding[
                'collection_scientific_identity_sha256'],
            member_files_sha256=binding['member_files_sha256'],
            source_members_sha256=provenance['source_members_sha256'],
            admission_qualification=value['admission_closure']['qualification'],
            admission_expected_sources_sha256=value['admission_closure'][
                'expected_sources_sha256'],
            admission_natural_members_sha256=value['admission_closure'][
                'natural_members_sha256'],
            campaign_scope=accounting['scope'],
            campaign_attempts=accounting['counts']['attempts'],
            campaign_successful_events=accounting['counts']['successful_events'])
    elif name=='points':
        for index,item in enumerate(points):
            curve=item['key']['curve'];bins=item['key']['bins']
            yield dict(index=index,semantic_id=item['semantic_id'],
                point_key_sha256=p.digest(item['key']),role=curve['role_id'],
                tune=curve['tune_id'],quantity=curve['quantity'],
                component=curve['component'],axis=curve['axis_id'] or '',
                bin=bins[0]['index'] if bins else -1,units=item['units'],
                center_status=item['center_status'],
                center_present=item['center'] is not None,
                center=_num(item['center']),
                uncertainty_status=item['uncertainty_status'],
                variance_present=item['variance'] is not None,
                variance=_num(item['variance']),
                error_present=item['standard_error'] is not None,
                error=_num(item['standard_error']))
    elif name=='event_moments':
        for item in value['event_moment_receipts']:
            yield dict(tune=item['tune_id'],block=item['block_id'],
                source_members_sha256=item['source_members_sha256'],
                scope=item['scope'],events=item['events'],sumw=_num(item['sumw']),
                sumw2=_num(item['sumw2']),sumabsw=_num(item['sumabsw']),
                event_weight_terms=item['event_weight_terms'],
                content_sha256=item['content_sha256'])
    elif name.startswith('diagnostic_') or name=='support_diagnostics':
        for item in value['support_diagnostic_receipts']:
            common=dict(tune=item['tune_id'],block=item['block_id'])
            if name=='support_diagnostics':
                yield dict(common,event_moments_sha256=item['event_moments_sha256'],
                    **{key:_num(item[key]) if key.endswith('_sum') else item[key]
                        for key in ('natural_final_hadrons',
                            'natural_final_weighted_sum','charm_constituents',
                            'charm_constituent_weighted_sum','beauty_constituents',
                            'beauty_constituent_weighted_sum',
                            'strict_selected_final_hadrons',
                            'strict_selected_final_weighted_sum',
                            'pthat_sum','hard_scale_sum')},
                    content_sha256=item['content_sha256'])
            elif name=='diagnostic_activity':
                for row in item['activity_counts']:yield dict(common,**row)
            elif name=='diagnostic_n_mpi':
                for row in item['n_mpi_counts']:yield dict(common,**row)
            elif name=='diagnostic_process':
                for row in item['process_counts']:yield dict(common,**row)
            elif name=='diagnostic_origin':
                for row in item['origin_pairs']:
                    yield dict(common,origin=row['origin'],category=row['category'],
                        sign=row['sign'],rows=row['rows'],
                        weighted_sum=_num(row['weighted_sum']))
            elif name=='diagnostic_closure':
                for row in item['closure_terms']:
                    yield dict(common,category=row['category'],
                        visible=row['visible'],coefficient=row['coefficient'],
                        rows=row['rows'],weighted_sum=_num(row['weighted_sum']))
    elif name in ('block_values','block_components','denominator_parents',
                  'denominator_deletions'):
        for index,item in enumerate(points):
            if name.startswith('block_'):
                for block in item['block_values']:
                    common=dict(point=index,tune=block['tune_id'],
                                block=block['block_id'])
                    if name=='block_values':
                        yield dict(common,events=block['events'],
                            sumw=_num(block['sumw']),sumw2=_num(block['sumw2']),
                            sumabsw=_num(block['sumabsw']),
                            event_weight_terms=block['event_weight_terms'],
                            event_moments_sha256=block['event_moments_sha256'])
                    else:
                        for component in block['additive_components']:
                            yield dict(common,component_id=component['id'],
                                       value=_num(component['value']))
            else:
                for ordinal,parent in enumerate(item['denominator_receipts']):
                    if name=='denominator_parents':
                        yield dict(point=index,ordinal=ordinal,
                            natural_key=parent['natural_key'],status=parent['status'],
                            retained_after_algebra=parent['retained_after_algebra'],
                            pooled_present=parent['pooled_value'] is not None,
                            pooled_value=_num(parent['pooled_value']),
                            policy_id=parent['policy_id'])
                    else:
                        for block,status in enumerate(parent['delete_one_statuses'],1):
                            yield dict(point=index,parent_ordinal=ordinal,
                                       block=block,status=status)
    elif name in ('covariance_points','covariance_factors'):
        index_by_key={p.canonical(item['key']):index for index,item in
                      enumerate(points)}
        for group in value['covariance']:
            if name=='covariance_points':
                for slot,key in enumerate(group['ordered_point_keys']):
                    yield dict(group_id=group['id'],slot=slot,
                        point=index_by_key[p.canonical(key)],
                        valid=group['valid_mask'][slot],
                        units=group['units_by_point'][slot])
            else:
                for family in group['independent_families']:
                    for block,complements in enumerate(family['complements'],1):
                        for slot,leaf in enumerate(complements):
                            mean=family['leave_mean'][slot]
                            finite=family['finite_mask'][block-1][slot]
                            valid=group['valid_mask'][slot] and family[
                                'usable_mask'][slot]
                            yield dict(group_id=group['id'],slot=slot,
                                tune=family['tune_id'],source_family_sha256=
                                family['source_family_digest'],block=block,
                                finite=finite,valid=valid,leaf=_num(leaf),
                                leave_mean=_num(mean),
                                centered_factor=math.sqrt(.9)*(
                                    _num(leaf)-_num(mean)) if valid else 0.)
    elif name=='class_boundaries':
        for item in value['resolved']['class_boundaries']:
            yield dict(tune=item['tune_id'],activity=item['activity_id'],
                class_id=item['class_id'],low=item['actual_integer_low'],
                high=item['actual_integer_high'],events=item['events'],
                event_weight=_num(item['event_weight']),empty=item['empty'],
                status=item['boundary_status'],
                content_sha256=item['boundary_receipt_sha256'])
    elif name=='class_boundary_deletions':
        for item in value['class_boundary_deletions']:
            yield dict(tune=item['tune_id'],class_id=item['class_id'],
                omitted_block=item['omitted_block'],
                source_family_sha256=item['source_family_digest'],
                status=item['status'],low_present=item['low'] is not None,
                low=item['low'] or 0,high_present=item['high'] is not None,
                high=item['high'] or 0,empty=item['empty'],
                weight_present=item['weighted_measure'] is not None,
                weighted_measure=_num(item['weighted_measure']),
                content_sha256=item['content_sha256'])
    elif name=='collection_members':
        for item in binding['member_files']:
            yield dict(file_id=item['file_id'],role=item['role'],
                shard_present=item['shard_ordinal'] is not None,
                shard_ordinal=item['shard_ordinal'] or 0,
                tune_present=item['tune_id'] is not None,
                tune=item['tune_id'] or '',sha256=item['sha256'],bytes=item['bytes'])
    elif name=='campaign_tunes':
        for item in accounting['by_tune']:
            yield dict(tune=item['tune_id'],**{key:item[key] for key in (
                'sources','successful_events','submitted_attempts',
                'accepted_attempts','discarded_attempts')})
    elif name=='campaign_trials':
        for item in accounting['generator_event_trials_by_tune']:
            yield dict(tune=item['tune_id'],scope=item['scope'],
                count_present=item['count'] is not None,
                count=item['count'] or 0,status=item['status'],
                reason_codes=p.canonical(item['reason_codes']))
    elif name=='campaign_attempt_evidence':
        yield from accounting['attempt_evidence']
    elif name=='selected_tune_exposure':
        for item in provenance['successful_events_by_tune']:
            yield dict(tune=item['tune_id'],successful_events=item['count'])
    elif name=='materialization':
        for index,item in enumerate(value['materialization']):
            yield dict(point=index,status=item['status'],
                       reason_codes=p.canonical(item['reason_codes']))
    elif name=='g9_science':
        metadata=value['resolved']['g9_science']
        if metadata is not None:
            yield dict(metadata_json=p.canonical(metadata),
                       metadata_sha256=p.digest(metadata))
    else:raise ValueError('unknown direct v4 ROOT table')


def _tree(ROOT,name,fields):
    tree=ROOT.TTree(name,name)
    holders={}
    for field,kind in fields.items():
        if kind=='s':
            holder=ROOT.std.string();tree.Branch(field,holder)
        else:
            code,leaf={'u':('Q','l'),'i':('q','L'),
                       'd':('d','D'),'b':('b','O')}[kind]
            holder=array(code,[0]);tree.Branch(field,holder,field+'/'+leaf)
        holders[field]=holder
    return tree,holders


def _fill(tree,holders,row):
    for field,holder in holders.items():
        value=row[field]
        if isinstance(holder,array):holder[0]=value
        else:holder.assign(value)
    tree.Fill()


def _node_tree(ROOT,value):
    stream=io.StringIO();root_id=typed_nodes.nodes(value,stream)
    tree=ROOT.TTree('nodes','Typed deduplicated value DAG')
    identifier=array('Q',[0]);kind=ROOT.std.string();text=ROOT.std.string()
    children=ROOT.std.vector('unsigned long long')()
    keys=ROOT.std.vector('string')()
    tree.Branch('id',identifier,'id/l');tree.Branch('kind',kind)
    tree.Branch('text',text);tree.Branch('children',children)
    tree.Branch('keys',keys)
    for line in stream.getvalue().splitlines():
        fields=line.split('\t')
        identifier[0]=int(fields[1]);kind.assign(fields[2])
        text.assign(typed_nodes.decode(fields[3]));children.clear();keys.clear()
        if fields[4]!='-':
            for item in fields[4].split(','):children.push_back(int(item))
        if fields[5]!='-':
            for item in fields[5].split(','):keys.push_back(typed_nodes.decode(item))
        tree.Fill()
    return tree,root_id


def _decode_nodes(tree,root_id):
    values=[]
    for row in tree:
        identifier=int(row.id);kind=str(row.kind);text=str(row.text)
        children=list(map(int,row.children));keys=list(map(str,row.keys))
        if identifier!=len(values) or any(i>=identifier for i in children):
            raise ValueError('v4 ROOT typed node order differs')
        if kind=='O':
            if keys!=sorted(set(keys)) or len(keys)!=len(children) or text:
                raise ValueError('v4 ROOT typed object topology differs')
            value={key:values[index] for key,index in zip(keys,children)}
        elif kind=='A':
            if keys or text:raise ValueError('v4 ROOT typed array topology differs')
            value=[values[index] for index in children]
        else:
            if keys or children:raise ValueError('v4 ROOT scalar topology differs')
            if kind=='N' and text=='':value=None
            elif kind=='B' and text in ('0','1'):value=text=='1'
            elif kind=='I' and str(int(text))==text:value=int(text)
            elif kind=='F' and math.isfinite(float.fromhex(text)):
                value=float.fromhex(text)
            elif kind=='S':value=text
            else:raise ValueError('v4 ROOT scalar kind differs')
        values.append(value)
    if not 0<=root_id<len(values):raise ValueError('v4 ROOT root node absent')
    return values[root_id]


def _equal(field,kind,actual,expected):
    if kind=='s':return str(actual)==expected
    if kind=='d':return float(actual).hex()==float(expected).hex()
    if kind=='b':return bool(actual)==bool(expected)
    return int(actual)==int(expected)


def write(value,output):
    import ROOT
    ROOT.gROOT.SetBatch(True)
    value=value.to_dict() if hasattr(value,'to_dict') else value
    if value.get('schema')!=p.RESULT_SCHEMA_NATIVE:
        raise ValueError('v4 ROOT writer requires canonical v4 result')
    p.ProjectionResult.from_dict(value,cold=True)
    output=Path(output).absolute()
    if output.exists() or output.is_symlink():raise FileExistsError(output)
    output.parent.mkdir(parents=True,exist_ok=True)
    descriptor,temporary=tempfile.mkstemp(prefix='.'+output.name+'.',
                                          suffix='.root',dir=output.parent)
    os.close(descriptor)
    try:
        file=ROOT.TFile.Open(temporary,'RECREATE')
        if not file or file.IsZombie():raise ValueError('v4 ROOT cannot create')
        try:
            nodes,root_id=_node_tree(ROOT,value)
            nodes.Write()
            metadata=dict(schema=SCHEMA,payload_schema=value['schema'],
                root_node=root_id,value_sha256=p.digest(value),
                request_sha256=value['request_sha256'],
                science_content_sha256=value['science_content_sha256'],
                collection_index_sha256=value['artifact_binding'][
                    'collection_index_sha256'],
                member_files_sha256=value['artifact_binding'][
                    'member_files_sha256'])
            ROOT.TObjString(p.canonical(metadata)).Write('v4_metadata')
            for name,fields in FIELDS.items():
                tree,holders=_tree(ROOT,name,fields)
                for row in _rows(value,name):_fill(tree,holders,row)
                tree.Write()
        finally:file.Close()
        root_sha=p.file_digest(temporary)
        recovered=read(temporary,root_sha,p.digest(value))
        if p.digest(recovered)!=p.digest(value):
            raise ValueError('v4 ROOT cold reconstruction differs')
        os.link(temporary,output)
        p._reducer().fsync_directory(output.parent)
    finally:
        if os.path.exists(temporary):os.unlink(temporary)
    return dict(schema=SCHEMA,path=str(output),root_sha256=root_sha,
                root_bytes=output.stat().st_size,value_sha256=p.digest(value),
                direct_tables={name:sum(1 for _ in _rows(value,name))
                               for name in FIELDS})


def read(path,expected_root_sha256,expected_value_sha256):
    import ROOT
    ROOT.gROOT.SetBatch(True)
    path=Path(path)
    if path.is_symlink() or not path.is_file() or \
            p.file_digest(path)!=expected_root_sha256:
        raise ValueError('v4 ROOT differs from trusted physical hash')
    file=ROOT.TFile.Open(str(path),'READ')
    if not file or file.IsZombie():raise ValueError('v4 ROOT cannot open')
    try:
        keys=list(file.GetListOfKeys())
        if any(int(key.GetCycle())!=1 for key in keys) or \
                {str(key.GetName()) for key in keys} != (
                    set(FIELDS)|{'nodes','v4_metadata'}):
            raise ValueError('v4 ROOT exact object domain differs')
        meta=json.loads(str(file.Get('v4_metadata').GetString()))
        if set(meta)!={'schema','payload_schema','root_node','value_sha256',
                'request_sha256','science_content_sha256',
                'collection_index_sha256','member_files_sha256'} or \
                meta['schema']!=SCHEMA or \
                meta['payload_schema']!=p.RESULT_SCHEMA_NATIVE or \
                meta['value_sha256']!=expected_value_sha256:
            raise ValueError('v4 ROOT metadata schema/value differs')
        nodes=file.Get('nodes')
        if not nodes or {str(b.GetName()) for b in nodes.GetListOfBranches()} != (
                {'id','kind','text','children','keys'}):
            raise ValueError('v4 ROOT typed node branches differ')
        value=_decode_nodes(nodes,meta['root_node'])
        p.ProjectionResult.from_dict(value,cold=True)
        if p.digest(value)!=expected_value_sha256 or \
                any(meta[field]!=value[source] for field,source in (
                    ('request_sha256','request_sha256'),
                    ('science_content_sha256','science_content_sha256'))) or \
                meta['collection_index_sha256']!=value['artifact_binding'][
                    'collection_index_sha256'] or \
                meta['member_files_sha256']!=value['artifact_binding'][
                    'member_files_sha256']:
            raise ValueError('v4 ROOT metadata/DAG binding differs')
        for name,fields in FIELDS.items():
            tree=file.Get(name)
            if not tree or {str(b.GetName()) for b in tree.GetListOfBranches()}!=set(fields):
                raise ValueError('v4 ROOT direct branch domain differs: '+name)
            expected=_rows(value,name)
            count=0
            for count,row in enumerate(expected,1):
                if tree.GetEntry(count-1)<=0 or any(not _equal(field,kind,
                        getattr(tree,field),row[field]) for field,kind in
                        fields.items()):
                    raise ValueError('v4 ROOT direct/DAG value differs: '+name)
            if tree.GetEntries()!=count:
                raise ValueError('v4 ROOT direct row domain differs: '+name)
        if p.file_digest(path)!=expected_root_sha256:
            raise ValueError('v4 ROOT changed during cold verification')
        return value
    finally:file.Close()


def export(path,expected_root_sha256,expected_value_sha256,output_directory):
    """Regenerate binary64-safe tables solely from a cold v4 numerical ROOT."""
    value=read(path,expected_root_sha256,expected_value_sha256)
    target=Path(output_directory).absolute()
    if target.exists() or target.is_symlink():raise FileExistsError(target)
    target.mkdir(parents=True)
    try:
        with (target/'points.csv').open('x',newline='',encoding='utf-8') as stream:
            writer=csv.writer(stream)
            writer.writerow(('semantic_id','role_id','tune_id','quantity',
                'component','axis_id','bin_index','units','center_hex',
                'center_status','standard_error_hex','variance_hex',
                'uncertainty_status','reason_codes'))
            for item in value['points']:
                curve=item['key']['curve'];bins=item['key']['bins']
                writer.writerow((item['semantic_id'],curve['role_id'],
                    curve['tune_id'],curve['quantity'],curve['component'],
                    curve['axis_id'] or '',bins[0]['index'] if bins else '',
                    item['units'],item['center'] or '',item['center_status'],
                    item['standard_error'] or '',item['variance'] or '',
                    item['uncertainty_status'],p.canonical(item['reasons'])))
        with (target/'missing.csv').open('x',newline='',encoding='utf-8') as stream:
            writer=csv.writer(stream)
            writer.writerow(('semantic_id','center_status','uncertainty_status',
                             'reason_codes'))
            for item in value['points']:
                if item['center'] is None or item['standard_error'] is None:
                    writer.writerow((item['semantic_id'],item['center_status'],
                        item['uncertainty_status'],p.canonical(item['reasons'])))
        accounting=value['provenance']['campaign_accounting']
        with (target/'accounting.csv').open('x',newline='',encoding='utf-8') as stream:
            writer=csv.writer(stream)
            writer.writerow(('scope','tune_id','quantity','unit','value','status',
                             'reason_codes'))
            for item in value['provenance']['successful_events_by_tune']:
                writer.writerow(('SELECTED_ACCEPTED_QUERY_SOURCES',item['tune_id'],
                    'successful_events','event',item['count'],'AVAILABLE','[]'))
            for item in accounting['by_tune']:
                for quantity,unit in (('successful_events','event'),
                    ('submitted_attempts','job_attempt'),
                    ('accepted_attempts','job_attempt'),
                    ('discarded_attempts','job_attempt')):
                    writer.writerow((accounting['scope'],item['tune_id'],
                        quantity,unit,item[quantity],'AVAILABLE','[]'))
            for item in accounting['generator_event_trials_by_tune']:
                writer.writerow((item['scope'],item['tune_id'],
                    'generator_event_trials','event_trial',
                    '' if item['count'] is None else item['count'],
                    item['status'],p.canonical(item['reason_codes'])))
        with (target/'t1.csv').open('x',newline='',encoding='utf-8') as stream:
            writer=csv.writer(stream)
            writer.writerow(('semantic_id','tune_id','signed_pdg','component',
                'quantity','unit','value_hex','status','uncertainty_status'))
            for item in value['points']:
                curve=item['key']['curve']
                if curve['role_id']!='accounting.natural_final_heavy':continue
                writer.writerow((item['semantic_id'],curve['tune_id'],
                    curve['associate_pdg'],curve['component'],curve['quantity'],
                    item['units'],item['center'] or '',item['center_status'],
                    item['uncertainty_status']))
        with (target/'accounting.tex').open('x',encoding='utf-8') as stream:
            stream.write('\\begin{tabular}{llll}\nTune & Scope & Quantity & Value \\\\\n\\hline\n')
            for item in value['provenance']['successful_events_by_tune']:
                stream.write('{} & selected query & successful events & {} \\\\\n'.format(
                    item['tune_id'],item['count']))
            for item in accounting['by_tune']:
                for quantity,amount in (('successful events',
                    item['successful_events']),('submitted job attempts',
                    item['submitted_attempts']),('accepted job attempts',
                    item['accepted_attempts']),('discarded job attempts',
                    item['discarded_attempts'])):
                    stream.write('{} & accepted campaign ledger & {} & {} \\\\\n'.format(
                        item['tune_id'],quantity,amount))
            for item in accounting['generator_event_trials_by_tune']:
                stream.write('{} & all submitted attempts & generator event trials & {} \\\\\n'.format(
                    item['tune_id'],item['count'] if item['count'] is not None
                    else r'\textemdash{} (unavailable)'))
            stream.write('\\end{tabular}\n')
        with (target/'t1.tex').open('x',encoding='utf-8') as stream:
            stream.write('\\begin{tabular}{lllll}\nTune & Signed PDG & '
                'Constituent measure & Raw observed count & State \\\\\n\\hline\n')
            for item in value['points']:
                curve=item['key']['curve']
                if curve['role_id']!='accounting.natural_final_heavy' or \
                        curve['quantity']!='raw_count':continue
                observed=(r'\texttt{'+item['center']+'}' if item['center']
                          is not None else r'\textemdash{}')
                stream.write('{} & {} & {} & {} & {} \\\\\n'.format(
                    curve['tune_id'],curve['associate_pdg'],
                    curve['component'].replace('_',r'\_'),observed,
                    item['center_status'].replace('_',r'\_')))
            stream.write('\\end{tabular}\n')
        receipt=dict(schema='hadronization_v4_root_exports_v1',
            numerical_root_sha256=expected_root_sha256,
            value_sha256=expected_value_sha256,
            files={name:p.file_digest(target/name) for name in
                ('points.csv','missing.csv','accounting.csv','t1.csv',
                 'accounting.tex','t1.tex')})
        with (target/'receipt.json').open('x',encoding='ascii') as stream:
            stream.write(p.canonical(receipt)+'\n')
        return receipt
    except BaseException:
        for path in target.iterdir():path.unlink()
        target.rmdir()
        raise
