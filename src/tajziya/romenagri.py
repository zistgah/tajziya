# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""Romenagri, as functions: the author's transliteration system, retrieved, built and run as he runs it.

    roman("वृद्धिरादैच्")          -> "w_ri_d_dhiraa_daich"
    devanagari("w_ri_d_dhiraa_daich") -> "वृद्धिरादैच्"

Nothing here transliterates. vendor/romenagri is the Romenagri folder of hindawiai/chintamani,
byte for byte, pinned in its UPSTREAM.json; build() compiles it with its own Makefile into
.deps/romenagri, and the functions pipe text through the programs exactly as its mass_hindawi
script does: UTF-8 to UTF-16, uni2acii, acii2rmn; and back through rmn2acii, acii2uni, UTF-16 to
UTF-8. Building needs gcc, flex and its library, and iconv.
"""
import os
import shutil
import subprocess

from .registry import path

VENDOR = path("vendor", "romenagri")
BUILD = path(".deps", "romenagri")
PROGRAMS = ("uni2acii", "acii2rmn", "rmn2acii", "acii2uni")


def available():
    return all(os.access(os.path.join(BUILD, p), os.X_OK) for p in PROGRAMS) and shutil.which("iconv") is not None


def missing_tools():
    return [t for t in ("gcc", "flex", "make", "iconv") if shutil.which(t) is None]


def build(force=False):
    """Compile the vendored tree with its own Makefile. Returns None, or why it cannot."""
    if available() and not force:
        return None
    if missing_tools():
        return "needs " + ", ".join(missing_tools())
    if os.path.exists(BUILD):
        shutil.rmtree(BUILD)
    shutil.copytree(VENDOR, BUILD)
    r = subprocess.run(["make", "all"], cwd=BUILD, capture_output=True, text=True)
    if r.returncode != 0 or not available():
        return "make all failed: " + " | ".join((r.stdout + r.stderr).strip().splitlines()[-3:])
    return None


def _pipe(cmd, data):
    if not available():
        raise RuntimeError("Romenagri is not built here; call romenagri.build() (needs gcc, flex, make, iconv)")
    r = subprocess.run(cmd, input=data, capture_output=True, shell=True, cwd=BUILD)
    return r.stdout


def roman_lines(lines):
    """Devanagari lines to Romenagri, one output line per input line."""
    out = _pipe("iconv -futf8 -tutf16 | ./uni2acii | ./acii2rmn", ("\n".join(lines) + "\n").encode("utf-8"))
    return out.decode("utf-8", "replace").replace("\r", "").split("\n")[:len(lines)]


def devanagari_lines(lines):
    """Romenagri lines back to Devanagari."""
    out = _pipe("./rmn2acii | ./acii2uni | iconv -futf16 -tutf8", ("\n".join(lines) + "\n").encode("ascii", "replace"))
    return out.decode("utf-8", "replace").replace("\r", "").lstrip("\ufeff").split("\n")[:len(lines)]


def acii_lines(lines):
    """Devanagari lines to the ACII pivot, as bytes, one item per line."""
    out = _pipe("iconv -futf8 -tutf16 | ./uni2acii", ("\n".join(lines) + "\n").encode("utf-8"))
    return out.replace(b"\r", b"").split(b"\n")[:len(lines)]


def roman(text):
    return roman_lines([text])[0]


def devanagari(text):
    return devanagari_lines([text])[0]
