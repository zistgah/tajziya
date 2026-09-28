# GLOSSARY: tajziya

© 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.

## Terms of this repository

| His term | What it means here | Nearest common terms | Where they differ |
|---|---|---|---|
| Node | One language at one stage, with its scripts and corpus (for example Old Persian, or Classical Sanskrit). | language variety, languoid, ISO 639-3 code plus period | A stage of a language can be its own node; the matrix decides. |
| Lineage | The genealogical family a node belongs to. | language family | |
| Layers L0 to L4 | L0 phonology; L1 script pivot; L2 orthography; L3s segmentation; L3m morphology; L4 syntax, following Project ILM. | NLP pipeline: phonology, transliteration, normalisation and tokenisation, word segmentation, morphological analysis, dependency parsing | Script and language are separate axes throughout. |
| Engine | A mechanism shared by phenomenon across lineages: a logogram engine, a syllabary engine, an affix chain. | shared analyser, finite-state component | Script mechanisms recur across unrelated lineages; language mechanisms follow descent. |
| Port, frame, module | A port parses one node; a frame covers a family and refuses what it cannot do; a module is a port packaged with its manifest, sources and examples. | adapter, fallback, plugin | |
| Refusal | A layer that is not built says so and names the engines and packages that would build it. | explicit not-implemented error with a pointer | Never a silent empty result. |
| Package | A hand-over kit for one node: brief, contract, skeleton, sources, quest, record and acceptance. | work package, starter kit, good first issue | |
| Acceptance A1 to A7 | Manifest, tree, licences, references, isolation, integration, quest and record. | conformance suite, unit and integration tests | A7 is the author's step 3 made checkable. |
| Elimination rule | U_i = K_i − Recover(K_not_i, R, X): what is lost if node i is taken away. | ablation, leave-one-out analysis | Translation counts as lossy, never as recovery. |
| Status I, P, U, S, C | Irreducible, provisional, undeciphered or unknown, stage, candidate for compression. | | Held as the matrix states it; conflicts are recorded, not ruled. |
| CoNLL-U | The common output. | Universal Dependencies format | |

## The estate's terms, and the nearest terms in common use

These are the author's terms. They are kept, not replaced: the right-hand columns exist so that
a reader, or another AI, who knows the market vocabulary can find their footing. Where the two
differ, the difference is stated rather than smoothed over.

| His term | What it means here | Nearest common terms | Where they differ |
|---|---|---|---|
| Cycler | An AI-agnostic protocol for human and AI working together: intent, context, a meaningful prompt, any AI answers, the human inspects, the artifacts and responses are kept under configuration management, the next prompt follows, until a final artifact the human authored, carrying its intention. The family is named by what it produces: print (matba), video (khwab), audio (awaz), immersive (tilasm), embodied (pench), memory (yadein), research (genie). | agent loop, agentic workflow, human-in-the-loop harness, prompt chain | A cycler is never the author and never an AI provider. Every prompt must create, verify, execute, measure, falsify or integrate an artifact, and it stays useful if every commercial provider vanishes. |
| Agent, harness | His placement: the cyclers and genie are the agents and harnesses of Act I, AGI completeness. | agent, agent harness, evaluation harness | The market term usually names the software; his names the protocol the software keeps. |
| Configuration management (step 3 of every cycle) | Every prompt, response, human decision and artifact version is identified, hashed and appended; nothing is overwritten; the current state is derived from the record. | configuration management (IEEE 828, ISO 10007), provenance tracking, experiment tracking, audit log | Responses are configuration items in their own right, not chat history. |
| AAB (آب, water) | The paint program for systems: the human paints actors, components, stores, gates, interfaces and environments, wires the flows, and the painting is the manifest every prompt carries. Quests are the eight VGC stages; a node glows verified only with a recorded oracle. Process cyclers, such as building one language layer, run here. | low-code system designer, spec-driven development, model-based systems engineering canvas | Gamification never outruns grounding: no oracle, no glow. |
| VGC | Verification-Gated Human-AI Co-Development: nothing is accepted without an oracle. | eval-gated development, CI gating, test-driven development with AI | Acceptance belongs to an oracle, never to the human or the AI. |
| Oracle | The check that decides acceptance: a test suite, a second implementation, a measurement or a review. | test oracle, acceptance test, conformance suite | |
| Quest | One VGC stage, completed only with typed evidence. | stage gate, milestone with acceptance criteria | |
| PANINI | His language for prompt cycles and his construct compiler: common semantics plus decorators, with many front ends and realization backends. | domain-specific language, orchestration language, compiler toolchain | The construct is primary; syntaxes are views of it. |
| Front end, middleware, realization backend | His layering of 27 Sep 2026: ILM and the language parsers (tajziya) are the front end; PANINI's own front ends and its fine-tuned language are the middleware; the realization backends are where programs meet a substrate, Panini Q among them. | compiler front end, intermediate representation and passes, compiler back end or target | |
| ILM | Integrative Linguistic Multiscript: one language core for all languages, with script, language and standard kept apart. | multilingual NLP, script-agnostic text processing, transliteration, Unicode normalisation | Script, language and standard are separate axes, never conflated. |
| CEM (CEMᵇ, CEMˢ, Eco-CEM) | Cognitive enablement modules, in bioform, synthetiform and ecological families; his Act II, with the accelerators. | AI accelerators, neuromorphic hardware, cognitive architectures, brain-computer interfaces | |
| The three Acts | His note "3 Act ASI ∧ Panini": Act I, AGI complete; Act II, post-AGI to ASI; Act III, post-ASI. PANINI runs through all three. | AGI, superintelligence (ASI) roadmaps | Placement says when a piece matters most, not when work on it starts. |
| Candor, Tok DOI, Misty DOI | Signed intent receipts; atomic timestamps; DOI minting, in the order seal, clear, attest, mint. | in-toto and SLSA attestations, OpenTimestamps, Zenodo DOI deposit | |
| Reference lab | His laboratory pattern for doing most of the research behind high-end AI, robotics and automation papers at modest cost, alongside the courses built on it. | AI research lab, robotics and automation lab | Public name pending his choice. |
