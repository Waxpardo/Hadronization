"""Cold, direct ROOT archive for authenticated native diagnostic runs.

This TEST_ONLY diagnostic format exposes point values, independent K10 factors,
and pooled/delete-one class boundaries as typed TTrees.  It is deliberately
distinct from the release ProjectionResult DTO: the native diagnostic does not
yet carry the complete per-point primitive and denominator receipts.
"""
from array import array
import csv
import json
import math
import os
from pathlib import Path
import tempfile

from . import native_runner as runner

p=runner.p
SCHEMA='hadronization_native_diagnostic_root_v2_TEST_ONLY'


def _text(value):
    return str(value)


def _number(value):
    if value=='-':return False,0.0
    result=float.fromhex(value)
    if not math.isfinite(result):raise ValueError('native ROOT input is nonfinite')
    return True,result


def _branch(tree,name,kind):
    if kind=='text':
        import ROOT
        value=ROOT.std.string()
        tree.Branch(name,value)
    else:
        value=array({'int':'i','long':'q','bool':'b','double':'d'}[kind],[0])
        tree.Branch(name,value,{'int':name+'/I','long':name+'/L',
                               'bool':name+'/O','double':name+'/D'}[kind])
    return value


def _set(holder,value):
    if isinstance(holder,array):holder[0]=value
    else:holder.assign(str(value))


def _tree(name,fields):
    import ROOT
    tree=ROOT.TTree(name,name)
    return tree,{field:_branch(tree,field,kind) for field,kind in fields.items()}


POINT_FIELDS=dict(index='int',semantic_id='text',point_key_json='text',
    center_status='text',center_present='bool',center='double',
    uncertainty_status='text',variance_present='bool',variance='double',
    error_present='bool',error='double',reason='text',
    diagnostic_variance_present='bool',diagnostic_variance='double')
FACTOR_FIELDS=dict(point='int',tune='text',source_family_sha256='text',
    block='int',valid='bool',leaf_present='bool',leaf='double',
    mean_present='bool',leave_mean='double',centered_factor='double')
BOUNDARY_FIELDS=dict(tune='text',source_family_sha256='text',class_id='int',
    omitted_block='int',status='text',low='int',high='int',empty='bool',
    weight_present='bool',weighted_measure='double')
GROUP_FIELDS=dict(group_id='text',slot='int',point='int',semantic_id='text',
    representation='text',valid='bool',units='text')


def _fill(tree,holders,values):
    for name,holder in holders.items():_set(holder,values[name])
    tree.Fill()


