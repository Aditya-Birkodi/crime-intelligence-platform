<script setup lang="ts">
import { ref } from "vue";
import { api } from "@/services/api";

const props = withDefaults(
  defineProps<{
    caseMasterId?: number;
    accusedId?: number;
    title?: string;
    defaultQuestion?: string;
  }>(),
  {
    title: "Ask AI",
    defaultQuestion: "Summarize modus operandi and related risk signals",
  },
);

const question = ref(props.defaultQuestion);
const asking = ref(false);
const useGraphRag = ref(true);
const answer = ref<string | null>(null);
const graphSummary = ref<string | null>(null);
const citations = ref<
  { crime_no: string | null; snippet: string | null; case_master_id: number | null }[]
>([]);
const error = ref<string | null>(null);
const provider = ref<string | null>(null);

async function ask() {
  if (!question.value.trim()) return;
  asking.value = true;
  error.value = null;
  answer.value = null;
  graphSummary.value = null;
  citations.value = [];
  try {
    const res = await api.aiChat({
      question: question.value.trim(),
      case_master_id: props.caseMasterId,
      accused_id: props.accusedId,
      use_graph_rag: useGraphRag.value,
      graph_depth: 2,
      top_k: 5,
    });
    answer.value = res.answer;
    graphSummary.value = res.graph_context?.summary ?? null;
    citations.value = res.citations ?? [];
    provider.value = res.provider;
  } catch (e) {
    error.value = e instanceof Error ? e.message : "AI request failed";
  } finally {
    asking.value = false;
  }
}
</script>

<template>
  <div class="cip-panel p-5 pl-6">
    <p class="cip-kicker">QuickML · Graph RAG</p>
    <h2 class="cip-display mt-1 text-xl text-[var(--cip-ink)]">{{ title }}</h2>
    <p class="mt-1 text-xs text-[var(--cip-muted)]">
      AppSail → QuickML GLM (server-side) · local FIR citations · optional Graph RAG.
    </p>

    <label class="mt-4 flex items-center gap-2 text-sm text-[var(--cip-ink-soft)]">
      <input v-model="useGraphRag" type="checkbox" class="accent-[var(--cip-accent)]" />
      Use Graph RAG
    </label>

    <textarea
      v-model="question"
      rows="3"
      class="cip-field"
      placeholder="Ask about FIRs, MO patterns, linked accused…"
    />

    <button
      type="button"
      class="cip-btn cip-btn-primary mt-3 disabled:opacity-50"
      :disabled="asking || !question.trim()"
      @click="ask"
    >
      {{ asking ? "Listening…" : "Ask desk AI" }}
    </button>

    <p v-if="error" class="mt-3 text-sm text-[#9b2c1f]">{{ error }}</p>

    <pre
      v-if="graphSummary"
      class="mt-4 whitespace-pre-wrap border border-[var(--cip-line)] bg-[rgba(13,107,124,0.05)] p-3 text-xs leading-relaxed text-[var(--cip-ink-soft)]"
      >{{ graphSummary }}</pre
    >

    <pre
      v-if="answer"
      class="mt-3 whitespace-pre-wrap border border-[var(--cip-line)] bg-[rgba(255,255,255,0.65)] p-4 text-sm leading-relaxed text-[var(--cip-ink)]"
      >{{ answer }}</pre
    >

    <div v-if="citations.length" class="mt-4 space-y-2">
      <p class="text-[0.65rem] font-semibold uppercase tracking-[0.16em] text-[var(--cip-muted)]">
        Citations
        <span v-if="provider" class="normal-case tracking-normal"> · {{ provider }}</span>
      </p>
      <div
        v-for="(c, i) in citations"
        :key="i"
        class="border-l-2 border-[var(--cip-signal)] bg-[rgba(255,255,255,0.5)] px-3 py-2 text-xs text-[var(--cip-muted)]"
      >
        <span class="font-mono text-[var(--cip-ink)]">{{
          c.crime_no || `case #${c.case_master_id}`
        }}</span>
        <p v-if="c.snippet" class="mt-1 line-clamp-3">{{ c.snippet }}</p>
      </div>
    </div>
  </div>
</template>
