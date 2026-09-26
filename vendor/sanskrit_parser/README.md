# Ashtadhyayi Rule Database — Sanskrit Parser Project

## Status

**152 of ~3,959 sutras** compiled, verified, and machine-readable:
Adhyaya 1 Pada 1 (all 75), Pada 2 (all 73), Pada 3 (first 4 of ~93).
`Segmenter` (`pipeline.py` / `pipeline.js`) now has real, working
vowel-sandhi logic (`sandhi.py` / `sandhi.js`) against a 12-word
placeholder lexicon (`lexicon.py` / `lexicon.js`) — `MorphAnalyzer` and
`KarakaParser` are still stubs, in both languages.

Every sutra entry is real, sourced text — nothing there is generated or
guessed. The sandhi logic is standard descriptive phonology, correct but
not yet cross-referenced to exact sutra numbers (see the sandhi module's
docstring in either language). Python and JS are kept behavior-identical —
see CONTRIBUTING.md.

## Why "~4,000" is approximate

The exact count depends on which traditional edition you follow:

| Edition / authority | Sutra count |
|---|---|
| Srisa Chandra Vasu (1891), following Jinendrabuddhi | 3,996 |
| Kashika-vritti (Jayaditya & Vamana, 7th c.) | 3,981 |
| Siddhanta Kaumudi (Bhattoji Dikshita, 17th c.) | 3,976 |

The spread comes down to editorial choices — e.g. whether the 14 Shiva Sutras
and the opening *atha śabdānuśāsanam* are counted as part of the numbered
text. "About 4,000" is the right way to describe it; no single number is
more "correct" than the others.

## Source

Sutra text, word-by-word grammatical parsing (*padaccheda*, with case and
number marked), and rule classification (*samjna* / *paribhasha* /
*atidesha*) come from the sortable Ashtadhyayi index compiled by Sai Susarla
at Sanskrit Documents, which cross-references the Kashika-vritti and
AVG-Sanskrit.org commentaries:

https://sanskritdocuments.org/learning_tools/ashtadhyayi/

Panini's sutras themselves are ~2,500 years old and firmly public domain.
This particular digital compilation is a modern scholarly aggregation of
them. The source site states that its texts are prepared by volunteers for
personal study and research, and are not to be copied or reposted without
permission. The compilation is therefore not redistributed in this
repository; data/SOURCE.json pins the exact bytes so a local copy can be
verified and used.

## Why not all ~3,959 rules yet

That index is a large sortable/paginated table. Only an initial slice of it
is server-rendered in the raw page — the rest loads via the page's own
client-side pagination script, which isn't reachable by a plain fetch.
Requesting more data per fetch doesn't help; the page genuinely only ships
this many rows before JavaScript takes over.

The same index is published in full as a spreadsheet, under the same terms:

- Excel: https://sanskritdocuments.org/learning_tools/ashtadhyayi/sutras.xlsx
- Google Sheets: https://docs.google.com/spreadsheet/ccc?key=0Aocnp1cX4xG8dGh5Q0JaX21WYTZ0MktsRVQ3NzVON0E


## Existing prior art worth knowing about

**vidyut-prakriya** (github.com/ambuda-org/vidyut, MIT licensed) is an
actively maintained, open-source Paninian word-derivation engine that
already implements roughly **2,000 of the ~4,000 sutras**, in Rust with
Python bindings, published academically (ISCLS 2024). It's built by people
who have been at exactly this problem for years.

That's not a reason not to build your own — depending on what you're
after (learning how the grammar works by implementing it yourself, a
different target language, a different architecture, sentence-level
parsing rather than word generation) a from-scratch build can make total
sense. But it's worth knowing it exists before deciding how much of this
to build versus build on top of.

## Full-sentence parsing: what already exists (worth reading first)

The chosen direction for this parser is full-sentence parsing — segmentation
+ morphology + karaka/syntax. Two things are worth knowing before building
much further:

**A complete, Panini-rule-based pipeline for exactly this already exists
and is live.** The Sanskrit Heritage Engine (Gérard Huet, INRIA) segments
Sanskrit text using the Ashtadhyayi's own sandhi rules against its lexicon,
and its output feeds directly into Prof. Amba Kulkarni's (University of
Hyderabad) karaka/dependency parser, "Samsaadhanii" — segmentation through
syntax, connected, free to use:
https://sanskrit.uohyd.ac.in/SKT/DICO/reader.html
It is actively maintained.

