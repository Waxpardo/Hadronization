"""Self-contained ROOT serialization of versioned scientific results.

No formula is evaluated here. A typed, deduplicated value DAG preserves every
contract field; ordinary points/block_values/covariance_factors TTrees expose
the numerical values directly. A cold reader reconstructs the exact DTO from
ROOT and verifies those independent typed views before admitting it.
"""
import argparse
import importlib.util
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[2]
_spec=importlib.util.spec_from_file_location('archive_projection',ROOT/'pipeline/reduce/projection.py')
p=importlib.util.module_from_spec(_spec);sys.modules[_spec.name]=p;_spec.loader.exec_module(p)
r=p._reducer()
SCHEMA='hadronization_self_contained_typed_root_v1'

def encode(value): return str(value).encode('utf-8').hex() or '-'
def decode(value): return bytes.fromhex(value).decode('utf-8') if value!='-' else ''
def numeric(value): return float.fromhex(value).hex() if value is not None else float(0).hex()

def build(work):
    work=Path(work).absolute();r.reject_symlink_components(work,'archive work')
    runtime=r.runtime_module().resolve(require_root=True);env=os.environ.copy();env.update(runtime['environment'])
    flags=['-std=c++17','-O2','-Wall','-Wextra','-Wpedantic','-Werror','-ffp-contract=off']
    cflags=r.command_tokens(env['ROOT_CONFIG'],'--cflags',env);libs=r.command_tokens(env['ROOT_CONFIG'],'--libs',env)
    identity=dict(schema=SCHEMA,source_sha256=p.file_digest(ROOT/'pipeline/reduce/archive.cpp'),
                  compiler=env['CXX'],runtime=runtime['diagnostics'],flags=flags+cflags,link_flags=libs)
    build_id=p.digest(identity);directory=work/'bin';directory.mkdir(parents=True,exist_ok=True)
    binary=directory/('archive-'+build_id[:20]);receipt=binary.with_suffix('.build.json')
    with r.build_lock(binary.with_suffix('.lock')):
        if r.cached_build(binary,receipt,identity) is None:
            with tempfile.TemporaryDirectory(prefix='archive-build-',dir=str(work)) as temporary:
                staged=Path(temporary)/'archive'
                result=subprocess.run([env['CXX']]+flags+[str(ROOT/'pipeline/reduce/archive.cpp')]+cflags+libs+['-o',str(staged)],env=env,capture_output=True,text=True)
                if result.returncode or result.stdout or result.stderr:raise ValueError('archive build failed: '+result.stdout+result.stderr)
                os.replace(str(staged),str(binary))
            r.atomic_json(receipt,dict(schema=SCHEMA+'_build',build_id=build_id,build_identity=identity,binary_sha256=p.file_digest(binary)),exclusive=False)
    return env,binary,r.json_file(receipt)

def execute(binary,env,operation,source,output):
    result=subprocess.run([str(binary),operation,str(source),str(output)],env=env,capture_output=True,text=True)
    if result.returncode or result.stdout or result.stderr:raise ValueError('archive '+operation+' failed: '+result.stdout+result.stderr)

def checked(value, *, cold=False):
    if value.get('schema') in (p.RESULT_SCHEMA,p.RESULT_SCHEMA_G9,
                               p.RESULT_SCHEMA_NATIVE):
        request=p.ProjectionRequest.from_dict(value['request_echo'],cold=cold)
        p.ProjectionResult.from_dict(value,request,value['primitive_routes'],cold=cold)
    else:
        raise ValueError('unsupported ROOT archive payload schema')
    return value

def nodes(value,stream):
    """Hash-cons structural nodes, without retaining repeated JSON strings."""
    intern={}
    def visit(v):
        if v is None:kind,text,children,keys='N','',(),()
        elif type(v) is bool:kind,text,children,keys='B',str(int(v)),(),()
        elif type(v) is int:kind,text,children,keys='I',str(v),(),()
        elif type(v) is float:
            if not math.isfinite(v):raise ValueError('nonfinite archive scalar')
            kind,text,children,keys='F',v.hex(),(),()
        elif type(v) is str:kind,text,children,keys='S',v,(),()
        elif type(v) is list:kind,text,children,keys='A','',tuple(visit(x) for x in v),()
        elif type(v) is dict:
            keys=tuple(sorted(v));kind,text,children='O','',tuple(visit(v[k]) for k in keys)
        else:raise ValueError('unsupported archive value')
        key=(kind,text,children,keys)
        if key in intern:return intern[key]
        identity=len(intern);intern[key]=identity
        stream.write('\t'.join(['N',str(identity),kind,encode(text),','.join(map(str,children)) or '-',','.join(map(encode,keys)) or '-'])+'\n')
        return identity
    return visit(value)

