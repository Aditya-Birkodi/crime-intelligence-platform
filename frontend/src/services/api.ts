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
  FaceAnalyseResponse,
  FaceCompareResponse,
  HealthResponse,
  HotspotsResponse,
  IdName,
  IncidentPoint,
  IntelligenceBriefResponse,
  MediaAttachment,
  MoClustersResponse,
  NetworkGraphResponse,
  OffenderProfile,
  SearchResponse,
  SocioEconomicOverlayResponse,
  TrendAlertsResponse,
} from "@/types";

export const baseUrl = (
  import.meta.env.VITE_CATALYST_API_GATEWAY_URL ||
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000"
).replace(/\/$/, "");

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const url = `${baseUrl}${path}`;
  let response: Response;
  try {
    // Use text/plain for JSON bodies so browsers skip CORS preflight.
    // AppSail's edge returns OPTIONS without Access-Control-* headers, which
    // breaks application/json POSTs from Slate (Failed to fetch).
    response = await fetch(url, {
      ...init,
      headers: {
        Accept: "application/json",
        ...(init?.body ? { "Content-Type": "text/plain;charset=UTF-8" } : {}),
        ...init?.headers,
      },
    });
  } catch (err) {
    const detail = err instanceof Error ? err.message : String(err);
    throw new Error(
      `Network error calling ${url} (${detail}). ` +
        "If this is a CORS/preflight failure from Slate→AppSail, redeploy both " +
        "and whitelist the Slate domain under Catalyst Authentication → Whitelisting (CORS).",
    );
  }
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
    request<CaseMasterDetail>(
      `/api/v1/cases/by-crime-no/${encodeURIComponent(crimeNo)}`,
    ),
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
  getSocioEconomicOverlay: () =>
    request<SocioEconomicOverlayResponse>(
      "/api/v1/analytics/socio-economic",
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
  aiMoClusters: (params: { min_size?: number; limit?: number } = {}) =>
    request<MoClustersResponse>(
      `/api/v1/ai/mo-clusters${toQuery(params)}`,
    ),
  aiIntelligenceBrief: (params: { horizon_days?: number } = {}) =>
    request<IntelligenceBriefResponse>(
      `/api/v1/ai/intelligence-brief${toQuery(params)}`,
    ),

  // Search + media + Zia
  search: (params: { q: string; types?: string; limit?: number }) =>
    request<SearchResponse>(
      `/api/v1/search${toQuery(params as Record<string, string | number | undefined>)}`,
    ),
  listMedia: (params: {
    case_master_id?: number;
    entity_type?: string;
    entity_id?: number;
    limit?: number;
  } = {}) =>
    request<{ items: MediaAttachment[]; total: number }>(
      `/api/v1/media${toQuery(params as Record<string, string | number | undefined>)}`,
    ),
  mediaContentUrl: (mediaId: string) => `${baseUrl}/api/v1/media/${mediaId}/content`,
  uploadMediaJson: (body: {
    image_base64: string;
    filename?: string;
    content_type?: string;
    entity_type?: string;
    entity_id?: number;
    case_master_id?: number;
    label?: string;
    analyse_face?: boolean;
    face_mode?: string;
  }) =>
    request<{
      attachment: MediaAttachment;
      face_analysis: Record<string, unknown> | null;
      provider: string;
    }>("/api/v1/media/upload-json", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  analyseFaceJson: (body: {
    image_base64: string;
    filename?: string;
    mode?: string;
    age?: boolean;
    emotion?: boolean;
    gender?: boolean;
    persist?: boolean;
    case_master_id?: number;
    entity_type?: string;
    entity_id?: number;
  }) =>
    request<FaceAnalyseResponse>("/api/v1/media/zia/analyse-face-json", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  compareFaceJson: (body: {
    source_base64: string;
    query_base64: string;
    source_filename?: string;
    query_filename?: string;
  }) =>
    request<FaceCompareResponse>("/api/v1/media/zia/compare-face-json", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  detectObjectsJson: (body: { image_base64: string; filename?: string }) =>
    request<Record<string, unknown>>("/api/v1/media/zia/detect-objects-json", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  ocrJson: (body: { image_base64: string; filename?: string }) =>
    request<Record<string, unknown>>("/api/v1/media/zia/ocr-json", {
      method: "POST",
      body: JSON.stringify(body),
    }),
};

export async function fileToBase64(file: File): Promise<string> {
  const buf = await file.arrayBuffer();
  const bytes = new Uint8Array(buf);
  let binary = "";
  for (let i = 0; i < bytes.length; i++) binary += String.fromCharCode(bytes[i]!);
  return btoa(binary);
}
