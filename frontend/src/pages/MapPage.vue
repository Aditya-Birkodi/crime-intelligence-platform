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
} from "@/types";

const route = useRoute();
const loading = ref(true);
const error = ref<string | null>(null);

const districts = ref<DistrictGeoSummary[]>([]);
const incidents = ref<IncidentPoint[]>([]);
const hotspots = ref<HotspotsResponse | null>(null);
const statuses = ref<IdName[]>([]);
const crimeHeads = ref<IdName[]>([]);

const showDistricts = ref(true);
const showIncidents = ref(true);
const showHotspots = ref(true);

const filterDistrict = ref("");
const filterStatus = ref("");
const filterHead = ref("");
const selected = ref<IncidentPoint | null>(null);

const districtOptions = computed(() =>
  districts.value.map((d) => ({ id: d.district_id, name: d.district_name })),
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
    const [geo, statusList, heads, inc, hs] = await Promise.all([
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
    ]);
    districts.value = geo;
    statuses.value = statusList;
    crimeHeads.value = heads;
    incidents.value = inc.items;
    hotspots.value = hs;

    const focusId = Number(route.query.case_id);
    if (Number.isFinite(focusId) && focusId > 0) {
      selected.value = inc.items.find((p) => p.case_master_id === focusId) ?? null;
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
</script>

<template>
  <section class="cip-rise space-y-7">
    <div class="flex flex-wrap items-end justify-between gap-4">
      <div>
        <p class="cip-kicker">Geospatial</p>
        <h1 class="cip-display mt-1 text-3xl text-[var(--cip-ink)]">Crime map</h1>
        <p class="mt-1 text-sm text-[var(--cip-muted)]">
          District aggregates, incident pins, and hotspot bins from analytics geo APIs.
        </p>
      </div>
      <p class="text-sm text-[var(--cip-muted)]">
        {{ incidents.length }} incidents · {{ districts.length }} districts ·
        {{ hotspots?.bins.length ?? 0 }} hotspot cells
      </p>
    </div>

    <div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
      <label class="block text-sm">
        <span class="text-[0.7rem] font-semibold uppercase tracking-[0.12em] text-[var(--cip-muted)]">District</span>
        <select
          v-model="filterDistrict"
          class="cip-field"
        >
          <option value="">All</option>
          <option v-for="d in districtOptions" :key="d.id" :value="String(d.id)">
            {{ d.name }}
          </option>
        </select>
      </label>
      <label class="block text-sm">
        <span class="text-[0.7rem] font-semibold uppercase tracking-[0.12em] text-[var(--cip-muted)]">Status</span>
        <select
          v-model="filterStatus"
          class="cip-field"
        >
          <option value="">All</option>
          <option v-for="s in statuses" :key="s.id" :value="String(s.id)">
            {{ s.name }}
          </option>
        </select>
      </label>
      <label class="block text-sm">
        <span class="text-[0.7rem] font-semibold uppercase tracking-[0.12em] text-[var(--cip-muted)]">Crime head</span>
        <select
          v-model="filterHead"
          class="cip-field"
        >
          <option value="">All</option>
          <option v-for="h in crimeHeads" :key="h.id" :value="String(h.id)">
            {{ h.name }}
          </option>
        </select>
      </label>
      <div class="flex flex-wrap items-end gap-3 pb-2 text-sm">
        <label class="inline-flex items-center gap-1.5">
          <input v-model="showDistricts" type="checkbox" /> Districts
        </label>
        <label class="inline-flex items-center gap-1.5">
          <input v-model="showHotspots" type="checkbox" /> Hotspots
        </label>
        <label class="inline-flex items-center gap-1.5">
          <input v-model="showIncidents" type="checkbox" /> Incidents
        </label>
      </div>
    </div>

    <p v-if="error" class="text-sm text-[#9b2c1f]">{{ error }}</p>
    <p v-else-if="loading" class="text-sm text-[var(--cip-muted)]">Loading map layers…</p>

    <div class="grid gap-4 lg:grid-cols-[1fr_18rem]">
      <IncidentMap
        :districts="districts"
        :incidents="incidents"
        :hotspots="hotspots"
        :show-districts="showDistricts"
        :show-incidents="showIncidents"
        :show-hotspots="showHotspots"
        @select-incident="onSelect"
      />

      <aside class="cip-panel p-4 pl-5">
        <h2 class="cip-display text-lg text-[var(--cip-ink)]">Selection</h2>
        <template v-if="selected">
          <p class="mt-3 font-mono text-xs text-[var(--cip-ink)]">{{ selected.crime_no }}</p>
          <p class="mt-1 text-sm text-[var(--cip-muted)]">Case {{ selected.case_no }}</p>
          <p class="mt-2 text-xs text-[var(--cip-muted)]">
            {{ selected.latitude }}, {{ selected.longitude }}
          </p>
          <p class="mt-1 text-xs text-[var(--cip-muted)]">
            Registered {{ selected.crime_registered_date ?? "—" }}
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

        <h3 class="mt-6 text-[0.65rem] font-semibold uppercase tracking-[0.14em] text-[var(--cip-muted)]">
          Top districts
        </h3>
        <ul class="mt-2 max-h-64 space-y-1.5 overflow-y-auto text-sm">
          <li
            v-for="d in districts.slice().sort((a, b) => b.case_count - a.case_count).slice(0, 12)"
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
            <span class="tabular-nums text-[var(--cip-muted)]">{{ d.case_count }}</span>
          </li>
        </ul>
      </aside>
    </div>
  </section>
</template>
