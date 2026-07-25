<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{
  items: { label: string; count: number }[];
  maxBars?: number;
}>();

const bars = computed(() => {
  const sliced = props.items.slice(0, props.maxBars ?? 8);
  const max = Math.max(1, ...sliced.map((b) => b.count));
  return sliced.map((b, i) => ({
    ...b,
    pct: Math.round((b.count / max) * 100),
    delay: `${i * 40}ms`,
  }));
});
</script>

<template>
  <ul class="space-y-3">
    <li v-for="b in bars" :key="b.label" class="text-sm">
      <div class="mb-1.5 flex justify-between gap-2">
        <span class="truncate font-medium text-[var(--cip-ink-soft)]">{{ b.label }}</span>
        <span class="shrink-0 tabular-nums text-[var(--cip-muted)]">{{ b.count }}</span>
      </div>
      <div class="h-1.5 overflow-hidden rounded-sm bg-[rgba(13,107,124,0.1)]">
        <div
          class="h-full rounded-sm origin-left"
          style="
            background: linear-gradient(90deg, var(--cip-accent-deep), var(--cip-signal));
            transition: width 0.7s cubic-bezier(0.22, 1, 0.36, 1);
          "
          :style="{ width: `${b.pct}%`, transitionDelay: b.delay }"
        />
      </div>
    </li>
    <li v-if="!bars.length" class="text-sm text-[var(--cip-muted)]">No data</li>
  </ul>
</template>
