#!/usr/bin/env python3
# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""Generate docs/data/registry.json and the page's copies of the parser's JavaScript.

    python3 tools/site_gen.py            write
    python3 tools/site_gen.py --check    exit 1 when anything committed differs from what
                                         would be written, so a stale page fails the gate
"""
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from tajziya import commonalities, elimination, harness, reconcile  # noqa: E402
from tajziya.registry import Registry  # noqa: E402

JS = ("sandhi.js", "lexicon.js", "pipeline.js")
SOURCES = ("registry/families.json", "registry/nodes.json", "registry/scripts.json", "registry/engines.json",
           "registry/bindings.json", "registry/conflicts.json", "registry/coverage.json",
           "registry/corpus_classes.json", "roadmap/packages.json")


def build():
    reg = Registry()
    m = elimination.minimum(reg)
    conf = harness.run_all(reg)
    rc = reconcile.reconcile(reg)
    src = []
    for f in SOURCES:
        with open(os.path.join(ROOT, f), "rb") as fh:
            src.append({"file": f, "sha256": hashlib.sha256(fh.read()).hexdigest()})
    data = {
        "schema": "tajziya.site/1", "generated_from": src,
        "counts": {"nodes": len(reg.nodes), "lineages": len(reg.lineages), "families": len(reg.families),
                   "scripts": len(reg.scripts), "engines": len(reg.engines), "packages": len(reg.packages),
                   "parsing": sorted(n for n, x in reg.nodes.items() if x["layers"]["L3s"] == "built")},
        "families": reg.families_doc["families"], "lineages": reg.families_doc["lineages"],
        "nodes": [{k: n[k] for k in ("id", "name", "lineage", "iso639_3", "stage", "scripts", "status",
                                     "corpus", "layers")} | ({"note": n["note"]} if "note" in n else {})
                  | ({"scope_excludes": n["scope_excludes"]} if "scope_excludes" in n else {})
                  | {"needs": [e for pair in [reg.engines_of(n)] for e in pair[0] + pair[1]]}
                  for n in reg.nodes_doc["nodes"]],
        "engines": commonalities.report(reg),
        "cuneiform": {"sumero_akkadian": commonalities.script_reach(reg, ["Xsux"]),
                      "all": commonalities.script_reach(reg, ["Xsux", "Xpeo", "Ugar"])},
        "minimum": {"L": len(m["L"]), "S": len(m["S"]["nodes"]), "corpus_objects": len(m["corpus_objects"]),
                    "G": m["G"], "C": m["C"], "certified": m["certified"], "reasons": m["reasons"],
                    "comparison": {k: len(v) for k, v in m["comparison"].items()}},
        "conflicts": reg.conflicts,
        "packages": [{k: p[k] for k in ("id", "title", "labels", "deps")} for p in reg.packages.values()],
        "conformance": {"nodes": conf["nodes"], "findings": conf["findings"], "failed": len(conf["failed"])},
        "reconcile": {"prior_rows": rc["prior_rows"], "matched": rc["matched"],
                      "outside_posters": len(rc["outside_posters"]),
                      "family_differs": [(x["prior"], x["prior_family"]) for x in rc["family_differs"]]},
    }
    files = {"docs/data/registry.json": json.dumps(data, ensure_ascii=False, indent=1, sort_keys=True) + "\n"}
    from tajziya import packets as _packets
    from urllib.parse import quote
    pk = []
    for pid, x in _packets.all_packets().items():
        body = (f"I am taking packet {pid}: {x['title']}.\n\nAcceptance: {x['acceptance']['command']}\n"
                f"Outputs: {', '.join(x['outputs'])}\n\nI will open a pull request when the command passes.")
        pk.append({k: x[k] for k in ("id", "title", "area", "wave", "size", "status", "summary", "outputs", "licence", "how")}
                  | {"command": x["acceptance"]["command"],
                     "claim": "https://github.com/zistgah/tajziya/issues/new?title=" + quote(f"Claim {pid}: {x['title']}")
                              + "&body=" + quote(body)})
    cov = {"languages": len(reg.coverage_ids()), "scripts": len(reg.ilm_scripts), "poster_nodes": len(reg.nodes)}
    files["docs/data/packets.json"] = json.dumps({"schema": "tajziya.site-packets/1", "coverage": cov, "packets": pk},
                                                  ensure_ascii=False, indent=1) + "\n"
    for f in JS:
        with open(os.path.join(ROOT, "vendor", "sanskrit_parser", "js", f), encoding="utf-8") as fh:
            files[f"docs/vendor/{f}"] = fh.read()
    return files


def main(argv):
    files = build()
    if "--check" in argv:
        stale = []
        for rel, text in files.items():
            p = os.path.join(ROOT, rel)
            if not os.path.exists(p):
                stale.append(rel)
                continue
            with open(p, encoding="utf-8") as fh:
                if fh.read() != text:
                    stale.append(rel)
        for s in stale:
            print("STALE", s)
        print(f"site: {'current' if not stale else str(len(stale)) + ' file(s) stale; run python3 tools/site_gen.py'}")
        return 1 if stale else 0
    for rel, text in files.items():
        p = os.path.join(ROOT, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(text)
    print(f"site: {len(files)} file(s) written")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
