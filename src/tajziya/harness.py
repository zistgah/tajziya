# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""D4. The conformance harness is the definition of a conforming parser.

TJZ-C1  a not_built layer refuses by NotBuilt naming existing packages; a built one answers
TJZ-C2  a not_built layer never returns a value
TJZ-C3  every expected reading of a reference input is returned
TJZ-C4  every reading joins back to its input, proved through join, not self-reported
TJZ-C6  the CoNLL-U output of every reference input is structurally valid
"""
from . import conllu
from .types import LAYERS, METHODS, NotBuilt

PROBE = "probe"


SCRIPT_LAYERS = ("L1", "L2")
SCRIPT_METHODS = {"L1": "pivot", "L2": "orthography"}


def check_script(parser, reg):
    """The layer conditions for a script module or frame: L1 and L2 only."""
    return _layer_findings(parser, reg, SCRIPT_LAYERS, SCRIPT_METHODS)


def check(parser, node, reg):
    found = _layer_findings(parser, reg, LAYERS, METHODS)
    return found + _reference_findings(parser, reg)


def _layer_findings(parser, reg, names, methods):
    found = []
    layers = parser.layers()
    for L in names:
        state = layers.get(L)
        fn = getattr(parser, methods[L])
        if state == "not_built":
            try:
                value = fn(PROBE)
            except NotBuilt as e:
                unknown = [p for p in e.packages if p not in reg.packages]
                ok = bool(e.packages) and not unknown
                found.append(("TJZ-C1", ok, f"{L} refuses" if ok else
                              f"{L} refuses naming {list(e.packages) or 'no package'}; unknown: {unknown}"))
                continue
            except Exception as e:
                found.append(("TJZ-C1", False, f"{L} raised {type(e).__name__} instead of NotBuilt"))
                continue
            found.append(("TJZ-C2", False, f"{L} is not_built and returned {value!r:.60}"))
        else:
            refs = getattr(parser, "REFERENCE", None) or {}
            probe = getattr(parser, "REFERENCE_INPUT", {}).get(L) or (next(iter(refs)) if L == "L3s" and refs else PROBE)
            try:
                fn(probe)
                found.append(("TJZ-C1", True, f"{L} ({state}) answers"))
            except NotBuilt as e:
                found.append(("TJZ-C1", False, f"{L} is declared {state} but refuses: {e}"))
    return found


def _reference_findings(parser, reg):
    found = []
    layers = parser.layers()
    reference = getattr(parser, "REFERENCE", None)
    if reference and layers.get("L3s") in ("built", "wired_unproven"):
        for text, expected in reference.items():
            try:
                res = parser.segment(text)
            except Exception as e:
                found.append(("TJZ-C3", False, f"{text}: segment raised {type(e).__name__}: {e}"))
                continue
            got = {seg.words for lat in res.tokens for seg in lat.alternatives}
            missing = [tuple(e) for e in expected if tuple(e) not in got]
            found.append(("TJZ-C3", not missing, f"{text}: " + (
                "every expected reading returned" if not missing else f"missing {missing}")))
            bad = [seg.words for lat in res.tokens for seg in lat.alternatives
                   if parser.join(seg.words) != lat.token]
            found.append(("TJZ-C4", not bad, f"{text}: " + (
                "every reading joins back" if not bad else f"does not join back: {bad}")))
            blocks = conllu.sentences(res)
            ok = isinstance(blocks, list) and all(conllu.valid(b) for b in blocks)
            found.append(("TJZ-C6", ok, f"{text}: CoNLL-U " + ("valid" if ok else "invalid")))
    return found


def run_all(reg, only=None):
    summary = {"nodes": 0, "findings": 0, "failed": []}
    bound_coverage = [n for n in reg.bindings if n not in reg.nodes and reg.has_node(n)]
    for nid in list(reg.nodes) + bound_coverage:
        if only and nid not in only:
            continue
        for cond, ok, detail in check(reg.bind(nid), reg.node(nid), reg):
            summary["findings"] += 1
            if not ok:
                summary["failed"].append({"node": nid, "condition": cond, "detail": detail})
        summary["nodes"] += 1
    return summary


def run_coverage(reg, sample=None):
    """Conformance over the coverage nodes: every one, or every n-th when sample is n."""
    ids = reg.coverage_ids()
    if sample:
        ids = ids[::sample]
    summary = {"nodes": 0, "findings": 0, "failed": []}
    for nid in ids:
        for cond, ok, detail in check(reg.bind(nid), reg.node(nid), reg):
            summary["findings"] += 1
            if not ok:
                summary["failed"].append({"node": nid, "condition": cond, "detail": detail})
        summary["nodes"] += 1
    return summary


def run_scripts(reg, only=None):
    summary = {"scripts": 0, "findings": 0, "failed": []}
    for code in reg.script_ids():
        if only and code not in only:
            continue
        for cond, ok, detail in check_script(reg.bind_script(code), reg):
            summary["findings"] += 1
            if not ok:
                summary["failed"].append({"script": code, "condition": cond, "detail": detail})
        summary["scripts"] += 1
    return summary
