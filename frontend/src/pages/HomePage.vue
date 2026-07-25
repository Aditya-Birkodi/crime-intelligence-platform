<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { RouterLink } from "vue-router";
import { api } from "@/services/api";
import StatCard from "@/components/StatCard.vue";
import BarChart from "@/components/BarChart.vue";
import type { AnalyticsOverview, TrendAlertsResponse } from "@/types";

const health = ref("checking…");
const apiStatus = ref("checking…");
const error = ref<string | null>(null);
const overview = ref<AnalyticsOverview | null>(null);
const trends = ref<TrendAlertsResponse | null>(null);
const riskTop = ref<
  {
    scope_id: number;
    scope_name: string | null;
    risk_score: number;
    case_count: number;
    top_crime_heads: string[];
  }[]
>([]);
const anomalies = ref<
  {
    title: string;
    severity: string;
    kind: string;
    score: number;
    detail: string;
  }[]
>([]);

const statusBars = computed(
  () =>
    overview.value?.by_status.map((s) => ({
      label: s.name,
      count: s.count,
    })) ?? [],
);

const headBars = computed(
  () =>
    overview.value?.by_crime_head.map((h) => ({
      label: h.name,
      count: h.count,
    })) ?? [],
);

const alertRows = computed(() => trends.value?.alerts.filter((a) => a.is_alert).slice(0, 8) ?? []);

