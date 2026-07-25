<script setup lang="ts">
import { computed } from "vue";

const props = withDefaults(
  defineProps<{
    items: { label: string; count: number }[];
    maxBars?: number;
    height?: number;
  }>(),
  { maxBars: 8, height: 240 },
);

const palette = [
  "#064552",
  "#0d6b7c",
  "#c4782a",
  "#1a7a6d",
  "#3d6b8a",
  "#8a5a2b",
  "#2f6f7a",
  "#b85c38",
];

const W = 420;
const H = 240;
const padL = 8;
const padR = 8;
const padT = 28;
const padB = 52;

const bars = computed(() => {
  const sliced = props.items.slice(0, props.maxBars);
  const max = Math.max(1, ...sliced.map((b) => b.count));
  const n = sliced.length || 1;
  const usable = W - padL - padR;
  const gap = 10;
  const bw = Math.max(18, (usable - gap * (n - 1)) / n);
  const chartH = H - padT - padB;
  return sliced.map((b, i) => {
    const h = Math.max(4, (b.count / max) * chartH);
    const x = padL + i * (bw + gap);
    const y = padT + chartH - h;
    const short =
      b.label.length > 14 ? `${b.label.slice(0, 12)}…` : b.label;
    return {
      ...b,
      x,
      y,
      w: bw,
      h,
      short,
      color: palette[i % palette.length],
      labelX: x + bw / 2,
    };
  });
});
</script>

<template>
  <div class="w-full overflow-x-auto">
    <svg
      :viewBox="`0 0 ${W} ${H}`"
      class="mx-auto w-full max-w-full"
      :style="{ minHeight: `${height}px` }"
      role="img"
      aria-label="Vertical bar chart"
    >
      <line
        :x1="padL"
        :x2="W - padR"
        :y1="H - padB"
        :y2="H - padB"
        stroke="rgba(10,42,50,0.14)"
        stroke-width="1"
      />
      <g v-for="(b, i) in bars" :key="b.label">
        <rect
          :x="b.x"
          :y="b.y"
          :width="b.w"
          :height="b.h"
          :fill="b.color"
          rx="2"
          class="cip-bar-grow"
          :style="{ animationDelay: `${i * 50}ms` }"
        >
          <title>{{ b.label }}: {{ b.count }}</title>
        </rect>
        <text
          :x="b.labelX"
          :y="b.y - 8"
          text-anchor="middle"
          font-size="12"
          fill="#1a4550"
          font-family="var(--font-ui)"
          font-weight="600"
        >
          {{ b.count }}
        </text>
        <text
          :x="b.labelX"
          :y="H - padB + 16"
          text-anchor="middle"
          font-size="10"
          fill="#5a6f76"
          font-family="var(--font-ui)"
        >
          <tspan
            v-for="(line, li) in b.short.split(' ')"
            :key="li"
            :x="b.labelX"
            :dy="li === 0 ? 0 : 11"
          >
            {{ line }}
          </tspan>
        </text>
      </g>
    </svg>
    <p v-if="!bars.length" class="py-8 text-center text-sm text-[var(--cip-muted)]">No data</p>
  </div>
</template>
