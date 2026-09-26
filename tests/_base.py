# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""Shared test setup: the package on the path, and a scratch folder inside the repository."""
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
SCRATCH = os.path.join(ROOT, "tests", ".scratch")


def scratch(name):
    p = os.path.join(SCRATCH, name)
    shutil.rmtree(p, ignore_errors=True)
    os.makedirs(p)
    return p
