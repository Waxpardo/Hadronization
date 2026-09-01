import itertools
import unittest

from helpers import ROOT, load_json, parse_card, sha256


class TuneCardContract(unittest.TestCase):
    def test_card_hashes_are_preserved(self):
        expected = {
            "monash.cmnd": "defd7f5dff774e790ffa773b3186341e89bd1fe7a5101f8fb491e3b10b156b23",
            "junctions.cmnd": "bbadecf78528637b1d80edd5594d0f3ea4d3ab73d0d44bc1e7e07c7bc25a41d8",
            "close_packing.cmnd": "dd0755ae85c340f7e3a438931bed14afa433220f164f84fcb0e18d4ae6f2f4de",
        }
        self.assertEqual({path.name for path in (ROOT / "config/tunes").iterdir()},
                         set(expected))
        for name, digest in expected.items():
            self.assertEqual(sha256(ROOT / "config/tunes" / name), digest)

    def test_common_values_and_tune_differences(self):
        study = load_json("config/study.json")
        cards = {
            row["name"]: parse_card(ROOT / row["card"])
            for row in study["tunes"]}
        common = study["tune_card_contract"]["common_required_values"]
        for tune, settings in cards.items():
            for key, value in common.items():
                self.assertEqual(settings.get(key), value, "{} {}".format(tune, key))
        allowed = set(study["tune_card_contract"]["allowed_tune_differences"])
        all_keys = set().union(*(set(card) for card in cards.values()))
        differing = {
            key for key in all_keys
            if len({cards[tune].get(key) for tune in cards}) > 1}
        self.assertTrue(differing)
        self.assertTrue(differing <= allowed, sorted(differing - allowed))
        self.assertNotIn("SigmaProcess:renormMultFac", all_keys)
        self.assertNotIn("SigmaProcess:factorMultFac", all_keys)


if __name__ == "__main__":
    unittest.main()
