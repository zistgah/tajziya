#!/usr/bin/env python3
# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""Write the work packets into packets/, one JSON per packet.

    python3 tools/packets_gen.py

A packet file that already exists is never rewritten: its status belongs to whoever is working
it. Adding a wave means adding definitions here and running this again.
"""
import csv
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "packets")
ASH = "github.com/ashtadhyayi-com/data at 5744762f010d677cfb43f347a42d02796cf615d6, sutraani/"
ASH_TERMS = ("ashtadhyayi.com's terms: use with credit (LicenseRef-ashtadhyayi-com; the notice is in "
             "modules/cls/data/LICENSES/ashtadhyayi-com.txt). The underlying work's own status is recorded too: "
             "a modern author's work enters the tree only on the owner's ruling.")
# sutras each ashtadhyayi.com file covers with text, counted 5 Oct 2026
COVERS = {"bhashya": 1702, "kashika": 3983, "nyaas": 3432, "padamanjari": 3368, "kaumudi": 3949,
          "praudhamanorama": 462, "balamanorama": 2912, "tattvabodhini": 2477, "laghukaumudi": 1254,
          "laghushabdendushekhar": 82, "prakriyasarvasvam": 3634, "sarala": 215, "sudha": 375,
          "sutrartha": 3983, "sutrartha_english": 838, "vasu_english": 3983}


def packet(pid, title, area, size, summary, inputs, outputs, licence, kind, args, how, depends=(), wave=1):
    return {"schema": "tajziya.packet/1", "id": pid, "title": title, "area": area, "wave": wave, "size": size,
            "status": "open", "summary": summary, "inputs": inputs, "outputs": outputs, "licence": licence,
            "acceptance": {"kind": kind, "args": args, "command": f"python3 -m tajziya packet check {pid}"},
            "depends": list(depends), "how": how}


def table_packet(pid, title, area, src_file, slug, source_id, licence=ASH_TERMS, size="S", summary=None, extra=()):
    n = COVERS[src_file]
    return packet(pid, title, area, size,
                  summary or f"Import {title} for the {n} sutras the source covers, keyed by sutra number.",
                  [{"what": f"{src_file}.txt", "where": ASH + f"{src_file}.txt"}],
                  [f"modules/cls/data/{area.split('-')[0]}/{slug}.tsv", "modules/cls/data/SOURCES.json"], licence,
                  "sutra-table", {"path": f"modules/cls/data/{area.split('-')[0]}/{slug}.tsv",
                                  "columns": ["id", "text"], "min_rows": n, "source_id": source_id},
                  ["Download the file at the pinned commit; record its sha256.",
                   "Write a deterministic import script in tools/ that keys each entry by sutra number (a.p.n) "
                   "and writes id and text, NFC, one row per sutra.",
                   "Add a source to modules/cls/data/SOURCES.json pinning the TSV you wrote, with the terms.",
                   *extra, "Run the acceptance command; open a pull request when it passes."])


def build():
    ps = []
    ps.append(packet("PKT-ROM-01", "Romenagri: bring the avagraha back", "romenagri", "S",
        "374 of the 3,983 sutras do not come back from Romenagri the same: ऽ returns as ्3. The fix is in the "
        "author's Romenagri, upstream; this repository then re-vendors it.",
        [{"what": "the sutras that differ", "where": "modules/cls/data/romenagri/sutras.tsv (round_trip = differs)"},
         {"what": "Romenagri", "where": "github.com/hindawiai/chintamani, Romenagri/"}],
        ["vendor/romenagri/", "modules/cls/data/romenagri/sutras.tsv"],
        "GPL-2.0-or-later, the author's own code; the change goes upstream first.",
        "romenagri-pin", {"expect_same": 3983},
        ["Fix the avagraha in hindawiai/chintamani's Romenagri (acii2rmn.lex, rmn2acii.lex or the tables).",
         "Re-vendor the folder byte for byte and update vendor/romenagri/UPSTREAM.json to the new commit.",
         "Regenerate modules/cls/data/romenagri/sutras.tsv with tools/romenagri_sutras.py.",
         "Run the acceptance command."]))
    ps.append(packet("PKT-ROM-02", "Romenagri in the browser", "romenagri", "M",
        "Compile the vendored Romenagri to WebAssembly with a JavaScript wrapper, so the pages can call "
        "roman() and devanagari() themselves, with output byte-identical to the C build on every sutra.",
        [{"what": "Romenagri", "where": "vendor/romenagri (pinned)"}],
        ["docs/vendor/romenagri.js", "docs/vendor/romenagri.wasm"], "GPL-2.0-or-later, as the vendored code.",
        "wasm-parity", {"js": "docs/vendor/romenagri.js"},
        ["Build the vendored C and lex with Emscripten; reproduce its own Makefile's pipeline, no rewrite.",
         "Make the wrapper read lines on stdin under node with --roman, and export roman() for the page.",
         "Run the acceptance command."]))
    ps.append(packet("PKT-IMP-01", "Which sutras the author's parser applies", "implementation", "M",
        "Map each junction rule in the author's Sanskrit parser to the sutra it implements: file, line, "
        "function, and what it applies in plain words.",
        [{"what": "the parser", "where": "vendor/sanskrit_parser (pinned)"}],
        ["modules/cls/data/implementation/tajziya.tsv"], "Our own index, CC-BY-SA-4.0; no code is copied.",
        "implementation-map", {"path": "modules/cls/data/implementation/tajziya.tsv", "root": ".", "min_rows": 5},
        ["Read vendor/sanskrit_parser's junction rules; never edit the vendored code.",
         "Write one row per rule: id, file, line, function, applies (for example: a + i becomes e).",
         "Run the acceptance command."]))
    ps.append(packet("PKT-IMP-02", "Which sutras vidyut-prakriya implements, and where", "implementation", "M",
        "Scan vidyut-prakriya's source at a pinned commit for the sutra codes it cites, so each sutra on the "
        "review page names the file and line that implements it.",
        [{"what": "vidyut", "where": "github.com/ambuda-org/vidyut, MIT, at a commit you pin"}],
        ["modules/cls/data/implementation/vidyut.tsv", "Makefile"], "vidyut is MIT; cite file and line, quote nothing long.",
        "implementation-map", {"path": "modules/cls/data/implementation/vidyut.tsv", "root": ".deps/vidyut", "min_rows": 1000},
        ["Add vidyut at a pinned commit to `make deps`, cloned into .deps/vidyut.",
         "Write a deterministic scanner in tools/ that finds sutra codes in vidyut-prakriya/src and writes id, file, line, "
         "function, applies (the rule's own comment, or the sutra text).",
         "Run the acceptance command."]))
    ps.append(table_packet("PKT-TRN-01", "the English meaning (sutrartha)", "translation", "sutrartha_english",
                           "english", "ashtadhyayi-com-sutrartha-english"))
    ps.append(table_packet("PKT-TRN-02", "Śrīśa Chandra Vasu's English translation", "translation", "vasu_english",
                           "vasu", "ashtadhyayi-com-vasu-english",
                           extra=["Record in the source who Vasu was, when the translation was published and its "
                                  "copyright status, with a citation for each."]))
    ps.append(table_packet("PKT-TRN-03", "the Sanskrit meaning (artha)", "translation", "sutrartha",
                           "sanskrit-artha", "ashtadhyayi-com-sutrartha"))
    trad = [("bhashya", "mahabhashya", "the Mahābhāṣya of Patañjali", "L"), ("kashika", "kashika", "the Kāśikā of Vāmana and Jayāditya", "M"),
            ("nyaas", "nyasa", "the Nyāsa of Jinendrabuddhi", "M"), ("padamanjari", "padamanjari", "the Padamañjarī of Haradatta", "M"),
            ("kaumudi", "siddhanta-kaumudi", "the Siddhānta Kaumudī of Bhaṭṭoji Dīkṣita", "M"),
            ("praudhamanorama", "praudhamanorama", "the Prauḍhamanoramā of Bhaṭṭoji Dīkṣita", "S"),
            ("balamanorama", "balamanorama", "the Bālamanoramā of Vāsudeva Dīkṣita", "M"),
            ("tattvabodhini", "tattvabodhini", "the Tattvabodhinī of Jñānendra Sarasvatī", "M"),
            ("laghukaumudi", "laghu-kaumudi", "the Laghu Kaumudī of Varadarāja", "S"),
            ("laghushabdendushekhar", "laghushabdendushekhara", "the Laghuśabdenduśekhara of Nāgeśa Bhaṭṭa", "S"),
            ("prakriyasarvasvam", "prakriyasarvasva", "the Prakriyāsarvasva of Nārāyaṇa Bhaṭṭa", "M"),
            ("sarala", "sarala", "the commentary the data names sarala", "S"),
            ("sudha", "sudha", "the commentary the data names sudha", "S")]
    for i, (f, slug, title, size) in enumerate(trad, 1):
        extra = (["First establish the work's author and date, with a citation, and its copyright status; a modern "
                  "work waits for the owner's ruling before it enters the tree."] if f in ("sarala", "sudha") else [])
        ps.append(table_packet(f"PKT-INT-{i:02d}", title, "interpretation-traditional", f, slug,
                               f"ashtadhyayi-com-{slug}", size=size, extra=extra))
    schools = [("katantra", "Kātantra"), ("candra", "Cāndra"), ("jainendra", "Jainendra"), ("shakatayana", "Śākaṭāyana"),
               ("haima", "Hemacandra's Siddhahemaśabdānuśāsana"), ("sarasvata", "Sārasvata"),
               ("mugdhabodha", "Mugdhabodha"), ("supadma", "Supadma")]
    for i, (slug, name) in enumerate(schools, 1):
        ps.append(packet(f"PKT-SCH-{i:02d}", f"The {name} school, beside Pāṇini", "interpretation-schools", "L",
            f"Find an openly licensed edition of the {name} grammar and record, for each of its rules that answers a "
            "Pāṇinian sutra, the correspondence and its text.",
            [{"what": f"an edition of the {name} grammar", "where": "to be found; record its terms"}],
            [f"modules/cls/data/schools/{slug}.tsv", "modules/cls/data/SOURCES.json"],
            "registry/licences.json decides; a restricted edition stays local-only and the packet waits for an open one.",
            "sutra-table", {"path": f"modules/cls/data/schools/{slug}.tsv", "columns": ["id", "school_rule", "text"],
                            "min_rows": 1, "multi": True, "source_id": f"school-{slug}"},
            ["Find the edition and read its terms; record them verbatim.",
             "Write a deterministic import and a concordance: Pāṇini's sutra id, the school's rule number, its text.",
             "Run the acceptance command."]))
    academic = [("bohtlingk", "Otto Böhtlingk, Pâṇini's Grammatik (1887)", True),
                ("renou", "Louis Renou, La grammaire de Pāṇini (1948 to 1954)", False),
                ("katre", "Sumitra M. Katre, Aṣṭādhyāyī of Pāṇini (1987)", False),
                ("sharma", "Rama Nath Sharma, The Aṣṭādhyāyī of Pāṇini (1987 to 2003)", False),
                ("cardona", "George Cardona's studies of Pāṇini", False),
                ("kiparsky", "Paul Kiparsky's studies of Pāṇini's grammar", False),
                ("joshi-roodbergen", "S. D. Joshi and J. A. F. Roodbergen's Mahābhāṣya translations", False),
                ("computational", "computational models of Pāṇini (vidyut, the Sanskrit Heritage Platform and others)", False)]
    for i, (slug, work, pd) in enumerate(academic, 1):
        if pd:
            ps.append(packet(f"PKT-ACA-{i:02d}", f"Import {work}", "interpretation-academic", "L",
                "A translation whose copyright has expired: import it from an openly available scan or transcription, keyed by sutra.",
                [{"what": work, "where": "a public-domain scan or transcription you cite"}],
                [f"modules/cls/data/academic/{slug}.tsv", "modules/cls/data/SOURCES.json"],
                "Public domain by age; record the edition, the scan's own terms and the evidence for the date.",
                "sutra-table", {"path": f"modules/cls/data/academic/{slug}.tsv", "columns": ["id", "text"],
                                "min_rows": 3900, "source_id": f"academic-{slug}"},
                ["Find a scan or transcription whose own terms allow reuse; record them.",
                 "Import deterministically, keyed by sutra; NFC; pin the TSV in SOURCES.json.", "Run the acceptance command."]))
        else:
            ps.append(packet(f"PKT-ACA-{i:02d}", f"Index {work}", "interpretation-academic", "M",
                f"A per-sutra index to {work}: where it treats each sutra, and a summary in our own words of what it says. "
                "The work's own text is never copied.",
                [{"what": work, "where": "the published work, cited"}],
                [f"modules/cls/data/academic/{slug}.tsv", "modules/cls/data/SOURCES.json"],
                "Our own index and summaries (CC-BY-SA-4.0); the work is cited, never reproduced.",
                "sutra-table", {"path": f"modules/cls/data/academic/{slug}.tsv", "columns": ["id", "locator", "summary"],
                                "min_rows": 1, "multi": True, "own_work": True, "max_chars": {"summary": 400},
                                "source_id": f"academic-{slug}"},
                ["Record the work's full citation in a source with a 'citation' field.",
                 "One row per place the work treats a sutra: id, locator (volume and page), a summary of at most 400 characters.",
                 "Run the acceptance command."]))
    with open(os.path.join(ROOT, "registry", "ilm", "scripts.tsv"), encoding="utf-8") as fh:
        scripts = {r["code"]: r for r in csv.DictReader(fh, delimiter="\t")}
    wave1 = ("Tibt Lepc Limb Mtei Cakm Saur Newa Brah Bhks Khar Shrd Takr Sidd Mahj Khoj Sind Mult Tirh Modi Nand "
             "Gran Dogr Kthi Sylo Gong Gonm Tutg Ahom Diak Phag Marc Zanb Soyo").split()
    for code in wave1:
        r = scripts[code]
        uname = r["unicode_pva"].replace("_", " ").upper()
        ps.append(packet(f"PKT-SCR-{code}", f"{r['name']} on Romenagri's pivot", "scripts", "S",
            f"A table taking Romenagri's ACII pivot to {r['name']} and back, so every sutra can be read in "
            f"{r['name']}. The round trip must be lossless on all 3,983 sutras.",
            [{"what": "the pivot", "where": "vendor/romenagri (iscii_map.csv shows the Brahmic layout)"},
             {"what": f"{r['name']} in Unicode {r['unicode_version']}", "where": "the Unicode Character Database"}],
            [f"tables/romenagri/{code}.csv"], "Our own table (CC0-1.0), derived from the Unicode Character Database, cited.",
            "script-table", {"path": f"tables/romenagri/{code}.csv", "unicode_name": uname, "min_unicode": r["unicode_version"]},
            ["Write tables/romenagri/<code>.csv with columns acii (hex, like A4) and char (the script's character or "
             "sequence), one row per ACII value the sutras use.",
             "Derive each character from the Unicode Character Database by name; cite the version.",
             "Run the acceptance command: every sutra's ACII must go to the script and come back unchanged."]))
    with open(os.path.join(ROOT, "registry", "nodes.json"), encoding="utf-8") as fh:
        nodes = json.load(fh)["nodes"]
    for n in nodes:
        ps.append(packet(f"PKT-COR-{n['id']}", f"A test corpus for {n['name']}", "corpus", "L",
            f"Attested text in {n['name']} with its analyses from the sources themselves, to measure the parser against. "
            "The rules are CORPUS.md's: retrieve, never recall; gold only from the source; exact counts.",
            [{"what": "candidate sources", "where": f"registry/corpora.json, node {n['id']}"}],
            [f"corpus/{n['id']}/"], "registry/licences.json decides; restricted sources stay local-only, pinned.",
            "corpus", {"node": n["id"]},
            ["Read CORPUS.md for the unit schema and the rules.",
             f"Build corpus/{n['id']}/: units.jsonl, SOURCES.json, README.md stating 'units: N', LICENSES/.",
             "Run the acceptance command."], wave=1 if n["id"] in ("vsn", "san-epic", "cls") else 2))
    return ps


def main():
    os.makedirs(OUT, exist_ok=True)
    made = 0
    for p in build():
        f = os.path.join(OUT, f"{p['id']}.json")
        if os.path.exists(f):
            continue
        with open(f, "w", encoding="utf-8") as fh:
            json.dump(p, fh, indent=1, ensure_ascii=False)
            fh.write("\n")
        made += 1
    print(f"packets_gen: {made} new packet(s); {len(os.listdir(OUT))} in packets/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
