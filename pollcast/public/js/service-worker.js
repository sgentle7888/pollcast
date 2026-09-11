const CACHE_NAME = "pollcast-v1.0.0";
const STATIC_CACHE = "pollcast-static-v1.0.0";
const DYNAMIC_CACHE = "pollcast-dynamic-v1.0.0";

// Assets to cache immediately
const STATIC_ASSETS = [
  "/",
  "/assets/pollcast/css/pollcast.css",
  "/assets/pollcast/css/dashboard.css",
  "/assets/pollcast/js/pollcast.js",
  "/assets/pollcast/js/dashboard.js",
  "/assets/pollcast/images/icon-192.png",
  "/assets/pollcast/images/icon-512.png",
  "/offline.html",
];

// API endpoints to cache
const API_CACHE_PATTERNS = [
  /\/api\/method\/pollcast\.api\./,
  /\/api\/resource\/Poll/,
  /\/api\/resource\/Survey/,
];

// Install event - cache static assets
self.addEventListener("install", (event) => {
  console.log("[SW] Installing service worker...");

  event.waitUntil(
    caches
      .open(STATIC_CACHE)
      .then((cache) => {
        console.log("[SW] Caching static assets");
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => {
        console.log("[SW] Static assets cached successfully");
        return self.skipWaiting();
      })
      .catch((error) => {
        console.error("[SW] Failed to cache static assets:", error);
      }),
  );
});

// Activate event - clean up old caches
self.addEventListener("activate", (event) => {
  console.log("[SW] Activating service worker...");

  event.waitUntil(
    caches
      .keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
              console.log("[SW] Deleting old cache:", cacheName);
              return caches.delete(cacheName);
            }
          }),
        );
      })
      .then(() => {
        console.log("[SW] Service worker activated");
        return self.clients.claim();
      }),
  );
});

// Fetch event - implement caching strategies
self.addEventListener("fetch", (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== "GET") {
    return;
  }

  // Handle different types of requests
  if (isFrontendAsset(request)) {
    // The Vue entry bundle must be refreshed after a deployment. Use the
    // network when online, while retaining an offline fallback.
    event.respondWith(networkFirst(request, STATIC_CACHE));
  } else if (isStaticAsset(request)) {
    event.respondWith(cacheFirst(request, STATIC_CACHE));
  } else if (isAPIRequest(request)) {
    event.respondWith(networkFirst(request, DYNAMIC_CACHE));
  } else if (isPageRequest(request)) {
    event.respondWith(staleWhileRevalidate(request, DYNAMIC_CACHE));
  } else {
    event.respondWith(networkFirst(request, DYNAMIC_CACHE));
  }
});

// Background sync for offline form submissions
self.addEventListener("sync", (event) => {
  console.log("[SW] Background sync triggered:", event.tag);

  if (event.tag === "poll-response-sync") {
    event.waitUntil(syncPollResponses());
  } else if (event.tag === "survey-response-sync") {
    event.waitUntil(syncSurveyResponses());
  }
});

// Push notifications
self.addEventListener("push", (event) => {
  console.log("[SW] Push notification received");

  const options = {
    body: event.data ? event.data.text() : "New poll available!",
    icon: "/assets/pollcast/images/icon-192.png",
    badge: "/assets/pollcast/images/badge-72.png",
    vibrate: [200, 100, 200],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1,
    },
    actions: [
      {
        action: "explore",
        title: "View Poll",
        icon: "/assets/pollcast/images/checkmark.png",
      },
      {
        action: "close",
        title: "Close",
        icon: "/assets/pollcast/images/xmark.png",
      },
    ],
  };

  event.waitUntil(self.registration.showNotification("Pollcast", options));
});

// Notification click handling
self.addEventListener("notificationclick", (event) => {
  console.log("[SW] Notification clicked:", event.action);

  event.notification.close();

  if (event.action === "explore") {
    event.waitUntil(clients.openWindow("/"));
  }
});

