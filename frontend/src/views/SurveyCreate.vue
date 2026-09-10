<template>
  <div class="create-view animate-fade-in-up">
    <!-- Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumbs">
          <RouterLink to="/">Home</RouterLink><span class="sep">/</span>
          <RouterLink
            v-if="isEditMode"
            :to="type === 'poll' ? '/polls' : '/surveys'"
            >{{ type === "poll" ? "Polls" : "Surveys" }}</RouterLink
          >
          <span v-if="isEditMode" class="sep">/</span>
          <span class="current">{{
            isEditMode
              ? `Edit ${type === "poll" ? "Poll" : "Survey"}`
              : `Create ${type === "poll" ? "Poll" : "Survey"}`
          }}</span>
        </div>
        <h1 class="page-title">
          {{
            isEditMode
              ? `Edit ${type === "poll" ? "Poll" : "Survey"}`
              : "Create New"
          }}
        </h1>
        <p v-if="isEditMode && form.title" class="page-subtitle text-secondary">
          Editing <strong>{{ targetDocName }}</strong> &mdash; {{ form.title }}
        </p>
      </div>
    </div>

    <!-- Loading State for Edit Mode -->
    <div v-if="loadingDoc" class="loading-state card">
      <div class="spinner"></div>
      <p>Loading {{ type === "poll" ? "poll" : "survey" }} details…</p>
    </div>

    <!-- Type selector (step 0 - create mode only) -->
    <div
      v-else-if="step === 0 && !isEditMode"
      class="type-selector-screen animate-fade-in-up"
    >
      <p
        class="text-secondary text-lg"
        style="text-align: center; margin-bottom: 2rem"
      >
        What would you like to create?
      </p>
      <div class="type-cards">
        <div
          class="type-card card card-interactive"
          @click="selectType('poll')"
        >
          <div class="type-card-icon type-icon-accent">
            <svg
              width="32"
              height="32"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="1.5"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path d="M9 12l2 2 4-4" />
              <path d="M5 7c0-1.1.9-2 2-2h10a2 2 0 0 1 2 2v12H5V7z" />
            </svg>
          </div>
          <h2>Poll</h2>
          <p class="text-secondary text-sm">
            A single question with multiple-choice options. Participants vote
            for one (or more) option.
          </p>
          <ul class="type-features">
            <li>✓ Quick single-question voting</li>
            <li>✓ Multiple choice options</li>
            <li>✓ Real-time vote counts</li>
          </ul>
          <div class="type-card-action btn btn-primary">Get Started →</div>
        </div>

        <div
          class="type-card card card-interactive"
          @click="selectType('survey')"
        >
          <div class="type-card-icon type-icon-violet">
            <svg
              width="32"
              height="32"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="1.5"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path
                d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"
              />
              <rect x="9" y="3" width="6" height="4" rx="1" />
              <line x1="9" y1="12" x2="15" y2="12" />
              <line x1="9" y1="16" x2="13" y2="16" />
            </svg>
          </div>
          <h2>Survey</h2>
          <p class="text-secondary text-sm">
            Multi-question feedback form. Supports rating scales (1–5), multiple
            choice, text input, and checkboxes.
          </p>
          <ul class="type-features">
            <li>✓ Rating scale (1–5) questions</li>
            <li>✓ Open text + multiple choice</li>
            <li>✓ Detailed analytics & reports</li>
          </ul>
          <div
            class="type-card-action btn btn-primary"
            style="background: linear-gradient(135deg, #7c3aed, #8b5cf6)"
          >
            Get Started →
          </div>
        </div>
      </div>
    </div>

    <!-- Steps 1+ : Form Wizard -->
    <div v-else-if="step > 0" class="wizard-layout">
      <!-- Stepper -->
      <div class="card stepper" style="padding: 1.5rem 2rem">
        <div
          v-for="(s, i) in wizardSteps"
          :key="i"
          :class="[
            'stepper-item',
            { active: step === i + 1, completed: step > i + 1 },
          ]"
        >
          <div class="step-bubble">
            <svg
              v-if="step > i + 1"
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="3"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <polyline points="20 6 9 17 4 12" />
            </svg>
            <span v-else>{{ i + 1 }}</span>
          </div>
          <span class="step-label">{{ s }}</span>
        </div>
      </div>

      <!-- Step 1: Basic Info -->
      <div v-if="step === 1" class="card wizard-step animate-fade-in-up">
        <h3 class="step-heading">
          {{
            isEditMode
              ? `Basic ${type === "poll" ? "Poll" : "Survey"} Information`
              : "Basic Information"
          }}
        </h3>
        <p class="text-secondary text-sm" style="margin-bottom: 1.5rem">
          {{
            isEditMode
              ? `Update the title, instructions, and timeline for this ${type}.`
              : `Give your ${type} a clear title and optional description.`
          }}
        </p>

        <!-- Warning if survey/poll already has responses -->
        <div
          v-if="isEditMode && responseCount > 0"
          class="response-warning-banner"
        >
          <div style="display: flex; align-items: flex-start; gap: 0.75rem">
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="text-warning"
              style="flex-shrink: 0; margin-top: 2px"
            >
              <path
                d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"
              />
              <line x1="12" y1="9" x2="12" y2="13" />
              <line x1="12" y1="17" x2="12.01" y2="17" />
            </svg>
            <div>
              <strong class="text-primary"
                >{{ type === "poll" ? "Poll" : "Survey" }} has
                {{ responseCount }} recorded response(s)</strong
              >
              <p
                class="text-secondary text-xs"
                style="margin-top: 0.2rem; line-height: 1.4"
              >
                To protect response data integrity, only System Managers can
                alter voting options or questions. You can freely update the
                title, instructions, status, and dates.
              </p>
            </div>
          </div>
        </div>

        <div class="form-grid">
          <div class="form-group" style="grid-column: span 2">
            <label class="form-label"
              >Title <span class="mandatory-star">*</span></label
            >
            <input
              type="text"
              class="form-control"
              v-model="form.title"
              :placeholder="
                type === 'poll'
                  ? 'e.g. Best programming language 2025?'
                  : 'e.g. Q2 Employee Satisfaction Survey'
              "
              maxlength="200"
            />
          </div>
          <div class="form-group" style="grid-column: span 2">
            <label class="form-label">Description / Instructions</label>
            <RichTextEditor v-model="form.description" />
          </div>
          <div v-if="isEditMode" class="form-group">
            <label class="form-label">Status</label>
            <select class="form-control" v-model="form.status">
              <option value="Draft">Draft</option>
              <option value="Active">Active</option>
              <option value="Closed">Closed</option>
              <option value="Archived">Archived</option>
            </select>
          </div>
          <div
            class="form-group"
            :style="{ 'grid-column': isEditMode ? 'span 1' : 'span 1' }"
          >
            <label class="form-label">Start Date</label>
            <input
              type="datetime-local"
              class="form-control"
              v-model="form.startDate"
            />
          </div>
          <div
            class="form-group"
            :style="{ 'grid-column': isEditMode ? 'span 2' : 'span 1' }"
          >
            <label class="form-label">End Date</label>
            <input
              type="datetime-local"
              class="form-control"
              v-model="form.endDate"
            />
          </div>

          <!-- Survey Company Branding Info -->
          <div
            class="survey-branding-card card-glass"
            style="grid-column: span 2"
          >
            <div class="branding-card-content">
              <div class="branding-thumb-box">
                <img
                  v-if="auth.companyLogo"
                  :src="auth.companyLogo"
                  alt="Company Logo"
                  class="branding-thumb-img"
                />
                <span v-else class="text-xs text-muted">No custom logo</span>
              </div>
              <div class="branding-meta">
                <div class="text-sm font-semibold text-primary">
                  Company Branding
                </div>
                <p class="text-xs text-secondary">
                  This company logo is automatically displayed on the survey
                  interface for participants.
                </p>
              </div>
              <button
                type="button"
                class="btn btn-secondary btn-sm branding-change-btn"
                @click="openSettingsModal"
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
                  <circle cx="12" cy="12" r="3" />
                  <path
                    d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1Z"
                  />
                </svg>
                <span>{{
                  auth.companyLogo ? "Change Logo" : "Upload Logo"
                }}</span>
              </button>
            </div>
          </div>
        </div>

        <div class="wizard-nav">
          <button v-if="!isEditMode" class="btn btn-ghost" @click="step = 0">
            ← Back
          </button>
          <RouterLink
            v-else
            :to="type === 'poll' ? '/polls' : '/surveys'"
            class="btn btn-ghost"
            >← Cancel</RouterLink
          >
          <button
            class="btn btn-primary"
            :disabled="!form.title.trim()"
            @click="step = 2"
          >
            Continue →
          </button>
        </div>
      </div>

      <!-- Step 2: Questions (Poll options or Survey questions) -->
      <div v-if="step === 2" class="card wizard-step animate-fade-in-up">
        <h3 class="step-heading">
          {{ type === "poll" ? "Poll Options" : "Survey Questions" }}
        </h3>
        <p class="text-secondary text-sm" style="margin-bottom: 1.5rem">
          {{
            type === "poll"
              ? "Add the options participants can vote for."
              : "Configure the questions in your survey."
          }}
        </p>

        <!-- POLL Options -->
        <div v-if="type === 'poll'" class="options-builder">
          <div
            v-if="isEditMode && responseCount > 0 && !auth.isAdmin"
            class="response-warning-banner"
            style="margin-bottom: 1rem"
          >
            <p class="text-xs text-secondary" style="margin: 0">
              ⚠️ This poll has recorded votes. Modifying or deleting options is
              restricted to System Managers.
            </p>
          </div>
          <div
            v-for="(opt, i) in form.options"
            :key="i"
            class="option-row-build"
          >
            <div class="opt-num">{{ i + 1 }}</div>
            <input
              type="text"
              class="form-control"
              v-model="opt.text"
              :placeholder="'Option ' + (i + 1)"
              :disabled="isEditMode && responseCount > 0 && !auth.isAdmin"
            />
            <button
              class="btn btn-ghost btn-icon"
              @click="removeOption(i)"
              :disabled="
                form.options.length <= 2 ||
                (isEditMode && responseCount > 0 && !auth.isAdmin)
              "
              title="Remove"
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
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </div>
          <button
            class="btn btn-secondary"
            @click="addOption"
            :disabled="
              form.options.length >= 10 ||
              (isEditMode && responseCount > 0 && !auth.isAdmin)
            "
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
              <line x1="12" y1="5" x2="12" y2="19" />
              <line x1="5" y1="12" x2="19" y2="12" />
            </svg>
            Add Option
          </button>
        </div>

        <!-- SURVEY Questions -->
        <div v-else class="questions-builder">
          <div
            v-for="(q, qi) in form.questions"
            :key="qi"
            class="question-card card-elevated"
          >
            <div class="q-header">
              <span class="q-num">Q{{ qi + 1 }}</span>
              <select
                class="form-control q-type-select"
                v-model="q.type"
                style="width: 200px"
              >
                <option value="Rating Scale">Rating Scale (1–5)</option>
                <option value="Multiple Choice">Multiple Choice</option>
                <option value="Checkbox">Checkbox</option>
                <option value="Text Input">Text Input</option>
                <option value="Section Heading">Section Heading</option>
              </select>
              <div class="checkbox-group q-required">
                <template v-if="q.type !== 'Section Heading'">
                  <input
                    type="checkbox"
                    :id="'req-' + qi"
                    v-model="q.required"
                  />
                  <label :for="'req-' + qi" class="text-sm">Required</label>
                </template>
              </div>
              <button
                class="btn btn-ghost btn-icon btn-sm"
                @click="removeQuestion(qi)"
                :disabled="
                  form.questions.length <= 1 ||
                  (isEditMode && responseCount > 0 && !auth.isAdmin)
                "
                :title="
                  isEditMode && responseCount > 0 && !auth.isAdmin
                    ? 'Cannot delete questions with existing responses'
                    : 'Remove question'
                "
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
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </button>
            </div>
            <input
              type="text"
              class="form-control q-text"
              v-model="q.text"
              :placeholder="
                q.type === 'Section Heading'
                  ? 'Section heading'
                  : 'Question ' + (qi + 1) + ' — what do you want to know?'
              "
            />

            <!-- MC/Checkbox sub-options -->
            <div
              v-if="q.type === 'Multiple Choice' || q.type === 'Checkbox'"
              class="q-suboptions"
            >
              <div
                v-for="(opt, oi) in q.options"
                :key="oi"
                class="q-subopt-row"
              >
                <input
                  type="text"
                  class="form-control"
                  v-model="q.options[oi]"
                  :placeholder="'Option ' + (oi + 1)"
                  style="font-size: 0.875rem"
                />
                <button
                  class="btn btn-ghost btn-icon btn-sm"
                  @click="q.options.splice(oi, 1)"
                  :disabled="q.options.length <= 2"
                >
                  <svg
                    width="12"
                    height="12"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <line x1="18" y1="6" x2="6" y2="18" />
                    <line x1="6" y1="6" x2="18" y2="18" />
                  </svg>
                </button>
              </div>
              <button class="btn btn-ghost btn-sm" @click="q.options.push('')">
                + Add option
              </button>
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

          <div class="question-builder-actions">
            <button class="btn btn-secondary" @click="addQuestion">
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
                <line x1="12" y1="5" x2="12" y2="19" />
                <line x1="5" y1="12" x2="19" y2="12" />
              </svg>
              Add Question
            </button>
            <button class="btn btn-ghost" @click="addSection">
              + Add Section
            </button>
          </div>
        </div>

        <div class="wizard-nav">
          <button class="btn btn-ghost" @click="step = 1">← Back</button>
          <button
            class="btn btn-primary"
            :disabled="!canProceedStep2"
            @click="step = 3"
          >
            {{ isEditMode ? "Review & Save →" : "Review & Create →" }}
          </button>
        </div>
      </div>

      <!-- Step 3: Review & Submit -->
      <div v-if="step === 3" class="card wizard-step animate-fade-in-up">
        <h3 class="step-heading">
          {{ isEditMode ? "Review & Save Changes" : "Review & Create" }}
        </h3>
        <p class="text-secondary text-sm" style="margin-bottom: 1.5rem">
          {{
            isEditMode
              ? "Check the updated survey details before saving."
              : "Check everything looks good before creating."
          }}
        </p>

        <div class="review-section">
          <div class="review-row">
            <span class="review-label">Type</span
            ><span class="badge badge-accent">{{
              type === "poll" ? "Poll" : "Survey"
            }}</span>
          </div>
          <div class="review-row">
            <span class="review-label">Title</span
            ><strong>{{ form.title }}</strong>
          </div>
          <div v-if="isEditMode" class="review-row">
            <span class="review-label">Status</span
            ><span class="badge badge-neutral">{{ form.status }}</span>
          </div>
          <div v-if="form.description" class="review-row">
            <span class="review-label">Description</span>
            <div
              class="review-rich-description text-secondary text-sm"
              v-html="sanitizedDescription"
            ></div>
          </div>
          <div v-if="form.startDate" class="review-row">
            <span class="review-label">Start</span
            ><span>{{ form.startDate }}</span>
          </div>
          <div v-if="form.endDate" class="review-row">
            <span class="review-label">End</span><span>{{ form.endDate }}</span>
          </div>
          <div class="divider"></div>
          <div v-if="type === 'poll'">
            <p class="text-sm font-semibold" style="margin-bottom: 0.75rem">
              Options ({{ form.options.length }})
            </p>
            <div class="review-options">
              <div
                v-for="(opt, i) in form.options"
                :key="i"
                class="review-option"
              >
                <span class="review-option-num">{{ i + 1 }}</span
                >{{ opt.text }}
              </div>
            </div>
          </div>
          <div v-else>
            <p class="text-sm font-semibold" style="margin-bottom: 0.75rem">
              Questions ({{ form.questions.length }})
            </p>
            <div class="review-questions">
              <div v-for="(q, i) in form.questions" :key="i" class="review-q">
                <div class="review-q-header">
                  <span class="q-num-sm">Q{{ i + 1 }}</span>
                  <span class="badge badge-neutral">{{ q.type }}</span>
                  <span
                    v-if="q.required"
                    class="badge badge-danger"
                    style="font-size: 0.6rem"
                    >Required</span
                  >
                </div>
                <p class="text-sm" style="margin-top: 0.35rem">{{ q.text }}</p>
              </div>
            </div>
          </div>
        </div>

        <div class="wizard-nav">
          <button class="btn btn-ghost" @click="step = 2">← Back</button>
          <button
            class="btn btn-primary btn-lg"
            :disabled="submitting"
            @click="submit"
          >
            <span v-if="submitting" class="spinner spinner-sm"></span>
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
                <polyline points="20 6 9 17 4 12" />
              </svg>
              {{
                isEditMode
                  ? `Save ${type === "poll" ? "Poll" : "Survey"} Changes`
                  : `Create ${type === "poll" ? "Poll" : "Survey"}`
              }}
            </span>
          </button>
        </div>
      </div>

      <!-- Step 4: Success + Shareable Link -->
      <div
        v-if="step === 4"
        class="card wizard-step animate-fade-in-up success-screen"
      >
        <div class="success-icon-wrap">
          <div class="success-icon-circle">
            <svg
              width="32"
              height="32"
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
        </div>
        <h3 class="step-heading" style="text-align: center">
          {{
            isEditMode
              ? `${type === "poll" ? "Poll" : "Survey"} Updated! 🎉`
              : `${type === "poll" ? "Poll" : "Survey"} Created! 🎉`
          }}
        </h3>
        <p
          class="text-secondary text-sm"
          style="text-align: center; margin-bottom: 1.75rem"
        >
          <strong>{{ form.title }}</strong>
          {{
            isEditMode
              ? "has been successfully updated."
              : "is ready. Share the link below with your participants."
          }}
        </p>

        <!-- Shareable Link Box -->
        <div class="share-link-box">
          <div
            class="share-link-label text-xs font-semibold text-secondary"
            style="margin-bottom: 0.5rem"
          >
            🔗 Shareable Link
          </div>
          <div class="share-link-row">
            <input
              type="text"
              class="form-control share-link-input"
              :value="shareUrl"
              readonly
              @click="$event.target.select()"
            />
            <button
              class="btn btn-primary share-copy-btn"
              :class="{ copied: linkCopied }"
              @click="copyLink"
            >
              <svg
                v-if="!linkCopied"
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
                <path
                  d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"
                />
              </svg>
              <svg
                v-else
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2.5"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <polyline points="20 6 9 17 4 12" />
              </svg>
              {{ linkCopied ? "Copied!" : "Copy Link" }}
            </button>
          </div>
          <p class="text-xs text-secondary" style="margin-top: 0.5rem">
            Guest users can open this link directly — no login required.
          </p>
        </div>

        <div
          class="wizard-nav"
          style="
            justify-content: center;
            gap: 1rem;
            margin-top: 1.75rem;
            flex-wrap: wrap;
          "
        >
          <button
            v-if="!isEditMode"
            class="btn btn-ghost"
            @click="createAnother"
          >
            + Create Another
          </button>
          <RouterLink
            :to="type === 'poll' ? '/polls' : '/surveys'"
            class="btn btn-ghost"
            >Back to {{ type === "poll" ? "Polls" : "Surveys" }}</RouterLink
          >
          <RouterLink
            :to="
              (type === 'poll' ? '/polls/' : '/surveys/') +
              (createdName || targetDocName)
            "
            class="btn btn-primary"
            >{{ type === "poll" ? "Take Poll" : "Take Survey" }}</RouterLink
          >
          <RouterLink
            :to="
              (type === 'poll' ? '/polls/' : '/surveys/') +
              (createdName || targetDocName) +
              '/results'
            "
            class="btn btn-secondary"
            >{{
              type === "poll" ? "Poll Results" : "Survey Results"
            }}</RouterLink
          >
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, inject, onMounted, watch } from "vue";
import { useRouter, useRoute, RouterLink } from "vue-router";
import { useAuthStore } from "../stores/auth.js";
import { frappeCall } from "../api/frappe.js";
import DOMPurify from "dompurify";
import RichTextEditor from "../components/RichTextEditor.vue";

