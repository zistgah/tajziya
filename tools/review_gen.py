#!/usr/bin/env python3
# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""Generate docs/review.html: every sutra, and the flags a reviewer acts on.

    python3 tools/review_gen.py [--check] [--repo ORG/NAME] [--local FILE]

Flags come from two places. modules/cls/data/review/flags.json records the fields where the
restricted sanskritdocuments.org compilation differs from the open data; its text is never
written into this tree. And a cross-check run here: each sutra's text against
vidyut-prakriya's sutrapatha (MIT), transliterated from SLP1. --local FILE writes
docs/review-local.html, which git ignores, with your own copy's values beside the open ones.
"""
import argparse
import html
import json
import os
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "modules", "cls", "data")
OUT = os.path.join(ROOT, "docs", "review.html")
LOCAL_OUT = os.path.join(ROOT, "docs", "review-local.html")

V_IND = dict(zip("aAiIuUfFxXeEoO", "अआइईउऊऋॠऌॡएऐओऔ"))
V_SIGN = dict(zip("aAiIuUfFxXeEoO", ["", "ा", "ि", "ी", "ु", "ू", "ृ", "ॄ", "ॢ", "ॣ", "े", "ै", "ो", "ौ"]))
CONS = dict(zip("kKgGNcCjJYwWqQRtTdDnpPbBmyrlvSzsh", "कखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसह"))
OTHER = {"M": "ं", "H": "ः", "~": "ँ", "'": "ऽ", "3": "३"}


def slp1_to_deva(text):
    """SLP1 to Devanagari: a consonant carries an inherent a, and a virama when no vowel follows."""
    out, pending = [], False
    for ch in text:
        if ch in CONS:
            if pending:
                out.append("्")
            out.append(CONS[ch])
            pending = True
        elif ch in V_IND:
            out.append(V_SIGN[ch] if pending else V_IND[ch])
            pending = False
        else:
            if pending:
                out.append("्")
            pending = False
            out.append(OTHER.get(ch, ch))
    if pending:
        out.append("्")
    return unicodedata.normalize("NFC", "".join(out))


def load_sutras():
    with open(os.path.join(DATA, "ashtadhyayi", "sutraani.tsv"), encoding="utf-8") as fh:
        cols = next(fh).rstrip("\n").split("\t")
        return [dict(zip(cols, line.rstrip("\n").split("\t"))) for line in fh]


def vidyut_mismatches(sutras):
    with open(os.path.join(DATA, "sutrapatha.tsv"), encoding="utf-8") as fh:
        next(fh)
        v = {}
        for line in fh:
            code, _, text = line.rstrip("\r\n").partition("\t")
            if code:
                v[code] = slp1_to_deva(text)
    return [r["id"] for r in sutras
            if unicodedata.normalize("NFC", r["sutra"]) != v.get(r["id"])]


def flags_for(sutras):
    with open(os.path.join(DATA, "review", "flags.json"), encoding="utf-8") as fh:
        f = json.load(fh)["flags"]
    out = {}
    for x in f:
        out.setdefault(x["id"], []).append({"field": x["field"], "against": x["against"]})
    for sid in vidyut_mismatches(sutras):
        out.setdefault(sid, []).append({"field": "sutra", "against": "vidyut-prakriya sutrapatha (MIT)"})
    return out


def romenagri_forms():
    p = os.path.join(DATA, "romenagri", "sutras.tsv")
    if not os.path.exists(p):
        return {}
    with open(p, encoding="utf-8") as fh:
        next(fh)
        return {a: (b, c) for a, b, c in (l.rstrip("\n").split("\t") for l in fh)}


def page(sutras, flags, repo, local=None):
    rows, rom = [], romenagri_forms()
    for r in sutras:
        row = {"id": r["id"], "t": r["type"], "tm": r["term"] or None, "s": r["sutra"], "pc": r["padaccheda"],
               "k": r["kaumudi"] or None, "f": flags.get(r["id"])}
        if r["id"] in rom:
            row["r"], row["rt"] = rom[r["id"]][0], rom[r["id"]][1] == "same"
        if local is not None and r["id"] in local:
            row["l"] = local[r["id"]]
        rows.append(row)
    nflag = sum(1 for r in rows if r["f"])
    data = json.dumps(rows, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    title = "Sanskrit sutras: source review" + (" (local)" if local is not None else "")
    return TEMPLATE.replace("@@TITLE@@", html.escape(title)).replace("@@REPO@@", html.escape(repo)) \
        .replace("@@N@@", str(len(rows))).replace("@@NFLAG@@", str(nflag)) \
        .replace("@@LOCALNOTE@@", "Your local copy's values are shown beside the open ones. This file is not committed."
                 if local is not None else "The restricted compilation's text is not reproduced here; "
                 "its disagreements are recorded by sutra and field.") \
        .replace("@@DATA@@", data)


def load_local(path):
    with open(path, encoding="utf-8") as fh:
        d = json.load(fh)
    d = d.get("data", d) if isinstance(d, dict) else d
    return {str(x.get("id")): {"sutra": x.get("sutra"), "padaccheda": x.get("padaccheda")} for x in d if x.get("id")}


TEMPLATE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>@@TITLE@@</title>
<!-- © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI. Generated by tools/review_gen.py; do not edit. -->
<style>
:root{--bg:#fbfaf7;--fg:#1d1d1b;--mut:#6b675f;--line:#e4e0d6;--flag:#fff3dc;--acc:#8a4b08}
@media (prefers-color-scheme:dark){:root{--bg:#171614;--fg:#ecebe6;--mut:#a29d93;--line:#34312c;--flag:#33281a;--acc:#e3a35a}}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.5 system-ui,sans-serif}
.wrap{max-width:960px;margin:0 auto;padding:1.2rem}
h1{font-size:1.4rem;margin:.2rem 0}.sub{color:var(--mut)}
.controls{display:flex;flex-wrap:wrap;gap:.6rem;align-items:center;margin:1rem 0}
input{flex:1 1 16rem;padding:.5rem;border:1px solid var(--line);background:transparent;color:inherit;border-radius:6px}
button{padding:.45rem .8rem;border:1px solid var(--line);background:transparent;color:inherit;border-radius:6px;cursor:pointer}
button.on{border-color:var(--acc);color:var(--acc)}
.card{border-top:1px solid var(--line);padding:.7rem 0}.card.flag{background:var(--flag)}
.id{font-weight:600}.meta{color:var(--mut);font-size:.9rem}.s{font-size:1.25rem}
.f{font-size:.9rem;margin-top:.3rem}.f a{color:var(--acc)}
</style></head><body><div class="wrap">
<h1>@@TITLE@@</h1>
<p class="sub">All @@N@@ sutras, from ashtadhyayi.com's data (credited). @@NFLAG@@ carry a flag: a field where
another source differs. @@LOCALNOTE@@ Every sutra has an issue link to <strong>@@REPO@@</strong>.
Translations, interpretations, the implementing code and more scripts arrive as work packets: <a href="index.html#packets">pick one up</a>.</p>
<div class="controls"><input id="q" placeholder="Search by number (2.3.17), text or term">
<button id="tf" class="on">Flagged</button><button id="ta">All</button><span id="n" class="meta"></span></div>
<div id="list"></div><button id="more" hidden>More</button>
</div><script>
const REPO="@@REPO@@", ROWS=@@DATA@@, PAGE=80;
let mode="flag", shown=PAGE;
const esc=s=>String(s==null?"":s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
function issue(r,f){const t=`Sutra ${r.id}: ${f.field} differs from ${f.against}`;
 const b=`Sutra ${r.id}\\nField: ${f.field}\\nOpen data (ashtadhyayi.com): ${f.field==="sutra"?r.s:r.pc}\\nDiffers from: ${f.against}\\n\\nReading and source for the correction:\\n`;
 return `https://github.com/${REPO}/issues/new?title=${encodeURIComponent(t)}&body=${encodeURIComponent(b)}`;}
function review(r){const t=`Sutra ${r.id}: review`;
 const b=`Sutra ${r.id}\n${r.s}\nPadaccheda: ${r.pc}\n${r.r?"Romenagri: "+r.r+"\n":""}\nWhich part is wrong (text, padaccheda, type or term, translation, interpretation, implementation, transliteration), and the source for the correction:\n`;
 return `https://github.com/${REPO}/issues/new?title=${encodeURIComponent(t)}&body=${encodeURIComponent(b)}`;}
function card(r){const fl=r.f||[];return `<div class="card${fl.length?" flag":""}"><span class="id">${esc(r.id)}</span>
 <span class="meta">${esc(r.t)}${r.tm?" · "+esc(r.tm):""}${r.k?" · SK "+esc(r.k):""}</span>
 <div class="s">${esc(r.s)}</div><div class="meta">${esc(r.pc)}</div>
 ${r.r?`<div class="meta">Romenagri: ${esc(r.r)}${r.rt?"":" · does not yet come back the same (packet PKT-ROM-01)"}</div>`:""}
 ${r.l?`<div class="meta">local: ${esc(r.l.sutra)} · ${esc(r.l.padaccheda)}</div>`:""}
 ${fl.map(f=>`<div class="f">${esc(f.field)} differs from ${esc(f.against)} · <a href="${issue(r,f)}" target="_blank" rel="noopener">Open issue</a></div>`).join("")}
 <div class="f"><a href="${review(r)}" target="_blank" rel="noopener">Open an issue on this sutra</a></div></div>`;}
function draw(){const q=document.getElementById("q").value.trim().toLowerCase();
 let rs=ROWS.filter(r=>mode==="all"||r.f);
 if(q)rs=rs.filter(r=>r.id.includes(q)||r.s.includes(q)||(r.tm||"").includes(q)||r.pc.includes(q));
 document.getElementById("n").textContent=rs.length+" shown";
 document.getElementById("list").innerHTML=rs.slice(0,shown).map(card).join("");
 document.getElementById("more").hidden=rs.length<=shown;}
document.getElementById("q").oninput=()=>{shown=PAGE;draw();};
document.getElementById("tf").onclick=()=>{mode="flag";shown=PAGE;tf.classList.add("on");ta.classList.remove("on");draw();};
document.getElementById("ta").onclick=()=>{mode="all";shown=PAGE;ta.classList.add("on");tf.classList.remove("on");draw();};
document.getElementById("more").onclick=()=>{shown+=PAGE;draw();};
draw();
</script></body></html>
"""


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--repo", default="zistgah/tajziya")
    ap.add_argument("--local", help="your local copy of the restricted compilation (JSON); writes docs/review-local.html")
    a = ap.parse_args(argv)
    sutras = load_sutras()
    flags = flags_for(sutras)
    if a.local:
        text = page(sutras, flags, a.repo, local=load_local(a.local))
        with open(LOCAL_OUT, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"review_gen: wrote {os.path.relpath(LOCAL_OUT, ROOT)}; git ignores it")
        return 0
    text = page(sutras, flags, a.repo)
    if a.check:
        ok = os.path.exists(OUT) and open(OUT, encoding="utf-8").read() == text
        print("review_gen: docs/review.html is current" if ok else "review_gen: STALE, regenerate docs/review.html")
        return 0 if ok else 1
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(text)
    print(f"review_gen: {len(sutras)} sutras, {len(flags)} flagged, docs/review.html written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
