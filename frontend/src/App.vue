<template>
  <div class="app-shell">
    <!-- Sidebar -->
    <AppSidebar
      v-model="mobileOpen"
      @collapse="onCollapse"
    />

    <!-- Mobile sidebar overlay -->
    <div
      :class="['sidebar-overlay', { visible: mobileOpen }]"
      @click="mobileOpen = false"
    ></div>

    <!-- Main Layout -->
    <div :class="['main-layout', { 'sidebar-collapsed': sidebarCollapsed }]">
      <!-- Top Header Bar -->
      <header class="top-bar">
        <div class="top-bar-inner">
          <!-- Mobile hamburger -->
          <button class="hamburger-btn btn btn-ghost btn-icon" @click="mobileOpen = !mobileOpen">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="3" y1="12" x2="21" y2="12"/>
              <line x1="3" y1="6" x2="21" y2="6"/>
              <line x1="3" y1="18" x2="21" y2="18"/>
            </svg>
          </button>

          <!-- Page title + breadcrumbs -->
          <div class="top-bar-title">
            <h2 class="current-page-title">{{ pageTitle }}</h2>
          </div>

          <!-- Right actions -->
          <div class="top-bar-right">
            <RouterLink
              v-if="auth.isPollManager"
              to="/create"
              class="btn btn-primary btn-sm"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
              </svg>
              Create
            </RouterLink>

            <a v-if="!auth.isGuest" href="/login?action=Logout" class="btn btn-ghost btn-sm hide-mobile">
              Sign out
            </a>
          </div>
        </div>
      </header>

      <!-- Page Content -->
      <main class="page-content">
        <RouterView v-slot="{ Component }">
          <Transition name="page" mode="out-in">
            <component :is="Component" />
          </Transition>
        </RouterView>
      </main>
    </div>

    <!-- Toast Notifications -->
    <div class="toast-container">
      <TransitionGroup name="toast">
        <div
          v-for="toast in toasts"
          :key="toast.id"
          :class="['toast', toast.type]"
          @click="removeToast(toast.id)"
        >
          <span class="toast-icon">
            <svg v-if="toast.type === 'success'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>
            </svg>
            <svg v-else-if="toast.type === 'error'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>
            </svg>
            <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
          </span>
          <span>{{ toast.message }}</span>
        </div>
      </TransitionGroup>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, provide, onMounted } from "vue";
import { useRoute } from "vue-router";
import { useAuthStore } from "./stores/auth.js";
import AppSidebar from "./components/AppSidebar.vue";

const auth = useAuthStore();
const route = useRoute();

onMounted(() => auth.init());

const mobileOpen = ref(false);
const sidebarCollapsed = ref(false);

const onCollapse = (val) => { sidebarCollapsed.value = val; };

const pageTitle = computed(() => route.meta?.title || "Pollcast");

// Toast system
const toasts = ref([]);
let toastId = 0;

const addToast = (message, type = "info", duration = 4000) => {
  const id = ++toastId;
  toasts.value.push({ id, message, type });
  if (duration > 0) setTimeout(() => removeToast(id), duration);
};

const removeToast = (id) => {
  const idx = toasts.value.findIndex((t) => t.id === id);
  if (idx !== -1) toasts.value.splice(idx, 1);
};

// Provide toast globally so child views can use it
provide("toast", addToast);
</script>

<style scoped>
.app-shell {
  display: flex;
  min-height: 100vh;
  position: relative;
}

/* Top Header Bar */
.top-bar {
  position: sticky;
  top: 0;
  z-index: 40;
  background: rgba(10,22,40,0.85);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--glass-border);
  flex-shrink: 0;
}

:root[data-theme="light"] .top-bar {
  background: rgba(255,255,255,0.85);
}

.top-bar-inner {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0 1.5rem;
  height: 60px;
}

.hamburger-btn {
  display: none;
  flex-shrink: 0;
}

.top-bar-title {
  flex: 1;
  min-width: 0;
}

.current-page-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.02em;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.top-bar-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-shrink: 0;
}

/* Page transition */
.page-enter-active,
.page-leave-active {
  transition: opacity 0.2s var(--ease), transform 0.2s var(--ease);
}
.page-enter-from {
  opacity: 0;
  transform: translateY(8px);
}
.page-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

/* Toast transitions */
.toast-enter-active,
.toast-leave-active { transition: all 0.3s var(--ease); }
.toast-enter-from { opacity: 0; transform: translateX(20px); }
.toast-leave-to  { opacity: 0; transform: translateX(20px); }

.toast-icon {
  display: flex;
  align-items: center;
  color: var(--text-accent);
}

.toast.success .toast-icon { color: var(--success); }
.toast.error   .toast-icon { color: var(--danger); }

@media (max-width: 768px) {
  .hamburger-btn { display: flex; }
  .hide-mobile   { display: none; }
}
</style>
