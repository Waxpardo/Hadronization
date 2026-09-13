"""Cold ROOT-only numerical archive tests for the bounded P1/P4/P6 seam."""
import copy
import importlib.util
import math
from pathlib import Path
import tempfile
import unittest

from helpers import ROOT


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


class TypedNumericalArchiveContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a = module('bounded_typed_archive', 'pipeline/reduce/archive.py')
        try:
            cls.a.r.runtime_module().resolve(require_root=True)
        except ValueError as error:
            raise unittest.SkipTest(str(error))
        cls.build_temporary = tempfile.TemporaryDirectory()
        cls.build_work = Path(cls.build_temporary.name).resolve() / 'archive-build'

    @classmethod
    def tearDownClass(cls):
        cls.build_temporary.cleanup()

    def setUp(self):
        from test_projection_interface import ProjectionInterfaceContract
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name).resolve()
        fixture = ProjectionInterfaceContract()
        fixture.setUpClass()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        self.request, self.value, self.routes = fixture.result_fixture()

    def independent_dense_value(self):
        value = copy.deepcopy(self.value)
        template = self.value['points'][1]
        points = []
        complements = [float(index) for index in range(10)]
        leave_mean = sum(complements) / 10
        variance = .9 * sum((item - leave_mean) ** 2 for item in complements)
        for tune in ('MONASH', 'JUNCTIONS'):
            point = copy.deepcopy(template)
            point['key']['curve']['tune_id'] = tune
            point['semantic_id'] = self.a.p.digest(dict(
                scientific_request_sha256=value['scientific_request_sha256'],
                point_key=point['key']))
            point['standard_error'] = self.a.p.hex64(math.sqrt(variance))
            point['variance'] = self.a.p.hex64(variance)
            point['uncertainty_status'] = 'AVAILABLE'
            for block in point['block_values']:
                block['tune_id'] = tune
            points.append(point)
        families = []
        for active, tune in enumerate(('MONASH', 'JUNCTIONS')):
            rows = []
            for complement in complements:
                row = [None, None]; row[active] = self.a.p.hex64(complement); rows.append(row)
            means = [None, None]; means[active] = self.a.p.hex64(leave_mean)
            families.append(dict(tune_id=tune, source_family_digest=self.a.p.digest([tune]),
                block_ids=list(range(1, 11)), complements=rows, leave_mean=means,
                covariance_prefactor=self.a.p.hex64(.9)))
        group = copy.deepcopy(value['covariance'][0])
        group.update(ordered_point_keys=[point['key'] for point in points],
            valid_mask=[True, True], units_by_point=['1', '1'], status='AVAILABLE_FULL',
            independent_families=families, representation='DENSE',
            dense_rows=[[self.a.p.hex64(variance), self.a.p.hex64(0.)],
                        [self.a.p.hex64(0.), self.a.p.hex64(variance)]], rank_bound=2)
        value['points'], value['covariance'] = points, [group]
        return value

    def science_transport(self, value, name='science.tsv'):
        path = self.base / name
        path.write_text('hadronization_typed_science_v1\n' +
                        '\n'.join(self.a.views(value)) + '\nEND\n')
        return path

    def with_valid_uncertainty(self, value, valid_indices):
        value = copy.deepcopy(value)
        for index, point in enumerate(value['points']):
            if index not in valid_indices:
                point.update(standard_error=None, variance=None,
                             uncertainty_status='WITHHELD_UNCERTAINTY',
                             reasons=['UNEQUAL_DESIGN_EXPOSURE'])
        group = value['covariance'][0]
        group['valid_mask'] = [index in valid_indices
                               for index in range(len(value['points']))]
        group['status'] = ('AVAILABLE_FULL' if all(group['valid_mask']) else
                           'AVAILABLE_PARTIAL' if any(group['valid_mask']) else
                           'UNAVAILABLE')
        families = []
        for family in group['independent_families']:
            family['leave_mean'] = [item if index in valid_indices else None
                                    for index, item in enumerate(family['leave_mean'])]
            family['complements'] = [
                [item if index in valid_indices else None
                 for index, item in enumerate(row)]
                for row in family['complements']]
            if any(item is not None for item in family['leave_mean']):
                families.append(family)
        group['independent_families'] = families
        group['dense_rows'] = [
            [item if row in valid_indices and column in valid_indices else None
             for column, item in enumerate(values)]
            for row, values in enumerate(group['dense_rows'])]
        return value

    def test_cold_root_only_direct_points_factors_covariance_and_bindings(self):
        path = self.base / 'TEST_ONLY-numerics.root'
        receipt = self.a.write(self.value, path, self.build_work)
        # The DTO reconstruction remains a compatibility view, while this
        # reader opens only explicit scientific TTrees and ignores nodes.
        restored = self.a.read(path, self.build_work,
                               receipt['root_sha256'], receipt['value_sha256'])
        science = self.a.read_science(path, self.build_work,
                                      receipt['root_sha256'])
        self.assertEqual(restored, self.value)
        binding = science['bindings']
        self.assertEqual(binding['science_content_sha256'],
                         self.value['science_content_sha256'])
        self.assertEqual(binding['analysis_config_sha256'],
                         self.value['provenance']['analysis_config_sha256'])
        self.assertEqual(binding['input_root_sha256'],
                         self.value['artifact_binding']['root_sha256'])
        self.assertEqual(binding['uncertainty_scope'], 'FINITE_MC_ONLY')
        self.assertEqual(len(science['points']), len(self.value['points']))
        first, zero, missing = science['points']
        self.assertEqual(float.fromhex(first[21]), -2.)
        self.assertEqual((first[20], first[23]), ('1', '0'))
        self.assertEqual((zero[23], float.fromhex(zero[24])), ('1', 0.))
        self.assertEqual((missing[20], missing[23]), ('0', '0'))
        self.assertEqual({row[5] for row in science['covariance_factors']},
                         {str(i) for i in range(1, 11)})
        self.assertTrue(all(len(self.a.decode(row[4])) == 64
                            for row in science['covariance_factors']))
        self.assertEqual(len(science['covariance_points']), 3)
        self.assertEqual(len(science['covariance_values']), 9)
        with self.assertRaises(FileExistsError):
            self.a.write(self.value, path, self.build_work)

    def test_direct_g9_metadata_requires_version_and_rejects_resigned_model_lie(self):
        value = copy.deepcopy(self.value)
        value['schema'] = self.a.p.RESULT_SCHEMA_G9
        value['resolved']['g9_science'] = self.a.p.g9_science_legacy({
            'scope': {'roles': [{'role_id': 'spectra.signed_heavy',
                'required_curve_keys': [{'associate_pdg': 521}]}]}})
        valid = self.science_transport(value, 'g9-science.tsv')
        science = self.a.from_science_transport(valid)
        self.assertEqual(science['g9_science'], value['resolved']['g9_science'])
        lines = valid.read_text().splitlines()
        absent = self.base / 'g9-absent.tsv'
        absent.write_text('\n'.join(line for line in lines
            if not line.startswith('M\t')) + '\n')
        with self.assertRaisesRegex(ValueError, 'G9 scientific metadata/schema'):
            self.a.from_science_transport(absent)
        index = next(i for i,line in enumerate(lines) if line.startswith('M\t'))
        metadata = dict(value['resolved']['g9_science'], status_low=80)
        lines[index] = '\t'.join(['M',self.a.encode(self.a.p.canonical(metadata)),
                                  self.a.encode(self.a.p.digest(metadata))])
        tampered = self.base / 'g9-resigned-lie.tsv'
        tampered.write_text('\n'.join(lines) + '\n')
        with self.assertRaisesRegex(ValueError, 'G9 selection/normalization model'):
            self.a.from_science_transport(tampered)

    def test_direct_reader_rejects_factor_not_matching_dense_and_point_variance(self):
        transport = self.base / 'mutant.tsv'
        self.a.transport(self.value, transport)
        lines = transport.read_text().splitlines()
        position = next(i for i, line in enumerate(lines)
                        if line.startswith('F\t') and line.split('\t')[2] == '1')
        fields = lines[position].split('\t')
        fields[7] = float(1.).hex()
        lines[position] = '\t'.join(fields)
        transport.write_text('\n'.join(lines) + '\n')
        env, binary, unused = self.a.build(self.build_work)
        path = self.base / 'TEST_ONLY-mutant.root'
        self.a.execute(binary, env, 'pack', transport, path)
        sha = self.a.p.file_digest(path)
        with self.assertRaisesRegex(ValueError, 'typed factor'):
            self.a.read_science(path, self.build_work, sha)
        with self.assertRaisesRegex(ValueError, 'actual typed ROOT values differ'):
            self.a.read(path, self.build_work, sha,
                        self.a.p.digest(self.value))

    def test_missing_negative_and_zero_dispersion_survive_exact_typed_masks(self):
        path = self.base / 'TEST_ONLY-statuses.root'
        receipt = self.a.write(self.value, path, self.build_work)
        science = self.a.read_science(path, self.build_work,
                                      receipt['root_sha256'])
        rows = science['points']
        statuses = [(self.a.decode(row[22]), self.a.decode(row[25])) for row in rows]
        self.assertEqual(statuses[0], ('AVAILABLE', 'WITHHELD_UNCERTAINTY'))
        self.assertEqual(statuses[1], ('AVAILABLE', 'AVAILABLE_ZERO_DISPERSION'))
        self.assertEqual(statuses[2], ('UNDEFINED', 'WITHHELD_UNCERTAINTY'))

    def test_independent_valid_families_have_exact_dense_zero_covariance(self):
        science = self.a.from_science_transport(
            self.science_transport(self.independent_dense_value()))
        cells = {(int(row[2]), int(row[3])): float.fromhex(row[5])
                 for row in science['covariance_values']}
        self.assertEqual(cells[0, 1], 0.)
        self.assertEqual(cells[1, 0], 0.)

    def test_direct_reader_rejects_key_family_leaf_primitive_and_unit_mutants(self):
        lines = self.science_transport(self.independent_dense_value()).read_text().splitlines()
        mutants = {}
        wrong_sign = copy.deepcopy(lines)
        index = next(i for i, line in enumerate(wrong_sign) if line.startswith('P\t'))
        fields = wrong_sign[index].split('\t'); fields[10] = '-411'; wrong_sign[index] = '\t'.join(fields)
        mutants['key digest'] = wrong_sign
        detached = copy.deepcopy(lines)
        index = next(i for i, line in enumerate(detached) if line.startswith('F\t') and line.split('\t')[6] == '1')
        fields = detached[index].split('\t'); fields[3] = self.a.encode('UNBOUND_REFERENCE'); detached[index] = '\t'.join(fields)
        mutants['factor family'] = detached
        wrong_family_identity = copy.deepcopy(lines)
        index = next(i for i, line in enumerate(wrong_family_identity)
                     if line.startswith('F\t') and line.split('\t')[6] == '1')
        fields = wrong_family_identity[index].split('\t'); fields[4] = self.a.encode('a' * 64)
        wrong_family_identity[index] = '\t'.join(fields)
        mutants['factor source family identity'] = wrong_family_identity
        invalid_leaf = copy.deepcopy(lines)
        index = next(i for i, line in enumerate(invalid_leaf)
                     if line.startswith('F\t') and line.split('\t')[5:7] == ['5', '1'])
        fields = invalid_leaf[index].split('\t'); fields[6] = '0'; invalid_leaf[index] = '\t'.join(fields)
        mutants['factor leaf validity'] = invalid_leaf
        mutants['primitive K10'] = [line for line in lines if not line.startswith('B\t')]
        wrong_units = copy.deepcopy(lines)
        index = next(i for i, line in enumerate(wrong_units) if line.startswith('G\t'))
        fields = wrong_units[index].split('\t'); fields[7] = self.a.encode('GeV'); wrong_units[index] = '\t'.join(fields)
        mutants['covariance point units'] = wrong_units
        for expected, content in mutants.items():
            with self.subTest(expected=expected):
                path = self.base / ('mutant-' + expected.replace(' ', '-') + '.tsv')
                path.write_text('\n'.join(content) + '\n')
                with self.assertRaisesRegex(ValueError, expected):
                    self.a.from_science_transport(path)

    def test_withheld_error_masks_require_only_families_of_valid_points(self):
        baseline = self.independent_dense_value()
        all_withheld = self.a.from_science_transport(self.science_transport(
            self.with_valid_uncertainty(baseline, set()), 'all-withheld.tsv'))
        self.assertEqual((all_withheld['source_family_binding'],
                          len(all_withheld['covariance_factors'])), (True, 0))
        no_covariance = [line for line in self.science_transport(
            self.with_valid_uncertainty(baseline, set()), 'all-withheld-with-groups.tsv'
        ).read_text().splitlines() if not line.startswith(('G\t', 'F\t', 'C\t'))]
        path = self.base / 'all-withheld-no-covariance.tsv'
        path.write_text('\n'.join(no_covariance) + '\n')
        science = self.a.from_science_transport(path)
        self.assertEqual((len(science['covariance_points']),
                          len(science['covariance_factors']),
                          len(science['covariance_values'])), (0, 0, 0))
        monash_only = self.a.from_science_transport(self.science_transport(
            self.with_valid_uncertainty(baseline, {0}), 'monash-only.tsv'))
        self.assertEqual({self.a.decode(row[3])
                          for row in monash_only['covariance_factors']}, {'MONASH'})

    def test_available_errors_require_complete_covariance_and_bound_family_ids(self):
        lines = self.science_transport(self.independent_dense_value()).read_text().splitlines()
        cases = {
            'capability absent': [line for line in lines if not line.startswith('V\t')],
            'required covariance domain': [line for line in lines
                if not line.startswith(('G\t', 'F\t', 'C\t'))],
            'factor family domain': [line for line in lines if not line.startswith('F\t')],
            'dense covariance domain': [line for line in lines if not line.startswith('C\t')],
        }
        blank = copy.deepcopy(lines)
        for index, line in enumerate(blank):
            if line.startswith('F\t'):
                fields = line.split('\t'); fields[4] = '-'; blank[index] = '\t'.join(fields)
        cases['source family binding is blank'] = blank
        for expected, content in cases.items():
            with self.subTest(expected=expected):
                path = self.base / ('missing-' + expected.replace(' ', '-') + '.tsv')
                path.write_text('\n'.join(content) + '\n')
                with self.assertRaisesRegex(ValueError, expected):
                    self.a.from_science_transport(path)

    def test_legacy_transport_exact_read_preserves_absent_family_branch(self):
        path = self.base / 'legacy-dump.tsv'
        with path.open('w', encoding='ascii') as stream:
            stream.write('hadronization_typed_root_transport_v1\n')
            root = self.a.nodes(self.value, stream)
            for line in self.a.views(self.value, source_family_binding=False):
                stream.write(line + '\n')
            stream.write('ROOT\t' + str(root) + '\nEND\n')
        self.assertEqual(self.a.from_transport(path), self.value)
        science_path = self.base / 'legacy-science.tsv'
        science_path.write_text('hadronization_typed_science_v1\n' +
            '\n'.join(self.a.views(self.value, source_family_binding=False)) + '\nEND\n')
        science = self.a.from_science_transport(science_path)
        self.assertFalse(science['source_family_binding'])


if __name__ == '__main__':
    unittest.main()
