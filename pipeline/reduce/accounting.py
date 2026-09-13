"""Accepted campaign attempt/exposure accounting through A's validator.

This inventory is independent of a query collection.  It reports declared
successful events for accepted sources and evidence-labelled discarded
attempts, never an inferred PYTHIA failure mechanism or projected event sum.
"""
from collections import Counter,defaultdict
import json
from pathlib import Path

from . import projection as p

SCHEMA='hadronization_campaign_attempt_accounting_v1'


def checked(path,expected_sha256,label):
    path=Path(path)
    p.validate(expected_sha256,'Digest',label+' SHA-256')
    p._reducer().reject_symlink_components(path,label)
    p._reducer().regular_file(path,label)
    if p.file_digest(path)!=expected_sha256:
        raise ValueError(label+' differs from trusted physical digest')
    return path


def inventory(campaign_path,campaign_sha256,manifest_path,manifest_sha256,
              attempts_path,attempts_sha256):
    """Validate all three accepted inputs, then report exact joined counts."""
    campaign_path=checked(campaign_path,campaign_sha256,'campaign descriptor')
    manifest_path=checked(manifest_path,manifest_sha256,'accepted raw manifest')
    attempts_path=checked(attempts_path,attempts_sha256,'attempt ledger')
    analyzer=p._reducer().analyzer_module()
    campaign=json.loads(campaign_path.read_text(encoding='utf-8'))
    adapter=analyzer.campaign_adapter(campaign)
    manifest=analyzer.load_manifest(manifest_path,campaign,adapter)
    attempts,observed_sha=analyzer.load_attempts(attempts_path)
    if observed_sha!=attempts_sha256:
        raise ValueError('attempt ledger changed during validation')
    analyzer.validate_attempts(campaign,adapter,manifest,attempts)
    if any(p.file_digest(path)!=digest for path,digest in (
            (campaign_path,campaign_sha256),(manifest_path,manifest_sha256),
            (attempts_path,attempts_sha256))):
        raise ValueError('campaign accounting input changed during validation')
    by_tune=defaultdict(lambda:dict(sources=0,successful_events=0,
                                    accepted_attempts=0,discarded_attempts=0))
    by_block=defaultdict(lambda:dict(sources=0,successful_events=0))
    for row in manifest:
        tune=row['tune'];block=row['block']
        by_tune[tune]['sources']+=1
        by_tune[tune]['successful_events']+=row['successful_events']
        by_block[tune,block]['sources']+=1
        by_block[tune,block]['successful_events']+=row['successful_events']
    evidence=Counter()
    for row in attempts:
        by_tune[row['tune']][row['outcome']+'_attempts']+=1
        evidence[row['outcome'],row['evidence_status']]+=1
    return dict(schema=SCHEMA,state='ACCEPTED_LEDGER_ONLY_NO_QUERY_CLOSURE',
        input_sha256=dict(campaign=campaign_sha256,raw_manifest=manifest_sha256,
                          attempts=attempts_sha256),
        campaign_id=campaign['campaign'],
        counts=dict(accepted_sources=len(manifest),attempts=len(attempts),
            accepted_attempts=sum(x['outcome']=='accepted' for x in attempts),
            discarded_attempts=sum(x['outcome']=='discarded' for x in attempts),
            successful_events=sum(x['successful_events'] for x in manifest)),
        by_tune=[dict(tune_id=tune,**by_tune[tune]) for tune in
                 campaign['tune_order']],
        by_block=[dict(tune_id=tune,block_id=block,**by_block[tune,block])
                  for tune in campaign['tune_order']
                  for block in range(1,adapter['block_count']+1)],
        attempt_evidence=[dict(outcome=outcome,evidence_status=status,count=count)
            for (outcome,status),count in sorted(evidence.items())],
        interpretation='discarded attempts are evidence-labelled submitted attempts; no failure mechanism is inferred')


def write(report,path):
    path=Path(path).absolute()
    p._reducer().reject_symlink_components(path,'accounting report')
    if path.exists() or path.is_symlink():raise FileExistsError(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='ascii',newline='\n') as stream:
        stream.write(p.canonical(report)+'\n')
    return dict(path=str(path),sha256=p.file_digest(path),bytes=path.stat().st_size)
