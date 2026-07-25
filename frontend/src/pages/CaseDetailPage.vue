<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, RouterLink } from "vue-router";
import { api, fileToBase64 } from "@/services/api";
import AiChatPanel from "@/components/AiChatPanel.vue";
import type { CaseMasterDetail, IdName, MediaAttachment } from "@/types";

const route = useRoute();
const loading = ref(true);
const error = ref<string | null>(null);
const detail = ref<CaseMasterDetail | null>(null);
const stations = ref<IdName[]>([]);
const statuses = ref<IdName[]>([]);
const crimeHeads = ref<IdName[]>([]);
const media = ref<MediaAttachment[]>([]);
const uploadBusy = ref(false);
const uploadMsg = ref<string | null>(null);
const graphCtx = ref<{
  summary: string;
  node_count: number;
  edge_count: number;
  neighbor_crime_nos: string[];
  linked_persons: string[];
  engine: string;
} | null>(null);

const caseId = computed(() => Number(route.params.id));

const stationLabel = computed(() => {
  const id = detail.value?.police_station_id;
  if (id == null) return "—";
  return stations.value.find((s) => s.id === id)?.name ?? String(id);
});

const statusLabel = computed(() => {
  const id = detail.value?.case_status_id;
  if (id == null) return "—";
  return statuses.value.find((s) => s.id === id)?.name ?? String(id);
});

const headLabel = computed(() => {
  const id = detail.value?.crime_major_head_id;
  if (id == null) return "—";
  return crimeHeads.value.find((h) => h.id === id)?.name ?? String(id);
});

async function loadMedia() {
  try {
    const res = await api.listMedia({ case_master_id: caseId.value, limit: 30 });
    media.value = res.items;
  } catch {
    media.value = [];
  }
}

async function onUpload(ev: Event, entityType: string, entityId?: number) {
  const input = ev.target as HTMLInputElement;
  const file = input.files?.[0];
  if (!file || !detail.value) return;
  uploadBusy.value = true;
  uploadMsg.value = null;
  try {
    const b64 = await fileToBase64(file);
    await api.uploadMediaJson({
      image_base64: b64,
      filename: file.name,
      content_type: file.type || "image/jpeg",
      entity_type: entityType,
      entity_id: entityId,
      case_master_id: detail.value.case_master_id,
      analyse_face: entityType === "accused",
      face_mode: "moderate",
      label: entityType,
    });
    uploadMsg.value = `Uploaded ${file.name}`;
    await loadMedia();
  } catch (e) {
    uploadMsg.value = e instanceof Error ? e.message : "Upload failed";
  } finally {
    uploadBusy.value = false;
    input.value = "";
  }
}

async function load() {
  loading.value = true;
  error.value = null;
  detail.value = null;
  graphCtx.value = null;
  try {
    const [d, st, statusList, heads] = await Promise.all([
      api.getCase(caseId.value),
      api.listStations().catch(() => [] as IdName[]),
      api.listCaseStatuses().catch(() => [] as IdName[]),
      api.listCrimeHeads().catch(() => [] as IdName[]),
    ]);
    detail.value = d;
    stations.value = st;
    statuses.value = statusList;
    crimeHeads.value = heads;
    void loadMedia();

    try {
      graphCtx.value = await api.aiGraphContext({
        case_id: caseId.value,
        depth: 2,
      });
    } catch {
      graphCtx.value = null;
    }
  } catch (e) {
    error.value = e instanceof Error ? e.message : "Failed to load case";
  } finally {
    loading.value = false;
  }
}

onMounted(load);
watch(caseId, load);
</script>

