# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""The matrix's elimination rule, run on recorded evidence (poster I §20, poster III).

    U_i = K_i - Recover(K_not_i, R, X)
    U_i empty      candidate for compression (C)
    U_i not empty  retained (I)
    U_i uncertain  provisional until the corpus is tested (P)

Translation is never recovery. A recovering relation needs an explicitly empty loss list
and evidence. The minimum is not certified while the universe or the loss function is open.
"""
RECOVERING = ("original", "stage_of")


def decide(node_id, rows):
    mine = [r for r in rows if node_id in r.get("cells", {})]
    if not mine:
        return {"computed": "P", "why": "untested: no coverage row names this node",
                "unique": [], "recovered": [], "uncertain": []}
    unique, recovered, uncertain = [], [], []
    for r in mine:
        rel = r["cells"][node_id].get("relation")
        if rel == "unknown":
            uncertain.append(r["id"])
            continue
        if rel != "original":
            continue
        by = sorted(j for j, c in r["cells"].items()
                    if j != node_id and c.get("relation") in RECOVERING
                    and c.get("loss") == [] and c.get("evidence"))
        if by:
            recovered.append({"row": r["id"], "by": by})
        else:
            unique.append(r["id"])
    if unique:
        computed, why = "I", "at least one recorded corpus is held only here"
    elif uncertain:
        computed, why = "P", "a coverage cell for this node is unknown"
    else:
        computed, why = "C", "every recorded original is recovered without declared loss"
    return {"computed": computed, "why": why, "unique": unique, "recovered": recovered,
            "uncertain": uncertain}


def minimum(reg, coverage=None):
    cov = coverage if coverage is not None else reg.coverage
    rows = cov.get("rows", [])
    decisions, L, S, U = {}, [], [], []
    for nid, n in reg.nodes.items():
        status = n["status"]["poster"]
        if status == "S":
            S.append(nid)
            continue
        if status == "U":
            U.append(nid)
            continue
        d = decide(nid, rows)
        decisions[nid] = d
        if d["computed"] != "C":
            L.append(nid)
    G = sorted({c for nid in L + S + U for c in reg.node(nid)["scripts"]})
    C = [c["id"] for c in reg.corpus_classes]
    frozen = cov.get("frozen", {})
    reasons = []
    if not frozen.get("universe"):
        reasons.append("the corpus universe is not frozen")
    if not frozen.get("loss_function"):
        reasons.append("the loss function is not frozen")
    untested = [k for k, d in decisions.items() if d["why"].startswith("untested")]
    if untested:
        reasons.append(f"{len(untested)} of {len(decisions)} candidate nodes are untested")
    comparison = {"agrees": [], "unevidenced": [], "differs": []}
    for nid, d in decisions.items():
        poster = reg.node(nid)["status"]["poster"]
        if d["why"].startswith("untested"):
            comparison["unevidenced"].append(nid)
        elif d["computed"] == poster:
            comparison["agrees"].append(nid)
        else:
            comparison["differs"].append(nid)
    return {"L": L, "S": {"nodes": S, "stage_trees": {k: v["stages"] for k, v in
                                                      reg.nodes_doc["stage_trees"].items()}},
            "G": G, "C": C, "corpus_objects": U, "certified": not reasons,
            "scope": "relative to the declared universe and loss function only",
            "reasons": reasons, "decisions": decisions, "comparison": comparison}
