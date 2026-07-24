<script setup lang="ts">
import { onMounted, ref } from "vue";
import { RouterLink } from "vue-router";
import { api, baseUrl } from "@/services/api";

const health = ref<string>("checking…");
const apiStatus = ref<string>("checking…");
const caseCount = ref<string>("—");
const error = ref<string | null>(null);
const overview = ref<{
  total_cases: number;
  cases_with_coordinates: number;
  districts_covered: number;
  stations_covered: number;
} | null>(null);
const riskTop = ref<
  { scope_id: number; risk_score: number; case_count: number }[]
>([]);
const anomalies = ref<
  { title: string; severity: string; kind: string; score: number }[]
>([]);

onMounted(async () => {
  try {
    const [h, s, cases, ov, risk, anom] = await Promise.all([
      api.getHealth(),
      api.getStatus(),
      api.listCases({ limit: 1 }),
      api.getAnalyticsOverview().catch(() => null),
      api.aiPredictRisk({ horizon_days: 7 }).catch(() => null),
      api.aiAnomalies(5).catch(() => null),
    ]);
    health.value = h.status;
    apiStatus.value = `${s.api}/${s.status}`;
    caseCount.value = String(cases.total);
    if (ov) overview.value = ov;
    if (risk) riskTop.value = risk.items.slice(0, 5);
    if (anom) anomalies.value = anom.items.slice(0, 5);
  } catch (e) {
    error.value = e instanceof Error ? e.message : "Failed to reach API";
    health.value = "down";
    apiStatus.value = "down";
  }
});
</script>

<template>
  <section class="space-y-8">
    <div>
      <h1 class="text-3xl font-semibold tracking-tight text-slate-900">
        SCRB intelligence shell
      </h1>
      <p class="mt-2 max-w-2xl text-slate-600">
        Vue 3 frontend wired to case, analytics, network, and AI APIs.
        API base:
        <code class="rounded bg-slate-100 px-1 text-sm">{{ baseUrl }}</code>
      </p>
    </div>

    <div
      v-if="error"
      class="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900"
    >
      {{ error }}
    </div>

    <div class="grid gap-4 sm:grid-cols-3 lg:grid-cols-6">
      <div class="rounded-lg border border-slate-200 bg-white p-4">
        <p class="text-xs uppercase tracking-wide text-slate-500">Health</p>
        <p class="mt-2 text-2xl font-medium">{{ health }}</p>
      </div>
      <div class="rounded-lg border border-slate-200 bg-white p-4">
        <p class="text-xs uppercase tracking-wide text-slate-500">API v1</p>
        <p class="mt-2 text-2xl font-medium">{{ apiStatus }}</p>
      </div>
      <div class="rounded-lg border border-slate-200 bg-white p-4">
        <p class="text-xs uppercase tracking-wide text-slate-500">Cases</p>
        <p class="mt-2 text-2xl font-medium">{{ caseCount }}</p>
      </div>
      <div class="rounded-lg border border-slate-200 bg-white p-4">
        <p class="text-xs uppercase tracking-wide text-slate-500">With coords</p>
        <p class="mt-2 text-2xl font-medium">
          {{ overview?.cases_with_coordinates ?? "—" }}
        </p>
      </div>
      <div class="rounded-lg border border-slate-200 bg-white p-4">
        <p class="text-xs uppercase tracking-wide text-slate-500">Districts</p>
        <p class="mt-2 text-2xl font-medium">
          {{ overview?.districts_covered ?? "—" }}
        </p>
      </div>
      <div class="rounded-lg border border-slate-200 bg-white p-4">
        <p class="text-xs uppercase tracking-wide text-slate-500">Stations</p>
        <p class="mt-2 text-2xl font-medium">
          {{ overview?.stations_covered ?? "—" }}
        </p>
      </div>
    </div>

    <div class="grid gap-4 lg:grid-cols-2">
      <div class="rounded-lg border border-slate-200 bg-white p-4">
        <h2 class="text-sm font-semibold text-slate-900">Top district risk</h2>
        <ul class="mt-3 space-y-2 text-sm text-slate-700">
          <li v-for="r in riskTop" :key="r.scope_id" class="flex justify-between">
            <span>District {{ r.scope_id }} · {{ r.case_count }} cases</span>
            <span class="font-medium">{{ r.risk_score.toFixed(1) }}</span>
          </li>
          <li v-if="!riskTop.length" class="text-slate-400">No risk data</li>
        </ul>
      </div>
      <div class="rounded-lg border border-slate-200 bg-white p-4">
        <h2 class="text-sm font-semibold text-slate-900">Anomalies</h2>
        <ul class="mt-3 space-y-2 text-sm text-slate-700">
          <li v-for="(a, i) in anomalies" :key="i">
            <span
              class="mr-2 rounded px-1.5 py-0.5 text-xs uppercase"
              :class="
                a.severity === 'high'
                  ? 'bg-red-100 text-red-800'
                  : 'bg-amber-100 text-amber-900'
              "
              >{{ a.severity }}</span
            >
            {{ a.title }}
          </li>
          <li v-if="!anomalies.length" class="text-slate-400">No anomalies</li>
        </ul>
      </div>
    </div>

    <div class="flex flex-wrap gap-3">
      <RouterLink
        to="/cases"
        class="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800"
      >
        Browse cases
      </RouterLink>
      <RouterLink
        to="/map"
        class="rounded-md border border-slate-300 bg-white px-4 py-2 text-sm text-slate-700 hover:bg-slate-50"
      >
        Map
      </RouterLink>
      <RouterLink
        to="/network"
        class="rounded-md border border-slate-300 bg-white px-4 py-2 text-sm text-slate-700 hover:bg-slate-50"
      >
        Network
      </RouterLink>
    </div>
  </section>
</template>
