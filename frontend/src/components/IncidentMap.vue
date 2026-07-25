<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from "vue";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import type {
  DistrictGeoSummary,
  HotspotsResponse,
  IncidentPoint,
  SocioDistrict,
  TrendAlert,
} from "@/types";

const props = withDefaults(
  defineProps<{
    districts: DistrictGeoSummary[];
    incidents: IncidentPoint[];
    hotspots: HotspotsResponse | null;
    trendAlerts?: TrendAlert[];
    socioDistricts?: SocioDistrict[];
    showDistricts?: boolean;
    showIncidents?: boolean;
    showHotspots?: boolean;
    showTrendAlerts?: boolean;
    showSocio?: boolean;
  }>(),
  {
    trendAlerts: () => [],
    socioDistricts: () => [],
    showDistricts: true,
    showIncidents: true,
    showHotspots: true,
    showTrendAlerts: true,
    showSocio: false,
  },
);

const emit = defineEmits<{
  selectIncident: [point: IncidentPoint];
}>();

const mapEl = ref<HTMLElement | null>(null);
let map: L.Map | null = null;
let districtLayer: L.LayerGroup | null = null;
let incidentLayer: L.LayerGroup | null = null;
let hotspotLayer: L.LayerGroup | null = null;
let alertLayer: L.LayerGroup | null = null;
let socioLayer: L.LayerGroup | null = null;
let pulseTimer: number | null = null;
const pulseMarkers: L.CircleMarker[] = [];

const KAR_CENTER: L.LatLngExpression = [14.5, 76.5];

function toNum(v: string | number | null | undefined): number | null {
  if (v == null || v === "") return null;
  const n = typeof v === "number" ? v : Number(v);
  return Number.isFinite(n) ? n : null;
}

function clearLayers() {
  districtLayer?.clearLayers();
  incidentLayer?.clearLayers();
  hotspotLayer?.clearLayers();
  alertLayer?.clearLayers();
  socioLayer?.clearLayers();
  pulseMarkers.length = 0;
}

function startPulse() {
  if (pulseTimer != null) window.clearInterval(pulseTimer);
  let growing = true;
  pulseTimer = window.setInterval(() => {
    for (const m of pulseMarkers) {
      const r = m.getRadius();
      m.setRadius(Math.max(10, Math.min(28, growing ? r + 1.2 : r - 1.2)));
    }
    growing = !growing;
  }, 450);
}

