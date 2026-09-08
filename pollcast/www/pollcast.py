import frappe


def get_context(context):
    """Frappe page controller for the Pollcast Vue 3 SPA.

    Passes session data to the HTML template so the Vue app can
    bootstrap without an extra API round-trip.

    Guest users are explicitly allowed so that shareable poll/survey links
    of the form /pollcast#/polls/:name and /pollcast#/surveys/:name work
    without requiring a login. The Vue router handles access control
    client-side (admin-only routes stay protected).
    """
    context.no_cache = 1
    context.show_sidebar = False
    context.allow_guest = 1   # Let unauthenticated users reach the SPA

    context.user = frappe.session.user
    context.csrf_token = frappe.sessions.get_csrf_token()
    logo = frappe.db.get_default('pollcast_company_logo')
    if not logo:
        logo = frappe.db.get_single_value('Website Settings', 'app_logo')
    context.company_logo = logo or ''

    return context

