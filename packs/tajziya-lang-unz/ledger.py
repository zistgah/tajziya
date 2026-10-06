#!/usr/bin/env python3
# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""The configuration record of a cycle: step 3 of the author's protocol.

    intent, then context, then a meaningful prompt; any AI answers and the human inspects;
    the artifacts and responses are kept under configuration management; the next prompt
    follows, until a final artifact the human authored, carrying its intention.

Every intent, context, prompt, response, decision and artifact version is appended to
runs/ledger.jsonl with its SHA-256, chained to the entry before it. Nothing is overwritten: a
correction is a new entry, and any current state is derived from the record.

    python3 ledger.py add KIND (--text TEXT | --file PATH) [--actor NAME] [--note NOTE]
    python3 ledger.py verify [--strict]    the chain; --strict also every recorded file as it stands
    python3 ledger.py status               files changed since their last recorded version
    python3 ledger.py show [--last N]

KIND is intent, context, prompt, response, decision or artifact. --actor names who produced the
entry; for a response it is the AI the operator names, never one the record asserts for itself.
A package's ledger.py is this file byte for byte, and acceptance check A7 holds it to that.
Exit 0 clean, 1 not clean, 2 usage.
"""
import argparse
import datetime
import hashlib
import json
import os
import sys

KINDS = ("intent", "context", "prompt", "response", "decision", "artifact")
LEDGER = os.path.join("runs", "ledger.jsonl")
GENESIS = "0" * 64


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _canon(entry):
    body = {k: v for k, v in entry.items() if k != "hash"}
    return json.dumps(body, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def read(root="."):
    p = os.path.join(root, LEDGER)
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def verify_entries(entries):
    probs, prev = [], GENESIS
    for i, e in enumerate(entries, 1):
        if e.get("seq") != i:
            probs.append(f"entry {i}: numbered {e.get('seq')}")
        if e.get("prev") != prev:
            probs.append(f"entry {i}: not chained to the entry before it")
        if e.get("kind") not in KINDS:
            probs.append(f"entry {i}: kind {e.get('kind')!r} is not one of {', '.join(KINDS)}")
        if "text" in e and _sha(str(e["text"]).encode("utf-8")) != e.get("sha256"):
            probs.append(f"entry {i}: its text does not match its sha256")
        if _sha(_canon(e)) != e.get("hash"):
            probs.append(f"entry {i}: altered after it was written")
        prev = e.get("hash", "")
    return probs


def status(root, entries):
    last = {}
    for e in entries:
        if "path" in e:
            last[e["path"]] = e.get("sha256")
    out = []
    for rel, sha in sorted(last.items()):
        p = os.path.join(root, rel)
        if not os.path.exists(p):
            out.append(f"{rel}: recorded, now absent")
            continue
        with open(p, "rb") as fh:
            if _sha(fh.read()) != sha:
                out.append(f"{rel}: changed since its last recorded version")
    return out


def verify(root=".", strict=False):
    entries = read(root)
    probs = verify_entries(entries)
    return probs + (status(root, entries) if strict else [])


def append(root, kind, text=None, file=None, actor="", note="", now=None):
    if kind not in KINDS:
        raise ValueError(f"kind {kind!r} is not one of {', '.join(KINDS)}")
    if (text is None) == (file is None):
        raise ValueError("give exactly one of --text or --file")
    entries = read(root)
    probs = verify_entries(entries)
    if probs:
        raise ValueError(f"the ledger does not verify, so nothing was appended: {probs[0]}")
    e = {"seq": len(entries) + 1, "kind": kind, "actor": actor, "note": note,
         "time": now or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
         "prev": entries[-1]["hash"] if entries else GENESIS}
    if file is not None:
        rel = os.path.normpath(file)
        if os.path.isabs(rel) or rel.split(os.sep)[0] == os.pardir:
            raise ValueError("an artifact must lie inside this folder")
        with open(os.path.join(root, rel), "rb") as fh:
            e["path"], e["sha256"] = rel.replace(os.sep, "/"), _sha(fh.read())
    else:
        e["text"], e["sha256"] = text, _sha(text.encode("utf-8"))
    e["hash"] = _sha(_canon(e))
    os.makedirs(os.path.join(root, "runs"), exist_ok=True)
    with open(os.path.join(root, LEDGER), "a", encoding="utf-8") as fh:
        fh.write(json.dumps(e, sort_keys=True, ensure_ascii=False) + "\n")
    return e


def main(argv=None):
    ap = argparse.ArgumentParser(prog="ledger.py", description="the configuration record of a cycle")
    ap.add_argument("--root", default=".", help="the folder holding runs/ledger.jsonl; default here")
    sub = ap.add_subparsers(dest="verb", required=True)
    ad = sub.add_parser("add")
    ad.add_argument("kind", choices=KINDS)
    g = ad.add_mutually_exclusive_group(required=True)
    g.add_argument("--text")
    g.add_argument("--file")
    ad.add_argument("--actor", default="")
    ad.add_argument("--note", default="")
    ve = sub.add_parser("verify")
    ve.add_argument("--strict", action="store_true")
    sub.add_parser("status")
    sh = sub.add_parser("show")
    sh.add_argument("--last", type=int, default=0)
    a = ap.parse_args(argv)
    if a.verb == "add":
        try:
            e = append(a.root, a.kind, a.text, a.file, a.actor, a.note)
        except (ValueError, OSError) as err:
            print(f"ledger: {err}", file=sys.stderr)
            return 1
        print(f"ledger: entry {e['seq']} {e['kind']} {e['sha256'][:12]}")
        return 0
    entries = read(a.root)
    if a.verb == "show":
        for e in entries[-a.last:] if a.last else entries:
            what = e.get("path") or (e.get("text", "")[:60].replace("\n", " "))
            print(f"{e['seq']:>4}  {e['time']}  {e['kind']:9} {e.get('actor', ''):14} {what}")
        return 0
    probs = status(a.root, entries) if a.verb == "status" else verify(a.root, a.strict)
    for p in probs:
        print(f"ledger: {p}")
    if not probs:
        print(f"ledger: {len(entries)} entries, " + ("nothing changed since recorded" if a.verb == "status" else "chain intact"))
    return 1 if probs else 0


if __name__ == "__main__":
    sys.exit(main())
