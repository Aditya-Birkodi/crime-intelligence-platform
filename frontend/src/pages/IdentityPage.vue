<script setup lang="ts">
import { ref } from "vue";
import { RouterLink } from "vue-router";
import { api, fileToBase64 } from "@/services/api";
import type {
  FaceAnalyseResponse,
  FaceCompareResponse,
  SearchHit,
} from "@/types";

const query = ref("");
const searching = ref(false);
const searchError = ref<string | null>(null);
const hits = ref<SearchHit[]>([]);

const faceFile = ref<File | null>(null);
const facePreview = ref<string | null>(null);
const faceMode = ref("moderate");
const faceBusy = ref(false);
const faceError = ref<string | null>(null);
const faceResult = ref<FaceAnalyseResponse | null>(null);

const sourceFile = ref<File | null>(null);
const queryFile = ref<File | null>(null);
const compareBusy = ref(false);
const compareError = ref<string | null>(null);
const compareResult = ref<FaceCompareResponse | null>(null);

const sceneFile = ref<File | null>(null);
const sceneBusy = ref(false);
const sceneOut = ref<Record<string, unknown> | null>(null);

const ocrFile = ref<File | null>(null);
const ocrBusy = ref(false);
const ocrOut = ref<Record<string, unknown> | null>(null);

async function runSearch() {
  const q = query.value.trim();
  if (q.length < 2) return;
  searching.value = true;
  searchError.value = null;
  try {
    const res = await api.search({ q, limit: 40 });
    hits.value = res.items;
  } catch (e) {
    searchError.value = e instanceof Error ? e.message : "Search failed";
    hits.value = [];
  } finally {
    searching.value = false;
  }
}

function onFacePick(ev: Event) {
  const input = ev.target as HTMLInputElement;
  const f = input.files?.[0] ?? null;
  faceFile.value = f;
  facePreview.value = f ? URL.createObjectURL(f) : null;
  faceResult.value = null;
}

async function runFaceAnalyse() {
  if (!faceFile.value) return;
  faceBusy.value = true;
  faceError.value = null;
  try {
    const b64 = await fileToBase64(faceFile.value);
    faceResult.value = await api.analyseFaceJson({
      image_base64: b64,
      filename: faceFile.value.name,
      mode: faceMode.value,
      age: true,
      emotion: true,
      gender: true,
      persist: true,
      entity_type: "probe",
    });
  } catch (e) {
    faceError.value = e instanceof Error ? e.message : "Face analysis failed";
  } finally {
    faceBusy.value = false;
  }
}

async function runCompare() {
  if (!sourceFile.value || !queryFile.value) return;
  compareBusy.value = true;
  compareError.value = null;
  try {
    compareResult.value = await api.compareFaceJson({
      source_base64: await fileToBase64(sourceFile.value),
      query_base64: await fileToBase64(queryFile.value),
      source_filename: sourceFile.value.name,
      query_filename: queryFile.value.name,
    });
  } catch (e) {
    compareError.value = e instanceof Error ? e.message : "Compare failed";
  } finally {
    compareBusy.value = false;
  }
}

async function runDetect() {
  if (!sceneFile.value) return;
  sceneBusy.value = true;
  try {
    sceneOut.value = await api.detectObjectsJson({
      image_base64: await fileToBase64(sceneFile.value),
      filename: sceneFile.value.name,
    });
  } catch (e) {
    sceneOut.value = {
      error: e instanceof Error ? e.message : "Detect failed",
    };
  } finally {
    sceneBusy.value = false;
  }
}

async function runOcr() {
  if (!ocrFile.value) return;
  ocrBusy.value = true;
  try {
    ocrOut.value = await api.ocrJson({
      image_base64: await fileToBase64(ocrFile.value),
      filename: ocrFile.value.name,
    });
  } catch (e) {
    ocrOut.value = { error: e instanceof Error ? e.message : "OCR failed" };
  } finally {
    ocrBusy.value = false;
  }
}

function faceSummary(result: Record<string, unknown> | undefined): string {
  if (!result) return "—";
  const faces = result.faces as Record<string, unknown>[] | undefined;
  if (faces?.length) {
    const f = faces[0]!;
    const bits: string[] = [];
    const age = f.age as { range?: string } | undefined;
    const emotion = f.emotion as { prediction?: string } | undefined;
    const gender = f.gender as { prediction?: string } | undefined;
    if (age?.range) bits.push(`Age ${age.range}`);
    if (emotion?.prediction) bits.push(String(emotion.prediction));
    if (gender?.prediction) bits.push(String(gender.prediction));
    return bits.join(" · ") || `${faces.length} face(s)`;
  }
  return JSON.stringify(result).slice(0, 160);
}
</script>

