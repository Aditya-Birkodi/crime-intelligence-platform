<script setup lang="ts">
import { onMounted, ref } from "vue";
import { RouterLink } from "vue-router";
import { api } from "@/services/api";
import AiChatPanel from "@/components/AiChatPanel.vue";
import type {
  CaseMaster,
  IntelligenceBriefResponse,
  MoCluster,
} from "@/types";

const cases = ref<CaseMaster[]>([]);
const caseId = ref("");
const accusedId = ref("");
const graphPreview = ref<string | null>(null);
const graphError = ref<string | null>(null);
const loadingGraph = ref(false);

const brief = ref<IntelligenceBriefResponse | null>(null);
const briefError = ref<string | null>(null);
const loadingBrief = ref(false);

const moClusters = ref<MoCluster[]>([]);
const moProvider = ref("");
const moTotal = ref(0);

const riskItems = ref<
  {
    scope_name: string | null;
    scope_id: number;
    risk_score: number;
    case_count: number;
    high_severity_share: number;
    top_crime_heads: string[];
  }[]
>([]);
const anomalies = ref<
  {
    anomaly_id: string;
    title: string;
    severity: string;
    kind: string;
    detail: string;
    score: number;
    case_master_ids: number[];
  }[]
>([]);

async function loadBrief() {
  loadingBrief.value = true;
  briefError.value = null;
  try {
    brief.value = await api.aiIntelligenceBrief({ horizon_days: 7 });
  } catch (e) {
    briefError.value =
      e instanceof Error ? e.message : "Failed to load intelligence brief";
  } finally {
    loadingBrief.value = false;
  }
}

onMounted(async () => {
  const [list, risk, anom, mo] = await Promise.all([
    api.listCases({ limit: 30 }).catch(() => ({ items: [] as CaseMaster[] })),
    api.aiPredictRisk({ horizon_days: 14 }).catch(() => null),
    api.aiAnomalies(10).catch(() => null),
    api.aiMoClusters({ min_size: 2, limit: 10 }).catch(() => null),
  ]);
  cases.value = list.items;
  if (list.items[0]) caseId.value = String(list.items[0].case_master_id);
  if (risk) riskItems.value = risk.items.slice(0, 8);
  if (anom) anomalies.value = anom.items;
  if (mo) {
    moClusters.value = mo.clusters;
    moProvider.value = mo.provider;
    moTotal.value = mo.total_cases_clustered;
  }
  void loadBrief();
});

async function previewGraph() {
  loadingGraph.value = true;
  graphError.value = null;
  graphPreview.value = null;
  try {
    const res = await api.aiGraphContext({
      case_id: caseId.value ? Number(caseId.value) : undefined,
      accused_id: accusedId.value ? Number(accusedId.value) : undefined,
      depth: 2,
    });
    graphPreview.value = [
      res.summary,
      "",
      `Engine: ${res.engine} · nodes ${res.node_count} · edges ${res.edge_count}`,
      res.neighbor_crime_nos.length
        ? `Neighbor FIRs: ${res.neighbor_crime_nos.slice(0, 15).join(", ")}`
        : "",
      res.linked_persons.length
        ? `Linked persons: ${res.linked_persons.slice(0, 10).join(", ")}`
        : "",
    ]
      .filter(Boolean)
      .join("\n");
  } catch (e) {
    const raw = e instanceof Error ? e.message : "Graph context failed";
    graphError.value = /Failed to fetch|Network error/i.test(raw)
      ? "Graph context timed out or was blocked. Retry, or use depth 1 on Network. " +
        "(AppSail has a ~30s limit; CORS errors often mask a timeout.)"
      : raw;
  } finally {
    loadingGraph.value = false;
  }
}
</script>

