"""Real filesystem tests of the guarded NFS publication protocol."""

from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager, ExitStack
import errno
import importlib.util
import os
from pathlib import Path
import stat
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

from pipeline.query import publication


@contextmanager
def fallback(module=publication, error=errno.EINVAL):
    """Only inject unsupported flags; exercise real mkdir/rename/fsync/readback."""
    linux = sys.platform.startswith("linux")
    with ExitStack() as stack:
        stack.enter_context(mock.patch.object(module, "sys", SimpleNamespace(platform="linux")))
        stack.enter_context(mock.patch.object(module, "_native_noreplace",
                                             side_effect=OSError(error, "unsupported flag")))
        if not linux:
            stack.enter_context(mock.patch.object(module, "_mount_id", return_value=None))
        yield


class ReservedDirectoryPublication(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name).resolve()

    def tearDown(self):
        # Test-only reservations must be traversable for TemporaryDirectory.
        for path in self.base.rglob("*"):
            if not path.is_symlink() and path.is_dir():
                path.chmod(0o700)
        self.temporary.cleanup()

    def stage(self, name=".stage", nested=False):
        path = self.base / name
        path.mkdir(mode=0o700)
        if nested:
            (path / "workspace").mkdir()
            (path / "workspace/query.root").write_bytes(b"TEST_ONLY nested content")
        (path / "manifest.json").write_bytes(b"TEST_ONLY complete pinned bytes")
        return path

    def test_native_success_and_empty_collision_unchanged(self):
        stage, output = self.stage(), self.base / "output"
        with mock.patch.object(publication, "_reserved_publish", side_effect=AssertionError):
            self.assertIsNone(publication.publish_directory(stage, output))
            contender = self.stage(".other")
            empty = self.base / "empty"; empty.mkdir()
            with self.assertRaises(OSError) as raised:
                publication.publish_directory(contender, empty)
            self.assertIn(raised.exception.errno, (errno.EEXIST, errno.ENOTEMPTY))
        self.assertTrue((output / "manifest.json").is_file())
        self.assertTrue(contender.is_dir())

    @unittest.skipUnless(sys.platform.startswith("linux"), "requires Linux mode-000 rename semantics")
    def test_each_unsupported_flag_uses_real_nested_publication(self):
        for index, code in enumerate((errno.EINVAL, errno.EOPNOTSUPP, errno.ENOSYS)):
            stage = self.stage(".stage-" + str(index), nested=True)
            output = self.base / ("output-" + str(index))
            original = stage.stat().st_ino
            with fallback(error=code):
                proof = publication.publish_directory(stage, output)
            self.assertFalse(stage.exists())
            self.assertEqual(output.stat().st_ino, original)
            self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o700)
            self.assertEqual(proof["published_inode"], proof["stage_inode"])
            self.assertNotEqual(proof["published_inode"], proof["reservation_inode"])
            self.assertEqual((output / "workspace/query.root").read_bytes(), b"TEST_ONLY nested content")

    def test_empty_nonempty_and_reservation_collisions_are_never_replaced(self):
        for index, mode in enumerate((0o700, 0o700, 0o000)):
            output = self.base / ("output-" + str(index)); output.mkdir(mode=mode)
            if index == 1:
                (output / "sentinel").write_bytes(b"PREEXISTING")
            before = output.stat().st_ino
            stage = self.stage(".stage-" + str(index))
            with fallback(), self.assertRaises(FileExistsError):
                publication.publish_directory(stage, output)
            self.assertEqual(output.stat().st_ino, before)
            self.assertTrue((stage / "manifest.json").is_file())
            if index == 1:
                self.assertEqual((output / "sentinel").read_bytes(), b"PREEXISTING")

    @unittest.skipUnless(sys.platform.startswith("linux"), "requires Linux mode-000 rename semantics")
    def test_private_attempt_can_publish_to_a_different_owned_parent(self):
        stage = self.stage(nested=True)
        parent = self.base / "collection"; parent.mkdir(mode=0o700)
        output = parent / "query"
        with fallback():
            publication.publish_directory(stage, output)
        self.assertFalse(stage.exists())
        self.assertTrue((output / "workspace/query.root").is_file())

    @unittest.skipUnless(sys.platform.startswith("linux"), "requires Linux mode-000 rename semantics")
    def test_two_concurrent_contenders_have_exactly_one_winner(self):
        stages = [self.stage(".first"), self.stage(".second")]
        output = self.base / "output"
        def attempt(stage):
            try:
                publication.publish_directory(stage, output)
                return "won", stage
            except FileExistsError:
                return "lost", stage
        with fallback(), ThreadPoolExecutor(2) as pool:
            results = list(pool.map(attempt, stages))
        self.assertEqual(sorted(state for state, _ in results), ["lost", "won"])
        for state, stage in results:
            self.assertEqual(stage.exists(), state == "lost")
        self.assertTrue((output / "manifest.json").is_file())

    def test_interruption_after_reservation_preserves_complete_stage(self):
        stage, output = self.stage(nested=True), self.base / "output"
        real_sync = os.fsync
        def interrupted(fd):
            real_sync(fd)
            if os.path.lexists(output):
                raise KeyboardInterrupt("TEST_ONLY after reservation")
        with fallback(), mock.patch.object(publication.os, "fsync", side_effect=interrupted):
            with self.assertRaises(KeyboardInterrupt):
                publication.publish_directory(stage, output)
        self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0)
        self.assertTrue((stage / "workspace/query.root").is_file())
        output.chmod(0o700)  # Even bypassing permissions, no complete manifest exists.
        self.assertEqual(list(output.iterdir()), [])

    def test_rename_error_before_effect_is_hold_without_retry(self):
        stage, output = self.stage(), self.base / "output"
        with fallback(), mock.patch.object(publication.os, "rename",
                side_effect=OSError(errno.EIO, "NFS reply lost")) as rename:
            with self.assertRaisesRegex(publication.PublicationError, "unresolved"):
                publication.publish_directory(stage, output)
        self.assertEqual(rename.call_count, 1)
        self.assertTrue((stage / "manifest.json").is_file())
        self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0)

    @unittest.skipUnless(sys.platform.startswith("linux"), "requires Linux mode-000 rename semantics")
    def test_completed_rename_with_error_requires_full_readback(self):
        stage, output = self.stage(nested=True), self.base / "output"
        real_rename = os.rename
        def completed(*args, **kwargs):
            real_rename(*args, **kwargs)
            raise OSError(errno.EIO, "NFS reply lost after success")
        with fallback(), mock.patch.object(publication.os, "rename", side_effect=completed) as rename:
            proof = publication.publish_directory(stage, output)
        self.assertEqual(rename.call_count, 1)
        self.assertEqual(proof["resolved_rename_errno"], errno.EIO)
        self.assertFalse(stage.exists())
        self.assertTrue((output / "workspace/query.root").is_file())

    @unittest.skipUnless(sys.platform.startswith("linux"), "requires Linux mode-000 rename semantics")
    def test_completed_rename_with_corrupt_readback_is_hold(self):
        stage, output = self.stage(), self.base / "output"
        real_rename = os.rename
        def corrupted(*args, **kwargs):
            real_rename(*args, **kwargs)
            (output / "manifest.json").write_bytes(b"corrupted")
            raise OSError(errno.EIO, "NFS reply lost")
        with fallback(), mock.patch.object(publication.os, "rename", side_effect=corrupted):
            with self.assertRaisesRegex(publication.PublicationError, "readback differs"):
                publication.publish_directory(stage, output)
        self.assertTrue(output.is_dir())
        self.assertFalse(stage.exists())

    def test_ambiguous_reservation_creation_is_hold(self):
        stage, output = self.stage(), self.base / "output"
        real_mkdir = os.mkdir
        def lost_reply(*args, **kwargs):
            real_mkdir(*args, **kwargs)
            raise OSError(errno.EIO, "mkdir reply lost")
        with fallback(), mock.patch.object(publication.os, "mkdir", side_effect=lost_reply):
            with self.assertRaisesRegex(publication.PublicationError, "reservation outcome unresolved"):
                publication.publish_directory(stage, output)
        self.assertTrue(stage.is_dir())
        self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0)

    @unittest.skipUnless(sys.platform.startswith("linux"), "requires Linux mode-000 rename semantics")
    def test_replaced_reservation_is_not_overwritten(self):
        stage, output = self.stage(), self.base / "output"
        foreign = self.base / "foreign"; foreign.mkdir(mode=0o700)
        foreign_inode = foreign.stat().st_ino
        real_sync = os.fsync
        def replaced(fd):
            real_sync(fd)
            if os.path.lexists(output) and foreign.exists():
                os.rename(foreign, output)
        with fallback(), mock.patch.object(publication.os, "fsync", side_effect=replaced):
            with self.assertRaisesRegex(publication.PublicationError, "reservation changed"):
                publication.publish_directory(stage, output)
        self.assertEqual(output.stat().st_ino, foreign_inode)
        self.assertTrue(stage.is_dir())

    def test_no_fallback_for_unrelated_native_errors_or_on_macos(self):
        for code in (errno.EACCES, errno.EIO, errno.EXDEV):
            with fallback(error=code), mock.patch.object(publication, "_reserved_publish") as reserve:
                with self.assertRaises(OSError) as raised:
                    publication.publish_directory("stage", "output")
                self.assertEqual(raised.exception.errno, code)
                reserve.assert_not_called()
        with mock.patch.object(publication, "sys", SimpleNamespace(platform="darwin")), \
                mock.patch.object(publication, "_native_noreplace", side_effect=OSError(errno.EINVAL, "bad")), \
                mock.patch.object(publication, "_reserved_publish") as reserve:
            with self.assertRaises(OSError):
                publication.publish_directory("stage", "output")
            reserve.assert_not_called()

    def test_unsafe_parent_stage_and_symlink_or_hardlink_content_refused(self):
        cases = ("shared_parent", "public_stage", "symlink_file", "symlink_stage",
                 "symlink_parent", "hardlink", "foreign_owner", "overlap")
        for index, case in enumerate(cases):
            with self.subTest(case=case):
                root = self.base / str(index); root.mkdir(mode=0o700)
                stage = root / ".stage"; stage.mkdir(mode=0o700)
                (stage / "data").write_bytes(b"owned")
                output = root / "output"
                uid = os.geteuid()
                if case == "shared_parent": root.chmod(0o770)
                if case == "public_stage": stage.chmod(0o755)
                if case == "symlink_file": (stage / "link").symlink_to(root)
                if case == "symlink_stage":
                    alias = root / "alias"; alias.symlink_to(stage); stage = alias
                if case == "symlink_parent":
                    alias = self.base / "alias"; alias.symlink_to(root); output = alias / "output"
                if case == "hardlink": os.link(stage / "data", stage / "other")
                if case == "overlap": output = stage / "inside"
                with fallback(), mock.patch.object(publication.os, "geteuid",
                        return_value=uid + 1 if case == "foreign_owner" else uid):
                    with self.assertRaises((OSError, ValueError)):
                        publication.publish_directory(stage, output)
                self.assertFalse(os.path.lexists(output))
                self.assertTrue((stage / "data").is_file())

    def test_foreign_mount_in_parent_or_nested_tree_refused(self):
        for nested in (False, True):
            root = self.base / str(nested); root.mkdir(mode=0o700)
            stage = root / ".stage"; stage.mkdir(mode=0o700)
            target = root / "dest-parent"; target.mkdir(mode=0o700)
            child = stage / "nested"; child.mkdir()
            foreign_inode = (child if nested else target).stat().st_ino
            def mount_id(fd):
                return 2 if os.fstat(fd).st_ino == foreign_inode else 1
            with fallback(), mock.patch.object(publication, "_mount_id", side_effect=mount_id):
                with self.assertRaisesRegex(publication.PublicationError, "mount"):
                    publication.publish_directory(stage, target / "output")
            self.assertFalse((target / "output").exists())

    @unittest.skipUnless(sys.platform.startswith("linux"), "requires Linux mode-000 rename semantics")
    def test_real_site_probe_uses_adapter_and_preserves_collision_stages(self):
        spec = importlib.util.spec_from_file_location("reserved_site_probe",
            Path(publication.__file__).with_name("site_probe.py"))
        probe = importlib.util.module_from_spec(spec); spec.loader.exec_module(probe)
        with fallback(probe.publication):
            result = probe.publish_probe(self.base, "TEST_ONLY")
        self.assertEqual(result["publication"]["method"], "linux_exclusive_directory_reservation")
        self.assertEqual(result["no_overwrite"], "PASS")
        self.assertEqual(probe.sha(Path(result["payload"])), result["sha256"])
        for collision in result["existing_destinations"].values():
            self.assertTrue(Path(collision["stage"]).is_dir())
        self.assertTrue(Path(result["interrupted_stage"]).is_dir())

    def test_manifest_readers_reject_inaccessible_and_empty_reservations(self):
        from pipeline.query import run, collection, condor, merge
        from pipeline import release
        output = self.base / "reservation"; output.mkdir(mode=0o000)
        checks = (
            lambda: run.load_prepared_pack(output),
            lambda: run.verify(output, self.base / "work", "a" * 64),
            lambda: collection.read(output / "index.json", "a" * 64),
            lambda: merge.merge(output / "index.json", "a" * 64, self.base / "merged"),
            lambda: condor._checked_site_bundle(output, "a" * 64),
            lambda: release.verify(output, "a" * 64, self.base / "work"),
        )
        for mode in (0o000, 0o700):
            output.chmod(mode)
            for check in checks:
                with self.assertRaises((OSError, ValueError)):
                    check()
        self.assertFalse((self.base / "merged").exists())
        missing = self.base / "stage-already-published"
        run.preserve_query_failure(missing, output, OSError(errno.EIO, "lost reply"))
        self.assertFalse(missing.exists())
