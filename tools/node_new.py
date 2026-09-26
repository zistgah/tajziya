#!/usr/bin/env python3
# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""Turn a stub node into a code package by copying the template port under a new id.

    python3 tools/node_new.py --node akk --impl akkadian_v0 [--out DIR] [--bind]

The copy refuses every layer exactly as the stub did, so nothing starts out pretending.
--bind points registry/bindings.json at the new port. Exit 0 written, 1 refused.
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--node", required=True)
    ap.add_argument("--impl", required=True)
    ap.add_argument("--out", default=os.path.join(ROOT, "src", "tajziya", "ports"))
    ap.add_argument("--bind", action="store_true")
    a = ap.parse_args()
    if not re.match(r"^[a-z][a-z0-9_]*_v\d+$", a.impl):
        print("node_new: refused, an implementation id is lowercase and versioned, for example akkadian_v0")
        return 1
    with open(os.path.join(ROOT, "registry", "nodes.json"), encoding="utf-8") as fh:
        nodes = {n["id"]: n for n in json.load(fh)["nodes"]}
    if a.node not in nodes:
        print(f"node_new: refused, no node '{a.node}' in registry/nodes.json")
        return 1
    dst = os.path.join(a.out, a.impl)
    if os.path.exists(dst):
        print(f"node_new: refused, {os.path.relpath(dst, ROOT)} already exists")
        return 1
    with open(os.path.join(ROOT, "src", "tajziya", "ports", "template", "__init__.py"), encoding="utf-8") as fh:
        text = fh.read()
    head = '"""D3. The empty port a contributor fills; tools/node_new.py copies it for a node.'
    if text.count(head) != 1:
        print("node_new: refused, the template's docstring anchor moved")
        return 1
    name = nodes[a.node]["name"]
    text = text.replace(head, f'"""Port for {name} ({a.node}), copied from the template port.', 1)
    text = text.replace("TemplatePort", "Port")
    os.makedirs(dst)
    with open(os.path.join(dst, "__init__.py"), "w", encoding="utf-8") as fh:
        fh.write(text)
    if a.bind:
        bp = os.path.join(ROOT, "registry", "bindings.json")
        with open(bp, encoding="utf-8") as fh:
            doc = json.load(fh)
        doc["bindings"][a.node] = {"kind": "port", "implementation": a.impl}
        with open(bp, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=1, ensure_ascii=False)
            fh.write("\n")
    print(f"node_new: {os.path.relpath(dst, ROOT)} written" + (" and bound" if a.bind else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
