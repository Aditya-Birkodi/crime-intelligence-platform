"""Network / link-analysis service (B3).

Builds ego graphs from CaseStore (Postgres or Catalyst Data Store).
"""

from __future__ import annotations

import re
from collections import defaultdict
from datetime import date

from app.exceptions.base import NotFoundError, ValidationError
from app.repositories.case.case_store import CaseStore
from app.schemas.case.case_master import AccusedRead, CaseMasterDetail
from app.schemas.network import (
    GraphEdge,
    GraphNode,
    NetworkGraphResponse,
    OffenderCaseSummary,
    OffenderProfile,
)

_SCORE = {
    "accused_of": 1.0,
    "victim_of": 1.0,
    "filed_at": 0.55,
    "same_person": 0.92,
    "co_accused": 0.75,
}


def _norm_name(name: str) -> str:
    return re.sub(r"\s+", " ", name.strip().lower())


def _case_node_id(case_id: int) -> str:
    return f"case:{case_id}"


def _accused_node_id(accused_id: int) -> str:
    return f"accused:{accused_id}"


def _victim_node_id(victim_id: int) -> str:
    return f"victim:{victim_id}"


def _station_node_id(station_id: int) -> str:
    return f"station:{station_id}"


class NetworkService:
    """Link analysis over FIR parties."""

    def __init__(
        self,
        store: CaseStore,
        station_names: dict[int, str] | None = None,
    ) -> None:
        self._store = store
        self._station_names = station_names or {}

    def graph(
        self,
        *,
        case_id: int | None = None,
        accused_id: int | None = None,
        depth: int = 1,
    ) -> NetworkGraphResponse:
        if (case_id is None) == (accused_id is None):
            raise ValidationError("Provide exactly one of case_id or accused_id")
        if depth < 1 or depth > 3:
            raise ValidationError("depth must be between 1 and 3")

        all_accused = self._store.list_accused(limit=5000)
        by_case = self._cases_index(limit=500)

        if case_id is not None:
            seed = _case_node_id(case_id)
            if case_id not in by_case:
                raise NotFoundError(f"Case {case_id} not found")
            seed_case_ids = {case_id}
            seed_accused_ids = {
                a.accused_master_id for a in all_accused if a.case_master_id == case_id
            }
        else:
            assert accused_id is not None
            seed = _accused_node_id(accused_id)
            seed_acc = next(
                (a for a in all_accused if a.accused_master_id == accused_id),
                None,
            )
            if seed_acc is None:
                raise NotFoundError(f"Accused {accused_id} not found")
            seed_accused_ids = {accused_id}
            seed_case_ids = {seed_acc.case_master_id}

        # Expand by same person / name across cases
        for _ in range(depth):
            related = self._related_accused(all_accused, seed_accused_ids)
            seed_accused_ids |= {a.accused_master_id for a in related}
            seed_case_ids |= {a.case_master_id for a in related}
            for cid in list(seed_case_ids):
                seed_accused_ids |= {
                    a.accused_master_id for a in all_accused if a.case_master_id == cid
                }

        nodes: dict[str, GraphNode] = {}
        edges: dict[str, GraphEdge] = {}

        for cid in seed_case_ids:
            detail = by_case.get(cid)
            if detail is None:
                continue
            self._add_case_subgraph(detail, nodes, edges)

        # same_person edges across accused in the ego set
        groups: dict[str, list[AccusedRead]] = defaultdict(list)
        for a in all_accused:
            if a.accused_master_id not in seed_accused_ids:
                continue
            key = (
                f"pid:{a.person_id.strip().lower()}"
                if a.person_id and a.person_id.strip()
                else f"name:{_norm_name(a.accused_name)}"
            )
            if key.startswith("name:unknown"):
                continue
            groups[key].append(a)

        for members in groups.values():
            if len(members) < 2:
                continue
            anchor = members[0]
            for other in members[1:]:
                eid = (
                    f"same_person:{anchor.accused_master_id}:"
                    f"{other.accused_master_id}"
                )
                edges[eid] = GraphEdge(
                    id=eid,
                    source=_accused_node_id(anchor.accused_master_id),
                    target=_accused_node_id(other.accused_master_id),
                    relation="same_person",
                    score=_SCORE["same_person"],
                )

        return NetworkGraphResponse(
            seed=seed,
            nodes=list(nodes.values()),
            edges=list(edges.values()),
        )

    def offender_profile(self, accused_id: int) -> OffenderProfile:
        all_accused = self._store.list_accused(limit=5000)
        seed = next((a for a in all_accused if a.accused_master_id == accused_id), None)
        if seed is None:
            raise NotFoundError(f"Accused {accused_id} not found")

        related = self._related_accused(all_accused, {accused_id})
        cohort = [seed, *[a for a in related if a.accused_master_id != accused_id]]
        by_case = self._cases_index(limit=500)

        cases: list[OffenderCaseSummary] = []
        mo: list[str] = []
        for a in cohort:
            detail = by_case.get(a.case_master_id)
            if detail is None:
                continue
            cases.append(
                OffenderCaseSummary(
                    case_master_id=detail.case_master_id,
                    crime_no=detail.crime_no,
                    case_no=detail.case_no,
                    brief_facts=detail.brief_facts,
                    crime_registered_date=detail.crime_registered_date,
                    police_station_id=detail.police_station_id,
                    crime_major_head_id=detail.crime_major_head_id,
                    accused_master_id=a.accused_master_id,
                )
            )
            if detail.brief_facts:
                mo.append(detail.brief_facts.strip())
            for sec in detail.act_sections:
                mo.append(f"{sec.act_id} {sec.section_id}".strip())

        # unique MO hints preserving order
        seen: set[str] = set()
        modus: list[str] = []
        for item in mo:
            key = item.lower()
            if key in seen:
                continue
            seen.add(key)
            modus.append(item)

        cases.sort(
            key=lambda c: (c.crime_registered_date or date.min, c.case_master_id)
        )

        return OffenderProfile(
            accused_master_id=seed.accused_master_id,
            accused_name=seed.accused_name,
            person_id=seed.person_id,
            age_year=seed.age_year,
            gender_id=seed.gender_id,
            case_count=len({c.case_master_id for c in cases}),
            cases=cases,
            modus_operandi=modus[:12],
            linked_accused_ids=[
                a.accused_master_id for a in cohort if a.accused_master_id != accused_id
            ],
        )

    def _cases_index(self, *, limit: int) -> dict[int, CaseMasterDetail]:
        items, _ = self._store.list_filtered(limit=limit, offset=0)
        out: dict[int, CaseMasterDetail] = {}
        for item in items:
            detail = self._store.get_detail(item.case_master_id)
            if detail is not None:
                out[detail.case_master_id] = detail
        return out

    @staticmethod
    def _related_accused(
        all_accused: list[AccusedRead], seed_ids: set[int]
    ) -> list[AccusedRead]:
        seeds = [a for a in all_accused if a.accused_master_id in seed_ids]
        if not seeds:
            return []
        person_ids = {
            a.person_id.strip().lower()
            for a in seeds
            if a.person_id and a.person_id.strip()
        }
        names = {_norm_name(a.accused_name) for a in seeds}
        names.discard("unknown")

        related: list[AccusedRead] = []
        for a in all_accused:
            if a.accused_master_id in seed_ids:
                continue
            if a.person_id and a.person_id.strip().lower() in person_ids:
                related.append(a)
                continue
            if _norm_name(a.accused_name) in names:
                related.append(a)
        return related

    def _add_case_subgraph(
        self,
        detail: CaseMasterDetail,
        nodes: dict[str, GraphNode],
        edges: dict[str, GraphEdge],
    ) -> None:
        cid = detail.case_master_id
        cnode = _case_node_id(cid)
        nodes[cnode] = GraphNode(
            id=cnode,
            type="case",
            label=detail.crime_no,
            meta={
                "case_master_id": cid,
                "case_no": detail.case_no,
                "brief_facts": detail.brief_facts,
                "crime_registered_date": (
                    detail.crime_registered_date.isoformat()
                    if detail.crime_registered_date
                    else None
                ),
                "police_station_id": detail.police_station_id,
            },
        )

        snode = _station_node_id(detail.police_station_id)
        station_label = self._station_names.get(
            detail.police_station_id,
            f"PS {detail.police_station_id}",
        )
        nodes.setdefault(
            snode,
            GraphNode(
                id=snode,
                type="station",
                label=station_label,
                meta={"police_station_id": detail.police_station_id},
            ),
        )
        eid = f"filed_at:{cid}:{detail.police_station_id}"
        edges[eid] = GraphEdge(
            id=eid,
            source=cnode,
            target=snode,
            relation="filed_at",
            score=_SCORE["filed_at"],
        )

        accused_ids: list[int] = []
        for a in detail.accused:
            anode = _accused_node_id(a.accused_master_id)
            accused_ids.append(a.accused_master_id)
            nodes[anode] = GraphNode(
                id=anode,
                type="accused",
                label=a.accused_name,
                meta={
                    "accused_master_id": a.accused_master_id,
                    "person_id": a.person_id,
                    "case_master_id": cid,
                    "age_year": a.age_year,
                    "gender_id": a.gender_id,
                    "display": (
                        f"{a.accused_name}"
                        + (f" ({a.age_year}y)" if a.age_year is not None else "")
                        + (f" · {a.person_id}" if a.person_id else "")
                    ),
                },
            )
            ae = f"accused_of:{a.accused_master_id}:{cid}"
            edges[ae] = GraphEdge(
                id=ae,
                source=anode,
                target=cnode,
                relation="accused_of",
                score=_SCORE["accused_of"],
            )

        for i, left in enumerate(accused_ids):
            for right in accused_ids[i + 1 :]:
                ce = f"co_accused:{left}:{right}:{cid}"
                edges[ce] = GraphEdge(
                    id=ce,
                    source=_accused_node_id(left),
                    target=_accused_node_id(right),
                    relation="co_accused",
                    score=_SCORE["co_accused"],
                )

        for v in detail.victims:
            vnode = _victim_node_id(v.victim_master_id)
            nodes[vnode] = GraphNode(
                id=vnode,
                type="victim",
                label=v.victim_name,
                meta={
                    "victim_master_id": v.victim_master_id,
                    "case_master_id": cid,
                    "age_year": v.age_year,
                    "gender_id": v.gender_id,
                    "display": (
                        f"{v.victim_name}"
                        + (f" ({v.age_year}y)" if v.age_year is not None else "")
                    ),
                },
            )
            ve = f"victim_of:{v.victim_master_id}:{cid}"
            edges[ve] = GraphEdge(
                id=ve,
                source=vnode,
                target=cnode,
                relation="victim_of",
                score=_SCORE["victim_of"],
            )


# date.min used above for stable sorting when registration date is missing
