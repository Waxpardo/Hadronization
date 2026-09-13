"""Source-bound v4 metadata shared by the native result and cold ROOT writer.

These builders use the already authenticated A collection and event-row scan.
They do not evaluate an observable or substitute moments for a covariance Gram.
"""
from pathlib import Path

from . import projection as p


def event_moment_receipts(request,moments):
    value=request.to_dict() if hasattr(request,'to_dict') else request
    groups={}
    for member in value['sources']['members']:
        groups.setdefault((member['tune_id'],member['block_id']),[]).append(member)
    if set(moments)!=set(groups):
        raise ValueError('observed event moment tune/block domain differs')
    result=[]
    for (tune,block),members in sorted(groups.items()):
        moment=moments[tune,block]
        body=dict(schema='hadronization_event_weight_moments_v1',
            tune_id=tune,block_id=block,
            source_members_sha256=p.digest(sorted(members,key=lambda m:m['source_id'])),
            scope='SELECTED_ACCEPTED_SOURCE_EVENTS_BEFORE_OBSERVABLE_CUTS',
            events=moment.events,sumw=moment.sumw.hex(),
            sumw2=moment.sumw2.hex(),sumabsw=moment.sumabsw.hex(),
            event_weight_terms=moment.events)
        result.append(dict(body,content_sha256=p.digest(body)))
    p.validate(result,['EventMomentReceiptV4'])
    return result


def support_diagnostic_receipts(run_receipt,moment_receipts):
    moments={(row['tune_id'],row['block_id']):row for row in
             run_receipt['event_block_moments']}
    raw={(row['tune_id'],row['block_id']):row for row in
         run_receipt['raw_origin_closure_diagnostics']}
    expected={(row['tune_id'],row['block_id']) for row in moment_receipts}
    if set(moments)!=expected or set(raw)!=expected:
        raise ValueError('native support diagnostic tune/block domain differs')
    result=[]
    for receipt in moment_receipts:
        key=receipt['tune_id'],receipt['block_id']
        event= moments[key];diagnostic=raw[key]
        body=dict(schema='hadronization_observed_support_diagnostics_v1',
            tune_id=key[0],block_id=key[1],
            event_moments_sha256=receipt['content_sha256'],
            activity_counts=[dict(activity_bin=activity,events=count)
                for activity,count in event['activity_counts']],
            n_mpi_counts=[dict(n_mpi=n_mpi,events=count)
                for n_mpi,count in event['n_mpi_counts']],
            process_counts=[dict(process_code=code,events=count)
                for code,count in event['process_counts']],
            pthat_sum=event['pthat_sum'],hard_scale_sum=event['hard_scale_sum'],
            **{name:diagnostic[name] for name in (
                'natural_final_hadrons','natural_final_weighted_sum',
                'charm_constituents','charm_constituent_weighted_sum',
                'beauty_constituents','beauty_constituent_weighted_sum',
                'strict_selected_final_hadrons',
                'strict_selected_final_weighted_sum',
                'origin_pairs','closure_terms')})
        result.append(dict(body,content_sha256=p.digest(body)))
    p.validate(result,['SupportDiagnosticReceiptV4'])
    return result


