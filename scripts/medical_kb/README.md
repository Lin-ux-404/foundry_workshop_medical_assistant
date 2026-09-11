# WHO medical knowledge base (`umc-dev`)

Builds a Foundry IQ knowledge base over three WHO clinical guidelines so the
day 1 grounded-answers lab can ask real medical questions and get cited answers.

Everything runs against **`umc-dev` only** and authenticates with **Microsoft Entra**
(managed identity for service-to-service, `az login` for you). No keys are stored,
read, or printed — the search service has `disableLocalAuth: true`.

## Run it

```powershell
az login
$env:SUBSCRIPTION_ID = "<your-subscription-id>"
pip install -r scripts/medical_kb/requirements.txt

python scripts/medical_kb/setup.py                  # idempotent, safe to rerun
python scripts/medical_kb/setup.py --reset-indexer  # force a full re-ingest
```

```bash
az login
export SUBSCRIPTION_ID=<your-subscription-id>
pip install -r scripts/medical_kb/requirements.txt

python scripts/medical_kb/setup.py
python scripts/medical_kb/setup.py --reset-indexer
```

Requires only Python 3.11+ and the packages in `requirements.txt` — the whole
pipeline is Python calling official Azure SDKs (`azure-search-documents`,
`azure-storage-blob`, `azure-mgmt-*`), no `az`, `curl`, `jq`, or `envsubst`.
`SUBSCRIPTION_ID` has no default and must be set; every other value falls back
to the umc-dev workshop defaults in `common.py` and can be overridden the same way.

| Script | Purpose |
| --- | --- |
| `common.py` | Shared config (env vars, no hardcoded subscription default), credential/client factories, and the `${VAR}` template renderer used in place of `envsubst`. |
| `00_assign_roles.py` | Idempotent RBAC for the search managed identity, the Foundry project managed identity, and your user, via `azure-mgmt-authorization`/`azure-mgmt-resource`/`azure-mgmt-search`. |
| `01_download_docs.py` | Downloads the three WHO PDFs into `labs/data/who_guidelines/`. |
| `02_upload_blobs.py` | Creates the container and uploads with citation metadata via `azure-storage-blob`. |
| `03_create_search_pipeline.py` | Create-or-update of all six search objects via `azure-search-documents`, then triggers and polls the indexer run (`--skip-run`, `--reset`). |
| `04_verify.py` | Ingestion, chunk-content, and retrieval checks via the SDK clients. Exits nonzero on failure. |
| `05_connect_kb_to_foundry.py` | Creates the `who-kb-mcp` project connection so agents can call the KB, via the generic ARM resource client. |
| `setup.py` | Orchestrates 00-05 in order (`--reset-indexer` to force a full re-ingest). |
| `documents.json` | The document manifest: titles, WHO page URLs, PDF URLs, topics, licence and suggested citation. |
| `kb_config.json` | Non-secret endpoints and names for the notebook to consume. |
| `search_objects/*.json` | Search-object payload templates (`${VAR}` placeholders rendered by `common.render_template`). |

## What gets created

| Kind | Name |
| --- | --- |
| Blob container in `umcdevstorage` | `who-guidelines` |
| Data source | `who-guidelines-datasource` |
| Index | `who-guidelines-index` |
| Skillset | `who-guidelines-skillset` |
| Indexer | `who-guidelines-indexer` |
| Knowledge source (`searchIndex`) | `who-guidelines-ks` |
| Knowledge base | `umc-medical-kb` |
| Foundry project connection (`RemoteTool`) | `who-kb-mcp` |

Reused, never modified: the search service, `umcdevstorage`, and the Foundry
account with its `text-embedding-3-large` and `gpt-5.6-luna` deployments.

## Design notes

- **API version `2026-08-01-preview`.** This serverless service rejects `2026-04-01`,
  and answer synthesis, `retrievalInstructions`, and `answerInstructions` are
  preview-only anyway.
- **Classic pipeline, not a managed blob knowledge source.** A managed `azureBlob`
  knowledge source generates its own index from a fixed template with no
  `sourceDataFields` or field-mapping hooks, so there is no supported way to surface
  the original WHO page URL as a citation field. Owning the index lets the blob
  metadata (`document_title`, `source_url`, `publisher`, `publication_id`, `topic`)
  flow through index projections into retrievable fields, and a `searchIndex`
  knowledge source exposes them via `sourceDataFields`.
- **Chunking**: `SplitSkill`, 2000 characters with 400 overlap → 402 chunks.
- **Vectors**: `text-embedding-3-large` at 3072 dimensions, HNSW/cosine, with an
  index-attached vectorizer so queries are vectorized server-side.
- **Semantic ranking**: `who-guidelines-semantic`, title `document_title`,
  content `chunk`, keywords `topic` + `publisher`.
- **Answer length** is controlled entirely by `answerInstructions` on the knowledge
  base. Without a hard cap the model produced ~400-word answers padded with headings,
  commentary about what the passages did or did not contain, and offers of follow-up
  help. The current instruction caps answers at 120 words, bans headings and
  meta-commentary, and forbids bullets that restate the lead sentence; answers now
  land around 35-135 words. `04_verify.py` fails if an answer exceeds 160 words, so
  this does not silently regress. Tune the cap in
  `search_objects/knowledge_base.json` and rerun `03_create_search_pipeline.py` -
  no re-ingestion is needed.

## Citations

`references[].sourceData` from `/retrieve` carries `document_title`, `source_url`,
`publisher`, `publication_id`, `topic`, `metadata_storage_name`, `chunk`, and
`chunk_id`. Answers cite chunks inline as `[ref_id:N]`, indexing into `references[]`.
- **Connecting the KB to an agent.** An agent reaches the knowledge base over MCP, not
  over the `/retrieve` REST endpoint. `05_connect_kb_to_foundry.py` creates a
  `RemoteTool` project connection targeting
  `{search}/knowledgebases/{kb}/mcp?api-version=2026-08-01-preview` with
  `authType: ProjectManagedIdentity` and `audience: https://search.azure.com/`.
  Three things reliably go wrong: `MCPTool` needs **both** `server_url` and
  `project_connection_id`; `project_connection_id` takes the connection **name**, not
  its ARM id; and an older `api-version` in the connection target fails tool
  enumeration with HTTP 406. The **project** managed identity - which is not the
  account identity - also needs `Search Index Data Reader`, otherwise the first tool
  call returns 403. `00_assign_roles.py` assigns it.
- **`retrievalReasoningEffort` must be `low` or `medium`.** `auto` is accepted by the
  direct `/retrieve` endpoint but rejected by agent retrieval with
  `InvalidAgentRetrievalRequest`.

## Source licensing

All three source documents are WHO publications released under
**CC BY-NC-SA 3.0 IGO**. The licence requires attribution, restricts use to
non-commercial purposes, and requires adaptations to carry a disclaimer.

The licence travels with the content through the pipeline: `documents.json` holds
the `license`, `license_url` and WHO suggested `citation` for each document; those
are written to blob metadata on upload, projected into the index as retrievable
fields, and exposed through the knowledge source's `sourceDataFields`, so a
generated answer can carry the attribution its source requires.

Full terms and the required adaptation disclaimer are in
[`labs/data/who_guidelines/NOTICE.md`](../../labs/data/who_guidelines/NOTICE.md).
