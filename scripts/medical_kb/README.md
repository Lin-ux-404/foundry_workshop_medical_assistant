# WHO medical knowledge base (`umc-dev`)

Builds a Foundry IQ knowledge base over three WHO clinical guidelines so the
day 1 grounded-answers lab can ask real medical questions and get cited answers.

Everything runs against **`umc-dev` only** and authenticates with **Microsoft Entra**
(managed identity for service-to-service, `az login` for you). No keys are stored,
read, or printed — the search service has `disableLocalAuth: true`.

## Run it

```bash
az login
./scripts/medical_kb/setup.sh          # idempotent, safe to rerun
RESET_INDEXER=1 ./scripts/medical_kb/setup.sh   # force a full re-ingest
```

Requires `az`, `curl`, `jq`, `envsubst`, and a Python with `requests` +
`azure-identity` (the repo `.venv` has them).

| Script | Purpose |
| --- | --- |
| `config.sh` | Names, endpoints, and REST helpers. Every value is overridable by env var. |
| `00_assign_roles.sh` | Idempotent RBAC for the search managed identity and your user. |
| `01_download_docs.sh` | Downloads the three WHO PDFs into `labs/data/who_guidelines/`. |
| `02_upload_blobs.sh` | Creates the container and uploads with citation metadata (`--auth-mode login`). |
| `03_create_search_pipeline.sh` | Create-or-update of all six search objects. |
| `04_verify.py` | Ingestion, chunk-content, and retrieval checks. Exits nonzero on failure. |
| `05_connect_kb_to_foundry.sh` | Creates the `who-kb-mcp` project connection so agents can call the KB. |
| `documents.json` | The document manifest: titles, WHO page URLs, PDF URLs, topics. |
| `kb_config.json` | Non-secret endpoints and names for the notebook to consume. |
| `search_objects/*.json` | REST payload templates (`${VAR}` placeholders rendered by `envsubst`). |

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
  `search_objects/knowledge_base.json` and rerun `03_create_search_pipeline.sh` -
  no re-ingestion is needed.

## Citations

`references[].sourceData` from `/retrieve` carries `document_title`, `source_url`,
`publisher`, `publication_id`, `topic`, `metadata_storage_name`, `chunk`, and
`chunk_id`. Answers cite chunks inline as `[ref_id:N]`, indexing into `references[]`.
- **Connecting the KB to an agent.** An agent reaches the knowledge base over MCP, not
  over the `/retrieve` REST endpoint. `05_connect_kb_to_foundry.sh` creates a
  `RemoteTool` project connection targeting
  `{search}/knowledgebases/{kb}/mcp?api-version=2026-08-01-preview` with
  `authType: ProjectManagedIdentity` and `audience: https://search.azure.com/`.
  Three things reliably go wrong: `MCPTool` needs **both** `server_url` and
  `project_connection_id`; `project_connection_id` takes the connection **name**, not
  its ARM id; and an older `api-version` in the connection target fails tool
  enumeration with HTTP 406. The **project** managed identity - which is not the
  account identity - also needs `Search Index Data Reader`, otherwise the first tool
  call returns 403. `00_assign_roles.sh` assigns it.
- **`retrievalReasoningEffort` must be `low` or `medium`.** `auto` is accepted by the
  direct `/retrieve` endpoint but rejected by agent retrieval with
  `InvalidAgentRetrievalRequest`.
