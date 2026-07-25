<script setup lang="ts">
import { computed } from "vue";

const props = withDefaults(
  defineProps<{
    items: { label: string; count: number }[];
    centerLabel?: string;
    size?: number;
  }>(),
  { centerLabel: "Total", size: 200 },
);

const palette = [
  "#064552",
  "#0d6b7c",
  "#c4782a",
  "#1a7a6d",
  "#3d6b8a",
  "#8a5a2b",
];

const total = computed(() =>
  props.items.reduce((s, i) => s + Math.max(0, i.count), 0),
);

const slices = computed(() => {
  const t = total.value || 1;
  let angle = -Math.PI / 2;
  const r = 42;
  const ir = 26;
  const cx = 50;
  const cy = 50;
  return props.items
    .filter((i) => i.count > 0)
    .map((item, idx) => {
      const frac = item.count / t;
      const sweep = frac * Math.PI * 2;
      const a0 = angle;
      const a1 = angle + sweep;
      angle = a1;
      const large = sweep > Math.PI ? 1 : 0;
      const x0 = cx + r * Math.cos(a0);
      const y0 = cy + r * Math.sin(a0);
      const x1 = cx + r * Math.cos(a1);
      const y1 = cy + r * Math.sin(a1);
      const xi0 = cx + ir * Math.cos(a1);
      const yi0 = cy + ir * Math.sin(a1);
      const xi1 = cx + ir * Math.cos(a0);
      const yi1 = cy + ir * Math.sin(a0);
      const d = [
        `M ${x0} ${y0}`,
        `A ${r} ${r} 0 ${large} 1 ${x1} ${y1}`,
        `L ${xi0} ${yi0}`,
        `A ${ir} ${ir} 0 ${large} 0 ${xi1} ${yi1}`,
        "Z",
      ].join(" ");
      return {
        ...item,
        d,
        color: palette[idx % palette.length],
        pct: Math.round(frac * 100),
      };
    });
});
</script>

<template>
  <div class="flex flex-col items-center gap-4 sm:flex-row sm:items-center sm:gap-6">
    <div class="relative shrink-0" :style="{ width: `${size}px`, height: `${size}px` }">
      <svg viewBox="0 0 100 100" class="h-full w-full cip-donut-spin" role="img">
        <circle cx="50" cy="50" r="42" fill="none" stroke="rgba(13,107,124,0.08)" stroke-width="16" />
        <path
          v-for="(s, i) in slices"
          :key="s.label"
          :d="s.d"
          :fill="s.color"
          class="cip-slice-in"
          :style="{ animationDelay: `${i * 60}ms` }"
        >
          <title>{{ s.label }}: {{ s.count }} ({{ s.pct }}%)</title>
        </path>
      </svg>
      <div class="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
        <p class="text-[0.6rem] font-semibold uppercase tracking-[0.16em] text-[var(--cip-muted)]">
          {{ centerLabel }}
        </p>
        <p class="cip-display text-2xl tabular-nums text-[var(--cip-ink)]">{{ total || "—" }}</p>
      </div>
    </div>
    <ul class="w-full min-w-0 space-y-2.5">
      <li
        v-for="s in slices"
        :key="s.label"
        class="flex items-center justify-between gap-3 text-sm"
      >
        <span class="flex min-w-0 items-center gap-2">
          <span class="h-2.5 w-2.5 shrink-0 rounded-sm" :style="{ background: s.color }" />
          <span class="truncate text-[var(--cip-ink-soft)]">{{ s.label }}</span>
        </span>
        <span class="shrink-0 tabular-nums text-[var(--cip-muted)]">
          {{ s.count }}
          <span class="text-[var(--cip-accent)]">· {{ s.pct }}%</span>
        </span>
      </li>
      <li v-if="!slices.length" class="text-sm text-[var(--cip-muted)]">No data</li>
    </ul>
  </div>
</template>
