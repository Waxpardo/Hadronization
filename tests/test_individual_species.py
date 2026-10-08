"""Independent domain and identity checks for the individual-state recipe."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from pipeline.query import model
from pipeline.reduce import family, projection

ROOT = Path(__file__).resolve().parents[1]


class IndividualSpecies(unittest.TestCase):
    def setUp(self):
        self.analysis, self.sha = model.checked_analysis(
            ROOT / 'config/analysis-individual-species.json')
        binding = self.analysis['associate_family_map']
        self.recipe = family.checked_family_map(ROOT / binding['path'], binding['sha256'])

    def test_complete_catalog_open_flavour_identity_partition(self):
        catalog = json.loads((ROOT / 'config/heavy-catalog.json').read_text())['states']
        # Independent predicate, with the inherited beauty-first sector rule.
        charm = {s['pdg'] for s in catalog if s['nb'] + s['nbbar'] == 0
                 and s['nc'] != s['ncbar']}
        beauty = {s['pdg'] for s in catalog if s['nb'] != s['nbbar']}
        self.assertEqual((len(charm), len(beauty)), (84, 118))
        self.assertEqual(set(self.recipe.members), charm | beauty)
        self.assertEqual(self.analysis['pair_query_registry']['associate_pdgs'],
                         {'charm': sorted(charm), 'beauty': sorted(beauty)})
        for pdg in self.recipe.members:
            self.assertEqual(self.recipe.members_by_destination[pdg], (pdg,))
        # D*, Xi prime/star, Sigma star and multiply-heavy species are separate.
        for pdg in (413, 4312, 4314, 4114, 4412, 541, 5412):
            self.assertEqual(self.recipe.destination_by_member[pdg], pdg)
        self.assertTrue({441,443,551,553}.isdisjoint(self.recipe.members))

    def test_existing_query_reuse_and_signed_flavour(self):
        construction, _ = model.checked_analysis(ROOT / 'config/analysis-all-origin.json')
        model.compatible_interpretation(construction, self.analysis)
        for field in ('profiles','axes','activities','pair_acceptance','trigger_selection',
                      'percentile_intervals','estimator_policy'):
            self.assertEqual(construction[field], self.analysis[field])
        states, pairs = model.observable_pairs(self.analysis, 'projection_formulas_v4')
        by_pdg = {s['pdg']: s for s in states}
        by_pair = {(p['trigger_pdg'],p['associate_pdg']): p for p in pairs}
        self.assertEqual(len(pairs),1212)
        for trigger in (421,4122):
            self.assertEqual(by_pair[trigger,-4314]['sign'],-1)
            self.assertEqual(by_pair[trigger,-4412]['sign'],-1)
        self.assertEqual(by_pair[521,5314]['sign'],-1)
        self.assertEqual(by_pair[5122,-5314]['sign'],-1)
        self.assertEqual(by_pdg[4412]['qc'],2)
        self.assertEqual(by_pdg[541]['sector'],'beauty')
        altered=copy.deepcopy(self.analysis)
        altered['axes']['eta']['low']=-5.
        with self.assertRaises(ValueError): model.compatible_interpretation(construction,altered)
        altered=copy.deepcopy(self.analysis)
        altered['pair_query_registry']['associate_pdgs']['beauty'].append(443)
        with self.assertRaises(ValueError): model.compatible_interpretation(construction,altered)

    def test_identity_does_not_admit_unproved_grouping(self):
        original=json.loads((ROOT/'config/grouping-individual-species.json').read_text())
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'recipe.json'
            for mutant in ('combine','hidden','conjugate','unknown','bad_type','bad_member'):
                data=copy.deepcopy(original)
                group=next(g for g in data['groups'] if g['destination_pdg']==413)
                if mutant=='combine':group['members'].append(411)
                elif mutant=='hidden':group.update(destination_pdg=443,members=[443],family='pdg-443')
                elif mutant=='conjugate':data['groups'].remove(group)
                elif mutant=='bad_type':group['destination_pdg']=[]
                elif mutant=='bad_member':group['members']=[{}]
                else:group.update(destination_pdg=999999,members=[999999],family='pdg-999999')
                path.write_text(json.dumps(data))
                with self.assertRaises(ValueError):
                    family.checked_family_map(path,hashlib.sha256(path.read_bytes()).hexdigest())

    def test_ground_and_excited_counts_are_not_combined(self):
        rows=[]
        for block in range(1,11):
            for pdg,count in ((-4132,block),(-4312,2*block),(-4314,7*block)):
                rows.append(dict(tune='MONASH',block=block,trigger_pdg=421,
                    associate_pdg=pdg,sign=-1,count=float(count),sumw2=float(count),
                    trigger_count=float(100+block)))
        result=family.group_additive_rows(rows,self.recipe)
        self.assertEqual(len(result),30)
        self.assertEqual(sum(r['count'] for r in result if r['associate_pdg']==-4132),55.)
        self.assertEqual(sum(r['count'] for r in result if r['associate_pdg']==-4314),385.)
        self.assertEqual({r['trigger_count'] for r in result},{float(100+b) for b in range(1,11)})


if __name__=='__main__': unittest.main()
