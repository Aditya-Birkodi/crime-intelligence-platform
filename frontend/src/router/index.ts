import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      name: "home",
      component: () => import("@/pages/HomePage.vue"),
      meta: { title: "Home" },
    },
    {
      path: "/cases",
      name: "cases",
      component: () => import("@/pages/CasesPage.vue"),
      meta: { title: "Cases" },
    },
    {
      path: "/cases/:id",
      name: "case-detail",
      component: () => import("@/pages/CaseDetailPage.vue"),
      meta: { title: "Case detail" },
    },
    {
      path: "/identity",
      name: "identity",
      component: () => import("@/pages/IdentityPage.vue"),
      meta: { title: "Identity" },
    },
    {
      path: "/map",
      name: "map",
      component: () => import("@/pages/MapPage.vue"),
      meta: { title: "Map" },
    },
    {
      path: "/network",
      name: "network",
      component: () => import("@/pages/NetworkPage.vue"),
      meta: { title: "Network" },
    },
    {
      path: "/intelligence",
      name: "intelligence",
      component: () => import("@/pages/IntelligencePage.vue"),
      meta: { title: "Intelligence" },
    },
  ],
  scrollBehavior: () => ({ top: 0 }),
});

router.afterEach((to) => {
  const title = (to.meta.title as string | undefined) ?? "CIP";
  document.title = `${title} · Crime Intelligence Platform`;
});

export default router;
