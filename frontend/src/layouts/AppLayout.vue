<script setup lang="ts">
import { RouterLink, RouterView, useRoute } from "vue-router";

const route = useRoute();

const links = [
  { to: "/", label: "Dashboard", exact: true },
  { to: "/cases", label: "Cases" },
  { to: "/identity", label: "Identity" },
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
        class="pointer-events-none absolute inset-0 opacity-[0.1]"
        style="
          background-image:
            linear-gradient(rgba(255, 255, 255, 0.06) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.06) 1px, transparent 1px);
          background-size: 32px 32px;
        "
      />
      <div
        class="pointer-events-none absolute -right-20 top-0 h-full w-[55%] opacity-25"
        style="
          background: radial-gradient(ellipse at 65% 20%, rgba(196, 120, 42, 0.5), transparent 58%);
        "
      />

      <div class="relative mx-auto max-w-7xl px-6 pt-5 pb-4">
        <div class="flex flex-wrap items-center justify-between gap-4">
          <RouterLink to="/" class="cip-rise block min-w-0">
            <p class="cip-kicker !text-[rgba(243,228,208,0.8)]">
              Karnataka State Police · SCRB
            </p>
            <span
              class="cip-display mt-1 block text-[clamp(1.45rem,3vw,1.95rem)] font-medium leading-tight text-white"
            >
              Crime Intelligence Platform
            </span>
          </RouterLink>
          <p
            class="cip-rise cip-rise-delay-1 hidden max-w-xs text-right text-xs font-light leading-relaxed text-[rgba(244,250,249,0.55)] sm:block"
          >
            FIR analytics · geospatial heat · link graphs · MO clusters · Graph RAG
          </p>
        </div>

        <nav
          class="cip-rise cip-rise-delay-2 mt-5 flex flex-wrap gap-1 border-t border-white/10 pt-3.5"
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

    <main class="mx-auto max-w-7xl px-6 py-8">
      <RouterView v-slot="{ Component }">
        <Transition name="route-fade" mode="out-in">
          <component :is="Component" />
        </Transition>
      </RouterView>
    </main>

    <footer class="border-t border-[var(--cip-line)]/70 py-5 text-center text-xs text-[var(--cip-muted)]">
      CIP · restricted operational use · not for public dissemination
    </footer>
  </div>
</template>