<template>
  <section class="cip-rise space-y-7">
    <div>
      <RouterLink to="/cases" class="text-sm text-[var(--cip-muted)] hover:text-[var(--cip-ink)]">
        ← Back to cases
      </RouterLink>
      <h1 class="cip-display mt-2 text-3xl text-[var(--cip-ink)]">
        {{ detail?.crime_no ?? "Case detail" }}
      </h1>
      <p v-if="detail" class="mt-1 text-sm text-[var(--cip-muted)]">
        Case {{ detail.case_no }} · {{ stationLabel }} · {{ statusLabel }}
      </p>
    </div>

    <p v-if="loading" class="text-sm text-[var(--cip-muted)]">Loading…</p>
    <p v-else-if="error" class="text-sm text-[#9b2c1f]">{{ error }}</p>

    <template v-else-if="detail">
      <div class="flex flex-wrap gap-2 text-sm">
        <RouterLink
          :to="{ path: '/network', query: { case_id: String(detail.case_master_id) } }"
          class="cip-btn cip-btn-ghost"
        >
          Open network
        </RouterLink>
        <RouterLink
          v-if="detail.latitude != null && detail.longitude != null"
          :to="{ path: '/map', query: { case_id: String(detail.case_master_id) } }"
          class="cip-btn cip-btn-ghost"
        >
          View on map
        </RouterLink>
      </div>

      <div class="cip-panel grid gap-4 p-5 pl-6 md:grid-cols-3">
        <div>
          <p class="text-[0.65rem] uppercase tracking-[0.12em] text-[var(--cip-muted)]">Crime No</p>
          <p class="mt-1 font-mono text-sm">{{ detail.crime_no }}</p>
        </div>
        <div>
          <p class="text-[0.65rem] uppercase tracking-[0.12em] text-[var(--cip-muted)]">Crime head</p>
          <p class="mt-1">{{ headLabel }}</p>
        </div>
        <div>
          <p class="text-[0.65rem] uppercase tracking-[0.12em] text-[var(--cip-muted)]">Registered</p>
          <p class="mt-1">{{ detail.crime_registered_date ?? "—" }}</p>
        </div>
        <div>
          <p class="text-[0.65rem] uppercase tracking-[0.12em] text-[var(--cip-muted)]">Incident window</p>
          <p class="mt-1 text-sm">
            {{ detail.incident_from_date ?? "—" }} → {{ detail.incident_to_date ?? "—" }}
          </p>
        </div>
        <div>
          <p class="text-[0.65rem] uppercase tracking-[0.12em] text-[var(--cip-muted)]">Coordinates</p>
          <p class="mt-1 text-sm">
            {{ detail.latitude ?? "—" }}, {{ detail.longitude ?? "—" }}
          </p>
        </div>
        <div>
          <p class="text-[0.65rem] uppercase tracking-[0.12em] text-[var(--cip-muted)]">Court ID</p>
          <p class="mt-1">{{ detail.court_id ?? "—" }}</p>
        </div>
        <div class="md:col-span-3">
          <p class="text-[0.65rem] uppercase tracking-[0.12em] text-[var(--cip-muted)]">Brief facts</p>
          <p class="mt-1 whitespace-pre-wrap text-[var(--cip-ink)]">
            {{ detail.brief_facts || "—" }}
          </p>
        </div>
      </div>

      <div
        v-if="detail.occurrence"
        class="cip-panel p-5 pl-6"
      >
        <h2 class="cip-display text-lg text-[var(--cip-ink)]">Occurrence</h2>
        <dl class="mt-3 grid gap-3 text-sm sm:grid-cols-2 lg:grid-cols-3">
          <div>
            <dt class="text-[0.65rem] uppercase tracking-[0.1em] text-[var(--cip-muted)]">Place</dt>
            <dd>{{ detail.occurrence.place_of_occurrence || "—" }}</dd>
          </div>
          <div>
            <dt class="text-[0.65rem] uppercase tracking-[0.1em] text-[var(--cip-muted)]">Village / city</dt>
            <dd>{{ detail.occurrence.village_or_city || "—" }}</dd>
          </div>
          <div>
            <dt class="text-[0.65rem] uppercase tracking-[0.1em] text-[var(--cip-muted)]">Beat</dt>
            <dd>{{ detail.occurrence.beat_number || "—" }}</dd>
          </div>
          <div>
            <dt class="text-[0.65rem] uppercase tracking-[0.1em] text-[var(--cip-muted)]">From → To</dt>
            <dd>
              {{ detail.occurrence.occurrence_from || "—" }} →
              {{ detail.occurrence.occurrence_to || "—" }}
            </dd>
          </div>
          <div>
            <dt class="text-[0.65rem] uppercase tracking-[0.1em] text-[var(--cip-muted)]">Distance from PS</dt>
            <dd>
              {{ detail.occurrence.distance_from_ps_km ?? "—" }} km
              <span v-if="detail.occurrence.direction_from_ps" class="text-[var(--cip-muted)]">
                · {{ detail.occurrence.direction_from_ps }}
              </span>
            </dd>
          </div>
        </dl>
      </div>

      <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <div class="cip-panel p-4 pl-5">
          <h2 class="cip-display text-lg text-[var(--cip-ink)]">
            Victims ({{ detail.victims.length }})
          </h2>
          <ul class="mt-3 space-y-3 text-sm text-[var(--cip-ink-soft)]">
            <li v-for="v in detail.victims" :key="v.victim_master_id">
              <span class="font-semibold text-[var(--cip-ink)]">{{ v.victim_name }}</span>
              <p class="mt-0.5 text-xs text-[var(--cip-muted)]">
                <span v-if="v.age_year != null">{{ v.age_year }}y</span>
                <span v-if="v.gender_id">
                  <span v-if="v.age_year != null"> · </span>{{ v.gender_id }}
                </span>
              </p>
              <label class="mt-1 block text-[10px] text-[var(--cip-accent)]">
                + photo
                <input
                  type="file"
                  accept="image/*"
                  class="sr-only"
                  :disabled="uploadBusy"
                  @change="onUpload($event, 'victim', v.victim_master_id)"
                />
              </label>
            </li>
            <li v-if="!detail.victims.length" class="text-[var(--cip-muted)]">None</li>
          </ul>
        </div>
        <div class="cip-panel p-4 pl-5">
          <h2 class="cip-display text-lg text-[var(--cip-ink)]">
            Accused ({{ detail.accused.length }})
          </h2>
          <ul class="mt-3 space-y-3 text-sm text-[var(--cip-ink-soft)]">
            <li v-for="a in detail.accused" :key="a.accused_master_id">
              <RouterLink
                :to="{
                  path: '/network',
                  query: { accused_id: String(a.accused_master_id) },
                }"
                class="font-semibold text-[var(--cip-ink)] hover:underline"
              >
                {{ a.accused_name }}
              </RouterLink>
              <p class="mt-0.5 text-xs text-[var(--cip-muted)]">
                <span v-if="a.age_year != null">{{ a.age_year }}y</span>
                <span v-if="a.gender_id">
                  <span v-if="a.age_year != null"> · </span>{{ a.gender_id }}
                </span>
                <span v-if="a.person_id">
                  <span v-if="a.age_year != null || a.gender_id"> · </span>
                  <span class="font-mono text-[var(--cip-accent)]">{{ a.person_id }}</span>
                </span>
              </p>
              <label class="mt-1 block text-[10px] text-[var(--cip-accent)]">
                + face photo (Zia)
                <input
                  type="file"
                  accept="image/*"
                  class="sr-only"
                  :disabled="uploadBusy"
                  @change="onUpload($event, 'accused', a.accused_master_id)"
                />
              </label>
            </li>
            <li v-if="!detail.accused.length" class="text-[var(--cip-muted)]">None</li>
          </ul>
        </div>
        <div class="cip-panel p-4 pl-5">
          <h2 class="cip-display text-lg text-[var(--cip-ink)]">
            Complainants ({{ detail.complainants?.length ?? 0 }})
          </h2>
          <ul class="mt-3 space-y-2 text-sm text-[var(--cip-ink-soft)]">
            <li v-for="c in detail.complainants" :key="c.complainant_id">
              {{ c.complainant_name }}
              <span v-if="c.age_year" class="text-[var(--cip-muted)]">({{ c.age_year }})</span>
            </li>
            <li v-if="!detail.complainants?.length" class="text-[var(--cip-muted)]">None</li>
          </ul>
        </div>
        <div class="cip-panel p-4 pl-5">
          <h2 class="cip-display text-lg text-[var(--cip-ink)]">Act / sections</h2>
          <ul class="mt-3 space-y-2 text-sm text-[var(--cip-ink-soft)]">
            <li v-for="s in detail.act_sections" :key="s.id">
              {{ s.act_id }} · {{ s.section_id }}
            </li>
            <li v-if="!detail.act_sections.length" class="text-[var(--cip-muted)]">None</li>
          </ul>
        </div>
      </div>

      <div class="cip-panel p-5 pl-6">
        <div class="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 class="cip-display text-lg text-[var(--cip-ink)]">Case media</h2>
            <p class="mt-1 text-xs text-[var(--cip-muted)]">
              Photos stored via Stratus / local media · face analysis on accused uploads
            </p>
          </div>
          <label class="cip-btn cip-btn-ghost cursor-pointer">
            {{ uploadBusy ? "Uploading…" : "Attach case image" }}
            <input
              type="file"
              accept="image/*"
              class="sr-only"
              :disabled="uploadBusy"
              @change="onUpload($event, 'case', detail.case_master_id)"
            />
          </label>
        </div>
        <p v-if="uploadMsg" class="mt-2 text-sm text-[var(--cip-ink-soft)]">{{ uploadMsg }}</p>
        <div class="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <a
            v-for="m in media"
            :key="m.media_id"
            :href="api.mediaContentUrl(m.media_id)"
            target="_blank"
            rel="noopener"
            class="border border-[rgba(197,212,216,0.65)] bg-[rgba(255,255,255,0.4)] p-2"
          >
            <img
              :src="api.mediaContentUrl(m.media_id)"
              :alt="m.filename"
              class="h-28 w-full object-cover"
            />
            <p class="mt-1 truncate text-[11px] text-[var(--cip-muted)]">
              {{ m.entity_type }} · {{ m.filename }}
            </p>
          </a>
          <p v-if="!media.length" class="text-sm text-[var(--cip-muted)]">No images yet</p>
        </div>
      </div>

      <div class="grid gap-4 md:grid-cols-2">
        <div class="cip-panel p-4 pl-5">
          <h2 class="cip-display text-lg text-[var(--cip-ink)]">
            Arrests ({{ detail.arrests?.length ?? 0 }})
          </h2>
          <ul class="mt-3 space-y-2 text-sm text-[var(--cip-ink-soft)]">
            <li v-for="a in detail.arrests" :key="a.arrest_surrender_id">
              {{ a.arrest_surrender_date || "—" }} · type {{ a.arrest_surrender_type_id }}
              <span v-if="a.accused_master_id" class="text-[var(--cip-muted)]">
                · accused #{{ a.accused_master_id }}
              </span>
            </li>
            <li v-if="!detail.arrests?.length" class="text-[var(--cip-muted)]">None</li>
          </ul>
        </div>
        <div class="cip-panel p-4 pl-5">
          <h2 class="cip-display text-lg text-[var(--cip-ink)]">
            Chargesheets ({{ detail.chargesheets?.length ?? 0 }})
          </h2>
          <ul class="mt-3 space-y-2 text-sm text-[var(--cip-ink-soft)]">
            <li v-for="cs in detail.chargesheets" :key="cs.cs_id">
              Type {{ cs.cs_type }} · {{ cs.cs_date || "—" }}
            </li>
            <li v-if="!detail.chargesheets?.length" class="text-[var(--cip-muted)]">None</li>
          </ul>
        </div>
      </div>

      <div
        v-if="graphCtx"
        class="cip-panel p-5 pl-6"
      >
        <h2 class="cip-display text-lg text-[var(--cip-ink)]">Graph RAG context</h2>
        <p class="mt-1 text-xs text-[var(--cip-muted)]">
          {{ graphCtx.engine }} · {{ graphCtx.node_count }} nodes ·
          {{ graphCtx.edge_count }} edges
        </p>
        <pre class="mt-3 whitespace-pre-wrap text-sm text-[var(--cip-ink-soft)]">{{ graphCtx.summary }}</pre>
        <p v-if="graphCtx.neighbor_crime_nos.length" class="mt-3 text-xs text-[var(--cip-muted)]">
          Neighbor FIRs:
          {{ graphCtx.neighbor_crime_nos.slice(0, 12).join(", ") }}
        </p>
      </div>

      <AiChatPanel
        :case-master-id="detail.case_master_id"
        title="Ask AI about this FIR"
        default-question="Summarize modus operandi and linked risk for this FIR"
      />
    </template>
  </section>
</template>