def collection_binding(source):
    """Inventory only explicit verified-index members, never directory guesses."""
    index=source.index
    if index['schema']!='hadronization_query_collection_v1':
        raise ValueError('native v4 collection schema differs')
    if p.file_digest(source.index_path)!=source.expected_sha256:
        raise ValueError('native v4 collection index pin differs')
    rows=[]
    def record(file_id,role,ref,ordinal=None,tune=None):
        path=Path(ref['path'])
        if (path.is_symlink() or not path.is_file() or
                path.stat().st_size!=ref['bytes'] or
                p.file_digest(path)!=ref['sha256']):
            raise ValueError('native v4 collection member pin differs: '+file_id)
        rows.append(dict(file_id=file_id,role=role,shard_ordinal=ordinal,
            tune_id=tune,sha256=ref['sha256'],bytes=ref['bytes']))
    for shard in index['shards']:
        ordinal=shard['ordinal']
        stem='shard_{:04d}_'.format(ordinal)
        record(stem+'root','QUERY_SHARD_ROOT',shard['query_root'],ordinal)
        record(stem+'metadata','SHARD_METADATA',shard['metadata'],ordinal)
        record(stem+'manifest','SHARD_MANIFEST',
               shard['workspace_manifest'],ordinal)
    if index['layout']=='MERGED':
        for ordinal,partition in enumerate(index['partitions']):
            record('partition_{:04d}_root'.format(ordinal),'MERGED_SPARSE_ROOT',
                   partition['root'],tune=partition['tune'])
    elif index['partitions']:
        raise ValueError('sharded v4 collection has merged partitions')
    rows.sort(key=lambda row:row['file_id'])
    if len({row['file_id'] for row in rows})!=len(rows):
        raise ValueError('native v4 collection member ID duplicated')
    merged_partitions=[dict(tune_id=part['tune'],
        root_sha256=part['root']['sha256'],
        families=[dict(id=family,cell_digest=part['cell_digests'][family])
                  for family in sorted(part['families'])])
        for part in index['partitions']]
    binding=dict(kind='QUERY_COLLECTION',collection_schema=index['schema'],
        layout=index['layout'],collection_state=index['state'],
        collection_index_sha256=source.expected_sha256,
        collection_index_bytes=source.index_path.stat().st_size,
        collection_scientific_identity_sha256=index['scientific_identity_sha256'],
        member_files=rows,member_files_sha256=p.digest(rows),
        pair_proofs=source.pair_proofs,
        pair_proofs_sha256=p.digest(source.pair_proofs),
        merged_partitions=merged_partitions,
        merged_partitions_sha256=p.digest(merged_partitions))
    p.validate(binding,'CollectionBindingV4')
    return binding


def admission_closure(source, expected_sources_path, expected_sources_sha256,
                      *, work_path=None, expected_work_sha256=None,
                      closure_path=None, expected_closure_sha256=None):
    """Obtain A's independently pinned exact-domain/site admission proof."""
    if not hasattr(source.api, 'admission_closure'):
        raise ValueError('A query collection has no admission closure verifier')
    receipt=source.api.admission_closure(
        source.index_path,source.expected_sha256,
        expected_sources_path,expected_sources_sha256,
        work_path=work_path,expected_work_sha256=expected_work_sha256,
        closure_path=closure_path,
        expected_closure_sha256=expected_closure_sha256)
    p.validate(receipt,'AdmissionClosureV4')
    if (receipt['collection_index_sha256']!=source.expected_sha256 or
            receipt['collection_scientific_identity_sha256']!=source.index[
                'scientific_identity_sha256'] or
            receipt['index_state']!=source.index['state']):
        raise ValueError('A admission closure differs from native source')
    return receipt


def campaign_accounting(report):
    """Represent verified job attempts and unavailable all-attempt trials."""
    if report['schema']!='hadronization_campaign_attempt_accounting_v1' or \
            report['state']!='ACCEPTED_LEDGER_ONLY_NO_QUERY_CLOSURE':
        raise ValueError('native v4 campaign ledger state differs')
    by_tune=[];trials=[]
    for row in report['by_tune']:
        by_tune.append(dict(tune_id=row['tune_id'],sources=row['sources'],
            successful_events=row['successful_events'],
            submitted_attempts=row['accepted_attempts']+row['discarded_attempts'],
            accepted_attempts=row['accepted_attempts'],
            discarded_attempts=row['discarded_attempts']))
        trials.append(dict(tune_id=row['tune_id'],
            scope='ALL_SUBMITTED_CAMPAIGN_ATTEMPTS',count=None,
            status='UNAVAILABLE',reason_codes=[
                'EVENT_TRIAL_COUNTS_NOT_RECORDED_IN_VERIFIED_INPUTS']))
    result=dict(schema='hadronization_campaign_accounting_v4',
        scope=report['state'],input_sha256=report['input_sha256'],
        campaign_id=report['campaign_id'],counts=report['counts'],
        by_tune=by_tune,by_block=report['by_block'],
        attempt_evidence=report['attempt_evidence'],
        generator_event_trials_by_tune=trials)
    p.validate(result,'CampaignAccountingV4')
    return result


