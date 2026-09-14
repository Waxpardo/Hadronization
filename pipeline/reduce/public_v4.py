"""Public A v2.2 collection to self-contained native v4 numerical ROOT route."""

import argparse
from collections import Counter
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
from types import SimpleNamespace

from pipeline.query import collection as collection_api
from . import accounting, archive, archive_v4, native, native_runner
from . import native_v4, native_v4_result, projection as p


ROOT = Path(__file__).resolve().parents[2]
ANALYSIS = ROOT / 'config/analysis.json'
PACKAGE_SCHEMA = 'hadronization_public_v4_portable_package_v1'


def _json(path, expected_sha, label):
    path = Path(path).absolute()
    p._reducer().reject_symlink_components(path, label)
    p._reducer().regular_file(path, label)
    p.validate(expected_sha, 'Digest', label + ' SHA-256')
    if p.file_digest(path) != expected_sha:
        raise ValueError(label + ' differs from independently pinned SHA-256')
    return json.loads(path.read_text(encoding='utf-8'))


def _write(path, value):
    path = Path(path)
    if path.exists() or path.is_symlink():
        raise FileExistsError(path)
    with path.open('x', encoding='ascii', newline='\n') as stream:
        stream.write(json.dumps(value, sort_keys=True, indent=2) + '\n')
    return p.file_digest(path)


def _package_manifest(output, report, *, collection_index, expected_sources,
                      expected_sources_sha, site_work,
                      site_work_sha, collector_closure, collector_closure_sha,
                      merge_receipt, merge_receipt_sha):
    names = ['report.json', 'numerics.root', 'admission-closure.json',
             'native-run-receipt.json', 'source-build-ledger.json']
    names += ['exports/' + name for name in sorted(report['exports']['files'])]
    names += ['exports/receipt.json']
    files = {name: {'sha256': p.file_digest(output / name),
                    'bytes': (output / name).stat().st_size} for name in names}
    external = [{'role': role, 'locator': str(path) if path else None,
                 'sha256': digest, 'portable_status': 'NOT_CHECKED_EXTERNAL'}
                for role, path, digest in (
                    ('collection_index', collection_index, report['collection_index_sha256']),
                    ('expected_sources', expected_sources, expected_sources_sha),
                    ('site_work', site_work, site_work_sha),
                    ('collector_closure', collector_closure, collector_closure_sha),
                    ('merge_receipt', merge_receipt, merge_receipt_sha))]
    return {'schema': PACKAGE_SCHEMA, 'files': files,
            'science_content_sha256': report['science_content_sha256'],
            'root_sha256': report['root']['root_sha256'],
            'execution_attestation': external}


def _package_file(package, name, fact):
    if (not isinstance(name, str) or name.startswith('/') or
            Path(name).as_posix() != name or
            any(part in ('', '.', '..') for part in Path(name).parts)):
        raise ValueError('portable package has an unsafe required locator')
    path = package / name
    p._reducer().reject_symlink_components(path, 'portable package artifact')
    p._reducer().regular_file(path, 'portable package artifact')
    if (set(fact) != {'sha256', 'bytes'} or type(fact['bytes']) is not int or
            fact['bytes'] < 0 or path.stat().st_size != fact['bytes'] or
            p.file_digest(path) != fact['sha256']):
        raise ValueError('portable package required artifact differs: ' + name)
    return path


def _real_directory(path, label):
    path = Path(path).absolute()
    p._reducer().reject_symlink_components(path, label)
    if not path.is_dir() or path.is_symlink():
        raise ValueError(label + ' must be an existing nonsymlink directory')
    return path


def _git(*arguments):
    return subprocess.check_output(['git', '-C', str(ROOT), *arguments],
                                   text=True).strip()


def _source_snapshot(full):
    """A committed build is required for FULL; dirty TEST_ONLY is explicit."""
    head = _git('rev-parse', 'HEAD')
    tree = _git('rev-parse', 'HEAD^{tree}')
    dirty = bool(_git('status', '--porcelain'))
    if full and dirty:
        raise ValueError('full v4 release requires a clean committed source tree')
    paths = [name for name in _git('ls-files').splitlines()
             if name == 'hadronization' or name.startswith(
                 ('config/', 'data/', 'pipeline/', 'tests/'))]
    committed_paths = set(_git('ls-tree', '-r', '--name-only', 'HEAD').splitlines())
    rows = []
    for name in paths:
        file = ROOT / name
        if not file.is_file() or file.is_symlink():
            raise ValueError('tracked source file is absent or symlinked: ' + name)
        actual_blob = subprocess.check_output(['git', '-C', str(ROOT),
            'hash-object', str(file)], text=True).strip()
        # The TEST_ONLY integration candidate may have newly staged source
        # files before its one combined commit.  Preserve that distinction in
        # the ledger; FULL still requires a clean committed tree above.
        committed_blob = (_git('rev-parse', 'HEAD:' + name)
                          if name in committed_paths else None)
        if full and actual_blob != committed_blob:
            raise ValueError('full v4 source differs from committed blob: ' + name)
        rows.append(dict(path=name, bytes=file.stat().st_size,
                         sha256=p.file_digest(file), git_blob=actual_blob,
                         committed_git_blob=committed_blob))
    return dict(schema='hadronization_v4_source_build_ledger_v1',
                status='COMMITTED_SOURCE' if not dirty else
                    'PRECOMMIT_TEST_ONLY_SOURCE',
                integrated_science_commit=head, git_tree=tree,
                tracked_source_files=rows)


