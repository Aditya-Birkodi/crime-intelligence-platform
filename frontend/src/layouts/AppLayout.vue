<script setup lang="ts">
import { RouterLink, RouterView, useRoute } from "vue-router";
import { baseUrl } from "@/services/api";

const route = useRoute();

const links = [
  { to: "/", label: "Dashboard", exact: true },
  { to: "/cases", label: "Cases" },
  { to: "/map", label: "Map" },
  { to: "/network", label: "Network" },
  { to: "/intelligence", label: "Intelligence" },
];

function isOn(to: string, exact?: boolean) {
  if (exact) return route.path === to;
  return route.path === to || route.path.startsWith(`${to}/`);
}
</script>

<template>
  <div class="cip-shell min-h-screen">
    <header class="relative overflow-hidden text-[#f4faf9]">
      <div
        class="absolute inset-0"
        style="
          background:
            linear-gradient(125deg, #042f38 0%, #0a4a56 42%, #0d5c4a 78%, #164038 100%);
        "
      />
      <div
        class="pointer-events-none absolute inset-0 opacity-[0.12]"
        style="
          background-image:
            linear-gradient(rgba(255, 255, 255, 0.07) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.07) 1px, transparent 1px);
          background-size: 28px 28px;
        "
      />
      <div
        class="pointer-events-none absolute -right-16 top-0 h-full w-1/2 opacity-30"
        style="
          background: radial-gradient(ellipse at 70% 30%, rgba(196, 120, 42, 0.55), transparent 55%);
        "
      />

      <div class="relative mx-auto max-w-7xl px-6 pt-6 pb-5">
        <div class="flex flex-wrap items-start justify-between gap-6">
          <div class="cip-rise max-w-xl">
            <p class="cip-kicker !text-[rgba(243,228,208,0.85)]">
              Karnataka State Police · SCRB
            </p>
            <RouterLink to="/" class="mt-2 block">
              <span
                class="cip-display block text-[clamp(1.85rem,4vw,2.75rem)] font-medium leading-[1.05] text-white"
              >
                Crime Intelligence
              </span>
              <span
                class="cip-display mt-0.5 block text-[clamp(1.35rem,3vw,2rem)] font-medium leading-none text-[rgba(243,228,208,0.92)]"
              >
                Platform
              </span>
            </RouterLink>
            <p class="mt-3 max-w-md text-sm font-light leading-relaxed text-[rgba(244,250,249,0.68)]">
              Operational desk for FIR analytics, geospatial heat, link graphs, and Graph RAG.
            </p>
          </div>

          <div
            class="cip-rise cip-rise-delay-1 flex items-center gap-3 rounded-sm border border-white/15 bg-white/5 px-3.5 py-2.5 backdrop-blur-sm"
          >
            <span class="cip-live-dot" aria-hidden="true" />
            <div class="min-w-0">
              <p class="text-[10px] font-semibold uppercase tracking-[0.16em] text-[rgba(244,250,249,0.55)]">
                Live API
              </p>
              <p class="max-w-[14rem] truncate font-mono text-[11px] text-[rgba(243,228,208,0.9)] sm:max-w-xs">
                {{ baseUrl.replace(/^https?:\/\//, "") }}
              </p>
            </div>
          </div>
        </div>

        <nav
          class="cip-rise cip-rise-delay-2 mt-7 flex flex-wrap gap-1 border-t border-white/10 pt-4"
          aria-label="Primary"
        >
          <RouterLink
            v-for="link in links"
            :key="link.to"
            :to="link.to"
            class="cip-nav-link"
            :class="{ 'router-link-active': isOn(link.to, link.exact) }"
            active-class=""
            exact-active-class=""
          >
            {{ link.label }}
          </RouterLink>
        </nav>
      </div>
    </header>

    <main class="mx-auto max-w-7xl px-6 py-9">
      <RouterView v-slot="{ Component }">
        <Transition name="route-fade" mode="out-in">
          <component :is="Component" />
        </Transition>
      </RouterView>
    </main>

    <footer class="border-t border-[var(--cip-line)]/70 py-5 text-center text-xs text-[var(--cip-muted)]">
      CIP · field intelligence shell · not for public dissemination
    </footer>
  </div>
</template>
