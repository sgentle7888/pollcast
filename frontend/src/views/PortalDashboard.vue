<template>
  <div class="home animate-fade-in-up">

    <!-- Hero Banner -->
    <div class="hero-banner card-glass">
      <div class="hero-mesh"></div>
      <div class="hero-content">
        <div class="hero-badge">
          <span class="pulse-dot"></span>
          Live Feedback Platform
        </div>
        <h1 class="hero-title">
          Insights That Drive<br/>
          <span class="hero-gradient-text">Better Decisions</span>
        </h1>
        <p class="hero-subtitle">
          Create polls, run surveys, and gather real-time insights across your organisation.
        </p>
        <div class="hero-actions">
          <RouterLink to="/polls" class="btn btn-primary btn-lg">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 12l2 2 4-4"/><path d="M5 7c0-1.1.9-2 2-2h10a2 2 0 0 1 2 2v12H5V7z"/></svg>
            Vote on Polls
          </RouterLink>
          <RouterLink to="/surveys" class="btn btn-secondary btn-lg">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/><rect x="9" y="3" width="6" height="4" rx="1"/></svg>
            Take a Survey
          </RouterLink>
        </div>
      </div>
      <div class="hero-visual">
        <div class="hero-ring hero-ring-1"></div>
        <div class="hero-ring hero-ring-2"></div>
        <div class="hero-ring hero-ring-3"></div>
        <div class="hero-center-icon">
          <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
        </div>
      </div>
    </div>

    <!-- KPI Stats -->
    <div class="kpi-grid stagger-1">
      <div class="card stat-card animate-fade-in-up stagger-1">
        <div class="stat-icon stat-icon-accent">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 12l2 2 4-4"/><path d="M5 7c0-1.1.9-2 2-2h10a2 2 0 0 1 2 2v12H5V7z"/></svg>
        </div>
        <div class="stat-body">
          <div class="stat-label">Active Polls</div>
          <div class="stat-value">{{ loading ? '…' : stats.activePolls }}</div>
          <div class="stat-trend up" v-if="stats.pollsChange > 0">↑ {{ stats.pollsChange }} this week</div>
        </div>
      </div>

      <div class="card stat-card animate-fade-in-up stagger-2">
        <div class="stat-icon stat-icon-violet">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/><rect x="9" y="3" width="6" height="4" rx="1"/></svg>
        </div>
        <div class="stat-body">
          <div class="stat-label">Active Surveys</div>
          <div class="stat-value">{{ loading ? '…' : stats.activeSurveys }}</div>
          <div class="stat-trend up" v-if="stats.surveysChange > 0">↑ {{ stats.surveysChange }} this week</div>
        </div>
      </div>

      <div class="card stat-card animate-fade-in-up stagger-3">
        <div class="stat-icon stat-icon-success">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
        </div>
        <div class="stat-body">
          <div class="stat-label">Total Responses</div>
          <div class="stat-value">{{ loading ? '…' : stats.totalResponses }}</div>
          <div class="stat-trend up" v-if="stats.responsesChange > 0">↑ {{ stats.responsesChange }} today</div>
        </div>
      </div>

      <div class="card stat-card animate-fade-in-up stagger-4">
        <div class="stat-icon stat-icon-warning">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 16 12 14 15 10 15 8 12 2 12"/><path d="M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"/></svg>
        </div>
        <div class="stat-body">
          <div class="stat-label">Engagement Rate</div>
          <div class="stat-value">{{ loading ? '…' : stats.engagementRate + '%' }}</div>
          <div class="stat-trend up" v-if="stats.engagementTrend > 0">↑ {{ stats.engagementTrend }}% vs last week</div>
        </div>
      </div>
    </div>

    <!-- Main Grid: Active items + Quick Actions -->
    <div class="home-main-grid">

      <!-- Active Polls -->
      <div class="card animate-fade-in-up stagger-2">
        <div class="card-header-row">
          <h3 class="section-title">
            <span class="section-title-icon">🗳️</span>
            Active Polls
          </h3>
          <RouterLink to="/polls" class="btn btn-ghost btn-sm">See all</RouterLink>
        </div>

        <div v-if="loading" class="mini-loading">
          <div class="spinner spinner-sm"></div>
        </div>
        <div v-else-if="activePolls.length === 0" class="mini-empty">
          <p class="text-secondary text-sm">No active polls right now.</p>
          <RouterLink v-if="auth.isPollManager" to="/create" class="btn btn-secondary btn-sm" style="margin-top: 0.75rem;">Create Poll</RouterLink>
        </div>
        <div v-else class="item-list">
          <div v-for="poll in activePolls.slice(0, 4)" :key="poll.name" class="item-row card-interactive" @click="$router.push('/polls/' + poll.name)">
            <div class="item-row-info">
              <span class="badge badge-success" style="margin-bottom: 0.35rem;">Active</span>
              <div class="item-row-title">{{ poll.title }}</div>
              <div class="item-row-meta">{{ poll.total_responses }} responses</div>
            </div>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="item-row-arrow"><polyline points="9 18 15 12 9 6"/></svg>
          </div>
        </div>
      </div>

      <!-- Active Surveys -->
      <div class="card animate-fade-in-up stagger-3">
        <div class="card-header-row">
          <h3 class="section-title">
            <span class="section-title-icon">📋</span>
            Active Surveys
          </h3>
          <RouterLink to="/surveys" class="btn btn-ghost btn-sm">See all</RouterLink>
        </div>

        <div v-if="loading" class="mini-loading">
          <div class="spinner spinner-sm"></div>
        </div>
        <div v-else-if="activeSurveys.length === 0" class="mini-empty">
          <p class="text-secondary text-sm">No active surveys right now.</p>
          <RouterLink v-if="auth.isPollManager" to="/create" class="btn btn-secondary btn-sm" style="margin-top: 0.75rem;">Create Survey</RouterLink>
        </div>
        <div v-else class="item-list">
          <div v-for="survey in activeSurveys.slice(0, 4)" :key="survey.name" class="item-row card-interactive" @click="$router.push('/surveys/' + survey.name)">
            <div class="item-row-info">
              <span class="badge badge-active" style="margin-bottom: 0.35rem;">Active</span>
              <div class="item-row-title">{{ survey.title }}</div>
              <div class="item-row-meta">{{ survey.total_responses }} responses</div>
            </div>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="item-row-arrow"><polyline points="9 18 15 12 9 6"/></svg>
          </div>
        </div>
      </div>

      <!-- Quick Actions Panel -->
      <div class="quick-actions-panel animate-fade-in-up stagger-4">
        <div class="card" style="flex: 1;">
          <h3 class="section-title" style="margin-bottom: 1.25rem;">
            <span class="section-title-icon">⚡</span>
            Quick Actions
          </h3>
          <div class="shortcuts-list">
            <RouterLink to="/analytics" class="shortcut-item">
              <div class="shortcut-icon-box shortcut-accent">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
              </div>
              <div class="shortcut-text">
                <strong>View Analytics</strong>
                <p>Responses, charts, trends</p>
              </div>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
            </RouterLink>

            <RouterLink to="/polls" class="shortcut-item">
              <div class="shortcut-icon-box shortcut-violet">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 12l2 2 4-4"/><path d="M5 7c0-1.1.9-2 2-2h10a2 2 0 0 1 2 2v12H5V7z"/></svg>
              </div>
              <div class="shortcut-text">
                <strong>Browse Polls</strong>
                <p>Vote on open polls</p>
              </div>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
            </RouterLink>

            <RouterLink to="/surveys" class="shortcut-item">
              <div class="shortcut-icon-box shortcut-success">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/><rect x="9" y="3" width="6" height="4" rx="1"/></svg>
              </div>
              <div class="shortcut-text">
                <strong>Take a Survey</strong>
                <p>Share your feedback</p>
              </div>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
            </RouterLink>

            <RouterLink v-if="auth.isPollManager" to="/create" class="shortcut-item shortcut-create">
              <div class="shortcut-icon-box shortcut-warning">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>
              </div>
              <div class="shortcut-text">
                <strong>Create New</strong>
                <p>Poll or survey wizard</p>
              </div>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
            </RouterLink>

            <div v-if="auth.isPollManager" class="shortcut-item" @click="openSettingsModal">
              <div class="shortcut-icon-box shortcut-accent">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="12" cy="12" r="3"/>
                  <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1Z"/>
                </svg>
              </div>
              <div class="shortcut-text">
                <strong>Company Branding</strong>
                <p>Upload company logo</p>
              </div>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
            </div>
          </div>
        </div>

        <!-- Info Card -->
        <div class="card info-card" style="flex: 1;">
          <h3 class="section-title" style="margin-bottom: 1rem;">
            <span class="section-title-icon">💡</span>
            How It Works
          </h3>
          <ul class="info-list">
            <li>🗳️ <strong>Polls</strong> — cast a vote on a single question.</li>
            <li>📋 <strong>Surveys</strong> — rate criteria on a 1–5 scale or answer open questions.</li>
            <li>📊 <strong>Analytics</strong> — see live charts and breakdown of all responses.</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, inject } from "vue";
