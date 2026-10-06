# The quest for Seru (szd)

© 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.

`aab-painting.json` beside this file is the package as an AAB painting: import it at
https://zistgah.org/aab/. AAB's eight quests are the VGC stages; here is what each means for
this package.

| AAB quest | In this package | Oracle |
|---|---|---|
| 0 Requirements | Pick one layer and one batch; say what will be true when it is done. | the batch is written down in the record |
| 1 Architecture | The painting: layers, stores, gates. Change it where your plan differs. | A1, A2 |
| 2 Reference build | Choose an openly licensed source, extract the data by script, implement. | A3 |
| 3 Forge the gate | Attested examples from the source, not from the code, every reading. | A4 |
| 4 Verify loop | `bash accept.sh` until it passes; repair by exact anchor. | A5, A6 |
| 5 Reconcile | Compare the layer states you declare with what the code does. | A1, A5 |
| 6 Package & licence | Every data file listed with its licence; restricted material local only. | A3 |
| 7 DOI · OTS · patent trail | Not per package: hand the package back, and the maintainers take it into tajziya's own record. | intake under a typed gate |

Between every prompt and the next, keep the record: `python3 ledger.py add ...` for the intent,
the context, each prompt, each response (naming the AI you used), each decision and each artifact
version. Check A7 holds the record to its chain.
