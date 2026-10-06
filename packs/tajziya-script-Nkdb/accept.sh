#!/usr/bin/env bash
# accept.sh: the generic acceptance test for this script module, in isolation and in integration.
# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
#
#   bash accept.sh    clones zistgah/tajziya into ./.deps when absent, then judges this folder
#
# Everything happens inside this folder. Exit 0 accepted, 1 refused, 3 cannot judge.
set -euo pipefail
RUN="$(pwd -P)"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
[ "$HERE" = "$RUN" ] || { echo "accept: run this from the folder it sits in"; exit 1; }
FORGE="${ZOPS_FORGE:-https://github.com}"
mkdir -p .deps logs
if [ ! -d .deps/tajziya/.git ]; then
  git clone --quiet --depth 1 "$FORGE/zistgah/tajziya.git" .deps/tajziya \
    || { echo "accept: cannot judge, zistgah/tajziya could not be cloned from $FORGE"; exit 3; }
fi
LOG="logs/accept.$(date -u +%Y%m%dT%H%M%SZ).log"
set +e
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$RUN/.deps/tajziya/src" \
  python3 -m tajziya accept "$RUN" --integration --scratch "$RUN/.deps/integration" > "$LOG" 2>&1
rc=$?
set -e
cat "$LOG"
exit "$rc"
