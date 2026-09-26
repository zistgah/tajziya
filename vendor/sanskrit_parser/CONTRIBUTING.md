# Contributing

This project is meant to be picked up in batches, not built end to end by
one person in one pass. A batch is one coherent chunk of rules -- e.g. one
pada, or one rule-type (all sandhi rules, all karaka rules) -- taken from
sourcing through to tested implementation.

## Per-batch checklist

1. **Source it.** Pull the rule text from a real, citable source (see
   README's "Sources" section). No rule text goes in `data/` without a
   named source.
2. **Record provenance.** For each source used: URL, retrieval date, and a
   content hash of what was actually pulled. Archive the page (e.g. Wayback
   Machine) rather than linking only the live URL -- community-maintained
   pages move and change.
3. **Cross-check.** Where more than one source covers the same rule(s),
   note any disagreement (numbering, wording, classification) rather than
   silently picking one. See README's "Differences across sources."
4. **Add to `data/`.** Follow the existing schema (see README's "Data
   schema"). Keep entries in traditional sutra order.
5. **Implement, if it's in scope for the current pipeline stage.** Not
   every sourced rule needs code immediately -- sourcing and implementing
   are separate, trackable steps.
6. **Test against real examples**, the same way `sandhi.py`/`sandhi.js`
   are tested against textbook sandhi examples in their own `__main__`
   blocks -- not just that the code runs, but that its output is correct.
7. **Release with a DOI.** A DOI is minted for this repository's own work.
   A third-party compilation is cited with its URL, retrieval date and
   content hash, and is deposited only where its terms permit
   redistribution.

## Keeping Python and JS in sync

`python/` and `js/` are meant to stay behavior-identical. If you change one,
port the change to the other and re-run both `__main__`/demo blocks to
confirm matching output before opening a PR.

## Scope reminders

- Don't hand-write rule *text* from memory, even rules that feel standard
  or well-known -- source it the same way everything else here was sourced.
  General linguistic description (e.g. explaining a phenomenon in a
  docstring) is fine; treating unsourced text as if it were a cited sutra
  is not.
- Check README's note on existing systems (Sanskrit Heritage Engine,
  Samsaadhanii, vidyut-prakriya/vidyut-cheda) before reimplementing
  something they already do well.
