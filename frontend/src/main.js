import { createApp } from "vue";
import { createPinia } from "pinia";
import App from "./App.vue";
import router from "./router/index.js";
import "./assets/main.css";

const VERSION_KEY = "pollcast_loaded_version";
const VERSION_ENDPOINT = "/api/method/pollcast.api.get_app_version";
const RELOAD_KEY = "pollcast_version_reload";

async function clearPollcastCaches() {
  if (!("caches" in window)) return;

  const cacheNames = await caches.keys();
  await Promise.all(
    cacheNames
      .filter((cacheName) => cacheName.startsWith("pollcast-"))
      .map((cacheName) => caches.delete(cacheName)),
  );
}

async function ensureCurrentVersion() {
  try {
    const response = await fetch(`${VERSION_ENDPOINT}?_=${Date.now()}`, {
      cache: "no-store",
      credentials: "same-origin",
    });

    if (!response.ok) return true;

    const payload = await response.json();
    const serverVersion = payload.message?.version;
    const localVersion = sessionStorage.getItem(VERSION_KEY);

    if (!serverVersion) return true;

    sessionStorage.setItem(VERSION_KEY, serverVersion);

    if (
      localVersion &&
      localVersion !== serverVersion &&
      !sessionStorage.getItem(RELOAD_KEY)
    ) {
      sessionStorage.setItem(RELOAD_KEY, "1");
      await clearPollcastCaches();
      window.location.reload();
      return false;
    }

    sessionStorage.removeItem(RELOAD_KEY);
    return true;
  } catch (error) {
    console.warn(
      "Pollcast version check failed; continuing with the current build.",
      error,
    );
    return true;
  }
}

async function startApp() {
  if (!(await ensureCurrentVersion())) return;

  const app = createApp(App);
  const pinia = createPinia();

  app.use(pinia);
  app.use(router);
  app.mount("#app");
}

startApp();
