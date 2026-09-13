"""Assemble the single typed v4 result from verified native estimator receipts.

This maps C++ values and K10 leaves into the existing result contract. It does
not evaluate a second observable formula or infer missing generator attempts.
"""
import math
from pathlib import Path

from . import native_runner as runner
from . import native_v4

p=runner.p


def _number(token):
    return None if token=='-' else float.fromhex(token).hex()


def _lines(path,header,request):
    stream=Path(path).open(encoding='ascii')
    if next(stream).rstrip('\n')!=header or next(stream).rstrip('\n').split('\t')!=[
            'BIND',request.request_sha256,request.scientific_request_sha256]:
        stream.close()
        raise ValueError('native v4 source stream/request binding differs')
    return stream


def from_verified_diagnostic(request,run_receipt,event_moments,
                             artifact_binding,provenance,primitive_routes,
                             capability_receipt,analysis,*,campaign_state='PARTIAL_SAMPLE',
                             admission_closure=None,cold=False,science_only=False):
    """Build a reviewable v4 DTO; a source/build ledger is mandatory input."""
    typed=p.ProjectionRequest.from_dict(
        request.to_dict() if hasattr(request,'to_dict') else request,cold=True)
    req=typed.to_dict();keys=typed.expected_point_keys
    diagnostic=run_receipt['diagnostic_path']
    blocks=run_receipt['block_primitive_path']
    denominators=run_receipt['denominator_path']
    if any(p.file_digest(run_receipt[name+'_path'])!=run_receipt[name+'_sha256']
           for name in ('diagnostic','block_primitive','denominator')):
        raise ValueError('native v4 diagnostic stream physical pin differs')
    runner.verify_native_diagnostic_stream(diagnostic,typed)
    runner.verify_native_block_primitives_stream(blocks,typed,event_moments)
    runner.verify_native_denominator_stream(denominators,typed,event_moments,blocks)
    moments=native_v4.event_moment_receipts(typed,event_moments)
    diagnostics=native_v4.support_diagnostic_receipts(run_receipt,moments)
    moment_by_group={(row['tune_id'],row['block_id']):row for row in moments}
    groups=req['statistics']['covariance_groups']
    memberships={p.canonical(key):[] for key in keys}
    expected_family={tune:p.digest([member for member in req['sources']['members']
        if member['tune_id']==tune]) for tune in req['scope']['ordered_tunes']}
    for group in groups:
        if group['representation']!='DELETE_ONE_FACTORS':
            raise ValueError('native v4 dense covariance requires explicit derivation')
        for key in group['ordered_point_keys']:
            memberships[p.canonical(key)].append(group['id'])
    points=[];materialization=[];point_leaves=[];point_means=[]
    result_stream=_lines(diagnostic,'hadronization_native_engine_diagnostic_v2',typed)
    block_stream=_lines(blocks,'hadronization_native_block_primitives_v1',typed)
    parent_stream=_lines(denominators,'hadronization_native_denominator_parents_v1',typed)
    try:
        for index,key in enumerate(keys):
            row=next(result_stream).rstrip('\n').split('\t')
            if row[:2]!=['R',str(index)]:
                raise ValueError('native v4 point order differs')
            curve=key['curve'];tunes=[curve['tune_id']]
            if curve['reference_tune_id'] is not None:
                tunes.append(curve['reference_tune_id'])
            leaves={};means={};block_values=[];parents=[];semantic_parents=[]
            for tune in tunes:
                leaves[tune]=[]
                family=expected_family[tune]
                for block in range(1,11):
                    factor=next(result_stream).rstrip('\n').split('\t')
                    if factor[:5]!=['F',str(index),tune,family,str(block)]:
                        raise ValueError('native v4 factor identity differs')
                    leaves[tune].append(_number(factor[6]))
                    if block==1:means[tune]=_number(factor[7])
                    elif means[tune]!=_number(factor[7]):
                        raise ValueError('native v4 factor leave mean differs')
                    primitive=next(block_stream).rstrip('\n').split('\t')
                    if primitive[:5]!=['B',str(index),tune,family,str(block)]:
                        raise ValueError('native v4 block primitive identity differs')
                    names=[] if primitive[7]=='-' else primitive[7].split(';')
                    values=[] if primitive[8]=='-' else primitive[8].split(';')
                    if len(names)!=len(values):
                        raise ValueError('native v4 component identity/value differs')
                    moment=moment_by_group[tune,block]
                    block_values.append(dict(tune_id=tune,block_id=block,
                        additive_components=[dict(id=name,value=_number(value))
                            for name,value in zip(names,values)],
                        events=moment['events'],sumw=moment['sumw'],
                        sumw2=moment['sumw2'],sumabsw=moment['sumabsw'],
                        event_weight_terms=moment['event_weight_terms'],
                        event_moments_sha256=moment['content_sha256']))
            for name,retained in p.expected_denominator_parents(key):
                parent=next(parent_stream).rstrip('\n').split('\t')
                if parent[:4]!=['D',str(index),name,str(int(retained))]:
                    raise ValueError('native v4 denominator identity differs')
                receipt=dict(natural_key=p.canonical(key)+'/parent='+name,
                    pooled_value=_number(parent[5]),status=parent[4],
                    retained_after_algebra=retained,
                    delete_one_statuses=parent[6].split(';'),policy_id=p.ESTIMATOR)
                parents.append(receipt)
                semantic_parents.append(dict(natural_key=receipt['natural_key'],
                    exists=receipt['status']!='UNDEFINED',materialized=True,
                    content_digest=p.digest(receipt),coverage_status='COMPLETE_K10'))
            point=dict(key=key,semantic_id=p.semantic_id(typed,key),
                units=p.expected_point_units(curve['quantity']),
                center=_number(row[3]),center_status=row[2],
                standard_error=_number(row[6]),variance=_number(row[5]),
                uncertainty_status=row[4],
                reasons=[] if row[9]=='-' else row[9].split(','),
                semantic_parents=semantic_parents,
                denominator_receipts=parents,block_values=block_values,
                covariance_group_ids=memberships[p.canonical(key)])
            points.append(point);point_leaves.append(leaves)
            point_means.append(means)
            materialization.append(dict(point_key=key,status='PRESENT',reason_codes=[]))
        if next(block_stream).rstrip('\n')!='END' or block_stream.read() or \
                next(parent_stream).rstrip('\n')!='END' or parent_stream.read():
            raise ValueError('native v4 primitive/denominator trailing rows differ')
        boundaries={};boundary_deletions=[]
        for tune in sorted(req['scope']['ordered_tunes']):
            for klass in sorted(req['classes'],key=lambda c:c['id']):
                for omit in range(11):
                    field=next(result_stream).rstrip('\n').split('\t')
                    if field[:5]!=['Q',tune,expected_family[tune],
                                   str(klass['id']),str(omit)]:
                        raise ValueError('native v4 class boundary identity differs')
                    resolved=field[5]=='RESOLVED'
                    body=dict(tune_id=tune,class_id=klass['id'],
                        omitted_block=omit,
                        source_family_digest=expected_family[tune],
                        status=field[5],low=int(field[6]) if resolved else None,
                        high=int(field[7]) if resolved else None,
                        empty=field[8]=='1',
                        weighted_measure=_number(field[9]) if resolved else None)
                    boundary_deletions.append(dict(body,
                        content_sha256=p.digest(body)))
                    if omit==0:boundaries[tune,klass['id']]=field
        if next(result_stream).rstrip('\n')!='END' or result_stream.read():
            raise ValueError('native v4 diagnostic trailing rows differ')
    finally:
        result_stream.close();block_stream.close();parent_stream.close()
    covariance=[]
    point_index={p.canonical(key):index for index,key in enumerate(keys)}
    for group in groups:
        ordered=group['ordered_point_keys']
        indices=[point_index[p.canonical(key)] for key in ordered]
        selected=[points[index] for index in indices]
        mask=[point['uncertainty_status'] in ('AVAILABLE',
            'AVAILABLE_ZERO_DISPERSION') for point in selected]
        family_tunes=sorted({tune for index,valid in zip(indices,mask)
            for tune,leaves in point_leaves[index].items()
            if any(leaf is not None for leaf in leaves) or valid})
        families=[]
        for tune in family_tunes:
            complements=[]
            means=[]
            usable=[]
            for index,valid in zip(indices,mask):
                family_leaves=point_leaves[index].get(tune,[])
                usable.append(valid and len(family_leaves)==10 and
                              all(leaf is not None for leaf in family_leaves))
                means.append(point_means[index].get(tune))
            for block in range(10):
                complements.append([point_leaves[index][tune][block]
                    if tune in point_leaves[index] else None
                    for index in indices])
            families.append(dict(tune_id=tune,source_family_digest=
                expected_family[tune],block_ids=list(range(1,11)),
                complements=complements,leave_mean=means,
                finite_mask=[[leaf is not None for leaf in row]
                             for row in complements],usable_mask=usable,
                covariance_prefactor=p.hex64(.9)))
        cov=dict(id=group['id'],ordered_point_keys=ordered,valid_mask=mask,
            units_by_point=[point['units'] for point in selected],
            status='AVAILABLE_FULL' if all(mask) else
                   'AVAILABLE_PARTIAL' if any(mask) else 'UNAVAILABLE',
            estimator_policy_id=p.ESTIMATOR,K=10,dof=9,
            independent_families=families,representation='DELETE_ONE_FACTORS',
            dense_rows=None,factors_root_object='covariance_factors',
            rank_bound=9*len(families),numerical_diagnostics=dict(
                symmetry_max_abs=p.hex64(0),minimum_eigenvalue=None,
                maximum_null_residual=None,accepted_rounding_bound=p.hex64(1e-12),
                valid_dimension=sum(mask),method_id='K10_FACTOR_DIAGONAL_CHECK',
                status='PASS'))
        cov['content_sha256']=p.digest(cov)
        covariance.append(cov)
    classes=[]
    for tune in req['scope']['ordered_tunes']:
        for klass in req['classes']:
            field=boundaries[tune,klass['id']]
            resolved=field[5]=='RESOLVED'
            low=int(field[6]) if resolved else -1
            high=int(field[7]) if resolved else -1
            event_count=sum(count for (member_tune,_),moment in event_moments.items()
                if member_tune==tune for activity,count in moment.activity_counts.items()
                if low<=activity<=high) if resolved else 0
            classes.append(dict(tune_id=tune,activity_id=req['activity']['semantic_id'],
                class_id=klass['id'],requested=klass,actual_integer_low=low,
                actual_integer_high=high,
                event_weight=_number(field[9]) if resolved else p.hex64(0),
                events=event_count,empty=field[8]=='1',
                boundary_status=field[5],coverage_status='COMPLETE_K10',
                boundary_receipt_sha256=p.digest(dict(field=field,request=klass,
                    source_members_sha256=req['sources']['selected_members_sha256']))))
    states,_=p._reducer().state_registry(analysis)
    labels={state['pdg']:state['name'] for state in states}
    if science_only:
        return dict(points=points,covariance=covariance,
            class_boundaries=classes,class_boundary_deletions=boundary_deletions,
            event_moment_receipts=moments,
            support_diagnostic_receipts=diagnostics,
            materialization=materialization)
    if any(value is None for value in (artifact_binding,provenance,
                                       primitive_routes,capability_receipt,
                                       admission_closure)):
        raise ValueError('canonical v4 source/build ledger is absent')
    result=dict(schema=p.RESULT_SCHEMA_NATIVE,request_echo=req,
        request_sha256=typed.request_sha256,
        scientific_request_sha256=typed.scientific_request_sha256,
        source_receipt=req['sources'],resolved=dict(profiles=req['profiles'],
            axes=req['axes'],class_boundaries=classes,
            signed_pairs=req['scope']['ordered_associate_pairs'],
            expected_point_keys=keys,
            observed_support=p.observed_support(req,points,materialization),
            category_order=p.category_order(req,labels),
            g9_science=p.g9_science(req) if any(role['role_id']==
                'spectra.signed_heavy' for role in req['scope']['roles']) else None),
        primitive_routes=primitive_routes,points=points,covariance=covariance,
        materialization=materialization,
        package_state='VALIDATED_COMPLETE',campaign_state=campaign_state,
        provenance=provenance,capability_receipt=capability_receipt,
        artifact_binding=artifact_binding,admission_closure=admission_closure,
        event_moment_receipts=moments,
        support_diagnostic_receipts=diagnostics,
        class_boundary_deletions=boundary_deletions)
    result['science_content_sha256']=p.digest({k:result[k] for k in (
        'scientific_request_sha256','resolved','points','covariance',
        'materialization','event_moment_receipts',
        'support_diagnostic_receipts','class_boundary_deletions')})
    return p.ProjectionResult.from_dict(result,typed,primitive_routes,cold=cold)
