#!/usr/bin/env python3
# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""How each sutra generates words: sample derivations with vidyut-prakriya, indexed by sutra.

    python3 tools/derivations.py --data <vidyut data dir> [--check]

vidyut-prakriya (MIT, github.com/ambuda-org/vidyut) derives a word from its recipe and logs every
sutra it applies. This runs a fixed, deterministic sample of recipes:
  - every root of the dhatupatha in every lakara, third person singular, active;
  - the first 60 roots in all lakaras, persons and numbers;
  - the first 200 roots with every krt suffix vidyut knows, as a nominative singular masculine;
  - five stems with every taddhita suffix vidyut knows;
  - fifteen nominal stems taught in the paradigms, in every case and number.
For each sutra it records in how many sample derivations it acts, and up to three of the shortest
examples with all their steps. Output: docs/data/generation/<adhyaya>.<pada>.json, and
docs/data/generation/index.json for looking a word up. Exit 3 when vidyut cannot run here.
"""
import argparse
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "data", "generation")
STEMS = [("rAma", "Pum"), ("hari", "Pum"), ("guru", "Pum"), ("pitf", "Pum"), ("rAjan", "Pum"), ("sarva", "Pum"),
         ("ramA", "Stri"), ("mati", "Stri"), ("nadI", "Stri"), ("DenU", "Stri"), ("vAc", "Stri"),
         ("jYAna", "Napumsaka"), ("vAri", "Napumsaka"), ("manas", "Napumsaka"), ("jagat", "Napumsaka")]


def build(data_dir):
    from vidyut import prakriya as P, lipi
    deva = lambda s: lipi.transliterate(s, lipi.Scheme.Slp1, lipi.Scheme.Devanagari)
    v = P.Vyakarana()
    entries = P.Data(os.path.join(data_dir, "prakriya")).load_dhatu_entries()
    recipes = []
    core = []
    for e in entries:
        for lak in P.Lakara.choices():
            recipes.append((f"{e.dhatu.aupadeshika} ({e.code}) · {lak} · Prathama · Eka · kartari",
                            P.Pada.Tinanta(dhatu=e.dhatu, prayoga=P.Prayoga.Kartari, lakara=lak,
                                           purusha=P.Purusha.Prathama, vacana=P.Vacana.Eka)))
    for e in entries[:200]:
        for krt in P.Krt.choices():
            recipes.append((f"{e.dhatu.aupadeshika} ({e.code}) + {krt} · Pum · Prathama · Eka",
                            P.Pada.Subanta(pratipadika=P.Pratipadika.krdanta(e.dhatu, krt), linga=P.Linga.Pum,
                                           vibhakti=P.Vibhakti.Prathama, vacana=P.Vacana.Eka)))
    for stem in ("upagu", "deva", "rAma", "guru", "nadI"):
        for t in P.Taddhita.choices():
            recipes.append((f"{stem} + {t} · Pum · Prathama · Eka",
                            P.Pada.Subanta(pratipadika=P.Pratipadika.taddhitanta(P.Pratipadika.basic(stem), t),
                                           linga=P.Linga.Pum, vibhakti=P.Vibhakti.Prathama, vacana=P.Vacana.Eka)))
    for e in entries[:60]:
        for lak in P.Lakara.choices():
            for pur in P.Purusha.choices():
                for vac in P.Vacana.choices():
                    recipes.append((f"{e.dhatu.aupadeshika} ({e.code}) · {lak} · {pur.name} · {vac.name} · kartari",
                                    P.Pada.Tinanta(dhatu=e.dhatu, prayoga=P.Prayoga.Kartari, lakara=lak,
                                                   purusha=pur, vacana=vac)))
    for stem, linga in STEMS:
        pr = P.Pratipadika.basic(stem)
        for vib in P.Vibhakti.choices():
            for vac in P.Vacana.choices():
                recipes.append((f"{stem} · {linga} · {vib.name} · {vac.name}",
                                P.Pada.Subanta(pratipadika=pr, linga=getattr(P.Linga, linga), vibhakti=vib, vacana=vac)))
                core.append(recipes[-1][0])
    core = set(core) | {r for r, _ in recipes if " · Prathama · Eka · kartari" in r and "la~w" in r}
    core |= {r for r, _ in recipes[len(entries) * len(P.Lakara.choices()):] if "kartari" in r}
    derivs = []
    for recipe, pada in recipes:
        try:
            results = v.derive(pada)
        except Exception:
            continue
        for p in results:
            steps = [[s.code, "+".join(s.result)] for s in p.history]
            derivs.append({"w": deva(p.text), "slp": p.text, "recipe": recipe, "steps": steps})
    derivs.sort(key=lambda d: (d["recipe"], d["slp"]))
    per = {}
    for i, d in enumerate(derivs):
        seen = set()
        for j, (code, _) in enumerate(d["steps"]):
            if code in seen:
                continue
            seen.add(code)
            per.setdefault(code, []).append((len(d["steps"]), d["recipe"], i, j))
    shards, words = {}, []
    for code, hits in per.items():
        parts = code.split(".")
        if len(parts) != 3 or not all(x.isdigit() for x in parts):
            continue
        hits.sort()
        ex = []
        for _, _, i, j in hits[:3]:
            d = derivs[i]
            ex.append({"w": d["w"], "slp": d["slp"], "recipe": d["recipe"], "steps": d["steps"], "at": j})
        shards.setdefault(f"{parts[0]}.{parts[1]}", {})[code] = {"n": len(hits), "ex": ex}
    viewable = [d for d in derivs if d["recipe"] in core]
    for d in viewable:
        words.append([d["w"], d["slp"], d["recipe"]])
    meta = {"schema": "tajziya.generation/1", "engine": "vidyut-prakriya 0.4.0 (MIT)", "derivations": len(derivs),
            "viewable": len(viewable),
            "recipes": len(recipes), "sutras_acting": sum(len(s) for s in shards.values())}
    dump = lambda x: json.dumps(x, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n"
    files = {os.path.join(OUT, f"{k}.json"): dump(v) for k, v in shards.items()}
    files[os.path.join(OUT, "index.json")] = dump({"meta": meta, "words": words})
    # each derivation in full, in 64 buckets by its word, for the learning page's derivation viewer
    buckets = {}
    for d in viewable:
        b = hashlib.sha256(d["w"].encode()).hexdigest()[:2]
        b = format(int(b, 16) % 64, "02d")
        buckets.setdefault(b, []).append(d)
    for b, ds in buckets.items():
        files[os.path.join(OUT, "words", f"{b}.json")] = dump(ds)
    return files, meta


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="vidyut's data directory (vidyut.download_data writes it)")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    try:
        files, meta = build(a.data)
    except ImportError:
        print("derivations: cannot judge, vidyut is not installed here (pip install vidyut==0.4.0)")
        return 3
    if a.check:
        stale = [os.path.relpath(p, ROOT) for p, t in files.items()
                 if not os.path.exists(p) or open(p, encoding="utf-8").read() != t]
        print("derivations: current" if not stale else f"derivations: STALE, {len(stale)} file(s)")
        return 0 if not stale else 1
    os.makedirs(os.path.join(OUT, "words"), exist_ok=True)
    for p, t in files.items():
        open(p, "w", encoding="utf-8").write(t)
    print(f"derivations: {meta['derivations']} derivations from {meta['recipes']} recipes; {meta['sutras_acting']} sutras act in them")
    return 0


if __name__ == "__main__":
    sys.exit(main())
