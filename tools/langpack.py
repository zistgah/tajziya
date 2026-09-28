#!/usr/bin/env python3
# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""Generate language packages: one self-contained, hand-over-ready module per node.

    python3 tools/langpack.py NODE_OR_CODE [...]     named nodes; an ISO 639-3 code names every node carrying it
    python3 tools/langpack.py --remaining            every node still bound to its family frame
    options:  --out DIR   inside this repository, default packs
              --tar       also write dist/tajziya-lang-<node>.tar.gz and dist/INDEX.json
              --bundle    also write dist/tajziya-language-packages.tar.gz holding every package
              --quiet

Each package is templates/langpack filled from the registry. Before anything is written out it
must pass the generic acceptance test, so every package starts in a conforming state. The same
registry always yields the same bytes. Exit 0 all accepted, 1 refused.
"""
import argparse
import gzip
import hashlib
import io
import json
import os
import re
import shutil
import sys
import tarfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from tajziya import accept, quests  # noqa: E402
from tajziya.registry import load  # noqa: E402

TEMPLATE = os.path.join(ROOT, "templates", "langpack")
MTIME = 1790380800  # 2026-09-26T00:00:00Z, so the archives are reproducible
STATUS = {"I": "irreducible", "P": "provisional", "U": "undeciphered or unknown", "S": "stage, not a separate language",
          "C": "candidate for compression"}


def impl_id(node_id):
    return re.sub(r"[^a-z0-9]+", "_", node_id.lower()).strip("_") + "_v0"


def resolve(reg, args, remaining):
    if remaining:
        return [n for n, b in reg.bindings.items() if b["kind"] == "frame"]
    out = []
    for a in args:
        hits = [n for n, x in reg.nodes.items() if a in x["iso639_3"]] or ([a] if a in reg.nodes else [])
        if not hits:
            raise SystemExit(f"langpack: refused, {a} is neither a node id nor an ISO 639-3 code of any node")
        for h in hits:
            b = reg.bindings[h]
            if b["kind"] == "module":
                print(f"langpack: {h} is already a bound module at {b['module']}; that folder is its package")
            elif h not in out:
                out.append(h)
    return out


def fill(text, values):
    for k, v in values.items():
        text = text.replace(f"@@{k}@@", v)
    left = re.findall(r"@@[A-Z_]+@@", text)
    if left:
        raise SystemExit(f"langpack: template placeholder never filled: {left[0]}")
    return text


def values_for(reg, nid, corpora):
    n = reg.node(nid)
    lin = reg.lineages[n["lineage"]]
    fam = reg.families[lin["family"]]
    names = {"L0": "phonology", "L1": "pivot", "L2": "orthography", "L3s": "segment", "L3m": "analyse", "L4": "relate"}
    rows = []
    for L, st in n["layers"].items():
        if st != "not_built":
            rows.append(f"| {L} | `{names[L]}` | {st.replace('_', ' ')} through the common layer | none |")
            continue
        needs, packs = reg.refusal(n, L)
        rows.append(f"| {L} | `{names[L]}` | {', '.join(needs) or 'none named'} | {', '.join(packs)} |")
    notes = []
    if n.get("note"):
        notes.append(f"Note: {n['note']}")
    for k, t in reg.nodes_doc["stage_trees"].items():
        if nid in t["nodes"] and len(t["nodes"]) == 1:
            notes.append(f"Its stage tree (poster III, Axis II): {', '.join(t['stages'])}.")
        elif nid in t["nodes"]:
            notes.append(f"One node of the {k} stage tree (poster III, Axis II): {', '.join(t['stages'])}. "
                         f"This node is the {n['stage']} stage.")
    for c in reg.conflicts:
        if re.search(rf"(^|[^\w-]){re.escape(nid)}([^\w-]|$)", c["held_as"]):
            notes.append(f"Held conflict {c['id']} ({c['where']}): {c['reads']} {c['against']} {c['held_as']}")
    rows_c = corpora.get(nid, [])
    corp = "\n".join(
        f"- [{r['treebank']}]({r['repository']}): {r['licence']}, "
        f"{'allowed in the tree' if r['allowed'] else 'not allowed in the tree'}"
        f"{'' if r['text_included'] else '; its text is not included and has its own terms'}"
        f"{', genre ' + r['genre'] if r.get('genre') else ''}" for r in rows_c) or "None found by language code."
    return n, {
        "NODE": nid, "NAME": n["name"], "IMPL": impl_id(nid), "LANGUAGE": n["language"],
        "STAGE": n["stage"] or "not staged on the posters", "PATH": " > ".join(
            reg.families[p]["name"] if p in reg.families else (reg.lineages[p]["name"] if p in reg.lineages else p)
            for p in lin["path"]) + ("" if fam["kind"] == "family" else f" ({fam['name'].lower()})"),
        "MTYPE": lin["morphological_type"], "ISO": ", ".join(n["iso639_3"]) or "none assigned",
        "SCRIPTS": ", ".join(f"{c} ({reg.scripts[c]['name']})" for c in n["scripts"]),
        "STATUS": n["status"]["poster"], "STATUS_NAME": STATUS[n["status"]["poster"]], "STATUS_SOURCE": n["status"]["source"],
        "CORPUS": n["corpus"], "NOTES": "\n\n".join(notes) or "No note or held conflict names this node.",
        "LAYER_TABLE": "\n".join(rows), "CORPORA": corp,
        "CYCLER": "TAJZIYA_" + impl_id(nid)[:-3].upper()}


def build(reg, nid, out_dir, corpora):
    n, v = values_for(reg, nid, corpora)
    pkg = os.path.join(out_dir, f"tajziya-lang-{nid}")
    if os.path.exists(pkg):
        shutil.rmtree(pkg)
    for base, _, files in os.walk(TEMPLATE):
        for f in files:
            src = os.path.join(base, f)
            rel = fill(os.path.relpath(src, TEMPLATE), v)
            rel = ".gitignore" if rel == "gitignore.template" else rel
            dst = os.path.join(pkg, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with open(src, encoding="utf-8") as fh:
                text = fill(fh.read(), v)
            with open(dst, "w", encoding="utf-8") as fh:
                fh.write(text)
            if dst.endswith(".sh"):
                os.chmod(dst, 0o755)
    lang, script = reg.engines_of(n)
    man = {"schema": "tajziya.module/1", "node": nid, "implementation": v["IMPL"], "api": "1", "version": "0.0.0",
           "layers": dict(n["layers"]), "scope_excludes": [],
           "accepts": [c for c in n["scripts"] if reg.scripts[c]["encoded"]],
           "engines": list(dict.fromkeys(lang + script)), "entry": f"python/{v['IMPL']}/__init__.py",
           "sources": "data/SOURCES.json", "reference": "reference/examples.json", "requires": [],
           "licence": {"code": "GPL-3.0-or-later"}}
    docs = {
        "module.json": man,
        "data/SOURCES.json": {"schema": "tajziya.sources/1",
                              "rule": "Every data file is listed here with its URL, retrieval date, SHA-256 and an "
                                      "allowed licence. Restricted material is local_only and sits in data/local/.",
                              "sources": [], "candidates": corpora.get(nid, [])},
        "reference/examples.json": {"schema": "tajziya.reference/1",
                                    "rule": "Each example is attested in a listed source at the locator given. A "
                                            "segmentation example gives every reading the source admits.",
                                    "examples": []},
        "quest/aab-painting.json": quests.language_layer(reg, nid)}
    shutil.copyfile(os.path.join(ROOT, "src", "tajziya", "ledger.py"), os.path.join(pkg, "ledger.py"))
    for rel, obj in docs.items():
        p = os.path.join(pkg, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as fh:
            json.dump(obj, fh, indent=1, ensure_ascii=False)
            fh.write("\n")
    return pkg


def tar(paths, arc_root, dest):
    raw = io.BytesIO()
    with gzip.GzipFile(fileobj=raw, mode="wb", mtime=0) as gz, tarfile.open(fileobj=gz, mode="w") as t:
        for base_dir, name in paths:
            entries = []
            for b, dirs, files in os.walk(base_dir):
                dirs.sort()
                for f in sorted(files):
                    entries.append(os.path.join(b, f))
            for full in sorted(entries):
                info = tarfile.TarInfo(os.path.join(arc_root, name, os.path.relpath(full, base_dir)) if arc_root
                                       else os.path.join(name, os.path.relpath(full, base_dir)))
                data = open(full, "rb").read()
                info.size, info.mtime, info.uid, info.gid, info.uname, info.gname = len(data), MTIME, 0, 0, "", ""
                info.mode = 0o755 if full.endswith(".sh") else 0o644
                t.addfile(info, io.BytesIO(data))
    with open(dest, "wb") as fh:
        fh.write(raw.getvalue())
    return hashlib.sha256(raw.getvalue()).hexdigest()


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("nodes", nargs="*")
    ap.add_argument("--remaining", action="store_true")
    ap.add_argument("--out", default="packs")
    ap.add_argument("--tar", action="store_true")
    ap.add_argument("--bundle", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)
    out_dir = os.path.realpath(os.path.join(ROOT, a.out))
    if os.path.commonpath([out_dir, ROOT]) != ROOT or out_dir == ROOT:
        print("langpack: refused, --out must be a folder inside this repository (master contract, clause 7)")
        return 1
    reg = load()
    targets = resolve(reg, a.nodes, a.remaining)
    if not targets:
        print("langpack: no node to package")
        return 1
    with open(os.path.join(ROOT, "registry", "corpora.json"), encoding="utf-8") as fh:
        corpora = json.load(fh)["nodes"]
    os.makedirs(out_dir, exist_ok=True)
    failed, index = [], []
    for nid in targets:
        pkg = build(reg, nid, out_dir, corpora)
        rows = accept.run(pkg)
        bad = [f"{r['id']} {x}" for r in rows if r["state"] == "FAIL" for x in r["problems"]]
        if bad:
            failed.append(nid)
            print(f"langpack: {nid} REFUSED by its own acceptance test: {bad[0]}")
            continue
        index.append({"node": nid, "name": reg.node(nid)["name"], "lineage": reg.node(nid)["lineage"],
                      "package": f"tajziya-lang-{nid}"})
        if not a.quiet:
            print(f"langpack: {nid:10} accepted as handed over  {os.path.relpath(pkg, ROOT)}")
    if a.tar or a.bundle:
        dist = os.path.join(out_dir, "dist")
        os.makedirs(dist, exist_ok=True)
        if a.tar:
            for e in index:
                e["sha256"] = tar([(os.path.join(out_dir, e["package"]), e["package"])], "",
                                  os.path.join(dist, e["package"] + ".tar.gz"))
        with open(os.path.join(dist, "INDEX.json"), "w", encoding="utf-8") as fh:
            json.dump({"schema": "tajziya.packs/1", "packages": index}, fh, indent=1, ensure_ascii=False)
            fh.write("\n")
        if a.bundle:
            idx_dir = os.path.join(out_dir, ".index")
            os.makedirs(idx_dir, exist_ok=True)
            shutil.copy(os.path.join(dist, "INDEX.json"), os.path.join(idx_dir, "INDEX.json"))
            sha = tar([(os.path.join(out_dir, e["package"]), e["package"]) for e in index] + [(idx_dir, "")],
                      "tajziya-language-packages", os.path.join(dist, "tajziya-language-packages.tar.gz"))
            shutil.rmtree(idx_dir)
            print(f"langpack: bundle dist/tajziya-language-packages.tar.gz sha256 {sha}")
    print(f"langpack: {len(index)} package(s) accepted as handed over, {len(failed)} refused")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
