#!/usr/bin/env python3
# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""Every page's scripts parse, and the review and packets pages render their content.

    python3 tools/page_check.py

A page whose script does not parse shows its header and nothing else, which is what 0.6.0's review
page did. node checks each inline script's syntax; then each data page runs against a stand-in
DOM with its real data, and must render content and no error. Exit 3 when node is not installed.
"""
import json
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
SCRATCH = os.path.join(ROOT, "tests", ".scratch", "page_check")
RENDER = {"review.html": "list", "packets.html": "pk-list"}
HARNESS = r"""
const fs = require("fs"), path = require("path");
const [page, listId] = process.argv.slice(2);
const html = fs.readFileSync(page, "utf8");
const code = [...html.matchAll(/<script(?![^>]*\b(src|type="importmap")\b)[^>]*>([\s\S]*?)<\/script>/g)].map(m => m[2]).join("\n");
const els = {};
const el = id => els[id] || (els[id] = {id, innerHTML: "", textContent: "", className: "", hidden: false, value: "",
  dataset: {}, children: [], style: {}, classList: {add() {}, remove() {}, toggle() {}},
  insertAdjacentHTML(_, h) { this.innerHTML += h; }, querySelectorAll() { return []; }, addEventListener() {}});
global.window = global;
global.document = {getElementById: el, querySelectorAll: () => [], addEventListener() {}};
global.fetch = async u => { const f = path.join(path.dirname(page), u);
  return {ok: fs.existsSync(f), status: fs.existsSync(f) ? 200 : 404, json: async () => JSON.parse(fs.readFileSync(f, "utf8"))}; };
let err = null;
try { eval(code); } catch (e) { err = e.message; }
setTimeout(() => { const lead = (els.lead || els["pk-lead"] || {}).innerHTML || "";
  console.log(JSON.stringify({error: err, rendered: (els[listId] || {}).innerHTML ? els[listId].innerHTML.length : 0,
                              failed: /class="err"/.test(lead)})); }, 400);
"""


def scripts(html):
    for m in re.finditer(r"<script(?P<attrs>[^>]*)>(?P<body>.*?)</script>", html, re.S):
        a = m.group("attrs")
        if "src=" in a or "importmap" in a or "application/json" in a or not m.group("body").strip():
            continue
        yield ("module" in a), m.group("body")


def main():
    if shutil.which("node") is None:
        print("page_check: cannot judge, node is not installed")
        return 3
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(SCRATCH)
    bad = []
    for name in sorted(f for f in os.listdir(DOCS) if f.endswith(".html")):
        with open(os.path.join(DOCS, name), encoding="utf-8") as fh:
            html = fh.read()
        for i, (module, body) in enumerate(scripts(html)):
            f = os.path.join(SCRATCH, f"{name}.{i}.{'mjs' if module else 'js'}")
            with open(f, "w", encoding="utf-8") as fh:
                fh.write(body)
            r = subprocess.run(["node", "--check", f], capture_output=True, text=True)
            if r.returncode != 0:
                bad.append(f"{name}: script {i} does not parse: {(r.stderr.strip().splitlines() or ['?'])[-1]}")
    h = os.path.join(SCRATCH, "harness.js")
    with open(h, "w", encoding="utf-8") as fh:
        fh.write(HARNESS)
    for name, list_id in RENDER.items():
        r = subprocess.run(["node", h, os.path.join(DOCS, name), list_id], capture_output=True, text=True)
        try:
            out = json.loads(r.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError):
            bad.append(f"{name}: the render harness produced nothing: {r.stderr.strip()[-200:]}")
            continue
        if out["error"] or out["failed"] or not out["rendered"]:
            bad.append(f"{name}: renders nothing (error {out['error']}, data failed {out['failed']})")
    shutil.rmtree(SCRATCH, ignore_errors=True)
    for b in bad:
        print(b)
    print("page_check: every script parses and the data pages render" if not bad else "page_check: FAIL")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
