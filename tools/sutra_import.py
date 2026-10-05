#!/usr/bin/env python3
# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""Derive the sutra database from ashtadhyayi.com's published data, deterministically.

    python3 tools/sutra_import.py <checkout of github.com/ashtadhyayi-com/data> [--check]

Reads sutraani/data.txt, refuses it unless it matches the pin in modules/cls/data/SOURCES.json,
and writes modules/cls/data/ashtadhyayi/sutraani.tsv: one row per sutra with its number, its
Siddhanta Kaumudi number, its type, the term a samjna sutra defines, its text and its
padaccheda (word, then vibhakti/vacana in Devanagari numerals; indeclinables 0/0). The data's
terms are its own README's: free to use with credit, which this module gives.
"""
import argparse
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOD = os.path.join(ROOT, "modules", "cls")
OUT = os.path.join(MOD, "data", "ashtadhyayi", "sutraani.tsv")
TYPES = {"V": "vidhi", "S": "samjna", "AT": "atidesha", "AD": "adhikara", "P": "paribhasha"}
DIGITS = "०१२३४५६७८९"
COLUMNS = ("id", "krama", "kaumudi", "type", "term", "type_name", "sutra", "padaccheda")


def sha(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def padaccheda(raw):
    """'वृद्धिः$S$1$1$##आत्-ऐच्$S$1$1$' -> 'वृद्धिः १/१ आत्-ऐच् १/१'. A word with no case is written bare."""
    out = []
    for part in (x for x in raw.split("##") if x):
        b = part.split("$") + ["", "", ""]
        word, vib, vac = b[0], b[2], b[3]
        if vib.isdigit() and vac.isdigit():
            out.append(f"{word} {''.join(DIGITS[int(c)] for c in vib)}/{''.join(DIGITS[int(c)] for c in vac)}")
        else:
            out.append(word)
    return " ".join(out)


def typed(raw):
    code, _, rest = (raw or "").partition("$")
    name = rest.split("$")[0]
    term = name[:-len("संज्ञा")] if code == "S" and name.endswith("संज्ञा") else ""
    if code not in TYPES:
        raise ValueError(f"unknown sutra type code {code!r}")
    return TYPES[code], term, name


def rows(data_txt):
    with open(data_txt, encoding="utf-8") as fh:
        data = json.load(fh)["data"]
    out = []
    for x in data:
        t, term, name = typed(x["type"])
        out.append({"id": f"{x['a']}.{x['p']}.{x['n']}", "krama": x["i"], "kaumudi": x.get("skn", ""),
                    "type": t, "term": term, "type_name": name, "sutra": x["s"], "padaccheda": padaccheda(x["pc"])})
    out.sort(key=lambda r: int(r["krama"]))
    return out


def tsv(rs):
    lines = ["\t".join(COLUMNS)] + ["\t".join(str(r[c]).replace("\t", " ") for c in COLUMNS) for r in rs]
    return "\n".join(lines) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("checkout")
    ap.add_argument("--check", action="store_true", help="refuse unless the tree's file is what this checkout yields")
    a = ap.parse_args(argv)
    src = os.path.join(a.checkout, "sutraani", "data.txt")
    with open(os.path.join(MOD, "data", "SOURCES.json"), encoding="utf-8") as fh:
        s = next(x for x in json.load(fh)["sources"] if x["id"] == "ashtadhyayi-com-data")
    if sha(src) != s["upstream_sha256"]:
        print(f"sutra_import: refused, {src} has sha256 {sha(src)}; the pin is {s['upstream_sha256']}")
        return 1
    text = tsv(rows(src))
    if a.check:
        ok = open(OUT, encoding="utf-8").read() == text
        print("sutra_import: the tree's sutraani.tsv is what the pinned source yields" if ok
              else "sutra_import: STALE, the tree's sutraani.tsv differs from the pinned source's")
        return 0 if ok else 1
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(text)
    print(f"sutra_import: {text.count(chr(10)) - 1} sutras written, sha256 {sha(OUT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
