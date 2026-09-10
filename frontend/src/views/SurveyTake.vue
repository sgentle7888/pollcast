<template>
  <div class="survey-take animate-fade-in-up">
    <!-- Loading -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading survey…</p>
    </div>

    <!-- Error -->
    <div
      v-else-if="error"
      class="error-state card"
      style="text-align: center; padding: 3rem"
    >
      <p class="text-danger" style="font-size: 1.25rem; margin-bottom: 1rem">
        ⚠️ {{ error }}
      </p>
      <RouterLink to="/surveys" class="btn btn-secondary"
        >← Back to Surveys</RouterLink
      >
    </div>

    <!-- Success Screen -->
    <div v-else-if="submitted" class="success-screen card animate-fade-in-up">
      <div
        v-if="displayLogo || displayCompanyName"
        class="survey-success-brand-wrap"
      >
        <img
          v-if="displayLogo"
          :src="displayLogo"
          alt="Company Logo"
          class="survey-brand-logo"
        />
        <div v-if="displayCompanyName" class="survey-brand-name">
          {{ displayCompanyName }}
        </div>
      </div>
      <div class="success-icon">
        <svg
          width="36"
          height="36"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <polyline points="20 6 9 17 4 12" />
        </svg>
      </div>
      <h2>Thank you for your feedback!</h2>
      <p class="text-secondary" style="max-width: 400px">
        Your response to <strong>{{ survey.title }}</strong> has been recorded
        successfully.
      </p>
      <div
        style="
          display: flex;
          gap: 1rem;
          margin-top: 1.5rem;
          flex-wrap: wrap;
          justify-content: center;
        "
      >
        <RouterLink
          :to="'/surveys/' + survey.name + '/results'"
          class="btn btn-primary"
        >
          <svg
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <line x1="18" y1="20" x2="18" y2="10" />
            <line x1="12" y1="20" x2="12" y2="4" />
            <line x1="6" y1="20" x2="6" y2="14" />
          </svg>
          View Results
        </RouterLink>
        <RouterLink v-if="!auth.isGuest" to="/surveys" class="btn btn-secondary"
          >Back to Surveys</RouterLink
        >
      </div>
    </div>

    <!-- Survey Form -->
    <div v-else-if="survey">
      <!-- Branded Company Header (Shows centered in EVERY take survey interface) -->
      <div
        v-if="displayLogo || displayCompanyName"
        class="survey-brand-header card card-glass"
      >
        <div class="survey-brand-inner">
          <img
            v-if="displayLogo"
            :src="displayLogo"
            alt="Company Logo"
            class="survey-brand-logo"
          />
          <div v-if="displayCompanyName" class="survey-brand-name">
            {{ displayCompanyName }}
          </div>
        </div>
      </div>

      <!-- Header -->
      <div class="page-header">
        <div>
          <div class="breadcrumbs" v-if="!auth.isGuest">
            <RouterLink to="/surveys">Surveys</RouterLink
            ><span class="sep">/</span>
            <span class="current">{{ survey.title }}</span>
          </div>
          <h1 class="page-title">{{ survey.title }}</h1>
          <div
            v-if="sanitizedDescription"
            class="page-subtitle rich-description"
            v-html="sanitizedDescription"
          ></div>
        </div>
        <RouterLink v-if="!auth.isGuest" to="/surveys" class="btn btn-ghost">
          <svg
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <polyline points="15 18 9 12 15 6" />
          </svg>
          Back
        </RouterLink>
      </div>

      <!-- Progress bar -->
      <div
        class="progress-bar-wrap card-glass"
        style="padding: 0.875rem 1.25rem; margin-bottom: 1.5rem"
      >
        <div
          style="
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.5rem;
          "
        >
          <span class="text-sm font-semibold text-secondary">Progress</span>
          <span class="text-sm font-semibold text-accent"
            >{{ answeredCount }} / {{ totalRequired }} required questions</span
          >
        </div>
        <div class="progress-track">
          <div
            class="progress-fill"
            :style="{ width: progressPct + '%' }"
          ></div>
        </div>
      </div>

      <form @submit.prevent="submitSurvey">
        <!-- ───────── Participant Information ───────── -->
        <div
          class="card participant-info-section"
          style="margin-bottom: 1.5rem"
        >
          <h3 class="section-heading">
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              style="
                display: inline;
                vertical-align: middle;
                margin-right: 0.35rem;
              "
            >
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
              <circle cx="12" cy="7" r="4" />
            </svg>
            Participant Information
            <span class="optional-note">(Optional)</span>
          </h3>
          <p class="text-secondary text-sm" style="margin-bottom: 1.25rem">
            Your identity remains confidential. These fields help us analyse
            results by department.
          </p>
          <div class="participant-grid">
            <div class="form-group">
              <label class="form-label">Full Name</label>
              <input
                type="text"
                class="form-control"
                v-model="participant.name"
                placeholder="e.g. John Adeyemi"
              />
            </div>
            <div class="form-group">
              <label class="form-label">Department / Unit</label>
              <input
                type="text"
                class="form-control"
                v-model="participant.department"
                placeholder="e.g. Operations"
              />
            </div>
            <div class="form-group">
              <label class="form-label">Job Title</label>
              <input
                type="text"
                class="form-control"
                v-model="participant.jobTitle"
                placeholder="e.g. Senior Manager"
              />
            </div>
            <div class="form-group">
              <label class="form-label">Branch / Location</label>
              <input
                type="text"
                class="form-control"
                v-model="participant.branch"
                placeholder="e.g. Lagos Island"
              />
            </div>
            <div class="form-group">
              <label class="form-label">Years of Service</label>
              <select class="form-control" v-model="participant.yearsOfService">
                <option value="">Select range</option>
                <option value="Less than 1 year">Less than 1 year</option>
                <option value="1–3 years">1–3 years</option>
                <option value="3–5 years">3–5 years</option>
                <option value="5–10 years">5–10 years</option>
                <option value="10+ years">10+ years</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Ordered survey items when section headings are present -->
        <template v-if="hasSectionHeadings">
          <template v-for="q in survey.questions" :key="q.name">
            <div
              v-if="q.question_type === 'Section Heading'"
              class="survey-section-heading"
            >
              <h3>{{ q.question_text }}</h3>
            </div>
            <div
              v-else-if="q.question_type === 'Rating Scale'"
              class="card question-card ordered-rating-card"
              style="margin-bottom: 1rem"
            >
              <div class="question-title">
                {{ q.question_text }}
                <span v-if="q.required" class="mandatory-star">*</span>
              </div>
              <div class="ordered-rating-options">
                <label v-for="score in [1, 2, 3, 4, 5]" :key="score">
                  <input
                    type="radio"
                    :name="'q-' + q.name"
                    :value="String(score)"
                    v-model="responses[q.name]"
                  />
                  {{ score }}
                </label>
                <label>
                  <input
                    type="radio"
                    :name="'q-' + q.name"
                    value="N/A"
                    v-model="responses[q.name]"
                  />
                  N/A
                </label>
              </div>
            </div>
            <div
              v-else-if="
                q.question_type === 'Multiple Choice' ||
                q.question_type === 'Checkbox'
              "
              class="card question-card"
              style="margin-bottom: 1rem"
            >
              <div class="question-title">
                {{ q.question_text }}
                <span v-if="q.required" class="mandatory-star">*</span>
              </div>
              <label
                v-for="opt in q.options || []"
                :key="opt"
                class="choice-item"
              >
                <input
                  v-if="q.question_type === 'Checkbox'"
                  type="checkbox"
                  :name="'q-' + q.name"
                  :value="opt"
                  v-model="checkboxResponses[q.name]"
                  class="choice-check"
                />
                <input
                  v-else
                  type="radio"
                  :name="'q-' + q.name"
                  :value="opt"
                  v-model="responses[q.name]"
                  class="choice-radio"
                />
                <span class="choice-label">{{ opt }}</span>
              </label>
            </div>
            <div
              v-else-if="q.question_type === 'Text Input'"
              class="card question-card"
              style="margin-bottom: 1rem"
            >
              <div class="question-title">
                {{ q.question_text }}
                <span v-if="q.required" class="mandatory-star">*</span>
              </div>
              <textarea
                class="form-control"
                v-model="responses[q.name]"
                rows="4"
                placeholder="Your response…"
              ></textarea>
            </div>
          </template>
        </template>

        <!-- ───────── Rating Scale Questions (Tabular Matrix) ───────── -->
        <div
          v-if="!hasSectionHeadings && ratingQuestions.length > 0"
          class="card rating-matrix-section"
          style="margin-bottom: 1.5rem"
        >
          <h3 class="section-heading">
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              style="
                display: inline;
                vertical-align: middle;
                margin-right: 0.35rem;
              "
            >
              <polygon
                points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"
              />
            </svg>
            Rating Assessment
          </h3>
          <p class="text-secondary text-sm" style="margin-bottom: 0.5rem">
            Please rate each of the following on a scale of
            <strong>1 to 5</strong> where:
          </p>
          <div class="rating-legend">
            <span class="legend-item"><strong>1</strong> = Very Poor</span>
            <span class="legend-sep">·</span>
            <span class="legend-item"><strong>2</strong> = Poor</span>
            <span class="legend-sep">·</span>
            <span class="legend-item"><strong>3</strong> = Average</span>
            <span class="legend-sep">·</span>
            <span class="legend-item"><strong>4</strong> = Good</span>
            <span class="legend-sep">·</span>
            <span class="legend-item"><strong>5</strong> = Excellent</span>
            <span class="legend-sep">·</span>
            <span class="legend-item text-muted"
              ><strong>N/A</strong> = Not Applicable</span
            >
          </div>

          <div class="rating-table-wrap" style="margin-top: 1.25rem">
            <table class="rating-table">
              <thead>
                <tr>
                  <th>Criteria</th>
                  <th class="score-col-header">
                    1<br /><span class="score-label">Very Poor</span>
                  </th>
                  <th class="score-col-header">
                    2<br /><span class="score-label">Poor</span>
                  </th>
                  <th class="score-col-header">
                    3<br /><span class="score-label">Average</span>
                  </th>
                  <th class="score-col-header">
                    4<br /><span class="score-label">Good</span>
                  </th>
                  <th class="score-col-header">
                    5<br /><span class="score-label">Excellent</span>
                  </th>
                  <th class="na-col-header">N/A</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="q in ratingQuestions"
                  :key="q.name"
                  :class="['', { 'row-rated': responses[q.name] }]"
                >
                  <td>
                    <div class="criteria-label">
                      {{ q.question_text }}
                      <span v-if="q.required" class="mandatory-star">*</span>
                    </div>
                  </td>
                  <td v-for="score in [1, 2, 3, 4, 5]" :key="score">
                    <input
                      type="radio"
                      class="rating-radio"
                      :name="'q-' + q.name"
                      :value="String(score)"
                      v-model="responses[q.name]"
                      :style="{ '--dot-color': getRatingColor(score) }"
                    />
                  </td>
                  <td>
                    <input
                      type="radio"
                      class="rating-radio rating-radio-na"
                      :name="'q-' + q.name"
                      value="N/A"
                      v-model="responses[q.name]"
                    />
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- ───────── Multiple Choice / Checkbox Questions ───────── -->
        <div
          v-for="q in choiceQuestions"
          v-if="!hasSectionHeadings"
          :key="q.name"
          class="card question-card"
          style="margin-bottom: 1rem"
        >
          <div class="question-title">
            {{ q.question_text }}
            <span v-if="q.required" class="mandatory-star">*</span>
          </div>
          <div class="choices-list">
            <!-- Multiple Choice (radio) -->
            <label
              v-if="q.question_type === 'Multiple Choice'"
              v-for="opt in q.options || []"
              :key="opt"
              class="choice-item"
            >
              <input
                type="radio"
                :name="'q-' + q.name"
                :value="opt"
                v-model="responses[q.name]"
                class="choice-radio"
              />
              <span class="choice-label">{{ opt }}</span>
            </label>
            <!-- Checkbox -->
            <label
              v-if="q.question_type === 'Checkbox'"
              v-for="opt in q.options || []"
              :key="opt"
              class="choice-item"
            >
              <input
                type="checkbox"
                :value="opt"
                v-model="checkboxResponses[q.name]"
                class="choice-check"
              />
              <span class="choice-label">{{ opt }}</span>
            </label>
          </div>
        </div>

        <!-- ───────── Text Input Questions ───────── -->
        <div
          v-for="q in textQuestions"
          v-if="!hasSectionHeadings"
          :key="q.name"
          class="card question-card"
          style="margin-bottom: 1rem"
        >
          <div class="question-title">
            {{ q.question_text }}
            <span v-if="q.required" class="mandatory-star">*</span>
          </div>
          <textarea
            class="form-control"
            v-model="responses[q.name]"
            rows="4"
            :placeholder="'Your response…'"
          ></textarea>
        </div>

        <!-- ───────── Additional Comments ───────── -->
        <div class="card" style="margin-bottom: 1.5rem">
          <h3 class="section-heading">
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              style="
                display: inline;
                vertical-align: middle;
                margin-right: 0.35rem;
              "
            >
              <path
                d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"
              />
            </svg>
            Additional Comments
            <span class="optional-note">(Optional)</span>
          </h3>
          <textarea
            class="form-control"
            v-model="additionalComments"
            rows="5"
            placeholder="Please share any other observations, suggestions, or feedback that may be useful…"
          ></textarea>
        </div>

        <!-- Submit -->
        <div
          class="submit-section card-glass"
          style="padding: 1.5rem; border-radius: var(--r-lg)"
        >
          <div class="submit-row">
            <div class="submit-info">
              <span class="text-sm text-secondary">
                <span v-if="missingRequired.length === 0" class="text-success"
                  >✓ All required questions answered</span
                >
                <span v-else class="text-warning"
                  >⚠ {{ missingRequired.length }} required question(s) still
                  unanswered</span
                >
              </span>
            </div>
            <button
              type="submit"
              class="btn btn-primary btn-lg"
              :disabled="submitting || missingRequired.length > 0"
            >
              <span v-if="submitting">
                <div
                  class="spinner spinner-sm"
                  style="display: inline-block"
                ></div>
                Submitting…
              </span>
              <span v-else>
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2.5"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <polyline points="22 2 15 22 11 13 2 9 22 2" />
                </svg>
                Submit Response
              </span>
            </button>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch, inject } from "vue";
