const VERSION_KEY = "pollcast_loaded_version";
const VERSION_ENDPOINT = "/api/method/pollcast.api.get_app_version";

export async function fetchAppVersion() {
  const response = await fetch(`${VERSION_ENDPOINT}?_=${Date.now()}`, {
    cache: "no-store",
    credentials: "same-origin",
  });

  if (!response.ok) throw new Error(`Version check failed: ${response.status}`);

  const payload = await response.json();
  return payload.message?.version || null;
}

export async function hasNewAppVersion() {
  const serverVersion = await fetchAppVersion();
  const loadedVersion = sessionStorage.getItem(VERSION_KEY);

  if (!serverVersion) return false;
  if (!loadedVersion) {
    sessionStorage.setItem(VERSION_KEY, serverVersion);
    return false;
  }

  return loadedVersion !== serverVersion;
}

export async function applyAppUpdate() {
  const serverVersion = await fetchAppVersion();
  if (serverVersion) sessionStorage.setItem(VERSION_KEY, serverVersion);

  if ("caches" in window) {
    const cacheNames = await caches.keys();
    await Promise.all(
      cacheNames
        .filter((cacheName) => cacheName.startsWith("pollcast-"))
        .map((cacheName) => caches.delete(cacheName)),
    );
  }

  window.location.reload();
}