def binding_records(value):
    request=value['request_echo'];provenance=value['provenance'];artifact=value['artifact_binding']
    query=provenance['query_source_sha256']
    yield '\t'.join(['H',encode(value['schema']),encode(value['request_sha256']),
        encode(value['scientific_request_sha256']),encode(value['science_content_sha256']),
        encode(value['package_state']),encode(value['campaign_state']),
        encode(request['sources']['campaign_descriptor_sha256']),
        encode(request['sources']['selected_members_sha256']),
        encode(provenance['source_members_sha256']),encode(provenance['analysis_config_sha256']),
        encode(provenance['particle_registry_sha256']),encode(provenance['activity_definition_sha256']),
        encode(provenance['selection_definitions_sha256']),encode(provenance['formula_source_sha256']),
        encode(provenance['statistics_source_sha256']),str(int(query is not None)),encode(query or ''),
        encode(provenance['uncertainty_scope']),encode(artifact['root_sha256']),str(artifact['root_bytes']),
        encode(artifact['root_content_sha256']),encode(artifact['manifest_sha256']),
        encode(artifact['source_fileset_sha256'])])

def g9_records(value):
    if value['schema']==p.RESULT_SCHEMA_G9:
        metadata=value['resolved']['g9_science']
        yield '\t'.join(['M',encode(p.canonical(metadata)),encode(p.digest(metadata))])

def point_records(value):
    for index,point in enumerate(value.get('points',[])):
        c=point['key']['curve'];bins=point['key']['bins'];b=bins[0] if bins else None
        if len(bins)>1:
            raise ValueError('typed numerical point bin domain is not directly representable')
        fields=['P',str(index)]+[encode(x or '') for x in [point['semantic_id'],p.digest(point['key']),c['role_id'],c['tune_id'],c['reference_tune_id'],c['profile_id'],c['activity_id']]]
        fields += [str(c['class_id'] if c['class_id'] is not None else -1)]+[str(c[n] or 0) for n in ['trigger_pdg','associate_pdg','reference_pdg']]
        fields += [encode(c[n] or '') for n in ['quantity','component','axis_id']]
        fields += [str(b['index'] if b else -1),numeric(b['low'] if b else None),numeric(b['high'] if b else None)]
        fields += [encode(point['units'])]
        fields += [str(int(point['center'] is not None)),numeric(point['center']),encode(point['center_status']),
                   str(int(point['standard_error'] is not None)),numeric(point['standard_error']),encode(point['uncertainty_status']),
                   str(int(point['variance'] is not None)),numeric(point['variance'])]
        fields += [encode(b['flow'] if b else 'NONE'),
                   str(int(b is not None and b['low'] is not None)),
                   str(int(b is not None and b['high'] is not None))]
        yield '\t'.join(fields)

def block_records(value):
    for index,point in enumerate(value.get('points',[])):
        for b in point['block_values']:
            yield '\t'.join(['B',str(index),encode(b['tune_id']),str(b['block_id']),
                ','.join(encode(c['id']) for c in b['additive_components']) or '-',
                ','.join(numeric(c['value']) for c in b['additive_components']) or '-',str(b['events']),
                numeric(b['sumw']),numeric(b['sumw2']),numeric(b['sumabsw']),str(b['fills'])])

def capability_records(source_family_binding=True):
    yield '\t'.join(['V','SOURCE_FAMILY_SHA256',str(int(source_family_binding))])

def factor_records(value,source_family_binding=True):
    for group in value.get('covariance',[]):
        for family in group['independent_families']:
            for k,block in enumerate(family['block_ids']):
                for index,complement in enumerate(family['complements'][k]):
                    mean=family['leave_mean'][index]
                    yield '\t'.join(['F',encode(group['id']),str(index),encode(family['tune_id']),
                                      encode(family['source_family_digest'] if source_family_binding else ''),str(block),
                                      str(int(complement is not None)),numeric(complement),numeric(mean)])

