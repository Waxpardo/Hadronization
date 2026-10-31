import unittest

from helpers import ROOT, load_json, parse_card, sha256


class TuneCardContract(unittest.TestCase):
    def test_current_card_files_and_digests_are_exact(self):
        expected = {
            "monash.cmnd": "35b8b01e72163e062834b8f942b97f3e765fa01a5a26ecf6814faac3155efa8a",
            "junctions.cmnd": "86330d6f0116676bd83f802a39c595f9ab289f57eadaceed10cbd5897d22a9c7",
            "close_packing.cmnd": "2e561e36f79297c60c8b3f08866933b4c6053786d96abb8ffde8677ceb943603",
        }
        self.assertEqual({path.name for path in (ROOT / "config/tunes").iterdir()},
                         set(expected))
        for name, digest in expected.items():
            path = ROOT / "config/tunes" / name
            with self.subTest(name=name):
                self.assertEqual(sha256(path), digest)
                self.assertTrue(parse_card(path))

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
        campaign = load_json("data/campaign.json")
        accepted = campaign["accepted_source"]["tune_cards"]
        self.assertEqual(accepted["MONASH"]["accepted_effective_sha256"],
                         "8dfa3ea896e8358cece4e3270133efe310b114724bd8cf06fa477fe7cd46b1f9")
        self.assertEqual(accepted["JUNCTIONS"]["accepted_effective_sha256"],
                         "db1c64736ae984f4e6496bbedeba9816f65ed8f3c668d67adfcfc87a58a70878")
        self.assertEqual(accepted["CLOSEPACKING"]["accepted_effective_sha256"],
                         "0a3bca5525e8a06dd9e5d9b34fed2e0d460e9b9945f3bd4df51f927dd89a6378")


if __name__ == "__main__":
    unittest.main()
