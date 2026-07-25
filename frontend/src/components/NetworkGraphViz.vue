<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import {
  forceCenter,
  forceCollide,
  forceLink,
  forceManyBody,
  forceSimulation,
  type SimulationNodeDatum,
} from "d3-force";
import type { GraphEdge, GraphNode } from "@/types";

type SimNode = SimulationNodeDatum &
  GraphNode & { x: number; y: number; degree: number; r: number };
type SimLink = {
  source: SimNode | string;
  target: SimNode | string;
  relation: string;
  score: number;
};

const props = withDefaults(
  defineProps<{
    nodes: GraphNode[];
    edges: GraphEdge[];
    width?: number;
    height?: number;
    visibleTypes?: Record<string, boolean>;
    labelMode?: "auto" | "all" | "none";
  }>(),
  {
    width: 900,
    height: 560,
    labelMode: "auto",
  },
);

const emit = defineEmits<{
  selectNode: [node: GraphNode];
}>();

const selectedId = ref<string | null>(null);
const hoveredId = ref<string | null>(null);
const transform = ref({ x: 0, y: 0, k: 1 });
const draggingCanvas = ref(false);
let dragStart = { x: 0, y: 0, tx: 0, ty: 0 };
let sim: ReturnType<typeof forceSimulation<SimNode>> | null = null;

const drawnNodes = ref<SimNode[]>([]);
const drawnLinks = ref<
  { x1: number; y1: number; x2: number; y2: number; relation: string; sourceId: string; targetId: string }[]
>([]);

const W = () => props.width;
const H = () => props.height;

const typeColor: Record<string, string> = {
  case: "#0d6b7c",
  accused: "#c4782a",
  victim: "#2f6f8f",
  station: "#3d555c",
};

const edgeColor: Record<string, string> = {
  accused_of: "#0d6b7c",
  victim_of: "#2f6f8f",
  filed_at: "#7a8f94",
  same_person: "#c4782a",
  co_accused: "#a35d1e",
};

function shortLabel(n: GraphNode): string {
  if (n.type === "case") {
    const parts = n.label.split("/");
    return parts.length > 1 ? parts.slice(-2).join("/") : n.label;
  }
  if (n.type === "station") {
    return n.label.length > 22 ? `${n.label.slice(0, 20)}…` : n.label;
  }
  // Accused / victim: first + last (drop middle fluff), keep readable
  const parts = n.label.trim().split(/\s+/);
  if (parts.length >= 2) {
    return `${parts[0]} ${parts[parts.length - 1]}`;
  }
  return n.label.length > 16 ? `${n.label.slice(0, 14)}…` : n.label;
}

function fullLabel(n: GraphNode): string {
  if (typeof n.meta?.display === "string" && n.meta.display) {
    return n.meta.display;
  }
  const bits = [n.label];
  if (n.meta?.age_year != null) bits.push(`${n.meta.age_year}y`);
  if (n.meta?.gender_id) bits.push(String(n.meta.gender_id));
  if (n.meta?.person_id) bits.push(String(n.meta.person_id));
  return bits.join(" · ");
}

const typeOk = (t: string) => props.visibleTypes?.[t] !== false;

const filtered = computed(() => {
  const nodes = props.nodes.filter((n) => typeOk(n.type));
  const ids = new Set(nodes.map((n) => n.id));
  const edges = props.edges.filter((e) => ids.has(e.source) && ids.has(e.target));
  return { nodes, edges };
});

const focusIds = computed(() => {
  const id = selectedId.value || hoveredId.value;
  const set = new Set<string>();
  if (!id) return set;
  set.add(id);
  for (const e of filtered.value.edges) {
    if (e.source === id) set.add(e.target);
    if (e.target === id) set.add(e.source);
  }
  return set;
});

const hoveredNode = computed(() =>
  drawnNodes.value.find((n) => n.id === hoveredId.value) ?? null,
);

function isMutedNode(id: string): boolean {
  return focusIds.value.size > 1 && !focusIds.value.has(id);
}

function isMutedEdge(sourceId: string, targetId: string): boolean {
  return (
    focusIds.value.size > 1 &&
    !(focusIds.value.has(sourceId) && focusIds.value.has(targetId))
  );
}

function shouldShowLabel(n: SimNode): boolean {
  if (props.labelMode === "none") return false;
  if (props.labelMode === "all") return true;
  if (selectedId.value === n.id || hoveredId.value === n.id) return true;
  if (focusIds.value.size > 1 && focusIds.value.has(n.id)) return true;
  if (n.degree >= 3) return true;
  if (n.type === "case" && filtered.value.nodes.length <= 40) return true;
  if (filtered.value.nodes.length <= 22) return true;
  return false;
}

