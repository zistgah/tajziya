# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""Commonalities are computed from the registry, not asserted.

A node needs the engines of its lineage (the language axis) and of its scripts (the script
axis). An engine needed by more than one lineage is common. Families are genealogical;
engines are not, which is why the two are kept on separate axes.
"""


def report(reg):
    rows = {}
    for nid, n in reg.nodes.items():
        lang, script = reg.engines_of(n)
        lin = n["lineage"]
        fam = reg.lineages[lin]["family"]
        for e in lang + script:
            r = rows.setdefault(e, {"nodes": [], "lineages": [], "families": []})
            for key, val in (("nodes", nid), ("lineages", lin), ("families", fam)):
                if val not in r[key]:
                    r[key].append(val)
    out = []
    for e, spec in reg.engines.items():
        r = rows.get(e, {"nodes": [], "lineages": [], "families": []})
        out.append({"id": e, "axis": spec["axis"], "package": spec["package"], **r,
                    "reach": {k: len(r[k]) for k in ("nodes", "lineages", "families")},
                    "common": len(r["lineages"]) > 1})
    out.sort(key=lambda r: (-r["reach"]["lineages"], -r["reach"]["nodes"], r["id"]))
    by_axis = {}
    for r in out:
        a = by_axis.setdefault(r["axis"], {"engines": 0, "common": 0})
        a["engines"] += 1
        a["common"] += int(r["common"])
    return {"engines": out, "by_axis": by_axis}


def script_reach(reg, codes):
    """Nodes and lineages served by a set of scripts, for example every cuneiform."""
    nodes = [nid for nid, n in reg.nodes.items() if set(n["scripts"]) & set(codes)]
    return {"scripts": list(codes), "nodes": nodes,
            "lineages": sorted({reg.nodes[x]["lineage"] for x in nodes})}
