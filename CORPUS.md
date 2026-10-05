# Work order: test corpora for tajziya

© 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.

## Why

tajziya (github.com/zistgah/tajziya) is a parser federation for the classical languages on
Abhishek Choudhary's posters: 79 language-and-stage nodes, each a module behind one acceptance
test. Version 0.5.0 (wait for the tag `upgrade-0.5.0-applied` before you clone) carries the whole
Aṣṭādhyāyī in `modules/cls/data/ashtadhyayi/sutraani.tsv`: 3,983 sutras with type, defined term,
padaccheda and Siddhānta Kaumudī number. 99 of them name छन्दसि, Vedic usage; 12 of those say
बहुलं छन्दसि.

Pāṇini's grammar does not account for every word of the Vedic and early Sanskrit corpus. Your job
is to measure where, and by how much, on attested text whose analyses come from the sources
themselves. Then build the same kind of test corpus for every other classical node, so each
language's parser has a yardstick.

## Rules that are not negotiable

1. **Retrieve, never recall.** Every unit comes from a file you downloaded, listed in a
   `SOURCES.json` with its URL, retrieval date and SHA-256. Nothing is typed from memory.
2. **Gold comes from the source.** Segmentation and analyses are the edition's or the treebank's.
   Anything you or a tool produce goes in a separate `machine` field with the tool and version,
   never in the gold fields.
3. **Never alter an attested form** to make it derivable, and never drop a form because it fails.
4. **Licences: `registry/licences.json` decides.**
   - A licence in `allowed` enters the tree.
   - One in `notice_required` enters with its notice in `LICENSES/`.
   - Anything else (non-commercial, no derivatives, no reposting, or no stated terms) is
     `local_only`: listed with its pin, its text never committed.
   - Where a source states terms without a licence, quote them verbatim, mark the source
     `"terms": "owner to rule"`, and commit nothing from it until he rules.
5. **Counts are exact.** Anything not run is reported as "not attempted", never estimated.
6. **Stay inside the repository.** No absolute paths. Tests make no network calls: imports
   run once from pinned downloads.
7. **Every authored file** carries `© 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.`;
   code also carries `SPDX-License-Identifier: GPL-3.0-or-later`. Affiliation is AyeAI only.

## What you deliver

    corpus/<node>/README.md        texts covered, sizes, what each source supplies, known gaps
    corpus/<node>/SOURCES.json     schema tajziya.sources/1, as in modules/cls/data/SOURCES.json
    corpus/<node>/units.jsonl      one unit per line, schema below
    corpus/<node>/LICENSES/        notices the licences require
    tools/corpus_import_<source>.py   deterministic import from a pinned download; --check
                                      regenerates units.jsonl byte for byte
    tools/corpus_coverage_san.py      the Pāṇinian coverage run
    corpus/vsn/coverage/           results.jsonl, summary.json, README.md

A unit:

    {"id": "RV.1.1.1", "node": "vsn", "source": "<SOURCES id>",
     "locator": "<as the edition cites it>",
     "text": "<surface text as the edition gives it, Unicode NFC>",
     "script": "Deva", "accented": true,
     "tokens": [...] or null,          the source's own segmentation (padapāṭha, treebank tokens)
     "analyses": [{"form", "lemma", "pos", "features"}] or null,   the source's gold
     "stratum": "<label>" or null, "stratum_source": "<citation>" or null}

A stratum is filled only from the source or a cited chronology, never from your judgement.

## Part A: Sanskrit (nodes vsn, san-epic, cls)

**A1. Gather.** Check these candidates, assuming no licence until you have read it:
- UD_Sanskrit-Vedic and UD_Sanskrit-UFAL (`registry/corpora.json` records their stated
  licences and whether the policy allows them);
- the Digital Corpus of Sanskrit;
- VedaWeb's annotated Ṛgveda;
- GRETIL;
- Ambuda;
- the Sanskrit Heritage Platform's data.

A padapāṭha from an openly licensed edition is gold segmentation for its saṃhitā.

**A2. Pilot first.** Take Ṛgveda maṇḍala 1, hymns 1 to 10, or the nearest stretch an allowed
source annotates, end to end through A3 and A4. Report it before scaling.

**A3. The test.** For each attested word with a gold analysis, ask vidyut-prakriya to derive the
form from that analysis. vidyut is MIT-licensed, published on PyPI as `vidyut` (0.4.0 on
5 October 2026); check what its Python bindings expose before relying on them. Record one
outcome per form:
- **derived**;
- **derived, accent differs**;
- **not derived**;
- **derived only through a chandasi sutra**: match the derivation's trace against the 99 in
  sutraani.tsv;
- **not attempted**: vidyut cannot express the analysis.

Keep the sutra ids from each trace.

Then, where gold tokens exist, run tajziya's segmenter (`python3 -m tajziya segment --node cls`,
IAST input) and record whether the gold split is the first reading, among the readings, or absent.

**A4. Report.** Coverage by stratum, where a stratum is sourced; by word class; and by category,
for example the subjunctive (leṭ), which Pāṇini admits only in chandas. The main result is the
list of forms not derived, each with its gold analysis and locator.

**A5. Scale.** Extend in this order, as open sources allow: the rest of the Ṛgveda, the
Atharvaveda, Brāhmaṇa and Upaniṣad prose, the Epic, Classical texts.

## Part B: the other classical nodes

- `registry/nodes.json` lists the 79 nodes. `registry/corpora.json` lists the Universal
  Dependencies treebanks matched to each, with stated licence and whether the policy allows it;
  50 nodes have at least one allowed.
- **Order of work:** build `corpus/<node>/` for those 50 first, the ones whose allowed treebanks
  carry morphological features ahead of the rest. Tokens and analyses come from the treebank.
- **Where no allowed treebank exists**, look for an openly licensed digital edition. If there is
  none, the README says so and lists what you checked with each source's terms. Fill nothing in.
- **Native grammars.** Where the language has a grammatical tradition of its own, note in the
  README whether an open, machine-readable edition of it exists; examples are the Tolkāppiyam,
  Sībawayh's Kitāb and Dionysius Thrax's Tékhnē. Building that coverage test is the next order,
  not this one.

## Acceptance, run by us on hand-back

- C1 every line of units.jsonl parses and has the fields above;
- C2 every unit names a source in SOURCES.json and a locator;
- C3 every source has URL, date, SHA-256 and an allowed or notice licence, or is local_only with
  its text absent from the tree;
- C4 text is NFC and in the scripts the node declares;
- C5 no unit is duplicated;
- C6 where tokens exist they are non-empty and, for languages without sandhi, rebuild the
  surface text;
- C7 every import script regenerates its units.jsonl byte for byte from its pinned download;
- C8 the counts in each README equal the data's.

## Hand-back

A tarball `tajziya-corpus-<date>.tar.gz` holding `corpus/` and `tools/`, with no restricted
text, and a `REPORT.md` covering:
- every source checked and its terms;
- counts per node;
- the Sanskrit coverage summary;
- what failed and why.

Do not push to the repository.