function runSimulation() {
  sim?.stop();
  const w = W();
  const h = H();
  const { nodes: srcNodes, edges: srcEdges } = filtered.value;

  const degree = new Map<string, number>();
  for (const e of srcEdges) {
    degree.set(e.source, (degree.get(e.source) ?? 0) + 1);
    degree.set(e.target, (degree.get(e.target) ?? 0) + 1);
  }

  const nodes: SimNode[] = srcNodes.map((n) => {
    const deg = degree.get(n.id) ?? 0;
    return {
      ...n,
      degree: deg,
      r: Math.min(22, 8 + Math.sqrt(deg + 1) * 3.2),
      x: w / 2 + (Math.random() - 0.5) * 120,
      y: h / 2 + (Math.random() - 0.5) * 120,
    };
  });

  const links: SimLink[] = srcEdges.map((e) => ({
    source: e.source,
    target: e.target,
    relation: e.relation,
    score: e.score,
  }));

  const nCount = Math.max(1, nodes.length);
  const charge = nCount > 80 ? -90 : nCount > 40 ? -160 : -280;
  const linkDist = nCount > 80 ? 48 : nCount > 40 ? 70 : 100;

  sim = forceSimulation(nodes)
    .force(
      "link",
      forceLink<SimNode, SimLink>(links)
        .id((d) => d.id)
        .distance(linkDist)
        .strength(0.45),
    )
    .force("charge", forceManyBody().strength(charge))
    .force("center", forceCenter(w / 2, h / 2))
    .force(
      "collide",
      forceCollide<SimNode>().radius((d) => d.r + 10),
    )
    .alpha(1)
    .on("tick", () => {
      drawnNodes.value = nodes.map((n) => ({ ...n }));
      drawnLinks.value = links.map((l) => {
        const s = l.source as SimNode;
        const t = l.target as SimNode;
        return {
          x1: s.x,
          y1: s.y,
          x2: t.x,
          y2: t.y,
          relation: l.relation,
          sourceId: s.id,
          targetId: t.id,
        };
      });
    });

  transform.value = {
    x: 0,
    y: 0,
    k: nCount > 100 ? 0.55 : nCount > 50 ? 0.75 : 1,
  };
}

function onNodeClick(n: SimNode) {
  selectedId.value = n.id;
  emit("selectNode", n);
}

function onWheel(ev: WheelEvent) {
  ev.preventDefault();
  const factor = ev.deltaY < 0 ? 1.08 : 0.92;
  const next = Math.min(3.5, Math.max(0.25, transform.value.k * factor));
  transform.value = { ...transform.value, k: next };
}

function onPointerDown(ev: PointerEvent) {
  if ((ev.target as HTMLElement).closest("[data-node]")) return;
  draggingCanvas.value = true;
  dragStart = {
    x: ev.clientX,
    y: ev.clientY,
    tx: transform.value.x,
    ty: transform.value.y,
  };
  (ev.currentTarget as HTMLElement).setPointerCapture(ev.pointerId);
}

function onPointerMove(ev: PointerEvent) {
  if (!draggingCanvas.value) return;
  transform.value = {
    ...transform.value,
    x: dragStart.tx + (ev.clientX - dragStart.x),
    y: dragStart.ty + (ev.clientY - dragStart.y),
  };
}

function onPointerUp() {
  draggingCanvas.value = false;
}

function resetView() {
  transform.value = { x: 0, y: 0, k: 1 };
  selectedId.value = null;
  runSimulation();
}

function selectExternal(id: string | null) {
  selectedId.value = id;
  const n = drawnNodes.value.find((x) => x.id === id) ?? props.nodes.find((x) => x.id === id);
  if (n) emit("selectNode", n);
}

defineExpose({ selectExternal, resetView });

onMounted(runSimulation);
watch(
  () => [props.nodes, props.edges, props.visibleTypes, props.labelMode],
  runSimulation,
  { deep: true },
);
onBeforeUnmount(() => sim?.stop());
</script>

