#!/usr/bin/env bash
# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
# The gate for tajziya. Each check reports PASS, FAIL or UNJUDGED; exit 1 on any FAIL.
#   bash ops/verify.sh [--json]
# UNJUDGED means a tool or checkout the check needs is absent. It is reported, never counted as
# a pass. `make deps` fetches the two checkouts (.deps/dhancha, .deps/panini) that V13 and V14 use.
set -uo pipefail
cd "$(dirname "$(dirname "$(readlink -f "$0")")")" || exit 1
export PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src
JSON=0; [ "${1:-}" = "--json" ] && JSON=1
FAILS=0; UNJ=0; ROWS=()

chk() {
  local id="$1" desc="$2"; shift 2
  local out rc; out="$("$@" 2>&1)"; rc=$?
  if [ "$rc" -eq 0 ]; then ROWS+=("PASS|$id|$desc")
  elif [ "$rc" -eq 3 ]; then ROWS+=("UNJUDGED|$id|$desc: $(printf '%s' "$out" | tail -1 | tr '|' '/')"); UNJ=$((UNJ + 1))
  else ROWS+=("FAIL|$id|$desc"); FAILS=$((FAILS + 1))
    [ "$JSON" = 1 ] || printf '%s\n' "$out" | tail -12 | sed "s/^/      [$id] /" >&2
  fi
}

# Everything that is, or would be, committed. Outside git: the tree, less local-only folders.
files() {
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then git ls-files --cached --others --exclude-standard
  else find . -type f -not -path './.git/*' -not -path './.deps/*' -not -path './tests/.scratch/*' | sed 's|^\./||'
  fi
}
authored() { files | grep -v -e '^LICENSES/' -e '^ops/verify.sh$'; }

v01() { local bad; bad=$(files | grep -E '\.(py|sh|js|mjs)$' | while read -r f; do grep -q "Abhishek Choudhary" "$f" || echo "$f"; done)
  [ -z "$bad" ] || { echo "no copyright line: $bad"; return 1; }; }
v02() { local pat="Independent""[ ]Researcher" hit; hit=$(authored | xargs -d '\n' grep -Il "$pat" 2>/dev/null)
  [ -z "$hit" ] || { echo "affiliation claimed other than AyeAI in: $hit"; return 1; }; }
v03() { python3 -m unittest discover -s tests -q; }
v04() { python3 tests/parity.py; }
v05() { python3 -m unittest discover -s tests -p test_harness.py -q; }
v06() { python3 -m tajziya doctor; }
v07() { python3 -m tajziya conformance; }
v08() { local pin hit; pin=$(python3 -c 'import json;print(json.load(open("vendor/sanskrit_parser/data/SOURCE.json"))["sha256"])')
  hit=$(files | while read -r f; do [ -f "$f" ] && [ "$(sha256sum "$f" | cut -c1-64)" = "$pin" ] && echo "$f"; done)
  [ -z "$hit" ] || { echo "the withheld compilation would be committed: $hit"; return 1; }; }
v09() { local hit; hit=$(files | grep -E '(^|/)__pycache__/|\.pyc$|\.tar\.gz$')
  [ -z "$hit" ] || { echo "build artefacts: $hit"; return 1; }; }
v10() { local pat="/ho""me/|/tm""p/" hit; hit=$(authored | xargs -d '\n' grep -IlE "$pat" 2>/dev/null)
  [ -z "$hit" ] || { echo "an absolute home or temp path in: $hit"; return 1; }; }
