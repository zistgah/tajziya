# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""Process quests as AAB paintings.

The process cyclers of 0.2.0 belong to AAB, the author's mechanism for designing (his ruling,
27 Sep 2026). Each one is written here as an AAB painting, the JSON the studio at
https://zistgah.org/aab/ exports and imports: the original intent, verbatim, and a model of
actors, components, stores, gates, interfaces and environments with the flows between them.
In the studio the eight VGC stages are the quests, and a node glows verified only with a
recorded oracle, so every gate here names the command or check that is its oracle, and a gate
with no oracle yet says so rather than pretending.
"""
from .types import LAYER_NAMES, LAYERS

AAB = {"tool": "AAB", "version": "0.2.0"}
EXPORTED = "2026-09-27T00:00:00Z"
TYPES = ("actor", "comp", "store", "gate", "iface", "env")
COLUMN = {"actor": 90, "iface": 280, "env": 280, "comp": 480, "store": 680, "gate": 880}

# His words, verbatim, as AAB keeps intent.
ASK_PACKAGES = ("Now for each of the remaining languages, build a package which can be handed over to "
                "another AI or human and they can provide a parser etc implementation for that language")
ASK_QUESTS = ("include the cyclers you had mentioned, but put them, your process cyclers, put them into "
              "AAB, the mechanism for designing")


class Painter:
    def __init__(self):
        self.nodes, self.wires, self._rows = [], [], {}

    def add(self, kind, name, note="", oracle=""):
        if kind not in TYPES:
            raise ValueError(f"no AAB brush {kind}")
        col = COLUMN[kind]
        row = self._rows.get(col, 0)
        self._rows[col] = row + 1
        nid = len(self.nodes) + 1
        self.nodes.append({"id": nid, "type": kind, "x": col, "y": 70 + 88 * row,
                           "name": name, "note": note, "oracle": oracle})
        return nid

    def wire(self, a, b):
        self.wires.append([a, b])

    def painting(self, original, current):
        return dict(AAB, exported=EXPORTED, intent={"original": original, "current": current}, domain={},
                    model={"nodes": self.nodes, "wires": self.wires, "xp": 0, "stages": {},
                           "nextId": len(self.nodes) + 1})


def _package_gates(p):
    g = {}
    for cid, what in (("A1", "the manifest names a real node, versioned implementation and API 1"),
                      ("A2", "only expected entries; no build artefacts; no path outside the package"),
                      ("A3", "every data file listed with URL, date, sha256 and an allowed licence"),
                      ("A4", "every built layer cites attested examples with locators"),
                      ("A5", "the module loads alone and conforms: refusals name packages"),
                      ("A6", "bound into a scratch copy of tajziya, doctor and full conformance pass"),
                      ("A7", "this painting is valid and the configuration record's chain is intact")):
        g[cid] = p.add("gate", f"{cid} {what.split(';')[0].split(':')[0][:48]}", what,
                       f"bash accept.sh (check {cid})")
    return g


def language_layer(reg, nid=None):
    """The quest for one language package; with no node, the generic form."""
    p = Painter()
    builder = p.add("actor", "Builder", "a person or any AI, named by the operator in the record")
    reviewer = p.add("actor", "Reviewer", "the author or a maintainer, who types the gate")
    api = p.add("iface", "tajziya.api v1", "the only surface a module may import")
    env = p.add("env", "Python 3.10 and tajziya", "accept.sh clones tajziya into .deps/ inside the package")
    n = reg.node(nid) if nid else None
    comps = []
    for L in LAYERS:
        if n is None:
            note = f"{L} {LAYER_NAMES[L]}: one batch at a time, from an openly licensed source"
        else:
            needs, packages = reg.refusal(n, L)
            note = (f"{L} {LAYER_NAMES[L]}: {n['layers'][L]}; engines {', '.join(needs) or 'none named'}; "
                    f"packages {', '.join(packages) or 'none'}")
        comps.append(p.add("comp", f"{L} {LAYER_NAMES[L]}", note))
    sources = p.add("store", "data/SOURCES.json", "every source: URL, date, sha256, licence; candidates listed")
    examples = p.add("store", "reference/examples.json", "attested examples, every reading, with locators")
    record = p.add("store", "runs/ledger.jsonl", "step 3: every prompt, response, decision and artifact version")
    g = _package_gates(p)
    for c in comps:
        p.wire(builder, c)
        p.wire(api, c)
        p.wire(c, g["A5"])
        p.wire(c, record)
    p.wire(sources, g["A3"])
    p.wire(examples, g["A4"])
    p.wire(record, g["A7"])
    p.wire(env, g["A6"])
    p.wire(reviewer, g["A6"])
    if n is None:
        current = "Build one layer of one language, one batch at a time, until bash accept.sh passes A1 to A7."
    else:
        current = (f"Build one layer of {n['name']} ({nid}) at a time, from an openly licensed source, "
                   f"until bash accept.sh passes A1 to A7.")
    return p.painting(ASK_PACKAGES, current)


def script_module(reg):
    p = Painter()
    builder = p.add("actor", "Builder", "a person or any AI")
    rom = p.add("iface", "Romenagri tables", "the one transliterator; never a second one")
    uni = p.add("env", "Unicode character data", "normalisation and grapheme rules come from it")
    parts = [p.add("comp", name, note) for name, note in (
        ("normalisation and graphemes", "NFC and grapheme clusters for the script"),
        ("detection", "which script a run of text is in"),
        ("pivot to the hub", "Devanagari hub for Brahmic scripts through Romenagri; a declared hub otherwise"))]
    src = p.add("store", "data/SOURCES.json", "Unicode files and tables, with licences")
    rt = p.add("gate", "round trip", "text to hub and back is identical on a test corpus; every loss listed",
               "OPEN: no round-trip checker exists yet; building it is the first task of this quest")
    lic = p.add("gate", "licences", "every table has an allowed licence", "python3 -m tajziya accept <module> (A3)")
    for c in parts:
        p.wire(builder, c)
        p.wire(c, rt)
    p.wire(rom, parts[2])
    p.wire(uni, parts[0])
    p.wire(src, lic)
    return p.painting(ASK_QUESTS, "One script module: normalisation, detection and a pivot to its hub, "
                                  "with a round-trip proof listing every loss.")


def shared_engine(reg):
    p = Painter()
    builder = p.add("actor", "Builder", "a person or any AI")
    eng = p.add("comp", "the engine, in the core", "shared by phenomenon, never copied per language")
    one = p.add("comp", "first lineage's module", "the engine's first user")
    two = p.add("comp", "second lineage's module", "proof that it is shared, not bespoke")
    reg_store = p.add("store", "registry/engines.json", "which nodes need which engine")
    road = p.add("store", "roadmap/packages.json", "the package that builds it")
    conf = p.add("gate", "conformance", "every node still conforms", "python3 -m tajziya conformance")
    integ = p.add("gate", "both modules integrate", "acceptance passes for both lineages",
                  "bash accept.sh --integration, in each module")
    for c in (one, two):
        p.wire(eng, c)
        p.wire(c, integ)
    p.wire(builder, eng)
    p.wire(reg_store, eng)
    p.wire(road, eng)
    p.wire(eng, conf)
    return p.painting(ASK_QUESTS, "One shared engine in the core, proven on two lineages.")


def source_choice(reg):
    p = Painter()
    builder = p.add("actor", "Builder", "a person or any AI")
    cand = p.add("comp", "candidates", "the package's listed corpora and editions")
    pick = p.add("comp", "the chosen edition", "the best openly licensed one; the restricted one stays local")
    policy = p.add("store", "registry/licences.json", "which licences data may carry")
    src = p.add("store", "data/SOURCES.json", "URL, retrieval date, sha256, licence, attribution")
    a3 = p.add("gate", "A3 licences", "every data file allowed, or local_only in data/local/",
               "python3 -m tajziya accept <module> (A3)")
    p.wire(builder, cand)
    p.wire(cand, pick)
    p.wire(policy, pick)
    p.wire(pick, src)
    p.wire(src, a3)
    return p.painting(ASK_QUESTS, "One vetted source record, and the open alternative wherever the first "
                                  "choice is restricted.")


def coverage(reg):
    p = Painter()
    builder = p.add("actor", "Builder", "a person or any AI")
    rows = p.add("comp", "coverage rows for one node", "who holds which corpus, original or translation, "
                                                        "with the declared loss")
    cov = p.add("store", "registry/coverage.json", "the evidenced rows")
    classes = p.add("store", "registry/corpus_classes.json", "the corpus classes the rows refer to")
    elim = p.add("gate", "the elimination rule", "computes I, P or C from the rows",
                 "python3 -m tajziya eliminate <node>")
    consistent = p.add("gate", "registry consistency", "the registry still agrees with itself",
                       "bash ops/verify.sh (V06)")
    p.wire(builder, rows)
    p.wire(rows, cov)
    p.wire(classes, rows)
    p.wire(cov, elim)
    p.wire(cov, consistent)
    return p.painting(ASK_QUESTS, "Evidenced coverage rows for one node, so its status is computed, not assumed.")


def process_quests(reg):
    return {"language-layer": language_layer(reg), "script-module": script_module(reg),
            "shared-engine": shared_engine(reg), "source-choice": source_choice(reg), "coverage": coverage(reg)}


def problems(painting):
    p = []
    if painting.get("tool") != "AAB":
        p.append("not an AAB painting")
    intent = painting.get("intent") or {}
    if not str(intent.get("original", "")).strip():
        p.append("the original intent is empty")
    model = painting.get("model") or {}
    nodes = model.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        return p + ["the model has no nodes"]
    ids = [n.get("id") for n in nodes]
    if len(set(ids)) != len(ids):
        p.append("node ids repeat")
    for n in nodes:
        if n.get("type") not in TYPES:
            p.append(f"node {n.get('id')}: no AAB brush {n.get('type')}")
        if n.get("type") == "gate" and not str(n.get("oracle", "")).strip():
            p.append(f"gate {n.get('name')}: names no oracle")
    for w in model.get("wires", []):
        if len(w) != 2 or w[0] not in ids or w[1] not in ids:
            p.append(f"wire {w} joins nodes that do not exist")
    if model.get("nextId", 0) <= max(i for i in ids if isinstance(i, int)):
        p.append("nextId would reuse an id")
    return p
