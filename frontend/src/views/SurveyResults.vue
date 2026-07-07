<template>
  <div class="survey-results-view animate-fade-in-up">
    <!-- Header -->
    <div class="page-header" v-if="survey">
      <div>
        <div class="breadcrumbs">
          <RouterLink to="/surveys">Surveys</RouterLink><span class="sep">/</span>
          <span class="current">{{ survey.title }} Results</span>
        </div>
        <h1 class="page-title">📊 {{ survey.title }} Results</h1>
        <p class="page-subtitle" v-if="survey.description" v-html="survey.description"></p>
      </div>
      <div class="header-actions">
        <button class="btn btn-secondary btn-sm" @click="printPage">
          Export PDF
        </button>
        <button class="btn btn-secondary btn-sm" @click="exportData('csv')" :disabled="exporting">
          <span v-if="exporting" class="spinner spinner-sm"></span>
          <span v-else>Export CSV</span>
        </button>
        <RouterLink v-if="survey.status === 'Active'" :to="'/surveys/' + survey.name" class="btn btn-primary btn-sm">
          Take Survey
        </RouterLink>
        <RouterLink to="/surveys" class="btn btn-secondary btn-sm">
          Back to List
        </RouterLink>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Fetching survey results...</p>
    </div>

    <!-- Empty/No Data -->
    <div v-else-if="!analytics || analytics.survey.total_responses === 0" class="empty-state card">
      <div class="empty-icon">📊</div>
      <h3>No Responses Yet</h3>
      <p class="text-secondary">No customer or participant satisfaction scores have been logged for this survey yet.</p>
      <div style="margin-top: 1rem; display: flex; gap: 1rem;">
        <RouterLink v-if="survey?.status === 'Active'" :to="'/surveys/' + survey?.name" class="btn btn-primary btn-sm">
          ✍️ Submit First Response
        </RouterLink>
      </div>
    </div>

    <!-- Main Results Grid -->
    <div v-else class="results-grid">
      <!-- KPIs -->
      <div class="kpi-row kpi-grid" style="margin-bottom: 1.5rem;">
        <div class="stat-card card animate-fade-in-up stagger-1">
          <div class="stat-icon stat-icon-accent">👥</div>
          <div class="stat-body">
            <span class="stat-label">Total Responses</span>
            <span class="stat-value">{{ analytics.survey.total_responses }}</span>
          </div>
        </div>
        <div class="stat-card card animate-fade-in-up stagger-2">
          <div class="stat-icon stat-icon-violet">⭐</div>
          <div class="stat-body">
            <span class="stat-label">Avg Completion Rate</span>
            <span class="stat-value">{{ analytics.survey.completion_rate }}%</span>
          </div>
        </div>
        <div class="stat-card card animate-fade-in-up stagger-3">
          <div class="stat-icon stat-icon-success">🎯</div>
          <div class="stat-body">
            <span class="stat-label">Unique Respondents</span>
            <span class="stat-value">{{ analytics.survey.unique_respondents }}</span>
          </div>
        </div>
        <div class="stat-card card animate-fade-in-up stagger-4">
          <div class="stat-icon stat-icon-warning">⏱️</div>
          <div class="stat-body">
            <span class="stat-label">Avg. Completion Time</span>
            <span class="stat-value" style="font-size: 1.5rem;">{{ analytics.survey.avg_completion_time ? analytics.survey.avg_completion_time + 'm' : 'N/A' }}</span>
          </div>
        </div>
      </div>

      <!-- Charts Row -->
      <div v-if="hasRatingQuestions" class="grid-2" style="margin-bottom: 1.5rem;">
        <!-- Radar performance map -->
        <div class="card chart-card animate-fade-in-up stagger-2">
          <div class="chart-header">
            <span class="chart-title">Performance Radar Map</span>
          </div>
          <div class="chart-container-lg">
            <canvas ref="radarChartRef"></canvas>
          </div>
        </div>

        <!-- Bar ratings chart -->
        <div class="card chart-card animate-fade-in-up stagger-3">
          <div class="chart-header">
            <span class="chart-title">Criteria Average Scores</span>
          </div>
          <div class="chart-container-lg">
            <canvas ref="barChartRef"></canvas>
          </div>
        </div>
      </div>

      <!-- Detailed Breakdown -->
      <div class="card animate-fade-in-up stagger-4" style="margin-bottom: 1.5rem;">
        <h3 class="section-title" style="margin-bottom: 1rem;">Detailed Question Analytics</h3>
        <div class="question-analytics-list">
          <div v-for="(q, index) in analytics.question_analytics" :key="q.question_id" class="card-elevated" style="margin-bottom: 1rem; padding: 1.25rem;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 0.75rem;">
              <div>
                <span class="badge badge-neutral" style="margin-right: 0.5rem;">Q{{ index + 1 }}</span>
                <span class="badge badge-accent">{{ q.question_type }}</span>
              </div>
              <span class="text-xs text-muted">{{ q.total_responses }} responses</span>
            </div>
            <h4 style="margin-bottom: 0.75rem; font-size: 1rem;">{{ q.question_text }}</h4>

            <!-- Rating distribution -->
            <div v-if="q.question_type === 'Rating Scale'" class="rating-breakdown">
              <div class="rating-score-pill" style="margin-bottom: 0.75rem;">
                Average Rating: <strong class="text-accent" style="font-size: 1.15rem; margin-left: 0.25rem;">{{ q.average_rating }} / 5.0</strong>
              </div>
              <div class="distribution-bars">
                <div v-for="score in ['5','4','3','2','1']" :key="score" class="dist-row">
                  <span class="dist-score">{{ score }}★</span>
                  <div class="progress-track" style="flex: 1; height: 8px;">
                    <div class="progress-fill" :style="{ width: getRatingPct(q, score) + '%', background: getRatingColor(score) }"></div>
                  </div>
                  <span class="dist-count">{{ q.rating_distribution?.[score] ?? 0 }}</span>
                </div>
              </div>
            </div>

            <!-- Choice options breakdown -->
            <div v-if="q.question_type === 'Multiple Choice' || q.question_type === 'Checkbox'" class="choices-breakdown">
              <div v-for="(count, opt) in q.option_counts" :key="opt" class="dist-row">
                <span class="dist-score" style="min-width: 120px; font-weight: 500;">{{ opt }}</span>
                <div class="progress-track" style="flex: 1; height: 8px;">
                  <div class="progress-fill" :style="{ width: getOptionPct(q, count) + '%' }"></div>
                </div>
                <span class="dist-count">{{ count }} ({{ getOptionPct(q, count) }}%)</span>
              </div>
            </div>

            <!-- Text responses -->
            <div v-if="q.question_type === 'Text Input'" class="text-responses-breakdown">
              <div class="sentiment-box" style="margin-bottom: 0.75rem;" v-if="q.sentiment_summary">
                Sentiment: 
                <span :class="['badge', 'badge-' + (q.sentiment_summary.sentiment || 'neutral')]">
                  {{ q.sentiment_summary.sentiment }}
                </span>
                <span class="text-xs text-muted" style="margin-left: 0.5rem;" v-if="q.sentiment_summary.confidence">
                  (Confidence: {{ Math.round(q.sentiment_summary.confidence * 100) }}%)
                </span>
              </div>
              <div class="comments-list">
                <div v-for="(comment, cidx) in q.text_responses" :key="cidx" class="comment-bubble">
                  {{ comment }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, inject } from "vue";
