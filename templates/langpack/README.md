# @@NAME@@ (`@@NODE@@`): a tajziya language module

© 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.

This folder is a complete tajziya language module, handed over to be built. As handed over it
passes the generic acceptance test, because every layer refuses by name. The work is to build
layers one at a time and keep `bash accept.sh` passing.

## The node

| | |
|---|---|
| Registry id | `@@NODE@@` |
| Language, stage | @@LANGUAGE@@, @@STAGE@@ |
| Lineage | @@PATH@@ |
| Morphological type | @@MTYPE@@ |
| ISO 639-3 | @@ISO@@ |
| Scripts (ISO 15924) | @@SCRIPTS@@ |
| Matrix status | @@STATUS@@ (@@STATUS_NAME@@), @@STATUS_SOURCE@@ |
| Corpus | @@CORPUS@@ |

@@NOTES@@

## What to build

Six layers, the Project ILM linguistic stack. Each is one method in
`python/@@IMPL@@/__init__.py`, and each refuses today.

| Layer | Method | Engines it needs | Packages |
|---|---|---|---|
@@LAYER_TABLE@@

An engine that serves several lineages is built once, as its package in zistgah/tajziya
(`registry/engines.json`, `roadmap/packages.json`), and imported. It is not rebuilt inside this
module.

## How a layer becomes built

1. Take one coherent batch from a real, citable edition under an allowed licence, and list it
   in `data/SOURCES.json` with its URL, retrieval date, SHA-256 and licence.
2. Implement the layer in `python/@@IMPL@@/__init__.py`, importing only `tajziya.api`.
3. Set the layer's state in `module.json`, and name in `scope_excludes` what it leaves out.
4. Add attested examples to `reference/examples.json`, each citing its source and a locator.
   For segmentation, give every reading the source admits.
5. Run `bash accept.sh`.

`cyclers/@@NODE@@.pni` carries the same steps as a PANINI cycler for any model to run.

## Sources and licences

Only material under a licence in zistgah/tajziya's `registry/licences.json` enters this folder.
Material whose terms restrict reposting, commercial use or derivatives stays in `data/local/`,
pinned by SHA-256 and never committed; where an openly licensed alternative exists, it is used
instead.

Treebanks matched to this node's language codes in Universal Dependencies (stage fit not
established):

@@CORPORA@@

## Done

`bash accept.sh` passes in isolation and in integration. The folder is handed back and becomes
`modules/@@NODE@@` in zistgah/tajziya, bound in `registry/bindings.json`.
