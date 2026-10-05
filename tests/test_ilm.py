# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""The ILM registry's languages and scripts: coverage nodes, script frames and their packages."""
import json
import os
import shutil
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import langpack  # noqa: E402
from tajziya import accept, harness  # noqa: E402
from tajziya.registry import load  # noqa: E402
from tajziya.types import NotBuilt  # noqa: E402

SCRATCH = os.path.join(ROOT, "tests", ".scratch", "ilm")


class Coverage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reg = load()

    def test_every_listed_language_is_a_curated_or_a_coverage_node(self):
        reg = self.reg
        cov = set(reg.coverage_ids())
        self.assertEqual(len(cov), len(reg.ilm_languages) - len(set(reg.ilm_languages) & reg.held_codes()))
        self.assertFalse(cov & set(reg.nodes))
        self.assertTrue(all(reg.has_node(c) for c in list(cov)[:50]))

    def test_coverage_refusals_name_the_profile_package_and_curated_ones_are_unchanged(self):
        reg = self.reg
        self.assertEqual(reg.refusal(reg.node("aaa"), "L0"), ((), ("P-L0-01", "P-PROF-01")))
        self.assertEqual(reg.refusal(reg.node("cls"), "L0"), ((), ("P-L0-01", "P-LIN-indo_aryan")))
        self.assertIn("P-PROF-01", reg.packages)

    def test_every_coverage_node_and_script_conforms(self):
        self.assertEqual(harness.run_coverage(self.reg)["failed"], [])
        self.assertEqual(harness.run_scripts(self.reg)["failed"], [])

    def test_script_frames_refuse_or_answer_by_encoding(self):
        reg = self.reg
        deva, afak = reg.bind_script("Deva"), reg.bind_script("Afak")
        self.assertEqual(deva.orthography("\u0915")["layer"], "L2")
        with self.assertRaises(NotBuilt) as e:
            afak.orthography("x")
        self.assertIn("P-ENG-11", e.exception.packages)
        with self.assertRaises(NotBuilt) as e:
            deva.pivot("x")
        self.assertEqual(tuple(e.exception.packages), ("P-ENG-09",))
        with self.assertRaises(NotBuilt) as e:
            reg.bind_script("Adlm").pivot("x")
        self.assertEqual(tuple(e.exception.packages), ("P-L1-01",))


class Packages(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        shutil.rmtree(SCRATCH, ignore_errors=True)
        cls.reg = load()
        rc = langpack.main(["aaa", "Deva", "Afak", "lat", "--out", "tests/.scratch/ilm/p", "--quiet"])
        assert rc == 0

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(SCRATCH, ignore_errors=True)

    def _state(self, pkg):
        return {r["id"]: r["state"] for r in accept.run(os.path.join(SCRATCH, "p", pkg), reg=self.reg)}

    def _copy(self, pkg, name):
        dst = os.path.join(SCRATCH, "p", name)
        shutil.rmtree(dst, ignore_errors=True)
        shutil.copytree(os.path.join(SCRATCH, "p", pkg), dst)
        return dst, name

    def test_generated_coverage_and_script_packages_pass_as_handed_over(self):
        for pkg in ("tajziya-lang-aaa", "tajziya-script-Deva", "tajziya-script-Afak", "tajziya-lang-lat"):
            self.assertTrue(all(s == "PASS" for s in self._state(pkg).values()), pkg)

    def test_a_script_module_that_claims_a_pivot_with_nothing_behind_it_fails(self):
        d, name = self._copy("tajziya-script-Deva", "claims-Deva")
        p = os.path.join(d, "module.json")
        man = json.load(open(p, encoding="utf-8"))
        man["layers"]["L1"] = "built"
        man["scope_excludes"] = ["a claim with nothing behind it"]
        json.dump(man, open(p, "w", encoding="utf-8"))
        st = self._state(name)
        self.assertEqual(st["A4"], "FAIL")
        self.assertEqual(st["A5"], "FAIL")

    def test_an_unknown_script_code_fails_the_manifest(self):
        d, name = self._copy("tajziya-script-Afak", "unknown-Afak")
        p = os.path.join(d, "module.json")
        man = json.load(open(p, encoding="utf-8"))
        man["script"] = "Zzzq"
        json.dump(man, open(p, "w", encoding="utf-8"))
        self.assertEqual(self._state(name)["A1"], "FAIL")


if __name__ == "__main__":
    unittest.main()
