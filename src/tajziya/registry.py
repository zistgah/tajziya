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
        self.script_bindings = _load("registry", "script_bindings.json")["bindings"]
        self._ilm, self._held = {}, None

    def node(self, node_id):
        if node_id in self.nodes:
            return self.nodes[node_id]
        if self.has_node(node_id):
            return self.coverage_node(node_id)
        raise KeyError(f"no node '{node_id}'; the nodes are in registry/nodes.json and registry/ilm/languages.tsv")

    def _ilm_table(self, name):
        if name not in self._ilm:
            import csv
            with open(path("registry", "ilm", name), encoding="utf-8", newline="") as fh:
                self._ilm[name] = {r["code"]: r for r in csv.DictReader(fh, delimiter="\t")}
        return self._ilm[name]

    @property
    def ilm_languages(self):
        """Every ISO 639-3 language the ILM registry (the 3D explorer's data) lists."""
        return self._ilm_table("languages.tsv")

    @property
    def ilm_scripts(self):
        """Every ISO 15924 script the ILM registry lists."""
        return self._ilm_table("scripts.tsv")

    def held_codes(self):
        """Codes a curated node already holds: its id and its ISO 639-3 codes."""
        if self._held is None:
            self._held = {c for n in self.nodes.values() for c in n["iso639_3"]} | set(self.nodes)
        return self._held

    def coverage_ids(self):
        """ILM languages no curated node holds: each becomes a coverage node."""
        return sorted(c for c in self.ilm_languages if c not in self.held_codes())

    def has_node(self, node_id):
        return node_id in self.nodes or (node_id in self.ilm_languages and node_id not in self.held_codes())

    def coverage_node(self, code):
        r = self.ilm_languages[code]
        return {"id": code, "kind": "coverage", "name": r["name"], "language": r["name"], "stage": None,
                "lineage": None, "iso639_3": [code], "scripts": [],
                "status": {"poster": "coverage", "source": f"ILM registry: {r['type']}, {r['scope']}, {r['status']}"},
                "corpus": "Not yet assessed. The ILM registry lists the language; its corpus is assessed once its "
                          "profile is established (P-PROF-01).",
                "layers": {"L0": "not_built", "L1": "not_built", "L2": "wired_unproven", "L3s": "not_built",
                           "L3m": "not_built", "L4": "not_built"},
                "scope_excludes": [], "ilm": dict(r)}

    def script_ids(self):
        return sorted(self.ilm_scripts)

    def script_node(self, code):
        """A script as the refusal machinery sees it: no lineage, one script."""
        r = self.ilm_scripts[code]
        encoded = bool(r["unicode_version"])
        return {"id": f"script:{code}", "kind": "script", "name": r["name"], "lineage": None, "scripts": [code],
                "encoded": encoded, "layers": {"L1": "not_built", "L2": "wired_unproven" if encoded else "not_built"},
                "ilm": dict(r)}

    def lineage_packages(self, node):
        if node.get("lineage") in self.lineages:
            return (f"P-LIN-{node['lineage']}",)
        if node.get("kind") == "coverage":
            return ("P-PROF-01",)
        return ()

    def bind_script(self, code, **options):
        if code not in self.ilm_scripts:
            raise KeyError(f"no script '{code}' in registry/ilm/scripts.tsv")
        b = self.script_bindings.get(code)
        if b:
            from . import modules
            return modules.bind(path(*b["module"].split("/")), self, **options)
        from .frames import script_frame
        return script_frame.make(self.script_node(code), self)

    def engines_of(self, node):
        """(language-axis engines from the lineage, script-axis engines from the scripts)."""
        lin = self.lineages.get(node.get("lineage"))
        lang = list(lin["language_engines"]) if lin else []
        script = []
        for code in node["scripts"]:
            for e in self.scripts.get(code, {}).get("engines", ()):
                if e not in script:
                    script.append(e)
        return lang, script

    def refusal(self, node, layer):
        """What an unbuilt layer of this node needs, and the packages that build it."""
        lang, script = self.engines_of(node)
        lin = self.lineage_packages(node)
        if layer == "L0":
            return (), ("P-L0-01",) + lin
        if layer == "L1":
            return (("abugida",), ("P-ENG-09",)) if "abugida" in script else ((), ("P-L1-01",))
        if layer == "L2":
            return ("sign_sequence",), ("P-ENG-11",) + lin
        pool = SEGMENTING if layer == "L3s" else MORPHOLOGICAL if layer == "L3m" else set()
        needs = tuple(e for e in lang + script if e in pool)
        packs = [self.engines[e]["package"] for e in needs]
        if layer == "L4":
            packs.append("P-L4-01")
        return needs, tuple(dict.fromkeys(packs + list(lin)))

    def bind(self, node_id, **options):
        node = self.node(node_id)
        b = self.bindings.get(node_id) or (
            {"kind": "frame", "implementation": "frame_family"} if node.get("kind") == "coverage" else None)
        if b is None:
            raise KeyError(f"node '{node_id}' has no binding in registry/bindings.json")
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
