# tajziya (تجزیہ)

Parsers for the classical languages of the human written corpus, grouped by family and built on
the dhancha spine.

© 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.

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

One node: Classical Sanskrit (`cls`), through the author's own parser in `vendor/sanskrit_parser`,
Python and JavaScript. It reverses vowel sandhi against a placeholder lexicon and returns every
admissible reading. Consonant and visarga sandhi, morphology and karaka relations are not built,
and the parser says so.

Every other node is a stub: bound to its family's frame, it normalises text and reports which
scripts it is written in, then refuses each further layer by name, listing the engines it needs
and the packages in `roadmap/packages.json` that would build them.

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
    make deps && make check                          also judges the spine and the cyclers
    PYTHONPATH=src python3 -m tajziya nodes
    PYTHONPATH=src python3 -m tajziya segment --node cls tatraiva
    PYTHONPATH=src python3 -m tajziya segment --node cls --conllu neti
    PYTHONPATH=src python3 -m tajziya layers --node akk
    PYTHONPATH=src python3 -m tajziya commonalities
    PYTHONPATH=src python3 -m tajziya eliminate

The sutra compilation the Sanskrit parser was built with is not redistributed here; see
`PROVENANCE.md`. A local copy whose hash matches the pin is used with
`PYTHONPATH=src python3 -m tajziya data import <archive or json>`, with the file placed inside
this repository's folder: nothing outside the folder a script runs in is read.

## Licences

Code GPL-3.0-or-later; the vendored parser MIT, as its author released it; documents CC-BY-SA-4.0;
registry and metadata CC0-1.0. Texts in `LICENSES/`.
