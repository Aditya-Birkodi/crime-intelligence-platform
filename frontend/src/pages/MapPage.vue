<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { RouterLink, useRoute } from "vue-router";
import { api } from "@/services/api";
import IncidentMap from "@/components/IncidentMap.vue";
import type {
  DistrictGeoSummary,
  HotspotsResponse,
  IdName,
  IncidentPoint,
  SocioDistrict,
  TrendAlert,
} from "@/types";

const route = useRoute();
const loading = ref(true);
const error = ref<string | null>(null);

const districts = ref<DistrictGeoSummary[]>([]);
const incidents = ref<IncidentPoint[]>([]);
const hotspots = ref<HotspotsResponse | null>(null);
const trendAlerts = ref<TrendAlert[]>([]);
const socioDistricts = ref<SocioDistrict[]>([]);
const socioInsight = ref("");
const statuses = ref<IdName[]>([]);
const crimeHeads = ref<IdName[]>([]);

const showDistricts = ref(true);
const showIncidents = ref(true);
const showHotspots = ref(true);
const showTrendAlerts = ref(true);
const showSocio = ref(false);

const filterDistrict = ref("");
const filterStatus = ref("");
const filterHead = ref("");
const selected = ref<IncidentPoint | null>(null);

const districtOptions = computed(() =>
  districts.value.map((d) => ({ id: d.district_id, name: d.district_name })),
);

const redZoneCount = computed(
  () => trendAlerts.value.filter((a) => a.is_alert).length,
);

function toOptionalInt(value: string): number | undefined {
  if (!value) return undefined;
  const n = Number(value);
  return Number.isFinite(n) ? n : undefined;
}

async function load() {
  loading.value = true;
  error.value = null;
  try {
    const districtFromQuery = route.query.district_id;
    if (
      typeof districtFromQuery === "string" &&
      districtFromQuery &&
      !filterDistrict.value
    ) {
      filterDistrict.value = districtFromQuery;
    }

    const [geo, statusList, heads, inc, hs, trends, socio] = await Promise.all([
      api.getGeoDistricts(),
      api.listCaseStatuses().catch(() => [] as IdName[]),
      api.listCrimeHeads().catch(() => [] as IdName[]),
      api.getGeoIncidents({
        district_id: toOptionalInt(filterDistrict.value),
        case_status_id: toOptionalInt(filterStatus.value),
        crime_major_head_id: toOptionalInt(filterHead.value),
        limit: 500,
      }),
      api.getHotspots({
        cell_size_degrees: 0.08,
        grain: "day",
        district_id: toOptionalInt(filterDistrict.value),
      }),
      api.getTrendAlerts().catch(() => null),
      api.getSocioEconomicOverlay().catch(() => null),
    ]);
    districts.value = geo;
    statuses.value = statusList;
    crimeHeads.value = heads;
    incidents.value = inc.items;
    hotspots.value = hs;
    trendAlerts.value = trends?.alerts ?? [];
    socioDistricts.value = socio?.districts ?? [];
    socioInsight.value = socio?.insight ?? "";

    const focusId = Number(route.query.case_id);
    if (Number.isFinite(focusId) && focusId > 0) {
      selected.value =
        inc.items.find((p) => p.case_master_id === focusId) ?? null;
    }
  } catch (e) {
    error.value = e instanceof Error ? e.message : "Failed to load map data";
  } finally {
    loading.value = false;
  }
}

onMounted(load);
watch([filterDistrict, filterStatus, filterHead], load);

function onSelect(p: IncidentPoint) {
  selected.value = p;
}

function focusAlert(a: TrendAlert) {
  filterDistrict.value = String(a.district_id);
  showTrendAlerts.value = true;
}
</script>