import { useRoute } from "vue-router";
import { useAuthStore } from "../stores/auth.js";
import { frappeCall } from "../api/frappe.js";
import DOMPurify from "dompurify";

const route = useRoute();
const auth = useAuthStore();
const toast = inject("toast");

const loading = ref(true);
const submitting = ref(false);
const submitted = ref(false);
const error = ref(null);
const survey = ref(null);

const displayLogo = computed(
  () =>
    survey.value?.company_logo ||
    auth.companyLogo ||
    window.pollcast_company_logo ||
    null,
);

const displayCompanyName = computed(() =>
  survey.value &&
  Object.prototype.hasOwnProperty.call(survey.value, "company_name")
    ? survey.value.company_name || ""
    : auth.companyName || window.pollcast_company_name || "",
);

const sanitizedDescription = computed(() =>
  DOMPurify.sanitize(survey.value?.description || ""),
);

// Responses: { [question_name]: value }
const responses = reactive({});
// Checkbox multi-value responses: { [question_name]: [] }
const checkboxResponses = reactive({});
const additionalComments = ref("");

const participant = reactive({
  name: "",
  department: "",
  jobTitle: "",
  branch: "",
  yearsOfService: "",
});

const loadSurvey = async () => {
  const name = route.params.name;
  if (!name) return;
  loading.value = true;
  error.value = null;
  submitted.value = false;
  survey.value = null;

  for (const k in responses) delete responses[k];
  for (const k in checkboxResponses) delete checkboxResponses[k];
  additionalComments.value = "";
  participant.name = "";
  participant.department = "";
  participant.jobTitle = "";
  participant.branch = "";
  participant.yearsOfService = "";

  if (!auth.companyLogo && !auth.companyName) {
    auth.fetchCompanyLogo();
  }

  try {
    const result = await frappeCall("pollcast.api.get_survey", {
      survey_name: name,
    });
    if (!result || result.error) {
      error.value = result?.error || "Survey not found";
      return;
    }
    survey.value = result;

    // Pre-initialise responses
    for (const q of result.questions || []) {
      if (q.question_type === "Checkbox") {
        checkboxResponses[q.name] = [];
      } else {
        responses[q.name] = "";
      }
    }
  } catch (e) {
    error.value = e.message;
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  loadSurvey();
});

