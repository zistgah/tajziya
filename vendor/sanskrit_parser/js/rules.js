// © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
// SPDX-License-Identifier: MIT
/**
 * Minimal loader for the Ashtadhyayi rule database. Pure JS port of
 * rules.py -- same behavior, same JSON file (../data/sutras_1.1-1.3.json).
 *
 * Just enough to load and query the rules compiled so far. Does NOT
 * implement any derivation/analysis logic -- see pipeline.js and README.md.
 */

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const DEFAULT_DATA_PATH = join(__dirname, "..", "data", "sutras_1.1-1.3.json");

export class Sutra {
  constructor({ id, sutra_krama, kaumudi_krama, type, term, sutra, padaccheda }) {
    this.id = id;                       // "1.1.1" (adhyaya.pada.sutra)
    this.sutra_krama = sutra_krama;     // sequential index, traditional order
    this.kaumudi_krama = kaumudi_krama; // position in Siddhanta Kaumudi order
    this.type = type;                   // "samjna" | "paribhasha" | "atidesha" | null
    this.term = term;                   // term defined, for samjna rules; else null
    this.sutra = sutra;                 // the rule text, Devanagari
    this.padaccheda = padaccheda;       // word-by-word split, Devanagari, or null
  }

  get adhyaya() {
    return Number(this.id.split(".")[0]);
  }

  get pada() {
    return Number(this.id.split(".")[1]);
  }

  get sutraNumber() {
    return Number(this.id.split(".")[2]);
  }
}

export function loadSutras(path = DEFAULT_DATA_PATH) {
  const raw = JSON.parse(readFileSync(path, "utf-8"));
  return raw.map((entry) => new Sutra(entry));
}

export function byId(sutras, sutraId) {
  return sutras.find((s) => s.id === sutraId) ?? null;
}

export function byType(sutras, type) {
  return sutras.filter((s) => s.type === type);
}

if (typeof process !== "undefined" && import.meta.url === `file://${process.argv[1]}`) {
  const sutras = loadSutras();
  console.log(`Loaded ${sutras.length} sutras (${sutras[0].id} - ${sutras[sutras.length - 1].id}).`);

  const samjnas = byType(sutras, "samjna");
  console.log(`\n${samjnas.length} are samjna (technical-term-defining) rules, e.g.:`);
  for (const s of samjnas.slice(0, 5)) {
    console.log(`  ${s.id}  ${s.term}  --  ${s.sutra}`);
  }

  const paribhashas = byType(sutras, "paribhasha");
  console.log(`\n${paribhashas.length} are paribhasha (interpretive meta-)rules, e.g.:`);
  for (const s of paribhashas.slice(0, 3)) {
    console.log(`  ${s.id}  --  ${s.sutra}`);
  }
}
