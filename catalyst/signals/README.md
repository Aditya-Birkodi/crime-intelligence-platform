# Catalyst Signals

React to in-project events (Data Store inserts, Stratus uploads, signups).

## AI reindex flow (required)

```text
Data Store: CaseMaster insert/update
  → Signal
  → Event Function
  → RagService.index_case
  → NoSQL upsert + QuickML RAG index
```

**TODO:**

- [ ] Register Signal on CaseMaster (or CIP case table) write
- [ ] Event Function invokes document_builder / RagService
- [ ] Stratus `fir/` upload → optional Zia OCR → same index path
- [ ] Cross-app event routing if multi-app