const hourLabel = computed(() =>
  new Intl.DateTimeFormat("en-IN", {
    weekday: "short",
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date()),
);

onMounted(async () => {
  try {
    const [h, s, ov, risk, anom, tr] = await Promise.all([
      api.getHealth(),
      api.getStatus(),
      api.getAnalyticsOverview().catch(() => null),
      api.aiPredictRisk({ horizon_days: 7 }).catch(() => null),
      api.aiAnomalies(8).catch(() => null),
      api.getTrendAlerts({ recent_days: 30, baseline_days: 90, threshold: 1.5 }).catch(() => null),
    ]);
    health.value = h.status;
    apiStatus.value = `${s.api} · ${s.status}`;
    overview.value = ov;
    if (risk) riskTop.value = risk.items.slice(0, 6);
    if (anom) anomalies.value = anom.items.slice(0, 6);
    trends.value = tr;
  } catch (e) {
    error.value = e instanceof Error ? e.message : "Failed to reach API";
    health.value = "down";
    apiStatus.value = "down";
  }
});
</script>

<template>
  <section class="space-y-10">
    <div
      class="cip-rise relative grid gap-8 overflow-hidden border border-[var(--cip-line)] bg-[rgba(255,255,255,0.55)] p-6 md:grid-cols-[1.35fr_0.65fr] md:p-8"
      style="border-radius: 2px"
    >
      <div
        class="pointer-events-none absolute -right-8 -top-10 h-48 w-48 rounded-full opacity-40"
        style="background: radial-gradient(circle, rgba(196,120,42,0.25), transparent 70%)"
      />
      <div>
        <p class="cip-kicker">Situation room</p>
        <h1 class="cip-display mt-2 text-[clamp(2rem,4.5vw,3.25rem)] font-medium leading-[1.08] text-[var(--cip-ink)]">
          Read the state<br class="hidden sm:block" />
          <span class="text-[var(--cip-accent)]">in one glance.</span>
        </h1>
        <p class="mt-4 max-w-lg text-[0.95rem] leading-relaxed text-[var(--cip-muted)]">
          FIR volume, district risk, anomaly spikes, and trend alerts — pulled live from
          Catalyst AppSail.
        </p>
        <div class="mt-6 flex flex-wrap gap-2.5">
          <RouterLink to="/cases" class="cip-btn cip-btn-primary">Browse FIRs</RouterLink>
          <RouterLink to="/map" class="cip-btn cip-btn-ghost">Open map</RouterLink>
          <RouterLink to="/intelligence" class="cip-btn cip-btn-ghost">Ask AI</RouterLink>
        </div>
      </div>
      <div class="relative flex flex-col justify-between gap-4 border-t border-[var(--cip-line)] pt-5 md:border-l md:border-t-0 md:pl-8 md:pt-0">
        <div>
          <p class="text-[0.65rem] font-semibold uppercase tracking-[0.18em] text-[var(--cip-muted)]">
            Desk clock
          </p>
          <p class="cip-display mt-2 text-2xl text-[var(--cip-ink)]">{{ hourLabel }}</p>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <p class="text-[0.65rem] uppercase tracking-[0.14em] text-[var(--cip-muted)]">Health</p>
            <p class="mt-1 font-semibold capitalize text-[var(--cip-accent-deep)]">{{ health }}</p>
          </div>
          <div>
            <p class="text-[0.65rem] uppercase tracking-[0.14em] text-[var(--cip-muted)]">API</p>
            <p class="mt-1 text-sm font-medium text-[var(--cip-ink-soft)]">{{ apiStatus }}</p>
          </div>
        </div>
      </div>
    </div>

    <div
      v-if="error"
      class="rounded-sm border border-[#e8b4a8] bg-[#fdf1ee] px-4 py-3 text-sm text-[#9b2c1f]"
    >
      {{ error }}
    </div>

    <div class="cip-rise cip-rise-delay-1 grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
      <StatCard label="Total FIRs" :value="overview?.total_cases ?? '—'" />
      <StatCard label="Geocoded" :value="overview?.cases_with_coordinates ?? '—'" />
      <StatCard label="Districts" :value="overview?.districts_covered ?? '—'" />
      <StatCard label="Stations" :value="overview?.stations_covered ?? '—'" />
      <StatCard label="Health" :value="health" />
      <StatCard label="API lane" :value="apiStatus" />
    </div>

    <div class="cip-rise cip-rise-delay-2 grid gap-5 lg:grid-cols-2">
      <div class="cip-panel p-5 pl-6">
        <h2 class="cip-display text-xl text-[var(--cip-ink)]">Cases by status</h2>
        <p class="mt-1 text-xs text-[var(--cip-muted)]">Composition of the seeded FIR corpus</p>
        <div class="mt-5">
          <BarChart :items="statusBars" />
        </div>
      </div>
      <div class="cip-panel p-5 pl-6">
        <h2 class="cip-display text-xl text-[var(--cip-ink)]">Crime heads</h2>
        <p class="mt-1 text-xs text-[var(--cip-muted)]">Major head frequency</p>
        <div class="mt-5">
          <BarChart :items="headBars" :max-bars="10" />
        </div>
      </div>
    </div>

    <div class="cip-rise cip-rise-delay-3 grid gap-5 lg:grid-cols-2">
      <div class="cip-panel p-5 pl-6">
        <div class="flex items-center justify-between gap-2">
          <div>
            <h2 class="cip-display text-xl text-[var(--cip-ink)]">District risk</h2>
            <p class="mt-1 text-xs text-[var(--cip-muted)]">7-day forecast scores</p>
          </div>
          <RouterLink to="/intelligence" class="text-xs font-semibold text-[var(--cip-accent)] hover:underline">
            Ask AI →
          </RouterLink>
        </div>
        <ul class="mt-4 divide-y divide-[rgba(197,212,216,0.7)]">
          <li
            v-for="r in riskTop"
            :key="r.scope_id"
            class="flex items-start justify-between gap-3 py-3"
          >
            <div>
              <p class="font-medium text-[var(--cip-ink)]">
                {{ r.scope_name || `District ${r.scope_id}` }}
              </p>
              <p class="mt-0.5 text-xs text-[var(--cip-muted)]">
                {{ r.case_count }} cases
                <span v-if="r.top_crime_heads?.length">
                  · {{ r.top_crime_heads.slice(0, 2).join(", ") }}
                </span>
              </p>
            </div>
            <span
              class="cip-display shrink-0 text-xl tabular-nums"
              :style="{
                color:
                  r.risk_score >= 70
                    ? '#9b2c1f'
                    : r.risk_score >= 40
                      ? 'var(--cip-signal)'
                      : 'var(--cip-accent-deep)',
              }"
            >
              {{ r.risk_score.toFixed(0) }}
            </span>
          </li>
          <li v-if="!riskTop.length" class="py-4 text-sm text-[var(--cip-muted)]">No risk data</li>
        </ul>
      </div>

      <div class="cip-panel p-5 pl-6">
        <h2 class="cip-display text-xl text-[var(--cip-ink)]">Anomalies</h2>
        <p class="mt-1 text-xs text-[var(--cip-muted)]">Pattern breaks worth a second look</p>
        <ul class="mt-4 space-y-3">
          <li
            v-for="(a, i) in anomalies"
            :key="i"
            class="border border-[rgba(197,212,216,0.65)] bg-[rgba(255,255,255,0.45)] px-3.5 py-3"
            style="border-radius: 2px"
          >
            <div class="flex items-center gap-2">
              <span
                class="cip-badge"
                :class="
                  a.severity === 'high'
                    ? 'cip-badge-high'
                    : a.severity === 'medium'
                      ? 'cip-badge-med'
                      : 'cip-badge-low'
                "
              >
                {{ a.severity }}
              </span>
              <span class="text-[10px] font-semibold uppercase tracking-[0.12em] text-[var(--cip-muted)]">
                {{ a.kind }}
              </span>
            </div>
            <p class="mt-2 text-sm font-semibold text-[var(--cip-ink)]">{{ a.title }}</p>
            <p class="mt-0.5 line-clamp-2 text-xs leading-relaxed text-[var(--cip-muted)]">
              {{ a.detail }}
            </p>
          </li>
          <li v-if="!anomalies.length" class="text-sm text-[var(--cip-muted)]">No anomalies</li>
        </ul>
      </div>
    </div>

    <div class="cip-rise cip-rise-delay-4 cip-panel p-5 pl-6">
      <h2 class="cip-display text-xl text-[var(--cip-ink)]">Trend alerts</h2>
      <p class="mt-1 text-xs text-[var(--cip-muted)]">
        Spikes vs baseline
        <span v-if="trends">
          · recent {{ trends.recent_days }}d · baseline {{ trends.baseline_days }}d ·
          {{ trends.threshold }}× threshold
        </span>
      </p>
      <div class="cip-table-wrap mt-5">
        <table>
          <thead>
            <tr>
              <th>District</th>
              <th>Crime head</th>
              <th>Recent</th>
              <th>Baseline avg</th>
              <th>Spike</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(a, i) in alertRows" :key="i">
              <td>{{ a.district_name }}</td>
              <td>{{ a.crime_head_name }}</td>
              <td class="tabular-nums">{{ a.recent_count }}</td>
              <td class="tabular-nums">{{ a.baseline_avg.toFixed(1) }}</td>
              <td class="cip-display text-lg tabular-nums text-[var(--cip-signal)]">
                {{ a.spike_ratio.toFixed(2) }}×
              </td>
            </tr>
            <tr v-if="!alertRows.length">
              <td colspan="5" class="py-8 text-center text-[var(--cip-muted)]">
                No active alerts
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>
</template>
