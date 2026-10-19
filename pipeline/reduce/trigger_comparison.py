"""Compare trigger-normalized yields with the native joint-block estimator."""

import json
import math
import os
from pathlib import Path
import tempfile

from . import archive_v4, projection as p

ROOT_DIR = Path(__file__).resolve().parents[2]
SCHEMA = 'hadronization_trigger_comparison_v1'
RECIPE = ROOT_DIR / 'config/trigger-comparison.json'
OBJECT_NAME = 'trigger-comparison.root'
AVAILABLE = {'AVAILABLE', 'AVAILABLE_ZERO_DISPERSION'}
FIELDS = dict(index='u', semantic_id='s', sector='s', tune='s', slot='u',
              numerator_trigger='i', denominator_trigger='i',
              numerator_associate='i', denominator_associate='i',
              numerator_id='s', denominator_id='s', source_family_sha256='s',
              center_present='b', center='d', error_present='b', error='d',
              variance_present='b', variance='d',
              value_status='s', uncertainty_status='s', reasons='s')
LEAF_FIELDS = dict(point='u', block='u', present='b', usable='b',
                   leaf='d', mean_present='b', mean='d', factor='d')


def checked_recipe(recipe):
    if (not isinstance(recipe, dict) or set(recipe) != {
            'schema', 'profile_id', 'class_id', 'sectors'} or
            recipe['schema'] != 'hadronization_trigger_comparison_recipe_v1' or
            not isinstance(recipe['profile_id'], str) or not recipe['profile_id'] or
            type(recipe['class_id']) is not int or recipe['class_id'] != 0 or
            not isinstance(recipe['sectors'], list) or
            any(not isinstance(item, dict) for item in recipe['sectors']) or
            [item.get('id') for item in recipe['sectors']] != ['charm', 'beauty']):
        raise ValueError('trigger comparison recipe differs')
    for sector in recipe['sectors']:
        if set(sector) != {'id', 'numerator_trigger', 'denominator_trigger',
                           'associate_pairs'}:
            raise ValueError('trigger comparison sector fields differ')
        triggers = [sector['numerator_trigger'], sector['denominator_trigger']]
        if any(type(v) is not int or not v for v in triggers) or len(set(triggers)) != 2:
            raise ValueError('trigger comparison identities differ')
        pairs = sector['associate_pairs']
        if not isinstance(pairs, list) or not pairs or any(
                not isinstance(pair, list) or len(pair) != 2 or
                any(type(v) is not int or not v for v in pair) for pair in pairs):
            raise ValueError('trigger comparison associate pairs differ')
        if any(len({pair[i] for pair in pairs}) != len(pairs) for i in range(2)):
            raise ValueError('trigger comparison associates repeat')
    return recipe


def native():
    import ROOT
    if not hasattr(ROOT, 'HadronizationTriggerComparison'):
        ROOT.gInterpreter.AddIncludePath(str(ROOT_DIR))
        if not ROOT.gInterpreter.Declare(r'''
#include "pipeline/reduce/statistics.hpp"
namespace HadronizationTriggerComparison {
using namespace Hadronization::Reduction;
DenominatorSeries Parent(const std::vector<std::vector<double>>& b,
                         unsigned column, bool survives, const std::string& id) {
  DenominatorSeries d; d.id=id; d.exact=true; d.algebraicallySurvives=survives;
  for (const auto& row:b) d.blocks.push_back(row[column]);
  return d;
}
JackknifeResult Estimate(const std::vector<std::vector<double>>& b) {
  // Columns: meson net count, meson triggers, baryon net count, baryon triggers.
  return PooledDeleteOne(b,[](const auto& x)->FunctionValue {
    if (x[0]==0. || x[1]==0. || x[3]==0.)
      return {false,{},"POOLED_DENOMINATOR_ZERO"};
    return {true,{(x[2]/x[3])/(x[0]/x[1])},{}};
  }, {Parent(b,0,true,"denominator_net_count"),
      Parent(b,3,true,"numerator_trigger_count"),
      Parent(b,1,false,"denominator_trigger_count")});
}
}
'''):
            raise RuntimeError('native trigger comparison compilation failed')
    return ROOT


