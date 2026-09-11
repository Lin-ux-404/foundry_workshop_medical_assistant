# WHO medical knowledge base

Builds a Foundry IQ knowledge base from three WHO clinical guideline PDFs for
the Day 1 grounded-answers lab. Every script is plain Python calling official
Azure SDKs, is safe to rerun, and authenticates with Microsoft Entra
(`az login`) — no keys are stored, read, or printed.

## Run it

```bash
az login
export SUBSCRIPTION_ID=<your-subscription-id>
pip install -r scripts/medical_kb/requirements.txt

python scripts/medical_kb/setup.py --resource-group <your-resource-group>
```

Add `--reset-indexer` to force a full re-ingest. `setup.py` runs the numbered
scripts (`00_assign_roles.py` ... `05_connect_kb_to_foundry.py`) in the right
order; run any of them directly to redo just that step. Names, endpoints, and
models default to the umc-dev workshop setup and can be overridden via env
var — see `common.py`.

## Licensing

The three source PDFs are WHO publications under **CC BY-NC-SA 3.0 IGO**,
which requires attribution and non-commercial use. `documents.json` carries
each document's licence and citation through blob metadata into the index and
knowledge base, so generated answers can attribute their sources. Full terms:
[`labs/data/who_guidelines/NOTICE.md`](../../labs/data/who_guidelines/NOTICE.md).
