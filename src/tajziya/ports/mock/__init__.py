# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""D3. The port that runs with nothing attached, used only by the harness's own tests.

It segments each whitespace token as one word and says so in its provenance. It is never
bound to a node; tests/test_registry.py asserts that.
"""
from ...types import LAYERS, NotBuilt, Result, Segmentation, TokenLattice


class MockPort:
    REFERENCE = {"mock": [("mock",)]}
    REFERENCE_INPUT = {"L3s": "mock"}

    def __init__(self, node, reg):
        self.node, self._n = node["id"], node

    def layers(self):
        return {L: ("built" if L == "L3s" else "not_built") for L in LAYERS}

    def _refuse(self, layer):
        raise NotBuilt(self.node, layer, "mock port", (f"P-LIN-{self._n['lineage']}",))

    def phonology(self, text):
        self._refuse("L0")

    def pivot(self, text):
        self._refuse("L1")

    def orthography(self, text):
        self._refuse("L2")

    def segment(self, text):
        return Result(self.node, "L3s", tuple(TokenLattice(t, (Segmentation((t,), (), True),))
                                              for t in text.split()), {"mock": True})

    def analyse(self, word):
        self._refuse("L3m")

    def relate(self, tokens):
        self._refuse("L4")

    def join(self, words):
        return "".join(words)


def make(node, reg, **options):
    return MockPort(node, reg)