const router = useRouter();
const route = useRoute();
const auth = useAuthStore();
const toast = inject("toast");
const openSettingsModal = inject("openSettingsModal", () => {});

const step = ref(0);
const type = ref("poll");
const submitting = ref(false);
const createdName = ref("");
const linkCopied = ref(false);

const loadingDoc = ref(false);
const responseCount = ref(0);

const targetDocName = computed(
  () => route.query.name || route.params.name || "",
);
const isPollEdit = computed(
  () => route.query.edit === "poll" || route.path.includes("/polls/"),
);
const isSurveyEdit = computed(
  () =>
    route.query.edit === "survey" ||
    route.path.includes("/surveys/") ||
    (!isPollEdit.value && !!targetDocName.value),
);
const isEditMode = computed(
  () => (isPollEdit.value || isSurveyEdit.value) && !!targetDocName.value,
);

const shareUrl = computed(() => {
  const name = createdName.value || targetDocName.value;
  if (!name) return "";
  const base = window.location.origin;
  const path =
    type.value === "poll"
      ? `/pollcast#/polls/${name}`
      : `/pollcast#/surveys/${name}`;
  return base + path;
});

const sanitizedDescription = computed(() =>
  DOMPurify.sanitize(form.value.description || ""),
);

const toDatetimeLocal = (str) => {
  if (!str) return "";
  const d = new Date(str.replace(" ", "T"));
  if (isNaN(d.getTime())) return "";
  const pad = (n) => String(n).padStart(2, "0");
  const yr = d.getFullYear();
  const mo = pad(d.getMonth() + 1);
  const day = pad(d.getDate());
  const hr = pad(d.getHours());
  const mi = pad(d.getMinutes());
  return `${yr}-${mo}-${day}T${hr}:${mi}`;
};