import { useAuthStore } from "../stores/auth.js";
import { frappeCall } from "../api/frappe.js";

const auth = useAuthStore();
const openSettingsModal = inject("openSettingsModal", () => {});
const loading = ref(true);
const stats = ref({
  activePolls: 0, activeSurveys: 0, totalResponses: 0, engagementRate: 0,
  pollsChange: 0, surveysChange: 0, responsesChange: 0, engagementTrend: 0,
});
const polls = ref([]);
const surveys = ref([]);

const activePolls   = computed(() => polls.value.filter(p => p.status === "Active"));
const activeSurveys = computed(() => surveys.value.filter(s => s.status === "Active"));

onMounted(async () => {
  try {
    const [summary, pollList, surveyList] = await Promise.all([
      frappeCall("pollcast.api.get_dashboard_summary"),
      frappeCall("pollcast.api.get_polls"),
      frappeCall("pollcast.api.get_surveys"),
    ]);
    if (summary && !summary.error) stats.value = { ...stats.value, ...summary };
    polls.value   = pollList   || [];
    surveys.value = surveyList || [];
  } catch (e) {
    console.error("Home load error:", e);
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.home { display: flex; flex-direction: column; gap: 1.5rem; }

/* Hero */
.hero-banner {
  padding: 3rem 2.5rem;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 2rem;
  border-radius: var(--r-xl);
  background: linear-gradient(135deg, rgba(99,102,241,0.08) 0%, rgba(139,92,246,0.05) 100%);
}

.hero-mesh {
  position: absolute;
  inset: 0;
  background: var(--gradient-mesh);
  opacity: 0.6;
  pointer-events: none;
}

.hero-content { position: relative; z-index: 1; flex: 1; }

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: var(--accent-dim);
  border: 1px solid var(--border-accent);
  color: var(--accent-light);
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.3rem 0.75rem;
  border-radius: var(--r-full);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-bottom: 1rem;
}

.hero-title {
  font-size: clamp(1.75rem, 4vw, 2.75rem);
  font-weight: 800;
  line-height: 1.15;
  letter-spacing: -0.03em;
  margin-bottom: 0.875rem;
}

.hero-gradient-text {
  background: var(--gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  color: var(--text-secondary);
  font-size: 1.0625rem;
  line-height: 1.6;
  max-width: 480px;
  margin-bottom: 2rem;
}

.hero-actions { display: flex; gap: 1rem; flex-wrap: wrap; }

/* Hero visual */
.hero-visual {
  position: relative;
  width: 200px;
  height: 200px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.hero-ring {
  position: absolute;
  border-radius: 50%;
  border: 1px solid;
  animation: spin 20s linear infinite;
}
.hero-ring-1 { width: 180px; height: 180px; border-color: rgba(99,102,241,0.3); }
.hero-ring-2 { width: 130px; height: 130px; border-color: rgba(139,92,246,0.25); animation-direction: reverse; animation-duration: 15s; }
.hero-ring-3 { width: 80px;  height: 80px;  border-color: rgba(99,102,241,0.2); animation-duration: 10s; }

.hero-center-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: var(--gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-glow);
  animation: glow 3s ease-in-out infinite;
  z-index: 1;
}

/* KPI */
.kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; }

/* Main grid */
.home-main-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 1.25rem;
  align-items: start;
}

/* Section titles */
.card-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.25rem;
}

