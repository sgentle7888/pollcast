// Copyright (c) 2025, Godwin Ariwodo and contributors
// For license information, please see license.txt

frappe.ui.form.on("Survey", {
    refresh: function(frm) {
        frm.add_custom_button(__('Get Survey Link'), function() {
            let survey_url = window.location.origin + '/survey?id=' + encodeURIComponent(frm.doc.name);
            frappe.msgprint({
                title: __('Survey Link'),
                indicator: 'green',
                message: `
                    <p>Share this link with participants:</p>
                    <p><code>${survey_url}</code></p>
                    <button class="btn btn-xs btn-default" onclick="navigator.clipboard.writeText('${survey_url}')">
                        Copy Link
                    </button>
                `
            });
        });
    }
});