def estimate(blocks):
    if len(blocks) != 10 or any(len(row) != 4 or any(
            not math.isfinite(x) or x != int(x) or abs(x) >= 2**53
            for x in row) for row in blocks):
        raise ValueError('trigger comparison requires exact K10 count primitives')
    root = native()
    matrix = root.std.vector('std::vector<double>')()
    for row in blocks:
        values = root.std.vector('double')()
        for value in row:
            values.push_back(value)
        matrix.push_back(values)
    result = root.HadronizationTriggerComparison.Estimate(matrix)
    def scalar(values):
        return float(values[0]).hex() if len(values) else None
    return dict(center=scalar(result.center), error=scalar(result.standardError),
                variance=scalar(result.diagonalVariance),
                value_status=str(result.valueStatus),
                uncertainty_status=str(result.uncertaintyStatus),
                reasons=list(map(str, result.reasons)),
                leaves=[scalar(row) for row in result.complements],
                leave_mean=scalar(result.leaveMean))


def _parent_blocks(point, tune):
    rows = sorted(point['block_values'], key=lambda row: row['block_id'])
    if len(rows) != 10 or [row['block_id'] for row in rows] != list(range(1, 11)):
        raise ValueError('trigger comparison parent lacks K10 block identity')
    result = []
    for row in rows:
        if row['tune_id'] != tune or any(float.fromhex(row[name]) != row['events']
                for name in ('sumw', 'sumw2', 'sumabsw')):
            raise ValueError('trigger comparison needs unit-weight parent events')
        values = {item['id']: float.fromhex(item['value'])
                  for item in row['additive_components']}
        if set(values) != {'pair_os', 'pair_ss', 'trigger'} or len(
                row['additive_components']) != 3 or any(
                not math.isfinite(v) or v < 0 or v != int(v) or v >= 2**53
                for v in values.values()):
            raise ValueError('trigger comparison parent components differ')
        result.append([values['pair_os']-values['pair_ss'], values['trigger']])
    return result, rows


