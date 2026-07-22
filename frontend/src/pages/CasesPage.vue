<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { RouterLink } from "vue-router";
import { api } from "@/services/api";
import type { CaseMaster, IdName } from "@/types";

const loading = ref(true);
const error = ref<string | null>(null);
const items = ref<CaseMaster[]>([]);
const total = ref(0);

const statuses = ref<IdName[]>([]);
const stations = ref<IdName[]>([]);
const crimeHeads = ref<IdName[]>([]);

const filterStatus = ref<string>("");
const filterStation = ref<string>("");
const filterHead = ref<string>("");

const statusName = computed(() => {
  const map = new Map(statuses.value.map((s) => [s.id, s.name]));
  return (id: number) => map.get(id) ?? String(id);
});

function toOptionalInt(value: string): number | undefined {
  if (!value) return undefined;
  const n = Number(value);
  return Number.isFinite(n) ? n : undefined;
}

async function loadLookups() {
  const [st, stationsList, heads] = await Promise.all([
    api.listCaseStatuses(),
    api.listStations(),
    api.listCrimeHeads(),
  ]);
  statuses.value = st;
  stations.value = stationsList;
  crimeHeads.value = heads;
}

async function loadCases() {
  loading.value = true;
  error.value = null;
  try {
    const res = await api.listCases({
      case_status_id: toOptionalInt(filterStatus.value),
      police_station_id: toOptionalInt(filterStation.value),
      crime_major_head_id: toOptionalInt(filterHead.value),
      limit: 50,
    });
    items.value = res.items;
    total.value = res.total;
  } catch (e) {
    error.value = e instanceof Error ? e.message : "Failed to load cases";
    items.value = [];
    total.value = 0;
  } finally {
    loading.value = false;
  }
}

onMounted(async () => {
  try {
    await loadLookups();
  } catch (e) {
    error.value = e instanceof Error ? e.message : "Failed to load lookups";
  }
  await loadCases();
});

watch([filterStatus, filterStation, filterHead], () => {
  void loadCases();
});
</script>

<template>
  <section class="space-y-6">
    <div class="flex flex-wrap items-end justify-between gap-4">
      <div>
        <h1 class="text-2xl font-semibold text-slate-900">Cases</h1>
        <p class="mt-1 text-sm text-slate-600">
          FIR list from <code class="text-xs">GET /api/v1/cases</code>
          · {{ total }} total
        </p>
      </div>
    </div>

    <div class="grid gap-3 sm:grid-cols-3">
      <label class="block text-sm">
        <span class="text-slate-500">Status</span>
        <select
          v-model="filterStatus"
          class="mt-1 w-full rounded-md border border-slate-300 bg-white px-3 py-2"
        >
          <option value="">All</option>
          <option v-for="s in statuses" :key="s.id" :value="String(s.id)">
            {{ s.name }}
          </option>
        </select>
      </label>
      <label class="block text-sm">
        <span class="text-slate-500">Station</span>
        <select
          v-model="filterStation"
          class="mt-1 w-full rounded-md border border-slate-300 bg-white px-3 py-2"
        >
          <option value="">All</option>
          <option v-for="s in stations" :key="s.id" :value="String(s.id)">
            {{ s.name }}
          </option>
        </select>
      </label>
      <label class="block text-sm">
        <span class="text-slate-500">Crime head</span>
        <select
          v-model="filterHead"
          class="mt-1 w-full rounded-md border border-slate-300 bg-white px-3 py-2"
        >
          <option value="">All</option>
          <option v-for="h in crimeHeads" :key="h.id" :value="String(h.id)">
            {{ h.name }}
          </option>
        </select>
      </label>
    </div>

    <p v-if="error" class="text-sm text-red-700">{{ error }}</p>
    <p v-else-if="loading" class="text-sm text-slate-500">Loading cases…</p>

    <div v-else class="overflow-x-auto rounded-lg border border-slate-200 bg-white">
      <table class="min-w-full text-left text-sm">
        <thead class="border-b border-slate-200 bg-slate-50 text-xs uppercase text-slate-500">
          <tr>
            <th class="px-4 py-3 font-medium">Crime No</th>
            <th class="px-4 py-3 font-medium">Case No</th>
            <th class="px-4 py-3 font-medium">Station</th>
            <th class="px-4 py-3 font-medium">Status</th>
            <th class="px-4 py-3 font-medium">Registered</th>
            <th class="px-4 py-3 font-medium"></th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="c in items"
            :key="c.case_master_id"
            class="border-b border-slate-100 last:border-0 hover:bg-slate-50/80"
          >
            <td class="px-4 py-3 font-mono text-xs">{{ c.crime_no }}</td>
            <td class="px-4 py-3">{{ c.case_no }}</td>
            <td class="px-4 py-3">{{ c.police_station_id }}</td>
            <td class="px-4 py-3">{{ statusName(c.case_status_id) }}</td>
            <td class="px-4 py-3">{{ c.crime_registered_date ?? "—" }}</td>
            <td class="px-4 py-3 text-right">
              <RouterLink
                :to="`/cases/${c.case_master_id}`"
                class="text-slate-900 underline-offset-2 hover:underline"
              >
                Open
              </RouterLink>
            </td>
          </tr>
          <tr v-if="items.length === 0">
            <td colspan="6" class="px-4 py-8 text-center text-slate-500">
              No cases found. Seed the backend or clear filters.
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>
