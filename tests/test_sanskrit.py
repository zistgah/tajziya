# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
import hashlib
import json
import os
import unittest

import _base
from tajziya import Unknown, conllu
from tajziya.registry import load, path
from tajziya.types import NotBuilt


class TestSanskrit(unittest.TestCase):
    def setUp(self):
        self.reg = load()
        self.p = self.reg.bind("cls")

    def readings(self, text, port=None):
        return [s.words for s in (port or self.p).segment(text).tokens[0].alternatives]

    def test_the_upstream_worked_examples(self):
        for text, expected in self.p.REFERENCE.items():
            self.assertEqual(self.readings(text), [tuple(e) for e in expected])

    def test_ambiguity_is_returned_whole(self):
        port = self.p.with_lexicon({"deva", "devā", "iha"})
        self.assertEqual(sorted(self.readings("deveha", port)), [("deva", "iha"), ("devā", "iha")])

    def test_every_reading_joins_back(self):
        port = self.p.with_lexicon({"deva", "devā", "iha"})
        for s in port.segment("deveha").tokens[0].alternatives:
            self.assertTrue(s.recombines)
            self.assertEqual(port.join(s.words), "deveha")

    def test_junction_is_recorded_and_its_sutra_is_not_invented(self):
        j = self.p.segment("tatraiva").tokens[0].alternatives[0].junctions[0]
        self.assertEqual((j.left, j.right, j.merged), ("a", "e", "ai"))
        self.assertTrue(j.rule.startswith("not established"))

    def test_devanagari_is_refused_by_name(self):
        with self.assertRaises(NotBuilt) as cm:
            self.p.segment("नेति")
        self.assertEqual(cm.exception.layer, "L1")
        self.assertIn("P-SAN-01", cm.exception.packages)

    def test_unbuilt_layers_refuse(self):
        for fn, layer in ((self.p.analyse, "L3m"), (self.p.relate, "L4"),
                          (self.p.phonology, "L0"), (self.p.pivot, "L1")):
            with self.assertRaises(NotBuilt) as cm:
                fn("neti")
            self.assertEqual(cm.exception.layer, layer)

    def test_an_unknown_word_is_reported_not_guessed(self):
        self.assertEqual(self.readings("rāmavanam"), [])

    def test_the_open_edition_holds_every_sutra(self):
        r = self.p.rules()
        self.assertEqual((len(r), r[0].id, r[-1].id), (3983, "1.1.1", "8.4.68"))
        self.assertIn("ashtadhyayi", self.p.rules_provenance)
        self.assertIn("MIT", self.p.rules_provenance)

    def test_the_restricted_compilation_is_local_or_absent(self):
        r = self.p.rules(source="local")
        if isinstance(r, Unknown):
            self.assertTrue(r.needs[0].endswith("sutras_1.1-1.3.json"))
        else:
            self.assertEqual(len(r), 152)

    def test_a_file_that_is_not_the_pinned_one_is_refused(self):
        p = os.path.join(_base.scratch("rules"), "sutras.json")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write("[]")
        with self.assertRaises(ValueError):
            self.p.rules(source="local", data_path=p)

    def test_a_pinned_file_loads(self):
        rows = [{"id": "9.9.1", "sutra_krama": 99901, "kaumudi_krama": None, "type": None,
                 "term": None, "sutra": "fixture", "padaccheda": None}]
        p = os.path.join(_base.scratch("rules2"), "sutras.json")
        with open(p, "w", encoding="utf-8") as fh:
            json.dump(rows, fh)
        with open(p, "rb") as fh:
            pin = hashlib.sha256(fh.read()).hexdigest()
        self.assertEqual([s.id for s in self.p.rules(source="local", data_path=p, pin=pin)], ["9.9.1"])

    def test_conllu_uses_a_multiword_token(self):
        block = conllu.sentences(self.p.segment("neti"))[0]
        self.assertTrue(conllu.valid(block))
        self.assertIn("1-2\tneti\t", block)

    def test_conllu_refuses_to_truncate(self):
        port = self.p.with_lexicon({"deva", "devā", "iha"})
        self.assertIsInstance(conllu.sentences(port.segment(" ".join(["deveha"] * 7))), Unknown)


if __name__ == "__main__":
    unittest.main()
