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

## Additional notebook prerequisites

The pipeline provisions the shared knowledge base, not every optional
workshop service. Lab 7 also requires a workspace-backed Application Insights
resource and a Foundry project connection with category `AppInsights` and
authentication type `ApiKey`. Its credential must contain the Application
Insights connection string. An environment variable alone does not satisfy
the notebook's `project.telemetry.get_application_insights_connection_string()`
lookup. Keep that value out of source control and notebook outputs.

Lab 5 creates its own temporary account-level RAI policy and requires
permission to manage that policy. Do not assume a new deployment's default
policy includes the same controls as another environment.

Lab 11's cloud red-team path is opt-in and requires a supported Foundry
region and a reviewed, enabled risk taxonomy. Review the generated taxonomy
before enabling the cloud run; the local tests do not replace that step.

## Licensing

The three source PDFs are WHO publications under **CC BY-NC-SA 3.0 IGO**,
which requires attribution and non-commercial use. `documents.json` carries
each document's licence and citation through blob metadata into the index and
knowledge base, so generated answers can attribute their sources. Full terms:
[`labs/data/who_guidelines/NOTICE.md`](../../labs/data/who_guidelines/NOTICE.md).

