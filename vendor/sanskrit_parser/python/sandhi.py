# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: MIT
"""
Vowel sandhi (svarasandhi): combination and reverse-lookup.

Scope: only the patterns needed to join or split two adjacent vowels across
a word boundary. This is standard, well-established descriptive Sanskrit
phonology -- safe to implement directly, unlike the enumerated sutra corpus
itself, which needs to come from a sourced text (see README.md). The `sutra`
field on SandhiResult is a placeholder: once the actual Adhyaya 6/8 rules are
sourced, each branch below should cite the specific sutra it implements,
rather than being described only in prose as it is now.

NOT covered here: consonant sandhi, visarga sandhi, or junctions spanning
more than two adjacent vowels. Those are separate, real rule sets (also in
Adhyaya 6 and 8) and belong in their own modules, built the same way.
"""

import unicodedata
from dataclasses import dataclass
from typing import Optional


def _nfc(s: str) -> str:
    """Normalize to precomposed Unicode so diacritics behave as single
    characters for indexing/slicing -- IAST vowels like 'ū' must not
    silently be two codepoints (base + combining macron)."""
    return unicodedata.normalize("NFC", s)


VOWELS = [_nfc(v) for v in
          ["a", "ā", "i", "ī", "u", "ū", "ṛ", "ṝ", "ḷ", "e", "ai", "o", "au"]]

SHORT_LONG = {_nfc(k): _nfc(v) for k, v in
              {"a": "ā", "i": "ī", "u": "ū", "ṛ": "ṝ"}.items()}
LONG_SHORT = {v: k for k, v in SHORT_LONG.items()}

GUNA_OF = {_nfc(k): _nfc(v) for k, v in
           {"i": "e", "ī": "e", "u": "o", "ū": "o", "ṛ": "ar", "ḷ": "al"}.items()}
VRDDHI_OF = {_nfc(k): _nfc(v) for k, v in
             {"i": "ai", "ī": "ai", "u": "au", "ū": "au", "e": "ai", "o": "au"}.items()}
YAN = {_nfc(k): v for k, v in
       {"i": "y", "ī": "y", "u": "v", "ū": "v", "ṛ": "r"}.items()}

A_LIKE = {_nfc("a"), _nfc("ā")}


@dataclass
class SandhiResult:
    combined: str
    sutra: Optional[str] = None  # TODO: fill in once Adhyaya 6/8 are sourced


def combine_vowels(left_final: str, right_initial: str) -> SandhiResult:
    """Combine two adjacent vowels across a word boundary."""
    left_final, right_initial = _nfc(left_final), _nfc(right_initial)

    # 1. savarna dirgha: identical vowel, short or long -> long
    l_short = LONG_SHORT.get(left_final, left_final)
    r_short = LONG_SHORT.get(right_initial, right_initial)
    if l_short == r_short and l_short in SHORT_LONG:
        return SandhiResult(SHORT_LONG[l_short])

    # 2. a/a-macron + i/i-macron/u/u-macron/vocalic-r/vocalic-l -> guna
    if left_final in A_LIKE and right_initial in GUNA_OF:
        return SandhiResult(GUNA_OF[right_initial])

    # 3. a/a-macron + e/o -> vrddhi (only reached when right isn't already
    #    caught by guna above, i.e. right_initial in {e, o})
    if left_final in A_LIKE and right_initial in VRDDHI_OF:
        return SandhiResult(VRDDHI_OF[right_initial])

    # 4. i/u/vocalic-r (long or short) + a dissimilar vowel -> semivowel + vowel
    if left_final in YAN and right_initial != left_final:
        return SandhiResult(YAN[left_final] + right_initial)

    # 5. e/o + a -> e/o with the a elided (avagraha in Devanagari; "'" here)
    if left_final in {_nfc("e"), _nfc("o")} and right_initial == _nfc("a"):
        return SandhiResult(left_final + "'")

    # 6. ai/au + any vowel -> a-macron-y / a-macron-v + that vowel
    if left_final == _nfc("ai"):
        return SandhiResult(_nfc("āy") + right_initial)
    if left_final == _nfc("au"):
        return SandhiResult(_nfc("āv") + right_initial)

    raise ValueError(f"No rule covers {left_final!r} + {right_initial!r}")


def _build_reverse_index():
    index: dict[str, list[tuple[str, str]]] = {}
    for l in VOWELS:
        for r in VOWELS:
            try:
                merged = combine_vowels(l, r).combined
            except ValueError:
                continue
            index.setdefault(merged, []).append((l, r))
    return index


REVERSE_INDEX = _build_reverse_index()


def possible_splits(merged: str) -> list[tuple[str, str]]:
    """Every (left, right) vowel pair whose combination could have produced
    `merged` -- i.e. reverse combine_vowels(). Usually more than one
    possibility: sandhi is not uniquely invertible without a lexicon, which
    is exactly the segmentation-ambiguity issue described in README.md."""
    return REVERSE_INDEX.get(_nfc(merged), [])


if __name__ == "__main__":
    examples = [
        ("a", "i", "e"),     # na + iti -> neti
        ("a", "e", "ai"),    # tatra + eva -> tatraiva
        ("u", "u", "ū"),     # guru + upadesha -> gurupadesha
        ("ā", "i", "e"),     # sita + iva -> siteva
    ]
    print("Forward (combine):")
    for l, r, expected in examples:
        result = combine_vowels(l, r)
        status = "OK" if result.combined == _nfc(expected) else f"MISMATCH (got {result.combined!r})"
        print(f"  {l} + {r} -> {result.combined}  [{status}]")

    print("\nReverse (segment): what could a bare 'e' junction have come from?")
    for pair in possible_splits("e"):
        print(f"  {pair[0]} + {pair[1]}")
    print("(this is the ambiguity itself -- 4 grammatically valid answers, not 1)")
