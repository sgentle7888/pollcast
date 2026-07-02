import frappe


def get_context(context):
    """Frappe page controller for the Pollcast Vue 3 SPA.

    Passes session data to the HTML template so the Vue app can
    bootstrap without an extra API round-trip. No authentication
    is enforced here — the Vue router handles that client-side.
    """
    context.no_cache = 1
    context.show_sidebar = False

    context.user = frappe.session.user
    context.csrf_token = frappe.sessions.get_csrf_token()

    return context
