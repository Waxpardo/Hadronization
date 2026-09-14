"""The public native builder must use and identify the configured compiler."""
import os
from pathlib import Path
import shlex
import shutil
import tempfile
import unittest
from unittest.mock import patch

from pipeline.reduce import native_runner


class NativeCompiler(unittest.TestCase):
    def test_configured_compiler_and_path_fallback_share_the_actual_build(self):
        compiler = shutil.which('c++')
        if compiler is None:
            self.skipTest('C++ compiler is unavailable')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            wrapper = root / 'c++'
            calls = root / 'compile-calls'
            wrapper.write_text('#!/bin/sh\n'
                'if [ "$1" != "--version" ]; then\n'
                '  echo compile >> ' + shlex.quote(str(calls)) + '\nfi\n'
                'exec ' + shlex.quote(compiler) + ' "$@"\n')
            wrapper.chmod(0o755)
            with patch.dict(os.environ, CXX=str(wrapper)):
                binary, build = native_runner.compile_engine(root / 'build')
            self.assertTrue(binary.is_file())
            self.assertEqual(build['compiler_id'], str(wrapper))
            self.assertTrue(build['compiler_version'])
            environment = dict(os.environ, PATH=str(root)+os.pathsep+os.environ['PATH'])
            environment.pop('CXX', None)
            with patch.dict(os.environ, environment, clear=True):
                cached, cached_build = native_runner.compile_engine(root / 'build')
            self.assertEqual((cached, cached_build), (binary, build))
            self.assertEqual(calls.read_text().splitlines(), ['compile'])
            with patch.dict(os.environ, CXX=str(root / 'absent-compiler')):
                with self.assertRaisesRegex(ValueError, 'configured C\\+\\+ compiler'):
                    native_runner.compile_engine(root / 'build')


if __name__ == '__main__':
    unittest.main()
