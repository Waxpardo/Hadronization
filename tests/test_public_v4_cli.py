"""Public native-v4 facade from a cwd outside the source checkout."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from helpers import ROOT


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class PublicV4CLI(unittest.TestCase):
    def setUp(self):
        base = os.environ.get('PHASEA_TEST_COLLECTION_DIR')
        if not base or Path(base).name != 'v22-d0-fixture':
            self.skipTest('authenticated external A v2.2 fixture was not supplied')
        self.base = Path(base)
        self.scratch = tempfile.TemporaryDirectory(dir=self.base.parent)
        self.addCleanup(self.scratch.cleanup)
        self.work = Path(self.scratch.name)
        self.output = self.work / 'result'
        self.request = self.base / 'native-merged-final/native-request.json'
        self.common = ['--collection-index', str(self.base / 'merged/index.json'),
            '--collection-index-sha',
                '379a19c32af3e5764c58ce9b5891e7ff49d8df5fdb9107cd5e6547f1f0f165c1',
            '--expected-sources', str(self.base / 'expected-sources.json'),
            '--expected-sources-sha',
                '29bc0d6645baa8701a4f22a52f181484f17416a1a2496fdbbbb881d9956e1b54',
            '--analysis-sha',
                'e959e00f8f8c7ced7aa6ec07dbe0e2b19b5bc30aab6ec4defb1df31319085ff8',
            '--request', str(self.request), '--request-sha', sha(self.request),
            '--work-root', str(self.work), '--output-dir', str(self.output)]

    def command(self, *args):
        environment = os.environ.copy()
        environment.pop('PYTHONPATH', None)
        return subprocess.run([str(ROOT / 'hadronization'), 'reduce', *args],
            cwd=str(self.work), env=environment, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def test_current_v22_merged_public_roundtrip(self):
        result = self.command('run', *self.common)
        self.assertEqual(result.returncode, 0, result.stderr)
        summary = json.loads(result.stdout)
        self.assertEqual(summary['points'], 114)
        self.assertEqual(summary['science_content_sha256'],
            '3072dd16371e4e24a116596d79f956210c0cef71d791642216ef471f46b10bb0')
        report = self.output / 'report.json'
        verified = self.command('verify', '--root', str(self.output /
            'numerics.root'), '--report', str(report), '--report-sha', sha(report))
        self.assertEqual(verified.returncode, 0, verified.stderr)
        self.assertEqual(json.loads(verified.stdout)['points'], 114)
        explained = self.command('explain', '--root', str(self.output /
            'numerics.root'), '--report', str(report), '--report-sha', sha(report))
        self.assertEqual(explained.returncode, 0, explained.stderr)
        self.assertEqual(json.loads(explained.stdout)['source_state'], 'TEST_ONLY')

    def test_default_request_selection_covers_every_paper_role_and_g9_t1(self):
        from types import SimpleNamespace
        from pipeline.query import collection
        from pipeline.reduce import native, projection as p, public_v4
        source = native.NativeCollection(self.base / 'merged/index.json',
            self.common[self.common.index('--collection-index-sha')+1],
            collection)
        analysis = json.loads((ROOT / 'config/analysis.json').read_text())
        tunes = list(source.index['tune_ordinals'])
        t1, _, _ = native.collect_t1(source, tunes)
        selection = public_v4._selection(SimpleNamespace(charm_trigger=421,
            profile_id='inclusive', activity_id=None,
            reference_tune='MONASH'), analysis)
        request = p.make_native_request(source, ROOT / 'config/analysis.json',
            p.file_digest(ROOT / 'config/analysis.json'), tunes,
            sorted({key[2] for key in t1}), selection)
        keys = request.expected_point_keys
        roles = {key['curve']['role_id'] for key in keys}
        self.assertEqual(roles, set(p.PAPER_ROLE_IDS))
        self.assertGreater(len(keys), 114)
        self.assertEqual({key['curve']['axis_id'] for key in keys if
            key['curve']['role_id']=='spectra.signed_heavy'},
            {'pt','eta','phi'})
        self.assertTrue(any(key['curve']['role_id']==
            'accounting.natural_final_heavy' for key in keys))
        self.assertEqual(selection['trigger_pdgs'][0], 421)
        self.assertEqual(public_v4._selection(SimpleNamespace(
            charm_trigger=411, profile_id='inclusive', activity_id=None,
            reference_tune='MONASH'), analysis)['trigger_pdgs'][0], 411)
        bounded = public_v4._representative_request(source, SimpleNamespace(
            charm_trigger=421, profile_id='inclusive', activity_id=None,
            reference_tune='MONASH', tunes=None,
            analysis_sha=p.file_digest(ROOT / 'config/analysis.json')),
            analysis)
        self.assertEqual({key['curve']['role_id'] for key in
            bounded.expected_point_keys}, set(p.PAPER_ROLE_IDS))
        self.assertTrue(114 < len(bounded.expected_point_keys) < 1000)

    def test_wrong_index_or_analysis_sha_fails_before_output(self):
        for key in ('--collection-index-sha', '--analysis-sha'):
            with self.subTest(key=key):
                args = self.common.copy()
                args[args.index(key)+1] = '0'*64
                result = self.command('run', *args)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(self.output.exists())

    def test_missing_pair_proof_fails_at_public_admission(self):
        index = json.loads((self.base / 'merged/index.json').read_text())
        metadata = json.loads(Path(index['shards'][0]['metadata']['path']).read_text())
        self.assertIn('pair_population_proof', metadata)
        metadata.pop('pair_population_proof')
        metadata_path = self.work / 'proof-free-metadata.json'
        metadata_path.write_text(json.dumps(metadata))
        index['shards'][0]['metadata'] = dict(path=str(metadata_path),
            bytes=metadata_path.stat().st_size, sha256=sha(metadata_path))
        index_path = self.work / 'proof-free-index.json'
        index_path.write_text(json.dumps(index))
        args = self.common.copy()
        args[args.index('--collection-index')+1] = str(index_path)
        args[args.index('--collection-index-sha')+1] = sha(index_path)
        result = self.command('run', *args)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('mandatory pair-population proof', result.stderr)
        self.assertFalse(self.output.exists())

    def test_omitted_request_pin_and_false_full_fail_before_numerics(self):
        args = self.common.copy()
        args.remove('--request-sha')
        args.remove(sha(self.request))
        result = self.command('run', *args)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('request requires --request-sha', result.stderr)
        request = json.loads(self.request.read_text())
        request['completion']['require_campaign_complete'] = True
        forged = self.work / 'false-full-request.json'
        forged.write_text(json.dumps(request))
        args = self.common.copy()
        args[args.index('--request')+1] = str(forged)
        args[args.index('--request-sha')+1] = sha(forged)
        result = self.command('run', *args)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('request completion differs', result.stderr)
        self.assertFalse(self.output.exists())

    def test_existing_output_is_immutable(self):
        self.output.mkdir()
        (self.output / 'sentinel').write_text('untouched')
        result = self.command('run', *self.common)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((self.output / 'sentinel').read_text(), 'untouched')
        self.assertFalse((self.output / 'numerics.root').exists())

    def test_legacy_v1_plan_has_explicit_command(self):
        result = self.command('run', '--plan', 'old.json')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('--collection-index', result.stderr)
        result = self.command('legacy-run', '--help')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('--plan', result.stdout)


if __name__ == '__main__':
    unittest.main()
