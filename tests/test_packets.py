# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""Work packets: well formed, and their acceptance checks pass what they should and refuse what they should."""
import json
import os
import shutil
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from tajziya import packets, romenagri  # noqa: E402


class Registry(unittest.TestCase):
    def test_every_packet_is_well_formed_with_a_command(self):
        ps = packets.all_packets()
        self.assertGreater(len(ps), 140)
        for pid, p in ps.items():
            self.assertEqual(packets.problems(p), [], pid)
            self.assertEqual(p["acceptance"]["command"], f"python3 -m tajziya packet check {pid}")

    def test_every_area_has_open_work(self):
        areas = {p["area"] for p in packets.all_packets().values() if p["status"] == "open"}
        self.assertEqual(areas, set(packets.AREAS))


class Checks(unittest.TestCase):
    def test_a_pinned_licensed_sutra_table_passes(self):
        state, probs = packets.v_sutra_table({"path": "modules/cls/data/ashtadhyayi/sutraani.tsv",
                                             "columns": ["id", "sutra"], "min_rows": 3983, "source_id": "ashtadhyayi-com-data"})
        self.assertEqual((state, probs), ("PASS", []))

    def test_a_table_short_of_its_count_or_unpinned_fails(self):
        state, probs = packets.v_sutra_table({"path": "modules/cls/data/ashtadhyayi/sutraani.tsv",
                                             "columns": ["id", "sutra"], "min_rows": 4000, "source_id": "vidyut-sutrapatha"})
        self.assertEqual(state, "FAIL")
        self.assertTrue(any("at least 4000" in p for p in probs))
        self.assertTrue(any("does not pin" in p for p in probs))

    def test_a_missing_output_fails(self):
        self.assertEqual(packets.check("PKT-TRN-01")[0], "FAIL")

    def test_a_corpus_without_its_count_fails_and_with_it_passes(self):
        d = os.path.join(ROOT, "corpus", "zz-test")
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d)
        try:
            json.dump({"sources": [{"id": "s1", "url": "https://example.org", "retrieved": "2026-10-05",
                                    "licence": "CC0-1.0", "files": []}]}, open(os.path.join(d, "SOURCES.json"), "w"))
            open(os.path.join(d, "units.jsonl"), "w").write(json.dumps(
                {"id": "u1", "node": "zz-test", "source": "s1", "locator": "1", "text": "अग्निमीळे"}, ensure_ascii=False) + "\n")
            open(os.path.join(d, "README.md"), "w").write("units: 2\n")
            self.assertEqual(packets.v_corpus({"node": "zz-test"})[0], "FAIL")
            open(os.path.join(d, "README.md"), "w").write("units: 1\n")
            self.assertEqual(packets.v_corpus({"node": "zz-test"}), ("PASS", []))
        finally:
            shutil.rmtree(d, ignore_errors=True)


@unittest.skipUnless(romenagri.build() is None, "Romenagri cannot be built here (gcc, flex, make, iconv)")
class Romenagri(unittest.TestCase):
    def test_roman_and_back_with_the_authors_pipeline(self):
        self.assertEqual(romenagri.roman("वृद्धिरादैच्"), "w_ri_d_dhiraa_daich")
        self.assertEqual(romenagri.devanagari("w_ri_d_dhiraa_daich"), "वृद्धिरादैच्")

    def test_the_committed_forms_are_what_the_pin_gives(self):
        sys.path.insert(0, os.path.join(ROOT, "tools"))
        import romenagri_sutras
        self.assertEqual(romenagri_sutras.main(["--check"]), 0)
