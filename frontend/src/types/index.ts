/** Types aligned with backend B1 OpenAPI schemas. */

export type HealthResponse = {
  status: string;
  service: string;
};

export type ApiStatusResponse = {
  api: string;
  status: string;
};

export type IdName = {
  id: number;
  name: string;
};

export type Victim = {
  victim_master_id: number;
  case_master_id: number;
  victim_name: string;
  age_year: number | null;
  gender_id: string | null;
  victim_police: string | null;
};

export type Accused = {
  accused_master_id: number;
  case_master_id: number;
  accused_name: string;
  age_year: number | null;
  gender_id: string | null;
  person_id: string | null;
};

export type ActSection = {
  id: number;
  case_master_id: number;
  act_id: string;
  section_id: string;
  act_order_id: number;
  section_order_id: number;
};

export type CaseMaster = {
  case_master_id: number;
  crime_no: string;
  case_no: string;
  crime_registered_date: string | null;
  police_station_id: number;
  case_category_id: number;
  gravity_offence_id: number | null;
  crime_major_head_id: number | null;
  crime_minor_head_id: number | null;
  case_status_id: number;
  court_id: number | null;
  incident_from_date: string | null;
  incident_to_date: string | null;
  info_received_ps_date: string | null;
  latitude: string | number | null;
  longitude: string | number | null;
  brief_facts: string | null;
};

export type CaseMasterDetail = CaseMaster & {
  victims: Victim[];
  accused: Accused[];
  act_sections: ActSection[];
};

export type CaseMasterListResponse = {
  items: CaseMaster[];
  total: number;
  limit: number;
  offset: number;
};

export type CaseListParams = {
  police_station_id?: number;
  case_status_id?: number;
  crime_major_head_id?: number;
  registered_from?: string;
  registered_to?: string;
  limit?: number;
  offset?: number;
};

export type AnalyticsOverview = {
  total_cases: number;
  cases_with_coordinates: number;
  by_status: { case_status_id: number; name: string; count: number }[];
  by_crime_head: {
    crime_major_head_id: number | null;
    name: string;
    count: number;
  }[];
  districts_covered: number;
  stations_covered: number;
};

export type DistrictGeoSummary = {
  district_id: number;
  district_name: string;
  case_count: number;
  avg_latitude: string | number | null;
  avg_longitude: string | number | null;
};

export type IncidentPoint = {
  case_master_id: number;
  crime_no: string;
  case_no: string;
  police_station_id: number;
  district_id: number | null;
  case_status_id: number;
  crime_major_head_id: number | null;
  latitude: string | number;
  longitude: string | number;
  incident_from_date: string | null;
  crime_registered_date: string | null;
};

export type HotspotsResponse = {
  grain: string;
  cell_size_degrees: number;
  bins: {
    lat_bin: number;
    lon_bin: number;
    hour_of_day: number | null;
    case_count: number;
    sample_case_ids: number[];
  }[];
};

export type TrendAlertsResponse = {
  recent_days: number;
  baseline_days: number;
  threshold: number;
  alerts: {
    district_id: number;
    district_name: string;
    crime_major_head_id: number | null;
    crime_head_name: string;
    recent_count: number;
    baseline_avg: number;
    spike_ratio: number;
    is_alert: boolean;
  }[];
};

export type GraphNode = {
  id: string;
  type: "case" | "accused" | "victim" | "station";
  label: string;
  meta: Record<string, unknown>;
};

export type GraphEdge = {
  id: string;
  source: string;
  target: string;
  relation: string;
  score: number;
};

export type NetworkGraphResponse = {
  seed: string;
  nodes: GraphNode[];
  edges: GraphEdge[];
};

export type OffenderProfile = {
  accused_master_id: number;
  accused_name: string;
  person_id: string | null;
  age_year: number | null;
  gender_id: string | null;
  case_count: number;
  cases: {
    case_master_id: number;
    crime_no: string;
    case_no: string;
    brief_facts: string | null;
    crime_registered_date: string | null;
    police_station_id: number;
    crime_major_head_id: number | null;
    accused_master_id: number;
  }[];
  modus_operandi: string[];
  linked_accused_ids: number[];
};
