# Old Russian (`orv`): a tajziya language module

© 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.

This folder is a complete tajziya language module, handed over to be built. As handed over it
passes the generic acceptance test, because every layer refuses by name. The work is to build
layers one at a time and keep `bash accept.sh` passing.

## The node

| | |
|---|---|
| Registry id | `orv` |
| Language, stage | Old Russian, not staged |
| Lineage | not yet established; package P-PROF-01 establishes it from open sources |
| Morphological type | not yet established; package P-PROF-01 establishes it from open sources |
| ISO 639-3 | orv |
| Scripts (ISO 15924) | not yet established; package P-PROF-01 establishes it from open sources |
| Matrix status | coverage (in the ILM registry, not on the posters), ILM registry (project-ilm/ilm.codes): historical, individual, pending |
| Corpus | Not yet assessed. The ILM registry lists the language; its corpus is assessed once its profile is established (P-PROF-01). |

This language comes from the ILM registry, the data the project-ilm 3D explorer draws, not from the posters. Its profile (lineage, morphological type, scripts) is the first task, package P-PROF-01; until then only the layers that need no profile are described.

## What to build

Six layers, the Project ILM linguistic stack. Each is one method in
`python/orv_v0/__init__.py`, and each refuses today.

| Layer | Method | Engines it needs | Packages |
|---|---|---|---|
| L0 | `phonology` | none named | P-L0-01, P-PROF-01 |
| L1 | `pivot` | none named | P-L1-01 |
| L2 | `orthography` | wired unproven through the common layer | none |
| L3s | `segment` | none named | P-PROF-01 |
| L3m | `analyse` | none named | P-PROF-01 |
| L4 | `relate` | none named | P-L4-01, P-PROF-01 |

An engine that serves several lineages is built once, as its package in zistgah/tajziya
(`registry/engines.json`, `roadmap/packages.json`), and imported. It is not rebuilt inside this
module.

## How a layer becomes built

1. Take one coherent batch from a real, citable edition under an allowed licence, and list it
   in `data/SOURCES.json` with its URL, retrieval date, SHA-256 and licence.
2. Implement the layer in `python/orv_v0/__init__.py`, importing only `tajziya.api`.
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

None matched yet: Universal Dependencies was matched against the posters' nodes only.

## Done

`bash accept.sh` passes in isolation and in integration. The folder is handed back and becomes
`modules/orv` in zistgah/tajziya, bound in `registry/bindings.json`.
