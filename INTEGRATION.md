# Attachment points

Five, closed. The fifth, MODULE, was added on the author's instruction of 26 Sep 2026 that the architecture carry
language modules. Anything that needs a sixth is a contract question, raised as one.

© 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.

**SCRIPT**: the Romenagri script tables (project-ilm/romenagri, `tables/<script>_to_deva.tsv`),
read as files. `registry/scripts.json` names the table for each Brahmic script that has one. This
is where the L1 pivot will attach; nothing here reimplements transliteration.

**CORPUS**: a text or CoNLL-U file supplied by the operator. Corpora are read, never bundled, and a
corpus whose terms forbid redistribution stays on the operator's machine.

**LEXICON**: a lexicon resource file whose licence is recorded beside it. The Sanskrit node's
placeholder lexicon is the only one bundled.

**DOOR**: the verbs of `skills/verbs.json`, served by darwaza to any model on the operator's own
machine. None is gated.

**MODULE**: a language module under `modules/<node>/`: `module.json`, a port importing only `tajziya.api`,
`data/SOURCES.json` with every licence, and `reference/examples.json` with attested examples. It is bound in
`registry/bindings.json` only after `python3 -m tajziya accept modules/<node> --integration` passes.
