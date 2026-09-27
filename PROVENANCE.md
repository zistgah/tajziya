# Provenance

Where every input came from, what was changed, and what was withheld.

© 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.

## The Sanskrit parser

Supplied by the author on 26 Sep 2026 as three files:

- `sanskrit-parser.zip`: `f319e1c9cf4d1af2d057f0ebdc75494e2d580e2fac37a1cceb69b0b2c7c2b245`
- `sanskrit-parser-LICENSE.txt`: `2919ab8da22e7b84021e8757159f04553bd15f9f5afebd45546c9d1ceb53455f` (identical to the LICENSE inside the archive)
- `sanskrit-parser-CONTRIBUTING.md`: `8120b7712fe16797aa1ee0572e7f1065ac4319084b0239bf9a9ece2042a5bb0c` (identical to the CONTRIBUTING inside the archive)

The archive holds one commit, `97e0df5857e5bdd8c8ddf95c262f9613ad09a477`, dated 2026-09-25T03:32:42+00:00. Its author
identity is a placeholder (`Sanskrit Parser Contributors <noreply@example.invalid>`); the work is the author's, as its
LICENSE states. `tools/vendor_import.py` derives `vendor/sanskrit_parser` from the archive, refuses
any archive whose hash is not the pin in `UPSTREAM.json`, and applies each change on an exact
anchor that must occur once.

Changes:

- `LICENSE`: holder name misspelt; estate copyright line applied
- `js/sandhi.js`: module threw ReferenceError on `process` when evaluated in a browser
- `js/pipeline.js`: module threw ReferenceError on `process` when evaluated in a browser
- `js/rules.js`: module threw ReferenceError on `process` when evaluated in a browser
- `README.md`: a claim of free reuse contradicted by the source site's own stated terms
- `README.md`: conversational text addressed to a chat, not to a reader
- `README.md`: conversational text addressed to a chat, not to a reader
- `README.md`: an undated, unverifiable time-bound claim
- `README.md`: conversational text addressed to a chat, not to a reader
- `CONTRIBUTING.md`: minting a third party's compilation would contradict its stated terms
- every `.py` and `.js` file: the estate copyright line and `SPDX-License-Identifier: MIT` prepended

| File | Upstream SHA-256 | Vendored SHA-256 | |
|---|---|---|---|
| `README.md` | `c31c6c978ffb86c1` | `4486bb006d9d7fb1` | changed |
| `CONTRIBUTING.md` | `8120b7712fe16797` | `05b1bbb987306247` | changed |
| `LICENSE` | `2919ab8da22e7b84` | `2a46b3ed626743ae` | changed |
| `.gitignore` | `36fbdf7206a150d3` | `36fbdf7206a150d3` | identical |
| `python/rules.py` | `d09c0d6638f63618` | `745b57e668d03560` | changed |
| `python/sandhi.py` | `92a56280e501de4e` | `df546461fd899e29` | changed |
| `python/lexicon.py` | `4f1a39a438a66a08` | `bcd84959f44f8303` | changed |
| `python/pipeline.py` | `a515f18927222fe4` | `18603035238d7505` | changed |
| `js/rules.js` | `8fd849ad4df3dfa1` | `1ec7e89b62142bb3` | changed |
| `js/sandhi.js` | `763c7542e6be9b96` | `43fd084ffb0559d3` | changed |
| `js/lexicon.js` | `972a5cb4e9bc7f21` | `6e88d151b39cfe6c` | changed |
| `js/pipeline.js` | `c23788641efccb0e` | `5796c17cf04f4cbf` | changed |
| `js/package.json` | `341089ebc323d17e` | `341089ebc323d17e` | identical |

`__pycache__` directories inside the archive were not copied.

## Withheld

