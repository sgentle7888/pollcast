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

const routes = [
  { path: "/",                    component: Home,          meta: { title: "Home" } },
  { path: "/analytics",           component: Analytics,     meta: { title: "Analytics" } },

  // Polls
  { path: "/polls",               component: PollsList,     meta: { title: "Polls & Surveys", tab: "polls" } },
  { path: "/polls/:name",         component: PollVote,      meta: { title: "Vote" } },
  { path: "/polls/:name/results", component: PollResults,   meta: { title: "Poll Results" } },

  // Surveys
  { path: "/surveys",             component: PollsList,     meta: { title: "Polls & Surveys", tab: "surveys" } },
  { path: "/surveys/create",      component: SurveyCreate,  meta: { title: "Create", requiresAdmin: true } },
  { path: "/surveys/:name",       component: SurveyTake,    meta: { title: "Take Survey" } },
  { path: "/surveys/:name/results", component: SurveyResults, meta: { title: "Survey Results" } },

  // Create alias (covers both polls and surveys)
  { path: "/create",              component: SurveyCreate,  meta: { title: "Create", requiresAdmin: true } },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
  scrollBehavior() {
    return { top: 0, behavior: "smooth" };
  },
});

// Navigation guard: update document title
router.beforeEach((to) => {
  if (to.meta?.title) {
    document.title = `${to.meta.title} — Pollcast`;
  }
  return true;
});

export default router;
