# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: MIT
"""
Pipeline skeleton for full-sentence Sanskrit parsing.

Three stages, matching the three real subproblems (see README.md):
  1. Segmenter      -- splits a sandhi'd phonetic stream into candidate words
  2. MorphAnalyzer  -- tags each candidate word with its grammatical structure
  3. KarakaParser   -- assigns karaka/dependency relations between words

Segmenter now does real vowel-sandhi reversal against a lexicon (see
sandhi.py, lexicon.py) -- MorphAnalyzer and KarakaParser are still stubs.
The rule data in data/sutras_1.1-1.3.json covers only the samjna/paribhasha/
atidesha rules of Adhyaya 1, Pada 1-3 so far -- the sandhi rules Segmenter's
vowel logic should eventually cite (~281 of them, mostly Adhyaya 6 Pada 1
and Adhyaya 8) and the karaka rules KarakaParser needs (Adhyaya 1.4, 2.3)
aren't sourced yet. See README.md's "Next steps" and its note on existing
systems (Sanskrit Heritage Engine + Samsaadhanii) before reimplementing too
much of this from scratch.
"""

from dataclasses import dataclass, field
from typing import Optional

from rules import Sutra, load_sutras


@dataclass
class Candidate:
    """One candidate word produced by segmentation, before morphological
    analysis has confirmed it's actually valid."""
    text: str   # the candidate word, as split out of the input
    start: int  # character offset of this candidate in the original input
    end: int


@dataclass
class Token:
    """A word after morphological analysis."""
    surface: str                              # the word as it appears (post-sandhi)
    lemma: Optional[str] = None               # dictionary form / root
    features: dict = field(default_factory=dict)  # case, number, tense, etc.


@dataclass
class KarakaRelation:
    """A syntactic/semantic relation between two analyzed tokens."""
    head: Token
    dependent: Token
    relation: str  # e.g. "karta" (agent), "karma" (object), "karana" (instrument)


class Segmenter:
    """Stage 1: split a continuous Sanskrit string into candidate words.

    IMPLEMENTED (partially): vowel-sandhi reversal against a lexicon, via
    sandhi.py + lexicon.py. This covers exactly one class of junction --
    two adjacent vowels merging into one -- and only knows words that are
    in the (tiny, placeholder) lexicon. NOT implemented: consonant sandhi,
    visarga sandhi, compounds, or anything beyond a toy word list. Real
    input is usually ambiguous: segment() returns every solution it finds,
    not one -- ranking/picking the intended one is a separate concern
    (see README's note on segmentation ambiguity) not yet addressed.
    """

    def __init__(self, sutras: list[Sutra], lexicon: Optional[set] = None):
        self.sutras = sutras
        if lexicon is None:
            from lexicon import TOY_LEXICON
            lexicon = TOY_LEXICON
        self.lexicon = lexicon

    def segment(self, text: str) -> list[list[Candidate]]:
        """Return every segmentation of `text` into lexicon words that's
        reachable by undoing zero or one vowel-sandhi merge per boundary."""
        word_sequences = self._segment_words(text)
        results = []
        for words in word_sequences:
            candidates = []
            pos = 0
            for w in words:
                candidates.append(Candidate(text=w, start=pos, end=pos + len(w)))
                pos += len(w)  # approximate: post-sandhi text is usually
                               # shorter than the sum of the original words
            results.append(candidates)
        return results

    def _segment_words(self, text: str) -> list[list[str]]:
        """Core recursion: every way to split `text` into lexicon words,
        undoing sandhi.REVERSE_INDEX junctions where needed."""
        from sandhi import REVERSE_INDEX

        results = []
        if text in self.lexicon:
            results.append([text])

        for junction, pairs in REVERSE_INDEX.items():
            start = text.find(junction)
            while start != -1:
                for left_v, right_v in pairs:
                    left = text[:start] + left_v
                    right = right_v + text[start + len(junction):]
                    if left in self.lexicon:
                        for rest in self._segment_words(right):
                            results.append([left] + rest)
                start = text.find(junction, start + 1)

        seen, unique = set(), []
        for r in results:
            key = tuple(r)
            if key not in seen:
                seen.add(key)
                unique.append(r)
        return unique


class MorphAnalyzer:
    """Stage 2: tag each segmented word with its grammatical structure."""

    def __init__(self, sutras: list[Sutra]):
        self.sutras = sutras

    def analyze(self, candidate: Candidate) -> list[Token]:
        """Return every valid morphological analysis of one candidate word
        (a single surface form can genuinely be ambiguous -- e.g. one
        spelling can be several different case forms at once)."""
        raise NotImplementedError(
            "MorphAnalyzer needs the karaka/vibhakti rules and a lexicon -- "
            "see README.md next steps."
        )


class KarakaParser:
    """Stage 3: assign karaka (syntactic/semantic) relations between the
    analyzed words of a sentence, per Panini's karaka theory (Adhyaya 1.4,
    2.3)."""

    def __init__(self, sutras: list[Sutra]):
        self.sutras = sutras

    def parse(self, tokens: list[Token]) -> list[KarakaRelation]:
        raise NotImplementedError(
            "KarakaParser needs the Adhyaya 1.4 / 2.3 karaka rules -- "
            "see README.md next steps."
        )


class SanskritParser:
    """Top-level pipeline: text in, karaka-annotated parse out."""

    def __init__(self, sutras: Optional[list[Sutra]] = None):
        self.sutras = sutras or load_sutras()
        self.segmenter = Segmenter(self.sutras)
        self.morph = MorphAnalyzer(self.sutras)
        self.karaka = KarakaParser(self.sutras)

    def parse(self, text: str):
        segmentations = self.segmenter.segment(text)
        # Once Segmenter/MorphAnalyzer/KarakaParser are real: pick or rank a
        # segmentation, run MorphAnalyzer over each candidate, then hand the
        # resulting tokens to KarakaParser.
        raise NotImplementedError


if __name__ == "__main__":
    parser = SanskritParser()
    print(f"Pipeline initialized with {len(parser.sutras)} rules loaded "
          f"({parser.sutras[0].id} - {parser.sutras[-1].id}).")

    print("\nSegmenter (real, limited) on known examples:")
    for text in ["neti", "tatraiva", "gurūpadeśa", "sīteva"]:
        solutions = parser.segmenter.segment(text)
        words = [[c.text for c in sol] for sol in solutions]
        print(f"  {text!r} -> {words}")

    print("\nMorphAnalyzer and KarakaParser are still stubs -- "
          "see README.md's Next steps for what unblocks each one.")
