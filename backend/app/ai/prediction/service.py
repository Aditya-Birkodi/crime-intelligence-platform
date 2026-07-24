"""Risk prediction + anomaly detection for B4 (heuristic / Zia-ready).

Uses `database/seed/ai_case_features.json` produced by the FIR seeder.
When Zia AutoML is configured later, swap `_score_scope` for live inference.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from app.core.config import Settings, get_settings
from app.core.logging import get_ai_logger
from app.schemas.ai.anomalies import AnomaliesResponse, AnomalyItem
from app.schemas.ai.prediction import (
    RiskPredictRequest,
    RiskPredictResponse,
    RiskScoreItem,
)


def _default_features_path() -> Path:
    return (
        Path(__file__).resolve().parents[4]
        / "database"
        / "seed"
        / "ai_case_features.json"
    )


class PredictionService:
    """District / station risk scores from seeded case features."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._logger = get_ai_logger()
        self._settings = settings or get_settings()

    def _features_path(self) -> Path:
        configured = self._settings.catalyst.ai_features_path or ""
        return Path(configured) if configured else _default_features_path()

    def _load_features(self) -> list[dict[str, Any]]:
        path = self._features_path()
        if not path.exists():
            self._logger.warning("ai_features_missing path=%s", path)
            return []
        raw = json.loads(path.read_text(encoding="utf-8"))
        return raw if isinstance(raw, list) else []

    def predict_risk(self, request: RiskPredictRequest) -> RiskPredictResponse:
        rows = self._load_features()
        if request.district_id is not None:
            rows = [
                r for r in rows if int(r.get("district_id") or 0) == request.district_id
            ]
        if request.police_station_id is not None:
            rows = [
                r
                for r in rows
                if int(r.get("police_station_id") or 0) == request.police_station_id
            ]

        by_district: dict[int, list[dict[str, Any]]] = defaultdict(list)
        by_station: dict[int, list[dict[str, Any]]] = defaultdict(list)
        for r in rows:
            by_district[int(r.get("district_id") or 0)].append(r)
            by_station[int(r.get("police_station_id") or 0)].append(r)

        items: list[RiskScoreItem] = []
        if request.police_station_id is not None:
            for sid, group in sorted(by_station.items()):
                items.append(self._score_scope("station", sid, group))
        else:
            for did, group in sorted(by_district.items()):
                items.append(self._score_scope("district", did, group))

        items.sort(key=lambda x: x.risk_score, reverse=True)
        return RiskPredictResponse(
            horizon_days=request.horizon_days,
            items=items,
            provider="catalyst_heuristic",
            model="local_risk_v1",
        )

    def list_anomalies(self, *, limit: int = 20) -> AnomaliesResponse:
        rows = self._load_features()
        items: list[AnomalyItem] = []

        # High risk cases
        for r in sorted(
            rows, key=lambda x: int(x.get("risk_score") or 0), reverse=True
        ):
            score = int(r.get("risk_score") or 0)
            if score < 80:
                continue
            cid = int(r.get("case_master_id") or 0)
            items.append(
                AnomalyItem(
                    anomaly_id=f"high-risk:{cid}",
                    kind="high_risk_case",
                    severity="high" if score >= 90 else "medium",
                    title=f"Elevated risk on CrimeNo {r.get('crime_no')}",
                    detail=(
                        f"RiskScore={score}, severity={r.get('severity')}, "
                        f"head={r.get('crime_major_head')}"
                    ),
                    district_id=int(r["district_id"]) if r.get("district_id") else None,
                    police_station_id=(
                        int(r["police_station_id"])
                        if r.get("police_station_id")
                        else None
                    ),
                    case_master_ids=[cid] if cid else [],
                    score=float(score),
                )
            )

        # District volume spikes vs median
        by_district: dict[int, list[dict[str, Any]]] = defaultdict(list)
        for r in rows:
            by_district[int(r.get("district_id") or 0)].append(r)
        counts = [len(g) for g in by_district.values()] or [0]
        counts_sorted = sorted(counts)
        median = counts_sorted[len(counts_sorted) // 2]
        for did, group in by_district.items():
            if median > 0 and len(group) >= max(3, int(median * 2)):
                items.append(
                    AnomalyItem(
                        anomaly_id=f"volume-spike:district:{did}",
                        kind="volume_spike",
                        severity="medium",
                        title=f"Case volume spike in district {did}",
                        detail=(
                            f"{len(group)} cases vs median {median} across districts"
                        ),
                        district_id=did,
                        case_master_ids=[
                            int(r["case_master_id"])
                            for r in group[:10]
                            if r.get("case_master_id") is not None
                        ],
                        score=float(len(group)),
                    )
                )

        # Repeat-heavy stations (many arrests)
        by_station: dict[int, list[dict[str, Any]]] = defaultdict(list)
        for r in rows:
            by_station[int(r.get("police_station_id") or 0)].append(r)
        for sid, group in by_station.items():
            arrests = sum(int(r.get("arrest_count") or 0) for r in group)
            if arrests >= 8:
                items.append(
                    AnomalyItem(
                        anomaly_id=f"arrest-cluster:station:{sid}",
                        kind="arrest_cluster",
                        severity="medium",
                        title=f"Arrest cluster at station {sid}",
                        detail=f"{arrests} arrests across {len(group)} cases",
                        police_station_id=sid,
                        case_master_ids=[
                            int(r["case_master_id"])
                            for r in group[:10]
                            if r.get("case_master_id") is not None
                        ],
                        score=float(arrests),
                    )
                )

        items.sort(key=lambda a: a.score, reverse=True)
        trimmed = items[:limit]
        return AnomaliesResponse(
            items=trimmed,
            provider="catalyst_heuristic",
            total=len(trimmed),
        )

    @staticmethod
    def _score_scope(
        scope: str, scope_id: int, group: list[dict[str, Any]]
    ) -> RiskScoreItem:
        if not group:
            return RiskScoreItem(
                scope=scope,
                scope_id=scope_id,
                risk_score=0.0,
                case_count=0,
                high_severity_share=0.0,
            )
        scores = [float(r.get("risk_score") or 0) for r in group]
        avg = sum(scores) / len(scores)
        high = sum(1 for r in group if str(r.get("severity") or "").lower() == "high")
        heads: dict[str, int] = defaultdict(int)
        for r in group:
            h = str(r.get("crime_major_head") or "unknown")
            heads[h] += 1
        top = [
            k for k, _ in sorted(heads.items(), key=lambda kv: kv[1], reverse=True)[:3]
        ]
        # blend average risk with volume pressure
        volume_boost = min(15.0, len(group) * 0.4)
        return RiskScoreItem(
            scope=scope,
            scope_id=scope_id,
            scope_name=None,
            risk_score=round(min(100.0, avg + volume_boost), 2),
            case_count=len(group),
            high_severity_share=round(high / len(group), 3),
            top_crime_heads=top,
        )
