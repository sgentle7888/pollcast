const VERSION_KEY = "pollcast_app_version";
const VERSION_ENDPOINT = "/api/method/pollcast.api.get_app_version";

/**
 * Returns the build version baked into this running JavaScript bundle.
 * In production builds, this is injected by Vite at build time.
 */
export function getRunningAppVersion() {
  if (typeof __APP_BUILD_VERSION__ !== "undefined" && __APP_BUILD_VERSION__) {
    return String(__APP_BUILD_VERSION__);
  }
  return window.pollcast_server_version || null;
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
    return payload.message?.version || payload.version || null;
  } catch (err) {
    console.warn("[AppVersion] Failed to fetch server version:", err);
    return null;
  }
}

/**
 * Checks if a newer version of Pollcast has been deployed to the server.
 *
 * Compares the server's build version against the currently running bundle's
 * version. If running from a cached bundle, getRunningAppVersion() will reflect
 * the older version, accurately detecting that an update is needed.
 */
export async function hasNewAppVersion() {
  try {
    const serverVersion = await fetchAppVersion();
    if (!serverVersion || serverVersion === "unknown") return false;

    const runningVersion = getRunningAppVersion();
    if (runningVersion && runningVersion !== "unknown") {
      return String(serverVersion) !== String(runningVersion);
    }

    // Fallback if runningVersion is unavailable (e.g. dev mode without define)
    const storedVersion = localStorage.getItem(VERSION_KEY);
    if (!storedVersion) {
      localStorage.setItem(VERSION_KEY, serverVersion);
      return false;
    }
    return String(storedVersion) !== String(serverVersion);
  } catch (error) {
    console.warn("[AppVersion] Error checking for update:", error);
    return false;
  }
}

/**
 * Performs a thorough, multi-layer cache purge and hard reload:
 * 1. Purges all Service Worker CacheStorage caches
 * 2. Unregisters all Service Workers on the origin
 * 3. Removes stale session and reload tracking keys
 * 4. Evicts the browser's HTTP cache using reload fetches
 * 5. Navigates with a cache-busting timestamp while preserving the route hash
 */
export async function applyAppUpdate() {
  console.info("[AppVersion] Applying app update & clearing all caches...");

  // 1. Purge all CacheStorage entries (Service Worker caches)
  if ("caches" in window) {
    try {
      const keys = await caches.keys();
      await Promise.all(keys.map((key) => caches.delete(key)));
      console.info("[AppVersion] Purged CacheStorage caches:", keys);
    } catch (e) {
      console.warn("[AppVersion] Error clearing CacheStorage:", e);
    }
  }

  // 2. Unregister all service workers so stale scripts cannot intercept requests
  if ("serviceWorker" in navigator) {
    try {
      const registrations = await navigator.serviceWorker.getRegistrations();
      await Promise.all(registrations.map((reg) => reg.unregister()));
      console.info("[AppVersion] Unregistered service workers:", registrations.length);
    } catch (e) {
      console.warn("[AppVersion] Error unregistering service workers:", e);
    }
  }

  // 3. Clear reload counters & stale session state
  try {
    sessionStorage.removeItem("pollcast_chunk_reload");
  } catch (_) {}

  // 4. Update the stored version in localStorage to match the server
  try {
    const serverVersion = await fetchAppVersion();
    if (serverVersion) {
      localStorage.setItem(VERSION_KEY, serverVersion);
    }
  } catch (_) {}

  // 5. Invalidate browser HTTP disk/memory cache for entry assets
  const bust = Date.now();
  try {
    await Promise.allSettled([
      fetch(`/pollcast?_reload=${bust}`, {
        cache: "reload",
        credentials: "same-origin",
      }),
      fetch(`/assets/pollcast/frontend/index.js?_bust=${bust}`, {
        cache: "reload",
      }),
      fetch(`/assets/pollcast/frontend/index.css?_bust=${bust}`, {
        cache: "reload",
      }),
    ]);
  } catch (_) {}

  // 6. Hard-navigate to the cache-busting URL while preserving current hash route
  const targetUrl = new URL(window.location.href);
  targetUrl.searchParams.set("_reload", String(bust));
  window.location.replace(targetUrl.toString());
}

