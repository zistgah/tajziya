#!/usr/bin/env python3
# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""Derive vendor/sanskrit_parser from the uploaded archive, and record every change.

    python3 tools/vendor_import.py --zip sanskrit-parser.zip [--out vendor/sanskrit_parser]

The archive is read, never trusted: its SHA-256 must equal the pin in
vendor/sanskrit_parser/UPSTREAM.json, or nothing is written. Every change is an
exact-anchor patch that aborts when its anchor does not occur exactly once. The
third-party sutra compilation inside the archive is NOT copied into the tree; see
CONTRACT.md T5.

Exit 0 written, 1 refused (with the reason), 3 cannot judge (archive absent).
"""
import argparse, hashlib, io, json, os, sys, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIN = os.path.join(ROOT, "vendor", "sanskrit_parser", "UPSTREAM.json")
HDR_PY = "# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.\n# SPDX-License-Identifier: MIT\n"
HDR_JS = "// © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.\n// SPDX-License-Identifier: MIT\n"
MAIN_GUARD = ("if (import.meta.url === `file://${process.argv[1]}`) {",
              "if (typeof process !== \"undefined\" && import.meta.url === `file://${process.argv[1]}`) {")

# (file, anchor, replacement, reason). Anchors are exact; each must occur once.
PATCHES = [
    ("LICENSE", "Copyright (c) 2026 Abhishek Chaudhary",
     "Copyright (c) 1993–2026 Abhishek Choudhary",
     "holder name misspelt; estate copyright line applied"),
    ("js/sandhi.js", MAIN_GUARD[0], MAIN_GUARD[1],
     "module threw ReferenceError on `process` when evaluated in a browser"),
    ("js/pipeline.js", MAIN_GUARD[0], MAIN_GUARD[1],
     "module threw ReferenceError on `process` when evaluated in a browser"),
    ("js/rules.js", MAIN_GUARD[0], MAIN_GUARD[1],
     "module threw ReferenceError on `process` when evaluated in a browser"),
    ("README.md",
     "Panini's sutras themselves are ~2,500 years old and firmly public domain;\n"
     "this particular digital compilation is a modern scholarly aggregation of\n"
     "them, freely published for exactly this kind of reuse.",
     "Panini's sutras themselves are ~2,500 years old and firmly public domain.\n"
     "This particular digital compilation is a modern scholarly aggregation of\n"
     "them. The source site states that its texts are prepared by volunteers for\n"
     "personal study and research, and are not to be copied or reposted without\n"
     "permission. The compilation is therefore not redistributed in this\n"
     "repository; data/SOURCE.json pins the exact bytes so a local copy can be\n"
     "verified and used.",
     "a claim of free reuse contradicted by the source site's own stated terms"),
    ("README.md",
     "**Fastest way to get the rest:** the same index is published in full as a\n"
     "spreadsheet, which a plain fetch *can't* parse but you can download and\n"
     "send back here for me to read directly:",
     "The same index is published in full as a spreadsheet, under the same terms:",
     "conversational text addressed to a chat, not to a reader"),
    ("README.md",
     "Upload either one and I can ingest the complete dataset in a single pass,\n"
     "instead of continuing to scrape the site page by page.\n",
     "",
     "conversational text addressed to a chat, not to a reader"),
    ("README.md",
     "It's actively maintained — Huet was personally fixing a bug report against\n"
     "it this week.",
     "It is actively maintained.",
     "an undated, unverifiable time-bound claim"),
    ("README.md",
     "than a replacement. Worth saying if that assumption is wrong.",
     "than a replacement.",
     "conversational text addressed to a chat, not to a reader"),
    ("CONTRIBUTING.md",
     "7. **Release with a DOI.** At each batch release, mint a DOI for the\n"
     "   compiled dataset snapshot (Zenodo is the natural free option) rather\n"
     "   than treating the underlying source pages as citable on their own --\n"
     "   most of them aren't formal publications and won't have DOIs of their\n"
     "   own.",
     "7. **Release with a DOI.** A DOI is minted for this repository's own work.\n"
     "   A third-party compilation is cited with its URL, retrieval date and\n"
     "   content hash, and is deposited only where its terms permit\n"
     "   redistribution.",
     "minting a third party's compilation would contradict its stated terms"),
]
COPY = ["README.md", "CONTRIBUTING.md", "LICENSE", ".gitignore",
        "python/rules.py", "python/sandhi.py", "python/lexicon.py", "python/pipeline.py",
        "js/rules.js", "js/sandhi.js", "js/lexicon.js", "js/pipeline.js", "js/package.json"]
WITHHELD = ["data/sutras_1.1-1.3.json"]


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", required=True)
    ap.add_argument("--out", default=os.path.join(ROOT, "vendor", "sanskrit_parser"))
    ap.add_argument("--pin", default=PIN)
    a = ap.parse_args()
    for given in (a.zip, a.out, a.pin):
        if os.path.commonpath([os.path.realpath(given), ROOT]) != ROOT:
            print(f"vendor_import: refused, {given} is outside this repository's folder (master contract, clause 7)")
            return 1
    if not os.path.exists(a.zip):
        print(f"vendor_import: cannot judge, no archive at {os.path.relpath(os.path.realpath(a.zip), ROOT)}")
        return 3
    blob = open(a.zip, "rb").read()
    pin = json.load(open(a.pin)) if os.path.exists(a.pin) else None
    if pin and sha(blob) != pin["archive"]["sha256"]:
        print(f"vendor_import: refused, archive sha256 {sha(blob)} is not the pinned "
              f"{pin['archive']['sha256']}")
        return 1
    z = zipfile.ZipFile(io.BytesIO(blob))
    prefix = "sanskrit_parser/"
    files, record = {}, []
    for rel in COPY:
        data = z.read(prefix + rel)
        files[rel] = data
        record.append({"file": rel, "upstream_sha256": sha(data)})
    for rel, anchor, repl, why in PATCHES:
        text = files[rel].decode("utf-8")
        n = text.count(anchor)
        if n != 1:
            print(f"vendor_import: refused, anchor in {rel} occurs {n} times, not once: "
                  f"{anchor[:60]!r}")
            return 1
        files[rel] = text.replace(anchor, repl).encode("utf-8")
    for rel in list(files):
        if rel.endswith(".py"):
            files[rel] = HDR_PY.encode() + files[rel]
        elif rel.endswith(".js"):
            files[rel] = HDR_JS.encode() + files[rel]
    for r in record:
        r["vendored_sha256"] = sha(files[r["file"]])
        r["changed"] = r["vendored_sha256"] != r["upstream_sha256"]
    for rel, data in files.items():
        dst = os.path.join(a.out, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, "wb") as fh:
            fh.write(data)
    withheld = [{"file": w, "upstream_sha256": sha(z.read(prefix + w)),
                 "reason": "third-party compilation; source terms do not permit reposting"}
                for w in WITHHELD]
    out = {"archive": {"sha256": sha(blob), "root": prefix.rstrip("/")},
           "files": record, "patches": [{"file": p[0], "reason": p[3]} for p in PATCHES],
           "headers": "estate copyright and SPDX-License-Identifier: MIT prepended to every .py and .js",
           "withheld": withheld}
    with open(os.path.join(a.out, "UPSTREAM.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    src = {"file": "sutras_1.1-1.3.json", "sha256": withheld[0]["upstream_sha256"],
           "entries": 152, "range": "1.1.1 to 1.3.4",
           "source": "https://sanskritdocuments.org/learning_tools/ashtadhyayi/",
           "compiled_by": "Sai Susarla, Sanskrit Documents, as stated in the upstream README",
           "terms": ("The source site states that its texts are volunteer-prepared, meant for "
                     "personal study and research, and not to be reposted without permission."),
           "terms_checked": "2026-09-26",
           "held_as": "not redistributed; a local copy whose sha256 matches is used when present",
           "local_path": "vendor/sanskrit_parser/data/sutras_1.1-1.3.json",
           "import_verb": "data import"}
    os.makedirs(os.path.join(a.out, "data"), exist_ok=True)
    with open(os.path.join(a.out, "data", "SOURCE.json"), "w", encoding="utf-8") as fh:
        json.dump(src, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print(f"vendor_import: {len(files)} files written to {os.path.relpath(a.out, ROOT)}, "
          f"{sum(r['changed'] for r in record)} changed, {len(withheld)} withheld")
    return 0


if __name__ == "__main__":
    sys.exit(main())
