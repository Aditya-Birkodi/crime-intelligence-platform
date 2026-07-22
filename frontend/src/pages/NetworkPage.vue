<script setup lang="ts">
import { onMounted, ref } from "vue";
import { RouterLink } from "vue-router";
import { api } from "@/services/api";
import type { CaseMasterDetail } from "@/types";

/**
 * Placeholder network view — builds a simple text graph from case parties
 * until GET /api/v1/network/graph (B3) is available.
 */
const loading = ref(true);
const error = ref<string | null>(null);
const edges = ref<string[]>([]);

onMounted(async () => {
  loading.value = true;
  try {
    const list = await api.listCases({ limit: 10 });
    const details: CaseMasterDetail[] = await Promise.all(
      list.items.slice(0, 5).map((c) => api.getCase(c.case_master_id)),
    );
    const lines: string[] = [];
    for (const d of details) {
      for (const a of d.accused) {
        lines.push(
          `Accused:${a.accused_name} —case→ ${d.crime_no}`,
        );
      }
      for (const v of d.victims) {
        lines.push(`Victim:${v.victim_name} —case→ ${d.crime_no}`);
      }
      lines.push(`Case:${d.crime_no} —station→ Unit:${d.police_station_id}`);
    }
    edges.value = lines;
  } catch (e) {
    error.value = e instanceof Error ? e.message : "Failed to build preview";
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <section class="space-y-6">
    <div>
      <h1 class="text-2xl font-semibold text-slate-900">Network</h1>
      <p class="mt-1 text-sm text-slate-600">
        Link-analysis placeholder derived from case parties. Full node graph UI
        waits on B3 <code class="text-xs">/api/v1/network/graph</code>.
      </p>
    </div>

    <p v-if="loading" class="text-sm text-slate-500">Building preview…</p>
    <p v-else-if="error" class="text-sm text-red-700">{{ error }}</p>

    <div
      v-else
      class="rounded-lg border border-slate-200 bg-white p-4 font-mono text-xs leading-relaxed text-slate-700"
    >
      <p v-for="(line, i) in edges" :key="i">{{ line }}</p>
      <p v-if="!edges.length" class="text-slate-400">No edges yet.</p>
    </div>

    <RouterLink to="/cases" class="text-sm text-slate-600 hover:text-slate-900">
      Browse source cases →
    </RouterLink>
  </section>
</template>
