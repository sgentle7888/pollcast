class SSEClient {
  constructor(options = {}) {
    this.baseUrl = options.baseUrl || ""
    this.channels = options.channels || ["global_updates"]
    this.eventSource = null
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectDelay = 1000
    this.listeners = {}
    this.isConnected = false

    this.connect()
  }

  connect() {
    try {
      const channelsParam = this.channels.join(",")
      const url = `${this.baseUrl}/api/method/pollcast.sse.sse_stream?channels=${channelsParam}`

      this.eventSource = new EventSource(url)

      this.eventSource.onopen = (event) => {
        console.log("[SSE] Connected to server")
        this.isConnected = true
        this.reconnectAttempts = 0
        this.emit("connected", { timestamp: new Date().toISOString() })
      }

      this.eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          this.emit("message", data)
        } catch (error) {
          console.error("[SSE] Failed to parse message:", error)
        }
      }

      this.eventSource.onerror = (event) => {
        console.error("[SSE] Connection error:", event)
        this.isConnected = false
        this.emit("error", event)

        if (this.eventSource.readyState === EventSource.CLOSED) {
          this.reconnect()
        }
      }

      // Handle specific event types
      this.eventSource.addEventListener("connected", (event) => {
        const data = JSON.parse(event.data)
        console.log("[SSE] Connection established:", data.connection_id)
        this.connectionId = data.connection_id
      })

      this.eventSource.addEventListener("heartbeat", (event) => {
        const data = JSON.parse(event.data)
        console.log("[SSE] Heartbeat received:", data.timestamp)
        this.emit("heartbeat", data)
      })

      this.eventSource.addEventListener("poll_update", (event) => {
        const data = JSON.parse(event.data)
        console.log("[SSE] Poll update received:", data)
        this.emit("poll_update", data)
      })

      this.eventSource.addEventListener("survey_update", (event) => {
        const data = JSON.parse(event.data)
        console.log("[SSE] Survey update received:", data)
        this.emit("survey_update", data)
      })

      this.eventSource.addEventListener("analytics_update", (event) => {
        const data = JSON.parse(event.data)
        console.log("[SSE] Analytics update received:", data)
        this.emit("analytics_update", data)
      })

      this.eventSource.addEventListener("system_notification", (event) => {
        const data = JSON.parse(event.data)
        console.log("[SSE] System notification received:", data)
        this.emit("system_notification", data)
      })
    } catch (error) {
      console.error("[SSE] Failed to establish connection:", error)
      this.reconnect()
    }
  }

  reconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error("[SSE] Max reconnection attempts reached")
      this.emit("max_reconnect_attempts", { attempts: this.reconnectAttempts })
      return
    }

    this.reconnectAttempts++
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1)

    console.log(`[SSE] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`)

    setTimeout(() => {
      this.disconnect()
      this.connect()
    }, delay)
  }

  disconnect() {
    if (this.eventSource) {
      this.eventSource.close()
      this.eventSource = null
      this.isConnected = false
      console.log("[SSE] Disconnected from server")
    }
  }

  on(event, callback) {
    if (!this.listeners[event]) {
      this.listeners[event] = []
    }
    this.listeners[event].push(callback)
  }

  off(event, callback) {
    if (this.listeners[event]) {
      this.listeners[event] = this.listeners[event].filter((cb) => cb !== callback)
    }
  }

  emit(event, data) {
    if (this.listeners[event]) {
      this.listeners[event].forEach((callback) => {
        try {
          callback(data)
        } catch (error) {
          console.error(`[SSE] Error in event listener for ${event}:`, error)
        }
      })
    }
  }

  getConnectionStatus() {
    return {
      isConnected: this.isConnected,
      connectionId: this.connectionId,
      reconnectAttempts: this.reconnectAttempts,
      channels: this.channels,
    }
  }
}

// Real-time dashboard integration
class RealTimeDashboard {
  constructor(sseClient) {
    this.sseClient = sseClient
    this.charts = {}
    this.setupEventListeners()
  }

  setupEventListeners() {
    this.sseClient.on("poll_update", (data) => {
      this.handlePollUpdate(data)
    })

    this.sseClient.on("survey_update", (data) => {
      this.handleSurveyUpdate(data)
    })

    this.sseClient.on("analytics_update", (data) => {
      this.handleAnalyticsUpdate(data)
    })

    this.sseClient.on("system_notification", (data) => {
      this.showNotification(data)
    })
  }

  handlePollUpdate(data) {
    console.log("[Dashboard] Poll update:", data)

    // Update poll-specific elements
    if (data.type === "new_response") {
      this.updatePollStats(data.poll_id, data.analytics)
      this.updatePollChart(data.poll_id, data.analytics)
      this.showResponseNotification("poll", data.poll_id)
    } else if (data.type === "poll_updated") {
      this.refreshPollInfo(data.poll_id, data.data)
    }
  }

