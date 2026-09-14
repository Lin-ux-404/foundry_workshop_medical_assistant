# Workshop environment setup

Stands up the Azure environment the workshop labs run against — resource
group, storage account, Azure AI Search service, Foundry account/project, and
model deployments — then builds a Foundry IQ knowledge base from three WHO
clinical guideline PDFs for the Day 1 grounded-answers lab. Every script is
plain Python calling official Azure SDKs, is safe to rerun, and authenticates
with Microsoft Entra (`az login`) — no keys are stored, read, or printed.

## Run it

```bash
az login
pip install -r scripts/setup/requirements.txt

python scripts/setup/run.py --resource-group <your-resource-group>
```

This uses whatever subscription `az account show` reports (i.e. whatever
`az login`/`az account set` last selected). Pass `--subscription-id <id>` or
set `SUBSCRIPTION_ID` if you want to target a different one.

This provisions everything from an empty subscription: the resource group,
storage account, Azure AI Search service, the Foundry account and project,
the two model deployments, then downloads the PDFs, uploads them, builds the
search pipeline and knowledge base, connects it to Foundry, and verifies it.
Add `--reset-indexer` to force a full re-ingest, or `--skip-provision` if the
storage account, search service, and Foundry project already exist and you
only want to (re)build the knowledge base on top of them.

`run.py` runs the numbered scripts (`00_provision_infra.py` ...
`06_verify.py`) in order; run any of them directly to redo just that step.
Names, endpoints, regions, SKUs, and models default to the umc-dev workshop
setup and can be overridden via env var — see `common.py`. The identity
running `00_provision_infra.py` needs Owner or Contributor on the target
subscription (or the resource group, if it already exists); every other
script only needs the roles `01_assign_roles.py` grants.

## Licensing

The three source PDFs are WHO publications under **CC BY-NC-SA 3.0 IGO**,
which requires attribution and non-commercial use. `documents.json` carries
each document's licence and citation through blob metadata into the index and
knowledge base, so generated answers can attribute their sources. Full terms:
[`labs/data/who_guidelines/NOTICE.md`](../../labs/data/who_guidelines/NOTICE.md).
