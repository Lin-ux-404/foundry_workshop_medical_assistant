# Workshop environment setup

Stands up the Azure environment the workshop labs run against (resource
group, storage, Azure AI Search, Foundry account/project, model deployments,
Log Analytics and Application Insights)
and builds a Foundry IQ knowledge base from three WHO clinical guideline PDFs
for the Day 1 grounded-answers lab. Every script is plain Python, safe to
rerun, and authenticates to Azure with Microsoft Entra (`az login`).
Telemetry setup reads the Application Insights connection string into memory
and stores it as a credential in a Foundry project connection. It is never
written to local files or printed.

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
| `--skip-provision` | off | Skip all infrastructure provisioning, including telemetry and its project connection. These must already exist. |

Object names, regions, SKUs, and models default to the umc-dev workshop setup
and can be overridden via environment variable — see `common.py`. Storage,
search, and Foundry account names must be globally unique across Azure, so
any resource group other than `umc-dev` gets a deterministic name suffix to
avoid collisions; override `STORAGE_ACCOUNT`, `SEARCH_SERVICE`, or
`FOUNDRY_ACCOUNT` directly if you still hit one. Running
`00_provision_infra.py` and `telemetry.py` need Owner or Contributor on the
target resource group (subscription scope is needed to create a new group).
Running `01_assign_roles.py` also requires permission to assign roles, such
as Owner or Role Based Access Control Administrator; Contributor alone cannot
grant roles. Keep management access for creating project connections and
reading telemetry resources; the data-plane roles granted by
`01_assign_roles.py` do not replace it.

Region availability is service-specific: a region with available model quota
may not support the configured Search SKU or have capacity for a new Search
service. Set `FOUNDRY_LOCATION` and `DATA_LOCATION` independently before the
first run when needed. Do not change `DATA_LOCATION` to move an already
created storage account; use a new account name instead.

## Telemetry for Lab 7

The provisioning step creates a Log Analytics workspace (`PerGB2018`, 30-day
workspace retention), workspace-backed Application Insights, and a Foundry
project connection with category `AppInsights` and authentication type
`ApiKey`. This connection enables Lab 7's
`project.telemetry.get_application_insights_connection_string()` lookup.
The final verification step checks the resource links; it does not send a
trace or prove telemetry delivery.

| Environment variable | Default | Purpose |
| --- | --- | --- |
| `TELEMETRY_LOCATION` | `FOUNDRY_LOCATION` (normally `swedencentral`) | Region for both telemetry resources. |
| `LOG_ANALYTICS_WORKSPACE` | `umc-workshop-logs` plus the resource-group suffix | Workspace name. |
| `APPLICATION_INSIGHTS` | `umc-workshop-insights` plus the resource-group suffix | Application Insights resource name. |
| `APP_INSIGHTS_CONNECTION_NAME` | `workshop-appinsights` | Connection name within the Foundry project. |

To add telemetry to an existing workshop without reprovisioning models,
Search or storage, reuse its subscription, resource group and Foundry settings:

```bash
export SUBSCRIPTION_ID="<subscription-id>"
export RESOURCE_GROUP="<existing-resource-group>"
export FOUNDRY_ACCOUNT="<existing-foundry-account>"
export FOUNDRY_PROJECT="<existing-foundry-project>"
export TELEMETRY_LOCATION="<region>"
python scripts/setup/telemetry.py
```

When telemetry already exists, set the resource and connection name overrides
to reuse it instead of creating a second set. Use the existing resource region;
changing the location setting does not move resources. Rerunning applies the
configured workspace retention and links.

Application Insights uses connection-string ingestion with local authentication
enabled to match Lab 7's exporter. Setup does not disable or configure
service-side content recording. Use synthetic workshop data, review tracing
privacy settings before sending other data, and account for telemetry ingestion
and retention charges. Keep connection strings out of source control and
notebook outputs.

## Additional notebook prerequisites

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
