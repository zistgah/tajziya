# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""The common output: CoNLL-U, one sentence per reading, a multiword token for a joined form.

Every reading is emitted. When the readings exceed the enumeration cap, the answer is
Unknown rather than a truncated list, because a truncated list reads as the whole.
"""
import itertools

from ._vendor.unknown import Unknown

CAP = 64


def _row(i, form, misc="_"):
    return "\t".join([str(i), form, "_", "_", "_", "_", "_", "_", "_", misc])


def sentences(result, cap=CAP):
    alts = [lat.alternatives or (None,) for lat in result.tokens]
    total = 1
    for a in alts:
        total *= len(a)
    if total > cap:
        return Unknown(f"{total} readings exceed the enumeration cap of {cap}", ("the lattice form",))
    text = " ".join(lat.token for lat in result.tokens)
    out = []
    for k, combo in enumerate(itertools.product(*alts), 1):
        lines = [f"# sent_id = {result.node}-{k}", f"# text = {text}", f"# reading = {k} of {total}"]
        i = 0
        for lat, seg in zip(result.tokens, combo):
            if seg is None:
                i += 1
                lines.append(_row(i, lat.token, "Segmentation=NotFound"))
                continue
            if len(seg.words) > 1:
                lines.append("\t".join([f"{i + 1}-{i + len(seg.words)}", lat.token] + ["_"] * 8))
            for w_idx, w in enumerate(seg.words):
                i += 1
                misc = "_"
                if w_idx < len(seg.junctions):
                    j = seg.junctions[w_idx]
                    misc = f"Junction={j.left}+{j.right}>{j.merged}"
                lines.append(_row(i, w, misc))
        out.append("\n".join(lines) + "\n")
    return out


def valid(block):
    """Ten tab-separated fields per word line, integer or range ids, no empty field."""
    for line in block.rstrip("\n").split("\n"):
        if line.startswith("#"):
            continue
        f = line.split("\t")
        if len(f) != 10 or any(x == "" for x in f):
            return False
        if "-" in f[0]:
            a, _, b = f[0].partition("-")
            if not (a.isdigit() and b.isdigit() and int(a) < int(b)):
                return False
            if any(x != "_" for x in f[2:9]):
                return False
        elif not f[0].isdigit():
            return False
    return True
