# Copyright (c) 2025, Godwin Ariwodo and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime

class SurveyResponse(Document):
    def before_insert(self):
        if not self.creation_timestamp:
            self.creation_timestamp = now_datetime()
