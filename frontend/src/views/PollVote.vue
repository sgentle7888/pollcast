<template>
  <div class="poll-vote-view animate-fade-in-up">

    <!-- Loading -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div><p>Loading poll…</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="error-state card" style="text-align: center; padding: 3rem;">
      <p class="text-danger" style="font-size: 1.25rem; margin-bottom: 1rem;">⚠️ {{ error }}</p>
      <RouterLink to="/polls" class="btn btn-secondary">← Back to Polls</RouterLink>
    </div>

    <!-- Voting Card -->
    <div v-else-if="poll" class="card poll-vote-card" style="max-width: 600px; margin: 0 auto;">
      <!-- Header -->
      <div class="poll-header-block" style="margin-bottom: 1.5rem;">
        <span class="badge badge-active" style="margin-bottom: 0.5rem;">Active Poll</span>
        <h2 style="font-size: 1.35rem; line-height: 1.3;">{{ poll.title }}</h2>
        <p v-if="poll.description" class="text-secondary text-sm" style="margin-top: 0.5rem;" v-html="poll.description"></p>
      </div>

      <form @submit.prevent="submitVote">
        <div class="options-list" style="display: flex; flex-direction: column; gap: 0.75rem; margin-bottom: 1.5rem;">
          <label
            v-for="opt in poll.questions"
            :key="opt.name"
            :class="['poll-option-item', { active: selectedOption === opt.name }]"
          >
            <input
              type="radio"
              name="poll-option"
              :value="opt.name"
              v-model="selectedOption"
              class="poll-radio-hidden"
            />
            <div class="custom-radio-indicator"></div>
            <span class="option-text font-medium">{{ opt.question_text }}</span>
          </label>
        </div>

        <div class="actions-row" style="display: flex; justify-content: space-between; align-items: center; gap: 1rem;">
          <RouterLink to="/polls" class="btn btn-secondary">Cancel</RouterLink>
          <div style="display: flex; gap: 0.5rem;">
            <RouterLink :to="'/polls/' + poll.name + '/results'" class="btn btn-ghost">View Results</RouterLink>
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="!selectedOption || voting"
            >
              <span v-if="voting" class="spinner spinner-sm" style="margin-right: 0.5rem;"></span>
              Cast Vote
            </button>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, inject } from "vue";
import { useRoute, useRouter } from "vue-router";
import { frappeCall } from "../api/frappe.js";

const route = useRoute();
const router = useRouter();
const toast = inject("toast");

const loading = ref(true);
const voting = ref(false);
const error = ref(null);
const poll = ref(null);
const selectedOption = ref("");

onMounted(async () => {
  try {
    const result = await frappeCall("pollcast.api.get_poll", {
      poll_name: route.params.name,
    });
    if (!result || result.error) {
      error.value = result?.error || "Poll not found";
      return;
    }
    poll.value = result;
  } catch (e) {
    error.value = e.message;
  } finally {
    loading.value = false;
  }
});

const submitVote = async () => {
  if (!selectedOption.value) return;
  voting.value = true;
  try {
    const result = await frappeCall("pollcast.api.submit_poll_response", {
      poll_name: poll.value.name,
      option_name: selectedOption.value,
    });

    if (result && result.success !== false) {
      toast?.("Vote cast successfully!", "success");
      router.push(`/polls/${poll.value.name}/results`);
    } else {
      toast?.(result?.error || "Failed to submit vote", "error");
    }
  } catch (e) {
    toast?.(e.message, "error");
  } finally {
    voting.value = false;
  }
};
</script>

<style scoped>
.poll-vote-view { padding: 2rem 0; }

.poll-option-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.25rem;
  border-radius: var(--r-lg);
  border: 1px solid var(--glass-border);
  background: var(--glass-bg);
  cursor: pointer;
  transition: all var(--dur) var(--ease);
}
.poll-option-item:hover {
  background: var(--glass-hover);
  border-color: var(--border-hover);
}
.poll-option-item.active {
  background: var(--accent-dim);
  border-color: var(--accent);
  box-shadow: 0 0 12px var(--accent-glow);
}

.poll-radio-hidden {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.custom-radio-indicator {
  width: 18px;
  height: 18px;
  border: 2px solid var(--glass-border);
  border-radius: 50%;
  position: relative;
  transition: all var(--dur) var(--ease);
  flex-shrink: 0;
}
.poll-option-item:hover .custom-radio-indicator {
  border-color: var(--accent-light);
}
.poll-option-item.active .custom-radio-indicator {
  border-color: var(--accent);
  background: var(--accent);
}
.poll-option-item.active .custom-radio-indicator::after {
  content: "";
  position: absolute;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: white;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.option-text {
  font-size: 0.9375rem;
  color: var(--text-primary);
}
</style>
