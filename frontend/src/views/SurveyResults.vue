<template>
  <div class="survey-results-view animate-fade-in-up">
    <!-- Header -->
    <div class="page-header" v-if="survey">
      <div>
        <div class="breadcrumbs">
          <RouterLink to="/surveys">Surveys</RouterLink
          ><span class="sep">/</span>
          <span class="current">{{ survey.title }} Results</span>
        </div>
        <h1 class="page-title">📊 {{ survey.title }} Results</h1>
        <div
          class="page-subtitle rich-description"
          v-if="sanitizedDescription"
          v-html="sanitizedDescription"
        ></div>
      </div>
      <div class="header-actions">
        <!-- Analytics tab actions -->
        <template v-if="activeTab === 'analytics'">
          <button class="btn btn-secondary btn-sm" @click="printPage">
            Export PDF
          </button>
          <button
            class="btn btn-secondary btn-sm"
            @click="exportData('csv')"
            :disabled="exporting"
          >
            <span v-if="exporting" class="spinner spinner-sm"></span>
            <span v-else>Export CSV</span>
          </button>
        </template>
        <!-- Respondents tab actions -->
        <template v-if="activeTab === 'respondents'">
          <button class="btn btn-secondary btn-sm" @click="printRespondents">
            🖨️ Export PDF
          </button>
          <button
            class="btn btn-primary btn-sm"
            @click="exportRespondentsExcel"
            :disabled="exportingRespondents"
          >
            <span v-if="exportingRespondents" class="spinner spinner-sm"></span>
            <span v-else>📥 Export Excel</span>
          </button>
        </template>
        <RouterLink
          v-if="survey.status === 'Active'"
          :to="'/surveys/' + survey.name"
          class="btn btn-primary btn-sm"
        >
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
    <div
      v-else-if="!analytics || analytics.survey.total_responses === 0"
      class="empty-state card"
    >
      <div class="empty-icon">📊</div>
      <h3>No Responses Yet</h3>
      <p class="text-secondary">
        No customer or participant satisfaction scores have been logged for this
        survey yet.
      </p>
      <div style="margin-top: 1rem; display: flex; gap: 1rem">
        <RouterLink
          v-if="survey?.status === 'Active'"
          :to="'/surveys/' + survey?.name"
          class="btn btn-primary btn-sm"
        >
          ✍️ Submit First Response
        </RouterLink>
      </div>
    </div>

    <!-- Tab navigation -->
    <div v-else class="results-tabs-wrapper">
      <div class="results-tab-bar">
        <button
          class="results-tab-btn"
          :class="{ active: activeTab === 'analytics' }"
          @click="activeTab = 'analytics'"
        >📊 Analytics Overview</button>
        <button
          class="results-tab-btn"
          :class="{ active: activeTab === 'respondents' }"
          @click="switchToRespondents"
        >👤 Individual Respondents</button>
      </div>

    <!-- Main Results Grid -->
    <div v-show="activeTab === 'analytics'" class="results-grid">
      <!-- KPIs -->
      <div class="kpi-row kpi-grid" style="margin-bottom: 1.5rem">
        <div class="stat-card card animate-fade-in-up stagger-1">
          <div class="stat-icon stat-icon-accent">👥</div>
          <div class="stat-body">
            <span class="stat-label">Total Responses</span>
            <span class="stat-value">{{
              analytics.survey.total_responses
            }}</span>
          </div>
        </div>
        <div class="stat-card card animate-fade-in-up stagger-2">
          <div class="stat-icon stat-icon-violet">⭐</div>
          <div class="stat-body">
            <span class="stat-label">Avg Completion Rate</span>
            <span class="stat-value"
              >{{ analytics.survey.completion_rate }}%</span
            >
          </div>
        </div>
        <div class="stat-card card animate-fade-in-up stagger-3">
          <div class="stat-icon stat-icon-success">🎯</div>
          <div class="stat-body">
            <span class="stat-label">Unique Respondents</span>
            <span class="stat-value">{{
              analytics.survey.unique_respondents
            }}</span>
          </div>
        </div>
        <div class="stat-card card animate-fade-in-up stagger-4">
          <div class="stat-icon stat-icon-warning">⏱️</div>
          <div class="stat-body">
            <span class="stat-label">Avg. Completion Time</span>
            <span class="stat-value" style="font-size: 1.5rem">{{
              analytics.survey.avg_completion_time
                ? analytics.survey.avg_completion_time + "m"
                : "N/A"
            }}</span>
          </div>
        </div>
      </div>

      <!-- Charts Row -->
      <div
        v-if="hasRatingQuestions"
        class="grid-2"
        style="margin-bottom: 1.5rem"
      >
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
      <div
        class="card animate-fade-in-up stagger-4"
        style="margin-bottom: 1.5rem"
      >
        <h3 class="section-title" style="margin-bottom: 1rem">
          Detailed Question Analytics
        </h3>
        <div class="choice-chart-toolbar" v-if="hasChoiceQuestions">
          <span class="text-xs text-muted">Choice question display</span>
          <select
            v-model="choiceChartType"
            class="choice-chart-select"
            @change="nextTick(renderAllChoiceCharts)"
            aria-label="Chart type for choice questions"
          >
            <option value="breakdown">Percentage breakdown</option>
            <option value="bar">Bar chart</option>
            <option value="pie">Pie chart</option>
            <option value="doughnut">Doughnut chart</option>
          </select>
        </div>
        <div class="question-analytics-list">
          <div
            v-for="(q, index) in analytics.question_analytics"
            :key="q.question_id"
            class="card-elevated"
            style="margin-bottom: 1rem; padding: 1.25rem"
          >
            <div
              style="
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                flex-wrap: wrap;
                gap: 0.5rem;
                margin-bottom: 0.75rem;
              "
            >
              <div>
                <span class="badge badge-neutral" style="margin-right: 0.5rem"
                  >Q{{ index + 1 }}</span
                >
                <span class="badge badge-accent">{{ q.question_type }}</span>
              </div>
              <span class="text-xs text-muted"
                >{{ q.total_responses }} responses</span
              >
            </div>
            <h4 style="margin-bottom: 0.75rem; font-size: 1rem">
              {{ q.question_text }}
            </h4>

            <!-- Rating distribution -->
            <div
              v-if="q.question_type === 'Rating Scale'"
              class="rating-breakdown"
            >
              <div class="rating-score-pill" style="margin-bottom: 0.75rem">
                Average Rating:
                <strong
                  class="text-accent"
                  style="font-size: 1.15rem; margin-left: 0.25rem"
                  >{{ q.average_rating }} / 5.0</strong
                >
              </div>
              <div class="distribution-bars">
                <div
                  v-for="score in ['5', '4', '3', '2', '1']"
                  :key="score"
                  class="dist-row"
                >
                  <span class="dist-score">{{ score }}★</span>
                  <div class="progress-track" style="flex: 1; height: 8px">
                    <div
                      class="progress-fill"
                      :style="{
                        width: getRatingPct(q, score) + '%',
                        background: getRatingColor(score),
                      }"
                    ></div>
                  </div>
                  <span class="dist-count">{{
                    q.rating_distribution?.[score] ?? 0
                  }}</span>
                </div>
              </div>
            </div>

            <!-- Choice options breakdown -->
            <div
              v-if="
                q.question_type === 'Multiple Choice' ||
                q.question_type === 'Checkbox'
              "
              class="choices-breakdown"
            >
              <div
                v-if="choiceChartType !== 'breakdown'"
                class="choice-chart-row"
              >
                <div class="choice-chart-container">
                  <canvas
                    :ref="
                      (element) => setChoiceChartRef(q.question_id, element)
                    "
                  ></canvas>
                </div>

                <!-- Custom HTML legend: lets us keep rows tight while still
                     giving the legend column room to breathe next to the chart. -->
                <ul
                  v-if="
                    choiceChartType === 'pie' || choiceChartType === 'doughnut'
                  "
                  class="chart-legend"
                >
                  <li
                    v-for="item in getChoiceLegend(q)"
                    :key="item.label"
                    class="chart-legend-item"
                  >
                    <span
                      class="chart-legend-dot"
                      :style="{ background: item.color }"
                    ></span>
                    <span class="chart-legend-label">{{ item.label }}</span>
                  </li>
                </ul>
              </div>

              <div v-if="choiceChartType === 'breakdown'">
                <div
                  v-for="(count, opt) in q.option_counts"
                  :key="opt"
                  class="dist-row"
                >
                  <span
                    class="dist-score"
                    style="min-width: 120px; font-weight: 500"
                    >{{ opt }}</span
                  >
                  <div class="progress-track" style="flex: 1; height: 8px">
                    <div
                      class="progress-fill"
                      :style="{ width: getOptionPct(q, count) + '%' }"
                    ></div>
                  </div>
                  <span class="dist-count"
                    >{{ count }} ({{ getOptionPct(q, count) }}%)</span
                  >
                </div>
              </div>
            </div>

            <!-- Text responses -->
            <div
              v-if="q.question_type === 'Text Input'"
              class="text-responses-breakdown"
            >
              <div
                class="sentiment-box"
                style="margin-bottom: 0.75rem"
                v-if="q.sentiment_summary"
              >
                Sentiment:
                <span
                  :class="[
                    'badge',
                    'badge-' + (q.sentiment_summary.sentiment || 'neutral'),
                  ]"
                >
                  {{ q.sentiment_summary.sentiment }}
                </span>
                <span
                  class="text-xs text-muted"
                  style="margin-left: 0.5rem"
                  v-if="q.sentiment_summary.confidence"
                >
                  (Confidence:
                  {{ Math.round(q.sentiment_summary.confidence * 100) }}%)
                </span>
              </div>
              <div class="comments-list">
                <div
                  v-for="(comment, cidx) in getVisibleTextResponses(q)"
                  :key="cidx"
                  class="comment-bubble"
                >
                  {{ comment }}
                </div>
              </div>
              <button
                v-if="
                  (q.text_responses?.length || 0) > TEXT_RESPONSES_PAGE_SIZE
                "
                type="button"
                class="btn btn-secondary btn-sm show-more-btn"
                @click="toggleTextResponses(q.question_id)"
              >
                {{
                  isTextResponsesExpanded(q.question_id)
                    ? "Show less"
                    : `Show all ${q.text_responses.length} responses`
                }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- END analytics tab -->

    <!-- ===== RESPONDENT VIEW TAB ===== -->
    <div v-show="activeTab === 'respondents'" class="respondents-tab" id="respondents-print-area">
      <div v-if="loadingRespondents" class="loading-state">
        <div class="spinner"></div>
        <p>Loading respondent data…</p>
      </div>
      <div v-else-if="respondentsError" class="empty-state card">
        <div class="empty-icon">⚠️</div>
        <p class="text-secondary">{{ respondentsError }}</p>
      </div>
      <div v-else-if="!respondentsData || respondentsData.respondents.length === 0" class="empty-state card">
        <div class="empty-icon">👤</div>
        <h3>No Respondents Yet</h3>
        <p class="text-secondary">Responses will appear here once participants submit the survey.</p>
      </div>
      <div v-else class="respondents-content">
        <p class="respondents-meta">
          Showing <strong>{{ respondentsData.respondents.length }}</strong> respondent(s) ·
          <strong>{{ respondentsData.questions.length }}</strong> question(s)
        </p>

        <!-- Each respondent as a card -->
        <div
          v-for="resp in respondentsData.respondents"
          :key="resp.respondent_number"
          class="respondent-card card-elevated"
        >
          <!-- Card header -->
          <div class="respondent-card-header">
            <span class="respondent-badge"># {{ resp.respondent_number }}</span>
            <span class="respondent-time">🕐 {{ resp.submitted_at }}</span>
            <span class="respondent-ip">🌐 {{ resp.participant_ip }}</span>
          </div>

          <!-- Answers grid -->
          <div class="respondent-answers">
            <div
              v-for="q in respondentsData.questions"
              :key="q.id"
              class="respondent-answer-row"
            >
              <div class="respondent-q-label">{{ q.text }}</div>
              <div
                class="respondent-q-answer"
                :class="{ 'no-answer': !resp.answers[q.id] }"
              >
                {{ resp.answers[q.id] || '— (no answer)' }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- END respondents tab -->

    </div><!-- close results-tabs-wrapper -->
  </div>
</template>

<script setup>
import {
  ref,
  computed,
  onMounted,
  nextTick,
  inject,
  onBeforeUnmount,
} from "vue";
import { useRoute } from "vue-router";
import { frappeCall } from "../api/frappe.js";
import Chart from "chart.js/auto";
import DOMPurify from "dompurify";

const route = useRoute();
const toast = inject("toast");

// ========== Tab state ==========
const activeTab = ref('analytics');

// ========== Respondent view state ==========
const respondentsData = ref(null);
const loadingRespondents = ref(false);
const exportingRespondents = ref(false);
const respondentsError = ref(null);

const switchToRespondents = async () => {
  activeTab.value = 'respondents';
  if (respondentsData.value !== null) return; // already loaded
  loadingRespondents.value = true;
  respondentsError.value = null;
  try {
    const result = await frappeCall('pollcast.api.get_survey_respondents', {
      survey_id: route.params.name,
    });
    if (result && result.error) {
      respondentsError.value = result.error;
    } else {
      respondentsData.value = result;
    }
  } catch (e) {
    respondentsError.value = e.message || 'Failed to load respondent data';
  } finally {
    loadingRespondents.value = false;
  }
};

const printRespondents = () => {
  // Temporarily hide the analytics tab, print, then restore
  const analyticsEl = document.querySelector('.results-grid');
  const tabBar = document.querySelector('.results-tab-bar');
  const headerActions = document.querySelector('.header-actions');
  if (analyticsEl) analyticsEl.style.display = 'none';
  if (tabBar) tabBar.style.display = 'none';
  if (headerActions) headerActions.style.display = 'none';
  window.print();
  if (analyticsEl) analyticsEl.style.display = '';
  if (tabBar) tabBar.style.display = '';
  if (headerActions) headerActions.style.display = '';
};

const exportRespondentsExcel = async () => {
  exportingRespondents.value = true;
  try {
    const result = await frappeCall('pollcast.api.export_survey_respondents', {
      survey_id: route.params.name,
      export_format: 'excel',
    });
    if (result && result.error) {
      toast?.('Export Failed: ' + result.error, 'error');
      return;
    }
    if (result && result.content) {
      const byteChars = atob(result.content);
      const byteNumbers = new Uint8Array(byteChars.length);
      for (let i = 0; i < byteChars.length; i++) {
        byteNumbers[i] = byteChars.charCodeAt(i);
      }
      const blob = new Blob([byteNumbers], { type: result.mime });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = result.filename || 'respondents.xlsx';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      toast?.('Excel downloaded successfully!', 'success');
    }
  } catch (e) {
    toast?.('Export Failed: ' + e.message, 'error');
  } finally {
    exportingRespondents.value = false;
  }
};

const printPage = () => {
  window.print();
};

const loading = ref(true);
const exporting = ref(false);
const survey = ref(null);
const analytics = ref(null);
const sanitizedDescription = computed(() =>
  DOMPurify.sanitize(survey.value?.description || ""),
);

const radarChartRef = ref(null);
const barChartRef = ref(null);
const choiceChartType = ref("pie");
const choiceChartRefs = ref({});

// Text-answer questions can have hundreds of responses; only show a first
// page of each and let the user expand it, rather than rendering everything.
const TEXT_RESPONSES_PAGE_SIZE = 10;
const expandedTextResponses = ref({});

const isTextResponsesExpanded = (questionId) =>
  !!expandedTextResponses.value[questionId];

const toggleTextResponses = (questionId) => {
  expandedTextResponses.value = {
    ...expandedTextResponses.value,
    [questionId]: !expandedTextResponses.value[questionId],
  };
};

const getVisibleTextResponses = (q) => {
  const all = q.text_responses || [];
  return isTextResponsesExpanded(q.question_id)
    ? all
    : all.slice(0, TEXT_RESPONSES_PAGE_SIZE);
};
let radarChart = null;
let barChart = null;
const choiceCharts = new Map();

const hasRatingQuestions = computed(() => {
  if (!analytics.value || !analytics.value.question_analytics) return false;
  return analytics.value.question_analytics.some(
    (q) => q.question_type === "Rating Scale",
  );
});

const hasChoiceQuestions = computed(() =>
  analytics.value?.question_analytics?.some(
    (q) =>
      q.question_type === "Multiple Choice" || q.question_type === "Checkbox",
  ),
);

onMounted(async () => {
  try {
    const sDoc = await frappeCall("pollcast.api.get_survey", {
      survey_name: route.params.name,
    });
    if (!sDoc || sDoc.error) {
      toast?.("Survey not found", "error");
      return;
    }
    survey.value = sDoc;

    const data = await frappeCall("pollcast.api.get_survey_analytics", {
      survey_id: route.params.name,
    });
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
  const colors = {
    1: "#EF4444",
    2: "#F97316",
    3: "#F59E0B",
    4: "#84CC16",
    5: "#22C55E",
  };
  return colors[score] || "var(--accent)";
};

const setChoiceChartRef = (questionId, element) => {
  if (element) choiceChartRefs.value[questionId] = element;
};

const getChoiceLegend = (question) => {
  const entries = Object.entries(question.option_counts || {});
  const colors = getChoiceChartColors(entries.length);
  return entries.map(([label], index) => ({ label, color: colors[index] }));
};

const getChoiceChartColors = (count) => {
  const colors = [
    "#6366F1",
    "#22C55E",
    "#F59E0B",
    "#EF4444",
    "#06B6D4",
    "#EC4899",
    "#84CC16",
    "#F97316",
  ];
  return Array.from(
    { length: count },
    (_, index) => colors[index % colors.length],
  );
};

const renderChoiceChart = (question) => {
  const chartType = choiceChartType.value;
  const existingChart = choiceCharts.get(question.question_id);
  if (existingChart) {
    existingChart.destroy();
    choiceCharts.delete(question.question_id);
  }
  if (chartType === "breakdown") return;

  const canvas = choiceChartRefs.value[question.question_id];
  if (!canvas) return;

  const entries = Object.entries(question.option_counts || {});
  const labels = entries.map(([option]) => option);
  const values = entries.map(([, count]) => count);
  const colors = getChoiceChartColors(labels.length);
  const percentageLabelsPlugin = {
    id: "choicePercentageLabels",
    afterDatasetsDraw(chartInstance) {
      if (chartType !== "pie" && chartType !== "doughnut") return;

      const context = chartInstance.ctx;
      const meta = chartInstance.getDatasetMeta(0);
      const total = values.reduce((sum, value) => sum + Number(value || 0), 0);
      if (!total) return;

      context.save();
      context.fillStyle = "#FFFFFF";
      context.font = "600 12px sans-serif";
      context.textAlign = "center";
      context.textBaseline = "middle";

      meta.data.forEach((arc, index) => {
        const percentage = Math.round(
          (Number(values[index] || 0) / total) * 100,
        );
        if (!percentage) return;
        const { x, y } = arc.getCenterPoint();
        context.fillText(`${percentage}%`, x, y);
      });

      context.restore();
    },
  };

  const chart = new Chart(canvas.getContext("2d"), {
    type: chartType === "bar" ? "bar" : chartType,
    data: {
      labels,
      datasets: [
        {
          label: "Responses",
          data: values,
          backgroundColor: colors,
          borderColor: "rgba(255, 255, 255, 0.7)",
          borderWidth: 1,
          borderRadius: chartType === "bar" ? 5 : 0,
        },
      ],
    },
    plugins: [percentageLabelsPlugin],
    options: {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: chartType === "bar" ? "y" : "x",
      plugins: {
        // Pie/doughnut now use the custom HTML legend in the template
        // (independent control of row spacing vs. chart gap). Bar charts
        // never showed a legend either way.
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (context) => {
              const count = context.raw || 0;
              return `${count} responses (${getOptionPct(question, count)}%)`;
            },
          },
        },
      },
      scales:
        chartType === "bar"
          ? {
              x: {
                beginAtZero: true,
                ticks: { color: "#94A3B8", precision: 0 },
                grid: { color: "rgba(255,255,255,0.04)" },
              },
              y: {
                ticks: { color: "#94A3B8" },
                grid: { display: false },
              },
            }
          : {},
    },
  });
  choiceCharts.set(question.question_id, chart);
};

const renderAllChoiceCharts = () => {
  if (!analytics.value) return;
  analytics.value.question_analytics
    .filter(
      (q) =>
        q.question_type === "Multiple Choice" || q.question_type === "Checkbox",
    )
    .forEach(renderChoiceChart);
};

const renderCharts = () => {
  if (!analytics.value || !analytics.value.question_analytics) return;

  const ratingQuestions = analytics.value.question_analytics.filter(
    (q) => q.question_type === "Rating Scale",
  );

  renderAllChoiceCharts();

  if (ratingQuestions.length === 0) return;

  const labels = ratingQuestions.map((q) =>
    q.question_text.length > 25
      ? q.question_text.slice(0, 25) + "…"
      : q.question_text,
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

onBeforeUnmount(() => {
  radarChart?.destroy();
  barChart?.destroy();
  choiceCharts.forEach((chart) => chart.destroy());
});

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
.survey-results-view {
  display: flex;
  flex-direction: column;
}

.results-grid {
  display: flex;
  flex-direction: column;
}

.dist-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.8125rem;
  margin-bottom: 0.4rem;
}
.dist-score {
  min-width: 32px;
  color: var(--text-secondary);
  font-weight: 600;
}
.dist-count {
  min-width: 24px;
  text-align: right;
  color: var(--text-muted);
  font-weight: 500;
}

.choice-chart-toolbar {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.choice-chart-select {
  border: 1px solid var(--glass-border);
  border-radius: var(--r-sm);
  background: var(--glass-bg);
  color: var(--text-primary);
  padding: 0.35rem 0.5rem;
  font-size: 0.8125rem;
}

.choice-chart-row {
  display: flex;
  align-items: center;
  /* Gap between the chart and the legend column — tune independently
     of the row spacing below. */
  gap: 2rem;
  margin-bottom: 0.75rem;
  flex-wrap: wrap;
}

.choice-chart-container {
  height: 200px;
  width: 200px;
  flex-shrink: 0;
}

.chart-legend {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  /* Vertical space between legend rows — set this as tight as you like. */
  gap: 0.35rem;
}

.chart-legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.chart-legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.chart-legend-label {
  font-size: 0.8125rem;
  color: var(--text-secondary, #94a3b8);
}

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
.comment-bubble:last-child {
  margin-bottom: 0;
}

.show-more-btn {
  display: block;
  margin: 0.5rem auto 0;
}

/* ===== Tabs ===== */
.results-tabs-wrapper {
  display: flex;
  flex-direction: column;
}

.results-tab-bar {
  display: flex;
  gap: 0;
  border-bottom: 2px solid var(--glass-border);
  margin-bottom: 1.5rem;
}

.results-tab-btn {
  padding: 0.6rem 1.4rem;
  background: transparent;
  border: none;
  border-bottom: 3px solid transparent;
  margin-bottom: -2px;
  color: var(--text-secondary);
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: color 0.2s, border-color 0.2s;
  border-radius: var(--r-sm) var(--r-sm) 0 0;
}
.results-tab-btn:hover {
  color: var(--text-primary);
  background: var(--glass-bg);
}
.results-tab-btn.active {
  color: var(--accent, #6366f1);
  border-bottom-color: var(--accent, #6366f1);
  font-weight: 600;
}

/* ===== Respondent view ===== */
.respondents-tab {
  display: flex;
  flex-direction: column;
}

.respondents-meta {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-bottom: 1rem;
}

.respondents-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.respondent-card {
  border-radius: var(--r-md);
  padding: 1.25rem;
  border: 1px solid var(--glass-border);
  background: var(--card-bg, var(--glass-bg));
  break-inside: avoid;
}

.respondent-card-header {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--glass-border);
}

.respondent-badge {
  background: var(--accent, #6366f1);
  color: #fff;
  font-size: 0.8125rem;
  font-weight: 700;
  padding: 0.2rem 0.65rem;
  border-radius: 999px;
}

.respondent-time {
  font-size: 0.8125rem;
  color: var(--text-secondary);
}

.respondent-ip {
  font-size: 0.8125rem;
  color: var(--text-muted);
  margin-left: auto;
}

.respondent-answers {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.respondent-answer-row {
  display: grid;
  grid-template-columns: minmax(160px, 35%) 1fr;
  gap: 0.75rem;
  align-items: start;
  font-size: 0.875rem;
  padding: 0.5rem 0;
  border-bottom: 1px dashed var(--glass-border);
}
.respondent-answer-row:last-child {
  border-bottom: none;
}

.respondent-q-label {
  color: var(--text-secondary);
  font-weight: 600;
  line-height: 1.4;
}

.respondent-q-answer {
  color: var(--text-primary);
  line-height: 1.5;
  word-break: break-word;
}

.respondent-q-answer.no-answer {
  color: var(--text-muted);
  font-style: italic;
}

/* ===== Print styles for respondents ===== */
@media print {
  .results-tab-bar,
  .header-actions,
  .page-header .btn,
  .results-grid {
    display: none !important;
  }
  .respondents-tab {
    display: flex !important;
  }
  .respondent-card {
    page-break-inside: avoid;
    box-shadow: none;
    border: 1px solid #d1d5db;
  }
}
</style>