def covariance_point_records(value):
    point_index={p.canonical(point['key']):index for index,point in enumerate(value.get('points',[]))}
    by_key={p.canonical(point['key']):point for point in value.get('points',[])}
    for group in value.get('covariance',[]):
        for slot,key in enumerate(group['ordered_point_keys']):
            token=p.canonical(key)
            if token not in point_index:raise ValueError('covariance point is absent from typed point domain')
            point=by_key[token]
            yield '\t'.join(['G',encode(group['id']),str(slot),str(point_index[token]),
                encode(point['semantic_id']),encode(p.digest(key)),str(int(group['valid_mask'][slot])),
                encode(group['units_by_point'][slot]),encode(group['status']),encode(group['representation']),
                str(group['K']),str(group['dof'])])

def covariance_value_records(value):
    for group in value.get('covariance',[]):
        if group['representation']!='DENSE':continue
        for row,values in enumerate(group['dense_rows']):
            for column,item in enumerate(values):
                yield '\t'.join(['C',encode(group['id']),str(row),str(column),
                    str(int(item is not None)),numeric(item)])

def views(value,source_family_binding=True):
    yield from capability_records(source_family_binding)
    for generator in (binding_records,point_records,block_records,covariance_point_records):
        yield from generator(value)
    yield from g9_records(value)
    yield from factor_records(value,source_family_binding)
    yield from covariance_value_records(value)

def normalized(line):
    fields=line.split('\t');kind=fields[0]
    if kind in ('V','H','G','M'):return line
    indices={'P':[17,18,21,24,27],'B':[7,8,9],'F':[7,8],'C':[5]}[kind]
    for i in indices:fields[i]=numeric(fields[i])
    if kind=='B' and fields[5]!='-':fields[5]=','.join(numeric(x) for x in fields[5].split(','))
    return '\t'.join(fields)

