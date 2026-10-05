# Work packets

© 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.

One JSON per packet, schema `tajziya.packet/1`: id, title, area, wave, size, status (open,
claimed, in-review, done), summary, inputs, outputs, licence, acceptance (kind, args, command),
depends, how. `tools/packets_gen.py` writes new packets and never rewrites one that exists. The
acceptance kinds are defined in `src/tajziya/packets.py`.
