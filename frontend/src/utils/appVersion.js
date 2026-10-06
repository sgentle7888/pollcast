const VERSION_KEY = "pollcast_app_version";
const DISMISSED_KEY = "pollcast_dismissed_version";
const VERSION_ENDPOINT = "/api/method/pollcast.api.get_app_version";

/**
 * Returns the build version baked into this running JavaScript bundle.
 * In production builds, this is injected by Vite at build time.
 */
export function getRunningAppVersion() {
  if (typeof __APP_BUILD_VERSION__ !== "undefined" && __APP_BUILD_VERSION__) {
    return String(__APP_BUILD_VERSION__);
  }
  return window.pollcast_server_version ? String(window.pollcast_server_version) : null;
}

/**
 * Fetch the latest frontend version from the server.
 * Always passes a unique timestamp and cache: 'no-store' to guarantee
 * a fresh response directly from Frappe backend.
 */
export async function fetchAppVersion() {
  try {
    const response = await fetch(`${VERSION_ENDPOINT}?_=${Date.now()}`, {
      cache: "no-store",
      credentials: "same-origin",
      headers: {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        Pragma: "no-cache",
      },
    });

    if (!response.ok) return null;
    const payload = await response.json();
    const ver = payload.message?.version || payload.version || null;
    return ver ? String(ver) : null;
  } catch (err) {
    console.warn("[AppVersion] Failed to fetch server version:", err);
    return null;
  }
}

/**
 * Checks if a newer version of Pollcast has been deployed to the server.
 *
 * Compares the server's build version against the currently running bundle's
 * version. Also checks if the user has already accepted or dismissed this
 * exact server version to avoid repeated prompts.
 */
export async function hasNewAppVersion() {
  try {
    const serverVersion = await fetchAppVersion();
    if (!serverVersion || serverVersion === "unknown") return false;

    // 1. If this exact server version was already accepted or dismissed, don't prompt again
    const dismissedVersion = localStorage.getItem(DISMISSED_KEY);
    if (dismissedVersion && String(dismissedVersion) === String(serverVersion)) {
      return false;
    }

    // 2. Compare against running bundle version
    const runningVersion = getRunningAppVersion();
    if (runningVersion && runningVersion !== "unknown") {
      const hasNew = String(serverVersion) !== String(runningVersion);
      if (!hasNew) {
        // App is already running the latest version, update storage
        localStorage.setItem(VERSION_KEY, String(serverVersion));
        localStorage.setItem(DISMISSED_KEY, String(serverVersion));
      }
      return hasNew;
    }

    // 3. Fallback if runningVersion is unavailable (e.g. dev mode)
    const storedVersion = localStorage.getItem(VERSION_KEY);
    if (!storedVersion) {
      localStorage.setItem(VERSION_KEY, String(serverVersion));
      return false;
    }
    return String(storedVersion) !== String(serverVersion);
  } catch (error) {
    console.warn("[AppVersion] Error checking for update:", error);
    return false;
  }
}

/**
 * Dismisses the update prompt for the current or specified server version.
 */
export function dismissAppVersion(serverVersion) {
  try {
    if (serverVersion) {
      localStorage.setItem(DISMISSED_KEY, String(serverVersion));
    }
    sessionStorage.setItem("pollcast_update_dismissed", "1");
    localStorage.setItem("pollcast_snooze_until", String(Date.now() + 60 * 60 * 1000));
  } catch (_) {}
}

/**
 * Called once on app startup. Strips the `_reload` cache-busting query param
 * that was added by applyAppUpdate().
 */
export function cleanupReloadParam() {
  try {
    const url = new URL(window.location.href);
    if (url.searchParams.has("_reload")) {
      url.searchParams.delete("_reload");
      window.history.replaceState(null, "", url.toString());
    }
  } catch (_) {}
}

/**
 * Performs a thorough, multi-layer cache purge and reload to apply the update:
 * 1. Records the server version as accepted in localStorage so the prompt won't re-trigger
 * 2. Purges all CacheStorage entries (Service Worker caches)
 * 3. Unregisters all service workers
 * 4. Clears reload tracking & session flags
 * 5. Navigates to a cache-busted URL to force network fetch of fresh HTML & assets
 */
export async function applyAppUpdate() {
  console.info("[AppVersion] Applying app update & clearing all caches...");

  // 1. Mark this update as applied in localStorage so hasNewAppVersion() returns false
  try {
    const serverVersion = await fetchAppVersion();
    if (serverVersion) {
      localStorage.setItem(VERSION_KEY, String(serverVersion));
      localStorage.setItem(DISMISSED_KEY, String(serverVersion));
    }
  } catch (_) {}

  // 2. Purge all CacheStorage entries
  if (typeof window !== "undefined" && "caches" in window) {
    try {
      const keys = await caches.keys();
      await Promise.all(keys.map((key) => caches.delete(key)));
      console.info("[AppVersion] Purged CacheStorage caches:", keys);
    } catch (e) {
      console.warn("[AppVersion] Error clearing CacheStorage:", e);
    }
  }

  // 3. Unregister all service workers
  if (typeof navigator !== "undefined" && "serviceWorker" in navigator) {
    try {
      const registrations = await navigator.serviceWorker.getRegistrations();
      await Promise.all(registrations.map((reg) => reg.unregister()));
      console.info("[AppVersion] Unregistered service workers:", registrations.length);
    } catch (e) {
      console.warn("[AppVersion] Error unregistering service workers:", e);
    }
  }

  // 4. Clear reload counters & session state
  try {
    sessionStorage.removeItem("pollcast_chunk_reload");
    sessionStorage.removeItem("pollcast_update_dismissed");
  } catch (_) {}

  // 5. Navigate to a cache-busted URL to force fresh network fetch
  const bust = Date.now();
  try {
    const targetUrl = new URL(window.location.href);
    targetUrl.searchParams.set("_reload", String(bust));
    window.location.href = targetUrl.toString();
  } catch (_) {
    window.location.reload();
  }
}
