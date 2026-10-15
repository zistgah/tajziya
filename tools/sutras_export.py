#!/usr/bin/env python3
# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""The sutras as a dataset anyone can download, and the default categories they can start from.

    python3 tools/sutras_export.py [--check]

Writes docs/data/sutras.csv and docs/data/sutras.json (every sutra: id, adhyaya, pada, number, krama,
Siddhanta Kaumudi number, type, term, text, padaccheda, Romenagri form) and
docs/data/categories.default.json (the sutras grouped by type, by adhyaya and by pada). The
categories page reads these; it never edits them.
"""
import csv
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "modules", "cls", "data")
OUT = os.path.join(ROOT, "docs", "data")
COLS = ["id", "adhyaya", "pada", "number", "krama", "kaumudi", "type", "term", "sutra", "padaccheda", "romenagri"]


def rows():
    with open(os.path.join(DATA, "ashtadhyayi", "sutraani.tsv"), encoding="utf-8") as fh:
        cols = next(fh).rstrip("\n").split("\t")
        base = [dict(zip(cols, l.rstrip("\n").split("\t"))) for l in fh]
    rom = {}
    p = os.path.join(DATA, "romenagri", "sutras.tsv")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as fh:
            next(fh)
            rom = {a: b for a, b, _ in (l.rstrip("\n").split("\t") for l in fh)}
    out = []
    for r in base:
        a, pa, n = r["id"].split(".")
        out.append({"id": r["id"], "adhyaya": a, "pada": pa, "number": n, "krama": r["krama"], "kaumudi": r["kaumudi"],
                    "type": r["type"], "term": r["term"], "sutra": r["sutra"], "padaccheda": r["padaccheda"],
                    "romenagri": rom.get(r["id"], "")})
    return out


def files():
    rs = rows()
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=COLS, lineterminator="\n")
    w.writeheader()
    w.writerows(rs)
    group = lambda key, label: {"name": label, "categories": [
        {"name": k, "sutras": [r["id"] for r in rs if key(r) == k]} for k in dict.fromkeys(key(r) for r in rs)]}
    default = {"schema": "tajziya.categories/1",
               "note": "Default groupings derived from the data. Any set of categories may replace them on categories.html.",
               "sets": [group(lambda r: r["type"], "type"), group(lambda r: r["adhyaya"], "adhyaya"),
                        group(lambda r: r["adhyaya"] + "." + r["pada"], "pada")]}
    dump = lambda x: json.dumps(x, ensure_ascii=False, separators=(",", ":")) + "\n"
    return {os.path.join(OUT, "sutras.csv"): buf.getvalue(),
            os.path.join(OUT, "sutras.json"): dump({"schema": "tajziya.sutras/1", "columns": COLS,
                                                    "rows": [[r[c] for c in COLS] for r in rs]}),
            os.path.join(OUT, "categories.default.json"): dump(default)}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    want = files()
    if "--check" in argv:
        stale = [os.path.relpath(p, ROOT) for p, t in want.items() if not os.path.exists(p) or open(p, encoding="utf-8").read() != t]
        print("sutras_export: current" if not stale else f"sutras_export: STALE: {', '.join(stale)}")
        return 0 if not stale else 1
    for p, t in want.items():
        open(p, "w", encoding="utf-8").write(t)
    print(f"sutras_export: {len(rows())} sutras written as CSV and JSON, with the default categories")
    return 0


if __name__ == "__main__":
    sys.exit(main())
