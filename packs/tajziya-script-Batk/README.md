# Batak (`Batk`): a tajziya script module

© 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.

This folder is a complete tajziya script module, handed over to be built. As handed over it
passes the generic acceptance test, because every layer it cannot yet do refuses by name. The
work is to build the layers and keep `bash accept.sh` passing.

## The script

| | |
|---|---|
| ISO 15924 | `Batk`, number 365 |
| Name | Batak |
| Unicode | encoded (property value alias Batak, version 6.0) |
| Status in the ILM registry | seeded (the project-ilm 3D explorer's data) |
| On the posters | no poster node uses it |

## What to build

Two layers, the script axis of the Project ILM stack. Each is one method in
`python/script_batk_v0/__init__.py`.

| Layer | Method | Engines it needs | Packages |
|---|---|---|---|
| L1 | `pivot` | none named | P-L1-01 |
| L2 | `orthography` | wired unproven through the common layer | none |

- **L1, the pivot:** a table taking this script to its hub and back. Brahmic scripts pivot to
  Devanagari through Romenagri's tables; any other script names its hub in `module.json`.
- **L2, orthography:** normalisation, grapheme clusters and detection for this script. While
  the script is encoded in Unicode this runs through the common layer and is wired but
  unproven; building it means the script's own rules, from the Unicode Character Database.

## How a layer becomes built

1. List each table in `data/SOURCES.json` with its URL, retrieval date, SHA-256 and licence.
   The Unicode Character Database is under the Unicode License v3, which needs its notice in
   `data/LICENSES/`.
2. Implement the layer, importing only `tajziya.api`.
3. Set its state in `module.json` and name in `scope_excludes` every loss the script forces.
4. Add round-trip examples to `reference/examples.json`, each citing its source.
5. Run `bash accept.sh`.

The steps are also an AAB painting in `quest/aab-painting.json`, which AAB's studio imports.
`ledger.py` keeps the configuration record of the work: every prompt, response, decision and
artifact version, hash-chained and private unless you choose to share it.

## Done

`bash accept.sh` passes in isolation and in integration. The folder is handed back and becomes
`modules/script-Batk` in zistgah/tajziya, bound in `registry/script_bindings.json`.
