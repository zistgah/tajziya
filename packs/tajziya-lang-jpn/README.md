# Modern Japanese (`jpn`): a tajziya language module

© 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.

This folder is a complete tajziya language module, handed over to be built. As handed over it
passes the generic acceptance test, because every layer refuses by name. The work is to build
layers one at a time and keep `bash accept.sh` passing.

## The node

| | |
|---|---|
| Registry id | `jpn` |
| Language, stage | Japanese, Modern |
| Lineage | Japonic |
| Morphological type | agglutinative |
| ISO 639-3 | jpn |
| Scripts (ISO 15924) | Hani (Han (Hanzi, Kanji, Hanja)), Hira (Hiragana), Kana (Katakana) |
| Matrix status | I (irreducible), poster I §15 |
| Corpus | Modern literature and intellectual corpus. |

No note or held conflict names this node.

## What to build

Six layers, the Project ILM linguistic stack. Each is one method in
`python/jpn_v0/__init__.py`, and each refuses today.

| Layer | Method | Engines it needs | Packages |
|---|---|---|---|
| L0 | `phonology` | none named | P-L0-01, P-LIN-japonic |
| L1 | `pivot` | none named | P-L1-01 |
| L2 | `orthography` | wired unproven through the common layer | none |
| L3s | `segment` | logogram, unspaced, syllabary | P-ENG-06, P-ENG-10, P-ENG-07, P-LIN-japonic |
| L3m | `analyse` | affix_chain | P-ENG-05, P-LIN-japonic |
| L4 | `relate` | none named | P-L4-01, P-LIN-japonic |

An engine that serves several lineages is built once, as its package in zistgah/tajziya
(`registry/engines.json`, `roadmap/packages.json`), and imported. It is not rebuilt inside this
module.

## How a layer becomes built

1. Take one coherent batch from a real, citable edition under an allowed licence, and list it
   in `data/SOURCES.json` with its URL, retrieval date, SHA-256 and licence.
2. Implement the layer in `python/jpn_v0/__init__.py`, importing only `tajziya.api`.
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

- [UD_Japanese-BCCWJ](https://github.com/UniversalDependencies/UD_Japanese-BCCWJ): CC-BY-NC-SA-4.0, not allowed in the tree; its text is not included and has its own terms, genre news, nonfiction, fiction, blog, web
- [UD_Japanese-BCCWJLUW](https://github.com/UniversalDependencies/UD_Japanese-BCCWJLUW): CC-BY-NC-SA-4.0, not allowed in the tree; its text is not included and has its own terms, genre news, nonfiction, fiction, blog, web
- [UD_Japanese-GSD](https://github.com/UniversalDependencies/UD_Japanese-GSD): CC-BY-SA-4.0, allowed in the tree, genre news, blog
- [UD_Japanese-GSDLUW](https://github.com/UniversalDependencies/UD_Japanese-GSDLUW): CC-BY-SA-4.0, allowed in the tree, genre news, blog
- [UD_Japanese-PUD](https://github.com/UniversalDependencies/UD_Japanese-PUD): CC-BY-SA-3.0, allowed in the tree, genre news, wiki
- [UD_Japanese-PUDLUW](https://github.com/UniversalDependencies/UD_Japanese-PUDLUW): CC-BY-SA-3.0, allowed in the tree, genre news, wiki

## Done

`bash accept.sh` passes in isolation and in integration. The folder is handed back and becomes
`modules/jpn` in zistgah/tajziya, bound in `registry/bindings.json`.
