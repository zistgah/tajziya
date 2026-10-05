# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""The sutra database: derived from ashtadhyayi.com's data, cross-checked, reviewed."""
import collections
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import review_gen  # noqa: E402
import sutra_import  # noqa: E402
from tajziya.registry import load  # noqa: E402

FLAGS = os.path.join(ROOT, "modules", "cls", "data", "review", "flags.json")


class Sutras(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = load().bind("cls")
        cls.r = {s.id: s for s in cls.p.rules()}

    def test_all_3983_in_devanagari_with_their_fields(self):
        s = self.r["1.1.1"]
        self.assertEqual(len(self.r), 3983)
        self.assertEqual((s.sutra, s.type, s.term, s.padaccheda, s.kaumudi_krama, s.sutra_krama),
                         ("वृद्धिरादैच्", "samjna", "वृद्धि", "वृद्धिः १/१ आत्-ऐच् १/१", 16, 11001))

    def test_the_types_including_the_adhikara_sutras(self):
        self.assertEqual(collections.Counter(s.type for s in self.r.values()),
                         {"vidhi": 3629, "samjna": 200, "atidesha": 67, "adhikara": 64, "paribhasha": 23})

    def test_padaccheda_writes_indeclinables_and_bare_words(self):
        self.assertEqual(self.r["1.2.18"].padaccheda, "न ०/० क्त्वा सेट् १/१")
        self.assertTrue(self.r["1.2.55"].padaccheda.endswith("स्यात्"))
        self.assertEqual(sutra_import.padaccheda("न$S$0$0$##इति$S$0$0$"), "न ०/० इति ०/०")
        self.assertEqual(sutra_import.typed("S$गुणसंज्ञा$"), ("samjna", "गुण", "गुणसंज्ञा"))
        with self.assertRaises(ValueError):
            sutra_import.typed("Q$x$")

    def test_the_review_flags_carry_no_restricted_text(self):
        flags = json.load(open(FLAGS, encoding="utf-8"))["flags"]
        self.assertEqual(len(flags), 53)
        self.assertEqual(len({f["id"] for f in flags}), 47)
        self.assertTrue(all(set(f) == {"id", "field", "against", "status"} for f in flags))
        self.assertTrue(all(f["id"] in self.r for f in flags))

    def test_the_second_open_source_agrees_but_for_eight(self):
        self.assertEqual(review_gen.slp1_to_deva("vfdDirAdEc"), "वृद्धिरादैच्")
        self.assertEqual(review_gen.slp1_to_deva("adeN guRaH"), "अदेङ् गुणः")
        mism = review_gen.vidyut_mismatches(review_gen.load_sutras())
        self.assertEqual(len(mism), 8, mism)

    def test_the_review_page_is_generated_and_current(self):
        self.assertEqual(review_gen.main(["--check"]), 0)


if __name__ == "__main__":
    unittest.main()
