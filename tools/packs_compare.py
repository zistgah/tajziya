#!/usr/bin/env python3
# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""The packages checked into packs/ are exactly what the generator makes.

    python3 tools/packs_compare.py packs <freshly generated folder>

Compares the two trees file by file, by SHA-256. Exit 1 on any file missing, extra or different.
"""
import hashlib
import os
import sys


def tree(root):
    out = {}
    for base, dirs, files in os.walk(root):
        dirs.sort()
        for f in files:
            p = os.path.join(base, f)
            with open(p, "rb") as fh:
                out[os.path.relpath(p, root)] = hashlib.sha256(fh.read()).hexdigest()
    return out


def main(argv=None):
    a, b = (sys.argv[1:] if argv is None else argv)[:2]
    x, y = tree(a), tree(b)
    missing = sorted(set(y) - set(x))
    extra = sorted(set(x) - set(y))
    differ = sorted(k for k in set(x) & set(y) if x[k] != y[k])
    for label, items in (("not checked in", missing), ("checked in but not generated", extra), ("different", differ)):
        if items:
            print(f"packs_compare: {len(items)} {label}, e.g. {', '.join(items[:3])}")
    if missing or extra or differ:
        return 1
    print(f"packs_compare: {len(x)} files, identical to the generator's")
    return 0


if __name__ == "__main__":
    sys.exit(main())
