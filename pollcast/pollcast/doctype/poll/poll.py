# Copyright (c) 2025, Godwin Ariwodo and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_url, now
import uuid

class Poll(Document):
    def before_insert(self):
        if not self.shareable_link:
            self.shareable_link = self.generate_shareable_link()
    
    def generate_shareable_link(self):
        """Generate a unique shareable link for the poll"""
        unique_id = str(uuid.uuid4())[:8]
        base_url = get_url()
        return f"{base_url}/poll/{unique_id}"
    
    def validate(self):
        if self.start_date and self.end_date:
            if self.start_date >= self.end_date:
                frappe.throw("End date must be after start date")
    
    def on_update(self):
        self.update_total_responses()
    
    def update_total_responses(self):
        """Update the total response count"""
        total = frappe.db.count('Poll Response', {'poll': self.name})
        frappe.db.set_value('Poll', self.name, 'total_responses', total)
    
    def get_analytics_data(self):
        """Get analytics data for the poll"""
        responses = frappe.get_all('Poll Response', 
            filters={'poll': self.name},
            fields=['poll_option', 'creation']
        )
        
        # Count responses per option
        option_counts = {}
        for response in responses:
            option = response.poll_option
            if option in option_counts:
                option_counts[option] += 1
            else:
                option_counts[option] = 1
        
        # Get option details
        options_data = []
        for option in self.options:
            count = option_counts.get(option.name, 0)
            percentage = (count / len(responses) * 100) if responses else 0
            options_data.append({
                'option': option.option_text,
                'count': count,
                'percentage': round(percentage, 2)
            })
        
        return {
            'total_responses': len(responses),
            'options': options_data,
            'response_timeline': self.get_response_timeline(responses)
        }
    
    def get_response_timeline(self, responses):
        """Get response timeline data for charts"""
        from collections import defaultdict
        from frappe.utils import getdate
        
        timeline = defaultdict(int)
        for response in responses:
            date = getdate(response.creation)
            timeline[str(date)] += 1
        
        return dict(timeline)

@frappe.whitelist()
def get_poll_data(poll_id):
    """API endpoint to get poll data for public voting"""
    try:
        # Extract poll name from shareable link
        poll = frappe.get_doc('Poll', {'shareable_link': {'like': f'%{poll_id}%'}})
        
        if poll.status != 'Active':
            return {'error': 'Poll is not active'}
        
        # Check if poll is within date range
        if poll.start_date and now() < poll.start_date:
            return {'error': 'Poll has not started yet'}
        
        if poll.end_date and now() > poll.end_date:
            return {'error': 'Poll has ended'}
        
        return {
            'poll': {
                'name': poll.name,
                'title': poll.title,
                'description': poll.description,
                'allow_multiple': poll.allow_multiple,
                'options': [{'name': opt.name, 'text': opt.option_text} for opt in poll.options]
            }
        }
    except Exception as e:
        return {'error': str(e)}

@frappe.whitelist(allow_guest=True)
def submit_poll_response(poll_id, selected_options, participant_info=None):
    """API endpoint to submit poll response"""
    try:
        poll = frappe.get_doc('Poll', {'shareable_link': {'like': f'%{poll_id}%'}})
        
        if poll.status != 'Active':
            return {'error': 'Poll is not active'}
        
        # Create poll responses
        for option_name in selected_options:
            response = frappe.get_doc({
                'doctype': 'Poll Response',
                'poll': poll.name,
                'poll_option': option_name,
                'participant_ip': frappe.local.request_ip if frappe.local.request_ip else '',
                'participant_info': participant_info or {}
            })
            response.insert(ignore_permissions=True)
        
        # Update poll total responses
        poll.update_total_responses()
        
        return {'success': True, 'message': 'Response submitted successfully'}
    
    except Exception as e:
        frappe.log_error(f"Poll response submission error: {str(e)}")
        return {'error': 'Failed to submit response'}

@frappe.whitelist()
def get_poll_analytics(poll_name):
    """API endpoint to get poll analytics"""
    try:
        poll = frappe.get_doc('Poll', poll_name)
        return poll.get_analytics_data()
    except Exception as e:
        return {'error': str(e)}
