/**
 * Catalyst Authentication (hosted login).
 * Login: https://…catalystserverless.in/__catalyst/auth/login
 * Docs: https://docs.catalyst.zoho.com/en/tutorials/hosted-login-app/nodejs/configure-client/
 */

export type AuthUser = {
  username: string;
  display_name: string;
  role: string;
  unit: string;
};

export type AuthSession = {
  access_token: string;
  expires_at: number;
  user: AuthUser;
  provider: "catalyst" | "demo";
};

const STORAGE_KEY = "cip_auth_session";

declare global {
  interface Window {
    catalyst?: {
      auth: {
        isUserAuthenticated: () => Promise<unknown>;
        signOut: (redirectURL: string) => void;
        getCurrentUser?: () => Promise<{ content?: Record<string, unknown> }>;
      };
    };
  }
}

/** Hosted Native Auth login (India DC project). */
export function getCatalystLoginUrl(): string {
  const fromEnv = import.meta.env.VITE_CATALYST_AUTH_LOGIN_URL as string | undefined;
  if (fromEnv?.trim()) return fromEnv.trim().replace(/\/$/, "");
  return "https://crime-intelligence-platform-60078759306.development.catalystserverless.in/__catalyst/auth/login";
}

/** Where Catalyst should send the browser after a successful sign-in. */
export function getPostLoginUrl(): string {
  const fromEnv = import.meta.env.VITE_AUTH_REDIRECT_URL as string | undefined;
  if (fromEnv?.trim()) return fromEnv.trim();
  return `${window.location.origin}/`;
}

export function loadSession(): AuthSession | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const session = JSON.parse(raw) as AuthSession;
    if (!session?.access_token || !session.user) return null;
    if (session.expires_at && session.expires_at < Date.now()) {
      clearSession();
      return null;
    }
    return session;
  } catch {
    return null;
  }
}

export function saveSession(session: AuthSession): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
}

export function clearSession(): void {
  localStorage.removeItem(STORAGE_KEY);
}

function mapCatalystUser(raw: unknown): AuthUser {
  const content =
    raw && typeof raw === "object" && "content" in raw
      ? ((raw as { content: Record<string, unknown> }).content ?? {})
      : ((raw as Record<string, unknown>) ?? {});
  const email = String(content.email_id || content.email || content.user_id || "officer");
  const first = String(content.first_name || "");
  const last = String(content.last_name || "");
  const name = [first, last].filter(Boolean).join(" ") || email;
  return {
    username: email,
    display_name: name,
    role: String(content.role_details || content.role || "SCRB Officer"),
    unit: "Karnataka State Police · SCRB",
  };
}

/** Probe Catalyst Web SDK; persist a desk session when authenticated. */
export async function refreshCatalystAuth(): Promise<boolean> {
  const auth = window.catalyst?.auth;
  if (!auth?.isUserAuthenticated) {
    return loadSession()?.provider === "catalyst";
  }
  try {
    const result = await auth.isUserAuthenticated();
    let profile: unknown = result;
    if (auth.getCurrentUser) {
      try {
        profile = await auth.getCurrentUser();
      } catch {
        /* use isUserAuthenticated payload */
      }
    }
    const user = mapCatalystUser(profile);
    saveSession({
      access_token: "catalyst_session",
      expires_at: Date.now() + 12 * 60 * 60 * 1000,
      user,
      provider: "catalyst",
    });
    return true;
  } catch {
    if (loadSession()?.provider === "catalyst") clearSession();
    return false;
  }
}

export function isAuthenticated(): boolean {
  return loadSession() != null;
}

/** Navigate to Catalyst Hosted Authentication. */
export function redirectToCatalystLogin(): void {
  const login = getCatalystLoginUrl();
  // serviceurl / SERVICE_URL used by some Catalyst hosted-login builds
  const redirect = encodeURIComponent(getPostLoginUrl());
  const sep = login.includes("?") ? "&" : "?";
  window.location.assign(`${login}${sep}serviceurl=${redirect}`);
}

export function signOutCatalyst(): void {
  clearSession();
  const login = getCatalystLoginUrl();
  const auth = window.catalyst?.auth;
  if (auth?.signOut) {
    auth.signOut(login);
    return;
  }
  window.location.assign(login);
}

export function authHeader(): Record<string, string> {
  return {};
}
