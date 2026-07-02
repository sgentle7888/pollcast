<template>
  <div class="create-view animate-fade-in-up">
    <div class="page-header">
      <div>
        <div class="breadcrumbs">
          <RouterLink to="/">Home</RouterLink><span class="sep">/</span>
          <span class="current">Create {{ type === 'poll' ? 'Poll' : 'Survey' }}</span>
        </div>
        <h1 class="page-title">Create New</h1>
      </div>
    </div>

    <!-- Type selector (step 0) -->
    <div v-if="step === 0" class="type-selector-screen animate-fade-in-up">
      <p class="text-secondary text-lg" style="text-align: center; margin-bottom: 2rem;">What would you like to create?</p>
      <div class="type-cards">
        <div class="type-card card card-interactive" @click="selectType('poll')">
          <div class="type-card-icon type-icon-accent">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M9 12l2 2 4-4"/><path d="M5 7c0-1.1.9-2 2-2h10a2 2 0 0 1 2 2v12H5V7z"/></svg>
          </div>
          <h2>Poll</h2>
          <p class="text-secondary text-sm">A single question with multiple-choice options. Participants vote for one (or more) option.</p>
          <ul class="type-features">
            <li>✓ Quick single-question voting</li>
            <li>✓ Multiple choice options</li>
            <li>✓ Real-time vote counts</li>
          </ul>
          <div class="type-card-action btn btn-primary">Get Started →</div>
        </div>

        <div class="type-card card card-interactive" @click="selectType('survey')">
          <div class="type-card-icon type-icon-violet">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/><rect x="9" y="3" width="6" height="4" rx="1"/><line x1="9" y1="12" x2="15" y2="12"/><line x1="9" y1="16" x2="13" y2="16"/></svg>
          </div>
          <h2>Survey</h2>
          <p class="text-secondary text-sm">Multi-question feedback form. Supports rating scales (1–5), multiple choice, text input, and checkboxes.</p>
          <ul class="type-features">
            <li>✓ Rating scale (1–5) questions</li>
            <li>✓ Open text + multiple choice</li>
            <li>✓ Detailed analytics & reports</li>
          </ul>
          <div class="type-card-action btn btn-primary" style="background: linear-gradient(135deg, #7C3AED, #8B5CF6);">Get Started →</div>
        </div>
      </div>
    </div>

    <!-- Steps 1+ : Form Wizard -->
    <div v-if="step > 0" class="wizard-layout">
      <!-- Stepper -->
      <div class="card stepper" style="padding: 1.5rem 2rem;">
        <div v-for="(s, i) in wizardSteps" :key="i" :class="['stepper-item', { active: step === i + 1, completed: step > i + 1 }]">
          <div class="step-bubble">
            <svg v-if="step > i + 1" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
            <span v-else>{{ i + 1 }}</span>
          </div>
          <span class="step-label">{{ s }}</span>
        </div>
      </div>

      <!-- Step 1: Basic Info -->
      <div v-if="step === 1" class="card wizard-step animate-fade-in-up">
        <h3 class="step-heading">Basic Information</h3>
        <p class="text-secondary text-sm" style="margin-bottom: 1.5rem;">Give your {{ type }} a clear title and optional description.</p>

        <div class="form-grid">
          <div class="form-group" style="grid-column: span 2;">
            <label class="form-label">Title <span class="mandatory-star">*</span></label>
            <input type="text" class="form-control" v-model="form.title" :placeholder="type === 'poll' ? 'e.g. Best programming language 2025?' : 'e.g. Q2 Employee Satisfaction Survey'" maxlength="200" />
          </div>
          <div class="form-group" style="grid-column: span 2;">
            <label class="form-label">Description</label>
            <textarea class="form-control" v-model="form.description" rows="3" placeholder="Optional context or instructions for participants…"></textarea>
          </div>
          <div class="form-group">
            <label class="form-label">Start Date</label>
            <input type="datetime-local" class="form-control" v-model="form.startDate" />
          </div>
          <div class="form-group">
            <label class="form-label">End Date</label>
            <input type="datetime-local" class="form-control" v-model="form.endDate" />
          </div>
        </div>

        <div class="wizard-nav">
          <button class="btn btn-ghost" @click="step = 0">← Back</button>
          <button class="btn btn-primary" :disabled="!form.title.trim()" @click="step = 2">
            Continue →
          </button>
        </div>
      </div>

      <!-- Step 2: Questions (Poll options or Survey questions) -->
      <div v-if="step === 2" class="card wizard-step animate-fade-in-up">
        <h3 class="step-heading">{{ type === 'poll' ? 'Poll Options' : 'Survey Questions' }}</h3>
        <p class="text-secondary text-sm" style="margin-bottom: 1.5rem;">
          {{ type === 'poll' ? 'Add the options participants can vote for.' : 'Add questions to your survey.' }}
        </p>

        <!-- POLL Options -->
        <div v-if="type === 'poll'" class="options-builder">
          <div v-for="(opt, i) in form.options" :key="i" class="option-row-build">
            <div class="opt-num">{{ i + 1 }}</div>
            <input type="text" class="form-control" v-model="opt.text" :placeholder="'Option ' + (i + 1)" />
            <button class="btn btn-ghost btn-icon" @click="removeOption(i)" :disabled="form.options.length <= 2" title="Remove">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            </button>
          </div>
          <button class="btn btn-secondary" @click="addOption" :disabled="form.options.length >= 10">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
            Add Option
          </button>
        </div>

        <!-- SURVEY Questions -->
        <div v-else class="questions-builder">
          <div v-for="(q, qi) in form.questions" :key="qi" class="question-card card-elevated">
            <div class="q-header">
              <span class="q-num">Q{{ qi + 1 }}</span>
              <select class="form-control q-type-select" v-model="q.type" style="width: 200px;">
                <option value="Rating Scale">Rating Scale (1–5)</option>
                <option value="Multiple Choice">Multiple Choice</option>
                <option value="Checkbox">Checkbox</option>
                <option value="Text Input">Text Input</option>
              </select>
              <div class="checkbox-group q-required">
                <input type="checkbox" :id="'req-' + qi" v-model="q.required" />
                <label :for="'req-' + qi" class="text-sm">Required</label>
              </div>
              <button class="btn btn-ghost btn-icon btn-sm" @click="removeQuestion(qi)" :disabled="form.questions.length <= 1" title="Remove question">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
              </button>
            </div>
            <input type="text" class="form-control q-text" v-model="q.text" :placeholder="'Question ' + (qi + 1) + ' — what do you want to know?'" />

            <!-- MC/Checkbox sub-options -->
            <div v-if="q.type === 'Multiple Choice' || q.type === 'Checkbox'" class="q-suboptions">
              <div v-for="(opt, oi) in q.options" :key="oi" class="q-subopt-row">
                <input type="text" class="form-control" v-model="q.options[oi]" :placeholder="'Option ' + (oi + 1)" style="font-size: 0.875rem;" />
                <button class="btn btn-ghost btn-icon btn-sm" @click="q.options.splice(oi, 1)" :disabled="q.options.length <= 2">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                </button>
              </div>
              <button class="btn btn-ghost btn-sm" @click="q.options.push('')">+ Add option</button>
            </div>

            <!-- Rating scale preview -->
            <div v-if="q.type === 'Rating Scale'" class="q-rating-preview">
              <span class="text-muted text-xs">Preview: </span>
              <div class="rating-preview-dots">
                <span v-for="n in 5" :key="n" class="rating-dot">{{ n }}</span>
                <span class="rating-dot na">N/A</span>
              </div>
            </div>
          </div>

          <button class="btn btn-secondary" @click="addQuestion">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
            Add Question
          </button>
        </div>

        <div class="wizard-nav">
          <button class="btn btn-ghost" @click="step = 1">← Back</button>
          <button class="btn btn-primary" :disabled="!canProceedStep2" @click="step = 3">
            Review & Create →
          </button>
        </div>
      </div>

      <!-- Step 3: Review & Submit -->
      <div v-if="step === 3" class="card wizard-step animate-fade-in-up">
        <h3 class="step-heading">Review & Create</h3>
        <p class="text-secondary text-sm" style="margin-bottom: 1.5rem;">Check everything looks good before creating.</p>

        <div class="review-section">
          <div class="review-row"><span class="review-label">Type</span><span class="badge badge-accent">{{ type === 'poll' ? 'Poll' : 'Survey' }}</span></div>
          <div class="review-row"><span class="review-label">Title</span><strong>{{ form.title }}</strong></div>
          <div v-if="form.description" class="review-row"><span class="review-label">Description</span><span class="text-secondary text-sm">{{ form.description }}</span></div>
          <div v-if="form.startDate" class="review-row"><span class="review-label">Start</span><span>{{ form.startDate }}</span></div>
          <div v-if="form.endDate"   class="review-row"><span class="review-label">End</span><span>{{ form.endDate }}</span></div>
          <div class="divider"></div>
          <div v-if="type === 'poll'">
            <p class="text-sm font-semibold" style="margin-bottom: 0.75rem;">Options ({{ form.options.length }})</p>
            <div class="review-options">
              <div v-for="(opt, i) in form.options" :key="i" class="review-option">
                <span class="review-option-num">{{ i + 1 }}</span>{{ opt.text }}
              </div>
            </div>
          </div>
          <div v-else>
            <p class="text-sm font-semibold" style="margin-bottom: 0.75rem;">Questions ({{ form.questions.length }})</p>
            <div class="review-questions">
              <div v-for="(q, i) in form.questions" :key="i" class="review-q">
                <div class="review-q-header">
                  <span class="q-num-sm">Q{{ i + 1 }}</span>
                  <span class="badge badge-neutral">{{ q.type }}</span>
                  <span v-if="q.required" class="badge badge-danger" style="font-size: 0.6rem;">Required</span>
                </div>
                <p class="text-sm" style="margin-top: 0.35rem;">{{ q.text }}</p>
              </div>
            </div>
          </div>
        </div>

        <div class="wizard-nav">
          <button class="btn btn-ghost" @click="step = 2">← Back</button>
          <button class="btn btn-primary btn-lg" :disabled="submitting" @click="submit">
            <span v-if="submitting" class="spinner spinner-sm"></span>
            <span v-else>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
              Create {{ type === 'poll' ? 'Poll' : 'Survey' }}
            </span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, inject } from "vue";