def _verify_source_snapshot(snapshot):
    if (_git('rev-parse', 'HEAD') != snapshot['integrated_science_commit']
            or _git('rev-parse', 'HEAD^{tree}') != snapshot['git_tree']):
        raise ValueError('v4 source commit/tree moved during native run')
    for row in snapshot['tracked_source_files']:
        file = ROOT / row['path']
        if (not file.is_file() or file.is_symlink() or
                file.stat().st_size != row['bytes'] or
                p.file_digest(file) != row['sha256']):
            raise ValueError('v4 tracked source changed during native run: '
                             + row['path'])
    if (snapshot['status'] == 'COMMITTED_SOURCE' and
            _git('status', '--porcelain')):
        raise ValueError('full v4 source tree became dirty during native run')


def _full_preflight(source, closure, snapshot):
    if source.index['state'] == 'TEST_ONLY':
        if closure['qualification'] != 'TEST_ONLY_DOMAIN_CLOSED':
            raise ValueError('TEST_ONLY source lacks exact-domain closure')
        return False
    if source.index['state'] != 'EXTERNAL_ACCEPTANCE_REQUIRED':
        raise ValueError('A collection state is not releasable')
    if (source.index['layout'] != 'MERGED' or not source.index['shards']
            or len(source.index['sources']) != closure['source_count']
            or len(source.index['partitions']) != len(source.index['tune_ordinals'])
            or set(source.index['tune_ordinals']) !=
                {'MONASH', 'JUNCTIONS', 'CLOSEPACKING'} or
            {part['tune'] for part in source.index['partitions']} !=
                {'MONASH', 'JUNCTIONS', 'CLOSEPACKING'} or
            any(set(part['families']) !=
                {'activity', 'closure', 'kinematics', 'pairs', 'triggers'}
                for part in source.index['partitions'])):
        raise ValueError('full v4 release requires complete physical MERGED collection')
    if (closure['qualification'] != 'FULL_ACCEPTED_DOMAIN_CLOSED'
            or not closure['domain_complete']
            or any(closure[key] is None for key in (
                'work_sha256', 'collector_closure_sha256',
                'external_pins_sha256', 'acquisition_manifest_sha256',
                'campaign_sha256'))):
        raise ValueError('full v4 release lacks independently pinned site/source closure')
    if snapshot['status'] != 'COMMITTED_SOURCE':
        raise ValueError('full v4 release lacks a committed source ledger')
    return True


def _selection(args, analysis):
    charm = args.charm_trigger
    signed = [pdg for sector in analysis['pair_query_registry'][
        'associate_pdgs'].values() for pdg in sector]
    return dict(profile_id=args.profile_id,
        activity_id=args.activity_id or analysis['activities'][0]['id'],
        reference_tune=args.reference_tune,
        trigger_pdgs=[charm, 4122, 521, 5122],
        baryon_meson_trigger_pdgs=[charm, 521], signed_pdgs=signed)