v11() { python3 tools/site_gen.py --check; }
v12() { python3 - <<'PY'
import glob, re, sys
VERBS = {"CREATE", "VERIFY", "EXECUTE", "MEASURE", "FALSIFY", "INTEGRATE"}
bad = []
files = sorted(glob.glob("cyclers/*.pni"))
if not files: bad.append("no cycler")
for f in files:
    lines = open(f, encoding="utf-8").read().splitlines()
    stages, in_ask, has_into, has_ask, cur = [], False, False, False, None
    for ln in lines:
        s = ln.strip()
        if in_ask:
            if s == "END ASK": in_ask = False
            continue
        if s.startswith("STAGE "): cur, has_into, has_ask = s.split()[1], False, False; stages.append(cur)
        elif s.startswith("VERB") and s.split()[1] not in VERBS: bad.append(f"{f}: verb {s.split()[1]} outside the closed set")
        elif s.startswith("INTO"): has_into = True
        elif s == "ASK": in_ask, has_ask = True, True
        elif s == "END STAGE" and has_ask and not has_into: bad.append(f"{f}: stage {cur} asks and stores nothing")
    if in_ask: bad.append(f"{f}: an ASK block is not closed")
    if not stages or stages[0] != "CONCEPT": bad.append(f"{f}: the first stage is not CONCEPT")
for b in bad: print(b)
sys.exit(1 if bad else 0)
PY
}
v13() { [ -f .deps/panini/panini.py ] || { echo "no .deps/panini checkout; make deps fetches it"; return 3; }
  local f; for f in cyclers/*.pni; do python3 .deps/panini/panini.py check "$f" || return 1; done; }
v14() { [ -d .deps/dhancha/tools ] || { echo "no .deps/dhancha checkout; make deps fetches it"; return 3; }
  python3 .deps/dhancha/tools/spine_validate.py descriptor.json --repo . || return 1
  local others; others=$(ls .deps/dhancha/descriptors/*.json | grep -v '/_template.json$')
  # shellcheck disable=SC2086
  python3 .deps/dhancha/tools/spine_leak.py descriptor.json $others; }
v15() { local pat="we c""laim|the inv""ention|inventive s""tep|novel meth""od for|apparatus c""omprising" hit
  hit=$(authored | xargs -d '\n' grep -IilE "$pat" 2>/dev/null)
  [ -z "$hit" ] || { echo "the language of an unfiled claim in: $hit"; return 1; }; }
v16() { local pat='10\.5281/zen''odo\.([^0-9]|$)|DOI-PEN''DING|ZENODO-D''OI' hit
  hit=$(authored | xargs -d '\n' grep -IlE "$pat" 2>/dev/null)
  [ -z "$hit" ] || { echo "a placeholder DOI in: $hit"; return 1; }; }
v18() { local pat='\$HO''ME|~''/|/t''mp|\.\.''/' hit
  hit=$(authored | grep -v -e '^vendor/' -e '^docs/vendor/' | grep -E '\.(sh|py|mjs|js)$' | xargs -d '\n' grep -lE "$pat" 2>/dev/null)
  [ -z "$hit" ] || { echo "a script that reaches outside its folder: $hit"; return 1; }; }
v17() { python3 - <<'PY'
import hashlib, json, os, sys
def h(p):
    with open(p, "rb") as fh: return hashlib.sha256(fh.read()).hexdigest()
bad = []
up = json.load(open("vendor/sanskrit_parser/UPSTREAM.json", encoding="utf-8"))
for f in up["files"]:
    p = os.path.join("vendor/sanskrit_parser", f["file"])
    if not os.path.exists(p) or h(p) != f["vendored_sha256"]: bad.append(f"vendored {f['file']} drifted from its pin")
pin = json.load(open("descriptor.json", encoding="utf-8"))["vendors_verbatim"][0]
if h(pin["path"]) != pin["sha256"]: bad.append(f"{pin['path']} drifted from its pin")
spine = ".deps/dhancha/core/unknown.py"
if os.path.exists(spine) and h(spine) != h(pin["path"]): print(f"note: the spine's current core/unknown.py differs from the vendored copy")
for b in bad: print(b)
sys.exit(1 if bad else 0)
PY
}

chk V01 "every source file carries the copyright line"            v01
chk V02 "no affiliation other than AyeAI is claimed"              v02
chk V03 "the test suite passes"                                    v03
chk V04 "the Python and JavaScript parsers agree (T9)"            v04
chk V05 "the harness catches a lying port (T2)"                   v05
chk V06 "the registry is consistent (T1, T10)"                    v06
chk V07 "every node conforms: refusals name packages (T2, T3)"    v07
chk V08 "the withheld compilation is not in the tree (T5)"        v08
chk V09 "no build artefacts"                                       v09
chk V10 "no absolute home or temp paths"                           v10
chk V11 "the site is generated from the registry, not stale"       v11
chk V12 "cyclers open with CONCEPT and keep the closed verb set"   v12
chk V13 "cyclers pass PANINI's own checker"                        v13
chk V14 "the spine judges the descriptor, D1 to D11 and D9 leak"   v14
chk V15 "no language of an unfiled claim"                          v15
chk V16 "no placeholder DOI"                                       v16
chk V17 "vendored files match their pins"                          v17
chk V18 "authored scripts stay inside their folder (clause 7)"       v18

if [ "$JSON" = 1 ]; then
  printf '{"element":"tajziya","failures":%d,"unjudged":%d,"checks":[' "$FAILS" "$UNJ"; sep=""
  for r in "${ROWS[@]}"; do IFS='|' read -r s i d <<<"$r"; d=${d//\\/\\\\}; d=${d//\"/\\\"}
    printf '%s{"id":"%s","state":"%s","check":"%s"}' "$sep" "$i" "$s" "$d"; sep=","; done; printf ']}\n'
else
  echo "tajziya: contract verification"
  for r in "${ROWS[@]}"; do IFS='|' read -r s i d <<<"$r"; printf '  %-8s %s  %s\n' "$s" "$i" "$d"; done
  echo "  $((${#ROWS[@]} - FAILS - UNJ)) passed, $FAILS failed, $UNJ unjudged"
fi
[ "$FAILS" -eq 0 ]
