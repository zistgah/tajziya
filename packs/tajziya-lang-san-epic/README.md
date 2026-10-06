# Epic Sanskrit (`san-epic`): a tajziya language module

© 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.

This folder is a complete tajziya language module, handed over to be built. As handed over it
passes the generic acceptance test, because every layer refuses by name. The work is to build
layers one at a time and keep `bash accept.sh` passing.

## The node

| | |
|---|---|
| Registry id | `san-epic` |
| Language, stage | Sanskrit, Epic |
| Lineage | Indo-European > indo_iranian > Indo-Aryan |
| Morphological type | fusional |
| ISO 639-3 | san |
| Scripts (ISO 15924) | Deva (Devanagari (Nagari)) |
| Matrix status | P (provisional), poster I §5 |
| Corpus | Mahābhārata; Rāmāyaṇa; associated traditions. Do not delete the stage. |

One node of the Sanskrit stage tree (poster III, Axis II): Vedic, Epic, Classical, later. This node is the Epic stage.

## What to build

Six layers, the Project ILM linguistic stack. Each is one method in
`python/san_epic_v0/__init__.py`, and each refuses today.

| Layer | Method | Engines it needs | Packages |
|---|---|---|---|
| L0 | `phonology` | none named | P-L0-01, P-LIN-indo_aryan |
| L1 | `pivot` | abugida | P-ENG-09 |
| L2 | `orthography` | wired unproven through the common layer | none |
| L3s | `segment` | juncture, compounding, abugida | P-ENG-01, P-ENG-03, P-ENG-09, P-LIN-indo_aryan |
| L3m | `analyse` | paradigm, compounding | P-ENG-02, P-ENG-03, P-LIN-indo_aryan |
| L4 | `relate` | none named | P-L4-01, P-LIN-indo_aryan |

An engine that serves several lineages is built once, as its package in zistgah/tajziya
(`registry/engines.json`, `roadmap/packages.json`), and imported. It is not rebuilt inside this
module.

## How a layer becomes built

1. Take one coherent batch from a real, citable edition under an allowed licence, and list it
   in `data/SOURCES.json` with its URL, retrieval date, SHA-256 and licence.
2. Implement the layer in `python/san_epic_v0/__init__.py`, importing only `tajziya.api`.
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

- [UD_Sanskrit-UFAL](https://github.com/UniversalDependencies/UD_Sanskrit-UFAL): CC-BY-SA-4.0, allowed in the tree, genre fiction
- [UD_Sanskrit-Vedic](https://github.com/UniversalDependencies/UD_Sanskrit-Vedic): CC-BY-SA-4.0, allowed in the tree, genre nonfiction

## Done

`bash accept.sh` passes in isolation and in integration. The folder is handed back and becomes
`modules/san-epic` in zistgah/tajziya, bound in `registry/bindings.json`.