  handleSurveyUpdate(data) {
    console.log("[Dashboard] Survey update:", data)

    // Update survey-specific elements
    if (data.type === "new_response") {
      this.updateSurveyStats(data.survey_id, data.analytics)
      this.updateSurveyChart(data.survey_id, data.analytics)
      this.showResponseNotification("survey", data.survey_id)
    } else if (data.type === "survey_updated") {
      this.refreshSurveyInfo(data.survey_id, data.data)
    }
  }

  handleAnalyticsUpdate(data) {
    console.log("[Dashboard] Analytics update:", data)

    if (data.content_type === "poll") {
      this.updatePollAnalytics(data.content_id, data.analytics)
    } else if (data.content_type === "survey") {
      this.updateSurveyAnalytics(data.content_id, data.analytics)
    }
  }

  updatePollStats(pollId, analytics) {
    const statsElement = document.querySelector(`[data-poll-stats="${pollId}"]`)
    if (statsElement) {
      statsElement.innerHTML = `
                <div class="stat-item">
                    <span class="stat-value">${analytics.total_responses}</span>
                    <span class="stat-label">Responses</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">${analytics.response_rate}%</span>
                    <span class="stat-label">Response Rate</span>
                </div>
            `
    }
  }

  updateSurveyStats(surveyId, analytics) {
    const statsElement = document.querySelector(`[data-survey-stats="${surveyId}"]`)
    if (statsElement) {
      statsElement.innerHTML = `
                <div class="stat-item">
                    <span class="stat-value">${analytics.total_responses}</span>
                    <span class="stat-label">Responses</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">${analytics.completion_rate}%</span>
                    <span class="stat-label">Completion Rate</span>
                </div>
            `
    }
  }

  updatePollChart(pollId, analytics) {
    const chartElement = document.querySelector(`[data-poll-chart="${pollId}"]`)
    if (chartElement && this.charts[`poll_${pollId}`]) {
      const chart = this.charts[`poll_${pollId}`]
      chart.data.datasets[0].data = analytics.option_counts
      chart.update("none") // No animation for real-time updates
    }
  }

  updateSurveyChart(surveyId, analytics) {
    const chartElement = document.querySelector(`[data-survey-chart="${surveyId}"]`)
    if (chartElement && this.charts[`survey_${surveyId}`]) {
      const chart = this.charts[`survey_${surveyId}`]
      // Update survey chart data based on analytics
      chart.update("none")
    }
  }

  showResponseNotification(type, id) {
    const notification = document.createElement("div")
    notification.className = "response-notification"
    notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-icon">📊</span>
                <span class="notification-text">New ${type} response received!</span>
            </div>
        `

    document.body.appendChild(notification)

    // Auto-remove after 3 seconds
    setTimeout(() => {
      notification.remove()
    }, 3000)
  }

  showNotification(data) {
    const notification = document.createElement("div")
    notification.className = `system-notification ${data.type}`
    notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-message">${data.message}</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `

    document.body.appendChild(notification)

    // Auto-remove after 5 seconds for non-error notifications
    if (data.type !== "error") {
      setTimeout(() => {
        if (notification.parentElement) {
          notification.remove()
        }
      }, 5000)
    }
  }

  refreshPollInfo(pollId, data) {
    const titleElement = document.querySelector(`[data-poll-title="${pollId}"]`)
    if (titleElement) {
      titleElement.textContent = data.title
    }

    const statusElement = document.querySelector(`[data-poll-status="${pollId}"]`)
    if (statusElement) {
      statusElement.textContent = data.status
      statusElement.className = `status-badge ${data.status.toLowerCase()}`
    }
  }

  refreshSurveyInfo(surveyId, data) {
    const titleElement = document.querySelector(`[data-survey-title="${surveyId}"]`)
    if (titleElement) {
      titleElement.textContent = data.title
    }

    const statusElement = document.querySelector(`[data-survey-status="${surveyId}"]`)
    if (statusElement) {
      statusElement.textContent = data.status
      statusElement.className = `status-badge ${data.status.toLowerCase()}`
    }
  }
}

// Initialize SSE client and dashboard
let sseClient = null
let realTimeDashboard = null

function initializeSSE(channels = ["global_updates"]) {
  if (sseClient) {
    sseClient.disconnect()
  }

  sseClient = new SSEClient({ channels })
  realTimeDashboard = new RealTimeDashboard(sseClient)

  // Global access
  window.sseClient = sseClient
  window.realTimeDashboard = realTimeDashboard

  return { sseClient, realTimeDashboard }
}

// Auto-initialize on page load
document.addEventListener("DOMContentLoaded", () => {
  // Determine channels based on current page
  const channels = ["global_updates"]

  if (window.location.pathname.includes("/dashboard")) {
    channels.push("analytics_updates")
  }

  if (window.location.pathname.includes("/poll")) {
    channels.push("poll_updates")
  }

  if (window.location.pathname.includes("/survey")) {
    channels.push("survey_updates")
  }

  initializeSSE(channels)
})
