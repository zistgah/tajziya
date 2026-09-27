# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
import hashlib
import os
import subprocess
import sys
import unittest

import _base
from tajziya.registry import load

ENV = dict(os.environ, PYTHONPATH=os.path.join(_base.ROOT, "src"), PYTHONDONTWRITEBYTECODE="1")


def langpack(*args):
    return subprocess.run([sys.executable, "tools/langpack.py", *args, "--quiet"], cwd=_base.ROOT, env=ENV,
                          capture_output=True, text=True)


def packages(out):
    d = os.path.join(_base.ROOT, out)
    return sorted(x for x in os.listdir(d) if x.startswith("tajziya-lang-"))


class TestLangpack(unittest.TestCase):
    def test_every_remaining_node_gets_an_accepted_package(self):
        out = os.path.join("tests", ".scratch", "lp-all")
        r = langpack("--remaining", "--out", out)
        self.assertEqual(r.returncode, 0, r.stdout)
        frames = sorted(n for n, b in load().bindings.items() if b["kind"] == "frame")
        self.assertEqual(packages(out), [f"tajziya-lang-{n}" for n in frames])

    def test_an_iso_code_names_every_node_carrying_it(self):
        out = os.path.join("tests", ".scratch", "lp-grc")
        self.assertEqual(langpack("grc", "--out", out).returncode, 0)
        self.assertEqual(packages(out), ["tajziya-lang-grc", "tajziya-lang-grc-byz", "tajziya-lang-grc-koine"])

    def test_the_archives_are_reproducible(self):
        digests = []
        for k in ("a", "b"):
            out = os.path.join("tests", ".scratch", f"lp-rep-{k}")
            self.assertEqual(langpack("akk", "lat", "--out", out, "--tar", "--bundle").returncode, 0)
            with open(os.path.join(_base.ROOT, out, "dist", "tajziya-language-packages.tar.gz"), "rb") as fh:
                digests.append(hashlib.sha256(fh.read()).hexdigest())
        self.assertEqual(digests[0], digests[1])

    def test_an_output_folder_outside_the_repository_is_refused(self):
        self.assertEqual(langpack("akk", "--out", os.path.join(os.pardir, "x")).returncode, 1)

    def test_an_unknown_code_is_refused(self):
        self.assertNotEqual(langpack("xyz").returncode, 0)


if __name__ == "__main__":
    unittest.main()
