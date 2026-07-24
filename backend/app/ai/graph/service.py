"""Graph RAG helpers — NetworkX projection hosted on Catalyst AppSail.

Open-source NetworkX runs in-process (no external Neo4j). Graph is built from
the same CaseStore ego network used by B3, then summarized for QuickML RAG.
"""

from __future__ import annotations

from typing import Any

import networkx as nx

from app.core.logging import get_ai_logger
from app.repositories.case.case_store import CaseStore
from app.schemas.ai.graph import GraphCentralNode, GraphRagContext
from app.services.network.service import NetworkService


class GraphService:
    """Build NetworkX ego graphs and text context for Graph RAG."""

    def __init__(self, store: CaseStore) -> None:
        self._logger = get_ai_logger()
        self._network = NetworkService(store)

    def context(
        self,
        *,
        case_id: int | None = None,
        accused_id: int | None = None,
        depth: int = 2,
    ) -> GraphRagContext:
        graph = self._network.graph(case_id=case_id, accused_id=accused_id, depth=depth)
        g = nx.Graph()
        node_meta: dict[str, dict[str, Any]] = {}
        for node in graph.nodes:
            g.add_node(node.id, type=node.type, label=node.label)
            node_meta[node.id] = {
                "type": node.type,
                "label": node.label,
                **(node.meta or {}),
            }
        for edge in graph.edges:
            g.add_edge(
                edge.source,
                edge.target,
                relation=edge.relation,
                score=float(edge.score),
            )

        # Degree centrality (fast, stable on small FIR ego graphs)
        if g.number_of_nodes() == 0:
            return GraphRagContext(
                seed=graph.seed,
                depth=depth,
                node_count=0,
                edge_count=0,
                summary="Empty graph neighborhood.",
            )

        centrality = nx.degree_centrality(g)
        top = sorted(centrality.items(), key=lambda kv: kv[1], reverse=True)[:8]
        central = [
            GraphCentralNode(
                id=nid,
                type=str(node_meta.get(nid, {}).get("type") or ""),
                label=str(node_meta.get(nid, {}).get("label") or nid),
                score=round(float(score), 4),
            )
            for nid, score in top
        ]

        crime_nos: list[str] = []
        case_ids: list[int] = []
        persons: list[str] = []
        fact_lines: list[str] = []
        for _nid, meta in node_meta.items():
            if meta.get("type") == "case":
                crime = str(meta.get("label") or "")
                if crime:
                    crime_nos.append(crime)
                cid = meta.get("case_master_id")
                if cid is not None:
                    case_ids.append(int(cid))
                brief = meta.get("brief_facts")
                if brief:
                    fact_lines.append(f"- Case {crime}: {str(brief)[:220]}")
            if meta.get("type") == "accused":
                pid = meta.get("person_id")
                label = meta.get("label")
                if pid:
                    persons.append(f"{label} ({pid})")
                elif label:
                    persons.append(str(label))

        # Unique preserve order
        def _uniq(items: list[str]) -> list[str]:
            seen: set[str] = set()
            out: list[str] = []
            for item in items:
                key = item.lower()
                if key in seen:
                    continue
                seen.add(key)
                out.append(item)
            return out

        crime_nos = _uniq(crime_nos)
        persons = _uniq(persons)
        case_ids = list(dict.fromkeys(case_ids))

        same_person = sum(
            1 for _, _, d in g.edges(data=True) if d.get("relation") == "same_person"
        )
        co_accused = sum(
            1 for _, _, d in g.edges(data=True) if d.get("relation") == "co_accused"
        )

        summary_parts = [
            f"Ego seed: {graph.seed} (depth={depth}).",
            f"Graph size: {g.number_of_nodes()} nodes, {g.number_of_edges()} edges "
            f"(NetworkX on AppSail).",
            f"Linked CrimeNos: {', '.join(crime_nos) or 'none'}.",
            f"Linked persons: {', '.join(persons[:12]) or 'none'}.",
            f"Identity links (same_person): {same_person}; co-accused links: {co_accused}.",
            "Central nodes: "
            + ", ".join(f"{c.label}[{c.type}]={c.score}" for c in central[:5]),
        ]
        if fact_lines:
            summary_parts.append("Neighborhood brief facts:")
            summary_parts.extend(fact_lines[:8])

        summary = "\n".join(summary_parts)
        self._logger.info(
            "graph_rag_context seed=%s nodes=%s edges=%s",
            graph.seed,
            g.number_of_nodes(),
            g.number_of_edges(),
        )
        return GraphRagContext(
            seed=graph.seed,
            depth=depth,
            node_count=g.number_of_nodes(),
            edge_count=g.number_of_edges(),
            neighbor_crime_nos=crime_nos,
            neighbor_case_ids=case_ids,
            linked_persons=persons[:20],
            central_nodes=central,
            summary=summary,
            engine="networkx",
        )
