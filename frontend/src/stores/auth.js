import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { frappeCall } from "../api/frappe.js";

export const useAuthStore = defineStore("auth", () => {
  const user = ref(window.frappe_user || "Guest");
  const employeeName = ref("");
  const roles = ref([]);
  const loading = ref(false);
  const error = ref(null);

  const isGuest         = computed(() => !user.value || user.value === "Guest");
  const isAdmin         = computed(() => roles.value.includes("System Manager"));
  const isPollManager   = computed(() => roles.value.includes("Poll Manager") || roles.value.includes("System Manager"));
  const isHRManager     = computed(() => roles.value.includes("HR Manager") || roles.value.includes("System Manager"));
  const isProjectManager= computed(() => roles.value.includes("Project Manager") || roles.value.includes("System Manager"));

  const companyLogo     = ref(window.pollcast_company_logo || "");

  const initials = computed(() => {
    const name = employeeName.value || user.value || "GU";
    return name
      .split(" ")
      .map((n) => n[0])
      .slice(0, 2)
      .join("")
      .toUpperCase();
  });

  async function fetchCompanyLogo() {
    try {
      const res = await frappeCall("pollcast.api.get_company_logo");
      if (res && res.logo !== undefined) {
        companyLogo.value = res.logo || "";
      }
    } catch (e) {
      console.warn("fetchCompanyLogo error:", e.message);
    }
  }

  function setCompanyLogo(url) {
    companyLogo.value = url || "";
  }

  async function init() {
    loading.value = true;
    error.value = null;
    fetchCompanyLogo();
    try {
      const result = await frappeCall("pollcast.api.get_user_info");
      if (result) {
        user.value = result.user || "Guest";
        employeeName.value = result.employee_name || result.user || "";
        roles.value = result.roles || [];
      }
    } catch (e) {
      // If pollcast.api.get_user_info doesn't exist yet, gracefully degrade
      console.warn("Auth init:", e.message);
      error.value = e.message;
    } finally {
      loading.value = false;
    }
  }

  return {
    user, roles, loading, error,
    isGuest, isAdmin, isPollManager, isHRManager, isProjectManager,
    employeeName, initials, companyLogo,
    init, fetchCompanyLogo, setCompanyLogo,
  };
});

