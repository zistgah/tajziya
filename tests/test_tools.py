# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import unittest

import _base
from tajziya import commonalities, reconcile
from tajziya.registry import load
from tajziya.types import NotBuilt

ROOT = _base.ROOT
ENV = dict(os.environ, PYTHONPATH=os.path.join(ROOT, "src"), PYTHONDONTWRITEBYTECODE="1")


def run(*args):
    return subprocess.run([sys.executable, *args], cwd=ROOT, env=ENV, capture_output=True, text=True)


class TestCommonalities(unittest.TestCase):
    def test_a_node_needs_its_lineage_and_its_scripts(self):
        reg = load()
        lang, script = reg.engines_of(reg.node("cls"))
        self.assertEqual((lang, script), (["juncture", "paradigm", "compounding"], ["abugida"]))
        lang, script = reg.engines_of(reg.node("egy"))
        self.assertEqual(lang, ["root_pattern"])
        self.assertEqual(set(script), {"logogram", "vocalisation", "unspaced"})

    def test_every_engine_is_reported_on_one_axis(self):
        rep = commonalities.report(load())
        self.assertEqual({e["id"] for e in rep["engines"]}, set(load().engines))
        self.assertTrue(all(e["axis"] in ("language", "script") for e in rep["engines"]))


class TestReconcile(unittest.TestCase):
    def test_the_prior_template_is_reconciled_not_copied(self):
        r = reconcile.reconcile(load())
        self.assertEqual(r["prior_rows"], 90)
        prior = {x["prior"]: x["prior_family"] for x in r["family_differs"]}
        self.assertEqual(prior.get("sanskrit_grantha"), "Dravidian")
        self.assertEqual(prior.get("gandhari"), "Ancient")


class TestTools(unittest.TestCase):
    def test_the_site_is_current(self):
        out = run("tools/site_gen.py", "--check")
        self.assertEqual(out.returncode, 0, out.stdout)

    def test_node_new_makes_a_port_that_refuses_like_the_stub(self):
        out_dir = _base.scratch("node_new")
        r = run("tools/node_new.py", "--node", "akk", "--impl", "akkadian_v0", "--out", out_dir)
        self.assertEqual(r.returncode, 0, r.stdout)
        spec = importlib.util.spec_from_file_location(
            "tajziya.ports.akkadian_v0", os.path.join(out_dir, "akkadian_v0", "__init__.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        reg = load()
        port = mod.make(reg.node("akk"), reg)
        with self.assertRaises(NotBuilt) as cm:
            port.segment("x")
        self.assertIn("P-LIN-semitic", cm.exception.packages)
        self.assertNotEqual(run("tools/node_new.py", "--node", "akk", "--impl", "Akkadian").returncode, 0)

    def test_the_command_line_answers_and_refuses(self):
        self.assertEqual(run("-m", "tajziya", "segment", "--node", "cls", "neti").returncode, 0)
        self.assertEqual(run("-m", "tajziya", "segment", "--node", "akk", "x").returncode, 3)
        self.assertEqual(run("-m", "tajziya", "doctor").returncode, 0)

    def test_vendored_files_match_their_pins(self):
        with open(os.path.join(ROOT, "vendor", "sanskrit_parser", "UPSTREAM.json"), encoding="utf-8") as fh:
            up = json.load(fh)
        for f in up["files"]:
            with open(os.path.join(ROOT, "vendor", "sanskrit_parser", f["file"]), "rb") as fh:
                self.assertEqual(hashlib.sha256(fh.read()).hexdigest(), f["vendored_sha256"], f["file"])
        with open(os.path.join(ROOT, "descriptor.json"), encoding="utf-8") as fh:
            pin = json.load(fh)["vendors_verbatim"][0]
        with open(os.path.join(ROOT, pin["path"]), "rb") as fh:
            self.assertEqual(hashlib.sha256(fh.read()).hexdigest(), pin["sha256"])


@unittest.skipUnless(shutil.which("node"), "node is not installed; parity is unjudged")
class TestParity(unittest.TestCase):
    def test_python_and_javascript_agree(self):
        self.assertEqual(run("tests/parity.py").returncode, 0)

    def test_parity_bites_on_a_changed_rule(self):
        d = os.path.join(_base.scratch("js_mut"), "js")
        shutil.copytree(os.path.join(ROOT, "vendor", "sanskrit_parser", "js"), d)
        p = os.path.join(d, "sandhi.js")
        with open(p, encoding="utf-8") as fh:
            text = fh.read()
        anchor = 'e: "ai", o: "au" });'
        self.assertEqual(text.count(anchor), 1)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(text.replace(anchor, 'e: "e", o: "au" });'))
        self.assertEqual(run("tests/parity.py", d).returncode, 1)


if __name__ == "__main__":
    unittest.main()


class TestStaysInFolder(unittest.TestCase):
    def test_data_import_refuses_a_source_outside_the_folder(self):
        out = run("-m", "tajziya", "data", "import", os.path.join(os.sep, "nonexistent-outside", "x.zip"))
        self.assertEqual(out.returncode, 1)
        self.assertIn("clause 7", out.stdout)

    def test_vendor_import_refuses_an_archive_outside_the_folder(self):
        out = run("tools/vendor_import.py", "--zip", os.path.join(os.sep, "nonexistent-outside", "x.zip"))
        self.assertEqual(out.returncode, 1)
