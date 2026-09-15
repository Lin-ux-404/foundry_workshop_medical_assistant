# Workshop environment setup

Stands up the Azure environment the workshop labs run against (resource
group, storage, Azure AI Search, Foundry account/project, model deployments)
and builds a Foundry IQ knowledge base from three WHO clinical guideline PDFs
for the Day 1 grounded-answers lab. Every script is plain Python, safe to
rerun, and authenticates with Microsoft Entra (`az login`) — no keys are
stored, read, or printed.

## Run it

```bash
az login
pip install -r scripts/setup/requirements.txt

python scripts/setup/run.py --resource-group <your-resource-group>
```

`run.py` runs the numbered scripts (`00_provision_infra.py` ... `06_verify.py`)
in order; run any of them directly to redo just that step.

## Arguments and overrides

| Flag | Default | What it does |
|---|---|---|
| `--resource-group` | `umc-dev` | Resource group to provision into. |
| `--subscription-id` | current `az account show` subscription | Subscription to use; `SUBSCRIPTION_ID` env var also works. |
| `--reset-indexer` | off | Force a full re-ingest of the PDFs. |
| `--skip-provision` | off | Skip `00_provision_infra.py`, e.g. when storage/search/Foundry already exist. |

Object names, regions, SKUs, and models default to the umc-dev workshop setup
and can be overridden via environment variable — see `common.py`. Storage,
search, and Foundry account names must be globally unique across Azure, so
any resource group other than `umc-dev` gets a deterministic name suffix to
avoid collisions; override `STORAGE_ACCOUNT`, `SEARCH_SERVICE`, or
`FOUNDRY_ACCOUNT` directly if you still hit one. Running
`00_provision_infra.py` needs Owner or Contributor on the target subscription
(or resource group); every other script only needs the roles
`01_assign_roles.py` grants.

Region availability is service-specific: a region with available model quota
may not support the configured Search SKU or have capacity for a new Search
service. Set `FOUNDRY_LOCATION` and `DATA_LOCATION` independently before the
first run when needed. Do not change `DATA_LOCATION` to move an already
created storage account; use a new account name instead.

## Licensing

The three source PDFs are WHO publications under **CC BY-NC-SA 3.0 IGO**,
which requires attribution and non-commercial use. `documents.json` carries
each document's licence and citation through blob metadata into the index and
knowledge base, so generated answers can attribute their sources. Full terms:
[`labs/data/who_guidelines/NOTICE.md`](../../labs/data/who_guidelines/NOTICE.md).