<template>
  <section class="cip-rise space-y-8">
    <div class="flex flex-wrap items-end justify-between gap-4">
      <div>
        <p class="cip-kicker">AI desk</p>
        <h1 class="cip-display mt-1 text-3xl text-[var(--cip-ink)]">
          Intelligence
        </h1>
        <p class="mt-1 max-w-2xl text-sm text-[var(--cip-muted)]">
          Strategic brief, modus-operandi clusters, Graph RAG, risk forecast, and
          Ask AI over FIR knowledge.
        </p>
      </div>
      <button
        type="button"
        class="cip-btn cip-btn-ghost disabled:opacity-50"
        :disabled="loadingBrief"
        @click="loadBrief"
      >
        {{ loadingBrief ? "Refreshing…" : "Refresh brief" }}
      </button>
    </div>

    <!-- Strategic brief -->
    <div class="cip-panel p-6 pl-7">
      <div class="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p class="cip-kicker">SCRB strategic brief</p>
          <h2 class="cip-display mt-1 text-2xl text-[var(--cip-ink)]">
            {{ brief?.title || "Weekly intelligence summary" }}
          </h2>
        </div>
        <p v-if="brief" class="text-xs text-[var(--cip-muted)]">
          Horizon {{ brief.horizon_days }}d ·
          {{ new Date(brief.generated_at).toLocaleString("en-IN") }}
        </p>
      </div>

      <p v-if="briefError" class="mt-3 text-sm text-[#9b2c1f]">{{ briefError }}</p>
      <p
        v-else-if="loadingBrief && !brief"
        class="mt-3 text-sm text-[var(--cip-muted)]"
      >
        Compiling brief…
      </p>
      <template v-else-if="brief">
        <p class="mt-4 text-base font-medium leading-relaxed text-[var(--cip-ink-soft)]">
          {{ brief.headline }}
        </p>
        <div class="mt-5 grid gap-4 md:grid-cols-2">
          <div
            v-for="(sec, i) in brief.sections"
            :key="i"
            class="border border-[rgba(197,212,216,0.65)] bg-[rgba(255,255,255,0.4)] px-4 py-3"
          >
            <h3 class="text-sm font-semibold text-[var(--cip-accent-deep)]">
              {{ sec.title }}
            </h3>
            <p class="mt-1.5 text-sm leading-relaxed text-[var(--cip-ink-soft)]">
              {{ sec.body }}
            </p>
          </div>
        </div>
        <div v-if="brief.recommended_actions.length" class="mt-5">
          <h3
            class="text-[0.65rem] font-semibold uppercase tracking-[0.14em] text-[var(--cip-muted)]"
          >
            Recommended actions
          </h3>
          <ol class="mt-2 list-decimal space-y-1.5 pl-5 text-sm text-[var(--cip-ink)]">
            <li v-for="(act, i) in brief.recommended_actions" :key="i">
              {{ act }}
            </li>
          </ol>
        </div>
      </template>
    </div>

    <!-- MO clusters + Ask AI / Graph -->
    <div class="grid gap-6 lg:grid-cols-2">
      <div class="space-y-4">
        <div class="cip-panel p-5 pl-6">
          <div class="flex flex-wrap items-baseline justify-between gap-2">
            <h2 class="cip-display text-xl text-[var(--cip-ink)]">
              MO clusters
            </h2>
            <span class="text-xs text-[var(--cip-muted)]">
              {{ moTotal }} FIRs · {{ moProvider || "heuristic" }}
            </span>
          </div>
          <p class="mt-1 text-xs text-[var(--cip-muted)]">
            Cases grouped by shared act/section tokens and brief-fact MO signals.
          </p>
          <ul class="mt-4 max-h-[28rem] space-y-3 overflow-y-auto">
            <li
              v-for="c in moClusters"
              :key="c.cluster_id"
              class="border border-[rgba(197,212,216,0.65)] bg-[rgba(255,255,255,0.45)] px-3 py-3"
            >
              <div class="flex items-start justify-between gap-2">
                <div>
                  <p class="text-sm font-semibold text-[var(--cip-ink)]">
                    {{ c.label }}
                  </p>
                  <p class="mt-0.5 font-mono text-[10px] text-[var(--cip-muted)]">
                    {{ c.mo_signature }}
                  </p>
                </div>
                <span class="cip-badge cip-badge-med shrink-0"
                  >{{ c.size }} cases</span
                >
              </div>
              <p
                v-if="c.similarity_note"
                class="mt-2 text-xs text-[var(--cip-ink-soft)]"
              >
                {{ c.similarity_note }}
              </p>
              <p
                v-if="c.districts.length"
                class="mt-1 text-[11px] text-[var(--cip-muted)]"
              >
                {{ c.districts.slice(0, 4).join(" · ") }}
              </p>
              <div class="mt-2 flex flex-wrap gap-2">
                <RouterLink
                  v-for="m in c.members.slice(0, 5)"
                  :key="m.case_master_id"
                  :to="`/cases/${m.case_master_id}`"
                  class="text-xs font-semibold text-[var(--cip-accent-deep)] underline-offset-2 hover:underline"
                >
                  {{ m.crime_no }}
                </RouterLink>
              </div>
            </li>
            <li
              v-if="!moClusters.length"
              class="py-4 text-sm text-[var(--cip-muted)]"
            >
              No MO clusters with current thresholds.
            </li>
          </ul>
        </div>

        <div class="cip-panel p-5 pl-6">
          <h2 class="cip-display text-xl text-[var(--cip-ink)]">Context seed</h2>
          <p class="mt-1 text-xs text-[var(--cip-muted)]">
            Optional case / accused scope for chat and Graph RAG preview.
          </p>
          <div class="mt-3 grid gap-3 sm:grid-cols-2">
            <label class="block text-sm">
              <span
                class="text-[0.7rem] font-semibold uppercase tracking-[0.12em] text-[var(--cip-muted)]"
                >Case</span
              >
              <select v-model="caseId" class="cip-field">
                <option value="">None</option>
                <option
                  v-for="c in cases"
                  :key="c.case_master_id"
                  :value="String(c.case_master_id)"
                >
                  {{ c.crime_no }}
                </option>
              </select>
            </label>
            <label class="block text-sm">
              <span
                class="text-[0.7rem] font-semibold uppercase tracking-[0.12em] text-[var(--cip-muted)]"
                >Accused id</span
              >
              <input
                v-model="accusedId"
                type="number"
                min="1"
                class="cip-field"
                placeholder="optional"
              />
            </label>
          </div>
          <button
            type="button"
            class="cip-btn cip-btn-ghost mt-3 disabled:opacity-50"
            :disabled="loadingGraph || (!caseId && !accusedId)"
            @click="previewGraph"
          >
            {{ loadingGraph ? "Loading…" : "Preview Graph RAG" }}
          </button>
          <p v-if="graphError" class="mt-2 text-sm text-[#9b2c1f]">
            {{ graphError }}
          </p>
          <pre
            v-if="graphPreview"
            class="mt-3 max-h-48 overflow-y-auto whitespace-pre-wrap border border-[var(--cip-line)] bg-[rgba(13,107,124,0.05)] p-3 text-xs text-[var(--cip-ink-soft)]"
            >{{ graphPreview }}</pre
          >
        </div>

        <AiChatPanel
          :case-master-id="caseId ? Number(caseId) : undefined"
          :accused-id="accusedId ? Number(accusedId) : undefined"
          title="Ask AI"
          default-question="What patterns link recent FIRs in this scope?"
        />
      </div>

      <div class="space-y-4">
        <div class="cip-panel p-5 pl-6">
          <h2 class="cip-display text-xl text-[var(--cip-ink)]">Risk forecast</h2>
          <ul class="mt-3 divide-y divide-[rgba(197,212,216,0.5)]">
            <li
              v-for="r in riskItems"
              :key="r.scope_id"
              class="flex justify-between gap-3 py-2.5 text-sm"
            >
              <div>
                <p class="font-semibold text-[var(--cip-ink)]">
                  {{ r.scope_name || `Scope ${r.scope_id}` }}
                </p>
                <p class="text-xs text-[var(--cip-muted)]">
                  {{ r.case_count }} cases ·
                  {{ Math.round(r.high_severity_share * 100) }}% high severity
                </p>
                <p
                  v-if="r.top_crime_heads?.length"
                  class="mt-0.5 text-[11px] text-[var(--cip-muted)]"
                >
                  {{ r.top_crime_heads.slice(0, 3).join(" · ") }}
                </p>
              </div>
              <span
                class="cip-display text-xl tabular-nums text-[var(--cip-accent-deep)]"
              >
                {{ r.risk_score.toFixed(0) }}
              </span>
            </li>
            <li
              v-if="!riskItems.length"
              class="py-4 text-sm text-[var(--cip-muted)]"
            >
              No risk scores
            </li>
          </ul>
        </div>

        <div class="cip-panel p-5 pl-6">
          <h2 class="cip-display text-xl text-[var(--cip-ink)]">Anomalies</h2>
          <ul class="mt-3 space-y-3">
            <li
              v-for="a in anomalies"
              :key="a.anomaly_id"
              class="border border-[rgba(197,212,216,0.65)] bg-[rgba(255,255,255,0.45)] px-3 py-2.5"
            >
              <div class="flex items-center gap-2">
                <span
                  class="cip-badge"
                  :class="
                    a.severity === 'high' ? 'cip-badge-high' : 'cip-badge-med'
                  "
                >
                  {{ a.severity }}
                </span>
                <span
                  class="text-[10px] font-semibold uppercase tracking-[0.12em] text-[var(--cip-muted)]"
                  >{{ a.kind }}</span
                >
              </div>
              <p class="mt-1 text-sm font-semibold text-[var(--cip-ink)]">
                {{ a.title }}
              </p>
              <p class="mt-0.5 text-xs text-[var(--cip-muted)]">{{ a.detail }}</p>
              <div
                v-if="a.case_master_ids?.length"
                class="mt-2 flex flex-wrap gap-2"
              >
                <RouterLink
                  v-for="id in a.case_master_ids.slice(0, 4)"
                  :key="id"
                  :to="`/cases/${id}`"
                  class="text-xs font-semibold text-[var(--cip-accent-deep)] underline-offset-2 hover:underline"
                >
                  Case {{ id }}
                </RouterLink>
              </div>
            </li>
            <li v-if="!anomalies.length" class="text-sm text-[var(--cip-muted)]">
              No anomalies
            </li>
          </ul>
        </div>
      </div>
    </div>
  </section>
</template>
