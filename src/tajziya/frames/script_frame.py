# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""The frame every ILM script stands in until a script module is bound for it.

L1, the pivot to the hub, refuses by name. L2 runs through the common orthography layer when
the script is encoded in Unicode, and refuses when it is not, because such text arrives as sign
numbers.
"""
from ..types import NotBuilt
from .. import scripts


class ScriptFrame:
    def __init__(self, node, reg):
        self.node, self._n, self._reg = node["id"], node, reg

    def layers(self):
        return dict(self._n["layers"])

    def _refuse(self, layer, what):
        needs, packages = self._reg.refusal(self._n, layer)
        raise NotBuilt(self.node, layer, what, packages, needs)

    def pivot(self, text):
        self._refuse("L1", "no pivot table for this script yet")

    def orthography(self, text):
        if self._n["layers"]["L2"] == "not_built":
            self._refuse("L2", "the script is not encoded in Unicode; text arrives as sign numbers")
        return scripts.orthography(text, self._n, self._reg)


def make(node, reg, **options):
    return ScriptFrame(node, reg)
