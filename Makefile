# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
PY ?= python3

check:
	@bash ops/verify.sh

site:
	@PYTHONDONTWRITEBYTECODE=1 $(PY) tools/site_gen.py

deps:
	@mkdir -p .deps
	@[ -d .deps/dhancha ] || git clone -q --depth 1 https://github.com/zistgah/dhancha .deps/dhancha
	@[ -d .deps/panini ] || git clone -q --depth 1 https://github.com/zistgah/panini .deps/panini
	@echo "deps: .deps/dhancha and .deps/panini present; make check now judges the spine and the cyclers"

.PHONY: check site deps
