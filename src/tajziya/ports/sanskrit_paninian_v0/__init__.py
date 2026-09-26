# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""Classical Sanskrit, through the author's parser in vendor/sanskrit_parser.

This port adds no sandhi logic. It calls the upstream Segmenter and combine_vowels, records
each junction by rejoining the returned words with the upstream function, and refuses every
layer the upstream does not implement. The sutra compilation is read only from a local copy
whose SHA-256 matches the pin in vendor/sanskrit_parser/data/SOURCE.json.
"""
import hashlib
import importlib
import json
import os
import sys
import unicodedata

from ... import scripts
from ..._vendor.unknown import Unknown
from ...registry import path
from ...types import Junction, NotBuilt, Result, Segmentation, TokenLattice

UPSTREAM = path("vendor", "sanskrit_parser", "python")
SOURCE = path("vendor", "sanskrit_parser", "data", "SOURCE.json")
RULE = "not established: the Adhyaya 6.1 sandhi sutras are not yet sourced (P-SAN-03)"


def _upstream():
    names = ("rules", "sandhi", "lexicon", "pipeline")
    sys.path.insert(0, UPSTREAM)
    try:
        mods = {n: importlib.import_module(n) for n in names}
    finally:
        sys.path.remove(UPSTREAM)
    for n, m in mods.items():
        where = os.path.dirname(os.path.abspath(getattr(m, "__file__", "") or ""))
        if where != UPSTREAM:
            raise ImportError(f"module name '{n}' resolved to {where}, not to the vendored parser")
    return mods


class SanskritPort:
    REFERENCE = {"neti": [("na", "iti")], "tatraiva": [("tatra", "eva")],
                 "gurūpadeśa": [("guru", "upadeśa")], "sīteva": [("sītā", "iva")]}
    REFERENCE_INPUT = {"L3s": "neti"}
    ACCEPTS = ("Latn",)

    def __init__(self, node, reg, lexicon=None):
        self.node, self._n, self._reg = node["id"], node, reg
        self._u = _upstream()
        self._lexicon = set(lexicon) if lexicon is not None else set(self._u["lexicon"].TOY_LEXICON)
        self._seg = self._u["pipeline"].Segmenter([], self._lexicon)
        self._vowels = sorted(self._u["sandhi"].VOWELS, key=len, reverse=True)

    def with_lexicon(self, lexicon):
        return SanskritPort(self._n, self._reg, lexicon)

    def layers(self):
        return dict(self._n["layers"])

    def phonology(self, text):
        raise NotBuilt(self.node, "L0", "no phonological base is defined", ("P-L0-01",))

    def pivot(self, text):
        raise NotBuilt(self.node, "L1", "Devanagari to the segmenter's IAST form is not bound",
                       ("P-SAN-01",), ("abugida",))

    def orthography(self, text):
        return scripts.orthography(text, self._n, self._reg)

    def _junction(self, left, right):
        lv = next((v for v in self._vowels if left.endswith(v)), None)
        rv = next((v for v in self._vowels if right.startswith(v)), None)
        if not lv or not rv:
            return None
        try:
            merged = self._u["sandhi"].combine_vowels(lv, rv).combined
        except ValueError:
            return None
        return Junction(lv, rv, merged, RULE), left[:len(left) - len(lv)] + merged + right[len(rv):]

    def join(self, words):
        acc = unicodedata.normalize("NFC", words[0])
        for w in words[1:]:
            j = self._junction(acc, unicodedata.normalize("NFC", w))
            if j is None:
                return None
            acc = j[1]
        return acc

    def segment(self, text):
        t = unicodedata.normalize("NFC", text).strip()
        counts, _ = scripts.detect(t, self._reg)
        other = sorted(set(counts) - set(self.ACCEPTS))
        if other:
            raise NotBuilt(self.node, "L1", f"input is in {', '.join(other)}; the segmenter reads "
                           "IAST and the script pivot is not bound", ("P-SAN-01",), ("abugida",))
        lattices = []
        for tok in t.split():
            alts = []
            for cands in self._seg.segment(tok):
                words = tuple(c.text for c in cands)
                junctions, acc = [], words[0]
                for w in words[1:]:
                    j = self._junction(acc, w)
                    if j is None:
                        junctions = None
                        break
                    junctions.append(j[0])
                    acc = j[1]
                alts.append(Segmentation(words, tuple(junctions or ()),
                                         junctions is not None and acc == tok))
            lattices.append(TokenLattice(tok, tuple(alts)))
        return Result(self.node, "L3s", tuple(lattices),
                      {"engine": "vendor/sanskrit_parser Segmenter", "lexicon_size": len(self._lexicon),
                       "scope_excludes": list(self._n.get("scope_excludes", []))})

    def analyse(self, word):
        raise NotBuilt(self.node, "L3m", "morphology needs sourced vibhakti rules and a lexicon",
                       ("P-SAN-05",), ("paradigm",))

    def relate(self, tokens):
        raise NotBuilt(self.node, "L4", "karaka relations need the morphology beneath them", ("P-SAN-06",))

    def rules(self, data_path=None, pin=None):
        with open(SOURCE, encoding="utf-8") as fh:
            src = json.load(fh)
        p = data_path or path(*src["local_path"].split("/"))
        want = pin or src["sha256"]
        if not os.path.exists(p):
            return Unknown("the sutra compilation is not present locally; it is not redistributed", (p,))
        with open(p, "rb") as fh:
            got = hashlib.sha256(fh.read()).hexdigest()
        if got != want:
            raise ValueError(f"refused: {p} has sha256 {got}; the pin is {want}")
        return self._u["rules"].load_sutras(p)


def make(node, reg, **options):
    return SanskritPort(node, reg, **options)
