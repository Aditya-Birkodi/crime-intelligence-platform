<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import {
  getCatalystLoginUrl,
  isAuthenticated,
  redirectToCatalystLogin,
  refreshCatalystAuth,
} from "@/services/auth";

const router = useRouter();
const checking = ref(true);
const redirecting = ref(false);
const loginUrl = getCatalystLoginUrl();

onMounted(async () => {
  const ok = (await refreshCatalystAuth()) || isAuthenticated();
  if (ok) {
    await router.replace("/");
    return;
  }
  checking.value = false;
});

function continueToCatalyst() {
  redirecting.value = true;
  redirectToCatalystLogin();
}
</script>

<template>
  <div class="login-shell">
    <div class="login-atmosphere" aria-hidden="true" />
    <div class="login-grid" aria-hidden="true" />
    <div class="login-glow" aria-hidden="true" />

    <div
      class="relative z-10 mx-auto flex min-h-screen w-full max-w-6xl flex-col justify-center px-6 py-12 lg:flex-row lg:items-center lg:gap-16 lg:py-16"
    >
      <div class="cip-rise max-w-xl shrink-0">
        <p class="cip-kicker !text-[rgba(243,228,208,0.85)]">
          Karnataka State Police · SCRB
        </p>
        <h1
          class="cip-display mt-3 text-[clamp(2.4rem,6vw,3.75rem)] font-medium leading-[1.05] text-white"
        >
          Crime Intelligence Platform
        </h1>
        <p class="mt-4 max-w-md text-base leading-relaxed text-[rgba(244,250,249,0.72)]">
          Sign in with Catalyst Authentication to open the FIR analytics and
          intelligence desk.
        </p>
        <p
          class="mt-8 text-[0.7rem] font-semibold uppercase tracking-[0.18em] text-[rgba(243,228,208,0.55)]"
        >
          Restricted operational use
        </p>
      </div>

      <div class="cip-rise cip-rise-delay-2 mt-10 w-full max-w-md lg:mt-0">
        <div class="login-panel">
          <h2 class="cip-display text-2xl text-[var(--cip-ink)]">Sign in</h2>
          <p class="mt-1 text-sm text-[var(--cip-muted)]">
            You will be redirected to Catalyst Hosted Authentication.
          </p>

          <p
            v-if="checking"
            class="mt-6 text-sm text-[var(--cip-muted)]"
          >
            Checking session…
          </p>

          <template v-else>
            <button
              type="button"
              class="cip-btn cip-btn-primary mt-6 w-full justify-center disabled:opacity-50"
              :disabled="redirecting"
              @click="continueToCatalyst"
            >
              {{ redirecting ? "Redirecting…" : "Continue to Catalyst Sign In" }}
            </button>

            <p class="mt-4 break-all text-[11px] leading-relaxed text-[var(--cip-muted)]">
              {{ loginUrl }}
            </p>

            <p class="mt-4 text-xs leading-relaxed text-[var(--cip-muted)]">
              After a successful sign-in, Catalyst returns you to this desk.
              Ensure the Slate URL is listed under Authentication → Whitelisting
              / redirect URLs in the Catalyst console.
            </p>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-shell {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  background: #042f38;
  color: #f4faf9;
}

.login-atmosphere {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    125deg,
    #042f38 0%,
    #0a4a56 42%,
    #0d5c4a 78%,
    #164038 100%
  );
}

.login-grid {
  position: absolute;
  inset: 0;
  opacity: 0.1;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.06) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.06) 1px, transparent 1px);
  background-size: 32px 32px;
}

.login-glow {
  position: absolute;
  right: -10%;
  top: -20%;
  width: 60%;
  height: 80%;
  opacity: 0.28;
  background: radial-gradient(
    ellipse at 60% 30%,
    rgba(196, 120, 42, 0.55),
    transparent 58%
  );
  pointer-events: none;
}

.login-panel {
  background: rgba(247, 250, 249, 0.94);
  border: 1px solid rgba(197, 212, 216, 0.9);
  backdrop-filter: blur(12px);
  padding: 1.75rem 1.6rem 1.5rem;
  border-radius: 2px;
  box-shadow: 0 24px 60px rgba(4, 47, 56, 0.35);
  position: relative;
}

.login-panel::before {
  content: "";
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: linear-gradient(180deg, var(--cip-accent), var(--cip-signal));
}
</style>
