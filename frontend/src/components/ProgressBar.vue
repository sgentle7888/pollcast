<template>
  <div class="progress-wrap">
    <div v-if="label || showValue" class="progress-header">
      <span v-if="label" class="progress-label-text">{{ label }}</span>
      <span v-if="showValue" class="progress-percent">{{ Math.round(value) }}%</span>
    </div>
    <div class="progress-track" :style="{ height: `${height}px` }">
      <div
        class="progress-fill"
        :style="{ width: clampedValue + '%', background: fillColor }"
      ></div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  value:     { type: Number, default: 0 },
  label:     { type: String, default: "" },
  showValue: { type: Boolean, default: true },
  height:    { type: Number, default: 6 },
  color:     { type: String, default: "" },
});

const clampedValue = computed(() => Math.min(100, Math.max(0, props.value || 0)));

const fillColor = computed(() => {
  if (props.color) return props.color;
  const v = clampedValue.value;
  if (v >= 75) return "var(--success)";
  if (v >= 40) return "linear-gradient(90deg, var(--accent), var(--accent-purple))";
  return "var(--warning)";
});
</script>

<style scoped>
.progress-wrap { display: flex; flex-direction: column; gap: 0.35rem; width: 100%; }

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.progress-label-text { font-size: 0.8125rem; color: var(--text-secondary); font-weight: 500; }
.progress-percent    { font-size: 0.8125rem; color: var(--accent-light); font-weight: 600; }

.progress-track {
  width: 100%;
  background: rgba(255, 255, 255, 0.07);
  border-radius: 999px;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  border-radius: 999px;
  transition: width 0.7s cubic-bezier(0.4, 0, 0.2, 1);
}
</style>