import { useRoute } from "vue-router";
import { frappeCall } from "../api/frappe.js";
import Chart from "chart.js/auto";

const route = useRoute();
const toast = inject("toast");

const printPage = () => {
  window.print();
};

const loading = ref(true);
const exporting = ref(false);
const survey = ref(null);
const analytics = ref(null);

const radarChartRef = ref(null);
const barChartRef = ref(null);
let radarChart = null;
let barChart = null;

const hasRatingQuestions = computed(() => {
  if (!analytics.value || !analytics.value.question_analytics) return false;
  return analytics.value.question_analytics.some(
    (q) => q.question_type === "Rating Scale"
  );
});

onMounted(async () => {
  try {
    const sDoc = await frappeCall("pollcast.api.get_survey", { survey_name: route.params.name });
    if (!sDoc || sDoc.error) {
      toast?.("Survey not found", "error");
      return;
    }
    survey.value = sDoc;

    const data = await frappeCall("pollcast.api.get_survey_analytics", { survey_id: route.params.name });
    if (data && !data.error) {
      analytics.value = data;
    }
  } catch (e) {
    console.error("Survey results load error:", e);
    toast?.(e.message, "error");
  } finally {
    loading.value = false;
    await nextTick();
    renderCharts();
  }
});

const getRatingPct = (q, score) => {
  if (!q.total_responses) return 0;
  const count = q.rating_distribution?.[score] ?? 0;
  return Math.round((count / q.total_responses) * 100);
};

