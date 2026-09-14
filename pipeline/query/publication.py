"""Dependency-light no-replace directory publisher shared by query and site probe."""

import ctypes
from contextlib import ExitStack
import errno
import hashlib
import os
from pathlib import Path
import stat
import sys


class PublicationError(ValueError):
    """Deterministic HOLD: inspect retained paths, never automatically retry."""


def _native_noreplace(staging, output):
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
    elif sys.platform.startswith("linux"):
        raise OSError(errno.ENOSYS, "renameat2 is unavailable", str(output))
    else:
        raise ValueError("atomic no-overwrite directory publication is unavailable on this platform")
    rename.restype = ctypes.c_int
    if rename(*arguments) != 0:
        error = ctypes.get_errno()
        raise OSError(error, os.strerror(error), str(output))


def _open_directory(path):
    """Walk from / using directory descriptors; never follow a symlink."""
    descriptor = os.open("/", os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in path.parts[1:]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                            dir_fd=descriptor)
            os.close(descriptor)
            descriptor = child
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def _mount_id(descriptor):
    # st_dev alone misses bind mounts of the same filesystem. On Linux require
    # the kernel's descriptor mount ID, including inside a container namespace.
    if not sys.platform.startswith("linux"):
        return None  # Allows the reservation mechanics to be tested on macOS.
    for line in Path("/proc/self/fdinfo/" + str(descriptor)).read_text().splitlines():
        if line.startswith("mnt_id:"):
            return int(line.split()[1])
    raise PublicationError("cannot attest publication mount ID")


def _identity(info):
    return info.st_dev, info.st_ino, info.st_mode, info.st_uid, info.st_gid


def _snapshot(descriptor, device, mount, relative=""):
    """Fsync and pin the complete private tree, including nested workspaces."""
    info = os.fstat(descriptor)
    if info.st_dev != device or _mount_id(descriptor) != mount:
        raise PublicationError("publication stage crosses a filesystem or mount")
    if info.st_uid != os.geteuid():
        raise PublicationError("publication stage contains a foreign owner")
    if stat.S_ISREG(info.st_mode):
        if info.st_nlink != 1:
            raise PublicationError("publication stage contains a hard link")
        digest = hashlib.sha256()
        while True:
            block = os.read(descriptor, 1024 * 1024)
            if not block:
                break
            digest.update(block)
        os.fsync(descriptor)
        after = os.fstat(descriptor)
        if (_identity(info), info.st_size, info.st_mtime_ns) != (
                _identity(after), after.st_size, after.st_mtime_ns):
            raise PublicationError("publication file changed during readback")
        return {relative: (_identity(info), info.st_size, info.st_mtime_ns,
                           digest.hexdigest())}
    if not stat.S_ISDIR(info.st_mode):
        raise PublicationError("publication stage contains a special file")
    result = {relative: _identity(info)}
    for name in sorted(os.listdir(descriptor)):
        entry = os.stat(name, dir_fd=descriptor, follow_symlinks=False)
        if not (stat.S_ISDIR(entry.st_mode) or stat.S_ISREG(entry.st_mode)):
            raise PublicationError("publication stage contains a symlink or special file")
        flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
        if stat.S_ISDIR(entry.st_mode):
            flags |= os.O_DIRECTORY
        child = os.open(name, flags, dir_fd=descriptor)
        try:
            if _identity(os.fstat(child)) != _identity(entry):
                raise PublicationError("publication stage entry changed")
            result.update(_snapshot(child, device, mount, relative + "/" + name))
        finally:
            os.close(child)
    os.fsync(descriptor)
    return result


