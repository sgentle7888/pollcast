<template>
  <div class="poll-results-view animate-fade-in-up">

    <!-- Loading -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div><p>Loading results…</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="error-state card" style="text-align: center; padding: 3rem;">
      <p class="text-danger" style="font-size: 1.25rem; margin-bottom: 1rem;">⚠️ {{ error }}</p>
      <RouterLink to="/polls" class="btn btn-secondary">← Back to Polls</RouterLink>
    </div>

    <div v-else-if="analytics">
      <!-- Header -->
      <div class="page-header">
        <div>
          <div class="breadcrumbs">
            <RouterLink to="/polls">Polls</RouterLink><span class="sep">/</span>
            <span class="current">{{ analytics.poll.title }} Results</span>
          </div>
          <h1 class="page-title">📊 {{ analytics.poll.title }} Results</h1>
          <p class="page-subtitle">Real-time vote counts and participant distribution.</p>
        </div>
        <div class="header-actions">
          <button class="btn btn-secondary btn-sm" @click="printPage">
            Export PDF
          </button>
          <RouterLink v-if="analytics.poll.status === 'Active'" :to="'/polls/' + analytics.poll.name" class="btn btn-primary btn-sm">
            Vote
          </RouterLink>
          <RouterLink to="/polls" class="btn btn-secondary btn-sm">Back to Polls</RouterLink>
        </div>
      </div>

      <!-- KPIs -->
      <div class="kpi-grid" style="margin-bottom: 1.5rem;">
        <div class="stat-card card">
          <div class="stat-icon stat-icon-accent">👥</div>
          <div class="stat-body">
            <span class="stat-label">Total Votes</span>
            <span class="stat-value">{{ analytics.poll.total_votes }}</span>
          </div>
        </div>
        <div class="stat-card card">
          <div class="stat-icon stat-icon-violet">📈</div>
          <div class="stat-body">
            <span class="stat-label">Engagement Score</span>
            <span class="stat-value">{{ analytics.poll.participation_rate || 0 }}%</span>
          </div>
        </div>
        <div class="stat-card card" v-if="peakTime">
          <div class="stat-icon stat-icon-success">⚡</div>
          <div class="stat-body">
            <span class="stat-label">Peak Voting Date</span>
            <span class="stat-value" style="font-size: 1.25rem; font-weight: 700; line-height: 1.3;">{{ formatDateShort(peakTime.date) }}</span>
            <span class="stat-trend">{{ peakTime.votes }} votes</span>
          </div>
        </div>
      </div>

      <!-- Charts row -->
      <div class="grid-2" style="margin-bottom: 1.5rem;">
        <!-- Donut chart -->
        <div class="card chart-card">
          <div class="chart-header">
            <span class="chart-title">Vote Share</span>
          </div>
          <div class="chart-container-lg">
            <canvas ref="donutChartRef"></canvas>
          </div>
        </div>

        <!-- Details list -->
        <div class="card" style="display: flex; flex-direction: column; justify-content: space-between;">
          <h3 class="section-title" style="margin-bottom: 1.25rem;">Detailed Standings</h3>
          <div class="standings-list" style="display: flex; flex-direction: column; gap: 0.875rem; flex: 1; justify-content: center;">
            <div
              v-for="(opt, idx) in sortedOptions"
              :key="opt.option_id"
              class="card-elevated"
              style="padding: 0.875rem 1rem; border-radius: var(--r-md);"
            >
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                  <span :class="['rank-badge', getRankClass(idx)]">{{ idx + 1 }}</span>
                  <span class="font-semibold text-sm">{{ opt.option_text }}</span>
                </div>
                <div class="text-sm font-bold text-accent">
                  {{ opt.percentage }}% <span class="text-muted text-xs font-normal">({{ opt.vote_count }} votes)</span>
                </div>
              </div>
              <div class="progress-track" style="height: 6px;">
                <div
                  class="progress-fill"
                  :style="{ width: opt.percentage + '%', background: getBarGradient(idx) }"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from "vue";
import { useRoute } from "vue-router";
import { frappeCall } from "../api/frappe.js";
import Chart from "chart.js/auto";

const route = useRoute();

const printPage = () => {
  window.print();
};
const loading = ref(true);
const error = ref(null);
const analytics = ref(null);
const donutChartRef = ref(null);
let donutChart = null;

const sortedOptions = computed(() => {
  if (!analytics.value || !analytics.value.vote_distribution) return [];
  return [...analytics.value.vote_distribution].sort((a, b) => b.vote_count - a.vote_count);
});

const peakTime = computed(() => analytics.value?.poll?.peak_voting_time);

onMounted(async () => {
  try {
    const data = await frappeCall("pollcast.api.get_poll_analytics", {
      poll_id: route.params.name,
    });
    if (data && !data.error) {
      analytics.value = data;
    } else {
      error.value = data?.error || "Results not found";
    }
  } catch (e) {
    error.value = e.message;
  } finally {
    loading.value = false;
    await nextTick();
    renderChart();
  }
});

const getRankClass = (idx) => {
  if (idx === 0) return "rank-gold";
  if (idx === 1) return "rank-silver";
  if (idx === 2) return "rank-bronze";
  return "rank-normal";
};

const getBarGradient = (idx) => {
  if (idx === 0) return "var(--gradient)";
  if (idx === 1) return "linear-gradient(135deg, #8B5CF6 0%, #A78BFA 100%)";
  return "linear-gradient(135deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.03) 100%)";
};

const renderChart = () => {
  if (!donutChartRef.value || !analytics.value || !analytics.value.vote_distribution) return;
  if (donutChart) donutChart.destroy();

  const labels = analytics.value.vote_distribution.map((o) => o.option_text);
  const data = analytics.value.vote_distribution.map((o) => o.vote_count);

  donutChart = new Chart(donutChartRef.value.getContext("2d"), {
    type: "doughnut",
    data: {
      labels,
      datasets: [
        {
          data,
          backgroundColor: [
            "#6366F1",
            "#8B5CF6",
            "#EC4899",
            "#F59E0B",
            "#10B981",
            "#3B82F6",
            "#64748B",
          ],
          borderColor: "rgba(10,22,40,0.85)",
          borderWidth: 2,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "bottom",
          labels: { color: "#94A3B8", boxWidth: 12, font: { size: 11 } },
        },
      },
      cutout: "70%",
    },
  });
};

const formatDateShort = (d) => {
  if (!d) return "";
  const dt = new Date(d);
  return dt.toLocaleDateString("en-GB", { day: "numeric", month: "short" });
};
</script>

<style scoped>
.poll-results-view { padding: 2rem 0; }
</style>
