<script setup lang="ts">
import { onMounted, ref } from "vue";
import { RouterLink } from "vue-router";
import { api, baseUrl } from "@/services/api";

const health = ref<string>("checking…");
const apiStatus = ref<string>("checking…");
const caseCount = ref<string>("—");
const error = ref<string | null>(null);

onMounted(async () => {
  try {
    const [h, s, cases] = await Promise.all([
      api.getHealth(),
      api.getStatus(),
      api.listCases({ limit: 1 }),
    ]);
    health.value = h.status;
    apiStatus.value = `${s.api}/${s.status}`;
    caseCount.value = String(cases.total);
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
        Vue 3 frontend wired to B1 case APIs. Point
        <code class="rounded bg-slate-100 px-1 text-sm">VITE_API_BASE_URL</code>
        at AppSail (or local <code class="rounded bg-slate-100 px-1 text-sm">http://127.0.0.1:8000</code>).
      </p>
    </div>

    <div
      v-if="error"
      class="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900"
    >
      {{ error }}
      <p class="mt-1 text-amber-800/80">
        Is the backend reachable and CORS allowing this origin?
        API base: <code>{{ baseUrl }}</code>
      </p>
    </div>

    <div class="grid gap-4 sm:grid-cols-3">
      <div class="rounded-lg border border-slate-200 bg-white p-4">
        <p class="text-xs uppercase tracking-wide text-slate-500">Health</p>
        <p class="mt-2 text-2xl font-medium">{{ health }}</p>
      </div>
      <div class="rounded-lg border border-slate-200 bg-white p-4">
        <p class="text-xs uppercase tracking-wide text-slate-500">API v1</p>
        <p class="mt-2 text-2xl font-medium">{{ apiStatus }}</p>
      </div>
      <div class="rounded-lg border border-slate-200 bg-white p-4">
        <p class="text-xs uppercase tracking-wide text-slate-500">Cases seeded</p>
        <p class="mt-2 text-2xl font-medium">{{ caseCount }}</p>
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
        Map (placeholder)
      </RouterLink>
      <RouterLink
        to="/network"
        class="rounded-md border border-slate-300 bg-white px-4 py-2 text-sm text-slate-700 hover:bg-slate-50"
      >
        Network (placeholder)
      </RouterLink>
    </div>
  </section>
</template>
