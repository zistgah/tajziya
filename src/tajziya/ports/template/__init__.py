# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""D3. The empty port a contributor fills; tools/node_new.py copies it for a node.

Orthography runs through the common layer where the script is encoded. Every other layer
refuses until someone writes it, and says which package that is.
"""
from ... import scripts
from ...types import NotBuilt


class TemplatePort:
    def __init__(self, node, reg):
        self.node, self._n, self._reg = node["id"], node, reg

    def layers(self):
        return dict(self._n["layers"])

    def _refuse(self, layer):
        needs, packages = self._reg.refusal(self._n, layer)
        raise NotBuilt(self.node, layer, "not yet written in this port", packages, needs)

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
    return TemplatePort(node, reg)