def write(diagnostic,request,index_sha256,output):
    """Write and cold-check a TEST_ONLY archive from a fully checked run."""
    import ROOT
    ROOT.gROOT.SetBatch(True)
    typed=(request if isinstance(request,p.ProjectionRequest) else
           p.ProjectionRequest.from_dict(request.to_dict() if hasattr(request,'to_dict')
                                         else request,cold=True))
    counts=runner.verify_native_diagnostic_stream(diagnostic,typed)
    p.validate(index_sha256,'Digest','native ROOT collection index SHA')
    output=Path(output).absolute()
    if output.exists() or output.is_symlink():raise FileExistsError(output)
    p._reducer().reject_symlink_components(output,'native ROOT diagnostic output')
    output.parent.mkdir(parents=True,exist_ok=True)
    request_json=p.canonical(typed.to_dict())
    metadata=dict(schema=SCHEMA,request_json=request_json,
        request_sha256=typed.request_sha256,
        scientific_request_sha256=typed.scientific_request_sha256,
        collection_index_sha256=index_sha256,
        diagnostic_sha256=p.file_digest(diagnostic),
        source_scientific_identity_sha256=typed.to_dict()['bindings'][
            'expected_source_content_sha256'],
        selected_members_sha256=typed.to_dict()['sources']['selected_members_sha256'],
        g9_science=(p.g9_science(typed.to_dict()) if any(
            role['role_id']=='spectra.signed_heavy' for role in
            typed.to_dict()['scope']['roles']) else None),
        state='TEST_ONLY_DIAGNOSTIC_NOT_RELEASE_DTO')
    handle,tempname=tempfile.mkstemp(prefix='.'+output.name+'.',suffix='.root',
                                    dir=output.parent)
    os.close(handle)
    try:
        file=ROOT.TFile.Open(tempname,'RECREATE')
        if not file or file.IsZombie():raise ValueError('native ROOT cannot create')
        try:
            ROOT.TObjString(p.canonical(metadata)).Write('native_metadata')
            points,ph=_tree('points',POINT_FIELDS)
            factors,fh=_tree('covariance_factors',FACTOR_FIELDS)
            boundaries,bh=_tree('class_boundaries',BOUNDARY_FIELDS)
            groups,gh=_tree('covariance_points',GROUP_FIELDS)
            expected=typed.expected_point_keys
            point_index={p.canonical(key):index for index,key in enumerate(expected)}
            with Path(diagnostic).open(encoding='ascii') as source:
                next(source);next(source)
                for index,key in enumerate(expected):
                    row=next(source).rstrip('\n').split('\t')
                    center=_number(row[3]);variance=_number(row[5]);error=_number(row[6])
                    diagnostic_variance=_number(row[10])
                    _fill(points,ph,dict(index=index,semantic_id=p.semantic_id(typed,key),
                        point_key_json=p.canonical(key),center_status=row[2],
                        center_present=center[0],center=center[1],
                        uncertainty_status=row[4],variance_present=variance[0],
                        variance=variance[1],error_present=error[0],error=error[1],
                        reason=row[9],diagnostic_variance_present=diagnostic_variance[0],
                        diagnostic_variance=diagnostic_variance[1]))
                    tunes=[key['curve']['tune_id']]
                    if key['curve']['reference_tune_id'] is not None:
                        tunes.append(key['curve']['reference_tune_id'])
                    for tune in tunes:
                        for block in range(1,11):
                            field=next(source).rstrip('\n').split('\t')
                            leaf=_number(field[6]);mean=_number(field[7]);factor=_number(field[8])
                            _fill(factors,fh,dict(point=index,tune=tune,
                                source_family_sha256=field[3],block=block,
                                valid=field[5]=='1',leaf_present=leaf[0],leaf=leaf[1],
                                mean_present=mean[0],leave_mean=mean[1],
                                centered_factor=factor[1]))
                for line in source:
                    if line=='END\n':break
                    field=line.rstrip('\n').split('\t')
                    weight=_number(field[9])
                    _fill(boundaries,bh,dict(tune=field[1],
                        source_family_sha256=field[2],class_id=int(field[3]),
                        omitted_block=int(field[4]),status=field[5],
                        low=int(field[6]) if field[6]!='-' else -1,
                        high=int(field[7]) if field[7]!='-' else -1,
                        empty=field[8]=='1',weight_present=weight[0],
                        weighted_measure=weight[1]))
            for group in typed.to_dict()['statistics']['covariance_groups']:
                for slot,key in enumerate(group['ordered_point_keys']):
                    index=point_index[p.canonical(key)]
                    points.GetEntry(index)
                    _fill(groups,gh,dict(group_id=group['id'],slot=slot,
                        point=index,semantic_id=p.semantic_id(typed,key),
                        representation=group['representation'],
                        valid=bool(points.variance_present),
                        units=p.expected_point_units(key['curve']['quantity'])))
            for tree in (points,factors,boundaries,groups):tree.Write()
            file.Write()
        finally:file.Close()
        with open(tempname,'rb') as staged:
            os.fsync(staged.fileno())
        if p.file_digest(diagnostic)!=metadata['diagnostic_sha256']:
            raise ValueError('native diagnostic changed during ROOT packing')
        root_sha=p.file_digest(tempname)
        checked=read(tempname,root_sha)
        if {k:checked[k] for k in counts}!=counts:
            raise ValueError('native ROOT cold row counts differ')
        os.link(tempname,output)
        p._reducer().fsync_directory(output.parent)
    finally:
        if os.path.exists(tempname):os.unlink(tempname)
    return dict(schema=SCHEMA,path=str(output),root_sha256=root_sha,
                root_bytes=output.stat().st_size,diagnostic_sha256=metadata[
                    'diagnostic_sha256'],**counts)


