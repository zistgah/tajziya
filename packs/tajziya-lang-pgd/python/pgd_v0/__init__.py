# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""Gāndhārī (pgd): the language module, as handed over.

Every layer refuses until it is built. To build one: implement it here, set its state in
module.json, name what it leaves out in scope_excludes, cite attested examples in
reference/examples.json from sources listed in data/SOURCES.json, and run bash accept.sh.
"""
import os

from tajziya import api

HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class Port:
    def __init__(self, node, reg, module_dir):
        self.node, self._n, self._reg = node["id"], node, reg
        self._dir = module_dir
        self._man = api.manifest(module_dir)
        self.REFERENCE = api.reference(module_dir, "L3s")

    def layers(self):
        return dict(self._man["layers"])

    def phonology(self, text):
        api.refuse(self, "L0", "not yet written in this module")

    def pivot(self, text):
        api.refuse(self, "L1", "not yet written in this module")

    def orthography(self, text):
        if self._man["layers"]["L2"] == "not_built":
            api.refuse(self, "L2", "the script is not encoded in Unicode; text arrives as sign numbers")
        return api.orthography(text, self._n, self._reg)

    def segment(self, text):
        api.refuse(self, "L3s", "not yet written in this module")

    def analyse(self, word):
        api.refuse(self, "L3m", "not yet written in this module")

    def relate(self, tokens):
        api.refuse(self, "L4", "not yet written in this module")

    def join(self, words):
        api.refuse(self, "L3s", "not yet written in this module")


def make(node, reg, module_dir=None, **options):
    return Port(node, reg, module_dir or HERE)
