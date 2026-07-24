/**
 * HTTP client for CIP backend.
 * Set VITE_API_BASE_URL (no trailing slash) — AppSail URL in production.
 */

import type {
  AnalyticsOverview,
  ApiStatusResponse,
  CaseListParams,
  CaseMasterDetail,
  CaseMasterListResponse,
  DistrictGeoSummary,
  HealthResponse,
  HotspotsResponse,
  IdName,
  IncidentPoint,
  NetworkGraphResponse,
  OffenderProfile,
  TrendAlertsResponse,
} from "@/types";

export const baseUrl = (
  import.meta.env.VITE_CATALYST_API_GATEWAY_URL ||
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000"
).replace(/\/$/, "");

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${baseUrl}${path}`, {
    ...init,
    headers: {
      Accept: "application/json",
      ...(init?.body ? { "Content-Type": "application/json" } : {}),
      ...init?.headers,
    },
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`API ${response.status}: ${text || response.statusText}`);
  }
  return response.json() as Promise<T>;
}

function toQuery(params: Record<string, string | number | undefined>): string {
  const q = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== "") {
      q.set(key, String(value));
    }
  }
  const s = q.toString();
  return s ? `?${s}` : "";
}

export const api = {
  getHealth: () => request<HealthResponse>("/health"),
  getStatus: () => request<ApiStatusResponse>("/api/v1/status"),
  listCases: (params: CaseListParams = {}) =>
    request<CaseMasterListResponse>(
      `/api/v1/cases${toQuery(params as Record<string, string | number | undefined>)}`,
    ),
  getCase: (id: number) => request<CaseMasterDetail>(`/api/v1/cases/${id}`),
  getCaseByCrimeNo: (crimeNo: string) =>
    request<CaseMasterDetail>(`/api/v1/cases/by-crime-no/${crimeNo}`),
  listCaseStatuses: () => request<IdName[]>("/api/v1/lookups/case-statuses"),
  listCaseCategories: () => request<IdName[]>("/api/v1/lookups/case-categories"),
  listDistricts: () => request<IdName[]>("/api/v1/lookups/districts"),
  listStations: (districtId?: number) =>
    request<IdName[]>(
      `/api/v1/lookups/stations${toQuery({ district_id: districtId })}`,
    ),
  listCrimeHeads: () => request<IdName[]>("/api/v1/lookups/crime-heads"),
  listGravityOffences: () =>
    request<IdName[]>("/api/v1/lookups/gravity-offences"),

  // B2 analytics
  getAnalyticsOverview: () =>
    request<AnalyticsOverview>("/api/v1/analytics/overview"),
  getGeoDistricts: () =>
    request<DistrictGeoSummary[]>("/api/v1/analytics/geo/districts"),
  getGeoIncidents: (
    params: {
      district_id?: number;
      police_station_id?: number;
      case_status_id?: number;
      crime_major_head_id?: number;
      registered_from?: string;
      registered_to?: string;
      limit?: number;
    } = {},
  ) =>
    request<{ items: IncidentPoint[]; total: number }>(
      `/api/v1/analytics/geo/incidents${toQuery(params)}`,
    ),
  getHotspots: (
    params: {
      cell_size_degrees?: number;
      grain?: "hour" | "day";
      district_id?: number;
      registered_from?: string;
      registered_to?: string;
    } = {},
  ) =>
    request<HotspotsResponse>(
      `/api/v1/analytics/hotspots${toQuery(params as Record<string, string | number | undefined>)}`,
    ),
  getTrendAlerts: (
    params: {
      recent_days?: number;
      baseline_days?: number;
      threshold?: number;
    } = {},
  ) =>
    request<TrendAlertsResponse>(
      `/api/v1/analytics/alerts/trends${toQuery(params)}`,
    ),

  // B3 network
  getNetworkGraph: (params: {
    case_id?: number;
    accused_id?: number;
    depth?: number;
  }) =>
    request<NetworkGraphResponse>(
      `/api/v1/network/graph${toQuery(params)}`,
    ),
  getOffenderProfile: (accusedId: number) =>
    request<OffenderProfile>(`/api/v1/network/offenders/${accusedId}`),

  // B4 AI
    aiChat: (body: {
    question: string;
    case_master_id?: number;
    accused_id?: number;
    use_graph_rag?: boolean;
    graph_depth?: number;
    top_k?: number;
  }) =>
    request<{
      answer: string;
      citations: {
        case_master_id: number | null;
        crime_no: string | null;
        doc_id: string | null;
        snippet: string | null;
      }[];
      provider: string;
      knowledge_base_id: string | null;
      graph_context: {
        seed: string;
        node_count: number;
        edge_count: number;
        neighbor_crime_nos: string[];
        summary: string;
        engine: string;
      } | null;
    }>("/api/v1/ai/chat", { method: "POST", body: JSON.stringify(body) }),
  aiGraphContext: (params: {
    case_id?: number;
    accused_id?: number;
    depth?: number;
  }) =>
    request<{
      seed: string;
      depth: number;
      node_count: number;
      edge_count: number;
      neighbor_crime_nos: string[];
      linked_persons: string[];
      summary: string;
      engine: string;
    }>(
      `/api/v1/ai/graph/context${toQuery(params as Record<string, string | number | undefined>)}`,
    ),
  aiPredictRisk: (body: {
    district_id?: number;
    police_station_id?: number;
    horizon_days?: number;
  } = {}) =>
    request<{
      horizon_days: number;
      items: {
        scope: string;
        scope_id: number;
        scope_name: string | null;
        risk_score: number;
        case_count: number;
        high_severity_share: number;
        top_crime_heads: string[];
      }[];
      provider: string;
      model: string | null;
    }>("/api/v1/ai/predict/risk", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  aiAnomalies: (limit = 20) =>
    request<{
      items: {
        anomaly_id: string;
        kind: string;
        severity: string;
        title: string;
        detail: string;
        district_id: number | null;
        police_station_id: number | null;
        case_master_ids: number[];
        score: number;
      }[];
      provider: string;
      total: number;
    }>(`/api/v1/ai/anomalies${toQuery({ limit })}`),
};
