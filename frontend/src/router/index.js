import { createRouter, createWebHashHistory } from "vue-router";

// Guest-facing views are imported eagerly (bundled into the main entry file) so a
// shared survey/poll link never depends on a second network request or a stale
// hashed chunk. Everything else stays lazy-loaded.
import PollVote from "../views/PollVote.vue";
import SurveyTake from "../views/SurveyTake.vue";
import GuestDenied from "../views/GuestDenied.vue";

// Lazy-loaded views (authenticated only)
const Home = () => import("../views/PortalDashboard.vue");
const Analytics = () => import("../views/Dashboard.vue");
const PollsList = () => import("../views/SurveysList.vue");
const SurveyCreate = () => import("../views/SurveyCreate.vue");
const SurveyResults = () => import("../views/SurveyResults.vue");
const PollResults = () => import("../views/PollResults.vue");

const routes = [
  // ── Guest-allowed routes (no sidebar/header shown) ──────────────────
  {
    path: "/polls/:name",
    component: PollVote,
    meta: { title: "Vote Now", allowGuest: true },
  },
  {
    path: "/surveys/:name",
    component: SurveyTake,
    meta: { title: "Take Survey", allowGuest: true },
  },

  // ── Authenticated-only routes ────────────────────────────────────────
  { path: "/", component: Home, meta: { title: "Home" } },
  { path: "/analytics", component: Analytics, meta: { title: "Analytics" } },
  {
    path: "/polls",
    component: PollsList,
    meta: { title: "Polls & Surveys", tab: "polls" },
  },
  {
    path: "/polls/:name/results",
    component: PollResults,
    meta: { title: "Poll Results" },
  },
  {
    path: "/surveys",
    component: PollsList,
    meta: { title: "Polls & Surveys", tab: "surveys" },
  },
  {
    path: "/surveys/create",
    component: SurveyCreate,
    meta: { title: "Create", requiresAdmin: true },
  },
  {
    path: "/polls/:name/edit",
    component: SurveyCreate,
    meta: { title: "Edit Poll", requiresAdmin: true },
  },
  {
    path: "/surveys/:name/edit",
    component: SurveyCreate,
    meta: { title: "Edit Survey", requiresAdmin: true },
  },
  {
    path: "/surveys/:name/results",
    component: SurveyResults,
    meta: { title: "Survey Results" },
  },
  {
    path: "/create",
    component: SurveyCreate,
    meta: { title: "Create", requiresAdmin: true },
  },

  // ── Fallback for guests hitting a restricted page ────────────────────
  {
    path: "/guest-denied",
    component: GuestDenied,
    meta: { title: "Access Restricted", allowGuest: true },
  },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
  scrollBehavior() {
    return { top: 0, behavior: "smooth" };
  },
});

// Navigation guard: enforce guest restrictions + update document title
router.beforeEach((to) => {
  if (to.meta?.title) {
    document.title = `${to.meta.title} — Pollcast`;
  }

  // Check if the current visitor is a guest (unauthenticated)
  const isGuest = !window.frappe_user || window.frappe_user === "Guest";

  if (isGuest && !to.meta?.allowGuest) {
    // Guest trying to reach a restricted page → send them to the denial page
    return { path: "/guest-denied" };
  }

  return true;
});

// If a lazy chunk fails to load (usually a stale cached index.js pointing at
// chunk hashes that no longer exist after a redeploy), reload once to fetch fresh files.
router.onError((err) => {
  const msg = String(err?.message || err);
  if (
    /dynamically imported module|Importing a module script failed|Loading chunk|Failed to fetch/i.test(
      msg,
    )
  ) {
    const key = "pollcast_chunk_reload";
    try {
      if (!sessionStorage.getItem(key)) {
        sessionStorage.setItem(key, "1");
        window.location.reload();
      }
    } catch {
      /* storage blocked (private mode / in-app browser) — don't loop */
    }
  }
});

router.isReady().then(() => {
  try {
    sessionStorage.removeItem("pollcast_chunk_reload");
  } catch {}
});

export default router;
