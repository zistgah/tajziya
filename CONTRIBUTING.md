# Contributing to tajziya

© 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.

Work arrives as packets. Each one names its inputs, the files it must produce, its licence rule
and the one command that decides whether it is done. A pull request is judged by that command
and by the gate, `bash ops/verify.sh`, in `.github/workflows/packets.yml`.

## Taking a work packet

1. Pick an open packet on the landing page, or with `python3 -m tajziya packet list`.
2. Follow its claim link: it opens an issue saying you have it. Set its `status` to `claimed`
   in `packets/<ID>.json` in your pull request.
3. Do the work in a fork, inside the paths the packet lists as outputs.
4. Run `python3 -m tajziya packet check <ID>` until it passes, then `bash ops/verify.sh`.
5. Set the packet's `status` to `done` and open the pull request. The workflow runs the same two
   commands; when they pass, the pull request is merged.

## The rules every packet keeps

- Never type text from memory: every line comes from a file you retrieved and pinned.
- Never alter an attested form, and never put your own analysis in a field meant for a source's.
- `registry/licences.json` decides every licence; restricted material stays local, pinned.
- Every authored file carries `© 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.`
- `CORPUS.md` carries the full rules for corpus packets.