const getOptionPct = (q, count) => {
  if (!q.total_responses) return 0;
  return Math.round((count / q.total_responses) * 100);
};

const getRatingColor = (score) => {
  const colors = { 1: "#EF4444", 2: "#F97316", 3: "#F59E0B", 4: "#84CC16", 5: "#22C55E" };
  return colors[score] || "var(--accent)";
};

const renderCharts = () => {
  if (!analytics.value || !analytics.value.question_analytics) return;

  const ratingQuestions = analytics.value.question_analytics.filter(
    (q) => q.question_type === "Rating Scale"
  );
  if (ratingQuestions.length === 0) return;

  const labels = ratingQuestions.map((q) =>
    q.question_text.length > 25 ? q.question_text.slice(0, 25) + "…" : q.question_text
  );
  const scores = ratingQuestions.map((q) => q.average_rating || 0);

  // 1. Radar Chart
  if (radarChartRef.value) {
    if (radarChart) radarChart.destroy();
    radarChart = new Chart(radarChartRef.value.getContext("2d"), {
      type: "radar",
      data: {
        labels,
        datasets: [
          {
            label: "Average score",
            data: scores,
            backgroundColor: "rgba(99, 102, 241, 0.2)",
            borderColor: "rgba(99, 102, 241, 0.8)",
            pointBackgroundColor: "rgba(99, 102, 241, 1)",
            pointBorderColor: "#fff",
            borderWidth: 2,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          r: {
            angleLines: { color: "rgba(255,255,255,0.06)" },
            grid: { color: "rgba(255,255,255,0.06)" },
            pointLabels: { color: "#94A3B8", font: { size: 10 } },
            ticks: { display: false, stepSize: 1 },
            min: 0,
            max: 5,
          },
        },
      },
    });
  }

  // 2. Bar Chart
  if (barChartRef.value) {
    if (barChart) barChart.destroy();
    barChart = new Chart(barChartRef.value.getContext("2d"), {
      type: "bar",
      data: {
        labels,
        datasets: [
          {
            label: "Score",
            data: scores,
            backgroundColor: scores.map((s) => {
              if (s >= 4.0) return "rgba(34, 197, 94, 0.75)";
              if (s >= 3.0) return "rgba(245, 158, 11, 0.75)";
              return "rgba(239, 68, 68, 0.75)";
            }),
            borderRadius: 6,
            borderSkipped: false,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: {
            grid: { color: "rgba(255,255,255,0.04)" },
            ticks: { color: "#94A3B8", font: { size: 10 } },
          },
          y: {
            grid: { color: "rgba(255,255,255,0.04)" },
            ticks: { color: "#94A3B8", font: { size: 11 } },
            min: 0,
            max: 5,
          },
        },
      },
    });
  }
};

const exportData = async (format) => {
  exporting.value = true;
  try {
    const result = await frappeCall("pollcast.api.export_analytics", {
      options: { surveys: true, responses: true },
      format,
    });
    if (result && result.error) {
      toast?.("Export Failed: " + result.error, "error");
      return;
    }
    if (result && result.content) {
      // Decode base64 and trigger a browser download
      const byteChars = atob(result.content);
      const byteNumbers = new Uint8Array(byteChars.length);
      for (let i = 0; i < byteChars.length; i++) {
        byteNumbers[i] = byteChars.charCodeAt(i);
      }
      const blob = new Blob([byteNumbers], { type: result.mime || "text/csv" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = result.filename || "pollcast_analytics.csv";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      toast?.("CSV downloaded successfully!", "success");
    }
  } catch (e) {
    toast?.("Export Failed: " + e.message, "error");
  } finally {
    exporting.value = false;
  }
};
</script>

<style scoped>
.survey-results-view { display: flex; flex-direction: column; }

.results-grid { display: flex; flex-direction: column; }

.dist-row { display: flex; align-items: center; gap: 0.75rem; font-size: 0.8125rem; margin-bottom: 0.4rem; }
.dist-score { min-width: 32px; color: var(--text-secondary); font-weight: 600; }
.dist-count { min-width: 24px; text-align: right; color: var(--text-muted); font-weight: 500; }

.comment-bubble {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: var(--r-md);
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
  line-height: 1.4;
}
.comment-bubble:last-child { margin-bottom: 0; }
</style>
