# Copyright (c) 2025, Godwin Ariwodo and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, time_diff_in_seconds

class BackgroundJobLog(Document):
    def before_insert(self):
        if not self.started_at:
            self.started_at = now_datetime()
        self.status = "Running"
    
    def mark_completed(self, details=None):
        """Mark job as completed"""
        self.completed_at = now_datetime()
        self.status = "Completed"
        if self.started_at and self.completed_at:
            self.duration = time_diff_in_seconds(self.completed_at, self.started_at)
        if details:
            self.details = details
        self.save(ignore_permissions=True)
    
    def mark_failed(self, error_message, details=None):
        """Mark job as failed"""
        self.completed_at = now_datetime()
        self.status = "Failed"
        self.error_message = error_message
        if self.started_at and self.completed_at:
            self.duration = time_diff_in_seconds(self.completed_at, self.started_at)
        if details:
            self.details = details
        self.save(ignore_permissions=True)

def create_job_log(job_name):
    """Create a new background job log entry"""
    log = frappe.get_doc({
        "doctype": "Background Job Log",
        "job_name": job_name
    })
    log.insert(ignore_permissions=True)
    return log

