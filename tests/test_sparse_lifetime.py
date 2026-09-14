"""Observe native destruction, including sparse objects owned by a ROOT file."""

import gc
from pathlib import Path
import unittest

from pipeline.query import collection, merge


class SparseLifetime(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.ROOT = collection._root()
        except ImportError as error:
            raise unittest.SkipTest(str(error))
        cls.ROOT.gInterpreter.Declare('''
            #include "THnSparse.h"
            namespace PhaseASparseLifetimeTest {
                int live = 0;
                class TrackedSparse : public THnSparseD {
                public:
                    TrackedSparse() { ++live; }
                    ~TrackedSparse() override { --live; }
                };
                TrackedSparse* make() { return new TrackedSparse; }
            }
        ''')

    def test_reader_releases_cpp_allocation_after_file_close(self):
        ROOT = self.ROOT

        class File:
            def __init__(self, attached):
                self.attached = attached
                self.objects = ROOT.TList()
                self.objects.SetOwner(True)

            def Get(self, _name):
                histogram = ROOT.PhaseASparseLifetimeTest.make()
                ROOT.SetOwnership(histogram, False)
                if self.attached:
                    self.objects.Add(histogram)
                return histogram

            def GetList(self):
                return self.objects

            def Close(self):
                self.objects.Delete()

        for attached in (False, True):
            with self.subTest(directory_owned=attached):
                file = File(attached)
                for _ in range(8):
                    histogram = collection.read_sparse(file, 'sparse_activity')
                    self.assertEqual(ROOT.PhaseASparseLifetimeTest.live, 1)
                    file.Close()
                    self.assertEqual(ROOT.PhaseASparseLifetimeTest.live, 1)
                    del histogram
                    gc.collect()
                    self.assertEqual(ROOT.PhaseASparseLifetimeTest.live, 0)

                def interrupted_read():
                    histogram = collection.read_sparse(file, 'sparse_activity')
                    raise RuntimeError('interrupted sparse scan')

                with self.assertRaisesRegex(RuntimeError, 'interrupted'):
                    interrupted_read()
                gc.collect()
                self.assertEqual(ROOT.PhaseASparseLifetimeTest.live, 0)

    def test_selected_clone_has_an_owner_and_survives_input_close(self):
        fixture = (Path(__file__).resolve().parent /
                   'fixtures/query_multitune/queries/shard-0000/query.root')
        file = self.ROOT.TFile.Open(str(fixture), 'READ')
        histogram = collection.read_sparse(file, 'sparse_activity')
        selected = merge._select_tune(histogram, 0, histogram.GetEntries())
        expected = list(collection._cells(selected))
        self.assertTrue(selected.__python_owns__)
        file.Close()
        del histogram
        gc.collect()
        self.assertEqual(list(collection._cells(selected)), expected)


if __name__ == '__main__':
    unittest.main()
