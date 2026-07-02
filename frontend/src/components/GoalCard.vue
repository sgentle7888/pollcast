<template>
  <RouterLink :to="`/goals/${goal.name}`" class="goal-card-link">
    <div class="goal-card">
      <!-- Header row -->
      <div class="goal-card-header">
        <span class="goal-cycle">{{ goal.appraisal_cycle || "—" }}</span>
        <span :class="['badge', statusClass]" style="text-transform: uppercase;">{{ goal.status }}</span>
      </div>

      <!-- Title -->
      <h3 class="goal-title">{{ goal.goal }}</h3>

      <!-- Employee Info -->
      <div class="employee-info" v-if="employeeName">
        <div class="avatar">{{ initials }}</div>
        <span class="employee-name">{{ employeeName }}</span>
      </div>

      <!-- Progress -->
      <div class="goal-progress">
        <div class="progress-row">
          <span class="progress-label">PROGRESS</span>
          <span class="progress-value">{{ goal.progress || 0 }}%</span>
        </div>
        <div class="progress-track">
          <div :class="['progress-fill', progressClass]" :style="{ width: `${goal.progress || 0}%` }"></div>
        </div>
      </div>

      <!-- Footer -->
      <div class="goal-card-footer">
        <div class="goal-dates" v-if="goal.start_date">
          <span>{{ formatDate(goal.start_date) }}</span>
          <span v-if="goal.end_date"> → {{ formatDate(goal.end_date) }}</span>
        </div>
        <span class="view-link" style="text-transform: uppercase;">DETAILS →</span>
      </div>
    </div>
  </RouterLink>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  goal: { type: Object, required: true },
});

const employeeName = window.frappe_user && window.frappe_user !== "Administrator" ? window.frappe_user : "Godwin Ariwodo";

const initials = computed(() => {
  if (!employeeName) return "GA";
  return employeeName.split(" ").map(n => n[0]).join("").substring(0, 2).toUpperCase();
});

const statusMap = {
  "Not Started": "badge-neutral",
  "In Progress": "badge-info",
  "Completed":   "badge-success",
  "Cancelled":   "badge-danger",
};

const statusClass = computed(() => {
  return props.goal.status ? statusMap[props.goal.status] || "badge-neutral" : "badge-neutral";
});

const progressClass = computed(() => {
  if (props.goal.status === 'Completed') return 'success';
  if (props.goal.status === 'In Progress') return 'info';
  return '';
});

function formatDate(dateStr) {
  if (!dateStr) return "";
  return new Date(dateStr).toLocaleDateString("en-GB", {
    day: "2-digit", month: "short", year: "numeric",
  }).toUpperCase();
}
</script>

<style scoped>
.goal-card-link { text-decoration: none; display: block; }

.goal-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  cursor: pointer;
  transition: all var(--transition);
  height: 100%;
}
.goal-card:hover {
  border-color: var(--border-hover);
  box-shadow: var(--shadow-lg);
  transform: translateY(-4px);
}

.goal-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.goal-cycle {
  font-size: 0.65rem;
  color: var(--text-muted);
  font-weight: 600;
  text-transform: uppercase;
  border: 1px solid var(--border);
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  letter-spacing: 0.05em;
}

.goal-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  letter-spacing: -0.01em;
}

.employee-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: rgba(99, 102, 241, 0.1);
  color: var(--accent-light);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.6rem;
  font-weight: 700;
}

.employee-name {
  font-size: 0.8125rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.goal-progress { display: flex; flex-direction: column; gap: 0.5rem; margin-top: auto; }
.progress-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.progress-label { font-size: 0.65rem; font-weight: 600; color: var(--text-muted); letter-spacing: 0.05em; }
.progress-value { font-size: 0.875rem; font-weight: 800; color: var(--text-primary); }

.goal-card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 1rem;
  border-top: 1px solid var(--border);
}
.goal-dates { font-size: 0.65rem; color: var(--text-muted); font-weight: 500; letter-spacing: 0.05em; }
.view-link {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--accent-light);
  transition: color var(--transition);
}
.goal-card:hover .view-link { color: var(--accent); }
</style>
