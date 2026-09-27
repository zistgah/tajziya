# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""Classical Sanskrit, as a language module: the author's parser in vendor/sanskrit_parser.

This module adds no sandhi logic. It calls the upstream Segmenter and combine_vowels, records
each junction by rejoining the returned words with the upstream function, and refuses every
layer the upstream does not implement. The sutra text comes from an MIT-licensed edition
(vidyut-prakriya, 3,983 sutras in SLP1). The earlier compilation, whose terms restrict
reposting, is read only from a local copy that matches its pin.
"""
import hashlib
import importlib
import json
import os
import sys
import unicodedata

from tajziya import api

HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UPSTREAM = api.repo_path("vendor", "sanskrit_parser", "python")
RULE = "not established: the Adhyaya 6.1 sandhi sutras are not yet mapped to junctions (P-SAN-03)"


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


def _sha(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


class SanskritPort:
    REFERENCE_INPUT = {"L3s": "neti"}
    ACCEPTS = ("Latn",)

    def __init__(self, node, reg, module_dir=None, lexicon=None):
        self.node, self._n, self._reg = node["id"], node, reg
        self._dir = module_dir or HERE
        self._man = api.manifest(self._dir)
        self._u = _upstream()
        self._lexicon = set(lexicon) if lexicon is not None else set(self._u["lexicon"].TOY_LEXICON)
        self._seg = self._u["pipeline"].Segmenter([], self._lexicon)
        self._vowels = sorted(self._u["sandhi"].VOWELS, key=len, reverse=True)
        self.REFERENCE = api.reference(self._dir, "L3s")
        self.rules_provenance = ""

    def with_lexicon(self, lexicon):
        return SanskritPort(self._n, self._reg, self._dir, lexicon)

    def layers(self):
        return dict(self._man["layers"])

    def phonology(self, text):
        raise api.NotBuilt(self.node, "L0", "no phonological base is defined", ("P-L0-01",))

    def pivot(self, text):
        raise api.NotBuilt(self.node, "L1", "Devanagari to the segmenter's IAST form is not bound",
                           ("P-SAN-01",), ("abugida",))

    def orthography(self, text):
        return api.orthography(text, self._n, self._reg)

    def _junction(self, left, right):
        lv = next((v for v in self._vowels if left.endswith(v)), None)
        rv = next((v for v in self._vowels if right.startswith(v)), None)
        if not lv or not rv:
            return None
        try:
            merged = self._u["sandhi"].combine_vowels(lv, rv).combined
        except ValueError:
            return None
        return api.Junction(lv, rv, merged, RULE), left[:len(left) - len(lv)] + merged + right[len(rv):]

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
        counts, _ = api.detect_scripts(t, self._reg)
        other = sorted(set(counts) - set(self.ACCEPTS))
        if other:
            raise api.NotBuilt(self.node, "L1", f"input is in {', '.join(other)}; the segmenter reads IAST and "
                               "the script pivot is not bound", ("P-SAN-01",), ("abugida",))
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
                alts.append(api.Segmentation(words, tuple(junctions or ()), junctions is not None and acc == tok))
            lattices.append(api.TokenLattice(tok, tuple(alts)))
        return api.Result(self.node, "L3s", tuple(lattices),
                          {"engine": "vendor/sanskrit_parser Segmenter", "lexicon_size": len(self._lexicon),
                           "scope_excludes": list(self._man.get("scope_excludes", []))})

    def analyse(self, word):
        raise api.NotBuilt(self.node, "L3m", "morphology needs sourced vibhakti rules and a lexicon",
                           ("P-SAN-05",), ("paradigm",))

    def relate(self, tokens):
        raise api.NotBuilt(self.node, "L4", "karaka relations need the morphology beneath them", ("P-SAN-06",))

    def _source(self, sid):
        with open(os.path.join(self._dir, self._man["sources"]), encoding="utf-8") as fh:
            return next(s for s in json.load(fh)["sources"] if s["id"] == sid)

    def rules(self, source="open", data_path=None, pin=None):
        """The sutras: "open" is the MIT edition in data/; "local" is the restricted compilation, if held."""
        Sutra = self._u["rules"].Sutra
        if source == "open":
            s = self._source("vidyut-sutrapatha")
            f = s["files"][0]
            p = os.path.join(self._dir, f["path"])
            if _sha(p) != f["sha256"]:
                raise ValueError(f"refused: {f['path']} does not match its pin")
            out = []
            with open(p, encoding="utf-8") as fh:
                next(fh)
                for line in fh:
                    code, _, text = line.rstrip("\r\n").partition("\t")
                    if not code:
                        continue
                    a, pd, n = (int(x) for x in code.split("."))
                    out.append(Sutra(id=code, sutra_krama=a * 10000 + pd * 1000 + n, kaumudi_krama=None, type=None,
                                     term=None, sutra=text, padaccheda=None))
            self.rules_provenance = f"{s['scheme']}, {s['licence']}, from {s['id']}"
            return out
        s = self._source("sanskritdocuments-compilation")
        p = data_path or os.path.join(self._dir, s["files"][0]["path"])
        want = pin or s["files"][0]["sha256"]
        if not os.path.exists(p):
            return api.Unknown("the local compilation is not present; it is never redistributed", (p,))
        if _sha(p) != want:
            raise ValueError(f"refused: {p} has sha256 {_sha(p)}; the pin is {want}")
        self.rules_provenance = "Devanagari, local copy, not redistributed"
        return self._u["rules"].load_sutras(p)


def make(node, reg, module_dir=None, **options):
    return SanskritPort(node, reg, module_dir, **options)
