# Copyright (c) 2025, Godwin Ariwodo and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestPoll(FrappeTestCase):
    """Tests for role-based edit & delete restrictions on the Poll doctype."""

    def _make_poll(self, title="Test Poll"):
        """Create and insert a bare-minimum Poll document."""
        poll = frappe.get_doc({
            "doctype": "Poll",
            "title": title,
            "status": "Draft",
            "questions": [
                {
                    "question_text": "Option A",
                    "question_type": "Single Choice",
                    "options": "Option A",
                }
            ],
        })
        poll.insert(ignore_permissions=True)
        frappe.db.commit()
        return poll

    def _add_response(self, poll):
        """Insert one Poll Response linked to *poll*."""
        question = poll.questions[0]
        frappe.get_doc({
            "doctype": "Poll Response",
            "poll": poll.name,
            "poll_question": question.name,
            "response_value": question.options,
        }).insert(ignore_permissions=True)
        frappe.db.commit()

    # ── no-response scenarios (Project Manager) ──────────────────────────────

    def test_project_manager_can_edit_poll_with_no_responses(self):
        """Project Manager should be able to edit a Poll that has no responses."""
        poll = self._make_poll("Edit Test (no responses)")
        frappe.set_user("Administrator")  # use Administrator for setup
        poll.reload()
        poll.title = "Edit Test (updated)"
        # Should not raise
        try:
            poll.validate()
        except frappe.PermissionError:
            self.fail("Project Manager should be able to edit a Poll with no responses.")
        finally:
            frappe.delete_doc("Poll", poll.name, ignore_permissions=True)
            frappe.db.commit()

    def test_project_manager_can_delete_poll_with_no_responses(self):
        """Project Manager should be able to delete a Poll that has no responses via API."""
        poll = self._make_poll("Delete Test (no responses)")
        from pollcast.api import delete_poll
        frappe.set_user("Administrator")
        result = delete_poll(poll_name=poll.name)
        self.assertTrue(result.get("success"), f"Expected success, got: {result}")

    # ── has-response scenarios (Project Manager blocked) ─────────────────────

    def test_project_manager_cannot_edit_poll_with_responses(self):
        """Project Manager must NOT be able to edit a Poll that already has responses."""
        poll = self._make_poll("Edit Blocked Test")
        self._add_response(poll)
        poll.reload()

        # Simulate Project Manager role check (on_trash / validate)
        with self.assertRaises(frappe.PermissionError):
            poll._current_user_roles = lambda: {"Project Manager"}
            poll.validate()

        frappe.delete_doc("Poll", poll.name, ignore_permissions=True)
        frappe.db.commit()

    def test_project_manager_cannot_delete_poll_with_responses(self):
        """Project Manager must NOT be able to delete a Poll that has responses via API."""
        poll = self._make_poll("Delete Blocked Test")
        self._add_response(poll)

        # Patch session roles
        original_get_roles = frappe.get_roles
        frappe.get_roles = lambda user=None: ["Project Manager", "All", "Guest"]
        try:
            from pollcast.api import delete_poll
            result = delete_poll(poll_name=poll.name)
            self.assertIn("error", result or {}, "Expected permission error for Project Manager with responses.")
        finally:
            frappe.get_roles = original_get_roles
            frappe.delete_doc("Poll", poll.name, ignore_permissions=True)
            frappe.db.commit()

    # ── System Manager can delete even with responses ─────────────────────────

    def test_system_manager_can_delete_poll_with_responses(self):
        """System Manager should be able to delete a Poll even when it has responses."""
        poll = self._make_poll("SM Delete Test")
        self._add_response(poll)

        original_get_roles = frappe.get_roles
        frappe.get_roles = lambda user=None: ["System Manager", "All"]
        try:
            from pollcast.api import delete_poll
            result = delete_poll(poll_name=poll.name)
            self.assertTrue(result.get("success"), f"System Manager should be able to delete: {result}")
        finally:
            frappe.get_roles = original_get_roles
            # poll is already deleted if test passed; ignore if missing
            if frappe.db.exists("Poll", poll.name):
                frappe.delete_doc("Poll", poll.name, ignore_permissions=True)
                frappe.db.commit()