import { useRouter } from "vue-router";
import { frappeCall } from "../api/frappe.js";

const router = useRouter();
const toast  = inject("toast");

const step = ref(0);
const type = ref("poll");
const submitting = ref(false);

const wizardSteps = computed(() =>
  type.value === "poll"
    ? ["Basic Info", "Options", "Review"]
    : ["Basic Info", "Questions", "Review"]
);

const form = ref({
  title: "",
  description: "",
  startDate: "",
  endDate: "",
  options: [{ text: "" }, { text: "" }],
  questions: [{ text: "", type: "Rating Scale", required: true, options: ["", ""] }],
});

const selectType = (t) => { type.value = t; step.value = 1; };

const addOption    = () => form.value.options.push({ text: "" });
const removeOption = (i) => form.value.options.splice(i, 1);

const addQuestion = () =>
  form.value.questions.push({ text: "", type: "Rating Scale", required: false, options: ["", ""] });
const removeQuestion = (i) => form.value.questions.splice(i, 1);

const canProceedStep2 = computed(() => {
  if (type.value === "poll") {
    return form.value.options.filter((o) => o.text.trim()).length >= 2;
  }
  return form.value.questions.filter((q) => q.text.trim()).length >= 1;
});

const submit = async () => {
  submitting.value = true;
  try {
    let result;
    if (type.value === "poll") {
      result = await frappeCall("pollcast.api.create_poll", {
        title:       form.value.title,
        description: form.value.description,
        start_date:  form.value.startDate || null,
        end_date:    form.value.endDate   || null,
        options:     form.value.options.filter((o) => o.text.trim()).map((o) => o.text),
      });
      if (result?.name) {
        toast?.("Poll created successfully!", "success");
        router.push("/polls/" + result.name);
      }
    } else {
      result = await frappeCall("pollcast.api.create_survey", {
        title:       form.value.title,
        description: form.value.description,
        start_date:  form.value.startDate || null,
        end_date:    form.value.endDate   || null,
        questions:   form.value.questions
          .filter((q) => q.text.trim())
          .map((q) => ({
            question_text: q.text,
            question_type: q.type,
            required:      q.required ? 1 : 0,
            options:       q.options?.filter(Boolean) || [],
          })),
      });
      if (result?.name) {
        toast?.("Survey created successfully!", "success");
        router.push("/surveys/" + result.name);
      }
    }
    if (result?.error) toast?.(result.error, "error");
  } catch (e) {
    toast?.(e.message, "error");
  } finally {
    submitting.value = false;
  }
};
</script>

