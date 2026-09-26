# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: MIT
"""
Minimal loader for the Ashtadhyayi rule database.

This is the first piece of infrastructure for the Sanskrit parser project --
just enough to load and query the rules compiled so far. It intentionally
does NOT implement any derivation/analysis logic yet, since that depends on
which direction the parser takes (word generation? morphological analysis?
full sentence parsing? sandhi only?) -- see README.md.
"""

from dataclasses import dataclass
from pathlib import Path
import json
from typing import Optional


@dataclass
class Sutra:
    id: str                        # "1.1.1" (adhyaya.pada.sutra, traditional order)
    sutra_krama: int                # sequential index in traditional order, e.g. 11001
    kaumudi_krama: Optional[int]    # position in Siddhanta Kaumudi (topical) order
    type: Optional[str]             # "samjna" | "paribhasha" | "atidesha" | None
    term: Optional[str]             # term being defined, for samjna (naming) rules
    sutra: str                      # the rule text, Devanagari
    padaccheda: Optional[str]       # word-by-word grammatical split, Devanagari

    @property
    def adhyaya(self) -> int:
        return int(self.id.split(".")[0])

    @property
    def pada(self) -> int:
        return int(self.id.split(".")[1])

    @property
    def sutra_number(self) -> int:
        return int(self.id.split(".")[2])


DEFAULT_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "sutras_1.1-1.3.json"


def load_sutras(path: str = DEFAULT_DATA_PATH) -> list[Sutra]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return [Sutra(**entry) for entry in raw]


def by_id(sutras: list[Sutra], sutra_id: str) -> Optional[Sutra]:
    return next((s for s in sutras if s.id == sutra_id), None)


def by_type(sutras: list[Sutra], type_: str) -> list[Sutra]:
    return [s for s in sutras if s.type == type_]


if __name__ == "__main__":
    sutras = load_sutras()
    print(f"Loaded {len(sutras)} sutras ({sutras[0].id} - {sutras[-1].id}).")

    samjnas = by_type(sutras, "samjna")
    print(f"\n{len(samjnas)} are samjna (technical-term-defining) rules, e.g.:")
    for s in samjnas[:5]:
        print(f"  {s.id}  {s.term}  --  {s.sutra}")

    paribhashas = by_type(sutras, "paribhasha")
    print(f"\n{len(paribhashas)} are paribhasha (interpretive meta-)rules, e.g.:")
    for s in paribhashas[:3]:
        print(f"  {s.id}  --  {s.sutra}")
