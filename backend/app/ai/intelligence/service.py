"""MO clustering + intelligence brief services (challenge AI stretch)."""

from __future__ import annotations

import re
from collections import defaultdict
from datetime import UTC, datetime
from typing import Any

from app.ai.prediction.service import PredictionService
from app.core.config import Settings, get_settings
from app.core.logging import get_ai_logger
from app.integrations.catalyst.datastore import CatalystDataStoreClient
from app.schemas.ai.intelligence import (
    IntelligenceBriefResponse,
    IntelligenceBriefSection,
    MoCluster,
    MoClusterMember,
    MoClustersResponse,
)
from app.schemas.ai.prediction import RiskPredictRequest
from app.services import lookups_catalog as lookups
from app.services.analytics.mock_service import MockAnalyticsService

_TOKEN = re.compile(r"[a-z0-9]{3,}")
_STOP = {
    "the",
    "and",
    "for",
    "from",
    "with",
    "near",
    "case",
    "accused",
    "victim",
    "police",
    "station",
    "complaint",
    "reported",
    "incident",
}


def _tokens(text: str) -> set[str]:
    return {t for t in _TOKEN.findall(text.lower()) if t not in _STOP}


class IntelligenceService:
    """MO clusters + one-page SCRB intelligence brief."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._logger = get_ai_logger()
        self._ds = CatalystDataStoreClient(self._settings)
        self._analytics = MockAnalyticsService(self._ds)
        self._prediction = PredictionService(self._settings)

    def mo_clusters(self, *, min_size: int = 3, limit: int = 12) -> MoClustersResponse:
        cases = self._ds.get_paged_rows("case_master", max_rows=5000)
        acts = self._ds.get_paged_rows("act_section_association", max_rows=5000)
        acts_by_case: dict[int, list[str]] = defaultdict(list)
        for a in acts:
            cid = int(a.get("case_master_id") or 0)
            if not cid:
                continue
            sig = f"{a.get('act_id')}:{a.get('section_id')}"
            acts_by_case[cid].append(sig)

        # Bucket by dominant act:section, then refine with brief-facts tokens
        buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for c in cases:
            cid = int(c.get("ROWID") or c.get("case_master_id") or 0)
            if not cid:
                continue
            sigs = sorted(set(acts_by_case.get(cid) or ["UNK:UNK"]))
            primary = sigs[0]
            buckets[primary].append(c)

        clusters: list[MoCluster] = []
        clustered = 0
        for idx, (sig, members) in enumerate(
            sorted(buckets.items(), key=lambda kv: -len(kv[1]))
        ):
            if len(members) < min_size:
                continue
            # token signature from briefs
            token_counts: dict[str, int] = defaultdict(int)
            district_names: set[str] = set()
            mapped_members: list[MoClusterMember] = []
            for m in members[:20]:
                cid = int(m.get("ROWID") or m.get("case_master_id") or 0)
                st = int(m.get("police_station_id") or 0)
                did = lookups.station_district_id(st)
                if did:
                    district_names.add(lookups.district_name(did))
                brief = str(m.get("brief_facts") or "")
                for t in _tokens(brief):
                    token_counts[t] += 1
                mapped_members.append(
                    MoClusterMember(
                        case_master_id=cid,
                        crime_no=str(m.get("crime_no") or ""),
                        brief_facts=brief or None,
                        police_station_id=st or None,
                        district_id=did,
                        crime_major_head_id=(
                            int(m["crime_major_head_id"])
                            if m.get("crime_major_head_id") not in (None, "")
                            else None
                        ),
                    )
                )
            top_tokens = [
                t
                for t, _ in sorted(
                    token_counts.items(), key=lambda kv: kv[1], reverse=True
                )[:5]
            ]
            act, sec = (sig.split(":", 1) + [""])[:2]
            label = f"{act} §{sec}" if sec else act
            if top_tokens:
                label = f"{label} · {'/'.join(top_tokens[:3])}"
            clusters.append(
                MoCluster(
                    cluster_id=f"mo-{idx+1:02d}",
                    label=label,
                    mo_signature=sig,
                    size=len(members),
                    districts=sorted(district_names)[:8],
                    act_sections=sig.split(",") if False else [sig],
                    members=mapped_members,
                    similarity_note=(
                        f"Shared act/section {sig}"
                        + (
                            f"; common tokens: {', '.join(top_tokens)}"
                            if top_tokens
                            else ""
                        )
                    ),
                )
            )
            clustered += len(members)
            if len(clusters) >= limit:
                break

        self._logger.info("mo_clusters count=%s cases=%s", len(clusters), clustered)
        return MoClustersResponse(
            clusters=clusters,
            total_cases_clustered=clustered,
        )

    def intelligence_brief(self, *, horizon_days: int = 7) -> IntelligenceBriefResponse:
        overview = self._analytics.overview()
        trends = self._analytics.trend_alerts(
            recent_days=horizon_days,
            baseline_days=max(28, horizon_days * 4),
            threshold=1.5,
        )
        socio = self._analytics.socio_economic_overlay()
        risk = self._prediction.predict_risk(
            RiskPredictRequest(horizon_days=horizon_days)
        )
        mo = self.mo_clusters(min_size=3, limit=5)

        top_alerts = [a for a in trends.alerts if a.is_alert][:5]
        top_risk = risk.items[:5]
        top_mo = mo.clusters[:3]

        if top_alerts:
            a0 = top_alerts[0]
            headline = (
                f"{a0.district_name} shows {a0.spike_ratio}× spike in "
                f"{a0.crime_head_name} ({a0.recent_count} recent FIRs)."
            )
        elif top_risk:
            r0 = top_risk[0]
            headline = (
                f"Highest predictive risk: {r0.scope_name or r0.scope_id} "
                f"(score {r0.risk_score})."
            )
        else:
            headline = (
                f"Statewide desk: {overview.total_cases} FIRs across "
                f"{overview.districts_covered} districts."
            )

        sections = [
            IntelligenceBriefSection(
                title="Statewide posture",
                body=(
                    f"{overview.total_cases} FIRs in view; "
                    f"{overview.cases_with_coordinates} geocoded; "
                    f"status mix led by "
                    f"{overview.by_status[0].name if overview.by_status else 'n/a'}."
                ),
            ),
            IntelligenceBriefSection(
                title="Emerging trends",
                body=(
                    "; ".join(
                        f"{a.district_name}/{a.crime_head_name} {a.spike_ratio}×"
                        for a in top_alerts
                    )
                    or "No spike alerts above threshold."
                ),
            ),
            IntelligenceBriefSection(
                title="Socio-economic pressure",
                body=socio.insight,
            ),
            IntelligenceBriefSection(
                title="MO / association clusters",
                body=(
                    "; ".join(
                        f"{c.label} (n={c.size}; districts: {', '.join(c.districts[:3]) or 'n/a'})"
                        for c in top_mo
                    )
                    or "No MO clusters above minimum size."
                ),
            ),
            IntelligenceBriefSection(
                title="Predictive risk watchlist",
                body=(
                    "; ".join(
                        f"{r.scope_name or r.scope_id}={r.risk_score}" for r in top_risk
                    )
                    or "No risk scores available."
                ),
            ),
        ]
        actions = [
            "Prioritize beat deployment in top spike districts during peak hotspot hours.",
            "Cross-check MO clusters for repeat person_id / name links across PS jurisdictions.",
            "Task SCRB analysts to validate socio-normalized pressure districts before resource shift.",
        ]
        if top_alerts:
            actions.insert(
                0,
                f"Issue red-zone advisory for {top_alerts[0].district_name} "
                f"({top_alerts[0].crime_head_name}).",
            )
        return IntelligenceBriefResponse(
            title="SCRB Strategic Intelligence Brief",
            generated_at=datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC"),
            horizon_days=horizon_days,
            headline=headline,
            sections=sections,
            recommended_actions=actions,
        )
