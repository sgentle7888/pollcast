<template>
  <div class="rating-slider" :class="{ 'is-readonly': readonly }">
    <div class="stars" role="group" :aria-label="`Rating: ${displayValue} of ${max}`">
      <button
        v-for="n in max"
        :key="n"
        class="star-btn"
        :class="{ 
          active: n <= localValue,
          'just-selected': n === lastSelected
        }"
        :disabled="readonly"
        @click="handleClick(n)"
        @mouseenter="!readonly && (hovered = n)"
        @mouseleave="!readonly && (hovered = 0)"
        :title="`${n} – ${scoreLabels[n]}`"
        type="button"
        :aria-label="`${n} star${n > 1 ? 's' : ''}`"
      >
        <svg viewBox="0 0 24 24" :fill="n <= localValue ? 'currentColor' : 'none'" width="26" height="26" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
        </svg>
      </button>
    </div>
    <div class="rating-meta">
      <span class="rating-score">{{ displayValue }}<span class="rating-max">/{{ max }}</span></span>
      <span v-if="scoreLabel" class="rating-label-text" :style="{ color: scoreLabelColor }">{{ scoreLabel }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";

const props = defineProps({
  modelValue: { type: Number, default: 0 },
  max:        { type: Number, default: 5 },
  readonly:   { type: Boolean, default: false },
});

const emit = defineEmits(["update:modelValue"]);
const hovered = ref(0);
const lastSelected = ref(0);

const scoreLabels = { 1: "Poor", 2: "Below Avg", 3: "Average", 4: "Good", 5: "Excellent" };
const scoreLabelColors = {
  1: "var(--danger)",
  2: "var(--warning)",
  3: "var(--warning)",
  4: "var(--accent-light)",
  5: "var(--success)",
};

const localValue = computed(() => hovered.value || props.modelValue);
const displayValue = computed(() => props.modelValue || 0);
const scoreLabel = computed(() => {
  const val = hovered.value || props.modelValue;
  return val > 0 ? scoreLabels[val] : "";
});
const scoreLabelColor = computed(() => {
  const val = hovered.value || props.modelValue;
  return val > 0 ? scoreLabelColors[val] : "var(--text-muted)";
});

const handleClick = (n) => {
  if (props.readonly) return;
  lastSelected.value = n;
  emit("update:modelValue", n);
  // Reset animation trigger
  setTimeout(() => { lastSelected.value = 0; }, 400);
};
</script>

<style scoped>
.rating-slider {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.stars {
  display: flex;
  gap: 0.2rem;
}

.star-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.2rem;
  color: var(--border);
  transition: color 0.15s ease, transform 0.15s ease;
  line-height: 0;
  display: flex;
  align-items: center;
}
.star-btn:disabled { cursor: default; opacity: 0.6; }

/* Hover: partially lit before click */
.star-btn:not(:disabled):hover {
  transform: scale(1.2);
  color: rgba(241, 196, 15, 0.7);
}

/* Active (filled) stars */
.star-btn.active {
  color: #f1c40f;
  filter: drop-shadow(0 0 4px rgba(241, 196, 15, 0.45));
}

/* Pop animation when star is clicked */
.star-btn.just-selected {
  animation: star-pop 0.35s cubic-bezier(0.4, 0, 0.2, 1) both;
}

@keyframes star-pop {
  0%   { transform: scale(1); }
  40%  { transform: scale(1.45); }
  100% { transform: scale(1); }
}

/* Rating meta info */
.rating-meta {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
  min-width: 70px;
}

.rating-score {
  font-size: 1rem;
  font-weight: 800;
  color: var(--text-primary);
  line-height: 1;
}

.rating-max {
  font-size: 0.7rem;
  font-weight: 500;
  color: var(--text-muted);
}

.rating-label-text {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  transition: color 0.2s ease;
}

/* Readonly mode: dimmer and no cursor changes */
.is-readonly .star-btn {
  cursor: default;
}
</style>