`data/sutras_1.1-1.3.json` (152 entries, 1.1.1 to 1.3.4), SHA-256 `6d952a605d026fb7313901de3898d4da62c93b7a454103c4faed36ca2da31c8d`.
Compiled by Sai Susarla, Sanskrit Documents, as stated in the upstream README, from https://sanskritdocuments.org/learning_tools/ashtadhyayi/. The source site states that its texts are volunteer-prepared, meant for personal study and research, and not to be reposted without permission. The upstream README's claim
that it was published for free reuse is not supported by those terms, so the file is neither
committed nor deposited. Pāṇini's sutras themselves are public domain; re-sourcing them from an
openly licensed edition, or permission, is package P-LEG-01. A local copy with the pinned hash is
used through `data import`.

## Vendored primitive

`src/tajziya/_vendor/unknown.py` is `zistgah/dhancha@e312d3960c5eb3572fd5975faf7767ba41d0d5a4 core/unknown.py`, byte for byte,
SHA-256 `2c68a58d1a6d98add86c06ba8ce3c7454b561964a06a182e8b07e8d2282bc09a`.

## Prior work reconciled

`registry/prior/ilm-template.csv` is zistgah/humanesque@1a0366929a912416f9cad7d66ee782133f7924da ilm/ilm-template.csv, SHA-256 `9cd4c2c75c00c6fda4af46b272f3eda338e89505b9ccda0f14ea205c4011c4cc`, the ILM template
of 30 Aug 2026. It is reconciled against this registry by `tajziya reconcile`, not merged.

## The posters

Three posters supplied by the author on 26 Sep 2026: *Candidate Language x Unique Corpus Matrix,
Version 0.1* (poster I), *Canonical Architecture for Human Knowledge Recovery* (poster II) and
*A Four-Axis Solution: Minimum-Loss Optimization for Human Knowledge* (poster III). Their language
rows, statuses, stage trees, script families, corpus classes, epistemic states and elimination rule
are transcribed into `registry/`, each entry citing its section. The images are not in this
repository; they belong in a poster lineage of their own. Poster II's natural substrates and
poster III's class C0 are outside this repository.

## Standards

ISO 639-3 and ISO 15924 codes were verified against iso-codes as shipped in pycountry 26.2.16.
Every code in the registry resolved; `pra`, an ISO 639-2 collective code, is not used.

## Licence texts

From spdx/license-list-data:

- `LICENSES/GPL-3.0-or-later.txt`: `fb981668c18a279e285fc4d83fba1e836cc84dd4daa73c9697d3cfd2d8aca6e0`
- `LICENSES/MIT.txt`: `b05785f9f18e6716bab63424b11454513b9943a222595b70411009202fc592b5`
- `LICENSES/CC-BY-SA-4.0.txt`: `cde7883b9050a1104f4ac19a1572aafd6e5d7323b68351aaf51fbf4beba54966`
- `LICENSES/CC0-1.0.txt`: `a2010f343487d3f7618affe54f789f5487602331c0a8d03f49e9a7c547cf0499`

## Sutra text, 0.2.0

`modules/cls/data/sutrapatha.tsv` is `vidyut-prakriya/data/sutrapatha.tsv` from
ambuda-org/vidyut@8da2f90bee3ce1c07505fa432fc3729e3f7e02ea, byte for byte: 3,983 sutras, SLP1,
SHA-256 `f2ff798707e8b8ea20dd5cf20a7bbcc4b849f0ab4d726a0a4af890ef87b7e87c`. The crate declares the MIT
licence; `modules/cls/data/LICENSES/vidyut-MIT.txt` is the repository's MIT notice, byte for byte. Its data
README states that the author of ashtadhyayi.com shared these files with vidyut under the MIT licence.
The four examples in `modules/cls/reference/examples.json` are attested in the parser's own demonstration,
`vendor/sanskrit_parser/python/pipeline.py`. The restricted compilation's local copy now sits in
`modules/cls/data/local/`; `vendor/sanskrit_parser/data/SOURCE.json` records where the upstream first
expected it.

## Treebank facts, 0.2.0

`registry/corpora.json` records, for 52 nodes, the Universal Dependencies treebanks whose language code
matches, each with its repository and stated licence, read from
UniversalDependencies/docs@b3768d7f7b4b44b74a84025eddb2fcce04f40eaf `treebanks/*/index.md` on
26 Sep 2026. Only names, links and licence statements are recorded; no treebank data is in this
repository.
