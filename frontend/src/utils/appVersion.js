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
 * Called once on app startup. Strips the `_reload` cache-busting query param
 * that was added by applyAppUpdate() and also writes the current server version
 * to localStorage so the very next hasNewAppVersion() check returns false
 * (preventing the update prompt from immediately re-appearing).
 */
export function cleanupReloadParam() {
  try {
    const url = new URL(window.location.href);
    if (url.searchParams.has("_reload")) {
      url.searchParams.delete("_reload");
      // replaceState keeps the hash route intact and leaves no history entry
      window.history.replaceState(null, "", url.toString());

      // Pre-populate the stored version so hasNewAppVersion() doesn't trigger
      // again immediately. We intentionally don't await — this is best-effort.
      fetchAppVersion()
        .then((v) => { if (v) localStorage.setItem(VERSION_KEY, v); })
        .catch(() => {});
    }
  } catch (_) {}
}

/**
 * Performs a thorough, multi-layer cache purge then navigates to a
 * cache-busting URL so the browser is guaranteed to fetch fresh HTML
 * and fresh assets from the network.
 *
 * Why URL navigation instead of location.reload():
 *   location.reload() does NOT bypass the browser's own HTTP disk cache.
 *   Even after the SW cache is cleared, the browser may serve the old
 *   index.js from its disk cache → old __APP_BUILD_VERSION__ → version
 *   mismatch → the update prompt immediately reappears.
 *
 *   Navigating to /pollcast?_reload=<timestamp> is a different URL, so
 *   the browser fetches fresh HTML. pollcast.py converts that param into
 *   a unique asset version (?v=BUILD_TIMESTAMP) → every asset URL is
 *   unique → browser must fetch all assets from the network.
 *
 *   cleanupReloadParam() (called in main.js on startup) strips _reload
 *   from the URL via history.replaceState so users never see it.
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

  // 2. Unregister all service workers so stale SW scripts cannot intercept
  //    the fresh-asset requests that follow.
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

  // 4. Navigate to a cache-busting URL.
  //    - _reload=<timestamp> makes this a URL the browser has never seen,
  //      so it MUST go to the network for fresh HTML.
  //    - pollcast.py appends the timestamp to the asset version so index.js
  //      and index.css URLs are also brand-new → browser fetches both fresh.
  //    - The hash (#/current/route) is preserved so the user lands on the
  //      same page after the reload.
  //    - cleanupReloadParam() in main.js strips _reload via replaceState
  //      so the address bar looks clean after the bundle boots.
  const bust = Date.now();
  const targetUrl = new URL(window.location.href);
  targetUrl.searchParams.set("_reload", String(bust));
  window.location.replace(targetUrl.toString());
}
