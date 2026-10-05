#!/usr/bin/env python3
# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""Every sutra in Romenagri, and whether it comes back to the same Devanagari.

    python3 tools/romenagri_sutras.py [--check]

Writes modules/cls/data/romenagri/sutras.tsv: id, Romenagri form, and "same" or "differs" for the
round trip. Exit 3 when Romenagri cannot be built here; --check exits 1 when the file is stale.
"""
import os
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from tajziya import romenagri  # noqa: E402

SUTRAS = os.path.join(ROOT, "modules", "cls", "data", "ashtadhyayi", "sutraani.tsv")
OUT = os.path.join(ROOT, "modules", "cls", "data", "romenagri", "sutras.tsv")


def table():
    rows = [l.rstrip("\n").split("\t") for l in open(SUTRAS, encoding="utf-8")][1:]
    texts = [r[6] for r in rows]
    rom = romenagri.roman_lines(texts)
    back = romenagri.devanagari_lines(rom)
    nf = lambda s: unicodedata.normalize("NFC", s)
    lines = ["id\tromenagri\tround_trip"] + [f"{r[0]}\t{rom[i]}\t{'same' if nf(back[i]) == nf(texts[i]) else 'differs'}"
                                              for i, r in enumerate(rows)]
    return "\n".join(lines) + "\n"


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    why = romenagri.build()
    if why:
        print(f"romenagri_sutras: cannot judge, Romenagri is not built here ({why})")
        return 3
    text = table()
    if "--check" in argv:
        ok = os.path.exists(OUT) and open(OUT, encoding="utf-8").read() == text
        print("romenagri_sutras: current" if ok else "romenagri_sutras: STALE, regenerate it")
        return 0 if ok else 1
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write(text)
    same = text.count("\tsame\n")
    print(f"romenagri_sutras: {text.count(chr(10)) - 1} sutras, {same} come back the same")
    return 0


if __name__ == "__main__":
    sys.exit(main())
