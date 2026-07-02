<template>
  <aside :class="['sidebar-nav', { collapsed: isCollapsed, 'mobile-open': mobileOpen }]">
    <!-- Brand Logo -->
    <div class="sidebar-brand" @click="goHome">
      <div class="brand-icon">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M18 20V10"/><path d="M12 20V4"/><path d="M6 20v-6"/>
        </svg>
      </div>
      <transition name="label-fade">
        <span v-if="!isCollapsed" class="brand-name">Pollcast</span>
      </transition>
    </div>

    <!-- Nav Links -->
    <nav class="sidebar-links">
      <RouterLink
        v-for="item in navItems"
        :key="item.to"
        :to="item.to"
        :class="['sidebar-link', { active: isActive(item) }]"
        :title="isCollapsed ? item.label : ''"
        @click="closeMobile"
      >
        <span class="link-icon" v-html="item.icon"></span>
        <transition name="label-fade">
          <span v-if="!isCollapsed" class="link-label">{{ item.label }}</span>
        </transition>
        <transition name="label-fade">
          <span v-if="!isCollapsed && item.badge" class="link-badge">{{ item.badge }}</span>
        </transition>
      </RouterLink>
    </nav>

    <!-- Divider -->
    <div class="sidebar-divider"></div>

    <!-- Admin Links -->
    <nav v-if="auth.isPollManager && !isCollapsed" class="sidebar-links">
      <div class="sidebar-section-label">Admin</div>
      <RouterLink to="/create" class="sidebar-link" @click="closeMobile">
        <span class="link-icon">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/>
          </svg>
        </span>
        <span class="link-label">Create New</span>
      </RouterLink>
    </nav>
    <nav v-else-if="auth.isPollManager && isCollapsed" class="sidebar-links">
      <RouterLink to="/create" class="sidebar-link" title="Create New" @click="closeMobile">
        <span class="link-icon">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/>
          </svg>
        </span>
      </RouterLink>
    </nav>

    <!-- Spacer -->
    <div class="sidebar-spacer"></div>

    <!-- Bottom: User + Collapse toggle + Theme -->
    <div class="sidebar-bottom">
      <!-- Theme toggle -->
      <button class="sidebar-link theme-btn" @click="toggleTheme" :title="'Switch to ' + (isDark ? 'light' : 'dark') + ' mode'">
        <span class="link-icon">
          <svg v-if="isDark" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/>
            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
            <line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/>
            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
          </svg>
          <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
          </svg>
        </span>
        <transition name="label-fade">
          <span v-if="!isCollapsed" class="link-label">{{ isDark ? 'Light Mode' : 'Dark Mode' }}</span>
        </transition>
      </button>

      <!-- User info -->
      <div v-if="!auth.isGuest" class="sidebar-user" :class="{ compact: isCollapsed }">
        <div class="user-avatar" :title="auth.employeeName">{{ auth.initials }}</div>
        <transition name="label-fade">
          <div v-if="!isCollapsed" class="user-meta">
            <span class="user-name">{{ auth.employeeName || auth.user }}</span>
            <a href="/login?action=Logout" class="user-logout">Sign out</a>
          </div>
        </transition>
      </div>

      <!-- Collapse toggle -->
      <button class="collapse-btn" @click="toggleCollapse" :title="isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'">
        <svg :style="{ transform: isCollapsed ? 'rotate(180deg)' : '' }" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="transition: transform 0.3s ease;">
          <polyline points="15 18 9 12 15 6"/>
        </svg>
      </button>
    </div>
  </aside>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth.js";

const props = defineProps({
  modelValue: { type: Boolean, default: false },  // mobileOpen
});
const emit = defineEmits(["update:modelValue", "collapse"]);

const auth = useAuthStore();
const route = useRoute();
const router = useRouter();

const isCollapsed = ref(false);
const isDark = ref(true);

const mobileOpen = computed(() => props.modelValue);

const navItems = [
  {
    to: "/",
    label: "Home",
    icon: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>`,
    exact: true,
  },
  {
    to: "/polls",
    label: "Polls",
    icon: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 12l2 2 4-4"/><path d="M5 7c0-1.1.9-2 2-2h10a2 2 0 0 1 2 2v12H5V7z"/><path d="M22 19H2"/></svg>`,
  },
  {
    to: "/surveys",
    label: "Surveys",
    icon: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/><rect x="9" y="3" width="6" height="4" rx="1"/><line x1="9" y1="12" x2="15" y2="12"/><line x1="9" y1="16" x2="13" y2="16"/></svg>`,
  },
  {
    to: "/analytics",
    label: "Analytics",
    icon: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>`,
  },
];

