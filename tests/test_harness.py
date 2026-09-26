# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
import unittest

import _base  # noqa: F401
from tajziya import harness
from tajziya.ports.mock import make as make_mock
from tajziya.registry import load
from tajziya.types import NotBuilt, Result, Segmentation, TokenLattice


class TestConformance(unittest.TestCase):
    def test_every_node_conforms(self):
        s = harness.run_all(load())
        self.assertEqual(s["failed"], [])
        self.assertEqual(s["nodes"], len(load().nodes))

    def test_the_mock_conforms(self):
        reg = load()
        self.assertEqual([f for f in harness.check(make_mock(reg.node("cls"), reg), reg.node("cls"), reg)
                          if not f[1]], [])


class Liar:
    """Wraps the real Classical Sanskrit port and breaks one promise."""

    def __init__(self):
        self.reg = load()
        self.real = self.reg.bind("cls")
        self.REFERENCE = self.real.REFERENCE
        self.REFERENCE_INPUT = self.real.REFERENCE_INPUT

    def __getattr__(self, name):
        return getattr(self.real, name)


class TestHarnessBites(unittest.TestCase):
    def failed(self, liar):
        return {f[0] for f in harness.check(liar, liar.reg.node("cls"), liar.reg) if not f[1]}

    def test_a_fabricated_analysis_is_caught(self):
        class L(Liar):
            def analyse(self, word):
                return [("fabricated",)]
        self.assertIn("TJZ-C2", self.failed(L()))

    def test_a_dropped_reading_is_caught(self):
        class L(Liar):
            def segment(self, text):
                r = self.real.segment(text)
                return Result(r.node, r.layer, tuple(TokenLattice(t.token, ()) for t in r.tokens))
        self.assertIn("TJZ-C3", self.failed(L()))

    def test_a_reading_that_does_not_join_back_is_caught_despite_its_own_claim(self):
        class L(Liar):
            def segment(self, text):
                r = self.real.segment(text)
                return Result(r.node, r.layer, tuple(
                    TokenLattice(t.token, tuple(Segmentation(tuple(reversed(s.words)), s.junctions, True)
                                                for s in t.alternatives)) for t in r.tokens))
        self.assertIn("TJZ-C4", self.failed(L()))

    def test_a_built_layer_that_refuses_is_caught(self):
        class L(Liar):
            def segment(self, text):
                raise NotBuilt("cls", "L3s", "liar", ("P-SAN-07",))
        self.assertIn("TJZ-C1", self.failed(L()))

    def test_a_refusal_naming_no_real_package_is_caught(self):
        class L(Liar):
            def phonology(self, text):
                raise NotBuilt("cls", "L0", "liar", ("P-NOPE",))
        self.assertIn("TJZ-C1", self.failed(L()))


if __name__ == "__main__":
    unittest.main()
