# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""The shapes every parser returns, and the refusal every unbuilt layer raises."""
from dataclasses import dataclass, field

LAYERS = ("L0", "L1", "L2", "L3s", "L3m", "L4")
LAYER_NAMES = {"L0": "phonology", "L1": "script pivot", "L2": "orthography",
               "L3s": "segmentation", "L3m": "morphology", "L4": "syntax"}
METHODS = {"L0": "phonology", "L1": "pivot", "L2": "orthography",
           "L3s": "segment", "L3m": "analyse", "L4": "relate"}
STATES = ("built", "wired_unproven", "not_built")


class NotBuilt(Exception):
    """A layer that is not built says so, names what it needs, and names the work that builds it."""

    def __init__(self, node, layer, what, packages, needs=()):
        self.node, self.layer, self.what = node, layer, what
        self.packages, self.needs = tuple(packages), tuple(needs)
        super().__init__(self.message())

    def message(self):
        need = f"; engines needed: {', '.join(self.needs)}" if self.needs else ""
        return (f"{self.node} {self.layer} ({LAYER_NAMES[self.layer]}) is not built: "
                f"{self.what}{need}; packages: {', '.join(self.packages) or 'none named'}")

    def as_dict(self):
        return {"node": self.node, "layer": self.layer, "state": "not_built", "what": self.what,
                "needs": list(self.needs), "packages": list(self.packages)}


@dataclass(frozen=True)
class Junction:
    left: str
    right: str
    merged: str
    rule: str


@dataclass(frozen=True)
class Segmentation:
    words: tuple
    junctions: tuple
    recombines: bool


@dataclass(frozen=True)
class TokenLattice:
    token: str
    alternatives: tuple


@dataclass(frozen=True)
class Result:
    node: str
    layer: str
    tokens: tuple
    provenance: dict = field(default_factory=dict)

    def as_dict(self):
        return {"node": self.node, "layer": self.layer, "provenance": self.provenance,
                "tokens": [{"token": t.token, "alternatives": [
                    {"words": list(s.words), "recombines": s.recombines,
                     "junctions": [vars(j) for j in s.junctions]} for s in t.alternatives]}
                    for t in self.tokens]}
