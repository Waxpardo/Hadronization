"""Observe native destruction, including sparse objects owned by a ROOT file."""

import gc
from pathlib import Path
import unittest
import weakref

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

    def test_owned_block_components_survive_input_close_and_are_released(self):
        fixture = (Path(__file__).resolve().parent /
                   'fixtures/query_multitune/queries/shard-0000/query.root')
        file = self.ROOT.TFile.Open(str(fixture), 'READ')
        histogram = collection.read_sparse(file, 'sparse_activity')
        expected = list(collection._cells(histogram))
        components = [merge._empty_like(histogram, 'activity_block_%02d' % block)
                      for block in range(1, 11)]
        merge._native().Accumulate(histogram, components, 0)
        self.assertTrue(all(component.__python_owns__ for component in components))
        references = [weakref.ref(component) for component in components]
        file.Close()
        del histogram
        gc.collect()
        for block in range(1, 11):
            self.assertEqual(list(collection._cells(components[block-1])),
                             [cell for cell in expected if cell[0][1] == block])
        del components
        gc.collect()
        self.assertTrue(all(reference() is None for reference in references))


if __name__ == '__main__':
    unittest.main()
