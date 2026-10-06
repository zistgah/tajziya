# English (`eng`): a tajziya language module

© 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.

This folder is a complete tajziya language module, handed over to be built. As handed over it
passes the generic acceptance test, because every layer refuses by name. The work is to build
layers one at a time and keep `bash accept.sh` passing.

## The node

| | |
|---|---|
| Registry id | `eng` |
| Language, stage | English, not staged on the posters |
| Lineage | Indo-European > Germanic |
| Morphological type | fusional |
| ISO 639-3 | eng |
| Scripts (ISO 15924) | Latn (Latin) |
| Matrix status | I (irreducible), poster I §18 |
| Corpus | Modern science; philosophy; political theory; economics; literature. |

Its stage tree (poster III, Axis II): Old, Middle, Early Modern, Modern.

## What to build

Six layers, the Project ILM linguistic stack. Each is one method in
`python/eng_v0/__init__.py`, and each refuses today.

| Layer | Method | Engines it needs | Packages |
|---|---|---|---|
| L0 | `phonology` | none named | P-L0-01, P-LIN-germanic |
| L1 | `pivot` | none named | P-L1-01 |
| L2 | `orthography` | wired unproven through the common layer | none |
| L3s | `segment` | compounding | P-ENG-03, P-LIN-germanic |
| L3m | `analyse` | paradigm, compounding | P-ENG-02, P-ENG-03, P-LIN-germanic |
| L4 | `relate` | none named | P-L4-01, P-LIN-germanic |

An engine that serves several lineages is built once, as its package in zistgah/tajziya
(`registry/engines.json`, `roadmap/packages.json`), and imported. It is not rebuilt inside this
module.

## How a layer becomes built

1. Take one coherent batch from a real, citable edition under an allowed licence, and list it
   in `data/SOURCES.json` with its URL, retrieval date, SHA-256 and licence.
2. Implement the layer in `python/eng_v0/__init__.py`, importing only `tajziya.api`.
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

- [UD_English-Atis](https://github.com/UniversalDependencies/UD_English-Atis): CC-BY-SA-4.0, allowed in the tree, genre spoken
- [UD_English-CHILDES](https://github.com/UniversalDependencies/UD_English-CHILDES): CC-BY-SA-4.0, allowed in the tree, genre spoken
- [UD_English-CTeTex](https://github.com/UniversalDependencies/UD_English-CTeTex): CC-BY-SA-4.0, allowed in the tree, genre nonfiction
- [UD_English-ESL](https://github.com/UniversalDependencies/UD_English-ESL): CC-BY-SA-4.0, allowed in the tree; its text is not included and has its own terms, genre learner-essays
- [UD_English-ESLSpok](https://github.com/UniversalDependencies/UD_English-ESLSpok): CC-BY-SA-4.0, allowed in the tree, genre spoken
- [UD_English-EWT](https://github.com/UniversalDependencies/UD_English-EWT): CC-BY-SA-4.0, allowed in the tree, genre blog, social, reviews, email, web
- [UD_English-GENTLE](https://github.com/UniversalDependencies/UD_English-GENTLE): CC-BY-NC-SA-4.0, not allowed in the tree, genre academic, grammar-examples, legal, medical, nonfiction, poetry, social, spoken
- [UD_English-GUM](https://github.com/UniversalDependencies/UD_English-GUM): CC-BY-NC-SA-4.0, not allowed in the tree, genre academic, blog, email, fiction, government, legal, news, nonfiction, social, spoken, web, wiki
- [UD_English-GUMReddit](https://github.com/UniversalDependencies/UD_English-GUMReddit): CC-BY-4.0, allowed in the tree; its text is not included and has its own terms, genre blog, social
- [UD_English-LinES](https://github.com/UniversalDependencies/UD_English-LinES): CC-BY-NC-SA-4.0, not allowed in the tree, genre fiction, nonfiction, spoken
- [UD_English-LittlePrince](https://github.com/UniversalDependencies/UD_English-LittlePrince): CC-BY-SA-4.0, allowed in the tree, genre fiction
- [UD_English-ParTUT](https://github.com/UniversalDependencies/UD_English-ParTUT): CC-BY-NC-SA-4.0, not allowed in the tree, genre legal, news, wiki
- [UD_English-Pronouns](https://github.com/UniversalDependencies/UD_English-Pronouns): CC-BY-SA-4.0, allowed in the tree, genre grammar-examples
- [UD_English-PUD](https://github.com/UniversalDependencies/UD_English-PUD): CC-BY-SA-3.0, allowed in the tree, genre news, wiki

## Done

`bash accept.sh` passes in isolation and in integration. The folder is handed back and becomes
`modules/eng` in zistgah/tajziya, bound in `registry/bindings.json`.