function render() {
  if (
    !map ||
    !districtLayer ||
    !incidentLayer ||
    !hotspotLayer ||
    !alertLayer ||
    !socioLayer
  ) {
    return;
  }
  clearLayers();
  const bounds: L.LatLngExpression[] = [];

  if (props.showSocio && props.socioDistricts.length) {
    const maxNorm = Math.max(
      1,
      ...props.socioDistricts.map((d) => d.crime_per_10k_density),
    );
    for (const d of props.socioDistricts) {
      const lat = toNum(d.avg_latitude);
      const lon = toNum(d.avg_longitude);
      if (lat == null || lon == null) continue;
      const intensity = d.crime_per_10k_density / maxNorm;
      socioLayer.addLayer(
        L.circleMarker([lat, lon], {
          radius: 10 + intensity * 18,
          color: "#0f766e",
          weight: 1,
          fillColor: d.is_urban_core ? "#0d9488" : "#5eead4",
          fillOpacity: 0.15 + intensity * 0.35,
        }).bindPopup(
          `<strong>${d.district_name}</strong><br/>${d.case_count} FIRs<br/>` +
            `Urban ${d.urbanization_pct}% · Density ${d.population_density_per_km2}<br/>` +
            `Unemployment ${d.youth_unemployment_pct}%<br/><em>${d.correlation_note}</em>`,
        ),
      );
      bounds.push([lat, lon]);
    }
  }

  if (props.showDistricts) {
    for (const d of props.districts) {
      const lat = toNum(d.avg_latitude);
      const lon = toNum(d.avg_longitude);
      if (lat == null || lon == null) continue;
      districtLayer.addLayer(
        L.circleMarker([lat, lon], {
          radius: Math.min(28, 8 + Math.sqrt(d.case_count) * 3),
          color: "#0f4c5c",
          weight: 1.5,
          fillColor: "#0f4c5c",
          fillOpacity: 0.18,
        }).bindPopup(
          `<strong>${d.district_name}</strong><br/>${d.case_count} cases`,
        ),
      );
      bounds.push([lat, lon]);
    }
  }

  if (props.showHotspots && props.hotspots) {
    const cell = props.hotspots.cell_size_degrees || 0.05;
    const maxCount = Math.max(
      1,
      ...props.hotspots.bins.map((b) => b.case_count),
    );
    for (const bin of props.hotspots.bins) {
      hotspotLayer.addLayer(
        L.rectangle(
          [
            [bin.lat_bin, bin.lon_bin],
            [bin.lat_bin + cell, bin.lon_bin + cell],
          ],
          {
            color: "#b45309",
            weight: 0,
            fillColor: "#f59e0b",
            fillOpacity: 0.2 + (bin.case_count / maxCount) * 0.55,
          },
        ).bindPopup(
          `Hotspot · ${bin.case_count} cases` +
            (bin.hour_of_day != null ? `<br/>Hour ${bin.hour_of_day}:00` : ""),
        ),
      );
      bounds.push([bin.lat_bin + cell / 2, bin.lon_bin + cell / 2]);
    }
  }

  if (props.showTrendAlerts) {
    for (const a of props.trendAlerts) {
      if (!a.is_alert) continue;
      const lat = toNum(a.avg_latitude);
      const lon = toNum(a.avg_longitude);
      if (lat == null || lon == null) continue;
      const marker = L.circleMarker([lat, lon], {
        radius: 12 + Math.min(16, a.spike_ratio * 3),
        color: "#991b1b",
        weight: 2,
        fillColor: "#ef4444",
        fillOpacity: 0.35,
      }).bindPopup(
        `<strong>RED ZONE</strong><br/>${a.district_name}<br/>${a.crime_head_name}<br/>` +
          `${a.spike_ratio}× spike · ${a.recent_count} recent`,
      );
      alertLayer.addLayer(marker);
      pulseMarkers.push(marker);
      bounds.push([lat, lon]);
    }
  }

  if (props.showIncidents) {
    for (const p of props.incidents) {
      const lat = toNum(p.latitude);
      const lon = toNum(p.longitude);
      if (lat == null || lon == null) continue;
      incidentLayer.addLayer(
        L.circleMarker([lat, lon], {
          radius: 5,
          color: "#0f172a",
          weight: 1,
          fillColor: "#dc2626",
          fillOpacity: 0.85,
        })
          .bindPopup(
            `<strong>${p.crime_no}</strong><br/>Case ${p.case_no}<br/><a href="/cases/${p.case_master_id}">Open case</a>`,
          )
          .on("click", () => emit("selectIncident", p)),
      );
      bounds.push([lat, lon]);
    }
  }

  if (bounds.length) {
    map.fitBounds(L.latLngBounds(bounds), { padding: [40, 40], maxZoom: 11 });
  } else {
    map.setView(KAR_CENTER, 7);
  }
}

onMounted(() => {
  if (!mapEl.value) return;
  map = L.map(mapEl.value, { zoomControl: true }).setView(KAR_CENTER, 7);
  L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> &copy; CARTO',
    maxZoom: 18,
  }).addTo(map);
  socioLayer = L.layerGroup().addTo(map);
  districtLayer = L.layerGroup().addTo(map);
  hotspotLayer = L.layerGroup().addTo(map);
  alertLayer = L.layerGroup().addTo(map);
  incidentLayer = L.layerGroup().addTo(map);
  render();
  startPulse();
});

onBeforeUnmount(() => {
  if (pulseTimer != null) window.clearInterval(pulseTimer);
  map?.remove();
  map = null;
});

watch(
  () => [
    props.districts,
    props.incidents,
    props.hotspots,
    props.trendAlerts,
    props.socioDistricts,
    props.showDistricts,
    props.showIncidents,
    props.showHotspots,
    props.showTrendAlerts,
    props.showSocio,
  ],
  () => render(),
  { deep: true },
);
</script>

<template>
  <div ref="mapEl" class="map-root" />
</template>

<style scoped>
.map-root {
  width: 100%;
  height: 100%;
  min-height: 420px;
  border-radius: 12px;
  overflow: hidden;
  background: #e8eef2;
}
</style>
