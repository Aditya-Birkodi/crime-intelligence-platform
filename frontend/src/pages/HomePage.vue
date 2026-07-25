<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { RouterLink } from "vue-router";
import { api } from "@/services/api";
import StatCard from "@/components/StatCard.vue";
import DonutChart from "@/components/DonutChart.vue";
import VBarChart from "@/components/VBarChart.vue";
import AreaChart from "@/components/AreaChart.vue";
import RankBars from "@/components/RankBars.vue";
import type {
  AnalyticsOverview,
  DistrictGeoSummary,
  HotspotsResponse,
  SocioDistrict,
  TrendAlertsResponse,
} from "@/types";

const loading = ref(true);
const error = ref<string | null>(null);
const overview = ref<AnalyticsOverview | null>(null);
const districts = ref<DistrictGeoSummary[]>([]);
const hotspots = ref<HotspotsResponse | null>(null);
const trends = ref<TrendAlertsResponse | null>(null);
const socioInsight = ref("");
const socioTop = ref<SocioDistrict[]>([]);
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

const districtBars = computed(() =>
  [...districts.value]
    .sort((a, b) => b.case_count - a.case_count)
    .slice(0, 8)
    .map((d) => ({
      label: d.district_name,
      count: d.case_count,
      hint: `District ${d.district_id}`,
    })),
);

/** Hour-of-day intensity from hotspot bins (0–23). */
const hourSeries = computed(() => {
  const hours = Array.from({ length: 24 }, () => 0);
  for (const bin of hotspots.value?.bins ?? []) {
    if (bin.hour_of_day != null && bin.hour_of_day >= 0 && bin.hour_of_day < 24) {
      hours[bin.hour_of_day] += bin.case_count;
    }
  }
  // If grain has no hour dimension, fall back to a flat signal from bin counts
  if (hours.every((h) => h === 0) && (hotspots.value?.bins.length ?? 0) > 0) {
    const top = [...(hotspots.value?.bins ?? [])]
      .sort((a, b) => b.case_count - a.case_count)
      .slice(0, 12)
      .map((b) => b.case_count);
    return top.length ? top : hours;
  }
  return hours;
});

const geocodePct = computed(() => {
  const t = overview.value?.total_cases ?? 0;
  const g = overview.value?.cases_with_coordinates ?? 0;
  if (!t) return "—";
  return `${Math.round((g / t) * 100)}%`;
});

const openShare = computed(() => {
  const rows = overview.value?.by_status ?? [];
  const total = overview.value?.total_cases ?? 0;
  if (!total) return "—";
  const open = rows
    .filter((s) => /investigat|open|pending/i.test(s.name))
    .reduce((a, s) => a + s.count, 0);
  return `${Math.round((open / total) * 100)}%`;
});

const alertRows = computed(
  () => trends.value?.alerts.filter((a) => a.is_alert).slice(0, 8) ?? [],
);

