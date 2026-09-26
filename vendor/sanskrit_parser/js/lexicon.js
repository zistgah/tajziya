// © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
// SPDX-License-Identifier: MIT
/**
 * Placeholder lexicon -- NOT a real dictionary. Pure JS port of lexicon.py.
 *
 * A dozen words, just enough to demonstrate Segmenter end-to-end (see
 * pipeline.js and sandhi.js). A real lexicon needs to come from an actual
 * source, e.g. vidyut's `kosha` component, or derived from DCS
 * (sanskrit-linguistics.org/dcs) -- see README.md's "Next steps". Every
 * entry below is a real Sanskrit word, but the *list* itself is arbitrary
 * and tiny on purpose: don't mistake it for coverage.
 */

export const TOY_LEXICON = new Set([
  "na", "iti", "tatra", "eva", "guru", "upadeśa", "sītā", "iva",
  "rāma", "hariḥ", "gacchati", "vanam",
]);
