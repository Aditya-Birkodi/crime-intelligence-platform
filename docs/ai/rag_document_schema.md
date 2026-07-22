# RAG document schema (Catalyst NoSQL / QuickML)

Documents produced by `etl.document_builder` and stored in **Catalyst NoSQL**,
then indexed into **Catalyst QuickML RAG**.

## Document shape

```json
{
  "doc_id": "case:123",
  "case_master_id": 123,
  "crime_no": "104430006202600001",
  "case_no": "202600001",
  "police_station_id": 6,
  "district_id": 443,
  "case_status_id": 1,
  "crime_major_head_id": null,
  "crime_minor_head_id": null,
  "brief_facts": "Complainant reported theft of two-wheeler...",
  "act_sections": [
    {"act_code": "IPC", "section_code": "379", "description": "Theft"}
  ],
  "incident_from": "2026-01-15T21:00:00",
  "incident_to": "2026-01-15T23:00:00",
  "latitude": 12.9716,
  "longitude": 77.5946,
  "source": "case_master",
  "catalyst": {
    "nosql_table": "${CATALYST_NOSQL_TABLE}",
    "rag_knowledge_base_id": "${CATALYST_RAG_KNOWLEDGE_BASE_ID}",
    "stratus_uri": null
  },
  "indexed_at": "2026-07-21T16:00:00Z"
}
```

## Text blob for embedding / RAG

Concatenate for QuickML indexing:

```text
CrimeNo: {crime_no}
Brief Facts: {brief_facts}
Sections: {act} {section} — {description}; ...
```

## Ownership

| Step | Catalyst service | Owner |
|------|------------------|-------|
| Read case | Data Store (via FS A API) | FS A |
| Optional PDF bytes | Stratus | AI |
| OCR if scanned | Zia Services | AI |
| Persist doc | NoSQL | AI |
| Index / query | QuickML RAG | AI |
| Trigger reindex | Signals + Cron | AI + FS B |
