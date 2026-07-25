<script setup lang="ts">
import { computed } from "vue";

const props = withDefaults(
  defineProps<{
    points: number[];
    labels?: string[];
    height?: number;
    fill?: string;
    stroke?: string;
  }>(),
  {
    height: 160,
    fill: "rgba(13, 107, 124, 0.18)",
    stroke: "var(--cip-accent-deep)",
  },
);

const path = computed(() => {
  const vals = props.points.length ? props.points : [0];
  const max = Math.max(1, ...vals);
  const min = Math.min(0, ...vals);
  const range = max - min || 1;
  const n = vals.length;
  const W = 100;
  const H = 100;
  const padY = 8;
  const padX = 2;
  const coords = vals.map((v, i) => {
    const x = padX + (n === 1 ? W / 2 : (i / (n - 1)) * (W - padX * 2));
    const y = H - padY - ((v - min) / range) * (H - padY * 2);
    return { x, y, v };
  });
  const line = coords
    .map((c, i) => `${i === 0 ? "M" : "L"} ${c.x.toFixed(2)} ${c.y.toFixed(2)}`)
    .join(" ");
  const area = `${line} L ${coords[coords.length - 1]?.x ?? 0} ${H - padY} L ${coords[0]?.x ?? 0} ${H - padY} Z`;
  return { line, area, coords, max };
});
</script>

<template>
  <div class="w-full">
    <svg
      viewBox="0 0 100 100"
      class="w-full"
      :style="{ height: `${height}px` }"
      preserveAspectRatio="none"
      role="img"
    >
      <defs>
        <linearGradient id="cipAreaGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="var(--cip-accent)" stop-opacity="0.35" />
          <stop offset="100%" stop-color="var(--cip-accent)" stop-opacity="0.02" />
        </linearGradient>
      </defs>
      <path :d="path.area" fill="url(#cipAreaGrad)" class="cip-area-in" />
      <path
        :d="path.line"
        fill="none"
        :stroke="stroke"
        stroke-width="1.4"
        stroke-linejoin="round"
        stroke-linecap="round"
        vector-effect="non-scaling-stroke"
        class="cip-line-draw"
      />
    </svg>
    <div
      v-if="labels?.length"
      class="mt-1 flex justify-between px-0.5 text-[0.62rem] uppercase tracking-wide text-[var(--cip-muted)]"
    >
      <span>{{ labels[0] }}</span>
      <span v-if="labels.length > 1">{{ labels[labels.length - 1] }}</span>
    </div>
  </div>
</template>
