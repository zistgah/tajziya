#!/usr/bin/env python3
# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""Generate docs/review.html and its data, docs/data/review.json: every sutra, and the flags a reviewer acts on.

    python3 tools/review_gen.py [--check] [--repo ORG/NAME] [--local FILE]

The page is a small shell; it fetches the data and renders the sutras as you scroll, so it opens fast
on a phone and shows an error, never a blank page, if the data cannot load.

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
DATA_OUT = os.path.join(ROOT, "docs", "data", "review.json")
LOCAL_OUT = os.path.join(ROOT, "docs", "review-local.html")
LOCAL_DATA_OUT = os.path.join(ROOT, "docs", "data", "review-local.json")

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


def rows_for(sutras, flags, local=None):
    rows, rom = [], romenagri_forms()
    for r in sutras:
        row = {"id": r["id"], "t": r["type"], "tm": r["term"] or None, "s": r["sutra"], "pc": r["padaccheda"],
               "k": r["kaumudi"] or None, "f": flags.get(r["id"])}
        if r["id"] in rom:
            row["r"], row["rt"] = rom[r["id"]][0], rom[r["id"]][1] == "same"
        if local is not None and r["id"] in local:
            row["l"] = local[r["id"]]
        rows.append(row)
    return rows


def data_json(rows, repo, local=False):
    meta = {"repo": repo, "sutras": len(rows), "flagged": sum(1 for r in rows if r["f"]),
            "romenagri_same": sum(1 for r in rows if r.get("rt")), "local": local}
    return json.dumps({"schema": "tajziya.review/1", "meta": meta, "rows": rows}, ensure_ascii=False,
                      separators=(",", ":")) + "\n"


