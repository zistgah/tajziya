# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""The process quests are AAB paintings the studio can import, and every gate names its oracle."""
import copy
import json
import os
import unittest

from tajziya import quests
from tajziya.registry import load

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Quests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reg = load()

    def test_every_process_quest_is_a_valid_painting_on_disk(self):
        for name, painting in quests.process_quests(self.reg).items():
            self.assertEqual(quests.problems(painting), [], name)
            with open(os.path.join(ROOT, "quests", f"{name}.aab.json"), encoding="utf-8") as fh:
                self.assertEqual(json.load(fh), painting, name)

    def test_the_shape_is_what_the_studio_imports(self):
        p = quests.language_layer(self.reg, "akk")
        self.assertEqual((p["tool"], p["version"]), ("AAB", "0.2.0"))
        self.assertTrue(p["model"]["nodes"] and "wires" in p["model"])
        self.assertEqual(set(p["intent"]), {"original", "current"})
        self.assertIn("build a package which can be handed over", p["intent"]["original"])

    def test_a_node_quest_carries_that_nodes_engines_and_packages(self):
        p = quests.language_layer(self.reg, "akk")
        seg = next(n for n in p["model"]["nodes"] if n["name"].startswith("L3s"))
        self.assertIn("logogram", seg["note"])
        self.assertIn("P-ENG-06", seg["note"])
        self.assertIn("Akkadian", p["intent"]["current"])

    def test_the_check_bites(self):
        good = quests.language_layer(self.reg, "akk")
        for mutate, why in (
                (lambda q: q.update(tool="not"), "not an AAB painting"),
                (lambda q: q["intent"].update(original=""), "intent"),
                (lambda q: next(n for n in q["model"]["nodes"] if n["type"] == "gate").update(oracle=""), "oracle"),
                (lambda q: q["model"]["wires"].append([1, 999]), "do not exist"),
                (lambda q: q["model"]["nodes"][0].update(type="cloud"), "brush")):
            bad = copy.deepcopy(good)
            mutate(bad)
            self.assertTrue(any(why in x for x in quests.problems(bad)), why)


if __name__ == "__main__":
    unittest.main()
