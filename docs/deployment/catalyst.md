# Catalyst Deployment Guide

**Deployment via Catalyst is mandatory** for hackathon submission.
Using a third-party alternative when a Catalyst service exists may affect validity.

Source: [`catalyst.txt`](../../catalyst.txt).

## Capability → Required Catalyst Service

| # | Capability | Required Catalyst Service |
|---|------------|---------------------------|
| 1 | Serverless functions / backend logic | Catalyst Serverless (Functions) |
| 2 | Docker image deployment | Catalyst AppSail (custom OCI runtime) |
| 3 | Full web app in managed runtime | Catalyst AppSail (managed runtime) |
| 4 | Frontend / SPA / static site | Catalyst Slate or Web Client Hosting |
| 5 | Custom domain + SSL | Catalyst Domain Mappings |
| 6 | Relational database | Catalyst Data Store |
| 7 | Unstructured / semi-structured data | Catalyst NoSQL |
| 8 | Object / blob storage | Catalyst Stratus |
| 9 | Cache | Catalyst Cache |
| 10 | Full-text search (within Data Store) | Catalyst Data Store |
| 11 | Text LLMs / RAG / knowledge bases | Catalyst QuickML |
| 12 | No-code ML pipelines | Catalyst QuickML |
| 13 | Automated model training (tabular) | Catalyst Zia AutoML |
| 14 | OCR / Face / Image / Barcode / ID | Catalyst Zia Services |
| 15 | Voice (STT / TTS / translation) | Catalyst Zia Services |
| 16 | PDF / screenshots / headless browser | Catalyst SmartBrowz |
| 17 | User auth | Catalyst Authentication |
| 18 | API routing / throttling / auth | Catalyst API Gateway |
| 19 | OAuth tokens (Zoho / 3rd-party) | Catalyst Connections |
| 20 | Scheduled jobs / cron | Catalyst Cron / Job Scheduling |
| 21 | In-project events | Catalyst Signals + Event Functions |
| 22 | Cross-app event bus | Catalyst Signals |
| 23 | Multi-step workflows | Catalyst Circuits |
| 24 | Transactional email | Catalyst Mail |
| 25 | Push notifications | Catalyst Push Notifications |
| 26 | CI/CD | Catalyst Pipelines |

## Local vs production

| Concern | Local | Production |
|---------|-------|------------|
| Relational DB | Docker Postgres | Catalyst Data Store |
| Cache | Docker Redis | Catalyst Cache |
| Backend | `uvicorn` | Functions or AppSail |
| Frontend | Vite dev server | Slate / Web Client Hosting |
| CI | Local pytest / lint | Catalyst Pipelines |

## Scaffold folders

See [`../../catalyst/`](../../catalyst/).

**New to Catalyst?** Follow the click-by-click console guide:
[`catalyst_console_setup.md`](catalyst_console_setup.md)

**TODO:** Provision Catalyst project and fill `.env` from `.env.example`.
