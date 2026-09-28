# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
import hashlib
import json
import os
import shutil
import subprocess
import sys
import unittest

import _base
from tajziya import accept

ENV = dict(os.environ, PYTHONPATH=os.path.join(_base.ROOT, "src"), PYTHONDONTWRITEBYTECODE="1")


def failed(rows):
    return {r["id"] for r in rows if r["state"] == "FAIL"}


class TestAcceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        out = os.path.join("tests", ".scratch", "accept-src")
        r = subprocess.run([sys.executable, "tools/langpack.py", "akk", "--out", out, "--quiet"], cwd=_base.ROOT,
                           env=ENV, capture_output=True, text=True)
        assert r.returncode == 0, r.stdout + r.stderr
        cls.pkg = os.path.join(_base.ROOT, out, "tajziya-lang-akk")

    def fresh(self, tag):
        d = os.path.join(_base.SCRATCH, "accept-" + tag)
        shutil.rmtree(d, ignore_errors=True)
        shutil.copytree(self.pkg, d)
        return d

    def edit_json(self, d, rel, fn):
        p = os.path.join(d, rel)
        with open(p, encoding="utf-8") as fh:
            doc = json.load(fh)
        fn(doc)
        with open(p, "w", encoding="utf-8") as fh:
            json.dump(doc, fh)

    def add_source(self, d, licence, rel="data/lexicon.tsv", sha=None, **extra):
        p = os.path.join(d, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write("a\tb\n")
        digest = sha or hashlib.sha256(open(p, "rb").read()).hexdigest()
        src = {"id": "s1", "title": "t", "url": "u", "retrieved": "2026-09-26", "licence": licence,
               "attribution": "a", "files": [{"path": rel, "sha256": digest}], **extra}
        self.edit_json(d, "data/SOURCES.json", lambda doc: doc["sources"].append(src))

    def test_the_reference_module_is_accepted_in_place(self):
        self.assertEqual(failed(accept.run(os.path.join(_base.ROOT, "modules", "cls"), integration=True)), set())

    def test_a_generated_package_is_accepted_in_isolation_and_in_integration(self):
        d = self.fresh("ok")
        rows = accept.run(d, integration=True, scratch=os.path.join(d, ".deps", "integration"))
        self.assertEqual(failed(rows), set())
        self.assertEqual([r["id"] for r in rows], ["A1", "A2", "A3", "A4", "A5", "A6", "A7"])

    def test_an_open_licence_with_its_file_listed_passes(self):
        d = self.fresh("open")
        self.add_source(d, "CC BY-SA 4.0")
        self.assertEqual(failed(accept.run(d)), set())

    def test_an_unlisted_data_file(self):
        d = self.fresh("unlisted")
        with open(os.path.join(d, "data", "lexicon.tsv"), "w", encoding="utf-8") as fh:
            fh.write("x\n")
        self.assertIn("A3", failed(accept.run(d)))

    def test_a_non_commercial_licence(self):
        d = self.fresh("nc")
        self.add_source(d, "CC BY-NC-SA 4.0")
        self.assertIn("A3", failed(accept.run(d)))

    def test_a_file_that_does_not_match_its_pin(self):
        d = self.fresh("sha")
        self.add_source(d, "CC BY-SA 4.0", sha="0" * 64)
        self.assertIn("A3", failed(accept.run(d)))

    def test_an_mit_source_without_its_notice(self):
        d = self.fresh("notice")
        self.add_source(d, "MIT")
        self.assertIn("A3", failed(accept.run(d)))

    def test_local_only_material_outside_data_local(self):
        d = self.fresh("local")
        self.add_source(d, "not stated", local_only=True)
        self.assertIn("A3", failed(accept.run(d)))

    def test_a_built_layer_without_examples(self):
        d = self.fresh("built")

        def f(m):
            m["layers"]["L3s"] = "built"
            m["scope_excludes"] = ["everything outside one test"]
        self.edit_json(d, "module.json", f)
        self.assertTrue({"A4", "A5"} <= failed(accept.run(d)))

    def test_an_example_citing_no_listed_source(self):
        d = self.fresh("example")
        self.edit_json(d, "reference/examples.json", lambda doc: doc["examples"].append(
            {"layer": "L3s", "input": "x", "readings": [["x"]], "source": "nowhere", "locator": "p. 1"}))
        self.assertIn("A4", failed(accept.run(d)))

    def test_a_script_naming_a_path_outside(self):
        d = self.fresh("outside")
        with open(os.path.join(d, "python", "akk_v0", "__init__.py"), "a", encoding="utf-8") as fh:
            fh.write("CACHE = '" + "/t" + "mp/x'\n")
        self.assertIn("A2", failed(accept.run(d)))

    def test_an_unexpected_entry(self):
        d = self.fresh("entry")
        os.makedirs(os.path.join(d, "notes"))
        self.assertIn("A2", failed(accept.run(d)))

    def test_a_port_that_answers_an_unbuilt_layer(self):
        d = self.fresh("liar")
        p = os.path.join(d, "python", "akk_v0", "__init__.py")
        with open(p, encoding="utf-8") as fh:
            src = fh.read()
        anchor = '        api.refuse(self, "L3m", "not yet written in this module")'
        self.assertEqual(src.count(anchor), 1)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(src.replace(anchor, "        return [(word,)]"))
        self.assertIn("A5", failed(accept.run(d)))


if __name__ == "__main__":
    unittest.main()
