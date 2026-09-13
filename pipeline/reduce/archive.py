"""Compatibility import boundary for the sole v4 typed numerical ROOT contract.

The renderer and active numerical tests call this module's stable signatures;
all serialization and verification are delegated to archive_v4.
"""
from . import archive_v4


def write(value, output, work=None):
    return archive_v4.write(value, output)


def read(source, work, expected_root_sha256, expected_value_sha256):
    return archive_v4.read(source, expected_root_sha256, expected_value_sha256)
