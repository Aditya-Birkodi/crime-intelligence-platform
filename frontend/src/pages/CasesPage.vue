<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { RouterLink, useRouter } from "vue-router";
import { api } from "@/services/api";
import type { CaseMaster, IdName, SearchHit } from "@/types";

const router = useRouter();
const loading = ref(true);
const error = ref<string | null>(null);
const items = ref<CaseMaster[]>([]);
const total = ref(0);
const pageSize = 25;
const offset = ref(0);

const statuses = ref<IdName[]>([]);
const stations = ref<IdName[]>([]);
const crimeHeads = ref<IdName[]>([]);

const filterStatus = ref("");
const filterStation = ref("");
const filterHead = ref("");
const filterCrimeNo = ref("");
const filterFrom = ref("");
const filterTo = ref("");
const filterName = ref("");
const nameHits = ref<SearchHit[]>([]);
const nameSearching = ref(false);

const stationName = computed(() => {
  const map = new Map(stations.value.map((s) => [s.id, s.name]));
  return (id: number) => map.get(id) ?? String(id);
});

const statusName = computed(() => {
  const map = new Map(statuses.value.map((s) => [s.id, s.name]));
  return (id: number) => map.get(id) ?? String(id);
});

const headName = computed(() => {
  const map = new Map(crimeHeads.value.map((h) => [h.id, h.name]));
  return (id: number | null) => (id == null ? "—" : (map.get(id) ?? String(id)));
});