const copyLink = async () => {
  try {
    await navigator.clipboard.writeText(shareUrl.value);
    linkCopied.value = true;
    setTimeout(() => {
      linkCopied.value = false;
    }, 2000);
  } catch {
    const el = document.querySelector(".share-link-input");
    if (el) {
      el.select();
      document.execCommand("copy");
    }
    linkCopied.value = true;
    setTimeout(() => {
      linkCopied.value = false;
    }, 2000);
  }
};

const createAnother = () => {
  createdName.value = "";
  linkCopied.value = false;
  form.value = {
    title: "",
    description: "",
    status: "Draft",
    startDate: "",
    endDate: "",
    options: [{ text: "" }, { text: "" }],
    questions: [
      { text: "", type: "Rating Scale", required: true, options: ["", ""] },
    ],
  };
  step.value = 0;
};

const wizardSteps = computed(() =>
  type.value === "poll"
    ? ["Basic Info", "Options", "Review"]
    : ["Basic Info", "Questions", "Review"],
);

const form = ref({
  title: "",
  description: "",
  status: "Draft",
  startDate: "",
  endDate: "",
  options: [{ text: "" }, { text: "" }],
  questions: [
    { text: "", type: "Rating Scale", required: true, options: ["", ""] },
  ],
});

const loadSurveyForEdit = async (name) => {
  if (!name) return;
  loadingDoc.value = true;
  type.value = "survey";
  step.value = 1;

  try {
    const res = await frappeCall("pollcast.api.get_survey", {
      survey_name: name,
    });
    if (res && !res.error) {
      createdName.value = res.name;
      responseCount.value = res.total_responses || 0;
      form.value.title = res.title || "";
      form.value.description = res.description || "";
      form.value.status = res.status || "Draft";
      form.value.startDate = toDatetimeLocal(res.start_date);
      form.value.endDate = toDatetimeLocal(res.end_date);

      if (res.questions && res.questions.length > 0) {
        form.value.questions = res.questions.map((q) => ({
          name: q.name,
          text: q.question_text || "",
          type: q.question_type || "Rating Scale",
          required: !!q.required,
          options:
            Array.isArray(q.options) && q.options.length
              ? [...q.options]
              : ["", ""],
          scale_min: q.scale_min || 1,
          scale_max: q.scale_max || 5,
        }));
      }
    } else {
      toast?.(res?.error || "Survey not found", "error");
    }
  } catch (err) {
    toast?.(err.message || "Failed to load survey", "error");
  } finally {
    loadingDoc.value = false;
  }
};