def from_science_transport(path):
    """Read the direct scientific tables; this deliberately ignores nodes/root_node."""
    records={'source_family_binding':None,'bindings':None,'g9_science':None,'points':[],'block_values':[],'covariance_points':[],
             'covariance_factors':[],'covariance_values':[]}
    names={'H':'bindings','P':'points','B':'block_values','G':'covariance_points',
           'F':'covariance_factors','C':'covariance_values'}
    with Path(path).open(encoding='ascii') as stream:
        if next(stream).rstrip('\n')!='hadronization_typed_science_v1':
            raise ValueError('typed science framing differs')
        ended=False
        for line in stream:
            line=line.rstrip('\n');fields=line.split('\t');kind=fields[0]
            if line=='END':
                if stream.read():raise ValueError('typed science trailing content')
                ended=True;break
            if kind=='V':
                if fields[:2]!=['V','SOURCE_FAMILY_SHA256'] or len(fields)!=3 or fields[2] not in ('0','1') or \
                        records['source_family_binding'] is not None:
                    raise ValueError('typed science capability record differs')
                records['source_family_binding']=fields[2]=='1'
            elif kind not in names and kind!='M':raise ValueError('unknown typed science record')
            elif kind=='H':
                if len(fields)!=24 or records['bindings'] is not None:raise ValueError('typed binding record differs')
                if fields[16] not in ('0','1'):raise ValueError('typed binding boolean differs')
                decoded=[decode(v) for v in fields[1:16]]
                records['bindings']=dict(schema=decoded[0],request_sha256=decoded[1],
                    scientific_request_sha256=decoded[2],science_content_sha256=decoded[3],
                    package_state=decoded[4],campaign_state=decoded[5],campaign_descriptor_sha256=decoded[6],
                    selected_members_sha256=decoded[7],source_members_sha256=decoded[8],analysis_config_sha256=decoded[9],
                    particle_registry_sha256=decoded[10],activity_definition_sha256=decoded[11],
                    selection_definitions_sha256=decoded[12],formula_source_sha256=decoded[13],
                    statistics_source_sha256=decoded[14],has_query_source_sha256=fields[16]=='1',
                    query_source_sha256=decode(fields[17]) or None,uncertainty_scope=decode(fields[18]),input_root_sha256=decode(fields[19]),
                    root_bytes=int(fields[20]),input_content_sha256=decode(fields[21]),
                    manifest_sha256=decode(fields[22]),source_fileset_sha256=decode(fields[23]))
            elif kind=='M':
                if len(fields)!=3 or records['g9_science'] is not None:
                    raise ValueError('typed G9 scientific metadata record differs')
                encoded=decode(fields[1]);metadata=json.loads(encoded)
                if p.canonical(metadata)!=encoded or p.digest(metadata)!=decode(fields[2]):
                    raise ValueError('typed G9 scientific metadata identity differs')
                p.validate(metadata,'G9Science','typed G9 science')
                species=metadata['signed_species_pdgs']
                if species!=sorted(set(species)) or not species:
                    raise ValueError('typed G9 signed species differ')
                reference=p.g9_science_legacy({'scope':{'roles':[{'role_id':'spectra.signed_heavy',
                    'required_curve_keys':[{'associate_pdg':pdg} for pdg in species]}]}})
                if metadata!=reference:
                    raise ValueError('typed G9 selection/normalization model differs')
                records['g9_science']=metadata
            else:
                records[names[kind]].append(normalized(line).split('\t'))
    if not ended or records['bindings'] is None or records['source_family_binding'] is None:
        raise ValueError('typed science completion/bindings/capability absent')
    binding=records['bindings']
    if binding['schema'] not in (p.RESULT_SCHEMA,p.RESULT_SCHEMA_G9) or binding['package_state'] not in ('VALIDATED_COMPLETE','VALIDATED_PARTIAL') or \
            binding['campaign_state'] not in ('FULL_ACCEPTED_CAMPAIGN','PARTIAL_SAMPLE') or binding['uncertainty_scope']!='FINITE_MC_ONLY':
        raise ValueError('typed science binding state differs')
    if (binding['schema']==p.RESULT_SCHEMA_G9)!=(records['g9_science'] is not None):
        raise ValueError('typed G9 scientific metadata/schema capability differs')
    digests=['request_sha256','scientific_request_sha256','science_content_sha256','campaign_descriptor_sha256',
             'selected_members_sha256','source_members_sha256','analysis_config_sha256','particle_registry_sha256',
             'activity_definition_sha256','selection_definitions_sha256','formula_source_sha256','statistics_source_sha256',
             'input_root_sha256','input_content_sha256','manifest_sha256','source_fileset_sha256']
    for name in digests:p.validate(binding[name],'Digest','typed bindings.'+name)
    if binding['has_query_source_sha256']!=(binding['query_source_sha256'] is not None):
        raise ValueError('typed query-source binding mask differs')
    if binding['query_source_sha256'] is not None:p.validate(binding['query_source_sha256'],'Digest','typed query source')
    points=records['points'];groups=records['covariance_points']
    if [int(row[1]) for row in points]!=list(range(len(points))):raise ValueError('typed point order differs')
    if any(len(row)!=31 for row in points):raise ValueError('typed point width differs')
    if len({row[2] for row in points})!=len(points) or len({row[3] for row in points})!=len(points):
        raise ValueError('typed point identity collides')
    def nullable_text(value):
        value=decode(value);return value or None
    def nullable_int(value):
        value=int(value);return value if value!=-1 else None
    def nullable_pdg(value):
        value=int(value);return value or None
    def point_key(row):
        axis=nullable_text(row[15]);bin_index=int(row[16])
        flow=decode(row[28]);has_low,has_high=row[29:31]
        if has_low not in ('0','1') or has_high not in ('0','1'):
            raise ValueError('typed point boundary masks differ')
        if flow=='NONE':
            if axis is not None or flow!='NONE' or has_low!='0' or has_high!='0':
                raise ValueError('typed scalar point axis differs')
            bins=[]
        else:
            if axis is None or flow not in ('REGULAR','UNDERFLOW','OVERFLOW'):
                raise ValueError('typed point flow differs')
            bins=[dict(axis_id=axis,index=bin_index,
                low=row[17] if has_low=='1' else None,
                high=row[18] if has_high=='1' else None,flow=flow)]
        key=dict(curve=dict(role_id=decode(row[4]),tune_id=decode(row[5]),
            reference_tune_id=nullable_text(row[6]),profile_id=nullable_text(row[7]),
            activity_id=nullable_text(row[8]),class_id=nullable_int(row[9]),
            trigger_pdg=nullable_pdg(row[10]),associate_pdg=nullable_pdg(row[11]),
            reference_pdg=nullable_pdg(row[12]),quantity=decode(row[13]),
            component=decode(row[14]),axis_id=axis),bins=bins)
        p.validate(key,'PointKey','typed point key')
        return key
    point_keys={}
    for row in points:
        for index in (2,3):p.validate(decode(row[index]),'Digest','typed point identity')
        for index in (20,23,26):
            if row[index] not in ('0','1'):raise ValueError('typed point boolean differs')
        key=point_key(row);point_keys[int(row[1])]=key
        if p.digest(key)!=decode(row[3]):raise ValueError('typed point key digest differs')
        if p.digest(dict(scientific_request_sha256=binding['scientific_request_sha256'],
                         point_key=key))!=decode(row[2]):
            raise ValueError('typed point semantic identity differs')
        expected_units=p.expected_point_units(key['curve']['quantity'])
        if decode(row[19])!=expected_units:raise ValueError('typed point units differ')
        has_center,row_center_status=row[20]=='1',decode(row[22])
        has_error,has_variance,row_error_status=row[23]=='1',row[26]=='1',decode(row[25])
        if has_center!=(row_center_status in ('AVAILABLE','AVAILABLE_ZERO_DISPERSION','UNSTABLE_DENOMINATOR')):
            raise ValueError('typed point center mask/status differs')
        available=row_error_status in ('AVAILABLE','AVAILABLE_ZERO_DISPERSION')
        if has_error!=available or has_variance!=available:
            raise ValueError('typed point uncertainty mask/status differs')
        if available:
            error,variance=float.fromhex(row[24]),float.fromhex(row[27])
            if error<0 or variance<0 or not math.isclose(error*error,variance,rel_tol=1e-12,abs_tol=1e-30):
                raise ValueError('typed point error/variance differs')
            if (row_error_status=='AVAILABLE_ZERO_DISPERSION')!=(variance==0):
                raise ValueError('typed point zero-dispersion status differs')
    point_by_index={int(row[1]):row for row in points};primitive_domains={}
    for row in records['block_values']:
        if len(row)!=11 or int(row[1]) not in point_by_index or not 1<=int(row[3])<=10:
            raise ValueError('typed primitive block domain differs')
        point=int(row[1]);key=(decode(row[2]),int(row[3]))
        if key in primitive_domains.setdefault(point,set()):raise ValueError('typed primitive block is duplicate')
        primitive_domains[point].add(key)
        components=[] if row[4]=='-' else [decode(value) for value in row[4].split(',')]
        values=[] if row[5]=='-' else row[5].split(',')
        if not components or len(components)!=len(values) or len(set(components))!=len(components) or \
                int(row[6])<0 or int(row[10])<0:
            raise ValueError('typed primitive receipt differs')
    def expected_families(index):
        curve=point_keys[index]['curve'];families={curve['tune_id']}
        if curve['reference_tune_id'] is not None:families.add(curve['reference_tune_id'])
        return families
    for index,point in point_by_index.items():
        expected={(tune,block) for tune in expected_families(index) for block in range(1,11)}
        actual=primitive_domains.get(index,set())
        if (actual and actual!=expected) or (point[20]=='1' and actual!=expected):
            raise ValueError('typed primitive K10/family domain differs')
    valid_point_indices={index for index,point in point_by_index.items() if point[23]=='1'}
    if valid_point_indices and not groups:raise ValueError('typed required covariance domain is absent')
    group_slots={};group_policy={};group_point_indices=set()
    for row in groups:
        if len(row)!=12:raise ValueError('typed covariance point width differs')
        if row[6] not in ('0','1'):raise ValueError('typed covariance point boolean differs')
        key=(decode(row[1]),int(row[2]));index=int(row[3])
        if key in group_slots or index not in point_by_index:raise ValueError('typed covariance point domain differs')
        if (key[0],index) in group_point_indices:
            raise ValueError('typed covariance point mapping is duplicate')
        group_point_indices.add((key[0],index))
        point=point_by_index[index]
        if decode(row[4])!=decode(point[2]) or decode(row[5])!=decode(point[3]):
            raise ValueError('typed covariance/point identity differs')
        if decode(row[7])!=decode(point[19]) or (row[6]=='1')!=(point[23]=='1'):
            raise ValueError('typed covariance point units/mask differs')
        if decode(row[8]) not in ('AVAILABLE_FULL','AVAILABLE_PARTIAL','UNAVAILABLE') or \
                decode(row[9]) not in ('DENSE','DELETE_ONE_FACTORS') or (int(row[10]),int(row[11]))!=(10,9):
            raise ValueError('typed covariance policy differs')
        group_slots[key]=row
        policy=(decode(row[8]),decode(row[9]),int(row[10]),int(row[11]))
        if key[0] in group_policy and group_policy[key[0]]!=policy:raise ValueError('typed covariance group policy differs')
        group_policy[key[0]]=policy
    mapped_valid_points={int(row[3]) for row in groups if row[6]=='1'}
    if mapped_valid_points!=valid_point_indices:
        raise ValueError('typed required covariance point domain differs')
    for label in ('covariance_factors','covariance_values'):
        for row in records[label]:
            key=(decode(row[1]),int(row[2]))
            if key not in group_slots:raise ValueError('typed covariance payload names a foreign point')
    factor_groups={}
    for row in records['covariance_factors']:
        if len(row)!=9 or row[6] not in ('0','1'):raise ValueError('typed factor width/boolean differs')
        key=(decode(row[1]),int(row[2]),decode(row[3]));block=int(row[5])
        family_digest=decode(row[4])
        if records['source_family_binding']:
            if not family_digest:raise ValueError('typed factor source family binding is blank')
            p.validate(family_digest,'Digest','typed factor source family')
        elif family_digest:
            raise ValueError('legacy typed factor unexpectedly carries source family binding')
        if not 1<=block<=10:raise ValueError('typed factor block domain differs')
        if block in factor_groups.setdefault(key,set()):raise ValueError('typed factor block is duplicate')
        factor_groups[key].add(block)
    group_families={}
    for (group,slot),mapping in group_slots.items():
        families=group_families.setdefault(group,set())
        if mapping[6]=='1':families.update(expected_families(int(mapping[3])))
    for group,families in group_families.items():
        slots={slot for candidate,slot in group_slots if candidate==group}
        expected={(group,slot,tune) for slot in slots for tune in families}
        if {key for key in factor_groups if key[0]==group}!=expected:
            raise ValueError('typed factor family domain differs')
        for key in expected:
            if factor_groups[key]!=set(range(1,11)):
                raise ValueError('typed factor block domain differs')
    factor_rows={}
    for row in records['covariance_factors']:
        factor_rows.setdefault((decode(row[1]),int(row[2]),decode(row[3])),[]).append(row)
    source_family_identities={}
    for key,rows in factor_rows.items():
        rows.sort(key=lambda row:int(row[5]));mapping=group_slots[key[:2]]
        active=mapping[6]=='1' and key[2] in expected_families(int(mapping[3]))
        identities={decode(row[4]) for row in rows}
        if len(identities)!=1:raise ValueError('typed factor source family identity differs')
        identity=next(iter(identities));family_key=(key[0],key[2])
        if family_key in source_family_identities and source_family_identities[family_key]!=identity:
            raise ValueError('typed factor source family identity differs')
        source_family_identities[family_key]=identity
        if any((row[6]=='1')!=active for row in rows):raise ValueError('typed factor leaf validity differs')
        complements=[float.fromhex(row[7]) for row in rows];means=[float.fromhex(row[8]) for row in rows]
        if active:
            if len(set(means))!=1 or not math.isclose(sum(complements)/10.,means[0],rel_tol=1e-12,abs_tol=1e-30):
                raise ValueError('typed factor leave mean differs')
        elif any(value!=0. for value in complements+means):
            raise ValueError('typed invalid factor payload differs')
    covariance_groups={}
    for row in records['covariance_values']:
        if len(row)!=6 or row[4] not in ('0','1'):raise ValueError('typed covariance cell width/boolean differs')
        group=decode(row[1]);key=(group,int(row[2]),int(row[3]))
        if key in covariance_groups:raise ValueError('typed covariance cell is duplicate')
        expected=(group_slots[(group,key[1])][6]=='1' and group_slots[(group,key[2])][6]=='1')
        if (row[4]=='1')!=expected:raise ValueError('typed covariance cell validity differs')
        covariance_groups[key]=row
    for group in {key[0] for key in group_slots}:
        slots=sorted(key[1] for key in group_slots if key[0]==group)
        if slots!=list(range(len(slots))):raise ValueError('typed covariance slot order differs')
        representation=decode(group_slots[(group,0)][9])
        masks=[group_slots[(group,slot)][6]=='1' for slot in slots]
        status=decode(group_slots[(group,0)][8])
        expected_status='AVAILABLE_FULL' if all(masks) else 'AVAILABLE_PARTIAL' if any(masks) else 'UNAVAILABLE'
        if status!=expected_status:raise ValueError('typed covariance status/mask differs')
        cells={key for key in covariance_groups if key[0]==group}
        if representation=='DENSE':
            expected={(group,row,column) for row in slots for column in slots}
            if cells!=expected:raise ValueError('typed dense covariance domain differs')
        elif cells:
            raise ValueError('factor covariance unexpectedly materializes dense cells')
    def factor_covariance(group,row,column):
        left_mapping=group_slots[(group,row)];right_mapping=group_slots[(group,column)]
        if left_mapping[6]!='1' or right_mapping[6]!='1':return None
        left_families=expected_families(int(left_mapping[3]))
        right_families=expected_families(int(right_mapping[3]))
        total=0.
        for tune in left_families & right_families:
            left=factor_rows[(group,row,tune)];right=factor_rows[(group,column,tune)]
            for a,b in zip(left,right):
                total += .9*(float.fromhex(a[7])-float.fromhex(a[8]))*(float.fromhex(b[7])-float.fromhex(b[8]))
        return total
    for (group,slot),mapping in group_slots.items():
        if mapping[6]!='1':continue
        actual=factor_covariance(group,slot,slot)
        if actual is None:raise ValueError('typed valid point lacks deletion factors')
        point=point_by_index[int(mapping[3])]
        if point[26]!='1' or not math.isclose(actual,float.fromhex(point[27]),rel_tol=1e-12,abs_tol=1e-30):
            raise ValueError('typed factor/point variance differs')
    for (group,row,column),cell in covariance_groups.items():
        if cell[4]!='1':continue
        actual=factor_covariance(group,row,column)
        if actual is None or not math.isclose(actual,float.fromhex(cell[5]),rel_tol=1e-12,abs_tol=1e-30):
            raise ValueError('typed factor/dense covariance differs')
    return records

