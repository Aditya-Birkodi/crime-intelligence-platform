<script setup lang="ts">
import { computed } from "vue";

const props = withDefaults(
  defineProps<{
    items: { label: string; count: number; hint?: string }[];
    maxBars?: number;
  }>(),
  { maxBars: 8 },
);

const bars = computed(() => {
  const sliced = props.items.slice(0, props.maxBars);
  const max = Math.max(1, ...sliced.map((b) => b.count));
  return sliced.map((b, i) => ({
    ...b,
    pct: Math.round((b.count / max) * 100),
    delay: `${i * 40}ms`,
    rank: i + 1,
  }));
});
</script>

<template>
  <ul class="space-y-3.5">
    <li v-for="b in bars" :key="b.label" class="text-sm">
      <div class="mb-1.5 flex items-end justify-between gap-2">
        <div class="min-w-0 flex items-baseline gap-2">
          <span class="cip-display text-lg tabular-nums text-[var(--cip-signal)]">
            {{ String(b.rank).padStart(2, "0") }}
          </span>
          <div class="min-w-0">
            <p class="truncate font-medium text-[var(--cip-ink-soft)]">{{ b.label }}</p>
            <p v-if="b.hint" class="truncate text-[0.7rem] text-[var(--cip-muted)]">{{ b.hint }}</p>
          </div>
        </div>
        <span class="cip-display shrink-0 text-lg tabular-nums text-[var(--cip-ink)]">
          {{ b.count }}
        </span>
      </div>
      <div class="h-2 overflow-hidden rounded-sm bg-[rgba(13,107,124,0.1)]">
        <div
          class="h-full rounded-sm origin-left"
          style="
            background: linear-gradient(90deg, var(--cip-accent-deep), var(--cip-signal));
            transition: width 0.75s cubic-bezier(0.22, 1, 0.36, 1);
          "
          :style="{ width: `${b.pct}%`, transitionDelay: b.delay }"
        />
      </div>
    </li>
    <li v-if="!bars.length" class="text-sm text-[var(--cip-muted)]">No data</li>
  </ul>
</template>