def _reserved_publish(staging, output):
    """NFS adapter for cooperating publishers under trusted owned parents.

    Exclusive mkdir wins the name. Its empty mode-000 directory is NEVER an
    accepted artifact: readers must require their manifest and content pins.
    Ordinary rename may replace only this call's pinned reservation. The owner
    must not concurrently chmod/replace it; malicious same-UID/root processes
    are outside this trust boundary. No failure path removes a reservation or
    stage, and an ambiguous NFS rename is resolved by inode AND full readback.
    """
    if any(".." in Path(path).parts for path in (staging, output)):
        raise PublicationError("publication paths must not contain '..'")
    staging, output = Path(staging).absolute(), Path(output).absolute()
    if staging == output or staging in output.parents or output in staging.parents:
        raise PublicationError("publication paths overlap")
    with ExitStack() as stack:
        def opened(path):
            descriptor = _open_directory(path)
            stack.callback(os.close, descriptor)
            return descriptor

        source_parent, target_parent = opened(staging.parent), opened(output.parent)
        parents = [os.fstat(fd) for fd in (source_parent, target_parent)]
        if any(info.st_uid != os.geteuid() or info.st_mode & 0o022 for info in parents):
            raise PublicationError("publication parents must be owned and not group/other writable")
        device, mount = parents[0].st_dev, _mount_id(source_parent)
        if parents[1].st_dev != device or _mount_id(target_parent) != mount:
            raise PublicationError("publication destination is on a different filesystem or mount")
        source = opened(staging)
        source_info = os.fstat(source)
        if (source_info.st_uid != os.geteuid() or
                stat.S_IMODE(source_info.st_mode) & 0o777 != 0o700):
            raise PublicationError("publication stage must be an owned private directory")
        before = _snapshot(source, device, mount)
        # All validation precedes exclusive reservation. EEXIST is an ordinary
        # collision, including an inaccessible, empty or interrupted reservation.
        try:
            os.mkdir(output.name, 0o000, dir_fd=target_parent)
        except FileExistsError:
            raise
        except OSError as error:
            raise PublicationError("exclusive reservation outcome unresolved; paths retained") from error
        try:
            reserved = os.stat(output.name, dir_fd=target_parent, follow_symlinks=False)
            if (not stat.S_ISDIR(reserved.st_mode) or reserved.st_dev != device or
                    reserved.st_uid != os.geteuid() or reserved.st_mode & 0o777):
                raise PublicationError("publication reservation identity/mode differs")
            os.fsync(target_parent)
            if (_identity(os.stat(output.name, dir_fd=target_parent, follow_symlinks=False)) !=
                    _identity(reserved) or
                    _identity(os.stat(staging.name, dir_fd=source_parent, follow_symlinks=False)) !=
                    _identity(source_info)):
                raise PublicationError("publication stage or reservation changed")
            rename_error = None
            try:
                os.rename(staging.name, output.name,
                          src_dir_fd=source_parent, dst_dir_fd=target_parent)
            except OSError as error:
                rename_error = error
            # An NFS server can complete rename and then return an error. Never
            # repeat rename or delete either path to guess at the outcome.
            published = os.stat(output.name, dir_fd=target_parent, follow_symlinks=False)
            try:
                os.stat(staging.name, dir_fd=source_parent, follow_symlinks=False)
            except FileNotFoundError:
                source_absent = True
            else:
                source_absent = False
            if _identity(published) != _identity(source_info) or not source_absent:
                raise PublicationError("publication rename unresolved; stage/reservation retained") from rename_error
            reopened = opened(output)
            if _snapshot(reopened, device, mount) != before:
                raise PublicationError("published directory content readback differs")
            for path, info in zip((staging.parent, output.parent), parents):
                if _identity(os.fstat(opened(path))) != _identity(info):
                    raise PublicationError("publication parent path changed")
            os.fsync(source_parent)
            os.fsync(target_parent)
            return {"method": "linux_exclusive_directory_reservation",
                    "device": device, "mount_id": mount,
                    "stage_inode": source_info.st_ino, "reservation_inode": reserved.st_ino,
                    "published_inode": published.st_ino,
                    "resolved_rename_errno": rename_error.errno if rename_error else None}
        except OSError as error:
            raise PublicationError("publication requires review; retained paths: " +
                                   str(staging) + ", " + str(output) + ": " + str(error)) from error


def publish_directory(staging, output):
    """Install a complete directory without replacing an existing destination.

    Native atomic no-replace behavior is unchanged. Only Linux unsupported-flag
    errors enter the guarded reservation adapter; unrelated I/O/access errors
    propagate. Callers must retain private stages once publication is attempted.
    """
    try:
        return _native_noreplace(staging, output)
    except OSError as error:
        if (not sys.platform.startswith("linux") or
                error.errno not in (errno.EINVAL, errno.EOPNOTSUPP, errno.ENOSYS)):
            raise
        return _reserved_publish(staging, output)
