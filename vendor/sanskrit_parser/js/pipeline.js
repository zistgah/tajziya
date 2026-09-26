// © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
// SPDX-License-Identifier: MIT
/**
 * Pipeline skeleton for full-sentence Sanskrit parsing. Pure JS port of
 * pipeline.py -- same structure, same behavior.
 *
 * Three stages, matching the three real subproblems (see README.md):
 *   1. Segmenter      -- splits a sandhi'd phonetic stream into candidate words
 *   2. MorphAnalyzer  -- tags each candidate word with its grammatical structure
 *   3. KarakaParser   -- assigns karaka/dependency relations between words
 *
 * Segmenter does real vowel-sandhi reversal against a lexicon (see
 * sandhi.js, lexicon.js) -- MorphAnalyzer and KarakaParser are still stubs.
 * The rule data in ../data/sutras_1.1-1.3.json covers only the
 * samjna/paribhasha/atidesha rules of Adhyaya 1, Pada 1-3 so far -- the
 * sandhi rules Segmenter's vowel logic should eventually cite (~281 of
 * them, mostly Adhyaya 6 Pada 1 and Adhyaya 8) and the karaka rules
 * KarakaParser needs (Adhyaya 1.4, 2.3) aren't sourced yet. See README.md's
 * "Next steps" and its note on existing systems (Sanskrit Heritage Engine +
 * Samsaadhanii) before reimplementing too much of this from scratch.
 */

import { loadSutras } from "./rules.js";
import { REVERSE_INDEX } from "./sandhi.js";
import { TOY_LEXICON } from "./lexicon.js";

export class Candidate {
  // One candidate word produced by segmentation, before morphological
  // analysis has confirmed it's actually valid.
  constructor(text, start, end) {
    this.text = text;   // the candidate word, as split out of the input
    this.start = start; // character offset of this candidate in the original input
    this.end = end;
  }
}

export class Token {
  // A word after morphological analysis.
  constructor(surface, lemma = null, features = {}) {
    this.surface = surface;   // the word as it appears (post-sandhi)
    this.lemma = lemma;       // dictionary form / root
    this.features = features; // case, number, tense, etc.
  }
}

export class KarakaRelation {
  // A syntactic/semantic relation between two analyzed tokens.
  constructor(head, dependent, relation) {
    this.head = head;
    this.dependent = dependent;
    this.relation = relation; // e.g. "karta" (agent), "karma" (object), "karana" (instrument)
  }
}

export class Segmenter {
  /**
   * Stage 1: split a continuous Sanskrit string into candidate words.
   *
   * IMPLEMENTED (partially): vowel-sandhi reversal against a lexicon, via
   * sandhi.js + lexicon.js. This covers exactly one class of junction --
   * two adjacent vowels merging into one -- and only knows words that are
   * in the (tiny, placeholder) lexicon. NOT implemented: consonant sandhi,
   * visarga sandhi, compounds, or anything beyond a toy word list. Real
   * input is usually ambiguous: segment() returns every solution it finds,
   * not one -- ranking/picking the intended one is a separate concern
   * (see README's note on segmentation ambiguity) not yet addressed.
   */
  constructor(sutras, lexicon = null) {
    this.sutras = sutras;
    this.lexicon = lexicon ?? TOY_LEXICON;
  }

  segment(text) {
    const wordSequences = this._segmentWords(text);
    return wordSequences.map((words) => {
      let pos = 0;
      return words.map((w) => {
        const c = new Candidate(w, pos, pos + w.length);
        pos += w.length; // approximate: post-sandhi text is usually
                          // shorter than the sum of the original words
        return c;
      });
    });
  }

  _segmentWords(text) {
    // Core recursion: every way to split `text` into lexicon words,
    // undoing sandhi.REVERSE_INDEX junctions where needed.
    const results = [];
    if (this.lexicon.has(text)) {
      results.push([text]);
    }

    for (const [junction, pairs] of REVERSE_INDEX) {
      let start = text.indexOf(junction);
      while (start !== -1) {
        for (const [leftV, rightV] of pairs) {
          const left = text.slice(0, start) + leftV;
          const right = rightV + text.slice(start + junction.length);
          if (this.lexicon.has(left)) {
            for (const rest of this._segmentWords(right)) {
              results.push([left, ...rest]);
            }
          }
        }
        start = text.indexOf(junction, start + 1);
      }
    }

    const seen = new Set();
    const unique = [];
    for (const r of results) {
      const key = JSON.stringify(r);
      if (!seen.has(key)) {
        seen.add(key);
        unique.push(r);
      }
    }
    return unique;
  }
}

export class MorphAnalyzer {
  // Stage 2: tag each segmented word with its grammatical structure.
  constructor(sutras) {
    this.sutras = sutras;
  }

  analyze(candidate) {
    throw new Error(
      "MorphAnalyzer needs the karaka/vibhakti rules and a lexicon -- see README.md next steps."
    );
  }
}

export class KarakaParser {
  // Stage 3: assign karaka (syntactic/semantic) relations between the
  // analyzed words of a sentence, per Panini's karaka theory (1.4, 2.3).
  constructor(sutras) {
    this.sutras = sutras;
  }

  parse(tokens) {
    throw new Error(
      "KarakaParser needs the Adhyaya 1.4 / 2.3 karaka rules -- see README.md next steps."
    );
  }
}

export class SanskritParser {
  // Top-level pipeline: text in, karaka-annotated parse out.
  constructor(sutras = null) {
    this.sutras = sutras ?? loadSutras();
    this.segmenter = new Segmenter(this.sutras);
    this.morph = new MorphAnalyzer(this.sutras);
    this.karaka = new KarakaParser(this.sutras);
  }

  parse(text) {
    const segmentations = this.segmenter.segment(text);
    // Once MorphAnalyzer/KarakaParser are real: pick or rank a
    // segmentation, run MorphAnalyzer over each candidate, then hand the
    // resulting tokens to KarakaParser.
    throw new Error("Not implemented past segmentation -- see README.md next steps.");
  }
}

if (typeof process !== "undefined" && import.meta.url === `file://${process.argv[1]}`) {
  const parser = new SanskritParser();
  console.log(
    `Pipeline initialized with ${parser.sutras.length} rules loaded ` +
    `(${parser.sutras[0].id} - ${parser.sutras[parser.sutras.length - 1].id}).`
  );

  console.log("\nSegmenter (real, limited) on known examples:");
  for (const text of ["neti", "tatraiva", "gurūpadeśa", "sīteva"]) {
    const solutions = parser.segmenter.segment(text);
    const words = solutions.map((sol) => sol.map((c) => c.text));
    console.log(`  ${JSON.stringify(text)} -> ${JSON.stringify(words)}`);
  }

  console.log(
    "\nMorphAnalyzer and KarakaParser are still stubs -- " +
    "see README.md's Next steps for what unblocks each one."
  );
}
