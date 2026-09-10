<template>
  <header class="app-header">
    <div class="header-inner">
      <!-- Logo / Brand -->
      <RouterLink to="/" class="brand">
        <div class="brand-logo-svg">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
          </svg>
        </div>
        <span class="brand-name">Internal Rating Survey</span>
      </RouterLink>

      <!-- Desktop Nav -->
      <nav class="desktop-nav">
        <RouterLink to="/" class="nav-link" active-class="active" exact-active-class="active">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0">
            <rect x="3" y="12" width="4" height="9" rx="1"/><rect x="10" y="7" width="4" height="14" rx="1"/><rect x="17" y="3" width="4" height="18" rx="1"/>
          </svg>
          Dashboard
        </RouterLink>
        <RouterLink to="/surveys" class="nav-link" active-class="active">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0">
            <path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/><rect x="9" y="3" width="6" height="4" rx="1"/><line x1="9" y1="12" x2="15" y2="12"/><line x1="9" y1="16" x2="13" y2="16"/>
          </svg>
          Surveys
        </RouterLink>
        <RouterLink to="/analytics" class="nav-link" active-class="active">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0">
            <line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>
          </svg>
          Analytics
        </RouterLink>
        <RouterLink v-if="auth.isHRManager" to="/surveys/create" class="nav-link" active-class="active">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0">
            <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/>
          </svg>
          Create Survey
        </RouterLink>
      </nav>

      <!-- User Section -->
      <div class="header-right">
        <!-- Theme Toggle Switch -->
        <button class="theme-toggle-btn" @click="toggleTheme" :aria-label="'Switch to ' + (theme === 'light' ? 'dark' : 'light') + ' theme'">
          <div class="toggle-icon-wrapper" :class="{ 'is-dark': theme === 'dark' }">
            <span class="toggle-icon sun">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>
            </span>
            <span class="toggle-icon moon">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>
            </span>
          </div>
        </button>

        <template v-if="!auth.isGuest">
          <div class="user-info hide-mobile" style="text-align: right;">
            <span class="user-name">{{ auth.employeeName }}</span>
            <a href="/login?action=Logout" class="logout-link">SIGN OUT</a>
          </div>
          <div class="user-avatar" :title="auth.employeeName">
            {{ auth.initials }}
          </div>
        </template>
        <template v-else>
          <a href="/login" class="login-btn hide-mobile">Sign In</a>
        </template>

        <!-- Mobile menu toggle -->
        <button class="mobile-menu-btn" @click="menuOpen = !menuOpen" aria-label="Menu">
          <span :class="['hamburger', { open: menuOpen }]"></span>
        </button>
      </div>
    </div>

    <!-- Mobile Nav Dropdown -->
    <Transition name="slide-down">
      <nav v-if="menuOpen" class="mobile-nav" @click="menuOpen = false">
        <RouterLink to="/" class="mobile-nav-link">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="12" width="4" height="9" rx="1"/><rect x="10" y="7" width="4" height="14" rx="1"/><rect x="17" y="3" width="4" height="18" rx="1"/></svg>
          Dashboard
        </RouterLink>
        <RouterLink to="/surveys" class="mobile-nav-link">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/><rect x="9" y="3" width="6" height="4" rx="1"/></svg>
          Surveys
        </RouterLink>
        <RouterLink v-if="auth.isHRManager" to="/surveys/create" class="mobile-nav-link">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>
          Create Survey
        </RouterLink>
        <a v-if="!auth.isGuest" href="/login?action=Logout" class="mobile-nav-link danger-link">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
          Sign out
        </a>
        <a v-else href="/login" class="mobile-nav-link">Sign in</a>
      </nav>
    </Transition>
  </header>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useAuthStore } from "../stores/auth.js";

const auth = useAuthStore();
const menuOpen = ref(false);

const theme = ref("light");

onMounted(() => {
  theme.value = document.documentElement.getAttribute("data-theme") || "light";
});

const toggleTheme = () => {
  const newTheme = theme.value === "light" ? "dark" : "light";
  theme.value = newTheme;
  document.documentElement.setAttribute("data-theme", newTheme);
  localStorage.setItem("theme", newTheme);
};
</script>

<style scoped>
.app-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: var(--bg-header);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--border);
}

.header-inner {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 1.5rem;
  height: 60px;
  display: flex;
  align-items: center;
  gap: 2rem;
}

