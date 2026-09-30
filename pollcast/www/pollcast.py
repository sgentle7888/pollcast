import os
import json
import frappe

# Prevent Frappe from caching this template page in Redis or internal website cache
no_cache = 1


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

    company_name = frappe.db.get_default('pollcast_company_name')
    if company_name is None:
        company_name = (
            frappe.db.get_single_value('Website Settings', 'app_name') or
            frappe.db.get_value('System Settings', None, 'app_name') or
            ''
        )
    context.company_name = company_name or ''

    # Get frontend build version
    version = 'unknown'
    try:
        ver_path = frappe.get_app_path('pollcast', 'public', 'frontend', 'version.json')
        if os.path.exists(ver_path):
            with open(ver_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                version = str(data.get('version') or '')
        if not version or version == 'unknown':
            idx_path = frappe.get_app_path('pollcast', 'public', 'frontend', 'index.js')
            version = str(os.stat(idx_path).st_mtime_ns)
    except Exception:
        version = str(int(frappe.utils.now_datetime().timestamp()))

    context.server_app_version = version

    # If the user or update script passed a reload cache buster, append it to asset_version
    reload_param = frappe.form_dict.get('_reload') or frappe.form_dict.get('v')
    if reload_param:
        context.asset_version = f"{version}_{reload_param}"
    else:
        context.asset_version = version

    return context


