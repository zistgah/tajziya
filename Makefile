# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
PY ?= python3

check:
	@bash ops/verify.sh

site:
	@PYTHONDONTWRITEBYTECODE=1 $(PY) tools/site_gen.py

deps:
	@mkdir -p .deps
	@[ -d .deps/dhancha ] || git clone -q --depth 1 https://github.com/zistgah/dhancha .deps/dhancha
	@echo "deps: .deps/dhancha present; make check now judges the spine"

packs:
	@PYTHONDONTWRITEBYTECODE=1 $(PY) tools/langpack.py --remaining --tar --bundle

.PHONY: check site deps packs
