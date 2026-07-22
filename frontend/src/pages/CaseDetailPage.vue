<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute, RouterLink } from "vue-router";
import { api } from "@/services/api";
import type { CaseMasterDetail } from "@/types";

const route = useRoute();
const loading = ref(true);
const error = ref<string | null>(null);
const detail = ref<CaseMasterDetail | null>(null);

const caseId = computed(() => Number(route.params.id));

onMounted(async () => {
  loading.value = true;
  error.value = null;
  try {
    detail.value = await api.getCase(caseId.value);
  } catch (e) {
    error.value = e instanceof Error ? e.message : "Failed to load case";
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <section class="space-y-6">
    <div>
      <RouterLink to="/cases" class="text-sm text-slate-500 hover:text-slate-800">
        ← Back to cases
      </RouterLink>
      <h1 class="mt-2 text-2xl font-semibold text-slate-900">Case detail</h1>
    </div>

    <p v-if="loading" class="text-sm text-slate-500">Loading…</p>
    <p v-else-if="error" class="text-sm text-red-700">{{ error }}</p>

    <template v-else-if="detail">
      <div class="grid gap-4 rounded-lg border border-slate-200 bg-white p-5 md:grid-cols-2">
        <div>
          <p class="text-xs uppercase text-slate-500">Crime No</p>
          <p class="mt-1 font-mono text-sm">{{ detail.crime_no }}</p>
        </div>
        <div>
          <p class="text-xs uppercase text-slate-500">Case No</p>
          <p class="mt-1">{{ detail.case_no }}</p>
        </div>
        <div>
          <p class="text-xs uppercase text-slate-500">Station ID</p>
          <p class="mt-1">{{ detail.police_station_id }}</p>
        </div>
        <div>
          <p class="text-xs uppercase text-slate-500">Registered</p>
          <p class="mt-1">{{ detail.crime_registered_date ?? "—" }}</p>
        </div>
        <div>
          <p class="text-xs uppercase text-slate-500">Location</p>
          <p class="mt-1">
            {{ detail.latitude ?? "—" }}, {{ detail.longitude ?? "—" }}
          </p>
        </div>
        <div>
          <p class="text-xs uppercase text-slate-500">Status ID</p>
          <p class="mt-1">{{ detail.case_status_id }}</p>
        </div>
        <div class="md:col-span-2">
          <p class="text-xs uppercase text-slate-500">Brief facts</p>
          <p class="mt-1 whitespace-pre-wrap text-slate-800">
            {{ detail.brief_facts || "—" }}
          </p>
        </div>
      </div>

      <div class="grid gap-4 md:grid-cols-3">
        <div class="rounded-lg border border-slate-200 bg-white p-4">
          <h2 class="text-sm font-semibold text-slate-900">Victims</h2>
          <ul class="mt-3 space-y-2 text-sm text-slate-700">
            <li v-for="v in detail.victims" :key="v.victim_master_id">
              {{ v.victim_name }}
              <span v-if="v.age_year" class="text-slate-400">({{ v.age_year }})</span>
            </li>
            <li v-if="!detail.victims.length" class="text-slate-400">None</li>
          </ul>
        </div>
        <div class="rounded-lg border border-slate-200 bg-white p-4">
          <h2 class="text-sm font-semibold text-slate-900">Accused</h2>
          <ul class="mt-3 space-y-2 text-sm text-slate-700">
            <li v-for="a in detail.accused" :key="a.accused_master_id">
              {{ a.person_id ? `${a.person_id} · ` : "" }}{{ a.accused_name }}
            </li>
            <li v-if="!detail.accused.length" class="text-slate-400">None</li>
          </ul>
        </div>
        <div class="rounded-lg border border-slate-200 bg-white p-4">
          <h2 class="text-sm font-semibold text-slate-900">Act / sections</h2>
          <ul class="mt-3 space-y-2 text-sm text-slate-700">
            <li v-for="s in detail.act_sections" :key="s.id">
              {{ s.act_id }} {{ s.section_id }}
            </li>
            <li v-if="!detail.act_sections.length" class="text-slate-400">None</li>
          </ul>
        </div>
      </div>
    </template>
  </section>
</template>
