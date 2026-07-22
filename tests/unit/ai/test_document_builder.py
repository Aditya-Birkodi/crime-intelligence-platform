"""Unit tests for Catalyst-oriented RAG document builder."""

from __future__ import annotations

import json
from pathlib import Path

from etl.document_builder.pipeline import DocumentBuilderPipeline, build_rag_text_blob

FIXTURE = Path(__file__).resolve().parents[2] / "fixtures" / "sample_fir_case.json"


def test_document_builder_produces_catalyst_schema() -> None:
    case = json.loads(FIXTURE.read_text(encoding="utf-8"))
    doc = DocumentBuilderPipeline().run(case)

    assert doc["doc_id"] == "case:1"
    assert doc["case_master_id"] == 1
    assert doc["crime_no"] == "104430006202600001"
    assert "theft" in doc["brief_facts"].lower()
    assert doc["catalyst"]["stratus_uri"] is None
    assert "text_blob" in doc
    assert "CrimeNo:" in doc["text_blob"]
    assert "IPC" in doc["text_blob"]


def test_build_rag_text_blob() -> None:
    blob = build_rag_text_blob(
        {
            "crime_no": "X",
            "brief_facts": "Y",
            "act_sections": [
                {"act_code": "IPC", "section_code": "302", "description": "Murder"}
            ],
        }
    )
    assert "CrimeNo: X" in blob
    assert "IPC 302" in blob
