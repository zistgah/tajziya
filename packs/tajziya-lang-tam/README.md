# Tamil (`tam`): a tajziya language module

© 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.

This folder is a complete tajziya language module, handed over to be built. As handed over it
passes the generic acceptance test, because every layer refuses by name. The work is to build
layers one at a time and keep `bash accept.sh` passing.

## The node

| | |
|---|---|
| Registry id | `tam` |
| Language, stage | Tamil, not staged on the posters |
| Lineage | Dravidian |
| Morphological type | agglutinative |
| ISO 639-3 | tam, oty |
| Scripts (ISO 15924) | Taml (Tamil), Brah (Brahmi) |
| Matrix status | I (irreducible), poster I §6 |
| Corpus | Sangam literature; classical poetry; grammar; ethics; devotional literature; inscriptions; scientific and religious traditions. |

Its stage tree (poster III, Axis II): Old, Classical/Medieval, Modern.

## What to build

Six layers, the Project ILM linguistic stack. Each is one method in
`python/tam_v0/__init__.py`, and each refuses today.

| Layer | Method | Engines it needs | Packages |
|---|---|---|---|
| L0 | `phonology` | none named | P-L0-01, P-LIN-dravidian |
| L1 | `pivot` | abugida | P-ENG-09 |
| L2 | `orthography` | wired unproven through the common layer | none |
| L3s | `segment` | juncture, abugida, unspaced | P-ENG-01, P-ENG-09, P-ENG-10, P-LIN-dravidian |
| L3m | `analyse` | affix_chain | P-ENG-05, P-LIN-dravidian |
| L4 | `relate` | none named | P-L4-01, P-LIN-dravidian |

An engine that serves several lineages is built once, as its package in zistgah/tajziya
(`registry/engines.json`, `roadmap/packages.json`), and imported. It is not rebuilt inside this
module.

## How a layer becomes built

1. Take one coherent batch from a real, citable edition under an allowed licence, and list it
   in `data/SOURCES.json` with its URL, retrieval date, SHA-256 and licence.
2. Implement the layer in `python/tam_v0/__init__.py`, importing only `tajziya.api`.
3. Set the layer's state in `module.json`, and name in `scope_excludes` what it leaves out.
4. Add attested examples to `reference/examples.json`, each citing its source and a locator.
   For segmentation, give every reading the source admits.
5. Run `bash accept.sh`.

`quest/aab-painting.json` is this package as an AAB painting. Import it at
https://zistgah.org/aab/ and work through the eight VGC quests there; every gate in it names its
oracle. `quest/QUEST.md` maps the quests onto this package.

`ledger.py` keeps step 3 of every cycle, the configuration record: `python3 ledger.py add prompt
--text "..."`, `add response --actor "<the AI you used>" --text "..."`, `add decision --text
"..."`, `add artifact --file <path>`. `python3 ledger.py verify` checks the chain, and acceptance
check A7 checks it again. Hand the record back with the package.

## Sources and licences

Only material under a licence in zistgah/tajziya's `registry/licences.json` enters this folder.
Material whose terms restrict reposting, commercial use or derivatives stays in `data/local/`,
pinned by SHA-256 and never committed; where an openly licensed alternative exists, it is used
instead.

Treebanks matched to this node's language codes in Universal Dependencies (stage fit not
established):

- [UD_Tamil-MWTT](https://github.com/UniversalDependencies/UD_Tamil-MWTT): CC-BY-SA-4.0, allowed in the tree, genre news
- [UD_Tamil-TTB](https://github.com/UniversalDependencies/UD_Tamil-TTB): CC-BY-NC-SA-3.0, not allowed in the tree, genre news

## Done

`bash accept.sh` passes in isolation and in integration. The folder is handed back and becomes
`modules/tam` in zistgah/tajziya, bound in `registry/bindings.json`.
