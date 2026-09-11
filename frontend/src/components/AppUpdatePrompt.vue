<template>
  <div
    v-if="visible && !autoUpdate"
    class="update-prompt-overlay"
    role="presentation"
  >
    <section
      class="update-prompt"
      role="dialog"
      aria-modal="true"
      aria-labelledby="update-title"
    >
      <div class="update-prompt-icon" aria-hidden="true">
        <svg
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="M20 11a8.1 8.1 0 0 0-15.5-2M4 5v4h4" />
          <path d="M4 13a8.1 8.1 0 0 0 15.5 2M20 19v-4h-4" />
        </svg>
      </div>
      <div class="update-prompt-content">
        <h2 id="update-title">A new version is available</h2>
        <p>Update Pollcast to use the latest features and improvements.</p>
      </div>
      <div class="update-prompt-actions">
        <button
          class="btn btn-ghost btn-sm"
          type="button"
          @click="visible = false"
        >
          Later
        </button>
        <button
          class="btn btn-primary btn-sm"
          type="button"
          :disabled="updating"
          @click="updateNow"
        >
          {{ updating ? "Updating..." : "Update now" }}
        </button>
      </div>
    </section>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from "vue";
import { applyAppUpdate, hasNewAppVersion } from "../utils/appVersion.js";

const props = defineProps({
  autoUpdate: {
    type: Boolean,
    default: false,
  },
});

const visible = ref(false);
const updating = ref(false);
let intervalId;

async function checkForUpdate() {
  if (visible.value || document.visibilityState !== "visible") return;

  try {
    if (await hasNewAppVersion()) {
      if (props.autoUpdate) {
        await applyAppUpdate();
      } else {
        visible.value = true;
      }
    }
  } catch (error) {
    console.warn("Pollcast update check failed.", error);
  }
}

async function updateNow() {
  updating.value = true;
  try {
    await applyAppUpdate();
  } catch (error) {
    updating.value = false;
    console.error("Pollcast update failed.", error);
  }
}

onMounted(() => {
  checkForUpdate();
  intervalId = window.setInterval(checkForUpdate, 5 * 60 * 1000);
  document.addEventListener("visibilitychange", checkForUpdate);
});

onUnmounted(() => {
  window.clearInterval(intervalId);
  document.removeEventListener("visibilitychange", checkForUpdate);
});
</script>
