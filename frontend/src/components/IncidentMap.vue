<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from "vue";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import type { DistrictGeoSummary, HotspotsResponse, IncidentPoint } from "@/types";

const props = defineProps<{
  districts: DistrictGeoSummary[];
  incidents: IncidentPoint[];
  hotspots: HotspotsResponse | null;
  showDistricts: boolean;
  showIncidents: boolean;
  showHotspots: boolean;
}>();

const emit = defineEmits<{
  selectIncident: [point: IncidentPoint];
}>();

const mapEl = ref<HTMLElement | null>(null);
let map: L.Map | null = null;
let districtLayer: L.LayerGroup | null = null;
let incidentLayer: L.LayerGroup | null = null;
let hotspotLayer: L.LayerGroup | null = null;

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
}

function render() {
  if (!map || !districtLayer || !incidentLayer || !hotspotLayer) return;
  clearLayers();

  const bounds: L.LatLngExpression[] = [];

  if (props.showDistricts) {
    for (const d of props.districts) {
      const lat = toNum(d.avg_latitude);
      const lon = toNum(d.avg_longitude);
      if (lat == null || lon == null) continue;
      const r = Math.min(28, 8 + Math.sqrt(d.case_count) * 3);
      const circle = L.circleMarker([lat, lon], {
        radius: r,
        color: "#0f4c5c",
        weight: 1.5,
        fillColor: "#0f4c5c",
        fillOpacity: 0.18,
      }).bindPopup(
        `<strong>${d.district_name}</strong><br/>${d.case_count} cases`,
      );
      districtLayer.addLayer(circle);
      bounds.push([lat, lon]);
    }
  }

  if (props.showHotspots && props.hotspots) {
    const cell = props.hotspots.cell_size_degrees || 0.05;
    const maxCount = Math.max(1, ...props.hotspots.bins.map((b) => b.case_count));
    for (const bin of props.hotspots.bins) {
      const lat = bin.lat_bin + cell / 2;
      const lon = bin.lon_bin + cell / 2;
      const opacity = 0.2 + (bin.case_count / maxCount) * 0.55;
      const rect = L.rectangle(
        [
          [bin.lat_bin, bin.lon_bin],
          [bin.lat_bin + cell, bin.lon_bin + cell],
        ],
        {
          color: "#b45309",
          weight: 0,
          fillColor: "#f59e0b",
          fillOpacity: opacity,
        },
      ).bindPopup(`Hotspot · ${bin.case_count} cases`);
      hotspotLayer.addLayer(rect);
      bounds.push([lat, lon]);
    }
  }

  if (props.showIncidents) {
    for (const p of props.incidents) {
      const lat = toNum(p.latitude);
      const lon = toNum(p.longitude);
      if (lat == null || lon == null) continue;
      const marker = L.circleMarker([lat, lon], {
        radius: 5,
        color: "#0f172a",
        weight: 1,
        fillColor: "#dc2626",
        fillOpacity: 0.85,
      })
        .bindPopup(
          `<strong>${p.crime_no}</strong><br/>Case ${p.case_no}<br/><a href="/cases/${p.case_master_id}">Open case</a>`,
        )
        .on("click", () => emit("selectIncident", p));
      incidentLayer.addLayer(marker);
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
  map = L.map(mapEl.value, { scrollWheelZoom: true }).setView(KAR_CENTER, 7);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap",
    maxZoom: 18,
  }).addTo(map);

  districtLayer = L.layerGroup().addTo(map);
  hotspotLayer = L.layerGroup().addTo(map);
  incidentLayer = L.layerGroup().addTo(map);
  render();
  setTimeout(() => map?.invalidateSize(), 80);
});

watch(
  () => [
    props.districts,
    props.incidents,
    props.hotspots,
    props.showDistricts,
    props.showIncidents,
    props.showHotspots,
  ],
  () => render(),
  { deep: true },
);

onBeforeUnmount(() => {
  map?.remove();
  map = null;
});
</script>

<template>
  <div
    ref="mapEl"
    class="h-[28rem] w-full overflow-hidden border border-[var(--cip-line)] bg-[#d9e4e2] md:h-[32rem]"
    style="border-radius: 2px"
  />
</template>

<style scoped>
:deep(.leaflet-container) {
  font-family: inherit;
  z-index: 0;
}
</style>