const isActive = (item) => {
  if (item.exact) return route.path === item.to;
  return route.path.startsWith(item.to) && item.to !== "/";
};

const goHome = () => { router.push("/"); closeMobile(); };

const closeMobile = () => emit("update:modelValue", false);

const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value;
  emit("collapse", isCollapsed.value);
  localStorage.setItem("sidebar-collapsed", isCollapsed.value ? "1" : "0");
};

const toggleTheme = () => {
  isDark.value = !isDark.value;
  const theme = isDark.value ? "dark" : "light";
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem("theme", theme);
};

onMounted(() => {
  isDark.value = (document.documentElement.getAttribute("data-theme") || "dark") === "dark";
  const saved = localStorage.getItem("sidebar-collapsed");
  if (saved === "1") {
    isCollapsed.value = true;
    emit("collapse", true);
  }
});
</script>

<style scoped>
/* Brand */
.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1.25rem 1rem;
  cursor: pointer;
  border-bottom: 1px solid var(--glass-border);
  user-select: none;
  flex-shrink: 0;
}

.brand-icon {
  width: 36px;
  height: 36px;
  border-radius: var(--r-md);
  background: var(--gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 0 20px var(--accent-glow);
}

.brand-name {
  font-size: 1.05rem;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -0.02em;
  white-space: nowrap;
}

/* Nav */
.sidebar-links {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 0.75rem 0.625rem;
}

.sidebar-section-label {
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-muted);
  padding: 0 0.375rem 0.5rem;
}

.sidebar-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem 0.75rem;
  border-radius: var(--r-md);
  color: var(--text-secondary);
  font-size: 0.875rem;
  font-weight: 500;
  text-decoration: none;
  cursor: pointer;
  border: none;
  background: transparent;
  width: 100%;
  transition: all var(--dur) var(--ease);
  white-space: nowrap;
  position: relative;
}

.sidebar-link:hover {
  background: var(--glass-hover);
  color: var(--text-primary);
}

.sidebar-link.active {
  background: var(--accent-dim);
  color: var(--accent-light);
  font-weight: 600;
}

.sidebar-link.active::before {
  content: "";
  position: absolute;
  left: 0;
  top: 25%;
  bottom: 25%;
  width: 3px;
  background: var(--gradient);
  border-radius: 0 var(--r-xs) var(--r-xs) 0;
}

.link-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 16px;
}

.link-label {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
}

.link-badge {
  background: var(--accent-dim);
  color: var(--accent-light);
  font-size: 0.65rem;
  font-weight: 700;
  padding: 0.15rem 0.45rem;
  border-radius: var(--r-full);
  border: 1px solid var(--border-accent);
  flex-shrink: 0;
}

/* Divider */
.sidebar-divider {
  height: 1px;
  background: var(--glass-border);
  margin: 0 0.625rem;
  flex-shrink: 0;
}

.sidebar-spacer { flex: 1; }

/* Bottom section */
.sidebar-bottom {
  padding: 0.75rem 0.625rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  border-top: 1px solid var(--glass-border);
  flex-shrink: 0;
}

.theme-btn { color: var(--text-secondary); }

/* User */
.sidebar-user {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem 0.75rem;
  border-radius: var(--r-md);
}

.sidebar-user.compact {
  justify-content: center;
  padding: 0.625rem 0.75rem;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--accent-dim);
  color: var(--accent-light);
  font-size: 0.75rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--border-accent);
  flex-shrink: 0;
}

.user-meta {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}

.user-name {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-logout {
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  transition: color var(--dur) var(--ease);
}
.user-logout:hover { color: var(--danger); }

/* Collapse button */
.collapse-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem;
  background: var(--glass-hover);
  border: 1px solid var(--glass-border);
  border-radius: var(--r-md);
  color: var(--text-muted);
  cursor: pointer;
  width: 100%;
  transition: all var(--dur) var(--ease);
}
.collapse-btn:hover { background: var(--glass-border); color: var(--text-primary); }

/* Label fade transition */
.label-fade-enter-active,
.label-fade-leave-active { transition: opacity 0.15s ease, transform 0.15s ease; }
.label-fade-enter-from,
.label-fade-leave-to { opacity: 0; transform: translateX(-4px); }

/* Mobile */
@media (max-width: 768px) {
  .collapse-btn { display: none; }
}
</style>
