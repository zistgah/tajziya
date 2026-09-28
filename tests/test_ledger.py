# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""The step-3 configuration record: append-only, hash-chained, and refusing tampering."""
import json
import os
import shutil
import unittest

from tajziya import ledger

HERE = os.path.dirname(os.path.abspath(__file__))
NOW = "2026-09-27T00:00:00Z"


class Ledger(unittest.TestCase):
    def setUp(self):
        self.d = os.path.join(HERE, ".scratch", "ledger-test")
        shutil.rmtree(self.d, ignore_errors=True)
        os.makedirs(self.d)
        with open(os.path.join(self.d, "port.py"), "w") as fh:
            fh.write("v1")

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def fill(self):
        ledger.append(self.d, "intent", text="segment Akkadian logograms", now=NOW)
        ledger.append(self.d, "prompt", text="propose the sign table", now=NOW)
        ledger.append(self.d, "response", text="a table", actor="any AI", now=NOW)
        ledger.append(self.d, "decision", text="accepted with two corrections", actor="builder", now=NOW)
        ledger.append(self.d, "artifact", file="port.py", now=NOW)

    def lines(self):
        with open(os.path.join(self.d, ledger.LEDGER), encoding="utf-8") as fh:
            return fh.read().splitlines()

    def write(self, lines):
        with open(os.path.join(self.d, ledger.LEDGER), "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")

    def test_a_clean_record_verifies_and_chains(self):
        self.fill()
        self.assertEqual(ledger.verify(self.d, strict=True), [])
        entries = ledger.read(self.d)
        self.assertEqual([e["seq"] for e in entries], [1, 2, 3, 4, 5])
        self.assertEqual(entries[0]["prev"], ledger.GENESIS)
        self.assertTrue(all(entries[i]["prev"] == entries[i - 1]["hash"] for i in range(1, 5)))
        self.assertEqual(entries[2]["actor"], "any AI")

    def test_an_edited_entry_is_caught(self):
        self.fill()
        lines = self.lines()
        lines[2] = lines[2].replace("a table", "a better table")
        self.write(lines)
        self.assertTrue(any("entry 3" in p for p in ledger.verify(self.d)))

    def test_a_removed_entry_breaks_the_chain(self):
        self.fill()
        lines = self.lines()
        del lines[1]
        self.write(lines)
        self.assertTrue(ledger.verify(self.d))

    def test_a_rehashed_forgery_still_breaks_the_chain(self):
        self.fill()
        lines = self.lines()
        e = json.loads(lines[2])
        e["text"] = "forged"
        e["sha256"] = ledger._sha(b"forged")
        e["hash"] = ledger._sha(ledger._canon(e))
        lines[2] = json.dumps(e, sort_keys=True)
        self.write(lines)
        self.assertTrue(any("entry 4" in p for p in ledger.verify(self.d)))

    def test_an_unrecorded_change_is_reported_and_refused_when_strict(self):
        self.fill()
        with open(os.path.join(self.d, "port.py"), "w") as fh:
            fh.write("v2")
        self.assertEqual(ledger.verify(self.d), [])
        self.assertEqual(ledger.verify(self.d, strict=True), ["port.py: changed since its last recorded version"])
        ledger.append(self.d, "artifact", file="port.py", now=NOW)
        self.assertEqual(ledger.verify(self.d, strict=True), [])

    def test_nothing_is_appended_to_a_record_that_does_not_verify(self):
        self.fill()
        lines = self.lines()
        lines[0] = lines[0].replace("Akkadian", "Sumerian")
        self.write(lines)
        with self.assertRaises(ValueError):
            ledger.append(self.d, "prompt", text="next", now=NOW)
        self.assertEqual(len(self.lines()), 5)

    def test_bad_input_is_refused(self):
        with self.assertRaises(ValueError):
            ledger.append(self.d, "gossip", text="x")
        with self.assertRaises(ValueError):
            ledger.append(self.d, "prompt")
        with self.assertRaises(ValueError):
            ledger.append(self.d, "artifact", file=os.path.join(os.pardir, "outside"))

    def test_the_command_line_round_trip(self):
        here = os.getcwd()
        os.chdir(self.d)
        try:
            self.assertEqual(ledger.main(["add", "prompt", "--text", "hello"]), 0)
            self.assertEqual(ledger.main(["verify", "--strict"]), 0)
            self.assertEqual(ledger.main(["status"]), 0)
        finally:
            os.chdir(here)


if __name__ == "__main__":
    unittest.main()
