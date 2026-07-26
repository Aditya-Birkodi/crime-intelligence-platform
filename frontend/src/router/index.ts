import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/login",
      name: "login",
      component: () => import("@/pages/LoginPage.vue"),
      meta: { title: "Sign in", public: true },
    },
    {
      path: "/",
      component: () => import("@/layouts/AppLayout.vue"),
      meta: { requiresAuth: true },
      children: [
        {
          path: "",
          name: "home",
          component: () => import("@/pages/HomePage.vue"),
          meta: { title: "Home", requiresAuth: true },
        },
        {
          path: "cases",
          name: "cases",
          component: () => import("@/pages/CasesPage.vue"),
          meta: { title: "Cases", requiresAuth: true },
        },
        {
          path: "cases/:id",
          name: "case-detail",
          component: () => import("@/pages/CaseDetailPage.vue"),
          meta: { title: "Case detail", requiresAuth: true },
        },
        {
          path: "identity",
          name: "identity",
          component: () => import("@/pages/IdentityPage.vue"),
          meta: { title: "Identity", requiresAuth: true },
        },
        {
          path: "map",
          name: "map",
          component: () => import("@/pages/MapPage.vue"),
          meta: { title: "Map", requiresAuth: true },
        },
        {
          path: "network",
          name: "network",
          component: () => import("@/pages/NetworkPage.vue"),
          meta: { title: "Network", requiresAuth: true },
        },
        {
          path: "intelligence",
          name: "intelligence",
          component: () => import("@/pages/IntelligencePage.vue"),
          meta: { title: "Intelligence", requiresAuth: true },
        },
      ],
    },
  ],
  scrollBehavior: () => ({ top: 0 }),
});

router.beforeEach(async (to) => {
  const { refreshCatalystAuth, isAuthenticated } = await import("@/services/auth");
  await refreshCatalystAuth();

  const publicRoute = to.matched.some((r) => r.meta.public === true);
  if (publicRoute) {
    if (to.name === "login" && isAuthenticated()) {
      return { path: "/" };
    }
    return true;
  }
  if (!isAuthenticated()) {
    return {
      path: "/login",
      query: { redirect: to.fullPath !== "/" ? to.fullPath : undefined },
    };
  }
  return true;
});

router.afterEach((to) => {
  const title = (to.meta.title as string | undefined) ?? "CIP";
  document.title = `${title} · Crime Intelligence Platform`;
});

export default router;
