// © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
// SPDX-License-Identifier: MIT
/**
 * Vowel sandhi (svarasandhi): combination and reverse-lookup.
 * Pure JS port of sandhi.py -- same rules, same behavior.
 *
 * Scope: only the patterns needed to join or split two adjacent vowels
 * across a word boundary. This is standard, well-established descriptive
 * Sanskrit phonology -- safe to implement directly, unlike the enumerated
 * sutra corpus itself, which needs to come from a sourced text (see
 * README.md). The `sutra` field on SandhiResult is a placeholder: once the
 * actual Adhyaya 6/8 rules are sourced, each branch below should cite the
 * specific sutra it implements, rather than being described only in prose
 * as it is now.
 *
 * NOT covered here: consonant sandhi, visarga sandhi, or junctions spanning
 * more than two adjacent vowels. Those are separate, real rule sets (also
 * in Adhyaya 6 and 8) and belong in their own modules, built the same way.
 */

function nfc(s) {
  // Normalize to precomposed Unicode so diacritics behave as single
  // characters for indexing/slicing -- IAST vowels like 'u-macron' must
  // not silently be two code points (base + combining macron).
  return s.normalize("NFC");
}

function mapNfc(obj, mapValuesToo = true) {
  const out = {};
  for (const [k, v] of Object.entries(obj)) {
    out[nfc(k)] = mapValuesToo ? nfc(v) : v;
  }
  return out;
}

export const VOWELS = ["a", "ā", "i", "ī", "u", "ū", "ṛ", "ṝ", "ḷ", "e", "ai", "o", "au"].map(nfc);

const SHORT_LONG = mapNfc({ a: "ā", i: "ī", u: "ū", ṛ: "ṝ" });
const LONG_SHORT = Object.fromEntries(Object.entries(SHORT_LONG).map(([k, v]) => [v, k]));

const GUNA_OF = mapNfc({ i: "e", ī: "e", u: "o", ū: "o", ṛ: "ar", ḷ: "al" });
const VRDDHI_OF = mapNfc({ i: "ai", ī: "ai", u: "au", ū: "au", e: "ai", o: "au" });
const YAN = mapNfc({ i: "y", ī: "y", u: "v", ū: "v", ṛ: "r" }, false);

const A_LIKE = new Set([nfc("a"), nfc("ā")]);

export class SandhiResult {
  constructor(combined, sutra = null) {
    this.combined = combined;
    this.sutra = sutra; // TODO: fill in once Adhyaya 6/8 are sourced
  }
}

export function combineVowels(leftFinal, rightInitial) {
  leftFinal = nfc(leftFinal);
  rightInitial = nfc(rightInitial);

  // 1. savarna dirgha: identical vowel, short or long -> long
  const lShort = LONG_SHORT[leftFinal] ?? leftFinal;
  const rShort = LONG_SHORT[rightInitial] ?? rightInitial;
  if (lShort === rShort && lShort in SHORT_LONG) {
    return new SandhiResult(SHORT_LONG[lShort]);
  }

  // 2. a/a-macron + i/i-macron/u/u-macron/vocalic-r/vocalic-l -> guna
  if (A_LIKE.has(leftFinal) && rightInitial in GUNA_OF) {
    return new SandhiResult(GUNA_OF[rightInitial]);
  }

  // 3. a/a-macron + e/o -> vrddhi (only reached when right isn't already
  //    caught by guna above, i.e. right_initial in {e, o})
  if (A_LIKE.has(leftFinal) && rightInitial in VRDDHI_OF) {
    return new SandhiResult(VRDDHI_OF[rightInitial]);
  }

  // 4. i/u/vocalic-r (long or short) + a dissimilar vowel -> semivowel + vowel
  if (leftFinal in YAN && rightInitial !== leftFinal) {
    return new SandhiResult(YAN[leftFinal] + rightInitial);
  }

  // 5. e/o + a -> e/o with the a elided (avagraha in Devanagari; "'" here)
  if ((leftFinal === nfc("e") || leftFinal === nfc("o")) && rightInitial === nfc("a")) {
    return new SandhiResult(leftFinal + "'");
  }

  // 6. ai/au + any vowel -> a-macron-y / a-macron-v + that vowel
  if (leftFinal === nfc("ai")) {
    return new SandhiResult(nfc("āy") + rightInitial);
  }
  if (leftFinal === nfc("au")) {
    return new SandhiResult(nfc("āv") + rightInitial);
  }

  throw new Error(`No rule covers ${JSON.stringify(leftFinal)} + ${JSON.stringify(rightInitial)}`);
}

function buildReverseIndex() {
  const index = new Map();
  for (const l of VOWELS) {
    for (const r of VOWELS) {
      let merged;
      try {
        merged = combineVowels(l, r).combined;
      } catch {
        continue;
      }
      if (!index.has(merged)) index.set(merged, []);
      index.get(merged).push([l, r]);
    }
  }
  return index;
}

export const REVERSE_INDEX = buildReverseIndex();

export function possibleSplits(merged) {
  return REVERSE_INDEX.get(nfc(merged)) ?? [];
}

if (typeof process !== "undefined" && import.meta.url === `file://${process.argv[1]}`) {
  const examples = [
    ["a", "i", "e"],    // na + iti -> neti
    ["a", "e", "ai"],   // tatra + eva -> tatraiva
    ["u", "u", "ū"],    // guru + upadesha -> gurupadesha
    ["ā", "i", "e"],    // sita + iva -> siteva
  ];
  console.log("Forward (combine):");
  for (const [l, r, expected] of examples) {
    const result = combineVowels(l, r);
    const status = result.combined === nfc(expected) ? "OK" : `MISMATCH (got ${JSON.stringify(result.combined)})`;
    console.log(`  ${l} + ${r} -> ${result.combined}  [${status}]`);
  }

  console.log("\nReverse (segment): what could a bare 'e' junction have come from?");
  for (const [l, r] of possibleSplits("e")) {
    console.log(`  ${l} + ${r}`);
  }
  console.log("(this is the ambiguity itself -- 4 grammatically valid answers, not 1)");
}
