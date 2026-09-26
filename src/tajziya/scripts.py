# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""L2, common to every node: normalise to NFC, then report which scripts the text is in.

Script evidence comes from Unicode character names matched against the prefixes each script
declares in registry/scripts.json. Unencoded scripts declare none, so their text cannot be
attributed here and their nodes carry L2 as not_built.
"""
import unicodedata


def _table(reg):
    rows = [(p, s["code"]) for s in reg.scripts.values() for p in s["unicode_name_prefixes"]]
    return sorted(rows, key=lambda r: -len(r[0]))


def detect(text, reg):
    """(counts per ISO 15924 code, letters and marks that could not be attributed)."""
    table, counts, unattributed = _table(reg), {}, 0
    for ch in unicodedata.normalize("NFC", text):
        cat = unicodedata.category(ch)
        if not (cat.startswith("L") or cat.startswith("M")):
            continue
        name = unicodedata.name(ch, "")
        if name.startswith("COMBINING "):
            continue
        code = next((c for p, c in table if name.startswith(p)), None)
        if code is None:
            unattributed += 1
        else:
            counts[code] = counts.get(code, 0) + 1
    return counts, unattributed


def orthography(text, node, reg):
    nfc = unicodedata.normalize("NFC", text)
    counts, unattributed = detect(nfc, reg)
    undeclared = sorted(set(counts) - set(node["scripts"]))
    return {"node": node["id"], "layer": "L2", "nfc": nfc, "changed_by_nfc": nfc != text,
            "scripts": counts, "unattributed": unattributed, "declared": list(node["scripts"]),
            "undeclared": undeclared, "consistent": not undeclared}
