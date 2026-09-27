# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
import copy
import os
import re
import unittest

import _base  # noqa: F401
from tajziya import modules
from tajziya.registry import load, path


class TestModules(unittest.TestCase):
    def test_discovery_finds_the_reference_module(self):
        self.assertIn("cls", modules.discover())

    def test_cls_is_bound_as_a_module_and_loaded_by_path(self):
        reg = load()
        self.assertEqual(reg.bindings["cls"]["kind"], "module")
        self.assertTrue(type(reg.bind("cls")).__module__.startswith("tajziya_modules."))

    def test_the_reference_module_imports_only_the_api(self):
        b = load().bindings["cls"]
        with open(path(*b["module"].split("/"), "python", b["implementation"], "__init__.py"), encoding="utf-8") as fh:
            src = fh.read()
        self.assertEqual(set(re.findall(r"^\s*(?:from|import)\s+(tajziya[\w.]*)", src, re.M)), {"tajziya"})
        self.assertIn("from tajziya import api", src)


class TestManifestBites(unittest.TestCase):
    def setUp(self):
        self.reg = load()
        self.dir = path("modules", "cls")
        self.man = modules.manifest(self.dir)

    def probs(self, **change):
        m = copy.deepcopy(self.man)
        m.update(change)
        return modules.problems(m, self.reg, self.dir)

    def test_the_reference_manifest_is_clean(self):
        self.assertEqual(self.probs(), [])

    def test_another_api_version(self):
        self.assertTrue(any("API" in p for p in self.probs(api="2")))

    def test_an_unknown_node(self):
        self.assertTrue(any("not in the registry" in p for p in self.probs(node="xxx")))

    def test_an_unversioned_implementation(self):
        self.assertTrue(any("versioned" in p for p in self.probs(implementation="Akkadian")))

    def test_a_built_layer_that_excludes_nothing(self):
        self.assertTrue(any("scope_excludes" in p for p in self.probs(scope_excludes=[])))

    def test_an_entry_outside_the_module(self):
        outside = os.path.join(os.pardir, os.pardir, "src", "tajziya", "api.py")
        self.assertTrue(any("outside the module" in p for p in self.probs(entry=outside)))


if __name__ == "__main__":
    unittest.main()
