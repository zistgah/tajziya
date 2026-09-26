# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""D1. The one capability surface every parser in this repository presents.

No implementation lives here and none is named. Each method is one ILM linguistic layer.
A layer that is not built raises tajziya.types.NotBuilt naming the package that builds it.
"""
from typing import Protocol, runtime_checkable


@runtime_checkable
class Parser(Protocol):
    node: str

    def layers(self) -> dict: ...            # layer id to built, wired_unproven or not_built
    def phonology(self, text: str): ...      # L0
    def pivot(self, text: str): ...          # L1
    def orthography(self, text: str): ...    # L2
    def segment(self, text: str): ...        # L3s
    def analyse(self, word: str): ...        # L3m
    def relate(self, tokens): ...            # L4
    def join(self, words): ...               # the inverse of segment, used to prove a reading