def _representative_request(source, args, analysis):
    """Bound a TEST_ONLY page-style domain without changing any formula."""
    tunes = args.tunes or list(source.index['tune_ordinals'])
    t1, _, _ = native.collect_t1(source, tunes)
    full = p.make_native_request(source, getattr(args, 'analysis', ANALYSIS), args.analysis_sha,
        tunes, sorted({key[2] for key in t1}), _selection(args, analysis))
    payload = full.to_dict()
    preferred = [-args.charm_trigger, args.charm_trigger, -4122, 4122,
                 -521, 521, -5122, 5122]
    order = {pdg: rank for rank, pdg in enumerate(preferred)}
    chosen = {}
    for key in full.expected_point_keys:
        curve = key['curve']
        role = curve['role_id']
        if role in ('spectra.signed_heavy',
                    'accounting.natural_final_heavy') and curve[
                        'associate_pdg'] not in (args.charm_trigger, 521):
            continue
        bucket = (role, curve['quantity'], curve['component'],
            curve['axis_id'], curve['tune_id'], curve['reference_tune_id'],
            curve['trigger_pdg'], curve['class_id'],
            curve['associate_pdg'] if role in (
                'spectra.signed_heavy', 'accounting.natural_final_heavy')
                else None)
        bin_index = key['bins'][0]['index'] if key['bins'] else -1
        rank = (order.get(curve['associate_pdg'], len(order)), bin_index,
                p.canonical(key))
        if bucket not in chosen or rank < chosen[bucket][0]:
            chosen[bucket] = (rank, key)
    keys = sorted((entry[1] for entry in chosen.values()), key=p.canonical)
    selected = {p.canonical(key) for key in keys}
    curves = {p.canonical(key['curve']) for key in keys}
    active_roles = {key['curve']['role_id'] for key in keys}
    point_roles = {key['curve']['role_id'] for key in full.expected_point_keys}
    if active_roles != point_roles:
        raise ValueError('representative v4 request lost a paper role')
    payload['scope']['roles'] = [dict(role,
        required_curve_keys=[curve for curve in role['required_curve_keys']
                             if p.canonical(curve) in curves],
        ordered_panels=[panel for panel in role['ordered_panels'] if
            panel['role_id'] in active_roles])
        for role in payload['scope']['roles']]
    payload['observables'] = [dict(observable,
        joint_point_domain=[key for key in observable['joint_point_domain']
                            if p.canonical(key) in selected])
        for observable in payload['observables'] if any(p.canonical(key) in
            selected for key in observable['joint_point_domain'])]
    payload['statistics']['covariance_groups'] = [dict(
        id='representative_native_v4', ordered_point_keys=keys,
        representation='DELETE_ONE_FACTORS',
        required_cross_groups=sorted(active_roles))]
    return p.ProjectionRequest.from_dict(payload, cold=True)


def _campaign_accounting(snapshot):
    names = ('data/campaign.json', 'data/raw_manifest.jsonl',
             'data/attempts.csv')
    pins = {row['path']: row['sha256'] for row in
            snapshot['tracked_source_files']}
    return native_v4.campaign_accounting(accounting.inventory(
        *(item for name in names for item in (ROOT / name, pins[name]))))


