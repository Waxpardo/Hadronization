"""Authenticated A collection to bounded native numerical diagnostic bridge.

This is a development diagnostic, never a release DTO.  The ROOT collection,
source lineage, normalized request and analysis bytes are independently pinned
before any physical sparse scan or C++ evaluation.  Python only maps exact
natural keys to transport rows; it does not evaluate observable formulas.
"""
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

ROOT=Path(__file__).resolve().parents[2]

def _load(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module
    spec.loader.exec_module(module)
    return module

p=_load('native_runner_projection','pipeline/reduce/projection.py')
n=_load('native_runner_primitives','pipeline/reduce/native.py')

def sha(path):
    return p.file_digest(path)

def require_full_campaign_input(source,value):
    if not value['completion']['require_campaign_complete']:
        return
    if (source.index['layout']!='MERGED' or
            source.index['state']!='EXTERNAL_ACCEPTANCE_REQUIRED' or
            not source.index['shards'] or
            len(source.index['partitions'])!=len(source.index['tune_ordinals']) or
            set(source.index['tune_ordinals'])!=
                {'MONASH','JUNCTIONS','CLOSEPACKING'} or
            set(value['scope']['ordered_tunes'])!=
                {'MONASH','JUNCTIONS','CLOSEPACKING'}):
        raise ValueError('full paper result requires the authenticated complete MERGED three-tune A collection')


def native_point_query(request,source,path):
    """Serialize the exact requested natural domain, never a plot subset."""
    value=request.to_dict() if hasattr(request,'to_dict') else request
    typed=p.ProjectionRequest.from_dict(value,cold=True)
    require_full_campaign_input(source,value)
    if value['bindings']['expected_source_content_sha256'] != source.index['scientific_identity_sha256']:
        raise ValueError('native request/A collection scientific identity differs')
    axes={axis['id']:axis for axis in value['axes']}
    for required in ('nch','dphi','pt','eta','phi'):
        if required not in axes:
            raise ValueError('native requested axis is absent: '+required)
    if axes['nch']['edges'] != [p.hex64(i) for i in range(len(axes['nch']['edges']))]:
        raise ValueError('native activity axis is not the admitted integer domain')
    if axes['pt']['edges'] != list(map(p.hex64,n.G9_PT_EDGES)):
        raise ValueError('native G9 no-floor pT axis differs')
    classes=[]
    for klass in value['classes']:
        if klass['kind'] not in ('INTEGRATED','TUNE_LOCAL_PERCENTILE'):
            raise ValueError('native class kind is unsupported')
        low,high=map(p.number,klass['percentile_interval'])
        if low!=int(low) or high!=int(high):
            raise ValueError('native class percentile is not integer')
        classes.append((klass['id'],klass['kind']=='INTEGRATED',int(low),int(high)))
    lines=['hadronization_native_points_v1',
        'BIND\t{}\t{}\t{}'.format(source.expected_sha256,
            source.index['scientific_identity_sha256'],source.index['analysis_sha256']),
        'REQUEST\t{}\t{}'.format(typed.request_sha256,
                                  typed.scientific_request_sha256),
        'AXES\t{}\t{}\t{}'.format(len(axes['nch']['edges'])-1,
            len(axes['dphi']['edges'])-1,len(axes['pt']['edges'])-1)]
    for tune in value['scope']['ordered_tunes']:
        family=[member for member in value['sources']['members']
                if member['tune_id']==tune]
        if not family:
            raise ValueError('native source family is absent: '+tune)
        lines.append('FAMILY\t{}\t{}'.format(tune,p.digest(family)))
    for id_,integrated,low,high in classes:
        lines.append('CLASS\t{}\t{}\t{}\t{}'.format(id_,int(integrated),low,high))
    # The aggregate associate identity in a POINT is 0. Its exact signed
    # contributors are carried separately and bound by the request digest.
    for pair in value['scope']['ordered_associate_pairs']:
        lines.append('SIGN_ASSOCIATE\t{}\t{}\t{}\t{}'.format(
            pair['trigger_pdg'],pair['sector'],pair['sign'],
            pair['associate_pdg']))
    for index,key in enumerate(typed.expected_point_keys):
        curve=key['curve'];role=curve['role_id']
        if role not in p.PAPER_ROLE_IDS:
            raise ValueError('native requested role is unsupported: '+role)
        axis=curve['axis_id']
        if len(key['bins']) > 1 or (axis is None)!=(not key['bins']):
            raise ValueError('native point scalar/bin shape differs')
        component={'OS_MINUS_SS':'NET'}.get(curve['component'],curve['component'])
        row=['POINT',str(index),role,curve['quantity'],curve['tune_id'],
             curve['reference_tune_id'] or '-',curve['profile_id'] or '-',
             str(curve['class_id'] or 0),str(curve['trigger_pdg'] or 0),
             str(curve['associate_pdg'] or 0),str(curve['reference_pdg'] or 0),
             component,axis or '-',str(key['bins'][0]['index'] if key['bins'] else -1),
             'TEST_ONLY_DIAGNOSTIC']
        lines.append('\t'.join(row))
    lines.append('END')
    path=Path(path)
    if path.exists() or path.is_symlink():raise FileExistsError(path)
    with path.open('x',encoding='ascii',newline='\n') as stream:
        stream.write('\n'.join(lines)+'\n')
    return dict(path=str(path),sha256=sha(path),points=len(typed.expected_point_keys),
                request_sha256=typed.request_sha256,
                scientific_request_sha256=typed.scientific_request_sha256)

def compile_engine(work):
    work=Path(work);work.mkdir(parents=True,exist_ok=True)
    source=ROOT/'pipeline/reduce/native_engine.cpp'
    header=ROOT/'pipeline/reduce/statistics.hpp'
    identity=p.digest(dict(source=sha(source),statistics=sha(header),flags=[
        '-std=c++17','-O2','-Wall','-Wextra','-Wpedantic','-Werror','-ffp-contract=off']))
    binary=work/('native-engine-'+identity[:20])
    if not binary.exists():
        with tempfile.TemporaryDirectory(prefix='native-build-',dir=work) as directory:
            staged=Path(directory)/'engine'
            result=subprocess.run(['/usr/bin/c++','-std=c++17','-O2','-Wall',
                '-Wextra','-Wpedantic','-Werror','-ffp-contract=off',str(source),
                '-o',str(staged)],capture_output=True,text=True)
            if result.returncode or result.stdout or result.stderr:
                raise ValueError('native engine build failed: '+result.stdout+result.stderr)
            os.replace(staged,binary)
    return binary,dict(build_identity_sha256=identity,binary_sha256=sha(binary),
                       source_sha256=sha(source),statistics_sha256=sha(header))

def read_native_diagnostic(path,request):
    """Check C++ R/F rows against exact request/source-family identities."""
    value=request.to_dict() if hasattr(request,'to_dict') else request
    typed=p.ProjectionRequest.from_dict(value,cold=True)
    expected=typed.expected_point_keys
    families={tune:p.digest([member for member in value['sources']['members']
        if member['tune_id']==tune]) for tune in value['scope']['ordered_tunes']}
    def number(token):
        if token=='-':return None
        result=float.fromhex(token)
        if not math.isfinite(result):raise ValueError('native diagnostic is nonfinite')
        return result
    rows=[];factors={};boundaries=set()
    activity_axis=next(axis for axis in value['axes'] if axis['id']=='nch')
    activity_bins=len(activity_axis['edges'])-1
    with Path(path).open(encoding='ascii') as stream:
        if next(stream).rstrip('\n')!='hadronization_native_engine_diagnostic_v2':
            raise ValueError('native diagnostic output schema differs')
        ended=False;binding_seen=False
        for line in stream:
            line=line.rstrip('\n')
            if line=='END':
                if stream.read():raise ValueError('native diagnostic has trailing content')
                ended=True;break
            fields=line.split('\t')
            if fields[0]=='BIND':
                if binding_seen or fields!=['BIND',typed.request_sha256,
                                             typed.scientific_request_sha256]:
                    raise ValueError('native diagnostic request identity differs')
                binding_seen=True
            elif fields[0]=='R':
                if not binding_seen:
                    raise ValueError('native diagnostic request binding is absent')
                if len(fields)!=11 or int(fields[1])!=len(rows) or len(rows)>=len(expected):
                    raise ValueError('native result point order/width differs')
                center_status,uncertainty_status=fields[2],fields[4]
                if center_status not in ('AVAILABLE','UNDEFINED','UNSTABLE_DENOMINATOR') or \
                        uncertainty_status not in ('AVAILABLE','AVAILABLE_ZERO_DISPERSION',
                                                   'WITHHELD_UNCERTAINTY'):
                    raise ValueError('native diagnostic point status differs')
                center,variance,error=map(number,(fields[3],fields[5],fields[6]))
                if (center is None)!=(center_status=='UNDEFINED') or \
                        (variance is None)!=(uncertainty_status=='WITHHELD_UNCERTAINTY') or \
                        (error is None)!=(uncertainty_status=='WITHHELD_UNCERTAINTY'):
                    raise ValueError('native diagnostic center/error mask differs')
                source_leaves=[number(token) for token in fields[7].split(';')]
                reference_leaves=[] if fields[8]=='-' else [
                    number(token) for token in fields[8].split(';')]
                if len(source_leaves)!=10 or (reference_leaves and
                    len(reference_leaves)!=10):
                    raise ValueError('native diagnostic K10 leaves differ')
                rows.append(dict(key=expected[len(rows)],
                    semantic_id=p.semantic_id(typed,expected[len(rows)]),
                    center_status=center_status,center=center,
                    uncertainty_status=uncertainty_status,
                    variance=variance,standard_error=error,
                    source_leaves=source_leaves,reference_leaves=reference_leaves,
                    reason=fields[9],diagnostic_variance=number(fields[10])))
            elif fields[0]=='F':
                if len(fields)!=9:raise ValueError('native factor width differs')
                point_id,block=int(fields[1]),int(fields[4])
                if not 0<=point_id<len(rows) or not 1<=block<=10 or \
                        fields[5] not in ('0','1'):
                    raise ValueError('native factor point/block order differs')
                tune=fields[2]
                if tune not in families or fields[3]!=families[tune]:
                    raise ValueError('native factor source-family identity differs')
                key=(point_id,tune,block)
                if key in factors:raise ValueError('native factor duplicate block differs')
                leaf,mean,factor=map(number,fields[6:9])
                valid=fields[5]=='1'
                if (factor is None)==valid:
                    raise ValueError('native factor validity mask differs')
                factors[key]=dict(valid=valid,leaf=leaf,leave_mean=mean,
                                  centered_factor=factor)
            elif fields[0]=='Q':
                if len(fields)!=10 or fields[1] not in families or \
                        fields[2]!=families[fields[1]]:
                    raise ValueError('native class boundary family/width differs')
                boundary=(fields[1],int(fields[3]),int(fields[4]))
                if boundary in boundaries:raise ValueError('native class boundary duplicates')
                if fields[3] not in {str(item['id']) for item in value['classes']} or \
                        not 0<=boundary[2]<=10 or fields[5] not in \
                        ('RESOLVED','UNRESOLVED') or fields[8] not in ('0','1'):
                    raise ValueError('native class boundary domain/status differs')
                weight=number(fields[9])
                if fields[5]=='RESOLVED':
                    low,high=int(fields[6]),int(fields[7])
                    if not 0<=low<=activity_bins or not -1<=high<activity_bins or \
                            (low>high and fields[8]!='1') or weight is None or \
                            (fields[8]=='1' and weight!=0.0) or \
                            (fields[8]=='0' and weight<=0.0):
                        raise ValueError('native class boundary range/weight differs')
                elif fields[6:8]!=['-','-'] or fields[8]!='1' or weight is not None:
                    raise ValueError('native unresolved class boundary payload differs')
                boundaries.add(boundary)
            else:raise ValueError('native diagnostic record differs')
    if not ended or not binding_seen or len(rows)!=len(expected):
        raise ValueError('native diagnostic point completion differs')
    for index,row in enumerate(rows):
        curve=row['key']['curve'];tunes=[curve['tune_id']]
        if curve['reference_tune_id'] is not None:tunes.append(curve['reference_tune_id'])
        if len(set(tunes))!=len(tunes):
            raise ValueError('native point compares a tune to itself')
        for tune in tunes:
            family=[factors.get((index,tune,block)) for block in range(1,11)]
            if any(item is None for item in family):
                raise ValueError('native point factor family/block is incomplete')
            expected_leaves=(row['source_leaves'] if tune==tunes[0]
                             else row['reference_leaves'])
            if [item['leaf'] for item in family]!=expected_leaves:
                raise ValueError('native factor/point leaves differ')
            expected_valid=row['variance'] is not None
            if any(item['valid']!=expected_valid for item in family):
                raise ValueError('native factor/point validity differs')
            if expected_valid:
                mean=sum(expected_leaves)/10.
                if any(not math.isclose(item['leave_mean'],mean,rel_tol=1e-12,
                                        abs_tol=1e-30) for item in family):
                    raise ValueError('native factor leave mean differs')
        if row['variance'] is not None:
            recovered=sum(item['centered_factor']**2
                for tune in tunes for block in range(1,11)
                for item in [factors[index,tune,block]])
            if not math.isclose(recovered,row['variance'],rel_tol=1e-12,
                                abs_tol=1e-30) or not math.isclose(
                    math.sqrt(row['variance']),row['standard_error'],
                    rel_tol=1e-12,abs_tol=1e-30):
                raise ValueError('native factor/variance/error differs')
    if len(factors)!=sum(10*(1+int(row['key']['curve'][
            'reference_tune_id'] is not None)) for row in rows):
        raise ValueError('native factor domain has foreign rows')
    expected_boundaries={(tune,klass['id'],omit)
        for tune in value['scope']['ordered_tunes'] for klass in value['classes']
        for omit in range(11)}
    if boundaries!=expected_boundaries:
        raise ValueError('native class boundary domain differs')
    return rows,factors

def verify_native_diagnostic_stream(path,request):
    """Bounded-memory exact R/F verification for the full natural domain."""
    typed=(request if isinstance(request,p.ProjectionRequest) else
           p.ProjectionRequest.from_dict(
               request.to_dict() if hasattr(request,'to_dict') else request,
               cold=True))
    value=typed.to_dict();expected=typed.expected_point_keys
    families={tune:p.digest([member for member in value['sources']['members']
        if member['tune_id']==tune]) for tune in value['scope']['ordered_tunes']}
    def number(token):
        if token=='-':return None
        result=float.fromhex(token)
        if not math.isfinite(result):raise ValueError('native diagnostic is nonfinite')
        return result
    counts=dict(points=0,factors=0,boundaries=0,available_errors=0,
                withheld_errors=0)
    with Path(path).open(encoding='ascii') as stream:
        if next(stream).rstrip('\n')!='hadronization_native_engine_diagnostic_v2':
            raise ValueError('native diagnostic output schema differs')
        if next(stream).rstrip('\n').split('\t')!=['BIND',typed.request_sha256,
                                                   typed.scientific_request_sha256]:
            raise ValueError('native diagnostic request identity differs')
        for index,key in enumerate(expected):
            row=next(stream).rstrip('\n').split('\t')
            if len(row)!=11 or row[:2]!=['R',str(index)]:
                raise ValueError('native result point order/width differs')
            if row[2] not in ('AVAILABLE','UNDEFINED','UNSTABLE_DENOMINATOR') or \
                    row[4] not in ('AVAILABLE','AVAILABLE_ZERO_DISPERSION',
                                   'WITHHELD_UNCERTAINTY'):
                raise ValueError('native diagnostic point status differs')
            center,variance,error=map(number,(row[3],row[5],row[6]))
            active=row[4]!='WITHHELD_UNCERTAINTY'
            if (center is None)!=(row[2]=='UNDEFINED') or \
                    active!=(variance is not None and error is not None):
                raise ValueError('native diagnostic center/error mask differs')
            tunes=[key['curve']['tune_id']]
            if key['curve']['reference_tune_id'] is not None:
                tunes.append(key['curve']['reference_tune_id'])
            if len(tunes)!=len(set(tunes)):
                raise ValueError('native point compares a tune to itself')
            leaf_sets=[row[7],row[8]]
            recovered=0.0
            for slot,tune in enumerate(tunes):
                declared=[number(token) for token in leaf_sets[slot].split(';')]
                if len(declared)!=10:
                    raise ValueError('native diagnostic K10 leaves differ')
                factors=[];means=[]
                for block in range(1,11):
                    field=next(stream).rstrip('\n').split('\t')
                    if len(field)!=9 or field[:6]!=['F',str(index),tune,
                                families[tune],str(block),str(int(active))]:
                        raise ValueError('native factor point/family/block identity differs')
                    leaf,mean,factor=map(number,field[6:9])
                    if leaf!=declared[block-1] or (factor is None)==active:
                        raise ValueError('native factor leaf/validity differs')
                    means.append(mean);factors.append(factor)
                if active:
                    expected_mean=sum(declared)/10.0
                    if any(not math.isclose(mean,expected_mean,rel_tol=1e-12,
                                            abs_tol=1e-30) for mean in means):
                        raise ValueError('native factor leave mean differs')
                    recovered+=sum(factor*factor for factor in factors)
                counts['factors']+=10
            if len(tunes)==1 and row[8]!='-':
                raise ValueError('native absolute point has foreign reference leaves')
            if active:
                if not math.isclose(recovered,variance,rel_tol=1e-12,
                                    abs_tol=1e-30) or not math.isclose(
                        math.sqrt(variance),error,rel_tol=1e-12,abs_tol=1e-30):
                    raise ValueError('native factor/variance/error differs')
                counts['available_errors']+=1
            else:counts['withheld_errors']+=1
            counts['points']+=1
        activity_bins=len(next(axis for axis in value['axes']
            if axis['id']=='nch')['edges'])-1
        for tune in sorted(value['scope']['ordered_tunes']):
            for klass in sorted(value['classes'],key=lambda item:item['id']):
                for omit in range(11):
                    field=next(stream).rstrip('\n').split('\t')
                    if len(field)!=10 or field[:5]!=['Q',tune,families[tune],
                                                     str(klass['id']),str(omit)] or \
                            field[5] not in ('RESOLVED','UNRESOLVED') or \
                            field[8] not in ('0','1'):
                        raise ValueError('native class boundary identity/status differs')
                    weight=number(field[9])
                    if field[5]=='RESOLVED':
                        low,high=int(field[6]),int(field[7])
                        if not 0<=low<=activity_bins or not -1<=high<activity_bins or \
                                (low>high and field[8]!='1') or weight is None or \
                                (field[8]=='1' and weight!=0.0) or \
                                (field[8]=='0' and weight<=0.0):
                            raise ValueError('native class boundary range/weight differs')
                    elif field[6:8]!=['-','-'] or field[8]!='1' or weight is not None:
                        raise ValueError('native unresolved class boundary payload differs')
                    counts['boundaries']+=1
        if next(stream).rstrip('\n')!='END' or stream.read():
            raise ValueError('native diagnostic trailing/foreign row differs')
    return counts


def verify_native_block_primitives_stream(path,request,event_moments):
    """Authenticate every pooled point/tune/block additive component row."""
    typed=(request if isinstance(request,p.ProjectionRequest) else
           p.ProjectionRequest.from_dict(request.to_dict() if hasattr(
               request,'to_dict') else request,cold=True))
    value=typed.to_dict()
    families={tune:p.digest([member for member in value['sources']['members']
        if member['tune_id']==tune]) for tune in value['scope']['ordered_tunes']}
    def ids(key):
        role=key['curve']['role_id']
        if role=='multiplicity.composite':return ['activity_bin','activity_total']
        if role=='spectra.signed_heavy':return ['g9_bin','g9_total']
        if role=='accounting.natural_final_heavy':
            return ['natural_count','natural_weighted_sum','event_exposure']
        result=['pair_os','pair_ss','trigger']
        if role=='balancing.baryon_meson.activity':
            result.extend(('reference_pair_os','reference_pair_ss'))
        return result
    counts=dict(rows=0,unresolved=0)
    with Path(path).open(encoding='ascii') as stream:
        if next(stream).rstrip('\n')!='hadronization_native_block_primitives_v1' or \
                next(stream).rstrip('\n').split('\t')!=['BIND',typed.request_sha256,
                    typed.scientific_request_sha256]:
            raise ValueError('native point primitive schema/request binding differs')
        for point_id,key in enumerate(typed.expected_point_keys):
            tunes=[key['curve']['tune_id']]
            if key['curve']['reference_tune_id'] is not None:
                tunes.append(key['curve']['reference_tune_id'])
            for tune in tunes:
                for block in range(1,11):
                    fields=next(stream).rstrip('\n').split('\t')
                    moment=event_moments.get((tune,block))
                    if len(fields)!=9 or fields[:6]!=['B',str(point_id),tune,
                            families[tune],str(block),str(moment.events if moment else -1)] or \
                            fields[6] not in ('AVAILABLE','UNDEFINED'):
                        raise ValueError('native point primitive block/source identity differs')
                    if fields[6]=='UNDEFINED':
                        if fields[7:]!=['-','-'] or key['curve']['role_id'] in (
                                'multiplicity.composite','spectra.signed_heavy',
                                'accounting.natural_final_heavy'):
                            raise ValueError('native undefined primitive payload differs')
                        counts['unresolved']+=1
                    else:
                        if fields[7].split(';')!=ids(key):
                            raise ValueError('native primitive component semantic domain differs')
                        values=[float.fromhex(token) for token in fields[8].split(';')]
                        if len(values)!=len(ids(key)) or not all(map(math.isfinite,values)):
                            raise ValueError('native primitive component values differ')
                        if key['curve']['role_id']=='multiplicity.composite' and \
                                not math.isclose(values[1],moment.sumw,rel_tol=1e-12,
                                                 abs_tol=1e-12):
                            raise ValueError('native P1 block total differs from exact events')
                        if key['curve']['role_id']=='accounting.natural_final_heavy' and \
                                values[2]!=moment.events:
                            raise ValueError('native T1 exposure differs from exact events')
                    counts['rows']+=1
        if next(stream).rstrip('\n')!='END' or stream.read():
            raise ValueError('native point primitive trailing/foreign row differs')
    return counts


def verify_native_denominator_stream(path,request,event_moments,block_path=None):
    """Check all semantic parent names and pooled/deletion validity states."""
    typed=(request if isinstance(request,p.ProjectionRequest) else
           p.ProjectionRequest.from_dict(request.to_dict() if hasattr(
               request,'to_dict') else request,cold=True))
    counts=dict(rows=0,undefined=0,unstable=0)
    def decoded(token,status):
        if status not in ('AVAILABLE','UNDEFINED','UNSTABLE_DENOMINATOR'):
            raise ValueError('native denominator status differs')
        value=None if token=='-' else float.fromhex(token)
        if value is not None and not math.isfinite(value):
            raise ValueError('native denominator value is nonfinite')
        if (value is None)!=(status=='UNDEFINED') or \
                (value==0.0)!=(status=='UNSTABLE_DENOMINATOR'):
            raise ValueError('native denominator status/value mask differs')
        return value
    def pooled_from_blocks(key,name,blocks,omit=0):
        curve=key['curve'];role=curve['role_id']
        reference=name.startswith('reference_') and name!='reference_os_minus_ss'
        tune=curve['reference_tune_id'] if reference else curve['tune_id']
        rows=[row for block,row in enumerate(blocks[tune],1) if block!=omit]
        if any(row is None for row in rows):return None
        def total(component):return sum(row[component] for row in rows)
        if name in ('normalization_total','source_normalization_total',
                    'reference_normalization_total'):
            return total('activity_total' if role=='multiplicity.composite'
                         else 'g9_total')
        if name=='accepted_event_exposure':return total('event_exposure')
        if name in ('trigger','shared_trigger','source_shared_trigger',
                    'reference_shared_trigger'):return total('trigger')
        if name in ('reference_os_minus_ss','source_meson_os_minus_ss',
                    'reference_meson_os_minus_ss'):
            return total('reference_pair_os')-total('reference_pair_ss')
        if name=='reference_tune_numerator_os_minus_ss':
            return total('pair_os')-total('pair_ss')
        if name.startswith('reference_tune_bin_'):
            numerator=total('activity_bin' if role=='multiplicity.composite'
                            else 'g9_bin')
            denominator=total('activity_total' if role=='multiplicity.composite'
                              else 'g9_total')
            return numerator/denominator if denominator else None
        if name.startswith('reference_tune_'):
            denominator=total('trigger')
            if not denominator:return None
            component=curve['component']
            numerator=(total('pair_os') if component=='OS' else
                       total('pair_ss') if component=='SS' else
                       total('pair_os')-total('pair_ss'))
            return numerator/denominator
        raise ValueError('native denominator parent checker lacks formula: '+name)
    block_stream=Path(block_path).open(encoding='ascii') if block_path else None
    try:
      if block_stream:
        if next(block_stream).rstrip('\n')!='hadronization_native_block_primitives_v1' or \
                next(block_stream).rstrip('\n').split('\t')!=['BIND',typed.request_sha256,
                    typed.scientific_request_sha256]:
            raise ValueError('native denominator block cross-check binding differs')
      with Path(path).open(encoding='ascii') as stream:
        if next(stream).rstrip('\n')!='hadronization_native_denominator_parents_v1' or \
                next(stream).rstrip('\n').split('\t')!=['BIND',typed.request_sha256,
                    typed.scientific_request_sha256]:
            raise ValueError('native denominator schema/request binding differs')
        for point_id,key in enumerate(typed.expected_point_keys):
            blocks={}
            if block_stream:
                tunes=[key['curve']['tune_id']]
                if key['curve']['reference_tune_id'] is not None:
                    tunes.append(key['curve']['reference_tune_id'])
                for tune in tunes:
                    entries=[]
                    for block in range(1,11):
                        field=next(block_stream).rstrip('\n').split('\t')
                        if len(field)!=9 or field[:3]!=['B',str(point_id),tune] or \
                                field[4]!=str(block):
                            raise ValueError('native denominator block cross-check order differs')
                        entries.append(None if field[6]=='UNDEFINED' else dict(zip(
                            field[7].split(';'),[float.fromhex(token) for token
                                                in field[8].split(';')])))
                    blocks[tune]=entries
            for name,retained in p.expected_denominator_parents(key):
                fields=next(stream).rstrip('\n').split('\t')
                if len(fields)!=8 or fields[:4]!=['D',str(point_id),name,
                                                  str(int(retained))]:
                    raise ValueError('native denominator semantic parent order differs')
                pooled=decoded(fields[5],fields[4])
                statuses=fields[6].split(';');tokens=fields[7].split(';')
                if len(statuses)!=10 or len(tokens)!=10:
                    raise ValueError('native denominator K10 leaf domain differs')
                leaves=[decoded(token,status) for token,status in zip(
                    tokens,statuses)]
                if block_stream:
                    expected=pooled_from_blocks(key,name,blocks)
                    if (expected is None)!=(pooled is None) or \
                            (expected is not None and not math.isclose(
                                expected,pooled,rel_tol=1e-12,abs_tol=1e-12)):
                        raise ValueError('native denominator pooled primitive algebra differs')
                    if key['curve']['role_id'] in (
                            'multiplicity.composite','spectra.signed_heavy',
                            'accounting.natural_final_heavy'):
                        for block,leaf in enumerate(leaves,1):
                            expected_leaf=pooled_from_blocks(key,name,blocks,block)
                            if (expected_leaf is None)!=(leaf is None) or \
                                    (expected_leaf is not None and not math.isclose(
                                        expected_leaf,leaf,rel_tol=1e-12,
                                        abs_tol=1e-12)):
                                raise ValueError('native denominator retained primitive algebra differs')
                if name=='accepted_event_exposure':
                    tune=key['curve']['tune_id']
                    exposures=[event_moments[tune,block].events
                               for block in range(1,11)]
                    if pooled!=sum(exposures) or leaves!=[
                            sum(exposures)-exposures[block-1]
                            for block in range(1,11)]:
                        raise ValueError('native denominator event exposure differs')
                if name=='normalization_total' and key['curve']['role_id']==\
                        'multiplicity.composite':
                    tune=key['curve']['tune_id']
                    weights=[event_moments[tune,block].sumw
                             for block in range(1,11)]
                    if pooled is None or not math.isclose(pooled,sum(weights),
                            rel_tol=1e-12,abs_tol=1e-12):
                        raise ValueError('native P1 denominator differs from exact events')
                counts['undefined']+=int(pooled is None)
                counts['unstable']+=int(fields[4]=='UNSTABLE_DENOMINATOR')
                counts['rows']+=1
        if next(stream).rstrip('\n')!='END' or stream.read():
            raise ValueError('native denominator trailing/foreign row differs')
      if block_stream and (next(block_stream).rstrip('\n')!='END' or
                           block_stream.read()):
        raise ValueError('native denominator block cross-check completion differs')
    finally:
      if block_stream:block_stream.close()
    return counts

def run_diagnostic(index_path,index_sha256,analysis_path,analysis_sha256,
                   request,work,collection_api=None,model_api=None,*,
                   selected_tunes=None,selection=None):
    """One authenticated sparse/T1 scan and source-bound C++ diagnostic run."""
    started=time.perf_counter()
    work=Path(work).absolute();work.mkdir(parents=True,exist_ok=True)
    if collection_api is None:collection_api=_load('native_runner_collection','pipeline/query/collection.py')
    if model_api is None:model_api=_load('native_runner_model','pipeline/query/model.py')
    source=n.NativeCollection(index_path,index_sha256,collection_api)
    if sha(analysis_path)!=analysis_sha256:
        raise ValueError('native requested analysis bytes differ from pin')
    analysis,validated_sha=model_api.checked_analysis(Path(analysis_path))
    if validated_sha!=analysis_sha256:
        raise ValueError('A normalized analysis digest differs')
    construction_path=Path(source.index['shards'][0]['workspace_manifest']['path']).parent/'analysis.json'
    if sha(construction_path)!=source.index['analysis_sha256']:
        raise ValueError('query construction analysis bytes/index binding differs')
    construction,construction_sha=model_api.checked_analysis(construction_path)
    if construction_sha!=source.index['analysis_sha256']:
        raise ValueError('query construction normalized model differs')
    compatibility=model_api.compatible_interpretation(construction,analysis)
    support_prepared=None;pre_support_seconds=0.0
    if request is None:
        if selected_tunes is None or selection is None:
            raise ValueError('direct native paper request requires tune and science scope')
        selected_tunes=list(selected_tunes)
        if not selected_tunes or len(selected_tunes)!=len(set(selected_tunes)) or \
                set(selected_tunes)-set(source.index['tune_ordinals']):
            raise ValueError('direct native paper tune scope differs')
        selected_activity=next((item for item in analysis['activities']
            if item['id']==selection['activity_id']),None)
        if selected_activity is None:
            raise ValueError('direct native requested activity is absent')
        before_support=time.perf_counter()
        support_prepared=n.collect_t1(source,selected_tunes,None,
            row_upper_bounds=True,event_activity_field=selected_activity[
                'physical_field'],include_diagnostics=True,
            work_root=work/'support-scan')
        pre_support_seconds=time.perf_counter()-before_support
        species=sorted({key[2] for key in support_prepared[0]})
        request=p.make_native_request(source,analysis_path,analysis_sha256,
                                      selected_tunes,species,selection)
    value=request.to_dict() if hasattr(request,'to_dict') else request
    typed=p.ProjectionRequest.from_dict(value,cold=True)
    require_full_campaign_input(source,value)
    request_path=work/'native-request.json'
    if request_path.exists() or request_path.is_symlink():
        raise FileExistsError(request_path)
    with request_path.open('x',encoding='ascii',newline='\n') as stream:
        stream.write(p.canonical(typed.to_dict())+'\n')
    tunes=value['scope']['ordered_tunes']
    lineage=source.source_lineage(tunes)
    admitted=time.perf_counter()
    if value['sources']!=lineage['source_selection']:
        raise ValueError('native request/A source lineage differs')
    if value['bindings']['analysis_config_sha256']!=analysis_sha256:
        raise ValueError('native request analysis binding differs')
    if value['bindings']['expected_source_content_sha256']!=source.index['scientific_identity_sha256']:
        raise ValueError('native request/A science binding differs')
    source_profiles={item['id']:item for item in analysis['profiles']}
    selected_profiles=[]
    eta=analysis['pair_acceptance']['eta']['value']
    for profile in value['profiles']:
        original=source_profiles.get(profile['id'])
        if original is None or profile!=p.normalized_profile(original,eta,
                value['science_contract']['structural_registry_sha256']):
            raise ValueError('native requested profile differs from A normalized model')
        selected_profiles.append(profile['id'])
    activity=next((item for item in analysis['activities']
        if p.normalized_activity(item)==value['activity']),None)
    if activity is None:
        raise ValueError('native requested activity differs from A normalized model')
    expected_classes=[[analysis['integrated_interval'][0],analysis['integrated_interval'][1]]]+analysis['percentile_intervals']
    if [list(map(p.number,item['percentile_interval'])) for item in value['classes']] != expected_classes:
        raise ValueError('native requested classes differ from pinned analysis recipe')
    registered={
        (item['trigger_pdg'],item['associate_pdg']):(
            item['reference_meson_pdg'],
            'OS' if item['sign']==-1 else 'SS',item['sector'].upper())
        for item in model_api.state_registry(analysis)[1]
        if item['trigger_pdg'] in value['scope']['ordered_triggers']}
    scoped={
        (item['trigger_pdg'],item['associate_pdg']):(
            item['reference_meson_pdg'],item['sign'],item['sector'])
        for item in value['scope']['ordered_associate_pairs']}
    if scoped != registered:
        raise ValueError('native signed associate domain differs from A registry')
    pairs=set(scoped)
    roles={item['role_id']:item for item in value['scope']['roles']}
    g9=p.g9_science(value)
    axes={axis['id']:axis for axis in value['axes']}
    boundary_axes={axis:list(map(p.number,axes[axis]['edges']))
                   for axis in ('pt','eta','phi')}
    primitives=n.collect_primitives(source,model_api,analysis,selected_profiles,
        activity['physical_field'],value['scope']['ordered_triggers'],pairs,tunes)
    sparse_primitives_done=time.perf_counter()
    if support_prepared is None:
        t1,events,support_opens,support_upper,event_moments,raw_diagnostics=n.collect_t1(
            source,tunes,None,row_upper_bounds=True,
            event_activity_field=activity['physical_field'],include_diagnostics=True,
            work_root=work/'support-scan')
    else:
        t1,events,support_opens,support_upper,event_moments,raw_diagnostics=support_prepared
    support_done=time.perf_counter()
    selected_t1={curve['associate_pdg'] for curve in
        roles['accounting.natural_final_heavy']['required_curve_keys']}
    if selected_t1-set(key[2] for key in t1):
        raise ValueError('native requested T1 species lacks observed natural support')
    t1={key:row for key,row in t1.items() if key[2] in selected_t1}
    g9_cells=n.collect_g9(source,g9['signed_species_pdgs'],
        boundary_axes['eta'],boundary_axes['phi'],tunes)
    g9_done=time.perf_counter()
    primitive_path=work/'native-primitives.tsv'
    primitive_receipt=n.write_native_transport(source,primitives,g9_cells,t1,
                                               events,primitive_path,support_upper,tunes)
    query_path=work/'native-points.tsv'
    query_receipt=native_point_query(typed,source,query_path)
    binary,build=compile_engine(work/'build')
    output=work/'native-diagnostic.tsv'
    block_output=work/'native-block-primitives.tsv'
    denominator_output=work/'native-denominator-parents.tsv'
    if output.exists() or output.is_symlink() or block_output.exists() or \
            block_output.is_symlink() or denominator_output.exists() or \
            denominator_output.is_symlink():
        raise FileExistsError('native numerical output')
    result=subprocess.run([str(binary),str(primitive_path),index_sha256,
        str(query_path),str(output),str(block_output),str(denominator_output)],
        capture_output=True,text=True)
    if result.returncode or result.stdout or result.stderr:
        raise ValueError('native diagnostic failed: '+result.stdout+result.stderr)
    checked=verify_native_diagnostic_stream(output,typed)
    checked_blocks=verify_native_block_primitives_stream(block_output,typed,
                                                          event_moments)
    checked_denominators=verify_native_denominator_stream(denominator_output,
                                                          typed,event_moments,
                                                          block_output)
    finished=time.perf_counter()
    scratch_bytes=sum(path.stat().st_size for path in
        (primitive_path,query_path,output,block_output,denominator_output))
    return dict(schema='hadronization_native_diagnostic_run_v1',
        collection_index_sha256=index_sha256,
        collection_scientific_identity_sha256=source.index['scientific_identity_sha256'],
        lineage_selected_members_sha256=lineage['source_selection']['selected_members_sha256'],
        analyzed_source_scientific_content_digests=lineage['analyzed_source_scientific_content_digests'],
        request_sha256=typed.request_sha256,
        scientific_request_sha256=typed.scientific_request_sha256,
        interpretation_analysis_sha256=analysis_sha256,
        construction_analysis_sha256=source.index['analysis_sha256'],
        interpretation_compatibility=compatibility,
        request_path=str(request_path),request_file_sha256=sha(request_path),
        primitive_transport=primitive_receipt,primitive_transport_sha256=sha(primitive_path),
        point_transport=query_receipt,
        diagnostic_path=str(output),diagnostic_sha256=sha(output),
        block_primitive_path=str(block_output),
        block_primitive_sha256=sha(block_output),
        checked_block_primitive_rows=checked_blocks['rows'],
        unresolved_block_primitive_rows=checked_blocks['unresolved'],
        denominator_path=str(denominator_output),
        denominator_sha256=sha(denominator_output),
        checked_denominator_rows=checked_denominators['rows'],
        denominator_status_counts={key:checked_denominators[key]
            for key in ('undefined','unstable')},
        checked_points=checked['points'],checked_factor_rows=checked['factors'],
        checked_boundary_rows=checked['boundaries'],
        checked_status_counts={key:checked[key] for key in
            ('available_errors','withheld_errors')},
        sparse_scan_metrics=dict(primitives=vars(primitives.metrics),g9=vars(g9_cells.metrics)),
        support_root_opens=support_opens,support_row_upper_bounds=support_upper,
        event_block_moments=[dict(tune_id=tune,block_id=block,**moment.report())
            for (tune,block),moment in sorted(event_moments.items())],
        raw_origin_closure_diagnostics=[dict(tune_id=tune,block_id=block,
            **raw_diagnostics.get((tune,block),n.RawDiagnostics()).report())
            for tune,block in sorted(event_moments)],
        wall_seconds=dict(total=finished-started,admission=admitted-started,
            request_support=pre_support_seconds,
            sparse_primitives=sparse_primitives_done-admitted,
            support=support_done-sparse_primitives_done,
            g9=g9_done-support_done,engine=finished-g9_done),
        scratch_transport_bytes=scratch_bytes,
        build=build)