watch(
  () => route.params.name,
  (newName, oldName) => {
    if (newName && newName !== oldName) {
      loadSurvey();
    }
  },
);

// Question type groups
const ratingQuestions = computed(() =>
  (survey.value?.questions || []).filter(
    (q) => q.question_type === "Rating Scale",
  ),
);
const choiceQuestions = computed(() =>
  (survey.value?.questions || []).filter(
    (q) =>
      q.question_type === "Multiple Choice" || q.question_type === "Checkbox",
  ),
);
const textQuestions = computed(() =>
  (survey.value?.questions || []).filter(
    (q) => q.question_type === "Text Input",
  ),
);
const hasSectionHeadings = computed(() =>
  (survey.value?.questions || []).some(
    (q) => q.question_type === "Section Heading",
  ),
);

const totalRequired = computed(
  () => (survey.value?.questions || []).filter((q) => q.required).length,
);
const answeredCount = computed(() => {
  return (survey.value?.questions || []).filter((q) => {
    if (!q.required) return false;
    if (q.question_type === "Checkbox")
      return (checkboxResponses[q.name] || []).length > 0;
    return responses[q.name] && responses[q.name].trim();
  }).length;
});

const progressPct = computed(() =>
  totalRequired.value === 0
    ? 100
    : Math.round((answeredCount.value / totalRequired.value) * 100),
);

