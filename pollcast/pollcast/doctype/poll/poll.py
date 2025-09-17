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
        for question in self.questions:
            responses_for_question = question_responses.get(question.name, [])
            
            if question.question_type in ['Single Choice', 'Multiple Choice']:
                # Count option frequencies
                option_counts = {}
                for response in responses_for_question:
                    if response in option_counts:
                        option_counts[response] += 1
                    else:
                        option_counts[response] = 1
                
                questions_data.append({
                    'question': question.question_text,
                    'type': question.question_type,
                    'total_responses': len(responses_for_question),
                    'option_counts': option_counts
                })
            
            elif question.question_type == 'Rating Scale':
                # Calculate average rating
                ratings = [float(r) for r in responses_for_question if r.replace('.','').isdigit()]
                avg_rating = sum(ratings) / len(ratings) if ratings else 0
                
                questions_data.append({
                    'question': question.question_text,
                    'type': question.question_type,
                    'total_responses': len(responses_for_question),
                    'average_rating': round(avg_rating, 2),
                    'ratings_distribution': self.get_rating_distribution(ratings)
                })
        
        return {
            'total_responses': len(set([r.get('creation') for r in responses])),
            'questions': questions_data,
            'response_timeline': self.get_response_timeline(responses)
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
        
        questions_data = []
        for question in poll.questions:
            q_data = {
                'name': question.name,
                'text': question.question_text,
                'type': question.question_type,
                'allow_multiple': question.allow_multiple if question.question_type == 'Multiple Choice' else False
            }
            
            if question.question_type in ['Single Choice', 'Multiple Choice']:
                q_data['options'] = [opt.strip() for opt in (question.options or '').split('\n') if opt.strip()]
            
            questions_data.append(q_data)
        
        return {
            'poll': {
                'name': poll.name,
                'title': poll.title,
                'description': poll.description,
                'questions': questions_data
            }
        }
    except Exception as e:
        return {'error': str(e)}

@frappe.whitelist(allow_guest=True)
def submit_poll_response(poll_id, responses, participant_info=None):
    """API endpoint to submit poll response"""
    try:
        poll = frappe.get_doc('Poll', {'shareable_link': {'like': f'%{poll_id}%'}})
        
        if poll.status != 'Active':
            return {'error': 'Poll is not active'}
        
        # Create poll responses
        for question_name, response_value in responses.items():
            if isinstance(response_value, list):
                # Handle multiple choice responses
                for value in response_value:
                    response_doc = frappe.get_doc({
                        'doctype': 'Poll Response',
                        'poll': poll.name,
                        'poll_question': question_name,
                        'response_value': str(value),
                        'participant_ip': frappe.local.request_ip if frappe.local.request_ip else '',
                        'participant_info': participant_info or {}
                    })
                    response_doc.insert(ignore_permissions=True)
            else:
                response_doc = frappe.get_doc({
                    'doctype': 'Poll Response',
                    'poll': poll.name,
                    'poll_question': question_name,
                    'response_value': str(response_value),
                    'participant_ip': frappe.local.request_ip if frappe.local.request_ip else '',
                    'participant_info': participant_info or {}
                })
                response_doc.insert(ignore_permissions=True)
        
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