def transport(value,path):
    with Path(path).open('w',encoding='ascii') as out:
        out.write('hadronization_typed_root_transport_v1\n');root=nodes(value,out)
        for line in views(value):out.write(line+'\n')
        out.write('ROOT\t'+str(root)+'\nEND\n')

def from_transport(path):
    values=[];actual=[];root=None;ended=False;source_family_binding=None
    with Path(path).open(encoding='ascii') as stream:
        if next(stream).rstrip('\n')!='hadronization_typed_root_transport_v1':raise ValueError('archive framing differs')
        for line in stream:
            line=line.rstrip('\n');f=line.split('\t')
            if f[0]=='N':
                if len(f)!=6 or int(f[1])!=len(values):raise ValueError('archive node order/width differs')
                kind,text=f[2],decode(f[3]);children=[] if f[4]=='-' else list(map(int,f[4].split(',')))
                keys=[] if f[5]=='-' else list(map(decode,f[5].split(',')))
                if any(i<0 or i>=len(values) for i in children):raise ValueError('cyclic archive node')
                if kind=='O':
                    if keys!=sorted(set(keys)) or len(keys)!=len(children) or text:raise ValueError('archive object topology differs')
                    v={k:values[i] for k,i in zip(keys,children)}
                elif kind=='A':
                    if keys or text:raise ValueError('archive array topology differs')
                    v=[values[i] for i in children]
                else:
                    if children or keys:raise ValueError('archive scalar topology differs')
                    if kind=='N' and text=='':v=None
                    elif kind=='B' and text in ('0','1'):v=text=='1'
                    elif kind=='I' and str(int(text))==text:v=int(text)
                    elif kind=='F' and math.isfinite(float.fromhex(text)):v=float.fromhex(text)
                    elif kind=='S':v=text
                    else:raise ValueError('archive scalar kind differs')
                values.append(v)
            elif f[0]=='V':
                if f[:2]!=['V','SOURCE_FAMILY_SHA256'] or len(f)!=3 or f[2] not in ('0','1') or source_family_binding is not None:
                    raise ValueError('archive capability record differs')
                source_family_binding=f[2]=='1';actual.append(line)
            elif f[0] in ('H','P','B','G','F','C','M'):actual.append(normalized(line))
            elif f[0]=='ROOT':
                if root is not None or len(f)!=2:raise ValueError('archive root repeated')
                root=int(f[1])
            elif line=='END':
                if stream.read():raise ValueError('archive trailing content')
                ended=True;break
            else:raise ValueError('unknown archive record')
    if not ended or root is None or not 0<=root<len(values) or source_family_binding is None:
        raise ValueError('archive root/completion/capability absent')
    value=values[root]
    if actual!=list(views(value,source_family_binding)):
        raise ValueError('actual typed ROOT values differ from reconstructed authority')
    return checked(value,cold=True)

