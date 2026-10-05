# tajziya (تجزیہ)

DOI: [10.5281/zenodo.23155053](https://doi.org/10.5281/zenodo.23155053)

Parsers for the classical languages of the human written corpus, grouped by family and built on
the dhancha spine.

© 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.

## Where it sits

In the author's layering (27 Sep 2026) tajziya and ILM are the **front end**: the languages a
program or a prompt can arrive in, Sanskrit first. PANINI's own front ends and the PANINI language
are the **middleware**; the **realization backends**, Panini Q among them, are where programs meet
a substrate. In his three Acts this is Act I, AGI completeness, beside the cyclers and genie as its
agents and harnesses. The process work of building a language, a script module, a shared engine,
a source choice or a coverage record is designed and run in AAB, as the paintings in `quests/`.
Every term is in [GLOSSARY.md](GLOSSARY.md), with the nearest term in common use beside it.

## What it holds

The registry carries 79 language and stage nodes, transcribed from the author's candidate language
matrix: every row of poster I, sections 1 to 18, plus Elamite from section 19 and poster III.
A node is a language at a stage, in declared scripts, holding a declared corpus, and it carries the
poster's own status: irreducible, provisional, undeciphered, stage, or candidate for compression.
Where the posters disagree with themselves, the conflict is recorded in `registry/conflicts.json`
and held, not resolved.

Nodes sit in 21 lineages under genealogical families. Dravidian is a family, not a node. The two
undeciphered corpora, Indus and Proto-Elamite, are kept as corpus objects with no language assigned.

## What parses

One node: Classical Sanskrit (`cls`), the reference language module in `modules/cls`, running the author's own
parser in `vendor/sanskrit_parser`, Python and JavaScript. It reverses vowel sandhi against a placeholder lexicon and returns every
admissible reading. Consonant and visarga sandhi, morphology and karaka relations are not built,
and the parser says so.

Every other node is a stub: bound to its family's frame, it normalises text and reports which
scripts it is written in, then refuses each further layer by name, listing the engines it needs
and the packages in `roadmap/packages.json` that would build them.

## Language modules

Every language is added as a module: a folder in `modules/<node>/` with `module.json`, a port that
imports only `tajziya.api`, `data/SOURCES.json` naming the licence of every data file, and
`reference/examples.json` citing attested examples. One generic test judges any module:

    PYTHONPATH=src python3 -m tajziya accept modules/<node> --integration

`tools/langpack.py` turns any node, any ISO 639-3 code, or every remaining node into such a module,
handed over as a self-contained package that already passes that test because every layer refuses:

    PYTHONPATH=src python3 tools/langpack.py --remaining --tar --bundle
    PYTHONPATH=src python3 tools/langpack.py akk grc

Each package carries its own `accept.sh`, which clones this repository inside the package folder
and judges the package in isolation and in integration.

## The layers

Parsing follows the Project ILM linguistic layers: L0 phonology, L1 script pivot, L2 orthography,
L3 segmentation and morphology, L4 syntax. Output is CoNLL-U, with a multiword token for each
joined form.

## Commonalities

Families are genealogical. The engines that do the work are shared by phenomenon, and a node needs
the engines of its lineage and of its scripts. `python3 -m tajziya commonalities` computes which
engines recur across lineages; script mechanisms recur across unrelated families far more than
language mechanisms do.

## The minimum language set

`python3 -m tajziya eliminate` runs the matrix's rule, U_i = K_i minus Recover(K_not_i, R, X),
on the coverage recorded in `registry/coverage.json`. Translation is never counted as recovery.
With no coverage recorded, nothing is eliminated and nothing is certified.

## Running it

    make check                                       the gate: ops/verify.sh
    make deps && make check                          also judges the spine
    PYTHONPATH=src python3 -m tajziya nodes
    PYTHONPATH=src python3 -m tajziya segment --node cls tatraiva
    PYTHONPATH=src python3 -m tajziya segment --node cls --conllu neti
    PYTHONPATH=src python3 -m tajziya layers --node akk
    PYTHONPATH=src python3 -m tajziya commonalities
    PYTHONPATH=src python3 -m tajziya eliminate

All 3,983 sutras carry their type, defined term, padaccheda and Siddhanta Kaumudi number,
derived from the data that powers ashtadhyayi.com (free to use with credit; the credit is in
`modules/cls/data/LICENSES/`). Their text is cross-checked against vidyut-prakriya's MIT edition.
`docs/review.html` is the source review: every sutra, the flags, and an issue link for each.

## Every language and script the ILM explorer shows

The project-ilm 3D explorer draws its points from the ILM registry: 7,867 ISO 639-3 languages
and 226 ISO 15924 scripts. tajziya carries a pinned copy in `registry/ilm/`. The 79 poster nodes
keep their curated records; each of the 7,787 other languages is a coverage node, and each script
stands in a script frame, all refusing by name until a module is bound.

    python3 -m tajziya coverage                         counts and conformance
    python3 tools/langpack.py --everything --tar --bundle   8,091 packages, each accepted

## Licences

Code GPL-3.0-or-later; the vendored parser MIT, as its author released it; documents CC-BY-SA-4.0;
registry and metadata CC0-1.0, except `registry/ilm/`, the verbatim copy of project-ilm/ilm.codes's
registry, which keeps that repository's GPL-2.0. Texts in `LICENSES/`.
