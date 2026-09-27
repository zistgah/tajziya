# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""tajziya (تجزیہ): parsers for the classical languages of the human corpus, by family.

A node is a language at a stage, in declared scripts, holding a declared corpus. Every node
is bound through registry/bindings.json. One node parses; every other node refuses by name.
"""
from ._vendor.unknown import Unknown, known
from .types import NotBuilt, Junction, Segmentation, TokenLattice, Result, LAYERS

__version__ = "0.2.0"
__all__ = ["Unknown", "known", "NotBuilt", "Junction", "Segmentation", "TokenLattice",
           "Result", "LAYERS", "__version__"]
