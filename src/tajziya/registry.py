# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""D2. Nodes are bound to implementations here and nowhere else.

0.2.0: a binding may name a language module (kind "module"), loaded by path from modules/.

A caller names a node. registry/bindings.json names the implementation, and this module
imports it by the kind the binding declares. No implementation id is written in code.
"""
import importlib
import json
import os
from functools import lru_cache

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SEGMENTING = {"juncture", "unspaced", "logogram", "syllabary", "vocalisation",
              "sign_sequence", "compounding", "abugida"}
MORPHOLOGICAL = {"paradigm", "root_pattern", "affix_chain", "compounding"}


def path(*parts):
    return os.path.join(ROOT, *parts)


def _load(*parts):
    with open(path(*parts), encoding="utf-8") as fh:
        return json.load(fh)


class Registry:
    def __init__(self):
        self.families_doc = _load("registry", "families.json")
        self.nodes_doc = _load("registry", "nodes.json")
        self.scripts_doc = _load("registry", "scripts.json")
        self.engines_doc = _load("registry", "engines.json")
        self.bindings = _load("registry", "bindings.json")["bindings"]
        self.conflicts = _load("registry", "conflicts.json")["conflicts"]
        self.coverage = _load("registry", "coverage.json")
        self.corpus_classes = _load("registry", "corpus_classes.json")["classes"]
        self.packages = {p["id"]: p for p in _load("roadmap", "packages.json")["packages"]}
        self.nodes = {n["id"]: n for n in self.nodes_doc["nodes"]}
        self.lineages = {x["id"]: x for x in self.families_doc["lineages"]}
        self.families = {x["id"]: x for x in self.families_doc["families"]}
        self.scripts = {x["code"]: x for x in self.scripts_doc["scripts"]}
        self.engines = {x["id"]: x for x in self.engines_doc["engines"]}

    def node(self, node_id):
        if node_id not in self.nodes:
            raise KeyError(f"no node '{node_id}'; the nodes are listed in registry/nodes.json")
        return self.nodes[node_id]

    def engines_of(self, node):
        """(language-axis engines from the lineage, script-axis engines from the scripts)."""
        lang = list(self.lineages[node["lineage"]]["language_engines"])
        script = []
        for code in node["scripts"]:
            for e in self.scripts[code]["engines"]:
                if e not in script:
                    script.append(e)
        return lang, script

    def refusal(self, node, layer):
        """What an unbuilt layer of this node needs, and the packages that build it."""
        lang, script = self.engines_of(node)
        lineage = f"P-LIN-{node['lineage']}"
        if layer == "L0":
            return (), ("P-L0-01", lineage)
        if layer == "L1":
            return (("abugida",), ("P-ENG-09",)) if "abugida" in script else ((), ("P-L1-01",))
        if layer == "L2":
            return ("sign_sequence",), ("P-ENG-11", lineage)
        pool = SEGMENTING if layer == "L3s" else MORPHOLOGICAL if layer == "L3m" else set()
        needs = tuple(e for e in lang + script if e in pool)
        packs = [self.engines[e]["package"] for e in needs]
        if layer == "L4":
            packs.append("P-L4-01")
        return needs, tuple(dict.fromkeys(packs + [lineage]))

    def bind(self, node_id, **options):
        node = self.node(node_id)
        b = self.bindings[node_id]
        if b["kind"] == "module":
            from . import modules
            mdir = path(*b["module"].split("/"))
            if modules.manifest(mdir)["node"] != node_id:
                raise ValueError(f"{b['module']} does not declare node {node_id}")
            return modules.bind(mdir, self, **options)
        module = importlib.import_module(f"tajziya.{b['kind']}s.{b['implementation']}")
        return module.make(node, self, **options)


@lru_cache(maxsize=1)
def load():
    return Registry()
