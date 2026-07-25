<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { RouterLink, useRoute, useRouter } from "vue-router";
import { api } from "@/services/api";
import NetworkGraphViz from "@/components/NetworkGraphViz.vue";
import type {
  CaseMaster,
  GraphNode,
  NetworkGraphResponse,
  OffenderProfile,
} from "@/types";

const route = useRoute();
const router = useRouter();
const graphRef = ref<InstanceType<typeof NetworkGraphViz> | null>(null);

const loading = ref(true);
const error = ref<string | null>(null);
const graph = ref<NetworkGraphResponse | null>(null);
const cases = ref<CaseMaster[]>([]);
const seedCaseId = ref("");
const seedAccusedId = ref("");
const depth = ref(2);
const selectedNode = ref<GraphNode | null>(null);
const offender = ref<OffenderProfile | null>(null);
const offenderLoading = ref(false);
const rosterQuery = ref("");
const labelMode = ref<"auto" | "all" | "none">("auto");

const visibleTypes = ref({
  case: true,
  accused: true,
  victim: true,
  station: true,
});

const edgeSummary = computed(() => {
  if (!graph.value) return [] as { relation: string; count: number }[];
  const counts = new Map<string, number>();
  for (const e of graph.value.edges) {
    counts.set(e.relation, (counts.get(e.relation) ?? 0) + 1);
  }
  return [...counts.entries()]
    .map(([relation, count]) => ({ relation, count }))
    .sort((a, b) => b.count - a.count);
});

const typeCounts = computed(() => {
  const c = { case: 0, accused: 0, victim: 0, station: 0 };
  for (const n of graph.value?.nodes ?? []) {
    if (n.type in c) c[n.type as keyof typeof c] += 1;
  }
  return c;
});

const degreeMap = computed(() => {
  const m = new Map<string, number>();
  for (const e of graph.value?.edges ?? []) {
    m.set(e.source, (m.get(e.source) ?? 0) + 1);
    m.set(e.target, (m.get(e.target) ?? 0) + 1);
  }
  return m;
});

const roster = computed(() => {
  const q = rosterQuery.value.trim().toLowerCase();
  const nodes = [...(graph.value?.nodes ?? [])]
    .filter((n) => visibleTypes.value[n.type as keyof typeof visibleTypes.value] !== false)
    .filter((n) => {
      if (!q) return true;
      return (
        n.label.toLowerCase().includes(q) ||
        n.id.toLowerCase().includes(q) ||
        String(n.meta?.person_id ?? "")
          .toLowerCase()
          .includes(q)
      );
    })
    .sort((a, b) => (degreeMap.value.get(b.id) ?? 0) - (degreeMap.value.get(a.id) ?? 0));
  return nodes.slice(0, 80);
});

const hubCases = computed(() =>
  cases.value.filter((c) =>
    /P100|RING|FBR|H2|theft|fraud|assault/i.test(
      `${c.crime_no} ${c.brief_facts ?? ""}`,
    ),
  ),
);

async function loadSeedCases() {
  const res = await api.listCases({ limit: 100 });
  cases.value = res.items;
  if (!seedCaseId.value && res.items[0]) {
    // Prefer a linked demo FIR when available
    const preferred =
      res.items.find((c) => /P100|RING3|FBR1/i.test(c.brief_facts ?? "")) ??
      res.items.find((c) => c.case_master_id <= 30) ??
      res.items[0];
    seedCaseId.value = String(preferred.case_master_id);
  }
}

async function loadGraph() {
  loading.value = true;
  error.value = null;
  offender.value = null;
  selectedNode.value = null;
  try {
    const caseId = seedCaseId.value ? Number(seedCaseId.value) : undefined;
    const accusedId = seedAccusedId.value ? Number(seedAccusedId.value) : undefined;
    if (!caseId && !accusedId) {
      error.value = "Pick a case or accused id to seed the graph.";
      graph.value = null;
      return;
    }
    graph.value = await api.getNetworkGraph({
      case_id: caseId,
      accused_id: accusedId,
      depth: depth.value,
    });

    await router.replace({
      query: {
        ...(caseId ? { case_id: String(caseId) } : {}),
        ...(accusedId ? { accused_id: String(accusedId) } : {}),
        depth: String(depth.value),
      },
    });
  } catch (e) {
    error.value = e instanceof Error ? e.message : "Failed to load network graph";
    graph.value = null;
  } finally {
    loading.value = false;
  }
}

