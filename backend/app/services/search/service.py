"""Cross-entity name search (accused / victim / complainant / case)."""

from __future__ import annotations

from typing import Any

from app.integrations.catalyst.datastore import CatalystDataStoreClient
from app.schemas.search import SearchHit, SearchResponse


class SearchService:
    def __init__(self, ds: CatalystDataStoreClient | None = None) -> None:
        self._ds = ds or CatalystDataStoreClient()

    def search(
        self,
        query: str,
        *,
        types: list[str] | None = None,
        limit: int = 40,
    ) -> SearchResponse:
        q = (query or "").strip().lower()
        if len(q) < 2:
            return SearchResponse(query=query, total=0, items=[])

        wanted = {
            t.strip().lower()
            for t in (types or ["accused", "victim", "complainant", "case"])
            if t.strip()
        }
        hits: list[SearchHit] = []

        case_by_id: dict[int, dict[str, Any]] = {}
        for row in self._ds.get_paged_rows("case_master", max_rows=3000):
            cid = int(row.get("ROWID") or row.get("case_master_id") or 0)
            if cid:
                case_by_id[cid] = row

        def crime_no_for(case_id: int | None) -> str | None:
            if not case_id:
                return None
            row = case_by_id.get(case_id)
            return str(row.get("crime_no")) if row else None

        if "case" in wanted:
            for cid, row in case_by_id.items():
                crime_no = str(row.get("crime_no") or "")
                case_no = str(row.get("case_no") or "")
                facts = str(row.get("brief_facts") or "")
                blob = f"{crime_no} {case_no} {facts}".lower()
                if q in blob:
                    field = (
                        "crime_no"
                        if q in crime_no.lower()
                        else ("case_no" if q in case_no.lower() else "brief_facts")
                    )
                    hits.append(
                        SearchHit(
                            entity_type="case",
                            entity_id=cid,
                            name=crime_no or case_no or f"Case {cid}",
                            case_master_id=cid,
                            crime_no=crime_no or None,
                            match_field=field,
                            score=1.0 if field != "brief_facts" else 0.6,
                        )
                    )

        if "accused" in wanted:
            for row in self._ds.get_paged_rows("accused", max_rows=5000):
                name = str(row.get("accused_name") or "")
                person_id = str(row.get("person_id") or "")
                if q not in name.lower() and q not in person_id.lower():
                    continue
                case_id: int | None = int(row.get("case_master_id") or 0) or None
                hits.append(
                    SearchHit(
                        entity_type="accused",
                        entity_id=int(row.get("ROWID") or 0),
                        name=name,
                        case_master_id=case_id,
                        crime_no=crime_no_for(case_id),
                        person_id=person_id or None,
                        match_field=(
                            "person_id" if q in person_id.lower() else "accused_name"
                        ),
                        score=1.0,
                    )
                )

        if "victim" in wanted:
            for row in self._ds.get_paged_rows("victim", max_rows=5000):
                name = str(row.get("victim_name") or "")
                if q not in name.lower():
                    continue
                case_id = int(row.get("case_master_id") or 0) or None
                hits.append(
                    SearchHit(
                        entity_type="victim",
                        entity_id=int(row.get("ROWID") or 0),
                        name=name,
                        case_master_id=case_id,
                        crime_no=crime_no_for(case_id),
                        match_field="victim_name",
                        score=1.0,
                    )
                )

        if "complainant" in wanted:
            for row in self._ds.get_paged_rows("complainant_details", max_rows=5000):
                name = str(row.get("complainant_name") or "")
                if q not in name.lower():
                    continue
                case_id = int(row.get("case_master_id") or 0) or None
                hits.append(
                    SearchHit(
                        entity_type="complainant",
                        entity_id=int(
                            row.get("ROWID") or row.get("complainant_id") or 0
                        ),
                        name=name,
                        case_master_id=case_id,
                        crime_no=crime_no_for(case_id),
                        match_field="complainant_name",
                        score=1.0,
                    )
                )

        # Prefer exact-ish name matches
        hits.sort(key=lambda h: (-h.score, h.name.lower()))
        limited = hits[:limit]
        return SearchResponse(query=query, total=len(hits), items=limited)
