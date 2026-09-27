# For any agent or person taking work here

© 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.

1. Read CONTRACT.md, then CONTEXT.md.
2. Run `make check`. If it is red before you start, that is the first thing to report.
3. Take one package from `roadmap/packages.json`. Packages with no dependencies can start now.
   Labels are capabilities (needs:code, needs:proof, needs:legal, needs:human, needs:testing),
   never a model name.
4. Work it through `cyclers/tajziya.pni`, or `cyclers/node.pni` for one batch on one node.
5. A package is done when its acceptance command passes and `bash ops/verify.sh` is green.
   Paste both outputs. A step you did not run is reported as not run.

Name nodes by registry id. Return every reading. Source every rule. Leave an unbuilt layer
refusing.

To build a language: `PYTHONPATH=src python3 tools/langpack.py <node or ISO code>` writes its
package under `packs/`. Work inside the package, run its `bash accept.sh`, and hand the folder back. It
becomes `modules/<node>` and is bound once `python3 -m tajziya accept modules/<node> --integration` passes.
