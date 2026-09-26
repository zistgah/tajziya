# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
import json
import os
import unittest

import _base
from tajziya import elimination
from tajziya.registry import load

with open(os.path.join(_base.ROOT, "tests", "fixtures", "coverage_synthetic.json"), encoding="utf-8") as fh:
    FIX = json.load(fh)


class TestRule(unittest.TestCase):
    def computed(self, node):
        return elimination.decide(node, FIX["rows"])["computed"]

    def test_a_corpus_held_only_here_is_irreducible(self):
        self.assertEqual(self.computed("x-a"), "I")

    def test_translation_is_never_recovery(self):
        self.assertEqual(self.computed("x-b"), "I")

    def test_lossless_recovery_with_evidence_is_a_compression_candidate(self):
        self.assertEqual(self.computed("x-d"), "C")

    def test_an_unknown_cell_leaves_the_node_provisional(self):
        self.assertEqual(self.computed("x-f"), "P")

    def test_an_untested_node_is_provisional(self):
        self.assertEqual(self.computed("x-g"), "P")

    def test_declared_loss_blocks_recovery(self):
        self.assertEqual(self.computed("x-h"), "I")

    def test_recovery_without_evidence_does_not_count(self):
        self.assertEqual(self.computed("x-j"), "I")


class TestMinimum(unittest.TestCase):
    def test_nothing_is_eliminated_or_certified_without_evidence(self):
        reg = load()
        m = elimination.minimum(reg)
        self.assertFalse(m["certified"])
        self.assertIn("the corpus universe is not frozen", m["reasons"])
        self.assertIn("the loss function is not frozen", m["reasons"])
        self.assertEqual(len(m["L"]) + len(m["S"]["nodes"]) + len(m["corpus_objects"]), len(reg.nodes))
        self.assertEqual(m["comparison"]["differs"], [])

    def test_certification_is_only_relative_even_when_frozen(self):
        reg = load()
        rows = [{"id": f"R-{n}", "cells": {n: {"relation": "original", "evidence": "fixture"}}}
                for n, x in reg.nodes.items() if x["status"]["poster"] not in ("S", "U")]
        m = elimination.minimum(reg, {"frozen": {"universe": True, "loss_function": True}, "rows": rows})
        self.assertTrue(m["certified"])
        self.assertEqual(m["scope"], "relative to the declared universe and loss function only")


if __name__ == "__main__":
    unittest.main()
