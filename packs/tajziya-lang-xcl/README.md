# Armenian (`xcl`): a tajziya language module

© 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.

This folder is a complete tajziya language module, handed over to be built. As handed over it
passes the generic acceptance test, because every layer refuses by name. The work is to build
layers one at a time and keep `bash accept.sh` passing.

## The node

| | |
|---|---|
| Registry id | `xcl` |
| Language, stage | Armenian, not staged on the posters |
| Lineage | Indo-European > Armenian |
| Morphological type | fusional |
| ISO 639-3 | xcl, hye |
| Scripts (ISO 15924) | Armn (Armenian) |
| Matrix status | I (irreducible), poster I §11 |
| Corpus | Historiography; theology; literature; manuscript tradition. |

No note or held conflict names this node.

## What to build

Six layers, the Project ILM linguistic stack. Each is one method in
`python/xcl_v0/__init__.py`, and each refuses today.

| Layer | Method | Engines it needs | Packages |
|---|---|---|---|
| L0 | `phonology` | none named | P-L0-01, P-LIN-armenian |
| L1 | `pivot` | none named | P-L1-01 |
| L2 | `orthography` | wired unproven through the common layer | none |
| L3s | `segment` | none named | P-LIN-armenian |
| L3m | `analyse` | paradigm | P-ENG-02, P-LIN-armenian |
| L4 | `relate` | none named | P-L4-01, P-LIN-armenian |

An engine that serves several lineages is built once, as its package in zistgah/tajziya
(`registry/engines.json`, `roadmap/packages.json`), and imported. It is not rebuilt inside this
module.

## How a layer becomes built

1. Take one coherent batch from a real, citable edition under an allowed licence, and list it
   in `data/SOURCES.json` with its URL, retrieval date, SHA-256 and licence.
2. Implement the layer in `python/xcl_v0/__init__.py`, importing only `tajziya.api`.
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

- [UD_Classical_Armenian-CAVaL](https://github.com/UniversalDependencies/UD_Classical_Armenian-CAVaL): CC-BY-NC-SA-4.0, not allowed in the tree, genre bible, fiction
- [UD_Armenian-ArmTDP](https://github.com/UniversalDependencies/UD_Armenian-ArmTDP): CC-BY-SA-4.0, allowed in the tree, genre academic, blog, fiction, government, grammar-examples, legal, medical, news, nonfiction, reviews, social
- [UD_Armenian-BSUT](https://github.com/UniversalDependencies/UD_Armenian-BSUT): CC-BY-SA-4.0, allowed in the tree, genre blog, fiction, government, legal, news, nonfiction, web, wiki

## Done

`bash accept.sh` passes in isolation and in integration. The folder is handed back and becomes
`modules/xcl` in zistgah/tajziya, bound in `registry/bindings.json`.