def _provenance(source, request, run, ledger, analysis, campaign):
    req = request.to_dict()
    lineage = source.source_lineage(req['scope']['ordered_tunes'])
    if lineage['source_selection'] != req['sources']:
        raise ValueError('public v4 request/source lineage differs')
    files = {row['path']: row['sha256'] for row in ledger[
        'tracked_source_files']}
    if (files['config/analysis.json'] != source.index['analysis_sha256'] or
            req['bindings']['analysis_config_sha256'] != run[
                'interpretation_analysis_sha256'] or
            files['pipeline/reduce/native_engine.cpp'] != run['build'][
                'source_sha256'] or
            files['pipeline/reduce/statistics.hpp'] != run['build'][
                'statistics_sha256']):
        raise ValueError('public v4 source/build bytes differ')
    binary = Path(run['build']['binary_path']) if 'binary_path' in run[
        'build'] else None
    if binary is None:
        identity = run['build']['build_identity_sha256']
        binary = Path(run['request_path']).parent / 'build' / (
            'native-engine-' + identity[:20])
    if p.file_digest(binary) != run['build']['binary_sha256']:
        raise ValueError('public v4 observed native binary differs')
    import ROOT as root_api
    root_version = str(root_api.gROOT.GetVersion())
    compiler = run['build']['compiler_id']
    compiler_version = run['build']['compiler_version']
    flags = ['-std=c++17', '-O2', '-Wall', '-Wextra', '-Wpedantic',
             '-Werror', '-ffp-contract=off']
    runtime = dict(os=platform.system(), architecture=platform.machine(),
        root_version=root_version, compiler_id=compiler,
        compiler_version=compiler_version, effective_cpp_standard='c++17',
        compile_flags=flags, link_flags=[], dependency_recipe_sha256=p.digest(
            dict(root_version=root_version, native_link_flags=[],
                 native_compiler=compiler)))
    definitions = dict(profiles=analysis['profiles'],
        pair_acceptance=analysis['pair_acceptance'],
        axes={key: analysis['axes'][key] for key in ('pt', 'eta')},
        structural_registry_sha256=req['science_contract'][
            'structural_registry_sha256'])
    p.validate(definitions, 'SourceSelectionDefinitions')
    campaign_json = json.loads((ROOT / 'data/campaign.json').read_text())
    limitations = ['RAW_V7_ANCESTRY_LIMITS', 'FINITE_MC_ONLY',
        'PHASE_A_INCLUSIVE_NO_FINAL_HADRON_PT_FLOOR',
        'G9_ALL_ORIGINS_NO_PT_FLOOR',
        'EVENT_TRIAL_COUNTS_NOT_RECORDED_IN_VERIFIED_INPUTS']
    if source.index['state'] == 'TEST_ONLY':
        limitations.append('TEST_ONLY_SYNTHETIC_NO_PHYSICS')
    if ledger['status'] != 'COMMITTED_SOURCE':
        limitations.append('PRECOMMIT_TEST_ONLY_SOURCE')
    return dict(campaign_descriptor_sha256=req['sources'][
            'campaign_descriptor_sha256'],
        source_members_sha256=req['sources']['selected_members_sha256'],
        analysis_config_sha256=req['bindings']['analysis_config_sha256'],
        particle_registry_sha256=req['bindings']['particle_registry_sha256'],
        selection_definitions_sha256=p.digest(dict(profiles=req['profiles'],
            activity=req['activity'], classes=req['classes'])),
        source_selection_definitions=definitions,
        activity_definition_sha256=req['bindings'][
            'activity_definition_sha256'],
        producer_commit=lineage['accepted_raw_producer_commit'],
        integrated_science_commit=ledger['integrated_science_commit'],
        formula_source_sha256=run['build']['source_sha256'],
        statistics_source_sha256=run['build']['statistics_sha256'],
        query_source_sha256=files['pipeline/query/query.cpp'],
        normalized_runtime_id=p.digest(runtime), runtime=runtime,
        build_recipe_sha256=run['build']['build_identity_sha256'],
        observed_binary_sha256=run['build']['binary_sha256'],
        generator_name='PYTHIA', generator_version=campaign_json['runtime'][
            'pythia_version'], collision_system=campaign_json['physics']['beam'],
        energy_gev=p.hex64(campaign_json['physics']['sqrt_s_gev']),
        successful_events_by_tune=req['sources']['expected_events_by_tune'],
        uncertainty_scope='FINITE_MC_ONLY', data_limitations=limitations,
        parent_artifact_digests=sorted([ledger['ledger_sha256'],
            source.expected_sha256,
            source.index['scientific_identity_sha256'],
            req['sources']['selected_members_sha256']]),
        campaign_accounting=campaign)


def _moments(run):
    return {(row['tune_id'], row['block_id']): SimpleNamespace(
        events=row['events'], sumw=float.fromhex(row['sumw']),
        sumw2=float.fromhex(row['sumw2']),
        sumabsw=float.fromhex(row['sumabsw']),
        activity_counts=dict(row['activity_counts']))
        for row in run['event_block_moments']}


def _capabilities(request):
    req = request.to_dict()
    return [dict(capability_id=capability, supported=True, reason=None,
        source_fields=[dict(object='query_native_sparse',
            column_or_axis='tune,block,activity,profile,pdg,bin'),
            dict(object='query_exact_support',
                 column_or_axis='events,heavy,pairs,closure')],
        supported_profile_ids=[row['id'] for row in req['profiles']],
        supported_activity_ids=[req['activity']['semantic_id']],
        supported_axes=req['axes'],
        structural_acceptance_id=req['science_contract'][
            'structural_registry_sha256'],
        allowed_predicates=['RECTANGLE', 'EXACT_RANGE'],
        requires_protected_rebuild=False)
        for capability in req['execution']['required_capabilities']]


