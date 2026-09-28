# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""The generic acceptance test for a language module: in isolation, then in integration.

    PYTHONPATH=src python3 -m tajziya accept <module directory> [--integration] [--scratch DIR] [--json]

A1 manifest     the schema, the API version, a known node, the six layers, honest states
A2 tree         conventional entries only; no build artefacts; no script naming a path outside
A3 licences     every data file listed with URL, retrieval date, SHA-256 and an allowed licence;
                a notice for licences that require one; restricted material local-only
A4 references   every built or wired layer cites attested examples from listed sources
A5 isolation    the conformance harness on the module alone, with its own references
A6 integration  bound in a scratch copy of the repository, doctor and full conformance pass

Exit 0 accepted, 1 refused, 3 cannot judge.
"""
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

from . import api, harness, ledger, modules, quests
from .registry import ROOT, load, path

CONVENTIONAL = {"module.json", "README.md", "CONTRACT.md", "CONTRIBUTING.md", "accept.sh", ".gitignore",
                "python", "js", "data", "reference", "tests", "cyclers", "quest", "ledger.py", "runs",
                "logs", ".deps"}
LOCAL_ONLY = ("logs", ".deps")
OUTSIDE = re.compile("\\$HO" + "ME|~" + "/|/t" + "mp|\\.\\." + "/")
SCRIPT = (".py", ".sh", ".js", ".mjs")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _sha(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def _walk(module_dir):
    for base, dirs, files in os.walk(module_dir):
        rel = os.path.relpath(base, module_dir)
        top = rel.split(os.sep)[0]
        if top in LOCAL_ONLY:
            dirs[:] = []
            continue
        for f in files:
            yield os.path.normpath(os.path.join(rel, f))
        for d in dirs:
            yield os.path.normpath(os.path.join(rel, d)) + os.sep


def a2_tree(module_dir):
    p = []
    for entry in sorted(os.listdir(module_dir)):
        if entry not in CONVENTIONAL:
            p.append(f"unexpected entry {entry} at the top of the module")
    for rel in _walk(module_dir):
        name = rel.rstrip(os.sep)
        if "__pycache__" in name.split(os.sep) or name.endswith((".pyc", ".tar.gz")):
            p.append(f"build artefact {name}")
            continue
        if rel.endswith(os.sep) or not name.endswith(SCRIPT):
            continue
        with open(os.path.join(module_dir, name), encoding="utf-8", errors="replace") as fh:
            for n, line in enumerate(fh, 1):
                if OUTSIDE.search(line):
                    p.append(f"{name}:{n} names a path outside the module")
    return p


def a3_licences(module_dir, man, policy):
    p, notes = [], []
    sp = os.path.join(module_dir, man["sources"])
    with open(sp, encoding="utf-8") as fh:
        doc = json.load(fh)
    listed, ids = {}, set()
    for s in doc.get("sources", []):
        sid = s.get("id", "?")
        ids.add(sid)
        miss = [k for k in ("id", "title", "url", "retrieved", "licence", "attribution", "files") if k not in s]
        if miss:
            p.append(f"source {sid} lacks {', '.join(miss)}")
            continue
        if not DATE.match(str(s["retrieved"])):
            p.append(f"source {sid}: retrieved must be YYYY-MM-DD, not {s['retrieved']}")
        lic = policy["normalise"].get(s["licence"], s["licence"])
        restricted = any(re.search(rf"(^|[-\s]){re.escape(k)}($|[-\s])", lic, re.I) for k in ("NC", "ND")) or \
            any(k.lower() in str(s.get("terms", "")).lower() for k in policy["restricted_markers"] if len(k) > 2)
        local = bool(s.get("local_only"))
        if not local and (lic not in policy["allowed"] or restricted):
            p.append(f"source {sid}: licence {s['licence']} is not allowed in the tree; keep it local-only under "
                     "data/local/ or use an openly licensed alternative")
        if not local and lic in policy["notice_required"]:
            nf = s.get("licence_file")
            if not nf or not os.path.isfile(os.path.join(module_dir, nf)):
                p.append(f"source {sid}: {lic} requires its notice; licence_file is missing")
        for f in s["files"]:
            rel = os.path.normpath(f.get("path", ""))
            if local:
                if not rel.startswith(os.path.join("data", "local") + os.sep):
                    p.append(f"source {sid} is local-only, so {rel} must sit under data/local/")
                full = os.path.join(module_dir, rel)
                if os.path.exists(full) and _sha(full) != f.get("sha256"):
                    p.append(f"source {sid}: local copy {rel} does not match its pin")
                continue
            listed[rel] = sid
            full = os.path.join(module_dir, rel)
            if not os.path.isfile(full):
                p.append(f"source {sid}: {rel} is listed and absent")
            elif _sha(full) != f.get("sha256"):
                p.append(f"source {sid}: {rel} has sha256 {_sha(full)}, not the listed {f.get('sha256')}")
    data_dir = os.path.join(module_dir, "data")
    if os.path.isdir(data_dir):
        for base, dirs, files in os.walk(data_dir):
            for f in files:
                rel = os.path.normpath(os.path.relpath(os.path.join(base, f), module_dir))
                if rel == os.path.normpath(man["sources"]) or rel.startswith(os.path.join("data", "LICENSES") + os.sep) \
                        or rel.startswith(os.path.join("data", "local") + os.sep):
                    continue
                if rel not in listed:
                    p.append(f"{rel} is in data/ and listed by no source")
    if os.path.isdir(os.path.join(data_dir, "local")):
        gi = os.path.join(module_dir, ".gitignore")
        text = open(gi, encoding="utf-8").read() if os.path.exists(gi) else ""
        if "data/local/" not in text:
            p.append("data/local/ holds local-only material and .gitignore does not exclude it")
    notes.append(f"{len(ids)} source(s), {len(listed)} data file(s) listed")
    return p, notes, ids


def a4_references(module_dir, man, ids, reg):
    p, notes = [], []
    rp = os.path.join(module_dir, man["reference"])
    with open(rp, encoding="utf-8") as fh:
        examples = json.load(fh).get("examples", [])
    node = reg.node(man["node"])
    allowed_scripts = set(man["accepts"]) | set(node["scripts"])
    for i, e in enumerate(examples):
        tag = f"example {i + 1}"
        if e.get("layer") not in man["layers"]:
            p.append(f"{tag}: layer {e.get('layer')} is not one of the six")
        if e.get("source") not in ids:
            p.append(f"{tag}: source {e.get('source')} is not listed in {man['sources']}")
        if not e.get("locator"):
            p.append(f"{tag}: no locator says where in the source it is attested")
        if e.get("layer") == "L3s" and not e.get("readings"):
            p.append(f"{tag}: a segmentation example states its readings")
        counts, _ = api.detect_scripts(str(e.get("input", "")), reg)
        extra = sorted(set(counts) - allowed_scripts)
        if extra:
            p.append(f"{tag}: input is in {', '.join(extra)}, which the module does not accept")
    for L, st in man["layers"].items():
        if st == "not_built" or L == "L2":
            continue
        n = sum(1 for e in examples if e.get("layer") == L)
        notes.append(f"{L} {st}: {n} attested example(s)")
        if n == 0:
            p.append(f"{L} is {st} and cites no attested example")
    if not [L for L, st in man["layers"].items() if st != "not_built" and L != "L2"]:
        notes.append("no layer is built yet; every layer refuses")
    return p, notes


def a5_isolation(module_dir, man, reg):
    p = []
    port = modules.bind(module_dir, reg)
    if port.layers() != man["layers"]:
        p.append("the port reports layer states its module.json does not declare")
    node = dict(reg.node(man["node"]))
    node["layers"] = dict(man["layers"])
    for cond, ok, detail in harness.check(port, node, reg):
        if not ok:
            p.append(f"{cond}: {detail}")
    return p


def _copy(src, dst, skip):
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns(*skip))


def a6_integration(module_dir, man, scratch):
    node = man["node"]
    here = os.path.realpath(os.path.join(ROOT, "modules", node))
    bound_in_place = os.path.realpath(module_dir) == here
    root = ROOT
    if not bound_in_place:
        if not scratch:
            return ["integration needs --scratch, a folder inside the one this runs in"], []
        scratch = os.path.realpath(scratch)
        if os.path.exists(scratch):
            shutil.rmtree(scratch)
        _copy(ROOT, scratch, (".git", ".deps", ".scratch", "packs", "logs", "__pycache__"))
        dest = os.path.join(scratch, "modules", node)
        if os.path.exists(dest):
            shutil.rmtree(dest)
        _copy(module_dir, dest, (".deps", "logs", "__pycache__", ".git"))
        with open(os.path.join(scratch, "registry", "bindings.json"), encoding="utf-8") as fh:
            b = json.load(fh)
        b["bindings"][node] = {"kind": "module", "implementation": man["implementation"], "module": f"modules/{node}"}
        with open(os.path.join(scratch, "registry", "bindings.json"), "w", encoding="utf-8") as fh:
            json.dump(b, fh, indent=1, ensure_ascii=False)
            fh.write("\n")
        with open(os.path.join(scratch, "registry", "nodes.json"), encoding="utf-8") as fh:
            nd = json.load(fh)
        for n in nd["nodes"]:
            if n["id"] == node:
                n["layers"] = dict(man["layers"])
                if man["scope_excludes"]:
                    n["scope_excludes"] = list(man["scope_excludes"])
        with open(os.path.join(scratch, "registry", "nodes.json"), "w", encoding="utf-8") as fh:
            json.dump(nd, fh, indent=1, ensure_ascii=False)
            fh.write("\n")
        root = scratch
    env = dict(os.environ, PYTHONPATH=os.path.join(root, "src"), PYTHONDONTWRITEBYTECODE="1")
    p = []
    for verb in ("doctor", "conformance"):
        r = subprocess.run([sys.executable, "-m", "tajziya", verb], cwd=root, env=env, capture_output=True, text=True)
        if r.returncode != 0:
            p.append(f"{verb} fails with the module bound: " + " | ".join((r.stdout + r.stderr).strip().splitlines()[-3:]))
    where = "in place" if bound_in_place else os.path.relpath(root, os.path.dirname(os.path.realpath(module_dir)))
    return p, [f"bound {where}; doctor and full conformance run"]


def a7_record(module_dir):
    """His step 3: the quest painting is valid and the configuration record has not been altered."""
    p, notes = [], []
    q = os.path.join(module_dir, "quest", "aab-painting.json")
    if os.path.isfile(q):
        with open(q, encoding="utf-8") as fh:
            p += [f"quest: {x}" for x in quests.problems(json.load(fh))]
    else:
        notes.append("no quest/aab-painting.json")
    lp = os.path.join(module_dir, "ledger.py")
    if os.path.isfile(lp) and _sha(lp) != _sha(path("src", "tajziya", "ledger.py")):
        p.append("ledger.py is not the core's ledger.py byte for byte")
    entries = ledger.read(module_dir)
    probs = ledger.verify_entries(entries)
    p += [f"record: {x}" for x in probs]
    if entries and not probs:
        notes.append(f"record: {len(entries)} entries, chain intact")
        notes += [f"record: {x}" for x in ledger.status(module_dir, entries)]
    elif not entries:
        notes.append("record: no entries yet")
    return p, notes


def run(module_dir, integration=False, scratch=None):
    module_dir = os.path.realpath(module_dir)
    rows = []

    def row(cid, name, probs, notes=()):
        rows.append({"id": cid, "check": name, "state": "FAIL" if probs else "PASS",
                     "problems": list(probs), "notes": list(notes)})
    reg = load()
    if not os.path.isfile(os.path.join(module_dir, "module.json")):
        return [{"id": "A1", "check": "manifest", "state": "FAIL", "problems": ["no module.json"], "notes": []}]
    man = modules.manifest(module_dir)
    probs = modules.problems(man, reg, module_dir)
    row("A1", "manifest", probs)
    if probs:
        return rows
    row("A2", "tree", a2_tree(module_dir))
    with open(path("registry", "licences.json"), encoding="utf-8") as fh:
        policy = json.load(fh)
    p3, n3, ids = a3_licences(module_dir, man, policy)
    row("A3", "licences", p3, n3)
    p4, n4 = a4_references(module_dir, man, ids, reg)
    row("A4", "references", p4, n4)
    try:
        row("A5", "isolation", a5_isolation(module_dir, man, reg))
    except Exception as e:
        row("A5", "isolation", [f"the module does not load or run: {type(e).__name__}: {e}"])
    if integration:
        if any(r["state"] == "FAIL" for r in rows):
            rows.append({"id": "A6", "check": "integration", "state": "NOT RUN",
                         "problems": [], "notes": ["isolation failed first"]})
        else:
            p6, n6 = a6_integration(module_dir, man, scratch)
            row("A6", "integration", p6, n6)
    p7, n7 = a7_record(module_dir)
    row("A7", "quest and record", p7, n7)
    return rows


def main(a):
    rows = run(a.module, a.integration, a.scratch)
    if a.json:
        print(json.dumps({"module": os.path.basename(os.path.realpath(a.module)), "checks": rows,
                          "at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")},
                         ensure_ascii=False, indent=1))
    else:
        print(f"accept: {os.path.basename(os.path.realpath(a.module))}")
        for r in rows:
            print(f"  {r['state']:8} {r['id']}  {r['check']}")
            for x in r["problems"]:
                print(f"           {x}")
            for x in r["notes"]:
                print(f"           note: {x}")
    return 1 if any(r["state"] == "FAIL" for r in rows) else 0
