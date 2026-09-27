# CONTEXT: tajziya

© 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.

## What it answers

The author asked for a complete system of parsers for the classical languages his posters set out,
with his Sanskrit parser in it, stubs for the other languages divided into families, their
commonalities found, and the whole seeded and minted (26 Sep 2026). The posters are the brief: the
candidate language matrix (poster I), the canonical architecture for knowledge recovery
(poster II), and the four-axis minimum-loss model (poster III).

## Where it sits

A Zistgah element on the dhancha spine: one interface, a registry that alone chooses
implementations, a mock and a template port, a harness that defines conformance, verbs as data,
four attachment points, a roadmap as data, and three honest states. It fills the linguistic layers
of Project ILM, whose layer repositories are scaffolds today.

## Work retrieved before building

- ILM layer stack (project-ilm, retrieved 26 Sep 2026): ilm-phonology L0, ilm-transliteration L1,
  ilm-orthography L2, ilm-lexicon L3, ilm-syntax-semantics L4. All five hold only a README.
- project-ilm/romenagri@ef57fa4: script tables projecting 75 scripts to a Devanagari hub. The L1
  pivot attaches there.
- zistgah/humanesque@1a03669: the ILM template of 30 Aug 2026, reconciled in `registry/prior/`.
- The Hindawi rulings: script, language and standard are separate axes; the construct is primary.
- zistgah/dhancha@e312d39: the ten invariants and the Unknown primitive.
- zistgah/panini@176b9cd: the cycler language and its checker.

## Choices made in this build, flagged for the author

- The name tajziya (تجزیہ, analysis) and the org zistgah. Both live in `seed.json`.
- Genealogical families and lineages, with the posters' areal groups kept on each node.
- The engine vocabulary, eleven engines on two axes, and each lineage's language engines. These are
  general typology; citable sources are package P-SRC-01.
- Classical Sanskrit alone is bound to the parser. Vedic and Epic stay stubs until the segmenter is
  validated on them (P-SAN-08).
- The sutra compilation is withheld on a reading of its source's stated terms (P-LEG-01).

## Licensing

Master clause 2: software GPL-3.0-or-later, documents CC-BY-SA-4.0, metadata CC0-1.0. The
vendored parser keeps the MIT licence its author chose.

## Deposit

A first deposit: a new record, not a version of any existing concept DOI. A DOI is a dated public
disclosure. Nothing here states an unfiled claim; V15 refuses the language of one.

## 0.2.0, 26 Sep 2026

The author asked for a package per remaining language that another model or a person can take and
return with an implementation, for the architecture to carry language modules, for one generic
package, one generator run over a list of codes, one generic acceptance test, and for the best proper
alternative wherever a licence stood in the way.

- Modules live in `modules/<node>/`, import only `tajziya.api` (API 1), and are bound only after
  `tajziya accept` passes. Classical Sanskrit is the reference module.
- The sutra text was re-sourced from vidyut-prakriya (MIT), whose data README states that
  ashtadhyayi.com shared these files under MIT. That covers all 3,983 sutras where the restricted
  compilation covered 152, at the cost of its padaccheda and Devanagari, which stay available only from a
  local copy.
- Packages point implementers at Universal Dependencies treebanks for their language codes, each marked by
  whether its licence lets it into the tree. Non-commercial and no-derivatives licences stay out.
- Not settled here, and left to the author: inbound terms for contributions from people other than the
  author that keep the author able to relicense (P-GOV-01). Work produced by an AI at the author's
  direction carries the estate copyright line.
- 0.2.0 is pushed and sealed without a new DOI. A version DOI beneath the 0.1.0 concept DOI needs a
  newversion path in the library; `zops_mint` refuses to mint a second record for a repository that
  already carries a DOI.