def page(data_file, local=False):
    note = ("Your local copy's values are shown beside the open ones. This page and its data are not committed."
            if local else "The restricted compilation's text is not reproduced here; its disagreements are recorded "
            "by sutra and field.")
    return TEMPLATE.replace("@@DATA@@", data_file).replace("@@LOCALNOTE@@", note) \
        .replace("@@TITLE@@", "Sanskrit sutras: source review" + (" (local)" if local else ""))


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
.controls{display:flex;flex-wrap:wrap;gap:.6rem;align-items:center;margin:1rem 0;position:sticky;top:0;background:var(--bg);padding:.5rem 0}
input{flex:1 1 16rem;padding:.5rem;border:1px solid var(--line);background:transparent;color:inherit;border-radius:6px}
button{padding:.45rem .8rem;border:1px solid var(--line);background:transparent;color:inherit;border-radius:6px;cursor:pointer}
button.on{border-color:var(--acc);color:var(--acc)}
.card{border-top:1px solid var(--line);padding:.7rem .3rem}.card.flag{background:var(--flag)}
.id{font-weight:600}.meta{color:var(--mut);font-size:.9rem}.s{font-size:1.25rem}
.f{font-size:.9rem;margin-top:.3rem}.f a{color:var(--acc)}
#more{padding:1rem 0;color:var(--mut)}.err{color:#b00020}
</style></head><body><div class="wrap">
<p class="meta"><a href="index.html">tajziya</a> · <a href="packets.html">work packets</a></p>
<h1>@@TITLE@@</h1>
<p class="sub" id="lead">Loading the sutras.</p>
<p class="sub">@@LOCALNOTE@@ Translations, interpretations, the implementing code and more scripts arrive as
<a href="packets.html">work packets</a>.</p>
<div class="controls"><input id="q" placeholder="Search by number (2.3.17), text, term or Romenagri">
<button id="tf" class="on">Flagged</button><button id="ta">All</button><span id="n" class="meta"></span></div>
<div id="list"></div><div id="more"></div>
</div><script>
(function () {
  var PAGE = 60, ROWS = [], REPO = "", mode = "flag", shown = PAGE, current = [];
  var $ = function (id) { return document.getElementById(id); };
  var esc = function (s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
    return {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}[c]; }); };
  function issueUrl(title, body) {
    return "https://github.com/" + REPO + "/issues/new?title=" + encodeURIComponent(title) + "&body=" + encodeURIComponent(body);
  }
  function flagIssue(r, f) {
    return issueUrl("Sutra " + r.id + ": " + f.field + " differs from " + f.against,
      "Sutra " + r.id + "\\nField: " + f.field + "\\nOpen data (ashtadhyayi.com): " + (f.field === "sutra" ? r.s : r.pc) +
      "\\nDiffers from: " + f.against + "\\n\\nReading and source for the correction:\\n");
  }
  function reviewIssue(r) {
    return issueUrl("Sutra " + r.id + ": review",
      "Sutra " + r.id + "\\n" + r.s + "\\nPadaccheda: " + r.pc + (r.r ? "\\nRomenagri: " + r.r : "") +
      "\\n\\nWhich part is wrong (text, padaccheda, type or term, translation, interpretation, implementation," +
      " transliteration), and the source for the correction:\\n");
  }
  function card(r) {
    var fl = r.f || [], h = '<div class="card' + (fl.length ? " flag" : "") + '"><span class="id">' + esc(r.id) + "</span> " +
      '<span class="meta">' + esc(r.t) + (r.tm ? " · " + esc(r.tm) : "") + (r.k ? " · SK " + esc(r.k) : "") + "</span>" +
      '<div class="s">' + esc(r.s) + '</div><div class="meta">' + esc(r.pc) + "</div>";
    if (r.r) h += '<div class="meta">Romenagri: ' + esc(r.r) + (r.rt ? "" : " · does not yet come back the same (packet PKT-ROM-01)") + "</div>";
    if (r.l) h += '<div class="meta">local: ' + esc(r.l.sutra) + " · " + esc(r.l.padaccheda) + "</div>";
    fl.forEach(function (f) { h += '<div class="f">' + esc(f.field) + " differs from " + esc(f.against) +
      ' · <a href="' + flagIssue(r, f) + '" target="_blank" rel="noopener">Open issue</a></div>'; });
    return h + '<div class="f"><a href="' + reviewIssue(r) + '" target="_blank" rel="noopener">Open an issue on this sutra</a></div></div>';
  }
  function select() {
    var q = $("q").value.trim().toLowerCase();
    current = ROWS.filter(function (r) { return mode === "all" || r.f; });
    if (q) current = current.filter(function (r) {
      return r.id.indexOf(q) >= 0 || r.s.indexOf(q) >= 0 || (r.tm || "").indexOf(q) >= 0 || r.pc.indexOf(q) >= 0 ||
        (r.r || "").toLowerCase().indexOf(q) >= 0; });
    shown = PAGE; $("list").innerHTML = ""; $("n").textContent = current.length + " shown"; more();
  }
  function more() {
    var start = $("list").children ? $("list").children.length : 0, html = "";
    current.slice(start, shown).forEach(function (r) { html += card(r); });
    $("list").insertAdjacentHTML ? $("list").insertAdjacentHTML("beforeend", html) : ($("list").innerHTML += html);
    $("more").textContent = shown < current.length ? "Scroll for more (" + (current.length - shown) + " left)" : "";
  }
  function tab(m) { mode = m; $("tf").className = m === "flag" ? "on" : ""; $("ta").className = m === "all" ? "on" : ""; select(); }
  $("q").oninput = select;
  $("tf").onclick = function () { tab("flag"); };
  $("ta").onclick = function () { tab("all"); };
  if ("IntersectionObserver" in window) {
    new IntersectionObserver(function (e) { if (e[0].isIntersecting && shown < current.length) { shown += PAGE; more(); } })
      .observe($("more"));
  } else { $("more").onclick = function () { shown += PAGE; more(); }; }
  fetch("data/@@DATA@@").then(function (r) { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); })
    .then(function (d) {
      ROWS = d.rows; REPO = d.meta.repo;
      $("lead").textContent = "All " + d.meta.sutras.toLocaleString() + " sutras, from ashtadhyayi.com's data (credited). " +
        d.meta.flagged + " carry a flag: a field where another source differs. " + d.meta.romenagri_same.toLocaleString() +
        " come back from Romenagri the same. Every sutra has an issue link to " + REPO + ".";
      select();
    })
    .catch(function (e) { $("lead").innerHTML = '<span class="err">The sutras could not be loaded (' + esc(e.message) +
      '). The data is <a href="data/@@DATA@@">data/@@DATA@@</a>.</span>'; });
})();
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
        rows = rows_for(sutras, flags, local=load_local(a.local))
        with open(LOCAL_DATA_OUT, "w", encoding="utf-8") as fh:
            fh.write(data_json(rows, a.repo, local=True))
        with open(LOCAL_OUT, "w", encoding="utf-8") as fh:
            fh.write(page("review-local.json", local=True))
        print(f"review_gen: wrote {os.path.relpath(LOCAL_OUT, ROOT)} and its data; git ignores both")
        return 0
    want = {OUT: page("review.json"), DATA_OUT: data_json(rows_for(sutras, flags), a.repo)}
    if a.check:
        stale = [os.path.relpath(p, ROOT) for p, t in want.items()
                 if not os.path.exists(p) or open(p, encoding="utf-8").read() != t]
        print("review_gen: the review page and its data are current" if not stale else f"review_gen: STALE: {', '.join(stale)}")
        return 0 if not stale else 1
    for p, t in want.items():
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(t)
    print(f"review_gen: {len(sutras)} sutras, {len(flags)} flagged; docs/review.html and docs/data/review.json written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
