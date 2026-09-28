#!/usr/bin/env python3
# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""Write the process quests as AAB paintings into quests/, or check that they are current.

    python3 tools/quests.py            write quests/<name>.aab.json
    python3 tools/quests.py --check    fail if any painting is stale, missing or invalid
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from tajziya import quests  # noqa: E402
from tajziya.registry import load  # noqa: E402


def render(obj):
    return json.dumps(obj, indent=1, ensure_ascii=False) + "\n"


def main(argv):
    check = "--check" in argv
    out, bad = os.path.join(ROOT, "quests"), []
    for name, painting in quests.process_quests(load()).items():
        bad += [f"{name}: {x}" for x in quests.problems(painting)]
        p = os.path.join(out, f"{name}.aab.json")
        text = render(painting)
        if check:
            have = open(p, encoding="utf-8").read() if os.path.exists(p) else None
            if have != text:
                bad.append(f"quests/{name}.aab.json is {'missing' if have is None else 'stale'}; run tools/quests.py")
        else:
            os.makedirs(out, exist_ok=True)
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(text)
    for b in bad:
        print(f"quests: {b}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