<style scoped>
.create-view { display: flex; flex-direction: column; }

/* Type Selector */
.type-selector-screen { display: flex; flex-direction: column; align-items: center; padding: 2rem 0; }
.type-cards { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; max-width: 800px; width: 100%; }

.type-card {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 2rem;
  cursor: pointer;
}

.type-card-icon {
  width: 64px;
  height: 64px;
  border-radius: var(--r-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.5rem;
}
.type-icon-accent { background: var(--accent-dim); color: var(--accent-light); }
.type-icon-violet { background: var(--violet-dim); color: var(--violet-light); }

.type-features { list-style: none; display: flex; flex-direction: column; gap: 0.4rem; }
.type-features li { font-size: 0.8125rem; color: var(--text-secondary); }
.type-card-action { margin-top: auto; width: 100%; }

/* Wizard */
.wizard-layout { display: flex; flex-direction: column; gap: 1.25rem; }
.wizard-step { }
.step-heading { font-size: 1.25rem; font-weight: 700; margin-bottom: 0.25rem; }

.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem; margin-bottom: 1.5rem; }

/* Poll options builder */
.options-builder { display: flex; flex-direction: column; gap: 0.75rem; margin-bottom: 1.5rem; }
.option-row-build { display: flex; align-items: center; gap: 0.75rem; }
.opt-num {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--accent-dim);
  color: var(--accent-light);
  font-size: 0.75rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

