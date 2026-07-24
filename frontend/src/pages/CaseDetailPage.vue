<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute, RouterLink } from "vue-router";
import { api } from "@/services/api";
import type { CaseMasterDetail } from "@/types";

const route = useRoute();
const loading = ref(true);
const error = ref<string | null>(null);
const detail = ref<CaseMasterDetail | null>(null);

const question = ref("Summarize modus operandi and linked risk for this FIR");
const asking = ref(false);
const aiAnswer = ref<string | null>(null);
const aiError = ref<string | null>(null);
const graphSummary = ref<string | null>(null);
const useGraphRag = ref(true);

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

async function askAi() {
  asking.value = true;
  aiError.value = null;
  aiAnswer.value = null;
  graphSummary.value = null;
  try {
    const res = await api.aiChat({
      question: question.value,
      case_master_id: caseId.value,
      use_graph_rag: useGraphRag.value,
      graph_depth: 2,
      top_k: 5,
    });
    aiAnswer.value = res.answer;
    graphSummary.value = res.graph_context?.summary ?? null;
  } catch (e) {
    aiError.value = e instanceof Error ? e.message : "AI request failed";
  } finally {
    asking.value = false;
  }
}
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
        <div v-if="detail.occurrence" class="md:col-span-2">
          <p class="text-xs uppercase text-slate-500">Place of occurrence</p>
          <p class="mt-1 text-slate-800">
            {{ detail.occurrence.place_of_occurrence || "—" }}
            <span v-if="detail.occurrence.beat_number" class="text-slate-500">
              · Beat {{ detail.occurrence.beat_number }}
            </span>
          </p>
        </div>
      </div>

      <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
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
          <h2 class="text-sm font-semibold text-slate-900">Complainants</h2>
          <ul class="mt-3 space-y-2 text-sm text-slate-700">
            <li v-for="c in detail.complainants" :key="c.complainant_id">
              {{ c.complainant_name }}
            </li>
            <li v-if="!detail.complainants?.length" class="text-slate-400">None</li>
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

      <div class="grid gap-4 md:grid-cols-2">
        <div class="rounded-lg border border-slate-200 bg-white p-4">
          <h2 class="text-sm font-semibold text-slate-900">Arrests</h2>
          <ul class="mt-3 space-y-2 text-sm text-slate-700">
            <li v-for="a in detail.arrests" :key="a.arrest_surrender_id">
              {{ a.arrest_surrender_date || "—" }} · type
              {{ a.arrest_surrender_type_id }}
              <span v-if="a.accused_master_id" class="text-slate-400">
                · accused #{{ a.accused_master_id }}
              </span>
            </li>
            <li v-if="!detail.arrests?.length" class="text-slate-400">None</li>
          </ul>
        </div>
        <div class="rounded-lg border border-slate-200 bg-white p-4">
          <h2 class="text-sm font-semibold text-slate-900">Chargesheets</h2>
          <ul class="mt-3 space-y-2 text-sm text-slate-700">
            <li v-for="cs in detail.chargesheets" :key="cs.cs_id">
              Type {{ cs.cs_type }} · {{ cs.cs_date || "—" }}
            </li>
            <li v-if="!detail.chargesheets?.length" class="text-slate-400">None</li>
          </ul>
        </div>
      </div>

      <div class="rounded-lg border border-slate-200 bg-white p-5">
        <h2 class="text-sm font-semibold text-slate-900">Ask AI</h2>
        <p class="mt-1 text-xs text-slate-500">
          QuickML RAG on AppSail; Graph RAG uses NetworkX neighborhood links.
        </p>
        <label class="mt-3 flex items-center gap-2 text-sm text-slate-700">
          <input v-model="useGraphRag" type="checkbox" class="rounded border-slate-300" />
          Use Graph RAG (NetworkX on Catalyst)
        </label>
        <textarea
          v-model="question"
          rows="2"
          class="mt-3 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
        />
        <button
          type="button"
          class="mt-3 rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50"
          :disabled="asking"
          @click="askAi"
        >
          {{ asking ? "Asking…" : "Ask" }}
        </button>
        <p v-if="aiError" class="mt-3 text-sm text-red-700">{{ aiError }}</p>
        <pre
          v-if="graphSummary"
          class="mt-3 whitespace-pre-wrap rounded-md border border-slate-200 bg-slate-50 p-3 text-xs text-slate-600"
          >{{ graphSummary }}</pre
        >
        <pre
          v-if="aiAnswer"
          class="mt-3 whitespace-pre-wrap rounded-md bg-slate-50 p-3 text-sm text-slate-800"
          >{{ aiAnswer }}</pre
        >
      </div>
    </template>
  </section>
</template>
