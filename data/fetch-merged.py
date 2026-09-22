#!/usr/bin/env python3
"""Download byte parts and restore the checksum-bound merged ROOT files."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
from urllib.request import urlopen


MANIFEST = Path(__file__).with_name('merged-download.json')


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def matches(path, fact):
    return (path.is_file() and not path.is_symlink() and
            path.stat().st_size == fact['bytes'] and digest(path) == fact['sha256'])


def check_fact(fact):
    if (not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*', fact['name']) or
            type(fact['bytes']) is not int or fact['bytes'] <= 0 or
            not re.fullmatch(r'[a-f0-9]{64}', fact['sha256'])):
        raise ValueError('invalid file identity in download manifest')


def manifest_read(path):
    data = json.loads(path.read_text())
    if data['schema'] != 'hadronization_merged_download_v1':
        raise ValueError('unsupported download manifest')
    names = set()
    for item in data['files']:
        check_fact(item)
        if item['name'] in names or not item['parts']:
            raise ValueError('duplicate file or empty parts')
        names.add(item['name'])
        for part in item['parts']:
            check_fact(part)
            if part['name'] in names or not part['url'].startswith(
                    'https://github.com/Waxpardo/Hadronization/releases/download/'):
                raise ValueError('duplicate part or unexpected download location')
            names.add(part['name'])
        if sum(p['bytes'] for p in item['parts']) != item['bytes']:
            raise ValueError('part sizes differ from complete file size')
    return data


def publish(streams, target, fact):
    """Close and check scratch bytes before a local no-replace publication."""
    fd, name = tempfile.mkstemp(prefix='.' + target.name + '.', dir=target.parent)
    stage = Path(name)
    try:
        with os.fdopen(fd, 'wb') as out:
            for stream in streams:
                with stream:
                    shutil.copyfileobj(stream, out, 8 * 1024 * 1024)
            out.flush()
            os.fsync(out.fileno())
        if not matches(stage, fact):
            raise ValueError('size or SHA-256 differs: ' + target.name)
        os.link(stage, target)
    finally:
        stage.unlink(missing_ok=True)


def fetch(data, output, local_parts=None, verify_only=False):
    if any(p.is_symlink() for p in (output, *output.parents)):
        raise ValueError('output path contains a symbolic link')
    if not verify_only:
        output.mkdir(parents=True, exist_ok=True)
    for item in data['files']:
        target = output / item['name']
        if target.exists() or target.is_symlink():
            if not matches(target, item):
                raise ValueError('existing ROOT file differs; preserve it: ' + str(target))
            print('VERIFIED ' + item['name'], flush=True)
            continue
        if verify_only:
            raise ValueError('missing ROOT file: ' + str(target))
        cache = output / '.parts'
        if cache.is_symlink():
            raise ValueError('part cache is a symbolic link')
        cache.mkdir(exist_ok=True)
        parts = []
        for part in item['parts']:
            path = (local_parts if local_parts is not None else cache) / part['name']
            if path.exists() or path.is_symlink():
                if not matches(path, part):
                    raise ValueError('existing download part differs: ' + str(path))
            elif local_parts is not None:
                raise ValueError('missing local part: ' + str(path))
            else:
                print('DOWNLOAD ' + part['name'], flush=True)
                publish([urlopen(part['url'], timeout=120)], path, part)
            parts.append(path)
        publish((path.open('rb') for path in parts), target, item)
        print('VERIFIED ' + item['name'], flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('data/work/merged'),
                        help='local destination; default: data/work/merged')
    parser.add_argument('--local-parts', type=Path,
                        help='read already downloaded parts instead of using the network')
    parser.add_argument('--verify-only', action='store_true',
                        help='check restored ROOT files without downloading or writing')
    args = parser.parse_args()
    try:
        fetch(manifest_read(MANIFEST), args.output.absolute(),
              args.local_parts, args.verify_only)
    except (OSError, ValueError, KeyError) as error:
        parser.exit(2, 'ERROR: ' + str(error) + '\n')


if __name__ == '__main__':
    main()