def run(args):
    work_root = _real_directory(args.work_root, 'v4 work root')
    os.environ['TMPDIR'] = str(work_root)
    tempfile.tempdir = None
    output = Path(args.output_dir).absolute()
    p._reducer().reject_symlink_components(output, 'v4 output directory')
    _real_directory(output.parent, 'v4 output parent')
    if output.exists() or output.is_symlink():
        raise FileExistsError(output)
    if ANALYSIS.is_symlink():
        raise ValueError('public v4 shipped analysis is symlinked')
    analysis = _json(args.analysis, args.analysis_sha, 'v2.2 requested analysis')
    from pipeline.query import model as model_api
    checked, normalized_sha = model_api.checked_analysis(Path(args.analysis))
    if normalized_sha != args.analysis_sha or checked != analysis or analysis[
            'version'] != '2.2.0':
        raise ValueError('public v4 route requires normalized A v2.2 analysis')
    source = native.NativeCollection(args.collection_index,
                                     args.collection_index_sha, collection_api)
    if source.index['analysis_sha256'] != p.file_digest(ANALYSIS):
        raise ValueError('A collection/shipped construction analysis binding differs')
    construction, _ = model_api.checked_analysis(ANALYSIS)
    model_api.compatible_interpretation(construction, analysis)
    closure = native_v4.admission_closure(source, args.expected_sources,
        args.expected_sources_sha, work_path=args.site_work,
        expected_work_sha256=args.site_work_sha,
        closure_path=args.collector_closure,
        expected_closure_sha256=args.collector_closure_sha,
        merge_receipt_path=args.merge_receipt,
        expected_merge_receipt_sha256=args.merge_receipt_sha)
    snapshot = _source_snapshot(source.index['state'] != 'TEST_ONLY')
    full = _full_preflight(source, closure, snapshot)
    if args.tunes and (len(args.tunes) != len(set(args.tunes)) or
            set(args.tunes) != set(source.index['tune_ordinals'])):
        raise ValueError('public v4 route requires the complete collection tune domain')
    if args.representative and (full or args.request):
        raise ValueError('representative scope is TEST_ONLY and cannot override a pinned request')
    if args.request:
        if not args.request_sha:
            raise ValueError('pinned request requires --request-sha')
        request = p.ProjectionRequest.from_dict(_json(args.request,
            args.request_sha, 'v4 paper request'), cold=True)
        req = request.to_dict()
        if req['completion']['require_campaign_complete'] != full:
            raise ValueError('request completion differs from authenticated A state')
        if set(req['scope']['ordered_tunes']) != set(source.index[
                'tune_ordinals']):
            raise ValueError('pinned request omits a collection tune')
        if (req['sources'] != source.source_lineage(req['scope'][
                'ordered_tunes'])['source_selection'] or
                req['bindings']['analysis_config_sha256'] != args.analysis_sha):
            raise ValueError('pinned request/source/analysis differs')
        native_runner.require_full_campaign_input(source, req)
    elif args.request_sha:
        raise ValueError('--request-sha requires --request')
    elif args.representative:
        request = _representative_request(source, args, analysis)
    else:
        request = None
    output.mkdir(mode=0o700)
    run_dir = Path(tempfile.mkdtemp(prefix='v4-native-', dir=work_root))
    if request is None:
        tunes = args.tunes or list(source.index['tune_ordinals'])
        receipt = native_runner.run_diagnostic(args.collection_index,
            args.collection_index_sha, args.analysis, args.analysis_sha, None,
            run_dir, selected_tunes=tunes,
            selection=_selection(args, analysis))
    else:
        receipt = native_runner.run_diagnostic(args.collection_index,
            args.collection_index_sha, args.analysis, args.analysis_sha, request,
            run_dir)
    _verify_source_snapshot(snapshot)
    native_receipt_path = output / 'native-run-receipt.json'
    _write(native_receipt_path, receipt)
    request = p.ProjectionRequest.from_dict(json.loads(Path(receipt[
        'request_path']).read_text()), cold=True)
    if request.to_dict()['completion']['require_campaign_complete'] != full:
        raise ValueError('native request completion differs from A source state')
    native_binary = run_dir / 'build' / ('native-engine-' + receipt[
        'build']['build_identity_sha256'][:20])
    frozen_binary = output / 'native-engine'
    with native_binary.open('rb') as source_binary, frozen_binary.open('xb') as target_binary:
        shutil.copyfileobj(source_binary, target_binary)
    if p.file_digest(frozen_binary) != receipt['build']['binary_sha256']:
        raise ValueError('public v4 binary copy differs from observed build')
    ledger = dict(snapshot, build_receipt=dict(receipt['build'],
        binary_path=str(frozen_binary),
        native_run_receipt_sha256=p.file_digest(native_receipt_path),
        collection_index_sha256=source.expected_sha256,
        analysis_sha256=args.analysis_sha))
    ledger_path = output / 'source-build-ledger.json'
    ledger_sha = _write(ledger_path, ledger)
    ledger['ledger_sha256'] = ledger_sha
    campaign = _campaign_accounting(snapshot)
    provenance = _provenance(source, request, receipt, ledger, analysis,
                             campaign)
    binding = native_v4.collection_binding(source)
    definitions, routes = native_v4.primitive_routes(source, request, analysis)
    if definitions != provenance['source_selection_definitions']:
        raise ValueError('public v4 primitive/source definitions differ')
    result = native_v4_result.from_verified_diagnostic(request, receipt,
        _moments(receipt), binding, provenance, routes,
        _capabilities(request), analysis,
        campaign_state='FULL_ACCEPTED_CAMPAIGN' if full else 'PARTIAL_SAMPLE',
        admission_closure=closure)
    root = output / 'numerics.root'
    written = archive.write(result.to_dict(), root, work_root)
    cold = archive.read(root, work_root, written['root_sha256'],
                        written['value_sha256'])
    if cold != result.to_dict():
        raise ValueError('public v4 independent cold ROOT differs')
    exports = archive_v4.export(root, written['root_sha256'],
                                written['value_sha256'], output / 'exports')
    closure_sha = _write(output / 'admission-closure.json', closure)
    statuses = Counter((row['center_status'], row['uncertainty_status'])
                       for row in cold['points'])
    report = dict(schema='hadronization_public_v4_numerical_report_v1',
        source_state=source.index['state'],
        campaign_state='FULL_ACCEPTED_CAMPAIGN' if full else 'PARTIAL_SAMPLE',
        source_ledger_status=snapshot['status'],
        source_ledger_path=str(ledger_path),
        source_ledger_sha256=ledger_sha,
        admission_closure_path=str(output / 'admission-closure.json'),
        admission_closure_sha256=closure_sha,
        native_run_receipt_path=str(native_receipt_path),
        native_run_receipt_sha256=p.file_digest(native_receipt_path),
        collection_index_sha256=source.expected_sha256,
        merge_lineage_sha256=args.merge_receipt_sha,
        analysis_sha256=args.analysis_sha,
        request_sha256=request.request_sha256,
        scientific_request_sha256=request.scientific_request_sha256,
        root=written, exports=exports, points=len(cold['points']),
        point_status_counts=[dict(center_status=center,
            uncertainty_status=uncertainty, count=count)
            for (center, uncertainty), count in sorted(statuses.items())],
        support_diagnostic_receipts=len(cold['support_diagnostic_receipts']),
        class_boundary_deletions=len(cold['class_boundary_deletions']),
        covariance_groups=len(cold['covariance']),
        science_content_sha256=cold['science_content_sha256'])
    report_sha = _write(output / 'report.json', report)
    package_sha = _write(output / 'package-manifest.json',
        _package_manifest(output, report,
            collection_index=args.collection_index,
            expected_sources=args.expected_sources,
            expected_sources_sha=args.expected_sources_sha,
            site_work=args.site_work, site_work_sha=args.site_work_sha,
            collector_closure=args.collector_closure,
            collector_closure_sha=args.collector_closure_sha,
            merge_receipt=args.merge_receipt,
            merge_receipt_sha=args.merge_receipt_sha))
    print(p.canonical(dict(root=str(root), root_sha256=written['root_sha256'],
        value_sha256=written['value_sha256'], points=len(cold['points']),
        science_content_sha256=cold['science_content_sha256'],
        campaign_state=report['campaign_state'],
        report=str(output / 'report.json'), report_sha256=report_sha,
        package_manifest_sha256=package_sha)))


