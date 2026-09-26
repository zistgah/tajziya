# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
import copy
import unittest

import _base  # noqa: F401
from tajziya import doctor
from tajziya.registry import load


class TestRegistry(unittest.TestCase):
    def setUp(self):
        self.reg = load()

    def test_doctor_clean(self):
        self.assertEqual(doctor.problems(self.reg), [])

    def test_every_poster_row_section_is_present(self):
        secs = {n["status"]["source"].split(";")[0] for n in self.reg.nodes.values()}
        for i in range(1, 19):
            self.assertIn(f"poster I §{i}", secs)

    def test_nothing_is_bound_to_the_mock_or_the_template(self):
        for b in self.reg.bindings.values():
            self.assertNotIn(b["implementation"], ("mock", "template"))

    def test_exactly_one_node_parses(self):
        self.assertEqual([n for n, x in self.reg.nodes.items() if x["layers"]["L3s"] == "built"], ["cls"])

    def test_undeciphered_corpora_carry_no_language(self):
        und = [n for n in self.reg.nodes.values() if n["lineage"] == "undeciphered"]
        self.assertEqual(len(und), 2)
        for n in und:
            self.assertEqual((n["iso639_3"], n["status"]["poster"], n["layers"]["L2"]), ([], "U", "not_built"))

    def test_conflicts_are_held_not_ruled(self):
        self.assertTrue(all(c["held_as"] and c["ruled"] is False for c in self.reg.conflicts))

    def test_dravidian_is_a_family_not_a_node(self):
        self.assertNotIn("dravidian", self.reg.nodes)
        self.assertEqual(sorted(n for n, x in self.reg.nodes.items() if x["lineage"] == "dravidian"),
                         ["kan", "mal", "tam", "tel"])


class TestDoctorBites(unittest.TestCase):
    """Each mutation must be reported: a check that cannot fail proves nothing."""

    def mutated(self, fn):
        reg = copy.deepcopy(load())
        fn(reg)
        return doctor.problems(reg)

    def test_a_built_layer_without_exclusions(self):
        def f(r):
            r.nodes["lat"]["layers"]["L3s"] = "built"
        self.assertTrue(any("declares nothing it excludes" in p for p in self.mutated(f)))

    def test_an_unknown_status(self):
        def f(r):
            r.nodes["lat"]["status"]["poster"] = "X"
        self.assertTrue(any("is not one of I P U S C" in p for p in self.mutated(f)))

    def test_a_dangling_dependency(self):
        def f(r):
            r.packages["P-SAN-01"]["deps"] = ["P-NOPE"]
        self.assertTrue(any("depends on unknown P-NOPE" in p for p in self.mutated(f)))

    def test_a_cycle(self):
        def f(r):
            r.packages["P-SAN-03"]["deps"] = ["P-SAN-02"]
        self.assertTrue(any("cycle" in p for p in self.mutated(f)))

    def test_an_unbound_node(self):
        def f(r):
            del r.bindings["lat"]
        self.assertTrue(any("lat: not bound" in p for p in self.mutated(f)))

    def test_a_model_name_as_a_label(self):
        def f(r):
            r.packages["P-SAN-01"]["labels"] = ["ai:claude"]
        self.assertTrue(any("is not a capability" in p for p in self.mutated(f)))


if __name__ == "__main__":
    unittest.main()
