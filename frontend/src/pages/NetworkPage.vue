<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { RouterLink } from "vue-router";
import { api } from "@/services/api";
import type { NetworkGraphResponse } from "@/types";

const loading = ref(true);
const error = ref<string | null>(null);
const graph = ref<NetworkGraphResponse | null>(null);
const caseId = ref<number | null>(null);

const edgeLines = computed(() => {
  if (!graph.value) return [];
  const labels = new Map(graph.value.nodes.map((n) => [n.id, n.label]));
  return graph.value.edges.map(
    (e) =>
      `${labels.get(e.source) ?? e.source} —${e.relation}(${e.score})→ ${labels.get(e.target) ?? e.target}`,
  );
});

onMounted(async () => {
  loading.value = true;
  try {
    const list = await api.listCases({ limit: 1 });
    const first = list.items[0];
    if (!first) {
      error.value = "No cases available to seed the graph.";
      return;
    }
    caseId.value = first.case_master_id;
    graph.value = await api.getNetworkGraph({
      case_id: first.case_master_id,
      depth: 2,
    });
  } catch (e) {
    error.value = e instanceof Error ? e.message : "Failed to load network graph";
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
        Link analysis from
        <code class="text-xs">GET /api/v1/network/graph</code>
        <span v-if="caseId"> (seed case {{ caseId }})</span>.
      </p>
    </div>

    <p v-if="loading" class="text-sm text-slate-500">Loading graph…</p>
    <p v-else-if="error" class="text-sm text-red-700">{{ error }}</p>

    <template v-else-if="graph">
      <p class="text-sm text-slate-600">
        {{ graph.nodes.length }} nodes · {{ graph.edges.length }} edges · seed
        {{ graph.seed }}
      </p>
      <div
        class="rounded-lg border border-slate-200 bg-white p-4 font-mono text-xs leading-relaxed text-slate-700"
      >
        <p v-for="(line, i) in edgeLines" :key="i">{{ line }}</p>
        <p v-if="!edgeLines.length" class="text-slate-400">No edges yet.</p>
      </div>
    </template>

    <RouterLink to="/cases" class="text-sm text-slate-600 hover:text-slate-900">
      Browse source cases →
    </RouterLink>
  </section>
</template>