def write(value,output,work):
    if value.get('schema')==p.RESULT_SCHEMA_NATIVE:
        from . import archive_v4
        return archive_v4.write(value,output)
    checked(value);output=Path(output);work=Path(work)
    r.reject_symlink_components(output,'typed ROOT output')
    if output.exists():raise FileExistsError('typed ROOT output already exists')
    env,binary,receipt=build(work)
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='typed-root-',dir=str(work)) as directory:
        temporary=Path(directory);source=temporary/'input.tsv';transport(value,source)
        staged=temporary/'archive.root';execute(binary,env,'pack',source,staged)
        dumped=temporary/'readback.tsv';execute(binary,env,'dump',staged,dumped)
        reconstructed=from_transport(dumped)
        if p.digest(reconstructed)!=p.digest(value):raise ValueError('ROOT reconstruction differs')
        r.fsync_file(staged)
        # Hard-link publication is atomic and cannot overwrite a racing name.
        # Work and destination must be on the same local filesystem.
        os.link(str(staged),str(output));r.fsync_directory(output.parent)
    return dict(schema=SCHEMA,root_sha256=p.file_digest(output),root_bytes=output.stat().st_size,
                value_sha256=p.digest(value),build=receipt)

def read(source,work,expected_root_sha256,expected_value_sha256):
    source=Path(source);r.regular_file(source,'typed ROOT archive')
    r.lower_sha(expected_root_sha256,'trusted archive ROOT digest');r.lower_sha(expected_value_sha256,'trusted reconstructed value digest')
    if p.file_digest(source)!=expected_root_sha256:raise ValueError('typed ROOT differs from trusted hash')
    import ROOT as root_api
    probe=root_api.TFile.Open(str(source),'READ')
    try:
        native_v4=bool(probe and not probe.IsZombie() and probe.Get('v4_metadata'))
    finally:
        if probe:probe.Close()
    if native_v4:
        from . import archive_v4
        return archive_v4.read(source,expected_root_sha256,expected_value_sha256)
    env,binary,_=build(Path(work))
    with tempfile.TemporaryDirectory(prefix='typed-root-read-',dir=str(work)) as directory:
        transport=Path(directory)/'readback.tsv';execute(binary,env,'dump',source,transport);value=from_transport(transport)
    if p.digest(value)!=expected_value_sha256 or p.file_digest(source)!=expected_root_sha256:raise ValueError('typed ROOT logical/physical readback differs')
    return value

