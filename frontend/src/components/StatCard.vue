<script setup lang="ts">
defineProps<{
  label: string;
  value: string | number;
  hint?: string;
  accent?: "teal" | "amber" | "ink";
}>();
</script>

<template>
  <div
    class="cip-stat"
    :class="{
      'cip-stat-amber': accent === 'amber',
      'cip-stat-ink': accent === 'ink',
    }"
  >
    <p
      class="relative z-[1] text-[0.65rem] font-semibold uppercase tracking-[0.16em] text-[var(--cip-muted)]"
    >
      {{ label }}
    </p>
    <p
      class="cip-display relative z-[1] mt-2 text-[1.75rem] font-medium tabular-nums leading-none text-[var(--cip-ink)]"
    >
      {{ value }}
    </p>
    <p v-if="hint" class="relative z-[1] mt-1.5 text-xs text-[var(--cip-muted)]">{{ hint }}</p>
  </div>
</template>
