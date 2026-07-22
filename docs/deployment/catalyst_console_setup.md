# Catalyst Web Console Setup (Beginner Guide)

You will set up Zoho Catalyst **in the browser**, then paste IDs into
[`.env`](../../.env.example). Code adapters live in
`backend/app/integrations/catalyst/`.

**Official console:** [https://console.catalyst.zoho.com](https://console.catalyst.zoho.com)
(Use your Zoho DC if different: `.in`, `.eu`, etc.)

**Docs:** [Create a project](https://docs.catalyst.zoho.com/en/getting-started/catalyst-projects/) ·
[QuickML RAG](https://docs.catalyst.zoho.com/en/quickml/help/generative-ai/rag/) ·
[Python SDK (third-party apps)](https://docs.catalyst.zoho.com/en/sdk/python/v1/integrate-sdk-in-third-party-apps/)

---

## Mental model

| Layer in console | What it is | Our use |
|------------------|------------|---------|
| **Cloud Scale** | Data, auth, cache, files, events | Data Store, NoSQL, Stratus, Cache, Auth, Signals, Cron, API Gateway |
| **Serverless** | Functions / AppSail | Backend deploy later |
| **QuickML** | LLM + RAG + ML pipelines | Officer Q&A (your AI focus) |
| **Zia / SmartBrowz** | OCR, AutoML, PDF | Later phases |
| **DevOps** | Pipelines | CI/CD later |

Local Postgres/Redis = **dev only**. Production paths = Catalyst services above.

---

## Part A — Create the project (15 min)

### A1. Sign in

1. Open [Catalyst console](https://console.catalyst.zoho.com).
2. Sign in with the Zoho account used for the hackathon.
3. You land on the **project index** page.

### A2. Create project

1. Click **Create New Project**.
2. Name (no spaces): `crime-intelligence-platform` (or `cip-ksp`).
3. Click **Create** → **Access Project**.

### A3. Copy Project ID + Org ID → `.env`

1. In the project, click the **Settings** (gear) icon (top-right).
2. Go to **Project Settings → General**.
3. Copy **Project ID** → `CATALYST_PROJECT_ID` in `.env`.
4. Look at the browser URL, e.g.
   `https://console.catalyst.zoho.com/baas/687259092/project/11811.../Development`
   The number after `/baas/` is **Org ID** → `CATALYST_ORG_ID`.
5. Set `CATALYST_ENV=Development` (stay in Development until demo day).

```bash
CATALYST_PROJECT_ID=paste_here
CATALYST_ORG_ID=paste_here
CATALYST_ENV=Development
```

---

## Part B — Cloud Scale (data + auth) — Full Stack A/B + you

Open the left menu → **Cloud Scale** → **Start Exploring** if prompted.

### B1. Authentication (FS B owns UI; you need it for API later)

1. Cloud Scale → **Authentication** (Security & Identity).
2. **Native Authentication** → **Set Up**.
3. Choose **Hosted Authentication** (simplest for hackathon) or Embedded.
4. Enable signup if judges need demo accounts.
5. After setup, note Client ID / related auth values →
   `CATALYST_AUTH_DOMAIN`, `CATALYST_CLIENT_ID`, `CATALYST_CLIENT_SECRET`.

Docs pattern: [ZCDrive auth tutorial](https://docs.catalyst.zoho.com/en/tutorials/zcdrive/).

### B2. Data Store (relational FIR tables — FS A)

1. Cloud Scale → **Storage** → **Data Store**.
2. **Create a Table** for masters first, e.g. `CaseStatusMaster`.
3. Add columns matching the ER PDF (start small).
4. Later: `CaseMaster` and children.

Local Alembic/Postgres can mirror this while FS A designs tables.

### B3. NoSQL (RAG documents — **you**)

1. Cloud Scale → **Storage** → **NoSQL**.
2. Create a table, e.g. `cip_rag_documents`.
3. Decide partition key: `doc_id` (string, e.g. `case:123`).
4. Paste into `.env`:

```bash
CATALYST_NOSQL_TABLE=cip_rag_documents
CATALYST_NOSQL_ENDPOINT=   # from table/API details if shown
```

Our builder already emits `doc_id` — see `docs/ai/rag_document_schema.md`.

### B4. Stratus (FIR PDFs / scans — **you**)

1. Cloud Scale → **Storage** → **Stratus**.
2. **Create Bucket** — globally unique name, e.g. `cip-fir-docs-<yourname>`.
3. Permission: **Authenticated** (recommended).
4. Optional: enable versioning.
5. `.env`:

```bash
CATALYST_STRATUS_BUCKET=your-bucket-name
CATALYST_STRATUS_ENDPOINT=
CATALYST_STRATUS_REGION=
```

**Key convention:** `fir/{year}/{station_id}/{crime_no}.pdf`

### B5. Cache (optional now, useful for chat)

1. Cloud Scale → **Cache**.
2. Create a segment, e.g. `cip_ai`.
3. `.env`: `CATALYST_CACHE_SEGMENT=cip_ai`

### B6. API Gateway (FS B)

1. Cloud Scale → **API Gateway**.
2. Create routes that will front Functions/AppSail (`/api/v1/*`, `/health`).
3. Attach Auth where needed.
4. `.env`: `CATALYST_API_GATEWAY_URL=...`

### B7. Signals (reindex on case write — **you + FS A**)

1. Cloud Scale → **Signals** (or Event Listeners / Signals in your console version).
2. Plan rule: **Data Store row insert/update on CaseMaster** → Event Function → reindex.
3. `.env`: `CATALYST_SIGNALS_TOPIC=...` / `CATALYST_EVENT_FUNCTION_ID=...`

Wire code later via `RagService.index_case`. Stub notes: `catalyst/signals/README.md`.

### B8. Cron (nightly reindex — later)

Cloud Scale → **Cron** / Job Scheduling → schedule Event Function.
`.env`: `CATALYST_CRON_JOB_ID=`

---

## Part C — QuickML RAG (your main AI path) — **do this carefully**

Official: [RAG help](https://docs.catalyst.zoho.com/en/quickml/help/generative-ai/rag/) ·
[Knowledge Base](https://docs.catalyst.zoho.com/en/quickml/help/generative-ai/knowledge-base/)

### C1. Open QuickML

1. In the project left nav, open **QuickML** (Generative AI / ML section).
2. You need a Zoho login that can access QuickML.

### C2. Knowledge Base — upload FIR text docs

1. Open **Knowledge Base**.
2. **Upload** sample docs (`.txt` / `.pdf` / `.docx`):
   - Export `text_blob` from our document builder into `.txt` files for the first demo.
   - Example content: CrimeNo + BriefFacts + sections (see schema doc).
3. Note document IDs if shown.

### C3. RAG chat in the console (prove it works before code)

1. Open **RAG** tab.
2. Model: **Qwen 2.5 14B Instruct** (current QuickML RAG model).
3. **Add Documents** → select files from Knowledge Base.
4. Ask: `Summarize the theft case involving a two-wheeler`.
5. Confirm answer + **View Response Breakdown** shows source docs.

If this fails in the console, fix KB/RAG here before writing Python.

### C4. Get RAG API endpoint → `.env`

1. Still on RAG screen → **View API** (top-right).
2. Copy **Endpoint URL** → `CATALYST_RAG_ENDPOINT` (and/or `CATALYST_QUICKML_ENDPOINT`).
3. Note OAuth scope: **`QuickML.deployment.READ`**.
4. Create OAuth client / token via [Zoho API Console](https://api-console.zoho.com/) (Self Client or Server-based app as per Zoho docs).
5. Store token/client securely — never commit:

```bash
CATALYST_RAG_ENDPOINT=https://...paste_from_view_api...
CATALYST_RAG_KNOWLEDGE_BASE_ID=paste_if_shown
CATALYST_QUICKML_ENDPOINT=https://...
CATALYST_QUICKML_MODEL_ID=qwen-or-model-id-from-ui
```

Our code calls this through `CatalystQuickMLClient.rag_query`
(`backend/app/integrations/catalyst/quickml.py`) — implement HTTP POST + OAuth next.

---

## Part D — Zia & SmartBrowz (Phase 3 — skim now)

| Console area | Enable when | `.env` |
|--------------|-------------|--------|
| **Zia** OCR / AutoML | Scanned FIRs / prediction | `CATALYST_ZIA_*`, `CATALYST_ZIA_AUTOML_*` |
| **SmartBrowz** | PDF case reports | `CATALYST_SMARTBROWZ_*` |

Skip until Case + RAG chat work.

---

## Part E — Hosting (FS B — coordinate)

| Goal | Console | Notes |
|------|---------|-------|
| React SPA | **Slate** or **Web Client Hosting** | Build `frontend/dist` |
| FastAPI | **Functions** (Advanced I/O) or **AppSail** | Prefer AppSail if you need full ASGI |
| Domain | **Domain Mappings** | Optional for demo |

CLI tip (after first project exists in console):

```bash
npm i -g zcatalyst-cli   # or follow current Catalyst CLI install docs
catalyst login
catalyst init            # link local folder to remote project
```

---

## Part F — Fill `.env` worksheet

Check off as you paste values:

- [ ] `CATALYST_PROJECT_ID`
- [ ] `CATALYST_ORG_ID`
- [ ] `CATALYST_ENV=Development`
- [ ] Auth: `CATALYST_CLIENT_ID` / `SECRET` / `AUTH_DOMAIN`
- [ ] `CATALYST_NOSQL_TABLE`
- [ ] `CATALYST_STRATUS_BUCKET`
- [ ] `CATALYST_CACHE_SEGMENT`
- [ ] `CATALYST_RAG_ENDPOINT` (from RAG **View API**)
- [ ] `CATALYST_RAG_KNOWLEDGE_BASE_ID`
- [ ] `CATALYST_QUICKML_*`
- [ ] OAuth access token strategy documented for the team (password manager / Catalyst Connections)

---

## Part G — How console maps to our repo

```text
Catalyst console                          This repo
─────────────────                         ─────────
QuickML RAG View API          →  .env + integrations/catalyst/quickml.py
Knowledge Base uploads        →  sample FIR .txt from document_builder
NoSQL table cip_rag_documents →  integrations/catalyst/nosql.py
Stratus bucket                →  integrations/catalyst/stratus.py
Data Store CaseMaster         →  FS A models + later Signals reindex
Authentication                →  FS B login + API Gateway
Signals / Cron                →  catalyst/signals + RagService.index_case
Slate / AppSail               →  frontend/ + backend deploy
```

---

## Recommended order for **you** (AI) this week

1. **A** — Create project, Project ID / Org ID in `.env`
2. **B3 + B4** — NoSQL table + Stratus bucket
3. **C** — Knowledge Base + RAG chat in UI with 1–2 sample FIR texts
4. **C4** — View API → wire `CatalystQuickMLClient` HTTP call
5. Tell FS A/B: Auth + Data Store + Gateway can proceed in parallel

---

## Common pitfalls

| Issue | Fix |
|-------|-----|
| Can’t create first project via CLI | Create in **console** first |
| RAG empty answers | Documents must be in **Knowledge Base** and **added** to the RAG session |
| 401 on RAG API | OAuth token missing scope `QuickML.deployment.READ` |
| Wrong environment | Check Development vs Production toggle in console |
| Secrets in git | Keep tokens only in `.env` (gitignored) |

---

## Help links

- [Catalyst projects](https://docs.catalyst.zoho.com/en/getting-started/catalyst-projects/)
- [General settings / Project ID](https://docs.catalyst.zoho.com/en/getting-started/set-up-a-catalyst-project/general-settings/)
- [Cloud Scale quick start](https://docs.catalyst.zoho.com/en/cloud-scale/getting-started/quick-start-guide/)
- [NoSQL intro](https://docs.catalyst.zoho.com/en/cloud-scale/help/nosql/introduction/)
- [QuickML RAG](https://docs.catalyst.zoho.com/en/quickml/help/generative-ai/rag/)
- [Python SDK overview](https://docs.catalyst.zoho.com/en/sdk/python/v1/overview/)
- Hackathon service list: [`catalyst.txt`](../../catalyst.txt)

When Project ID + RAG endpoint are in `.env`, say **“wire QuickML client”** and we can implement the real HTTP call in `quickml.py` next.
