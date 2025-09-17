# Copyright (c) 2025, Godwin Ariwodo and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_url, get_datetime, now
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
            if get_datetime(self.start_date) >= get_datetime(self.end_date):
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
            fields=['poll_question', 'response_value', 'creation']
        )
        
        # Group responses by question
        question_responses = {}
        for response in responses:
            question = response.poll_question
            if question not in question_responses:
                question_responses[question] = []
            question_responses[question].append(response.response_value)
        
        # Analyze each question
        questions_data = []
        first_question_options = [] # This will hold the options for the dashboard view

        for i, question in enumerate(self.questions):
            responses_for_question = question_responses.get(question.name, [])
            total_q_responses = len(responses_for_question)
            
            question_data = {
                'question': question.question_text,
                'type': question.question_type,
                'total_responses': total_q_responses
            }

            if question.question_type in ['Single Choice', 'Multiple Choice']:
                option_counts = {}
                for response in responses_for_question:
                    option_counts[response] = option_counts.get(response, 0) + 1
                
                # Create a structured list of options with counts and percentages
                structured_options = []
                defined_options = [opt.strip() for opt in (question.options or '').split('\n') if opt.strip()]
                
                for opt_text in defined_options:
                    count = option_counts.get(opt_text, 0)
                    percentage = round((count / total_q_responses) * 100, 1) if total_q_responses > 0 else 0
                    structured_options.append({
                        'option': opt_text,
                        'count': count,
                        'percentage': percentage
                    })
                
                question_data['options'] = structured_options
                
                # For the main dashboard analytics, use the options from the first question
                if i == 0:
                    first_question_options = structured_options

            elif question.question_type == 'Rating Scale':
                ratings = [float(r) for r in responses_for_question if r.replace('.','').isdigit()]
                avg_rating = sum(ratings) / len(ratings) if ratings else 0
                question_data['average_rating'] = round(avg_rating, 2)
                question_data['ratings_distribution'] = self.get_rating_distribution(ratings)
            
            questions_data.append(question_data)

        return {
            'total_responses': len(set([r.get('creation') for r in responses])),
            'questions': questions_data,
            'response_timeline': self.get_response_timeline(responses),
            # Add the new top-level key that api.py is expecting
            'options': first_question_options
        }
    
    def get_rating_distribution(self, ratings):
        """Get distribution of ratings"""
        distribution = {str(i): 0 for i in range(1, 6)}  # 1-5 scale
        for rating in ratings:
            if str(int(rating)) in distribution:
                distribution[str(int(rating))] += 1
        return distribution
    
    def get_response_timeline(self, responses):
        """Get response timeline data for charts"""
        from collections import defaultdict
        from frappe.utils import getdate
        
        timeline = defaultdict(int)
        unique_responses = set()
        
        for response in responses:
            response_id = f"{response.get('creation')}"
            if response_id not in unique_responses:
                unique_responses.add(response_id)
                date = getdate(response.creation)
                timeline[str(date)] += 1
        
        return dict(timeline)

# ... (rest of the file remains the same) ...
@frappe.whitelist(allow_guest=True)
def get_poll_data(poll_id):
    """API endpoint to get poll data for public voting"""
    try:
        frappe.log_error(f"Looking for poll_id: {poll_id}")
        
        # Find poll by shareable link
        polls = frappe.get_list('Poll', 
            filters={'shareable_link': ['like', f'%{poll_id}%']},
            fields=['name'],
            limit=1,
            ignore_permissions=True
        )
        
        if not polls:
            return {'error': 'Poll not found'}
        
        poll = frappe.get_doc('Poll', polls[0].name)
        frappe.log_error(f"Found poll: {poll.name}")
        
        if poll.status != 'Active':
            return {'error': 'Poll is not active'}
        
        # Check if poll is within date range
        current_time = get_datetime()
        if poll.start_date and current_time < get_datetime(poll.start_date):
            return {'error': 'Poll has not started yet'}
        
        if poll.end_date and current_time > get_datetime(poll.end_date):
            return {'error': 'Poll has ended'}
        
        # Check if poll has questions
        if not poll.questions:
            return {'error': 'No questions found in this poll'}
        
        # For simplicity, we'll handle the first question only (as your frontend expects)
        first_question = poll.questions[0]
        
        # Build options array from the first question
        options = []
        if first_question.options:
            option_lines = [opt.strip() for opt in first_question.options.split('\n') if opt.strip()]
            for opt_text in option_lines:
                options.append({
                    'name': opt_text,  # Use the option text as the name/value
                    'text': opt_text
                })
        
        return {
            'poll': {
                'name': poll.name,
                'title': poll.title,
                'description': poll.description,
                'allow_multiple': first_question.allow_multiple if hasattr(first_question, 'allow_multiple') else False,
                'options': options,
                'question_name': first_question.name,  # Store the question name for response submission
                'question_text': first_question.question_text
            }
        }
    except Exception as e:
        frappe.log_error(f"Poll data error: {str(e)}")
        return {'error': str(e)}

@frappe.whitelist(allow_guest=True)
def submit_poll_response(poll_id, selected_options, participant_info=None):
    """API endpoint to submit poll response"""
    try:
        # Find poll by shareable link
        polls = frappe.get_list('Poll', 
            filters={'shareable_link': ['like', f'%{poll_id}%']},
            fields=['name'],
            limit=1,
            ignore_permissions=True
        )
        
        if not polls:
            return {'error': 'Poll not found'}
        
        poll = frappe.get_doc('Poll', polls[0].name)
        
        if poll.status != 'Active':
            return {'error': 'Poll is not active'}
        
        if not poll.questions:
            return {'error': 'No questions found in this poll'}
        
        first_question = poll.questions[0]
        
        # Create poll responses
        if isinstance(selected_options, list):
            # Handle multiple selections
            for option in selected_options:
                response_doc = frappe.get_doc({
                    'doctype': 'Poll Response',
                    'poll': poll.name,
                    'poll_question': first_question.name,
                    'response_value': str(option),
                    'participant_ip': frappe.local.request_ip if frappe.local and hasattr(frappe.local, 'request_ip') else '',
                    'participant_info': participant_info or {},
                    'creation_timestamp': now()
                })
                response_doc.insert(ignore_permissions=True)
        else:
            # Handle single selection
            response_doc = frappe.get_doc({
                'doctype': 'Poll Response',
                'poll': poll.name,
                'poll_question': first_question.name,
                'response_value': str(selected_options),
                'participant_ip': frappe.local.request_ip if frappe.local and hasattr(frappe.local, 'request_ip') else '',
                'participant_info': participant_info or {},
                'creation_timestamp': now()
            })
            response_doc.insert(ignore_permissions=True)
        
        # Update poll total responses
        poll.update_total_responses()
        frappe.db.commit()
        
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