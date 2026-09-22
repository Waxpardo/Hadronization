"""Check byte restoration and refusal without external scientific files."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

from helpers import ROOT

spec = importlib.util.spec_from_file_location('fetch_merged', ROOT / 'data/fetch-merged.py')
download = importlib.util.module_from_spec(spec)
spec.loader.exec_module(download)


class MergedDownload(unittest.TestCase):
    def fixture(self, base):
        parts = base / 'parts'
        parts.mkdir()
        body = b'ROOT test bytes across two transfer parts'
        records = []
        for number, content in enumerate((body[:13], body[13:])):
            name = 'tune-00.root.part-%02d' % number
            (parts / name).write_bytes(content)
            records.append({'name':name, 'bytes':len(content),
                            'sha256':hashlib.sha256(content).hexdigest(),
                            'url':'https://github.com/Waxpardo/Hadronization/releases/download/test/'+name})
        data = {'schema':'hadronization_merged_download_v1', 'files':[
            {'name':'tune-00.root', 'bytes':len(body),
             'sha256':hashlib.sha256(body).hexdigest(), 'parts':records}]}
        manifest = base / 'manifest.json'
        manifest.write_text(json.dumps(data))
        return download.manifest_read(manifest), parts, body

    def test_restore_restart_and_read_only_verification(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            data, parts, body = self.fixture(base)
            output = base / 'output'
            download.fetch(data, output, parts)
            self.assertEqual((output / 'tune-00.root').read_bytes(), body)
            before = (output / 'tune-00.root').stat().st_mtime_ns
            download.fetch(data, output, parts)
            download.fetch(data, output, verify_only=True)
            self.assertEqual((output / 'tune-00.root').stat().st_mtime_ns, before)

    def test_corrupt_part_and_existing_output_are_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            data, parts, body = self.fixture(base)
            part = parts / data['files'][0]['parts'][0]['name']
            part.write_bytes(b'bad')
            output = base / 'output'
            with self.assertRaisesRegex(ValueError, 'download part differs'):
                download.fetch(data, output, parts)
            self.assertFalse((output / 'tune-00.root').exists())
            (output / 'tune-00.root').write_bytes(b'preserve')
            with self.assertRaisesRegex(ValueError, 'existing ROOT file differs'):
                download.fetch(data, output, parts)
            self.assertEqual((output / 'tune-00.root').read_bytes(), b'preserve')

    def test_missing_verify_and_symlink_refusal(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            data, parts, body = self.fixture(base)
            output = base / 'absent'
            with self.assertRaisesRegex(ValueError, 'missing ROOT file'):
                download.fetch(data, output, verify_only=True)
            self.assertFalse(output.exists())
            output.symlink_to(parts, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, 'symbolic link'):
                download.fetch(data, output)

    def test_failed_download_bytes_never_publish(self):
        import io
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            data, parts, body = self.fixture(base)
            target = base / 'download'
            with self.assertRaisesRegex(ValueError, 'SHA-256 differs'):
                download.publish([io.BytesIO(b'truncated')], target, data['files'][0])
            self.assertFalse(target.exists())
            self.assertFalse(list(base.glob('.download.*')))


if __name__ == '__main__':
    unittest.main()
