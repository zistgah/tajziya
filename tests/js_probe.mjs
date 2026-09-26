// © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
// SPDX-License-Identifier: GPL-3.0-or-later
// Prints what the JavaScript port of the parser answers, for tests/parity.py to compare.
import { pathToFileURL } from "node:url";
import { resolve } from "node:path";

const dir = resolve(process.argv[2]);
const cases = JSON.parse(process.argv[3]);
const load = (f) => import(pathToFileURL(resolve(dir, f)).href);
const sandhi = await load("sandhi.js");
const lex = await load("lexicon.js");
const pipe = await load("pipeline.js");
const pairs = {};
for (const l of sandhi.VOWELS) {
  for (const r of sandhi.VOWELS) {
    let v = null;
    try { v = sandhi.combineVowels(l, r).combined; } catch (e) { v = null; }
    pairs[`${l}|${r}`] = v;
  }
}
const splits = {};
for (const [k, v] of sandhi.REVERSE_INDEX) splits[k] = v.map((p) => [p[0], p[1]]);
const segs = {};
for (const c of cases) {
  const s = new pipe.Segmenter([], c.lexicon ? new Set(c.lexicon) : lex.TOY_LEXICON);
  segs[c.text] = s.segment(c.text).map((sol) => sol.map((x) => x.text));
}
process.stdout.write(JSON.stringify({ pairs, splits, segs }));