def _verify(args):
    portable = args.mode == 'portable'
    if portable:
        if args.package_dir is None or args.package_manifest_sha is None:
            raise ValueError('portable verification requires package directory and independently pinned manifest SHA')
        package = _real_directory(args.package_dir, 'portable package directory')
        manifest = _json(package / 'package-manifest.json',
                         args.package_manifest_sha, 'portable package manifest')
        if (manifest.get('schema') != PACKAGE_SCHEMA or
                not isinstance(manifest.get('files'), dict) or
                set(manifest) != {'schema', 'files', 'science_content_sha256',
                                  'root_sha256', 'execution_attestation'}):
            raise ValueError('portable package manifest schema differs')
        files = manifest['files']
        required = {'report.json', 'numerics.root', 'admission-closure.json',
                    'native-run-receipt.json', 'source-build-ledger.json'}
        if not required.issubset(files):
            raise ValueError('portable package required locator is absent')
        paths = {name: _package_file(package, name, fact)
                 for name, fact in files.items()}
        report = _json(paths['report.json'], files['report.json']['sha256'],
                       'portable v4 report')
        ledger_path, closure_path, native_path = (paths[name] for name in
            ('source-build-ledger.json', 'admission-closure.json',
             'native-run-receipt.json'))
        root = paths['numerics.root']
        if (args.root is not None or args.report is not None or args.report_sha is not None):
            raise ValueError('portable verification uses package-relative artifacts only')
    else:
        if args.report is None or args.report_sha is None or args.root is None:
            raise ValueError('producer verification requires root, report and independent report SHA')
        report = _json(args.report, args.report_sha, 'v4 report')
        ledger_path = report['source_ledger_path']
        closure_path = report['admission_closure_path']
        native_path = report['native_run_receipt_path']
        root = Path(args.root).absolute()
    if report.get('schema') != 'hadronization_public_v4_numerical_report_v1':
        raise ValueError('public v4 report schema differs')
    ledger = _json(ledger_path,
        report['source_ledger_sha256'], 'v4 source/build ledger')
    closure = _json(closure_path,
        report['admission_closure_sha256'], 'v4 admission closure')
    native_receipt = _json(native_path,
        report['native_run_receipt_sha256'], 'v4 native run receipt')
    if ledger['build_receipt']['native_run_receipt_sha256'] != report['native_run_receipt_sha256']:
        raise ValueError('public v4 observed build/receipt differs')
    if not portable:
        binary = Path(ledger['build_receipt']['binary_path'])
        p._reducer().reject_symlink_components(binary, 'v4 native binary')
        p._reducer().regular_file(binary, 'v4 native binary')
        if p.file_digest(binary) != ledger['build_receipt']['binary_sha256']:
            raise ValueError('public v4 observed binary differs')
        _verify_source_snapshot(ledger)
        locator_manifest_path = Path(args.report).absolute().parent / 'package-manifest.json'
        locator_manifest = json.loads(locator_manifest_path.read_text(encoding='utf-8'))
        if locator_manifest.get('schema') != PACKAGE_SCHEMA:
            raise ValueError('producer package locator manifest differs')
        locators = {item['role']: item for item in
                    locator_manifest['execution_attestation']}
        if set(locators) != {'collection_index', 'expected_sources',
                            'site_work', 'collector_closure', 'merge_receipt'}:
            raise ValueError('producer execution locator roles differ')
        if (locators['collection_index']['sha256'] != report['collection_index_sha256'] or
                locators['expected_sources']['sha256'] != closure['expected_sources_sha256'] or
                locators['site_work']['sha256'] != closure['work_sha256'] or
                locators['collector_closure']['sha256'] != closure['collector_closure_sha256'] or
                locators['merge_receipt']['sha256'] != report.get('merge_lineage_sha256')):
            raise ValueError('producer execution locator pins differ from report')
        observed_closure = collection_api.admission_closure(
            Path(locators['collection_index']['locator']),
            report['collection_index_sha256'],
            Path(locators['expected_sources']['locator']),
            closure['expected_sources_sha256'],
            work_path=locators['site_work']['locator'],
            expected_work_sha256=closure['work_sha256'],
            closure_path=locators['collector_closure']['locator'],
            expected_closure_sha256=closure['collector_closure_sha256'],
            merge_receipt_path=locators['merge_receipt']['locator'],
            expected_merge_receipt_sha256=report.get('merge_lineage_sha256'))
        if observed_closure != closure:
            raise ValueError('producer execution collection closure differs')
    if not portable and root != Path(report['root']['path']).absolute():
        raise ValueError('public v4 report/ROOT path differs')
    if portable and (manifest['science_content_sha256'] != report['science_content_sha256'] or
                     manifest['root_sha256'] != report['root']['root_sha256'] or
                     set(files) != {'report.json', 'numerics.root',
                                    'admission-closure.json', 'native-run-receipt.json',
                                    'source-build-ledger.json'} |
                                    {'exports/' + name for name in report['exports']['files']} |
                                    {'exports/receipt.json'}):
        raise ValueError('portable package manifest/science domain differs')
    value = archive_v4.read(root, report['root']['root_sha256'],
                            report['root']['value_sha256'])
    if (value['science_content_sha256'] != report['science_content_sha256']
            or len(value['points']) != report['points']
            or value['campaign_state'] != report['campaign_state']
            or value['artifact_binding']['collection_index_sha256'] !=
                report['collection_index_sha256'] or
            value['provenance']['integrated_science_commit'] !=
                ledger['integrated_science_commit'] or
            value['admission_closure'] != closure or
            native_receipt['request_sha256'] != report['request_sha256'] or
            native_receipt['collection_index_sha256'] !=
                report['collection_index_sha256']):
        raise ValueError('public v4 report/cold science differs')
    statuses = Counter((row['center_status'], row['uncertainty_status'])
                       for row in value['points'])
    if ([dict(center_status=center, uncertainty_status=uncertainty,
              count=count) for (center, uncertainty), count in
              sorted(statuses.items())] != report['point_status_counts'] or
            len(value['support_diagnostic_receipts']) !=
                report['support_diagnostic_receipts'] or
            len(value['class_boundary_deletions']) !=
                report['class_boundary_deletions'] or
            len(value['covariance']) != report['covariance_groups']):
        raise ValueError('public v4 report point/support domain differs')
    with tempfile.TemporaryDirectory(prefix='v4-export-verify-') as scratch:
        exported = archive_v4.export(root, report['root']['root_sha256'],
                                     report['root']['value_sha256'],
                                     Path(scratch) / 'exports')
        if exported != report['exports']:
            raise ValueError('public v4 compact exports differ from numerical ROOT')
        expected_receipt_sha = p.file_digest(Path(scratch) / 'exports' / 'receipt.json')
    export_dir = package / 'exports' if portable else Path(report['root']['path']).parent / 'exports'
    for name, digest in report['exports']['files'].items():
        export_path = export_dir / name
        if not export_path.is_file() or export_path.is_symlink() or p.file_digest(export_path) != digest:
            raise ValueError('public v4 required compact export differs: ' + name)
    if p.file_digest(export_dir / 'receipt.json') != expected_receipt_sha:
        raise ValueError('public v4 export receipt differs from numerical ROOT')
    if portable:
        attestations = manifest['execution_attestation']
        if (not isinstance(attestations, list) or
                any(not isinstance(item, dict) or set(item) !=
                    {'role', 'locator', 'sha256', 'portable_status'} or
                    item['portable_status'] != 'NOT_CHECKED_EXTERNAL' or
                    (item['locator'] is None) != (item['sha256'] is None)
                    for item in attestations)):
            raise ValueError('portable external execution attestation status differs')
        pins = {item['role']: item['sha256'] for item in attestations}
        if (len(pins) != len(attestations) or
                pins != {'collection_index': report['collection_index_sha256'],
                         'expected_sources': closure['expected_sources_sha256'],
                         'site_work': closure['work_sha256'],
                         'collector_closure': closure['collector_closure_sha256'],
                         'merge_receipt': report.get('merge_lineage_sha256')}):
            raise ValueError('portable external execution pins differ from report')
        status = 'EXTERNAL_EXECUTION_NOT_CHECKED'
    else:
        status = 'PRODUCER_SOURCE_BUILD_AND_COLLECTION_CHECKED'
    return report, value, status


