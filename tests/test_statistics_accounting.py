"""Accepted attempt inventory remains distinct from query statistics."""
from pathlib import Path
import tempfile
import unittest

from helpers import ROOT
from pipeline.reduce import accounting


class CampaignAccountingContract(unittest.TestCase):
    def test_accepted_manifest_attempt_join_and_evidence_distinction(self):
        report=accounting.inventory(
            ROOT/'data/campaign.json',
            'cc2c0593d8b48103560bed7ba46fa7f81a8137bae24994c6ef2316dd9265005d',
            ROOT/'data/raw_manifest.jsonl',
            '5f354cbc9e0bdfb7ead07adb341d74e4c98f14709d873f8f247585912e2df247',
            ROOT/'data/attempts.csv',
            'c550fffb652d0ff71945ee128cfc8fe475d9b1d64433454e9073fd2076c5d8d9')
        self.assertEqual(report['state'],'ACCEPTED_LEDGER_ONLY_NO_QUERY_CLOSURE')
        self.assertEqual(report['counts'],dict(accepted_sources=3000,attempts=3127,
            accepted_attempts=3000,discarded_attempts=127,
            successful_events=300000000))
        self.assertEqual({row['tune_id']:row['discarded_attempts']
            for row in report['by_tune']},
            {'MONASH':0,'JUNCTIONS':63,'CLOSEPACKING':64})
        self.assertEqual({(row['tune_id'],row['block_id']):
            (row['sources'],row['successful_events']) for row in report['by_block']},
            {(tune,block):(100,10000000) for tune in
             ('MONASH','JUNCTIONS','CLOSEPACKING') for block in range(1,11)})
        self.assertIn(dict(outcome='discarded',
            evidence_status='scheduler_log_confirmed',count=127),
            report['attempt_evidence'])
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory).resolve()/'accounting.json'
            receipt=accounting.write(report,path)
            self.assertEqual(receipt['bytes'],path.stat().st_size)
            with self.assertRaises(FileExistsError):accounting.write(report,path)
        with self.assertRaisesRegex(ValueError,'trusted physical digest'):
            accounting.inventory(ROOT/'data/campaign.json','0'*64,
                ROOT/'data/raw_manifest.jsonl','5f354cbc9e0bdfb7ead07adb341d74e4c98f14709d873f8f247585912e2df247',
                ROOT/'data/attempts.csv','c550fffb652d0ff71945ee128cfc8fe475d9b1d64433454e9073fd2076c5d8d9')


if __name__=='__main__':unittest.main()