<template>
  <div
    class="relative overflow-hidden border border-[var(--cip-line)] bg-[rgba(255,255,255,0.75)]"
    style="border-radius: 2px"
  >
    <div class="absolute left-3 top-3 z-10 flex flex-wrap gap-2 text-[11px]">
      <button
        type="button"
        class="cip-btn cip-btn-ghost !px-2 !py-1 text-[11px]"
        @click="resetView"
      >
        Reset view
      </button>
      <span class="rounded-sm bg-white/80 px-2 py-1 text-[var(--cip-muted)]">
        Scroll zoom · drag pan · hover for name
      </span>
    </div>

    <svg
      :viewBox="`0 0 ${W()} ${H()}`"
      class="h-[32rem] w-full touch-none md:h-[36rem]"
      role="img"
      aria-label="Link analysis graph"
      style="background:
        radial-gradient(ellipse at 30% 20%, rgba(13,107,124,0.08), transparent 50%),
        radial-gradient(ellipse at 80% 70%, rgba(196,120,42,0.07), transparent 45%),
        #f3f7f6"
      @wheel="onWheel"
      @pointerdown="onPointerDown"
      @pointermove="onPointerMove"
      @pointerup="onPointerUp"
      @pointerleave="onPointerUp"
    >
      <g :transform="`translate(${transform.x} ${transform.y}) scale(${transform.k})`">
        <line
          v-for="(l, i) in drawnLinks"
          :key="i"
          :x1="l.x1"
          :y1="l.y1"
          :x2="l.x2"
          :y2="l.y2"
          :stroke="edgeColor[l.relation] ?? '#9bb4ba'"
          :stroke-width="l.relation === 'same_person' ? 2.4 : 1.4"
          :stroke-opacity="
            isMutedEdge(l.sourceId, l.targetId)
              ? 0.1
              : l.relation === 'same_person'
                ? 0.95
                : 0.72
          "
          :stroke-dasharray="l.relation === 'filed_at' ? '4 3' : undefined"
        />

        <g
          v-for="n in drawnNodes"
          :key="n.id"
          data-node
          class="cursor-pointer"
          @click.stop="onNodeClick(n)"
          @pointerenter="hoveredId = n.id"
          @pointerleave="hoveredId = null"
        >
          <circle
            v-if="selectedId === n.id || hoveredId === n.id"
            :cx="n.x"
            :cy="n.y"
            :r="n.r + 6"
            fill="none"
            stroke="#c4782a"
            stroke-width="2"
            stroke-opacity="0.75"
          />
          <circle
            :cx="n.x"
            :cy="n.y"
            :r="n.r"
            :fill="typeColor[n.type] ?? '#5a6f76'"
            :opacity="isMutedNode(n.id) ? 0.2 : 1"
            stroke="#f7faf9"
            stroke-width="2"
          />
          <text
            v-if="shouldShowLabel(n)"
            :x="n.x"
            :y="n.y + n.r + 14"
            text-anchor="middle"
            fill="#0a2a32"
            :font-size="selectedId === n.id || hoveredId === n.id ? 12 : 11"
            font-weight="600"
            style="font-family: Outfit, sans-serif; paint-order: stroke; stroke: #f3f7f6; stroke-width: 3px"
          >
            {{ shortLabel(n) }}
          </text>
        </g>
      </g>
    </svg>

    <div
      v-if="hoveredNode"
      class="pointer-events-none absolute bottom-3 left-3 max-w-sm rounded-sm border border-[var(--cip-line)] bg-white/95 px-3 py-2 text-xs"
    >
      <p
        class="font-semibold uppercase tracking-[0.12em] text-[var(--cip-muted)]"
        style="font-size: 10px"
      >
        {{ hoveredNode.type }} · {{ hoveredNode.degree }} links
      </p>
      <p class="mt-0.5 text-sm font-semibold text-[var(--cip-ink)]">
        {{ fullLabel(hoveredNode) }}
      </p>
    </div>

    <div
      class="flex flex-wrap items-center gap-x-4 gap-y-2 border-t border-[var(--cip-line)] px-4 py-2.5 text-[11px] text-[var(--cip-muted)]"
    >
      <span
        v-for="(color, type) in typeColor"
        :key="type"
        class="inline-flex items-center gap-1.5"
      >
        <span
          class="inline-block h-2.5 w-2.5"
          style="border-radius: 2px"
          :style="{ background: color }"
        />
        {{ type }}
      </span>
      <span class="mx-1 opacity-40">|</span>
      <span
        v-for="(color, rel) in edgeColor"
        :key="rel"
        class="inline-flex items-center gap-1.5"
      >
        <span class="inline-block h-0.5 w-3" :style="{ background: color }" />
        {{ rel }}
      </span>
    </div>
  </div>
</template>
