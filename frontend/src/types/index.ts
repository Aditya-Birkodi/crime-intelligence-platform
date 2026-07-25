/** Types aligned with backend B1 OpenAPI schemas. */

export type HealthResponse = {
  status: string;
  service: string;
};

export type ApiStatusResponse = {
  api: string;
  status: string;
  persistence?: string;
  datastore_mock?: string;
  cases_source?: string;
  lookups_source?: string;
  analytics_source?: string;
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

export type Complainant = {
  complainant_id: number;
  case_master_id: number;
  complainant_name: string;
  age_year: number | null;
  gender_id: string | null;
  occupation_id: number | null;
  religion_id: number | null;
  caste_id: number | null;
};

export type Occurrence = {
  case_master_id: number;
  occurrence_from: string | null;
  occurrence_to: string | null;
  place_of_occurrence: string | null;
  beat_number: string | null;
  distance_from_ps_km: string | number | null;
  direction_from_ps: string | null;
  village_or_city: string | null;
};

export type Arrest = {
  arrest_surrender_id: number;
  case_master_id: number;
  arrest_surrender_type_id: number;
  arrest_surrender_date: string | null;
  arrest_surrender_state_id: number | null;
  arrest_surrender_district_id: number | null;
  police_station_id: number | null;
  io_id: number | null;
  court_id: number | null;
  accused_master_id: number | null;
  is_accused: boolean;
  is_complainant_accused: boolean;
};

export type Chargesheet = {
  cs_id: number;
  case_master_id: number;
  cs_date: string | null;
  cs_type: string;
  police_person_id: number | null;
};

export type CaseMaster = {
  case_master_id: number;
  crime_no: string;
  case_no: string;
  crime_registered_date: string | null;
  police_person_id: number | null;
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
  complainants: Complainant[];
  act_sections: ActSection[];
  occurrence: Occurrence | null;
  arrests: Arrest[];
  chargesheets: Chargesheet[];
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
  crime_no?: string;
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

export type TrendAlert = {
  district_id: number;
  district_name: string;
  crime_major_head_id: number | null;
  crime_head_name: string;
  recent_count: number;
  baseline_avg: number;
  spike_ratio: number;
  is_alert: boolean;
  avg_latitude: string | number | null;
  avg_longitude: string | number | null;
};

export type TrendAlertsResponse = {
  recent_days: number;
  baseline_days: number;
  threshold: number;
  alerts: TrendAlert[];
};

export type SocioDistrict = {
  district_id: number;
  district_name: string;
  case_count: number;
  avg_latitude: string | number | null;
  avg_longitude: string | number | null;
  population_density_per_km2: number;
  urbanization_pct: number;
  literacy_pct: number;
  youth_unemployment_pct: number;
  per_capita_income_index: number;
  is_urban_core: boolean;
  crime_per_10k_density: number;
  correlation_note: string;
};

export type SocioEconomicOverlayResponse = {
  districts: SocioDistrict[];
  insight: string;
  provider: string;
};

export type MoClusterMember = {
  case_master_id: number;
  crime_no: string;
  brief_facts: string | null;
  police_station_id: number | null;
  district_id: number | null;
  crime_major_head_id: number | null;
};

export type MoCluster = {
  cluster_id: string;
  label: string;
  mo_signature: string;
  size: number;
  districts: string[];
  act_sections: string[];
  members: MoClusterMember[];
  similarity_note: string;
};

export type MoClustersResponse = {
  clusters: MoCluster[];
  provider: string;
  total_cases_clustered: number;
};

export type IntelligenceBriefSection = {
  title: string;
  body: string;
};

export type IntelligenceBriefResponse = {
  title: string;
  generated_at: string;
  horizon_days: number;
  headline: string;
  sections: IntelligenceBriefSection[];
  recommended_actions: string[];
  provider: string;
};

export type SearchHit = {
  entity_type: "accused" | "victim" | "complainant" | "case" | string;
  entity_id: number;
  name: string;
  case_master_id: number | null;
  crime_no: string | null;
  person_id: string | null;
  match_field: string;
  score: number;
};

export type SearchResponse = {
  query: string;
  total: number;
  items: SearchHit[];
  provider: string;
};

export type MediaAttachment = {
  media_id: string;
  entity_type: string;
  entity_id: number | null;
  case_master_id: number | null;
  filename: string;
  content_type: string;
  uri: string;
  size_bytes: number;
  label: string | null;
  zia_face: Record<string, unknown> | null;
  created_at: string;
};

export type FaceAnalyseResponse = {
  result: Record<string, unknown>;
  provider: string;
  media_id: string | null;
};

export type FaceCompareResponse = {
  result: Record<string, unknown>;
  provider: string;
  matched: boolean | null;
  confidence: number | null;
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