<template>
  <section class="cip-rise space-y-7">
    <div class="flex flex-wrap items-end justify-between gap-4">
      <div>
        <p class="cip-kicker">Geospatial ops</p>
        <h1 class="cip-display mt-1 text-3xl text-[var(--cip-ink)]">Crime map</h1>
        <p class="mt-1 max-w-xl text-sm text-[var(--cip-muted)]">
          Live FIR pins, hotspot density, pulsing red-zone spikes, and socio-economic
          pressure overlays for SCRB desk briefings.
        </p>
      </div>
      <div class="flex flex-wrap gap-3 text-right text-sm text-[var(--cip-muted)]">
        <span class="cip-badge cip-badge-med">{{ incidents.length }} pins</span>
        <span class="cip-badge cip-badge-med">{{ hotspots?.bins.length ?? 0 }} cells</span>
        <span
          class="cip-badge"
          :class="redZoneCount ? 'cip-badge-high' : 'cip-badge-med'"
        >
          {{ redZoneCount }} red zones
        </span>
      </div>
    </div>

    <div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
      <label class="block text-sm">
        <span
          class="text-[0.7rem] font-semibold uppercase tracking-[0.12em] text-[var(--cip-muted)]"
          >District</span
        >
        <select v-model="filterDistrict" class="cip-field">
          <option value="">All</option>
          <option
            v-for="d in districtOptions"
            :key="d.id"
            :value="String(d.id)"
          >
            {{ d.name }}
          </option>
        </select>
      </label>
      <label class="block text-sm">
        <span
          class="text-[0.7rem] font-semibold uppercase tracking-[0.12em] text-[var(--cip-muted)]"
          >Status</span
        >
        <select v-model="filterStatus" class="cip-field">
          <option value="">All</option>
          <option v-for="s in statuses" :key="s.id" :value="String(s.id)">
            {{ s.name }}
          </option>
        </select>
      </label>
      <label class="block text-sm">
        <span
          class="text-[0.7rem] font-semibold uppercase tracking-[0.12em] text-[var(--cip-muted)]"
          >Crime head</span
        >
        <select v-model="filterHead" class="cip-field">
          <option value="">All</option>
          <option v-for="h in crimeHeads" :key="h.id" :value="String(h.id)">
            {{ h.name }}
          </option>
        </select>
      </label>
      <div class="flex flex-wrap items-end gap-x-3 gap-y-2 pb-2 text-xs font-medium text-[var(--cip-ink-soft)]">
        <label class="inline-flex items-center gap-1.5">
          <input v-model="showDistricts" type="checkbox" /> Districts
        </label>
        <label class="inline-flex items-center gap-1.5">
          <input v-model="showHotspots" type="checkbox" /> Hotspots
        </label>
        <label class="inline-flex items-center gap-1.5">
          <input v-model="showIncidents" type="checkbox" /> Incidents
        </label>
        <label class="inline-flex items-center gap-1.5">
          <input v-model="showTrendAlerts" type="checkbox" /> Red zones
        </label>
        <label class="inline-flex items-center gap-1.5">
          <input v-model="showSocio" type="checkbox" /> Socio overlay
        </label>
      </div>
    </div>

    <p
      v-if="showSocio && socioInsight"
      class="cip-panel border-l-0 px-4 py-3 text-sm text-[var(--cip-ink-soft)]"
    >
      {{ socioInsight }}
    </p>

    <p v-if="error" class="text-sm text-[#9b2c1f]">{{ error }}</p>
    <p v-else-if="loading" class="text-sm text-[var(--cip-muted)]">
      Loading map layers…
    </p>

    <div class="grid gap-4 lg:grid-cols-[1fr_19rem]">
      <div class="cip-panel cip-panel-flush overflow-hidden" style="min-height: 480px">
        <IncidentMap
          :districts="districts"
          :incidents="incidents"
          :hotspots="hotspots"
          :trend-alerts="trendAlerts"
          :socio-districts="socioDistricts"
          :show-districts="showDistricts"
          :show-incidents="showIncidents"
          :show-hotspots="showHotspots"
          :show-trend-alerts="showTrendAlerts"
          :show-socio="showSocio"
          @select-incident="onSelect"
        />
      </div>

      <aside class="space-y-4">
        <div class="cip-panel p-4 pl-5">
          <h2 class="cip-display text-lg text-[var(--cip-ink)]">Selection</h2>
          <template v-if="selected">
            <p class="mt-3 font-mono text-xs text-[var(--cip-ink)]">
              {{ selected.crime_no }}
            </p>
            <p class="mt-1 text-sm text-[var(--cip-muted)]">
              Case {{ selected.case_no }}
            </p>
            <p class="mt-2 text-xs text-[var(--cip-muted)]">
              {{ selected.latitude }}, {{ selected.longitude }}
            </p>
            <RouterLink
              :to="`/cases/${selected.case_master_id}`"
              class="mt-4 inline-block text-sm font-semibold text-[var(--cip-accent-deep)] underline-offset-2 hover:underline"
            >
              Open case →
            </RouterLink>
          </template>
          <p v-else class="mt-3 text-sm text-[var(--cip-muted)]">
            Click an incident pin for details.
          </p>
        </div>

        <div class="cip-panel p-4 pl-5">
          <h3
            class="text-[0.65rem] font-semibold uppercase tracking-[0.14em] text-[var(--cip-muted)]"
          >
            Pulsing red zones
          </h3>
          <ul class="mt-2 max-h-44 space-y-2 overflow-y-auto text-sm">
            <li
              v-for="a in trendAlerts.filter((x) => x.is_alert).slice(0, 10)"
              :key="`${a.district_id}-${a.crime_major_head_id}`"
            >
              <button
                type="button"
                class="w-full text-left"
                @click="focusAlert(a)"
              >
                <span class="font-semibold text-[var(--cip-ink)]">{{
                  a.district_name
                }}</span>
                <span class="mt-0.5 block text-xs text-[var(--cip-muted)]">
                  {{ a.crime_head_name }} · {{ a.spike_ratio }}× spike
                </span>
              </button>
            </li>
            <li
              v-if="!trendAlerts.some((a) => a.is_alert)"
              class="text-sm text-[var(--cip-muted)]"
            >
              No active spikes
            </li>
          </ul>
        </div>

        <div class="cip-panel p-4 pl-5">
          <h3
            class="text-[0.65rem] font-semibold uppercase tracking-[0.14em] text-[var(--cip-muted)]"
          >
            Top districts
          </h3>
          <ul class="mt-2 max-h-52 space-y-1.5 overflow-y-auto text-sm">
            <li
              v-for="d in districts
                .slice()
                .sort((a, b) => b.case_count - a.case_count)
                .slice(0, 12)"
              :key="d.district_id"
              class="flex justify-between gap-2"
            >
              <button
                type="button"
                class="truncate text-left text-[var(--cip-ink-soft)] hover:underline"
                @click="filterDistrict = String(d.district_id)"
              >
                {{ d.district_name }}
              </button>
              <span class="tabular-nums text-[var(--cip-muted)]">{{
                d.case_count
              }}</span>
            </li>
          </ul>
        </div>
      </aside>
    </div>
  </section>
</template>
