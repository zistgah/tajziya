# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""The 30 Aug ILM template, reconciled against this registry rather than copied into it."""
import csv
import json

from .registry import path


def reconcile(reg):
    with open(path("registry", "prior", "SOURCE.json"), encoding="utf-8") as fh:
        src = json.load(fh)
    with open(path("registry", "prior", "ilm-template.csv"), encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    mapping, matched, outside, differs, labels = src["map"], [], [], [], {}
    for r in rows:
        nid = mapping.get(r["language"])
        if not nid:
            outside.append(r["language"])
            continue
        node = reg.node(nid)
        lpath = reg.lineages[node["lineage"]]["path"]
        label = r["family"].strip().lower().replace("-", "_")
        entry = {"prior": r["language"], "prior_family": r["family"], "prior_script": r["script"],
                 "node": nid, "path": lpath}
        (matched if label in lpath else differs).append(entry)
        labels.setdefault(node["lineage"], set()).add(r["family"])
    return {"source": src["from"], "prior_rows": len(rows), "matched": len(matched),
            "outside_posters": sorted(outside), "family_differs": differs,
            "one_lineage_several_labels": {k: sorted(v) for k, v in labels.items() if len(v) > 1}}