def primitive_routes(source,request,analysis,scan_metrics=None):
    """Declare the exact A sparse/support readers used by the native scan."""
    req=request.to_dict() if hasattr(request,'to_dict') else request
    profiles={item['id']:item for item in analysis['profiles']}
    structural=req['science_contract']['structural_registry_sha256']
    eta=analysis['pair_acceptance']['eta']['value']
    source_definitions=dict(profiles=analysis['profiles'],
        pair_acceptance=analysis['pair_acceptance'],
        axes={name:analysis['axes'][name] for name in ('pt','eta')},
        structural_registry_sha256=structural)
    p.validate(source_definitions,'SourceSelectionDefinitions')
    def objects(family,exact_rows=False):
        if exact_rows:
            return [(f'shard_{shard["ordinal"]:04d}/{name}',
                     shard['scientific_content_sha256'])
                    for shard in source.index['shards'] for name in
                    ('events','heavy','pairs','closure')]
        if source.index['layout']=='MERGED':
            return [(f'partition_{index:04d}/sparse_{family}',
                     item['cell_digests'][family])
                    for index,item in enumerate(source.index['partitions'])]
        return [(f'shard_{item["ordinal"]:04d}/sparse_{family}',
                 item['scientific_content_sha256'])
                for item in source.index['shards']]
    routes=[]
    def append(family,profile,route,predicate,axes,exact_rows=False):
        object_facts=objects(family,exact_rows)
        metrics=(scan_metrics or {}).get(family,{})
        routes.append(dict(primitive_family=family,profile_id=profile,
            source_kind='QUERY_ROOT',route=route,
            exactness={'NATIVE_ALIGNED_SPARSE':'ALIGNED_RECTANGLE',
                       'EXACT_ROWS':'BINARY64_ROWS'}[route],
            root_object_names=[name for name,_ in object_facts],
            object_content_digests=[digest for _,digest in object_facts],
            predicate_sha256=p.digest(predicate),resolved_axis_selection=axes,
            diagnostic_readers=[dict(purpose='EXACT_EVENT_AND_CLASS_ACCOUNTING',
                route='EXACT_ROWS',objects=['events','heavy','pairs','closure'])]
                if family in ('activity','kinematics','natural_final_heavy') else [],
            observed_input_cells=metrics.get('selected_cells',0),
            observed_input_rows=metrics.get('observed_rows',0)))
    append('activity',None,'NATIVE_ALIGNED_SPARSE',req['activity'],[])
    edges=source_definitions['axes']['pt']['edges']
    eta_axis=source_definitions['axes']['eta']
    for profile in req['profiles']:
        original=profiles[profile['id']]
        if profile!=p.normalized_profile(original,eta,structural):
            raise ValueError('native v4 route profile differs from A model')
        for family in ('pairs','triggers'):
            pair=family=='pairs'
            predicate=dict(profile=original if pair else
                {key:original[key] for key in ('id','trigger_pt')},
                pair_acceptance=analysis['pair_acceptance'])
            selections=[]
            for role in (('trigger_pt','associate_pt') if pair else
                         ('trigger_pt',)):
                cut=original[role]
                first=1 if cut is None else next((i+1 for i,edge in
                    enumerate(edges[:-1]) if edge>=cut['value']),len(edges))
                selections.append(dict(axis_id=role,predicate=profile[role],
                    included_regular_bins=list(range(first,len(edges))),
                    include_underflow=False,include_overflow=True,
                    endpoint_adjustment='NONE'))
            for role in (('trigger_eta','associate_eta') if pair else
                         ('trigger_eta',)):
                selections.append(dict(axis_id=role,predicate=profile[role],
                    included_regular_bins=list(range(1,eta_axis['bins']+1)),
                    include_underflow=False,include_overflow=False,
                    endpoint_adjustment='ARCHIVED_INCLUSIVE_HIGH'))
            append(family,profile['id'],'NATIVE_ALIGNED_SPARSE',
                   predicate,selections)
    if any(role['role_id']=='spectra.signed_heavy' for role in
           req['scope']['roles']):
        append('kinematics',None,'NATIVE_ALIGNED_SPARSE',
               p.g9_science(req),[])
    if any(role['role_id']=='accounting.natural_final_heavy' for role in
           req['scope']['roles']):
        append('natural_final_heavy',None,'EXACT_ROWS',
               dict(acceptance='NATURAL_FINAL_HEAVY'),[],True)
    p.validate_profile_routes(req['profiles'],structural,
                              source_definitions,routes)
    return source_definitions,routes
