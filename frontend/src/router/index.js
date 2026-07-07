import { createRouter, createWebHashHistory } from "vue-router";

// Lazy-loaded views
const Home          = () => import("../views/PortalDashboard.vue");
const Analytics     = () => import("../views/Dashboard.vue");
const PollsList     = () => import("../views/SurveysList.vue");
const SurveyCreate  = () => import("../views/SurveyCreate.vue");
const SurveyTake    = () => import("../views/SurveyTake.vue");
const SurveyResults = () => import("../views/SurveyResults.vue");
const PollVote      = () => import("../views/PollVote.vue");
const PollResults   = () => import("../views/PollResults.vue");

// Minimal page shown to guests who try to access a restricted route
const GuestDenied = {
  template: `
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:60vh;text-align:center;padding:2rem;gap:1rem;">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="color:var(--text-muted)">
        <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>
      </svg>
      <h2 style="font-size:1.25rem;font-weight:700;color:var(--text-primary)">Access Restricted</h2>
      <p style="color:var(--text-secondary);max-width:340px;line-height:1.6;">
        This page requires you to be logged in. If you have a poll or survey link, please open it directly.
      </p>
      <a href="/login" style="margin-top:0.5rem;padding:0.6rem 1.5rem;background:var(--accent);color:#fff;border-radius:var(--r-md);font-weight:600;text-decoration:none;">
        Sign In
      </a>
    </div>
  `,
};

const routes = [
  // ── Guest-allowed routes (no sidebar/header shown) ──────────────────
  { path: "/polls/:name",   component: PollVote,  meta: { title: "Vote Now",    allowGuest: true } },
  { path: "/surveys/:name", component: SurveyTake, meta: { title: "Take Survey", allowGuest: true } },

  // ── Authenticated-only routes ────────────────────────────────────────
  { path: "/",                      component: Home,        meta: { title: "Home" } },
  { path: "/analytics",             component: Analytics,   meta: { title: "Analytics" } },
  { path: "/polls",                 component: PollsList,   meta: { title: "Polls & Surveys", tab: "polls" } },
  { path: "/polls/:name/results",   component: PollResults, meta: { title: "Poll Results" } },
  { path: "/surveys",               component: PollsList,   meta: { title: "Polls & Surveys", tab: "surveys" } },
  { path: "/surveys/create",        component: SurveyCreate, meta: { title: "Create", requiresAdmin: true } },
  { path: "/surveys/:name/results", component: SurveyResults, meta: { title: "Survey Results" } },
  { path: "/create",                component: SurveyCreate, meta: { title: "Create", requiresAdmin: true } },

  // ── Fallback for guests hitting a restricted page ────────────────────
  { path: "/guest-denied", component: GuestDenied, meta: { title: "Access Restricted", allowGuest: true } },
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

export default router;