// Helper functions
function isStaticAsset(request) {
  return (
    request.url.includes("/assets/") ||
    request.url.includes("/images/") ||
    request.url.includes(".css") ||
    request.url.includes(".js")
  );
}

function isFrontendAsset(request) {
  return request.url.includes("/assets/pollcast/frontend/");
}

function isAPIRequest(request) {
  return API_CACHE_PATTERNS.some((pattern) => pattern.test(request.url));
}

function isPageRequest(request) {
  return request.headers.get("accept").includes("text/html");
}

// Caching strategies
async function cacheFirst(request, cacheName) {
  try {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }

    const networkResponse = await fetch(request);
    const cache = await caches.open(cacheName);
    cache.put(request, networkResponse.clone());

    return networkResponse;
  } catch (error) {
    console.error("[SW] Cache first strategy failed:", error);
    return new Response("Offline", { status: 503 });
  }
}

async function networkFirst(request, cacheName) {
  try {
    const networkResponse = await fetch(request);
    const cache = await caches.open(cacheName);
    cache.put(request, networkResponse.clone());

    return networkResponse;
  } catch (error) {
    console.log("[SW] Network failed, trying cache:", error);
    const cachedResponse = await caches.match(request);

    if (cachedResponse) {
      return cachedResponse;
    }

    // Return offline page for navigation requests
    if (isPageRequest(request)) {
      return caches.match("/offline.html");
    }

    return new Response("Offline", { status: 503 });
  }
}

async function staleWhileRevalidate(request, cacheName) {
  const cache = await caches.open(cacheName);
  const cachedResponse = await caches.match(request);

  const fetchPromise = fetch(request).then((networkResponse) => {
    cache.put(request, networkResponse.clone());
    return networkResponse;
  });

  return cachedResponse || fetchPromise;
}

// Sync functions
async function syncPollResponses() {
  try {
    const db = await openDB();
    const responses = await getAllPendingResponses(db, "poll-responses");

    for (const response of responses) {
      try {
        await fetch("/api/method/pollcast.api.submit_poll_response", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(response.data),
        });

        await deletePendingResponse(db, "poll-responses", response.id);
        console.log("[SW] Synced poll response:", response.id);
      } catch (error) {
        console.error("[SW] Failed to sync poll response:", error);
      }
    }
  } catch (error) {
    console.error("[SW] Poll response sync failed:", error);
  }
}

async function syncSurveyResponses() {
  try {
    const db = await openDB();
    const responses = await getAllPendingResponses(db, "survey-responses");

    for (const response of responses) {
      try {
        await fetch("/api/method/pollcast.api.submit_survey_response", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(response.data),
        });

        await deletePendingResponse(db, "survey-responses", response.id);
        console.log("[SW] Synced survey response:", response.id);
      } catch (error) {
        console.error("[SW] Failed to sync survey response:", error);
      }
    }
  } catch (error) {
    console.error("[SW] Survey response sync failed:", error);
  }
}

// IndexedDB helpers
function openDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open("pollcast-offline", 1);

    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);

    request.onupgradeneeded = (event) => {
      const db = event.target.result;

      if (!db.objectStoreNames.contains("poll-responses")) {
        db.createObjectStore("poll-responses", {
          keyPath: "id",
          autoIncrement: true,
        });
      }

      if (!db.objectStoreNames.contains("survey-responses")) {
        db.createObjectStore("survey-responses", {
          keyPath: "id",
          autoIncrement: true,
        });
      }
    };
  });
}

function getAllPendingResponses(db, storeName) {
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([storeName], "readonly");
    const store = transaction.objectStore(storeName);
    const request = store.getAll();

    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);
  });
}

function deletePendingResponse(db, storeName, id) {
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([storeName], "readwrite");
    const store = transaction.objectStore(storeName);
    const request = store.delete(id);

    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve();
  });
}
