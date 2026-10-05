# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""Work packets: small, self-contained pieces of work any AI or person can pick up.

Each packet is packets/<ID>.json. It names its inputs, the files it must produce, its licence
rule, and an acceptance check of a named kind. The check is mechanical: a pull request that
completes a packet is judged by `python3 -m tajziya packet check <ID>` and by the gate, so no
reviewer, human or AI, has to read it to know whether it is done.

Results: PASS, FAIL, or UNJUDGED (exit 3) when the check needs a tool this machine lacks.
"""
import csv
import glob
import hashlib
import json
import os
import shutil
import subprocess
import unicodedata

from .registry import load, path

SCHEMA = "tajziya.packet/1"
STATUSES = ("open", "claimed", "in-review", "done")
AREAS = ("romenagri", "scripts", "translation", "interpretation-traditional", "interpretation-schools",
         "interpretation-academic", "implementation", "corpus")
REQUIRED = ("schema", "id", "title", "area", "wave", "size", "status", "summary", "inputs", "outputs",
            "licence", "acceptance", "depends", "how")
MOD = path("modules", "cls")


def all_packets():
    out = {}
    for p in sorted(glob.glob(path("packets", "*.json"))):
        with open(p, encoding="utf-8") as fh:
            d = json.load(fh)
        out[d.get("id", os.path.basename(p))] = d
    return out


def sha(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def sutra_ids():
    with open(os.path.join(MOD, "data", "ashtadhyayi", "sutraani.tsv"), encoding="utf-8") as fh:
        next(fh)
        return [l.split("\t", 1)[0] for l in fh]


def _policy():
    with open(path("registry", "licences.json"), encoding="utf-8") as fh:
        return json.load(fh)


def _source(sid):
    with open(os.path.join(MOD, "data", "SOURCES.json"), encoding="utf-8") as fh:
        return next((s for s in json.load(fh)["sources"] if s["id"] == sid), None)


# ------------------------------------------------------------------ the kinds of acceptance

def v_sutra_table(a):
    """A TSV keyed by sutra id: the right columns, real ids, NFC text, pinned, and licensed."""
    p, f = [], path(*a["path"].split("/"))
    if not os.path.isfile(f):
        return "FAIL", [f"{a['path']} does not exist"]
    with open(f, encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    cols = rows[0].keys() if rows else []
    p += [f"column {c} is missing" for c in a["columns"] if c not in cols]
    ids, seen = set(sutra_ids()), set()
    for r in rows:
        if r.get("id") not in ids:
            p.append(f"{r.get('id')} is not a sutra"); continue
        if r["id"] in seen and not a.get("multi"):
            p.append(f"{r['id']} appears twice")
        seen.add(r["id"])
        for c, v in r.items():
            if v and unicodedata.normalize("NFC", v) != v:
                p.append(f"{r['id']} {c} is not NFC")
            if c in a.get("max_chars", {}) and v and len(v) > a["max_chars"][c]:
                p.append(f"{r['id']} {c} is longer than {a['max_chars'][c]} characters")
        if "text" in r and not (r["text"] or "").strip():
            p.append(f"{r['id']} has no text")
    if len(seen) < a.get("min_rows", 1):
        p.append(f"{len(seen)} sutras covered; the packet asks for at least {a['min_rows']}")
    s = _source(a["source_id"])
    if s is None:
        p.append(f"modules/cls/data/SOURCES.json has no source {a['source_id']}")
    elif a.get("own_work"):
        if not s.get("citation"):
            p.append(f"source {a['source_id']} gives no citation for the work indexed")
    else:
        rel = os.path.relpath(f, MOD).replace(os.sep, "/")
        pins = {x["path"]: x["sha256"] for x in s.get("files", [])}
        if pins.get(rel) != sha(f):
            p.append(f"source {a['source_id']} does not pin {rel} at its current sha256")
        pol = _policy()
        if s.get("licence") in pol["notice_required"]:
            if not os.path.isfile(os.path.join(MOD, s.get("licence_file") or "-")):
                p.append(f"{s['licence']} needs its notice at {s.get('licence_file')}")
        elif s.get("licence") not in pol["allowed"]:
            p.append(f"licence {s.get('licence')} is not allowed by registry/licences.json")
    return ("FAIL" if p else "PASS"), p[:20]


def v_implementation_map(a):
    """Sutra to file and line: real sutras, real files, lines that exist."""
    p, f = [], path(*a["path"].split("/"))
    if not os.path.isfile(f):
        return "FAIL", [f"{a['path']} does not exist"]
    with open(f, encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    ids = set(sutra_ids())
    for c in ("id", "file", "line", "function", "applies"):
        if rows and c not in rows[0]:
            p.append(f"column {c} is missing")
    root = path(*a.get("root", ".").split("/"))
    if not os.path.isdir(root):
        return "UNJUDGED", [f"{a.get('root')} is not checked out here; make deps fetches it"]
    for r in rows:
        if r.get("id") not in ids:
            p.append(f"{r.get('id')} is not a sutra"); continue
        target = os.path.join(root, r["file"])
        if not os.path.isfile(target):
            p.append(f"{r['id']}: {r['file']} does not exist"); continue
        n = sum(1 for _ in open(target, encoding="utf-8", errors="replace"))
        if not r["line"].isdigit() or not 1 <= int(r["line"]) <= n:
            p.append(f"{r['id']}: line {r['line']} is not in {r['file']}")
        if not (r.get("applies") or "").strip():
            p.append(f"{r['id']}: says nothing about what is applied")
    if len(rows) < a.get("min_rows", 1):
        p.append(f"{len(rows)} rows; the packet asks for at least {a['min_rows']}")
    return ("FAIL" if p else "PASS"), p[:20]


def v_script_table(a):
    """A table on Romenagri's ACII pivot for one script: its own characters, one to one, and a
    lossless round trip of every sutra's ACII through it."""
    from . import romenagri
    p, f = [], path(*a["path"].split("/"))
    if not os.path.isfile(f):
        return "FAIL", [f"{a['path']} does not exist"]
    want = tuple(int(x) for x in str(a.get("min_unicode") or "0").split(".")[:2] if x.isdigit())
    have = tuple(int(x) for x in unicodedata.unidata_version.split(".")[:2])
    if want and have < want:
        return "UNJUDGED", [f"this Python knows Unicode {unicodedata.unidata_version}; {a['path']} needs {a['min_unicode']}"]
    with open(f, encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    fwd, back = {}, {}
    for r in rows:
        try:
            b = int(r["acii"], 16)
        except (KeyError, ValueError):
            p.append(f"bad acii value {r.get('acii')}"); continue
        ch = r.get("char") or ""
        for c in ch:
            if a["unicode_name"].replace("-", " ") not in unicodedata.name(c, "").replace("-", " "):
                p.append(f"{r['acii']}: {c!r} is not a {a['unicode_name']} character")
        if b in fwd:
            p.append(f"{r['acii']} appears twice")
        if ch in back:
            p.append(f"{ch!r} is given to two ACII values")
        fwd[b], back[ch] = ch, b
    if p:
        return "FAIL", p[:20]
    why = romenagri.build()
    if why:
        return "UNJUDGED", [f"the round trip needs Romenagri built here ({why})"]
    unmapped, lost = 0, 0
    with open(os.path.join(MOD, "data", "ashtadhyayi", "sutraani.tsv"), encoding="utf-8") as fh:
        next(fh)
        texts = [l.split("\t")[6] for l in fh]
    for acii in romenagri.acii_lines(texts):
        out = []
        for b in acii:
            if b < 0x80:
                out.append(chr(b))
            elif b in fwd:
                out.append(fwd[b])
            else:
                unmapped += 1
        s = "".join(out)
        again, i, keys = bytearray(), 0, sorted(back, key=len, reverse=True)
        while i < len(s):
            for k in keys:
                if k and s.startswith(k, i):
                    again.append(back[k]); i += len(k); break
            else:
                again.append(ord(s[i]) if ord(s[i]) < 0x80 else 0x3F); i += 1
        if bytes(again) != bytes(b for b in acii if b < 0x80 or b in fwd):
            lost += 1
    if unmapped:
        p.append(f"{unmapped} ACII bytes in the sutras have no {a['unicode_name']} character in the table")
    if lost:
        p.append(f"{lost} sutras do not come back to the same ACII")
    return ("FAIL" if p else "PASS"), p


def v_romenagri_pin(a):
    """The vendored Romenagri brings every sutra back to the same Devanagari."""
    from . import romenagri
    why = romenagri.build(force=True)
    if why:
        return "UNJUDGED", [f"Romenagri cannot be built here ({why})"]
    with open(os.path.join(MOD, "data", "ashtadhyayi", "sutraani.tsv"), encoding="utf-8") as fh:
        next(fh)
        texts = [l.split("\t")[6] for l in fh]
    back = romenagri.devanagari_lines(romenagri.roman_lines(texts))
    nf = lambda s: unicodedata.normalize("NFC", s)
    same = sum(1 for x, y in zip(texts, back) if nf(x) == nf(y))
    return ("PASS" if same >= a["expect_same"] else "FAIL"), [f"{same} of {len(texts)} come back the same"]


def v_wasm_parity(a):
    """The browser build gives the C build's output byte for byte on every sutra."""
    from . import romenagri
    js = path(*a["js"].split("/"))
    if not os.path.isfile(js):
        return "FAIL", [f"{a['js']} does not exist"]
    if shutil.which("node") is None:
        return "UNJUDGED", ["node is not installed here"]
    why = romenagri.build()
    if why:
        return "UNJUDGED", [f"the C build is needed to compare against ({why})"]
    with open(os.path.join(MOD, "data", "ashtadhyayi", "sutraani.tsv"), encoding="utf-8") as fh:
        next(fh)
        texts = [l.split("\t")[6] for l in fh]
    want = romenagri.roman_lines(texts)
    r = subprocess.run(["node", js, "--roman"], input="\n".join(texts) + "\n", capture_output=True, text=True)
    got = r.stdout.replace("\r", "").split("\n")[:len(texts)]
    diff = sum(1 for x, y in zip(want, got) if x != y) + abs(len(want) - len(got))
    return ("PASS" if r.returncode == 0 and diff == 0 else "FAIL"), [f"{diff} sutras differ from the C build"]


def v_corpus(a):
    """C1 to C5 and C8 of the corpus work order, on corpus/<node>/."""
    d = path("corpus", a["node"])
    p = []
    for f in ("units.jsonl", "SOURCES.json", "README.md"):
        if not os.path.isfile(os.path.join(d, f)):
            p.append(f"corpus/{a['node']}/{f} does not exist")
    if p:
        return "FAIL", p
    with open(os.path.join(d, "SOURCES.json"), encoding="utf-8") as fh:
        srcs = {s["id"]: s for s in json.load(fh).get("sources", [])}
    pol = _policy()
    for s in srcs.values():
        for k in ("url", "retrieved", "licence"):
            if not s.get(k):
                p.append(f"source {s.get('id')} lacks {k}")
        local = s.get("local_only")
        for x in s.get("files", []):
            fp = os.path.join(d, x["path"])
            if local and os.path.exists(fp):
                p.append(f"{x['path']} is local_only but sits in the tree")
            if not local and (not os.path.exists(fp) or sha(fp) != x["sha256"]):
                p.append(f"{x['path']} is missing or differs from its pin")
        if not local and s.get("licence") not in pol["allowed"] + pol["notice_required"]:
            p.append(f"source {s.get('id')}: licence {s.get('licence')} is not allowed in the tree")
    seen, n = set(), 0
    with open(os.path.join(d, "units.jsonl"), encoding="utf-8") as fh:
        for i, line in enumerate(fh, 1):
            try:
                u = json.loads(line)
            except ValueError:
                p.append(f"line {i} is not JSON"); continue
            n += 1
            for k in ("id", "node", "source", "locator", "text"):
                if not u.get(k):
                    p.append(f"line {i} lacks {k}")
            if u.get("source") and u["source"] not in srcs:
                p.append(f"line {i} names an unlisted source {u['source']}")
            if u.get("text") and unicodedata.normalize("NFC", u["text"]) != u["text"]:
                p.append(f"line {i} text is not NFC")
            if u.get("id") in seen:
                p.append(f"unit {u.get('id')} appears twice")
            seen.add(u.get("id"))
    readme = open(os.path.join(d, "README.md"), encoding="utf-8").read()
    if f"units: {n}" not in readme:
        p.append(f"README.md does not state 'units: {n}'")
    return ("FAIL" if p else "PASS"), p[:20]


KINDS = {"sutra-table": v_sutra_table, "implementation-map": v_implementation_map, "script-table": v_script_table,
         "romenagri-pin": v_romenagri_pin, "wasm-parity": v_wasm_parity, "corpus": v_corpus}


def problems(pk):
    """Is the packet itself well formed?"""
    p = [f"{pk.get('id')}: lacks {k}" for k in REQUIRED if k not in pk]
    if p:
        return p
    if pk["schema"] != SCHEMA:
        p.append(f"{pk['id']}: schema is not {SCHEMA}")
    if pk["status"] not in STATUSES:
        p.append(f"{pk['id']}: status {pk['status']} is not one of {', '.join(STATUSES)}")
    if pk["area"] not in AREAS:
        p.append(f"{pk['id']}: area {pk['area']} is not one of {', '.join(AREAS)}")
    if pk["acceptance"].get("kind") not in KINDS:
        p.append(f"{pk['id']}: acceptance kind {pk['acceptance'].get('kind')} is unknown")
    return p


def check(pid, packets=None):
    packets = packets or all_packets()
    pk = packets[pid]
    probs = problems(pk)
    if probs:
        return "FAIL", probs
    return KINDS[pk["acceptance"]["kind"]](pk["acceptance"]["args"])


def changed(base):
    """The packets a change touches: their own JSON, or any file they produce."""
    r = subprocess.run(["git", "diff", "--name-only", f"{base}...HEAD"], cwd=path(), capture_output=True, text=True)
    files = [f for f in r.stdout.split() if f]
    out = []
    for pid, pk in all_packets().items():
        mine = [f"packets/{pid}.json"] + pk.get("outputs", [])
        if any(f == o or f.startswith(o.rstrip("/") + "/") for f in files for o in mine):
            out.append(pid)
    return out
