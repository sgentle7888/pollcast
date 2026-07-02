<template>
  <div class="list-view animate-fade-in-up">
    <div class="page-header">
      <div>
        <h1 class="page-title">{{ activeTab === 'polls' ? 'Polls' : 'Surveys' }}</h1>
        <p class="page-subtitle">{{ activeTab === 'polls' ? 'Browse and vote on active polls.' : 'Browse and take active surveys.' }}</p>
      </div>
      <div class="header-actions">
        <RouterLink v-if="auth.isPollManager" to="/create" class="btn btn-primary">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          Create New
        </RouterLink>
      </div>
    </div>

    <!-- Type Tabs -->
    <div class="tab-bar" style="margin-bottom: 1.5rem;">
      <button :class="['tab-btn', { active: activeTab === 'polls' }]"   @click="setTab('polls')">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 12l2 2 4-4"/><path d="M5 7c0-1.1.9-2 2-2h10a2 2 0 0 1 2 2v12H5V7z"/></svg>
        Polls <span v-if="filteredPolls.length" class="tab-count">{{ filteredPolls.length }}</span>
      </button>
      <button :class="['tab-btn', { active: activeTab === 'surveys' }]" @click="setTab('surveys')">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/><rect x="9" y="3" width="6" height="4" rx="1"/></svg>
        Surveys <span v-if="filteredSurveys.length" class="tab-count">{{ filteredSurveys.length }}</span>
      </button>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar card-glass" style="padding: 0.875rem 1.25rem; margin-bottom: 1.5rem;">
      <div class="search-wrap" style="flex: 1;">
        <svg class="search-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        <input type="text" class="form-control search-input" v-model="search" :placeholder="'Search ' + activeTab + '…'" />
      </div>
      <select class="form-control" v-model="statusFilter" style="width: 140px;">
        <option value="">All Statuses</option>
        <option value="Active">Active</option>
        <option value="Draft">Draft</option>
        <option value="Closed">Closed</option>
        <option value="Archived">Archived</option>
      </select>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div><p>Loading…</p>
    </div>

    <!-- ── POLLS grid ── -->
    <div v-else-if="activeTab === 'polls'">
      <div v-if="filteredPolls.length === 0" class="empty-state card">
        <div class="empty-icon">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M9 12l2 2 4-4"/><path d="M5 7c0-1.1.9-2 2-2h10a2 2 0 0 1 2 2v12H5V7z"/></svg>
        </div>
        <h3>No polls found</h3>
        <p class="text-secondary">{{ search || statusFilter ? 'Try adjusting your filters.' : 'No polls have been created yet.' }}</p>
        <button v-if="search || statusFilter" class="btn btn-secondary btn-sm" @click="resetFilters" style="margin-top: 0.75rem;">Clear filters</button>
      </div>
      <div v-else class="items-grid">
        <div v-for="poll in filteredPolls" :key="poll.name" class="item-card card card-interactive animate-fade-in-up">
          <div class="item-card-top">
            <span :class="['badge', 'badge-' + (poll.status || 'draft').toLowerCase()]">{{ poll.status }}</span>
            <span class="item-date text-muted text-xs">{{ formatDate(poll.creation) }}</span>
          </div>
          <h3 class="item-title">{{ poll.title }}</h3>
          <p v-if="poll.description" class="item-desc text-secondary text-sm">{{ stripHtml(poll.description) }}</p>
          <div class="item-meta">
            <span class="meta-chip">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/></svg>
              {{ poll.total_responses || 0 }} votes
            </span>
          </div>
          <div class="divider"></div>
          <div class="item-actions">
            <RouterLink v-if="poll.status === 'Active'" :to="'/polls/' + poll.name" class="btn btn-primary btn-sm flex-1">
              Vote Now
            </RouterLink>
            <RouterLink v-if="(poll.total_responses || 0) > 0" :to="'/polls/' + poll.name + '/results'" class="btn btn-secondary btn-sm flex-1">
              Results
            </RouterLink>
            <div v-if="auth.isPollManager" class="dropdown" @click.stop>
              <button class="btn btn-ghost btn-icon btn-sm" @click="toggleMenu(poll.name)">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="1"/><circle cx="12" cy="5" r="1"/><circle cx="12" cy="19" r="1"/></svg>
              </button>
              <div v-if="openMenu === poll.name" class="dropdown-menu">
                <button v-if="poll.status !== 'Active'"  class="dropdown-item" @click="updatePollStatus(poll, 'Active')">Activate</button>
                <button v-if="poll.status !== 'Closed'"  class="dropdown-item danger" @click="updatePollStatus(poll, 'Closed')">Close</button>
                <button v-if="poll.status !== 'Archived'" class="dropdown-item" @click="updatePollStatus(poll, 'Archived')">Archive</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ── SURVEYS grid ── -->
    <div v-else-if="activeTab === 'surveys'">
      <div v-if="filteredSurveys.length === 0" class="empty-state card">
        <div class="empty-icon">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/><rect x="9" y="3" width="6" height="4" rx="1"/></svg>
        </div>
        <h3>No surveys found</h3>
        <p class="text-secondary">{{ search || statusFilter ? 'Try adjusting your filters.' : 'No surveys have been created yet.' }}</p>
        <button v-if="search || statusFilter" class="btn btn-secondary btn-sm" @click="resetFilters" style="margin-top: 0.75rem;">Clear filters</button>
      </div>
      <div v-else class="items-grid">
        <div v-for="survey in filteredSurveys" :key="survey.name" class="item-card card card-interactive animate-fade-in-up">
          <div class="item-card-top">
            <span :class="['badge', 'badge-' + (survey.status || 'draft').toLowerCase()]">{{ survey.status }}</span>
            <span class="item-date text-muted text-xs">{{ formatDate(survey.creation) }}</span>
          </div>
          <h3 class="item-title">{{ survey.title }}</h3>
          <p v-if="survey.description" class="item-desc text-secondary text-sm">{{ stripHtml(survey.description) }}</p>
          <div class="item-meta">
            <span class="meta-chip">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/></svg>
              {{ survey.total_responses || 0 }} responses
            </span>
            <span class="meta-chip">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
              {{ survey.question_count || 0 }} questions
            </span>
          </div>
          <div class="divider"></div>
          <div class="item-actions">
            <RouterLink v-if="survey.status === 'Active'" :to="'/surveys/' + survey.name" class="btn btn-primary btn-sm flex-1">
              Take Survey
            </RouterLink>
            <RouterLink v-if="(survey.total_responses || 0) > 0" :to="'/surveys/' + survey.name + '/results'" class="btn btn-secondary btn-sm flex-1">
              Results
            </RouterLink>
            <div v-if="auth.isPollManager" class="dropdown" @click.stop>
              <button class="btn btn-ghost btn-icon btn-sm" @click="toggleMenu(survey.name)">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="1"/><circle cx="12" cy="5" r="1"/><circle cx="12" cy="19" r="1"/></svg>
              </button>
              <div v-if="openMenu === survey.name" class="dropdown-menu">
                <button v-if="survey.status !== 'Active'"  class="dropdown-item" @click="updateSurveyStatus(survey, 'Active')">Activate</button>
                <button v-if="survey.status !== 'Closed'"  class="dropdown-item danger" @click="updateSurveyStatus(survey, 'Closed')">Close</button>
                <button v-if="survey.status !== 'Archived'" class="dropdown-item" @click="updateSurveyStatus(survey, 'Archived')">Archive</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import { useAuthStore } from "../stores/auth.js";
