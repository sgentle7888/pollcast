<template>
  <div class="analytics-view animate-fade-in-up">
    <div class="page-header">
      <div>
        <h1 class="page-title">Analytics</h1>
        <p class="page-subtitle">Real-time response data, trends, and performance insights.</p>
      </div>
      <div class="header-actions">
        <div class="tab-bar">
          <button :class="['tab-btn', { active: activeTab === 'overview' }]" @click="activeTab = 'overview'">Overview</button>
          <button :class="['tab-btn', { active: activeTab === 'polls' }]"    @click="activeTab = 'polls'">Polls</button>
          <button :class="['tab-btn', { active: activeTab === 'surveys' }]"  @click="activeTab = 'surveys'">Surveys</button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading analytics…</p>
    </div>

    <template v-else>

      <!-- ── OVERVIEW TAB ── -->
      <div v-if="activeTab === 'overview'" class="animate-fade-in-up">
        <!-- KPIs -->
        <div class="kpi-grid" style="margin-bottom: 1.5rem;">
          <div class="card stat-card">
            <div class="stat-icon stat-icon-accent">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 12l2 2 4-4"/><path d="M5 7c0-1.1.9-2 2-2h10a2 2 0 0 1 2 2v12H5V7z"/></svg>
            </div>
            <div class="stat-body">
              <div class="stat-label">Active Polls</div>
              <div class="stat-value">{{ summary.activePolls ?? 0 }}</div>
            </div>
          </div>
          <div class="card stat-card">
            <div class="stat-icon stat-icon-violet">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/><rect x="9" y="3" width="6" height="4" rx="1"/></svg>
            </div>
            <div class="stat-body">
              <div class="stat-label">Active Surveys</div>
              <div class="stat-value">{{ summary.activeSurveys ?? 0 }}</div>
            </div>
          </div>
          <div class="card stat-card">
            <div class="stat-icon stat-icon-success">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 16 12 14 15 10 15 8 12 2 12"/><path d="M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"/></svg>
            </div>
            <div class="stat-body">
              <div class="stat-label">Total Responses</div>
              <div class="stat-value">{{ summary.totalResponses ?? 0 }}</div>
            </div>
          </div>
          <div class="card stat-card">
            <div class="stat-icon stat-icon-warning">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
            </div>
            <div class="stat-body">
              <div class="stat-label">Engagement Rate</div>
              <div class="stat-value">{{ summary.engagementRate ?? 0 }}%</div>
            </div>
          </div>
        </div>

        <!-- Charts row -->
        <div class="grid-2" style="margin-bottom: 1.5rem;">
          <div class="card chart-card">
            <div class="chart-header">
              <span class="chart-title">Top Polls by Votes</span>
            </div>
            <div class="chart-container">
              <canvas ref="pollsBarRef"></canvas>
            </div>
          </div>
          <div class="card chart-card">
            <div class="chart-header">
              <span class="chart-title">Top Surveys by Responses</span>
            </div>
            <div class="chart-container">
              <canvas ref="surveysBarRef"></canvas>
            </div>
          </div>
        </div>
      </div>

      <!-- ── POLLS TAB ── -->
      <div v-if="activeTab === 'polls'" class="animate-fade-in-up">
        <div class="kpi-grid" style="margin-bottom: 1.5rem;">
          <div class="card stat-card">
            <div class="stat-icon stat-icon-accent">🗳️</div>
            <div class="stat-body">
              <div class="stat-label">Active Polls</div>
              <div class="stat-value">{{ pollSummary.activePolls ?? 0 }}</div>
            </div>
          </div>
          <div class="card stat-card">
            <div class="stat-icon stat-icon-success">📊</div>
            <div class="stat-body">
              <div class="stat-label">Total Votes</div>
              <div class="stat-value">{{ pollSummary.totalPollResponses ?? 0 }}</div>
            </div>
          </div>
          <div class="card stat-card">
            <div class="stat-icon stat-icon-warning">🏆</div>
            <div class="stat-body">
              <div class="stat-label">Top Poll</div>
              <div class="stat-value" style="font-size: 1rem; line-height: 1.3;">{{ pollSummary.topPollTitle ?? 'N/A' }}</div>
              <div class="stat-trend">{{ pollSummary.topPollResponses ?? 0 }} votes</div>
            </div>
          </div>
        </div>

        <!-- Polls list with analytics -->
        <div class="analytics-list">
          <div v-if="pollsData.length === 0" class="empty-state card">
            <div class="empty-icon">🗳️</div>
            <h3>No poll data</h3>
            <p class="text-secondary">No active polls with responses yet.</p>
          </div>
          <div v-for="poll in pollsData" :key="poll.name" class="card analytics-item animate-fade-in-up">
            <div class="analytics-item-header">
              <div>
                <span class="badge badge-active">Active</span>
                <h3 style="margin-top: 0.5rem; font-size: 1rem;">{{ poll.title }}</h3>
              </div>
              <RouterLink :to="'/polls/' + poll.name + '/results'" class="btn btn-secondary btn-sm">View Results</RouterLink>
            </div>
            <div class="options-breakdown">
              <div v-for="opt in (poll.options || []).slice(0, 5)" :key="opt.option_id" class="option-row">
                <div class="option-label">{{ opt.option_text }}</div>
                <div class="option-bar-wrap">
                  <div class="progress-track" style="flex: 1;">
                    <div class="progress-fill" :style="{ width: opt.percentage + '%', background: 'var(--gradient)' }"></div>
                  </div>
                  <span class="option-pct">{{ opt.percentage }}%</span>
                  <span class="option-count">{{ opt.vote_count }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ── SURVEYS TAB ── -->
      <div v-if="activeTab === 'surveys'" class="animate-fade-in-up">
        <div class="kpi-grid" style="margin-bottom: 1.5rem;">
          <div class="card stat-card">
            <div class="stat-icon stat-icon-violet">📋</div>
            <div class="stat-body">
              <div class="stat-label">Active Surveys</div>
              <div class="stat-value">{{ surveySummary.activeSurveys ?? 0 }}</div>
            </div>
          </div>
          <div class="card stat-card">
            <div class="stat-icon stat-icon-success">✅</div>
            <div class="stat-body">
              <div class="stat-label">Total Responses</div>
              <div class="stat-value">{{ surveySummary.totalSurveyResponses ?? 0 }}</div>
            </div>
          </div>
          <div class="card stat-card">
            <div class="stat-icon stat-icon-warning">⭐</div>
            <div class="stat-body">
              <div class="stat-label">Avg. Rating</div>
              <div class="stat-value">{{ surveySummary.avgRating ?? 'N/A' }}</div>
            </div>
          </div>
          <div class="card stat-card">
            <div class="stat-icon stat-icon-accent">📈</div>
            <div class="stat-body">
              <div class="stat-label">Avg Completion</div>
              <div class="stat-value">{{ surveySummary.avgCompletionRate ?? 0 }}%</div>
            </div>
          </div>
        </div>

        <div class="analytics-list">
          <div v-if="surveysData.length === 0" class="empty-state card">
            <div class="empty-icon">📋</div>
            <h3>No survey data</h3>
            <p class="text-secondary">No active surveys with responses yet.</p>
          </div>
          <div v-for="survey in surveysData" :key="survey.name" class="card analytics-item animate-fade-in-up">
            <div class="analytics-item-header">
              <div>
                <span class="badge badge-active">Active</span>
                <h3 style="margin-top: 0.5rem; font-size: 1rem;">{{ survey.title }}</h3>
              </div>
              <RouterLink :to="'/surveys/' + survey.name + '/results'" class="btn btn-secondary btn-sm">View Results</RouterLink>
            </div>
            <div class="survey-qs-preview">
              <div v-for="q in (survey.questions || []).slice(0, 3)" :key="q.question_id" class="sq-row">
                <span class="sq-type badge badge-neutral">{{ q.question_type }}</span>
                <span class="sq-text">{{ q.question_text }}</span>
                <span class="sq-responses">{{ q.total_responses }} resp.</span>
              </div>
            </div>
          </div>
        </div>
      </div>

    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from "vue";
import { frappeCall } from "../api/frappe.js";
import Chart from "chart.js/auto";

const activeTab = ref("overview");
const loading   = ref(true);

const summary       = ref({});
const pollSummary   = ref({});
const surveySummary = ref({});
const pollsData     = ref([]);
const surveysData   = ref([]);

const pollsBarRef   = ref(null);
const surveysBarRef = ref(null);
let pollsBarChart   = null;
let surveysBarChart = null;

onMounted(async () => {
  try {
    const [s, ps, ss, pd, sd] = await Promise.all([
      frappeCall("pollcast.api.get_dashboard_summary"),
      frappeCall("pollcast.api.get_polls_dashboard_summary"),
      frappeCall("pollcast.api.get_surveys_dashboard_summary"),
      frappeCall("pollcast.api.get_polls_analytics"),
      frappeCall("pollcast.api.get_surveys_analytics"),
    ]);
    summary.value       = s  || {};
    pollSummary.value   = ps || {};
    surveySummary.value = ss || {};
    pollsData.value     = Array.isArray(pd) ? pd : [];
    surveysData.value   = Array.isArray(sd) ? sd : [];
  } catch (e) {
    console.error("Analytics load error:", e);
  } finally {
    loading.value = false;
    await nextTick();
    renderCharts();
  }
});

watch(activeTab, async () => {
  await nextTick();
  if (activeTab.value === "overview") renderCharts();
});

const renderCharts = () => {
  renderPollsBar();
  renderSurveysBar();
};

const chartDefaults = {
  responsive: true, maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: {
    x: { grid: { color: "rgba(255,255,255,0.04)" }, ticks: { color: "#94A3B8", font: { size: 11 } } },
    y: { grid: { color: "rgba(255,255,255,0.04)" }, ticks: { color: "#94A3B8", font: { size: 11 } } },
  },
};

const renderPollsBar = () => {
  if (!pollsBarRef.value) return;
  if (pollsBarChart) pollsBarChart.destroy();
  const data = pollsData.value.slice(0, 6);
  if (!data.length) return;
  pollsBarChart = new Chart(pollsBarRef.value.getContext("2d"), {
    type: "bar",
    data: {
      labels: data.map(p => p.title.length > 20 ? p.title.slice(0, 20) + "…" : p.title),
      datasets: [{ label: "Votes", data: data.map(p => p.total_responses),
        backgroundColor: "rgba(99,102,241,0.7)", borderRadius: 6, borderSkipped: false }],
    },
    options: chartDefaults,
  });
};

const renderSurveysBar = () => {
  if (!surveysBarRef.value) return;
  if (surveysBarChart) surveysBarChart.destroy();
  const data = surveysData.value.slice(0, 6);
  if (!data.length) return;
  surveysBarChart = new Chart(surveysBarRef.value.getContext("2d"), {
    type: "bar",
    data: {
      labels: data.map(s => s.title.length > 20 ? s.title.slice(0, 20) + "…" : s.title),
      datasets: [{ label: "Responses", data: data.map(s => s.total_responses),
        backgroundColor: "rgba(139,92,246,0.7)", borderRadius: 6, borderSkipped: false }],
    },
    options: chartDefaults,
  });
};
</script>

<style scoped>
.analytics-view { display: flex; flex-direction: column; gap: 0; }

.analytics-list { display: flex; flex-direction: column; gap: 1rem; }

.analytics-item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.25rem;
  gap: 1rem;
}

.options-breakdown { display: flex; flex-direction: column; gap: 0.625rem; }
.option-row { display: flex; align-items: center; gap: 0.75rem; font-size: 0.875rem; }
.option-label { min-width: 140px; color: var(--text-secondary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.option-bar-wrap { display: flex; align-items: center; gap: 0.75rem; flex: 1; }
.option-pct  { font-size: 0.75rem; font-weight: 700; color: var(--text-primary); min-width: 36px; text-align: right; }
.option-count { font-size: 0.7rem; color: var(--text-muted); min-width: 32px; text-align: right; }

.survey-qs-preview { display: flex; flex-direction: column; gap: 0.5rem; }
.sq-row { display: flex; align-items: center; gap: 0.75rem; font-size: 0.8125rem; }
.sq-type { flex-shrink: 0; }
.sq-text { flex: 1; color: var(--text-secondary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.sq-responses { font-size: 0.7rem; color: var(--text-muted); flex-shrink: 0; }
</style>