/* Brand */
.brand {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  text-decoration: none;
  flex-shrink: 0;
}
.brand-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: var(--gradient);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  font-weight: 800;
  box-shadow: var(--shadow-glow);
}
.brand-name {
  font-size: 1.1rem;
  font-weight: 800;
  color: var(--text-primary);
  white-space: nowrap;
  letter-spacing: -0.02em;
}

/* Desktop nav */
.desktop-nav {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
  margin-left: 1rem;
}
.nav-link {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.45rem 1rem;
  border-radius: var(--radius-xl);
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-secondary);
  text-decoration: none;
  transition: all var(--transition);
}
.nav-link:hover { color: var(--text-primary); background: var(--bg-secondary); }
.nav-link.active {
  color: var(--text-primary);
  background: rgba(155, 64, 128, 0.15);
  border: 1px solid rgba(155, 64, 128, 0.25);
}
.nav-icon { font-size: 0.85rem; }

/* Right section */
.header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-left: auto;
}
.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(155, 64, 128, 0.15);
  color: var(--accent-light);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
  font-weight: 700;
  flex-shrink: 0;
  cursor: default;
  border: 1px solid rgba(155, 64, 128, 0.3);
}
.user-info {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}
.user-name {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
}
.logout-link {
  font-size: 0.65rem;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  transition: color var(--transition);
}
.logout-link:hover { color: var(--danger); }

.login-btn {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary);
  padding: 0.45rem 1rem;
  border-radius: var(--radius-xl);
  border: 1px solid var(--border);
}
.login-btn:hover {
  background: var(--bg-secondary);
}

/* Hamburger */
.mobile-menu-btn {
  display: none;
  background: none;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 0.4rem;
  cursor: pointer;
  width: 36px;
  height: 36px;
  align-items: center;
  justify-content: center;
}
.hamburger {
  display: block;
  width: 18px;
  height: 2px;
  background: var(--text-secondary);
  position: relative;
  transition: all var(--transition);
}
.hamburger::before,
.hamburger::after {
  content: "";
  position: absolute;
  width: 100%;
  height: 2px;
  background: var(--text-secondary);
  left: 0;
  transition: all var(--transition);
}
.hamburger::before { top: -5px; }
.hamburger::after  { top: 5px; }
.hamburger.open { background: transparent; }
.hamburger.open::before { transform: rotate(45deg); top: 0; }
.hamburger.open::after  { transform: rotate(-45deg); top: 0; }

/* Mobile nav */
.mobile-nav {
  display: flex;
  flex-direction: column;
  padding: 0.5rem 1.5rem 1rem;
  border-top: 1px solid var(--border);
  background: var(--bg-mobile-nav);
}
.mobile-nav-link {
  padding: 0.75rem 0.5rem;
  color: var(--text-secondary);
  font-size: 0.9rem;
  font-weight: 500;
  border-bottom: 1px solid var(--border);
  text-decoration: none;
  transition: color var(--transition);
  display: flex;
  align-items: center;
  gap: 0.6rem;
}
.mobile-nav-link:last-child { border-bottom: none; }
.mobile-nav-link:hover { color: var(--text-primary); }
.danger-link:hover { color: var(--danger) !important; }

/* Transition */
.slide-down-enter-active,
.slide-down-leave-active { transition: all 0.2s ease; }
.slide-down-enter-from,
.slide-down-leave-to { opacity: 0; transform: translateY(-8px); }

/* Theme Toggle Button styling */
.theme-toggle-btn {
  background: transparent;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  overflow: hidden;
  position: relative;
  transition: all var(--transition);
}

.theme-toggle-btn:hover {
  background: var(--bg-card-hover);
  border-color: var(--border-focus);
}

.toggle-icon-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.toggle-icon {
  font-size: 1.15rem;
  position: absolute;
  transition: opacity var(--transition), transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.toggle-icon.sun {
  opacity: 1;
  transform: rotate(0deg);
}

.toggle-icon.moon {
  opacity: 0;
  transform: rotate(-90deg);
}

.toggle-icon-wrapper.is-dark {
  transform: rotate(360deg);
}

.toggle-icon-wrapper.is-dark .toggle-icon.sun {
  opacity: 0;
  transform: rotate(90deg);
}

.toggle-icon-wrapper.is-dark .toggle-icon.moon {
  opacity: 1;
  transform: rotate(0deg);
}

/* Hide desktop nav on mobile */
.hide-mobile { display: flex; }
@media (max-width: 768px) {
  .desktop-nav { display: none; }
  .hide-mobile { display: none; }
  .mobile-menu-btn { display: flex; }
}
</style>
