class PWAManager {
  constructor() {
    this.deferredPrompt = null
    this.isInstalled = false
    this.isOnline = navigator.onLine

    this.init()
  }

  init() {
    this.registerServiceWorker()
    this.setupInstallPrompt()
    this.setupConnectionHandling()
    this.setupNotifications()
    this.setupOfflineStorage()

    console.log("[PWA] PWA Manager initialized")
  }

  async registerServiceWorker() {
    if ("serviceWorker" in navigator) {
      try {
        const registration = await navigator.serviceWorker.register("/assets/pollcast/js/service-worker.js")
        console.log("[PWA] Service Worker registered:", registration)

        // Handle updates
        registration.addEventListener("updatefound", () => {
          const newWorker = registration.installing
          newWorker.addEventListener("statechange", () => {
            if (newWorker.state === "installed" && navigator.serviceWorker.controller) {
              this.showUpdateNotification()
            }
          })
        })
      } catch (error) {
        console.error("[PWA] Service Worker registration failed:", error)
      }
    }
  }

  setupInstallPrompt() {
    window.addEventListener("beforeinstallprompt", (e) => {
      e.preventDefault()
      this.deferredPrompt = e
      this.showInstallButton()
    })

    window.addEventListener("appinstalled", () => {
      this.isInstalled = true
      this.hideInstallButton()
      console.log("[PWA] App installed successfully")
    })
  }

  setupConnectionHandling() {
    window.addEventListener("online", () => {
      this.isOnline = true
      this.showConnectionStatus("online")
      this.syncOfflineData()
    })

    window.addEventListener("offline", () => {
      this.isOnline = false
      this.showConnectionStatus("offline")
    })
  }

  async setupNotifications() {
    if ("Notification" in window && "serviceWorker" in navigator) {
      const permission = await Notification.requestPermission()
      console.log("[PWA] Notification permission:", permission)
    }
  }

  setupOfflineStorage() {
    // Initialize IndexedDB for offline storage
    this.initOfflineDB()
  }

  async initOfflineDB() {
    try {
      this.db = await this.openDB()
      console.log("[PWA] Offline database initialized")
    } catch (error) {
      console.error("[PWA] Failed to initialize offline database:", error)
    }
  }

  openDB() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open("pollcast-offline", 1)

      request.onerror = () => reject(request.error)
      request.onsuccess = () => resolve(request.result)

      request.onupgradeneeded = (event) => {
        const db = event.target.result

        if (!db.objectStoreNames.contains("poll-responses")) {
          db.createObjectStore("poll-responses", { keyPath: "id", autoIncrement: true })
        }

        if (!db.objectStoreNames.contains("survey-responses")) {
          db.createObjectStore("survey-responses", { keyPath: "id", autoIncrement: true })
        }

        if (!db.objectStoreNames.contains("cached-polls")) {
          db.createObjectStore("cached-polls", { keyPath: "id" })
        }

        if (!db.objectStoreNames.contains("cached-surveys")) {
          db.createObjectStore("cached-surveys", { keyPath: "id" })
        }
      }
    })
  }

  async installApp() {
    if (this.deferredPrompt) {
      this.deferredPrompt.prompt()
      const { outcome } = await this.deferredPrompt.userChoice

      if (outcome === "accepted") {
        console.log("[PWA] User accepted the install prompt")
      } else {
        console.log("[PWA] User dismissed the install prompt")
      }

      this.deferredPrompt = null
    }
  }

  showInstallButton() {
    const installButton = document.getElementById("install-app-button")
    if (installButton) {
      installButton.style.display = "block"
      installButton.addEventListener("click", () => this.installApp())
    }
  }

  hideInstallButton() {
    const installButton = document.getElementById("install-app-button")
    if (installButton) {
      installButton.style.display = "none"
    }
  }

  showConnectionStatus(status) {
    const statusElement = document.getElementById("connection-status")
    if (statusElement) {
      statusElement.className = `connection-status ${status}`
      statusElement.textContent = status === "online" ? "Connected" : "Offline"

      // Auto-hide after 3 seconds if online
      if (status === "online") {
        setTimeout(() => {
          statusElement.style.display = "none"
        }, 3000)
      } else {
        statusElement.style.display = "block"
      }
    }
  }

  showUpdateNotification() {
    const notification = document.createElement("div")
    notification.className = "update-notification"
    notification.innerHTML = `
            <div class="update-content">
                <span>A new version is available!</span>
                <button onclick="window.location.reload()">Update</button>
            </div>
        `
    document.body.appendChild(notification)
  }

  async saveOfflineResponse(type, data) {
    if (!this.db) return false

    try {
      const transaction = this.db.transaction([`${type}-responses`], "readwrite")
      const store = transaction.objectStore(`${type}-responses`)

      await store.add({
        data: data,
        timestamp: Date.now(),
        synced: false,
      })

      // Register background sync
      if ("serviceWorker" in navigator && "sync" in window.ServiceWorkerRegistration.prototype) {
        const registration = await navigator.serviceWorker.ready
        await registration.sync.register(`${type}-response-sync`)
      }

      console.log(`[PWA] ${type} response saved offline`)
      return true
    } catch (error) {
      console.error(`[PWA] Failed to save ${type} response offline:`, error)
      return false
    }
  }

  async syncOfflineData() {
    if (!this.isOnline || !this.db) return

    try {
      // Trigger background sync for all pending responses
      if ("serviceWorker" in navigator && "sync" in window.ServiceWorkerRegistration.prototype) {
        const registration = await navigator.serviceWorker.ready
        await registration.sync.register("poll-response-sync")
        await registration.sync.register("survey-response-sync")
      }

      console.log("[PWA] Offline data sync triggered")
    } catch (error) {
      console.error("[PWA] Failed to sync offline data:", error)
    }
  }

  async cacheContent(type, id, data) {
    if (!this.db) return

    try {
      const transaction = this.db.transaction([`cached-${type}s`], "readwrite")
      const store = transaction.objectStore(`cached-${type}s`)

      await store.put({
        id: id,
        data: data,
        cached_at: Date.now(),
      })

      console.log(`[PWA] ${type} ${id} cached for offline access`)
    } catch (error) {
      console.error(`[PWA] Failed to cache ${type}:`, error)
    }
  }

  async getCachedContent(type, id) {
    if (!this.db) return null

    try {
      const transaction = this.db.transaction([`cached-${type}s`], "readonly")
      const store = transaction.objectStore(`cached-${type}s`)
      const result = await store.get(id)

      return result ? result.data : null
    } catch (error) {
      console.error(`[PWA] Failed to get cached ${type}:`, error)
      return null
    }
  }
}

// Initialize PWA Manager
const pwaManager = new PWAManager()

// Export for global access
window.pwaManager = pwaManager
