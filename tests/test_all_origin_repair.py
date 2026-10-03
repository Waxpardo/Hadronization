"""Cross-boundary regressions for the approved all-origin family release."""
import copy
import unittest
from types import SimpleNamespace

from pipeline.reduce import archive_v4, native, native_runner, projection as p


class AllOriginRepair(unittest.TestCase):
    def _population(self):
        profiles=('inclusive','pt_1_0p15','pt_2p5_0p5')
        pair=('MONASH',1,0,421,-421,-1,25)
        trigger=('MONASH',1,0,421)
        pair_rows=[
            dict(profile_id=profile,tune_id=pair[0],block_id=pair[1],
                 activity_bin=pair[2],trigger_pdg=pair[3],
                 associate_pdg=pair[4],sign=pair[5],dphi_bin=pair[6],
                 count=1,sumw=2.,sumw2=4.,sumabsw=2.)
            for profile in profiles]
        trigger_rows=[
            dict(profile_id=profile,tune_id=trigger[0],block_id=trigger[1],
                 activity_bin=trigger[2],trigger_pdg=trigger[3],
                 count=2,sumw=5.,sumw2=13.,sumabsw=5.)
            for profile in profiles]
        primitives=native.NativePrimitives({}, {
            (profile,)+trigger: native.AdditiveCell(5.,13.,1)
            for profile in profiles}, {
            (profile,)+pair: native.AdditiveCell(2.,4.,1)
            for profile in profiles}, SimpleNamespace(),profiles,'a15_eta4',
            (421,),((421,-421),))
        proof=dict(cells=[{k:v for k,v in pair_rows[0].items()
                           if k!='profile_id'}],profile_pair_cells=pair_rows[1:],
                   profile_trigger_cells=trigger_rows,
                   scanned_profile_ids=list(profiles))
        return primitives,proof

    def test_profile_oracle_checks_each_pair_and_zero_partner_denominator(self):
        primitives,proof=self._population()
        native_runner.verify_reconstructed_pair_cells(primitives,copy.deepcopy(proof))
        wrong=copy.deepcopy(proof)
        wrong['profile_trigger_cells'][1]['sumw']=4.
        with self.assertRaisesRegex(ValueError,'trigger denominator population differs'):
            native_runner.verify_reconstructed_pair_cells(primitives,wrong)
        stale=copy.deepcopy(proof)
        stale['profile_pair_cells'].pop()
        with self.assertRaisesRegex(ValueError,'pair key domain differs'):
            native_runner.verify_reconstructed_pair_cells(primitives,stale)

    def test_scoped_diagnostics_are_versioned_and_old_receipts_stay_readable(self):
        legacy=native.RawDiagnostics().report()
        scoped=native.RawDiagnostics().report('all_origins')
        self.assertNotIn('closure_population_scope',legacy)
        self.assertEqual(scoped['closure_population_scope'],
                         'HISTORICAL_ANALYZED_CLOSURE_ROWS')
        self.assertEqual(scoped['origin_pair_population_scope'],
                         'ALL_ORIGIN_SELECTED_PAIRS')
        self.assertEqual(native.RawDiagnostics().report('historical_hard_root')[
            'origin_pair_population_scope'],
            'HISTORICAL_HARD_ROOT_SELECTED_PAIRS')
        def receipt(version):
            body=dict(schema='hadronization_observed_support_diagnostics_v'+version,
                tune_id='MONASH',block_id=1,event_moments_sha256='a'*64,
                activity_counts=[],n_mpi_counts=[],process_counts=[],
                pthat_sum=(0.).hex(),hard_scale_sum=(0.).hex(),
                natural_final_hadrons=0,natural_final_weighted_sum=(0.).hex(),
                charm_constituents=0,charm_constituent_weighted_sum=(0.).hex(),
                beauty_constituents=0,beauty_constituent_weighted_sum=(0.).hex(),
                strict_selected_final_hadrons=0,
                strict_selected_final_weighted_sum=(0.).hex(),
                origin_pairs=[],closure_terms=[])
            if version=='2':
                body.update(origin_pair_population_scope='ALL_ORIGIN_SELECTED_PAIRS',
                            closure_population_scope='HISTORICAL_ANALYZED_CLOSURE_ROWS')
            return dict(body,content_sha256=p.digest(body))
        old,new=receipt('1'),receipt('2')
        p.validate(old,'SupportDiagnosticReceiptAny')
        p.validate(new,'SupportDiagnosticReceiptAny')
        self.assertNotIn('population_scope',archive_v4._fields({
            'support_diagnostic_receipts':[old]})['diagnostic_closure'])
        self.assertEqual(archive_v4._fields({
            'support_diagnostic_receipts':[new]})['diagnostic_closure'][
                'population_scope'],'s')
        mutant=copy.deepcopy(new)
        mutant['closure_population_scope']='ALL_ORIGIN_SELECTED_PAIRS'
        with self.assertRaises(ValueError):
            p.validate(mutant,'SupportDiagnosticReceiptAny')


if __name__=='__main__':
    unittest.main()
