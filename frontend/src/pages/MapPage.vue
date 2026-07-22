<script setup lang="ts">
import { onMounted, ref } from "vue";
import { RouterLink } from "vue-router";
import { api } from "@/services/api";
import type { CaseMaster } from "@/types";

/** Placeholder map page — plots case lat/long as a simple list until B2 geo APIs. */
const points = ref<CaseMaster[]>([]);
const error = ref<string | null>(null);

onMounted(async () => {
  try {
    const res = await api.listCases({ limit: 100 });
    points.value = res.items.filter((c) => c.latitude != null && c.longitude != null);
  } catch (e) {
    error.value = e instanceof Error ? e.message : "Failed to load points";
  }
});
</script>

<template>
  <section class="space-y-6">
    <div>
      <h1 class="text-2xl font-semibold text-slate-900">Map</h1>
      <p class="mt-1 text-sm text-slate-600">
        Placeholder geospatial view. Uses case lat/long from B1 until
        <code class="text-xs">/api/v1/analytics/geo/*</code> (B2) lands.
      </p>
    </div>

    <p v-if="error" class="text-sm text-red-700">{{ error }}</p>

    <div
      class="flex min-h-64 items-center justify-center rounded-lg border border-dashed border-slate-300 bg-white/60 p-8 text-center text-slate-500"
    >
      Interactive district map coming in B2 (FE).
      <br />
      {{ points.length }} geocoded cases available from API.
    </div>

    <ul class="divide-y divide-slate-200 rounded-lg border border-slate-200 bg-white">
      <li
        v-for="p in points"
        :key="p.case_master_id"
        class="flex flex-wrap items-center justify-between gap-2 px-4 py-3 text-sm"
      >
        <div>
          <span class="font-mono text-xs">{{ p.crime_no }}</span>
          <span class="ml-2 text-slate-500">
            {{ p.latitude }}, {{ p.longitude }}
          </span>
        </div>
        <RouterLink
          :to="`/cases/${p.case_master_id}`"
          class="text-slate-900 underline-offset-2 hover:underline"
        >
          Open
        </RouterLink>
      </li>
      <li v-if="!points.length && !error" class="px-4 py-6 text-center text-slate-400">
        No cases with coordinates.
      </li>
    </ul>
  </section>
</template>
