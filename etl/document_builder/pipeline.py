"""Build RAG documents for Catalyst NoSQL + QuickML RAG.

Output shape: docs/ai/rag_document_schema.md
Downstream: CatalystNoSQLClient.upsert + CatalystQuickMLClient.index_document
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


def build_rag_text_blob(document: dict[str, Any]) -> str:
    """Plain text used for QuickML embedding / retrieval."""
    sections = document.get("act_sections") or []
    section_parts: list[str] = []
    for item in sections:
        if not isinstance(item, dict):
            continue
        section_parts.append(
            f"{item.get('act_code', '')} {item.get('section_code', '')} — "
            f"{item.get('description', '')}".strip()
        )
    sections_line = "; ".join(section_parts) if section_parts else ""
    return (
        f"CrimeNo: {document.get('crime_no', '')}\n"
        f"Brief Facts: {document.get('brief_facts', '')}\n"
        f"Sections: {sections_line}"
    ).strip()


class DocumentBuilderPipeline:
    """FIR case dict → Catalyst-oriented RAG document."""

    def run(
        self, case: dict[str, Any], *, stratus_uri: str | None = None
    ) -> dict[str, Any]:
        """Build a NoSQL/QuickML-ready document from a case payload.

        Expected keys (from CaseMaster / joins): case_master_id, crime_no,
        brief_facts, optional act_sections list, geo/status ids.
        """
        case_master_id = case.get("case_master_id") or case.get("CaseMasterID")
        if case_master_id is None:
            raise ValueError("case_master_id is required")

        crime_no = str(case.get("crime_no") or case.get("CrimeNo") or "")
        doc_id = f"case:{case_master_id}"

        document: dict[str, Any] = {
            "doc_id": doc_id,
            "case_master_id": int(case_master_id),
            "crime_no": crime_no,
            "case_no": case.get("case_no") or case.get("CaseNo"),
            "police_station_id": case.get("police_station_id")
            or case.get("PoliceStationID"),
            "district_id": case.get("district_id"),
            "case_status_id": case.get("case_status_id") or case.get("CaseStatusID"),
            "crime_major_head_id": case.get("crime_major_head_id")
            or case.get("CrimeMajorHeadID"),
            "crime_minor_head_id": case.get("crime_minor_head_id")
            or case.get("CrimeMinorHeadID"),
            "brief_facts": case.get("brief_facts") or case.get("BriefFacts") or "",
            "act_sections": case.get("act_sections") or [],
            "incident_from": case.get("incident_from") or case.get("IncidentFromDate"),
            "incident_to": case.get("incident_to") or case.get("IncidentToDate"),
            "latitude": case.get("latitude"),
            "longitude": case.get("longitude"),
            "source": "case_master",
            "catalyst": {
                "nosql_table": None,  # filled by caller from settings
                "rag_knowledge_base_id": None,
                "stratus_uri": stratus_uri,
            },
            "indexed_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        }
        document["text_blob"] = build_rag_text_blob(document)
        return document

    def run_and_publish(
        self,
        case: dict[str, Any],
        *,
        nosql_client: Any,
        quickml_client: Any,
        stratus_uri: str | None = None,
        nosql_table: str | None = None,
        rag_knowledge_base_id: str | None = None,
    ) -> dict[str, Any]:
        """Build doc then push to Catalyst NoSQL + QuickML RAG.

        Pass real Catalyst clients in production. Unit tests should mock them.
        """
        document = self.run(case, stratus_uri=stratus_uri)
        document["catalyst"]["nosql_table"] = nosql_table
        document["catalyst"]["rag_knowledge_base_id"] = rag_knowledge_base_id
        nosql_client.upsert_rag_document(document)
        quickml_client.index_document(document)
        return document