const loadPollForEdit = async (name) => {
  if (!name) return;
  loadingDoc.value = true;
  type.value = "poll";
  step.value = 1;

  try {
    const res = await frappeCall("pollcast.api.get_poll", { poll_name: name });
    if (res && !res.error) {
      createdName.value = res.name;
      responseCount.value = res.total_responses || 0;
      form.value.title = res.title || "";
      form.value.description = res.description || "";
      form.value.status = res.status || "Draft";
      form.value.startDate = toDatetimeLocal(res.start_date);
      form.value.endDate = toDatetimeLocal(res.end_date);

      if (res.questions && res.questions.length > 0) {
        form.value.options = res.questions.map((q) => ({
          text: q.question_text || "",
        }));
      }
      while (form.value.options.length < 2) {
        form.value.options.push({ text: "" });
      }
    } else {
      toast?.(res?.error || "Poll not found", "error");
    }
  } catch (err) {
    toast?.(err.message || "Failed to load poll", "error");
  } finally {
    loadingDoc.value = false;
  }
};

const loadDocForEdit = () => {
  if (!isEditMode.value) return;
  if (isPollEdit.value) {
    loadPollForEdit(targetDocName.value);
  } else {
    loadSurveyForEdit(targetDocName.value);
  }
};

onMounted(() => {
  loadDocForEdit();
});

