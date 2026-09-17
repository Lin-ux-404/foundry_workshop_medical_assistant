# Workshop environment setup

Creates the workshop's storage, Search, Foundry project, model deployments,
and telemetry. It also builds a Foundry IQ knowledge base from three WHO PDFs.

## Run it

You need permission to create resources and assign roles, such as Owner.
Creating a new resource group requires subscription-level access.

```bash
az login
pip install -r scripts/setup/requirements.txt

python scripts/setup/run.py --resource-group <your-resource-group>
```

The numbered scripts run in order and can be rerun.

## Arguments and overrides

| Flag | Default | What it does |
|---|---|---|
| `--resource-group` | `umc-dev` | Resource group to provision into. |
| `--subscription-id` | current `az account show` subscription | Subscription to use; `SUBSCRIPTION_ID` env var also works. |
| `--reset-indexer` | off | Force a full re-ingest of the PDFs. |
| `--skip-provision` | off | Use existing infrastructure, including connected telemetry. |

Set environment variables to override the defaults in [`common.py`](common.py).
`FOUNDRY_LOCATION` controls Foundry and telemetry; `DATA_LOCATION` controls
Search and storage. Availability varies by service. Choose regions before
provisioning; changing a setting does not move existing resources.

Names get a resource-group suffix outside `umc-dev` to reduce collisions.
Use the name overrides in `common.py` to reuse existing resources.

## Telemetry for Lab 11

Setup creates Log Analytics (30-day workspace retention), Application Insights,
and the Foundry connection needed by Lab 11. To reuse existing telemetry, set
`LOG_ANALYTICS_WORKSPACE`, `APPLICATION_INSIGHTS`, and `APP_INSIGHTS_CONNECTION_NAME`.

The connection string is stored in Foundry, never in local files or logs.
Local authentication stays enabled for the lab's exporter. Use synthetic data:
setup does not disable service-side content recording. Telemetry charges apply.

## Additional notebook prerequisites

Lab 10 needs permission to manage guardrail policies. The Extras red-team
run is opt-in and needs a supported region and a reviewed, enabled risk taxonomy.

## Licensing

The WHO PDFs use **CC BY-NC-SA 3.0 IGO** (attribution, non-commercial use,
and share-alike). See the [source notice](../../labs/data/who_guidelines/NOTICE.md).
