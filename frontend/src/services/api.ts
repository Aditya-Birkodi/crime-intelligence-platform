/**
 * HTTP client for CIP backend.
 * Set VITE_API_BASE_URL to your ngrok HTTPS URL (no trailing slash).
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
};