watch(
  () => [route.query.name, route.params.name, route.query.edit, route.path],
  () => {
    loadDocForEdit();
  },
);

const selectType = (t) => {
  type.value = t;
  step.value = 1;
};

const addOption = () => form.value.options.push({ text: "" });
const removeOption = (i) => form.value.options.splice(i, 1);

const addQuestion = () =>
  form.value.questions.push({
    text: "",
    type: "Rating Scale",
    required: false,
    options: ["", ""],
  });
const addSection = () =>
  form.value.questions.push({
    text: "",
    type: "Section Heading",
    required: false,
    options: [],
  });
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
    if (isEditMode.value) {
      if (type.value === "poll") {
        result = await frappeCall("pollcast.api.update_poll", {
          poll_name: targetDocName.value,
          title: form.value.title,
          description: form.value.description,
          status: form.value.status,
          start_date: form.value.startDate || null,
          end_date: form.value.endDate || null,
          options: form.value.options
            .filter((o) => o.text.trim())
            .map((o) => o.text),
        });
        if (result?.success || result?.name) {
          toast?.("Poll updated successfully!", "success");
          createdName.value = targetDocName.value;
          step.value = 4;
        }
      } else {
        result = await frappeCall("pollcast.api.update_survey", {
          survey_name: targetDocName.value,
          title: form.value.title,
          description: form.value.description,
          status: form.value.status,
          start_date: form.value.startDate || null,
          end_date: form.value.endDate || null,
          questions: form.value.questions
            .filter((q) => q.text.trim())
            .map((q) => ({
              name: q.name,
              question_text: q.text,
              question_type: q.type,
              required: q.required ? 1 : 0,
              options: q.options?.filter(Boolean) || [],
              scale_min: q.scale_min || 1,
              scale_max: q.scale_max || 5,
            })),
        });

        if (result?.success || result?.name) {
          toast?.("Survey updated successfully!", "success");
          createdName.value = targetDocName.value;
          step.value = 4;
        }
      }
    } else if (type.value === "poll") {
      result = await frappeCall("pollcast.api.create_poll", {
        title: form.value.title,
        description: form.value.description,
        start_date: form.value.startDate || null,
        end_date: form.value.endDate || null,
        options: form.value.options
          .filter((o) => o.text.trim())
          .map((o) => o.text),
      });
      if (result?.name) {
        toast?.("Poll created successfully!", "success");
        createdName.value = result.name;
        step.value = 4;
      }
    } else {
      result = await frappeCall("pollcast.api.create_survey", {
        title: form.value.title,
        description: form.value.description,
        start_date: form.value.startDate || null,
        end_date: form.value.endDate || null,
        questions: form.value.questions
          .filter((q) => q.text.trim())
          .map((q) => ({
            question_text: q.text,
            question_type: q.type,
            required: q.required ? 1 : 0,
            options: q.options?.filter(Boolean) || [],
          })),
      });
      if (result?.name) {
        toast?.("Survey created successfully!", "success");
        createdName.value = result.name;
        step.value = 4;
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
.create-view {
  display: flex;
  flex-direction: column;
}

/* Type Selector */
.type-selector-screen {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem 0;
}
.type-cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  max-width: 800px;
  width: 100%;
}

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
.type-icon-accent {
  background: var(--accent-dim);
  color: var(--accent-light);
}
.type-icon-violet {
  background: var(--violet-dim);
  color: var(--violet-light);
}

.type-features {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}
.type-features li {
  font-size: 0.8125rem;
  color: var(--text-secondary);
}
.type-card-action {
  margin-top: auto;
  width: 100%;
}

/* Wizard */
.wizard-layout {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}
.wizard-step {
}
.step-heading {
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;
  margin-bottom: 1.5rem;
}

/* Response Warning Banner */
.response-warning-banner {
  padding: 1rem 1.25rem;
  border-radius: var(--r-md);
  border-left: 3px solid var(--warning);
  background: var(--warning-dim);
  margin-bottom: 1.5rem;
}

/* Survey Branding Card */
.survey-branding-card {
  padding: 1rem 1.25rem;
  border-radius: var(--r-md);
  border: 1px solid var(--glass-border);
  background: var(--glass-bg);
}

.branding-card-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.branding-thumb-box {
  width: 80px;
  height: 48px;
  border-radius: var(--r-sm);
  background: rgba(0, 0, 0, 0.15);
  border: 1px dashed var(--glass-border);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.25rem;
  flex-shrink: 0;
}

:root[data-theme="light"] .branding-thumb-box {
  background: rgba(0, 0, 0, 0.04);
}

.branding-thumb-img {
  max-height: 40px;
  max-width: 72px;
  object-fit: contain;
}

.branding-meta {
  flex: 1;
  min-width: 180px;
}

.branding-change-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
}

