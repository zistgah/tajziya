# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""tajziya on the command line: PYTHONPATH=src python3 -m tajziya <verb>

Exit 0 answered, 1 refused or failed, 3 cannot judge (a layer is not built, or data is absent).
"""
import argparse
import hashlib
import json
import os
import sys
import zipfile

from . import commonalities, conllu, doctor, elimination, harness, reconcile
from ._vendor.unknown import Unknown
from .registry import load, path
from .types import LAYER_NAMES, NotBuilt


def _nodes(reg, a):
    for n in reg.nodes.values():
        if a.lineage and n["lineage"] != a.lineage:
            continue
        if a.status and n["status"]["poster"] != a.status:
            continue
        built = [L for L, s in n["layers"].items() if s == "built"]
        print(f"{n['id']:10} {n['status']['poster']}  {n['lineage']:15} {n['name']:28} "
              f"{','.join(n['scripts']):22} {'parses: ' + ','.join(built) if built else 'stub'}")
    return 0


def _segment(reg, a):
    p = reg.bind(a.node)
    try:
        res = p.segment(" ".join(a.text))
    except NotBuilt as e:
        print(e)
        return 3
    if a.conllu:
        blocks = conllu.sentences(res)
        if isinstance(blocks, Unknown):
            print(blocks)
            return 3
        print("\n".join(blocks), end="")
        return 0
    for lat in res.tokens:
        if not lat.alternatives:
            print(f"{lat.token}: no segmentation found in the lexicon")
        for k, s in enumerate(lat.alternatives, 1):
            j = "; ".join(f"{x.left}+{x.right}>{x.merged}" for x in s.junctions) or "no junction"
            print(f"{lat.token}: reading {k} of {len(lat.alternatives)}: {' + '.join(s.words)}  [{j}]")
    return 0


def _data_import(reg, a):
    with open(path("modules", "cls", "data", "SOURCES.json"), encoding="utf-8") as fh:
        local = next(s for s in json.load(fh)["sources"] if s.get("local_only"))
    src = {"file": os.path.basename(local["files"][0]["path"]), "sha256": local["files"][0]["sha256"],
           "entries": local["entries"], "local_path": "modules/cls/" + local["files"][0]["path"]}
    src_path = os.path.realpath(a.source)
    if os.path.commonpath([src_path, os.path.realpath(path())]) != os.path.realpath(path()):
        print("data import: refused, the source must sit inside this repository's folder; nothing "
              "outside the folder a script runs in is read (master contract, clause 7)")
        return 1
    if not os.path.exists(src_path):
        print(f"data import: nothing at {os.path.relpath(src_path, path())}")
        return 3
    if zipfile.is_zipfile(src_path):
        z = zipfile.ZipFile(src_path)
        hits = [m for m in z.namelist() if m.endswith("data/" + src["file"])]
        if len(hits) != 1:
            print(f"data import: refused, the archive holds {len(hits)} copies of {src['file']}")
            return 1
        blob = z.read(hits[0])
    else:
        with open(src_path, "rb") as fh:
            blob = fh.read()
    got = hashlib.sha256(blob).hexdigest()
    if got != src["sha256"]:
        print(f"data import: refused, sha256 {got} is not the pinned {src['sha256']}")
        return 1
    dst = path(*src["local_path"].split("/"))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, "wb") as fh:
        fh.write(blob)
    print(f"data import: {src['entries']} sutras written to {src['local_path']}; git ignores this "
          "file and it is never deposited")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="tajziya")
    sub = ap.add_subparsers(dest="verb", required=True)
    d = sub.add_parser("doctor", help="registry integrity")
    d.add_argument("--strict", action="store_true")
    n = sub.add_parser("nodes", help="every language and stage node")
    n.add_argument("--lineage")
    n.add_argument("--status")
    sub.add_parser("lineages", help="lineages, their family and engines")
    c = sub.add_parser("commonalities", help="engines by reach across lineages")
    c.add_argument("--json", action="store_true")
    s = sub.add_parser("segment", help="segment text for a node")
    s.add_argument("--node", required=True)
    s.add_argument("--conllu", action="store_true")
    s.add_argument("text", nargs="+")
    ly = sub.add_parser("layers", help="a node's layer states and what each refusal names")
    ly.add_argument("--node", required=True)
    e = sub.add_parser("eliminate", help="the elimination rule over recorded coverage")
    e.add_argument("--json", action="store_true")
    cf = sub.add_parser("conformance", help="the harness over every bound node")
    cf.add_argument("--json", action="store_true")
    rc = sub.add_parser("reconcile", help="the 30 Aug ILM template against this registry")
    rc.add_argument("--json", action="store_true")
    ru = sub.add_parser("rules", help="the sutra compilation, when a pinned local copy exists")
    ru.add_argument("--node", default="cls")
    pk = sub.add_parser("packet", help="work packets: list them, or run a packet's acceptance check")
    pk.add_argument("action", choices=("list", "check"))
    pk.add_argument("ids", nargs="*")
    pk.add_argument("--all", action="store_true")
    pk.add_argument("--changed", metavar="BASE", help="check the packets a change since BASE touches")
    cv = sub.add_parser("coverage", help="the ILM registry's languages and scripts: counts and conformance")
    cv.add_argument("--sample", type=int, help="judge every n-th coverage language")
    cv.add_argument("--script", action="append", help="judge only this script (repeatable)")
    cv.add_argument("--scripts-only", action="store_true")
    ac = sub.add_parser("accept", help="the generic acceptance test for a language or script module")
    ac.add_argument("module")
    ac.add_argument("--integration", action="store_true")
    ac.add_argument("--scratch")
    ac.add_argument("--json", action="store_true")
    da = sub.add_parser("data", help="import the pinned sutra compilation from a local copy")
    da.add_argument("action", choices=["import"])
    da.add_argument("source")
    a = ap.parse_args(argv)
    reg = load()

    if a.verb == "doctor":
        probs = doctor.problems(reg)
        for p in probs:
            print("FAIL", p)
        print(f"doctor: {len(reg.nodes)} nodes, {len(reg.lineages)} lineages, {len(reg.scripts)} scripts, "
              f"{len(reg.engines)} engines, {len(reg.packages)} packages, {len(probs)} problem(s)")
        return 1 if probs else 0
    if a.verb == "nodes":
        return _nodes(reg, a)
    if a.verb == "lineages":
        for x in reg.lineages.values():
            count = sum(1 for n in reg.nodes.values() if n["lineage"] == x["id"])
            print(f"{x['id']:15} {' > '.join(x['path']):40} {count:2} nodes  "
                  f"{x['morphological_type']:12} {', '.join(x['language_engines']) or '-'}")
        return 0
    if a.verb == "commonalities":
        rep = commonalities.report(reg)
        if a.json:
            print(json.dumps(rep, ensure_ascii=False, indent=1))
            return 0
        for r in rep["engines"]:
            print(f"{r['id']:14} {r['axis']:9} {r['reach']['lineages']:2} lineages {r['reach']['nodes']:3} nodes  "
                  f"{'common' if r['common'] else 'one lineage'}  {', '.join(r['lineages'])}")
        return 0
    if a.verb == "segment":
        return _segment(reg, a)
    if a.verb == "layers":
        p, node = reg.bind(a.node), reg.node(a.node)
        for L, st in p.layers().items():
            line = f"{L:4} {LAYER_NAMES[L]:13} {st}"
            if st == "not_built":
                fn = getattr(p, {"L0": "phonology", "L1": "pivot", "L2": "orthography", "L3s": "segment",
                                 "L3m": "analyse", "L4": "relate"}[L])
                try:
                    fn("probe")
                except NotBuilt as e:
                    line += f"  packages: {', '.join(e.packages)}"
            print(line)
        if node.get("scope_excludes"):
            print("excludes:", "; ".join(node["scope_excludes"]))
        return 0
    if a.verb == "eliminate":
        m = elimination.minimum(reg)
        if a.json:
            print(json.dumps(m, ensure_ascii=False, indent=1))
        else:
            print(f"L: {len(m['L'])} candidate language nodes retained; S: {len(m['S']['nodes'])} stage "
                  f"nodes; corpus objects: {len(m['corpus_objects'])}; G: {len(m['G'])} scripts; "
                  f"C: {', '.join(m['C'])}")
            print("certified:", "yes, " + m["scope"] if m["certified"] else "no; " + "; ".join(m["reasons"]))
            print(f"against the poster: {len(m['comparison']['agrees'])} agree, "
                  f"{len(m['comparison']['unevidenced'])} unevidenced, {len(m['comparison']['differs'])} differ")
        return 0
    if a.verb == "conformance":
        s = harness.run_all(reg)
        if a.json:
            print(json.dumps(s, ensure_ascii=False, indent=1))
        else:
            for f in s["failed"]:
                print(f"FAIL {f['node']} {f['condition']}: {f['detail']}")
            print(f"conformance: {s['nodes']} nodes, {s['findings']} findings, {len(s['failed'])} failed")
        return 1 if s["failed"] else 0
    if a.verb == "reconcile":
        r = reconcile.reconcile(reg)
        if a.json:
            print(json.dumps(r, ensure_ascii=False, indent=1))
            return 0
        print(f"{r['prior_rows']} prior rows from {r['source']}: {r['matched']} agree with a node's lineage, "
              f"{len(r['family_differs'])} differ, {len(r['outside_posters'])} are not poster nodes")
        for x in r["family_differs"]:
            print(f"  {x['prior']}: filed under {x['prior_family']}; here {' > '.join(x['path'])}")
        for k, v in r["one_lineage_several_labels"].items():
            print(f"  lineage {k} carried {len(v)} labels there: {', '.join(v)}")
        return 0
    if a.verb == "rules":
        p = reg.bind(a.node)
        if not hasattr(p, "rules"):
            print(f"{a.node}: this node holds no rule database")
            return 3
        r = p.rules()
        if isinstance(r, Unknown):
            print(r)
            return 3
        print(f"{len(r)} sutras loaded, {r[0].id} to {r[-1].id}; {getattr(p, 'rules_provenance', '')}".rstrip("; "))
        return 0
    if a.verb == "data":
        return _data_import(reg, a)
    if a.verb == "packet":
        from . import packets
        allp = packets.all_packets()
        if a.action == "list":
            for pid, x in allp.items():
                print(f"{pid:22} {x['status']:9} {x['area']:26} {x['title']}")
            return 0
        ids = list(allp) if a.all else (packets.changed(a.changed) if a.changed else a.ids)
        if not ids:
            print("packet: nothing to check"); return 0
        worst = 0
        for pid in ids:
            if pid not in allp:
                print(f"FAIL     {pid}: no such packet"); worst = 1; continue
            if a.all and allp[pid]["status"] != "done":
                probs = packets.problems(allp[pid])
                state = "FAIL" if probs else "PASS"
                print(f"{state:8} {pid}: well formed" + ("" if not probs else ": " + "; ".join(probs))); worst = max(worst, 1 if probs else 0)
                continue
            state, probs = packets.check(pid, allp)
            print(f"{state:8} {pid}" + ("" if not probs else ": " + "; ".join(probs[:3])))
            worst = max(worst, {"PASS": 0, "FAIL": 1, "UNJUDGED": 0}[state])
        return worst
    if a.verb == "coverage":
        failed = []
        if not a.script and not a.scripts_only:
            s = harness.run_coverage(reg, a.sample)
            failed += s["failed"]
            print(f"coverage: {len(reg.coverage_ids())} languages from the ILM registry beyond the {len(reg.nodes)} curated nodes; "
                  f"{s['nodes']} judged, {len(s['failed'])} failed")
        t = harness.run_scripts(reg, a.script)
        failed += t["failed"]
        print(f"coverage: {t['scripts']} of {len(reg.ilm_scripts)} scripts judged, {len(t['failed'])} failed")
        for f in failed[:20]:
            print(f"FAIL {f.get('node') or f.get('script')} {f['condition']}: {f['detail']}")
        return 1 if failed else 0
    if a.verb == "accept":
        from . import accept
        return accept.main(a)
    return 1


if __name__ == "__main__":
    sys.exit(main())