/* Survey questions builder */
.questions-builder { display: flex; flex-direction: column; gap: 1rem; margin-bottom: 1.5rem; }
.question-card { padding: 1.25rem; }
.q-header { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.875rem; flex-wrap: wrap; }
.q-num {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--gradient);
  color: white;
  font-size: 0.75rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.q-type-select { flex: 0 0 auto; }
.q-required { flex: 1; justify-content: flex-end; }
.q-text { margin-bottom: 0.875rem; }

.q-suboptions { display: flex; flex-direction: column; gap: 0.5rem; padding: 0.875rem; background: var(--glass-bg); border-radius: var(--r-md); border: 1px solid var(--glass-border); }
.q-subopt-row { display: flex; align-items: center; gap: 0.5rem; }

.q-rating-preview { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem; background: var(--glass-bg); border-radius: var(--r-md); border: 1px solid var(--glass-border); }
.rating-preview-dots { display: flex; gap: 0.5rem; }
.rating-dot {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 2px solid var(--glass-border);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--text-muted);
}
.rating-dot.na { border-style: dashed; font-size: 0.65rem; width: 40px; border-radius: var(--r-sm); }

/* Review */
.review-section { display: flex; flex-direction: column; gap: 0.875rem; }
.review-row { display: flex; align-items: flex-start; gap: 1rem; padding: 0.5rem 0; }
.review-label { font-size: 0.8125rem; font-weight: 600; color: var(--text-muted); min-width: 100px; flex-shrink: 0; }

.review-options, .review-questions { display: flex; flex-direction: column; gap: 0.5rem; }
.review-option { display: flex; align-items: center; gap: 0.75rem; font-size: 0.875rem; padding: 0.5rem 0.75rem; background: var(--glass-bg); border-radius: var(--r-sm); }
.review-option-num {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: var(--accent-dim);
  color: var(--accent-light);
  font-size: 0.7rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.review-q { padding: 0.875rem; background: var(--glass-bg); border-radius: var(--r-md); border: 1px solid var(--glass-border); }
.review-q-header { display: flex; align-items: center; gap: 0.5rem; }
.q-num-sm { font-size: 0.75rem; font-weight: 700; color: var(--text-muted); }

.wizard-nav { display: flex; justify-content: space-between; align-items: center; margin-top: 2rem; padding-top: 1.5rem; border-top: 1px solid var(--glass-border); }

@media (max-width: 768px) {
  .type-cards { grid-template-columns: 1fr; }
  .form-grid  { grid-template-columns: 1fr; }
  .form-grid > * { grid-column: span 1 !important; }
}
</style>