import { frappeCall } from "../api/frappe.js";

const auth  = useAuthStore();
const route = useRoute();

const activeTab    = ref(route.meta?.tab === "surveys" ? "surveys" : "polls");
const loading      = ref(true);
const search       = ref("");
const statusFilter = ref("");
const openMenu     = ref(null);
const polls        = ref([]);
const surveys      = ref([]);

const setTab = (tab) => { activeTab.value = tab; resetFilters(); };
const resetFilters = () => { search.value = ""; statusFilter.value = ""; };

const filteredPolls = computed(() =>
  polls.value.filter(p => {
    const matchSearch = !search.value || p.title.toLowerCase().includes(search.value.toLowerCase());
    const matchStatus = !statusFilter.value || p.status === statusFilter.value;
    return matchSearch && matchStatus;
  })
);

const filteredSurveys = computed(() =>
  surveys.value.filter(s => {
    const matchSearch = !search.value || s.title.toLowerCase().includes(search.value.toLowerCase());
    const matchStatus = !statusFilter.value || s.status === statusFilter.value;
    return matchSearch && matchStatus;
  })
);

const toggleMenu = (name) => { openMenu.value = openMenu.value === name ? null : name; };

onMounted(async () => {
  document.addEventListener("click", () => { openMenu.value = null; });
  try {
    const [p, s] = await Promise.all([
      frappeCall("pollcast.api.get_polls"),
      frappeCall("pollcast.api.get_surveys"),
    ]);
    polls.value   = p || [];
    surveys.value = s || [];
  } catch (e) {
    console.error("List load error:", e);
  } finally {
    loading.value = false;
  }
});

const updatePollStatus = async (poll, status) => {
  openMenu.value = null;
  try {
    await frappeCall("pollcast.api.update_poll_status", { poll_name: poll.name, status });
    poll.status = status;
  } catch (e) { alert("Error: " + e.message); }
};

const updateSurveyStatus = async (survey, status) => {
  openMenu.value = null;
  try {
    await frappeCall("pollcast.api.update_survey_status", { survey_name: survey.name, status });
    survey.status = status;
  } catch (e) { alert("Error: " + e.message); }
};

const formatDate = (d) => {
  if (!d) return "";
  const dt = new Date(d);
  return dt.toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" });
};

const stripHtml = (html) => {
  const tmp = document.createElement("div");
  tmp.innerHTML = html;
  return (tmp.textContent || "").slice(0, 100);
};
</script>

<style scoped>
.list-view { display: flex; flex-direction: column; }

.filter-bar { display: flex; gap: 1rem; align-items: center; }

.items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.25rem;
}

.item-card { display: flex; flex-direction: column; }
.item-card-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.875rem; }
.item-date { flex-shrink: 0; }
.item-title { font-size: 1.0625rem; font-weight: 700; margin-bottom: 0.5rem; line-height: 1.3; }
.item-desc  { font-size: 0.875rem; line-height: 1.5; margin-bottom: 0.75rem; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }

.item-meta { display: flex; gap: 0.75rem; margin-top: auto; }
.meta-chip {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.75rem;
  color: var(--text-muted);
  font-weight: 500;
}

.item-actions { display: flex; gap: 0.625rem; align-items: center; }
.flex-1 { flex: 1; }

.tab-count {
  background: var(--accent-dim);
  color: var(--accent-light);
  font-size: 0.65rem;
  padding: 0.1rem 0.4rem;
  border-radius: var(--r-full);
  font-weight: 700;
  margin-left: 0.25rem;
}
</style>
