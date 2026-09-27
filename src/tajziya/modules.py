# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""Language modules: found by scanning modules/, validated, loaded by path.

A module is a directory holding module.json and a Python package whose __init__.py defines
make(node, reg, module_dir=None, **options). It is discovered, never listed. It is used only
once registry/bindings.json binds it, and before that it is judged on its own by
`python3 -m tajziya accept <directory>`.
"""
import importlib.util
import json
import os
import re
import sys

from .registry import path
from .types import LAYERS, STATES

SCHEMA = "tajziya.module/1"
IMPL = re.compile(r"^[a-z][a-z0-9_]*_v[0-9]+$")
REQUIRED = ("schema", "node", "implementation", "api", "version", "layers", "scope_excludes", "accepts",
            "engines", "entry", "sources", "reference", "licence", "requires")


def discover(root=None):
    base = os.path.join(root or path(), "modules")
    if not os.path.isdir(base):
        return {}
    return {d: os.path.join(base, d) for d in sorted(os.listdir(base))
            if os.path.isfile(os.path.join(base, d, "module.json"))}


def manifest(module_dir):
    with open(os.path.join(module_dir, "module.json"), encoding="utf-8") as fh:
        return json.load(fh)


def _inside(child, parent):
    child, parent = os.path.realpath(child), os.path.realpath(parent)
    return os.path.commonpath([child, parent]) == parent


def problems(man, reg, module_dir=None):
    from .api import API_VERSION
    missing = [k for k in REQUIRED if k not in man]
    if missing:
        return [f"module.json lacks {', '.join(missing)}"]
    p = []
    if man["schema"] != SCHEMA:
        p.append(f"schema is {man['schema']}, not {SCHEMA}")
    if str(man["api"]).split(".")[0] != API_VERSION:
        p.append(f"written for API {man['api']}; this tajziya offers API {API_VERSION}")
    if man["node"] not in reg.nodes:
        p.append(f"node {man['node']} is not in the registry")
    if not IMPL.match(man["implementation"]):
        p.append(f"implementation id {man['implementation']} is not lowercase and versioned, like akk_v0")
    if tuple(man["layers"]) != LAYERS:
        p.append(f"layers must be exactly {', '.join(LAYERS)}")
    for L, st in man["layers"].items():
        if st not in STATES:
            p.append(f"{L} state {st} is not one of {', '.join(STATES)}")
        elif st != "not_built" and L != "L2" and not man["scope_excludes"]:
            p.append(f"{L} is {st} but scope_excludes names nothing it leaves out")
    p += [f"accepts unknown script {s}" for s in man["accepts"] if s not in reg.scripts]
    p += [f"names unknown engine {e}" for e in man["engines"] if e not in reg.engines]
    p += [f"requires {r}, which this repository does not hold" for r in man["requires"]
          if not os.path.exists(path(*r.split("/")))]
    if module_dir:
        for key in ("entry", "sources", "reference"):
            target = os.path.join(module_dir, man[key])
            if not _inside(target, module_dir):
                p.append(f"{key} {man[key]} lies outside the module")
            elif not os.path.isfile(target):
                p.append(f"{key} {man[key]} does not exist")
    return p


def load(module_dir, man):
    entry = os.path.join(module_dir, man["entry"])
    name = f"tajziya_modules.{man['implementation']}"
    spec = importlib.util.spec_from_file_location(name, entry, submodule_search_locations=[os.path.dirname(entry)])
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    if not callable(getattr(mod, "make", None)):
        raise ImportError(f"{man['entry']} defines no make(node, reg, module_dir=None, **options)")
    return mod


def bind(module_dir, reg, node_id=None, **options):
    man = manifest(module_dir)
    if node_id and man["node"] != node_id:
        raise ValueError(f"the module at {module_dir} implements {man['node']}, not {node_id}")
    probs = problems(man, reg, module_dir)
    if probs:
        raise ValueError("; ".join(probs))
    return load(module_dir, man).make(reg.node(man["node"]), reg, module_dir=module_dir, **options)
