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
 * Strips a stale `_reload` query-string parameter that may have been left in
 * the URL by a previous (now-fixed or legacy) update flow. Call this once on
 * app startup so users never see a dirty URL bar after a forced reload.
 */
export function cleanupReloadParam() {
  try {
    const url = new URL(window.location.href);
    if (url.searchParams.has("_reload")) {
      url.searchParams.delete("_reload");
      // replaceState keeps the hash route intact and leaves no history entry
      window.history.replaceState(null, "", url.toString());
    }
  } catch (_) {}
}

/**
 * Performs a thorough, multi-layer cache purge and hard reload:
 * 1. Purges all Service Worker CacheStorage caches
 * 2. Unregisters all Service Workers on the origin
 * 3. Removes stale session and reload tracking keys
 * 4. Updates the stored version to match the server
 * 5. Calls location.reload() — clean, no URL pollution
 *
 * Because all SW caches are cleared BEFORE the reload, the browser fetches
 * fresh assets from the network on the very next load.
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

  // 5. Reload cleanly — caches are already purged so the browser fetches fresh
  //    assets. No URL query-param pollution; the hash route is preserved.
  window.location.reload();
}