def parser():
    top = argparse.ArgumentParser(prog='hadronization reduce',
        description='A v2.2 MERGED collection to native v4 typed numerics')
    sub = top.add_subparsers(dest='command', required=True)
    command = sub.add_parser('run', help='build immutable typed v4 numerics')
    command.add_argument('--collection-index', type=Path, required=True)
    command.add_argument('--collection-index-sha', required=True)
    command.add_argument('--expected-sources', type=Path, required=True)
    command.add_argument('--expected-sources-sha', required=True)
    command.add_argument('--analysis', type=Path, default=ANALYSIS)
    command.add_argument('--analysis-sha', required=True)
    command.add_argument('--request', type=Path)
    command.add_argument('--request-sha')
    command.add_argument('--work-root', type=Path, required=True)
    command.add_argument('--output-dir', type=Path, required=True)
    command.add_argument('--site-work', type=Path)
    command.add_argument('--site-work-sha')
    command.add_argument('--collector-closure', type=Path)
    command.add_argument('--collector-closure-sha')
    command.add_argument('--merge-receipt', type=Path)
    command.add_argument('--merge-receipt-sha')
    command.add_argument('--tunes', nargs='+')
    command.add_argument('--profile-id', default='inclusive')
    command.add_argument('--activity-id')
    command.add_argument('--reference-tune', default='MONASH')
    command.add_argument('--charm-trigger', type=int, choices=(421, 411),
                         default=421)
    command.add_argument('--representative', action='store_true',
        help='bounded all-role TEST_ONLY page-style request')
    for name in ('verify', 'explain'):
        item = sub.add_parser(name, help='cold-check typed v4 ROOT and report')
        item.add_argument('--mode', choices=('producer', 'portable'), default='producer')
        item.add_argument('--root', type=Path)
        item.add_argument('--report', type=Path)
        item.add_argument('--report-sha')
        item.add_argument('--package-dir', type=Path)
        item.add_argument('--package-manifest-sha')
    return top


def main(arguments=None):
    args = parser().parse_args(arguments)
    try:
        if args.command == 'run':
            run(args)
        else:
            report, value, verification_status = _verify(args)
            if args.command == 'explain':
                print(json.dumps(report, sort_keys=True, indent=2))
            else:
                print(p.canonical(dict(root=str((Path(args.root) if args.root else
                    Path(args.package_dir) / 'numerics.root').absolute()),
                    root_sha256=report['root']['root_sha256'],
                    value_sha256=report['root']['value_sha256'],
                    science_content_sha256=value['science_content_sha256'],
                    points=len(value['points']),
                    campaign_state=value['campaign_state'],
                    verification_status=verification_status)))
        return 0
    except (OSError, ValueError, RuntimeError,
            subprocess.CalledProcessError) as error:
        print('ERROR: ' + str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