def derive(payload, recipe, root_sha, value_sha):
    """Use an already verified numerical payload; never read query rows."""
    checked_recipe(recipe)
    if payload['schema'] != 'hadronization_projection_result_v4':
        raise ValueError('trigger comparison requires numerical v4 primitives')
    request = payload['request_echo']
    classes = [c for c in request['classes'] if c['id'] == recipe['class_id']]
    if len(classes) != 1 or classes[0]['kind'] != 'INTEGRATED':
        raise ValueError('trigger comparison class is not integrated')
    sources = request['sources']['members']
    tunes = request['scope']['ordered_tunes']
    families = {t: p.digest([s for s in sources if s['tune_id'] == t]) for t in tunes}
    parents = {}
    for point in payload['points']:
        c = point['key']['curve']
        if (c['role_id'].startswith('balancing.integrated.') and
                c['quantity'] == 'os_minus_ss_per_trigger' and
                c['reference_tune_id'] is None and c['class_id'] == recipe['class_id'] and
                c['profile_id'] == recipe['profile_id'] and not point['key']['bins']):
            key = (c['role_id'], c['tune_id'], c['trigger_pdg'], c['associate_pdg'])
            if key in parents:
                raise ValueError('trigger comparison parent is ambiguous')
            parents[key] = point
    labels = {}
    for record in payload['resolved']['category_order']:
        for pdg, label in zip(record['associate_pdgs'], record['labels']):
            if str(pdg) in labels and labels[str(pdg)] != label:
                raise ValueError('trigger comparison particle label differs')
            labels[str(pdg)] = label
    points = []
    for sector in recipe['sectors']:
        role = 'balancing.integrated.' + sector['id']
        for slot, (na, da) in enumerate(sector['associate_pairs'], 1):
            for tune in tunes:
                nk = (role, tune, sector['numerator_trigger'], na)
                dk = (role, tune, sector['denominator_trigger'], da)
                if nk not in parents or dk not in parents:
                    raise ValueError('trigger comparison parent is not materialized')
                numerator, denominator = parents[nk], parents[dk]
                nb, nr = _parent_blocks(numerator, tune)
                db, dr = _parent_blocks(denominator, tune)
                if any((a['events'], a['event_moments_sha256']) !=
                       (b['events'], b['event_moments_sha256']) for a, b in zip(nr, dr)):
                    raise ValueError('trigger comparison parent block populations differ')
                blocks = [d+n for d, n in zip(db, nb)]
                result = estimate(blocks)
                identity = dict(sector=sector['id'], tune=tune, slot=slot,
                    numerator_trigger=sector['numerator_trigger'],
                    denominator_trigger=sector['denominator_trigger'],
                    numerator_associate=na, denominator_associate=da,
                    numerator_id=numerator['semantic_id'], denominator_id=denominator['semantic_id'])
                points.append(dict(index=len(points), semantic_id=p.digest(identity),
                    source_family_sha256=families[tune], **identity, **result,
                    input_blocks=[[x.hex() for x in row] for row in blocks]))
    covariance = []
    for a in points:
        row = []
        for b in points:
            if any(q['uncertainty_status'] not in AVAILABLE for q in (a, b)):
                value = None
            elif a['tune'] != b['tune']:
                value = 0.
            else:
                am, bm = (float.fromhex(q['leave_mean']) for q in (a, b))
                value = .9*math.fsum((float.fromhex(x)-am)*(float.fromhex(y)-bm)
                                     for x, y in zip(a['leaves'], b['leaves']))
            row.append(None if value is None else value.hex())
        covariance.append(row)
    return dict(schema=SCHEMA, parent_root_sha256=root_sha,
        parent_value_sha256=value_sha, parent_request_sha256=payload['request_sha256'],
        recipe=recipe, recipe_sha256=p.digest(recipe), tunes=tunes,
        estimator=p.ESTIMATOR, K=10, units='dimensionless',
        statistics_header_sha256=p.file_digest(ROOT_DIR/'pipeline/reduce/statistics.hpp'),
        campaign_state=payload['campaign_state'], species_labels=labels,
        points=points, covariance=covariance)


def _rows(value):
    rows, leaves = [], []
    for q in value['points']:
        row = {k: q[k] for k in FIELDS if k in q}
        row['reasons'] = ';'.join(q['reasons'])
        for name in ('center', 'error', 'variance'):
            row[name+'_present'] = q[name] is not None
            row[name] = 0. if q[name] is None else float.fromhex(q[name])
        rows.append(row)
        for block, leaf in enumerate(q['leaves'], 1):
            mean = q['leave_mean']
            usable = q['uncertainty_status'] in AVAILABLE and leaf is not None
            leaves.append(dict(point=q['index'], block=block, present=leaf is not None,
                usable=usable, leaf=0. if leaf is None else float.fromhex(leaf),
                mean_present=mean is not None, mean=0. if mean is None else float.fromhex(mean),
                factor=(math.sqrt(.9)*(float.fromhex(leaf)-float.fromhex(mean))
                        if usable else 0.)))
    return rows, leaves


