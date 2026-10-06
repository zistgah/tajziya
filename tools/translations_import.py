#!/usr/bin/env python3
# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""Import the translations of the sutras from ashtadhyayi.com's data, deterministically.

    python3 tools/translations_import.py <checkout of github.com/ashtadhyayi-com/data>

Writes, under modules/cls/data/translation/:
  vasu.tsv            Srisa Chandra Vasu's English translation and notes (1891 to 1898), all 3,983
  english.tsv         the short English meaning, for the 838 sutras the data gives one
  sanskrit-artha.tsv  the Sanskrit meaning (artha) and its explanation, all 3,983
and pins each in modules/cls/data/SOURCES.json. Newlines are written as \\n and tabs as spaces;
only <i> survives of the source's markup. Each upstream file must match its pin.
"""
import ast
import hashlib
import json
import os
import re
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOD = os.path.join(ROOT, "modules", "cls")
OUT = os.path.join(MOD, "data", "translation")
COMMIT = "5744762f010d677cfb43f347a42d02796cf615d6"
TERMS = ("You are free to use this data in your own projects provided that appropriate credits are mentioned "
         "wherever applicable. (the repository's README)")
FILES = {
    "vasu": ("vasu_english.txt", "ashtadhyayi-com-vasu-english",
             "Srisa Chandra Vasu's English translation of the Ashtadhyayi, with his notes",
             "Vasu, Srisa Chandra (1861 to 1918), translator. The Ashtadhyayi of Panini. Allahabad: Indian Press, "
             "1891 to 1898 (books 4 to 8: Benares, Panini Office). HathiTrust record 100325742. Public domain by age; "
             "the transcription is ashtadhyayi.com's, used on its terms with credit."),
    "english": ("sutrartha_english.txt", "ashtadhyayi-com-sutrartha-english",
                "The short English meaning of the sutras, where ashtadhyayi.com's data gives one", None),
    "sanskrit-artha": ("sutrartha.txt", "ashtadhyayi-com-sutrartha",
                       "The Sanskrit meaning (artha) of each sutra and its explanation", None),
}


def sha(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def clean(text):
    text = re.sub(r"<(?!/?i>)[^>]*>", "", str(text))
    text = unicodedata.normalize("NFC", text.replace("\r", "").replace("\t", " ").strip())
    return text.replace("\\", "\\\\").replace("\n", "\\n")


def sid(key):
    k = str(key)
    return f"{int(k[0])}.{int(k[1])}.{int(k[2:])}" if k.isdigit() and len(k) >= 5 else None


def rows(slug, data):
    out = []
    for k, v in data.items():
        i = sid(k)
        if not i or not str(v).strip():
            continue
        if slug == "sanskrit-artha":
            d = ast.literal_eval(v) if isinstance(v, str) else v
            if not str(d.get("sa", "")).strip():
                continue
            out.append((i, clean(d.get("sa", "")), clean(d.get("sd", ""))))
        else:
            out.append((i, clean(v)))
    out.sort(key=lambda r: tuple(int(x) for x in r[0].split(".")))
    return out


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        print(__doc__); return 2
    src = os.path.join(argv[0], "sutraani")
    with open(os.path.join(MOD, "data", "SOURCES.json"), encoding="utf-8") as fh:
        doc = json.load(fh)
    pins = {s["id"]: s.get("upstream_sha256") for s in doc["sources"]}
    os.makedirs(OUT, exist_ok=True)
    for slug, (fname, source_id, title, citation) in FILES.items():
        up = os.path.join(src, fname)
        if pins.get(source_id) and pins[source_id] != sha(up):
            print(f"translations_import: refused, {fname} does not match its pin"); return 1
        with open(up, encoding="utf-8") as fh:
            data = json.load(fh)
        rs = rows(slug, data)
        cols = ["id", "text", "detail"] if slug == "sanskrit-artha" else ["id", "text"]
        path = os.path.join(OUT, f"{slug}.tsv")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("\t".join(cols) + "\n" + "".join("\t".join(r) + "\n" for r in rs))
        entry = {"id": source_id, "title": title, "url": f"https://github.com/ashtadhyayi-com/data/tree/{COMMIT}/sutraani",
                 "commit": COMMIT, "retrieved": "2026-10-06", "licence": "LicenseRef-ashtadhyayi-com",
                 "licence_file": "data/LICENSES/ashtadhyayi-com.txt", "terms": TERMS,
                 "attribution": "ashtadhyayi.com" + (f"; {citation}" if citation else ""),
                 "upstream_path": f"sutraani/{fname}", "upstream_sha256": sha(up), "derived_by": "tools/translations_import.py",
                 "entries": len(rs), "files": [{"path": f"data/translation/{slug}.tsv", "sha256": sha(path)}],
                 "local_only": False}
        if citation:
            entry["citation"] = citation
        doc["sources"] = [s for s in doc["sources"] if s["id"] != source_id] + [entry]
        print(f"translations_import: {slug}: {len(rs)} sutras")
    with open(os.path.join(MOD, "data", "SOURCES.json"), "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