**Rule-based segmentation alone doesn't fully solve the problem.** A
Sanskrit phonetic string often has many grammatically valid splits — real
ambiguity, not a gap in implementation. Applying the ~281 documented sandhi
rules "forwards" to generate candidate splits is the easy part; picking the
one a human intended needs disambiguation that the Ashtadhyayi itself
doesn't supply. That's exactly why Ambuda's own vidyut-cheda (rule-based,
same family as vidyut-prakriya) is now marked experimental/likely-to-be-
removed, with its maintainers recommending a neural model ("Dharmamitra")
instead for real accuracy. This is an open, actively-researched problem
(see Krishnan & Kulkarni, "Sanskrit Segmentation Revisited"), not something
either of us is expected to fully solve as a side effect of encoding rules.

**What this means here:** none of the above makes building this pointless —
implementing Panini's system yourself is a different (and legitimate) goal
from "have any working Sanskrit parser," whether for learning how the
grammar actually works, a specific language/platform target, or wanting
first-principles control rather than a black box. This project is
proceeding on the assumption that a personal implementation is the actual
goal, using the existing tools above as reference and validation rather
than a replacement.

## Repository layout & running it

```
sanskrit-parser/
├── LICENSE            code license (MIT) + data-attribution pointer
├── CONTRIBUTING.md    batch/provenance workflow for adding rules
├── data/
│   └── sutras_1.1-1.3.json
├── python/            rules.py, sandhi.py, lexicon.py, pipeline.py
└── js/                same four modules, pure JS (ES modules), zero deps
```

Both implementations are kept behavior-identical — same rule data, same
sandhi logic, same test cases, verified to produce matching output.

**Python** (3.9+, no dependencies): `python3 python/pipeline.py`

**JavaScript** (Node 14+, no dependencies): `node js/pipeline.js`

Either one loads all 152 rules and runs the segmenter against the worked
examples in "Status" above.

## Data schema

`data/sutras_1.1-1.3.json` — a JSON array; each entry:

```json
{
  "id": "1.1.1",            // adhyaya.pada.sutra, traditional order
  "sutra_krama": 11001,      // sequential index, traditional order
  "kaumudi_krama": 16,       // position in Siddhanta Kaumudi (topical) order
  "type": "samjna",          // "samjna" | "paribhasha" | "atidesha" | null
  "term": "वृद्धिः",          // term defined, for samjna rules; else null
  "sutra": "वृद्धिरादैच् ।",   // the rule text, Devanagari
  "padaccheda": "वृद्धिः १/१ आदैच् १/१"  // word-by-word split w/ case+number
}
```

`python/rules.py` / `js/rules.js` — a `Sutra` type and a loader
(`load_sutras()`/`loadSutras()`, `by_id()`/`byId()`, `by_type()`/`byType()`).
Run `python3 python/rules.py` or `node js/rules.js` for a demo against the
real data.

## Next steps

**Decided:** the parser targets full sentence parsing — segmentation
(sandhi-viccheda) + morphology + karaka/syntax analysis. `pipeline.py` has
a three-stage skeleton (`Segmenter` → `MorphAnalyzer` → `KarakaParser`)
wired to the rule loader, with each stage stubbed out and documented with
exactly what it's blocked on.

1. **Finish rule ingestion** — priority order now that the direction is
   set: the ~281 sandhi rules (mostly Adhyaya 6, Pada 1, and Adhyaya 8)
   feed `Segmenter` directly; the karaka rules (Adhyaya 1.4, 2.3) feed
   `KarakaParser`. Both are behind the same pagination wall as the rest of
   the corpus — an uploaded spreadsheet (see above) is the fast path to
   all of it at once; continued scraping only ever reaches the same first
   152 rules.
2. **A lexicon.** Segmentation and morphology both need an inventory of
   attested roots (Dhatupatha, ~2,000 entries) and stems — Panini's rules
   validate/generate forms but don't provide the list of what's actually a
   word. vidyut's `kosha` component (mentioned above) is a ready-made
   option if you don't want to build one from scratch.
3. **Rule representation + conflict resolution.** Panini's own meta-rules
   (*para*, *vipratiṣedha*, *apavāda* vs. *utsarga*, and others drawn from
   the paribhasha rules already in this dataset) govern which rule fires
   when several apply to the same input — this is the real engine, and
   everything above depends on it.
4. **A disambiguation strategy for `Segmenter`**, once (1) exists — even a
   simple heuristic (fewest words, most common words) beats none, per the
   ambiguity issue described above.

## Contributing

Meant to be picked up in batches (by pada, or by rule-type), each one
sourced -> provenance-recorded -> cross-checked -> integrated -> tested.
See CONTRIBUTING.md for the full checklist, including keeping python/ and
js/ behavior-identical.

## License

Code (`python/`, `js/`): MIT — see LICENSE.

Data (`data/sutras_1.1-1.3.json`): Panini's sutras are ~2,500-year-old
public domain text; this specific compiled/cross-referenced index is
sourced from sanskritdocuments.org (compiled by Sai Susarla, cross-linking
Kashika-vritti and AVG-Sanskrit.org) — credit that source if you
redistribute this dataset. See "Source" above.
