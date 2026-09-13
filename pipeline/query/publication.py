"""Dependency-light no-replace directory publisher shared by query and site probe."""

import ctypes
import os
import sys


def publish_directory(staging, output):
    """Atomically install a complete directory, refusing even an empty destination."""
    libc = ctypes.CDLL(None, use_errno=True)
    source, destination = os.fsencode(staging), os.fsencode(output)
    if sys.platform == "darwin":
        rename = libc.renamex_np
        rename.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint]
        arguments = [source, destination, 0x00000004]  # Darwin RENAME_EXCL.
    elif sys.platform.startswith("linux") and hasattr(libc, "renameat2"):
        rename = libc.renameat2
        rename.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int,
                           ctypes.c_char_p, ctypes.c_uint]
        arguments = [-100, source, -100, destination, 1]  # AT_FDCWD, RENAME_NOREPLACE.
    else:
        raise ValueError("atomic no-overwrite directory publication is unavailable on this platform")
    rename.restype = ctypes.c_int
    if rename(*arguments) != 0:
        error = ctypes.get_errno()
        raise OSError(error, os.strerror(error), str(output))