def read_science(source,work,expected_root_sha256):
    source=Path(source);r.regular_file(source,'typed ROOT archive')
    r.lower_sha(expected_root_sha256,'trusted archive ROOT digest')
    if p.file_digest(source)!=expected_root_sha256:raise ValueError('typed ROOT differs from trusted hash')
    env,binary,_=build(Path(work))
    with tempfile.TemporaryDirectory(prefix='typed-science-read-',dir=str(work)) as directory:
        transport=Path(directory)/'science.tsv';execute(binary,env,'science',source,transport)
        return from_science_transport(transport)

def main():
    cli=argparse.ArgumentParser(description=__doc__);cli.add_argument('operation',choices=['pack','unpack','verify'])
    cli.add_argument('--input',type=Path,required=True);cli.add_argument('--output',type=Path)
    cli.add_argument('--work-root',type=Path,required=True);cli.add_argument('--expected-root-sha256');cli.add_argument('--expected-value-sha256')
    args=cli.parse_args()
    if args.operation=='pack':print(p.canonical(write(r.json_file(args.input),args.output,args.work_root)))
    else:
        value=read(args.input,args.work_root,args.expected_root_sha256,args.expected_value_sha256)
        if args.operation=='unpack':r.atomic_json(args.output,value,exclusive=True)
        print('TYPED_ROOT_VERIFIED '+p.digest(value))

if __name__=='__main__':main()