async function onSelectNode(node: GraphNode) {
  selectedNode.value = node;
  offender.value = null;
  if (node.type !== "accused") return;
  const metaId = node.meta?.accused_master_id ?? node.id.replace(/^accused:/, "");
  const id = Number(metaId);
  if (!Number.isFinite(id)) return;
  offenderLoading.value = true;
  try {
    offender.value = await api.getOffenderProfile(id);
  } catch {
    offender.value = null;
  } finally {
    offenderLoading.value = false;
  }
}

function pickFromRoster(n: GraphNode) {
  graphRef.value?.selectExternal(n.id);
  void onSelectNode(n);
}

onMounted(async () => {
  try {
    if (route.query.case_id) seedCaseId.value = String(route.query.case_id);
    if (route.query.accused_id) seedAccusedId.value = String(route.query.accused_id);
    if (route.query.depth) depth.value = Number(route.query.depth) || 2;
    await loadSeedCases();
    await loadGraph();
  } catch (e) {
    error.value = e instanceof Error ? e.message : "Failed to initialize network";
    loading.value = false;
  }
});

watch(depth, () => {
  if (seedCaseId.value || seedAccusedId.value) void loadGraph();
});
</script>

<template>
  <section class="cip-rise space-y-7">
    <div class="flex flex-wrap items-end justify-between gap-4">
      <div>
        <p class="cip-kicker">Graph</p>
        <h1 class="cip-display mt-1 text-3xl text-[var(--cip-ink)]">Link analysis</h1>
        <p class="mt-1 max-w-2xl text-sm text-[var(--cip-muted)]">
          Ego network of FIRs, accused, victims, and stations. Hover for full names; click an
          accused for offender profile. Dense graphs: zoom, pan, and filter types.
        </p>
      </div>
      <p v-if="graph" class="text-sm text-[var(--cip-muted)]">
        {{ graph.nodes.length }} nodes · {{ graph.edges.length }} edges
      </p>
    </div>

    <div class="cip-panel grid gap-3 p-4 pl-5 sm:grid-cols-2 lg:grid-cols-5">
      <label class="block text-sm lg:col-span-2">
        <span class="text-[0.7rem] font-semibold uppercase tracking-[0.12em] text-[var(--cip-muted)]">
          Seed case
        </span>
        <select
          v-model="seedCaseId"
          class="cip-field"
          @change="seedAccusedId = ''"
        >
          <option value="">—</option>
          <option
            v-for="c in cases"
            :key="c.case_master_id"
            :value="String(c.case_master_id)"
          >
            {{ c.crime_no }} · #{{ c.case_master_id }}
          </option>
        </select>
      </label>
      <label class="block text-sm">
        <span class="text-[0.7rem] font-semibold uppercase tracking-[0.12em] text-[var(--cip-muted)]">
          Accused id
        </span>
        <input
          v-model="seedAccusedId"
          type="number"
          min="1"
          placeholder="optional"
          class="cip-field"
          @input="seedCaseId = ''"
        />
      </label>
      <label class="block text-sm">
        <span class="text-[0.7rem] font-semibold uppercase tracking-[0.12em] text-[var(--cip-muted)]">
          Depth
        </span>
        <select v-model.number="depth" class="cip-field">
          <option :value="1">1 · tight</option>
          <option :value="2">2 · linked</option>
          <option :value="3">3 · wide</option>
        </select>
      </label>
      <div class="flex items-end">
        <button
          type="button"
          class="cip-btn cip-btn-primary w-full"
          :disabled="loading"
          @click="loadGraph"
        >
          {{ loading ? "Loading…" : "Load graph" }}
        </button>
      </div>
    </div>

    <div v-if="hubCases.length" class="flex flex-wrap gap-2">
      <span class="text-xs font-semibold uppercase tracking-[0.12em] text-[var(--cip-muted)] self-center">
        Try hubs
      </span>
      <button
        v-for="c in hubCases.slice(0, 6)"
        :key="c.case_master_id"
        type="button"
        class="cip-btn cip-btn-ghost !px-2.5 !py-1 text-xs"
        @click="
          seedCaseId = String(c.case_master_id);
          seedAccusedId = '';
          loadGraph();
        "
      >
        {{ c.crime_no.split('/').slice(-2).join('/') }}
      </button>
    </div>

    <p v-if="error" class="text-sm text-[#9b2c1f]">{{ error }}</p>

    <template v-if="graph">
      <div class="flex flex-wrap items-center gap-4 text-sm">
        <label
          v-for="(_on, type) in visibleTypes"
          :key="type"
          class="inline-flex items-center gap-1.5"
        >
          <input v-model="visibleTypes[type as keyof typeof visibleTypes]" type="checkbox" class="accent-[var(--cip-accent)]" />
          <span class="capitalize">{{ type }}</span>
          <span class="tabular-nums text-[var(--cip-muted)]">
            ({{ typeCounts[type as keyof typeof typeCounts] }})
          </span>
        </label>
        <label class="ml-auto inline-flex items-center gap-2 text-xs text-[var(--cip-muted)]">
          Labels
          <select v-model="labelMode" class="cip-field !mt-0 !w-auto !py-1 text-xs">
            <option value="auto">Auto</option>
            <option value="all">All</option>
            <option value="none">None</option>
          </select>
        </label>
      </div>

      <div class="grid gap-4 xl:grid-cols-[1fr_22rem]">
        <NetworkGraphViz
          ref="graphRef"
          :nodes="graph.nodes"
          :edges="graph.edges"
          :visible-types="visibleTypes"
          :label-mode="labelMode"
          @select-node="onSelectNode"
        />

        <aside class="space-y-4">
          <div class="cip-panel p-4 pl-5">
            <h2 class="cip-display text-lg text-[var(--cip-ink)]">Edge mix</h2>
            <ul class="mt-3 space-y-1.5 text-sm">
              <li
                v-for="e in edgeSummary"
                :key="e.relation"
                class="flex justify-between gap-2"
              >
                <span class="text-[var(--cip-ink-soft)]">{{ e.relation }}</span>
                <span class="tabular-nums text-[var(--cip-muted)]">{{ e.count }}</span>
              </li>
            </ul>
          </div>

          <div class="cip-panel p-4 pl-5">
            <h2 class="cip-display text-lg text-[var(--cip-ink)]">Node roster</h2>
            <input
              v-model="rosterQuery"
              type="search"
              placeholder="Search name / person id…"
              class="cip-field"
            />
            <ul class="mt-3 max-h-56 space-y-1 overflow-y-auto text-sm">
              <li v-for="n in roster" :key="n.id">
                <button
                  type="button"
                  class="flex w-full items-start justify-between gap-2 rounded-sm px-1.5 py-1 text-left hover:bg-[rgba(13,107,124,0.06)]"
                  :class="selectedNode?.id === n.id ? 'bg-[rgba(13,107,124,0.1)]' : ''"
                  @click="pickFromRoster(n)"
                >
                  <span class="min-w-0">
                    <span class="text-[10px] uppercase tracking-wide text-[var(--cip-muted)]">{{ n.type }}</span>
                    <span class="block truncate font-medium text-[var(--cip-ink)]">{{ n.label }}</span>
                    <span
                      v-if="n.type === 'accused' || n.type === 'victim'"
                      class="block truncate text-[11px] text-[var(--cip-muted)]"
                    >
                      <template v-if="n.meta?.age_year != null">{{ n.meta.age_year }}y</template>
                      <template v-if="n.meta?.gender_id">
                        <template v-if="n.meta?.age_year != null"> · </template>{{ n.meta.gender_id }}
                      </template>
                      <template v-if="n.meta?.person_id">
                        <template v-if="n.meta?.age_year != null || n.meta?.gender_id"> · </template>
                        {{ n.meta.person_id }}
                      </template>
                    </span>
                  </span>
                  <span class="shrink-0 tabular-nums text-xs text-[var(--cip-muted)]">
                    {{ degreeMap.get(n.id) ?? 0 }}
                  </span>
                </button>
              </li>
              <li v-if="!roster.length" class="text-[var(--cip-muted)]">No matches</li>
            </ul>
          </div>

          <div class="cip-panel p-4 pl-5">
            <h2 class="cip-display text-lg text-[var(--cip-ink)]">Selection</h2>
            <template v-if="selectedNode">
              <p class="mt-2 text-[0.65rem] uppercase tracking-[0.14em] text-[var(--cip-muted)]">
                {{ selectedNode.type }}
              </p>
              <p class="mt-1 text-sm font-semibold text-[var(--cip-ink)]">{{ selectedNode.label }}</p>
              <p
                v-if="selectedNode.type === 'accused' || selectedNode.type === 'victim'"
                class="mt-1 text-xs text-[var(--cip-muted)]"
              >
                <span v-if="selectedNode.meta?.age_year != null">{{ selectedNode.meta.age_year }}y</span>
                <span v-if="selectedNode.meta?.gender_id">
                  <span v-if="selectedNode.meta?.age_year != null"> · </span>{{ selectedNode.meta.gender_id }}
                </span>
              </p>
              <p v-if="selectedNode.meta?.person_id" class="mt-1 text-xs text-[var(--cip-accent)]">
                person {{ selectedNode.meta.person_id }}
              </p>
              <p
                v-if="selectedNode.meta?.brief_facts"
                class="mt-2 line-clamp-4 text-xs leading-relaxed text-[var(--cip-muted)]"
              >
                {{ selectedNode.meta.brief_facts }}
              </p>
              <RouterLink
                v-if="selectedNode.type === 'case' && selectedNode.meta?.case_master_id"
                :to="`/cases/${selectedNode.meta.case_master_id}`"
                class="mt-3 inline-block text-sm font-semibold text-[var(--cip-accent-deep)] underline-offset-2 hover:underline"
              >
                Open case →
              </RouterLink>
            </template>
            <p v-else class="mt-2 text-sm text-[var(--cip-muted)]">Click a node or roster row</p>
          </div>

          <div v-if="offenderLoading || offender" class="cip-panel p-4 pl-5">
            <h2 class="cip-display text-lg text-[var(--cip-ink)]">Offender profile</h2>
            <p v-if="offenderLoading" class="mt-2 text-sm text-[var(--cip-muted)]">Loading…</p>
            <template v-else-if="offender">
              <p class="mt-2 font-semibold text-[var(--cip-ink)]">{{ offender.accused_name }}</p>
              <p class="text-xs text-[var(--cip-muted)]">
                <span v-if="offender.age_year != null">{{ offender.age_year }}y</span>
                <span v-if="offender.gender_id">
                  <span v-if="offender.age_year != null"> · </span>{{ offender.gender_id }}
                </span>
                <span v-if="offender.person_id">
                  <span v-if="offender.age_year != null || offender.gender_id"> · </span>{{ offender.person_id }}
                </span>
                · {{ offender.case_count }} cases
              </p>
              <div v-if="offender.modus_operandi.length" class="mt-3">
                <p class="text-[0.65rem] uppercase tracking-[0.12em] text-[var(--cip-muted)]">
                  Modus operandi
                </p>
                <ul class="mt-1 space-y-1 text-xs text-[var(--cip-ink-soft)]">
                  <li v-for="(m, i) in offender.modus_operandi.slice(0, 5)" :key="i">{{ m }}</li>
                </ul>
              </div>
              <ul class="mt-3 space-y-1.5 text-sm">
                <li v-for="c in offender.cases.slice(0, 8)" :key="c.case_master_id">
                  <RouterLink
                    :to="`/cases/${c.case_master_id}`"
                    class="font-mono text-xs hover:underline"
                  >
                    {{ c.crime_no }}
                  </RouterLink>
                </li>
              </ul>
            </template>
          </div>
        </aside>
      </div>
    </template>
  </section>
</template>
