/**
 * Frappe API helper for the Pollcast Vue 3 SPA.
 *
 * Reads the CSRF token injected by www/pollcast.html and wraps
 * every call in a consistent response shape.
 */

export function getCsrfToken() {
  // First try the meta tag, then the window global injected by the HTML page
  const meta = document.querySelector('meta[name="frappe-csrf-token"]');
  return meta ? meta.getAttribute("content") : (window.frappe_csrf_token || "");
}

/**
 * Call a whitelisted Frappe Python method via POST.
 *
 * @param {string} method  Dotted Python path, e.g. "pollcast.api.get_polls"
 * @param {object} args    Arguments to pass
 * @returns {Promise<any>} The `message` field from Frappe's response envelope
 */
export async function frappeCall(method, args = {}) {
  const formData = new URLSearchParams();
  formData.append("cmd", method);

  for (const [key, value] of Object.entries(args)) {
    formData.append(
      key,
      typeof value === "object" ? JSON.stringify(value) : String(value)
    );
  }

  const response = await fetch(`/api/method/${method}`, {
    method: "POST",
    headers: {
      "X-Frappe-CSRF-Token": getCsrfToken(),
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: formData,
  });

  if (response.status === 403) {
    window.location.href = `/login?redirect-to=${encodeURIComponent(
      window.location.pathname + window.location.hash
    )}`;
    throw new Error("Unauthorised");
  }

  if (!response.ok) {
    const text = await response.text();
    let msg = `HTTP ${response.status}`;
    try {
      const j = JSON.parse(text);
      msg = j.exc_type || j.message || msg;
    } catch {}
    throw new Error(msg);
  }

  const json = await response.json();
  return json.message ?? json;
}

/**
 * GET a Frappe REST resource list.
 */
export async function frappeGetList(doctype, filters = {}, fields = ["name"], opts = {}) {
  const params = new URLSearchParams({
    fields: JSON.stringify(fields),
    filters: JSON.stringify(Object.entries(filters).map(([k, v]) => [doctype, k, "=", v])),
    limit_page_length: String(opts.limit || 200),
    order_by: opts.orderBy || "modified desc",
  });

  const response = await fetch(
    `/api/resource/${encodeURIComponent(doctype)}?${params}`,
    { headers: { "X-Frappe-CSRF-Token": getCsrfToken() } }
  );

  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const json = await response.json();
  return json.data ?? [];
}

/**
 * Open an SSE connection to a Frappe method.
 *
 * @param {string} method  API method path
 * @param {function} onMessage  callback(parsedData)
 * @param {function} onError    callback(event)
 * @returns {EventSource} — call .close() to disconnect
 */
export function frappeSSE(method, onMessage, onError) {
  const url = `/api/method/${method}`;
  const es = new EventSource(url);

  es.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch {
      onMessage(event.data);
    }
  };

  if (onError) es.onerror = onError;
  return es;
}
