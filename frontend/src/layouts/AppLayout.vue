<script setup lang="ts">
import { RouterLink, RouterView } from "vue-router";
import { baseUrl } from "@/services/api";

const links = [
  { to: "/", label: "Home" },
  { to: "/cases", label: "Cases" },
  { to: "/map", label: "Map" },
  { to: "/network", label: "Network" },
];
</script>

<template>
  <div class="min-h-screen">
    <header class="border-b border-slate-200/80 bg-white/80 backdrop-blur">
      <div
        class="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4 px-6 py-4"
      >
        <div>
          <p class="text-xs uppercase tracking-[0.2em] text-slate-500">
            Karnataka State Police
          </p>
          <RouterLink to="/" class="text-lg font-semibold text-slate-900">
            Crime Intelligence Platform
          </RouterLink>
        </div>
        <nav class="flex flex-wrap gap-1">
          <RouterLink
            v-for="link in links"
            :key="link.to"
            :to="link.to"
            class="rounded-md px-3 py-1.5 text-sm text-slate-600 transition hover:bg-slate-100 hover:text-slate-900"
            active-class="!bg-slate-900 !text-white"
          >
            {{ link.label }}
          </RouterLink>
        </nav>
      </div>
      <div
        class="border-t border-slate-100 bg-slate-50/80 px-6 py-1.5 text-xs text-slate-500"
      >
        <div class="mx-auto max-w-6xl truncate">
          API:
          <code class="text-slate-700">{{ baseUrl }}</code>
        </div>
      </div>
    </header>
    <main class="mx-auto max-w-6xl px-6 py-8">
      <RouterView />
    </main>
  </div>
</template>
