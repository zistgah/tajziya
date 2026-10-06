# CONTRACT: the script-Sgnw module

This overlay adds to zistgah/tajziya's CONTRACT.md and to the master contract at
zistgah/governance, and relaxes neither.

© 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.

**S1. A layer that is not built refuses by name** through `api.refuse`, which names the
packages the registry derives for this script. It never returns a plausible answer.

**S2. A built layer declares what it leaves out** in `scope_excludes`, and cites attested
examples from listed sources.

**S3. No table is written from memory.** Character ranges, normalisation and grapheme rules come
from the Unicode Character Database; a pivot table comes from Romenagri where one exists.

**S4. One transliterator.** A pivot goes through Romenagri's tables, never through a second
transliterator written here.

**S5. A pivot is proven by round trip.** Text to the hub and back is identical on the reference
examples, and every loss the script forces is listed in `scope_excludes`.

**S6. Licences.** Only allowed licences enter the folder; restricted material stays in
`data/local/`, pinned by SHA-256 and ignored by git.

**S7. The module stays inside its folder** (master clause 7) and imports `tajziya.api` and
nothing else from tajziya.

Enforced by the generic acceptance test: `bash accept.sh`.
