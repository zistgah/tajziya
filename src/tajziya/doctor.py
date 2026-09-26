# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""Registry integrity. Each check protects a clause in CONTRACT.md."""
import importlib
import json
import os
import re

from .registry import path
from .types import LAYERS, STATES

ISO3 = re.compile(r"^[a-z]{3}$")


def problems(reg):
    p = []
    ids = [n["id"] for n in reg.nodes_doc["nodes"]]
    if len(ids) != len(set(ids)):
        p.append("node ids are not unique")
    for n in reg.nodes.values():
        i = n["id"]
        if n["lineage"] not in reg.lineages:
            p.append(f"{i}: unknown lineage {n['lineage']}")
        p += [f"{i}: malformed ISO 639-3 code {c}" for c in n["iso639_3"] if not ISO3.match(c)]
        p += [f"{i}: unknown script {s}" for s in n["scripts"] if s not in reg.scripts]
        if n["status"]["poster"] not in ("I", "P", "U", "S", "C"):
            p.append(f"{i}: status {n['status']['poster']} is not one of I P U S C")
        if tuple(n["layers"]) != LAYERS:
            p.append(f"{i}: layers must be exactly {', '.join(LAYERS)}")
        for L, st in n["layers"].items():
            if st not in STATES:
                p.append(f"{i}: {L} state {st} is not one of {', '.join(STATES)}")
            elif st != "not_built" and L != "L2" and not n.get("scope_excludes"):
                p.append(f"{i}: {L} is {st} but the node declares nothing it excludes")
        if not n["iso639_3"] and n["lineage"] != "undeciphered":
            p.append(f"{i}: no ISO 639-3 code and not an undeciphered corpus")
        if i not in reg.bindings:
            p.append(f"{i}: not bound")
    for i, b in reg.bindings.items():
        if i not in reg.nodes:
            p.append(f"binding for unknown node {i}")
        if b["kind"] not in ("port", "frame"):
            p.append(f"{i}: binding kind {b['kind']}")
        try:
            importlib.import_module(f"tajziya.{b['kind']}s.{b['implementation']}")
        except Exception as e:
            p.append(f"{i}: binding does not import ({type(e).__name__}: {e})")
    for x in reg.lineages.values():
        if x["family"] not in reg.families:
            p.append(f"lineage {x['id']}: unknown family {x['family']}")
        p += [f"lineage {x['id']}: unknown engine {e}" for e in x["language_engines"] if e not in reg.engines]
        if f"P-LIN-{x['id']}" not in reg.packages:
            p.append(f"lineage {x['id']}: no package P-LIN-{x['id']}")
        if not any(n["lineage"] == x["id"] for n in reg.nodes.values()):
            p.append(f"lineage {x['id']}: holds no node")
    for s in reg.scripts.values():
        p += [f"script {s['code']}: unknown engine {e}" for e in s["engines"] if e not in reg.engines]
    for e in reg.engines.values():
        if e["package"] not in reg.packages:
            p.append(f"engine {e['id']}: no package {e['package']}")
    pk = reg.packages
    for k, v in pk.items():
        p += [f"{k}: depends on unknown {d}" for d in v["deps"] if d not in pk]
        if not v["acceptance"].strip():
            p.append(f"{k}: no acceptance")
        p += [f"{k}: label {lab} is not a capability" for lab in v["labels"] if not lab.startswith("needs:")]
    if not any(not v["deps"] for v in pk.values()):
        p.append("no zero-dependency package, so nobody can start")
    seen, stack = set(), set()

    def cyclic(k):
        if k in stack:
            return True
        if k in seen:
            return False
        stack.add(k)
        hit = any(cyclic(d) for d in pk[k]["deps"] if d in pk)
        stack.discard(k)
        seen.add(k)
        return hit
    if any(cyclic(k) for k in pk):
        p.append("the roadmap has a dependency cycle")
    p += [f"conflict {c['id']}: not held" for c in reg.conflicts if not c.get("held_as")]
    for k, t in reg.nodes_doc["stage_trees"].items():
        p += [f"stage tree {k}: unknown node {x}" for x in t["nodes"] if x not in reg.nodes]
    n = len(reg.nodes)
    for f in ("README.md", "seed.json", "misty.json"):
        fp = path(f)
        if os.path.exists(fp):
            with open(fp, encoding="utf-8") as fh:
                text = fh.read()
            p += [f"{f} claims {m} language and stage nodes; the registry holds {n}"
                  for m in re.findall(r"(\d+) language and stage nodes", text) if int(m) != n]
    dp, ip = path("descriptor.json"), path("INTEGRATION.md")
    if os.path.exists(dp) and os.path.exists(ip):
        with open(dp, encoding="utf-8") as fh:
            d = json.load(fh)
        with open(ip, encoding="utf-8") as fh:
            t = fh.read()
        for a in d.get("attachment_points", []):
            key = a.split(":")[0]
            if f"**{key}**" not in t:
                p.append(f"attachment point {key} is not enumerated in INTEGRATION.md")
    return p
