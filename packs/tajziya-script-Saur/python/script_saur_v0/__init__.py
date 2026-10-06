# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""Saurashtra (Saur): the script module, as handed over.

L1 refuses until a pivot table is built. L2 runs through the common orthography layer while
the script is encoded in Unicode, and refuses when it is not.
"""
import os

from tajziya import api

HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class Port:
    def __init__(self, node, reg, module_dir):
        self.node, self._n, self._reg = node["id"], node, reg
        self._dir = module_dir
        self._man = api.manifest(module_dir)

    def layers(self):
        return dict(self._man["layers"])

    def pivot(self, text):
        api.refuse(self, "L1", "no pivot table for this script yet")

    def orthography(self, text):
        if self._man["layers"]["L2"] == "not_built":
            api.refuse(self, "L2", "the script is not encoded in Unicode; text arrives as sign numbers")
        return api.orthography(text, self._n, self._reg)


def make(node, reg, module_dir=None, **options):
    return Port(node, reg, module_dir or HERE)
