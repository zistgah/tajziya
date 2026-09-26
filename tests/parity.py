# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""The Python and JavaScript ports of the parser must agree (the upstream CONTRIBUTING rule).

    python3 tests/parity.py [JS_DIR]     exit 0 agree, 1 disagree, 3 node absent (unjudged)
"""
import json
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = os.path.join(ROOT, "vendor", "sanskrit_parser", "python")
JS = os.path.join(ROOT, "vendor", "sanskrit_parser", "js")
CASES = [{"text": t} for t in ("neti", "tatraiva", "gurūpadeśa", "sīteva", "neti tatraiva", "rāmavanam")]
CASES.append({"text": "deveha", "lexicon": ["deva", "devā", "iha"]})


def python_side():
    sys.path.insert(0, PY)
    try:
        import sandhi, lexicon, pipeline
    finally:
        sys.path.remove(PY)
    pairs = {}
    for l in sandhi.VOWELS:
        for r in sandhi.VOWELS:
            try:
                pairs[f"{l}|{r}"] = sandhi.combine_vowels(l, r).combined
            except ValueError:
                pairs[f"{l}|{r}"] = None
    splits = {k: [list(p) for p in v] for k, v in sandhi.REVERSE_INDEX.items()}
    segs = {}
    for c in CASES:
        s = pipeline.Segmenter([], set(c["lexicon"]) if "lexicon" in c else lexicon.TOY_LEXICON)
        segs[c["text"]] = [[x.text for x in sol] for sol in s.segment(c["text"])]
    return {"pairs": pairs, "splits": splits, "segs": segs}


def js_side(js_dir):
    out = subprocess.run(["node", os.path.join(ROOT, "tests", "js_probe.mjs"), js_dir, json.dumps(CASES)],
                         capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def differences(a, b):
    d = []
    for k in sorted(set(a["pairs"]) | set(b["pairs"])):
        if a["pairs"].get(k) != b["pairs"].get(k):
            d.append(f"combine {k}: python {a['pairs'].get(k)!r}, javascript {b['pairs'].get(k)!r}")
    for key in ("splits", "segs"):
        for k in sorted(set(a[key]) | set(b[key])):
            if sorted(map(tuple, a[key].get(k, []))) != sorted(map(tuple, b[key].get(k, []))):
                d.append(f"{key} {k}: python {a[key].get(k)}, javascript {b[key].get(k)}")
    return d


def main(argv):
    if not shutil.which("node"):
        print("parity: node is not installed, so the JavaScript port is unjudged")
        return 3
    diff = differences(python_side(), js_side(argv[1] if len(argv) > 1 else JS))
    for line in diff:
        print("DIFFER", line)
    print(f"parity: {'agree' if not diff else str(len(diff)) + ' difference(s)'}")
    return 1 if diff else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