const deskStamp = computed(() =>
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
    const [ov, geo, hs, risk, anom, tr, socio] = await Promise.all([
      api.getAnalyticsOverview(),
      api.getGeoDistricts().catch(() => [] as DistrictGeoSummary[]),
      api.getHotspots({ grain: "hour", cell_size_degrees: 0.08 }).catch(() => null),
      api.aiPredictRisk({ horizon_days: 7 }).catch(() => null),
      api.aiAnomalies(8).catch(() => null),
      api
        .getTrendAlerts({ recent_days: 30, baseline_days: 90, threshold: 1.5 })
        .catch(() => null),
      api.getSocioEconomicOverlay().catch(() => null),
    ]);
    overview.value = ov;
    districts.value = geo;
    hotspots.value = hs;
    if (risk) riskTop.value = risk.items.slice(0, 6);
    if (anom) anomalies.value = anom.items.slice(0, 5);
    trends.value = tr;
    if (socio) {
      socioInsight.value = socio.insight;
      socioTop.value = [...socio.districts]
        .sort((a, b) => b.crime_per_10k_density - a.crime_per_10k_density)
        .slice(0, 5);
    }
  } catch (e) {
    error.value = e instanceof Error ? e.message : "Could not load analytics";
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <section class="space-y-8">
    <!-- Compact ops strip -->
    <div
      class="cip-rise flex flex-wrap items-end justify-between gap-4 border-b border-[var(--cip-line)] pb-5"
    >
      <div>
        <p class="cip-kicker">Operations desk</p>
        <h1 class="cip-display mt-1 text-[clamp(1.75rem,3.5vw,2.35rem)] text-[var(--cip-ink)]">
          Statewide FIR pulse
        </h1>
        <p class="mt-1.5 max-w-xl text-sm text-[var(--cip-muted)]">
          Live volume, composition, hotspots, and risk — Catalyst Data Store.
        </p>
      </div>
      <div class="flex flex-wrap items-center gap-2">
        <p class="mr-2 text-xs text-[var(--cip-muted)]">{{ deskStamp }}</p>
        <RouterLink to="/cases" class="cip-btn cip-btn-primary">Cases</RouterLink>
        <RouterLink to="/map" class="cip-btn cip-btn-ghost">Map</RouterLink>
        <RouterLink to="/intelligence" class="cip-btn cip-btn-ghost">Intelligence</RouterLink>
      </div>
    </div>

    <div
      v-if="error"
      class="rounded-sm border border-[#e8b4a8] bg-[#fdf1ee] px-4 py-3 text-sm text-[#9b2c1f]"
    >
      {{ error }}
    </div>

    <div
      v-if="loading"
      class="cip-rise grid gap-3 sm:grid-cols-2 lg:grid-cols-4"
      aria-busy="true"
    >
      <div v-for="i in 4" :key="i" class="cip-stat h-[5.5rem] animate-pulse opacity-60" />
    </div>

    <template v-else>
      <!-- KPI row -->
      <div class="cip-rise cip-rise-delay-1 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          label="Total FIRs"
          :value="overview?.total_cases ?? '—'"
          :hint="`${overview?.stations_covered ?? 0} stations · ${overview?.districts_covered ?? 0} districts`"
        />
        <StatCard
          label="Geocoded"
          :value="geocodePct"
          :hint="`${overview?.cases_with_coordinates ?? 0} with coordinates`"
          accent="teal"
        />
        <StatCard
          label="Under investigation"
          :value="openShare"
          hint="Share of open caseload"
          accent="amber"
        />
        <StatCard
          label="Active alerts"
          :value="alertRows.length"
          :hint="trends ? `${trends.recent_days}d vs ${trends.baseline_days}d baseline` : 'Trend spikes'"
          accent="ink"
        />
      </div>

      <!-- Charts row 1: donut + vertical bars -->
      <div class="cip-rise cip-rise-delay-2 grid gap-5 lg:grid-cols-2">
        <div class="cip-panel p-5 pl-6">
          <h2 class="cip-display text-xl text-[var(--cip-ink)]">Case status mix</h2>
          <p class="mt-1 text-xs text-[var(--cip-muted)]">Share of the live FIR corpus</p>
          <div class="mt-5">
            <DonutChart :items="statusBars" center-label="FIRs" :size="190" />
          </div>
        </div>
        <div class="cip-panel p-5 pl-6">
          <h2 class="cip-display text-xl text-[var(--cip-ink)]">Crime heads</h2>
          <p class="mt-1 text-xs text-[var(--cip-muted)]">Major head frequency</p>
          <div class="mt-3">
            <VBarChart :items="headBars" :max-bars="6" :height="240" />
          </div>
        </div>
      </div>

      <!-- Charts row 2: area + district ranks -->
      <div class="cip-rise cip-rise-delay-3 grid gap-5 lg:grid-cols-[1.1fr_0.9fr]">
        <div class="cip-panel p-5 pl-6">
          <div class="flex flex-wrap items-end justify-between gap-2">
            <div>
              <h2 class="cip-display text-xl text-[var(--cip-ink)]">Temporal intensity</h2>
              <p class="mt-1 text-xs text-[var(--cip-muted)]">
                Hotspot activity by hour of day
                <span v-if="hotspots"> · {{ hotspots.bins.length }} cells</span>
              </p>
            </div>
            <RouterLink to="/map" class="text-xs font-semibold text-[var(--cip-accent)] hover:underline">
              Open map →
            </RouterLink>
          </div>
          <div class="mt-4 rounded-sm border border-[rgba(197,212,216,0.7)] bg-[rgba(255,255,255,0.4)] px-2 pt-3">
            <AreaChart
              :points="hourSeries"
              :labels="['00:00', '12:00', '23:00']"
              :height="180"
            />
          </div>
        </div>
        <div class="cip-panel p-5 pl-6">
          <h2 class="cip-display text-xl text-[var(--cip-ink)]">District volume</h2>
          <p class="mt-1 text-xs text-[var(--cip-muted)]">Top districts by FIR count</p>
          <div class="mt-5">
            <RankBars :items="districtBars" :max-bars="7" />
          </div>
        </div>
      </div>

      <!-- Risk + anomalies -->
      <div class="cip-rise cip-rise-delay-4 grid gap-5 lg:grid-cols-2">
        <div class="cip-panel p-5 pl-6">
          <div class="flex items-center justify-between gap-2">
            <div>
              <h2 class="cip-display text-xl text-[var(--cip-ink)]">District risk</h2>
              <p class="mt-1 text-xs text-[var(--cip-muted)]">7-day forecast scores</p>
            </div>
            <RouterLink
              to="/intelligence"
              class="text-xs font-semibold text-[var(--cip-accent)] hover:underline"
            >
              Ask AI →
            </RouterLink>
          </div>
          <ul class="mt-4 space-y-3">
            <li
              v-for="r in riskTop"
              :key="r.scope_id"
              class="grid grid-cols-[1fr_auto] items-center gap-3"
            >
              <div class="min-w-0">
                <div class="flex items-center justify-between gap-2">
                  <p class="truncate font-medium text-[var(--cip-ink)]">
                    {{ r.scope_name || `District ${r.scope_id}` }}
                  </p>
                  <span class="cip-display text-sm tabular-nums text-[var(--cip-ink-soft)]">
                    {{ r.risk_score.toFixed(0) }}
                  </span>
                </div>
                <div class="mt-1.5 h-1.5 overflow-hidden rounded-sm bg-[rgba(13,107,124,0.1)]">
                  <div
                    class="h-full rounded-sm"
                    :style="{
                      width: `${Math.min(100, r.risk_score)}%`,
                      background:
                        r.risk_score >= 70
                          ? '#9b2c1f'
                          : r.risk_score >= 40
                            ? 'var(--cip-signal)'
                            : 'var(--cip-accent)',
                    }"
                  />
                </div>
                <p class="mt-1 text-[0.7rem] text-[var(--cip-muted)]">
                  {{ r.case_count }} cases
                  <span v-if="r.top_crime_heads?.length">
                    · {{ r.top_crime_heads.slice(0, 2).join(", ") }}
                  </span>
                </p>
              </div>
            </li>
            <li v-if="!riskTop.length" class="text-sm text-[var(--cip-muted)]">No risk data</li>
          </ul>
        </div>

        <div class="cip-panel p-5 pl-6">
          <h2 class="cip-display text-xl text-[var(--cip-ink)]">Anomalies</h2>
          <p class="mt-1 text-xs text-[var(--cip-muted)]">Pattern breaks worth review</p>
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
                <span
                  class="text-[10px] font-semibold uppercase tracking-[0.12em] text-[var(--cip-muted)]"
                >
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

      <!-- Socio + trend alerts -->
      <div class="cip-rise cip-rise-delay-4 grid gap-5 lg:grid-cols-[0.9fr_1.1fr]">
        <div class="cip-panel p-5 pl-6">
          <div class="flex items-center justify-between gap-2">
            <div>
              <h2 class="cip-display text-xl text-[var(--cip-ink)]">
                Socio-economic pressure
              </h2>
              <p class="mt-1 text-xs text-[var(--cip-muted)]">
                Crime intensity vs urbanization / density
              </p>
            </div>
            <RouterLink
              to="/map"
              class="text-xs font-semibold text-[var(--cip-accent)] hover:underline"
            >
              Overlay →
            </RouterLink>
          </div>
          <p
            v-if="socioInsight"
            class="mt-4 text-sm leading-relaxed text-[var(--cip-ink-soft)]"
          >
            {{ socioInsight }}
          </p>
          <ul class="mt-4 space-y-2.5">
            <li
              v-for="d in socioTop"
              :key="d.district_id"
              class="flex items-center justify-between gap-3 text-sm"
            >
              <div class="min-w-0">
                <p class="truncate font-medium text-[var(--cip-ink)]">
                  {{ d.district_name }}
                  <span
                    v-if="d.is_urban_core"
                    class="ml-1 text-[10px] font-semibold uppercase tracking-wider text-[var(--cip-accent)]"
                    >urban</span
                  >
                </p>
                <p class="text-[11px] text-[var(--cip-muted)]">
                  Unemp {{ d.youth_unemployment_pct }}% · Urban
                  {{ d.urbanization_pct }}%
                </p>
              </div>
              <span class="cip-display tabular-nums text-[var(--cip-accent-deep)]">
                {{ d.crime_per_10k_density.toFixed(1) }}
              </span>
            </li>
            <li v-if="!socioTop.length" class="text-sm text-[var(--cip-muted)]">
              Socio overlay unavailable
            </li>
          </ul>
        </div>

        <div class="cip-panel p-5 pl-6">
          <div class="flex items-center justify-between gap-2">
            <div>
              <h2 class="cip-display text-xl text-[var(--cip-ink)]">Trend alerts</h2>
              <p class="mt-1 text-xs text-[var(--cip-muted)]">
                Spikes vs baseline
                <span v-if="trends">
                  · {{ trends.recent_days }}d / {{ trends.baseline_days }}d ·
                  {{ trends.threshold }}×
                </span>
              </p>
            </div>
            <RouterLink
              to="/map"
              class="text-xs font-semibold text-[var(--cip-accent)] hover:underline"
            >
              Red zones →
            </RouterLink>
          </div>
          <div class="cip-table-wrap mt-5">
            <table>
              <thead>
                <tr>
                  <th>District</th>
                  <th>Crime head</th>
                  <th>Recent</th>
                  <th>Spike</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(a, i) in alertRows" :key="i">
                  <td>
                    <RouterLink
                      :to="`/map?district_id=${a.district_id}`"
                      class="font-medium text-[var(--cip-accent-deep)] hover:underline"
                    >
                      {{ a.district_name }}
                    </RouterLink>
                  </td>
                  <td>{{ a.crime_head_name }}</td>
                  <td class="tabular-nums">{{ a.recent_count }}</td>
                  <td
                    class="cip-display text-lg tabular-nums text-[var(--cip-signal)]"
                  >
                    {{ a.spike_ratio.toFixed(2) }}×
                  </td>
                </tr>
                <tr v-if="!alertRows.length">
                  <td colspan="4" class="py-8 text-center text-[var(--cip-muted)]">
                    No active alerts
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </template>
  </section>
</template>
