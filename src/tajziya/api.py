# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""The surface a language module imports. API version 1.

A module uses what is here and nothing else from tajziya, so the core can change beneath it.
Changing anything here changes API_VERSION, and the loader refuses a module written for
another version. A port keeps three attributes the helpers rely on: node (the id), _n (the
registry record) and _reg (the registry).
"""
import json
import os

from . import conllu
from ._vendor.unknown import Unknown, known
from .registry import path as repo_path
from .scripts import detect as detect_scripts, orthography
from .types import LAYER_NAMES, LAYERS, METHODS, STATES, Junction, NotBuilt, Result, Segmentation, TokenLattice

API_VERSION = "1"


def refuse(port, layer, what):
    """Raise NotBuilt for this port's node, naming the engines and packages the registry derives."""
    needs, packages = port._reg.refusal(port._n, layer)
    raise NotBuilt(port.node, layer, what, packages, needs)


def manifest(module_dir):
    """The module's own module.json."""
    with open(os.path.join(module_dir, "module.json"), encoding="utf-8") as fh:
        return json.load(fh)


def reference(module_dir, layer="L3s"):
    """The module's attested examples for one layer, as {input: [reading, ...]}."""
    p = os.path.join(module_dir, "reference", "examples.json")
    if not os.path.exists(p):
        return {}
    with open(p, encoding="utf-8") as fh:
        examples = json.load(fh).get("examples", [])
    return {e["input"]: [tuple(r) for r in e["readings"]] for e in examples if e.get("layer") == layer}


__all__ = ["API_VERSION", "Junction", "LAYERS", "LAYER_NAMES", "METHODS", "NotBuilt", "Result", "STATES",
           "Segmentation", "TokenLattice", "Unknown", "conllu", "detect_scripts", "known", "manifest", "orthography",
           "reference", "refuse", "repo_path"]