def write(value, output):
    """Publish a typed ROOT file without replacing an existing path."""
    output = Path(output).absolute()
    p._reducer().reject_symlink_components(output, 'trigger comparison output')
    if output.exists():
        raise FileExistsError(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    import ROOT
    descriptor, name = tempfile.mkstemp(prefix='.trigger-comparison-', suffix='.root', dir=output.parent)
    os.close(descriptor)
    temporary = Path(name)
    try:
        root = ROOT.TFile.Open(str(temporary), 'RECREATE')
        if not root or root.IsZombie():
            raise ValueError('trigger comparison ROOT creation failed')
        ROOT.TObjString(p.canonical(value)).Write('payload')
        ROOT.TObjString(p.digest(value)).Write('value_sha256')
        for tree_name, fields, rows in zip(('points', 'deletions'),
                                           (FIELDS, LEAF_FIELDS), _rows(value)):
            tree, holders = archive_v4._tree(ROOT, tree_name, fields)
            for row in rows:
                archive_v4._fill(tree, holders, row)
            tree.Write()
        n = len(value['points'])
        covariance = ROOT.TH2D('covariance', 'Joint covariance;Point;Point', n, 0, n, n, 0, n)
        valid = ROOT.TH2I('covariance_valid', 'Covariance validity;Point;Point', n, 0, n, n, 0, n)
        for i, row in enumerate(value['covariance'], 1):
            for j, token in enumerate(row, 1):
                covariance.SetBinContent(i, j, 0. if token is None else float.fromhex(token))
                valid.SetBinContent(i, j, int(token is not None))
        covariance.Write(); valid.Write(); root.Close()
        read(temporary, p.file_digest(temporary))
        with temporary.open('rb') as stream:
            os.fsync(stream.fileno())
        os.link(temporary, output)
    finally:
        temporary.unlink(missing_ok=True)
    return p.file_digest(output)


def read(path, expected_sha):
    path = Path(path).absolute()
    p._reducer().reject_symlink_components(path, 'trigger comparison ROOT')
    p._reducer().regular_file(path, 'trigger comparison ROOT')
    p.validate(expected_sha, 'Digest', 'trigger comparison SHA-256')
    if p.file_digest(path) != expected_sha:
        raise ValueError('trigger comparison physical SHA-256 differs')
    import ROOT
    root = ROOT.TFile.Open(str(path))
    if not root or root.IsZombie():
        raise ValueError('trigger comparison ROOT open failed')
    try:
        keys = list(root.GetListOfKeys())
        if any(k.GetCycle() != 1 for k in keys) or {k.GetName() for k in keys} != {
                'payload', 'value_sha256', 'points', 'deletions', 'covariance', 'covariance_valid'}:
            raise ValueError('trigger comparison ROOT object set differs')
        value = json.loads(str(root.Get('payload').GetString()))
        if value.get('schema') != SCHEMA or p.digest(value) != str(root.Get('value_sha256').GetString()):
            raise ValueError('trigger comparison value identity differs')
        checked_recipe(value['recipe'])
        for name, fields, rows in zip(('points', 'deletions'), (FIELDS, LEAF_FIELDS), _rows(value)):
            tree = root.Get(name)
            if tree.GetEntries() != len(rows) or {b.GetName() for b in tree.GetListOfBranches()} != set(fields):
                raise ValueError('trigger comparison typed row domain differs')
            for actual, expected in zip(tree, rows):
                for field, kind in fields.items():
                    observed = getattr(actual, field)
                    observed = str(observed) if kind == 's' else float(observed) if kind == 'd' else int(observed)
                    if observed != expected[field]:
                        raise ValueError('trigger comparison typed value differs: '+field)
        n = len(value['points'])
        if any(root.Get(name).GetNbinsX() != n or root.Get(name).GetNbinsY() != n
               for name in ('covariance', 'covariance_valid')):
            raise ValueError('trigger comparison covariance domain differs')
        for i, row in enumerate(value['covariance'], 1):
            for j, token in enumerate(row, 1):
                if (root.Get('covariance_valid').GetBinContent(i, j) != int(token is not None) or
                        root.Get('covariance').GetBinContent(i, j) !=
                        (0. if token is None else float.fromhex(token))):
                    raise ValueError('trigger comparison covariance content differs')
        return value
    finally:
        root.Close()


def verify(value, parent, root_sha, value_sha):
    expected = derive(parent, value['recipe'], root_sha, value_sha)
    # Native calculations can differ by a final rounding bit across supported hosts.
    def equal(a, b):
        if isinstance(a, dict):
            return isinstance(b, dict) and set(a) == set(b) and all(equal(v, b[k]) for k, v in a.items())
        if isinstance(a, list):
            return isinstance(b, list) and len(a) == len(b) and all(equal(x, y) for x, y in zip(a, b))
        if isinstance(a, str) and isinstance(b, str) and ('0x' in a[:3]):
            return math.isclose(float.fromhex(a), float.fromhex(b), rel_tol=5e-11, abs_tol=2e-15)
        return a == b
    if not equal(value, expected):
        raise ValueError('trigger comparison differs from joint native parent reconstruction')
    return value
