# Copyright (c) 2025, Godwin Ariwodo and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestSurvey(FrappeTestCase):
    """Tests for role-based edit & delete restrictions on the Survey doctype."""

    def _make_survey(self, title="Test Survey"):
        """Create and insert a bare-minimum Survey document."""
        survey = frappe.get_doc({
            "doctype": "Survey",
            "title": title,
            "status": "Draft",
            "questions": [
                {
                    "question_text": "How satisfied are you?",
                    "question_type": "Rating Scale",
                    "required": 0,
                }
            ],
        })
        survey.insert(ignore_permissions=True)
        frappe.db.commit()
        return survey

    def _add_response(self, survey):
        """Insert one Survey Response linked to *survey*."""
        question = survey.questions[0]
        frappe.get_doc({
            "doctype": "Survey Response",
            "survey": survey.name,
            "survey_question": question.name,
            "response_value": "4",
        }).insert(ignore_permissions=True)
        frappe.db.commit()

    # ── no-response scenarios (Project Manager) ──────────────────────────────

    def test_project_manager_can_edit_survey_with_no_responses(self):
        """Project Manager should be able to edit a Survey that has no responses."""
        survey = self._make_survey("Edit Test (no responses)")
        survey.reload()
        survey.title = "Edit Test (updated)"
        try:
            survey.validate()
        except frappe.PermissionError:
            self.fail("Project Manager should be able to edit a Survey with no responses.")
        finally:
            frappe.delete_doc("Survey", survey.name, ignore_permissions=True)
            frappe.db.commit()

    def test_project_manager_can_delete_survey_with_no_responses(self):
        """Project Manager should be able to delete a Survey that has no responses via API."""
        survey = self._make_survey("Delete Test (no responses)")
        from pollcast.api import delete_survey
        frappe.set_user("Administrator")
        result = delete_survey(survey_name=survey.name)
        self.assertTrue(result.get("success"), f"Expected success, got: {result}")

    # ── has-response scenarios (Project Manager blocked) ─────────────────────

    def test_project_manager_cannot_edit_survey_with_responses(self):
        """Project Manager must NOT be able to edit a Survey that already has responses."""
        survey = self._make_survey("Edit Blocked Test")
        self._add_response(survey)
        survey.reload()

        with self.assertRaises(frappe.PermissionError):
            survey._current_user_roles = lambda: {"Project Manager"}
            survey.validate()

        frappe.delete_doc("Survey", survey.name, ignore_permissions=True)
        frappe.db.commit()

    def test_project_manager_cannot_delete_survey_with_responses(self):
        """Project Manager must NOT be able to delete a Survey that has responses via API."""
        survey = self._make_survey("Delete Blocked Test")
        self._add_response(survey)

        original_get_roles = frappe.get_roles
        frappe.get_roles = lambda user=None: ["Project Manager", "All", "Guest"]
        try:
            from pollcast.api import delete_survey
            result = delete_survey(survey_name=survey.name)
            self.assertIn("error", result or {}, "Expected permission error for Project Manager with responses.")
        finally:
            frappe.get_roles = original_get_roles
            frappe.delete_doc("Survey", survey.name, ignore_permissions=True)
            frappe.db.commit()

    # ── System Manager can delete even with responses ─────────────────────────

    def test_system_manager_can_delete_survey_with_responses(self):
        """System Manager should be able to delete a Survey even when it has responses."""
        survey = self._make_survey("SM Delete Test")
        self._add_response(survey)

        original_get_roles = frappe.get_roles
        frappe.get_roles = lambda user=None: ["System Manager", "All"]
        try:
            from pollcast.api import delete_survey
            result = delete_survey(survey_name=survey.name)
            self.assertTrue(result.get("success"), f"System Manager should be able to delete: {result}")
        finally:
            frappe.get_roles = original_get_roles
            if frappe.db.exists("Survey", survey.name):
                frappe.delete_doc("Survey", survey.name, ignore_permissions=True)
                frappe.db.commit()
