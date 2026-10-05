# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""The stub every unbuilt node is bound to: the frame of its family.

The frame knows the node's lineage, its scripts and the engines they imply. Orthography (L2)
runs, because normalisation and script evidence are common to every encoded script. Every
other layer refuses by name and points to the packages that would build it.
"""
from .. import scripts
from ..types import NotBuilt

WHAT = {"L0": "no phonological base is defined for this node",
        "L1": "no script pivot is bound for this node",
        "L2": "the script is not encoded in Unicode, so the text arrives as sign numbers",
        "L3s": "no segmentation is built for this node",
        "L3m": "no morphology is built for this node",
        "L4": "no syntactic relations are built for this node"}


class FamilyFrame:
    def __init__(self, node, reg):
        self.node, self._n, self._reg = node["id"], node, reg
        self.lineage = reg.lineages.get(node.get("lineage"))
        self.engines = reg.engines_of(node)

    def layers(self):
        return dict(self._n["layers"])

    def _refuse(self, layer):
        needs, packages = self._reg.refusal(self._n, layer)
        raise NotBuilt(self.node, layer, WHAT[layer], packages, needs)

    def phonology(self, text):
        self._refuse("L0")

    def pivot(self, text):
        self._refuse("L1")

    def orthography(self, text):
        if self._n["layers"]["L2"] == "not_built":
            self._refuse("L2")
        return scripts.orthography(text, self._n, self._reg)

    def segment(self, text):
        self._refuse("L3s")

    def analyse(self, word):
        self._refuse("L3m")

    def relate(self, tokens):
        self._refuse("L4")

    def join(self, words):
        self._refuse("L3s")


def make(node, reg, **options):
    return FamilyFrame(node, reg)