<template>
  <section class="cip-rise space-y-8">
    <div>
      <p class="cip-kicker">Identity desk</p>
      <h1 class="cip-display mt-1 text-3xl text-[var(--cip-ink)]">
        Persons &amp; faces
      </h1>
      <p class="mt-1 max-w-2xl text-sm text-[var(--cip-muted)]">
        Search accused / victims / complainants by name, run Catalyst Zia face
        analytics, and match probe images against a known face.
      </p>
    </div>

    <!-- Name search -->
    <div class="cip-panel p-5 pl-6">
      <h2 class="cip-display text-xl text-[var(--cip-ink)]">Name search</h2>
      <div class="mt-3 flex flex-wrap gap-2">
        <input
          v-model="query"
          type="search"
          class="cip-field max-w-md flex-1 !mt-0"
          placeholder="Accused / victim / complainant / crime no…"
          @keydown.enter="runSearch"
        />
        <button
          type="button"
          class="cip-btn cip-btn-primary disabled:opacity-50"
          :disabled="searching || query.trim().length < 2"
          @click="runSearch"
        >
          {{ searching ? "Searching…" : "Search" }}
        </button>
      </div>
      <p v-if="searchError" class="mt-2 text-sm text-[#9b2c1f]">{{ searchError }}</p>
      <div class="cip-table-wrap mt-4">
        <table>
          <thead>
            <tr>
              <th>Type</th>
              <th>Name</th>
              <th>Crime no</th>
              <th>Person id</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(h, i) in hits" :key="i">
              <td>
                <span class="cip-badge cip-badge-med">{{ h.entity_type }}</span>
              </td>
              <td class="font-medium">{{ h.name }}</td>
              <td class="font-mono text-xs">{{ h.crime_no || "—" }}</td>
              <td class="font-mono text-xs text-[var(--cip-accent)]">
                {{ h.person_id || "—" }}
              </td>
              <td class="text-right">
                <RouterLink
                  v-if="h.case_master_id"
                  :to="`/cases/${h.case_master_id}`"
                  class="text-sm font-semibold text-[var(--cip-accent-deep)] hover:underline"
                >
                  Open case
                </RouterLink>
                <RouterLink
                  v-if="h.entity_type === 'accused'"
                  :to="{
                    path: '/network',
                    query: { accused_id: String(h.entity_id) },
                  }"
                  class="ml-3 text-sm font-semibold text-[var(--cip-accent-deep)] hover:underline"
                >
                  Network
                </RouterLink>
              </td>
            </tr>
            <tr v-if="!hits.length">
              <td colspan="5" class="py-8 text-center text-[var(--cip-muted)]">
                Enter at least 2 characters to search parties and FIRs.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="grid gap-6 lg:grid-cols-2">
      <!-- Face analytics -->
      <div class="cip-panel p-5 pl-6">
        <h2 class="cip-display text-xl text-[var(--cip-ink)]">Face analytics</h2>
        <p class="mt-1 text-xs text-[var(--cip-muted)]">
          Catalyst Zia <code>analyse_face</code> — age, emotion, gender.
        </p>
        <div class="mt-3 space-y-3">
          <input type="file" accept="image/*" @change="onFacePick" />
          <img
            v-if="facePreview"
            :src="facePreview"
            alt="Face preview"
            class="max-h-48 rounded-sm border border-[var(--cip-line)] object-contain"
          />
          <label class="block text-sm">
            <span
              class="text-[0.7rem] font-semibold uppercase tracking-[0.12em] text-[var(--cip-muted)]"
              >Mode</span
            >
            <select v-model="faceMode" class="cip-field">
              <option value="basic">basic</option>
              <option value="moderate">moderate</option>
              <option value="advanced">advanced</option>
            </select>
          </label>
          <button
            type="button"
            class="cip-btn cip-btn-primary disabled:opacity-50"
            :disabled="!faceFile || faceBusy"
            @click="runFaceAnalyse"
          >
            {{ faceBusy ? "Analysing…" : "Analyse face" }}
          </button>
          <p v-if="faceError" class="text-sm text-[#9b2c1f]">{{ faceError }}</p>
          <div
            v-if="faceResult"
            class="border border-[rgba(197,212,216,0.65)] bg-[rgba(255,255,255,0.45)] px-3 py-3 text-sm"
          >
            <p class="font-semibold text-[var(--cip-ink)]">
              {{ faceSummary(faceResult.result) }}
            </p>
            <p class="mt-1 text-xs text-[var(--cip-muted)]">
              Provider {{ faceResult.provider }}
              <span v-if="faceResult.media_id">
                · media {{ faceResult.media_id }}</span
              >
            </p>
            <pre
              class="mt-2 max-h-40 overflow-auto text-[11px] text-[var(--cip-ink-soft)]"
              >{{ JSON.stringify(faceResult.result, null, 2) }}</pre
            >
          </div>
        </div>
      </div>

      <!-- Face compare -->
      <div class="cip-panel p-5 pl-6">
        <h2 class="cip-display text-xl text-[var(--cip-ink)]">Face recognition</h2>
        <p class="mt-1 text-xs text-[var(--cip-muted)]">
          Catalyst Zia <code>compare_face</code> — known face vs probe.
        </p>
        <div class="mt-3 grid gap-3 sm:grid-cols-2">
          <label class="block text-sm">
            <span
              class="text-[0.7rem] font-semibold uppercase tracking-[0.12em] text-[var(--cip-muted)]"
              >Known / gallery</span
            >
            <input
              type="file"
              accept="image/*"
              class="mt-1 block w-full text-xs"
              @change="
                sourceFile = ($event.target as HTMLInputElement).files?.[0] ?? null
              "
            />
          </label>
          <label class="block text-sm">
            <span
              class="text-[0.7rem] font-semibold uppercase tracking-[0.12em] text-[var(--cip-muted)]"
              >Probe / CCTV</span
            >
            <input
              type="file"
              accept="image/*"
              class="mt-1 block w-full text-xs"
              @change="
                queryFile = ($event.target as HTMLInputElement).files?.[0] ?? null
              "
            />
          </label>
        </div>
        <button
          type="button"
          class="cip-btn cip-btn-primary mt-3 disabled:opacity-50"
          :disabled="!sourceFile || !queryFile || compareBusy"
          @click="runCompare"
        >
          {{ compareBusy ? "Comparing…" : "Compare faces" }}
        </button>
        <p v-if="compareError" class="mt-2 text-sm text-[#9b2c1f]">
          {{ compareError }}
        </p>
        <div
          v-if="compareResult"
          class="mt-3 border border-[rgba(197,212,216,0.65)] bg-[rgba(255,255,255,0.45)] px-3 py-3"
        >
          <p class="text-sm font-semibold text-[var(--cip-ink)]">
            <span
              class="cip-badge"
              :class="
                compareResult.matched ? 'cip-badge-high' : 'cip-badge-med'
              "
            >
              {{
                compareResult.matched == null
                  ? "result"
                  : compareResult.matched
                    ? "MATCH"
                    : "NO MATCH"
              }}
            </span>
            <span
              v-if="compareResult.confidence != null"
              class="ml-2 tabular-nums"
            >
              {{ (compareResult.confidence * 100).toFixed(0) }}% confidence
            </span>
          </p>
          <pre
            class="mt-2 max-h-40 overflow-auto text-[11px] text-[var(--cip-ink-soft)]"
            >{{ JSON.stringify(compareResult.result, null, 2) }}</pre
          >
        </div>
      </div>
    </div>

    <div class="grid gap-6 lg:grid-cols-2">
      <div class="cip-panel p-5 pl-6">
        <h2 class="cip-display text-xl text-[var(--cip-ink)]">Scene objects</h2>
        <p class="mt-1 text-xs text-[var(--cip-muted)]">
          Zia object detection — vehicles, persons, scene tags.
        </p>
        <input
          type="file"
          accept="image/*"
          class="mt-3 block text-xs"
          @change="sceneFile = ($event.target as HTMLInputElement).files?.[0] ?? null"
        />
        <button
          type="button"
          class="cip-btn cip-btn-ghost mt-3 disabled:opacity-50"
          :disabled="!sceneFile || sceneBusy"
          @click="runDetect"
        >
          {{ sceneBusy ? "Detecting…" : "Detect objects" }}
        </button>
        <pre
          v-if="sceneOut"
          class="mt-3 max-h-48 overflow-auto text-[11px] text-[var(--cip-ink-soft)]"
          >{{ JSON.stringify(sceneOut, null, 2) }}</pre
        >
      </div>
      <div class="cip-panel p-5 pl-6">
        <h2 class="cip-display text-xl text-[var(--cip-ink)]">OCR</h2>
        <p class="mt-1 text-xs text-[var(--cip-muted)]">
          Extract text from FIR scans / ID images via Zia OCR.
        </p>
        <input
          type="file"
          accept="image/*"
          class="mt-3 block text-xs"
          @change="ocrFile = ($event.target as HTMLInputElement).files?.[0] ?? null"
        />
        <button
          type="button"
          class="cip-btn cip-btn-ghost mt-3 disabled:opacity-50"
          :disabled="!ocrFile || ocrBusy"
          @click="runOcr"
        >
          {{ ocrBusy ? "Reading…" : "Run OCR" }}
        </button>
        <pre
          v-if="ocrOut"
          class="mt-3 max-h-48 overflow-auto text-[11px] text-[var(--cip-ink-soft)]"
          >{{ JSON.stringify(ocrOut, null, 2) }}</pre
        >
      </div>
    </div>
  </section>
</template>
