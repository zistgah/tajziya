# Changelog

© 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.

## 0.2.0

- Language modules. A language is a folder under `modules/<node>/` with `module.json`, a port importing
  only `tajziya.api`, `data/SOURCES.json` and `reference/examples.json`. Modules are discovered by
  scanning, loaded by path, and used only when `registry/bindings.json` binds them.
- `tajziya accept`: one generic acceptance test for any module, in isolation (A1 to A5) and bound in a
  scratch copy of the repository (A6).
- `tools/langpack.py`: generates a hand-over package for any node, any ISO 639-3 code, or every remaining
  node. Each package passes the acceptance test as handed over, and archives are reproducible.
- Classical Sanskrit moved into `modules/cls` as the reference module. Its sutra text is re-sourced from
  vidyut-prakriya's MIT-licensed sutrapatha, all 3,983 sutras; the restricted compilation is local-only.
- `registry/licences.json`: the licences data may carry. `registry/corpora.json`: Universal Dependencies
  treebanks matched to 52 nodes, each with its stated licence and whether the tree may carry it.
- The harness now exercises every layer declared built, including one with no reference input.
- `tools/node_new.py` removed; `tools/langpack.py` replaces it.

## 0.1.0

- The registry of 79 language and stage nodes, the family frames, the Classical Sanskrit segmenter,
  the elimination rule, the site, and the gate. DOI 10.5281/zenodo.22982238.