const page = computed(() => Math.floor(offset.value / pageSize) + 1);
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)));
const canPrev = computed(() => offset.value > 0);
const canNext = computed(() => offset.value + pageSize < total.value);

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
    const crimeNo = filterCrimeNo.value.trim();
    if (crimeNo && !filterStatus.value && !filterStation.value && !filterHead.value) {
      try {
        const detail = await api.getCaseByCrimeNo(crimeNo);
        items.value = [detail];
        total.value = 1;
        offset.value = 0;
        return;
      } catch {
        /* fall through to list filter */
      }
    }

    const res = await api.listCases({
      case_status_id: toOptionalInt(filterStatus.value),
      police_station_id: toOptionalInt(filterStation.value),
      crime_major_head_id: toOptionalInt(filterHead.value),
      crime_no: crimeNo || undefined,
      registered_from: filterFrom.value || undefined,
      registered_to: filterTo.value || undefined,
      limit: pageSize,
      offset: offset.value,
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

function resetAndLoad() {
  offset.value = 0;
  void loadCases();
}

function prevPage() {
  if (!canPrev.value) return;
  offset.value = Math.max(0, offset.value - pageSize);
  void loadCases();
}

function nextPage() {
  if (!canNext.value) return;
  offset.value += pageSize;
  void loadCases();
}

async function jumpCrimeNo() {
  const q = filterCrimeNo.value.trim();
  if (!q) return;
  try {
    const detail = await api.getCaseByCrimeNo(q);
    await router.push(`/cases/${detail.case_master_id}`);
  } catch {
    resetAndLoad();
  }
}

async function searchByName() {
  const q = filterName.value.trim();
  if (q.length < 2) {
    nameHits.value = [];
    return;
  }
  nameSearching.value = true;
  try {
    const res = await api.search({
      q,
      types: "accused,victim,complainant",
      limit: 20,
    });
    nameHits.value = res.items;
  } catch {
    nameHits.value = [];
  } finally {
    nameSearching.value = false;
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

watch([filterStatus, filterStation, filterHead, filterFrom, filterTo], resetAndLoad);
</script>

<template>
  <section class="cip-rise space-y-7">
    <div class="flex flex-wrap items-end justify-between gap-4">
      <div>
        <p class="cip-kicker">Case register</p>
        <h1 class="cip-display mt-1 text-3xl text-[var(--cip-ink)]">FIR desk</h1>
        <p class="mt-1 text-sm text-[var(--cip-muted)]">
          {{ total }} records · page {{ page }} of {{ totalPages }}
        </p>
      </div>
    </div>

    <div class="cip-panel grid gap-3 p-4 pl-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
      <label class="block text-sm sm:col-span-2 xl:col-span-2">
        <span class="text-[0.7rem] font-semibold uppercase tracking-[0.12em] text-[var(--cip-muted)]">Crime number</span>
        <div class="mt-1 flex gap-2">
          <input
            v-model="filterCrimeNo"
            type="search"
            placeholder="e.g. 0123/2024"
            class="cip-field !mt-0"
            @keydown.enter="jumpCrimeNo"
          />
          <button type="button" class="cip-btn cip-btn-ghost shrink-0" @click="jumpCrimeNo">Go</button>
        </div>
      </label>
      <label class="block text-sm sm:col-span-2 xl:col-span-2">
        <span class="text-[0.7rem] font-semibold uppercase tracking-[0.12em] text-[var(--cip-muted)]">Person name</span>
        <div class="mt-1 flex gap-2">
          <input
            v-model="filterName"
            type="search"
            placeholder="Accused / victim / complainant"
            class="cip-field !mt-0"
            @keydown.enter="searchByName"
          />
          <button
            type="button"
            class="cip-btn cip-btn-ghost shrink-0"
            :disabled="nameSearching"
            @click="searchByName"
          >
            {{ nameSearching ? "…" : "Find" }}
          </button>
        </div>
      </label>
      <label class="block text-sm">
        <span class="text-[0.7rem] font-semibold uppercase tracking-[0.12em] text-[var(--cip-muted)]">Status</span>
        <select v-model="filterStatus" class="cip-field">
          <option value="">All</option>
          <option v-for="s in statuses" :key="s.id" :value="String(s.id)">{{ s.name }}</option>
        </select>
      </label>
      <label class="block text-sm">
        <span class="text-[0.7rem] font-semibold uppercase tracking-[0.12em] text-[var(--cip-muted)]">Station</span>
        <select v-model="filterStation" class="cip-field">
          <option value="">All</option>
          <option v-for="s in stations" :key="s.id" :value="String(s.id)">{{ s.name }}</option>
        </select>
      </label>
      <label class="block text-sm">
        <span class="text-[0.7rem] font-semibold uppercase tracking-[0.12em] text-[var(--cip-muted)]">Crime head</span>
        <select v-model="filterHead" class="cip-field">
          <option value="">All</option>
          <option v-for="h in crimeHeads" :key="h.id" :value="String(h.id)">{{ h.name }}</option>
        </select>
      </label>
      <label class="block text-sm">
        <span class="text-[0.7rem] font-semibold uppercase tracking-[0.12em] text-[var(--cip-muted)]">From</span>
        <input v-model="filterFrom" type="date" class="cip-field" />
      </label>
      <label class="block text-sm">
        <span class="text-[0.7rem] font-semibold uppercase tracking-[0.12em] text-[var(--cip-muted)]">To</span>
        <input v-model="filterTo" type="date" class="cip-field" />
      </label>
    </div>

    <p v-if="error" class="text-sm text-[#9b2c1f]">{{ error }}</p>
    <p v-else-if="loading" class="text-sm text-[var(--cip-muted)]">Loading cases…</p>

    <div v-if="nameHits.length" class="cip-panel p-4 pl-5">
      <div class="flex items-center justify-between gap-2">
        <h2 class="cip-display text-lg text-[var(--cip-ink)]">
          Name matches ({{ nameHits.length }})
        </h2>
        <button
          type="button"
          class="text-xs font-semibold text-[var(--cip-muted)] hover:underline"
          @click="nameHits = []"
        >
          Clear
        </button>
      </div>
      <ul class="mt-3 divide-y divide-[rgba(197,212,216,0.5)]">
        <li
          v-for="(h, i) in nameHits"
          :key="i"
          class="flex flex-wrap items-center justify-between gap-2 py-2 text-sm"
        >
          <div>
            <span class="cip-badge cip-badge-med mr-2">{{ h.entity_type }}</span>
            <span class="font-semibold text-[var(--cip-ink)]">{{ h.name }}</span>
            <span v-if="h.crime_no" class="ml-2 font-mono text-xs text-[var(--cip-muted)]">{{
              h.crime_no
            }}</span>
          </div>
          <RouterLink
            v-if="h.case_master_id"
            :to="`/cases/${h.case_master_id}`"
            class="font-semibold text-[var(--cip-accent-deep)] hover:underline"
          >
            Open case →
          </RouterLink>
        </li>
      </ul>
    </div>

    <div v-if="!loading" class="cip-table-wrap">
      <table>
        <thead>
          <tr>
            <th>Crime No</th>
            <th>Case No</th>
            <th>Station</th>
            <th>Crime head</th>
            <th>Status</th>
            <th>Registered</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in items" :key="c.case_master_id">
            <td class="font-mono text-xs">{{ c.crime_no }}</td>
            <td>{{ c.case_no }}</td>
            <td>{{ stationName(c.police_station_id) }}</td>
            <td>{{ headName(c.crime_major_head_id) }}</td>
            <td>
              <span class="cip-badge cip-badge-med">{{
                statusName(c.case_status_id)
              }}</span>
            </td>
            <td>{{ c.crime_registered_date ?? "—" }}</td>
            <td class="text-right">
              <RouterLink
                :to="`/cases/${c.case_master_id}`"
                class="text-sm font-semibold text-[var(--cip-accent-deep)] underline-offset-2 hover:underline"
              >
                Open
              </RouterLink>
            </td>
          </tr>
          <tr v-if="items.length === 0">
            <td colspan="7" class="py-10 text-center text-[var(--cip-muted)]">
              No cases found. Adjust filters or seed the backend.
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="flex items-center justify-between gap-3 text-sm">
      <button type="button" class="cip-btn cip-btn-ghost disabled:opacity-40" :disabled="!canPrev || loading" @click="prevPage">
        Previous
      </button>
      <span class="text-[var(--cip-muted)]">Showing {{ items.length }} of {{ total }}</span>
      <button type="button" class="cip-btn cip-btn-ghost disabled:opacity-40" :disabled="!canNext || loading" @click="nextPage">
        Next
      </button>
    </div>
  </section>
</template>