.section-title {
  font-size: 0.9375rem;
  font-weight: 700;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.section-title-icon { font-size: 1rem; }

/* Item list */
.item-list { display: flex; flex-direction: column; gap: 0.5rem; }

.item-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1rem;
  border-radius: var(--r-md);
  border: 1px solid var(--glass-border);
  cursor: pointer;
  transition: all var(--dur) var(--ease);
}
.item-row:hover {
  border-color: var(--border-accent);
  background: var(--accent-dim);
  transform: translateX(4px);
}

.item-row-info { flex: 1; min-width: 0; }
.item-row-title { font-weight: 600; font-size: 0.875rem; color: var(--text-primary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.item-row-meta  { font-size: 0.75rem; color: var(--text-muted); margin-top: 0.15rem; }
.item-row-arrow { color: var(--text-muted); flex-shrink: 0; }

.mini-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.mini-empty {
  text-align: center;
  padding: 1.5rem;
}

/* Quick Actions */
.quick-actions-panel { display: flex; flex-direction: column; gap: 1.25rem; }

.shortcuts-list { display: flex; flex-direction: column; gap: 0.375rem; }

.shortcut-item {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  padding: 0.75rem 1rem;
  border-radius: var(--r-md);
  border: 1px solid var(--glass-border);
  cursor: pointer;
  text-decoration: none;
  color: var(--text-primary);
  transition: all var(--dur) var(--ease);
}
.shortcut-item:hover {
  border-color: var(--border-accent);
  background: var(--accent-dim);
  transform: translateX(4px);
}

.shortcut-icon-box {
  width: 36px;
  height: 36px;
  border-radius: var(--r-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.shortcut-accent  { background: var(--accent-dim); color: var(--accent-light); }
.shortcut-violet  { background: var(--violet-dim); color: var(--violet-light); }
.shortcut-success { background: var(--success-dim); color: var(--success); }
.shortcut-warning { background: var(--warning-dim); color: var(--warning); }

.shortcut-text { flex: 1; min-width: 0; }
.shortcut-text strong { display: block; font-size: 0.875rem; font-weight: 600; }
.shortcut-text p { font-size: 0.75rem; color: var(--text-muted); margin-top: 0.1rem; }

/* Info card */
.info-card { padding: 1.25rem; }
.info-list { list-style: none; display: flex; flex-direction: column; gap: 0.6rem; }
.info-list li { font-size: 0.8125rem; color: var(--text-secondary); line-height: 1.5; }

@media (max-width: 1100px) {
  .home-main-grid { grid-template-columns: 1fr 1fr; }
  .quick-actions-panel { grid-column: span 2; display: grid; grid-template-columns: 1fr 1fr; }
}

@media (max-width: 768px) {
  .hero-banner { flex-direction: column; padding: 2rem 1.5rem; }
  .hero-visual { display: none; }
  .home-main-grid { grid-template-columns: 1fr; }
  .quick-actions-panel { grid-column: 1; display: flex; }
}
</style>
