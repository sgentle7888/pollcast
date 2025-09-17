# Copyright (c) 2025, Godwin Ariwodo and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PollQuestion(Document):
    def validate(self):
        if self.question_type in ['Single Choice', 'Multiple Choice']:
            if not self.options or not self.options.strip():
                frappe.throw("Options are required for choice-based questions")
            
            # Validate that we have at least 2 options
            options_list = [opt.strip() for opt in self.options.split('\n') if opt.strip()]
            if len(options_list) < 2:
                frappe.throw("At least 2 options are required for choice-based questions")