def read(path,expected_root_sha256):
    """Cold-check exact typed branches, request keys, K10 factors and masks."""
    import ROOT
    ROOT.gROOT.SetBatch(True)
    path=Path(path)
    if path.is_symlink() or not path.is_file() or p.file_digest(path)!=expected_root_sha256:
        raise ValueError('native ROOT differs from trusted physical hash')
    file=ROOT.TFile.Open(str(path),'READ')
    if not file or file.IsZombie():raise ValueError('native ROOT cannot open')
    try:
        if {str(key.GetName()) for key in file.GetListOfKeys()}!=\
                {'native_metadata','points','covariance_factors',
                 'class_boundaries','covariance_points'}:
            raise ValueError('native ROOT exact object domain differs')
        metadata=json.loads(_text(file.Get('native_metadata').GetString()))
        if set(metadata)!={'schema','request_json','request_sha256',
                'scientific_request_sha256','collection_index_sha256',
                'diagnostic_sha256','source_scientific_identity_sha256',
                'selected_members_sha256','g9_science','state'}:
            raise ValueError('native ROOT metadata field set differs')
        if metadata['schema']!=SCHEMA or metadata['state']!=\
                'TEST_ONLY_DIAGNOSTIC_NOT_RELEASE_DTO':
            raise ValueError('native ROOT diagnostic schema/state differs')
        typed=p.ProjectionRequest.from_dict(json.loads(metadata['request_json']),cold=True)
        if metadata['request_json']!=p.canonical(typed.to_dict()) or \
                metadata['request_sha256']!=typed.request_sha256 or \
                metadata['scientific_request_sha256']!=typed.scientific_request_sha256 or \
                metadata['source_scientific_identity_sha256']!=typed.to_dict()[
                    'bindings']['expected_source_content_sha256'] or \
                metadata['selected_members_sha256']!=typed.to_dict()['sources'][
                    'selected_members_sha256'] or \
                metadata['g9_science']!=(p.g9_science(typed.to_dict()) if any(
                    role['role_id']=='spectra.signed_heavy' for role in
                    typed.to_dict()['scope']['roles']) else None):
            raise ValueError('native ROOT request/source binding differs')
        p.validate(metadata['collection_index_sha256'],'Digest','native ROOT index')
        p.validate(metadata['diagnostic_sha256'],'Digest','native ROOT diagnostic')
        points=file.Get('points');factors=file.Get('covariance_factors')
        boundaries=file.Get('class_boundaries');groups=file.Get('covariance_points')
        for tree,fields in ((points,POINT_FIELDS),(factors,FACTOR_FIELDS),
                            (boundaries,BOUNDARY_FIELDS),(groups,GROUP_FIELDS)):
            if not tree or {str(branch.GetName()) for branch in tree.GetListOfBranches()}!=set(fields):
                raise ValueError('native ROOT direct branch domain differs')
        value=typed.to_dict();keys=typed.expected_point_keys
        families={tune:p.digest([member for member in value['sources']['members']
            if member['tune_id']==tune]) for tune in value['scope']['ordered_tunes']}
        counts=dict(points=0,factors=0,boundaries=0,available_errors=0,
                    withheld_errors=0)
        factor_index=0
        for index,key in enumerate(keys):
            if points.GetEntry(index)<=0 or int(points.index)!=index or \
                    _text(points.point_key_json)!=p.canonical(key) or \
                    _text(points.semantic_id)!=p.semantic_id(typed,key):
                raise ValueError('native ROOT point natural identity differs')
            active=bool(points.variance_present)
            if _text(points.center_status) not in ('AVAILABLE','UNDEFINED',
                    'UNSTABLE_DENOMINATOR') or _text(points.uncertainty_status) not in (
                    'AVAILABLE','AVAILABLE_ZERO_DISPERSION','WITHHELD_UNCERTAINTY'):
                raise ValueError('native ROOT point scientific status differs')
            if bool(points.error_present)!=active or bool(points.center_present)!=\
                    (_text(points.center_status)!='UNDEFINED') or \
                    active!=(_text(points.uncertainty_status)!='WITHHELD_UNCERTAINTY'):
                raise ValueError('native ROOT point status/mask differs')
            if points.center_present and not math.isfinite(points.center):
                raise ValueError('native ROOT point center is nonfinite')
            if active and (not math.isfinite(points.variance) or points.variance<0 or
                    not math.isclose(points.error**2,points.variance,
                                     rel_tol=1e-12,abs_tol=1e-30)):
                raise ValueError('native ROOT point error/variance differs')
            tunes=[key['curve']['tune_id']]
            if key['curve']['reference_tune_id'] is not None:
                tunes.append(key['curve']['reference_tune_id'])
            recovered=0.0
            for tune in tunes:
                leaves=[];means=[]
                for block in range(1,11):
                    if factors.GetEntry(factor_index)<=0 or int(factors.point)!=index or \
                            _text(factors.tune)!=tune or int(factors.block)!=block or \
                            _text(factors.source_family_sha256)!=families[tune] or \
                            bool(factors.valid)!=active:
                        raise ValueError('native ROOT factor family/block differs')
                    if bool(factors.leaf_present) and not math.isfinite(factors.leaf):
                        raise ValueError('native ROOT factor leaf is nonfinite')
                    if bool(factors.mean_present) and not math.isfinite(factors.leave_mean):
                        raise ValueError('native ROOT factor leave mean is nonfinite')
                    if active:
                        if not factors.leaf_present or not factors.mean_present or \
                                not math.isfinite(factors.centered_factor):
                            raise ValueError('native ROOT valid factor payload differs')
                        leaves.append(float(factors.leaf));means.append(float(factors.leave_mean))
                        recovered+=float(factors.centered_factor)**2
                    factor_index+=1
                if active:
                    mean=sum(leaves)/10.0
                    if any(not math.isclose(item,mean,rel_tol=1e-12,
                                             abs_tol=1e-30) for item in means):
                        raise ValueError('native ROOT family leave mean differs')
                counts['factors']+=10
            if active:
                if not math.isclose(recovered,float(points.variance),
                                    rel_tol=1e-12,abs_tol=1e-30):
                    raise ValueError('native ROOT factor variance differs')
                counts['available_errors']+=1
            else:counts['withheld_errors']+=1
            counts['points']+=1
        if points.GetEntries()!=len(keys) or factors.GetEntries()!=factor_index:
            raise ValueError('native ROOT point/factor completion differs')
        expected_boundary=[(tune,klass['id'],omit)
            for tune in sorted(value['scope']['ordered_tunes'])
            for klass in sorted(value['classes'],key=lambda item:item['id'])
            for omit in range(11)]
        activity_bins=len(next(axis for axis in value['axes']
            if axis['id']=='nch')['edges'])-1
        for index,(tune,class_id,omit) in enumerate(expected_boundary):
            if boundaries.GetEntry(index)<=0 or _text(boundaries.tune)!=tune or \
                    _text(boundaries.source_family_sha256)!=families[tune] or \
                    int(boundaries.class_id)!=class_id or \
                    int(boundaries.omitted_block)!=omit:
                raise ValueError('native ROOT class boundary identity differs')
            if _text(boundaries.status)=='RESOLVED':
                if not boundaries.weight_present or not 0<=boundaries.low<=activity_bins or \
                        not -1<=boundaries.high<activity_bins or \
                        (boundaries.low>boundaries.high and not boundaries.empty) or \
                        (boundaries.empty and boundaries.weighted_measure!=0.0) or \
                        (not boundaries.empty and boundaries.weighted_measure<=0.0):
                    raise ValueError('native ROOT class boundary payload differs')
            elif _text(boundaries.status)!='UNRESOLVED' or boundaries.weight_present or \
                    not boundaries.empty:
                raise ValueError('native ROOT unresolved class boundary differs')
            counts['boundaries']+=1
        if boundaries.GetEntries()!=len(expected_boundary):
            raise ValueError('native ROOT boundary completion differs')
        group_index=0
        point_index={p.canonical(key):index for index,key in enumerate(keys)}
        for group in value['statistics']['covariance_groups']:
            for slot,key in enumerate(group['ordered_point_keys']):
                index=point_index[p.canonical(key)]
                if groups.GetEntry(group_index)<=0 or \
                        _text(groups.group_id)!=group['id'] or \
                        int(groups.slot)!=slot or int(groups.point)!=index or \
                        _text(groups.semantic_id)!=p.semantic_id(typed,key) or \
                        _text(groups.representation)!=group['representation'] or \
                        _text(groups.units)!=p.expected_point_units(
                            key['curve']['quantity']):
                    raise ValueError('native ROOT covariance point/group identity differs')
                points.GetEntry(index)
                if bool(groups.valid)!=bool(points.variance_present):
                    raise ValueError('native ROOT covariance point mask differs')
                group_index+=1
        if groups.GetEntries()!=group_index:
            raise ValueError('native ROOT covariance group completion differs')
        return dict(schema=SCHEMA,root_sha256=expected_root_sha256,
                    request_sha256=typed.request_sha256,
                    scientific_request_sha256=typed.scientific_request_sha256,
                    collection_index_sha256=metadata['collection_index_sha256'],**counts)
    finally:file.Close()