const missingRequired = computed(() =>
  (survey.value?.questions || []).filter((q) => {
    if (!q.required) return false;
    if (q.question_type === "Checkbox")
      return (checkboxResponses[q.name] || []).length === 0;
    return !responses[q.name] || !responses[q.name].trim();
  }),
);

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

const submitSurvey = async () => {
  if (missingRequired.value.length > 0) return;
  submitting.value = true;
  try {
    // Build responses payload
    const allResponses = {};

    for (const [qname, val] of Object.entries(responses)) {
      if (val && val.trim) allResponses[qname] = val;
      else if (val) allResponses[qname] = String(val);
    }

    for (const [qname, vals] of Object.entries(checkboxResponses)) {
      if (vals && vals.length) allResponses[qname] = vals.join(", ");
    }

    if (additionalComments.value.trim()) {
      allResponses["__comments__"] = additionalComments.value;
    }

    const result = await frappeCall("pollcast.api.submit_survey_response", {
      survey_name: survey.value.name,
      responses: JSON.stringify(allResponses),
      respondent_info: JSON.stringify(participant),
    });

    if (result?.success !== false) {
      submitted.value = true;
      window.scrollTo({ top: 0, behavior: "smooth" });
    } else {
      toast?.(result?.error || "Submission failed", "error");
    }
  } catch (e) {
    toast?.(e.message, "error");
  } finally {
    submitting.value = false;
  }
};
</script>