/* Poll options builder */
.options-builder {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}
.option-row-build {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
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
.questions-builder {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
}
.question-card {
  padding: 1.25rem;
}
.q-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.875rem;
  flex-wrap: wrap;
}
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
.q-type-select {
  flex: 0 0 auto;
}
.q-required {
  flex: 1;
  justify-content: flex-end;
}
.q-text {
  margin-bottom: 0.875rem;
}

.q-suboptions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 0.875rem;
  background: var(--glass-bg);
  border-radius: var(--r-md);
  border: 1px solid var(--glass-border);
}
.q-subopt-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.q-rating-preview {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: var(--glass-bg);
  border-radius: var(--r-md);
  border: 1px solid var(--glass-border);
}
.rating-preview-dots {
  display: flex;
  gap: 0.5rem;
}
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
.rating-dot.na {
  border-style: dashed;
  font-size: 0.65rem;
  width: 40px;
  border-radius: var(--r-sm);
}

/* Review section */
.review-section {
  display: flex;
  flex-direction: column;
  gap: 0.875rem;
}
.review-row {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 0.5rem 0;
}
.review-label {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--text-muted);
  min-width: 100px;
  flex-shrink: 0;
}
.review-options,
.review-questions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.review-option {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.875rem;
  padding: 0.5rem 0.75rem;
  background: var(--glass-bg);
  border-radius: var(--r-sm);
}
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
.review-q {
  padding: 0.875rem;
  background: var(--glass-bg);
  border-radius: var(--r-md);
  border: 1px solid var(--glass-border);
}
.review-q-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.q-num-sm {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--text-muted);
}

.wizard-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--glass-border);
}

@media (max-width: 768px) {
  .type-cards,
  .form-grid {
    grid-template-columns: 1fr;
  }
  .form-grid > * {
    grid-column: span 1 !important;
  }
}

/* Success Screen */
.success-screen {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2.5rem 2rem;
  max-width: 560px;
  margin: 0 auto;
  width: 100%;
}

.success-icon-wrap {
  margin-bottom: 1.25rem;
}

.success-icon-circle {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent), var(--accent-light));
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 0 32px var(--accent-glow);
  animation: successPop 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes successPop {
  from {
    transform: scale(0.5);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

.share-link-box {
  width: 100%;
  padding: 1.25rem;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: var(--r-lg);
}

.share-link-row {
  display: flex;
  gap: 0.625rem;
  align-items: center;
}

.share-link-input {
  flex: 1;
  font-family: monospace;
  font-size: 0.8125rem;
  color: var(--text-secondary);
  cursor: text;
}

.share-copy-btn {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  min-width: 110px;
  justify-content: center;
  transition:
    background 0.2s,
    box-shadow 0.2s;
}

.share-copy-btn.copied {
  background: var(--success);
  box-shadow: 0 0 14px rgba(34, 197, 94, 0.35);
}
</style>