def export_tables(path,expected_root_sha256,csv_path,tex_path,missing_path):
    """Regenerate round-trip-safe TEST_ONLY point and missing-state tables.

    The ROOT artifact is the sole input.  TeX is a compact role/status index;
    the point CSV carries every natural key and numerical value.
    """
    import ROOT
    checked=read(path,expected_root_sha256)
    destinations=[Path(item).absolute() for item in
                  (csv_path,tex_path,missing_path)]
    for destination in destinations:
        p._reducer().reject_symlink_components(destination,'native export')
        if destination.exists() or destination.is_symlink():
            raise FileExistsError(destination)
        destination.parent.mkdir(parents=True,exist_ok=True)
    root=ROOT.TFile.Open(str(path),'READ')
    if not root or root.IsZombie():raise ValueError('native ROOT export cannot open')
    staged=[]
    try:
        for destination in destinations:
            descriptor,name=tempfile.mkstemp(prefix='.'+destination.name+'.',
                                            suffix='.tmp',dir=destination.parent)
            staged.append((descriptor,name,destination))
        points=root.Get('points')
        role_counts={}
        with os.fdopen(staged[0][0],'w',encoding='utf-8',newline='') as point_file,\
             os.fdopen(staged[2][0],'w',encoding='utf-8',newline='') as missing_file:
            point_writer=csv.writer(point_file)
            missing_writer=csv.writer(missing_file)
            point_writer.writerow(['semantic_id','natural_point_key_json','units',
                'center_status','center_hex64','uncertainty_status',
                'variance_hex64','standard_error_hex64','reason'])
            missing_writer.writerow(['semantic_id','role_id','center_status',
                'uncertainty_status','reason'])
            for index in range(points.GetEntries()):
                points.GetEntry(index)
                key=json.loads(_text(points.point_key_json))
                role=key['curve']['role_id']
                role_counts.setdefault(role,[0,0,0])
                role_counts[role][0]+=1
                role_counts[role][1]+=int(bool(points.center_present))
                role_counts[role][2]+=int(bool(points.error_present))
                def shown(present,value):
                    return float(value).hex() if present else 'UNAVAILABLE'
                point_writer.writerow([_text(points.semantic_id),
                    _text(points.point_key_json),
                    p.expected_point_units(key['curve']['quantity']),
                    _text(points.center_status),shown(points.center_present,points.center),
                    _text(points.uncertainty_status),
                    shown(points.variance_present,points.variance),
                    shown(points.error_present,points.error),_text(points.reason)])
                if not points.center_present or not points.error_present:
                    missing_writer.writerow([_text(points.semantic_id),role,
                        _text(points.center_status),
                        _text(points.uncertainty_status),_text(points.reason)])
            point_file.flush();os.fsync(point_file.fileno())
            missing_file.flush();os.fsync(missing_file.fileno())
        with os.fdopen(staged[1][0],'w',encoding='utf-8',newline='\n') as tex:
            tex.write('% TEST_ONLY native diagnostic; not a release science table\n')
            tex.write('\\begin{tabular}{lrrr}\nRole & Points & Centers & Errors \\\\\n\\hline\n')
            for role,counts in sorted(role_counts.items()):
                escaped=role.replace('_','\\_')
                tex.write('{} & {} & {} & {} \\\\\n'.format(escaped,*counts))
            tex.write('\\end{tabular}\n')
            tex.flush();os.fsync(tex.fileno())
        for _,name,destination in staged:
            os.link(name,destination)
            p._reducer().fsync_directory(destination.parent)
        return dict(schema='hadronization_native_diagnostic_exports_v1_TEST_ONLY',
            root_sha256=expected_root_sha256,points=checked['points'],
            files={destination.name:dict(path=str(destination),sha256=p.file_digest(destination),
                   bytes=destination.stat().st_size) for destination in destinations})
    finally:
        root.Close()
        for descriptor,name,_ in staged:
            try:os.close(descriptor)
            except OSError:pass
            if os.path.exists(name):os.unlink(name)