<style scoped>
.survey-section-heading {
  margin: 2rem 0 1rem;
  padding: 0.75rem 0;
  border-bottom: 2px solid var(--border-color, #e5e7eb);
}

.survey-section-heading h3 {
  margin: 0;
  font-size: 1.15rem;
  color: var(--text-primary, #1f2937);
}

.ordered-rating-options {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem 1rem;
}

.ordered-rating-options label {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.survey-take {
  display: flex;
  flex-direction: column;
}

/* Sections */
.section-heading {
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}
.optional-note {
  font-size: 0.75rem;
  font-weight: 400;
  color: var(--text-muted);
  font-style: italic;
  margin-left: 0.35rem;
}

/* Participant info grid */
.participant-info-section {
}
.participant-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.25rem;
}

/* Rating legend */
.rating-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  align-items: center;
  padding: 0.75rem 1rem;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: var(--r-md);
  font-size: 0.8125rem;
  margin-top: 0.75rem;
}
.legend-item {
  color: var(--text-secondary);
}
.legend-item strong {
  color: var(--text-primary);
}
.legend-sep {
  color: var(--text-muted);
}

/* Score column label */
.score-label {
  display: block;
  font-size: 0.6rem;
  font-weight: 500;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-top: 0.2rem;
}

/* Rating radio — color-coded by score */
.rating-radio {
  accent-color: var(--accent);
}

/* N/A radio */
.rating-radio-na:checked {
  border-color: var(--text-muted);
  background: rgba(255, 255, 255, 0.1);
  box-shadow: none;
}

/* Question cards */
.question-card {
}
.question-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 1rem;
  line-height: 1.5;
}

.choices-list {
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
}
.choice-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: var(--r-md);
  border: 1px solid var(--glass-border);
  cursor: pointer;
  transition: all var(--dur) var(--ease);
}
.choice-item:hover {
  background: var(--accent-dim);
  border-color: var(--border-accent);
}

.choice-radio,
.choice-check {
  width: 18px;
  height: 18px;
  accent-color: var(--accent);
  cursor: pointer;
  flex-shrink: 0;
}

.choice-label {
  font-size: 0.9rem;
  color: var(--text-primary);
  cursor: pointer;
}

/* Submit section */
.submit-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}
.submit-info {
  flex: 1;
}

/* Progress bar */
.progress-bar-wrap {
}

/* Error state */
.error-state p {
  margin-bottom: 1rem;
}

@media (max-width: 768px) {
  .submit-row {
    flex-direction: column;
  }
  .submit-row .btn {
    width: 100%;
  }
  .rating-legend {
    gap: 0.4rem;
  }
}

/* Company Logo Branding Header */
.survey-brand-header {
  margin-bottom: 1.5rem;
  padding: 1.25rem 1.5rem;
  border-radius: var(--r-lg);
  border: 1px solid var(--glass-border);
  background: var(--glass-bg);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  display: flex;
  justify-content: center;
  align-items: center;
  text-align: center;
}

.survey-brand-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: 0.5rem;
  width: 100%;
}

.survey-brand-logo {
  max-height: 60px;
  max-width: 240px;
  object-fit: contain;
  display: block;
  margin: 0 auto;
}

.survey-brand-name {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.01em;
  text-align: center;
}

.pre-line-text {
  white-space: pre-line;
}

.survey-success-brand-wrap {
  margin-bottom: 1.25rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  text-align: center;
}
</style>
