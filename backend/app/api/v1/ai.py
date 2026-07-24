"""B4 AI HTTP routes — QuickML RAG, Graph RAG, risk, anomalies."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.ai.chat.service import ChatService
from app.ai.graph.service import GraphService
from app.ai.prediction.service import PredictionService
from app.exceptions.base import ValidationError
from app.repositories.case.case_store import CaseStore
from app.repositories.case.factory import get_case_store
from app.schemas.ai.anomalies import AnomaliesResponse
from app.schemas.ai.chat import ChatRequest, ChatResponse
from app.schemas.ai.graph import GraphRagContext
from app.schemas.ai.prediction import RiskPredictRequest, RiskPredictResponse

router = APIRouter(prefix="/ai", tags=["ai"])


def _chat_service(
    store: Annotated[CaseStore, Depends(get_case_store)],
) -> ChatService:
    return ChatService(store)


def _graph_service(
    store: Annotated[CaseStore, Depends(get_case_store)],
) -> GraphService:
    return GraphService(store)


def _prediction_service() -> PredictionService:
    return PredictionService()


@router.post("/chat", response_model=ChatResponse)
def ai_chat(
    payload: ChatRequest,
    service: Annotated[ChatService, Depends(_chat_service)],
) -> ChatResponse:
    """Ask AI over FIR corpus; optional NetworkX Graph RAG on AppSail."""
    return service.run(payload)


@router.get("/graph/context", response_model=GraphRagContext)
def ai_graph_context(
    service: Annotated[GraphService, Depends(_graph_service)],
    case_id: int | None = None,
    accused_id: int | None = None,
    depth: Annotated[int, Query(ge=1, le=3)] = 2,
) -> GraphRagContext:
    """NetworkX ego-graph summary for a case or accused (Graph RAG input)."""
    if (case_id is None) == (accused_id is None):
        raise ValidationError("Provide exactly one of case_id or accused_id")
    return service.context(case_id=case_id, accused_id=accused_id, depth=depth)


@router.post("/predict/risk", response_model=RiskPredictResponse)
def ai_predict_risk(
    payload: RiskPredictRequest,
    service: Annotated[PredictionService, Depends(_prediction_service)],
) -> RiskPredictResponse:
    """District/station risk scores (heuristic now; Zia AutoML later)."""
    return service.predict_risk(payload)


@router.get("/anomalies", response_model=AnomaliesResponse)
def ai_anomalies(
    service: Annotated[PredictionService, Depends(_prediction_service)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> AnomaliesResponse:
    """Recent anomaly call-outs (high risk, volume spikes, arrest clusters)."""
    return service.list_anomalies(limit=limit)
